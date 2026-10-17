#!/usr/bin/env python3
"""r94-critic: volatile-masked structural diff of two sox-r94 receipts.

Masks (recorded, never armed, per the author's convention):
  * host / host_exit / pw_census_entry / pw_census_exit
  * every wall_s
  * the 7 legs marked volatile_sha (their law IS nondeterminism)
Everything else must be identical for a cross-run/cross-seat identity claim.
"""
import json, sys

VOL_FIELDS = {"wall_s", "utc", "loadavg"}
VOL_DROP = {"host", "host_exit", "pw_census_entry", "pw_census_exit"}

def norm(o, vol_legs, name=None):
    if isinstance(o, dict):
        if name in vol_legs:
            return {"__volatile_leg__": name,
                    "n_distinct_shas": o.get("n_distinct_shas"),
                    "stable": o.get("stable"),
                    "rc": o.get("rc"),
                    "reps_n": o.get("reps_n")}
        return {k: norm(v, vol_legs, k) for k, v in o.items()
                if k not in VOL_FIELDS and k not in VOL_DROP}
    if isinstance(o, list):
        return [norm(v, vol_legs, name) for v in o]
    return o

def walk_diff(a, b, path="", out=None):
    if out is None:
        out = []
    if type(a) is not type(b):
        out.append((path, type(a).__name__, type(b).__name__)); return out
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a: out.append((path + "/" + str(k), "<absent>", b[k]))
            elif k not in b: out.append((path + "/" + str(k), a[k], "<absent>"))
            else: walk_diff(a[k], b[k], path + "/" + str(k), out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((path + "/len", len(a), len(b))); return out
        for i, (x, y) in enumerate(zip(a, b)):
            walk_diff(x, y, path + "/%d" % i, out)
    elif a != b:
        out.append((path, a, b))
    return out

def main(pa, pb):
    da, db = json.load(open(pa)), json.load(open(pb))
    va = {k for e in da["measurements"].values()
          for k, l in (e.get("legs") or {}).items()
          if isinstance(l, dict) and l.get("volatile_sha")}
    vb = {k for e in db["measurements"].values()
          for k, l in (e.get("legs") or {}).items()
          if isinstance(l, dict) and l.get("volatile_sha")}
    assert va == vb, (va ^ vb)
    na, nb = norm(da, va), norm(db, vb)
    d = walk_diff(na, nb)
    print("A:", pa)
    print("B:", pb)
    print("volatile legs:", sorted(va))
    print("diffs outside volatile legs/fields:", len(d))
    for p, x, y in d[:60]:
        print("   ", p, "|", repr(x)[:90], "->", repr(y)[:90])
    return len(d)

if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1], sys.argv[2]) == 0 else 1)
