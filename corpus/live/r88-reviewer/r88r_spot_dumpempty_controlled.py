#!/usr/bin/env python3
"""r88 reviewer SPOT — controlled reproduction of the wd_dump_empty
false-FAIL under churn.

Control iteration: c1 / pw-dump '' / c2 with no injected churn -> the
arm passes.  Churn iteration: a seat-owned null sink (r88r_churn_<pid>,
name-verified unload by module index) is created between c1 and the ''
dump and removed before c2 -> the arm sees two different brackets and
false-FAILs exactly as r88r2 did.  Read-only on foreign objects; only
its own sink is created and destroyed.
"""
import json
import os
import re
import subprocess
import sys
import time

PID = os.getpid()
NAME = f"r88r_churn_{PID}"


def dump_ids(*args):
    out = subprocess.run(["pw-dump", *args], capture_output=True,
                         timeout=30).stdout
    return sorted(str(o.get("id")) for o in json.loads(out))


def mods():
    out = subprocess.run(["pactl", "list", "modules", "short"],
                         capture_output=True, timeout=10).stdout.decode()
    return {int(m.group(1)): m.group(2)
            for m in re.finditer(r"^(\d+)\t(.*)$", out, re.M)}


def main():
    results = []
    for mode in ("control", "churn"):
        c1 = dump_ids()
        idx = None
        if mode == "churn":
            p = subprocess.run(
                ["pactl", "load-module", "module-null-sink",
                 f"sink_name={NAME}"], capture_output=True, timeout=15)
            idx = int(p.stdout.decode().strip())
            time.sleep(0.3)
        e = dump_ids("")
        if mode == "churn":
            # name-verified unload: same index must still carry our name
            m = mods()
            args = m.get(idx, "")
            if NAME not in args:
                print(f"REFUSING unload: index {idx} args={args!r}",
                      file=sys.stderr)
                sys.exit(2)
            subprocess.run(["pactl", "unload-module", str(idx)],
                           capture_output=True, timeout=15)
            time.sleep(0.3)
        c2 = dump_ids()
        rec = {"mode": mode, "module_index": idx,
               "n_c1": len(c1), "n_e": len(e), "n_c2": len(c2),
               "eq_before": e == c1, "eq_after": e == c2,
               "delta_before": len(set(e) ^ set(c1)),
               "delta_after": len(set(e) ^ set(c2)),
               "arm_false_fail": (e != c1 and e != c2)}
        results.append(rec)
        print(json.dumps(rec), flush=True)
    sinks = subprocess.run(["pactl", "list", "sinks", "short"],
                           capture_output=True, timeout=10).stdout.decode()
    rec = {"teardown": {"own_sink_still_present": NAME in sinks,
                        "module_gone":
                        all(NAME not in a for a in mods().values())}}
    results.append(rec)
    print(json.dumps(rec), flush=True)
    with open("corpus/live/r88-reviewer/receipts/"
              "spot-dumpempty-controlled.json", "w") as fh:
        json.dump(results, fh, indent=1)


if __name__ == "__main__":
    main()
