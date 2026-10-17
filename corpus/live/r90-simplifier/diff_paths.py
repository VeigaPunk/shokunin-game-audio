#!/usr/bin/env python3
"""Flatten both projections to path->value and print ONLY the changed leaves.

Usage: diff_paths.py <run_dir_A> <run_dir_B> [--entry <name>]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import compare_runs as C  # noqa: E402


def flat(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flat(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flat(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def main():
    a, b = sys.argv[1], sys.argv[2]
    only = None
    if len(sys.argv) > 3 and sys.argv[3] == "--entry":
        only = sys.argv[4]
    ea, eb = C.load(a), C.load(b)
    total = 0
    for name in sorted(set(ea) | set(eb)):
        if only and name != only:
            continue
        pa = flat(C.project_entry(ea.get(name, {})))
        pb = flat(C.project_entry(eb.get(name, {})))
        keys = sorted(set(pa) | set(pb))
        changed = [k for k in keys if pa.get(k) != pb.get(k)]
        fa = (ea.get(name) or {}).get("failures")
        fb = (eb.get(name) or {}).get("failures")
        print(f"\n== {name}  failures {fa} -> {fb}  "
              f"changed leaves: {len(changed)} / {len(keys)}")
        for k in changed:
            total += 1
            va = pa.get(k, "<absent>")
            vb = pb.get(k, "<absent>")
            print(f"   {k}\n      A: {json.dumps(va)[:180]}\n"
                  f"      B: {json.dumps(vb)[:180]}")
    print(f"\nTOTAL changed leaves: {total}")


if __name__ == "__main__":
    main()
