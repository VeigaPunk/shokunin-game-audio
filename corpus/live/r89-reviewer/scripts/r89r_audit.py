#!/usr/bin/env python3
"""r89 reviewer audit — independent, receipt-only re-derivation of EVERY
armed verdict branch of the r89 pwprof family.

Target: committed blob 0d732989:corpus/fixtures/measure_audio.py
sha256 623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22
(lines 29293-30781: constants, helpers, the four *_r89_entry functions).

This script imports NOTHING from the fixture and touches no live host: it
re-implements the verdict code against receipt JSON alone. Where the receipt
retains `stdout_raw` (the keep_raw legs) the derived fields are RE-COMPUTED
and cross-checked against the recorded ones; where the raw was popped by
design (signal legs, schema windows) the recorded derived fields are used
and their internal consistency is checked against recorded primitives.

Usage: r89r_audit.py <receipt.json> [<receipt.json> ...]
"""
import json
import sys
from pathlib import Path

PWPROF = "pwprof_"


# ---------------------------------------------------------------- helpers
def jparse(text):
    """Mirror of _pwprof_r89_jparse."""
    txt = (text or "").strip()
    try:
        arr = json.loads(txt)
    except ValueError as exc:
        return None, f"{exc} (len={len(txt)})"
    return arr, None


def blocks(arr):
    """Mirror of _pwprof_r89_blocks."""
    out, cur = [], None
    for r in arr or []:
        if not isinstance(r, dict) or not r:
            continue
        if r.get("type") == "info":
            cur = {"info": r, "clock": None, "driver": None,
                   "followers": [], "fclocks": [], "other": [],
                   "seq": ["info"]}
            out.append(cur)
        elif cur is None:
            continue
        else:
            cur["seq"].append(r.get("type"))
            if r.get("type") == "clock":
                cur["clock"] = r
            elif r.get("type") == "driver":
                cur["driver"] = r
            elif r.get("type") == "follower":
                cur["followers"].append(r)
            elif r.get("type") == "followerClock":
                cur["fclocks"].append(r)
            else:
                cur["other"].append(r)
    return out


def n_info(arr):
    return sum(1 for r in arr
               if isinstance(r, dict) and r.get("type") == "info") \
        if arr else None


def derive(leg, checks, tag):
    """Return (parse_error, n_info, term_ok) re-derived from stdout_raw when
    present, else the recorded values; cross-check both when both exist."""
    rec = (leg.get("parse_error"), leg.get("n_info"), leg.get("term_ok"))
    if "stdout_raw" in leg:
        arr, perr = jparse(leg.get("stdout_raw") or "")
        got = (perr, n_info(arr), bool(arr) and arr[-1] == {})
        checks.append((f"{tag}.derived-vs-raw",
                       got == rec,
                       f"recomputed={got} recorded={rec}"))
        return got
    return rec


def chk(checks, name, ok, detail=""):
    checks.append((name, bool(ok), detail))


# ---------------------------------------------------------------- entries
def audit_gate(e):
    """Every armed branch of pwprof_gate_r89_entry (verdicts 29939-30038)."""
    checks, legs = [], e.get("legs") or {}
    chk(checks, "gate.g_link",
        (legs.get("g_link") or {}).get("player"),
        f"player={(legs.get('g_link') or {}).get('player')} "
        "(coverage_blocked when falsy)")

    l = legs.get("g_own") or {}
    pe, ni, tk = derive(l, checks, "g_own")
    if "stdout_raw" in l:
        arr, _ = jparse(l.get("stdout_raw") or "")
        drv = sorted({(b.get("driver") or {}).get("name")
                      for b in blocks(arr)
                      if (b.get("driver") or {}).get("name")})
        chk(checks, "g_own.drivers-derived",
            drv == sorted(l.get("drivers") or []),
            f"derived={drv} recorded={l.get('drivers')}")
    chk(checks, "g_own.verdict",
        l.get("exit_code") == 0 and tk and ni == 8,
        f"rc={l.get('exit_code')} term={tk} n_info={ni}")

    l = legs.get("g_two") or {}
    pe, ni, tk = derive(l, checks, "g_two")
    if "stdout_raw" in l:
        arr, _ = jparse(l.get("stdout_raw") or "")
        tb = blocks(arr)
        hist = sorted({n: sum(1 for b in tb
                              if (b.get("driver") or {}).get("name") == n)
                       for n in {(b.get("driver") or {}).get("name")
                                 for b in tb} if n}.items())
        chk(checks, "g_two.hist-derived",
            [list(x) for x in hist] ==
            [list(x) for x in (l.get("driver_info_hist") or [])],
            f"derived={hist} recorded={l.get('driver_info_hist')}")
    chk(checks, "g_two.verdict",
        l.get("exit_code") == 0 and ni == 4 and tk and
        (l.get("wall_s") or 9) <= 1.5,
        f"rc={l.get('exit_code')} n_info={ni} term={tk} "
        f"wall={l.get('wall_s')} hist={l.get('driver_info_hist')}")

    for nm, want_rc in (("g_term", 0), ("g_int", 0)):
        l = legs.get(nm) or {}
        chk(checks, f"{nm}.verdict",
            l.get("exit_code") == want_rc and l.get("term_ok") is True,
            f"rc={l.get('exit_code')} term={l.get('term_ok')}")

    for nm, want in (("g_kill", -9), ("g_hup", -1), ("g_usr1", -10)):
        l = legs.get(nm) or {}
        chk(checks, f"{nm}.verdict",
            l.get("exit_code") == want and l.get("parse_error") is not None,
            f"rc={l.get('exit_code')} parse={str(l.get('parse_error'))[:60]}")

    l = legs.get("g_blocks") or {}
    samples = l.get("stream_samples") or []
    nonzero = [s for s in samples if s.get("bytes")]
    chk(checks, "g_blocks.verdict",
        bool(nonzero) and not any(s["bytes"] % 4096 for s in nonzero),
        f"samples={samples}")

    l = legs.get("g_o_ignored") or {}
    chk(checks, "g_o_ignored.verdict",
        not l.get("file_created") and
        "Logging to" not in (l.get("stderr") or ""),
        f"created={l.get('file_created')} stderr={l.get('stderr')!r}")

    l = legs.get("g_extra") or {}
    pe, ni, tk = derive(l, checks, "g_extra")
    chk(checks, "g_extra.verdict",
        l.get("exit_code") == 0 and ni == 4,
        f"rc={l.get('exit_code')} n_info={ni}")

    l = legs.get("g_remote_empty") or {}
    pe, ni, tk = derive(l, checks, "g_remote_empty")
    chk(checks, "g_remote_empty.verdict",
        l.get("exit_code") == 0 and ni == 4,
        f"rc={l.get('exit_code')} n_info={ni}")

    for nm in ("g_remote_bogus", "g_env_bogus"):
        l = legs.get(nm) or {}
        chk(checks, f"{nm}.verdict",
            l.get("exit_code") == 255 and
            l.get("error_class") == "pwprof_connect_down",
            f"rc={l.get('exit_code')} class={l.get('error_class')} "
            f"hit={l.get('error_hit')}")

    l = legs.get("g_opt_bogus") or {}
    chk(checks, "g_opt_bogus.verdict",
        l.get("exit_code") == 255 and l.get("error_class") == "pwprof_opt",
        f"rc={l.get('exit_code')} class={l.get('error_class')}")

    l = legs.get("g_version") or {}
    chk(checks, "g_version.verdict",
        l.get("exit_code") == 0 and
        "libpipewire" in (l.get("stdout") or ""),
        f"rc={l.get('exit_code')} stdout={l.get('stdout')!r}")

    l = legs.get("g_lastwins") or {}
    pe, ni, tk = derive(l, checks, "g_lastwins")
    chk(checks, "g_lastwins.verdict",
        l.get("alive_at_sig") is True and l.get("exit_code") == 0 and
        (ni or 0) >= 5,
        f"alive={l.get('alive_at_sig')} rc={l.get('exit_code')} "
        f"n_info={ni}")

    for nm, want in (("n_007", 7), ("n_plus3", 3), ("n_space3", 3)):
        l = legs.get(nm) or {}
        pe, ni, tk = derive(l, checks, nm)
        chk(checks, f"{nm}.verdict",
            l.get("exit_code") == 0 and ni == want and
            l.get("alive_at_sig") is not True,
            f"rc={l.get('exit_code')} n_info={ni} "
            f"alive={l.get('alive_at_sig')}")

    for nm in ("n_2_5", "n_3abc", "n_1e1", "n_huge", "n_neg",
               "n_abc", "n_zero"):
        l = legs.get(nm) or {}
        pe, ni, tk = derive(l, checks, nm)
        chk(checks, f"{nm}.verdict",
            l.get("alive_at_sig") is True and l.get("exit_code") == 0 and
            (ni or 0) >= 5,
            f"alive={l.get('alive_at_sig')} rc={l.get('exit_code')} "
            f"n_info={ni}")

    # teardown / structure
    chk(checks, "gate.sinks_gone",
        isinstance(e.get("sinks_gone"), dict) and
        all(e["sinks_gone"].values()) and bool(e["sinks_gone"]),
        f"{e.get('sinks_gone')}")
    chk(checks, "gate.own_nodes_after",
        e.get("own_nodes_after") == [],
        f"{e.get('own_nodes_after')}")
    chk(checks, "gate.unloads",
        bool(e.get("unloads")) and all(
            (v or {}).get("exit_code") == 0
            for v in (e.get("unloads") or {}).values()),
        f"{ {k: (v or {}).get('exit_code') for k, v in (e.get('unloads') or {}).items()} }")
    return checks


def audit_oart(e):
    """Every armed branch of pwprof_oart_r89_entry (verdicts 30152-30213)."""
    checks, legs = [], e.get("legs") or {}
    aux_want = {f"Timing{i}.plot" for i in range(1, 6)} | \
        {"Timings.html", "generate_timings.sh"}
    chk(checks, "oart.o_link",
        (legs.get("o_link") or {}).get("player"),
        f"player={(legs.get('o_link') or {}).get('player')}")

    l = legs.get("o_live") or {}
    chk(checks, "o_live.verdict",
        l.get("exit_code") == 0 and l.get("rows") == 10 and
        aux_want.issubset(set(l.get("aux_present") or ())) and
        "Logging to" in (l.get("stderr") or "") and
        "generate_timings" in (l.get("stdout") or "") +
        (l.get("stderr") or ""),
        f"rc={l.get('exit_code')} rows={l.get('rows')} "
        f"aux={l.get('aux_present')}")

    l = legs.get("o_int") or {}
    chk(checks, "o_int.verdict",
        l.get("exit_code") == 0 and (l.get("bytes") or 0) > 0,
        f"rc={l.get('exit_code')} bytes={l.get('bytes')}")

    l = legs.get("o_kill") or {}
    chk(checks, "o_kill.verdict",
        l.get("exit_code") == -9 and (l.get("bytes") or 0) > 0 and
        (l.get("rows") or 0) > 0,
        f"rc={l.get('exit_code')} bytes={l.get('bytes')} "
        f"rows={l.get('rows')}")

    l = legs.get("o_exist") or {}
    chk(checks, "o_exist.verdict", l.get("marker_gone") is True,
        f"marker_gone={l.get('marker_gone')}")

    l = legs.get("o_eager") or {}
    chk(checks, "o_eager.verdict", l.get("watch_seen") is not None,
        f"watch_seen={l.get('watch_seen')}")

    l = legs.get("o_default") or {}
    chk(checks, "o_default.verdict",
        l.get("exit_code") == 0 and (l.get("profiler_log") or 0) > 0,
        f"rc={l.get('exit_code')} profiler.log={l.get('profiler_log')}")

    l = legs.get("o_dash") or {}
    chk(checks, "o_dash.verdict",
        l.get("exit_code") == 0 and (l.get("dash_file") or 0) > 0,
        f"rc={l.get('exit_code')} dash={l.get('dash_file')}")

    l = legs.get("o_devnull") or {}
    chk(checks, "o_devnull.verdict",
        l.get("exit_code") == 0 and
        aux_want.issubset(set(l.get("aux_present") or ())),
        f"rc={l.get('exit_code')} aux={l.get('aux_present')}")

    for nm in ("o_dir", "o_empty", "o_proc"):
        l = legs.get(nm) or {}
        chk(checks, f"{nm}.verdict",
            l.get("exit_code") == 255 and
            l.get("error_class") == "pwprof_cant_open",
            f"rc={l.get('exit_code')} class={l.get('error_class')}")

    chk(checks, "oart.sinks_gone",
        isinstance(e.get("sinks_gone"), dict) and
        all(e["sinks_gone"].values()) and bool(e["sinks_gone"]),
        f"{e.get('sinks_gone')}")
    chk(checks, "oart.own_nodes_after", e.get("own_nodes_after") == [],
        f"{e.get('own_nodes_after')}")
    return checks


def audit_schema(e):
    """Every armed branch of pwprof_schema_r89_entry (verdicts 30338-30343)."""
    checks, legs = [], e.get("legs") or {}
    chk(checks, "schema.s_link",
        (legs.get("s_link") or {}).get("player"),
        f"player={(legs.get('s_link') or {}).get('player')}")

    l = legs.get("s_window") or {}
    st = l.get("stats") or {}
    chk(checks, "s_window.window",
        l.get("exit_code") == 0 and l.get("parse_error") is None,
        f"rc={l.get('exit_code')} parse={l.get('parse_error')}")
    chk(checks, "s_window.own_blocks>=3",
        (st.get("own_blocks") or 0) >= 3, f"own_blocks={st.get('own_blocks')}")
    if st.get("own_blocks"):
        counts = st.get("own_counts") or []
        chk(checks, "s_window.count_step_ok-consistency",
            st.get("count_step_ok") == all(
                counts[i + 1] == counts[i] + 1
                for i in range(len(counts) - 1)),
            f"recorded={st.get('count_step_ok')} from counts={counts[:4]}...")
        shapes = [tuple(s) for s in (st.get("own_seq_shapes") or [])]
        chk(checks, "s_window.seq_order_ok-consistency",
            st.get("seq_order_ok") == all(
                s[:3] == ("info", "clock", "driver") for s in shapes),
            f"recorded={st.get('seq_order_ok')} shapes={shapes}")
        chk(checks, "s_window.seq_order_ok",
            st.get("seq_order_ok") is True, f"{st.get('own_seq_shapes')}")
        chk(checks, "s_window.count_step_ok",
            bool(st.get("count_step_ok")),
            f"counts={st.get('own_counts')}")
        chk(checks, "s_window.quantum_relation_ok",
            st.get("quantum_relation_ok") is True,
            f"rates={st.get('rates')} durations={st.get('durations')}")
        chk(checks, "s_window.pos_step_ok",
            st.get("pos_step_ok") is True, "")
        chk(checks, "s_window.transports==[stopped]",
            (st.get("transports") or []) == ["stopped"],
            f"{st.get('transports')}")
        chk(checks, "s_window.diffs==[1.0]",
            (st.get("diffs") or []) == [1.0], f"{st.get('diffs')}")
        chk(checks, "s_window.order_ok",
            st.get("order_ok") is True, "")
        chk(checks, "s_window.prev_is_last_signal",
            st.get("prev_is_last_signal") is True, "")
        chk(checks, "s_window.driver_statuses==[finished]",
            (st.get("driver_statuses") or []) == ["finished"],
            f"{st.get('driver_statuses')}")
        chk(checks, "s_window.driver_latencies==[0/0]",
            (st.get("driver_latencies") or []) == ["0/0"],
            f"{st.get('driver_latencies')}")
        own_id = ((e.get("refs") or {}).get("own_node_id"))
        chk(checks, "s_window.id-law",
            set(st.get("clock_ids") or ()) == {own_id} and
            set(st.get("driver_ids") or ()) == {own_id},
            f"clock_ids={st.get('clock_ids')} driver_ids="
            f"{st.get('driver_ids')} own={own_id}")
        chk(checks, "s_window.clock_names",
            (st.get("clock_names") or []) == ["clock.system.monotonic"],
            f"{st.get('clock_names')}")
        chk(checks, "s_window.nsec_in_window",
            st.get("nsec_in_window") is True, "")
        chk(checks, "s_window.xrun==0",
            (st.get("xruns") or [1]) == [0] and
            (st.get("xrun_counts") or [1]) == [0],
            f"xruns={st.get('xruns')} counts={st.get('xrun_counts')}")
        chk(checks, "s_window.fclock_rows==0",
            not st.get("fclock_rows"), f"{st.get('fclock_rows')}")
        chk(checks, "s_window.nsb_blocks==0",
            (st.get("nsb_blocks") or 0) == 0, f"{st.get('nsb_blocks')}")

    l = legs.get("s_second") or {}
    c1 = (st.get("own_counts") or [None])[-1]
    c2 = (l.get("own_counts") or [None])[0]
    chk(checks, "s_second.monotone",
        bool(l.get("own_counts")) and c1 is not None and c2 is not None and
        c2 > c1, f"counts {c1} -> {c2}")

    l = legs.get("s_suspend") or {}
    if l.get("kill_mono") is None:
        chk(checks, "s_suspend.kill-hook", False,
            "kill hook never fired — leg unmeasured")
    else:
        chk(checks, "s_suspend.pre>0", (l.get("own_pre_kill") or 0) > 0,
            f"pre={l.get('own_pre_kill')}")
        chk(checks, "s_suspend.after==0",
            (l.get("own_after_kill") or 0) == 0,
            f"after={l.get('own_after_kill')} "
            f"foreign_after={l.get('foreign_after_kill')} "
            f"own_blocks={l.get('own_blocks')}")

    chk(checks, "schema.sinks_gone",
        isinstance(e.get("sinks_gone"), dict) and
        all(e["sinks_gone"].values()) and bool(e["sinks_gone"]),
        f"{e.get('sinks_gone')}")
    chk(checks, "schema.own_nodes_after", e.get("own_nodes_after") == [],
        f"{e.get('own_nodes_after')}")
    return checks


def audit_xw(e):
    """Every armed branch of pwprof_xw_r89_entry (verdicts 30695-30778)."""
    checks, legs = [], e.get("legs") or {}
    chk(checks, "xw.x_link",
        (legs.get("x_link") or {}).get("player"),
        f"player={(legs.get('x_link') or {}).get('player')}")

    l = legs.get("x_modreg") or {}
    chk(checks, "x_modreg.verdict",
        l.get("own_in_dump_modules") is False and
        l.get("own_node_in_dump") is True and
        str(l.get("own_pactl_idx")) in (l.get("pactl_added") or ()),
        f"{l}")

    l = legs.get("x_blank") or {}
    chk(checks, "x_blank.verdict",
        bool(l.get("blank_lines")) and l.get("own_found") is not None,
        f"{l}")

    l = legs.get("x_foot") or {}
    chk(checks, "x_foot.verdict",
        l.get("pwprof_during") == (l.get("pwprof_before") or 0) + 1 and
        l.get("nodes_delta") == 0, f"{l}")

    l = legs.get("x_conc") or {}
    chk(checks, "x_conc.capture",
        l.get("rc1") == 0 and l.get("rc2") == 0 and
        not l.get("parse1") and not l.get("parse2"),
        f"rc={l.get('rc1')},{l.get('rc2')} parse="
        f"{l.get('parse1')},{l.get('parse2')}")
    if not l.get("shared"):
        chk(checks, "x_conc.coverage",
            True,
            "zero overlapping blocks -> coverage_blocked, law unmeasured")
    else:
        chk(checks, "x_conc.broadcast",
            l.get("shared_identical") is True,
            f"shared={l.get('shared')} identical={l.get('shared_identical')} "
            f"bytes={l.get('bytes1')}/{l.get('bytes2')} "
            f"byte_identical={l.get('byte_identical')}")

    l = legs.get("x_top") or {}
    row = l.get("own_row") or {}
    pw, pb = l.get("prof_wait_us_med"), l.get("prof_busy_us_med")
    if l.get("own_row") is None:
        chk(checks, "x_top.coverage", True,
            "no real-state own row -> coverage_blocked")
    elif pw is None or pb is None or row.get("wait_us") is None or \
            row.get("busy_us") is None:
        chk(checks, "x_top.coverage", True, f"partial witnesses {l}")
    else:
        def close(a, b):
            return a is not None and b is not None and \
                0.25 <= (a / b if b else float("inf")) <= 4.0
        chk(checks, "x_top.agreement",
            close(row["wait_us"], pw) and close(row["busy_us"], pb),
            f"top {row['wait_us']}/{row['busy_us']}us vs profiler "
            f"{pw}/{pb}us")

    l = legs.get("x_profobj") or {}
    if not l.get("ids"):
        chk(checks, "x_profobj.coverage", True,
            "no Profiler object -> coverage_blocked")
    else:
        for sub in ("info", "enum"):
            r = l.get(sub) or {}
            chk(checks, f"x_profobj.{sub}",
                r.get("exit_code") == 0 and
                "unsupported type PipeWire:Interface:Profiler" in
                (r.get("stderr") or "") + (r.get("stdout") or ""),
                f"rc={r.get('exit_code')} stderr={r.get('stderr')!r}")

    l = legs.get("x_sigpipe") or {}
    chk(checks, "x_sigpipe.verdict", l.get("rc") == -13, f"rc={l.get('rc')}")

    l = legs.get("x_devfull") or {}
    chk(checks, "x_devfull.verdict",
        l.get("rc") == 0 and l.get("stderr_bytes") == 0, f"{l}")

    chk(checks, "xw.sinks_gone",
        isinstance(e.get("sinks_gone"), dict) and
        all(e["sinks_gone"].values()) and bool(e["sinks_gone"]),
        f"{e.get('sinks_gone')}")
    chk(checks, "xw.own_nodes_after", e.get("own_nodes_after") == [],
        f"{e.get('own_nodes_after')}")
    return checks


AUDIT = {"pwprof_gate_r89_probe": audit_gate,
         "pwprof_oart_r89_probe": audit_oart,
         "pwprof_schema_r89_probe": audit_schema,
         "pwprof_xw_r89_probe": audit_xw}


def main(paths):
    grand = {"checks": 0, "passed": 0, "failed": 0, "runs": {}}
    for p in paths:
        doc = json.loads(Path(p).read_text())
        meas = doc.get("measurements", doc)
        run = {"file": p, "mode": doc.get("mode"),
               "entries": {}, "checks": 0, "passed": 0, "failed": 0,
               "recorded_failures": {}, "coverage_blocked": {}}
        for name, fn in AUDIT.items():
            e = meas.get(name)
            if e is None:
                run["entries"][name] = "MISSING"
                continue
            checks = fn(e)
            bad = [c for c in checks if not c[1]]
            run["entries"][name] = {
                "checks": len(checks), "failed": len(bad),
                "failures": [c[0] + ": " + c[2] for c in bad]}
            run["checks"] += len(checks)
            run["passed"] += len(checks) - len(bad)
            run["failed"] += len(bad)
            run["recorded_failures"][name] = e.get("failures")
            run["coverage_blocked"][name] = e.get("coverage_blocked")
        grand["checks"] += run["checks"]
        grand["passed"] += run["passed"]
        grand["failed"] += run["failed"]
        grand["runs"][p] = run
        print(f"== {p}")
        print(f"   mode={run['mode']} checks={run['checks']} "
              f"passed={run['passed']} failed={run['failed']}")
        for name, r in run["entries"].items():
            if r == "MISSING":
                print(f"   {name}: MISSING")
                continue
            print(f"   {name}: {r['checks'] - r['failed']}/{r['checks']}"
                  f" (recorded failures={run['recorded_failures'][name]},"
                  f" coverage_blocked={run['coverage_blocked'][name]})")
            for f in r["failures"]:
                print(f"      FAIL {f}")
    print(f"== TOTAL checks={grand['checks']} passed={grand['passed']} "
          f"failed={grand['failed']}")
    out = Path(__file__).resolve().parent.parent / "receipts" / \
        "audit-summary.json"
    out.write_text(json.dumps(grand, indent=2) + "\n")
    print(f"wrote {out}")
    return 1 if grand["failed"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
