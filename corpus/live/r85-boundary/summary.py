#!/usr/bin/env python3
"""r85 boundary — receipt summarizer (read-only). Usage: summary.py <receipt.json> [section]"""
import json, sys
from pathlib import Path

p = Path(sys.argv[1])
R = json.loads(p.read_text())
sec = sys.argv[2] if len(sys.argv) > 2 else None


def show(k, v, depth=0):
    pad = "  " * depth
    if isinstance(v, dict):
        print(f"{pad}{k}:")
        for kk, vv in v.items():
            show(kk, vv, depth + 1)
    elif isinstance(v, list):
        print(f"{pad}{k}: [{len(v)} items]")
        for i, vv in enumerate(v[:6]):
            if isinstance(vv, dict):
                keep = {kk: vv[kk] for kk in list(vv)[:14]}
                print(f"{pad}  [{i}] {json.dumps(keep, default=str)[:600]}")
            else:
                print(f"{pad}  [{i}] {str(vv)[:300]}")
        if len(v) > 6:
            print(f"{pad}  ... +{len(v)-6} more")
    else:
        print(f"{pad}{k}: {str(v)[:400]}")


keys = [sec] if sec else list(R)
for k in keys:
    if k in R:
        show(k, R[k])
