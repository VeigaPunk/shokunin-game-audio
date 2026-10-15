#!/usr/bin/env python3
"""r78b p1 — forged / hostile target.object + --target variants on playback."""
import os, sys, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *

out = {"probe": "p1-forged-target", "ts": time.time(),
       "env": foreign_note()}
out["cleanup"] = unload_all_mine()
make_tone(TONE, dur=1.8)
TONE4 = os.path.join(RAW, "tone4.wav")
make_tone(TONE4, dur=4.0)

m1, _, _ = load_null(NS, "r78b probe A")
m2, _, _ = load_null(NS2, "r78b probe B")
time.sleep(0.6)
ns_serial = serial_of(NS)
ns2_serial = serial_of(NS2)
line_serial = serial_of(LINE)
out["serials"] = {"ns": ns_serial, "ns2": ns2_serial,
                  "line": line_serial,
                  "spdif": serial_of(S_SPDIF)}
# a real Port serial (ns playback_FL) for the port-serial forgery
out["port_serial"] = port_serial("playback_FL")  # first match; refine below
rc, o, e, _, _ = sh(["pw-dump"], timeout=10)
import json as _j
port_ser = None
try:
    for o_ in _j.loads(o.decode(errors="replace")):
        if o_.get("type") == "PipeWire:Interface:Port":
            p = o_.get("info", {}).get("props", {}) or {}
            if p.get("port.name") == "playback_FL" and \
               p.get("node.name") == NS if "node.name" in p else False:
                port_ser = p.get("object.serial")
except Exception:
    pass
# fallback: grab any Port whose object.serial exists and belongs to ns — scan
try:
    d = _j.loads(o.decode(errors="replace"))
    node_ids = {x["id"] for x in d
                if x.get("type") == "PipeWire:Interface:Node"
                and (x.get("info", {}).get("props", {}) or {}).get(
                    "node.name") == NS}
    for x in d:
        if x.get("type") == "PipeWire:Interface:Port":
            p = x.get("info", {}).get("props", {}) or {}
            if p.get("node.id") in node_ids or \
               (p.get("port.name") == "playback_FL"):
                port_ser = p.get("object.serial")
                break
except Exception:
    pass
out["port_serial"] = port_ser

legs = {}

def leg(name, args, env=None, timeout=10.0, actions=None,
        timeline_every=0.0, tone=TONE, monitors=None):
    tag = f"r78bA_{name}"
    argv = ["pw-play", "-P", f"node.name={tag}", *args, tone]
    legs[name] = play_leg(argv, tag, timeout=timeout, env=env,
                          actions=actions, timeline_every=timeline_every,
                          monitors=monitors)

# -- prop forgery -------------------------------------------------------
leg("srcname_prop", ["-P", f"target.object={LINE}"])
leg("monitor_prop", ["-P", f"target.object={S_SPDIF}.monitor"])
leg("srcserial_prop", ["-P", f"target.object={line_serial}"])
leg("bogus_serial_prop", ["-P", "target.object=99999999"])
leg("empty_prop", ["-P", "target.object="])
leg("portserial_prop",
    ["-P", f"target.object={port_ser}"] if port_ser else
    ["-P", "target.object=1"])
leg("glob_prop", ["-P", "target.object=r78b_*"])
leg("trailspace_prop", ["-P", f"target.object={NS} "])
leg("zeroprop", ["-P", "target.object=0"], timeout=8.0)

# -- flag forgery on the same shapes ------------------------------------
leg("srcname_flag", ["--target", LINE])
leg("u32max_flag", ["--target", "4294967295"])
leg("neg_flag", ["--target", "-1"], timeout=8.0)
leg("hex_flag", ["--target", "0x50"])
leg("ws_serial_flag", ["--target", f" {ns_serial} "])

# -- decoy stream node as target (flag + prop) ---------------------------
# spawn a decoy pw-play whose node.name we then forge as a target
dec = subprocess.Popen(["pw-play", "-P", "node.name=r78bA_decoy",
                        "--target", NS, TONE4],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.7)
legs["decoy_state"] = {"alive": dec.poll() is None,
                       "nodes": pw_objects_by_name("r78bA_decoy")}
leg("streamnode_prop", ["-P", "target.object=r78bA_decoy"], timeout=8.0)
leg("streamnode_flag", ["--target", "r78bA_decoy"], timeout=8.0)
dec.wait(timeout=6)

# -- duplicate sink name --------------------------------------------------
dm1, _, _ = load_null("r78b_dup", "r78b dup A")
time.sleep(0.3)
dm2, _, _ = load_null("r78b_dup", "r78b dup B")
time.sleep(0.5)
dup_nodes = pw_objects_by_name("r78b_dup")
out["dup_nodes"] = dup_nodes
dup_serials = [str(n["object.serial"]) for n in dup_nodes]
dup_wit = [("ns", NS), ("spdif", S_SPDIF)]
for i, s in enumerate(dup_serials[:2]):
    dup_wit.append((f"dup{i}_{s}", s))
mon = Monitors(sinks=dup_wit, tag="r78bdupmon")
leg("dupname_flag", ["--target", "r78b_dup"], monitors=mon)
mon = Monitors(sinks=dup_wit, tag="r78bdupmon")
leg("dupname_prop", ["-P", "target.object=r78b_dup"], monitors=mon)

# -- late bind: target loads AFTER the stream spawned ---------------------
def _load_late():
    mid_, rc_, e_ = load_null("r78b_late", "r78b late sink")
    return f"loaded={mid_} rc={rc_}"
mon = Monitors(sinks=[("ns", NS), ("spdif", S_SPDIF),
                      ("late", "r78b_late")], tag="r78blatemon")
leg("late_bind", ["--target", "r78b_late"], timeout=10.0,
    actions=[(0.8, _load_late)], timeline_every=0.25, tone=TONE4)
unload_all_mine(prefix="r78b_late")

# -- pin law variant: FL only ---------------------------------------------
def _pin_fl():
    r = sh(["pw-link", f"r78bA_pinfl:output_FL", f"{NS}:playback_FL"],
           timeout=6)
    return f"pinrc={r[0]} err={r[2].strip()[:80]}"
leg("pin_fl_only", ["--target", "0"], timeout=9.0,
    actions=[(1.6, _pin_fl)], timeline_every=0.4, tone=TONE4)

out["legs"] = legs
out["post_cleanup"] = unload_all_mine()
out["post_default"] = get_default_sink()
save("probe-p1-forged-target-r78b.json", out)
for k, l in legs.items():
    if isinstance(l, dict) and "rc" in l:
        print(f"{k:22s} rc={l['rc']} wall={l['wall_s']} "
              f"carried={l['carried']} err={l['stderr'][:60]!r}")
    else:
        print(k, l)
