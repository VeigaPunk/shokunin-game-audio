#!/usr/bin/env python3
"""r86 reviewer — independent re-derivation of every armed r86 verdict
from RECEIPT DATA ALONE (no fixture code, no live host).

Re-implements the `pwctl_*_r86_probe` arms from
corpus/fixtures/measure_audio.py @ fa5994a0 as a reader of the receipt
JSON, so a green receipt must survive an independent reading of the law.

Usage: r86r_audit.py RECEIPT.json [RECEIPT.json ...]
Writes a JSON summary next to the caller's choice via --out.
"""
import argparse
import json
import re
import sys

CHECKS = []


def chk(name, ok, detail=""):
    CHECKS.append({"name": name, "ok": bool(ok), "detail": str(detail)[:220]})
    return bool(ok)


def rows_of(text):
    return [ln for ln in (text or "").splitlines()
            if ln.lstrip().startswith("update:")]


def vol_pct(rec):
    m = re.search(r"(\d+)\s*%", (rec or {}).get("stdout") or "")
    return int(m.group(1)) if m else None


def teardown(entry, tag, ns_name, meta=False):
    """Per-entry custody witnesses (armed in every entry)."""
    chk(f"{tag}: failures empty", entry.get("failures") == [],
        entry.get("failures"))
    chk(f"{tag}: no blocked", not entry.get("blocked"),
        entry.get("blocked"))
    cb = entry.get("coverage_blocked")
    chk(f"{tag}: coverage_blocked empty", not cb, cb)
    un = (entry.get("unloads") or {}).get(ns_name) or {}
    chk(f"{tag}: unload verified_index==captured",
        un.get("verified_index") == un.get("captured")
        and un.get("verified_index") is not None,
        un.get("verified_index"))
    chk(f"{tag}: unload not recycled", un.get("recycled") is False,
        un.get("recycled"))
    chk(f"{tag}: unload rc0", un.get("exit_code") == 0, un.get("exit_code"))
    chk(f"{tag}: unload field sink_name",
        un.get("field") == "sink_name", un.get("field"))
    chk(f"{tag}: unload value == own ns",
        un.get("value") == ns_name, un.get("value"))
    sg = entry.get("sinks_gone")
    chk(f"{tag}: sinks_gone all true",
        isinstance(sg, dict) and sg and all(sg.values()), sg)
    chk(f"{tag}: own_nodes_after []", entry.get("own_nodes_after") == [],
        entry.get("own_nodes_after"))
    if meta:
        chk(f"{tag}: meta_keys_gone true",
            entry.get("meta_keys_gone") is True,
            entry.get("meta_keys_gone"))


def audit_addr(e):
    t = "addr"
    legs = e["legs"]
    ns = (e.get("ns_leaf") or {})
    nid, ser = ns.get("node_id"), str(ns.get("object_serial"))
    chk(f"{t}: ns media_class Audio/Sink",
        ns.get("media_class") == "Audio/Sink", ns.get("media_class"))
    l = legs["ls_serial"]
    chk(f"{t}: ls_serial rc0+resolves",
        l.get("exit_code") == 0
        and f'object.serial = "{ser}"' in (l.get("stdout") or "")
        and f"id {nid}," in (l.get("stdout") or ""), l.get("exit_code"))
    l = legs["ls_id"]
    chk(f"{t}: ls_id does NOT resolve (serial namespace)",
        l.get("exit_code") == 0
        and f'object.serial = "{ser}"' not in (l.get("stdout") or ""),
        l.get("exit_code"))
    l = legs["info_id"]
    chk(f"{t}: info_id rc0+resolves",
        l.get("exit_code") == 0
        and f"id: {nid}" in (l.get("stdout") or ""), l.get("exit_code"))
    for nm in ("info_serial", "enum_serial", "info_bogus"):
        l = legs[nm]
        chk(f"{t}: {nm} rc0 unknown_global",
            l.get("exit_code") == 0
            and l.get("error_class") == "pwcli_unknown_global",
            (l.get("exit_code"), l.get("error_class")))
    for cls in ("Node", "Port", "Metadata", "Client"):
        l = legs[f"ls_{cls}"]
        rows = re.findall(r"\bid (\d+),\s*type PipeWire:Interface:(\w+)/",
                          l.get("stdout") or "")
        chk(f"{t}: ls_{cls} typed rows all {cls}",
            l.get("exit_code") == 0 and rows
            and all(x == cls for _, x in rows),
            (l.get("exit_code"), len(rows)))
    for cls in ("Bogus", "node", "Session"):
        l = legs[f"ls_{cls}"]
        chk(f"{t}: ls_{cls} indistinguishable-empty",
            l.get("exit_code") == 0 and l.get("stdout_bytes") == 0,
            (l.get("exit_code"), l.get("stdout_bytes")))
    for nm in ("dump_id", "dump_serial"):
        l = legs[nm]
        chk(f"{t}: {nm} rc0+resolves+bytes",
            l.get("exit_code") == 0 and l.get("stdout_bytes", 0) > 0
            and f'"id": {nid}' in (l.get("stdout") or ""),
            (l.get("exit_code"), l.get("stdout_bytes")))
    chk(f"{t}: dump_id == dump_serial previews",
        legs["dump_id"].get("stdout") == legs["dump_serial"].get("stdout"))
    for nm in ("dump_badid", "dump_bogus", "dump_color_sep"):
        l = legs[nm]
        chk(f"{t}: {nm} silent-empty rc0",
            l.get("exit_code") == 0 and l.get("stdout_bytes") == 0,
            (l.get("exit_code"), l.get("stdout_bytes")))
    l = legs["dump_color_join"]
    chk(f"{t}: dump_color_join dumps",
        l.get("exit_code") == 0 and l.get("stdout_bytes", 0) >= 1000,
        (l.get("exit_code"), l.get("stdout_bytes")))
    chk(f"{t}: dump_color_eq armed=False (record-only)",
        legs["dump_color_eq"].get("armed") is False)
    for rep in (1, 2):
        l = legs[f"dump_full{rep}"]
        chk(f"{t}: dump_full{rep} self-Client law",
            l.get("exit_code") == 0 and l.get("self_clients", 0) >= 1,
            (l.get("exit_code"), l.get("self_clients")))
    chk(f"{t}: dump_full self serials disjoint (fresh client each)",
        set(legs["dump_full1"].get("self_serials") or [])
        .isdisjoint(legs["dump_full2"].get("self_serials") or []),
        (legs["dump_full1"].get("self_serials"),
         legs["dump_full2"].get("self_serials")))
    l = legs["info_all"]
    chk(f"{t}: info_all rc0+bytes",
        l.get("exit_code") == 0 and l.get("stdout_bytes", 0) >= 10000,
        (l.get("exit_code"), l.get("stdout_bytes")))
    for nm in ("list_vars", "list_remotes"):
        l = legs[nm]
        chk(f"{t}: {nm} rc0+bytes",
            l.get("exit_code") == 0 and l.get("stdout_bytes", 0) > 0,
            (l.get("exit_code"), l.get("stdout_bytes")))
    l = legs["remote_down"]
    chk(f"{t}: remote_down real nonzero refusal",
        l.get("exit_code") != 0
        and "failed to connect" in ((l.get("stderr") or "")
                                    + (l.get("stdout") or "")),
        (l.get("exit_code"), l.get("error_class")))
    if "meta_info_empty" in legs:
        l = legs["meta_info_empty"]
        chk(f"{t}: meta_info_empty silent on live object",
            l.get("exit_code") == 0 and l.get("stdout_bytes") == 0,
            (l.get("exit_code"), l.get("stdout_bytes")))
    l = legs["mk_self_loop"]
    own = (legs.get("self_loop_census") or {}).get("links") or []
    chk(f"{t}: self-loop formed",
        l.get("exit_code") == 0 and own
        and own[0].get("out") == f"{ns_name(e)}:monitor_FL"
        and own[0].get("in") == f"{ns_name(e)}:playback_FL",
        (l.get("exit_code"), own))
    if "info_link" in legs:
        l = legs["info_link"]
        ok = all(k in (l.get("stdout") or "") for k in
                 ("output-node-id", "input-node-id", "state"))
        chk(f"{t}: info_link census fields", l.get("exit_code") == 0 and ok,
            (l.get("exit_code"), l.get("has_pod")))
    if "destroy_link" in legs:
        l = legs["destroy_link"]
        chk(f"{t}: destroy_link removed the link",
            l.get("exit_code") == 0
            and not (legs.get("destroy_census") or {}).get("surviving"),
            (l.get("exit_code"), (legs.get("destroy_census") or {})
             .get("surviving")))


def ns_name(e):
    return e.get("ns_name") or ""


def audit_params(e):
    t = "params"
    legs = e["legs"]
    for nm in ("n_props", "n_propinfo", "n_enumformat", "p_enumformat",
               "p_latency", "p_io", "p_meta", "d_profile", "d_enumprofile",
               "d_enumroute"):
        l = legs[nm]
        chk(f"{t}: {nm} pod dump",
            l.get("exit_code") == 0 and l.get("has_pod"),
            (l.get("exit_code"), l.get("has_pod")))
    for nm in ("p_format", "n_latency", "n_proclat"):
        l = legs[nm]
        chk(f"{t}: {nm} pod-absent",
            l.get("exit_code") == 0 and not l.get("has_pod"),
            (l.get("exit_code"), l.get("has_pod"), l.get("error_class")))
    chk(f"{t}: n_format armed rc_only",
        legs["n_format"].get("armed") == "rc_only")
    chk(f"{t}: n_format rc0 (pod recorded)",
        legs["n_format"].get("exit_code") == 0,
        legs["n_format"].get("exit_code"))
    for nm in ("n_io", "n_meta", "n_profile", "p_props", "d_props"):
        l = legs[nm]
        chk(f"{t}: {nm} remote ENOENT",
            l.get("exit_code") == 0
            and l.get("error_class") == "pwcli_remote_enoent",
            (l.get("exit_code"), l.get("error_class")))
    chk(f"{t}: d_route armed=False (record-only)",
        legs["d_route"].get("armed") is False)
    chk(f"{t}: n_num3 == n_enumformat bytes",
        legs["n_num3"].get("stdout") == legs["n_enumformat"].get("stdout"))
    for nm in ("n_bogus", "n_999", "n_all", "sp_bogusp"):
        l = legs[nm]
        chk(f"{t}: {nm} unknown_param_type",
            l.get("exit_code") == 0
            and l.get("error_class") == "pwcli_unknown_param",
            (l.get("exit_code"), l.get("error_class")))
    l = legs["enum_badobj"]
    chk(f"{t}: enum_badobj unknown_global",
        l.get("exit_code") == 0
        and l.get("error_class") == "pwcli_unknown_global",
        (l.get("exit_code"), l.get("error_class")))
    for nm in ("c_props", "f_props", "m_props", "l_props",
               "core_setparam"):
        l = legs.get(nm)
        if l is None:
            continue
        chk(f"{t}: {nm} not-implemented",
            l.get("exit_code") == 0
            and l.get("error_class") == "pwcli_not_impl",
            (l.get("exit_code"), l.get("error_class")))
    l = legs["sp_garbage"]
    chk(f"{t}: sp_garbage -> None echo",
        l.get("exit_code") == 0
        and (l.get("stdout") or "").strip() == "None",
        (l.get("exit_code"), (l.get("stdout") or "").strip()[:40]))
    l = legs["sp_empty"]
    chk(f"{t}: sp_empty -> empty pod echo",
        l.get("exit_code") == 0 and l.get("has_pod"),
        (l.get("exit_code"), l.get("has_pod")))
    chk(f"{t}: sp_zzz key stripped on re-enum",
        legs["sp_zzz"].get("exit_code") == 0
        and "zzz" not in (legs["re_zzz"].get("stdout") or ""))
    l = legs["sp_voltype"]
    chk(f"{t}: sp_voltype None slot echo",
        l.get("exit_code") == 0 and "None" in (l.get("stdout") or ""),
        l.get("exit_code"))
    l = legs["sp_enumf"]
    chk(f"{t}: sp_enumf remote -95",
        l.get("exit_code") == 0
        and l.get("error_class") == "pwcli_remote_notsup",
        (l.get("exit_code"), l.get("error_class")))
    l = legs["sp_port_lat"]
    chk(f"{t}: sp_port_lat echo-lie (not_impl + Port type)",
        l.get("exit_code") == 0
        and l.get("error_class") == "pwcli_not_impl"
        and "type:PipeWire:Interface:Port" in (l.get("stderr") or ""),
        (l.get("exit_code"), l.get("error_class")))
    chk(f"{t}: re_port_lat minQuantum unchanged",
        bool(re.search(r"minQuantum[\s\S]{0,140}?Float 0\.000000",
                       legs["re_port_lat"].get("stdout") or "")))
    l = legs["sp_badid"]
    chk(f"{t}: sp_badid unknown_global",
        l.get("exit_code") == 0
        and l.get("error_class") == "pwcli_unknown_global",
        (l.get("exit_code"), l.get("error_class")))
    l = legs["sp_nojson"]
    chk(f"{t}: sp_nojson usage",
        l.get("exit_code") == 0 and l.get("error_class") == "pwcli_usage",
        (l.get("exit_code"), l.get("error_class")))


def audit_dsp(e):
    t = "dsp"
    legs = e["legs"]
    chk(f"{t}: tap validated pre-player",
        bool((legs.get("tap_link") or {}).get("edges")),
        len((legs.get("tap_link") or {}).get("edges") or []))
    pa = legs.get("player_attach") or {}
    if not pa.get("sink"):
        chk(f"{t}: player attach (else coverage_blocked)",
            "player never attached" in " ".join(
                e.get("coverage_blocked") or []), e.get("coverage_blocked"))
        return
    regs = legs.get("regions") or {}
    solo = (regs.get("solo") or {}).get("median_peak")
    chk(f"{t}: solo in x8192 [0.85,1.18]",
        solo is not None and 0.85 * 8192 <= solo <= 1.18 * 8192, solo)
    envs = {"cv25": (0.15, 0.35), "cv50": (0.40, 0.60),
            "reset": (0.85, 1.18), "dead": (0.85, 1.18),
            "pa25": (0.008, 0.035), "pa100": (0.85, 1.18)}
    for nm, (lo, hi) in envs.items():
        v = (regs.get(nm) or {}).get("median_peak")
        chk(f"{t}: {nm} in x8192 [{lo},{hi}]",
            v is not None and lo * 8192 <= v <= hi * 8192, v)
    mv = (regs.get("mute") or {}).get("median_peak")
    chk(f"{t}: mute <= 64", mv is not None and mv <= 64, mv)
    p25 = vol_pct(legs.get("pactl_after_cv25"))
    chk(f"{t}: pactl reads cube-root after cv25 [50,80]",
        p25 is not None and 50 <= p25 <= 80, p25)
    chk(f"{t}: pactl still 100 after dead key",
        vol_pct(legs.get("pactl_after_dead")) == 100,
        vol_pct(legs.get("pactl_after_dead")))
    chk(f"{t}: enum_after_dead reads Float 0.25",
        bool(re.search(r"Props:volume[\s\S]{0,120}?Float 0\.25",
                       (legs.get("enum_after_dead") or {}).get("stdout")
                       or "")))
    chk(f"{t}: pactl_read_25 == 25",
        vol_pct(legs.get("pactl_read_25")) == 25,
        vol_pct(legs.get("pactl_read_25")))
    chk(f"{t}: pactl_read_100 == 100",
        vol_pct(legs.get("pactl_read_100")) == 100,
        vol_pct(legs.get("pactl_read_100")))
    for nm in ("w_cv25", "w_cv50", "w_mute", "w_reset", "w_dead"):
        l = (legs.get("writes") or {}).get(nm) or {}
        chk(f"{t}: {nm} rc0", l.get("exit_code") == 0, l.get("exit_code"))
    for nm in ("w_cv25", "w_cv50", "w_mute", "w_reset", "w_dead"):
        l = (legs.get("writes") or {}).get(nm) or {}
        chk(f"{t}: {nm} written after solo", (l.get("done_at_s") or 0) > 0,
            l.get("done_at_s"))


def audit_meta(e):
    t = "meta"
    legs = e["legs"]
    l = legs["meta_list"]
    chk(f"{t}: store census rows",
        l.get("exit_code") == 0
        and re.search(r'Found "[^"]+" metadata \d+',
                      l.get("stdout") or ""), l.get("exit_code"))
    chk(f"{t}: bare == -n default",
        legs["meta_bare"].get("stdout") == legs["meta_default"].get("stdout")
        and legs["meta_bare"].get("exit_code") == 0)
    l = legs["meta_bogus"]
    chk(f"{t}: bogus store silent-empty",
        l.get("exit_code") == 0 and l.get("stdout_bytes") == 0,
        (l.get("exit_code"), l.get("stdout_bytes")))
    cen = e.get("meta_census") or {}
    if cen.get("store_ids") and cen.get("ls_ids"):
        chk(f"{t}: -l == ls Metadata census",
            cen["store_ids"] == cen["ls_ids"],
            (cen.get("store_ids"), cen.get("ls_ids")))
        chk(f"{t}: dump Metadata strict subset",
            set(cen.get("dump_ids") or []) < set(cen.get("ls_ids") or []),
            (cen.get("dump_ids"), cen.get("ls_ids")))
    m = re.search(r"set property: id:(\d+)", legs["m_write"].get("stdout")
                  or "")
    nid = m.group(1) if m else None
    chk(f"{t}: m_write set echo", bool(nid), nid)
    if not nid:
        return
    rows = rows_of(legs["m_read"].get("stdout"))
    chk(f"{t}: m_read live-subject read-back",
        any(f"id:{nid}" in r and "key:'r86a_k'" in r and "value:'v1'" in r
            for r in rows), rows[:2])
    rows = rows_of(legs["m_read2"].get("stdout"))
    chk(f"{t}: m_read2 full replace",
        any("value:'v2'" in r for r in rows)
        and not any("value:'v1'" in r for r in rows), rows[:2])
    rows = rows_of(legs["m_read3"].get("stdout"))
    chk(f"{t}: m_read3 typed value verbatim",
        any("type:'Spa:String'" in r for r in rows), rows[:2])
    chk(f"{t}: m_absent Found-only silent",
        not rows_of(legs["m_absent"].get("stdout"))
        and legs["m_absent"].get("exit_code") == 0)
    chk(f"{t}: m_del delete echo",
        legs["m_del"].get("exit_code") == 0
        and "delete property:" in (legs["m_del"].get("stdout") or ""))
    chk(f"{t}: m_read4 key gone after delete",
        not rows_of(legs["m_read4"].get("stdout")))
    chk(f"{t}: m_delabsent same no-op echo",
        legs["m_delabsent"].get("exit_code") == 0
        and "delete property:" in (legs["m_delabsent"].get("stdout") or ""))
    chk(f"{t}: m_dead_w echo lies",
        "set property:" in (legs["m_dead_w"].get("stdout") or ""))
    chk(f"{t}: m_dead_r nothing persisted",
        not rows_of(legs["m_dead_r"].get("stdout")))
    chk(f"{t}: m_wipe subject wipe echo",
        f"delete properties: id:{nid}" in
        (legs["m_wipe"].get("stdout") or ""))
    chk(f"{t}: m_read5 keys gone after wipe",
        not rows_of(legs["m_read5"].get("stdout")))
    l = legs["m_filter"]
    rows = rows_of(l.get("stdout"))
    chk(f"{t}: m_filter kill-bounded subject rows",
        l.get("killed_at_bound") and rows
        and all(f"id:{nid}" in r for r in rows), (len(rows),))
    l = legs["m_filter0"]
    rows0 = rows_of(l.get("stdout"))
    chk(f"{t}: m_filter0 subject-0 rows only",
        l.get("killed_at_bound") and rows0
        and all("id:0" in r for r in rows0), (len(rows0),))
    l = legs["subj0_read"]
    chk(f"{t}: subject-0 read-only baseline",
        l.get("exit_code") == 0
        and 'Found "default"' in (l.get("stdout") or ""))
    chk(f"{t}: subject-0 keys recorded (not armed)",
        isinstance(legs.get("subj0_keys"), list), legs.get("subj0_keys"))


def audit_tools(e):
    t = "tools"
    legs = e["legs"]
    l = legs["top_batch"]
    chk(f"{t}: top batch table",
        l.get("exit_code") == 0 and "FORMAT" in (l.get("stdout") or "")
        and "NAME" in (l.get("stdout") or ""), l.get("exit_code"))
    l = legs["top_batch0"]
    chk(f"{t}: top -n 0 one table rc0",
        l.get("exit_code") == 0 and l.get("stdout_lines", 0) >= 1,
        l.get("exit_code"))
    l = legs["top_batch_term"]
    chk(f"{t}: batch TERM clean",
        l.get("exit_code") == 0 and not l.get("signal")
        and not l.get("loop_assert"),
        (l.get("exit_code"), l.get("signal"), l.get("loop_assert")))
    l = legs["top_tui_term"]
    chk(f"{t}: TUI TERM SIGABRT + loop assert",
        l.get("signal") == "SIGABRT" and l.get("loop_assert"),
        (l.get("signal"), l.get("loop_assert")))
    l = legs["top_tui_kill"]
    chk(f"{t}: TUI KILL SIGKILL no assert",
        l.get("signal") == "SIGKILL" and not l.get("loop_assert"),
        (l.get("signal"), l.get("loop_assert")))
    l = legs["cli_devnull"]
    chk(f"{t}: pw-cli /dev/null SIGABRT",
        l.get("signal") == "SIGABRT"
        and "remove_from_poll" in (l.get("stderr") or ""),
        (l.get("signal"),))
    l = legs["cli_quit"]
    chk(f"{t}: quit clean exit",
        l.get("exit_code") == 0 and not l.get("killed_at_bound"),
        (l.get("exit_code"), l.get("killed_at_bound")))
    l = legs["cli_pipe"]
    chk(f"{t}: pipe stdin hangs (SIGKILL at bound)",
        l.get("killed_at_bound") and l.get("signal") == "SIGKILL",
        (l.get("killed_at_bound"), l.get("signal")))
    envs = {"jack_p": {"Q": "512/48000"},
            "jack_sp": {"Q": "256/44100"},
            "jack_s_only": {"Q": "unset"},
            "jack_v": {"D": "3"}, "jack_vv": {"D": "4"},
            "jack_v_preset": {"D": "5"}}
    for nm, want in envs.items():
        l = legs[nm]
        got = dict(re.findall(r"([QDR])=(\S+)", l.get("stdout") or ""))
        chk(f"{t}: {nm} env {want}",
            l.get("exit_code") == 0
            and all(got.get(k) == v for k, v in want.items()),
            (l.get("exit_code"), got))
    l = legs["jack_r"]
    got = dict(re.findall(r"([QDR])=(\S+)", l.get("stdout") or ""))
    chk(f"{t}: jack_r REMOTE exported",
        l.get("exit_code") == 0 and got.get("R", "").startswith("r86a_"),
        got)
    for nm in ("jack_help", "jack_noargs", "jack_badopt"):
        chk(f"{t}: {nm} rc0",
            legs[nm].get("exit_code") == 0, legs[nm].get("exit_code"))
    chk(f"{t}: jack -Z usage/illegal-option shape",
        "illegal option" in (legs["jack_badopt"].get("stderr") or "")
        and "run JACK applications" in
        (legs["jack_badopt"].get("stdout") or ""))
    l = legs["jack_bogus"]
    chk(f"{t}: bogus payload exec-127",
        l.get("exit_code") == 127 and l.get("error_class") == "pwjack_exec",
        (l.get("exit_code"), l.get("error_class")))
    chk(f"{t}: lk_create formed own-port link",
        legs["lk_create"].get("exit_code") == 0
        and (legs.get("lk_census") or {}).get("links"))
    l = legs["lk_dup"]
    chk(f"{t}: lk_dup rc255 File exists",
        l.get("exit_code") == 255
        and l.get("error_class") == "pwlink_exists",
        (l.get("exit_code"), l.get("error_class")))
    l = legs["lk_bogus"]
    chk(f"{t}: lk_bogus rc255 noent",
        l.get("exit_code") == 255
        and l.get("error_class") == "pwlink_noent",
        (l.get("exit_code"), l.get("error_class")))
    for nm in ("lk_usage", "lk_I_alone", "lk_v_alone"):
        chk(f"{t}: {nm} rc255", legs[nm].get("exit_code") == 255,
            legs[nm].get("exit_code"))
    for nm in ("lk_list", "lk_list_I"):
        l = legs[nm]
        chk(f"{t}: {nm} rc0 lists own node",
            l.get("exit_code") == 0
            and e["ns_name"] in (l.get("stdout") or ""),
            l.get("exit_code"))
    if "lk_d_port" in legs:
        chk(f"{t}: lk_d_port rc255 (wants link id)",
            legs["lk_d_port"].get("exit_code") == 255,
            legs["lk_d_port"].get("exit_code"))
        chk(f"{t}: lk_d_link unlinked",
            legs["lk_d_link"].get("exit_code") == 0
            and not (legs.get("lk_after_unlink") or {}).get("links"),
            legs["lk_d_link"].get("exit_code"))
    chk(f"{t}: junk props silently accepted + link formed",
        legs["lk_junkprops"].get("exit_code") == 0
        and (legs.get("lk_junkprops_census") or {}).get("links"))


def audit_receipt(path):
    with open(path) as fh:
        d = json.load(fh)
    m = d["measurements"]
    chk("receipt: mode probe-pwctl-r86", d.get("mode") == "probe-pwctl-r86",
        d.get("mode"))
    want = ["pwctl_addr_r86_probe", "pwctl_params_r86_probe",
            "pwctl_dsp_r86_probe", "pwctl_meta_r86_probe",
            "pwctl_tools_r86_probe"]
    chk("receipt: 5 r86 entries", all(k in m for k in want),
        [k for k in want if k not in m])
    if not all(k in m for k in want):
        return
    ea, ep, ed, em, et = (m[k] for k in want)
    # ns name from the addr entry's own census
    ns = (ea.get("ns_leaf") or {})
    ns_name_s = None
    links = (ea["legs"].get("self_loop_census") or {}).get("links") or []
    if links:
        ns_name_s = links[0]["out"].split(":")[0]
    for e in (ea, ep, ed, em, et):
        e["ns_name"] = ns_name_s or ""
    chk("receipt: ns name resolved", bool(ns_name_s), ns_name_s)
    audit_addr(ea)
    audit_params(ep)
    audit_dsp(ed)
    audit_meta(em)
    audit_tools(et)
    for e, tag in ((ea, "addr"), (ep, "params"), (ed, "dsp"),
                   (em, "meta"), (et, "tools")):
        teardown(e, tag, ns_name_s or "", meta=(tag == "meta"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("receipts", nargs="+")
    ap.add_argument("--out")
    args = ap.parse_args()
    results = {}
    for path in args.receipts:
        del CHECKS[:]
        audit_receipt(path)
        bad = [c for c in CHECKS if not c["ok"]]
        results[path] = {"checks": len(CHECKS), "pass": len(CHECKS) - len(bad),
                         "fail": len(bad), "failing": bad}
        print(f"{path}: {len(CHECKS)} checks, "
              f"{len(CHECKS) - len(bad)} pass, {len(bad)} fail")
        for c in bad:
            print(f"   FAIL {c['name']} :: {c['detail']}")
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(results, fh, indent=2)
            fh.write("\n")
    return 1 if any(r["fail"] for r in results.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
