#!/usr/bin/env python3
"""Normalize volatile fields out of a --probe-module-r80 receipt so two
runs compare on the non-volatile body only.

Volatile by construction (r80 code stamps them per-process / per-load):
  - pid-stamped names        r80md_<pid>*  incl. r80md_desc_<pid>_marker
  - per-load module ids      module_id, pulse_module_id, destroyed_id,
                             stdout_tail when it IS the returned index,
                             sink_input.index / .sink
  - pw-dump object ids       object_id, object_serial, client_id
  - this process's pid       contention.own_pid
  - measured waits           *_waited_s keys
  - tmpdir names             module-r80-topo-XXXXXX inside tail labels
Everything else (leg names, booleans, error classes, edge sets modulo
the pid tag, failures lists, SPECS measurements) is the contract under
proof: any post-normalization difference rejects the fold.
"""
import json
import re
import sys

TAG = re.compile(r"r80md_(?:desc_)?\d+")
TMP = re.compile(r"module-r80-topo-[A-Za-z0-9_]+")

VOL_KEYS = {
    "module_id", "pulse_module_id", "object_id", "object_serial",
    "client_id", "destroyed_id", "index", "sink", "own_pid",
    "sink_waited_s", "node_waited_s", "edge_a_waited_s",
    # foreign module activity on the host between the two snapshots
    "module_count_before", "module_count_after",
    # tap windows: the tag tone's frequency is PID-DERIVED
    # (PLAYBACK_R78_TONE_L_HZ = 997 + (pid % 4) * 211), so the measured
    # dominant freq + Hann-corrected amplitude are per-process data;
    # the verdict fields (mine/audio/carries_tone/...) stay literal.
    "f_l", "f_r", "a_l", "a_r", "peak_l", "peak_r",
}


def norm(node, key=None):
    if isinstance(node, dict):
        return {norm_str(str(k)): norm(v, k) for k, v in node.items()}
    if isinstance(node, list):
        return [norm(v, key) for v in node]
    return norm_scalar(node, key)


def norm_str(s):
    return TMP.sub("<tmp>", TAG.sub("r80md_<pid>", s))


def norm_scalar(v, key):
    if isinstance(v, str):
        v = norm_str(v)
        if key in VOL_KEYS or (key == "stdout_tail" and v.isdigit()):
            return "<v>"
        return v
    if key in VOL_KEYS:
        return "<v>"
    return v


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    with open(src) as f:
        data = json.load(f)
    with open(dst, "w") as f:
        json.dump(norm(data), f, indent=2, sort_keys=False)
        f.write("\n")
