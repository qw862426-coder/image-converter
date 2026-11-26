"""Convert the MI-GAN TorchScript archive to ONNX without PyTorch: read weights from the zip,
interpret the (straight-line) TorchScript code, and write the ONNX protobuf by hand."""
import zipfile, pickle, io, ast, struct, sys, numpy as np

PT, OUT = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(PT); root = z.namelist()[0].split('/')[0]

# ---------------- load pickled module tree ----------------
class Obj:
    cls = None
    def __init__(self, *a): self.attrs = {}
    def __setstate__(self, st): self.attrs = st if isinstance(st, dict) else {'__state': st}
_types = {}
DT = {'FloatStorage': np.float32, 'HalfStorage': np.float16, 'LongStorage': np.int64, 'DoubleStorage': np.float64, 'IntStorage': np.int32}
def rebuild_tensor(storage, offset, size, stride, *a):
    arr = storage
    if len(size) == 0: return arr[offset:offset + 1].reshape(())
    return np.lib.stride_tricks.as_strided(arr[offset:], shape=size, strides=[s * arr.itemsize for s in stride]).copy()
class U(pickle.Unpickler):
    def __init__(self, f, prefix): super().__init__(f); self.prefix = prefix
    def find_class(self, mod, name):
        if mod == 'torch._utils' and name == '_rebuild_tensor_v2': return rebuild_tensor
        if mod == 'torch' and name.endswith('Storage'): return name
        if mod == 'collections' and name == 'OrderedDict':
            import collections; return collections.OrderedDict
        if mod.startswith('__torch__'):
            full = mod + '.' + name
            if full not in _types: _types[full] = type(name, (Obj,), {'cls': full})
            return _types[full]
        if mod == 'torch.jit._pickle' and name == 'build_tensor_from_id': return lambda i: None
        raise Exception('class ' + mod + '.' + name)
    def persistent_load(self, pid):
        typ, stype, key, loc, numel = pid
        raw = z.read('%s/%s/%s' % (root, self.prefix, key))
        return np.frombuffer(raw, dtype=DT[stype]).copy()
def load(name, prefix):
    return U(io.BytesIO(z.read('%s/%s' % (root, name))), prefix).load()
model = load('data.pkl', 'data')
consts = load('constants.pkl', 'constants')
print('constants', [np.asarray(c).tolist() for c in consts])

# ---------------- code index ----------------
code = {}
for n in z.namelist():
    if '/code/' in n and n.endswith('.py'):
        mod = n.split('/code/')[1][:-3].replace('/', '.')
        tree = ast.parse(z.read(n).decode())
        for c in tree.body:
            if isinstance(c, ast.ClassDef):
                code[mod + '.' + c.name] = next(f for f in c.body if isinstance(f, ast.FunctionDef) and f.name == 'forward')

# ---------------- ONNX graph building ----------------
nodes, inits, cnt = [], [], [0]
def fresh(p='t'): cnt[0] += 1; return '%s%d' % (p, cnt[0])
def init(arr, p='w'):
    n = fresh(p); inits.append((n, np.ascontiguousarray(arr, dtype=np.float32))); return n
def node(op, ins, attrs=None, nout=1):
    outs = [fresh(op.lower()) for _ in range(nout)]
    nodes.append((op, ins, outs, attrs or {})); return outs[0] if nout == 1 else outs
scalar_cache = {}
def sconst(v):
    if v not in scalar_cache: scalar_cache[v] = init(np.array(v, dtype=np.float32), 'c')
    return scalar_cache[v]

def ev(e, env):
    if isinstance(e, ast.Name):
        if e.id == 'None': return None
        return env[e.id]
    if isinstance(e, ast.Constant): return e.value
    if isinstance(e, ast.UnaryOp) and isinstance(e.op, ast.USub): return -ev(e.operand, env)
    if isinstance(e, (ast.List, ast.Tuple)): return [ev(x, env) for x in e.elts]
    if isinstance(e, ast.Attribute):
        if isinstance(e.value, ast.Name) and e.value.id == 'self': return env['self'].attrs[e.attr]
        if isinstance(e.value, ast.Name) and e.value.id == 'CONSTANTS': return ('const', np.asarray(consts[int(e.attr[1:])]))
        raise Exception('attr ' + ast.dump(e))
    if isinstance(e, ast.Call):
        f = e.func; args = [ev(a, env) for a in e.args]
        if isinstance(f, ast.Attribute) and f.attr == 'forward':
            return run(ev(f.value, env), args)
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == 'torch':
            return torch_op(f.attr, args)
        raise Exception('call ' + ast.dump(e))
    raise Exception('expr ' + ast.dump(e))

def val(x):
    if isinstance(x, tuple) and x[0] == 'const': return init(x[1].astype(np.float32), 'k')
    if isinstance(x, (int, float)): return sconst(float(x))
    if isinstance(x, np.ndarray): return init(x.astype(np.float32), 'p')
    return x

def torch_op(op, a):
    if op == '_convolution':
        x, w, b, stride, pad, dil, transposed, opad, groups = a[:9]
        attrs = {'strides': stride, 'pads': [pad[0], pad[1], pad[0], pad[1]], 'dilations': dil, 'group': groups, 'kernel_shape': list(w.shape[2:])}
        ins = [x, init(w)] + ([init(b)] if b is not None else [])
        if transposed:
            attrs['output_padding'] = opad
            return node('ConvTranspose', ins, attrs)
        return node('Conv', ins, attrs)
    if op in ('leaky_relu_', 'leaky_relu'): return node('LeakyRelu', [val(a[0])], {'alpha': float(a[1])})
    if op in ('mul', 'mul_'): return node('Mul', [val(a[0]), val(a[1])])
    if op in ('add', 'add_'): return node('Add', [val(a[0]), val(a[1])])
    if op == 'clamp': return node('Clip', [val(a[0]), sconst(float(a[1])), sconst(float(a[2]))])
    if op == 'pad':
        l, r, t, bt = a[1]; p = np.array([0, 0, t, l, 0, 0, bt, r], dtype=np.int64)
        n = fresh('pads'); inits.append((n, p)); return node('Pad', [a[0], n], {'mode': b'constant'})
    raise Exception('torch.' + op)

def run(mod, args):
    fn = code[mod.cls]
    env = {'self': mod}
    params = [p.arg for p in fn.args.args][1:]
    for p, v in zip(params, args): env[p] = v
    for st in fn.body:
        if isinstance(st, ast.Assign):
            v = ev(st.value, env); tgt = st.targets[0]
            if isinstance(tgt, ast.Tuple):
                for t, vv in zip(tgt.elts, v): env[t.id] = vv
            else: env[tgt.id] = v
        elif isinstance(st, ast.Return): return ev(st.value, env)
        elif isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant): pass
        else: raise Exception('stmt ' + ast.dump(st))

out = run(model, ['input'])
print('nodes', len(nodes), 'initializers', len(inits), 'params', sum(a.size for _, a in inits))

# ---------------- protobuf writer ----------------
def varint(n):
    n &= (1 << 64) - 1; b = bytearray()
    while True:
        x = n & 0x7f; n >>= 7
        if n: b.append(x | 0x80)
        else: b.append(x); return bytes(b)
def key(f, wt): return varint((f << 3) | wt)
def fld_bytes(f, data): return key(f, 2) + varint(len(data)) + data
def fld_str(f, s): return fld_bytes(f, s.encode() if isinstance(s, str) else s)
def fld_int(f, n): return key(f, 0) + varint(n)
def fld_float(f, x): return key(f, 5) + struct.pack('<f', x)
def attr(name, v):
    b = fld_str(1, name)
    if isinstance(v, float): return b + fld_float(2, v) + fld_int(20, 1)
    if isinstance(v, bytes): return b + fld_bytes(4, v) + fld_int(20, 3)
    if isinstance(v, int): return b + fld_int(3, v) + fld_int(20, 2)
    if isinstance(v, (list, tuple)): return b + b''.join(fld_int(8, int(i)) for i in v) + fld_int(20, 7)
    raise Exception(v)
def tensor(name, arr):
    dt = 1 if arr.dtype == np.float32 else 7
    return b''.join(fld_int(1, d) for d in arr.shape) + fld_int(2, dt) + fld_str(8, name) + fld_bytes(9, arr.tobytes())
def vinfo(name, shape):
    dims = b''.join(fld_bytes(1, fld_int(1, d) if isinstance(d, int) else fld_str(2, d)) for d in shape)
    tt = fld_int(1, 1) + fld_bytes(2, dims)
    return fld_str(1, name) + fld_bytes(2, fld_bytes(1, tt))
bad=[(op,[type(x).__name__ for x in ins]) for op,ins,outs,attrs in nodes if any(not isinstance(x,str) for x in ins)]; print("bad",[(i,[repr(x)[:80] for x in ins]) for i,(op,ins,outs,attrs) in enumerate(nodes) if any(not isinstance(x,str) for x in ins)][:2]); g = b""
for i, (op, ins, outs, attrs) in enumerate(nodes):
    nb = b''.join(fld_str(1, x) for x in ins) + b''.join(fld_str(2, x) for x in outs) + fld_str(3, 'n%d' % i) + fld_str(4, op)
    nb += b''.join(fld_bytes(5, attr(k, v)) for k, v in attrs.items())
    g += fld_bytes(1, nb)
g += fld_str(2, 'migan')
for n, a in inits: g += fld_bytes(5, tensor(n, a))
g += fld_bytes(11, vinfo('input', [1, 4, 'H', 'W']))
# rename final output
op, ins, outs, attrs = nodes[-1]
g = g  # output name is the last node's output
g += fld_bytes(12, vinfo(out, [1, 3, 'H', 'W']))
m = fld_int(1, 7) + fld_str(2, 'picshifter-ts2onnx') + fld_bytes(7, g) + fld_bytes(8, fld_str(1, '') + fld_int(2, 11))
open(OUT, 'wb').write(m)
print('wrote', OUT, len(m), 'bytes; output name', out)
