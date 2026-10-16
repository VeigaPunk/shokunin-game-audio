#!/usr/bin/env python3
"""r84 REVIEWER — compare a fresh reviewer run of the pinned committed
blob against the committed author receipts, leaf by leaf, with the same
volatile-path normalization the audit receipt uses.

Usage: python3 r84r_compare.py <fresh measurements.json> [<baseline>]
"""
import json
import re
import sys
from pathlib import Path

ENTRIES = ("alsapw_dev_lattice_r84_probe", "alsapw_pw_args_r84_probe",
           "alsapw_pulseprop_r84_probe", "alsapw_pactl_write_r84_probe",
           "alsapw_monstream_r84_probe", "alsapw_negctl_r84_probe")
VOLATILE = ("pid", "index", "serial", "id", "path", "file", "wait_s",
            "wall_s", "tmp", "loadavg", "at_s", "client.id", "object.id",
            "object.serial", "application.process.id", "module_id",
            "a_killed_at_s", "stream_wait_s", "spawn_wait", "dur_s",
            "wall", "stderr", "stdout", "hit", "name", "tag", "argv",
            "byte", "bytes", "size", "lufs", "centroid", "peak", "rms",
            "timestamp", "u", "elapsed", "pulse.attr", "node.driver-id",
            "series[", "/state", "/first_starts", "hold", "unloads",
            "contention", "oracle_at_start", "inventory", "tools",
            "pcm_state", "loads", "role_reset", "reset_sink", "sink_index",
            "ns2_index", "note", "skipped", "free_pcm", "held_pcm")
BENIGN = ("respawn_tap_series_tail[", "/sig/windows[")


def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, o


def is_volatile(p):
    if any(tok in p for tok in VOLATILE):
        return True
    if any(tok in p for tok in BENIGN):
        return p.endswith(("/a", "/b", "/at_s", "][0]", "][1]")) or \
            "respawn_tap_series_tail" in p
    return False


def norm(v):
    if isinstance(v, str):
        return re.sub(r"\d{6,}", "<n>", v)
    if isinstance(v, int) and v > 100000:
        return "<index>"
    return v


def main():
    fresh = json.loads(Path(sys.argv[1]).read_text())["measurements"]
    base_p = sys.argv[2] if len(sys.argv) > 2 else \
        "corpus/live/r84-author/runs/run1/measurements.json"
    base = json.loads(Path(base_p).read_text())["measurements"]
    print(f"fresh: {sys.argv[1]}")
    print(f"base : {base_p}")
    total = 0
    for e in ENTRIES:
        fa = dict(leaves(fresh[e]["legs"]))
        ba = dict(leaves(base[e]["legs"]))
        diffs = []
        for p in sorted(set(fa) - set(ba)):
            if not is_volatile(p):
                diffs.append(f"{p}: only fresh = {fa[p]!r}")
        for p in sorted(set(ba) - set(fa)):
            if not is_volatile(p):
                diffs.append(f"{p}: only base = {ba[p]!r}")
        for p in set(fa) & set(ba):
            if is_volatile(p):
                continue
            if norm(fa[p]) != norm(ba[p]):
                diffs.append(f"{p}: fresh={fa[p]!r} base={ba[p]!r}")
        nlegs_f = len(fresh[e]["legs"])
        nlegs_b = len(base[e]["legs"])
        print(f"\n== {e}: legs fresh={nlegs_f} base={nlegs_b}, "
              f"failures fresh={fresh[e].get('failures')}")
        print(f"   non-volatile leaf diffs: {len(diffs)}")
        for d in diffs[:12]:
            print("   -", d)
        total += len(diffs)
    print(f"\nTOTAL non-volatile leaf diffs: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
