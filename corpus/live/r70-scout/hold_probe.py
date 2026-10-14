#!/usr/bin/env python3
"""r70-scout: measure the fifo writer-attach window for dec_act.

Two probes, all state inside this scratch dir:
 A) strace -tt -f on a held-writer fifo leg -> wall-clock of open#1,
    ffmpeg execve, open#2.
 B) hold-ladder sanity reps (h = 0, 0.05) on dec_act to show which
    verdict cell lands; NOT the author's full ladder/rep battery.
"""
import os, re, signal, subprocess, sys, tempfile, threading, time
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SCRATCH = ROOT / "corpus/live/r70-scout"
MEMBER = ROOT / "corpus/live/round-66/pair_dec_act.wav"
ARM_TIMEOUT = 8.0

def run_leg(fifo, hold_s, timeout=ARM_TIMEOUT):
    """Mirrors transport_matrix's fifo arm; returns (exit, error, elapsed, stderr_tail)."""
    data = MEMBER.read_bytes()
    def feed():
        try:
            with fifo.open("wb") as fh:
                fh.write(data); fh.flush()
                if hold_s: time.sleep(hold_s)
        except OSError:
            pass
    w = threading.Thread(target=feed, daemon=True); w.start()
    t0 = time.time()
    p = subprocess.Popen(["sox", "-V6", str(fifo), "-n", "stat"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True)
    try:
        _o, err = p.communicate(timeout=timeout)
        code, to = p.returncode, False
    except subprocess.TimeoutExpired:
        to = True
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        try: _o, err = p.communicate(timeout=5)
        except subprocess.TimeoutExpired: err = b""
        code = None
    el = time.time() - t0
    w.join(timeout=hold_s + 5)
    text = err.decode(errors="replace")
    fails = [l for l in text.strip().splitlines() if "sox FAIL" in l]
    m = re.search(r"':\s*(.*)$", fails[-1]) if fails else None
    e = m.group(1) if m else ("TIMEOUT-killpg" if to else "no-FAIL")
    return code, e, round(el, 3), text.strip().splitlines()[-1][:120] if text.strip() else ""

def main():
    fifo = SCRATCH / "pair_dec_act.wav"
    if fifo.exists(): fifo.unlink()
    os.mkfifo(fifo)
    print("# A) strace'd held-writer leg (hold=1.0)")
    tr = SCRATCH / "strace-tt.txt"
    p = subprocess.Popen(["strace", "-tt", "-f", "-o", str(tr),
                          "sox", "-V4", str(fifo), "-n", "stat"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    data = MEMBER.read_bytes()
    def feedh():
        try:
            with fifo.open("wb") as fh:
                fh.write(data); fh.flush(); time.sleep(1.0)
        except OSError: pass
    w = threading.Thread(target=feedh, daemon=True); w.start()
    try: p.wait(timeout=ARM_TIMEOUT)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL); p.wait()
    w.join(timeout=7)
    print("strace ->", tr)
    print("# B) hold sanity reps on dec_act fifo_path arm")
    for h in (0.0, 0.05):
        for i in range(5):
            code, e, el, tail = run_leg(fifo, h)
            print(f"h={h:<5} rep{i}: exit={code} err={e[:60]!r} t={el}s")
    fifo.unlink(missing_ok=True)

if __name__ == "__main__":
    sys.exit(main())
