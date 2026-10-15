#!/usr/bin/env python3
"""R82 BOUNDARY harness — stress the r82 scout's ffmpeg/pulse claims at edges.

Seat scope: corpus/live/r82-boundary/ ONLY. No tracked-file edits. Own tone
(numpy), own Goertzel classifier, own receipts. Every leg is bounded: output
bound (-t), wall cap (subprocess timeout), and captures are `-t` bounded.

Seat-owned names: r82bnd_* (sink r82bnd_ns, nodes r82bnd_*). The only sink
loaded is module-null-sink sink_name=r82bnd_ns; unload is strictly by the
module index returned by load-module, re-verified against
`pactl list short modules` (module-null-sink + sink_name=r82bnd_ns) before
issuing unload-module. No set-default-* ever.

Usage: r82bnd_probe.py <stage>  in
  {setup, c1, c2, c3, c4, c5, c6, teardown, manifest}
"""
import argparse
import hashlib
import json
import os
import re
import resource
import struct
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
RUNS = OUT / "runs"
TMP = OUT / "tmp"
REC = OUT / "receipts"
for _d in (RUNS, TMP, REC):
    _d.mkdir(parents=True, exist_ok=True)

NS = "r82bnd_ns"
TAG = "r82bnd"
STATE = OUT / ".state.json"
SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
LINE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
TONE2 = TMP / "tone2.wav"
TONE6 = TMP / "tone6.wav"
TONE7 = TMP / "tone7.wav"
FFMPEG = "ffmpeg"

WALL_DEFAULT = 12.0


def _nocore():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def sh(cmd, timeout=30, env=None):
    """Run, return (rc, stdout, stderr, wall). rc None = timeout."""
    c = [os.fsencode(x) if isinstance(x, str) else x for x in cmd]
    t0 = time.monotonic()
    try:
        r = subprocess.run(c, capture_output=True, timeout=timeout, env=env,
                           preexec_fn=_nocore)
        return r.returncode, r.stdout.decode("utf-8", "replace"), \
            r.stderr.decode("utf-8", "replace"), round(time.monotonic() - t0, 3)
    except subprocess.TimeoutExpired as e:
        return None, (e.stdout or b"").decode("utf-8", "replace"), \
            (e.stderr or b"").decode("utf-8", "replace"), \
            round(time.monotonic() - t0, 3)


def sha16(path):
    p = Path(path)
    if not p.exists() or p.is_dir():
        return None
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=1))


# ---------------------------------------------------------------- tone
def make_tone(path, secs, rate=48000, amp=8192, seed=0x82):
    if path.exists() and path.stat().st_size > 1000:
        return
    rng = np.random.default_rng(seed)
    n = int(rate * secs)
    t = np.arange(n) / rate
    l = (amp * np.sin(2 * np.pi * 1000 * t)
         + rng.integers(-30, 31, size=n)).astype("<i2")
    r = (amp * np.sin(2 * np.pi * 1500 * t)
         + rng.integers(-30, 31, size=n)).astype("<i2")
    st = np.column_stack([l, r]).ravel()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(st.tobytes())


def ensure_tones():
    make_tone(TONE2, 2.0)
    make_tone(TONE6, 6.0)
    make_tone(TONE7, 7.0)


def read_wav(path):
    """(float data [n,ch], rate) or (None, 0)."""
    try:
        w = wave.open(str(path), "rb")
        ch = w.getnchannels()
        rate = w.getframerate()
        sw = w.getsampwidth()
        raw = w.readframes(w.getnframes())
        w.close()
        if sw != 2 or ch < 1:
            return None, rate
        d = np.frombuffer(raw, dtype="<i2")
        if d.size < ch:
            return None, rate
        return d[: (d.size // ch) * ch].reshape(-1, ch).astype(float), rate
    except Exception:
        return None, 0


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


def tone_windows(path, win_s=0.5, amp_lo=800, amp_hi=20000):
    """Windowed dual-tone classifier (L@1000, R@1500), cross terms quiet."""
    d, rate = read_wav(path)
    if d is None or rate <= 0:
        return []
    winsz = int(rate * win_s)
    out = []
    for off in range(0, max(0, d.shape[0] - winsz + 1), winsz):
        seg = d[off:off + winsz]
        t = np.arange(seg.shape[0]) / rate
        l1k = abs(np.dot(seg[:, 0], np.exp(-2j * np.pi * 1000 * t))) / len(t)
        l15 = abs(np.dot(seg[:, 0], np.exp(-2j * np.pi * 1500 * t))) / len(t)
        r15 = abs(np.dot(seg[:, 1], np.exp(-2j * np.pi * 1500 * t))) / len(t)
        r1k = abs(np.dot(seg[:, 1], np.exp(-2j * np.pi * 1000 * t))) / len(t)
        if (amp_lo <= l1k <= amp_hi and amp_lo <= r15 <= amp_hi
                and l15 < 0.15 * l1k and r1k < 0.15 * r15):
            out.append(round(off / rate, 2))
    return out


# ------------------------------------------------------------- pipewire
def pw_dump():
    rc, out, _, _ = sh(["pw-dump"], timeout=15)
    if rc != 0:
        return []
    try:
        return json.loads(out)
    except Exception:
        return []


def pw_snapshot(pid=None, name_rx=None):
    """Nodes (+props) and links; if pid given, only that client's nodes.
    If name_rx given, only links touching a node whose name matches."""
    dump = pw_dump()
    cmap = {}
    node_name = {}
    node_of_client = {}
    ports = {}
    for o in dump:
        t = o.get("type")
        if t == "PipeWire:Interface:Client":
            pr = o.get("info", {}).get("props", {}) or {}
            try:
                p = int(pr.get("application.process.id") or 0)
            except (TypeError, ValueError):
                p = 0
            cmap[o["id"]] = p
        elif t == "PipeWire:Interface:Node":
            pr = o.get("info", {}).get("props", {}) or {}
            node_name[o["id"]] = pr.get("node.name", str(o["id"]))
            node_of_client.setdefault(pr.get("client.id"), []).append(o["id"])
        elif t == "PipeWire:Interface:Port":
            pr = o.get("info", {}).get("props", {}) or {}
            ports[o["id"]] = {"port.name": pr.get("port.name", "?"),
                              "node.id": pr.get("node.id")}
    my_nodes = []
    for o in dump:
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        pr = o.get("info", {}).get("props", {}) or {}
        cid = pr.get("client.id")
        if pid is not None and cmap.get(cid) != pid:
            continue
        if name_rx is not None and not re.search(name_rx, pr.get("node.name", "")):
            continue
        my_nodes.append({
            "id": o["id"], "name": pr.get("node.name", ""),
            "media.name": pr.get("media.name", ""),
            "class": pr.get("media.class"),
            "state": o.get("info", {}).get("state"),
            "props": {k: v for k, v in pr.items()
                      if not k.startswith("audio.position")}})
    my_ids = {n["id"] for n in my_nodes}
    links = []
    for o in dump:
        if o.get("type") != "PipeWire:Interface:Link":
            continue
        pr = o.get("info", {}).get("props", {}) or {}
        op, ip = pr.get("link.output.port"), pr.get("link.input.port")
        on = node_name.get(ports.get(op, {}).get("node.id"), "?")
        inn = node_name.get(ports.get(ip, {}).get("node.id"), "?")
        onid = ports.get(op, {}).get("node.id")
        inid = ports.get(ip, {}).get("node.id")
        if onid in my_ids or inid in my_ids:
            links.append({"out": f"{on}:{ports.get(op, {}).get('port.name','?')}",
                          "in": f"{inn}:{ports.get(ip, {}).get('port.name','?')}",
                          "out_id": onid, "in_id": inid})
    return {"nodes": my_nodes, "links": links}


def peer_sinks(pid):
    """Names of nodes my pid's output ports are linked into."""
    snap = pw_snapshot(pid=pid)
    return sorted({l["in"].split(":")[0] for l in snap["links"]})


def node_names_for_pid(pid):
    return [n["name"] for n in pw_snapshot(pid=pid)["nodes"]]


# ------------------------------------------------------------- pactl
def sinks_short():
    _, out, _, _ = sh(["pactl", "list", "short", "sinks"], timeout=10)
    return out


def modules_short():
    _, out, _, _ = sh(["pactl", "list", "short", "modules"], timeout=10)
    return out


def ns_module_row(idx):
    for line in modules_short().splitlines():
        parts = line.split("\t")
        if not parts:
            continue
        if parts[0].strip() == str(idx):
            return line
    return None


def ns_sink_rows():
    """Sink rows whose name is exactly NS (monitors are sources, not sinks)."""
    return [l for l in sinks_short().splitlines()
            if re.match(r"^\d+\t" + re.escape(NS) + r"\t", l)]


def ns_module_rows():
    return [l for l in modules_short().splitlines()
            if "module-null-sink" in l and f"sink_name={NS}" in l]


def cleanup_all_ns():
    """Unload every module-null-sink sink_name=r82bnd_ns by VERIFIED index."""
    out = []
    for line in ns_module_rows():
        idx = int(line.split("\t")[0].strip())
        out.append({"idx": idx, "row": line, "unload": unload_ns(idx)})
    return out


def ensure_ns():
    st = load_state()
    rows = ns_sink_rows()
    if len(rows) == 1:
        mods = ns_module_rows()
        if len(mods) == 1:
            st["ns_idx"] = int(mods[0].split("\t")[0].strip())
            save_state(st)
            return st["ns_idx"], "already-loaded"
        return None, f"sink-exists-but-{len(mods)}-module-rows"
    if len(rows) > 1:
        return None, f"DUPLICATE-SINKS:{len(rows)}"
    rc, out, err, wall = sh(["pactl", "load-module", "module-null-sink",
                             f"sink_name={NS}",
                             "sink_properties=device.description=r82bnd_ns"],
                            timeout=10)
    m = re.search(r"(\d+)", out or "")
    if rc != 0 or not m:
        return None, f"load-failed rc={rc} out={out!r} err={err!r}"
    idx = int(m.group(1))
    row = ns_module_row(idx)
    if not row or "module-null-sink" not in row or f"sink_name={NS}" not in row:
        return None, f"load-index-verify-failed idx={idx} row={row!r}"
    st["ns_idx"] = idx
    save_state(st)
    return idx, "loaded"


def unload_ns(idx):
    """Index-verified unload: refuse unless the index row is our module."""
    row = ns_module_row(idx)
    if not row or "module-null-sink" not in row or f"sink_name={NS}" not in row:
        return {"ok": False, "refused": True, "row": row}
    rc, out, err, wall = sh(["pactl", "unload-module", str(idx)], timeout=10)
    gone = len(ns_sink_rows()) == 0
    row_after = ns_module_row(idx)
    st = load_state()
    if st.get("ns_idx") == idx:
        st.pop("ns_idx", None)
        save_state(st)
    return {"ok": rc == 0 and gone, "refused": False, "rc": rc,
            "row_before": row, "row_after": row_after, "sink_gone": gone,
            "err": err.strip()[:200]}


# ------------------------------------------------------------- receipts
def leg_dir(stage, leg):
    d = RUNS / stage / leg
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_leg(stage, leg, cmd, rc, out, err, wall, extra=None, files=None):
    d = leg_dir(stage, leg)
    cmd_s = cmd if isinstance(cmd, str) else " ".join(
        x if isinstance(x, str) else repr(x) for x in cmd)
    (d / "cmd.txt").write_text(cmd_s + "\n")
    (d / "stdout.txt").write_text(out or "")
    (d / "stderr.txt").write_text(err or "")
    meta = {"leg": leg, "stage": stage, "rc": rc, "wall_s": wall,
            "stderr_head": (err or "").strip().splitlines()[:6]}
    if extra:
        meta.update(extra)
    if files:
        meta["files"] = {k: {"sha16": sha16(v), "shape": wav_shape(v)}
                         for k, v in files.items()}
    (d / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def save_stage(stage, legs):
    REC.mkdir(parents=True, exist_ok=True)
    p = REC / f"{stage}.json"
    p.write_text(json.dumps(legs, indent=1))
    return p


def inventory():
    rc, info, _, _ = sh(["pactl", "info"], timeout=10)
    _, dev, _, _ = sh(["ffmpeg", "-hide_banner", "-devices"], timeout=10)
    _, mods, _, _ = sh(["pactl", "list", "short", "modules"], timeout=10)
    return {"pactl_info": [l for l in info.splitlines()
                           if l.startswith(("Server Name", "Default Sink",
                                            "Default Source"))],
            "ffmpeg_devices_audio": [l for l in dev.splitlines()
                                     if re.search(r"\b(alsa|pulse|jack|oss|sndio)\b", l)],
            "foreign_modules": [l for l in mods.splitlines()
                                if TAG not in l and "sink_name=r82bnd" not in l],
            "sinks": sinks_short().splitlines(),
            "loadavg": Path("/proc/loadavg").read_text().strip()}


# =============================================================== stages
def stage_setup():
    ensure_tones()
    idx, how = ensure_ns()
    inv = inventory()
    st = load_state()
    st["setup"] = {"ns_idx": idx, "how": how, "ts": time.strftime("%FT%TZ", time.gmtime())}
    save_state(st)
    rec = {"ns_idx": idx, "how": how, "inventory": inv,
           "ffmpeg_version": sh(["ffmpeg", "-version"])[1].splitlines()[:1],
           "tones": {p.name: {"sha16": sha16(p), "shape": wav_shape(p)}
                     for p in (TONE2, TONE6, TONE7)}}
    save_stage("setup", rec)
    print(json.dumps({"ns_idx": idx, "how": how}, indent=1))


# ---------------------------------------------------------------- C1
C1_LEGS = [
    ("valid_ns", "r82bnd_ns"),
    ("bogus", "no_such_sink_r82bnd"),
    ("monitor_name", "r82bnd_ns.monitor"),
    ("source_name", LINE),
    ("empty", ""),
    ("spaces", "   "),
    ("space_inside", "no such sink r82bnd"),
    ("unicode", "r82bnd_\U0001F3B5_sink"),
    ("invalid_utf8", b"\xff\xfe"),
    ("long512", "x" * 512),
    ("default_kw", "default"),
    ("alias_default_monitor", "@DEFAULT_MONITOR@"),
    ("alias_default_source", "@DEFAULT_SOURCE@"),
]


def _bg_witness(tag, dev, secs, out):
    c = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin", "-y",
         "-f", "pulse", "-name", f"{TAG}_wit_{tag}", "-i", dev,
         "-t", str(secs), "-c:a", "pcm_s16le", str(out)]
    fh = open(out.with_suffix(".stderr.log"), "wb")
    p = subprocess.Popen([os.fsencode(x) if isinstance(x, str) else x for x in c],
                         stdout=subprocess.DEVNULL, stderr=fh,
                         preexec_fn=_nocore)
    return p, fh


def stage_c1():
    idx, how = ensure_ns()
    ensure_tones()
    inv = inventory()
    legs = []
    for leg, dev in C1_LEGS:
        d = leg_dir("c1", leg)
        wit_def = d / "wit_def.wav"
        wit_ns = d / "wit_ns.wav"
        for f in (wit_def, wit_ns):
            f.unlink(missing_ok=True)
        w1, f1 = _bg_witness("def", f"{SPDIF}.monitor", 3.6, wit_def)
        w2, f2 = _bg_witness("ns", f"{NS}.monitor", 3.6, wit_ns)
        time.sleep(0.25)
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
               "-re", "-f", "wav", "-i", str(TONE2),
               "-f", "pulse", "-name", f"{TAG}_p1", "-device",
               dev if not isinstance(dev, bytes) else dev,
               f"{TAG}-play"]
        t0 = time.monotonic()
        p = subprocess.Popen([os.fsencode(x) if isinstance(x, str) else x for x in cmd],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             preexec_fn=_nocore)
        time.sleep(1.0)
        snap = pw_snapshot(pid=p.pid)
        time.sleep(0.05)
        try:
            out_b, err_b = p.communicate(timeout=6.0)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            p.kill()
            out_b, err_b = p.communicate()
            rc = None
        wall = round(time.monotonic() - t0, 3)
        for w, fh in ((w1, f1), (w2, f2)):
            try:
                w.wait(timeout=6.0)
            except subprocess.TimeoutExpired:
                w.kill()
            fh.close()
        extra = {
            "device_repr": repr(dev) if isinstance(dev, bytes) else dev,
            "player_rc": rc,
            "player_nodes": [{"name": n["name"], "media.name": n["media.name"],
                              "target.object": n["props"].get("target.object"),
                              "client.api": n["props"].get("client.api")}
                             for n in snap["nodes"]],
            "player_links": [f"{l['out']} -> {l['in']}" for l in snap["links"]],
            "peer_sinks": sorted({l["in"].split(":")[0] for l in snap["links"]}),
            "wit_def_tone_windows": tone_windows(wit_def, 0.5),
            "wit_ns_tone_windows": tone_windows(wit_ns, 0.5),
            "wit_def_shape": wav_shape(wit_def),
            "wit_ns_shape": wav_shape(wit_ns),
        }
        legs.append(save_leg("c1", leg, cmd, rc,
                             out_b.decode("utf-8", "replace"),
                             err_b.decode("utf-8", "replace"), wall, extra,
                             files={"wit_def": wit_def, "wit_ns": wit_ns}))
        print(f"c1 {leg:22s} rc={rc} peers={extra['peer_sinks']} "
              f"def={extra['wit_def_tone_windows'][:3]} ns={extra['wit_ns_tone_windows'][:3]}",
              flush=True)
    save_stage("c1", {"ns_idx": idx, "how": how, "inventory": inv, "legs": legs})


# ---------------------------------------------------------------- C2
def stage_c2():
    idx, how = ensure_ns()
    inv = inventory()
    legs = []
    o = TMP / "c2_out.wav"

    def cap_leg(leg, args, reps, timeout=8.0):
        for r in range(reps):
            o.unlink(missing_ok=True)
            cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
                   "-y"] + args + [str(o)]
            rc, out, err, wall = sh(cmd, timeout=timeout)
            extra = {"rep": r, "wav": wav_shape(o), "shape": wav_shape(o)}
            legs.append(save_leg("c2", f"{leg}_r{r}", cmd, rc, out, err, wall,
                                 extra, files={"out": o}))
            print(f"c2 {leg} r{r} rc={rc} wall={wall}", flush=True)

    cap_leg("sink_bare", ["-f", "pulse", "-i", NS, "-t", "2"], 5)
    cap_leg("bogus_source", ["-f", "pulse", "-i", "no_such_source_r82bnd",
                             "-t", "2"], 5)
    cap_leg("default_kw", ["-f", "pulse", "-i", "default", "-t", "2"], 6,
            timeout=8.0)
    cap_leg("default_monitor_alias", ["-f", "pulse", "-i", "@DEFAULT_MONITOR@",
                                      "-t", "1"], 2)
    cap_leg("default_source_alias", ["-f", "pulse", "-i", "@DEFAULT_SOURCE@",
                                     "-t", "1"], 2)
    cap_leg("monitor_ok", ["-f", "pulse", "-i", f"{NS}.monitor", "-t", "1"], 2)
    cap_leg("nonexistent_monitor", ["-f", "pulse", "-i",
                                    "no_such_sink_r82bnd.monitor", "-t", "1"], 2)

    # ALSA busy-PCM cell: hold hw:0,0 with arecord, then ffmpeg
    for r in range(2):
        hold = subprocess.Popen(["arecord", "-D", "hw:0,0", "-f", "S16_LE",
                                 "-r", "48000", "-c", "2", "-d", "3",
                                 str(TMP / "c2_hold.wav")],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, preexec_fn=_nocore)
        time.sleep(0.4)
        o.unlink(missing_ok=True)
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
               "-y", "-f", "alsa", "-i", "hw:0,0", "-t", "1", str(o)]
        rc, out, err, wall = sh(cmd, timeout=8.0)
        legs.append(save_leg("c2", f"alsa_busy_hw00_r{r}", cmd, rc, out, err,
                             wall, {"rep": r, "wav": wav_shape(o),
                                    "holder_pid": hold.pid},
                             files={"out": o}))
        print(f"c2 alsa_busy_hw00 r{r} rc={rc} wall={wall}", flush=True)
        hold.terminate()
        try:
            hold.wait(timeout=3)
        except subprocess.TimeoutExpired:
            hold.kill()

    # ALSA default via pipewire-alsa (contrast: rc should be 0)
    o.unlink(missing_ok=True)
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin", "-y",
           "-f", "alsa", "-i", "default", "-t", "1", str(o)]
    rc, out, err, wall = sh(cmd, timeout=8.0)
    legs.append(save_leg("c2", "alsa_default_r0", cmd, rc, out, err, wall,
                         {"wav": wav_shape(o)}, files={"out": o}))
    print(f"c2 alsa_default r0 rc={rc} wall={wall}", flush=True)
    save_stage("c2", {"ns_idx": idx, "how": how, "inventory": inv, "legs": legs})


# ---------------------------------------------------------------- C3
def _c3_capture_leg(leg, args, secs=1.5, timeout=8.0, loglevel="warning"):
    """args placed between '-f pulse' and '-i NS.monitor' (pre) OR after the
    input (post) — the caller passes the full option list in order."""
    d = leg_dir("c3", leg)
    o = d / "out.wav"
    o.unlink(missing_ok=True)
    cmd = [FFMPEG, "-hide_banner", "-loglevel", loglevel, "-nostdin", "-y"] \
        + args + ["-t", str(secs), "-c:a", "pcm_s16le", str(o)]
    t0 = time.monotonic()
    p = subprocess.Popen([os.fsencode(x) if isinstance(x, str) else x for x in cmd],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         preexec_fn=_nocore)
    time.sleep(0.8)
    snap = pw_snapshot(pid=p.pid)
    try:
        out_b, err_b = p.communicate(timeout=timeout)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        p.kill()
        out_b, err_b = p.communicate()
        rc = None
    wall = round(time.monotonic() - t0, 3)
    extra = {
        "nodes": [{"name": n["name"], "media.name": n["media.name"],
                   "fragsize": n["props"].get("pulse.attr.fragsize"),
                   "latency": n["props"].get("node.latency"),
                   "target.object": n["props"].get("target.object")}
                  for n in snap["nodes"]],
        "wav": wav_shape(o),
    }
    meta = save_leg("c3", leg, cmd, rc, out_b.decode("utf-8", "replace"),
                    err_b.decode("utf-8", "replace"), wall, extra,
                    files={"out": o})
    print(f"c3 {leg:26s} rc={rc} nodes={[(n['name'], n['fragsize'], n['latency'], n['media.name']) for n in extra['nodes']]} "
          f"wav={extra['wav'].get('rate')}x{extra['wav'].get('ch')}", flush=True)
    return meta


def stage_c3():
    idx, how = ensure_ns()
    inv = inventory()
    legs = []
    M = f"{NS}.monitor"

    legs.append(_c3_capture_leg(
        "pre_frag", ["-f", "pulse", "-fragment_size", "2048", "-i", M]))
    legs.append(_c3_capture_leg(
        "post_frag", ["-f", "pulse", "-i", M, "-fragment_size", "2048"]))
    legs.append(_c3_capture_leg(
        "post_frag_verbose", ["-f", "pulse", "-i", M, "-fragment_size", "2048"],
        loglevel="verbose"))
    legs.append(_c3_capture_leg(
        "post_wallclock", ["-f", "pulse", "-i", M, "-wallclock", "0"]))
    legs.append(_c3_capture_leg(
        "post_wallclock_verbose", ["-f", "pulse", "-i", M, "-wallclock", "0"],
        loglevel="verbose"))
    legs.append(_c3_capture_leg(
        "post_stream_name", ["-f", "pulse", "-i", M, "-stream_name", "POSTBND"]))
    legs.append(_c3_capture_leg(
        "pre_stream_name", ["-f", "pulse", "-stream_name", "PREBND", "-i", M]))
    legs.append(_c3_capture_leg(
        "post_channels_rate", ["-f", "pulse", "-i", M, "-channels", "1",
                               "-sample_rate", "44100"]))
    legs.append(_c3_capture_leg(
        "pre_channels_rate", ["-f", "pulse", "-channels", "1",
                              "-sample_rate", "44100", "-i", M]))
    legs.append(_c3_capture_leg(
        "post_frame_size_8192", ["-f", "pulse", "-i", M, "-frame_size", "8192"]))
    legs.append(_c3_capture_leg(
        "post_frame_size_1024", ["-f", "pulse", "-i", M, "-frame_size", "1024"]))
    legs.append(_c3_capture_leg(
        "post_frame_size_1", ["-f", "pulse", "-i", M, "-frame_size", "1"]))
    legs.append(_c3_capture_leg(
        "pre_frame_size_8192", ["-f", "pulse", "-frame_size", "8192", "-i", M]))
    legs.append(_c3_capture_leg(
        "pre_buffer_size", ["-f", "pulse", "-buffer_size", "16384", "-i", M]))
    legs.append(_c3_capture_leg(
        "post_buffer_size", ["-f", "pulse", "-i", M, "-buffer_size", "16384"]))
    legs.append(_c3_capture_leg(
        "post_server", ["-f", "pulse", "-i", M, "-server", "unix:/nonexistent-r82bnd"]))

    # lavfi controls (no audio server) for the position law
    lav = [("lavfi_post_wallclock",
            ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "0.2",
             "-wallclock", "0"]),
           ("lavfi_pre_wallclock",
            ["-f", "lavfi", "-wallclock", "0", "-i", "anullsrc=r=48000:cl=stereo",
             "-t", "0.2"]),
           ("lavfi_post_frag",
            ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "0.2",
             "-fragment_size", "2048"]),
           ("lavfi_pre_frag",
            ["-f", "lavfi", "-fragment_size", "2048", "-i", "anullsrc=r=48000:cl=stereo",
             "-t", "0.2"]),
           ("lavfi_post_frame_size",
            ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "0.2",
             "-frame_size", "1024"]),
           ("lavfi_post_channels",
            ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "0.2",
             "-channels", "1"]),
           ("lavfi_bogus_post",
            ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "0.2",
             "-bogus_xyz", "1"]),
           ("lavfi_bogus_pre",
            ["-f", "lavfi", "-bogus_xyz", "1", "-i", "anullsrc=r=48000:cl=stereo",
             "-t", "0.2"])]
    for leg, args in lav:
        d = leg_dir("c3", leg)
        o = d / "out.wav"
        o.unlink(missing_ok=True)
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
               "-y"] + args + [str(o)]
        rc, out, err, wall = sh(cmd, timeout=8.0)
        legs.append(save_leg("c3", leg, cmd, rc, out, err, wall,
                             {"wav": wav_shape(o)}, files={"out": o}))
        print(f"c3 {leg:26s} rc={rc} wav={wav_shape(o).get('rate')}x"
              f"{wav_shape(o).get('ch')} err={err.strip()[:80]!r}", flush=True)
    save_stage("c3", {"ns_idx": idx, "how": how, "inventory": inv, "legs": legs})


# ---------------------------------------------------------------- C4
class LinkPoller(threading.Thread):
    def __init__(self, node_name, t0, period=0.035):
        super().__init__(daemon=True)
        self.node_name = node_name
        self.t0 = t0
        self.period = period
        self.stop_ev = threading.Event()
        self.samples = []

    def run(self):
        rx = re.compile(re.escape(self.node_name))
        while not self.stop_ev.is_set():
            t = round(time.monotonic() - self.t0, 3)
            snap = pw_snapshot(name_rx=re.escape(self.node_name))
            peers = sorted({(l["in"].split(":")[0] if rx.search(l["out"])
                             else l["out"].split(":")[0])
                            for l in snap["links"]})
            self.samples.append((t, peers))
            self.stop_ev.wait(self.period)

    def changes(self):
        out = []
        prev = None
        for t, peers in self.samples:
            if peers != prev:
                out.append({"t": t, "peers": peers})
                prev = peers
        return out


def _run_c4_play(rep, load_hogs):
    idx, how = ensure_ns()
    d = leg_dir("c4", f"play_r{rep}")
    wit = d / "wit_def.wav"
    wit.unlink(missing_ok=True)
    player = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
              "-re", "-f", "wav", "-i", str(TONE6), "-f", "pulse",
              "-name", f"{TAG}_lossplay", "-device", NS, f"{TAG}-lossplay"]
    w, wfh = _bg_witness("c4def", f"{SPDIF}.monitor", 7.2, wit)
    time.sleep(0.3)
    t0 = time.monotonic()
    p = subprocess.Popen([os.fsencode(x) if isinstance(x, str) else x for x in player],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         preexec_fn=_nocore)
    poller = LinkPoller(f"{TAG}_lossplay", t0)
    poller.start()
    time.sleep(2.0)
    t_unload = round(time.monotonic() - t0, 3)
    ul = unload_ns(idx)
    try:
        out_b, err_b = p.communicate(timeout=10.0)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        p.kill()
        out_b, err_b = p.communicate()
        rc = None
    poller.stop_ev.set()
    poller.join(timeout=2)
    try:
        w.wait(timeout=8.0)
    except subprocess.TimeoutExpired:
        w.kill()
    wfh.close()
    extra = {"rep": rep, "unload_t": t_unload, "unload": ul,
             "rc": rc, "timeline": poller.changes(),
             "tone_windows": tone_windows(wit, 0.25),
             "load_hogs": load_hogs,
             "loadavg_after": Path("/proc/loadavg").read_text().strip()}
    meta = save_leg("c4", f"play_r{rep}", player, rc,
                    out_b.decode("utf-8", "replace"),
                    err_b.decode("utf-8", "replace"), t_unload, extra,
                    files={"wit_def": wit})
    print(f"c4 play r{rep} rc={rc} unload@{t_unload} timeline={poller.changes()} "
          f"tonewins={extra['tone_windows']}", flush=True)
    return meta


def _run_c4_capture(rep, load_hogs):
    idx, how = ensure_ns()
    d = leg_dir("c4", f"cap_r{rep}")
    capw = d / "cap.wav"
    capw.unlink(missing_ok=True)
    pump = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
            "-re", "-f", "wav", "-i", str(TONE7), "-f", "pulse",
            "-name", f"{TAG}_losspump", "-device", NS, f"{TAG}-losspump"]
    capt = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin", "-y",
            "-f", "pulse", "-name", f"{TAG}_losscap", "-i", f"{NS}.monitor",
            "-t", "7.0", "-c:a", "pcm_s16le", str(capw)]
    pp = subprocess.Popen([os.fsencode(x) if isinstance(x, str) else x for x in pump],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          preexec_fn=_nocore)
    time.sleep(0.3)
    t0 = time.monotonic()
    cp = subprocess.Popen([os.fsencode(x) if isinstance(x, str) else x for x in capt],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          preexec_fn=_nocore)
    poller = LinkPoller(f"{TAG}_losscap", t0)
    poller2 = LinkPoller(f"{TAG}_losspump", t0)
    poller.start()
    poller2.start()
    time.sleep(2.0)
    t_unload = round(time.monotonic() - t0, 3)
    ul = unload_ns(idx)
    try:
        c_out, c_err = cp.communicate(timeout=12.0)
        crc = cp.returncode
    except subprocess.TimeoutExpired:
        cp.kill()
        c_out, c_err = cp.communicate()
        crc = None
    try:
        p_out, p_err = pp.communicate(timeout=6.0)
        prc = pp.returncode
    except subprocess.TimeoutExpired:
        pp.kill()
        p_out, p_err = pp.communicate()
        prc = None
    for poller_ in (poller, poller2):
        poller_.stop_ev.set()
        poller_.join(timeout=2)
    extra = {"rep": rep, "unload_t": t_unload, "unload": ul,
             "cap_rc": crc, "pump_rc": prc,
             "cap_timeline": poller.changes(),
             "pump_timeline": poller2.changes(),
             "tone_windows": tone_windows(capw, 0.25),
             "cap_wav": wav_shape(capw),
             "load_hogs": load_hogs,
             "loadavg_after": Path("/proc/loadavg").read_text().strip()}
    meta = save_leg("c4", f"cap_r{rep}", capt, crc,
                    c_out.decode("utf-8", "replace"),
                    c_err.decode("utf-8", "replace"), t_unload, extra,
                    files={"cap": capw})
    print(f"c4 cap r{rep} crc={crc} unload@{t_unload}\n   cap={extra['cap_timeline']}\n"
          f"   pump={extra['pump_timeline']}\n   wins={extra['tone_windows']}", flush=True)
    return meta


def _hogs(n):
    ps = []
    for _ in range(n):
        ps.append(subprocess.Popen(["yes"], stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL,
                                   preexec_fn=_nocore))
    return ps


def stage_c4():
    legs = []
    print("== c4 playback: 3 quiet reps", flush=True)
    for r in range(3):
        legs.append(_run_c4_play(r, 0))
    print("== c4 playback: 3 reps under 8 CPU hogs", flush=True)
    hogs = _hogs(8)
    try:
        for r in range(3, 6):
            legs.append(_run_c4_play(r, 8))
    finally:
        for h in hogs:
            h.kill()
        for h in hogs:
            h.wait()
    print("== c4 capture: 3 quiet reps", flush=True)
    for r in range(3):
        legs.append(_run_c4_capture(r, 0))
    print("== c4 capture: 2 reps under 8 CPU hogs", flush=True)
    hogs = _hogs(8)
    try:
        for r in range(3, 5):
            legs.append(_run_c4_capture(r, 8))
    finally:
        for h in hogs:
            h.kill()
        for h in hogs:
            h.wait()
    save_stage("c4", {"legs": legs,
                      "loadavg_end": Path("/proc/loadavg").read_text().strip()})


# ---------------------------------------------------------------- C5
def stage_c5():
    idx, how = ensure_ns()
    ensure_tones()
    inv = inventory()
    legs = []
    cases = [
        ("pulse_sink_set", {"SDL_AUDIODRIVER": "pulseaudio",
                            "PULSE_SINK": NS}, 3),
        ("pulse_sink_unset", {"SDL_AUDIODRIVER": "pulseaudio"}, 2),
        ("native_default", {}, 1),
    ]
    for leg, envset, reps in cases:
        for r in range(reps):
            d = leg_dir("c5", f"{leg}_r{r}")
            wit_def = d / "wit_def.wav"
            wit_ns = d / "wit_ns.wav"
            for f in (wit_def, wit_ns):
                f.unlink(missing_ok=True)
            w1, f1 = _bg_witness("def", f"{SPDIF}.monitor", 3.4, wit_def)
            w2, f2 = _bg_witness("ns", f"{NS}.monitor", 3.4, wit_ns)
            time.sleep(0.25)
            env = dict(os.environ)
            env.update(envset)
            cmd = ["ffplay", "-hide_banner", "-loglevel", "warning",
                   "-nodisp", "-autoexit", str(TONE2)]
            t0 = time.monotonic()
            p = subprocess.Popen([os.fsencode(x) for x in cmd],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 env={k: os.fsencode(v) for k, v in env.items()},
                                 preexec_fn=_nocore)
            time.sleep(0.9)
            snap = pw_snapshot(pid=p.pid)
            try:
                out_b, err_b = p.communicate(timeout=8.0)
                rc = p.returncode
            except subprocess.TimeoutExpired:
                p.kill()
                out_b, err_b = p.communicate()
                rc = None
            wall = round(time.monotonic() - t0, 3)
            for w, fh in ((w1, f1), (w2, f2)):
                try:
                    w.wait(timeout=6.0)
                except subprocess.TimeoutExpired:
                    w.kill()
                fh.close()
            extra = {"env": envset, "rep": r, "rc": rc,
                     "nodes": [{"name": n["name"], "media.name": n["media.name"],
                                "target.object": n["props"].get("target.object"),
                                "client.api": n["props"].get("client.api"),
                                "latency": n["props"].get("node.latency"),
                                "tlength": n["props"].get("pulse.attr.tlength")}
                               for n in snap["nodes"]],
                     "links": [f"{l['out']} -> {l['in']}" for l in snap["links"]],
                     "wit_def_tone_windows": tone_windows(wit_def, 0.5),
                     "wit_ns_tone_windows": tone_windows(wit_ns, 0.5)}
            legs.append(save_leg("c5", f"{leg}_r{r}", cmd, rc,
                                 out_b.decode("utf-8", "replace"),
                                 err_b.decode("utf-8", "replace"), wall, extra,
                                 files={"wit_def": wit_def, "wit_ns": wit_ns}))
            print(f"c5 {leg} r{r} rc={rc} nodes={[(n['name'], n['target.object']) for n in extra['nodes']]} "
                  f"def={extra['wit_def_tone_windows'][:3]} ns={extra['wit_ns_tone_windows'][:3]}",
                  flush=True)
    save_stage("c5", {"ns_idx": idx, "how": how, "inventory": inv, "legs": legs})


# ---------------------------------------------------------------- C6
def stage_c6():
    idx, how = ensure_ns()
    inv = inventory()
    legs = []
    o = TMP / "c6_out.wav"
    M = f"{NS}.monitor"

    def one(leg, args, timeout=8.0):
        o.unlink(missing_ok=True)
        cmd = [FFMPEG, "-hide_banner", "-loglevel", "warning", "-nostdin",
               "-y"] + args + [str(o)]
        rc, out, err, wall = sh(cmd, timeout=timeout)
        shp = wav_shape(o)
        legs.append(save_leg("c6", leg, cmd, rc, out, err, wall,
                             {"wav": shp}, files={"out": o}))
        print(f"c6 {leg:30s} rc={rc} wall={wall} rate={shp.get('rate')} "
              f"ch={shp.get('ch')} err={err.strip().splitlines()[:1]}", flush=True)

    # ALSA clamp family
    for v in ("12345", "44100", "8000", "1", "96000", "999999", "0", "-1"):
        one(f"alsa_rate_{v}", ["-f", "alsa", "-i", "hw:0,0", "-sample_rate", v,
                               "-t", "1"])
    # pulse rate family (contrast)
    for v in ("12345", "0"):
        one(f"pulse_rate_{v}", ["-f", "pulse", "-sample_rate", v, "-i", M,
                                "-t", "1"])
    # channels / fragment families
    one("pulse_ch_0", ["-f", "pulse", "-channels", "0", "-i", M, "-t", "1"])
    one("pulse_ch_99", ["-f", "pulse", "-channels", "99", "-i", M, "-t", "1"])
    one("pulse_frag_-2", ["-f", "pulse", "-fragment_size", "-2", "-i", M,
                          "-t", "1"])
    one("pulse_rate_999999", ["-f", "pulse", "-sample_rate", "999999", "-i", M,
                              "-t", "1"])
    one("alsa_ch_0", ["-f", "alsa", "-channels", "0", "-i", "hw:0,0",
                      "-t", "1"])
    save_stage("c6", {"ns_idx": idx, "how": how, "inventory": inv, "legs": legs})


# ---------------------------------------------------------------- teardown
def stage_teardown():
    st = load_state()
    res = {"ns_idx": st.get("ns_idx")}
    if st.get("ns_idx"):
        res["unload"] = unload_ns(st["ns_idx"])
    else:
        # nothing recorded; if a sink with our name exists, refuse (never
        # unload by name) and report.
        res["unload"] = {"skipped": True,
                         "sink_present": f"{NS}.monitor" in sinks_short()}
    # kill any stray r82bnd ffmpeg/ffplay/arecord (never foreign)
    rc, out, _, _ = sh(["pgrep", "-af", "ffmpeg|ffplay|arecord|parec"], timeout=10)
    mine = [l for l in out.splitlines() if TAG in l and "r82bnd_probe" not in l]
    killed = []
    for line in mine:
        pid = int(line.split()[0])
        try:
            os.kill(pid, 15)
            killed.append(line)
        except ProcessLookupError:
            pass
    time.sleep(0.5)
    res["stray_killed"] = killed
    res["post"] = inventory()
    save_stage("teardown", res)
    print(json.dumps(res, indent=1)[:2000])


# ---------------------------------------------------------------- manifest
def stage_manifest():
    entries = []
    for p in sorted(OUT.rglob("*")):
        if p.is_dir() or p.name == "manifest.json" or "__pycache__" in p.parts:
            continue
        entries.append({"path": str(p.relative_to(OUT)), "bytes": p.stat().st_size,
                        "sha16": sha16(p)})
    man = {"generated": time.strftime("%FT%TZ", time.gmtime()),
           "host": os.uname().nodename,
           "ffmpeg": sh(["ffmpeg", "-version"])[1].splitlines()[:1],
           "pactl_server": [l for l in sh(["pactl", "info"])[1].splitlines()
                            if l.startswith(("Server Name", "Default Sink",
                                             "Default Source"))],
           "files": entries, "n_files": len(entries)}
    (OUT / "manifest.json").write_text(json.dumps(man, indent=1))
    print(f"manifest: {len(entries)} files")


STAGES = {"setup": stage_setup, "c1": stage_c1, "c2": stage_c2, "c3": stage_c3,
          "c4": stage_c4, "c5": stage_c5, "c6": stage_c6,
          "teardown": stage_teardown, "manifest": stage_manifest}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=sorted(STAGES))
    a = ap.parse_args()
    STAGES[a.stage]()
