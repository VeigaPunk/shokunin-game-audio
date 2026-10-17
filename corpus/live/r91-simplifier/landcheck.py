#!/usr/bin/env python3
"""Landability check: do both r91 folds apply exactly once to the bytes of
another revision (HEAD / the working tree), and does the folded blob stay a
valid module with the same AST-level census?

Usage: landcheck.py <rev-or-file> [<rev-or-file> ...]
"""
import ast
import hashlib
import pathlib
import subprocess
import sys

FOLDS = pathlib.Path(
    "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
    "r91-simplifier/fold_apply.py")


def load_folds():
    ns = {}
    exec(FOLDS.read_text(), ns)
    return ns["FOLD1"] + ns["FOLD2"]


def blob(spec):
    if pathlib.Path(spec).exists():
        return pathlib.Path(spec).read_bytes()
    return subprocess.run(["git", "show", f"{spec}:corpus/fixtures/"
                           "measure_audio.py"], capture_output=True,
                          check=True).stdout


def census(src):
    tree = ast.parse(src)
    loads = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            loads[node.id] = loads.get(node.id, 0) + 1
    return loads


for spec in sys.argv[1:]:
    raw = blob(spec)
    src = raw.decode()
    print(f"== {spec}: sha256 {hashlib.sha256(raw).hexdigest()}")
    for needle, repl, want in load_folds():
        n = src.count(needle)
        status = "OK" if n == want else "REFUSED"
        print(f"   fold occurrence {n}/{want} {status} :: {needle[:52]!r}")
        assert n == want, f"{spec}: fold does not apply exactly once"
    folded = src.replace(load_folds()[0][0], load_folds()[0][1])
    for needle, repl, want in load_folds()[1:]:
        folded = folded.replace(needle, repl)
    ast.parse(folded)                       # syntax
    b0, b1 = raw.decode().splitlines(), folded.splitlines()
    print(f"   lines {len(b0)} -> {len(b1)}")
    l0, l1 = census(src), census(folded)
    for name in ("hooks", "pending", "want_state_drop", "want_header"):
        print(f"   name {name!r}: loads {l0.get(name, 0)} -> "
              f"{l1.get(name, 0)}")
    print(f"   folded sha256 {hashlib.sha256(folded.encode()).hexdigest()}")
print("ALL FOLDS APPLY EXACTLY ONCE")
