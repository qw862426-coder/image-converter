"""Minimal ONNX protobuf reader/rewriter (no onnx package): read opset, shrink float32 weights."""
import struct, sys, numpy as np
def rv(b,i):
    r=0;s=0
    while True:
        x=b[i]; i+=1; r|=(x&0x7f)<<s; s+=7
        if not x&0x80: return r,i
def fields(b):
    i=0; out=[]
    while i<len(b):
        k,i=rv(b,i); f,wt=k>>3,k&7
        if wt==0: v,i=rv(b,i)
        elif wt==2: n,i=rv(b,i); v=b[i:i+n]; i+=n
        elif wt==5: v=b[i:i+4]; i+=4
        elif wt==1: v=b[i:i+8]; i+=8
        else: raise Exception('wt %d'%wt)
        out.append((f,wt,v))
    return out
def wv(n):
    n&=(1<<64)-1; o=bytearray()
    while True:
        x=n&0x7f; n>>=7
        if n: o.append(x|0x80)
        else: o.append(x); return bytes(o)
def enc(f,wt,v):
    k=wv((f<<3)|wt)
    if wt==0: return k+wv(v)
    if wt==2: return k+wv(len(v))+bytes(v)
    return k+bytes(v)
def opsets(model):
    return [(dict((f,v) for f,wt,v in fields(v))) for f,wt,v in fields(model) if f==8]
