#!/usr/bin/env python3
"""r97b stage C4 — the priority.driver fallback cells (r97 scout §3.1 cells
10-11), armed correctly.

The scout's cells 10/11 need sinks that carry **no** `priority.session` key at
all (not an empty value: `priority.session=` is a spa-json parse error and the
node is never created — measured in the first r97b pass). This stage creates
them by omitting the keys.

Cells (own private pair, fresh pw-cli per rep, 3 reps):
  n1 incumbent session=100 ; challenger with NO priority keys -> incumbent keeps
  n2 incumbent session=100 ; challenger driver=999 only       -> challenger wins
  n3 incumbent session=100 ; challenger driver=999 only ;
     then a session=200 newcomer                             -> session 200 wins
Bounded: 8 s caps, own pids only.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import (SEAT, ENV, REC, SCR, run, dump, nullsink, sink_by_name,
                     default_sink_value, ensure_up, stage_out, stage_write,
                     loadavg, PwCli)


def create(cli, name, session=None, driver=None):
    props = (f"{{ factory.name=support.null-audio-sink node.name={name} "
             f"node.description={name} media.class=Audio/Sink ")
    if session is not None:
        props += f"priority.session={session} "
    if driver is not None:
        props += f"priority.driver={driver} "
    props += "}"
    return cli.cmd(f"create-node adapter {props}")


def wait_node(name, cap=10.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < cap:
        objs = dump()
        if objs is None:
            return None
        i = sink_by_name(objs, name)
        if i is not None:
            return i
        time.sleep(0.2)
    return None


def wait_default(name, cap=10.0):
    t0 = time.monotonic()
    val = None
    while time.monotonic() - t0 < cap:
        objs = dump()
        if objs is None:
            return None, None, round(time.monotonic() - t0, 3)
        _, val = default_sink_value(objs)
        got = (val or {}).get("name") if isinstance(val, dict) else val
        if got == name:
            return True, val, round(time.monotonic() - t0, 3)
        time.sleep(0.2)
    return False, val, round(time.monotonic() - t0, 3)


def rep(n, cli, obs):
    nm = lambda s: f"r97b_n{s}{n}"
    run(["wpctl", "clear-default"], timeout=8.0)
    # n1
    create(cli, nm("a"), session=100, driver=100)
    ida = wait_node(nm("a"))
    wait_default(nm("a"))
    create(cli, nm("b"))                      # no priority keys at all
    idb = wait_node(nm("b"))
    time.sleep(1.2)
    _, val = default_sink_value(dump())
    obs.append({"tag": "n1_no_priority_keys_does_not_displace", "a": ida, "b": idb,
                "default": val, "loadavg": loadavg()})
    for i in (ida, idb):
        if i:
            cli.cmd(f"destroy {i}")
    time.sleep(0.8)
    run(["wpctl", "clear-default"], timeout=8.0)

    # n2
    create(cli, nm("c"), session=100, driver=100)
    idc = wait_node(nm("c"))
    wait_default(nm("c"))
    create(cli, nm("d"), driver=999)          # driver only, no session
    idd = wait_node(nm("d"))
    ok, val, secs = wait_default(nm("d"))
    obs.append({"tag": "n2_driver_only_999_takes_over", "c": idc, "d": idd,
                "ok": ok, "default": val, "secs": secs, "loadavg": loadavg()})

    # n3: a session=200 newcomer must beat the driver-999 node
    create(cli, nm("e"), session=200, driver=100)
    ide = wait_node(nm("e"))
    ok, val, secs = wait_default(nm("e"))
    obs.append({"tag": "n3_session_200_beats_driver_only_999", "e": ide, "ok": ok,
                "default": val, "secs": secs, "loadavg": loadavg()})
    for i in (idc, idd, ide):
        if i:
            cli.cmd(f"destroy {i}")
    time.sleep(0.8)
    run(["wpctl", "clear-default"], timeout=8.0)


def main():
    arm_name = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out = stage_out("c4_priority")
    out["arm"] = arm_name
    e = ensure_up(verbose=True)
    out["pair"] = e
    for n in range(reps):
        cli = PwCli(logpath=os.path.join(SCR, f"pwcli_n{n}.log"))
        obs = []
        try:
            rep(n, cli, obs)
        except Exception as ex:
            obs.append({"exception": repr(ex)})
        finally:
            cli.close()
            time.sleep(0.5)
        out["reps"].append({"rep": n, "obs": obs})
    for r in out["reps"]:
        for o in r["obs"]:
            print(f"rep{r['rep']} {o.get('tag')} default={o.get('default')} "
                  f"ok={o.get('ok')} {json.dumps({k: v for k, v in o.items() if k in ('a','b','c','d','e')})}")
    stage_write(out, "c4_priority.json")


if __name__ == "__main__":
    main()
