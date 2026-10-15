#!/usr/bin/env python3
"""r100b manifest — sha256 of every file under corpus/live/r100-boundary/.

Usage: mkmanifest.py [--check]
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "MANIFEST.sha256")
SKIP = {"MANIFEST.sha256", "__pycache__"}


def walk():
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in sorted(files):
            if f in SKIP or f.endswith(".pyc"):
                continue
            p = os.path.join(root, f)
            yield p


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    check = "--check" in sys.argv
    lines = []
    for p in sorted(walk()):
        lines.append("%s  %s" % (sha(p), os.path.relpath(p, HERE)))
    body = "\n".join(lines) + "\n"
    if check:
        old = open(OUT).read() if os.path.exists(OUT) else ""
        print("MATCH" if old == body else "MISMATCH (%d files now)" % len(lines))
        return 0 if old == body else 1
    with open(OUT, "w") as f:
        f.write(body)
    total = sum(os.path.getsize(p) for p in walk())
    print("wrote %s: %d files, %.2f MB" % (OUT, len(lines), total / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
