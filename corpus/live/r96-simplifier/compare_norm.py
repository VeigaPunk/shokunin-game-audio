#!/usr/bin/env python3
"""r96 simplifier — normalized receipt pair comparator.

Volatile classes are normalized BY PATH (per-run namespace/pid, server
indices, module ids, wall times, text tails, race censuses, foreign
censuses, witness counts).  Everything else — every armed value, every
predicted/measured attr, every rc/class, every census list, every
receipt key — is compared exactly.

Usage: compare_norm.py A.json B.json --kind KIND --label L [--json-out F]
KIND: control | c5 | c4rep | c4del | c5+c4rep | c5+c4del
"""
import argparse
import json
import re
import sys

PLACE = "<VOLATILE>"


def norm(path, v, kind="control"):
    p = path
    # --- intended-fold paths are never normalized (they must show up) ---
    if "t_proc_lat_b" in p and "c5" in kind:
        return v
    if p.endswith(".pid") and "c4rep" in kind:
        return v
    # --- timing ---
    if re.search(r"(wall_s|polls|_t$|_abs$|waited_s|wall|nsec|seq|serial|"
                 r"row_t|link_t|t_row_s|bound_s|hold_s|wait)", p):
        return PLACE
    # --- server / module indices ---
    if re.search(r"(\.index$|\.client$|\.client_index$|module_id$|"
                 r"captured$|verified_index$|\.id$|\.ids|"
                 r"landed_sink_index|landed_source_index|"
                 r"row\.sink$|row\.source$|\.sink$|\.source$|"
                 r"\.node_id|\.object_id|\.si$|\.so$)", p):
        return PLACE
    # --- per-run names ---
    if re.search(r"(landed_sink_name|landed_source_name|"
                 r"row\.props\.media\.name|row\.props\.target\.object|"
                 r"row\.props\.application\.name|"
                 r"row\.props\.module-stream-restore\.id)", p):
        return PLACE
    # --- recorded text (stderr/stdout tails carry client indices) ---
    if re.search(r"(stdout|stderr)", p):
        return PLACE
    # --- race censuses / host censuses ---
    if re.search(r"(first_snapshot_attrs|first_snapshot_missing_attrs|"
                 r"foreign|contention|loadavg|capture_miss_census|"
                 r"oracle|inventory|pulse_server|\.socket$)", p):
        return PLACE
    # --- the live node state behind the named e_native_corked block ---
    if re.search(r"(node_state_before|node_state_after|live_state_stable)", p):
        return PLACE
    # --- named coverage-block texts: identity only (owner + rep) ---
    if "coverage_blocked" in p and isinstance(v, str):
        head = v.split(" — ")[0].split(": ")[0]
        return re.sub(r"\d+", "#", head)
    # --- witness counts (bounded, not equality-armed; the law set arms
    #     the bounds) — `stderr_bytes` is law-armed, never normalized ---
    if p.endswith("stderr_bytes"):
        return v
    if re.search(r"(frames|nonzero_frames|_samples|drained|readable|peak|"
                 r"rows$|bytes$|\.size|\.len$|count$|n_|_n$)", p):
        if "restore_before" in p or "restore_after" in p:
            return v
        return PLACE
    # --- per-run namespace / pid / temp dir inside strings ---
    if isinstance(v, str):
        s = v
        s = re.sub(r"r96a_ns2?_\d+", "r96a_ns_<PID>", s)
        s = re.sub(r"r96a_([A-Za-z]+)_\d+", r"r96a_\1_<PID>", s)
        s = re.sub(r"r96a_\d+", "r96a_<PID>", s)
        s = re.sub(r"/home/vgpnk/Projects/shokunin/tmp/[^ ]*", "<TMP>", s)
        s = re.sub(r"Client Index: \d+", "Client Index: <N>", s)
        s = re.sub(r"module-stream-restore\.id[^ ]*", "msr.id", s)
        return s
    return v


DIGEST_LISTS = (".events", ".subscribe_lines")


def flat(x, prefix=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from flat(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(x, list):
        if prefix.endswith(DIGEST_LISTS):
            # recorded timing series: keep the distinct normalized lines,
            # drop timestamps and per-index presence (counts are law-checked)
            lines = sorted({re.sub(r"\d+", "#", str(item.get("line", "")))
                            for item in x if isinstance(item, dict)})
            yield f"{prefix}.<digest>", lines
            return
        if prefix.endswith(".corked_samples"):
            pairs = sorted({(item.get("corked"), str(item.get("pulse_corked")))
                            for item in x if isinstance(item, dict)})
            yield f"{prefix}.<digest>", [list(p) for p in pairs]
            return
        for i, v in enumerate(x):
            yield from flat(v, f"{prefix}[{i}]")
    else:
        yield prefix, x


def norm_view(receipt, kind="control"):
    return {p: norm(p, v, kind) for p, v in flat(receipt)}


def intended(path, kind, va, vb):
    has_c5 = "c5" in kind
    has_rep = "c4rep" in kind
    has_del = "c4del" in kind
    if "t_proc_lat_b" in path and has_c5:
        return "C5: duplicate leg removed"
    if path.endswith("late_attr_census.legs") and has_c5 \
            and va == 66 and vb == 64:
        return "C5: recorded census follows the cell count"
    if path.endswith(".pid") and has_rep and isinstance(vb, int):
        return "C4rep: child pid recorded"
    if path.endswith(".row") and "t_f32le_invalid" in path and has_del \
            and vb is None:
        return "C4del: dead recording removed"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--kind", default="control")
    ap.add_argument("--label", default="pair")
    ap.add_argument("--json-out")
    args = ap.parse_args()
    A = json.load(open(args.a))
    B = json.load(open(args.b))
    fa, fb = dict(flat(A)), dict(flat(B))
    na, nb = norm_view(A, args.kind), norm_view(B, args.kind)
    paths = sorted(set(na) | set(nb))
    diffs = []
    for p in paths:
        # key-presence changes are diffs even when the value is None/absent
        if (p in fa) != (p in fb):
            diffs.append((p, fa.get(p), fb.get(p), na.get(p), nb.get(p)))
        elif na.get(p) != nb.get(p):
            diffs.append((p, fa.get(p), fb.get(p), na.get(p), nb.get(p)))
    kinds = {}
    for p, va, vb, xa, xb in diffs:
        k = intended(p, args.kind, va, vb) or "RESIDUAL"
        kinds.setdefault(k, []).append(p)
    out = {"label": args.label, "kind": args.kind, "a": args.a, "b": args.b,
           "leaves": len(paths), "n_diff": len(diffs),
           "classes": {k: len(v) for k, v in kinds.items()},
           "residual": [{"path": p, "a": repr(va)[:120],
                         "b": repr(vb)[:120]}
                        for p, va, vb, xa, xb in diffs
                        if (intended(p, args.kind, va, vb) or
                            "RESIDUAL") == "RESIDUAL"],
           "diffs": [{"path": p, "a": repr(va)[:120], "b": repr(vb)[:120],
                      "class": intended(p, args.kind, va, vb) or "RESIDUAL"}
                     for p, va, vb, xa, xb in diffs]}
    print(f"== {args.label} [{args.kind}]: normalized leaves={len(paths)} "
          f"diffs={len(diffs)} classes={out['classes']}")
    for d in out["diffs"]:
        if d["class"] == "RESIDUAL":
            print(f"   RESIDUAL {d['path']}: {d['a']} -> {d['b']}")
    for d in out["diffs"]:
        if d["class"] != "RESIDUAL":
            print(f"   {d['class']}: {d['path']}")
    if args.json_out:
        json.dump(out, open(args.json_out, "w"), indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
