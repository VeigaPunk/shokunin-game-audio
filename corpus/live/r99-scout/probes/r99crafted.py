#!/usr/bin/env python3
"""r99-scout: crafted-sender receive path with an active graph (null sink present)."""
import json, os, sys, time
SEAT = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, SEAT)
import r99_probe as P

for ts0 in (0, 1000000):
    P.write_fragment([("libpipewire-module-rtp-source", P.source_args())], objects=[P.NULL_SINK_OBJ])
    ok, msg = P.core_up(with_wp=True)
    print("core:", ok, msg)
    wav = os.path.join(P.RAW, "d0", "crafted-ts%d.wav" % ts0)
    rec = P.record(wav, "r99s_src", seconds=6)
    time.sleep(1.5)
    print("nodes during:", [(n["props"].get("node.name"), n["state"], n["n_in"], n["n_out"]) for n in P.nodes()])
    send = P.sender(46101, 3.0, group="239.255.42.99", ifname="lo", count=3000, ts0=ts0)
    send.wait(timeout=8)
    time.sleep(1.5)
    print("links:", P.sh("pw-link -l", timeout=6)[1].splitlines()[:8])
    P.kill(rec); time.sleep(0.5)
    print("ts0=%d wav:" % ts0, json.dumps(P.wav_analyze(wav)))
    P.core_down()
