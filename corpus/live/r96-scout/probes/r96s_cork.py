#!/usr/bin/env python3
"""r96-scout battery B — libpulse client cork/trigger/prebuf/record-cork + device resolution.

Own C client (probes/r96pulse) linked against host libpulse 17.0; own monitor
capture (pw-record, exact frame count) for onset timing; `pactl` JSON snapshots
matched to the client pid. Bounded: every child gets a wall cap + process-group
kill; captures are frame-bounded by construction.
"""
from __future__ import annotations

import array
import json
import os
import signal
import subprocess
import sys
import time
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r96s_lib as L  # noqa: E402

ROOT = L.ROOT
SEAT = L.SEAT_SINK_NAME
CLIENT = os.path.join(ROOT, "probes", "r96pulse")
RUNLOG = os.path.join(ROOT, "runs", "batteryB.log")


def my_stream_rows(pid, kind="sink-inputs"):
    rows, _ = L.pactl_json(["list", kind])
    out = []
    for row in rows or []:
        props = row.get("properties", {})
        if str(props.get("application.process.id")) == str(pid):
            out.append({
                "index": row.get("index"),
                "sink": row.get("sink"), "source": row.get("source"),
                "corked": row.get("corked"), "mute": row.get("mute"),
                "buffer_latency_usec": row.get("buffer_latency_usec"),
                "sink_latency_usec": row.get("sink_latency_usec"),
                "props": {k: props.get(k) for k in (
                    "pulse.corked", "pulse.attr.tlength", "pulse.attr.prebuf",
                    "pulse.attr.minreq", "node.latency", "target.object",
                    "application.name", "media.class",
                ) if k in props},
            })
    return out


def run_client_leg(name, mode_args, cap_frames=None, rep=0, client_timeout=14.0, snapshot_dt=0.15):
    """One C-client leg; optional pw-record monitor capture for onset timing."""
    cap = None
    cap_path = None
    t_rec = None
    if cap_frames:
        cap_path = os.path.join(ROOT, "scratch", f"cap_{name}_r{rep}.wav")
        t_rec = time.monotonic()
        cap = subprocess.Popen(
            ["pw-record", "-P", "stream.capture.sink=true", "--target", SEAT, "-n", str(cap_frames),
             "--rate", "48000", "--channels", "1", "--format", "s16", cap_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            start_new_session=True, preexec_fn=L._limits)
        time.sleep(0.35)  # let the capture link while the sink is silent

    t_cli = time.monotonic()
    cli = subprocess.Popen([CLIENT] + mode_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           start_new_session=True, preexec_fn=L._limits)
    timeline = []
    kind = "source-outputs" if mode_args[0] == "record" else "sink-inputs"
    deadline = t_cli + client_timeout
    while cli.poll() is None and time.monotonic() < deadline:
        rows = my_stream_rows(cli.pid, kind)
        timeline.append({"t": round(time.monotonic() - t_cli, 3), "rows": rows})
        time.sleep(snapshot_dt)
    timed_out = cli.poll() is None
    if timed_out:
        try:
            os.killpg(cli.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    out, err = cli.communicate()
    t_cli_end = time.monotonic()
    cap_err = b""
    if cap is not None:
        remaining = (cap_frames / 48000.0 + 0.5) - (time.monotonic() - t_rec)
        try:
            cap.wait(timeout=max(0.5, remaining))
        except subprocess.TimeoutExpired:
            try:
                os.killpg(cap.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                cap.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(cap.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        cap_err = cap.stderr.read() if cap.stderr else b""
    events = []
    for line in out.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    onset = None
    if cap_path and os.path.exists(cap_path):
        try:
            with wave.open(cap_path, "rb") as w:
                n = w.getnframes()
                data = w.readframes(n)
            a = array.array("h")
            a.frombytes(data[: (len(data) // 2) * 2])
            rate = 48000
            for i, v in enumerate(a):
                if abs(v) > 1000:
                    onset = {"first_tone_frame": i, "frames": len(a),
                             "onset_wall": t_rec + i / rate, "rate": rate,
                             "peak": max(abs(x) for x in a) if a else 0}
                    break
            if onset is None:
                onset = {"first_tone_frame": None, "frames": len(a), "rate": rate,
                         "peak": max(abs(x) for x in a) if a else 0}
        except (wave.Error, OSError) as exc:
            onset = {"error": str(exc)}
    rel = {}
    for e in events:
        if e.get("ev") in ("uncork", "trigger"):
            rel["event_t"] = e.get("t_ms")
    onset_rel_uncork = None
    if onset and onset.get("onset_wall") and rel.get("event_t"):
        onset_rel_uncork = round((onset["onset_wall"] - rel["event_t"] / 1000.0) * 1000, 1)
    onset_rel_cli = None
    if onset and onset.get("onset_wall"):
        onset_rel_cli = round((onset["onset_wall"] - t_cli) * 1000, 1)
    result = {
        "leg": name, "rep": rep, "argv": [CLIENT] + mode_args,
        "rc": cli.returncode, "timed_out": timed_out,
        "wall_s": round(t_cli_end - t_cli, 3),
        "events": events,
        "timeline": timeline,
        "capture": {"path": cap_path, "start_mono": t_rec, "onset": onset, "stderr": cap_err.decode("utf-8", "replace")[:500]},
        "onset_ms_rel_cli": onset_rel_cli,
        "onset_ms_rel_event": onset_rel_uncork,
        "stderr": err.decode("utf-8", "replace")[:2000],
    }
    L.log_line(RUNLOG, f"{name} rep{rep} rc={cli.returncode} events={[e.get('ev') for e in events]} onset={onset}")
    return result


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    receipts = {}
    if only in ("all", "resolve"):
        receipts["g_resolve"] = {}
        for tag, dev in (("name", SEAT), ("index", str(L.seat_sink_index())),
                         ("badindex", "999999"), ("missing", "no_such_r96s")):
            reps = [run_client_leg(f"g_resolve_{tag}", ["resolve", "--device", dev,
                                                        "--tone-ms", "300", "--hold-ms", "100",
                                                        "--tail-ms", "100"], rep=r) for r in range(3)]
            receipts["g_resolve"][tag] = {"device": dev, "results": reps}
    if only in ("all", "cork"):
        receipts["h_cork"] = {"results": [run_client_leg("h_cork", [
            "cork", "--device", SEAT, "--label", "r96s_pulse_cork",
            "--tone-ms", "1500", "--hold-ms", "1200", "--tail-ms", "1500"], cap_frames=192000, rep=r) for r in range(3)]}
        receipts["h_trigger"] = {"results": [run_client_leg("h_trigger", [
            "trigger", "--device", SEAT, "--label", "r96s_pulse_trigger",
            "--tone-ms", "1500", "--hold-ms", "1200", "--tail-ms", "1500"], cap_frames=192000, rep=r) for r in range(3)]}
    if only in ("all", "prebuf"):
        receipts["i_prebuf_default"] = {"results": [run_client_leg("i_prebuf_default", [
            "prebuf", "--device", SEAT, "--label", "r96s_pulse_pb_def",
            "--tone-ms", "1200", "--chunk-ms", "100", "--period-ms", "250", "--tail-ms", "600"],
            cap_frames=192000, rep=r) for r in range(3)]}
        receipts["i_prebuf_zero"] = {"results": [run_client_leg("i_prebuf_zero", [
            "prebuf0", "--device", SEAT, "--label", "r96s_pulse_pb_0", "--prebuf", "0",
            "--tone-ms", "1200", "--chunk-ms", "100", "--period-ms", "250", "--tail-ms", "600"],
            cap_frames=192000, rep=r) for r in range(3)]}
        # fast-feed controls: one write, no starvation expected
        receipts["i_prebuf_zero_fast"] = {"results": [run_client_leg("i_prebuf_zero_fast", [
            "prebuf0", "--device", SEAT, "--label", "r96s_pulse_pb_0f", "--prebuf", "0",
            "--tone-ms", "1200", "--chunk-ms", "1200", "--period-ms", "250", "--tail-ms", "600"],
            cap_frames=192000, rep=r) for r in range(2)]}
        receipts["i_prebuf_default_fast"] = {"results": [run_client_leg("i_prebuf_default_fast", [
            "prebuf", "--device", SEAT, "--label", "r96s_pulse_pb_df",
            "--tone-ms", "1200", "--chunk-ms", "1200", "--period-ms", "250", "--tail-ms", "600"],
            cap_frames=192000, rep=r) for r in range(2)]}
    if only in ("all", "record"):
        receipts["j_record_cork"] = {"results": [run_client_leg("j_record_cork", [
            "record", "--device", f"{SEAT}.monitor", "--label", "r96s_pulse_rec",
            "--hold-ms", "1200", "--tail-ms", "900"], rep=r) for r in range(3)]}
    payload = {"battery": "r96s_cork", "seat_sink": SEAT, "seat_sink_index": L.seat_sink_index(),
               "client_sha": L.run_bounded(["sha256sum", CLIENT], timeout=4)["stdout"].strip(),
               "receipts": receipts}
    path = L.write_receipt(f"r96s_cork_{only}.json", payload)
    print("wrote", path)
    for k, v in receipts.items():
        if isinstance(v, dict) and "results" in v:
            print(f"  {k}: rc={[r['rc'] for r in v['results']]} onsets={[r['onset_ms_rel_event'] for r in v['results']]}")
        elif isinstance(v, dict):
            for kk, vv in v.items():
                print(f"  {k}.{kk}: rc={[r['rc'] for r in vv['results']]}")


if __name__ == "__main__":
    main()
