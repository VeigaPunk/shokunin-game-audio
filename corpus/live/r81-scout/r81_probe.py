#!/usr/bin/env python3
"""R81 scout harness — GStreamer surface on this PipeWire host, measured.

Seat scope: corpus/live/r81-scout/ ONLY. No tracked file read for behaviour and
none written; corpus/fixtures is never imported. Every leg is bounded three
ways: element-level bound (num-buffers) where available, a wall-clock cap, and
a byte cap checked in the same loop that owns the process group (no helper
thread that could fail to arm — the r77 flood lesson).

Legs never unload a pulse module by name; only by the index returned from
load-module. Nodes/streams are named gst_r81_* so a concurrent seat's graph
witness cannot alias ours.

Usage: r81_probe.py <stage>   with stage in {baseline, inventory, pw_sink,
pw_src, pulse, loss, errors, final}
"""
import argparse
import hashlib
import json
import math
import os
import re
import signal
import struct
import subprocess
import sys
import time
import wave
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
RUNS = OUT / "runs"
TMP = OUT / "tmp"
REC = OUT / "receipts"
for d in (RUNS, TMP, REC):
    d.mkdir(parents=True, exist_ok=True)

NS = "gst_r81_ns"                     # seat-owned null sink
TONE = TMP / "tone_r81.wav"           # seat-owned 1 kHz anchor
SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
SPEAKER = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"
LINE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
BYTE_CAP = 4 * 1024 * 1024
WALL_CAP = 8.0
ANSI = re.compile(r"\x1b\[[0-9;]*m")
RAW = "audio/x-raw,format=S16LE,rate=48000,channels=2"

INTEREST = re.compile(r"gst|r81")
PHYSICAL = re.compile(r"SPDIF|Speaker|Headphones|hdmi-stereo|Line__|Mic__|r78")


# --------------------------------------------------------------- primitives
def sh(cmd, timeout=30, env=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           env=env)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return None, "", "timeout"
    except FileNotFoundError as exc:
        return 127, "", repr(exc)


def sha16(path):
    p = Path(path)
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def rm(path):
    p = Path(path)
    if p.exists():
        p.unlink()


def wav_shape(path):
    p = Path(path)
    o = {"exists": p.exists(), "bytes": None, "riff": None, "data": None,
         "frames": None, "fmt": None, "ch": None, "rate": None, "bits": None}
    if not p.exists():
        return o
    size = p.stat().st_size
    o["bytes"] = size
    if size < 44:
        o["riff"] = "short"
        return o
    head = p.open("rb").read(64)
    if head[:4] != b"RIFF" or head[8:12] != b"WAVE":
        o["riff"] = "not_wav"
        return o
    riff = struct.unpack("<I", head[4:8])[0]
    o["riff"] = ("finalized" if riff == size - 8 else
                 "placeholder_8" if riff == 8 else
                 "zero" if riff == 0 else
                 "placeholder_7ffff000" if riff == 0x7FFFF000 else
                 "wavenc_streaming" if riff == 0x7FFF0024 else "other:%d" % riff)
    o["fmt"] = struct.unpack("<H", head[20:22])[0]
    o["ch"] = struct.unpack("<H", head[22:24])[0]
    o["rate"] = struct.unpack("<I", head[24:28])[0]
    o["bits"] = struct.unpack("<H", head[34:36])[0]
    off = 12
    while off + 8 <= 64:
        cid = head[off:off + 4]
        csz = struct.unpack("<I", head[off + 4:off + 8])[0]
        if cid == b"data":
            o["data"] = ("finalized" if csz == size - (off + 8) else
                         "placeholder_7ffff000" if csz == 0x7FFFF000 else
                         "zero" if csz == 0 else "other:%d" % csz)
            frame = max(1, (o["ch"] or 1) * ((o["bits"] or 8) // 8))
            o["frames"] = csz // frame
            break
        off += 8 + csz + (csz & 1)
    return o


def pcm_peak(path, limit=48000):
    p = Path(path)
    if not p.exists() or p.stat().st_size < 44:
        return None
    try:
        with wave.open(str(p), "rb") as w:
            n = min(w.getnframes(), limit)
            raw = w.readframes(n)
        if w.getsampwidth() != 2:
            return None
        vals = struct.unpack("<%dh" % (len(raw) // 2), raw)
        return max(abs(v) for v in vals) if vals else 0
    except Exception:
        return None


def err_class(text):
    pats = (
        ("no_element", r"No such element or plugin '([^']+)'"),
        ("could_not_link", r"could not link ([^\n]+)"),
        ("internal_data_stream", r"Internal data stream error"),
        ("not_negotiated", r"not-negotiated"),
        ("state_change_failed", r"Failed to set pipeline to PAUSED"),
        ("target_not_found", r"stream error: target not found"),
        ("no_such_entity", r"No such entity"),
        ("device_open_failed", r"Could not open audio device"),
        ("connection_refused", r"Connection refused|Failed to connect"),
        ("parse_error", r"could not parse|Erroneous pipeline|syntax error|no property|WARNING: erroneous"),
        ("gobject_critical", r"GLib-GObject-CRITICAL|GstStructure"),
        ("no_such_file", r"No such file or directory"),
        ("other_error", r"ERROR:"),
    )
    for name, pat in pats:
        m = re.search(pat, text)
        if m:
            return name, m.group(0).strip()[:120]
    return None, None


# ------------------------------------------------------------------ pw-dump
PROP_KEEP = re.compile(
    r"^(node\.|stream\.|target\.|media\.|application\.|client\.|object\.|"
    r"priority\.|monitor\.|resample\.|pulse\.|api\.|device\.)")


def graph():
    rc, out, err = sh(["pw-dump"], timeout=30)
    if rc != 0:
        return {"err": err[:200]}
    try:
        objs = json.loads(out)
    except Exception as exc:
        return {"err": repr(exc)}
    nodes, ports, clients = {}, {}, {}
    raw_links = []
    for o in objs:
        t = o.get("type", "")
        i = o.get("info") or {}
        p = i.get("props") or {}
        if t.endswith("Node"):
            name = p.get("node.name") or i.get("name") or ("id%d" % o["id"])
            nodes[o["id"]] = {
                "name": name,
                "class": p.get("media.class"),
                "desc": p.get("node.description"),
                "client": p.get("client.id"),
                "factory": p.get("factory.name"),
                "serial": p.get("object.serial"),
                "state": i.get("state"),
                "props": ({k: v for k, v in p.items() if PROP_KEEP.match(k)}
                          if INTEREST.search(name or "") else None),
            }
        elif t.endswith("Port"):
            ports[o["id"]] = {"node": i.get("node-id"),
                              "name": p.get("port.name"),
                              "dir": p.get("port.direction")}
        elif t.endswith("Link"):
            raw_links.append((i.get("output-node-id"), i.get("output-port-id"),
                              i.get("input-node-id"), i.get("input-port-id")))
        elif t.endswith("Client"):
            clients[o["id"]] = {"name": p.get("client.name") or p.get("application.name"),
                                "binary": p.get("application.process.binary")}

    def ep(nid, pid):
        n = nodes.get(nid, {}).get("name") or ("id:%s" % nid)
        pt = ports.get(pid, {}).get("name") or ("pid:%s" % pid)
        return "%s:%s" % (n, pt)

    links = sorted({"%s -> %s" % (ep(a, b), ep(c, d)) for a, b, c, d in raw_links})
    my_nodes = {n["name"]: {k: v for k, v in n.items() if k != "props" or v}
                for n in nodes.values()
                if n["props"] is not None}
    phys = {n["name"]: {"class": n["class"], "state": n["state"],
                        "serial": n["serial"]}
            for n in nodes.values()
            if n["props"] is None and n["class"] and PHYSICAL.search(n["name"] or "")}
    return {"links": links, "my_nodes": my_nodes, "phys": phys,
            "node_count": len(nodes), "clients": clients}


def ns_module():
    """Return the live pulse module index owning NS, or None."""
    rc, out, _ = sh(["pactl", "list", "short", "modules"])
    for line in out.splitlines():
        if "module-null-sink" in line and NS in line:
            return int(line.split("\t")[0])
    return None


def ns_alive():
    rc, out, _ = sh(["pactl", "list", "short", "sinks"])
    return any(NS in ln for ln in out.splitlines())


def load_ns():
    rc, out, err = sh(["pactl", "load-module", "module-null-sink",
                       "sink_name=" + NS,
                       "sink_properties=device.description=" + NS])
    return {"rc": rc, "stdout": out.strip(), "stderr": err.strip(),
            "index": int(out.strip()) if rc == 0 and out.strip().isdigit() else None}


def unload_module(idx):
    rc, out, err = sh(["pactl", "unload-module", str(idx)])
    return {"rc": rc, "stdout": out.strip(), "stderr": err.strip()}


def make_tone(path=TONE, seconds=20, peak=8192, freq=1000):
    path = Path(path)
    if path.exists() and path.stat().st_size > 1000:
        return path
    rate = 48000
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        buf = bytearray()
        for n in range(rate * seconds):
            v = int(peak * math.sin(2 * math.pi * freq * n / rate))
            buf += struct.pack("<hh", v, v)
        w.writeframes(bytes(buf))
    return path


# ---------------------------------------------------------------------- leg
def leg(name, argv, *, env_extra=None, out_path=None, wall_cap=WALL_CAP,
        byte_cap=BYTE_CAP, samples=(0.4, 1.0), timeline=None,
        at=(), sever=None, sever_after=None, stage="misc", note=None):
    """Run one bounded leg, sampling the live graph.

    timeline: sample every N seconds instead of the fixed `samples` list.
    at: list of (delay_s, callable) fired once.
    """
    env = None
    if env_extra:
        env = dict(os.environ)
        env.update(env_extra)
    if out_path:
        rm(out_path)
    argv = list(argv)
    t0 = time.monotonic()
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                         text=True, env=env, preexec_fn=os.setsid)
    pgid = os.getpgid(p.pid)
    snaps, actions = [], []
    pend_at = sorted(at, key=lambda x: x[0])
    next_due = [t0 + timeline] if timeline else [t0 + s for s in samples]
    killed = None
    sent = None
    sev = sever
    while True:
        now = time.monotonic()
        el = now - t0
        if p.poll() is not None:
            break
        while pend_at and el >= pend_at[0][0]:
            _, fn = pend_at.pop(0)
            try:
                res = fn()
            except Exception as exc:                       # pragma: no cover
                res = {"exc": repr(exc)}
            actions.append({"t": round(el, 3), "result": res})
        if next_due and el >= next_due[0] - t0:
            sz = None
            if out_path and Path(out_path).exists():
                sz = Path(out_path).stat().st_size
            snaps.append({"t": round(el, 3), "size": sz, "g": graph()})
            if timeline:
                next_due[0] += timeline
            else:
                next_due.pop(0)
        if sev is not None and sever_after is not None and el >= sever_after:
            try:
                os.killpg(pgid, sev)
                sent = signal.Signals(sev).name
            except ProcessLookupError:
                sent = "already_gone"
            sev = None
        if out_path and Path(out_path).exists() and \
                Path(out_path).stat().st_size > byte_cap:
            killed = "bytecap:%d" % Path(out_path).stat().st_size
            os.killpg(pgid, signal.SIGKILL)
            break
        if el > wall_cap:
            killed = "wallcap"
            os.killpg(pgid, signal.SIGKILL)
            break
        time.sleep(0.008)
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:                      # pragma: no cover
        os.killpg(pgid, signal.SIGKILL)
        p.wait(timeout=5)
    err = ANSI.sub("", p.stderr.read() or "")
    post = graph()
    rc = p.returncode
    cls, hit = err_class(err)
    rec = {"name": name, "argv": argv, "env_extra": env_extra or None,
           "rc": rc, "signal": signal.Signals(-rc).name if (rc or 0) < 0 else None,
           "sent": sent, "killed": killed, "elapsed_s": round(time.monotonic() - t0, 3),
           "stderr_head": err.strip().splitlines()[:3], "err_class": cls,
           "err_hit": hit, "actions": actions, "samples": snaps,
           "post_links": post["links"], "out": wav_shape(out_path) if out_path else None,
           "out_peak": pcm_peak(out_path) if out_path else None,
           "note": note}
    d = RUNS / stage / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "cmd.txt").write_text(" ".join(argv) + "\n")
    (d / "stderr.txt").write_text(err)
    (d / "receipt.json").write_text(json.dumps(rec, indent=1))
    print("  leg %-34s rc=%-4s %-22s %s" % (
        name, rc, cls or "-", ("links:" + str(post["links"][:3])) if post.get("links") else ""))
    if out_path:
        rm(out_path)
    return rec


def receipt(stage, body, extra=None):
    doc = {"probe": stage, "host": os.uname().nodename,
           "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "toolchain": toolchain(), "byte_cap_bytes": BYTE_CAP,
           "wall_cap_s": WALL_CAP, "body": body}
    if extra:
        doc.update(extra)
    p = REC / ("%s.json" % stage)
    p.write_text(json.dumps(doc, indent=1))
    print("[receipt] %s (%d B)" % (p.name, p.stat().st_size))
    return p


def toolchain():
    def one(*a):
        rc, out, err = sh(list(a), timeout=20)
        line = (out + err).strip().splitlines()
        return line[0] if line else None
    return {
        "gst_launch": one("gst-launch-1.0", "--version"),
        "gst_inspect": one("gst-inspect-1.0", "--version"),
        "pw_cli": one("pw-cli", "--version"),
        "pactl": one("pactl", "--version"),
        "ffprobe": one("ffprobe", "-version"),
        "python": sys.version.split()[0],
        "kernel": os.uname().release,
        "pkgs": one("pacman", "-Q", "gstreamer", "gst-plugins-base",
                    "gst-plugins-good", "gst-plugin-pipewire", "pipewire"),
    }


def dir_bytes(p):
    p = Path(p)
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) if p.exists() else 0


# ------------------------------------------------------------------ stages
ELEMENTS = ["pipewiresink", "pipewiresrc", "pulsesink", "pulsesrc",
            "autoaudiosink", "autoaudiosrc", "alsasink", "alsasrc",
            "audiotestsrc", "wavenc", "wavparse", "filesink", "fakesink",
            "audioconvert", "audioresample", "volume", "level", "spectrum",
            "jackaudiosink", "jackaudiosrc", "osssink", "oss4sink",
            "openalsink", "playbin", "pipewire", "nosuchelement_xyz"]


def stage_inventory():
    body = {"reps": 3, "elements": {}, "plugin": None}
    for el in ELEMENTS:
        rows = []
        for rep in range(3):
            rc, out, err = sh(["gst-inspect-1.0", el], timeout=30)
            txt = ANSI.sub("", out + err)
            klass = None
            m = re.search(r"^\s*Klass\s+(.+)$", txt, re.M)
            if m:
                klass = m.group(1).strip()
            plug = None
            m = re.search(r"^\s*Filename\s+(\S+)$", txt, re.M)
            if m:
                plug = m.group(1).strip()
            ver = None
            m = re.search(r"^\s*Version\s+(\S+)$", txt, re.M)
            if m:
                ver = m.group(1).strip()
            first = txt.strip().splitlines()[0] if txt.strip() else ""
            rows.append({"rc": rc, "klass": klass, "plugin": plug, "version": ver,
                         "first_line": first[:120],
                         "stderr_head": ANSI.sub("", err).strip().splitlines()[:2]})
        body["elements"][el] = rows
    rc, out, err = sh(["gst-inspect-1.0", "--version"])
    body["plugin"] = {"version_rc": rc, "version": (out + err).strip().splitlines()[:2]}
    rc, out, err = sh(["gst-inspect-1.0", "-b"])
    body["blacklist"] = {"rc": rc, "tail": (out + err).strip().splitlines()[-2:]}
    rc, out, err = sh(["pactl", "list", "short", "sinks"])
    body["sinks_at_entry"] = out.strip().splitlines()
    receipt("s1-inventory", body)


def stage_pw_sink():
    """pipewiresink identity + prop vector lattice, 3 reps/leg."""
    mod = load_ns()
    print("  null sink load:", mod)
    body = {"ns_load": mod, "legs": {}, "reps": 3,
            "default_sink": sh(["pactl", "get-default-sink"])[1].strip()}
    base = ["gst-launch-1.0", "-q", "audiotestsrc", "wave=silence",
            "num-buffers=96", "!", RAW, "!"]
    L = [
        ("s0_bare", ["pipewiresink"], None),
        ("s1_target_object", ["pipewiresink", "target-object=" + NS], None),
        ("s2_node_name", ["pipewiresink",
                          "stream-properties=props,node.name=gst_r81_snk_name"], None),
        ("s3_prop_node_target", ["pipewiresink",
                                 "stream-properties=props,node.target=" + NS], None),
        ("s4_prop_target_object", ["pipewiresink",
                                   "stream-properties=props,target.object=" + NS], None),
        ("s5_client_name", ["pipewiresink", "client-name=gst_r81_client"], None),
        ("s6_prop_media_class_sink", ["pipewiresink",
                                      "stream-properties=props,media.class=Audio/Sink"], None),
        ("s7_env_pipewire_props", ["pipewiresink"],
         {"PIPEWIRE_PROPS": "{ node.name=gst_r81_env node.target=" + NS + " }"}),
        ("s8_env_pipewire_node", ["pipewiresink"], {"PIPEWIRE_NODE": NS}),
        ("s9_no_autoconnect", ["pipewiresink",
                               "stream-properties=props,node.autoconnect=false"], None),
        ("s10_bogus_target", ["pipewiresink", "target-object=no_such_sink_r81"], None),
        ("s11_prop_beats_prop", ["pipewiresink", "target-object=" + NS,
                                 "stream-properties=props,target.object=no_such_r81"], None),
        ("s12_client_props", ["pipewiresink",
                              "client-properties=props,application.name=gst_r81_app"], None),
    ]
    for name, tail, envx in L:
        reps = []
        for rep in range(3):
            reps.append(leg(name + "_r%d" % rep, base + tail, env_extra=envx,
                            samples=(0.4, 0.9), stage="s2-pw-sink", wall_cap=6.0))
        body["legs"][name] = reps
    receipt("s2-pw-sink", body)
    print("  ns module id:", ns_module())


def stage_pw_src():
    """pipewiresrc identity + prop vector, 3 reps/leg, tone-anchored."""
    tone = make_tone(seconds=60)
    print("  tone:", tone, tone.stat().st_size, "B")
    tp = subprocess.Popen(["pw-play", "-P", "node.name=gst_r81_tone",
                           "--target", NS, str(tone)],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          preexec_fn=os.setsid)
    time.sleep(0.6)
    body = {"ns_alive": ns_alive(), "tone": str(tone), "legs": {}, "reps": 3}
    out = str(TMP / "cap.wav")
    try:
        # (name, pipewiresrc props, env, capture out path)
        L = [
            ("c0_no_prop", ["target-object=" + NS], None, out),
            ("c1_prop_capture_sink",
             ["target-object=" + NS,
              "stream-properties=props,stream.capture.sink=true"], None, out),
            ("c2_prop_node_name",
             ["target-object=" + NS,
              "stream-properties=props,stream.capture.sink=true,node.name=gst_r81_src_name"], None, out),
            ("c3_client_name",
             ["target-object=" + NS, "client-name=gst_r81_src_client",
              "stream-properties=props,stream.capture.sink=true"], None, out),
            ("c4_monitor_suffix",
             ["target-object=" + NS + ".monitor",
              "stream-properties=props,stream.capture.sink=true"], None, out),
            ("c5_env_props", ["target-object=" + NS],
             {"PIPEWIRE_PROPS": "{ stream.capture.sink=true node.name=gst_r81_src_env }"}, out),
            ("c6_no_autoconnect",
             ["target-object=" + NS,
              "stream-properties=props,stream.capture.sink=true,node.autoconnect=false"], None, out),
            ("c7_prop_node_target",
             ["stream-properties=props,stream.capture.sink=true,node.target=" + NS], None, out),
            ("c8_garbage_with_prop",
             ["target-object=no_such_r81",
              "stream-properties=props,stream.capture.sink=true"], None, out),
        ]
        for name, props, envx, op in L:
            reps = []
            for rep in range(3):
                argv = (["gst-launch-1.0", "-q", "pipewiresrc"] + props +
                        ["num-buffers=100", "!", RAW, "!", "wavenc", "!",
                         "filesink", "location=" + op])
                reps.append(leg(name + "_r%d" % rep, argv, env_extra=envx,
                                out_path=op, samples=(0.4, 0.9),
                                stage="s3-pw-src", wall_cap=6.0))
            body["legs"][name] = reps
        # cross-client naming anchor: pw-record on the same sink
        reps = []
        for rep in range(3):
            reps.append(leg("c9_pw_record_anchor_r%d" % rep,
                            ["pw-record", "-P", "node.name=gst_r81_pwrec",
                             "-P", "stream.capture.sink=true", "--target", NS,
                             "-n", "48000", str(TMP / "rec.wav")],
                            out_path=str(TMP / "rec.wav"), samples=(0.4, 0.9),
                            stage="s3-pw-src", wall_cap=6.0))
        body["legs"]["c9_pw_record_anchor"] = reps
    finally:
        try:
            os.killpg(os.getpgid(tp.pid), signal.SIGKILL)
        except Exception:
            pass
    body["ns_alive_after"] = ns_alive()
    receipt("s3-pw-src", body)


def stage_pulse():
    """pulsesink device= lattice + bind-vs-resolve probes, 3 reps/leg."""
    body = {"ns_alive": ns_alive(), "legs": {}, "reps": 3,
            "default_sink": sh(["pactl", "get-default-sink"])[1].strip()}
    base = ["gst-launch-1.0", "-q", "audiotestsrc", "wave=silence",
            "num-buffers=96", "!", RAW, "!"]
    L = [
        ("p0_bare", ["pulsesink"], None, (0.4, 0.9), None),
        ("p1_device_ns", ["pulsesink", "device=" + NS], None, (0.4, 0.9), None),
        ("p2_device_bogus", ["pulsesink", "device=no_such_sink_r81"], None, (0.4, 0.9), None),
        ("p3_device_monitor", ["pulsesink", "device=" + NS + ".monitor"], None, (0.4, 0.9), None),
        ("p4_device_spdif", ["pulsesink", "device=" + SPDIF], None, (0.4, 0.9), None),
        ("p5_device_source", ["pulsesink", "device=" + LINE], None, (0.4, 0.9), None),
        ("p6_env_pulse_sink", ["pulsesink"], {"PULSE_SINK": NS}, (0.4, 0.9), None),
        ("p7_env_vs_device", ["pulsesink", "device=" + SPDIF], {"PULSE_SINK": NS}, (0.4, 0.9), None),
        ("p8_bogus_server", ["pulsesink", "server=unix:/nonexistent-r81"], None, (0.4, 0.9), None),
        ("p9_stream_props_name", ["pulsesink", "device=" + NS,
                                  "stream-properties=props,node.name=gst_r81_pulse_name"], None, (0.4, 0.9), None),
    ]
    for name, tail, envx, samples, op in L:
        reps = []
        for rep in range(3):
            reps.append(leg(name + "_r%d" % rep, base + tail, env_extra=envx,
                            samples=samples, stage="s4-pulse", wall_cap=6.0))
        body["legs"][name] = reps

    # bind-vs-resolve: move the stream mid-leg, then watch for a snap-back.
    # NOTE pactl short sink-inputs prints the sink's *serial* in col 2, not its
    # name — resolve serial first, then match.
    def mover():
        rc, out, _ = sh(["pactl", "list", "short", "sinks"])
        serial = None
        for ln in out.splitlines():
            f = ln.split("\t")
            if len(f) > 1 and f[1] == NS:
                serial = f[0]
        if serial is None:
            return {"moved": False, "reason": "no sink named " + NS}
        rc, out, _ = sh(["pactl", "list", "short", "sink-inputs"])
        idx = None
        for ln in out.splitlines():
            f = ln.split("\t")
            if len(f) > 2 and f[1] == serial and "audiotest" in ln:
                idx = f[0]
        if idx is None:
            return {"moved": False, "reason": "no sink-input on sink serial " + serial,
                    "sink_inputs": out.strip().splitlines()}
        r = sh(["pactl", "move-sink-input", idx, SPDIF])
        return {"sink_input": idx, "sink_serial": serial, "rc": r[0],
                "stderr": r[2].strip()}

    long_src = ["gst-launch-1.0", "-q", "audiotestsrc", "wave=silence",
                "!", RAW, "!", "pulsesink", "device=" + NS]
    reps = []
    for rep in range(3):
        reps.append(leg("p10_move_mid_leg_r%d" % rep, long_src,
                        samples=(0.5, 1.3), timeline=0.25, at=[(1.5, mover)],
                        stage="s4-pulse", wall_cap=4.0,
                        note="move-sink-input to SPDIF at t=1.5; watch +1s/+2.5s"))
    body["legs"]["p10_move_mid_leg"] = reps
    body["ns_alive_after"] = ns_alive()
    receipt("s4-pulse", body)


def stage_loss():
    """Target loss: unload the seat-owned sink module mid-leg (by index)."""
    idx = ns_module()
    if idx is None:
        print("!! null sink missing at stage entry; reloading")
        mod = load_ns()
        idx = mod["index"]
    print("  target module index:", idx)
    body = {"ns_module_at_entry": idx, "default_sink": sh(["pactl", "get-default-sink"])[1].strip(),
            "legs": {}, "reps": 3,
            "note": "unload happens at t=1.2 via pactl unload-module <index>"}
    play = ["gst-launch-1.0", "-q", "audiotestsrc", "wave=silence",
            "!", RAW, "!"]
    cap_tail = ["num-buffers=1000000", "!", RAW, "!", "wavenc", "!",
                "filesink", "location=" + str(TMP / "loss.wav")]
    L = [
        ("t1_pwsink", play + ["pipewiresink", "target-object=" + NS], None),
        ("t2_pulsesink", play + ["pulsesink", "device=" + NS], None),
        ("t3_pwsrc_default",
         ["gst-launch-1.0", "-q", "pipewiresrc", "target-object=" + NS,
          "stream-properties=props,stream.capture.sink=true"] + cap_tail, None),
        ("t4_pwsrc_on_disconnect_error",
         ["gst-launch-1.0", "-q", "pipewiresrc", "target-object=" + NS,
          "on-disconnect=error",
          "stream-properties=props,stream.capture.sink=true"] + cap_tail, None),
        ("t5_pwsrc_on_disconnect_eos",
         ["gst-launch-1.0", "-q", "pipewiresrc", "target-object=" + NS,
          "on-disconnect=eos",
          "stream-properties=props,stream.capture.sink=true"] + cap_tail, None),
    ]
    for name, argv, envx in L:
        reps = []
        for rep in range(3):
            if not ns_alive():
                load_ns()
            live = ns_module()
            fn = (lambda i: (lambda: unload_module(i)))(live)
            reps.append(leg("%s_r%d" % (name, rep), argv,
                            out_path=str(TMP / "loss.wav") if "pwsrc" in name else None,
                            timeline=0.2, at=[(1.2, fn)], env_extra=envx,
                            stage="s5-loss", wall_cap=4.5,
                            note="target unloaded at t=1.2 (module %s)" % live))
        body["legs"][name] = reps
        print("  ns alive after %s: %s" % (name, ns_alive()))
    body["ns_alive_after"] = ns_alive()
    body["ns_module_after"] = ns_module()
    receipt("s5-loss", body)


def stage_loss2():
    """Follow-up to stage_loss: discriminate *why* the gst capture stalls.

    t6 = same capture, but ONLY the pw prop target.object=NS (no gst
    target-object -> no node.target prop). If t6 re-links to the default
    monitor while t3 does not, the stale node.target prop is the cause.
    t7 = pw-record control on the same host event (r80 L4 law, re-measured
    in this session so the cross-client difference is contention-matched).
    """
    body = {"default_sink": sh(["pactl", "get-default-sink"])[1].strip(),
            "ns_module_at_entry": ns_module(), "legs": {}, "reps": 3}
    cap_tail = ["num-buffers=1000000", "!", RAW, "!", "wavenc", "!",
                "filesink", "location=" + str(TMP / "loss2.wav")]
    L = [
        ("t6_pwsrc_prop_target_object_only",
         ["gst-launch-1.0", "-q", "pipewiresrc",
          "stream-properties=props,stream.capture.sink=true,target.object=" + NS] + cap_tail,
         str(TMP / "loss2.wav")),
        ("t7_pw_record_control",
         ["pw-record", "-P", "stream.capture.sink=true",
          "-P", "node.name=gst_r81_pwrec_ctrl", "--target", NS,
          "-n", "1000000", str(TMP / "loss2.wav")],
         str(TMP / "loss2.wav")),
    ]
    for name, argv, op in L:
        reps = []
        for rep in range(3):
            if not ns_alive():
                load_ns()
            live = ns_module()
            fn = (lambda i: (lambda: unload_module(i)))(live)
            reps.append(leg("%s_r%d" % (name, rep), argv, out_path=op,
                            timeline=0.2, at=[(1.2, fn)], stage="s5-loss",
                            wall_cap=4.5,
                            note="target unloaded at t=1.2 (module %s)" % live))
        body["legs"][name] = reps
        print("  ns alive after %s: %s" % (name, ns_alive()))
    doc = json.load(open(REC / "s5-loss.json"))
    doc["body"]["followup"] = body
    (REC / "s5-loss.json").write_text(json.dumps(doc, indent=1))
    print("[patched] s5-loss.json followup")


def stage_errors():
    """gst-launch exit/error classes + same-session pw anchors, 3 reps."""
    body = {"legs": {}, "reps": 3}
    f = str(TMP / "err.wav")
    L = [
        ("e1_missing_element_src", ["gst-launch-1.0", "-q", "nosuchelementsrc_xyz",
                                    "!", "wavenc", "!", "filesink", "location=" + f], f),
        ("e2_missing_element_sink", ["gst-launch-1.0", "-q", "audiotestsrc",
                                     "num-buffers=4", "!", "nosuchelementsink_xyz"], None),
        ("e3_bogus_property", ["gst-launch-1.0", "-q", "audiotestsrc",
                               "bogus-prop=42", "num-buffers=4", "!", "fakesink"], None),
        ("e4_bogus_property_pw", ["gst-launch-1.0", "-q", "audiotestsrc",
                                  "wave=silence", "num-buffers=4", "!", RAW, "!",
                                  "pipewiresink", "bogus-prop=42"], None),
        ("e5_bogus_enum", ["gst-launch-1.0", "-q", "audiotestsrc", "wave=silence",
                           "num-buffers=4", "!", RAW, "!", "pipewiresink",
                           "mode=bogus"], None),
        ("e6_bogus_caps_value", ["gst-launch-1.0", "-q", "audiotestsrc",
                                 "num-buffers=4", "!", "audio/x-raw,format=BOGUSFMT",
                                 "!", "fakesink"], None),
        ("e7_negotiation_video", ["gst-launch-1.0", "-q", "audiotestsrc",
                                  "num-buffers=4", "!", "video/x-raw,format=I420,"
                                  "width=64,height=64,framerate=30/1", "!",
                                  "fakesink"], None),
        ("e8_negotiation_sink", ["gst-launch-1.0", "-q", "audiotestsrc",
                                 "num-buffers=4", "!",
                                 "audio/x-raw,format=F64LE,rate=48000,channels=2",
                                 "!", "pulsesink", "device=" + SPDIF], None),
        ("e9_parse_incomplete", ["gst-launch-1.0", "-q", "audiotestsrc", "!"], None),
        ("e10_pwsrc_no_prop_garbage", ["gst-launch-1.0", "-q", "pipewiresrc",
                                       "target-object=no_such_node_r81",
                                       "num-buffers=4", "!", RAW, "!", "wavenc",
                                       "!", "filesink", "location=" + f], f),
        ("e11_pulsesrc_bogus", ["gst-launch-1.0", "-q", "pulsesrc",
                                "device=no_such_node_r81", "num-buffers=4", "!",
                                RAW, "!", "wavenc", "!", "filesink",
                                "location=" + f], f),
        ("e12_inspect_missing", ["gst-inspect-1.0", "nosuchelement_xyz"], None),
        ("e13_bad_capsfilter_link", ["gst-launch-1.0", "-q", "audiotestsrc",
                                     "num-buffers=4", "!", "capsfilter",
                                     "caps=audio/x-raw,format=BOGUSFMT", "!",
                                     "fakesink"], None),
    ]
    for name, argv, op in L:
        reps = []
        for rep in range(3):
            reps.append(leg("%s_r%d" % (name, rep), argv, out_path=op,
                            samples=(0.3,), stage="s6-errors", wall_cap=6.0))
        body["legs"][name] = reps
    receipt("s6-errors", body)


def stage_baseline(tag):
    rc, out, _ = sh(["pactl", "list", "short", "sinks"])
    rc2, out2, _ = sh(["pactl", "list", "short", "sources"])
    rc3, out3, _ = sh(["pactl", "list", "short", "modules"])
    rc4, out4, _ = sh(["ps", "-eo", "pid,lstart,args"])
    procs = [ln for ln in out4.splitlines()
             if re.search(r"measure_audio|pw-|parec|gst-|pactl", ln) and "ps -eo" not in ln]
    body = {"sinks": out.strip().splitlines(), "sources": out2.strip().splitlines(),
            "modules": out3.strip().splitlines(), "procs": procs,
            "graph": graph(), "scratch_bytes": dir_bytes(OUT)}
    receipt("s0-%s" % tag, body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage")
    a = ap.parse_args()
    st = a.stage
    if st == "baseline":
        stage_baseline("baseline")
    elif st == "inventory":
        stage_inventory()
    elif st == "pw_sink":
        stage_pw_sink()
    elif st == "pw_src":
        stage_pw_src()
    elif st == "pulse":
        stage_pulse()
    elif st == "loss":
        stage_loss()
    elif st == "loss2":
        stage_loss2()
    elif st == "errors":
        stage_errors()
    elif st == "final":
        stage_baseline("final")
    else:
        raise SystemExit("unknown stage " + st)


if __name__ == "__main__":
    main()
