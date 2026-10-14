#!/usr/bin/env python3
"""r69 boundary: extension sweep x fifo-starved delivery.

For each fifo name extension, the writer pushes N bytes of the member then
closes IMMEDIATELY (no linger) -> the reader's prefetch sees len=N at open.
Measures the len-gated verdict transitions on the post-table + ext-gated
paths, incl. the sndr CHECK len<8 uninitialized-byte window and the .txw
reader's !seekable refusal at every N.

Stall cells: writer writes K bytes then HOLDS the fifo open without writing
more for `stall_s`; measures whether sox's prefetch blocks until more data
or EOF (verdict lands only after the hold ends / on timeout).
"""
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBES = HERE / "probes"
RUNS = HERE / "runs"
LOGS = RUNS / "logs"
TIMEOUT_S = 10

EXTS = ["wav", "txw", "f32", "snd", "au", "bin"]
# N bytes written by the starved writer (immediate close)
NS = [0, 1, 2, 3, 7, 8, 16, 64, 128, 257, 429, 512]
SND_REPS = 8  # reps for the len<8 uninit-byte cell


def norm_error(text):
    fails = [l for l in text.strip().splitlines() if "sox FAIL" in l]
    if not fails:
        return None
    m = re.search(r"':\s*(.*)$", fails[-1])
    return m.group(1) if m else fails[-1]


def fifo_leg(name, data, hold_after_close_s=0.0, stall_write=None,
             stall_hold_s=0.0, timeout_s=TIMEOUT_S, log=None):
    """One fifo leg: writer writes `data` (or stall_write first, holds,
    then writes rest) then closes after hold_after_close_s linger."""
    text = ""
    with tempfile.TemporaryDirectory(prefix="r69-starve-") as tmp:
        fifo = Path(tmp) / name
        os.mkfifo(fifo)

        def feed():
            try:
                with fifo.open("wb") as fh:
                    if stall_write is not None:
                        fh.write(stall_write)
                        fh.flush()
                        time.sleep(stall_hold_s)
                    fh.write(data)
                    fh.flush()
                    if hold_after_close_s:
                        time.sleep(hold_after_close_s)
            except OSError:
                pass

        t = threading.Thread(target=feed, daemon=True)
        t0 = time.time()
        t.start()
        try:
            p = subprocess.run(["sox", "-V6", str(fifo), "-n", "stat"],
                               capture_output=True, timeout=timeout_s)
            text = p.stderr.decode(errors="replace")
            code = p.returncode
            err = norm_error(text)
        except subprocess.TimeoutExpired as e:
            text = (e.stderr or b"").decode(errors="replace")
            code = None
            err = f"blocked: no verdict within {timeout_s} s"
        elapsed = time.time() - t0
        t.join(timeout=5)
    if log is not None:
        log.write_text(text)
    det = re.search(r"detected file format type `(\S+?)'", text)
    read = re.search(r"Samples read:\s*(\d+)", text)
    return {"detected": det.group(1) if det else None,
            "exit": code, "samples": int(read.group(1)) if read else None,
            "error": err, "elapsed_s": round(elapsed, 2)}


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    nm_ascii = (PROBES / "nm_ascii").read_bytes()
    nm_z2 = (PROBES / "nm_z2").read_bytes()
    rows = []
    for ext in EXTS:
        data = nm_z2 if ext in ("snd", "au") else nm_ascii
        for n in NS:
            reps = SND_REPS if (ext == "snd" and n < 8) else 1
            for rep in range(reps):
                r = fifo_leg(f"st.{ext}", data[:n],
                             log=LOGS / f"starve_{ext}_n{n}_r{rep}.log")
                rows.append({"ext": ext, "n": n, "rep": rep, **r})
                print(f"{ext:4s} n={n:3d} rep={rep} det={r['detected']!s:6} "
                      f"exit={r['exit']!s:4} samp={r['samples']!s:6} "
                      f"t={r['elapsed_s']:5.2f} err={r['error']}")
    # uppercase .SND starve cells: case-insensitive gate + uninit window
    for n in (2, 8):
        r = fifo_leg("st.SND", nm_z2[:n], log=LOGS / f"starve_SND_n{n}.log")
        rows.append({"ext": "SND", "n": n, "rep": 0, **r})
        print(f"SND  n={n:3d} rep=0 det={r['detected']!s:6} "
              f"exit={r['exit']!s:4} samp={r['samples']!s:6} "
              f"t={r['elapsed_s']:5.2f} err={r['error']}")
    # stall cells: writer delivers `stall_write` bytes then holds the fifo
    # open `hold` seconds without EOF, then dumps the rest + closes.
    print("--- stall cells (writer holds open, no EOF) ---")
    for ext, stall_n, hold in [("wav", 4, 1.0), ("wav", 257, 1.0),
                               ("f32", 4, 1.0), ("snd", 2, 1.0),
                               ("snd", 2, 3.0), ("txw", 6, 1.0),
                               ("bin", 0, 1.0), ("bin", 0, 3.0)]:
        data = nm_z2 if ext in ("snd", "au") else nm_ascii
        sw, rest = data[:stall_n], data[stall_n:]
        r = fifo_leg(f"stall.{ext}", rest, stall_write=sw, stall_hold_s=hold,
                     timeout_s=TIMEOUT_S,
                     log=LOGS / f"stall_{ext}_k{stall_n}_h{hold}.log")
        rows.append({"ext": ext, "n": f"stall{stall_n}+h{hold}", "rep": 0, **r})
        print(f"{ext:4s} stall k={stall_n} hold={hold}s -> det={r['detected']!s:6} "
              f"exit={r['exit']!s:4} t={r['elapsed_s']:5.2f} err={r['error']}")
    # never-close cell: writer writes 0 bytes and outlives the probe timeout
    print("--- never-close cell (writer outlives timeout) ---")
    with tempfile.TemporaryDirectory(prefix="r69-nc-") as tmp:
        fifo = Path(tmp) / "nc.bin"
        os.mkfifo(fifo)
        stop = threading.Event()

        def feed_hold():
            try:
                fh = fifo.open("wb")
                stop.wait(TIMEOUT_S + 8)
                fh.close()
            except OSError:
                pass

        t = threading.Thread(target=feed_hold, daemon=True)
        t0 = time.time()
        t.start()
        try:
            p = subprocess.run(["sox", "-V6", str(fifo), "-n", "stat"],
                               capture_output=True, timeout=TIMEOUT_S)
            text = p.stderr.decode(errors="replace")
            code, err = p.returncode, norm_error(text)
        except subprocess.TimeoutExpired as e:
            text = (e.stderr or b"").decode(errors="replace")
            code, err = None, f"blocked: no verdict within {TIMEOUT_S} s"
        print(f"bin never-close -> exit={code!s:4} t={time.time()-t0:5.2f} err={err}")
        (LOGS / "neverclose_bin.log").write_text(text)
        rows.append({"ext": "bin", "n": "neverclose", "rep": 0,
                     "detected": None, "exit": code, "samples": None,
                     "error": err, "elapsed_s": round(time.time() - t0, 2)})
        stop.set()
        t.join(timeout=TIMEOUT_S + 12)
    out = RUNS / "fifo_starve.tsv"
    with out.open("w") as fh:
        fh.write("ext\tn\trep\tdetected\texit\tsamples\telapsed_s\terror\n")
        for r in rows:
            fh.write("\t".join(str(r[k]) for k in
                               ("ext", "n", "rep", "detected", "exit",
                                "samples", "elapsed_s", "error")) + "\n")
    print(f"\n{len(rows)} legs -> {out}")


if __name__ == "__main__":
    sys.exit(main())
