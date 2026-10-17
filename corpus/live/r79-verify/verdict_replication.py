#!/usr/bin/env python3
"""r79-verifier: verdict-key replication across the four receipts.

Compares every verdict-bearing cell (entry blocked/coverage/failures/
teardown, per-leg topology unions + expectations, outcomes, tap verdicts,
matrix signatures, latency values, filter-chain verdicts) after
normalizing pid-stamped probe names. Output: differing keys only.
"""
import json
import re
import sys

PAT = [
    (re.compile(r"(r79lb_[A-Za-z0-9_]*?_)\d+"), r"\1<pid>"),
    (re.compile(r"(r79lb_)\d+(_)"), r"\1<pid>\2"),
    (re.compile(r"(r79fc_)\d+"), r"\1<pid>"),
    (re.compile(r"(r79exp_)\d+"), r"\1<pid>"),
    (re.compile(r"pw-loopback-\d+"), "pw-loopback-<pid>"),
    (re.compile(r"loopback-\d+-\d+"), "loopback-<pid>-<n>"),
]


def n(v):
    if isinstance(v, str):
        for rx, rep in PAT:
            v = rx.sub(rep, v)
    return v


def norm(o):
    if isinstance(o, dict):
        return {n(k): norm(v) for k, v in o.items()}
    if isinstance(o, list):
        return [norm(i) for i in o]
    return n(o)


def verdicts(p):
    d = json.load(open(p))["measurements"]
    out = {}
    for k, v in d.items():
        if not k.endswith("_r79_probe"):
            continue
        s = k.replace("_r79_probe", "")
        for key in ("blocked", "coverage_blocked", "failures",
                    "own_nodes_after", "sinks_gone", "named_outcomes",
                    "confound_observed"):
            out[f"{s}.{key}"] = norm(v.get(key))
        for ln, leg in (v.get("legs") or {}).items():
            if not isinstance(leg, dict):
                out[f"{s}.{ln}"] = norm(leg)
                continue
            for key in ("outcome", "input_producers_union",
                        "output_consumers_union", "producers_union",
                        "consumers_union", "expected_producers",
                        "expected_consumers", "target_object_lies",
                        "target_requested", "target_object_advertised",
                        "node_latency", "latency_param_verdict",
                        "expect_met", "loader_rc", "verdict",
                        "killed_at_bound", "exit_code", "error_class",
                        "fed", "stream_capture_sink", "media_role",
                        "chain_nodes", "stderr_class", "reply_verdict"):
                if key in leg:
                    out[f"{s}.{ln}.{key}"] = norm(leg[key])
            for key in ("tap", "tap_flag_sink", "content", "two_tone"):
                t = leg.get(key)
                if isinstance(t, dict):
                    for sub in ("bound_to_target", "ran", "carries_tone",
                                "mine_windows", "never_bound",
                                "mix_signature", "stereo_signature"):
                        if sub in t:
                            out[f"{s}.{ln}.{key}.{sub}"] = norm(t[sub])
            if "mix_half_gain_ratio" in leg:
                out[f"{s}.{ln}.ratio"] = leg["mix_half_gain_ratio"]
    return out


def main():
    runs = {}
    for p in sys.argv[1:]:
        ts = p.split("/")[-2] + "/" + p.split("/")[-1][:15]
        runs[ts] = verdicts(p)
    keys = sorted(set().union(*[set(t) for t in runs.values()]))
    diffs = [k for k in keys
             if len({json.dumps(runs[t].get(k), sort_keys=True)
                     for t in runs}) > 1]
    print(f"verdict keys compared: {len(keys)} | differing after pid "
          f"normalization: {len(diffs)}")
    for k in diffs:
        print("DIFF", k)
        for t in runs:
            print("   ", t, runs[t].get(k))
    print("tags:", list(runs))


if __name__ == "__main__":
    main()
