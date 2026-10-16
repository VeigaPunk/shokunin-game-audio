#!/usr/bin/env python3
"""r86 reviewer — normalized verdict-surface diff across r86 receipts.

Builds a per-leg verdict surface (the fields the arms read, never the
volatile text/timing) for the 5 pwctl entries and diffs it between
receipts. Used to calibrate run1-vs-run2 volatility and then to check
that the reviewer's live run differs only inside that volatile set.

Usage: r86r_surface.py RECEIPT... [--json OUT]
"""
import argparse
import json
import re
import sys

LEGS = ("pwctl_addr_r86_probe", "pwctl_params_r86_probe",
        "pwctl_dsp_r86_probe", "pwctl_meta_r86_probe",
        "pwctl_tools_r86_probe")


def leaf_surface(l):
    out = {}
    for k in ("exit_code", "signal", "killed_at_bound", "error_class",
              "has_pod", "stdout_bytes", "stdout_lines", "armed"):
        if k in l:
            out[k] = l[k]
    return out


def surface(path):
    d = json.load(open(path))
    m = d["measurements"]
    s = {}
    for name in LEGS:
        e = m[name]
        es = {}
        for ln, l in (e.get("legs") or {}).items():
            if isinstance(l, dict):
                es[ln] = leaf_surface(l)
        es["__failures"] = e.get("failures")
        es["__blocked"] = e.get("blocked")
        es["__coverage_blocked"] = e.get("coverage_blocked")
        es["__sinks_gone"] = e.get("sinks_gone")
        es["__own_nodes_after"] = e.get("own_nodes_after")
        if name == "pwctl_dsp_r86_probe":
            regs = (e.get("legs") or {}).get("regions") or {}
            es["__regions"] = {k: v.get("median_peak")
                               for k, v in regs.items()}
            es["__pactl_pct"] = {
                k: (re.search(r"(\d+)\s*%",
                              (e["legs"].get(k) or {}).get("stdout") or "")
                    or [None, None])[1]
                for k in ("pactl_after_cv25", "pactl_after_cv50",
                          "pactl_after_dead", "pactl_read_25",
                          "pactl_read_100")}
            es["__enum_dead_float25"] = bool(re.search(
                r"Props:volume[\s\S]{0,120}?Float 0\.25",
                (e["legs"].get("enum_after_dead") or {}).get("stdout")
                or ""))
        if name == "pwctl_addr_r86_probe":
            es["__self_clients"] = [e["legs"][f"dump_full{i}"]
                                    .get("self_clients") for i in (1, 2)]
            es["__ns_media_class"] = (e.get("ns_leaf") or {}).get(
                "media_class")
            es["__meta_store_ids"] = e.get("meta_store_ids")
        if name == "pwctl_meta_r86_probe":
            es["__meta_census"] = e.get("meta_census")
            es["__subj0_keys"] = (e["legs"] or {}).get("subj0_keys")
        if name == "pwctl_tools_r86_probe":
            es["__jack_env"] = {ln: e["legs"][ln].get("env")
                                for ln in e["legs"]
                                if isinstance(e["legs"][ln], dict)
                                and e["legs"][ln].get("env")}
        s[name] = es
    return s


def flat(s):
    out = {}
    for entry, legs in s.items():
        for ln, v in legs.items():
            out[f"{entry}/{ln}"] = v
    return out


def diff(a, b):
    fa, fb = flat(a), flat(b)
    keys = sorted(set(fa) | set(fb))
    d = {}
    for k in keys:
        if fa.get(k) != fb.get(k):
            d[k] = [fa.get(k), fb.get(k)]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("receipts", nargs="+")
    ap.add_argument("--json")
    args = ap.parse_args()
    surfs = {p: surface(p) for p in args.receipts}
    base = args.receipts[0]
    out = {"surfaces": surfs, "diffs": {}}
    for p in args.receipts[1:]:
        out["diffs"][f"{base} -> {p}"] = diff(surfs[base], surfs[p])
    for pair, d in out["diffs"].items():
        print(f"=== {pair}: {len(d)} differing keys ===")
        for k, (x, y) in d.items():
            print(f"  {k}: {json.dumps(x)[:110]}  !=  {json.dumps(y)[:110]}")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
