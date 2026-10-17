#!/usr/bin/env python3
"""r95 SIMPLIFIER — apply the queued folds to a SCRATCH copy only.

Reads the shared corpus/fixtures/measure_audio.py (read-only), applies the
four queued folds by exact-string replacement (each replacement asserted to
occur exactly once / exactly twice as declared), writes
measure_audio-folded.py next to this file, py_compiles it, and reports
which top-level functions changed at AST level.  The shared tree is never
written.

Prints fold-apply.json to stdout and writes it next to this file.
"""
import ast
import json
import py_compile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED = HERE.parents[2] / "corpus" / "fixtures" / "measure_audio.py"
src = SHARED.read_text()
orig = src
OUT = {"folds": [], "shared_sha_before": None, "shared_sha_after": None}

# ---------------------------------------------------------------- F1
# (C fixture) -- handled in r95jack-nortprio.c, not here.
OUT["folds"].append({
    "id": "F1", "target": "corpus/fixtures/r95jack.c",
    "kind": "dead mode deletion (rtprio)",
    "note": "scratch copy r95jack-nortprio.c; build + dispatch proven",
})

# ---------------------------------------------------------------- F2
F2_A = '''            entry.setdefault("unloads", {})[JACK_R95_NS] = \\
                _pactlmon_r85_unload_own(
                    leaf.get("module_id"), "sink_name", JACK_R95_NS)
            loads = {}
            sinks_now = _capture_r77_sink_names_strict()
            entry["ns_gone_after_unload"] = (
                None if sinks_now is None else JACK_R95_NS not in sinks_now)
            if entry["ns_gone_after_unload"] is False:
                failures.append(
                    f"s_shape: probe sink {JACK_R95_NS} survived the "
                    "name-verified unload")
'''
F2_A_NEW = '''            _jack_r95_unload_ns(entry, failures, leaf, "s_shape")
            loads = {}
'''
F2_B = F2_A.replace('f"s_shape: ', 'f"b_jack2pw: ')
F2_B_NEW = '''            _jack_r95_unload_ns(entry, failures, leaf, "b_jack2pw")
            loads = {}
'''
F2_HELPER = '''def _jack_r95_unload_ns(entry, failures, leaf, label):
    """Name-verified mid-run unload of the driver sink + its residue law
    (ONE authority for the two entries that unload it between legs)."""
    entry.setdefault("unloads", {})[JACK_R95_NS] = \\
        _pactlmon_r85_unload_own(
            leaf.get("module_id"), "sink_name", JACK_R95_NS)
    sinks_now = _capture_r77_sink_names_strict()
    entry["ns_gone_after_unload"] = (
        None if sinks_now is None else JACK_R95_NS not in sinks_now)
    if entry["ns_gone_after_unload"] is False:
        failures.append(
            f"{label}: probe sink {JACK_R95_NS} survived the "
            "name-verified unload")


'''
for name, needle, repl, want in (("F2/A", F2_A, F2_A_NEW, 1),
                                 ("F2/B", F2_B, F2_B_NEW, 1)):
    got = src.count(needle)
    assert got == want, f"{name}: {got} != {want}"
    src = src.replace(needle, repl)
anchor = "def _jack_r95_block(entry, failures, msg, loads=None, procs=()):\n"
assert src.count(anchor) == 1
src = src.replace(anchor, F2_HELPER + anchor)
OUT["folds"].append({"id": "F2", "kind": "duplicate block -> one helper",
                     "sites": 2, "replacement": "call site + helper"})

# ---------------------------------------------------------------- F3
F3 = '                if dst != conns_want[0] if conns_want else False:\n'
F3_NEW = '                if conns_want and dst != conns_want[0]:\n'
assert src.count(F3) == 1
src = src.replace(F3, F3_NEW)
OUT["folds"].append({"id": "F3", "kind": "redundant conditional",
                     "sites": 1})

# ---------------------------------------------------------------- F4
F4 = '''            if not l.get("killed_at_bound"):
                _jack_r95_band(failures, "d_xrun_stall", "stall_cycles",
                               j.get("stall_cycles"), 4, 100000)
                _jack_r95_band(failures, "d_xrun_stall", "cb",
                               j.get("cb"), 10, 100000)
                _jack_r95_band(failures, "d_xrun_stall", "xrun_cbs",
                               j.get("xrun_cbs"), 0, 1)
'''
F4_NEW = ''
assert src.count(F4) == 1
src = src.replace(F4, F4_NEW)
F4_ELSE = '''            else:
                _jack_r95_eq(failures, "d_xrun_stall", "rc",
                             l.get("exit_code"), 0)
'''
F4_ELSE_NEW = '''            else:
                _jack_r95_eq(failures, "d_xrun_stall", "rc",
                             l.get("exit_code"), 0)
                _jack_r95_band(failures, "d_xrun_stall", "stall_cycles",
                               j.get("stall_cycles"), 4, 100000)
                _jack_r95_band(failures, "d_xrun_stall", "cb",
                               j.get("cb"), 10, 100000)
                _jack_r95_band(failures, "d_xrun_stall", "xrun_cbs",
                               j.get("xrun_cbs"), 0, 1)
'''
assert src.count(F4_ELSE) == 1
src = src.replace(F4_ELSE, F4_ELSE_NEW)
OUT["folds"].append({"id": "F4", "kind": "double test of one condition",
                     "sites": 1})

# ---------------------------------------------------------------- F5
F5 = '    rec["row_count"] = len(rows)\n'
assert src.count(F5) == 1
src = src.replace(F5, '')
OUT["folds"].append({"id": "F5", "kind": "dead computation (no reader)",
                     "sites": 1})

# ---------------------------------------------------------------- F6
F6 = '    ("jack_r95_no_daemon", r"Could not connect to JACK server"),\n'
assert src.count(F6) == 1
src = src.replace(F6, '')
OUT["folds"].append({"id": "F6", "kind": "dead error class (no emitter)",
                     "sites": 1})

folded = HERE / "measure_audio-folded.py"
folded.write_text(src)
py_compile.compile(str(folded), cfile=str(HERE / "measure_audio-folded.pyc"),
                   doraise=True)
OUT["folded_compiles"] = True
OUT["line_delta"] = len(src.split("\n")) - len(orig.split("\n"))

# which top-level defs changed?
def defs(text):
    t = ast.parse(text)
    return {n.name: ast.dump(n) for n in t.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

a, b = defs(orig), defs(src)
changed = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
OUT["changed_top_level_defs"] = changed
OUT["added_defs"] = sorted(set(b) - set(a))
OUT["removed_defs"] = sorted(set(a) - set(b))
# module-level constants changed?
ca = [ast.dump(n) for n in ast.parse(orig).body if isinstance(n, ast.Assign)]
cb = [ast.dump(n) for n in ast.parse(src).body if isinstance(n, ast.Assign)]
OUT["module_level_assign_delta"] = len(cb) - len(ca)

(HERE / "fold-apply.json").write_text(json.dumps(OUT, indent=2, sort_keys=True) + "\n")
print(json.dumps(OUT, indent=2, sort_keys=True))
