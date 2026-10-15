#!/usr/bin/env python3
"""r97-scout stage C — default-node policy in a private PipeWire+WirePlumber pair.

Every leg is bounded (wall cap + byte cap, process-group kill). Nothing here
touches the shared daemons: the env points at corpus/live/r97-scout/run.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97lib import (SEAT, RUN, ENV, PwCli, run, dump, nodes, meta_rows,
                    nullsink, sink_by_name, default_sink_value)

REC = os.path.join(SEAT, "receipts")


def wait_default(name, cap=6.0):
    """Poll until default.audio.sink == name (or cap). Returns (ok, value, secs)."""
    t0 = time.monotonic()
    val = None
    while time.monotonic() - t0 < cap:
        objs = dump()
        _, val = default_sink_value(objs)
        got = (val or {}).get("name") if isinstance(val, dict) else val
        if got == name:
            return True, val, round(time.monotonic() - t0, 2)
        time.sleep(0.3)
    return False, val, round(time.monotonic() - t0, 2)


def wait_node(name, cap=6.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < cap:
        i = sink_by_name(dump(), name)
        if i is not None:
            return i
        time.sleep(0.2)
    return None


def configured_state():
    p = os.path.join(SEAT, "conf", "xdg-state", "wireplumber", "default-nodes")
    if not os.path.exists(p):
        return None
    return open(p).read()


def rep(n, cli):
    obs = {"rep": n, "steps": []}

    def note(tag, **kw):
        kw["tag"] = tag
        kw["t"] = round(time.monotonic() - t0, 2)
        obs["steps"].append(kw)

    t0 = time.monotonic()
    # 0. clean slate
    note("clear_default", r=run(["wpctl", "clear-default"], timeout=6.0))
    time.sleep(0.5)

    # 1. A alone, priority.session=100
    nullsink(cli, f"r97s_a{n}", 100, 100)
    ida = wait_node(f"r97s_a{n}")
    ok, val, secs = wait_default(f"r97s_a{n}")
    note("A_first_sink_becomes_default", node=ida, default=val, ok=ok, secs=secs)

    # 2. B higher session priority -> should take over
    nullsink(cli, f"r97s_b{n}", 200, 100)
    idb = wait_node(f"r97s_b{n}")
    ok, val, secs = wait_default(f"r97s_b{n}")
    note("B_higher_session_priority_takes_default", node=idb, default=val, ok=ok, secs=secs)

    # 3. C lower session priority -> must NOT take over
    nullsink(cli, f"r97s_c{n}", 50, 999)
    idc = wait_node(f"r97s_c{n}")
    time.sleep(1.2)
    _, val = default_sink_value(dump())
    note("C_lower_session_priority_does_not_take_default", node=idc, default=val)

    # 4. explicit user choice on C
    note("set_default_C", r=run(["wpctl", "set-default", str(idc)], timeout=6.0))
    ok, val, secs = wait_default(f"r97s_c{n}")
    note("C_explicit_default", node=idc, default=val, ok=ok, secs=secs)
    obs["state_after_set_default"] = configured_state()

    # 5. D with the highest priority appears -> explicit choice must survive
    nullsink(cli, f"r97s_d{n}", 300, 100)
    idd = wait_node(f"r97s_d{n}")
    time.sleep(1.5)
    _, val = default_sink_value(dump())
    note("D_highest_priority_does_not_override_explicit", node=idd, default=val)

    # 6. clear-default -> best (D) must win
    note("clear_default_2", r=run(["wpctl", "clear-default"], timeout=6.0))
    ok, val, secs = wait_default(f"r97s_d{n}")
    note("after_clear_default_best_wins", default=val, ok=ok, secs=secs)

    # 7. remove the current default (D) -> fallback
    cli.cmd(f"destroy {idd}")
    time.sleep(1.0)
    ok, val, secs = wait_default(f"r97s_b{n}")
    note("removed_default_falls_back_to_best_remaining", default=val, ok=ok, secs=secs)

    # 8. only priority.driver differs -> who wins?
    cli.cmd(f"destroy {ida}"); cli.cmd(f"destroy {idb}"); cli.cmd(f"destroy {idc}")
    time.sleep(1.0)
    note("clear_default_3", r=run(["wpctl", "clear-default"], timeout=6.0))
    nullsink(cli, f"r97s_e{n}", 100, 100)
    ide = wait_node(f"r97s_e{n}")
    nullsink(cli, f"r97s_f{n}", 100, 999)
    idf = wait_node(f"r97s_f{n}")
    time.sleep(1.5)
    _, val = default_sink_value(dump())
    note("driver_priority_only_e_vs_f", e=ide, f=idf, default=val)

    # 9. node with no priority.session at all
    nullsink(cli, f"r97s_g{n}", "", "")
    idg = wait_node(f"r97s_g{n}")
    time.sleep(1.5)
    _, val = default_sink_value(dump())
    note("no_priority_session_node_g", g=idg, default=val)

    # 10. cleanup: destroy own sinks, clear default
    for i in (ide, idf, idg):
        if i:
            cli.cmd(f"destroy {i}")
    time.sleep(0.8)
    note("final_clear_default", r=run(["wpctl", "clear-default"], timeout=6.0))
    obs["state_final"] = configured_state()
    return obs


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = {"stage": "c_default_nodes", "host": os.uname().nodename,
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "env": {k: ENV[k] for k in ("PIPEWIRE_RUNTIME_DIR", "XDG_STATE_HOME")},
           "reps": []}
    for n in range(reps):
        cli = PwCli(logpath=os.path.join(SEAT, "scratch", f"pwcli_c{n}.log"))
        try:
            out["reps"].append(rep(n, cli))
        finally:
            cli.close()
            time.sleep(1.0)
    os.makedirs(REC, exist_ok=True)
    with open(os.path.join(REC, "c_default_nodes.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
