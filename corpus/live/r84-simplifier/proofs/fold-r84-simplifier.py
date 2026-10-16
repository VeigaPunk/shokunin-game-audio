#!/usr/bin/env python3
"""r84 simplifier fold — apply the 8 items (12 exact-match replacements /
deletions) to a scratch copy of the commit-pinned r84 blob.

Every replacement is asserted to match EXACTLY ONCE in the base file; the
fold aborts on 0 or >1 matches (the r83 homograph discipline). Writes only
proofs/folded/measure_audio.py (scratch) and proofs/fold-apply.txt.

Usage: python3 fold-r84-simplifier.py <base.py> <out.py>
"""
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "proofs/base-measure_audio.py"
OUT = sys.argv[2] if len(sys.argv) > 2 else "proofs/folded/measure_audio.py"

# (item, old, new) — exact text, no regex
EDITS = [
    # T1 — unused constant (copy of PWCAT_R83_LINK_WAIT_S; zero refs)
    ("T1",
     'ALSAPW_R84_LINK_WAIT_S = 5.0\nALSAPW_R84_STREAM_WAIT_S = 8.0',
     'ALSAPW_R84_STREAM_WAIT_S = 8.0'),
    # T2a — dead falsy guard in teardown
    ("T2a",
     '    for tag, leaf in (loads or {}).items():\n'
     '        entry.setdefault("unloads", {})[tag] = _gst_r81_unload_own(\n'
     '            (leaf or {}).get("module_id"), sink_name=tag)\n'
     '    sinks_now = _capture_r77_sink_names_strict()',
     '    for tag, leaf in (loads or {}).items():\n'
     '        entry.setdefault("unloads", {})[tag] = _gst_r81_unload_own(\n'
     '            leaf.get("module_id"), sink_name=tag)\n'
     '    sinks_now = _capture_r77_sink_names_strict()'),
    # T2b — dead falsy guard in block
    ("T2b",
     '    for tag, leaf in (loads or {}).items():\n'
     '        entry.setdefault("unloads", {})[tag] = _gst_r81_unload_own(\n'
     '            (leaf or {}).get("module_id"), sink_name=tag)\n'
     '    entry["failures"] = failures',
     '    for tag, leaf in (loads or {}).items():\n'
     '        entry.setdefault("unloads", {})[tag] = _gst_r81_unload_own(\n'
     '            leaf.get("module_id"), sink_name=tag)\n'
     '    entry["failures"] = failures'),
    # T3a — dead parameter `ctx` in st_leg
    ("T3a",
     'def _alsapw_r84_st_leg(dev, ctx, tail, timeout_s=25.0):',
     'def _alsapw_r84_st_leg(dev, tail, timeout_s=25.0):'),
    # T3b — call site 1 drops the dead argument
    ("T3b",
     '                legs["st_pw_node"] = _alsapw_r84_st_leg(\n'
     '                    f"pipewire:NODE={ns}", ctx,\n'
     '                    ["-c", "2", "-l", "1", "-t", "sine", "-f", "700"])',
     '                legs["st_pw_node"] = _alsapw_r84_st_leg(\n'
     '                    f"pipewire:NODE={ns}",\n'
     '                    ["-c", "2", "-l", "1", "-t", "sine", "-f", "700"])'),
    # T3c — call site 2 drops the dead argument
    ("T3c",
     '                legs["st_pw_c6"] = _alsapw_r84_st_leg(\n'
     '                    f"pipewire:NODE={ns}", ctx,\n'
     '                    ["-c", "6", "-l", "1", "-t", "sine", "-f", "700"],\n'
     '                    timeout_s=42.0)',
     '                legs["st_pw_c6"] = _alsapw_r84_st_leg(\n'
     '                    f"pipewire:NODE={ns}",\n'
     '                    ["-c", "6", "-l", "1", "-t", "sine", "-f", "700"],\n'
     '                    timeout_s=42.0)'),
    # T4a — dead `hit` store in prop_leg
    ("T4a",
     '    err = proc.stderr.read().decode(errors="replace")\n'
     '    cls, hit = _alsapw_r84_errclass(err)\n'
     '    rec.update({"exit_code": proc.returncode,\n'
     '                "signal": (signal.Signals(-proc.returncode).name\n'
     '                           if (proc.returncode or 0) < 0 else None),\n'
     '                "killed": killed,',
     '    err = proc.stderr.read().decode(errors="replace")\n'
     '    cls, _ = _alsapw_r84_errclass(err)\n'
     '    rec.update({"exit_code": proc.returncode,\n'
     '                "signal": (signal.Signals(-proc.returncode).name\n'
     '                           if (proc.returncode or 0) < 0 else None),\n'
     '                "killed": killed,'),
    # T4b — dead `hit` store in negctl ctl_sigkill
    ("T4b",
     '        err = kill_proc.stderr.read().decode(errors="replace")\n'
     '        cls, hit = _alsapw_r84_errclass(err)\n'
     '        legs["ctl_sigkill"] = {',
     '        err = kill_proc.stderr.read().decode(errors="replace")\n'
     '        cls, _ = _alsapw_r84_errclass(err)\n'
     '        legs["ctl_sigkill"] = {'),
    # T5 — dead pre-loop fetch in wait_moved
    ("T5",
     '    t0 = time.monotonic()\n'
     '    leaf = _alsapw_r84_stream_leaf(tag)\n'
     '    while time.monotonic() - t0 < timeout_s:',
     '    t0 = time.monotonic()\n'
     '    while time.monotonic() - t0 < timeout_s:'),
    # T6 — dead pre-loop init in prop_leg
    ("T6",
     '    node = None\n'
     '    g = {}\n'
     '    while time.monotonic() - t0 < 2.2:',
     '    node = None\n'
     '    while time.monotonic() - t0 < 2.2:'),
    # T7 — subsumed `(si1 or {})` in the sticky guard
    ("T7",
     '    if si1 is None or (si1 or {}).get("sink") in (None, 4294967295):',
     '    if si1 is None or si1.get("sink") in (None, 4294967295):'),
    # T8 — redundant recomputation of `flipped` in hold_note
    ("T8",
     '                    "hold_note": ("own pin flipped a pcm"\n'
     '                                  if held_pcm in [k for k in running\n'
     '                                                  if "RUNNING" not in\n'
     '                                                  states0.get(k, "")]\n'
     '                                  else "held pcm set (may include a "\n'
     '                                       "foreign-held device)")}',
     '                    "hold_note": ("own pin flipped a pcm"\n'
     '                                  if held_pcm in flipped\n'
     '                                  else "held pcm set (may include a "\n'
     '                                       "foreign-held device)")}'),
    # T9a — teardown's `(loads or {})` (required positional; all 4 call sites
    # pass a dict). Runs AFTER T2a so the anchor is teardown-specific.
    ("T9a",
     '    for tag, leaf in (loads or {}).items():\n'
     '        entry.setdefault("unloads", {})[tag] = _gst_r81_unload_own(\n'
     '            leaf.get("module_id"), sink_name=tag)\n'
     '    sinks_now = _capture_r77_sink_names_strict()',
     '    for tag, leaf in loads.items():\n'
     '        entry.setdefault("unloads", {})[tag] = _gst_r81_unload_own(\n'
     '            leaf.get("module_id"), sink_name=tag)\n'
     '    sinks_now = _capture_r77_sink_names_strict()'),
    # T9bc — teardown's remaining `(loads or {})` sites; the anchor runs
    # through the ALSAPW_R84_PREFIX line so the r83 twin (identical region)
    # cannot match (the r83 helper uses the same text).
    ("T9bc",
     '        gone = {nm: nm not in sinks_now for nm in (loads or {})}\n'
     '        entry["sinks_gone"] = gone\n'
     '        if not all(gone.values()):\n'
     '            failures.append(\n'
     '                "teardown: probe sinks survived unload: "\n'
     '                f"{[n for n, g in gone.items() if not g]}")\n'
     '    names = _playback_r78_node_names()\n'
     '    if names is None:\n'
     '        entry["own_nodes_after"] = "reader_error"\n'
     '        entry.setdefault("coverage_blocked", []).append(\n'
     '            "teardown: node reader failed — own_nodes_after unmeasured")\n'
     '    else:\n'
     '        rest = sorted(n for n in names\n'
     '                      if ALSAPW_R84_PREFIX in n or n in (loads or {}))',
     '        gone = {nm: nm not in sinks_now for nm in loads}\n'
     '        entry["sinks_gone"] = gone\n'
     '        if not all(gone.values()):\n'
     '            failures.append(\n'
     '                "teardown: probe sinks survived unload: "\n'
     '                f"{[n for n, g in gone.items() if not g]}")\n'
     '    names = _playback_r78_node_names()\n'
     '    if names is None:\n'
     '        entry["own_nodes_after"] = "reader_error"\n'
     '        entry.setdefault("coverage_blocked", []).append(\n'
     '            "teardown: node reader failed — own_nodes_after unmeasured")\n'
     '    else:\n'
     '        rest = sorted(n for n in names\n'
     '                      if ALSAPW_R84_PREFIX in n or n in loads)'),
    # T10 — ebusy pre-loop init pair: the loop bound is the hardcoded literal
    # 5.0, so the values are never read (labrat item #2 + the symmetric half)
    ("T10",
     '                held_pcm = None\n'
     '                states_held = {}\n'
     '                t0 = time.monotonic()\n'
     '                while time.monotonic() - t0 < 5.0:',
     '                t0 = time.monotonic()\n'
     '                while time.monotonic() - t0 < 5.0:'),
]

src = open(BASE, encoding="utf-8").read()
log = [f"base={BASE} bytes={len(src)}"]
for item, old, new in EDITS:
    n = src.count(old)
    log.append(f"{item}: matches={n} delta_lines={new.count(chr(10)) - old.count(chr(10))}")
    if n != 1:
        raise SystemExit(f"ABORT {item}: expected exactly 1 match, got {n}")
    src = src.replace(old, new, 1)

import os
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(src)
log.append(f"folded={OUT} bytes={len(src)}")
open("proofs/fold-apply.txt", "w").write("\n".join(log) + "\n")
print("\n".join(log))
