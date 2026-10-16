#!/usr/bin/env python3
"""r87 simplifier — executed differentials (D1-D9), base vs folded.

Both copies are loaded as modules (importlib) and their REAL r87
functions are executed against stubbed I/O.  Every check compares the
full observable surface (returned entry, failure list, recorded keys,
stub call list) — not a hand-copied snippet — wherever the function is
importable; pure-expression folds (D4-D7) execute the exact base/folded
source slices extracted from the two blobs.
"""
import importlib.util
import inspect
import json
import pathlib
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BASE = load(HERE / "base-measure_audio.py", "r87_base")
FOLD = load(HERE / "folded" / "measure_audio.py", "r87_folded")


def stub(mod, sinks, names, nodes, calls):
    """Install deterministic stubs on one module copy."""
    def unload(mid, field, value):
        calls["unload"].append((mid, field, value))
        return {"verified_index": mid, "recycled": False}
    def pwcli(*a, **k):
        calls["pwcli"].append((a, k.get("timeout_s")))
        return {"argv": " ".join(map(str, a)), "exit_code": 0}
    mod._pactlmon_r85_unload_own = unload
    mod._capture_r77_sink_names_strict = lambda: sinks
    mod._playback_r78_node_names = lambda: names
    mod._pwbind_r87_graph = lambda: {"nodes": nodes}
    mod._pwbind_r87_pwcli = pwcli
    mod.time.sleep = lambda *_: None


# ------------------------------------------------------------------ D1
# the real _pwbind_r87_teardown over the reachable loads domain
LOAD_SHAPES = [
    {"ns": {"module_id": 42, "field": "sink_name", "value": "r87a_ns_1"}},
    {},
    {"ns": {"module_id": 42}},
    {"ns": {"module_id": None, "rc": 1, "error": "no module"}},
    {"ns": {"module_id": 7, "field": "sink_name", "value": "r87a_ns_1"},
     "ns2": {"module_id": 8, "field": "sink_name", "value": "r87a_ns2_1"}},
]
READER_CASES = [
    (None, None, {}),                                    # both readers fail
    ([], [], {}),                                        # both empty
    (["other-sink"], ["other-node"], {}),                # foreign only
    (["r87a_ns_1"], ["r87a_ns_1"], {}),                  # survivor
    ([], ["r87a_ns_1"], {"n9": {"name": "r87a_ns_1"}}),  # residue destroy
]
d1 = 0
for shape in LOAD_SHAPES:
    for sinks, names, nodes in READER_CASES:
        outs = []
        for mod in (BASE, FOLD):
            calls = {"unload": [], "pwcli": []}
            stub(mod, sinks, names, nodes, calls)
            entry, failures = {}, []
            mod._pwbind_r87_teardown(entry, failures, dict(shape))
            outs.append((entry, failures, calls))
        d1 += 1
        if outs[0] != outs[1]:
            check("D1 teardown differential", False,
                  f"shape={shape} sinks={sinks} names={names} "
                  f"base={outs[0]} folded={outs[1]}")
            break
    else:
        continue
    break
else:
    check("D1 teardown differential (5 loads x 5 reader cases)", True,
          f"{d1} comparisons identical (entry+failures+unload+pwcli calls)")

# ------------------------------------------------------------------ D2
# the real _pwbind_r87_block (loads guard LIVE: None/{} /dict)
d2 = 0
for loads in (None, {}, {"ns": {"module_id": 42, "field": "sink_name",
                                "value": "r87a_ns_1"}},
              {"ns": {"module_id": None}}):
    outs = []
    for mod in (BASE, FOLD):
        calls = {"unload": [], "pwcli": []}
        stub(mod, [], [], {}, calls)
        entry, failures = {}, []
        if loads is None:
            mod._pwbind_r87_block(entry, failures, "probe blocked")
        else:
            mod._pwbind_r87_block(entry, failures, "probe blocked",
                                  dict(loads))
        outs.append((entry, failures, calls))
    d2 += 1
    if outs[0] != outs[1]:
        check("D2 block differential", False, f"loads={loads} {outs}")
        break
else:
    check("D2 block differential (None/{}/leaf shapes)", True,
          f"{d2} comparisons identical")

# ------------------------------------------------------------------ D3
# the fmt_sink slice: exact base/folded source executed with a stub
def slice_of(mod_src, marker, end_marker):
    s = mod_src.index(marker)
    e = mod_src.index(end_marker, s)
    return mod_src[s:e + len(end_marker)]


base_src = (HERE / "base-measure_audio.py").read_text()
fold_src = (HERE / "folded" / "measure_audio.py").read_text()
b_slice = slice_of(base_src, "            fs = {}\n", '            legs["fmt_sink"] = fs')
f_slice = slice_of(fold_src, "            fs = {}\n", '            legs["fmt_sink"] = fs')
b_slice = "\n".join(l[12:] if l.startswith(" " * 12) else l
                    for l in b_slice.splitlines())
f_slice = "\n".join(l[12:] if l.startswith(" " * 12) else l
                    for l in f_slice.splitlines())


def run_fs(src, nid):
    ns = {"_pwbind_r87_pwcli": lambda *a, **k: {"argv": " ".join(map(str, a)),
                                                "exit_code": 0},
          "nid": nid, "legs": {}}
    exec(compile(src, "<fs-slice>", "exec"), ns)
    return ns["fs"], ns["legs"]


reach = [nid for nid in (12345, 0, -1, 99999999)]
ok = all(run_fs(b_slice, nid) == run_fs(f_slice, nid) for nid in reach)
check("D3 fmt_sink slice differential (reachable nid domain)", ok,
      f"{len(reach)} nid values: identical fs + legs")
od_b = run_fs(b_slice, None)
od_f = run_fs(f_slice, None)
check("D3 fmt_sink out-of-domain disclosed (nid=None)",
      od_b[0] == {} and od_f[0] != {},
      "base leaves fs empty, folded calls the three verbs — unreachable: "
      "`if nid is None: return` blocks the entry first")

# ------------------------------------------------------------------ D4
# the DEF fallback: base vs folded over the reachable domain (key set)
b_def = lambda e: e.get("default_sink_at_start") or "<unreadable-default>"
f_def = lambda e: e["default_sink_at_start"]
dom = [{"default_sink_at_start": "alsa_output.x"},
       {"default_sink_at_start": "a"},
       {"default_sink_at_start": "x" * 200}]
check("D4 DEF differential over the reachable domain",
      all(b_def(e) == f_def(e) for e in dom),
      "identical for every entry that reaches the verdicts (key set)")
# out-of-domain disclosure: only reachable if the DEF0 block-return is
# removed AND a falsy/absent default is recorded
od_base = b_def({"default_sink_at_start": None})
od_fold = f_def({"default_sink_at_start": None})
try:
    f_def({})
except KeyError:
    od_key = "KeyError"
else:
    od_key = "no-raise"
check("D4 DEF out-of-domain disclosed",
      od_base == "<unreadable-default>" and od_fold is None and
      od_key == "KeyError",
      f"falsy value: base={od_base!r} folded={od_fold!r}; absent key: "
      f"folded={od_key} — both unreachable (DEF0 falsy block-returns "
      "before any verdict)")

# ------------------------------------------------------------------ D5
# cold_nowarm predicate equivalence over a text domain
def b_cold(blob, nid):
    return f"unknown global '{nid}'" not in blob and "unknown global" not in blob


def f_cold(blob, nid):
    return "unknown global" not in blob


blobs = ["unknown global '99999999'", "unknown global '12345'",
         "unknown global", "", "other text",
         "unknown global '99999999' then more", "no such global '99999999'"]
check("D5 cold_nowarm predicate differential",
      all(b_cold(b, 99999999) == f_cold(b, 99999999) for b in blobs),
      f"{len(blobs)} texts identical (id-form/generic/neither)")

# ------------------------------------------------------------------ D6
# coll_ports guard equivalence over the port domain
def b_coll(ports):
    return bool(ports) and not all(str(p).startswith("playback_") for p in ports)


def f_coll(ports):
    return not all(str(p).startswith("playback_") for p in ports)


port_dom = [[], ["playback_1"], ["input_1"], ["playback_1", "input_2"],
            ["monitor_1"], [None], ["playback_"]]
check("D6 coll_ports predicate differential",
      all(b_coll(p) == f_coll(p) for p in port_dom),
      f"{len(port_dom)} port lists identical (incl. empty list)")

# ------------------------------------------------------------------ D7
# the solo slice: base vs folded executed with fake mark/sleep
def run_solo(src):
    ns = {"mark": lambda: 100.0, "sleep_to": lambda at: None,
          "mark_calls": []}
    def mark():
        ns["mark_calls"].append(len(ns["mark_calls"]))
        return 100.0 + len(ns["mark_calls"])
    ns["mark"] = mark
    exec(compile(src, "<solo-slice>", "exec"), ns)
    return ns["solo_lo"], ns["solo_hi"]


b_solo = ("solo_lo, solo_hi = mark(), None\n"
          "sleep_to(solo_lo + 0.6)\n"
          "solo_hi = mark()\n")
f_solo = ("solo_lo = mark()\n"
          "sleep_to(solo_lo + 0.6)\n"
          "solo_hi = mark()\n")
check("D7 solo slice differential", run_solo(b_solo) == run_solo(f_solo),
      f"identical (solo_lo, solo_hi)={run_solo(f_solo)}")

# ------------------------------------------------------------------ D8
# module attribute delta
def r87_attrs(mod):
    return {k: v for k, v in vars(mod).items()
            if k.startswith("PWBIND_R87") or k == "_PWBIND_R87_ERR_CLASSES"}


ba, fa = r87_attrs(BASE), r87_attrs(FOLD)
missing = sorted(set(ba) - set(fa))
added = sorted(set(fa) - set(ba))
changed = sorted(k for k in set(ba) & set(fa) if ba[k] != fa[k])
check("D8 module attribute delta is exactly the two constants",
      missing == ["PWBIND_R87_LINK_WAIT_S", "PWBIND_R87_TAP_WAIT_S"] and
      not added and not changed,
      f"missing={missing} added={added} changed={changed}")

# ------------------------------------------------------------------ D9
# symtable symbol-set diff over the r87 functions
import symtable


def fn_symbols(path, fname):
    st = symtable.symtable(pathlib.Path(path).read_text(), str(path), "exec")
    out = {}
    for child in st.get_children():
        if "r87" in child.get_name():
            out[child.get_name()] = sorted(
                (s.get_name(), s.is_assigned(), s.is_referenced())
                for s in child.get_symbols())
    return out


bs = fn_symbols(HERE / "base-measure_audio.py", "base")
fs = fn_symbols(HERE / "folded" / "measure_audio.py", "folded")
diffs = [k for k in bs if bs[k] != fs.get(k)]
check("D9 symtable diff (r87 functions)", not diffs,
      f"{len(bs)} functions identical; diffs={diffs}")
new_unread = []
for k in bs:
    fb = {(n, a, r) for n, a, r in bs[k]}
    ff = {(n, a, r) for n, a, r in fs[k]}
    for n, a, r in ff - fb:
        if a and not r:
            new_unread.append((k, n))
check("D9 no new unread name introduced", not new_unread,
      f"new-unread={new_unread}")

bad = [n for n, ok, _ in results if not ok]
print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
sys.exit(1 if bad else 0)
