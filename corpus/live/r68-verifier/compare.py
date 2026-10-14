#!/usr/bin/env python3
"""Verifier's independent compare:
(a) my 114 exits vs author's ledger-r68.tsv exits (positional);
(b) my 114 receipt bytes vs the author's committed r68-ledger receipts;
(c) my prior-112 receipt bytes vs committed r67-ledger receipts
    (r68 rows {1} u {4..114} <-> r67 rows {1..112});
(d) my failure-summary strings vs author's (normalized whitespace).
"""
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
MINE = REPO / "corpus/live/r68-verifier/ledger-r68-verifier.tsv"
AUTHOR = REPO / "corpus/live/r68-author/ledger-r68.tsv"
R67 = REPO / "corpus/live/r67-author/ledger-r67.tsv"


def rows(tsv):
    out = []
    for line in tsv.read_text().splitlines():
        idx, code, receipt, failsum = line.split("\t", 3)
        out.append({"idx": int(idx), "code": int(code), "receipt": receipt,
                    "failsum": " ".join(failsum.split())})
    return out


def main():
    me, au, r67 = rows(MINE), rows(AUTHOR), rows(R67)
    assert len(me) == 114 and len(au) == 114 and len(r67) == 112
    problems = []

    # (a)+(d) exits and failure summaries, positional
    exit_mism = [r["idx"] for r, a in zip(me, au) if r["code"] != a["code"]]
    fail_mism = [r["idx"] for r, a in zip(me, au) if r["failsum"] != a["failsum"]]
    z = sum(1 for r in me if r["code"] == 0); o = sum(1 for r in me if r["code"] == 1)
    print(f"[a] my exits: {z} exit-0 / {o} exit-1 / {114-z-o} other "
          f"(author claims 49/65); exit mismatches vs author: {exit_mism or 'NONE'}")
    print(f"[d] failure-summary mismatches vs author: {fail_mism or 'NONE'}")

    # (b) my receipts vs author's committed r68 receipts, positional
    b_mism = []
    for r, a in zip(me, au):
        if r["receipt"] == "-" or a["receipt"] == "-":
            b_mism.append(f"{r['idx']}: missing receipt"); continue
        if Path(r["receipt"]).read_bytes() != Path(a["receipt"]).read_bytes():
            b_mism.append(f"{r['idx']}: bytes differ vs author receipt")
    print(f"[b] my receipts vs author's committed r68 receipts: {len(b_mism)} mismatches")
    for m in b_mism[:8]: print("    ", m)

    # (c) my prior-112 receipts vs committed r67 receipts
    pairs = [(me[0], r67[0])] + [(me[2 + k], r67[k]) for k in range(1, 112)]
    c_mism = []
    for m_r, p_r in pairs:
        if m_r["code"] != p_r["code"]:
            c_mism.append(f"exit r68v[{m_r['idx']}]={m_r['code']} vs r67[{p_r['idx']}]={p_r['code']}")
            continue
        if m_r["receipt"] == "-" or p_r["receipt"] == "-":
            c_mism.append(f"missing receipt {m_r['idx']}/{p_r['idx']}"); continue
        if Path(m_r["receipt"]).read_bytes() != Path(p_r["receipt"]).read_bytes():
            c_mism.append(f"bytes differ my row {m_r['idx']} vs r67 row {p_r['idx']}")
    print(f"[c] my prior-112 receipts vs committed r67 receipts: {len(c_mism)} mismatches")
    for m in c_mism[:8]: print("    ", m)

    return bool(exit_mism or fail_mism or b_mism or c_mism)


if __name__ == "__main__":
    sys.exit(main())
