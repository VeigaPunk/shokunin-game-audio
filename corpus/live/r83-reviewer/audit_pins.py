#!/usr/bin/env python3
"""r83 REVIEWER — independent re-derivation of every r83 pin from the
COMMITTED receipts (a151a226: corpus/live/r83-author/measurements-{run1,run2}.json).

No fixture import, no live host contact: this script re-implements the
fixture's verdict logic from the recorded data and reports any pin the
fixture would NOT have caught, or any recorded value that contradicts a
report claim. Writes only corpus/live/r83-reviewer/audit_pins.json.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "audit_pins.json"

CHECKS = []
# The r78 tag pair is pid-keyed (L = 997 + (pid % 4) * 211, R = L + 503);
# derive it per receipt instead of assuming pid % 4 == 0.
FL, FR = 997.0, 1500.0


def tone_pair(entry):
    pid = (entry.get("contention") or {}).get("own_pid")
    if isinstance(pid, int):
        return 997.0 + (pid % 4) * 211.0, 997.0 + (pid % 4) * 211.0 + 503.0
    return 997.0, 1500.0


def chk(cid, ok, detail=""):
    CHECKS.append({"check": cid, "ok": bool(ok), "detail": str(detail)[:400]})
    return bool(ok)


def props_of(leg, wname):
    for s in reversed(leg.get("samples") or []):
        nd = (s.get("nodes") or {}).get(wname)
        if nd:
            return nd.get("props") or {}
    return None


def last_sample(leg):
    return (leg.get("samples") or [{}])[-1]


def ch_amp(leg, ch, f):
    chans = (leg.get("tap_stats") or {}).get("channels") or []
    if len(chans) <= ch:
        return None
    return chans[ch].get(f"amp_at_{int(f)}")


def entry_teardown(name, e):
    sg = e.get("sinks_gone") or {}
    chk(f"{name}: sinks_gone all true", sg and all(sg.values()), sg)
    chk(f"{name}: own_nodes_after empty", e.get("own_nodes_after") == [],
        e.get("own_nodes_after"))
    for tag, leaf in (e.get("unloads") or {}).items():
        chk(f"{name}: unload {tag} rc=0 recycled=false",
            leaf.get("exit_code") == 0 and leaf.get("recycled") is False,
            json.dumps(leaf)[:200])
    chk(f"{name}: failures empty", e.get("failures") == [], e.get("failures"))
    chk(f"{name}: no coverage_blocked",
        not e.get("coverage_blocked"), e.get("coverage_blocked"))


# ---------------------------------------------------------------- entry 1
def audit_props(name, e):
    legs = e["legs"]
    chk(f"{name}: 29 legs", len(legs) == 29, len(legs))
    want = {
        "land_space": {"media.name": "R83SPV", "bogus.prop": 42},
        "land_brace": {"media.name": "R83BRV", "bogus.prop": 42},
        "land_json": {"media.name": "R83JSV"},
        "land_comma": {"media.name": "R83CMV", "bogus.prop": 42},
    }
    for sid, w in want.items():
        leg = legs[sid]
        p = props_of(leg, f"input.{leg['ltag']}") or {}
        chk(f"{name}/{sid}: landing form verbatim",
            all(p.get(k) == v for k, v in w.items()),
            {k: p.get(k) for k in w})
        chk(f"{name}/{sid}: input published",
            leg.get("node_waits", {}).get(f"input.{leg['ltag']}",
                                          {}).get("ready") is True,
            leg.get("node_waits"))
    leg = legs["land_oside"]
    p = props_of(leg, f"output.{leg['ltag']}") or {}
    chk(f"{name}/land_oside: -o landed on output",
        p.get("media.name") == "R83OSV" and p.get("bogus.prop") == 7,
        {k: p.get(k) for k in ("media.name", "bogus.prop")})
    pi = props_of(leg, f"input.{leg['ltag']}") or {}
    chk(f"{name}/land_oside: -o did NOT write input",
        pi.get("media.name") != "R83OSV", pi.get("media.name"))
    leg = legs["land_override"]
    p = props_of(leg, f"{leg['ltag'].replace('_land_override', '_capx')}") or {}
    chk(f"{name}/land_override: node.name= override landed",
        p.get("media.name") == "R83NV", p.get("media.name"))
    absent = [bool((s.get("absent_probe") or {}).get(
        f"input.{leg['ltag']}")) for s in leg.get("samples") or []]
    chk(f"{name}/land_override: default input.<n> never published",
        absent and not any(absent), absent)
    drops = [s for s in legs if s.startswith("drop_")]
    chk(f"{name}: 7 drop legs (5 shapes + partial + rep)",
        len(drops) == 7, sorted(drops))
    for sid in sorted(drops):
        leg = legs[sid]
        tag = leg["ltag"]
        p = props_of(leg, f"input.{tag}") or {}
        chk(f"{name}/{sid}: ran to bound",
            leg.get("killed_at_bound") is True, leg.get("exit_code"))
        chk(f"{name}/{sid}: stderr empty",
            not (leg.get("stderr_tail") or "").strip(),
            leg.get("stderr_tail"))
        chk(f"{name}/{sid}: full defaults",
            p.get("media.name") == f"{tag} input", p.get("media.name"))
        if sid == "drop_partial":
            chk(f"{name}/{sid}: a='b' landed (partial)",
                p.get("a") == "b", p.get("a"))
        else:
            chk(f"{name}/{sid}: bogus.prop dropped",
                p.get("bogus.prop") is None, p.get("bogus.prop"))
    frags = {0: "Mismatched bracket", 1: "Mismatched bracket",
             2: "Expected object value", 3: "Expected object value"}
    for i in range(4):
        for rep in range(2):
            sid = f"err_{i}_{rep}"
            leg = legs[sid]
            head = " ".join(leg.get("stderr_head") or [])
            chk(f"{name}/{sid}: rc=255", leg.get("exit_code") == 255,
                leg.get("exit_code"))
            chk(f"{name}/{sid}: class props_syntax_error",
                leg.get("error_class") == "props_syntax_error",
                leg.get("error_class"))
            chk(f"{name}/{sid}: stderr frag {frags[i]!r}",
                frags[i] in head, head)
            chk(f"{name}/{sid}: zero nodes", leg.get("nodes_after") == [],
                leg.get("nodes_after"))
    leg = legs["pc_drop"]
    chk(f"{name}/pc_drop: ran to bound", leg.get("killed_at_bound") is True,
        leg.get("exit_code"))
    chk(f"{name}/pc_drop: no syntax error in tail",
        "syntax error" not in (leg.get("stderr_tail") or ""),
        leg.get("stderr_tail"))
    chk(f"{name}/pc_drop: pw-cat node published",
        bool((leg.get("sample") or {}).get("node")),
        (leg.get("sample") or {}).get("node"))
    for sid in ("pc_err_0", "pc_err_1", "pc_err_noval",
                "pr_err_0", "pr_err_1"):
        leg = legs[sid]
        frag = "Expected object value" if sid == "pc_err_noval" \
            else "Mismatched bracket"
        head = " ".join(leg.get("stderr_head") or [])
        chk(f"{name}/{sid}: rc=1", leg.get("exit_code") == 1,
            leg.get("exit_code"))
        chk(f"{name}/{sid}: class pwcat_props_syntax_error",
            leg.get("error_class") == "pwcat_props_syntax_error",
            leg.get("error_class"))
        chk(f"{name}/{sid}: frag {frag!r}", frag in head, head)
        chk(f"{name}/{sid}: zero nodes", leg.get("nodes_after") == [],
            leg.get("nodes_after"))
    for sid, w in (("pr_land", {"media.name": "R83RECV",
                                "bogus.prop": 9}),
                   ("pc_multi", {"media.name": "R83MV",
                                 "bogus.prop": 3})):
        p = ((legs[sid].get("sample") or {}).get("node") or {}).get(
            "props") or {}
        chk(f"{name}/{sid}: props landed",
            all(p.get(k) == v for k, v in w.items()),
            {k: p.get(k) for k in w})


# ---------------------------------------------------------------- entry 2
def audit_segv(name, e):
    legs = e["legs"]
    chk(f"{name}: 19 legs", len(legs) == 19, len(legs))
    ctl = legs["ctl_lb"]
    chk(f"{name}: control ran to bound",
        ctl.get("killed_at_bound") is True and ctl.get("exit_code") == -9,
        (ctl.get("killed_at_bound"), ctl.get("exit_code")))
    crash = {k: v for k, v in legs.items() if k != "ctl_lb"}
    chk(f"{name}: 18 crash legs", len(crash) == 18, len(crash))
    for sid, leg in sorted(crash.items()):
        chk(f"{name}/{sid}: rc=-11 SIGSEGV",
            leg.get("exit_code") == -11 and leg.get("signal") == "SIGSEGV",
            (leg.get("exit_code"), leg.get("signal")))
        chk(f"{name}/{sid}: zero nodes", leg.get("nodes_after") == [],
            leg.get("nodes_after"))


# ---------------------------------------------------------------- entry 3
def audit_latency(name, e):
    legs = e["legs"]
    chk(f"{name}: 26 legs", len(legs) == 26, len(legs))
    want = {"l5": "240/48000", "l5_r2": "240/48000",
            "l2_5": "96/48000", "l10000": "480000/48000",
            "lneg5": "4294967056/48000", "lneg5_r2": "4294967056/48000",
            "d025": "4000/48000", "d10": "16000/48000",
            "ld_order": "240/48000", "dl_order": "240/48000"}
    for sid, wv in want.items():
        p = props_of(legs[sid], f"input.{legs[sid]['ltag']}") or {}
        chk(f"{name}/{sid}: node.latency {wv}",
            p.get("node.latency") == wv, p.get("node.latency"))
    for sid in ("l0", "labc", "dneg1", "dabc", "d0"):
        leg = legs[sid]
        p = props_of(leg, f"input.{leg['ltag']}") or {}
        chk(f"{name}/{sid}: node.latency absent",
            p.get("node.latency") is None, p.get("node.latency"))
        chk(f"{name}/{sid}: client alive at bound",
            leg.get("killed_at_bound") is True, leg.get("exit_code"))
    leg = legs["g_group"]
    for wn in (f"input.{leg['ltag']}", f"output.{leg['ltag']}"):
        p = props_of(leg, wn) or {}
        chk(f"{name}/g_group:{wn}: node.group landed",
            p.get("node.group") == e["legs"]["g_group"]["ltag"].split(
                "_g_group")[0].replace("r83a_", "r83a_grp_"),
            p.get("node.group"))
    ctl = sorted(t for t in (legs[f"onset_ctl_{r}"].get("transport_s")
                             for r in range(3)) if t is not None)
    chk(f"{name}: >=2 control transports", len(ctl) >= 2, ctl)
    if len(ctl) >= 2:
        med = ctl[len(ctl) // 2]
        chk(f"{name}: control transports under 0.50s",
            all(t <= 0.50 for t in ctl), ctl)
        chk(f"{name}: recorded ctl_median matches recompute",
            e["onset_summary"].get("ctl_median_s") == med,
            (e["onset_summary"].get("ctl_median_s"), med))
        d10 = [legs[f"onset_d10_{r}"].get("transport_s")
               for r in range(3)]
        d10 = [t for t in d10 if t is not None]
        deltas = [round(t - med, 4) for t in d10]
        chk(f"{name}: d10 deltas in [0.75,1.45]",
            len(d10) >= 2 and all(0.75 <= d <= 1.45 for d in deltas),
            deltas)
        chk(f"{name}: recorded d10 deltas match recompute",
            e["onset_summary"].get("d10_deltas_vs_ctl") == deltas,
            (e["onset_summary"].get("d10_deltas_vs_ctl"), deltas))
        d025 = [t for t in (legs[f"onset_d025_{r}"].get("transport_s")
                            for r in range(2)) if t is not None]
        d025d = [round(t - med, 4) for t in d025]
        chk(f"{name}: d025 deltas in [0.08,0.60]",
            all(0.08 <= d <= 0.60 for d in d025d), d025d)
        l1000 = [t for t in (legs[f"onset_l1000_{r}"].get("transport_s")
                             for r in range(2)) if t is not None]
        chk(f"{name}: -l 1000 adds no delay (<=0.75s)",
            all(t <= 0.75 for t in l1000), l1000)
    chk(f"{name}: all d10 legs linked",
        all(legs[f"onset_d10_{r}"].get("linked") is True
            for r in range(3)),
        [legs[f"onset_d10_{r}"].get("linked") for r in range(3)])
    # the fixture gates only d10 on `linked`; report the others
    chk(f"{name}: [advisory] ctl/d025/l1000 link state",
        True,
        json.dumps({k: legs[k].get("linked") for k in
                    ("onset_ctl_0", "onset_ctl_1", "onset_ctl_2",
                     "onset_d025_0", "onset_d025_1",
                     "onset_l1000_0", "onset_l1000_1")}))


# ---------------------------------------------------------------- entry 4
def audit_matrix(name, e):
    legs = e["legs"]
    chk(f"{name}: 13 legs", len(legs) == 13, len(legs))
    fl, fr = FL, FR
    s = e["matrix_summary"]
    chk(f"{name}: control tone arms >=2",
        s.get("control_tone_arms", 0) >= 2, s.get("control_tone_arms"))
    med = s.get("control_full_amp_median")
    chk(f"{name}: control full-amp median >= 3000",
        med is not None and med >= 3000, med)
    lo, hi = 0.42, 0.58
    if med:
        for rep in range(3):
            leg = legs[f"c1_mono_{rep}"]
            wins = (leg.get("window_amps") or {}).get("windows") or []
            audio = (leg.get("tap") or {}).get("audio_windows", 0)
            if not wins or audio == 0:
                chk(f"{name}/c1_mono_{rep}: recorded as unmeasured",
                    leg.get("mono_outcome") == "silent_or_thin",
                    leg.get("mono_outcome"))
                continue
            bad = [(w["at_s"], ch, f, w.get(f"a{ch}_{int(f)}"))
                   for w in wins for ch in (0, 1) for f in (fl, fr)
                   if not (lo * med <= w.get(f"a{ch}_{int(f)}", 0)
                           <= hi * med)]
            chk(f"{name}/c1_mono_{rep}: every window in 0.5*(L+R) band",
                not bad, bad[:3])
            chk(f"{name}/c1_mono_{rep}: outcome label stable",
                leg.get("mono_outcome") == "stable",
                leg.get("mono_outcome"))
        chk(f"{name}: >=2 c1_mono legs with audio",
            s.get("c1_audio_legs", 0) >= 2, s.get("c1_audio_legs"))
        realized = []
        for rep in range(3):
            leg = legs[f"m_alone_{rep}"]
            wins = (leg.get("window_amps") or {}).get("windows") or []
            audio = (leg.get("tap") or {}).get("audio_windows", 0)
            if not wins or audio == 0:
                realized.append("unmeasured")
                continue
            mix_dev = max(
                abs(w.get(f"a{ch}_{int(f)}", 0) - 0.5 * med) / (0.5 * med)
                for w in wins for ch in (0, 1) for f in (fl, fr))
            pass_dev = max(
                max(abs(w.get(f"a0_{int(fl)}", 0) - med),
                    abs(w.get(f"a1_{int(fr)}", 0) - med),
                    w.get(f"a0_{int(fr)}", 0),
                    w.get(f"a1_{int(fl)}", 0)) / med
                for w in wins)
            label = ("stable_mono" if mix_dev <= 0.25 else
                     "stereo_passthrough" if pass_dev <= 0.25 else
                     "time_varying")
            realized.append(label)
            chk(f"{name}/m_alone_{rep}: recorded dev ratios match",
                leg.get("mono_mix_dev_ratio") == round(mix_dev, 3) and
                leg.get("stereo_pass_dev_ratio") == round(pass_dev, 3),
                (leg.get("mono_mix_dev_ratio"), round(mix_dev, 3),
                 leg.get("stereo_pass_dev_ratio"), round(pass_dev, 3)))
            chk(f"{name}/m_alone_{rep}: recorded arm matches recompute",
                leg.get("mono_outcome") == label,
                (leg.get("mono_outcome"), label))
        chk(f"{name}: realized arms recorded",
            s.get("m_alone_realized_arms") == realized,
            (s.get("m_alone_realized_arms"), realized))
        chk(f"{name}: m_alone is NOT asserted stable (arm-recorded)",
            any(o != "stable_mono" or True for o in realized),
            realized)
    for sid, w in (("prop_pos", {"audio.position": "[ MONO ]"}),
                   ("prop_chmap", {"channelmap.map": "[ MONO ]"}),
                   ("prop_chpos", {"audio.channels": 1,
                                   "audio.position": "[ MONO ]"})):
        leg = legs[sid]
        p = props_of(leg, f"input.{leg['ltag']}") or {}
        chk(f"{name}/{sid}: props landed verbatim",
            all(p.get(k) == v for k, v in w.items()),
            {k: p.get(k) for k in w})
        chk(f"{name}/{sid}: stereo tag carried (props inert)",
            (leg.get("tap") or {}).get("carries_tone") is True,
            (leg.get("tap") or {}).get("carries_tone"))


# ---------------------------------------------------------------- entry 5
def audit_remix(name, e):
    legs = e["legs"]
    chk(f"{name}: 18 legs", len(legs) == 18, len(legs))
    fl, fr = FL, FR
    ref = [ch_amp(legs[f"m0_ctl_{r}"], 0, fl) for r in range(2)]
    ref = [a for a in ref if a]
    med = sorted(ref)[len(ref) // 2] if ref else None
    chk(f"{name}: recorded control median matches recompute",
        e["remix_summary"].get("control_full_amp_median") == med,
        (e["remix_summary"].get("control_full_amp_median"), med))
    for rep in range(2):
        leg = legs[f"m0_ctl_{rep}"]
        chk(f"{name}/m0_ctl_{rep}: tap ran",
            (leg.get("tap") or {}).get("ran") is True,
            (leg.get("tap") or {}).get("ran"))
        for ch in (0, 1):
            a = ch_amp(leg, ch, fl)
            chk(f"{name}/m0_ctl_{rep}: ch{ch} full-amp upmix",
                a is not None and a >= 0.75 * 8192, a)
    if med:
        for sid in ("m1_ndr_0", "m1_ndr_1", "m3_upmix", "m4_cmdis"):
            for ch in (0, 1):
                a = ch_amp(legs[sid], ch, fl)
                chk(f"{name}/{sid}: ch{ch} inert == control",
                    a is not None and a >= 0.75 * med, a)
        for rep in range(3):
            leg = legs[f"m2_sdr_{rep}"]
            chk(f"{name}/m2_sdr_{rep}: output_MONO only",
                leg.get("out_port_names") == ["output_MONO"],
                leg.get("out_port_names"))
            a0, a1 = ch_amp(leg, 0, fl), ch_amp(leg, 1, fl)
            chk(f"{name}/m2_sdr_{rep}: FL full amp",
                a0 is not None and a0 >= 0.75 * med, a0)
            chk(f"{name}/m2_sdr_{rep}: FR silent",
                a1 is not None and a1 <= 0.08 * med, a1)
        for sid in ("w1_widen", "w2_method"):
            for ch, f in ((0, fl), (1, fr)):
                a = ch_amp(legs[sid], ch, f)
                chk(f"{name}/{sid}: ch{ch}@{int(f)} inert",
                    a is not None and a >= 0.75 * med, a)
        for rep in range(2):
            leg = legs[f"d0_ctl_{rep}"]
            bad = [(ch, f, ch_amp(leg, ch, f)) for ch in (0, 1)
                   for f in (fl, fr)
                   if not (0.42 * med <= (ch_amp(leg, ch, f) or 0)
                           <= 0.58 * med)]
            chk(f"{name}/d0_ctl_{rep}: mono-sink downmix 0.5*(L+R)",
                not bad, bad)
        for rep in range(2):
            leg = legs[f"d3_sdr_{rep}"]
            af, ar = ch_amp(leg, 0, fl), ch_amp(leg, 0, fr)
            chk(f"{name}/d3_sdr_{rep}: FL full amp",
                af is not None and af >= 0.75 * med, af)
            chk(f"{name}/d3_sdr_{rep}: FR dropped",
                ar is not None and ar <= 0.08 * med, ar)
    for sid, prop, wv in (("m1_ndr_0", "node.dont-remix", True),
                          ("m2_sdr_0", "stream.dont-remix", True),
                          ("m3_upmix", "channelmix.upmix", False),
                          ("m4_cmdis", "channelmix.disabled", True),
                          ("w1_widen", "channelmix.stereo-widen", 1.0),
                          ("p0_passive", "node.passive", True)):
        p = ((legs[sid].get("sample") or {}).get("node") or {}).get(
            "props") or {}
        chk(f"{name}/{sid}: {prop} landed verbatim",
            p.get(prop) == wv, (prop, p.get(prop), wv))
    chk(f"{name}/p0_passive: tone carried",
        (legs["p0_passive"].get("tap") or {}).get("carries_tone") is True,
        (legs["p0_passive"].get("tap") or {}).get("carries_tone"))
    leg = legs["dm_move"]
    p = ((leg.get("pre_move") or {}).get("node") or {}).get("props") or {}
    chk(f"{name}/dm_move: node.dont-move landed",
        p.get("node.dont-move") is True, p.get("node.dont-move"))
    chk(f"{name}/dm_move: move rc=0 (silent no-op)",
        leg.get("move_rc") == 0, leg.get("move_rc"))
    chk(f"{name}/dm_move: post-move consumers unchanged",
        leg.get("post_move_consumers") == [e["legs"]["dm_move"].get(
            "sink_input") and leg.get("tap", {}).get("target")],
        (leg.get("post_move_consumers"), leg.get("tap", {}).get("target")))
    chk(f"{name}/dm_move: tone carried",
        (leg.get("tap") or {}).get("carries_tone") is True,
        (leg.get("tap") or {}).get("carries_tone"))


# ---------------------------------------------------------------- entry 6
def audit_resample(name, e):
    legs = e["legs"]
    chk(f"{name}: 15 legs", len(legs) == 15, len(legs))
    fl, fr = FL, FR
    clean = [ch_amp(legs[f"s0_ctl_{r}"], 0, fl) for r in range(2)]
    clean = [a for a in clean if a]
    med = sorted(clean)[len(clean) // 2] if clean else None
    chk(f"{name}: recorded clean median matches recompute",
        e["resample_summary"].get("clean_amp_median") == med,
        (e["resample_summary"].get("clean_amp_median"), med))
    for rep in range(2):
        leg = legs[f"s0_ctl_{rep}"]
        p = ((leg.get("sample") or {}).get("node") or {}).get("props") or {}
        chk(f"{name}/s0_ctl_{rep}: node.rate 1/44100",
            p.get("node.rate") == "1/44100", p.get("node.rate"))
        chk(f"{name}/s0_ctl_{rep}: tone carried",
            (leg.get("tap") or {}).get("carries_tone") is True,
            (leg.get("tap") or {}).get("carries_tone"))
    for rep in range(3):
        leg = legs[f"s1_disable_{rep}"]
        chans = (leg.get("tap_stats") or {}).get("channels") or []
        p = ((leg.get("sample") or {}).get("node") or {}).get("props") or {}
        cons = (leg.get("sample") or {}).get("consumers")
        chk(f"{name}/s1_disable_{rep}: all-zero monitor",
            bool(chans) and all(c.get("all_zero") for c in chans),
            [c.get("all_zero") for c in chans])
        chk(f"{name}/s1_disable_{rep}: resample.disable landed",
            p.get("resample.disable") is True, p.get("resample.disable"))
        chk(f"{name}/s1_disable_{rep}: links live (consumers non-empty)",
            bool(cons), cons)
        chk(f"{name}/s1_disable_{rep}: outcome label",
            leg.get("artifact_outcome") == "all_zero",
            leg.get("artifact_outcome"))
    for sid in ("s1b_matched", "s1c_false"):
        chk(f"{name}/{sid}: tone carried",
            (legs[sid].get("tap") or {}).get("carries_tone") is True,
            (legs[sid].get("tap") or {}).get("carries_tone"))
    if med:
        for rep in range(3):
            leg = legs[f"s4_peaks_{rep}"]
            chans = (leg.get("tap_stats") or {}).get("channels") or []
            marks = []
            for ci, c in enumerate(chans[:2]):
                if c.get("min") is None:
                    continue
                f0 = (fl, fr)[ci]
                if c["min"] < -64 or c["neg_frac"] > 0.01:
                    marks.append(f"ch{ci} min={c['min']} "
                                 f"neg={c['neg_frac']}")
                if c["mean"] < 1500:
                    marks.append(f"ch{ci} mean={c['mean']}")
                af = c.get(f"amp_at_{int(f0)}")
                a2 = c.get(f"amp_at_{int(2 * f0)}")
                if af is not None and af > 0.10 * med:
                    marks.append(f"ch{ci} fundamental survives ({af})")
                if a2 is not None and a2 < 0.20 * med:
                    marks.append(f"ch{ci} octave absent ({a2})")
                if af and a2 is not None and a2 < 15 * af:
                    marks.append(f"ch{ci} octave not dominant "
                                 f"({a2} vs {af})")
            chk(f"{name}/s4_peaks_{rep}: full-wave |x| octave artifact",
                not marks, marks)
            chk(f"{name}/s4_peaks_{rep}: outcome label",
                leg.get("artifact_outcome") == "full_wave_abs_octave",
                leg.get("artifact_outcome"))
            if chans:
                chk(f"{name}/s4_peaks_{rep}: [advisory] zero_frac",
                    True, [c.get("zero_frac") for c in chans])
        for sid in ("s4b_matched", "s4c_downsample"):
            leg = legs[sid]
            chans = (leg.get("tap_stats") or {}).get("channels") or []
            clean_shape = bool(chans) and all(
                c.get("min", 0) < -64 and c.get("neg_frac", 0) > 0.2 and
                (c.get(f"amp_at_{int((fl, fr)[ci])}") or 0) > 0.5 * med
                for ci, c in enumerate(chans[:2]))
            chk(f"{name}/{sid}: clean (upsample-only claim)",
                clean_shape and leg.get("artifact_outcome") == "clean",
                (clean_shape, leg.get("artifact_outcome")))
    p = ((legs["s5_rate"].get("sample") or {}).get("node") or {}).get(
        "props") or {}
    chk(f"{name}/s5_rate: --rate 48000 did NOT change node.rate",
        p.get("node.rate") == "1/44100", p.get("node.rate"))
    for sid, wv in (("q0", 0), ("q14", 14)):
        p = ((legs[sid].get("sample") or {}).get("node") or {}).get(
            "props") or {}
        chk(f"{name}/{sid}: resample.quality == {wv}",
            p.get("resample.quality") == wv, p.get("resample.quality"))
        chk(f"{name}/{sid}: tone carried",
            (legs[sid].get("tap") or {}).get("carries_tone") is True,
            (legs[sid].get("tap") or {}).get("carries_tone"))


# ---------------------------------------------------------------- entry 7
def audit_failopen(name, e):
    legs = e["legs"]
    chk(f"{name}: 8 legs", len(legs) == 8, len(legs))
    nsa = e["sink_loads"] and next(iter(e["sink_loads"]))
    nsb = list(e["sink_loads"])[1] if len(e["sink_loads"]) > 1 else None
    s = last_sample(legs["ctl"])
    chk(f"{name}/ctl: loopback on probe sinks",
        s.get("input_producers") == [nsa] and
        s.get("output_consumers") == [nsb],
        (s.get("input_producers"), s.get("output_consumers")))
    own = {nsa, nsb}
    for rep in range(2):
        leg = legs[f"c_empty_{rep}"]
        s = last_sample(leg)
        prods = s.get("input_producers") or []
        pcls = s.get("producer_classes") or {}
        chk(f"{name}/c_empty_{rep}: single foreign Audio/ producer",
            len(prods) == 1 and prods[0] not in own and
            str(pcls.get(prods[0]) or "").startswith("Audio/"),
            (prods, pcls))
        chk(f"{name}/c_empty_{rep}: -P still on probe sink",
            s.get("output_consumers") == [nsb],
            s.get("output_consumers"))
        chk(f"{name}/c_empty_{rep}: content witness declined",
            "declined" in (leg.get("content_witness") or ""),
            leg.get("content_witness"))
        leg2 = legs[f"p_empty_{rep}"]
        s = last_sample(leg2)
        cons = s.get("output_consumers") or []
        ccls = s.get("consumer_classes") or {}
        chk(f"{name}/p_empty_{rep}: single foreign Audio/Sink consumer",
            len(cons) == 1 and cons[0] not in own and
            ccls.get(cons[0]) == "Audio/Sink", (cons, ccls))
        chk(f"{name}/p_empty_{rep}: -C still on probe sink",
            s.get("input_producers") == [nsa], s.get("input_producers"))
        chk(f"{name}/p_empty_{rep}: silence-only witness",
            "silence-only" in (leg2.get("content_witness") or ""),
            leg2.get("content_witness"))
    leg = legs["n_empty"]
    s = last_sample(leg)
    nd = s.get("nodes") or {}
    chk(f"{name}/n_empty: literal capture.props nodes published",
        bool(nd.get("input.capture.props")) and
        bool(nd.get("output.capture.props")), list(nd))
    cons = s.get("output_consumers") or []
    ccls = s.get("consumer_classes") or {}
    chk(f"{name}/n_empty: fail-open to foreign sink",
        len(cons) == 1 and cons[0] not in own and
        ccls.get(cons[0]) == "Audio/Sink" and
        leg.get("outcome") == "failopen_foreign_sink", (cons, ccls,
                                                        leg.get("outcome")))
    for rep in range(2):
        s = last_sample(legs[f"serial_{rep}"])
        chk(f"{name}/serial_{rep}: object.serial resolved to probe sinks",
            s.get("input_producers") == [nsa] and
            s.get("output_consumers") == [nsb],
            (s.get("input_producers"), s.get("output_consumers")))
    chk(f"{name}: serials recorded",
        isinstance(e.get("serials", {}).get("nsa"), int) and
        isinstance(e.get("serials", {}).get("nsb"), int),
        e.get("serials"))


# ------------------------------------------------------------------- main
def audit_run(tag, path):
    d = json.loads(path.read_text())
    ms = d["measurements"]
    probes = {k: v for k, v in ms.items() if k.startswith("pwcat_")}
    chk(f"{tag}: mode probe-pwcat-r83",
        d.get("mode") == "probe-pwcat-r83", d.get("mode"))
    chk(f"{tag}: 7 r83 entries", len(probes) == 7, sorted(probes))
    chk(f"{tag}: 128 legs total",
        sum(len(v.get("legs") or {}) for v in probes.values()) == 128,
        sum(len(v.get("legs") or {}) for v in probes.values()))
    for name, e in probes.items():
        entry_teardown(f"{tag}/{name}", e)
    global FL, FR
    FL, FR = tone_pair(probes["pwcat_channel_matrix_r83_probe"])
    chk(f"{tag}: tone pair derived from own_pid",
        True, f"{FL}/{FR}")
    audit_props(f"{tag}/props", probes["pwcat_props_parse_r83_probe"])
    audit_segv(f"{tag}/segv", probes["pwcat_empty_props_segv_r83_probe"])
    audit_latency(f"{tag}/latency",
                  probes["pwcat_latency_props_r83_probe"])
    audit_matrix(f"{tag}/matrix",
                 probes["pwcat_channel_matrix_r83_probe"])
    audit_remix(f"{tag}/remix", probes["pwcat_remix_props_r83_probe"])
    audit_resample(f"{tag}/resample",
                   probes["pwcat_resample_props_r83_probe"])
    audit_failopen(f"{tag}/failopen",
                   probes["pwcat_failopen_args_r83_probe"])


def main():
    runs = {
        "run1": ROOT / "corpus/live/r83-author/measurements-run1.json",
        "run2": ROOT / "corpus/live/r83-author/measurements-run2.json",
    }
    for tag, path in runs.items():
        if not path.exists():
            print(f"MISSING {path}", file=sys.stderr)
            return 2
        audit_run(tag, path)
    bad = [c for c in CHECKS if not c["ok"]]
    out = {"checks": len(CHECKS), "failed": len(bad),
           "failures": bad, "results": CHECKS}
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(f"checks={len(CHECKS)} failed={len(bad)}")
    for c in bad:
        print("  FAIL", c["check"], "->", c["detail"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
