#!/usr/bin/env python3
"""Grep-literal dead-symbol scan of the tracked fixture (LSP unavailable).

Reports, for corpus/fixtures/measure_audio.py:
  - module-level defs whose name occurs nowhere else (def line excluded)
  - argparse flags whose args.<name> attribute is referenced nowhere else
  - UPPER_CASE module constants with no other occurrence
This is NOT semantic proof (seat card: grep-literal fallback only).
"""
import ast, re, sys, collections
from pathlib import Path

p = Path(sys.argv[1] if len(sys.argv) > 1 else
         "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/fixtures/measure_audio.py")
src = p.read_text()
tree = ast.parse(src)
lines = src.splitlines()

defs = []
consts = []
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        defs.append(node.name)
    elif isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id.isupper():
                consts.append(t.id)

flags = []
for node in ast.walk(tree):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_argument" and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
            and node.args[0].value.startswith("--")):
        flags.append(node.args[0].value)

def occurrences(name):
    pat = re.compile(r"\b" + re.escape(name) + r"\b")
    hits = []
    for i, ln in enumerate(lines, 1):
        for m in pat.finditer(ln):
            hits.append(i)
    return hits

print("== defs with no other occurrence ==")
dead_defs = []
for name in defs:
    hits = occurrences(name)
    others = [h for h in hits if not lines[h-1].lstrip().startswith("def " + name)]
    if not others:
        dead_defs.append(name)
        print(f"DEAD-DEF {name} def@{hits[0]}")
print(f"({len(dead_defs)}/{len(defs)} defs dead)")

print("== argparse flags with no args.<attr> reference ==")
dead_flags = []
for flag in flags:
    attr = "args." + flag.lstrip("-").replace("-", "_")
    if attr not in src:
        dead_flags.append(flag)
        print(f"DEAD-FLAG {flag}")
print(f"({len(dead_flags)}/{len(flags)} flags dead)")

print("== UPPER_CASE constants with no other occurrence ==")
dead_consts = []
for name in consts:
    hits = occurrences(name)
    assigns = [h for h in hits if lines[h-1].startswith(name + " ")]
    others = [h for h in hits if h not in assigns]
    if not others:
        dead_consts.append(name)
        print(f"DEAD-CONST {name} @{assigns}")
print(f"({len(dead_consts)}/{len(consts)} consts dead)")

print("== duplicate-shape census (group-by-signature loops) ==")
for i, ln in enumerate(lines, 1):
    if "for group in" in ln or "for g in groups" in ln:
        print(f"group-loop @ {i}: {ln.strip()}")
