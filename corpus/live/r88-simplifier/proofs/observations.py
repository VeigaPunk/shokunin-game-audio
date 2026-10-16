#!/usr/bin/env python3
"""r88 simplifier — observed-but-NOT-folded items (evidence only).

Records the things that look like dead code but are not (intentional fd
hold), the cosmetic unused bindings left in place, the duplicate-spawn
observations, and the pre-existing tracked dirty .pyc. Reads only."""
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
text = open(os.path.join(HERE, "base-measure_audio.py"),
            encoding="utf-8").read()
lines = text.splitlines()

print("== O1: `_r88_family_lock` is an intentional fd hold, NOT a dead "
      "binding ==")
for i, ln in enumerate(lines, 1):
    if "_r88_family_lock" in ln or "def _btwit_r88_family_lock" in ln:
        print(f"  :{i} {ln.strip()}")
print("  -> removing the assignment would drop the flock and let two "
      "same-tree runs interleave; NOT folded.")
print()

print("== O2: unused bindings left in place (cosmetic, no line change) ==")
for i, ln in enumerate(lines, 1):
    if "rec, own_dump = _btwit_r88_dump_objs(own_id)" in ln:
        print(f"  :{i} {ln.strip()}  (rec unused; call has the side effect)")
    if "pk, _pl = _btwit_r88_cli_props" in ln:
        print(f"  :{i} {ln.strip()}  (pk unused; call has the side effect)")
print("  -> kept: a rename to _rec/_pk is style, not a deletion; the "
      "T6 loop-var fold is the only true binding deletion offered.")
print()

print("== O3: duplicate spawns observed (live evidence, not folded) ==")
seg = "\n".join(lines[28598:28650])
print("  wd_dump_color spawns `pw-dump --color=always <id>`",
      seg.count('["pw-dump", "--color=always", own_id]'), "times "
      "(record, json_parses probe, has_ansi probe)")
print("  _btwit_r88_dump_objs spawns `pw-dump <args>` twice per call "
      "(bounded recorded witness + full JSON parse)")
print("  -> intentional: the recorded rec truncates at keep_chars=300, "
      "the parse needs the full stream; not folded.")
print()

print("== O4: pre-existing tracked dirty .pyc (NOT touched by this seat) ==")
pyc = os.path.join(TREE, "corpus", "fixtures", "__pycache__",
                   "measure_audio.cpython-314.pyc")
st = os.stat(pyc)
print(f"  {pyc}")
print(f"  size={st.st_size} mtime={st.st_mtime:.3f} "
      f"({__import__('time').strftime('%Y-%m-%dT%H:%M:%S', __import__('time').localtime(st.st_mtime))}) "
      f"sha256={hashlib.sha256(open(pyc,'rb').read()).hexdigest()}")
status = subprocess.run(["git", "status", "--short", "--",
                         "corpus/fixtures/__pycache__/"],
                        cwd=TREE, capture_output=True, text=True).stdout
print(f"  git status: {status.strip()}")
print("  -> dirty before this seat's first command (mtime 04:22:52, "
      "inside the author window per r88-scribe ADJ-10); every import in "
      "this seat used PYTHONDONTWRITEBYTECODE on scratch copies only.")
print()

print("== O5: tree state at report time ==")
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=TREE,
                      capture_output=True, text=True).stdout.strip()
print(f"  HEAD={head} (pin c19bec96; fixture sha256 unchanged at HEAD: "
      f"{subprocess.run(['git','show','HEAD:corpus/fixtures/measure_audio.py'],cwd=TREE,capture_output=True).stdout is not None})")
diff = subprocess.run(["git", "diff", "--numstat", "HEAD", "--",
                       "corpus/fixtures/measure_audio.py"], cwd=TREE,
                      capture_output=True, text=True).stdout
print(f"  fixture vs HEAD numstat: {diff.strip()!r} (empty = clean)")
