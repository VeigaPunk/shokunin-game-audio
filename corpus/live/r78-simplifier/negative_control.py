#!/usr/bin/env python3
"""r78 SIMPLIFIER negative control: the comparator must catch a verdict-leaf
flip and a removed leaf (otherwise the A = 0 result is vacuous).

usage: negative_control.py CONTROL_RECEIPT CAND_RECEIPT
writes /tmp/r78-simpl/negctl-{flip,drop}.json and prints the two comparator
verdicts.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path("/tmp/r78-simpl")
CTL, CAND = sys.argv[1], sys.argv[2]


def load(p):
    return json.load(open(p))


def save(rec, name):
    p = HERE / name
    json.dump(rec, open(p, "w"), indent=1, allow_nan=False)
    return str(p)


def run(a, b):
    out = subprocess.run(["python3", str(HERE / "compare_r78.py"), a, b],
                         capture_output=True, text=True)
    line = [l for l in out.stdout.splitlines() if l.startswith("VERDICT")]
    strict = [l for l in out.stdout.splitlines() if l.startswith("  STRICT")]
    return (line[0] if line else "NO VERDICT"), strict[:6]


def main():
    cand = load(CAND)
    # 1. flip one pinned verdict leaf (the lattice's content witness)
    flip = json.loads(json.dumps(cand))
    leg = flip["measurements"]["playback_target_lattice_r78_probe"]["legs"]
    name = sorted(leg)[0]
    leg[name]["carries_tone"] = not leg[name]["carries_tone"]
    p1 = save(flip, "negctl-flip.json")
    v1, s1 = run(CTL, p1)
    print(f"[flip carries_tone on {name}] {v1}")
    for l in s1:
        print("   ", l.strip())
    # 2. drop a whole derived table (the R1 candidate)
    drop = json.loads(json.dumps(cand))
    del drop["measurements"]["playback_target_lattice_r78_probe"][
        "default_sink_trace"]
    p2 = save(drop, "negctl-drop.json")
    v2, s2 = run(CTL, p2)
    print(f"[drop default_sink_trace] {v2}")
    for l in s2[:3]:
        print("   ", l.strip())
    caught = "FAIL" in v1 and "FAIL" in v2
    print("NEGATIVE CONTROL:", "PASS (both mutations caught)" if caught
          else "FAIL (comparator blind)")
    return 0 if caught else 1


if __name__ == "__main__":
    sys.exit(main())
