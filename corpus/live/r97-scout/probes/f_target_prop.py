#!/usr/bin/env python3
"""r97-scout stage F — the property `pw-cat --target` actually writes.

Decides whether the numeric target is a global id (node.target) or a serial
(target.object): the stream node is dumped while it is linked.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97lib import SEAT, PwCli, dump, nullsink, sink_by_name, ensure_up
from d_linking import Stream, link_map

REC = os.path.join(SEAT, "receipts")


def stream_props(name):
    for o in dump() or []:
        if o.get("type") == "PipeWire:Interface:Node":
            p = (o.get("info") or {}).get("props", {})
            if p.get("node.name") == name:
                return {k: v for k, v in p.items()
                        if "target" in k or k in ("node.id", "object.serial",
                                                  "media.class", "node.autoconnect")}
    return None


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    ensure_up()
    out = {"stage": "f_target_property", "reps": []}
    for n in range(reps):
        cli = PwCli(logpath=os.path.join(SEAT, "scratch", f"pwcli_f{n}.log"))
        rec = {"rep": n}
        try:
            nullsink(cli, f"r97s_ta{n}", 100, 100)
            time.sleep(1.0)
            objs = dump()
            ida = sink_by_name(objs, f"r97s_ta{n}")
            serial = None
            for o in objs or []:
                if o.get("type") == "PipeWire:Interface:Node":
                    p = (o.get("info") or {}).get("props", {})
                    if p.get("node.name") == f"r97s_ta{n}":
                        serial = p.get("object.serial")
            rec["sink"] = {"global_id": ida, "object_serial": serial}
            for tag, target in (("by_serial", serial), ("by_global_id", ida)):
                st = Stream(target=target, props="{ node.name = r97s_str }")
                time.sleep(1.6)
                objs = dump()
                rec[tag] = {"target_arg": target,
                            "stream_props": stream_props("r97s_str"),
                            "links": [l for l in link_map(objs)
                                      if "r97s_str" in (l[0], l[1])]}
                st.stop()
                time.sleep(0.6)
            cli.cmd(f"destroy {ida}")
        finally:
            cli.close()
            time.sleep(0.5)
        out["reps"].append(rec)
    json.dump(out, open(os.path.join(REC, "f_target_property.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
