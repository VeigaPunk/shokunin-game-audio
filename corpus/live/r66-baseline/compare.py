#!/usr/bin/env python3
"""r66 baseline receipt comparison.

Row i of ledger-r66-baseline.tsv (fresh, frozen tree) replays row i of the
committed corpus/live/r65-author/ledger-r65.tsv (canonical run dirs).
Per-row: sha256(fresh) vs sha256(committed). On byte mismatch, retry after
normalizing the disclosed path embedding: replace the frozen-ROOT infix
'corpus/live/r66-baseline/frozen/corpus/' with 'corpus/' in the fresh bytes.
Writes committed-shas.tsv and receipt-compare.tsv; prints a summary.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
COMMITTED = ROOT / "corpus/live/r65-author/ledger-r65.tsv"
FRESH = HERE / "ledger-r66-baseline.tsv"
INFIX = b"corpus/live/r66-baseline/frozen/corpus/"
CANON = b"corpus/"


def rows(path):
    out = []
    for line in path.read_text().splitlines():
        idx, code, receipt, failsum = line.split("\t", 3)
        out.append((int(idx), int(code), receipt, failsum))
    return out


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    old, new = rows(COMMITTED), rows(FRESH)
    assert len(old) == len(new) == 96
    with (HERE / "committed-shas.tsv").open("w") as cs, \
         (HERE / "receipt-compare.tsv").open("w") as rc:
        n_ident = n_norm = n_diff = 0
        for orow, nrow in zip(old, new):
            o_idx, o_code, o_path, _ = orow
            n_idx, n_code, n_path, _ = nrow
            assert o_idx == n_idx
            ob = Path(o_path).read_bytes()
            nb = Path(n_path).read_bytes()
            os, ns = sha(ob), sha(nb)
            cs.write(f"{o_idx:02d}\t{os}\t{o_path}\n")
            status = "identical" if ob == nb else "normalized" if ob == nb.replace(INFIX, CANON) else "DIFFERS"
            if status == "identical":
                n_ident += 1
            elif status == "normalized":
                n_norm += 1
            else:
                n_diff += 1
            rc.write(f"{n_idx:02d}\t{status}\t{ns}\t{n_path}\n")
        print(f"identical={n_ident} normalized={n_norm} DIFFERS={n_diff}")
        return 0 if n_diff == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
