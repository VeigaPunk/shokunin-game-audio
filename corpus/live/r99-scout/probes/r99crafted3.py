#!/usr/bin/env python3
"""r99-scout: crafted sender vs sess.ts-offset (default random vs pinned 0)."""
import json, os, sys, time
SEAT = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, SEAT)
import r99_probe as P
P.ENV["PIPEWIRE_DEBUG"] = "4"
res = {}
for tsoff in ("default", 0):
    args = P.source_args(extra_props=("sess.ts-offset = 0" if tsoff == 0 else ""))
    P.write_fragment([("libpipewire-module-rtp-source", args)], objects=[P.NULL_SINK_OBJ])
    ok, msg = P.core_up(with_wp=True)
    wav = os.path.join(P.RAW, "d0", "tsoff-%s.wav" % tsoff)
    rec = P.record(wav, "r99s_src", seconds=6)
    time.sleep(1.5)
    send = P.sender(46101, 3.0, group="239.255.42.99", ifname="lo", count=3000, ts0=0)
    send.wait(timeout=8)
    time.sleep(1.5)
    P.kill(rec); time.sleep(0.5)
    log = open(os.path.join(SEAT, "runs", "core.log")).read().splitlines()
    res[str(tsoff)] = {"wav": P.wav_analyze(wav),
                       "src_props": P.node_props("r99s_src", ["rtp.", "node."]),
                       "sync_log": [l for l in log if ("sync" in l or "expected" in l) and "rtp" in l][-6:]}
    P.core_down()
json.dump(res, open(os.path.join(P.REC, "crafted-tsoff.json"), "w"), indent=1, default=str)
for k, v in res.items():
    w = v["wav"] or {}
    print(k, "frames=", w.get("frames"), "peak=", w.get("peak_l"), "g997=", (w.get("goertzel_L") or {}).get("997"),
          "recv_ts_offset=", (v["src_props"] or {}).get("props", {}).get("rtp.receiver-ts-offset"))
    for l in v["sync_log"]: print("   ", l[:160])
