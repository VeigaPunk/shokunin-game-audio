#!/usr/bin/env python3
"""r88 simplifier fold: exact-string, region-scoped (27507-29252), each
edit asserted to match exactly once (or exactly twice for the shared
teardown/block unload text) INSIDE the region. Writes
folded/measure_audio.py and fold.diff. Never touches the tracked tree."""
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "base-measure_audio.py")
OUTDIR = os.path.join(HERE, "folded")
OUT = os.path.join(OUTDIR, "measure_audio.py")

text = open(BASE, encoding="utf-8").read()
lines = text.splitlines(keepends=True)
R0, R1 = 27507, 29252          # 1-based inclusive region
prefix = "".join(lines[:R0 - 1])
region = "".join(lines[R0 - 1:R1])
suffix = "".join(lines[R1:])

assert region.startswith("# r88: the BLUEZ ABSENT-CLASS")
assert region.rstrip().endswith("return entry")

EDITS = []          # (item, old, new, expected_count_in_region)


def edit(item, old, new, count=1):
    EDITS.append((item, old, new, count))


# ---------------- T1: _btwit_r88_run dead env/stdin_data ----------------
edit("T1a", """def _btwit_r88_run(argv, timeout_s, env=None, stdin_data=None,
                   keep_chars=900, keep_raw=False):""",
     """def _btwit_r88_run(argv, timeout_s, keep_chars=900, keep_raw=False):""")

edit("T1b", """        proc = subprocess.Popen(
            argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=(subprocess.PIPE if stdin_data is not None
                   else subprocess.DEVNULL),
            env=env, start_new_session=True)""",
     """        proc = subprocess.Popen(
            argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, start_new_session=True)""")

edit("T1c",
     "        out, err = proc.communicate(input=stdin_data, timeout=timeout_s)",
     "        out, err = proc.communicate(timeout=timeout_s)")

# ---------------- T2: teardown dead guards (dict domain) ----------------
edit("T2a", '''    via pw-cli before the final sweep."""
    for tag, leaf in (loads or {}).items():
        leaf = leaf or {}
        entry.setdefault("unloads", {})[tag] = \\''',
     '''    via pw-cli before the final sweep."""
    for tag, leaf in loads.items():
        entry.setdefault("unloads", {})[tag] = \\''')

edit("T2b",
     "        gone = {nm: nm not in sinks_now for nm in (loads or {})}",
     "        gone = {nm: nm not in sinks_now for nm in loads}")

edit("T2c", """        rest = sorted(n for n in names
                      if f"r88a_{BTWIT_R88_PID}" in n
                      or n in (loads or {}))""",
     """        rest = sorted(n for n in names
                      if f"r88a_{BTWIT_R88_PID}" in n
                      or n in loads)""")

# ---------------- T3: block leaf guard only ((loads or {}) retained) ----
edit("T3", '''    entry.setdefault("coverage_blocked", []).append(msg)
    for tag, leaf in (loads or {}).items():
        leaf = leaf or {}
''', '''    entry.setdefault("coverage_blocked", []).append(msg)
    for tag, leaf in (loads or {}).items():
''')

# ---------------- T4: dead _frames_cache pops ---------------------------
edit("T4a", '        r_top.pop("_frames_cache", None)\n', "")
edit("T4b", '                    r_top2.pop("_frames_cache", None)\n', "")

# ---------------- T5: dead .get() fallbacks on load_ns leaves -----------
edit("T5", """                leaf.get("module_id"),
                leaf.get("field", "sink_name"),
                leaf.get("value", tag))""",
     """                leaf.get("module_id"),
                leaf["field"],
                leaf["value"])""", count=2)

# ---------------- T6: unused loop variable nid --------------------------
edit("T6", """            n.get("name") for nid, n in
            (g2.get("nodes") or {}).items()""",
     """            n.get("name") for n in
            (g2.get("nodes") or {}).values()""")

folded = region
for item, old, new, count in EDITS:
    n = folded.count(old)
    assert n == count, (item, "matches", n, "expected", count)
    folded = folded.replace(old, new)
    print(f"{item}: {n} site(s) folded")

# region-only assertions: the folded region must not contain the removed
# strings any more, and must not have lost anything else
for bad in ("stdin_data", "env=env", "env=None, stdin_data",
            "leaf = leaf or {}"):
    assert bad not in folded, bad
assert "for tag, leaf in loads.items():" in folded        # T2 head
assert "for tag, leaf in (loads or {}).items():" in folded  # T3 head kept
assert folded.count('_frames_cache') == 2   # the set (29047) + the verdict pop (29175)
assert folded.count('leaf["field"],') == 2   # the two unload call sites

new_text = prefix + folded + suffix
os.makedirs(OUTDIR, exist_ok=True)
open(OUT, "w", encoding="utf-8").write(new_text)
os.chmod(OUT, 0o755)   # tracked file mode is 100755

nl_old = len(lines)
nl_new = len(new_text.splitlines())
print(f"\nlines {nl_old} -> {nl_new} (net {nl_new - nl_old:+d})")
print("base sha256  :", hashlib.sha256(open(BASE, 'rb').read()).hexdigest())
print("folded sha256:", hashlib.sha256(new_text.encode()).hexdigest())

# unified diff (git-style) for patch round-trip
diff = subprocess.run(
    ["git", "diff", "--no-index", "--no-color", "--",
     "base-measure_audio.py", "folded/measure_audio.py"],
    cwd=HERE, capture_output=True, text=True).stdout
# normalize the header paths so the patch applies with -p1 against the
# tracked file corpus/fixtures/measure_audio.py
diff = re.sub(r"^diff --git .*base-measure_audio\.py .*folded/measure_audio\.py$",
              "diff --git a/corpus/fixtures/measure_audio.py "
              "b/corpus/fixtures/measure_audio.py", diff, flags=re.M)
diff = re.sub(r"^--- .*base-measure_audio\.py$",
              "--- a/corpus/fixtures/measure_audio.py", diff, flags=re.M)
diff = re.sub(r"^\+\+\+ .*folded/measure_audio\.py$",
              "+++ b/corpus/fixtures/measure_audio.py", diff, flags=re.M)
# the tracked file is mode 100755; drop the scratch-copy mode lines
# (base copy is 0644) and pin the index mode to the tracked mode
diff = re.sub(r"^(old|new) mode .*\n", "", diff, flags=re.M)
diff = re.sub(r"^index [0-9a-f]+\.\.[0-9a-f]+$",
              "index bc5a978..921c475 100755", diff, flags=re.M)
open(os.path.join(HERE, "fold.diff"), "w").write(diff)
print("fold.diff lines:", len(diff.splitlines()))
print("numstat:",
      subprocess.run(["git", "apply", "--numstat", "fold.diff"], cwd=HERE,
                     capture_output=True, text=True).stdout.strip())
