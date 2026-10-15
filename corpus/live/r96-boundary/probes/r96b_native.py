#!/usr/bin/env python3
"""r96-boundary native-stream cells — re-measure the scout's claim 16
(`Corked:` for a native non-pulse stream is a node-state projection) and the
short-form client-name question (scout unknown #3).

native_idle : a starved but linked native `pw-play` stream (no `pulse.corked`)
              sampled for `Corked:` / node state / props.
client_short: a live pulse stream; `pactl list clients` full vs short name field
              vs the stream's application.name.

Usage: r96b_native.py GROUP TAG
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r96b_lib as L  # noqa: E402

ROOT = L.ROOT
SEAT = L.SEAT_SINK_NAME
TONE = os.path.join(ROOT, "scratch", "tone1k5.wav")


def native_idle():
    fifo = os.path.join(ROOT, "scratch", "r96b_fifo")
    if os.path.exists(fifo):
        os.unlink(fifo)
    os.mkfifo(fifo)
    # `--raw` avoids format sniffing (without it pw-play blocks before creating
    # the stream); O_RDWR keeps the fifo open with zero bytes ever written.
    p = subprocess.Popen(["pw-play", "--raw", "--rate", "48000", "--channels", "1", "--format", "s16",
                          "--target", SEAT, fifo], env=L.base_env(),
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                         start_new_session=True, preexec_fn=L._limits)
    time.sleep(0.4)
    wfd = os.open(fifo, os.O_RDWR)
    time.sleep(0.8)
    # native nodes carry no application.process.id in pw-dump props; select by
    # node.name + target.object instead (pactl cannot match them by pid).
    rows, _ = L.pactl_json(["list", "sink-inputs"])
    mine = [r for r in (rows or []) if r.get("properties", {}).get("target.object") == SEAT
            and r.get("properties", {}).get("application.name") == "pw-play"]
    nodes, _ = L.pw_dump_filtered(["pw-play"])
    nodes = [n for n in nodes if n.get("target.object") == SEAT and n.get("node.name") == "pw-play"]
    out = {"pid": p.pid, "rows": [], "nodes": nodes,
           "stderr": p.stderr.read().decode("utf-8", "replace")[:200] if p.poll() is not None else None,
           "pactl_native_visible": bool(mine)}
    for r in mine:
        props = r.get("properties", {})
        out["rows"].append({
            "index": r.get("index"), "corked": r.get("corked"),
            "state": r.get("state"),
            "props": {k: props.get(k) for k in
                      ("pulse.corked", "application.name", "node.name", "media.class", "client.api",
                       "target.object", "stream.is-live", "node.latency") if k in props},
        })
    # second sample after another second (still starved)
    time.sleep(1.0)
    rows2, _ = L.pactl_json(["list", "sink-inputs"])
    mine2 = [r for r in (rows2 or []) if r.get("properties", {}).get("target.object") == SEAT
             and r.get("properties", {}).get("application.name") == "pw-play"]
    out["rows_t1"] = [{"index": r.get("index"), "corked": r.get("corked"),
                       "pulse.corked": r.get("properties", {}).get("pulse.corked")} for r in mine2]
    os.close(wfd)
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    p.communicate()
    return out


def client_short():
    env = L.base_env(); env.update({"PULSE_SINK": SEAT})
    p = subprocess.Popen(["paplay", TONE, "--client-name=r96b_short"], env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                         start_new_session=True, preexec_fn=L._limits)
    time.sleep(0.5)
    full = L.run_bounded(["pactl", "-f", "json", "list", "clients"], timeout=6)
    out = {"pid": p.pid, "full_rows": [], "short": None}
    try:
        clients = json.loads(full["stdout"])
        for c in clients:
            props = c.get("properties", {})
            if str(props.get("application.process.id")) == str(p.pid):
                out["full_rows"].append({"index": c.get("index"), "name": c.get("name"),
                                         "application.name": props.get("application.name"),
                                         "client.api": props.get("client.api")})
    except json.JSONDecodeError:
        out["full_error"] = full["stdout"][:200]
    short = L.run_bounded(["pactl", "list", "clients", "short"], timeout=6)["stdout"]
    idx = out["full_rows"][0]["index"] if out["full_rows"] else None
    out["short_line"] = next((ln for ln in short.splitlines() if idx is not None and ln.startswith(f"{idx}\t")), None)
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    p.communicate()
    return out


GROUPS = {"native_idle": native_idle, "client_short": client_short}


def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "native_idle"
    tag = sys.argv[2] if len(sys.argv) > 2 else "adhoc"
    L.ensure_sink()
    rec = GROUPS[group]()
    payload = {"battery": "r96b_native", "group": group, "tag": tag, "loadavg": L.loadavg(), "receipt": rec}
    path = L.write_receipt(f"r96b_native_{group}_{tag}.json", payload)
    print("wrote", path)
    print(json.dumps(rec, indent=1)[:1500])


if __name__ == "__main__":
    main()
