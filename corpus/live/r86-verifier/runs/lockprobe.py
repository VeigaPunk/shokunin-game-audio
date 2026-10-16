#!/usr/bin/env python3
"""r86-verifier executed lock probe (verifier-owned).

H: the committed `_pwctl_r86_family_lock` resolves its lock path to
<ROOT>/live/measure_audio-pwctl-r86.lock independent of TMPDIR, while the
r85 `_pactlmon_r85_family_lock` is TMPDIR-scoped. Extraction is by anchor
from the FROZEN TREE fixture (sha 5ceba940…, identical to committed blob);
no fixture import, no live-audio effect.

Runs the helpers with TMPDIR pointed at a fresh foreign scratch dir and a
patched ROOT (scratch corpus) plus, for r86, the frozen-tree ROOT.
"""
import fcntl
import json
import os
import re
import sys
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()          # frozen tree root
FIXTURE = TREE / "corpus" / "fixtures" / "measure_audio.py"
FOREIGN = Path(sys.argv[2]).resolve()       # foreign TMPDIR
SCRATCH_ROOT = Path(sys.argv[3]).resolve()  # scratch corpus dir (has live/)

src = FIXTURE.read_text()


def extract(name):
    m = re.search(rf"^def {name}\(\):.*?(?=^def |\Z)", src, re.S | re.M)
    if not m:
        raise SystemExit(f"anchor not found: {name}")
    return m.group(0)


r86_src = extract("_pwctl_r86_family_lock")
r85_src = extract("_pactlmon_r85_family_lock")

results = {"tmpdir": str(FOREIGN), "checks": []}


def check(name, ok, detail):
    results["checks"].append({"check": name, "ok": bool(ok), "detail": str(detail)})


os.environ["TMPDIR"] = str(FOREIGN)
FOREIGN.mkdir(parents=True, exist_ok=True)
(SCRATCH_ROOT / "live").mkdir(parents=True, exist_ok=True)

# --- r86: frozen-tree ROOT (the real lane layout, frozen copy) ---
ns86 = {"os": os, "fcntl": fcntl, "Path": Path,
        "ROOT": TREE / "corpus",
        "PWCTL_R86_PID": 424242, "PWCTL_R86_NS": "r86a_ns_424242",
        "PWCTL_R86_ROLE": "r86arole424242"}
exec(r86_src, ns86)
fd = ns86["_pwctl_r86_family_lock"]()
r86_path = TREE / "corpus" / "live" / "measure_audio-pwctl-r86.lock"
check("r86.lock_at_frozen_tree_corpus_live", r86_path.exists(), r86_path)
check("r86.lock_not_under_foreign_tmpdir",
      not (FOREIGN / "measure_audio-pwctl-r86.lock").exists(),
      FOREIGN / "measure_audio-pwctl-r86.lock")
check("r86.lock_witness_written", r86_path.read_text().startswith("pid=424242 "),
      r86_path.read_text().strip())
# contention: a second exclusive attempt must block while fd is held
blocked = False
try:
    fd2 = os.open(str(r86_path), os.O_RDWR)
    fcntl.flock(fd2, fcntl.LOCK_EX | fcntl.LOCK_NB)
    os.close(fd2)
except BlockingIOError:
    blocked = True
check("r86.second_exclusive_attempt_blocks_while_held", blocked, blocked)
os.close(fd)
fd3 = os.open(str(r86_path), os.O_RDWR)
fcntl.flock(fd3, fcntl.LOCK_EX | fcntl.LOCK_NB)
os.close(fd3)
check("r86.lock_free_after_release", True, True)

# --- r86: scratch ROOT (proves ROOT-relative, not fixed absolute) ---
ns86b = dict(ns86)
ns86b["ROOT"] = SCRATCH_ROOT
exec(r86_src, ns86b)
fd = ns86b["_pwctl_r86_family_lock"]()
scratch_lock = SCRATCH_ROOT / "live" / "measure_audio-pwctl-r86.lock"
check("r86.scratch_root_lock_follows_ROOT", scratch_lock.exists(), scratch_lock)
check("r86.scratch_root_still_not_under_foreign_tmpdir",
      not (FOREIGN / "measure_audio-pwctl-r86.lock").exists(),
      FOREIGN)
os.close(fd)

# --- r85 control: TMPDIR-scoped ---
ns85 = {"os": os, "fcntl": fcntl, "Path": Path, "tempfile": __import__("tempfile"),
        "PACTLMON_R85_PID": 424242, "PACTLMON_R85_NS": "r85v_ns_424242",
        "PACTLMON_R85_ROLE": "r85vrole424242"}
exec(r85_src, ns85)
fd = ns85["_pactlmon_r85_family_lock"]()
r85_path = FOREIGN / "measure_audio-pactlmon-r85.lock"
check("r85.control_lock_under_foreign_tmpdir", r85_path.exists(), r85_path)
os.close(fd)

print(json.dumps(results, indent=1))
sys.exit(0 if all(c["ok"] for c in results["checks"]) else 1)
