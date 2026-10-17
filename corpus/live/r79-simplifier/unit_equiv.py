#!/usr/bin/env python3
"""Unit equivalence: control fixture vs folded candidate, on the arms the
healthy full probe cannot exercise, plus machine re-checks of the static
premises every fold rests on.

    python3 unit_equiv.py control/corpus/fixtures/measure_audio.py \
                         cand/corpus/fixtures/measure_audio.py
"""
import ast
import importlib.util
import sys
from pathlib import Path


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ctl_path, cand_path = sys.argv[1], sys.argv[2]
ctl = load(ctl_path, "ma_ctl")
cand = load(cand_path, "ma_cand")
ctl_src = Path(ctl_path).read_text()
cand_src = Path(cand_path).read_text()

FAILS = []


def check(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)


print("== 1. F13 check_tap: every arm, control vs candidate ==")
cases = [
    ("no tap key", {}, None),
    ("empty tap", {"tap": {}}, None),
    ("tap ran=False", {"tap": {"ran": False}}, None),
    ("tap bound elsewhere", {"tap": {"ran": True, "bound_to_target": False,
                                     "bound_producers": ["other"],
                                     "target": "sink_x",
                                     "windows": [{"at_s": 0}]}}, None),
    ("want_tone=True, silent", {"tap": {"ran": True, "bound_to_target": True,
                                        "bound_producers": ["sink_x"],
                                        "target": "sink_x",
                                        "windows": [{"at_s": 0}],
                                        "carries_tone": False}}, True),
    ("want_tone=False, mine", {"fed": False,
                               "tap": {"ran": True, "bound_to_target": True,
                                       "bound_producers": ["sink_x"],
                                       "target": "sink_x",
                                       "windows": [{"at_s": 0}],
                                       "mine_windows": 3,
                                       "peak_l": 100, "peak_r": 100}},
     False),
]
for label, leg, want_tone in cases:
    e1, e2, f1, f2 = {}, {}, [], []
    l1, l2 = dict(leg), dict(leg)
    ctl._loopback_r79_check_tap(e1, f1, "unit", l1, want_tone=want_tone)
    cand._loopback_r79_check_tap(e2, f2, "unit", l2, want_tone=want_tone)
    same = (f1 == f2 and e1 == e2 and
            {k: v for k, v in l1.items() if k == "confound"} ==
            {k: v for k, v in l2.items() if k == "confound"})
    check(same, f"check_tap arm [{label}]: failures={f1} confound="
                f"{l1.get('confound') is not None}")

# require= is never passed at any call site (kw-only, default True)
check("require=" not in ctl_src.replace("want_tone=None, require=True", ""),
      "no control call site passes require=")
check("require=" not in cand_src and "require:" not in cand_src,
      "candidate has no 'require' parameter left")

print("\n== 2. F14 union: helper vs the control's inline comprehension ==")


def inline_union(samples, node, key):
    # verbatim shape of the control's inline expression
    return sorted({n for s in samples
                   for n in (s["watch"].get(node) or {}).get(key) or []})


grid = [
    [],
    [{"watch": {}}],
    [{"watch": {"input.x": {}}}],
    [{"watch": {"input.x": {"producers": []}}}],
    [{"watch": {"input.x": {"producers": ["a"]}}}],
    [{"watch": {"input.x": {"producers": ["b", "a"]}}},
     {"watch": {"input.x": {"producers": ["a"]}}}],
    [{"watch": {"input.x": {"producers": None}}},
     {"watch": {"input.x": {"producers": ["c"]}}}],
]
ok = all(inline_union(g, "input.x", "producers") ==
         cand._loopback_r79_union(g, "input.x", "producers") for g in grid)
check(ok, f"union identical on {len(grid)} synthetic sample sets")

print("\n== 3. F16 block: inline control block vs candidate helper ==")
for msg in ("no default sink/source authority readable",
            "no default sink authority readable",
            "a probe null sink/monitor did not enumerate",
            "the probe null sink/monitor did not enumerate",
            "the fc null sink/monitor did not enumerate",
            "no shipped filter-chain.conf"):
    for with_loads in (False, True):
        ctl_calls, cand_calls = [], []
        ctl._loopback_r79_sinks_unload = lambda l: ctl_calls.append(l)
        cand._loopback_r79_sinks_unload = lambda l: cand_calls.append(l)
        loads = {"sink_a": {"module_id": 7}}
        e1, f1 = {}, []
        # control inline block, verbatim statement order
        e1["blocked"] = msg
        e1["coverage_blocked"] = [e1["blocked"]]
        if with_loads:
            ctl._loopback_r79_sinks_unload(loads)
        e1["failures"] = f1
        r1 = e1
        e2, f2 = {}, []
        r2 = cand._loopback_r79_block(
            e2, f2, msg, loads if with_loads else None)
        want = 1 if with_loads else 0
        check(r1 == r2 and f1 == f2 and len(ctl_calls) == want and
              len(cand_calls) == want and
              (not with_loads or ctl_calls == cand_calls),
              f"block [{msg[:34]}…] loads={with_loads}: entry equal, "
              f"unload calls ctl={len(ctl_calls)} cand={len(cand_calls)}")

print("\n== 4. static premises (machine re-checked on the control source) ==")
tree = ast.parse(ctl_src)


def count_name(src, name, ctx):
    n = 0
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Name) and node.id == name and \
                isinstance(node.ctx, ctx):
            n += 1
    return n


check(ctl_src.count("LOOPBACK_R79_TIMEOUT_S") == 1 and
      cand_src.count("LOOPBACK_R79_TIMEOUT_S") == 0,
      "F1 LOOPBACK_R79_TIMEOUT_S: 1 ref in control (its def), 0 in cand")

# extra_tw / want_node / ltag / inv / ctx: stored-but-never-loaded premises
def dead_locals(src, func):
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == func:
            loads, stores = {}, {}
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name):
                    (stores if isinstance(sub.ctx, ast.Store) else loads
                     ).setdefault(sub.id, 0)
                    if isinstance(sub.ctx, ast.Load):
                        loads[sub.id] = loads.get(sub.id, 0) + 1
            return {k for k in stores if loads.get(k, 0) == 0}
    return None


check("extra_tw" in dead_locals(ctl_src, "loopback_playback_lattice_r79_entry"),
      "F6 extra_tw is store-only in the control")
check("inv" in dead_locals(ctl_src, "loopback_matrix_r79_entry") and
      "inv" in dead_locals(ctl_src, "filterchain_module_r79_entry"),
      "F7/F8 inv is store-only in the matrix and fc entries")
check("ctx" in dead_locals(ctl_src, "filterchain_module_r79_entry"),
      "F9 ctx is store-only in the fc entry")
check("want_node" in dead_locals(ctl_src, "filterchain_module_r79_entry"),
      "F10 want_node is store-only in the fc entry")
check("ltag" in dead_locals(ctl_src, "loopback_hotplug_r79_entry"),
      "F11 ltag is store-only in the hotplug entry")
check("line" in dead_locals(ctl_src, "_loopback_r79_run"),
      "F2 line is store-only in the r79 runner")

# s0 single-assignment in the capture entry
cap = ctl_src[ctl_src.index("def loopback_capture_lattice_r79_entry"):
              ctl_src.index("def loopback_playback_lattice_r79_entry")]
check(cap.count("s0 = ora0[") == 1 and "and s0 is None" in cap,
      "F5 s0 is assigned once in the capture entry (so `s0 is None` at "
      "the leg loop is False)")

# RECS table identity: the 4 element lines appear twice, verbatim
recs_lines = [l.strip() for l in ctl_src.splitlines()
              if l.strip().startswith('("d2')]
norm = [l.replace(")):", "),") for l in recs_lines]
check(len(norm) == 8 and norm[:4] == norm[4:],
      "F12 the verdict loop's re-declared table equals RECS verbatim "
      "(4 lines, twice)")

# tap_t ternary vacuity
check('tap_t = ns_b if kind != "none" else ns_b' in ctl_src,
      "F4 tap_t ternary has identical arms in the control")

# doc claims vs code
check("latency_param_verdict" in ctl_src and
      "latency_param_verdict" in cand_src and
      "byte-identical\n    on every leg" not in cand_src and
      "byte-identical on\n#     every leg" not in cand_src and
      "RECORDED as a" in cand_src,
      "F15 the code computes a tracks-request verdict in both; both stale "
      "byte-identical claims are gone from the candidate")

print("\nUNIT VERDICT:", "PASS" if not FAILS else f"FAIL {FAILS}")
sys.exit(1 if FAILS else 0)
