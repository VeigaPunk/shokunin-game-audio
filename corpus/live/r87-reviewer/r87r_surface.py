#!/usr/bin/env python3
"""r87 reviewer — cross-run verdict-surface diff.

Extracts a curated, volatile-free surface from an r87 receipt (the
fields the encoded laws actually read) and diffs receipts pairwise.
Volatile ids/serials/pids/times/paths are dropped or typed; calibration
numbers (medians, byte counts, ratios) are kept and reported.
"""
import json
import re
import sys

VOLATILE = {"node_id", "object_id", "object_serial", "stream_index",
            "sink", "module_id", "fd", "pid", "wall_s", "at_s", "wait_s",
            "spawn_at_s", "done_at_s", "t", "loadavg", "contention",
            "oracle_at_start", "inventory", "tools", "refs", "ns_leaf",
            "head_hex", "bridge", "seq_port", "foreign_candidates",
            "collision_objects", "default_sink_at_start",
            "default_sink_at_end", "unloads", "probe"}


def scrub_str(s):
    s = re.sub(r"r87a_\d+", "r87a_<pid>", s)
    s = re.sub(r"r87a-\w+", "r87a-<tmp>", s)
    s = re.sub(r"node \d+", "node <n>", s)
    s = re.sub(r"id[:=]\s*\d+", "id=<n>", s)
    s = re.sub(r"seq[:=]\s*\d+", "seq=<n>", s)
    s = re.sub(r"/home/\S+", "<path>", s)
    s = re.sub(r"\d{4,}", "<n>", s)
    return s


def surface(obj, key=None, depth=0):
    if depth > 12:
        return "<deep>"
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in VOLATILE and depth > 0:
                continue
            if k in ("failures", "coverage_blocked", "errors",
                     "error_class", "error_hit", "stdout_head",
                     "stderr_head", "sent", "linger", "log_tail",
                     "blocked", "sinks_gone", "own_nodes_after"):
                out[k] = surface(v, k, depth + 1)
            elif k in ("argv", "stdout", "stderr", "play_err"):
                out[k] = scrub_str(str(v))
            else:
                out[k] = surface(v, k, depth + 1)
        return out
    if isinstance(obj, list):
        return [surface(v, key, depth + 1) for v in obj]
    if isinstance(obj, str):
        return scrub_str(obj)
    return obj


def extract(path):
    d = json.load(open(path))
    ms = d["measurements"]
    surf = {}
    for k, v in ms.items():
        if not k.startswith("pwbind_"):
            continue
        entry = {kk: v.get(kk) for kk in
                 ("failures", "coverage_blocked", "blocked", "sinks_gone",
                  "own_nodes_after")}
        entry["legs"] = surface(v.get("legs") or {})
        surf[k] = entry
    return surf


def flat(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out.update(flat(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = d
    return out


if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    fa, fb = flat(extract(a)), flat(extract(b))
    keys = sorted(set(fa) | set(fb))
    diffs = []
    for k in keys:
        if fa.get(k) != fb.get(k):
            diffs.append({"key": k, "a": fa.get(k), "b": fb.get(k)})
    print(json.dumps({"a": a, "b": b, "keys": len(keys),
                      "diffs": len(diffs), "diff_keys": diffs},
                     indent=1))
