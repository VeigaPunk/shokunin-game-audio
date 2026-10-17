#!/usr/bin/env python3
"""Static census of the r79 loopback block in corpus/fixtures/measure_audio.py.

Sections:
  1  constant reference counts (LOOPBACK_R79_* / PLAYBACK_R78_* touched by r79)
  2  r79 function call-site counts
  3  per-function parameter use counts (body loads vs binding)
  4  dead local bindings (assigned, never loaded) inside r79 functions
  5  named branch/guard probes (printed verbatim source lines)
"""
import ast
import re
import sys
from collections import Counter
from pathlib import Path

FIX = Path(sys.argv[1] if len(sys.argv) > 1 else
           "corpus/fixtures/measure_audio.py")
SRC = FIX.read_text()
LINES = SRC.splitlines()
TREE = ast.parse(SRC)

# r79 block: from the family banner to `def main():`
start = SRC.index("# r79 LOOPBACK frontier")
end = SRC.index("def main():")
BLOCK_START = SRC[:start].count("\n") + 1
BLOCK_END = SRC[:end].count("\n") + 1
print(f"# r79 block lines {BLOCK_START}..{BLOCK_END} "
      f"({BLOCK_END - BLOCK_START + 1} lines)")
block = SRC[start:end]


def is_r79(node):
    ln = getattr(node, "lineno", 0)
    return BLOCK_START <= ln <= BLOCK_END


# ---------------------------------------------------------------- section 1
print("\n## 1 constants")
for m in re.finditer(r"^(LOOPBACK_R79_\w+|PLAYBACK_R78_\w+)\s*=", SRC, re.M):
    name = m.group(1)
    if not name.startswith("LOOPBACK_R79_"):
        continue
    refs = len(re.findall(rf"\b{re.escape(name)}\b", SRC)) - 1
    print(f"  {name:32s} refs_outside_def={refs}")

# ---------------------------------------------------------------- section 2
funcs = {}
for node in ast.walk(TREE):
    if isinstance(node, ast.FunctionDef) and is_r79(node):
        funcs[node.name] = node
print(f"\n## 2 r79 functions ({len(funcs)})")
for name, node in funcs.items():
    refs = len(re.findall(rf"\b{re.escape(name)}\b", SRC)) - 1
    print(f"  {name:44s} def_line={node.lineno:5d} refs={refs}")

# ---------------------------------------------------------------- section 3
print("\n## 3 parameter use counts (params never loaded in body)")
for name, node in funcs.items():
    args = [a.arg for a in node.args.args + node.args.kwonlyargs]
    loads = Counter()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
            loads[sub.id] += 1
    unused = [a for a in args if loads[a] == 0]
    if unused:
        print(f"  {name}: NEVER-LOADED params {unused}")

# ---------------------------------------------------------------- section 4
print("\n## 4 dead local bindings (store, no load in the same function)")
for name, node in funcs.items():
    stores = {}
    loads = Counter()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            if isinstance(sub.ctx, (ast.Store,)):
                stores.setdefault(sub.id, []).append(sub.lineno)
            elif isinstance(sub.ctx, ast.Load):
                loads[sub.id] += 1
    dead = {k: v for k, v in stores.items() if loads[k] == 0}
    for k, v in sorted(dead.items()):
        print(f"  {name}: local {k!r} stored at {v} — 0 loads")

# ---------------------------------------------------------------- section 5
print("\n## 5 named guard probes")
probes = [
    (r"tap_t = ns_b if kind != \"none\" else ns_b",
     "capture-lattice tap_t ternary (both arms ns_b)"),
    (r"and s0 is None", "capture-lattice @SRC@ guard's s0 conjunct"),
    (r"extra_tw", "playback-lattice extra_tw"),
    (r"require=", "check_tap require= at any call site"),
    (r"want is None", "check_side want-is-None arm"),
    (r"_loopback_r79_union\(", "union helper call sites"),
    (r"if not tap:", "check_tap empty-tap arm"),
    (r"PLAYBACK_R78_TONE_L_HZ|PLAYBACK_R78_TONE_R_HZ",
     "tone frequency constants (pid-derived)"),
]
for pat, desc in probes:
    hits = [(i + 1, LINES[i].strip()) for i, l in enumerate(LINES)
            if re.search(pat, l)]
    print(f"\n  [{desc}]  ({len(hits)} hits)")
    for ln, text in hits[:24]:
        print(f"    {ln}: {text[:110]}")
