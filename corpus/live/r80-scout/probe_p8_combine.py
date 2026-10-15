#!/usr/bin/env python3
"""P8 — combine-sink slave spelling, default sink name, rate/format landing,
remap master topology.  REPS reps per row."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r80_probe import Receipt, load, unload, snap, pactl, run

REPS = 3
T = "r80_z"


def nodes_of(idx, s=None):
    s = s or snap()
    return {k: v for k, v in s["nodes"].items() if v.get("pulse.module.id") == idx}


def full_props(nid):
    d = run(["pw-dump", str(nid)])
    try:
        return json.loads(d["stdout"])[0]["info"]
    except Exception:
        return {}


def main():
    rc = Receipt("p8-combine-and-params")
    defsink = pactl("get-default-sink")["stdout"].strip()
    rc.note(f"default sink = {defsink}")

    # a private null sink to use as a literal slave/master name
    base, rbase = load("module-null-sink", f"sink_name={T}_base")
    time.sleep(0.4)
    rc.note(f"base null sink idx={base}")

    ROWS = [
        ("combine-slaves-literal", "module-combine-sink", [f"sink_name={T}_c1", f"slaves={T}_base"]),
        ("combine-sinks-literal", "module-combine-sink", [f"sink_name={T}_c2", f"sinks={T}_base"]),
        ("combine-slaves-default", "module-combine-sink", [f"sink_name={T}_c3", f"slaves={defsink}"]),
        ("combine-slaves-two", "module-combine-sink", [f"sink_name={T}_c4", f"slaves={T}_base,{defsink}"]),
        ("combine-noargs", "module-combine-sink", [f"sink_name={T}_c5"]),
        ("combine-latcomp", "module-combine-sink", [f"sink_name={T}_c6", f"slaves={T}_base", "latency_compensate=false"]),
        ("combine-adjust", "module-combine-sink", [f"sink_name={T}_c7", f"slaves={T}_base", "adjust_time=1"]),
        ("combine-remix", "module-combine-sink", [f"sink_name={T}_c8", f"slaves={T}_base", "remix=no"]),
        ("null-noargs-name", "module-null-sink", []),
        ("null-rate44", "module-null-sink", [f"sink_name={T}_r44", "rate=44100"]),
        ("null-rate96", "module-null-sink", [f"sink_name={T}_r96", "rate=96000"]),
        ("null-rate-odd", "module-null-sink", [f"sink_name={T}_rod", "rate=99999"]),
        ("null-fmt-s16", "module-null-sink", [f"sink_name={T}_f16", "format=s16le"]),
        ("null-fmt-u8", "module-null-sink", [f"sink_name={T}_f8", "format=u8"]),
        ("null-chmap-passthrough", "module-null-sink", [f"sink_name={T}_cp", "sink_properties=node.pause-on-idle=false monitor.passthrough=false"]),
        ("remap-master-mine", "module-remap-sink", [f"sink_name={T}_rm", f"master={T}_base"]),
        ("remap-master-mine-51", "module-remap-sink", [f"sink_name={T}_rm5", f"master={T}_base",
                                                       "master_channel_map=front-left,front-right",
                                                       "channels=1", "channel_map=mono"]),
        ("remap-bad-master", "module-remap-sink", [f"sink_name={T}_rmx", "master=no_such_sink"]),
        ("echo-master-mine", "module-echo-cancel", [f"sink_name={T}_ec", f"source_name={T}_ecs",
                                                    f"sink_master={T}_base",
                                                    f"source_master={defsink}.monitor",
                                                    "aec_method=webrtc"]),
        ("echo-bad-master", "module-echo-cancel", [f"sink_name={T}_ecx", f"source_name={T}_ecxs",
                                                   "sink_master=no_such_sink",
                                                   "source_master=no_such_source",
                                                   "aec_method=webrtc"]),
        ("echo-bad-method", "module-echo-cancel", [f"sink_name={T}_ecy", f"source_name={T}_ecys",
                                                   "aec_method=nosuchmethod"]),
        ("loopback-mine", "module-loopback", [f"sink_name={T}_lb", f"source={T}_base.monitor",
                                              f"sink={T}_base"]),
    ]
    for label, mod, args in ROWS:
        reps = []
        for rep in range(REPS):
            idx, r = load(mod, *args)
            time.sleep(0.7)
            s = snap()
            ns = nodes_of(idx, s) if idx else {}
            ids = set(int(k) for k in ns)
            links = [l["out"] + "->" + l["in"] for l in s["links"]
                     if l["out.node"] in ids or l["in.node"] in ids]
            ps = pactl("list", "short", "sinks")["stdout"]
            pss = pactl("list", "short", "sources")["stdout"]
            # params for the first node
            par = {}
            for k in list(ns)[:1]:
                info = full_props(k)
                ef = (info.get("params") or {}).get("EnumFormat")
                par = {"EnumFormat": ef, "n_in": info.get("n-input-ports"),
                       "n_out": info.get("n-output-ports"),
                       "state": info.get("state"),
                       "props_subset": {kk: vv for kk, vv in (info.get("props") or {}).items()
                                        if kk in ("media.class", "node.name", "factory.name",
                                                  "node.description", "audio.channels",
                                                  "audio.position", "pulse.module.id",
                                                  "node.driver", "monitor.passthrough",
                                                  "node.pause-on-idle", "node.virtual",
                                                  "node.autoconnect", "node.group",
                                                  "node.link-group", "object.linger")}}
            u = unload(idx) if idx else None
            reps.append({"rep": rep, "index": idx, "load": r, "nodes": ns, "links": links,
                         "params": par, "unload": u,
                         "pactl_sink_names": [l.split("\t")[1] for l in ps.splitlines()
                                              if len(l.split("\t")) > 1 and T in l],
                         "pactl_source_names": [l.split("\t")[1] for l in pss.splitlines()
                                                if len(l.split("\t")) > 1 and T in l]})
            time.sleep(0.3)
        sigs = {json.dumps({"rc": x["load"]["rc"], "err": x["load"]["stderr"].strip(),
                            "names": sorted(v["name"] for v in x["nodes"].values()),
                            "links": len(x["links"])}, sort_keys=True) for x in reps}
        rc.leg(label, {"module": mod, "args": args, "reps": reps, "stable": len(sigs) == 1})
        x = reps[0]
        rc.note(f"{label:24s} rc={x['load']['rc']} idx={x['index']} "
                f"err={x['load']['stderr'].strip()[:70]!r}")
        for k, v in x["nodes"].items():
            rc.note(f"     node {k} {v['name']} class={v['class']} in/out={v['n_in']}/{v['n_out']} ch={v['audio.channels']} pos={v['audio.position']} factory={v['factory']}")
        rc.note(f"     links={x['links'][:8]}")
        ef = x["params"].get("EnumFormat")
        if ef:
            rc.note(f"     EnumFormat={json.dumps(ef)[:300]}")
        rc.note(f"     pactl sinks={x['pactl_sink_names']} sources={x['pactl_source_names']}")
        time.sleep(0.3)
    unload(base)
    rc.close()


if __name__ == "__main__":
    main()
