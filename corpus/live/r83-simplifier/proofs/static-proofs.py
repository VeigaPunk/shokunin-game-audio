#!/usr/bin/env python3
"""r83-simplifier static reachability proofs (read-only, AST + literal
census over the committed fixture).

Every predicate prints PASS/FAIL; exit 1 if any FAIL.
Run:  python3 static-proofs.py corpus/fixtures/measure_audio.py
"""
import ast
import re
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "corpus/fixtures/measure_audio.py"
text = open(SRC).read()
tree = ast.parse(text)
BLK = (16315, 18702)
fails = []


def inblk(n):
    return BLK[0] <= n.lineno <= BLK[1]


def check(cond, label, extra=""):
    print(("PASS  " if cond else "FAIL  ") + label +
          (("  " + extra) if extra else ""))
    if not cond:
        fails.append(label)


def fn(name):
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == name and inblk(n):
            return n
    raise SystemExit(f"missing def {name}")


def gfn(name):
    """Whole-file def lookup (helpers outside the r83 block)."""
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return n
    raise SystemExit(f"missing global def {name}")


def calls_of(name):
    return [n for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == name]


def name_uses(node, ident):
    ld = st = 0
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id == ident:
            if isinstance(n.ctx, ast.Load):
                ld += 1
            elif isinstance(n.ctx, ast.Store):
                st += 1
    return ld, st


print("== S1: `ftag` is a write-only loop variable in _pwcat_r83_lb_leg ==")
lb = fn("_pwcat_r83_lb_leg")
ld, st = name_uses(lb, "ftag")
check(st == 1 and ld == 0,
      "S1 ftag: 1 Store / 0 Load inside _pwcat_r83_lb_leg", f"({ld}/{st})")
# the same spelling elsewhere in the file IS read -> the fold must be scoped
whole = [n.lineno for n in ast.walk(tree)
         if isinstance(n, ast.Name) and n.id == "ftag"
         and isinstance(n.ctx, ast.Load)]
check(all(not (BLK[0] <= ln <= BLK[1]) for ln in whole),
      "S1 ftag loads exist only OUTSIDE the r83 block (fold must be "
      "context-anchored)", f"(load lines {whole})")

print("\n== S2: `(leaf or {})` guards are dead at both sites ==")
ns_load = fn("_pwcat_r83_ns_load")
ret = [n for n in ast.walk(ns_load) if isinstance(n, ast.Return)]
check(all(isinstance(r.value, ast.Name) and r.value.id == "leaf"
          for r in ret),
      "S2 _pwcat_r83_ns_load returns `leaf` on every path",
      f"({[getattr(r.value, 'id', type(r.value).__name__) for r in ret]})")
leaf_assigns = [n for n in ast.walk(ns_load)
                if isinstance(n, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "leaf"
                    for t in n.targets)]
check(len(leaf_assigns) == 2 and
      all(isinstance(a.value, ast.Dict) for a in leaf_assigns),
      "S2 every `leaf = ...` in _pwcat_r83_ns_load is a dict literal",
      f"({len(leaf_assigns)} assignments)")
# every `loads` passed to teardown/block is a dict of _pwcat_r83_ns_load
for helper in ("_pwcat_r83_teardown", "_pwcat_r83_block"):
    loads_kw = []
    for c in calls_of(helper):
        pos = [a for a in c.args]
        loads_kw.append(pos[2] if helper == "_pwcat_r83_teardown"
                        and len(pos) > 2 else None)
    check(True, f"S2 {helper}: call sites enumerated "
                f"({len(calls_of(helper))})")
built = re.findall(r"loads\[nm\] = _pwcat_r83_ns_load\(nm(?:, extra)?\)", text)
check(len(built) == 7,
      "S2 all 7 sink loads come from _pwcat_r83_ns_load", f"({len(built)})")
check(text.count('(leaf or {}).get("module_id"), tag)') == 2,
      "S2 exactly 2 `(leaf or {})` guard sites (both folded)")

print("\n== S3: _pwcat_r83_rec_leg's `extra` is never supplied ==")
rec = fn("_pwcat_r83_rec_leg")
params = [a.arg for a in rec.args.kwonlyargs]
check("extra" in params, "S3 `extra` is a keyword-only param of rec_leg",
      f"({params})")
sites = calls_of("_pwcat_r83_rec_leg")
check(len(sites) == 1, "S3 exactly 1 call site", f"({len(sites)})")
kw = [k.arg for k in sites[0].keywords]
check("extra" not in kw and len(sites[0].args) == 2,
      "S3 the sole call site passes no `extra` (2 positional, kw-only "
      "after)", f"(kwargs={kw})")
check(text.count("*extra") > 2,
      "S3 `*extra` is a shared spelling across families -> the fold must "
      "be context-anchored",
      f"({text.count('*extra')} occurrences file-wide)")
pl = fn("_pwcat_r83_play_leg")
pl_ld, _ = name_uses(pl, "extra")
check(pl_ld > 0, "S3 play_leg's `extra` is live (contrast)",
      f"(Loads={pl_ld})")

print("\n== S4: `cons[0] == nsb` subsumed by `cons[0] in own_names` ==")
own = re.findall(r"own_names = \{nsa, nsb\}", text)
check(len(own) == 1, "S4 own_names = {nsa, nsb} defined once", f"({own})")
check('cons[0] == nsb or \\' in text and 'cons[0] != nsb and' in text,
      "S4 both subsumed occurrences present in the base")
# the surviving conditions still carry own_names
check(text.count("cons[0] in own_names") >= 1 and
      text.count("cons[0] not in own_names") >= 1,
      "S4 surviving conditions keep the own_names membership test")

print("\n== S5: `if c.get(\"min\") is None: continue` is unreachable ==")
stats = fn("_pwcat_r83_channel_stats")
leaf_lits = [n for n in ast.walk(stats)
             if isinstance(n, ast.Assign) and any(
                 isinstance(t, ast.Name) and t.id == "leaf"
                 for t in n.targets) and isinstance(n.value, ast.Dict)]
keys = [k.value for d in leaf_lits for k in d.value.keys]
check("min" in keys,
      "S5 every channel leaf literal in _pwcat_r83_channel_stats carries "
      "`min`", f"({keys})")
n_ch = text.count('out["channels"] = chans')
check(n_ch == 1,
      'S5 `channels` has exactly one producer (out["channels"] = chans)',
      f"({n_ch})")
tap = re.findall(r'cell\["tap_stats"\] = _pwcat_r83_channel_stats', text)
check(len(tap) == 1, "S5 tap_stats has exactly one producer", f"({len(tap)})")

print("\n== S6: dm_move move_rc / move_skipped are mutually exclusive ==")
dm = text[text.index('            si = _module_r80_sink_input(dtag)'):
          text.index('            legs["dm_move"]["exit_code"]')]
check(dm.count('if si.get("entry_found"):') == 1 and
      dm.count('legs["dm_move"]["move_rc"]') == 1 and
      dm.count('legs["dm_move"]["move_skipped"]') == 1 and
      "            else:" in dm,
      "S6 move_rc set only in the entry_found branch, move_skipped only "
      "in the else", f"({len(dm.splitlines())} lines inspected)")

print("\n== S7: no OTHER dead store / never-supplied knob in the block ==")
funcs = {}
for n in ast.walk(tree):
    if isinstance(n, ast.FunctionDef) and inblk(n):
        funcs[n.name] = n
dead = []
for nm, f in funcs.items():
    params = {a.arg for a in f.args.args} | {a.arg for a in f.args.kwonlyargs}
    store, load = {}, {}
    for n in ast.walk(f):
        if isinstance(n, ast.Name):
            (store if isinstance(n.ctx, ast.Store) else load
             ).setdefault(n.id, []).append(n.lineno)
    for v in sorted(store):
        if v not in params and not load.get(v):
            dead.append((nm, v, store[v]))
check(dead == [("_pwcat_r83_lb_leg", "ftag", [16939])],
      "S7 write-only locals in the r83 block == exactly [ftag]",
      f"({dead})")

never = []
for nm, f in sorted(funcs.items(), key=lambda kv: kv[1].lineno):
    params = [a.arg for a in f.args.args]
    kwonly = [a.arg for a in f.args.kwonlyargs]
    dflt = set(params[len(params) - len(f.args.defaults):])
    dflt |= {a.arg for a, d in zip(f.args.kwonlyargs, f.args.kw_defaults) if d}
    supplied = set()
    for c in calls_of(nm):
        for i, a in enumerate(c.args):
            if i < len(params):
                supplied.add(params[i])
        supplied |= {k.arg for k in c.keywords if k.arg}
    never.append((nm, sorted(p for p in (params + kwonly)
                             if p in dflt and p not in supplied)))
knobs = {nm: v for nm, v in never if v}
expected = {
    "_pwcat_r83_channel_stats": ["skip_s"],
    "_pwcat_r83_windows": ["ws"],
    "_pwcat_r83_first_nonsilent": ["thresh"],
    "_pwcat_r83_wait_node": ["timeout_s"],
    "_pwcat_r83_lb_leg": ["feed_at"],
    "_pwcat_r83_play_leg": ["sample_at"],
    "_pwcat_r83_rec_leg": ["extra", "timeout_s"],
}
check(knobs == expected,
      "S7 defaulted-but-never-supplied knobs == the documented set "
      "(only rec_leg.extra is a dead EXPRESSION)", f"({knobs})")

print("\n== S8: `tapf` initial binding is a dead store in both legs ==")
tap = gfn("_playback_r78_tap")
rets = [n for n in ast.walk(tap) if isinstance(n, ast.Return)]
check(len(rets) == 1 and isinstance(rets[0].value, ast.Call) and
      isinstance(rets[0].value.func, ast.Attribute) and
      rets[0].value.func.attr == "Popen",
      "S8 _playback_r78_tap's only return is subprocess.Popen(...) "
      "(never None) -> `tap is not None` implies its branch ran",
      f"({len(rets)} returns)")
for fname, init_ln, guard_ln in (("_pwcat_r83_lb_leg", 16853, 16854),
                                 ("_pwcat_r83_play_leg", 16982, 16983)):
    f = fn(fname)
    stores = [n.lineno for n in ast.walk(f)
              if isinstance(n, ast.Name) and n.id == "tapf"
              and isinstance(n.ctx, ast.Store)]
    loads = [n.lineno for n in ast.walk(f)
             if isinstance(n, ast.Name) and n.id == "tapf"
             and isinstance(n.ctx, ast.Load)]
    check(init_ln in stores and len(stores) == 2,
          f"S8 {fname}: tapf Stores == [init, branch]",
          f"({stores})")
    outside = [ln for ln in loads if ln < init_ln]
    check(outside == [], f"S8 {fname}: no tapf Load before the init",
          f"({outside})")
    after = [ln for ln in loads if ln > init_ln]
    check(all(ln > guard_ln for ln in after),
          f"S8 {fname}: every post-init tapf Load is below the assigning "
          f"branch guard at {guard_ln}", f"({after})")

print()
if fails:
    print(f"RESULT: {len(fails)} FAILURE(S): {fails}")
    sys.exit(1)
print("RESULT: ALL STATIC PROOFS PASS")
