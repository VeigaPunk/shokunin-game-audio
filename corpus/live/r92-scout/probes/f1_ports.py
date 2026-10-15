#!/usr/bin/env python3
"""f1 — exact port names of every object in the hand-wired pipeline."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib as L
import driver as D

res = {"probe": "f1_ports", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

s_in = D.sink_load(D.NS_IN)
s_out = D.sink_load(D.NS_OUT)
res["sink_loads"] = [s_in, s_out]
time.sleep(0.5)


def dump(tag):
    d = L.run(["pw-dump"], wall=6.0)
    objs = json.loads(d.out)
    ports = {}
    nodes = {}
    for o in objs:
        p = o.get("info", {}).get("props", {})
        nm = p.get("node.name", "")
        if o.get("type") == "PipeWire:Interface:Node":
            nodes[o["id"]] = {"name": nm, "class": p.get("media.class"),
                              "ch": p.get("audio.channels"), "pos": p.get("audio.position"),
                              "state": o.get("info", {}).get("state")}
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Port":
            continue
        p = o.get("info", {}).get("props", {})
        nid = p.get("node.id")
        nm = nodes.get(nid, {}).get("name", "?")
        if nm.startswith("r92s") or nm.startswith("filter-chain-"):
            ports.setdefault(nm, []).append("%s (%s/%s)" % (p.get("port.name"),
                                                           p.get("port.direction"), p.get("format.dsp")))
    return {"tag": tag, "nodes": {k: v for k, v in nodes.items()
                                  if v["name"].startswith(("r92s", "filter-chain-"))},
            "ports": {k: sorted(v) for k, v in ports.items()}}


res["after_sinks"] = dump("after_sinks")

tok = D.fckwargs([D.NODE("bq_lowpass", Freq=1000.0, Q=0.707)])
res["fc_args"] = tok
p = D.Pipeline("f1", tok)
p.arm(link=False)
time.sleep(0.6)
res["after_fc"] = dump("after_fc")
res["load_out"] = p.load_out[-600:]
res["fc_log"] = p.fc_log()

# record node
rec = D.Bg(["pw-record", "-P", "node.name=%s" % D.RECN,
            "-P", "node.autoconnect=false", "/tmp/r92s_f1.wav"], wall=12.0)
time.sleep(0.8)
res["after_rec"] = dump("after_rec")

# player node
play = D.Bg(["pw-play", "-P", "node.name=%s" % D.PLAY,
             "-P", "node.autoconnect=false", os.path.join(D.SCRATCH, "tone.wav")], wall=12.0)
time.sleep(0.8)
res["after_play"] = dump("after_play")

# try every plausible link shape and record rc/err verbatim
tries = []
for a, b in [(f"{D.NS_IN}:monitor_MONO", f"{D.FC_IN}:input_MONO"),
             (f"{D.NS_IN}:monitor_FL", f"{D.FC_IN}:input_MONO"),
             (f"{D.FC_OUT}:output_MONO", f"{D.NS_OUT}:playback_MONO"),
             (f"{D.FC_OUT}:output_MONO", f"{D.NS_OUT}:playback_FL"),
             (f"{D.NS_OUT}:monitor_MONO", f"{D.RECN}:input_MONO"),
             (f"{D.NS_OUT}:monitor_FL", f"{D.RECN}:input_MONO"),
             (f"{D.PLAY}:output_MONO", f"{D.NS_IN}:playback_MONO"),
             (f"{D.PLAY}:output_MONO", f"{D.NS_IN}:playback_FL")]:
    r = L.run(["pw-link", a, b], wall=5.0)
    tries.append({"argv": [a, b], "rc": r.rc, "err": r.err.strip(), "out": r.out.strip()[:200]})
    time.sleep(0.2)
res["link_tries"] = tries
time.sleep(0.5)
lk = L.run(["pw-link", "-l"], wall=5.0).out
res["links_after"] = [l for l in lk.splitlines() if "r92s" in l]
res["rec_alive"] = rec.alive()
res["play_alive"] = play.alive()
res["rec_stop"] = rec.stop()
res["play_stop"] = play.stop()
time.sleep(0.4)
res["wav_bytes"] = os.path.getsize("/tmp/r92s_f1.wav") if os.path.exists("/tmp/r92s_f1.wav") else 0
res["teardown"] = p.disarm()
res["final"] = dump("final")
L.jdump(os.path.join(D.REC, "f1_ports.json"), res)
print(json.dumps({k: res[k] for k in ("after_sinks", "after_fc", "after_rec", "after_play",
                                      "link_tries", "links_after", "wav_bytes")}, indent=1)[:5000])
print("FINAL nodes:", {k: v["name"] for k, v in res["final"]["nodes"].items()})
