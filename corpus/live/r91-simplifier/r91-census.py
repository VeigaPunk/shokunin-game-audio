#!/usr/bin/env python3
"""Reference census for the r91 (gstfrz) block of measure_audio.py.

Prints, for every module-level name defined in the r91 region:
  - AST-level Name loads anywhere in the file (a block-local name may be
    referenced outside the block) + call-site count
  - per-parameter call-site census: positional-arity histogram and the set of
    kwargs ever supplied, so 'never supplied' is a measured claim
  - 'assigned but never loaded' locals inside the region functions
  - branch sensitivity: does the function body test the parameter at all?

Usage: r91-census.py <path-to-measure_audio.py>
"""
import ast
import sys
from collections import Counter, defaultdict

path = sys.argv[1]
src = open(path).read()
tree = ast.parse(src)
lines = src.splitlines()

import re as _re
_banner = _re.compile(r"^# r\d+: ")
start = next(i for i, l in enumerate(lines, 1)
             if l.startswith("# r91: the Gst CAPTURE-FREEZE"))
end = next(i for i, l in enumerate(lines, 1)
           if i > start and (_banner.match(l) or l.startswith("def main():")))
print(f"region: {start}..{end}  ({end - start} lines)")

region_names = {}
for node in tree.body:
    if start <= node.lineno <= end:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            region_names[node.name] = ("def", node)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    region_names[t.id] = ("assign", node)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target,
                                                             ast.Name):
            region_names[node.target.id] = ("annassign", node)

print(f"module-level names in region: {len(region_names)}")

loads = Counter()
call_kwargs = defaultdict(Counter)
calls = defaultdict(list)
for node in ast.walk(tree):
    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
        loads[node.id] += 1
    if isinstance(node, ast.Call):
        f = node.func
        nm = f.id if isinstance(f, ast.Name) else (
            "." + f.attr if isinstance(f, ast.Attribute) else "?")
        calls[nm].append(node)

print("\n== region module-level names: load counts (whole file) ==")
for nm, (kind, node) in sorted(region_names.items()):
    n = loads.get(nm, 0)
    ncall = len(calls.get(nm, []))
    flag = "  <== ZERO LOADS" if n == 0 else ""
    print(f"{nm:34s} {kind:9s} loads={n:4d} callsites={ncall:3d}{flag}")

print("\n== region function call sites (whole file) ==")
for nm in sorted(region_names):
    if region_names[nm][0] != "def":
        continue
    ls = calls.get(nm, [])
    kw = call_kwargs.get(nm, Counter())
    print(f"{nm:34s} n={len(ls):3d} "
          f"lines={[c.lineno for c in ls]}")

print("\n== parameter census (never-supplied params are the dead-param "
      "candidates) ==")
for nm, (kind, node) in sorted(region_names.items()):
    if kind != "def":
        continue
    a = node.args
    pos = [x.arg for x in a.args]
    kwonly = [x.arg for x in a.kwonlyargs]
    defaults = [ast.unparse(d) for d in a.defaults]
    kw_used = Counter()
    pos_hist = Counter()
    for c in calls.get(nm, []):
        pos_hist[len(c.args)] += 1
        for k in c.keywords:
            kw_used[k.arg] += 1
    never = [p for p in pos + kwonly
             if kw_used.get(p, 0) == 0 and p not in ("self",)]
    # positional params are only 'never supplied' if no call site can reach
    # them: a param at index i is supplied positionally iff some call has
    # len(args) > i
    maxpos = max(pos_hist) if pos_hist else 0
    never = [p for p in never if pos.index(p) >= maxpos or p in kwonly]
    src_fun = ast.get_source_segment(src, node) or ""
    print(f"\n{nm}  pos={pos} kwonly={kwonly} defaults={defaults}")
    print(f"    call pos-arity histogram: {dict(pos_hist)}; "
          f"kwargs ever used: {dict(kw_used)}")
    print(f"    NEVER SUPPLIED: {never}")
    for p in never:
        # crude branch-sensitivity: is the bare name tested anywhere?
        tested = any(isinstance(n, ast.Name) and n.id == p
                     for n in ast.walk(node))
        print(f"      - {p}: referenced-in-body={tested}")

print("\n== assigned-but-never-loaded locals in region functions ==")
for nm, (kind, node) in sorted(region_names.items()):
    if kind != "def":
        continue
    assigned = defaultdict(list)
    loaded = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            if isinstance(n.ctx, ast.Store):
                assigned[n.id].append(n.lineno)
            elif isinstance(n.ctx, ast.Load):
                loaded.add(n.id)
    dead = {k: v for k, v in assigned.items() if k not in loaded}
    if dead:
        print(f"  {nm}: {dead}")
