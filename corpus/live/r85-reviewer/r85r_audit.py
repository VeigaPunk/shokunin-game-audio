#!/usr/bin/env python3
"""r85 reviewer audit — re-derive every armed r85 verdict from the
COMMITTED receipts alone (no live host), independently of the fixture's
own verdict code. Emits a check table + a JSON summary.

Usage: python3 r85r_audit.py <run1.json> <run2.json>
"""
import json
import re
import sys


def load(p):
    d = json.load(open(p))
    return d["measurements"]


def legs(d, name):
    return d[name]["legs"]


def med(windows, key):
    vals = [w[key] for w in windows if key in w]
    return sum(vals) / len(vals) if vals else None


def link_ports(leg):
    return {e.get("out_port_name") for s in leg.get("samples", [])
            for e in s.get("links", [])}


def links_of(leg):
    return [e for s in leg.get("samples", []) for e in s.get("links", [])]


def run_checks(d, run):
    out = []
    add = lambda ok, name, detail: out.append(
        {"run": run, "check": name, "ok": bool(ok), "detail": detail})

    # ---------- addr entry ----------
    L = legs(d, "pactlmon_addr_r85_probe")
    add(len(L) == 40, "addr.leg_count", len(L))
    # serial-is-the-number: name/serial/defsink/parse edges rc0 + Volume
    for nm in ("g_name", "g_serial", "g_defsink", "g_leadspace",
               "g_plus", "g_float", "g_xsuf", "g_hex"):
        l = L[nm]
        add(l.get("exit_code") == 0 and "Volume:" in (l.get("stdout") or ""),
            f"addr.{nm}.rc0_volume", f"rc={l.get('exit_code')}")
    pct = lambda l: int(re.search(r"(\d+)\s*%", l.get("stdout") or "").group(1)) \
        if re.search(r"(\d+)\s*%", l.get("stdout") or "") else None
    add(pct(L["g_serial"]) == pct(L["g_name"]),
        "addr.serial_row_equals_name_row",
        f"{pct(L['g_serial'])} vs {pct(L['g_name'])}")
    for nm in ("g_objid", "g_defsrc", "g_defmon", "g_monitor_as_sink",
               "g_bogus", "g_huge", "g_neg", "g_uscr", "g_defsinkX"):
        l = L[nm]
        add(l.get("exit_code") == 1 and
            l.get("error_class") == "pa_get_info_noent",
            f"addr.{nm}.noent", f"rc={l.get('exit_code')} "
            f"cls={l.get('error_class')}")
    l = L["g_empty"]
    add(l.get("exit_code") == 1 and l.get("error_class") == "pa_invalid_arg",
        "addr.g_empty.invalid_arg", f"rc={l.get('exit_code')} "
        f"cls={l.get('error_class')}")
    add(L["g_zero"].get("exit_code") == 0 and
        pct(L["g_zero"]) == pct(L["g_defsink"]),
        "addr.g_zero.live_default", f"pct={pct(L['g_zero'])} "
        f"def={pct(L['g_defsink'])}")
    add(L["g_lead0"].get("armed") is False, "addr.g_lead0.record_only",
        f"armed={L['g_lead0'].get('armed')} rc={L['g_lead0'].get('exit_code')}")
    for nm in ("s_monitor_name", "s_sink_serial", "s_defmon", "s_defsrc",
               "s_zero"):
        l = L[nm]
        add(l.get("exit_code") == 0 and "Volume:" in (l.get("stdout") or ""),
            f"addr.{nm}.rc0_volume", f"rc={l.get('exit_code')}")
    add(pct(L["s_sink_serial"]) == pct(L["s_monitor_name"]),
        "addr.monitor_shares_sink_serial",
        f"{pct(L['s_sink_serial'])} vs {pct(L['s_monitor_name'])}")
    for nm in ("s_sinkname", "s_defsink", "s_bogus"):
        l = L[nm]
        add(l.get("exit_code") == 1 and
            l.get("error_class") == "pa_get_info_noent",
            f"addr.{nm}.sink_refusal", f"rc={l.get('exit_code')} "
            f"cls={l.get('error_class')}")
    # pw-cli inversion
    add(L["pwcli_id"].get("exit_code") == 0 and
        str(L["pwcli_id"].get("stdout", "")).find(
            str(d["pactlmon_addr_r85_probe"]["ns_props"]["node_id"])) >= 0,
        "addr.pwcli_id_resolves",
        f"rc={L['pwcli_id'].get('exit_code')}")
    blob = (L["pwcli_serial"].get("stderr") or "") + \
        (L["pwcli_serial"].get("stdout") or "")
    add(L["pwcli_serial"].get("exit_code") == 0 and
        "unknown global" in blob, "addr.pwcli_serial_rc0_lie",
        f"rc={L['pwcli_serial'].get('exit_code')}")
    # moves
    si = d["pactlmon_addr_r85_probe"]["sink_index"]
    a1 = (L["mv_name"].get("after") or {})
    add(L["mv_name"]["pactl"].get("exit_code") == 0 and
        a1.get("sink") == si["ns2"], "addr.mv_name", a1.get("sink"))
    a2 = (L["mv_serial"].get("after") or {})
    add(L["mv_serial"]["pactl"].get("exit_code") == 0 and
        a2.get("sink") == si["ns"], "addr.mv_serial", a2.get("sink"))
    add(L["mv_bogus"]["pactl"].get("exit_code") != 0 and
        (L["mv_bogus"].get("after") or {}).get("sink") == a2.get("sink"),
        "addr.mv_bogus_refuses_and_stays",
        f"rc={L['mv_bogus']['pactl'].get('exit_code')}")
    cm = L["cdup_move"]
    add(cm["pactl"].get("exit_code") == 0 and
        (cm.get("after") or {}).get("sink") == si["ns"],
        "addr.cdup_move_serial_first",
        f"after={(cm.get('after') or {}).get('sink')} ns={si['ns']}")
    # cdup_cap realization — re-derive independently from raw link shapes
    cl = L["cdup_cap"]
    ns_name = L["g_name"]["argv"].split()[-1]
    mon = [e for e in links_of(cl)
           if (e.get("out_port_name") or "").startswith("monitor_")]
    if mon and all(e.get("out_node") == ns_name for e in mon):
        want_real = "serial_monitor_bypass"
    elif mon:
        want_real = "foreign_monitor"
    elif links_of(cl):
        want_real = "name_shadow_bound"
    elif cl.get("exit_code") == 1 and not cl.get("alive_at_end"):
        want_real = "refused"
    elif cl.get("alive_at_end"):
        want_real = "stalled"
    else:
        want_real = "other"
    add(cl["realization"] == want_real,
        "addr.cdup_cap.label_matches_links",
        f"{cl['realization']} vs re-derived {want_real} "
        f"(mon={len(mon)} links={len(links_of(cl))})")
    add(cl["realization"] != "foreign_monitor" and
        cl["realization"] != "other",
        "addr.cdup_cap.either_way_nonforeign", cl["realization"])
    # serial monotonicity (re-derive from raw rows)
    sc = d["pactlmon_addr_r85_probe"]["serial_cycles"]
    sers, mods = sc["serials"], sc["module_indices"]
    add(len(sers) == 3 and len(set(sers)) == 3 and sers == sorted(sers),
        "addr.serials_strictly_increasing", sers)
    add(len(set(mods)) == 1, "addr.module_index_recycled", mods)

    # ---------- mix entry ----------
    M = legs(d, "pactlmon_mix_r85_probe")
    add(len(M) == 7, "mix.leg_count", len(M))
    for nm in ("solo", "mix2", "mixdup", "mixdelay", "mixinv", "mixclip"):
        edges = M[nm].get("tap_link") or []
        add(bool(edges) and all((e.get("out_port_name") or "")
                                .startswith("monitor_") for e in edges),
            f"mix.{nm}.tap_link_validated",
            f"n={len(edges)}")
    solo = M["solo"]["ref"]
    add(solo["l_a"] is not None and 0.85 * 8192 <= solo["l_a"] <= 1.18 * 8192
        and 0.85 * 8192 <= solo["r_b"] <= 1.18 * 8192,
        "mix.solo_ref_window", solo)
    add((solo["r_a_bleed"] or 0) <= 0.05 * 8192 and
        (solo["l_b_bleed"] or 0) <= 0.05 * 8192,
        "mix.solo_zero_bleed", solo)
    ref = min(solo["l_a"], solo["r_b"])
    for k in ("l_a", "r_b", "l_c", "r_d"):
        v = M["mix2"]["meds"][k]
        add(0.85 * ref <= v <= 1.18 * ref, f"mix.mix2.{k}.full_amp",
            f"{v} vs ref {ref}")
    for k in ("r_a", "l_b", "r_c", "l_d"):
        v = M["mix2"]["bleed"][k]
        add(v <= 0.05 * ref, f"mix.mix2.{k}.zero_bleed", v)
    edges = M["mix2"]["mix_edges"]
    ports = {e.get("in") for e in edges}
    outs = {e.get("out") for e in edges}
    add(len(edges) == 4 and len(ports) == 2 and
        all(":playback_" in p for p in ports),
        "mix.mix2.four_links_two_ports", f"edges={len(edges)} ports={ports}")
    add(len(outs) >= 4, "mix.mix2.four_producers", len(outs))
    # re-derive the classification labels from the raw ratio
    def classify(r):
        if r is None:
            return "unmeasured"
        if 1.80 <= r <= 2.20:
            return "coherent_2x"
        if r < 0.12:
            return "cancelled"
        return "partial"
    add(classify(M["mixdup"]["dup_ratio"]) == M["mixdup"]["realization"],
        "mix.mixdup.label_matches_ratio",
        f"{M['mixdup']['dup_ratio']} -> {M['mixdup']['realization']}")
    add(M["mixdup"]["dup_ratio"] <= 2.05, "mix.mixdup.linear_bound",
        M["mixdup"]["dup_ratio"])
    add(classify(M["mixdelay"]["delay_ratio"]) ==
        M["mixdelay"]["realization"], "mix.mixdelay.label_matches_ratio",
        f"{M['mixdelay']['delay_ratio']} -> {M['mixdelay']['realization']}")
    add(M["mixdelay"]["delay_ratio"] <= 2.05, "mix.mixdelay.linear_bound",
        M["mixdelay"]["delay_ratio"])
    add(M["mixinv"]["realization"] ==
        ("cancelled" if M["mixinv"]["residual_ratio"] < 0.12 else "slipped"),
        "mix.mixinv.label_matches_ratio",
        f"{M['mixinv']['residual_ratio']} -> {M['mixinv']['realization']}")
    add(M["mixinv"]["residual_ratio"] <= 2.05, "mix.mixinv.bound",
        M["mixinv"]["residual_ratio"])
    clip = M["mixclip"]["clip"]
    add(clip["peak_med"] >= 32767, "mix.mixclip.rail_peak", clip)
    add(0.08 <= clip["rail_frac_med"] <= 0.60, "mix.mixclip.rail_envelope",
        clip)
    add(clip["spur_max"] >= 300.0, "mix.mixclip.spur_floor", clip)

    # ---------- aplay env ----------
    A = legs(d, "pactlmon_aplayenv_r85_probe")
    add(len(A) == 6, "aplayenv.leg_count", len(A))
    def consumers(leg):
        return [c.get("consumers") for c in (leg.get("nodes_mid") or [])]
    ns = None
    # derive ns name from the graph candidates of env_node
    hits = A["env_node"].get("target_candidates") or []
    add(bool(hits), "aplayenv.env_node.publishes_target",
        len(hits))
    for nm in ("env_node", "env_props", "env_conflict"):
        hs = A[nm].get("target_candidates") or []
        add(bool(hs) and any(
            any(str(x).startswith("r85a_ns_") for x in
                (c.get("consumers") or [])) for c in hs),
            f"aplayenv.{nm}.links_named_sink", consumers(A[nm]))
    add(not any("r85a_ns2_" in str(c) for c in
                [x for cs in consumers(A["env_conflict"]) for x in (cs or [])]),
        "aplayenv.env_conflict.props_win_no_ns2",
        consumers(A["env_conflict"]))
    hs = A["env_serial"].get("target_candidates") or []
    add(bool(hs) and any(
        any(str(x).startswith("r85a_ns_") for x in (c.get("consumers") or []))
        for c in hs), "aplayenv.env_serial.resolves",
        A["env_serial"].get("target_candidates"))
    add(bool(A["env_bogus"].get("target_candidates")),
        "aplayenv.env_bogus.publishes_bogus_target",
        len(A["env_bogus"].get("target_candidates") or []))
    def_sink = d["pactlmon_aplayenv_r85_probe"]["inventory"]["default_sink"]
    for nm in ("env_bogus", "env_none"):
        l = A[nm]
        pool = (l.get("target_candidates") if nm == "env_bogus"
                else l.get("nodes_mid")) or []
        add(any(def_sink in (c.get("consumers") or []) for c in pool),
            f"aplayenv.{nm}.silent_default_fallback",
            f"default={def_sink}")

    # ---------- capture ----------
    C = legs(d, "pactlmon_capture_r85_probe")
    add(len(C) == 17, "capture.leg_count", len(C))
    bp = link_ports(C["cap_baseline"])
    add(bool(bp) and all((p or "").startswith("capture_") for p in bp),
        "capture.baseline.capture_bind", bp)
    add((C["cap_baseline"]["nz"] or {}).get("peak", 0) >= 1000,
        "capture.baseline.content", C["cap_baseline"]["nz"])
    for rep in range(2):
        l = C[f"cap_loss_{rep}"]
        sams = l.get("samples") or []
        post_links = [e for s in sams[1:] for e in s.get("links", [])]
        add(bool(sams[0].get("links")), f"capture.loss{rep}.pre_links",
            len(sams[0].get("links", [])))
        add(not post_links, f"capture.loss{rep}.no_reform", post_links)
        add(l.get("alive_at_end"), f"capture.loss{rep}.alive",
            l.get("alive_at_end"))
        add(l["unloaded"].get("exit_code") == 0,
            f"capture.loss{rep}.name_verified_unload",
            l["unloaded"])
        post = l["post"]
        add((post.get("post_frames") or 0) <= 16384,
            f"capture.loss{rep}.flush_bound", post)
        add(sams[-1].get("size") == sams[-2].get("size"),
            f"capture.loss{rep}.growth_ceased",
            f"{sams[-2].get('size')}->{sams[-1].get('size')}")
        add(post.get("realization") in ("froze", "grew_zeros",
                                        "grew_content"),
            f"capture.loss{rep}.shape_recorded", post.get("realization"))
    lp = link_ports(C["cap_loss_prop"])
    post_l = C["cap_loss_prop"]["post_links"]
    add(bool(post_l) and all(
        e.get("out_node") == def_sink and
        (e.get("out_port_name") or "").startswith("monitor_")
        for e in post_l), "capture.loss_prop.default_monitor",
        f"default={def_sink} n={len(post_l)}")
    # lattice
    tsp = link_ports(C["t_sinkname"])
    add(not any((p or "").startswith("monitor_") for p in tsp),
        "capture.t_sinkname.never_monitor", tsp)
    add(C["t_sinkname"]["realization"] != "other",
        "capture.t_sinkname.known_realization",
        C["t_sinkname"]["realization"])
    sp = link_ports(C["t_sinkserial"])
    ns2_name = C["t_sinkname"]["target"]
    add(bool(sp) and all((p or "").startswith("monitor_") for p in sp) and
        any(e.get("out_node") == ns2_name for e in links_of(C["t_sinkserial"])),
        "capture.t_sinkserial.monitor_bypass", sp)
    for nm in ("t_srcname", "t_srcserial", "t_srcid"):
        lp = link_ports(C[nm])
        add(bool(lp) and all((p or "").startswith("capture_") for p in lp),
            f"capture.{nm}.source_bind", lp)
    lp = link_ports(C["t_prop_sinkname"])
    add(bool(lp) and all((p or "").startswith("monitor_") for p in lp),
        "capture.t_prop_sinkname.monitor", lp)
    pl = links_of(C["t_prop_srcname"])
    add(bool(pl) and all((e.get("out_port_name") or "")
                         .startswith("monitor_") for e in pl) and
        any(e.get("out_node") == def_sink for e in pl),
        "capture.t_prop_srcname.default_monitor", f"default={def_sink}")
    # self-destruct
    l = C["sd_idle"]
    add(l.get("module_dead_at_s") is None and
        l.get("source_dead_at_s") is None, "capture.sd_idle.survives",
        (l.get("module_dead_at_s"), l.get("source_dead_at_s")))
    for nm in ("sd_record", "sd_parec"):
        l = C.get(nm) or {}
        add(l.get("module_dead_at_s") is not None and
            l["module_dead_at_s"] <= 1.5, f"capture.{nm}.bind_kill",
            l.get("module_dead_at_s"))
        add((l.get("out") or {}).get("data_actual", 0) <= 200 and
            not l.get("links"), f"capture.{nm}.no_content_no_links",
            l.get("out"))
    l = C["sd_prop"]
    plinks = links_of(l)
    add(l["realization"] in ("clean_default_fallback",
                             "bind_killed_then_default"),
        "capture.sd_prop.realization_known", l["realization"])
    add(l["realization"] == ("clean_default_fallback"
                             if not l["sd_module_gone_after"]
                             else "bind_killed_then_default"),
        "capture.sd_prop.label_matches_module_fate",
        (l["realization"], l["sd_module_gone_after"]))
    add(bool(plinks) and all((e.get("out_port_name") or "")
                             .startswith("monitor_") for e in plinks),
        "capture.sd_prop.monitor_only", len(plinks))
    add(any(e.get("out_node") == def_sink for e in plinks),
        "capture.sd_prop.default_monitor", def_sink)
    l = C["sd_pwlink"]
    add(l.get("module_alive") and l.get("source_alive"),
        "capture.sd_pwlink.survives", (l.get("module_alive"),
                                       l.get("source_alive")))
    # latebind
    l = C["latebind"]
    lk = links_of(l)
    good = bool(lk) and all(
        e.get("out_node", "").startswith("r85a_late_") and
        (e.get("out_port_name") or "").startswith("capture_") for e in lk)
    add(l["realization"] == ("late_bound" if good else
                             "stalled" if l.get("alive_at_end") else
                             "refused" if l.get("exit_code") == 1 else
                             "other"), "capture.latebind.label_matches_links",
        f"{l['realization']} links={len(lk)}")
    add(l["realization"] in ("late_bound", "stalled", "refused"),
        "capture.latebind.either_way", l["realization"])

    # ---------- negctl ----------
    N = legs(d, "pactlmon_negctl_r85_probe")
    add(len(N) == 17, "negctl.leg_count", len(N))
    bad = [k for k, v in N.items() if k.startswith("u_") and
           v.get("got") != v.get("expect")]
    add(not bad, "negctl.unit_table_got_equals_expect", bad)
    add(N["ctl_pactl_info"]["exit_code"] == 0 and
        not N["ctl_pactl_info"]["error_class"], "negctl.ctl_pactl_info",
        N["ctl_pactl_info"]["exit_code"])
    add(N["ctl_pwdump"]["exit_code"] == 0 and
        not N["ctl_pwdump"]["error_class"], "negctl.ctl_pwdump",
        N["ctl_pwdump"]["exit_code"])
    add(N["ctl_pwcli_ser"]["exit_code"] == 0 and "unknown global" in
        (N["ctl_pwcli_ser"].get("stderr") or "") +
        (N["ctl_pwcli_ser"].get("stdout") or ""),
        "negctl.ctl_pwcli_ser", N["ctl_pwcli_ser"]["exit_code"])
    add(N["ctl_sigkill"]["signal"] == "SIGKILL" and
        N["ctl_sigkill"]["error_class"] is None,
        "negctl.ctl_sigkill_discriminator",
        (N["ctl_sigkill"]["signal"], N["ctl_sigkill"]["error_class"]))

    # ---------- teardown witnesses ----------
    for ent in ("pactlmon_addr_r85_probe", "pactlmon_mix_r85_probe",
                "pactlmon_aplayenv_r85_probe", "pactlmon_capture_r85_probe",
                "pactlmon_negctl_r85_probe"):
        e = d[ent]
        add(e.get("own_nodes_after") == [], f"{ent}.own_nodes_after",
            e.get("own_nodes_after"))
        sg = e.get("sinks_gone")
        if isinstance(sg, dict):
            add(all(sg.values()), f"{ent}.sinks_gone", sg)
        src = e.get("sources_gone")
        if isinstance(src, dict) and src:
            add(all(src.values()), f"{ent}.sources_gone", src)
        add(not e.get("failures"), f"{ent}.failures_empty", e.get("failures"))
    return out


def main():
    r1 = load(sys.argv[1])
    r2 = load(sys.argv[2])
    checks = run_checks(r1, "run1") + run_checks(r2, "run2")
    fails = [c for c in checks if not c["ok"]]
    print(f"checks={len(checks)} pass={len(checks) - len(fails)} "
          f"fail={len(fails)}")
    for c in fails:
        print(f"FAIL {c['run']} {c['check']}: {c['detail']}")
    # volatile-diff surface between the two runs
    print("\n-- cross-run volatile surface (documented) --")
    for ent, keys in (("pactlmon_mix_r85_probe",
                       ["mixdup", "mixdelay", "mixinv"]),):
        for k in keys:
            print(ent, k, "run1=", r1[ent]["legs"][k].get("realization"),
                  r1[ent]["legs"][k].get("dup_ratio") or
                  r1[ent]["legs"][k].get("delay_ratio") or
                  r1[ent]["legs"][k].get("residual_ratio"),
                  "run2=", r2[ent]["legs"][k].get("realization"),
                  r2[ent]["legs"][k].get("dup_ratio") or
                  r2[ent]["legs"][k].get("delay_ratio") or
                  r2[ent]["legs"][k].get("residual_ratio"))
    json.dump(checks, open(sys.argv[3], "w"), indent=1, default=str)
    print("wrote", sys.argv[3])


if __name__ == "__main__":
    main()
