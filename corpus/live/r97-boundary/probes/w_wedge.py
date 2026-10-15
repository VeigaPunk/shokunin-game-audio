#!/usr/bin/env python3
"""r97b stage W — isolating the private-core WEDGE (r97 scout §2.5 / [?]3).

The scout observed the wedge twice ("process alive, sockets present, zero
replies to any client") but did not isolate a trigger. This stage arms four
candidate triggers against a freshly re-armed private pair, probing liveness
between every step with a bounded `pw-dump`, and records the exact operation
that preceded the first failed probe.

  W1 dump storm        : N x pw-dump (no mutation)
  W2 sink churn        : N x (create sink -> dump -> destroy -> dump)
  W3 set-default churn : N x (wpctl set-default / clear-default) with two sinks
  W4 wp restart churn  : N x (stop WP -> start WP) with sinks alive
Every trigger runs on its own freshly re-armed pair, so a wedge cannot leak
between variants. Bounded: 6 s liveness cap, 10 s operation cap, own pids only.
"""
import json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import (SEAT, ENV, REC, SCR, RUN, run, dump, nullsink, sink_by_name,
                     default_sink_value, ensure_up, down, stage_out, stage_write,
                     loadavg, hog_count, note_wedge, health, PwCli)

LIVE_CAP = 6.0


def arm_fresh(verbose=False):
    down("both")
    time.sleep(0.5)
    return ensure_up(verbose=verbose)


def probe(tag, live=()):
    """Bounded liveness probe; returns dict with ok + the live operation log."""
    h = health(cap=LIVE_CAP, context=tag)
    return h


def variant(name, fn, steps, out):
    rep = {"variant": name, "steps": steps, "log": [], "loadavg_start": loadavg(),
           "hogs": hog_count()}
    arm_fresh()
    h0 = probe(f"{name}/before")
    rep["health_before"] = h0
    if not h0["ok"]:
        rep["skipped"] = "core not healthy before the variant"
        out["variants"].append(rep)
        return rep
    cli = PwCli(logpath=os.path.join(SCR, f"pwcli_w_{name}.log"))
    try:
        fn(cli, rep, out)
    except Exception as e:
        rep["exception"] = repr(e)
    finally:
        cli.close()
    out["variants"].append(rep)
    return rep


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    n_steps = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    out = stage_out("w_wedge")
    out["arm"] = arm
    out["n_steps"] = n_steps
    out["variants"] = []

    # ---------------- W1 dump storm ----------------
    def w1(cli, rep, out):
        for i in range(n_steps):
            h = probe(f"W1/dump{i}")
            rep["log"].append({"i": i, "op": "pw-dump", **h})
            if not h["ok"]:
                rep["wedge_at"] = i
                note_wedge("wedge_W1_dump_storm", f"step {i}", h)
                return
        rep["wedge_at"] = None

    # ---------------- W2 sink churn ----------------
    def w2(cli, rep, out):
        for i in range(n_steps):
            name = f"r97b_w2_{i}"
            nullsink(cli, name, 100, 100)
            h1 = probe(f"W2/create{i}")
            rep["log"].append({"i": i, "op": "create-node", "name": name, **h1})
            if not h1["ok"]:
                rep["wedge_at"] = i
                note_wedge("wedge_W2_create", f"step {i}", h1)
                return
            i2 = sink_by_name(dump(), name)
            if i2 is not None:
                cli.cmd(f"destroy {i2}")
            h2 = probe(f"W2/destroy{i}")
            rep["log"].append({"i": i, "op": "destroy", "id": i2, **h2})
            if not h2["ok"]:
                rep["wedge_at"] = i
                note_wedge("wedge_W2_destroy", f"step {i}", h2)
                return
        rep["wedge_at"] = None

    # ---------------- W3 set-default churn ----------------
    def w3(cli, rep, out):
        nullsink(cli, "r97b_w3_a", 100, 100)
        nullsink(cli, "r97b_w3_b", 500, 100)
        time.sleep(1.0)
        for i in range(n_steps):
            objs = dump()
            if objs is None:
                rep["wedge_at"] = i
                note_wedge("wedge_W3_setup_dump", f"step {i}", {"loadavg": loadavg()})
                return
            ia = sink_by_name(objs, "r97b_w3_a")
            ib = sink_by_name(objs, "r97b_w3_b")
            tgt = ia if i % 2 == 0 else ib
            r = run(["wpctl", "set-default", str(tgt)], timeout=10.0)
            h = probe(f"W3/set-default{i}")
            rep["log"].append({"i": i, "op": "wpctl set-default", "id": tgt,
                               "rc": r["rc"], "dur_s": r["dur_s"], **h})
            if not h["ok"]:
                rep["wedge_at"] = i
                note_wedge("wedge_W3_set_default", f"step {i}", h)
                return
            if i % 5 == 4:
                rc = run(["wpctl", "clear-default"], timeout=10.0)
                h2 = probe(f"W3/clear{i}")
                rep["log"].append({"i": i, "op": "wpctl clear-default",
                                   "rc": rc["rc"], **h2})
                if not h2["ok"]:
                    rep["wedge_at"] = i
                    note_wedge("wedge_W3_clear_default", f"step {i}", h2)
                    return
        rep["wedge_at"] = None

    # ---------------- W4 wp restart churn ----------------
    def w4(cli, rep, out):
        nullsink(cli, "r97b_w4_a", 100, 100)
        nullsink(cli, "r97b_w4_b", 500, 100)
        time.sleep(1.0)
        for i in range(n_steps):
            d = down("wp")
            up = subprocess.run([os.path.join(SEAT, "probes", "up.sh"), "wp"],
                                capture_output=True, text=True, timeout=90, env=ENV)
            h = probe(f"W4/restart{i}")
            rep["log"].append({"i": i, "op": "wp restart", "up": up.stdout.strip(),
                               "down": d.stdout.strip()[:80], **h})
            if not h["ok"]:
                rep["wedge_at"] = i
                note_wedge("wedge_W4_wp_restart", f"step {i}", h)
                return
            rc = run(["wpctl", "status"], timeout=10.0)
            rep["log"].append({"i": i, "op": "wpctl status after restart",
                               "rc": rc["rc"], "timed_out": rc["timed_out"],
                               "dur_s": rc["dur_s"], "bytes": len(rc["stdout"])})
        rep["wedge_at"] = None

    which = sys.argv[3] if len(sys.argv) > 3 else "all"
    outname = sys.argv[4] if len(sys.argv) > 4 else "w_wedge.json"

    # ---------------- W5 rapid connection storm ----------------
    def w5(cli, rep, out):
        """N back-to-back short-lived pw-dump clients, no sleep. This is the
        shape stage C actually produced (poll loops at 0.1 s with a 10 s cap)."""
        fail = 0
        for i in range(n_steps):
            h = probe(f"W5/dump{i}", )
            if i % 25 == 0 or not h["ok"]:
                rep["log"].append({"i": i, "op": "pw-dump", **h})
            if not h["ok"]:
                fail += 1
                if fail == 1:
                    rep["wedge_at"] = i
                    note_wedge("wedge_W5_rapid_dumps", f"step {i}", h)
                    return
        rep["wedge_at"] = None
        rep["final"] = probe("W5/final")

    table = {"W1_dump_storm": w1, "W2_sink_churn": w2,
             "W3_setdefault_churn": w3, "W4_wp_restart_churn": w4,
             "W5_rapid_dump_storm": w5}
    for name, fn in table.items():
        if which not in ("all", name):
            continue
        r = variant(name, fn, n_steps, out)
        print(f"--- {name}: wedge_at={r.get('wedge_at')} "
              f"steps={len(r['log'])} loadavg={r['loadavg_start']} "
              f"hogs={r['hogs']} {r.get('skipped', '')}")
        if r["log"]:
            last = r["log"][-1]
            print(f"    last op: {json.dumps(last)[:200]}")
    # merge with any earlier variants already receipted in the same file
    prev = os.path.join(REC, outname)
    if os.path.exists(prev):
        try:
            old = json.load(open(prev))
            keep = [v for v in old.get("variants", [])
                    if v["variant"] not in {v2["variant"] for v2 in out["variants"]}]
            out["variants"] = keep + out["variants"]
            out["merged_from"] = prev.replace(SEAT, "$SEAT")
        except Exception as e:
            out["merge_error"] = repr(e)
    stage_write(out, outname)


if __name__ == "__main__":
    main()
