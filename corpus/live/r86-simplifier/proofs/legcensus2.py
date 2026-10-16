#!/usr/bin/env python3
"""r86 leg census v2: expand literal loop/dynamic reads so the residual
'unread stored leg' list is trustworthy (pinned blob, r86 block)."""
import ast
import re

BASE = "base-measure_audio.py"
LO, HI = 23730, 25451
src = open(BASE, encoding="utf-8").read()
tree = ast.parse(src)

ENTRY_FNS = ("pwctl_addr_r86_entry", "pwctl_params_r86_entry",
             "pwctl_dsp_r86_entry", "pwctl_meta_r86_entry",
             "pwctl_tools_r86_entry")


def lit_strings(node):
    out = set()
    if isinstance(node, (ast.Tuple, ast.List)):
        for e in node.elts:
            out |= lit_strings(e)
    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
        out.add(node.value)
    return out


for fn in ENTRY_FNS:
    fnode = next(n for n in tree.body
                 if isinstance(n, ast.FunctionDef) and n.name == fn)
    # loop var -> literal key candidates
    loopvals = {}
    for n in ast.walk(fnode):
        if isinstance(n, ast.For) and isinstance(n.target, ast.Name):
            s = lit_strings(n.iter)
            if s:
                loopvals.setdefault(n.target.id, set()).update(s)
    # dynamic reads
    dyn = set()
    for n in ast.walk(fnode):
        if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Load):
            v, s = n.value, n.slice
            if isinstance(v, ast.Name) and v.id in ("legs", "entry") \
                    and isinstance(s, ast.Name) and s.id in loopvals:
                dyn |= loopvals[s.id]
            if isinstance(v, ast.Name) and v.id in ("legs", "entry") \
                    and isinstance(s, ast.JoinedStr):
                prefix = "".join(p.value for p in s.values
                                 if isinstance(p, ast.Constant))
                for vv in s.values:
                    if isinstance(vv, ast.FormattedValue) \
                            and isinstance(vv.value, ast.Name):
                        for cand in loopvals.get(vv.value.id, ()):
                            dyn.add(prefix + cand)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                and n.func.id == "jack_env" and n.args:
            a = n.args[0]
            if isinstance(a, ast.Constant):
                dyn.add(a.value)
    # literal reads + stores
    reads, stores = set(), {}
    for n in ast.walk(fnode):
        if isinstance(n, ast.Subscript):
            v, s = n.value, n.slice
            if isinstance(v, ast.Name) and v.id in ("legs", "entry") \
                    and isinstance(s, ast.Constant) \
                    and isinstance(s.value, str):
                if isinstance(n.ctx, ast.Store):
                    stores.setdefault(s.value, n.lineno)
                else:
                    reads.add(s.value)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr == "get" \
                and isinstance(n.func.value, ast.Name) \
                and n.func.value.id in ("legs", "entry") \
                and n.args and isinstance(n.args[0], ast.Constant) \
                and isinstance(n.args[0].value, str):
            reads.add(n.args[0].value)
    print(f"== {fn} ==")
    unread = sorted(k for k in stores if k not in reads and k not in dyn)
    print(f"  stored keys: {len(stores)}; literal-read: {len(reads)}; "
          f"dynamic-read candidates: {len(dyn)}")
    print(f"  RESIDUAL stored-never-read: {unread}")
    print()
