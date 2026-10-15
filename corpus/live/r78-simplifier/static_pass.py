#!/usr/bin/env python3
"""r78 SIMPLIFIER static pass over the +2401/-3 r78 block of measure_audio.py.

1. every r78 function: params + in-body use counts (Name loads) -> dead params
2. every r78 top-level constant: reference count in the whole file
3. every r78 local: assignment count vs load count -> dead locals
4. dead subscript-key pins: dict keys written on r78 entries/legs, with the
   read sites (grep-style, whole file) -> pins nothing reads
"""
import ast, re, sys
from collections import Counter, defaultdict
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else
           "corpus/fixtures/measure_audio.py")
src = SRC.read_text()
lines = src.splitlines()
tree = ast.parse(src)

R78_START = 5906   # the r78 banner line
def in_r78(node):
    return getattr(node, "lineno", 0) >= R78_START

# ---- 1. functions + params ------------------------------------------------
print("== 1. r78 function params (use counts) ==")
for node in tree.body:
    if not isinstance(node, ast.FunctionDef) or not in_r78(node):
        continue
    name = node.name
    if not (name.startswith("_playback_r78") or name.endswith("_r78_entry")):
        continue
    args = [a.arg for a in node.args.args]
    if node.args.kwarg:
        args.append(node.args.kwarg.arg)
    loads = Counter()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
            loads[sub.id] += 1
        elif isinstance(sub, ast.arg):
            pass
    print(f"  {name} (line {node.lineno}):")
    for a in args:
        print(f"      {a}: uses={loads.get(a,0)}")

# ---- 2. constants ---------------------------------------------------------
print("\n== 2. r78 top-level constants (file-wide reference count) ==")
for node in tree.body:
    if isinstance(node, ast.Assign) and in_r78(node):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id.startswith("PLAYBACK_R78"):
                refs = len(re.findall(r"\b" + re.escape(t.id) + r"\b", src))
                print(f"  {t.id} = ... refs={refs}")

# ---- 3. locals ------------------------------------------------------------
print("\n== 3. r78 locals: stores vs loads (function-scoped) ==")
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and in_r78(node):
        stores, loads = Counter(), Counter()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name):
                if isinstance(sub.ctx, ast.Store):
                    stores[sub.id] += 1
                else:
                    loads[sub.id] += 1
        params = {a.arg for a in node.args.args}
        dead = [n for n, c in stores.items() if loads.get(n, 0) == 0]
        if dead:
            print(f"  {node.name} (line {node.lineno}): never-loaded stores: {dead}")
        # stored-once-and-loaded-once is fine; report store>=2 (shadowing)
        for n, c in stores.items():
            if c >= 3 and loads.get(n, 0) <= 1 and n not in params:
                print(f"  {node.name}: store-heavy {n} stores={c} loads={loads.get(n,0)}")

# ---- 4. subscript pins written in the r78 block ---------------------------
print("\n== 4. dict-key pins written in the r78 block, read-site count ==")
writes = Counter()
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and in_r78(node):
        for t in ast.walk(node):
            if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name):
                k = t.slice
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    writes[k.value] += 1
for k, c in sorted(writes.items()):
    # read sites: subscript or .get("k") anywhere in the file
    pat = (r'\["' + re.escape(k) + r'"\]|\.get\(\s*"' + re.escape(k) + r'"')
    reads = len(re.findall(pat, src))
    if reads <= 1:
        print(f"  key {k!r}: writes={c} read_sites={reads}")
