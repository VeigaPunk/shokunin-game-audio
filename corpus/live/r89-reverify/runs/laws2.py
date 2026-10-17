#!/usr/bin/env python3
"""r89 RE-VERIFY law set — re-derivation on the COMMITTED bytes (5755be5b).

Base: the r89 verifier's 106-law set (`corpus/live/r89-verifier/runs/laws.py`),
with the two laws whose ARMED SEMANTICS the foldfix changed re-encoded to the
committed fixture's own verdict arms:

  * X03 x_foot — was the GLOBAL census law (`pwprof_during == before+1 and
    nodes_delta == 0`, the pre-fix lottery). Committed arm (measure_audio.py
    :31002-31015): OWN-scoped — Client objects carrying
    `application.process.id == foot.pid` must be exactly 1 and objects owned by
    that client must be 0; unreadable census / foot rc != 0 / own client not
    enumerated -> `coverage_blocked` (named, never green).
  * X06 x_top — was the single-frame law (`own_row.wait_us` vs profiler
    medians). Committed arm (:31038-31060): the pw-top MEDIAN over the
    real-cycle rows (`top_wait_med`/`top_busy_med`) vs the profiler medians,
    band 0.25-4.0 unchanged; no real-cycle row -> `coverage_blocked`.

Re-verifier additions (R-series, reported separately from the 106):
  R01 leg census armed == 27/12/4/9 (52)      [prior F4 class]
  R02 x_top real-row provenance (quant>0, cells>0, status!="C") when armed
  R03 g_hup bounded at the sig point (rc -1, wall<=1.5, bytes>0)
  R04 x_foot globals recorded-but-unarmed (demotion evidence)
  R05 no unknown leg keys beyond the declared census

Usage: laws2.py RECEIPT [RECEIPT ...]   (exit 1 on any FAIL)
"""
import json
import sys

ENTRIES = ("pwprof_gate_r89_probe", "pwprof_oart_r89_probe",
           "pwprof_schema_r89_probe", "pwprof_xw_r89_probe")
WANT_CENSUS = {"pwprof_gate_r89_probe": 27, "pwprof_oart_r89_probe": 12,
               "pwprof_schema_r89_probe": 4, "pwprof_xw_r89_probe": 9}

results = []  # (receipt, law, verdict, detail)


def law(rid, name, verdict, detail=""):
    results.append((rid, name, verdict, detail))


def parse_class(leg):
    """(class, n_info) — 'bounded' iff the leg exited before the bound."""
    alive = leg.get("alive_at_sig")
    if alive is True:
        return "unbounded", leg.get("n_info")
    if alive is None and leg.get("exit_code") == 0:
        return "bounded", leg.get("n_info")
    return "other", leg.get("n_info")


def derive(rid, path):
    d = json.load(open(path))
    m = d.get("measurements") or {}
    missing = [e for e in ENTRIES if e not in m]
    if missing:
        law(rid, "C01 four entries present", "FAIL", f"missing {missing}")
        return
    law(rid, "C01 four entries present", "PASS", "27/12/4/9 legs")
    counts = {e: len((m[e].get("legs") or {})) for e in ENTRIES}
    census_ok = counts == WANT_CENSUS
    law(rid, "C01b leg census", "PASS" if census_ok else "FAIL",
        str(counts) + f" total={sum(counts.values())}")

    # ---------------- custody ----------------
    for e in ENTRIES:
        ent = m[e]
        fails = ent.get("failures")
        law(rid, f"C02 {e} failures", "PASS" if fails == [] else "FAIL",
            str(fails)[:160])
        cb = ent.get("coverage_blocked") or []
        law(rid, f"C03 {e} coverage_blocked",
            "PASS" if not cb else "BLOCKED", str(cb)[:160])
        un = ent.get("unloads") or {}
        law(rid, f"C04 {e} unloads rc0",
            "PASS" if un and all((v or {}).get("exit_code") == 0
                                 for v in un.values()) else "FAIL",
            str({k: (v or {}).get("exit_code") for k, v in un.items()}))
        sg = ent.get("sinks_gone")
        law(rid, f"C05 {e} sinks_gone",
            "PASS" if isinstance(sg, dict) and sg and
            all(sg.values()) else "FAIL", str(sg))
        on = ent.get("own_nodes_after")
        law(rid, f"C06 {e} own_nodes_after",
            "PASS" if on == [] else "FAIL", str(on))
        tools = ent.get("tools") or {}
        law(rid, f"C07 {e} tools",
            "PASS" if tools and all(tools.values()) else "FAIL",
            str(tools))

    # ---------------- gate ----------------
    g = m["pwprof_gate_r89_probe"]["legs"]
    l = g.get("g_own", {})
    law(rid, "G01 g_own exact-N rc0/term/8",
        "PASS" if l.get("exit_code") == 0 and l.get("term_ok") is True and
        l.get("n_info") == 8 else "FAIL",
        f"rc={l.get('exit_code')} term={l.get('term_ok')} "
        f"n_info={l.get('n_info')} wall={l.get('wall_s')} "
        f"drivers={l.get('drivers')}")
    l = g.get("g_two", {})
    hist = l.get("driver_info_hist") or []
    hsum = sum(c for _, c in hist)
    law(rid, "G02 g_two summed-N rc0/4/wall<=1.5",
        "PASS" if l.get("exit_code") == 0 and l.get("n_info") == 4 and
        l.get("term_ok") is True and (l.get("wall_s") or 99) <= 1.5
        else "FAIL",
        f"rc={l.get('exit_code')} n_info={l.get('n_info')} "
        f"wall={l.get('wall_s')} hist={hist}")
    law(rid, "G02b g_two hist sums to N",
        "PASS" if hsum == l.get("n_info") else "FAIL", f"sum={hsum}")
    for nm, sig in (("g_term", 0), ("g_int", 0)):
        l = g.get(nm, {})
        law(rid, f"G03 {nm} graceful rc0+term",
            "PASS" if l.get("exit_code") == sig and
            l.get("term_ok") is True else "FAIL",
            f"rc={l.get('exit_code')} term={l.get('term_ok')} "
            f"n_info={l.get('n_info')} bytes={l.get('stdout_bytes')}")
        law(rid, f"G03b {nm} flush has >=5 infos",
            "PASS" if (l.get("n_info") or 0) >= 5 else "FAIL",
            f"n_info={l.get('n_info')}")
    for nm, sig in (("g_kill", -9), ("g_hup", -1), ("g_usr1", -10)):
        l = g.get(nm, {})
        law(rid, f"G04 {nm} truncating rc{sig}+invalid",
            "PASS" if l.get("exit_code") == sig and
            l.get("parse_error") is not None else "FAIL",
            f"rc={l.get('exit_code')} parse={str(l.get('parse_error'))[:48]} "
            f"bytes={l.get('stdout_bytes')}")
    l = g.get("g_blocks", {})
    sm = l.get("stream_samples") or []
    nz = [s for s in sm if s.get("bytes")]
    law(rid, "G05 g_blocks exact-4096 multiples",
        "PASS" if nz and all(s["bytes"] % 4096 == 0 for s in nz)
        else "FAIL", str(sm))
    mono = all(sm[i + 1]["bytes"] >= sm[i]["bytes"]
               for i in range(len(sm) - 1))
    law(rid, "G05b g_blocks monotone",
        "PASS" if mono else "FAIL", f"mono={mono}")
    l = g.get("g_o_ignored", {})
    law(rid, "G06 g_o_ignored -o ignored under -J",
        "PASS" if l.get("file_created") is False and
        "Logging to" not in (l.get("stderr") or "") else "FAIL",
        f"created={l.get('file_created')} rc={l.get('exit_code')} "
        f"n_info={l.get('n_info')}")
    l = g.get("g_extra", {})
    law(rid, "G07 g_extra positional ignored rc0/4",
        "PASS" if l.get("exit_code") == 0 and l.get("n_info") == 4
        else "FAIL", f"rc={l.get('exit_code')} n_info={l.get('n_info')}")
    l = g.get("g_remote_empty", {})
    law(rid, "G08 g_remote_empty -r '' default rc0/4",
        "PASS" if l.get("exit_code") == 0 and l.get("n_info") == 4
        else "FAIL", f"rc={l.get('exit_code')} n_info={l.get('n_info')}")
    for nm in ("g_remote_bogus", "g_env_bogus"):
        l = g.get(nm, {})
        law(rid, f"G09 {nm} rc255 connect_down",
            "PASS" if l.get("exit_code") == 255 and
            l.get("error_class") == "pwprof_connect_down" else "FAIL",
            f"rc={l.get('exit_code')} class={l.get('error_class')} "
            f"hit={str(l.get('error_hit'))[:48]}")
    l = g.get("g_opt_bogus", {})
    law(rid, "G10 g_opt_bogus rc255 opt class",
        "PASS" if l.get("exit_code") == 255 and
        l.get("error_class") == "pwprof_opt" else "FAIL",
        f"rc={l.get('exit_code')} class={l.get('error_class')} "
        f"hit={str(l.get('error_hit'))[:48]}")
    l = g.get("g_version", {})
    law(rid, "G11 g_version rc0 libpipewire",
        "PASS" if l.get("exit_code") == 0 and
        "libpipewire" in (l.get("stdout") or "") else "FAIL",
        f"rc={l.get('exit_code')} stdout={str(l.get('stdout'))[:60]}")
    l = g.get("g_lastwins", {})
    law(rid, "G12 g_lastwins -n4 -n0 unbounded",
        "PASS" if l.get("alive_at_sig") is True and
        l.get("exit_code") == 0 and (l.get("n_info") or 0) >= 5 else "FAIL",
        f"alive={l.get('alive_at_sig')} rc={l.get('exit_code')} "
        f"n_info={l.get('n_info')}")
    # the strtol lattice
    for nm, want in (("n_007", 7), ("n_plus3", 3), ("n_space3", 3)):
        l = g.get(nm, {})
        cls, n_info = parse_class(l)
        law(rid, f"G13 {nm} strtol->{want} bounded",
            "PASS" if l.get("exit_code") == 0 and n_info == want and
            cls == "bounded" else "FAIL",
            f"class={cls} rc={l.get('exit_code')} n_info={n_info} "
            f"wall={l.get('wall_s')}")
    for nm in ("n_2_5", "n_3abc", "n_1e1", "n_huge", "n_neg",
               "n_abc", "n_zero"):
        l = g.get(nm, {})
        cls, n_info = parse_class(l)
        law(rid, f"G14 {nm} unbounded",
            "PASS" if cls == "unbounded" and l.get("exit_code") == 0 and
            (n_info or 0) >= 5 else "FAIL",
            f"class={cls} rc={l.get('exit_code')} n_info={n_info} "
            f"alive={l.get('alive_at_sig')}")
    parser = [nm for nm in g if nm.startswith("n_")]
    classes = {nm: parse_class(g[nm])[0] for nm in parser}
    law(rid, "G15 parser partition (no 'other')",
        "PASS" if len(parser) == 10 and
        all(c in ("bounded", "unbounded") for c in classes.values())
        else "FAIL", str(classes))

    # ---------------- oart ----------------
    o = m["pwprof_oart_r89_probe"]["legs"]
    aux_want = {f"Timing{i}.plot" for i in range(1, 6)} | \
        {"Timings.html", "generate_timings.sh"}
    l = o.get("o_live", {})
    law(rid, "O01 o_live rc0 10 rows",
        "PASS" if l.get("exit_code") == 0 and l.get("rows") == 10
        else "FAIL", f"rc={l.get('exit_code')} rows={l.get('rows')} "
        f"wall={l.get('wall_s')}")
    aux = set(l.get("aux_present") or ())
    law(rid, "O02 o_live aux set superset",
        "PASS" if aux_want.issubset(aux) else "FAIL", str(sorted(aux)))
    law(rid, "O03 o_live Logging-to stderr",
        "PASS" if "Logging to" in (l.get("stderr") or "") else "FAIL",
        str(l.get("stderr"))[:80])
    law(rid, "O04 o_live generate_timings mentioned",
        "PASS" if "generate_timings" in
        (l.get("stdout") or "") + (l.get("stderr") or "") else "FAIL", "")
    l = o.get("o_int", {})
    law(rid, "O05 o_int graceful rc0 bytes>0",
        "PASS" if l.get("exit_code") == 0 and (l.get("bytes") or 0) > 0
        else "FAIL", f"rc={l.get('exit_code')} bytes={l.get('bytes')}")
    l = o.get("o_kill", {})
    law(rid, "O06 o_kill SIGKILL leaves content",
        "PASS" if l.get("exit_code") == -9 and (l.get("bytes") or 0) > 0
        and (l.get("rows") or 0) > 0 else "FAIL",
        f"rc={l.get('exit_code')} bytes={l.get('bytes')} "
        f"rows={l.get('rows')} wall={l.get('wall_s')}")
    law(rid, "O06b o_kill size %4096==0 (incremental blocks)",
        "PASS" if (l.get("bytes") or 0) > 0 and
        (l.get("bytes") or 1) % 4096 == 0 else "FAIL",
        f"bytes={l.get('bytes')}")
    l = o.get("o_exist", {})
    law(rid, "O07 o_exist truncating open",
        "PASS" if l.get("marker_gone") is True else "FAIL",
        f"marker_gone={l.get('marker_gone')}")
    l = o.get("o_eager", {})
    law(rid, "O08 o_eager created inside run",
        "PASS" if l.get("watch_seen") is not None else "FAIL",
        str(l.get("watch_seen")))
    l = o.get("o_default", {})
    law(rid, "O09 o_default profiler.log>0",
        "PASS" if l.get("exit_code") == 0 and
        (l.get("profiler_log") or 0) > 0 else "FAIL",
        f"rc={l.get('exit_code')} profiler.log={l.get('profiler_log')}")
    l = o.get("o_dash", {})
    law(rid, "O10 o_dash literal filename",
        "PASS" if l.get("exit_code") == 0 and
        (l.get("dash_file") or 0) > 0 else "FAIL",
        f"rc={l.get('exit_code')} dash={l.get('dash_file')}")
    l = o.get("o_devnull", {})
    aux2 = set(l.get("aux_present") or ())
    law(rid, "O11 o_devnull aux in cwd",
        "PASS" if l.get("exit_code") == 0 and aux_want.issubset(aux2)
        else "FAIL", f"rc={l.get('exit_code')} aux={sorted(aux2)}")
    for nm in ("o_dir", "o_empty", "o_proc"):
        l = o.get(nm, {})
        law(rid, f"O12 {nm} rc255 cant_open",
            "PASS" if l.get("exit_code") == 255 and
            l.get("error_class") == "pwprof_cant_open" else "FAIL",
            f"rc={l.get('exit_code')} class={l.get('error_class')} "
            f"hit={str(l.get('error_hit'))[:48]}")

    # ---------------- schema ----------------
    s = m["pwprof_schema_r89_probe"]["legs"]
    l = s.get("s_window", {})
    st = l.get("stats") or {}
    law(rid, "S01 s_window rc0 clean parse",
        "PASS" if l.get("exit_code") == 0 and
        l.get("parse_error") is None else "FAIL",
        f"rc={l.get('exit_code')} parse={str(l.get('parse_error'))[:48]}")
    law(rid, "S02 s_window own_blocks>=3",
        "PASS" if (st.get("own_blocks") or 0) >= 3 else "FAIL",
        f"own_blocks={st.get('own_blocks')}")
    law(rid, "S02b s_window own-driver fraction recorded", "PASS",
        f"own_blocks={st.get('own_blocks')} "
        f"drivers={st.get('driver_names')}")
    for k, want, name in (
            ("seq_order_ok", True, "block order info->clock->driver"),
            ("count_step_ok", True, "info.count +1/cycle"),
            ("quantum_relation_ok", True, "next_nsec-nsec==duration/rate"),
            ("pos_step_ok", True, "position+=duration"),
            ("order_ok", True, "prev<=signal<=awake<=finish"),
            ("prev_is_last_signal", True, "prev[k+1]==signal[k]"),
            ("nsec_in_window", True, "nsec inside monotonic window")):
        law(rid, f"S03 {name}", "PASS" if st.get(k) is True else "FAIL",
            str(st.get(k)))
    law(rid, "S04 transports==['stopped']",
        "PASS" if (st.get("transports") or []) == ["stopped"] else "FAIL",
        str(st.get("transports")))
    law(rid, "S05 diffs==[1.0]",
        "PASS" if (st.get("diffs") or []) == [1.0] else "FAIL",
        str(st.get("diffs")))
    law(rid, "S06 driver_statuses==['finished']",
        "PASS" if (st.get("driver_statuses") or []) == ["finished"]
        else "FAIL", str(st.get("driver_statuses")))
    law(rid, "S07 driver_latencies==['0/0']",
        "PASS" if (st.get("driver_latencies") or []) == ["0/0"]
        else "FAIL", str(st.get("driver_latencies")))
    refs = (m["pwprof_schema_r89_probe"].get("refs") or {})
    own_id = refs.get("own_node_id")
    law(rid, "S08 ids == own node",
        "PASS" if own_id is not None and
        set(st.get("clock_ids") or ()) == {own_id} and
        set(st.get("driver_ids") or ()) == {own_id} else "FAIL",
        f"own={own_id} clock={st.get('clock_ids')} "
        f"driver={st.get('driver_ids')}")
    law(rid, "S09 clock_names==['clock.system.monotonic']",
        "PASS" if (st.get("clock_names") or []) ==
        ["clock.system.monotonic"] else "FAIL", str(st.get("clock_names")))
    law(rid, "S10 xruns==[0] and xrun_counts==[0]",
        "PASS" if (st.get("xruns") or [1]) == [0] and
        (st.get("xrun_counts") or [1]) == [0] else "FAIL",
        f"xruns={st.get('xruns')} xrun_counts={st.get('xrun_counts')}")
    law(rid, "S11 fclock_rows==0",
        "PASS" if st.get("fclock_rows") == 0 else "FAIL",
        str(st.get("fclock_rows")))
    law(rid, "S12 nsb_blocks==0 (follower-less sink)",
        "PASS" if st.get("nsb_blocks") == 0 else "FAIL",
        str(st.get("nsb_blocks")))
    counts1 = st.get("own_counts") or []
    law(rid, "S13 own counts contiguous +1 (window-local)",
        "PASS" if counts1 and all(
            counts1[i + 1] == counts1[i] + 1
            for i in range(len(counts1) - 1)) else "FAIL",
        f"first={counts1[:2]} last={counts1[-2:]} n={len(counts1)}")
    l2 = s.get("s_second", {})
    c1 = counts1[-1] if counts1 else None
    c2 = (l2.get("own_counts") or [None])[0]
    law(rid, "S14 s_second count persists (c2>c1)",
        "PASS" if c1 is not None and c2 is not None and c2 > c1 else "FAIL",
        f"c1={c1} c2={c2} gap={None if (c1 is None or c2 is None) else c2 - c1}")
    l3 = s.get("s_suspend", {})
    law(rid, "S15 s_suspend kill hook fired",
        "PASS" if l3.get("kill_mono") is not None else "FAIL",
        f"kill_mono={l3.get('kill_mono')}")
    law(rid, "S16 s_suspend own_pre_kill>0",
        "PASS" if (l3.get("own_pre_kill") or 0) > 0 else "FAIL",
        f"pre={l3.get('own_pre_kill')} blocks={l3.get('own_blocks')}")
    law(rid, "S17 s_suspend own_after_kill==0",
        "PASS" if l3.get("own_after_kill") == 0 else "FAIL",
        f"after={l3.get('own_after_kill')} "
        f"foreign_after={l3.get('foreign_after_kill')}")
    law(rid, "S18 s_suspend graceful TERM rc0",
        "PASS" if l3.get("exit_code") == 0 and
        (l3.get("wall_s") or 0) >= 2.3 else "FAIL",
        f"rc={l3.get('exit_code')} wall={l3.get('wall_s')}")

    # ---------------- xw ----------------
    x = m["pwprof_xw_r89_probe"]["legs"]
    l = x.get("x_modreg", {})
    law(rid, "X01 x_modreg pactl-vs-native mismatch",
        "PASS" if l.get("own_in_dump_modules") is False and
        l.get("own_node_in_dump") is True and
        str(l.get("own_pactl_idx")) in (l.get("pactl_added") or ())
        else "FAIL", json.dumps(l))
    l = x.get("x_blank", {})
    law(rid, "X02 x_blank guarded parse survives",
        "PASS" if l.get("blank_lines") and
        l.get("own_found") is not None else "FAIL", json.dumps(l))
    # ---- X03: COMMITTED own-scoped x_foot arm (:31002-31015) ----
    l = x.get("x_foot", {})
    oc = l.get("own_clients")
    if oc is None:
        law(rid, "X03 x_foot own-scoped 1-Client footprint", "BLOCKED",
            "census unreadable — named coverage class " + json.dumps(l))
    elif l.get("rc") not in (0, None):
        law(rid, "X03 x_foot own-scoped 1-Client footprint", "BLOCKED",
            f"foot rc={l.get('rc')} — named coverage class")
    elif len(oc) == 0:
        law(rid, "X03 x_foot own-scoped 1-Client footprint", "BLOCKED",
            "own client not enumerated in the 0.35s bracket — named "
            "coverage class " + json.dumps(
                {k: l.get(k) for k in
                 ("own_pid", "pwprof_before", "pwprof_during",
                  "nodes_delta")}))
    else:
        ok = len(oc) == 1 and not l.get("own_objects")
        law(rid, "X03 x_foot own-scoped 1-Client footprint",
            "PASS" if ok else "FAIL", json.dumps(l))
    l = x.get("x_conc", {})
    if l.get("rc1") != 0 or l.get("rc2") != 0 or l.get("parse1") or \
            l.get("parse2"):
        law(rid, "X04 x_conc clean captures", "FAIL", json.dumps(l))
    else:
        law(rid, "X04 x_conc clean captures", "PASS",
            f"rc={l.get('rc1')},{l.get('rc2')} bytes="
            f"{l.get('bytes1')},{l.get('bytes2')} "
            f"byte_identical={l.get('byte_identical')}")
    if not l.get("shared"):
        law(rid, "X05 x_conc broadcast dict-identity", "BLOCKED",
            "zero overlapping blocks")
    else:
        law(rid, "X05 x_conc broadcast dict-identity",
            "PASS" if l.get("shared_identical") is True else "FAIL",
            f"shared={l.get('shared')}")
    # ---- X06: COMMITTED median-armed x_top band (:31038-31060) ----
    l = x.get("x_top", {})
    tw, tb = l.get("top_wait_med"), l.get("top_busy_med")
    pw, pb = l.get("prof_wait_us_med"), l.get("prof_busy_us_med")
    if l.get("own_row") is None:
        law(rid, "X06 x_top median WAIT/BUSY cross-witness", "BLOCKED",
            f"no real-cycle own row (transient skipped: "
            f"{l.get('transient_own_rows')}) — named coverage class")
    elif tw is None or tb is None or pw is None or pb is None:
        law(rid, "X06 x_top median WAIT/BUSY cross-witness", "BLOCKED",
            f"partial witnesses {json.dumps(l)}")
    else:
        def _close(a, b):
            return b and 0.25 <= a / b <= 4.0
        ok = _close(tw, pw) and _close(tb, pb)
        law(rid, "X06 x_top median WAIT/BUSY cross-witness",
            "PASS" if ok else "FAIL",
            f"top-med {tw}/{tb}us over {len(l.get('real_own_rows') or ())} "
            f"real rows vs prof {pw}/{pb}us")
    l = x.get("x_profobj", {})
    if not l.get("ids"):
        law(rid, "X07 x_profobj introspection refusal", "BLOCKED",
            "no Profiler object")
    else:
        bad = []
        for sub in ("info", "enum"):
            r = l.get(sub) or {}
            if r.get("exit_code") != 0 or \
                    "unsupported type PipeWire:Interface:Profiler" not in \
                    (r.get("stderr") or "") + (r.get("stdout") or ""):
                bad.append(sub)
        law(rid, "X07 x_profobj introspection refusal",
            "PASS" if not bad else "FAIL", f"ids={l.get('ids')} bad={bad}")
    l = x.get("x_sigpipe", {})
    law(rid, "X08 x_sigpipe closed reader rc-13",
        "PASS" if l.get("rc") == -13 else "FAIL", json.dumps(l))
    l = x.get("x_devfull", {})
    law(rid, "X09 x_devfull silent write error",
        "PASS" if l.get("rc") == 0 and l.get("stderr_bytes") == 0
        else "FAIL", json.dumps(l))

    # ---------------- re-verifier additions (R-series) ----------------
    law(rid, "R01 leg census == 27/12/4/9 (52)",
        "PASS" if census_ok else "FAIL", str(counts))
    l = x.get("x_top", {})
    if l.get("own_row") is None:
        law(rid, "R02 x_top real-row provenance", "BLOCKED",
            "unarmed (no real row) — coverage class")
    else:
        row = l["own_row"]
        real = (row.get("status") != "C" and (row.get("quant") or 0) > 0
                and (row.get("wait_us") or 0) > 0
                and (row.get("busy_us") or 0) > 0)
        law(rid, "R02 x_top real-row provenance",
            "PASS" if real and l.get("real_own_rows") else "FAIL",
            f"row={json.dumps(row)} real_rows="
            f"{len(l.get('real_own_rows') or ())} "
            f"transient={l.get('transient_own_rows')}")
    l = g.get("g_hup", {})
    law(rid, "R03 g_hup bounded at sig point",
        "PASS" if l.get("exit_code") == -1 and
        (l.get("wall_s") or 99) <= 1.5 and
        (l.get("stdout_bytes") or 0) > 0 else "FAIL",
        f"rc={l.get('exit_code')} wall={l.get('wall_s')} "
        f"bytes={l.get('stdout_bytes')} alive={l.get('alive_at_sig')}")
    l = x.get("x_foot", {})
    law(rid, "R04 x_foot globals recorded-but-unarmed",
        "PASS" if all(k in l for k in
                      ("pwprof_before", "pwprof_during", "clients_added",
                       "nodes_delta")) else "FAIL",
        json.dumps({k: l.get(k) for k in
                    ("pwprof_before", "pwprof_during", "clients_added",
                     "nodes_delta", "own_clients")}))
    known = {"x_modreg", "x_blank", "x_link", "x_foot", "x_conc", "x_top",
             "x_profobj", "x_sigpipe", "x_devfull"}
    extra = sorted(set(x) - known)
    law(rid, "R05 no undeclared xw leg keys",
        "PASS" if not extra else "FAIL", str(extra))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    for path in argv[1:]:
        rid = path.split("/")[-2] if path.endswith("measurements.json") \
            else path.split("/")[-1]
        derive(rid, path)
    npass = sum(1 for r in results if r[2] == "PASS")
    nfail = sum(1 for r in results if r[2] == "FAIL")
    nblk = sum(1 for r in results if r[2] == "BLOCKED")
    for rid, name, verdict, detail in results:
        print(f"LAW {rid} {name} {verdict} {detail}")
    base = [r for r in results if not r[1].startswith("R")]
    radd = [r for r in results if r[1].startswith("R")]
    print(f"SUMMARY receipts={len(set(r[0] for r in results))} "
          f"PASS={npass} FAIL={nfail} BLOCKED={nblk} "
          f"TOTAL={npass + nfail + nblk} "
          f"| base106={len(base)} pass={sum(1 for r in base if r[2] == 'PASS')} "
          f"fail={sum(1 for r in base if r[2] == 'FAIL')} "
          f"blocked={sum(1 for r in base if r[2] == 'BLOCKED')} "
          f"| R-add={len(radd)} pass={sum(1 for r in radd if r[2] == 'PASS')} "
          f"fail={sum(1 for r in radd if r[2] == 'FAIL')} "
          f"blocked={sum(1 for r in radd if r[2] == 'BLOCKED')}")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
