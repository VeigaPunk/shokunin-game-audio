#!/usr/bin/env python3
"""Dump the r81-boundary receipts into a compact, quotable text digest."""
import collections
import json
import sys
from pathlib import Path

REC = Path(__file__).resolve().parent / "receipts"


def steps(leg):
    vals = [(t, s) for t, s in leg["sizes"] if s is not None]
    seq = []
    for t, s in vals:
        if not seq or seq[-1][1] != s:
            seq.append((t, s))
    dl = collections.Counter(seq[i + 1][1] - seq[i][1] for i in range(len(seq) - 1))
    return seq, dict(dl)


def linksets(leg, pat="gst_r81_bnd"):
    out, prev = [], None
    for s in leg["samples"]:
        ls = tuple(l for l in (s["g"].get("links") or []) if pat in l)
        if ls != prev:
            out.append((s["t"], list(ls)))
            prev = ls
    return out


def main():
    stage = sys.argv[1]
    for p in sorted(REC.glob("s%s-*.json" % stage)):
        doc = json.loads(p.read_text())
        print("#" * 70)
        print("RECEIPT %s when=%s" % (p.name, doc.get("when")))
        body = doc.get("body") or {}
        if "loads" in body:
            print("loads: %s" % json.dumps([{k: v.get(k) for k in
                                             ("pre_nodes", "nodes_after_unload",
                                              "nodes_after_load")}
                                            for v in body["loads"]]))
        if "rounds" in body:
            for r in body["rounds"]:
                print("ROUND r%s first_idx=%s second_idx=%s nodes_dup=%s nodes_end=%s" % (
                    r["rep"], r.get("first_idx"), r.get("second_idx"),
                    r.get("nodes_after_dup"), r.get("nodes_end")))
                print("   modules_after_dup: %s" % r.get("modules_after_dup"))
                for key in ("detail_before", "detail_end"):
                    d = r.get(key) or {}
                    print("   %s seat_nodes=%s" % (key, json.dumps(d.get("seat_nodes"))))
                    for l in d.get("links") or []:
                        print("      %s" % l)
        for leg in body.get("legs", []):
            o = leg.get("out") or {}
            seq, dl = steps(leg)
            print("== %s r%s rc=%s killed=%s el=%ss" % (
                leg["name"], leg.get("rep"), leg["rc"], leg.get("killed"),
                leg["elapsed_s"]))
            print("   out bytes=%s frames=%s riff=%s peak=%s exists=%s" % (
                o.get("bytes"), o.get("frames"), o.get("riff"),
                leg.get("out_peak"), o.get("exists")))
            if leg.get("kept"):
                print("   kept %s sha=%s head48=%s riff_size=%s data_size=%s" % (
                    leg["kept"]["path"], leg["kept"]["sha256"][:16],
                    leg["kept"]["head48"]["hex"], leg["kept"]["head48"]["riff_size"],
                    leg["kept"]["head48"]["data_size"]))
            if leg.get("env_extra"):
                print("   env %s" % json.dumps(leg["env_extra"]))
            for a in leg.get("actions", []):
                r = a["result"]
                keys = ("rc", "index", "dup_modules", "nodes_before", "nodes_after",
                        "reason", "nodes", "load", "nodes_after_load")
                keep = {k: r[k] for k in keys if k in r}
                if "detail" in r:
                    keep["detail_links"] = (r["detail"] or {}).get("links")
                    keep["detail_nodes"] = (r["detail"] or {}).get("seat_nodes")
                print("   act@%s %s" % (a["t"], json.dumps(keep)[:400]))
            for pr in leg.get("producers") or []:
                print("   prod %s started=%s ended=%s killed=%s rc=%s" % (
                    pr["name"], pr.get("started"), pr.get("ended"),
                    pr.get("killed"), pr.get("rc")))
            if seq:
                print("   sizes first/last=%s ... %s steps=%s" % (seq[0], seq[-1], dl))
            for t, ls in linksets(leg):
                print("   g@%s %s" % (t, ls if ls else "NO-SEAT-LINKS"))
            if leg.get("stderr_head"):
                print("   stderr %s" % leg["stderr_head"][:2])
        if "final_nodes" in body:
            print("final_nodes=%s final_modules=%s" % (body.get("final_nodes"),
                                                       body.get("final_modules")))


if __name__ == "__main__":
    main()
