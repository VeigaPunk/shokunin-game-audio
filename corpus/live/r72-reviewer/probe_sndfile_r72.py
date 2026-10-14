#!/usr/bin/env python3
"""r72-reviewer: INDEPENDENT libsndfile 1.2.2 verdict matrix on the 9-member
transport corpus (4 arms), written from the API surface directly rather than
reusing the frontier harness, so the review has its own measurement path.

Arms mirror TRANSPORT_R67_ARMS:
  file          sf_open(path)                        named,   seekable
  stdin_pipe    sf_open_fd(dup(pipe r))              unnamed, unseekable
  redirected_fd sf_open_fd(dup(fd of file))          unnamed, seekable
  fifo_path     sf_open(fifo) + writer thread        named,   unseekable

Verdict: (format_name, frames, read_frames, error). A NULL SNDFILE* is a
reject; sf_strerror(NULL) carries the reason. Also records the raw
`sndfile-info` stdout verdict lines per member for the CLI leg.
"""
import ctypes, json, os, subprocess, sys, tempfile, threading, time

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
LIB.sf_open_fd.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(SF_INFO), ctypes.c_int]
LIB.sf_strerror.restype = ctypes.c_char_p
LIB.sf_strerror.argtypes = [ctypes.c_void_p]
LIB.sf_error_str.restype = ctypes.c_char_p
LIB.sf_error_str.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
LIB.sf_close.argtypes = [ctypes.c_void_p]
LIB.sf_format_check.argtypes = [ctypes.POINTER(SF_INFO)]
LIB.sf_command.restype = ctypes.c_int
LIB.sf_command.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
LIB.sf_readf_short.restype = ctypes.c_int64
LIB.sf_readf_short.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_short), ctypes.c_int64]
LIB.sf_version_string.restype = ctypes.c_char_p


def names_table():
    def enum(count_cmd, item_cmd):
        n = ctypes.c_int(0)
        LIB.sf_command(None, count_cmd, ctypes.byref(n), ctypes.sizeof(n))
        out = {}
        for i in range(n.value):
            fi = SF_FORMAT_INFO()
            fi.format = i
            LIB.sf_command(None, item_cmd, ctypes.byref(fi), ctypes.sizeof(fi))
            out[fi.format] = fi.name.decode() if fi.name else None
        return out
    return enum(SFC_GET_FORMAT_MAJOR_COUNT, SFC_GET_FORMAT_MAJOR), \
        enum(SFC_GET_FORMAT_SUBTYPE_COUNT, SFC_GET_FORMAT_SUBTYPE)


MAJORS, SUBS = names_table()


def verdict(snd, info):
    if not snd:
        return {"format_name": None, "frames": None, "read_frames": None,
                "error": LIB.sf_strerror(None).decode(errors="replace")}
    name = "%s/%s" % (MAJORS.get(info.format & 0x0FFF0000, "?"),
                      SUBS.get(info.format & 0x0000FFFF, "?"))
    buf = (ctypes.c_short * 65536)()
    got = LIB.sf_readf_short(snd, buf, 65536)
    ebuf = ctypes.create_string_buffer(256)
    LIB.sf_error_str(snd, ebuf, 256)
    out = {"format_name": name, "format_hex": hex(info.format),
           "frames": info.frames, "samplerate": info.samplerate,
           "channels": info.channels, "sf_seekable": bool(info.seekable),
           "format_check": bool(LIB.sf_format_check(ctypes.byref(info))),
           "read_frames": got, "error": ebuf.value.decode(errors="replace") or None}
    LIB.sf_close(snd)
    return out


def leg_file(path):
    info = SF_INFO()
    return verdict(LIB.sf_open(os.fsencode(path), SFM_READ, ctypes.byref(info)), info)


def leg_fd(fd_source, data=None):
    if data is not None:
        r, w = os.pipe()
        os.write(w, data)
        os.close(w)
        fd = r
    else:
        fd = os.open(fd_source, os.O_RDONLY)
    try:
        info = SF_INFO()
        return verdict(LIB.sf_open_fd(fd, SFM_READ, ctypes.byref(info), 0), info)
    finally:
        os.close(fd)


def leg_fifo(path, data, hold=1.0):
    tmp = tempfile.mkdtemp(prefix="r72-reviewer-")
    fifo = os.path.join(tmp, os.path.basename(path))
    os.mkfifo(fifo)

    def feed():
        try:
            with open(fifo, "wb") as w:
                w.write(data)
                w.flush()
        except OSError:
            pass
        time.sleep(hold)

    t = threading.Thread(target=feed, daemon=True)
    t.start()
    try:
        return leg_file(fifo)
    finally:
        t.join(timeout=hold + 5)
        os.unlink(fifo)
        os.rmdir(tmp)


def info_stdout(path):
    p = subprocess.run(["sndfile-info", path], capture_output=True, timeout=20)
    text = p.stdout.decode(errors="replace")
    return {"exit": p.returncode,
            "head": [ln for ln in text.splitlines()[:6]],
            "error_lines": [ln for ln in text.splitlines() if ln.startswith("Error")]}


def main():
    members = json.loads(sys.argv[1])
    out = {"libsndfile": LIB.sf_version_string().decode(), "members": {}}
    for name, rel in members.items():
        path = os.path.abspath(rel)
        data = open(path, "rb").read()
        arms = {"file": leg_file(path),
                "stdin_pipe": leg_fd(None, data=data),
                "redirected_fd": leg_fd(path),
                "fifo_path": leg_fifo(path, data)}
        out["members"][name] = {"path": rel, "bytes": len(data), "arms": arms,
                                "sndfile_info": info_stdout(path)}
        print(f"{name}: " + "; ".join(
            f"{a}={v['format_name'] or 'REJ'}({v['read_frames']})"
            for a, v in arms.items()), file=sys.stderr)
    json.dump(out, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
