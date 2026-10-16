#!/usr/bin/env python3
"""r85 verifier — independent armed-law checker over a fixture receipt.

Re-derives the r85 armed verdict surface from the recorded data with
verifier-owned logic (no fixture import). The point is not to restate
the fixture's own `failures` but to check that the *data* in the receipt
satisfies the law set the landing claims, and that the host-bimodal
realizations land inside their armed sets.

Usage: laws.py receipt.json [label]
Prints: LAW <name> PASS|FAIL <detail>
Exit 0 iff every law passes.
"""
import json
import sys

AMP = 8192.0
SOLO_ENV = (0.85, 1.18)
BLEED_MAX = 0.05
FLUSH_BOUND = 16384
RAIL_ENV = (0.08, 0.60)
SPUR_MIN = 300.0
DUP_MAX = 2.05


def med(ws, key, lo=None, hi=None):
    vals = [w[key] for w in ws if key in w and w.get(key) is not None
            and (lo is None or w.get("at_s", 0) >= lo)
            and (hi is None or w.get("at_s", 0) <= hi)]
    return sum(vals) / len(vals) if vals else None


def links_of(leg):
    return [e for s in (leg.get("samples") or []) for e in s.get("links") or []]


def ports(leg):
    return {e.get("out_port_name") for e in links_of(leg)}


def post_links(leg):
    sams = leg.get("samples") or []
    return [e for s in sams[1:] for e in s.get("links") or []]


def main():
    doc = json.load(open(sys.argv[1]))
    label = sys.argv[2] if len(sys.argv) > 2 else "receipt"
    m = doc["measurements"]
    addr_entry = m["pactlmon_addr_r85_probe"]
    addr = addr_entry["legs"]
    mix = m["pactlmon_mix_r85_probe"]["legs"]
    env = m["pactlmon_aplayenv_r85_probe"]["legs"]
    cap = m["pactlmon_capture_r85_probe"]["legs"]
    neg = m["pactlmon_negctl_r85_probe"]["legs"]
    env_entry = m["pactlmon_aplayenv_r85_probe"]
    cap_entry = m["pactlmon_capture_r85_probe"]
    rows = []

    def law(name, ok, detail=""):
        rows.append((name, bool(ok), detail))

    def rc(rec, code, cls=None):
        if (rec or {}).get("exit_code") != code:
            return False
        return cls is None or (rec or {}).get("error_class") == cls

    # ---------------- addr lattice ----------------
    def vol(rec):
        import re
        mm = re.search(r"(\d+)\s*%", (rec or {}).get("stdout") or "")
        return int(mm.group(1)) if mm else None
    for nm in ("g_name", "g_serial", "g_defsink", "g_leadspace", "g_plus",
               "g_float", "g_xsuf", "g_hex"):
        l = addr[nm]
        law(f"addr.{nm}.rc0_volume", rc(l, 0) and "Volume:" in (l.get("stdout") or ""),
            f"rc={l.get('exit_code')} class={l.get('error_class')}")
    law("addr.g_serial_eq_g_name", vol(addr["g_serial"]) == vol(addr["g_name"]),
        f"{vol(addr['g_serial'])} vs {vol(addr['g_name'])}")
    for nm in ("g_objid", "g_defsrc", "g_defmon", "g_monitor_as_sink",
               "g_bogus", "g_huge", "g_neg", "g_uscr", "g_defsinkX"):
        l = addr[nm]
        law(f"addr.{nm}.noent", rc(l, 1, "pa_get_info_noent"),
            f"rc={l.get('exit_code')} class={l.get('error_class')}")
    l = addr["g_empty"]
    law("addr.g_empty.invalid_arg", rc(l, 1, "pa_invalid_arg"),
        f"rc={l.get('exit_code')} class={l.get('error_class')}")
    l = addr["g_zero"]
    law("addr.g_zero.live_default",
        rc(l, 0) and vol(l) == vol(addr["g_defsink"]),
        f"rc={l.get('exit_code')} pct={vol(l)} vs {vol(addr['g_defsink'])}")
    law("addr.g_lead0.record_only", addr["g_lead0"].get("armed") is False,
        f"armed={addr['g_lead0'].get('armed')}")
    for nm in ("s_monitor_name", "s_sink_serial", "s_defmon", "s_defsrc",
               "s_zero"):
        l = addr[nm]
        law(f"addr.{nm}.rc0_volume", rc(l, 0) and "Volume:" in (l.get("stdout") or ""),
            f"rc={l.get('exit_code')} class={l.get('error_class')}")
    law("addr.s_serial_eq_monitor_name",
        vol(addr["s_sink_serial"]) == vol(addr["s_monitor_name"]),
        f"{vol(addr['s_sink_serial'])} vs {vol(addr['s_monitor_name'])}")
    for nm in ("s_sinkname", "s_defsink", "s_bogus"):
        l = addr[nm]
        law(f"addr.{nm}.noent", rc(l, 1, "pa_get_info_noent"),
            f"rc={l.get('exit_code')} class={l.get('error_class')}")
    l = addr["pwcli_id"]
    law("addr.pwcli_id.resolves",
        rc(l, 0) and str(addr_entry.get("ns_props", {}).get("node_id")) in
        (l.get("stdout") or ""), f"rc={l.get('exit_code')}")
    l = addr["pwcli_serial"]
    blob = (l.get("stderr") or "") + (l.get("stdout") or "")
    law("addr.pwcli_serial.rc0_lie",
        rc(l, 0) and "unknown global" in blob, f"rc={l.get('exit_code')}")
    mv = addr.get("mv_name") or {}
    ns_idx = (addr_entry.get("sink_index") or {}).get("ns")
    ns2_idx = (addr_entry.get("sink_index") or {}).get("ns2")
    a1 = mv.get("after") or {}
    law("addr.mv_name.moves", rc(mv.get("pactl"), 0) and a1.get("sink") == ns2_idx,
        f"rc={(mv.get('pactl') or {}).get('exit_code')} sink={a1.get('sink')} want={ns2_idx}")
    mv = addr.get("mv_serial") or {}
    a2 = mv.get("after") or {}
    law("addr.mv_serial.moves", rc(mv.get("pactl"), 0) and a2.get("sink") == ns_idx,
        f"rc={(mv.get('pactl') or {}).get('exit_code')} sink={a2.get('sink')} want={ns_idx}")
    mv = addr.get("mv_bogus") or {}
    a3 = mv.get("after") or {}
    law("addr.mv_bogus.refuse_stay",
        (mv.get("pactl") or {}).get("exit_code") not in (0, None)
        and a3.get("sink") == a2.get("sink"),
        f"rc={(mv.get('pactl') or {}).get('exit_code')} sink={a3.get('sink')}")
    mv = addr.get("cdup_move") or {}
    a4 = mv.get("after") or {}
    law("addr.cdup_move.serial_holder",
        rc(mv.get("pactl"), 0) and a4.get("sink") == ns_idx,
        f"rc={(mv.get('pactl') or {}).get('exit_code')} sink={a4.get('sink')} want={ns_idx}")
    ns_name = (addr["g_name"].get("argv") or "").split()[-1]
    ns2_name = ((addr.get("mv_name") or {}).get("pactl") or {}).get("argv", "").split()[-1]
    cl = addr.get("cdup_cap") or {}
    cl_links = links_of(cl)
    mon = [e for e in cl_links if (e.get("out_port_name") or "").startswith("monitor_")]
    real = cl.get("realization")
    law("addr.cdup_cap.armed_realization",
        real in ("serial_monitor_bypass", "name_shadow_bound", "stalled",
                 "refused"),
        f"realization={real} mon_links={len(mon)}")
    law("addr.cdup_cap.monitor_only_serial_holder",
        (not mon) or all(e.get("out_node") == ns_name for e in mon),
        f"mon out_nodes={sorted({e.get('out_node') for e in mon})} holder={ns_name}")
    sc = addr_entry.get("serial_cycles") or {}
    sers = sc.get("serials") or []
    law("addr.serial_monotonic",
        len(sers) == 3 and all(isinstance(s, int) for s in sers)
        and sers == sorted(sers) and len(set(sers)) == 3,
        f"serials={sers}")

    # ---------------- mix ----------------
    def tap_ok(nm):
        l = mix[nm]
        edges = l.get("tap_link") or []
        return bool(edges) and all(
            (e.get("out_port_name") or "").startswith("monitor_") for e in edges)
    for nm in ("solo", "mix2", "mixdup", "mixdelay", "mixinv", "mixclip"):
        law(f"mix.{nm}.tap_link_validated", tap_ok(nm),
            f"tap_links={len(mix[nm].get('tap_link') or [])}")
    sa = (mix["solo"].get("amps") or {}).get("windows") or []
    la, rb = med(sa, "l_a"), med(sa, "r_b")
    ra, lb = med(sa, "r_a") or 0, med(sa, "l_b") or 0
    law("mix.solo.ref_in_window",
        la is not None and rb is not None
        and SOLO_ENV[0] * AMP <= la <= SOLO_ENV[1] * AMP
        and SOLO_ENV[0] * AMP <= rb <= SOLO_ENV[1] * AMP,
        f"l_a={la} r_b={rb}")
    law("mix.solo.zero_bleed", ra <= BLEED_MAX * AMP and lb <= BLEED_MAX * AMP,
        f"r_a={ra} l_b={lb}")
    ref = min(la, rb) if (la and rb) else None
    mw = (mix["mix2"].get("amps") or {}).get("windows") or []
    ok_amp, det = True, []
    for k in ("l_a", "r_b", "l_c", "r_d"):
        v = med(mw, k)
        det.append(f"{k}={v}")
        if ref and (v is None or not (SOLO_ENV[0] * ref <= v <= SOLO_ENV[1] * ref)):
            ok_amp = False
    law("mix.mix2.full_amplitude", ok_amp, " ".join(det))
    ok_bl, det = True, []
    for k in ("r_a", "l_b", "r_c", "l_d"):
        v = med(mw, k) or 0
        det.append(f"{k}={v}")
        if ref and v > BLEED_MAX * ref:
            ok_bl = False
    law("mix.mix2.zero_bleed", ok_bl, " ".join(det))
    edges = mix["mix2"].get("mix_edges") or []
    ports_seen = {e.get("in") for e in edges}
    law("mix.mix2.topology_4_to_2",
        len(edges) == 4 and len(ports_seen) == 2
        and all(":playback_" in (p or "") for p in ports_seen),
        f"edges={len(edges)} ports={sorted(ports_seen)}")
    dw = (mix["mixdup"].get("amps") or {}).get("windows") or []
    drat = (med(dw, "l_a") / ref) if (ref and med(dw, "l_a") is not None) else None
    law("mix.mixdup.linear_bound", drat is not None and drat <= DUP_MAX,
        f"ratio={drat} realization={mix['mixdup'].get('realization')}")
    dw = [w for w in ((mix["mixdelay"].get("amps") or {}).get("windows") or [])
          if w.get("at_s", 0) >= 1.2]
    drat = (med(dw, "l_a") / ref) if (ref and med(dw, "l_a") is not None) else None
    law("mix.mixdelay.linear_bound", drat is not None and drat <= DUP_MAX,
        f"ratio={drat} realization={mix['mixdelay'].get('realization')}")
    iw = (mix["mixinv"].get("amps") or {}).get("windows") or []
    irat = (med(iw, "l_a") / ref) if (ref and med(iw, "l_a") is not None) else None
    law("mix.mixinv.linear_bound", irat is not None and irat <= DUP_MAX,
        f"ratio={irat} realization={mix['mixinv'].get('realization')}")
    cw = (mix["mixclip"].get("amps") or {}).get("windows") or []
    pk, rail = med(cw, "peak"), med(cw, "rail_frac")
    spur = max([med(cw, k) or 0 for k in ("l_h1", "r_h1", "l_h3", "r_h3",
                                          "l_i1", "r_i1")])
    law("mix.mixclip.rail", pk is not None and pk >= 32767,
        f"peak={pk}")
    law("mix.mixclip.rail_frac_envelope",
        rail is not None and RAIL_ENV[0] <= rail <= RAIL_ENV[1],
        f"rail_frac={rail}")
    law("mix.mixclip.spur_floor", spur >= SPUR_MIN, f"spur={spur}")

    # ---------------- aplay env ----------------
    def_sink = env_entry["inventory"]["default_sink"]
    ns = ns_name
    ser = env_entry.get("ns_serial")

    def to_sink(nm, want_obj, want_consumer):
        l = env[nm]
        hits = [c for c in (l.get("nodes_mid") or [])
                if str((c.get("props") or {}).get("target.object")) == str(want_obj)]
        ok = bool(hits) and any(
            want_consumer in (c.get("consumers") or []) for c in hits)
        law(f"env.{nm}.lands", ok,
            f"cands={len(hits)} consumers={[c.get('consumers') for c in hits]}")
    to_sink("env_node", ns, ns)
    to_sink("env_props", ns, ns)
    to_sink("env_conflict", ns, ns)
    law("env.env_conflict.props_win",
        not any(ns2_name in (c.get("consumers") or [])
                for c in (env["env_conflict"].get("nodes_mid") or [])),
        f"ns2={ns2_name}")
    to_sink("env_serial", ser, ns)
    bogus_hits = [c for c in (env["env_bogus"].get("nodes_mid") or [])
                  if str((c.get("props") or {}).get("target.object")) == "no_such_r85a"]
    law("env.env_bogus.publish_then_default",
        bool(bogus_hits) and any(def_sink in (c.get("consumers") or [])
                                 for c in bogus_hits), "")
    law("env.env_none.default_fallback",
        any(def_sink in (c.get("consumers") or [])
            for c in (env["env_none"].get("nodes_mid") or [])), "")

    # ---------------- capture ----------------
    bp = ports(cap["cap_baseline"])
    law("cap.baseline.bind_capture",
        bp and all((p or "").startswith("capture_") for p in bp),
        f"ports={sorted(bp)}")
    law("cap.baseline.content", (cap["cap_baseline"].get("nz") or {}).get("peak", 0) >= 1000,
        f"peak={(cap['cap_baseline'].get('nz') or {}).get('peak')}")
    for nm in ("t_srcname", "t_srcserial", "t_srcid"):
        lp = ports(cap[nm])
        law(f"cap.{nm}.binds_source",
            lp and all((p or "").startswith("capture_") for p in lp),
            f"ports={sorted(lp)}")
    l = cap["t_sinkserial"]
    sp = ports(l)
    law("cap.t_sinkserial.monitor_bypass",
        sp and all((p or "").startswith("monitor_") for p in sp)
        and all(e.get("out_node") == ns2_name for e in links_of(l)),
        f"ports={sorted(sp)} out_nodes={sorted({e.get('out_node') for e in links_of(l)})}")
    ts = cap["t_sinkname"]
    tsp = ports(ts)
    law("cap.t_sinkname.never_monitor",
        ts.get("realization") in ("bound_source", "stalled", "refused")
        and not any((p or "").startswith("monitor_") for p in tsp),
        f"realization={ts.get('realization')} ports={sorted(tsp)}")
    lp = ports(cap["t_prop_sinkname"])
    law("cap.t_prop_sinkname.monitor",
        lp and all((p or "").startswith("monitor_") for p in lp),
        f"ports={sorted(lp)}")
    pl = links_of(cap["t_prop_srcname"])
    law("cap.t_prop_srcname.default_monitor",
        pl and all((e.get("out_port_name") or "").startswith("monitor_") for e in pl)
        and any(e.get("out_node") == def_sink for e in pl),
        f"links={len(pl)}")
    for rep in (0, 1):
        l = cap[f"cap_loss_{rep}"]
        sams = l.get("samples") or []
        post = l.get("post") or {}
        law(f"cap.cap_loss_{rep}.linked_pre_loss",
            bool(sams) and bool(sams[0].get("links")), "")
        law(f"cap.cap_loss_{rep}.no_relink", not post_links(l),
            f"post_links={len(post_links(l))}")
        law(f"cap.cap_loss_{rep}.alive", l.get("alive_at_end") is True, "")
        law(f"cap.cap_loss_{rep}.unload_rc0",
            (l.get("unloaded") or {}).get("exit_code") == 0, "")
        law(f"cap.cap_loss_{rep}.flush_bounded",
            (post.get("post_frames") or 0) <= FLUSH_BOUND,
            f"post_frames={post.get('post_frames')} realization={post.get('realization')}")
        law(f"cap.cap_loss_{rep}.growth_ceased",
            len(sams) >= 2 and sams[-1].get("size") == sams[-2].get("size"),
            f"sizes={[s.get('size') for s in sams]}")
    l = cap["cap_loss_prop"]
    pst = post_links(l)
    law("cap.cap_loss_prop.default_monitor_relink",
        any(e.get("out_node") == def_sink
            and (e.get("out_port_name") or "").startswith("monitor_")
            for e in pst), f"post_links={len(pst)}")
    law("cap.cap_loss_prop.unload_rc0",
        (l.get("unloaded") or {}).get("exit_code") == 0, "")
    l = cap["sd_idle"]
    law("cap.sd_idle.survives",
        l.get("module_dead_at_s") is None and l.get("source_dead_at_s") is None,
        f"mod={l.get('module_dead_at_s')} src={l.get('source_dead_at_s')}")
    for nm in ("sd_record", "sd_parec"):
        l = cap.get(nm) or {}
        if not l:
            continue
        law(f"cap.{nm}.bind_kill",
            l.get("module_dead_at_s") is not None
            and l.get("module_dead_at_s") <= 1.5,
            f"mod_dead={l.get('module_dead_at_s')}")
        law(f"cap.{nm}.no_link_content",
            (l.get("out") or {}).get("data_actual", 0) <= 200
            and not l.get("links"), "")
    l = cap["sd_prop"]
    plinks = links_of(l)
    law("cap.sd_prop.armed_realization",
        l.get("realization") in ("clean_default_fallback",
                                 "bind_killed_then_default"),
        f"realization={l.get('realization')}")
    law("cap.sd_prop.links_monitor_default",
        (not plinks) or (all((e.get("out_port_name") or "").startswith("monitor_")
                             for e in plinks)
                         and any(e.get("out_node") == def_sink for e in plinks)),
        f"links={len(plinks)}")
    l = cap["sd_pwlink"]
    if not l.get("skipped"):
        law("cap.sd_pwlink.no_client_kill",
            l.get("module_alive") is True and l.get("source_alive") is True, "")
    l = cap["latebind"]
    lk = links_of(l)
    law("cap.latebind.armed_realization",
        l.get("realization") in ("late_bound", "stalled", "refused"),
        f"realization={l.get('realization')}")
    law("cap.latebind.shape",
        (not lk) or all(
            (e.get("out_port_name") or "").startswith("capture_")
            and "late_" in (e.get("out_node") or "")
            for e in lk), f"links={len(lk)}")

    # ---------------- negctl ----------------
    cases = [(k, v) for k, v in neg.items() if k.startswith("u_")]
    bad = [(k, v.get("got"), v.get("expect")) for k, v in cases
           if v.get("got") != v.get("expect")]
    law("neg.unit_table", not bad and len(cases) == 13,
        f"n={len(cases)} bad={bad}")
    for nm in ("ctl_pactl_info", "ctl_pwdump"):
        l = neg[nm]
        law(f"neg.{nm}.clean",
            l.get("exit_code") == 0 and not l.get("error_class")
            and not l.get("signal") and not l.get("killed_at_bound"), "")
    l = neg["ctl_pwcli_ser"]
    blob = (l.get("stderr") or "") + (l.get("stdout") or "")
    law("neg.ctl_pwcli_ser.rc0_lie",
        l.get("exit_code") == 0 and "unknown global" in blob, "")
    l = neg["ctl_sigkill"]
    law("neg.ctl_sigkill.discriminator",
        l.get("signal") == "SIGKILL" and l.get("error_class") is None, "")

    fails = [r for r in rows if not r[1]]
    print(f"# {label}: {len(rows)} laws, {len(fails)} FAIL")
    for n, ok, d in rows:
        if not ok:
            print(f"LAW {n} FAIL {d}")
    if not fails:
        for n, ok, d in rows:
            print(f"LAW {n} PASS {d}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
