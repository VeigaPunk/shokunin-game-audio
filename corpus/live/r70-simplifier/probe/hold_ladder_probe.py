#!/usr/bin/env python3
"""r70 simplifier — INDEPENDENT fifo writer-hold ladder on member dec_act.

Mirrors transport_matrix()'s fifo_path arm semantics exactly
(corpus/fixtures/measure_audio.py:276-295): a writer thread does
open("wb") -> write(member bytes) -> flush -> sleep(hold) -> close, while
the reader leg is `sox -V6 <fifo> -n stat` under the 10 s arm timeout.

Axes swept independently of the author's landing:
  hold_s  in {0, 0.05, 0.2, 0.5, 1.0, 2.0}
  feed    in {oneshot (write-all-then-linger), chunked (64 B writes, 25 ms
          apart, then linger)}   -- the fifo_feed contract variants
  reps    = REPS per cell

Every rep uses a fresh tempdir+fifo so no state carries between cells.
Output: per-cell JSON rows + a summary to stdout.
"""
import json, os, re, subprocess, sys, tempfile, threading, time
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
MEMBER = ROOT / "corpus/live/round-66/pair_dec_act.wav"
OUT = Path(__file__).resolve().parent / "hold_ladder_results.jsonl"
ARM_TIMEOUT_S = 10
HOLDS = [0.0, 0.05, 0.2, 0.5, 1.0, 2.0]
FEEDS = ["oneshot", "chunked"]
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 10
DET = re.compile(r"detected file format type `(\S+?)'")
SMP = re.compile(r"Samples read:\s*(\d+)")
FAIL = re.compile(r"':\s*(.*)$")


def verdict(text, code, timed_out):
    det = DET.search(text)
    read = SMP.search(text)
    fails = [ln for ln in text.strip().splitlines() if "sox FAIL" in ln]
    err = None
    if timed_out:
        err = f"blocked: no verdict within {ARM_TIMEOUT_S} s"
    elif fails:
        m = FAIL.search(fails[-1])
        err = m.group(1) if m else fails[-1]
    return {"detected": det.group(1) if det else None,
            "route": "ffmpeg" if (det and det.group(1) == "act") or "(ffmpeg)" in text
                     else ("native" if det else "none"),
            "exit": code,
            "samples": int(read.group(1)) if read else None,
            "error": err}


def rep(feed, hold):
    data = MEMBER.read_bytes()
    with tempfile.TemporaryDirectory(prefix="r70simp-") as tmp:
        fifo = Path(tmp) / MEMBER.name
        os.mkfifo(fifo)

        def writer():
            try:
                with fifo.open("wb") as fh:
                    if feed == "oneshot":
                        fh.write(data)
                        fh.flush()
                    else:  # chunked: 64 B writes 25 ms apart
                        for i in range(0, len(data), 64):
                            fh.write(data[i:i + 64])
                            fh.flush()
                            time.sleep(0.025)
                    time.sleep(hold)
            except OSError:
                pass

        t = threading.Thread(target=writer, daemon=True)
        t0 = time.time()
        t.start()
        timed_out = False
        try:
            p = subprocess.run(["sox", "-V6", str(fifo), "-n", "stat"],
                               capture_output=True, timeout=ARM_TIMEOUT_S)
            text = p.stderr.decode(errors="replace")
            code = p.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            text = (exc.stderr or b"").decode(errors="replace")
            code = None
        el = time.time() - t0
        t.join(timeout=hold + 6)
        v = verdict(text, code, timed_out)
        v["elapsed_s"] = round(el, 3)
        return v


def main():
    rows = []
    for feed in FEEDS:
        for hold in HOLDS:
            for r in range(REPS):
                v = rep(feed, hold)
                v.update({"feed": feed, "hold_s": hold, "rep": r})
                rows.append(v)
                print(f"{feed:8s} h={hold:<4} rep={r} -> exit={v['exit']!s:>4} "
                      f"det={v['detected']} smp={v['samples']} "
                      f"err={v['error']} ({v['elapsed_s']}s)", flush=True)
    OUT.write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n")
    # summary: per-cell distinct signature counts
    from collections import Counter, defaultdict
    cells = defaultdict(Counter)
    for r in rows:
        sig = (r["exit"], r["detected"], r["samples"], r["error"])
        cells[(r["feed"], r["hold_s"])][sig] += 1
    print("\n=== per-cell signature distribution ===")
    for (feed, hold), c in sorted(cells.items()):
        for sig, n in c.most_common():
            print(f"{feed:8s} h={hold:<4} n={n:2d}/{REPS}  exit={sig[0]!s:>4} "
                  f"det={sig[1]} smp={sig[2]} err={sig[3]}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
