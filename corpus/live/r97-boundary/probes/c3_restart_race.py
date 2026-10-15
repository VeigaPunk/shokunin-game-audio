#!/usr/bin/env python3
"""r97b stage C3R — the configured-default / restart RACE.

The r97 scout states two things that are in tension:
  (a) `wpctl set-default` writes the state file
      `$XDG_STATE_HOME/wireplumber/default-nodes` (claim 5), and
  (b) the configured default survives a WirePlumber restart (claim 4 / §3.2),
  (c) §3.2 also notes "the file lags the metadata by up to ~1 s (observed empty
      1 s after set-default, populated later)".

If (c) is real, then (b) cannot be unconditional: a restart inside the lag
window must lose the configured choice. This stage arms that race directly.

Arms (own private pair, fresh pw-cli session, 3 reps each):
  R1 restart immediately after set-default          (t ~= 0, inside the lag)
  R2 restart after the state-file row appears       (t = observed lag)
  R3 restart after a fixed 0.5 s wait               (inside the lag, bounded)
Plus a fine-grained lag measurement (poll the state file every 50 ms) in R2.
Bounded: 10 s caps, own pids only, guarded kills.
"""
import json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import (SEAT, ENV, REC, SCR, run, dump, nullsink, sink_by_name,
                     default_sink_value, meta_value, state_file, ensure_up, down,
                     stage_out, stage_write, loadavg, hog_count, note_wedge,
                     health_or_rearm, PwCli)


def wait_default(name, cap=12.0, interval=0.1):
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
        time.sleep(interval)
    return False, val, round(time.monotonic() - t0, 3)


def wait_node(name, cap=12.0):
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


def lag_until_file(needle, cap=6.0, interval=0.05):
    t0 = time.monotonic()
    while time.monotonic() - t0 < cap:
        s = state_file() or ""
        if needle in s:
            return round(time.monotonic() - t0, 3), s
        time.sleep(interval)
    return None, state_file()


def restart_wp():
    down("wp")
    time.sleep(0.3)
    up = subprocess.run([os.path.join(SEAT, "probes", "up.sh"), "wp"],
                        capture_output=True, text=True, timeout=90, env=ENV)
    return up.stdout.strip()


def arm(n, mode, obs):
    """One rep of the race. mode in {'immediate','wait_file','wait_500ms'}"""
    nm = lambda s: f"r97b_rr{s}{n}"
    run(["wpctl", "clear-default"], timeout=8.0)
    cli = PwCli(logpath=os.path.join(SCR, f"pwcli_rr{n}_{mode}.log"))
    try:
        nullsink(cli, nm("p"), 100, 100)
        idp = wait_node(nm("p"))
        nullsink(cli, nm("q"), 500, 100)
        idq = wait_node(nm("q"))
        ok, val, secs = wait_default(nm("q"))
        step = {"mode": mode, "p": idp, "q": idq,
                "q_is_default_before_set": ok, "default": val, "secs": secs}
        t_set = time.monotonic()
        run(["wpctl", "set-default", str(idp)], timeout=8.0)
        ok, val, secs = wait_default(nm("p"))
        step["p_took_over"] = ok
        step["p_took_over_secs"] = secs
        step["state_file_at_set"] = state_file()
        step["t_set_to_restart_s"] = round(time.monotonic() - t_set, 3)

        if mode == "wait_file":
            lag, body = lag_until_file(f"default.configured.audio.sink={nm('p')}")
            step["file_lag_s"] = lag
            step["state_file_before_restart"] = body
        elif mode == "wait_500ms":
            time.sleep(0.5)
            step["state_file_before_restart"] = state_file()
        else:
            step["state_file_before_restart"] = state_file()
        step["t_set_to_restart_s"] = round(time.monotonic() - t_set, 3)

        step["up"] = restart_wp()
        ok, val, secs = wait_default(nm("p"), cap=12.0)
        step["after_restart_default_is_p"] = ok
        step["after_restart_default"] = val
        step["after_restart_secs"] = secs
        objs = dump()
        step["after_restart_rows"] = {k: meta_value(objs, k)[1] for k in
                                      ("default.audio.sink",
                                       "default.configured.audio.sink",
                                       "default.configured.audio.sink.0")}
        step["state_file_after_restart"] = state_file()
        step["loadavg"] = loadavg()
        obs.append(step)
    finally:
        cli.close()
        time.sleep(0.5)


def main():
    arm_name = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out = stage_out("c3_restart_race")
    out["arm"] = arm_name
    out["reps"] = []
    e = ensure_up(verbose=True)
    out["pair"] = e
    for n in range(reps):
        for mode in ("immediate", "wait_file", "wait_500ms"):
            obs = []
            try:
                arm(n, mode, obs)
            except Exception as ex:
                obs.append({"mode": mode, "exception": repr(ex)})
            out["reps"].append({"rep": n, "obs": obs})
            h = health_or_rearm(context=f"c3r rep{n} {mode}")
            out.setdefault("rearms", []).append(h)
    for r in out["reps"]:
        for s in r["obs"]:
            print(f"rep{r['rep']} {s.get('mode'):<12} "
                  f"file_at_set={(s.get('state_file_at_set') or '').strip()!r:<46} "
                  f"lag={s.get('file_lag_s')} t_set_to_restart={s.get('t_set_to_restart_s')} "
                  f"after_p={s.get('after_restart_default_is_p')} "
                  f"default={s.get('after_restart_default')}")
    stage_write(out, "c3_restart_race.json")


if __name__ == "__main__":
    main()
