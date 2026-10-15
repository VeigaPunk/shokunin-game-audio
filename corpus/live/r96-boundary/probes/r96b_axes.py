#!/usr/bin/env python3
"""r96-boundary axes battery — independent axes the scout did not vary:

  quantum <q>   clock.force-quantum=<q> (settings metadata), replay attr/cork
                cells, restore 0. Records settings before/after + live node dump.
  rate <r>      clock.force-rate=<r>, same shape, restore 0.
  order         CLI flag-order cells for the server flag + latency/process-time
                (also armed inside battery A; here as a focused receipt).

The metadata writes are global host state; each window is short and the original
value (0) is restored and verified in the same receipt. No `set-default-*`.
Usage: r96b_axes.py AXIS [VALUE] [TAG]
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
import r96b_cli as A  # noqa: E402

ROOT = L.ROOT
SEAT = L.SEAT_SINK_NAME
TONE = os.path.join(ROOT, "scratch", "tone1k5.wav")


def set_meta(key, value):
    return L.run_bounded(["pw-metadata", "-n", "settings", "0", key, str(value)], timeout=6)


def live_node_dump(seconds=2.0):
    """Start a seat stream, dump the live node props, kill it."""
    env = L.base_env(); env.update({"PULSE_SINK": SEAT})
    p = subprocess.Popen(["paplay", TONE], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True, preexec_fn=L._limits)
    time.sleep(0.6)
    nodes, meta = L.pw_dump_filtered(["r96b"])
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    p.communicate()
    return {"nodes": nodes, "meta": meta}


def axis_quantum(q, tag):
    rec = {"axis": "quantum", "value": q, "tag": tag, "loadavg": L.loadavg()}
    rec["settings_before"] = L.settings_meta()
    rec["set_rc"] = set_meta("clock.force-quantum", q)
    time.sleep(0.6)
    rec["settings_set"] = L.settings_meta()
    rec["live_nodes"] = live_node_dump()
    rec["d_default"] = A.leg_stream("xq_default", ["paplay", TONE], {"PULSE_SINK": SEAT}, reps=2)
    rec["d_env100"] = A.leg_stream("xq_env100", ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": "100"}, reps=2)
    rec["d_flag100"] = A.leg_stream("xq_flag100", ["pacat", "--playback", "--latency-msec=100", "--raw", "--rate=48000",
                                                    "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT}, reps=2)
    rec["d_proctime5"] = A.leg_stream("xq_proctime5", ["pacat", "--playback", "--process-time-msec=5", "--raw", "--rate=48000",
                                                       "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT}, reps=2)
    rec["restore_rc"] = set_meta("clock.force-quantum", 0)
    time.sleep(0.4)
    rec["settings_after"] = L.settings_meta()
    return rec


def axis_rate(r, tag):
    rec = {"axis": "rate", "value": r, "tag": tag, "loadavg": L.loadavg()}
    rec["settings_before"] = L.settings_meta()
    rec["set_rc"] = set_meta("clock.force-rate", r)
    time.sleep(0.8)
    rec["settings_set"] = L.settings_meta()
    rec["live_nodes"] = live_node_dump()
    rec["d_default"] = A.leg_stream("xr_default", ["paplay", TONE], {"PULSE_SINK": SEAT}, reps=2)
    rec["d_env100"] = A.leg_stream("xr_env100", ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": "100"}, reps=2)
    rec["restore_rc"] = set_meta("clock.force-rate", 0)
    time.sleep(0.4)
    rec["settings_after"] = L.settings_meta()
    return rec


def axis_order(tag):
    rec = {"axis": "order", "tag": tag, "loadavg": L.loadavg()}
    uid = os.getuid()
    rec["pactl_s_before"] = A.leg_cmd("xo_pactl_s_before", ["pactl", "-s", f"unix:/run/user/{uid}/pulse/native", "info"], reps=2)
    rec["pactl_s_after"] = A.leg_cmd("xo_pactl_s_after", ["pactl", "info", "-s", f"unix:/run/user/{uid}/pulse/native"], reps=2)
    rec["pactl_s_after_eq"] = A.leg_cmd("xo_pactl_s_after_eq", ["pactl", "info", "--server=unix:/run/user/{}/pulse/native".format(uid)], reps=2)
    rec["lat_dev"] = A.leg_stream("xo_lat_dev", ["pacat", "--playback", "--latency-msec=100", "--device=" + SEAT,
                                                 "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], reps=2)
    rec["dev_lat"] = A.leg_stream("xo_dev_lat", ["pacat", "--playback", "--device=" + SEAT, "--latency-msec=100",
                                                 "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], reps=2)
    rec["proc_lat"] = A.leg_stream("xo_proc_lat", ["pacat", "--playback", "--process-time-msec=5", "--latency-msec=100",
                                                   "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE],
                                   {"PULSE_SINK": SEAT}, reps=2)
    rec["lat_proc"] = A.leg_stream("xo_lat_proc", ["pacat", "--playback", "--latency-msec=100", "--process-time-msec=5",
                                                   "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE],
                                   {"PULSE_SINK": SEAT}, reps=2)
    return rec


AXES = {
    "quantum": axis_quantum,
    "rate": axis_rate,
    "order": axis_order,
}


def main():
    axis = sys.argv[1] if len(sys.argv) > 1 else "order"
    value = sys.argv[2] if len(sys.argv) > 2 else None
    tag = sys.argv[3] if len(sys.argv) > 3 else "adhoc"
    t_start = time.time()
    L.ensure_sink()
    if axis == "order":
        rec = axis_order(tag)
        name = f"r96b_axes_order_{tag}.json"
    else:
        rec = AXES[axis](value, tag)
        name = f"r96b_axes_{axis}_{value}_{tag}.json"
    payload = {"battery": "r96b_axes", "axis": axis, "value": value, "tag": tag,
               "started": t_start, "finished": time.time(), "loadavg_start": L.loadavg(), "receipt": rec}
    path = L.write_receipt(name, payload)
    print("wrote", path)


if __name__ == "__main__":
    main()
