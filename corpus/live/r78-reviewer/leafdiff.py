#!/usr/bin/env python3
"""r78 REVIEWER — leaf-level diff of two receipts with declared-class buckets.

Usage: leafdiff.py <fresh.json> <reference.json> <out.txt> [--label fresh/ref]

Walks both measurement trees to leaf paths and reports only-in-fresh,
only-in-ref, and differing leaves, bucketed by a declared-class predicate:
  env      — source/sink inventory + target-name substitution (topology)
  contention — hw-device busy/free, witness, aplay tails, ffmpeg_alsa
  wall     — declared wall-clock/rate keys
  scrubbed — stderr_tail / argv path scrub windows
  undeclared — everything else (the finding surface)
"""
import json
import sys
from pathlib import Path


def leaves(obj, prefix=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, prefix + (str(k),))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, prefix + (f"[{i}]",))
    else:
        yield prefix, obj


def key_of(path):
    return "/".join(path)


def bucket(path, a, b):
    k = key_of(path)
    if any(s in k for s in ("inventory", "default_source", "default_sink",
                            "sources", "sinks", "monitors", "capture_ports",
                            "playback_devices", "card", "card_id", "card_name",
                            "device_census", "device_axis", "name_axis",
                            "gate.", "sever.", "bounded.", "argv", "target",
                            "legs.default", "legs.pipewire")):
        return "env"
    if any(s in k for s in ("busy", "free", "witness", "alsa", "hw_first",
                            "plughw", "sysdefault", "aplay", "arecord",
                            "ffmpeg_alsa", "contention", "pcm")):
        return "contention"
    if any(s in k for s in ("wall", "rate", "pacing", "duration_bucket",
                            "frames", "bytes", "peak", "sha", "nonzero_frac",
                            "drift", "stderr_tail", "undershoot")):
        return "wall"
    return "undeclared"


def main():
    fresh = json.load(open(sys.argv[1]))
    ref = json.load(open(sys.argv[2]))
    out = Path(sys.argv[3])
    label = sys.argv[4] if len(sys.argv) > 4 else "fresh/ref"
    fm = fresh.get("measurements", fresh)
    rm = ref.get("measurements", ref)
    lines = []
    counts = {}
    for entry in sorted(set(fm) | set(rm)):
        a = fm.get(entry)
        b = rm.get(entry)
        if a is None or b is None:
            lines.append(f"ENTRY-ONLY {entry} ({label})")
            counts["entry"] = counts.get("entry", 0) + 1
            continue
        la = dict(leaves(a))
        lb = dict(leaves(b))
        for path in sorted(set(la) | set(lb)):
            va, vb = la.get(path, "<missing>"), lb.get(path, "<missing>")
            if va == vb:
                continue
            if isinstance(va, float) and isinstance(vb, float) and \
                    abs(va - vb) < 1e-9:
                continue
            bk = bucket(path, va, vb)
            counts[bk] = counts.get(bk, 0) + 1
            lines.append(f"{bk:11s} {entry}:{key_of(path)}  "
                         f"fresh={va!r} ref={vb!r}")
    out.write_text("\n".join(lines) + "\n")
    print(f"{sys.argv[1]} vs {sys.argv[2]}: {len(lines)} differing leaves")
    for k in sorted(counts):
        print(f"  {k:11s} {counts[k]}")


if __name__ == "__main__":
    main()
