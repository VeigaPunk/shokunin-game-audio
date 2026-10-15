#!/usr/bin/env python3
"""r83 boundary stages — attack the r83 scout pins under varied host state."""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r83b_probe as P  # noqa: E402

PICK = ["media.name", "bogus.prop", "audio.channels", "audio.position",
        "channelmap.map", "resample.quality", "resample.disable",
        "resample.peaks", "resample.prefill", "node.latency",
        "node.force-latency", "node.passive", "node.dont-move",
        "node.dont-remix", "stream.dont-remix", "channelmix.disabled",
        "channelmix.stereo-widen", "channelmix.upmix", "node.name",
        "node.group", "node.link-group", "target.object", "stream.is-live",
        "node.autoconnect", "media.class"]

LB = P.LB_BASE


def hdr(stage):
    return {"stage": stage, "start": time.strftime("%H:%M:%S"),
            "load": os.getloadavg(), "legs": []}


# ---------------------------------------------------------------- setup

def stage_setup():
    r = hdr("setup")
    r["host"] = P.host_snapshot()
    r["git"] = P.sh(["git", "rev-parse", "--short", "HEAD"],
                    timeout=10.0)["out"].strip()
    r["tools"] = {}
    for tool, cmd in (("pw-loopback", ["pw-loopback", "--version"]),
                      ("pactl", ["pactl", "--version"]),
                      ("pw-cat", ["pw-cat", "--version"]),
                      ("pw-record", ["pw-record", "--version"]),
                      ("pw-mididump", ["pw-mididump", "--version"]),
                      ("pw-midiplay", ["pw-midiplay", "--version"]),
                      ("pipewire", ["pipewire", "--version"])):
        rr = P.sh(cmd, timeout=10.0)
        r["tools"][tool] = (rr["out"] or rr["err"]).strip().splitlines()[:2]
    r["core_pattern"] = P.sh(["cat", "/proc/sys/kernel/core_pattern"],
                             timeout=5.0)["out"].strip()
    r["pre_r83b"] = [s for s in
                     P.sh(["pactl", "list", "short", "sinks"],
                          timeout=10.0)["out"].splitlines() if "r83b" in s]
    r["sinks"] = [P.ns_load(P.NS_A), P.ns_load(P.NS_B),
                  P.ns_load(P.NS_M, ["channel_map=mono"]),
                  P.ns_load(P.NS_48), P.ns_load(P.NS_44, ["rate=44100"])]
    r["tones"] = {k: os.path.basename(v)
                  for k, v in P.ensure_tones().items()}
    r["midi"] = P.midi_file()
    r["post_sinks"] = [ln for ln in
                       P.sh(["pactl", "list", "short", "sinks"],
                            timeout=10.0)["out"].splitlines()
                       if "r83b" in ln]
    P.save_receipt("setup.json", r)
    return r


# ---------------------------------------------------------------- s1 args

def _lb_props_leg(stage, leg, extra, timeout_s=8):
    name = f"r83b_s1_{leg}"
    rec = P.lb_leg(stage, leg, name, LB + list(extra),
                   sample_props=PICK, timeout_s=timeout_s)
    return rec


def _segv_leg(stage, leg, args, direct=False, timeout_s=6):
    d = P.leg_dir(stage, leg)
    rec = {"leg": leg, "args": list(args), "direct": direct,
           "load_before": os.getloadavg()}
    with open(os.path.join(d, "cmd.txt"), "w") as fh:
        fh.write(" ".join(["pw-loopback"] + [str(a) for a in args]))
    if direct:
        p = P.spawn(["pw-loopback"] + list(args))
    else:
        p = P.spawn(["timeout", "-s", "KILL", str(timeout_s), "pw-loopback"]
                    + list(args))
    rr = P.reap(p, wait=timeout_s + 2)
    rec["rc"], rec["stderr"] = rr["rc"], rr["err"]
    rec["load_after"] = os.getloadavg()
    with open(os.path.join(d, "stderr.txt"), "w") as fh:
        fh.write(rr["err"])
    P.save_leg(stage, leg, rec)
    return rec


def stage_s1_args():
    stage = "s1_args"
    r = hdr(stage)
    # --- syntax forms (replay verbatim) ---
    r["legs"].append(_lb_props_leg(stage, "A0_base", []))
    r["legs"].append(_lb_props_leg(
        stage, "A1_space", ["-i", "media.name=SPACEV bogus.prop=42"]))
    r["legs"].append(_lb_props_leg(
        stage, "A2_brace", ["-i", "{ media.name = BRACEV bogus.prop = 42 }"]))
    r["legs"].append(_lb_props_leg(
        stage, "A3_braceq",
        ["-i", '{ "media.name" = "BRACEQ" "bogus.prop" = "42" }']))
    r["legs"].append(_lb_props_leg(
        stage, "A4_colon", ["-i", '{ "media.name": "COLONV" }']))
    r["legs"].append(_lb_props_leg(
        stage, "A5_comma", ["-i", "media.name=COMMAV,bogus.prop=42"]))
    # --- malformed forms ---
    r["legs"].append(_lb_props_leg(stage, "A6_malformed", ["-i", "}{ garbage"]))
    for i, val in enumerate(["a=b }{ c=d", "{ bad", "[1,2", "media.name=",
                             "{ }", "null", '"str"', "a=b,", "}{"]):
        r["legs"].append(_lb_props_leg(
            stage, f"A6x_mal{i}", ["-i", val], timeout_s=5))
    # --- empty props: segv class ---
    for i in range(3):
        r["legs"].append(_segv_leg(stage, f"A7_empty_i_t{i}", ["-i", ""]))
    for i in range(3):
        r["legs"].append(_segv_leg(stage, f"A7_empty_o_t{i}",
                                   ["-C", P.NS_A, "-P", P.NS_B, "-o", ""]))
    r["legs"].append(_segv_leg(stage, "A7_empty_i_direct", ["-i", ""],
                               direct=True))
    r["legs"].append(_segv_leg(stage, "A7_empty_o_direct",
                               ["-C", P.NS_A, "-P", P.NS_B, "-o", ""],
                               direct=True))
    # empty single-space / empty -n / -C '' / -P '' (unstated modes)
    r["legs"].append(_segv_leg(stage, "A7x_space_i", ["-i", " "]))
    r["legs"].append(_segv_leg(stage, "A7x_n_empty",
                               ["-n", "", "-C", P.NS_A, "-P", P.NS_B]))
    r["legs"].append(_segv_leg(stage, "A7x_C_empty",
                               ["-C", "", "-P", P.NS_B, "-i",
                                "stream.capture.sink=true"]))
    r["legs"].append(_segv_leg(stage, "A7x_P_empty",
                               ["-C", P.NS_A, "-i", "stream.capture.sink=true",
                                "-P", ""]))
    # --- under load ---
    n = P.hogs_start(16)
    r["hogs"] = n
    r["load_hogs"] = os.getloadavg()
    for i in range(3):
        r["legs"].append(_segv_leg(stage, f"A8_empty_i_ld_t{i}", ["-i", ""]))
    r["legs"].append(_lb_props_leg(stage, "A8_malformed_ld",
                                   ["-i", "}{ garbage"], timeout_s=5))
    r["legs"].append(_lb_props_leg(stage, "A8_space_ld",
                                   ["-i", "media.name=SPACEV bogus.prop=42"]))
    P.hogs_stop()
    r["load_after_hogs"] = os.getloadavg()
    P.save_receipt("s1-args.json", r)
    return r


# ---------------------------------------------------------------- s2 channel

def stage_s2_channel():
    stage = "s2_channel"
    r = hdr(stage)
    r["legs"].append(P.lb_content_leg(
        stage, "C0_base", "r83b_s2_C0", LB, P.SCRATCH + "/tone48.wav",
        P.NS_A, P.NS_B, sample_props=PICK))
    r["legs"].append(P.lb_content_leg(
        stage, "C1_pos_i", "r83b_s2_C1",
        LB + ["-i", "audio.position=[ MONO ]"], P.SCRATCH + "/tone48.wav",
        P.NS_A, P.NS_B, sample_props=PICK))
    r["legs"].append(P.lb_content_leg(
        stage, "C2_pos_both", "r83b_s2_C2",
        LB + ["-i", "audio.position=[ MONO ]", "-o", "audio.position=[ MONO ]"],
        P.SCRATCH + "/tone48.wav", P.NS_A, P.NS_B, sample_props=PICK))
    r["legs"].append(P.lb_content_leg(
        stage, "C3_flag_m", "r83b_s2_C3", LB + ["-m", "[ MONO ]"],
        P.SCRATCH + "/tone48.wav", P.NS_A, P.NS_B, sample_props=PICK))
    r["legs"].append(P.lb_content_leg(
        stage, "C4_flag_c1", "r83b_s2_C4",
        LB + ["-c", "1", "-m", "[ MONO ]"], P.SCRATCH + "/tone48.wav",
        P.NS_A, P.NS_B, sample_props=PICK))
    r["legs"].append(P.lb_content_leg(
        stage, "C5_channelmap", "r83b_s2_C5",
        LB + ["-i", "channelmap.map=[ MONO ]"], P.SCRATCH + "/tone48.wav",
        P.NS_A, P.NS_B, sample_props=PICK))
    r["legs"].append(P.lb_content_leg(
        stage, "C6_ch1_prop", "r83b_s2_C6",
        LB + ["-i", "audio.channels=1 audio.position=[ MONO ]"],
        P.SCRATCH + "/tone48.wav", P.NS_A, P.NS_B, sample_props=PICK))
    P.save_receipt("s2-channel.json", r)
    return r


# ---------------------------------------------------------------- s3 remix

def stage_s3_remix():
    stage = "s3_remix"
    r = hdr(stage)
    T48 = P.SCRATCH + "/tone48.wav"
    MONO = P.SCRATCH + "/mono48.wav"
    props = [("M0", []), ("M1", ["node.dont-remix=true"]),
             ("M2", ["stream.dont-remix=true"]),
             ("M3", ["channelmix.upmix=false"]),
             ("M4", ["channelmix.disabled=true"])]
    for tag, pr in props:
        r["legs"].append(P.pc_leg(
            stage, f"{tag}_mono2stereo", f"r83b_s3_{tag}", MONO, P.NS_B,
            props=pr, mon_sink=P.NS_B))
    for tag, pr in [("W0", []), ("W1", ["channelmix.stereo-widen=1.0"]),
                    ("W2", ["channelmix.stereo-widen=0.5"]),
                    ("W3", ["node.dont-remix=true"]),
                    ("W4", ["channelmix.upmix-method=simple"])]:
        r["legs"].append(P.pc_leg(
            stage, f"{tag}_stereo", f"r83b_s3_{tag}", T48, P.NS_B,
            props=pr, mon_sink=P.NS_B))
    for tag, pr in [("D0", []), ("D1", ["channelmix.downmix=false"]),
                    ("D2", ["node.dont-remix=true"]),
                    ("D3", ["stream.dont-remix=true"])]:
        r["legs"].append(P.pc_leg(
            stage, f"{tag}_stereo2mono", f"r83b_s3_{tag}", T48, P.NS_M,
            props=pr, mon_sink=P.NS_M, mon_ch=1))
    # under load rep of the two decisive cells
    n = P.hogs_start(16)
    r["hogs"] = n
    r["load_hogs"] = os.getloadavg()
    r["legs"].append(P.pc_leg(
        stage, "M2_ld", "r83b_s3_M2ld", MONO, P.NS_B,
        props=["stream.dont-remix=true"], mon_sink=P.NS_B))
    r["legs"].append(P.pc_leg(
        stage, "D3_ld", "r83b_s3_D3ld", T48, P.NS_M,
        props=["stream.dont-remix=true"], mon_sink=P.NS_M, mon_ch=1))
    P.hogs_stop()
    r["load_after_hogs"] = os.getloadavg()
    P.save_receipt("s3-remix.json", r)
    return r


# ---------------------------------------------------------------- s4 resample

def stage_s4_resample():
    stage = "s4_resample"
    r = hdr(stage)
    T44 = P.SCRATCH + "/tone44.wav"
    T48 = P.SCRATCH + "/tone48.wav"
    legs = [
        ("S0_44into48", T44, P.NS_48, [], None),
        ("S1_disable", T44, P.NS_48, ["resample.disable=true"], None),
        ("S1b_disable_matched", T48, P.NS_48, ["resample.disable=true"], None),
        ("S1c_disable_false", T44, P.NS_48, ["resample.disable=false"], None),
        ("S4_peaks", T44, P.NS_48, ["resample.peaks=true"], None),
        ("S4b_peaks_matched", T48, P.NS_48, ["resample.peaks=true"], None),
        ("S4c_peaks_down", T48, P.NS_44, ["resample.peaks=true"], None),
        ("S6_48into44", T48, P.NS_44, [], None),
        ("S5_rate_flag", T44, P.NS_48, [], ["--rate", "48000"]),
    ]
    for tag, wav, tgt, pr, extra in legs:
        r["legs"].append(P.pc_leg(
            stage, tag, f"r83b_s4_{tag}", wav, tgt, props=pr,
            mon_sink=tgt, extra=extra))
    # loopback across the rate boundary
    lb_args = ["-C", P.NS_44, "-i", "stream.capture.sink=true", "-P", P.NS_48]
    r["legs"].append(P.lb_content_leg(
        stage, "LB0_def", "r83b_s4_LB0", lb_args, T44, P.NS_44, P.NS_48,
        sample_props=PICK))
    r["legs"].append(P.lb_content_leg(
        stage, "LB1_disable_false", "r83b_s4_LB1",
        ["-C", P.NS_44, "-i", "stream.capture.sink=true",
         "-i", "resample.disable=false", "-P", P.NS_48,
         "-o", "resample.disable=false"], T44, P.NS_44, P.NS_48,
        sample_props=PICK))
    r["legs"].append(P.lb_content_leg(
        stage, "LB2_disable_true", "r83b_s4_LB2",
        ["-C", P.NS_44, "-i", "stream.capture.sink=true",
         "-i", "resample.disable=true", "-P", P.NS_48,
         "-o", "resample.disable=true"], T44, P.NS_44, P.NS_48,
        sample_props=PICK))
    r["legs"].append(P.lb_content_leg(
        stage, "LB3_peaks", "r83b_s4_LB3",
        ["-C", P.NS_44, "-i", "stream.capture.sink=true",
         "-i", "resample.peaks=true", "-P", P.NS_48],
        T44, P.NS_44, P.NS_48, sample_props=PICK))
    # under load: determinism of the two artifacts
    n = P.hogs_start(16)
    r["hogs"] = n
    r["load_hogs"] = os.getloadavg()
    r["legs"].append(P.pc_leg(
        stage, "S1_disable_ld1", "r83b_s4_S1ld1", T44, P.NS_48,
        props=["resample.disable=true"], mon_sink=P.NS_48))
    r["legs"].append(P.pc_leg(
        stage, "S1_disable_ld2", "r83b_s4_S1ld2", T44, P.NS_48,
        props=["resample.disable=true"], mon_sink=P.NS_48))
    r["legs"].append(P.pc_leg(
        stage, "S4_peaks_ld1", "r83b_s4_S4ld1", T44, P.NS_48,
        props=["resample.peaks=true"], mon_sink=P.NS_48))
    r["legs"].append(P.pc_leg(
        stage, "S4_peaks_ld2", "r83b_s4_S4ld2", T44, P.NS_48,
        props=["resample.peaks=true"], mon_sink=P.NS_48))
    P.hogs_stop()
    r["load_after_hogs"] = os.getloadavg()
    P.save_receipt("s4-resample.json", r)
    return r


# ---------------------------------------------------------------- s5 latency

def stage_s5_latency():
    stage = "s5_latency"
    r = hdr(stage)
    pick = PICK + ["node.link-group"]
    legs = [("L5", ["-l", "5"]), ("L25", ["-l", "2.5"]),
            ("L0", ["-l", "0"]), ("Labc", ["-l", "abc"]),
            ("L10k", ["-l", "10000"]), ("Lneg", ["-l", "-5"]),
            ("D025", ["-d", "0.25"]), ("D1", ["-d", "1.0"]),
            ("Dneg", ["-d", "-1"]), ("Dabc", ["-d", "abc"]),
            ("D0", ["-d", "0"]),
            ("LD", ["-l", "5", "-d", "0.25"]),
            ("DL", ["-d", "0.25", "-l", "5"]),
            ("Lgrp", ["-g", "r83b_grp"])]
    for tag, extra in legs:
        r["legs"].append(P.lb_leg(
            stage, tag, f"r83b_s5_{tag}", LB + extra, sample_props=pick))
    # onset legs: loopback up first, recorder + tone, compare control vs -d 1.0
    for tag, extra in [("O0_ctrl", []), ("O1_d1", ["-d", "1.0"]),
                       ("O2_ctrl_r2", []), ("O3_d1_r2", ["-d", "1.0"])]:
        r["legs"].append(P.lb_content_leg(
            stage, tag, f"r83b_s5_{tag}", LB + extra,
            P.SCRATCH + "/tone48.wav", P.NS_A, P.NS_B, secs=5))
    n = P.hogs_start(16)
    r["hogs"] = n
    r["load_hogs"] = os.getloadavg()
    for tag, extra in [("O4_ctrl_ld", []), ("O5_d1_ld", ["-d", "1.0"])]:
        r["legs"].append(P.lb_content_leg(
            stage, tag, f"r83b_s5_{tag}", LB + extra,
            P.SCRATCH + "/tone48.wav", P.NS_A, P.NS_B, secs=5))
    P.hogs_stop()
    r["load_after_hogs"] = os.getloadavg()
    P.save_receipt("s5-latency.json", r)
    return r


# ---------------------------------------------------------------- s6 midi

def stage_s6_midi():
    stage = "s6_midi"
    r = hdr(stage)
    mid = P.midi_file()

    def md_leg(tag, argv, timeout_s=8):
        d = P.leg_dir(stage, tag)
        with open(os.path.join(d, "cmd.txt"), "w") as fh:
            fh.write(" ".join(str(a) for a in argv))
        p = P.spawn(["timeout", "-s", "KILL", str(timeout_s)] + argv)
        rr = P.reap(p, wait=timeout_s + 2)
        rec = {"leg": tag, "argv": argv, "rc": rr["rc"],
               "stderr": rr["err"][:2000], "load_before": os.getloadavg()}
        with open(os.path.join(d, "stderr.txt"), "w") as fh:
            fh.write(rr["err"])
        P.save_leg(stage, tag, rec)
        return rec

    # file mode
    rec = md_leg("m1_file", ["pw-mididump", mid])
    r["legs"].append(rec)
    r["legs"].append(md_leg("m2_missing", ["pw-mididump", "/tmp/r83b_no.mid"]))
    # bare live sink: node shape, zero links
    d = P.leg_dir(stage, "m3_live")
    p = P.spawn(["timeout", "-s", "KILL", "6", "pw-mididump"])
    time.sleep(1.2)
    g = P.Graph(P.pw_dump())
    nodes = g.nodes_matching("midi-dump")
    rec = {"leg": "m3_live", "nodes": nodes, "load_before": os.getloadavg()}
    if nodes:
        rec["props"] = {n: {k: (g.node(n) or {}).get(k) for k in
                            ("media.type", "media.category", "media.role",
                             "media.class", "node.name", "node.want-driver",
                             "node.autoconnect")} for n in nodes}
        rec["edges"] = g.edges("midi-dump")
    rr = P.reap(p, 8)
    rec["rc"], rec["stderr"] = rr["rc"], rr["err"][:800]
    with open(os.path.join(d, "stderr.txt"), "w") as fh:
        fh.write(rr["err"])
    P.save_leg(stage, "m3_live", rec)
    r["legs"].append(rec)
    # playback: auto + name + serial-0
    r["legs"].append(md_leg("m4_play_auto", ["pw-midiplay", mid]))
    r["legs"].append(md_leg("m5_play_name",
                            ["pw-midiplay", "--target", "Midi-Bridge", mid]))
    r["legs"].append(md_leg("m6_play_bogus",
                            ["pw-midiplay", "--target", "no_such_midi_r83b",
                             mid]))
    d = P.leg_dir(stage, "m7_play_serial0")
    p = P.spawn(["timeout", "-s", "KILL", "6", "pw-midiplay", "--target", "0",
                 "-P", "node.name=r83b_mplay", mid])
    time.sleep(1.2)
    g = P.Graph(P.pw_dump())
    nodes = g.nodes_matching("r83b_mplay")
    rec = {"leg": "m7_play_serial0", "nodes": nodes,
           "load_before": os.getloadavg()}
    if nodes:
        rec["props"] = {n: {k: (g.node(n) or {}).get(k) for k in
                            ("media.class", "media.type", "node.name",
                             "stream.is-live")} for n in nodes}
        rec["edges"] = g.edges("r83b_mplay")
    rr = P.reap(p, 8)
    rec["rc"], rec["stderr"] = rr["rc"], rr["err"][:500]
    P.save_leg(stage, "m7_play_serial0", rec)
    r["legs"].append(rec)
    r["legs"].append(md_leg("m8_play_missing",
                            ["pw-midiplay", "--target", "0",
                             "/tmp/r83b_no.mid"]))
    P.save_receipt("s6-midi.json", r)
    return r


# ---------------------------------------------------------------- s7 filter

def stage_s7_filter():
    stage = "s7_filter"
    r = hdr(stage)
    r["which"] = P.sh(["which", "pw-filter"], timeout=10.0)
    r["pkg_pipewire_audio"] = P.sh(
        ["bash", "-c", "pacman -Ql pipewire-audio | grep bin/ || true"],
        timeout=15.0)
    r["pkg_pipewire"] = P.sh(
        ["bash", "-c", "pacman -Ql pipewire | grep bin/ || true"],
        timeout=15.0)
    r["man"] = P.sh(["man", "-w", "pw-filter"], timeout=10.0)
    r["find"] = P.sh(["bash", "-c",
                      "find /usr -name 'pw-filter*' 2>/dev/null | head -5"],
                     timeout=20.0)
    r["filter_graph_dir"] = P.sh(
        ["bash", "-c", "ls /usr/lib/spa-0.2/filter-graph/ 2>/dev/null"],
        timeout=10.0)
    r["filter_man"] = P.sh(["man", "-w", "libpipewire-module-filter-chain"],
                           timeout=10.0)
    r["pw_cli_help"] = P.sh(["bash", "-c", "pw-cli help 2>&1 | head -40"],
                            timeout=15.0)
    r["pw_cli_modules"] = P.sh(
        ["bash", "-c", "pw-cli ls Module 2>&1 | grep -c 'id ' || true"],
        timeout=15.0)
    P.save_receipt("s7-filter.json", r)
    return r


# ---------------------------------------------------------------- s8 serial

def stage_s8_serial():
    stage = "s8_serial"
    r = hdr(stage)
    g = P.Graph(P.pw_dump())
    serials = {}
    for nm in (P.NS_A, P.NS_B):
        node = g.node(nm) or {}
        serials[nm] = node.get("object.serial")
    r["serials"] = serials
    if serials.get(P.NS_A) and serials.get(P.NS_B):
        rec = P.lb_leg(stage, "serial_targets", "r83b_s8_ser",
                       ["-C", str(serials[P.NS_A]),
                        "-i", "stream.capture.sink=true",
                        "-P", str(serials[P.NS_B])],
                       sample_props=PICK + ["object.serial"])
        r["legs"].append(rec)
    P.save_receipt("s8-serial.json", r)
    return r


# ---------------------------------------------------------------- s9 misc

def stage_s9_misc():
    stage = "s9_misc"
    r = hdr(stage)
    # pw-cat / pw-record with empty -P props (does the empty-props segv generalize?)
    for tag, argv in [
        ("pcat_emptyP", ["timeout", "-s", "KILL", "5", "pw-cat", "-p", "-P", "",
                         "--target", P.NS_B, P.SCRATCH + "/tone48.wav"]),
        ("prec_emptyP", ["timeout", "-s", "KILL", "5", "pw-record", "-P", "",
                         "--target", P.NS_B, "-n", "4800",
                         "/tmp/r83b_emptyP.wav"]),
    ]:
        d = P.leg_dir(stage, tag)
        with open(os.path.join(d, "cmd.txt"), "w") as fh:
            fh.write(" ".join(argv))
        p = P.spawn(argv)
        rr = P.reap(p, 8)
        rec = {"leg": tag, "argv": argv, "rc": rr["rc"],
               "stderr": rr["err"][:800], "load_before": os.getloadavg()}
        with open(os.path.join(d, "stderr.txt"), "w") as fh:
            fh.write(rr["err"])
        P.save_leg(stage, tag, rec)
        r["legs"].append(rec)
    # stream.dont-remix on the loopback (unstated in scout)
    r["legs"].append(P.lb_content_leg(
        stage, "LB_streamremix", "r83b_s9_LBsr",
        LB + ["-i", "stream.dont-remix=true"],
        P.SCRATCH + "/tone48.wav", P.NS_A, P.NS_B, sample_props=PICK))
    r["legs"].append(P.lb_content_leg(
        stage, "LB_node_remix", "r83b_s9_LBnr",
        LB + ["-i", "node.dont-remix=true"],
        P.SCRATCH + "/tone48.wav", P.NS_A, P.NS_B, sample_props=PICK))
    # node.dont-move replay: pw-cat stream, move to NS_M
    d = P.leg_dir(stage, "dontmove")
    rec = {"leg": "dontmove", "load_before": os.getloadavg()}
    play = P.spawn(["timeout", "-s", "KILL", "8", "pw-cat", "-p",
                    "-P", "node.name=r83b_s9_move",
                    "-P", "node.dont-move=true", "--target", P.NS_B,
                    P.SCRATCH + "/tone48.wav"])
    try:
        time.sleep(1.0)
        g = P.Graph(P.pw_dump())
        rec["edges_before"] = g.edges("r83b_s9_move")
        rows = P.sh(["pactl", "list", "short", "sink-inputs"],
                    timeout=10.0)["out"].splitlines()
        idx = None
        for ln in rows:
            if "r83b_s9_move" in ln:
                idx = ln.split("\t")[0]
        rec["sink_input_idx"] = idx
        if idx:
            mv = P.sh(["pactl", "move-sink-input", idx, P.NS_M], timeout=10.0)
            rec["move_rc"] = mv["rc"]
            rec["move_err"] = mv["err"].strip()
            time.sleep(0.8)
            g = P.Graph(P.pw_dump())
            rec["edges_after"] = g.edges("r83b_s9_move")
    finally:
        rr = P.reap(play, 10)
        rec["rc"], rec["stderr"] = rr["rc"], rr["err"][:500]
    P.save_leg(stage, "dontmove", rec)
    r["legs"].append(rec)
    # control move without dont-move (expect re-negotiated to mono)
    d = P.leg_dir(stage, "move_ctrl")
    rec = {"leg": "move_ctrl", "load_before": os.getloadavg()}
    play = P.spawn(["timeout", "-s", "KILL", "8", "pw-cat", "-p",
                    "-P", "node.name=r83b_s9_movec", "--target", P.NS_B,
                    P.SCRATCH + "/tone48.wav"])
    try:
        time.sleep(1.0)
        g = P.Graph(P.pw_dump())
        rec["edges_before"] = g.edges("r83b_s9_movec")
        rows = P.sh(["pactl", "list", "short", "sink-inputs"],
                    timeout=10.0)["out"].splitlines()
        idx = None
        for ln in rows:
            if "r83b_s9_movec" in ln:
                idx = ln.split("\t")[0]
        rec["sink_input_idx"] = idx
        if idx:
            mv = P.sh(["pactl", "move-sink-input", idx, P.NS_M], timeout=10.0)
            rec["move_rc"] = mv["rc"]
            rec["move_err"] = mv["err"].strip()
            time.sleep(0.8)
            g = P.Graph(P.pw_dump())
            rec["edges_after"] = g.edges("r83b_s9_movec")
    finally:
        rr = P.reap(play, 10)
        rec["rc"], rec["stderr"] = rr["rc"], rr["err"][:500]
    P.save_leg(stage, "move_ctrl", rec)
    r["legs"].append(rec)
    P.save_receipt("s9-misc.json", r)
    return r


# ---------------------------------------------------------------- teardown

def stage_teardown():
    stage = "teardown"
    r = hdr(stage)
    P.hogs_stop()
    P.kill_all()
    r["unloads"] = [P.ns_unload(n) for n in
                    (P.NS_A, P.NS_B, P.NS_M, P.NS_48, P.NS_44)]
    time.sleep(0.5)
    r["leftover_sinks"] = [ln for ln in
                           P.sh(["pactl", "list", "short", "sinks"],
                                timeout=10.0)["out"].splitlines()
                           if "r83b" in ln]
    r["leftover_sources"] = [ln for ln in
                             P.sh(["pactl", "list", "short", "sources"],
                                  timeout=10.0)["out"].splitlines()
                             if "r83b" in ln]
    r["leftover_modules"] = [ln for ln in
                             P.sh(["pactl", "list", "short", "modules"],
                                  timeout=10.0)["out"].splitlines()
                             if "r83b" in ln]
    r["leftover_procs"] = P.sh(
        ["bash", "-c", "ps -eo pid,args | grep -E 'r83b' | grep -v grep "
                       "| grep -v r83b_probe | head -20 || true"],
        timeout=10.0)["out"].strip().splitlines()
    r["defaults"] = P.check_defaults()
    r["host_after"] = P.host_snapshot()
    P.save_receipt("teardown.json", r)
    return r


STAGES = {"setup": stage_setup, "s1_args": stage_s1_args,
          "s2_channel": stage_s2_channel, "s3_remix": stage_s3_remix,
          "s4_resample": stage_s4_resample, "s5_latency": stage_s5_latency,
          "s6_midi": stage_s6_midi, "s7_filter": stage_s7_filter,
          "s8_serial": stage_s8_serial, "s9_misc": stage_s9_misc,
          "teardown": stage_teardown}


def main():
    which = sys.argv[1:] or list(STAGES)
    for name in which:
        fn = STAGES.get(name)
        if not fn:
            print(f"unknown stage {name}", file=sys.stderr)
            continue
        print(f"== {name} {P.now()} load={os.getloadavg()} ==", flush=True)
        t0 = time.monotonic()
        try:
            res = fn()
            print(f"   done {name} in {round(time.monotonic() - t0, 1)}s",
                  flush=True)
        except Exception as exc:
            print(f"   STAGE {name} EXC {exc!r}", flush=True)
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
