#!/usr/bin/env python3
"""r77-baseline POST-COMMIT replay: the SAME 126-command battery (MODES
imported verbatim from rerun.py, so the ordering is identical and row N of the
post ledger is directly comparable with row N of the Phase-1 ledger) run
against the post-commit env (measure-env-post, pinned to the author work
commit 65790f13).

The r77 mode itself (--probe-capture-r77) is deliberately NOT in the battery:
this replay isolates "did the author commit change any prior row's behaviour",
which is the baseline's post-commit obligation. Adding the new family is the
next round's battery decision.

Writes ledger-r77-baseline-post.tsv + out-post/{01..126}.{stdout,stderr}.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rerun import MODES  # noqa: E402  (same ordering, single source of truth)

MEASURE = str(HERE / "measure-env-post" / "corpus" / "fixtures" / "measure_audio.py")
TSV = HERE / "ledger-r77-baseline-post.tsv"
OUT = HERE / "out-post"

assert len(MODES) == 126, len(MODES)


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
                failsum = "UNPARSED:" + proc.stdout.strip()[-120:] + " | " + proc.stderr.strip()[-120:]
            failsum = " ".join(failsum.splitlines())
            fh.write(f"{i:02d}\t{proc.returncode}\t{receipt}\t{failsum}\n")
            fh.flush()
            print(f"{i:03d} exit={proc.returncode} {flag or 'normal'}", file=sys.stderr)


if __name__ == "__main__":
    main()
