#!/usr/bin/env python3
"""r93 recon4 — notify readout hunt: enum-params Props while a tone flows."""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib93 as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(HERE, "receipts")
SCRATCH = os.path.join(HERE, "scratch")

NS = "r93s_in"
FC_IN, FC_OUT = "r93s_fc_in", "r93s_fc_out"


def ebur_args(nodes, extra=""):
    return (
        "node.description=r93s_fc,"
        "filter.graph={nodes=[%s],%s"
        'inputs=["e:In DUAL MONO"],outputs=["e:Out DUAL MONO"]},'
        "audio.channels=1,audio.position=[MONO],"
        "capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},"
        "playback.props={node.name=%s,node.autoconnect=false}%s"
        % (nodes, extra, FC_IN, FC_OUT, ("", ",%s" % extra)[1] if extra else "")
    )


ARGS = ebur_args("{type=ebur128,name=e,label=ebur128}")

res = {"stage": "recon4", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

sink = L.run(["pactl", "load-module", "module-null-sink", "sink_name=%s" % NS, "channels=1"], wall=6.0)
res["sink"] = sink.out.strip()
time.sleep(0.3)
cli = L.PwCli(idle=0.4, hard=4.0)
load_out, var = cli.load("libpipewire-module-filter-chain", ARGS)
res["fc_var"] = var
time.sleep(0.8)

d = L.run(["pw-dump"], wall=6.0)
objs = json.loads(d.out)
ids = {}
for o in objs:
    if o.get("type") == "PipeWire:Interface:Node":
        p = o.get("info", {}).get("props", {})
        if p.get("node.name") in (FC_IN, FC_OUT):
            ids[p["node.name"]] = o["id"]
res["ids"] = ids


def link(a, b, tries=10):
    for i in range(tries):
        r = L.run(["pw-link", a, b], wall=4.0)
        if r.rc == 0 or "File exists" in r.err:
            return {"rc": 0, "tries": i + 1}
        time.sleep(0.25)
    return {"rc": r.rc, "err": r.err.strip()}


res["feed_link"] = link(f"{NS}:monitor_MONO", f"{FC_IN}:playback_MONO")
time.sleep(0.3)

tone = os.path.join(SCRATCH, "recon4_tone.wav")
L.write_wav_f32(tone, L.sine(1000, 6.0, amp=0.5))

sample_cli = L.PwCli(idle=0.3, hard=3.0)


def enum_props(nid, tag):
    txt = sample_cli.cmd("enum-params %d Props" % nid, idle=0.8, hard=5.0)
    blocks = []
    for m in re.finditer(r"object %d param (\d+) index (\d+)(.*?)(?=\nremote |\Z)" % nid,
                         txt, re.S):
        blocks.append({"param": int(m.group(1)), "index": int(m.group(2)),
                       "text": m.group(3)[:4000]})
    return {"tag": tag, "n_blocks": len(blocks), "blocks": blocks}


play = L.Bg(["pw-play", "--target", NS, tone], wall=10.0)
time.sleep(1.6)
res["t1_fc_in"] = enum_props(ids[FC_IN], "t1")
res["t1_fc_out"] = enum_props(ids[FC_OUT], "t1")
time.sleep(1.0)
res["t2_fc_in"] = enum_props(ids[FC_IN], "t2")
time.sleep(0.5)
# fresh pw-dump of the node mid-tone
d2 = L.run(["pw-dump", str(ids[FC_IN])], wall=6.0)
res["dump_mid"] = d2.out
time.sleep(1.0)
res["t3_fc_in"] = enum_props(ids[FC_IN], "t3")
pstop = play.stop()
res["play"] = {"rc": pstop["rc"], "dur": pstop["dur"], "err": pstop["err"][-300:]}

if var is not None:
    res["unload"] = cli.cmd("unload-module %d" % var)[-200:]
sample_cli.close()
cli.close()
time.sleep(0.4)
if sink.out.strip().isdigit():
    L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)

L.jdump(os.path.join(REC, "recon4.json"), res)
print("ids:", ids, "feed:", res["feed_link"], "play:", res["play"])
for k in ("t1_fc_in", "t1_fc_out", "t2_fc_in", "t3_fc_in"):
    v = res[k]
    print("=" * 20, k, "blocks:", v["n_blocks"])
    for b in v["blocks"][:3]:
        print("  param", b["param"], "index", b["index"])
        print("  ", b["text"][:1800].replace("\n", "\n   "))
print("dump_mid LUFS?", "LUFS" in res["dump_mid"], "len", len(res["dump_mid"]))
i = res["dump_mid"].find("Props")
print(res["dump_mid"][i - 200:i + 2000] if i >= 0 else res["dump_mid"][-1500:])
