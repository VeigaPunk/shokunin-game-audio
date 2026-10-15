#!/usr/bin/env python3
"""r97b stage A2 — where does the r97 scout's V1 failure chain actually live?

The scout's claim 1 reports, for `WIREPLUMBER_CONFIG_DIR=<dir without
wireplumber.conf>`: `no modules loaded from context.modules` -> `can't find
protocol 'PipeWire:Protocol:Native'` -> `Failed to connect to PipeWire`.
Neither string is in any r97-scout receipt. `strings` puts the first two in
**libpipewire** (`libpipewire-0.3.so.0`) and the third in `/usr/bin/wireplumber`.

This stage arms the shape that actually produces the chain, in its own runtime
dir `run2/` (never the shared one, never this seat's main pair):
  L1  `pipewire -c <stub with no context.modules>`          (core alone)
  L2  same stub core, then `wireplumber -c wireplumber.conf -p main` on top
Bounded: 8 s cap per leg; the stub core is killed by its own pid with a
cmdline namespace guard.
"""
import json, os, signal, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import SEAT, ENV, REC, SCR, run, stage_out, stage_write, loadavg

RUN2 = os.path.join(SEAT, "run2")
CHAIN = ["no modules loaded from context.modules",
         "can't find protocol 'PipeWire:Protocol:Native'",
         "Failed to connect to PipeWire",
         "Could not locate configuration file 'wireplumber.conf'",
         "Could not locate script 'sm-objects.lua'"]


def guarded_kill(pid):
    try:
        cmd = open(f"/proc/{pid}/cmdline").read().replace("\0", " ")
    except Exception:
        return "gone"
    if SEAT in cmd:
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except Exception:
            try:
                os.kill(pid, signal.SIGKILL)
            except Exception:
                pass
        return "killed"
    return f"REFUSED (foreign cmd={cmd})"


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out = stage_out("a2_core_no_modules")
    out["arm"] = arm
    os.makedirs(RUN2, exist_ok=True)
    stub = os.path.join(SEAT, "conf", "pw", "r97b-nomodules.conf")
    with open(stub, "w") as f:
        f.write("# r97b: core config with NO context.modules section\n"
                "context.properties = {\n  core.daemon = true\n  core.name = pipewire-0\n}\n")
    out["stub_conf"] = stub.replace(SEAT, "$SEAT")
    e = dict(ENV)
    e["PIPEWIRE_RUNTIME_DIR"] = RUN2
    e["XDG_RUNTIME_DIR"] = RUN2
    e["PIPEWIRE_DEBUG"] = "2"
    e["WIREPLUMBER_DEBUG"] = "I"
    e["XDG_CONFIG_HOME"] = SEAT + "/conf/xdg-config"

    for n in range(reps):
        rep = {"rep": n, "legs": {}}
        # L1: the modules-less core alone
        r1 = run(["pipewire", "-c", stub], timeout=6.0, env=e)
        t1 = r1["stderr"] + r1["stdout"]
        open(os.path.join(SCR, f"a2_L1_rep{n}.log"), "w").write(t1)
        rep["legs"]["L1_core_alone"] = {
            "rc": r1["rc"], "timed_out": r1["timed_out"], "dur_s": r1["dur_s"],
            "chain": {c: (c in t1) for c in CHAIN}, "raw": t1[:900],
            "loadavg": loadavg()}

        # L2: same stub core, a real WirePlumber client on top
        p = subprocess.Popen(["pipewire", "-c", stub], env=e,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             start_new_session=True, text=True)
        time.sleep(1.5)
        r2 = run(["wireplumber", "-c", "wireplumber.conf", "-p", "main"],
                 timeout=8.0, env=e)
        t2 = r2["stderr"] + r2["stdout"]
        open(os.path.join(SCR, f"a2_L2_rep{n}.log"), "w").write(t2)
        rep["legs"]["L2_wp_on_stub_core"] = {
            "rc": r2["rc"], "timed_out": r2["timed_out"], "dur_s": r2["dur_s"],
            "chain": {c: (c in t2) for c in CHAIN}, "raw": t2[:1500],
            "loadavg": loadavg()}
        rep["stub_core_kill"] = guarded_kill(p.pid)
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        out["reps"].append(rep)
        time.sleep(0.5)

    for rep in out["reps"]:
        for k, L in rep["legs"].items():
            print(f"--- rep {rep['rep']} {k} rc={L['rc']} timed={L['timed_out']} "
                  f"chain={[c[:30] for c, x in L['chain'].items() if x]}")
    stage_write(out, "a2_core_no_modules.json")


if __name__ == "__main__":
    main()
