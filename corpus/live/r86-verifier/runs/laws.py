#!/usr/bin/env python3
"""r86-verifier independent law re-derivation (verifier-owned logic, no
fixture import). Each law is re-derived from raw receipt data only.

Usage: laws.py RECEIPT.json [RECEIPT.json ...]
"""
import json
import re
import sys

A = "pwctl_addr_r86_probe"
P = "pwctl_params_r86_probe"
D = "pwctl_dsp_r86_probe"
M = "pwctl_meta_r86_probe"
T = "pwctl_tools_r86_probe"


def pod_float(stdout, key):
    lines = (stdout or "").splitlines()
    for i, ln in enumerate(lines):
        if f":{key} (" in ln:
            for nxt in lines[i + 1:i + 3]:
                m = re.match(r"\s*Float ([-\d.]+)", nxt)
                if m:
                    return float(m.group(1))
    return None


def pct(stdout):
    m = re.search(r"(\d+)%", stdout or "")
    return int(m.group(1)) if m else None


def laws(R):
    out = []

    def law(name, ok, detail=""):
        out.append((name, bool(ok), str(detail)[:110]))

    def leg(ent, name):
        return R[ent]["legs"].get(name) or {}

    # ---------------- ADDR ----------------
    a = R[A]
    nid, ser = a["ns_leaf"]["node_id"], a["ns_leaf"]["object_serial"]
    l = leg(A, "ls_serial")
    law("addr.ls_serial_resolves_node",
        l.get("exit_code") == 0 and f'object.serial = "{ser}"' in (l.get("stdout") or "")
        and f"id {nid}," in (l.get("stdout") or ""), f"rc={l.get('exit_code')}")
    l = leg(A, "ls_id")
    law("addr.ls_id_empty_serial_namespace",
        l.get("exit_code") == 0 and f'object.serial = "{ser}"' not in (l.get("stdout") or ""),
        f"rc={l.get('exit_code')} bytes={l.get('stdout_bytes')}")
    l = leg(A, "info_id")
    law("addr.info_id_resolves", l.get("exit_code") == 0 and f"id: {nid}" in (l.get("stdout") or ""),
        f"rc={l.get('exit_code')}")
    for nm in ("info_serial", "enum_serial", "info_bogus"):
        l = leg(A, nm)
        law(f"addr.{nm}_rc0_unknown_global",
            l.get("exit_code") == 0 and l.get("error_class") == "pwcli_unknown_global",
            f"rc={l.get('exit_code')} class={l.get('error_class')}")
    for cls in ("Node", "Port", "Metadata", "Client"):
        l = leg(A, f"ls_{cls}")
        rows = re.findall(r"\bid (\d+),\s*type PipeWire:Interface:(\w+)/", l.get("stdout") or "")
        law(f"addr.ls_{cls}_typed_rows",
            l.get("exit_code") == 0 and rows and all(t == cls for _, t in rows)
            and l.get("typed_rows") == len(rows),
            f"rows={len(rows)} typed_rows={l.get('typed_rows')}")
    for cls in ("Bogus", "node", "Session"):
        l = leg(A, f"ls_{cls}")
        law(f"addr.ls_{cls}_indistinguishable_empty",
            l.get("exit_code") == 0 and l.get("stdout_bytes") == 0,
            f"rc={l.get('exit_code')} bytes={l.get('stdout_bytes')}")
    di, ds = leg(A, "dump_id"), leg(A, "dump_serial")
    law("addr.dump_id_serial_resolve_and_byte_equal",
        di.get("exit_code") == 0 and ds.get("exit_code") == 0
        and di.get("stdout_bytes", 0) > 0 and f'"id": {nid}' in (di.get("stdout") or "")
        and di.get("stdout") == ds.get("stdout"),
        f"bytes={di.get('stdout_bytes')}/{ds.get('stdout_bytes')}")
    for nm in ("dump_badid", "dump_bogus", "dump_color_sep"):
        l = leg(A, nm)
        law(f"addr.{nm}_silent_empty_rc0",
            l.get("exit_code") == 0 and l.get("stdout_bytes") == 0,
            f"rc={l.get('exit_code')} bytes={l.get('stdout_bytes')}")
    l = leg(A, "dump_color_join")
    law("addr.dump_color_join_dumps", l.get("exit_code") == 0 and (l.get("stdout_bytes") or 0) >= 1000,
        f"bytes={l.get('stdout_bytes')}")
    law("addr.dump_color_eq_record_only", leg(A, "dump_color_eq").get("armed") is False,
        f"armed={leg(A, 'dump_color_eq').get('armed')} bytes={leg(A, 'dump_color_eq').get('stdout_bytes')}")
    s1, s2 = leg(A, "dump_full1"), leg(A, "dump_full2")
    law("addr.self_client_exactly_one_per_invocation",
        s1.get("exit_code") == 0 and s2.get("exit_code") == 0
        and s1.get("self_clients") == 1 and s2.get("self_clients") == 1,
        f"selfs={s1.get('self_clients')}/{s2.get('self_clients')}")
    law("addr.self_serials_fresh_and_increasing",
        set(s1.get("self_serials") or []) != set(s2.get("self_serials") or [])
        and all(int(x) < int(y) for x, y in zip(sorted(s1.get("self_serials") or []),
                                                 sorted(s2.get("self_serials") or []))),
        f"{s1.get('self_serials')} -> {s2.get('self_serials')}")
    l = leg(A, "info_all")
    law("addr.info_all_rc0_bulk", l.get("exit_code") == 0 and (l.get("stdout_bytes") or 0) >= 10000,
        f"bytes={l.get('stdout_bytes')}")
    for nm in ("list_vars", "list_remotes"):
        l = leg(A, nm)
        law(f"addr.{nm}_rc0", l.get("exit_code") == 0 and (l.get("stdout_bytes") or 0) > 0,
            f"bytes={l.get('stdout_bytes')}")
    l = leg(A, "remote_down")
    law("addr.remote_down_real_nonzero",
        l.get("exit_code") not in (0, None) and "failed to connect" in (l.get("stderr") or ""),
        f"rc={l.get('exit_code')}")
    l = leg(A, "meta_info_empty")
    law("addr.info_live_metadata_silent_empty",
        l.get("exit_code") == 0 and l.get("stdout_bytes") == 0, f"bytes={l.get('stdout_bytes')}")
    l = leg(A, "mk_self_loop")
    links = leg(A, "self_loop_census").get("links") or []
    law("addr.self_loop_forms",
        l.get("exit_code") == 0 and any("monitor_FL" in x.get("out", "") and "playback_FL" in x.get("in", "")
                                        for x in links), f"links={len(links)}")
    l = leg(A, "info_link")
    law("addr.info_link_census_fields",
        l.get("exit_code") == 0 and all(k in (l.get("stdout") or "")
                                        for k in ("output-node-id", "input-node-id", "state")),
        f"rc={l.get('exit_code')}")
    l = leg(A, "destroy_link")
    law("addr.destroy_link_removes",
        l.get("exit_code") == 0 and not (leg(A, "destroy_census").get("surviving") or []),
        f"surviving={leg(A, 'destroy_census').get('surviving')}")

    # ---------------- PARAMS ----------------
    p = R[P]
    for nm in ("n_props", "n_propinfo", "n_enumformat", "p_enumformat", "p_latency",
               "p_io", "p_meta", "d_profile", "d_enumprofile", "d_enumroute"):
        l = leg(P, nm)
        law(f"params.{nm}_pod_present", l.get("exit_code") == 0 and l.get("has_pod") is True,
            f"rc={l.get('exit_code')} pod={l.get('has_pod')}")
    for nm in ("p_format", "n_latency", "n_proclat"):
        l = leg(P, nm)
        law(f"params.{nm}_pod_absent", l.get("exit_code") == 0 and l.get("has_pod") is False,
            f"pod={l.get('has_pod')}")
    law("params.n_format_armed_rc_only",
        leg(P, "n_format").get("exit_code") == 0 and leg(P, "n_format").get("armed") == "rc_only",
        f"armed={leg(P, 'n_format').get('armed')} pod={leg(P, 'n_format').get('has_pod')}")
    for nm in ("n_io", "n_meta", "n_profile", "p_props", "d_props"):
        l = leg(P, nm)
        law(f"params.{nm}_remote_enoent",
            l.get("exit_code") == 0 and l.get("error_class") == "pwcli_remote_enoent",
            f"class={l.get('error_class')}")
    law("params.d_route_record_only", leg(P, "d_route").get("armed") is False,
        f"armed={leg(P, 'd_route').get('armed')}")
    law("params.numeric_3_equals_enumformat",
        leg(P, "n_num3").get("stdout") == leg(P, "n_enumformat").get("stdout"),
        f"equal={leg(P, 'n_num3').get('stdout') == leg(P, 'n_enumformat').get('stdout')}")
    for nm in ("n_bogus", "n_999", "n_all", "sp_bogusp"):
        l = leg(P, nm)
        law(f"params.{nm}_unknown_param",
            l.get("exit_code") == 0 and l.get("error_class") == "pwcli_unknown_param",
            f"class={l.get('error_class')}")
    l = leg(P, "enum_badobj")
    law("params.enum_badobj_unknown_global",
        l.get("exit_code") == 0 and l.get("error_class") == "pwcli_unknown_global",
        f"class={l.get('error_class')}")
    for nm in ("c_props", "f_props", "m_props", "l_props", "core_setparam"):
        l = leg(P, nm)
        law(f"params.{nm}_not_implemented",
            l.get("exit_code") == 0 and l.get("error_class") == "pwcli_not_impl",
            f"class={l.get('error_class')}")
    l = leg(P, "sp_garbage")
    law("params.sp_garbage_none_echo", l.get("exit_code") == 0
        and (l.get("stdout") or "").strip() == "None", f"out={(l.get('stdout') or '').strip()[:20]!r}")
    law("params.sp_empty_pod_echo", leg(P, "sp_empty").get("has_pod") is True,
        f"pod={leg(P, 'sp_empty').get('has_pod')}")
    law("params.sp_zzz_stripped_keys",
        leg(P, "sp_zzz").get("exit_code") == 0 and "zzz" not in (leg(P, "re_zzz").get("stdout") or ""),
        "unknown key not stored")
    law("params.sp_voltype_none_slot", "None" in (leg(P, "sp_voltype").get("stdout") or ""),
        "wrong-type -> None slot")
    law("params.sp_enumf_remote_notsup",
        leg(P, "sp_enumf").get("error_class") == "pwcli_remote_notsup",
        f"class={leg(P, 'sp_enumf').get('error_class')}")
    l = leg(P, "sp_port_lat")
    law("params.sp_port_lat_local_not_impl",
        l.get("exit_code") == 0 and l.get("error_class") == "pwcli_not_impl"
        and "Interface:Port" in (l.get("error_hit") or ""), f"class={l.get('error_class')}")
    law("params.port_latency_write_dropped",
        pod_float(leg(P, "re_port_lat").get("stdout"), "minQuantum") == 0.0,
        f"minQuantum={pod_float(leg(P, 're_port_lat').get('stdout'), 'minQuantum')}")
    law("params.props_volume_readback_stable",
        pod_float(leg(P, "re_vol").get("stdout"), "volume") == 1.0,
        f"volume={pod_float(leg(P, 're_vol').get('stdout'), 'volume')}")
    l = leg(P, "sp_badid")
    law("params.sp_badid_unknown_global", l.get("error_class") == "pwcli_unknown_global",
        f"class={l.get('error_class')}")
    l = leg(P, "sp_nojson")
    law("params.sp_nojson_usage", l.get("error_class") == "pwcli_usage", f"class={l.get('error_class')}")

    # ---------------- DSP ----------------
    d = R[D]
    edges = leg(D, "tap_link").get("edges") or []
    law("dsp.tap_link_two_edges_active",
        len(edges) == 2 and all(e.get("state") == "active" for e in edges),
        f"edges={len(edges)}")
    law("dsp.player_attached",
        leg(D, "player_attach").get("stream_index") is not None
        and leg(D, "player_attach").get("sink") is not None, "")
    w = leg(D, "writes")
    law("dsp.all_writes_rc0", all((v or {}).get("exit_code") == 0 for v in w.values()),
        f"rcs={ {k: v.get('exit_code') for k, v in w.items()} }")
    reg = leg(D, "regions")
    bounds = {"solo": (8000, 10000), "cv25": (2000, 2100), "cv50": (4000, 4200),
              "mute": (0, 0), "reset": (8000, 10000), "dead": (8000, 10000),
              "pa25": (120, 140), "pa100": (8000, 10000)}
    for k, (lo, hi) in bounds.items():
        v = (reg.get(k) or {}).get("median_peak")
        law(f"dsp.region_{k}_in_envelope", v is not None and lo <= v <= hi, f"median={v}")
    law("dsp.pactl_scale_coupling",
        pct(leg(D, "pactl_after_cv25").get("stdout")) in (62, 63, 64)
        and pct(leg(D, "pactl_after_cv50").get("stdout")) in (78, 79, 80)
        and pct(leg(D, "pactl_after_dead").get("stdout")) == 100,
        f"cv25={pct(leg(D, 'pactl_after_cv25').get('stdout'))} "
        f"cv50={pct(leg(D, 'pactl_after_cv50').get('stdout'))} "
        f"dead={pct(leg(D, 'pactl_after_dead').get('stdout'))}")
    law("dsp.pactl_read_25_100",
        pct(leg(D, "pactl_read_25").get("stdout")) == 25
        and pct(leg(D, "pactl_read_100").get("stdout")) == 100,
        f"25={pct(leg(D, 'pactl_read_25').get('stdout'))} 100={pct(leg(D, 'pactl_read_100').get('stdout'))}")
    law("dsp.scalar_volume_display_dead",
        pod_float(leg(D, "enum_after_dead").get("stdout"), "volume") == 0.25,
        f"volume={pod_float(leg(D, 'enum_after_dead').get('stdout'), 'volume')}")
    law("dsp.player_alive_at_end", leg(D, "player_alive_at_end") is True, "")
    law("dsp.tap_peak_all_8192", leg(D, "tap_peak_all") == 8192, f"peak={leg(D, 'tap_peak_all')}")

    # ---------------- META ----------------
    m = R[M]
    cen = m.get("meta_census") or {}
    law("meta.census_nine_stores_ls_agree",
        len(cen.get("store_ids") or []) == 9 and cen.get("store_ids") == cen.get("ls_ids"),
        f"stores={cen.get('store_ids')}")
    law("meta.dump_sees_strict_subset",
        set(cen.get("dump_ids") or []) < set(cen.get("store_ids") or [])
        and len(cen.get("dump_ids") or []) >= 1,
        f"dump_ids={cen.get('dump_ids')}")
    l = leg(M, "meta_list")
    law("meta.meta_list_9_rows", l.get("exit_code") == 0 and l.get("stdout_lines") == 9,
        f"lines={l.get('stdout_lines')}")
    for nm in ("meta_bare", "meta_default"):
        l = leg(M, nm)
        law(f"meta.{nm}_default_store_found",
            l.get("exit_code") == 0 and 'Found "default" metadata 39' in (l.get("stdout") or ""),
            f"rc={l.get('exit_code')}")
    l = leg(M, "meta_bogus")
    law("meta.meta_bogus_silent_empty",
        l.get("exit_code") == 0 and l.get("stdout_bytes") == 0, f"bytes={l.get('stdout_bytes')}")
    law("meta.echo_write_read_v1",
        re.search(r"set property: id:\d+ key:r86a_k value:v1",
                  leg(M, "m_write").get("stdout") or "")
        and re.search(r"update: id:\d+ key:'r86a_k' value:'v1'",
                      leg(M, "m_read").get("stdout") or ""), "")
    law("meta.overwrite_read_v2",
        re.search(r"set property: id:\d+ key:r86a_k value:v2",
                  leg(M, "m_over").get("stdout") or "")
        and re.search(r"update: id:\d+ key:'r86a_k' value:'v2'",
                      leg(M, "m_read2").get("stdout") or ""), "")
    law("meta.typed_roundtrip",
        "type:'Spa:String'" in (leg(M, "m_read3").get("stdout") or ""), "")
    law("meta.absent_read_no_update_row",
        "update:" not in (leg(M, "m_absent").get("stdout") or ""), "")
    law("meta.delete_then_absent",
        re.search(r"delete property: id:\d+ key:r86a_k$",
                  (leg(M, "m_del").get("stdout") or "").strip())
        and "update:" not in (leg(M, "m_read4").get("stdout") or ""), "")
    law("meta.delete_absent_silent",
        leg(M, "m_delabsent").get("exit_code") == 0
        and re.search(r"delete property: id:\d+ key:r86a_k_nope",
                      leg(M, "m_delabsent").get("stdout") or ""), "")
    law("meta.dead_subject_echo_no_readback",
        "set property: id:99997" in (leg(M, "m_dead_w").get("stdout") or "")
        and "update:" not in (leg(M, "m_dead_r").get("stdout") or ""), "")
    law("meta.wipe_subject_then_empty",
        re.search(r"delete properties: id:\d+$",
                  (leg(M, "m_wipe").get("stdout") or "").strip())
        and "update:" not in (leg(M, "m_read5").get("stdout") or ""), "")
    law("meta.keys_gone_after_teardown", m.get("meta_keys_gone") is True,
        f"meta_keys_gone={m.get('meta_keys_gone')}")
    l = leg(M, "m_filter")
    law("meta.filter_monitor_sees_own_key",
        l.get("signal") == "SIGKILL" and l.get("killed_at_bound") is True
        and "r86a_k_f" in (l.get("stdout") or ""), f"sig={l.get('signal')}")
    l = leg(M, "m_filter0")
    law("meta.filter0_monitor_subject0",
        l.get("signal") == "SIGKILL" and l.get("killed_at_bound") is True
        and "id:0" in (l.get("stdout") or ""), f"sig={l.get('signal')}")

    # ---------------- TOOLS ----------------
    t = R[T]
    l = leg(T, "cli_devnull")
    law("tools.pwcli_eof_sigabrt",
        l.get("exit_code") == -6 and l.get("signal") == "SIGABRT"
        and l.get("error_class") == "pw_loop_assert", f"rc={l.get('exit_code')}")
    l = leg(T, "cli_pipe")
    law("tools.pwcli_pipe_never_exits_killed_at_bound",
        l.get("exit_code") == -9 and l.get("signal") == "SIGKILL" and l.get("killed_at_bound") is True,
        f"rc={l.get('exit_code')}")
    l = leg(T, "cli_quit")
    law("tools.pwcli_quit_rc0", l.get("exit_code") == 0, f"rc={l.get('exit_code')}")
    jack_envs = {"jack_p": {"Q": "512/48000", "D": "unset", "R": "unset"},
                 "jack_sp": {"Q": "256/44100", "D": "unset", "R": "unset"},
                 "jack_s_only": {"Q": "unset", "D": "unset", "R": "unset"},
                 "jack_v": {"Q": "unset", "D": "3", "R": "unset"},
                 "jack_vv": {"Q": "unset", "D": "4", "R": "unset"},
                 "jack_v_preset": {"Q": "unset", "D": "5", "R": "unset"}}
    for nm, env in jack_envs.items():
        got = leg(T, nm).get("env") or {}
        law(f"tools.{nm}_env", got == env, f"got={got}")
    got = leg(T, "jack_r").get("env") or {}
    law("tools.jack_r_remote_env",
        got.get("R", "").startswith("r86a_") and got.get("R", "").endswith("_remote")
        and got.get("Q") == "unset" and got.get("D") == "unset", f"R={got.get('R')}")
    for nm, rc, cls in (("lk_dup", 255, "pwlink_exists"),
                        ("lk_bogus", 255, "pwlink_noent"),
                        ("lk_usage", 255, "pwlink_usage"),
                        ("lk_I_alone", 255, "pwlink_usage"),
                        ("lk_v_alone", 255, "pwlink_usage")):
        l = leg(T, nm)
        law(f"tools.{nm}_rc_cls", l.get("exit_code") == rc and l.get("error_class") == cls,
            f"rc={l.get('exit_code')} class={l.get('error_class')}")
    for nm in ("lk_create",):
        law(f"tools.{nm}_rc0", leg(T, nm).get("exit_code") == 0, f"rc={leg(T, nm).get('exit_code')}")
    law("tools.lk_list_rows", (leg(T, "lk_list").get("stdout_lines") or 0) > 0, "")
    law("tools.lk_list_I_rows", (leg(T, "lk_list_I").get("stdout_lines") or 0) > 0, "")
    law("tools.lk_census_own_link",
        any("monitor_FL" in x.get("out", "") for x in (leg(T, "lk_census").get("links") or [])), "")
    l = leg(T, "lk_d_port")
    law("tools.lk_d_port_rc255", l.get("exit_code") == 255 and l.get("error_class") == "pwlink_noent",
        f"rc={l.get('exit_code')}")
    law("tools.lk_d_link_rc0", leg(T, "lk_d_link").get("exit_code") == 0, "")
    law("tools.lk_after_unlink_empty", (leg(T, "lk_after_unlink").get("links") or []) == [], "")
    law("tools.lk_junkprops_accepted",
        leg(T, "lk_junkprops").get("exit_code") == 0
        and any("monitor_FR" in x.get("out", "") for x in (leg(T, "lk_junkprops_census").get("links") or [])), "")
    law("tools.lk_junkprops_unlink_rc0", leg(T, "lk_junkprops_unlink").get("exit_code") == 0, "")
    l = leg(T, "top_batch")
    law("tools.top_batch_rc0", l.get("exit_code") == 0, f"rc={l.get('exit_code')}")
    l = leg(T, "top_batch0")
    law("tools.top_batch0_rc0", l.get("exit_code") == 0, f"rc={l.get('exit_code')}")
    l = leg(T, "top_batch_term")
    law("tools.top_batch_term_clean",
        l.get("exit_code") == 0 and l.get("loop_assert") is False, f"rc={l.get('exit_code')}")
    l = leg(T, "top_tui_term")
    law("tools.top_tui_term_sigabrt",
        l.get("exit_code") == -6 and l.get("signal") == "SIGABRT" and l.get("loop_assert") is True,
        f"rc={l.get('exit_code')}")
    l = leg(T, "top_tui_kill")
    law("tools.top_tui_kill_sigkill",
        l.get("exit_code") == -9 and l.get("signal") == "SIGKILL", f"rc={l.get('exit_code')}")
    l = leg(T, "jack_bogus")
    law("tools.jack_bogus_rc127", l.get("exit_code") == 127, f"rc={l.get('exit_code')}")
    l = leg(T, "jack_badopt")
    law("tools.jack_badopt_usage_rc0",
        l.get("exit_code") == 0 and "illegal option" in (l.get("stderr") or ""), f"rc={l.get('exit_code')}")

    # ---------------- CUSTODY (all entries) ----------------
    for ent in (A, P, D, M, T):
        e = R[ent]
        sg = e.get("sinks_gone")
        law(f"custody.{ent.split('_')[1]}_sinks_gone",
            isinstance(sg, dict) and sg and all(v is True for v in sg.values()), f"{sg}")
        law(f"custody.{ent.split('_')[1]}_own_nodes_gone", (e.get("own_nodes_after") or []) == [],
            f"{e.get('own_nodes_after')}")
        for tag, u in (e.get("unloads") or {}).items():
            law(f"custody.{ent.split('_')[1]}_unload_verified",
                (u or {}).get("verified_index") == (u or {}).get("captured")
                and (u or {}).get("recycled") is False and (u or {}).get("exit_code") == 0,
                f"{tag} idx={(u or {}).get('verified_index')} cap={(u or {}).get('captured')}")
    return out


def main():
    files = sys.argv[1:]
    results = {}
    for f in files:
        R = json.load(open(f))["measurements"]
        results[f] = laws(R)
    names = [n for n, _, _ in results[files[0]]]
    width = max(len(n) for n in names)
    for f in files:
        npass = sum(1 for _, ok, _ in results[f] if ok)
        print(f"== {f}: {npass}/{len(results[f])} PASS")
    for n, ok0, _ in results[files[0]]:
        row = []
        for f in files:
            d = dict((x, (o, dd)) for x, o, dd in results[f])
            o, dd = d[n]
            row.append("PASS" if o else f"FAIL({dd})")
        print(f"{n:<{width}}  " + "  ".join(row))
    return 0 if all(ok for f in files for _, ok, _ in results[f]) else 1


if __name__ == "__main__":
    sys.exit(main())
