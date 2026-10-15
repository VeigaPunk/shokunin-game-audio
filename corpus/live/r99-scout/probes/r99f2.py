#!/usr/bin/env python3
"""r99-scout: refusal classes with proper log capture (bad ifname / tiny mtu / sap)."""
import json, os, sys, time
SEAT = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, SEAT)
import r99_probe as P
res={}
cases = {
 "bad_ifname": [("libpipewire-module-rtp-sink", P.sink_args(ifname="r99s_nosuchif"))],
 "tiny_mtu":   [("libpipewire-module-rtp-sink", P.sink_args(mtu=64))],
 "sap_default":[("libpipewire-module-rtp-sap", '{ sap.ip = "239.255.255.255" sap.port = 9875 net.loop = false }')],
}
for name, mods in cases.items():
    P.write_fragment(mods)
    ok, msg = P.core_up(with_wp=False)
    t0 = time.time()
    timeline=[]
    for i in range(6):
        time.sleep(0.5)
        n = P.node_props("r99s_sink", ["rtp.","node."]) if "sink" in mods[0][0] else None
        timeline.append({"t": round(time.time()-t0,1), "node": bool(n), "state": (n or {}).get("state")})
    log = open(os.path.join(SEAT,"runs","core.log")).read().splitlines()
    modlines=[l for l in log if ("rtp" in l.lower() or "mod.rtp" in l)]
    res[name]={"core_up":ok,"timeline":timeline,"module_log":modlines[-8:]}
    P.core_down()
json.dump(res, open(os.path.join(P.REC,"refusal-detail.json"),"w"), indent=1, default=str)
for k,v in res.items():
    print("=====",k, v["core_up"], v["timeline"])
    for l in v["module_log"]: print("   ", l[:190])
