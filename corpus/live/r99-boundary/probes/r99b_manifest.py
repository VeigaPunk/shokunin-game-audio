#!/usr/bin/env python3
"""r99-boundary manifest: sha256 of every seat artifact except run/ and itself."""
import hashlib, os

SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"run", "__pycache__"}
SKIP_FILES = {"manifest.sha256"}


def main():
    rows = []
    for root, dirs, files in os.walk(SEAT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f in SKIP_FILES:
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, SEAT)
            h = hashlib.sha256()
            try:
                with open(p, "rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(chunk)
            except OSError:
                continue
            rows.append((h.hexdigest(), rel))
    rows.sort(key=lambda r: r[1])
    with open(os.path.join(SEAT, "manifest.sha256"), "w") as fh:
        for h, rel in rows:
            fh.write("%s  %s\n" % (h, rel))
    total = sum(os.path.getsize(os.path.join(SEAT, r)) for _, r in rows)
    print("manifest: %d files, %.1f MB" % (len(rows), total / 1e6))


if __name__ == "__main__":
    main()
