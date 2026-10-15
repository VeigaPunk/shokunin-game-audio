#!/usr/bin/env python3
"""r96-scout teardown + exit census. Unloads seat modules by exact id, kills
seat processes by /proc cmdline scan (never by name pattern that can match the
caller), then verifies the graph is clean and records the state left behind.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r96s_lib as L  # noqa: E402

ROOT = L.ROOT
SEAT = L.SEAT_SINK_NAME
SEAT2 = L.SEAT_SINK2_NAME


def seat_procs():
    me = {os.getpid(), os.getppid()}
    out = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit() or int(pid) in me:
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                cmd = fh.read().replace(b"\x00", b" ").decode("utf-8", "replace")
        except OSError:
            continue
        if "r96s" in cmd and any(b in cmd for b in ("r96pulse", "pw-record", "parec", "paplay", "pacat", "pw-play", "pactl", "python3 probes/")):
            out.append((int(pid), cmd[:200]))
    return out


def main():
    census = {"stage": "exit", "ts": time.time()}
    # 1. processes
    procs = seat_procs()
    census["seat_procs_before"] = procs
    for pid, _ in procs:
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    time.sleep(0.5)
    census["seat_procs_after"] = seat_procs()
    # 2. modules: unload seat modules by exact id, name-checked
    # JSON short form carries no index; parse the text short form (index name args)
    mods_txt = L.run_bounded(["pactl", "list", "modules", "short"], env=L.base_env(), timeout=8)["stdout"]
    seat_mods = []
    for line in mods_txt.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and (SEAT in parts[2] or SEAT2 in parts[2]):
            seat_mods.append({"index": parts[0], "name": parts[1], "args": parts[2][:120]})
    census["seat_modules"] = seat_mods
    for m in seat_mods:
        if m["name"] == "module-null-sink" and (SEAT in m["args"] or SEAT2 in m["args"]):
            r = L.run_bounded(["pactl", "unload-module", str(m["index"])], env=L.base_env(), timeout=8)
            census.setdefault("unload", []).append({"index": m["index"], "rc": r["rc"], "stderr": r["stderr"][:200]})
    time.sleep(0.3)
    # 3. census
    census["sinks_r96s"] = [s for s in (L.pactl_json(["list", "sinks", "short"])[0] or []) if SEAT in s.get("name", "")]
    census["sources_r96s"] = [s for s in (L.pactl_json(["list", "sources", "short"])[0] or []) if SEAT in s.get("name", "")]
    census["modules_r96s"] = [ln for ln in
                              L.run_bounded(["pactl", "list", "modules", "short"], env=L.base_env(), timeout=8)["stdout"].splitlines()
                              if SEAT in ln or SEAT2 in ln]
    census["default_sink"] = L.run_bounded(["pactl", "get-default-sink"], env=L.base_env(), timeout=5)["stdout"].strip()
    census["default_source"] = L.run_bounded(["pactl", "get-default-source"], env=L.base_env(), timeout=5)["stdout"].strip()
    census["info"] = L.run_bounded(["pactl", "info"], env=L.base_env(), timeout=5)["stdout"][:800]
    # pw-dump r96s
    r = L.run_bounded(["pw-dump"], timeout=10, out_cap=8_000_000)
    nodes = []
    try:
        for o in json.loads(r["stdout"]):
            props = (o.get("info", {}) or {}).get("props", {}) or {}
            if str(props.get("node.name", "")).startswith("r96s") or str(props.get("application.name", "")).startswith("r96s"):
                nodes.append({"id": o.get("id"), "type": o.get("type"), "node.name": props.get("node.name")})
    except json.JSONDecodeError:
        nodes = ["pw-dump parse error"]
    census["pw_dump_r96s"] = nodes
    # metadata keys (settings)
    md = L.run_bounded(["pw-metadata", "-n", "settings"], timeout=6)["stdout"]
    census["settings_metadata_keys"] = [ln for ln in md.splitlines() if "force-quantum" in ln or "force-rate" in ln or "clock.quantum" in ln]
    # stream-properties rows (disclosure; r90 class: no CLI delete)
    path = os.path.expanduser("~/.local/state/wireplumber/stream-properties")
    try:
        with open(path, errors="replace") as fh:
            lines = fh.read().splitlines()
        census["stream_properties_total_rows"] = len(lines)
        census["stream_properties_r96s_rows"] = [ln[:160] for ln in lines if "r96s" in ln]
    except OSError as exc:
        census["stream_properties_error"] = str(exc)
    path2 = os.path.join(ROOT, "receipts", "r96s_census.json")
    with open(path2, "w") as fh:
        json.dump(census, fh, indent=1, sort_keys=True)
    print(json.dumps(census, indent=1)[:3000])
    print("wrote", path2)


if __name__ == "__main__":
    main()
