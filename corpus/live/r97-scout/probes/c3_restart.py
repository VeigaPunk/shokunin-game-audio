#!/usr/bin/env python3
"""r97-scout stage C3 — configured-default history + restore across a
private WirePlumber restart (this seat's own instance only; the shared
WirePlumber is never signalled).
"""
import json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97lib import (SEAT, ENV, PwCli, run, dump, meta_rows, nullsink,
                    sink_by_name, default_sink_value, ensure_up)

REC = os.path.join(SEAT, "receipts")


def up_wp():
    return subprocess.run([os.path.join(SEAT, "probes", "up.sh"), "wp"],
                          capture_output=True, text=True, timeout=60, env=ENV)


def down_wp():
    """Restart ONLY the private WirePlumber; the private core stays up."""
    return subprocess.run([os.path.join(SEAT, "probes", "down.sh"), "wp"],
                          capture_output=True, text=True, timeout=60, env=ENV)


def rows(name="default"):
    mid, rr = meta_rows(dump(), name)
    return mid, {r["key"]: r.get("value") for r in (rr or [])}


def wait_node(name, cap=6.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < cap:
        i = sink_by_name(dump(), name)
        if i is not None:
            return i
        time.sleep(0.2)
    return None


def state_file():
    p = os.path.join(SEAT, "conf", "xdg-state", "wireplumber", "default-nodes")
    return open(p).read() if os.path.exists(p) else None


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = {"stage": "c3_restart", "reps": []}
    ensure_up()
    for n in range(reps):
        cli = PwCli(logpath=os.path.join(SEAT, "scratch", f"pwcli_c3_{n}.log"))
        obs = {"rep": n, "steps": []}
        t0 = time.monotonic()

        def note(tag, **kw):
            kw["tag"] = tag
            kw["t"] = round(time.monotonic() - t0, 2)
            obs["steps"].append(kw)

        try:
            run(["wpctl", "clear-default"], timeout=6.0)
            # two live sinks, kept alive by this pw-cli session
            nullsink(cli, f"r97s_p{n}", 100, 100)
            idp = wait_node(f"r97s_p{n}")
            nullsink(cli, f"r97s_q{n}", 500, 100)
            idq = wait_node(f"r97s_q{n}")
            time.sleep(1.2)
            _, d = default_sink_value(dump())
            note("q_high_priority_is_default", p=idp, q=idq, default=d)

            # explicit choice of the LOW priority sink
            run(["wpctl", "set-default", str(idp)], timeout=6.0)
            time.sleep(0.8)
            mid, rw = rows()
            note("configured_p", default=rw.get("default.audio.sink"),
                 configured=rw.get("default.configured.audio.sink"))
            # history: now choose Q explicitly too
            run(["wpctl", "set-default", str(idq)], timeout=6.0)
            time.sleep(0.8)
            mid, rw = rows()
            note("configured_q_history", configured=rw.get("default.configured.audio.sink"),
                 configured_0=rw.get("default.configured.audio.sink.0"),
                 default=rw.get("default.audio.sink"))
            obs["state_after_two_sets"] = state_file()

            # back to P, then restart WP with the sinks still alive
            run(["wpctl", "set-default", str(idp)], timeout=6.0)
            time.sleep(1.0)
            before_mid, before = rows()
            note("before_restart", mid=before_mid, default=before.get("default.audio.sink"),
                 configured=before.get("default.configured.audio.sink"))

            down_wp()
            time.sleep(1.0)
            note("wp_down", alive_after=None, up=up_wp().stdout.strip())
            time.sleep(2.5)
            after_mid, after = rows()
            note("after_restart", mid=after_mid,
                 default=after.get("default.audio.sink"),
                 configured=after.get("default.configured.audio.sink"),
                 p_alive=sink_by_name(dump(), f"r97s_p{n}"),
                 q_alive=sink_by_name(dump(), f"r97s_q{n}"))
            obs["state_after_restart"] = state_file()
        finally:
            cli.close()
            time.sleep(0.5)
            for nm in (f"r97s_p{n}", f"r97s_q{n}"):
                pass
        out["reps"].append(obs)
    os.makedirs(REC, exist_ok=True)
    json.dump(out, open(os.path.join(REC, "c3_restart.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
