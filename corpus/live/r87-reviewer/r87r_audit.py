#!/usr/bin/env python3
"""r87 reviewer — independent re-derivation of every armed r87 verdict
from receipt data ALONE (no fixture import, no host access).

The law set is re-implemented from the committed code's verdict blocks
(blob sha256 be31da67…), but the checker never imports the fixture: it
reads only measurements.json. Names (NS/NS2/DEF) are re-derived from the
receipt's own argv/consumer/default fields.

Usage: r87r_audit.py <receipt.json> [<receipt.json> ...]
"""
import json
import pathlib
import re
import sys

SOLO_ENV = (0.85, 1.18)
V25_ENV = (0.15, 0.35)
V50_ENV = (0.40, 0.60)
V150_ENV = (1.35, 1.65)
V000_MAX = 200
MUTE_MAX = 128
AMP = 8192
DEAD = "99999999"
STALE_SERIAL = "98765432"


class Audit:
    def __init__(self):
        self.checks = []

    def ok(self, name, cond, detail=""):
        self.checks.append({"check": name, "pass": bool(cond),
                            "detail": str(detail)[:220]})
        return bool(cond)


def consumers(leg):
    out = set()
    for s in leg.get("snaps") or []:
        for e in s.get("edges_out") or []:
            if e.get("in_node"):
                out.add(e["in_node"])
    return sorted(out)


def last_snap(leg):
    for s in reversed(leg.get("snaps") or []):
        if s.get("present"):
            return s
    return (leg.get("snaps") or [{}])[-1]


def blob(rec):
    return (rec.get("stdout") or "") + "\n" + (rec.get("stderr") or "")


def ports_of(snap):
    return snap.get("ports") or {}


def derive_names(m):
    """NS / NS2 / pid from the receipt's own argv + consumer fields."""
    pid = None
    for leg in (m.get("legs") or {}).values():
        if not isinstance(leg, dict):
            continue
        for txt in (leg.get("argv"),):
            if not txt:
                continue
            for mm in re.finditer(r"r87a_(ns2?)_(\d+)", txt):
                pid = pid or mm.group(2)
    for leg in (m.get("legs") or {}).values():
        if not isinstance(leg, dict):
            continue
        for c in leg.get("consumers") or []:
            mm = re.search(r"r87a_ns2?_(\d+)", c)
            if mm:
                pid = pid or mm.group(1)
    if pid is None:
        return None, None, None
    return f"r87a_ns_{pid}", f"r87a_ns2_{pid}", pid


def audit_modes(m, a):
    legs = m["legs"]
    cats = legs["binaries"]["members"]
    for t in ("pw-play", "pw-record", "pw-midiplay", "pw-midirecord"):
        a.ok(f"modes/binaries/{t}-is-pwcat",
             cats[t]["same_as_pwcat"] and
             cats[t]["sha256"] == legs["binaries"]["pw_cat_sha"],
             cats[t])
    for t in ("pw-mididump", "pw-cli"):
        a.ok(f"modes/binaries/{t}-distinct",
             not cats[t]["same_as_pwcat"] and
             cats[t]["sha256"] != legs["binaries"]["pw_cat_sha"], cats[t])
    for name, cls in (("m_bare", "pwcat_mode_required"),
                      ("m_mflag_only", "pwcat_mode_required"),
                      ("m_noflag_target", "pwcat_mode_required"),
                      ("m_capture", "pwcat_unknown_longopt"),
                      ("m_duplex", "pwcat_unknown_longopt"),
                      ("m_clip", "midiclip_read_fail"),
                      ("m_dsd", "dsd_read_fail")):
        l = legs[name]
        a.ok(f"modes/{name}/refusal",
             l.get("exit_code") != 0 and l.get("error_class") == cls and
             not l.get("killed_at_bound"),
             {k: l.get(k) for k in ("exit_code", "error_class",
                                    "killed_at_bound")})
    want = {"m_p_r": "Stream/Input/Audio", "m_r_p": "Stream/Output/Audio",
            "m_p_r_p": "Stream/Output/Audio",
            "m_r_p_r": "Stream/Input/Audio",
            "m_play_r": "Stream/Input/Audio",
            "m_record_p": "Stream/Output/Audio",
            "m_midi_p": "Stream/Output/Midi",
            "m_midi_r": "Stream/Input/Midi",
            "m_ump": "Stream/Output/Midi",
            "m_sysex": "Stream/Output/Midi"}
    want_in = {"m_p_r", "m_r_p_r", "m_play_r"}
    want_out = {"m_r_p", "m_p_r_p", "m_record_p"}
    for name, cls in want.items():
        leg = legs[name]
        snap = last_snap(leg)
        p = ports_of(snap)
        ins = sorted(k for k, d in p.items() if str(d) == "in")
        outs = sorted(k for k, d in p.items() if str(d) == "out")
        has_in = any(k.startswith("input") for k in ins)
        has_out = any(k.startswith("output") for k in outs)
        a.ok(f"modes/{name}/present", snap.get("present"), snap.get("at_s"))
        a.ok(f"modes/{name}/media_class", snap.get("media_class") == cls,
             snap.get("media_class"))
        a.ok(f"modes/{name}/never-duplex", not (has_in and has_out),
             {"in": ins, "out": outs})
        if name in want_in:
            a.ok(f"modes/{name}/input_ports", has_in, ins)
        if name in want_out:
            a.ok(f"modes/{name}/output_ports", has_out, outs)
        if name == "m_midi_r":
            a.ok(f"modes/{name}/input_1", "input_1" in ins, ins)
        if name == "m_midi_p":
            a.ok(f"modes/{name}/output_1", "output_1" in outs, outs)
        if name == "m_sysex":
            a.ok(f"modes/{name}/not-exited-clean",
                 leg.get("exit_code") != 0,
                 {"rc": leg.get("exit_code"),
                  "exited_before_observe": leg.get("exited_before_observe")})


def audit_target(m, a):
    legs = m["legs"]
    NS, NS2, pid = derive_names(m)
    DEF = m.get("default_sink_at_start")
    a.ok("target/names-derived", NS is not None and NS2 is not None,
         {"NS": NS, "NS2": NS2, "pid": pid, "DEF": DEF})
    a.ok("target/default-stable",
         m.get("default_sink_at_end") == DEF,
         [DEF, m.get("default_sink_at_end")])
    want = {"p_own": [NS], "p_cat": [NS], "p_garbage": [DEF],
            "p_pb1": [DEF], "p_pb2": [NS], "p_pb3": [NS2], "p_nt": [NS],
            "p_nt_vs_flag": [NS], "p_nt_rev": [NS2], "p_nt_garbage": [DEF],
            "p_three": [NS2], "p_prop_twice": [NS2], "p_serial": [NS],
            "p_objid": [DEF], "p_serial_stale": [DEF],
            "p_prop_serial": [NS], "p_prop_objid": [DEF], "p_mon": [DEF],
            "p_mon_cs": [DEF], "p_src_name": [DEF], "p_src_serial": [DEF],
            "p_env": [NS], "p_env_nobrace": [NS], "p_env_vs_prop": [NS],
            "p_env_garbage": [DEF], "p_mediarole": [DEF],
            "p_capsink": [DEF], "p_empty": [DEF], "p_coll": [NS]}
    for name, exp in want.items():
        got = consumers(legs[name])
        a.ok(f"target/{name}/consumers", got == exp, {"got": got,
                                                      "want": exp})
    for name in ("p_zero", "p_zero_prop", "p_noauto"):
        leg = legs[name]
        got = consumers(leg)
        present = any(s.get("present") for s in leg.get("snaps") or [])
        a.ok(f"target/{name}/hard-no-link", not got and present,
             {"consumers": got, "present": present})
    coll_ports = [e.get("in_port_name")
                  for s in legs["p_coll"].get("snaps") or []
                  for e in s.get("edges_out") or []]
    a.ok("target/p_coll/playback-ports",
         bool(coll_ports) and all(str(p).startswith("playback_")
                                  for p in coll_ports), coll_ports)
    a.ok("target/p_coll/collision-present",
         len(legs.get("collision_objects") or []) >= 2,
         legs.get("collision_objects"))
    # the encoded boundary correction, re-stated as data laws
    a.ok("target/law/flag-beats-node.target-both-directions",
         consumers(legs["p_nt_vs_flag"]) == [NS] and
         consumers(legs["p_nt_rev"]) == [NS2],
         {"a": consumers(legs["p_nt_vs_flag"]),
          "b": consumers(legs["p_nt_rev"])})
    a.ok("target/law/garbage-flag-no-fallthrough",
         consumers(legs["p_nt_garbage"]) == [DEF],
         consumers(legs["p_nt_garbage"]))
    a.ok("target/law/prop-beats-flag-both-directions",
         consumers(legs["p_pb1"]) == [DEF] and
         consumers(legs["p_pb2"]) == [NS])
    a.ok("target/law/env-beats-prop",
         consumers(legs["p_env_vs_prop"]) == [NS])
    a.ok("target/law/serial-resolves-object.id-never",
         consumers(legs["p_serial"]) == [NS] and
         consumers(legs["p_prop_serial"]) == [NS] and
         consumers(legs["p_objid"]) == [DEF] and
         consumers(legs["p_prop_objid"]) == [DEF] and
         consumers(legs["p_serial_stale"]) == [DEF])


def audit_cli(m, a):
    legs = m["legs"]
    c = legs["cold_nowarm"]
    cb = blob(c)
    a.ok("cli/cold_nowarm/unknown-global", "unknown global" in cb,
         c.get("error_class"))
    nid = str((m.get("ns_leaf") or {}).get("node_id"))
    a.ok("cli/cold_nowarm/exact-live-id",
         f"unknown global '{nid}'" in cb,
         {"ns_leaf_id": nid,
          "stderr_head": (c.get("stderr_head") or [])[:1]})
    w = legs["warm_control"]
    a.ok("cli/warm_control/ok",
         w.get("exit_code") == 0 and "id:" in (w.get("stdout") or ""),
         w.get("exit_code"))
    for v, l in legs["unknowns"].items():
        b = blob(l)
        a.ok(f"cli/unknowns/{v}",
             DEAD in b and "unknown global" in b, l.get("error_class"))
    a.ok("cli/tap_link/validated", bool(legs["tap_link"]["edges"]),
         len(legs["tap_link"]["edges"]))
    regs = legs.get("regions") or {}
    solo = (regs.get("solo") or {}).get("median_peak")

    def ratio(name):
        v = (regs.get(name) or {}).get("median_peak")
        return (v / solo) if (v is not None and solo) else None

    a.ok("cli/dsp/solo-reference",
         solo is not None and SOLO_ENV[0] * AMP <= solo <= SOLO_ENV[1] * AMP,
         solo)
    if solo is not None:
        for name, env in (("vol25", V25_ENV), ("restore", SOLO_ENV),
                          ("unmute", SOLO_ENV)):
            r = ratio(name)
            a.ok(f"cli/dsp/{name}-envelope",
                 r is not None and env[0] <= r <= env[1],
                 {"ratio": r, "env": env})
        mv = (regs.get("mute") or {}).get("median_peak")
        a.ok("cli/dsp/mute", mv is not None and mv <= MUTE_MAX, mv)
        for wn in ("w_v25", "w_v10", "w_mute", "w_unmute"):
            a.ok(f"cli/dsp/{wn}-rc0",
                 (legs.get("writes") or {}).get(wn, {}).get("exit_code") == 0,
                 (legs.get("writes") or {}).get(wn, {}).get("exit_code"))
    if legs.get("props_unk") is not None:
        pu = legs["props_unk"]
        a.ok("cli/props_unk/silent-drop",
             pu.get("exit_code") == 0 and not pu.get("errors"),
             pu.get("errors"))
    for scope, key in (("fmt_stream", "post_valid"),
                       ("fmt_stream", "post_empty"),
                       ("fmt_sink", "post_valid")):
        f = legs.get(scope) or {}
        pre = fmt_of(f.get("pre") or {})
        post = fmt_of(f.get(key) or {})
        a.ok(f"cli/{scope}/{key}-seal",
             pre.get("rate") is not None and post == pre,
             {"pre": pre, "post": post})
    fu = legs.get("fmt_unlinked") or {}
    if fu:
        ef = blob(fu["enum_fmt"])
        ep = blob(fu["enum_props"])
        a.ok("cli/fmt_unlinked/format-res-2", "res:-2" in ef,
             ef[-120:])
        a.ok("cli/fmt_unlinked/props-read",
             "Object:" in ep and "res:-" not in ep, ep[-120:])
    sc = legs.get("sendcmd") or {}
    a.ok("cli/sendcmd/Suspend",
         (sc.get("Suspend") or {}).get("state_after") == "suspended",
         (sc.get("Suspend") or {}).get("state_after"))
    a.ok("cli/sendcmd/Resume-refused",
         "unknown node command type: Resume" in
         ((sc.get("Resume") or {}).get("cmd") or {}).get("stderr", ""))
    st = sc.get("Start") or {}
    a.ok("cli/sendcmd/Start-noop",
         not (st.get("cmd") or {}).get("errors") and
         st.get("state_after") == "suspended",
         {"state": st.get("state_after"),
          "errors": (st.get("cmd") or {}).get("errors")})
    a.ok("cli/sendcmd/Pause",
         (sc.get("Pause") or {}).get("state_after") == "suspended")
    for k in ("0", "bogus-cmd"):
        a.ok(f"cli/sendcmd/{k}-unknown",
             "unknown node command type" in
             ((sc.get(k) or {}).get("cmd") or {}).get("stderr", ""))
    a.ok("cli/sendcmd/no_args-usage",
         bool(((sc.get("no_args") or {}).get("cmd") or {}).get("errors")))
    a.ok("cli/latency/res-95", "res:-95" in (legs.get("latency") or
                                             {}).get("stderr", ""))
    fo = legs.get("foreign") or {}
    if fo:
        allerr = (fo["write_samevalue"].get("errors") or []) + \
            (fo["write_unk"].get("errors") or []) + \
            (fo["enum_pre"].get("errors") or []) + \
            (fo["enum_post"].get("errors") or [])
        a.ok("cli/foreign/no-gate-errors", not allerr, allerr)
        a.ok("cli/foreign/identical-value-unchanged",
             fo.get("volume_read") is not None and
             fo.get("volume_after") == fo.get("volume_read"),
             {"read": fo.get("volume_read"),
              "after": fo.get("volume_after")})
        a.ok("cli/foreign/bogus-type-refused",
             "unknown param type" in blob(fo["write_bogus"]))
    ds = legs.get("destroy_stream") or {}
    if ds:
        a.ok("cli/destroy_stream/unconnected-exit",
             ds.get("play_rc") == 1 and
             "unconnected" in (ds.get("play_err") or ""),
             {"rc": ds.get("play_rc"), "err": ds.get("play_err")})
        a.ok("cli/destroy_stream/node-gone", not ds.get("node_after"))
    cs = legs.get("create_session") or {}
    a.ok("cli/create_session/session-bound",
         cs.get("present_in_session") and not cs.get("present_after_quit"),
         {k: cs.get(k) for k in ("present_in_session",
                                 "present_after_quit")})
    cl = legs.get("create_linger") or {}
    a.ok("cli/create_linger/linger-carveout",
         cl.get("present_after_quit") and
         not cl.get("present_after_destroy"),
         {k: cl.get(k) for k in ("present_after_quit",
                                 "present_after_destroy")})
    bf = legs.get("create_badfac") or {}
    a.ok("cli/create_badfac/res-2", "res:-2" in (bf.get("log_tail") or ""),
         (bf.get("log_tail") or "")[-100:])
    cu = legs.get("create_usage") or {}
    a.ok("cli/create_usage/usage",
         "usage: factory.name=" in (cu.get("log_tail") or "") or
         "res:-22" in (cu.get("log_tail") or ""),
         (cu.get("log_tail") or "")[-100:])
    dk = legs.get("destroy_sink_module") or {}
    a.ok("cli/destroy_sink_module/module-gone",
         dk.get("sink_listed_after") is False and not dk.get("node_after"),
         {k: dk.get(k) for k in ("sink_listed_after", "node_after")})
    if legs["vol_tap_link"]["edges"]:
        vm = legs.get("volume_legs") or {}
        base = (vm.get("v100") or {}).get("median_peak")
        a.ok("cli/volume/v100-reference",
             base is not None and
             SOLO_ENV[0] * AMP <= base <= SOLO_ENV[1] * AMP, base)
        if base:
            for vk, env in (("v050", V50_ENV), ("v150", V150_ENV)):
                r = (vm.get(vk) or {}).get("ratio_vs_v100")
                a.ok(f"cli/volume/{vk}-ratio",
                     r is not None and env[0] <= r <= env[1],
                     {"ratio": r, "env": env})
            mv = (vm.get("v000") or {}).get("median_peak")
            a.ok("cli/volume/v000-zero", mv is not None and mv <= V000_MAX,
                 mv)


def fmt_of(rec):
    s = blob(rec)
    rate = re.search(r"Format:Audio:rate \(65539\).*?Int (\d+)", s, re.S)
    fid = re.search(r"Format:Audio:format \(65537\).*?Id (\d+)", s, re.S)
    return {"rate": int(rate.group(1)) if rate else None,
            "format_id": int(fid.group(1)) if fid else None}


def audit_midi(m, a):
    legs = m["legs"]
    for name in ("m_t_bridge", "m_t_serial", "m_t_objid", "m_t_garbage",
                 "m_t_prop", "m_t_nt"):
        l = legs.get(name)
        if l is None:
            continue
        b = blob(l)
        a.ok(f"midi/{name}/dead-target",
             l.get("exit_code") != 0 and
             "no target node available" in b and "res:-2" in b,
             {"rc": l.get("exit_code"), "class": l.get("error_class")})
    for name in ("m_t_zero", "m_noauto"):
        leg = legs[name]
        snap = last_snap(leg)
        got = consumers(leg)
        a.ok(f"midi/{name}/publish-unlinked",
             snap.get("present") and not got and
             snap.get("media_class") == "Stream/Output/Midi",
             {"present": snap.get("present"), "links": got,
              "class": snap.get("media_class")})
    pin = legs["pin"]
    if pin.get("file"):
        f = pin["file"]
        pl = pin.get("pwlink") or {}
        a.ok("midi/pin/pwlink-rc0", pl.get("exit_code") == 0,
             pl.get("exit_code"))
        a.ok("midi/pin/45B-real-events",
             f.get("has_mthd") and (f.get("bytes") or 0) >= 40 and
             all(f.get("note_ons") or []) and
             any(f.get("note_offs") or []),
             {"bytes": f.get("bytes"), "ons": f.get("note_ons"),
              "offs": f.get("note_offs")})
        a.ok("midi/pin/record-rc", pin.get("record_rc") != 0,
             pin.get("record_rc"))
    else:
        a.ok("midi/pin/coverage-marker",
             bool(m.get("coverage_blocked")), m.get("coverage_blocked"))
    sk = legs["skeleton"]["file"]
    a.ok("midi/skeleton/26B-no-payload",
         legs["skeleton"].get("rc") != 0 and sk.get("has_mthd") and
         20 <= (sk.get("bytes") or 0) <= 34 and
         not any(sk.get("note_ons") or []),
         {"rc": legs["skeleton"].get("rc"), "file": sk})
    md = legs["mdump_off"]
    a.ok("midi/mdump_off/offline-parse",
         md.get("exit_code") == 0 and "Note On" in (md.get("stdout") or ""),
         md.get("exit_code"))
    live = (legs.get("mdump_live") or {}).get("attempts") or []
    noted = [x for x in live if x.get("node")]
    if live and not noted:
        a.ok("midi/mdump_live/coverage-marker",
             bool(m.get("coverage_blocked")), m.get("coverage_blocked"))
    elif noted:
        a.ok("midi/mdump_live/note-lines",
             any("Note On" in (x.get("stdout") or "") for x in noted),
             [x.get("stdout", "")[:40] for x in noted])
    for name in ("pactl_raop", "pactl_zc", "pactl_bogus"):
        l = legs[name]
        a.ok(f"midi/{name}/no-such-entity",
             l.get("exit_code") != 0 and
             "Failure: No such entity" in blob(l), l.get("exit_code"))
    for name in ("pwcli_raop", "pwcli_zc", "pwcli_null", "pwcli_panull"):
        a.ok(f"midi/{name}/could-not-load",
             "Could not load module" in blob(legs[name]))
    for name in ("remote_flag", "remote_env", "remote_cli"):
        l = legs[name]
        a.ok(f"midi/{name}/host-down",
             l.get("exit_code") != 0 and "Host is down" in blob(l),
             l.get("exit_code"))
    cen = legs["remote_census"]
    a.ok("midi/remote_census/no-remote-nodes",
         not cen["remote_named_nodes"], cen["remote_named_nodes"])
    a.ok("midi/remote_census/no-raop-modules",
         not cen["net_modules"], cen["net_modules"])


def audit_teardown(m, a, scope):
    for key in ("sinks_gone", "own_nodes_after"):
        v = m.get(key)
        if key == "sinks_gone":
            if isinstance(v, dict):
                # the fixture's arm is `all(gone.values())`; an entry that
                # loaded no sink has {} and is vacuously clean (recorded)
                a.ok(f"{scope}/teardown/sinks-gone",
                     all(v.values()), {"sinks_gone": v})
            else:
                a.ok(f"{scope}/teardown/sinks-gone",
                     v == "reader_error" and
                     bool(m.get("coverage_blocked")), v)
        else:
            if isinstance(v, list):
                a.ok(f"{scope}/teardown/own-nodes-after", v == [], v)
            else:
                a.ok(f"{scope}/teardown/own-nodes-after",
                     v == "reader_error" and
                     bool(m.get("coverage_blocked")), v)


def audit_receipt(path):
    d = json.load(open(path))
    ms = d["measurements"]
    a = Audit()
    out = {}
    for key, fn in (("pwbind_modes_r87_probe", audit_modes),
                    ("pwbind_target_r87_probe", audit_target),
                    ("pwbind_cli_r87_probe", audit_cli),
                    ("pwbind_midi_r87_probe", audit_midi)):
        m = ms.get(key)
        if m is None:
            a.ok(f"{key}/present", False)
            continue
        fn(m, a)
        audit_teardown(m, a, key.replace("pwbind_", "").replace(
            "_r87_probe", ""))
    npass = sum(1 for c in a.checks if c["pass"])
    nfail = len(a.checks) - npass
    out = {"receipt": str(path), "mode": d.get("mode"),
           "checks": len(a.checks), "pass": npass, "fail": nfail,
           "failures": [c for c in a.checks if not c["pass"]],
           "entry_failures": {k: (v.get("failures") or [])
                              for k, v in ms.items()
                              if k.startswith("pwbind_")},
           "entry_coverage_blocked": {
               k: v.get("coverage_blocked") for k, v in ms.items()
               if k.startswith("pwbind_") and v.get("coverage_blocked")}}
    return out


if __name__ == "__main__":
    res = [audit_receipt(p) for p in sys.argv[1:]]
    print(json.dumps(res, indent=1))
    print("SUMMARY:", [(r["receipt"].split("/")[-2], r["pass"], r["fail"])
                       for r in res])
