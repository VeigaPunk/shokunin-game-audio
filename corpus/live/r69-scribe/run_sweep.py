#!/usr/bin/env python3
"""r69 SCRIBE independent extension-suffix sweep.

Re-runs the declared r69 extension sweep on my OWN members using the landed
r67/r68 arm machinery imported verbatim from the tracked
corpus/fixtures/measure_audio.py (no copy, no edit).

Members: one no-match byte body replicated under different names
  .wav .bin .txw .f32 .snd (+ .au .mp3 and extension-less controls).
Two bodies:
  bodyA = 300 B all zeros  (arms the ext-gated sndr row under .snd)
  bodyB = 512 B, first 8 bytes zero, deterministic nonzero tail
Every arm's sox_detected_format is recorded so the .snd detection fork and
any accidental CHECK match are both visible.

Output: runs/sweep-<body>.json (transport_entry-shaped receipts + verbatim
stderr tails), runs/logs/*.stderr raw legs.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SCRATCH = REPO / "corpus" / "live" / "r69-scribe"
PROBES = SCRATCH / "probes"
RUNS = SCRATCH / "runs"
LOGS = RUNS / "logs"
MEASURE = REPO / "corpus" / "fixtures" / "measure_audio.py"

spec = importlib.util.spec_from_file_location("measure_audio", MEASURE)
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

NAMES = ["wav", "bin", "txw", "f32", "snd", "au", "mp3", "noext"]


def build_body_a():
    # 300 B all-zero: satisfies NO unconditional CHECK row; bytes 0,1,7 are
    # 0x00 so the ext-gated sndr row arms only when the name ends .snd.
    return bytes(300)


def build_body_b():
    # 512 B: bytes 0-7 zero (sndr arming + kills every offset-0 magic), then a
    # deterministic nonzero tail (i*7+3 pattern family, same as r68 members).
    b = bytearray(512)
    for i in range(8, 512):
        b[i] = (i * 7 + 3) & 0xFF
    return bytes(b)


def write_members():
    for tag, body in (("a", build_body_a()), ("b", build_body_b())):
        for name in NAMES:
            fn = f"nomatch_{tag}.{name}" if name != "noext" else f"nomatch_{tag}_noext"
            (PROBES / fn).write_bytes(body)


def sha(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sweep(body_tag):
    results = {}
    for name in NAMES:
        fn = f"nomatch_{body_tag}.{name}" if name != "noext" else f"nomatch_{body_tag}_noext"
        path = PROBES / fn
        arms = ma.transport_matrix(path)
        for t, leg in arms.items():
            (LOGS / f"{fn}.{t}.stderr").write_text(
                json.dumps(leg, indent=2, allow_nan=False) + "\n")
        groups = []
        for t in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
            a = arms[t]
            sig = (a["sox_detected_format"], a["sox_route"], a["exit_code"],
                   a["samples_read"], a["error"])
            for g in groups:
                if g[0] == sig:
                    g[1].append(t)
                    break
            else:
                groups.append((sig, [t]))
        results[fn] = {
            "sha256": sha(path),
            "bytes": path.stat().st_size,
            "arms": arms,
            "verdict_groups": [
                {"transports": ts, "detected": s[0], "route": s[1],
                 "exit": s[2], "samples": s[3], "error": s[4]}
                for s, ts in groups],
            "n_groups": len(groups),
            "detection_values": {t: arms[t]["sox_detected_format"]
                                 for t in ("file", "stdin_pipe",
                                           "redirected_fd", "fifo_path")},
            "detection_fork": len({arms[t]["sox_detected_format"]
                                   for t in ("file", "stdin_pipe",
                                             "redirected_fd", "fifo_path")}) > 1,
        }
    return results


def main():
    PROBES.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    write_members()
    out = {}
    for tag in ("a", "b"):
        res = sweep(tag)
        out[f"body_{tag}"] = res
        (RUNS / f"sweep-body-{tag}.json").write_text(
            json.dumps(res, indent=2, allow_nan=False) + "\n")
    # summary table to stdout
    for tag in ("a", "b"):
        print(f"== body_{tag} ==")
        for fn, r in out[f"body_{tag}"].items():
            dets = r["detection_values"]
            print(f"{fn:22s} groups={r['n_groups']} detfork={r['detection_fork']} "
                  f"det={dets['file']}/{dets['fifo_path']}/{dets['stdin_pipe']}/{dets['redirected_fd']}")
            for g in r["verdict_groups"]:
                print(f"    {'/'.join(g['transports']):32s} det={g['detected']} "
                      f"exit={g['exit']} n={g['samples']} err={g['error']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
