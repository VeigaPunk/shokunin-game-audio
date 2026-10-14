#!/usr/bin/env python3
"""r67 boundary — fifo write-timing probes.

Writer opens fifo, writes chunk1, sleeps `gap` seconds, writes rest,
optionally closes. Reader: `sox -V4 fifo -n stat` with timeout.

The AUTO_DETECT_SIZE window is 257 bytes; a first read() on a fifo
returns whatever is buffered — so detection itself is racy when the
writer splits inside the predicate window.
"""
import os, re, subprocess, sys, threading, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROBES = ROOT / "probes"
LOGS = ROOT / "runs" / "logs" / "race"
SOX = "/usr/bin/sox"
DET = re.compile(r"detected file format type `([^']+)'")
SMP = re.compile(r"Samples read:\s+(\d+)")


def split_writer(fifo, data, cut, gap, hold_after=0.0, close=True):
    w = os.open(fifo, os.O_WRONLY)
    os.write(w, data[:cut])
    time.sleep(gap)
    if cut < len(data):
        os.write(w, data[cut:])
    if hold_after:
        time.sleep(hold_after)
    if close:
        os.close(w)


def probe(fn, cut, gap, hold=0.0, timeout=8):
    path = PROBES / fn
    data = path.read_bytes()
    fifo = PROBES / ".race_fifo"
    try:
        os.unlink(fifo)
    except FileNotFoundError:
        pass
    os.mkfifo(fifo)
    t = threading.Thread(target=split_writer, args=(str(fifo), data, cut, gap, hold),
                         daemon=True)
    t.start()
    t0 = time.time()
    try:
        p = subprocess.run([SOX, "-V4", str(fifo), "-n", "stat"],
                           capture_output=True, timeout=timeout)
        el = time.time() - t0
        out = (p.stderr or b"").decode(errors="replace") + (p.stdout or b"").decode(errors="replace")
        det = DET.search(out); smp = SMP.search(out)
        msg = ""
        for line in out.splitlines():
            if "sox FAIL" in line or "sox WARN" in line:
                msg = line.strip(); break
        res = (p.returncode, det.group(1) if det else "", smp.group(1) if smp else "", f"{el:.2f}s", msg[:100])
    except subprocess.TimeoutExpired:
        el = time.time() - t0
        res = ("TIMEOUT", "?", "", f"{el:.2f}s", f"still running at {timeout}s kill")
    t.join(timeout=3)
    os.unlink(fifo)
    return res


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    cases = [
        # act conjunct needs byte 256 within first read
        ("pair_dec_act.wav",       [128, 200, 255, 256, 257, 300, 600]),
        ("pair_preempt_act.wav",   [256, 257]),
        # hcom needs FSSD@65 + HCOM@128-131 -> first read >=132
        ("pair_dec_hcom.wav",      [64, 128, 131, 132, 257, 600]),
        ("pair_lengate_hcom_132.wav", [64, 131, 132]),
        # gsrt needs ring.bin\0@16-24 -> first read >=25
        ("pair_preempt_gsrt.wav",  [16, 24, 25, 100, 257]),
        ("pair_lengate_gsrt_25.wav", [24, 25]),
        # transport-invariant controls
        ("z_hcom_dec.bin",         [64, 132]),
        ("g_txw_hcom.bin",         [132]),
    ]
    rows = []
    for fn, cuts in cases:
        for cut in cuts:
            for gap in (0.8,):
                r = probe(fn, cut, gap)
                tag = f"{fn}:cut{cut}:gap{gap}"
                print(f"{tag}\t{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}", flush=True)
                rows.append((tag,) + tuple(str(x) for x in r))
    # starvation: full predicate window, then long mid-body stall, then rest
    print("--- starvation legs (cut=257, gap=2.0s, hold) ---")
    for fn in ["pair_dec_act.wav", "pair_preempt_gsrt.wav", "z_hcom_dec.bin",
               "pair_lengate_gsrt_25.wav", "g_amrnb_hcom.bin"]:
        for hold in (0.0,):
            r = probe(fn, 257, 2.0, hold=hold, timeout=15)
            tag = f"{fn}:starve257:g2.0:h{hold}"
            print(f"{tag}\t{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}", flush=True)
            rows.append((tag,) + tuple(str(x) for x in r))
    # dribble: 64-byte writes with 60ms gaps over the whole file
    print("--- dribble legs (64B x 60ms) ---")
    for fn in ["pair_dec_act.wav", "pair_preempt_gsrt.wav", "g_amrnb_hcom.bin", "z_hcom_dec.bin"]:
        data = (PROBES / fn).read_bytes()
        fifo = PROBES / ".race_fifo"
        try: os.unlink(fifo)
        except FileNotFoundError: pass
        os.mkfifo(fifo)
        def dribble():
            w = os.open(fifo, os.O_WRONLY)
            for i in range(0, len(data), 64):
                os.write(w, data[i:i+64]); time.sleep(0.06)
            os.close(w)
        t = threading.Thread(target=dribble, daemon=True); t.start()
        t0 = time.time()
        try:
            p = subprocess.run([SOX, "-V4", str(fifo), "-n", "stat"],
                               capture_output=True, timeout=30)
            el = time.time() - t0
            out = (p.stderr or b"").decode(errors="replace") + (p.stdout or b"").decode(errors="replace")
            det = DET.search(out); smp = SMP.search(out)
            msg = ""
            for line in out.splitlines():
                if "sox FAIL" in line or "sox WARN" in line:
                    msg = line.strip(); break
            r = (p.returncode, det.group(1) if det else "", smp.group(1) if smp else "", f"{el:.2f}s", msg[:100])
        except subprocess.TimeoutExpired:
            r = ("TIMEOUT", "?", "", "30s", "dribble kill")
        t.join(timeout=3); os.unlink(fifo)
        tag = f"{fn}:dribble64x60ms"
        print(f"{tag}\t{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}", flush=True)
        rows.append((tag,) + tuple(str(x) for x in r))
    with open(ROOT / "runs" / "race.tsv", "a") as f:
        for row in rows:
            f.write("\t".join(row) + "\n")


if __name__ == "__main__":
    main()
