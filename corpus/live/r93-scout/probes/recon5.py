#!/usr/bin/env python3
"""r93 recon5 — notify->debug:Control log readout path (the crucial unknown)."""
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


def args_for(port, notify="Momentary LUFS", extra_nodes="", extra_links="", cfg=""):
    nodes = "{type=ebur128,name=e,label=ebur128%s},{type=builtin,name=dbg,label=debug}" % cfg
    if extra_nodes:
        nodes += "," + extra_nodes
    links = '{output="e:%s",input="dbg:Control"}' % notify
    if extra_links:
        links += "," + extra_links
    return (
        "node.description=r93s_fc,"
        'filter.graph={nodes=[%s],links=[%s],inputs=["e:In %s"],outputs=["e:Out %s"]},'
        "audio.channels=1,audio.position=[MONO],"
        "capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},"
        "playback.props={node.name=%s,node.autoconnect=false}"
        % (nodes, links, port, port, FC_IN, FC_OUT)
    )


res = {"stage": "recon5", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def link(a, b, tries=10):
    for i in range(tries):
        r = L.run(["pw-link", a, b], wall=4.0)
        if r.rc == 0 or "File exists" in r.err:
            return {"rc": 0, "tries": i + 1}
        time.sleep(0.25)
    return {"rc": r.rc, "err": r.err.strip()}


def one_leg(tag, args, tone_amp=0.5, dur=3.0):
    out = {"tag": tag}
    sink = L.run(["pactl", "load-module", "module-null-sink", "sink_name=%s" % NS,
                  "channels=1"], wall=6.0)
    out["sink"] = sink.out.strip()
    time.sleep(0.3)
    cli = L.PwCli(env={"PIPEWIRE_DEBUG": "3"}, idle=0.4, hard=4.0)
    load_out, var = cli.load("libpipewire-module-filter-chain", args)
    out["fc_var"] = var
    out["load_tail"] = load_out[-800:]
    time.sleep(0.8)
    out["feed"] = link(f"{NS}:monitor_MONO", f"{FC_IN}:playback_MONO")
    tone = os.path.join(SCRATCH, "recon5_tone.wav")
    L.write_wav_f32(tone, L.sine(1000, dur, amp=tone_amp))
    play = L.Bg(["pw-play", "--target", NS, tone], wall=dur + 6)
    # read the cli log for `dur` seconds while the tone plays
    import select
    buf = b""
    t0 = time.time()
    while time.time() - t0 < dur + 1.5:
        r, _, _ = select.select([cli.p.stdout], [], [], 0.2)
        if r:
            chunk = os.read(cli.p.stdout.fileno(), 262144)
            if not chunk:
                break
            buf += chunk
    txt = buf.decode("utf-8", "replace")
    out["log_bytes"] = len(txt)
    out["control_lines"] = [l.strip()[:160] for l in txt.splitlines() if "control:" in l]
    vals = [float(m.group(1)) for m in re.finditer(r"control:\s*(-?[\d.]+|nan|-?inf)", txt)]
    out["n_control"] = len(vals)
    out["first_vals"] = vals[:6]
    out["last_vals"] = vals[-6:]
    pstop = play.stop()
    out["play"] = {"rc": pstop["rc"], "dur": pstop["dur"]}
    if var is not None:
        cli.cmd("unload-module %d" % var)
    cli.close()
    time.sleep(0.4)
    if sink.out.strip().isdigit():
        L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)
    time.sleep(0.3)
    return out


legs = {}
legs["dual-mono"] = one_leg("dual-mono", args_for("DUAL MONO"))
legs["fl"] = one_leg("fl", args_for("FL"))
res["legs"] = legs

# quick label probes (do debug/ramp/zeroramp/sqrt/busy/null load?)
labels = ["debug", "ramp", "zeroramp", "sqrt", "busy", "null"]
lab = {}
for lb in labels:
    sink = L.run(["pactl", "load-module", "module-null-sink", "sink_name=%s" % NS,
                  "channels=1"], wall=6.0)
    time.sleep(0.2)
    cli = L.PwCli(idle=0.4, hard=3.0)
    a = ("node.description=r93s_fc,"
         'filter.graph={nodes=[{type=builtin,name=x,label=%s}]},'
         "audio.channels=1,audio.position=[MONO],"
         "capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},"
         "playback.props={node.name=%s,node.autoconnect=false}" % (lb, FC_IN, FC_OUT))
    lo, var = cli.load("libpipewire-module-filter-chain", a)
    lab[lb] = {"var": var, "tail": lo[-300:]}
    if var is not None:
        cli.cmd("unload-module %d" % var)
    cli.close()
    time.sleep(0.3)
    if sink.out.strip().isdigit():
        L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)
res["labels"] = lab

L.jdump(os.path.join(REC, "recon5.json"), res)
for k, v in res["legs"].items():
    print("=", k, "var:", v["fc_var"], "feed:", v["feed"], "log_bytes:", v["log_bytes"],
          "n_control:", v["n_control"])
    print("  first:", v["first_vals"], "last:", v["last_vals"])
    for l in v["control_lines"][:4]:
        print("  L>", l)
print("LABELS:", json.dumps(res["labels"], indent=1)[:1500])
