#!/usr/bin/env python3
"""Static census of the r89 pwprof landing (commit 0d732989).

Reports, over the commit-pinned blob:
  A. module-level r89 names and their load counts (unreferenced detection)
  B. per-function parameter binding census (params never bound at any
     call site of that function name)
  C. per-function local stores never loaded (dead bindings), incl.
     loop-target components
  D. literal-string .get(key, default) sites inside the r89 region
  E. `or {}` guard sites inside the r89 region with their enclosing
     function and call-site census of the guarded expression

Read-only: parses text only; writes nothing.
"""
import ast
import sys
from collections import defaultdict

BASE = sys.argv[1]
src = open(BASE).read()
tree = ast.parse(src)

R89_START, R89_END = 29255, 30783  # inserted family region, 1-based inclusive


def in_region(node):
    return (node.lineno >= R89_START and
            getattr(node, "end_lineno", node.lineno) <= R89_END)


# ---------- A. module-level defs in region + load census ----------
mod_defs = {}
for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        if in_region(node):
            mod_defs[node.name] = ("def", node)
    elif isinstance(node, ast.Assign):
        if in_region(node):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    mod_defs[t.id] = ("assign", node)

loads = defaultdict(list)
stores = defaultdict(list)
for node in ast.walk(tree):
    if isinstance(node, ast.Name):
        if isinstance(node.ctx, ast.Load):
            loads[node.id].append(node.lineno)
        else:
            stores[node.id].append(node.lineno)

print("== A. module-level r89 names ==")
for name in sorted(mod_defs):
    kind = mod_defs[name][0]
    n = len(loads.get(name, []))
    print(f"{kind:6s} {name:34s} loads={n:3d} "
          f"{loads.get(name, [])[:8]}")

# ---------- B. parameter binding census ----------
# collect all call sites by callee name (Name or Attribute .attr)
call_sites = defaultdict(list)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        fn = node.func
        if isinstance(fn, ast.Name):
            call_sites[fn.id].append(node)
        elif isinstance(fn, ast.Attribute):
            call_sites[fn.attr].append(node)

print("\n== B. r89 function parameter binding ==")
for name, (kind, node) in sorted(mod_defs.items()):
    if kind != "def":
        continue
    a = node.args
    pnames = [p.arg for p in a.posonlyargs + a.args]
    defaults = [None] * (len(pnames) - len(a.defaults)) + \
        [ast.unparse(d) for d in a.defaults]
    kwonly = {p.arg: (ast.unparse(d) if d else None)
              for p, d in zip(a.kwonlyargs, a.kw_defaults)}
    sites = call_sites.get(name, [])
    bound = defaultdict(int)
    for c in sites:
        for i, arg in enumerate(c.args):
            if i < len(pnames):
                bound[pnames[i]] += 1
        for k in c.keywords:
            if k.arg:
                bound[k.arg] += 1
    print(f"\n{name}: {len(sites)} call sites")
    for p, d in zip(pnames, defaults):
        print(f"    pos {p:14s} default={str(d):22s} bound={bound.get(p, 0)}")
    for p, d in kwonly.items():
        print(f"    kw  {p:14s} default={str(d):22s} bound={bound.get(p, 0)}")

# ---------- C. dead local bindings ----------
print("\n== C. dead local bindings (store never loaded in function) ==")


class FuncLocalCensus(ast.NodeVisitor):
    def __init__(self, fn):
        self.fn = fn
        self.loaded = set()
        self.stored = {}

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.loaded.add(node.id)
        elif isinstance(node.ctx, (ast.Store, ast.Del)):
            self.stored.setdefault(node.id, []).append(node.lineno)

    def run(self):
        for n in ast.walk(self.fn):
            if isinstance(n, ast.Name):
                self.visit_Name(n)
        # exclude params
        a = self.fn.args
        params = {p.arg for p in a.posonlyargs + a.args + a.kwonlyargs}
        if a.vararg:
            params.add(a.vararg.arg)
        if a.kwarg:
            params.add(a.kwarg.arg)
        out = []
        for nm, lns in sorted(self.stored.items()):
            if nm in params or nm in self.loaded:
                continue
            out.append((nm, lns))
        return out


for name, (kind, node) in sorted(mod_defs.items()):
    if kind != "def":
        continue
    dead = FuncLocalCensus(node).run()
    if dead:
        print(f"\n{name}:")
        for nm, lns in dead:
            print(f"    {nm}: stores at {lns}")

# nested closures inside entries: walk every FunctionDef in region
print("\n== C2. nested function dead locals ==")
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and in_region(node) and \
            node.name not in mod_defs:
        dead = FuncLocalCensus(node).run()
        if dead:
            print(f"nested {node.name} @{node.lineno}: {dead}")

# ---------- D. literal .get sites in region ----------
print("\n== D. literal-string .get(key, default) in region ==")
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and in_region(node):
        fn = node.func
        if isinstance(fn, ast.Attribute) and fn.attr == "get" and \
                len(node.args) == 2 and \
                isinstance(node.args[0], ast.Constant) and \
                isinstance(node.args[0].value, str):
            print(f"  L{node.lineno}: {ast.unparse(node)}")

# ---------- E. `or {}` / `or ()` guard sites in region ----------
print("\n== E. `X or {}` / `X or ()` guard sites in region ==")
for node in ast.walk(tree):
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or) and \
            in_region(node):
        rhs = node.values[-1]
        if isinstance(rhs, ast.Dict) and not rhs.keys or \
                (isinstance(rhs, ast.Dict) and not rhs.keys):
            print(f"  L{node.lineno}: {ast.unparse(node)[:110]}")
        elif isinstance(rhs, ast.Tuple) and not rhs.elts:
            print(f"  L{node.lineno}: {ast.unparse(node)[:110]}")
