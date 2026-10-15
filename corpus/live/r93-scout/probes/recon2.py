#!/usr/bin/env python3
"""r93 recon2 — readout mechanism: pw-cli ids, enum-params, pw-dump -m under tone."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib93 as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(HERE, "receipts")
SCRATCH = os.path.join(HERE, "scratch")

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

res = {"stage": "recon2", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

# --- arm
sink = L.run(["pactl", "load-module", "module-null-sink", "sink_name=%s" % NS, "channels=1"], wall=6.0)
res["sink"] = sink.out.strip()
time.sleep(0.3)
cli = L.PwCli(idle=0.4, hard=4.0)
load_out, var = cli.load("libpipewire-module-filter-chain", ARGS)
res["load"] = load_out[-600:]
res["fc_var"] = var
time.sleep(0.8)

# ls Node through a second one-shot pw-cli
ls = L.run(["pw-cli"], wall=8.0, stdin_data=b"ls Node\nquit\n")
res["ls_node"] = ls.out[-4000:]

# node ids from pw-dump
d = L.run(["pw-dump"], wall=6.0)
objs = json.loads(d.out)
ids = {}
for o in objs:
    if o.get("type") == "PipeWire:Interface:Node":
        p = o.get("info", {}).get("props", {})
        if p.get("node.name") in (FC_IN, FC_OUT):
            ids[p["node.name"]] = {"id": o["id"], "serial": p.get("object.serial")}
res["ids"] = ids

# try enum-params in several id forms on the fc_in node
for label, key in (("fc_in", FC_IN), ("fc_out", FC_OUT)):
    if key not in ids:
        continue
    for form in (str(ids[key]["id"]), str(ids[key]["serial"])):
        e = L.run(["pw-cli"], wall=8.0,
                  stdin_data=("enum-params %s Props\nquit\n" % form).encode())
        res.setdefault("enum_tries", {})["%s-%s" % (label, form)] = (e.out + e.err)[-2500:]

# tone + pw-dump -m monitor
L.write_wav_f32(os.path.join(SCRATCH, "recon2_tone.wav"), L.sine(1000, 2.5, amp=0.5))
mon = L.Bg(["pw-dump", "-m", "-N"], wall=5.0)
time.sleep(0.5)
play = L.Bg(["pw-play", "--target", NS, os.path.join(SCRATCH, "recon2_tone.wav")], wall=6.0)
time.sleep(3.0)
mstop = mon.stop()
pstop = play.stop()
res["mon"] = {"rc": mstop["rc"], "dur": mstop["dur"]}
res["play"] = {"rc": pstop["rc"], "dur": pstop["dur"], "err": pstop["err"][-300:]}
res["mon_lines"] = [l for l in (mstop["out"] + mstop["err"]).splitlines()
                    if "r93s" in l or "LUFS" in l or "param" in l.lower()][:200]

# unload / teardown
if var is not None:
    res["unload"] = cli.cmd("unload-module %d" % var)[-200:]
cli.close()
time.sleep(0.4)
if sink.out.strip().isdigit():
    L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)

L.jdump(os.path.join(REC, "recon2.json"), res)
print("ids:", res["ids"])
print("ls_node:", res["ls_node"][:1200])
for k, v in res.get("enum_tries", {}).items():
    print("---", k, ":", v[:600].replace("\n", " | "))
print("mon_lines count:", len(res["mon_lines"]))
for l in res["mon_lines"][:60]:
    print("M>", l[:300])
