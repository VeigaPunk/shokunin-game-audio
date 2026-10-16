#!/usr/bin/env python3
"""r99 author fixture: own RTP/UDP codec, tone generator and LAN counter.

This is the r99 family's own implementation of the RTP wire surface it
measures — no third-party RTP tool is involved (the host has no
`roc`/`snapcast`/`jack-trip`, and `module-rtp-sink`'s peer is this file).
It exists so that every r99 claim is read off bytes this repository
produced and parsed itself.

Modes
-----
  tone  --wav F --out J --seconds S [--freq HZ] [--amp I16] [--rate R]
        Write an int16 stereo RIFF/WAVE tone to --wav and its receipt to
        --out.  The two paths are separate because --out always carries
        the JSON: one path cannot hold both.  Defaults match the family
        stimulus: 997 Hz, int16 peak 16383 (= 0.499969482421875 as float).

  recv  --port P --seconds S --out J [--group G --ifname IF]
        [--bufsize N] [--maxpkts N] [--min-arrivals N]
        Bind a UDP socket, optionally join a multicast group, capture for
        S seconds and write the RTP analysis to J.  The concatenated
        payload is written to `<J>.payload`.  `--bufsize` defaults to
        65535: the r99-boundary showed a 2048-byte receive buffer
        truncates a large datagram and manufactures a false "packet cap"
        (FALSIFIED C9b), so the default here is deliberately large.

  send  --port P --seconds S --out J [--host H] [--from-port FP]
        [--group G --ifname IF] [--ssrc S] [--pt PT] [--frames N]
        [--rate R] [--ts0 T] [--count N] [--freq HZ] [--amp I16]
        [--format s16|s24] [--seq0 N]
        Emit a tone as an RTP stream.  `--group` + `--ifname` set
        SO_BINDTODEVICE and IP_MULTICAST_IF so a loopback-bound send can
        never leak onto another interface.  `--ts0` defaults to a
        deliberately arbitrary value (1000000) — the r99-boundary's
        corrected crafted-delivery law needs no clock alignment.

  wav   --file F --out J [--max-seconds S]
        Analyse an int16 stereo WAV this repository produced.

Every mode writes exactly one JSON object to --out and prints it to
stdout.  No mode touches a PipeWire object: the fixture owns plain
unprivileged AF_INET sockets and plain files.  Interface counters for
the loopback-confinement law are read by the harness, not here, so that
the arm window's boundaries stay in one process.
"""
import argparse
import array
import json
import math
import os
import socket
import struct
import sys
import time

RTP_HEADER = 12


# ------------------------------------------------------------------ tone
def make_tone(seconds, freq=997.0, amp=16383, rate=48000):
    n = int(round(seconds * rate))
    two_pi_f = 2.0 * math.pi * freq / rate
    samples = array.array("h", bytes(4 * n))
    for i in range(n):
        v = int(round(amp * math.sin(two_pi_f * i)))
        samples[2 * i] = v
        samples[2 * i + 1] = v
    # NOTE: no byteswap.  A RIFF/WAVE data chunk is little-endian, and
    # array("h").tobytes() is already native little-endian on this host.
    # (decode_s16be DOES byteswap: an RTP L16 payload is big-endian.)
    return samples.tobytes()


def write_wav(path, data, rate=48000, channels=2):
    hdr = (b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE"
           + b"fmt " + struct.pack("<IHHIIHH", 16, 1, channels, rate,
                                   rate * channels * 2, channels * 2, 16)
           + b"data" + struct.pack("<I", len(data)))
    with open(path, "wb") as fh:
        fh.write(hdr)
        fh.write(data)


def read_wav(path):
    """Minimal RIFF reader for the family's own int16 stereo files."""
    with open(path, "rb") as fh:
        raw = fh.read()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError("not a RIFF/WAVE file")
    pos, fmt, data = 12, None, None
    while pos + 8 <= len(raw):
        cid = raw[pos:pos + 4]
        size = struct.unpack("<I", raw[pos + 4:pos + 8])[0]
        body = raw[pos + 8:pos + 8 + size]
        if cid == b"fmt ":
            fmt = struct.unpack("<HHIIHH", body[:16])
        elif cid == b"data":
            data = body
        pos += 8 + size + (size & 1)
    if fmt is None or data is None:
        raise ValueError("missing fmt/data chunk")
    # struct "<HHIIHH" unpacks to (format, channels, rate, byte_rate,
    # block_align, bits) — six fields, so the channels/rate pair sits at
    # index 1/2, not 2/3.
    _format, channels, rate, _byte_rate, _block_align, _bits = fmt
    a = array.array("h")
    a.frombytes(data[:len(data) - (len(data) % (2 * channels))])
    left = [v / 32768.0 for v in a[0::channels]]
    right = ([v / 32768.0 for v in a[1::channels]]
             if channels > 1 else list(left))
    return {"channels": channels, "rate": rate, "frames": len(left),
            "left": left, "right": right}


# ------------------------------------------------------------------ dsp
def goertzel(x, freq, rate=48000):
    """Power of one bin (r99 convention: squared, unnormalised)."""
    n = len(x)
    if n == 0:
        return 0.0
    k = int(0.5 + n * freq / rate)
    w = 2.0 * math.pi * k / n
    coeff = 2.0 * math.cos(w)
    q1 = q2 = 0.0
    for v in x:
        q0 = coeff * q1 - q2 + v
        q2, q1 = q1, q0
    return q1 * q1 + q2 * q2 - coeff * q1 * q2


def tone_slice_fraction(x, rate=48000, freq=997.0, amp=16383.0, step=16):
    """Fraction of non-zero samples that sit on the exact tone lattice.

    The r99-boundary's qualification of C5: at 1 ms ptime the ring is not
    always filled, so the payload is tone-with-holes.  A sample is 'on
    the lattice' when it equals the tone value for some frame index
    congruent to its own index mod `step` (16-sample granularity).
    """
    n = len(x)
    if n == 0:
        return None
    two_pi_f = 2.0 * math.pi * freq / rate
    exact = nonzero = 0
    for i, v in enumerate(x):
        if v == 0.0:
            continue
        nonzero += 1
        if abs(v - int(round(amp * math.sin(two_pi_f * i))) / 32768.0) < 1e-9:
            exact += 1
    if nonzero == 0:
        return {"nonzero": 0, "exact": 0, "fraction": None}
    return {"nonzero": nonzero, "exact": exact, "fraction": exact / nonzero}


def longest_zero_run(x):
    best = run = 0
    for v in x:
        if v == 0.0:
            run += 1
            if run > best:
                best = run
        else:
            run = 0
    return best


def decode_s16be(payload, channels=2):
    a = array.array("h")
    a.frombytes(payload[:len(payload) - (len(payload) % 2)])
    if sys.byteorder == "little":
        a.byteswap()
    left = [v / 32768.0 for v in a[0::channels]]
    right = ([v / 32768.0 for v in a[1::channels]]
             if channels > 1 else list(left))
    return left, right


def decode_s24be(payload, channels=2):
    out = []
    stride = 3 * channels
    for off in range(0, len(payload) - stride + 1, 3):
        v = (payload[off] << 16) | (payload[off + 1] << 8) | payload[off + 2]
        if v & 0x800000:
            v -= 1 << 24
        out.append(v / 8388608.0)
    return out[0::channels], out[1::channels]


# ------------------------------------------------------------------ rtp
def rtp_packet(seq, ts, ssrc, payload, pt=127, marker=0):
    hdr = struct.pack("!BBHII", 0x80, (marker << 7) | (pt & 0x7f), seq & 0xffff,
                      ts & 0xffffffff, ssrc & 0xffffffff)
    return hdr + payload


def analyse(packets, sizes_note=None):
    """RTP analysis over a list of (t_rel, datagram) pairs."""
    if not packets:
        return {"n": 0}
    sizes = sorted(set(len(p[1]) for p in packets))
    h = packets[0][1]
    seqs = [int.from_bytes(p[1][2:4], "big") for p in packets]
    tss = [int.from_bytes(p[1][4:8], "big") for p in packets]
    ia = [round(packets[i + 1][0] - packets[i][0], 6)
          for i in range(min(40, len(packets) - 1))]
    span = packets[-1][0] - packets[0][0]
    res = {
        "n": len(packets),
        "sizes": sizes,
        "rate_pkt_s": round(len(packets) / span, 1) if span > 0 else None,
        "span_s": round(span, 4),
        "rtp": {"version": h[0] >> 6,
                "padding": (h[0] >> 5) & 1,
                "extension": (h[0] >> 4) & 1,
                "csrc_count": h[0] & 0x0f,
                "marker": h[1] >> 7,
                "pt": h[1] & 0x7f,
                "seq0": seqs[0], "ts0": tss[0],
                "ssrc": "%08x" % int.from_bytes(h[8:12], "big")},
        "seq_deltas": sorted(set((seqs[i + 1] - seqs[i]) % 65536
                                 for i in range(len(seqs) - 1))),
        "ts_deltas": sorted(set((tss[i + 1] - tss[i]) % 2 ** 32
                                for i in range(len(tss) - 1))),
        "inter_arrival_s": ia,
    }
    return res


# ------------------------------------------------------------------ modes
def do_tone(args):
    data = make_tone(args.seconds, args.freq, args.amp, args.rate)
    write_wav(args.wav, data, args.rate, 2)
    res = {"path": args.wav, "bytes": len(data), "frames": len(data) // 4,
           "freq": args.freq, "amp_i16": args.amp, "rate": args.rate,
           "peak": args.amp / 32768.0}
    return res


def _iface_ipv4(ifname):
    """The interface's own IPv4 address, via SIOCGIFADDR.  Needed because
    IP_MULTICAST_IF takes an `struct in_addr` (the interface ADDRESS), not
    an ifindex: passing the ifindex silently selects 1.0.0.0 and the send
    goes nowhere.  `IP_ADD_MEMBERSHIP` takes an `ip_mreqn`, which is why
    the receive side uses the ifindex and the send side does not."""
    import fcntl
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(
            fcntl.ioctl(s.fileno(), 0x8915,
                        struct.pack("256s", ifname.encode()[:15]))[20:24])
    except OSError:
        return None
    finally:
        s.close()


def _bind(args, port):
    """Bind the wildcard address and JOIN the group, never bind the group
    address itself: the RTP source module binds the group, and a second
    socket bound to the same specific address would compete for the
    datagrams the measurement depends on."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port))
    if args.group:
        ifidx = socket.if_nametoindex(args.ifname)
        mreq = (socket.inet_aton(args.group) + socket.inet_aton("0.0.0.0")
                + struct.pack("I", ifidx))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return s


def do_recv(args):
    s = _bind(args, args.port)
    s.settimeout(0.2)
    t0 = time.monotonic()
    packets = []
    peers = set()
    while time.monotonic() - t0 < args.seconds and len(packets) < args.maxpkts:
        try:
            d, a = s.recvfrom(args.bufsize)
            packets.append((time.monotonic() - t0, d))
            peers.add("%s:%d" % a)
        except socket.timeout:
            continue
    s.close()
    res = analyse(packets)
    res.update({"port": args.port, "group": args.group, "ifname": args.ifname,
                "seconds": args.seconds, "bufsize": args.bufsize,
                "peers": sorted(peers)})
    payload = b"".join(p[1][RTP_HEADER:] for p in packets)
    with open(args.out + ".payload", "wb") as fh:
        fh.write(payload)
    res["payload_bytes"] = len(payload)
    res["payload_sha256"] = _sha(payload)
    if payload:
        try:
            left, right = decode_s16be(payload)
            res["content"] = {
                "frames": len(left),
                "peak_l": round(max(abs(v) for v in left), 9),
                "peak_r": round(max(abs(v) for v in right), 9),
                "nonzero_l": sum(1 for v in left if v != 0.0),
                "longest_zero_run": longest_zero_run(left),
                "goertzel_L": {str(f): round(goertzel(left, f, 48000), 1)
                               for f in (440, 997, 2000)},
                "tone_lattice": tone_slice_fraction(left),
            }
        except Exception as exc:  # pragma: no cover - diagnostic only
            res["content"] = {"error": repr(exc)[:200]}
    return res


def do_send(args):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # SO_REUSEADDR is required for the C8b arm, where the sender binds the
    # very port the source module already holds: the module's own socket is
    # a wildcard bind, so a specific bind can only coexist in the same
    # reuse group.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if args.ifname:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE,
                     args.ifname.encode() + b"\0")
    if args.from_port:
        s.bind(("0.0.0.0", args.from_port))
    if args.group:
        addr = _iface_ipv4(args.ifname or "lo")
        if addr is None:
            s.close()
            return {"sent": 0, "error": "no IPv4 address on %r" % args.ifname}
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
                     struct.pack("4s", socket.inet_aton(addr)))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,
                     struct.pack("b", args.ttl))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP,
                     struct.pack("b", 1))
    src_port = s.getsockname()[1]
    # `--group` selects the destination; `--host` is the unicast form.  A
    # group arm that silently kept the default unicast host would send the
    # whole stream to 127.0.0.1 and the module — bound to the group — would
    # record silence for a reason that has nothing to do with the module.
    dest = (args.group, args.port) if args.group else (args.host, args.port)
    tone = make_tone(max(args.seconds, args.count * args.frames / args.rate),
                     args.freq, args.amp, args.rate)
    sent = 0
    t0 = time.monotonic()
    seq = args.seq0
    ts = args.ts0
    try:
        while sent < args.count and time.monotonic() - t0 < args.seconds:
            nbytes = args.frames * 2 * 2
            off = (sent * nbytes) % max(1, len(tone) - nbytes)
            chunk = tone[off:off + nbytes]
            if len(chunk) < nbytes:
                chunk = chunk + bytes(nbytes - len(chunk))
            s.sendto(rtp_packet(seq, ts, args.ssrc, chunk, args.pt), dest)
            seq += 1
            ts += args.frames
            sent += 1
            time.sleep(args.frames / args.rate)
    except OSError as exc:
        s.close()
        return {"sent": sent, "error": str(exc)[:160]}
    s.close()
    return {"sent": sent, "dest": list(dest), "host": args.host,
            "port": args.port,
            "mcast_if": addr if args.group else None,
            "from_port": src_port,
            "ssrc": "%08x" % args.ssrc, "pt": args.pt, "ts0": args.ts0,
            "frames_per_packet": args.frames, "span_s": round(time.monotonic() - t0, 3)}


def _sha(data):
    import hashlib
    return hashlib.sha256(data).hexdigest()


def do_wav(args):
    """Analyse an int16 stereo WAV this repository produced.

    The receive-path peak is reported, never armed: the r99-boundary
    reproduced an unexplained overshoot on the source side, so the armed
    laws are presence, spectral dominance and the exact tone lattice.
    """
    w = read_wav(args.file)
    left = w["left"]
    if args.max_seconds:
        left = left[:int(args.max_seconds * w["rate"])]
    res = {
        "file": args.file, "frames": w["frames"], "rate": w["rate"],
        "channels": w["channels"], "analysed_frames": len(left),
        "peak": round(max(abs(v) for v in left), 9) if left else None,
        "rms": round(math.sqrt(sum(v * v for v in left) / max(1, len(left))), 9),
        "nonzero": sum(1 for v in left if v != 0.0),
        "longest_zero_run": longest_zero_run(left),
        "goertzel_L": {str(f): round(goertzel(left, f, w["rate"]), 1)
                       for f in (440, 997, 2000)},
        "tone_lattice": tone_slice_fraction(left, rate=w["rate"]),
    }
    return res


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)

    t = sub.add_parser("tone")
    t.add_argument("--wav", required=True)
    t.add_argument("--out", required=True)
    t.add_argument("--seconds", type=float, default=1.5)
    t.add_argument("--freq", type=float, default=997.0)
    t.add_argument("--amp", type=int, default=16383)
    t.add_argument("--rate", type=int, default=48000)

    r = sub.add_parser("recv")
    r.add_argument("--port", type=int, required=True)
    r.add_argument("--seconds", type=float, default=3.0)
    r.add_argument("--out", required=True)
    r.add_argument("--group", default=None)
    r.add_argument("--ifname", default="lo")
    r.add_argument("--bufsize", type=int, default=65535)
    r.add_argument("--maxpkts", type=int, default=200000)

    s = sub.add_parser("send")
    s.add_argument("--port", type=int, required=True)
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--group", default=None)
    s.add_argument("--ifname", default="lo")
    s.add_argument("--ttl", type=int, default=1)
    s.add_argument("--from-port", type=int, default=0)
    s.add_argument("--seconds", type=float, default=4.0)
    s.add_argument("--count", type=int, default=100000)
    s.add_argument("--frames", type=int, default=48)
    s.add_argument("--rate", type=int, default=48000)
    s.add_argument("--ssrc", type=lambda v: int(v, 0), default=0x5A5A0001)
    s.add_argument("--pt", type=int, default=127)
    s.add_argument("--seq0", type=int, default=0)
    s.add_argument("--ts0", type=lambda v: int(v, 0), default=1000000)
    s.add_argument("--freq", type=float, default=997.0)
    s.add_argument("--amp", type=int, default=16383)
    s.add_argument("--out", required=True)

    w = sub.add_parser("wav")
    w.add_argument("--file", required=True)
    w.add_argument("--max-seconds", type=float, default=0.0)
    w.add_argument("--out", required=True)

    args = ap.parse_args()
    fn = {"tone": do_tone, "recv": do_recv, "send": do_send,
          "wav": do_wav}[args.mode]
    res = fn(args)
    res["mode"] = args.mode
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print(json.dumps(res))


if __name__ == "__main__":
    sys.exit(main())
