#!/usr/bin/env python3
"""r93 recon3 — do notify ports surface in Props? enum-params under a live tone."""
import json
import os
import subprocess
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

res = {"stage": "recon3", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

sink = L.run(["pactl", "load-module", "module-null-sink", "sink_name=%s" % NS, "channels=1"], wall=6.0)
res["sink"] = sink.out.strip()
time.sleep(0.3)
cli = L.PwCli(idle=0.4, hard=4.0)
load_out, var = cli.load("libpipewire-module-filter-chain", ARGS)
res["fc_var"] = var
time.sleep(0.8)

# find ids
d = L.run(["pw-dump"], wall=6.0)
objs = json.loads(d.out)
ids = {}
for o in objs:
    if o.get("type") == "PipeWire:Interface:Node":
        p = o.get("info", {}).get("props", {})
        if p.get("node.name") in (FC_IN, FC_OUT):
            ids[p["node.name"]] = o["id"]
res["ids"] = ids

# feed: link sink monitor -> fc_in playback_MONO, then tone
tone = os.path.join(SCRATCH, "recon3_tone.wav")
L.write_wav_f32(tone, L.sine(1000, 4.0, amp=0.5))

def link(a, b, tries=10):
    for i in range(tries):
        r = L.run(["pw-link", a, b], wall=4.0)
        if r.rc == 0 or "File exists" in r.err:
            return {"rc": 0, "tries": i + 1}
        time.sleep(0.25)
    return {"rc": r.rc, "err": r.err.strip()}

res["feed_link"] = link(f"{NS}:monitor_MONO", f"{FC_IN}:playback_MONO")
time.sleep(0.3)

# start tone, then enum-params mid-tone
play = L.Bg(["pw-play", "--target", NS, tone], wall=8.0)
time.sleep(1.2)
for name, nid in ids.items():
    out = cli.cmd("enum-params %d Props" % nid, idle=1.2, hard=6.0)
    res.setdefault("enum_props", {})[name] = out[-5000:]
time.sleep(1.5)
pstop = play.stop()
res["play"] = {"rc": pstop["rc"], "dur": pstop["dur"], "err": pstop["err"][-200:]}

# also monitor param events to a file while a second tone plays
monf = os.path.join(SCRATCH, "recon3_mon.json")
with open(monf, "w") as fh:
    mon = subprocess.Popen(["pw-dump", "-m", "-N"], stdout=fh, stderr=subprocess.STDOUT,
                           stdin=subprocess.DEVNULL, start_new_session=True, preexec_fn=L._ncore)
time.sleep(0.5)
play2 = L.Bg(["pw-play", "--target", NS, tone], wall=8.0)
time.sleep(2.5)
try:
    os.killpg(os.getpgid(mon.pid), 15)
except Exception:
    pass
mon.wait(timeout=3)
p2 = play2.stop()
res["play2"] = {"rc": p2["rc"], "dur": p2["dur"]}
# extract events mentioning our nodes or LUFS
ev = []
with open(monf, errors="replace") as fh:
    buf = fh.read()
for chunk in buf.split("remote 0 "):
    if ("r93s" in chunk or "LUFS" in chunk or "Mono" in chunk) and len(chunk) < 4000:
        ev.append(chunk.strip()[:800])
res["mon_events"] = ev[-40:]
res["mon_bytes"] = len(buf)

if var is not None:
    res["unload"] = cli.cmd("unload-module %d" % var)[-200:]
cli.close()
time.sleep(0.4)
if sink.out.strip().isdigit():
    L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)

L.jdump(os.path.join(REC, "recon3.json"), res)
for name, txt in res.get("enum_props", {}).items():
    print("=" * 30, name)
    print(txt[:4000])
print("MON events:", len(res["mon_events"]), "bytes:", res["mon_bytes"])
for e in res["mon_events"][:12]:
    print("EV>", e[:500].replace("\n", " | "))
