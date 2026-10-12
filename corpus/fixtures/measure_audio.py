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
    "stem_sections": (4.0, 100, 2000, True),
    "stem_layer": (4.0, 100, 2000, True),
    "stem_layer_alt": (4.0, 100, 2000, True),
    "stem_layer_third": (4.0, 100, 2000, True),
}


def command(*args):
    return subprocess.run(args, check=True, capture_output=True)


def measure(name, spec, path=None):
    path = path or ARTIFACTS / (name + ".wav")
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
    slope_delta = float(abs((samples[-1] - samples[-2]) - (samples[1] - samples[0]))) if spec[3] else None
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
    if spec[3] and slope_delta > .001:
        failures.append("loop seam: slope mismatch > .001 full scale per sample")
    return {"path": str(path.relative_to(ROOT)), "duration_s": duration,
            "sample_rate_hz": rate, "channels": int(stream["channels"]),
            "peak_full_scale": peak, "rms_dbfs": float(20*np.log10(rms)),
            "integrated_lufs": lufs if np.isfinite(lufs if lufs is not None else float("nan")) else None,
            "spectral_centroid_hz": centroid, "spectral_bandwidth_hz": bandwidth,
            "seam_endpoint_delta_full_scale": seam_delta,
            "seam_slope_delta_full_scale_per_sample": slope_delta, "failures": failures}


def section_contrast(path, component_hz=30):
    raw = command("sox", str(path), "-t", "f32", "-e", "floating-point", "-").stdout
    samples = np.frombuffer(raw, dtype="<f4").astype(np.float64)
    if len(samples) != 192000:
        return {"component_hz": component_hz, "section_samples": 96000,
                "actual_samples": len(samples), "component_amplitudes_full_scale": [],
                "section_rms_full_scale": [], "component_amplitude_contrast_db": None,
                "internal_join_adjacent_delta_full_scale": None,
                "internal_join_side_slope_mismatch_full_scale_per_sample": None,
                "valid": False, "passed": False, "failure_kind": "section count"}
    halves = np.split(samples, 2)
    component_bin = component_hz * len(halves[0]) // 48000
    amps = [float(2 * abs(np.fft.rfft(half)[component_bin]) / len(half)) for half in halves]
    rms = [float(np.sqrt(np.mean(half**2))) for half in halves]
    valid = all(np.isfinite(amps)) and all(a >= .01 for a in amps) and all(r >= .001 for r in rms)
    delta_db = float(20*np.log10(amps[1]/amps[0])) if valid else None
    join_delta = float(abs(samples[96000] - samples[95999]))
    join_slope = float(abs((samples[96001] - samples[96000]) - (samples[95999] - samples[95998])))
    return {"component_hz": component_hz, "section_samples": 96000, "component_amplitudes_full_scale": amps,
            "section_rms_full_scale": rms, "component_amplitude_contrast_db": delta_db,
            "internal_join_adjacent_delta_full_scale": join_delta,
            "internal_join_side_slope_mismatch_full_scale_per_sample": join_slope,
            "valid": valid, "passed": bool(valid and delta_db >= 6.0)}


def invalid_probes():
    probes = ROOT / "live" / "round-6"
    results = []
    for name, expected in (("short_sections", "section count"),
                           ("corrupt", "decode"), ("wrong_format", "format"),
                           ("odd_sections", "section count")):
        path = (ROOT / "live" / "round-7" if name == "odd_sections" else probes) / (name + ".wav")
        result = {"probe": name, "path": str(path.relative_to(ROOT)),
                  "expected_failure": expected, "observed_failure": None}
        if name == "corrupt":
            try:
                command("ffprobe", "-v", "error", "-show_entries",
                        "stream=sample_rate,channels:format=duration", "-of", "json", str(path))
            except subprocess.CalledProcessError as exc:
                result["observed_failure"] = "decode"
                result["detail"] = {"tool": "ffprobe", "exit_code": exc.returncode,
                                    "stderr": exc.stderr.decode(errors="replace").strip()}
        elif name == "wrong_format":
            probe = json.loads(command("ffprobe", "-v", "error", "-show_entries",
                                       "stream=sample_rate,channels:format=duration", "-of", "json", str(path)).stdout)
            stream = probe["streams"][0]
            result["sample_rate_hz"] = int(stream["sample_rate"])
            result["channels"] = int(stream["channels"])
            if result["sample_rate_hz"] != 48000 or result["channels"] != 1:
                result["observed_failure"] = "format"
        else:
            section = section_contrast(path)
            result["section"] = section
            if section.get("failure_kind") == "section count":
                result["observed_failure"] = "section count"
        result["status"] = ("expected_failure" if result["observed_failure"] == expected
                            else "unexpected_result")
        results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-failing", action="store_true")
    parser.add_argument("--probe-slope", action="store_true")
    parser.add_argument("--probe-flat", action="store_true")
    parser.add_argument("--probe-layer-flat", action="store_true")
    parser.add_argument("--probe-layer-join", action="store_true")
    parser.add_argument("--probe-layer-slope", action="store_true")
    parser.add_argument("--probe-layer-alt-flat", action="store_true")
    parser.add_argument("--probe-layer-alt-join", action="store_true")
    parser.add_argument("--probe-layer-alt-slope", action="store_true")
    parser.add_argument("--probe-layer-alt-reverse", action="store_true")
    parser.add_argument("--probe-layer-third-slope", action="store_true")
    parser.add_argument("--probe-layer-third-slope-edge-pass", action="store_true")
    parser.add_argument("--probe-layer-third-slope-edge-fail", action="store_true")
    parser.add_argument("--probe-invalid", action="store_true")
    args = parser.parse_args()
    if sum([args.probe_slope, args.probe_failing, args.probe_flat, args.probe_layer_flat, args.probe_layer_join, args.probe_layer_slope, args.probe_layer_alt_flat, args.probe_layer_alt_join, args.probe_layer_alt_slope, args.probe_layer_alt_reverse, args.probe_layer_third_slope, args.probe_layer_third_slope_edge_pass, args.probe_layer_third_slope_edge_fail, args.probe_invalid]) > 1:
        parser.error("choose one probe mode")
    if args.probe_invalid:
        command(sys.executable, str(Path(__file__).with_name("build_artifacts.py")), "--probe-invalid")
        results = invalid_probes()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        out = ROOT / "live" / "runs" / (stamp + "-invalid")
        out.mkdir(parents=True)
        (out / "measurements.json").write_text(json.dumps({"mode": "probe-invalid", "invalid_probes": results}, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"receipt": str(out / "measurements.json"),
                          "failures": {r["probe"]: r["observed_failure"] for r in results}}))
        return 1 if all(r["status"] == "expected_failure" for r in results) else 2
    command(sys.executable, str(Path(__file__).with_name("build_artifacts.py")),
            *(["--probe-failing"] if args.probe_failing else []),
            *(["--probe-slope"] if args.probe_slope else []),
            *(["--probe-flat"] if args.probe_flat else []),
            *(["--probe-layer-flat"] if args.probe_layer_flat else []),
            *(["--probe-layer-join"] if args.probe_layer_join else []),
            *(["--probe-layer-slope"] if args.probe_layer_slope else []),
            *(["--probe-layer-alt-flat"] if args.probe_layer_alt_flat else []),
            *(["--probe-layer-alt-join"] if args.probe_layer_alt_join else []),
            *(["--probe-layer-alt-slope"] if args.probe_layer_alt_slope else []),
            *(["--probe-layer-alt-reverse"] if args.probe_layer_alt_reverse else []),
            *(["--probe-layer-third-slope"] if args.probe_layer_third_slope else []),
            *(["--probe-layer-third-slope-edge-pass"] if args.probe_layer_third_slope_edge_pass else []),
            *(["--probe-layer-third-slope-edge-fail"] if args.probe_layer_third_slope_edge_fail else []))
    measurements = {name: measure(name, spec) for name, spec in SPECS.items()}
    if args.probe_slope:
        path = ROOT / "live" / "round-3" / "slope_probe.wav"
        measurements["slope_probe"] = measure("slope_probe", (1.0, 5, 24000, True), path)
    if args.probe_flat:
        path = ROOT / "live" / "round-4" / "flat30_probe.wav"
        measurements["flat30_probe"] = measure("flat30_probe", SPECS["stem_sections"], path)
    if args.probe_layer_flat:
        path = ROOT / "live" / "round-8" / "flat120_probe.wav"
        measurements["flat120_probe"] = measure("flat120_probe", SPECS["stem_layer"], path)
    if args.probe_layer_join:
        path = ROOT / "live" / "round-10" / "join_probe.wav"
        measurements["join_probe"] = measure("join_probe", SPECS["stem_layer"], path)
    if args.probe_layer_slope:
        path = ROOT / "live" / "round-11" / "slope_probe.wav"
        measurements["layer_slope_probe"] = measure("layer_slope_probe", SPECS["stem_layer"], path)
    if args.probe_layer_alt_flat:
        path = ROOT / "live" / "round-13" / "flat180_probe.wav"
        measurements["flat180_probe"] = measure("flat180_probe", SPECS["stem_layer_alt"], path)
    if args.probe_layer_alt_join:
        path = ROOT / "live" / "round-14" / "join180_probe.wav"
        measurements["join180_probe"] = measure("join180_probe", SPECS["stem_layer_alt"], path)
    if args.probe_layer_alt_slope:
        path = ROOT / "live" / "round-15" / "slope180_probe.wav"
        measurements["slope180_probe"] = measure("slope180_probe", SPECS["stem_layer_alt"], path)
    if args.probe_layer_alt_reverse:
        path = ROOT / "live" / "round-16" / "reverse180_probe.wav"
        measurements["reverse180_probe"] = measure("reverse180_probe", SPECS["stem_layer_alt"], path)
    if args.probe_layer_third_slope:
        path = ROOT / "live" / "round-18" / "slope200_probe.wav"
        measurements["slope200_probe"] = measure("slope200_probe", SPECS["stem_layer_third"], path)
    if args.probe_layer_third_slope_edge_pass or args.probe_layer_third_slope_edge_fail:
        name = "edgepass_probe" if args.probe_layer_third_slope_edge_pass else "edgefail_probe"
        path = ROOT / "live" / "round-19" / (name + ".wav")
        measurements[name] = measure(name, SPECS["stem_layer_third"], path)
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
    sections = {name: section_contrast(ROOT / data["path"], 200 if name in ("stem_layer_third", "slope200_probe", "edgepass_probe", "edgefail_probe") else
                                       180 if name in ("stem_layer_alt", "flat180_probe", "join180_probe", "slope180_probe", "reverse180_probe") else
                                       120 if name in ("stem_layer", "flat120_probe", "join_probe", "layer_slope_probe") else 30)
                for name, data in measurements.items()
                if name in ("stem_sections", "flat30_probe", "stem_layer", "stem_layer_alt", "stem_layer_third", "slope200_probe", "edgepass_probe", "edgefail_probe", "flat120_probe", "flat180_probe", "join180_probe", "slope180_probe", "reverse180_probe", "join_probe", "layer_slope_probe")}
    for name, result in sections.items():
        if not result["passed"]:
            measurements[name]["failures"].append(f"sections: {result['component_hz']} Hz component amplitude contrast < 6 dB or invalid")
        if name in ("stem_layer", "stem_layer_alt", "stem_layer_third", "slope200_probe", "edgepass_probe", "edgefail_probe", "flat180_probe", "join180_probe", "slope180_probe", "reverse180_probe", "join_probe", "layer_slope_probe") and result["internal_join_adjacent_delta_full_scale"] is not None and result["internal_join_adjacent_delta_full_scale"] > .03:
            measurements[name]["failures"].append("sections: internal join adjacent sample gap > .03 full scale")
        if name in ("stem_layer", "stem_layer_alt", "stem_layer_third", "slope200_probe", "edgepass_probe", "edgefail_probe", "flat180_probe", "join180_probe", "slope180_probe", "reverse180_probe", "layer_slope_probe") and result["internal_join_side_slope_mismatch_full_scale_per_sample"] is not None and result["internal_join_side_slope_mismatch_full_scale_per_sample"] > .001:
            measurements[name]["failures"].append("sections: internal join side slope mismatch > .001 full scale per sample")
    mode = "probe-layer-third-slope-edge-pass" if args.probe_layer_third_slope_edge_pass else ("probe-layer-third-slope-edge-fail" if args.probe_layer_third_slope_edge_fail else "probe-layer-third-slope" if args.probe_layer_third_slope else ("probe-layer-alt-reverse" if args.probe_layer_alt_reverse else ("probe-layer-alt-slope" if args.probe_layer_alt_slope else ("probe-layer-alt-join" if args.probe_layer_alt_join else ("probe-layer-alt-flat" if args.probe_layer_alt_flat else ("probe-layer-slope" if args.probe_layer_slope else ("probe-layer-join" if args.probe_layer_join else ("probe-layer-flat" if args.probe_layer_flat else ("probe-flat" if args.probe_flat else ("probe-slope" if args.probe_slope else ("probe-failing" if args.probe_failing else "normal")))))))))))
    receipt = {"mode": mode,
               "thresholds": {"rate_hz": 48000, "duration_tolerance_s": .001,
                              "peak_max_exclusive": .95, "rms_min_exclusive": .001,
                              "loop_endpoint_delta_max": .03,
                              "loop_slope_delta_max_full_scale_per_sample": .001,
                              "section_contrast_min_db": 6.0,
                              "internal_join_adjacent_delta_max_full_scale": .03,
                              "internal_join_side_slope_mismatch_max_full_scale_per_sample": .001,
                              "section_component_amplitude_min_full_scale": .01,
                              "section_rms_min_full_scale": .001,
                              "distinctness_duration_delta_min_s": .020,
                              "distinctness_centroid_relative_delta_min": .10,
                              "centroid_bands_hz": {k: [v[1], v[2]] for k,v in SPECS.items()}},
               "measurements": measurements, "distinctness": distinctness,
               "sections": sections}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    suffix = "-layer-third-slope-edge-pass" if args.probe_layer_third_slope_edge_pass else ("-layer-third-slope-edge-fail" if args.probe_layer_third_slope_edge_fail else "-layer-third-slope" if args.probe_layer_third_slope else ("-layer-alt-reverse" if args.probe_layer_alt_reverse else ("-layer-alt-slope" if args.probe_layer_alt_slope else ("-layer-alt-join" if args.probe_layer_alt_join else ("-layer-alt-flat" if args.probe_layer_alt_flat else ("-layer-slope" if args.probe_layer_slope else ("-layer-join" if args.probe_layer_join else ("-layer-flat" if args.probe_layer_flat else ("-flat" if args.probe_flat else ("-slope" if args.probe_slope else ("-failing" if args.probe_failing else "-normal")))))))))))
    out = ROOT / "live" / "runs" / (stamp + suffix)
    out.mkdir(parents=True)
    (out / "measurements.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    failed = {k: v["failures"] for k,v in measurements.items() if v["failures"]}
    print(json.dumps({"receipt": str(out / "measurements.json"), "failures": failed}))
    return bool(failed)


if __name__ == "__main__":
    sys.exit(main())
