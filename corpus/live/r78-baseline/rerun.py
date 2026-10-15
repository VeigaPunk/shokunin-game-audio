#!/usr/bin/env python3
"""r78-baseline replay: the 127-command battery, serially, against the env
materialization (measure-env/corpus — tracked-only files proven byte-equal to
frozen HEAD 731937c via env-proofs.txt + env-comm.txt direction checks).

MODE order = newest-first, folding the r77 family into the battery (the r77
baseline's declared next-round decision): the r77-baseline 126-command ordering
verbatim (r76-baseline ordering + --probe-capture-r76 at 02) with
--probe-capture-r77 inserted at position 02, so the two capture families are
rows 02 (r77) and 03 (r76). MODES is imported from the r77-baseline rerun.py so
row N of this ledger is the same flag as row N of the r77 Phase-1 ledger for
N >= 03.

Writes ledger-r78-baseline.tsv: idx \t exit \t receipt_path \t failure_summary;
per-command captures to out/{01..127}.{stdout,stderr}.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEASURE = str(HERE / "measure-env" / "corpus" / "fixtures" / "measure_audio.py")
TSV = HERE / "ledger-r78-baseline.tsv"
OUT = HERE / "out"

_R77 = HERE.parent / "r77-baseline" / "rerun.py"
_spec = importlib.util.spec_from_file_location("r77_rerun", _R77)
_r77 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_r77)
_PRIOR = list(_r77.MODES)
assert len(_PRIOR) == 126, len(_PRIOR)

# newest-first: r77 capture family at 02, r76 capture family (prior row 02) at 03.
MODES = [_PRIOR[0], "--probe-capture-r77"] + _PRIOR[1:]
assert len(MODES) == 127, len(MODES)
assert MODES[2] == "--probe-capture-r76"
assert MODES[3] == "--probe-consumers2-r75"


def main():
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
