#!/usr/bin/env python3
"""r74 simplifier: deep-compare two measurement receipts.

Reports: byte sha256 of each file; per-key diffs of the JSON; optionally
excludes declared jitter keys (timing) and reports the stable projection.

Usage: python3 diff_receipts.py A.json B.json [jitter_key ...]
"""
import hashlib
import json
import sys
from pathlib import Path

JITTER_DEFAULT = ["wall_s", "waited_s", "live_s", "elapsed_s", "duration_s_wall"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def walk(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(walk(v, f"{prefix}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(walk(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def main():
    a, b = sys.argv[1], sys.argv[2]
    jitter = sys.argv[3:] or JITTER_DEFAULT
    ja, jb = json.load(open(a)), json.load(open(b))
    fa, fb = walk(ja), walk(jb)
    keys = sorted(set(fa) | set(fb))
    diffs = []
    jdiffs = []
    for k in keys:
        va, vb = fa.get(k, "<missing>"), fb.get(k, "<missing>")
        if va != vb:
            if any(("." + jk) in k for jk in jitter):
                jdiffs.append((k, va, vb))
            else:
                diffs.append((k, va, vb))
    print(f"A sha256: {sha(a)}")
    print(f"B sha256: {sha(b)}")
    print(f"keys: A={len(fa)} B={len(fb)} union={len(keys)}")
    print(f"STABLE diffs: {len(diffs)}")
    for k, va, vb in diffs[:40]:
        print(f"  DIFF {k}: {va!r} -> {vb!r}")
    print(f"JITTER diffs (declared, excluded): {len(jdiffs)}")
    for k, va, vb in jdiffs[:20]:
        print(f"  jitter {k}: {va!r} -> {vb!r}")
    if not diffs:
        print("VERDICT: stable projection IDENTICAL")
    else:
        print("VERDICT: stable projection DIFFERS")
    return 0 if not diffs else 1


if __name__ == "__main__":
    sys.exit(main())
