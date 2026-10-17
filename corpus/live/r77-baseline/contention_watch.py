#!/usr/bin/env python3
"""r77-baseline contention watch (bounded): samples host/audio-stack state every
SAMPLE_S seconds for WINDOW_S seconds and appends one line per sample, so the
replay's drift rows can be attributed to (or cleared of) concurrent-seat
contention on the shared PipeWire/ALSA stack.

Columns: utc, load1, default_sink, n_audio_procs, audio-proc summary (name+pid).
Writes contention-watch.txt.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "contention-watch.txt"
WINDOW_S = 1500
SAMPLE_S = 30
PAT = "measure_audio|pw-cat|pw-record|parec|parecord|arecord|aplay|ffmpeg|sox|mpv"


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True,
                          text=True).stdout.strip()


def sample():
    utc = time.strftime("%H:%M:%SZ", time.gmtime())
    load = sh("cut -d' ' -f1-3 /proc/loadavg")
    sink = sh("pactl get-default-sink 2>/dev/null") or "-"
    procs = [l for l in sh(f"ps -eo pid=,args= | grep -E '{PAT}' | grep -v grep").splitlines()]
    names = sorted({l.split(None, 1)[1].split()[0].split('/')[-1] for l in procs if l.split(None, 1)[1:]})
    return f"{utc}\tload={load}\tsink={sink}\tn_audio={len(procs)}\t{','.join(names) or '-'}"


def main():
    t0 = time.time()
    with OUT.open("a") as fh:
        fh.write(f"=== contention watch start {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
                 f"window={WINDOW_S}s sample={SAMPLE_S}s ===\n")
        fh.flush()
        while time.time() - t0 < WINDOW_S:
            line = sample()
            fh.write(line + "\n")
            fh.flush()
            print(line, file=sys.stderr)
            time.sleep(SAMPLE_S)
        fh.write(f"=== contention watch end {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} ===\n")


if __name__ == "__main__":
    main()
