#!/usr/bin/env python3
"""r73-scout: independent pw-cat playback matrix (file/fifo arms).

pw-cat needs a live PipeWire daemon (PIPEWIRE_RUNTIME_DIR / XDG_RUNTIME_DIR).
Decode layer is libsndfile (content sniff, no name axis); consumption is
playback-paced. Writer protocol: one-shot write + close (no linger needed).
"""
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = ROOT / "corpus" / "live" / "r73-scout"
LOGS = OUT / "logs" / "pwcat"
RUNS = OUT / "runs"
FIFOS = OUT / "fifos"
for d in (LOGS, RUNS, FIFOS):
    d.mkdir(parents=True, exist_ok=True)

ARM_TIMEOUT_S = 15
RUNTIME = "/run/user/1000"

MEMBERS = {
    "posttable_nomatch": ROOT / "corpus/live/round-68/posttable_nomatch.wav",
    "txw_piperefuse": ROOT / "corpus/live/round-68/txw_piperefuse.wav",
    "dec_act": ROOT / "corpus/live/round-66/pair_dec_act.wav",
    "dec_hcom": ROOT / "corpus/live/round-66/pair_dec_hcom.wav",
    "extsuffix_wav": ROOT / "corpus/live/round-69/extsuffix_nomatch.wav",
    "extsuffix_bin": ROOT / "corpus/live/round-69/extsuffix_nomatch.bin",
    "extsuffix_txw": ROOT / "corpus/live/round-69/extsuffix_nomatch.txw",
    "extsuffix_f32": ROOT / "corpus/live/round-69/extsuffix_nomatch.f32",
    "extsuffix_snd": ROOT / "corpus/live/round-69/extsuffix_nomatch.snd",
    "lengate_gsrt_25": ROOT / "corpus/live/round-66/pair_lengate_gsrt_25.wav",
    "tone4s": OUT / "tone4s.wav",
}


def unblock_writer(fifo):
    try:
        fd = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
        os.close(fd)
    except OSError:
        pass


def writer_thread(fifo, data, linger_s=0.0):
    try:
        with open(fifo, "wb", buffering=0) as fh:
            fh.write(data)
            if linger_s:
                time.sleep(linger_s)
    except OSError:
        pass


def run_leg(member, arm, extra=None, env=None, writer_linger=0.0):
    path = MEMBERS[member]
    data = path.read_bytes()
    tag = arm if not extra else f"{arm}-{extra}"
    log = LOGS / f"{member}__{tag}.log"
    argv = ["timeout", "-s", "KILL", str(ARM_TIMEOUT_S), "pw-cat", "-p"]
    if extra:
        argv += extra
    fifo = None
    wthr = None
    if arm == "file":
        argv.append(str(path))
    elif arm == "fifo_path":
        fifo = FIFOS / f"{member}__{tag}.fifo"
        if fifo.exists():
            fifo.unlink()
        os.mkfifo(fifo)
        wthr = threading.Thread(target=writer_thread,
                                args=(fifo, data, writer_linger), daemon=True)
        wthr.start()
        argv.append(str(fifo))
    else:
        raise ValueError(arm)
    e = dict(os.environ)
    e["XDG_RUNTIME_DIR"] = RUNTIME
    if env:
        e.update(env)
    t0 = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=ARM_TIMEOUT_S + 5,
                              env=e)
        rc = proc.returncode
        err = proc.stderr.decode(errors="replace")
        blocked = None
    except subprocess.TimeoutExpired:
        rc, err, blocked = None, "", "blocked: no verdict within timeout"
    wall = time.monotonic() - t0
    if wthr is not None:
        wthr.join(timeout=1.0)
        if wthr.is_alive():
            unblock_writer(fifo)
            wthr.join(timeout=1.0)
        try:
            fifo.unlink()
        except OSError:
            pass
    log.write_text(err)
    return {
        "member": member, "arm": arm, "tag": tag, "rc": rc,
        "wall_s": round(wall, 3), "blocked": blocked,
        "stderr": err.strip(),
        "log": str(log.relative_to(ROOT)),
    }


def main():
    run_tag = sys.argv[1] if len(sys.argv) > 1 else "run1"
    cells = []
    for member in MEMBERS:
        for arm in ("file", "fifo_path"):
            v = run_leg(member, arm)
            cells.append(v)
            print(f"{member:20s} {arm:9s} rc={v['rc']} wall={v['wall_s']:>6.3f} "
                  f"err={v['stderr'][:60]!r}")
    doc = {
        "probe": "pw-cat playback matrix (r73-scout independent)",
        "tool": "pw-cat / libpipewire 1.6.8; daemon pipewire pid 1905 live",
        "runtime_dir": RUNTIME,
        "arm_timeout_s": ARM_TIMEOUT_S,
        "writer_protocol": "one-shot write + immediate close (no linger)",
        "cells": cells,
    }
    out = RUNS / f"pwcat-matrix-{run_tag}.json"
    out.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
