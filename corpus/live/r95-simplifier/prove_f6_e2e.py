#!/usr/bin/env python3
"""r95 SIMPLIFIER — F6 end-to-end differential: the error-class table.

Runs the REAL fixture binary (built in this scratch dir) through BOTH
modules' `_jack_r95_run` with a no-daemon environment, and compares the
receipt fields the class table feeds (`error_class`, `error_hit`,
`exit_code`, `stdout`).  This is the narrow affected leg for F6 (the
`jack_r95_no_daemon` entry) — it needs no live JACK client, so it runs
while the host's daemon is saturated.

Writes prove-f6-e2e.json next to this file.
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = str(HERE / "bin" / "r95s_jack")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


shared = load("measure_audio_shared", HERE / "measure_audio.py")
folded = load("measure_audio_folded2", HERE / "measure_audio-folded.py")

env = os.environ.copy()
env["R95A_NAME"] = f"r95s_{os.getpid()}_e2e"
env["PIPEWIRE_RUNTIME_DIR"] = "/nonexistent-r95s"
argv = [FIX, "info", "0.1"]

a = shared._jack_r95_run(argv, 12.0, env=env, keep_raw=True)
b = folded._jack_r95_run(argv, 12.0, env=env, keep_raw=True)
keys = ("exit_code", "signal", "error_class", "error_hit", "stdout",
        "stderr", "killed_at_bound")
OUT = {"argv": " ".join(argv), "env_class": "no-daemon (PIPEWIRE_RUNTIME_DIR bogus)",
       "shared": {k: a.get(k) for k in keys},
       "folded": {k: b.get(k) for k in keys},
       "equal": {k: a.get(k) == b.get(k) for k in keys}}
OUT["all_equal"] = all(OUT["equal"].values())
(HERE / "prove-f6-e2e.json").write_text(json.dumps(OUT, indent=2, sort_keys=True) + "\n")
print(json.dumps(OUT, indent=2, sort_keys=True))
