#!/usr/bin/env python3
"""r67-scribe: transport matrix extension — second sitting.

Two additions over run_transport.py's matrix (runs/transport-matrix.tsv):

1. `fifo_hold` transport: named fifo where the parent holds the fifo O_RDWR
   for the whole leg, so the act->ffmpeg bridge's second open() never blocks
   (a writer is always attached) and the writer-close is driven by evidence,
   not a timing constant: after the payload write we poll FIONREAD until the
   pipe buffer is drained (the ffmpeg child consumed the post-prefetch tail)
   or sox exits, then close -> deterministic EOF. This isolates the
   "contended fifo" verdict the author's pinned 1.0 s writer-linger lands,
   without depending on spawn-latency margins.

2. Decode-fork carriers the tracked member set lacks: the brief's "88
   samples on pipe" is r65-critic's 600-B D2 construction; r65-boundary's
   coll_* probes are byte-identical to tracked members (g726) or carry a
   decodable encoding (alaw). Run all four base transports + fifo_hold so
   the decode-level fork is in this seat's own matrix.

Bare-writer `fifo` on act members already measured as HANG in
transport-matrix.tsv (SCRIBE-TIMEOUT-30s-killpg) — that IS the verdict for
that protocol; fifo_hold measures the other fifo cell.

Emits runs/transport-matrix-ext.tsv + logs under runs/logs/.
"""
import array
import fcntl
import os
import re
import signal
import subprocess
import sys
import termios
import time
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SCRATCH = ROOT / "corpus/live/r67-scribe"
LOGS = SCRATCH / "runs" / "logs"
TSV = SCRATCH / "runs" / "transport-matrix-ext.tsv"
TIMEOUT = 30
HOLD_CAP_S = 15      # upper bound waiting for the bridge's second-open drain
HOLD_GRACE_S = 0.4   # settle time between observed drain and writer close

# Five transports x the decode-fork carriers; fifo_hold-only on members whose
# bare-fifo cell already recorded HANG (act) plus non-act controls.
FULL = [
    ("boundary", "corpus/live/r65-critic/var/D2_gsrtULAW+act.wav"),
    ("boundary", "corpus/live/r65-critic/var/D2b_gsrtALAW+act.wav"),
    ("boundary", "corpus/live/r65-boundary/probes/coll_gsrt_alaw.wav"),
    ("boundary", "corpus/live/r65-boundary/probes/coll_gsrt_g726.wav"),
    ("boundary", "corpus/live/r65-boundary/probes/coll_act_base.wav"),
]
HOLD_ONLY = [
    ("tracked", "corpus/live/round-63/pair_route_84.wav"),
    ("tracked", "corpus/live/round-65/pair_preempt_act.wav"),
    ("tracked", "corpus/live/round-66/pair_dec_act.wav"),
    ("tracked", "corpus/live/round-65/pair_preempt_gsrt.wav"),
    ("tracked", "corpus/live/round-66/pair_dec_hcom.wav"),
    ("tracked", "corpus/artifacts/ui.wav"),
]


def sox_guarded(args, stdin=None, timeout=TIMEOUT):
    p = subprocess.Popen(args, stdin=stdin, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, start_new_session=True)
    timed_out = False
    try:
        _out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            _out, err = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            err = b""
    return p.returncode, err, timed_out


def parse(stderr: bytes, rc: int, timed_out: bool):
    text = (stderr or b"").decode(errors="replace")
    det = re.search(r"detected file format type `(\S+?)'", text)
    samp = re.search(r"Samples read:\s*(\d+)", text)
    lines = [l for l in text.splitlines() if "FAIL" in l or "WARN" in l]
    tail = lines[-1].split("sox ", 1)[-1][:140] if lines else "ok"
    if timed_out:
        tail = f"SCRIBE-TIMEOUT-{TIMEOUT}s-killpg | " + tail
    return (det.group(1) if det else "-", rc,
            int(samp.group(1)) if samp else -1, tail)


def run_file(path):
    return sox_guarded(["sox", "-V4", str(path), "-n", "stat"])


def run_pipe(path):
    cat = subprocess.Popen(["cat", str(path)], stdout=subprocess.PIPE)
    try:
        return sox_guarded(["sox", "-V4", "-", "-n", "stat"], stdin=cat.stdout)
    finally:
        cat.stdout.close()
        cat.wait()


def run_redir(path):
    with open(path, "rb") as fh:
        return sox_guarded(["sox", "-V4", "-", "-n", "stat"], stdin=fh)


def run_fifo(path, fifo_path):
    """Bare one-shot writer (same protocol as run_transport.py post-fix)."""
    p = subprocess.Popen(["sox", "-V4", str(fifo_path), "-n", "stat"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True)
    wr = open(fifo_path, "wb")
    cat = subprocess.Popen(["cat", str(path)], stdout=wr,
                           stderr=subprocess.DEVNULL)
    wr.close()
    timed_out = False
    try:
        _out, err = p.communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            _out, err = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            err = b""
    finally:
        try:
            cat.wait(timeout=10)
        except subprocess.TimeoutExpired:
            cat.kill()
            cat.wait()
    return p.returncode, err, timed_out


def run_fifo_hold(path, fifo_path):
    """Held-writer fifo: parent opens O_RDWR before sox starts, so the
    bridge's second open() always succeeds; payload is written once, then
    the writer stays attached until the pipe drains (FIONREAD==0, i.e. a
    second reader consumed the tail) or sox exits; close -> true EOF."""
    fd = os.open(fifo_path, os.O_RDWR)
    p = subprocess.Popen(["sox", "-V4", str(fifo_path), "-n", "stat"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True)
    os.write(fd, path.read_bytes())
    buf = array.array("i", [0])
    deadline = time.time() + HOLD_CAP_S
    drained = False
    while time.time() < deadline:
        if p.poll() is not None:
            break
        fcntl.ioctl(fd, termios.FIONREAD, buf, True)
        if buf[0] == 0:
            drained = True
            break
        time.sleep(0.05)
    time.sleep(HOLD_GRACE_S)
    os.close(fd)
    timed_out = False
    try:
        _out, err = p.communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            _out, err = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            err = b""
    note = f"SCRIBE-HOLD:drained={drained} t={round(deadline - time.time(), 2)}s-left\n"
    return p.returncode, (err or b"") + note.encode(), timed_out


def emit(rows, cls, name, transport, result):
    rc, err, to = result
    (LOGS / f"{name}.{transport}.log").write_bytes(err or b"")
    det, rc2, samp, tail = parse(err, rc, to)
    row = f"{cls}\t{name}\t{transport}\t{det}\t{rc2}\t{samp}\t{tail}"
    rows.append(row)
    print(row, flush=True)


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    rows = ["class\tfixture\ttransport\tdetected\texit\tsamples\ttail"]
    for cls, rel in FULL:
        path = ROOT / rel
        name = Path(rel).name
        emit(rows, cls, name, "file", run_file(path))
        emit(rows, cls, name, "pipe", run_pipe(path))
        emit(rows, cls, name, "redir", run_redir(path))
        for transport, fn in (("fifo", run_fifo), ("fifo_hold", run_fifo_hold)):
            fifo_path = SCRATCH / "runs" / f"{name}.fifo"
            if fifo_path.exists():
                fifo_path.unlink()
            os.mkfifo(fifo_path)
            try:
                emit(rows, cls, name, transport, fn(path, fifo_path))
            finally:
                fifo_path.unlink(missing_ok=True)
    for cls, rel in HOLD_ONLY:
        path = ROOT / rel
        name = Path(rel).name
        fifo_path = SCRATCH / "runs" / f"{name}.fifo"
        if fifo_path.exists():
            fifo_path.unlink()
        os.mkfifo(fifo_path)
        try:
            emit(rows, cls, name, "fifo_hold", run_fifo_hold(path, fifo_path))
        finally:
            fifo_path.unlink(missing_ok=True)
    TSV.write_text("\n".join(rows) + "\n")


if __name__ == "__main__":
    sys.exit(main())
