#!/usr/bin/env python3
"""r97b stage C — replay of the r97 scout default-node policy cells (claim 4-5,
rows `wp.default.*`) with fresh processes, plus the timing claims the scout's
row table asserts (`default.audio.sink` within <=0.1 s; state file lag <=1 s).

Cells (namespaced r97b_*, own private pair, own pw-cli session per rep):
  c1 first sink becomes default                    (timed)
  c2 strictly higher priority.session takes over   (timed)
  c3 lower priority.session does not
  c4 wpctl set-default on the low-priority sink    (both metadata rows + state file)
  c5 newcomer with the highest priority does not steal an explicit default
  c6 clear-default -> best available
  c7 destroying the default falls back to the best remaining
  c8 equal priority.session, different priority.driver, BOTH creation orders
  c9 a sink with no priority at all does not displace a 100
  c10 no priority.session but priority.driver=999 DOES take over
  c11 configured default survives a private WirePlumber restart (+ history .0)
  c12 state-file byte content after set-default

Bounded: 12 s cap per external call, process-group kill, own pid files only.
"""
import json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import (SEAT, ENV, REC, SCR, run, dump, nodes, meta_rows, nullsink,
                     sink_by_name, default_sink_value, meta_value, state_file,
                     ensure_up, down, stage_out, stage_write, loadavg, PwCli,
                     note_wedge, health, health_or_rearm)

STATE = os.path.join(SEAT, "conf", "xdg-state", "wireplumber", "default-nodes")


class Wedged(Exception):
    pass


WEDGE = {"events": 0, "context": ""}


def dd(tag=""):
    """dump() that turns a wedged core into an abort of the current rep."""
    objs = dump()
    if objs is None:
        WEDGE["events"] += 1
        WEDGE["context"] = tag
        note_wedge("stage_c_dump_fail", tag, {"events": WEDGE["events"]})
        raise Wedged(tag)
    return objs


def dump_timed(tag=""):
    t0 = time.monotonic()
    objs = dd(tag)
    return objs, round(time.monotonic() - t0, 3)


def wait_default(name, cap=10.0, interval=0.1):
    """Poll default.audio.sink; return (ok, value, secs, polls, max_dump_s)."""
    t0 = time.monotonic()
    val, polls, maxd = None, 0, 0.0
    while time.monotonic() - t0 < cap:
        objs, d = dump_timed(f"wait_default:{name}")
        polls += 1
        maxd = max(maxd, d)
        _, val = default_sink_value(objs)
        got = (val or {}).get("name") if isinstance(val, dict) else val
        if got == name:
            return True, val, round(time.monotonic() - t0, 3), polls, maxd
        time.sleep(interval)
    return False, val, round(time.monotonic() - t0, 3), polls, maxd


def wait_node(name, cap=10.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < cap:
        i = sink_by_name(dd(f"wait_node:{name}"), name)
        if i is not None:
            return i
        time.sleep(0.2)
    return None


def wait_file_contains(needle, cap=8.0, interval=0.1):
    t0 = time.monotonic()
    while time.monotonic() - t0 < cap:
        s = state_file() or ""
        if needle in s:
            return True, round(time.monotonic() - t0, 3), s
        time.sleep(interval)
    return False, round(time.monotonic() - t0, 3), state_file()


def rows_now():
    objs = dd("rows_now")
    return {k: meta_value(objs, k)[1] for k in
            ("default.audio.sink", "default.configured.audio.sink",
             "default.configured.audio.sink.0")}


def purge_own_sinks(cli, objs):
    """Destroy any pre-existing `r97b_*` node before the cells.

    Own-namespace only (name prefix `r97b_`): a previous stage of THIS seat can
    leave sinks alive (a killed chain orphans its pw-cli session), and a
    leftover `priority.session=500` sink silently contaminates c3/c6/c8. Never
    touches a node outside this seat's namespace.
    """
    killed = []
    for i, n, mc, ps, d in nodes(objs):
        if (n or "").startswith("r97b_") and mc in ("Audio/Sink", "Audio/Source"):
            cli.cmd(f"destroy {i}")
            killed.append((i, n, ps))
    if killed:
        time.sleep(0.8)
    return killed


def rep(n, cli):
    obs = {"rep": n, "steps": []}
    t0 = time.monotonic()

    def note(tag, **kw):
        kw["tag"] = tag
        kw["t"] = round(time.monotonic() - t0, 3)
        kw["loadavg"] = loadavg()
        obs["steps"].append(kw)
        return kw

    def nm(s):
        return f"r97b_{s}{n}"

    try:
        run(["wpctl", "clear-default"], timeout=8.0)
        obs["purged_before_rep"] = purge_own_sinks(cli, dd("purge"))
        time.sleep(0.3)

        # c1 first sink wins
        nullsink(cli, nm("a"), 100, 100)
        ida = wait_node(nm("a"))
        ok, val, secs, polls, maxd = wait_default(nm("a"))
        note("c1_first_sink_becomes_default", node=ida, ok=ok, default=val,
             secs=secs, polls=polls, max_dump_s=maxd)

        # c2 higher session priority takes over
        nullsink(cli, nm("b"), 200, 100)
        idb = wait_node(nm("b"))
        ok, val, secs, polls, maxd = wait_default(nm("b"))
        note("c2_higher_session_takes_over", node=idb, ok=ok, default=val,
             secs=secs, polls=polls, max_dump_s=maxd)

        # c3 lower session priority does not
        nullsink(cli, nm("c"), 50, 999)
        idc = wait_node(nm("c"))
        time.sleep(1.5)
        _, val = default_sink_value(dd("cell_read"))
        note("c3_lower_session_does_not_take", node=idc, default=val)

        # c4 explicit set-default on the low-priority sink
        note("c4_set_default_c", r=run(["wpctl", "set-default", str(idc)], timeout=8.0))
        ok, val, secs, polls, maxd = wait_default(nm("c"))
        note("c4_explicit_default", ok=ok, default=val, secs=secs, polls=polls)
        f_ok, f_secs, f_body = wait_file_contains(f"default.configured.audio.sink={nm('c')}")
        obs["state_file_after_c4"] = {"found": f_ok, "secs": f_secs, "body": f_body}
        note("c4_state_file_lag", found=f_ok, secs=f_secs)
        note("c4_metadata_rows", rows=rows_now())

        # c5 newcomer with the highest priority does not steal
        nullsink(cli, nm("d"), 300, 100)
        idd = wait_node(nm("d"))
        time.sleep(1.5)
        _, val = default_sink_value(dd("cell_read"))
        note("c5_highest_priority_newcomer_does_not_steal", node=idd, default=val)

        # c6 clear-default -> best (d)
        note("c6_clear_default", r=run(["wpctl", "clear-default"], timeout=8.0))
        ok, val, secs, polls, maxd = wait_default(nm("d"))
        note("c6_after_clear_default_best_wins", ok=ok, default=val, secs=secs)

        # c7 destroy the default -> best remaining
        cli.cmd(f"destroy {idd}")
        time.sleep(0.5)
        ok, val, secs, polls, maxd = wait_default(nm("b"))
        note("c7_removed_default_falls_back", ok=ok, default=val, secs=secs)

        # c8 equal session priority, different driver priority, both orders
        for i in (ida, idb, idc):
            if i:
                cli.cmd(f"destroy {i}")
        time.sleep(0.6)
        run(["wpctl", "clear-default"], timeout=8.0)
        # order A: low driver first
        nullsink(cli, nm("e"), 100, 100)
        ide = wait_node(nm("e"))
        ok_e = wait_default(nm("e"))[0]
        nullsink(cli, nm("f"), 100, 999)
        idf = wait_node(nm("f"))
        time.sleep(1.5)
        _, val = default_sink_value(dd("cell_read"))
        note("c8a_low_driver_first_incumbent_keeps", e=ide, f=idf, default=val)
        for i in (ide, idf):
            if i:
                cli.cmd(f"destroy {i}")
        time.sleep(0.6)
        run(["wpctl", "clear-default"], timeout=8.0)
        # order B: high driver first
        nullsink(cli, nm("g"), 100, 999)
        idg = wait_node(nm("g"))
        wait_default(nm("g"))
        nullsink(cli, nm("h"), 100, 100)
        idh = wait_node(nm("h"))
        time.sleep(1.5)
        _, val = default_sink_value(dd("cell_read"))
        note("c8b_high_driver_first_incumbent_keeps", g=idg, h=idh, default=val)
        for i in (idg, idh):
            if i:
                cli.cmd(f"destroy {i}")
        time.sleep(0.6)
        run(["wpctl", "clear-default"], timeout=8.0)

        # c9/c10: no priority.session; driver 999 vs an incumbent with session 100
        nullsink(cli, nm("i"), 100, 100)
        idi = wait_node(nm("i"))
        wait_default(nm("i"))
        nullsink(cli, nm("j"), "", "")
        idj = wait_node(nm("j"))
        time.sleep(1.5)
        _, val = default_sink_value(dd("cell_read"))
        note("c9_no_priority_node_does_not_displace", i=idi, j=idj, default=val)
        nullsink(cli, nm("k"), "", 999)
        idk = wait_node(nm("k"))
        ok, val, secs, polls, maxd = wait_default(nm("k"))
        note("c10_no_session_driver999_takes_over", i=idi, k=idk, ok=ok,
             default=val, secs=secs)
        for i in (idi, idj, idk):
            if i:
                cli.cmd(f"destroy {i}")
        time.sleep(0.6)
        run(["wpctl", "clear-default"], timeout=8.0)
        obs["state_file_final"] = state_file()
    except Exception as e:
        note("exception", error=repr(e))
    return obs


def rep_restart(n, cli):
    """c11: configured default survives a private WirePlumber restart."""
    obs = {"rep": n, "steps": []}
    t0 = time.monotonic()

    def note(tag, **kw):
        kw["tag"] = tag
        kw["t"] = round(time.monotonic() - t0, 3)
        kw["loadavg"] = loadavg()
        obs["steps"].append(kw)

    def nm(s):
        return f"r97b_r{s}{n}"

    run(["wpctl", "clear-default"], timeout=8.0)
    nullsink(cli, nm("p"), 100, 100)
    idp = wait_node(nm("p"))
    nullsink(cli, nm("q"), 500, 100)
    idq = wait_node(nm("q"))
    wait_default(nm("q"))
    run(["wpctl", "set-default", str(idp)], timeout=8.0)
    ok, val, secs, _, _ = wait_default(nm("p"))
    note("before_restart_low_priority_configured", p=idp, q=idq, ok=ok, secs=secs)
    obs["state_before"] = state_file()

    down("wp")
    time.sleep(1.0)
    up = subprocess.run([os.path.join(SEAT, "probes", "up.sh"), "wp"],
                        capture_output=True, text=True, timeout=90, env=ENV)
    note("wp_restart", up=up.stdout.strip())
    t1 = time.monotonic()
    ok, val, secs, polls, _ = wait_default(nm("p"), cap=15.0)
    note("after_restart_default_is_configured_p", ok=ok, default=val,
         secs_since_up=round(time.monotonic() - t1, 3), polls=polls)
    objs = dd("after_restart_rows")
    note("after_restart_rows", rows={k: meta_value(objs, k)[1] for k in
                                     ("default.audio.sink", "default.configured.audio.sink",
                                      "default.configured.audio.sink.0")},
         p_alive=sink_by_name(objs, nm("p")), q_alive=sink_by_name(objs, nm("q")))
    obs["state_after"] = state_file()
    return obs


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out = stage_out("c_defaults")
    out["arm"] = arm
    e = ensure_up(verbose=True)
    out["pair"] = e
    if not e.get("ok") and not e.get("already"):
        out["fatal"] = "private pair did not come up"
        stage_write(out, "c_defaults.json")
        return
    cells_only = "cells-only" in sys.argv
    for n in range(reps):
        for attempt in (0, 1):
            WEDGE["events"] = 0
            cli = PwCli(logpath=os.path.join(SCR, f"pwcli_c{n}_{attempt}.log"))
            try:
                r = rep(n, cli)
            except Wedged as e:
                r = {"rep": n, "aborted": "wedged", "context": str(e), "steps": []}
            finally:
                cli.close()
                time.sleep(0.5)
            r["attempt"] = attempt
            r["wedge_events"] = WEDGE["events"]
            if WEDGE["events"] == 0 or attempt == 1:
                out["reps"].append(r)
                break
            out.setdefault("wedge_recoveries", []).append(
                health_or_rearm(context=f"c_defaults cells rep{n} attempt{attempt}",
                                verbose=False))
        if cells_only:
            out["loadavg_end_rep"] = loadavg()
            continue
        for attempt in (0, 1):
            WEDGE["events"] = 0
            cli = PwCli(logpath=os.path.join(SCR, f"pwcli_cr{n}_{attempt}.log"))
            try:
                r = rep_restart(n, cli)
            except Wedged as e:
                r = {"rep": n, "aborted": "wedged", "context": str(e), "steps": []}
            finally:
                cli.close()
                time.sleep(0.5)
            r["attempt"] = attempt
            r["wedge_events"] = WEDGE["events"]
            if WEDGE["events"] == 0 or attempt == 1:
                out["reps"].append(r)
                break
            out.setdefault("wedge_recoveries", []).append(
                health_or_rearm(context=f"c_defaults restart rep{n} attempt{attempt}",
                                verbose=False))
        out["loadavg_end_rep"] = loadavg()
    for r in out["reps"]:
        print(f"--- rep {r['rep']} attempt={r.get('attempt')} "
              f"wedge_events={r.get('wedge_events')} "
              f"{'ABORTED' if r.get('aborted') else ''}")
        for s in r["steps"]:
            d = {k: v for k, v in s.items() if k not in ("tag", "t", "loadavg")}
            print(f"  {s['tag']:<44} t={s['t']:>6} {json.dumps(d)[:170]}")
    stage_write(out, "c_defaults.json")


if __name__ == "__main__":
    main()
