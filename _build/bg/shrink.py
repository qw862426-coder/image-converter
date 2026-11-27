"""Shrink an ONNX model's weights: big conv weights -> 8-bit (one scale per output channel, DequantizeLinear),
other weights -> 16-bit (Cast). usage: python3 shrink.py in.onnx out.onnx QMIN   (QMIN=0: 16-bit only)"""
import sys, numpy as np
from onnxrw import fields, enc, wv, rv
src, dst, QMIN = sys.argv[1], sys.argv[2], int(sys.argv[3])
model = open(src, 'rb').read()
def tensor_info(tb):
    dims = []; dt = None; name = None; raw = None; fl = None
    for f, wt, v in fields(tb):
        if f == 1:
            if wt == 0: dims.append(v)
            else:
                i = 0
                while i < len(v): d, i = rv(v, i); dims.append(d)
        elif f == 2: dt = v
        elif f == 8: name = bytes(v).decode()
        elif f == 9: raw = bytes(v)
        elif f == 4: fl = np.frombuffer(bytes(v), np.float32)
    return dims, dt, name, raw, fl
def tensor(name, arr, dt):
    return b''.join(enc(1, 0, int(d)) for d in arr.shape) + enc(2, 0, dt) + enc(8, 2, name.encode()) + enc(9, 2, arr.tobytes())
def nodeb(op, ins, outs, attrs=b''):
    return b''.join(enc(1, 2, x.encode()) for x in ins) + b''.join(enc(2, 2, x.encode()) for x in outs) + enc(3, 2, ('shrink_' + outs[0]).encode()) + enc(4, 2, op.encode()) + attrs
def attr_int(name, v): return enc(5, 2, enc(1, 2, name.encode()) + enc(3, 0, v) + enc(20, 0, 2))
out = b''; before = after = 0; nq = nh = 0
for f, wt, v in fields(model):
    if f != 7: out += enc(f, wt, v); continue
    newnodes = b''; rest = b''
    for gf, gwt, gv in fields(v):
        if gf == 5:
            dims, dt, name, raw, fl = tensor_info(gv)
            if dt == 1:
                arr = (np.frombuffer(raw, np.float32) if raw is not None else fl).reshape(dims) if dims else None
                before += arr.size * 4 if arr is not None else 0
                if arr is not None and QMIN and arr.ndim == 4 and arr.size >= QMIN:
                    sc = (np.abs(arr).reshape(arr.shape[0], -1).max(1) / 127 + 1e-12).astype(np.float32)
                    q = np.clip(np.round(arr / sc[:, None, None, None]), -127, 127).astype(np.int8)
                    rest += enc(5, 2, tensor(name + '_q', q, 3)) + enc(5, 2, tensor(name + '_s', sc, 1)) + enc(5, 2, tensor(name + '_z', np.zeros(arr.shape[0], np.int8), 3))
                    newnodes += enc(1, 2, nodeb('DequantizeLinear', [name + '_q', name + '_s', name + '_z'], [name], attr_int('axis', 0)))
                    after += q.size + sc.size * 5; nq += 1; continue
                if arr is not None and arr.size >= 1024:
                    rest += enc(5, 2, tensor(name + '_h', arr.astype(np.float16), 10))
                    newnodes += enc(1, 2, nodeb('Cast', [name + '_h'], [name], attr_int('to', 1)))
                    after += arr.size * 2; nh += 1; continue
                after += arr.size * 4 if arr is not None else 0
            rest += enc(gf, gwt, gv)
        else: rest += enc(gf, gwt, gv)
    out += enc(7, 2, newnodes + rest)
open(dst, 'wb').write(out)
print('weights %.1f MB -> %.1f MB; 8-bit tensors %d, 16-bit tensors %d; file %.1f MB' % (before / 1e6, after / 1e6, nq, nh, len(out) / 1e6))
