#!/usr/bin/env python3
"""r99-scout: crafted-sender receive path, with a tap on the same group.

Answers: do the crafted packets reach the group? does the source see them
(rtp.receiving / 'sync to timestamp' log)? does audio reach pw-record?
"""
import json, os, sys, time

SEAT = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, SEAT)
import r99_probe as P

P.ENV["PIPEWIRE_DEBUG"] = "4"
res = {}
for ts0 in (0, 1000000):
    P.write_fragment([("libpipewire-module-rtp-source", P.source_args())], objects=[P.NULL_SINK_OBJ])
    ok, msg = P.core_up(with_wp=True)
    tap = os.path.join(P.RAW, "d0", "crafted-ts%d.tap.json" % ts0)
    wav = os.path.join(P.RAW, "d0", "crafted-ts%d.wav" % ts0)
    p_tap = P.receiver(tap, 46101, 6.0, group="239.255.42.99", ifname="lo")
    rec = P.record(wav, "r99s_src", seconds=6)
    time.sleep(1.5)
    send = P.sender(46101, 3.0, group="239.255.42.99", ifname="lo", count=3000, ts0=ts0)
    send.wait(timeout=8)
    send_out = send.stdout.read().decode().strip()
    time.sleep(1.5)
    P.kill(rec)
    p_tap.wait(timeout=8)
    P.kill(p_tap)
    log = open(os.path.join(SEAT, "runs", "core.log")).read().splitlines()
    interesting = [l for l in log if ("sync to timestamp" in l or "timestamp: expected" in l or
                                      "rtp-source" in l or "overrun" in l or "underrun" in l)]
    res["ts%d" % ts0] = {"send": send_out, "tap": P.read_json(tap),
                         "src_props": P.node_props("r99s_src", ["rtp.", "node."]),
                         "wav": P.wav_analyze(wav),
                         "log": interesting[-12:]}
    P.core_down()
json.dump(res, open(os.path.join(P.REC, "crafted.json"), "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str)[:4000])
