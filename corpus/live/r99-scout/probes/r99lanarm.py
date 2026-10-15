#!/usr/bin/env python3
"""r99-scout: measure the LAN footprint of the native rtp-sink multicast arm.

Arms (each: private core + rtp-sink, ~20 s of continuous RTP):
  idle      - core up, no rtp module
  mcast-lo  - destination 239.255.42.99, local.ifname=lo, net.loop=true
  mcast-en  - destination 239.255.42.99, local.ifname=enp7s0 (positive control)
Counts packets the sink actually emitted (loopback receiver joined on lo) and the
enp7s0 tx_packets delta over the same window.
"""
import json, os, subprocess, sys, time

SEAT = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, SEAT)
import r99_probe as P


def tx():
    return int(open("/sys/class/net/enp7s0/statistics/tx_packets").read())


def arm(name, modules, seconds=20.0, port=46101):
    P.write_fragment(modules)
    ok, msg = P.core_up(with_wp=True)
    if not ok:
        return {"arm": name, "error": msg}
    rec = os.path.join(P.RAW, "lan", "%s.recv.json" % name)
    os.makedirs(os.path.dirname(rec), exist_ok=True)
    p_recv = P.receiver(rec, port, seconds + 1.0, group="239.255.42.99", ifname="lo")
    time.sleep(0.8)
    play = P.play("r99s_sink", node_name="r99s_play") if modules else None
    a = tx()
    t0 = time.monotonic()
    time.sleep(seconds)
    b = tx()
    dt = time.monotonic() - t0
    P.kill(play)
    p_recv.wait(timeout=8)
    P.kill(p_recv)
    r = P.read_json(rec) or {}
    P.core_down()
    return {"arm": name, "seconds": round(dt, 2), "enp7s0_tx_delta": b - a,
            "emitted_packets": r.get("n"), "peers": r.get("peers"), "sizes": r.get("sizes")}


def main():
    out = []
    out.append(arm("idle", []))
    out.append(arm("mcast-lo", [("libpipewire-module-rtp-sink",
                                 P.sink_args(dest_ip="239.255.42.99", dest_port=46101, ifname="lo", loop=True))]))
    out.append(arm("mcast-en", [("libpipewire-module-rtp-sink",
                                 P.sink_args(dest_ip="239.255.42.99", dest_port=46101, ifname="enp7s0", loop=True))]))
    json.dump(out, open(os.path.join(P.REC, "lan-footprint.json"), "w"), indent=1)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
