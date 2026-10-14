#!/usr/bin/env python3
"""r72-critic: is the frontier's single sf_readf_short call a full drain?
Compare single-call count vs loop-to-EOF total on the same members."""
import ctypes, sys

lib = ctypes.CDLL("libsndfile.so.1")
SFM_READ = 0x10
class SF_INFO(ctypes.Structure):
    _fields_ = [("frames", ctypes.c_int64), ("samplerate", ctypes.c_int),
                ("channels", ctypes.c_int), ("format", ctypes.c_int),
                ("sections", ctypes.c_int), ("seekable", ctypes.c_int)]
lib.sf_open.restype = ctypes.c_void_p
lib.sf_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(SF_INFO)]
lib.sf_readf_short.restype = ctypes.c_int64
lib.sf_readf_short.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_short), ctypes.c_int64]
lib.sf_close.argtypes = [ctypes.c_void_p]
lib.sf_strerror.restype = ctypes.c_char_p
lib.sf_strerror.argtypes = [ctypes.c_void_p]

for path in sys.argv[1:]:
    info = SF_INFO()
    snd = lib.sf_open(path.encode(), SFM_READ, ctypes.byref(info))
    if not snd:
        print(f"{path}: OPEN FAIL: {lib.sf_strerror(None).decode()}"); continue
    buf = (ctypes.c_short * 65536)()
    first = lib.sf_readf_short(snd, buf, 65536)
    total = first
    while True:
        n = lib.sf_readf_short(snd, buf, 65536)
        if n <= 0: break
        total += n
    print(f"{path}: info.frames={info.frames} single_call={first} drained_total={total}")
    lib.sf_close(snd)
