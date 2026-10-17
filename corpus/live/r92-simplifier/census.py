#!/usr/bin/env python3
"""r92 simplifier — AST census over the audited blob.

Literal fallback (no lsp device answers this tree): module-wide load census of
every module-level name defined inside the r92 block, dead-local census per
function, call-signature census, and duplicate-body scan.

Usage: python3 census.py <module.py> <block_start_line> <block_end_line>
"""
import ast
import sys
from collections import Counter, defaultdict


def name_loads(tree):
    """Count Name(id) loads and Attribute(value=Name) loads module-wide."""
    loads = Counter()
    attr_on = Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            loads[node.id] += 1
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            attr_on[node.value.id] += 1
    return loads, attr_on


def block_defs(tree, lo, hi):
    out = []
    for node in tree.body:
        if lo <= node.lineno <= hi:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.append((node.name, node.lineno, "def", node))
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        out.append((t.id, node.lineno, "assign", node))
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                out.append((node.target.id, node.lineno, "assign", node))
    return out


def call_sites(tree, fname):
    """All Call nodes whose func resolves to Name(fname) or Attribute attr==fname."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id == fname:
                out.append(node)
            elif isinstance(f, ast.Attribute) and f.attr == fname:
                out.append(node)
    return out


def dead_locals(fn):
    """Locals assigned but never loaded inside fn (Name-level, ignores attrs)."""
    assigned = {}
    loaded = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, (ast.Store,)):
                assigned.setdefault(node.id, node.lineno)
            elif isinstance(node.ctx, ast.Load):
                loaded.add(node.id)
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            loaded.add(node.value.id)
        elif isinstance(node, ast.Global) or isinstance(node, ast.Nonlocal):
            for n in node.names:
                loaded.add(n)
    dead = []
    for n, ln in assigned.items():
        if n not in loaded and not n.startswith("_"):
            dead.append((n, ln))
        elif n not in loaded:
            dead.append((n, ln))
    return sorted(dead, key=lambda x: x[1])


def body_key(fn):
    """Normalized body text for duplicate detection (names stripped)."""
    out = []
    for stmt in fn.body:
        for node in ast.walk(stmt):
            if isinstance(node, ast.Name):
                out.append("N")
            elif isinstance(node, ast.Attribute):
                out.append("A." + node.attr)
            elif isinstance(node, ast.Constant):
                out.append(repr(node.value)[:24])
            elif isinstance(node, ast.arg):
                out.append("arg")
            else:
                out.append(type(node).__name__)
    return " ".join(out)


def main():
    path, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    src = open(path).read()
    tree = ast.parse(src)
    loads, attr_on = name_loads(tree)
    defs = block_defs(tree, lo, hi)
    print(f"# module {path}  lines {lo}-{hi}")
    print(f"# module-level defs in block: {len(defs)}")
    zero = []
    for name, ln, kind, node in defs:
        n = loads.get(name, 0) + attr_on.get(name, 0)
        cs = len(call_sites(tree, name)) if kind == "def" else None
        flag = ""
        if kind == "def" and (n == 0 or cs == 0):
            flag = "  <-- ZERO"
            zero.append((name, ln, kind, n, cs))
        print(f"{ln:6d} {kind:6s} {name:40s} loads={n:4d} calls={cs} {flag}")
    print("\n# ZERO-REFERENCE module-level names in block:")
    for row in zero:
        print("  ", row)

    print("\n# dead locals per block function:")
    for node in tree.body:
        if lo <= node.lineno <= hi and isinstance(node, ast.FunctionDef):
            d = dead_locals(node)
            if d:
                print(f"  {node.name} (line {node.lineno}):")
                for n, ln in d:
                    print(f"      {ln:6d} {n}")

    print("\n# call-signature census (block functions with kwargs/defaults):")
    for node in tree.body:
        if lo <= node.lineno <= hi and isinstance(node, ast.FunctionDef):
            args = node.args
            positional = [a.arg for a in args.args]
            defaults = args.defaults
            kwonly = [(a.arg, d is None) for a, d in zip(args.kwonlyargs, args.kw_defaults)]
            has_default = [positional[len(positional) - len(defaults) + i]
                           for i in range(len(defaults))]
            calls = call_sites(tree, node.name)
            if not calls:
                continue
            npos = Counter(len(c.args) for c in calls)
            kwargs_used = Counter(k.arg for c in calls for k in c.keywords if k.arg)
            posonly = npos.get(len(positional), 0)
            if has_default or kwonly:
                print(f"  {node.name} line {node.lineno}: args={positional} "
                      f"defaults={has_default} kwonly={kwonly} ncalls={len(calls)} "
                      f"argcounts={dict(npos)} kwargs={dict(kwargs_used)}")


if __name__ == "__main__":
    main()
