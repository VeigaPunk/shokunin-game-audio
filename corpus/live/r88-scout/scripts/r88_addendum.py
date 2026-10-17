#!/usr/bin/env python3
"""r88 scout addendum — the pw-dump id-or-serial set rule, pw-top first-refresh
artifact, and tight same-window state triple. Fresh processes, receipts only."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
REC = ROOT / "receipts"

COMPOSITE = (
    'echo "== cli =="; pw-cli info 46 2>/dev/null | grep -m1 state; '
    'echo "== dump =="; pw-dump 46 2>/dev/null | jq -r \'.[] | select(.id==46) | .info.state\'; '
    'echo "== ptop-r2 =="; pw-top -b -n 2 2>/dev/null | grep " 46 " | tail -1 | awk \'{print $1, $2}\''
)


def run(argv):
    t0 = datetime.now(timezone.utc)
    p = subprocess.run(argv, capture_output=True, text=True, timeout=25)
    return {
        "argv": argv, "rc": p.returncode,
        "stdout_sha256": hashlib.sha256(p.stdout.encode()).hexdigest(),
        "stdout": p.stdout, "stderr": p.stderr,
        "start_utc": t0.isoformat(),
    }


def leg(name, argv, reps=3, ext="txt"):
    rows = []
    for i in range(1, reps + 1):
        r = run(argv)
        rows.append({k: v for k, v in r.items() if k not in ("stdout", "stderr")})
        (RAW / f"{name}.{i}.{ext}").write_text(r["stdout"])
        (RAW / f"{name}.{i}.err").write_text(r["stderr"])
    return {
        "leg": name, "argv": argv, "reps": reps,
        "stable_stdout": len({r["stdout_sha256"] for r in rows}) == 1,
        "rcs": [r["rc"] for r in rows],
        "stdout_sha256": [r["stdout_sha256"] for r in rows],
        "rows": rows,
    }


def main():
    legs = []
    # 1. discriminator: same key 60 on the two witnesses
    legs.append(leg("add-dump-60", ["pw-dump", "60"], ext="json"))
    legs.append(leg("add-cli-info-60", ["pw-cli", "info", "60"]))
    legs.append(leg("add-cli-format-60", ["pw-cli", "enum-params", "60", "Format"]))
    # 2. set-rule membership probes
    for i in (32, 33, 45, 35, 46):
        legs.append(leg(f"add-dump-{i}", ["pw-dump", str(i)], ext="json"))
    # 3. pw-top refresh artifact
    legs.append(leg("add-pwtop-n2", ["pw-top", "-b", "-n", "2"]))
    legs.append(leg("add-pwtop-n3", ["pw-top", "-b", "-n", "3"]))
    # 4. tight same-window state triple (one process, back-to-back commands)
    legs.append(leg("add-state-triple", ["bash", "-c", COMPOSITE]))
    # 5. params surface on the bluez-adjacent node and a null sink
    legs.append(leg("add-cli-enumfmt-133", ["pw-cli", "enum-params", "133", "EnumFormat"]))
    legs.append(leg("add-cli-enumfmt-35", ["pw-cli", "enum-params", "35", "EnumFormat"]))
    legs.append(leg("add-cli-io-35", ["pw-cli", "enum-params", "35", "IO"]))
    # 6. static docs witness for the state legend
    legs.append(leg("add-pwtop-man", ["bash", "-c", "man pw-top | col -b"], reps=1))

    out = {
        "harness": "r88_addendum.py",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "legs": legs,
    }
    (REC / "r88-addendum.json").write_text(json.dumps(out, indent=1))
    print(f"addendum legs={len(legs)} unstable={[l['leg'] for l in legs if not l['stable_stdout']]}")


if __name__ == "__main__":
    main()
