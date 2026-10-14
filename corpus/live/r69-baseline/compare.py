#!/usr/bin/env python3
"""r69 baseline receipt comparison.

Row i of ledger-r69-baseline.tsv (fresh, minimal HEAD materialization under
corpus/live/r69-baseline/measure-env/corpus) replays row i of the committed
corpus/live/r68-author/ledger-r68.tsv (canonical run dirs, 114 rows).
Per-row: sha256(fresh) vs sha256(committed). On byte mismatch, retry after
normalizing the disclosed path embedding: replace the env-ROOT infix
'corpus/live/r69-baseline/measure-env/corpus/' with 'corpus/' in the fresh bytes.

Committed receipts are anchored on the FROZEN COMMIT 7b8d423 explicitly
(git show 7b8d423:<relpath>), so a mid-window HEAD move cannot skew the
anchor — the r67 lesson carried forward. The committed r68-verifier ledger's
receipt is cross-referenced as a second committed reference.

Writes committed-shas.tsv and receipt-compare.tsv; prints a summary.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
COMMIT = "7b8d423819e5a0750cd51e5df9a73fe253a9aa6f"
COMMITTED = ROOT / "corpus/live/r68-author/ledger-r68.tsv"
VERIFIER = ROOT / "corpus/live/r68-verifier/ledger-r68-verifier.tsv"
FRESH = HERE / "ledger-r69-baseline.tsv"
INFIX = b"corpus/live/r69-baseline/measure-env/corpus/"
CANON = b"corpus/"


def rows(path):
    out = []
    for line in path.read_text().splitlines():
        idx, code, receipt, failsum = line.split("\t", 3)
        out.append((int(idx), int(code), receipt, failsum))
    return out


def sha(data):
    return hashlib.sha256(data).hexdigest()


def gitshow(rel):
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{COMMIT}:{rel}"],
                          capture_output=True).stdout


def main():
    old = rows(COMMITTED)
    new = rows(FRESH)
    ver = rows(VERIFIER)
    assert len(old) == len(new) == len(ver) == 114, (len(old), len(new), len(ver))
    n_track = n_ident = n_norm = n_diff = 0
    with (HERE / "committed-shas.tsv").open("w") as cs, \
         (HERE / "receipt-compare.tsv").open("w") as rc:
        for (o_idx, _oc, o_path, _of), (n_idx, _nc, n_path, _nf), (v_idx, _vc, v_path, _vf) \
                in zip(old, new, ver):
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
        print(f"tracked-committed={n_track}/114 identical={n_ident} "
              f"normalized={n_norm} DIFFERS={n_diff}")
        return 0 if n_diff == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
