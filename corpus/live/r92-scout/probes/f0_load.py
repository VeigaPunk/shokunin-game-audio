#!/usr/bin/env python3
"""f0 — filter-chain load feasibility + load-shape census + lifecycle law.

Legs:
  L1  comma-form single-token args -> does pw-cli load-module parse it?
  L2  load shape: nodes/ports/props/media.class of a pw-cli-loaded filter-chain
  L3  what does WP link by itself (host-sink safety witness)
  L4  lifecycle: do the nodes die when the pw-cli process exits?
  L5  spaced-form args (control for the tokenizer)
No tone is ever played in this probe. Zero writes outside the seat dir.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(HERE, "runs", "f0")
os.makedirs(RUN, exist_ok=True)

ARGS_COMMA = (
    "node.description=r92s_fc,"
    "filter.graph={nodes=[{type=builtin,name=bq1,label=bq_lowpass,"
    "control={Freq=1000.0,Q=0.707}}]},"
    "audio.channels=1,audio.position=[MONO],"
    "capture.props={node.name=r92s_fc_in,node.autoconnect=false},"
    "playback.props={node.name=r92s_fc_out,node.autoconnect=false}"
)
ARGS_SPACED = ARGS_COMMA.replace(",", " ")


def census(tag):
    d = L.run(["pw-dump"], wall=6.0)
    try:
        objs = json.loads(d.out)
    except Exception:
        objs = []
    nodes = []
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        p = o.get("info", {}).get("props", {})
        nm = p.get("node.name", "")
        if not nm.startswith("r92s"):
            continue
        ports = [q["info"]["props"].get("port.name")
                 for q in objs if q.get("type") == "PipeWire:Interface:Port"
                 and q.get("info", {}).get("props", {}).get("node.id") == o["id"]]
        nodes.append({
            "id": o["id"], "node.name": nm,
            "media.class": p.get("media.class"),
            "node.autoconnect": p.get("node.autoconnect"),
            "node.passive": p.get("node.passive"),
            "audio.channels": p.get("audio.channels"),
            "audio.position": p.get("audio.position"),
            "media.type": p.get("media.type"),
            "stream.is-live": p.get("stream.is-live"),
            "node.latency": p.get("node.latency"),
            "node.driver-id": p.get("node.driver-id"),
            "factory.name": p.get("factory.name"),
            "node.description": p.get("node.description"),
            "port.names": ports,
            "state": o.get("info", {}).get("state"),
        })
    lk = L.run(["pw-link", "-l"], wall=5.0).out
    mine = [l for l in lk.splitlines() if "r92s" in l]
    to_spdif = [l for l in lk.splitlines() if "SPDIF" in l]
    return {"tag": tag, "n_r92s_nodes": len(nodes), "nodes": nodes,
            "r92s_links": mine, "spdif_links": to_spdif}


def leg(name, args, ttag):
    rec = {"leg": name, "args": args}
    rec["census_before"] = census(name + "-before")
    cli = L.PwCli()
    rec["cli_greeting"] = cli.log[0][-500:]
    out, mid = cli.load("libpipewire-module-filter-chain", args)
    rec["load_out"] = out[-2000:]
    rec["module_id_parsed"] = mid
    time.sleep(0.6)
    rec["census_live"] = census(name + "-live")
    if mid is not None:
        rec["unload_out"] = cli.cmd("unload-module %d" % mid)[-800:]
        time.sleep(0.4)
        rec["census_after_unload"] = census(name + "-after-unload")
    log = cli.close()
    time.sleep(0.7)
    rec["census_after_exit"] = census(name + "-after-exit")
    rec["cli_log_tail"] = "".join(log)[-1500:]
    return rec


def main():
    res = {"probe": "f0", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    res["args_comma"] = ARGS_COMMA
    res["legs"] = []
    res["legs"].append(leg("L1L4-comma-form", ARGS_COMMA, "comma"))
    res["legs"].append(leg("L5-spaced-form", ARGS_SPACED, "spaced"))
    L.jdump(os.path.join(RUN, "receipt.json"), res)
    print(json.dumps({
        "L1_load_out": res["legs"][0]["load_out"][-600:],
        "L1_module_id": res["legs"][0]["module_id_parsed"],
        "L1_nodes_live": res["legs"][0]["census_live"]["n_r92s_nodes"],
        "L1_nodes_after_exit": res["legs"][0]["census_after_exit"]["n_r92s_nodes"],
        "L1_spdif_links_live": res["legs"][0]["census_live"]["spdif_links"],
        "L5_load_out": res["legs"][1]["load_out"][-400:],
        "L5_nodes_live": res["legs"][1]["census_live"]["n_r92s_nodes"],
        "nodes_detail": res["legs"][0]["census_live"]["nodes"],
    }, indent=1)[:6000])


if __name__ == "__main__":
    main()
