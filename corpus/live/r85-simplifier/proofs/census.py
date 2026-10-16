#!/usr/bin/env python3
"""r85 simplifier census — static census over the commit-pinned r85 block.

Input : proofs/base-measure_audio.py  (byte-identical to
        2a49d540:corpus/fixtures/measure_audio.py)
Output: census.txt (defs, params, call sites, write-only locals, constants,
        wiring, entry registry)
Read-only: never touches the tracked tree.
"""
import ast
import io
import re
import sys
from collections import defaultdict

BASE = "proofs/base-measure_audio.py"
src = open(BASE, encoding="utf-8").read()
lines = src.splitlines()
tree = ast.parse(src)

# r85 region: the family block header through the line before `def main():`
start = next(i for i, l in enumerate(lines) if l.startswith("# r85: the pactl"))
end = next(i for i, l in enumerate(lines) if l.startswith("def main():"))
out = io.StringIO()


def p(*a):
    print(*a, file=out)


p(f"[region] r85 block lines {start+1}..{end} ({end-start} lines)")

FAMILY = re.compile(r"^(?:_pactlmon_r85_|pactlmon_.*_r85_)")

funcs = {}
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        funcs[node.name] = node

r85_funcs = {n: f for n, f in funcs.items() if FAMILY.match(n)}
p(f"== r85 functions: {len(r85_funcs)}")

# ---------- call sites (whole file, by name) ----------
calls = defaultdict(list)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        f = node.func
        nm = f.id if isinstance(f, ast.Name) else (
            f.attr if isinstance(f, ast.Attribute) else None)
        if nm:
            calls[nm].append(node)


def store_load_census(fn):
    stores = defaultdict(list)
    loads = defaultdict(list)
    for n in ast.walk(fn):
        if isinstance(n, ast.Name):
            if isinstance(n.ctx, ast.Store):
                stores[n.id].append(n.lineno)
            elif isinstance(n.ctx, ast.Load):
                loads[n.id].append(n.lineno)
    return stores, loads


p("== per-function: args, defaults, arg-usage, call sites, write-only locals")
for name in sorted(r85_funcs):
    fn = r85_funcs[name]
    a = fn.args
    posonly = [x.arg for x in a.posonlyargs]
    pos = [x.arg for x in a.args]
    kwonly = [x.arg for x in a.kwonlyargs]
    allargs = posonly + pos + kwonly
    ndef = len(a.defaults)
    defmap = {}
    for i, d in enumerate(a.defaults):
        defmap[pos[len(pos) - ndef + i]] = ast.unparse(d)
    for d, kw in zip(a.kw_defaults, kwonly):
        if d is not None:
            defmap[kw] = ast.unparse(d)
    stores, loads = store_load_census(fn)
    argloads = {x: len(loads.get(x, [])) for x in allargs}
    unused = [x for x in allargs if not loads.get(x)]
    wo = sorted(k for k, v in stores.items()
                if v and not loads.get(k) and k not in allargs)
    ncalls = len(calls.get(name, []))
    p(f"  {name}  L{fn.lineno}  args={allargs}  defaults={defmap}")
    p(f"      arg_loads={argloads}  unused_args={unused}  callsites={ncalls}")
    if wo:
        p(f"      WRITE-ONLY-LOCALS={wo}")
    # store-after-last-load locals (dead store tail)
    tail = []
    for k, st in stores.items():
        if k in allargs:
            continue
        ld = loads.get(k, [])
        if st and (not ld or max(st) > max(ld)):
            tail.append((k, st, ld))
    if tail:
        p(f"      STORE-AFTER-LAST-LOAD={sorted(tail)}")

# ---------- call-site arg supply census ----------
p("\n== call-site argument supply census (r85 funcs)")
for name in sorted(r85_funcs):
    fn = r85_funcs[name]
    a = fn.args
    allargs = [x.arg for x in a.posonlyargs] + [x.arg for x in a.args] + \
              [x.arg for x in a.kwonlyargs]
    if not allargs:
        continue
    supplied = defaultdict(int)
    n = 0
    for c in calls.get(name, []):
        n += 1
        npos = len([x for x in c.args if not isinstance(x, ast.Starred)])
        for i, x in enumerate(a.posonlyargs + a.args):
            if i < npos:
                supplied[x.arg] += 1
        for k in c.keywords:
            if k.arg is None:
                supplied["<kwstar>"] += 1
            else:
                supplied[k.arg] += 1
    p(f"  {name}: {n} calls; supply={dict(supplied)}")

# ---------- constants ----------
p("\n== PACTLMON_R85_* constant usage (whole file, word-boundary)")
for node in tree.body:
    if isinstance(node, ast.Assign) and node.targets:
        t = node.targets[0]
        if isinstance(t, ast.Name) and t.id.startswith("PACTLMON_R85"):
            uses = len(re.findall(rf"\b{t.id}\b", src)) - 1
            p(f"  {t.id} @L{node.lineno} uses={uses}")

# ---------- module-level names defined in r85 region, use census ----------
p("\n== names defined in r85 region: use census")
for i in range(start, end):
    m = re.match(r"^(?:def |class )?([A-Za-z_][A-Za-z0-9_]*)\s*[=(]", lines[i])
    if m and not lines[i].startswith((" ", "\t", "#")):
        nm = m.group(1)
        if nm in ("def", "return", "if", "for", "while", "try", "with"):
            continue
        uses = len(re.findall(rf"\b{re.escape(nm)}\b", src)) - 1
        p(f"  {nm} @L{i+1} uses={uses}")

# ---------- helpers referenced nowhere ----------
p("\n== r85 defs with zero call sites (name-based, whole file)")
for name in sorted(r85_funcs):
    if len(calls.get(name, [])) == 0:
        p(f"  ZERO-CALLS: {name} @L{r85_funcs[name].lineno}")

# ---------- entry wiring ----------
p("\n== wiring: --probe-pactlmon-r85 and entry names")
for i, l in enumerate(lines):
    if "pactlmon-r85" in l or "pactlmon_r85" in l:
        if "probe" in l or "choices" in l or "mode" in l or "suffix" in l:
            p(f"  L{i+1}: {l.strip()[:220]}")

p("\n== ENTRY registry (name = entry) for r85")
for i, l in enumerate(lines):
    if re.search(r"pactlmon_\w+_r85_entry", l) and "def " not in l:
        p(f"  L{i+1}: {l.strip()[:220]}")

# ---------- dead-guard / dead-payload scan ----------
p("\n== `or {}` / `or []` guard sites in the r85 region")
for i in range(start, end):
    if re.search(r"or \{\}|or \[\]|or \(\)", lines[i]):
        p(f"  L{i+1}: {lines[i].strip()}")

open("proofs/census.txt", "w").write(out.getvalue())
print(out.getvalue())
