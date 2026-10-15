#!/usr/bin/env python3
"""GST-SCOUT harness (round 77) — GStreamer capture/playback surface, measured.

Seat scope: corpus/live/gst-scout/ ONLY. No tracked file is read for behavior
and none is written; corpus/fixtures is never imported.

Every gst-launch leg is byte-capped three ways: (a) num-buffers where the
element has it, (b) a wall-clock watchdog that severs the pipeline, (c) a
byte watchdog that SIGKILLs the pipeline when the output file crosses a hard
ceiling (the honest cap for an unbounded free-running source).

Receipts: probe-<stage>-r77.json in this directory. Scratch under scratch/.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import struct
import subprocess
import sys
import threading
import time
import wave
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
SCRATCH = OUT / "scratch"
BYTE_CAP = 16 * 1024 * 1024          # hard ceiling for any single artifact
WALL_CAP_S = 20.0                    # hard ceiling for any single leg
ANSI = re.compile(r"\x1b\[[0-9;]*m")

# r77 host inventory (measured below, not assumed)
SINK_SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
SINK_SPEAKER = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"
SRC_LINE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
NULL_SINK = "gstscout_null"


# ---------------------------------------------------------------- utilities
def sha16(path):
    path = Path(path)
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def wav_inspect(path):
    """Header shape in the r77 vocabulary, extended with the gst family."""
    path = Path(path)
    out = {"exists": path.exists(), "bytes": None, "riff_sz": None,
           "riff_class": None, "fmt_tag": None, "channels": None, "rate": None,
           "bits": None, "data_off": None, "data_field": None,
           "data_class": None, "frames_declared": None, "finalized": None,
           "err": None}
    if not path.exists():
        return out
    size = path.stat().st_size
    out["bytes"] = size
    if size < 44:
        out["riff_class"] = "short"
        return out
    try:
        head = path.open("rb").read(4096)
    except OSError as exc:                                   # pragma: no cover
        out["err"] = repr(exc)
        return out
    if head[:4] != b"RIFF" or head[8:12] != b"WAVE":
        out["riff_class"] = "not_wav"
        return out
    riff_sz = struct.unpack("<I", head[4:8])[0]
    out["riff_sz"] = riff_sz
    out["riff_class"] = (
        "finalized" if riff_sz == size - 8 else
        "placeholder_8" if riff_sz == 8 else
        "zero" if riff_sz == 0 else
        "placeholder_ff" if riff_sz == 0xFFFFFFFF else
        "placeholder_80000000" if riff_sz == 0x80000000 else
        "placeholder_7ffff000" if riff_sz == 0x7FFFF000 else
        "wavenc_streaming" if riff_sz == 0x7FFF0024 else
        "other")
    out["streaming_placeholder"] = riff_sz == 0x7FFF0024
    fmt_tag = struct.unpack("<H", head[20:22])[0]
    out["fmt_tag"] = fmt_tag
    out["channels"] = struct.unpack("<H", head[22:24])[0]
    out["rate"] = struct.unpack("<I", head[24:28])[0]
    out["bits"] = struct.unpack("<H", head[34:36])[0]
    out["chunks"] = []
    out["fmt_size"] = struct.unpack("<I", head[16:20])[0]
    if out["fmt_size"] >= 18:
        out["cb_size"] = struct.unpack("<H", head[36:38])[0]
    if out["fmt_size"] >= 40:
        out["valid_bits"] = struct.unpack("<H", head[38:40])[0]
        out["channel_mask"] = struct.unpack("<I", head[40:44])[0]
    off = 12
    while off + 8 <= min(len(head), size):
        cid = head[off:off + 4]
        csz = struct.unpack("<I", head[off + 4:off + 8])[0]
        out["chunks"].append(cid.decode("latin1") + ":" + str(csz))
        if cid == b"data":
            out["data_off"] = off + 8
            out["data_field"] = csz
            out["data_class"] = (
                "finalized" if csz == size - (off + 8) else
                "placeholder_8" if csz == 8 else
                "zero" if csz == 0 else
                "placeholder_ff" if csz == 0xFFFFFFFF else
                "placeholder_80000000" if csz == 0x80000000 else
                "placeholder_7ffff000" if csz == 0x7FFFF000 else
                "wavenc_streaming" if csz == 0x7FFFF000 else "other")
            ch = out["channels"] or 1
            bits = out["bits"] or 8
            frame = max(1, ch * (bits // 8))
            out["frames_declared"] = csz // frame
            break
        off += 8 + csz + (csz & 1)
    out["finalized"] = out["riff_class"] == "finalized"
    return out


def pcm_stats(path, insp):
    path = Path(path)
    if not insp.get("exists") or not insp.get("data_off"):
        return {"peak": None, "rms": None, "nonzero_frac": None, "err": None}
    try:
        with wave.open(str(path), "rb") as w:
            n = w.getnframes()
            raw = w.readframes(min(n, 48000))
    except Exception as exc:
        return {"peak": None, "rms": None, "nonzero_frac": None,
                "err": type(exc).__name__}
    if not raw:
        return {"peak": 0, "rms": 0.0, "nonzero_frac": 0.0, "err": None}
    a = np.frombuffer(raw, dtype="<i2").astype(np.float64)
    return {"peak": int(np.abs(a).max()), "rms": float(np.sqrt((a ** 2).mean())),
            "nonzero_frac": float((a != 0).mean()), "err": None}


def pcm_stats_raw(path, insp):
    """Content witness that works for every fmt tag (incl. F32/F64/extensible).

    stdlib wave refuses non-PCM and float WAVs, so a float capture has NO
    content witness without this path — and byte-identity between two silent
    float captures is then not evidence of anything (r77 §1.3 trap).
    """
    path = Path(path)
    if not insp.get("exists") or not insp.get("data_off"):
        return {"peak": None, "rms": None, "nonzero_frac": None, "err": "no_data"}
    bits = insp.get("bits") or 16
    tag = insp.get("fmt_tag")
    ch = insp.get("channels") or 1
    n = min(insp.get("bytes", 0) - insp["data_off"], 2 << 20)
    n -= n % max(1, ch * (bits // 8))
    if n <= 0:
        return {"peak": 0, "rms": 0.0, "nonzero_frac": 0.0, "err": None}
    try:
        with path.open("rb") as fh:
            fh.seek(insp["data_off"])
            raw = fh.read(n)
    except OSError as exc:
        return {"peak": None, "rms": None, "nonzero_frac": None, "err": repr(exc)[:60]}
    dtype = ("<f4" if bits == 32 else "<f8" if bits == 64 else
             "<u1" if bits == 8 else "<i2" if bits == 16 else
             "<i4" if bits == 32 else "<i2")
    if bits == 24:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        a = (b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16))
        a = np.where(a >= 0x800000, a - 0x1000000, a).astype(np.float64)
    else:
        a = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    scale = 32768.0 if tag == 3 else (128.0 if bits == 8 else 1.0)
    return {"peak": float(np.abs(a).max()), "rms": float(np.sqrt((a ** 2).mean())),
            "nonzero_frac": float((a != 0).mean()), "err": None,
            "decoded_as": ("float" if tag == 3 else "int") + "%d" % bits,
            "scale": scale}


def readers(path, insp):
    """Five witnesses, r77 vocabulary. Honest abstention is recorded as None."""
    path = Path(path)
    out = {"soxi_s": None, "soxi_D": None, "soxi_precision": None,
           "soxi_warn": None, "wave_frames": None,
           "wave_ok": False, "wave_err": None, "sndfile_frames": None,
           "sndfile_ok": False, "sndfile_err": None, "ffprobe_duration": None,
           "ffprobe_codec": None, "ffprobe_error": None}
    if not insp.get("exists"):
        return out
    try:
        with wave.open(str(path), "rb") as w:
            out["wave_frames"] = w.getnframes()
            out["wave_ok"] = True
    except Exception as exc:
        out["wave_err"] = type(exc).__name__ + ": " + str(exc)[:60]
    try:
        r = subprocess.run(("soxi", str(path)), capture_output=True, text=True,
                           timeout=20)
        m = re.search(r"^Precision\s+:\s+(.+)$", r.stdout, re.M)
        out["soxi_precision"] = m.group(1).strip() if m else None
        m = re.search(r"^soxi WARN.*$", r.stdout + r.stderr, re.M)
        out["soxi_warn"] = m.group(0).strip()[:80] if m else None
    except Exception as exc:                                 # pragma: no cover
        out["soxi_precision"] = "exc:" + type(exc).__name__
    for key, args in (("soxi_s", ("soxi", "-s", str(path))),
                      ("soxi_D", ("soxi", "-D", str(path)))):
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=20)
            out[key] = r.stdout.strip() if r.returncode == 0 else \
                "rc=%d" % r.returncode
        except Exception as exc:                             # pragma: no cover
            out[key] = "exc:" + type(exc).__name__
    try:
        r = subprocess.run(("sndfile-info", str(path)), capture_output=True,
                           text=True, timeout=20)
        txt = r.stdout + r.stderr
        m = re.search(r"^Frames\s+:\s+(\d+)", txt, re.M)
        if m:
            out["sndfile_frames"] = int(m.group(1))
            out["sndfile_ok"] = True
        else:
            out["sndfile_err"] = (re.search(r"^Error.*", txt, re.M) or
                                  re.search(r"^.*error.*", txt, re.M))
            out["sndfile_err"] = (out["sndfile_err"].group(0).strip()[:80]
                                  if out["sndfile_err"] else "no_frames_line")
    except Exception as exc:                                 # pragma: no cover
        out["sndfile_err"] = "exc:" + type(exc).__name__
    try:
        r = subprocess.run(
            ("ffprobe", "-v", "error", "-show_entries",
             "format=duration:stream=codec_name", "-of", "json", str(path)),
            capture_output=True, text=True, timeout=20)
        if r.returncode == 0 and r.stdout.strip():
            doc = json.loads(r.stdout)
            fmt = doc.get("format", {})
            out["ffprobe_duration"] = float(fmt["duration"]) if "duration" in fmt else None
            st = doc.get("streams", [{}])
            out["ffprobe_codec"] = st[0].get("codec_name") if st else None
        else:
            out["ffprobe_error"] = (r.stderr.strip().splitlines() or ["rc=%d" % r.returncode])[-1][:80]
    except Exception as exc:                                 # pragma: no cover
        out["ffprobe_error"] = "exc:" + type(exc).__name__
    return out


def clean(path):
    path = Path(path)
    if path.exists():
        path.unlink()


def _byte_watch(path, stop, killed, cap, pgid=None):
    """Hard byte ceiling: SIGKILL the pipeline when the artifact crosses cap.

    NOTE (measured the hard way, r77): a str path here raises in the thread,
    the cap silently never arms, and a free-running source writes GBs. The
    Path() coercion and the cap argument are load-bearing.
    """
    path = Path(path)
    while not stop.is_set():
        try:
            if path.exists() and path.stat().st_size > cap:
                killed.append(path.stat().st_size)
                if pgid is not None:
                    try:
                        os.killpg(pgid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                return
        except OSError:
            pass
        stop.wait(0.01)


def run_gst(pipeline, out_path=None, sever=None, sever_after=1.5,
            wall_cap=WALL_CAP_S, eos=False, extra=(), byte_cap=BYTE_CAP):
    """Run one gst-launch leg. Returns rc/signal/stderr/elapsed/killed."""
    argv = ["gst-launch-1.0", "-q"] + (["-e"] if eos else []) + list(extra) + \
        pipeline.split()
    if out_path is not None:
        clean(out_path)
    t0 = time.monotonic()
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, text=True,
                         preexec_fn=os.setsid)
    stop = threading.Event()
    killed = []
    watch_path = out_path if out_path is not None else Path("/dev/null")
    th = threading.Thread(target=_byte_watch,
                          args=(watch_path, stop, killed, byte_cap,
                                os.getpgid(p.pid)), daemon=True)
    th.start()
    sent = None
    if sever is not None:
        deadline = t0 + sever_after
        while time.monotonic() < deadline and p.poll() is None and not killed:
            time.sleep(0.02)
        if p.poll() is None and not killed:
            try:
                os.killpg(os.getpgid(p.pid), sever)
                sent = signal.Signals(sever).name
            except ProcessLookupError:
                sent = "already_gone"
    try:
        while True:
            if p.poll() is not None:
                break
            if killed:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                sent = (sent + "+bytecap_kill") if sent else "bytecap_kill"
                p.wait(timeout=5)
                break
            if time.monotonic() - t0 > wall_cap:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                sent = (sent + "+wallcap_kill") if sent else "wallcap_kill"
                p.wait(timeout=5)
                break
            time.sleep(0.02)
    finally:
        stop.set()
        th.join(timeout=1)
    err = ANSI.sub("", p.stderr.read() or "")
    rc = p.returncode
    sig = None
    if rc is not None and rc < 0:
        sig = signal.Signals(-rc).name
    return {"pipeline": pipeline, "argv": argv, "rc": rc, "signal": sig,
            "sent": sent, "eos": eos, "elapsed_s": round(time.monotonic() - t0, 3),
            "stderr": err, "stderr_head": err.strip().splitlines()[:1],
            "byte_cap_killed_at": killed[0] if killed else None,
            "out": str(out_path) if out_path else None}


def first_error(text):
    for line in text.splitlines():
        if line.startswith("ERROR") or "ERROR" in line[:40]:
            return line.strip()[:160]
    return (text.strip().splitlines() or [""])[0][:160]


def err_class(text):
    """Named refusal classes for gst-launch stderr (most specific first)."""
    pats = (
        ("no_element", r"No such element or plugin '([^']+)'"),
        ("could_not_link", r"could not link ([^\n]+)"),
        ("internal_link_error", r"Internal data stream error"),
        ("not_negotiated", r"not-negotiated"),
        ("state_change_failed", r"Failed to set pipeline to PAUSED"),
        ("target_not_found", r"stream error: target not found"),
        ("device_open_failed", r"Could not open audio device"),
        ("device_busy", r"Device or resource busy"),
        ("no_such_file", r"No such file or directory"),
        ("not_writable", r"Permission denied|Read-only file system"),
        ("parse_error", r"could not parse|Erroneous pipeline|syntax error|no property"),
        ("write_error", r"writing to file|No space left"),
    )
    for name, pat in pats:
        m = re.search(pat, text)
        if m:
            return name, m.group(0).strip()[:120]
    return None, None


def receipt(stage, body):
    doc = {"probe": stage, "host": os.uname().nodename,
           "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "toolchain": toolchain(),
           "byte_cap_bytes": BYTE_CAP, "wall_cap_s": WALL_CAP_S,
           "scratch_bytes_before": dir_bytes(SCRATCH),
           "body": body}
    p = OUT / ("probe-%s-r77.json" % stage)
    p.write_text(json.dumps(doc, indent=1, sort_keys=False))
    print("[receipt] %s  %d bytes" % (p.name, p.stat().st_size))
    return p


def dir_bytes(p):
    if not p.exists():
        return 0
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def toolchain():
    def one(*a):
        try:
            r = subprocess.run(a, capture_output=True, text=True, timeout=15)
            return (r.stdout + r.stderr).strip().splitlines()[0]
        except Exception:
            return None
    return {"gst_launch": one("gst-launch-1.0", "--version"),
            "gst_inspect": one("gst-inspect-1.0", "--version"),
            "pw_version": one("pw-cli", "info", "0"),
            "ffprobe": one("ffprobe", "-version"),
            "soxi": one("soxi", "--version"),
            "sndfile": one("sndfile-info", "--version"),
            "python": sys.version.split()[0],
            "numpy": np.__version__}


# ------------------------------------------------------------------ stage 1
def _inspect_element(name):
    """gst-inspect-1.0 <element> -> klass/pads/props, or absent."""
    r = subprocess.run(("gst-inspect-1.0", name), capture_output=True, text=True,
                       timeout=30)
    txt = r.stdout
    if r.returncode != 0 or "Factory Details" not in txt:
        return {"present": False}
    def field(label):
        m = re.search(r"^\s*%s\s+(.+)$" % label, txt, re.M)
        return m.group(1).strip() if m else None
    klasses = re.findall(r"^\s*Klass\s+(.+)$", txt, re.M)
    pads = re.findall(r"^\s*(\S+):\s+(Always|Sometimes|On request)", txt, re.M)
    return {"present": True, "klass": klasses[-1] if klasses else None,
            "long_name": field("Long-name"), "author": field("Author"),
            "src_pads": len(re.findall(r"SRC template: '([^']+)'", txt)),
            "sink_pads": len(re.findall(r"SINK template: '([^']+)'", txt)),
            "props": len(re.findall(r"^\s+[a-z][a-z0-9-]*\s+:", txt, re.M))}


def stage_inventory():
    r = subprocess.run(("gst-inspect-1.0",), capture_output=True, text=True,
                       timeout=120)
    # `gst-inspect-1.0` with no args prints "<plugin>:  <factory>: <desc>"
    feats, plugin_of = {}, {}
    for l in r.stdout.splitlines():
        if ":  " not in l or l.startswith(" "):
            continue
        plugin, _, rest = l.partition(":  ")
        factory, _, desc = rest.partition(": ")
        feats[factory.strip()] = desc.strip()
        plugin_of[factory.strip()] = plugin.strip()
    r2 = subprocess.run(("gst-inspect-1.0", "-b"), capture_output=True, text=True,
                        timeout=120)
    blacklisted = [l.strip() for l in r2.stdout.splitlines() if l.strip()]
    candidates = [
        # the brief's named families
        "pulsesrc", "pulsesink", "pipewiresrc", "pipewiresink", "alsasrc",
        "alsasink", "autoaudiosrc", "autoaudiosink", "filesrc", "filesink",
        "wavparse", "wavenc", "flacdec", "flacenc", "audiotestsrc",
        # parsing / container / codec families
        "auparse", "wavpackparse", "wavpackdec", "wavpackenc", "id3demux",
        "icydemux", "oggdemux", "vorbisdec", "vorbisenc", "opusdec", "opusenc",
        "mpg123audiodec", "lame", "lamemp3enc", "twolamemp2enc", "mad",
        "mpegaudioparse", "sbcdec", "sbcenc", "speexdec", "speexenc",
        "adpcmdec", "adpcmenc", "mulawdec", "mulawenc", "alawdec", "alawenc",
        "dsddec", "avdec_mp3", "avdec_aac", "avdec_flac", "avdec_vorbis",
        "avenc_aac", "avenc_mp3", "avenc_ac3",
        # plumbing / control
        "audioconvert", "audioresample", "audiorate", "audiomixer", "adder",
        "volume", "level", "spectrum", "removesilence", "audiobuffersplit",
        "capsfilter", "queue", "fakesink", "fakesrc", "appsink", "appsrc",
        "identity", "tee", "filesrc",
        # transport / network / other backends
        "souphttpsrc", "uridecodebin", "playbin", "decodebin", "giostreamsrc",
        "jackaudiosrc", "jackaudiosink", "oss4src", "oss4sink", "osssrc",
        "osssink", "openalsrc", "directsoundsrc", "sfsrc", "rfsrc",
        "shmsrc", "shmsink", "unixfdsrc", "unixfdsink", "udpsrc",
        "audiotestsrc", "videotestsrc", "osxaudiosrc", "sndiosrc",
    ]
    census = {}
    for c in sorted(set(candidates)):
        census[c] = _inspect_element(c)
    audio = {k: v for k, v in feats.items()
             if re.search(r"audio|sound|pcm|codec", v, re.I)}
    body = {"feature_count": len(feats),
            "plugin_count": len({v for v in plugin_of.values()}),
            "blacklisted": blacklisted,
            "census": census,
            "census_present": sorted(k for k, v in census.items() if v["present"]),
            "census_absent": sorted(k for k, v in census.items() if not v["present"]),
            "audioish_features": audio,
            "audioish_count": len(audio)}
    return body


# ------------------------------------------------------------------ stage 2
WAVES = ["sine", "square", "saw", "triangle", "silence", "white-noise",
         "pink-noise", "sine-table", "ticks", "gaussian-noise", "red-noise",
         "blue-noise", "violet-noise"]


def stage_control():
    body = {}
    leg = str(SCRATCH / "ctl_%s.wav")
    # 2.1 known-good loop, num-buffers as the honest bound
    for nb in (1, 100):
        out = leg % ("nb%d" % nb)
        run = run_gst("audiotestsrc wave=sine freq=1000 num-buffers=%d ! "
                      "audio/x-raw,format=S16LE,rate=48000,channels=2 ! "
                      "wavenc ! filesink location=%s" % (nb, out), out)
        insp = wav_inspect(Path(out))
        body["known_good_nb%d" % nb] = {"run": run, "insp": insp,
                                        "stats": pcm_stats(out, insp),
                                        "sha16": sha16(out)}
    # 2.2 unbounded free-run under three bounds (num-buffers / wall / byte)
    out = leg % "unbounded_wall"
    run = run_gst("audiotestsrc wave=sine freq=1000 ! wavenc ! filesink "
                  "location=%s" % out, out, wall_cap=2.0, byte_cap=8 << 20)
    body["unbounded_wall2s"] = {"run": run, "insp": wav_inspect(out),
                                "readers": readers(out, wav_inspect(out)),
                                "sha16": sha16(out)}
    out = leg % "unbounded_sync_wall"
    run = run_gst("audiotestsrc wave=sine freq=1000 ! wavenc ! filesink sync=true "
                  "location=%s" % out, out, sever=signal.SIGTERM, sever_after=1.5,
                  wall_cap=10.0, byte_cap=8 << 20)
    body["unbounded_sync_TERM1.5s"] = {"run": run, "insp": wav_inspect(out),
                                       "readers": readers(out, wav_inspect(out)),
                                       "sha16": sha16(out)}
    out = leg % "unbounded_bytecap"
    run = run_gst("audiotestsrc wave=sine freq=1000 ! wavenc ! filesink "
                  "location=%s" % out, out, wall_cap=20.0, byte_cap=8 << 20)
    body["unbounded_bytecap8MiB"] = {"run": run, "insp": wav_inspect(out),
                                     "readers": readers(out, wav_inspect(out)),
                                     "sha16": sha16(out)}
    # 2.3 wave axis (content witness per waveform)
    body["waves"] = {}
    for w in WAVES:
        out = SCRATCH / ("wave_%s.wav" % w.replace("-", "_"))
        run = run_gst("audiotestsrc wave=%s freq=1000 volume=0.5 num-buffers=25 ! "
                      "audio/x-raw,format=S16LE,rate=48000,channels=1 ! "
                      "wavenc ! filesink location=%s" % (w, out), out)
        insp = wav_inspect(Path(out))
        body["waves"][w] = {"rc": run["rc"], "stderr_head": run["stderr_head"],
                            "bytes": insp["bytes"], "insp": insp,
                            "stats": pcm_stats(out, insp), "sha16": sha16(out)}
    # 2.4 freq / volume axis
    body["freq_volume"] = {}
    for label, pipe in (
            ("freq100", "audiotestsrc wave=sine freq=100 num-buffers=25"),
            ("freq20000", "audiotestsrc wave=sine freq=20000 num-buffers=25"),
            ("freq30000_above_nyquist", "audiotestsrc wave=sine freq=30000 num-buffers=25"),
            ("freq0", "audiotestsrc wave=sine freq=0 num-buffers=25"),
            ("vol0", "audiotestsrc wave=sine freq=1000 volume=0 num-buffers=25"),
            ("vol2_clip", "audiotestsrc wave=sine freq=1000 volume=2 num-buffers=25"),
            ("vol4_clip", "audiotestsrc wave=sine freq=1000 volume=4 num-buffers=25")):
        out = SCRATCH / ("fv_%s.wav" % label)
        run = run_gst("%s ! audio/x-raw,format=S16LE,rate=48000,channels=1 ! "
                      "wavenc ! filesink location=%s" % (pipe, out), out)
        insp = wav_inspect(Path(out))
        body["freq_volume"][label] = {"rc": run["rc"], "stderr_head": run["stderr_head"],
                                      "bytes": insp["bytes"], "insp": insp,
                                      "stats": pcm_stats(out, insp), "sha16": sha16(out)}
    # 2.5 caps axis into wavenc (extensible-tag boundary, cross-check r77 §3.3)
    body["caps"] = {}
    for label, caps in (
            ("s16_48k_2ch", "audio/x-raw,format=S16LE,rate=48000,channels=2"),
            ("f32_48k_2ch", "audio/x-raw,format=F32LE,rate=48000,channels=2"),
            ("u8_48k_2ch", "audio/x-raw,format=U8,rate=48000,channels=2"),
            ("s24_48k_2ch", "audio/x-raw,format=S24LE,rate=48000,channels=2"),
            ("s32_48k_2ch", "audio/x-raw,format=S32LE,rate=48000,channels=2"),
            ("s16_96k_2ch", "audio/x-raw,format=S16LE,rate=96000,channels=2"),
            ("s16_44k1_2ch", "audio/x-raw,format=S16LE,rate=44100,channels=2"),
            ("s16_48k_1ch", "audio/x-raw,format=S16LE,rate=48000,channels=1"),
            ("s16_48k_6ch", "audio/x-raw,format=S16LE,rate=48000,channels=6"),
            ("s16_48k_3ch", "audio/x-raw,format=S16LE,rate=48000,channels=3"),
            ("f64_48k_2ch", "audio/x-raw,format=F64LE,rate=48000,channels=2")):
        out = SCRATCH / ("caps_%s.wav" % label)
        run = run_gst("audiotestsrc wave=sine freq=1000 num-buffers=25 ! %s ! "
                      "wavenc ! filesink location=%s" % (caps, out), out)
        insp = wav_inspect(Path(out))
        body["caps"][label] = {"rc": run["rc"], "stderr_head": run["stderr_head"],
                               "bytes": insp["bytes"], "insp": insp,
                               "readers": readers(out, insp), "sha16": sha16(out)}
    # 2.6 container axis: wav vs flac vs raw
    body["containers"] = {}
    for label, tail in (
            ("wav", "wavenc ! filesink location=%s"),
            ("flac", "flacenc ! filesink location=%s"),
            ("raw_s16", "filesink location=%s")):
        out = SCRATCH / ("cont_%s.bin" % label)
        run = run_gst("audiotestsrc wave=sine freq=1000 num-buffers=25 ! "
                      "audio/x-raw,format=S16LE,rate=48000,channels=2 ! %s"
                      % (tail % out), out)
        insp = wav_inspect(Path(out))
        body["containers"][label] = {
            "rc": run["rc"], "stderr_head": run["stderr_head"],
            "bytes": insp["bytes"], "riff_class": insp["riff_class"],
            "readers": readers(out, insp), "sha16": sha16(out)}
    return body


# ------------------------------------------------------------------ stage 3
def stage_errors():
    """Named refusal taxonomy: one bounded leg per error family."""
    body = {}
    legs = {
        "no_element_src": "nosuchelementsrc ! wavenc ! filesink location=%s",
        "no_element_sink": "audiotestsrc num-buffers=5 ! nosuchelementsink location=%s",
        "link_fail_wavparse": "audiotestsrc num-buffers=5 ! wavparse ! filesink location=%s",
        "no_sink_at_all": "audiotestsrc num-buffers=5 ! wavenc",
        "filesrc_missing": "filesrc location=/nonexistent/gstscout.wav ! wavparse ! wavenc ! filesink location=%s",
        "filesink_bad_dir": "audiotestsrc num-buffers=5 ! wavenc ! filesink location=/nonexistent-dir/x.wav",
        "caps_parse_bogus": "audiotestsrc num-buffers=5 ! capsfilter caps=bogus ! wavenc ! filesink location=%s",
        "caps_unsatisfiable": "audiotestsrc num-buffers=5 ! capsfilter caps=audio/x-raw,format=NOPE,rate=48000,channels=2 ! wavenc ! filesink location=%s",
        "alsasrc_bad_device": "alsasrc device=hw:99 num-buffers=5 ! wavenc ! filesink location=%s",
        "alsasrc_bad_pcm_name": "alsasrc device=no_such_pcm num-buffers=5 ! wavenc ! filesink location=%s",
        "pulsesrc_bad_device": "pulsesrc device=no_such_node_xyz num-buffers=5 ! wavenc ! filesink location=%s",
        "pipewiresrc_bad_target": "pipewiresrc target-object=no_such_node_xyz num-buffers=5 ! wavenc ! filesink location=%s",
        "pipewiresrc_no_target": "pipewiresrc num-buffers=5 ! wavenc ! filesink location=%s",
        "wavparse_from_test_src": "audiotestsrc num-buffers=5 ! wavparse ! filesink location=%s",
        "flacdec_from_test_src": "audiotestsrc num-buffers=5 ! flacdec ! filesink location=%s",
        "wavenc_bad_caps_f64": "audiotestsrc num-buffers=5 ! audio/x-raw,format=F64LE,rate=48000,channels=2 ! wavenc ! filesink location=%s",
        "dev_full": "audiotestsrc num-buffers=5 ! wavenc ! filesink location=/dev/full",
        "empty_pipeline": "",
    }
    for name, tmpl in legs.items():
        out = SCRATCH / ("err_%s.wav" % name)
        pipe = tmpl % out if "%s" in tmpl else tmpl
        run = run_gst(pipe, out if "%s" in tmpl else None, wall_cap=8.0)
        insp = wav_inspect(out) if "%s" in tmpl else None
        cls, hit = err_class(run["stderr"])
        body[name] = {"pipeline": pipe, "rc": run["rc"], "signal": run["signal"],
                      "stderr_full": run["stderr"][:800],
                      "elapsed_s": run["elapsed_s"], "err_class": cls,
                      "err_hit": hit, "stderr_head": first_error(run["stderr"]),
                      "stderr_lines": len([l for l in run["stderr"].splitlines() if l.strip()]),
                      "out": insp}
    return body


# ------------------------------------------------------------------ stage 4
def pw_targets():
    sinks, sources = [], []
    r = subprocess.run(("pactl", "list", "short", "sinks"), capture_output=True,
                       text=True, timeout=20)
    for l in r.stdout.splitlines():
        parts = l.split("\t")
        if len(parts) > 1:
            sinks.append(parts[1])
    r = subprocess.run(("pactl", "list", "short", "sources"), capture_output=True,
                       text=True, timeout=20)
    for l in r.stdout.splitlines():
        parts = l.split("\t")
        if len(parts) > 1:
            sources.append(parts[1])
    return sinks, sources


def link_producers():
    r = subprocess.run(("pw-link", "-l"), capture_output=True, text=True,
                       timeout=20)
    return r.stdout


def gst_input_producers(links, client="gst-launch-1.0"):
    """pw-link -l blocks: a port line, then its producers as '  |<- <node>:port'.

    Returns {input_port: [producer...]} — the only honest statement of which
    node a capture stream actually consumes (r77 §1.2: target.object lies).
    """
    out, cur = {}, None
    for line in links.splitlines():
        if line.startswith(" ") or line.startswith("\t"):
            if cur is not None and "|<-" in line:
                out[cur].append(line.split("|<-", 1)[1].strip())
        else:
            port = line.strip()
            cur = port if (client in port and ":input" in port) else None
            if cur:
                out.setdefault(cur, [])
    return out


def stage_lattice():
    """pipewiresrc target lattice, prop/no-prop, tone-anchored where it matters.

    Tone anchor is a NULL SINK this seat owns (gstscout_null) — no physical
    device is written, so no concurrent seat's capture can be contaminated.
    """
    sinks, sources = pw_targets()
    mon = [s for s in sinks if s == SINK_SPDIF]
    src = [s for s in sources if s == SRC_LINE]
    body = {"sinks": sinks, "sources": sources}
    # 4.0 stream-properties syntax probe (which spelling parses?)
    body["syntax"] = {}
    for label, prop in (("props_prefix", "props,stream.capture.sink=true"),
                        ("bare", "stream.capture.sink=true"),
                        ("quoted_props", '"props,stream.capture.sink=true"')):
        out = SCRATCH / ("syn_%s.wav" % label)
        run = run_gst("pipewiresrc target-object=%s stream-properties=%s "
                      "num-buffers=5 ! wavenc ! filesink location=%s"
                      % (mon[0], prop, out), out, wall_cap=8.0)
        body["syntax"][label] = {"prop": prop, "rc": run["rc"],
                                 "stderr_head": first_error(run["stderr"]),
                                 "err_class": err_class(run["stderr"])[0],
                                 "insp": wav_inspect(out)}
    # 4.1 target lattice without the prop (source semantics only)
    body["lattice_noprop"] = {}
    cells = [("sink_spdif", mon[0]), ("sink_spdif_monitor", mon[0] + ".monitor"),
             ("source_line", src[0]), ("source_line_dot_monitor", src[0] + ".monitor"),
             ("garbage", "no_such_node_xyz"), ("default", "default"),
             ("pulse", "pulse"), ("at_default_source", "@DEFAULT_SOURCE@"),
             ("at_default_monitor", "@DEFAULT_MONITOR@"), ("serial_int", "0")]
    for name, target in cells:
        out = SCRATCH / ("lat_np_%s.wav" % name)
        run = run_gst("pipewiresrc target-object=%s num-buffers=50 ! wavenc ! "
                      "filesink location=%s" % (target, out), out, wall_cap=12.0)
        insp = wav_inspect(Path(out))
        body["lattice_noprop"][name] = {
            "target": target, "rc": run["rc"], "signal": run["signal"],
            "elapsed_s": run["elapsed_s"], "err_class": err_class(run["stderr"])[0],
            "stderr_head": first_error(run["stderr"]), "insp": insp,
            "stats": pcm_stats(out, insp), "stats_raw": pcm_stats_raw(out, insp),
            "sha16": sha16(out)}
    # 4.2 with the prop (capture.sink semantics) — the pw-record comparison
    body["lattice_prop"] = {}
    for name, target in cells:
        out = SCRATCH / ("lat_p_%s.wav" % name)
        run = run_gst("pipewiresrc target-object=%s "
                      "stream-properties=props,stream.capture.sink=true "
                      "num-buffers=50 ! wavenc ! filesink location=%s"
                      % (target, out), out, wall_cap=12.0)
        insp = wav_inspect(Path(out))
        body["lattice_prop"][name] = {
            "target": target, "rc": run["rc"], "signal": run["signal"],
            "elapsed_s": run["elapsed_s"], "err_class": err_class(run["stderr"])[0],
            "stderr_head": first_error(run["stderr"]), "insp": insp,
            "stats": pcm_stats(out, insp), "stats_raw": pcm_stats_raw(out, insp),
            "sha16": sha16(out)}
    # 4.1b caps dependence of the prop's fallback
    body["caps_dependence"] = {}
    for label, tail in (
            ("audio_caps_wavenc", "audio/x-raw,format=S16LE,rate=48000,channels=2 ! wavenc ! filesink location=%s"),
            ("audio_caps_fakesink", "audio/x-raw,format=S16LE,rate=48000,channels=2 ! fakesink sync=false"),
            ("bare_fakesink", "fakesink sync=false"),
            ("video_caps_fakesink", "video/x-raw ! fakesink"),
            ("audioconvert_fakesink", "audioconvert ! fakesink sync=false")):
        out = SCRATCH / ("capsdep_%s.wav" % label)
        tail = tail % out if "%s" in tail else tail
        run = run_gst("pipewiresrc target-object=no_such_node_xyz "
                      "stream-properties=props,stream.capture.sink=true num-buffers=5 ! %s" % tail,
                      out, wall_cap=10.0)
        insp = wav_inspect(out)
        body["caps_dependence"][label] = {
            "tail": tail, "rc": run["rc"], "err_class": err_class(run["stderr"])[0],
            "stderr_head": first_error(run["stderr"]), "insp": insp,
            "frames": insp["frames_declared"], "sha16": sha16(out)}

    # 4.2b TOPOLOGY witness — the honest discriminator when content is silence
    body["topology"] = {}
    for label, target in (("prop_garbage", "no_such_node_xyz"),
                          ("prop_sink_spdif", mon[0]),
                          ("prop_source_line", src[0]),
                          ("noprop_source_line", src[0])):
        out = SCRATCH / ("topo_%s.wav" % label)
        prop = ("" if label.startswith("noprop") else
                " stream-properties=props,stream.capture.sink=true")
        # audio caps are load-bearing: with video caps (or a bare fakesink)
        # the same prop yields `target not found` (measured, §5 of the report)
        pipe = ("pipewiresrc target-object=%s%s ! audio/x-raw,format=S16LE,"
                "rate=48000,channels=2 ! wavenc ! filesink location=%s"
                % (target, prop, out))
        cap = subprocess.Popen(["gst-launch-1.0", "-q"] + pipe.split(),
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                               text=True)
        time.sleep(1.0)
        links = link_producers()
        producers = gst_input_producers(links)
        mine = [l.strip() for l in links.splitlines()
                if "gst-launch-1.0" in l and ("|->" in l or "|<-" in l)]
        cap.terminate()
        try:
            cap.wait(timeout=5)
        except subprocess.TimeoutExpired:                     # pragma: no cover
            cap.kill()
        nodes = subprocess.run(("pw-cli", "ls", "Node"), capture_output=True,
                               text=True, timeout=20).stdout
        gst_nodes = [l.strip() for l in nodes.splitlines()
                     if "gst" in l.lower()]
        body["topology"][label] = {
            "target": target, "pipe": pipe, "gst_links": mine[:12],
            "gst_nodes": gst_nodes[:6], "capture_bytes": out.stat().st_size if out.exists() else None,
            "input_producers": {k: v for k, v in list(producers.items())[:12]},
            "stderr_head": first_error(cap.stderr.read() or "")}

    # 4.3 pw-record cross-client control, same session
    body["pw_record_control"] = {}
    for name, target, prop in (("sink_spdif", mon[0], True),
                               ("source_line", src[0], True),
                               ("garbage", "no_such_node_xyz", True),
                               ("sink_spdif_noprop", mon[0], False)):
        out = SCRATCH / ("pwr_%s.wav" % name)
        argv = ["pw-record"]
        if prop:
            argv += ["-P", "stream.capture.sink=true"]
        argv += ["--target", target, "-n", "24000", "--rate", "48000",
                 "--channels", "2", "--format", "s16", str(out)]
        clean(out)
        t0 = time.monotonic()
        r = subprocess.run(argv, capture_output=True, text=True, timeout=20)
        insp = wav_inspect(Path(out))
        body["pw_record_control"][name] = {
            "argv": argv, "rc": r.returncode, "elapsed_s": round(time.monotonic() - t0, 3),
            "stderr_head": (r.stderr.strip().splitlines() or [""])[0][:120],
            "insp": insp, "stats": pcm_stats(out, insp), "sha16": sha16(out)}
    return body


# ------------------------------------------------------------------ stage 5
def stage_sever():
    """TERM/INT/KILL on a running gst pipeline, +/- `-e` (EOS-on-shutdown)."""
    body = {}
    combos = []
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGKILL):
        for eos in (False, True):
            combos.append((sig, eos))
    # testsrc legs carry filesink sync=true: a free-running source would cross
    # the byte cap in ~0.03 s and the requested sever would never be delivered
    # (measured: the first pass recorded bytecap_kill at 0.142 s, not the
    # signal). Real-time rate makes the sever the bound under test.
    for src, tail in (("audiotestsrc wave=sine freq=1000", "filesink sync=true location=%s"),
                      ("pipewiresrc target-object=%s stream-properties=props,stream.capture.sink=true" % SINK_SPDIF, "filesink location=%s")):
        tag = "testsrc" if src.startswith("audiotestsrc") else "pipewiresrc"
        body[tag] = {}
        for sig, eos in combos:
            key = "%s%s" % (signal.Signals(sig).name, "_eos" if eos else "")
            out = SCRATCH / ("sev_%s_%s.wav" % (tag, key))
            pipe = "%s ! audio/x-raw,format=S16LE,rate=48000,channels=2 ! wavenc ! %s" % (src, tail % out)
            run = run_gst(pipe, out, sever=sig, sever_after=1.5, eos=eos,
                          wall_cap=12.0)
            insp = wav_inspect(out)
            body[tag][key] = {"run": run, "insp": insp,
                              "stats": pcm_stats(out, insp),
                              "readers": readers(out, insp), "sha16": sha16(out)}
    # 5.2 cross-consumer control, same session, same wall time
    body["cross_consumer"] = {}
    for name, argv in (
            ("pw_record_TERM", ["pw-record", "-P", "stream.capture.sink=true",
                                "--target", SINK_SPDIF, "-n", "96000", "--rate",
                                "48000", "--channels", "2", "--format", "s16"]),
            ("pw_record_KILL", ["pw-record", "-P", "stream.capture.sink=true",
                                "--target", SINK_SPDIF, "-n", "96000", "--rate",
                                "48000", "--channels", "2", "--format", "s16"]),
            ("parecord_KILL", ["parecord", "--device", SINK_SPDIF + ".monitor",
                               "--file-format=wav"])):
        out = SCRATCH / ("sev_%s.wav" % name)
        clean(out)
        argv = argv + [str(out)]
        sig = signal.SIGKILL if name.endswith("KILL") else signal.SIGTERM
        p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE, text=True)
        time.sleep(1.5)
        p.send_signal(sig)
        try:
            p.wait(timeout=6)
        except subprocess.TimeoutExpired:                     # pragma: no cover
            p.kill()
        insp = wav_inspect(Path(out))
        body["cross_consumer"][name] = {
            "argv": argv, "rc": p.returncode, "sent": signal.Signals(sig).name,
            "stderr_head": first_error(p.stderr.read() or ""),
            "insp": insp, "stats": pcm_stats(out, insp),
            "readers": readers(out, insp), "sha16": sha16(out)}
    # 5.3 link topology witness for the live pipewiresrc monitor capture
    body["link_producers_sample"] = link_producers()
    return body


# ------------------------------------------------------------------ stage 6
def stage_formats():
    """Source-element property axis: pulse/alsa device + latency knobs."""
    body = {}
    # 6.1 pulsesrc device lattice (bounded num-buffers; no hardware exclusive)
    body["pulsesrc"] = {}
    for name, dev in (("line_source", SRC_LINE), ("spdif_monitor", SINK_SPDIF + ".monitor"),
                      ("garbage", "no_such_node_xyz"), ("default", None)):
        out = SCRATCH / ("ps_%s.wav" % name)
        prop = " device=%s" % dev if dev else ""
        run = run_gst("pulsesrc%s num-buffers=50 ! audio/x-raw,format=S16LE,"
                      "rate=48000,channels=2 ! wavenc ! filesink location=%s"
                      % (prop, out), out, wall_cap=12.0)
        insp = wav_inspect(Path(out))
        body["pulsesrc"][name] = {
            "device": dev, "rc": run["rc"], "err_class": err_class(run["stderr"])[0],
            "stderr_head": first_error(run["stderr"]), "insp": insp,
            "stats": pcm_stats(out, insp), "sha16": sha16(out)}
    # 6.2 latency/buffer-time knobs: do they reach the artifact?
    body["pulsesrc_knobs"] = {}
    for name, extra in (("baseline", ""),
                        ("buffer_time_2s", " buffer-time=2000000 latency-time=100000"),
                        ("buffer_time_50ms", " buffer-time=50000 latency-time=10000"),
                        ("blocksize_4096", " blocksize=4096"),
                        ("blocksize_65536", " blocksize=65536")):
        out = SCRATCH / ("psknob_%s.wav" % name)
        run = run_gst("pulsesrc device=%s%s num-buffers=50 ! "
                      "audio/x-raw,format=S16LE,rate=48000,channels=2 ! wavenc ! "
                      "filesink location=%s" % (SRC_LINE, extra, out), out, wall_cap=15.0)
        insp = wav_inspect(Path(out))
        body["pulsesrc_knobs"][name] = {
            "extra": extra, "rc": run["rc"], "elapsed_s": run["elapsed_s"],
            "stderr_head": first_error(run["stderr"]), "bytes": insp["bytes"],
            "frames_declared": insp["frames_declared"], "insp": insp,
            "sha16": sha16(out), "stats": pcm_stats(out, insp)}
    # 6.3 alsasrc: null device + refusal classes (NO real hw device is opened)
    body["alsasrc"] = {}
    for name, dev in (("null", "null"), ("bad_pcm", "no_such_pcm"),
                      ("hw99", "hw:99")):
        out = SCRATCH / ("as_%s.wav" % name)
        run = run_gst("alsasrc device=%s num-buffers=50 ! audio/x-raw,format=S16LE,"
                      "rate=48000,channels=2 ! wavenc ! filesink location=%s"
                      % (dev, out), out, wall_cap=12.0)
        insp = wav_inspect(Path(out))
        body["alsasrc"][name] = {
            "device": dev, "rc": run["rc"], "err_class": err_class(run["stderr"])[0],
            "stderr_head": first_error(run["stderr"]), "insp": insp,
            "stats": pcm_stats(out, insp), "sha16": sha16(out)}
    # 6.4 null-sink roundtrip: gst player -> gst capture, tone-anchored,
    #     zero physical-device writes (the r76 roundtrip idiom, gst edition)
    body["roundtrip"] = roundtrip()
    return body


def null_sink_load():
    r = subprocess.run(("pactl", "load-module", "module-null-sink",
                        "sink_name=" + NULL_SINK,
                        "sink_properties=device.description=gstscout"),
                       capture_output=True, text=True, timeout=20)
    return {"rc": r.returncode, "stdout": r.stdout.strip(),
            "stderr": r.stderr.strip()[:120]}


def null_sink_id():
    r = subprocess.run(("pactl", "list", "short", "modules"), capture_output=True,
                       text=True, timeout=20)
    for l in r.stdout.splitlines():
        if "module-null-sink" in l and NULL_SINK in l:
            return l.split("\t")[0]
    return None


def roundtrip():
    load = null_sink_load()
    time.sleep(0.6)
    res = {"load": load, "cells": {}}
    try:
        for label, capture_pipe, prop in (
                ("pipewiresrc_noprop", "pipewiresrc target-object=%s num-buffers=96", False),
                ("pipewiresrc_prop", "pipewiresrc target-object=%s num-buffers=96", True),
                ("pipewiresrc_monitor_suffix", "pipewiresrc target-object=%s.monitor num-buffers=96", False),
                ("pw_record_prop", None, True)):
            out = SCRATCH / ("rt_%s.wav" % label)
            clean(out)
            if capture_pipe is None:
                cap = subprocess.Popen(
                    ["pw-record", "-P", "stream.capture.sink=true", "--target",
                     NULL_SINK, "-n", "96000", "--rate", "48000", "--channels", "2",
                     "--format", "s16", str(out)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            else:
                pipe = capture_pipe % NULL_SINK
                if prop:
                    pipe += " stream-properties=props,stream.capture.sink=true"
                pipe += " ! audio/x-raw,format=S16LE,rate=48000,channels=2 ! wavenc ! filesink location=%s" % out
                cap = subprocess.Popen(["gst-launch-1.0", "-q", "-e"] + pipe.split(),
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.PIPE, text=True)
            time.sleep(0.5)
            play = run_gst("audiotestsrc wave=sine freq=1000 volume=0.5 "
                           "num-buffers=200 ! audio/x-raw,format=S16LE,rate=48000,"
                           "channels=2 ! pipewiresink target-object=%s" % NULL_SINK,
                           wall_cap=10.0)
            try:
                cap.wait(timeout=12)
            except subprocess.TimeoutExpired:
                cap.kill()
            insp = wav_inspect(out)
            res["cells"][label] = {
                "capture_argv": cap.args, "cap_rc": cap.returncode,
                "cap_stderr_head": first_error(cap.stderr.read() or ""),
                "play_rc": play["rc"], "play_stderr_head": play["stderr_head"],
                "insp": insp, "stats": pcm_stats(out, insp), "sha16": sha16(out),
                "carries_tone": (pcm_stats(out, insp).get("peak") or 0) > 100}
    finally:
        mid = null_sink_id()
        res["module_id"] = mid
        if mid:
            r = subprocess.run(("pactl", "unload-module", mid), capture_output=True,
                               text=True, timeout=20)
            res["unload"] = {"rc": r.returncode, "stderr": r.stderr.strip()[:120]}
        res["sinks_after"] = pw_targets()[0]
    return res


# ------------------------------------------------------------------ driver
STAGES = {"inventory": stage_inventory, "control": stage_control,
          "errors": stage_errors, "lattice": stage_lattice,
          "sever": stage_sever, "formats": stage_formats}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", nargs="+", choices=sorted(STAGES) + ["all"])
    ap.add_argument("--keep", action="store_true", help="keep scratch artifacts")
    args = ap.parse_args()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    stages = sorted(STAGES) if "all" in args.stage else args.stage
    for s in stages:
        t0 = time.monotonic()
        body = STAGES[s]()
        p = receipt(s, body)
        print("[stage] %-10s %6.1fs -> %s" % (s, time.monotonic() - t0, p.name))
    if not args.keep:
        print("[scratch] kept (operator may prune): %s = %d bytes"
              % (SCRATCH, dir_bytes(SCRATCH)))


if __name__ == "__main__":
    main()
