#!/usr/bin/env python3
"""r83-simplifier — rigorous per-parameter supply census + structurally
constant branch census over the r83 family block.

Read-only. Run:  python3 params.py corpus/fixtures/measure_audio.py
"""
import ast
import sys

BLK_START = 16315
BLK_END = 18702

SRC = sys.argv[1] if len(sys.argv) > 1 else "corpus/fixtures/measure_audio.py"
text = open(SRC).read()
tree = ast.parse(text)


def inblk(node):
    return BLK_START <= node.lineno <= BLK_END


funcs = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and inblk(node):
        funcs[node.name] = node

print("== rigorous per-parameter supply census (r83 block helpers) ==")
for nm in sorted(funcs, key=lambda n: funcs[n].lineno):
    fn = funcs[nm]
    params = [a.arg for a in fn.args.args]
    kwonly = [a.arg for a in fn.args.kwonlyargs]
    defaults = fn.args.defaults
    ndef = len(defaults)
    defaulted = set(params[len(params) - ndef:]) if ndef else set()
    kwdefaulted = {a.arg for a, d in
                   zip(fn.args.kwonlyargs, fn.args.kw_defaults) if d}
    sites = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == nm]
    star = False
    supplied = {}
    for c in sites:
        for i, a in enumerate(c.args):
            if isinstance(a, ast.Starred):
                star = True
            elif i < len(params):
                supplied[params[i]] = supplied.get(params[i], 0) + 1
        for kw in c.keywords:
            if kw.arg is None:
                star = True
            else:
                supplied[kw.arg] = supplied.get(kw.arg, 0) + 1
    overridable = defaulted | kwdefaulted
    never = [p for p in (params + kwonly)
             if p in overridable and p not in supplied]
    if never or star:
        print(f"  {nm}")
        print(f"      sites={len(sites)}  star-args={star}")
        print(f"      defaulted-but-never-supplied: {never}")
        print(f"      supplied counts: "
              f"{ {k: v for k, v in sorted(supplied.items())} }")

print("\n== structurally constant / trivially-true-if branch census ==")
CONST_TESTS = (ast.Constant,)
for nm, fn in sorted(funcs.items(), key=lambda kv: kv[1].lineno):
    for n in ast.walk(fn):
        if isinstance(n, ast.If):
            t = n.test
            if isinstance(t, CONST_TESTS):
                print(f"  {nm}@{n.lineno}: literal-constant test {t.value!r}")
            elif isinstance(t, ast.Name) and isinstance(t.ctx, ast.Load):
                # a bare name test: flag when the name is a parameter that
                # is never supplied non-falsy anywhere (needs manual read)
                print(f"  {nm}@{n.lineno}: bare-name test {t.id!r}")

print("\n== `while` / `for` with constant bounds ==")
for nm, fn in sorted(funcs.items(), key=lambda kv: kv[1].lineno):
    for n in ast.walk(fn):
        if isinstance(n, ast.While) and isinstance(n.test, ast.Constant):
            print(f"  {nm}@{n.lineno}: while {n.test.value!r}")

print("\n== dict-literal keys written into leg/cell/entry (evidence leaves) ==")
print("  (informational only; see report §3)")

print("\n== done ==")
