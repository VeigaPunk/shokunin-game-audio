#!/usr/bin/env python3
"""r83-simplifier manifest — sha256 census of the seat's own outputs.

Writes corpus/live/r83-simplifier/manifest.json and manifest.sha256.
Run from the repo root:  python3 corpus/live/r83-simplifier/proofs/manifest.py
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]          # audio-shokunin/
SEAT = ROOT / "corpus" / "live" / "r83-simplifier"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


files = []
for p in sorted(SEAT.rglob("*")):
    if not p.is_file():
        continue
    if p.name in ("manifest.json", "manifest.sha256"):
        continue
    files.append({"bytes": p.stat().st_size,
                  "path": str(p.relative_to(SEAT)),
                  "sha256": sha(p)})

receipts = {f["path"]: {"bytes": f["bytes"], "sha256": f["sha256"]}
            for f in files if f["path"].startswith("proofs/")}

man = {
    "file_count": len(files),
    "files": files,
    "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "receipts": receipts,
    "seat": "audio r83 simplifier (executor-class, leaf)",
    "total_bytes": sum(f["bytes"] for f in files),
}
(SEAT / "manifest.json").write_text(json.dumps(man, indent=1) + "\n")
(SEAT / "manifest.sha256").write_text(
    "".join(f"{f['sha256']}  {f['path']}\n" for f in files))
print(f"manifest.json: {len(files)} files, "
      f"{man['total_bytes']} bytes")
