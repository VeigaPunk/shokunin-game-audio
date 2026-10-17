#!/usr/bin/env python3
"""Reference census for the r90 block of measure_audio.py.

Prints, for every module-level name defined in the r90 region:
  - total textual references outside its own def line
  - AST-level Name/Attribute loads and Call sites with keyword args
Also prints per-parameter keyword-arg usage for r90 functions.
"""
import ast
import sys
from collections import Counter, defaultdict

path = sys.argv[1]
src = open(path).read()
tree = ast.parse(src)
lines = src.splitlines()

# r90 region: from the 'ROUND 90' banner to the end of wpformat_r90_entry
start = None
for i, ln in enumerate(lines, 1):
    if ln.startswith("# ROUND 90"):
        start = i
        break
end = None
for i, ln in enumerate(lines, 1):
    if ln.startswith("def main():"):
        end = i
        break
print(f"region: {start}..{end}")

region_names = {}
for node in tree.body:
    if start <= node.lineno <= end:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            region_names[node.name] = ("def", node)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    region_names[t.id] = ("assign", node)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            region_names[node.target.id] = ("annassign", node)

print(f"module-level names in region: {len(region_names)}")

# collect all loads in the whole file
loads = Counter()
call_kwargs = defaultdict(Counter)
calls = defaultdict(list)
for node in ast.walk(tree):
    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
        loads[node.id] += 1
    if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
        loads["." + node.attr] += 1
    if isinstance(node, ast.Call):
        f = node.func
        nm = f.id if isinstance(f, ast.Name) else (
            "." + f.attr if isinstance(f, ast.Attribute) else "?")
        calls[nm].append(node.lineno)
        for kw in node.keywords:
            call_kwargs[nm][kw.arg] += 1

# references to region names from anywhere (AST loads)
print("\n== region module-level names: load counts (whole file) ==")
for nm, (kind, node) in sorted(region_names.items()):
    n = loads.get(nm, 0)
    ncall = len(calls.get(nm, []))
    flag = "  <== ZERO LOADS" if n == 0 else ""
    print(f"{nm:34s} {kind:9s} loads={n:4d} callsites={ncall:3d}{flag}")

print("\n== r90 function call sites: line numbers ==")
for nm in sorted(region_names):
    if region_names[nm][0] == "def" and nm.startswith("_"):
        ls = calls.get(nm, [])
        kw = call_kwargs.get(nm, Counter())
        print(f"{nm:34s} n={len(ls):3d} kwargs={dict(kw)} lines={ls}")

print("\n== parameters never passed as kwargs (def-side vs call-side) ==")
for nm, (kind, node) in sorted(region_names.items()):
    if kind != "def":
        continue
    args = node.args
    names = [a.arg for a in args.args] + [a.arg for a in args.kwonlyargs]
    used_kw = set(call_kwargs.get(nm, {}))
    pos = [a.arg for a in args.args]
    positional_calls = 0
    for ln in calls.get(nm, []):
        # find the call node at that line to count positional args
        pass
    unused = [a for a in names if a not in used_kw]
    print(f"{nm:34s} args={names} kwargs_used={sorted(used_kw)} never_kw={unused}")
