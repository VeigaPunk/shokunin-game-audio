#!/usr/bin/env python3
"""R77 scout — FRONTIER 5 + 6: raw-stream integrity witness, and
concurrent playback+capture on the same node.

F5: parec --raw / pw-cat -r --raw / pw-record --raw — is byte count the ONLY
verdict a raw capture carries? Compare TERM vs KILL at the same bound: if the
two byte counts coincide within a granule and neither carries a header, then
nothing in the artifact distinguishes a completed raw capture from a severed
one.
F6: play a known 1 kHz tone into the default sink while capturing its
monitor concurrently — does the tone appear (same-node concurrent attach),
and what is the ordering hazard?
"""
import hashlib
import os
import signal
import subprocess
import sys
import struct
import time
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r77_probe import (CAP_BYTES, LINE, M_SPDIF, S_SPDIF, emit,  # noqa
                       errclass, mk, norm_err, sh, sh_capped)

TMP = mk()
TONE = os.path.join(TMP, "tone_1k_2s.wav")


def make_tone():
    """1 kHz sine, 2.0 s, stereo s16 48 kHz, amplitude 0.5 — probe-owned."""
    n = 96000
    fr = bytearray()
    for i in range(n):
        v = int(16384 * __import__("math").sin(2 * 3.141592653589793 * 1000 *
                                               i / 48000))
        fr += struct.pack("<hh", v, v)
    with wave.open(TONE, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(bytes(fr))
    return os.path.getsize(TONE)


def nz(data):
    if not data:
        return None
    return round(sum(1 for b in data if b) / len(data), 4)


def peak(data):
    if len(data) < 2:
        return None
    return max(abs(v) for v in struct.unpack("<%dh" % (len(data) // 2),
                                             data[:len(data) // 2 * 2]))


def run_raw(label, argv, sig, wait=1.0, cap=CAP_BYTES):
    rc, n, se, wall, cap_hit, sigsent, raw = sh_capped(
        argv, cap=cap, timeout=8.0, kill_after=wait if sig == "KILL" else None,
        term_after=wait if sig == "TERM" else None)
    return {"leg": label, "argv": argv, "rc": rc, "signal": sigsent,
            "nbytes": n, "cap_hit": cap_hit, "wall_s": wall,
            "sha": hashlib.sha256(raw).hexdigest()[:16],
            "nonzero_frac": nz(raw), "peak": peak(raw),
            "err_class": errclass(se)[0], "err_tail": norm_err(se)}


def main():
    out = {"probe": "raw-concurrent-r77", "tmp": TMP,
           "tone_bytes": make_tone(), "raw": {}, "concurrent": {}}

    # ---- F5: raw integrity -------------------------------------------
    raws = [
        ("parec_raw_TERM", ["parec", "-d", LINE, "--raw"]),
        ("parec_raw_KILL", ["parec", "-d", LINE, "--raw"]),
        ("parec_raw_mon_TERM", ["parec", "-d", M_SPDIF, "--raw"]),
        ("parec_raw_mon_KILL", ["parec", "-d", M_SPDIF, "--raw"]),
        ("pwcat_raw_TERM", ["pw-cat", "-r", "--raw", "--target", LINE]),
        ("pwcat_raw_KILL", ["pw-cat", "-r", "--raw", "--target", LINE]),
        ("pwcat_raw_stdout_TERM", ["pw-cat", "-r", "--target", LINE]),
        ("pwcat_raw_stdout_KILL", ["pw-cat", "-r", "--target", LINE]),
    ]
    for label, argv in raws:
        sig = "KILL" if label.endswith("KILL") else "TERM"
        out["raw"][label] = run_raw(label, argv, sig)
    # exact-count raw: the only deterministic raw witness
    p = os.path.join(TMP, "exact.raw")
    r = subprocess.run(["pw-record", "--raw", "--target", LINE, "-n", "48000",
                        p], capture_output=True, timeout=15)
    out["raw"]["pwrecord_raw_exact_n48000"] = {
        "rc": r.returncode,
        "bytes": os.path.getsize(p) if os.path.exists(p) else None,
        "expected": 48000 * 2 * 2,
        "err": r.stderr.decode(errors="replace").strip().splitlines()[-1][:120]
        if r.stderr.strip() else ""}

    # ---- F6: concurrent playback + capture on the same node -----------
    def concurrent(label, play_argv, cap_argv, cap_path, wait=2.2):
        pl = subprocess.Popen(play_argv, stdout=subprocess.DEVNULL,
                              stderr=subprocess.PIPE)
        time.sleep(0.15)
        cp = subprocess.Popen(cap_argv, stdout=subprocess.DEVNULL,
                              stderr=subprocess.PIPE)
        t0 = time.monotonic()
        try:
            pl.wait(timeout=wait)
        except subprocess.TimeoutExpired:
            pl.kill()
        time.sleep(0.2)
        if cp.poll() is None:
            cp.send_signal(signal.SIGTERM)
            try:
                cp.wait(timeout=6)
            except subprocess.TimeoutExpired:
                cp.kill()
                cp.wait(timeout=6)
        d = open(cap_path, "rb").read() if os.path.exists(cap_path) else b""
        pay = d[44:] if d[:4] == b"RIFF" else d
        return {"leg": label, "play_argv": play_argv, "cap_argv": cap_argv,
                "play_rc": pl.returncode,
                "play_err": norm_err(pl.stderr.read().decode(errors="replace"))
                if pl.stderr else "",
                "cap_rc": cp.returncode, "cap_bytes": len(d),
                "cap_payload_bytes": len(pay), "cap_nonzero_frac": nz(pay),
                "cap_peak": peak(pay), "wall_s": round(
                    time.monotonic() - t0, 2)}

    cases = [
        ("pwcat_play_into_sink + pwrecord_monitor",
         ["pw-cat", "-p", TONE, "--target", S_SPDIF],
         ["pw-record", "-P", "stream.capture.sink=true", "--target", S_SPDIF,
          os.path.join(TMP, "cc1.wav")], os.path.join(TMP, "cc1.wav")),
        ("paplay_into_sink + pwrecord_monitor",
         ["paplay", "--device", S_SPDIF, TONE],
         ["pw-record", "-P", "stream.capture.sink=true", "--target", S_SPDIF,
          os.path.join(TMP, "cc2.wav")], os.path.join(TMP, "cc2.wav")),
        ("pwcat_play + parec_monitor",
         ["pw-cat", "-p", TONE, "--target", S_SPDIF],
         ["parec", "-d", M_SPDIF, "--raw"], os.path.join(TMP, "cc3.raw")),
        ("pwcat_play + ffmpeg_monitor",
         ["pw-cat", "-p", TONE, "--target", S_SPDIF],
         ["ffmpeg", "-nostdin", "-nostats", "-v", "error", "-f", "pulse",
          "-i", M_SPDIF, "-t", "2", "-y", os.path.join(TMP, "cc4.wav")],
         os.path.join(TMP, "cc4.wav")),
        ("TWO pwrecord on same monitor",
         ["pw-record", "-P", "stream.capture.sink=true", "--target", S_SPDIF,
          "-n", "96000", os.path.join(TMP, "cc5b.wav")],
         ["pw-record", "-P", "stream.capture.sink=true", "--target", S_SPDIF,
          os.path.join(TMP, "cc5.wav")], os.path.join(TMP, "cc5.wav")),
    ]
    for label, play, cap, path in cases:
        if os.path.exists(path):
            os.unlink(path)
        out["concurrent"][label] = concurrent(label, play, cap, path)

    # silent-baseline: monitor captured with nothing playing
    pb = os.path.join(TMP, "cc0.wav")
    r = subprocess.run(["pw-record", "-P", "stream.capture.sink=true",
                        "--target", S_SPDIF, "-n", "48000", pb],
                       capture_output=True, timeout=20)
    d = open(pb, "rb").read() if os.path.exists(pb) else b""
    out["concurrent"]["BASELINE_no_playback"] = {
        "rc": r.returncode, "cap_bytes": len(d),
        "cap_payload_bytes": len(d) - 44,
        "cap_nonzero_frac": nz(d[44:]), "cap_peak": peak(d[44:])}

    emit(out, "probe-raw-concurrent-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
