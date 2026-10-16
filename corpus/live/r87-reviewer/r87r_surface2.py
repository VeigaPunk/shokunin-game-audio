#!/usr/bin/env python3
"""r87 reviewer — curated verdict surface (volatile-free).

Extracts exactly the values the r87 verdicts read, per entry, so two
receipts can be compared field-by-field without id/timing noise.
Derived booleans are computed, never raw log text.
"""
import json
import re
import sys


def blob(r):
    return (r.get("stdout") or "") + (r.get("stderr") or "")


def fmt_of(r):
    s = blob(r)
    rate = re.search(r"Format:Audio:rate \(65539\).*?Int (\d+)", s, re.S)
    fid = re.search(r"Format:Audio:format \(65537\).*?Id (\d+)", s, re.S)
    return {"rate": int(rate.group(1)) if rate else None,
            "format_id": int(fid.group(1)) if fid else None}


def surfaces(path):
    d = json.load(open(path))
    ms = d["measurements"]
    out = {}
    for k, v in ms.items():
        if not k.startswith("pwbind_"):
            continue
        legs = v.get("legs") or {}
        s = {"failures": len(v.get("failures") or []),
             "coverage_blocked": len(v.get("coverage_blocked") or []),
             "blocked": v.get("blocked") is not None,
             "sinks_gone_all": (all((v.get("sinks_gone") or {}).values())
                                if isinstance(v.get("sinks_gone"), dict)
                                else v.get("sinks_gone")),
             "own_nodes_after": (v.get("own_nodes_after")
                                 if not isinstance(v.get("own_nodes_after"),
                                                   list)
                                 else len(v["own_nodes_after"]))}
        if k == "pwbind_modes_r87_probe":
            s["binaries"] = {t: m["same_as_pwcat"] for t, m in
                             legs["binaries"]["members"].items()}
            s["pwcat_sha"] = legs["binaries"]["pw_cat_sha"]
            for name in ("m_bare", "m_mflag_only", "m_noflag_target",
                         "m_capture", "m_duplex", "m_clip", "m_dsd"):
                l = legs[name]
                s[name] = [l.get("exit_code"), l.get("error_class"),
                           bool(l.get("killed_at_bound"))]
            for name in ("m_p_r", "m_r_p", "m_p_r_p", "m_r_p_r",
                         "m_play_r", "m_record_p", "m_midi_p",
                         "m_midi_r", "m_ump", "m_sysex"):
                l = legs[name]
                s[name] = {
                    "classes": [x.get("media_class")
                                for x in l.get("snaps") or []],
                    "present": [bool(x.get("present"))
                                for x in l.get("snaps") or []],
                    "ports": [sorted((x.get("ports") or {}).keys())
                              for x in l.get("snaps") or []],
                    "dirs": [sorted({d2 for d2 in
                                     (x.get("ports") or {}).values()})
                             for x in l.get("snaps") or []],
                    "exited_before_observe":
                        bool(l.get("exited_before_observe")),
                    "rc_nonzero": l.get("exit_code") != 0,
                    "recorded_file": (l.get("recorded_file") or {}
                                      ).get("exists")}
        elif k == "pwbind_target_r87_probe":
            s["default_stable"] = (v.get("default_sink_at_start") ==
                                   v.get("default_sink_at_end"))
            s["collision_classes"] = sorted(
                o.get("media_class") for o in
                (legs.get("collision_objects") or []))
            for name, l in legs.items():
                if name == "collision_objects":
                    continue
                s[name] = sorted(l.get("consumers") or [])
            s["ports_by_leg"] = {
                name: sorted((l.get("last") or {}).get("ports") or [])
                for name, l in legs.items()
                if isinstance(l, dict) and l.get("last")}
        elif k == "pwbind_cli_r87_probe":
            regs = legs.get("regions") or {}
            s["regions"] = {n: (regs.get(n) or {}).get("median_peak")
                            for n in ("solo", "vol25", "restore", "mute",
                                      "unmute")}
            s["writes_rc"] = {n: (legs.get("writes") or {}).get(n, {}
                               ).get("exit_code")
                              for n in ("w_v25", "w_v10", "w_mute",
                                        "w_unmute", "w_unk")}
            s["props_unk"] = [legs["props_unk"].get("exit_code"),
                              len(legs["props_unk"].get("errors") or [])] \
                if legs.get("props_unk") else None
            for scope in ("fmt_stream", "fmt_sink"):
                f = legs.get(scope) or {}
                s[scope] = {kk: fmt_of(f.get(kk) or {})
                            for kk in ("pre", "post_valid", "post_empty")
                            if kk in f}
            fu = legs.get("fmt_unlinked") or {}
            s["fmt_unlinked"] = {
                "fmt_res_minus2": "res:-2" in blob(fu.get("enum_fmt") or {}),
                "props_object": "Object:" in blob(
                    fu.get("enum_props") or {}),
                "props_no_res": "res:-" not in blob(
                    fu.get("enum_props") or {})} if fu else None
            s["sendcmd"] = {c: (legs["sendcmd"][c].get("state_after"),
                                len((legs["sendcmd"][c].get("cmd") or {}
                                     ).get("errors") or []))
                            for c in ("Suspend", "Resume", "Start", "Pause",
                                      "0", "bogus-cmd", "no_args")}
            s["latency_res95"] = "res:-95" in (
                legs.get("latency") or {}).get("stderr", "")
            fo = legs.get("foreign") or {}
            s["foreign"] = {
                "vol_read": fo.get("volume_read"),
                "vol_after": fo.get("volume_after"),
                "err_counts": [len(fo.get(k, {}).get("errors") or [])
                               for k in ("write_samevalue", "write_unk",
                                         "enum_pre", "enum_post")],
                "bogus_type": "unknown param type" in blob(
                    fo.get("write_bogus") or {})} if fo else None
            ds = legs.get("destroy_stream") or {}
            s["destroy_stream"] = [ds.get("play_rc"),
                                   "unconnected" in (ds.get("play_err")
                                                     or ""),
                                   bool(ds.get("node_after"))]
            s["create_session"] = [bool(legs["create_session"].get(
                "present_in_session")),
                bool(legs["create_session"].get("present_after_quit"))]
            cl = legs.get("create_linger") or {}
            s["create_linger"] = [bool(cl.get("present_after_quit")),
                                  bool(cl.get("present_after_destroy"))]
            s["create_badfac"] = {
                "refusal_in_tail": "res:-2" in (legs["create_badfac"].get(
                    "log_tail") or ""),
                "refusal_in_errors": any(
                    "res:-2" in e for e in
                    legs["create_badfac"].get("errors") or [])}
            s["create_usage"] = {
                "usage_in_tail": ("usage: factory.name=" in
                                  (legs["create_usage"].get("log_tail")
                                   or "") or
                                  "res:-22" in
                                  (legs["create_usage"].get("log_tail")
                                   or ""))}
            dk = legs.get("destroy_sink_module") or {}
            s["destroy_sink_module"] = [dk.get("sink_listed_after"),
                                        bool(dk.get("node_after"))]
            s["tap_link_edges"] = len((legs.get("tap_link") or {}).get(
                "edges") or [])
            s["vol_tap_edges"] = len((legs.get("vol_tap_link") or {}).get(
                "edges") or [])
            s["volume"] = {n: [(vm.get("median_peak")),
                               vm.get("ratio_vs_v100")]
                           for n, vm in (legs.get("volume_legs") or {}
                                         ).items()}
            s["player_exit"] = legs.get("player_exit")
            s["wake_state"] = (legs.get("wake_after_suspend") or {}
                               ).get("state_after")
        elif k == "pwbind_midi_r87_probe":
            for name in ("m_t_bridge", "m_t_serial", "m_t_objid",
                         "m_t_garbage", "m_t_prop", "m_t_nt",
                         "pactl_raop", "pactl_zc", "pactl_bogus",
                         "pwcli_raop", "pwcli_zc", "pwcli_null",
                         "pwcli_panull", "remote_flag", "remote_env",
                         "remote_cli"):
                l = legs.get(name)
                if l is None:
                    continue
                s[name] = [l.get("exit_code"), l.get("error_class")]
            for name in ("m_t_zero", "m_noauto"):
                l = legs[name]
                s[name] = [bool(any(x.get("present")
                                    for x in l.get("snaps") or [])),
                           sorted(l.get("consumers") or []),
                           (l.get("last") or {}).get("media_class")]
            pin = legs.get("pin") or {}
            pf = pin.get("file") or {}
            s["pin"] = [pf.get("exists"), pf.get("bytes"),
                        pf.get("note_ons"), pf.get("note_offs"),
                        (pin.get("pwlink") or {}).get("exit_code")]
            sk = legs.get("skeleton") or {}
            s["skeleton"] = [sk.get("rc"), (sk.get("file") or {}).get(
                "bytes"), (sk.get("file") or {}).get("note_ons")]
            s["mdump_off"] = [legs["mdump_off"].get("exit_code"),
                              "Note On" in (legs["mdump_off"].get("stdout")
                                            or "")]
            s["mdump_live"] = [(x.get("node"),
                                "Note On" in (x.get("stdout") or ""))
                               for x in (legs.get("mdump_live") or {}
                                         ).get("attempts") or []]
            cen = legs.get("remote_census") or {}
            s["remote_census"] = [len(cen.get("remote_named_nodes") or []),
                                  cen.get("module_dir_count"),
                                  len(cen.get("net_modules") or [])]
            s["bridge_present"] = bool(v.get("bridge"))
        out[k] = s
    return out


def flat(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(d, list):
        out[prefix] = json.dumps(d)
    else:
        out[prefix] = d
    return out


if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    fa, fb = flat(surfaces(a)), flat(surfaces(b))
    keys = sorted(set(fa) | set(fb))
    diffs = [{"key": k, "a": fa.get(k), "b": fb.get(k)}
             for k in keys if fa.get(k) != fb.get(k)]
    print(json.dumps({"a": a, "b": b, "keys": len(keys),
                      "diffs": len(diffs), "diff_keys": diffs}, indent=1))
