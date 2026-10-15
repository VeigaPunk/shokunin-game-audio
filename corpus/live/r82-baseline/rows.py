#!/usr/bin/env python3
"""Row census of a receipt: entries, legs, flattened leaf paths, failures.

`rows` = receipt entries + the legs inside every entry's `legs` map; the
leaf count is the flattened JSON leaf count (the "cells" percase.py
compares). Used to state the r81 replay scope precisely.
"""
import json, sys

def flatten(obj, path, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            flatten(v, f"{path}/{k}", out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            flatten(v, f"{path}[{i}]", out)
    else:
        out[path] = obj

def census(path, verbose=False):
    d = json.load(open(path))
    m = d["measurements"]
    legs = 0
    fam = {}
    for k, v in m.items():
        n = len(v.get("legs") or {}) if isinstance(v, dict) else 0
        legs += n
        if n:
            fam[k] = n
    leaves = {}
    flatten(d, "", leaves)
    fails = {k: v.get("failures") for k, v in m.items()
             if isinstance(v, dict) and v.get("failures")}
    print(f"{path}")
    print(f"  mode={d['mode']} entries={len(m)} legs={legs} leaves={len(leaves)} "
          f"cases_with_failures={len(fails)}")
    if verbose:
        for k in sorted(fam):
            print(f"    {k}: {fam[k]} legs")
        for k, f in fails.items():
            print(f"    FAIL {k}: {f}")

if __name__ == "__main__":
    args = sys.argv[1:]
    verbose = False
    if args and args[0] == "-v":
        verbose = True
        args = args[1:]
    for p in args:
        census(p, verbose)
