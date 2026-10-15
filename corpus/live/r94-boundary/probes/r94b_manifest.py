#!/usr/bin/env python3
"""r94b manifest — sha256 of every file this seat wrote (excluding __pycache__).

Usage: python3 probes/r94b_manifest.py [--check]
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SEAT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"__pycache__"}
SKIP_NAMES = {"manifest.sha256"}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk():
    out = []
    for p in sorted(SEAT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(SEAT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if rel.name in SKIP_NAMES:
            continue
        out.append((str(rel), sha256(p)))
    return out


def main():
    entries = walk()
    lines = [f"{h}  {rel}" for rel, h in entries]
    text = "\n".join(lines) + "\n"
    (SEAT / "manifest.sha256").write_text(text)
    total_bytes = sum((SEAT / rel).stat().st_size for rel, _ in entries)
    print(f"{len(entries)} files, {total_bytes / 1e6:.1f} MB, "
          f"manifest sha256 {hashlib.sha256(text.encode()).hexdigest()}")


if __name__ == "__main__":
    main()
