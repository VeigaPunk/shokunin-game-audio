#!/usr/bin/env python3
"""r78 critic — replay each entry's gate over the final receipt, then mutate.

Re-implements the failure predicates of measure_audio.py's r78 entries as
pure functions over the recorded leg dicts. For each entry: (a) replay the
recorded legs -> reproduce the zero-failure verdict; (b) apply targeted
mutations (dead tap, absent leg, foreign/wrong outcomes) -> show which
mutations still pass (forged/vacuous PASS) vs which are caught.
"""
import copy
import json
import sys

E = json.load(open("/home/vgpnk/Projects/shokunin/audio-shokunin/"
                   "corpus/live/r78-critic/r78-entries.json"))

LAT_TONE_S = 2.6
LOSS_TONE_S = 6.0
LOSS_EVENT_S = 2.0
TAP_LEAD_S = 0.4
STALL_BOUND_S = 6.0


def gate_lattice(lat):
    """Re-implements playback_target_lattice_r78_entry's failure loop."""
    inv = lat["inventory"]
    peer = (lat.get("source_peer") or {}).get("peer_sink")
    sinks = inv["sinks"]
    tg = {"probe_sink": None, "other_sink": None, "source": None,
          "probe_monitor": None}
    # resolvers: rebuild from recorded target_arg / known names
    fails = []
    legs = lat["legs"]
    TABLE = [
        ("probe_sink", "honored"),
        ("other_sink", "honored"),
        ("garbage", "fallback"), ("absent_sink", "fallback"),
        ("default_token", "fallback"), ("pulse_token", "fallback"),
        ("at_default_sink", "fallback"), ("at_default_monitor", "fallback"),
        ("at_default_source", "fallback"), ("source_name", "fallback"),
        ("monitor_name", "source_peer"), ("empty_target", "fallback"),
        ("no_target", "fallback"), ("target_0", "unlinked_stall"),
    ]
    for name, expect in TABLE:
        leg = legs.get(name)
        if leg is None:
            fails.append(f"{name}: leg absent")
            continue
        if "blocked" in leg:
            continue
        if expect == "unlinked_stall":
            if not leg["killed_at_bound"]:
                fails.append(f"{name}: must stall")
            if leg["consumers_union"]:
                fails.append(f"{name}: fed consumers")
            ports = {p for s in leg["samples"]
                     for p in (s.get("output_ports") or [])}
            if len(ports) < 2:
                fails.append(f"{name}: ports <2")
            states = [s.get("node", {}).get("state") for s in leg["samples"]
                      if s.get("node", {}).get("found")]
            if states and "suspended" not in states:
                fails.append(f"{name}: no suspended state")
            if (leg.get("tap") or {}).get("mine_windows"):
                fails.append(f"{name}: tone on default")
            continue
        if expect == "source_peer":
            if leg["exit_code"] != 0 or leg["error_class"] is not None:
                fails.append(f"{name}: rc/stderr")
            d0l = leg["default_sink_at_leg"]
            allowed = {d0l, peer} - {None}
            if not leg["consumers_union"] or \
                    set(leg["consumers_union"]) - allowed:
                fails.append(f"{name}: consumers outside allowed")
            if d0l and d0l in leg["consumers_union"] and \
                    not leg.get("carries_tone"):
                fails.append(f"{name}: default consumed w/o tone")
            continue
        d0 = leg["default_sink_at_leg"]
        want = leg["target_arg"] if expect == "honored" else d0
        if leg["exit_code"] != 0 or leg["error_class"] is not None:
            fails.append(f"{name}: rc/stderr")
        if leg["consumers_union"] != [want]:
            foreign = [n for n in leg["consumers_union"]
                       if n not in ({want, d0} | set(sinks))]
            if foreign:
                pass  # confound recorded, NOT a failure
            else:
                fails.append(f"{name}: consumers != [{want}]")
        if not leg.get("carries_tone"):
            fails.append(f"{name}: no tag tone on tap")
        if expect == "fallback" and leg["wall_s"] < LAT_TONE_S - 0.6:
            fails.append(f"{name}: wall too short")
    if not any(l.get("target_object_lies") for l in legs.values()
               if isinstance(l, dict)):
        fails.append("no fallback leg advertised request")
    if lat.get("probe_sink_gone") is not True:
        fails.append("teardown")
    return fails


def gate_follow(fl):
    fails = []
    legs = fl["legs"]
    meta0 = fl["metadata_initial"]["name"]
    s_new = fl["def_sink_load"]  # name recovered from switches
    s_new_name = None
    # recover s_new from 'moved' leg expectation
    s_new_name = legs["moved"]["consumers_union"][0]
    exp = {"before": meta0, "moved": s_new_name, "restored": meta0}
    for name, want in exp.items():
        leg = legs.get(name)
        if leg is None:
            fails.append(f"{name} absent")
            continue
        if leg["exit_code"] != 0 or leg["error_class"] is not None:
            fails.append(f"{name} rc/stderr")
        if leg["consumers_union"] != [want]:
            fails.append(f"{name} consumers")
        if not leg.get("carries_tone"):
            fails.append(f"{name} no tone")
    sp = legs.get("still_probe") or {}
    allowed = {s_new_name, meta0}
    if sp:
        if sp["exit_code"] != 0 or sp["error_class"] is not None:
            fails.append("still_probe rc")
        for s in sp.get("samples", []):
            if not s["live"] or set(s["nodes"]) - allowed:
                fails.append("still_probe consumers outside set")
                break
    if fl["switches"]["to_probe"]["applied"]["applied"] is not True:
        fails.append("switch never applied")
    pa = fl["switches"]["pactl"]
    if not (pa.get("pactl_stale_default") or pa.get("pactl_delayed_default")):
        fails.append("pactl neither stale nor delayed")
    nf = legs.get("nofollow") or {}
    nfs = nf.get("samples", [])
    nf_pre = nfs[0]["nodes"] if nfs else None
    nf_post = [s["nodes"] for s in nfs[1:]]
    allowed_nf = {tuple(nf_pre or []), (meta0,)}
    followed = bool(nf_post) and all(p == [meta0] for p in nf_post)
    pinned = bool(nf_post) and all(p == nf_pre for p in nf_post)
    if not nf_pre or any(tuple(p) not in allowed_nf for p in nf_post):
        fails.append("nofollow post outside set")
    elif not (followed or pinned):
        fails.append("nofollow neither followed nor pinned")
    mevs = [f for f in nf.get("fired", []) if f["kind"] == "metadata_default"]
    if not mevs or mevs[0].get("exit") != 0:
        fails.append("restore did not fire")
    if nf.get("exit_code") != 0:
        fails.append("nofollow rc")
    if fl["metadata_final"].get("name") != meta0:
        fails.append("restore left dirty")
    if fl.get("def_sink_gone") is not True:
        fails.append("teardown")
    return fails


def gate_loss(tl):
    fails = []
    legs = tl["legs"]
    d0 = tl["fallback_node"]
    sink = tl["sink_name"]
    u = legs.get("unload_relink") or {}
    us = u.get("samples", [])
    if (us[0]["nodes"] if us else None) != [sink]:
        fails.append("unload pre consumers")
    if any(s["nodes"] != [d0] for s in us[1:]):
        fails.append("unload post consumers")
    unf = [f for f in u.get("fired", [])
           if f["kind"] == "unload_module" and f.get("exit_code") != 0]
    if unf or not any(f["kind"] == "unload_module"
                      for f in u.get("fired", [])):
        fails.append("unload event not clean")
    if u.get("exit_code") != 0 or u.get("error_class") is not None:
        fails.append("unload rc/stderr")
    if u.get("wall_s", 0) < LOSS_TONE_S - 0.6:
        fails.append("unload wall")
    tu = u.get("tap") or {}
    pre = [w for w in tu.get("windows", [])
           if w["at_s"] < LOSS_EVENT_S + TAP_LEAD_S - 0.3]
    if any(w["mine"] for w in pre):
        fails.append("tone on default before loss")
    post_spans = [s for s in tu.get("mine_spans", [])
                  if s[0] >= LOSS_EVENT_S - 0.4]
    if not tu.get("carries_tone") or not post_spans:
        fails.append("relink unproven")
    m = legs.get("manual_unlink") or {}
    if "blocked" not in m:
        ms = m.get("samples", [])
        if (ms[0]["nodes"] if ms else None) != [sink]:
            fails.append("unlink pre consumers")
        if any(s["nodes"] for s in ms[1:]):
            fails.append("unlink post consumers")
        lrc = [l["exit"] for f in m.get("fired", [])
               if f["kind"] == "pwlink_d" for l in f.get("links", [])]
        if not lrc or any(rc != 0 for rc in lrc):
            fails.append("unlink rc")
        if m.get("exit_code") != 0 or m.get("error_class") is not None:
            fails.append("unlink rc/stderr")
        if m.get("wall_s", 0) < LOSS_TONE_S - 0.6:
            fails.append("unlink wall")
        if (m.get("tap_default") or {}).get("mine_windows"):
            fails.append("tone on default")
        ts = m.get("tap_self") or {}
        late = [w for w in ts.get("windows", [])
                if w["at_s"] > LOSS_EVENT_S + TAP_LEAD_S + 0.8]
        early = [w for w in ts.get("windows", [])
                 if w["at_s"] < LOSS_EVENT_S + TAP_LEAD_S]
        if not any(w["mine"] for w in early):
            fails.append("self tap pre unlink unproven")
        if any(w["mine"] for w in late):
            fails.append("tone after unlink")
    if tl.get("sink_gone") is not True:
        fails.append("teardown")
    return fails


def gate_props(pr):
    fails = []
    legs = pr["legs"]
    SPEC = {
        "flag_a_prop_b": False, "flag_b_prop_a": False, "prop_only": False,
        "node_target": False, "flag_garbage_prop_b": False,
        "prop_garbage": False, "node_target_garbage": False,
        "env_props_flag_a": False, "env_props_flag_garbage": False,
        "role_decoration": False, "capture_prop_decoration": False,
        "monitor_prop_decoration": False,
        "autoconnect_false": True, "class_source_stall": True,
    }
    for name, stall in SPEC.items():
        leg = legs.get(name)
        if leg is None:
            fails.append(f"{name} absent")
            continue
        want = leg["expected_nodes"]
        if stall:
            if not leg["killed_at_bound"]:
                fails.append(f"{name} must stall")
            if leg["consumers_union"]:
                fails.append(f"{name} fed consumers")
            ports = {p for s in leg["samples"]
                     for p in (s.get("output_ports") or [])}
            if len(ports) < 2:
                fails.append(f"{name} ports <2")
            continue
        if leg["exit_code"] != 0 or leg["error_class"] is not None:
            fails.append(f"{name} rc/stderr")
        if leg["consumers_union"] != want:
            fails.append(f"{name} consumers")
        if not leg.get("carries_tone"):
            fails.append(f"{name} no tone")
    if pr.get("sinks_gone") is not True:
        fails.append("teardown")
    return fails


def gate_segv(sv):
    fails = []
    legs = sv["legs"]
    a = "r78_prop_a_844895"
    for name, leg in legs.items():
        if not name.startswith("segv_"):
            continue
        if leg["exit_code"] != -11:
            fails.append(f"{name} rc != -11")
        if leg["stderr_tail"]:
            fails.append(f"{name} stderr nonempty")
        if leg["wall_s"] >= 4.0:
            fails.append(f"{name} wall >= 4")
        for s in leg.get("samples", []):
            if s.get("nodes"):
                fails.append(f"{name} consumers")
    ctl = legs.get("control_output") or {}
    if ctl.get("exit_code") != 0 or \
            ctl.get("samples", [{}])[0].get("nodes") != [a]:
        fails.append("control_output")
    bnd = legs.get("boundary_source") or {}
    if not bnd.get("killed_at_bound") or \
            any(s.get("nodes") for s in bnd.get("samples", [])):
        fails.append("boundary_source")
    if sv.get("sink_gone") is not True:
        fails.append("teardown")
    return fails


def gate_aplay(ap):
    fails = []
    legs = ap["legs"]
    pp = legs["params_play"]["params"]
    cp = legs["params_cap"]["params"]
    if pp.get("channels_max") is not None and \
            cp.get("channels_max") is not None:
        if not (pp["channels_max"] > cp["channels_max"]
                and pp["channels_min"] == 2):
            fails.append("envelope channels")
    if "S32_LE" in (pp.get("formats") or []) and \
            "S32_LE" in (cp.get("formats") or []):
        fails.append("S32 in both")
    if legs["hw_baseline"]["exit_code"] != 0:
        fails.append("hw baseline")
    if legs["hw_baseline"].get("new_nodes") not in (None, []):
        fails.append("baseline new nodes")
    if legs["busy_under_witness"].get("error_class") != "alsa_busy":
        fails.append("busy under witness")
    ph = legs["pipewire_hold"]
    if ph["exit_code"] != 0:
        fails.append("hold leg")
    if legs["retention_1s"].get("error_class") != "alsa_busy":
        fails.append("retention 1s")
    if legs["retention_7s"].get("exit_code") != 0:
        fails.append("retention 7s")
    cf = legs["convert_float"]
    if cf["exit_code"] != 0 or not cf.get("converted_to"):
        fails.append("convert")
    rb = legs["refuse_bogus"]
    if rb["exit_code"] != 1 or rb.get("error_class") != "aplay_bad_format" \
            or rb["wall_s"] > 1.0:
        fails.append("refuse bogus")
    ac = legs["arecord_constrain"]
    if ac["exit_code"] == 0:
        fails.append("arecord constrained nothing")
    ah = legs["arecord_honored"]
    acls = ac.get("error_class")
    if ah["exit_code"] != 0 and acls != "alsa_busy":
        fails.append("arecord honored")
    for n in ("plugin_default", "plugin_pipewire"):
        if legs[n]["exit_code"] != 0 or \
                not legs[n]["tap"].get("carries_tone"):
            fails.append(n)
    if legs["pulse_refuse"].get("error_class") != "alsa_unknown_pcm":
        fails.append("pulse refuse")
    nu = legs["null_unpaced"]
    if nu["exit_code"] != 0 or nu["wall_s"] > 0.6:
        fails.append("null unpaced")
    return fails


def gate_zeros(z):
    fails = []
    legs = z["legs"]
    c = z["sink_name"]
    a = legs.get("consumer_unlink") or {}
    if a:
        if a.get("exit_code") != 1 or a.get("bytes") != a.get(
                "expected_bytes") or a.get("data_finalized") is not True:
            fails.append("a rc/bytes/finalized")
        if any(r["exit"] != 0 for r in a.get("unlink_rc", [])):
            fails.append("a unlink rc")
        if any(r["exit"] != 0 for r in a.get("relink_rc", [])):
            fails.append("a relink rc")
        seq = a.get("size_trace", [])
        if len(seq) >= 7:
            if not seq[1]["bytes"] > seq[0]["bytes"] + 80000:
                fails.append("a not growing pre")
            if not seq[4]["bytes"] - seq[2]["bytes"] < 8192:
                fails.append("a not frozen")
            if not seq[6]["bytes"] > seq[4]["bytes"] + 150000:
                fails.append("a not resumed")
        prods = [s.get("nodes") for s in a.get("producer_samples", [])]
        if prods and (prods[0] != [c] or prods[1] != [] or prods[2] != [c]):
            fails.append("a producers")
        wl = (a.get("file_windows") or {}).get("windows", [])
        if wl and not any(w["mine"] for w in wl[:14]):
            fails.append("a baseline unproven")
    b = legs.get("producer_unlink") or {}
    if b:
        if b.get("exit_code") != 1 or b.get("bytes") != b.get(
                "expected_bytes") or b.get("data_finalized") is not True:
            fails.append("b rc/bytes/finalized")
        rcs_b = b.get("unlink_rc")
        if rcs_b and any(r["exit"] != 0 for r in rcs_b):
            fails.append("b unlink rc")
        sq = b.get("size_trace", [])
        if len(sq) >= 2 and not all(
                s2["bytes"] > s1["bytes"] + 50000
                for s1, s2 in zip(sq, sq[1:])):
            fails.append("b growth")
        wlb = (b.get("file_windows") or {}).get("windows", [])
        preb = [w for w in wlb if w["at_s"] < 1.4]
        midb = [w for w in wlb if w["at_s"] > 2.2]
        if not any(w["mine"] for w in preb):
            fails.append("b baseline unproven")
        if midb and any(w["audio"] for w in midb):
            fails.append("b post audio")
        if len(midb) < 3:
            fails.append("b zero windows <3")
    if z.get("sink_gone") is not True:
        fails.append("teardown")
    return fails


def gate_parec(pf):
    fails = []
    legs = pf["legs"]

    def imp(n, k):
        return (legs.get(n) or {}).get(k)

    if imp("rate_req", "implied_rate") != 22050:
        fails.append("rate_req")
    if imp("rate_fix", "implied_rate") != 48000:
        fails.append("rate_fix")
    if imp("fmt_req", "implied_bpf") != 4:
        fails.append("fmt_req")
    if imp("fmt_fix", "implied_bpf") != 4:
        fails.append("fmt_fix")
    if imp("ch_req", "implied_ch") != 1:
        fails.append("ch_req")
    if imp("ch_fix", "implied_ch") != 2:
        fails.append("ch_fix")
    for name, field, wh, ik, wi in (
            ("hdr_rate_fix", "rate", 22050, "implied_rate", 48000),
            ("hdr_fmt_fix", "bits", 16, "implied_bpf", 4),
            ("hdr_ch_fix", "channels", 1, "implied_ch", 2)):
        leg = legs.get(name) or {}
        fmt = leg.get("fmt") or {}
        if not fmt:
            fails.append(f"{name} no fmt")
        elif not (fmt.get(field) == wh and leg.get(ik) == wi):
            fails.append(f"{name} mismatch absent")
    pl = legs.get("hdr_rate_plain") or {}
    pf_ = pl.get("fmt") or {}
    if not (pf_.get("rate") == 22050 and pl.get("implied_rate") == 22050):
        fails.append("hdr plain not honest")
    if pf["sink_gone"] is not True:
        fails.append("teardown")
    return fails


GATES = {
    "playback_target_lattice_r78_probe": gate_lattice,
    "playback_default_follow_r78_probe": gate_follow,
    "playback_target_loss_r78_probe": gate_loss,
    "playback_props_r78_probe": gate_props,
    "playback_class_segv_r78_probe": gate_segv,
    "playback_aplay_axis_r78_probe": gate_aplay,
    "capture_unlinked_zeros_r78_probe": gate_zeros,
    "capture_parec_fix_r78_probe": gate_parec,
}

print("=== REPLAY (unmutated) ===")
for k, g in GATES.items():
    f = g(copy.deepcopy(E[k]))
    print(f"{k}: replayed failures={f}")

print("\n=== MUTATIONS ===")


def mut(entry, fn):
    e = copy.deepcopy(entry)
    fn(e)
    return e


# M1: fallback leg with dead tap (tap file missing)
lat = E["playback_target_lattice_r78_probe"]
def m1(e):
    e["legs"]["garbage"]["tap"] = {"exists": False, "bytes": 0,
                                   "windows": [], "mine_spans": []}
    e["legs"]["garbage"]["carries_tone"] = \
        e["legs"]["garbage"]["tap"].get("carries_tone")
f = gate_lattice(mut(lat, m1))
print("M1 fallback leg, tap file missing ->", f or "STILL PASSES?!",
      "=> caught" if f else "FORGED")

# M2: target_0 stall leg, tap never ran -> negative pin vacuous
def m2(e):
    e["legs"]["target_0"]["tap"] = {"exists": False, "bytes": 0,
                                    "windows": [], "mine_spans": []}
f = gate_lattice(mut(lat, m2))
print("M2 target_0 leg, tap dead (no windows) ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED (negative pin vacuous)")

# M3: monitor_name lands ONLY the source peer -> content check skipped
def m3(e):
    peer = (e.get("source_peer") or {}).get("peer_sink")
    e["legs"]["monitor_name"]["consumers_union"] = [peer]
    for s in e["legs"]["monitor_name"]["samples"]:
        s["nodes"] = [peer]
    e["legs"]["monitor_name"]["carries_tone"] = None
f = gate_lattice(mut(lat, m3))
print("M3 monitor_name peer-only, no tap on peer ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED (content pin skipped)")

# M4: capture zeros legs absent entirely
z = E["capture_unlinked_zeros_r78_probe"]
def m4(e):
    e["legs"]["consumer_unlink"] = {}
    e["legs"]["producer_unlink"] = {}
f = gate_zeros(mut(z, m4))
print("M4 zeros legs empty dicts ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED (absent leg is silent)")

# M5: arecord_constrain refuses via BUSY (not sample-format) + honored dead
ap = E["playback_aplay_axis_r78_probe"]
def m5(e):
    e["legs"]["arecord_constrain"]["exit_code"] = 1
    e["legs"]["arecord_constrain"]["error_class"] = "alsa_busy"
    e["legs"]["arecord_honored"]["exit_code"] = 1
f = gate_aplay(mut(ap, m5))
print("M5 arecord pair under lingering lock ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED (constrain class unasserted)")

# M6: segv boundary_source publishes NOTHING (no ports)
sv = E["playback_class_segv_r78_probe"]
def m6(e):
    for s in e["legs"]["boundary_source"]["samples"]:
        s["output_ports"] = []
        s["node"] = {"found": False}
f = gate_segv(mut(sv, m6))
print("M6 boundary_source no ports/node ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED (published-half unasserted)")

# M7: still_probe unlinked through the transition
fl = E["playback_default_follow_r78_probe"]
def m7(e):
    for s in e["legs"]["still_probe"]["samples"]:
        s["nodes"] = []
    e["legs"]["still_probe"]["consumers_union"] = []
f = gate_follow(mut(fl, m7))
print("M7 still_probe unlinked all samples ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED (transitional [] admitted)")

# M8: lattice leg reports 'blocked' -> skipped, no failure
def m8(e):
    e["legs"]["probe_sink"] = {"blocked": "probe-owned null sink did "
                                          "not load"}
f = gate_lattice(mut(lat, m8))
print("M8 probe_sink leg blocked ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED (blocked leg is silent)")

# M9: lattice leg fed want + one FOREIGN node -> confound not failure
def m9(e):
    leg = e["legs"]["garbage"]
    leg["consumers_union"] = ["alsa_output.usb-Generic_USB_Audio-00."
                              "HiFi__SPDIF__sink", "foreign_node_X"]
    for s in leg["samples"]:
        s["nodes"] = leg["consumers_union"]
f = gate_lattice(mut(lat, m9))
print("M9 fallback leg consumers=[want,foreign] ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED (foreign-extra -> confound)")

# M10: fallback leg lands on a DIFFERENT real sink (routed != pactl default)
def m10(e):
    leg = e["legs"]["garbage"]
    leg["consumers_union"] = ["alsa_output.pci-0000_01_00.1.hdmi-stereo"]
    for s in leg["samples"]:
        s["nodes"] = leg["consumers_union"]
    leg["carries_tone"] = True  # tap followed content (migration)
f = gate_lattice(mut(lat, m10))
print("M10 fallback routed to other real sink ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED")

# M11: nofollow leg — stream moved to a THIRD node
def m11(e):
    nf = e["legs"]["nofollow"]
    nf["samples"][1]["nodes"] = ["alsa_output.pci-0000_01_00.1.hdmi-stereo"]
f = gate_follow(mut(fl, m11))
print("M11 nofollow post -> third node ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED")

# M12: segv leg exits 0 but consumed nothing (soft wrong outcome)
def m12(e):
    e["legs"]["segv_sink"]["exit_code"] = 0
f = gate_segv(mut(sv, m12))
print("M12 segv_sink rc=0 ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED")

# M13: zeros producer leg — post-unlink windows carry audio (wrong outcome)
def m13(e):
    fw = e["legs"]["producer_unlink"]["file_windows"]
    for w in fw["windows"]:
        if w["at_s"] > 2.2:
            w["audio"] = True
f = gate_zeros(mut(z, m13))
print("M13 producer_unlink post-gap audio ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED")

# M14: parec hdr leg payload honored the request (no mismatch) -> must fail
pf = E["capture_parec_fix_r78_probe"]
def m14(e):
    e["legs"]["hdr_rate_fix"]["implied_rate"] = 22050
f = gate_parec(mut(pf, m14))
print("M14 hdr_rate_fix payload==request ->", f or "STILL PASSES",
      "=> caught" if f else "FORGED")
