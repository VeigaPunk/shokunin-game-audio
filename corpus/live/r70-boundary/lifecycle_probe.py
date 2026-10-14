#!/usr/bin/env python3
"""r70 boundary — leg lifecycle timing: when does sox exit vs ffmpeg die vs
stderr FAIL appear, for each fifo hang cell.

Runs `sox -V6 <fifo> -n stat` with Popen; polls /proc every 50 ms recording
which of {sox, ffmpeg} are alive + ffmpeg wchan; simultaneously drains the
shared stderr pipe timestamping each line (FAIL visibility vs exit).

Because the ffmpeg grandchild inherits sox's stderr fd, the PIPE stays open
after sox exits — communicate()/pipe-drain only returns at the LAST writer's
death. That IS the canonical `blocked` mechanism under subprocess.run.
"""
import os
import re
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hold_probe import FIFODIR, ROOT, feed_write

MEMBER = "corpus/live/round-66/pair_dec_act.wav"


def find_procs(fifo_str):
    """pid -> (comm, wchan, ppid) for sox/ffmpeg referencing this fifo."""
    out = {}
    for pid in filter(str.isdigit, os.listdir("/proc")):
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                cmd = fh.read().decode(errors="replace").replace("\0", " ")
            if fifo_str not in cmd:
                continue
            comm = Path(f"/proc/{pid}/comm").read_text().strip()
            if comm not in ("sox", "ffmpeg"):
                continue
            wchan = Path(f"/proc/{pid}/wchan").read_text().strip()
            ppid = re.search(r"PPid:\s*(\d+)",
                             Path(f"/proc/{pid}/status").read_text())
            out[pid] = (comm, wchan, ppid.group(1) if ppid else "?")
        except (OSError, FileNotFoundError):
            continue
    return out


def lifecycle(shape, hold, timeout, rdwr_park=None, label=""):
    path = ROOT / MEMBER
    data = path.read_bytes()
    FIFODIR.mkdir(parents=True, exist_ok=True)
    fifo = FIFODIR / f"lfc-{os.getpid()}-{label}.fifo"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    rdwr_fd = None
    threads = []

    def w_linger(h):
        try:
            fd = os.open(str(fifo), os.O_WRONLY)
            os.write(fd, data)
            if h:
                time.sleep(h)
            os.close(fd)
        except OSError:
            pass

    def w_rdwr_park(park):
        # O_RDWR attach before sox spawn, write now, close at +park
        nonlocal rdwr_fd
        rdwr_fd = os.open(str(fifo), os.O_RDWR)
        os.write(rdwr_fd, data)
        if park is not None:
            threading.Thread(target=lambda: (time.sleep(park),
                                             os.close(rdwr_fd)),
                             daemon=True).start()

    t0 = time.monotonic()
    if shape == "rdwr":
        w_rdwr_park(rdwr_park)
    else:
        th = threading.Thread(target=w_linger,
                              args=(0.0 if shape == "oneshot" else hold,),
                              daemon=True)
        threads.append(th)
        th.start()

    proc = subprocess.Popen(["sox", "-V6", str(fifo), "-n", "stat"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, start_new_session=True)
    lines = []

    def drain():
        for raw in proc.stderr:
            lines.append((round(time.monotonic() - t0, 3),
                          raw.decode(errors="replace").rstrip()))
    dt = threading.Thread(target=drain, daemon=True)
    dt.start()

    events = []
    first_seen = {}
    last_seen = {}
    fail_t = None
    while True:
        el = time.monotonic() - t0
        procs = find_procs(str(fifo))
        for pid, info in procs.items():
            first_seen.setdefault(pid, (round(el, 3),) + info)
            last_seen[pid] = (round(el, 3),) + info
        sox_alive = any(c == "sox" for c, _, _ in procs.values())
        ff_alive = any(c == "ffmpeg" for c, _, _ in procs.values())
        if fail_t is None and any("sox FAIL" in l for _, l in lines):
            fail_t = round(el, 3)
        if not sox_alive and not ff_alive and proc.poll() is not None:
            break
        if el > timeout:
            os.killpg(proc.pid, signal.SIGKILL)
            break
        time.sleep(0.05)
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass
    dt.join(timeout=2)
    for th in threads:
        th.join(timeout=2)
    if rdwr_fd is not None:
        try:
            os.close(rdwr_fd)
        except OSError:
            pass
    try:
        fifo.unlink()
    except FileNotFoundError:
        pass
    return {"label": label, "shape": shape, "hold": hold,
            "rdwr_park": rdwr_park, "timeout": timeout,
            "fail_line_at": fail_t, "procs": first_seen,
            "procs_last": last_seen,
            "stderr_lines": lines}


def show(r):
    print(f"### {r['label']} shape={r['shape']} hold={r['hold']} "
          f"rdwr_park={r['rdwr_park']} timeout={r['timeout']}")
    print(f"    FAIL emitted at t={r['fail_line_at']}")
    for pid, (t, comm, wchan, ppid) in sorted(r["procs"].items()):
        lt = r["procs_last"].get(pid, ("?", "", ""))
        print(f"    {comm:7} pid={pid} ppid={ppid} first@{t}s "
              f"last@{lt[0]}s wchan={wchan}->{lt[2] if len(lt) > 2 else ''}")
    interesting = [(t, l) for t, l in r["stderr_lines"]
                   if "FAIL" in l or "detected" in l or "WARN" in l][:8]
    for t, l in interesting:
        print(f"    stderr@{t}: {l[:120]}")
    print()


def main():
    runs = [
        ("writer-gone (oneshot)", "oneshot", 0.0, None, 6.0),
        ("rdwr-park-forever", "rdwr", 1.0, None, 6.0),
        ("rdwr-park-1.5 (EOF late)", "rdwr", 1.0, 1.5, 6.0),
        ("linger-1.0 canonical", "linger", 1.0, None, 6.0),
        ("linger-0.3 short", "linger", 0.3, None, 6.0),
        ("linger-0.08 tiny", "linger", 0.08, None, 6.0),
    ]
    for label, shape, hold, park, to in runs:
        r = lifecycle(shape, hold, to, rdwr_park=park, label=label.split()[0])
        show(r)


if __name__ == "__main__":
    main()
