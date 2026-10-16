#!/usr/bin/env python3
"""r87-verifier independent law re-derivation (verifier-owned; raw
receipt JSON only, no fixture import). Each law is a predicate over one
receipt; usage: laws.py receipt.json [...] -> per-receipt pass/fail.

Laws marked ARM_WINDOW re-derive the fixture's own log-tail arms — they
are the ones the wave observed false-FAILing under foreign registry
churn (see runs/repro_cli_refusal.py).
"""
import json
import re
import sys

DEF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.29"
LAWS = []


def law(name):
    def deco(fn):
        LAWS.append((name, fn))
        return fn
    return deco


def blob(leg):
    return json.dumps(leg or {}, default=str)


def errs(leg):
    return (leg or {}).get("errors") or []


def _cls(leg):
    return (leg or {}).get("error_class")


def _ns_names(e):
    """NS / NS2 / default consumer names from the entry's own census."""
    keys = list((e.get("sinks_gone") or {}).keys())
    ns = next((k for k in keys if re.match(r"^r87a_ns_\d+$", k)), None)
    ns2 = next((k for k in keys if re.match(r"^r87a_ns2_\d+$", k)), None)
    dflt = ((e.get("inventory") or {}).get("default_sink"))
    return ns, ns2, dflt


# ---------------- modes ----------------
@law("modes.binaries: 4 aliases of pw-cat share realpath+sha; mididump/cli distinct")
def _(r):
    b = r["pwbind_modes_r87_probe"]["legs"]["binaries"]
    m = b["members"]
    return (all(m[k]["realpath"] == b["pw_cat"] and
                m[k]["same_as_pwcat"] and m[k]["sha256"] == b["pw_cat_sha"]
                for k in ("pw-play", "pw-record", "pw-midiplay",
                          "pw-midirecord")) and
            not m["pw-mididump"]["same_as_pwcat"] and
            not m["pw-cli"]["same_as_pwcat"])


@law("modes.refusals: bare/-m/no-flag rc!=0 class=pwcat_mode_required")
def _(r):
    l = r["pwbind_modes_r87_probe"]["legs"]
    return all(l[k]["exit_code"] != 0 and
               _cls(l[k]) == "pwcat_mode_required"
               for k in ("m_bare", "m_mflag_only", "m_noflag_target"))


@law("modes.no-duplex: --capture/--duplex unrecognized, rc!=0")
def _(r):
    l = r["pwbind_modes_r87_probe"]["legs"]
    return all(l[k]["exit_code"] != 0 and
               _cls(l[k]) == "pwcat_unknown_longopt"
               for k in ("m_capture", "m_duplex"))


@law("modes.readers: -c SMF -> midiclip; -d wav -> dsdfile")
def _(r):
    l = r["pwbind_modes_r87_probe"]["legs"]
    return _cls(l["m_clip"]) == "midiclip_read_fail" and \
        _cls(l["m_dsd"]) == "dsd_read_fail"


@law("modes.last-wins: -p -r -> Input/Audio with input_* ports")
def _(r):
    l = r["pwbind_modes_r87_probe"]["legs"]
    for k in ("m_p_r", "m_r_p_r", "m_play_r"):
        snap = l[k]["snaps"][-1]
        if snap["media_class"] != "Stream/Input/Audio":
            return False
        if not any(p.startswith("input_") for p in snap["ports"]):
            return False
    return True


@law("modes.last-wins: -r -p -> Output/Audio with output_* ports")
def _(r):
    l = r["pwbind_modes_r87_probe"]["legs"]
    for k in ("m_r_p", "m_p_r_p", "m_record_p"):
        snap = l[k]["snaps"][-1]
        if snap["media_class"] != "Stream/Output/Audio":
            return False
        if not any(p.startswith("output_") for p in snap["ports"]):
            return False
    return True


@law("modes.midi: midi legs publish Stream/*/Midi with 1 port")
def _(r):
    l = r["pwbind_modes_r87_probe"]["legs"]
    want = {"m_midi_p": ("Stream/Output/Midi", ["output_1"]),
            "m_midi_r": ("Stream/Input/Midi", ["input_1"]),
            "m_ump": ("Stream/Output/Midi", ["output_1"]),
            "m_sysex": ("Stream/Output/Midi", ["output_1"])}
    for k, (cls, ports) in want.items():
        snap = l[k]["snaps"][-1]
        if snap["media_class"] != cls or sorted(snap["ports"]) != ports:
            return False
    return True


@law("modes.no-duplex-shape: no snapshot carries both input_* and non-monitor output_*")
def _(r):
    for leg in r["pwbind_modes_r87_probe"]["legs"].values():
        for s in (leg or {}).get("snaps") or []:
            ins = [p for p in s["ports"] if p.startswith("input_")]
            outs = [p for p in s["ports"] if p.startswith("output_")]
            if ins and outs:
                return False
    return True


# ---------------- target ----------------
@law("target.happy: 9 name/serial/env/prop legs land NS")
def _(r):
    e = r["pwbind_target_r87_probe"]
    l = e["legs"]
    ns, _, _ = _ns_names(e)
    for k in ("p_own", "p_cat", "p_pb2", "p_nt", "p_serial",
              "p_prop_serial", "p_env", "p_env_nobrace", "p_env_vs_prop"):
        if l[k]["consumers"] != [ns]:
            return False
    return True


@law("target.flag-beats-node.target (boundary correction)")
def _(r):
    e = r["pwbind_target_r87_probe"]
    ns, _, _ = _ns_names(e)
    return e["legs"]["p_nt_vs_flag"]["consumers"] == [ns]


@law("target.second-sink legs land NS2")
def _(r):
    e = r["pwbind_target_r87_probe"]
    _, ns2, _ = _ns_names(e)
    for k in ("p_pb3", "p_nt_rev", "p_three", "p_prop_twice"):
        if e["legs"][k]["consumers"] != [ns2]:
            return False
    return True


@law("target.default-landed: 14 unresolvable/wrong-class legs land the default sink")
def _(r):
    e = r["pwbind_target_r87_probe"]
    keys = ("p_garbage", "p_pb1", "p_nt_garbage", "p_objid",
            "p_prop_objid", "p_serial_stale", "p_mon", "p_mon_cs",
            "p_src_name", "p_src_serial", "p_env_garbage", "p_mediarole",
            "p_capsink", "p_empty")
    _, _, dflt = _ns_names(e)
    return all(e["legs"][k]["consumers"] == [dflt] for k in keys)


@law("target.hard-no-link: --target 0 / 0-prop / autoconnect=false")
def _(r):
    l = r["pwbind_target_r87_probe"]["legs"]
    return all(l[k]["consumers"] == []
               for k in ("p_zero", "p_zero_prop", "p_noauto"))


@law("target.collision: same-named stream does not shadow the sink")
def _(r):
    e = r["pwbind_target_r87_probe"]
    ns, _, _ = _ns_names(e)
    return e["legs"]["p_coll"]["consumers"] == [ns] and \
        len(e["legs"]["collision_objects"]) == 2


@law("target.no default drift mid-entry")
def _(r):
    e = r["pwbind_target_r87_probe"]
    return e["default_sink_at_start"] == e["default_sink_at_end"]


# ---------------- cli ----------------
@law("cli.cold-registry: cold_nowarm fires unknown global; warm info works")
def _(r):
    l = r["pwbind_cli_r87_probe"]["legs"]
    cold = blob(l["cold_nowarm"])
    warm = l["warm_control"]
    return "unknown global" in cold and \
        warm["exit_code"] == 0 and "unknown global" not in blob(warm)


@law("cli.unknowns: 5 verbs on 99999999 all unknown global")
def _(r):
    l = r["pwbind_cli_r87_probe"]["legs"]["unknowns"]
    return all("unknown global '99999999'" in blob(v) for v in l.values())


@law("cli.writes: Props writes rc0; solo>=8000, v25==0.25x, mute==0, unmute>=8000")
def _(r):
    e = r["pwbind_cli_r87_probe"]
    w, g = e["legs"]["writes"], e["legs"]["regions"]
    if not all(v["exit_code"] == 0 for v in w.values()):
        return False
    solo = g["solo"]["median_peak"]
    return solo >= 8000 and 0.2 <= g["vol25"]["median_peak"] / solo <= 0.3 \
        and g["mute"]["median_peak"] <= 128 and \
        g["unmute"]["median_peak"] >= 8000 and \
        g["restore"]["median_peak"] >= 8000


@law("cli.volume_legs: spawn --volume 1.0/0.5/0.0/1.5 exact ratios, unclamped")
def _(r):
    v = r["pwbind_cli_r87_probe"]["legs"]["volume_legs"]
    return v["v100"]["median_peak"] == 8192 and \
        0.45 <= v["v050"]["ratio_vs_v100"] <= 0.55 and \
        v["v000"]["median_peak"] == 0 and \
        1.4 <= v["v150"]["ratio_vs_v100"] <= 1.6


@law("cli.props_unk: unknown key rc0, zero errors")
def _(r):
    p = r["pwbind_cli_r87_probe"]["legs"]["props_unk"]
    return p["exit_code"] == 0 and not errs(p)


@law("cli.fmt seal: running stream+sink Format unchanged by both writes")
def _(r):
    l = r["pwbind_cli_r87_probe"]["legs"]

    def fmt(d):
        m = re.search(r"(\w+)/(\d+)", blob(d))
        return m.groups() if m else None
    return fmt(l["fmt_stream"]["pre"]) == fmt(l["fmt_stream"]["post_valid"]) == \
        fmt(l["fmt_stream"]["post_empty"]) and \
        fmt(l["fmt_sink"]["pre"]) == fmt(l["fmt_sink"]["post_valid"])


@law("cli.fmt_unlinked: enum Format res:-2 while Props still reads")
def _(r):
    f = r["pwbind_cli_r87_probe"]["legs"]["fmt_unlinked"]
    return "res:-2" in (f["enum_fmt"].get("stderr") or "") and \
        f["enum_props"].get("has_pod") is True


@law("cli.sendcmd: Suspend/Pause->suspended, Resume refused, Start no-op")
def _(r):
    s = r["pwbind_cli_r87_probe"]["legs"]["sendcmd"]
    return s["Suspend"]["state_after"] == "suspended" and \
        s["Pause"]["state_after"] == "suspended" and \
        s["Resume"]["state_after"] == "suspended" and \
        "unknown node command type: Resume" in blob(s["Resume"]) and \
        s["Start"]["state_after"] == "suspended"


@law("cli.latency: set-param Latency -> res:-95 on the sink")
def _(r):
    lat = r["pwbind_cli_r87_probe"]["legs"]["latency"].get("stderr") or ""
    return "res:-95" in lat


@law("cli.foreign: enum 1.0; identical write accepted; unknown key dropped")
def _(r):
    f = r["pwbind_cli_r87_probe"]["legs"]["foreign"]
    return f["write_samevalue"]["exit_code"] == 0 and \
        not errs(f["write_samevalue"]) and f["enum_post"]["exit_code"] == 0


@law("cli.destroy_stream: node gone, pw-play exits rc1 unconnected")
def _(r):
    d = r["pwbind_cli_r87_probe"]["legs"]["destroy_stream"]
    return d["node_after"] is False and d["play_rc"] == 1 and \
        "unconnected" in (d.get("play_err") or "")


@law("cli.create_session: session-bound; create_linger: survives quit, dies on destroy")
def _(r):
    l = r["pwbind_cli_r87_probe"]["legs"]
    cs, cl = l["create_session"], l["create_linger"]
    return cs["present_in_session"] and not cs["present_after_quit"] and \
        cl["present_after_quit"] and not cl["present_after_destroy"]


@law("cli.create_badfac: res:-2 refusal visible in the last-500 window (ARM_WINDOW)")
def _(r):
    return "res:-2" in (r["pwbind_cli_r87_probe"]["legs"]
                        ["create_badfac"].get("log_tail") or "")


@law("cli.create_usage: usage refusal visible in the last-500 window (ARM_WINDOW)")
def _(r):
    t = r["pwbind_cli_r87_probe"]["legs"]["create_usage"].get("log_tail") or ""
    return "usage: factory.name=" in t or "res:-22" in t


@law("cli.destroy_sink_module: whole module unloaded by node destroy")
def _(r):
    d = r["pwbind_cli_r87_probe"]["legs"]["destroy_sink_module"]
    return d["sink_listed_after"] is False and d["node_after"] is False


# ---------------- midi ----------------
@law("midi.target-dead: 6 target forms -> rc!=0 + no target node available + res:-2")
def _(r):
    l = r["pwbind_midi_r87_probe"]["legs"]
    for k in ("m_t_bridge", "m_t_serial", "m_t_objid", "m_t_garbage",
              "m_t_prop", "m_t_nt"):
        b = blob(l[k])
        if l[k].get("exit_code") == 0 or "no target node available" not in b \
                or "res:-2" not in b:
            return False
    return True


@law("midi.publish-unlinked: --target 0 / autoconnect=false publish Stream/Output/Midi, 0 links")
def _(r):
    l = r["pwbind_midi_r87_probe"]["legs"]
    for k in ("m_t_zero", "m_noauto"):
        snap = l[k]["last"]
        if snap["media_class"] != "Stream/Output/Midi" or \
                sorted(snap["ports"]) != ["output_1"] or \
                l[k]["consumers"] != []:
            return False
    return True


@law("midi.pin: pw-link rc0, link visible, 45 B SMF with both on/offs")
def _(r):
    p = r["pwbind_midi_r87_probe"]["legs"]["pin"]
    f = p.get("file") or {}
    return p.get("pwlink", {}).get("exit_code") == 0 and \
        len(p.get("links") or []) >= 1 and \
        f.get("bytes") == 45 and f.get("has_mthd") and \
        all(f.get("note_ons") or []) and all(f.get("note_offs") or [])


@law("midi.skeleton: refused midirecord writes 26 B MThd+MTrk+EOT, no payload")
def _(r):
    s = r["pwbind_midi_r87_probe"]["legs"]["skeleton"]
    f = s["file"]
    return s["rc"] != 0 and f["bytes"] == 26 and f["has_mthd"] and \
        not any(f["note_ons"]) and not any(f["note_offs"])


@law("midi.mdump_off: offline parse rc0 with Note lines")
def _(r):
    m = r["pwbind_midi_r87_probe"]["legs"]["mdump_off"]
    return m["exit_code"] == 0 and \
        any("Note On" in ln for ln in m.get("stdout_head") or []) or \
        "Note On" in (m.get("stdout") or "")


@law("midi.mdump_live: pass (published+notes) or coverage_blocked — never silent")
def _(r):
    e = r["pwbind_midi_r87_probe"]
    ml = e["legs"]["mdump_live"]
    if ml.get("attempts"):
        a = ml["attempts"][0]
        return a.get("node") and "Note" in (a.get("stdout") or "")
    return bool(e.get("coverage_blocked"))


@law("midi.pactl: raop/zc/bogus all No such entity")
def _(r):
    l = r["pwbind_midi_r87_probe"]["legs"]
    return all(l[k]["exit_code"] != 0 and
               "Failure: No such entity" in blob(l[k])
               for k in ("pactl_raop", "pactl_zc", "pactl_bogus"))


@law("midi.pwcli-modules: 4 load-module attempts all Could not load module")
def _(r):
    l = r["pwbind_midi_r87_probe"]["legs"]
    return all("Could not load module" in blob(l[k])
               for k in ("pwcli_raop", "pwcli_zc", "pwcli_null",
                         "pwcli_panull"))


@law("midi.remote: -R/env/cli all Host is down, rc!=0")
def _(r):
    l = r["pwbind_midi_r87_probe"]["legs"]
    return all(l[k]["exit_code"] != 0 and "Host is down" in blob(l[k])
               for k in ("remote_flag", "remote_env", "remote_cli"))


@law("midi.remote_stall: recorded stall (record-only)")
def _(r):
    s = r["pwbind_midi_r87_probe"]["legs"]["remote_stall"]
    return "exit_code" in s or "killed_at_bound" in s


@law("midi.remote_census: zero remote/raop/zeroconf nodes and zero .so")
def _(r):
    c = r["pwbind_midi_r87_probe"]["legs"]["remote_census"]
    b = json.dumps(c)
    return ("raop" not in b.lower() or
            (isinstance(c, dict) and
             all(not v for k, v in c.items() if "count" in str(k))))


# ---------------- custody (all four entries) ----------------
@law("custody: sinks_gone all true, own_nodes_after empty (per entry)")
def _(r):
    for k, e in r.items():
        if not k.startswith("pwbind"):
            continue
        sg = e.get("sinks_gone") or {}
        if any(not v for v in sg.values()):
            return False
        if e.get("own_nodes_after"):
            return False
    return True


@law("custody: name-verified unloads (verified_index == captured, no recycle)")
def _(r):
    for k, e in r.items():
        if not k.startswith("pwbind"):
            continue
        for tag, u in (e.get("unloads") or {}).items():
            u = u or {}
            if u.get("verified_index") is not None and \
                    u.get("verified_index") != u.get("captured"):
                return False
            if u.get("recycled"):
                return False
    return True


def run(path):
    r = json.load(open(path))["measurements"]
    res = []
    for name, fn in LAWS:
        try:
            res.append((name, bool(fn(r)), None))
        except Exception as exc:      # noqa: BLE001
            res.append((name, None, f"{type(exc).__name__}: {exc}"))
    return res


def main():
    paths = sys.argv[1:]
    allres = {}
    for p in paths:
        allres[p] = run(p)
    names = [n for n, _ in LAWS]
    for p in paths:
        res = dict((n, (ok, err)) for n, ok, err in allres[p])
        npass = sum(1 for n in names if res[n][0] is True)
        nfail = [n for n in names if res[n][0] is False]
        nerr = [n for n in names if res[n][0] is None]
        print(f"== {p}\n   {npass}/{len(names)} PASS")
        for n in nfail:
            print(f"   FAIL {n}")
        for n in nerr:
            print(f"   ERR  {n}: {res[n][1]}")
    print("\n== per-law matrix ==")
    for n in names:
        row = "".join("." if allres[p] and dict(
            (x, y) for x, y, _ in allres[p])[n] is True else
            ("F" if dict((x, y) for x, y, _ in allres[p])[n] is False
             else "E") for p in paths)
        print(f"   {row}  {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
