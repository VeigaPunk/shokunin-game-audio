#!/usr/bin/env python3
"""Run --probe-capture-r79 with an injected fault so the entries' blocked
paths (unreachable on a healthy host) are exercised end to end, identically
on the control and the folded candidate.

    python3 faultrun.py monitor   <probe.py>
    python3 faultrun.py authority <probe.py>

monitor   — `_loopback_r79_wait_monitor` reports "not ready", so every
            entry's null-sink/monitor gate blocks AFTER a real module load
            (the unload path in the shared block helper runs for real).
authority — `_capture_inventory` and `_loopback_r79_oracle` report nothing
            readable (all None) and the shipped filter-chain.conf is
            reported absent, so the six authority blocks and the fc
            base-missing block fire.
"""
import importlib.util
import pathlib
import sys


def load(path):
    spec = importlib.util.spec_from_file_location("ma_fault", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fault, probe = sys.argv[1], sys.argv[2]
mod = load(probe)

if fault == "monitor":
    def broken_monitor(name, timeout_s=mod.LOOPBACK_R79_NODE_WAIT_S):
        return False, 0.0, {"pactl_listed": False, "monitor_ports": False,
                            "injected_fault": "monitor-gate"}
    mod._loopback_r79_wait_monitor = broken_monitor
elif fault == "authority":
    mod._capture_inventory = lambda: {
        "sources": [], "monitors": [], "default_source": None,
        "default_sink": None, "server_name": None, "pw_capture_ports": [],
        "alsa_capture_devices": [], "alsa_plugins": [],
        "ffmpeg_demuxers": {}, "injected_fault": "authority"}
    mod._loopback_r79_oracle = lambda: {
        "sink_meta": None, "source_meta": None, "sink_pactl": None,
        "source_pactl": None, "pactl_exit": None,
        "injected_fault": "authority"}
    _orig_exists = pathlib.Path.exists

    def exists(self):
        if str(self) == "/usr/share/pipewire/filter-chain.conf":
            return False
        return _orig_exists(self)
    pathlib.Path.exists = exists
else:
    raise SystemExit(f"unknown fault {fault!r}")

sys.argv = [probe, "--probe-capture-r79"]
mod.main()
