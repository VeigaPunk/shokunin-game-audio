#!/usr/bin/env python3
"""r89 simplifier fold: exact-string, region-scoped (29255-30783), each
edit asserted to match exactly once (or exactly twice for the shared
teardown/block unload text) INSIDE the region. Writes
folded/measure_audio.py and fold.diff. Never touches the tracked tree."""
import hashlib
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "base-measure_audio.py")
OUTDIR = os.path.join(HERE, "folded")
OUT = os.path.join(OUTDIR, "measure_audio.py")

text = open(BASE, encoding="utf-8").read()
lines = text.splitlines(keepends=True)
R0, R1 = 29255, 30783          # 1-based inclusive region
prefix = "".join(lines[:R0 - 1])
region = "".join(lines[R0 - 1:R1])
suffix = "".join(lines[R1:])

assert region.startswith("# r89: the PW-PROFILER OUTPUT LATTICE")
assert region.rstrip().endswith("return entry")

EDITS = []          # (item, old, new, expected_count_in_region)


def edit(item, old, new, count=1):
    EDITS.append((item, old, new, count))


# ---------------- T1: _pwprof_r89_play dead role param -----------------
edit("T1a", "def _pwprof_r89_play(tag, target, tone, role=None):",
     "def _pwprof_r89_play(tag, target, tone):")
edit("T1b", '             "-P", f"media.role={role or PWPROF_R89_ROLE}",',
     '             "-P", f"media.role={PWPROF_R89_ROLE}",')

# ---------------- T2: _pwprof_r89_nleg dead wd param -------------------
edit("T2a", """def _pwprof_r89_nleg(n_arg, bound_s=PWPROF_R89_SIG_S, extra=(),
                     wd=None):""",
     """def _pwprof_r89_nleg(n_arg, bound_s=PWPROF_R89_SIG_S, extra=()):""")
edit("T2b", """        ["pw-profiler", "-J", *extra, "-n", str(n_arg)],
        bound_s + 8.0, wd=wd, sig_at=bound_s, sig=signal.SIGTERM,""",
     """        ["pw-profiler", "-J", *extra, "-n", str(n_arg)],
        bound_s + 8.0, sig_at=bound_s, sig=signal.SIGTERM,""")

# ---------------- T3: _pwprof_r89_block dead players param + loop ------
edit("T3a", """def _pwprof_r89_block(entry, failures, msg, loads=None, players=()):
    \"\"\"The named coverage block: kill players, unload anything
    loaded, record the block.\"\"\"
    for proc in players or ():
        if proc is None:
            continue
        _alsapw_r84_killpg(proc, signal.SIGTERM)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _alsapw_r84_killpg(proc)
    entry["blocked"] = msg""",
     """def _pwprof_r89_block(entry, failures, msg, loads=None):
    \"\"\"The named coverage block: unload anything loaded, record the
    block.\"\"\"
    entry["blocked"] = msg""")

# ---------------- T4: _pwprof_r89_ensure_player dead wait_s default ----
edit("T4a", "def _pwprof_r89_ensure_player(ctx, tag, wait_s=6.0):",
     "def _pwprof_r89_ensure_player(ctx, tag):")
edit("T4b", "    deadline = time.monotonic() + wait_s",
     "    deadline = time.monotonic() + 6.0")

# ---------------- T5: teardown dead guards (dict domain) ---------------
edit("T5a", """            _alsapw_r84_killpg(proc)
    for tag, leaf in (loads or {}).items():
        leaf = leaf or {}
        entry.setdefault("unloads", {})[tag] = \\""",
     """            _alsapw_r84_killpg(proc)
    for tag, leaf in loads.items():
        entry.setdefault("unloads", {})[tag] = \\""")
edit("T5b",
     "        gone = {nm: nm not in sinks_now for nm in (loads or {})}",
     "        gone = {nm: nm not in sinks_now for nm in loads}")
edit("T5c", """        rest = sorted(n for n in names
                      if f"r89a_{PWPROF_R89_PID}" in n
                      or n in (loads or {}))""",
     """        rest = sorted(n for n in names
                      if f"r89a_{PWPROF_R89_PID}" in n
                      or n in loads)""")

# ---------------- T6: block leaf guard only ((loads or {}) retained) ---
edit("T6", '''    entry.setdefault("coverage_blocked", []).append(msg)
    for tag, leaf in (loads or {}).items():
        leaf = leaf or {}
''', '''    entry.setdefault("coverage_blocked", []).append(msg)
    for tag, leaf in (loads or {}).items():
''')

# ---------------- T5d: dead .get() fallbacks on load_ns leaves ---------
edit("T5d", """                leaf.get("module_id"),
                leaf.get("field", "sink_name"),
                leaf.get("value", tag))""",
     """                leaf.get("module_id"),
                leaf["field"],
                leaf["value"])""", count=2)

# ---------------- T7: schema verdict dead stats guard ------------------
edit("T7", '    st = l.get("stats") or {}', '    st = l.get("stats")')

folded = region
for item, old, new, count in EDITS:
    n = folded.count(old)
    assert n == count, (item, "matches", n, "expected", count)
    folded = folded.replace(old, new)
    print(f"{item}: {n} site(s) folded")

# region-only assertions: removed strings gone, kept strings kept
for bad in ("role=None", "role or PWPROF_R89_ROLE",
            "wd=None):", ", wd=wd,", "wait_s",
            "leaf = leaf or {}",
            "leaf.get(\"field\", \"sink_name\")",
            "leaf.get(\"value\", tag)",
            "l.get(\"stats\") or {}",
            "def _pwprof_r89_block(entry, failures, msg, loads=None, players=()):"):
    assert bad not in folded, bad
assert folded.count("(loads or {})") == 1        # the block head only
assert folded.count("for tag, leaf in loads.items():") == 1
assert folded.count('leaf["field"],') == 2
assert folded.count("time.monotonic() + 6.0") == 1
assert folded.count("players or ()") == 1        # teardown loop only
assert "def _pwprof_r89_block(entry, failures, msg, loads=None):" in folded
assert "players" not in folded.split("def _pwprof_r89_block(entry")[1] \
    .split("def _pwprof_r89_play")[0]

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
base_oid = subprocess.run(["git", "hash-object", BASE], cwd=HERE,
                          capture_output=True, text=True).stdout.strip()
fold_oid = subprocess.run(["git", "hash-object", OUT], cwd=HERE,
                          capture_output=True, text=True).stdout.strip()
diff = re.sub(r"^diff --git .*base-measure_audio\.py .*folded/measure_audio\.py$",
              "diff --git a/corpus/fixtures/measure_audio.py "
              "b/corpus/fixtures/measure_audio.py", diff, flags=re.M)
diff = re.sub(r"^--- .*base-measure_audio\.py$",
              "--- a/corpus/fixtures/measure_audio.py", diff, flags=re.M)
diff = re.sub(r"^\+\+\+ .*folded/measure_audio\.py$",
              "+++ b/corpus/fixtures/measure_audio.py", diff, flags=re.M)
diff = re.sub(r"^(old|new) mode .*\n", "", diff, flags=re.M)
diff = re.sub(r"^index [0-9a-f]+\.\.[0-9a-f]+$",
              f"index {base_oid[:7]}..{fold_oid[:7]} 100755", diff, flags=re.M)
open(os.path.join(HERE, "fold.diff"), "w").write(diff)
print("fold.diff lines:", len(diff.splitlines()))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
print("numstat:",
      subprocess.run(["git", "apply", "--numstat",
                      os.path.join(HERE, "fold.diff")], cwd=TREE,
                     capture_output=True, text=True).stdout.strip())
