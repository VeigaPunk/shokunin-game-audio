#!/usr/bin/env python3
"""r74 reviewer — independent pw-cat ops-2 probes (ARM B), pre-landing.

Cells (all bounded; fifo-open blocks are SIGTERM-immune -> KILL bound):
  1. writerless fifo + TERM-only bound      -> expect hang (outer KILL rc137)
  2. writerless fifo + KILL bound           -> rc -9 / 137
  3. --target 0 on a file + TERM bound 4 s  -> rc124 (TERM-terminable)
  4. raw (-a) vs normal on identical .snd bytes through fifos named
     axis.wav / axis.bin                     -> name axis dies under -a
"""
import json
import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SND = ROOT / "corpus/live/round-70"  # placeholder, resolved below
HOLD = 1.0


def find_snd_member():
    for p in sorted((ROOT / "corpus/live").rglob("*.snd")):
        if p.name.startswith("extsuffix") or "nomatch" in p.name:
            return p
    return None


def feed(fifo, data, hold):
    try:
        with open(fifo, "wb") as fh:
            fh.write(data)
            fh.flush()
            time.sleep(hold)
    except OSError:
        pass


def run(argv, timeout_s, kill=False, **kw):
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True,
                           timeout=timeout_s, **kw)
        return {"rc": p.returncode, "wall_s": round(time.monotonic() - t0, 3),
                "stderr_tail": p.stderr.decode(errors="replace").strip().splitlines()[-1:] or None}
    except subprocess.TimeoutExpired:
        return {"rc": None, "wall_s": round(time.monotonic() - t0, 3),
                "blocked": True}


def main():
    out = {}
    snd = find_snd_member()
    out["snd_member"] = str(snd.relative_to(ROOT)) if snd else None
    data = snd.read_bytes() if snd else b"\x00" * 4096

    # 1/2: writerless fifo
    with tempfile.TemporaryDirectory(prefix="rv-ops2-") as tmp:
        fifo = Path(tmp) / "nowriter.wav"
        os.mkfifo(fifo)
        # outer KILL 10 s bounds a TERM-immune child; inner TERM at 3 s
        out["writerless_term_then_kill"] = run(
            ["timeout", "-s", "KILL", "10", "timeout", "-s", "TERM", "3",
             "pw-cat", "-p", str(fifo)], 15)
        out["writerless_kill"] = run(
            ["timeout", "-s", "KILL", "6", "pw-cat", "-p", str(fifo)], 10)

    # 3: --target 0 on a decodable file, TERM bound
    dec = None
    for p in sorted((ROOT / "corpus/live").rglob("*.wav")):
        if "dec" in p.name or "hcom" in p.name:
            dec = p
            break
    if dec is None:
        for p in sorted((ROOT / "corpus/live").rglob("*.wav")):
            dec = p
            break
    out["target0_member"] = str(dec.relative_to(ROOT))
    out["target0_term4"] = run(
        ["timeout", "-s", "TERM", "4", "pw-cat", "-p", "--target", "0",
         str(dec)], 8)

    # 4: raw vs normal on identical bytes through differently-named fifos
    legs = {}
    for fname in ("axis.wav", "axis.bin", "axis.snd"):
        for mode, extra in (("normal", []), ("raw", ["-a"])):
            with tempfile.TemporaryDirectory(prefix="rv-ops2-") as tmp:
                fifo = Path(tmp) / fname
                os.mkfifo(fifo)
                w = threading.Thread(target=feed, args=(fifo, data, HOLD),
                                     daemon=True)
                w.start()
                try:
                    r = run(["pw-cat", "-p", *extra, str(fifo)], 15)
                finally:
                    w.join(timeout=HOLD + 5)
                legs[f"{mode}:{fname}"] = r
    out["name_axis_raw"] = legs
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
