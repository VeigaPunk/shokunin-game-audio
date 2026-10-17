#!/usr/bin/env python3
"""r79-verifier independent field comparison.

Compares the r79 receipts (author B/C, verifier runs) two ways:

  1. canonical projection: the whole receipt with pid-stamped names
     normalized, run-local identity + timing leaves dropped, and long
     sample/window lists collapsed to structural summaries. Any
     remaining difference is either a measured value (printed) or a
     verdict/structure difference (flagged).
  2. curated verdict cells: the exact cells the author's report pins,
     printed side by side for all receipts.

No shared code with corpus/live/r79-author/receipt-BC-diff.txt.
"""
import json
import re
import sys
from pathlib import Path

VOLATILE_KEYS = {
    "when_s", "at_s", "wall_s", "waited_s", "monitor_waited_s",
    "module_id", "client_id", "node_id", "global_id",
    "pactl_exit", "exit", "own_pid", "fixture_runs",
}
PID_TAIL_RE = re.compile(r"(r79lb_[A-Za-z0-9_]*?_)\d+")
PID_HEAD_RE = re.compile(r"(r79lb_)\d+(_)")
PID2_RE = re.compile(r"(r79fc_)\d+")
PID3_RE = re.compile(r"(r79exp_)\d+")
LG_RE = re.compile(r"loopback-\d+-\d+")
PG_RE = re.compile(r"pw-loopback-\d+")
TMP_RE = re.compile(r"/tmp/(?:r79fc|capture-r79|r79lb)[A-Za-z0-9_.-]*")
TS_RE = re.compile(r"\[\d\d:\d\d:\d\d\.\d+\]")
PTR_RE = re.compile(r"0x[0-9a-f]+")


def norm(v):
    if isinstance(v, str):
        v = PID_TAIL_RE.sub(r"\1<pid>", v)
        v = PID_HEAD_RE.sub(r"\1<pid>\2", v)
        v = PID2_RE.sub(r"\1<pid>", v)
        v = PID3_RE.sub(r"\1<pid>", v)
        v = LG_RE.sub("loopback-<pid>-<n>", v)
        v = PG_RE.sub("pw-loopback-<pid>", v)
        v = TMP_RE.sub("/tmp/<tmp>", v)
        v = TS_RE.sub("[<ts>]", v)
        v = PTR_RE.sub("<ptr>", v)
        return v
    return v


def is_window_list(lst):
    return (len(lst) > 8 and all(isinstance(i, dict) and "at_s" in i
                                 for i in lst))


def summarize_windows(lst):
    out = {"n": len(lst)}
    for key in ("mine", "audio"):
        vals = [i.get(key) for i in lst]
        out[key + "_count"] = sum(1 for v in vals if v)
    for key in ("peak_l", "peak_r"):
        vals = [i.get(key) or 0 for i in lst]
        out[key + "_max"] = max(vals) if vals else 0
    if any("f_l" in i for i in lst):
        out["f_l_any"] = sorted({i.get("f_l") for i in lst if i.get("f_l")})
        out["f_r_any"] = sorted({i.get("f_r") for i in lst if i.get("f_r")})
    return out


def canon(x, path=()):
    if isinstance(x, dict):
        return {norm(k): canon(v, path + (norm(k),))
                for k, v in x.items() if k not in VOLATILE_KEYS}
    if isinstance(x, list):
        if is_window_list(x):
            return summarize_windows(x)
        return [canon(i, path + (str(idx),)) for idx, i in enumerate(x)]
    return norm(x)


def walk_diff(a, b, path="$"):
    """Yield (path, a, b) for every differing leaf/collection."""
    if type(a) is not type(b):
        yield path, a, b
        return
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                yield f"{path}.{k}", "<absent>", b[k]
            elif k not in b:
                yield f"{path}.{k}", a[k], "<absent>"
            else:
                yield from walk_diff(a[k], b[k], f"{path}.{k}")
        return
    if isinstance(a, list):
        if len(a) != len(b):
            yield f"{path}[]", f"len={len(a)}", f"len={len(b)}"
            return
        for idx, (x, y) in enumerate(zip(a, b)):
            yield from walk_diff(x, y, f"{path}[{idx}]")
        return
    if isinstance(a, float) and isinstance(b, float):
        if abs(a - b) > 1e-9:
            yield path, a, b
        return
    if a != b:
        yield path, a, b


def load(p):
    return canon(json.loads(Path(p).read_text()))


def cells(d):
    """Curated verdict cells, keyed by path."""
    m = d["measurements"]
    out = {}
    for name, e in m.items():
        if not name.endswith("_r79_probe"):
            continue
        short = name.replace("_r79_probe", "")
        out[f"{short}.blocked"] = e.get("blocked")
        out[f"{short}.failures"] = e.get("failures")
        out[f"{short}.coverage_blocked"] = e.get("coverage_blocked")
        out[f"{short}.own_nodes_after"] = e.get("own_nodes_after")
        out[f"{short}.sinks_gone"] = e.get("sinks_gone")
        for lname, leg in (e.get("legs") or {}).items():
            base = f"{short}.{lname}"
            if not isinstance(leg, dict):
                out[base] = leg
                continue
            for key in ("exit_code", "killed_at_bound", "error_class",
                        "fed", "input_producers_union",
                        "output_consumers_union", "producers_union",
                        "consumers_union", "expected_producers",
                        "expected_consumers", "target_object_advertised",
                        "target_requested", "node_latency",
                        "latency_param_verdict", "outcome",
                        "stream_capture_sink", "media_role",
                        "expect_met", "loader_rc", "verdict"):
                if key in leg:
                    out[f"{base}.{key}"] = leg[key]
            tap = leg.get("tap")
            if isinstance(tap, dict):
                out[f"{base}.tap.bound"] = tap.get("bound_to_target")
                out[f"{base}.tap.ran"] = tap.get("ran")
                out[f"{base}.tap.carries_tone"] = tap.get("carries_tone")
                out[f"{base}.tap.mine"] = tap.get("mine_windows")
                out[f"{base}.tap.peaks"] = (tap.get("peak_l"),
                                            tap.get("peak_r"))
            tt = leg.get("two_tone")
            if isinstance(tt, dict):
                out[f"{base}.tt.mix"] = tt.get("mix_signature")
                out[f"{base}.tt.stereo"] = tt.get("stereo_signature")
                out[f"{base}.tt.channels"] = tt.get("channels")
            if "mix_half_gain_ratio" in leg:
                out[f"{base}.ratio"] = leg["mix_half_gain_ratio"]
    # baseline battery must be identical across runs
    for name in ("ui", "ui_alt", "ui_third", "impact", "impact_alt",
                 "impact_third", "movement", "movement_alt",
                 "movement_third", "ambience", "ambience_alt",
                 "ambience_third", "stem"):
        v = m.get(name)
        if isinstance(v, dict):
            out[f"battery.{name}.verdict"] = v.get("verdict") or \
                v.get("failures")
    return out


def classify(path):
    if re.search(r"(when_s|at_s|wall_s|waited|\.n$|_count$|f_l_any|f_r_any"
                 r"|windows|stderr_scan|bytes|\.reply|zero_windows"
                 r"|audio_windows|\.cfg|tag$|ltag$|argv|node_group"
                 r"|media_name|\.state$)", path):
        return "timing-or-runlocal"
    return "MEASURED-OR-STRUCTURAL"


def main():
    paths = sys.argv[1:]
    runs = {}
    for p in paths:
        ts = Path(p).name.split("-capture-")[0].replace("receipt-run", "")
        tag = f"{Path(p).parent.name}/{ts}"
        runs[tag] = load(p)
    base_tag = list(runs)[0]
    for tag, d in runs.items():
        if tag == base_tag:
            continue
        diffs = list(walk_diff(runs[base_tag], d))
        buckets = {}
        for path, a, b in diffs:
            buckets.setdefault(classify(path), []).append((path, a, b))
        print(f"### full canonical diff: {base_tag} vs {tag} "
              f"({len(diffs)} differing paths; "
              f"{len(buckets.get('MEASURED-OR-STRUCTURAL', []))} "
              "measured/structural)")
        for path, a, b in buckets.get("MEASURED-OR-STRUCTURAL", []):
            print(f"  DIFF {path}\n    {base_tag}: {a}\n    {tag}: {b}")
        for cat in ("timing-or-runlocal",):
            items = buckets.get(cat, [])
            print(f"  -- {len(items)} {cat} diffs, paths only --")
            for path, a, b in items:
                print(f"     {path}: {base_tag}={a!r} {tag}={b!r}")
        print()

    print("### curated verdict cells")
    table = {tag: cells(d) for tag, d in runs.items()}
    keys = sorted(set().union(*[set(t) for t in table.values()]))
    tags = list(runs)
    for k in keys:
        vals = [table[t].get(k, "<absent>") for t in tags]
        if all(v == vals[0] for v in vals):
            continue
        print(f"  CELL {k}")
        for t, v in zip(tags, vals):
            print(f"    {t}: {v}")


if __name__ == "__main__":
    main()
