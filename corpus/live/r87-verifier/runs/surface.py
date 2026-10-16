#!/usr/bin/env python3
"""r87-verifier tiered receipt comparator (verifier-owned, no fixture
import). Tiers: exact (verdict-bearing keys), named (law-bearing
magnitudes/witnesses), entry (teardown projections), analog (everything
else — counted, never a verdict).

Usage: surface.py A.json B.json [--quiet]
"""
import json
import re
import sys

EXACT_KEYS = {
    "exit_code", "signal", "killed_at_bound", "signal_delivered",
    "loop_assert", "armed", "state", "state_after", "media_class",
    "class", "consumers", "present_in_session", "present_after_quit",
    "present_after_destroy", "linger", "sink_listed_after", "node_after",
    "has_mthd", "has_pod", "rc", "play_rc", "record_rc", "aplaymidi_rc",
    "pwlink_rc", "exited_before_observe", "same_as_pwcat", "realpath",
    "verified_ok", "recycled", "field", "value", "error_class",
    "in_ports", "out_ports", "my_in", "node_found", "pinned",
    "present", "node", "players_alive", "stream_alive", "surviving",
    "dumped", "connect_failed", "stores", "links_n",
}
NAMED_KEYS = {
    "median_peak", "bytes", "note_ons", "note_offs", "ratio_vs_v100",
    "volume", "pct", "peak", "rms", "n_links", "stdout_bytes",
    "serial_resolved", "id_resolved", "bytes0", "none_echo",
}
RACE_EXEMPT = set()   # none declared for r87 yet (see report)
# scalar legs that record host state / sampling counts, not a law
SCALAR_ANALOG = {("pwbind_cli_r87_probe", "tap_windows"),
                 ("pwbind_cli_r87_probe", "foreign_candidates")}
# error_class is ARMED only on the seven pw-cat refusal legs; elsewhere it
# is recorded (a foreign registry-churn line can win the table scan — the
# reviewer's R1 run shows latency res:-95 shadowed by a churn res:-2).
ARMED_ERROR_CLASS = {("pwbind_modes_r87_probe", n) for n in
                     ("m_bare", "m_mflag_only", "m_noflag_target",
                      "m_capture", "m_duplex", "m_clip", "m_dsd")}
ID_KEYS = {"id", "node_id", "object_id", "object_serial", "serial",
           "module_id", "stream_id", "nid"}


def _idkey(k):
    return k in ID_KEYS


def norm(s):
    if isinstance(s, dict):
        return {norm(k): ("<ID>" if k in ID_KEYS else norm(v))
                for k, v in s.items()}
    if isinstance(s, list):
        return [norm(v) for v in s]
    if isinstance(s, float):
        return round(s, 6)
    if not isinstance(s, str):
        return s
    s = re.sub(r"r87a_ns2_\d+", "r87a_ns2_<P>", s)
    s = re.sub(r"r87a_ns_\d+", "r87a_ns_<P>", s)
    s = re.sub(r"r87a_\d+", "r87a_<P>", s)
    s = re.sub(r"r87v_\d+", "r87v_<P>", s)
    s = re.sub(r"r87b_\d+", "r87b_<P>", s)
    s = re.sub(r"r86a_\d+", "r86a_<P>", s)
    s = re.sub(r"r86v_\d+", "r86v_<P>", s)
    s = re.sub(r"r85v_\d+", "r85v_<P>", s)
    s = re.sub(r"r87arole\d+", "r87arole<P>", s)
    s = re.sub(r"/home/[^\s\"']*?/tmp/[^\s\"']*?/(?=[\w.\-]*\.(?:wav|mid|smf))",
               "<TMP>/", s)
    s = re.sub(r"/home/[^\s\"']*?/tmp/[^\s\"' ]*", "<TMPDIR>", s)
    s = re.sub(r"object \d+", "object <ID>", s)
    s = re.sub(r"unknown global '\d+'", "unknown global '<ID>'", s)
    s = re.sub(r"\bno global \d+", "no global <N>", s)
    s = re.sub(r"unknown resource \d+", "unknown resource <N>", s)
    s = re.sub(r"object\.serial = \"\d+\"", "object.serial = \"<N>\"", s)
    s = re.sub(r"\bid=\d+", "id=<N>", s)
    s = re.sub(r"\bseq=\d+", "seq=<N>", s)
    s = re.sub(r"\bserial \d+", "serial <N>", s)
    s = re.sub(r"node \d+", "node <N>", s)
    s = re.sub(r"0x[0-9a-fA-F]+", "0x<HEX>", s)
    s = re.sub(r"\b\d{4,}\b", "<N>", s)
    return s


def walk(la, lb, path, out, tier):
    if isinstance(la, dict) and isinstance(lb, dict):
        for k in sorted(set(la) | set(lb)):
            walk(la.get(k), lb.get(k), path + [k], out, tier)
        return
    if path and path[-1] in ID_KEYS:
        la = lb = "<ID>"
    if norm(la) != norm(lb):
        out[tier].append({"path": ".".join(path), "a": la, "b": lb})


def classify_key(k):
    if k in EXACT_KEYS:
        return "exact"
    if k in NAMED_KEYS:
        return "named"
    return "analog"


def compare_leg(ent, name, la, lb, out):
    if not isinstance(la, dict) or not isinstance(lb, dict):
        if norm(la) != norm(lb):
            if (ent, name) in SCALAR_ANALOG:
                out["analog_n"] += 1
            else:
                out["exact"].append({"path": f"{ent}.{name}",
                                     "a": la, "b": lb})
        return
    for k in sorted(set(la) | set(lb)):
        tier = classify_key(k)
        if k in ("error_class", "error_hit") and \
                (ent, name) not in ARMED_ERROR_CLASS:
            tier = "named"
        if tier == "analog":
            if norm(la.get(k)) != norm(lb.get(k)):
                out["analog_n"] += 1
            continue
        walk(la.get(k), lb.get(k), [f"{ent}.{name}", k], out, tier)


def entry_proj(e):
    o = {"sinks_gone": norm(e.get("sinks_gone")),
         "own_nodes_after": sorted(norm(x) for x in
                                   (e.get("own_nodes_after") or [])),
         "failures": e.get("failures"),
         "coverage_blocked": e.get("coverage_blocked"),
         "foreign_r87a_nodes": sorted(norm(x) for x in
                                      (e.get("foreign_r87a_nodes") or [])),
         "default_sink_at_end": norm(e.get("default_sink_at_end"))}
    ul = {}
    for tag, u in (e.get("unloads") or {}).items():
        u = u or {}
        ul[norm(tag)] = {"field": u.get("field"),
                         "value": norm(str(u.get("value"))),
                         "verified_ok": u.get("verified_index") ==
                         u.get("captured"),
                         "recycled": u.get("recycled"),
                         "exit_code": u.get("exit_code")}
    o["unloads"] = ul
    return o


def compare(pa, pb):
    A = json.load(open(pa))["measurements"]
    B = json.load(open(pb))["measurements"]
    ents = sorted(k for k in A if k.startswith("pwbind"))
    out = {"exact": [], "named": [], "entry": [], "analog_n": 0,
           "legs": 0}
    for ent in ents:
        ea, eb = entry_proj(A[ent]), entry_proj(B[ent])
        for k in sorted(set(ea) | set(eb)):
            if norm(ea.get(k)) != norm(eb.get(k)):
                out["entry"].append({"path": f"{ent}.{k}",
                                     "a": ea.get(k), "b": eb.get(k)})
        for name in sorted(set(A[ent]["legs"]) | set(B[ent]["legs"])):
            out["legs"] += 1
            compare_leg(ent, name, A[ent]["legs"].get(name),
                        B[ent]["legs"].get(name), out)
    return out


def main():
    pa, pb = sys.argv[1], sys.argv[2]
    quiet = "--quiet" in sys.argv
    r = compare(pa, pb)
    print(f"== {pa}  vs  {pb}  ({r['legs']} leg names)")
    for tier in ("exact", "named", "entry"):
        print(f"-- {tier}: {len(r[tier])} diff(s)")
        if not quiet:
            for d in r[tier][:30]:
                print("   ", json.dumps(d, default=str)[:400])
    print(f"-- analog: {r['analog_n']} volatile field(s) (not a verdict)")
    return 1 if (r["exact"] or r["named"] or r["entry"]) else 0


if __name__ == "__main__":
    sys.exit(main())
