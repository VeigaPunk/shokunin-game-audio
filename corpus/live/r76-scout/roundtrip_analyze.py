#!/usr/bin/env python3
"""r76-scout roundtrip analysis v2 (scratch): decode with ffmpeg (tolerant of
unfinalized headers), then compare envelope + centroid of the monitor capture
against the played source member."""
import json
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/artifacts/stem_sections.wav")
CAPS = ["legs/rt-ffmpeg-mon.wav", "legs/rt-ffmpeg-mon2.wav",
        "legs/rt-parec-mon.wav", "legs/rt-pwrec-mon.wav"]


def decode(path, sr=48000):
    """ffmpeg-decode any container to mono s16le @ sr (tolerates bad headers)."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1",
                        "-ar", str(sr), "-f", "s16le", "-"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    a = np.frombuffer(p.stdout, dtype="<i2").astype(np.float64)
    return a, sr, p.stderr.decode("utf-8", "replace").strip()


def envelope(a, sr, win=0.25):
    step = int(sr * win)
    return [round(float(np.sqrt(np.mean(a[i:i + step] ** 2))), 1)
            for i in range(0, len(a) - step + 1, step)]


def centroid(a, sr, lo=0.6, hi=4.0):
    seg = a[int(lo * sr):int(hi * sr)]
    if len(seg) < 1024:
        return None
    w = np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(seg * w))
    freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
    return round(float((spec * freqs).sum() / spec.sum()), 1)


def peak_dbfs(a):
    p = np.max(np.abs(a)) / 32768.0
    return round(20 * float(np.log10(p)), 2) if p > 0 else None


out = {}
sa, ssr, _ = decode(SRC)
out["source"] = {"path": str(SRC), "duration_s": round(len(sa) / ssr, 3),
                 "peak_dbfs": peak_dbfs(sa), "centroid_hz": centroid(sa, ssr),
                 "envelope_rms": envelope(sa, ssr)}
for cap in CAPS:
    p = HERE / cap
    if not p.exists():
        out[cap] = {"absent": True}
        continue
    a, sr, err = decode(p)
    out[cap] = {"duration_s": round(len(a) / sr, 3),
                "peak_dbfs": peak_dbfs(a), "centroid_hz": centroid(a, sr),
                "envelope_rms": envelope(a, sr),
                "decode_stderr": err[:200]}
(HERE / "runs").mkdir(exist_ok=True)
(HERE / "runs" / "roundtrip-analysis.json").write_text(json.dumps(out, indent=1) + "\n")
for k, v in out.items():
    print("%-26s dur=%-7s peak=%-8s centroid=%-9s" % (
        k, v.get("duration_s"), v.get("peak_dbfs"), v.get("centroid_hz")))
print("\nenvelopes (0.25 s RMS windows, int16 counts):")
for k, v in out.items():
    print(" %-26s %s" % (k, v.get("envelope_rms")))
