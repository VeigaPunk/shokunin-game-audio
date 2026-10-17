#!/usr/bin/env python3
"""Call-graph reachability census for the r91 entries: from each entry
function, which module-level functions are reachable, and does the reachable
set contain any literal "pw-play" invocation?

This is the literal fallback for the `lsp` device (none answers this tree):
an AST call graph, not a semantic reference query.
"""
import ast
import re
import sys
from collections import defaultdict

path = sys.argv[1]
src = open(path).read()
tree = ast.parse(src)
funcs = {n.name: n for n in tree.body
         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def callees(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id in funcs:
                out.add(f.id)
    return out


ENTRIES = [n for n in funcs if n.endswith("_r91_entry")]
for e in sorted(ENTRIES):
    seen, stack = set(), [e]
    while stack:
        f = stack.pop()
        if f in seen:
            continue
        seen.add(f)
        stack.extend(callees(funcs[f]) - seen)
    hits = sorted(f for f in seen if "pw-play" in ast.unparse(funcs[f]))
    print(f"{e}: reachable module functions={len(seen)} "
          f"pw-play-reaching={hits}")
    if hits:
        for h in hits:
            for i, l in enumerate(ast.unparse(funcs[h]).splitlines(), 1):
                if "pw-play" in l:
                    print(f"    {h}: {l.strip()}")
