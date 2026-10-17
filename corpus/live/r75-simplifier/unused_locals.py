#!/usr/bin/env python3
"""r75 simplifier: unused-local / unused-parameter scan (AST, file-local).
For each function whose def line is in [lo,hi], reports:
  - params never loaded in the function body
  - local names (Assign/For/With-as/comprehension targets) never loaded
Name loads are counted across the whole file (closures/global reads count).

Usage: python3 unused_locals.py <file.py> [lo] [hi]
"""
import ast
import sys
from pathlib import Path


def main():
    path = sys.argv[1]
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
    tree = ast.parse(Path(path).read_text())
    print(f"== {path} functions in {lo}..{hi} ==")
    hits = 0
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not (lo <= fn.lineno <= hi):
            continue
        params = [a.arg for a in fn.args.args + fn.args.kwonlyargs]
        locals_ = []
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Assign):
                for t in sub.targets:
                    if isinstance(t, ast.Name):
                        locals_.append((t.id, sub.lineno))
            elif isinstance(sub, (ast.For, ast.AsyncFor)):
                for t in ast.walk(sub.target):
                    if isinstance(t, ast.Name):
                        locals_.append((t.id, sub.lineno))
            elif isinstance(sub, ast.withitem) and isinstance(sub.optional_vars, ast.Name):
                locals_.append((sub.optional_vars.id, getattr(sub, "lineno", -1)))
        loads = {n.id for n in ast.walk(fn)
                 if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        stores = {n.id for n in ast.walk(fn)
                  if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
        for p in params:
            if p not in loads and p not in stores and p != "self":
                print(f"  UNUSED-PARAM {fn.name}@{fn.lineno}: {p}")
                hits += 1
        seen = set()
        for name, lineno in locals_:
            if name in seen:
                continue
            seen.add(name)
            if name not in loads:
                print(f"  UNUSED-LOCAL {fn.name}@{fn.lineno}: {name} assign@{lineno}")
                hits += 1
    if not hits:
        print("  (no unused params/locals in window)")


if __name__ == "__main__":
    main()
