#!/usr/bin/env python3
"""r78 SIMPLIFIER static census over the r78 block of measure_audio.py.

  §1 every PLAYBACK_R78_* constant: file-wide reference count (the definition
     counts as 1, so refs=1 is dead weight)
  §2 every r78 function: parameters + in-body Name-load counts
  §3 the call sites of the two deleted parameters
  §4 the return-field census of the intermediate helpers: which fields any
     caller reads (dead envelope fields)
  §5 the branch census for the vacuous guards and dead filters
"""
import ast
import re
import sys
from collections import Counter
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else
           "corpus/fixtures/measure_audio.py")
src = SRC.read_text()
lines = src.splitlines()
tree = ast.parse(src)
R78_START = 5906


def in_r78(node):
    return getattr(node, "lineno", 0) >= R78_START


print("# r78 SIMPLIFIER static census")
print(f"# fixture: {SRC}")
print(f"# r78 block: lines {R78_START}..{len(lines)} "
      f"({len(lines) - R78_START + 1} lines)")
print()
print("## §1 r78 constants: file-wide reference count (definition = 1)")
for node in tree.body:
    if isinstance(node, ast.Assign) and in_r78(node):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id.startswith("PLAYBACK_R78"):
                refs = len(re.findall(r"\b" + re.escape(t.id) + r"\b", src))
                flag = "  <-- DEAD (definition only)" if refs == 1 else ""
                print(f"  refs={refs:3d}  {t.id}{flag}")
print()
print("## §2 r78 functions: parameter use counts (Name loads in body)")
for node in tree.body:
    if not isinstance(node, ast.FunctionDef) or not in_r78(node):
        continue
    name = node.name
    if not (name.startswith("_playback_r78") or name.endswith("_r78_entry")):
        continue
    args = [a.arg for a in node.args.args]
    loads = Counter()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
            loads[sub.id] += 1
    row = ", ".join(f"{a}={loads.get(a, 0)}" for a in args) or "(no params)"
    print(f"  {name}: {row}")
print()
print("## §3 call-site census for the deleted parameters")
for pat in (r"_playback_r78_write_tone\(", r"_playback_r78_tone_windows\("):
    hits = [(i + 1, lines[i].strip())
            for i, l in enumerate(lines) if re.search(pat, l)]
    print(f"  {pat.rstrip(chr(92)+'(')}: {len(hits)} sites")
    for ln, text in hits:
        print(f"      line {ln}: {text[:96]}")
print()
print("## §4 call-site census: what each caller reads off the helper")
for helper, fields in (
        ("_playback_r78_link_map", ("links", "exit", "error")),
        ("_playback_r78_consumers", ("consumer_ports", "nodes", "ambiguous")),
        ("_playback_r78_producers", ("producer_ports", "nodes", "ambiguous")),
):
    calls = [i + 1 for i, l in enumerate(lines)
             if re.search(re.escape(helper) + r"\(\)", l)
             and not l.strip().startswith("def ")]
    print(f"  {helper}: {len(calls)} call site(s) -> lines {calls}")
    for i in calls:
        window = " ".join(lines[i - 1:i + 4])
        hit = [f for f in fields
               if re.search(rf'\.get\(\s*"{f}"|\["{f}"\]', window)]
        print(f"      line {i} reads {hit or 'none'}: "
              f"{lines[i - 1].strip()[:80]}")
print()
print("## §6 the zeros legs' size-sample counts (the S3 guards)")
fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
          and n.name == "capture_unlinked_zeros_r78_entry")
for sub in ast.walk(fn):
    if isinstance(sub, ast.For) and isinstance(sub.iter, ast.List):
        kinds = [e.elts[1].value for e in sub.iter.elts]
        n_size = sum(1 for k in kinds if k == "size")
        has_break = any(isinstance(x, ast.Break)
                        for x in ast.walk(sub))
        print(f"  line {sub.lineno}: {len(kinds)} events, {n_size} size "
              f"samples, break={has_break}")
print()
print("## §5 branch census: the guards the fold removes")
for ln in (7955, 7991, 6793, 6798, 6627, 6633, 6639):
    if ln - 1 < len(lines):
        print(f"  line {ln}: {lines[ln - 1].strip()}")
