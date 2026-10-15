#!/usr/bin/env python3
"""r97b stage F — replay of the r97 scout settings lattice (claim 11, row
`wp.settings.lattice_25`) + the two metadata faces, with fresh processes.

Legs:
  f1 `wpctl settings` listing, 3 fresh processes: key count, sha256, byte order
  f2 pw-dump: the `schema-sm-settings` and `sm-settings` metadata objects
  f3 the same listing read from the OPERATOR's shared instance (READ-ONLY:
     `wpctl settings` with no arguments only reads) — cross-instance lattice
  f4 key-set diff private vs shared
Bounded: 12 s cap per call, process-group kill.
"""
import hashlib, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import (SEAT, ENV, REC, SCR, SHARED_ENV, run, dump, ensure_up,
                     stage_out, stage_write, loadavg, wp_ready)

SCOUT_LIST = os.path.join(os.path.dirname(SEAT), "r97-scout", "scratch", "settings_list.txt")


def parse_listing(text):
    keys = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("- Id:"):
            keys.append(s.split("Id:", 1)[1].strip())
    return keys


def meta_objects(objs):
    out = {}
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Metadata":
            name = (o.get("props") or {}).get("metadata.name")
            out[name] = {"id": o["id"], "rows": len(o.get("metadata") or []),
                         "keys": sorted({r.get("key") for r in (o.get("metadata") or [])})}
    return out


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out = stage_out("f_settings")
    out["arm"] = arm
    e = ensure_up(verbose=True)
    out["pair"] = e
    # MEASURED (first f pass): `wpctl settings` exits 3 with a 35 B listing when
    # WirePlumber is down, and the private graph then carries only the core's
    # `settings` metadata (8 rows), not the WP `schema-sm-settings`/`sm-settings`
    # pair. Gate on the sm-settings object, and record the gate result.
    ready, secs = wp_ready(timeout=20.0)
    out["wp_ready"] = {"ok": ready, "secs": secs, "loadavg": loadavg()}

    for n in range(reps):
        rep = {"rep": n, "legs": {}}
        r = run(["wpctl", "settings"], timeout=12.0)
        txt = r["stdout"]
        keys = parse_listing(txt)
        lp = os.path.join(SCR, f"f_settings_rep{n}.txt")
        open(lp, "w").write(txt)
        rep["legs"]["f1_listing"] = {
            "rc": r["rc"], "timed_out": r["timed_out"], "dur_s": r["dur_s"],
            "n_keys": len(keys), "keys": keys,
            "sha256": hashlib.sha256(txt.encode()).hexdigest(),
            "bytes": len(txt), "log": lp.replace(SEAT, "$SEAT"),
            "stderr_head": r["stderr"][:200], "loadavg": loadavg()}
        objs = dump()
        rep["legs"]["f2_metadata_faces"] = meta_objects(objs)
        out["reps"].append(rep)

    # f3/f4: shared instance, READ-ONLY listing
    rs = run(["wpctl", "settings"], timeout=15.0, env=SHARED_ENV)
    shared_keys = parse_listing(rs["stdout"])
    lp = os.path.join(SCR, "f_settings_shared.txt")
    open(lp, "w").write(rs["stdout"])
    priv_keys = out["reps"][0]["legs"]["f1_listing"]["keys"] if out["reps"] else []
    out["f3_shared_listing"] = {
        "rc": rs["rc"], "timed_out": rs["timed_out"], "dur_s": rs["dur_s"],
        "n_keys": len(shared_keys), "keys": shared_keys,
        "sha256": hashlib.sha256(rs["stdout"].encode()).hexdigest(),
        "bytes": len(rs["stdout"]), "log": lp.replace(SEAT, "$SEAT"),
        "stderr_head": rs["stderr"][:200], "loadavg": loadavg(),
        "note": "READ-ONLY: wpctl settings with no arguments lists; nothing written"}
    out["f4_diff"] = {
        "only_private": sorted(set(priv_keys) - set(shared_keys)),
        "only_shared": sorted(set(shared_keys) - set(priv_keys)),
        "same_order": priv_keys == shared_keys}
    if os.path.exists(SCOUT_LIST):
        st = open(SCOUT_LIST).read()
        out["f5_scout_list_compare"] = {
            "scout_sha256": hashlib.sha256(st.encode()).hexdigest(),
            "scout_bytes": len(st),
            "scout_n_keys": len(parse_listing(st)),
            "byte_identical_to_f1_rep0": st == out["reps"][0]["legs"]["f1_listing"] and None or
            (st == open(os.path.join(SCR, "f_settings_rep0.txt")).read()),
        }

    for rep in out["reps"]:
        L = rep["legs"]
        print(f"--- rep {rep['rep']} keys={L['f1_listing']['n_keys']} "
              f"sha={L['f1_listing']['sha256'][:16]} rc={L['f1_listing']['rc']} "
              f"{L['f1_listing']['dur_s']}s")
        print("    metadata faces:",
              {k: v["rows"] for k, v in L["f2_metadata_faces"].items()})
    print("--- shared (read-only) keys=%s sha=%s" % (
        out["f3_shared_listing"]["n_keys"], out["f3_shared_listing"]["sha256"][:16]))
    print("--- diff:", json.dumps(out["f4_diff"])[:300])
    if "f5_scout_list_compare" in out:
        print("--- scout list compare:", json.dumps(out["f5_scout_list_compare"]))
    stage_write(out, "f_settings.json")


if __name__ == "__main__":
    main()
