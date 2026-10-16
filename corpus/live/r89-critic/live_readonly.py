#!/usr/bin/env python3
"""r89 critic: bounded READ-ONLY live corroboration.

Every command below is a read verb or a self-terminating refusal/version
leg: nothing is created, loaded, unloaded, linked, destroyed, and no
stream is spawned (a `pw-profiler -J -n N` stream would attach a Client
and could perturb a sibling wave-B seat's census/footprint legs, so the
profiler legs are limited to --version / --help / refusals, which exit
before connecting). All commands are bounded.
"""
import json
import re
import subprocess
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
res = {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "legs": {}}


def run(name, argv, timeout=15, env=None, parse=None):
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout,
                           env=env)
        rc, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        rc, so, se = None, exc.stdout or b"", exc.stderr or b""
        rc = "TIMEOUT"
    rec = {"argv": argv, "exit_code": rc,
           "stdout": so.decode(errors="replace")[:600],
           "stderr": se.decode(errors="replace")[:600],
           "stdout_bytes": len(so), "stderr_bytes": len(se),
           "wall_s": round(time.monotonic() - t0, 3)}
    if parse:
        rec.update(parse(so, se, rc))
    res["legs"][name] = rec
    return rec


run("version", ["pw-profiler", "--version"])
run("help", ["pw-profiler", "--help"], parse=lambda so, se, rc: {
    "mentions_n": "-n" in (so + se).decode(errors="replace"),
    "mentions_o": "-o" in (so + se).decode(errors="replace"),
    "mentions_J": "-J" in (so + se).decode(errors="replace"),
    "mentions_profiler_log": "profiler.log" in (so + se).decode(
        errors="replace")})
run("opt_bogus", ["pw-profiler", "--r89criticbogus"])
run("remote_bogus", ["pw-profiler", "-r", "r89a_bogus_remote_critic",
                     "-J", "-n", "2"])
run("profiler_obj", ["pw-cli", "info", "5"])
run("profiler_enum", ["pw-cli", "enum-params", "5", "Props"])


def dump_parse(so, se, rc):
    try:
        objs = json.loads(so or b"[]")
    except ValueError as exc:
        return {"parse_error": str(exc)}
    mods = sorted(str(o.get("id")) for o in objs
                  if str(o.get("type", "")).endswith("Module"))
    profs = [o.get("id") for o in objs
             if str(o.get("type", "")).endswith("Profiler")]
    clients = sorted(str(((o.get("info") or {}).get("props") or {})
                         .get("application.name"))
                     for o in objs
                     if str(o.get("type", "")).endswith("Client"))
    names = sorted(str(((o.get("info") or {}).get("props") or {})
                       .get("node.name"))
                   for o in objs
                   if str(o.get("type", "")).endswith("Node"))
    return {"objects": len(objs), "module_ids": mods,
            "module_count": len(mods), "profiler_ids": profs,
            "clients": clients,
            "pwprof_clients": clients.count("pw-profiler"),
            "pwplay_clients": clients.count("pw-play"),
            "r89_nodes": [n for n in names if "r89a" in n],
            "foreign_probe_nodes": [n for n in names
                                    if re.search(r"r8[0-8]", n)]}


run("pw_dump", ["pw-dump"], parse=dump_parse)


def pactl_parse(so, se, rc):
    txt = so.decode(errors="replace")
    lines = txt.splitlines()
    blank = [i + 1 for i, l in enumerate(lines) if not l.strip()]
    return {"lines": len(lines), "blank_lines": blank,
            "r89_modules": [l for l in lines if "r89a" in l],
            "r8_modules": [l for l in lines if re.search(r"r8[0-8]a_", l)]}


run("pactl_modules", ["pactl", "list", "modules", "short"],
    parse=pactl_parse)
run("pwtop", ["pw-top", "-b", "-n", "1"])


def ps_parse(so, se, rc):
    txt = so.decode(errors="replace")
    procs = [l for l in txt.splitlines()
             if re.search(r"measure_audio|pw-profiler|pw-play|pw-dump|"
                          r"pw-top|pw-cli|pactl", l)
             and "grep" not in l]
    return {"probe_processes": procs}


run("ps", ["ps", "-eo", "pid,etimes,args"], parse=ps_parse)
run("loadavg", ["cat", "/proc/loadavg"],
    parse=lambda so, se, rc: {"loadavg": so.decode().strip()})
run("locks", ["ls", "-la", "corpus/live/"],
    parse=lambda so, se, rc: {
        "lock_files": sorted(l.split()[-1] for l in
                             so.decode().splitlines() if ".lock" in l)})

res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
(OUT / "live-readonly.json").write_text(json.dumps(res, indent=2) + "\n")
for name, rec in res["legs"].items():
    print(f"--- {name}: rc={rec['exit_code']} wall={rec['wall_s']}")
    for k, v in rec.items():
        if k in ("argv", "wall_s"):
            continue
        print(f"      {k}: {str(v)[:180]}")
