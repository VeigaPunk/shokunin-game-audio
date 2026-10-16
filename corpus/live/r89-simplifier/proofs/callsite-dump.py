#!/usr/bin/env python3
"""Explicit call-site dump for the four never-bound r89 params.

Prints every Call node for _pwprof_r89_block / _pwprof_r89_nleg /
_pwprof_r89_play / _pwprof_r89_ensure_player with arg/kwarg binding, and
asserts the never-bound claim for the specific params. Read-only.
"""
import ast
import sys

BASE = sys.argv[1]
src = open(BASE).read()
tree = ast.parse(src)

TARGETS = {
    "_pwprof_r89_block": ["loads", "players"],
    "_pwprof_r89_nleg": ["wd"],
    "_pwprof_r89_play": ["role"],
    "_pwprof_r89_ensure_player": ["wait_s"],
}

sites = {k: [] for k in TARGETS}
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        fn = node.func
        nm = fn.id if isinstance(fn, ast.Name) else \
            (fn.attr if isinstance(fn, ast.Attribute) else None)
        if nm in TARGETS:
            sites[nm].append(node)

for nm, params in TARGETS.items():
    print(f"== {nm} ({len(sites[nm])} call sites) ==")
    for c in sites[nm]:
        args = ", ".join(ast.unparse(a)[:40] for a in c.args)
        kwargs = ", ".join(f"{k.arg}={ast.unparse(k.value)[:40]}"
                           for k in c.keywords)
        print(f"  L{c.lineno}: pos=[{args}] kw=[{kwargs}]")
    # binding check
    for p in params:
        bound = 0
        for c in sites[nm]:
            names = [a.id for a in c.args if isinstance(a, ast.Name)]
            if p in names:
                bound += 1
            if any(k.arg == p for k in c.keywords):
                bound += 1
        # positional binding needs arity info; recompute properly below
        print(f"  -> param {p!r}: kw/name-bound={bound}")
    print()

# arity-correct positional binding check
print("== arity-correct positional binding ==")
import importlib.util
spec = importlib.util.spec_from_file_location("ma", BASE)
# do not execute the module (imports would run); parse signatures instead
sig = {}
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in TARGETS:
        a = node.args
        sig[node.name] = [p.arg for p in a.posonlyargs + a.args]

for nm, params in TARGETS.items():
    counts = {p: 0 for p in params}
    for c in sites[nm]:
        pnames = sig[nm]
        for i, arg in enumerate(c.args):
            if i < len(pnames) and pnames[i] in counts:
                counts[pnames[i]] += 1
        for k in c.keywords:
            if k.arg in counts:
                counts[k.arg] += 1
    print(f"{nm}: {counts}")
