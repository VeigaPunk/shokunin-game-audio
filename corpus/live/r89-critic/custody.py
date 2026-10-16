#!/usr/bin/env python3
"""r89 critic: custody + wiring static verification of committed 0d732989.

Reads ONLY the commit object (git show) and the worktree; writes nothing
tracked. Emits custody.json.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMMIT = "0d732989"
FIXTURE = "corpus/fixtures/measure_audio.py"
OUT = Path(__file__).resolve().parent


def sh(*a):
    return subprocess.run(a, cwd=ROOT, capture_output=True, text=True).stdout


src = sh("git", "show", f"{COMMIT}:{FIXTURE}")
work = (ROOT / FIXTURE).read_text()
diff = sh("git", "show", COMMIT, "--", FIXTURE)

res = {}
res["commit"] = COMMIT
res["commit_full"] = sh("git", "rev-parse", COMMIT).strip()
res["blob_sha256"] = __import__("hashlib").sha256(src.encode()).hexdigest()
res["worktree_sha256"] = __import__("hashlib").sha256(work.encode()).hexdigest()
res["worktree_identical"] = src == work
res["numstat"] = sh("git", "show", COMMIT, "--numstat").strip().splitlines()
res["stat"] = sh("git", "show", COMMIT, "--stat").strip().splitlines()[-1]

# hunk census: per-hunk +/- counts
hunks = []
cur = None
for ln in diff.splitlines():
    m = re.match(r"^@@ -(\d+),(\d+) \+(\d+),(\d+) @@(.*)$", ln)
    if m:
        cur = {"old_at": int(m.group(1)), "old_len": int(m.group(2)),
               "new_at": int(m.group(3)), "new_len": int(m.group(4)),
               "ctx": m.group(5).strip(), "plus": 0, "minus": 0}
        hunks.append(cur)
        continue
    if cur is None:
        continue
    if ln.startswith("+") and not ln.startswith("+++"):
        cur["plus"] += 1
    elif ln.startswith("-") and not ln.startswith("---"):
        cur["minus"] += 1
res["hunks"] = hunks
res["total_plus"] = sum(h["plus"] for h in hunks)
res["total_minus"] = sum(h["minus"] for h in hunks)

# every deleted line, verbatim (only the 3 wiring splices may be deleted)
res["deleted_lines"] = [ln[1:] for ln in diff.splitlines()
                        if ln.startswith("-") and not ln.startswith("---")]
res["deleted_count"] = len(res["deleted_lines"])
res["deleted_kinds"] = []
for ln in res["deleted_lines"]:
    if ln.strip().startswith("if sum(["):
        res["deleted_kinds"].append("mutex-sum")
    elif ln.strip().startswith("mode = "):
        res["deleted_kinds"].append("mode-ternary")
    elif ln.strip().startswith("suffix = "):
        res["deleted_kinds"].append("suffix-ternary")
    else:
        res["deleted_kinds"].append("OTHER:" + ln[:60])

# inserted r89 block boundaries in the committed source
lines = src.splitlines()
start = next(i for i, l in enumerate(lines)
             if l.startswith("# r89: the PW-PROFILER OUTPUT LATTICE"))
end = next(i for i, l in enumerate(lines)
           if l.startswith("def pwprof_gate_r89_entry()"))
prev_end = max(i for i, l in enumerate(lines[:start])
               if l.startswith("def ") or l.startswith("# r88"))
res["block_start_line"] = start + 1
res["block_end_line"] = end
res["block_lines"] = end - start
# where does it sit? after pwtop_r88_entry()'s return, before def main()
prev_def = [l for l in lines[:start] if l.startswith("def ")][-1]
res["preceding_def"] = prev_def
next_def = lines[end]
res["first_line_of_block"] = lines[start]
res["append_position"] = "after r88 entry block, before def main()"

# wiring assertions (programmatic, on the committed source)
w = {}
w["arg_present"] = bool(re.search(
    r'add_argument\("--probe-pwprof-r89", action="store_true"\)', src))
m = re.search(r"if sum\(\[(.*?)\]\) > 1:", src, re.S)
w["mutex_sum_line"] = "args.probe_pwprof_r89" in (m.group(1) if m else "")
w["mutex_count"] = (m.group(1).count("args.probe_") if m else None)
w["dispatch_present"] = bool(re.search(
    r"if args\.probe_pwprof_r89:", src))
w["lock_before_first_entry"] = bool(re.search(
    r"if args\.probe_pwprof_r89:\n(?:.*\n)*?\s+_r89_family_lock = "
    r"_pwprof_r89_family_lock\(\)\s*# held to exit\n"
    r"(?:.*\n)*?\s+measurements\[\"pwprof_gate_r89_probe\"\]", src))
w["entries_dispatched"] = re.findall(
    r"measurements\[\"(pwprof_[a-z_0-9]+)\"\] = \\\n\s+(pwprof_[a-z_0-9]+)_entry\(\)",
    src)
m = re.search(r'mode = (.*?)\n', src, re.S)
w["mode_first"] = m.group(1).strip().startswith(
    '"probe-pwprof-r89" if args.probe_pwprof_r89')
m = re.search(r'suffix = (.*?)\n', src, re.S)
w["suffix_first"] = m.group(1).strip().startswith(
    '"-pwprof-r89" if args.probe_pwprof_r89')
res["wiring"] = w

# guard assertions
g = {}
g["set_default_occurrences"] = len(re.findall(r"set-default", src))
g["set_default_non_comment"] = [
    l for l in lines if "set-default" in l and not l.strip().startswith("#")]
g["role_key"] = "r89arole" in src
g["role_never_music"] = not re.search(r'media\.role=\{?["\']music', src)
g["killpg_used"] = src.count("_alsapw_r84_killpg(")
g["own_namespace"] = "r89a_" in src
g["fixed_lock_path"] = (
    '_pwprof_r89_family_lock' in src and
    'ROOT / "live" / "measure_audio-pwprof-r89.lock"' in src)
g["tmpdir_lock"] = bool(re.search(
    r"_pwprof_r89_family_lock[\s\S]{0,400}?gettempdir", src))
g["name_verified_unload"] = "_pactlmon_r85_unload_own" in src
g["sinks_gone_armed"] = 'entry["sinks_gone"]' in src
g["own_nodes_after_armed"] = 'entry["own_nodes_after"]' in src
res["guards"] = g

# compile check of the committed source (in-memory, no bytecode written)
try:
    compile(src, FIXTURE, "exec")
    res["compile_ok"] = True
except SyntaxError as exc:
    res["compile_ok"] = f"SyntaxError: {exc}"

# prior-family guard: does the commit touch any r76-r88 line?
res["prior_family_lines_touched"] = [
    ln for ln in res["deleted_lines"] if "r8" in ln and "probe_pwprof" not in ln
]

(OUT / "custody.json").write_text(json.dumps(res, indent=2) + "\n")
print(json.dumps({k: v for k, v in res.items()
                  if k not in ("deleted_lines",)}, indent=2)[:4000])
print("deleted_lines[:1]:", res["deleted_lines"][:1])
