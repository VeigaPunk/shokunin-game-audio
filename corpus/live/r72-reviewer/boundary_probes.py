#!/usr/bin/env python3
"""r72-reviewer: boundary probes that a third-decoder transport arm must get
right, measured independently before reviewing the author's implementation.

A. sndfile-info on a FIFO (named, unseekable) and on /dev/stdin — what the CLI
   leg can and cannot see (the CLI takes paths only).
B. sf_open("/dev/stdin") / sf_open("/dev/fd/0") — the *approximated* anonymous
   arm, vs the true sf_open_fd boundary. Records whether the path spelling
   changes the verdict (it must not be used as the anonymous bound if it does).
C. sf_open on a fifo with NO writer attached — does the reader block (needs a
   bounded leg) or fail fast?
"""
import ctypes, json, os, subprocess, sys, tempfile, threading, time

LIB = ctypes.CDLL("libsndfile.so.1")
SFM_READ = 0x10


class SF_INFO(ctypes.Structure):
    _fields_ = [("frames", ctypes.c_int64), ("samplerate", ctypes.c_int),
                ("channels", ctypes.c_int), ("format", ctypes.c_int),
                ("sections", ctypes.c_int), ("seekable", ctypes.c_int)]


LIB.sf_open.restype = ctypes.c_void_p
LIB.sf_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(SF_INFO)]
LIB.sf_open_fd.restype = ctypes.c_void_p
LIB.sf_open_fd.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(SF_INFO), ctypes.c_int]
LIB.sf_strerror.restype = ctypes.c_char_p
LIB.sf_strerror.argtypes = [ctypes.c_void_p]
LIB.sf_readf_short.restype = ctypes.c_int64
LIB.sf_readf_short.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_short), ctypes.c_int64]
LIB.sf_close.argtypes = [ctypes.c_void_p]

SND = "corpus/live/round-69/extsuffix_nomatch.snd"
WAV = "corpus/live/round-66/pair_dec_act.wav"
out = {}


def verdict(snd, info):
    if not snd:
        return {"format": None, "error": LIB.sf_strerror(None).decode(errors="replace")}
    buf = (ctypes.c_short * 65536)()
    got = LIB.sf_readf_short(snd, buf, 65536)
    LIB.sf_close(snd)
    return {"format": hex(info.format), "frames": info.frames,
            "samplerate": info.samplerate, "channels": info.channels,
            "seekable": bool(info.seekable), "read_frames": got}


def sfopen_path(p):
    info = SF_INFO()
    return verdict(LIB.sf_open(os.fsencode(p), SFM_READ, ctypes.byref(info)), info)


def fifo_with_writer(member, hold=1.0):
    tmp = tempfile.mkdtemp(prefix="r72-rev-fifo-")
    fifo = os.path.join(tmp, os.path.basename(member))
    os.mkfifo(fifo)
    data = open(member, "rb").read()

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
    return tmp, fifo, t, hold


# --- A: CLI leg on a fifo and on /dev/stdin -------------------------------
tmp, fifo, t, hold = fifo_with_writer(SND)
try:
    p = subprocess.run(["sndfile-info", fifo], capture_output=True, timeout=20)
    out["A_sndfile_info_fifo"] = {
        "exit": p.returncode,
        "lines": [ln for ln in p.stdout.decode(errors="replace").splitlines()
                  if ln.strip()][:8]}
except subprocess.TimeoutExpired:
    out["A_sndfile_info_fifo"] = {"exit": None, "lines": ["BLOCKED >20s"]}
t.join(timeout=hold + 5)
os.unlink(fifo)
os.rmdir(tmp)

p = subprocess.run(["sndfile-info", "/dev/stdin"], stdin=open(SND, "rb"),
                   capture_output=True, timeout=20)
out["A_sndfile_info_dev_stdin"] = {
    "exit": p.returncode,
    "lines": [ln for ln in p.stdout.decode(errors="replace").splitlines() if ln.strip()][:6]}

# --- B: path-spelling anonymous arms --------------------------------------
# /dev/stdin with the member on stdin: does sf_open see a name? (it must not,
# for the anonymous bound to be honest)
r, w = os.pipe()
os.write(w, open(SND, "rb").read())
os.close(w)
saved = os.dup(0)
os.dup2(r, 0)
try:
    out["B_sf_open_dev_stdin_snd"] = sfopen_path("/dev/stdin")
    out["B_sf_open_dev_fd0_snd"] = sfopen_path("/dev/fd/0")
finally:
    os.dup2(saved, 0)
    os.close(saved)
    os.close(r)

# true fd boundary for the same bytes
r, w = os.pipe()
os.write(w, open(SND, "rb").read())
os.close(w)
info = SF_INFO()
out["B_sf_open_fd_snd"] = verdict(
    LIB.sf_open_fd(r, SFM_READ, ctypes.byref(info), 0), info)
os.close(r)

# --- C: fifo with no writer -----------------------------------------------
tmp = tempfile.mkdtemp(prefix="r72-rev-nowriter-")
fifo = os.path.join(tmp, os.path.basename(WAV))
os.mkfifo(fifo)
res = {}

def open_nowriter():
    try:
        res["verdict"] = sfopen_path(fifo)
    except Exception as exc:  # noqa: BLE001
        res["verdict"] = {"exception": repr(exc)}

th = threading.Thread(target=open_nowriter, daemon=True)
th.start()
th.join(timeout=5)
out["C_fifo_no_writer"] = res.get("verdict", {"blocked": "no return within 5 s"})
os.unlink(fifo)
os.rmdir(tmp)

json.dump(out, sys.stdout, indent=1)
