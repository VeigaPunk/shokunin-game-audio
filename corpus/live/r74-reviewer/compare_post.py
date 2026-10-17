#!/usr/bin/env python3
"""r74 reviewer — post-landing receipt comparator.

1. consumers-r73: compare the 9 member entries + all pre-existing ops cells
   against the pre-landing receipt, ignoring any NEW key/sub-block the author
   added inside consumer_pwcat_ops_r73_probe (the briefed ops-2 extension).
2. other prior rows: strict byte compare.
Usage: compare_post.py <pre.json> <post.json> [--ops-extended]
"""
import json
import sys


def strip_new_ops(pre_ops, post_ops):
    """Return post_ops minus keys absent from pre_ops, plus the list of added keys."""
    added = sorted(set(post_ops) - set(pre_ops))
    kept = {k: v for k, v in post_ops.items() if k in pre_ops}
    return kept, added


def main():
    pre = json.load(open(sys.argv[1]))
    post = json.load(open(sys.argv[2]))
    ops_extended = "--ops-extended" in sys.argv
    diffs = []
    added_keys = []
    for k in pre["measurements"]:
        if k not in post["measurements"]:
            diffs.append(f"missing key {k}")
            continue
        a, b = pre["measurements"][k], post["measurements"][k]
        if ops_extended and k == "consumer_pwcat_ops_r73_probe":
            a2, b2 = dict(a), dict(b)
            a2.pop("failures", None); b2.pop("failures", None)
            kept, added = strip_new_ops(a2, b2)
            added_keys = added
            a_cmp, b_cmp = a2, kept
            if json.dumps(a_cmp, sort_keys=True) != json.dumps(b_cmp, sort_keys=True):
                # locate the differing leaves
                for kk in set(a_cmp) | set(b_cmp):
                    if a_cmp.get(kk) != b_cmp.get(kk):
                        diffs.append(f"{k}.{kk} changed")
        else:
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                diffs.append(f"{k} changed")
    new_keys = sorted(set(post["measurements"]) - set(pre["measurements"]))
    print(json.dumps({"added_ops_keys": added_keys, "new_measurement_keys": new_keys,
                      "diffs": diffs, "identical": not diffs}, indent=2))
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main())
