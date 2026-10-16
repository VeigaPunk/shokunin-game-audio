#!/usr/bin/env python3
"""r86-verifier tiered receipt comparator (verifier-owned, no fixture import).

Tiers (r85 convention, extended for the r86 surface):
  exact  = verdict-bearing scalars + structural law fields, with only
           run-invariant normalisation (pids/namespaces/object ids/serials);
  named  = law-bearing values whose magnitude is a claim (DSP medians,
           pactl percentages, store counts);
  entry  = per-entry teardown/witness projections;
  analog = everything else (timings, sizes, ids, argv, loadavg, host
           census) — counted, never a verdict.

Usage: surface.py A.json B.json [--label A B]
"""
import json
import re
import sys

EXACT_BASE = ("exit_code", "signal", "killed_at_bound", "signal_delivered",
              "loop_assert", "armed")
# cli_pipe's error_class/hit are a registry-event race (boundary #21): the
# same run can or cannot observe a foreign `no global N` line. Exempted.
RACE_EXEMPT = {("pwctl_tools_r86_probe", "cli_pipe")}
# Scalar legs that record host state / sampling counts, not a law.
SCALAR_ANALOG = {("pwctl_dsp_r86_probe", "tap_windows"),
                 ("pwctl_meta_r86_probe", "subj0_keys")}
# DSP envelope bounds (the medians are windowed envelopes; bounds are the law).
DSP_BOUNDS = {"solo": lambda v: v >= 8000,
              "cv25": lambda v: 2000 <= v <= 2100,
              "cv50": lambda v: 4000 <= v <= 4200,
              "mute": lambda v: v == 0.0,
              "reset": lambda v: v >= 8000,
              "dead": lambda v: v >= 8000,
              "pa25": lambda v: 120 <= v <= 140,
              "pa100": lambda v: v >= 8000}


def norm(s):
    if not isinstance(s, str):
        return s
    s = re.sub(r"r86a_ns_\d+", "r86a_ns_<P>", s)
    s = re.sub(r"r86a_tap_\d+", "r86a_tap_<P>", s)
    s = re.sub(r"r86arole\d+", "r86arole<P>", s)
    s = re.sub(r"r86a_\d+", "r86a_<P>", s)
    s = re.sub(r"r86v_\d+", "r86v_<P>", s)
    s = re.sub(r"object \d+", "object <ID>", s)
    s = re.sub(r"0x[0-9a-fA-F]+", "0x<HEX>", s)
    s = re.sub(r"\b\d{3,}\b", "<N>", s)
    return s


def pct(stdout):
    m = re.search(r"(\d+)%", stdout or "")
    return int(m.group(1)) if m else None


def pod_float(stdout, key):
    """The `Float X` value following `Prop: key ...:<key> (`."""
    lines = (stdout or "").splitlines()
    for i, ln in enumerate(lines):
        if f":{key} (" in ln:
            for nxt in lines[i + 1:i + 3]:
                m = re.match(r"\s*Float ([-\d.]+)", nxt)
                if m:
                    return float(m.group(1))
    return None


def exact(ent, name, leg):
    o = {}
    if not isinstance(leg, dict):
        return {"scalar": leg}
    for k in EXACT_BASE:
        if k in leg:
            o[k] = leg[k]
    if (ent, name) in RACE_EXEMPT:
        o["error_class"] = "<race>"
        o["error_hit"] = "<race>"
    else:
        if "error_class" in leg:
            o["error_class"] = leg["error_class"]
        if "error_hit" in leg:
            o["error_hit"] = norm(leg["error_hit"])
    if ent == "pwctl_params_r86_probe" and "has_pod" in leg:
        o["has_pod"] = leg["has_pod"]
    if ent == "pwctl_addr_r86_probe":
        if name in ("ls_Node", "ls_Port", "ls_Metadata", "ls_Client") \
                and "typed_rows" in leg:
            o["typed_rows"] = leg["typed_rows"]
        if name.startswith("dump_full") and "self_clients" in leg:
            o["self_clients"] = leg["self_clients"]
        if name == "destroy_census":
            o["surviving"] = leg.get("surviving")
        if name == "self_loop_census":
            o["n_links"] = len(leg.get("links") or [])
    if ent == "pwctl_tools_r86_probe" and "env" in leg:
        o["env"] = {k: norm(str(v)) for k, v in leg["env"].items()}
    if ent == "pwctl_dsp_r86_probe" and name == "writes":
        o["writes"] = {k: v.get("exit_code") for k, v in leg.items()}
    return o


def named(ent, name, leg):
    o = {}
    if not isinstance(leg, dict):
        return o
    if ent == "pwctl_dsp_r86_probe":
        if name == "regions":
            o = {k: bool(DSP_BOUNDS[k](v["median_peak"]))
                 for k, v in leg.items() if k in DSP_BOUNDS}
        if name.startswith("pactl_"):
            o["pct"] = pct(leg.get("stdout"))
        if name == "enum_after_dead":
            o["volume"] = pod_float(leg.get("stdout"), "volume")
    if ent == "pwctl_addr_r86_probe":
        st = leg.get("stdout") or ""
        if name == "ls_serial":
            o["serial_resolved"] = "object.serial = " in st
        if name == "ls_id":
            o["serial_absent"] = "object.serial = " not in st
        if name == "info_id":
            o["id_resolved"] = "id: " in st
        if name in ("dump_badid", "dump_bogus", "dump_color_sep",
                    "meta_info_empty"):
            o["bytes0"] = leg.get("stdout_bytes") == 0
        if name == "dump_color_join":
            o["dumped"] = (leg.get("stdout_bytes") or 0) >= 1000
        if name == "remote_down":
            o["connect_failed"] = "failed to connect" in (leg.get("stderr") or "")
    if ent == "pwctl_params_r86_probe":
        if name == "sp_garbage":
            o["none_echo"] = (leg.get("stdout") or "").strip() == "None"
        if name == "sp_voltype":
            o["none_slot"] = "None" in (leg.get("stdout") or "")
        if name == "re_vol":
            o["volume"] = pod_float(leg.get("stdout"), "volume")
        if name == "re_port_lat":
            o["minQuantum"] = pod_float(leg.get("stdout"), "minQuantum")
    if ent == "pwctl_meta_r86_probe":
        if name == "meta_list":
            o["stores"] = leg.get("stdout_lines")
    if ent == "pwctl_tools_r86_probe":
        if name == "lk_list":
            o["own_rows"] = (leg.get("stdout_lines") or 0) > 0
    return o


def entry_proj(ent, e):
    o = {}
    sg = e.get("sinks_gone")
    if isinstance(sg, dict):
        o["sinks_gone"] = {norm(k): v for k, v in sg.items()}
    else:
        o["sinks_gone"] = sg
    o["own_nodes_after"] = sorted(norm(x) for x in (e.get("own_nodes_after") or []))
    if "meta_keys_gone" in e:
        o["meta_keys_gone"] = e["meta_keys_gone"]
    ul = {}
    for tag, u in (e.get("unloads") or {}).items():
        u = u or {}
        ul[norm(tag)] = {"field": u.get("field"),
                         "value": norm(str(u.get("value"))),
                         "verified_ok": u.get("verified_index") == u.get("captured"),
                         "recycled": u.get("recycled"),
                         "exit_code": u.get("exit_code")}
    o["unloads"] = ul
    o["failures"] = e.get("failures")
    o["coverage_blocked"] = e.get("coverage_blocked")
    o["foreign_r86a_nodes"] = sorted(norm(x) for x in (e.get("foreign_r86a_nodes") or []))
    return o


def compare(pa, pb):
    A = json.load(open(pa))["measurements"]
    B = json.load(open(pb))["measurements"]
    ents = sorted(k for k in A if "r86" in k)
    out = {"exact": [], "named": [], "entry": [], "analog_n": 0}
    for ent in ents:
        ea, eb = entry_proj(ent, A[ent]), entry_proj(ent, B[ent])
        if ea != eb:
            for k in sorted(set(ea) | set(eb)):
                if ea.get(k) != eb.get(k):
                    out["entry"].append((ent, k, ea.get(k), eb.get(k)))
        names = sorted(set(A[ent]["legs"]) | set(B[ent]["legs"]))
        for name in names:
            la, lb = A[ent]["legs"].get(name), B[ent]["legs"].get(name)
            if not isinstance(la, dict) or not isinstance(lb, dict):
                if la != lb:
                    if (ent, name) in SCALAR_ANALOG:
                        out["analog_n"] += 1
                    else:
                        out["exact"].append((ent, name, la, lb))
                continue
            xa, xb = exact(ent, name, la), exact(ent, name, lb)
            if xa != xb:
                out["exact"].append((ent, name, xa, xb))
            na, nb = named(ent, name, la), named(ent, name, lb)
            if na != nb:
                out["named"].append((ent, name, na, nb))
            keys = set(la) | set(lb)
            xkeys = set(xa) | set(xb) | set(na) | set(nb)
            for k in keys - xkeys:
                if la.get(k) != lb.get(k):
                    out["analog_n"] += 1
    return out


def main():
    pa, pb = sys.argv[1], sys.argv[2]
    r = compare(pa, pb)
    print(f"== {pa}  vs  {pb}")
    for tier in ("exact", "named", "entry"):
        print(f"-- {tier}: {len(r[tier])} diff(s)")
        for d in r[tier][:25]:
            print("   ", json.dumps(d, default=str)[:400])
    print(f"-- analog: {r['analog_n']} volatile field(s) (not a verdict)")
    return 1 if (r["exact"] or r["named"] or r["entry"]) else 0


if __name__ == "__main__":
    sys.exit(main())
