#!/usr/bin/env python3
"""r67 boundary transport matrix — edge transports outside the declared
{file, stdin-pipe, redirected-fd, fifo-path} arm.

Each leg runs `sox -V4 <input> -n stat` and records:
  detected format (from `detected file format type'X'`),
  stat samples-read, sox exit code, first FAIL/WARN line.

Transports:
  file          sox path
  pipe          cat path | sox -
  redir         sox - < path          (redirected fd: stdin IS the regular file)
  fifo          mkfifo; cat path > f &; sox f
  devstdin_reg  sox /dev/stdin < path
  devstdin_pipe cat path | sox /dev/stdin
  procfd_reg    fd=open(path); sox /proc/self/fd/{fd}   (inherited fd)
  procfd_pipe   fd=pipe-read-end (pre-filled); sox /proc/self/fd/{fd}
  memfd         memfd_create+write; sox /proc/self/fd/{fd}
  owronlyfd     fd=open(path,O_WRONLY); sox /proc/self/fd/{fd}
  opathfd       fd=open(path,O_PATH);  sox /proc/self/fd/{fd}
  sockstdin     sox - ; fd0 = real SOCK_STREAM socketpair (not a pipe)
  sockpath      sox <unix-socket-path>  (open() on a socket inode)
  tmpfs         sox /dev/shm/copy       (regular file, tmpfs backend)
"""
import os, re, socket, subprocess, sys, tempfile, threading, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROBES = ROOT / "probes"
LOGS = ROOT / "runs" / "logs"
SOX = "/usr/bin/sox"
DET = re.compile(r"detected file format type `([^']+)'")
SMP = re.compile(r"Samples read:\s+(\d+)")
FAIL = re.compile(r"^sox (FAIL|WARN).*", re.M)


def run(argv, stdin=None, pass_fds=(), timeout=20):
    p = subprocess.run(argv, stdin=stdin, capture_output=True,
                       pass_fds=pass_fds, timeout=timeout)
    out = (p.stderr or b"").decode(errors="replace") + \
          (p.stdout or b"").decode(errors="replace")
    det = DET.search(out)
    smp = SMP.search(out)
    msgs = FAIL.findall(out)
    firstmsg = ""
    for line in out.splitlines():
        if "sox FAIL" in line or "sox WARN" in line:
            firstmsg = line.strip()
            break
    return {"exit": p.returncode, "detected": det.group(1) if det else "",
            "samples": smp.group(1) if smp else "", "msg": firstmsg,
            "raw": out}


def cat_writer(path, wfd):
    with open(path, "rb") as f:
        data = f.read()
    os.write(wfd, data)
    os.close(wfd)


def leg(name, path):
    res = {}
    if name == "file":
        res = run([SOX, "-V4", str(path), "-n", "stat"])
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
        fifo = PROBES / ".fifo_probe"
        try:
            os.unlink(fifo)
        except FileNotFoundError:
            pass
        os.mkfifo(fifo)
        t = threading.Thread(target=lambda: cat_writer(path, os.open(fifo, os.O_WRONLY)), daemon=True)
        t.start()
        res = run([SOX, "-V4", str(fifo), "-n", "stat"])
        t.join(); os.unlink(fifo)
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
        fd = os.memfd_create("r67memfd")
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
        res_holder = {}
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
        dst = Path("/dev/shm") / f"r67_{os.getpid()}_{Path(path).name}"
        dst.write_bytes(open(path, "rb").read())
        res = run([SOX, "-V4", str(dst), "-n", "stat"])
        dst.unlink()
    else:
        raise ValueError(name)
    return res


TRANSPORTS = ["file", "pipe", "redir", "fifo", "devstdin_reg", "devstdin_pipe",
              "procfd_reg", "procfd_pipe", "memfd", "owronlyfd", "opathfd",
              "sockstdin", "sockpath", "tmpfs"]

FILES = ["pair_route_00.wav", "pair_route_84.wav",
         "pair_valid_8.wav", "pair_valid_9.wav", "pair_valid_24.wav",
         "pair_valid_25.wav", "pair_valid_56.wav", "pair_valid_57.wav",
         "pair_preempt_act.wav", "pair_preempt_both.wav",
         "pair_preempt_gsrt.wav", "pair_preempt_hcom.wav",
         "pair_dec_act.wav", "pair_dec_hcom.wav",
         "pair_lengate_gsrt_24.wav", "pair_lengate_gsrt_25.wav",
         "pair_lengate_hcom_131.wav", "pair_lengate_hcom_132.wav",
         "z_gsrt_ulaw.bin", "z_hcom_dec.bin", "b_wve_dec.bin",
         "g_txw_hcom.bin", "p_smp_intact.bin", "p_voc_intact.bin",
         "z_riff_act.wav", "g_amrnb_hcom.bin", "a_wve_valid.bin"]


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    rows = []
    only = sys.argv[1:] or None
    for fn in FILES:
        path = PROBES / fn
        if not path.exists():
            continue
        for tr in TRANSPORTS:
            if only and tr not in only:
                continue
            try:
                r = leg(tr, path)
            except subprocess.TimeoutExpired:
                r = {"exit": "TIMEOUT", "detected": "", "samples": "",
                     "msg": "leg timed out", "raw": ""}
            except Exception as e:
                r = {"exit": "EXC", "detected": "", "samples": "",
                     "msg": f"{type(e).__name__}: {e}", "raw": ""}
            rows.append((fn, tr, r["exit"], r["detected"], r["samples"], r["msg"]))
            safe = fn.replace("/", "_")
            (LOGS / f"{safe}.{tr}.log").write_text(r.get("raw", ""))
            print(f"{fn}\t{tr}\t{r['exit']}\t{r['detected']}\t{r['samples']}\t{r['msg'][:80]}",
                  flush=True)
    with open(ROOT / "runs" / "edge_matrix.tsv", "a") as f:
        for row in rows:
            f.write("\t".join(str(x) for x in row) + "\n")


if __name__ == "__main__":
    main()
