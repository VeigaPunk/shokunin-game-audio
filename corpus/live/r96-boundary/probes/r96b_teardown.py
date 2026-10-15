#!/usr/bin/env python3
"""r96-boundary teardown + exit census.

- kills only PIDs recorded by this seat (scratch/hogs.json if present) and
  processes whose /proc cmdline contains this seat's probe path
  (`corpus/live/r96-boundary/probes/`) — never a namespace-blind name sweep;
- unloads only modules whose name is `module-null-sink` AND whose args contain
  `r96b_ns` (the exact id from the text short form is used);
- verifies zero r96b sinks/sources/modules/nodes and records the state left.
"""
from __future__ import annotations

import json
import os
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r96b_lib as L  # noqa: E402

ROOT = L.ROOT
SEAT = L.SEAT_SINK_NAME
SEAT2 = L.SEAT_SINK2_NAME
HOGS = os.path.join(ROOT, "scratch", "hogs.json")


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
        if "corpus/live/r96-boundary/probes/" in cmd:
            out.append({"pid": int(pid), "cmd": cmd[:200]})
    return out


def main():
    census = {"stage": "exit", "ts": time.time(), "loadavg": L.loadavg()}
    # 1. own hogs (recorded pids only)
    if os.path.exists(HOGS):
        with open(HOGS) as fh:
            rec = json.load(fh)
        for pid in rec.get("pids", []):
            try:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        census["hogs_killed"] = rec.get("pids")
        os.unlink(HOGS)
    # 2. own probe processes (cmdline path match)
    procs = seat_procs()
    census["seat_procs_before"] = procs
    for p in procs:
        try:
            os.killpg(os.getpgid(p["pid"]), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            try:
                os.kill(p["pid"], signal.SIGKILL)
            except ProcessLookupError:
                pass
    time.sleep(0.5)
    census["seat_procs_after"] = seat_procs()
    # 3. seat modules: unload by exact id, name-checked + arg-checked
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
    time.sleep(0.4)
    # 4. census
    census["sinks_r96b"] = [s for s in (L.pactl_json(["list", "sinks", "short"])[0] or []) if "r96b" in str(s.get("name", ""))]
    census["sources_r96b"] = [s for s in (L.pactl_json(["list", "sources", "short"])[0] or []) if "r96b" in str(s.get("name", ""))]
    census["modules_r96b"] = [ln for ln in L.run_bounded(["pactl", "list", "modules", "short"], env=L.base_env(), timeout=8)["stdout"].splitlines() if "r96b" in ln]
    census["default_sink"] = L.run_bounded(["pactl", "get-default-sink"], env=L.base_env(), timeout=5)["stdout"].strip()
    census["default_source"] = L.run_bounded(["pactl", "get-default-source"], env=L.base_env(), timeout=5)["stdout"].strip()
    census["settings_meta"] = L.settings_meta()
    census["default_meta"] = L.default_meta()
    nodes, _ = L.pw_dump_filtered(["r96b"])
    census["pw_nodes_r96b"] = [n for n in nodes if str(n.get("node.name", "")).startswith("r96b") or str(n.get("application.name", "")).startswith("r96b")]
    census["restore_rows"] = L.restore_rows()
    census["all_sinks"] = [s.get("name") for s in (L.pactl_json(["list", "sinks", "short"])[0] or [])]
    census["pactl_info"] = L.run_bounded(["pactl", "info"], timeout=6)["stdout"][:500]
    path = L.write_receipt("r96b_census_exit.json", census)
    print(json.dumps(census, indent=1)[:3500])
    print("wrote", path)


if __name__ == "__main__":
    main()
