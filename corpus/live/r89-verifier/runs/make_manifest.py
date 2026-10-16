#!/usr/bin/env python3
"""Build manifest.json + manifest.sha256 for the r89 verifier seat dir.

Covers every regular file under corpus/live/r89-verifier/ except the
regenerable snapshot trees (tree/, runs/cotree*/) — same convention as
the r88 verifier manifest.
"""
import hashlib
import json
from pathlib import Path

SEAT = Path(__file__).resolve().parent.parent  # corpus/live/r89-verifier
SKIP_DIRS = {"tree", "cotree1", "cotree2", "cotree3"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


files = []
for p in sorted(SEAT.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(SEAT)
    if any(part in SKIP_DIRS for part in rel.parts):
        continue
    if rel.name in ("manifest.json", "manifest.sha256"):
        continue
    files.append({"path": str(rel), "bytes": p.stat().st_size,
                  "sha256": sha256(p)})
manifest = {"seat": "audio-r89-verifier", "commit": "0d732989",
            "note": "manifest.sha256 covers every entry here plus "
                    "manifest.json's own final sha256; manifest.sha256 "
                    "itself cannot list itself (its hash is reported in "
                    "reports/round-89/r89-verifier.md).",
            "files": files}
(SEAT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
lines = [f"{f['sha256']}  {f['path']}\n" for f in files]
lines.append(f"{sha256(SEAT / 'manifest.json')}  manifest.json\n")
(SEAT / "manifest.sha256").write_text("".join(lines))
print(f"files={len(files)} total_bytes={sum(f['bytes'] for f in files)}")
print(f"manifest.json sha256={sha256(SEAT / 'manifest.json')}")
print(f"manifest.sha256 sha256={sha256(SEAT / 'manifest.sha256')}")
