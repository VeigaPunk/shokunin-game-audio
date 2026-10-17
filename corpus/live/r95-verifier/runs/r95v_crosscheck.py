#!/usr/bin/env python3
"""r95v — cross-seat cell re-derivation.

For a curated set of headline cells, pull the value the r95 AUTHOR's green
receipt recorded and every value the TRACKED cross-seat receipts (r95-scout,
r95-boundary — both committed at HEAD) recorded under the same key name.
Prints a comparison so the verifier can see which cells re-derive identically.
"""
import glob
import json
import sys

AUTHOR = ("/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r95/corpus/live/runs/"
          "20261016T085527000328Z-jack-r95/measurements.json")
CROSS = ("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
         "r95-verifier/tree/corpus/live/{seat}/receipts/*.json")

# key -> (label, author side)
CELLS = [
    ("version_ints", "a_avail", "JACK version quadruple"),
    ("export_count", "a_avail", "jack_* export count"),
    ("flags", "s_shape", "port flags (all five)"),
    ("request_monitor_rc", "s_shape", "monitor API rc"),
    ("monitoring_input", "s_shape", "monitoring_input"),
    ("ensure_monitor_rc", "s_shape", "ensure_monitor rc"),
    ("out_connected", "s_shape", "autoconnect absent"),
    ("out_connections", "s_shape", "connection list"),
    ("group", "s_shape", "node.group"),
    ("media_category", "s_shape", "media.category"),
    ("always_process", "s_shape", "node.always-process"),
    ("connect_rc", "addr", "jack_connect rc"),
    ("bufsize_activated", "quantum", "activated buffer size"),
    ("bufsize_after_set_active", "quantum", "live set"),
    ("bufsize_active", "quantum", "second client"),
    ("force_quantum", "quantum", "node.force-quantum"),
    ("lat_cap", "defects", "latency cap"),
    ("lat_play", "defects", "latency play"),
    ("total", "defects", "latency total"),
    ("state_after_start", "defects", "transport state"),
    ("xrun_cbs", "defects", "xrun callback count"),
    ("stall_cycles", "defects", "stall cycles"),
    ("get_client_value", "defects", "metadata round-trip"),
    ("get_missing_rc", "defects", "missing key rc"),
]


def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, o


def leafvals(obj, key):
    out = []
    for p, v in walk(obj):
        if p.rsplit("/", 1)[-1].split("[")[0] == key:
            out.append(v)
    return out


def main():
    author = json.load(open(AUTHOR))["measurements"]
    cross = {}
    for seat in ("r95-scout", "r95-boundary"):
        for p in sorted(glob.glob(CROSS.format(seat=seat))):
            cross[f"{seat}/{p.rsplit('/', 1)[-1]}"] = json.load(open(p))
    rows = []
    for key, side, label in CELLS:
        # author's recorded values for this key
        avals = []
        for entry, e in author.items():
            if "r95" not in entry:
                continue
            if side == "a_avail" and entry != "jack_surface_r95_probe":
                continue
            if side == "s_shape" and entry != "jack_surface_r95_probe":
                continue
            if side == "addr" and entry != "jack_addr_r95_probe":
                continue
            if side == "quantum" and entry != "jack_quantum_r95_probe":
                continue
            if side == "defects" and entry != "jack_defects_r95_probe":
                continue
            avals += leafvals(e, key)
        cvals = {}
        for name, obj in cross.items():
            v = leafvals(obj, key)
            if v:
                cvals[name] = v
        rows.append((key, label, avals, cvals))
    for key, label, avals, cvals in rows:
        uniq_a = sorted({json.dumps(v) for v in avals})
        uniq_c = sorted({json.dumps(v) for v in
                         [x for vs in cvals.values() for x in vs]})
        inter = sorted(set(uniq_a) & set(uniq_c))
        print(f"\n## {key}  ({label})")
        print(f"   author : {uniq_a[:8]}{' ...' if len(uniq_a) > 8 else ''}")
        print(f"   cross  : {uniq_c[:8]}{' ...' if len(uniq_c) > 8 else ''}")
        print(f"   shared : {inter}")
        for name, vs in sorted(cvals.items()):
            u = sorted({json.dumps(v) for v in vs})
            if not set(u) & set(uniq_a):
                print(f"     differs in {name}: {u[:6]}")


if __name__ == "__main__":
    sys.exit(main())
