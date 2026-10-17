#!/usr/bin/env python3
"""r96 simplifier — literal-fallback reference census (no lsp device exists
in this seat; AST + grep only, never presented as semantic proof).

Reports, per fixture variant:
  * top-level def/assign counts and duplicate top-level names;
  * every `_attr_leg(<literal>, ...)` cell (the duplicate-cell proof);
  * every `_pulsecli_r96_row(...)` call site with its pid argument;
  * Name-load census for the fold-touched helpers.

Usage: census.py FIXTURE.py
"""
import ast
import sys
from collections import Counter

WATCH = ("_pulsecli_r96_row", "_pulsecli_r96_row_view", "_pulsecli_r96_run",
         "_pulsecli_r96_stream_leg")


def main():
    path = sys.argv[1]
    src = open(path).read()
    tree = ast.parse(src)
    loads = Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            loads[node.id] += 1
    top_defs = [n.name for n in tree.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    top_assigns = [t.id for n in tree.body if isinstance(n, ast.Assign)
                   for t in n.targets if isinstance(t, ast.Name)]
    dupes = sorted(n for n, c in Counter(top_defs + top_assigns).items()
                   if c > 1)
    cells = []
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        nm = fn.id if isinstance(fn, ast.Name) else None
        if nm == "_attr_leg" and node.args and \
                isinstance(node.args[0], ast.Constant):
            cells.append((node.args[0].value, node.lineno))
        if nm == "_pulsecli_r96_row":
            key = ast.unparse(node.args[1]) if len(node.args) > 1 else "?"
            rows.append((node.lineno, key))
    print(f"# {path}")
    print(f"top-level defs={len(top_defs)} assigns={len(top_assigns)} "
          f"duplicate-top-level-names={dupes}")
    for w in WATCH:
        print(f"  {w}: loads={loads.get(w, 0)}")
    print(f"  _attr_leg cells ({len(cells)}):")
    for name, ln in cells:
        print(f"    {ln}: {name}")
    print(f"  _pulsecli_r96_row call sites ({len(rows)}):")
    for ln, key in rows:
        print(f"    {ln}: pid_key={key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
