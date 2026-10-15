#!/usr/bin/env python3
"""r96-boundary census — entry/exit state, foreign-object disclosure.

Read-only: pactl/pw-dump/pw-metadata/proc scan. Namespace guard: reports the
seat's own r96b_* objects; foreign rows are listed for the contention ledger
only and are never touched.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r96b_lib as L  # noqa: E402


def proc_scan(needle):
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
        if needle in cmd:
            out.append({"pid": int(pid), "cmd": cmd[:220]})
    return out


def census(stage):
    c = {"stage": stage, "ts": time.time(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         "loadavg": L.loadavg()}
    c["git_head"] = L.run_bounded(["git", "rev-parse", "--short", "HEAD"], cwd="/home/vgpnk/Projects/shokunin/audio-shokunin", timeout=6)["stdout"].strip()
    c["git_status_uno"] = L.run_bounded(["git", "status", "--porcelain", "-uno"], cwd="/home/vgpnk/Projects/shokunin/audio-shokunin", timeout=8)["stdout"][:2000]
    c["pactl_info"] = L.run_bounded(["pactl", "info"], timeout=6)["stdout"][:900]
    sinks, _ = L.pactl_json(["list", "sinks", "short"])
    srcs, _ = L.pactl_json(["list", "sources", "short"])
    c["sinks"] = sinks
    c["sources"] = srcs
    c["seat_sinks"] = [s for s in sinks or [] if "r96b" in str(s.get("name", ""))]
    c["seat_sources"] = [s for s in srcs or [] if "r96b" in str(s.get("name", ""))]
    mods_txt = L.run_bounded(["pactl", "list", "modules", "short"], timeout=8)["stdout"]
    c["modules_short"] = mods_txt.splitlines()
    c["seat_modules"] = [ln for ln in mods_txt.splitlines() if "r96b" in ln]
    c["foreign_modules_r9xb"] = [ln for ln in mods_txt.splitlines() if "r9" in ln and "r96b" not in ln]
    c["default_sink"] = L.run_bounded(["pactl", "get-default-sink"], timeout=5)["stdout"].strip()
    c["default_source"] = L.run_bounded(["pactl", "get-default-source"], timeout=5)["stdout"].strip()
    c["settings_meta"] = L.settings_meta()
    c["default_meta"] = L.default_meta()
    nodes, _ = L.pw_dump_filtered(["r96b", "r9"])
    c["pw_nodes_r96b"] = [n for n in nodes if str(n.get("node.name", "")).startswith("r96b") or str(n.get("application.name", "")).startswith("r96b")]
    c["pw_nodes_foreign_r9"] = [n for n in nodes if not (str(n.get("node.name", "")).startswith("r96b") or str(n.get("application.name", "")).startswith("r96b"))]
    c["restore_rows"] = L.restore_rows()
    c["procs_r96b"] = proc_scan("r96-boundary")
    c["procs_foreign_lanes"] = proc_scan("corpus/live/r9")
    c["hogs_alive"] = proc_scan("r96-boundary/scratch/hogs")
    return c


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "entry"
    c = census(stage)
    path = L.write_receipt(f"r96b_census_{stage}.json", c)
    print(json.dumps({k: (v if not isinstance(v, (list, dict)) else (len(v) if isinstance(v, list) else v)) for k, v in c.items()}, indent=1)[:2500])
    print("wrote", path)


if __name__ == "__main__":
    main()
