#!/usr/bin/env python3
"""Call-signature census for the r90 helpers: how many positional args and
which kwargs each call site supplies. Proves 'never supplied' claims."""
import ast
import sys
from collections import Counter

path = sys.argv[1]
tree = ast.parse(open(path).read())
lines = open(path).read().splitlines()
start = next(i for i, l in enumerate(lines, 1) if l.startswith("# ROUND 90"))
end = next(i for i, l in enumerate(lines, 1) if l.startswith("def main():"))

TARGETS = [n for n in sys.argv[2:]]
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and \
            node.func.id in TARGETS:
        npos = len(node.args)
        kw = sorted(k.arg for k in node.keywords)
        print(f"line {node.lineno:6d}  {node.func.id:30s} "
              f"pos={npos} kw={kw}")

print("\n-- positional-arg histogram --")
hist = Counter()
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and \
            node.func.id in TARGETS:
        hist[(node.func.id, len(node.args))] += 1
for k in sorted(hist):
    print(f"  {k[0]:30s} pos={k[1]}  x{hist[k]}")

print("\n-- 'pre' key writes in the r90 region --")
for i, l in enumerate(lines, 1):
    if start <= i <= end and ("[\"pre\"]" in l or "['pre']" in l):
        print(f"  {i}: {l.strip()}")
