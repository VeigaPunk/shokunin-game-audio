#!/usr/bin/env python3
"""r87 simplifier — sha256 census of every seat file (receipts + report).

Writes corpus/live/r87-simplifier/manifest.json and manifest.sha256.
Read-only against the repo; only the two manifest files are written.
"""
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SEAT = HERE.parent
REPO = HERE.parents[3]
REPORT = REPO / "reports/round-87/r87-simplifier.md"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


# run-all.log is the live log of the invoking shell (it keeps growing
# until after this script exits) -> excluded by construction; every
# other seat file is hashed at its final bytes.
SKIP = {"manifest.json", "manifest.sha256", "run-all.log"}
files = {}
for p in sorted(SEAT.rglob("*")):
    if p.is_file() and p.name not in SKIP \
            and "__pycache__" not in p.parts and p.suffix != ".pyc":
        files[str(p.relative_to(REPO))] = sha(p)
if REPORT.exists():
    files[str(REPORT.relative_to(REPO))] = sha(REPORT)

manifest = {
    "seat": "r87-simplifier",
    "pin": "d1e687b9",
    "base_sha256": sha(HERE / "base-measure_audio.py"),
    "folded_sha256": sha(HERE / "folded" / "measure_audio.py"),
    "patch_sha256": sha(SEAT / "r87-simplifier.patch"),
    "files": files,
}
(SEAT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
lines = [f"{v}  {k}" for k, v in sorted(files.items())]
lines.append(f"{sha(SEAT / 'manifest.json')}  corpus/live/r87-simplifier/manifest.json")
(SEAT / "manifest.sha256").write_text("\n".join(lines) + "\n")
print(f"manifest: {len(files)} seat files + manifest.json")
print(f"base={manifest['base_sha256']}")
print(f"folded={manifest['folded_sha256']}")
print(f"patch={manifest['patch_sha256']}")
