#!/usr/bin/env python3
"""r70 baseline: JSON-level receipt equality modulo disclosed path embeddings.

For rows whose raw bytes differ, prove equality at field level:
  - identical JSON structure (same key paths, same leaf types/counts);
  - every differing string leaf contains a 'corpus/' anchor in BOTH receipts
    and the two leaves share the identical suffix after the LAST 'corpus/'
    occurrence (the fresh leaf may additionally carry the
    'live/r70-baseline/measure-env/' infix, possibly truncated mid-token at the
    head by measure_audio.py's tail[-1][-160:] stderr window);
  - non-string leaves must be exactly equal.

Writes semantic-compare.tsv (row \t verdict \t differing-leaf-paths).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
COMMITTED = ROOT / "corpus/live/r69-author/ledger-r69.tsv"
FRESH = HERE / "ledger-r70-baseline.tsv"
INFIX = "live/r70-baseline/measure-env/corpus/"
ANCHOR = "corpus/"


def rows(path):
    out = {}
    for line in path.read_text().splitlines():
        idx, code, receipt, failsum = line.split("\t", 3)
        out[int(idx)] = receipt
    return out


def leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, f"{prefix}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def anchored(s):
    i = s.rfind(ANCHOR)
    return None if i < 0 else s[i:]


def main():
    old, new = rows(COMMITTED), rows(FRESH)
    bad = []
    with (HERE / "semantic-compare.tsv").open("w") as fh:
        for idx in sorted(old):
            o = json.loads(Path(old[idx]).read_text())
            n = json.loads(Path(new[idx]).read_text())
            ol, nl = dict(leaves(o)), dict(leaves(n))
            if ol.keys() != nl.keys():
                fh.write(f"{idx:02d}\tSTRUCTURE-DIFF\n")
                bad.append(idx)
                continue
            diffed = []
            ok = True
            for k in sorted(ol):
                a, b = ol[k], nl[k]
                if a == b:
                    continue
                if isinstance(a, str) and isinstance(b, str):
                    sa, sb = anchored(a), anchored(b)
                    if sa is not None and sa == sb and INFIX in b:
                        diffed.append(k)
                        continue
                ok = False
                diffed.append(k + "!!")
            verdict = "EQUAL" if not diffed else ("EQUAL-MOD-PATHS" if ok else "CONTENT-DIFF")
            if not ok:
                bad.append(idx)
            fh.write(f"{idx:02d}\t{verdict}\t{','.join(diffed) if diffed else '-'}\n")
    print("CONTENT-DIFF rows:", bad if bad else "none")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
