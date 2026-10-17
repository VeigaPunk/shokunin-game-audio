#!/usr/bin/env python3
"""r77 verifier — N-row: is `--probe-capture-r77` in the mutual-exclusion
guard?

The fixture's argparse guard is
`if sum([...args.probe_capture_r76]) > 1: parser.error("choose one probe
mode")`. This script imports the fixture, STUBS every capture entry so no
audio leg can run, then calls main() with two probe flags and records
whether the guard fires. Zero device side effects.
"""
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = REPO / "corpus/live/r77-verifier"
ENTRIES = ("capture_target_loss_r77_entry", "capture_source_lattice_r77_entry",
           "capture_readers_r77_entry", "capture_arecord_sever_r77_entry",
           "capture_split_sentinel_r77_entry", "capture_format_axis_r77_entry",
           "capture_gate_r76_entry", "capture_bounded_r76_entry",
           "capture_sever_r76_entry", "capture_name_axis_r76_entry",
           "capture_device_axis_r76_entry", "capture_roundtrip_r76_entry")


def trial(flags):
    spec = importlib.util.spec_from_file_location(
        "ma_probe", REPO / "corpus/fixtures/measure_audio.py")
    ma = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ma)
    for name in ENTRIES:
        if hasattr(ma, name):
            setattr(ma, name,
                    (lambda n: (lambda: {"probe": n, "stub": True,
                                         "failures": []}))(name))
    sys.argv = ["measure_audio.py", *flags]
    sys.stderr = open("/dev/null", "w")
    try:
        rc = ma.main()
        return {"flags": flags, "guard_fired": False, "main_rc": rc}
    except SystemExit as exc:
        return {"flags": flags, "guard_fired": exc.code == 2,
                "system_exit_code": exc.code}


def main():
    entry = {"probe": "r77-verifier probe-mode guard check",
             "trials": [], "failures": []}
    for flags in (["--probe-capture-r76", "--probe-consumers2-r75"],
                  ["--probe-capture-r77", "--probe-capture-r76"],
                  ["--probe-capture-r77", "--probe-consumers2-r75"],
                  ["--probe-capture-r77"]):
        entry["trials"].append(trial(flags))
    for t in entry["trials"]:
        two_flags = len([f for f in t["flags"] if f.startswith("--probe")]) > 1
        if two_flags and not t.get("guard_fired"):
            entry["failures"].append(
                f"{' '.join(t['flags'])}: two probe modes accepted — the "
                f"guard did not fire")
        if two_flags and t.get("guard_fired"):
            entry.setdefault("guard_fires_for", []).append(t["flags"])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "v7_guard.json").write_text(json.dumps(entry, indent=2) + "\n")
    print(json.dumps({"receipt": str(OUT / "v7_guard.json"),
                      "failures": entry["failures"],
                      "trials": entry["trials"]}))


if __name__ == "__main__":
    main()
