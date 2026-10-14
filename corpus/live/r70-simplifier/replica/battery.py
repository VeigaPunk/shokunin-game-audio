#!/usr/bin/env python3
"""r70-simplifier byte-stability battery: run prior ledger modes inside the
replica tree (HEAD + landed r70 overlay) and compare each fresh receipt
byte-for-byte against the committed r69-ledger receipt for the same mode.

Replica runs write receipts under replica/tree/corpus/live/runs/<stamp>-<suf>/.
The committed receipt path for each mode comes from r69-author/ledger-r69.tsv
(col 3); the suffix after the timestamp names the mode.
"""
import json
import subprocess
import sys
from pathlib import Path

REPLICA = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r70-simplifier/replica/tree")
MEASURE = REPLICA / "corpus/fixtures/measure_audio.py"
R69_TSV = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r69-author/ledger-r69.tsv")
OUT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r70-simplifier/replica/battery-results.txt")

# mode-flag -> receipt-dir suffix (as produced by measure_audio.py)
MODES = [
    ("", "-normal"),
    ("--probe-transport-extsuffix-wav-r69", "-transport-extsuffix-wav-r69"),
    ("--probe-transport-extsuffix-bin-r69", "-transport-extsuffix-bin-r69"),
    ("--probe-transport-extsuffix-txw-r69", "-transport-extsuffix-txw-r69"),
    ("--probe-transport-extsuffix-f32-r69", "-transport-extsuffix-f32-r69"),
    ("--probe-transport-extsuffix-snd-r69", "-transport-extsuffix-snd-r69"),
    ("--probe-transport-posttable-nomatch-r68", "-transport-posttable-nomatch-r68"),
    ("--probe-transport-txw-piperefuse-r68", "-transport-txw-piperefuse-r68"),
    ("--probe-transport-preempt-act-r67", "-transport-preempt-act-r67"),
    ("--probe-transport-preempt-gsrt-r67", "-transport-preempt-gsrt-r67"),
    ("--probe-transport-preempt-hcom-r67", "-transport-preempt-hcom-r67"),
    ("--probe-transport-preempt-both-r67", "-transport-preempt-both-r67"),
    ("--probe-transport-dec-hcom-r67", "-transport-dec-hcom-r67"),
    ("--probe-transport-dec-act-r67", "-transport-dec-act-r67"),
    ("--probe-transport-lengate-gsrt-24-r67", "-transport-lengate-gsrt-24-r67"),
    ("--probe-transport-lengate-gsrt-25-r67", "-transport-lengate-gsrt-25-r67"),
    ("--probe-transport-lengate-hcom-131-r67", "-transport-lengate-hcom-131-r67"),
    ("--probe-transport-lengate-hcom-132-r67", "-transport-lengate-hcom-132-r67"),
    ("--probe-ui-dec-hcom-r66", "-ui-dec-hcom-r66"),
    ("--probe-ui-dec-act-r66", "-ui-dec-act-r66"),
    ("--probe-ui-lengate-hcom-132-r66", "-ui-lengate-hcom-132-r66"),
    ("--probe-ui-preempt-act-r65", "-ui-preempt-act-r65"),
    ("--probe-ui-extensible-valid-8-r64", "-ui-extensible-valid-8-r64"),
    ("--probe-ui-route-act-84-r63", "-ui-route-act-84-r63"),
    ("--probe-ui-extensible-valid-17-r61", "-ui-extensible-valid-17-r61"),
    ("--probe-invalid", "-invalid"),
]


def committed_for(suffix):
    """Committed r69-ledger receipt path for a receipt-dir suffix."""
    for line in R69_TSV.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[2].endswith(suffix + "/measurements.json"):
            return parts[1], Path(parts[2])
    return None, None


def main():
    results = []
    for flag, suffix in MODES:
        argv = [sys.executable, str(MEASURE)] + ([flag] if flag else [])
        proc = subprocess.run(argv, capture_output=True, text=True, cwd=REPLICA)
        try:
            receipt_path = Path(json.loads(proc.stdout.strip().splitlines()[-1])["receipt"])
        except Exception:
            results.append((flag or "normal", f"UNPARSED rc={proc.returncode} "
                            f"out={proc.stdout[-160:]!r} err={proc.stderr[-160:]!r}"))
            continue
        cexit, committed = committed_for(suffix)
        if committed is None:
            results.append((flag or "normal", f"no committed receipt for {suffix}"))
            continue
        same = receipt_path.read_bytes() == committed.read_bytes()
        results.append((flag or "normal",
                        f"exit={proc.returncode} committed-exit={cexit} "
                        f"{'IDENTICAL' if same else 'DIFFERS'} "
                        f"replica={receipt_path.name}"))
        print(results[-1][0], "->", results[-1][1], flush=True)
    OUT.write_text("\n".join(f"{m}\t{r}" for m, r in results) + "\n")
    bad = [m for m, r in results if "IDENTICAL" not in r]
    print(f"\n{len(results)} modes; non-identical: {bad}")


if __name__ == "__main__":
    main()
