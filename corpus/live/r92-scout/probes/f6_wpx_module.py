#!/usr/bin/env python3
"""f6 — does a wpexec LocalModule's node set reach the live graph while it runs?

W4 proved LocalModule() is callable and returns a WpImplModule; its nodes were
never visible because the script called Core.quit() immediately. This leg keeps
the interpreter alive with Core.timeout_add so a census can see the graph.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib as L
import driver as D
import driver2 as D2

SCR, REC = D.SCRATCH, D.REC
ARGS = ("node.description=r92s_wpx,filter.graph={nodes=[{type=builtin,name=n0,label=copy}]},"
        "audio.channels=1,audio.position=[MONO],"
        "capture.props={node.name=r92s_wpx_in,node.autoconnect=false,media.class=Audio/Sink},"
        "playback.props={node.name=r92s_wpx_out,node.autoconnect=false}")

S = os.path.join(SCR, "f6_localmodule_hold.lua")
open(S, "w").write(r'''
print("LocalModule type=" .. type(LocalModule))
local ok, mod = pcall(LocalModule, "libpipewire-module-filter-chain", %s)
print("pcall ok=" .. tostring(ok) .. " mod=" .. tostring(mod))
Core.timeout_add(2500, function() print("quitting"); Core.quit() end)
''' % ('[==[' + ARGS + ']==]'))

res = {"probe": "f6", "script": S, "args": ARGS, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
res["preflight"] = D2.preflight()
rows = []
for rep in range(3):
    p = D.Bg(["wpexec", S], wall=10.0)
    time.sleep(1.2)
    c1 = D2.live_r92s()
    lk = L.run(["pw-link", "-l"], wall=5.0).out
    mid = {"nodes": c1["nodes"], "links": [l.strip() for l in lk.splitlines() if "r92s" in l],
           "spdif_links": [l.strip() for l in lk.splitlines() if "SPDIF" in l],
           "procs": c1["procs"]}
    alive = p.alive()
    st = p.stop()
    time.sleep(0.8)
    c2 = D2.live_r92s()
    rows.append({"rep": rep, "alive_at_1.2s": alive, "during": mid,
                 "stdout": st["out"][-400:], "stderr": st["err"][-300:], "rc": st["rc"],
                 "after_exit": c2["nodes"]})
    print("f6 r%d alive=%s during_nodes=%s during_links=%d spdif=%d after=%s rc=%s" %
          (rep, alive, mid["nodes"], len(mid["links"]), len(mid["spdif_links"]),
           c2["nodes"], st["rc"]))
    print("    stdout:", st["out"].strip().replace("\n", " | ")[:200])
    time.sleep(0.4)
res["rows"] = rows
res["sweep"] = D2.sweep()
res["final"] = D2.live_r92s()
L.jdump(os.path.join(REC, "f6_wpx_module.json"), res)
print("sweep clean:", res["sweep"]["clean"], "final:", res["final"])
