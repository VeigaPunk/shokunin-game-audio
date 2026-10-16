#!/usr/bin/env python3
"""r87 simplifier — static reachability/dominance/wiring proofs (S1-S16).

Reads only the pinned base blob + the folded copy + the r87 landing
diff + the fold patch.  Region-scoped: every census that could collide
with a prior family (r84-r86 keep the same guard/homograph shapes) is
restricted to the r87 family region, located by marker lines.
"""
import ast
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
BASE = (HERE / "base-measure_audio.py").read_text()
FOLDED = (HERE / "folded" / "measure_audio.py").read_text()
PATCH = (HERE.parent / "r87-simplifier.patch").read_text()
LAND = (HERE / "r87-diff.patch").read_text()

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


def occ(text, pat):
    return len(re.findall(pat, text))


def region(text):
    """The r87 family region: header comment .. end of the dispatch
    block (the line before the r85 dispatch block)."""
    lines = text.splitlines(keepends=True)
    lo = hi = None
    for i, l in enumerate(lines):
        if l.startswith("# r87: the DEVICE-BINDING lattice"):
            lo = i
        if lo is not None and l.startswith("    if args.probe_pactlmon_r85:"):
            hi = i
            break
    assert lo is not None and hi is not None
    return "".join(lines[lo:hi]), lo + 1, hi


BR, BLO, BHI = region(BASE)
FR, FLO, FHI = region(FOLDED)

# ---------------------------------------------------------------- S1
for nm in ("PWBIND_R87_LINK_WAIT_S", "PWBIND_R87_TAP_WAIT_S"):
    b = occ(BR, r"\b" + nm + r"\b")
    f = occ(FR, r"\b" + nm + r"\b")
    check(f"S1 dead constant {nm}", b == 1 and f == 0, f"base={b} folded={f}")
b = occ(BR, r"\bPWBIND_R87_STREAM_WAIT_S\b")
f = occ(FR, r"\bPWBIND_R87_STREAM_WAIT_S\b")
check("S1 contrast STREAM_WAIT_S live", b == 2 and f == 2,
      f"base={b} folded={f} (def+use)")

# ---------------------------------------------------------------- S2
b = occ(BR, r"\(loads or \{\}\)")
f = occ(FR, r"\(loads or \{\}\)")
check("S2 r87 (loads or {}) 4 -> 1 (block guard retained)",
      b == 4 and f == 1, f"base={b} folded={f}")
check("S2 teardown loads.items() direct",
      occ(FR, r"for tag, leaf in loads\.items\(\):") == 1 and
      occ(BR, r"for tag, leaf in loads\.items\(\):") == 0)

# ---------------------------------------------------------------- S3
check("S3 r87 leaf = leaf or {} gone",
      occ(BR, r"leaf = leaf or \{\}") == 2 and
      occ(FR, r"leaf = leaf or \{\}") == 0)

# ---------------------------------------------------------------- S4
tree = ast.parse(BASE)
tear = next(n for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name == "_pwbind_r87_teardown")
args = [a.arg for a in tear.args.args]
defaults = len(tear.args.defaults)
check("S4 teardown signature (3 params, no default on loads)",
      args == ["entry", "failures", "loads"] and defaults == 0,
      f"args={args} defaults={defaults}")
calls = [n.lineno for n in ast.walk(tree)
         if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
         and n.func.id == "_pwbind_r87_teardown"]
allpos = all(len(c.args) == 3 and not c.keywords for c in ast.walk(tree)
             if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
             and c.func.id == "_pwbind_r87_teardown")
check("S4 teardown call sites all pass loads positionally",
      calls == [26201, 26428, 26952, 27400] and allpos, f"calls={calls}")

# ---------------------------------------------------------------- S5
pwcat = next(n for n in tree.body
             if isinstance(n, ast.FunctionDef) and n.name == "_pwcat_r83_ns_load")
rets = [n for n in ast.walk(pwcat) if isinstance(n, ast.Return)]
dict_rets = [n for n in rets if isinstance(n.value, ast.Name)]
check("S5 _pwcat_r83_ns_load returns `leaf` on both paths (dict literal domain)",
      len(rets) == 2 and len(dict_rets) == 2, f"returns={len(rets)}")
loadns = ast.unparse(next(n for n in tree.body
                          if isinstance(n, ast.FunctionDef)
                          and n.name == "_pwbind_r87_load_ns"))
check("S5 _pwbind_r87_load_ns adds field/value to the leaf",
      re.search(r"""leaf\[['"]field['"]\]""", loadns) is not None and
      re.search(r"""leaf\[['"]value['"]\]""", loadns) is not None and
      "return leaf" in loadns)

# ---------------------------------------------------------------- S6
for entry in ("pwbind_modes_r87_entry", "pwbind_target_r87_entry",
              "pwbind_cli_r87_entry", "pwbind_midi_r87_entry"):
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == entry)
    assigns = [n for n in ast.walk(fn)
               if isinstance(n, ast.Assign) and
               any(isinstance(t, ast.Name) and t.id == "loads"
                   for t in n.targets)]
    shapes = []
    for a in assigns:
        v = a.value
        if isinstance(v, ast.Dict) and not v.keys:
            shapes.append(f"{a.lineno}:{{}}")
        elif isinstance(v, ast.Subscript):
            shapes.append(f"{a.lineno}:[k]=load_ns()")
        else:
            shapes.append(f"{a.lineno}:{ast.dump(v)[:40]}")
    ok = shapes and all(s.endswith(":{}") or s.endswith("[k]=load_ns()")
                        for s in shapes)
    check(f"S6 {entry} loads domain is dict", ok, ",".join(shapes))

# ---------------------------------------------------------------- S7
lines = BASE.splitlines()
seg = lines[26497 - 1:27167]
nid_ret = [i for i, l in enumerate(seg) if re.search(r"if nid is None:", l)]
nid_store = [i for i, l in enumerate(seg) if re.search(r"^\s+nid = ", l)]
fmt_guard = [i for i, l in enumerate(seg) if re.search(r"if nid is not None:", l)]
check("S7 cli nid early block-return dominates the fmt_sink guard",
      len(nid_ret) == 1 and len(nid_store) == 1 and len(fmt_guard) == 1 and
      nid_store[0] < nid_ret[0] < fmt_guard[0],
      f"store@{26497+nid_store[0]} return@{26497+nid_ret[0]} "
      f"use@{26497+fmt_guard[0]} (no nid rebind between)")

# ---------------------------------------------------------------- S8
tgt = lines[26279 - 1:26494]
def0 = [i for i, l in enumerate(tgt) if re.search(r"if not DEF0:", l)]
set0 = [i for i, l in enumerate(tgt)
        if 'entry["default_sink_at_start"] = DEF0' in l]
defv = [i for i, l in enumerate(tgt) if re.search(r"^\s+DEF = ", l)]
check("S8 target DEF fallback dominated by the DEF0 block-return",
      len(def0) == 1 and len(set0) == 1 and len(defv) == 1 and
      def0[0] < set0[0] < defv[0],
      f"if-not-DEF0@{26279+def0[0]} set@{26279+set0[0]} DEF@{26279+defv[0]}")

# ---------------------------------------------------------------- S9
check("S9 cli solo_hi None init gone (region-scoped)",
      BR.count("solo_lo, solo_hi = mark(), None") == 1 and
      FR.count("solo_lo, solo_hi = mark(), None") == 0 and
      FR.count("\n                solo_lo = mark()\n") == 1)
check("S9 solo_hi real assignment retained",
      FR.count("\n                solo_hi = mark()\n") == 1)

# ---------------------------------------------------------------- S10
a = f"unknown global '{99999999}'"
check("S10 T8 subsumption (id form contains the generic form)",
      "unknown global" in a)
check("S10 T8 id-term gone from the region",
      occ(BR, r"""f"unknown global '\{nid\}'" not in blob""") == 1 and
      occ(FR, r"""f"unknown global '\{nid\}'" not in blob""") == 0)

# ---------------------------------------------------------------- S11
check("S11 T9 coll_ports guard gone; all([]) is True",
      occ(BR, r"if coll_ports and not all") == 1 and
      occ(FR, r"if coll_ports and not all") == 0 and all([]) is True)

# ---------------------------------------------------------------- S12
region_lo, region_hi = BLO, BHI
hunks = []
for ln in PATCH.splitlines():
    m = re.match(r"@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@", ln)
    if m:
        hunks.append((int(m.group(1)), int(m.group(2) or 1)))
check("S12 patch confinement (all hunks in the r87 region)",
      hunks and all(region_lo <= h[0] <= region_hi for h in hunks),
      f"{len(hunks)} hunks, base-side starts {[h[0] for h in hunks]}")

# ---------------------------------------------------------------- S13
check("S13 --probe-pwbind-r87 flag once", occ(FOLDED, r'"--probe-pwbind-r87"') == 1)
check("S13 mutex sum term once",
      occ(FOLDED, r"args\.probe_pwbind_r87\]\) > 1:") == 1)
check("S13 dispatch 4 entries",
      occ(FOLDED, r'measurements\["pwbind_(modes|target|cli|midi)_r87_probe"\]') == 4)
check("S13 mode/suffix heads",
      occ(FOLDED, r'mode = "probe-pwbind-r87" if args\.probe_pwbind_r87') == 1 and
      occ(FOLDED, r'suffix = "-pwbind-r87" if args\.probe_pwbind_r87') == 1)

# ---------------------------------------------------------------- S14
removed = [l for l in LAND.splitlines()
           if l.startswith("-") and not l.startswith("---")]
added = [l for l in LAND.splitlines()
         if l.startswith("+") and not l.startswith("+++")]
check("S14 r87 landing insertion-only except 3 wiring lines",
      len(removed) == 3 and len(added) == 2083,
      f"-{len(removed)} +{len(added)}")

# ---------------------------------------------------------------- S15
blk = [n for n in ast.walk(tree)
       if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
       and n.func.id == "_pwbind_r87_block"]
no_loads = [c.lineno for c in blk if len(c.args) == 3]
with_loads = [c.lineno for c in blk if len(c.args) == 4]
check("S15 block loads guard is LIVE (4/9 call sites omit)",
      len(blk) == 9 and len(no_loads) == 4 and len(with_loads) == 5,
      f"total={len(blk)} without={no_loads} with={with_loads}")

# ---------------------------------------------------------------- S16
removed_forms = {
    "LINK_WAIT_S const": "PWBIND_R87_LINK_WAIT_S",
    "TAP_WAIT_S const": "PWBIND_R87_TAP_WAIT_S",
    "teardown gone dict": "for nm in (loads or {})",
    "teardown n-in-loads": "or n in (loads or {})",
    "solo None init": "solo_lo, solo_hi = mark(), None",
    "nid fmt_sink guard": "if nid is not None:",
    "DEF fallback": 'entry.get("default_sink_at_start") or',
    "coll_ports guard": "if coll_ports and not all",
}
bad = [k for k, s in removed_forms.items() if s in FR]
check("S16 region free of every removed form", not bad, f"still present: {bad}")
# the loop-head homograph: folded region carries exactly ONE
# `(loads or {})` head (the block's live guard) and ONE direct head
# (the teardown's)
check("S16 loop-head census (block kept / teardown direct)",
      FR.count("for tag, leaf in (loads or {}).items():") == 1 and
      FR.count("for tag, leaf in loads.items():") == 1 and
      BR.count("for tag, leaf in (loads or {}).items():") == 2)
# leaf-guard is gone everywhere in the region
check("S16 leaf = leaf or {} gone from region", "leaf = leaf or {}" not in FR)

bad = [n for n, ok, _ in results if not ok]
print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
sys.exit(1 if bad else 0)
