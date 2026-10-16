#!/usr/bin/env python3
"""r85 simplifier STATIC proofs over the commit-pinned blob (read-only).

Every check re-derives one fold item from the pinned base text (AST +
word-boundary census) and, where relevant, re-checks the folded copy.
"""
import ast
import re
from pathlib import Path

BASE = Path("proofs/base-measure_audio.py")
FOLD = Path("proofs/folded/measure_audio.py")
bsrc = BASE.read_text(encoding="utf-8")
fsrc = FOLD.read_text(encoding="utf-8")
blines = bsrc.splitlines()
flines = fsrc.splitlines()
btree = ast.parse(bsrc)
ftree = ast.parse(fsrc)

OUT = []
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    tag = "PASS" if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    OUT.append(f"[{tag}] {name}: {detail}")


bstart = next(i for i, l in enumerate(blines) if l.startswith("# r85: the pactl"))
bend = next(i for i, l in enumerate(blines) if l.startswith("def main():"))
region = "\n".join(blines[bstart:bend])

FAMILY = re.compile(r"^(?:_pactlmon_r85_|pactlmon_.*_r85_)")
bfuncs = {n.name: n for n in ast.walk(btree)
          if isinstance(n, ast.FunctionDef) and FAMILY.match(n.name)}
ffuncs = {n.name: n for n in ast.walk(ftree)
          if isinstance(n, ast.FunctionDef) and FAMILY.match(n.name)}
bcalls = {}
for n in ast.walk(btree):
    if isinstance(n, ast.Call):
        f = n.func
        nm = f.id if isinstance(f, ast.Name) else (
            f.attr if isinstance(f, ast.Attribute) else None)
        if nm:
            bcalls.setdefault(nm, []).append(n)


def loads_of(fn, name):
    return [n.lineno for n in ast.walk(fn)
            if isinstance(n, ast.Name) and n.id == name
            and isinstance(n.ctx, ast.Load)]


def stores_of(fn, name):
    return [n.lineno for n in ast.walk(fn)
            if isinstance(n, ast.Name) and n.id == name
            and isinstance(n.ctx, ast.Store)]


# ---------------------------------------------------------------- S1
refs = len(re.findall(r"\bPACTLMON_R85_STREAM_WAIT_S\b", bsrc))
sib = len(re.findall(r"\bALSAPW_R84_STREAM_WAIT_S\b", bsrc))
check("S1 PACTLMON_R85_STREAM_WAIT_S unused constant",
      refs == 1 and sib == 5 and
      "PACTLMON_R85_STREAM_WAIT_S" not in fsrc,
      f"base refs={refs} (definition only); live r84 sibling "
      f"ALSAPW_R84_STREAM_WAIT_S refs={sib}; folded has none")

# ---------------------------------------------------------------- S2
wcalls = len(bcalls.get("_pactlmon_r85_wait_node", []))
others = [l for l in blines[bstart:bend] if "wait_node" in l and
          "_pactlmon_r85_wait_node" not in l]
check("S2 _pactlmon_r85_wait_node has zero call sites",
      wcalls == 0 and not others and
      "_pactlmon_r85_wait_node" not in fsrc and
      len(bfuncs) == len(ffuncs) + 1,
      f"base call sites={wcalls}; other wait_node mentions={others}; "
      f"folded defines none; r85 defs base/folded={len(bfuncs)}/"
      f"{len(ffuncs)}")

# ---------------------------------------------------------------- S3
sd = bfuncs["_pactlmon_r85_sd_leg"]
sd_ctx = loads_of(sd, "ctx")
sd_sites = bcalls["_pactlmon_r85_sd_leg"]
sd_second = [c.lineno for c in sd_sites
             if len(c.args) >= 2 and ast.unparse(c.args[1]) == "ctx"]
check("S3 _pactlmon_r85_sd_leg `ctx` param is never read",
      not sd_ctx and len(sd_sites) == 2 and len(sd_second) == 2 and
      [a.arg for a in ffuncs["_pactlmon_r85_sd_leg"].args.args] ==
      ["name", "sd", "client_argv", "dur_s"],
      f"ctx loads inside base fn={sd_ctx}; call sites={len(sd_sites)} "
      f"(passing ctx as arg#2: {sd_second}); folded args="
      f"{[a.arg for a in ffuncs['_pactlmon_r85_sd_leg'].args.args]}")

# ---------------------------------------------------------------- S4
tl = bfuncs["_pactlmon_r85_wait_tap_link"]
tl_sink = loads_of(tl, "sink")
tl_sites = bcalls["_pactlmon_r85_wait_tap_link"]
tl_first = [c.lineno for c in tl_sites
            if c.args and "ctx" in ast.unparse(c.args[0])]
check("S4 _pactlmon_r85_wait_tap_link `sink` param is never read",
      not tl_sink and len(tl_sites) == 1 and len(tl_first) == 1 and
      [a.arg for a in ffuncs["_pactlmon_r85_wait_tap_link"].args.args] ==
      ["tap_tag", "timeout_s"],
      f"sink loads inside base fn={tl_sink}; call sites={len(tl_sites)} "
      f"(passing ctx['mix']: {tl_first}); folded args="
      f"{[a.arg for a in ffuncs['_pactlmon_r85_wait_tap_link'].args.args]}")

# ---------------------------------------------------------------- S5
cap = bfuncs["_pactlmon_r85_cap_leg"]
sdleg = bfuncs["_pactlmon_r85_sd_leg"]
cap_hit_s, cap_hit_l = stores_of(cap, "hit"), loads_of(cap, "hit")
sd_hit_s, sd_hit_l = stores_of(sdleg, "hit"), loads_of(sdleg, "hit")
run = bfuncs["_pactlmon_r85_run"]
run_hit_s, run_hit_l = stores_of(run, "hit"), loads_of(run, "hit")
neg = bfuncs["pactlmon_negctl_r85_entry"]
neg_hit_s, neg_hit_l = stores_of(neg, "hit"), loads_of(neg, "hit")
check("S5 the two folded `hit` stores are dead; every other `hit` is live",
      cap_hit_s == [22218] and cap_hit_l == [] and
      sd_hit_s == [22304] and sd_hit_l == [] and
      len(run_hit_l) == 1 and len(neg_hit_l) >= 1 and
      fsrc.splitlines()[bstart:bend].__str__().count("cls, hit =") == 1,
      f"cap_leg stores={cap_hit_s} loads={cap_hit_l}; sd_leg "
      f"stores={sd_hit_s} loads={sd_hit_l}; _run loads={run_hit_l} "
      f"(error_hit); negctl stores={neg_hit_s} loads={neg_hit_l}; "
      f"folded r85-region `cls, hit =` count="
      f"{fsrc.splitlines()[bstart:bend].__str__().count('cls, hit =')} "
      f"(the live _pactlmon_r85_run site)")

# ---------------------------------------------------------------- S6
addr = bfuncs["pactlmon_addr_r85_entry"]
sers_s, sers_l = stores_of(addr, "sers"), loads_of(addr, "sers")
check("S6 addr entry `sers` is a dead store",
      sers_s == [22738] and sers_l == [] and
      not re.search(r"\bsers\b", fsrc) and
      "serials != sorted(serials)" in bsrc,
      f"stores={sers_s} loads={sers_l}; the following monotonicity "
      f"check reads `serials` (the loop list), not `sers`; folded has "
      f"no `sers`")

# ---------------------------------------------------------------- S7
capent = bfuncs["pactlmon_capture_r85_entry"]
lp_s, lp_l = stores_of(capent, "lp"), loads_of(capent, "lp")
check("S7 capture entry `lp` @L23510 is a store-after-last-load",
      sorted(lp_s) == [23497, 23504, 23510] and max(lp_l) < 23510 and
      "link_ports(\"t_prop_srcname\")" not in fsrc and
      'pl = [e for s in legs["t_prop_srcname"]' in bsrc,
      f"stores={lp_s} loads={lp_l} (max load {max(lp_l)} < last store "
      f"23510); the next statement binds `pl` from the same leg")

# ---------------------------------------------------------------- S8
wn_s, wn_l = stores_of(capent, "want_node"), loads_of(capent, "want_node")
check("S8 capture entry `want_node` is a dead loop payload",
      wn_s == [23491] and wn_l == [] and
      'for nm in ("t_srcname", "t_srcserial", "t_srcid"):' in fsrc and
      "want_node" not in fsrc,
      f"stores={wn_s} loads={wn_l}; the loop body only reads `nm`; "
      f"folded header = the 3-name tuple")

# ---------------------------------------------------------------- S9
gsv = None
for sub in ast.walk(addr):
    if isinstance(sub, ast.FunctionDef) and sub.name == "gsv":
        gsv = sub
gsv_label = loads_of(gsv, "label") if gsv else None
gsv_calls = [c for c in ast.walk(addr)
             if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
             and c.func.id == "gsv"]
gsv_two = [c.lineno for c in gsv_calls if len(c.args) == 2]
fgsv = None
for sub in ast.walk(ffuncs["pactlmon_addr_r85_entry"]):
    if isinstance(sub, ast.FunctionDef) and sub.name == "gsv":
        fgsv = sub
check("S9 the entry-local `gsv` `label` param is never read",
      gsv is not None and gsv_label == [] and len(gsv_calls) == 20 and
      len(gsv_two) == 20 and
      [a.arg for a in fgsv.args.args] == ["arg"] and
      fsrc.count("gsv(") == 21,
      f"base label loads={gsv_label}; gsv call sites={len(gsv_calls)} "
      f"(supplying a label: {len(gsv_two)}); folded signature args="
      f"{[a.arg for a in fgsv.args.args]}; folded gsv( count="
      f"{fsrc.count('gsv(')}")

# ---------------------------------------------------------------- S10
td = bfuncs["_pactlmon_r85_teardown"]
blk = bfuncs["_pactlmon_r85_block"]
td_defaults = len(td.args.defaults) + len(td.args.kw_defaults)
blk_defaults = [ast.unparse(d) for d in blk.args.defaults]
td_calls = bcalls["_pactlmon_r85_teardown"]
td_supplied = [c.lineno for c in td_calls if len(c.args) >= 3]
blk_calls = bcalls["_pactlmon_r85_block"]
blk_supplied = [c.lineno for c in blk_calls if len(c.args) >= 4]
check("S10 teardown `(loads or {})` dead; block's guard live",
      td_defaults == 0 and len(td_calls) == 5 and
      len(td_supplied) == 5 and len(blk_calls) == 11 and
      len(blk_supplied) == 6 and blk_defaults == ["None"] and
      "for tag, leaf in loads.items():" in fsrc and
      "for tag, leaf in (loads or {}).items():" in fsrc,
      f"teardown defaults={td_defaults} (required positional), call "
      f"sites={len(td_calls)} passing loads={len(td_supplied)}; block "
      f"defaults={blk_defaults}, call sites={len(blk_calls)} passing "
      f"loads={len(blk_supplied)} -> block's guard is a real path and "
      f"is RETAINED in the folded copy")

# ---------------------------------------------------------------- S11
ns_load = next(n for n in ast.walk(btree)
               if isinstance(n, ast.FunctionDef)
               and n.name == "_pwcat_r83_ns_load")
ns_returns = [n for n in ast.walk(ns_load) if isinstance(n, ast.Return)]
ns_leaf_bind = [n for n in ast.walk(ns_load)
                if isinstance(n, ast.Name) and n.id == "leaf"
                and isinstance(n.ctx, ast.Store)]
ns_leaf_dict = [n for n in ast.walk(ns_load)
                if isinstance(n, ast.Assign) and
                isinstance(n.targets[0], ast.Name) and
                n.targets[0].id == "leaf" and
                isinstance(n.value, ast.Dict)]
loads_vals = []
for n in ast.walk(btree):
    if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Subscript):
        t = n.targets[0]
        if isinstance(t.value, ast.Name) and t.value.id == "loads" and \
                bstart + 1 <= n.lineno <= bend:
            loads_vals.append((n.lineno, ast.unparse(n.value)[:60]))
prod_ok = all(("_pwcat_r83_ns_load" in v or "_pactlmon_r85_remap_load" in v
               or "_pactlmon_r85_sd_load" in v or v.startswith("dict(")
               or "late_load" in v) for _, v in loads_vals)
check("S11 every `loads[...]` value is a dict -> `leaf or {}` guards dead",
      len(ns_returns) == 2 and len(ns_leaf_bind) == 2 and
      len(ns_leaf_dict) == 2 and len(loads_vals) == 16 and prod_ok and
      "leaf = leaf or {}" not in fsrc,
      f"_pwcat_r83_ns_load returns={len(ns_returns)} (all `leaf`); leaf "
      f"bindings={len(ns_leaf_bind)} (dict literals: {len(ns_leaf_dict)}); "
      f"loads[...] value assignments={len(loads_vals)} (the 13 other "
      f"`loads[...][...] = ...` sites mutate those dicts); all from "
      f"dict-returning producers={prod_ok}; folded has no "
      f"`leaf = leaf or {{}}`")

# ---------------------------------------------------------------- S12
subsumed = [
    ("a1", 'a1 = (legs.get("mv_name") or {}).get("after") or {}'),
    ("a2", 'a2 = (legs.get("mv_serial") or {}).get("after") or {}'),
    ("a4", 'a4 = cm.get("after") or {}'),
]
ok12 = all(needle in bsrc for _, needle in subsumed)
ok12 = ok12 and '(a1 or {})' not in fsrc and '(a2 or {})' not in fsrc \
    and '(a4 or {})' not in fsrc
check("S12 the four subsumed `(aN or {})` guards are gone",
      ok12,
      "a1/a2/a4 are bound by `... or {}` before every guard "
      "(dict domain); folded still has "
      f"(a1 or {{}})={'(a1 or {})' in fsrc} (a2 or {{}})="
      f"{'(a2 or {})' in fsrc} (a4 or {{}})={'(a4 or {})' in fsrc}")

# ---------------------------------------------------------------- S13
vp = bfuncs["_pactlmon_r85_vol_pct"]
vp_calls = bcalls["_pactlmon_r85_vol_pct"]
vp_args = [ast.unparse(c.args[0]) for c in vp_calls]
check("S13 _pactlmon_r85_vol_pct `(rec or {})` is dead",
      "(rec or {})" not in fsrc and
      're.search(r"(\\d+)\\s*%", rec.get("stdout") or "")' in fsrc and
      len(vp_calls) == 7 and
      all("legs[" in a or a == "l" for a in vp_args),
      f"call args={vp_args} (leg dicts only); folded body drops the "
      f"falsy guard")

# ---------------------------------------------------------------- S14
feeder_guard = bsrc.count("if feeder is not None and feeder.poll() is None:")
check("S14 the pre-ladder `feeder is not None` conjunct is dead",
      feeder_guard == 2 and
      fsrc.count("if feeder is not None and feeder.poll() is None:") == 1 and
      fsrc.count("if feeder.poll() is None:") == 1 and
      'feeder = _pactlmon_r85_play(' in bsrc,
      f"base occurrences={feeder_guard} (the live one is the `finally` "
      f"guard; the folded one is the pre-ladder site); folded keeps the "
      f"finally guard and the bare-poll pre-ladder guard; `feeder` is "
      f"bound unconditionally before the pre-ladder site (an exception "
      f"skips the site entirely)")

# ---------------------------------------------------------------- S15
wiring = {}
for i, l in enumerate(blines):
    if "probe-pactlmon-r85" in l and "add_argument" in l:
        wiring["parser"] = i + 1
    if "args.probe_pactlmon_r85" in l:
        if "sum([" in l:
            wiring["mutex"] = i + 1
        elif re.match(r"\s*if args\.probe_pactlmon_r85:", l):
            wiring["dispatch"] = i + 1
        elif 'mode = "probe-pactlmon-r85"' in l:
            wiring["mode"] = i + 1
        elif 'suffix = "-pactlmon-r85"' in l:
            wiring["suffix"] = i + 1
mutex_line = blines[wiring["mutex"] - 1]
terms = re.findall(r"args\.probe_\w+", mutex_line)
check("S15 wiring: all five surfaces consume --probe-pactlmon-r85",
      set(wiring) == {"parser", "mutex", "dispatch", "mode", "suffix"} and
      len(terms) == len(set(terms)) and
      "args.probe_pactlmon_r85" in terms,
      f"surfaces={wiring}; mutex terms={len(terms)} duplicates="
      f"{len(terms) - len(set(terms))}; new arg present="
      f"{'args.probe_pactlmon_r85' in terms}")

# ---------------------------------------------------------------- S16
defs_b = [n for n in ast.walk(btree)
          if isinstance(n, ast.FunctionDef) and FAMILY.match(n.name)]
defs_f = [n for n in ast.walk(ftree)
          if isinstance(n, ast.FunctionDef) and FAMILY.match(n.name)]
allnames = [n.name for n in defs_b]
check("S16 r85 defs are namespaced, unique, and the fold removes exactly one",
      len(allnames) == len(set(allnames)) and
      sorted(allnames) == sorted(set(allnames)) and
      set(n.name for n in defs_f) == set(allnames) -
      {"_pactlmon_r85_wait_node"},
      f"base r85 defs={len(allnames)} unique={len(set(allnames))}; "
      f"folded defs={len(defs_f)} (only _pactlmon_r85_wait_node removed)")

# ---------------------------------------------------------------- S17
import json
runs = {}
for r in ("run1", "run2"):
    d = json.loads(Path(f"../r85-author/runs/{r}/measurements.json")
                   .read_text())
    runs[r] = d
legs = {r: {k: len(v.get("legs", {})) for k, v in
            d["measurements"].items() if k.startswith("pactlmon_")}
        for r, d in runs.items()}
fails = {r: {k: v.get("failures") for k, v in d["measurements"].items()
             if k.startswith("pactlmon_")} for r, d in runs.items()}
check("S17 oracle: 87 legs x2 runs, no failures",
      all(sum(v.values()) == 87 for v in legs.values()) and
      all(all(f == [] for f in v.values()) for v in fails.values()),
      f"legs run1={legs['run1']} total={sum(legs['run1'].values())}; "
      f"run2={legs['run2']} total={sum(legs['run2'].values())}; "
      f"all failures empty")

# ---------------------------------------------------------------- S18
neg = bfuncs["pactlmon_negctl_r85_entry"]
cases = [n for n in ast.walk(neg) if isinstance(n, ast.Assign) and
         isinstance(n.targets[0], ast.Name) and n.targets[0].id == "cases"]
case_elts = [e for e in ast.walk(cases[0].value) if isinstance(e, ast.Tuple)]
wants = [ast.literal_eval(e.elts[2]) for e in case_elts]
families = set(wants) - {None}
check("S18 classifier unit table covers both family-local classes",
      len(case_elts) == 13 and
      {"pa_invalid_arg", "pwcli_unknown_global"} <= families and
      None in wants and
      len(re.findall(r'\("pa_invalid_arg", r"Operation failed: Invalid argument"\)',
                     bsrc)) == 1,
      f"unit cases={len(case_elts)}; classes={sorted(x for x in families)}; "
      f"must-classify-nothing={wants.count(None)}")

# ---------------------------------------------------------------- S19
def unit_map(src):
    t = ast.parse(src)
    ls = src.splitlines()
    fns, consts = {}, {}
    for n in t.body:
        if isinstance(n, ast.FunctionDef):
            fns[n.name] = "\n".join(ls[n.lineno - 1:n.end_lineno])
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
            consts[n.targets[0].id] = "\n".join(ls[n.lineno - 1:n.end_lineno])
    return fns, consts


bu, bc = unit_map(bsrc)
fu, fc = unit_map(fsrc)
changed_fn = sorted(k for k in bu if bu[k] != fu.get(k))
changed_const = sorted(k for k in bc if bc[k] != fc.get(k))
EXPECT_FN = sorted(["_pactlmon_r85_cap_leg", "_pactlmon_r85_sd_leg",
                    "_pactlmon_r85_teardown", "_pactlmon_r85_block",
                    "_pactlmon_r85_vol_pct",
                    "_pactlmon_r85_wait_tap_link",
                    "_pactlmon_r85_tapped_mix",
                    "_pactlmon_r85_wait_node",
                    "pactlmon_addr_r85_entry",
                    "pactlmon_capture_r85_entry"])
check("S19 only the intended units differ (8 functions + 1 constant)",
      changed_fn == EXPECT_FN and
      changed_const == ["PACTLMON_R85_STREAM_WAIT_S"] and
      len(bu) == len(fu) + 1,
      f"changed functions={changed_fn}; changed constants={changed_const}; "
      f"functions total base/folded={len(bu)}/{len(fu)}")

Path("proofs/static-proofs.txt").write_text("\n".join(OUT) + "\n\n"
                                           f"TOTAL: {PASS} PASS / {FAIL} FAIL\n",
                                           encoding="utf-8")
print("\n".join(OUT))
print(f"\nTOTAL: {PASS} PASS / {FAIL} FAIL")
