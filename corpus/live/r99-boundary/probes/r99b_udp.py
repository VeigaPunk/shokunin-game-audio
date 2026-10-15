#!/usr/bin/env python3
"""r99-boundary UDP RTP capture/inject helper (own code, seat-local).

Modes
  recv --port P --seconds S --out OUT.json [--group G --ifname lo] [--bufsize 65535]
  send --port P --seconds S [--host H] [--group G --ifname lo] [--mcast-if 127.0.0.1]
       [--from-port FP] [--count N] [--frames N] [--freq F] [--ssrc S] [--ts0 T]

Differences from the scout's r99udp.py (deliberate, documented):
  * recv buffer default 65535 (the scout used recvfrom(2048) -> any datagram
    larger than 2048 B was silently truncated by the *tap*).
  * full seq/ts delta sets (not capped at 20) and per-packet (seq, ts, size).
  * multicast sends go to the group when --group is given (the scout's crafted
    arms passed --group but sent unicast to the default host 127.0.0.1).
  * payload continuity: byte-exact match against the seat's own 997 Hz tone
    generator (int(0.5*32767*sin)) at the best constant frame offset.
"""
import argparse, array, json, math, socket, struct, sys, time


def gso(x, f, sr=48000):
    n = len(x)
    if n == 0:
        return 0.0
    k = int(0.5 + n * f / sr)
    w = 2 * math.pi * k / n
    c, s = math.cos(w), math.sin(w)
    coeff = 2 * c
    q1 = q2 = 0.0
    for v in x:
        q0 = coeff * q1 - q2 + v
        q2, q1 = q1, q0
    return q1 * q1 + q2 * q2 - coeff * q1 * q2


def tone(n, f=997.0, rate=48000, amp=0.5):
    return int(amp * 32767 * math.sin(2 * math.pi * f * n / rate))


def decode(payload, channels=2):
    a = array.array("h")
    a.frombytes(payload[: len(payload) - (len(payload) % 2)])
    if sys.byteorder == "little":
        a.byteswap()
    return [v / 32768.0 for v in a[0::channels]], [v / 32768.0 for v in a[1::channels]]


def exactness(L, limit=2000, f=997.0, rate=48000):
    """Is the (non-silent part of the) left channel a constant-frame-shift copy
    of the tone?

    Skips the leading silence that an always-process RTP sink emits before a
    client is linked, then does a 24-sample filter over all offsets 0..4799 and
    a full `limit`-sample verification of every surviving candidate.
    """
    start = 0
    while start < len(L) and abs(L[start]) < 0.01:
        start += 1
    n = min(len(L) - start, limit)
    if n < 64:
        return {"checked": n, "best_offset": None, "mismatches": None, "exact": None,
                "silence_frames": start}
    seg = L[start:start + n]
    gen = [tone(i, f, rate) for i in range(4800 + n + 8)]
    vals = [int(v * 32768.0) for v in seg]
    cand = [o for o in range(4800) if all(vals[i] == gen[o + i] for i in range(24))]
    best = (None, None)
    for o in cand:
        mm = sum(1 for i in range(n) if vals[i] != gen[o + i])
        if best[1] is None or mm < best[1]:
            best = (o, mm)
        if mm == 0:
            break
    return {"checked": n, "best_offset": best[0], "mismatches": best[1],
            "candidates": len(cand), "exact": best[1] == 0, "silence_frames": start}


def do_recv(a):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", a.port))
    if a.group:
        ifidx = socket.if_nametoindex(a.ifname)
        mreq = struct.pack("4s4s", socket.inet_aton(a.group), socket.inet_aton("0.0.0.0")) + struct.pack("I", ifidx)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    s.settimeout(0.2)
    t0 = time.monotonic()
    pkts = []          # (t, bytes)
    peers = set()
    trunc = 0
    while time.monotonic() - t0 < a.seconds and len(pkts) < a.maxpkts:
        try:
            d, addr = s.recvfrom(a.bufsize)
            pkts.append((time.monotonic() - t0, d))
            peers.add("%s:%d" % addr)
        except socket.timeout:
            continue
        except OSError:
            trunc += 1
            continue
    out = {"n": len(pkts), "peers": sorted(peers), "port": a.port, "group": a.group,
           "ifname": a.ifname, "seconds": a.seconds, "bufsize": a.bufsize}
    if pkts:
        sizes = sorted(set(len(p[1]) for p in pkts))
        h = pkts[0][1][:12]
        seqs = [int.from_bytes(p[1][2:4], "big") for p in pkts]
        tss = [int.from_bytes(p[1][4:8], "big") for p in pkts]
        dseq = sorted(set((seqs[i + 1] - seqs[i]) % 65536 for i in range(len(seqs) - 1)))
        dts = sorted(set((tss[i + 1] - tss[i]) % (2 ** 32) for i in range(len(tss) - 1)))
        ia = [round(pkts[i + 1][0] - pkts[i][0], 5) for i in range(min(30, len(pkts) - 1))]
        times = [round(p[0], 4) for p in pkts]
        gaps = [[times[i], times[i + 1], round(times[i + 1] - times[i], 4)]
                for i in range(len(pkts) - 1) if times[i + 1] - times[i] > 0.003]
        out.update({
            "sizes": sizes,
            "hdr_hex": h.hex(),
            "rtp": {"version": h[0] >> 6, "pt": h[1] & 0x7f, "seq0": seqs[0],
                    "ts0": tss[0], "ssrc": "%08x" % int.from_bytes(h[8:12], "big"),
                    "marker": h[1] >> 7},
            "seq_deltas": dseq, "ts_deltas": dts,
            "inter_arrival": ia,
            "first_t": pkts[0][0], "last_t": pkts[-1][0],
            "pkt_times": times[:50000],
            "gaps_gt_3ms": gaps[:40],
            "distinct_ssrc": sorted(set("%08x" % int.from_bytes(p[1][8:12], "big") for p in pkts)),
            "pkts_meta": [{"seq": seqs[i], "ts": tss[i], "size": len(pkts[i][1])}
                          for i in range(min(400, len(pkts)))],
        })
        payload = b"".join(p[1][12:] for p in pkts)
        with open(a.out + ".payload", "wb") as f:
            f.write(payload)
        try:
            fl, fr = decode(payload, 2)
            out["content"] = {
                "frames": len(fl),
                "peak_l": round(max(abs(v) for v in fl), 6),
                "peak_r": round(max(abs(v) for v in fr), 6),
                "goertzel_L": {str(f): round(gso(fl, f), 1) for f in (440, 997, 2000)},
                "goertzel_R": {str(f): round(gso(fr, f), 1) for f in (440, 997, 2000)},
                "exact_997": exactness(fl),
            }
        except Exception as e:
            out["content"] = {"error": repr(e)}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("n", "sizes", "rtp", "seq_deltas", "ts_deltas") if k in out}))


def do_send(a):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if a.from_port:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", a.from_port))
    if a.group:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, a.ifname.encode())
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
                     struct.pack("4s", socket.inet_aton(a.mcast_if)))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, a.ttl)
        dest = (a.group, a.port)
    else:
        dest = (a.host, a.port)
    nframes = a.frames
    stride = 2 * a.channels
    t0 = time.monotonic()
    n = 0
    ts = a.ts0
    phase = 0.0
    while n < a.count and time.monotonic() - t0 < a.seconds:
        body = bytearray()
        for i in range(nframes):
            v = int(0.5 * 32767 * math.sin(2 * math.pi * a.freq * (phase + i) / a.rate))
            for _ in range(a.channels):
                body += struct.pack(">h", v)
        phase += nframes
        hdr = struct.pack(">BBHII", 0x80, a.pt, n & 0xffff, ts & 0xffffffff, a.ssrc)
        s.sendto(hdr + bytes(body), dest)
        ts += nframes
        n += 1
        target = t0 + n * nframes / a.rate
        dt = target - time.monotonic()
        if dt > 0:
            time.sleep(dt)
    print(json.dumps({"sent": n, "bytes": n * (12 + nframes * stride), "dest": dest,
                      "from_port": s.getsockname()[1], "ts0": a.ts0}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["recv", "send"])
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--seconds", type=float, default=3.0)
    ap.add_argument("--out", default="/dev/stdout")
    ap.add_argument("--maxpkts", type=int, default=200000)
    ap.add_argument("--bufsize", type=int, default=65535)
    ap.add_argument("--group", default=None)
    ap.add_argument("--ifname", default="lo")
    ap.add_argument("--mcast-if", default="127.0.0.1")
    ap.add_argument("--ttl", type=int, default=1)
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
