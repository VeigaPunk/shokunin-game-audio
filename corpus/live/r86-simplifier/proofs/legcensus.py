#!/usr/bin/env python3
"""r86 leg/entry key census: which stored keys are ever read (verdict
surface) vs recorded-only — over the commit-pinned blob, r86 block."""
import ast
import re

BASE = "base-measure_audio.py"
LO, HI = 23730, 25451
src = open(BASE, encoding="utf-8").read()
tree = ast.parse(src)
lines = src.splitlines()

ENTRY_FNS = ("pwctl_addr_r86_entry", "pwctl_params_r86_entry",
             "pwctl_dsp_r86_entry", "pwctl_meta_r86_entry",
             "pwctl_tools_r86_entry")


def sub(node, lo, hi):
    return LO <= node.lineno <= HI


def key_of(node):
    """legs["k"] / entry["k"] / legs.get("k") -> (base, key) or None."""
    if not isinstance(node, ast.Subscript):
        return None
    v = node.value
    base = None
    if isinstance(v, ast.Name):
        base = v.id
    if base not in ("legs", "entry", "writes"):
        return None
    s = node.slice
    if isinstance(s, ast.Constant) and isinstance(s.value, str):
        return base, s.value
    return None


def getkey_of(node):
    if not isinstance(node, ast.Call):
        return None
    f = node.func
    if not (isinstance(f, ast.Attribute) and f.attr == "get"
            and isinstance(f.value, ast.Name)
            and f.value.id in ("legs", "entry", "writes")):
        return None
    if node.args and isinstance(node.args[0], ast.Constant) \
            and isinstance(node.args[0].value, str):
        return f.value.id, node.args[0].value
    return None


for fn in ENTRY_FNS:
    fnode = next(n for n in tree.body
                 if isinstance(n, ast.FunctionDef) and n.name == fn)
    stores, reads = {}, {}
    for n in ast.walk(fnode):
        k = key_of(n)
        if k and isinstance(n.ctx, ast.Store):
            stores.setdefault(k, []).append(n.lineno)
        elif k and isinstance(n.ctx, ast.Load):
            reads.setdefault(k, []).append(n.lineno)
        gk = getkey_of(n)
        if gk:
            reads.setdefault(gk, []).append(n.lineno)
    print(f"== {fn} ==")
    for (base, key), sl in sorted(stores.items()):
        rl = reads.get((base, key), [])
        flag = "UNREAD " if not rl else ""
        print(f"  {flag}{base}[{key!r}] stored@{sl} reads@{rl}")
    print()

# leg keys referenced only via f-strings (dynamic legs[f"..."])
print("== dynamic leg keys ==")
for m in re.finditer(r'legs\[f"([^"]+)"\]', src):
    ln = src[:m.start()].count("\n") + 1
    if LO <= ln <= HI:
        print(f"  L{ln}: {m.group(0)}")
print()
print("== self_serials occurrences (whole file) ==")
for i, ln in enumerate(lines, 1):
    if "self_serials" in ln:
        print(f"  L{i}: {ln.strip()}")
print()
print("== re_vol occurrences ==")
for i, ln in enumerate(lines, 1):
    if "re_vol" in ln:
        print(f"  L{i}: {ln.strip()}")
print()
print("== specific suspect lines ==")
for ln in (23917, 23964, 24014, 24019, 24094, 24181, 24250, 24418,
           24493, 24529, 24767, 24827, 24898, 24918, 25028, 25052,
           25184, 25217, 25363, 25367):
    print(f"  L{ln}: {lines[ln-1]}")
