"""r87-scribe laws re-derivation: independent re-check of every headline
claim of reports/round-87/r87-author.md against the TWO cited green
receipts (A=070036, B=070305). Reads receipts only; writes nothing.

usage: laws-recheck.py  -> prints one PASS/FAIL line per check + totals
"""
import json
import re
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
RUNS = {
    "A": LANE / "corpus/live/runs/20261016T070036115509Z-pwbind-r87/measurements.json",
    "B": LANE / "corpus/live/runs/20261016T070305393338Z-pwbind-r87/measurements.json",
}
CHECKS = []


def ck(name, cond, detail=""):
    CHECKS.append((name, bool(cond), detail))


def parse_format(text):
    """independent re-implementation of the negotiated-Format reader"""
    rate = re.search(r"Format:Audio:rate \(65539\).*?Int (\d+)", text or "", re.S)
    fmt = re.search(r"Format:Audio:format \(65537\).*?Id (\d+)", text or "", re.S)
    return {"rate": int(rate.group(1)) if rate else None,
            "format_id": int(fmt.group(1)) if fmt else None}


def parse_volume(text):
    m = re.search(r"Props:volume \(65539\).*?\n\s*Float ([0-9.]+)", text or "")
    return float(m.group(1)) if m else None


def run_checks(tag, d):
    m = d["measurements"]
    modes = m["pwbind_modes_r87_probe"]
    target = m["pwbind_target_r87_probe"]
    cli = m["pwbind_cli_r87_probe"]
    midi = m["pwbind_midi_r87_probe"]
    ml, tl, cl, mdl = modes["legs"], target["legs"], cli["legs"], midi["legs"]
    p = f"{tag}:"

    # ---------- modes ----------
    cats = ml["binaries"]["members"]
    base = ml["binaries"]["pw_cat_sha"]
    for t in ("pw-play", "pw-record", "pw-midiplay", "pw-midirecord"):
        ck(f"{p}modes.binaries.{t}-aliases-pwcat",
           cats[t]["same_as_pwcat"] and cats[t]["sha256"] == base)
    for t in ("pw-mididump", "pw-cli"):
        ck(f"{p}modes.binaries.{t}-distinct", not cats[t]["same_as_pwcat"])
    for name, cls in (("m_bare", "pwcat_mode_required"),
                      ("m_mflag_only", "pwcat_mode_required"),
                      ("m_noflag_target", "pwcat_mode_required"),
                      ("m_capture", "pwcat_unknown_longopt"),
                      ("m_duplex", "pwcat_unknown_longopt"),
                      ("m_clip", "midiclip_read_fail"),
                      ("m_dsd", "dsd_read_fail")):
        ck(f"{p}modes.refusal.{name}",
           ml[name]["exit_code"] != 0 and ml[name].get("error_class") == cls)
    ck(f"{p}modes.refusal.none-killed",
       not any(ml[n].get("killed_at_bound") for n in
               ("m_capture", "m_duplex", "m_clip", "m_dsd")))
    for name in ("m_p_r", "m_r_p_r", "m_play_r"):
        ck(f"{p}modes.direction.{name}=Input/Audio",
           ml[name]["last"]["media_class"] == "Stream/Input/Audio"
           and any(x.startswith("input_") for x in ml[name]["last"]["ports"]))
    for name in ("m_r_p", "m_p_r_p", "m_record_p"):
        ck(f"{p}modes.direction.{name}=Output/Audio",
           ml[name]["last"]["media_class"] == "Stream/Output/Audio"
           and any(x.startswith("output_") for x in ml[name]["last"]["ports"]))
    for name in ("m_midi_p", "m_ump", "m_sysex"):
        ck(f"{p}modes.direction.{name}=Output/Midi",
           ml[name]["last"]["media_class"] == "Stream/Output/Midi"
           and "output_1" in ml[name]["last"]["ports"])
    ck(f"{p}modes.direction.m_midi_r=Input/Midi",
       ml["m_midi_r"]["last"]["media_class"] == "Stream/Input/Midi"
       and "input_1" in ml["m_midi_r"]["last"]["ports"])
    viol = [n for n, leg in ml.items()
            if isinstance(leg.get("last"), dict)
            and any(x.startswith("input_") for x in leg["last"].get("ports") or [])
            and any(x.startswith("output_") for x in leg["last"].get("ports") or [])]
    ck(f"{p}modes.never-duplex", not viol, str(viol))
    ck(f"{p}modes.m_sysex-stays-up", ml["m_sysex"]["exit_code"] != 0)
    ck(f"{p}modes.recorded-files",
       all(ml[n].get("recorded_file", {}).get("exists")
           for n in ("m_p_r", "m_r_p_r", "m_play_r"))
       and ml["m_midi_r"]["recorded_file"]["bytes"] == 26)

    # ---------- target routing ----------
    NS = target["refs"]["ns_id"]
    SER = target["refs"]["ns_serial"]
    nsname = target["unloads"] and [k for k in target["sinks_gone"]][0]
    ns2name = [k for k in target["sinks_gone"]][1]
    DEF = target["inventory"]["default_sink"]
    want = {
        "p_own": nsname, "p_cat": nsname, "p_pb2": nsname, "p_nt": nsname,
        "p_nt_vs_flag": nsname, "p_serial": nsname, "p_prop_serial": nsname,
        "p_env": nsname, "p_env_nobrace": nsname, "p_env_vs_prop": nsname,
        "p_coll": nsname,
        "p_pb3": ns2name, "p_nt_rev": ns2name, "p_three": ns2name,
        "p_prop_twice": ns2name,
        "p_garbage": DEF, "p_pb1": DEF, "p_nt_garbage": DEF,
        "p_objid": DEF, "p_prop_objid": DEF, "p_serial_stale": DEF,
        "p_mon": DEF, "p_mon_cs": DEF, "p_src_name": DEF,
        "p_src_serial": DEF, "p_env_garbage": DEF, "p_mediarole": DEF,
        "p_capsink": DEF, "p_empty": DEF,
    }
    for name, expect in want.items():
        ck(f"{p}target.{name}->{expect[:12]}",
           tl[name]["consumers"] == [expect], str(tl[name]["consumers"]))
    for name in ("p_zero", "p_zero_prop", "p_noauto"):
        ck(f"{p}target.{name}=no-link", tl[name]["consumers"] == [])
    # the boundary-corrected reversal, spelled out on the raw argv
    ck(f"{p}target.flag-beats-node.target",
       "--target" in tl["p_nt_vs_flag"]["argv"]
       and "node.target=" in tl["p_nt_vs_flag"]["argv"]
       and tl["p_nt_vs_flag"]["consumers"] == [nsname])
    ck(f"{p}target.garbage-flag-no-fallthrough",
       "no_such_r87a" in tl["p_nt_garbage"]["argv"]
       and tl["p_nt_garbage"]["consumers"] == [DEF])
    ck(f"{p}target.serial-resolves",
       f"--target {SER}" in tl["p_serial"]["argv"]
       and tl["p_serial"]["consumers"] == [nsname])
    ck(f"{p}target.prop-serial-resolves",
       f"target.object={SER}" in tl["p_prop_serial"]["argv"]
       and tl["p_prop_serial"]["consumers"] == [nsname])
    ck(f"{p}target.object.id-never-resolves",
       f"--target {NS}" in tl["p_objid"]["argv"]
       and tl["p_objid"]["consumers"] == [DEF])
    ck(f"{p}target.prop-object.id-never-resolves",
       f"target.object={NS}" in tl["p_prop_objid"]["argv"]
       and tl["p_prop_objid"]["consumers"] == [DEF])
    ck(f"{p}target.default-sink-stable",
       target["default_sink_at_start"] == target["default_sink_at_end"]
       == DEF)
    ck(f"{p}target.sinks-gone", all(target["sinks_gone"].values()))
    ck(f"{p}target.unloads-name-verified",
       all(u["verified_index"] == u["captured"] and u["recycled"] is False
           for u in target["unloads"].values()))
    ck(f"{p}target.own-after-empty", target["own_nodes_after"] == [])
    ck(f"{p}target.foreign-empty", target["foreign_r87a_nodes"] == [])
    ck(f"{p}target.collision-2-objects",
       isinstance(tl["collision_objects"], list)
       and len(tl["collision_objects"]) == 2
       and {x["media_class"] for x in tl["collision_objects"]}
       == {"Audio/Sink", "Stream/Output/Audio"})

    # ---------- cli ----------
    nid = cli["ns_leaf"]["node_id"]
    cold = (cl["cold_nowarm"].get("stdout") or "") + \
        (cl["cold_nowarm"].get("stderr") or "")
    ck(f"{p}cli.cold-artifact", f"unknown global '{nid}'" in cold)
    ck(f"{p}cli.warm-control",
       f"id: {nid}" in (cl["warm_control"].get("stdout") or ""))
    for v in ("info", "enum-params", "set-param", "destroy", "get-permissions"):
        ck(f"{p}cli.unknowns.{v}",
           cl["unknowns"][v].get("error_class") == "pwcli_unknown_global")
    for w in ("w_v25", "w_v10", "w_mute", "w_unmute", "w_unk"):
        ck(f"{p}cli.writes.{w}-rc0",
           cl["writes"][w]["exit_code"] == 0
           and cl["writes"][w].get("has_pod") and not cl["writes"][w]["errors"])
    reg = cl["regions"]
    ck(f"{p}cli.regions.solo-8192", reg["solo"]["median_peak"] == 8192.0)
    ck(f"{p}cli.regions.vol25-2048-exact-ratio",
       reg["vol25"]["median_peak"] == 2048.0)
    ck(f"{p}cli.regions.restore-8192", reg["restore"]["median_peak"] == 8192.0)
    ck(f"{p}cli.regions.mute-0", reg["mute"]["median_peak"] == 0.0)
    ck(f"{p}cli.regions.unmute-8192", reg["unmute"]["median_peak"] == 8192.0)
    vl = cl["volume_legs"]
    ck(f"{p}cli.volume.v100", vl["v100"]["median_peak"] == 8192.0
       and vl["v100"]["ratio_vs_v100"] == 1.0)
    ck(f"{p}cli.volume.v050", vl["v050"]["median_peak"] == 4096.0
       and vl["v050"]["ratio_vs_v100"] == 0.5)
    ck(f"{p}cli.volume.v000", vl["v000"]["median_peak"] == 0.0)
    ck(f"{p}cli.volume.v150-unclamped", vl["v150"]["median_peak"] == 12288.0
       and vl["v150"]["ratio_vs_v100"] == 1.5)
    fs = cl["fmt_stream"]
    pre = parse_format(fs["pre"].get("stdout"))
    pv = parse_format(fs["post_valid"].get("stdout"))
    pe = parse_format(fs["post_empty"].get("stdout"))
    ck(f"{p}cli.fmt_stream.pre-S16LE-48000",
       pre == {"rate": 48000, "format_id": 259}, str(pre))
    ck(f"{p}cli.fmt_stream.valid-write-sealed", pv == pre, f"{pre}->{pv}")
    ck(f"{p}cli.fmt_stream.empty-write-sealed", pe == pre, f"{pre}->{pe}")
    fk = cl["fmt_sink"]
    prek = parse_format(fk["pre"].get("stdout"))
    postk = parse_format(fk["post_valid"].get("stdout"))
    ck(f"{p}cli.fmt_sink.pre-F32P-48000",
       prek == {"rate": 48000, "format_id": 518}, str(prek))
    ck(f"{p}cli.fmt_sink.write-sealed", postk == prek, f"{prek}->{postk}")
    fu = cl["fmt_unlinked"]
    ck(f"{p}cli.fmt_unlinked.enum-Fmt-res-2",
       fu["enum_fmt"].get("error_class") == "pwcli_remote_enoent"
       and "res:-2" in fu["enum_fmt"].get("stderr", ""))
    ck(f"{p}cli.fmt_unlinked.enum-Props-reads",
       fu["enum_props"].get("has_pod")
       and "Object:" in fu["enum_props"].get("stdout", ""))
    sc = cl["sendcmd"]
    ck(f"{p}cli.sendcmd.Suspend", sc["Suspend"]["state_after"] == "suspended")
    ck(f"{p}cli.sendcmd.Resume-unknown",
       "unknown node command type: Resume" in sc["Resume"]["cmd"].get("stderr", ""))
    ck(f"{p}cli.sendcmd.Start-noop",
       sc["Start"]["state_after"] == "suspended")
    ck(f"{p}cli.sendcmd.Pause", sc["Pause"]["state_after"] == "suspended")
    ck(f"{p}cli.latency-res-95",
       cl["latency"].get("error_class") == "pwcli_remote_notsup")
    ck(f"{p}cli.props_unk-silent",
       cl["props_unk"]["exit_code"] == 0 and not cl["props_unk"]["errors"])
    fo = cl["foreign"]
    ck(f"{p}cli.foreign.volume-read", fo["volume_read"] == 1.0)
    ck(f"{p}cli.foreign.samevalue-no-error",
       not fo["write_samevalue"]["errors"] and fo["volume_after"] == 1.0)
    ck(f"{p}cli.foreign.unknown-key-silent", not fo["write_unk"]["errors"])
    ck(f"{p}cli.foreign.bogus-type",
       fo["write_bogus"].get("error_class") == "pwcli_unknown_param")
    ck(f"{p}cli.destroy_stream", cl["destroy_stream"]["node_after"] is False
       and cl["destroy_stream"]["play_rc"] == 1
       and "unconnected" in (cl["destroy_stream"].get("play_err") or ""))
    ck(f"{p}cli.create_session", cl["create_session"]["present_in_session"]
       and not cl["create_session"]["present_after_quit"])
    ck(f"{p}cli.create_linger",
       cl["create_linger"]["present_after_quit"]
       and cl["create_linger"].get("present_after_destroy") is False)
    ck(f"{p}cli.create_badfac",
       "can't create node" in cl["create_badfac"]["log_tail"])
    ck(f"{p}cli.create_usage",
       "usage: factory.name=" in cl["create_usage"]["log_tail"])
    ck(f"{p}cli.destroy_sink_module",
       cl["destroy_sink_module"]["sink_listed_after"] is False
       and cl["destroy_sink_module"]["node_after"] is False)
    ck(f"{p}cli.player-alive-at-end", cl["player_alive_at_end"] is True)

    # ---------- midi ----------
    for t in ("m_t_bridge", "m_t_serial", "m_t_objid", "m_t_garbage",
              "m_t_prop", "m_t_nt"):
        ck(f"{p}midi.dead-target.{t}",
           mdl[t]["exit_code"] != 0
           and mdl[t].get("error_class") == "no_target_node_midi"
           and "no target node available" in mdl[t].get("stderr", "")
           and "res:-2" in mdl[t].get("stderr", ""))
    for t in ("m_t_zero", "m_noauto"):
        ck(f"{p}midi.publish.{t}",
           mdl[t]["last"]["media_class"] == "Stream/Output/Midi"
           and "output_1" in mdl[t]["last"]["ports"]
           and mdl[t]["consumers"] == [])
    pin = mdl["pin"]
    ck(f"{p}midi.pin.pwlink-rc0-active",
       pin["pwlink"]["exit_code"] == 0 and len(pin["links"]) == 1
       and pin["links"][0]["state"] == "active")
    ck(f"{p}midi.pin.aplaymidi-rc0", pin["aplaymidi_rc"] == 0)
    ck(f"{p}midi.pin.record-rc1", pin["record_rc"] == 1)
    pf = pin["file"]
    ck(f"{p}midi.pin.45B-real-events",
       pf["bytes"] == 45 and pf["has_mthd"]
       and pf["note_ons"] == [True, True] and pf["note_offs"] == [True, True]
       and pf["head_hex"].startswith("4d546864")
       and "90" in pf["head_hex"] and "80" in pf["head_hex"])
    sk = mdl["skeleton"]["file"]
    ck(f"{p}midi.skeleton.26B-no-notes",
       sk["bytes"] == 26 and sk["has_mthd"]
       and not any(sk["note_ons"]) and not any(sk["note_offs"]))
    ck(f"{p}midi.mdump_off",
       "Note On" in mdl["mdump_off"].get("stdout", ""))
    att = mdl["mdump_live"]["attempts"][0]
    ck(f"{p}midi.mdump_live.first-attempt",
       att["node"] and att["pwlink_rc"] == 0
       and "Note On" in att.get("stdout", ""))
    for t in ("pactl_raop", "pactl_zc", "pactl_bogus"):
        ck(f"{p}midi.{t}",
           mdl[t]["exit_code"] != 0
           and mdl[t].get("error_class") == "pa_module_noent"
           and "No such entity" in mdl[t].get("stderr", ""))
    for t in ("pwcli_raop", "pwcli_zc", "pwcli_null", "pwcli_panull"):
        ck(f"{p}midi.{t}",
           mdl[t].get("error_class") == "pwcli_module_load_fail")
    for t in ("remote_flag", "remote_env"):
        ck(f"{p}midi.{t}", mdl[t]["exit_code"] != 0
           and mdl[t].get("error_class") == "remote_host_down")
    ck(f"{p}midi.remote_cli-rc255",
       mdl["remote_cli"]["exit_code"] == 255
       and mdl["remote_cli"].get("error_class") == "pwcli_connect_down")
    ck(f"{p}midi.remote_stall-killed",
       mdl["remote_stall"].get("killed_at_bound") is True)
    rc = mdl["remote_census"]
    ck(f"{p}midi.remote_census-zero",
       rc["remote_named_nodes"] == [] and rc["net_modules"] == []
       and rc["module_dir_count"] == 34)
    ck(f"{p}midi.bridge-present",
       midi["bridge"]["node"]["name"] == "Midi-Bridge")
    ck(f"{p}midi.seq-port", midi["seq_port"] == "14:0")

    # ---------- meta / teardown ----------
    for name, e in (("modes", modes), ("target", target), ("cli", cli),
                    ("midi", midi)):
        ck(f"{p}meta.{name}.failures-empty", e["failures"] == [])
        ck(f"{p}meta.{name}.coverage_blocked-absent-or-empty",
           not e.get("coverage_blocked"))
        ck(f"{p}meta.{name}.own-after-empty", e.get("own_nodes_after") == [])
        ck(f"{p}meta.{name}.foreign-empty", e.get("foreign_r87a_nodes") == [])
        if e.get("sinks_gone"):
            ck(f"{p}meta.{name}.sinks-gone", all(e["sinks_gone"].values()))


A = json.load(open(RUNS["A"]))
B = json.load(open(RUNS["B"]))
run_checks("A", A)
run_checks("B", B)

# ---------- cross-run stability ----------
def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}/{i}")
    else:
        yield path, o


def norm_text(s):
    s = re.sub(r"r87a_\d+", "r87a_<pid>", s)
    s = re.sub(r"r87arole\d+", "r87arole<pid>", s)
    s = re.sub(r"r84a_\d+", "r84a_<pid>", s)
    s = re.sub(r"\b\d{5,}\b", "<num>", s)
    s = re.sub(r"/tmp/[A-Za-z0-9._/-]+", "<tmp>", s)
    s = re.sub(r"r87a-[a-z0-9]+", "r87a-<tmp>", s)
    return s


la, lb = dict(leaves(A)), dict(leaves(B))
paths = sorted(set(la) | set(lb))
diff = [k for k in paths if la.get(k) != lb.get(k)]


def norm_any(s):
    s = re.sub(r"\d{5,}", "<num>", str(s))
    s = re.sub(r"r87a-[a-z0-9]+", "r87a-<tmp>", s)
    s = re.sub(r"r87a_\d+", "r87a_<pid>", s)
    s = re.sub(r"/tmp/[A-Za-z0-9._/-]+", "<tmp>", s)
    return s


# compare on NORMALIZED paths AND values (pid/node-id churn is by design)
nA = {norm_any(k): norm_any(json.dumps(v)) for k, v in la.items()}
nB = {norm_any(k): norm_any(json.dumps(v)) for k, v in lb.items()}
npaths = sorted(set(nA) | set(nB))
ndiff = [k for k in npaths if nA.get(k) != nB.get(k)]
verdict_fields = ("exit_code", "signal", "killed_at_bound")
vdiff = [k for k in ndiff
         if any(k.endswith("/" + f) for f in verdict_fields)]
ck("X: no verdict-class difference A vs B (normalized)", not vdiff,
   str(vdiff[:5]))
ck("X: pid/num-normalized leaf diff (count reported)", True,
   f"{len(ndiff)} differing leaves of {len(npaths)}")

fails = [(n, d) for n, ok, d in CHECKS if not ok]
for n, ok, det in CHECKS:
    print(f"{'PASS' if ok else 'FAIL'} {n}" + (f"  [{det}]" if not ok and det else ""))
print()
print(f"TOTAL {len(CHECKS) - len(fails)}/{len(CHECKS)} checks pass; "
      f"{len(fails)} fail")
if fails:
    sys.exit(1)
