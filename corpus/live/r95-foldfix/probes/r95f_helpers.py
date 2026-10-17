"""r95 foldfix — narrow helper probe (no family run, no host mutation
beyond the lock file and one `pactl info`). Imports the FIXED worktree
fixture as a module and exercises the new/changed helpers."""
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SRC = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/fixtures/measure_audio.py")
spec = importlib.util.spec_from_file_location("ma_r95f", SRC)
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

out = {}

# 1. daemon gate on the (restarted) daemon
g = ma._jack_r95_daemon_gate()
out["daemon_gate"] = {"ok": g.get("ok"), "rc": g.get("exit_code"),
                      "killed": g.get("killed_at_bound"),
                      "wall_s": g.get("wall_s"), "block": g.get("block")}

# 2. probe-state classification (F4) — synthetic records, no daemon
out["probe_state"] = {
    "ok": ma._jack_r95_probe_state({"json": {"version_ints": [3, 1, 6, 8]}}),
    "open_timeout": ma._jack_r95_probe_state(
        {"killed_at_bound": True, "wall_s": 10.0, "stdout_bytes": 0,
         "json": None}),
    "no_daemon": ma._jack_r95_probe_state(
        {"json": None, "exit_code": 3, "error_class": "jack_r95_no_daemon",
         "error_hit": "Could not connect to JACK server"}),
    "no_record": ma._jack_r95_probe_state(
        {"json": None, "exit_code": 1, "stderr": "boom", "stdout": ""}),
}

# 3. host-global lock: path, acquire, cross-tree exclusion (bounded),
#    stale-text handling. The waiter runs from a DIFFERENT directory to
#    prove the path does not move with the tree.
lock = ma._jack_r95_family_lock()
out["lock_path"] = lock["path"]
out["lock_acquired"] = lock["fd"] is not None
out["lock_stale_text"] = lock["stale_text"]
waiter = subprocess.run(
    [sys.executable, "-c", (
        "import importlib.util,sys,json\n"
        f"spec=importlib.util.spec_from_file_location('m',r'{SRC}')\n"
        "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "r=m._jack_r95_family_lock(wait_s=2.0)\n"
        "print(json.dumps({'acquired': r['fd'] is not None,"
        " 'block': r['block'], 'waited_s': r['waited_s'],"
        " 'holder_text': r['holder_text']}))\n")],
    capture_output=True, text=True, cwd="/home/vgpnk/Projects/shokunin",
    timeout=60)
out["lock_waiter_other_tree"] = json.loads(waiter.stdout.strip().splitlines()[-1])

# 4. stale holder: write a dead pid's text under the held lock, release,
#    re-acquire -> stale_text must be recorded, file truncated on release
dead = subprocess.Popen(["/bin/true"])
dead.wait()
Path(lock["path"]).write_text(f"pid={dead.pid} ns=r95a_ns_0 role=r\n")
ma._jack_r95_lock_release(lock["fd"])
out["lock_file_after_release"] = Path(lock["path"]).read_text()
lock2 = ma._jack_r95_family_lock()
out["lock2_acquired"] = lock2["fd"] is not None
out["lock2_stale_text"] = lock2["stale_text"]
out["lock2_stale_pid_dead"] = lock2.get("stale_pid_dead")
ma._jack_r95_lock_release(lock2["fd"])

# 5. metadata census keeps the subject dimension (F1)
mrec = ma._jack_r95_meta_rows("settings")
out["meta_rows"] = {"keys": sorted(mrec.get("rows") or {})[:4],
                    "subjects": sorted((mrec.get("rows_by_subject") or {})),
                    "row_count": mrec.get("row_count"),
                    "subject_count": mrec.get("subject_count"),
                    "force_quantum": (mrec.get("rows") or {})
                    .get("clock.force-quantum", {}).get("value")}

# 6. block path carries legs + census + measured=false (F2/C1/F3), using a
#    synthetic entry and an EMPTY loads dict (nothing to unload).
entry = {"probe": "synthetic", "settings_at_start": {}}
failures = []
legs = {"a_avail": {"synthetic": True}}
blk = ma._jack_r95_block(entry, failures, "synthetic block", {}, [],
                         legs, census=["r95f_never_loaded"])
out["block_entry"] = {
    "has_legs": "legs" in blk, "legs": blk.get("legs"),
    "measured": blk.get("measured"), "blocked": blk.get("blocked"),
    "sinks_gone": blk.get("sinks_gone"),
    "sinks_censused": blk.get("sinks_censused"),
    "own_nodes_after": blk.get("own_nodes_after"),
    "stream_properties_own_rows": blk.get("stream_properties_own_rows"),
    "coverage_blocked": blk.get("coverage_blocked"),
    "failures": blk.get("failures")}

# 7. F5 restore is a no-op unless the entry says the arm moved the key
e2 = {"probe": "synthetic"}
f2 = []
ma._jack_r95_settings_restore(e2, f2)
out["restore_noop"] = {"keys": sorted(e2), "failures": f2}

# 8. witness gate: readable vs unreadable snapshot
e3 = {}
out["witness_ok"] = ma._jack_r95_witness_gate(
    e3, "leg", {"error": None, "graph_ok": True})
out["witness_bad"] = ma._jack_r95_witness_gate(
    e3, "leg", {"error": "TimeoutExpired: pw-dump", "graph_ok": False})
out["witness_blocks"] = e3.get("coverage_blocked")

# 9. lock-blocked entry shape
lb = ma._jack_r95_lock_blocked_entry("jack_surface_r95_probe", "busy")
out["lock_blocked_entry"] = lb

print(json.dumps(out, indent=1, default=str))
