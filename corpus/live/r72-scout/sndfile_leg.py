#!/usr/bin/env python3
"""r72-scout: ONE bounded libsndfile leg (child process, so the parent can
impose the r71 arm timeout on the blocking ctypes calls).

Usage:
  sndfile_leg.py path <member-path>   # sf_open(path)            named arm
  sndfile_leg.py fd                   # sf_open_fd(0)            anonymous arm
                                      #   stdin = pipe (stdin_pipe)
                                      #   stdin = file (redirected_fd)

Prints one JSON object: the frontier-seat verdict shape (SF_INFO fields,
sf_format_check, sf_readf_short count, sf_error_str/sf_strerror).
"""
import ctypes
import json
import os
import sys

lib = ctypes.CDLL("libsndfile.so.1")

SFM_READ = 0x10
SFC_GET_FORMAT_MAJOR_COUNT = 0x1030
SFC_GET_FORMAT_MAJOR = 0x1031
SFC_GET_FORMAT_SUBTYPE_COUNT = 0x1032
SFC_GET_FORMAT_SUBTYPE = 0x1033


class SF_INFO(ctypes.Structure):
    _fields_ = [("frames", ctypes.c_int64),
                ("samplerate", ctypes.c_int),
                ("channels", ctypes.c_int),
                ("format", ctypes.c_int),
                ("sections", ctypes.c_int),
                ("seekable", ctypes.c_int)]


class SF_FORMAT_INFO(ctypes.Structure):
    _fields_ = [("format", ctypes.c_int),
                ("name", ctypes.c_char_p),
                ("extension", ctypes.c_char_p)]


lib.sf_open.restype = ctypes.c_void_p
lib.sf_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(SF_INFO)]
lib.sf_open_fd.restype = ctypes.c_void_p
lib.sf_open_fd.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(SF_INFO),
                           ctypes.c_int]
lib.sf_strerror.restype = ctypes.c_char_p
lib.sf_strerror.argtypes = [ctypes.c_void_p]
lib.sf_error_str.restype = ctypes.c_char_p
lib.sf_error_str.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
lib.sf_close.argtypes = [ctypes.c_void_p]
lib.sf_format_check.argtypes = [ctypes.POINTER(SF_INFO)]
lib.sf_command.restype = ctypes.c_int
lib.sf_command.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p,
                           ctypes.c_int]
lib.sf_readf_short.restype = ctypes.c_int64
lib.sf_readf_short.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_short),
                               ctypes.c_int64]


def enum(count_cmd, item_cmd):
    n = ctypes.c_int(0)
    lib.sf_command(None, count_cmd, ctypes.byref(n), ctypes.sizeof(n))
    out = {}
    for i in range(n.value):
        fi = SF_FORMAT_INFO()
        fi.format = i
        lib.sf_command(None, item_cmd, ctypes.byref(fi), ctypes.sizeof(fi))
        out[fi.format] = (fi.name.decode(), (fi.extension or b"").decode())
    return out


MAJORS = enum(SFC_GET_FORMAT_MAJOR_COUNT, SFC_GET_FORMAT_MAJOR)
SUBS = enum(SFC_GET_FORMAT_SUBTYPE_COUNT, SFC_GET_FORMAT_SUBTYPE)


def main():
    mode = sys.argv[1]
    info = SF_INFO()
    if mode == "fd":
        snd = lib.sf_open_fd(0, SFM_READ, ctypes.byref(info), 0)
    else:
        snd = lib.sf_open(os.fsencode(sys.argv[2]), SFM_READ,
                          ctypes.byref(info))
    if not snd:
        print(json.dumps({
            "opened": False, "format": None, "type_hex": None, "sub_hex": None,
            "format_name": None, "format_ext": None, "format_check": None,
            "frames": None, "samplerate": None, "channels": None,
            "sf_seekable": None, "read_frames": None,
            "error": lib.sf_strerror(None).decode(errors="replace")}))
        return
    sub = info.format & 0x0000FFFF
    mj = MAJORS.get(info.format & 0x0FFF0000, (None, None))
    st = SUBS.get(sub, (None, None))
    name = ("%s/%s" % (mj[0], st[0])) if mj[0] else None
    check = bool(lib.sf_format_check(ctypes.byref(info)))
    buf = (ctypes.c_short * (65536 * max(info.channels, 1)))()
    got = lib.sf_readf_short(snd, buf, 65536)
    ebuf = ctypes.create_string_buffer(256)
    lib.sf_error_str(snd, ebuf, 256)
    errstr = ebuf.value.decode(errors="replace") or None
    lib.sf_close(snd)
    print(json.dumps({
        "opened": True, "format": hex(info.format),
        "type_hex": hex(info.format & 0x0FFF0000), "sub_hex": hex(sub),
        "format_name": name, "format_ext": mj[1], "format_check": check,
        "frames": info.frames, "samplerate": info.samplerate,
        "channels": info.channels, "sf_seekable": bool(info.seekable),
        "read_frames": got, "error": errstr}))


if __name__ == "__main__":
    main()
