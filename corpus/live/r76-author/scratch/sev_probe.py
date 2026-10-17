#!/usr/bin/env python3
"""Scratch sever-class probe: spawn argv, wait, signal, inspect wav."""
import json, os, signal, struct, subprocess, sys, time

def wav_chunks(path):
    try:
        d = open(path, "rb").read()
    except OSError:
        return {"exists": False}
    r = {"exists": True, "bytes": len(d), "riff": d[:4] == b"RIFF"}
    if not r["riff"]:
        r["head"] = d[:16].hex()
        return r
    r["riff_size"] = struct.unpack("<I", d[4:8])[0]
    off, chunks = 12, []
    while off + 8 <= len(d):
        cid = d[off:off+4].decode("latin1")
        csz = struct.unpack("<I", d[off+4:off+8])[0]
        chunks.append([cid, csz, off])
        off += 8 + csz + (csz & 1)
    r["chunks"] = chunks
    for cid, csz, off in chunks:
        if cid == "data":
            r["data_declared"] = csz
            r["data_actual"] = len(d) - off - 8
            r["data_finalized"] = csz == len(d) - off - 8
    return r

def sever(argv, wait_s, sig, out):
    try:
        os.unlink(out)
    except OSError:
        pass
    p = subprocess.Popen(argv, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(wait_s)
    p.send_signal(sig)
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.wait()
    err = p.stderr.read().decode(errors="replace") if p.stderr else ""
    return {"rc": p.returncode, "tail": err.strip().splitlines()[-1][-140:] if err.strip() else None,
            "file": wav_chunks(out)}

SRC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
MON = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.monitor"
CASES = {}
if len(sys.argv) > 1 and sys.argv[1] == "all":
    for name, argv, out in [
        ("pwr_term", ["pw-record", "--target", SRC, "sev_pwr.wav"], "sev_pwr.wav"),
        ("prd_term", ["parecord", "-d", "@DEFAULT_MONITOR@", "sev_prd.wav"], "sev_prd.wav"),
        ("arc_term", ["arecord", "-D", "hw:0,0", "-f", "S16_LE", "-r", "48000", "-c", "2", "-t", "wav", "sev_arc.wav"], "sev_arc.wav"),
        ("ffm_term", ["ffmpeg", "-nostats", "-v", "error", "-f", "pulse", "-i", MON, "-y", "sev_ffm.wav"], "sev_ffm.wav"),
    ]:
        CASES[name] = sever(argv, 1.5, signal.SIGTERM, out)
        print(json.dumps({name: CASES[name]}, indent=None))
    for name, argv, out in [
        ("pwr_kill", ["pw-record", "--target", SRC, "sev_pwr_k.wav"], "sev_pwr_k.wav"),
        ("prd_kill", ["parecord", "-d", "@DEFAULT_MONITOR@", "sev_prd_k.wav"], "sev_prd_k.wav"),
        ("arc_kill", ["arecord", "-D", "hw:0,0", "-f", "S16_LE", "-r", "48000", "-c", "2", "-t", "wav", "sev_arc_k.wav"], "sev_arc_k.wav"),
        ("ffm_kill", ["ffmpeg", "-nostats", "-v", "error", "-f", "pulse", "-i", MON, "-y", "sev_ffm_k.wav"], "sev_ffm_k.wav"),
    ]:
        CASES[name] = sever(argv, 1.5, signal.SIGKILL, out)
        print(json.dumps({name: CASES[name]}, indent=None))
