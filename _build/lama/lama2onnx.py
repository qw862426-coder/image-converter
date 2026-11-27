"""Convert big-lama (TorchScript from IOPaint's model release) to ONNX without PyTorch.
- reads the weights from the zip and interprets the TorchScript code with fixed shapes
- the Fourier units (rfft2 / irfft2, 'ortho') become plain matrix products, so no FFT operator is needed
- weights can be stored as 8-bit numbers (one scale per output channel) to make the download 4x smaller
usage: python3 lama2onnx.py big-lama.pt out.onnx SIZE [int8]"""
import zipfile, pickle, io, ast, struct, sys, numpy as np, collections

PT, OUT, SIZE = sys.argv[1], sys.argv[2], int(sys.argv[3]); Q8 = len(sys.argv) > 4 and sys.argv[4] == 'int8'; QMIN = int(sys.argv[5]) if len(sys.argv) > 5 else 4096; F16 = len(sys.argv) > 4 and sys.argv[4] in ('fp16', 'mix'); Q8 = Q8 or (len(sys.argv) > 4 and sys.argv[4] == 'mix')
z = zipfile.ZipFile(PT); root = z.namelist()[0].split('/')[0]

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
        if mod == 'collections' and name == 'OrderedDict': return collections.OrderedDict
        if mod.startswith('__torch__'):
            full = mod + '.' + name
            if full not in _types: _types[full] = type(name, (Obj,), {'cls': full})
            return _types[full]
        if mod == 'torch.jit._pickle' and name == 'build_tensor_from_id': return lambda i: None
        raise Exception('class ' + mod + '.' + name)
    def persistent_load(self, pid):
        typ, stype, key, loc, numel = pid
        return np.frombuffer(z.read('%s/%s/%s' % (root, self.prefix, key)), dtype=DT[stype]).copy()
def load(name, prefix): return U(io.BytesIO(z.read('%s/%s' % (root, name))), prefix).load()
model = load('data.pkl', 'data'); consts = load('constants.pkl', 'constants')
print('constants', [np.asarray(c).shape for c in consts], [float(np.asarray(c).ravel()[0]) if np.asarray(c).size else None for c in consts])

code = {}
for n in z.namelist():
    if '/code/' in n and n.endswith('.py'):
        mod = n.split('/code/')[1][:-3].replace('/', '.')
        for c in ast.parse(z.read(n).decode()).body:
            if isinstance(c, ast.ClassDef):
                for f in c.body:
                    if isinstance(f, ast.FunctionDef) and f.name.startswith('forward'): code[(mod + '.' + c.name, f.name)] = f

# ---------------- graph with static shapes ----------------
nodes, inits, cnt, SH = [], [], [0], {}
def fresh(p='t'): cnt[0] += 1; return '%s%d' % (p, cnt[0])
def init(arr, p='w', dtype=np.float32):
    n = fresh(p); a = np.ascontiguousarray(arr, dtype=dtype); inits.append((n, a)); SH[n] = list(a.shape); return n
def weight(arr):
    """conv weights: 8-bit with one scale per output channel (DequantizeLinear), or float32"""
    arr = np.asarray(arr, np.float32)
    if F16 and not (Q8 and arr.size >= QMIN):
        h = init(arr.astype(np.float16), 'h', np.float16); out = node('Cast', [h], {'to': 1}); SH[out] = list(arr.shape); return out
    if not Q8 or arr.size < QMIN: return init(arr)  # (float16 handled above)
    ax = 0; sc = np.abs(arr).reshape(arr.shape[0], -1).max(1) / 127 + 1e-12
    q = np.clip(np.round(arr / sc.reshape([-1] + [1] * (arr.ndim - 1))), -127, 127).astype(np.int8)
    qn = init(q, 'q', np.int8); sn = init(sc.astype(np.float32), 's'); zn = init(np.zeros(arr.shape[0], np.int8), 'z', np.int8)
    out = node('DequantizeLinear', [qn, sn, zn], {'axis': ax}); SH[out] = list(arr.shape); return out
def node(op, ins, attrs=None, shape=None):
    o = fresh(op.lower()); nodes.append((op, ins, [o], attrs or {}))
    if shape is not None: SH[o] = list(shape)
    return o
sc_cache = {}
def sconst(v):
    if v not in sc_cache: sc_cache[v] = init(np.array(v, dtype=np.float32), 'c')
    return sc_cache[v]
def bshape(a, b):
    a, b = SH[a], SH[b]; n = max(len(a), len(b)); a = [1] * (n - len(a)) + a; b = [1] * (n - len(b)) + b
    return [max(x, y) for x, y in zip(a, b)]
def binop(op, a, b): return node(op, [a, b], shape=bshape(a, b))
def i64(v): return init(np.array(v, np.int64), 'i', np.int64)
def reshape(x, shape): return node('Reshape', [x, i64(shape)], shape=shape)

def conv(x, w, b, stride, pad, dil, transposed, opad, groups):
    N, C, H, W = SH[x]; k = list(w.shape[2:])
    attrs = {'strides': stride, 'pads': [pad[0], pad[1], pad[0], pad[1]], 'dilations': dil, 'group': groups, 'kernel_shape': k}
    ins = [x, weight(w)] + ([init(b)] if b is not None else [])
    if transposed:
        attrs['output_padding'] = opad; O = w.shape[1] * groups
        oh = (H - 1) * stride[0] - 2 * pad[0] + dil[0] * (k[0] - 1) + opad[0] + 1
        ow = (W - 1) * stride[1] - 2 * pad[1] + dil[1] * (k[1] - 1) + opad[1] + 1
        return node('ConvTranspose', ins, attrs, [N, O, oh, ow])
    oh = (H + 2 * pad[0] - dil[0] * (k[0] - 1) - 1) // stride[0] + 1; ow = (W + 2 * pad[1] - dil[1] * (k[1] - 1) - 1) // stride[1] + 1
    return node('Conv', ins, attrs, [N, w.shape[0], oh, ow])

def fourier_unit(mod, x):
    """rfft2 (ortho) -> 1x1 conv + BN + ReLU on [real, imag] channels -> irfft2 (ortho), as matrix products"""
    N, C, H, W = SH[x]; W2 = W // 2 + 1; s = 1 / np.sqrt(H * W)
    w = np.arange(W)[:, None]; k = np.arange(W2)[None, :]
    FwC = init(np.cos(2 * np.pi * w * k / W) * s); FwS = init(-np.sin(2 * np.pi * w * k / W) * s)
    h = np.arange(H)[:, None]; kh = np.arange(H)[None, :]
    Ch = init(np.cos(2 * np.pi * h * kh / H)); Sh = init(np.sin(2 * np.pi * h * kh / H))
    def mm(a, b, shape): return node('MatMul', [a, b], shape=shape)
    Ar = mm(x, FwC, [N, C, H, W2]); Ai = mm(x, FwS, [N, C, H, W2])          # along width: A = x * e^{-i..}
    # along height with e^{-i..} = cos - i sin:  Yr = Ch Ar + Sh Ai ; Yi = Ch Ai - Sh Ar
    Yr = binop('Add', mm(Ch, Ar, [N, C, H, W2]), mm(Sh, Ai, [N, C, H, W2]))
    Yi = binop('Sub', mm(Ch, Ai, [N, C, H, W2]), mm(Sh, Ar, [N, C, H, W2]))
    st = node('Concat', [reshape(Yr, [N, C, 1, H, W2]), reshape(Yi, [N, C, 1, H, W2])], {'axis': 2}, [N, C, 2, H, W2])
    y = reshape(st, [N, 2 * C, H, W2])
    y = run(mod.attrs['conv_layer'], [y]); y = run(mod.attrs['bn'], [y]); y = node('Relu', [y], shape=SH[y])
    C2 = SH[y][1] // 2; y = reshape(y, [N, C2, 2, H, W2])
    Zr0 = reshape(node('Slice', [y, i64([0]), i64([1]), i64([2])], shape=[N, C2, 1, H, W2]), [N, C2, H, W2])
    Zi0 = reshape(node('Slice', [y, i64([1]), i64([2]), i64([2])], shape=[N, C2, 1, H, W2]), [N, C2, H, W2])
    # inverse along height (e^{+i..} = cos + i sin): Zr = Ch Yr - Sh Yi ; Zi = Ch Yi + Sh Yr
    Zr = binop('Sub', mm(Ch, Zr0, [N, C2, H, W2]), mm(Sh, Zi0, [N, C2, H, W2]))
    Zi = binop('Add', mm(Ch, Zi0, [N, C2, H, W2]), mm(Sh, Zr0, [N, C2, H, W2]))
    # complex-to-real along width: x = sum_k c_k (Zr cos - Zi sin), c_k = 1 at 0 and W/2, else 2
    ck = np.full(W2, 2.0); ck[0] = 1; ck[-1] = 1 if W % 2 == 0 else 2
    kk = np.arange(W2)[:, None]; ww = np.arange(W)[None, :]
    Gc = init(ck[:, None] * np.cos(2 * np.pi * kk * ww / W) * s); Gs = init(ck[:, None] * np.sin(2 * np.pi * kk * ww / W) * s)
    return binop('Sub', mm(Zr, Gc, [N, C2, H, W]), mm(Zi, Gs, [N, C2, H, W]))

def val(x):
    if isinstance(x, tuple) and x[0] == 'const':
        a = x[1].astype(np.float32); return sconst(float(a)) if a.ndim == 0 else init(a, 'k')
    if isinstance(x, (int, float)) and not isinstance(x, bool): return sconst(float(x))
    if isinstance(x, np.ndarray): return init(x.astype(np.float32), 'p')
    return x

def torch_op(op, a, kw):
    if op == '_convolution': return conv(*a[:9])
    if op == 'reflection_pad2d':
        l, r, t, b = a[1]
        if not any(a[1]): return a[0]
        N, C, H, W = SH[a[0]]
        return node('Pad', [a[0], i64([0, 0, t, l, 0, 0, b, r])], {'mode': b'reflect'}, [N, C, H + t + b, W + l + r])
    if op == 'batch_norm':
        x, w, b, m, v = a[:5]; eps = a[7]
        return node('BatchNormalization', [x, init(w), init(b), init(m), init(v)], {'epsilon': float(eps)}, SH[x])
    if op in ('relu_', 'relu'): return node('Relu', [a[0]], shape=SH[a[0]])
    if op == 'sigmoid': return node('Sigmoid', [a[0]], shape=SH[a[0]])
    if op == 'add':
        x, y = val(a[0]), val(a[1]); return binop('Add', x, y)
    if op == 'mul': return binop('Mul', val(a[0]), val(a[1]))
    if op == 'rsub': return binop('Sub', val(a[1]), val(a[0]))   # rsub(x, y) = y - x
    if op == 'cat':
        xs = a[0]; ax = a[1]; sh = list(SH[xs[0]]); sh[ax] = sum(SH[t][ax] for t in xs)
        return node('Concat', xs, {'axis': ax}, sh)
    raise Exception('torch.' + op)

def ev(e, env):
    if isinstance(e, ast.Name): return None if e.id == 'None' else env[e.id]
    if isinstance(e, ast.Constant): return e.value
    if isinstance(e, ast.UnaryOp) and isinstance(e.op, ast.USub): return -ev(e.operand, env)
    if isinstance(e, (ast.List, ast.Tuple)): return [ev(x, env) for x in e.elts]
    if isinstance(e, ast.Attribute):
        if isinstance(e.value, ast.Name) and e.value.id == 'self': return env['self'].attrs[e.attr]
        if isinstance(e.value, ast.Name) and e.value.id == 'CONSTANTS': return ('const', np.asarray(consts[int(e.attr[1:])]))
        raise Exception('attr ' + ast.dump(e))
    if isinstance(e, ast.Call):
        f = e.func
        if isinstance(f, ast.Name) and f.id == 'getattr': return ev(e.args[0], env).attrs[e.args[1].value]
        args = [ev(a, env) for a in e.args]; kw = {k.arg: ev(k.value, env) for k in e.keywords}
        if isinstance(f, ast.Attribute) and f.attr.startswith('forward'): return run(ev(f.value, env), args, f.attr)
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == 'torch': return torch_op(f.attr, args, kw)
        raise Exception('call ' + ast.dump(e)[:200])
    raise Exception('expr ' + ast.dump(e)[:200])

def run(mod, args, meth='forward'):
    if mod.cls.endswith('.FourierUnit'): return fourier_unit(mod, args[0])
    if mod.cls.split('.')[-1] in ('Identity',): return args[0] if args else None
    if mod.cls.split('.')[-1] == 'ReLU': return node('Relu', [args[0]], shape=SH[args[0]])
    if mod.cls.split('.')[-1] == 'Sigmoid': return node('Sigmoid', [args[0]], shape=SH[args[0]])
    fn = code[(mod.cls, meth)]; env = {'self': mod}
    for p, v in zip([p.arg for p in fn.args.args][1:], args): env[p] = v
    for st in fn.body:
        if isinstance(st, ast.Assign):
            v = ev(st.value, env); tgt = st.targets[0]
            if isinstance(tgt, ast.Tuple):
                for t, vv in zip(tgt.elts, v): env[t.id] = vv
            else: env[tgt.id] = v
        elif isinstance(st, ast.Return): return ev(st.value, env)
        elif isinstance(st, ast.Expr): pass
        else: raise Exception('stmt ' + ast.dump(st)[:200])

SH['img'] = [1, 3, SIZE, SIZE]; SH['mask'] = [1, 1, SIZE, SIZE]
out = run(model, ['img', 'mask'])
print('nodes', len(nodes), 'initializers', len(inits), 'output shape', SH[out])

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
TDT = {np.dtype(np.float32): 1, np.dtype(np.int8): 3, np.dtype(np.int64): 7, np.dtype(np.float16): 10}
def tensor(name, arr): return b''.join(fld_int(1, d) for d in arr.shape) + fld_int(2, TDT[arr.dtype]) + fld_str(8, name) + fld_bytes(9, arr.tobytes())
def vinfo(name, shape):
    dims = b''.join(fld_bytes(1, fld_int(1, d)) for d in shape)
    return fld_str(1, name) + fld_bytes(2, fld_bytes(1, fld_int(1, 1) + fld_bytes(2, dims)))
g = b''
for i, (op, ins, outs, attrs) in enumerate(nodes):
    nb = b''.join(fld_str(1, x) for x in ins) + b''.join(fld_str(2, x) for x in outs) + fld_str(3, 'n%d' % i) + fld_str(4, op)
    nb += b''.join(fld_bytes(5, attr(k, v)) for k, v in attrs.items())
    g += fld_bytes(1, nb)
g += fld_str(2, 'big-lama')
for n, a in inits: g += fld_bytes(5, tensor(n, a))
g += fld_bytes(11, vinfo('img', SH['img'])) + fld_bytes(11, vinfo('mask', SH['mask']))
g += fld_bytes(12, vinfo(out, SH[out]))
m = fld_int(1, 7) + fld_str(2, 'picshifter-lama2onnx') + fld_bytes(7, g) + fld_bytes(8, fld_str(1, '') + fld_int(2, 13))
open(OUT, 'wb').write(m); print('wrote', OUT, len(m), 'bytes; output', out)
