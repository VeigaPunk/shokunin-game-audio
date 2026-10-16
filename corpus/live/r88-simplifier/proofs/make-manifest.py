#!/usr/bin/env python3
"""r88 simplifier — manifest of every file this seat wrote under
corpus/live/r88-simplifier/ (sha256 census). Excludes __pycache__."""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # corpus/live/r88-simplifier


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


files = {}
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d != "__pycache__"]
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        rel = os.path.relpath(p, ROOT)
        if rel in ("manifest.json", "manifest.sha256",
                   "proofs/manifest-census.txt"):
            continue
        files[rel] = {"sha256": sha(p), "bytes": os.path.getsize(p)}

manifest = {
    "seat": "r88-simplifier",
    "pin": {"commit": "c19bec96",
            "blob": "corpus/fixtures/measure_audio.py",
            "sha256":
            "ad9d59b1e0dc5e2be4274f4966e571dabefed94076c06093eed1bf4cd2aef4c4",
            "lines": 30504},
    "folded": {"sha256":
               "1beac939703a163093c2f634c3ec61e3e5d2bea6ac7a56966c3f398e55a045a6",
               "lines": 30497},
    "patch": {"file": "proofs/fold.diff", "applied": False,
              "numstat": "12 19",
              "sha256": files["proofs/fold.diff"]["sha256"]},
    "files": files,
    "file_count": len(files),
}
open(os.path.join(ROOT, "manifest.json"), "w").write(
    json.dumps(manifest, indent=2, sort_keys=True) + "\n")
lines = [f"{v['sha256']}  {k}" for k, v in sorted(files.items())]
open(os.path.join(ROOT, "manifest.sha256"), "w").write("\n".join(lines) + "\n")
census = (f"manifest: {len(files)} files\n" + "\n".join(
    f"  {v['sha256'][:16]}…  {v['bytes']:>9}  {k}"
    for k, v in sorted(files.items())) + "\n")
open(os.path.join(HERE, "manifest-census.txt"), "w").write(census)
print(census, end="")
