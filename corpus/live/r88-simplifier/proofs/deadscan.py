#!/usr/bin/env python3
"""Dead-store / unused-local census for the r88 region of the pinned blob.

Reports, per r88 function: names assigned but never loaded afterwards in
the same function, names loaded before any assignment (dead inits), and
for each function parameter whether any call site binds it.
"""
import ast
import re

SRC = "base-measure_audio.py"
text = open(SRC, encoding="utf-8").read()
lines = text.splitlines()
tree = ast.parse(text)
R88_START, R88_END = 27507, 29252

region_funcs = [n for n in tree.body
                if isinstance(n, ast.FunctionDef)
                and R88_START <= n.lineno <= R88_END]

def name_of(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return None
    if isinstance(node, ast.Subscript):
        return name_of(node.value)
    if isinstance(node, ast.Tuple):
        return None
    return None

print("== assigned-but-never-loaded locals (per r88 function) ==")
for fn in region_funcs:
    stores, loads = {}, set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                stores.setdefault(node.id, []).append(node.lineno)
            elif isinstance(node.ctx, ast.Load):
                loads.add(node.id)
    dead = {k: v for k, v in stores.items()
            if k not in loads and not k.startswith("_")}
    # locals only (module-level names excluded)
    modnames = {t.id for n in tree.body if isinstance(n, ast.Assign)
                for t in n.targets if isinstance(t, ast.Name)}
    dead = {k: v for k, v in dead.items() if k not in modnames}
    if dead:
        print(f"{fn.name} (: {fn.lineno}):")
        for k, v in sorted(dead.items(), key=lambda kv: kv[1][0]):
            print(f"    {k:24s} stores at {v}")

print("\n== parameters never bound at any call site ==")
for fn in region_funcs:
    if fn.name.startswith("_btwit_r88") or fn.name.endswith("_r88_entry"):
        params = [a.arg for a in fn.args.args]
        if not params:
            continue
        used_kw, used_pos = set(), 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and \
                    isinstance(node.func, ast.Name) and \
                    node.func.id == fn.name:
                used_pos = max(used_pos, len(node.args))
                for k in node.keywords:
                    used_kw.add(k.arg)
        never = [p for i, p in enumerate(params)
                 if i >= used_pos and p not in used_kw and
                 not (p == "self")]
        # a param with a default may be omitted intentionally
        ndef = len(fn.args.defaults)
        print(f"{fn.name:32s} params={params} defaults={ndef} "
              f"maxpos={used_pos} kw={sorted(used_kw)} "
              f"never_bound={never}")

print("\n== _frames_cache sites (whole file) ==")
for i, ln in enumerate(lines, 1):
    if "_frames_cache" in ln:
        print(f"  :{i} {ln.strip()}")

print("\n== `(loads or {})` / `leaf = leaf or {}` sites (whole file) ==")
for i, ln in enumerate(lines, 1):
    if "(loads or {})" in ln or "leaf = leaf or {}" in ln:
        print(f"  :{i} {ln.strip()}")
