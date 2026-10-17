#!/usr/bin/env python3
"""Canonical before/after comparison of two --probe-wpstate-r90 runs.

Usage: compare_runs.py <run_dir_A> <run_dir_B> [--full]

Projects each run's measurements.json onto its VERDICT surface and its
LAW surface:

  verdict : the four r90 entries' `failures` / `coverage_blocked` / `blocked`
            and the leg-key census (15/15/24/6).
  law     : per leg, every field that is a recorded *claim* — rc, exit_code,
            error_class, error_hit, sha12, byte counts, link counts, row
            counts, outcomes, field-split values, fresh-key guard, teardown
            census, unload rc — with every pid/nonce/timestamp/wall/sample
            normalized away (those differ by construction between two live
            runs).

`--full` also prints the raw canonical diff (volatile fields included) so a
reviewer can see what was dropped and why.
"""
import json
import re
import sys
from pathlib import Path

VOLATILE = re.compile(
    r"^(samples|value|pre_value|value_after|row|live|rows|links|mine|head|"
    r"stream_node|node|port|default_sink|edges_.*|replay_node_present|"
    r"sink_input|module_id|^id$|probes|after|cmd_ms|delta|wall_s|"
    r"t$|t_.*|keys|store_at_entry|store_at_exit|key_pre|"
    r"argv|replay_argv|object|stdout_token|stdout_raw|stderr_raw|"
    r"captured|verified_index|serial|pid|nonce|"
    r"link_id|object\.id|object\.serial|factory\.id|client\.id|node\.id|"
    r"port\.id|link\.input\.node|link\.input\.port|link\.output\.node|"
    r"link\.output\.port|live_objects|schema_objects)$")


# volatile numeric object identities: the family recycles module indices,
# link ids and object serials by its own boundary law — never a claim
ID_KEYS = re.compile(
    r"^(id|object|object\.id|object\.serial|serial|link_id|link\..*|"
    r"factory\.id|client\.id|node\.id|port\.id|module_id|captured|"
    r"verified_index|index)$")


def nkey(k):
    """Normalize a dict key: pid/nonce-bearing keys must fold together."""
    k = re.sub(r"r90a_\d+n\d+", "r90a_<pid>n<nonce>", k)
    k = re.sub(r"r90a_[a-z0-9_]*?_(\d+)", r"r90a_<tag>_<pid>", k)
    return re.sub(r"_\d{4,}$", "_<pid>", k)


def project_unloads(un):
    """The name-verified unload surface: rc + class + the field/value pair
    it re-checked. The captured/verified module INDEX is recycled by
    construction (the r90 boundary's own recycling law) — volatile."""
    if not isinstance(un, dict):
        return norm(un)
    return {nkey(k): {kk: norm(vv) for kk, vv in v.items()
                      if kk not in ("captured", "verified_index")}
            for k, v in un.items()}

# entry-level keys that are host/seat state, never the family's claim
DROP_ENTRY = {"live_receipt", "loadavg", "contention", "oracle_at_start",
              "inventory", "foreign_r90a_nodes", "probe", "tools", "keys",
              "store_at_entry", "store_at_exit"}

# leg-level keys that carry the claim but are volatile in *form*
KEEP_VOLATILE = {"own_links", "n_links", "n_rows", "out_len", "n_keys",
                 "count", "sink_gone", "row_present", "control_row_present",
                 "outcome", "status", "own_sinks_alive", "id_recycled_by_"
                 "foreign", "node_present", "sink_present", "pre_present",
                 "stream_alive", "killed_at_bound", "replay_node_present"}


def norm(x):
    if isinstance(x, str):
        s = re.sub(r"r90a_[a-z0-9_]*?_(\d+)", r"r90a_<tag>_<pid>", x)
        s = re.sub(r"r90a_(\d+)n\d+", r"r90a_<pid>n<nonce>", s)
        s = re.sub(r"r90a_(\d+)_", r"r90a_<pid>_", s)
        s = re.sub(r"r90arole(\d+)", r"r90arole<pid>", s)
        # every OTHER r9x seat's live object: sibling churn, never a claim
        s = re.sub(r"r9\da_[A-Za-z0-9_.:-]*", "<foreign>", s)
        s = re.sub(r"(<foreign>[\s,;|]*)+", "<foreign>", s)
        s = re.sub(r"\b\d{6,}\b", "<num>", s)
        s = re.sub(r"\b(id|seq):\d+", r"\1:<n>", s)
        s = re.sub(r"\.\d+Z", "<ts>", s)
        return s
    if isinstance(x, list):
        return [norm(v) for v in x]
    if isinstance(x, dict):
        return {nkey(k): norm(v) for k, v in x.items()
                if not ID_KEYS.match(k)}
    return x


# Post-steps for the legs whose recorded text/counts are host-wide: keep the
# ARMED predicate, drop the global table. (raw, out) -> out
def _post_k_ids(raw, out):
    out.pop("n_links", None)          # global table size, not the claim
    out["mine_n"] = len(raw.get("mine") or [])
    return out


def _post_k_m_stream(raw, out):
    out["streamed"] = bool(raw.get("stdout_bytes"))
    out.pop("stdout", None)
    out.pop("stdout_bytes", None)
    return out


def _post_listing(name, fn):
    def go(raw, out):
        out[name] = fn(out.pop("stdout", ""))
        out.pop("stdout_bytes", None)
        out.pop("n_rows", None)
        return out
    return go


POST = {
    "k_ids": _post_k_ids,
    "k_m_stream": _post_k_m_stream,
    "k_list_slot": _post_listing("leak_present",
                                 lambda t: any(":playback_FL" in r and
                                               "<tag>" in r
                                               for r in t.splitlines())),
    "k_list_filtered": _post_listing("leak_present",
                                     lambda t: any(":playback_FL" in r and
                                                   "<tag>" in r
                                                   for r in t.splitlines())),
    "k_l_pattern": _post_listing("nonempty", lambda t: bool(t.strip())),
    "k_v": _post_listing("n_rows_ge_2", lambda t: len(t.splitlines()) >= 2),
    "k_o_pattern": _post_listing(
        "all_rows_ours",
        lambda t: bool(t.splitlines()) and
        all(r.startswith("r90a_<tag>_<pid>") for r in t.splitlines()
            if r.strip())),
}


def project_entry(entry):
    out = {}
    for k, v in entry.items():
        if k in DROP_ENTRY:
            continue
        if k == "legs":
            legs = {}
            for lk, lv in v.items():
                legs[lk] = project_leg(lv, lk)
            out["legs"] = legs
        elif k in ("sinks_gone", "own_nodes_after", "own_modules_after"):
            out[k] = norm(v)
        elif k == "unloads":
            out[k] = project_unloads(v)
        else:
            out[k] = norm(v)
    return out


def project_leg(leg, lk=None):
    if not isinstance(leg, dict):
        return norm(leg)
    out = {}
    for k, v in leg.items():
        if VOLATILE.match(k) and k not in KEEP_VOLATILE:
            continue
        if k == "objects" and isinstance(v, list):
            # the metadata census: only the 25-key twins are ARMED (the
            # family's own `w_meta` claim); every other Metadata object is
            # sibling/operator churn that comes and goes between runs
            out["objects"] = sorted(
                ({kk: norm(vv) for kk, vv in o.items() if kk != "id"}
                 for o in v if o.get("n_keys") == 25),
                key=lambda o: json.dumps(o, sort_keys=True))
            out["objects_not_armed"] = len(v) - len(out["objects"])
        else:
            out[k] = project_leg(v) if isinstance(v, dict) else norm(v)
    if lk in POST:
        out = POST[lk](leg, out)
    return out


def load(run_dir):
    j = json.loads((Path(run_dir) / "measurements.json").read_text())
    return {k: v for k, v in j["measurements"].items()
            if k.endswith("r90_probe")}


def main():
    a, b = sys.argv[1], sys.argv[2]
    ea, eb = load(a), load(b)
    print(f"A {a}\nB {b}")
    pa = {k: project_entry(v) for k, v in ea.items()}
    pb = {k: project_entry(v) for k, v in eb.items()}
    ok = True
    for k in sorted(set(pa) | set(pb)):
        va, vb = pa.get(k), pb.get(k)
        fa = ea.get(k, {}).get("failures")
        fb = eb.get(k, {}).get("failures")
        la = sorted((va or {}).get("legs", {}))
        lb = sorted((vb or {}).get("legs", {}))
        same = json.dumps(va, sort_keys=True) == json.dumps(vb, sort_keys=True)
        if not same:
            ok = False
        print(f"\n== {k}: failures A={fa} B={fb} "
              f"legs A={len(la)} B={len(lb)} law-projection "
              f"{'IDENTICAL' if same else 'DIFFERS'}")
        if la != lb:
            ok = False
            print(f"   leg keys only in A: {sorted(set(la) - set(lb))}")
            print(f"   leg keys only in B: {sorted(set(lb) - set(la))}")
        if fa != fb:
            ok = False
        if not same:
            import difflib
            sa = json.dumps(va, indent=1, sort_keys=True).splitlines()
            sb = json.dumps(vb, indent=1, sort_keys=True).splitlines()
            d = list(difflib.unified_diff(sa, sb, "A", "B", lineterm="",
                                          n=1))
            print("\n".join(d[:400]))
            print(f"   ... {max(0, len(d) - 400)} more diff lines")
    print(f"\nVERDICT: {'ALL law projections + verdicts identical' if ok else 'DIFFERS (see the hunks above)'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
