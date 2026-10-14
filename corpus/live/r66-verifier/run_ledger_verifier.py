#!/usr/bin/env python3
"""r66 verifier ledger: replay the author's exact 102-command MODES list
(imported from corpus/live/r66-author/run_ledger.py so the command list is
the committed author's, not re-typed). Run from the worktree root.
Writes corpus/live/r66-verifier/ledger-r66-verifier.tsv:
  idx \t exit \t receipt_path \t failure_summary
"""
import json
import subprocess
import sys
from pathlib import Path

AUTHOR = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r66-author")
sys.path.insert(0, str(AUTHOR))
from run_ledger import MODES  # committed 102-entry list
assert len(MODES) == 102, len(MODES)

MEASURE = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/fixtures/measure_audio.py"
TSV = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r66-verifier/ledger-r66-verifier.tsv")


def main():
    with TSV.open("w") as fh:
        for i, flag in enumerate(MODES, 1):
            cmd = ["python3", MEASURE] + ([flag] if flag else [])
            proc = subprocess.run(cmd, capture_output=True, text=True)
            receipt = "-"
            failsum = "none"
            try:
                payload = json.loads(proc.stdout.strip().splitlines()[-1])
                receipt = payload.get("receipt", "-")
                fails = payload.get("failures", {})
                if fails:
                    failsum = "; ".join(f"{k}: {'; '.join(v) if isinstance(v, list) else v}"
                                        for k, v in fails.items())
            except Exception:
                failsum = "UNPARSED:" + proc.stdout.strip()[-120:] + " | " + proc.stderr.strip()[-120:]
            fh.write(f"{i:02d}\t{proc.returncode}\t{receipt}\t{failsum}\n")
            fh.flush()
            print(f"{i:03d} exit={proc.returncode} {flag or 'normal'}", file=sys.stderr)


if __name__ == "__main__":
    main()
