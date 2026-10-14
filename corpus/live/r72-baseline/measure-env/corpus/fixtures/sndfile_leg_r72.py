#!/usr/bin/env python3
"""r72 libsndfile leg — one bounded subprocess verdict for measure_audio.py's
--probe-sndfile-transport-r72 mode. Frontier-harness pattern
(corpus/live/frontier-sndfile/probe_sndfile.py) reduced to a per-leg CLI so the
parent harness can time it out exactly like the sox/ffprobe/ffmpeg legs.

Usage:
  sndfile_leg_r72.py info  path <path>   # sf_open(path) -> SF_INFO verdict
  sndfile_leg_r72.py info  fd            # sf_open_fd(dup(0)) on stdin
  sndfile_leg_r72.py read  path <path>   # sf_open + sf_readf_short to EOF
  sndfile_leg_r72.py read  fd            # sf_open_fd(dup(0)) + read to EOF
  sndfile_leg_r72.py formats             # major/subtype enum tables (hex->name)

Verdict JSON on stdout, exit 0 — a rejected open is a verdict, not a crash
(error carries sf_strerror(NULL)). decode frames = sf_readf_short loop total.
"""
import ctypes
import json
import os
import sys

LIB = ctypes.CDLL("libsndfile.so.1")
SFM_READ = 0x10
SFC_GET_FORMAT_MAJOR = 0x1031
SFC_GET_FORMAT_SUBTYPE = 0x1033
SFC_GET_FORMAT_MAJOR_COUNT = 0x1030
SFC_GET_FORMAT_SUBTYPE_COUNT = 0x1032


class SF_INFO(ctypes.Structure):
    _fields_ = [("frames", ctypes.c_int64), ("samplerate", ctypes.c_int),
                ("channels", ctypes.c_int), ("format", ctypes.c_int),
                ("sections", ctypes.c_int), ("seekable", ctypes.c_int)]


class SF_FORMAT_INFO(ctypes.Structure):
    _fields_ = [("format", ctypes.c_int), ("name", ctypes.c_char_p),
                ("extension", ctypes.c_char_p)]


LIB.sf_open.restype = ctypes.c_void_p
LIB.sf_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(SF_INFO)]
LIB.sf_open_fd.restype = ctypes.c_void_p
LIB.sf_open_fd.argtypes = [ctypes.c_int, ctypes.c_int,
                         ctypes.POINTER(SF_INFO), ctypes.c_int]
LIB.sf_strerror.restype = ctypes.c_char_p
LIB.sf_strerror.argtypes = [ctypes.c_void_p]
LIB.sf_error_str.restype = ctypes.c_char_p
LIB.sf_error_str.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
LIB.sf_close.argtypes = [ctypes.c_void_p]
LIB.sf_format_check.argtypes = [ctypes.POINTER(SF_INFO)]
LIB.sf_command.restype = ctypes.c_int
LIB.sf_command.argtypes = [ctypes.c_void_p, ctypes.c_int,
                           ctypes.c_void_p, ctypes.c_int]
LIB.sf_readf_short.restype = ctypes.c_int64
LIB.sf_readf_short.argtypes = [ctypes.c_void_p,
                               ctypes.POINTER(ctypes.c_short), ctypes.c_int64]
LIB.sf_version_string.restype = ctypes.c_char_p


def enum(count_cmd, item_cmd):
    n = ctypes.c_int(0)
    LIB.sf_command(None, count_cmd, ctypes.byref(n), ctypes.sizeof(n))
    out = {}
    for i in range(n.value):
        fi = SF_FORMAT_INFO()
        fi.format = i
        LIB.sf_command(None, item_cmd, ctypes.byref(fi), ctypes.sizeof(fi))
        out[fi.format] = (fi.name.decode(),
                          (fi.extension or b"").decode())
    return out


def open_source(source):
    """source='path' -> sf_open(argv path); 'fd' -> sf_open_fd(dup(0)) — the
    genuine anonymous bound: an fd with no name at all (pipe on stdin_pipe,
    seekable file fd on redirected_fd)."""
    info = SF_INFO()
    if source == "path":
        snd = LIB.sf_open(os.fsencode(sys.argv[3]), SFM_READ,
                          ctypes.byref(info))
        via = "sf_open"
    else:
        fd = os.dup(0)
        snd = LIB.sf_open_fd(fd, SFM_READ, ctypes.byref(info), 0)
        via = "sf_open_fd"
    return snd, info, via


def name_of(fmt, majors, subs):
    mj = majors.get(fmt & 0x0FFF0000, (None, None))[0]
    st = subs.get(fmt & 0x0000FFFF, (None, None))[0]
    return "%s/%s" % (mj, st) if mj else None


def main():
    mode = sys.argv[1]
    majors = enum(SFC_GET_FORMAT_MAJOR_COUNT, SFC_GET_FORMAT_MAJOR)
    subs = enum(SFC_GET_FORMAT_SUBTYPE_COUNT, SFC_GET_FORMAT_SUBTYPE)
    if mode == "formats":
        json.dump({"libsndfile_version": LIB.sf_version_string().decode(),
                   "majors": {hex(k): v[0] for k, v in majors.items()},
                   "subs": {hex(k): v[0] for k, v in subs.items()}},
                  sys.stdout, indent=1)
        print()
        return 0
    snd, info, via = open_source(sys.argv[2])
    if not snd:
        verdict = {"sf_open_via": via, "format_hex": None,
                   "sndfile_format": None, "sf_frames": None,
                   "samplerate": None, "channels": None,
                   "sf_seekable": None, "sf_format_check": None,
                   "sf_decode_frames": None,
                   "error": LIB.sf_strerror(None).decode()}
        json.dump(verdict, sys.stdout, indent=1)
        print()
        return 0
    verdict = {"sf_open_via": via,
               "format_hex": "0x%08x" % info.format,
               "sndfile_format": name_of(info.format, majors, subs),
               "sf_frames": info.frames, "samplerate": info.samplerate,
               "channels": info.channels,
               "sf_seekable": bool(info.seekable),
               "sf_format_check": bool(LIB.sf_format_check(
                   ctypes.byref(info)))}
    if mode == "read":
        total = 0
        buf = (ctypes.c_short * 65536)()
        while True:
            got = LIB.sf_readf_short(snd, buf, 65536)
            if got <= 0:
                break
            total += got
        ebuf = ctypes.create_string_buffer(256)
        LIB.sf_error_str(snd, ebuf, 256)
        err = ebuf.value.decode(errors="replace")
        verdict["sf_decode_frames"] = total
        verdict["error"] = None if err in ("", "No Error.") else err
    else:
        verdict["sf_decode_frames"] = None
        verdict["error"] = None
    LIB.sf_close(snd)
    json.dump(verdict, sys.stdout, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
