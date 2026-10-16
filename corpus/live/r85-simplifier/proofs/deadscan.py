#!/usr/bin/env python3
"""r85 simplifier — dead-store / unused-name scanner (static, over the pinned blob).

Reports every local Name store whose value is never loaded AFTER the store in
the same function scope, plus every function parameter that is never loaded.
Heuristic; every hit is re-derived by hand in static-proofs.py.
"""
import ast
import re
import sys

BASE = "proofs/base-measure_audio.py"
src = open(BASE, encoding="utf-8").read()
lines = src.splitlines()
tree = ast.parse(src)
start = next(i for i, l in enumerate(lines) if l.startswith("# r85: the pactl"))
end = next(i for i, l in enumerate(lines) if l.startswith("def main():"))

FAMILY = re.compile(r"^(?:_pactlmon_r85_|pactlmon_.*_r85_)")
r85_funcs = {}
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and \
            FAMILY.match(node.name):
        r85_funcs[node.name] = node

print("== store-without-later-load candidates (r85 family) ==")
for name, fn in sorted(r85_funcs.items(), key=lambda kv: kv[1].lineno):
    stores, loads = {}, {}
    for n in ast.walk(fn):
        if isinstance(n, ast.Name):
            if isinstance(n.ctx, ast.Store):
                stores.setdefault(n.id, []).append(n.lineno)
            elif isinstance(n.ctx, ast.Load):
                loads.setdefault(n.id, []).append(n.lineno)
    for k, st in stores.items():
        ld = loads.get(k, [])
        for s in st:
            if not any(l > s for l in ld):
                print(f"  {name} @L{fn.lineno}: store {k} @L{s} "
                      f"(all loads {ld})")

print()
print("== never-loaded parameters (r85 family) ==")
for name, fn in sorted(r85_funcs.items(), key=lambda kv: kv[1].lineno):
    a = fn.args
    allargs = [x.arg for x in a.posonlyargs] + [x.arg for x in a.args] + \
              [x.arg for x in a.kwonlyargs]
    loads = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            loads.add(n.id)
    for x in allargs:
        if x not in loads:
            print(f"  {name} @L{fn.lineno}: param `{x}` never loaded")

print()
print("== nested (entry-local) defs: params never loaded ==")
for name, fn in sorted(r85_funcs.items(), key=lambda kv: kv[1].lineno):
    for sub in ast.walk(fn):
        if isinstance(sub, ast.FunctionDef) and sub is not fn:
            a = sub.args
            allargs = [x.arg for x in a.posonlyargs] + \
                      [x.arg for x in a.args] + \
                      [x.arg for x in a.kwonlyargs]
            loads = set()
            for n in ast.walk(sub):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    loads.add(n.id)
            for x in allargs:
                if x not in loads:
                    print(f"  {name}.{sub.name} @L{sub.lineno}: "
                          f"param `{x}` never loaded")

print()
print("== nested (entry-local) defs: stores without later load ==")
for name, fn in sorted(r85_funcs.items(), key=lambda kv: kv[1].lineno):
    for sub in ast.walk(fn):
        if isinstance(sub, ast.FunctionDef) and sub is not fn:
            stores, loads = {}, {}
            for n in ast.walk(sub):
                if isinstance(n, ast.Name):
                    if isinstance(n.ctx, ast.Store):
                        stores.setdefault(n.id, []).append(n.lineno)
                    elif isinstance(n.ctx, ast.Load):
                        loads.setdefault(n.id, []).append(n.lineno)
            for k, st in stores.items():
                ld = loads.get(k, [])
                for s in st:
                    if not any(l > s for l in ld):
                        print(f"  {name}.{sub.name} @L{sub.lineno}: "
                              f"store {k} @L{s} (all loads {ld})")

print()
print("== module-level r85 names: zero whole-file references ==")
for i in range(start, end):
    m = re.match(r"^(?:def )?([A-Za-z_][A-Za-z0-9_]*)\s*[=(]", lines[i])
    if m and not lines[i].startswith((" ", "\t", "#")):
        nm = m.group(1)
        if nm in ("def", "return", "if", "for", "while", "try", "with"):
            continue
        uses = len(re.findall(rf"\b{re.escape(nm)}\b", src)) - 1
        if uses == 0:
            print(f"  {nm} @L{i+1} uses=0")
