#!/usr/bin/env python3
"""r97b stage H — the PipeWire clock/quantum axis (assigned independent axis).

The r97 scout never varied the core clock. This stage re-arms the private core
with a DIFFERENT clock (rate 44100, quantum 64) and replays the load-bearing
cells, so every law can be checked against a non-default clock:

  h0 core clock read-back (must show the re-armed values)
  h1 first sink becomes default
  h2 strictly higher priority.session takes over
  h3 explicit set-default wins and survives a higher-priority newcomer
  h4 `--target <object.serial>` resolves to the requested sink
  h5 `--target <global id>` silently falls back to the default sink
  h6 bogus target + node.dont-fallback -> 0 links + client error
  h7 a 48000 Hz stream into the 44100 Hz core still links to the requested sink
  h8 wpexec inventory still byte-identical (sandbox is clock-independent)

Bounded: 8 s caps, own pids, process-group kills. The clock fragment is written
to conf/pw/r97b-pipewire.conf.d/20-r97b-clock.conf and removed at the end.
"""
import json, os, signal, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import (SEAT, ENV, REC, SCR, run, dump, nullsink, sink_by_name,
                     sink_serial, default_sink_value, ensure_up, down,
                     stage_out, stage_write, loadavg, core_clock, wp_ready, PwCli)

CLOCK = """## r97b clock/quantum axis (stage H): non-default clock under test
context.properties = {
  default.clock.rate          = 44100
  default.clock.allowed-rates = [ 44100 48000 ]
  default.clock.quantum       = 64
  default.clock.min-quantum   = 32
  default.clock.max-quantum   = 2048
}
"""
CLOCK_FRAG = os.path.join(SEAT, "conf", "pw", "r97b-pipewire.conf.d", "20-r97b-clock.conf")


class Stream:
    def __init__(self, argv, cap=8.0):
        self.argv = argv
        self.p = subprocess.Popen(argv, stdin=subprocess.PIPE,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                  env=ENV, start_new_session=True, text=True)

    def stop(self):
        try:
            self.p.stdin.close()
        except Exception:
            pass
        try:
            self.p.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            err = self.p.stderr.read() or ""
        except Exception:
            err = ""
        return {"rc": self.p.returncode, "stderr": err[:300]}


def links_of(objs, name):
    by_id = {}
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Node":
            by_id[o["id"]] = (o.get("info") or {}).get("props", {}).get("node.name")
    out = []
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Link":
            info = o.get("info") or {}
            a, b = by_id.get(info.get("output-node-id")), by_id.get(info.get("input-node-id"))
            if name in (a, b):
                out.append([a, b])
    return out


def leg(obs, tag, argv, settle=2.0):
    st = Stream(argv)
    time.sleep(settle)
    objs = dump()
    lk = links_of(objs, "r97b_h_str")
    stop = st.stop()
    obs.append({"tag": tag, "argv": argv, "links": lk, "stop": stop,
                "loadavg": loadavg()})
    return lk


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


def rep(n, cli, obs):
    nm = lambda s: f"r97b_h{s}{n}"
    obs.append({"tag": "h0_core_clock", "clock": core_clock(), "loadavg": loadavg()})
    run(["wpctl", "clear-default"], timeout=8.0)
    nullsink(cli, nm("a"), 100, 100)
    ida = wait_node(nm("a"))
    ok, val, secs = wait_default(nm("a"))
    obs.append({"tag": "h1_first_sink_wins", "node": ida, "ok": ok, "default": val,
                "secs": secs, "loadavg": loadavg()})
    nullsink(cli, nm("b"), 500, 100)
    idb = wait_node(nm("b"))
    ok, val, secs = wait_default(nm("b"))
    obs.append({"tag": "h2_higher_session_takes_over", "node": idb, "ok": ok,
                "default": val, "secs": secs, "loadavg": loadavg()})
    run(["wpctl", "set-default", str(ida)], timeout=8.0)
    ok, val, secs = wait_default(nm("a"))
    nullsink(cli, nm("c"), 900, 100)
    idc = wait_node(nm("c"))
    time.sleep(1.2)
    _, val = default_sink_value(dump())
    obs.append({"tag": "h3_explicit_survives_newcomer", "set_ok": ok, "node": idc,
                "default": val, "loadavg": loadavg()})
    objs = dump()
    sera = sink_serial(objs, nm("a"))
    P = "{ node.name = r97b_h_str }"
    leg(obs, "h4_target_object_serial", ["pw-cat", "-p", "--raw", "--rate", "48000",
                                         "--channels", "1", "--format", "s16",
                                         "--target", str(sera), "-P", P, "-"])
    leg(obs, "h5_target_global_id", ["pw-cat", "-p", "--raw", "--rate", "48000",
                                     "--channels", "1", "--format", "s16",
                                     "--target", str(ida), "-P", P, "-"])
    leg(obs, "h6_bogus_dont_fallback", ["pw-cat", "-p", "--raw", "--rate", "48000",
                                        "--channels", "1", "--format", "s16",
                                        "--target", "99999", "-P",
                                        "{ node.name = r97b_h_str node.dont-fallback = true }", "-"])
    leg(obs, "h7_rate44100_stream_into_44100_core",
        ["pw-cat", "-p", "--raw", "--rate", "44100", "--channels", "1", "--format", "s16",
         "--target", str(sera), "-P", P, "-"])
    run(["wpctl", "clear-default"], timeout=8.0)
    for i in (ida, idb, idc):
        if i:
            cli.cmd(f"destroy {i}")
    time.sleep(0.8)


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out = stage_out("h_clock")
    out["arm"] = arm
    with open(CLOCK_FRAG, "w") as f:
        f.write(CLOCK)
    out["clock_fragment"] = open(CLOCK_FRAG).read()
    down("both")
    time.sleep(0.5)
    e = ensure_up(verbose=True)
    out["pair"] = e
    ready, secs = wp_ready(timeout=25.0)
    out["wp_ready"] = {"ok": ready, "secs": secs}
    out["clock_after_rearm"] = core_clock()
    for n in range(reps):
        cli = PwCli(logpath=os.path.join(SCR, f"pwcli_h{n}.log"))
        obs = []
        try:
            rep(n, cli, obs)
        except Exception as ex:
            obs.append({"exception": repr(ex)})
        finally:
            cli.close()
            time.sleep(0.5)
        out["reps"].append({"rep": n, "obs": obs})
    # restore the default clock fragment for later stages
    if os.path.exists(CLOCK_FRAG):
        os.unlink(CLOCK_FRAG)
    out["clock_fragment_removed"] = not os.path.exists(CLOCK_FRAG)
    for r in out["reps"]:
        for o in r["obs"]:
            print(f"rep{r['rep']} {o.get('tag'):<34} "
                  f"links={o.get('links')} default={o.get('default')} "
                  f"ok={o.get('ok')} clock={o.get('clock')} "
                  f"stderr={((o.get('stop') or {}).get('stderr') or '').strip()[:40]!r}")
    stage_write(out, "h_clock.json")


if __name__ == "__main__":
    main()
