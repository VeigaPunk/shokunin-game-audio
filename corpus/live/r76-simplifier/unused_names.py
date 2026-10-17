#!/usr/bin/env python3
"""AST scan: local bindings never loaded in their own function scope.

Structural (semantic-ish) evidence only: a name bound by assignment or
tuple-unpacking inside a function that is never read as a Name load in
that function body (nested scopes included, since a nested scope load
still uses the binding) is dead weight.  Does not claim anything about
module-level or receipt-visible state.
"""
import ast
import sys
from pathlib import Path

src = Path(sys.argv[1]).read_text()
tree = ast.parse(src)

TARGET_ONLY = sys.argv[2] if len(sys.argv) > 2 else None


def loads_and_stores(fn):
    """(loaded names, stored names) for the function's own body."""
    loaded, stored = set(), set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                loaded.add(node.id)
            elif isinstance(node.ctx, ast.Store):
                stored.add(node.id)
        elif isinstance(node, ast.Global) or isinstance(node, ast.Nonlocal):
            loaded.update(node.names)
    return loaded, stored


def report(fn, path):
    loaded, stored = loads_and_stores(fn)
    args = {a.arg for a in fn.args.args + fn.args.kwonlyargs}
    if fn.args.vararg:
        args.add(fn.args.vararg.arg)
    if fn.args.kwarg:
        args.add(fn.args.kwarg.arg)
    dead = sorted(stored - loaded)
    for name in dead:
        print(f"{path}:{fn.lineno} {fn.name}: bound-but-never-loaded: {name}")


for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if TARGET_ONLY and not node.name.startswith(TARGET_ONLY):
            continue
        report(node, Path(sys.argv[1]).name)
