#!/usr/bin/env python3
"""r93 scout — cross-stage summary over the receipts (read-only analysis)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(HERE, "receipts")


def load(name):
    p = os.path.join(REC, name + ".json")
    if not os.path.exists(p):
        return None
    return json.load(open(p))


def main():
    pm = load("portmap")
    print("== portmap: Momentary / Global plateau per input port ==")
    rows = {}
    for leg in pm["legs"]:
        st = leg["stats"]
        rows.setdefault((leg["port"], leg["readout"]), []).append(st["plateau"])
    for k in sorted(rows):
        print("  %-11s %-14s %s" % (k[0], k[1], rows[k]))

    amp = load("amp")
    print("== amp ladder (Momentary) vs own reference ==")
    for leg in amp["legs"]:
        if leg["readout"] == "Momentary LUFS":
            st = leg["stats"]
            print("  amp=%-8s plateau=%-11s ref=%-11s d=%.6f" % (
                leg["amp"], st["plateau"], leg["ref_momentary"],
                st["plateau"] - leg["ref_momentary"]))

    fq = load("freq")
    print("== freq ladder (Momentary) ==")
    for leg in fq["legs"]:
        st = leg["stats"]
        print("  %6d Hz plateau=%-11s ref=%-11s" % (leg["freq"], st["plateau"],
                                                    leg["ref_momentary"]))

    st = load("stereo")
    print("== stereo ==")
    rows = {}
    for leg in st["legs"]:
        rows.setdefault((leg["cfg"], leg["readout"]), []).append(
            leg["stats"]["plateau"] if leg["stats"].get("plateau") is not None
            else ("-inf" if leg["stats"]["n_inf"] else "nan"))
    for k in sorted(rows):
        print("  %-20s %-14s %s" % (k[0], k[1], rows[k]))

    md = load("modes")
    print("== modes (notify-only coupling) ==")
    for leg in md["legs"]:
        st = leg["stats"]
        post = leg.get("post") or {}
        print("  %-22s plateau=%-11s nan=%d inf=%d post_nz=%s" % (
            leg["arm"], st.get("plateau"), st["n_nan"], st["n_inf"], post.get("nz")))

    wn = load("window")
    print("== window (Window LUFS) ==")
    for leg in wn["legs"]:
        st = leg["stats"]
        print("  %-24s plateau=%-11s nan=%d inf=%d tail=%s" % (
            leg["tag"], st.get("plateau"), st["n_nan"], st["n_inf"], st["tail"][-1]))

    hs = load("history")
    print("== history (Global through silence) ==")
    for leg in hs["legs"]:
        st = leg["stats"]
        print("  %-24s tail=%s" % (leg["tag"], st["tail"][-2:]))

    h2 = load("hist2")
    print("== hist2 (two bursts) ==")
    for leg in h2["legs"]:
        st = leg["stats"]
        print("  %-24s plateau=%-11s ref=%s" % (
            leg["tag"], st["plateau"], (leg.get("ref_global") or {}).get("lufs")))

    pk = load("peaks")
    print("== peaks ==")
    for leg in pk["legs"]:
        st = leg["stats"]
        print("  %-16s %-10s plateau=%-8s tail=%s" % (
            leg["cfg"], leg["readout"], st.get("plateau"), st["tail"][-1]))

    lg = load("lufs2gain")
    print("== lufs2gain ==")
    for leg in lg["legs"]:
        st = leg.get("stats") or {}
        print("  %-26s valid=%-5s plateau=%-10s ratio=%s" % (
            leg["tag"], leg.get("valid"), st.get("plateau"), leg.get("audio_ratio")))

    ck = load("l2gcheck")
    if ck:
        print("== l2gcheck (Global + Gain in one leg) ==")
        for leg in ck["legs"]:
            print("  %-22s global_tail=%s gain_tail=%s ref_global=%s" % (
                leg["tag"], leg.get("global_tail"), leg.get("gain_tail"),
                (leg.get("ref_global") or {}).get("lufs")))

    cg = load("ctlgrammar")
    if cg:
        print("== ctlgrammar ==")
        for leg in cg["legs"]:
            print("  %-22s load_ok=%-5s errs=%s" % (
                leg["tag"], leg.get("load_ok"), (leg.get("errs") or [])[:1]))

    ed = load("edge")
    print("== edge ==")
    for leg in ed["legs"]:
        st = leg.get("stats") or {}
        print("  %-24s load_ok=%-5s plateau=%-11s warnerr=%s" % (
            leg["tag"], leg.get("load_ok"), st.get("plateau"),
            (leg.get("log_warnerr") or [])[:1]))

    lb = load("labels")
    print("== labels (load matrix) ==")
    rows = {}
    for leg in lb["legs"]:
        rows.setdefault(leg["label"], []).append(leg["load_ok"])
    for k, v in rows.items():
        print("  %-12s %s" % (k, v))

    lb2 = load("labels2")
    if lb2:
        print("== labels2 (null shapes) ==")
        for leg in lb2["legs"]:
            print("  %-24s load_ok=%-5s errs=%s" % (
                leg["tag"], leg.get("load_ok"), (leg.get("errs") or [])[:1]))

    pt = load("passthrough")
    if pt:
        print("== passthrough ==")
        for leg in pt.get("legs", []):
            print("  %-16s align=%s ref=%s post=%s" % (
                leg["tag"], leg.get("align"), None, None))

    gt = load("gating")
    print("== gating ==")
    for leg in gt["legs"]:
        print("  %-24s plateau=%-11s seg=%s ref=%s" % (
            leg["tag"], leg["stats"].get("plateau"), leg.get("seg"),
            (leg.get("ref_global") or {}).get("lufs")))

    mx = load("mix")
    print("== mix ==")
    for leg in mx["legs"]:
        print("  %-22s plateau=%s" % (leg["tag"], leg["stats"].get("plateau")))

    rf = load("refflat")
    print("== refflat ==")
    print("  ffmpeg:", rf["legs"][0]["summary"])
    print("  own ref on stimulus:", rf["ref_stimulus"])


if __name__ == "__main__":
    main()
