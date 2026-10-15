#!/usr/bin/env python3
"""r96-scout shared helpers: bounded subprocess legs + pulse introspection + receipts.

No repo fixtures are read or imported. Stdlib only.
"""
from __future__ import annotations

import json
import os
import resource
import signal
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # corpus/live/r96-scout
NS = "r96s"
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
    env = {k: v for k, v in os.environ.items() if k not in PULSE_ENV_KEYS}
    return env


def _limits():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


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


def seat_sink_index(env=None):
    sinks, _ = pactl_json(["list", "sinks", "short"], env=env)
    for s in sinks or []:
        if s.get("name") == SEAT_SINK_NAME:
            return s.get("index")
    return None


def seat_sink_index2(env=None):
    sinks, _ = pactl_json(["list", "sinks", "short"], env=env)
    for s in sinks or []:
        if s.get("name") == SEAT_SINK2_NAME:
            return s.get("index")
    return None


def seat_monitor_index(env=None):
    srcs, _ = pactl_json(["list", "sources", "short"], env=env)
    for s in srcs or []:
        if s.get("name") == SEAT_SINK_NAME + ".monitor":
            return s.get("index")
    return None


def seat_streams(kind="sink-inputs", env=None, index_key=None):
    """Pulse streams belonging to the seat null sink (sink-inputs: sink==idx; source-outputs: source==idx)."""
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
                    )
                    if k in props
                },
            }
        )
    return slim, {"sink_index": want}


def pw_dump_seat(timeout=8.0):
    """pw-dump filtered to seat stream nodes (node.name r96s* / target r96s_ns) - slim."""
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
        name = props.get("node.name", "")
        if not (name.startswith(NS) or props.get("target.object") == SEAT_SINK_NAME):
            continue
        rows.append(
            {
                "id": obj.get("id"),
                "type": obj.get("type"),
                "node.name": name,
                "node.latency": props.get("node.latency"),
                "node.rate": props.get("node.rate"),
                "media.class": props.get("media.class"),
                "pulse.attr.prebuf": props.get("pulse.attr.prebuf"),
                "pulse.attr.tlength": props.get("pulse.attr.tlength"),
                "pulse.attr.minreq": props.get("pulse.attr.minreq"),
                "state": (info.get("state") or ""),
            }
        )
    return rows, {}


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
