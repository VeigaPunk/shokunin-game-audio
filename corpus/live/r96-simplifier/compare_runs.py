#!/usr/bin/env python3
"""r96 simplifier — receipt pair comparator.

Usage: compare_runs.py A.json B.json --label NAME [--json-out out.json]

Structural: per-entry leg-key sets, leg counts, failures/coverage_blocked.
Leaf walk: every differing leaf path, classified:
  INTENDED  — matches the named fold effect for this pair
  VOLATILE  — matches a named volatile class (also present in the
              identical-bytes control pair, or a declared volatile regex)
  UNEXPLAINED — must be empty for a clean fold
Armed projection: the verdict-bearing fields per leg (predicted, env_ms,
frame_size, exit_code, error_class, failures, row_seen, linked,
attr_present, stderr_bytes, latency_rcs, ...) compared exactly.
"""
import argparse
import json
import re
import sys

sys.path.insert(0, "/home/vgpnk/Projects/shokunin/r96s")
import compare_norm as CN

VOLATILE = [
    (r"\.wall_s$", "wall clock"),
    (r"\.polls$", "poll count"),
    (r"_t$", "elapsed time"),
    (r"\.stdout", "recorded stdout text"),
    (r"\.stderr", "recorded stderr text"),
    (r"\.index$", "server object index"),
    (r"\.client$", "client index"),
    (r"\.client_index", "client index"),
    (r"\.module_id$", "module index"),
    (r"\.captured$", "captured module index"),
    (r"\.verified_index$", "re-read module index"),
    (r"\.row\.index$", "row index"),
    (r"\.row\.client$", "row client id"),
    (r"\.foreign", "foreign-lane census"),
    (r"\.contention", "contention census"),
    (r"\.loadavg", "loadavg"),
    (r"\.oracle", "oracle census"),
    (r"\.inventory", "inventory census"),
    (r"\.first_snapshot_attrs", "late-attr race census"),
    (r"\.socket$", "socket path"),
    (r"\.id$", "volatile id"),
    (r"\.ids", "volatile ids"),
    (r"\.nsec", "nsec counter"),
    (r"\.seq$", "sequence"),
    (r"\.serial", "serial"),
    (r"\.tap\.frames$", "tap frame count (bounded, not equality-armed)"),
    (r"\.tap\.nonzero_frames$", "tap count (bounded)"),
    (r"nonzero_frames$", "nonzero-frame count (bounded)"),
    (r"\.cork_flip\..*_samples$", "cork-flip sample count (bounded)"),
    (r"\.pid$", "child pid (recorded, never armed)"),
    (r"\.series", "event series (timing)"),
    (r"\.events", "event list"),
    (r"\.wall", "wall clock"),
    (r"\.rcs$", "per-call rc list (recorded)"),
    (r"\.row\.props\.module-stream-restore\.id", "restore id"),
    (r"\.rows$", "row count (census)"),
    (r"\.bytes$", "byte count (census)"),
    (r"\.size", "size census"),
    (r"\.waited_s$", "enumeration wait"),
    (r"\.sink_waited", "enumeration wait"),
    (r"\.monitor_waited", "enumeration wait"),
    (r"\.path$", "path"),
    (r"\.stdout_bytes$", "stdout bytes"),
]

ARMED_LEG_KEYS = (
    "predicted", "env_ms", "env_raw", "frame_size", "exit_code",
    "error_class", "error_hit", "failures", "row_seen", "linked",
    "attr_present", "killed_at_bound", "signal", "stderr_bytes",
    "latency_rcs", "changes_at_uncork", "has_pulse_corked",
    "restore_before", "restore_after", "corked_witness", "suppressed",
    "source_sha256", "binary_sha256", "cc_exit", "ok", "readable",
    "drained", "peak", "frames", "nonzero_frames", "tap_exit_code",
    "server_gate", "coverage_blocked", "blocked", "src_sha256",
)


def flat(x, prefix=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from flat(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from flat(v, f"{prefix}[{i}]")
    else:
        yield prefix, x


def classify(path, kind, va, vb):
    has_c5 = "c5" in kind
    has_rep = "c4rep" in kind
    has_del = "c4del" in kind
    if "t_proc_lat_b" in path and has_c5:
        return "INTENDED-C5 duplicate leg removed"
    if "late_attr_census.legs" in path and has_c5 and va == 66 and vb == 64:
        return "INTENDED-C5 recorded census follows the cell count"
    if path.endswith(".pid") and has_rep and isinstance(vb, int):
        return "INTENDED-C4rep child pid recorded"
    if path.endswith(".row") and "t_f32le_invalid" in path and has_del \
            and vb is None:
        return "INTENDED-C4del dead recording removed"
    for rx, cls in VOLATILE:
        if re.search(rx, path):
            return cls
    return "UNEXPLAINED"


def armed_view(receipt, kind="control"):
    """{entry.leg.key: value} for the verdict-bearing keys, with the same
    volatile-class normalization as the normalized comparator (so the
    headline armed_diff counts are meaningful)."""
    out = {}
    for entry, e in (receipt.get("measurements") or {}).items():
        for leg, leaf in ((e or {}).get("legs") or {}).items():
            if not isinstance(leaf, dict):
                continue
            for k in ARMED_LEG_KEYS:
                if k in leaf:
                    path = f"{entry}.{leg}.{k}"
                    for sub, v in CN.flat(leaf[k], path):
                        out[sub] = CN.norm(sub, v, kind)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--label", default="pair")
    ap.add_argument("--kind", default="control",
                    help="c5 | c4rep | c4del | c5+c4rep | c5+c4del | control")
    ap.add_argument("--armed-note", default="")
    ap.add_argument("--json-out")
    args = ap.parse_args()
    A = json.load(open(args.a))
    B = json.load(open(args.b))
    fa = dict(flat(A))
    fb = dict(flat(B))
    paths = sorted(set(fa) | set(fb))
    diffs = []
    for p in paths:
        if fa.get(p) != fb.get(p):
            diffs.append((p, fa.get(p), fb.get(p)))
    struct = {}
    for entry in sorted(set((A.get("measurements") or {}))
                        | set((B.get("measurements") or {}))):
        la = set(((A.get("measurements") or {}).get(entry) or {}).get("legs")
                 or {})
        lb = set(((B.get("measurements") or {}).get(entry) or {}).get("legs")
                 or {})
        if la != lb:
            struct[entry] = {"only_a": sorted(la - lb),
                             "only_b": sorted(lb - la),
                             "count_a": len(la), "count_b": len(lb)}
    aa, ab = armed_view(A, args.kind), armed_view(B, args.kind)
    armed_diff = [p for p in sorted(set(aa) | set(ab))
                  if aa.get(p) != ab.get(p)]
    armed_missing = [p for p in sorted(set(aa) | set(ab))
                     if (p in aa) != (p in ab)]
    out = {"label": args.label, "kind": args.kind, "a": args.a, "b": args.b,
           "leaves_a": len(fa), "leaves_b": len(fb),
           "n_diff": len(diffs), "struct": struct,
           "armed_diff": armed_diff, "armed_missing": armed_missing,
           "armed_cells_a": len(aa), "armed_cells_b": len(ab),
           "diffs": [{"path": p, "a": repr(x)[:160], "b": repr(y)[:160],
                      "class": classify(p, args.kind, x, y)}
                     for p, x, y in diffs]}
    print(f"== {args.label}: leaves {len(fa)}/{len(fb)} diffs={len(diffs)} "
          f"armed_diff={len(armed_diff)} armed_missing={len(armed_missing)}")
    if struct:
        print(f"   struct: {json.dumps(struct, sort_keys=True)}")
    bycls = {}
    for d in out["diffs"]:
        bycls.setdefault(d["class"], []).append(d["path"])
    for cls, ps in sorted(bycls.items()):
        print(f"   {cls}: {len(ps)}")
        for p in ps[:14]:
            d = next(x for x in out["diffs"] if x["path"] == p)
            print(f"     {p}: {d['a']} -> {d['b']}")
    if armed_diff:
        print(f"   ARMED DIFFS: {armed_diff[:20]}")
    if args.json_out:
        json.dump(out, open(args.json_out, "w"), indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
