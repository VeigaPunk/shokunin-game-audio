#!/usr/bin/env python3
"""r82-simplifier static reachability proofs (read-only).

Parses the committed fixture (sha256 eb865760…) and asserts, per item, the
call-site facts the deletions rest on. Exit 0 = all proofs hold.
Run:  python3 static-proofs.py <measure_audio.py>
"""
import ast
import collections
import sys

path = sys.argv[1] if len(sys.argv) > 1 else \
    "corpus/fixtures/measure_audio.py"
src = open(path).read()
tree = ast.parse(src)
LO, HI = 14179, 16312          # r82 family block (author anchors)
fails = []


def region(node):
    return LO <= node.lineno <= HI


def call_sites(name):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if (isinstance(f, ast.Name) and f.id == name) or \
               (isinstance(f, ast.Attribute) and f.attr == name):
                kw = {k.arg for k in node.keywords}
                pos = len(node.args)
                out.append((node.lineno, pos, sorted(kw)))
    return sorted(out)


def check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        fails.append(msg)


print("== T1: FFPW_R82_FFPLAY constant ==")
loads = [n.lineno for n in ast.walk(tree)
         if isinstance(n, ast.Name) and n.id == "FFPW_R82_FFPLAY"
         and isinstance(n.ctx, ast.Load)]
check(not loads, f"FFPW_R82_FFPLAY has 0 Load refs (got {loads})")

print("\n== T2: _ffpw_r82_last_node require_linked ==")
sites = call_sites("_ffpw_r82_last_node")
bad = [s for s in sites if "require_linked" in s[2]]
check(len(sites) == 22 and not bad,
      f"{len(sites)} call sites, 0 pass require_linked (bad={bad})")

print("\n== T3: _ffpw_r82_shot env_extra ==")
sites = call_sites("_ffpw_r82_shot")
bad = [s for s in sites if "env_extra" in s[2]]
# 7 AST call sites = d0's rep loop (1 site, 2 executions) + d1..d6
check(len(sites) == 7 and not bad,
      f"{len(sites)} call sites (8 executions), 0 pass env_extra (bad={bad})")

print("\n== T4: _landed_on taps ==")
sites = call_sites("_landed_on")
bad = [s for s in sites if "taps" in s[2]]
check(len(sites) == 8 and not bad,
      f"{len(sites)} call sites, 0 pass taps (bad={bad})")

print("\n== T5: entry-6 legs omit out_path ==")
ent = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and \
            node.name == "ffpw_error_classes_r82_entry":
        ent = node
legs = []
for node in ast.walk(ent):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and \
            node.func.id == "_ffpw_r82_leg":
        kw = {k.arg for k in node.keywords}
        legs.append((node.lineno, "out_path" in kw))
check(len(legs) == 6 and not any(h for _, h in legs),
      f"6 legs, none passes out_path (got {legs})")
# and the reader shape: _ffpw_r82_leg stores out=None without out_path
seg = src.splitlines()
store = [i + 1 for i, ln in enumerate(seg)
         if "_gst_r81_wav_inspect(out_path)" in ln]
store2 = [i + 1 for i, ln in enumerate(seg) if "if out_path else None" in ln]
check(bool(store) and bool(store2),
      f"_ffpw_r82_leg stores out=None without out_path "
      f"(lines {store}+{store2})")

print("\n== T6: superseded predicate (implication) ==")
# find the per-device loop and the any(...) check
has_loop = "if rows.get(dev) != flags:" in src
has_any = "if any(rows.get(d) is None for d in want_flags):" in src
check(has_loop and has_any,
      "per-device mismatch loop precedes the any(...is None) predicate")

print("\n== T7: _star dead store ==")
star_loads = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Name) and n.id == "_star"
              and isinstance(n.ctx, ast.Load)]
check(not star_loads, f"_star has 0 Load refs (got {star_loads})")

print("\n== T8: entry-2 _cap post ==")
sites = call_sites("_cap")
bad = [s for s in sites if "post" in s[2]]
check(not bad, f"no _cap call site passes post (bad={bad}); "
               f"{len(sites)} total _cap calls (both closures)")

print("\n== T10: _ffpw_r82_kill_watch ==")
sites = call_sites("_ffpw_r82_kill_watch")
check(len(sites) == 1 and sites[0][1] == 2,
      f"1 call site with 2 positional args: {sites}")
check('(2.0, "kill_watch", "pump")' in src,
      'sole kill_watch event arg is the literal "pump"')
check('watch={"pump": pump}' in src,
      'same leg passes watch={"pump": pump} (live Popen)')

print("\n== T11: _ffpw_r82_tone_windows path ==")
sites = call_sites("_ffpw_r82_tone_windows")
check(len(sites) == 4, f"4 call sites: {sites}")
for ln, pos, kw in sites:
    line = src.splitlines()[ln - 1]
    print(f"      line {ln}: {line.strip()}")

print("\n== census: module-level names in the region ==")
defined = {}
for node in tree.body:
    if region(node):
        for t in getattr(node, "targets", []) or []:
            for n in ast.walk(t):
                if isinstance(n, ast.Name):
                    defined[n.id] = node.lineno
        if isinstance(node, ast.FunctionDef):
            defined[node.name] = node.lineno
loads = collections.Counter()
for n in ast.walk(tree):
    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
        loads[n.id] += 1
zero = [(n, ln) for n, ln in defined.items() if loads.get(n, 0) == 0]
check(zero == [("FFPW_R82_FFPLAY", 14267)],
      f"only definition-only region name is FFPW_R82_FFPLAY (got {zero})")

print()
if fails:
    print(f"RESULT: {len(fails)} FAILURE(S)")
    sys.exit(1)
print("RESULT: ALL STATIC PROOFS HOLD")
