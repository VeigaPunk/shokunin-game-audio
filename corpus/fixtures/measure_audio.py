#!/usr/bin/env python3
"""Headless checks of deterministic WAV fixtures; JSON receipt even on failure."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
SPECS = {
    "ui": (.12, 250, 4000, False),
    "ui_alt": (.16, 250, 4000, False),
    "impact": (.32, 50, 15000, False),
    "impact_alt": (.32, 50, 15000, False),
    "movement": (.24, 100, 16000, False),
    "movement_alt": (.36, 100, 16000, False),
    "ambience": (2.0, 5, 200, True),
    "ambience_alt": (2.0, 5, 200, True),
    "stem": (2.0, 100, 2000, True),
}


def command(*args):
    return subprocess.run(args, check=True, capture_output=True)


def measure(name, spec):
    path = ARTIFACTS / (name + ".wav")
    probe = json.loads(command("ffprobe", "-v", "error", "-show_entries",
                               "stream=sample_rate,channels:format=duration", "-of", "json", str(path)).stdout)
    stream = probe["streams"][0]
    rate = int(stream["sample_rate"])
    pcm = command("sox", str(path), "-t", "f32", "-e", "floating-point", "-").stdout
    samples = np.frombuffer(pcm, dtype="<f4").astype(np.float64)
    duration = float(probe["format"]["duration"])
    # Weighted positive-frequency centroid on the entire waveform; no claim of timbre.
    spectrum = np.abs(np.fft.rfft(samples))
    freqs = np.fft.rfftfreq(len(samples), 1/rate)
    centroid = float(np.dot(freqs, spectrum) / spectrum.sum())
    bandwidth = float(np.sqrt(np.dot((freqs-centroid)**2, spectrum) / spectrum.sum()))
    rms = float(np.sqrt(np.mean(samples**2)))
    peak = float(np.max(np.abs(samples)))
    # ebur128 integrated loudness is undefined on quiet/low-frequency signals;
    # report both the measured LUFS (if finite) and RMS dBFS, never conflate them.
    loud = command("ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                   "-filter_complex", "ebur128=peak=true", "-f", "null", "-").stderr.decode()
    matches = re.findall(r"Integrated loudness:\s*I:\s*([+\-]?(?:\d+(?:\.\d+)?|inf)) LUFS", loud)
    lufs = float(matches[-1]) if matches else None
    # -70 LUFS is ebur128's gated floor, not a useful short-SFX level.
    if lufs is not None and (not np.isfinite(lufs) or lufs <= -70):
        lufs = None
    seam_delta = float(abs(samples[0] - samples[-1])) if spec[3] else None
    failures = []
    if rate != 48000 or int(stream["channels"]) != 1:
        failures.append("format: expected 48kHz mono")
    if abs(duration-spec[0]) > .001:
        failures.append("duration: outside ±1 ms")
    if peak >= .95 or rms < .001:
        failures.append("level: clipping headroom or near silence")
    if not spec[1] <= centroid <= spec[2]:
        failures.append("spectrum: centroid outside fixture band")
    if spec[3] and seam_delta > .03:
        failures.append("loop seam: endpoint jump > .03 full scale")
    return {"path": str(path.relative_to(ROOT)), "duration_s": duration,
            "sample_rate_hz": rate, "channels": int(stream["channels"]),
            "peak_full_scale": peak, "rms_dbfs": float(20*np.log10(rms)),
            "integrated_lufs": lufs if np.isfinite(lufs if lufs is not None else float("nan")) else None,
            "spectral_centroid_hz": centroid, "spectral_bandwidth_hz": bandwidth,
            "seam_endpoint_delta_full_scale": seam_delta, "failures": failures}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-failing", action="store_true")
    args = parser.parse_args()
    command(sys.executable, str(Path(__file__).with_name("build_artifacts.py")),
            *(["--probe-failing"] if args.probe_failing else []))
    measurements = {name: measure(name, spec) for name, spec in SPECS.items()}
    distinctness = {}
    for name, variant in measurements.items():
        if not name.endswith("_alt"):
            continue
        base = measurements[name[:-4]]
        duration_delta = abs(variant["duration_s"] - base["duration_s"])
        centroid_relative_delta = abs(variant["spectral_centroid_hz"] - base["spectral_centroid_hz"]) / base["spectral_centroid_hz"]
        passed = duration_delta >= .020 or centroid_relative_delta >= .10
        distinctness[name] = {"baseline": name[:-4], "duration_delta_s": duration_delta,
                              "centroid_relative_delta": centroid_relative_delta, "passed": passed}
        if not passed:
            variant["failures"].append("distinctness: duration < .020 s and centroid delta < 10%")
    receipt = {"mode": "probe-failing" if args.probe_failing else "normal",
               "thresholds": {"rate_hz": 48000, "duration_tolerance_s": .001,
                              "peak_max_exclusive": .95, "rms_min_exclusive": .001,
                              "loop_endpoint_delta_max": .03,
                              "distinctness_duration_delta_min_s": .020,
                              "distinctness_centroid_relative_delta_min": .10,
                              "centroid_bands_hz": {k: [v[1], v[2]] for k,v in SPECS.items()}},
               "measurements": measurements, "distinctness": distinctness}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = ROOT / "live" / "runs" / (stamp + ("-failing" if args.probe_failing else "-normal"))
    out.mkdir(parents=True)
    (out / "measurements.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    failed = {k: v["failures"] for k,v in measurements.items() if v["failures"]}
    print(json.dumps({"receipt": str(out / "measurements.json"), "failures": failed}))
    return bool(failed)


if __name__ == "__main__":
    sys.exit(main())
