#!/usr/bin/env python3
"""r86 symtable census: assigned-but-never-referenced locals per
function scope in the r86 block (comprehension-aware) — pinned blob."""
import symtable

BASE = "base-measure_audio.py"
LO, HI = 23730, 25451
src = open(BASE, encoding="utf-8").read()
lines = src.splitlines()
st = symtable.symtable(src, BASE, "exec")

block_fns = {n.get_name() for n in st.get_children()}


def walk_scope(s, depth=0):
    for sym in s.get_symbols():
        if sym.is_assigned() and not sym.is_referenced() \
                and not sym.is_parameter():
            # find the line(s)
            print(f"ASSIGNED-NEVER-REFERENCED  scope={s.get_name():32s} "
                  f"sym={sym.get_name()}")
    for c in s.get_children():
        walk_scope(c, depth + 1)


for s in st.get_children():
    if s.get_name() in block_fns:
        walk_scope(s)
