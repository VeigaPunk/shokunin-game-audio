#!/usr/bin/env python3
"""r79 CRITIC forge 2 — the content pin is not injective.

One real leg is spawned through the frozen `_loopback_r79_leg` with a
ONE-TOKEN change: the tag-tone feed goes to the TAP's sink instead of the
leg's capture source.  `_loopback_r79_guard_playback` accepts it (both
names are probe-owned) and nothing else in the arm notices.

The leg's route under test is  tone -> <ns_a> -> loopback -> <ns_b2>.
The tap listens on <ns_b>, which the loopback NEVER feeds.

Expected if the content pin were injective: the tap reports no `mine`
window (the path under test carried nothing to it).
"""
import importlib.util
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "r79_measure_audio", HERE.parents[1] / "fixtures/measure_audio.py")
m = importlib.util.module_from_spec(spec)
sys.modules["r79_measure_audio"] = m
spec.loader.exec_module(m)

PID = os.getpid()
NS_A = f"r79cr_a_{PID}"      # capture source (probe-owned)
NS_B = f"r79cr_b_{PID}"      # tap target (probe-owned)  <- bypass sink
NS_B2 = f"r79cr_b2_{PID}"    # the leg's real playback target

out = {"pid": PID, "sinks": [NS_A, NS_B, NS_B2], "legs": {}}
loads = {}
try:
    for nm in (NS_A, NS_B, NS_B2):
        mid, rc, err = m._playback_r78_null_sink_load(nm)
        ready, waited, diag = m._loopback_r79_wait_monitor(nm)
        loads[nm] = mid
        out.setdefault("sink_loads", {})[nm] = {
            "module_id": mid, "rc": rc, "error": err,
            "monitor_ready": ready, "monitor_waited_s": waited}
    with tempfile.TemporaryDirectory(prefix="r79cr-bypass-") as tmp:
        tone = Path(tmp) / "tag_tone.wav"
        m._playback_r78_write_tone(tone, m.LOOPBACK_R79_TONE_S)
        ctx = {"tmp": tmp, "tone": tone, "bound_s": m.LOOPBACK_R79_LEG_BOUND_S,
               "own_sinks": {NS_A, NS_B, NS_B2},
               "redact": [NS_A, NS_B, NS_B2],
               "default_at_start": NS_B2, "source_at_start": NS_A}

        def one(name, feed_sink, tap_target, play_target):
            leg = m._loopback_r79_leg(
                name, ["-C", NS_A, "-i", "stream.capture.sink=true",
                       "-P", play_target], ctx,
                feed_sink=feed_sink, tap_target=tap_target,
                tap_seconds=m.LOOPBACK_R79_LEG_BOUND_S +
                m.PLAYBACK_R78_TAP_LEAD_S + 0.5)
            ltag = leg["ltag"]
            in_n, out_n = f"input.{ltag}", f"output.{ltag}"
            entry, failures = {}, []
            m._loopback_r79_check_side(entry, failures, name, leg,
                                       "consumers", out_n, play_target,
                                       {"sink_meta": leg.get(
                                            "default_sink_at_leg"),
                                        "source_meta": None})
            m._loopback_r79_check_tap(entry, failures, name, leg,
                                      want_tone=True)
            tap = leg.get("tap") or {}
            # the loopback's own consumers: where the tone under test went
            cons = m._loopback_r79_union(leg["samples"], out_n, "consumers")
            # every node the loopback's output ports actually fed
            cons_ports = m._loopback_r79_union(
                leg["samples"], out_n, "consumer_ports")
            from_lb = [p for p in cons_ports
                       if p.rsplit(":", 1)[0] == tap_target]
            return {
                "feed_sink": feed_sink, "tap_target": tap_target,
                "play_target": play_target,
                "loopback_consumers": cons,
                "tap_bound_to_target": tap.get("bound_to_target"),
                "tap_bound_producers": tap.get("bound_producers"),
                "tap_mine_windows": tap.get("mine_windows"),
                "tap_peak_l": tap.get("peak_l"),
                "tap_peak_r": tap.get("peak_r"),
                "tap_carries_tone": tap.get("carries_tone"),
                "link_from_loopback_to_tap_target": from_lb,
                "failures": failures,
                "verdict": "PASS (content pin satisfied)"
                           if not failures else "FAIL",
            }

        # the FROZEN shape (control): feed the capture source, tap the
        # playback target.
        out["legs"]["control_feed_source"] = one(
            "ctrl", NS_A, NS_B2, NS_B2)
        time.sleep(m.LOOPBACK_R79_SETTLE_S)
        # the FORGE: one token changed — feed the TAP target directly.
        out["legs"]["forge_feed_tap_target"] = one(
            "forge", NS_B, NS_B, NS_B2)
finally:
    for nm, mid in loads.items():
        m._playback_r78_unload(mid)
    time.sleep(0.8)
    sinks_now = m._capture_r77_sink_names() or []
    out["teardown"] = {nm: nm not in sinks_now for nm in loads}
    out["own_nodes_after"] = [n for n in (m._playback_r78_node_names() or [])
                              if "r79cr_" in n]

print(json.dumps(out, indent=1))
