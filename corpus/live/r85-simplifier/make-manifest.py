#!/usr/bin/env python3
"""r85 simplifier manifest — sha256 census of every seat artifact.
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
    "seat": "r85-simplifier",
    "wave": "shokunin-train-20261015-w22 / audio-r85-simplifier",
    "pinned_commit": "2a49d5401b55371a667ac86f66a3c200648f19e9",
    "base_blob": {"path": "corpus/fixtures/measure_audio.py",
                  "sha256": "714564a32141f134f849401dd029e1e10c4aa19bb848a43fd50f70a251499ee2",
                  "lines": 24900},
    "folded_blob": {"path": "corpus/live/r85-simplifier/proofs/folded/measure_audio.py",
                    "sha256": "840f35be6d4930fc4783db909d509a5c93e5b7fc24baf372d8bdf813516a62c6",
                    "lines": 24878},
    "patch": {"path": "corpus/live/r85-simplifier/r85-simplifier.patch",
              "sha256": "8d349469e61ac612251dcf61d66730099f2d946fe381edc61444f02b6d6e330c",
              "hunks": 21, "numstat": "42 64 corpus/fixtures/measure_audio.py",
              "net_lines": -22, "applied": False},
    "proofs": {"static": "19/19 PASS", "receipt": "8/8 PASS",
               "differential": "13/13 PASS",
               "bimodal_arms": "7/7 PASS",
               "patch_roundtrip": "byte-identical",
               "py_compile": "OK",
               "labrat_probe": "14/14 NOT-FALSIFIED + C1/C2 CONFIRMED"},
    "items": ["T1 dead constant PACTLMON_R85_STREAM_WAIT_S",
              "T2 zero-call helper _pactlmon_r85_wait_node",
              "T3 sd_leg ctx dead param (+2 call sites)",
              "T4 wait_tap_link sink dead param (+1 call site)",
              "T5 cap_leg/sd_leg `hit` dead stores x2",
              "T6 addr entry `sers` dead store",
              "T7 capture entry `lp` dead store",
              "T8 capture entry `want_node` dead loop payload",
              "T9 gsv closure `label` dead param (+20 call sites)",
              "T10 teardown dead guards (loads/leaf/l) x7",
              "T11 block `leaf = leaf or {}` (loads guard kept)",
              "T12 four subsumed (aN or {}) guards",
              "T13 vol_pct `(rec or {})` dead guard",
              "T14 capture pre-ladder `feeder is not None` dead conjunct"],
    "files": files,
    "file_count": len(files),
    "total_bytes": total,
}
Path("manifest.json").write_text(json.dumps(man, indent=2) + "\n")
Path("manifest.sha256").write_text(
    "".join(f"{f['sha256']}  {f['path']}\n" for f in files))
print(f"manifest: {len(files)} files, {total} bytes")
