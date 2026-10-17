#!/usr/bin/env python3
"""Per-case field stability across receipts, pid-normalized.

Classes per leaf path:
  exact      -- identical in every receipt
  volatile   -- identical after normalization (pid-stamped probe names,
                /tmp scratch dirs, client-id/own-pid keyed values)
  jitter     -- all values numeric (non-bool) but differing: measurement
                noise; reported with spread
  semantic   -- anything else: bool/str/None/shape/absence differences
Usage: percase.py [--split N] receiptA.json receiptB.json [...]
  --split N : first N receipts are the reference group, the rest the fresh
              group (default: half). ADDED/REMOVED and CODE-DELTA are
              computed across the split.
"""
import json, re, sys, collections

VOLATILE_KEYS = {"own_pid", "client_id", "object.id", "object.serial",
                 "client.id", "link_group", "node_link_group"}
DIGITS = re.compile(r"\d{5,}")
SCRATCH = re.compile(r"/tmp/[^/\s]+/")
CLOCK = re.compile(r"\b\d\d:\d\d:\d\d\.\d+\b")
PTR = re.compile(r"0x[0-9a-f]{6,}")

def norm_key(k):
    return DIGITS.sub("<N>", k)

def norm_str(s):
    s = SCRATCH.sub("/tmp/<scratch>/", s)
    s = CLOCK.sub("<t>", s)
    s = PTR.sub("<ptr>", s)
    return DIGITS.sub("<N>", s)

def flatten(obj, path, out, collisions):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = norm_key(k)
            p = f"{path}/{nk}"
            if p in out and nk != k:
                collisions.add(p)
            flatten(v, p, out, collisions)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            flatten(v, f"{path}[{i}]", out, collisions)
    else:
        out[path] = obj

def class_of(vals, key=""):
    if key in VOLATILE_KEYS:
        return "volatile"
    if len(set(map(repr, vals))) == 1:
        return "exact"
    if all(isinstance(v, str) for v in vals) and len(set(map(norm_str, vals))) == 1:
        return "volatile"
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals):
        return "jitter"
    return "semantic"

def spread(vals):
    lo, hi = min(vals), max(vals)
    if lo == hi:
        return "0"
    denom = max(abs(lo), abs(hi)) or 1
    return f"{lo}..{hi} (rel {abs(hi - lo) / denom:.4g})"

def main(paths, split=None):
    maps, colls = [], set()
    for p in paths:
        m = {}
        flatten(json.load(open(p)), "", m, colls)
        maps.append(m)
    allpaths = set()
    for m in maps:
        allpaths |= set(m)
    percase = collections.defaultdict(lambda: collections.Counter())
    details = collections.defaultdict(list)
    half = split if split else (len(maps) // 2 if len(maps) % 2 == 0 else 0)
    for p in sorted(allpaths):
        case = p.split("/")[2] if p.startswith("/measurements/") else "TOP:" + p.split("/")[1]
        vals = [m.get(p, "<absent>") for m in maps]
        leafkey = re.sub(r"\[\d+\]$", "", p).split("/")[-1]
        if all(v != "<absent>" for v in vals):
            cls = class_of(vals, leafkey)
        elif half:
            refv, freshv = vals[:half], vals[half:]
            if all(v == "<absent>" for v in refv) and all(v != "<absent>" for v in freshv):
                cls = "added"
            elif all(v == "<absent>" for v in freshv) and all(v != "<absent>" for v in refv):
                cls = "removed"
            else:
                cls = "semantic"
        else:
            cls = "semantic"
        percase[case][cls] += 1
        if cls in ("jitter", "semantic"):
            details[case].append((cls, p, vals))
    print(f"# receipts: {len(paths)}")
    for p in paths:
        print(f"#   {p}")
    print(f"# total leaf paths: {len(allpaths)}  normalized-key collisions: {len(colls)}")
    for c in sorted(colls):
        print(f"#   COLLISION {c}")
    print()
    hdr = (f"{'case':46s} {'exact':>7s} {'volat':>7s} {'jit':>6s} {'sem':>5s} "
           f"{'added':>6s} {'rem':>5s} {'total':>6s}")
    print(hdr)
    tot = collections.Counter()
    for case in sorted(percase):
        c = percase[case]
        print(f"{case:46s} {c['exact']:7d} {c['volatile']:7d} {c['jitter']:6d} "
              f"{c['semantic']:5d} {c['added']:6d} {c['removed']:5d} {sum(c.values()):6d}")
        tot.update(c)
    print(f"{'TOTAL':46s} {tot['exact']:7d} {tot['volatile']:7d} {tot['jitter']:6d} "
          f"{tot['semantic']:5d} {tot['added']:6d} {tot['removed']:5d} {sum(tot.values()):6d}")
    print()
    print("## jitter detail (numeric, non-bool):")
    for case in sorted(details):
        js = [d for d in details[case] if d[0] == "jitter"]
        if not js:
            continue
        print(f"  {case}: {len(js)} jitter paths")
        for cls, p, vals in js[:6]:
            print(f"    {p}\n      {spread(vals)}")
        if len(js) > 6:
            print(f"    … {len(js) - 6} more")
    print()
    def pairkind(vals):
        """With 4 receipts: [0,1] reference pair, [2,3] fresh pair."""
        if len(vals) != 4:
            return ""
        r_same = repr(vals[0]) == repr(vals[1])
        f_same = repr(vals[2]) == repr(vals[3])
        cross = repr(vals[0]) == repr(vals[2])
        if r_same and f_same and not cross:
            return "CODE-DELTA(ref-pair stable, fresh-pair stable, pairs differ)"
        if r_same and f_same and cross:
            return "impossible"
        if r_same and not f_same:
            return "fresh-pair noise"
        if f_same and not r_same:
            return "ref-pair noise"
        return "mixed/noisy"
    print("## semantic detail (reportable instability):")
    for case in sorted(details):
        ss = [d for d in details[case] if d[0] == "semantic"]
        if not ss:
            continue
        print(f"  {case}: {len(ss)} semantic paths")
        for cls, p, vals in ss[:25]:
            print(f"    {p}   [{pairkind(vals)}]")
            for i, v in enumerate(vals):
                s = repr(v)
                print(f"      [{i}] {s[:140]}{'…' if len(s) > 140 else ''}")
        if len(ss) > 25:
            print(f"    … {len(ss) - 25} more")

if __name__ == "__main__":
    argv = sys.argv[1:]
    sp = None
    if argv and argv[0] == "--split":
        sp = int(argv[1])
        argv = argv[2:]
    main(argv, sp)
