#!/usr/bin/env python3
"""r87 simplifier — executed evidence for the FINDINGS (recorded-only /
unarmed / fail-open surfaces; none of these is a fold item — deleting
recorded data would change receipt content).

F1: the m_sysex "stays up" arm fires only on rc==0; a crash (rc!=0)
    is indistinguishable from the harness SIGTERM exit (both rc=1 on
    this host — receipts) and passes silently; `exited_before_observe`
    is recorded but never armed.
F5: the p_zero/p_zero_prop/p_noauto verdict subscripts `legs[name]
    ["snaps"]` directly; a watch spawn error yields a rec WITHOUT that
    key -> KeyError (the entry raises instead of recording a failure).
"""
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "r87_base", HERE / "base-measure_audio.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

print("F1 arm domain — the verdict `leg.get('exit_code') == 0`:")
for rc in (0, 1, -15, None):
    print(f"   exit_code={rc!r:6} -> arm fires: {rc == 0}")
print("   receipts: every watch leg (m_sysex/m_ump/m_p_r/m_r_p/m_midi_r/"
      "p_zero) recorded exit_code=1, killed=None, "
      "exited_before_observe=False on BOTH runs -> the arm cannot fire "
      "for a harness kill and cannot fire for a crash either; the "
      "recorded exited_before_observe marker is never armed.")

print()
print("F5 spawn-error shape of _pwbind_r87_watch:")
rec = mod._pwbind_r87_watch("r87a_probe_missing", ["/nonexistent/xyz"])
print("   rec keys:", sorted(rec))
try:
    rec["snaps"]
    print("   direct ['snaps'] subscript: OK (no error)")
except KeyError as exc:
    print(f"   direct ['snaps'] subscript raises KeyError: {exc!r}")
print("   the target verdict loops `for s in legs[name]['snaps']` for "
      "p_zero/p_zero_prop/p_noauto -> a spawn error would raise instead "
      "of appending a failure (fail-closed by crash, not by verdict).")

print()
print("F-recorded-only fields (recorded in the receipts, read by no "
      "verdict):")
import json
for run in ("20261016T070036115509Z-pwbind-r87",
            "20261016T070305393338Z-pwbind-r87"):
    j = json.loads((HERE.parents[3] / "corpus/live/runs" / run /
                    "measurements.json").read_text())
    modes = j["measurements"]["pwbind_modes_r87_probe"]["legs"]
    cli = j["measurements"]["pwbind_cli_r87_probe"]["legs"]
    tgt = j["measurements"]["pwbind_target_r87_probe"]["legs"]
    midi = j["measurements"]["pwbind_midi_r87_probe"]["legs"]
    print(f"   {run[-18:]}: binaries.pw_cat_sha={modes['binaries']['pw_cat_sha']!r} "
          f"m_p_r.recorded_file={modes['m_p_r']['recorded_file']} "
          f"m_p_r.last={modes['m_p_r']['last']} "
          f"collision_objects={tgt['collision_objects']} "
          f"tap_windows={cli['tap_windows']} "
          f"player_alive_at_end={cli['player_alive_at_end']} "
          f"player_exit={cli['player_exit']} tap_exit={cli['tap_exit']} "
          f"pin.bridge={midi['pin']['bridge']!r} pin.seq_port={midi['pin']['seq_port']!r}")
sys.exit(0)
