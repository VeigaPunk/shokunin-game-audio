#!/usr/bin/env python3
"""r93-boundary analyzer: collapse own receipts into a claim-verdict table.

Read-only over corpus/live/r93-boundary/receipts/*.json; writes
receipts/analysis.json + a printable table.
"""
import json
import glob
import math
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(HERE, "receipts")
OUT = os.path.join(REC, "analysis.json")


def num(v):
    return v


def nget(d, *keys):
    """Nested dict get that survives non-dict intermediates."""
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def load_all():
    out = []
    for p in sorted(glob.glob(os.path.join(REC, "*.json"))):
        if os.path.basename(p) in ("analysis.json",):
            continue
        try:
            with open(p) as f:
                d = json.load(f)
        except Exception as e:
            print("skip", p, e)
            continue
        d["_file"] = os.path.basename(p)
        d["_cond"] = d.get("cond", "?")
        out.append(d)
    return out


def main():
    docs = load_all()
    legs = []
    for d in docs:
        cond = d.get("_cond")
        reps = d.get("reps")
        for r in d.get("legs", []):
            legs.append({"stage": d.get("stage"), "cond": cond, "reps": reps,
                         "load": d.get("load_requested", 0), "file": d["_file"], **r})

    def plateaus(pred):
        vals = []
        for r in legs:
            if not pred(r):
                continue
            st = r.get("stats") or {}
            vals.append({"tag": r["tag"], "cond": r["cond"], "reps": r["reps"],
                         "plateau": st.get("plateau"), "n": st.get("n"),
                         "n_nan": st.get("n_nan"), "n_inf": st.get("n_inf"),
                         "loadavg": (r.get("loadavg_start") or {}).get("l1"),
                         "plcad": ((r.get("cadence_plateau") or {}).get("frames_at_48k")),
                         "ref_mom": (r.get("ref") or {}).get("momentary"),
                         "ref_glob": ((r.get("ref") or {}).get("global") or {}).get("lufs"),
                         "valid": r.get("valid")})
        return vals

    res = {"n_docs": len(docs), "n_legs": len(legs),
           "files": [d["_file"] for d in docs],
           "by_tag": {}}
    for r in legs:
        res["by_tag"].setdefault(r["tag"], []).append(
            {k: r.get(k) for k in ("cond", "reps", "valid", "plateau")}
            | {"plateau": (r.get("stats") or {}).get("plateau"),
               "n_nan": (r.get("stats") or {}).get("n_nan"),
               "n_inf": (r.get("stats") or {}).get("n_inf"),
               "plcad": (r.get("cadence_plateau") or {}).get("frames_at_48k"),
               "ref_glob": nget(r, "ref", "global", "lufs"),
               "ref_mom": nget(r, "ref", "momentary"),
               "loadavg_l1": (r.get("loadavg_start") or {}).get("l1"),
               "audio_ratio": r.get("audio_ratio"),
               "align": r.get("align"),
               "decay_30db_s": r.get("decay_30db_s"),
               "seg": r.get("seg"),
               "law_resid_db": r.get("law_resid_db"),
               "gain_plateau": r.get("gain_plateau"),
               "global_plateau": r.get("global_plateau"),
               "arm_failed": r.get("arm_failed"),
               "play_rc": (r.get("play") or {}).get("rc"),
               "attempt": r.get("attempt"),
               "lib_full": nget(r, "ref", "libebur128", "full", "I"),
               "lib_trim": nget(r, "ref", "libebur128", "trim", "I"),
               "implied_global": r.get("implied_global"),
               "force_quantum": r.get("force_quantum"),
               "sink_rate_arg": r.get("sink_rate_arg"),
               "load_errs": (r.get("load_errs") or [])[:1]})

    with open(OUT, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)

    print("files=%d legs=%d -> %s\n" % (len(docs), len(legs), OUT))
    for tag in sorted(res["by_tag"]):
        rows = res["by_tag"][tag]
        parts = []
        for x in rows:
            parts.append("%s/r%s%s:pl=%s%s%s" % (
                x["cond"], x["reps"],
                ("+retry%d" % x["attempt"]) if x.get("attempt") else "",
                x["plateau"],
                ("/nan%d" % x["n_nan"]) if x.get("n_nan") else "",
                ("/inf%d" % x["n_inf"]) if x.get("n_inf") else ""))
            if x.get("arm_failed"):
                parts[-1] += " ARM_FAILED(rc=%s)" % x.get("play_rc")
        extra = ""
        if rows[0].get("plcad"):
            extra += " plcad=%s" % rows[0]["plcad"]
        if rows[0].get("ref_glob") is not None:
            extra += " refglob=%s" % rows[0]["ref_glob"]
        if rows[0].get("lib_full") is not None:
            extra += " lib128_full=%s lib128_trim=%s" % (rows[0]["lib_full"], rows[0]["lib_trim"])
        if rows[0].get("gain_plateau"):
            extra += " gain=%s glob=%s" % (rows[0]["gain_plateau"], rows[0]["global_plateau"])
        if rows[0].get("decay_30db_s") is not None:
            extra += " decay=%s" % rows[0]["decay_30db_s"]
        if rows[0].get("seg"):
            extra += " seg=%s" % rows[0]["seg"]
        if rows[0].get("audio_ratio"):
            extra += " ratio=%s" % rows[0]["audio_ratio"]
        if rows[0].get("align"):
            extra += " align=%s" % rows[0]["align"]
        if rows[0].get("implied_global"):
            extra += " impliedG=%s resid=%s" % (rows[0]["implied_global"], rows[0]["law_resid_db"])
        if rows[0].get("force_quantum"):
            extra += " fq=%s" % rows[0]["force_quantum"]
        if rows[0].get("sink_rate_arg"):
            extra += " sinkrate=%s" % rows[0]["sink_rate_arg"]
        if rows[0].get("load_errs"):
            extra += " err=%s" % str(rows[0]["load_errs"])[:60]
        print("%-30s %s%s" % (tag, " | ".join(parts), extra))


if __name__ == "__main__":
    main()
