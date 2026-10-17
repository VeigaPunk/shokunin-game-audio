#!/usr/bin/env python3
"""r94-critic: structural + drift analysis of the sox family receipts."""
import json, sys, os

def load(p):
    return json.load(open(p))

def entries(d):
    return d["measurements"]

def summarize(p):
    d = load(p)
    es = entries(d)
    tot_legs = 0
    out = []
    for name, e in es.items():
        legs = e.get("legs", {})
        fails = e.get("failures", [])
        cb = e.get("coverage_blocked", [])
        vol = [k for k, v in legs.items() if isinstance(v, dict) and v.get("volatile_sha")]
        tot_legs += len(legs)
        out.append((name, len(legs), len(fails), len(cb), vol))
    return d, out, tot_legs

def strip_volatile(o, volatile_legs, path=""):
    """Walk and drop volatile fields; return a normalized structure."""
    VOL_FIELDS = {"wall_s", "utc", "loadavg", "loadavg1", "ts", "started_utc",
                  "ended_utc", "host_loadavg", "duration_s_wall"}
    if isinstance(o, dict):
        r = {}
        for k, v in o.items():
            if k in VOL_FIELDS:
                continue
            if k in ("pw_census_entry", "pw_census_exit"):
                # keep shape but drop counters
                r[k] = {kk: vv for kk, vv in v.items()
                        if kk in ("own_objects", "own_modules")}
                continue
            r[k] = strip_volatile(v, volatile_legs, path + "/" + str(k))
        return r
    if isinstance(o, list):
        return [strip_volatile(v, volatile_legs, path) for v in o]
    return o

def diff(a, b, path="", out=None, skip_under=()):
    if out is None:
        out = []
    for s in skip_under:
        if s in path:
            return out
    if type(a) is not type(b):
        out.append((path, a, b)); return out
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a: out.append((path + "/" + str(k), "<missing>", b[k]))
            elif k not in b: out.append((path + "/" + str(k), a[k], "<missing>"))
            else: diff(a[k], b[k], path + "/" + str(k), out, skip_under)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((path + "/len", len(a), len(b))); return out
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, path + "/%d" % i, out, skip_under)
    else:
        if a != b:
            out.append((path, a, b))
    return out

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "summ":
        for p in sys.argv[2:]:
            d, out, tot = summarize(p)
            print("==", p)
            print("   mode:", d.get("mode"), "entries:", len(out), "legs:", tot)
            for name, nl, nf, ncb, vol in out:
                print("   %-32s legs=%3d failures=%d cb=%d volatile=%s" %
                      (name, nl, nf, ncb, vol))
    elif cmd == "drift":
        a, b = sys.argv[2], sys.argv[3]
        da, db = load(a), load(b)
        skip = sys.argv[4:] or ()
        diffs = diff(strip_volatile(da, None), strip_volatile(db, None),
                     skip_under=tuple(skip))
        print("diffs:", len(diffs))
        for path, x, y in diffs[:80]:
            print("  ", path, "|", repr(x)[:80], "->", repr(y)[:80])
