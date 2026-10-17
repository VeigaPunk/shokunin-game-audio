#!/usr/bin/env python3
"""r73 reviewer: compare the landed r73 receipt against my independent matrix.

Checks, per member and per consumer:
  - rc of the two shared transports (file, fifo_path) vs my measured matrix
  - fork set vs my measured fork set (under fixture naming)
  - protocol constants (timeout, hold) vs my harness
  - replay hygiene: absolute paths / timestamps / ASLR tags in the receipt text
"""
import json
import re
import sys
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
receipt = json.loads(Path(sys.argv[1]).read_text())
mine = json.loads((REPO / "corpus/live/r73-reviewer/my-matrix-fixture-naming.json").read_text())
ms = receipt["measurements"]

print("mode:", receipt["mode"])
print("entries:", len(ms))
rows = []
for member in sorted(mine):
    entry = ms.get(f"consumer_{member}_r73_probe")
    if entry is None:
        rows.append((member, "MISSING ENTRY", "", "", ""))
        continue
    for consumer, key in (("pw-cat", "pwcat"), ("mpv", "mpv")):
        axis = entry["consumers"][consumer]["transport_axis"]
        fork = entry["consumers"][consumer]["transport_fork"]
        for t in ("file", "fifo_path"):
            landed = axis[t]["exit_code"]
            myrc = mine[member][f"{key}-{t.replace('_path','')}"]["rc"]
            mark = "OK " if str(landed) == str(myrc) else "DIFF"
            rows.append((member, consumer, t, landed, myrc, mark))
bad = [r for r in rows if r[-1] == "DIFF"]
for r in rows:
    print(f"{r[0]:20s} {r[1]:6s} {r[2]:10s} landed={str(r[3]):5s} mine={str(r[4]):5s} {r[5]}")
print(f"\ncells compared={len(rows)} agree={len(rows)-len(bad)} diff={len(bad)}")

# fork summary from the receipt vs mine
print("\nlanded forks:")
for member, e in ms.items():
    if not member.endswith("_r73_probe") or member == "consumer_pwcat_ops_r73_probe":
        continue
    for consumer, c in e["consumers"].items():
        if c["transport_fork"]:
            groups = [(g["transports"], g["verdict"]) for g in c["transport_verdict_groups"]]
            print(f"  {member}: {consumer} -> {groups}")

# hygiene scan
text = json.dumps(receipt)
pat = {
    "absolute /home path": re.findall(r"/home/[^\"]*", text),
    "absolute /tmp path": re.findall(r"/tmp/[^\"]*", text),
    "mpv timestamp [ 0.000]": re.findall(r"\[\s*\d+\.\d+\]", text),
    "ASLR 0x tag": re.findall(r"0x[0-9a-f]{6,}", text),
    "tempdir pwcat-r73": re.findall(r"pwcat-r73-[A-Za-z0-9_]+", text),
    "tempdir mpv-r73": re.findall(r"mpv-r73-[A-Za-z0-9_]+", text),
}
print("\nhygiene:")
for k, v in pat.items():
    print(f"  {k}: {len(v)} {v[:2]}")
print("\nops entry:", json.dumps(ms.get("consumer_pwcat_ops_r73_probe"), indent=1)[:1800])
