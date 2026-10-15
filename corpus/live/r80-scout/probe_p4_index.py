#!/usr/bin/env python3
"""P4 — module-index semantics: allocation, recycling, unload-by-index vs
unload-by-name, double unload, bogus unload.  REPS reps per row."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r80_probe import Receipt, load, unload, snap, pactl, run

REPS = 3
T = "r80_p4"


def live_dynamic_modules():
    r = pactl("list", "short", "modules")
    out = []
    for ln in r["stdout"].splitlines():
        f = ln.split("\t")
        if len(f) >= 2 and f[0].strip().isdigit() and int(f[0]) >= 536870912:
            out.append((f[0].strip(), f[1].strip()))
    return out


def main():
    rc = Receipt("p4-index")
    for rep in range(REPS):
        legs = {}
        # ---- 1. allocation: 6 sequential loads, all live
        idxs = []
        for i in range(6):
            idx, r = load("module-null-sink", f"sink_name={T}_a{i}")
            idxs.append({"i": i, "idx": idx, "rc": r["rc"], "err": r["stderr"].strip()})
        legs["alloc_6_live"] = {"loads": idxs, "live": live_dynamic_modules()}
        rc.note(f"rep{rep} alloc 6 live -> {[x['idx'] for x in idxs]} live={live_dynamic_modules()}")

        # ---- 2. unload the middle one, reload: reuse?
        mid = idxs[2]["idx"]
        u = unload(mid)
        time.sleep(0.3)
        idx_new, r_new = load("module-null-sink", f"sink_name={T}_b")
        legs["recycle_after_mid_unload"] = {"unloaded": mid, "unload": u,
                                            "new": {"idx": idx_new, "rc": r_new["rc"],
                                                    "err": r_new["stderr"].strip()},
                                            "live": live_dynamic_modules()}
        rc.note(f"rep{rep} unload mid {mid} rc={u['rc']} -> reload idx={idx_new} (reuse={idx_new==mid})")

        # ---- 3. unload ALL of ours, then reload: what index?
        for x in idxs:
            if x["idx"]:
                unload(x["idx"])
        if idx_new:
            unload(idx_new)
        time.sleep(0.4)
        idx_after, r_after = load("module-null-sink", f"sink_name={T}_c")
        legs["alloc_after_all_free"] = {"idx": idx_after, "rc": r_after["rc"],
                                        "err": r_after["stderr"].strip(),
                                        "live": live_dynamic_modules()}
        rc.note(f"rep{rep} after all freed -> idx={idx_after}")

        # ---- 4. unload-by-name (module name string, not index)
        u_name = pactl("unload-module", "module-null-sink")
        time.sleep(0.3)
        still = [m for m in live_dynamic_modules() if T in m[1] or True]
        legs["unload_by_name"] = {"unload": u_name, "live_after": still,
                                  "our_node_still": [v["name"] for k, v in snap()["nodes"].items()
                                                     if (v.get("name") or "").startswith(T)]}
        rc.note(f"rep{rep} unload-module module-null-sink rc={u_name['rc']} "
                f"err={u_name['stderr'].strip()!r} live_after={still}")

        # ---- 5. unload with '#N' form and bare-number form on a fresh module
        idx2, _ = load("module-null-sink", f"sink_name={T}_d")
        time.sleep(0.3)
        u_hash = pactl("unload-module", f"#{idx2}")
        legs["unload_hash_form"] = {"idx": idx2, "unload": u_hash,
                                    "still_present": idx2 in [m[0] for m in live_dynamic_modules()]}
        rc.note(f"rep{rep} unload-module #{idx2} rc={u_hash['rc']} err={u_hash['stderr'].strip()!r} "
                f"still_present={idx2 in [m[0] for m in live_dynamic_modules()]}")

        idx3, _ = load("module-null-sink", f"sink_name={T}_e")
        time.sleep(0.3)
        u_bare = pactl("unload-module", str(idx3))
        u_twice = pactl("unload-module", str(idx3))
        u_bogus = pactl("unload-module", "536870000")
        legs["unload_bare_and_double"] = {"idx": idx3, "first": u_bare, "second": u_twice,
                                          "bogus": u_bogus}
        rc.note(f"rep{rep} bare unload rc={u_bare['rc']} / double rc={u_twice['rc']} "
                f"err={u_twice['stderr'].strip()!r} / bogus rc={u_bogus['rc']} err={u_bogus['stderr'].strip()!r}")

        # ---- 6. unload a STATIC module (module-stream-restore is harmless-ish)
        u_static = pactl("unload-module", "536870915")
        time.sleep(0.4)
        legs["unload_static_stream_restore"] = {"unload": u_static,
                                                "live": live_dynamic_modules()}
        rc.note(f"rep{rep} unload static 536870915 (module-stream-restore) rc={u_static['rc']} "
                f"err={u_static['stderr'].strip()!r} live={live_dynamic_modules()}")

        # ---- 7. does the object id / serial correlate with the module index?
        idx4, _ = load("module-null-sink", f"sink_name={T}_f")
        time.sleep(0.35)
        s = snap()
        n = {k: v for k, v in s["nodes"].items() if v.get("pulse.module.id") == idx4}
        legs["index_vs_object"] = {"idx": idx4, "nodes": n}
        rc.note(f"rep{rep} idx={idx4} node={[(k, v['name'], v['serial'], v['client.id']) for k, v in n.items()]}")
        unload(idx4)

        rc.leg(f"rep{rep}", legs)
        # cleanup any leftovers of ours
        for m in live_dynamic_modules():
            if T in m[1]:
                unload(m[0])
        time.sleep(0.3)
    rc.close()


if __name__ == "__main__":
    main()
