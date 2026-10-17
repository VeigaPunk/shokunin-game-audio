#!/usr/bin/env python3
"""Canonical before/after comparison of two --probe-gstfrz-r91 batteries.

Usage: compare_runs_r91.py <run_dir_A> <run_dir_B>

Projects each run's measurements.json onto its VERDICT surface (the five
entries' failures / coverage_blocked / blocked + the leg-key census + the
fired-event census) and its LAW surface (the armed cells: props, frozen
header/state/fed_by cells, keepalive line counts, resume app status, the
class-armed shapes, connect rcs/classes, unload rc/field/value, teardown
census) with every pid / module index / node id / wall time / sample /
distribution-valued size normalized or dropped (they differ by
construction between two live runs).
"""
import difflib
import json
import re
import sys
from pathlib import Path

# entry-level keys that are host/seat state, never the family's claim
DROP_ENTRY = {"probe", "contention", "oracle_at_start", "inventory",
              "loadavg", "foreign_r91a_nodes"}
# keys dropped at EVERY level: distribution-valued sizes, wall-clock gate
# times, stream byte counts, timeline samples and recorded text
VOLATILE_KEYS = {"bytes", "stderr_bytes", "stdout_bytes", "wall_s", "at",
                 "gate_bytes", "sizes", "sizes_tail", "grew", "tail_grew",
                 "alive_sizes", "resume_bytes", "at_relink", "pre", "post",
                 "samples", "argv", "stdout", "stderr", "first_bytes",
                 "last_bytes", "clock_lost_t", "elapsed_s", "data_actual",
                 "frames_declared"}
# fired-event fields: the gate TIME is a wall clock, never a claim
DROP_FIRED = {"at", "gate_bytes"}


def nkey(k):
    k = re.sub(r"r91a_[a-z0-9_]*?_(\d+)", r"r91a_<tag>_<pid>", k)
    return re.sub(r"_\d{4,}$", "_<pid>", k)


def norm(x):
    if isinstance(x, str):
        # the tree the battery ran from is recorded verbatim (entry["app"]):
        # a cross-tree pair differs by construction — normalize it
        s = re.sub(r"/r91s/[a-z0-9]+/", "<tree>/", x)
        s = re.sub(r"/r91-verify-tree/", "<tree>/", s)
        s = re.sub(r"r91a_[a-z0-9_]*?_(\d+)", r"r91a_<tag>_<pid>", s)
        s = re.sub(r"r91a_(\d+)_", r"r91a_<pid>_", s)
        s = re.sub(r"r91arole(\d+)", r"r91arole<pid>", s)
        s = re.sub(r"gst_r91a_[a-z0-9_]*?_(\d+)", "gst_r91a_<tag>_<pid>", s)
        # every OTHER r9x seat's live object: sibling churn, never a claim
        s = re.sub(r"r9\da_[A-Za-z0-9_.:-]*", "<foreign>", s)
        s = re.sub(r"(<foreign>[\s,;|]*)+", "<foreign>", s)
        s = re.sub(r"\b\d{6,}\b", "<num>", s)
        s = re.sub(r"\.\d+Z", "<ts>", s)
        s = re.sub(r"/tmp/[^\s\"']*", "<tmp>", s)
        return s
    if isinstance(x, list):
        return [norm(v) for v in x]
    if isinstance(x, dict):
        return {nkey(k): norm(v) for k, v in x.items()}
    return x


def project_unloads(un):
    """The name-verified unload surface: rc + the field/value pair it
    re-checked. The captured/verified module INDEX is recycled by
    construction (the boundary's own recycling law) — volatile."""
    if not isinstance(un, dict):
        return norm(un)
    return {nkey(k): {kk: norm(vv) for kk, vv in v.items()
                      if kk not in ("captured", "verified_index",
                                    "recycled")}
            for k, v in un.items()}


def project_fired(fired):
    out = []
    for f in fired or []:
        d = {k: norm(v) for k, v in f.items() if k not in DROP_FIRED}
        res = d.get("result")
        if isinstance(res, dict):
            d["result"] = {k: norm(v) for k, v in res.items()
                           if k not in ("captured", "verified_index",
                                        "at", "links")}
            if "links" in res:
                d["result"]["links"] = [
                    {"out": norm(l.get("out")), "in": norm(l.get("in")),
                     "rc": (l.get("res") or {}).get("exit_code"),
                     "cls": (l.get("res") or {}).get("error_class")}
                    for l in (res.get("links") or [])]
        out.append(d)
    return sorted(out, key=lambda d: json.dumps(d, sort_keys=True))


def project_out(out):
    if not isinstance(out, dict):
        return norm(out)
    return {k: norm(v) for k, v in out.items() if k not in VOLATILE_KEYS}


def project_app(st):
    if not isinstance(st, dict):
        return norm(st)
    keep = {}
    for k, v in st.items():
        if k in ("clock_lost", "forced", "errors", "exit", "rc"):
            keep[k] = norm(v)
        elif k == "state_changes":
            keep[k] = [{"old": norm(c.get("old")), "new": norm(c.get("new"))}
                       for c in (v or [])]
        elif k == "bus_types":
            keep[k] = sorted({norm(b.get("type")) for b in (v or [])})
    return keep


def project_leg(leg):
    if not isinstance(leg, dict):
        return norm(leg)
    out = {}
    for k, v in leg.items():
        if k in VOLATILE_KEYS:
            continue
        if k == "fired":
            out[k] = project_fired(v)
        elif k == "out":
            out[k] = project_out(v)
        elif k == "app_status":
            out[k] = project_app(v)
        else:
            out[k] = norm(v)
    # derived predicates: the recorded TEXT is volatile, its armed
    # predicates are not
    so = leg.get("stdout") or ""
    se = leg.get("stderr") or ""
    out["stdout_nonempty"] = bool(so.strip())
    out["stderr_nonempty"] = bool(se.strip())
    out["has_clock_line"] = "Clock lost, selecting a new one" in so
    out["has_playing_line"] = "Setting pipeline to PLAYING" in so
    return out


def project_entry(entry):
    out = {}
    for k, v in entry.items():
        if k in DROP_ENTRY:
            continue
        if k == "legs":
            out["legs"] = {lk: project_leg(lv) for lk, lv in v.items()}
        elif k in ("sinks_gone", "own_nodes_after"):
            out[k] = norm(v)
        elif k == "unloads":
            out[k] = project_unloads(v)
        elif k == "relink":
            out[k] = {kk: norm(vv) for kk, vv in (v or {}).items()
                      if kk not in VOLATILE_KEYS}
        else:
            out[k] = drop_volatile(v)
    return out


def drop_volatile(x):
    if isinstance(x, dict):
        return {nkey(k): drop_volatile(v) for k, v in x.items()
                if k not in VOLATILE_KEYS}
    if isinstance(x, list):
        return [drop_volatile(v) for v in x]
    return norm(x)


def load(run_dir):
    j = json.loads((Path(run_dir) / "measurements.json").read_text())
    return {k: v for k, v in j["measurements"].items()
            if k.endswith("r91_probe")}


def census(entries):
    """leg-key census + the fired-event shape census (every fired event must
    be a GATED one: the deleted `hooks` path never fired in any run)."""
    legs, gated, plain = {}, 0, 0
    for k, e in entries.items():
        legs[k] = sorted((e.get("legs") or {}))
        for leg in (e.get("legs") or {}).values():
            for f in (leg.get("fired") or []):
                if f.get("gated"):
                    gated += 1
                else:
                    plain += 1
    return legs, gated, plain


def leaves(x):
    if isinstance(x, dict):
        return sum(leaves(v) for v in x.values())
    if isinstance(x, list):
        return sum(leaves(v) for v in x)
    return 1


def changed(x, y):
    """Number of leaves that differ between two projections."""
    if isinstance(x, dict) and isinstance(y, dict):
        return sum(changed(x.get(k), y.get(k))
                   for k in set(x) | set(y))
    if isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        return sum(changed(a, b) for a, b in zip(x, y))
    return 0 if x == y else 1


def main():
    a, b = sys.argv[1], sys.argv[2]
    ea, eb = load(a), load(b)
    pa = {k: project_entry(v) for k, v in ea.items()}
    pb = {k: project_entry(v) for k, v in eb.items()}
    print(f"A {a}\nB {b}")
    la, ga, pla = census(ea)
    lb, gb, plb = census(eb)
    print(f"fired-event census: A gated={ga} ungated={pla} | "
          f"B gated={gb} ungated={plb}")
    print(f"projected law leaves: A={leaves(pa)} B={leaves(pb)}")
    ok = True
    for k in sorted(set(pa) | set(pb)):
        va, vb = pa.get(k), pb.get(k)
        fa = ea.get(k, {}).get("failures")
        fb = eb.get(k, {}).get("failures")
        ka = la.get(k, [])
        kb = lb.get(k, [])
        same = json.dumps(va, sort_keys=True) == json.dumps(vb, sort_keys=True)
        if not same:
            ok = False
        print(f"\n== {k}: failures A={fa} B={fb} "
              f"legs A={len(ka)} B={len(kb)} law-projection "
              f"{'IDENTICAL' if same else 'DIFFERS'}")
        if ka != kb:
            ok = False
            print(f"   leg keys only in A: {sorted(set(ka) - set(kb))}")
            print(f"   leg keys only in B: {sorted(set(kb) - set(ka))}")
        if fa != fb:
            ok = False
        if not same:
            sa = json.dumps(va, indent=1, sort_keys=True).splitlines()
            sb = json.dumps(vb, indent=1, sort_keys=True).splitlines()
            d = list(difflib.unified_diff(sa, sb, "A", "B", lineterm="",
                                          n=1))
            print("\n".join(d[:300]))
            print(f"   ... {max(0, len(d) - 300)} more diff lines")
    print(f"\nVERDICT: "
          f"{'ALL law projections + verdicts identical' if ok else 'DIFFERS (see the hunks above)'}"
          f" | changed leaves {sum(changed(pa.get(k), pb.get(k)) for k in set(pa) | set(pb))}"
          f" / {leaves(pa)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
