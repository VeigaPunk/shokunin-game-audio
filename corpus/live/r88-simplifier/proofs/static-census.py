#!/usr/bin/env python3
"""Static census over the c19bec96-pinned blob: r88 (btwit) defs,
constants, call sites, parameter usage, and region confinement."""
import ast
import re
import sys
from collections import Counter

SRC = "base-measure_audio.py"
text = open(SRC, encoding="utf-8").read()
lines = text.splitlines()
tree = ast.parse(text)

R88_START = 27507          # 1-based: comment block start
R88_END = 29252            # 1-based: `return entry` of pwtop_r88_entry
# verify region markers
assert lines[R88_START - 1].startswith("# r88:"), lines[R88_START - 1]
assert lines[R88_END - 1].strip() == "return entry", lines[R88_END - 1]
assert lines[R88_END].strip() == "", lines[R88_END]
assert lines[R88_END + 1].strip() == "", lines[R88_END + 1]
assert lines[R88_END + 2].startswith("def main():"), lines[R88_END + 2]

print("== file ==")
print("lines:", len(lines), "sha256(base file, see sha256.txt)")

# ---- 1. every module-level name defined inside the r88 region ----
defs = {}
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if R88_START <= node.lineno <= R88_END:
            defs[node.name] = node
    elif isinstance(node, ast.Assign):
        if R88_START <= node.lineno <= R88_END:
            for t in node.targets:
                if isinstance(t, ast.Name):
                    defs[t.id] = node

print("\n== module-level defs in region ==")
for name, node in sorted(defs.items(), key=lambda kv: kv[1].lineno):
    kind = "def " if isinstance(node, ast.FunctionDef) else "var "
    print(f"{kind}{name:38s} :{node.lineno}")

# ---- 2. word-boundary occurrence census over the whole file ----
print("\n== occurrence census (whole file, word boundary) ==")
for name in sorted(defs):
    pat = re.compile(r"(?<![\w.])" + re.escape(name) + r"(?![\w])")
    hits = [(i + 1, ln.strip()[:100]) for i, ln in enumerate(lines)
            if pat.search(ln)]
    print(f"{name:38s} uses={len(hits)-1:3d} sites={[h[0] for h in hits]}")

# ---- 3. r88 function call sites + keyword arguments ----
print("\n== call sites of r88 defs (name(args...) occurrences) ==")
for name, node in sorted(defs.items(), key=lambda kv: kv[1].lineno):
    if not isinstance(node, ast.FunctionDef):
        continue
    args = [a.arg for a in node.args.args]
    defaults = len(node.args.defaults)
    calls = []
    for sub in ast.walk(tree):
        if isinstance(sub, ast.Call):
            f = sub.func
            if isinstance(f, ast.Name) and f.id == name:
                kw = [k.arg for k in sub.keywords]
                calls.append((sub.lineno, len(sub.args), kw))
    print(f"\n{name}  params={args} defaults={defaults}  "
          f"calls={len(calls)}")
    for lineno, npos, kw in calls:
        print(f"    :{lineno}  pos={npos} kw={kw}")

# ---- 4. names referenced inside the region but defined outside ----
region_text = "\n".join(lines[R88_START - 1:R88_END])
region_names = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", region_text))
outside_defs = set()
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.lineno < R88_START:
        outside_defs.add(node.name)
    if isinstance(node, ast.Assign) and node.lineno < R88_START:
        for t in node.targets:
            if isinstance(t, ast.Name):
                outside_defs.add(t.id)
print("\n== region references to pre-r88 module-level names ==")
print(sorted(region_names & outside_defs))
