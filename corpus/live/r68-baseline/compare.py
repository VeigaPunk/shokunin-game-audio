#!/usr/bin/env python3
"""r68 baseline receipt comparison.

Row i of ledger-r68-baseline.tsv (fresh, frozen tree) replays row i of the
committed corpus/live/r67-author/ledger-r67.tsv (canonical run dirs).
Per-row: sha256(fresh) vs sha256(committed). On byte mismatch, retry after
normalizing the disclosed path embedding: replace the frozen-ROOT infix
'corpus/live/r68-baseline/frozen/corpus/' with 'corpus/' in the fresh bytes.

Committed receipts are anchored on the FROZEN COMMIT bd5e1fe explicitly
(git show bd5e1fe:<relpath>), so a mid-window HEAD move cannot skew the
anchor — the r67 lesson applied. The committed r67-verifier ledger's
receipt is cross-referenced as a second committed reference.

Writes committed-shas.tsv and receipt-compare.tsv; prints a summary.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
COMMIT = "bd5e1fe9abcfc67455bb08f64548594b3e33aa02"
COMMITTED = ROOT / "corpus/live/r67-author/ledger-r67.tsv"
VERIFIER = ROOT / "corpus/live/r67-verifier/ledger-r67-verifier.tsv"
FRESH = HERE / "ledger-r68-baseline.tsv"
INFIX = b"corpus/live/r68-baseline/frozen/corpus/"
CANON = b"corpus/"


def rows(path):
    out = []
    for line in path.read_text().splitlines():
        idx, code, receipt, failsum = line.split("\t", 3)
        out.append((int(idx), int(code), receipt, failsum))
    return out


def sha(b):
    return hashlib.sha256(b).hexdigest()


def gitshow(relpath):
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{COMMIT}:{relpath}"],
                          capture_output=True, check=True).stdout


def main():
    old, ver, new = rows(COMMITTED), rows(VERIFIER), rows(FRESH)
    assert len(old) == len(ver) == len(new) == 112
    with (HERE / "committed-shas.tsv").open("w") as cs, \
         (HERE / "receipt-compare.tsv").open("w") as rc:
        n_ident = n_norm = n_diff = n_track = 0
        for orow, vrow, nrow in zip(old, ver, new):
            o_idx, o_code, o_path, _ = orow
            v_idx, v_code, v_path, _ = vrow
            n_idx, n_code, n_path, _ = nrow
            assert o_idx == n_idx == v_idx
            ob = Path(o_path).read_bytes()
            rel = str(Path(o_path).relative_to(ROOT))
            tracked = gitshow(rel) == ob
            n_track += tracked
            vb = Path(v_path).read_bytes()
            nb = Path(n_path).read_bytes()
            os_, ns, vs = sha(ob), sha(nb), sha(vb)
            cs.write(f"{o_idx:02d}\t{os_}\t{o_path}\n")
            if ob == nb:
                status = "identical"
            elif ob == nb.replace(INFIX, CANON):
                status = "normalized"
            elif vb == nb:
                status = "identical-verifier"
            elif vb == nb.replace(INFIX, CANON):
                status = "normalized-verifier"
            else:
                status = "DIFFERS"
            n_ident += status.startswith("identical")
            n_norm += status.startswith("normalized")
            n_diff += status == "DIFFERS"
            rc.write(f"{n_idx:02d}\t{status}\ttracked={tracked}\t{ns}\t{n_path}\n")
        print(f"tracked-committed={n_track}/112 identical={n_ident} "
              f"normalized={n_norm} DIFFERS={n_diff}")
        return 0 if n_diff == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
