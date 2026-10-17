#!/usr/bin/env python3
"""r87 scout supplement — create-node roundtrip, send-command, Format set-param,
midi-dump live pin, midi prop-path targets."""
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r87_probe import (RUNS, GEN, RECEIPTS, TAG, TONE, SMF, RATE, sh, norm,
                       pw_dump, nodes_by_name, port_inventory, links_for,
                       spawn, stop, pw_cli, pwcli_events, module_idx_of_sink,
                       load_own_sink, unload_own_sink)


def cli_session(cmds, label):
    r = pw_cli(cmds, wait_s=12, label=label)
    ev = pwcli_events(r["log"])
    ev["marks"] = r["marks"]
    ev["log_tail"] = [l for l in r["log"].splitlines() if "error" in l.lower()
                      or "Object: size" in l or "created" in l.lower()
                      or "usage" in l.lower()][-30:]
    return ev


def leg_create_node():
    res = {}
    cmds = [(0, 'create-node adapter { factory.name="support.null-audio-sink" '
               'node.name="r87_adp" media.class="Audio/Sink" '
               'object.linger="false" }'),
            (1.2, "list-objects Node")]
    r = pw_cli(cmds, wait_s=8, label="sb-create-node")
    res["cli_errors"] = pwcli_events(r["log"])["errors"]
    res["proxy_lines"] = [l for l in r["log"].splitlines()
                          if "@proxy" in l or "error id:" in l][:8]
    time.sleep(0.5)
    adp = nodes_by_name("r87_adp")
    res["present"] = bool(adp)
    res["id"] = adp[0]["id"] if adp else None
    if adp:
        res["props"] = {k: v for k, v in adp[0]["info"]["props"].items()
                        if k.startswith(("media.", "node.", "object.", "factory."))}
        c2 = pw_cli([(0, f"destroy {adp[0]['id']}")], wait_s=5,
                    label="sb-destroy-adp")
        res["destroy_errors"] = pwcli_events(c2["log"])["errors"]
        time.sleep(0.5)
        res["present_after_destroy"] = bool(nodes_by_name("r87_adp"))
    return res


def leg_send_command(sink="r87_ns"):
    res = {}
    nds = nodes_by_name(sink)
    sid = nds[0]["id"] if nds else None
    res["sink_id"] = sid
    if sid is None:
        return res
    for cmd_id in ("Suspend", "Pause", "0", "bogus-cmd"):
        r = pw_cli([(0, f'send-command {sid} {cmd_id} {{}}'),
                    (0.6, f"info {sid}")], wait_s=6,
                   label=f"sb-sendcmd-{cmd_id.replace(' ','_')}")
        ev = pwcli_events(r["log"])
        res[cmd_id] = {"errors": ev["errors"],
                       "lines": [l.strip() for l in r["log"].splitlines()
                                 if "send-command" in l or "state:" in l
                                 or "error" in l.lower()][-8:]}
        time.sleep(0.4)
    return res


def leg_format_setparam():
    """set-param Format variants on a live own stream + enum-params witnesses."""
    res = {}
    pp = spawn(["pw-play", "-P", f"node.name={TAG}fmt",
                "--target", "r87_ns", str(TONE)])
    time.sleep(1.0)
    nds = nodes_by_name(f"{TAG}fmt")
    fid = nds[0]["id"] if nds else None
    res["stream_id"] = fid
    if fid is not None:
        cmds = [
            (0, f"enum-params {fid} EnumFormat"),
            (0.6, 'set-param {0} Format {{ mediaType: 1, mediaSubtype: 1, '
                  'format: 3, rate: 96000, channels: 2 }}'.format(fid)),
            (0.7, f"enum-params {fid} Format"),
            (0.5, f"set-param {fid} Format {{ }}"),
            (0.6, f"enum-params {fid} Format"),
        ]
        r = pw_cli(cmds, wait_s=12, label="sb-format")
        res["errors"] = pwcli_events(r["log"])["errors"]
        res["marks"] = r["marks"]
        # does the node still play?
        res["node_alive"] = pp.poll() is None
        res["links"] = links_for(f"{TAG}fmt")
    rc, err = stop(pp)
    res["play_rc"] = rc
    res["play_err"] = norm(err)[-200:]
    return res


def leg_mididump_live():
    """pin bridge capture -> midi-dump input; aplaymidi; read dump stdout."""
    res = {}
    dp = spawn(["pw-mididump"], keep_stdout=True)
    time.sleep(1.2)
    d = pw_dump()
    mnode = nodes_by_name("midi-dump", d)
    bnode = nodes_by_name("Midi-Bridge", d)
    ports = port_inventory(d)
    res["dump_node"] = mnode[0]["info"]["props"] if mnode else None
    din = [p for p in ports if mnode and p["node_id"] == str(mnode[0]["id"])
           and p["direction"] == "in"]
    bout = [p for p in ports if bnode and p["node_id"] == str(bnode[0]["id"])
            and p["direction"] == "out"]
    res["dump_in"] = din
    res["bridge_out"] = bout
    if din and bout:
        lk = sh(["pw-link", f"Midi-Bridge:{bout[0]['name']}",
                 f"midi-dump:{din[0]['name']}"], timeout=10)
        res["pwlink_rc"] = lk["rc"]
        res["pwlink_err"] = norm(lk["err"])[-200:]
        time.sleep(0.4)
        res["links_after"] = links_for("midi-dump")
        inj = sh(["aplaymidi", "-p", "14:0", str(SMF)], timeout=15)
        res["aplaymidi_rc"] = inj["rc"]
        time.sleep(1.0)
    rc, err = stop(dp)
    try:
        out = dp.stdout.read().decode(errors="replace") if dp.stdout else ""
    except OSError:
        out = ""
    res["rc"] = rc
    res["stdout"] = out[-1200:]
    res["stderr"] = norm(err)[-300:]
    return res


def leg_midi_props():
    """prop-path targeting on midi playback (does target.object unlock midi?)."""
    res = {}
    for leg, extra in (("mprop_tobj_bridge", "target.object=Midi-Bridge"),
                       ("mprop_nodetgt_bridge", "node.target=Midi-Bridge"),
                       ("mprop_tobj_garbage", "target.object=r87_no_such"),
                       ("mprop_noauto", "node.autoconnect=false")):
        nm = f"{TAG}{leg}"
        p = spawn(["pw-midiplay", "-P", f"node.name={nm}",
                   "-P", extra, str(SMF)])
        time.sleep(1.1)
        d = pw_dump()
        nds = nodes_by_name(nm, d)
        res[leg] = {"present": bool(nds),
                    "class": (nds[0]["info"]["props"].get("media.class")
                              if nds else None),
                    "links": links_for(nm)}
        rc, err = stop(p)
        res[leg]["rc"] = rc
        res[leg]["stderr"] = norm(err)[-200:]
    return res


def leg_midi_modeflag():
    """pw-cat -m -p (midi+direction) vs argv0 midiplay."""
    res = {}
    p = spawn(["pw-cat", "-m", "-p", "-P", f"node.name={TAG}mm_p",
               "--target", "0", str(SMF)])
    time.sleep(0.9)
    nds = nodes_by_name(f"{TAG}mm_p")
    res["pwcat_m_p"] = {"present": bool(nds),
                        "class": (nds[0]["info"]["props"].get("media.class")
                                  if nds else None),
                        "ports": [q for q in port_inventory()
                                  if nds and q["node_id"] == str(nds[0]["id"])]}
    rc, err = stop(p)
    res["pwcat_m_p"]["rc"] = rc
    res["pwcat_m_p"]["stderr"] = norm(err)[-200:]
    # -d dsd mode on wav
    p = spawn(["pw-cat", "-d", "-p", "-P", f"node.name={TAG}md_p",
               "--target", "0", str(TONE)])
    time.sleep(0.9)
    nds = nodes_by_name(f"{TAG}md_p")
    res["pwcat_d_p"] = {"present": bool(nds),
                        "class": (nds[0]["info"]["props"].get("media.class")
                                  if nds else None)}
    rc, err = stop(p)
    res["pwcat_d_p"]["rc"] = rc
    res["pwcat_d_p"]["stderr"] = norm(err)[-200:]
    return res


def main():
    if not nodes_by_name("r87_ns"):
        load_own_sink("r87_ns")
    out = {}
    try:
        out["create_node"] = leg_create_node()
        out["send_command"] = leg_send_command()
        out["format_setparam"] = leg_format_setparam()
        out["mididump_live"] = leg_mididump_live()
        out["midi_props"] = leg_midi_props()
        out["midi_modeflag"] = leg_midi_modeflag()
    finally:
        for nm in ("r87_ns", "r87_adp"):
            unload_own_sink(nm)
        json.dump(out, open(RECEIPTS / "s8-supplement.json", "w"), indent=1)
    print("done")


if __name__ == "__main__":
    main()
