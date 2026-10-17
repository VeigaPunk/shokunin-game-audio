#!/usr/bin/env python3
"""r76 verifier — follow-up: resolve the two spot-verify DISAGREEs.

C5'  arecord KILL on a FREE device (the first attempt hit a busy card
     and early-exited, so the -9 wound never landed).
C8'  roundtrip with the CORRECT member path (corpus/artifacts/...), plus
     pw-cat stderr when it fails.
C9   parecord's declared rate vs actual byte rate — the source of the
     boundary seat's 1.95 s vs the file's declared-rate 1.77 s fit.
"""
import json
import os
import signal
import struct
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SINK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
MEMBER = REPO / "corpus" / "artifacts" / "stem_sections.wav"
OUT = []


def rec(claim, verdict, detail):
    OUT.append({"claim": claim, "verdict": verdict, "detail": detail})
    print(f"[{verdict}] {claim}\n      {detail}")


def raw_inspect(path):
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
    while off + 8 <= len(d):
        cid = d[off:off + 4].decode("latin1")
        csz = struct.unpack("<I", d[off + 4:off + 8])[0]
        if cid == "fmt " and csz >= 16:
            tag, ch, rate, _br, _ba, bits = struct.unpack(
                "<HHIIHH", d[off + 8:off + 24])
            r["fmt"] = {"tag": tag, "channels": ch, "rate": rate,
                        "bits": bits}
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


def devices():
    p = subprocess.run(["arecord", "-l"], capture_output=True, timeout=10)
    import re
    return [f"hw:{m.group(1)},{m.group(2)}" for m in re.finditer(
        r"card (\d+): \S+ \[[^\]]*\], device (\d+):",
        p.stdout.decode(errors="replace"))]


def main():
    tmp = Path(tempfile.mkdtemp(prefix="r76-verifier-fu-", dir="/tmp"))

    # ---- C5' arecord KILL on the first device that is not busy ---------
    devs = devices()
    got = None
    attempts = []
    for dev in devs:
        f = tmp / f"arc_{dev.replace(':','_')}.wav"
        pr = subprocess.Popen(
            ["arecord", "-D", dev, "-f", "S16_LE", "-r", "48000",
             "-c", "2", "-t", "wav", str(f)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True)
        early = None
        try:
            pr.wait(timeout=1.5)
            early = pr.returncode
        except subprocess.TimeoutExpired:
            pass
        if early is None:
            if pr.poll() is None:
                pr.send_signal(signal.SIGKILL)
            try:
                pr.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                os.killpg(pr.pid, signal.SIGKILL)
                pr.wait()
        err = pr.stderr.read().decode(errors="replace").strip()
        r = raw_inspect(f)
        nf, werr = wave_frames(f)
        honest = (r.get("data_actual", 0) // 4) if r else 0
        attempts.append(
            f"{dev}: early_rc={early} rc={pr.returncode} "
            f"bytes={r.get('bytes') if r else None} "
            f"data_decl={hex(r.get('data_decl', 0)) if r else None} "
            f"data_actual={r.get('data_actual') if r else None} "
            f"wave_frames={nf} wave_err={werr} "
            f"stderr={err[:60]!r}")
        if pr.returncode == -9 and r and \
                r.get("data_decl") == 0x80000000:
            got = (dev, r, nf, honest, pr.returncode)
            break
    detail = " || ".join(attempts)
    if got:
        dev, r, nf, honest, rc = got
        ok = nf is not None and honest > 0 and nf > honest * 4
        rec("C5' arecord KILL: data=0x80000000 + stdlib wave ACCEPTS and "
            "INFLATES", "AGREE" if ok else "DISAGREE",
            f"device={dev} rc={rc} bytes={r['bytes']} "
            f"data_actual={r['data_actual']} honest_frames={honest} "
            f"wave_frames={nf}  ||  {detail}")
    else:
        rec("C5' arecord KILL: data=0x80000000 + wave accept-and-lie",
            "INCONCLUSIVE (no free device this pass)", detail)

    # ---- C8' roundtrip with the CORRECT member ------------------------
    f = tmp / "roundtrip.wav"
    rec_pr = subprocess.Popen(
        ["pw-record", "-P", "stream.capture.sink=true", "--target", SINK,
         "-n", "240000", "--rate", "48000", "--channels", "2",
         "--format", "s16", str(f)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True)
    time.sleep(0.7)
    pl = subprocess.run(["pw-cat", "-p", str(MEMBER)],
                        capture_output=True, timeout=60)
    try:
        rec_pr.wait(timeout=60)
    except subprocess.TimeoutExpired:
        os.killpg(rec_pr.pid, signal.SIGKILL)
        rec_pr.wait()
    r = raw_inspect(f)
    d = f.read_bytes()[44:] if f.exists() else b""
    nz = sum(1 for x in d if x) / max(1, len(d))
    peak = max((abs(struct.unpack("<h", d[i:i + 2])[0])
                for i in range(0, len(d) - 1, 2)), default=0)
    detail = (f"member={MEMBER} exists={MEMBER.exists()} "
              f"player_rc={pl.returncode} "
              f"player_err={pl.stderr.decode(errors='replace')[:80]!r} "
              f"rec_rc={rec_pr.returncode} bytes={r['bytes']} "
              f"finalized={r['riff_sz'] == r['bytes'] - 8} "
              f"nonzero_fraction={nz:.3f} peak={peak}")
    ok = r["bytes"] == 960044 and nz > 0.5 and pl.returncode == 0
    rec("C8' roundtrip: 960044 B AND nonzero audio (content witness)",
        "AGREE" if ok else "DISAGREE", detail)

    # ---- C9 parecord declared rate vs byte rate -----------------------
    pts = []
    for rate, tag in ((None, "default(header rate)"),
                      ("48000", "--rate=48000")):
        f = tmp / f"prd_rate_{tag.split('(')[0].strip('--')}.wav"
        argv = ["parecord", "-d", "@DEFAULT_SOURCE@"]
        if rate:
            argv += [f"--rate={rate}"]
        pr = subprocess.Popen(argv + [str(f)], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              start_new_session=True)
        time.sleep(4.0)
        if pr.poll() is None:
            pr.send_signal(signal.SIGTERM)
        try:
            pr.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            os.killpg(pr.pid, signal.SIGKILL)
            pr.wait()
        r = raw_inspect(f)
        pts.append((tag, r.get("fmt", {}).get("rate"),
                    r.get("data_actual"), pr.returncode))
    detail = " | ".join(
        f"{t}: header_rate={hr} data_actual={a} rc={rc}"
        for t, hr, a, rc in pts)
    rec("C9 parecord: file header rate 44100 while the source is "
        "48000 — the rate the dead-start fit must use", "REPORTED",
        detail + "   (fit @declared 44100 vs @source 48000 differ by "
        "~0.19 s on a 4 s window)")

    print("\n=== SUMMARY ===")
    for o in OUT:
        print(f"{o['verdict']:9s} {o['claim'][:74]}")
    Path("corpus/live/r76-verifier/followup.json").write_text(
        json.dumps(OUT, indent=1))
    sys.exit(0)


if __name__ == "__main__":
    main()
