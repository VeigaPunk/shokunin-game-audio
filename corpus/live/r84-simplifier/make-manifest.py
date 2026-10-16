#!/usr/bin/env python3
"""r84 simplifier manifest — sha256 census of every seat artifact.
Writes manifest.json + manifest.sha256 (excludes __pycache__).
"""
import hashlib
import json
import os
from pathlib import Path

SKIP_DIRS = {"__pycache__"}
files = []
for root, dirs, names in os.walk("."):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for n in sorted(names):
        if n in ("manifest.json", "manifest.sha256"):
            continue
        p = Path(root) / n
        rel = str(p)[2:] if str(p).startswith("./") else str(p)
        data = p.read_bytes()
        files.append({"path": rel, "bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest()})
files.sort(key=lambda f: f["path"])
total = sum(f["bytes"] for f in files)
man = {
    "seat": "r84-simplifier",
    "wave": "shokunin-train-20261015-w22 / audio-r84-simplifier",
    "pinned_commit": "fbe65713b5adf1e76b3f6839968fc813a36d3fbf",
    "base_blob": {"path": "corpus/fixtures/measure_audio.py",
                  "sha256": "8ed09d19990480fd337cba99e45cb0588e0615fd90e34793ecc4841c21368e4e",
                  "lines": 22725},
    "folded_blob": {"path": "corpus/live/r84-simplifier/proofs/folded/measure_audio.py",
                    "sha256": "65c21ab77b07a678e2ebb21271ec025b0031b48aff5f513c1295bfa5cf63bff9",
                    "lines": 22718},
    "patch": {"path": "corpus/live/r84-simplifier/r84-simplifier.patch",
              "sha256": "df424b848694d73472ff64e99f3ccfb0983477dfb6e446844669ea6a40e89c80",
              "hunks": 13, "numstat": "12 19 corpus/fixtures/measure_audio.py",
              "applied": False},
    "proofs": {"static": "21/21 PASS", "receipt": "9/9 PASS",
               "differential": "8/8 PASS",
               "patch_roundtrip": "byte-identical",
               "py_compile": "OK"},
    "files": files,
    "file_count": len(files),
    "total_bytes": total,
}
Path("manifest.json").write_text(json.dumps(man, indent=2) + "\n")
Path("manifest.sha256").write_text(
    "".join(f"{f['sha256']}  {f['path']}\n" for f in files))
print(f"manifest: {len(files)} files, {total} bytes")
