#!/usr/bin/env python3
"""r74 simplifier dead-symbol scan (grep-literal, NOT semantic proof).

Parses the fixture with ast and reports, for a given file:
  - top-level defs / classes with zero references elsewhere in the file
  - argparse flags with zero `args.<name>` uses in the file
  - UPPER_CASE module constants with zero other references
  - names assigned but never read (best-effort, single-assignment locals)

Usage: python3 scan_dead.py <file.py> [...]
"""
import ast
import re
import sys
from pathlib import Path


def scan(path):
    src = Path(path).read_text()
    tree = ast.parse(src)
    lines = src.splitlines()
    out = []

    # top-level function/class defs
    defs = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs.append((node.name, node.lineno))
    for name, lineno in defs:
        refs = len(re.findall(r"\b" + re.escape(name) + r"\b", src))
        if refs <= 1:
            out.append(f"DEAD-DEF {name} def@{lineno} refs={refs}")

    # argparse flags
    flags = re.findall(r'add_argument\("(--[a-z0-9-]+)"', src)
    for flag in flags:
        attr = flag[2:].replace("-", "_")
        uses = len(re.findall(r"\bargs\." + re.escape(attr) + r"\b", src))
        if uses == 0:
            out.append(f"DEAD-FLAG {flag} args.{attr} uses={uses}")

    # module constants
    consts = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and re.fullmatch(r"[A-Z][A-Z0-9_]*", t.id):
                    consts.append((t.id, node.lineno))
    for name, lineno in consts:
        refs = len(re.findall(r"\b" + re.escape(name) + r"\b", src))
        if refs <= 1:
            out.append(f"DEAD-CONST {name} assign@{lineno} refs={refs}")

    # UPPER_CASE constants assigned inside functions (e.g. local aliases)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Assign):
                    for t in sub.targets:
                        if isinstance(t, ast.Name) and re.fullmatch(r"[A-Z][A-Z0-9_]*", t.id):
                            refs = len(re.findall(r"\b" + re.escape(t.id) + r"\b", src))
                            if refs <= 1:
                                out.append(f"DEAD-LOCALCONST {t.id} @{sub.lineno} refs={refs}")

    # simple locals: assigned once in a function, never read again
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        assigned = {}
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Assign):
                for t in sub.targets:
                    if isinstance(t, ast.Name):
                        assigned.setdefault(t.id, sub.lineno)
        for name, lineno in assigned.items():
            if name.startswith("_"):
                continue
            uses = len(re.findall(r"\b" + re.escape(name) + r"\b", src))
            if uses <= 1:
                out.append(f"DEAD-LOCAL {fn.name}:{name} assign@{lineno} refs={uses}")

    return out


def main():
    for path in sys.argv[1:]:
        print(f"== {path} ==")
        rows = scan(path)
        if not rows:
            print("(no dead symbols found)")
        for r in rows:
            print(r)


if __name__ == "__main__":
    main()
