#!/usr/bin/env python3
"""r76 verifier — independent byte-level spot verification of the r76
pinned claims.  Re-derives from raw bytes; does NOT import the fixture's
classifiers.  Scratch only (corpus/live/r76-verifier/)."""
import json
import os
import re
import signal
import struct
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

SRC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
SINK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
HW0 = "hw:0,0"
OUT = []


def rec(claim, verdict, detail):
    OUT.append({"claim": claim, "verdict": verdict, "detail": detail})
    print(f"[{verdict}] {claim}\n      {detail}")


def raw_inspect(path):
    """Independent structural read: (exists, bytes, riff_sz, data_decl,
    data_actual, riff_ok)."""
    p = Path(path)
    if not p.exists():
        return None
    d = p.read_bytes()
    r = {"bytes": len(d)}
    if len(d) < 12 or d[:4] != b"RIFF" or d[8:12] != b"WAVE":
        r["riff"] = False
        return r
    r["riff"] = True
    r["riff_sz"] = struct.unpack("<I", d[4:8])[0]
    off = 12
    r["chunks"] = []
    while off + 8 <= len(d):
        cid = d[off:off + 4].decode("latin1")
        csz = struct.unpack("<I", d[off + 4:off + 8])[0]
        r["chunks"].append((cid, csz))
        if cid == "data":
            r["data_decl"] = csz
            r["data_actual"] = len(d) - (off + 8)
            break
        off += 8 + csz + (csz & 1)
    return r


def wave_frames(path):
    try:
        with wave.open(str(path), "rb") as w:
            return w.getnframes(), None
    except Exception as exc:
        return None, type(exc).__name__


def sever(argv, out, sig, wait_s):
    pr = subprocess.Popen(argv + [out], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          start_new_session=True)
    time.sleep(wait_s)
    if pr.poll() is None:
        pr.send_signal(sig)
    try:
        pr.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        os.killpg(pr.pid, signal.SIGKILL)
        pr.wait()
    return pr.returncode


def main():
    tmp = Path(tempfile.mkdtemp(prefix="r76-verifier-spot-",
                                dir="/tmp"))

    # ---- C1 pw-record TERM finalizes / KILL wounds --------------------
    for sig, tag in ((signal.SIGTERM, "TERM"), (signal.SIGKILL, "KILL")):
        f = tmp / f"pwr_{tag}.wav"
        rc = sever(["pw-record", "--target", SRC, "--rate", "48000",
                    "--channels", "2", "--format", "s16"], str(f), sig,
                   1.5)
        r = raw_inspect(f)
        nf, werr = wave_frames(f)
        detail = (f"rc={rc} bytes={r['bytes']} riff_sz={r['riff_sz']} "
                  f"data_decl={r.get('data_decl')} "
                  f"data_actual={r.get('data_actual')} "
                  f"wave_frames={nf} wave_err={werr}")
        if tag == "TERM":
            ok = rc == 1 and r["riff_sz"] == r["bytes"] - 8 and \
                r.get("data_decl") == r.get("data_actual") and \
                nf is not None
            rec("C1a pw-record TERM: rc=1 + FINALIZED header",
                "AGREE" if ok else "DISAGREE", detail)
        else:
            ok = rc == -9 and r["riff_sz"] == 8 and \
                r.get("data_decl") == 0 and r.get("data_actual", 0) > 0 \
                and werr is not None
            rec("C1b pw-record KILL: riff_sz=8/data=0 wound rejected by "
                "stdlib wave", "AGREE" if ok else "DISAGREE", detail)

    # ---- C2 parecord TERM finalizes / KILL wounds ---------------------
    for sig, tag in ((signal.SIGTERM, "TERM"), (signal.SIGKILL, "KILL")):
        f = tmp / f"prd_{tag}.wav"
        rc = sever(["parecord", "-d", "@DEFAULT_SOURCE@"], str(f), sig,
                   2.5)
        r = raw_inspect(f)
        nf, werr = wave_frames(f)
        detail = (f"rc={rc} bytes={r['bytes']} riff_sz={r['riff_sz']} "
                  f"data_decl={r.get('data_decl')} "
                  f"data_actual={r.get('data_actual')} "
                  f"64k_aligned={r.get('data_actual', 0) % 65536 == 0} "
                  f"wave_frames={nf} wave_err={werr}")
        if tag == "TERM":
            ok = rc == 0 and r["riff_sz"] == r["bytes"] - 8 and \
                r.get("data_actual", 0) > 0 and \
                r["data_actual"] % 65536 == 0 and nf is not None
            rec("C2a parecord TERM: rc=0 + finalized 64-KiB-granule "
                "payload", "AGREE" if ok else "DISAGREE", detail)
        else:
            ok = rc == -9 and r["riff_sz"] == 8 and \
                r.get("data_decl") == 0 and r.get("data_actual", 0) > 0 \
                and werr is not None
            rec("C2b parecord KILL: riff_sz=8/data=0 wound rejected",
                "AGREE" if ok else "DISAGREE", detail)

    # ---- C3 the rc=0-EMPTY reachable degeneracy (D1 reachability) -----
    # parecord's ~1.9 s dead start: a TERM inside that window must land
    # rc=0 with a FINALIZED header over ZERO audio bytes.
    f = tmp / "prd_fast.wav"
    rc = sever(["parecord", "-d", "@DEFAULT_SOURCE@"], str(f),
               signal.SIGTERM, 0.4)
    r = raw_inspect(f)
    nf, werr = wave_frames(f)
    detail = (f"rc={rc} bytes={r['bytes']} riff_sz={r['riff_sz']} "
              f"data_decl={r.get('data_decl')} "
              f"data_actual={r.get('data_actual')} wave_frames={nf} "
              f"wave_err={werr}  (TERM at 0.4 s, inside the dead start)")
    ok = rc == 0 and r["riff_sz"] == r["bytes"] - 8 and \
        r.get("data_actual") == 0
    rec("C3 rc=0-with-EMPTY-capture is REACHABLE (rc is never the "
        "verdict)", "AGREE" if ok else "DISAGREE", detail)

    # ---- C4 ffmpeg TERM finalized / KILL placeholder_ff ---------------
    for sig, tag in ((signal.SIGTERM, "TERM"), (signal.SIGKILL, "KILL")):
        f = tmp / f"ffm_{tag}.wav"
        rc = sever(["ffmpeg", "-nostdin", "-nostats", "-v", "error",
                    "-f", "pulse", "-i", SRC, "-y"], str(f), sig, 2.5)
        r = raw_inspect(f)
        nf, werr = wave_frames(f)
        detail = (f"rc={rc} exists={r is not None} "
                  f"bytes={r.get('bytes') if r else None} "
                  f"riff_sz={r.get('riff_sz') if r else None} "
                  f"data_decl={r.get('data_decl') if r else None} "
                  f"data_actual={r.get('data_actual') if r else None} "
                  f"wave_frames={nf} wave_err={werr}")
        if tag == "TERM":
            ok = rc == 255 and r and r["riff_sz"] == r["bytes"] - 8 and \
                nf is not None
            rec("C4a ffmpeg TERM: rc=255 with a USABLE finalized file",
                "AGREE" if ok else "DISAGREE", detail)
        else:
            ok = rc == -9 and (r is None or r["bytes"] == 0 or
                               r.get("riff_sz") == 0xFFFFFFFF)
            rec("C4b ffmpeg KILL: unfinalized class (missing / 0-byte / "
                "0xFFFFFFFF)", "AGREE" if ok else "DISAGREE", detail)

    # ---- C5 arecord KILL accept-and-lie -------------------------------
    f = tmp / "arc_kill.wav"
    rc = sever(["arecord", "-D", HW0, "-f", "S16_LE", "-r", "48000",
                "-c", "2", "-t", "wav"], str(f), signal.SIGKILL, 1.5)
    r = raw_inspect(f)
    nf, werr = wave_frames(f)
    honest = r.get("data_actual", 0) // 4 if r else 0
    detail = (f"rc={rc} bytes={r['bytes']} riff_sz={r['riff_sz']} "
              f"(0x{r['riff_sz']:08x}) data_decl={r.get('data_decl')} "
              f"(0x{r.get('data_decl', 0):08x}) "
              f"data_actual={r.get('data_actual')} honest_frames={honest} "
              f"wave_frames={nf} wave_err={werr}")
    ok = rc == -9 and r.get("data_decl") == 0x80000000 and \
        nf is not None and honest > 0 and nf > honest * 4
    rec("C5 arecord KILL: data=0x80000000, stdlib wave ACCEPTS and "
        "INFLATES (accept-and-lie)", "AGREE" if ok else "DISAGREE",
        detail)

    # ---- C6 arecord -D null -d 1 : exact 192044 B, unpaced ------------
    f = tmp / "arc_null.wav"
    t0 = time.monotonic()
    pr = subprocess.run(["arecord", "-D", "null", "-d", "1",
                         "-f", "S16_LE", "-r", "48000", "-c", "2",
                         "-t", "wav", str(f)], capture_output=True,
                        timeout=15)
    wall = time.monotonic() - t0
    r = raw_inspect(f)
    detail = (f"rc={pr.returncode} bytes={r['bytes']} "
              f"data_actual={r.get('data_actual')} "
              f"riff_sz={r['riff_sz']} wall={wall:.3f} s")
    ok = pr.returncode == 0 and r["bytes"] == 192044 and wall < 0.5
    rec("C6 arecord -D null -d 1: EXACT 192044 B, unpaced (wall << 1 s)",
        "AGREE" if ok else "DISAGREE", detail)

    # ---- C7 parecord ~1.9 s dead start (two-point fit) ----------------
    pts = []
    for wait_s in (4.0, 8.0):
        f = tmp / f"prd_{wait_s}.wav"
        rc = sever(["parecord", "-d", "@DEFAULT_SOURCE@"], str(f),
                   signal.SIGTERM, wait_s)
        r = raw_inspect(f)
        cap_s = r.get("data_actual", 0) / 4 / 44100
        pts.append((wait_s, cap_s, r.get("data_actual"), rc))
        time.sleep(0.3)
    dead = [(w - c) for w, c, _, _ in pts]
    detail = (" | ".join(f"TERM@{w}s -> captured {c:.3f} s "
                         f"({b} B, rc={rc})"
                         for w, c, b, rc in pts)
              + f"  => dead-start estimate {min(dead):.3f}-"
                f"{max(dead):.3f} s")
    ok = all(1.5 <= d <= 2.3 for d in dead)
    rec("C7 parecord has a ~1.9 s fixed dead start (dead start = wait - "
        "captured)", "AGREE" if ok else "DISAGREE", detail)

    # ---- C8 roundtrip monitor capture = 960044 B, nonzero -------------
    f = tmp / "roundtrip.wav"
    member = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/"
                  "artifacts/stem_sections.wav")
    rec_pr = subprocess.Popen(
        ["pw-record", "-P", "stream.capture.sink=true", "--target", SINK,
         "-n", "240000", "--rate", "48000", "--channels", "2",
         "--format", "s16", str(f)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True)
    time.sleep(0.7)
    pl = subprocess.run(["pw-cat", "-p", str(member)],
                        capture_output=True, timeout=60)
    try:
        rec_pr.wait(timeout=60)
    except subprocess.TimeoutExpired:
        os.killpg(rec_pr.pid, signal.SIGKILL)
        rec_pr.wait()
    r = raw_inspect(f)
    d = f.read_bytes()[44:] if f.exists() else b""
    nz = sum(1 for x in d if x) / max(1, len(d))
    detail = (f"rc={rec_pr.returncode} player_rc={pl.returncode} "
              f"bytes={r['bytes']} expected=960044 "
              f"data_finalized={r['riff_sz'] == r['bytes'] - 8} "
              f"nonzero_byte_fraction={nz:.3f}")
    ok = r["bytes"] == 960044 and nz > 0.5 and pl.returncode == 0
    rec("C8 roundtrip: monitor capture = 960044 B with nonzero audio",
        "AGREE" if ok else "DISAGREE", detail)

    print("\n=== SUMMARY ===")
    for o in OUT:
        print(f"{o['verdict']:9s} {o['claim'][:72]}")
    Path("corpus/live/r76-verifier/spot_verify.json").write_text(
        json.dumps(OUT, indent=1))
    sys.exit(0)


if __name__ == "__main__":
    main()
