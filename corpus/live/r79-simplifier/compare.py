#!/usr/bin/env python3
"""Leaf comparator for two r79 probe receipts.

    python3 compare.py control.json cand.json [--allow classes.txt] [--group]

Normalization (per-run identity, not host behavior):
  * pid-stamped node/module names  r79lb_<digits> / r79fc_<digits> -> <pid>
  * the run's own pid leaf         .contention.own_pid -> <pid>
  * TemporaryDirectory paths       /tmp/capture-r79-*/ and /tmp/r79fc-* -> <tmp>

Declared drift classes (regexes on the flattened leaf path) are read from
--allow; every leaf outside them must be equal, including the key set.
--group prints all diffs grouped by path shape (indices -> [n]) instead.
"""
import json
import re
import sys
from collections import Counter, OrderedDict

PID = re.compile(r"(r79lb|r79fc)_\d+")
TMP = re.compile(r"/tmp/(?:capture-r79-[a-z]+-|r79fc-)[A-Za-z0-9_]+")
NUM = re.compile(r"\[\d+\]")


def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{p}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{p}[{i}]")
    else:
        yield p, o


def norm_key(k):
    return NUM.sub("[n]", k)


def norm_val(k, v):
    if isinstance(v, str):
        v = PID.sub(r"\1_<pid>", v)
        v = TMP.sub("<tmp>", v)
        return v
    if k.endswith(".own_pid") and isinstance(v, int):
        return "<pid>"
    return v


def load(path):
    d = json.load(open(path))
    out = OrderedDict()
    for k, v in leaves(d):
        k = TMP.sub("<tmp>", PID.sub(r"\1_<pid>", k))
        out[k] = norm_val(k, v)
    return out


def main():
    a_path, b_path = sys.argv[1], sys.argv[2]
    allow = []
    if "--allow" in sys.argv:
        allow = [l.strip() for l in
                 open(sys.argv[sys.argv.index("--allow") + 1])
                 if l.strip() and not l.startswith("#")]
    group = "--group" in sys.argv

    A, B = load(a_path), load(b_path)
    ka, kb = set(A), set(B)
    only_a, only_b = sorted(ka - kb), sorted(kb - ka)
    diffs = [(k, A[k], B[k]) for k in sorted(ka & kb) if A[k] != B[k]]

    if group:
        shapes = Counter()
        for k, va, vb in diffs:
            shapes[norm_key(k)] += 1
        print(f"leaves A={len(A)} B={len(B)} differing={len(diffs)} "
              f"key-only-A={len(only_a)} key-only-B={len(only_b)}")
        for shape, n in shapes.most_common():
            sample = next(k for k, _, _ in diffs
                          if norm_key(k) == shape)
            print(f"  {n:5d}  {shape}   e.g. {A[sample]!r} -> {B[sample]!r}")
        for k in only_a[:20]:
            print(f"  ONLY-A {k} = {A[k]!r}")
        for k in only_b[:20]:
            print(f"  ONLY-B {k} = {B[k]!r}")
        return 0

    def declared(k):
        return any(re.search(p, k) for p in allow)

    undeclared = [(k, va, vb) for k, va, vb in diffs if not declared(k)]
    declared_n = len(diffs) - len(undeclared)
    print(f"leaves compared         : {len(ka | kb)}")
    print(f"key-set diffs           : {len(only_a)} only-A, "
          f"{len(only_b)} only-B")
    print(f"value diffs             : {len(diffs)}")
    print(f"  declared drift        : {declared_n}")
    print(f"  UNDECLARED            : {len(undeclared)}")
    for k, va, vb in undeclared[:40]:
        print(f"    ! {k}: {va!r} -> {vb!r}")
    for k in only_a[:20]:
        print(f"    ! only-A {k} = {A[k]!r}")
    for k in only_b[:20]:
        print(f"    ! only-B {k} = {B[k]!r}")
    fa = A.get(".measurements.loopback_shape_r79_probe.failures")
    fb = B.get(".measurements.loopback_shape_r79_probe.failures")
    ok = not undeclared and not only_a and not only_b
    print(f"VERDICT: {'PASS' if ok else 'FAIL'} "
          f"(A={len(only_a)} B={len(only_b)} "
          f"undeclared={len(undeclared)} declared={declared_n})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
