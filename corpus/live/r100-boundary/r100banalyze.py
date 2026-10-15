#!/usr/bin/env python3
"""r100b analyzer — replay cells vs the r100 scout's own receipts.

Reads the scout's `runs/sofa_*.json` and this seat's `receipts/*.json`, compares
each cell in BOTH analysis recipes (the scout's 0.4 s-of-fc-rate window and the
0.4 s-of-file-rate window) and prints a comparison table + JSON summary.

Usage: r100banalyze.py [out.json]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCOUT = os.path.join(os.path.dirname(HERE), "r100-scout", "runs")
REC = os.path.join(HERE, "receipts")

CELLS = ["noconfig_48k", "sofa_48k", "sofa_44k_az0", "sofa_44k_az90", "sofa_44k_az270",
         "sofa_44k_az180", "sofa_48k_az90"]


def load_scout():
    rows = []
    for f in ("sofa_gate.json", "sofa_azimuth.json", "sofa_extra.json"):
        p = os.path.join(SCOUT, f)
        if os.path.exists(p):
            for r in json.load(open(p)):
                r["_src"] = f
                rows.append(r)
    return rows


def load_mine(arm):
    rows = []
    for stage in ("gate", "azimuth", "extra", "fgprobe"):
        p = os.path.join(REC, "%s-%s.json" % (arm, stage))
        if os.path.exists(p):
            for r in json.load(open(p)):
                r["_src"] = "%s-%s" % (arm, stage)
                rows.append(r)
    return rows


def _tone(c):
    return c.get("tone440", c.get("tone"))


def recipe(row, which):
    a = row.get("analysis") or {}
    if which == "scout":
        s = a.get("scout")
        if s:
            ch = s.get("channels") or []
            return {"rms": [c["rms"] for c in ch], "tone": [_tone(c) for c in ch],
                    "ild": s.get("ild_db"), "win_offset": [c["win_offset"] for c in ch],
                    "win": s.get("win")}
        # the scout's own receipts: `channels` IS the scout recipe
        ch = a.get("channels") or []
        return {"rms": [c["rms"] for c in ch], "tone": [_tone(c) for c in ch],
                "ild": a.get("ild_db"), "win_offset": [c["win_offset"] for c in ch],
                "win": None}
    ch = a.get("channels") or []
    return {"rms": [c["rms"] for c in ch], "tone": [_tone(c) for c in ch],
            "ild": a.get("ild_db"), "win_offset": [c["win_offset"] for c in ch],
            "win": None}


def rel(a, b):
    if a is None or b is None:
        return None
    d = abs(a - b)
    m = max(abs(a), abs(b), 1e-12)
    return d / m


def nsamples(row):
    for l in row.get("fc_log", []):
        m = re.search(r"using n_samples:(\d+)", l)
        if m:
            return int(m.group(1))
    return None


def summarize(rows, label):
    out = {}
    for r in rows:
        key = (r["leg"], r.get("rep", 0))
        out[key] = {"label": label, "src": r.get("_src"), "wall": r.get("wall_s"),
                    "load1": (r.get("loadavg_end") or {}).get("l1"),
                    "clean": (r.get("post_sweep") or {}).get("clean"),
                    "play_origin": r.get("play_link_origin"),
                    "play_hang": r.get("play_hang"),
                    "file_rate": (r.get("analysis") or {}).get("file_rate"),
                    "frames": (r.get("analysis") or {}).get("frames"),
                    "n_samples": nsamples(r),
                    "err_no_config": any("no config was given" in l for l in r.get("fc_log", [])),
                    "err_rate_string": any("Only the same sampling rate supported" in l
                                           for l in r.get("fc_log", [])),
                    "scout": recipe(r, "scout"), "r100b": recipe(r, "r100b")}
    return out


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "scratch", "compare.json")
    scout = summarize(load_scout(), "scout")
    quiet = summarize(load_mine("quiet"), "quiet")
    load = summarize(load_mine("load"), "load")
    res = {"cells": {}, "scout": {}, "quiet": {}, "load": {}}

    print("== replay cells: scout (r100s) vs this seat (r100b), scout recipe ==")
    hdr = "%-16s %-4s | %-28s | %-28s | %-28s" % ("cell", "rep", "scout rms L/R (ild)",
                                                   "quiet rms L/R (ild)", "load rms L/R (ild)")
    print(hdr)
    for leg in CELLS:
        reps = sorted({k[1] for k in list(scout) + list(quiet) + list(load) if k[0] == leg})
        for rep in reps:
            s = scout.get((leg, rep))
            q = quiet.get((leg, rep))
            l = load.get((leg, rep))
            def fmt(x):
                if not x:
                    return "-"
                sc = x["scout"]
                return "%s/%s (%s)" % (sc["rms"][0] if sc["rms"] else "-",
                                       sc["rms"][1] if len(sc["rms"]) > 1 else "-", sc["ild"])
            print("%-16s %-4s | %-28s | %-28s | %-28s" % (leg, rep, fmt(s), fmt(q), fmt(l)))
            res["cells"]["%s_r%d" % (leg, rep)] = {"scout": s, "quiet": q, "load": l}

    print()
    print("== scout-recipe relative deltas (quiet vs scout, load vs scout) ==")
    deltas = {}
    for leg in CELLS:
        for rep in sorted({k[1] for k in quiet if k[0] == leg}):
            s = scout.get((leg, rep))
            q = quiet.get((leg, rep))
            l = load.get((leg, rep))
            row = {}
            for ch in (0, 1):
                if s and q and len(s["scout"]["rms"]) > ch and len(q["scout"]["rms"]) > ch:
                    row["quiet_ch%d" % ch] = rel(s["scout"]["rms"][ch], q["scout"]["rms"][ch])
                if s and l and len(s["scout"]["rms"]) > ch and len(l["scout"]["rms"]) > ch:
                    row["load_ch%d" % ch] = rel(s["scout"]["rms"][ch], l["scout"]["rms"][ch])
            deltas["%s_r%d" % (leg, rep)] = row
            print("%-18s quiet=%s load=%s" % ("%s_r%d" % (leg, rep),
                                              {k: ("%.2e" % v) for k, v in row.items() if k.startswith("quiet")},
                                              {k: ("%.2e" % v) for k, v in row.items() if k.startswith("load")}))
    res["deltas"] = deltas

    print()
    print("== structural pins ==")
    for label, data in (("scout", scout), ("quiet", quiet), ("load", load)):
        for key in sorted(data):
            d = data[key]
            if d["n_samples"] is None and not d["err_no_config"] and key[0] != "noconfig_48k":
                continue
            print("%-6s %-18s n_samples=%s no_config_err=%s rate_string=%s file_rate=%s frames=%s clean=%s play=%s hang=%s"
                  % (label, "%s_r%d" % key, d["n_samples"], d["err_no_config"],
                     d["err_rate_string"], d["file_rate"], d["frames"], d["clean"],
                     d["play_origin"], d["play_hang"]))
    res["summary"] = {"scout": {str(k): v for k, v in scout.items()},
                      "quiet": {str(k): v for k, v in quiet.items()},
                      "load": {str(k): v for k, v in load.items()}}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(res, f, indent=1, default=str)
    print("\nwrote", out_path)


if __name__ == "__main__":
    main()
