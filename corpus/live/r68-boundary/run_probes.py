#!/usr/bin/env python3
"""r68 boundary — POST-TABLE FALLBACK edge matrix.

The r68 declared claim: post-table fallback forks on transport seekability
({file, redirected_fd} vs {stdin_pipe, fifo_path}). Source read says the real
discriminators are (a) ft->io_type == lsx_io_pipe — only `|cmd` inputs, and
(b) lsx_find_file_extension(path) — the NAME's extension, not the fd class.
This matrix measures a no-match member across the r67 transport set plus the
new fallback-specific arms:

  file / pipe(-) / redir(-<) / fifo / devstdin_reg / devstdin_pipe /
  procfd_reg / procfd_pipe / memfd / owronlyfd / opathfd / sockstdin /
  sockpath / tmpfs                    (r67 set)
  popen       `|cat <path>`           — the ONLY lsx_io_pipe arm
  fifo_wav    fifo named *.wav        — non-seekable + known extension
  fifo_noext  fifo named without ext  — non-seekable + no extension
  file_noext  regular file, no ext    — seekable + no extension
  magic       --magic flag on file    — libmagic between CHECK table and fallback

Each leg: `sox -V4 <input> -n stat` -> detected format, samples, exit, msg.
"""
import os, re, socket, subprocess, sys, tempfile, threading, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROBES = ROOT / "probes"
LOGS = ROOT / "runs" / "logs"
SOX = "/usr/bin/sox"
DET = re.compile(r"detected file format type `([^']+)'")
SMP = re.compile(r"Samples read:\s+(\d+)")
ASSUME = re.compile(r"assuming input pipe")


def run(argv, stdin=None, pass_fds=(), timeout=20, cwd=None):
    p = subprocess.run(argv, stdin=stdin, capture_output=True,
                       pass_fds=pass_fds, timeout=timeout,
                       cwd=cwd or str(PROBES))
    out = (p.stderr or b"").decode(errors="replace") + \
          (p.stdout or b"").decode(errors="replace")
    det = DET.search(out)
    smp = SMP.search(out)
    assume = bool(ASSUME.search(out))
    firstmsg = ""
    for line in out.splitlines():
        if "sox FAIL" in line or "sox WARN" in line:
            firstmsg = line.strip()
            break
    return {"exit": p.returncode, "detected": det.group(1) if det else "",
            "assume_sox": assume,
            "samples": smp.group(1) if smp else "", "msg": firstmsg,
            "raw": out}


def cat_writer(path, wfd):
    with open(path, "rb") as f:
        data = f.read()
    try:
        os.write(wfd, data)
    finally:
        os.close(wfd)


def fifo_leg(path, fifo_name=None, hold=0.0):
    fifo = PROBES / (fifo_name or ".fifo_probe")
    try:
        os.unlink(fifo)
    except FileNotFoundError:
        pass
    os.mkfifo(fifo)
    def writer():
        fd = os.open(fifo, os.O_WRONLY)
        data = open(path, "rb").read()
        os.write(fd, data)
        if hold:
            time.sleep(hold)
        os.close(fd)
    t = threading.Thread(target=writer, daemon=True)
    t.start()
    try:
        res = run([SOX, "-V4", str(fifo), "-n", "stat"])
    finally:
        t.join()
        os.unlink(fifo)
    return res


def leg(name, path):
    res = {}
    if name == "file":
        res = run([SOX, "-V4", str(path), "-n", "stat"])
    elif name == "file_noext":
        res = run([SOX, "-V4", str(path), "-n", "stat"])
    elif name == "magic":
        res = run([SOX, "--magic", "-V4", str(path), "-n", "stat"])
    elif name == "popen":
        res = run([SOX, "-V4", f"|cat {path}", "-n", "stat"])
    elif name == "pipe":
        r, w = os.pipe()
        t = threading.Thread(target=cat_writer, args=(path, w), daemon=True)
        t.start()
        res = run([SOX, "-V4", "-", "-n", "stat"], stdin=r)
        os.close(r); t.join()
    elif name == "redir":
        fd = os.open(path, os.O_RDONLY)
        res = run([SOX, "-V4", "-", "-n", "stat"], stdin=fd)
        os.close(fd)
    elif name == "fifo":
        res = fifo_leg(path)
    elif name == "fifo_wav":
        res = fifo_leg(path, fifo_name=".fifo_probe.wav")
    elif name == "fifo_noext":
        res = fifo_leg(path, fifo_name=".fifo_probe")
    elif name == "devstdin_reg":
        fd = os.open(path, os.O_RDONLY)
        res = run([SOX, "-V4", "/dev/stdin", "-n", "stat"], stdin=fd)
        os.close(fd)
    elif name == "devstdin_pipe":
        r, w = os.pipe()
        t = threading.Thread(target=cat_writer, args=(path, w), daemon=True)
        t.start()
        res = run([SOX, "-V4", "/dev/stdin", "-n", "stat"], stdin=r)
        os.close(r); t.join()
    elif name == "procfd_reg":
        fd = os.open(path, os.O_RDONLY)
        res = run([SOX, "-V4", f"/proc/self/fd/{fd}", "-n", "stat"], pass_fds=(fd,))
        os.close(fd)
    elif name == "procfd_pipe":
        r, w = os.pipe()
        data = open(path, "rb").read()
        os.write(w, data); os.close(w)
        res = run([SOX, "-V4", f"/proc/self/fd/{r}", "-n", "stat"], pass_fds=(r,))
        os.close(r)
    elif name == "memfd":
        fd = os.memfd_create("r68memfd")
        data = open(path, "rb").read()
        os.write(fd, data); os.lseek(fd, 0, os.SEEK_SET)
        res = run([SOX, "-V4", f"/proc/self/fd/{fd}", "-n", "stat"], pass_fds=(fd,))
        os.close(fd)
    elif name == "owronlyfd":
        fd = os.open(path, os.O_WRONLY)
        res = run([SOX, "-V4", f"/proc/self/fd/{fd}", "-n", "stat"], pass_fds=(fd,))
        os.close(fd)
    elif name == "opathfd":
        fd = os.open(path, os.O_PATH)
        res = run([SOX, "-V4", f"/proc/self/fd/{fd}", "-n", "stat"], pass_fds=(fd,))
        os.close(fd)
    elif name == "sockstdin":
        s1, s2 = socket.socketpair()
        data = open(path, "rb").read()
        def writer():
            try:
                s2.sendall(data)
            finally:
                s2.close()
        t = threading.Thread(target=writer, daemon=True); t.start()
        res = run([SOX, "-V4", "-", "-n", "stat"], stdin=s1.fileno())
        s1.close(); t.join()
    elif name == "sockpath":
        spath = str(PROBES / ".sock_probe")
        try:
            os.unlink(spath)
        except FileNotFoundError:
            pass
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(spath); srv.listen(1)
        res = run([SOX, "-V4", spath, "-n", "stat"], timeout=10)
        srv.close(); os.unlink(spath)
    elif name == "tmpfs":
        dst = Path("/dev/shm") / f"r68_{os.getpid()}_{Path(path).name}"
        dst.write_bytes(open(path, "rb").read())
        res = run([SOX, "-V4", str(dst), "-n", "stat"])
        dst.unlink()
    else:
        raise ValueError(name)
    return res


TRANSPORTS = ["file", "pipe", "redir", "fifo", "fifo_wav", "fifo_noext",
              "file_noext", "popen", "magic",
              "devstdin_reg", "devstdin_pipe", "procfd_reg", "procfd_pipe",
              "memfd", "owronlyfd", "opathfd", "sockstdin", "sockpath", "tmpfs"]

# member name -> probe file; file_noext uses a no-dot sibling path
FILES = [
    "nomatch_txt.wav",      # no-match + known ext -> extension fallback
    "nomatch_txt.mp3",      # no-match + mp3 ext
    "nomatch_txt.txw",      # no-match + txw ext (pipe-refusal handler)
    "nomatch_txt.smp",      # no-match + smp ext (pipe-refusal handler)
    "nomatch_txt.bin",      # no-match + handler-less ext
    "nomatch_riff.bin",     # RIFF-flavoured no-match
    "nomatch_png.bin",      # libmagic-known no-match
    "nomatch_zeros.snd",    # ext-gated sndr CHECK inside the table
    "nomatch_zeros.bin",    # same bytes, .bin ext
    "g_txw_hcom.bin",       # txw-detected member (r67 probe family)
    "p_smp_intact.bin",     # smp-detected member
]


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    rows = []
    only_t = only_f = None
    for a in sys.argv[1:]:
        if a.startswith("t:"):
            only_t = a[2:].split(",")
        elif a.startswith("f:"):
            only_f = a[2:].split(",")
    (ROOT / "runs").mkdir(exist_ok=True)
    out_tsv = ROOT / "runs" / "edge_matrix.tsv"
    new = not out_tsv.exists()
    with open(out_tsv, "a") as tsv:
        if new:
            tsv.write("member\ttransport\texit\tdetected\tassume_sox\tsamples\tmsg\n")
        for fn in FILES:
            if only_f and fn not in only_f:
                continue
            path = PROBES / fn
            if not path.exists():
                continue
            noext = PROBES / (Path(fn).stem + "_noext")
            if not noext.exists() and "." in Path(fn).name:
                noext.write_bytes(path.read_bytes())
            for tr in TRANSPORTS:
                if only_t and tr not in only_t:
                    continue
                use = noext if tr == "file_noext" else path
                if tr == "file_noext" and not noext.exists():
                    continue
                try:
                    r = leg(tr, use)
                except subprocess.TimeoutExpired:
                    r = {"exit": "TIMEOUT", "detected": "", "assume_sox": "",
                         "samples": "", "msg": "leg timed out", "raw": ""}
                except Exception as e:
                    r = {"exit": "EXC", "detected": "", "assume_sox": "",
                         "samples": "", "msg": f"{type(e).__name__}: {e}", "raw": ""}
                tag = f"{fn}@noext" if tr == "file_noext" else fn
                safe = tag.replace("/", "_")
                (LOGS / f"{safe}.{tr}.log").write_text(r.get("raw", ""))
                row = (tag, tr, r["exit"], r["detected"], r["assume_sox"],
                       r["samples"], r["msg"][:110])
                rows.append(row)
                tsv.write("\t".join(str(x) for x in row) + "\n")
                print("\t".join(str(x) for x in row), flush=True)


if __name__ == "__main__":
    main()
