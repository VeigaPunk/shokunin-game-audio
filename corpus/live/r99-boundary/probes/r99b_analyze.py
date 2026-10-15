#!/usr/bin/env python3
"""r99-boundary verdict engine: turns raw/<pass>/*.json into receipts/verdicts.json.

Each claim is evaluated independently in the quiet-ish pass and the load pass;
the final verdict distinguishes a *law* falsification from a load deviation.
"""
import glob, json, math, os, sys

SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(SEAT, "raw")
REC = os.path.join(SEAT, "receipts")
PASSES = ("quiet", "load")


def load_pass(p):
    out = {}
    for f in glob.glob(os.path.join(RAW, p, "*.json")):
        base = os.path.basename(f)[:-5]
        cell, _, rep = base.rpartition("-rep")
        try:
            rep = int(rep)
        except ValueError:
            continue
        out.setdefault(cell, {})[rep] = json.load(open(f))
    return out


def reps(p, cell, data=None):
    d = (data or load_pass(p)).get(cell, {})
    return [d[k] for k in sorted(d)]


def ok_reps(p, cell, data=None):
    return [r for r in reps(p, cell, data) if r.get("ok")]


def V(v, **kw):
    d = {"verdict": v}
    d.update(kw)
    return d


def payload_metrics(path):
    """Continuity metrics for a captured payload: hole fraction, tone exactness."""
    if not os.path.exists(path):
        return None
    import array
    b = open(path, "rb").read()
    a = array.array("h")
    a.frombytes(b[: len(b) - (len(b) % 2)])
    if sys.byteorder == "little":
        a.byteswap()
    L = [v / 32768.0 for v in a[0::2]]
    if not L:
        return None
    n = len(L)
    nz = [i for i, v in enumerate(L) if abs(v) > 0.01]
    if not nz:
        return {"frames": n, "nonzero": 0, "nonzero_frac": 0.0, "longest_zero_run": n,
                "tone_exact_frac_of_nonzero": None}
    # longest zero run
    best = cur = 0
    for v in L:
        cur = cur + 1 if abs(v) <= 0.01 else 0
        best = max(best, cur)
    start = nz[0]

    def tone(i, f=997.0, rate=48000):
        return int(0.5 * 32767 * math.sin(2 * math.pi * f * i / rate))
    gen = [tone(i) for i in range(4800 + min(n - start, 4000) + 8)]
    vals = [int(v * 32768.0) for v in L[start:start + 2000]]
    if len(vals) < 64:
        return {"frames": n, "nonzero": len(nz), "nonzero_frac": len(nz) / n,
                "longest_zero_run": best, "tone_exact_frac_of_nonzero": None}
    cand = [o for o in range(4800) if all(vals[i] == gen[o + i] for i in range(24))]
    if not cand:
        return {"frames": n, "nonzero": len(nz), "nonzero_frac": len(nz) / n,
                "longest_zero_run": best, "tone_exact_frac_of_nonzero": 0.0, "candidates": 0}
    o = cand[0]
    hit = sum(1 for i in range(len(vals)) if abs(vals[i]) > 0.01 * 32768 and vals[i] == gen[o + i])
    nz_in = sum(1 for i in range(len(vals)) if abs(vals[i]) > 0.01 * 32768)
    return {"frames": n, "nonzero": len(nz), "nonzero_frac": round(len(nz) / n, 4),
            "longest_zero_run": best, "tone_exact_frac_of_nonzero": round(hit / nz_in, 4) if nz_in else None,
            "candidates": len(cand)}


def aux_dir(p):
    """Aux (payload/wav/tap) dir for a pass; the quiet pass ran before the
    per-pass aux dirs existed and was moved to cells-quiet."""
    for cand in ("cells-%s" % p, "cells"):
        d = os.path.join(RAW, cand)
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*")):
            if cand == "cells" and p == "quiet":
                return d
            if cand == "cells-%s" % p:
                return d
    return os.path.join(RAW, "cells-%s" % p)


def rtp_of(r):
    return r.get("recv") or r.get("tap") or {}


# ------------------------------------------------------------------ claims
def c2_sink_props(p, data):
    exp = {"rtp.ptime": 1.0, "rtp.framecount": 48, "rtp.mime": "L16", "rtp.payload": 127,
           "net.mtu": 1280, "net.header": 28, "rtp.dscp": 34, "rtp.ttl": 1,
           "node.network": True, "media.class": "Audio/Sink", "rtp.rate": 48000,
           "rtp.channels": 2, "rtp.destination.port": 46200, "rtp.destination.ip": "127.0.0.1"}
    rows = []
    for r in ok_reps(p, "sink_p1", data):
        pr = (r.get("sink_props") or {}).get("props", {})
        bad = {k: (pr.get(k), v) for k, v in exp.items() if pr.get(k) != v}
        rows.append({"bad": bad, "n_in": (r.get("sink_props") or {}).get("n_in"),
                     "n_out": (r.get("sink_props") or {}).get("n_out"),
                     "ssrc": pr.get("rtp.ssrc"), "ts_offset": pr.get("rtp.sender-ts-offset")})
    return V("CONFIRMED" if rows and all(not x["bad"] for x in rows) else "FALSIFIED", rows=rows,
             expected=exp)


def c2b_defaults(p, data):
    rows = []
    for r in ok_reps(p, "sink_default", data):
        pr = (r.get("sink_props") or {}).get("props", {})
        rr = rtp_of(r)
        rows.append({"ptime": pr.get("rtp.ptime"), "framecount": pr.get("rtp.framecount"),
                     "sizes": rr.get("sizes"), "n": rr.get("n")})
    # the report's wording "defaults are a 1 ms/48-frame stream"
    word_true = all(x["ptime"] == 1.0 and x["framecount"] == 48 for x in rows)
    return V("CONFIRMED" if word_true else "FALSIFIED",
             measured=rows,
             true_default="6.458333 ms / 310 frames / 1252 B" if rows and not word_true else None,
             note="scout §1.2 says the sink *defaults* are 1 ms/48 frames; the module defaults are 2/20")


def c3_socket(p, data):
    rows = []
    for r in ok_reps(p, "sink_socket", data):
        for s in r.get("udp_sockets_after_play", []) + r.get("udp_sockets_after_load", []):
            rows.append(s)
    good = [s for s in rows if "127.0.0.1:" in s and "0 0 " in s]
    return V("CONFIRMED" if good else "FALSIFIED", rows=rows[:8])


def c3b_two_sinks(p, data):
    rows = []
    for r in ok_reps(p, "sink_two", data):
        rr = rtp_of(r)
        socks = r.get("udp_sockets", [])
        rows.append({"ssrcs": rr.get("distinct_ssrc"), "sizes": rr.get("sizes"), "n": rr.get("n"),
                     "socks": socks, "props_a": (r.get("props_a") or {}).get("state"),
                     "props_b": (r.get("props_b") or {}).get("state")})
    good = all(len(x["ssrcs"] or []) == 2 for x in rows) and rows
    return V("CONFIRMED" if good else "FALSIFIED", rows=rows)


def c4_wire(p, data):
    rows = []
    for r in ok_reps(p, "sink_p1", data):
        rr = rtp_of(r)
        rows.append({"sizes": rr.get("sizes"), "pt": (rr.get("rtp") or {}).get("pt"),
                     "ver": (rr.get("rtp") or {}).get("version"),
                     "seq_deltas": rr.get("seq_deltas"), "ts_deltas": rr.get("ts_deltas"),
                     "pps": round(rr.get("n", 0) / rr.get("seconds", 1), 1) if rr.get("n") else None})
    good = all(x["sizes"] == [204] and x["pt"] == 127 and x["ver"] == 2 and x["seq_deltas"] == [1]
               for x in rows) and rows
    return V("CONFIRMED" if good else "FALSIFIED", rows=rows)


def c4b_tsdeltaset(p, data):
    """The report's §1.4/§2 set {48,80,96,112,128,144} vs the full measured set."""
    report = {48, 80, 96, 112, 128, 144}
    rows = []
    for r in ok_reps(p, "sink_p1", data):
        rr = rtp_of(r)
        d = set(rr.get("ts_deltas") or [])
        d = {x for x in d if x < 2 ** 31}
        rows.append({"measured": sorted(d), "report_subset_ok": report <= d,
                     "extra": sorted(d - report)})
    good = all(x["report_subset_ok"] for x in rows) and rows
    return V("CONFIRMED" if good else "FALSIFIED", rows=rows,
             note="the report's set is a subset of the measured set (160/176 were omitted)")


def c5_content(p, data):
    rows = []
    for r in ok_reps(p, "sink_p1", data):
        rr = rtp_of(r)
        c = rr.get("content") or {}
        g = c.get("goertzel_L") or {}
        g997, g440 = g.get("997"), g.get("440")
        pm = payload_metrics(os.path.join(aux_dir(p), "sink_p1-rep%d.recv.json.payload" % r.get("rep", 0)))
        rows.append({"peak_l": c.get("peak_l"), "peak_r": c.get("peak_r"),
                     "g997": g997, "g440": g440, "ratio": round(g997 / g440, 1) if g440 else None,
                     "exact": (c.get("exact_997") or {}).get("exact"),
                     "payload": pm})
    peaks_ok = all(x["peak_l"] == 0.499969 and x["peak_r"] == 0.499969 for x in rows) and rows
    dom_ok = all((x["ratio"] or 0) > 100 for x in rows) and rows
    return V("CONFIRMED" if (peaks_ok and dom_ok) else ("FALSIFIED" if rows else "INDETERMINATE"),
             peaks_ok=peaks_ok, dominance_ok=dom_ok, rows=rows,
             note="peak equality is the sample-exactness witness; 997 dominance is fill-dependent")


def c6_e2e(p, data):
    rows = []
    for r in ok_reps(p, "e2e_native", data):
        w = r.get("wav") or {}
        g = (w.get("goertzel_L") or {})
        rows.append({"frames": w.get("frames"), "peak": w.get("peak_l"),
                     "g997": g.get("997"), "g440": g.get("440"),
                     "ratio": round(g["997"] / g["440"], 1) if g.get("440") else None,
                     "tap_n": (r.get("tap") or {}).get("n")})
    present = all((x["peak"] or 0) > 0.4 for x in rows) and rows
    dominant = [x for x in rows if (x["ratio"] or 0) > 100]
    return V("CONFIRMED" if present else ("FALSIFIED" if rows else "INDETERMINATE"),
             tone_present_every_rep=present, dominant_reps=len(dominant), reps=len(rows), rows=rows,
             note="peak present in every rep; 997 dominance degrades when the fill fraction drops")


def c7_lan(p, data):
    f = os.path.join(REC, "lan-%s.json" % p)
    strong = os.path.join(REC, "lan-confinement-20s.json")
    if not os.path.exists(f):
        return V("INDETERMINATE", note="lan receipt missing")
    arms = json.load(open(f))
    idles = [a for a in arms if a["arm"] == "idle"]
    lo = next((a for a in arms if a["arm"] == "mcast-lo"), {})
    en = next((a for a in arms if a["arm"] == "mcast-en"), {})
    idle_max = max([a.get("enp7s0_tx_delta") or 0 for a in idles] or [0])
    lo_d, en_d = lo.get("enp7s0_tx_delta"), en.get("enp7s0_tx_delta")
    lo_emit, en_emit = lo.get("emitted_packets") or 0, en.get("emitted_packets") or 0
    # primary witness: the dedicated 20 s windows (receipt written once, same window)
    strong_data = json.load(open(strong)) if os.path.exists(strong) else None
    strong_ok = None
    if strong_data:
        i1, m, i2 = strong_data["idle1"], strong_data["module_lo"], strong_data["idle2"]
        strong_ok = (m["pkts"] <= max(i1["pkts"], i2["pkts"]) and m["bytes"] <= max(i1["bytes"], i2["bytes"])
                     and m["rtp_emitted"] >= 10000)
    control = en_d is not None and en_d >= (lo_d or 0) + max(200, 0.5 * max(en_emit, lo_emit))
    return V("CONFIRMED" if (strong_ok and control) else "FALSIFIED",
             idle=[a.get("enp7s0_tx_delta") for a in idles], idle_max=idle_max,
             mcast_lo={"delta": lo_d, "emitted": lo_emit, "recv_en": (lo.get("recv") or {}).get("n")},
             mcast_en={"delta": en_d, "emitted": en_emit, "recv_en": (en.get("recv") or {}).get("n")},
             strong_20s=strong_data, strong_ok=strong_ok, control=control,
             note="the enp7s0-joined receiver also sees the local loopback copy of a lo-bound send "
                  "(peer = this host's LAN address); egress is judged by the tx counter")


def c8_src_port0(p, data):
    rows = []
    for r in ok_reps(p, "src_port0", data):
        rows.append({"core_up": r.get("core_up"), "invalid": bool(r.get("invalid_source_port_log")),
                     "ctx_fail": bool(r.get("context_fail_log")),
                     "mandatory": bool(r.get("load_module_err"))})
    good = all((not x["core_up"]) and x["invalid"] and x["ctx_fail"] for x in rows) and rows
    return V("CONFIRMED" if good else "FALSIFIED", rows=rows)


def c8b_unicast(p, data):
    rows = []
    for r in ok_reps(p, "src_unicast", data):
        w = r.get("wav") or {}
        g = w.get("goertzel_L") or {}
        rows.append({"arm": r.get("arm"), "peak": w.get("peak_l"), "g997": g.get("997"),
                     "g440": g.get("440"),
                     "ratio": round(g["997"] / g["440"], 1) if g.get("440") else None,
                     "sync": any("sync to timestamp" in l for l in (r.get("witness") or [])),
                     "socks": r.get("udp_sockets")})
    same = [x for x in rows if x["arm"] == "same-port"]
    foreign = [x for x in rows if x["arm"] == "foreign-port"]
    good = (same and all((x["ratio"] or 0) > 100 and x["sync"] for x in same)
            and foreign and all((x["peak"] or 0) == 0.0 and not x["sync"] for x in foreign))
    return V("CONFIRMED" if good else "FALSIFIED", rows=rows)


def c9_lattice(p, data):
    expect = {"mtu1280_p1": (1.0, 48, [204]), "mtu200_p1": (1.0, 48, [204]),
              "mtu8000_p1": (1.0, 48, [204]), "default_pmin2": (6.458333, 310, [1252]),
              "pmin10": (10.0, 480, [1932]), "pmin50": (50.0, 2400, None)}
    rows = []
    for r in ok_reps(p, "lattice", data):
        pr = (r.get("sink_props") or {}).get("props", {})
        rr = rtp_of(r)
        e = expect.get(r.get("case"))
        rows.append({"case": r.get("case"), "ptime": pr.get("rtp.ptime"),
                     "framecount": pr.get("rtp.framecount"), "sizes": rr.get("sizes"),
                     "expect_ptime": e[0] if e else None, "expect_fc": e[1] if e else None,
                     "ok": bool(e) and pr.get("rtp.ptime") == e[0] and pr.get("rtp.framecount") == e[1]
                           and (e[2] is None or rr.get("sizes") == e[2])})
    return V("CONFIRMED" if rows and all(x["ok"] for x in rows) else "FALSIFIED", rows=rows)


def c9b_cap(p, data):
    rows = []
    for r in ok_reps(p, "lattice", data):
        if r.get("case") != "pmin50":
            continue
        rr = rtp_of(r)
        rows.append({"sizes": rr.get("sizes"), "n": rr.get("n"),
                     "frames": (rr.get("content") or {}).get("frames")})
    fals = all(x["sizes"] == [9612] for x in rows) and rows
    return V("FALSIFIED" if fals else ("CONFIRMED" if rows else "INDETERMINATE"), rows=rows,
             corrected="the wire packet is 12 + 2400*4 = 9612 B; the scout's 2048 was its own "
                       "recvfrom(2048) tap buffer")


def c10_refusals(p, data):
    rows = []
    for r in ok_reps(p, "refusal", data):
        rows.append({"case": r.get("case"), "core_up": r.get("core_up"), "msg": r.get("msg"),
                     "node_state": (r.get("node") or {}).get("state"),
                     "socks": len(r.get("udp_sockets") or []),
                     "log": (r.get("log_tail") or [])[-2:]})
    d = {x["case"]: x for x in rows}
    hard = all(d.get(c, {}).get("core_up") is False for c in ("bad_dest_ip", "bad_format_f32le", "bad_media"))
    soft = all(d.get(c, {}).get("core_up") is True for c in ("bad_ifname_nowp", "tiny_mtu_nowp"))
    return V("CONFIRMED" if (rows and hard and soft) else "FALSIFIED", rows=rows,
             hard_refusals_ok=hard, soft_loads_ok=soft)


def c10b_wp_scope(p, data):
    rows = []
    for r in ok_reps(p, "refusal", data):
        if r.get("case") in ("bad_ifname_wp", "tiny_mtu_wp", "s24be"):
            rows.append({"case": r.get("case"), "core_up": r.get("core_up"),
                         "node_state": (r.get("node") or {}).get("state"),
                         "socks": len(r.get("udp_sockets") or []),
                         "log": (r.get("log_tail") or [])[-3:]})
    driven = []
    for r in ok_reps(p, "badifname_driven", data):
        driven.append({"core_up": r.get("core_up"),
                       "state_pre": (r.get("pre") or {}).get("state"),
                       "state_during": (r.get("during") or {}).get("state"),
                       "state_after": (r.get("after") or {}).get("state"),
                       "socks": len(r.get("udp_sockets") or []),
                       "bindtodevice_err": bool(r.get("bindtodevice_err")),
                       "stream_err": bool(r.get("stream_err"))})
    loads = rows and all(x["core_up"] for x in rows)
    deferred = driven and all(x["bindtodevice_err"] and x["stream_err"] for x in driven)
    return V("CONFIRMED" if (loads and deferred) else "INDETERMINATE", rows=rows, driven=driven,
             note="the module loads and the node is created; the SO_BINDTODEVICE failure surfaces "
                  "only when a session manager drives the stream")


def c11_fake(p, data):
    rows = []
    for r in ok_reps(p, "src_fake", data):
        pr = (r.get("src_props") or {}).get("props", {})
        rows.append({"receiving": pr.get("rtp.receiving"), "ts_offset": pr.get("rtp.receiver-ts-offset"),
                     "state": (r.get("src_props") or {}).get("state"),
                     "sync": [l for l in (r.get("sync_log") or []) if "sync to timestamp" in l]})
    ok = all(x["receiving"] is True and x["ts_offset"] for x in rows) and rows
    offs = [x["ts_offset"] for x in rows]
    return V("CONFIRMED" if ok else "FALSIFIED", rows=rows, distinct_ts_offsets=len(set(offs)),
             note="rtp.receiving=true on a source that has never seen a packet; ts offset random per load")


def c12_crafted(p, data):
    """A/B: the scout's unicast shape vs a correct multicast path."""
    rows = {"unicast_scout_shape": [], "mcast_correct_path": []}
    for r in ok_reps(p, "crafted_unicast", data):
        w = r.get("wav") or {}
        rows["unicast_scout_shape"].append({
            "tap_n": (r.get("tap") or {}).get("n"), "peak": w.get("peak_l"),
            "sync": any("sync to timestamp" in l for l in (r.get("witness") or [])),
            "proc_rows": r.get("proc_net_udp_rows")})
    for r in ok_reps(p, "crafted_mcast", data):
        w = r.get("wav") or {}
        g = w.get("goertzel_L") or {}
        rows["mcast_correct_path"].append({
            "tap_n": (r.get("tap") or {}).get("n"), "peak": w.get("peak_l"),
            "g997": g.get("997"), "g440": g.get("440"),
            "sync": any("sync to timestamp" in l for l in (r.get("witness") or [])),
            "proc_rows": r.get("proc_net_udp_rows")})
    u, m = rows["unicast_scout_shape"], rows["mcast_correct_path"]
    fals = (u and all((x["peak"] or 0) == 0.0 and not x["sync"] for x in u)
            and m and all((x["peak"] or 0) > 0.4 and x["sync"] for x in m))
    return V("FALSIFIED" if fals else "INDETERMINATE", rows=rows,
             note="the scout's crafted arms sent unicast to 127.0.0.1 while the source socket was "
                  "bound to the multicast group -> the silence was a delivery artifact, not clock gating")


def c12b_tsoff(p, data):
    rows = []
    for r in ok_reps(p, "crafted_tsoff", data):
        w = r.get("wav") or {}
        g = w.get("goertzel_L") or {}
        rows.append({"delta": r.get("delta"), "ts_offset_arg": r.get("ts_offset_arg"),
                     "peak": w.get("peak_l"), "g997": g.get("997"),
                     "sync": any("sync to timestamp" in l for l in (r.get("witness") or []))})
    good = rows and all((x["peak"] or 0) > 0.4 for x in rows)
    return V("CONFIRMED" if good else "INDETERMINATE", rows=rows,
             note="sess.ts-offset as a module arg; a repaired crafted sender proves the mechanism "
                  "is not needed for a correctly-delivered stream")


def c13_sap(p, data):
    rows = []
    for r in ok_reps(p, "sap", data):
        names = r.get("nodes") or []
        rows.append({"arm": r.get("arm"), "core_up": r.get("core_up"),
                     "nodes": names, "rtp_nodes": [n for n in names if "sap" in str(n).lower() or "rtp" in str(n).lower()],
                     "tx_delta": r.get("enp7s0_tx_delta"),
                     "join_log": [l for l in (r.get("join_log") or []) if "join" in l.lower()][:3]})
    no_node = all(not x["rtp_nodes"] for x in rows) and rows
    joined = all(x["join_log"] for x in rows)
    return V("CONFIRMED" if (no_node and joined) else "INDETERMINATE", rows=rows)


def c14_s24be(p, data):
    rows = []
    for r in ok_reps(p, "refusal", data):
        if r.get("case") != "s24be":
            continue
        rr = r.get("recv") or {}
        rows.append({"core_up": r.get("core_up"), "sizes": rr.get("sizes"),
                     "pt": (rr.get("rtp") or {}).get("pt"), "n": rr.get("n")})
    good = rows and all(x["core_up"] and x["sizes"] == [300] for x in rows)
    return V("CONFIRMED" if good else ("INDETERMINATE" if not rows else "FALSIFIED"), rows=rows,
             expected_wire="12 + 48*6 = 300 B (S24BE, 2ch)")


def ax_graph(p, data):
    rows = []
    for r in ok_reps(p, "pwcli_private", data):
        rows.append({"during": bool(r.get("node_during")), "after": bool(r.get("node_after_cli_exit")),
                     "recv_n": (r.get("recv") or {}).get("n")})
    shared = []
    for r in ok_reps(p, "shared_graph", data):
        shared.append({"pre": r.get("pre_census", {}).get("objects"),
                       "during": r.get("during_census", {}).get("objects"),
                       "post": r.get("post_census", {}).get("objects"),
                       "recv_n": (r.get("recv") or {}).get("n")})
    return V("CONFIRMED" if rows and all(x["during"] and not x["after"] for x in rows) else "INDETERMINATE",
             pwcli_private=rows, shared_graph=shared)


def ax_quantum(p, data):
    rows = []
    for r in ok_reps(p, "axis_quantum", data):
        rr = rtp_of(r)
        rows.append({"quantum": r.get("quantum"), "ts_deltas": rr.get("ts_deltas"),
                     "sizes": rr.get("sizes"), "ptime": (r.get("sink_props") or {}).get("props", {}).get("rtp.ptime")})
    return V("MEASURED", rows=rows,
             note="does the ts-delta lattice track quantum/64?")


def ax_rate(p, data):
    rows = []
    for r in ok_reps(p, "axis_rate", data):
        pr = (r.get("sink_props") or {}).get("props", {})
        rr = rtp_of(r)
        rows.append({"arm": r.get("arm"), "rtp.rate": pr.get("rtp.rate"), "ptime": pr.get("rtp.ptime"),
                     "framecount": pr.get("rtp.framecount"), "sizes": rr.get("sizes"),
                     "ts_deltas": rr.get("ts_deltas")})
    return V("MEASURED", rows=rows)


def ax_order(p, data):
    rows = []
    for r in ok_reps(p, "axis_order", data):
        pr = (r.get("sink_props") or {}).get("props", {})
        rr = rtp_of(r)
        rows.append({"arm": r.get("arm"), "ptime": pr.get("rtp.ptime"), "framecount": pr.get("rtp.framecount"),
                     "sizes": rr.get("sizes"), "n": rr.get("n")})
    return V("MEASURED", rows=rows)


def ax_flagorder(p, data):
    rows = []
    for r in ok_reps(p, "flagorder", data):
        t, o = r.get("target_recv") or {}, r.get("other_recv") or {}
        rows.append({"args_first": r.get("args_first"), "target_n": t.get("n"), "other_n": o.get("n"),
                     "target_peak": (t.get("content") or {}).get("peak_l"),
                     "other_peak": (o.get("content") or {}).get("peak_l")})
    return V("CONFIRMED" if rows and all((x["target_peak"] or 0) > 0.4 and (x["other_peak"] or 0) == 0 for x in rows) else "FALSIFIED", rows=rows)


def relink_series(payload_path, times, frames=48, t_kill=None, t_play2=None):
    """Per-packet tone presence from the tap payload (48 frames/packet)."""
    import array
    if not os.path.exists(payload_path):
        return None
    b = open(payload_path, "rb").read()
    a = array.array("h")
    a.frombytes(b[: len(b) - (len(b) % 2)])
    if sys.byteorder == "little":
        a.byteswap()
    per = frames * 2
    peaks = []
    for i in range(0, len(a) - per + 1, per):
        seg = a[i:i + per]
        peaks.append(max(abs(v) for v in seg) / 32768.0)
    n = min(len(peaks), len(times))
    tone = [peaks[i] > 0.2 for i in range(n)]
    episodes = []
    s = None
    for i, t in enumerate(tone):
        if t and s is None:
            s = i
        if not t and s is not None:
            episodes.append((round(times[s], 3), round(times[i - 1], 3)))
            s = None
    if s is not None:
        episodes.append((round(times[s], 3), round(times[n - 1], 3)))
    ts = [times[i] for i in range(n) if tone[i]]
    out = {"packets": n, "tone_packets": sum(tone), "episodes": episodes[:12],
           "n_episodes": len(episodes), "first_tone": round(ts[0], 3) if ts else None,
           "last_tone": round(ts[-1], 3) if ts else None}
    if t_kill is not None:
        before = [x for x in ts if x < t_kill]
        out["last_tone_before_kill"] = round(before[-1], 3) if before else None
        out["silence_tail_s"] = round(t_kill - before[-1], 3) if before else None
    if t_play2 is not None:
        after = [x for x in ts if x > t_play2]
        out["first_tone_after_restart"] = round(after[0], 3) if after else None
        out["relock_s"] = round(after[0] - t_play2, 3) if after else None
    return out


def ax_relink(p, data):
    rows = []
    for r in ok_reps(p, "relink", data):
        t = r.get("tap") or {}
        times = t.get("pkt_times") or []
        series = relink_series(os.path.join(aux_dir(p), "relink-rep%d.tap.json.payload" % r.get("rep", 0)),
                               times, t_kill=r.get("t_kill"), t_play2=r.get("t_play2"))
        rows.append({"t_play1": r.get("t_play1"), "t_kill": r.get("t_kill"),
                     "t_play2": r.get("t_play2"), "t_kill2": r.get("t_kill2"),
                     "n": t.get("n"), "first_pkt": t.get("first_t"), "last_pkt": t.get("last_t"),
                     "gap_count": len(t.get("gaps_gt_3ms") or []), "tone_series": series})
    return V("MEASURED", rows=rows)


def c15_load_invariance(p, data):
    """Compare quiet and load for the deterministic cells."""
    rows = []
    quiet = load_pass("quiet")
    for cell in ("sink_p1", "lattice", "src_unicast", "crafted_mcast", "crafted_unicast",
                 "e2e_native", "axis_quantum", "axis_rate", "axis_order"):
        q = reps("quiet", cell, quiet)
        l = reps("load", cell, data)
        def sig(rs):
            out = []
            for r in rs:
                rr = rtp_of(r)
                out.append((r.get("case") or r.get("arm") or cell, tuple(rr.get("sizes") or []),
                            (r.get("sink_props") or {}).get("props", {}).get("rtp.ptime"),
                            (r.get("sink_props") or {}).get("props", {}).get("rtp.framecount"),
                            (r.get("wav") or {}).get("peak_l")))
            return sorted(out, key=str)
        rows.append({"cell": cell, "quiet": sig(q), "load": sig(l), "identical": sig(q) == sig(l)})
    return V("CONFIRMED" if rows and all(x["identical"] for x in rows) else "MEASURED", rows=rows)


def _rec(name):
    f = os.path.join(REC, name)
    return json.load(open(f)) if os.path.exists(f) else None


def c10c_refusal_dichotomy(p, data):
    """The scout's claim 10 dichotomy: refusals are module-init -EINVAL or nothing."""
    d = _rec("axis-order-ptime.json")
    if not d:
        return V("INDETERMINATE", note="axis-order-ptime.json missing")
    hard = d.get("stream_props_ptime20_fc960_consistent", {})
    third = (hard.get("core_up") is False and "rc=-8" in str(hard.get("msg")))
    return V("FALSIFIED" if third else "CONFIRMED", sigfpe_case=hard,
             note="a third refusal class exists: a *consistent* rtp.ptime/rtp.framecount pair in "
                  "stream.props leaves psamples=0 and the daemon dies with SIGFPE (rc=-8), not -EINVAL")


def c16_ptime_props(p, data):
    d = _rec("axis-order-ptime.json") or {}
    w = _rec("axis-order-wire.json") or {}
    mod_args = d.get("module_args_ptime20_fc480_inconsistent", {})
    inconsistent = d.get("stream_props_ptime20_fc480_inconsistent", {})
    consistent = d.get("stream_props_ptime20_fc960_consistent", {})
    only = w.get("streamprops_ptime20_only", {})
    wire = w.get("streamprops_ptime20_fc480", {})
    ok = (mod_args.get("ptime") == 1.0 and mod_args.get("framecount") == 48          # module args ignored
          and inconsistent.get("ptime") == 20 and inconsistent.get("framecount") == 480
          and wire.get("sizes") == [3852]                                            # prop 480, wire 960
          and only.get("sizes") == [3852] and only.get("props", {}).get("rtp.framecount") == 960
          and consistent.get("core_up") is False)
    return V("CONFIRMED" if ok else "INDETERMINATE",
             module_args_ignored=mod_args, consistent_pair=consistent,
             inconsistent_pair=inconsistent, wire_inconsistent=wire, wire_only=only,
             note="rtp.ptime/rtp.framecount are read from stream.props, not from the module args")


CLAIMS = [
    ("C1", "34 modules / 10 network-capable / roc-zeroconf-snapcast absent / no man pages", None),
    ("C2", "sink props with explicit 1 ms ptime: 204 B L16 stream, send_*/monitor_* ports", c2_sink_props),
    ("C2b", "the sink *defaults* are a 1 ms / 48-frame L16 stream", c2b_defaults),
    ("C3", "sink socket = connected UDP with an ephemeral source port", c3_socket),
    ("C3b", "two sinks on one destination coexist", c3b_two_sinks),
    ("C4", "wire: 204 B, V=2, PT=127, seq+1, one size", c4_wire),
    ("C4b", "ts-delta set is {48,80,96,112,128,144}", c4b_tsdeltaset),
    ("C5", "tone survives the wire sample-exact (peak 0.499969, 997 dominant)", c5_content),
    ("C6", "native end-to-end sink->mcast(lo)->source->pw-record carries the tone", c6_e2e),
    ("C7", "local.ifname=lo keeps the multicast send off the LAN", c7_lan),
    ("C8", "source.port=0 is a hard init error (rc 234)", c8_src_port0),
    ("C8b", "unicast source = connected socket; only packets from source.port accepted", c8b_unicast),
    ("C9", "packetization table (6 cells)", c9_lattice),
    ("C9b", "50/100 cell is capped at 2048 B on the wire", c9b_cap),
    ("C10", "refusals: 3 init-EINVAL classes kill the core; bad ifname / tiny mtu load fine", c10_refusals),
    ("C10b", "'loads fine' measured without a session manager", c10b_wp_scope),
    ("C11", "rtp.receiving=true is faked at init; ts offset random per load", c11_fake),
    ("C12", "crafted RTP with arbitrary ts -> silence (clock-gating mechanism)", c12_crafted),
    ("C12b", "sess.ts-offset at module-arg level repairs a crafted sender", c12b_tsoff),
    ("C13", "rtp-sap: no node, joins the group, listener + send timer", c13_sap),
    ("C14", "S24BE is supported (no S24LE/S32/F32)", c14_s24be),
    ("C15", "load invariance of the deterministic cells", c15_load_invariance),
    ("C16", "rtp.ptime/rtp.framecount: module args ignored; stream.props consistent pair kills the daemon", c16_ptime_props),
    ("C10c", "refusals are module-init -EINVAL or nothing at all (dichotomy)", c10c_refusal_dichotomy),
    ("AX-GRAPH", "private-core daemon module vs client-side pw-cli vs shared graph", ax_graph),
    ("AX-QUANTUM", "quantum axis: does the ts lattice track quantum/64?", ax_quantum),
    ("AX-RATE", "rate axis: module audio.rate / core clock.rate 44100", ax_rate),
    ("AX-ORDER", "module-arg order, duplicate keys, ptime in stream.props", ax_order),
    ("AX-FLAGORDER", "pw-play --target before vs after the file", ax_flagorder),
    ("AX-RELINK", "player start/kill/restart timing", ax_relink),
]


def main():
    data = load_pass("load")
    verdicts = []
    for cid, claim, fn in CLAIMS:
        if fn is None:
            census = os.path.join(REC, "census.json")
            if os.path.exists(census):
                c = json.load(open(census))
                ok = (c["native_module_count"] == "34" and len(c["network_capable_modules"]) == 10
                      and all("was not found" in p for p in c["packages"][2:])
                      and all("No manual entry" in m for m in c["man_pages"]))
                verdicts.append({"id": cid, "claim": claim, "verdict": "CONFIRMED" if ok else "FALSIFIED",
                                 "detail": {"census": c}})
            else:
                verdicts.append({"id": cid, "claim": claim, "verdict": "INDETERMINATE"})
            continue
        per = {}
        for p in PASSES:
            d = load_pass(p) if p == "quiet" else data
            try:
                per[p] = fn(p, d)
            except Exception as e:
                per[p] = V("INDETERMINATE", error=repr(e))
        q, l = per["quiet"]["verdict"], per["load"]["verdict"]
        if q == l:
            final = q
        elif q == "CONFIRMED" and l == "FALSIFIED":
            final = "CONFIRMED-quiet/FALSIFIED-load"
        elif q == "FALSIFIED" and l == "CONFIRMED":
            final = "FALSIFIED-quiet/CONFIRMED-load"
        else:
            final = "%s / %s" % (q, l)
        verdicts.append({"id": cid, "claim": claim, "verdict": final, "quiet": per["quiet"], "load": per["load"]})
    json.dump(verdicts, open(os.path.join(REC, "verdicts.json"), "w"), indent=1, default=str)

    lines = ["%-12s %-46s %s" % ("id", "verdict", "claim")]
    for v in verdicts:
        lines.append("%-12s %-46s %s" % (v["id"], v["verdict"], v["claim"]))
    open(os.path.join(SEAT, "runs", "analysis-verdicts.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
