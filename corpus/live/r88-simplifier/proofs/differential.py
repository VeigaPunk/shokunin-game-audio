#!/usr/bin/env python3
"""r88 simplifier — executed differential suite (D1..D6): load the pinned
blob and the folded copy as modules (no bytecode writes, no live audio)
and compare the folded surfaces under stubs. Writes nothing."""
import importlib.util
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
FAIL = []
RESULTS = []


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


base = load("r88simp_base", os.path.join(HERE, "base-measure_audio.py"))
fold = load("r88simp_folded", os.path.join(HERE, "folded", "measure_audio.py"))


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        FAIL.append(name)


# ================= D1: runner (dead env/stdin_data) ======================
class FakeProc:
    def __init__(self, argv, kwargs, rec, mode):
        self.argv, self.kwargs, self.rec, self.mode = argv, kwargs, rec, mode
        self.pid = 424242
        self.returncode = -9 if mode == "timeout" else 0
        self._first = True

    def communicate(self, *a, **kw):
        self.rec["comm_kwargs"].append(
            {"input": kw.get("input", None), "timeout": kw.get("timeout")})
        if self.mode == "timeout" and self._first:
            self._first = False
            raise subprocess.TimeoutExpired(self.argv, kw.get("timeout"))
        return (b"stdout-line\n", b"stderr-line\n")


def run_case(mod, mode, **kw):
    rec = {"popen_kwargs": [], "comm_kwargs": []}

    def fake_popen(argv, **kwargs):
        rec["popen_kwargs"].append(
            {"stdin": kwargs.get("stdin"),
             "env": kwargs.get("env"),
             "start_new_session": kwargs.get("start_new_session")})
        return FakeProc(argv, kwargs, rec, mode)

    real_popen = mod.subprocess.Popen
    real_killpg = os.killpg
    real_sleep = time.sleep
    mod.subprocess.Popen = fake_popen
    os.killpg = lambda *a, **k: None
    time.sleep = lambda *a, **k: None
    try:
        out = mod._btwit_r88_run(["echo", "hi"], 1.0, **kw)
    finally:
        mod.subprocess.Popen = real_popen
        os.killpg = real_killpg
        time.sleep = real_sleep
    return out, rec


for mode in ("normal", "timeout"):
    rb, cb = run_case(base, mode)
    rf, cf = run_case(fold, mode)
    rb.pop("wall_s", None), rf.pop("wall_s", None)
    check(f"D1[{mode}] rec identical base vs folded (wall_s excluded)",
          rb == rf, "" if rb == rf else f"\n  base={rb}\n  fold={rf}")
    check(f"D1[{mode}] Popen stdin/env/start_new_session identical",
          cb["popen_kwargs"] == cf["popen_kwargs"],
          f"{cb['popen_kwargs']}")
    check(f"D1[{mode}] Popen got stdin=DEVNULL and env=None on both",
          all(k["stdin"] == subprocess.DEVNULL and k["env"] is None and
              k["start_new_session"] is True
              for k in cb["popen_kwargs"] + cf["popen_kwargs"]))
    check(f"D1[{mode}] normalized communicate kwargs identical",
          cb["comm_kwargs"] == cf["comm_kwargs"],
          f"base={cb['comm_kwargs']} fold={cf['comm_kwargs']}")
rb, _ = run_case(base, "normal", keep_chars=300, keep_raw=True)
rf, _ = run_case(fold, "normal", keep_chars=300, keep_raw=True)
rb.pop("wall_s", None), rf.pop("wall_s", None)
check("D1[raw] keep_raw/keep_chars rec identical",
      rb == rf and "stdout_raw" in rb)

# ================= D2: teardown guards ==================================
NS = "r88a_ns_TEST"
LEAF = {"module_id": 4242, "rc": 0, "field": "sink_name", "value": NS,
        "sink_seen": True, "monitor_seen": True}


def td_scenario(mod, loads, graph, sinks_now, names):
    calls = {"unload": [], "cli": []}

    def unload(mid, field, value):
        calls["unload"].append((mid, field, value))
        return {"verified_index": 1, "captured": mid, "field": field,
                "value": value}

    def cli(*args, **kw):
        calls["cli"].append((args, kw))
        return {"exit_code": 0}

    orig = {k: getattr(mod, k) for k in
            ("_pactlmon_r85_graph", "_capture_r77_sink_names_strict",
             "_playback_r78_node_names", "_pactlmon_r85_unload_own",
             "_btwit_r88_cli")}
    real_sleep = time.sleep
    mod._pactlmon_r85_graph = lambda: graph
    mod._capture_r77_sink_names_strict = lambda: sinks_now
    mod._playback_r78_node_names = lambda: names
    mod._pactlmon_r85_unload_own = unload
    mod._btwit_r88_cli = cli
    time.sleep = lambda *a, **k: None
    try:
        entry, failures = {}, []
        mod._btwit_r88_teardown(entry, failures, loads)
    finally:
        for k, v in orig.items():
            setattr(mod, k, v)
        time.sleep = real_sleep
    return entry, failures, calls


G = {"nodes": {5: {"name": "foreign"}, 7: {"name": f"r88a_{base.BTWIT_R88_PID}_x"},
               9: {"name": NS}}}
TD_CASES = [
    ("empty", {}, {"nodes": {}}, set(), []),
    ("one-leaf", {NS: LEAF}, {"nodes": {}}, {"foreign"}, []),
    ("residual-destroy", {NS: {**LEAF, "module_id": None}},
     {"nodes": {7: {"name": f"r88a_{base.BTWIT_R88_PID}_z"}}}, set(), []),
    ("reader-error-sinks", {NS: LEAF}, {"nodes": {}}, None, []),
    ("reader-error-nodes", {NS: LEAF}, {"nodes": {}}, {NS}, None),
    ("foreign+own", {NS: LEAF}, G, {NS}, ["foreign", NS]),
]
for name, loads, graph, sinks_now, names in TD_CASES:
    eb, fb, cb = td_scenario(base, loads, graph, sinks_now, names)
    ef, ff, cf = td_scenario(fold, loads, graph, sinks_now, names)
    check(f"D2[{name}] entry identical", eb == ef,
          "" if eb == ef else f"\n  base={eb}\n  fold={ef}")
    check(f"D2[{name}] failures identical", fb == ff)
    check(f"D2[{name}] unload/cli calls identical",
          cb == cf, f"base={cb} fold={cf}")

# out-of-domain disclosure: a leaf that never came from _btwit_r88_load_ns
ob, of_ = {}, {}
tb, _fb, cb = td_scenario(base, {NS: {"module_id": 1}}, {"nodes": {}},
                          set(), [])
try:
    ef, ff, cf = td_scenario(fold, {NS: {"module_id": 1}}, {"nodes": {}},
                             set(), [])
    of_ = {"entry": ef, "failures": ff, "calls": cf}
except KeyError as exc:
    of_ = {"KeyError": str(exc)}
check("D2[out-of-domain] disclosed divergence recorded (unreachable)",
      cb["unload"] == [(1, "sink_name", NS)] and
      "KeyError" in of_, f"base={cb['unload']} fold={of_}")

# ================= D3: block guard ======================================
def blk_case(mod, loads):
    calls = []

    def unload(mid, field, value):
        calls.append((mid, field, value))
        return {"verified_index": 1}

    orig = mod._pactlmon_r85_unload_own
    mod._pactlmon_r85_unload_own = unload
    try:
        entry, failures = {}, []
        out = mod._btwit_r88_block(entry, failures, "blocked-msg", loads)
    finally:
        mod._pactlmon_r85_unload_own = orig
    return out, failures, calls


for name, loads in (("none", None), ("empty", {}), ("leaf", {NS: LEAF}),
                    ("mid-none", {NS: {**LEAF, "module_id": None}})):
    ob, fbb, cb = blk_case(base, loads)
    of_, fbf, cf = blk_case(fold, loads)
    check(f"D3[{name}] entry identical", ob == of_,
          "" if ob == of_ else f"\n  base={ob}\n  fold={of_}")
    check(f"D3[{name}] failures identical", fbb == fbf)
    check(f"D3[{name}] unload calls identical", cb == cf, f"{cb} vs {cf}")

try:
    of_ = blk_case(fold, {NS: {"module_id": 1}})
    od = "no-divergence"
except KeyError as exc:
    od = f"KeyError {exc}"
check("D3[out-of-domain] disclosed divergence recorded (unreachable)",
      od.startswith("KeyError"), od)

# ================= D4: _frames_cache pops are no-ops ====================
FRAME1 = ("S   ID  QUANT   RATE    WAIT    BUSY   W/Q   B/Q  ERR FORMAT"
          "           NAME\n"
          "C   12   1024  48000   0.0us   0.0us  0.00  0.00    0  S16LE"
          "           r88a_ns_TEST\n")
FRAME2 = ("S   ID  QUANT   RATE    WAIT    BUSY   W/Q   B/Q  ERR FORMAT"
          "           NAME\n"
          "S   12   1024  48000   0.0us   0.0us  0.00  0.00    0  S16LE"
          "           r88a_ns_TEST\n"
          "I   13   1024  48000   0.0us   0.0us  0.00  0.00    0  S16LE"
          "           foreign\n")


def top_case(mod, texts):
    seq = {"i": 0, "calls": 0}

    def fake_run(argv, timeout_s, **kw):
        seq["calls"] += 1
        txt = texts[min(seq["i"], len(texts) - 1)]
        seq["i"] += 1
        return {"argv": " ".join(argv), "exit_code": 0, "signal": None,
                "killed_at_bound": False, "wall_s": 0.01,
                "stdout_head": txt.splitlines()[:1], "stdout": txt[:300],
                "stdout_bytes": len(txt), "stderr_head": [], "stderr": "",
                "stderr_bytes": 0, "error_class": None, "error_hit": None,
                "stdout_raw": txt, "stderr_raw": ""}

    orig = mod._btwit_r88_run
    mod._btwit_r88_run = fake_run
    try:
        rec, frames = mod._btwit_r88_top_until(3, 2, bound_s=20.0, tries=3)
    finally:
        mod._btwit_r88_run = orig
    return rec, frames, seq["calls"]


for name, texts in (("one-shot", [FRAME1 + FRAME2]),
                    ("retry", [FRAME1, FRAME1 + FRAME2])):
    rb, fb_, nb = top_case(base, texts)
    rf, ff, nf = top_case(fold, texts)
    rb.pop("wall_s", None), rf.pop("wall_s", None)
    check(f"D4[{name}] rec identical (wall_s excluded)", rb == rf,
          "" if rb == rf else f"\n  base={rb}\n  fold={rf}")
    check(f"D4[{name}] frames identical and attempts equal",
          fb_ == ff and nb == nf, f"base={nb} fold={nf}")
    check(f"D4[{name}] _frames_cache absent from the returned rec",
          "_frames_cache" not in rb and "_frames_cache" not in rf)
    # the folded statement is a no-op: pop vs no-pop leave the dict equal
    pop_applied = dict(rb)
    pop_applied.pop("_frames_cache", None)
    check(f"D4[{name}] pop(no-key) leaves the dict byte-equal to no-pop",
          pop_applied == rf)

# ================= D5: load_ns leaf carries field/value =================
def leaf_case(mod):
    orig = mod._pwcat_r83_ns_load
    mod._pwcat_r83_ns_load = lambda nm, extra_args=(): {
        "module_id": 777, "rc": 0}
    try:
        leaf = mod._btwit_r88_load_ns("r88a_ns_D5")
    finally:
        mod._pwcat_r83_ns_load = orig
    return leaf


lb, lf = leaf_case(base), leaf_case(fold)
check("D5 leaf field/value identical", lb == lf and
      lb["field"] == "sink_name" and lb["value"] == "r88a_ns_D5", f"{lb}")

# ================= D6: unused loop var / .values() ======================
def residue_case(mod, folded_slice):
    mod._pactlmon_r85_graph = lambda: {
        "nodes": {5: {"name": "foreign"},
                  7: {"name": f"{mod.BTWIT_R88_PREFIX}_bz_create_a2dpsink"},
                  9: {"name": f"{mod.BTWIT_R88_PREFIX}_other"},
                  11: {"name": "r88a_999_bz_create_x"}}}
    env = dict(mod.__dict__)
    exec(compile(folded_slice, "<slice>", "exec"), env)
    return env["legs"]["bz_own_residue"]


base_slice = """legs = {}
g2 = _pactlmon_r85_graph()
legs["bz_own_residue"] = sorted(
    n.get("name") for nid, n in
    (g2.get("nodes") or {}).items()
    if n.get("name") and
    f"{BTWIT_R88_PREFIX}_bz_create" in n["name"])
"""
fold_slice = """legs = {}
g2 = _pactlmon_r85_graph()
legs["bz_own_residue"] = sorted(
    n.get("name") for n in
    (g2.get("nodes") or {}).values()
    if n.get("name") and
    f"{BTWIT_R88_PREFIX}_bz_create" in n["name"])
"""
res_b = residue_case(base, base_slice)
res_f = residue_case(fold, fold_slice)
check("D6 bz_own_residue identical (own-prefixed only, foreign excluded)",
      res_b == res_f and len(res_b) == 1 and "bz_create" in res_b[0],
      f"{res_b}")

print()
print(f"DIFFERENTIAL: {'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
sys.exit(1 if FAIL else 0)
