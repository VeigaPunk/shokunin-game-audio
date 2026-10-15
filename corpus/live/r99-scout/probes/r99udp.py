#!/usr/bin/env python3
"""r99-scout: UDP RTP capture helper.

Modes:
  recv  --port P --seconds S --out OUT.json [--group G --ifname lo]
  send  --port P --seconds S --freq F [--from-port FP] [--count N] [--payload-file F]
        [--host H] [--ssrc S] [--pt PT] [--frames N] [--rate R]
Writes a JSON summary to --out plus (recv) the concatenated payload to <out>.payload.
All sockets are plain unprivileged AF_INET UDP sockets.
"""
import argparse, json, socket, struct, sys, time

def gso(x, f, sr=48000):
    n = len(x)
    if n == 0:
        return 0.0
    k = int(0.5 + n * f / sr)
    w = 2 * 3.141592653589793 * k / n
    c, s = __import__("math").cos(w), __import__("math").sin(w)
    coeff = 2 * c
    q1 = q2 = 0.0
    for v in x:
        q0 = coeff * q1 - q2 + v
        q2, q1 = q1, q0
    return q1 * q1 + q2 * q2 - coeff * q1 * q2


def decode_s16be(payload, channels=2):
    import array
    a = array.array("h")
    a.frombytes(bytes(payload))
    if sys.byteorder == "little":
        a.byteswap()
    return [v / 32768.0 for v in a[0::channels]], [v / 32768.0 for v in a[1::channels]]


def do_recv(args):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", args.port))
    if args.group:
        ifidx = socket.if_nametoindex(args.ifname)
        mreq = struct.pack("4s4s", socket.inet_aton(args.group), socket.inet_aton("0.0.0.0")) + struct.pack("I", ifidx)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    s.settimeout(0.2)
    t0 = time.monotonic()
    pkts = []
    peers = set()
    while time.monotonic() - t0 < args.seconds and len(pkts) < args.maxpkts:
        try:
            d, a = s.recvfrom(2048)
            pkts.append((time.monotonic() - t0, d))
            peers.add("%s:%d" % a)
        except socket.timeout:
            continue
    out = {"n": len(pkts), "peers": sorted(peers), "port": args.port, "group": args.group,
           "ifname": args.ifname, "seconds": args.seconds}
    if pkts:
        sizes = sorted(set(len(p[1]) for p in pkts))
        h = pkts[0][1][:12]
        seqs = [int.from_bytes(p[1][2:4], "big") for p in pkts]
        tss = [int.from_bytes(p[1][4:8], "big") for p in pkts]
        dseq = sorted(set((seqs[i + 1] - seqs[i]) % 65536 for i in range(len(seqs) - 1)))
        dts = sorted(set((tss[i + 1] - tss[i]) % (2 ** 32) for i in range(len(tss) - 1)))
        ia = [round(pkts[i + 1][0] - pkts[i][0], 5) for i in range(min(30, len(pkts) - 1))]
        out.update({
            "sizes": sizes,
            "hdr_hex": h.hex(),
            "rtp": {"version": h[0] >> 6, "pt": h[1] & 0x7f, "seq0": seqs[0],
                    "ts0": tss[0], "ssrc": "%08x" % int.from_bytes(h[8:12], "big"),
                    "marker": h[1] >> 7},
            "seq_deltas": dseq, "ts_deltas": dts[:20],
            "inter_arrival": ia,
            "first_t": pkts[0][0], "last_t": pkts[-1][0],
        })
        # content: concatenate payloads, decode as S16BE stereo
        payload = b"".join(p[1][12:] for p in pkts)
        with open(args.out + ".payload", "wb") as f:
            f.write(payload)
        try:
            fl, fr = decode_s16be(payload, 2)
            out["content"] = {
                "frames": len(fl),
                "peak_l": round(max(abs(v) for v in fl), 6),
                "peak_r": round(max(abs(v) for v in fr), 6),
                "goertzel_L": {str(f): round(gso(fl, f), 1) for f in (440, 997, 2000)},
                "goertzel_R": {str(f): round(gso(fr, f), 1) for f in (440, 997, 2000)},
            }
        except Exception as e:  # pragma: no cover
            out["content"] = {"error": repr(e)}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("n", "sizes", "rtp", "seq_deltas", "ts_deltas") if k in out}))


def do_send(args):
    import math
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if args.from_port:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", args.from_port))
    if args.group and args.ifname:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, args.ifname.encode())  # keep mcast off the LAN
        ifidx = socket.if_nametoindex(args.ifname)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, struct.pack("4s", socket.inet_aton(args.mcast_if)))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    dest = (args.host, args.port)
    nframes = args.frames
    stride = 2 * args.channels
    t0 = time.monotonic()
    n = 0
    ts = args.ts0
    phase = 0.0
    while n < args.count and time.monotonic() - t0 < args.seconds:
        body = bytearray()
        for i in range(nframes):
            v = int(0.5 * 32767 * math.sin(2 * math.pi * args.freq * (phase + i) / args.rate))
            for _ in range(args.channels):
                body += struct.pack(">h", v)
        phase += nframes
        hdr = struct.pack(">BBHII", 0x80, args.pt, n & 0xffff, ts & 0xffffffff, args.ssrc)
        s.sendto(hdr + bytes(body), dest)
        ts += nframes
        n += 1
        # pace at 1 packet per frame-count/sample-rate
        target = t0 + n * nframes / args.rate
        dt = target - time.monotonic()
        if dt > 0:
            time.sleep(dt)
    print(json.dumps({"sent": n, "bytes": n * (12 + nframes * stride), "host": args.host, "port": args.port,
                      "from_port": s.getsockname()[1]}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["recv", "send"])
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--seconds", type=float, default=3.0)
    ap.add_argument("--out", default="/dev/stdout")
    ap.add_argument("--maxpkts", type=int, default=20000)
    ap.add_argument("--group", default=None)
    ap.add_argument("--ifname", default="lo")
    ap.add_argument("--mcast-if", default="127.0.0.1")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--from-port", type=int, default=0)
    ap.add_argument("--count", type=int, default=2000)
    ap.add_argument("--freq", type=float, default=997.0)
    ap.add_argument("--rate", type=int, default=48000)
    ap.add_argument("--channels", type=int, default=2)
    ap.add_argument("--frames", type=int, default=48)
    ap.add_argument("--pt", type=int, default=127)
    ap.add_argument("--ssrc", type=lambda x: int(x, 0), default=0x99C0FFEE)
    ap.add_argument("--ts0", type=int, default=1000000)
    a = ap.parse_args()
    (do_recv if a.mode == "recv" else do_send)(a)


if __name__ == "__main__":
    main()
