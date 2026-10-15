#!/usr/bin/env python3
"""r93 nullprobe — verbatim load output for the `null` label shapes."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib93 as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(HERE, "receipts")
NS = "r93s_in"
FC_IN, FC_OUT = "r93s_fc_in", "r93s_fc_out"


def mk(nodes, ins, outs):
    return ("node.description=r93s_fc,"
            "filter.graph={nodes=[%s],links=[],inputs=[%s],outputs=[%s]},"
            "audio.channels=1,audio.position=[MONO],"
            "capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},"
            "playback.props={node.name=%s,node.autoconnect=false}"
            % (nodes, ",".join('"%s"' % i for i in ins),
               ",".join('"%s"' % o for o in outs), FC_IN, FC_OUT))


cases = {
    "null_only_outnull": mk("{type=builtin,name=x,label=null}", ["x:In"], ["null"]),
    "null_plus_copy": mk("{type=builtin,name=x,label=null},{type=builtin,name=c,label=copy}",
                         ["x:In"], ["c:Out"]),
    "null_out_in": mk("{type=builtin,name=x,label=null}", ["x:In"], ["x:In"]),
    "copy_control_ref": mk("{type=builtin,name=c,label=copy}", ["c:In"], ["c:Out"]),
}
res = {"stage": "nullprobe", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
for name, args in cases.items():
    sink = L.run(["pactl", "load-module", "module-null-sink", "sink_name=%s" % NS,
                  "channels=1"], wall=6.0)
    time.sleep(0.25)
    cli = L.PwCli(idle=0.4, hard=3.0)
    lo, var = cli.load("libpipewire-module-filter-chain", args)
    res[name] = {"load_ok": var is not None, "out": lo[-1500:]}
    if var is not None:
        cli.cmd("unload-module %d" % var)
    cli.close()
    time.sleep(0.3)
    if sink.out.strip().isdigit():
        L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)
    time.sleep(0.2)
L.jdump(os.path.join(REC, "nullprobe.json"), res)
for k, v in res.items():
    if k == "stage" or k == "ts":
        continue
    print("==", k, "load_ok:", v["load_ok"])
    for l in v["out"].splitlines():
        if "[E]" in l or "[W]" in l or "Error" in l or "cannot" in l:
            print("   ", l.strip()[:240])
