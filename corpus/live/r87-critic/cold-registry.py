#!/usr/bin/env python3
"""r87-critic cold-registry probe (dispatcher fallback).

The frozen probeParent dispatched exactly one read-only `labrat`; its
substrate exposed no command-execution tool, so it returned STILL NO
EXEC. That unavailability is recorded as unavailability, not absence.
This script runs the SAME bounded read-only battery directly.

READ-ONLY verbs only: `pw-cli info`, `pw-cli --version`, `pw-dump`,
`pactl list sinks short`, `pactl get-default-sink`. No graph mutation.

Hypothesis H1: on a LIVE global id, `pw-cli info <id>` (argv) succeeds
while `printf 'info <id>\\n' | pw-cli` (stdin at t=0) reports
`unknown global '<id>'`.
"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def run(argv, stdin_text=None, timeout=15):
    try:
        p = subprocess.run(argv, input=(stdin_text.encode()
                                        if stdin_text is not None else None),
                           capture_output=True, timeout=timeout)
        return {"argv": " ".join(argv),
                "stdin": stdin_text,
                "rc": p.returncode,
                "stdout": p.stdout.decode(errors="replace")[:900],
                "stderr": p.stderr.decode(errors="replace")[:900]}
    except subprocess.TimeoutExpired:
        return {"argv": " ".join(argv), "stdin": stdin_text, "rc": "TIMEOUT",
                "stdout": "", "stderr": ""}
    except Exception as ex:
        return {"argv": " ".join(argv), "stdin": stdin_text, "rc": None,
                "error": str(ex)[:200]}


def main():
    out = {"loadavg": open("/proc/loadavg").read().strip(),
           "pw_cli_version": run(["pw-cli", "--version"]),
           "which": subprocess.run(["bash", "-lc", "which -a pw-cli"],
                                   capture_output=True).stdout.decode().strip()}

    ds = subprocess.run(["pactl", "get-default-sink"],
                        capture_output=True).stdout.decode().strip()
    out["default_sink"] = ds
    short = subprocess.run(["pactl", "list", "sinks", "short"],
                           capture_output=True).stdout.decode()
    out["sinks_short"] = short
    serial = None
    for ln in short.splitlines():
        f = ln.split("\t")
        if f and f[0].strip().isdigit() and ds and f[1].strip() == ds:
            serial = f[0].strip()
            break
    out["default_sink_serial"] = serial

    # the GLOBAL id (not the pactl index/serial) — from pw-dump
    dump = subprocess.run(["pw-dump"], capture_output=True)
    live_id, gid_kind = None, None
    try:
        for o in json.loads(dump.stdout.decode(errors="replace")):
            props = ((o.get("info") or {}).get("props") or {})
            if props.get("node.name") == ds:
                live_id = str(o.get("id"))
                gid_kind = o.get("type")
                break
    except Exception as ex:
        out["dump_error"] = str(ex)[:200]
    out["live_id_chosen"] = live_id
    out["live_id_kind"] = gid_kind
    out["live_id_is_not_serial"] = (live_id != serial)

    probes = {}
    if live_id:
        probes["argv_live"] = run(["pw-cli", "info", live_id])
        probes["stdin_live"] = run(["pw-cli"],
                                   stdin_text=f"info {live_id}\nquit\n")
        probes["stdin_live_2nd"] = run(["pw-cli"],
                                       stdin_text=f"info {live_id}\nquit\n")
    probes["argv_bogus"] = run(["pw-cli", "info", "99999999"])
    probes["stdin_bogus"] = run(["pw-cli"],
                                stdin_text="info 99999999\nquit\n")
    probes["argv_serial"] = run(["pw-cli", "info", serial]) if serial else {}
    out["probes"] = probes

    # verdict
    def blob(d):
        return (d.get("stdout") or "") + (d.get("stderr") or "")

    v = {}
    if live_id:
        av = probes["argv_live"]
        sv = probes["stdin_live"]
        v["argv_live_unknown_global"] = f"unknown global '{live_id}'" in blob(av)
        v["argv_live_rc"] = av.get("rc")
        v["stdin_live_unknown_global"] = f"unknown global '{live_id}'" in blob(sv)
        v["stdin_live_rc"] = sv.get("rc")
        v["argv_live_has_object"] = "Object:" in blob(av) or "id:" in blob(av)
        v["stdin_live_has_object"] = "Object:" in blob(sv) or "id:" in blob(sv)
        same = (v["argv_live_unknown_global"] == v["stdin_live_unknown_global"])
        v["H1"] = (not v["argv_live_unknown_global"]) and \
                  v["stdin_live_unknown_global"]
        v["falsified"] = same
        v["verdict"] = ("CONFIRMED" if v["H1"] else
                        "FALSIFIED" if same else "OTHER")
    v["bogus_argv_unknown"] = "unknown global '99999999'" in blob(
        probes["argv_bogus"])
    v["bogus_stdin_unknown"] = "unknown global '99999999'" in blob(
        probes["stdin_bogus"])
    out["verdict"] = v

    json.dump(out, open(os.path.join(HERE, "cold-registry.json"), "w"),
              indent=1, sort_keys=True)

    lines = [f"loadavg: {out['loadavg']}",
             f"pw-cli: {out['which']}  version rc={out['pw_cli_version']['rc']}",
             f"default sink: {ds!r}  live id chosen: {live_id}",
             ""]
    for k, d in probes.items():
        lines.append(f"[{k}] argv={d['argv']} stdin={d.get('stdin')!r} "
                     f"rc={d.get('rc')}")
        lines.append(f"    stdout: {(d.get('stdout') or '').strip()[:220]!r}")
        lines.append(f"    stderr: {(d.get('stderr') or '').strip()[:220]!r}")
    lines.append("")
    lines.append(f"VERDICT: {v.get('verdict')}")
    for k, val in v.items():
        lines.append(f"   {k} = {val}")
    txt = "\n".join(lines) + "\n"
    open(os.path.join(HERE, "cold-registry.out"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
