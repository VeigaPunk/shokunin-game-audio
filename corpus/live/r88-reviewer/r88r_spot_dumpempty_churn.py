#!/usr/bin/env python3
"""r88 reviewer SPOT — churn sensitivity of the wd_dump_empty arm.

The fixture's arm: e_ids (pw-dump '') must equal the c1 OR c2 bracketing
census id-set exactly.  This spot replicates that measurement N times
(read-only: pw-dump only) and reports, per iteration:
  eq_before / eq_after  — would the arm pass?
  delta_before / delta_after — the churn delta (ids only in one side)
"""
import json
import subprocess
import sys
import time


def dump_ids(*args):
    out = subprocess.run(["pw-dump", *args], capture_output=True,
                         timeout=30).stdout
    return sorted(str(o.get("id")) for o in json.loads(out))


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    results = []
    for i in range(n):
        c1 = dump_ids()
        e = dump_ids("")
        c2 = dump_ids()
        db = sorted(set(e) ^ set(c1))
        da = sorted(set(e) ^ set(c2))
        rec = {"i": i, "n_c1": len(c1), "n_e": len(e), "n_c2": len(c2),
               "eq_before": e == c1, "eq_after": e == c2,
               "delta_before": len(db), "delta_after": len(da),
               "delta_before_ids": db[:6], "delta_after_ids": da[:6]}
        results.append(rec)
        print(json.dumps(rec), flush=True)
        time.sleep(0.2)
    both = sum(1 for r in results if not r["eq_before"] and not r["eq_after"])
    print(json.dumps({"summary": {"n": n, "arm_false_fail": both,
                                  "arm_pass": n - both}}))
    with open("corpus/live/r88-reviewer/receipts/spot-dumpempty-churn.json",
              "w") as fh:
        json.dump(results, fh, indent=1)


if __name__ == "__main__":
    main()
