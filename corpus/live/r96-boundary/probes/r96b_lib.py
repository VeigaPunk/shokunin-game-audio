#!/usr/bin/env python3
"""r96-boundary shared helpers (seat BOUNDARY, namespace r96b).

Adapted from the r96 scout's r96s_lib.py (same bounded-leg discipline):
wall cap + process-group kill + byte caps, stdlib only, no repo fixture reads.
Seat objects only: r96b_*. Kill only own recorded PIDs.
"""
from __future__ import annotations

import json
import os
import resource
import signal
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # corpus/live/r96-boundary
NS = "r96b"
SEAT_SINK_NAME = f"{NS}_ns"
SEAT_SINK2_NAME = f"{NS}_ns2"
PULSE_ENV_KEYS = (
    "PULSE_SERVER",
    "PULSE_SINK",
    "PULSE_SOURCE",
    "PULSE_LATENCY_MSEC",
    "PULSE_PROP",
    "PULSE_PROP_OVERRIDE",
    "PULSE_COOKIE",
    "PULSE_RUNTIME_PATH",
    "PULSE_CLIENTCONFIG",
    "PULSE_CONFIG_PATH",
    "PULSE_STATE_PATH",
    "PULSE_LOG",
    "PULSE_LOG_SYSLOG",
    "PULSE_LOG_COLORS",
    "PULSE_LOG_META",
)


def base_env() -> dict:
    """Environment with every PULSE_* key stripped (legs add their own)."""
    return {k: v for k, v in os.environ.items() if k not in PULSE_ENV_KEYS}


def _limits():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def loadavg() -> dict:
    a, b, c = os.getloadavg()
    return {"l1": round(a, 2), "l5": round(b, 2), "l15": round(c, 2), "nproc": os.cpu_count()}


def run_bounded(argv, env=None, timeout=8.0, stdin_bytes=None, cwd=None, out_cap=65536):
    """Run argv with a wall cap and process-group kill; byte caps on both streams."""
    t0 = time.monotonic()
    proc = subprocess.Popen(
        argv,
        env=env,
        cwd=cwd,
        stdin=subprocess.PIPE if stdin_bytes is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        preexec_fn=_limits,
    )
    timed_out = False
    try:
        out, err = proc.communicate(input=stdin_bytes, timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
    wall = time.monotonic() - t0
    return {
        "argv": argv,
        "rc": proc.returncode,
        "timed_out": timed_out,
        "wall_s": round(wall, 4),
        "stdout": out[:out_cap].decode("utf-8", "replace"),
        "stderr": err[:out_cap].decode("utf-8", "replace"),
        "stdout_bytes": len(out),
        "stderr_bytes": len(err),
        "loadavg": loadavg(),
    }


def pactl_json(args, env=None, timeout=8.0):
    """pactl -f json <args> -> parsed JSON (or None with error text)."""
    r = run_bounded(["pactl", "-f", "json"] + args, env=env or base_env(), timeout=timeout)
    if r["rc"] != 0:
        return None, r
    try:
        return json.loads(r["stdout"]), r
    except json.JSONDecodeError as exc:  # pragma: no cover
        return None, {**r, "json_error": str(exc)}


def _find_name(kind, name):
    rows, _ = pactl_json(["list", kind, "short"])
    for s in rows or []:
        if s.get("name") == name:
            return s.get("index")
    return None


def seat_sink_index(env=None):
    return _find_name("sinks", SEAT_SINK_NAME)


def seat_sink_index2(env=None):
    return _find_name("sinks", SEAT_SINK2_NAME)


def seat_monitor_index(env=None):
    return _find_name("sources", SEAT_SINK_NAME + ".monitor")


def seat_streams(kind="sink-inputs", env=None):
    """Pulse streams belonging to the seat null sink."""
    if kind == "sink-inputs":
        want = seat_sink_index(env)
        idx_key = "sink"
    else:
        want = seat_monitor_index(env)
        idx_key = "source"
    rows, r = pactl_json(["list", kind], env=env)
    if rows is None:
        return [], {"error": r["stderr"][:400], "rc": r["rc"]}
    mine = [row for row in rows if row.get(idx_key) == want]
    slim = []
    for row in mine:
        props = row.get("properties", {})
        slim.append(
            {
                "index": row.get("index"),
                idx_key: row.get(idx_key),
                "corked": row.get("corked"),
                "mute": row.get("mute"),
                "sample_specification": row.get("sample_specification"),
                "buffer_latency_usec": row.get("buffer_latency_usec"),
                "sink_latency_usec": row.get("sink_latency_usec"),
                "source_latency_usec": row.get("source_latency_usec"),
                "props_subset": {
                    k: props.get(k)
                    for k in (
                        "pulse.corked",
                        "pulse.attr.tlength",
                        "pulse.attr.prebuf",
                        "pulse.attr.minreq",
                        "pulse.attr.maxlength",
                        "node.latency",
                        "node.rate",
                        "media.role",
                        "application.name",
                        "media.name",
                        "zzz.invented",
                        "state.restore-props",
                        "target.object",
                        "client.api",
                    )
                    if k in props
                },
            }
        )
    return slim, {"sink_index": want}


def ensure_sink(name=SEAT_SINK_NAME, rate=48000, channels=1):
    """Create the seat null sink if absent; record module id (namespace-checked)."""
    idx = _find_name("sinks", name)
    if idx is not None:
        return {"created": False, "index": idx, "module_id": None}
    r = run_bounded(
        ["pactl", "load-module", "module-null-sink", f"sink_name={name}", f"rate={rate}",
         f"channels={channels}", "sink_properties=state.restore-props=false"],
        env=base_env(), timeout=8)
    rec = {"created": True, "module_id": r["stdout"].strip(), "rc": r["rc"], "stderr": r["stderr"][:300]}
    path = os.path.join(ROOT, "scratch", "sinks.json")
    data = []
    if os.path.exists(path):
        try:
            with open(path) as fh:
                data = json.load(fh)
        except json.JSONDecodeError:
            data = []
    data.append({"name": name, "module_id": rec["module_id"]})
    with open(path, "w") as fh:
        json.dump(data, fh, indent=1)
    rec["index"] = _find_name("sinks", name)
    return rec


def unload_seat_sink(name=SEAT_SINK_NAME):
    """Unload only a module whose args contain `name` AND whose module is a null sink."""
    mods_txt = run_bounded(["pactl", "list", "modules", "short"], env=base_env(), timeout=8)["stdout"]
    out = []
    for line in mods_txt.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[1] == "module-null-sink" and name in parts[2]:
            r = run_bounded(["pactl", "unload-module", parts[0]], env=base_env(), timeout=8)
            out.append({"index": parts[0], "args": parts[2][:120], "rc": r["rc"], "stderr": r["stderr"][:200]})
    return out


def pw_dump_filtered(prefixes, timeout=12.0):
    """pw-dump rows whose node.name/application.name starts with any prefix."""
    r = run_bounded(["pw-dump"], timeout=timeout, out_cap=8_000_000)
    if r["rc"] != 0:
        return [], {"error": r["stderr"][:300]}
    try:
        dump = json.loads(r["stdout"])
    except json.JSONDecodeError as exc:
        return [], {"error": str(exc)}
    rows = []
    for obj in dump:
        info = obj.get("info", {}) or {}
        props = info.get("props", {}) or {}
        name = str(props.get("node.name", ""))
        app = str(props.get("application.name", ""))
        if not any(name.startswith(p) or app.startswith(p) for p in prefixes):
            continue
        rows.append(
            {
                "id": obj.get("id"),
                "type": obj.get("type"),
                "node.name": name,
                "application.name": app,
                "application.process.id": props.get("application.process.id"),
                "node.latency": props.get("node.latency"),
                "node.rate": props.get("node.rate"),
                "node.quantum": props.get("node.quantum"),
                "media.class": props.get("media.class"),
                "pulse.corked": props.get("pulse.corked"),
                "pulse.attr.prebuf": props.get("pulse.attr.prebuf"),
                "pulse.attr.tlength": props.get("pulse.attr.tlength"),
                "pulse.attr.minreq": props.get("pulse.attr.minreq"),
                "target.object": props.get("target.object"),
                "state": (info.get("state") or ""),
            }
        )
    return rows, {}


def pw_metadata(object_name, timeout=6.0):
    r = run_bounded(["pw-metadata", "-n", object_name], timeout=timeout)
    return r


def settings_meta() -> dict:
    r = pw_metadata("settings")
    keys = {}
    for line in r["stdout"].splitlines():
        if "key:'" in line and "value:'" in line:
            k = line.split("key:'", 1)[1].split("'", 1)[0]
            v = line.split("value:'", 1)[1].split("'", 1)[0]
            keys[k] = v
    return keys


def default_meta() -> dict:
    r = pw_metadata("default")
    keys = {}
    for line in r["stdout"].splitlines():
        if "key:'" in line and "value:'" in line:
            k = line.split("key:'", 1)[1].split("'", 1)[0]
            v = line.split("value:'", 1)[1].split("'", 1)[0]
            keys[k] = v
    return keys


def restore_rows(tag=NS):
    path = os.path.expanduser("~/.local/state/wireplumber/stream-properties")
    try:
        with open(path, "r", errors="replace") as fh:
            data = fh.read()
    except OSError:
        return {"path": path, "exists": False}
    lines = data.splitlines()
    mine = [ln for ln in lines if tag in ln]
    return {"path": path, "exists": True, "total_rows": len(lines), "tag_rows": len(mine), "sample": mine[:6]}


def write_receipt(name, payload):
    os.makedirs(os.path.join(ROOT, "receipts"), exist_ok=True)
    path = os.path.join(ROOT, "receipts", name)
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
    return path


def log_line(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as fh:
        fh.write(text.rstrip("\n") + "\n")
