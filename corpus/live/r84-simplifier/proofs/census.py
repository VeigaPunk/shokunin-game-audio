#!/usr/bin/env python3
"""r84 simplifier census — static census over the commit-pinned r84 block.

Input : proofs/base-measure_audio.py  (byte-identical to fbe65713:corpus/fixtures/measure_audio.py)
Output: census.txt (defs, params, call sites, write-only locals, constants, wiring)
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

# r84 region: the family block header through the line before `def main():`
start = next(i for i, l in enumerate(lines) if l.startswith("# r84: the aplay"))
# back up to the "# ===" banner
while not lines[start].startswith("# ===="):
    start -= 1
end = next(i for i, l in enumerate(lines) if l.startswith("def main():"))
print(f"[region] r84 block lines {start+1}..{end} ({end-start} lines)", file=sys.stdout)
out = io.StringIO()


def p(*a):
    print(*a, file=out)


FAMILY = re.compile(r"^(?:_alsapw_r84_|alsapw_.*_r84_)")

funcs = {}
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        funcs[node.name] = node

r84_funcs = {n: f for n, f in funcs.items() if FAMILY.match(n)}
p(f"== r84 functions: {len(r84_funcs)}")

# ---------- call sites (whole file, by name) ----------
calls = defaultdict(list)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        f = node.func
        nm = f.id if isinstance(f, ast.Name) else (
            f.attr if isinstance(f, ast.Attribute) else None)
        if nm:
            calls[nm].append(node)

# ---------- per-function census ----------
def store_load_census(fn):
    stores = defaultdict(int)
    loads = defaultdict(int)
    for n in ast.walk(fn):
        if isinstance(n, ast.Name):
            if isinstance(n.ctx, ast.Store):
                stores[n.id] += 1
            elif isinstance(n.ctx, ast.Load):
                loads[n.id] += 1
    return stores, loads


p("== per-function: args, defaults, arg-usage, call sites, write-only locals")
for name in sorted(r84_funcs):
    fn = r84_funcs[name]
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
    argloads = {x: loads.get(x, 0) for x in allargs}
    unused = [x for x in allargs if loads.get(x, 0) == 0]
    wo = sorted(k for k, v in stores.items()
                if v > 0 and loads.get(k, 0) == 0 and k not in allargs)
    ncalls = len(calls.get(name, []))
    p(f"  {name}  L{fn.lineno}  args={allargs}  defaults={defmap}")
    p(f"      arg_loads={argloads}  unused_args={unused}  callsites={ncalls}")
    if wo:
        p(f"      WRITE-ONLY-LOCALS={wo}")

# ---------- call-site arg supply census ----------
p("\n== call-site argument supply census (r84 funcs)")
for name in sorted(r84_funcs):
    fn = r84_funcs[name]
    a = fn.args
    allargs = [x.arg for x in a.posonlyargs] + [x.arg for x in a.args] + \
              [x.arg for x in a.kwonlyargs]
    if not allargs:
        continue
    supplied = defaultdict(int)
    n = 0
    for c in calls.get(name, []):
        n += 1
        for arg in c.args:
            if isinstance(arg, ast.Starred):
                supplied["<star>"] += 1
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
p("\n== ALSAPW_R84_* constant usage")
for node in tree.body:
    if isinstance(node, ast.Assign) and node.targets:
        t = node.targets[0]
        if isinstance(t, ast.Name) and t.id.startswith("ALSAPW_R84"):
            uses = len(re.findall(rf"\b{t.id}\b", src)) - 1
            p(f"  {t.id} @L{node.lineno} uses={uses}")
for node in tree.body:
    if isinstance(node, ast.AnnAssign):
        pass

# ---------- module-level names defined in r84 region, use census ----------
p("\n== names defined in r84 region: use census")
for i in range(start, end):
    m = re.match(r"^(?:def |class )?([A-Za-z_][A-Za-z0-9_]*)\s*[=(]", lines[i])
    if m and not lines[i].startswith((" ", "\t", "#")):
        nm = m.group(1)
        if nm in ("def", "return", "if", "for", "while", "try", "with"):
            continue
        uses = len(re.findall(rf"\b{re.escape(nm)}\b", src)) - 1
        p(f"  {nm} @L{i+1} uses={uses}")

# ---------- helpers referenced nowhere ----------
p("\n== r84 defs with zero call sites (name-based, whole file)")
for name in sorted(r84_funcs):
    if name == "main":
        continue
    if len(calls.get(name, [])) == 0:
        p(f"  ZERO-CALLS: {name} @L{r84_funcs[name].lineno}")

# ---------- entry wiring ----------
p("\n== wiring: --probe-alsapw-r84 and entry names")
for i, l in enumerate(lines):
    if "alsapw-r84" in l or "alsapw_r84" in l:
        if "probe" in l or "choices" in l or "mode" in l or "suffix" in l:
            p(f"  L{i+1}: {l.strip()}")
for i, l in enumerate(lines):
    if "alsapw_dev_lattice_r84" in l or "alsapw_pw_args_r84" in l or \
       "alsapw_pulseprop_r84" in l or "alsapw_pactl_write_r84" in l or \
       "alsapw_monstream_r84" in l or "alsapw_negctl_r84" in l:
        p(f"  L{i+1}: {l.strip()}")

# ---------- entry registry: which r84 entries are dispatched ----------
p("\n== ENTRY registry (name = entry) for r84")
for i, l in enumerate(lines):
    if re.search(r"alsapw_\w+_r84_entry", l) and "def " not in l:
        p(f"  L{i+1}: {l.strip()}")

open("proofs/census.txt", "w").write(out.getvalue())
print(out.getvalue())
