#!/usr/bin/env python3
"""R82 scout harness — ffmpeg/ffprobe on the PipeWire host, measured.

Seat scope: corpus/live/r82-scout/ ONLY. No tracked-file edits; corpus/fixtures
never read or imported (sibling lanes mutate it). Own tone, own classifiers,
own receipts. Every leg is triple-bounded: an output bound (-t / -n / byte cap)
a wall cap, and a reader byte cap inside the same loop that owns the process.

Stream/node names are r82ff_*; the only sink this seat loads is module
null-sink sink_name=r82ff_ns{,2}, unloaded strictly by the index returned by
load-module (never by name — foreign r78_prop_* orphans live on this host).

Usage: r82_probe.py <stage>  in {baseline, inventory, capture, playback,
loss, buffers, alsa, errors, final}
"""
import argparse
import hashlib
import json
import os
import re
import signal
import struct
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
RUNS = OUT / "runs"
TMP = OUT / "tmp"
REC = OUT / "receipts"
for d in (RUNS, TMP, REC):
    d.mkdir(parents=True, exist_ok=True)

NS = "r82ff_ns"
NS2 = "r82ff_ns2"
TAG = "r82ff"
TONE = TMP / "tone_r82.wav"          # 8 s dual-tone anchor
TONE_SHORT = TMP / "tone_r82_2s.wav"
SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
SPEAKER = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"
LINE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"


# ----------------------------------------------------------------- helpers
def sh(cmd, timeout=30, env=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, env=env)
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


def wav_shape(path):
    p = Path(path)
    o = {"exists": p.exists(), "bytes": None, "riff": None, "data": None,
         "frames": None, "ch": None, "rate": None, "bits": None}
    if not p.exists():
        return o
    size = p.stat().st_size
    o["bytes"] = size
    if size < 44:
        o["riff"] = "short" if size else "empty"
        return o
    head = p.open("rb").read(128)
    if head[:4] != b"RIFF" or head[8:12] != b"WAVE":
        o["riff"] = "not_wav"
        return o
    riff = struct.unpack("<I", head[4:8])[0]
    o["riff"] = ("finalized" if riff == size - 8 else
                 "placeholder_8" if riff == 8 else
                 "zero" if riff == 0 else
                 "wavenc_streaming" if riff == 0x7FFF0024 else
                 "max_u32" if riff == 0xFFFFFFFF else "other:%d" % riff)
    o["ch"] = struct.unpack("<H", head[22:24])[0]
    o["rate"] = struct.unpack("<I", head[24:28])[0]
    o["bits"] = struct.unpack("<H", head[34:36])[0]
    off = 12
    while off + 8 <= 128:
        cid = head[off:off + 4]
        csz = struct.unpack("<I", head[off + 4:off + 8])[0]
        if cid == b"data":
            o["data"] = ("finalized" if csz == size - (off + 8) else
                         "max_u32" if csz == 0xFFFFFFFF else
                         "zero" if csz == 0 else "other:%d" % csz)
            fr = max(1, (o["ch"] or 1) * ((o["bits"] or 8) // 8))
            o["frames"] = csz // fr if csz < 0xFFFFFFF0 else None
            break
        off += 8 + csz + (csz & 1)
    return o


def wav_data(path):
    """Return (data_bytes, ch, rate, bits) locating the real data chunk —
    ffmpeg wavs carry a LIST chunk so offset 44 is NOT payload."""
    p = Path(path)
    if not p.exists() or p.stat().st_size < 46:
        return None, 0, 0, 0
    raw = p.read_bytes()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        return None, 0, 0, 0
    ch = struct.unpack("<H", raw[22:24])[0]
    rate = struct.unpack("<I", raw[24:28])[0]
    bits = struct.unpack("<H", raw[34:36])[0]
    off = 12
    while off + 8 <= len(raw):
        cid = raw[off:off + 4]
        csz = struct.unpack("<I", raw[off + 4:off + 8])[0]
        if cid == b"data":
            return raw[off + 8:off + 8 + min(csz, len(raw) - off - 8)], \
                ch, rate, bits
        off += 8 + csz + (csz & 1)
    return None, ch, rate, bits


def pcm_peak(path, max_bytes=4 << 20):
    p = Path(path)
    if not p.exists() or p.stat().st_size < 46:
        return None
    data, ch, rate, bits = wav_data(path)
    if not data:
        return None
    buf = data[:max_bytes]
    n = len(buf) // 2
    v = memoryview(buf).cast("h")
    peak = 0
    for i in range(n):
        a = abs(v[i])
        if a > peak:
            peak = a
    return peak


def tone_mag(buf, rate, freq, ch, want_ch):
    """DFT magnitude of one channel at freq (Goertzel on whole buffer)."""
    n = len(buf) // (2 * ch)
    if n == 0:
        return 0.0
    v = memoryview(buf).cast("h")
    w = 2.0 * 3.141592653589793 * freq / rate
    cw = 2.0 * __import__("math").cos(w)
    s0 = s1 = s2 = 0.0
    for i in range(n):
        x = v[i * ch + want_ch]
        s0 = x + cw * s1 - s2
        s2 = s1
        s1 = s0
    return (s1 * s1 + s2 * s2 - cw * s1 * s2) ** 0.5 / max(1, n)


def tone_windows(path, rate=48000, ch=2, win_s=0.5, amp_lo=500, amp_hi=16000):
    """Windowed dual-tone classifier: returns list of windows carrying MY tone
    (L@1000, R@1500 within tolerance, cross-terms quiet)."""
    payload, ch0, r0, b0 = wav_data(path)
    if not payload or len(payload) < 400:
        return []
    if ch0:
        ch = ch0
    if r0:
        rate = r0
    bpf = 2 * ch
    winsz = int(rate * win_s) * bpf
    out = []
    t = 0.0
    off = 0
    while off + winsz <= len(payload):
        seg = payload[off:off + winsz]
        l1k = tone_mag(seg, rate, 1000, ch, 0)
        l15 = tone_mag(seg, rate, 1500, ch, 0)
        r15 = tone_mag(seg, rate, 1500, ch, 1) if ch > 1 else 0.0
        r1k = tone_mag(seg, rate, 1000, ch, 1) if ch > 1 else 0.0
        if (amp_lo <= l1k <= amp_hi and amp_lo <= r15 <= amp_hi
                and l15 < 0.15 * l1k and r1k < 0.15 * r15):
            out.append(round(t, 2))
        t += win_s
        off += winsz
    return out


def pw_dump():
    rc, out, _ = sh(["pw-dump"], timeout=15)
    if rc != 0:
        return []
    try:
        return json.loads(out)
    except Exception:
        return []


def nodes_named(pattern):
    rx = re.compile(pattern)
    res = []
    for o in pw_dump():
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        props = o.get("info", {}).get("props", {}) or {}
        nm = props.get("node.name", "")
        mn = props.get("media.name", "")
        an = props.get("application.name", "")
        if rx.search(nm or "") or rx.search(mn or "") or rx.search(an or ""):
            res.append({"id": o["id"], "name": nm, "media.name": mn,
                        "app.name": an,
                        "class": props.get("media.class"),
                        "state": o.get("info", {}).get("state"),
                        "props": {k: v for k, v in props.items()
                                  if not k.startswith("audio.position")}})
    return res


def clients_by_pid():
    """Map client.id -> application.process.pid for live clients."""
    out = {}
    for o in pw_dump():
        if o.get("type") != "PipeWire:Interface:Client":
            continue
        props = o.get("info", {}).get("props", {}) or {}
        pid = props.get("application.process.id") or props.get(
            "application.process.pid")
        try:
            pid = int(pid) if pid is not None else None
        except (TypeError, ValueError):
            pid = None
        out[o["id"]] = {"pid": pid,
                        "name": props.get("application.name"),
                        "process": props.get("application.process.binary")}
    return out


def nodes_of_pid(pid):
    """All stream nodes owned by the client with this OS pid — unambiguous
    even if a sibling lane also runs ffmpeg."""
    cmap = clients_by_pid()
    mine = {cid for cid, c in cmap.items() if c["pid"] == pid}
    res = []
    for o in pw_dump():
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        props = o.get("info", {}).get("props", {}) or {}
        if props.get("client.id") in mine:
            res.append({"id": o["id"],
                        "name": props.get("node.name", ""),
                        "media.name": props.get("media.name", ""),
                        "class": props.get("media.class"),
                        "state": o.get("info", {}).get("state"),
                        "props": {k: v for k, v in props.items()
                                  if not k.startswith("audio.position")}})
    return res


def node_props(node_id):
    for o in pw_dump():
        if o.get("id") == node_id and o.get("type") == "PipeWire:Interface:Node":
            return o.get("info", {}).get("props", {}) or {}
    return {}


def links_touching(name_rx):
    """Links where either endpoint node's name matches name_rx.
    Builds the port/node map from ONE fresh pw-dump per call."""
    rx = re.compile(name_rx)
    dump = pw_dump()
    node_name = {}
    port_info = {}
    for o in dump:
        t = o.get("type")
        if t == "PipeWire:Interface:Node":
            node_name[o["id"]] = (o.get("info", {}).get("props", {})
                                  or {}).get("node.name", str(o["id"]))
        elif t == "PipeWire:Interface:Port":
            pr = o.get("info", {}).get("props", {}) or {}
            port_info[o["id"]] = {"port.name": pr.get("port.name", "?"),
                                  "node.id": pr.get("node.id")}
    links = []
    for o in dump:
        if o.get("type") != "PipeWire:Interface:Link":
            continue
        props = o.get("info", {}).get("props", {}) or {}
        op = props.get("link.output.port")
        ip = props.get("link.input.port")
        on = node_name.get(port_info.get(op, {}).get("node.id"), "?")
        in_ = node_name.get(port_info.get(ip, {}).get("node.id"), "?")
        links.append({"out": f"{on}:{port_info.get(op, {}).get('port.name','?')}",
                      "in": f"{in_}:{port_info.get(ip, {}).get('port.name','?')}",
                      "mine_out": bool(rx.search(on)),
                      "mine_in": bool(rx.search(in_))})
    return links


def consumers_of(rx):
    """Set of peer node names feeding/fed by my ports, plus my link list."""
    links = links_touching(rx)
    cons = sorted({l["in"] for l in links if l["mine_out"]} |
                  {l["out"] for l in links if l["mine_in"]})
    mine = [f"{l['out']} -> {l['in']}" for l in links
            if l["mine_out"] or l["mine_in"]]
    return cons, mine


def pactl_load_null(name):
    rc, out, err = sh(["pactl", "load-module", "module-null-sink",
                       f"sink_name={name}",
                       "sink_properties=device.description=r82ff_scout_ns"],
                      timeout=10)
    idx = None
    m = re.search(r"(\d+)", out or "")
    if m:
        idx = int(m.group(1))
    return rc, idx, (out or "") + (err or "")


def pactl_unload(idx):
    return sh(["pactl", "unload-module", str(idx)], timeout=10)


def node_exists(name):
    return any(n["name"] == name for n in nodes_named(re.escape(name)))


def ensure_tone():
    # NB: a *pure* 1k/1.5k s16 dual-tone is mis-probed as mpegts by ffmpeg
    # (192-periodic 0x47 sync chains in the payload) — measured this session.
    # The ±30 LSB dither below keeps the FFT classifier happy and the probe safe.
    import random
    rng = random.Random(0x82)
    rate, ch, amp = 48000, 2, 8192
    for path, secs in ((TONE, 8.0), (TONE_SHORT, 2.0)):
        if path.exists() and path.stat().st_size > 1000:
            continue
        n = int(rate * secs)
        frames = bytearray()
        for i in range(n):
            l = int(amp * __import__("math").sin(2 * 3.141592653589793 * 1000 * i / rate)) + rng.randint(-30, 30)
            r = int(amp * __import__("math").sin(2 * 3.141592653589793 * 1500 * i / rate)) + rng.randint(-30, 30)
            frames += struct.pack("<hh", l, r)
        import wave as _w
        with _w.open(str(path), "wb") as w:
            w.setnchannels(ch); w.setsampwidth(2); w.setframerate(rate)
            w.writeframes(bytes(frames))


class Proc:
    """Spawn + triple-bounded collect (wall cap + byte cap in owner loop)."""
    def __init__(self, cmd, env=None, wall=10.0, byte_cap=8 << 20):
        self.cmd = cmd
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True,
                                  env=env, start_new_session=True)
        self.t0 = time.monotonic()
        self.wall = wall
        self.byte_cap = byte_cap
        self.rc = None
        self.out = []
        self.err = []
        import threading
        self._lock = threading.Lock()
        def rd(fh, acc):
            n = 0
            while True:
                c = fh.readline()
                if not c:
                    break
                with self._lock:
                    if n < self.byte_cap:
                        acc.append(c)
                        n += len(c)
            fh.close()
        self._t1 = threading.Thread(target=rd, args=(self.p.stdout, self.out), daemon=True)
        self._t2 = threading.Thread(target=rd, args=(self.p.stderr, self.err), daemon=True)
        self._t1.start(); self._t2.start()

    def poll(self):
        return self.p.poll()

    def finish(self):
        while time.monotonic() - self.t0 < self.wall:
            rc = self.p.poll()
            if rc is not None:
                self.rc = rc
                self._t1.join(1); self._t2.join(1)
                return self.rc, "".join(self.out), "".join(self.err), \
                    time.monotonic() - self.t0
            time.sleep(0.02)
        try:
            os.killpg(self.p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        self.p.wait(3)
        self.rc = self.p.returncode
        self._t1.join(1); self._t2.join(1)
        return self.rc, "".join(self.out), "".join(self.err), \
            time.monotonic() - self.t0

    def kill(self):
        try:
            os.killpg(self.p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            self.p.wait(3)
        except Exception:
            pass
        self.rc = self.p.returncode
        self._t1.join(1); self._t2.join(1)
        return self.rc, "".join(self.out), "".join(self.err)


def first_err_lines(err, n=3):
    lines = [l for l in (err or "").splitlines() if l.strip()]
    return lines[:n]


def save_receipt(leg_dir, cmd, rc, out, err, wall, extra=None):
    leg_dir.mkdir(parents=True, exist_ok=True)
    (leg_dir / "cmd.txt").write_text(" ".join(map(str, cmd)))
    (leg_dir / "stdout.txt").write_text(out or "")
    (leg_dir / "stderr.txt").write_text(err or "")
    meta = {"rc": rc, "wall_s": round(wall, 3)}
    if extra:
        meta.update(extra)
    (leg_dir / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta


# ------------------------------------------------------------------ stages
def stage_baseline():
    rec = {}
    rec["host_time_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for name, cmd in (
            ("ffmpeg_version", [FFMPEG, "-hide_banner", "-version"]),
            ("ffprobe_version", [FFPROBE, "-hide_banner", "-version"]),
            ("ffplay_version", ["ffplay", "-version"]),
            ("devices", [FFMPEG, "-hide_banner", "-devices"]),
            ("formats_pulse_rows", ["bash", "-c", "ffmpeg -hide_banner -formats 2>&1 | grep -iE 'pulse|pipe|alsa|jack|oss|sndio'"]),
            ("sources_pulse", [FFMPEG, "-hide_banner", "-sources", "pulse"]),
            ("sinks_pulse", [FFMPEG, "-hide_banner", "-sinks", "pulse"]),
            ("indev_pulse_help", [FFMPEG, "-hide_banner", "-h", "demuxer=pulse"]),
            ("outdev_pulse_help", [FFMPEG, "-hide_banner", "-h", "muxer=pulse"]),
            ("indev_alsa_help", [FFMPEG, "-hide_banner", "-h", "demuxer=alsa"]),
            ("pactl_info", ["pactl", "info"]),
            ("pactl_sinks", ["pactl", "list", "short", "sinks"]),
            ("pactl_sources", ["pactl", "list", "short", "sources"]),
            ("pactl_clients", ["pactl", "list", "short", "clients"]),
    ):
        rows = []
        for rep in range(3):
            rc, out, err = sh(cmd, timeout=20)
            rows.append({"rep": rep, "rc": rc, "out": out.strip(),
                         "err": first_err_lines(err)})
            time.sleep(0.15)
        rec[name] = rows
    (REC / "s0-baseline.json").write_text(json.dumps(rec, indent=1))
    print("baseline done")


def ensure_ns():
    """Load r82ff_ns unless a node with the name already exists and is ours."""
    if node_exists(NS):
        return None  # may be ours from an earlier stage — caller reuses
    rc, idx, txt = pactl_load_null(NS)
    return {"rc": rc, "idx": idx, "raw": txt.strip()}


def unload_ns(idx, name=NS):
    """Unload module index, only if pactl's module line maps it to OUR sink."""
    rc, out, _ = sh(["pactl", "list", "short", "modules"], timeout=10)
    for line in out.splitlines():
        m = re.match(rf"^{idx}\s+module-null-sink\s+.*sink_name={name}\b", line)
        if m:
            return pactl_unload(idx)
    return (1, "", f"refused: index {idx} does not map to {name}")


def cleanup_mine():
    """Unload every module-null-sink carrying an r82ff_* name, by index only."""
    rc, out, _ = sh(["pactl", "list", "short", "modules"], timeout=10)
    done = []
    for line in out.splitlines():
        m = re.match(r"^(\d+)\s+module-null-sink\s+.*sink_name=(r82ff_\w+)",
                     line)
        if m:
            r2, o2, e2 = pactl_unload(int(m.group(1)))
            done.append({"idx": int(m.group(1)), "name": m.group(2),
                         "rc": r2, "err": (e2 or "").strip()})
    return done


def ffplay_or_ffmpeg_play(cmd_in, extra, wall=12.0):
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin"] + cmd_in + extra
    return cmd


def stage_capture():
    """ffmpeg -f pulse capture lattice."""
    ensure_tone()
    res = {"ns_load": ensure_ns()}
    time.sleep(0.4)
    tone = Proc([FFMPEG, "-hide_banner", "-loglevel", "error", "-nostdin",
                 "-stream_loop", "-1", "-re", "-f", "wav", "-i", str(TONE),
                 "-f", "pulse", "-device", NS, "-name", "r82ff_tone_pump",
                 "-stream_name", "r82ff tone", "pulse-play"],
                wall=120)
    time.sleep(0.8)
    nsmon = NS + ".monitor"
    legs = [
        ("c0_default",      ["-f", "pulse", "-i", "default"]),
        ("c1_ns_monitor",   ["-f", "pulse", "-i", nsmon]),
        ("c2_ns_bare",      ["-f", "pulse", "-i", NS]),
        ("c3_bogus_src",    ["-f", "pulse", "-i", "no_such_source_r82"]),
        ("c4_named",        ["-f", "pulse", "-name", "r82ff_cap_name",
                             "-stream_name", "r82ff cap stream",
                             "-i", nsmon]),
        ("c5_spec_44k1",    ["-f", "pulse", "-sample_rate", "44100",
                             "-channels", "1", "-i", nsmon]),
        ("c6_env_props",    ["-f", "pulse", "-i", nsmon]),
        ("c7_bad_server",   ["-f", "pulse", "-server",
                             "unix:/nonexistent-r82", "-i", "default"]),
        ("c8_sink_name",    ["-f", "pulse", "-i", SPDIF]),
        ("c9_weird_ch7",    ["-f", "pulse", "-channels", "7", "-i", nsmon]),
        ("c10_srcname",     ["-f", "pulse", "-i", LINE]),
    ]
    reps = 3
    for name, inargs in legs:
        legdir = RUNS / "capture" / name
        legdir.mkdir(parents=True, exist_ok=True)
        rows = []
        for rep in range(reps):
            out_wav = legdir / f"r{rep}.wav"
            if out_wav.exists():
                out_wav.unlink()
            env = dict(os.environ)
            if name == "c6_env_props":
                env["PIPEWIRE_PROPS"] = "{ node.name=r82ff_env stream.capture.sink=true }"
            if name == "c8_sink_name":
                env["PIPEWIRE_PROPS"] = "{ stream.capture.sink=true node.name=r82ff_sinkname }"
            if name == "c1_ns_monitor" or name == "c4_named" or name == "c5_spec_44k1" or name == "c9_weird_ch7" or name == "c2_ns_bare" or name == "c10_srcname":
                env["PIPEWIRE_PROPS"] = "{ stream.capture.sink=true }"
            cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning",
                   "-nostdin", "-y"] + inargs + [
                   "-t", "2.0", "-c:a", "pcm_s16le", str(out_wav)]
            p = Proc(cmd, env=env, wall=15)
            time.sleep(0.9)   # let the stream node publish
            nodes = nodes_of_pid(p.p.pid)
            cons, links = consumers_of(r"r82ff|Lavf|ffmpeg")
            rc, out, err, wall = p.finish()
            peak = pcm_peak(out_wav)
            twin = tone_windows(out_wav)
            rows.append({"rep": rep, "rc": rc, "wall_s": round(wall, 3),
                         "wav": wav_shape(out_wav), "peak": peak,
                         "tone_windows": twin[:8],
                         "nodes": nodes, "consumers": cons, "links": links,
                         "stderr_head": first_err_lines(err)})
            save_receipt(legdir / f"r{rep}", cmd, rc, out, err, wall,
                         {"peak": peak, "wav": wav_shape(out_wav)})
            time.sleep(0.25)
        res[name] = rows
        (REC / "s1-capture.json").write_text(json.dumps(res, indent=1))
    tone.kill()
    cleanup_mine()
    print("capture done")


def stage_playback():
    ensure_tone()
    res = {"ns_load": ensure_ns()}
    time.sleep(0.4)
    reps = 3
    legs = [
        ("p0_honor_ns",   ["-device", NS], {}),
        ("p1_bogus",      ["-device", "no_such_sink_r82"], {}),
        ("p2_src_name",   ["-device", LINE], {}),
        ("p3_alias",      ["-device", "@DEFAULT_SINK@"], {}),
        ("p4_no_device",  [], {}),
        ("p5_named",      ["-device", NS, "-name", "r82ff_play_name",
                           "-stream_name", "r82ff play stream"], {}),
        ("p6_monitor_nm", ["-device", NS + ".monitor"], {}),
        ("p7_env_sink",   [], {"PULSE_SINK": NS}),
        ("p8_bad_server", ["-server", "unix:/nonexistent-r82",
                           "-device", NS], {}),
        ("p9_default_kw", ["-device", "default"], {}),
    ]
    for name, xargs, extra_env in legs:
        legdir = RUNS / "playback" / name
        legdir.mkdir(parents=True, exist_ok=True)
        rows = []
        for rep in range(reps):
            # content witness on both my ns monitor and the default sink monitor
            w_ns = legdir / f"r{rep}_wit_ns.wav"
            w_def = legdir / f"r{rep}_wit_def.wav"
            env_w = dict(os.environ)
            env_w["PIPEWIRE_PROPS"] = "{ stream.capture.sink=true }"
            wit1 = Proc([FFMPEG, "-hide_banner", "-loglevel", "error",
                         "-nostdin", "-y",
                         "-f", "pulse", "-i", NS + ".monitor",
                         "-name", "r82ff_wit1", "-t", "4.5",
                         "-c:a", "pcm_s16le", str(w_ns)], env=env_w, wall=12)
            wit2 = Proc([FFMPEG, "-hide_banner", "-loglevel", "error",
                         "-nostdin", "-y",
                         "-f", "pulse", "-i", SPDIF + ".monitor",
                         "-name", "r82ff_wit2", "-t", "4.5",
                         "-c:a", "pcm_s16le", str(w_def)], env=env_w, wall=12)
            time.sleep(0.6)
            env = dict(os.environ)
            env.update(extra_env)
            cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning",
                   "-nostdin", "-re", "-f", "wav", "-i", str(TONE_SHORT),
                   "-f", "pulse"] + xargs + ["r82ff-play"]
            p = Proc(cmd, env=env, wall=15)
            time.sleep(1.0)
            nodes = nodes_of_pid(p.p.pid)
            cons, links = consumers_of(r"r82ff|Lavf|ffmpeg")
            # pulse-level view of the sink-input while live
            rc_si, si, _ = sh(["pactl", "list", "sink-inputs"], timeout=10)
            si_rows = [l.strip() for l in si.splitlines()
                       if re.search(r"Sink Input|application.name|media.name|"
                                    r"sample spec|channel map|Latency|"
                                    r"device|target|node\.|format\.|rate", l)]
            rc_p, out, err, wall = p.finish()
            wit1.finish(); wit2.finish()
            rows.append({"rep": rep, "rc": rc_p, "wall_s": round(wall, 3),
                         "nodes": nodes, "consumers": cons, "links": links,
                         "sink_input": si_rows,
                         "wit_ns_peak": pcm_peak(w_ns),
                         "wit_ns_tone": tone_windows(w_ns)[:8],
                         "wit_def_peak": pcm_peak(w_def),
                         "wit_def_tone": tone_windows(w_def)[:8],
                         "stderr_head": first_err_lines(err)})
            save_receipt(legdir / f"r{rep}", cmd, rc_p, out, err, wall)
            time.sleep(0.3)
        res[name] = rows
        (REC / "s2-playback.json").write_text(json.dumps(res, indent=1))
    cleanup_mine()
    print("playback done")


def stage_loss():
    """Sink-loss re-link for ffmpeg pulse playback + capture, 3 reps each."""
    ensure_tone()
    res = {}
    for rep in range(3):
        # fresh ns each rep
        rc, idx, _ = pactl_load_null(NS)
        time.sleep(0.5)
        legdir = RUNS / "loss" / f"play_r{rep}"
        # playback: 8 s tone, unload at ~2 s
        env_w = dict(os.environ)
        env_w["PIPEWIRE_PROPS"] = "{ stream.capture.sink=true }"
        w_def = legdir
        w_def.mkdir(parents=True, exist_ok=True)
        wit = Proc([FFMPEG, "-hide_banner", "-loglevel", "error", "-nostdin",
                    "-y", "-f", "pulse", "-i", SPDIF + ".monitor",
                    "-name", "r82ff_wit_loss", "-t", "7.5",
                    "-c:a", "pcm_s16le", str(legdir / "wit_def.wav")],
                   env=env_w, wall=12)
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
               "-re", "-f", "wav", "-i", str(TONE), "-f", "pulse",
               "-device", NS, "-name", "r82ff_loss_play", "r82ff-play"]
        p = Proc(cmd, wall=14)
        timeline = []
        t_start = time.monotonic()
        unloaded = False
        while time.monotonic() - t_start < 9.5:
            t = time.monotonic() - t_start
            cons, links = consumers_of(r"r82ff_loss_play")
            timeline.append({"t": round(t, 2), "consumers": cons})
            if not unloaded and t >= 2.0:
                urc, uout, uerr = unload_ns(idx)
                timeline.append({"t": round(t, 2), "unload_rc": urc,
                                 "unload_err": (uerr or "").strip()})
                unloaded = True
            if p.poll() is not None:
                timeline.append({"t": round(t, 2), "proc_exit": p.poll()})
                break
            time.sleep(0.2)
        rc_p, out, err, wall = p.finish()
        wit.finish()
        rows = {"rep": rep, "rc": rc_p, "wall_s": round(wall, 3),
                "timeline": timeline,
                "wit_def_tone": tone_windows(legdir / "wit_def.wav"),
                "wit_def_peak": pcm_peak(legdir / "wit_def.wav"),
                "stderr_head": first_err_lines(err)}
        res.setdefault("play", []).append(rows)
        save_receipt(legdir / "play", cmd, rc_p, out, err, wall)
        cleanup_mine()
        time.sleep(0.4)

    for rep in range(3):
        rc, idx, _ = pactl_load_null(NS)
        time.sleep(0.5)
        legdir = RUNS / "loss" / f"cap_r{rep}"
        legdir.mkdir(parents=True, exist_ok=True)
        # tone INTO ns so the monitor carries it
        pump = Proc([FFMPEG, "-hide_banner", "-loglevel", "error", "-nostdin",
                     "-stream_loop", "-1", "-re", "-f", "wav", "-i",
                     str(TONE), "-f", "pulse", "-device", NS,
                     "-name", "r82ff_loss_pump", "pulse-play"], wall=15)
        time.sleep(0.8)
        env = dict(os.environ)
        env["PIPEWIRE_PROPS"] = "{ stream.capture.sink=true node.name=r82ff_loss_cap }"
        out_wav = legdir / "cap.wav"
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
               "-y", "-f", "pulse", "-name", "r82ff_loss_cap_c",
               "-i", NS + ".monitor", "-c:a", "pcm_s16le", str(out_wav)]
        p = Proc(cmd, env=env, wall=14)
        timeline = []
        sizes = []
        t_start = time.monotonic()
        unloaded = False
        while time.monotonic() - t_start < 8.5:
            t = time.monotonic() - t_start
            sizes.append({"t": round(t, 2),
                          "sz": out_wav.stat().st_size if out_wav.exists() else 0})
            cons, links = consumers_of(r"r82ff_loss_cap")
            timeline.append({"t": round(t, 2), "consumers": cons})
            if not unloaded and t >= 2.0:
                urc, uout, uerr = unload_ns(idx)
                timeline.append({"t": round(t, 2), "unload_rc": urc,
                                 "unload_err": (uerr or "").strip()})
                unloaded = True
            time.sleep(0.25)
        p.kill()
        pump.kill()
        rows = {"rep": rep, "rc": p.rc, "sizes": sizes, "timeline": timeline,
                "wav": wav_shape(out_wav),
                "tone_windows": tone_windows(out_wav),
                "stderr_head": first_err_lines("".join(p.err))}
        res.setdefault("cap", []).append(rows)
        cleanup_mine()
        time.sleep(0.4)
    (REC / "s3-loss.json").write_text(json.dumps(res, indent=1))
    print("loss done")


def stage_buffers():
    """Do the pulse buffer knobs reach pw stream props?"""
    ensure_tone()
    res = {"ns_load": ensure_ns()}
    time.sleep(0.4)
    reps = 3
    out_legs = [
        ("b0_default",   []),
        ("b1_bufsize",   ["-buffer_size", "16384"]),
        ("b2_bufdur",    ["-buffer_duration", "500"]),
        ("b3_prebuf",    ["-prebuf", "8192"]),
        ("b4_minreq",    ["-minreq", "512"]),
        ("b5_all",       ["-buffer_size", "32768", "-buffer_duration", "200",
                          "-prebuf", "16384", "-minreq", "1024"]),
        ("b6_bufsize_1", ["-buffer_size", "1"]),
    ]
    for name, xargs in out_legs:
        legdir = RUNS / "buffers" / name
        rows = []
        for rep in range(reps):
            cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
                   "-re", "-f", "wav", "-i", str(TONE), "-f", "pulse",
                   "-device", NS, "-name", f"r82ff_{name}"] + xargs + [
                   "r82ff-play"]
            p = Proc(cmd, wall=10)
            time.sleep(1.4)
            nodes = nodes_of_pid(p.p.pid)
            cons, links = consumers_of(rf"r82ff_{name}")
            rc_si, si, _ = sh(["pactl", "list", "sink-inputs"], timeout=10)
            # capture the block for OUR sink input only
            blocks = si.split("Sink Input #")
            myblock = [b for b in blocks if f"r82ff_{name}" in b or "Lavf" in b]
            si_rows = []
            for b in myblock[:1]:
                si_rows = [l.strip() for l in b.splitlines()
                           if re.search(r"Latency|application\.|media\.|"
                                        r"node\.|target|sample spec|Rate|"
                                        r"format\.|device", l)]
            p.kill()
            rows.append({"rep": rep, "rc": p.rc, "nodes": nodes,
                         "consumers": cons, "sink_input": si_rows,
                         "stderr_head": first_err_lines("".join(p.err))})
            save_receipt(legdir / f"r{rep}", cmd, p.rc,
                         "".join(p.out), "".join(p.err), 0)
            time.sleep(0.3)
        res[name] = rows
        (REC / "s4-buffers.json").write_text(json.dumps(res, indent=1))

    # indev knobs
    cap_legs = [
        ("ci0_default",  []),
        ("ci1_frag",     ["-fragment_size", "2048"]),
        ("ci2_frames",   ["-frame_size", "8192"]),
        ("ci3_frag_big", ["-fragment_size", "65536"]),
        ("ci4_rate44k",  ["-sample_rate", "44100", "-channels", "1"]),
    ]
    for name, xargs in cap_legs:
        legdir = RUNS / "buffers" / name
        rows = []
        for rep in range(reps):
            env = dict(os.environ)
            env["PIPEWIRE_PROPS"] = "{ stream.capture.sink=true node.name=%s }" % ("r82ff_" + name)
            cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
                   "-y", "-f", "pulse", "-i", NS + ".monitor",
                   "-name", "r82ff_" + name] + xargs + [
                   "-t", "2.0", "-c:a", "pcm_s16le",
                   str(legdir / f"r{rep}.wav")]
            legdir.mkdir(parents=True, exist_ok=True)
            p = Proc(cmd, env=env, wall=12)
            time.sleep(1.2)
            nodes = nodes_of_pid(p.p.pid)
            cons, links = consumers_of(rf"r82ff_{name}")
            rc, out, err, wall = p.finish()
            rows.append({"rep": rep, "rc": rc, "wall_s": round(wall, 3),
                         "wav": wav_shape(legdir / f"r{rep}.wav"),
                         "nodes": nodes, "consumers": cons,
                         "stderr_head": first_err_lines(err)})
            save_receipt(legdir / f"r{rep}", cmd, rc, out, err, wall)
            time.sleep(0.3)
        res[name] = rows
        (REC / "s4-buffers.json").write_text(json.dumps(res, indent=1))
    cleanup_mine()
    print("buffers done")


def stage_alsa():
    """-f alsa under contention + bogus PCM."""
    ensure_tone()
    res = {}
    reps = 3
    # a) capture from hw:0,0 while arecord holds it
    rows = []
    for rep in range(reps):
        legdir = RUNS / "alsa" / "cap_hw00_busy"
        legdir.mkdir(parents=True, exist_ok=True)
        holder = Proc(["arecord", "-D", "hw:0,0", "-f", "cd", "-d", "8",
                       str(legdir / f"hold_r{rep}.wav")], wall=12)
        time.sleep(0.8)
        out_wav = legdir / f"r{rep}.wav"
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
               "-y", "-f", "alsa", "-i", "hw:0,0", "-t", "2.0",
               "-c:a", "pcm_s16le", str(out_wav)]
        _t0 = time.monotonic()
        rc, out, err = sh(cmd, timeout=12)
        wall = time.monotonic() - _t0
        rows.append({"rep": rep, "rc": rc, "wall_s": round(wall, 3),
                     "wav": wav_shape(out_wav),
                     "stderr_head": first_err_lines(err)})
        save_receipt(legdir / f"r{rep}", cmd, rc, out, err, wall)
        holder.kill()
        time.sleep(0.4)
    res["cap_hw00_busy"] = rows
    # b) playback to hw:0,0 while aplay holds it
    rows = []
    for rep in range(reps):
        legdir = RUNS / "alsa" / "play_hw00_busy"
        legdir.mkdir(parents=True, exist_ok=True)
        holder = Proc(["aplay", "-D", "hw:0,0", str(TONE)], wall=14)
        time.sleep(0.8)
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
               "-re", "-f", "wav", "-i", str(TONE_SHORT), "-f", "alsa",
               "hw:0,0"]
        _t0 = time.monotonic()
        rc, out, err = sh(cmd, timeout=12)
        wall = time.monotonic() - _t0
        rows.append({"rep": rep, "rc": rc, "wall_s": round(wall, 3),
                     "stderr_head": first_err_lines(err)})
        save_receipt(legdir / f"r{rep}", cmd, rc, out, err, wall)
        holder.kill()
        time.sleep(0.6)
    res["play_hw00_busy"] = rows
    # c) PipeWire holds hw:0,0 (Speaker sink live stream) -> ffmpeg -f alsa
    rows = []
    for rep in range(reps):
        legdir = RUNS / "alsa" / "cap_hw00_pwheld"
        legdir.mkdir(parents=True, exist_ok=True)
        pump = Proc([FFMPEG, "-hide_banner", "-loglevel", "error", "-nostdin",
                     "-stream_loop", "-1", "-re", "-f", "wav", "-i",
                     str(TONE), "-f", "pulse", "-device", SPEAKER,
                     "-name", "r82ff_hold_spk", "pulse-play"], wall=14)
        time.sleep(1.0)
        out_wav = legdir / f"r{rep}.wav"
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
               "-y", "-f", "alsa", "-i", "hw:0,0", "-t", "2.0",
               "-c:a", "pcm_s16le", str(out_wav)]
        _t0 = time.monotonic()
        rc, out, err = sh(cmd, timeout=12)
        wall = time.monotonic() - _t0
        rows.append({"rep": rep, "rc": rc, "wall_s": round(wall, 3),
                     "wav": wav_shape(out_wav),
                     "stderr_head": first_err_lines(err)})
        save_receipt(legdir / f"r{rep}", cmd, rc, out, err, wall)
        pump.kill()
        time.sleep(6.5)   # alsa_lock_retention — wait out the lock
    res["cap_hw00_pwheld"] = rows
    # d) bogus + refused PCMs
    for name, dev in (("cap_bogus", "no_such_pcm_r82"),
                      ("cap_pipewire", "pipewire"),
                      ("cap_default", "default"),
                      ("cap_sysdefault", "sysdefault")):
        rows = []
        for rep in range(reps):
            legdir = RUNS / "alsa" / name
            legdir.mkdir(parents=True, exist_ok=True)
            out_wav = legdir / f"r{rep}.wav"
            cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
                   "-y", "-f", "alsa", "-i", dev, "-t", "1.5",
                   "-c:a", "pcm_s16le", str(out_wav)]
            _t0 = time.monotonic()
            rc, out, err = sh(cmd, timeout=10)
            wall = time.monotonic() - _t0
            rows.append({"rep": rep, "rc": rc, "wall_s": round(wall, 3),
                         "wav": wav_shape(out_wav),
                         "peak": pcm_peak(out_wav),
                         "stderr_head": first_err_lines(err)})
            save_receipt(legdir / f"r{rep}", cmd, rc, out, err, wall)
            time.sleep(0.3)
        res[name] = rows
    (REC / "s5-alsa.json").write_text(json.dumps(res, indent=1))
    print("alsa done")


def stage_errors():
    """Negotiation-failure + misc refusal shapes."""
    ensure_tone()
    res = {"ns_load": ensure_ns()}
    time.sleep(0.4)
    legs = [
        ("e1_rate0",      ["-f", "pulse", "-sample_rate", "0", "-i", "default"]),
        ("e2_ch0",        ["-f", "pulse", "-channels", "0", "-i", "default"]),
        ("e3_ch99",       ["-f", "pulse", "-channels", "99",
                           "-i", NS + ".monitor"]),
        ("e4_rate999999", ["-f", "pulse", "-sample_rate", "999999",
                           "-i", NS + ".monitor"]),
        ("e5_frag_neg",   ["-f", "pulse", "-fragment_size", "-2",
                           "-i", NS + ".monitor"]),
        ("e6_bogus_fmt",  ["-f", "pulse", "-i", "default"]),
    ]
    reps = 3
    for name, inargs in legs:
        legdir = RUNS / "errors" / name
        legdir.mkdir(parents=True, exist_ok=True)
        rows = []
        for rep in range(reps):
            env = dict(os.environ)
            env["PIPEWIRE_PROPS"] = "{ stream.capture.sink=true node.name=%s }" % ("r82ff_" + name)
            out_wav = legdir / f"r{rep}.wav"
            cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning",
                   "-nostdin", "-y"] + inargs + [
                   "-t", "1.5", "-c:a", "pcm_s16le", str(out_wav)]
            _t0 = time.monotonic()
            rc, out, err = sh(cmd, timeout=12, env=env)
            wall = time.monotonic() - _t0
            rows.append({"rep": rep, "rc": rc, "wall_s": round(wall, 3),
                         "wav": wav_shape(out_wav),
                         "stderr_head": first_err_lines(err, 4)})
            save_receipt(legdir / f"r{rep}", cmd, rc, out, err, wall)
            time.sleep(0.25)
        res[name] = rows
        (REC / "s6-errors.json").write_text(json.dumps(res, indent=1))
    cleanup_mine()
    print("errors done")


def stage_final():
    """Cleanup: unload any r82ff_ns still loaded (by index, verified)."""
    rc, out, _ = sh(["pactl", "list", "short", "modules"], timeout=10)
    unloaded = []
    for line in out.splitlines():
        m = re.match(r"^(\d+)\s+module-null-sink\s+.*sink_name=(r82ff_\w+)",
                     line)
        if m:
            r2, o2, e2 = pactl_unload(int(m.group(1)))
            unloaded.append({"idx": int(m.group(1)), "name": m.group(2),
                             "rc": r2, "err": (e2 or "").strip()})
    remain = nodes_named(r"r82ff")
    rec = {"unloaded": unloaded, "remaining_r82ff_nodes": remain}
    (REC / "s9-final.json").write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec, indent=1))


STAGES = {"baseline": stage_baseline, "capture": stage_capture,
          "playback": stage_playback, "loss": stage_loss,
          "buffers": stage_buffers, "alsa": stage_alsa,
          "errors": stage_errors, "final": stage_final}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=sorted(STAGES))
    a = ap.parse_args()
    STAGES[a.stage]()
