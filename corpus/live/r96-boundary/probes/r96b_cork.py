#!/usr/bin/env python3
"""r96-boundary battery B — replay of the r96 scout's libpulse cork/trigger/
prebuf/record/resolve cells under controlled conditions (tag = quiet|load).

Own C client (probes/r96b_pulse, namespace r96b), own monitor capture
(pw-record, exact frame count), `pactl` JSON snapshots matched to the client
pid. Bounded: every child gets a wall cap + process-group kill; captures are
frame-bounded by construction. New in this seat: `--latency-mid 1` samples
pa_stream_get_latency during the hold/tail (scout unknown #7), and a subscribe
cell that counts events for the seat stream.

Usage: r96b_cork.py GROUP TAG
Groups: resolve cork trigger prebuf record subscribe
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
import r96b_lib as L  # noqa: E402

ROOT = L.ROOT
SEAT = L.SEAT_SINK_NAME
CLIENT = os.path.join(ROOT, "probes", "r96b_pulse")


def runlog(tag):
    return os.path.join(ROOT, "runs", f"batteryB_{tag}.log")


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
                "source_latency_usec": row.get("source_latency_usec"),
                "props": {k: props.get(k) for k in (
                    "pulse.corked", "pulse.attr.tlength", "pulse.attr.prebuf",
                    "pulse.attr.minreq", "node.latency", "target.object",
                    "application.name", "media.class", "node.name",
                ) if k in props},
            })
    return out


def run_client_leg(name, mode_args, cap_frames=None, rep=0, client_timeout=16.0, snapshot_dt=0.15):
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
        timeline.append({"t": round(time.monotonic() - t_cli, 3), "rows": rows,
                         "loadavg": L.loadavg()["l1"]})
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
            nonzero = sum(1 for v in a if abs(v) > 1000)
            for i, v in enumerate(a):
                if abs(v) > 1000:
                    onset = {"first_tone_frame": i, "frames": len(a), "nonzero": nonzero,
                             "onset_wall": t_rec + i / rate, "rate": rate,
                             "peak": max(abs(x) for x in a) if a else 0}
                    break
            if onset is None:
                onset = {"first_tone_frame": None, "frames": len(a), "nonzero": nonzero, "rate": rate,
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
        "loadavg": L.loadavg(),
        "events": events,
        "timeline": timeline,
        "capture": {"path": cap_path, "start_mono": t_rec, "onset": onset, "stderr": cap_err.decode("utf-8", "replace")[:500]},
        "onset_ms_rel_cli": onset_rel_cli,
        "onset_ms_rel_event": onset_rel_uncork,
        "stderr": err.decode("utf-8", "replace")[:2000],
    }
    L.log_line(runlog(name), f"{name} rep{rep} rc={cli.returncode} events={[e.get('ev') for e in events]} onset={onset}")
    return result


def group_resolve():
    rec = {}
    for tag, dev in (("name", SEAT), ("index", str(L.seat_sink_index())),
                     ("badindex", "999999"), ("missing", "no_such_r96b")):
        reps = [run_client_leg(f"g_resolve_{tag}", ["resolve", "--device", dev, "--label", f"r96b_res_{tag}",
                                                    "--amp", "0.001", "--tone-ms", "300", "--hold-ms", "100",
                                                    "--tail-ms", "100"], rep=r) for r in range(3)]
        rec[tag] = {"device": dev, "results": reps}
    return rec


def group_cork():
    rec = {}
    rec["h_cork"] = {"results": [run_client_leg("h_cork", [
        "cork", "--device", SEAT, "--label", "r96b_pulse_cork", "--latency-mid", "1",
        "--tone-ms", "1500", "--hold-ms", "1200", "--tail-ms", "1500"], cap_frames=192000, rep=r) for r in range(3)]}
    return rec


def group_trigger():
    rec = {}
    rec["h_trigger"] = {"results": [run_client_leg("h_trigger", [
        "trigger", "--device", SEAT, "--label", "r96b_pulse_trigger", "--latency-mid", "1",
        "--tone-ms", "1500", "--hold-ms", "1200", "--tail-ms", "1500"], cap_frames=192000, rep=r) for r in range(3)]}
    return rec


def group_prebuf():
    rec = {}
    rec["i_prebuf_default"] = {"results": [run_client_leg("i_prebuf_default", [
        "prebuf", "--device", SEAT, "--label", "r96b_pulse_pb_def", "--latency-mid", "1",
        "--tone-ms", "1200", "--chunk-ms", "100", "--period-ms", "250", "--tail-ms", "600"],
        cap_frames=192000, rep=r) for r in range(3)]}
    rec["i_prebuf_zero"] = {"results": [run_client_leg("i_prebuf_zero", [
        "prebuf0", "--device", SEAT, "--label", "r96b_pulse_pb_0", "--prebuf", "0", "--latency-mid", "1",
        "--tone-ms", "1200", "--chunk-ms", "100", "--period-ms", "250", "--tail-ms", "600"],
        cap_frames=192000, rep=r) for r in range(3)]}
    rec["i_prebuf_zero_fast"] = {"results": [run_client_leg("i_prebuf_zero_fast", [
        "prebuf0", "--device", SEAT, "--label", "r96b_pulse_pb_0f", "--prebuf", "0",
        "--tone-ms", "1200", "--chunk-ms", "1200", "--period-ms", "250", "--tail-ms", "600"],
        cap_frames=192000, rep=r) for r in range(2)]}
    rec["i_prebuf_default_fast"] = {"results": [run_client_leg("i_prebuf_default_fast", [
        "prebuf", "--device", SEAT, "--label", "r96b_pulse_pb_df",
        "--tone-ms", "1200", "--chunk-ms", "1200", "--period-ms", "250", "--tail-ms", "600"],
        cap_frames=192000, rep=r) for r in range(2)]}
    return rec


def group_record():
    rec = {}
    rec["j_record_cork"] = {"results": [run_client_leg("j_record_cork", [
        "record", "--device", f"{SEAT}.monitor", "--label", "r96b_pulse_rec",
        "--hold-ms", "1200", "--tail-ms", "900"], rep=r) for r in range(3)]}
    return rec


def group_subscribe():
    """Unbuffered, timestamped subscribe trace across one cork/uncork/remove lifecycle."""
    import threading
    rec = {}
    for rep in range(2):
        sub = subprocess.Popen(["stdbuf", "-o0", "pactl", "subscribe"], env=L.base_env(),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True, preexec_fn=L._limits)
        t0 = time.monotonic()
        lines = []

        def reader():
            for raw in sub.stdout:
                lines.append((round(time.monotonic() - t0, 3), raw.decode("utf-8", "replace").strip()))

        th = threading.Thread(target=reader, daemon=True)
        th.start()
        time.sleep(0.5)
        res = run_client_leg("k_sub", [
            "cork", "--device", SEAT, "--label", "r96b_pulse_sub",
            "--tone-ms", "1500", "--hold-ms", "1000", "--tail-ms", "800"], rep=rep)
        time.sleep(0.5)
        try:
            os.killpg(sub.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            sub.communicate(timeout=6)
        except subprocess.TimeoutExpired:
            pass
        th.join(timeout=3)
        # our stream's sink-input index from the client timeline
        idx = None
        for t in res["timeline"]:
            for r in t["rows"]:
                idx = r["index"]
        uncork_abs = next((round(e["t_ms"] / 1000.0, 3) for e in res["events"] if e.get("ev") == "uncork"), None)
        mine = [(t, ln) for t, ln in lines if idx is not None and f"#{idx}" in ln]
        rec[f"k_sub_rep{rep}"] = {"stream_index": idx, "t0_mono": round(t0, 3),
                                  "uncork_abs_mono": uncork_abs,
                                  "events_mine": mine, "all_event_count": len(lines),
                                  "client": res}
    return rec


GROUPS = {
    "resolve": group_resolve,
    "cork": group_cork,
    "trigger": group_trigger,
    "prebuf": group_prebuf,
    "record": group_record,
    "subscribe": group_subscribe,
}


def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "cork"
    tag = sys.argv[2] if len(sys.argv) > 2 else "adhoc"
    t_start = time.time()
    receipts = GROUPS[group]()
    payload = {
        "battery": "r96b_cork",
        "group": group,
        "tag": tag,
        "started": t_start,
        "finished": time.time(),
        "loadavg_start": L.loadavg(),
        "seat_sink": SEAT,
        "seat_sink_index": L.seat_sink_index(),
        "client_sha": L.run_bounded(["sha256sum", CLIENT], timeout=4)["stdout"].strip(),
        "receipts": receipts,
    }
    path = L.write_receipt(f"r96b_cork_{group}_{tag}.json", payload)
    print("wrote", path)
    for k, v in receipts.items():
        if isinstance(v, dict) and "results" in v:
            print(f"  {k}: rc={[r['rc'] for r in v['results']]} onsets={[r['onset_ms_rel_event'] for r in v['results']]}")
        elif isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, dict) and "results" in vv:
                    print(f"  {k}.{kk}: rc={[r['rc'] for r in vv['results']]}")
                else:
                    print(f"  {k}.{kk}: (meta)")
        else:
            print(f"  {k}: (meta)")


if __name__ == "__main__":
    main()
