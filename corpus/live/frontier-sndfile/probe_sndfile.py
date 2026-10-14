#!/usr/bin/env python3
"""frontier-sndfile: libsndfile verdicts on the 4-transport matrix.

Arms (mirroring TRANSPORT_R67_ARMS):
  file          sf_open(path)                          named,   seekable
  stdin_pipe    sf_open_fd(dup(0)) with stdin=pipe     unnamed, unseekable
  redirected_fd sf_open_fd(dup(0)) with stdin=<file    unnamed, seekable
  fifo_path     sf_open(fifo_path) + writer thread     named,   unseekable

Verdict per arm: (format, format_name, format_check, frames, samplerate,
channels, seekable_flag, read_frames, error_string). A NULL SNDFILE* gives
format=None and error=sf_strerror(NULL).

sndfile_info CLI arms are run separately by run_matrix.sh (sndfile-info
takes paths only).
"""
import ctypes, os, sys, json, subprocess, tempfile, threading, time

lib = ctypes.CDLL("libsndfile.so.1")

SFM_READ = 0x10
SFC_GET_FORMAT_INFO = 0x1028

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
lib.sf_open_fd.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(SF_INFO), ctypes.c_int]
lib.sf_strerror.restype = ctypes.c_char_p
lib.sf_strerror.argtypes = [ctypes.c_void_p]
lib.sf_error_str.restype = ctypes.c_char_p
lib.sf_error_str.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
lib.sf_close.argtypes = [ctypes.c_void_p]
lib.sf_format_check.argtypes = [ctypes.POINTER(SF_INFO)]
lib.sf_command.restype = ctypes.c_int
lib.sf_command.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
lib.sf_readf_short.restype = ctypes.c_int64
lib.sf_readf_short.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_short), ctypes.c_int64]

def fmt_names():
    """major|subtype -> (major_name, major_ext, subtype_name) via
    SFC_GET_FORMAT_MAJOR(_COUNT)/SFC_GET_FORMAT_SUBTYPE(_COUNT)."""
    def enum(count_cmd, item_cmd):
        n = ctypes.c_int(0)
        lib.sf_command(None, count_cmd, ctypes.byref(n), ctypes.sizeof(n))
        out = {}
        for i in range(n.value):
            fi = SF_FORMAT_INFO(); fi.format = i
            lib.sf_command(None, item_cmd, ctypes.byref(fi), ctypes.sizeof(fi))
            out[fi.format] = (fi.name.decode(), (fi.extension or b"").decode())
        return out
    majors = enum(0x1030, 0x1031)   # SFC_GET_FORMAT_MAJOR_COUNT/MAJOR
    subs = enum(0x1032, 0x1033)     # SFC_GET_FORMAT_SUBTYPE_COUNT/SUBTYPE
    return {"majors": majors, "subs": subs}

def verdict(snd, info, err_when_null):
    if not snd:
        return {"format": None, "format_name": None, "format_check": None,
                "frames": None, "samplerate": None, "channels": None,
                "sf_seekable": None, "read_frames": None, "error": err_when_null}
    names = fmt_names_cache
    fm = info.format & 0x0FFF0000
    sub = info.format & 0x0000FFFF
    mj = names["majors"].get(info.format & 0x0FFF0000, (None, None))
    st = names["subs"].get(sub, (None, None))
    name = ("%s/%s" % (mj[0], st[0])) if mj[0] else None
    ext = mj[1]
    check = bool(lib.sf_format_check(ctypes.byref(info)))
    buf = (ctypes.c_short * 65536)()
    got = lib.sf_readf_short(snd, buf, 65536)
    ebuf = ctypes.create_string_buffer(256)
    lib.sf_error_str(snd, ebuf, 256)
    errstr = ebuf.value.decode(errors="replace") or None
    lib.sf_close(snd)
    return {"format": hex(info.format), "type_hex": hex(fm), "sub_hex": hex(sub),
            "format_name": name, "format_ext": ext,
            "format_check": check,
            "frames": info.frames, "samplerate": info.samplerate,
            "channels": info.channels, "sf_seekable": bool(info.seekable),
            "read_frames": got, "error": errstr}

def leg_file(path):
    info = SF_INFO()
    snd = lib.sf_open(os.fsencode(path), SFM_READ, ctypes.byref(info))
    err = lib.sf_strerror(None).decode() if not snd else None
    return verdict(snd, info, err)

def leg_fifo(path, data, hold=1.0):
    tmp = tempfile.mkdtemp(prefix="frontier-sndfile-")
    fifo = os.path.join(tmp, os.path.basename(path))
    os.mkfifo(fifo)
    def feed():
        try:
            with open(fifo, "wb") as w:
                w.write(data)
        except (BrokenPipeError, OSError):
            pass
        time.sleep(hold)
    t = threading.Thread(target=feed, daemon=True); t.start()
    try:
        return leg_file(fifo)
    finally:
        t.join(timeout=hold + 5)
        os.unlink(fifo); os.rmdir(tmp)

def leg_fd(source):
    """source: bytes (pipe feed) — we dup a fresh pipe fd filled with data,
    or a path (redirect) — dup an fd opened on the file. Either way the
    decoder sees an anonymous fd: no name at all."""
    if isinstance(source, bytes):
        r, w = os.pipe()
        os.write(w, source); os.close(w)
        fd = r
    else:
        fd = os.open(source, os.O_RDONLY)
    try:
        info = SF_INFO()
        snd = lib.sf_open_fd(fd, SFM_READ, ctypes.byref(info), 0)
        err = lib.sf_strerror(None).decode() if not snd else None
        return verdict(snd, info, err)
    finally:
        os.close(fd)

fmt_names_cache = fmt_names()

def main():
    members = json.loads(sys.argv[1])  # {name: relpath}
    results = {}
    for name, rel in members.items():
        path = os.path.abspath(rel)
        data = open(path, "rb").read()
        e = {}
        e["file"] = leg_file(path)
        e["stdin_pipe"] = leg_fd(data)
        e["redirected_fd"] = leg_fd(path)
        e["fifo_path"] = leg_fifo(path, data)
        results[name] = {"path": rel, "bytes": len(data), "arms": e}
        print(f"{name}: " + "; ".join(
            f"{a}={v['format_name'] or 'REJ'}:{v['read_frames']}:{(v['error'] or '')[:40]}"
            for a, v in e.items()), file=sys.stderr)
    json.dump(results, sys.stdout, indent=1)

if __name__ == "__main__":
    main()
