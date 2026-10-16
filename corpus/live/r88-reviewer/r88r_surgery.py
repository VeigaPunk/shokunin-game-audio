#!/usr/bin/env python3
"""r88 reviewer — insertion-only surgery proof.

Reconstruct the parent blob (a7d2367b) from the committed blob (c19bec96)
by (1) dropping the inserted r88 block, (2) dropping the pure-new wiring
lines, (3) removing the inserted terms from the three shared splice lines.
Byte-exact reconstruction => insertion-only, prior rows untouched.
"""
import hashlib
import re
import sys

COMMIT = "corpus/live/r88-reviewer/pins/measure_audio.c19bec96.py"
PARENT = "corpus/live/r88-reviewer/pins/measure_audio.a7d2367b.py"

src = open(COMMIT).read().split("\n")
lines = src[:]  # keep trailing element from final newline

# 1. the r88 block: committed lines 27507..29254 (1-based) — the 1748
#    lines between the r87 midi entry and `def main():`
assert lines[27506].startswith("# r88: the BLUEZ ABSENT-CLASS"), \
    lines[27506][:60]
assert lines[29254] == "def main():", lines[29254][:60]
assert lines[29253] == "" and lines[29252] == "", (29252, 29253)
del lines[27506:29254]  # 1-based 27507..29254

# 2. pure-new wiring line
n = [i for i, l in enumerate(lines)
     if l == '    parser.add_argument("--probe-btwit-r88", action="store_true")']
assert len(n) == 1, n
del lines[n[0]]

# 3. the 20-line main() branch (pure insertion)
n = [i for i, l in enumerate(lines) if l == "    if args.probe_btwit_r88:"]
assert len(n) == 1, n
i0 = n[0]
assert lines[i0 + 19] == "            pwtop_r88_entry()", lines[i0 + 19]
del lines[i0:i0 + 20]

# 4. the three splice lines: remove the inserted terms
n = [i for i, l in enumerate(lines) if l.startswith("    if sum([")]
assert len(n) == 1, n
before = lines[n[0]]
lines[n[0]] = before.replace(", args.probe_btwit_r88]) > 1:",
                             "]) > 1:")
assert lines[n[0]] != before, "sum splice not reversed"

n = [i for i, l in enumerate(lines) if l.startswith("    mode = ")]
assert len(n) == 1, n
before = lines[n[0]]
lines[n[0]] = before.replace('"probe-btwit-r88" if args.probe_btwit_r88 else ', "", 1)
assert lines[n[0]] != before, "mode splice not reversed"

n = [i for i, l in enumerate(lines) if l.startswith("    suffix = ")]
assert len(n) == 1, n
before = lines[n[0]]
lines[n[0]] = before.replace('"-btwit-r88" if args.probe_btwit_r88 else ', "", 1)
assert lines[n[0]] != before, "suffix splice not reversed"

rebuilt = "\n".join(lines).encode()
parent = open(PARENT, "rb").read()
h = hashlib.sha256(rebuilt).hexdigest()
ph = hashlib.sha256(parent).hexdigest()
print("rebuilt sha256:", h)
print("parent  sha256:", ph)
print("parent  recorded: be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516")
print("BYTE-EXACT" if rebuilt == parent else "MISMATCH")
sys.exit(0 if rebuilt == parent else 1)
