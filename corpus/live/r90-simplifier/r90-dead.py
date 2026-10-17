#!/usr/bin/env python3
"""Dead-weight pass over the r90 region: unused params, unused locals,
unreachable-after-return, constant-None recorded keys."""
import ast, sys
from collections import defaultdict

path = sys.argv[1]
src = open(path).read()
tree = ast.parse(src)
lines = src.splitlines()
start = next(i for i, l in enumerate(lines, 1) if l.startswith("# ROUND 90"))
end = next(i for i, l in enumerate(lines, 1) if l.startswith("def main():"))

def region(node):
    return start <= node.lineno <= end

print("=== 1. function params never referenced in body ===")
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and region(node):
        params = {a.arg for a in node.args.args + node.args.kwonlyargs}
        used = set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
                used.add(sub.id)
            if isinstance(sub, ast.arg) and sub is not None:
                pass
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                pass
        dead = sorted(p for p in params if p not in used)
        if dead:
            print(f"  {node.name:34s} never-referenced params: {dead}")

print("\n=== 2. locals assigned but never loaded ===")
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and region(node):
        stores = defaultdict(list)
        loads = set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name):
                if isinstance(sub.ctx, ast.Store):
                    stores[sub.id].append(sub.lineno)
                elif isinstance(sub.ctx, ast.Load):
                    loads.add(sub.id)
        dead = {k: v for k, v in stores.items() if k not in loads}
        if dead:
            print(f"  {node.name:34s} {dead}")

print("\n=== 3. statements after a bare return/raise in the same body ===")
def check_body(body, where):
    for i, st in enumerate(body):
        if isinstance(st, (ast.Return, ast.Raise, ast.Continue, ast.Break)):
            if i + 1 < len(body):
                print(f"  {where}: line {st.lineno} terminator, then "
                      f"line {body[i+1].lineno}")
for node in ast.walk(tree):
    if region(node) and hasattr(node, "body"):
        check_body(node.body, f"{type(node).__name__}@{getattr(node,'lineno','?')}")

print("\n=== 4. dict-literal keys with constant value in legs[*] = {...} ===")
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and region(node):
        tgt = node.targets[0]
        name = ast.unparse(tgt)
        if isinstance(node.value, ast.Dict):
            for k, v in zip(node.value.keys, node.value.values):
                if k is None:
                    continue
                ks = ast.unparse(k)
                if isinstance(v, ast.Constant):
                    print(f"  line {node.lineno}: {name}[{ks}] = {v.value!r}")

print("\n=== 5. string literal keys written into legs dicts anywhere ===")
writes = defaultdict(set)
for node in ast.walk(tree):
    if isinstance(node, ast.Subscript) and region(node) and \
            isinstance(node.ctx, ast.Store):
        if isinstance(node.value, ast.Name):
            writes[node.value.id].add(ast.unparse(node.slice))
for k in sorted(writes):
    print(f"  {k}: {sorted(writes[k])}")
