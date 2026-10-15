#!/usr/bin/env python3
"""f5 — corrected absent-class pass: every value that contains :, #, = or / is QUOTED.

The v2 `absent` stage invalidated its lv2/ffmpeg legs: spa-json rejects an
unquoted value containing ':' or '#' with `error parsing more than 0 properties`,
which is a *syntax* failure and says nothing about plugin availability.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib as L
import driver as D
import driver2 as D2

SCR, REC = D.SCRATCH, D.REC

LEGS = {
    "lv2-quoted-missing-uri":
        '{type=lv2,name=v,plugin="http://example.org/r92s#none",label="x"}',
    "lv2-quoted-spec-uri":
        '{type=lv2,name=v,plugin="http://lv2plug.in/ns/ext/atom",label="x"}',
    "lv2-quoted-urid":
        '{type=lv2,name=v,plugin="http://lv2plug.in/ns/ext/urid",label="x"}',
    "ffmpeg-quoted-label":
        '{type=ffmpeg,name=f,plugin=filtergraph,label="volume=0.5"}',
    "ffmpeg-quoted-highpass":
        '{type=ffmpeg,name=f,plugin=filtergraph,label="highpass=f=1000"}',
    "sofa-spatializer-no-file":
        '{type=sofa,name=s,label=spatializer,config={filename="/nonexistent/r92s.sofa"}}',
    "sofa-spatializer-noconfig":
        '{type=sofa,name=s,label=spatializer}',
    "ebur128-label-ebur128":
        '{type=ebur128,name=e,label=ebur128}',
    "ebur128-label-loudness":
        '{type=ebur128,name=e,label=loudness}',
    "ebur128-label-x":
        '{type=ebur128,name=e,label=x}',
    "ladspa-abs-path-plugin":
        '{type=ladspa,name=l,plugin="/usr/lib/libmltladspa",label="x"}',
}

res = {"probe": "f5_absent2", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
res["preflight"] = D2.preflight()
res["legs"] = {}
for name, node in LEGS.items():
    tok = ("node.description=r92s_fc,filter.graph={nodes=[%s]},audio.channels=1,"
           "audio.position=[MONO],capture.props={node.name=%s,node.autoconnect=false,"
           "media.class=Audio/Sink},playback.props={node.name=%s,node.autoconnect=false}"
           % (node, D2.FC_IN, D2.FC_OUT))
    rows = []
    for rep in range(3):
        b = L.run(["pw-cli"], wall=8.0, env={"PIPEWIRE_DEBUG": "3"}, stdin_data=(
            "load-module libpipewire-module-filter-chain " + tok + "\nquit\n").encode())
        ok = "@module:" in b.out
        keep = [l.strip()[:260] for l in b.out.splitlines()
                if "[E]" in l or "[W]" in l or "spa.filter-graph" in l or "plugin_" in l]
        rows.append({"rep": rep, "loaded": ok, "rc": b.rc, "log": keep[-8:]})
        time.sleep(0.15)
    res["legs"][name] = {"node": node, "rows": rows}
    first = rows[0]
    print("%-28s loaded=%-18s %s" % (name, [r["loaded"] for r in rows],
                                     (first["log"][-1][:150] if first["log"] else "-")))
    print("     args: %s" % tok[:200])

res["sweep"] = D2.sweep()
res["final"] = D2.live_r92s()
L.jdump(os.path.join(REC, "f5_absent2.json"), res)
print("sweep clean:", res["sweep"]["clean"])
