#!/usr/bin/env python3
"""r84 simplifier STATIC proofs S1..S14 over the commit-pinned blob and the
folded copy. Read-only; writes only proofs/static-proofs.txt.

Every proof is derived from the two files themselves (AST / literal census /
executed source slices); nothing is trusted from the patch author's memory.
"""
import ast
import json
import re
import sys
from pathlib import Path

BASE = Path("proofs/base-measure_audio.py")
FOLD = Path("proofs/folded/measure_audio.py")
bsrc, fsrc = BASE.read_text(), FOLD.read_text()
blines, flines = bsrc.splitlines(), fsrc.splitlines()
btree, ftree = ast.parse(bsrc), ast.parse(fsrc)
out = []
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    tag = "PASS" if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    out.append(f"[{tag}] {name}: {detail}")
    return cond


def in_r84(node):
    return 18821 <= node.lineno <= 21578


def funcs(tree):
    return {n.name: n for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef)}


bf, ff = funcs(btree), funcs(ftree)

# ---------------------------------------------------------------- S1
refs = [i + 1 for i, l in enumerate(blines)
        if re.search(r"\bALSAPW_R84_LINK_WAIT_S\b", l)]
r83refs = [i + 1 for i, l in enumerate(blines)
           if re.search(r"\bPWCAT_R83_LINK_WAIT_S\b", l)]
check("S1 LINK_WAIT_S unused constant",
      len(refs) == 1 and refs[0] == 18968 and len(r83refs) == 4,
      f"ALSAPW_R84_LINK_WAIT_S refs={refs} (definition only); "
      f"live r83 sibling PWCAT_R83_LINK_WAIT_S refs={len(r83refs)}")

# ---------------------------------------------------------------- S2
nsload = bf["_pwcat_r83_ns_load"]
ret = [n for n in ast.walk(nsload) if isinstance(n, ast.Return)]
binds = [n for n in ast.walk(nsload)
         if isinstance(n, ast.Assign) and
         any(isinstance(t, ast.Name) and t.id == "leaf" for t in n.targets)]
check("S2a _pwcat_r83_ns_load returns a dict on every path",
      len(ret) == 2 and all(isinstance(r.value, ast.Name) and
                            r.value.id == "leaf" for r in ret) and
      len(binds) == 2 and all(isinstance(b.value, ast.Dict) for b in binds),
      f"returns={len(ret)} (all `leaf`); leaf bindings={len(binds)} (all dict "
      f"literals) -> cannot return None")

loads_assign = []
for n in ast.walk(btree):
    if isinstance(n, ast.Assign) and in_r84(n):
        tgt = n.targets[0]
        if isinstance(tgt, ast.Subscript) and isinstance(tgt.value, ast.Name) \
                and tgt.value.id == "loads":
            loads_assign.append((n.lineno, ast.unparse(n.value)))
ok = all(v.startswith("_pwcat_r83_ns_load(") for _, v in loads_assign)
check("S2b every r84 `loads[...]` value is _pwcat_r83_ns_load(...)",
      ok and len(loads_assign) == 5,
      f"{len(loads_assign)} sites: {loads_assign}")

teardown_calls, block_calls = [], []
for n in ast.walk(btree):
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and \
            in_r84(n):
        if n.func.id == "_alsapw_r84_teardown":
            teardown_calls.append((n.lineno, len(n.args),
                                   ast.unparse(n.args[2]) if len(n.args) > 2
                                   else None))
        elif n.func.id == "_alsapw_r84_block":
            loads_arg = None
            if len(n.args) >= 4:
                loads_arg = ast.unparse(n.args[3])
            for k in n.keywords:
                if k.arg == "loads":
                    loads_arg = ast.unparse(k.value)
            block_calls.append((n.lineno, loads_arg))
check("S2c teardown always receives a dict; block sometimes omits loads",
      len(teardown_calls) == 4 and
      all(a == 3 and v == "loads" for _, a, v in teardown_calls) and
      sum(1 for _, v in block_calls if v is None) == 7,
      f"teardown calls={teardown_calls} (all positional `loads`); block calls="
      f"{len(block_calls)}, loads omitted in "
      f"{sum(1 for _, v in block_calls if v is None)} -> teardown's `(loads "
      f"or {{}})` is dead (T9); block's is LIVE (retained)")

folded_leaf = [i + 1 for i, l in enumerate(flines)
               if 'leaf.get("module_id"), sink_name=tag' in l]


def guard_census(fn):
    """(count of `loads or {}` guards, count of `leaf or {}` guards) — the
    needles carry no parentheses because ast.unparse drops them."""
    g = [ast.unparse(n) for n in ast.walk(fn) if isinstance(n, ast.BoolOp)]
    return (sum(1 for t in g if "loads or {}" in t),
            sum(1 for t in g if "leaf or {}" in t))


check("S2d fold state: leaf guards gone; block's loads guard kept",
      guard_census(bf["_alsapw_r84_teardown"]) == (4, 1) and
      guard_census(ff["_alsapw_r84_teardown"]) == (0, 0) and
      guard_census(bf["_alsapw_r84_block"]) == (1, 1) and
      guard_census(ff["_alsapw_r84_block"]) == (1, 0) and
      len(folded_leaf) == 2,
      f"folded leaf-guard sites={folded_leaf}; (loads-or, leaf-or) guard "
      f"counts base/teardown={guard_census(bf['_alsapw_r84_teardown'])} "
      f"folded/teardown={guard_census(ff['_alsapw_r84_teardown'])} "
      f"base/block={guard_census(bf['_alsapw_r84_block'])} "
      f"folded/block={guard_census(ff['_alsapw_r84_block'])}")

# ---------------------------------------------------------------- S3
st = bf["_alsapw_r84_st_leg"]
st_ctx = [n for n in ast.walk(st) if isinstance(n, ast.Name) and n.id == "ctx"]
st_calls = [n for n in ast.walk(btree) if isinstance(n, ast.Call) and
            isinstance(n.func, ast.Name) and n.func.id == "_alsapw_r84_st_leg"]
n_ctx_arg = sum(1 for c in st_calls if len(c.args) >= 2)
check("S3a st_leg `ctx` has zero Name nodes in the body",
      len(st_ctx) == 0,
      f"Name('ctx') nodes inside _alsapw_r84_st_leg = {len(st_ctx)} "
      f"(contrast arecord_leg which applies ctx['redact'])")
check("S3b both st_leg call sites pass ctx as arg #2",
      len(st_calls) == 2 and n_ctx_arg == 2,
      f"call sites={len(st_calls)} at L{[c.lineno for c in st_calls]}; "
      f"passing a 2nd positional arg={n_ctx_arg}")
folded_st = ff["_alsapw_r84_st_leg"]
check("S3c folded signature dropped exactly the ctx parameter",
      [a.arg for a in folded_st.args.args] == ["dev", "tail", "timeout_s"] and
      [a.arg for a in st.args.args] == ["dev", "ctx", "tail", "timeout_s"],
      f"base args={[a.arg for a in st.args.args]} folded="
      f"{[a.arg for a in folded_st.args.args]}")

# ---------------------------------------------------------------- S4
def hit_report(fn):
    stores = sorted(n.lineno for n in ast.walk(fn) if isinstance(n, ast.Name)
                    and n.id == "hit" and isinstance(n.ctx, ast.Store))
    loads = sorted(n.lineno for n in ast.walk(fn) if isinstance(n, ast.Name)
                   and n.id == "hit" and isinstance(n.ctx, ast.Load))
    return stores, loads


prop = bf["_alsapw_r84_prop_leg"]
pst, pld = hit_report(prop)
check("S4a prop_leg `hit`: single store, zero loads",
      pst == [20559] and pld == [],
      f"stores={pst} loads={pld}")

neg = bf["alsapw_negctl_r84_entry"]
nst, nld = hit_report(neg)
check("S4b negctl `hit`: the 21546 store is dead (all loads precede it)",
      nst == [21509, 21546] and nld == [21512],
      f"stores={nst} loads={nld}; the only load reads the unit-table binding "
      f"(21509) at 21512, before the dead store at 21546")

sites = []
for fn in (bf.values()):
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple) \
                and len(n.targets[0].elts) == 2 and \
                ast.unparse(n.targets[0].elts[1]) == "hit" and in_r84(n):
            st_, ld_ = hit_report(fn)
            dead = not any(l > n.lineno for l in ld_)
            sites.append((n.lineno, fn.name, dead))
dead_sites = sorted(l for l, _, d in sites if d)
live_sites = sorted(l for l, _, d in sites if not d)
check("S4c exactly the two folded `X, hit =` sites are dead",
      dead_sites == [20559, 21546] and
      live_sites == [19179, 19517, 19560, 19608, 19815, 21509],
      f"all 8 r84 `X, hit =` sites={sorted(l for l,_,_ in sites)}; "
      f"dead={dead_sites} live={live_sites}")

# ---------------------------------------------------------------- S5
wm = bf["_alsapw_r84_wait_moved"]
wm_stores = sorted(n.lineno for n in ast.walk(wm) if isinstance(n, ast.Name)
                   and n.id == "leaf" and isinstance(n.ctx, ast.Store))
wm_loads = sorted(n.lineno for n in ast.walk(wm) if isinstance(n, ast.Name)
                  and n.id == "leaf" and isinstance(n.ctx, ast.Load))
wm_calls = [n for n in ast.walk(btree) if isinstance(n, ast.Call) and
            isinstance(n.func, ast.Name) and
            n.func.id == "_alsapw_r84_wait_moved"]
wm_supplied = [k.arg for c in wm_calls for k in c.keywords]
check("S5 wait_moved: pre-loop fetch is a dead binding over a live I/O call",
      wm_stores == [19334, 19336] and wm_loads == [19337, 19337, 19340] and
      wm_supplied == [],
      f"stores={wm_stores} loads={wm_loads} supplied kwargs={wm_supplied}; "
      f"timeout_s default 2.0 -> the while condition is true on entry and the "
      f"body rebinds leaf before any read; only 19340 (post-loop) is returned")

# ---------------------------------------------------------------- S6
prop_g_stores = sorted(n.lineno for n in ast.walk(prop)
                       if isinstance(n, ast.Name) and n.id == "g" and
                       isinstance(n.ctx, ast.Store))
prop_g_loads = sorted(n.lineno for n in ast.walk(prop)
                      if isinstance(n, ast.Name) and n.id == "g" and
                      isinstance(n.ctx, ast.Load))
check("S6 prop_leg `g`: init never read, no read after the loop",
      prop_g_stores == [20529, 20531] and prop_g_loads == [20532, 20533],
      f"stores={prop_g_stores} loads={prop_g_loads} (both loads inside the "
      f"loop, after the loop-body store at 20531)")

# ---------------------------------------------------------------- S7
def find_test(tree, fn, needle):
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            for s in ast.walk(n):
                if isinstance(s, ast.If) and needle in ast.unparse(s.test):
                    return s.test
    return None


bt = find_test(btree, "_alsapw_r84_sticky_leg", "4294967295")
ft = find_test(ftree, "_alsapw_r84_sticky_leg", "4294967295")
samples = [None, {}, {"sink": None}, {"sink": 4294967295}, {"sink": 77},
           {"index": 5}]
res_b = [eval(ast.unparse(bt), {"si1": s}) for s in samples]
res_f = [eval(ast.unparse(ft), {"si1": s}) for s in samples]
sl = bf["_alsapw_r84_stream_leaf"]
sl_rets = sorted(ast.unparse(r.value) for r in ast.walk(sl)
                 if isinstance(r, ast.Return))
wa = bf["_alsapw_r84_wait_attached"]
wa_ret = sorted({ast.unparse(r.value) for r in ast.walk(wa)
                 if isinstance(r, ast.Return)})
wa_leaf_stores = [(n.lineno, ast.unparse(n.value)) for n in ast.walk(wa)
                  if isinstance(n, ast.Assign) and
                  ast.unparse(n.targets[0]) == "leaf"]
check("S7 sticky guard: `(si1 or {})` subsumed; domain = None | dict",
      res_b == res_f and sl_rets[0] == "None" and sl_rets[1].startswith("{") and
      wa_ret == ["(leaf, round(time.monotonic() - t0, 3))"] and
      wa_leaf_stores == [(19290, "None"),
                         (19292, "_alsapw_r84_stream_leaf(tag, what)")],
      f"base={ast.unparse(bt)!r} folded={ast.unparse(ft)!r} equal over "
      f"{samples} -> {res_b}; stream_leaf returns {sl_rets}; wait_attached "
      f"leaf bindings={wa_leaf_stores} -> si1 is None or a leaf dict")

# ---------------------------------------------------------------- S8
tuple_txt = bsrc.split("_ALSAPW_R84_ERR_CLASSES = (", 1)[1].split("\n)", 1)[0]
err_classes = re.findall(r'\("([a-z0-9_]+)",', tuple_txt)
cases_txt = bsrc.split("    cases = [", 1)[1].split("\n    ]", 1)[0]
cases = ast.literal_eval("[" + cases_txt + "]")
covered = {c[2] for c in cases if c[2]}
negative = [c[0] for c in cases if c[2] is None]
check("S8 every family-local stderr class has a positive unit-table case",
      covered == set(err_classes) and len(err_classes) == 18 and
      len(negative) == 5,
      f"classes={len(err_classes)} covered={len(covered)} missing="
      f"{sorted(set(err_classes) - covered)}; must-classify-nothing cases="
      f"{len(negative)}")

# ---------------------------------------------------------------- S9
wire = {k: [i + 1 for i, l in enumerate(blines) if k in l]
        for k in ('parser.add_argument("--probe-alsapw-r84"',
                  "args.probe_alsapw_r84")}
mutex_line = next(i + 1 for i, l in enumerate(blines)
                  if l.startswith("    if sum([args.probe_slope"))
terms = re.findall(r"args\.(probe_[a-z0-9_]+)", blines[mutex_line - 1])
addargs = set(re.findall(r'add_argument\("--([a-z0-9-]+)"', bsrc))
def dashed(t):
    return t.replace("probe_", "probe-").replace("_", "-")


missing = [t for t in terms if dashed(t) not in addargs]
dups = sorted({t for t in terms if terms.count(t) > 1})
check("S9 wiring: --probe-alsapw-r84 on all five surfaces; mutex sum clean",
      len(wire['parser.add_argument("--probe-alsapw-r84"']) == 1 and
      len(wire["args.probe_alsapw_r84"]) == 4 and not dups and not missing,
      f"parser arg L{wire['parser.add_argument(\"--probe-alsapw-r84\"']}; "
      f"args.probe_alsapw_r84 used at L{wire['args.probe_alsapw_r84']} "
      f"(mutex sum, dispatch guard, mode ternary, suffix ternary); mutex "
      f"terms={len(terms)} duplicates={dups} terms-without-parser-arg={missing}")

# ---------------------------------------------------------------- S10
defs = [n.name for n in btree.body
        if isinstance(n, ast.FunctionDef) and in_r84(n)]
allsyms = [n.name for n in ast.walk(btree) if isinstance(n, ast.FunctionDef)]
dupsym = sorted({d for d in defs if allsyms.count(d) > 1})
namespaced = all(re.match(r"^(?:_alsapw_r84_|alsapw_.*_r84_)", d) for d in defs)
check("S10 all module-level r84 defs namespaced and unique",
      namespaced and not dupsym and len(defs) == 52,
      f"{len(defs)} module-level r84 defs, all `_alsapw_r84_*`/"
      f"`alsapw_*_r84_*`; duplicates={dupsym}")

# ---------------------------------------------------------------- S11
rec = json.loads(Path("../r84-author/runs/run1/measurements.json").read_text())
rec2 = json.loads(Path("../r84-author/runs/run2/measurements.json").read_text())
ENTRIES = ["alsapw_dev_lattice_r84_probe", "alsapw_pw_args_r84_probe",
           "alsapw_pulseprop_r84_probe", "alsapw_pactl_write_r84_probe",
           "alsapw_monstream_r84_probe", "alsapw_negctl_r84_probe"]
legs = sum(len((rec["measurements"][e].get("legs") or {})) for e in ENTRIES)
legs2 = sum(len((rec2["measurements"][e].get("legs") or {})) for e in ENTRIES)
fails = [e for e in ENTRIES if rec["measurements"][e].get("failures")]
fails2 = [e for e in ENTRIES if rec2["measurements"][e].get("failures")]
check("S11 oracle: 147 legs x2 runs, no failures",
      legs == legs2 == 147 and not fails and not fails2,
      f"run1 legs={legs} run2 legs={legs2}; entries with failures="
      f"{fails or fails2 or 'none'}")

# ---------------------------------------------------------------- S12
def find_hold_note(tree):
    for n in ast.walk(tree):
        if isinstance(n, ast.Dict):
            for k, v in zip(n.keys, n.values):
                if isinstance(k, ast.Constant) and k.value == "hold_note":
                    return v
    return None


bh, fh = find_hold_note(btree), find_hold_note(ftree)
samples2 = [([], {}, None), (["card0/pcm3c"], {"card0/pcm3c": "closed"},
                             "card0/pcm3c"),
            (["a", "b"], {"a": "RUNNING", "b": "closed"}, "b")]
res_b2 = [eval(ast.unparse(bh), {"running": r, "states0": s, "held_pcm": h})
          for r, s, h in samples2]
res_f2 = [eval(ast.unparse(fh), {"running": r, "states0": s, "held_pcm": h,
                                "flipped": [k for k in r
                                            if "RUNNING" not in s.get(k, "")]})
          for r, s, h in samples2]
check("S12 hold_note: recomputed comprehension == the loop's `flipped`",
      res_b2 == res_f2 and len(res_b2) == 3,
      f"base={res_b2} folded={res_f2}")

# ---------------------------------------------------------------- S13
te = bf["_alsapw_r84_teardown"]
te_guard_txt = sorted(ast.unparse(n) for n in ast.walk(te)
                      if isinstance(n, ast.BoolOp))
fte = ff["_alsapw_r84_teardown"]
fte_guard_txt = sorted(ast.unparse(n) for n in ast.walk(fte)
                       if isinstance(n, ast.BoolOp))
bk = bf["_alsapw_r84_block"]
bk_guard_txt = sorted(ast.unparse(n) for n in ast.walk(bk)
                      if isinstance(n, ast.BoolOp))
check("S13 teardown `(loads or {})` dead (T9); block's guard live",
      guard_census(bf["_alsapw_r84_teardown"]) == (4, 1) and
      guard_census(ff["_alsapw_r84_teardown"]) == (0, 0) and
      guard_census(bf["_alsapw_r84_block"]) == (1, 1) and
      guard_census(ff["_alsapw_r84_block"]) == (1, 0) and
      te.args.defaults == [] and len(bk.args.defaults) == 1,
      f"base teardown guards={te_guard_txt} (signature defaults="
      f"{te.args.defaults} -> loads is a REQUIRED positional); folded teardown "
      f"guards={fte_guard_txt}; block guard={bk_guard_txt} with defaults="
      f"{bk.args.defaults}")

# ---------------------------------------------------------------- S14
dev = bf["alsapw_dev_lattice_r84_entry"]
fdev = ff["alsapw_dev_lattice_r84_entry"]


def pair_census(fn, names=("held_pcm", "states_held")):
    stores = sorted(n.lineno for n in ast.walk(fn)
                    if isinstance(n, ast.Name) and n.id in names and
                    isinstance(n.ctx, ast.Store))
    loads = sorted(n.lineno for n in ast.walk(fn)
                   if isinstance(n, ast.Name) and n.id in names and
                   isinstance(n.ctx, ast.Load))
    return stores, loads


while_bounds = [ast.unparse(n.test) for n in ast.walk(dev)
                if isinstance(n, ast.While)]
pair, pair_loads = pair_census(dev)
fpair, fpair_loads = pair_census(fdev)
check("S14 ebusy pre-loop init pair (held_pcm/states_held) never read",
      pair == [20019, 20020, 20023, 20029, 20032] and
      min(pair_loads) > 20023 and
      fpair == [20019, 20025, 20028] and min(fpair_loads) > 20019 and
      "5.0" in while_bounds[0],
      f"base stores={pair} loads={pair_loads}; folded stores={fpair} "
      f"loads={fpair_loads}; while bound={while_bounds[0]!r} (hardcoded "
      f"literal > 0 -> at least one iteration, so the pre-loop values are "
      f"never read)")

out.append(f"\nTOTAL: {PASS} PASS / {FAIL} FAIL")
Path("proofs/static-proofs.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
sys.exit(1 if FAIL else 0)
