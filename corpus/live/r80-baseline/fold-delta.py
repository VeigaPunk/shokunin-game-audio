#!/usr/bin/env python3
"""Verdict-surface delta across receipts: legs / classes / named outcomes.

Path-wise diffs (percase.py) descend into ordered lists, so an inserted
entry shifts every later index. This script compares the verdict-bearing
*collections* per probe entry as sets/multisets, which is the honest
reading of an additive fold.

Usage: fold-delta.py ref1.json ref2.json ... -- fresh1.json fresh2.json ...
"""
import json, sys, collections

def collections_of(receipt):
    out = {}
    for case, e in receipt["measurements"].items():
        if not isinstance(e, dict):
            continue
        legs = e.get("legs")
        if not isinstance(legs, dict):
            continue
        out[case] = {
            "legs": set(legs),
            "classes_extra": set(e.get("classes_extra") or []),
            "named_outcomes": collections.Counter(e.get("named_outcomes") or []),
            "failures": e.get("failures") or [],
        }
    return out

def tag(s):
    return s.split(" — ")[0].split(":")[0].strip()

def main(argv):
    i = argv.index("--")
    refs = [json.load(open(p)) for p in argv[:i]]
    fresh = [json.load(open(p)) for p in argv[i + 1:]]
    R, F = collections_of(refs[0]), collections_of(fresh[0])
    for r in refs[1:]:
        assert set(collections_of(r)) == set(R)
    for f in fresh[1:]:
        assert set(collections_of(f)) == set(F)
    for case in sorted(set(R) | set(F)):
        r, f = R.get(case), F.get(case)
        if r is None or f is None:
            print(f"## {case}: only in {'fresh' if r is None else 'ref'}")
            continue
        rl, fl = r["legs"], f["legs"]
        add, rem = fl - rl, rl - fl
        rc, fc = r["classes_extra"], f["classes_extra"]
        ro, fo = r["named_outcomes"], f["named_outcomes"]
        if not (add or rem or fc - rc or rc - fc or ro != fo or r["failures"] != f["failures"]):
            print(f"## {case}: verdict surface IDENTICAL (legs {len(rl)})")
            continue
        print(f"## {case}: legs {len(rl)} -> {len(fl)}")
        if add:
            print(f"   LEGS ADDED:   {sorted(add)}")
        if rem:
            print(f"   LEGS REMOVED: {sorted(rem)}")
        if fc - rc:
            print(f"   CLASSES ADDED:   {sorted(fc - rc)}")
        if rc - fc:
            print(f"   CLASSES REMOVED: {sorted(rc - fc)}")
        if ro != fo:
            print(f"   named_outcomes: {sum(ro.values())} -> {sum(fo.values())}")
            for k in sorted((fo - ro).elements()):
                print(f"     + {k[:150]}")
            for k in sorted((ro - fo).elements()):
                print(f"     - {k[:150]}")
            # tag-level (drop the correlate tail) for the same comparison
            rt = collections.Counter(tag(k) for k in ro.elements())
            ft = collections.Counter(tag(k) for k in fo.elements())
            if rt != ft:
                print(f"   tag-level: {sum(rt.values())} -> {sum(ft.values())}")
                for k in sorted((ft - rt).elements()):
                    print(f"     + {k}")
                for k in sorted((rt - ft).elements()):
                    print(f"     - {k}")
        if r["failures"] != f["failures"]:
            print(f"   FAILURES: {r['failures']} -> {f['failures']}")

if __name__ == "__main__":
    main(sys.argv[1:])
