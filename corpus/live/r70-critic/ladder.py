#!/usr/bin/env python3
"""r70 critic: independent fifo writer-hold ladder on the dec_act member.

Reproduces the arm mechanism from measure_audio.py transport_matrix():
mkfifo -> writer thread (one-shot write, sleep(hold), close) ->
`sox -V6 <fifo> -n stat` bounded by a timeout. Records verdict class,
wall time, and surviving ffmpeg orphans per cell — the mechanism
observables a verdict-only ladder cannot see.
"""
import os, re, subprocess, sys, tempfile, threading, time, json
from pathlib import Path

MEMBER = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/round-66/pair_dec_act.wav")
ARM_TIMEOUT = 10.0
DATA = MEMBER.read_bytes()


def transport_error(text):
    fails = [l for l in text.strip().splitlines() if "sox FAIL" in l]
    if not fails:
        return None
    m = re.search(r"':\s*(.*)$", fails[-1])
    return m.group(1) if m else fails[-1]


def leg(hold, chunk_s=None, tag=""):
    """One fifo leg. chunk_s: if set, write in 100B chunks with this delay
    between chunks (chunked-feed variant); hold is post-write linger."""
    with tempfile.TemporaryDirectory(prefix="r70critic-") as tmp:
        fifo = Path(tmp) / MEMBER.name
        os.mkfifo(fifo)
        def feed():
            try:
                with fifo.open("wb") as fh:
                    if chunk_s is None:
                        fh.write(DATA)
                    else:
                        for i in range(0, len(DATA), 100):
                            fh.write(DATA[i:i+100]); fh.flush()
                            time.sleep(chunk_s)
                    fh.flush()
                    time.sleep(hold)
            except OSError:
                pass
        w = threading.Thread(target=feed, daemon=True)
        t0 = time.monotonic()
        w.start()
        try:
            p = subprocess.run(["sox", "-V6", str(fifo), "-n", "stat"],
                               capture_output=True, timeout=ARM_TIMEOUT)
            wall = time.monotonic() - t0
            text = p.stderr.decode(errors="replace")
            code = p.returncode
            err = transport_error(text)
        except subprocess.TimeoutExpired as e:
            wall = time.monotonic() - t0
            text = (e.stderr or b"").decode(errors="replace")
            code = None
            err = "blocked: no verdict within %.0f s" % ARM_TIMEOUT
        det = re.search(r"detected file format type `(\S+?)'", text)
        read = re.search(r"Samples read:\s*(\d+)", text)
        w.join(timeout=hold + 5)
    return {"hold": hold, "chunk_s": chunk_s, "tag": tag,
            "detected": det.group(1) if det else None,
            "exit": code, "samples": int(read.group(1)) if read else None,
            "error": err, "wall_s": round(wall, 3)}


def orphans():
    """ffmpeg bridge processes still alive, blocked on our fifo shape."""
    try:
        out = subprocess.run(["pgrep", "-af", "ffmpeg -i"], capture_output=True,
                             text=True, timeout=5).stdout
    except Exception:
        return []
    return [l for l in out.splitlines() if "r70critic" in l or "pair_dec_act" in l]


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    holds = [0, 0.05, 0.2, 0.5, 1.0, 2.0]
    rows = []
    for h in holds:
        for r in range(reps):
            row = leg(h)
            rows.append(row)
            print(f"h={h:>5} rep{r}: det={row['detected']} exit={row['exit']} "
                  f"samples={row['samples']} wall={row['wall_s']}s err={row['error']!r}",
                  flush=True)
    # chunked-feed variant: 6 x 100B chunks @50ms = ~300ms feed span, hold=0
    for r in range(reps):
        row = leg(0, chunk_s=0.05)
        rows.append(row)
        print(f"chunked hold=0 rep{r}: det={row['detected']} exit={row['exit']} "
              f"samples={row['samples']} wall={row['wall_s']}s err={row['error']!r}",
              flush=True)
    out = Path(__file__).parent / "ladder_idle.json"
    out.write_text(json.dumps(rows, indent=1))
    orph = orphans()
    print("ORPHANS:", orph if orph else "none")


if __name__ == "__main__":
    main()
