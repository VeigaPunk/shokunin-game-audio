#!/usr/bin/env python3
"""r75 simplifier: duplicate-literal / duplicate-regex scan (grep-literal, NOT
semantic proof). Reports string constants and re.* patterns appearing >=2
times, with line numbers, optionally restricted to a line window.

Usage: python3 dup_scan.py <file.py> [lo] [hi]
"""
import ast
import sys
from collections import defaultdict
from pathlib import Path

REGEX_FUNCS = {"compile", "search", "match", "findall", "finditer", "sub", "fullmatch"}


def main():
    path = sys.argv[1]
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
    src = Path(path).read_text()
    tree = ast.parse(src)
    lits = defaultdict(list)
    pats = defaultdict(list)
    for node in ast.walk(tree):
        if not hasattr(node, "lineno"):
            continue
        if not (lo <= node.lineno <= hi):
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            v = node.value
            if len(v) >= 4:  # ignore trivial tokens
                lits[v].append(node.lineno)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "re" and node.func.attr in REGEX_FUNCS
                and node.args and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            pats[node.args[0].value].append(node.lineno)
    print(f"== {path} window {lo}..{hi} ==")
    print("-- duplicate string literals (>=2, len>=4) --")
    n = 0
    for v, lines in sorted(lits.items(), key=lambda kv: -len(kv[1])):
        if len(lines) >= 2:
            n += 1
            print(f"  x{len(lines)} {v!r} @ {lines}")
    if not n:
        print("  (none)")
    print("-- duplicate regex patterns (>=2) --")
    n = 0
    for v, lines in sorted(pats.items(), key=lambda kv: -len(kv[1])):
        if len(lines) >= 2:
            n += 1
            print(f"  x{len(lines)} {v!r} @ {lines}")
    if not n:
        print("  (none)")


if __name__ == "__main__":
    main()
