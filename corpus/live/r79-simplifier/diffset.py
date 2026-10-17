#!/usr/bin/env python3
"""Diff-set classifier for the r79 healthy pair.

    python3 diffset.py base.json other.json          # one comparison
    python3 diffset.py base.json a.json b.json       # base vs a, base vs b,
                                                     # and the containment check

Normalization (per-run identity only):
  * pid-stamped r79 names      r79lb_<tag>_<pid> / r79fc_<tag>_<pid> -> _<pid>
  * the run's own pid leaf     .contention.own_pid -> <pid>
  * TemporaryDirectory paths   /tmp/capture-r79-*/ and /tmp/r79fc-* -> <tmp>
  * pw-cli/pipewire log noise  [W][hh:mm:ss.ffffff] -> [W][<t>], 0xhex -> <ptr>

Reports, for each comparison: differing leaves grouped by shape (indices ->
[n]), tail keys of longer arrays, and the key-set diffs. With three receipts
it also checks that every base-vs-b diff shape also appears as a base-vs-a
diff shape (the fold's diff set must be contained in the host's own noise).
"""
import json
import re
import sys
from collections import Counter, OrderedDict

PID = re.compile(r"((?:r79lb|r79fc)(?:_[A-Za-z0-9]+)*?)_\d{6,}")
CHILD = re.compile(r"(pw-loopback-)\d+|(loopback-)\d+-\d+")
TMP = re.compile(r"/tmp/(?:capture-r79-[a-z]+-|r79fc-)[A-Za-z0-9_]+")
TS = re.compile(r"\[\d\d:\d\d:\d\d\.\d+\]")
PTR = re.compile(r"0x[0-9a-f]{6,}")
NUM = re.compile(r"\[\d+\]")
TAILARR = re.compile(r"\.windows$")


def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{p}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{p}[{i}]")
    else:
        yield p, o


def norm(k, v):
    if isinstance(v, str):
        v = PID.sub(r"\1_<pid>", v)
        v = CHILD.sub(lambda m: (m.group(1) or m.group(2)) + "<pid>", v)
        v = TMP.sub("<tmp>", v)
        v = TS.sub("[<t>]", v)
        v = PTR.sub("<ptr>", v)
    if k.endswith(".own_pid") and isinstance(v, int):
        return "<pid>"
    return v


def load(path):
    out = OrderedDict()
    for k, v in leaves(json.load(open(path))):
        k = TMP.sub("<tmp>", PID.sub(r"\1_<pid>", k))
        out[k] = norm(k, v)
    return out


def shape(k):
    return NUM.sub("[n]", k)


def compare(a_path, b_path):
    A, B = load(a_path), load(b_path)
    ka, kb = set(A), set(B)
    only_a = [k for k in sorted(ka - kb) if shape(k) not in {shape(x) for x in kb}]
    only_b = [k for k in sorted(kb - ka) if shape(k) not in {shape(x) for x in ka}]
    # tail keys: same shape exists on the other side -> array-length drift
    tail_a = [k for k in sorted(ka - kb) if k not in only_a]
    tail_b = [k for k in sorted(kb - ka) if k not in only_b]
    diffs = [(k, A[k], B[k]) for k in sorted(ka & kb) if A[k] != B[k]]
    return A, B, diffs, only_a, only_b, tail_a, tail_b


def report(tag, a_path, b_path):
    A, B, diffs, only_a, only_b, tail_a, tail_b = compare(a_path, b_path)
    shapes = Counter(shape(k) for k, _, _ in diffs)
    print(f"--- {tag}: {a_path.split('/')[-3]} vs {b_path.split('/')[-3]}")
    print(f"    leaves A={len(A)} B={len(B)}  value-diffs={len(diffs)}  "
          f"key-only A={len(only_a)} B={len(only_b)}  "
          f"array-tail keys A={len(tail_a)} B={len(tail_b)}")
    for s, n in shapes.most_common(14):
        print(f"      {n:5d}  {s}")
    if only_a:
        print("    UNMATCHED only-A:", only_a[:6])
    if only_b:
        print("    UNMATCHED only-B:", only_b[:6])
    return {shape(k) for k, _, _ in diffs} | {shape(k) for k in only_a} | \
           {shape(k) for k in only_b}


def main():
    if len(sys.argv) == 3:
        report("pair", sys.argv[1], sys.argv[2])
        return 0
    base, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
    sa = report("base-vs-A (host baseline)", base, a)
    sb = report("base-vs-B (fold candidate)", base, b)
    extra = sorted(sb - sa)
    print(f"\nshapes only in base-vs-B (NOT explained by host noise): "
          f"{len(extra)}")
    for s in extra:
        print("   !", s)
    return 1 if extra else 0


if __name__ == "__main__":
    sys.exit(main())
