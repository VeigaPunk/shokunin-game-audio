#!/usr/bin/env python3
"""r97b manifest builder — sha256 of every seat artifact (receipts, probes,
conf, runs, scratch), excluding runtime sockets/locks and __pycache__.
Writes corpus/live/r97-boundary/manifest.sha256.
"""
import hashlib, os, sys

SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"__pycache__", "run", "run2", "run3", "run-sibling"}
SKIP_EXT = {".lock"}
SKIP_NAMES = {".nfs", "manifest.sha256"}  # the manifest cannot pin itself


def main():
    rows = []
    for root, dirs, files in os.walk(SEAT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f in SKIP_NAMES or os.path.splitext(f)[1] in SKIP_EXT:
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, SEAT)
            try:
                b = open(p, "rb").read()
            except Exception:
                continue
            rows.append((hashlib.sha256(b).hexdigest(), len(b), rel))
    rows.sort(key=lambda r: r[2])
    out = os.path.join(SEAT, "manifest.sha256")
    with open(out, "w") as fh:
        for h, n, rel in rows:
            fh.write(f"{h}  {n:>9}  {rel}\n")
    print(f"wrote {out}: {len(rows)} files, "
          f"{sum(n for _, n, _ in rows)} bytes")
    for h, n, rel in rows:
        if rel.startswith("receipts/"):
            print(f"  {h[:16]}  {rel}")


if __name__ == "__main__":
    main()
