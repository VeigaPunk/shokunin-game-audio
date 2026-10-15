#!/usr/bin/env python3
"""Generate manifest.json for corpus/live/r83-boundary (untracked artifacts)."""
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    files = []
    for root, dirs, names in os.walk(HERE):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for n in sorted(names):
            p = os.path.join(root, n)
            rel = os.path.relpath(p, HERE)
            if rel == "manifest.json":
                continue
            st = os.stat(p)
            files.append({"path": rel, "bytes": st.st_size,
                          "sha256": sha256(p)})
    receipts = {}
    rdir = os.path.join(HERE, "receipts")
    if os.path.isdir(rdir):
        for n in sorted(os.listdir(rdir)):
            if n.endswith(".json"):
                p = os.path.join(rdir, n)
                receipts[n] = {"bytes": os.path.getsize(p),
                               "sha256": sha256(p)}
    man = {
        "seat": "audio r83 boundary (executor-class, leaf)",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "file_count": len(files),
        "total_bytes": sum(f["bytes"] for f in files),
        "receipts": receipts,
        "files": files,
    }
    out = os.path.join(HERE, "manifest.json")
    with open(out, "w") as fh:
        json.dump(man, fh, indent=1, sort_keys=True)
    print(f"manifest.json: {len(files)} files, "
          f"{man['total_bytes']} bytes, {len(receipts)} receipts")


if __name__ == "__main__":
    main()
