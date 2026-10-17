#!/usr/bin/env python3
"""r79 CRITIC forge 3 — the foreign-tone ceiling, measured.

Live: load a probe null sink, play a tag-shaped tone (this run's own pid
frequency pair) into it at three amplitudes, tap the sink's monitor and
push the REAL tap leaf through the REAL `_loopback_r79_check_tap` as a
leg that was never fed.

  A  amp 8192  (this arm's own nominal)      -> ?
  B  amp 12000 (the measured 07:16Z event)   -> ?
  C  amp 9000  (between the two)             -> ?

Also records the tap's real producer set, to show what the arm's
provenance witness can and cannot name.
"""
import importlib.util
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "r79_measure_audio", HERE.parents[1] / "fixtures/measure_audio.py")
m = importlib.util.module_from_spec(spec)
sys.modules["r79_measure_audio"] = m
spec.loader.exec_module(m)

PID = os.getpid()
SINK = f"r79cr_ceil_{PID}"
TAG = f"r79cr_feed_{PID}"
RATE = m.PLAYBACK_R78_TONE_RATE
L = m.PLAYBACK_R78_TONE_L_HZ
Rr = m.PLAYBACK_R78_TONE_R_HZ


def write_tone(path, amp, seconds=3.0):
    import numpy as np
    n = int(RATE * seconds)
    t = np.arange(n) / RATE
    left = (amp * np.sin(2 * np.pi * L * t)).astype("<i2")
    right = (amp * np.sin(2 * np.pi * Rr * t)).astype("<i2")
    pcm = np.empty(n * 2, dtype="<i2")
    pcm[0::2], pcm[1::2] = left, right
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())


out = {"pid": PID, "sink": SINK, "tone_l_hz": L, "tone_r_hz": Rr,
       "ceiling": m.PLAYBACK_R78_TONE_AMP * 1.05, "variants": {}}
mid, rc, err = m._playback_r78_null_sink_load(SINK)
out["sink_module"] = {"module_id": mid, "rc": rc, "error": err}
ready, waited, diag = m._loopback_r79_wait_monitor(SINK)
out["monitor_gate"] = {"ready": ready, "waited_s": waited, **diag}

try:
    with tempfile.TemporaryDirectory(prefix="r79cr-ceil-") as tmp:
        for label, amp in (("A_8192", 8192), ("C_9000", 9000),
                           ("B_12000", 12000)):
            wav = Path(tmp) / f"tone_{label}.wav"
            tapf = Path(tmp) / f"tap_{label}.wav"
            write_tone(wav, amp)
            feed = subprocess.Popen(
                ["pw-cat", "-p", "-P", f"node.name={TAG}_{label}",
                 "--target", SINK, str(wav)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True)
            time.sleep(0.6)
            tap = m._playback_r78_tap(SINK, tapf, int(RATE * 1.6),
                                      f"{TAG}_{label}_tap")
            links = m._playback_r78_links()
            prods = m._playback_r78_producers(f"{TAG}_{label}_tap", links)
            m._capture_r77_reap(tap, m.PLAYBACK_R78_TIMEOUT_S)
            if feed.poll() is None:
                os.killpg(feed.pid, signal.SIGKILL)
            feed.wait()
            wins = m._playback_r78_tone_windows(tapf)
            leaf = {"target": SINK, "exit_code": tap.returncode,
                    "bound_to_target": prods["nodes"] == [SINK],
                    "bound_producers": prods["nodes"],
                    "never_bound": False, "stderr_tail": "",
                    **wins}
            leaf["ran"] = bool(leaf.get("windows"))
            # the leg shape: a `want_tone=False` leg of the -C/-P lattices
            # (tap on the shared default sink, never fed by this arm)
            leg = {"fed": False, "input_producers_union": [SINK],
                   "output_consumers_union": [], "tap": leaf}
            entry = {}
            failures = []
            m._loopback_r79_check_tap(entry, failures,
                                      f"forge3 {label}", leg,
                                      want_tone=False)
            out["variants"][label] = {
                "amp": amp,
                "tap_peak_l": leaf.get("peak_l"),
                "tap_peak_r": leaf.get("peak_r"),
                "mine_windows": leaf.get("mine_windows"),
                "carries_tone": leaf.get("carries_tone"),
                "tap_producers": prods["nodes"],
                "tap_producer_ports": prods["producer_ports"],
                "tone_played_by": f"{TAG}_{label}",
                "leg_outcome": leg.get("outcome"),
                "leg_confound": leg.get("confound"),
                "foreign_tone_witness": leg.get("foreign_tone_witness"),
                "failures": failures,
                "entry_named_outcomes": entry.get("named_outcomes"),
                "verdict": "EXCUSED (no failure)" if not failures
                           else "FAILED",
            }
finally:
    m._playback_r78_unload(mid)
    time.sleep(0.6)
    left = [s for s in (m._capture_r77_sink_names() or []) if s == SINK]
    out["teardown_sink_gone"] = not left
    out["own_nodes_after"] = [n for n in (m._playback_r78_node_names() or [])
                              if "r79cr_" in n]

print(json.dumps(out, indent=1))
