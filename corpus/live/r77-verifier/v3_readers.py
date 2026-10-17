#!/usr/bin/env python3
"""r77 verifier — independent reader-matrix spot check (claim 3):
3 wounds x this verifier's OWN reader invocations.

Wounds (KILL at 2.5 s, serialized, each < 1 MB):
  A `pw_record_kill`        — pw-record monitor capture, open header unwritten
                              (declared 0)
  B `arecord_bounded_kill`  — arecord `-d 12` on the hw device (bound-derived
                              declaration 2304000 B = 576000 frames)
  C `ffmpeg_pulse_kill`     — ffmpeg pulse demuxer, 0xFFFFFFFF declaration
Plus one TERM control on A (finalized header) to show the honest case.

Readers, all invoked here directly: python `wave`, `ffprobe`,
`soxi -s`, `soxi -D`, `sndfile-info`. `honest` and `declared` frames are
derived from this script's own RIFF walk, never from a reader.
"""
import array
import importlib.util
import json
import re
import signal
import struct
import subprocess
import tempfile
import time
import wave
from pathlib import Path

_here = Path(__file__).with_name("v1_lattice.py")
_spec = importlib.util.spec_from_file_location("v1", _here)
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)

OUT = v1.OUT
REPO = v1.REPO
SEVER_S = 2.5
KILL_WAIT_S = 6.0


def riff(path):
    b = Path(path).read_bytes()
    st = {"bytes": len(b)}
    if len(b) < 44 or b[:4] != b"RIFF":
        return st
    tag, ch, rate, _br, _ba, bits = struct.unpack("<HHIIHH", b[20:36])
    st["fmt"] = {"tag": tag, "channels": ch, "rate": rate, "bits": bits}
    st["riff_size_field"] = ("finalized" if struct.unpack("<I", b[4:8])[0]
                             == len(b) - 8 else
                             "placeholder_80000000"
                             if struct.unpack("<I", b[4:8])[0] == 0x80000000
                             else "placeholder_ff"
                             if struct.unpack("<I", b[4:8])[0] == 0xFFFFFFFF
                             else "placeholder_8"
                             if struct.unpack("<I", b[4:8])[0] == 8 else "other")
    off = 12
    while off + 8 <= len(b):
        cid = b[off:off + 4]
        csz = struct.unpack("<I", b[off + 4:off + 8])[0]
        if cid == b"data":
            st["data_offset"] = off
            st["data_declared"] = csz
            st["data_actual"] = len(b) - (off + 8)
            st["data_finalized"] = (csz == st["data_actual"])
            break
        off += 8 + csz + (csz & 1)
    fb = st["fmt"]["channels"] * (st["fmt"]["bits"] // 8)
    st["frame_bytes"] = fb
    st["honest_frames"] = st["data_actual"] // fb
    st["declared_frames"] = st["data_declared"] // fb
    st["rate"] = st["fmt"]["rate"]
    return st


def klass(value, honest, declared):
    if value is None:
        return "absent"
    if honest == 0:
        return "honest_empty" if value == 0 else "inflated"
    if value == honest:
        return "honest"
    if declared != honest and value == declared:
        return "declared_echo"
    return "inflated" if value > honest else "underreports"


def readers(path, st):
    rate, fb = st["rate"], st["frame_bytes"]
    honest, declared = st["honest_frames"], st["declared_frames"]
    out = {"honest_frames": honest, "declared_frames": declared}
    try:
        with wave.open(str(path), "rb") as w:
            n = w.getnframes()
        out["wave"] = {"value": n, "verdict": klass(n, honest, declared)}
    except Exception as exc:
        out["wave"] = {"value": None, "verdict": "rejects",
                       "error": type(exc).__name__}
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "json", str(path)],
                       capture_output=True, timeout=15)
    try:
        dur = json.loads(p.stdout or b"{}").get("format", {}).get("duration")
    except ValueError:
        dur = None
    if dur is None:
        out["ffprobe"] = {"value": None, "verdict": "abstain"}
    else:
        n = round(float(dur) * rate)
        out["ffprobe"] = {"duration_s": round(float(dur), 6), "value": n,
                          "verdict": klass(n, honest, declared)}
    for key, flag in (("soxi_s", "-s"), ("soxi_D", "-D")):
        p = subprocess.run(["soxi", flag, str(path)], capture_output=True,
                           text=True, timeout=15)
        raw = p.stdout.strip()
        if not raw:
            out[key] = {"value": None, "verdict": "absent"}
            continue
        n = int(float(raw)) if flag == "-s" else round(float(raw) * rate)
        out[key] = {"raw": raw, "value": n,
                    "verdict": klass(n, honest, declared)}
    p = subprocess.run(["sndfile-info", str(path)], capture_output=True,
                       text=True, timeout=15)
    m = re.search(r"^Frames\s*:\s*(\d+)", p.stdout, re.M)
    if m:
        n = int(m.group(1))
        out["sndfile"] = {"value": n, "verdict": klass(n, honest, declared)}
    else:
        out["sndfile"] = {"value": None, "verdict": "reject_or_absent",
                          "exit_code": p.returncode}
    return out


def wound(name, argv, sig, tmp, wait_s=SEVER_S):
    out = Path(tmp) / f"{name}.wav"
    proc = subprocess.Popen(argv + [str(out)], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    early = None
    try:
        proc.wait(timeout=wait_s)
        early = proc.returncode
    except subprocess.TimeoutExpired:
        pass
    if early is None:
        proc.send_signal(sig)
        try:
            proc.wait(timeout=KILL_WAIT_S)
        except subprocess.TimeoutExpired:
            import os
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
    err = proc.stderr.read().decode(errors="replace")
    rec = {"argv": " ".join(argv) + " <out>", "signal": sig.name,
           "sever_after_s": wait_s,
           "early_exit_code": early, "exit_code": proc.returncode,
           "stderr": err.strip().splitlines()[:2]}
    if not out.exists() or not out.stat().st_size:
        rec["file"] = {"exists": out.exists()}
        return rec
    st = riff(out)
    rec["file"] = {k: st[k] for k in
                   ("bytes", "fmt", "riff_size_field", "data_declared",
                    "data_actual", "data_finalized")}
    rec["readers"] = readers(out, st)
    return rec


def main():
    sink = v1.default_sink()
    mon = sink + ".monitor"
    hw0 = "hw:0,0"
    entry = {"probe": "r77-verifier independent reader matrix",
             "sever_s": SEVER_S, "wounds": {}, "failures": []}
    with tempfile.TemporaryDirectory(prefix="r77v-readers-") as tmp:
        entry["wounds"]["pw_record_kill"] = wound(
            "pw_record_kill",
            ["pw-record", "-P", "stream.capture.sink=true",
             "--target", sink], signal.SIGKILL, tmp)
        entry["wounds"]["pw_record_term"] = wound(
            "pw_record_term",
            ["pw-record", "-P", "stream.capture.sink=true",
             "--target", sink], signal.SIGTERM, tmp)
        time.sleep(1.0)
        entry["wounds"]["arecord_bounded_kill"] = wound(
            "arecord_bounded_kill",
            ["arecord", "-D", hw0, "-d", "12", "-f", "S16_LE", "-r", "48000",
             "-c", "2", "-t", "wav"], signal.SIGKILL, tmp)
        time.sleep(1.0)
        entry["wounds"]["ffmpeg_pulse_kill"] = wound(
            "ffmpeg_pulse_kill",
            ["ffmpeg", "-nostdin", "-nostats", "-v", "error", "-f", "pulse",
             "-i", mon, "-t", "12", "-y"], signal.SIGKILL, tmp)
    f = entry["failures"]
    w = entry["wounds"]
    # the arm's pinned classes, re-derived here
    for key in ("pw_record_kill", "arecord_bounded_kill", "ffmpeg_pulse_kill"):
        leg = w[key]
        rd = leg.get("readers")
        if not rd:
            f.append(f"{key}: no readers ran ({leg.get('file')})")
            continue
        if rd["sndfile"]["verdict"] != "honest":
            f.append(f"{key}: sndfile-info expected honest, got "
                     f"{rd['sndfile']['verdict']}")
    if w["pw_record_kill"].get("readers", {}).get("wave", {}).get("verdict") \
            != "rejects":
        f.append("pw_record_kill: stdlib wave expected to reject the "
                 "unwritten header")
    if w["pw_record_kill"].get("readers", {}).get("soxi_s", {}).get(
            "verdict") != "declared_echo":
        f.append("pw_record_kill: soxi -s expected declared_echo")
    ak = w["arecord_bounded_kill"]
    if ak.get("file", {}).get("data_declared") != 12 * 192000:
        f.append(f"arecord_bounded_kill: expected the bound-derived "
                 f"declaration 2304000 B, got "
                 f"{ak.get('file', {}).get('data_declared')}")
    if ak.get("readers", {}).get("wave", {}).get("verdict") not in (
            "declared_echo", "inflated"):
        f.append("arecord_bounded_kill: stdlib wave expected to accept and "
                 "inflate the over-declared header")
    fk = w["ffmpeg_pulse_kill"]
    if fk.get("file", {}).get("data_declared") != 0xFFFFFFFF:
        f.append(f"ffmpeg_pulse_kill: expected the 0xFFFFFFFF declaration, "
                 f"got {fk.get('file', {}).get('data_declared')}")
    if w["pw_record_term"].get("file", {}).get("data_finalized") is not True:
        f.append("pw_record_term: TERM must finalize the header")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "v3_readers.json").write_text(json.dumps(entry, indent=2) + "\n")
    print(json.dumps({"receipt": str(OUT / "v3_readers.json"),
                      "failures": entry["failures"]}))


if __name__ == "__main__":
    main()
