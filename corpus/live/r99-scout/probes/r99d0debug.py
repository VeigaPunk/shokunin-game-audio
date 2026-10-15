#!/usr/bin/env python3
"""r99-scout: why is the crafted-sender receive path silent? debug-level trace."""
import json, os, sys, time

SEAT = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, SEAT)
import r99_probe as P

P.ENV["PIPEWIRE_DEBUG"] = "4"
P.write_fragment([("libpipewire-module-rtp-source", P.source_args())])
ok, msg = P.core_up(with_wp=True)
print("core:", ok, msg)
wav = os.path.join(P.RAW, "d0", "debug.wav")
rec = P.record(wav, "r99s_src", seconds=6)
time.sleep(1.5)
print("nodes during:", [(n["props"].get("node.name"), n["state"], n["n_in"], n["n_out"]) for n in P.nodes()])
print("links during:", P.sh("pw-link -l", timeout=6)[1].splitlines())
send = P.sender(46101, 3.0, group="239.255.42.99", ifname="lo", count=3000, ts0=0)
send.wait(timeout=8)
print("send:", send.stdout.read().decode().strip())
time.sleep(1.5)
print("nodes after:", [(n["props"].get("node.name"), n["state"], n["n_in"], n["n_out"]) for n in P.nodes()])
P.kill(rec)
time.sleep(0.5)
print("wav:", json.dumps(P.wav_analyze(wav)))
log = open(os.path.join(SEAT, "runs", "core.log")).read().splitlines()
keep = [l for l in log if any(k in l for k in ("rtp", "rtp-stream", "receiver", "sync", "underrun", "samples",
                                               "read", "write", "mod.rtp", "stream.c", "audio.c"))]
print("--- log lines of interest (%d):" % len(keep))
for l in keep[-40:]:
    print(l)
P.core_down()
