#!/usr/bin/env python3
"""r88-verifier tiered verdict-surface comparator.

Compares two --probe-btwit-r88 receipts and classifies every diff into
exact (verdict-bearing) / named (law-bearing magnitudes) / entry
(teardown projections + failures) / analog (volatile) buckets.

Volatile fields are replaced by a *shape* token (type + list/dict length)
so structural drift still surfaces without id/serial/timing noise.
"""
import json
import re
import sys

VOLATILE_KEYS = {
    # timings / sizes / argv / raw text
    "wall_s", "stdout_bytes", "stderr_bytes", "argv", "stdout", "stderr",
    "stdout_head", "stderr_head", "stdout_raw", "stderr_raw", "stderr_tail",
    "stdout_bytes", "stdout_bytes",
    # host / process state
    "own_pid", "loadavg", "contention", "oracle_at_start", "inventory",
    "tools", "refs", "host_is_quiet", "fixture_runs",
    # ids / serials / module indices
    "module_id", "ids", "members", "ls_ids", "dump_ids", "extra",
    "dump_metadata", "parsed_ids", "got", "predicted", "serial", "own_id",
    "own_serial", "foreign", "foreign_serial", "device_id", "port_id",
    "path", "id", "device", "verified_index", "captured", "recycled",
    "index", "name", "card", "card_id",
    # device prop renderings (recorded, not armed)
    "uuids", "class", "icon", "connected", "paired", "modalias",
    "active_profile",
    # listings that are law-bearing but boot-local in exact content
    "matches", "bluez_objects", "devices", "adapters", "sinks", "cards",
    "files", "media_transport_objects", "substring_hits", "by_type",
    "objects", "top", "pactl", "dump", "cli", "top_frames",
    "last_frame_status_hist", "status_sets", "frames", "sink_meta",
    "sink_pactl", "source_meta", "source_pactl", "pactl_exit",
    "pw_play", "pw_record", "pw_cat", "pw_loopback", "paplay", "parec",
    "pacat", "aplay", "arecord", "ffmpeg",
}

# keys whose diff is verdict-bearing
EXACT_KEYS = {
    "exit_code", "signal", "killed_at_bound", "error_class", "error_hit",
    "rc", "has_pod", "outcome", "linked", "port_objects",
    "own_index_follows", "described", "metadata_described",
    "equals_before", "equals_after", "json_parses", "has_ansi",
    "sink_seen", "monitor_seen", "skipped", "count", "hits",
    "bluez_modules", "audio_uuids", "ls_layout", "info_layout",
    "cli_only", "dump_only", "dump_empty", "vocab", "violations",
    "standalone_lines",
}
# keys whose diff is a law-bearing magnitude (not a fixed verdict token)
NAMED_KEYS = {
    "cli", "dump", "uuid16", "dump_type", "dump_value", "cli_render",
    "cli_has", "bluez5_names", "top_frames", "frames", "attempt",
    "churn_recensus", "matched", "unmatched", "ls_key_count",
    "info_key_count", "dump_count", "sink_seen",
}
# keys whose diff is a teardown/entry projection
ENTRY_KEYS = {
    "failures", "coverage_blocked", "unloads", "sinks_gone",
    "own_nodes_after", "residual_destroy", "blocked",
    "foreign_r88a_nodes", "unloads",
}

STR_NORM = [
    (re.compile(r"r88a_ns2_\d+"), "r88a_ns2_<pid>"),
    (re.compile(r"r88a_ns_\d+"), "r88a_ns_<pid>"),
    (re.compile(r"r88a_\d+_"), "r88a_<pid>_"),
    (re.compile(r"r88arole\d+"), "r88arole<pid>"),
    (re.compile(r"r88a-bogus-\d+"), "r88a-bogus-<pid>"),
    (re.compile(r"id:\d+ seq:\d+"), "id:<n> seq:<n>"),
    (re.compile(r"object \d+"), "object <n>"),
    (re.compile(r"unknown global '\d+'"), "unknown global '<id>'"),
    (re.compile(r"no global \d+"), "no global <id>"),
    (re.compile(r"unknown resource \d+"), "unknown resource <id>"),
    (re.compile(r"remote \d+:"), "remote <n>:"),
    (re.compile(r"id (\d+),"), "id <n>,"),
    (re.compile(r"id = \d+"), "id = <n>"),
    (re.compile(r"object\.serial = \d+"), "object.serial = <n>"),
    (re.compile(r"object\.serial = \"\d+\""), "object.serial = \"<n>\""),
    (re.compile(r"/tmp/[\w.\-/]+"), "/tmp/<path>"),
    (re.compile(r"0x[0-9a-fA-F]+"), "0x<hex>"),
    (re.compile(r"seq:\d+"), "seq:<n>"),
]


def norm_str(s):
    for rx, rep in STR_NORM:
        s = rx.sub(rep, s)
    return s


def shape(v):
    if isinstance(v, dict):
        return {"__shape__": "dict", "n": len(v)}
    if isinstance(v, list):
        return {"__shape__": "list", "n": len(v),
                "types": sorted({type(x).__name__ for x in v})}
    return {"__shape__": type(v).__name__}


KEY_NORM = [
    (re.compile(r"^r88a_ns2_\d+$"), "r88a_ns2_<pid>"),
    (re.compile(r"^r88a_ns_\d+$"), "r88a_ns_<pid>"),
]


def norm_key(k):
    for rx, rep in KEY_NORM:
        if rx.match(k):
            return rep
    return k


def norm(v, key=None):
    if key in VOLATILE_KEYS:
        return shape(v)
    if isinstance(v, dict):
        return {norm_key(k): norm(x, k) for k, x in v.items()}
    if isinstance(v, list):
        return [norm(x, key) for x in v]
    if isinstance(v, str):
        s = norm_str(v)
        # typed-pair serial renderings (recorded, volatile)
        if key == "cli_render" and re.fullmatch(r'"\d{4,}"', s):
            return '"<n>"'
        return s
    if isinstance(v, int) and key == "dump_value" and abs(v) > 9999:
        return "<n>"
    return v


def diff(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append((path + [k], a.get(k, "<absent>"),
                            b.get(k, "<absent>")))
            else:
                diff(a[k], b[k], path + [k], out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, f"len={len(a)}", f"len={len(b)}"))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                diff(x, y, path + [f"[{i}]"], out)
    else:
        if a != b:
            out.append((path, a, b))


def classify(path):
    keys = [p for p in path if not p.startswith("[")]
    for k in reversed(keys):
        if k in ENTRY_KEYS:
            return "entry"
        if k in EXACT_KEYS:
            return "exact"
        if k in NAMED_KEYS:
            return "named"
    return "analog"


def main(fa, fb, label_a, label_b):
    A = json.load(open(fa))["measurements"]
    B = json.load(open(fb))["measurements"]
    buckets = {"exact": [], "named": [], "entry": [], "analog": []}
    for ent in sorted(set(A) | set(B)):
        d = []
        diff(norm(A.get(ent, {})), norm(B.get(ent, {})), [ent], d)
        for path, a, b in d:
            buckets[classify(path)].append((path, a, b))
    print(f"# {label_a} vs {label_b}")
    for cls in ("exact", "named", "entry", "analog"):
        print(f"{cls}: {len(buckets[cls])}")
    for cls in ("exact", "entry"):
        for path, a, b in buckets[cls]:
            print(f"  {cls}: {'/'.join(path)}\n    A={a!r}\n    B={b!r}")
    print("named diffs:")
    for path, a, b in buckets["named"]:
        print(f"  {'/'.join(path)}: A={str(a)[:120]!r} B={str(b)[:120]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2],
                  sys.argv[3] if len(sys.argv) > 3 else "A",
                  sys.argv[4] if len(sys.argv) > 4 else "B"))
