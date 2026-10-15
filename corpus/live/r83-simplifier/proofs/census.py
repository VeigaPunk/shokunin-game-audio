#!/usr/bin/env python3
"""r83-simplifier static census — call-site / dead-parameter / dead-name
census over the r83 family block of corpus/fixtures/measure_audio.py.

Read-only. Prints one line per predicate; exit 0 always (the report reads
the PASS/FAIL text). Run:

    python3 census.py corpus/fixtures/measure_audio.py
"""
import ast
import sys

BLK_START = 16315          # first line of the r83 comment header
BLK_END = 18702            # last line before `def main()`

SRC = sys.argv[1] if len(sys.argv) > 1 else "corpus/fixtures/measure_audio.py"
text = open(SRC).read()
lines = text.splitlines()
tree = ast.parse(text)


def inblk(node):
    return BLK_START <= node.lineno <= BLK_END


# ---------------------------------------------------------------- defs
funcs = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and inblk(node):
        funcs[node.name] = node

print("== defs in block ==")
for nm, fn in sorted(funcs.items(), key=lambda kv: kv[1].lineno):
    print(f"  {fn.lineno:6d}-{fn.end_lineno:6d}  {nm}")

# ------------------------------------------------- module-level consts
consts = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and inblk(node):
        for t in node.targets:
            if isinstance(t, ast.Name):
                consts[t.id] = node.lineno

print("\n== module-level block constants: load census (whole file) ==")
for nm, ln in sorted(consts.items(), key=lambda kv: kv[1]):
    loads = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Name) and n.id == nm
             and isinstance(n.ctx, ast.Load)]
    stores = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Name) and n.id == nm
              and isinstance(n.ctx, ast.Store)]
    verdict = "DEAD(definition-only)" if not loads else "live"
    print(f"  {nm:32s} def@{ln:6d} loads={len(loads)} "
          f"stores={len(stores)} {verdict}")
    if loads:
        print(f"      load lines: {loads}")

# ------------------------------------------------------ call-site census
print("\n== call-site census per block helper ==")
calls = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in funcs:
        calls.setdefault(node.func.id, []).append(node)

for nm in sorted(funcs, key=lambda n: funcs[n].lineno):
    fn = funcs[nm]
    params = [a.arg for a in fn.args.args]
    sites = calls.get(nm, [])
    supplied = set()
    star = False
    site_lines = []
    for c in sites:
        site_lines.append(c.lineno)
        for kw in c.keywords:
            if kw.arg is None:
                star = True
            else:
                supplied.add(kw.arg)
        if len(c.args) > len(params):
            star = True
    never = [p for p in params if p not in supplied]
    # positional coverage: a param may be supplied positionally
    maxpos = max([len(c.args) for c in sites], default=0)
    pos_covered = set(params[:maxpos])
    never = [p for p in never if p not in pos_covered]
    print(f"  {nm:30s} sites={len(sites):3d} params={params}")
    print(f"      never-supplied-by-name: {never}"
          f"{'  (kwargs/**splat present -> inconclusive)' if star else ''}")
    print(f"      site lines: {site_lines}")

# ------------------------------------------- param load/store per func
print("\n== parameter use census (Load vs Store inside the def) ==")
for nm, fn in sorted(funcs.items(), key=lambda kv: kv[1].lineno):
    params = [a.arg for a in fn.args.args]
    unused = []
    for p in params:
        ld = st = 0
        for n in ast.walk(fn):
            if isinstance(n, ast.Name) and n.id == p:
                if isinstance(n.ctx, ast.Load):
                    ld += 1
                elif isinstance(n.ctx, ast.Store):
                    st += 1
        if ld == 0:
            unused.append((p, st))
    if unused:
        print(f"  {nm:30s} unused-params(load=0): {unused}")

# ------------------------------------------------ write-only locals
print("\n== write-only locals inside block defs ==")
for nm, fn in sorted(funcs.items(), key=lambda kv: kv[1].lineno):
    store = {}
    load = {}
    for n in ast.walk(fn):
        if isinstance(n, ast.Name):
            if isinstance(n.ctx, ast.Store):
                store.setdefault(n.id, []).append(n.lineno)
            elif isinstance(n.ctx, ast.Load):
                load.setdefault(n.id, []).append(n.lineno)
    params = {a.arg for a in fn.args.args}
    for var in sorted(store):
        if var in params:
            continue
        if not load.get(var):
            print(f"  {nm:30s} {var:24s} stores={store[var]} loads=0")

# ------------------------------------------------------------- main
print("\n== done ==")
