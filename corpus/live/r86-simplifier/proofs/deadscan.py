#!/usr/bin/env python3
"""r86 simplifier static census: reachability of r86-block defs/consts,
dead params, dead stores — over the commit-pinned blob only."""
import ast
import sys
from collections import Counter, defaultdict

BASE = "base-measure_audio.py"
LO, HI = 23730, 25451          # r86 block, 1-based inclusive (pinned blob)

src = open(BASE, encoding="utf-8").read()
tree = ast.parse(src)
lines = src.splitlines()


def in_block(node):
    return LO <= node.lineno <= HI


def name_loads(root):
    c = Counter()
    for n in ast.walk(root):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            c[n.id] += 1
        elif isinstance(n, ast.Attribute):
            pass
    return c


# ---- whole-file call census ----------------------------------------------
calls = Counter()
for n in ast.walk(tree):
    if isinstance(n, ast.Call):
        f = n.func
        if isinstance(f, ast.Name):
            calls[f.id] += 1
        elif isinstance(f, ast.Attribute):
            calls[f.attr] += 1

# ---- module-level names defined in the r86 block -------------------------
defs = []
for n in tree.body:
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and in_block(n):
        defs.append(("def", n.name, n.lineno, n.end_lineno))
    elif isinstance(n, ast.Assign) and in_block(n):
        for t in n.targets:
            if isinstance(t, ast.Name):
                defs.append(("const", t.id, n.lineno, n.end_lineno))
    elif isinstance(n, ast.AnnAssign) and in_block(n):
        if isinstance(n.target, ast.Name):
            defs.append(("const", n.target.id, n.lineno, n.end_lineno))

print("== module-level r86 names: call/load census (whole file) ==")
for kind, name, lo, hi in defs:
    n_loads = sum(1 for x in ast.walk(tree)
                  if isinstance(x, ast.Name) and x.id == name
                  and isinstance(x.ctx, ast.Load))
    n_calls = calls.get(name, 0)
    # exclude loads that are just the def itself / decorators
    print(f"{kind:5s} {name:32s} L{lo:>6}-{hi:<6} loads={n_loads:<3} "
          f"calls={n_calls}")

# ---- params never loaded in their function body --------------------------
print("\n== params with zero loads in own function body (r86 block) ==")
for n in ast.walk(tree):
    if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    if not in_block(n):
        continue
    body_loads = name_loads(n)
    for a in (n.args.args + n.args.kwonlyargs + n.args.posonlyargs):
        if a.arg in ("self", "cls"):
            continue
        if body_loads[a.arg] == 0:
            print(f"DEAD PARAM {n.name} L{n.lineno}: '{a.arg}' "
                  f"(line {a.lineno})")

# ---- dead stores inside r86 functions ------------------------------------
print("\n== name stores with no later load in same function (r86 block) ==")
for n in ast.walk(tree):
    if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    if not in_block(n):
        continue
    # collect loads with positions
    loads = []
    for x in ast.walk(n):
        if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load):
            loads.append((x.lineno, x.col_offset, x.id))
    for x in ast.walk(n):
        if not isinstance(x, ast.Name) or not isinstance(x.ctx, ast.Store):
            continue
        later = [l for l in loads
                 if (l[0], l[1]) > (x.lineno, x.col_offset) and l[2] == x.id]
        if not later:
            print(f"DEAD STORE {n.name} L{x.lineno}: '{x.id}'")

# ---- r86 constant/leg-key census -----------------------------------------
print("\n== r86 block: names bound at module level, full-file loads ==")
for kind, name, lo, hi in defs:
    if not name.startswith(("PWCTL_R86", "_PWCTL_R86")):
        continue
    occ = [i + 1 for i, ln in enumerate(lines) if name in ln]
    print(f"{name:28s} occurrences={len(occ)} lines={occ}")
