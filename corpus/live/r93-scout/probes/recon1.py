#!/usr/bin/env python3
"""r93 recon1 — ebur128 node topology + readout mechanism discovery (bounded)."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib93 as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(HERE, "receipts")
SCRATCH = os.path.join(HERE, "scratch")
RUNS = os.path.join(HERE, "runs")

NS = "r93s_in"
FC_IN, FC_OUT = "r93s_fc_in", "r93s_fc_out"
ARGS = (
    "node.description=r93s_fc,"
    "filter.graph={nodes=[{type=ebur128,name=e,label=ebur128}],"
    'inputs=["e:In DUAL MONO"],outputs=["e:Out DUAL MONO"]},'
    "audio.channels=1,audio.position=[MONO],"
    "capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},"
    "playback.props={node.name=%s,node.autoconnect=false}" % (FC_IN, FC_OUT)
)

res = {"stage": "recon1", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def census_nodes():
    d = L.run(["pw-dump"], wall=6.0)
    try:
        objs = json.loads(d.out)
    except Exception:
        objs = []
    out = []
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        p = o.get("info", {}).get("props", {})
        nm = p.get("node.name", "")
        if nm.startswith("r93s") or p.get("node.description") == "r93s_fc":
            out.append({"id": o["id"], "name": nm, "class": p.get("media.class"),
                        "state": o.get("info", {}).get("state")})
    return out, objs


# preflight: kill any r93s residue
pre = L.run(["ps", "-eo", "pid,cmd"], wall=5.0).out
stray = [l.strip()[:120] for l in pre.splitlines()
         if "r93s" in l and l.strip().split(None, 1)[-1].startswith(
             ("pw-", "pipewire", "pactl"))]
res["pre_stray"] = stray
for l in stray:
    try:
        os.kill(int(l.split()[0]), 9)
    except Exception:
        pass
mods = [l.split()[0] for l in L.run(["pactl", "list", "modules", "short"], wall=6.0).out.splitlines()
        if "r93s" in l]
for m in mods:
    L.run(["pactl", "unload-module", m], wall=6.0)
res["pre_modules"] = mods
time.sleep(0.4)

sink = L.run(["pactl", "load-module", "module-null-sink", "sink_name=%s" % NS, "channels=1"],
             wall=6.0)
res["sink"] = sink.as_dict()
time.sleep(0.3)

cli = L.PwCli(env={"PIPEWIRE_DEBUG": "3"}, idle=0.5, hard=6.0)
load_out, var = cli.load("libpipewire-module-filter-chain", ARGS)
res["load_out"] = load_out[-3000:]
res["fc_var"] = var
time.sleep(1.0)

# capture full debug log for the port table
res["cli_log_full"] = "".join(cli.log)[-20000:]

nodes, objs = census_nodes()
res["nodes"] = nodes

# full pw-dump of the two nodes
for n in nodes:
    d = L.run(["pw-dump", str(n["id"])], wall=6.0)
    n["pw_dump"] = d.out[-12000:]

# enum-params Props on both nodes
for n in nodes:
    e = L.run(["pw-cli"], wall=8.0, stdin_data=("enum-params %d Props\nquit\n" % n["id"]).encode())
    n["enum_props"] = (e.out + e.err)[-6000:]

# pw-mon for 3 s while nothing plays
mon = L.Bg(["pw-mon", "-N"], wall=4.0)
time.sleep(3.0)
m = mon.stop()
keep = [l for l in (m["out"] + m["err"]).splitlines()
        if ("r93s" in l or FC_IN in l or FC_OUT in l or "param" in l.lower())]
res["pw_mon_lines"] = keep[-80:]

# unload + teardown
if var is not None:
    res["unload"] = cli.cmd("unload-module %d" % var)[-300:]
cli.close()
time.sleep(0.5)
if sink.rc == 0 and sink.out.strip().isdigit():
    res["sink_unload"] = L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0).as_dict()
time.sleep(0.3)
nodes_after, _ = census_nodes()
res["nodes_after"] = nodes_after
res["pactl_after"] = [l for l in L.run(["pactl", "list", "modules", "short"], wall=6.0).out.splitlines()
                      if "r93s" in l]

L.jdump(os.path.join(REC, "recon1.json"), res)
print(json.dumps({k: v for k, v in res.items() if k not in ("cli_log_full", "nodes")},
                 indent=1)[:3000])
print("=== NODES ===")
print(json.dumps(res["nodes"], indent=1)[:6000])
print("=== PORT TABLE ===")
for l in res["cli_log_full"].splitlines():
    if "using port" in l or "loaded n_" in l or "[E]" in l or "[W]" in l:
        print(l.strip()[:200])
