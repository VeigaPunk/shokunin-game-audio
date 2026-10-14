#!/usr/bin/env python3
"""r69 baseline replay: run the COMMITTED r68 114-mode ledger verbatim against
the minimal HEAD materialization at corpus/live/r69-baseline/measure-env/corpus
(tracked files only, verified byte-equal to `git show HEAD:` per env-proofs.txt).

MODES imported straight from the committed corpus/live/r68-author/run_ledger.py
so the command list cannot drift; only MEASURE/TSV/OUTDIR are re-pointed into
this lane's scratch. Writes ledger-r69-baseline.tsv plus out/{NN}.{stdout,stderr}.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ENV = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r69-baseline/measure-env")
MEASURE = str(ENV / "corpus" / "fixtures" / "measure_audio.py")
TSV = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r69-baseline/ledger-r69-baseline.tsv")
OUTDIR = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r69-baseline/out")
COMMITTED_RUN = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r68-author/run_ledger.py")

spec = importlib.util.spec_from_file_location("committed_r68_run_ledger", COMMITTED_RUN)
committed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(committed)
MODES = committed.MODES
assert len(MODES) == 114, len(MODES)


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    with TSV.open("w") as fh:
        for i, flag in enumerate(MODES, 1):
            cmd = ["python3", MEASURE] + ([flag] if flag else [])
            proc = subprocess.run(cmd, capture_output=True, text=True)
            (OUTDIR / f"{i:02d}.stdout").write_text(proc.stdout)
            (OUTDIR / f"{i:02d}.stderr").write_text(proc.stderr)
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
            failsum = " ".join(failsum.splitlines())           # TSV rows are physical lines
            fh.write(f"{i:02d}\t{proc.returncode}\t{receipt}\t{failsum}\n")
            fh.flush()
            print(f"{i:03d} exit={proc.returncode} {flag or 'normal'}", file=sys.stderr)


if __name__ == "__main__":
    main()
