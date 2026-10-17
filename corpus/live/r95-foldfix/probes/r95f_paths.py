"""r95 foldfix — block/failure-path probes (end-to-end through the FIXED
entry functions; no repo writes, no daemon mutation beyond the
`clock.force-quantum 0` restore the family itself owns).

Sections:
  A  daemon gate, two failure modes, end-to-end through the 5 entries
  B  except-path census (F3/C2) + harness-side restore on the failure
     path (F5)
  C  family-lock busy path (F6/C4) with the dispatch's exact expression
"""
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

TREE = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r95-foldfix/tree")
SRC = TREE / "corpus/fixtures/measure_audio.py"
STUB = Path("/home/vgpnk/Projects/shokunin/tmp/r95f/stub")


def load():
    spec = importlib.util.spec_from_file_location("ma_r95f_probe", SRC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ENTRIES = ("jack_surface_r95_probe", "jack_addr_r95_probe",
           "jack_bytes_r95_probe", "jack_quantum_r95_probe",
           "jack_defects_r95_probe")


def summarise(entries):
    out = {}
    for k, e in entries.items():
        out[k] = {"measured": e.get("measured"),
                  "legs_measured": e.get("legs_measured"),
                  "legs": sorted(e.get("legs") or {}),
                  "blocked": (e.get("blocked") or "")[:150],
                  "failures": e.get("failures"),
                  "coverage_blocked": [c[:120] for c in
                                       (e.get("coverage_blocked") or [])],
                  "census_keys": sorted(
                      x for x in e if x in
                      ("sinks_gone", "sinks_censused", "own_nodes_after",
                       "stream_properties_own_rows", "sinks_gone_note"))}
    return out


report = {}

# ---------------------------------------------------------------- A
STUB.mkdir(parents=True, exist_ok=True)
env = dict(os.environ)
env["PATH"] = f"{STUB}:{env['PATH']}"

# A1: fast refusal (the reviewer's rc-1 "Connection failure: Timeout")
(STUB / "pactl").write_text('#!/bin/sh\necho "Connection failure: Timeout" >&2\nexit 1\n')
os.chmod(STUB / "pactl", 0o755)
m = load()
os.environ["PATH"] = env["PATH"]
lock = m._jack_r95_family_lock()
a1 = {k: fn() for k, fn in (
    ("jack_surface_r95_probe", m.jack_surface_r95_entry),
    ("jack_addr_r95_probe", m.jack_addr_r95_entry),
    ("jack_bytes_r95_probe", m.jack_bytes_r95_entry),
    ("jack_quantum_r95_probe", m.jack_quantum_r95_entry),
    ("jack_defects_r95_probe", m.jack_defects_r95_entry))}
m._jack_r95_lock_release(lock["fd"])
report["A1_pactl_refuses"] = summarise(a1)

# A2: the incident's SIGKILL-at-bound mode (stub sleeps past the gate bound)
(STUB / "pactl").write_text('#!/bin/sh\nsleep 60\n')
os.chmod(STUB / "pactl", 0o755)
m = load()
lock = m._jack_r95_family_lock()
a2 = {}
for k, fn in (("jack_surface_r95_probe", m.jack_surface_r95_entry),
              ("jack_addr_r95_probe", m.jack_addr_r95_entry),
              ("jack_bytes_r95_probe", m.jack_bytes_r95_entry),
              ("jack_quantum_r95_probe", m.jack_quantum_r95_entry),
              ("jack_defects_r95_probe", m.jack_defects_r95_entry)):
    t0 = time.monotonic()
    a2[k] = fn()
    a2[k]["_wall_s"] = round(time.monotonic() - t0, 1)
m._jack_r95_lock_release(lock["fd"])
report["A2_pactl_hangs"] = summarise(a2)
report["A2_wall_s"] = {k: v.get("_wall_s") for k, v in a2.items()}
report["A2_daemon_gate"] = {
    k: {x: (v.get("daemon_gate") or {}).get(x)
        for x in ("ok", "exit_code", "killed_at_bound")}
    for k, v in a2.items()}

# ---------------------------------------------------------------- B
m = load()
orig_build = m._jack_r95_build


def boom(tmp):
    raise RuntimeError("synthetic mid-entry abort")


m._jack_r95_build = boom
b1 = m.jack_surface_r95_entry()
m._jack_r95_build = orig_build
report["B1_except_path"] = {
    "measured": b1.get("measured"), "legs_measured": b1.get("legs_measured"),
    "coverage_blocked": b1.get("coverage_blocked"),
    "failures": b1.get("failures"),
    "census_keys_present": sorted(
        x for x in b1 if x in ("sinks_gone", "sinks_censused",
                               "own_nodes_after",
                               "stream_properties_own_rows",
                               "sinks_gone_note"))}

# F5: the harness-side restore fires from teardown when the arm ran
m = load()
b2 = {"probe": "synthetic", "settings_global_moved": True}
f2 = []
m._jack_r95_teardown(b2, f2, {}, ())
report["B2_restore_on_failure_path"] = {
    "settings_restore_rc": (b2.get("settings_restore") or {}).get("exit_code"),
    "settings_restore_argv": (b2.get("settings_restore") or {}).get("argv"),
    "settings_after_restore_force_quantum":
        (b2.get("settings_after_restore") or {}).get("clock.force-quantum"),
    "failures": f2}

# ---------------------------------------------------------------- C
# Hold the host-global lock from a child, then exercise the dispatch's
# exact expression with a bounded cap.
holder = subprocess.Popen(
    [sys.executable, "-c", (
        "import importlib.util,time\n"
        f"spec=importlib.util.spec_from_file_location('m',r'{SRC}')\n"
        "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "r=m._jack_r95_family_lock()\n"
        "print('held' if r['fd'] is not None else 'failed', flush=True)\n"
        "time.sleep(25)\n")],
    stdout=subprocess.PIPE, text=True)
assert holder.stdout.readline().strip() == "held"
m = load()
lock = m._jack_r95_family_lock(wait_s=2.0)
block = lock["block"]
c1 = {}
for k, fn in (("jack_surface_r95_probe", m.jack_surface_r95_entry),
              ("jack_addr_r95_probe", m.jack_addr_r95_entry),
              ("jack_bytes_r95_probe", m.jack_bytes_r95_entry),
              ("jack_quantum_r95_probe", m.jack_quantum_r95_entry),
              ("jack_defects_r95_probe", m.jack_defects_r95_entry)):
    c1[k] = m._jack_r95_lock_blocked_entry(k, block) if block else fn()
holder.kill()
holder.wait()
report["C1_lock_busy"] = {
    "block": (block or "")[:200],
    "waited_s": lock["waited_s"],
    "holder_text": lock["holder_text"],
    "entries": summarise(c1)}

print(json.dumps(report, indent=1, default=str))
