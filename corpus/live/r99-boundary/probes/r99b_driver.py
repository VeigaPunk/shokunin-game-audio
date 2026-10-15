#!/usr/bin/env python3
"""r99-boundary battery driver: replays the r99-scout armed cells with fresh
processes, quiet-ish and under load, and varies the named axes.

usage: r99b_driver.py cells --pass quiet|load [--only a,b,c] [--reps N]
       r99b_driver.py lan   --pass quiet|load
       r99b_driver.py hogs  --n 14 --seconds 1800   (hold hogs; for shell use)

Every object is r99b_*; ports 46200-46299; own PIDs only.
"""
import argparse, json, os, re, signal, socket, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r99b_common import *  # noqa

P = 46200  # port base

AUXD = [os.path.join(RAW, "cells")]  # per-pass aux dir, set in run_cells()


def aux(name):
    d = AUXD[0]
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, name)


# ------------------------------------------------------------------ args
def sink_args(node="r99b_sink", dest_port=P, dest_ip="127.0.0.1", fmt="S16BE", minp=1, maxp=1,
              mtu=None, ifname=None, rate=48000, extra_props="", extra_module="", ptime=None,
              framecount=None):
    a = ['{ destination.ip = "%s"' % dest_ip, "destination.port = %d" % dest_port]
    if mtu is not None:
        a.append("net.mtu = %d" % mtu)
    if ifname:
        a.append('local.ifname = "%s"' % ifname)
    if minp is not None:
        a.append("sess.min-ptime = %s" % minp)
    if maxp is not None:
        a.append("sess.max-ptime = %s" % maxp)
    if ptime is not None:
        a.append("rtp.ptime = %s" % ptime)
    if framecount is not None:
        a.append("rtp.framecount = %d" % framecount)
    a.append('audio.format = "%s"' % fmt)
    a.append("audio.rate = %d" % rate)
    a.append("audio.channels = 2")
    a.append("stream.props = { node.name = \"%s\" media.class = \"Audio/Sink\" node.virtual = false "
             "node.always-process = true %s }" % (node, extra_props))
    if extra_module:
        a.append(extra_module)
    a.append("}")
    return " ".join(a)


def source_args(node="r99b_src", src_ip="239.255.42.99", src_port=P + 1, fmt="S16BE", ifname="lo",
                latency=100, rate=48000, extra_props="", extra_module=""):
    a = ['{ source.ip = "%s"' % src_ip, "source.port = %d" % src_port]
    if ifname:
        a.append('local.ifname = "%s"' % ifname)
    if latency is not None:
        a.append("sess.latency.msec = %s" % latency)
    a.append('audio.format = "%s"' % fmt)
    a.append("audio.rate = %d" % rate)
    a.append("audio.channels = 2")
    a.append('stream.props = { node.name = "%s" media.class = "Audio/Source" node.virtual = false %s }'
             % (node, extra_props))
    if extra_module:
        a.append(extra_module)
    a.append("}")
    return " ".join(a)


# ------------------------------------------------------------------ helpers
def tone_props(node):
    return node_props(node, ["rtp.", "sess.", "net.", "node.", "media.", "audio."])


def live_tap(out, port, seconds, group=None, ifname="lo", bufsize=65535):
    return recv_child(out, port, seconds, group=group, ifname=ifname, bufsize=bufsize)


def finish(p, timeout=20):
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        kill(p)
        try:
            out, err = p.communicate(timeout=5)
        except Exception:
            out, err = b"", b""
    return (out or b"").decode(errors="replace"), (err or b"").decode(errors="replace")


def run_cell(name, fn, rep, stage):
    t0 = time.time()
    rec = {"cell": name, "rep": rep, "pass": stage, "loadavg_start": loadavg(),
           "procs_running_start": procs_running(), "t_start": t0}
    try:
        rec.update(fn(rep) or {})
        rec["ok"] = True
    except Exception as e:
        rec["ok"] = False
        rec["error"] = repr(e)
        import traceback
        rec["traceback"] = traceback.format_exc()
    rec["t_end"] = time.time()
    rec["wall_s"] = round(rec["t_end"] - t0, 3)
    rec["loadavg_end"] = loadavg()
    leg_write(stage, name, rep, rec)
    return rec


# ------------------------------------------------------------------ cells: sink
def cell_sink_p1(rep):
    write_fragment([("libpipewire-module-rtp-sink", sink_args())])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    out = aux("sink_p1-rep%d.recv.json" % rep)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p_recv = live_tap(out, P, 3.5)
    time.sleep(0.6)
    p_play = play("r99b_sink", node_name="r99b_play")
    time.sleep(3.4)
    kill(p_play)
    finish(p_recv, 8)
    core_pid = int(open(CORE_PID).read())
    d = {"core_up": True, "msg": msg,
         "sink_props": tone_props("r99b_sink"),
         "play_node": node_props("r99b_play", ["node.", "media."]),
         "links": [l for l in sh("pw-link -l", timeout=10)[1].splitlines() if "r99b" in l],
         "udp_sockets": ss_udp(core_pid),
         "recv": read_json(out),
         "core_log_witness": [l for l in core_log() if "rtp" in l.lower()][-6:]}
    core_down()
    return d


def cell_sink_default(rep):
    """C2b: no ptime args -> the module's true defaults."""
    write_fragment([("libpipewire-module-rtp-sink", sink_args(minp=None, maxp=None))])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    out = aux("sink_default-rep%d.recv.json" % rep)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p_recv = live_tap(out, P, 3.0)
    time.sleep(0.6)
    p_play = play("r99b_sink", node_name="r99b_play")
    time.sleep(2.8)
    kill(p_play)
    finish(p_recv, 8)
    d = {"core_up": True, "msg": msg,
         "sink_props": tone_props("r99b_sink"),
         "recv": read_json(out),
         "core_log_witness": [l for l in core_log() if "ptime" in l or "latency" in l][-4:]}
    core_down()
    return d


def cell_sink_two(rep):
    """AX-SIB: two r99b sinks, one destination."""
    write_fragment([
        ("libpipewire-module-rtp-sink", sink_args(node="r99b_sink_a", dest_port=P + 1)),
        ("libpipewire-module-rtp-sink", sink_args(node="r99b_sink_b", dest_port=P + 1)),
    ])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    out = aux("sink_two-rep%d.recv.json" % rep)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p_recv = live_tap(out, P + 1, 3.5)
    time.sleep(0.6)
    p1 = play("r99b_sink_a", node_name="r99b_play_a")
    p2 = play("r99b_sink_b", node_name="r99b_play_b")
    time.sleep(3.2)
    kill(p1)
    kill(p2)
    finish(p_recv, 8)
    core_pid = int(open(CORE_PID).read())
    d = {"core_up": True, "msg": msg,
         "props_a": tone_props("r99b_sink_a"), "props_b": tone_props("r99b_sink_b"),
         "udp_sockets": ss_udp(core_pid),
         "recv": read_json(out)}
    core_down()
    return d


def cell_sink_socket(rep):
    """C3: socket shape + 3 fresh loads."""
    write_fragment([("libpipewire-module-rtp-sink", sink_args())])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg}
    core_pid = int(open(CORE_PID).read())
    socks = ss_udp(core_pid)
    p_play = play("r99b_sink", node_name="r99b_play")
    time.sleep(1.2)
    socks_live = ss_udp(core_pid)
    kill(p_play)
    d = {"core_up": True, "msg": msg, "udp_sockets_after_load": socks,
         "udp_sockets_after_play": socks_live, "sink_props": tone_props("r99b_sink")}
    core_down()
    return d


# ------------------------------------------------------------------ cells: source
def cell_src_port0(rep):
    """C8: source.port=0 -> rc 234."""
    write_fragment([("libpipewire-module-rtp-source", source_args(src_port=0))])
    ok, msg = core_up(with_wp=False)
    log = core_log()
    d = {"core_up": ok, "msg": msg,
         "rc": (lambda: int(open(CORE_PID).read()) if os.path.exists(CORE_PID) else None)(),
         "invalid_source_port_log": [l for l in log if "source.port" in l],
         "context_fail_log": [l for l in log if "failed to create context" in l],
         "load_module_err": [l for l in log if "could not load mandatory module" in l]}
    core_down()
    return d


def cell_src_fake(rep):
    """C11: rtp.receiving faked at init; random receiver-ts-offset."""
    write_fragment([("libpipewire-module-rtp-source", source_args(node="r99b_src_fake"))])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    p = tone_props("r99b_src_fake")
    d = {"core_up": True, "msg": msg, "src_props": p,
         "receiving": p["props"].get("rtp.receiving") if p else None,
         "ts_offset": p["props"].get("rtp.receiver-ts-offset") if p else None,
         "udp_sockets": ss_udp(int(open(CORE_PID).read())),
         "sync_log": [l for l in core_log() if "sync" in l][-4:]}
    core_down()
    return d


def cell_src_unicast(rep):
    """C8b: unicast source; arm by rep (0 = same-port sender, 1 = foreign-port)."""
    arm = "same-port" if rep % 2 == 0 else "foreign-port"
    port = P + 2
    write_fragment([("libpipewire-module-rtp-source",
                     source_args(node="r99b_src_u", src_ip="127.0.0.1", src_port=port, ifname=None,
                                 extra_props="node.always-process = true"))])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    wav = aux("src_unicast-%s-rep%d.wav" % (arm, rep))
    os.makedirs(os.path.dirname(wav), exist_ok=True)
    p_rec = record(wav, "r99b_src_u", seconds=4.5)
    time.sleep(1.2)
    core_pid = int(open(CORE_PID).read())
    socks = ss_udp(core_pid)
    from_port = port if arm == "same-port" else P + 90
    p_send = send_child(port, 2.5, from_port=from_port, count=2500)
    sent, _ = finish(p_send, 10)
    time.sleep(1.0)
    kill(p_rec)
    d = {"core_up": True, "msg": msg, "arm": arm, "udp_sockets": socks,
         "send": sent.strip(), "src_props": tone_props("r99b_src_u"),
         "wav": wav_analyze(wav),
         "witness": [l for l in core_log() if "sync" in l or "unexpected" in l][-4:]}
    core_down()
    return d


def cell_crafted_mcast(rep):
    """C12: crafted sender over a CORRECT multicast path (lo)."""
    port = P + 3
    write_fragment([("libpipewire-module-rtp-source", source_args(node="r99b_src_c", src_port=port))])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    wav = aux("crafted_mcast-rep%d.wav" % rep)
    tap = aux("crafted_mcast-rep%d.tap.json" % rep)
    os.makedirs(os.path.dirname(wav), exist_ok=True)
    p_rec = record(wav, "r99b_src_c", seconds=5.0)
    p_tap = live_tap(tap, port, 4.5, group="239.255.42.99", ifname="lo")
    time.sleep(1.2)
    core_pid = int(open(CORE_PID).read())
    socks = ss_udp(core_pid)
    proc_rows = [l.strip() for l in open("/proc/net/udp")
                 if (":%X" % port) in l.upper()]
    p_send = send_child(port, 2.5, host="239.255.42.99", group="239.255.42.99", ifname="lo",
                        count=2500, ts0=1000000)
    sent, _ = finish(p_send, 10)
    time.sleep(1.0)
    kill(p_rec)
    kill(p_tap)
    d = {"core_up": True, "msg": msg, "send": sent.strip(),
         "src_props": tone_props("r99b_src_c"),
         "udp_sockets": socks, "proc_net_udp_rows": proc_rows,
         "tap": read_json(tap), "wav": wav_analyze(wav),
         "witness": [l for l in core_log() if "sync" in l or "receiving" in l or "unexpected" in l][-6:]}
    core_down()
    return d


def cell_crafted_unicast_scoutshape(rep):
    """C12 A/B: the scout's exact crafted shape — multicast-configured source,
    sender sends UNICAST to 127.0.0.1 (host default), so the group-bound source
    socket never sees the packets. Delivery artifact, not clock-gating."""
    port = P + 13
    write_fragment([("libpipewire-module-rtp-source", source_args(node="r99b_src_cu", src_port=port))])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    wav = aux("crafted_unicast-rep%d.wav" % rep)
    tap = aux("crafted_unicast-rep%d.tap.json" % rep)
    os.makedirs(os.path.dirname(wav), exist_ok=True)
    p_rec = record(wav, "r99b_src_cu", seconds=5.0)
    p_tap = live_tap(tap, port, 4.5, group="239.255.42.99", ifname="lo")
    time.sleep(1.2)
    core_pid = int(open(CORE_PID).read())
    socks = ss_udp(core_pid)
    proc_rows = [l.strip() for l in open("/proc/net/udp") if (":%X" % port) in l.upper()]
    p_send = send_child(port, 2.5, host="127.0.0.1", count=2500, ts0=1000000)  # scout shape
    sent, _ = finish(p_send, 10)
    time.sleep(1.0)
    kill(p_rec)
    kill(p_tap)
    d = {"core_up": True, "msg": msg, "send": sent.strip(),
         "src_props": tone_props("r99b_src_cu"),
         "udp_sockets": socks, "proc_net_udp_rows": proc_rows,
         "tap": read_json(tap), "wav": wav_analyze(wav),
         "witness": [l for l in core_log() if "sync to timestamp" in l or "unexpected" in l][-6:]}
    core_down()
    return d


def cell_badifname_driven(rep):
    """C10b: bad local.ifname WITH a session manager and a linked client.

    The scout's source reading says the SO_BINDTODEVICE failure is deferred to
    stream start (module-rtp-sink.c:230-236 -> goto error). Without a client the
    node stays suspended and nothing is exercised; drive it with pw-play.
    """
    write_fragment([("libpipewire-module-rtp-sink", sink_args(ifname="r99b_nosuchif"))])
    ok, msg = core_up(with_wp=True, timeout=20)
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    pre = node_props("r99b_sink", ["rtp.", "node."])
    p_play = play("r99b_sink", node_name="r99b_play")
    time.sleep(2.5)
    during = node_props("r99b_sink", ["rtp.", "node."])
    socks = ss_udp(int(open(CORE_PID).read()))
    kill(p_play)
    time.sleep(0.5)
    after = node_props("r99b_sink", ["rtp.", "node."])
    log = core_log()
    d = {"core_up": True, "msg": msg, "pre": pre, "during": during, "after": after,
         "udp_sockets": socks,
         "bindtodevice_err": [l for l in log if "SO_BINDTODEVICE" in l or "setsockopt" in l][-4:],
         "stream_err": [l for l in log if "stream error" in l or "schedule_destroy" in l][-4:],
         "log_tail": [l for l in log if "mod.rtp-sink" in l or "error" in l.lower()][-8:]}
    core_down()
    return d


def cell_crafted_tsoff(rep):
    """C12b: crafted sender + sess.ts-offset pinned at module-arg level.

    rep 0..4 sweep offsets around the estimated graph clock position.
    """
    port = P + 4
    ts0 = 1000000
    core_t0 = time.time()
    # estimate clock position at the moment the sender starts (~1.2 s after core up)
    est_clock = int(1.2 * 48000)
    delta = [0, -1024, 1024, -2048, 2048][rep % 5]
    ts_offset = ts0 - est_clock + 4800 + delta
    write_fragment([("libpipewire-module-rtp-source",
                     source_args(node="r99b_src_t", src_port=port,
                                 extra_module="sess.ts-offset = %d" % ts_offset))])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    wav = aux("crafted_tsoff-rep%d.wav" % rep)
    tap = aux("crafted_tsoff-rep%d.tap.json" % rep)
    os.makedirs(os.path.dirname(wav), exist_ok=True)
    p_rec = record(wav, "r99b_src_t", seconds=5.0)
    p_tap = live_tap(tap, port, 4.5, group="239.255.42.99", ifname="lo")
    time.sleep(1.2)
    p_send = send_child(port, 2.5, host="239.255.42.99", group="239.255.42.99", ifname="lo",
                        count=2500, ts0=ts0)
    sent, _ = finish(p_send, 10)
    time.sleep(1.0)
    kill(p_rec)
    kill(p_tap)
    d = {"core_up": True, "msg": msg, "send": sent.strip(), "ts_offset_arg": ts_offset,
         "delta": delta, "src_props": tone_props("r99b_src_t"),
         "tap": read_json(tap), "wav": wav_analyze(wav),
         "witness": [l for l in core_log() if "sync" in l or "unexpected write" in l][-8:]}
    core_down()
    return d


# ------------------------------------------------------------------ cells: end-to-end / timing
def _e2e_pair(port):
    write_fragment([
        ("libpipewire-module-rtp-sink", sink_args(dest_ip="239.255.42.99", dest_port=port, ifname="lo")),
        ("libpipewire-module-rtp-source", source_args(src_port=port)),
    ])


def cell_e2e_native(rep):
    port = P + 5
    _e2e_pair(port)
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    wav = aux("e2e_native-rep%d.wav" % rep)
    tap = aux("e2e_native-rep%d.tap.json" % rep)
    os.makedirs(os.path.dirname(wav), exist_ok=True)
    p_rec = record(wav, "r99b_src", seconds=5.0)
    p_tap = live_tap(tap, port, 4.5, group="239.255.42.99", ifname="lo")
    time.sleep(1.2)
    p_play = play("r99b_sink", node_name="r99b_play")
    time.sleep(4.0)
    kill(p_play)
    time.sleep(0.5)
    kill(p_rec)
    kill(p_tap)
    d = {"core_up": True, "msg": msg,
         "sink_props": tone_props("r99b_sink"), "src_props": tone_props("r99b_src"),
         "tap": read_json(tap), "wav": wav_analyze(wav),
         "witness": [l for l in core_log() if "sync" in l][-4:]}
    core_down()
    return d


def cell_relink(rep):
    """AX-RELINK: player start -> first packet, kill -> silence, restart -> re-lock."""
    port = P + 6
    _e2e_pair(port)
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    tap = aux("relink-rep%d.tap.json" % rep)
    os.makedirs(os.path.dirname(tap), exist_ok=True)
    t0 = time.monotonic()
    p_tap = live_tap(tap, port, 12.0, group="239.255.42.99", ifname="lo")
    time.sleep(1.0)
    p1 = play("r99b_sink", node_name="r99b_play1")
    t_play1 = time.monotonic() - t0
    time.sleep(3.0)
    kill(p1)
    t_kill = time.monotonic() - t0
    time.sleep(3.0)
    p2 = play("r99b_sink", node_name="r99b_play2")
    t_play2 = time.monotonic() - t0
    time.sleep(3.0)
    kill(p2)
    t_kill2 = time.monotonic() - t0
    finish(p_tap, 15)
    d = {"core_up": True, "msg": msg,
         "t_play1": round(t_play1, 3), "t_kill": round(t_kill, 3),
         "t_play2": round(t_play2, 3), "t_kill2": round(t_kill2, 3),
         "tap": read_json(tap), "witness": [l for l in core_log() if "sync" in l][-6:]}
    core_down()
    return d


def cell_flagorder(rep):
    """AX-ORDER: pw-play --target before vs after the file, with TWO sinks so the
    target actually discriminates (rep 0 = flags first, rep 1 = flags last)."""
    write_fragment([
        ("libpipewire-module-rtp-sink", sink_args(node="r99b_sink_target", dest_port=P + 7)),
        ("libpipewire-module-rtp-sink", sink_args(node="r99b_sink_other", dest_port=P + 17)),
    ])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12)}
    out_t = aux("flagorder-rep%d.target.json" % rep)
    out_o = aux("flagorder-rep%d.other.json" % rep)
    os.makedirs(os.path.dirname(out_t), exist_ok=True)
    p_recv_t = live_tap(out_t, P + 7, 3.0)
    p_recv_o = live_tap(out_o, P + 17, 3.0)
    time.sleep(0.6)
    args_first = (rep % 2 == 0)
    p_play = play("r99b_sink_target", node_name="r99b_play", args_first=args_first)
    time.sleep(2.8)
    kill(p_play)
    finish(p_recv_t, 8)
    finish(p_recv_o, 8)
    d = {"core_up": True, "msg": msg, "args_first": args_first,
         "target_recv": read_json(out_t), "other_recv": read_json(out_o),
         "play_stderr": (lambda: (finish(p_play, 2)[1].strip().splitlines() or [""])[-1])(),
         "play_node": node_props("r99b_play", ["node.", "media."])}
    core_down()
    return d


# ------------------------------------------------------------------ cells: packetization
LATTICE = [
    ("mtu1280_p1", dict(mtu=1280, minp=1, maxp=1)),
    ("mtu200_p1", dict(mtu=200, minp=1, maxp=1)),
    ("mtu8000_p1", dict(mtu=8000, minp=1, maxp=1)),
    ("default_pmin2", dict(mtu=1280, minp=2, maxp=20)),
    ("pmin10", dict(mtu=1280, minp=10, maxp=20)),
    ("pmin50", dict(mtu=1280, minp=50, maxp=100)),
]


def cell_lattice(rep):
    name, kw = LATTICE[rep % len(LATTICE)]
    port = P + 8
    write_fragment([("libpipewire-module-rtp-sink", sink_args(node="r99b_sink", dest_port=port, **kw))])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12), "case": name}
    out = aux("lattice-%s-rep%d.recv.json" % (name, rep))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p_recv = live_tap(out, port, 2.5, bufsize=65535)
    time.sleep(0.5)
    p_play = play("r99b_sink", node_name="r99b_play")
    time.sleep(2.4)
    kill(p_play)
    finish(p_recv, 8)
    d = {"core_up": True, "msg": msg, "case": name, "kw": kw,
         "sink_props": tone_props("r99b_sink"), "recv": read_json(out),
         "witness": [l for l in core_log() if "ptime" in l or "latency" in l][-3:]}
    core_down()
    return d


# ------------------------------------------------------------------ cells: refusals
REFUSALS = [
    ("bad_dest_ip", [("libpipewire-module-rtp-sink", sink_args(dest_ip="999.1.2.3"))]),
    ("bad_format_f32le", [("libpipewire-module-rtp-sink", sink_args(fmt="F32LE"))]),
    ("bad_media", [("libpipewire-module-rtp-sink", sink_args(extra_module='sess.media = "r99b_bogus"'))]),
    ("bad_ifname_nowp", [("libpipewire-module-rtp-sink", sink_args(ifname="r99b_nosuchif"))]),
    ("tiny_mtu_nowp", [("libpipewire-module-rtp-sink", sink_args(mtu=64))]),
    ("bad_ifname_wp", [("libpipewire-module-rtp-sink", sink_args(ifname="r99b_nosuchif"))]),
    ("tiny_mtu_wp", [("libpipewire-module-rtp-sink", sink_args(mtu=64))]),
    ("s24be", [("libpipewire-module-rtp-sink", sink_args(fmt="S24BE"))]),
]


def cell_refusal(rep):
    name, mods = REFUSALS[rep % len(REFUSALS)]
    with_wp = name.endswith("_wp") or name in ("s24be",)
    write_fragment(mods)
    ok, msg = core_up(with_wp=with_wp, timeout=20)
    d = {"case": name, "with_wp": with_wp, "core_up": ok, "msg": msg}
    if ok:
        # for the _wp arms wait a moment and see whether the stream start errors
        time.sleep(1.5)
        d["node"] = node_props("r99b_sink", ["rtp.", "node.", "media."])
        d["udp_sockets"] = ss_udp(int(open(CORE_PID).read()))
        if name in ("s24be",):
            out = aux("refusal-s24be-rep%d.recv.json" % rep)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            p_recv = live_tap(out, P, 2.5)
            time.sleep(0.4)
            p_play = play("r99b_sink", node_name="r99b_play")
            time.sleep(2.2)
            kill(p_play)
            finish(p_recv, 8)
            d["recv"] = read_json(out)
    d["log_tail"] = [l for l in core_log() if ("error" in l.lower() or "invalid" in l.lower()
                                               or "unsupported" in l.lower() or "failed" in l.lower())][-5:]
    core_down()
    return d


# ------------------------------------------------------------------ cells: SAP
def cell_sap(rep):
    """C13: sap with no local.ifname (rep 0) vs ifname=lo + loopback group (rep 1)."""
    if rep % 2 == 0:
        mods = [("libpipewire-module-rtp-sap", '{ sap.ip = "239.255.255.255" sap.port = 9875 net.loop = false }')]
        arm = "no-ifname-default-group"
    else:
        mods = [("libpipewire-module-rtp-sap",
                 '{ sap.ip = "239.255.42.98" sap.port = 9876 local.ifname = "lo" net.loop = false }')]
        arm = "ifname-lo"
    iface = "enp7s0"
    tx0 = int(open("/sys/class/net/%s/statistics/tx_packets" % iface).read())
    write_fragment(mods)
    ok, msg = core_up(with_wp=False, timeout=20)
    t0 = time.time()
    time.sleep(4.0)
    tx1 = int(open("/sys/class/net/%s/statistics/tx_packets" % iface).read())
    d = {"arm": arm, "core_up": ok, "msg": msg, "enp7s0_tx_delta": tx1 - tx0,
         "seconds": round(time.time() - t0, 2),
         "nodes": [n["props"].get("node.name") for n in nodes()],
         "udp_sockets": ss_udp(int(open(CORE_PID).read())) if ok else [],
         "join_log": [l for l in core_log() if "join" in l.lower() or "sap" in l.lower()][-8:]}
    core_down()
    return d


# ------------------------------------------------------------------ cells: axes
def cell_axis_quantum(rep):
    """AX-RATE: quantum 256 / 4096 (rep 0 / 1) with ptime 1 -> ts-delta multiples?"""
    q = [256, 4096][rep % 2]
    write_fragment([("libpipewire-module-rtp-sink", sink_args())], quantum=q)
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12), "quantum": q}
    out = aux("axis_quantum-%d-rep%d.recv.json" % (q, rep))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p_recv = live_tap(out, P, 3.0)
    time.sleep(0.5)
    p_play = play("r99b_sink", node_name="r99b_play")
    time.sleep(2.8)
    kill(p_play)
    finish(p_recv, 8)
    d = {"core_up": True, "msg": msg, "quantum": q,
         "sink_props": tone_props("r99b_sink"), "recv": read_json(out)}
    core_down()
    return d


def cell_axis_rate(rep):
    """AX-RATE: module audio.rate 44100 (rep 0) / core default.clock.rate 44100 (rep 1)."""
    if rep % 2 == 0:
        write_fragment([("libpipewire-module-rtp-sink", sink_args(rate=44100))])
        arm = "module_rate44100"
    else:
        write_fragment([("libpipewire-module-rtp-sink", sink_args())], rate=44100)
        arm = "core_rate44100"
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12), "arm": arm}
    out = aux("axis_rate-%s-rep%d.recv.json" % (arm, rep))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p_recv = live_tap(out, P, 3.0)
    time.sleep(0.5)
    p_play = play("r99b_sink", node_name="r99b_play")
    time.sleep(2.8)
    kill(p_play)
    finish(p_recv, 8)
    d = {"core_up": True, "msg": msg, "arm": arm,
         "sink_props": tone_props("r99b_sink"), "recv": read_json(out),
         "witness": [l for l in core_log() if "ptime" in l or "rate" in l][-4:]}
    core_down()
    return d


def cell_axis_order(rep):
    """AX-ORDER: reversed module-arg order (rep 0), duplicate min-ptime (rep 1),
    rtp.ptime inside stream.props (rep 2)."""
    if rep % 3 == 0:
        args = ('{ stream.props = { node.name = "r99b_sink" media.class = "Audio/Sink" '
                'node.virtual = false node.always-process = true } audio.channels = 2 audio.rate = 48000 '
                'audio.format = "S16BE" sess.max-ptime = 1 sess.min-ptime = 1 destination.port = %d '
                'destination.ip = "127.0.0.1" }' % P)
        arm = "reversed"
    elif rep % 3 == 1:
        args = sink_args().replace("sess.min-ptime = 1", "sess.min-ptime = 1 sess.min-ptime = 20")
        arm = "dup_min_ptime_1_then_20"
    else:
        args = sink_args(extra_props="rtp.ptime = 20 rtp.framecount = 960")
        arm = "ptime_in_stream_props"
    write_fragment([("libpipewire-module-rtp-sink", args)])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg, "log": core_log(12), "arm": arm}
    out = aux("axis_order-%s-rep%d.recv.json" % (arm, rep))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p_recv = live_tap(out, P, 2.5)
    time.sleep(0.5)
    p_play = play("r99b_sink", node_name="r99b_play")
    time.sleep(2.2)
    kill(p_play)
    finish(p_recv, 8)
    d = {"core_up": True, "msg": msg, "arm": arm,
         "sink_props": tone_props("r99b_sink"), "recv": read_json(out)}
    core_down()
    return d


# ------------------------------------------------------------------ cells: graph axis
def cell_pwcli_private(rep):
    """AX-GRAPH(b): pw-cli load-module into the PRIVATE core (client-side?)."""
    write_fragment([])
    ok, msg = core_up()
    if not ok:
        return {"core_up": False, "msg": msg}
    out = aux("pwcli_private-rep%d.recv.json" % rep)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p_recv = live_tap(out, P + 10, 3.5)
    time.sleep(0.4)
    cmd = ["pw-cli"]
    stdin = 'load-module libpipewire-module-rtp-sink %s\n' % sink_args(node="r99b_sink_cli",
                                                                       dest_port=P + 10)
    # keep pw-cli alive so the client-side module lives
    p_cli = subprocess.Popen(cmd, env=ENV, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, start_new_session=True)
    p_cli.stdin.write(stdin.encode())
    p_cli.stdin.flush()
    time.sleep(1.5)
    during = node_props("r99b_sink_cli", ["rtp.", "node."])
    kill_tree(p_cli.pid, marker="pw-cli")
    time.sleep(1.0)
    after = node_props("r99b_sink_cli", ["rtp.", "node."])
    finish(p_recv, 8)
    d = {"core_up": True, "msg": msg, "node_during": during, "node_after_cli_exit": after,
         "recv": read_json(out), "cli_stderr_tail": [l for l in core_log() if "rtp" in l.lower()][-3:]}
    core_down()
    return d


def cell_shared_graph(rep):
    """AX-GRAPH(c): client-side rtp-sink in the SHARED graph, loopback dest only.

    One short leg; the node is r99b_* and dies with pw-cli.
    """
    out = aux("shared_graph-rep%d.recv.json" % rep)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pre = shared_census()
    p_recv = recv_child(out, P + 11, 4.5)
    time.sleep(0.4)
    stdin = 'load-module libpipewire-module-rtp-sink %s\n' % sink_args(node="r99b_sink_sh",
                                                                       dest_port=P + 11)
    p_cli = subprocess.Popen(["pw-cli"], env=dict(os.environ, PIPEWIRE_RUNTIME_DIR="/run/user/1000",
                                                  XDG_RUNTIME_DIR="/run/user/1000"),
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             start_new_session=True)
    p_cli.stdin.write(stdin.encode())
    p_cli.stdin.flush()
    time.sleep(1.5)
    during = shared_census()
    # try to drive it: a pw-play in the shared graph targeting r99b_sink_sh
    p_play = subprocess.Popen(["pw-play", "--target", "r99b_sink_sh", "-P", "node.name=r99b_play_sh", TONE],
                              env=dict(os.environ, PIPEWIRE_RUNTIME_DIR="/run/user/1000",
                                       XDG_RUNTIME_DIR="/run/user/1000"),
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(2.2)
    kill(p_play)
    kill_tree(p_cli.pid, marker="pw-cli")
    time.sleep(1.0)
    post = shared_census()
    finish(p_recv, 8)
    d = {"pre_census": pre, "during_census": during, "post_census": post,
         "recv": read_json(out)}
    return d


# ------------------------------------------------------------------ registry
CELLS = {
    "sink_p1": (cell_sink_p1, 2),
    "sink_default": (cell_sink_default, 2),
    "sink_two": (cell_sink_two, 2),
    "sink_socket": (cell_sink_socket, 3),
    "src_port0": (cell_src_port0, 2),
    "src_fake": (cell_src_fake, 2),
    "src_unicast": (cell_src_unicast, 2),
    "crafted_mcast": (cell_crafted_mcast, 2),
    "crafted_unicast": (cell_crafted_unicast_scoutshape, 2),
    "crafted_tsoff": (cell_crafted_tsoff, 5),
    "badifname_driven": (cell_badifname_driven, 1),
    "e2e_native": (cell_e2e_native, 2),
    "relink": (cell_relink, 2),
    "flagorder": (cell_flagorder, 2),
    "lattice": (cell_lattice, 6),
    "refusal": (cell_refusal, 8),
    "sap": (cell_sap, 2),
    "axis_quantum": (cell_axis_quantum, 2),
    "axis_rate": (cell_axis_rate, 2),
    "axis_order": (cell_axis_order, 3),
    "pwcli_private": (cell_pwcli_private, 1),
    "shared_graph": (cell_shared_graph, 1),
}


def run_cells(stage, only=None, reps=None):
    AUXD[0] = os.path.join(RAW, "cells-%s" % stage)
    names = only.split(",") if only else list(CELLS)
    t0 = time.time()
    summary = []
    for name in names:
        fn, n = CELLS[name]
        n = reps if reps is not None else n
        for rep in range(n):
            rec = run_cell(name, fn, rep, stage)
            summary.append({k: rec.get(k) for k in ("cell", "rep", "ok", "error", "wall_s")})
            print("[%s] %s rep%d ok=%s wall=%.1fs %s" % (stage, name, rep, rec.get("ok"),
                                                         rec.get("wall_s", 0), rec.get("error", "")),
                  flush=True)
    receipt("cells-%s.json" % stage, summary)
    print("pass %s: %d cells in %.1fs" % (stage, len(summary), time.time() - t0))


# ------------------------------------------------------------------ LAN footprint
LAND = [os.path.join(RAW, "lan")]


def lan_path(name):
    os.makedirs(LAND[0], exist_ok=True)
    return os.path.join(LAND[0], name)


def lan_arm(arm, seconds=10.0):
    """One LAN-footprint arm. Bracketed by matched idle windows in run_lan().

    The receiver is joined on enp7s0 (the LAN interface); a second receiver on lo
    counts what the seat actually emitted. The module runs with net.loop=false,
    so the enp7s0-joined receiver sees only egress traffic, not our own loop.
    """
    iface = "enp7s0"
    tx0 = int(open("/sys/class/net/%s/statistics/tx_packets" % iface).read())
    t0 = time.time()
    if arm == "idle":
        time.sleep(seconds)          # a real idle window, matched in duration
        tx1 = int(open("/sys/class/net/%s/statistics/tx_packets" % iface).read())
        return {"arm": arm, "seconds": round(time.time() - t0, 2), "enp7s0_tx_delta": tx1 - tx0,
                "emitted_packets": 0, "recv": None, "recv_lo": None}
    port = P + 12
    if arm == "mcast-lo":
        mods = [("libpipewire-module-rtp-sink",
                 sink_args(node="r99b_sink_lan", dest_ip="239.255.42.99", dest_port=port, ifname="lo"))]
    else:
        mods = [("libpipewire-module-rtp-sink",
                 sink_args(node="r99b_sink_lan", dest_ip="239.255.42.99", dest_port=port, ifname=iface))]
    write_fragment(mods)
    ok, msg = core_up()
    if not ok:
        return {"arm": arm, "core_up": False, "msg": msg}
    out_en = lan_path("%s-en.json" % arm)
    out_lo = lan_path("%s-lo.json" % arm)
    p_en = recv_child(out_en, port, seconds, group="239.255.42.99", ifname=iface)
    p_lo = recv_child(out_lo, port, seconds, group="239.255.42.99", ifname="lo")
    time.sleep(0.5)
    p_play = play("r99b_sink_lan", node_name="r99b_play_lan")
    time.sleep(seconds - 0.5)
    kill(p_play)
    finish(p_en, 8)
    finish(p_lo, 8)
    emitted = (read_json(out_lo) or {}).get("n", 0)
    core_down()
    tx1 = int(open("/sys/class/net/%s/statistics/tx_packets" % iface).read())
    return {"arm": arm, "seconds": round(time.time() - t0, 2), "enp7s0_tx_delta": tx1 - tx0,
            "emitted_packets": emitted, "recv": read_json(out_en), "recv_lo": read_json(out_lo)}


def run_lan(stage):
    LAND[0] = os.path.join(RAW, "lan-%s" % stage)
    res = []
    seq = ["idle", "mcast-lo", "idle", "mcast-en", "idle"]
    for i, arm in enumerate(seq):
        r = lan_arm(arm, seconds=8.0)
        r["pass"] = stage
        r["slot"] = i
        res.append(r)
        print("[%s] lan %s: tx_delta=%s emitted=%s recv_en=%s" % (
            stage, arm, r.get("enp7s0_tx_delta"), r.get("emitted_packets"),
            (r.get("recv") or {}).get("n")), flush=True)
    receipt("lan-%s.json" % stage, res)


# ------------------------------------------------------------------ main
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["cells", "lan", "hogs"])
    ap.add_argument("--pass", dest="stage", default="quiet")
    ap.add_argument("--only", default=None)
    ap.add_argument("--reps", type=int, default=None)
    ap.add_argument("--n", type=int, default=14)
    ap.add_argument("--seconds", type=float, default=1800.0)
    a = ap.parse_args()
    if a.mode == "cells":
        run_cells(a.stage, only=a.only, reps=a.reps)
    elif a.mode == "lan":
        run_lan(a.stage)
    elif a.mode == "hogs":
        hs = start_hogs(a.n, a.seconds)
        print(json.dumps([p.pid for p in hs]))
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            print(json.dumps(stop_hogs()))
