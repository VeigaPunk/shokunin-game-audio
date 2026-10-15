#!/usr/bin/env python3
"""r87b supplement — targeted re-checks:
  (a) exact refusal messages with BOTH streams captured (-d, -c),
  (b) port inventories with the int/str node_id bug fixed,
  (c) pw-mididump live mode: bare vs PIPEWIRE_PROPS env,
  (d) unstated precedence combinations (env vs -P vs node.target vs --target 0).
Writes receipts/b1x-supplement.json. All objects r87b_*.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r87b_lib import (  # noqa: E402
    TAG, NS, NS2, TONE, SMF, RUNS, RECEIPTS, sh, norm, pw_dump, props_of,
    nodes_by_name, port_inventory, links_for, spawn, stop, play_leg)


def save(name, obj):
    (RECEIPTS / name).write_text(json.dumps(obj, indent=1, default=str))


def ports_leg(name, args, wait=1.0):
    p = spawn(args)
    time.sleep(wait)
    d = pw_dump()
    nds = nodes_by_name(name, d)
    node = nds[0] if nds else None
    ports = [{"name": q["name"], "direction": q["direction"]}
             for q in port_inventory(d)
             if node and q["node_id"] == str(node["id"])]
    rc, err = stop(p)
    return {"argv": args, "present": node is not None,
            "class": props_of(node or {}).get("media.class"),
            "ports": ports, "rc": rc, "stderr": norm(err)[-200:]}


def mdump_live(label, env=None):
    dp = spawn(["pw-mididump"], env=env, keep_stdout=True)
    time.sleep(1.2)
    alive = dp.poll() is None
    d = pw_dump()
    cands = [o for o in d if props_of(o).get("media.category") == "Filter"
             and props_of(o).get("media.type") == "Midi"]
    res = {"alive_after_1.2s": alive,
           "filter_nodes": [{"id": o["id"], "name": props_of(o).get("node.name"),
                             "client": props_of(o).get("client.id")}
                            for o in cands]}
    dn = cands[-1] if cands else None
    if dn:
        din = [p for p in port_inventory(d)
               if p["node_id"] == str(dn["id"]) and p["direction"] == "in"]
        bnode = nodes_by_name("Midi-Bridge", d)
        brout = [p for p in port_inventory(d)
                 if bnode and p["node_id"] == str(bnode[0]["id"])
                 and p["direction"] == "out"]
        if din and brout:
            lk = sh(["pw-link", f"Midi-Bridge:{brout[0]['name']}",
                     f"{props_of(dn).get('node.name')}:{din[0]['name']}"],
                    timeout=10)
            res["pwlink_rc"] = lk["rc"]
            time.sleep(0.4)
            inj = sh(["aplaymidi", "-p", "14:0", str(SMF)], timeout=15)
            res["aplaymidi_rc"] = inj["rc"]
            time.sleep(1.5)
    rc, err = stop(dp)
    try:
        out = dp.stdout.read().decode(errors="replace") if dp.stdout else ""
    except OSError:
        out = ""
    res["rc"] = rc
    res["stdout"] = norm(out)[-700:]
    res["stderr"] = norm(err)[-200:]
    return res


def main():
    out = {}
    # (a) exact refusal classes with both streams
    for tag, args in (("m_dsd", ["pw-cat", "-d", "-p", "-P", f"node.name={TAG}s_d",
                                 "--target", "0", str(TONE)]),
                      ("m_clip", ["pw-cat", "-c", "-p", "-P", f"node.name={TAG}s_c",
                                  "--target", "0", str(SMF)]),
                      ("m_sysex", ["pw-cat", "-s", "-p", "-P", f"node.name={TAG}s_s",
                                   "--target", "0", str(SMF)])):
        r = sh(args, timeout=10)
        out[tag] = {"rc": r["rc"], "out": norm(r["out"])[:600],
                    "err": norm(r["err"])[:600]}
    # (b) port inventories (fixed comparison)
    out["ports"] = {
        "rec_long": ports_leg(TAG + "sp_recl",
                              ["pw-cat", "--record", "-P", f"node.name={TAG}sp_recl",
                               "-P", "stream.capture.sink=true", "--target", NS,
                               "-n", str(2 * 48000), str(RUNS / "sp_recl.wav")]),
        "midi_p": ports_leg(TAG + "sp_mp",
                            ["pw-cat", "-m", "-p", "-P", f"node.name={TAG}sp_mp",
                             "--target", "0", str(SMF)]),
        "midi_r": ports_leg(TAG + "sp_mr",
                            ["pw-cat", "-m", "-r", "-P", f"node.name={TAG}sp_mr",
                             "--target", "0", str(RUNS / "sp_mr.mid")]),
        "sysex": ports_leg(TAG + "sp_sx",
                           ["pw-cat", "-s", "-p", "-P", f"node.name={TAG}sp_sx",
                            "--target", "0", str(SMF)]),
        "ump_midi_p": ports_leg(TAG + "sp_ump",
                                ["pw-cat", "-M", "ump", "-m", "-p",
                                 "-P", f"node.name={TAG}sp_ump", "--target", "0",
                                 str(SMF)]),
        "p_then_r": ports_leg(TAG + "sp_pr",
                              ["pw-cat", "-p", "-r", "-P", f"node.name={TAG}sp_pr",
                               "-P", "stream.capture.sink=true", "--target", NS,
                               "-n", str(2 * 48000), str(RUNS / "sp_pr.wav")]),
        "play_own": ports_leg(TAG + "sp_own",
                              ["pw-play", "-P", f"node.name={TAG}sp_own",
                               "--target", NS, str(TONE)]),
    }
    # (c) mididump live: bare vs env
    out["mdump_bare"] = mdump_live("bare")
    out["mdump_env"] = mdump_live("env", env={"PIPEWIRE_PROPS":
                                              "{ node.name = r87b_mdump }"})
    # (d) unstated precedence combinations
    combos = [
        ("x_env_swap", ["pw-play", "-P", f"node.name={TAG}x_envswap",
                        "-P", f"target.object={NS}",
                        "--target", "r87b_no_such_target", str(TONE)],
         {"PIPEWIRE_PROPS": "{ target.object = %s }" % NS2}),
        ("x_env_garbage", ["pw-play", "-P", f"node.name={TAG}x_envgarb",
                           "-P", f"target.object={NS}",
                           "--target", "r87b_no_such_target", str(TONE)],
         {"PIPEWIRE_PROPS": "{ target.object = r87b_no_such }"}),
        ("x_env_vs_nodetarget", ["pw-play", "-P", f"node.name={TAG}x_envnt",
                                 "-P", f"node.target={NS}",
                                 "--target", "r87b_no_such_target", str(TONE)],
         {"PIPEWIRE_PROPS": "{ target.object = %s }" % NS2}),
        ("x_prop_twice", ["pw-play", "-P", f"node.name={TAG}x_ptwice",
                          "-P", f"target.object={NS}",
                          "-P", f"target.object={NS2}", str(TONE)], None),
        ("x_zero_prop", ["pw-play", "-P", f"node.name={TAG}x_zprop",
                         "-P", f"target.object={NS}",
                         "--target", "0", str(TONE)], None),
        ("x_auto_false", ["pw-play", "-P", f"node.name={TAG}x_auto",
                          "-P", "node.autoconnect=false",
                          "--target", NS, str(TONE)], None),
        ("x_nt_vs_flag", ["pw-play", "-P", f"node.name={TAG}x_ntvf",
                          "-P", f"node.target={NS2}",
                          "--target", NS, str(TONE)], None),
    ]
    for leg, args, env in combos:
        nm = [a.split("=", 1)[1] for a in args if a.startswith("node.name=")][0]
        out[leg] = play_leg(nm, args, env=env, observe_s=(1.0, 1.6))
    save("b1x-supplement.json", out)
    print("supplement done")


if __name__ == "__main__":
    main()
