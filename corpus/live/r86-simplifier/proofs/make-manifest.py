#!/usr/bin/env python3
"""r86-simplifier manifest: sha256 + size census of every seat file
under corpus/live/r86-simplifier/ (manifest files excluded)."""
import hashlib
import json
from pathlib import Path

SEAT = Path(__file__).resolve().parent.parent
OUT = SEAT / "manifest.json"
SKIP = {"manifest.json", "manifest.sha256"}

files = []
for p in sorted(SEAT.rglob("*")):
    if not p.is_file():
        continue
    rel = str(p.relative_to(SEAT))
    if rel in SKIP or p.name in SKIP:
        continue
    if "__pycache__" in rel:
        continue
    files.append({"path": rel,
                  "size": p.stat().st_size,
                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})

manifest = {"seat": "r86-simplifier",
            "wave": "shokunin-train-20261015-w22",
            "pin": "fa5994a029507e666315cd40257988510579284f",
            "base_sha256":
                "5ceba94019eaaa8f1db9ac18ea15023f7e4891e844defe86711f"
                "37873059b780",
            "folded_sha256":
                "e35b0c2636b28ce292a20a27960f1179a08ff6af309657fe404337a"
                "73dc50c1b",
            "patch_sha256":
                "5cc93d42cb77288c5877ad63db22e6c8011c86481df1f22ac42d54"
                "14306dccf7",
            "files": files}
OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(f"manifest.json: {len(files)} files, "
      f"{sum(f['size'] for f in files)} bytes")
sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
(SEAT / "manifest.sha256").write_text(f"{sha}  manifest.json\n",
                                      encoding="utf-8")
print("manifest.sha256:", sha)
