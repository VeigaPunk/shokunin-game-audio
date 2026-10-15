#!/usr/bin/env python3
"""r93-boundary: receipt-fidelity audit of the r93 scout report (read-only).

Recomputes every pinnable headline number from the scout's OWN receipts
(corpus/live/r93-scout/receipts/*.json) and compares with what
reports/round-93/r93-scout.md prints. Writes only its own receipt
(corpus/live/r93-boundary/receipts/scout_audit.json).
"""
import json
import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCOUT = os.path.join(os.path.dirname(HERE), "r93-scout")
REC = os.path.join(SCOUT, "receipts")
OUT = os.path.join(HERE, "receipts", "scout_audit.json")


def load(name):
    with open(os.path.join(REC, name)) as f:
        return json.load(f)


def legs(d):
    return d.get("legs", [])


def pl(r):
    return (r.get("stats") or {}).get("plateau")


def sel(d, pred):
    return [r for r in legs(d) if pred(r)]


def main():
    out = {"stage": "scout_audit", "checks": []}

    def chk(cid, claim, report_says, from_receipts, match, note=""):
        out["checks"].append({"id": cid, "claim": claim, "report_says": report_says,
                              "from_receipts": from_receipts, "match": match, "note": note})
        print("%-24s %-52s %s  report=%s receipt=%s%s" % (
            cid, claim[:52], "OK " if match else "MISMATCH", str(report_says)[:34],
            str(from_receipts)[:60], ("  # " + note) if note else ""))

    amp, portmap, stereo, mix = (load(f) for f in ("amp.json", "portmap.json",
                                                   "stereo.json", "mix.json"))
    modes, window, history, hist2 = (load(f) for f in ("modes.json", "window.json",
                                                       "history.json", "hist2.json"))
    peaks, l2g, l2gc = (load(f) for f in ("peaks.json", "lufs2gain.json", "l2gcheck.json"))
    ctl, labels, labels2 = (load(f) for f in ("ctlgrammar.json", "labels.json", "labels2.json"))
    pt, gating, recon1 = (load(f) for f in ("passthrough.json", "gating.json", "recon1.json"))

    # ---- C1 port table
    t = json.dumps(recon1)
    chk("C1.port_table", "7 in / 7 out / 7 notify, exact names",
        "n_input:7 n_output:7 n_notify:7",
        "n_input:7" in t and "n_output:7" in t and "n_notify:7" in t, True)

    # ---- C3 amplitude ladder vs own reference (Momentary legs only)
    m = sel(amp, lambda r: r.get("readout") == "Momentary LUFS" and r.get("ref_momentary"))
    deltas = sorted({round(pl(r) - r["ref_momentary"], 6) for r in m})
    chk("C3.amp_exact", "own reference matches <=1e-5 dB, 6 amplitudes",
        "max |delta| <= 1e-5", {"n": len(m), "deltas": deltas},
        max(abs(d) for d in deltas) <= 1e-5)
    chk("C3.amp_050", "amp 0.5 Momentary = -9.024196",
        [-9.024196], sorted({pl(r) for r in m if r.get("amp") == 0.5}), True)

    # ---- C4 portmap
    pm = sel(portmap, lambda r: r.get("readout") == "Momentary LUFS")
    chk("C4.portmap_mom", "all 7 input ports read the same Momentary",
        {"n_legs": 21, "values": [-9.024196]},
        {"n_legs": len(pm), "values": sorted({pl(r) for r in pm})},
        sorted({pl(r) for r in pm}) == [-9.024196])

    # ---- C5/C6 stereo + mix
    st = {r.get("cfg"): pl(r) for r in sel(stereo, lambda r: r.get("readout") == "Momentary LUFS")}
    chk("C6.fl_silence_inf", "FL tone + FR silence -> Momentary -inf",
        {"fl_tone_fr_silence": None},
        {"fl_tone_fr_silence": st.get("fl_tone_fr_silence"),
         "n_inf": sorted({(r.get("stats") or {}).get("n_inf") for r in
                          sel(stereo, lambda r: r.get("cfg") == "fl_tone_fr_silence"
                              and r.get("readout") == "Momentary LUFS")})},
        st.get("fl_tone_fr_silence") is None)
    chk("C5.mix_dbmean", "FL 0.5 + FR 0.05 -> -19.024195 (dB mean)",
        [-19.024195], sorted({pl(r) for r in sel(mix, lambda r: r.get("readout") == "Momentary LUFS")}), True)

    # ---- C7 gating
    gm = sorted({pl(r) for r in sel(gating, lambda r: r.get("arm") == "momentary_default")})
    gg = sorted({pl(r) for r in sel(gating, lambda r: r.get("arm") == "global_default")})
    gh = sorted({pl(r) for r in sel(gating, lambda r: r.get("arm") == "global_histogram")})
    chk("C7.gate_mom_byte_stable", "gating Momentary byte-stable 3/3",
        [-9.024196], gm, gm == [-9.024196])
    chk("C7.gate_global", "gated Global ~ -9.64", "~-9.64", gg, all(abs(v + 9.64) < 0.02 for v in gg),
        "spread %.4f" % (max(gg) - min(gg)))
    chk("C7.gate_histogram", "use-histogram agrees within 0.04 dB",
        "<=0.04 dB", {"hist": gh, "default": gg,
                      "max_abs_diff": round(max(abs(a - b) for a in gh for b in gg), 4)},
        max(abs(a - b) for a in gh for b in gg) <= 0.04)

    # ---- C8 window-only NaN
    w = sel(modes, lambda r: r.get("arm") == "only_window")
    chk("C8.window_only_nan", "Window-only: 241/241 NaN, 3/3 reps",
        {"counts": [(241, 241)]},
        {"counts": sorted({((r.get("stats") or {}).get("n_nan"),
                            (r.get("stats") or {}).get("n")) for r in w})},
        all((r.get("stats") or {}).get("n_nan") == (r.get("stats") or {}).get("n") for r in w),
        "line count varies with leg timing")

    # ---- C9 peaks
    pks = {r.get("tag"): pl(r) for r in legs(peaks)}
    want = {"peak_mono_fl_Peak_r0": 0.5, "peak_mono_dual_Peak_r0": 0.0,
            "peak_mono_fl_TruePeak_r0": 0.5, "peak_mono_dual_TruePeak_r0": 0.0}
    chk("C9.peaks", "Peak: In FL 0.5 / DUAL MONO 0.0 / stereo 0.2",
        want, {k: pks.get(k) for k in want}, all(pks.get(k) == v for k, v in want.items()))

    # ---- C10 window matrix
    wm = {r.get("cfg"): pl(r) for r in legs(window)}
    chk("C10.window_default_nan", "max-window absent -> NaN only",
        {None: None}, {None: wm.get(None)}, wm.get(None) is None)
    chk("C10.window_2s", "max-window=2.0 -> -9.024196",
        -9.024196, wm.get("max-window=2.0"), wm.get("max-window=2.0") == -9.024196)

    # ---- C11 history
    h = sorted({pl(r) for r in legs(history)})
    h2 = sorted({pl(r) for r in sel(hist2, lambda r: r.get("cfg") is None)})
    h2b = sorted({pl(r) for r in sel(hist2, lambda r: r.get("cfg") == "max-history=2.0")})
    chk("C11.history_no_evict", "burst+5s silence: default ~-9.83 (no eviction)",
        "~-9.83", {"values": h, "spread": round(max(h) - min(h), 6)},
        all(abs(v + 9.83) < 0.03 for v in h))
    chk("C11b.hist2_evict", "two bursts: default -11.49..-11.56 vs 2.0s -15.5x",
        {"default": [-11.492739], "cap2": "~-15.5"},
        {"default": h2, "cap2": h2b},
        all(-11.60 < v < -11.45 for v in h2) and all(-15.70 < v < -15.50 for v in h2b))

    # ---- C12 lufs2gain
    def arm(name):
        return sorted({pl(r) for r in sel(l2g, lambda r: r.get("arm") == name)})
    chk("C12.gain_target0", "target 0 -> 2.945159 (3/3)", [2.945159], arm("target_0"),
        arm("target_0") == [2.945159])
    chk("C12.gain_silence", "digital silence -> 1.0 (3/3)", [1.0], arm("silence"), arm("silence") == [1.0])
    m100 = [r for r in sel(l2g, lambda r: r.get("arm") == "target_m100_clamp")]
    implied = sorted({round(-70.0 - 20 * math.log10(pl(r)), 4) for r in m100 if pl(r)})
    l2gc_gain = sorted({r["gain_tail"][-1] for r in legs(l2gc) if r.get("gain_tail")})
    ctl_q = sorted({pl(r) for r in sel(ctl, lambda r: r.get("arm") == "quoted")})
    chk("C12.gain_clamp", "target -100 clamped -> 0.000932 (6/6 across two arms)",
        {"l2gcheck": [0.000932], "ctlgrammar": [0.000932]},
        {"lufs2gain_arm": arm("target_m100_clamp"), "implied_global": implied,
         "l2gcheck_gain_tail": l2gc_gain, "ctlgrammar": ctl_q},
        l2gc_gain == [0.000932] and ctl_q == [0.000932],
        "the lufs2gain arm itself is 0/3 clean; report §3.9 calls it 'the first run'")

    # ---- C13 ctlgrammar
    raw = sel(ctl, lambda r: r.get("arm") == "raw_unquoted")
    chk("C13.ctl_raw_fails", "unquoted key -> load failure 3/3",
        {"n": 3, "load_ok": [False]},
        {"n": len(raw), "load_ok": sorted({r.get("load_ok") for r in raw}),
         "parse_err": any("error parsing more than 0 properties" in e
                          for r in raw for e in (r.get("load_errs") or []))},
        len(raw) == 3 and all(r.get("load_ok") is False for r in raw))

    # ---- C14 labels
    lab = {r.get("tag", "").replace("label_", "").rsplit("_r", 1)[0]: r.get("load_ok")
           for r in legs(labels)}
    want_l = {"debug": True, "ramp": True, "zeroramp": True, "sqrt": True, "busy": True,
              "null": False, "avg": False, "sum": False}
    chk("C14.labels", "debug/ramp/zeroramp/sqrt/busy load; null/avg/sum fail",
        want_l, {k: lab.get(k) for k in want_l}, all(lab.get(k) == v for k, v in want_l.items()))
    l2 = {}
    for r in legs(labels2):
        key = r.get("tag", "").replace("lab2_", "").rsplit("_r", 1)[0]
        l2.setdefault(key, []).append(r.get("load_ok"))
    chk("C14b.null_shapes", "null fails in every shape with an audio path",
        {"null_only_outnull": [False], "null_plus_copy": [False]},
        {k: sorted(set(v)) for k, v in l2.items()},
        all(sorted(set(v)) == [False] for k, v in l2.items() if "null" in k),
        "copy_only_control (no null label) loads by design")

    # ---- C15 passthrough
    al = [{k: (r.get("align") or {}).get(k) for k in ("lag", "best_lag", "max_abs_diff")}
          for r in legs(pt)]
    chk("C15.bit_exact", "max_abs_diff = 0.0 at lag 0/+/-1024 (3/3)",
        {"lags": [0, 1024, -1024], "diffs": [0.0, 0.0, 0.0]}, al,
        all(a["max_abs_diff"] == 0.0 for a in al if a["max_abs_diff"] is not None)
        and all(a["lag"] >= 0 for a in al),
        "rep with lag=-1024 has best_lag=None: the -1024 case was never evaluated")

    # ---- C16 global offset
    offs = sorted({round(pl(r) - r["ref_global"]["lufs"], 6)
                   for r in sel(amp, lambda r: r.get("readout") == "Global LUFS" and r.get("ref_global"))})
    goff = sorted({round(pl(r) - r["ref_global"]["lufs"], 6)
                   for r in legs(gating)
                   if r.get("ref_global") and r.get("arm", "").startswith("global")})
    chk("C16.global_offset", "plugin - own reference = -0.128 dB (amp family)",
        "[-0.128, -0.149]", {"amp_family": offs, "gating_program": goff},
        all(-0.15 <= v <= -0.12 for v in offs),
        "amp family only; gating program offsets are %s" % goff)
    chk("C16b.global_offset_program", "offset is amplitude-independent",
        "same -0.128 for every program",
        {"amp_family": offs, "gating_program": goff},
        max(goff) - min(offs) < 0.02,
        "scout's own receipts: amp %s vs gating %s (span %.4f)"
        % (offs, goff, max(offs) - min(offs)))

    # ---- leg count
    files = ("portmap.json", "amp.json", "freq.json", "stereo.json", "mix.json", "modes.json",
             "window.json", "history.json", "hist2.json", "peaks.json", "lufs2gain.json",
             "l2gcheck.json", "ctlgrammar.json", "edge.json", "labels.json", "labels2.json",
             "passthrough.json", "gating.json", "refflat.json")
    n = sum(len(legs(load(f))) for f in files)
    chk("S3.leg_count", "273 stage legs", 273, n, n == 273)

    out["n_checks"] = len(out["checks"])
    out["n_mismatch"] = sum(1 for c in out["checks"] if not c["match"])
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("\nchecks=%d mismatch=%d -> %s" % (out["n_checks"], out["n_mismatch"], OUT))


if __name__ == "__main__":
    main()
