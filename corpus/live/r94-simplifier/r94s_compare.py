#!/usr/bin/env python3
"""r94s_ structural walk: compare two r94 sox receipts and report every
difference outside the declared volatile field set. Used to prove that a fold
set preserves the retained contract (same legs, same values, same laws).

Usage: python3 r94s_compare.py <baseline.json> <variant.json> [--full]
"""
import json
import sys

# recorded, never armed: wall clock, host load, census co-tenancy, own pid tag
VOLATILE_KEYS = {"wall_s", "utc", "loadavg", "own_prefix", "stderr_bytes"}
VOLATILE_SUBTREES = {"pw_census_entry", "pw_census_exit", "host", "host_exit"}


def flatten(node, path=()):
    out = {}
    if isinstance(node, dict):
        for k, v in node.items():
            out.update(flatten(v, path + (str(k),)))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.update(flatten(v, path + (str(i),)))
    else:
        out[path] = node
    return out


def volatile(path):
    return path[-1] in VOLATILE_KEYS or any(p in VOLATILE_SUBTREES for p in path)


def load(path):
    doc = json.loads(open(path).read())
    return {k: v for k, v in doc["measurements"].items() if k.endswith("r94_probe")}


def main():
    base, var = sys.argv[1], sys.argv[2]
    full = "--full" in sys.argv
    B, V = load(base), load(var)
    print(f"baseline: {base}\nvariant : {var}")
    removed, added, diffs = [], [], []
    for entry in sorted(set(B) | set(V)):
        b, v = B.get(entry), V.get(entry)
        if b is None or v is None:
            diffs.append((entry, "<entry>", "present on one side only"))
            continue
        bl, vl = set(b["legs"]), set(v["legs"])
        removed += [f"{entry}:{ln}" for ln in sorted(bl - vl)]
        added += [f"{entry}:{ln}" for ln in sorted(vl - bl)]
        # skip volatile legs entirely (their bytes are nondeterministic by law)
        skip = {ln for ln in bl & vl
                if b["legs"][ln].get("volatile_sha")
                or v["legs"][ln].get("volatile_sha")}
        fb = {p: x for p, x in flatten(b).items()
              if not volatile(p) and not (len(p) > 1 and p[1] in skip)}
        fv = {p: x for p, x in flatten(v).items()
              if not volatile(p) and not (len(p) > 1 and p[1] in skip)}
        for p in sorted(set(fb) | set(fv)):
            if fb.get(p, "<MISSING>") != fv.get(p, "<MISSING>"):
                diffs.append((entry, "/".join(p),
                              f"{fb.get(p, '<MISSING>')!r} -> {fv.get(p, '<MISSING>')!r}"))
    print(f"\nlegs removed by the variant ({len(removed)}):")
    for r in removed:
        print("   -", r)
    print(f"legs added by the variant ({len(added)}): {added}")
    print(f"\nfield differences outside the volatile set: {len(diffs)}")
    shown = diffs if full else diffs[:60]
    for e, p, d in shown:
        print(f"   {e}  {p}  {d}")
    if len(diffs) > len(shown):
        print(f"   ... {len(diffs) - len(shown)} more")
    nb, nv = len(open(base).read()), len(open(var).read())
    print(f"\nreceipt bytes: baseline {nb} variant {nv} ({nv - nb:+d})")
    # classify the residual diffs: are they all removals of the two dead fields?
    def intended(d):
        if not d[2].endswith("-> '<MISSING>'"):
            return False
        if "first8_ints" in d[1] or "fmt_tag" in d[1]:
            return True
        return d[1].startswith("legs/alias_20k_v/")

    other = [d for d in diffs if not intended(d)]
    print(f"residual diffs other than the dead-field removals: {len(other)}")
    for d in other[:40]:
        print("   !", d)
    return 0 if not other else 1


if __name__ == "__main__":
    sys.exit(main())
