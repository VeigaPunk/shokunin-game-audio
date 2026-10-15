#!/usr/bin/env python3
"""r87b boundary probe — falsify the r87 scout claims (verbatim replays,
host-state variation, hog load, unstated-mode hunting).

Stages: quiet | load | host | cleanup | all
Every audio object is r87b_*. Receipts under corpus/live/r87-boundary/.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r87b_lib import (  # noqa: E402
    TAG, NS, NS2, TONE, SMF, RUNS, GEN, RECEIPTS, RATE, OWN_PROCS,
    sh, norm, pw_dump, props_of, nodes_by_name, node_info, all_node_names,
    port_inventory, links_for, link_pairs, spawn, stop, pw_cli, pwcli_split,
    pwcli_errors, parse_props_volume, parse_format, load_own_sink,
    unload_own_sink, own_module_idx, mod_lines, gen_tone, gen_smf,
    wav_window_rms, rms_ratio, hog_start, hog_stop, loadavg,
    contention_snapshot, play_leg, nowarm_info, proc_snapshot)


def save(name, obj):
    p = RECEIPTS / name
    p.write_text(json.dumps(obj, indent=1, default=str))
    return str(p)


def ensure_sinks():
    d = pw_dump()
    for nm in (NS, NS2):
        if not [o for o in nodes_by_name(nm, d)
                if props_of(o).get("media.class") == "Audio/Sink"]:
            load_own_sink(nm)
            time.sleep(0.4)
    d = pw_dump()
    out = {}
    for nm in (NS, NS2):
        nds = [o for o in nodes_by_name(nm, d)
               if props_of(o).get("media.class") == "Audio/Sink"]
        if nds:
            p = props_of(nds[0])
            out[nm] = {"id": nds[0]["id"], "serial": p.get("object.serial"),
                       "module_idx": own_module_idx(nm)}
    return out


# ---------------- B1: target lattice ----------------

def b1_lattice(sinks):
    res = {"sinks": sinks, "default_sink": sh(["pactl", "get-default-sink"])["out"].strip()}
    d = pw_dump()
    ns_id = sinks[NS]["id"]
    ns_ser = str(sinks[NS]["serial"])
    ns2_id = sinks[NS2]["id"]
    ns2_ser = str(sinks[NS2]["serial"])
    src = [o for o in all_node_names(d)
           if o["class"] == "Audio/Source" and "Line" in str(o["name"])]
    hdmi = [o for o in all_node_names(d)
            if o["class"] == "Audio/Sink" and "hdmi" in str(o["name"])]
    res["refs"] = {"ns_id": ns_id, "ns_serial": ns_ser,
                   "ns2_id": ns2_id, "ns2_serial": ns2_ser,
                   "src": src[0] if src else None,
                   "hdmi": hdmi[0] if hdmi else None,
                   "scout_stale_serial": 41546}
    legs = [
        ("p_own", ["pw-play", "-P", f"node.name={TAG}p_own",
                   "--target", NS, str(TONE)], None),
        ("p_cat_flag", ["pw-cat", "--playback", "-P", f"node.name={TAG}p_catflag",
                        "--target", NS, str(TONE)], None),
        ("p_cat_noflag", ["pw-cat", "-P", f"node.name={TAG}p_catnf",
                          "--target", NS, str(TONE)], None),
        ("p_garbage", ["pw-play", "-P", f"node.name={TAG}p_garb",
                       "--target", "r87b_no_such_target", str(TONE)], None),
        ("p_pb1", ["pw-play", "-P", f"node.name={TAG}p_pb1",
                   "-P", "target.object=r87b_no_such_target",
                   "--target", NS, str(TONE)], None),
        ("p_pb2", ["pw-play", "-P", f"node.name={TAG}p_pb2",
                   "-P", f"target.object={NS}",
                   "--target", "r87b_no_such_target", str(TONE)], None),
        ("p_pb3", ["pw-play", "-P", f"node.name={TAG}p_pb3",
                   "-P", f"target.object={NS2}",
                   "--target", NS, str(TONE)], None),
        ("p_nt", ["pw-play", "-P", f"node.name={TAG}p_nt",
                  "-P", f"node.target={NS}", str(TONE)], None),
        ("p_zero", ["pw-play", "-P", f"node.name={TAG}p_zero",
                    "--target", "0", str(TONE)], None),
        ("p_mon", ["pw-play", "-P", f"node.name={TAG}p_mon",
                   "--target", NS + ".monitor", str(TONE)], None),
        ("p_mon_capsink", ["pw-play", "-P", f"node.name={TAG}p_moncs",
                           "-P", "stream.capture.sink=true",
                           "--target", NS + ".monitor", str(TONE)], None),
        ("p_src_name", ["pw-play", "-P", f"node.name={TAG}p_src",
                        "--target", str(src[0]["name"]) if src else "n/a",
                        str(TONE)], None),
        ("p_src_serial", ["pw-play", "-P", f"node.name={TAG}p_srcser",
                          "--target", str(src[0]["serial"]) if src else "n/a",
                          str(TONE)], None),
        ("p_serial", ["pw-play", "-P", f"node.name={TAG}p_ser",
                      "--target", ns_ser, str(TONE)], None),
        ("p_objid", ["pw-play", "-P", f"node.name={TAG}p_oid",
                     "--target", str(ns_id), str(TONE)], None),
        ("p_objid_hdmi", ["pw-play", "-P", f"node.name={TAG}p_oidh",
                          "--target", str(hdmi[0]["id"]) if hdmi else "n/a",
                          str(TONE)], None),
        ("p_serial_stale", ["pw-play", "-P", f"node.name={TAG}p_stale",
                            "--target", "41546", str(TONE)], None),
        ("p_env_props", ["pw-play", "-P", f"node.name={TAG}p_env",
                         "--target", "r87b_no_such_target", str(TONE)],
         {"PIPEWIRE_PROPS": "{ target.object = %s }" % NS}),
        ("p_env_nobrace", ["pw-play", "-P", f"node.name={TAG}p_envnb",
                           "--target", "r87b_no_such_target", str(TONE)],
         {"PIPEWIRE_PROPS": "target.object=%s" % NS}),
        ("p_env_vs_prop", ["pw-play", "-P", f"node.name={TAG}p_envvp",
                           "-P", f"target.object={NS2}",
                           "--target", "r87b_no_such_target", str(TONE)],
         {"PIPEWIRE_PROPS": "{ target.object = %s }" % NS}),
        ("p_prop_serial", ["pw-play", "-P", f"node.name={TAG}p_pser",
                           "-P", f"target.object={ns_ser}", str(TONE)], None),
        ("p_prop_objid", ["pw-play", "-P", f"node.name={TAG}p_poid",
                          "-P", f"target.object={ns_id}", str(TONE)], None),
        ("p_empty", ["pw-play", "-P", f"node.name={TAG}p_empty",
                     "--target", "", str(TONE)], None),
        ("p_mediarole", ["pw-play", "-P", f"node.name={TAG}p_mr",
                         "--media-role", "Communication",
                         "--target", "r87b_no_such_target", str(TONE)], None),
        ("p_capsink_prop", ["pw-play", "-P", f"node.name={TAG}p_cs",
                            "-P", "stream.capture.sink=true",
                            "--target", "r87b_no_such_target", str(TONE)], None),
    ]
    for leg, args, env in legs:
        names = [a.split("=", 1)[1] for a in args if a.startswith("node.name=")]
        nm = names[0] if names else leg
        res[leg] = play_leg(nm, args, env=env)
    # name-collision: a stream node sharing the sink's node.name
    coll = spawn(["pw-play", "-P", f"node.name={NS}", "--target", "0", str(TONE)])
    time.sleep(0.9)
    d = pw_dump()
    coll_objs = [{"id": o["id"], "class": props_of(o).get("media.class")}
                 for o in nodes_by_name(NS, d)]
    coll_leg = play_leg(TAG + "p_coll", ["pw-play", "-P", f"node.name={TAG}p_coll",
                                         "--target", NS, str(TONE)])
    rc_c, err_c = stop(coll)
    res["collision"] = {"objects_while_colliding": coll_objs,
                        "coll_rc": rc_c, "coll_err": norm(err_c)[-200:],
                        "p_coll": coll_leg}
    save("b1-lattice.json", res)
    return res


# ---------------- B2: mode flags + unstated modes ----------------

def b2_modes(sinks):
    res = {"sinks": sinks}
    legs = [
        ("m_capture_long", ["pw-cat", "--capture", str(TONE)]),
        ("m_duplex_long", ["pw-cat", "--duplex", str(TONE)]),
        ("m_noflag", ["pw-cat", "-P", f"node.name={TAG}m_nf",
                      "--target", NS, str(TONE)]),
        ("m_p_then_r", ["pw-cat", "-p", "-r", "-P", f"node.name={TAG}m_pr",
                        "-P", "stream.capture.sink=true",
                        "--target", NS, "-n", str(RATE), str(RUNS / "m_pr.wav")]),
        ("m_r_then_p", ["pw-cat", "-r", "-p", "-P", f"node.name={TAG}m_rp",
                        "--target", NS, str(TONE)]),
        ("m_p_r_p", ["pw-cat", "-p", "-r", "-p", "-P", f"node.name={TAG}m_prp",
                     "--target", NS, str(TONE)]),
        ("m_r_p_r", ["pw-cat", "-r", "-p", "-r", "-P", f"node.name={TAG}m_rpr",
                     "-P", "stream.capture.sink=true",
                     "--target", NS, "-n", str(RATE), str(RUNS / "m_rpr.wav")]),
        ("m_play_argv0_r", ["pw-play", "-r", "-P", f"node.name={TAG}m_playr",
                            "-P", "stream.capture.sink=true",
                            "--target", NS, "-n", str(RATE), str(RUNS / "m_playr.wav")]),
        ("m_record_argv0_p", ["pw-record", "-p", "-P", f"node.name={TAG}m_recp",
                              "--target", NS, str(TONE)]),
        ("m_cat_midi_flag", ["pw-cat", "-m", "-P", f"node.name={TAG}m_midif",
                             str(SMF)]),
        ("m_midi_p", ["pw-cat", "-m", "-p", "-P", f"node.name={TAG}m_mp",
                      "--target", "0", str(SMF)]),
        ("m_midi_r", ["pw-cat", "-m", "-r", "-P", f"node.name={TAG}m_mr",
                      "--target", "0", str(RUNS / "m_mr.mid")]),
        ("m_ump_midi_p", ["pw-cat", "-M", "ump", "-m", "-p",
                          "-P", f"node.name={TAG}m_ump", "--target", "0", str(SMF)]),
        ("m_sysex_p", ["pw-cat", "-s", "-p", "-P", f"node.name={TAG}m_sx",
                       "--target", "0", str(SMF)]),
        ("m_clip_p", ["pw-cat", "-c", "-p", "-P", f"node.name={TAG}m_cl",
                      "--target", "0", str(SMF)]),
    ]
    for leg, args in legs:
        names = [a.split("=", 1)[1] for a in args if a.startswith("node.name=")]
        nm = names[0] if names else leg
        res[leg] = play_leg(nm, args, observe_s=(0.9, 1.4))
    # -d on a wav: capture BOTH streams (scout reported class from stdout)
    d = sh(["pw-cat", "-d", "-p", "-P", f"node.name={TAG}m_d",
            "--target", "0", str(TONE)], timeout=10)
    res["m_dsd"] = {"rc": d["rc"], "out": norm(d["out"])[-400:],
                    "err": norm(d["err"])[-400:]}
    if (RUNS / "m_mr.mid").exists():
        res["m_midi_r_file"] = {"bytes": (RUNS / "m_mr.mid").stat().st_size,
                                "head": (RUNS / "m_mr.mid").read_bytes()[:48].hex()}
    # unstated: --volume at spawn (stream volume 0-1.0), monitor-RMS witness
    res["volume_legs"] = volume_legs()
    save("b2-modes.json", res)
    return res


def volume_legs():
    out = {}
    for tag, vol in (("v100", "1.0"), ("v050", "0.5"), ("v000", "0.0"),
                     ("v150", "1.5")):
        mon = RUNS / f"vol_{tag}.wav"
        rec = spawn(["pw-record", "-P", f"node.name={TAG}volrec_{tag}",
                     "-P", "stream.capture.sink=true", "--target", NS,
                     "-n", str(6 * RATE), str(mon)])
        time.sleep(0.7)
        p = spawn(["pw-play", "-P", f"node.name={TAG}vol_{tag}",
                   "--volume", vol, "--target", NS, str(TONE)])
        time.sleep(2.6)
        rc, err = stop(p)
        stop(rec)
        r = {"volume_arg": vol, "play_rc": rc, "stderr": norm(err)[-200:]}
        if mon.exists() and mon.stat().st_size > 4096:
            r["rms_L_1.2_1.8"] = round(wav_window_rms(mon, 1.2, 1.8, 0) or 0, 2)
            r["rms_R_1.2_1.8"] = round(wav_window_rms(mon, 1.2, 1.8, 1) or 0, 2)
        out[tag] = r
    base = out.get("v100", {}).get("rms_L_1.2_1.8")
    for tag, r in out.items():
        r["ratio_L_vs_v100"] = rms_ratio(r.get("rms_L_1.2_1.8"), base)
    return out


# ---------------- B3: pw-cli ----------------

def mut_leg(label, rec_s=12):
    mon = RUNS / (label + "_mon.wav")
    rec_name = TAG + "mon_" + re.sub(r"\W", "_", label)
    mut_name = TAG + "mut_" + re.sub(r"\W", "_", label)
    rec_t0 = time.time()
    rp = spawn(["pw-record", "-P", f"node.name={rec_name}",
                "-P", "stream.capture.sink=true", "--target", NS,
                "-n", str(rec_s * RATE), str(mon)])
    time.sleep(0.8)
    play_rel = time.time() - rec_t0
    pp = spawn(["pw-play", "-P", f"node.name={mut_name}",
                "--target", NS, str(TONE)])
    time.sleep(1.0)
    d = pw_dump()
    nds = nodes_by_name(mut_name, d)
    sid = nds[0]["id"] if nds else None
    res = {"stream_id": sid, "record": str(mon), "play_rel_s": round(play_rel, 3)}
    if sid is not None:
        cmds = [
            (0.0, f"info {sid}"),
            (0.4, f"enum-params {sid} Props"),
            (0.5, f"set-param {sid} Props {{ volume: 0.25 }}"),
            (0.9, f"enum-params {sid} Props"),
            (0.6, f"set-param {sid} Props {{ volume: 1.0 }}"),
            (0.9, f"set-param {sid} Props {{ mute: true }}"),
            (0.9, f"set-param {sid} Props {{ mute: false }}"),
            (0.7, f"set-param {sid} NoSuchType {{ }}"),
            (0.3, f"set-param {sid} Props {{ no_such_prop: 3 }}"),
            (0.5, f"enum-params {sid} Format"),
            (0.4, f"set-param {sid} Format "
                  "{ mediaType: 1, mediaSubtype: 1, format: 259, "
                  "rate: 96000, channels: 2 }"),
            (0.6, f"enum-params {sid} Format"),
            (0.4, f"set-param {sid} Format {{ }}"),
            (0.5, f"enum-params {sid} Format"),
            (0.3, f"send-command {sid}"),
        ]
        cli_wall = time.time()
        cli = pw_cli(cmds, wait_s=20, label=label)
        cli_rel = cli_wall - rec_t0
        res["cli_rel_s"] = round(cli_rel, 3)
        res["marks"] = cli["marks"]
        res["errors"] = pwcli_errors(cli["log"])
        segs = pwcli_split(cli["log"])
        res["props_echo"] = [{"cmd": c, "volume": parse_props_volume(s)}
                             for c, s in segs if c.startswith("set-param")
                             and "Props" in c]
        res["format_enum"] = [{"cmd": c, "fmt": parse_format(s)}
                              for c, s in segs if c.startswith("enum-params")
                              and "Format" in c]
        res["sendcommand_noargs_errors"] = [
            e for e in pwcli_errors(cli["log"]) if "send-command" in e]
    rc_p, err_p = stop(pp)
    rc_r, err_r = stop(rp)
    res["play_rc"] = rc_p
    res["play_err"] = norm(err_p)[-200:]
    res["record_rc"] = rc_r
    res["record_err"] = norm(err_r)[-200:]
    res["bytes"] = mon.stat().st_size if mon.exists() else 0
    if mon.exists() and mon.stat().st_size > 4096:
        fixed = {"silence_head": (0.1, 0.5), "tone_v1": (2.8, 3.2),
                 "tone_v025": (4.7, 5.3), "tone_restored": (6.0, 6.5),
                 "tone_muted": (7.0, 7.4), "tone_unmuted": (7.9, 8.3),
                 "post_format": (9.7, 10.1)}
        res["windows_fixed_L"] = {k: (round(wav_window_rms(mon, a, b, 0), 2)
                                      if wav_window_rms(mon, a, b, 0) is not None
                                      else None)
                                  for k, (a, b) in fixed.items()}
        # mark-derived windows (robust to pacing drift)
        def win_after(cmd_sub, dur=(0.5, 1.1)):
            for m in res.get("marks", []):
                if cmd_sub in m["cmd"]:
                    t0 = cli_rel + m["t"] + dur[0]
                    t1 = cli_rel + m["t"] + dur[1]
                    v = wav_window_rms(mon, t0, t1, 0)
                    return {"mark_t": m["t"], "win": [round(t0, 2), round(t1, 2)],
                            "rms": round(v, 2) if v is not None else None}
            return None
        res["mark_windows_L"] = {
            "baseline": {"win": [round(play_rel + 0.9, 2), round(play_rel + 1.5, 2)],
                         "rms": round(wav_window_rms(mon, play_rel + 0.9,
                                                     play_rel + 1.5, 0) or 0, 2)},
            "vol025": win_after("volume: 0.25"),
            "restore": win_after("volume: 1.0", (0.45, 0.85)),
            "mute_true": win_after("mute: true", (0.45, 0.85)),
            "mute_false": win_after("mute: false", (0.4, 0.65)),
        }
        base = res["mark_windows_L"]["baseline"]["rms"]
        for k in ("vol025", "restore", "mute_true", "mute_false"):
            w = res["mark_windows_L"].get(k)
            if w:
                w["ratio_vs_baseline"] = rms_ratio(w.get("rms"), base)
    return res


def fmt_sealed_leg(label):
    pp = spawn(["pw-play", "-P", f"node.name={TAG}fmt",
                "--target", NS, str(TONE)])
    time.sleep(1.0)
    d = pw_dump()
    nds = nodes_by_name(TAG + "fmt", d)
    sid = nds[0]["id"] if nds else None
    res = {"stream_id": sid}
    if sid is not None:
        cmds = [(0, f"enum-params {sid} Format"),
                (0.5, f"set-param {sid} Format {{ mediaType: 1, mediaSubtype: 1,"
                      " format: 259, rate: 96000, channels: 2 }"),
                (0.6, f"enum-params {sid} Format"),
                (0.4, f"set-param {sid} Format {{ }}"),
                (0.5, f"enum-params {sid} Format")]
        cli = pw_cli(cmds, wait_s=12, label=label)
        res["errors"] = pwcli_errors(cli["log"])
        segs = pwcli_split(cli["log"])
        res["format_enum"] = [{"cmd": c, "fmt": parse_format(s)}
                              for c, s in segs if c.startswith("enum-params")]
        res["links"] = links_for(TAG + "fmt")
    rc, err = stop(pp)
    res["play_rc"] = rc
    res["play_err"] = norm(err)[-200:]
    return res


def fmt_param_leg(target_name, label, pod_rate="44100"):
    """set-param Format on a SINK (scout only measured a stream)."""
    info = node_info(target_name)
    res = {"target": info}
    if not info:
        return res
    sid = info["id"]
    cmds = [(0, f"enum-params {sid} Format"),
            (0.5, f"set-param {sid} Format {{ mediaType: 1, mediaSubtype: 1,"
                  f" format: 259, rate: {pod_rate}, channels: 2 }}"),
            (0.6, f"enum-params {sid} Format"),
            (0.4, f"set-param {sid} Format {{ }}"),
            (0.5, f"enum-params {sid} Format")]
    cli = pw_cli(cmds, wait_s=12, label=label)
    segs = pwcli_split(cli["log"])
    res["errors"] = pwcli_errors(cli["log"])
    res["format_enum"] = [{"cmd": c, "fmt": parse_format(s)}
                          for c, s in segs if c.startswith("enum-params")]
    res["state_after"] = node_info(target_name)
    return res


def fmt_unlinked_leg():
    pp = spawn(["pw-play", "-P", f"node.name={TAG}fmtu",
                "-P", "node.autoconnect=false", "--target", "0", str(TONE)])
    time.sleep(1.0)
    d = pw_dump()
    nds = nodes_by_name(TAG + "fmtu", d)
    sid = nds[0]["id"] if nds else None
    res = {"stream_id": sid, "links": links_for(TAG + "fmtu")}
    if sid is not None:
        cmds = [(0, f"enum-params {sid} Format"),
                (0.5, f"set-param {sid} Format {{ mediaType: 1, mediaSubtype: 1,"
                      " format: 259, rate: 96000, channels: 2 }"),
                (0.6, f"enum-params {sid} Format")]
        cli = pw_cli(cmds, wait_s=10, label="b3-fmt-unlinked")
        segs = pwcli_split(cli["log"])
        res["errors"] = pwcli_errors(cli["log"])
        res["format_enum"] = [{"cmd": c, "fmt": parse_format(s)}
                              for c, s in segs if c.startswith("enum-params")]
    rc, err = stop(pp)
    res["play_rc"] = rc
    res["play_err"] = norm(err)[-200:]
    return res


def sendcmd_leg(target_name):
    info = node_info(target_name)
    res = {"target": info}
    if not info:
        return res
    sid = info["id"]
    seq = ["Suspend", "Resume", "Start", "Pause"]
    cmds = []
    for c in seq:
        cmds.append((0.0, f"send-command {sid} {c} {{}}"))
        cmds.append((0.6, f"info {sid}"))
    cmds.append((0.3, f"send-command {sid} 0 {{}}"))
    cmds.append((0.3, f"send-command {sid} bogus-cmd {{}}"))
    cli = pw_cli(cmds, wait_s=14, label="b3-sendcmd")
    res["errors"] = pwcli_errors(cli["log"])
    segs = pwcli_split(cli["log"])
    res["per_command"] = []
    for c, s in segs:
        states = re.findall(r'state: "([a-z]+)"', s)
        if c.startswith("send-command") or "state:" in s:
            res["per_command"].append({"cmd": c, "states": states})
    res["state_after"] = node_info(target_name)
    return res


def latency_leg(target_name):
    info = node_info(target_name)
    res = {"target": info}
    if not info:
        return res
    sid = info["id"]
    cmds = [(0, f"enum-params {sid} Latency"),
            (0.5, f"set-param {sid} Latency {{ }}"),
            (0.5, f"enum-params {sid} Latency")]
    cli = pw_cli(cmds, wait_s=10, label="b3-latency")
    res["errors"] = pwcli_errors(cli["log"])
    res["latency_lines"] = [l.strip() for l in cli["log"].splitlines()
                            if "Latency" in l or "latency" in l][:24]
    return res


def create_linger_leg():
    out_file = RUNS / "b3-create-linger.log"
    fh = open(out_file, "wb")
    p = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE, stdout=fh,
                         stderr=subprocess.STDOUT)
    OWN_PROCS.append(p)
    res = {"session": str(out_file)}
    try:
        p.stdin.write(b'create-node adapter { factory.name="support.null-audio-sink" '
                      b'node.name="r87b_ling" media.class="Audio/Sink" '
                      b'object.linger=true }\n')
        p.stdin.flush()
        time.sleep(2.0)
        d = pw_dump()
        nds = nodes_by_name("r87b_ling", d)
        res["present_while_session"] = bool(nds)
        res["live_id"] = nds[0]["id"] if nds else None
        p.stdin.write(b"quit\n")
        p.stdin.flush()
        p.stdin.close()
        try:
            p.wait(timeout=6)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait(timeout=3)
    except (BrokenPipeError, OSError):
        pass
    fh.close()
    res["rc"] = p.returncode
    time.sleep(0.6)
    d = pw_dump()
    nds = nodes_by_name("r87b_ling", d)
    res["present_after_quit"] = bool(nds)
    if nds:
        cli = pw_cli([(0, f"destroy {nds[0]['id']}"),
                      (0.5, f"info {nds[0]['id']}")], wait_s=6,
                     label="b3-linger-destroy")
        res["destroy_errors"] = pwcli_errors(cli["log"])
        time.sleep(0.5)
        res["present_after_destroy"] = bool(nodes_by_name("r87b_ling"))
    res["log_tail"] = out_file.read_text(errors="replace")[-600:]
    return res


def destroy_leg():
    pp = spawn(["pw-play", "-P", f"node.name={TAG}dst",
                "--target", NS, str(TONE)])
    time.sleep(1.0)
    d = pw_dump()
    nds = nodes_by_name(TAG + "dst", d)
    kid = nds[0]["id"] if nds else None
    res = {"node_id": kid}
    if kid is not None:
        cli = pw_cli([(0, f"destroy {kid}"), (0.6, f"info {kid}")],
                     wait_s=6, label="b3-destroy")
        res["errors"] = pwcli_errors(cli["log"])
    time.sleep(0.8)
    res["play_rc_after"] = pp.poll()
    res["node_after"] = bool(nodes_by_name(TAG + "dst"))
    rc, err = stop(pp)
    res["play_rc"] = rc
    res["play_err"] = norm(err)[-300:]
    return res


def b3_cli(sinks):
    res = {"sinks": sinks}
    info = node_info(NS)
    res["sink"] = info
    sid = info["id"] if info else None
    if sid is not None:
        res["cold_nowarm_live"] = nowarm_info(sid)
        w = pw_cli([(0, f"info {sid}")], label="b3-warm-live")
        res["warm_live"] = {"errors": pwcli_errors(w["log"]),
                            "state_lines": [l.strip() for l in w["log"].splitlines()
                                            if "state:" in l]}
        w2 = pw_cli([(0, "info 99999999")], label="b3-warm-unknown")
        res["warm_unknown"] = {"errors": pwcli_errors(w2["log"])}
    res["mut_quiet"] = mut_leg("b3-mut-quiet")
    res["fmt_sealed"] = fmt_sealed_leg("b3-fmt-sealed")
    res["fmt_sink"] = fmt_param_leg(NS, "b3-fmt-sink")
    res["fmt_unlinked"] = fmt_unlinked_leg()
    res["sendcmd"] = sendcmd_leg(NS)
    res["latency"] = latency_leg(NS)
    res["create_linger"] = create_linger_leg()
    res["destroy"] = destroy_leg()
    save("b3-cli.json", res)
    return res


# ---------------- B4: midi ----------------

def b4_midi():
    res = {"bridge": node_info("Midi-Bridge")}
    br = node_info("Midi-Bridge")
    legs = [
        ("m_t_bridge", ["pw-midiplay", "-P", f"node.name={TAG}mp_bn",
                        "--target", "Midi-Bridge", str(SMF)]),
        ("m_t_serial", ["pw-midiplay", "-P", f"node.name={TAG}mp_ser",
                        "--target", str(br["serial"]) if br else "n/a", str(SMF)]),
        ("m_t_objid", ["pw-midiplay", "-P", f"node.name={TAG}mp_oid",
                       "--target", str(br["id"]) if br else "n/a", str(SMF)]),
        ("m_t_garbage", ["pw-midiplay", "-P", f"node.name={TAG}mp_gb",
                         "--target", "r87b_no_such", str(SMF)]),
        ("m_t_zero", ["pw-midiplay", "-P", f"node.name={TAG}mp_z",
                      "--target", "0", str(SMF)]),
        ("m_t_prop", ["pw-midiplay", "-P", f"node.name={TAG}mp_pr",
                      "-P", "target.object=Midi-Bridge", str(SMF)]),
        ("m_t_noauto", ["pw-midiplay", "-P", f"node.name={TAG}mp_na",
                        "-P", "node.autoconnect=false", str(SMF)]),
    ]
    for leg, args in legs:
        names = [a.split("=", 1)[1] for a in args if a.startswith("node.name=")]
        res[leg] = play_leg(names[0], args, observe_s=(0.9, 1.8))
    # pinned capture with real events
    rec = RUNS / "mr_pin.mid"
    if rec.exists():
        rec.unlink()
    mp = spawn(["pw-midirecord", "-P", f"node.name={TAG}mr",
                "--target", "0", str(rec)])
    time.sleep(1.0)
    d = pw_dump()
    mnode = nodes_by_name(TAG + "mr", d)
    bnode = nodes_by_name("Midi-Bridge", d)
    ports = port_inventory(d)
    myin = [p for p in ports if mnode and p["node_id"] == str(mnode[0]["id"])
            and p["direction"] == "in"]
    brout = [p for p in ports if bnode and p["node_id"] == str(bnode[0]["id"])
             and p["direction"] == "out"]
    res["pin"] = {"my_in": myin, "bridge_out": brout}
    if myin and brout:
        lk = sh(["pw-link", f"Midi-Bridge:{brout[0]['name']}",
                 f"{TAG}mr:{myin[0]['name']}"], timeout=10)
        res["pin"]["pwlink_rc"] = lk["rc"]
        res["pin"]["pwlink_err"] = norm(lk["err"])[-200:]
        time.sleep(0.4)
        res["pin"]["links_after"] = links_for(TAG + "mr")
        inj = sh(["aplaymidi", "-p", "14:0", str(SMF)], timeout=15)
        res["pin"]["aplaymidi_rc"] = inj["rc"]
        time.sleep(1.3)
    rc_m, err_m = stop(mp)
    res["pin"]["rc"] = rc_m
    res["pin"]["stderr"] = norm(err_m)[-300:]
    res["pin"]["bytes"] = rec.stat().st_size if rec.exists() else None
    if rec.exists():
        res["pin"]["head"] = rec.read_bytes()[:80].hex()
        p2 = sh(["pw-mididump", str(rec)], timeout=10)
        res["pin"]["offline_parse"] = {"rc": p2["rc"],
                                       "out": norm(p2["out"])[-500:]}
    # mididump live through a pin
    env = {"PIPEWIRE_PROPS": "{ node.name = r87b_mdump }"}
    dp = spawn(["pw-mididump"], env=env, keep_stdout=True)
    time.sleep(1.2)
    d = pw_dump()
    cand = nodes_by_name(TAG + "mdump", d) or nodes_by_name("midi-dump", d)
    cand.sort(key=lambda o: o["id"])
    dn = cand[-1] if cand else None
    res["mdump_live"] = {"node": ({"id": dn["id"], "props": props_of(dn)}
                                  if dn else None),
                         "candidates": [{"id": o["id"],
                                         "name": props_of(o).get("node.name")}
                                        for o in cand]}
    if dn:
        din = [p for p in port_inventory(d)
               if p["node_id"] == str(dn["id"]) and p["direction"] == "in"]
        bnode = nodes_by_name("Midi-Bridge", d)
        brout2 = [p for p in port_inventory(d)
                  if bnode and p["node_id"] == str(bnode[0]["id"])
                  and p["direction"] == "out"]
        if din and brout2:
            lk = sh(["pw-link", f"Midi-Bridge:{brout2[0]['name']}",
                     f"{dn['info']['props'].get('node.name')}:{din[0]['name']}"],
                    timeout=10)
            res["mdump_live"]["pwlink_rc"] = lk["rc"]
            time.sleep(0.4)
            inj = sh(["aplaymidi", "-p", "14:0", str(SMF)], timeout=15)
            res["mdump_live"]["aplaymidi_rc"] = inj["rc"]
            time.sleep(1.5)
    rc_d, err_d = stop(dp)
    try:
        out_d = dp.stdout.read().decode(errors="replace") if dp.stdout else ""
    except OSError:
        out_d = ""
    res["mdump_live"]["rc"] = rc_d
    res["mdump_live"]["stdout"] = norm(out_d)[-800:]
    res["mdump_live"]["stderr"] = norm(err_d)[-200:]
    # offline file parse + UMP mode (unstated)
    f1 = sh(["pw-mididump", str(SMF)], timeout=10)
    res["mdump_file"] = {"rc": f1["rc"], "out": norm(f1["out"])[-500:]}
    f2 = sh(["pw-mididump", "-M", "ump", str(SMF)], timeout=10)
    res["mdump_ump"] = {"rc": f2["rc"], "out": norm(f2["out"])[-500:],
                        "err": norm(f2["err"])[-300:]}
    # midirecord --target Midi-Bridge (verbatim refusal shape) and garbage
    rec2 = RUNS / "mr_bridge.mid"
    if rec2.exists():
        rec2.unlink()
    mp2 = spawn(["pw-midirecord", "-P", f"node.name={TAG}mrb",
                 "--target", "Midi-Bridge", str(rec2)])
    time.sleep(1.0)
    inj = sh(["aplaymidi", "-p", "14:0", str(SMF)], timeout=15)
    res["mrb_aplaymidi_rc"] = inj["rc"]
    time.sleep(1.0)
    rc_b, err_b = stop(mp2)
    res["midirecord_bridge"] = {"rc": rc_b, "stderr": norm(err_b)[-300:],
                                "bytes": rec2.stat().st_size if rec2.exists() else None,
                                "head": rec2.read_bytes()[:64].hex()
                                if rec2.exists() else None}
    g = sh(["pw-midirecord", "-P", f"node.name={TAG}mrg",
            "--target", "r87b_no_such", str(RUNS / "mr_garb.mid")], timeout=8)
    res["midirecord_garbage"] = {"rc": g["rc"], "err": norm(g["err"])[-300:]}
    save("b4-midi.json", res)
    return res


# ---------------- B5: remote ----------------

def trip(cmd, n=3):
    return [{"rc": o["rc"], "out": norm(o["out"])[-200:],
             "err": norm(o["err"])[-200:]} for o in
            [sh(cmd, timeout=15) for _ in range(n)]]


def b5_remote():
    res = {}
    res["pactl_raop"] = trip(["pactl", "load-module", "module-raop-discover"])
    res["pactl_zc"] = trip(["pactl", "load-module", "module-zeroconf-discover"])
    res["pactl_raop_sink"] = trip(["pactl", "load-module", "module-raop-sink"], 1)
    res["pactl_bogus"] = trip(["pactl", "load-module", "module-totally-bogus-r87b"], 1)
    res["pwcat_remote"] = trip(["pw-cat", "-R", "r87b_no_such_remote", "-p", str(TONE)])
    env = dict(os.environ, PIPEWIRE_REMOTE="r87b_no_such_remote")
    res["pwplay_env_remote"] = [
        {"rc": x["rc"], "err": norm(x["err"])[-200:]}
        for x in [sh(["pw-play", str(TONE)], timeout=15, env=env) for _ in range(3)]]
    cli = pw_cli([(0, "list-remotes"),
                  (0.4, "load-module libpipewire-module-raop-discover"),
                  (0.4, "load-module libpipewire-module-zeroconf-discover"),
                  (0.4, "load-module libpipewire-module-null-sink"),
                  (0.4, "load-module module-null-sink"),
                  (0.4, "connect r87b_no_such_remote"),
                  (0.5, "list-remotes")], wait_s=12, label="b5-remote")
    res["pwcli"] = {"errors": pwcli_errors(cli["log"])}
    (RECEIPTS / "b5-remote.raw.txt").write_text(cli["log"])
    moddir = "/usr/lib/pipewire-0.3"
    try:
        mods = sorted(os.listdir(moddir))
    except OSError:
        mods = []
    res["module_dir_count"] = len(mods)
    res["module_dir_network"] = [m for m in mods if re.search(
        r"raop|zeroconf|airplay|rtp|tunnel|netjack|vban", m)]
    d = pw_dump()
    res["remote_named_objects"] = [{"id": o["id"], "type": o.get("type"),
                                    "name": o.get("info", {}).get("name")}
                                   for o in d
                                   if "remote" in str(o.get("info", {}).get("name", "")).lower()]
    save("b5-remote.json", res)
    return res


# ---------------- B6: foreign ----------------

def b6_foreign():
    d = pw_dump()
    foreign = [o for o in d if o.get("type") == "PipeWire:Interface:Node"
               and props_of(o).get("media.class") == "Audio/Sink"
               and str(props_of(o).get("client.id")) == "33"
               and str(props_of(o).get("node.name", "")).startswith("alsa_")]
    hdmi = [o for o in foreign if "hdmi" in str(props_of(o).get("node.name"))]
    target = hdmi[0] if hdmi else (foreign[0] if foreign else None)
    res = {"foreign_candidates": [{"id": o["id"], "name": props_of(o).get("node.name")}
                                  for o in foreign]}
    if target is None:
        save("b6-foreign.json", res)
        return res
    fid = target["id"]
    fname = props_of(target).get("node.name")
    res["target"] = {"id": fid, "name": fname}
    cmds = [(0, f"info {fid}"),
            (0.3, f"enum-params {fid} Props"),
            (0.4, f"enum-params {fid} Format"),
            (0.4, f"set-param {fid} Props {{ no_such_prop: 3 }}"),
            (0.3, f"set-param {fid} BogusType {{ }}"),
            (0.3, "info 99999999"),
            (0.3, "enum-params 99999999 Props"),
            (0.3, "set-param 99999999 Props { volume: 0.5 }"),
            (0.3, "destroy 99999999"),
            (0.3, "get-permissions 33"),
            (0.3, "get-permissions 99999999")]
    cli = pw_cli(cmds, wait_s=12, label="b6-foreign")
    res["errors"] = pwcli_errors(cli["log"])
    segs = pwcli_split(cli["log"])
    res["props_enum_volume"] = [parse_props_volume(s) for c, s in segs
                                if c.startswith("enum-params") and "Props" in c]
    (RECEIPTS / "b6-foreign.raw.txt").write_text(cli["log"])
    # identical-value write (same value as currently in force)
    vol = res["props_enum_volume"][0] if res["props_enum_volume"] else None
    if vol is not None:
        cli2 = pw_cli([(0, f"set-param {fid} Props {{ volume: {vol} }}"),
                       (0.5, f"enum-params {fid} Props")], wait_s=6,
                      label="b6-foreign-samevalue")
        res["samevalue"] = {"errors": pwcli_errors(cli2["log"]),
                            "volume_after": [parse_props_volume(s) for c, s in
                                             pwcli_split(cli2["log"])
                                             if c.startswith("enum-params")]}
        (RECEIPTS / "b6-foreign-samevalue.raw.txt").write_text(cli2["log"])
    save("b6-foreign.json", res)
    return res


# ---------------- load battery ----------------

def load_battery(sinks):
    res = {"loadavg_before": loadavg(),
           "contention_before": contention_snapshot()}
    hog_pids = hog_start(24)
    time.sleep(1.0)
    res["hog_pids"] = hog_pids
    res["loadavg_under"] = loadavg()
    try:
        d = pw_dump()
        ns_id = sinks[NS]["id"]
        ns_ser = str(sinks[NS]["serial"])
        legs = [
            ("l_own", ["pw-play", "-P", f"node.name={TAG}l_own",
                       "--target", NS, str(TONE)], None),
            ("l_garbage", ["pw-play", "-P", f"node.name={TAG}l_garb",
                           "--target", "r87b_no_such_target", str(TONE)], None),
            ("l_pb2", ["pw-play", "-P", f"node.name={TAG}l_pb2",
                       "-P", f"target.object={NS}",
                       "--target", "r87b_no_such_target", str(TONE)], None),
            ("l_serial", ["pw-play", "-P", f"node.name={TAG}l_ser",
                          "--target", ns_ser, str(TONE)], None),
            ("l_objid", ["pw-play", "-P", f"node.name={TAG}l_oid",
                         "--target", str(ns_id), str(TONE)], None),
            ("l_zero", ["pw-play", "-P", f"node.name={TAG}l_zero",
                        "--target", "0", str(TONE)], None),
            ("l_mode_pr", ["pw-cat", "-p", "-r", "-P", f"node.name={TAG}l_pr",
                           "-P", "stream.capture.sink=true", "--target", NS,
                           "-n", str(RATE), str(RUNS / "l_pr.wav")], None),
            ("l_mode_rp", ["pw-cat", "-r", "-p", "-P", f"node.name={TAG}l_rp",
                           "--target", NS, str(TONE)], None),
        ]
        for leg, args, env in legs:
            names = [a.split("=", 1)[1] for a in args if a.startswith("node.name=")]
            res[leg] = play_leg(names[0], args, env=env, observe_s=(1.2, 2.0))
        # cold-registry under load: nowarm / 1.4 s / 2.5 s
        res["l_cold_nowarm"] = nowarm_info(ns_id)
        for warm in (1.4, 2.5):
            w = pw_cli([(0, f"info {ns_id}")], warm_s=warm,
                       label=f"l-warm-{warm}")
            res[f"l_warm_{warm}"] = {
                "errors": pwcli_errors(w["log"]),
                "state_lines": [l.strip() for l in w["log"].splitlines()
                                if "state:" in l]}
        res["l_mut1"] = mut_leg("l-mut-1")
        res["l_mut2"] = mut_leg("l-mut-2")
        res["l_fmt_sealed"] = fmt_sealed_leg("l-fmt-sealed")
        # midi under load: no-target + pin carries events
        res["l_midi_notarget"] = play_leg(
            TAG + "l_mp", ["pw-midiplay", "-P", f"node.name={TAG}l_mp",
                           "--target", "Midi-Bridge", str(SMF)],
            observe_s=(1.2, 2.0))
        rec = RUNS / "l_mr_pin.mid"
        if rec.exists():
            rec.unlink()
        mp = spawn(["pw-midirecord", "-P", f"node.name={TAG}l_mr",
                    "--target", "0", str(rec)])
        time.sleep(1.2)
        d = pw_dump()
        mnode = nodes_by_name(TAG + "l_mr", d)
        bnode = nodes_by_name("Midi-Bridge", d)
        ports = port_inventory(d)
        myin = [p for p in ports if mnode and p["node_id"] == str(mnode[0]["id"])
                and p["direction"] == "in"]
        brout = [p for p in ports if bnode and p["node_id"] == str(bnode[0]["id"])
                 and p["direction"] == "out"]
        res["l_midi_pin"] = {"my_in": myin, "bridge_out": brout}
        if myin and brout:
            lk = sh(["pw-link", f"Midi-Bridge:{brout[0]['name']}",
                     f"{TAG}l_mr:{myin[0]['name']}"], timeout=10)
            res["l_midi_pin"]["pwlink_rc"] = lk["rc"]
            time.sleep(0.4)
            inj = sh(["aplaymidi", "-p", "14:0", str(SMF)], timeout=20)
            res["l_midi_pin"]["aplaymidi_rc"] = inj["rc"]
            time.sleep(1.5)
        rc_m, err_m = stop(mp)
        res["l_midi_pin"]["rc"] = rc_m
        res["l_midi_pin"]["stderr"] = norm(err_m)[-300:]
        res["l_midi_pin"]["bytes"] = rec.stat().st_size if rec.exists() else None
        if rec.exists():
            res["l_midi_pin"]["head"] = rec.read_bytes()[:80].hex()
            p2 = sh(["pw-mididump", str(rec)], timeout=10)
            res["l_midi_pin"]["offline_parse"] = {"rc": p2["rc"],
                                                  "out": norm(p2["out"])[-400:]}
    finally:
        killed = hog_stop()
        res["hog_killed_pids"] = killed
        res["loadavg_after"] = loadavg()
        res["contention_after"] = contention_snapshot()
    save("l1-load.json", res)
    return res


# ---------------- host-state variation ----------------

def host_battery(sinks):
    res = {"contention_before": contention_snapshot()}
    d0 = sh(["pactl", "get-default-sink"])["out"].strip()
    res["default_sink_initial"] = d0
    set_r = sh(["pactl", "set-default-sink", NS], timeout=10)
    res["set_default_rc"] = set_r["rc"]
    time.sleep(0.4)
    res["default_sink_now"] = sh(["pactl", "get-default-sink"])["out"].strip()
    try:
        res["h_garbage"] = play_leg(TAG + "h_garb",
                                    ["pw-play", "-P", f"node.name={TAG}h_garb",
                                     "--target", "r87b_no_such_target",
                                     str(TONE)])
        res["h_mon"] = play_leg(TAG + "h_mon",
                                ["pw-play", "-P", f"node.name={TAG}h_mon",
                                 "--target", NS + ".monitor", str(TONE)])
        res["h_own"] = play_leg(TAG + "h_own",
                                ["pw-play", "-P", f"node.name={TAG}h_own",
                                 "--target", NS, str(TONE)])
    finally:
        rst = sh(["pactl", "set-default-sink", d0], timeout=10)
        time.sleep(0.4)
        res["restore_rc"] = rst["rc"]
        res["default_sink_restored"] = sh(["pactl", "get-default-sink"])["out"].strip()
    res["h_garbage_restored"] = play_leg(
        TAG + "h_garb2", ["pw-play", "-P", f"node.name={TAG}h_garb2",
                          "--target", "r87b_no_such_target", str(TONE)])
    # suspended-sink variation
    info = node_info(NS)
    if info:
        cli = pw_cli([(0, f"send-command {info['id']} Suspend {{}}"),
                      (0.6, f"info {info['id']}")], wait_s=6,
                     label="h-suspend")
        res["suspend"] = {"errors": pwcli_errors(cli["log"]),
                          "state": node_info(NS)}
        res["h_own_suspended"] = play_leg(
            TAG + "h_susp", ["pw-play", "-P", f"node.name={TAG}h_susp",
                             "--target", NS, str(TONE)])
        cli2 = pw_cli([(0, f"send-command {info['id']} Resume {{}}"),
                       (0.6, f"info {info['id']}")], wait_s=6,
                      label="h-resume")
        res["resume"] = {"errors": pwcli_errors(cli2["log"]),
                         "state": node_info(NS)}
        res["h_own_resumed"] = play_leg(
            TAG + "h_res", ["pw-play", "-P", f"node.name={TAG}h_res",
                            "--target", NS, str(TONE)])
    res["contention_after"] = contention_snapshot()
    save("h1-host.json", res)
    return res


# ---------------- cleanup ----------------

def cleanup():
    res = {"hog_killed": hog_stop()}
    me = os.getpid()
    killed, stubborn = [], []
    for e in proc_snapshot():
        c = e["cmd"]
        if e["pid"] == me or "r87b_probe" in c or "r87b_lib" in c:
            continue
        if "r87b_" in c:
            try:
                os.kill(e["pid"], signal.SIGTERM)
                killed.append(e)
            except OSError:
                pass
    time.sleep(1.2)
    for e in killed:
        try:
            os.kill(e["pid"], 0)
            os.kill(e["pid"], signal.SIGKILL)
            stubborn.append(e)
        except OSError:
            pass
    res["killed"] = killed
    res["sigkilled"] = stubborn
    time.sleep(0.5)
    res["unload"] = {}
    for nm in (NS, NS2):
        res["unload"][nm] = unload_own_sink(nm)
    time.sleep(0.6)
    d = pw_dump()
    res["leftover_nodes"] = [{"id": o["id"], "name": props_of(o).get("node.name")}
                             for o in d if o.get("type") == "PipeWire:Interface:Node"
                             and str(props_of(o).get("node.name", "")).startswith(TAG)]
    res["leftover_modules"] = [l for l in mod_lines() if "r87b" in l]
    res["pactl_default_sink"] = sh(["pactl", "get-default-sink"])["out"].strip()
    res["loadavg"] = loadavg()
    save("final-cleanup.json", res)
    return res


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    gen_tone(dur_s=12.0)
    gen_smf()
    out = {}
    if stage in ("quiet", "all"):
        sinks = ensure_sinks()
        out["inventory"] = {
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "uname": sh(["uname", "-r"])["out"].strip(),
            "pw_cat_version": sh(["pw-cat", "--version"], timeout=10)["out"].strip().splitlines(),
            "pactl": sh(["pactl", "--version"], timeout=10)["out"].strip().splitlines()[:1],
            "symlinks": {t: {"realpath": os.path.realpath("/usr/bin/" + t),
                             "islink": os.path.islink("/usr/bin/" + t)}
                         for t in ("pw-play", "pw-record", "pw-midiplay",
                                   "pw-midirecord", "pw-mididump", "pw-cli")},
            "sha256": {t: sh(["sha256sum", os.path.realpath("/usr/bin/" + t)])["out"].split()[0]
                       for t in ("pw-play", "pw-record", "pw-midiplay",
                                 "pw-midirecord", "pw-mididump", "pw-cli")},
            "sinks": sinks,
            "contention": contention_snapshot(),
        }
        save("b0-inventory.json", out["inventory"])
        out["b1"] = b1_lattice(sinks)
        out["b2"] = b2_modes(sinks)
        out["b3"] = b3_cli(sinks)
        out["b4"] = b4_midi()
        out["b5"] = b5_remote()
        out["b6"] = b6_foreign()
    if stage in ("load", "all"):
        sinks = ensure_sinks()
        out["load"] = load_battery(sinks)
    if stage in ("host", "all"):
        sinks = ensure_sinks()
        out["host"] = host_battery(sinks)
    if stage in ("cleanup", "all"):
        out["cleanup"] = cleanup()
    print("stage", stage, "done")


if __name__ == "__main__":
    main()
