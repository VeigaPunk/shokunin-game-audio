#!/usr/bin/env python3
"""Headless checks of deterministic WAV fixtures; JSON receipt even on failure."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
SPECS = {
    "ui": (.12, 250, 4000, False),
    "ui_alt": (.16, 250, 4000, False),
    "ui_third": (.20, 250, 4000, False),
    "impact": (.32, 50, 15000, False),
    "impact_alt": (.32, 50, 15000, False),
    "impact_third": (.40, 50, 15000, False),
    "movement": (.24, 100, 16000, False),
    "movement_alt": (.36, 100, 16000, False),
    "movement_third": (.30, 100, 16000, False),
    "ambience": (2.0, 5, 200, True),
    "ambience_alt": (2.0, 5, 200, True),
    "ambience_third": (2.0, 5, 200, True),
    "stem": (2.0, 100, 2000, True),
    "stem_sections": (4.0, 100, 2000, True),
    "stem_layer": (4.0, 100, 2000, True),
    "stem_layer_alt": (4.0, 100, 2000, True),
    "stem_layer_third": (4.0, 100, 2000, True),
}


def command(*args):
    return subprocess.run(args, check=True, capture_output=True)


def format_failures(stream):
    failures = []
    if int(stream["sample_rate"]) != 48000 or int(stream["channels"]) != 1:
        failures.append("format: expected 48kHz mono")
    if stream.get("codec_name") != "pcm_s16le" or stream.get("bits_per_sample") != 16:
        failures.append("format: expected PCM16")
    return failures


def measure(name, spec, path=None):
    path = path or ARTIFACTS / (name + ".wav")
    probe = json.loads(command("ffprobe", "-v", "error", "-show_entries",
                               "stream=sample_rate,channels,codec_name,bits_per_sample:format=duration", "-of", "json", str(path)).stdout)
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
    failures.extend(format_failures(stream))
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
            "codec_name": stream.get("codec_name"), "bits_per_sample": stream.get("bits_per_sample"),
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
                           ("odd_sections", "section count"),
                           ("native16_probe", None), ("native24_probe", "format"),
                           ("stereo48_probe", "format"), ("mono441_probe", "format")):
        directory = (ROOT / "live" / "round-25" if name in ("stereo48_probe", "mono441_probe") else
                     ROOT / "live" / "round-22" if name.startswith("native") else
                     ROOT / "live" / "round-7" if name == "odd_sections" else probes)
        path = directory / (name + ".wav")
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
        elif name in ("wrong_format", "native16_probe", "native24_probe", "stereo48_probe", "mono441_probe"):
            probe = json.loads(command("ffprobe", "-v", "error", "-show_entries",
                                       "stream=sample_rate,channels,codec_name,bits_per_sample:format=duration",
                                       "-of", "json", str(path)).stdout)
            stream = probe["streams"][0]
            result["sample_rate_hz"] = int(stream["sample_rate"])
            result["channels"] = int(stream["channels"])
            result["codec_name"] = stream.get("codec_name")
            result["bits_per_sample"] = stream.get("bits_per_sample")
            if format_failures(stream):
                result["observed_failure"] = "format"
        else:
            section = section_contrast(path)
            result["section"] = section
            if section.get("failure_kind") == "section count":
                result["observed_failure"] = "section count"
        result["status"] = ("expected_pass" if expected is None and result["observed_failure"] is None else
                            "expected_failure" if expected is not None and result["observed_failure"] == expected else
                            "unexpected_result")
        results.append(result)
    return results


# r67 transport axis: the 2x2 transport space {named x seekable}. Every prior
# ledger row ran the `file` arm implicitly; this arm records transport
# explicitly per member. The member set is the complete tracked autodetect
# family (r65 preempt + r66 dec/lengate members) — every member whose route
# is a detection decision.
TRANSPORT_R67_ARMS = (("file", True, True), ("stdin_pipe", False, False),
                      ("redirected_fd", False, True), ("fifo_path", True, False))
TRANSPORT_R67_MEMBERS = {
    "preempt_act": ("round-65", "pair_preempt_act.wav"),
    "preempt_gsrt": ("round-65", "pair_preempt_gsrt.wav"),
    "preempt_hcom": ("round-65", "pair_preempt_hcom.wav"),
    "preempt_both": ("round-65", "pair_preempt_both.wav"),
    "dec_hcom": ("round-66", "pair_dec_hcom.wav"),
    "dec_act": ("round-66", "pair_dec_act.wav"),
    "lengate_gsrt_24": ("round-66", "pair_lengate_gsrt_24.wav"),
    "lengate_gsrt_25": ("round-66", "pair_lengate_gsrt_25.wav"),
    "lengate_hcom_131": ("round-66", "pair_lengate_hcom_131.wav"),
    "lengate_hcom_132": ("round-66", "pair_lengate_hcom_132.wav"),
}
TRANSPORT_R67_ARM_TIMEOUT_S = 10
# The ffmpeg bridge re-opens the input by name (open #2); on a fifo that open
# blocks unless a writer is still attached. The feed below writes the member
# once then lingers this long holding the fifo open, so the bridge's second
# open resolves deterministically to the truncated-stream verdict instead of
# racing the writer's exit. Native readers see EOF when the writer closes.
TRANSPORT_R67_FIFO_WRITER_HOLD_S = 1.0
# r68 post-table fallback axis: members whose verdict exercises the path
# AFTER the CHECK table returns NULL (posttable_nomatch) or a reader-level
# !seekable gate downstream of a real detection (txw_piperefuse). The .wav
# extension on posttable_nomatch is part of the member contract — the
# post-table fallback is lsx_find_file_extension(path), so named arms route
# to the wav reader while anonymous '-' arms can't determine a type.
TRANSPORT_R68_MEMBERS = {
    "posttable_nomatch": ("round-68", "posttable_nomatch.wav"),
    "txw_piperefuse": ("round-68", "txw_piperefuse.wav"),
}
# r69 extension-suffix axis: ONE no-match byte buffer under five names.
# Inside the named arm the extension alone selects the post-table handler
# (wav reader / no-handler / txw reader / f32 raw decode); the .snd name is
# the only member whose DETECTION fires — the ext-gated sndr CHECK row
# (formats.c:247-248) matches \0\0@0 ^ \0@7 — so detection itself, not just
# the decode verdict, forks on transport name. All five files carry
# identical bytes (sha256 f073e70a…); anonymous '-' arms have no extension
# and stay can't-determine on every member.
TRANSPORT_R69_MEMBERS = {
    "extsuffix_wav": ("round-69", "extsuffix_nomatch.wav"),
    "extsuffix_bin": ("round-69", "extsuffix_nomatch.bin"),
    "extsuffix_txw": ("round-69", "extsuffix_nomatch.txw"),
    "extsuffix_f32": ("round-69", "extsuffix_nomatch.f32"),
    "extsuffix_snd": ("round-69", "extsuffix_nomatch.snd"),
}


def transport_error(text):
    """Normalized verdict: message after the input-name close-quote on the last
    `sox FAIL` line; None when no FAIL line (decode produced samples)."""
    fails = [line for line in text.strip().splitlines() if "sox FAIL" in line]
    if not fails:
        return None
    match = re.search(r"':\s*(.*)$", fails[-1])
    return match.group(1) if match else fails[-1]


def transport_leg(args, label, data=None, stdin=None):
    """One bounded `sox -V6 <input> -n stat` leg -> detection+decode verdict."""
    kw = {"input": data} if data is not None else ({"stdin": stdin} if stdin else {})
    try:
        proc = subprocess.run(args, capture_output=True,
                              timeout=TRANSPORT_R67_ARM_TIMEOUT_S, **kw)
        text = proc.stderr.decode(errors="replace")
        code = proc.returncode
        error = transport_error(text)
    except subprocess.TimeoutExpired as exc:
        text = (exc.stderr or b"").decode(errors="replace")
        code = None
        error = f"blocked: no verdict within {TRANSPORT_R67_ARM_TIMEOUT_S} s"
    detected = re.search(r"detected file format type `(\S+?)'", text)
    read = re.search(r"Samples read:\s*(\d+)", text)
    leg = {"input": label,
           "sox_detected_format": detected.group(1) if detected else None,
           "sox_route": ("ffmpeg" if (detected and detected.group(1) == "act")
                         or "(ffmpeg)" in text else "native" if detected else "none"),
           "exit_code": code,
           "samples_read": int(read.group(1)) if read else None,
           "error": error}
    tail = text.strip().splitlines()
    if tail:
        # ASLR context addresses and the concrete input path are stripped so
        # the receipt stays byte-deterministic across transports and runs.
        leg["stderr_tail"] = re.sub(r"`[^']*'", "`<input>'",
                                    re.sub(r" @ 0x[0-9a-f]+\]", "]", tail[-1]))[-160:]
    return leg


def transport_matrix(path):
    """The member's detection+decode verdict on each of the four transports."""
    arms = {}
    arms["file"] = transport_leg(["sox", "-V6", str(path), "-n", "stat"],
                                 str(path.relative_to(ROOT)))
    arms["stdin_pipe"] = transport_leg(["sox", "-V6", "-", "-n", "stat"], "-",
                                       data=path.read_bytes())
    with path.open("rb") as fh:
        arms["redirected_fd"] = transport_leg(["sox", "-V6", "-", "-n", "stat"],
                                              "-", stdin=fh)
    with tempfile.TemporaryDirectory(prefix="transport-r67-") as tmp:
        fifo = Path(tmp) / path.name
        os.mkfifo(fifo)

        def feed():
            try:
                with fifo.open("wb") as fh:
                    fh.write(path.read_bytes())
                    fh.flush()
                    time.sleep(TRANSPORT_R67_FIFO_WRITER_HOLD_S)
            except OSError:
                pass

        writer = threading.Thread(target=feed, daemon=True)
        writer.start()
        try:
            arms["fifo_path"] = transport_leg(["sox", "-V6", str(fifo), "-n", "stat"],
                                              path.name)
        finally:
            writer.join(timeout=TRANSPORT_R67_FIFO_WRITER_HOLD_S + 5)
    for transport, named, seekable in TRANSPORT_R67_ARMS:
        arms[transport]["named"] = named
        arms[transport]["seekable"] = seekable
    return arms


def transport_entry(member, path):
    """Receipt entry: transport axis matrix + verdict groups + fork pin."""
    arms = transport_matrix(path)
    groups = []
    for transport in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
        arm = arms[transport]
        signature = (arm["sox_detected_format"], arm["sox_route"], arm["exit_code"],
                     arm["samples_read"], arm["error"])
        for group in groups:
            if group[0] == signature:
                group[1].append(transport)
                break
        else:
            groups.append((signature, [transport]))
    entry = {"path": str(path.relative_to(ROOT)), "pair_member": member,
             "transport_axis": arms,
             "transport_protocol": {"arm_timeout_s": TRANSPORT_R67_ARM_TIMEOUT_S,
                                    "fifo_writer_hold_s": TRANSPORT_R67_FIFO_WRITER_HOLD_S,
                                    "fifo_feed": "one-shot write then writer lingers"},
             "transport_verdict_groups": [
                 {"transports": ts, "sox_detected_format": sig[0], "sox_route": sig[1],
                  "exit_code": sig[2], "samples_read": sig[3], "error": sig[4]}
                 for sig, ts in groups],
             "transport_fork": len(groups) > 1,
             "failures": []}
    if entry["transport_fork"]:
        desc = " vs ".join("/".join(ts) + "=" + (sig[4] or f"decode {sig[3]} samples")
                           for sig, ts in groups)
        entry["failures"].append(f"transport: detection+decode verdict forks across transports ({desc})")
    return entry


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
    parser.add_argument("--probe-layer-third-join", action="store_true")
    parser.add_argument("--probe-layer-third-join-edge-pass", action="store_true")
    parser.add_argument("--probe-layer-third-join-edge-fail", action="store_true")
    parser.add_argument("--probe-invalid", action="store_true")
    parser.add_argument("--probe-ui-clone", action="store_true")
    parser.add_argument("--probe-ui-duration-below", action="store_true")
    parser.add_argument("--probe-ui-duration-at", action="store_true")
    parser.add_argument("--probe-ui-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-lower-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-lower-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-orientation-forward", action="store_true")
    parser.add_argument("--probe-ui-orientation-reverse", action="store_true")
    parser.add_argument("--probe-ui-joint-below", action="store_true")
    parser.add_argument("--probe-ui-mixed-pass", action="store_true")
    parser.add_argument("--probe-ambience-centroid-below", action="store_true")
    parser.add_argument("--probe-ambience-centroid-above", action="store_true")
    parser.add_argument("--probe-ambience-orientation-forward", action="store_true")
    parser.add_argument("--probe-ambience-orientation-reverse", action="store_true")
    parser.add_argument("--probe-outer-endpoint-983", action="store_true")
    parser.add_argument("--probe-outer-endpoint-984", action="store_true")
    parser.add_argument("--probe-outer-slope-32", action="store_true")
    parser.add_argument("--probe-outer-slope-33", action="store_true")
    parser.add_argument("--probe-ui-peak-31129", action="store_true")
    parser.add_argument("--probe-ui-peak-31130", action="store_true")
    parser.add_argument("--probe-ui-crest-46", action="store_true")
    parser.add_argument("--probe-ui-crest-47", action="store_true")
    parser.add_argument("--probe-ui-tolerance-5807", action="store_true")
    parser.add_argument("--probe-ui-tolerance-5809", action="store_true")
    parser.add_argument("--probe-ui-lower-tolerance-5713", action="store_true")
    parser.add_argument("--probe-ui-lower-tolerance-5711", action="store_true")
    parser.add_argument("--probe-ui-absolute-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-absolute-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-upper-centroid-below", action="store_true")
    parser.add_argument("--probe-ui-upper-centroid-above", action="store_true")
    parser.add_argument("--probe-ui-rate-47999", action="store_true")
    parser.add_argument("--probe-ui-rate-48000", action="store_true")
    parser.add_argument("--probe-ui-rate-48001", action="store_true")
    parser.add_argument("--probe-ui-rate-48000-r49", action="store_true")
    parser.add_argument("--probe-ui-channel-stereo", action="store_true")
    parser.add_argument("--probe-ui-channel-mono", action="store_true")
    parser.add_argument("--probe-ui-pcm24", action="store_true")
    parser.add_argument("--probe-ui-pcm16", action="store_true")
    parser.add_argument("--probe-ui-pcm8", action="store_true")
    parser.add_argument("--probe-ui-pcm16-r52", action="store_true")
    parser.add_argument("--probe-ui-float32", action="store_true")
    parser.add_argument("--probe-ui-pcm16-r53", action="store_true")
    parser.add_argument("--probe-ui-pcm32", action="store_true")
    parser.add_argument("--probe-ui-pcm16-r54", action="store_true")
    parser.add_argument("--probe-ui-extensible-pcm16", action="store_true")
    parser.add_argument("--probe-ui-standard-pcm16-r55", action="store_true")
    parser.add_argument("--probe-ui-extensible-mask-zero", action="store_true")
    parser.add_argument("--probe-ui-extensible-mask-center", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-15", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-16", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-14-r58", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-16-r58", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-13-r59", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-16-r59", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-0-r60", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-16-r60", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-17-r61", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-16-r61", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-24-r62", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-32-r62", action="store_true")
    parser.add_argument("--probe-ui-route-act-84-r63", action="store_true")
    parser.add_argument("--probe-ui-route-act-00-r63", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-8-r64", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-9-r64", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-24-r64", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-25-r64", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-56-r64", action="store_true")
    parser.add_argument("--probe-ui-extensible-valid-57-r64", action="store_true")
    parser.add_argument("--probe-ui-preempt-act-r65", action="store_true")
    parser.add_argument("--probe-ui-preempt-gsrt-r65", action="store_true")
    parser.add_argument("--probe-ui-preempt-hcom-r65", action="store_true")
    parser.add_argument("--probe-ui-preempt-both-r65", action="store_true")
    parser.add_argument("--probe-ui-dec-hcom-r66", action="store_true")
    parser.add_argument("--probe-ui-dec-act-r66", action="store_true")
    parser.add_argument("--probe-ui-lengate-gsrt-24-r66", action="store_true")
    parser.add_argument("--probe-ui-lengate-gsrt-25-r66", action="store_true")
    parser.add_argument("--probe-ui-lengate-hcom-131-r66", action="store_true")
    parser.add_argument("--probe-ui-lengate-hcom-132-r66", action="store_true")
    parser.add_argument("--probe-transport-preempt-act-r67", action="store_true")
    parser.add_argument("--probe-transport-preempt-gsrt-r67", action="store_true")
    parser.add_argument("--probe-transport-preempt-hcom-r67", action="store_true")
    parser.add_argument("--probe-transport-preempt-both-r67", action="store_true")
    parser.add_argument("--probe-transport-dec-hcom-r67", action="store_true")
    parser.add_argument("--probe-transport-dec-act-r67", action="store_true")
    parser.add_argument("--probe-transport-lengate-gsrt-24-r67", action="store_true")
    parser.add_argument("--probe-transport-lengate-gsrt-25-r67", action="store_true")
    parser.add_argument("--probe-transport-lengate-hcom-131-r67", action="store_true")
    parser.add_argument("--probe-transport-lengate-hcom-132-r67", action="store_true")
    parser.add_argument("--probe-transport-posttable-nomatch-r68", action="store_true")
    parser.add_argument("--probe-transport-txw-piperefuse-r68", action="store_true")
    parser.add_argument("--probe-transport-extsuffix-wav-r69", action="store_true")
    parser.add_argument("--probe-transport-extsuffix-bin-r69", action="store_true")
    parser.add_argument("--probe-transport-extsuffix-txw-r69", action="store_true")
    parser.add_argument("--probe-transport-extsuffix-f32-r69", action="store_true")
    parser.add_argument("--probe-transport-extsuffix-snd-r69", action="store_true")
    args = parser.parse_args()
    if sum([args.probe_slope, args.probe_failing, args.probe_flat, args.probe_layer_flat, args.probe_layer_join, args.probe_layer_slope, args.probe_layer_alt_flat, args.probe_layer_alt_join, args.probe_layer_alt_slope, args.probe_layer_alt_reverse, args.probe_layer_third_slope, args.probe_layer_third_slope_edge_pass, args.probe_layer_third_slope_edge_fail, args.probe_layer_third_join, args.probe_layer_third_join_edge_pass, args.probe_layer_third_join_edge_fail, args.probe_invalid, args.probe_ui_clone, args.probe_ui_duration_below, args.probe_ui_duration_at, args.probe_ui_centroid_below, args.probe_ui_centroid_above, args.probe_ui_lower_centroid_below, args.probe_ui_lower_centroid_above, args.probe_ui_orientation_forward, args.probe_ui_orientation_reverse, args.probe_ui_joint_below, args.probe_ui_mixed_pass, args.probe_ambience_centroid_below, args.probe_ambience_centroid_above, args.probe_ambience_orientation_forward, args.probe_ambience_orientation_reverse, args.probe_outer_endpoint_983, args.probe_outer_endpoint_984, args.probe_outer_slope_32, args.probe_outer_slope_33, args.probe_ui_peak_31129, args.probe_ui_peak_31130, args.probe_ui_crest_46, args.probe_ui_crest_47, args.probe_ui_tolerance_5807, args.probe_ui_tolerance_5809, args.probe_ui_lower_tolerance_5713, args.probe_ui_lower_tolerance_5711, args.probe_ui_absolute_centroid_below, args.probe_ui_absolute_centroid_above, args.probe_ui_upper_centroid_below, args.probe_ui_upper_centroid_above, args.probe_ui_rate_47999, args.probe_ui_rate_48000, args.probe_ui_rate_48001, args.probe_ui_rate_48000_r49, args.probe_ui_channel_stereo, args.probe_ui_channel_mono, args.probe_ui_pcm24, args.probe_ui_pcm16, args.probe_ui_pcm8, args.probe_ui_pcm16_r52, args.probe_ui_float32, args.probe_ui_pcm16_r53, args.probe_ui_pcm32, args.probe_ui_pcm16_r54, args.probe_ui_extensible_pcm16, args.probe_ui_standard_pcm16_r55, args.probe_ui_extensible_mask_zero, args.probe_ui_extensible_mask_center, args.probe_ui_extensible_valid_15, args.probe_ui_extensible_valid_16, args.probe_ui_extensible_valid_14_r58, args.probe_ui_extensible_valid_16_r58, args.probe_ui_extensible_valid_13_r59, args.probe_ui_extensible_valid_16_r59, args.probe_ui_extensible_valid_0_r60, args.probe_ui_extensible_valid_16_r60, args.probe_ui_extensible_valid_17_r61, args.probe_ui_extensible_valid_16_r61, args.probe_ui_extensible_valid_24_r62, args.probe_ui_extensible_valid_32_r62, args.probe_ui_route_act_84_r63, args.probe_ui_route_act_00_r63, args.probe_ui_extensible_valid_8_r64, args.probe_ui_extensible_valid_9_r64, args.probe_ui_extensible_valid_24_r64, args.probe_ui_extensible_valid_25_r64, args.probe_ui_extensible_valid_56_r64, args.probe_ui_extensible_valid_57_r64, args.probe_ui_preempt_act_r65, args.probe_ui_preempt_gsrt_r65, args.probe_ui_preempt_hcom_r65, args.probe_ui_preempt_both_r65, args.probe_ui_dec_hcom_r66, args.probe_ui_dec_act_r66, args.probe_ui_lengate_gsrt_24_r66, args.probe_ui_lengate_gsrt_25_r66, args.probe_ui_lengate_hcom_131_r66, args.probe_ui_lengate_hcom_132_r66, args.probe_transport_preempt_act_r67, args.probe_transport_preempt_gsrt_r67, args.probe_transport_preempt_hcom_r67, args.probe_transport_preempt_both_r67, args.probe_transport_dec_hcom_r67, args.probe_transport_dec_act_r67, args.probe_transport_lengate_gsrt_24_r67, args.probe_transport_lengate_gsrt_25_r67, args.probe_transport_lengate_hcom_131_r67, args.probe_transport_lengate_hcom_132_r67, args.probe_transport_posttable_nomatch_r68, args.probe_transport_txw_piperefuse_r68, args.probe_transport_extsuffix_wav_r69, args.probe_transport_extsuffix_bin_r69, args.probe_transport_extsuffix_txw_r69, args.probe_transport_extsuffix_f32_r69, args.probe_transport_extsuffix_snd_r69]) > 1:
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
        return 1 if all(r["status"] in ("expected_failure", "expected_pass") for r in results) else 2
    command(sys.executable, str(Path(__file__).with_name("build_artifacts.py")),
            *(["--probe-transport-extsuffix-wav-r69"] if args.probe_transport_extsuffix_wav_r69 else []),
            *(["--probe-transport-extsuffix-bin-r69"] if args.probe_transport_extsuffix_bin_r69 else []),
            *(["--probe-transport-extsuffix-txw-r69"] if args.probe_transport_extsuffix_txw_r69 else []),
            *(["--probe-transport-extsuffix-f32-r69"] if args.probe_transport_extsuffix_f32_r69 else []),
            *(["--probe-transport-extsuffix-snd-r69"] if args.probe_transport_extsuffix_snd_r69 else []),
            *(["--probe-transport-posttable-nomatch-r68"] if args.probe_transport_posttable_nomatch_r68 else []),
            *(["--probe-transport-txw-piperefuse-r68"] if args.probe_transport_txw_piperefuse_r68 else []),
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
            *(["--probe-layer-third-slope-edge-fail"] if args.probe_layer_third_slope_edge_fail else []),
            *(["--probe-layer-third-join"] if args.probe_layer_third_join else []),
            *(["--probe-layer-third-join-edge-pass"] if args.probe_layer_third_join_edge_pass else []),
            *(["--probe-layer-third-join-edge-fail"] if args.probe_layer_third_join_edge_fail else []),
            *(["--probe-ui-clone"] if args.probe_ui_clone else []),
            *(["--probe-ui-duration-below"] if args.probe_ui_duration_below else []),
            *(["--probe-ui-duration-at"] if args.probe_ui_duration_at else []),
            *(["--probe-ui-centroid-below"] if args.probe_ui_centroid_below else []),
            *(["--probe-ui-centroid-above"] if args.probe_ui_centroid_above else []),
            *(["--probe-ui-lower-centroid-below"] if args.probe_ui_lower_centroid_below else []),
            *(["--probe-ui-lower-centroid-above"] if args.probe_ui_lower_centroid_above else []),
            *(["--probe-ui-orientation-forward"] if args.probe_ui_orientation_forward else []),
            *(["--probe-ui-orientation-reverse"] if args.probe_ui_orientation_reverse else []),
            *(["--probe-ui-joint-below"] if args.probe_ui_joint_below else []),
            *(["--probe-ui-mixed-pass"] if args.probe_ui_mixed_pass else []),
            *(["--probe-ambience-centroid-below"] if args.probe_ambience_centroid_below else []),
            *(["--probe-ambience-centroid-above"] if args.probe_ambience_centroid_above else []),
            *(["--probe-ambience-orientation-forward"] if args.probe_ambience_orientation_forward else []),
            *(["--probe-ambience-orientation-reverse"] if args.probe_ambience_orientation_reverse else []),
            *(["--probe-outer-endpoint-983"] if args.probe_outer_endpoint_983 else []),
            *(["--probe-outer-endpoint-984"] if args.probe_outer_endpoint_984 else []),
            *(["--probe-outer-slope-32"] if args.probe_outer_slope_32 else []),
            *(["--probe-outer-slope-33"] if args.probe_outer_slope_33 else []),
            *(["--probe-ui-peak-31129"] if args.probe_ui_peak_31129 else []),
            *(["--probe-ui-peak-31130"] if args.probe_ui_peak_31130 else []),
            *(["--probe-ui-crest-46"] if args.probe_ui_crest_46 else []),
            *(["--probe-ui-crest-47"] if args.probe_ui_crest_47 else []),
            *(["--probe-ui-tolerance-5807"] if args.probe_ui_tolerance_5807 else []),
            *(["--probe-ui-tolerance-5809"] if args.probe_ui_tolerance_5809 else []),
            *(["--probe-ui-lower-tolerance-5713"] if args.probe_ui_lower_tolerance_5713 else []),
            *(["--probe-ui-lower-tolerance-5711"] if args.probe_ui_lower_tolerance_5711 else []),
            *(["--probe-ui-absolute-centroid-below"] if args.probe_ui_absolute_centroid_below else []),
            *(["--probe-ui-absolute-centroid-above"] if args.probe_ui_absolute_centroid_above else []),
            *(["--probe-ui-upper-centroid-below"] if args.probe_ui_upper_centroid_below else []),
            *(["--probe-ui-upper-centroid-above"] if args.probe_ui_upper_centroid_above else []),
            *(["--probe-ui-rate-47999"] if args.probe_ui_rate_47999 else []),
            *(["--probe-ui-rate-48000"] if args.probe_ui_rate_48000 else []),
            *(["--probe-ui-rate-48001"] if args.probe_ui_rate_48001 else []),
            *(["--probe-ui-rate-48000-r49"] if args.probe_ui_rate_48000_r49 else []),
            *(["--probe-ui-channel-stereo"] if args.probe_ui_channel_stereo else []),
            *(["--probe-ui-channel-mono"] if args.probe_ui_channel_mono else []),
            *(["--probe-ui-pcm24"] if args.probe_ui_pcm24 else []),
            *(["--probe-ui-pcm16"] if args.probe_ui_pcm16 else []),
            *(["--probe-ui-pcm8"] if args.probe_ui_pcm8 else []),
            *(["--probe-ui-pcm16-r52"] if args.probe_ui_pcm16_r52 else []),
            *(["--probe-ui-float32"] if args.probe_ui_float32 else []),
            *(["--probe-ui-pcm16-r53"] if args.probe_ui_pcm16_r53 else []),
            *(["--probe-ui-pcm32"] if args.probe_ui_pcm32 else []),
            *(["--probe-ui-pcm16-r54"] if args.probe_ui_pcm16_r54 else []),
            *(["--probe-ui-extensible-pcm16"] if args.probe_ui_extensible_pcm16 else []),
            *(["--probe-ui-standard-pcm16-r55"] if args.probe_ui_standard_pcm16_r55 else []),
            *(["--probe-ui-extensible-mask-zero"] if args.probe_ui_extensible_mask_zero else []),
            *(["--probe-ui-extensible-mask-center"] if args.probe_ui_extensible_mask_center else []),
            *(["--probe-ui-extensible-valid-15"] if args.probe_ui_extensible_valid_15 else []),
            *(["--probe-ui-extensible-valid-16"] if args.probe_ui_extensible_valid_16 else []),
            *(["--probe-ui-extensible-valid-14-r58"] if args.probe_ui_extensible_valid_14_r58 else []),
            *(["--probe-ui-extensible-valid-16-r58"] if args.probe_ui_extensible_valid_16_r58 else []),
            *(["--probe-ui-extensible-valid-13-r59"] if args.probe_ui_extensible_valid_13_r59 else []),
            *(["--probe-ui-extensible-valid-16-r59"] if args.probe_ui_extensible_valid_16_r59 else []),
            *(["--probe-ui-extensible-valid-0-r60"] if args.probe_ui_extensible_valid_0_r60 else []),
            *(["--probe-ui-extensible-valid-16-r60"] if args.probe_ui_extensible_valid_16_r60 else []),
            *(["--probe-ui-extensible-valid-17-r61"] if args.probe_ui_extensible_valid_17_r61 else []),
            *(["--probe-ui-extensible-valid-16-r61"] if args.probe_ui_extensible_valid_16_r61 else []),
            *(["--probe-ui-extensible-valid-24-r62"] if args.probe_ui_extensible_valid_24_r62 else []),
            *(["--probe-ui-extensible-valid-32-r62"] if args.probe_ui_extensible_valid_32_r62 else []),
            *(["--probe-ui-route-act-84-r63"] if args.probe_ui_route_act_84_r63 else []),
            *(["--probe-ui-route-act-00-r63"] if args.probe_ui_route_act_00_r63 else []),
            *(["--probe-ui-extensible-valid-8-r64"] if args.probe_ui_extensible_valid_8_r64 else []),
            *(["--probe-ui-extensible-valid-9-r64"] if args.probe_ui_extensible_valid_9_r64 else []),
            *(["--probe-ui-extensible-valid-24-r64"] if args.probe_ui_extensible_valid_24_r64 else []),
            *(["--probe-ui-extensible-valid-25-r64"] if args.probe_ui_extensible_valid_25_r64 else []),
            *(["--probe-ui-extensible-valid-56-r64"] if args.probe_ui_extensible_valid_56_r64 else []),
            *(["--probe-ui-extensible-valid-57-r64"] if args.probe_ui_extensible_valid_57_r64 else []),
            *(["--probe-ui-preempt-act-r65"] if args.probe_ui_preempt_act_r65 else []),
            *(["--probe-ui-preempt-gsrt-r65"] if args.probe_ui_preempt_gsrt_r65 else []),
            *(["--probe-ui-preempt-hcom-r65"] if args.probe_ui_preempt_hcom_r65 else []),
            *(["--probe-ui-preempt-both-r65"] if args.probe_ui_preempt_both_r65 else []),
            *(["--probe-ui-dec-hcom-r66"] if args.probe_ui_dec_hcom_r66 else []),
            *(["--probe-ui-dec-act-r66"] if args.probe_ui_dec_act_r66 else []),
            *(["--probe-ui-lengate-gsrt-24-r66"] if args.probe_ui_lengate_gsrt_24_r66 else []),
            *(["--probe-ui-lengate-gsrt-25-r66"] if args.probe_ui_lengate_gsrt_25_r66 else []),
            *(["--probe-ui-lengate-hcom-131-r66"] if args.probe_ui_lengate_hcom_131_r66 else []),
            *(["--probe-ui-lengate-hcom-132-r66"] if args.probe_ui_lengate_hcom_132_r66 else []))
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
    if args.probe_layer_third_join:
        path = ROOT / "live" / "round-20" / "join200_probe.wav"
        measurements["join200_probe"] = measure("join200_probe", SPECS["stem_layer_third"], path)
    if args.probe_layer_third_join_edge_pass or args.probe_layer_third_join_edge_fail:
        name = "join200_edgepass_probe" if args.probe_layer_third_join_edge_pass else "join200_edgefail_probe"
        path = ROOT / "live" / "round-21" / (name + ".wav")
        measurements[name] = measure(name, SPECS["stem_layer_third"], path)
    if args.probe_ui_clone:
        for name in ("ui_clone", "ui_clone_alt"):
            path = ROOT / "live" / "round-26" / (name + ".wav")
            measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_duration_below or args.probe_ui_duration_at:
        label = "below" if args.probe_ui_duration_below else "at"
        duration = 6719 / 48000 if args.probe_ui_duration_below else 6720 / 48000
        for name, spec in ((f"ui_duration_{label}", SPECS["ui"]),
                           (f"ui_duration_{label}_alt", (duration, *SPECS["ui"][1:]))):
            path = ROOT / "live" / "round-27" / (name + ".wav")
            measurements[name] = measure(name, spec, path)
    if args.probe_ui_centroid_below or args.probe_ui_centroid_above:
        label = "below" if args.probe_ui_centroid_below else "above"
        for name in (f"ui_centroid_{label}", f"ui_centroid_{label}_alt"):
            path = ROOT / "live" / "round-28" / (name + ".wav")
            measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_lower_centroid_below or args.probe_ui_lower_centroid_above:
        label = "below" if args.probe_ui_lower_centroid_below else "above"
        for name in (f"ui_lower_centroid_{label}", f"ui_lower_centroid_{label}_alt"):
            path = ROOT / "live" / "round-29" / (name + ".wav")
            measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_orientation_forward or args.probe_ui_orientation_reverse:
        label = "reverse" if args.probe_ui_orientation_reverse else "forward"
        for name in (f"ui_orientation_{label}", f"ui_orientation_{label}_alt"):
            path = ROOT / "live" / "round-30" / (name + ".wav")
            measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_joint_below:
        for name, spec in (("ui_joint_below", SPECS["ui"]),
                           ("ui_joint_below_alt", (6719 / 48000, *SPECS["ui"][1:]))):
            path = ROOT / "live" / "round-31" / (name + ".wav")
            measurements[name] = measure(name, spec, path)
    if args.probe_ui_mixed_pass:
        for name, spec in (("ui_mixed_pass", SPECS["ui"]),
                           ("ui_mixed_pass_alt", (6719 / 48000, *SPECS["ui"][1:]))):
            path = ROOT / "live" / "round-32" / (name + ".wav")
            measurements[name] = measure(name, spec, path)
    if (args.probe_transport_extsuffix_wav_r69 or args.probe_transport_extsuffix_bin_r69
            or args.probe_transport_extsuffix_txw_r69 or args.probe_transport_extsuffix_f32_r69
            or args.probe_transport_extsuffix_snd_r69):
        # r69 arm: pin EXTENSION-SUFFIX as a measured axis of the post-table
        # fallback. r68 pinned named-vs-anonymous; these five members carry
        # ONE identical no-match buffer under five names, so the only
        # variable inside the named arm is lsx_find_file_extension(path).
        # wav/bin/txw/f32 exercise four distinct fallback-handler outcomes;
        # snd fires the ext-gated sndr CHECK row — the first tracked member
        # whose DETECTION (sox_detected_format), not just its decode
        # verdict, forks on transport name. Members built by
        # build_ui_extsuffix_r69_probe (forwarded above); same
        # transport_entry machinery as r67/r68.
        member = ("extsuffix_wav" if args.probe_transport_extsuffix_wav_r69 else
                  "extsuffix_bin" if args.probe_transport_extsuffix_bin_r69 else
                  "extsuffix_txw" if args.probe_transport_extsuffix_txw_r69 else
                  "extsuffix_f32" if args.probe_transport_extsuffix_f32_r69 else
                  "extsuffix_snd")
        directory, filename = TRANSPORT_R69_MEMBERS[member]
        name = f"transport_{member}_r69_probe"
        measurements[name] = transport_entry(member, ROOT / "live" / directory / filename)
    if (args.probe_transport_posttable_nomatch_r68
            or args.probe_transport_txw_piperefuse_r68):
        # r68 arm: pin the POST-TABLE path as a measured axis. r67 showed
        # detection never forks over matched members; this arm measures what
        # happens when NO CHECK row matches (posttable_nomatch) — the
        # remaining classifier is the filename extension (named arms route
        # to the wav reader: file via true rewind, fifo via pending-buffer
        # replay of the <=257-B prefetch; anonymous '-' arms fail
        # 'can't determine type') — plus the reader-level !seekable
        # pipe-refusal pin downstream of a real txw detection
        # (txw_piperefuse). Members built by build_ui_posttable_r68_probe
        # (forwarded above); same transport_entry machinery as r67.
        member = ("posttable_nomatch" if args.probe_transport_posttable_nomatch_r68
                  else "txw_piperefuse")
        directory, filename = TRANSPORT_R68_MEMBERS[member]
        name = f"transport_{member}_r68_probe"
        measurements[name] = transport_entry(member, ROOT / "live" / directory / filename)
    if (args.probe_transport_preempt_act_r67 or args.probe_transport_preempt_gsrt_r67
            or args.probe_transport_preempt_hcom_r67 or args.probe_transport_preempt_both_r67
            or args.probe_transport_dec_hcom_r67 or args.probe_transport_dec_act_r67
            or args.probe_transport_lengate_gsrt_24_r67 or args.probe_transport_lengate_gsrt_25_r67
            or args.probe_transport_lengate_hcom_131_r67 or args.probe_transport_lengate_hcom_132_r67):
        # r67 transport arm: pin TRANSPORT as a measured axis of the autodetect
        # ledger. Every prior row ran the `file` transport implicitly; each
        # member now records a {file, stdin_pipe, redirected_fd, fifo_path}
        # detection+decode verdict matrix explicitly. r65/r66 established the
        # forks this axis pins: gsrt's seekable-gated checksum pass (file:
        # premature EOF vs non-seekable: encoding/header fail), the ffmpeg
        # bridge's file-only decode (named seekable decodes; `-` dies; pipe
        # dies on the pending-buffer au-magic poison), and hcom/wav as the
        # transport-invariant controls. The member set is the complete tracked
        # autodetect family — no new fixtures (members already tracked under
        # live/round-65|66); the fork set over it is exactly measurable.
        member = ("preempt_act" if args.probe_transport_preempt_act_r67 else
                  "preempt_gsrt" if args.probe_transport_preempt_gsrt_r67 else
                  "preempt_hcom" if args.probe_transport_preempt_hcom_r67 else
                  "preempt_both" if args.probe_transport_preempt_both_r67 else
                  "dec_hcom" if args.probe_transport_dec_hcom_r67 else
                  "dec_act" if args.probe_transport_dec_act_r67 else
                  "lengate_gsrt_24" if args.probe_transport_lengate_gsrt_24_r67 else
                  "lengate_gsrt_25" if args.probe_transport_lengate_gsrt_25_r67 else
                  "lengate_hcom_131" if args.probe_transport_lengate_hcom_131_r67 else
                  "lengate_hcom_132")
        directory, filename = TRANSPORT_R67_MEMBERS[member]
        name = f"transport_{member}_r67_probe"
        measurements[name] = transport_entry(member, ROOT / "live" / directory / filename)
    if (args.probe_ui_dec_hcom_r66 or args.probe_ui_dec_act_r66
            or args.probe_ui_lengate_gsrt_24_r66 or args.probe_ui_lengate_gsrt_25_r66
            or args.probe_ui_lengate_hcom_131_r66 or args.probe_ui_lengate_hcom_132_r66):
        # r66 preemptor-map completion family. The dec pair shares the r65
        # preemptor-collision shape but the hcom member is reader-valid:
        # detected hcom -> the native hcom reader decodes 9 samples @22050
        # (the standard ffprobe->duration pipeline cannot complete on the
        # hcom stream, so that member lands in the measure_pipeline branch).
        # The lengate members pin the CHECK len gates at exact file sizes:
        # gsrt 24|25 and hcom 131|132 — the below-gate member is the same
        # RIFF/WAVE shell minus the signature's final byte and falls
        # through to the wav row. Same leg set as r65 plus a raw f32
        # decode leg (the decodable-preemptor claim's direct evidence).
        member = ("dec_hcom" if args.probe_ui_dec_hcom_r66 else
                  "dec_act" if args.probe_ui_dec_act_r66 else
                  "lengate_gsrt_24" if args.probe_ui_lengate_gsrt_24_r66 else
                  "lengate_gsrt_25" if args.probe_ui_lengate_gsrt_25_r66 else
                  "lengate_hcom_131" if args.probe_ui_lengate_hcom_131_r66 else
                  "lengate_hcom_132")
        name = f"ui_{member}_r66_probe"
        path = ROOT / "live" / "round-66" / f"pair_{member}.wav"
        route = subprocess.run(["sox", "-V6", str(path), "-n", "stat"], capture_output=True)
        detected = re.search(r"detected file format type `(\S+?)'",
                             route.stderr.decode(errors="replace"))
        read = re.search(r"Samples read:\s*(\d+)", route.stderr.decode(errors="replace"))
        bridge = subprocess.run(["sox", "-t", "act", str(path), "-n", "stat"], capture_output=True)
        bread = re.search(r"Samples read:\s*(\d+)", bridge.stderr.decode(errors="replace"))
        native = subprocess.run(["sox", "-t", "wav", str(path), "-n", "stat"], capture_output=True)
        nread = re.search(r"Samples read:\s*(\d+)", native.stderr.decode(errors="replace"))
        f32 = subprocess.run(["sox", str(path), "-t", "f32", "-e", "floating-point", "-"],
                             capture_output=True)
        try:
            entry = measure(name, SPECS["ui"], path)
        except subprocess.CalledProcessError as exc:
            # ffprobe demuxer diagnostics carry an ASLR context address
            # ("[wav @ 0x...]"); strip the address so the receipt is
            # byte-deterministic while keeping the message verbatim.
            entry = {"path": str(path.relative_to(ROOT)),
                     "decode_error_tool": Path(exc.cmd[0]).name,
                     "sox_exit_code": exc.returncode,
                     "sox_stderr": re.sub(r" @ 0x[0-9a-f]+\]", "]",
                                          exc.stderr.decode(errors="replace").strip()),
                     "failures": ["decode: default SoX route rejected input"]}
        except Exception as exc:
            # measure() completes ffprobe+sox decode but can still stop on
            # stream-shape gaps (e.g. hcom's format object carries no
            # duration field) — record the stop point deterministically.
            entry = {"path": str(path.relative_to(ROOT)),
                     "decode_error_tool": "measure_pipeline",
                     "measure_error": f"{type(exc).__name__}: {exc}",
                     "failures": ["decode: standard measurement pipeline rejected input"]}
        entry["pair_member"] = member
        entry["sox_detected_format"] = detected.group(1) if detected else None
        entry["sox_route"] = ("ffmpeg" if (detected and detected.group(1) == "act")
                              or b"(ffmpeg)" in route.stderr else "native")
        entry["sox_stat_exit_code"] = route.returncode
        entry["sox_stat_samples_read"] = int(read.group(1)) if read else None
        if route.returncode and not read:
            tail = route.stderr.decode(errors="replace").strip().splitlines()
            entry["sox_stat_stderr"] = tail[-1][-160:] if tail else ""
        entry["sox_bridge_exit_code"] = bridge.returncode
        entry["sox_bridge_samples_read"] = int(bread.group(1)) if bread else None
        if bridge.returncode and not bread:
            tail = bridge.stderr.decode(errors="replace").strip().splitlines()
            entry["sox_bridge_stderr"] = tail[-1][-160:] if tail else ""
        entry["sox_native_exit_code"] = native.returncode
        entry["sox_native_samples_read"] = int(nread.group(1)) if nread else None
        if native.returncode and not nread:
            tail = native.stderr.decode(errors="replace").strip().splitlines()
            entry["sox_native_stderr"] = tail[-1][-160:] if tail else ""
        entry["sox_f32_exit_code"] = f32.returncode
        entry["sox_f32_bytes"] = len(f32.stdout)
        measurements[name] = entry
    if (args.probe_ui_preempt_act_r65 or args.probe_ui_preempt_gsrt_r65
            or args.probe_ui_preempt_hcom_r65 or args.probe_ui_preempt_both_r65):
        # r65 preemptor-collision family: every member carries the r63 act
        # trigger (RIFF@0, 0x84@256); "gsrt"/"hcom"/"both" additionally carry
        # preemptor signatures (gsrt "ring.bin\0"@16, hcom "FSSD"@65 +
        # "HCOM"@128). Detection is first-match-wins, so the recorded
        # detected-format/route is the receipt's discriminating content.
        # The forced -t act leg is the counterfactual (would the bridge have
        # decoded it) and the -t wav leg the native verdict underneath.
        member = ("act" if args.probe_ui_preempt_act_r65 else
                  "gsrt" if args.probe_ui_preempt_gsrt_r65 else
                  "hcom" if args.probe_ui_preempt_hcom_r65 else "both")
        name = f"ui_preempt_{member}_r65_probe"
        path = ROOT / "live" / "round-65" / f"pair_preempt_{member}.wav"
        route = subprocess.run(["sox", "-V6", str(path), "-n", "stat"], capture_output=True)
        detected = re.search(r"detected file format type `(\S+?)'",
                             route.stderr.decode(errors="replace"))
        read = re.search(r"Samples read:\s*(\d+)", route.stderr.decode(errors="replace"))
        bridge = subprocess.run(["sox", "-t", "act", str(path), "-n", "stat"], capture_output=True)
        bread = re.search(r"Samples read:\s*(\d+)", bridge.stderr.decode(errors="replace"))
        native = subprocess.run(["sox", "-t", "wav", str(path), "-n", "stat"], capture_output=True)
        nread = re.search(r"Samples read:\s*(\d+)", native.stderr.decode(errors="replace"))
        try:
            entry = measure(name, SPECS["ui"], path)
        except subprocess.CalledProcessError as exc:
            # ffprobe demuxer diagnostics carry an ASLR context address
            # ("[wav @ 0x...]"); strip the address so the receipt is
            # byte-deterministic while keeping the message verbatim.
            entry = {"path": str(path.relative_to(ROOT)),
                     "decode_error_tool": Path(exc.cmd[0]).name,
                     "sox_exit_code": exc.returncode,
                     "sox_stderr": re.sub(r" @ 0x[0-9a-f]+\]", "]",
                                          exc.stderr.decode(errors="replace").strip()),
                     "failures": ["decode: default SoX route rejected input"]}
        entry["sox_detected_format"] = detected.group(1) if detected else None
        entry["sox_route"] = ("ffmpeg" if (detected and detected.group(1) == "act")
                              or b"(ffmpeg)" in route.stderr else "native")
        entry["sox_stat_exit_code"] = route.returncode
        entry["sox_stat_samples_read"] = int(read.group(1)) if read else None
        if route.returncode and not read:
            tail = route.stderr.decode(errors="replace").strip().splitlines()
            entry["sox_stat_stderr"] = tail[-1][-160:] if tail else ""
        entry["sox_bridge_exit_code"] = bridge.returncode
        entry["sox_bridge_samples_read"] = int(bread.group(1)) if bread else None
        if bridge.returncode and not bread:
            tail = bridge.stderr.decode(errors="replace").strip().splitlines()
            entry["sox_bridge_stderr"] = tail[-1][-160:] if tail else ""
        entry["sox_native_exit_code"] = native.returncode
        entry["sox_native_samples_read"] = int(nread.group(1)) if nread else None
        if native.returncode and not nread:
            tail = native.stderr.decode(errors="replace").strip().splitlines()
            entry["sox_native_stderr"] = tail[-1][-160:] if tail else ""
        measurements[name] = entry
    if (args.probe_ui_extensible_valid_8_r64 or args.probe_ui_extensible_valid_9_r64
            or args.probe_ui_extensible_valid_24_r64 or args.probe_ui_extensible_valid_25_r64
            or args.probe_ui_extensible_valid_56_r64 or args.probe_ui_extensible_valid_57_r64):
        # r64 sweep control: each member sits on one side of a width step of the
        # valid-bits -> codec map (8|9: u8|s16le, 24|25: s24le|s32le,
        # 56|57: none|s64le). Byte 256 is pinned 0x84 -> default route is
        # act-detected -> ffmpeg bridge. Record the negotiated codec plus both
        # route outcomes so each receipt carries the boundary evidence.
        valid = (8 if args.probe_ui_extensible_valid_8_r64 else
                 9 if args.probe_ui_extensible_valid_9_r64 else
                 24 if args.probe_ui_extensible_valid_24_r64 else
                 25 if args.probe_ui_extensible_valid_25_r64 else
                 56 if args.probe_ui_extensible_valid_56_r64 else 57)
        name = f"ui_extensible_valid_{valid}_r64_probe"
        path = ROOT / "live" / "round-64" / f"pair_valid_{valid}.wav"
        route = subprocess.run(["sox", "-V6", str(path), "-n", "stat"], capture_output=True)
        detected = re.search(r"detected file format type `(\S+?)'",
                             route.stderr.decode(errors="replace"))
        read = re.search(r"Samples read:\s*(\d+)", route.stderr.decode(errors="replace"))
        native = subprocess.run(["sox", "-t", "wav", str(path), "-n", "stat"], capture_output=True)
        nread = re.search(r"Samples read:\s*(\d+)", native.stderr.decode(errors="replace"))
        try:
            entry = measure(name, SPECS["ui"], path)
        except subprocess.CalledProcessError as exc:
            entry = {"path": str(path.relative_to(ROOT)),
                     "sox_exit_code": exc.returncode,
                     "sox_stderr": exc.stderr.decode(errors="replace").strip(),
                     "failures": ["decode: default SoX route rejected input"]}
        entry["valid_bits"] = valid
        entry["sox_detected_format"] = detected.group(1) if detected else None
        entry["sox_route"] = ("ffmpeg" if (detected and detected.group(1) == "act")
                              or b"(ffmpeg)" in route.stderr else "native")
        entry["sox_stat_exit_code"] = route.returncode
        entry["sox_stat_samples_read"] = int(read.group(1)) if read else None
        entry["sox_native_exit_code"] = native.returncode
        entry["sox_native_samples_read"] = int(nread.group(1)) if nread else None
        if native.returncode and not nread:
            tail = native.stderr.decode(errors="replace").strip().splitlines()
            entry["sox_native_stderr"] = tail[-1][-160:] if tail else ""
        measurements[name] = entry
    if args.probe_ui_route_act_84_r63 or args.probe_ui_route_act_00_r63:
        byte = 0x84 if args.probe_ui_route_act_84_r63 else 0x00
        name = f"ui_route_act_{byte:02x}_r63_probe"
        path = ROOT / "live" / "round-63" / f"pair_route_{byte:02x}.wav"
        route = subprocess.run(["sox", "-V6", str(path), "-n", "stat"], capture_output=True)
        detected = re.search(r"detected file format type `(\S+?)'",
                             route.stderr.decode(errors="replace"))
        try:
            entry = measure(name, SPECS["ui"], path)
        except subprocess.CalledProcessError as exc:
            entry = {"path": str(path.relative_to(ROOT)),
                     "sox_exit_code": exc.returncode,
                     "sox_stderr": exc.stderr.decode(errors="replace").strip(),
                     "failures": ["decode: default SoX route rejected input"]}
        entry["sox_detected_format"] = detected.group(1) if detected else None
        entry["sox_route"] = "ffmpeg" if b"(ffmpeg)" in route.stderr else "native"
        measurements[name] = entry
    if args.probe_ui_extensible_valid_24_r62 or args.probe_ui_extensible_valid_32_r62:
        valid = 24 if args.probe_ui_extensible_valid_24_r62 else 32
        name = f"ui_extensible_valid_{valid}_r62_probe"
        path = ROOT / "live" / "round-62" / f"pair_valid_{valid}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_extensible_valid_17_r61 or args.probe_ui_extensible_valid_16_r61:
        valid = 17 if args.probe_ui_extensible_valid_17_r61 else 16
        name = f"ui_extensible_valid_{valid}_r61_probe"
        path = ROOT / "live" / "round-61" / f"pair_valid_{valid}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_extensible_valid_0_r60 or args.probe_ui_extensible_valid_16_r60:
        valid = 0 if args.probe_ui_extensible_valid_0_r60 else 16
        name = f"ui_extensible_valid_{valid}_r60_probe"
        path = ROOT / "live" / "round-60" / f"pair_valid_{valid}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_extensible_valid_13_r59 or args.probe_ui_extensible_valid_16_r59:
        valid = 13 if args.probe_ui_extensible_valid_13_r59 else 16
        name = f"ui_extensible_valid_{valid}_r59_probe"
        path = ROOT / "live" / "round-59" / f"pair_valid_{valid}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_extensible_valid_14_r58 or args.probe_ui_extensible_valid_16_r58:
        valid = 14 if args.probe_ui_extensible_valid_14_r58 else 16
        name = f"ui_extensible_valid_{valid}_r58_probe"
        path = ROOT / "live" / "round-58" / f"pair_valid_{valid}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_extensible_valid_15 or args.probe_ui_extensible_valid_16:
        valid = 15 if args.probe_ui_extensible_valid_15 else 16
        name = f"ui_extensible_valid_{valid}_r57_probe"
        path = ROOT / "live" / "round-57" / f"pair_valid_{valid}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_extensible_mask_zero or args.probe_ui_extensible_mask_center:
        mask = "zero" if args.probe_ui_extensible_mask_zero else "center"
        name = f"ui_extensible_mask_{mask}_r56_probe"
        path = ROOT / "live" / "round-56" / f"pair_mask_{mask}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_extensible_pcm16 or args.probe_ui_standard_pcm16_r55:
        header = "extensible" if args.probe_ui_extensible_pcm16 else "standard"
        name = f"ui_{header}_pcm16_r55_probe"
        path = ROOT / "live" / "round-55" / f"pair_{header}_pcm16.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_pcm32 or args.probe_ui_pcm16_r54:
        depth = "pcm32" if args.probe_ui_pcm32 else "pcm16"
        name = f"ui_depth_{depth}_r54_probe"
        path = ROOT / "live" / "round-54" / f"pair_{depth}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_float32 or args.probe_ui_pcm16_r53:
        depth = "float32" if args.probe_ui_float32 else "pcm16"
        name = f"ui_depth_{depth}_r53_probe"
        path = ROOT / "live" / "round-53" / f"pair_{depth}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_pcm8 or args.probe_ui_pcm16_r52:
        depth = "pcm8" if args.probe_ui_pcm8 else "pcm16"
        name = f"ui_depth_{depth}_r52_probe"
        path = ROOT / "live" / "round-52" / f"pair_{depth}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_pcm24 or args.probe_ui_pcm16:
        depth = "pcm24" if args.probe_ui_pcm24 else "pcm16"
        name = f"ui_depth_{depth}_probe"
        path = ROOT / "live" / "round-51" / f"pair_{depth}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_channel_stereo or args.probe_ui_channel_mono:
        channel = "stereo" if args.probe_ui_channel_stereo else "mono"
        name = f"ui_channel_{channel}_probe"
        path = ROOT / "live" / "round-50" / f"{channel}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_rate_48001 or args.probe_ui_rate_48000_r49:
        rate = 48001 if args.probe_ui_rate_48001 else 48000
        name = f"ui_rate_r49_{rate}_probe"
        path = ROOT / "live" / "round-49" / f"ui-{rate}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_rate_47999 or args.probe_ui_rate_48000:
        rate = 47999 if args.probe_ui_rate_47999 else 48000
        name = f"ui_rate_{rate}_probe"
        path = ROOT / "live" / "round-48" / f"ui-{rate}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_upper_centroid_below or args.probe_ui_upper_centroid_above:
        label = "below" if args.probe_ui_upper_centroid_below else "above"
        name = f"ui_upper_centroid_{label}_probe"
        path = ROOT / "live" / "round-47" / f"upper-{label}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_absolute_centroid_below or args.probe_ui_absolute_centroid_above:
        label = "below" if args.probe_ui_absolute_centroid_below else "above"
        name = f"ui_absolute_centroid_{label}_probe"
        path = ROOT / "live" / "round-46" / f"centroid-{label}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_lower_tolerance_5713 or args.probe_ui_lower_tolerance_5711:
        frames = 5713 if args.probe_ui_lower_tolerance_5713 else 5711
        name = f"ui_lower_tolerance_{frames}_probe"
        path = ROOT / "live" / "round-45" / f"duration-{frames}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_tolerance_5807 or args.probe_ui_tolerance_5809:
        frames = 5807 if args.probe_ui_tolerance_5807 else 5809
        name = f"ui_tolerance_{frames}_probe"
        path = ROOT / "live" / "round-44" / f"duration-{frames}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_crest_46 or args.probe_ui_crest_47:
        counts = 46 if args.probe_ui_crest_46 else 47
        name = f"ui_crest_{counts}_probe"
        path = ROOT / "live" / "round-43" / f"crest-{counts}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_ui_peak_31129 or args.probe_ui_peak_31130:
        counts = 31129 if args.probe_ui_peak_31129 else 31130
        name = f"ui_peak_{counts}_probe"
        path = ROOT / "live" / "round-42" / f"ui-peak-{counts}.wav"
        measurements[name] = measure(name, SPECS["ui"], path)
    if args.probe_outer_slope_32 or args.probe_outer_slope_33:
        counts = 32 if args.probe_outer_slope_32 else 33
        name = f"slope_{counts}_probe"
        path = ROOT / "live" / "round-41" / f"slope-{counts}.wav"
        measurements[name] = measure(name, (2.0, 5, 200, True), path)
    if args.probe_outer_endpoint_983 or args.probe_outer_endpoint_984:
        counts = 983 if args.probe_outer_endpoint_983 else 984
        name = f"endpoint_{counts}_probe"
        path = ROOT / "live" / "round-40" / f"endpoint_{counts}.wav"
        measurements[name] = measure(name, (2.0, 5, 200, True), path)
    if args.probe_ambience_orientation_forward or args.probe_ambience_orientation_reverse:
        reverse = args.probe_ambience_orientation_reverse
        for name, source in (("ambience_orientation", "orientation_high" if reverse else "orientation_low"),
                             ("ambience_orientation_alt", "orientation_low" if reverse else "orientation_high")):
            path = ROOT / "live" / "round-39" / (source + ".wav")
            measurements[name] = measure(name, (2.0, 5, 200, True), path)
    if args.probe_ambience_centroid_above:
        for name in ("ambience_above", "ambience_above_alt"):
            path = ROOT / "live" / "round-38" / (name + ".wav")
            measurements[name] = measure(name, (2.0, 5, 200, True), path)
    if args.probe_ambience_centroid_below:
        for name in ("ambience_probe", "ambience_probe_alt"):
            path = ROOT / "live" / "round-37" / (name + ".wav")
            measurements[name] = measure(name, (2.0, 5, 200, True), path)
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
    ui_family_comparisons = {}
    third = measurements["ui_third"]
    for name in ("ui", "ui_alt"):
        base = measurements[name]
        duration_delta = abs(third["duration_s"] - base["duration_s"])
        centroid_relative_delta = abs(third["spectral_centroid_hz"] - base["spectral_centroid_hz"]) / base["spectral_centroid_hz"]
        passed = duration_delta >= .020 or centroid_relative_delta >= .10
        ui_family_comparisons[name] = {"baseline": name, "variant": "ui_third",
                                       "duration_delta_s": duration_delta,
                                       "centroid_relative_delta": centroid_relative_delta,
                                       "passed": passed}
        if not passed:
            third["failures"].append(f"ui family distinctness: ui_third vs {name} below duration and centroid minima")
    impact_family_comparisons = {}
    third_impact = measurements["impact_third"]
    for name in ("impact", "impact_alt"):
        base = measurements[name]
        duration_delta = abs(third_impact["duration_s"] - base["duration_s"])
        centroid_relative_delta = abs(third_impact["spectral_centroid_hz"] - base["spectral_centroid_hz"]) / base["spectral_centroid_hz"]
        passed = duration_delta >= .020 or centroid_relative_delta >= .10
        impact_family_comparisons[name] = {"baseline": name, "variant": "impact_third",
                                           "duration_delta_s": duration_delta,
                                           "centroid_relative_delta": centroid_relative_delta,
                                           "passed": passed}
        if not passed:
            third_impact["failures"].append(f"impact family distinctness: impact_third vs {name} below duration and centroid minima")
    movement_family_comparisons = {}
    third_movement = measurements["movement_third"]
    for name in ("movement", "movement_alt"):
        base = measurements[name]
        duration_delta = abs(third_movement["duration_s"] - base["duration_s"])
        centroid_relative_delta = abs(third_movement["spectral_centroid_hz"] - base["spectral_centroid_hz"]) / base["spectral_centroid_hz"]
        passed = duration_delta >= .020 or centroid_relative_delta >= .10
        movement_family_comparisons[name] = {"baseline": name, "variant": "movement_third",
                                             "duration_delta_s": duration_delta,
                                             "centroid_relative_delta": centroid_relative_delta,
                                             "passed": passed}
        if not passed:
            third_movement["failures"].append(f"movement family distinctness: movement_third vs {name} below duration and centroid minima")
    ambience_family_comparisons = {}
    third_ambience = measurements["ambience_third"]
    for name in ("ambience", "ambience_alt"):
        base = measurements[name]
        duration_delta = abs(third_ambience["duration_s"] - base["duration_s"])
        centroid_relative_delta = abs(third_ambience["spectral_centroid_hz"] - base["spectral_centroid_hz"]) / base["spectral_centroid_hz"]
        passed = duration_delta >= .020 or centroid_relative_delta >= .10
        ambience_family_comparisons[name] = {"baseline": name, "variant": "ambience_third",
                                             "duration_delta_s": duration_delta,
                                             "centroid_relative_delta": centroid_relative_delta,
                                             "passed": passed}
        if not passed:
            third_ambience["failures"].append(f"ambience family distinctness: ambience_third vs {name} below duration and centroid minima")
    sections = {name: section_contrast(ROOT / data["path"], 200 if name in ("stem_layer_third", "slope200_probe", "edgepass_probe", "edgefail_probe", "join200_probe", "join200_edgepass_probe", "join200_edgefail_probe") else
                                       180 if name in ("stem_layer_alt", "flat180_probe", "join180_probe", "slope180_probe", "reverse180_probe") else
                                       120 if name in ("stem_layer", "flat120_probe", "join_probe", "layer_slope_probe") else 30)
                for name, data in measurements.items()
                if name in ("stem_sections", "flat30_probe", "stem_layer", "stem_layer_alt", "stem_layer_third", "slope200_probe", "edgepass_probe", "edgefail_probe", "join200_probe", "join200_edgepass_probe", "join200_edgefail_probe", "flat120_probe", "flat180_probe", "join180_probe", "slope180_probe", "reverse180_probe", "join_probe", "layer_slope_probe")}
    for name, result in sections.items():
        if not result["passed"]:
            measurements[name]["failures"].append(f"sections: {result['component_hz']} Hz component amplitude contrast < 6 dB or invalid")
        if name in ("stem_layer", "stem_layer_alt", "stem_layer_third", "slope200_probe", "edgepass_probe", "edgefail_probe", "join200_probe", "join200_edgepass_probe", "join200_edgefail_probe", "flat180_probe", "join180_probe", "slope180_probe", "reverse180_probe", "join_probe", "layer_slope_probe") and result["internal_join_adjacent_delta_full_scale"] is not None and result["internal_join_adjacent_delta_full_scale"] > .03:
            measurements[name]["failures"].append("sections: internal join adjacent sample gap > .03 full scale")
        if name in ("stem_layer", "stem_layer_alt", "stem_layer_third", "slope200_probe", "edgepass_probe", "edgefail_probe", "join200_probe", "join200_edgepass_probe", "join200_edgefail_probe", "flat180_probe", "join180_probe", "slope180_probe", "reverse180_probe", "layer_slope_probe") and result["internal_join_side_slope_mismatch_full_scale_per_sample"] is not None and result["internal_join_side_slope_mismatch_full_scale_per_sample"] > .001:
            measurements[name]["failures"].append("sections: internal join side slope mismatch > .001 full scale per sample")
    mode = "probe-transport-extsuffix-wav-r69" if args.probe_transport_extsuffix_wav_r69 else "probe-transport-extsuffix-bin-r69" if args.probe_transport_extsuffix_bin_r69 else "probe-transport-extsuffix-txw-r69" if args.probe_transport_extsuffix_txw_r69 else "probe-transport-extsuffix-f32-r69" if args.probe_transport_extsuffix_f32_r69 else "probe-transport-extsuffix-snd-r69" if args.probe_transport_extsuffix_snd_r69 else "probe-transport-posttable-nomatch-r68" if args.probe_transport_posttable_nomatch_r68 else "probe-transport-txw-piperefuse-r68" if args.probe_transport_txw_piperefuse_r68 else "probe-transport-preempt-act-r67" if args.probe_transport_preempt_act_r67 else "probe-transport-preempt-gsrt-r67" if args.probe_transport_preempt_gsrt_r67 else "probe-transport-preempt-hcom-r67" if args.probe_transport_preempt_hcom_r67 else "probe-transport-preempt-both-r67" if args.probe_transport_preempt_both_r67 else "probe-transport-dec-hcom-r67" if args.probe_transport_dec_hcom_r67 else "probe-transport-dec-act-r67" if args.probe_transport_dec_act_r67 else "probe-transport-lengate-gsrt-24-r67" if args.probe_transport_lengate_gsrt_24_r67 else "probe-transport-lengate-gsrt-25-r67" if args.probe_transport_lengate_gsrt_25_r67 else "probe-transport-lengate-hcom-131-r67" if args.probe_transport_lengate_hcom_131_r67 else "probe-transport-lengate-hcom-132-r67" if args.probe_transport_lengate_hcom_132_r67 else "probe-ui-dec-hcom-r66" if args.probe_ui_dec_hcom_r66 else "probe-ui-dec-act-r66" if args.probe_ui_dec_act_r66 else "probe-ui-lengate-gsrt-24-r66" if args.probe_ui_lengate_gsrt_24_r66 else "probe-ui-lengate-gsrt-25-r66" if args.probe_ui_lengate_gsrt_25_r66 else "probe-ui-lengate-hcom-131-r66" if args.probe_ui_lengate_hcom_131_r66 else "probe-ui-lengate-hcom-132-r66" if args.probe_ui_lengate_hcom_132_r66 else "probe-ui-preempt-act-r65" if args.probe_ui_preempt_act_r65 else "probe-ui-preempt-gsrt-r65" if args.probe_ui_preempt_gsrt_r65 else "probe-ui-preempt-hcom-r65" if args.probe_ui_preempt_hcom_r65 else "probe-ui-preempt-both-r65" if args.probe_ui_preempt_both_r65 else "probe-ui-extensible-valid-8-r64" if args.probe_ui_extensible_valid_8_r64 else "probe-ui-extensible-valid-9-r64" if args.probe_ui_extensible_valid_9_r64 else "probe-ui-extensible-valid-24-r64" if args.probe_ui_extensible_valid_24_r64 else "probe-ui-extensible-valid-25-r64" if args.probe_ui_extensible_valid_25_r64 else "probe-ui-extensible-valid-56-r64" if args.probe_ui_extensible_valid_56_r64 else "probe-ui-extensible-valid-57-r64" if args.probe_ui_extensible_valid_57_r64 else "probe-ui-route-act-84-r63" if args.probe_ui_route_act_84_r63 else "probe-ui-route-act-00-r63" if args.probe_ui_route_act_00_r63 else "probe-ui-extensible-valid-24-r62" if args.probe_ui_extensible_valid_24_r62 else ("probe-ui-extensible-valid-32-r62" if args.probe_ui_extensible_valid_32_r62 else ("probe-ui-extensible-valid-17-r61" if args.probe_ui_extensible_valid_17_r61 else ("probe-ui-extensible-valid-16-r61" if args.probe_ui_extensible_valid_16_r61 else ("probe-ui-extensible-valid-0-r60" if args.probe_ui_extensible_valid_0_r60 else ("probe-ui-extensible-valid-16-r60" if args.probe_ui_extensible_valid_16_r60 else ("probe-ui-extensible-valid-13-r59" if args.probe_ui_extensible_valid_13_r59 else ("probe-ui-extensible-valid-16-r59" if args.probe_ui_extensible_valid_16_r59 else ("probe-ui-extensible-valid-14-r58" if args.probe_ui_extensible_valid_14_r58 else ("probe-ui-extensible-valid-16-r58" if args.probe_ui_extensible_valid_16_r58 else ("probe-ui-extensible-valid-15" if args.probe_ui_extensible_valid_15 else ("probe-ui-extensible-valid-16" if args.probe_ui_extensible_valid_16 else ("probe-ui-extensible-mask-zero" if args.probe_ui_extensible_mask_zero else ("probe-ui-extensible-mask-center" if args.probe_ui_extensible_mask_center else ("probe-ui-extensible-pcm16" if args.probe_ui_extensible_pcm16 else ("probe-ui-standard-pcm16-r55" if args.probe_ui_standard_pcm16_r55 else ("probe-ui-pcm32" if args.probe_ui_pcm32 else ("probe-ui-pcm16-r54" if args.probe_ui_pcm16_r54 else ("probe-ui-float32" if args.probe_ui_float32 else ("probe-ui-pcm16-r53" if args.probe_ui_pcm16_r53 else ("probe-ui-pcm8" if args.probe_ui_pcm8 else ("probe-ui-pcm16-r52" if args.probe_ui_pcm16_r52 else ("probe-ui-pcm24" if args.probe_ui_pcm24 else ("probe-ui-pcm16" if args.probe_ui_pcm16 else ("probe-ui-channel-stereo" if args.probe_ui_channel_stereo else ("probe-ui-channel-mono" if args.probe_ui_channel_mono else ("probe-ui-rate-48001" if args.probe_ui_rate_48001 else ("probe-ui-rate-48000-r49" if args.probe_ui_rate_48000_r49 else ("probe-ui-rate-47999" if args.probe_ui_rate_47999 else ("probe-ui-rate-48000" if args.probe_ui_rate_48000 else ("probe-ui-upper-centroid-below" if args.probe_ui_upper_centroid_below else ("probe-ui-upper-centroid-above" if args.probe_ui_upper_centroid_above else ("probe-ui-absolute-centroid-below" if args.probe_ui_absolute_centroid_below else ("probe-ui-absolute-centroid-above" if args.probe_ui_absolute_centroid_above else ("probe-ui-lower-tolerance-5713" if args.probe_ui_lower_tolerance_5713 else ("probe-ui-lower-tolerance-5711" if args.probe_ui_lower_tolerance_5711 else ("probe-ui-tolerance-5807" if args.probe_ui_tolerance_5807 else ("probe-ui-tolerance-5809" if args.probe_ui_tolerance_5809 else ("probe-ui-crest-46" if args.probe_ui_crest_46 else ("probe-ui-crest-47" if args.probe_ui_crest_47 else ("probe-ui-peak-31129" if args.probe_ui_peak_31129 else ("probe-ui-peak-31130" if args.probe_ui_peak_31130 else ("probe-outer-slope-32" if args.probe_outer_slope_32 else ("probe-outer-slope-33" if args.probe_outer_slope_33 else ("probe-outer-endpoint-983" if args.probe_outer_endpoint_983 else ("probe-outer-endpoint-984" if args.probe_outer_endpoint_984 else ("probe-ambience-orientation-forward" if args.probe_ambience_orientation_forward else ("probe-ambience-orientation-reverse" if args.probe_ambience_orientation_reverse else ("probe-ambience-centroid-above" if args.probe_ambience_centroid_above else ("probe-ambience-centroid-below" if args.probe_ambience_centroid_below else ("probe-ui-mixed-pass" if args.probe_ui_mixed_pass else ("probe-ui-joint-below" if args.probe_ui_joint_below else ("probe-ui-orientation-forward" if args.probe_ui_orientation_forward else ("probe-ui-orientation-reverse" if args.probe_ui_orientation_reverse else ("probe-ui-lower-centroid-below" if args.probe_ui_lower_centroid_below else ("probe-ui-lower-centroid-above" if args.probe_ui_lower_centroid_above else ("probe-ui-centroid-below" if args.probe_ui_centroid_below else ("probe-ui-centroid-above" if args.probe_ui_centroid_above else ("probe-ui-duration-below" if args.probe_ui_duration_below else ("probe-ui-duration-at" if args.probe_ui_duration_at else ("probe-ui-clone" if args.probe_ui_clone else ("probe-layer-third-join-edge-pass" if args.probe_layer_third_join_edge_pass else ("probe-layer-third-join-edge-fail" if args.probe_layer_third_join_edge_fail else ("probe-layer-third-join" if args.probe_layer_third_join else ("probe-layer-third-slope-edge-pass" if args.probe_layer_third_slope_edge_pass else ("probe-layer-third-slope-edge-fail" if args.probe_layer_third_slope_edge_fail else "probe-layer-third-slope" if args.probe_layer_third_slope else ("probe-layer-alt-reverse" if args.probe_layer_alt_reverse else ("probe-layer-alt-slope" if args.probe_layer_alt_slope else ("probe-layer-alt-join" if args.probe_layer_alt_join else ("probe-layer-alt-flat" if args.probe_layer_alt_flat else ("probe-layer-slope" if args.probe_layer_slope else ("probe-layer-join" if args.probe_layer_join else ("probe-layer-flat" if args.probe_layer_flat else ("probe-flat" if args.probe_flat else ("probe-slope" if args.probe_slope else ("probe-failing" if args.probe_failing else "normal")))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))
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
               "ui_family_comparisons": ui_family_comparisons,
               "impact_family_comparisons": impact_family_comparisons,
               "movement_family_comparisons": movement_family_comparisons,
               "ambience_family_comparisons": ambience_family_comparisons, "sections": sections}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    suffix = "-transport-extsuffix-wav-r69" if args.probe_transport_extsuffix_wav_r69 else "-transport-extsuffix-bin-r69" if args.probe_transport_extsuffix_bin_r69 else "-transport-extsuffix-txw-r69" if args.probe_transport_extsuffix_txw_r69 else "-transport-extsuffix-f32-r69" if args.probe_transport_extsuffix_f32_r69 else "-transport-extsuffix-snd-r69" if args.probe_transport_extsuffix_snd_r69 else "-transport-posttable-nomatch-r68" if args.probe_transport_posttable_nomatch_r68 else "-transport-txw-piperefuse-r68" if args.probe_transport_txw_piperefuse_r68 else "-transport-preempt-act-r67" if args.probe_transport_preempt_act_r67 else "-transport-preempt-gsrt-r67" if args.probe_transport_preempt_gsrt_r67 else "-transport-preempt-hcom-r67" if args.probe_transport_preempt_hcom_r67 else "-transport-preempt-both-r67" if args.probe_transport_preempt_both_r67 else "-transport-dec-hcom-r67" if args.probe_transport_dec_hcom_r67 else "-transport-dec-act-r67" if args.probe_transport_dec_act_r67 else "-transport-lengate-gsrt-24-r67" if args.probe_transport_lengate_gsrt_24_r67 else "-transport-lengate-gsrt-25-r67" if args.probe_transport_lengate_gsrt_25_r67 else "-transport-lengate-hcom-131-r67" if args.probe_transport_lengate_hcom_131_r67 else "-transport-lengate-hcom-132-r67" if args.probe_transport_lengate_hcom_132_r67 else "-ui-dec-hcom-r66" if args.probe_ui_dec_hcom_r66 else "-ui-dec-act-r66" if args.probe_ui_dec_act_r66 else "-ui-lengate-gsrt-24-r66" if args.probe_ui_lengate_gsrt_24_r66 else "-ui-lengate-gsrt-25-r66" if args.probe_ui_lengate_gsrt_25_r66 else "-ui-lengate-hcom-131-r66" if args.probe_ui_lengate_hcom_131_r66 else "-ui-lengate-hcom-132-r66" if args.probe_ui_lengate_hcom_132_r66 else "-ui-preempt-act-r65" if args.probe_ui_preempt_act_r65 else "-ui-preempt-gsrt-r65" if args.probe_ui_preempt_gsrt_r65 else "-ui-preempt-hcom-r65" if args.probe_ui_preempt_hcom_r65 else "-ui-preempt-both-r65" if args.probe_ui_preempt_both_r65 else "-ui-extensible-valid-8-r64" if args.probe_ui_extensible_valid_8_r64 else "-ui-extensible-valid-9-r64" if args.probe_ui_extensible_valid_9_r64 else "-ui-extensible-valid-24-r64" if args.probe_ui_extensible_valid_24_r64 else "-ui-extensible-valid-25-r64" if args.probe_ui_extensible_valid_25_r64 else "-ui-extensible-valid-56-r64" if args.probe_ui_extensible_valid_56_r64 else "-ui-extensible-valid-57-r64" if args.probe_ui_extensible_valid_57_r64 else "-ui-route-act-84-r63" if args.probe_ui_route_act_84_r63 else "-ui-route-act-00-r63" if args.probe_ui_route_act_00_r63 else "-ui-extensible-valid-24-r62" if args.probe_ui_extensible_valid_24_r62 else ("-ui-extensible-valid-32-r62" if args.probe_ui_extensible_valid_32_r62 else ("-ui-extensible-valid-17-r61" if args.probe_ui_extensible_valid_17_r61 else ("-ui-extensible-valid-16-r61" if args.probe_ui_extensible_valid_16_r61 else ("-ui-extensible-valid-0-r60" if args.probe_ui_extensible_valid_0_r60 else ("-ui-extensible-valid-16-r60" if args.probe_ui_extensible_valid_16_r60 else ("-ui-extensible-valid-13-r59" if args.probe_ui_extensible_valid_13_r59 else ("-ui-extensible-valid-16-r59" if args.probe_ui_extensible_valid_16_r59 else ("-ui-extensible-valid-14-r58" if args.probe_ui_extensible_valid_14_r58 else ("-ui-extensible-valid-16-r58" if args.probe_ui_extensible_valid_16_r58 else ("-ui-extensible-valid-15" if args.probe_ui_extensible_valid_15 else ("-ui-extensible-valid-16" if args.probe_ui_extensible_valid_16 else ("-ui-extensible-mask-zero" if args.probe_ui_extensible_mask_zero else ("-ui-extensible-mask-center" if args.probe_ui_extensible_mask_center else ("-ui-extensible-pcm16" if args.probe_ui_extensible_pcm16 else ("-ui-standard-pcm16-r55" if args.probe_ui_standard_pcm16_r55 else ("-ui-pcm32" if args.probe_ui_pcm32 else ("-ui-pcm16-r54" if args.probe_ui_pcm16_r54 else ("-ui-float32" if args.probe_ui_float32 else ("-ui-pcm16-r53" if args.probe_ui_pcm16_r53 else ("-ui-pcm8" if args.probe_ui_pcm8 else ("-ui-pcm16-r52" if args.probe_ui_pcm16_r52 else ("-ui-pcm24" if args.probe_ui_pcm24 else ("-ui-pcm16" if args.probe_ui_pcm16 else ("-ui-channel-stereo" if args.probe_ui_channel_stereo else ("-ui-channel-mono" if args.probe_ui_channel_mono else ("-ui-rate-48001" if args.probe_ui_rate_48001 else ("-ui-rate-48000-r49" if args.probe_ui_rate_48000_r49 else ("-ui-rate-47999" if args.probe_ui_rate_47999 else ("-ui-rate-48000" if args.probe_ui_rate_48000 else ("-ui-upper-centroid-below" if args.probe_ui_upper_centroid_below else ("-ui-upper-centroid-above" if args.probe_ui_upper_centroid_above else ("-ui-absolute-centroid-below" if args.probe_ui_absolute_centroid_below else ("-ui-absolute-centroid-above" if args.probe_ui_absolute_centroid_above else ("-ui-lower-tolerance-5713" if args.probe_ui_lower_tolerance_5713 else ("-ui-lower-tolerance-5711" if args.probe_ui_lower_tolerance_5711 else ("-ui-tolerance-5807" if args.probe_ui_tolerance_5807 else ("-ui-tolerance-5809" if args.probe_ui_tolerance_5809 else ("-ui-crest-46" if args.probe_ui_crest_46 else ("-ui-crest-47" if args.probe_ui_crest_47 else ("-ui-peak-31129" if args.probe_ui_peak_31129 else ("-ui-peak-31130" if args.probe_ui_peak_31130 else ("-outer-slope-32" if args.probe_outer_slope_32 else ("-outer-slope-33" if args.probe_outer_slope_33 else ("-outer-endpoint-983" if args.probe_outer_endpoint_983 else ("-outer-endpoint-984" if args.probe_outer_endpoint_984 else ("-ambience-orientation-forward" if args.probe_ambience_orientation_forward else ("-ambience-orientation-reverse" if args.probe_ambience_orientation_reverse else ("-ambience-centroid-above" if args.probe_ambience_centroid_above else ("-ambience-centroid-below" if args.probe_ambience_centroid_below else ("-ui-mixed-pass" if args.probe_ui_mixed_pass else ("-ui-joint-below" if args.probe_ui_joint_below else ("-ui-orientation-forward" if args.probe_ui_orientation_forward else ("-ui-orientation-reverse" if args.probe_ui_orientation_reverse else ("-ui-lower-centroid-below" if args.probe_ui_lower_centroid_below else ("-ui-lower-centroid-above" if args.probe_ui_lower_centroid_above else ("-ui-centroid-below" if args.probe_ui_centroid_below else ("-ui-centroid-above" if args.probe_ui_centroid_above else ("-ui-duration-below" if args.probe_ui_duration_below else ("-ui-duration-at" if args.probe_ui_duration_at else ("-ui-clone" if args.probe_ui_clone else ("-layer-third-join-edge-pass" if args.probe_layer_third_join_edge_pass else ("-layer-third-join-edge-fail" if args.probe_layer_third_join_edge_fail else ("-layer-third-join" if args.probe_layer_third_join else ("-layer-third-slope-edge-pass" if args.probe_layer_third_slope_edge_pass else ("-layer-third-slope-edge-fail" if args.probe_layer_third_slope_edge_fail else "-layer-third-slope" if args.probe_layer_third_slope else ("-layer-alt-reverse" if args.probe_layer_alt_reverse else ("-layer-alt-slope" if args.probe_layer_alt_slope else ("-layer-alt-join" if args.probe_layer_alt_join else ("-layer-alt-flat" if args.probe_layer_alt_flat else ("-layer-slope" if args.probe_layer_slope else ("-layer-join" if args.probe_layer_join else ("-layer-flat" if args.probe_layer_flat else ("-flat" if args.probe_flat else ("-slope" if args.probe_slope else ("-failing" if args.probe_failing else "-normal")))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))
    out = ROOT / "live" / "runs" / (stamp + suffix)
    out.mkdir(parents=True)
    (out / "measurements.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    failed = {k: v["failures"] for k,v in measurements.items() if v["failures"]}
    print(json.dumps({"receipt": str(out / "measurements.json"), "failures": failed}))
    return bool(failed)


if __name__ == "__main__":
    sys.exit(main())
