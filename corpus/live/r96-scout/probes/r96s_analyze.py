#!/usr/bin/env python3
"""r96-scout analysis — buffer-attr law check + receipt summaries.

The server-side law is implemented from the version-matched source
(pipewire-1.6.8 module-protocol-pulse: pulse-server.c fix_playback_buffer_attr
:434-525, constants :60-65, clamp_latency :427-432) and checked against every
measured `pulse.attr.*` row. Stdlib only.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = "r96s"

# source constants (pulse-server.c:60-65, :5567)
MIN_REQ = (256, 48000)
DEFAULT_REQ = (960, 48000)
DEFAULT_TLENGTH = (96000, 48000)
MIN_QUANTUM = (256, 48000)
QUANTUM_LIMIT = 8192
MAXLENGTH = 4 * 1024 * 1024


def frac_bytes(num, denom, rate, frame):
    """frac_to_bytes_round_up: bytes, rounded up to a whole frame."""
    b = (num * rate * frame + denom - 1) // denom
    return ((b + frame - 1) // frame) * frame


def rdown(v, frame):
    return (v // frame) * frame


def fix_playback(tlength, minreq, prebuf, frame, rate, adjust):
    """Transcription of fix_playback_buffer_attr + clamp_latency."""
    maxlength = rdown(MAXLENGTH, frame)
    minreq_floor = frac_bytes(*MIN_REQ, rate, frame)
    max_latency = QUANTUM_LIMIT * frame
    if tlength == -1:
        tlength = frac_bytes(*DEFAULT_TLENGTH, rate, frame)
    tlength = max(minreq_floor, min(tlength, maxlength))
    tlength = ((tlength + frame - 1) // frame) * frame
    if minreq == -1:
        process = frac_bytes(*DEFAULT_REQ, rate, frame)
        m = rdown(tlength // 4, frame)
        minreq = min(process, m)
    minreq = max(minreq, minreq_floor)
    if tlength < minreq + frame:
        tlength = min(minreq + frame, maxlength)
    if adjust:
        latency = min(max_latency, (tlength - minreq * 2) // 2) if tlength > minreq * 2 else minreq
        latency = rdown(latency, frame)
        if tlength >= latency:
            tlength -= latency
    else:
        latency = min(max_latency, tlength - minreq * 2) if tlength > minreq * 2 else minreq
    if tlength < latency + 2 * minreq:
        tlength = min(latency + 2 * minreq, maxlength)
    minreq = rdown(minreq, frame)
    if minreq <= 0:
        minreq = frame
        tlength += frame * 2
    if tlength <= minreq:
        tlength = min(minreq * 2 + frame, maxlength)
    max_prebuf = tlength + frame - minreq
    if prebuf == -1 or prebuf > max_prebuf:
        prebuf = max_prebuf
    prebuf = rdown(prebuf, frame)
    lat_frames = latency // frame
    if lat_frames * MIN_QUANTUM[1] // rate < MIN_QUANTUM[0]:
        lat_frames = (MIN_QUANTUM[0] * rate + rate - 1) // rate
    return {"tlength": tlength, "minreq": minreq, "prebuf": prebuf, "lat_frames": lat_frames}


def us_to_bytes(usec, rate, frame):
    return (usec * rate * frame) // 1000000


def rows_from_receipt(path):
    """Yield (leg, rep, measured dict) for every seat stream row in a receipt."""
    with open(path) as fh:
        data = json.load(fh)
    rec = data.get("receipts", {})
    bodies = []
    for leg, body in rec.items():
        if isinstance(body, dict) and "results" in body:
            bodies.append((leg, body))
        elif isinstance(body, dict):  # nested group (e.g. d_matrix)
            for sub, subbody in body.items():
                if isinstance(subbody, dict) and "results" in subbody:
                    bodies.append((f"{leg}.{sub}", subbody))
    for leg, body in bodies:
        for r in body["results"]:
            for s in r.get("my_streams", []):
                p = s.get("props", {})
                yield leg, r.get("rep"), {
                    "tlength": int(p["pulse.attr.tlength"]) if p.get("pulse.attr.tlength") else None,
                    "prebuf": int(p["pulse.attr.prebuf"]) if p.get("pulse.attr.prebuf") else None,
                    "minreq": int(p["pulse.attr.minreq"]) if p.get("pulse.attr.minreq") else None,
                    "node_latency": p.get("node.latency"),
                }


def main():
    out = []
    cli_lat = os.path.join(ROOT, "receipts", "r96s_cli_latency.json")
    cases = []
    with open(cli_lat) as fh:
        data = json.load(fh)["receipts"]
    flat = {}
    for leg, body in data.items():
        if isinstance(body, dict) and "results" in body:
            flat[leg] = body
        elif isinstance(body, dict):
            for sub, subbody in body.items():
                if isinstance(subbody, dict) and "results" in subbody:
                    flat[f"{leg}.{sub}"] = subbody
    for leg, rep, m in rows_from_receipt(cli_lat):
        if m["tlength"] is None or leg not in flat:
            continue
        body = flat[leg]["results"][rep]
        env = body.get("env_extra", {})
        argv = body["argv"]
        frame = 4 if ("--channels=2" in argv or "--format=f32le" in argv) else 2
        t_req, mr_req, pb_req, adjust = -1, -1, -1, False
        if "PULSE_LATENCY_MSEC" in env and env["PULSE_LATENCY_MSEC"].isdigit() and int(env["PULSE_LATENCY_MSEC"]) > 0:
            t_req = us_to_bytes(int(env["PULSE_LATENCY_MSEC"]) * 1000, 48000, frame)
            adjust = True
        else:
            for a in argv:
                if a.startswith("--latency-msec="):
                    t_req = us_to_bytes(int(a.split("=")[1]) * 1000, 48000, frame)
                    adjust = True
                elif a.startswith("--latency="):
                    t_req = int(a.split("=")[1])
                    adjust = True
                elif a.startswith("--process-time-msec="):
                    mr_req = us_to_bytes(int(a.split("=")[1]) * 1000, 48000, frame)
                elif a.startswith("--process-time="):
                    mr_req = int(a.split("=")[1])
        pred = fix_playback(t_req, mr_req, pb_req, frame, 48000, adjust)
        ok = (pred["tlength"] == m["tlength"] and pred["prebuf"] == m["prebuf"]
              and pred["minreq"] == m["minreq"] and m["node_latency"] == f"{pred['lat_frames']}/48000")
        cases.append((leg, rep, frame, m, pred, ok))
    n_ok = sum(1 for c in cases if c[5])
    out.append(f"# buffer-attr law check — {n_ok}/{len(cases)} rows exact (frame_size-aware)")
    out.append("leg | rep | frame | measured(tlength/prebuf/minreq/latency) | predicted | ok")
    for leg, rep, frame, m, pred, ok in cases:
        out.append(f"{leg} | {rep} | {frame} | {m['tlength']}/{m['prebuf']}/{m['minreq']}/{m['node_latency']} | "
                   f"{pred['tlength']}/{pred['prebuf']}/{pred['minreq']}/{pred['lat_frames']}/48000 | {ok}")
    text = "\n".join(out) + "\n"
    with open(os.path.join(ROOT, "runs", "analysis-bufferattr.txt"), "w") as fh:
        fh.write(text)
    print(text)


if __name__ == "__main__":
    main()
