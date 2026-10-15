#!/usr/bin/env python3
"""r97-scout stage C2 — the cells stage C left ambiguous:
  - priority.driver control with REVERSED creation order
  - a sink with no priority.session at all
  - the configured-default metadata row + state file
  - state restore across a private WirePlumber restart (own instance only)
"""
import json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97lib import (SEAT, RUN, ENV, PwCli, run, dump, meta_rows, nullsink,
                    sink_by_name, default_sink_value)

REC = os.path.join(SEAT, "receipts")


def rows_by_key(name):
    mid, rows = meta_rows(dump(), name)
    return mid, {r["key"]: r.get("value") for r in (rows or [])}


def wait_node(name, cap=6.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < cap:
        i = sink_by_name(dump(), name)
        if i is not None:
            return i
        time.sleep(0.2)
    return None


def wait_default(name, cap=6.0):
    t0 = time.monotonic()
    val = None
    while time.monotonic() - t0 < cap:
        _, val = default_sink_value(dump())
        if (val or {}).get("name") == name:
            return True, val, round(time.monotonic() - t0, 2)
        time.sleep(0.3)
    return False, val, round(time.monotonic() - t0, 2)


def state_file():
    p = os.path.join(SEAT, "conf", "xdg-state", "wireplumber", "default-nodes")
    if not os.path.exists(p):
        return {"exists": False}
    return {"exists": True, "size": os.path.getsize(p),
            "content": open(p).read()[:400]}


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = {"stage": "c2_default_controls", "reps": []}
    for n in range(reps):
        cli = PwCli(logpath=os.path.join(SEAT, "scratch", f"pwcli_c2_{n}.log"))
        obs = {"rep": n, "steps": []}
        t0 = time.monotonic()

        def note(tag, **kw):
            kw["tag"] = tag
            kw["t"] = round(time.monotonic() - t0, 2)
            obs["steps"].append(kw)

        try:
            run(["wpctl", "clear-default"], timeout=6.0)
            # --- driver-priority control: create the HIGH-driver sink FIRST ---
            nullsink(cli, f"r97s_h{n}", 100, 999)   # high driver priority
            idh = wait_node(f"r97s_h{n}")
            nullsink(cli, f"r97s_l{n}", 100, 100)   # low driver priority
            idl = wait_node(f"r97s_l{n}")
            time.sleep(1.5)
            _, val = default_sink_value(dump())
            note("driver_control_high_first", high=idh, low=idl, default=val)

            # --- a sink with no priority.session key at all ---
            props = (f"{{ factory.name=support.null-audio-sink node.name=r97s_np{n} "
                     f"node.description=r97s_np{n} media.class=Audio/Sink }}")
            cli.cmd("create-node adapter " + props)
            idn = wait_node(f"r97s_np{n}")
            time.sleep(1.5)
            _, val = default_sink_value(dump())
            note("no_priority_session_key", node=idn, default=val)

            # --- explicit default: metadata + state file ---
            run(["wpctl", "clear-default"], timeout=6.0)
            time.sleep(0.5)
            run(["wpctl", "set-default", str(idl)], timeout=6.0)
            ok, val, secs = wait_default(f"r97s_l{n}")
            mid, drow = rows_by_key("default")
            note("set_default_row", default=val, ok=ok,
                 default_metadata_id=mid,
                 configured=drow.get("default.configured.audio.sink"),
                 sink_row=drow.get("default.audio.sink"))
            time.sleep(2.0)   # give the state hook time to flush
            obs["state_after_set"] = state_file()

            # --- destroy everything, then check the configured row survives ---
            for i in (idh, idl, idn):
                if i:
                    cli.cmd(f"destroy {i}")
            time.sleep(1.0)
            mid, drow = rows_by_key("default")
            note("configured_row_without_sinks", default_metadata_id=mid,
                 configured=drow.get("default.configured.audio.sink"),
                 sink_row=drow.get("default.audio.sink"))
            obs["state_no_sinks"] = state_file()
        finally:
            cli.close()
            time.sleep(0.5)
        out["reps"].append(obs)
    os.makedirs(REC, exist_ok=True)
    json.dump(out, open(os.path.join(REC, "c2_default_controls.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
