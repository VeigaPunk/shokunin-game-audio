#!/usr/bin/env python3
"""r84 verifier — tiered verdict-surface comparator (r83 convention).

Usage: surface.py A.json B.json [label]

Tiers
  exact : the verdict surface — rc/signal/error_class/error_hit/
          killed_at_bound/unknown_pcm_name/stderr/stdout/arm/out.exists/
          rate/riff/unsupported/stream-leaf volume + semantic props/
          suspend rows/tap_exit/player_exit/sig.exists ...
  named : coarse law outcomes derived from analog numbers — gain-law bucket
          from `ratio`, sticky tap median, volume value/percent, sig window
          signature set.
  analog: never exact-diffed (timing, amps, series, pids, object indices,
          stream cork flags).

Normalization collapses pid runs, pactl/pw object indices, tmp paths and
seat namespaces (r84a_/r84v_/r84arole<pid>) to placeholders.
"""
import json
import re
import sys

ANALOG_KEYS = {
    "wall_s", "dur_s", "series", "base_amp", "post_amp", "muted_amp",
    "restored_amp", "stream_wait_s", "stream_a_wait_s", "stream_b_wait_s",
    "parec_wall_s", "respawn_tap_series_tail", "out_bytes_at_kill",
    "loadavg", "spawn1_wait_s", "respawn_wait_s", "repaired_wait_s",
    "a_killed_at_s", "wake_wait_s", "hold_note", "pcm_state_at_probe",
    "corked", "player_a_pid", "player_b_pid", "pid", "a_pid", "b_pid",
    "stream_index", "ns2_index", "sink_index", "hold_exit", "so_wait_s",
    # realized-state fields the author's own two runs disagree on
    # (leaf volume at sample time; pw node state at sample time):
    "volume", "state",
}
ID_KEYS = {                       # volatile object identifiers
    "index", "sink", "source", "object_id", "object.id", "client.id",
    "factory.id", "node.id", "device.id", "node.driver-id",
    "application.process.id", "application.process.session-id",
    "source_output_index",
}
ANALOG_OUT_KEYS = {
    "bytes", "data_actual", "data_declared", "frames", "nz_rows", "bursts",
    "first_starts", "peak",
}
VOLATILE_PROP_KEYS = {"client.id", "factory.id", "object.id", "object.serial",
                      "node.id", "device.id", "node.driver-id",
                      "application.process.id",
                      "application.process.session-id", "clock.quantum-limit",
                      "pulse.server.type", "config.name", "client.api"}

PID = re.compile(r"\b\d{5,}\b")
PATH = re.compile(r"/home/vgpnk/Projects/shokunin/tmp/[^\s'\"]+")
SEAT = re.compile(r"r84[av][A-Za-z0-9_]*?\d{5,}")
ANALOG = "<ANALOG>"
IDV = "<ID>"


def norm_str(s):
    s = PATH.sub("<TMP>", s)
    s = SEAT.sub("r84<SEAT>", s)
    s = PID.sub("<N>", s)
    return s


def proj(k, v):
    if k in ANALOG_KEYS:
        return ANALOG
    if k in ID_KEYS:
        return IDV
    if k == "out" and isinstance(v, dict):
        return {kk: (ANALOG if kk in ANALOG_OUT_KEYS else proj(kk, vv))
                for kk, vv in v.items()}
    if k == "sig" and isinstance(v, dict):
        return {"exists": v.get("exists"),
                "unsupported": v.get("unsupported"), "windows": ANALOG}
    if k in ("properties", "props") and isinstance(v, dict):
        return {kk: norm_str(str(x)) for kk, x in v.items()
                if kk not in VOLATILE_PROP_KEYS
                and not kk.startswith("pulse.attr.")}
    if isinstance(v, dict):
        return {kk: proj(kk, vv) for kk, vv in v.items()}
    if isinstance(v, list):
        return [proj(None, x) for x in v]
    if isinstance(v, str):
        return norm_str(v)
    return v


def project(rec):
    if not isinstance(rec, dict):
        return rec, None
    exact, named = {}, {}
    for k, v in rec.items():
        if k == "ratio" and isinstance(v, (int, float)):
            named["ratio_x"] = f"x{round(v, 6)}"
        elif k == "respawn_tap_med" and isinstance(v, (int, float)):
            named["respawn_tap_med"] = int(round(v))
        elif k == "volume_value" and isinstance(v, (int, float)):
            named["volume_value"] = int(v)
        elif k == "volume_percent":
            named["volume_percent"] = str(v)
        else:
            p = proj(k, v)
            if k == "sig" and isinstance(v, dict):
                wins = [w.get("sig") for w in v.get("windows", [])
                        if isinstance(w, dict)]
                named["sig_set"] = ",".join(sorted({w for w in wins if w}))
            exact[k] = p
    return exact, named


def legs(doc):
    m = doc["measurements"] if "measurements" in doc else doc
    out = {}
    for entry, e in m.items():
        if "r84" not in entry or not isinstance(e, dict) or "legs" not in e:
            continue
        for leg, rec in e["legs"].items():
            out[f"{entry}/{leg}"] = rec
    return out


def main():
    a = json.load(open(sys.argv[1]))
    b = json.load(open(sys.argv[2]))
    label = sys.argv[3] if len(sys.argv) > 3 else "AB"
    la, lb = legs(a), legs(b)
    keys = sorted(set(la) | set(lb))
    ex_diffs, nm_diffs = [], []
    for k in keys:
        if k not in la or k not in lb:
            ex_diffs.append((k, "<missing>", "<missing>"))
            continue
        ea, na = project(la[k])
        eb, nb = project(lb[k])
        if ea != eb:
            ex_diffs.append((k, json.dumps(ea, sort_keys=True),
                             json.dumps(eb, sort_keys=True)))
        if na != nb:
            nm_diffs.append((k, json.dumps(na, sort_keys=True),
                             json.dumps(nb, sort_keys=True)))
    print(f"# {label}: legs A={len(la)} B={len(lb)} keys={len(keys)}")
    print(f"# exact diffs: {len(ex_diffs)}   named diffs: {len(nm_diffs)}")
    for k, x, y in ex_diffs:
        print(f"EXACT {k}\n  A={x[:900]}\n  B={y[:900]}")
    for k, x, y in nm_diffs:
        print(f"NAMED {k}\n  A={x[:400]}\n  B={y[:400]}")
    return 1 if (ex_diffs or nm_diffs) else 0


if __name__ == "__main__":
    sys.exit(main())
