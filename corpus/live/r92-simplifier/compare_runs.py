#!/usr/bin/env python3
"""r92 simplifier — law-surface projection + pair comparison.

Projects a filterchain-r92 receipt onto the leaves the arms read (plus the
recorded-not-armed census leaves that are *stable by construction*: the host
inventory pins, the error classes, the shape witnesses), normalizes every
volatile leaf and pid-tagged key, and prints the changed leaves between two
receipts.

Usage: python3 compare_runs.py <receiptA.json> <receiptB.json> [--out FILE]
"""
import json
import re
import sys

ENTRIES = ("filterchain_arm_r92_probe", "filterchain_dsp_r92_probe",
           "filterchain_ir_r92_probe", "filterchain_wpx_r92_probe")

# leaves that are recorded, never armed, and volatile across windows/hosts
DROP = {
    # ids / handles / counts of transient objects
    "module_id", "var", "tries", "wall_s", "sent", "text", "log_tail",
    "bytes", "ref_bytes", "out_bytes", "ir_bytes", "stim_bytes", "lines",
    "stdout", "stderr", "err_lines", "warn_lines", "load_text", "args",
    "sinks", "unloads", "unload_module", "snapshots", "lag",
    "foreign_r92a_nodes", "contention", "loadavg", "reader_tries",
    "live_after", "win_offsets", "spdif_links", "capture_state",
    "error_hit", "signal", "host_is_quiet", "own_pid", "residual_destroy",
    "inventory", "daemon", "state", "unloads_note",
    # capture-length / energy record (the validity gate is `valid`)
    "out_frames", "ref_frames", "n", "rms", "ref_stats", "ref_mags",
    "out_mags", "out_stats",
}

# the wpx stdout substrings the arms read (derived booleans replace stdout)
W_STDOUT = {
    "w_print": "r92a hello from wpexec",
    "w_globals": "Core=table LocalModule=function Settings=table "
                 "require_api=nil",
    "w_lm_bad_module": "pcall ok=true mod=nil",
    "w_lm_bad_label": "pcall ok=true mod=nil",
    "w_settings": "restore-props=",
}


def scrub(s):
    s = re.sub(r"\S*/scratch[^/]*/(?:run\d+/)?", "<scratch>/", s)
    s = re.sub(r"r92a_\d+", "r92a_<pid>", s)
    s = re.sub(r"0x[0-9a-f]+", "0x<ptr>", s)
    return s


def norm(o, key=None, tag=None):
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if k in DROP:
                continue
            out[scrub(k)] = norm(v, k, tag)
        return out
    if isinstance(o, list):
        return [norm(x, key, tag) for x in o]
    if isinstance(o, str):
        return scrub(o)
    if isinstance(o, float):
        return round(o, 6)
    return o


def leg_proj(tag, leg):
    out = {}
    for k, v in leg.items():
        if k == "stdout" and tag in W_STDOUT:
            out["stdout_has"] = W_STDOUT[tag] in (v or "")
            continue
        if k == "stdout":
            out["stdout_len_class"] = ("empty" if not v else
                                       "short" if len(v) < 200 else "long")
            continue
        if k == "snapshots":
            out["snapshots"] = [
                {"own_nodes_nonempty": bool(s.get("own_nodes")),
                 "own_edges": s.get("own_edges")} for s in v]
            continue
        if k == "out_stats":
            out["out_stats"] = {"max_abs": v.get("max_abs")}
            continue
        if k == "log_stats":
            out["log_stats"] = {"E": v.get("E"), "W": v.get("W")}
            continue
        if k in DROP:
            continue
        out[scrub(k)] = norm(v, k, tag)
    return out


def project(receipt):
    m = receipt["measurements"]
    out = {"mode": receipt.get("mode")}
    for e in ENTRIES:
        entry = m[e]
        proj = {}
        for k, v in entry.items():
            if k in ("legs", "unloads", "sinks", "foreign_r92a_nodes",
                     "contention", "loadavg", "reader_tries", "live_after",
                     "inventory", "residual_destroy"):
                continue
            if k == "tools":
                proj["tools"] = {kk: bool(vv) for kk, vv in v.items()}
                continue
            if k == "daemon":
                proj["daemon_ok"] = v.get("ok")
                continue
            if k == "sinks_gone":
                proj["sinks_gone"] = sorted(
                    scrub(kk) for kk, vv in v.items())
                continue
            if k == "own_nodes_after":
                proj["own_nodes_after"] = sorted(
                    scrub(x) for x in (v or []))
                continue
            proj[scrub(k)] = norm(v, k)
        legs = {}
        for tag, leg in (entry.get("legs") or {}).items():
            if isinstance(leg, dict):
                legs[tag] = leg_proj(tag, leg)
            else:
                legs[tag] = leg
        proj["legs"] = legs
        out[e] = proj
    return out


def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, o


def main():
    a = json.load(open(sys.argv[1]))
    b = json.load(open(sys.argv[2]))
    pa, pb = project(a), project(b)
    la, lb = dict(leaves(pa)), dict(leaves(pb))
    keys = sorted(set(la) | set(lb))
    changed = [(k, la.get(k), lb.get(k)) for k in keys
               if la.get(k) != lb.get(k)]
    print(f"projected leaves: A={len(la)} B={len(lb)} changed={len(changed)}")
    for k, va, vb in changed:
        print(f"  {k}\n    A={va!r}\n    B={vb!r}")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
        json.dump({"changed": [{"leaf": k, "a": va, "b": vb}
                               for k, va, vb in changed],
                   "leaves_a": len(la), "leaves_b": len(lb)},
                  open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
