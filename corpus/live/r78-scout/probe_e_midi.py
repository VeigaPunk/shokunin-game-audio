#!/usr/bin/env python3
"""Probe E — MIDI / ALSA-seq capture surface.

Questions:
 1. `arecordmidi` / `aseqdump` on Midi Through (14:0): baseline empty vs
    aseqsend/aplaymidi injection — is there a bounded fixture-row surface?
 2. `pw-record -M midi --target <Midi-Bridge>`: does PipeWire's MIDI surface
    capture ALSA-seq events through the bridge?
 3. Named refusal classes on bad ports.
"""
import json
import os
import signal
import struct
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78_probe import (SEAT, SCRATCH, sh, errclass, norm_err, mk, emit, du)


def mk_smf(path):
    """Minimal SMF: MThd + one MTrk, note-on/note-off C4 60, tempo 96bpm."""
    trk = bytearray()
    trk += b"\x00\x90\x3c\x60"      # dt=0 note-on ch1 C4 vel 96
    trk += b"\x83\x60\x80\x3c\x40"  # dt=480 note-off
    trk += b"\x00\xff\x2f\x00"      # end of track
    smf = b"MThd" + struct.pack(">IH HH", 6, 0, 1, 480) + \
        b"MTrk" + struct.pack(">I", len(trk)) + bytes(trk)
    open(path, "wb").write(smf)
    return path


def timed(argv, kill_after=3.0, timeout=6, env=None):
    p = subprocess.Popen(argv, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env or dict(os.environ))
    t0 = time.monotonic()
    time.sleep(kill_after)
    rc = p.poll()
    sig = None
    if rc is None:
        p.send_signal(signal.SIGTERM)
        sig = "TERM"
        try:
            rc = p.wait(timeout=4)
        except subprocess.TimeoutExpired:
            p.send_signal(signal.SIGKILL)
            sig = "KILL"
            rc = p.wait(timeout=4)
    so = p.stdout.read()
    se = p.stderr.read().decode(errors="replace")
    return {"argv": argv, "rc": rc, "sig": sig,
            "stdout": so.decode(errors="replace")[:600],
            "err_line": norm_err(se), "err_class": errclass(se)[0],
            "wall_s": round(time.monotonic() - t0, 3)}


def file_info(path):
    if not os.path.exists(path):
        return {"exists": False}
    d = open(path, "rb").read()
    return {"exists": True, "bytes": len(d), "head16": d[:16].hex(),
            "mthd": d[:4] == b"MThd", "mtrk_count": d.count(b"MTrk"),
            "noteon_90": d.count(b"\x90"), "tail8": d[-8:].hex()}


def main():
    tmp = mk()
    res = {"seq_ports": None, "legs": {}}
    rc, so, se, _w, _t = sh(["arecordmidi", "-l"], timeout=6)
    res["arecordmidi_l"] = so.decode(errors="replace").strip()
    rc, so, se, _w, _t = sh(["aseqdump", "-l"], timeout=6)
    res["aseqdump_l"] = so.decode(errors="replace").strip()

    smf = mk_smf(os.path.join(tmp, "in.mid"))

    # 1. aseqdump baseline (no events): bounded 1.5s
    res["legs"]["aseqdump_idle"] = timed(
        ["aseqdump", "-p", "14:0"], kill_after=1.5)

    # 2. arecordmidi -n 2 bounded record + aseqsend SysEx injection
    out_mid = os.path.join(tmp, "rec_sysex.mid")
    rec = subprocess.Popen(
        ["arecordmidi", "-p", "14:0", "-n", "4", out_mid],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    time.sleep(0.6)
    # aseqsend sends raw bytes as events (SysEx F0 ... F7)
    s1 = sh(["aseqsend", "-p", "14:0", "-s", "f0437f7c00f7"], timeout=5)
    s2 = sh(["aseqsend", "-p", "14:0", "-s", "f07e7f0901f7"], timeout=5)
    s3 = sh(["aseqsend", "-p", "14:0", "-s", "f0437f7c01f7"], timeout=5)
    s4 = sh(["aseqsend", "-p", "14:0", "-s", "f0437f7c02f7"], timeout=5)
    rcv = None
    t0 = time.monotonic()
    while rcv is None and time.monotonic() - t0 < 8:
        rcv = rec.poll()
        time.sleep(0.05)
    if rcv is None:
        rec.send_signal(signal.SIGTERM)
        rcv = rec.wait(timeout=4)
    rec_se = rec.stderr.read().decode(errors="replace")
    res["legs"]["arecordmidi_sysex"] = {
        "send_rcs": [s1[0], s2[0], s3[0], s4[0]],
        "send_errs": [norm_err(x[2]) for x in (s1, s2, s3, s4)],
        "rc": rcv, "err": norm_err(rec_se), "file": file_info(out_mid)}

    # 3. arecordmidi record + aplaymidi playing the SMF into 14:0
    out_mid2 = os.path.join(tmp, "rec_smf.mid")
    rec = subprocess.Popen(
        ["arecordmidi", "-p", "14:0", "-n", "4", "-b", "120", out_mid2],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    time.sleep(0.6)
    ap = sh(["aplaymidi", "-p", "14:0", smf], timeout=8)
    rcv = None
    t0 = time.monotonic()
    while rcv is None and time.monotonic() - t0 < 8:
        rcv = rec.poll()
        time.sleep(0.05)
    if rcv is None:
        rec.send_signal(signal.SIGTERM)
        rcv = rec.wait(timeout=4)
    res["legs"]["arecordmidi_smf"] = {
        "aplay_rc": ap[0], "aplay_err": norm_err(ap[2]),
        "rc": rcv, "file": file_info(out_mid2)}

    # 4. aseqdump WHILE aplaymidi injects (the text witness)
    dump = subprocess.Popen(["aseqdump", "-p", "14:0"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.5)
    ap = sh(["aplaymidi", "-p", "14:0", smf], timeout=8)
    time.sleep(0.4)
    dump.send_signal(signal.SIGTERM)
    dso, dse = dump.communicate(timeout=4)
    res["legs"]["aseqdump_with_events"] = {
        "aplay_rc": ap[0],
        "stdout": dso.decode(errors="replace")[:800],
        "err": norm_err(dse.decode(errors="replace"))}

    # 5. pw-record -M midi against the Midi-Bridge node names
    for nm, target in (("pwrmidi_bridge", "Midi-Bridge"),
                       ("pwrmidi_portname", "Midi Through"),
                       ("pwrmidi_garbage", "no_such_midi_xyz")):
        out = os.path.join(tmp, nm + ".mid")
        p = subprocess.Popen(
            ["pw-record", "-M", "midi", "-P", "node.name=r78mid",
             "--target", target, "-n", "128", out],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        time.sleep(0.8)
        s = sh(["aseqsend", "-p", "14:0", "-s", "f0437f7c00f7"], timeout=5)
        time.sleep(0.5)
        prc = p.poll()
        if prc is None:
            p.send_signal(signal.SIGTERM)
            try:
                prc = p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.kill()
                prc = p.wait(timeout=3)
        se = p.stderr.read().decode(errors="replace")
        res["legs"][nm] = {"rc": prc, "err_class": errclass(se)[0],
                           "err": norm_err(se), "send_rc": s[0],
                           "file": file_info(out)}

    # 6. refusal lattice
    for nm, argv in (
        ("arecordmidi_badport", ["arecordmidi", "-p", "99:9",
                                 os.path.join(tmp, "bad.mid")]),
        ("aseqdump_badport", ["aseqdump", "-p", "99:9"]),
        ("aplaymidi_badport", ["aplaymidi", "-p", "99:9", smf]),
    ):
        res["legs"][nm] = timed(argv, kill_after=1.2)

    res["scratch_bytes"] = du()
    emit(res, "probe-midi-r78.json")


if __name__ == "__main__":
    main()
