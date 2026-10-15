#!/usr/bin/env python3
"""r78-baseline PHASE 2 replay: the SAME 127-command battery (MODES imported
from rerun.py, so row N is the same flag as row N of the Phase-1 ledger),
against measure-env-post (materialized at the landed r78 arm commit).

Writes ledger-r78-baseline-post.tsv + out-post/{01..127}.{stdout,stderr}.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEASURE = str(HERE / "measure-env-post" / "corpus" / "fixtures" / "measure_audio.py")
TSV = HERE / "ledger-r78-baseline-post.tsv"
OUT = HERE / "out-post"

_spec = importlib.util.spec_from_file_location("r78_rerun", HERE / "rerun.py")
_r = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_r)
MODES = _r.MODES
assert len(MODES) == 127, len(MODES)


def main():
    OUT.mkdir(exist_ok=True)
    with TSV.open("w") as fh:
        for i, flag in enumerate(MODES, 1):
            cmd = ["python3", MEASURE] + ([flag] if flag else [])
            proc = subprocess.run(cmd, capture_output=True, text=True)
            (OUT / f"{i:02d}.stdout").write_text(proc.stdout)
            (OUT / f"{i:02d}.stderr").write_text(proc.stderr)
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
                failsum = ("UNPARSED:" + proc.stdout.strip()[-120:] + " | "
                           + proc.stderr.strip()[-120:])
            failsum = " ".join(failsum.splitlines())
            fh.write(f"{i:02d}\t{proc.returncode}\t{receipt}\t{failsum}\n")
            fh.flush()
            print(f"{i:03d} exit={proc.returncode} {flag or 'normal'}",
                  file=sys.stderr)


if __name__ == "__main__":
    main()
