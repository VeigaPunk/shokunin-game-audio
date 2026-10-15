#!/usr/bin/env python3
"""r99-scout: does a multicast send actually egress enp7s0?

Root-free method: /sys/class/net/enp7s0/statistics/tx_packets deltas around a
20 000-packet burst, compared against an idle baseline of the same duration.
Arms: idle | bound-lo (SO_BINDTODEVICE=lo + IP_MULTICAST_IF=127.0.0.1) | default-route.
"""
import socket, struct, sys, time

IF = "enp7s0"


def tx():
    return int(open("/sys/class/net/%s/statistics/tx_packets" % IF).read())


def burst(n, mode):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if mode == "bound-lo":
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b"lo")
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, struct.pack("4s", socket.inet_aton("127.0.0.1")))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)  # no local copy needed for this test
    s.connect(("239.255.42.96", 46195))
    payload = b"x" * 12
    for _ in range(n):
        s.send(payload)
    s.close()


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    res = {}
    for mode in ("idle", "bound-lo", "default-route"):
        deltas = []
        for _ in range(rounds):
            a = tx()
            t0 = time.monotonic()
            if mode != "idle":
                burst(n, mode)
            dt = time.monotonic() - t0
            b = tx()
            deltas.append({"delta": b - a, "seconds": round(dt, 3)})
            time.sleep(0.8)
        res[mode] = deltas
        print(mode, deltas)
    print("RESULT", res)


if __name__ == "__main__":
    main()
