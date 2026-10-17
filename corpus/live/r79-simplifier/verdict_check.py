#!/usr/bin/env python3
"""Three-tier receipt check: strict verdict leaves / host-content leaves /
declared identity+timing classes.

    python3 verdict_check.py base.json cand.json [--show-host]

STRICT is every leaf that is neither a declared class (classes.txt) nor a
host-content witness (audio magnitudes, shared-sink link content, spawn-time
host snapshots). STRICT must be empty; host-content and declared diffs are
reported by class so nothing is hidden.
"""
import json
import re
import sys
from collections import Counter, OrderedDict

import diffset as D

DECLARED = [
    (r"\.client_id$", "identity: daemon client id"),
    (r"\.module_id$", "identity: daemon module id"),
    (r"\.loaded\[\d+\]$", "identity: daemon module id"),
    (r"\.wall_s$", "timing: wall clock"),
    (r"\.when_s$", "timing: event clock"),
    (r"\.waited_s$", "timing: port-gate wait"),
    (r"\.monitor_waited_s$", "timing: monitor-gate wait"),
    (r"\.applied_in_s$", "timing: metadata apply"),
    (r"\.samples\[\d+\]\.at_s$", "timing: measured sample clock"),
    (r"\.latency_param(\[\d+\])?\.", "per-run negotiated stream params"),
    (r"\.contention\.", "host: sibling-process snapshot"),
]

HOST = [
    (r"\.(tap|tap_flag_sink)\.windows\[\d+\]\.(f_l|f_r|a_l|a_r|audio|mine)$",
     "host: tap window content"),
    (r"\.(tap|tap_flag_sink)\.(audio_windows|zero_windows|peak_l|peak_r)$",
     "host: tap content aggregate"),
    (r"\.(content|two_tone)\.windows\[\d+\]\.", "host: record/tap windows"),
    (r"\.two_tone\.channels\[\d+\]\.(at_l|at_r|peak)$",
     "host: two-tone magnitudes"),
    (r"\.two_tone\.mix_half_gain_ratio$", "host: derived half-gain ratio"),
    (r"\.mix_half_gain_ratio$", "host: derived half-gain ratio"),
    (r"\.oracle_at_(leg|start)\.", "host: spawn-time authority snapshot"),
    (r"\.inventory\.", "host: enumeration snapshot"),
    (r"\.sources(\.|$)", "host: source enumeration"),
    (r"\.default_(source|sink)_at_leg$", "host: leg's spawn-time default"),
    (r"\.tap_witnesses\.", "host: tap's actual producers"),
    (r"\.samples\[\d+\]\.watch\..*\.(consumers|producers|consumer_ports|"
     r"producer_ports)(\[\d+\])?$", "host: live link content"),
    (r"\.confound$", "host: named confound"),
    (r"\.foreign_tone_witness\.", "host: foreign-tone witness"),
    (r"\.stderr_scan$", "host: loader log (timestamps/pointers)"),
    # the `-P @SRC@` leg substitutes the host's enumerated first non-default
    # source: the stored request and the advertised target are host inputs.
    (r"\.c04_source_name\.tail\[\d+\]$", "host: @SRC@ substitution"),
    (r"\.c04_source_name\.target_object_advertised$",
     "host: @SRC@ substitution"),
    (r"\.c04_source_name\.samples\[\d+\]\.nodes\.(input|output)\..*"
     r"\.target_object$", "host: @SRC@ substitution"),
]

# key-set (array tail) diffs that are host/identity, not verdict moves: an
# EXTRA element in a union/loaded array. Value moves inside the common prefix
# stay strict; every hit here is named in the report.
KEYSET = [
    (r"\.loaded\[\d+\]$", "identity: extra module id"),
    (r"\.(input_producers_union|output_consumers_union|consumers_union|"
     r"producers_union|bound_producers)\[\d+\]$",
     "host: extra element in a live union (foreign node)"),
    (r"\.latency_param\[\d+\]\.", "host: extra negotiated param block"),
    (r"\.(f7_cli_load|f8_unload_refusal|f9_bad_label|f10_bad_args)"
     r"\.reply\[\d+\]$", "host: pw-cli transcript tail (chunked read)"),
]


def classify(k, keyset=False):
    for pat, name in DECLARED:
        if re.search(pat, k):
            return ("declared", name)
    for pat, name in HOST:
        if re.search(pat, k):
            return ("host", name)
    if keyset:
        for pat, name in KEYSET:
            if re.search(pat, k):
                return ("host", name)
    return ("strict", "")


def main():
    A, B = D.load(sys.argv[1]), D.load(sys.argv[2])
    show_host = "--show-host" in sys.argv
    ka, kb = set(A), set(B)
    keys = ka & kb
    diffs = [(k, A[k], B[k]) for k in sorted(keys) if A[k] != B[k]]
    only_a = sorted(ka - kb)
    only_b = sorted(kb - ka)

    buckets = {"strict": [], "host": [], "declared": []}
    for k, va, vb in diffs:
        tier, name = classify(k)
        buckets[tier].append((k, va, vb, name))

    ks_buckets = {"strict": [], "host": [], "declared": []}
    for k in only_a + only_b:
        tier, name = classify(k, keyset=True)
        ks_buckets[tier].append((k, A.get(k, B.get(k)), name))

    print(f"leaves A={len(A)} B={len(B)}  value-diffs={len(diffs)}  "
          f"key-only A={len(only_a)} B={len(only_b)}")
    for tier in ("strict", "host", "declared"):
        rows = buckets[tier]
        print(f"\n[{tier.upper()}] {len(rows)} diffs")
        per = Counter(name for _, _, _, name in rows)
        for name, n in per.most_common():
            print(f"   {n:5d}  {name}")
        if tier != "host" or show_host:
            for k, va, vb, name in rows[:25]:
                print(f"      {k}\n        A={va!r}\n        B={vb!r}")
    for tier in ("strict", "host", "declared"):
        rows = ks_buckets[tier]
        if not rows:
            continue
        print(f"\n[KEY-SET {tier.upper()}] {len(rows)} diffs")
        per = Counter(name for _, _, name in rows)
        for name, n in per.most_common():
            print(f"   {n:5d}  {name}")
        if tier != "host" or show_host:
            for k, v, name in rows[:25]:
                print(f"      {k} = {v!r}")
    ok = (not buckets["strict"] and not ks_buckets["strict"])
    print(f"\nVERDICT: {'PASS' if ok else 'FAIL'} "
          f"(strict={len(buckets['strict'])}+{len(ks_buckets['strict'])} "
          f"host={len(buckets['host'])}+{len(ks_buckets['host'])} "
          f"declared={len(buckets['declared'])}+{len(ks_buckets['declared'])})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
