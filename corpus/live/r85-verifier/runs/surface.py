#!/usr/bin/env python3
"""r85 verifier — tiered verdict-surface comparator (r83/r84 convention).

Usage: surface.py A.json B.json [label]

Tiers
  exact : the deterministic verdict surface after normalization —
          rc/signal/error_class/error_hit/killed_at_bound/expect/got/
          armed/alive_at_end/module_alive/source_alive/skipped/recycled/
          link shapes (node names + port names + state)/unit-table rows/
          unload records/structural booleans.
  named : armed-quantity buckets that the fixture itself arms (volume
          percent rows, serial-monotonicity shape). Mix phase/coherence
          realizations are NOT compared here — laws.py re-derives the
          armed bounds from the raw numbers.
  analog: never exact-diffed (timing, sizes, amps, indices, serials,
          pids, paths, module ids).

Normalization collapses pid runs, pactl/pw object ids + serials, module
indices, hex ids, tmp paths and seat namespaces (r85a_/r85v_/r85b_,
r85arole<pid>) to placeholders. `realization` fields are excluded from
the exact tier and reported separately (the three host-bimodal sites +
mix phase realizations are legitimately volatile; laws.py checks their
armed sets).
"""
import json
import re
import sys

# ---- keys never exact-diffed -------------------------------------------
ANALOG_KEYS = {
    "wall_s", "at_s", "waited_s", "tap_link_wait_s", "dur_s", "settle_s",
    "size", "size_at_loss", "bytes", "loss_bytes", "peak", "post_frames",
    "post_peak", "post_nonzero", "rail_frames", "rail_frac", "data_actual",
    "frames", "module_dead_at_s", "source_dead_at_s", "index", "sink",
    "source", "module_id", "node_id", "object_serial", "serial", "serials",
    "module_indices", "node_latency", "tap_exit", "player_exits",
    "sink_index", "ns2_index", "own_pid", "loadavg", "wall", "amp",
    "ratio", "dup_ratio", "delay_ratio", "residual_ratio", "l_a_med",
    "l_a_med_late", "peak_med", "rail_frac_med", "spur_max", "ref",
    "meds", "bleed", "clip", "amps", "windows", "post", "grid", "samples",
    "corked", "state", "volume", "mute",
}
# `samples`/`post`/`grid` are handled structurally below, not as blobs.
STRUCT_KEYS = {"samples", "post", "grid", "ref", "meds", "bleed", "clip",
               "amps", "windows"}
ANALOG_KEYS -= STRUCT_KEYS
ID_KEYS = {
    "object_id", "object.id", "node.id", "client.id", "factory.id",
    "device.id", "application.process.id", "application.process.session-id",
    "node.driver-id", "source_output_index", "verified_index", "captured",
    "module_stream_restore.id", "module-stream-restore.id",
}
VOLATILE_PROP_KEYS = {
    "client.id", "factory.id", "object.id", "object.serial", "node.id",
    "device.id", "node.driver-id", "application.process.id",
    "application.process.session-id", "clock.quantum-limit",
    "pulse.server.type", "config.name", "client.api", "media.filename",
    "media.name", "application.name", "media.role",
    "module-stream-restore.id", "target.object",
}
# realization fields are host-bimodal by design — reported, not exact-diffed
REALIZATION_KEY = "realization"

DIGITS = re.compile(r"\d+")
PATH = re.compile(r"/home/vgpnk/Projects/shokunin/tmp/[^\s'\"]+")
SEAT = re.compile(r"r85[abv][A-Za-z0-9_]*?(?=\d)")
HEX = re.compile(r"0x[0-9A-Fa-f]+")
NUMS = re.compile(r"\b\d{4,}\b")
ANALOG = "<ANALOG>"
IDV = "<ID>"


def norm_str(s):
    s = PATH.sub("<TMP>", s)
    s = SEAT.sub("r85<SEAT>", s)
    s = HEX.sub("<HEX>", s)
    s = DIGITS.sub("<N>", s)
    return s


def norm_edge(e):
    if not isinstance(e, dict):
        return norm_str(str(e))
    return {k: ("<STATE>" if k == "state"
                else norm_str(v) if isinstance(v, str) else v)
            for k, v in e.items()}


def proj(k, v):
    if k == REALIZATION_KEY:
        return "<REALIZATION>"
    if k in ANALOG_KEYS:
        return ANALOG
    if k in ID_KEYS:
        return IDV
    if k in ("links", "tap_link", "mix_edges"):
        return [norm_edge(e) for e in (v or [])]
    if k == "samples":
        return [{"at_s": ANALOG,
                 "links": [norm_edge(e) for e in (s.get("links") or [])],
                 "size": ANALOG,
                 "node_alive": s.get("node_alive")}
                for s in (v or [])]
    if k == "post":
        if not isinstance(v, dict):
            return v
        return {kk: (ANALOG if kk in ("post_frames", "post_peak",
                                      "post_nonzero", "loss_bytes",
                                      "bytes") else
                     vv if kk == "exists" else
                     "<REALIZATION>" if kk == "realization" else
                     norm_str(str(vv)) if isinstance(vv, str) else vv)
                for kk, vv in v.items()}
    if k == "grid":
        gs = v or []
        return {"n": ANALOG,
                "any_module_dead": any(not g.get("module") for g in gs),
                "any_source_dead": any(not g.get("source") for g in gs),
                "last": [bool(gs[-1].get("module")), bool(gs[-1].get("source"))]
                if gs else None}
    if k in ("ref", "meds", "bleed", "clip", "amps", "windows"):
        return ANALOG
    if k in ("properties", "props") and isinstance(v, dict):
        return {kk: norm_str(str(x)) for kk, x in v.items()
                if kk not in VOLATILE_PROP_KEYS
                and not kk.startswith("pulse.attr.")}
    if k == "unloads" and isinstance(v, dict):
        return {tag: proj("unload", rec) for tag, rec in v.items()}
    if k == "unload" and isinstance(v, dict):
        return {kk: (IDV if kk in ("verified_index", "captured")
                     else norm_str(str(vv)) if isinstance(vv, str)
                     else ANALOG if kk == "module_id" else vv)
                for kk, vv in v.items()}
    if k == "serial_cycles" and isinstance(v, dict):
        return {kk: [ANALOG for _ in (vv or [])]
                for kk, vv in v.items()}
    if k == "load_leaf" and isinstance(v, dict):
        return {kk: (IDV if kk in ("module_id",)
                     else ANALOG if isinstance(vv, float)
                     else norm_str(str(vv)) if isinstance(vv, str)
                     else vv)
                for kk, vv in v.items()}
    if isinstance(v, dict):
        return {kk: proj(kk, vv) for kk, vv in v.items()}
    if isinstance(v, list):
        return [proj(None, x) for x in v]
    if isinstance(v, str):
        return norm_str(v)
    if isinstance(v, float):
        return ANALOG
    return v


def project(rec):
    if not isinstance(rec, dict):
        return rec
    return {k: proj(k, v) for k, v in rec.items()}


def legs(doc):
    m = doc["measurements"] if "measurements" in doc else doc
    out = {}
    for entry, e in m.items():
        if "pactlmon" not in entry or not isinstance(e, dict) or \
                "legs" not in e:
            continue
        for leg, rec in e["legs"].items():
            out[f"{entry}/{leg}"] = rec
    return out


def realizations(doc):
    out = {}
    m = doc["measurements"] if "measurements" in doc else doc
    for entry, e in m.items():
        if "pactlmon" not in entry or not isinstance(e, dict):
            continue
        for leg, rec in (e.get("legs") or {}).items():
            if isinstance(rec, dict) and "realization" in rec:
                out[f"{entry}/{leg}"] = rec["realization"]
            elif isinstance(rec, dict) and isinstance(
                    rec.get("post"), dict) and "realization" in \
                    rec["post"]:
                out[f"{entry}/{leg}/post"] = rec["post"]["realization"]
    return out


def vol_pct(rec):
    if not isinstance(rec, dict):
        return None
    m = re.search(r"(\d+)\s*%", (rec.get("stdout") or ""))
    return int(m.group(1)) if m else None


def entry_view(doc):
    out = {}
    m = doc["measurements"] if "measurements" in doc else doc
    for entry, e in m.items():
        if "pactlmon" not in entry or not isinstance(e, dict):
            continue
        sc = e.get("serial_cycles") or {}
        sers = sc.get("serials") or []
        def nk(d):
            if not isinstance(d, dict):
                return d
            return {norm_str(str(k)): v for k, v in d.items()}
        out[entry] = {
            "failures": e.get("failures"),
            "blocked": e.get("blocked"),
            "coverage_blocked": e.get("coverage_blocked"),
            "sinks_gone": nk(e.get("sinks_gone")),
            "sources_gone": nk(e.get("sources_gone")),
            "own_nodes_after": [norm_str(str(x)) for x in
                                (e.get("own_nodes_after") or [])]
            if isinstance(e.get("own_nodes_after"), list)
            else e.get("own_nodes_after"),
            "serial_monotonic": (len(sers) == 3
                                 and all(isinstance(x, int) for x in sers)
                                 and sers == sorted(sers)
                                 and len(set(sers)) == 3) if sers else None,
            "leg_count": len(e.get("legs") or {}),
        }
    return out


def main():
    a = json.load(open(sys.argv[1]))
    b = json.load(open(sys.argv[2]))
    label = sys.argv[3] if len(sys.argv) > 3 else "AB"
    la, lb = legs(a), legs(b)
    keys = sorted(set(la) | set(lb))
    ex_diffs = []
    nm_diffs = []
    for k in keys:
        if k not in la or k not in lb:
            ex_diffs.append((k, "<missing>", "<missing>"))
            continue
        ea, eb = project(la[k]), project(lb[k])
        if ea != eb:
            ex_diffs.append((k, json.dumps(ea, sort_keys=True),
                             json.dumps(eb, sort_keys=True)))
        va, vb = vol_pct(la[k]), vol_pct(lb[k])
        if va is not None or vb is not None:
            if va != vb:
                nm_diffs.append((k, f"vol_pct={va}", f"vol_pct={vb}"))
    print(f"# {label}: legs A={len(la)} B={len(lb)} keys={len(keys)}")
    print(f"# exact diffs: {len(ex_diffs)}   named diffs: {len(nm_diffs)}")
    for k, x, y in ex_diffs:
        print(f"EXACT {k}\n  A={x[:900]}\n  B={y[:900]}")
    for k, x, y in nm_diffs:
        print(f"NAMED {k}: A={x} B={y}")
    ea_, eb_ = entry_view(a), entry_view(b)
    ediff = [(k, ea_.get(k), eb_.get(k)) for k in sorted(set(ea_) | set(eb_))
             if ea_.get(k) != eb_.get(k)]
    print(f"# entry-level diffs: {len(ediff)}")
    for k, x, y in ediff:
        print(f"ENTRY {k}\n  A={json.dumps(x, sort_keys=True)[:600]}"
              f"\n  B={json.dumps(y, sort_keys=True)[:600]}")
    ra, rb = realizations(a), realizations(b)
    rkeys = sorted(set(ra) | set(rb))
    rdiff = [(k, ra.get(k), rb.get(k)) for k in rkeys
             if ra.get(k) != rb.get(k)]
    print(f"# realization fields: {len(rkeys)} total, "
          f"{len(rdiff)} differ (host-bimodal by design)")
    for k, x, y in rdiff:
        print(f"REAL {k}: A={x} B={y}")
    return 1 if ex_diffs else 0


if __name__ == "__main__":
    sys.exit(main())
