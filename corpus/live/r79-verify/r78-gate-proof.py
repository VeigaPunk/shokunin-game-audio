#!/usr/bin/env python3
"""r79-verifier: first-hand mechanism proof for the r78 monitor-source gate.

Imports the PRISTINE HEAD module (git show HEAD:…) — no r79 diff — and
exercises the committed `_playback_r78_wait_source("<sink>.monitor")` path
against a freshly loaded null sink, recording each half of the gate:
pactl source listing vs pw-link port ownership. Read-only w.r.t. the repo;
one null sink loaded and unloaded by module id.
"""
import importlib.util
import json
import os
import time

SPEC = importlib.util.spec_from_file_location(
    "measure_audio_head",
    "corpus/live/r79-verify/head-mod/measure_audio_head.py")
mah = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mah)

name = f"r79verify_ns_{os.getpid()}"
out = {"sink": name, "module": "head",
       "module_sha256": None}
import hashlib
out["module_sha256"] = hashlib.sha256(open(
    "corpus/live/r79-verify/head-mod/measure_audio_head.py",
    "rb").read()).hexdigest()

mid, rc, err = mah._playback_r78_null_sink_load(name)
out["sink_load"] = {"module_id": mid, "rc": rc, "error": err}
time.sleep(1.0)
out["pactl_sources_contains_monitor"] = \
    f"{name}.monitor" in mah._playback_r78_source_names()
out["pwlink_output_ports_owned_by_sink"] = \
    mah._playback_r78_output_ports(name)
out["pwlink_output_ports_tagged_monitor_source"] = \
    mah._playback_r78_output_ports(f"{name}.monitor")
t0 = time.monotonic()
seen, waited = mah._playback_r78_wait_source(f"{name}.monitor")
out["r78_wait_source"] = {"enumerated": seen, "waited_s": waited,
                          "wall_s": round(time.monotonic() - t0, 2)}
# the r79-local gate for contrast (same module? no — r79 code is not in
# HEAD; read the working tree module's gate separately)
spec2 = importlib.util.spec_from_file_location(
    "measure_audio_tree", "corpus/fixtures/measure_audio.py")
mah2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(mah2)
out["r79_wait_monitor"] = dict(zip(("ready", "waited_s", "diag"),
                                   mah2._loopback_r79_wait_monitor(name)))
out["unload_rc"] = mah._playback_r78_unload(mid)
time.sleep(0.5)
out["sink_gone"] = name not in mah._capture_r77_sink_names()
print(json.dumps(out, indent=2))
