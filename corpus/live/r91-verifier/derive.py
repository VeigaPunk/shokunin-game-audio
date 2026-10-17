#!/usr/bin/env python3
"""r91 VERIFIER — independent leg re-derivation for the --probe-gstfrz-r91
family. Reads one measurements.json and re-derives every armed cell of the
15 legs (5 entries) from raw leg data with this seat's own logic; prints a
table and returns nonzero when any derived cell is red.

Usage: derive.py <measurements.json> [<measurements.json> ...]
"""
import json
import sys

RIFF = 0x7FFF0024
DATA = 0x7FFF0000
NS = "r91a_ns_"
NS2 = "r91a_ns2_"
SRC = "r91a_src_"
CLOCK_LINE = "Clock lost, selecting a new one"
PLAYING_LINE = "Setting pipeline to PLAYING"

results = []  # (leg, check, ok, detail)


def chk(leg, name, ok, detail=""):
    results.append((leg, name, bool(ok), detail))
    return bool(ok)


def nodes(leg, after=None, margin=0.2):
    out = []
    for s in leg.get("samples") or []:
        if after is not None and s.get("t", 0) < after + margin:
            continue
        out += s.get("nodes") or []
    return out


def post_samples(leg, after, margin=0.2):
    return [s for s in leg.get("samples") or []
            if after is not None and s.get("t", 0) >= after + margin]


def sizes(samples):
    return [s.get("size") for s in samples if s.get("size") is not None]


def last_node(leg, after=None):
    for s in reversed(leg.get("samples") or []):
        if after is not None and s.get("t", 0) < after:
            continue
        if s.get("nodes"):
            return s["nodes"][0]
    return None


def fired(leg, kind, kinds=None):
    for f in leg.get("fired") or []:
        if kinds and f.get("kind") not in kinds:
            continue
        if kinds is None and f.get("kind") != kind:
            continue
        return f.get("at"), (f.get("result") or {})
    return None, {}


def unload_leaf_ok(leaf):
    """Every fired unload: verified index equals captured (or captured
    None), not recycled, rc 0, and it actually fired (not skipped)."""
    if not leaf:
        return False, "no leaf"
    if leaf.get("skipped"):
        return False, f"skipped={leaf.get('skipped')}"
    ok = (leaf.get("exit_code") == 0
          and leaf.get("recycled") is False
          and leaf.get("verified_index") is not None
          and (leaf.get("captured") is None
               or leaf["captured"] == leaf["verified_index"]))
    return ok, (f"idx={leaf.get('verified_index')} "
                f"cap={leaf.get('captured')} rc={leaf.get('exit_code')} "
                f"recycled={leaf.get('recycled')}")


def entry(rec, name):
    return (rec.get("measurements") or {}).get(name) or {}


def main(path):
    rec = json.load(open(path))
    M = rec.get("measurements") or {}
    print(f"# {path}\n# mode={rec.get('mode')}")
    for name, e in sorted(M.items()):
        print(f"# entry {name}: failures={e.get('failures')} "
              f"coverage_blocked={e.get('coverage_blocked')} "
              f"blocked={e.get('blocked')}")
    P = entry(rec, "gstfrz_prop_r91_probe")
    C = entry(rec, "gstfrz_clock_r91_probe")
    R = entry(rec, "gstfrz_resume_r91_probe")
    S = entry(rec, "gstfrz_srcloss_r91_probe")
    X = entry(rec, "gstfrz_connect_r91_probe")

    # ---------------- entry 1: prop lattice (4 legs) ----------------
    legs = P.get("legs") or {}
    chk("p_cap", "leg present + no spawn error",
        "p_cap" in legs and not legs.get("p_cap", {}).get("spawn_error"),
        str(legs.get("p_cap", {}).get("spawn_error")))
    nd = last_node(legs.get("p_cap") or {})
    pr = (nd or {}).get("props") or {}
    chk("p_cap", "node.dont-reconnect is JSON true",
        pr.get("node.dont-reconnect") is True,
        repr(pr.get("node.dont-reconnect")))
    chk("p_cap", "stream.capture.sink lands literal 'TRUE'",
        pr.get("stream.capture.sink") == "TRUE",
        repr(pr.get("stream.capture.sink")))
    chk("p_cap", "target.object names the seat sink",
        str(pr.get("target.object", "")).startswith(NS),
        repr(pr.get("target.object")))
    nd = last_node(legs.get("p_cap_false") or {})
    v = ((nd or {}).get("props") or {}).get("node.dont-reconnect")
    chk("p_cap_false", "override lands as literal 'FALSE'", v == "FALSE",
        repr(v))
    nd = last_node(legs.get("p_rec") or {})
    chk("p_rec", "node observed", nd is not None)
    chk("p_rec", "pw-record carries NO node.dont-reconnect",
        nd is not None and
        "node.dont-reconnect" not in ((nd or {}).get("props") or {}),
        repr(((nd or {}).get("props") or {}).get("node.dont-reconnect")))
    leg = legs.get("p_sink") or {}
    unl_at, ul = fired(leg, None, kinds=("unload_sink", "unload_source"))
    chk("p_sink", "target unload fired", unl_at is not None,
        f"at={unl_at}")
    nd = last_node(leg, after=unl_at)
    chk("p_sink", "pipewiresink carries NO node.dont-reconnect",
        nd is not None and
        "node.dont-reconnect" not in ((nd or {}).get("props") or {}))
    pre = [n.get("state") for s in (leg.get("samples") or [])
           if unl_at is not None and s.get("t", 0) < unl_at
           for n in (s.get("nodes") or [])]
    chk("p_sink", "stream running before the loss (all pre samples)",
        bool(pre) and all(s == "running" for s in pre), str(pre[:4]))
    post = post_samples(leg, unl_at)
    st = [n.get("state") for n in nodes(leg, after=unl_at)]
    cls = None
    if leg.get("killed") == "wallcap" and st and all(s == "running"
                                                     for s in st):
        cls = "survived_running"
    elif leg.get("killed") is None and \
            leg.get("exit_code") not in (0, -9, None) and \
            all(s != "running" for s in st):
        cls = "exited"
    chk("p_sink", "post-loss class in {survived_running, exited}",
        cls is not None,
        f"derived={cls} rc={leg.get('exit_code')} "
        f"killed={leg.get('killed')} states={st[-3:]}")
    rec_cls = (P.get("cells") or {}).get("p_sink_post_class")
    chk("p_sink", "recorded class == derived class", cls == rec_cls,
        f"derived={cls} recorded={rec_cls}")
    chk("p_sink", "recorded cells: dont-reconnect true / FALSE / absent",
        (P.get("cells") or {}).get("p_cap_dont_reconnect") is True and
        (P.get("cells") or {}).get("p_cap_false_value") == "FALSE" and
        (P.get("cells") or {}).get("p_rec_prop_present") is False and
        (P.get("cells") or {}).get("p_sink_prop_present") is False,
        json.dumps(P.get("cells") or {}, default=str)[:200])

    # ---------------- entry 2: clock lattice (4 legs) ----------------
    legs = C.get("legs") or {}
    for tag in ("c_quiet", "c_verbose", "c_keepalive"):
        leg = legs.get(tag) or {}
        unl_at, ul = fired(leg, None, kinds=("unload_sink",))
        chk(tag, "target unload fired", unl_at is not None, f"at={unl_at}")
        leaf = (C.get("unloads") or {}).get("r91a_ns_%s" % tag) or {}
        if not leaf:
            # unloads dict is keyed by the sink name, shared across legs
            leaves = list((C.get("unloads") or {}).values())
            leaf = next((l for l in leaves
                         if l.get("value") and l.get("value") ==
                         leg.get("target")), {})
        chk(tag, "frozen: alive at the wall cap",
            leg.get("killed") == "wallcap",
            f"killed={leg.get('killed')} rc={leg.get('exit_code')}")
        post = post_samples(leg, unl_at)
        sz = sizes(post)
        chk(tag, "artifact carries real bytes after the loss",
            bool(sz) and max(sz) > 44, f"sizes={sz[:3]}..{sz[-3:]}")
        chk(tag, "post-loss shape is FLAT",
            len(sz) >= 3 and max(sz) == min(sz),
            f"min={min(sz) if sz else None} max={max(sz) if sz else None} "
            f"n={len(sz)}")
        fed = sorted({f for n in nodes(leg, after=unl_at)
                      for f in (n.get("fed_by") or [])})
        chk(tag, "no re-created link into the frozen capture",
            fed == [], str(fed))
        st = [n.get("state") for n in nodes(leg, after=unl_at)]
        chk(tag, "stream state leaves running",
            bool(st) and st[-1] != "running", f"states={st[-3:]}")
        out = leg.get("out") or {}
        chk(tag, "pinned wavenc streaming header",
            out.get("riff_size") == RIFF and out.get("data_declared") == DATA,
            f"riff={out.get('riff_size')} data={out.get('data_declared')} "
            f"bytes={out.get('bytes')}")
        chk(tag, "recorded frozen cell matches raw leg",
            (C.get("frozen") or {}).get(tag, {}).get("sizes_tail") == sz[-3:]
            and (C.get("frozen") or {}).get(tag, {}).get("fed_by") == fed,
            json.dumps((C.get("frozen") or {}).get(tag) or {})[:200])
    leg = legs.get("c_quiet") or {}
    chk("c_quiet", "stdout empty (-q)", not (leg.get("stdout") or "").strip(),
        repr((leg.get("stdout") or "")[:80]))
    chk("c_quiet", "stderr empty", not (leg.get("stderr") or "").strip(),
        repr((leg.get("stderr") or "")[:120]))
    leg = legs.get("c_verbose") or {}
    so = leg.get("stdout") or ""
    chk("c_verbose", "launcher CLOCK_LOST line on stdout",
        CLOCK_LINE in so, repr(so[:200]))
    chk("c_verbose", "launcher PLAYING line on stdout",
        PLAYING_LINE in so, repr(so[:200]))
    chk("c_verbose", "stderr empty (prose claim, not family-armed)",
        not (leg.get("stderr") or "").strip(),
        repr((leg.get("stderr") or "")[:120]))
    chk("c_verbose", "argv has no -q", "-q" not in (leg.get("argv") or ""),
        (leg.get("argv") or "")[:120])
    leg = legs.get("c_keepalive") or {}
    lc = leg.get("line_counts") or {}
    chk("c_keepalive", "0 keepalive-resend lines", lc.get(
        "timeout, send keepalive buffer") == 0, json.dumps(lc))
    chk("c_keepalive", "0 popped-buffer lines", lc.get("popped buffer") == 0,
        json.dumps(lc))
    chk("c_keepalive", "debug stderr non-empty (the log exists)",
        (leg.get("stderr_bytes") or 0) > 0,
        f"stderr_bytes={leg.get('stderr_bytes')}")
    chk("c_keepalive", "keepalive-time=20 armed in argv",
        "keepalive-time=20" in (leg.get("argv") or ""),
        (leg.get("argv") or "")[-160:])
    leg = legs.get("c_alive") or {}
    sz = sizes(leg.get("samples") or [])
    chk("c_alive", "target-alive control GROWS >= 65536",
        len(sz) >= 3 and sz[-1] - sz[0] >= 65536,
        f"sizes={sz[:2]}..{sz[-2:]}")
    nd = last_node(leg)
    chk("c_alive", "control stream state is running",
        (nd or {}).get("state") == "running", str((nd or {}).get("state")))
    chk("c_alive", "control was NOT killed by the loss (no unload fired)",
        not (leg.get("fired") or []))

    # ---------------- entry 3: resume control (1 leg + fixture) ------
    legs = R.get("legs") or {}
    leg = legs.get("r_app") or {}
    st = leg.get("app_status") or {}
    chk("r_app", "fixture wrote a status file", bool(st) and
        not st.get("reader_error"), str(st.get("reader_error")))
    chk("r_app", "fixture SAW CLOCK_LOST", st.get("clock_lost") is True,
        f"clock_lost={st.get('clock_lost')} t={st.get('clock_lost_t')}")
    chk("r_app", "fixture never forced the state (forced is null)",
        st.get("forced") is None, repr(st.get("forced")))
    chk("r_app", "fixture bus errors empty", not st.get("errors"),
        str(st.get("errors"))[:160])
    chk("r_app", "fixture bounded itself at its own wall",
        st.get("exit") == "wall" and st.get("rc") == 0,
        f"exit={st.get('exit')} rc={st.get('rc')} "
        f"elapsed={st.get('elapsed_s')}")
    chk("r_app", "battery never had to kill the fixture",
        leg.get("killed") is None, f"killed={leg.get('killed')}")
    sc = [c.get("new") for c in (st.get("state_changes") or [])]
    chk("r_app", "state changes are only null->ready->paused->playing",
        sc == ["ready", "paused", "playing"], str(sc))
    unl_at, _ = fired(leg, None, kinds=("unload_sink",))
    rel_at, rel = fired(leg, "relink")
    chk("r_app", "target unload fired before the relink",
        unl_at is not None and rel_at is not None and unl_at < rel_at,
        f"unload={unl_at} relink={rel_at}")
    chk("r_app", "manual link fires AFTER the clock-lost",
        st.get("clock_lost_t") is None or rel_at is None or
        st["clock_lost_t"] <= rel_at,
        f"cl={st.get('clock_lost_t')} relink={rel_at}")
    links = (rel or {}).get("links") or []
    chk("r_app", "manual relink found a port pair", len(links) >= 1,
        f"n={len(links)}")
    chk("r_app", "every manual pw-link rc 0",
        bool(links) and all((l.get("res") or {}).get("exit_code") == 0
                            for l in links),
        str([(l.get("res") or {}).get("exit_code") for l in links]))
    chk("r_app", "relink pairs are discovered monitor_*->input_*",
        bool(links) and all(
            ":monitor_" in l.get("out", "") and ":input_" in l.get("in", "")
            for l in links),
        str([(l.get("out"), l.get("in")) for l in links]))
    smp = [s for s in (leg.get("samples") or [])
           if s.get("size") is not None]
    pre = [s["size"] for s in smp
           if unl_at is not None and rel_at is not None
           and unl_at + 0.35 <= s["t"] <= rel_at - 0.05]
    after = [s["size"] for s in smp
             if rel_at is not None and s["t"] >= rel_at + 0.2]
    at_rel = next((s["size"] for s in smp
                   if rel_at is not None and s["t"] >= rel_at), None)
    chk("r_app", "artifact FLAT while no link exists (<=8192 span)",
        len(pre) < 2 or max(pre) - min(pre) <= 8192,
        f"pre={pre[:2]}..{pre[-2:]} span="
        f"{max(pre) - min(pre) if pre else None} "
        f"{'ARMED' if len(pre) >= 2 else 'UNARMED (<2 pre samples)'}")
    chk("r_app", "artifact GROWS >= 65536 after the manual link",
        at_rel is not None and bool(after) and after[-1] - at_rel >= 65536,
        f"at_relink={at_rel} post={after[-3:]}")
    fed = sorted({f for s in (leg.get("samples") or [])
                  if rel_at is not None and s["t"] >= rel_at + 0.2
                  for n in (s.get("nodes") or [])
                  for f in (n.get("fed_by") or [])})
    chk("r_app", "post-link producer is the seat remap-source",
        bool(fed) and all(f.startswith(SRC.split("_")[0] + "_") or
                          "r91a_src_" in f for f in fed), str(fed))
    chk("r_app", "recorded resume_bytes match raw samples",
        (R.get("resume_bytes") or {}).get("at_relink") == at_rel and
        (R.get("resume_bytes") or {}).get("post", [])[-3:] == after[-3:],
        json.dumps(R.get("resume_bytes") or {})[:200])
    # the fixture's OWN witness must agree with the battery's file sampling
    chk("r_app", "fixture witness agrees: last-first >= 65536",
        (st.get("last_bytes") or 0) - (st.get("first_bytes") or 0)
        >= 65536,
        f"first={st.get('first_bytes')} last={st.get('last_bytes')}")
    desc = st.get("desc") or ""
    chk("r_app", "fixture pipeline == the canonical capture shape",
        all(tok in desc for tok in
            ("pipewiresrc client-name=", "target-object=" + NS,
             "stream-properties=props,stream.capture.sink=true",
             "num-buffers=1000000", "audio/x-raw,format=S16LE,rate=48000,"
             "channels=2", "wavenc ! filesink")),
        desc[:200])
    chk("r_app", "fixture never re-enters PLAYING after CLOCK_LOST",
        [c.get("new") for c in (st.get("state_changes") or [])]
        .count("playing") == 1,
        str([c.get("new") for c in (st.get("state_changes") or [])]))
    chk("r_app", "fixture CLOCK_LOST is in its own bus trace",
        any("clock-lost" in json.dumps(b).lower() or
            "clock_lost" in json.dumps(b).lower()
            for b in (st.get("bus_types") or [])),
        json.dumps([b.get("type") for b in (st.get("bus_types") or [])])
        [:300])

    # ---------------- entry 4: source-loss envelope (2 legs) ---------
    legs = S.get("legs") or {}
    for tag in ("s_norelink", "s_relink"):
        leg = legs.get(tag)
        if leg is None:
            chk(tag, "leg present (else named coverage_blocked)", False,
                "leg absent — see coverage_blocked")
            continue
        unl_at, _ = fired(leg, None, kinds=("unload_source",))
        chk(tag, "source unload fired", unl_at is not None, f"at={unl_at}")
        chk(tag, "alive at the wall cap", leg.get("killed") == "wallcap",
            f"killed={leg.get('killed')} rc={leg.get('exit_code')}")
        post = post_samples(leg, unl_at)
        sz = sizes(post)
        stt = [n.get("state") for n in nodes(leg, after=unl_at)]
        tail = (sz[-1] - sz[-4]) if len(sz) >= 4 else (
            sz[-1] - sz[0] if len(sz) >= 2 else None)
        last = stt[-1] if stt else None
        cls = None
        if last == "running" and (tail or 0) >= 32768:
            cls = "grows_running"
        elif last in ("idle", "paused", "suspended") and (tail or 0) <= 8192:
            cls = "freeze_idle"
        chk(tag, "post-loss shape in {grows_running, freeze_idle}",
            cls is not None,
            f"derived={cls} last={last} tail={tail} "
            f"sizes={sz[:2]}..{sz[-2:]}")
        rec_cls = ((S.get("shapes") or {}).get(tag) or {}).get("class")
        chk(tag, "recorded shape class == derived", cls == rec_cls,
            f"derived={cls} recorded={rec_cls}")
    leg = legs.get("s_relink") or {}
    rel_at, rel = fired(leg, "relink")
    links = (rel or {}).get("links") or []
    chk("s_relink", "manual pw-link rc 0",
        bool(links) and all((l.get("res") or {}).get("exit_code") == 0
                            for l in links),
        str([(l.get("res") or {}).get("exit_code") for l in links]))
    smp = [s for s in (leg.get("samples") or [])
           if s.get("size") is not None]
    at_rel = next((s["size"] for s in smp
                   if rel_at is not None and s["t"] >= rel_at), None)
    after = [s["size"] for s in smp
             if rel_at is not None and s["t"] >= rel_at + 0.2]
    chk("s_relink", "flow continues across the link (>=65536)",
        at_rel is not None and bool(after) and after[-1] - at_rel >= 65536,
        f"at_relink={at_rel} after={after[-3:]}")
    ast = [n.get("state") for s in (leg.get("samples") or [])
           if rel_at is not None and s["t"] >= rel_at + 0.2
           for n in (s.get("nodes") or [])]
    chk("s_relink", "stream running after the link",
        bool(ast) and ast[-1] == "running", f"states={ast[-3:]}")

    # ---------------- entry 5: connect law (4 legs) ------------------
    legs = X.get("legs") or {}
    l = legs.get("x_rec_sink") or {}
    chk("x_rec_sink", "rc 1", l.get("exit_code") == 1,
        str(l.get("exit_code")))
    chk("x_rec_sink", "artifact stops at the 44 B header",
        (l.get("out") or {}).get("bytes") == 44,
        str((l.get("out") or {}).get("bytes")))
    chk("x_rec_sink", "named refusal class gstfrz_no_target_node",
        l.get("error_class") == "gstfrz_no_target_node",
        f"{l.get('error_class')} {l.get('error_hit')}")
    l = legs.get("x_gst_sink") or {}
    chk("x_gst_sink", "rc 255", l.get("exit_code") == 255,
        str(l.get("exit_code")))
    chk("x_gst_sink", "named refusal class gstfrz_target_not_found",
        l.get("error_class") == "gstfrz_target_not_found",
        f"{l.get('error_class')} {l.get('error_hit')}")
    l = legs.get("x_rec_sink_remapfed") or {}
    rc = l.get("exit_code")
    rcls = ("refused" if rc == 1 else
            "linked_live" if l.get("killed") == "wallcap" else
            f"other:{rc}")
    chk("x_rec_sink_remapfed", "bounded outcome in {refused, linked_live}",
        rcls in ("refused", "linked_live"),
        f"derived={rcls} rc={rc} killed={l.get('killed')}")
    chk("x_rec_sink_remapfed", "recorded class == derived",
        rcls == (X.get("remapfed") or {}).get("class"),
        f"derived={rcls} recorded={(X.get('remapfed') or {}).get('class')}")
    l = legs.get("x_rec_src") or {}
    fed = sorted({f for s in (l.get("samples") or [])
                  for n in (s.get("nodes") or [])
                  for f in (n.get("fed_by") or [])})
    sz = sizes(l.get("samples") or [])
    chk("x_rec_src", "direction control links (producer seen)", bool(fed),
        str(fed))
    chk("x_rec_src", "direction control stays alive to the wall cap",
        l.get("killed") == "wallcap", f"killed={l.get('killed')}")
    chk("x_rec_src", "direction control records >= 65536 B",
        len(sz) >= 2 and sz[-1] >= 65536, f"sizes={sz[:2]}..{sz[-2:]}")
    chk("x_rec_sink", "target verified present (bare) before the refusal",
        (X.get("targets_present_bare") or {}).get("sink") is True,
        json.dumps(X.get("targets_present_bare")))
    chk("x_rec_src", "target verified present before the control",
        (X.get("targets_present") or {}).get("source") is True,
        json.dumps(X.get("targets_present")))

    # ---------------- cross-entry: teardown + census -----------------
    for tag, e in (("prop", P), ("clock", C), ("resume", R),
                   ("srcloss", S), ("connect", X)):
        chk(f"{tag}:entry", "no failures", e.get("failures") == [],
            str(e.get("failures")))
        chk(f"{tag}:entry", "coverage_blocked empty",
            not e.get("coverage_blocked"),
            str(e.get("coverage_blocked")))
        sg = e.get("sinks_gone")
        chk(f"{tag}:entry", "sinks_gone all true (or reader_error named)",
            sg == "reader_error" or (isinstance(sg, dict) and
                                     sg and all(sg.values())),
            str(sg))
        oa = e.get("own_nodes_after")
        chk(f"{tag}:entry", "own_nodes_after empty (or reader_error named)",
            oa == "reader_error" or oa == [], str(oa))
        chk(f"{tag}:entry", "foreign r91a census recorded",
            "foreign_r91a_nodes" in e,
            str(e.get("foreign_r91a_nodes")))
        ul = e.get("unloads") or {}
        bad = {k: v for k, v in ul.items()
               if v and (v.get("exit_code") not in (0, None)
                         or v.get("recycled") is True)}
        chk(f"{tag}:entry", "no failed/recycled teardown unload",
            not bad, json.dumps(bad, default=str)[:200])
        # gated (in-leg) unloads must be name-verified and rc 0
        gfired = [(l.get("name"), f) for l in (e.get("legs") or {}).values()
                  for f in (l.get("fired") or [])
                  if f.get("kind") in ("unload_sink", "unload_source")]
        gbad = [(nm, (f.get("result") or {}))
                for nm, f in gfired
                if (f.get("result") or {}).get("exit_code") != 0
                or (f.get("result") or {}).get("verified_index") !=
                (f.get("result") or {}).get("captured")
                or (f.get("result") or {}).get("recycled") is True]
        chk(f"{tag}:entry", "every GATED unload name-verified, rc 0",
            not gbad, json.dumps(gbad, default=str)[:200])

    npass = sum(1 for _, _, ok, _ in results if ok)
    nfail = len(results) - npass
    for leg, name, ok, detail in results:
        if not ok:
            print(f"FAIL {leg:22s} {name} :: {detail}")
    print(f"\n== derived: {npass} PASS / {nfail} FAIL "
          f"({len(results)} checks) ==")
    return 1 if nfail else 0


if __name__ == "__main__":
    rc = 0
    for p in sys.argv[1:]:
        rc |= main(p)
    sys.exit(rc)
