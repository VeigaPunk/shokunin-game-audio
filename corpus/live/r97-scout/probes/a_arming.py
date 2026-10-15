#!/usr/bin/env python3
"""r97-scout stage A — the arming law: how a PRIVATE WirePlumber 0.5.17 gets
its configuration, and what each override actually replaces.

Each variant runs a bounded (5 s) short-lived `wireplumber` against this seat's
private PipeWire core and records the config-resolution log lines, the exit
status and whether the daemon reached "policy ready". The shared WirePlumber is
never touched: PIPEWIRE_RUNTIME_DIR points at corpus/live/r97-scout/run.
"""
import json, os, re, signal, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97lib import SEAT, ENV, run, ensure_up

REC = os.path.join(SEAT, "receipts")
CONF = os.path.join(SEAT, "conf")


def wp_leg(name, extra_env, cap=5.0, args=("-c", "wireplumber.conf", "-p", "main")):
    env = dict(ENV)
    env.update(extra_env)
    env["WIREPLUMBER_DEBUG"] = "I"
    t0 = time.monotonic()
    p = subprocess.Popen(["wireplumber", *args], env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, start_new_session=True, text=True)
    timed = False
    try:
        out, _ = p.communicate(timeout=cap)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, _ = p.communicate()
        timed = True
    lines = [l for l in out.splitlines() if re.search(
        r"lookup 'wireplumber.conf'|opening fragment file|using configuration file|"
        r"no modules loaded|Failed to connect|policy|Error|error", l)]
    return {"variant": name, "argv": ["wireplumber", *args], "rc": p.returncode,
            "timed_out": timed, "dur_s": round(time.monotonic() - t0, 2),
            "env_overrides": {k: v for k, v in extra_env.items()},
            "lines": lines, "raw_len": len(out)}


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    ensure_up()
    # prepare the "no conf here" dir and the "conf copied here" dir
    empty_dir = os.path.join(CONF, "wp-empty")
    copy_dir = os.path.join(CONF, "wp-copy")
    os.makedirs(empty_dir, exist_ok=True)
    os.makedirs(os.path.join(copy_dir, "wireplumber.conf.d"), exist_ok=True)
    if not os.path.exists(os.path.join(copy_dir, "wireplumber.conf")):
        with open("/usr/share/wireplumber/wireplumber.conf") as f:
            conf = f.read()
        with open(os.path.join(copy_dir, "wireplumber.conf"), "w") as f:
            f.write(conf)
        with open("/usr/share/wireplumber/wireplumber.conf.d/alsa-vm.conf") as f:
            frag = f.read()
        with open(os.path.join(copy_dir, "wireplumber.conf.d", "alsa-vm.conf"), "w") as f:
            f.write(frag)

    variants = [
        ("V1_CONFIGDIR_without_conf",
         {"WIREPLUMBER_CONFIG_DIR": empty_dir}, {}),
        ("V2_CONFIGDIR_with_conf_copy",
         {"WIREPLUMBER_CONFIG_DIR": copy_dir}, {}),
        ("V3_private_XDG_CONFIG_HOME",
         {"XDG_CONFIG_HOME": os.path.join(CONF, "xdg-config")}, {}),
        ("V4_default_user_config",
         {}, {"drop": ["XDG_CONFIG_HOME"]}),
        ("V5_DATA_DIR_additive",
         {"XDG_CONFIG_HOME": os.path.join(CONF, "xdg-config-probe"),
          "WIREPLUMBER_DATA_DIR": os.path.join(CONF, "wpdata")}, {}),
    ]
    out = {"stage": "a_arming", "reps": []}
    for n in range(reps):
        rep = {"rep": n, "legs": []}
        for name, extra, opts in variants:
            env = dict(extra)
            if opts.get("drop"):
                for k in opts["drop"]:
                    env[k] = None
            if env and None in env.values():
                # run with those variables removed
                e = {k: v for k, v in extra.items() if v is not None}
                env = e
                rep["legs"].append(wp_leg_drop(name, env, opts["drop"]))
            else:
                rep["legs"].append(wp_leg(name, env))
        out["reps"].append(rep)
    os.makedirs(REC, exist_ok=True)
    json.dump(out, open(os.path.join(REC, "a_arming.json"), "w"), indent=1)
    for rep in out["reps"]:
        print(f"--- rep {rep['rep']}")
        for L in rep["legs"]:
            frags = [l.split("wp_conf_open: ")[-1].split("opening fragment file: ")[-1]
                     for l in L["lines"] if "opening fragment" in l]
            key = [l.split("] ")[-1] for l in L["lines"] if "lookup 'wireplumber.conf'" in l
                   or "no modules loaded" in l or "Failed to connect" in l or "using configuration" in l]
            print(f"  {L['variant']:<28} rc={L['rc']:<4} timed={L['timed_out']} frags={frags}")
            for k in key:
                print(f"      {k}")


def wp_leg_drop(name, env, drop):
    e = dict(ENV)
    e.update(env)
    for k in drop:
        e.pop(k, None)
    e["WIREPLUMBER_DEBUG"] = "I"
    t0 = time.monotonic()
    p = subprocess.Popen(["wireplumber", "-c", "wireplumber.conf", "-p", "main"],
                         env=e, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         start_new_session=True, text=True)
    timed = False
    try:
        o, _ = p.communicate(timeout=5.0)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        o, _ = p.communicate()
        timed = True
    lines = [l for l in o.splitlines() if re.search(
        r"lookup 'wireplumber.conf'|opening fragment file|using configuration file|"
        r"no modules loaded|Failed to connect", l)]
    return {"variant": name, "rc": p.returncode, "timed_out": timed,
            "dur_s": round(time.monotonic() - t0, 2), "env_overrides": {"dropped": drop},
            "lines": lines, "raw_len": len(o)}


if __name__ == "__main__":
    main()
