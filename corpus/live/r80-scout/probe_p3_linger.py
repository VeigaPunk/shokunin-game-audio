#!/usr/bin/env python3
"""P3 — orphan inventory: what `object.linger=true` leaves behind after
`pactl unload-module`, and how each destruction path treats it."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r80_probe import Receipt, load, unload, snap, pactl, run, SEAT


def full_props(nid):
    r = run(["pw-dump", str(nid)], timeout=20)
    try:
        d = json.loads(r["stdout"])
        return (d[0].get("info", {}) or {}).get("props", {})
    except Exception:
        return {"_raw": r["stdout"][:500], "_rc": r["rc"]}


def main():
    rc = Receipt("p3-linger-orphans")
    s = snap()
    orphans = {k: v for k, v in s["nodes"].items()
               if (v.get("name") or "").startswith("r80")}
    rc.leg("orphan-inventory", {"nodes": orphans, "n": len(orphans)})
    rc.note(f"orphans at entry: {[(k, v['name'], v['pulse.module.id'], v['client.id'], v['obj_linger']) for k, v in orphans.items()]}")

    # Are orphans still visible to pactl as sinks?
    ps = pactl("list", "short", "sinks")
    pss = pactl("list", "short", "sources")
    rc.leg("pactl-view-of-orphans", {"sinks": ps, "sources": pss})
    rc.note("pactl short sinks: " + " | ".join(ps["stdout"].splitlines()))
    rc.note("pactl short sources: " + " | ".join(pss["stdout"].splitlines()))

    # full props of the first orphan
    first = next(iter(orphans), None)
    if first:
        fp = full_props(first)
        rc.leg("orphan-full-props", {"id": first, "props": fp})
        rc.note(f"orphan {first} props keys: {sorted(fp.keys())}")
        for k in ("object.linger", "client.id", "pulse.module.id", "node.name",
                  "media.class", "factory.name", "node.driver", "object.id",
                  "object.serial", "node.description", "monitor.passthrough",
                  "monitor.channel-volumes", "clock.quantum-limit", "node.loop.name",
                  "node.want-driver", "node.virtual", "node.autoconnect", "node.group"):
            rc.note(f"   {k} = {fp.get(k, '<absent>')!r}")

    # can the pulse server still unload / address them?
    if first:
        u = pactl("unload-module", str(orphans[first]["pulse.module.id"]))
        rc.leg("unload-orphans-module-index", {"unload": u,
                                               "id": first,
                                               "module_index": orphans[first]["pulse.module.id"]})
        rc.note(f"unload-module {orphans[first]['pulse.module.id']} rc={u['rc']} err={u['stderr'].strip()!r}")

    # native destroy
    if first:
        d = run(["pw-cli", "destroy", str(first)], timeout=20)
        time.sleep(0.5)
        s2 = snap()
        rc.leg("pw-cli-destroy-orphan", {"cmd": d, "still_present": first in s2["nodes"]})
        rc.note(f"pw-cli destroy {first} rc={d['rc']} err={d['stderr'].strip()[:80]!r} still_present={first in s2['nodes']}")

    # clean up any remaining r80 nodes
    left = []
    for k, v in sorted(snap()["nodes"].items()):
        if (v.get("name") or "").startswith("r80"):
            d = run(["pw-cli", "destroy", str(k)], timeout=20)
            left.append({"id": k, "name": v["name"], "rc": d["rc"], "err": d["stderr"].strip()})
            time.sleep(0.2)
    rc.leg("cleanup-remaining", {"destroyed": left})
    rc.note(f"cleanup: {left}")
    time.sleep(0.5)
    s3 = snap()
    rc.leg("post-cleanup", {"r80_nodes": {k: v["name"] for k, v in s3["nodes"].items()
                                           if (v.get("name") or "").startswith("r80")}})
    rc.close()


if __name__ == "__main__":
    main()
