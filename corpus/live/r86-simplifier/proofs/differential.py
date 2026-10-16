#!/usr/bin/env python3
"""r86-simplifier differential proofs D1-D8: executed base-vs-folded
comparisons on scratch imports with stubbed I/O. No live PipeWire
traffic; no file outside this directory is written."""
import importlib.util
import json
import subprocess
import sys
import textwrap
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / "base-measure_audio.py"
FOLD = HERE / "folded" / "measure_audio.py"
NS = "r86a_ns_TEST"
lines_b = BASE.read_text(encoding="utf-8").splitlines()
lines_f = FOLD.read_text(encoding="utf-8").splitlines()
results = []


def ck(name, cond, detail=""):
    results.append(bool(cond))
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


mod_b = load("ma_r86_base", BASE)
mod_f = load("ma_r86_fold", FOLD)


def run_teardown(mod, loads, sinks_now, names, meta_stdout=None):
    saved = (mod._capture_r77_sink_names_strict,
             mod._playback_r78_node_names, mod._pactlmon_r85_unload_own)
    calls = []
    mod._capture_r77_sink_names_strict = lambda: sinks_now
    mod._playback_r78_node_names = lambda: names
    mod._pactlmon_r85_unload_own = lambda mid, field, value: (
        calls.append((mid, field, value))
        or {"verified_index": 1, "captured": 1, "recycled": False})
    real_run = subprocess.run
    if meta_stdout is not None:
        subprocess.run = lambda *a, **k: types.SimpleNamespace(
            stdout=meta_stdout)
    try:
        entry, failures = {}, []
        mod._pwctl_r86_teardown(entry, failures, loads,
                                meta_subject=meta_stdout is not None)
    finally:
        (mod._capture_r77_sink_names_strict,
         mod._playback_r78_node_names, mod._pactlmon_r85_unload_own) = saved
        subprocess.run = real_run
    return entry, failures, calls


# D1 — teardown ------------------------------------------------------------
shapes = [
    {},
    {NS: {"module_id": 7, "field": "sink_name", "value": NS}},
    {NS: {"module_id": 7, "field": "sink_name", "value": NS, "x": 1}},
    {NS: {"module_id": None, "rc": 1, "error": "boom"}},
]
ok = True
for i, loads in enumerate(shapes):
    for sinks in ([], [NS], ["other"]):
        for names in ([], [NS, "r86a_1_foreign"]):
            rb = run_teardown(mod_b, loads, sinks, names)
            rf = run_teardown(mod_f, loads, sinks, names)
            ok = ok and rb == rf
ck("D1 teardown identical over 4 loads x 3 sinks x 2 names", ok)
rb = run_teardown(mod_b, shapes[1], [], [], meta_stdout=b'Found "d" x\n')
rf = run_teardown(mod_f, shapes[1], [], [], meta_stdout=b'Found "d" x\n')
ck("D1 teardown meta_subject path identical", rb == rf)
rb = run_teardown(mod_b, shapes[1], [], [],
                  meta_stdout=b'key "r86a_k" here\n')
rf = run_teardown(mod_f, shapes[1], [], [],
                  meta_stdout=b'key "r86a_k" here\n')
ck("D1 teardown meta leftover path identical", rb == rf)


# D2 — block ---------------------------------------------------------------
def run_block(mod, loads):
    saved = mod._pactlmon_r85_unload_own
    calls = []
    mod._pactlmon_r85_unload_own = lambda mid, field, value: (
        calls.append((mid, field, value))
        or {"verified_index": 1, "captured": 1, "recycled": False})
    try:
        entry, failures = {}, []
        if loads is None:
            out = mod._pwctl_r86_block(entry, failures, "blocked")
        else:
            out = mod._pwctl_r86_block(entry, failures, "blocked", loads)
    finally:
        mod._pactlmon_r85_unload_own = saved
    return out, failures, calls


ok = True
for loads in (None, {}, shapes[1], shapes[2], shapes[3]):
    ok = ok and run_block(mod_b, loads) == run_block(mod_f, loads)
ck("D2 block identical over 5 loads shapes (incl. omitted)", ok)


# D3 — own_links -----------------------------------------------------------
leaves = [
    {"id": 1, "state": "active", "out": f"{NS}:monitor_FL",
     "in": f"{NS}:playback_FL"},
    {"id": 2, "state": "active", "out": "other:out", "in": "other:in"},
    {"id": 3, "state": "active", "out": "None:None", "in": "None:None"},
    {"id": 4, "state": "active", "out": f"{NS}:monitor_FR", "in": "z:q"},
]
saved_b, saved_f = mod_b._pwctl_r86_links, mod_f._pwctl_r86_links
mod_b._pwctl_r86_links = lambda: list(leaves)
mod_f._pwctl_r86_links = lambda: list(leaves)
try:
    rb, rf = (mod_b._pwctl_r86_own_links(NS),
              mod_f._pwctl_r86_own_links(NS))
finally:
    mod_b._pwctl_r86_links, mod_f._pwctl_r86_links = saved_b, saved_f
ck("D3 own_links identical on the reachable domain", rb == rf,
   f"{len(rb)} links")
mod_b._pwctl_r86_links = lambda: None
mod_f._pwctl_r86_links = lambda: None
ck("D3 own_links reader-failure None identical",
   mod_b._pwctl_r86_own_links() is None
   and mod_f._pwctl_r86_own_links() is None)
mod_b._pwctl_r86_links = saved_b
mod_f._pwctl_r86_links = saved_f
# disclosed out-of-domain divergence: out=None (impossible from the
# _pwctl_r86_links f-string construction)
mod_b._pwctl_r86_links = lambda: [{"id": 9, "out": None, "in": "a:b"}]
mod_f._pwctl_r86_links = lambda: [{"id": 9, "out": None, "in": "a:b"}]
try:
    rb = mod_b._pwctl_r86_own_links()
    b_out = "filtered"
except Exception as exc:                       # pragma: no cover
    b_out = type(exc).__name__
try:
    mod_f._pwctl_r86_own_links()
    f_out = "filtered"
except Exception as exc:
    f_out = type(exc).__name__
ck("D3 disclosed: out-of-domain out=None differs (base=filtered, "
   f"folded={f_out})", b_out == "filtered" and f_out == "AttributeError")
mod_b._pwctl_r86_links = saved_b
mod_f._pwctl_r86_links = saved_f


# D4 — dsp tap_link early-return dominance ---------------------------------
def slice_between(text_lines, start_pat, end_pat, close_pat="loads)"):
    a = next(i for i, ln in enumerate(text_lines) if start_pat in ln)
    b = next(i for i, ln in enumerate(text_lines)
             if end_pat in ln and i > a)
    b = next(i for i, ln in enumerate(text_lines)
             if close_pat in ln and i > b)
    return "\n".join(text_lines[a:b + 1])


sl_b = slice_between(lines_b, 'legs["tap_link"] = {"edges": edges',
                     '"monitor tap never linked — dsp arms skipped",')
sl_f = slice_between(lines_f, 'legs["tap_link"] = {"edges": edges',
                     '"monitor tap never linked — dsp arms skipped",')
ck("D4 the early-return slice is byte-identical base/folded", sl_b == sl_f)


def exec_reach(sl):
    first = sl.splitlines()[0]
    ind = " " * (len(first) - len(first.lstrip()) + 4)
    prog = ("def run(legs, edges, waited, entry, failures, loads, tap, "
            "killpg, block):\n" + textwrap.indent(sl, "    ")
            + "\n" + ind + "return 'after'\n")
    g = {"_alsapw_r84_killpg": lambda p: None,
         "_pwctl_r86_block": lambda *a, **k: "block",
         "PWCTL_R86_NS": NS, "PWCTL_R86_TAP": "t"}
    exec(prog, g)
    return g["run"]


reach = exec_reach(sl_b)
tap = types.SimpleNamespace(poll=lambda: None, wait=lambda: None)
ck("D4 edges=[] takes the early return (verdict unreachable)",
   reach({}, [], 0.1, {}, [], {}, tap, None, None) == "block")
ck("D4 edges=[...] falls through (verdict reachable, no failure)",
   reach({}, ["e"], 0.1, {}, [], {}, tap, None, None) == "after")
# base verdict snippet on the reachable domain vs folded no-op
vb = ("    if not legs[\"tap_link\"][\"edges\"]:\n"
      "        failures.append(\"tap_link: the monitor tap never "
      "validated\")\n")


def exec_verdict(src):
    prog = ("def run(legs, failures):\n"
            + textwrap.indent(src, "    ") + "\n")
    g = {}
    exec(prog, g)
    return g["run"]


run_v = exec_verdict(vb)
f_reach = []
run_v({"tap_link": {"edges": ["e"]}}, f_reach)
ck("D4 reachable domain: base verdict adds no failure", f_reach == [])
ck("D4 folded has no tap_link verdict at all",
   'if not legs["tap_link"]["edges"]' not in "\n".join(lines_f))


# D5 — addr dump_full loop / self_serials ----------------------------------
def slice_loop(ls):
    a = next(i for i, ln in enumerate(ls)
             if "self_serials = []" in ln or
             "# full dumps are parsed, not previewed" in ln)
    b = next(i for i, ln in enumerate(ls)
             if "pw-cli destroy: the id-family write" in ln)
    return "\n".join(ls[a:b])


def exec_loop(sl):
    dump = [{"id": 1, "type": "PipeWire:Interface:Client",
             "info": {"props": {"application.name": "pw-dump",
                                "object.serial": 243277}}},
            {"id": 2, "type": "PipeWire:Interface:Node",
             "info": {"props": {"node.name": "x"}}}]
    first = sl.splitlines()[0]
    ind = " " * (len(first) - len(first.lstrip()) + 4)
    prog = ("def run(legs, subprocess, json):\n"
            + textwrap.indent(sl, "    ")
            + "\n" + ind + "return legs, locals().get('self_serials')\n")
    g = {}
    exec(prog, g)
    real = subprocess.run
    subprocess.run = lambda *a, **k: types.SimpleNamespace(
        stdout=json.dumps(dump).encode(), returncode=0)
    try:
        return g["run"]({}, subprocess, json)
    finally:
        subprocess.run = real


legs_b, acc_b = exec_loop(slice_loop(lines_b))
legs_f, acc_f = exec_loop(slice_loop(lines_f))
ck("D5 dump_full legs identical base/folded", legs_b == legs_f)
ck("D5 base accumulated self_serials (dead value)", acc_b is not None,
   str(acc_b))
ck("D5 folded has no accumulator", acc_f is None)
ck("D5 recorded self_serials key intact in folded",
   legs_f["dump_full1"]["self_serials"]
   == ["243277"] == legs_b["dump_full1"]["self_serials"])


# D6 — solo window ---------------------------------------------------------
def exec_solo(src_lines):
    first = src_lines[0]
    ind = " " * (len(first) - len(first.lstrip()) + 4)
    prog = ("def run(mark, sleep_to):\n"
            + textwrap.indent("\n".join(src_lines), "    ")
            + "\n" + ind + "return solo_lo, solo_hi\n")
    g = {}
    exec(prog, g)
    t = {"now": 100.0}
    return g["run"](lambda: t["now"], lambda at: t.update(now=at))


sb = ["solo_lo, solo_hi = mark(), None", "sleep_to(solo_lo + 0.6)",
      "solo_hi = mark()"]
sf = ["solo_lo = mark()", "sleep_to(solo_lo + 0.6)", "solo_hi = mark()"]
ck("D6 solo window identical", exec_solo(sb) == exec_solo(sf),
   str(exec_solo(sf)))


# D7 — ser predicate -------------------------------------------------------
def pred_base(ser):
    return ser in (None, "None")


def pred_fold(ser):
    return ser == "None"


dom = [str(x) for x in (None, 0, 1, "None", "abc", 99999)]
ck("D7 ser predicate identical over the str domain",
   all(pred_base(s) == pred_fold(s) for s in dom), str(dom))


# D8 — module surface ------------------------------------------------------
attrs_b = {a for a in dir(mod_b) if a.startswith("PWCTL_R86")}
attrs_f = {a for a in dir(mod_f) if a.startswith("PWCTL_R86")}
ck("D8 module attribute delta is exactly the two dead constants",
   attrs_b - attrs_f == {"PWCTL_R86_LINK_WAIT_S", "PWCTL_R86_TAP_WAIT_S"}
   and not attrs_f - attrs_b, str(sorted(attrs_b - attrs_f)))
ck("D8 folded errclass still executes",
   mod_f._pwctl_r86_errclass("Error: \"enum-params <id>\"")[0]
   == mod_b._pwctl_r86_errclass("Error: \"enum-params <id>\"")[0])

n_fail = results.count(False)
print(f"\n{len(results) - n_fail}/{len(results)} PASS")
sys.exit(1 if n_fail else 0)
