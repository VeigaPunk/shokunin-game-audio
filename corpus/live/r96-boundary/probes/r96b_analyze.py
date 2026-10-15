#!/usr/bin/env python3
"""r96-boundary analysis — law checks over the boundary receipts.

Same transcription of the pipewire-1.6.8 pulse-server buffer-attr law as the
r96 scout's r96s_analyze.py (constants :60-65, fix_playback_buffer_attr
:434-525, clamp_latency :427-432), applied to every measured row this seat
took (quiet + load + quantum/rate/order axes). Stdlib only.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(ROOT, "receipts")
RUNS = os.path.join(ROOT, "runs")

MIN_REQ = (256, 48000)
DEFAULT_REQ = (960, 48000)
DEFAULT_TLENGTH = (96000, 48000)
MIN_QUANTUM = (256, 48000)
QUANTUM_LIMIT = 8192
MAXLENGTH = 4 * 1024 * 1024


def frac_bytes(num, denom, rate, frame):
    b = (num * rate * frame + denom - 1) // denom
    return ((b + frame - 1) // frame) * frame


def rdown(v, frame):
    return (v // frame) * frame


def fix_playback(tlength, minreq, prebuf, frame, rate, adjust):
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


def pa_atou(v):
    """Transcription of PulseAudio v17.0 pa_atou: prepare_number_string
    (reject isspace/'+'/'-'; strip leading zeros unless the string starts with
    lowercase '0x') then strtoul base 0, full string, uint32 range."""
    if not v:
        return None
    if v[0].isspace() or v[0] == "+" or v[0] == "-":
        return None
    s = v
    if s[0] == "0" and (len(s) < 2 or s[1] != "x"):
        while len(s) > 1 and s[0] == "0":
            s = s[1:]
    m = re.match(r"^(0[xX][0-9a-fA-F]+|[0-9]+)$", s)
    if not m:
        return None
    val = int(s, 0) if s.lower().startswith("0x") else int(s, 10)
    if val > 0xFFFFFFFF:
        return None
    return val


def iter_legs(path):
    """Yield (leg, body, rep_result) from a receipt file (handles nested groups)."""
    with open(path) as fh:
        data = json.load(fh)
    rec = data.get("receipts", data.get("receipt", {}))
    if not isinstance(rec, dict):
        return
    for leg, body in rec.items():
        if isinstance(body, dict) and "results" in body:
            yield leg, body
        elif isinstance(body, dict):
            for sub, subbody in body.items():
                if isinstance(subbody, dict) and "results" in subbody:
                    yield f"{leg}.{sub}", subbody


def attr_rows():
    """(source, leg, rep, frame, measured, predicted, ok, extra) for every attr row."""
    rows = []
    for fname in sorted(os.listdir(REC)):
        if not fname.startswith(("r96b_cli_latency", "r96b_cli_extra", "r96b_axes_quantum", "r96b_axes_rate", "r96b_axes_order")):
            continue
        path = os.path.join(REC, fname)
        for leg, body in iter_legs(path):
            if "my_streams" not in json.dumps(body)[:2000] and not leg.startswith(("d_", "xq_", "xr_", "xo_", "z_", "w_")):
                continue
            for r in body["results"]:
                streams = r.get("my_streams", [])
                if not streams:
                    continue
                argv = r.get("argv", [])
                env = r.get("env_extra", {})
                frame = 2
                if "--channels=2" in argv or "--format=float32le" in argv or "--format=f32le" in argv:
                    frame = 4
                if "--format=s24le" in argv:
                    frame = 3
                t_req, mr_req, adjust = -1, -1, False
                env_ms = env.get("PULSE_LATENCY_MSEC")
                if env_ms is not None:
                    ms = pa_atou(env_ms)
                    if ms is not None and ms > 0:
                        t_req = us_to_bytes(ms * 1000, 48000, frame)
                        adjust = True
                if t_req == -1:
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
                pred = fix_playback(t_req, mr_req, -1, frame, 48000, adjust)
                for s in streams:
                    p = s.get("props", {})
                    try:
                        m = {"tlength": int(p["pulse.attr.tlength"]), "prebuf": int(p["pulse.attr.prebuf"]),
                             "minreq": int(p["pulse.attr.minreq"]), "node_latency": p.get("node.latency"),
                             "maxlength": int(p.get("pulse.attr.maxlength", -1))}
                    except (KeyError, TypeError, ValueError):
                        continue
                    ok = (m["tlength"] == pred["tlength"] and m["prebuf"] == pred["prebuf"]
                          and m["minreq"] == pred["minreq"] and m["node_latency"] == f"{pred['lat_frames']}/48000")
                    rows.append({"source": fname, "leg": leg, "rep": r.get("rep"), "frame": frame,
                                 "measured": m, "predicted": pred, "ok": ok,
                                 "loadavg": r.get("loadavg", {}).get("l1"), "env_ms": env_ms})
    return rows


def main():
    os.makedirs(RUNS, exist_ok=True)
    out = {}
    rows = attr_rows()
    n_ok = sum(1 for r in rows if r["ok"])
    lines = [f"# buffer-attr law check (boundary receipts) — {n_ok}/{len(rows)} rows exact",
             "source | leg | rep | frame | measured(tl/pb/mr/lat) | predicted | ok | load"]
    for r in rows:
        m, p = r["measured"], r["predicted"]
        lines.append(f"{r['source']} | {r['leg']} | {r['rep']} | {r['frame']} | "
                     f"{m['tlength']}/{m['prebuf']}/{m['minreq']}/{m['node_latency']} | "
                     f"{p['tlength']}/{p['prebuf']}/{p['minreq']}/{p['lat_frames']}/48000 | {r['ok']} | {r['loadavg']}")
    with open(os.path.join(RUNS, "analysis-bufferattr.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    out["buffer_attr"] = {"rows": len(rows), "exact": n_ok,
                          "by_source": {s: {"rows": sum(1 for r in rows if r["source"] == s),
                                            "ok": sum(1 for r in rows if r["source"] == s and r["ok"])}
                                        for s in sorted({r["source"] for r in rows})}}

    # server lattice
    srv = {}
    for fname in sorted(os.listdir(REC)):
        if not fname.startswith("r96b_cli_server"):
            continue
        tag = fname.split("_")[-1].replace(".json", "")
        for leg, body in iter_legs(os.path.join(REC, fname)):
            rs = [{"rc": r["rc"], "wall_s": r["wall_s"], "stderr": r["stderr"][:120], "timed_out": r["timed_out"]}
                  for r in body["results"]]
            srv.setdefault(leg, {})[tag] = rs
    with open(os.path.join(RUNS, "analysis-server.txt"), "w") as fh:
        for leg, tags in sorted(srv.items()):
            fh.write(f"{leg}\n")
            for tag, rs in tags.items():
                fh.write(f"  {tag}: " + "; ".join(f"rc={x['rc']} wall={x['wall_s']} {x['stderr'][:60]!r}" for x in rs) + "\n")
    out["server"] = {leg: {t: [x["rc"] for x in rs] for t, rs in tags.items()} for leg, tags in srv.items()}

    # target lattice
    tgt = {}
    for fname in sorted(os.listdir(REC)):
        if not fname.startswith("r96b_cli_target"):
            continue
        tag = fname.split("_")[-1].replace(".json", "")
        for leg, body in iter_legs(os.path.join(REC, fname)):
            landings = []
            for r in body["results"]:
                for s in r.get("my_streams", []):
                    landings.append({"rc": r["rc"], "sink_name": s.get("sink_name"), "source_name": s.get("source_name"),
                                     "target.object": s.get("props", {}).get("target.object"),
                                     "stderr": r["stderr"][:90]})
                if not r.get("my_streams"):
                    landings.append({"rc": r["rc"], "landed": None, "stderr": r["stderr"][:90]})
            tgt.setdefault(leg, {})[tag] = landings
    with open(os.path.join(RUNS, "analysis-target.txt"), "w") as fh:
        for leg, tags in sorted(tgt.items()):
            fh.write(f"{leg}\n")
            for tag, ls in tags.items():
                fh.write(f"  {tag}: " + "; ".join(f"rc={x['rc']} sink={x.get('sink_name')} src={x.get('source_name')} "
                                                  f"target={x.get('target.object')} {x.get('stderr','')[:40]!r}" for x in ls) + "\n")
    out["target"] = {leg: {t: [(x["rc"], x.get("sink_name") or x.get("source_name"), x.get("target.object")) for x in ls]
                           for t, ls in tags.items()} for leg, tags in tgt.items()}

    # cork/trigger/record
    cork = {}
    for fname in sorted(os.listdir(REC)):
        if not fname.startswith("r96b_cork_"):
            continue
        tag = fname.split("_")[-1].replace(".json", "")
        for leg, body in iter_legs(os.path.join(REC, fname)):
            for r in body["results"]:
                cap = r.get("capture", {}).get("onset") or {}
                lats = [(e.get("rc"), e.get("usec")) for e in r.get("events", []) if e.get("ev") == "latency_mid"]
                ready = next((e for e in r.get("events", []) if e.get("ev") == "stream_ready"), {})
                fin = next((e for e in r.get("events", []) if e.get("ev") == "final"), {})
                cork.setdefault(leg, {}).setdefault(tag, []).append({
                    "rc": r["rc"], "onset_rel_event": r.get("onset_ms_rel_event"),
                    "nonzero": cap.get("nonzero"), "peak": cap.get("peak"),
                    "latency_rc_ready": ready.get("latency_rc"), "latency_rc_final": fin.get("latency_rc"),
                    "latency_mid_rc": sorted({x[0] for x in lats}), "load": r.get("loadavg", {}).get("l1"),
                })
    with open(os.path.join(RUNS, "analysis-cork.txt"), "w") as fh:
        for leg, tags in sorted(cork.items()):
            fh.write(f"{leg}\n")
            for tag, rs in tags.items():
                for x in rs:
                    fh.write(f"  {tag}: rc={x['rc']} onset={x['onset_rel_event']} nonzero={x['nonzero']} peak={x['peak']} "
                             f"lrc_ready={x['latency_rc_ready']} lrc_final={x['latency_rc_final']} lrc_mid={x['latency_mid_rc']} load={x['load']}\n")
    out["cork"] = {leg: {t: [(x["onset_rel_event"], x["nonzero"], x["peak"], x["latency_rc_ready"], x["latency_rc_final"])
                          for x in rs] for t, rs in tags.items()} for leg, tags in cork.items()}

    # props
    props = {}
    for fname in sorted(os.listdir(REC)):
        if not fname.startswith("r96b_cli_props"):
            continue
        tag = fname.split("_")[-1].replace(".json", "")
        with open(os.path.join(REC, fname)) as fh:
            data = json.load(fh)
        rec = data["receipts"]
        for leg, body in rec.items():
            if isinstance(body, dict) and "results" in body:
                props.setdefault(leg, {})[tag] = [
                    {k: v for k, v in s.get("props", {}).items() if v is not None}
                    for r in body["results"] for s in r.get("my_streams", [])]
            elif isinstance(body, dict) and "rows_before" in body:
                props.setdefault(leg + ".rowcount", {})[tag] = {"before": body["rows_before"], "after": body["rows_after"]}
    with open(os.path.join(RUNS, "analysis-props.txt"), "w") as fh:
        for leg, tags in sorted(props.items()):
            fh.write(f"{leg}\n")
            for tag, v in tags.items():
                fh.write(f"  {tag}: {json.dumps(v)[:600]}\n")
    out["props"] = {leg: {t: v for t, v in tags.items()} for leg, tags in props.items()}

    # loadavg + hog context
    load_ctx = {}
    for fname in sorted(os.listdir(REC)):
        if fname.startswith("r96b_census_"):
            with open(os.path.join(REC, fname)) as fh:
                c = json.load(fh)
            load_ctx[fname] = {"loadavg": c.get("loadavg"), "utc": c.get("utc")}
    out["load_context"] = load_ctx

    # anomalies: hung legs + rows observed before pulse.attr.* were set
    anomalies = {"timed_out": [], "missing_attr_rows": []}
    for fname in sorted(os.listdir(REC)):
        if not fname.startswith("r96b_cli_"):
            continue
        for leg, body in iter_legs(os.path.join(REC, fname)):
            for r in body["results"]:
                if r.get("timed_out"):
                    anomalies["timed_out"].append({"file": fname, "leg": leg, "rep": r.get("rep"),
                                                   "rc": r.get("rc"), "load": r.get("loadavg", {}).get("l1")})
                if leg.startswith(("d_", "z_", "w_")) and r.get("my_streams") and not any(
                        "pulse.attr.tlength" in s.get("props", {}) for s in r["my_streams"]):
                    anomalies["missing_attr_rows"].append({"file": fname, "leg": leg, "rep": r.get("rep"),
                                                           "load": r.get("loadavg", {}).get("l1")})
    with open(os.path.join(RUNS, "analysis-anomalies.txt"), "w") as fh:
        fh.write(f"timed-out legs: {len(anomalies['timed_out'])}\n")
        for x in anomalies["timed_out"]:
            fh.write(f"  {x}\n")
        fh.write(f"rows observed without pulse.attr.*: {len(anomalies['missing_attr_rows'])}\n")
        for x in anomalies["missing_attr_rows"]:
            fh.write(f"  {x}\n")
    out["anomalies"] = anomalies

    with open(os.path.join(RUNS, "analysis-summary.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({"buffer_attr": out["buffer_attr"], "load_context": load_ctx}, indent=1))
    print("wrote runs/analysis-{bufferattr,server,target,cork,props}.txt + analysis-summary.json")


if __name__ == "__main__":
    main()
