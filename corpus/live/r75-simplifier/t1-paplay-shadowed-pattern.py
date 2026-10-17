#!/usr/bin/env python3
"""Headless checks of deterministic WAV fixtures; JSON receipt even on failure."""
import argparse
import ctypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import signal
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
# r70: the hold is a MEASURED bound, not a chosen point — parameterized via
# MEASURE_FIFO_WRITER_HOLD_S (ad-hoc legs; the receipt records the effective
# value so an override is never silent) and swept by
# --probe-fifo-hold-ladder-r70. The default stays 1.0 s so every prior
# member/receipt is byte-stable.
TRANSPORT_R67_FIFO_WRITER_HOLD_S = 1.0
FIFO_WRITER_HOLD_ENV = "MEASURE_FIFO_WRITER_HOLD_S"
# r70 ladder grid + the chunked-feed variant shape. chunked keeps the writer
# continuously attached during delivery (~CHUNKS*GAP s of attach window
# before the post-write hold) — the 'correctly blocking writer' arm of the
# r70 claim: if the verdict is binary on writer-attached-at-open-#2, chunked
# is stable at hold 0 whenever the feed window alone covers open #2.
TRANSPORT_R70_HOLDS = (0.0, 0.05, 0.2, 0.5, 1.0, 2.0)
TRANSPORT_R70_REPS = 10
TRANSPORT_R70_FEEDS = ("oneshot", "chunked")
TRANSPORT_R70_CHUNK_BYTES = 100
TRANSPORT_R70_CHUNK_GAP_S = 0.05
TRANSPORT_R70_MEMBER = "dec_act"
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


def fifo_writer_hold_s():
    """Effective fifo writer hold for the standard arm: the pinned 1.0 s
    default unless MEASURE_FIFO_WRITER_HOLD_S overrides (ad-hoc legs only —
    transport_protocol records the effective value, so an override is never
    silent)."""
    return float(os.environ.get(FIFO_WRITER_HOLD_ENV,
                                TRANSPORT_R67_FIFO_WRITER_HOLD_S))


def fifo_feed(fifo, data, hold_s, feed="oneshot"):
    """Writer protocol of the fifo arm: open for write (blocks until the
    reader attaches), deliver the member bytes per `feed`, then linger
    hold_s holding the fifo open so the ffmpeg bridge's open #2 resolves.
    "oneshot" is the r67 protocol verbatim; "chunked" writes CHUNK_BYTES
    chunks separated by CHUNK_GAP_S — a continuously-attached feed window
    before the same linger. OSError is swallowed so a reader that exits
    early never crashes the writer thread."""
    try:
        with fifo.open("wb") as fh:
            if feed == "chunked":
                for i in range(0, len(data), TRANSPORT_R70_CHUNK_BYTES):
                    fh.write(data[i:i + TRANSPORT_R70_CHUNK_BYTES])
                    fh.flush()
                    time.sleep(TRANSPORT_R70_CHUNK_GAP_S)
            else:
                fh.write(data)
                fh.flush()
            time.sleep(hold_s)
    except OSError:
        pass


def fifo_feed_span_s(data_len, feed):
    """Delivery window of the chunked feed (attach time before the hold)."""
    if feed != "chunked":
        return 0.0
    return -(-data_len // TRANSPORT_R70_CHUNK_BYTES) * TRANSPORT_R70_CHUNK_GAP_S


def reap_fifo_orphans(fifo):
    """SIGKILL any survivor still carrying this fifo's path on its cmdline.

    The sox ffmpeg bridge grandchild can escape the child's process group
    (r70-critic observed one alive 5+ min after a blocked ladder leg —
    killpg is necessary but not sufficient); a cmdline sweep is the
    verdict-neutral backstop for both fifo legs."""
    needle = str(fifo).encode()
    for pid_dir in Path("/proc").iterdir():
        if not pid_dir.name.isdigit():
            continue
        try:
            cmd = (pid_dir / "cmdline").read_bytes()
        except OSError:
            continue
        if needle in cmd:
            try:
                os.kill(int(pid_dir.name), signal.SIGKILL)
            except OSError:
                pass


def transport_matrix(path, hold_s=None, feed="oneshot"):
    """The member's detection+decode verdict on each of the four transports.
    hold_s/feed parameterize only the fifo arm; defaults reproduce the r67
    protocol (env-resolved 1.0 s oneshot) so prior receipts stay byte-stable."""
    hold_s = fifo_writer_hold_s() if hold_s is None else hold_s
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
        data = path.read_bytes()

        writer = threading.Thread(target=fifo_feed, args=(fifo, data, hold_s, feed),
                                  daemon=True)
        writer.start()
        try:
            arms["fifo_path"] = transport_leg(["sox", "-V6", str(fifo), "-n", "stat"],
                                              path.name)
        finally:
            writer.join(timeout=hold_s + fifo_feed_span_s(len(data), feed) + 5)
            reap_fifo_orphans(fifo)
    for transport, named, seekable in TRANSPORT_R67_ARMS:
        arms[transport]["named"] = named
        arms[transport]["seekable"] = seekable
    return arms


def fifo_hold_leg(path, hold_s, feed):
    """One fifo_path leg at an explicit writer hold + feed shape, for the r70
    ladder. Verdict fields are identical to transport_leg; the
    runner differs deliberately: the child runs in its own session and a
    timeout kills the process GROUP, because a blocked leg means the ffmpeg
    bridge grandchild is dead-locked in openat(fifo, O_RDONLY) (open #2 with
    no writer attached) and a parent-only kill would orphan one sleeper per
    rep."""
    with tempfile.TemporaryDirectory(prefix="fifo-hold-r70-") as tmp:
        fifo = Path(tmp) / path.name
        os.mkfifo(fifo)
        data = path.read_bytes()
        writer = threading.Thread(target=fifo_feed, args=(fifo, data, hold_s, feed),
                                  daemon=True)
        writer.start()
        try:
            proc = subprocess.Popen(["sox", "-V6", str(fifo), "-n", "stat"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    start_new_session=True)
            try:
                _, err = proc.communicate(timeout=TRANSPORT_R67_ARM_TIMEOUT_S)
                text = err.decode(errors="replace")
                code = proc.returncode
                emitted = transport_error(text)
                error = emitted
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                _, err = proc.communicate()
                text = err.decode(errors="replace")
                code = None
                # `error` stays the leg-level outcome (transport_leg's blocked
                # convention); `verdict_emitted` records the FAIL line when the
                # sox parent already emitted it — a blocked leg means the
                # ffmpeg grandchild still holds the stderr pipe open while
                # dead-blocked in openat, not that the verdict differed.
                emitted = transport_error(text)
                error = f"blocked: no verdict within {TRANSPORT_R67_ARM_TIMEOUT_S} s"
            leg = {"input": path.name,
                   "sox_detected_format": (m.group(1) if (m := re.search(
                       r"detected file format type `(\S+?)'", text)) else None),
                   "sox_route": None,
                   "exit_code": code,
                   "samples_read": (int(m.group(1)) if (m := re.search(
                       r"Samples read:\s*(\d+)", text)) else None),
                   "error": error, "verdict_emitted": emitted}
            leg["sox_route"] = ("ffmpeg" if (leg["sox_detected_format"] == "act")
                                or "(ffmpeg)" in text else
                                "native" if leg["sox_detected_format"] else "none")
            tail = text.strip().splitlines()
            if tail:
                leg["stderr_tail"] = re.sub(r"`[^']*'", "`<input>'",
                                            re.sub(r" @ 0x[0-9a-f]+\]", "]",
                                                   tail[-1]))[-160:]
        finally:
            writer.join(timeout=hold_s + fifo_feed_span_s(len(data), feed) + 5)
            reap_fifo_orphans(fifo)
    leg["named"], leg["seekable"] = True, False
    return leg


def fifo_hold_ladder_entry(member, path):
    """r70 receipt entry: the fifo writer-hold LADDER on the dec_act member —
    per-{feed, hold} cell verdict distributions, not a point pin. h* per feed
    is the smallest hold whose entire distribution equals the pinned arm's
    signature; None when no hold in the ladder is rep-stable."""
    cells = []
    for feed in TRANSPORT_R70_FEEDS:
        for hold in TRANSPORT_R70_HOLDS:
            reps = []
            for rep in range(TRANSPORT_R70_REPS):
                leg = fifo_hold_leg(path, hold, feed)
                leg["rep"] = rep
                reps.append(leg)
            dist = {}
            for leg in reps:
                sig = json.dumps([leg["sox_detected_format"], leg["sox_route"],
                                  leg["exit_code"], leg["samples_read"],
                                  leg["error"]])
                dist[sig] = dist.get(sig, 0) + 1
            cells.append({"fifo_feed": feed, "fifo_writer_hold_s": hold,
                          "reps_planned": TRANSPORT_R70_REPS, "reps": reps,
                          "verdict_distribution": [
                              {"signature": dict(zip(
                                  ("sox_detected_format", "sox_route", "exit_code",
                                   "samples_read", "error"), json.loads(sig))),
                               "count": count}
                              for sig, count in sorted(dist.items(),
                                                       key=lambda kv: -kv[1])]})
    # The reference verdict is the pinned arm's signature (oneshot @1.0 s —
    # the value every committed receipt carries).
    pinned = next(c for c in cells
                  if c["fifo_feed"] == "oneshot" and
                  c["fifo_writer_hold_s"] == TRANSPORT_R67_FIFO_WRITER_HOLD_S)
    pinned_dist = pinned["verdict_distribution"]
    reference = (pinned_dist[0]["signature"]
                 if len(pinned_dist) == 1 and
                 pinned_dist[0]["count"] == TRANSPORT_R70_REPS else None)
    divergent = {}
    bands = {}
    for feed in TRANSPORT_R70_FEEDS:
        feed_cells = [c for c in cells if c["fifo_feed"] == feed]
        stable = [c["fifo_writer_hold_s"] for c in feed_cells
                  if len(c["verdict_distribution"]) == 1 and
                  c["verdict_distribution"][0]["signature"] == reference]
        # The honest bound shape (r70-critic): not a point h* but the
        # transition zone — the highest hold still diverging from the
        # pinned signature vs the lowest all-stable hold, per feed, on
        # THIS run's host load. A ms-scale fifo race makes h* a
        # load-dependent zone, never a host constant.
        div_holds = [c["fifo_writer_hold_s"] for c in feed_cells
                     if not (len(c["verdict_distribution"]) == 1 and
                             c["verdict_distribution"][0]["signature"]
                             == reference)]
        bands[feed] = {
            "max_divergent_hold_s": max(div_holds) if div_holds else None,
            "min_stable_hold_s": min(stable) if stable else None}
        divergent[feed] = [
            {"fifo_writer_hold_s": c["fifo_writer_hold_s"],
             "verdict_distribution": c["verdict_distribution"]}
            for c in feed_cells
            if not (len(c["verdict_distribution"]) == 1 and
                    c["verdict_distribution"][0]["signature"] == reference)]
    entry = {"path": str(path.relative_to(ROOT)), "pair_member": member,
             "probe": "fifo_writer_hold_s determinism ladder — 1.0 s as a measured bound",
             "transport_protocol": {
                 "arm_timeout_s": TRANSPORT_R67_ARM_TIMEOUT_S,
                 "fifo_writer_hold_s_ladder": list(TRANSPORT_R70_HOLDS),
                 "fifo_feeds": {
                     "oneshot": "one-shot write then writer lingers",
                     "chunked": (f"{TRANSPORT_R70_CHUNK_BYTES}-B chunked write "
                                 f"({TRANSPORT_R70_CHUNK_GAP_S} s inter-chunk) "
                                 f"then writer lingers")},
                 "reps_per_cell": TRANSPORT_R70_REPS,
                 "timeout_kill": ("process-group SIGKILL (start_new_session + "
                                  "killpg) + a /proc cmdline reap sweep — the "
                                  "bridge grandchild can escape the child's "
                                  "group (r70-critic falsified killpg-only "
                                  "via a 5+-min survivor)")},
             "hold_ladder": cells,
             "reference_signature": reference,
             # Critic-corrected shape: a transition zone per feed, not a
             # point h*. chunked@h*=0 is the binary-arm control (feed
             # duration itself spans open-#2), not a hold bound.
             "hold_transition_band_s": bands,
             "hstar_semantics": ("load-dependent transition zone on this "
                                 "host/run — {max divergent, min all-stable} "
                                 "per feed — never a host constant; the "
                                 "outcome space is attach x "
                                 "close-before-deadline, not "
                                 "binary-on-attach"),
             "failures": []}
    if reference is None:
        entry["failures"].append(
            "transport: fifo arm non-deterministic at the pinned hold "
            f"{TRANSPORT_R67_FIFO_WRITER_HOLD_S} s: {pinned_dist}")
    for feed in TRANSPORT_R70_FEEDS:
        if divergent[feed]:
            desc = ", ".join(
                f"h={d['fifo_writer_hold_s']} -> " +
                "/".join(f"{s['count']}x(exit {s['signature']['exit_code']}, "
                         f"{s['signature']['error']})"
                         for s in d["verdict_distribution"])
                for d in divergent[feed])
            entry["failures"].append(
                f"transport: {feed} fifo verdict diverges from the pinned "
                f"signature below/around the measured bound ({desc}); "
                f"transition band {bands[feed]}")
    return entry


# r71 second-decoder runtime: ffmpeg n9.0.1 / ffprobe on the same members and
# the same 4-transport matrix. Declared falsifiable claim: ffmpeg tracks
# CONTENT probing, not the suffix axis -- it accepts members SoX
# extension-rejects when content is parseable, and rejects by content where
# SoX accepts by suffix. The member set reuses the tracked transport corpus:
# r69's five identical-byte extension members isolate the suffix axis; the
# r68 pair isolates post-table/no-match content; dec_act/dec_hcom are the
# ffmpeg-bridge members whose SoX verdicts already route through ffmpeg.
TRANSPORT_R71_MEMBERS = {
    "posttable_nomatch": TRANSPORT_R68_MEMBERS["posttable_nomatch"],
    "txw_piperefuse": TRANSPORT_R68_MEMBERS["txw_piperefuse"],
    "dec_act": TRANSPORT_R67_MEMBERS["dec_act"],
    "dec_hcom": TRANSPORT_R67_MEMBERS["dec_hcom"],
    "extsuffix_wav": TRANSPORT_R69_MEMBERS["extsuffix_wav"],
    "extsuffix_bin": TRANSPORT_R69_MEMBERS["extsuffix_bin"],
    "extsuffix_txw": TRANSPORT_R69_MEMBERS["extsuffix_txw"],
    "extsuffix_f32": TRANSPORT_R69_MEMBERS["extsuffix_f32"],
    "extsuffix_snd": TRANSPORT_R69_MEMBERS["extsuffix_snd"],
}
TRANSPORT_R71_ARM_TIMEOUT_S = 15


def ffprobe_leg(path_arg, label, data=None, stdin_path=None, feed=None):
    """One bounded ffmpeg leg -> detection + decode verdict.

    ffprobe reports the detection verdict (format_name + probe_score);
    `ffmpeg -v error -i <in> -f null -` reports the decode verdict.
    <in> is a path for named transports or `pipe:` for the anonymous
    stdin transports. stderr tails keep ASLR/path normalization.

    `feed` = (fifo_dir, filename, data, hold_s): when given, EACH of the
    two subprocesses gets its own fifo + writer — the r71 fix for the
    r67-analog defect where the second process opened the (already
    writer-dead) fifo and blocked forever. transport_protocol records the
    effective hold so an env override is never silent."""
    kw = {"input": data} if data is not None else {}
    # stdin_path: a SEEKABLE backing fd for the `pipe:` protocol — each
    # subprocess must get a FRESH fd at offset 0 (an fh consumed by the
    # ffprobe leg would leave ffmpeg reading EOF; measured r71 artifact).
    if stdin_path is not None:
        data = None

    def run(argv, fifodata=None):
        fh = open(stdin_path, "rb") if stdin_path is not None else None
        if fifodata is None:
            try:
                proc = subprocess.run(argv, capture_output=True,
                                      timeout=TRANSPORT_R71_ARM_TIMEOUT_S,
                                      stdin=fh, **kw)
                return (proc.stdout.decode(errors="replace"),
                        proc.stderr.decode(errors="replace"),
                        proc.returncode, None)
            except subprocess.TimeoutExpired as exc:
                err = exc.stderr or b""
                return ((exc.stdout or b"").decode(errors="replace"),
                        err.decode(errors="replace"), None,
                        f"blocked: no verdict within {TRANSPORT_R71_ARM_TIMEOUT_S} s")
            finally:
                if fh is not None:
                    fh.close()
        tmp, fname, bytes_, hold = fifodata
        fifo = Path(tmp) / fname
        os.mkfifo(fifo)
        writer = threading.Thread(target=fifo_feed, args=(fifo, bytes_, hold),
                                  daemon=True)
        writer.start()
        try:
            proc = subprocess.run(argv, capture_output=True,
                                  timeout=TRANSPORT_R71_ARM_TIMEOUT_S)
            return (proc.stdout.decode(errors="replace"),
                    proc.stderr.decode(errors="replace"),
                    proc.returncode, None)
        except subprocess.TimeoutExpired as exc:
            err = exc.stderr or b""
            return ((exc.stdout or b"").decode(errors="replace"),
                    err.decode(errors="replace"), None,
                    f"blocked: no verdict within {TRANSPORT_R71_ARM_TIMEOUT_S} s")
        finally:
            writer.join(timeout=hold + 5)
            reap_fifo_orphans(fifo)
            fifo.unlink(missing_ok=True)

    if feed is None:
        probe_arg, fifodata = path_arg, None
    else:
        probe_arg, fifodata = str(Path(feed[0]) / feed[1]), feed
    pout, perr, pcode, perr_msg = run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=format_name,probe_score", "-of", "json", probe_arg],
        fifodata)
    fmt, score = None, None
    if pout.strip():
        try:
            j = json.loads(pout)
            fmt = j.get("format", {}).get("format_name")
            score = j.get("format", {}).get("probe_score")
        except json.JSONDecodeError:
            fmt = "json-parse-error"
    def _tail(err):
        lines = err.strip().splitlines()
        if not lines:
            return None
        t = re.sub(r"`[^']*'", "`<input>'", lines[-1])
        t = re.sub(r" @ 0x[0-9a-fA-F]+", "", t)   # ASLR module tags
        return t.replace(probe_arg, "<input>")[-160:]

    ptail = _tail(perr)

    dout, derr, dcode, derr_msg = run(
        ["ffmpeg", "-v", "error", "-i", probe_arg, "-f", "null", "-"],
        fifodata)
    dtail = _tail(derr)

    return {"input": label,
            "ffprobe_format": fmt, "probe_score": score,
            "ffprobe_exit": pcode, "ffprobe_error": perr_msg or ptail,
            "ffmpeg_exit": dcode, "ffmpeg_error": derr_msg or dtail}


def ffmpeg_transport_matrix(path, hold_s=None):
    """The member's ffmpeg verdict on each of the four transports. The fifo
    arm reuses the r67/r70 writer protocol (same fifo_feed + hold + reap) —
    a fifo reader with no attached writer blocks at open() just like sox's
    ffmpeg bridge."""
    hold_s = fifo_writer_hold_s() if hold_s is None else hold_s
    rel = str(path.relative_to(ROOT))
    arms = {}
    arms["file"] = ffprobe_leg(str(path), rel)
    data = path.read_bytes()
    arms["stdin_pipe"] = ffprobe_leg("pipe:", "pipe:", data=data)
    arms["redirected_fd"] = ffprobe_leg("pipe:", "pipe:", stdin_path=str(path))
    with tempfile.TemporaryDirectory(prefix="transport-r71-") as tmp:
        arms["fifo_path"] = ffprobe_leg(None, path.name,
                                        feed=(tmp, path.name, data, hold_s))
    for transport, named, seekable in TRANSPORT_R67_ARMS:
        arms[transport]["named"] = named
        arms[transport]["seekable"] = seekable
    return arms


def ffprobe_transport_entry(member, path):
    """r71 receipt entry: ffmpeg's per-transport verdict groups for one
    member -- the cross-decoder partition. Groups key on the ffmpeg
    detection+decode signature so a transport fork lands in the receipt,
    and ffprobe_groups key on the detection signature alone (ffmpeg can
    decode-diverge where ffprobe detection agrees)."""
    arms = ffmpeg_transport_matrix(path)
    groups, pgroups = [], []
    for transport in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
        arm = arms[transport]
        sig = (arm["ffprobe_format"], arm["ffmpeg_exit"], arm["ffmpeg_error"])
        psig = (arm["ffprobe_format"], arm["ffprobe_exit"], arm["ffprobe_error"])
        for group in groups:
            if group[0] == sig:
                group[1].append(transport); break
        else:
            groups.append((sig, [transport]))
        for group in pgroups:
            if group[0] == psig:
                group[1].append(transport); break
        else:
            pgroups.append((psig, [transport]))
    entry = {"path": str(path.relative_to(ROOT)), "pair_member": member,
             "decoder": "ffmpeg/ffprobe",
             "transport_axis": arms,
             "transport_protocol": {"arm_timeout_s": TRANSPORT_R71_ARM_TIMEOUT_S,
                                    "fifo_writer_hold_s": fifo_writer_hold_s(),
                                    "fifo_feed": "one-shot write then writer lingers"},
             "transport_verdict_groups": [
                 {"transports": ts, "ffprobe_format": sig[0],
                  "ffmpeg_exit": sig[1], "ffmpeg_error": sig[2]}
                 for sig, ts in groups],
             "ffprobe_verdict_groups": [
                 {"transports": ts, "ffprobe_format": sig[0],
                  "ffprobe_exit": sig[1], "ffprobe_error": sig[2]}
                 for sig, ts in pgroups],
             "transport_fork": len(groups) > 1,
             "failures": []}
    if entry["transport_fork"]:
        desc = " vs ".join("/".join(ts) + "=" + (sig[2] or str(sig[0]))
                           for sig, ts in groups)
        entry["failures"].append(
            f"transport: ffmpeg verdict forks across transports ({desc})")
    return entry


TRANSPORT_R72_MEMBERS = TRANSPORT_R71_MEMBERS   # same canonical 9


class _SF_INFO(ctypes.Structure):
    _fields_ = [("frames", ctypes.c_int64), ("samplerate", ctypes.c_int),
                ("channels", ctypes.c_int), ("format", ctypes.c_int),
                ("sections", ctypes.c_int), ("seekable", ctypes.c_int)]


class _SF_FORMAT_INFO(ctypes.Structure):
    _fields_ = [("format", ctypes.c_int), ("name", ctypes.c_char_p),
                ("extension", ctypes.c_char_p)]


try:
    _SNDFILE = ctypes.CDLL("libsndfile.so.1")
except OSError:
    # Host without libsndfile: the r72 legs record a blocked verdict and
    # every other fixture mode still imports + runs.
    _SNDFILE = None
if _SNDFILE is not None:
    _SNDFILE.sf_version_string.restype = ctypes.c_char_p
    _SNDFILE.sf_open.restype = ctypes.c_void_p
    _SNDFILE.sf_open.argtypes = [ctypes.c_char_p, ctypes.c_int,
                                 ctypes.POINTER(_SF_INFO)]
    _SNDFILE.sf_open_fd.restype = ctypes.c_void_p
    _SNDFILE.sf_open_fd.argtypes = [ctypes.c_int, ctypes.c_int,
                                    ctypes.POINTER(_SF_INFO), ctypes.c_int]
    _SNDFILE.sf_close.argtypes = [ctypes.c_void_p]
    _SNDFILE.sf_strerror.restype = ctypes.c_char_p
    _SNDFILE.sf_strerror.argtypes = [ctypes.c_void_p]
    _SNDFILE.sf_error_str.restype = ctypes.c_char_p
    _SNDFILE.sf_error_str.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                                      ctypes.c_size_t]
    _SNDFILE.sf_format_check.argtypes = [ctypes.POINTER(_SF_INFO)]
    _SNDFILE.sf_command.restype = ctypes.c_int
    _SNDFILE.sf_command.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                   ctypes.c_void_p, ctypes.c_int]
    _SNDFILE.sf_readf_short.restype = ctypes.c_int64
    _SNDFILE.sf_readf_short.argtypes = [ctypes.c_void_p,
                                        ctypes.POINTER(ctypes.c_short),
                                        ctypes.c_int64]
_SFM_READ = 0x10
_SFC_GET_FORMAT_MAJOR_COUNT = 0x1030
_SFC_GET_FORMAT_MAJOR = 0x1031
_SFC_GET_FORMAT_SUBTYPE_COUNT = 0x1032
_SFC_GET_FORMAT_SUBTYPE = 0x1033


def _sndfile_format_names():
    def enum(count_cmd, item_cmd):
        n = ctypes.c_int(0)
        _SNDFILE.sf_command(None, count_cmd, ctypes.byref(n), ctypes.sizeof(n))
        out = {}
        for i in range(n.value):
            fi = _SF_FORMAT_INFO()
            fi.format = i
            _SNDFILE.sf_command(None, item_cmd, ctypes.byref(fi),
                                ctypes.sizeof(fi))
            out[fi.format] = (fi.name.decode(),
                              (fi.extension or b"").decode())
        return out
    return {"majors": enum(_SFC_GET_FORMAT_MAJOR_COUNT, _SFC_GET_FORMAT_MAJOR),
            "subs": enum(_SFC_GET_FORMAT_SUBTYPE_COUNT, _SFC_GET_FORMAT_SUBTYPE)}


_SNDFILE_NAMES = (_sndfile_format_names() if _SNDFILE is not None
                  else {"majors": {}, "subs": {}})


def _sndfile_verdict(snd, info):
    """Detection + decode verdict for one opened handle. Decode is a
    single sf_readf_short drain with a 65536-frame cap — equal to a full
    drain on this corpus (largest member = 500 frames), not a proof of
    drain semantics past the cap."""
    if not snd:
        return {"format_hex": None, "format_name": None, "format_check": None,
                "frames": None, "samplerate": None, "channels": None,
                "sf_seekable": None, "read_frames": None,
                "error": _SNDFILE.sf_strerror(None).decode(errors="replace"),
                "error_str": None}
    names = _SNDFILE_NAMES
    mj = names["majors"].get(info.format & 0x0FFF0000, (None, None))
    st = names["subs"].get(info.format & 0x0000FFFF, (None, None))
    buf = (ctypes.c_short * 65536)()
    got = _SNDFILE.sf_readf_short(snd, buf, 65536)
    errbuf = ctypes.create_string_buffer(256)
    _SNDFILE.sf_error_str(snd, errbuf, 256)
    raw = errbuf.value.decode(errors="replace")
    _SNDFILE.sf_close(snd)
    return {"format_hex": hex(info.format),
            "format_name": f"{mj[0]}/{st[0]}" if mj[0] else None,
            "format_check": bool(_SNDFILE.sf_format_check(ctypes.byref(info))),
            "frames": info.frames, "samplerate": info.samplerate,
            "channels": info.channels, "sf_seekable": bool(info.seekable),
            "read_frames": got, "error": None,
            "error_str": None if raw in ("", "No Error.") else raw}


def _sndfile_leg(transport, path, data, hold_s):
    """One libsndfile leg, in-process (ctypes) so the anonymous arms use
    sf_open_fd honestly (a /dev/stdin path would be a NAMED open)."""
    if _SNDFILE is None:
        return {"format_hex": None, "format_name": None,
                "format_check": None, "frames": None, "samplerate": None,
                "channels": None, "sf_seekable": None, "read_frames": None,
                "error": "blocked: libsndfile unavailable on host",
                "error_str": None}
    class _Timeout(Exception):
        pass
    def _alarm(signum, frame):
        raise _Timeout()
    prev = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, TRANSPORT_R71_ARM_TIMEOUT_S)
    try:
        if transport == "file":
            info = _SF_INFO()
            return _sndfile_verdict(
                _SNDFILE.sf_open(os.fsencode(str(path)), _SFM_READ,
                                 ctypes.byref(info)), info)
        if transport == "stdin_pipe":
            r, w = os.pipe()
            try:
                os.write(w, data)
                os.close(w)
                info = _SF_INFO()
                return _sndfile_verdict(
                    _SNDFILE.sf_open_fd(r, _SFM_READ, ctypes.byref(info), 0),
                    info)
            finally:
                os.close(r)
        if transport == "redirected_fd":
            fd = os.open(str(path), os.O_RDONLY)
            try:
                info = _SF_INFO()
                return _sndfile_verdict(
                    _SNDFILE.sf_open_fd(fd, _SFM_READ, ctypes.byref(info), 0),
                    info)
            finally:
                os.close(fd)
        # fifo_path: named open of a real fifo; per-process writer (r71
        # convention: a consumer chain needs a fresh fifo+writer each)
        with tempfile.TemporaryDirectory(prefix="sndfile-r72-") as tmp:
            fifo = os.path.join(tmp, os.path.basename(str(path)))
            os.mkfifo(fifo)
            def feed():
                try:
                    with open(fifo, "wb") as w:
                        w.write(data)
                except OSError:
                    pass
                time.sleep(hold_s)
            t = threading.Thread(target=feed, daemon=True)
            t.start()
            try:
                info = _SF_INFO()
                return _sndfile_verdict(
                    _SNDFILE.sf_open(os.fsencode(fifo), _SFM_READ,
                                     ctypes.byref(info)), info)
            finally:
                t.join(timeout=hold_s + 5)
                reap_fifo_orphans(fifo)
    except _Timeout:
        return {"format_hex": None, "format_name": None, "format_check": None,
                "frames": None, "samplerate": None, "channels": None,
                "sf_seekable": None, "read_frames": None,
                "error": f"blocked: no verdict within {TRANSPORT_R71_ARM_TIMEOUT_S} s",
                "error_str": None}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, prev)


def sndfile_transport_entry(member, path):
    """r72 receipt entry: THIRD DECODER (libsndfile) on the canonical
    member x transport matrix. Decode verdict = one sf_readf_short drain
    (65536-frame cap, equal to full drain on this corpus); detection =
    the sf_open'ed SF_INFO format + name table. The receipt records the
    measured decoder partition; a transport fork lands as a failure per
    the r67 convention."""
    if _SNDFILE is None:
        return {"path": str(path.relative_to(ROOT)), "pair_member": member,
                "decoder": "libsndfile unavailable",
                "transport_axis": {},
                "transport_protocol": {"runtime": "blocked: libsndfile "
                                                  "unavailable on host"},
                "sndfile_info_cli": None,
                "transport_verdict_groups": [],
                "transport_fork": False,
                "failures": ["runtime: libsndfile unavailable on host"]}
    hold_s = fifo_writer_hold_s()
    data = path.read_bytes()
    arms = {t: _sndfile_leg(t, path, data, hold_s)
            for t in ("file", "stdin_pipe", "redirected_fd", "fifo_path")}
    for t, named, seekable in (("file", True, True), ("stdin_pipe", False, False),
                               ("redirected_fd", False, True),
                               ("fifo_path", True, False)):
        arms[t]["named"], arms[t]["seekable"] = named, seekable
    # sndfile-info CLI leg on the file arm only — exits 0 even on reject;
    # its Frames line is the container field, not a decode count (critic:
    # never key a verdict on it). Anonymous arms have no honest CLI arm.
    cli = None
    try:
        proc = subprocess.run(["sndfile-info", str(path)],
                              capture_output=True, timeout=15)
        out = proc.stdout.decode(errors="replace")
        def _find(rx):
            m = re.search(rx, out, re.M)
            return m.group(1).strip() if m else None
        lines = [ln.strip() for ln in out.strip().splitlines() if ln.strip()]
        cli = {"exit": proc.returncode,
               "format_hex": _find(r"^Format\s*:\s*(0x[0-9A-Fa-f]+)"),
               "frames_field": _find(r"^Frames\s*:\s*(\S+)"),
               "reason": (lines[-1] if lines and "Error" in out else None)}
    except (subprocess.TimeoutExpired, OSError) as exc:
        cli = {"exit": None, "error": str(exc)[:120]}
    groups = []
    for t in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
        sig = (arms[t]["format_name"], arms[t]["read_frames"], arms[t]["error"])
        for g in groups:
            if g[0] == sig:
                g[1].append(t); break
        else:
            groups.append((sig, [t]))
    entry = {"path": str(path.relative_to(ROOT)), "pair_member": member,
             "decoder": "libsndfile " +
                        _SNDFILE.sf_version_string().decode(errors="replace"),
             "transport_axis": arms,
             "transport_protocol": {"arm_timeout_s": TRANSPORT_R71_ARM_TIMEOUT_S,
                                    "fifo_writer_hold_s": hold_s,
                                    "fifo_feed": "one-shot write then writer lingers"},
             "sndfile_info_cli": cli,
             "transport_verdict_groups": [
                 {"transports": ts, "sndfile_format": sig[0],
                  "read_frames": sig[1], "error": sig[2]}
                 for sig, ts in groups],
             "transport_fork": len(groups) > 1,
             "failures": []}
    if entry["transport_fork"]:
        desc = " vs ".join("/".join(ts) + "=" + (sig[2] or str(sig[0]))
                           for sig, ts in groups)
        entry["failures"].append(
            f"transport: libsndfile verdict forks across transports ({desc})")
    return entry


# r73 CONSUMER-class expansion: playback consumers (not decoder runtimes) on
# the canonical member x transport matrix.
#   pw-cat (PipeWire realtime playback) decodes via libsndfile — `sndfile:`
#   error lines — and paces consumption at playback rate. Viability is
#   conditional on a reachable daemon: the pw_context_connect gate fires
#   BEFORE the input is opened (ops entry records both sides; frontier
#   measured instant rc=1 "Host is down" with an empty runtime dir).
#   mpv detects by content via libavformat on every transport and, on
#   exactly one tracked member, forks at the demux/seek layer: a seekable
#   hcom stream gets lavf's "refresh seek to 0" which fails with a
#   SYNTHETIC EPERM (hcom has no .read_seek; EPERM = strerror(-1) — strace
#   shows zero failing syscalls) after stream probing drained the whole
#   member (zero data -> rc=2), while the same bytes on a non-seekable
#   stream skip the refresh and decode (rc=0). r73 adjudicated: the
#   briefed class-polarity partition was FALSIFIED corpus-wide — two
#   member-local forks only (mpv x dec_hcom seekable-bit wound; pw-cat x
#   .snd name-axis via its libsndfile decode layer); the other 7 members
#   are transport-invariant on both consumers.
CONSUMER_R73_MEMBERS = TRANSPORT_R72_MEMBERS   # same canonical 9
CONSUMER_R73_TIMEOUT_S = 15
# Pacing member: a base SPEC artifact (4.0 s programme) — long enough for
# playback-paced consumption to be measurable against instant delivery.
CONSUMER_R73_PACER = ARTIFACTS / "stem_sections.wav"
CONSUMER_R73_PACER_DURATION_S = 4.0
CONSUMER_R73_NOWRITER_WAIT_S = 3.0
CONSUMER_R73_TRICKLE_CHUNKS = 8
CONSUMER_R73_TRICKLE_GAP_S = 0.75


def _consumer_tail(text, probe_arg):
    """Normalized last-line tail: mpv `[t][lvl][mod]` log tags, quoted input
    paths, backtick names and ASLR tags stripped so the receipt is
    byte-deterministic across transports and runs."""
    lines = text.strip().splitlines()
    if not lines:
        return None
    t = re.sub(r"^\s*(\[[^\]]*\])+\s*", "", lines[-1])
    t = re.sub(r"`[^']*'", "`<input>'", t)
    t = re.sub(r'"[^"]*"', '"<input>"', t)
    t = re.sub(r" @ 0x[0-9a-fA-F]+", "", t)
    return t.replace(str(probe_arg), "<input>")[-160:]


def _pwcat_fields(text):
    """pw-cat's decode layer is libsndfile: the `sndfile:` line carries the
    format verdict, the trailing `error:` line the stream/open verdict."""
    m = re.search(r'sndfile: failed to open audio file "[^"]*":\s*(.*)', text)
    sndfile_err = m.group(1).strip() if m else None
    errs = [ln for ln in text.strip().splitlines() if ln.startswith("error:")]
    pw_err = errs[-1].split(":", 1)[1].strip() if errs else None
    return sndfile_err, pw_err


def pwcat_leg(transport, path, data, hold_s):
    """One bounded `pw-cat -p <in>` playback leg -> stream-consume verdict.

    <in> is a path for the named transports or `-` (stdin) for the
    anonymous arms — a pipe for stdin_pipe, a fresh O_RDONLY fd (anonymous
    but SEEKABLE) for redirected_fd. The fifo arm reuses the r67 writer
    protocol; pw-cat single-opens its input (no re-open bridge — the hold
    only keeps parity with sibling arms) and exits rc=0 at writer EOF.
    A timeout means open()/read() waits on a writer; subprocess's
    timeout-kill is SIGKILL — the only signal a fifo-blocked pw-cat honors
    (frontier measured >30 s SIGTERM survival in open())."""
    def run(argv, **kw):
        try:
            proc = subprocess.run(argv, capture_output=True,
                                  timeout=CONSUMER_R73_TIMEOUT_S, **kw)
            return proc.stderr.decode(errors="replace"), proc.returncode, None
        except subprocess.TimeoutExpired as exc:
            return ((exc.stderr or b"").decode(errors="replace"), None,
                    f"blocked: no verdict within {CONSUMER_R73_TIMEOUT_S} s")

    if transport == "file":
        text, code, blocked = run(["pw-cat", "-p", str(path)])
        label = str(path.relative_to(ROOT))
    elif transport == "stdin_pipe":
        text, code, blocked = run(["pw-cat", "-p", "-"], input=data)
        label = "-"
    elif transport == "redirected_fd":
        with path.open("rb") as fh:
            text, code, blocked = run(["pw-cat", "-p", "-"], stdin=fh)
        label = "-"
    else:
        with tempfile.TemporaryDirectory(prefix="pwcat-r73-") as tmp:
            fifo = Path(tmp) / path.name
            os.mkfifo(fifo)
            writer = threading.Thread(target=fifo_feed,
                                      args=(fifo, data, hold_s), daemon=True)
            writer.start()
            try:
                text, code, blocked = run(["pw-cat", "-p", str(fifo)])
            finally:
                writer.join(timeout=hold_s + 5)
                reap_fifo_orphans(fifo)
        label = path.name
    sndfile_err, pw_err = _pwcat_fields(text)
    leg = {"input": label, "exit_code": code,
           "sndfile_error": sndfile_err, "pw_error": pw_err,
           "error": blocked or sndfile_err or pw_err}
    tail = _consumer_tail(text, label)
    if tail:
        leg["stderr_tail"] = tail
    return leg


def mpv_leg(transport, path, data, hold_s):
    """One bounded mpv playback leg -> mandatory-seek consumer verdict.

    mpv sniffs content via libavformat on every transport; `--log-file` is
    the parse surface (--really-quiet leaves the console empty), decoded
    with ao/vo null so no device is needed. <in> is a path for the named
    transports or `-` (stdin) for the anonymous arms — a pipe for
    stdin_pipe, a fresh O_RDONLY fd for redirected_fd (anonymous but
    SEEKABLE: lavf treats the fd as seekable and attempts the refresh
    seek, grouping it with the file arm). The fifo arm reuses the r67
    writer protocol; mpv exits at writer EOF."""
    def run(argv, **kw):
        try:
            proc = subprocess.run(argv, capture_output=True,
                                  timeout=CONSUMER_R73_TIMEOUT_S, **kw)
            return proc.returncode, None
        except subprocess.TimeoutExpired:
            return None, f"blocked: no verdict within {CONSUMER_R73_TIMEOUT_S} s"

    with tempfile.TemporaryDirectory(prefix="mpv-r73-") as tmp:
        log = Path(tmp) / "mpv.log"
        argv = ["mpv", "--no-config", "--vo=null", "--ao=null",
                "--audio-display=no", "--really-quiet", f"--log-file={log}"]
        if transport == "file":
            code, blocked = run(argv + [str(path)])
            label = str(path.relative_to(ROOT))
        elif transport == "stdin_pipe":
            code, blocked = run(argv + ["-"], input=data)
            label = "-"
        elif transport == "redirected_fd":
            with path.open("rb") as fh:
                code, blocked = run(argv + ["-"], stdin=fh)
            label = "-"
        else:
            fifo = Path(tmp) / path.name
            os.mkfifo(fifo)
            writer = threading.Thread(target=fifo_feed,
                                      args=(fifo, data, hold_s), daemon=True)
            writer.start()
            try:
                code, blocked = run(argv + [str(fifo)])
            finally:
                writer.join(timeout=hold_s + 5)
                reap_fifo_orphans(fifo)
            label = path.name
        text = log.read_text(errors="replace") if log.exists() else ""
    detected = re.search(r"Detected file format: (\S+) \(libavformat\)", text)
    probe = re.search(r"Found '([^']+)' at score=(\d+)", text)
    seekfail = re.search(r"Seek failed \(([^)]*)\)", text)
    track = re.search(r"Audio\s+--aid=1\s+\(([^)]*)\)", text)
    verdict = re.search(r"finished playback, (.*)$", text, re.M)
    reason = (verdict.group(1).strip() if verdict else
              "Failed to recognize file format."
              if "Failed to recognize file format" in text else None)
    leg = {"input": label, "exit_code": code,
           "lavf_detected": detected.group(1) if detected else None,
           "lavf_probe": probe.group(1) if probe else None,
           "lavf_score": int(probe.group(2)) if probe else None,
           "stream_not_seekable": "Stream is not seekable" in text,
           "refresh_seek": "refresh seek to" in text,
           "seek_failed": seekfail.group(1) if seekfail else None,
           "audio_track": track.group(1) if track else None,
           "mpv_verdict": reason,
           "error": blocked or (None if code == 0 else
                                reason or f"exit {code}")}
    return leg


def consumer_transport_entry(member, path):
    """r73 receipt entry: BOTH playback consumers on the member's transport
    matrix. Each consumer gets its own verdict groups keyed on its verdict
    signature; a fork lands as a failure per the r67 convention, keyed by
    consumer so the receipt pins which polarity axis each one exercises."""
    hold_s = fifo_writer_hold_s()
    data = path.read_bytes()
    consumers = {}
    failures = []
    for consumer in ("pw-cat", "mpv"):
        legs = pwcat_leg if consumer == "pw-cat" else mpv_leg
        arms = {t: legs(t, path, data, hold_s)
                for t in ("file", "stdin_pipe", "redirected_fd", "fifo_path")}
        for t, named, seekable in TRANSPORT_R67_ARMS:
            arms[t]["named"], arms[t]["seekable"] = named, seekable
        groups = []
        for t in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
            a = arms[t]
            sig = ((a["exit_code"], a["sndfile_error"]) if consumer == "pw-cat"
                   else (a["exit_code"], a["lavf_detected"], a["seek_failed"]))
            for g in groups:
                if g[0] == sig:
                    g[1].append(t)
                    break
            else:
                groups.append((sig, [t]))
        consumers[consumer] = {
            "transport_axis": arms,
            "transport_verdict_groups": [
                {"transports": ts, "verdict": list(sig)}
                for sig, ts in groups],
            "transport_fork": len(groups) > 1}
        if consumers[consumer]["transport_fork"]:
            desc = " vs ".join("/".join(ts) + "=" + "/".join(str(s) for s in sig)
                               for sig, ts in groups)
            failures.append(f"transport: {consumer} verdict forks across "
                            f"transports ({desc})")
    return {"path": str(path.relative_to(ROOT)), "pair_member": member,
            "consumers": consumers,
            "consumer_protocol": {
                "arm_timeout_s": CONSUMER_R73_TIMEOUT_S,
                "fifo_writer_hold_s": hold_s,
                "fifo_feed": "one-shot write then writer lingers",
                "pwcat": ("pw-cat -p <in|-> — PipeWire realtime playback, "
                          "libsndfile decode layer (sndfile: errors); "
                          "SIGKILL-bound (survives SIGTERM fifo-blocked)"),
                "mpv": ("mpv --no-config --vo=null --ao=null "
                        "--audio-display=no --really-quiet "
                        "--log-file=<tmp> <in|->")},
            "failures": failures}


def consumer_ops_entry():
    """r73 ops entry — the member-independent pw-cat operational surface:
    (a) daemon liveness + the pw_context_connect gate's precedence over
    input open, (b) fifo writer-attach semantics (no-writer open block,
    empty-writer verdict), (c) playback-paced consumption on a 4.0 s
    member (instant dump + starved trickle)."""
    failures = []
    entry = {"probe": "pw-cat realtime consumer operational surface"}
    # (a) daemon liveness via the PulseAudio-on-PipeWire protocol, then the
    # gate leg: PIPEWIRE_RUNTIME_DIR=<empty> severs the socket without
    # touching the real session daemon — frontier measured instant rc=1
    # "Host is down" BEFORE the input is opened (no fifo block).
    try:
        proc = subprocess.run(["pactl", "info"], capture_output=True,
                              timeout=10)
        out = proc.stdout.decode(errors="replace")
        m = re.search(r"^Server Name:\s*(.*)$", out, re.M)
        s = re.search(r"^Default Sink:\s*(.*)$", out, re.M)
        entry["daemon_live"] = {
            "pactl_exit": proc.returncode,
            "server_name": m.group(1).strip() if m else None,
            "default_sink": s.group(1).strip() if s else None,
            "live": proc.returncode == 0}
    except (subprocess.TimeoutExpired, OSError) as exc:
        entry["daemon_live"] = {"pactl_exit": None, "live": False,
                                "error": str(exc)[:120]}
    directory, filename = TRANSPORT_R67_MEMBERS["dec_hcom"]
    dec = ROOT / "live" / directory / filename
    with tempfile.TemporaryDirectory(prefix="pwrt-r73-") as emptyrt:
        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                ["pw-cat", "-p", str(dec)], capture_output=True,
                env={**os.environ, "PIPEWIRE_RUNTIME_DIR": emptyrt},
                timeout=CONSUMER_R73_TIMEOUT_S)
            entry["daemon_gate"] = {
                "env_override": "PIPEWIRE_RUNTIME_DIR=<empty dir>",
                "exit_code": proc.returncode,
                "wall_s": round(time.monotonic() - t0, 3),
                "stderr_tail": _consumer_tail(
                    proc.stderr.decode(errors="replace"), str(dec))}
        except subprocess.TimeoutExpired:
            entry["daemon_gate"] = {
                "env_override": "PIPEWIRE_RUNTIME_DIR=<empty dir>",
                "exit_code": None, "blocked": True,
                "wall_s": round(time.monotonic() - t0, 3)}
    gate = entry["daemon_gate"]
    if gate.get("exit_code") != 1 or "pw_context_connect" not in (
            gate.get("stderr_tail") or ""):
        failures.append("consumer: daemon gate deviated from the frontier "
                        "signature (instant rc=1 pw_context_connect failure)")
    # (b) writer-attach semantics on a fifo.
    with tempfile.TemporaryDirectory(prefix="pwcat-r73-") as tmp:
        fifo = Path(tmp) / "nowriter.wav"
        os.mkfifo(fifo)
        proc = subprocess.Popen(["pw-cat", "-p", str(fifo)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True)
        try:
            proc.wait(timeout=CONSUMER_R73_NOWRITER_WAIT_S)
            entry["fifo_no_writer"] = {
                "blocked": False, "exit_code": proc.returncode,
                "waited_s": CONSUMER_R73_NOWRITER_WAIT_S}
        except subprocess.TimeoutExpired:
            try:
                wchan = Path(f"/proc/{proc.pid}/wchan").read_text().strip()
            except OSError:
                wchan = None
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            entry["fifo_no_writer"] = {
                "blocked": True, "wchan": wchan,
                "waited_s": CONSUMER_R73_NOWRITER_WAIT_S,
                "exit_code": proc.returncode}
        finally:
            reap_fifo_orphans(fifo)
        fifo2 = Path(tmp) / "empty.wav"
        os.mkfifo(fifo2)

        def empty_feed():
            try:
                open(fifo2, "wb").close()
            except OSError:
                pass
        t = threading.Thread(target=empty_feed, daemon=True)
        t.start()
        try:
            proc = subprocess.run(["pw-cat", "-p", str(fifo2)],
                                  capture_output=True,
                                  timeout=CONSUMER_R73_TIMEOUT_S)
            se, pe = _pwcat_fields(proc.stderr.decode(errors="replace"))
            entry["fifo_empty_writer"] = {"exit_code": proc.returncode,
                                          "sndfile_error": se,
                                          "pw_error": pe}
        except subprocess.TimeoutExpired:
            entry["fifo_empty_writer"] = {"exit_code": None, "blocked": True}
        finally:
            t.join(timeout=5)
            reap_fifo_orphans(fifo2)
    if not entry["fifo_no_writer"].get("blocked"):
        failures.append("consumer: fifo open without a writer did not block")
    ew = entry["fifo_empty_writer"]
    if ew.get("exit_code") != 1 or ew.get("sndfile_error") != "Format not recognised.":
        failures.append("consumer: empty-writer fifo deviated from the "
                        "frontier signature (rc=1 'Format not recognised.')")
    # (c) playback-paced consumption: instant dump of a 4.0 s member must
    # still take ~4.0 s of wall (drain is realtime), and a slower-than-
    # realtime trickle must stream as bytes arrive (block when starved,
    # no underrun abort) with wall >= the delivery window.
    data = CONSUMER_R73_PACER.read_bytes()
    with tempfile.TemporaryDirectory(prefix="pwcat-r73-") as tmp:
        fifo = Path(tmp) / CONSUMER_R73_PACER.name
        os.mkfifo(fifo)
        writer = threading.Thread(target=fifo_feed, args=(fifo, data, 0.0),
                                  daemon=True)
        t0 = time.monotonic()
        writer.start()
        try:
            proc = subprocess.run(["pw-cat", "-p", str(fifo)],
                                  capture_output=True,
                                  timeout=CONSUMER_R73_TIMEOUT_S)
            wall = time.monotonic() - t0
            entry["pacing_instant"] = {
                "member": str(CONSUMER_R73_PACER.relative_to(ROOT)),
                "bytes": len(data),
                "content_duration_s": CONSUMER_R73_PACER_DURATION_S,
                "exit_code": proc.returncode, "wall_s": round(wall, 3),
                "playback_paced": bool(wall >= CONSUMER_R73_PACER_DURATION_S * .75)}
        except subprocess.TimeoutExpired:
            entry["pacing_instant"] = {
                "member": str(CONSUMER_R73_PACER.relative_to(ROOT)),
                "exit_code": None, "blocked": True}
        finally:
            writer.join(timeout=5)
            reap_fifo_orphans(fifo)
        fifo2 = Path(tmp) / ("trickle-" + CONSUMER_R73_PACER.name)
        os.mkfifo(fifo2)
        chunk = -(-len(data) // CONSUMER_R73_TRICKLE_CHUNKS)

        def trickle_feed():
            try:
                with open(fifo2, "wb") as fh:
                    for i in range(0, len(data), chunk):
                        fh.write(data[i:i + chunk])
                        fh.flush()
                        time.sleep(CONSUMER_R73_TRICKLE_GAP_S)
            except OSError:
                pass
        writer = threading.Thread(target=trickle_feed, daemon=True)
        t0 = time.monotonic()
        writer.start()
        try:
            proc = subprocess.run(["pw-cat", "-p", str(fifo2)],
                                  capture_output=True,
                                  timeout=CONSUMER_R73_TIMEOUT_S + 10)
            wall = time.monotonic() - t0
            entry["pacing_trickle"] = {
                "member": str(CONSUMER_R73_PACER.relative_to(ROOT)),
                "chunks": CONSUMER_R73_TRICKLE_CHUNKS,
                "chunk_gap_s": CONSUMER_R73_TRICKLE_GAP_S,
                "delivery_window_s": round(
                    CONSUMER_R73_TRICKLE_CHUNKS * CONSUMER_R73_TRICKLE_GAP_S, 3),
                "exit_code": proc.returncode,
                "wall_s": round(wall, 3),
                "starved_ok": proc.returncode == 0}
        except subprocess.TimeoutExpired:
            entry["pacing_trickle"] = {"exit_code": None, "blocked": True}
        finally:
            writer.join(timeout=5)
            reap_fifo_orphans(fifo2)
    # (d) pw-cat name axis on the .snd member (critic's 2x2 control): the
    # identical no-magic bytes through fifos carrying DIFFERENT names —
    # .snd accepts via libsndfile's name fallback; a non-raw-family name
    # rejects. Isolates name-vs-transport decisively (same fifo arm, same
    # bytes, only the path's extension moves).
    snd_dir, snd_name = TRANSPORT_R69_MEMBERS["extsuffix_snd"]
    snd_data = (ROOT / "live" / snd_dir / snd_name).read_bytes()
    name_hold_s = fifo_writer_hold_s()
    with tempfile.TemporaryDirectory(prefix="pwcat-r73-") as tmp:
        name_axis = {}
        for fname in ("axis.snd", "axis.wav", "axis.bin"):
            fifo = Path(tmp) / fname
            os.mkfifo(fifo)
            writer = threading.Thread(
                target=fifo_feed, args=(fifo, snd_data, name_hold_s),
                daemon=True)
            writer.start()
            try:
                proc = subprocess.run(["pw-cat", "-p", str(fifo)],
                                      capture_output=True,
                                      timeout=CONSUMER_R73_TIMEOUT_S)
                se, pe = _pwcat_fields(
                    proc.stderr.decode(errors="replace"))
                name_axis[fname] = {"exit_code": proc.returncode,
                                    "sndfile_error": se, "pw_error": pe}
            except subprocess.TimeoutExpired:
                name_axis[fname] = {"exit_code": None, "blocked": True}
            finally:
                writer.join(timeout=name_hold_s + 5)
                reap_fifo_orphans(fifo)
        entry["pwcat_name_axis"] = {
            "member": str((ROOT / "live" / snd_dir / snd_name
                           ).relative_to(ROOT)),
            "legs": name_axis}
    na = entry["pwcat_name_axis"]["legs"]
    if not (na.get("axis.snd", {}).get("exit_code") == 0
            and na.get("axis.wav", {}).get("exit_code") == 1
            and na.get("axis.bin", {}).get("exit_code") == 1):
        failures.append("consumer: pw-cat name axis deviated from the "
                        "measured fork (.snd=rc0, .wav/.bin=rc1 on "
                        "identical fifo-fed bytes)")
    pi = entry["pacing_instant"]
    if pi.get("exit_code") != 0 or not pi.get("playback_paced"):
        failures.append("consumer: instant-dump consumption was not "
                        "playback-paced")
    pt = entry["pacing_trickle"]
    if pt.get("exit_code") != 0:
        failures.append("consumer: starved trickle aborted instead of "
                        "blocking to EOF")
    entry["failures"] = failures
    return entry


# r74 lavf NO-SEEK demuxer sweep (xconnector X2): mpv's inverted
# seekability fork as a function of the demuxer's seek capability.
# Source-derived rule under test (measured member-locally on hcom in r73):
# a lavf demuxer forks mpv on the seekable bit IFF (1) the content probe
# detects it, (2) the demuxer carries no .read_seek/.read_timestamp,
# (3) no AVFMT_GENERIC_INDEX, and (4) the codec is not pcm_*+block_align
# (mpv's PCM seek hack rescues wav-family streams). Member family:
#   predicted FORK (all 4 clauses): iss (IMA_ADPCM_Sound), apc (CRYO_APC),
#     acm (Interplay ACM; AVFMT_NO_BYTE_SEEK|NOTIMESTAMPS flags)
#   predicted INVARIANT: adx (GENERIC_INDEX index-seek rescue), aifc
#     (aiff's own read_seek), dec_act (wav: read_seek + the pcm seek hack
#     — already tracked under round-66)
# Two wound shapes are measured, not asserted: a member small enough that
# stream probing drains it shows the hcom shape ({file,redirected_fd}=rc2
# EPERM vs {stdin_pipe,fifo}=rc0); a MULTI-PACKET member keeps unread
# packets behind the probe window, so the seekable arm survives the
# failed refresh seek and plays a truncated head (rc=0 + EPERM) — the
# acm row shows the same ENOSYS-class wound at small size. Members are
# byte-deterministic under corpus/live/round-74 (hand-built headers for
# the demuxer-only formats; ffmpeg lavfi synth where a muxer exists) so
# the arm is self-sufficient on a fresh tree.
LAVF_R74_DIR = "round-74"
LAVF_R74_EXTENT_TIMEOUT_S = CONSUMER_R73_TIMEOUT_S  # one bound, declared in the protocol block
LAVF_R74_START_S = 2.0
# Position-fork cell pacer: the r73 4.0 s wav (seekable demuxer + pcm
# seek hack) — `mpv --start=2` predicts {file,redirected_fd} -> ~2.0 s of
# decoded output vs {stdin_pipe,fifo} -> ~4.0 s.
LAVF_R74_PACER = CONSUMER_R73_PACER
LAVF_R74_ZERO_SINK_WAIT_S = 6.0
LAVF_R74_MEMBERS = {
    "lavf_iss":       (LAVF_R74_DIR, "lavf_iss.iss", "fork"),
    "lavf_apc":       (LAVF_R74_DIR, "lavf_apc.apc", "fork"),
    "lavf_acm":       (LAVF_R74_DIR, "lavf_acm.acm", "fork"),
    "lavf_iss_multi": (LAVF_R74_DIR, "lavf_iss_multi.iss", "fork"),
    "lavf_adx":       (LAVF_R74_DIR, "lavf_adx.adx", "invariant"),
    "lavf_aifc":      (LAVF_R74_DIR, "lavf_aifc.aifc", "invariant"),
    "dec_act":        (*TRANSPORT_R67_MEMBERS["dec_act"], "invariant"),
}


def build_lavf_r74_members():
    """Byte-deterministic member generation for the r74 sweep.

    Header layouts are taken from the n9.0.1 demuxer sources
    (libavformat/iss.c, apc.c, acm.c — all probe-detected, no
    read_seek/read_timestamp, no AVFMT_GENERIC_INDEX, non-pcm codecs):
      iss "IMA_ADPCM_Sound" + 9 space-separated ASCII tokens, then
          packets of exactly packet_size bytes (iss_read_packet fails on
          a short read, so the payload is always whole packets);
      apc "CRYO_APC"+"1.20" | u32LE samples | u32LE rate | 8B extradata |
          u32LE stereo flag | payload (demuxer reads <=4096 B/packet);
      acm BE magic 0x97280301 inside the demuxer's 14-B extradata |
          u32LE samples | u16LE channels | u16LE rate | u16LE subformat
          (0x7700 -> level 0, rows 0x77 -> 119-byte all-zero frames that
          interplayacm decodes to silence — payload is 20 frames).
    adx/aifc come from `ffmpeg -f lavfi` synth (muxers exist for both);
    generation is idempotent — every run rewrites identical bytes. A
    missing ffmpeg or a failed synth is recorded as a per-member blockage
    (the hand-built members still run); a fabricated member is never
    substituted."""
    out = ROOT / "live" / LAVF_R74_DIR
    out.mkdir(parents=True, exist_ok=True)
    made, blocked = {}, {}

    def _iss(packet_size, n_packets, name):
        tokens = ["IMA_ADPCM_Sound", str(packet_size), "0",
                  str(packet_size * n_packets), "0", "0", "1", "0", "1",
                  str(packet_size * n_packets)]
        path = out / name
        path.write_bytes(" ".join(tokens).encode()
                         + b" " + b"\x00" * (packet_size * n_packets))

    _iss(256, 2, "lavf_iss.iss")            # drains during probe -> rc2 wound
    _iss(512, 256, "lavf_iss_multi.iss")    # > probe window -> truncated head
    made["lavf_iss"] = "iss"
    made["lavf_iss_multi"] = "iss"

    # apc: 32-byte header then adpcm_ima_apc payload.
    apc = (b"CRYO_APC" + b"1.20"
           + (5120).to_bytes(4, "little") + (44100).to_bytes(4, "little")
           + b"\x00" * 8 + (0).to_bytes(4, "little") + b"\x00" * 5120)
    (out / "lavf_apc.apc").write_bytes(apc)
    made["lavf_apc"] = "apc"

    # acm: 14-byte header (extradata INCLUDES the BE magic) + 20x119B
    # zero frames that interplayacm decodes to silence.
    acm = (bytes((0x97, 0x28, 0x03, 0x01))
           + (400).to_bytes(4, "little")
           + (1).to_bytes(2, "little") + (44100).to_bytes(2, "little")
           + (0x7700).to_bytes(2, "little") + b"\x00" * 2380)
    (out / "lavf_acm.acm").write_bytes(acm)
    made["lavf_acm"] = "acm"

    for member, name, codec in (
            ("lavf_adx", "lavf_adx.adx", "adpcm_adx"),
            ("lavf_aifc", "lavf_aifc.aifc", "pcm_s16be")):
        try:
            subprocess.run(
                ["ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-i",
                 "sine=frequency=440:sample_rate=44100:duration=0.5",
                 "-ac", "1", "-c:a", codec, str(out / name)],
                check=True, capture_output=True, timeout=30)
            made[member] = name.rsplit(".", 1)[1]
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
                OSError) as exc:
            blocked[member] = f"ffmpeg lavfi synth -> {name} failed: {exc}"
    made["dec_act"] = "preexisting tracked member (round-66 wav)"
    return {"directory": f"live/{LAVF_R74_DIR}", "generated": made,
            "blocked": blocked}


def mpv_extent_leg(transport, path, data, hold_s, extra_opts=()):
    """mpv leg whose AO is `pcm` instead of `null`: the decoded stream
    lands in a scratch wav and its byte length is the PCM-extent pin —
    the observable for the head-truncation (lavf_iss_multi) and position
    (--start=N on a seeking wav) wound shapes, where the fork is in HOW
    MUCH audio plays, not the verdict signature. ao=pcm needs no device
    (the r73 ao=null pin guards the pipewire/dead-runtime class only);
    log parsing mirrors mpv_leg's field set."""
    def run(argv, **kw):
        try:
            proc = subprocess.run(argv, capture_output=True,
                                  timeout=LAVF_R74_EXTENT_TIMEOUT_S, **kw)
            return proc.returncode, None
        except subprocess.TimeoutExpired:
            return None, (f"blocked: no verdict within "
                          f"{LAVF_R74_EXTENT_TIMEOUT_S} s")

    with tempfile.TemporaryDirectory(prefix="mpv-r74-") as tmp:
        log = Path(tmp) / "mpv.log"
        pcm = Path(tmp) / "out.wav"
        argv = ["mpv", "--no-config", "--vo=null", "--ao=pcm",
                f"--ao-pcm-file={pcm}", "--audio-display=no",
                "--really-quiet", f"--log-file={log}", *extra_opts]
        if transport == "file":
            code, blocked = run(argv + [str(path)])
            label = str(path.relative_to(ROOT))
        elif transport == "stdin_pipe":
            code, blocked = run(argv + ["-"], input=data)
            label = "-"
        elif transport == "redirected_fd":
            with path.open("rb") as fh:
                code, blocked = run(argv + ["-"], stdin=fh)
            label = "-"
        else:
            fifo = Path(tmp) / path.name
            os.mkfifo(fifo)
            writer = threading.Thread(target=fifo_feed,
                                      args=(fifo, data, hold_s), daemon=True)
            writer.start()
            try:
                code, blocked = run(argv + [str(fifo)])
            finally:
                writer.join(timeout=hold_s + 5)
                reap_fifo_orphans(fifo)
            label = path.name
        text = log.read_text(errors="replace") if log.exists() else ""
        pcm_bytes = pcm.stat().st_size if pcm.exists() else None
        duration = None
        if pcm.exists():
            try:
                probe = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries",
                     "format=duration", "-of", "default=nw=1:nk=1",
                     str(pcm)], capture_output=True, timeout=10)
                duration = float(probe.stdout.decode().strip())
            except (subprocess.TimeoutExpired, ValueError, OSError):
                duration = None
    detected = re.search(r"Detected file format: (\S+) \(libavformat\)", text)
    probe_tag = re.search(r"Found '([^']+)' at score=(\d+)", text)
    seekfail = re.search(r"Seek failed \(([^)]*)\)", text)
    verdict = re.search(r"finished playback, (.*)$", text, re.M)
    reason = (verdict.group(1).strip() if verdict else
              "Failed to recognize file format."
              if "Failed to recognize file format" in text else None)
    leg = {"input": label, "exit_code": code,
           "lavf_detected": detected.group(1) if detected else None,
           "lavf_probe": probe_tag.group(1) if probe_tag else None,
           "lavf_score": int(probe_tag.group(2)) if probe_tag else None,
           "stream_not_seekable": "Stream is not seekable" in text,
           "refresh_seek": "refresh seek to" in text,
           "seek_failed": seekfail.group(1) if seekfail else None,
           "mpv_verdict": reason,
           "pcm_out_bytes": pcm_bytes,
           "pcm_out_duration_s": duration,
           "error": blocked or (None if code == 0 else
                                reason or f"exit {code}")}
    return leg


def lavf_transport_entry(member, path):
    """r74 receipt entry: mpv's seekable-bit verdict matrix on one member —
    the mpv consumer half of consumer_transport_entry (same leg + group
    machinery). `predicted` names the claim cell the member exercises:
    "fork" members must split the matrix on the seekable bit, "invariant"
    members must not. Failures pin deviations from the declared cell, so
    an absent predicted fork and an invariant-member fork are both
    measured falsifications."""
    prediction = LAVF_R74_MEMBERS[member][2]
    hold_s = fifo_writer_hold_s()
    data = path.read_bytes()
    arms = {t: mpv_leg(t, path, data, hold_s)
            for t in ("file", "stdin_pipe", "redirected_fd", "fifo_path")}
    for t, named, seekable in TRANSPORT_R67_ARMS:
        arms[t]["named"], arms[t]["seekable"] = named, seekable
    groups = []
    for t in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
        a = arms[t]
        sig = (a["exit_code"], a["lavf_detected"], a["seek_failed"])
        for g in groups:
            if g[0] == sig:
                g[1].append(t)
                break
        else:
            groups.append((sig, [t]))
    # Critic r74-F: fork kind annotation — a partition on seek_failed
    # alone (same exit_code, same decoded output) is a WOUND-level fork
    # (the lavf refresh-seek fires but the demuxer survives it: acm's
    # AVFMT_NOGENSEARCH early-return), NOT an output-level fork. The
    # output fork is the rc partition (iss/apc small members, hcom);
    # truncation is carried by the extent legs for multi-packet members.
    rcs = {g[0][0] for g in groups}
    if len(groups) <= 1:
        fork_kind = None
    elif len(rcs) > 1:
        fork_kind = "output_rc"
    else:
        fork_kind = "wound"
    entry = {"path": str(path.relative_to(ROOT)), "pair_member": member,
             "predicted": prediction,
             "fork_kind": fork_kind,
             "transport_axis": arms,
             "transport_protocol": {
                 "arm_timeout_s": CONSUMER_R73_TIMEOUT_S,
                 "fifo_writer_hold_s": hold_s,
                 "fifo_feed": "one-shot write then writer lingers",
                 "mpv": ("mpv --no-config --vo=null --ao=null "
                         "--audio-display=no --really-quiet "
                         "--log-file=<tmp> <in|->")},
             "transport_verdict_groups": [
                 {"transports": ts, "verdict": list(sig)}
                 for sig, ts in groups],
             "transport_fork": len(groups) > 1,
             "failures": []}
    if entry["transport_fork"] != (prediction == "fork"):
        if prediction == "fork":
            entry["failures"].append(
                "lavf: predicted seekable-bit fork absent "
                f"({len(groups)} verdict group(s))")
        else:
            desc = " vs ".join("/".join(ts) + "=" + "/".join(str(s) for s in sig)
                               for sig, ts in groups)
            entry["failures"].append(
                "lavf: predicted-invariant member forked across "
                f"transports ({desc})")
    if member == "lavf_iss_multi":
        # Wound-shape corollary cell: a multi-packet member on a no-seek
        # demuxer predicts head-truncation (seekable arm plays fewer PCM
        # bytes than the stream arm) rather than the rc2 wound.
        entry["extent_legs"] = {
            t: mpv_extent_leg(t, path, data, hold_s)
            for t in ("file", "fifo_path")}
        f_leg, p_leg = (entry["extent_legs"]["file"],
                        entry["extent_legs"]["fifo_path"])
        f_b, p_b = f_leg.get("pcm_out_bytes"), p_leg.get("pcm_out_bytes")
        entry["head_truncation"] = {
            "file_pcm_out_bytes": f_b,
            "file_pcm_out_duration_s": f_leg.get("pcm_out_duration_s"),
            "fifo_pcm_out_bytes": p_b,
            "fifo_pcm_out_duration_s": p_leg.get("pcm_out_duration_s"),
            "delta_bytes": (p_b - f_b) if None not in (f_b, p_b) else None,
            "truncated": (p_b > f_b) if None not in (f_b, p_b) else None}
        if entry["head_truncation"]["truncated"] is not True:
            entry["failures"].append(
                "lavf: multi-packet no-seek member did not show "
                "head-truncation on the seekable arm")
        elif entry["fork_kind"] == "wound":
            # Reviewer r74-F1: a measured head-truncation outranks the
            # verdict-group wound label — the real wound shape here is
            # lost PCM bytes at rc=0, not just a failed refresh seek.
            entry["fork_kind"] = "truncation"
    return entry


def lavf_startpos_entry(path):
    """r74 --start=N position-fork cell: on a SEEKING member (wav — own
    read_seek + the pcm seek hack), `mpv --start=2` seeks the seekable
    arms to 2.0 s while the non-seekable arms cannot seek and play from
    0 — the fork is positional, so the pin is decoded extent (ao=pcm
    output duration), never bare rc."""
    hold_s = fifo_writer_hold_s()
    data = path.read_bytes()
    legs = {t: mpv_extent_leg(t, path, data, hold_s,
                              extra_opts=(f"--start={LAVF_R74_START_S}",))
            for t in ("file", "stdin_pipe", "redirected_fd", "fifo_path")}
    for t, named, seekable in TRANSPORT_R67_ARMS:
        legs[t]["named"], legs[t]["seekable"] = named, seekable
    durations = {t: legs[t].get("pcm_out_duration_s")
                 for t in ("file", "stdin_pipe", "redirected_fd",
                           "fifo_path")}
    seekable = [durations[t] for t in ("file", "redirected_fd")]
    streaming = [durations[t] for t in ("stdin_pipe", "fifo_path")]
    complete = None not in (*seekable, *streaming)
    entry = {"path": str(path.relative_to(ROOT)),
             "cell": f"mpv --start={LAVF_R74_START_S} on a seeking wav member",
             "predicted": ("seekable arms play from --start (extent ~= "
                           "duration - start); non-seekable arms play "
                           "from 0 (extent ~= duration)"),
             "extent_legs": legs,
             "pcm_out_duration_s": durations,
             "position_fork": (bool(complete) and
                               max(seekable) < min(streaming) - 1.0
                               if complete else None),
             "failures": []}
    if entry["position_fork"] is not True:
        entry["failures"].append(
            "lavf: --start position fork absent (seekable arms did not "
            "start at the seek point vs the streaming arms)")
    return entry


def pwcat_ops2_entry():
    """r74 ops-2 — the pw-cat hang taxonomy pinned as SEPARATE classes plus
    the raw-bypass name-axis kill:
    (a) writerless-fifo open-block: SIGTERM-IMMUNE in wait_for_partner;
        r73 pinned the block itself — this cell adds the measured
        kill-escalation (TERM ignored for a beat, KILL -> rc -9).
    (b) `--target 0` unlinked-stream hang: TERM-TERMINABLE — a bounded
        NEGATIVE ops case (GNU `timeout -s TERM` -> rc 124 at the bound;
        r73-boundary measured the same class).
    (c) `-a/--raw` bypass: no libsndfile decode layer -> the r73 name
        axis dies — identical .snd-family bytes through raw mode accept
        under EVERY fifo name (.wav/.bin included).
    (d) zero-sink private daemon: socket reachable but no Audio/Sink —
        pw-cat hangs on stream link, KILL-bounded (cheap: a private
        PIPEWIRE_RUNTIME_DIR; recorded as a blockage when the private
        daemon cannot be spawned or its socket never appears)."""
    failures = []
    entry = {"probe": "pw-cat ops-2 — hang taxonomy + raw name-axis kill"}
    directory, filename = TRANSPORT_R67_MEMBERS["dec_hcom"]
    member_path = ROOT / "live" / directory / filename
    # (a) writerless fifo: SIGTERM is ignored inside the open block (the
    # r73 cell); the escalation to SIGKILL lands the measured rc -9.
    with tempfile.TemporaryDirectory(prefix="pwcat-r74-") as tmp:
        fifo = Path(tmp) / "nowriter.wav"
        os.mkfifo(fifo)
        proc = subprocess.Popen(["pw-cat", "-p", str(fifo)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True)
        try:
            proc.wait(timeout=CONSUMER_R73_NOWRITER_WAIT_S)
            entry["fifo_no_writer_escalation"] = {
                "blocked": False, "exit_code": proc.returncode,
                "waited_s": CONSUMER_R73_NOWRITER_WAIT_S}
        except subprocess.TimeoutExpired:
            try:
                wchan = Path(f"/proc/{proc.pid}/wchan").read_text().strip()
            except OSError:
                wchan = None
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=1.0)
                term_immune = False
            except subprocess.TimeoutExpired:
                term_immune = True
            if term_immune:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            entry["fifo_no_writer_escalation"] = {
                "blocked": True, "wchan": wchan,
                "sigterm_wait_s": 1.0, "sigterm_immune": term_immune,
                "exit_code": proc.returncode,
                "waited_s": CONSUMER_R73_NOWRITER_WAIT_S}
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            reap_fifo_orphans(fifo)
    esc = entry["fifo_no_writer_escalation"]
    if not (esc.get("blocked") and esc.get("sigterm_immune")
            and esc.get("exit_code") == -signal.SIGKILL):
        failures.append("consumer: writerless-fifo block deviated from "
                        "the measured escalation (blocked, SIGTERM-immune, "
                        "SIGKILL -> rc -9)")
    # (b) --target 0: the stream object exists but nothing links it — the
    # hang is real yet TERM-TERMINABLE (contrast (a)'s TERM immunity).
    # GNU `timeout -s TERM` converts the kill to rc 124 at the bound;
    # the subprocess timeout is only the backstop for a TERM-immune
    # surprise.
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            ["timeout", "-s", "TERM", "4", "pw-cat", "-p", "--target", "0",
             str(member_path)], capture_output=True,
            timeout=CONSUMER_R73_TIMEOUT_S)
        entry["target0_unlinked_stream"] = {
            "argv": "timeout -s TERM 4 pw-cat -p --target 0 <member>",
            "bound_s": 4, "signal": "TERM",
            "exit_code": proc.returncode,
            "wall_s": round(time.monotonic() - t0, 3),
            "term_terminable": proc.returncode == 124,
            "stderr_tail": _consumer_tail(
                proc.stderr.decode(errors="replace"), str(member_path))}
    except subprocess.TimeoutExpired:
        entry["target0_unlinked_stream"] = {
            "argv": "timeout -s TERM 4 pw-cat -p --target 0 <member>",
            "bound_s": 4, "signal": "TERM", "exit_code": None,
            "wall_s": round(time.monotonic() - t0, 3),
            "term_terminable": False, "blocked_past_wrapper": True}
    t0e = entry["target0_unlinked_stream"]
    if not (t0e.get("exit_code") == 124 and t0e.get("term_terminable")):
        failures.append("consumer: --target 0 hang deviated from the "
                        "TERM-terminable class (timeout -s TERM -> rc 124)")
    # (c) --raw bypass kills the name axis: pw-cat -a/--raw skips the
    # libsndfile decode layer entirely, so identical no-magic bytes accept
    # under EVERY fifo name — the .snd/.wav/.bin fork of ops-1's
    # pwcat_name_axis collapses to rc=0 without the decode layer.
    snd_dir, snd_name = TRANSPORT_R69_MEMBERS["extsuffix_snd"]
    snd_data = (ROOT / "live" / snd_dir / snd_name).read_bytes()
    name_hold_s = fifo_writer_hold_s()
    with tempfile.TemporaryDirectory(prefix="pwcat-r74-") as tmp:
        raw_axis = {}
        for fname in ("axis.snd", "axis.wav", "axis.bin"):
            fifo = Path(tmp) / fname
            os.mkfifo(fifo)
            writer = threading.Thread(
                target=fifo_feed, args=(fifo, snd_data, name_hold_s),
                daemon=True)
            writer.start()
            try:
                proc = subprocess.run(["pw-cat", "-p", "--raw", str(fifo)],
                                      capture_output=True,
                                      timeout=CONSUMER_R73_TIMEOUT_S)
                se, pe = _pwcat_fields(proc.stderr.decode(errors="replace"))
                raw_axis[fname] = {"exit_code": proc.returncode,
                                   "sndfile_error": se, "pw_error": pe}
            except subprocess.TimeoutExpired:
                raw_axis[fname] = {"exit_code": None, "blocked": True}
            finally:
                writer.join(timeout=name_hold_s + 5)
                reap_fifo_orphans(fifo)
        entry["pwcat_raw_name_axis"] = {
            "member": str((ROOT / "live" / snd_dir / snd_name
                           ).relative_to(ROOT)),
            "mode": "pw-cat -p --raw (libsndfile decode layer bypassed)",
            "legs": raw_axis}
    ra = entry["pwcat_raw_name_axis"]["legs"]
    if not all(ra.get(f, {}).get("exit_code") == 0
               for f in ("axis.snd", "axis.wav", "axis.bin")):
        failures.append("consumer: raw-bypass name-axis kill deviated "
                        "(predicted rc=0 under every fifo name)")
    # (d) zero-sink private daemon: a private pipewire in a scratch
    # PIPEWIRE_RUNTIME_DIR exposes a socket but no Audio/Sink — pw-cat
    # hangs on the stream link rather than erroring (r73-boundary
    # measured the same class; teardown restores nothing — the private
    # daemon is killed, the live daemon is never touched).
    with tempfile.TemporaryDirectory(prefix="pwrt-r74-") as rt_dir:
        env = {**os.environ, "PIPEWIRE_RUNTIME_DIR": rt_dir,
               "XDG_RUNTIME_DIR": rt_dir}
        daemon = None
        try:
            daemon = subprocess.Popen(
                ["pipewire"], env=env,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            sock = Path(rt_dir) / "pipewire-0"
            for _ in range(50):
                if sock.exists():
                    break
                time.sleep(0.2)
            if not sock.exists():
                entry["zero_sink_daemon"] = {
                    "attempted": True, "socket_up": False,
                    "blockage": "private pipewire socket never appeared"}
            else:
                sinks = None
                try:
                    dump = subprocess.run(
                        ["timeout", "-s", "KILL", "5", "pw-dump"], env=env,
                        capture_output=True, timeout=10)
                    if dump.returncode == 0:
                        sinks = sum(
                            1 for o in json.loads(
                                dump.stdout.decode("utf-8", "replace"))
                            if ((o.get("info") or {}).get("props") or {})
                            .get("media.class") == "Audio/Sink")
                except (subprocess.TimeoutExpired, OSError, ValueError):
                    sinks = None
                proc = subprocess.Popen(
                    ["pw-cat", "-p", str(member_path)], env=env,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    start_new_session=True)
                try:
                    proc.wait(timeout=LAVF_R74_ZERO_SINK_WAIT_S)
                    zs_leg = {"exit_code": proc.returncode,
                              "blocked": False}
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                    zs_leg = {"exit_code": proc.returncode,
                              "blocked": True}
                finally:
                    if proc.poll() is None:
                        os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait()
                entry["zero_sink_daemon"] = {
                    "attempted": True, "socket_up": True,
                    "audio_sink_count": sinks,
                    "pwcat_wait_s": LAVF_R74_ZERO_SINK_WAIT_S,
                    "pwcat": zs_leg}
                if not zs_leg["blocked"]:
                    failures.append("consumer: zero-sink daemon pw-cat "
                                    "exited instead of hanging on stream "
                                    "link")
        except OSError as exc:
            entry["zero_sink_daemon"] = {
                "attempted": False,
                "blockage": f"private pipewire spawn failed: {exc}"}
        finally:
            if daemon is not None:
                daemon.terminate()
                try:
                    daemon.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    daemon.kill()
                    daemon.wait()
    entry["failures"] = failures
    return entry


# r75 CONSUMER-class breadth-2: three NEW playback consumers on the
# canonical member x transport matrix (r73 shape; a new parallel ledger
# family --probe-consumers2-r75, prior rows untouched).
#   paplay (pacat, PulseAudio client over pipewire-pulse): decodes via
#     libsndfile through sf_open_FD — an fd-based open is NAME-BLIND, so
#     the r73 pw-cat .snd name-axis fork (path-based sf_open) cannot
#     transfer (frontier: identical no-magic bytes reject under
#     {.snd,.wav,.bin,.au} named files and fifos alike). Daemon-gated
#     like pw-cat but with the opposite ORDER: paplay opens the input
#     first, so a writerless fifo blocks in open() before the server —
#     dead or alive — is ever contacted. The open block has no custom
#     TERM disposition: SIGTERM kills it (rc -15), unlike pw-cat's
#     SIGTERM-immune -9.
#   aplay (ALSA in-process): NO daemon — kernel device coupling. The
#     matrix runs `-D null` (an in-process plugin device that discards
#     samples) so the input-parse verdict stays device-free; the ops
#     entry censuses `aplay -l`/`-L` and records the device gates
#     (default routes through the PipeWire plugin on this host —
#     daemon-coupled; hw:<card> applies the kernel driver's format
#     constraints — device-coupled). Header parse is forward-only
#     content magic, so the name axis is dead AND the raw fallback
#     accepts every unmatched buffer under every name.
#   ffplay (SDL + libavformat pull-model): a SECOND lavf consumer —
#     answers whether mpv's inverted-seek fork (r73 dec_hcom) is a lavf
#     property or an mpv-ism. ffplay's read thread pulls packets with no
#     post-probe refresh seek (avio `Statistics: ... seeks:0` on the
#     seekable file arm), so the dec_hcom fork cannot transfer. The
#     parse surface is ffplay's own stderr at -v debug (Input #0 detect
#     + Statistics seeks); exit_code is NOT the verdict — ffplay returns
#     0 even on "Invalid data found" input. SDL_AUDIODRIVER=dummy makes
#     the sink deterministic; the ops entry axes {dummy,pulse,alsa}.
CONSUMER_R75_MEMBERS = CONSUMER_R73_MEMBERS   # same canonical 9
CONSUMER_R75_TIMEOUT_S = CONSUMER_R73_TIMEOUT_S
CONSUMER_R75_NOWRITER_WAIT_S = CONSUMER_R73_NOWRITER_WAIT_S
CONSUMER_R75_SIGTERM_WAIT_S = 1.0
CONSUMER_R75_START_S = LAVF_R74_START_S       # -ss 2 position cell
FFPLAY_R75_ENV = {"SDL_AUDIODRIVER": "dummy"}


def _consumer2_tail(text, probe_arg):
    """_consumer_tail plus determinism scrubbing for the r75 consumers:
    single-quoted input names normalize wholesale (`Playing WAVE
    '<abs-or-tmp-path>' -> '<input>') and any residual UNQUOTED
    directory prefix before <input> (absolute member path, fifo
    mkdtemp dir — aplay/ffplay echo paths verbatim where
    _consumer_tail's relative probe_arg only covers the basename)
    collapses, so a tail never leaks host paths or mkdtemp suffixes."""
    tail = _consumer_tail(text, probe_arg)
    if not tail:
        return tail
    tail = re.sub(r"'[^']*'", "'<input>'", tail)
    tail = re.sub(r"\S+<input>", "<input>", tail)
    return tail


_PACAT_RACY_TAIL = re.compile(
    r"^(Time:.*Latency:|Playback stream drained\.|"
    r"Draining connection to server\.|Connected to device.*|"
    r"Stream started\..*)$")


def _paplay_fields(text):
    """pacat -v surface: the negotiated sample spec on accept; the open/
    connect error line on reject. `Connected to device ... (index: N)`
    carries a per-run index and is never keyed on."""
    spec = re.search(r"Using sample spec '([^']+)'", text)
    err = None
    for pat in (r"open\(\): [^\n]+", r"Connection failure: [^\n]+",
                r"Failed to open audio file\.?"):
        m = re.search(pat, text)
        if m:
            err = m.group(0).strip()
            break
    return (spec.group(1) if spec else None), err


def paplay_leg(transport, path, data, hold_s):
    """One bounded `paplay -v` playback leg -> stream-consume verdict.

    pacat reads stdin only as its NO-ARG source ('-' is a literal
    filename -> `open(): No such file or directory`), so the anonymous
    arms are `paplay -v` with piped or redirected stdin; named arms take
    the path. The decode front-end is libsndfile via sf_open_fd — an
    fd-based open is name-blind on EVERY transport, so the r73 pw-cat
    .snd name fork cannot transfer. Viability is daemon-gated like
    pw-cat but in the opposite ORDER: input open precedes
    pa_context_connect — a writerless fifo blocks before any server
    contact (the ops entry pins the ordering cell). A fifo leg without
    a writer blocks in open(); the subprocess timeout is the KILL
    bound, though unlike pw-cat a bare SIGTERM already suffices."""
    def run(argv, **kw):
        try:
            proc = subprocess.run(argv, capture_output=True,
                                  timeout=CONSUMER_R75_TIMEOUT_S, **kw)
            return proc.stderr.decode(errors="replace"), proc.returncode, None
        except subprocess.TimeoutExpired as exc:
            return ((exc.stderr or b"").decode(errors="replace"), None,
                    f"blocked: no verdict within {CONSUMER_R75_TIMEOUT_S} s")

    if transport == "file":
        text, code, blocked = run(["paplay", "-v", str(path)])
        label = str(path.relative_to(ROOT))
    elif transport == "stdin_pipe":
        text, code, blocked = run(["paplay", "-v"], input=data)
        label = "-"
    elif transport == "redirected_fd":
        with path.open("rb") as fh:
            text, code, blocked = run(["paplay", "-v"], stdin=fh)
        label = "-"
    else:
        with tempfile.TemporaryDirectory(prefix="paplay-r75-") as tmp:
            fifo = Path(tmp) / path.name
            os.mkfifo(fifo)
            writer = threading.Thread(target=fifo_feed,
                                      args=(fifo, data, hold_s), daemon=True)
            writer.start()
            try:
                text, code, blocked = run(["paplay", "-v", str(fifo)])
            finally:
                writer.join(timeout=hold_s + 5)
                reap_fifo_orphans(fifo)
        label = path.name
    spec, pa_err = _paplay_fields(text)
    leg = {"input": label, "exit_code": code,
           "pa_sample_spec": spec, "pa_error": pa_err,
           "error": blocked or pa_err}
    # pacat's -v tail is racy: the `Time:...Latency:` progress carriage
    # and the drain couplet compete for the last line. Filter them (plus
    # the index-bearing `Connected to device` and `Stream started`) so
    # the tail is deterministic — a successful leg ends on the
    # negotiated `Using sample spec ...` line.
    ftext = "\n".join(ln for ln in text.splitlines()
                      if not _PACAT_RACY_TAIL.match(ln))
    tail = _consumer2_tail(ftext, label)
    if tail:
        leg["stderr_tail"] = tail
    return leg


def _aplay_fields(text):
    """aplay parse surface: `Playing <KIND> '<input>' : <spec>` names the
    content-magic classification (WAVE|VOC|AU|raw data — the filename
    only decorates the line, extension is never consulted); `aplay:
    <func>:<line>: <msg>` is the parse/device error (func:line is
    build-pinned, kept verbatim)."""
    m = re.search(r"Playing (WAVE|VOC|AU|raw data) '[^']*' : ([^\n]*)", text)
    err = re.search(r"^(aplay: [^\n]+)$", text, re.M)
    return ((m.group(1), m.group(2).strip()) if m else (None, None),
            err.group(1).strip() if err else None)


def aplay_leg(transport, path, data, hold_s, device="null"):
    """One bounded `aplay -D <device>` leg -> ALSA content-parse verdict.

    aplay is daemon-free (in-process ALSA); the matrix fixes -D null so
    the input-side verdict is device-independent — ops records the
    device axis (default/pipewire/hw) separately. `-` means stdin
    (`Playing ... 'stdin'`); the header parse is forward-only content
    magic — seekability is never exercised. A member that matches no
    container magic falls through to `Playing raw data` (u8/8000/mono
    defaults) and ACCEPTS under every name, so aplay's verdict is
    predicted invariant-accept where paplay's is invariant-reject. A
    fifo leg without a writer blocks in open() like every other
    consumer; aplay catches SIGTERM ('Aborted by signal Terminated')
    yet stays blocked -> the ops cell lands the KILL escalation."""
    def run(argv, **kw):
        try:
            proc = subprocess.run(argv, capture_output=True,
                                  timeout=CONSUMER_R75_TIMEOUT_S, **kw)
            return proc.stderr.decode(errors="replace"), proc.returncode, None
        except subprocess.TimeoutExpired as exc:
            return ((exc.stderr or b"").decode(errors="replace"), None,
                    f"blocked: no verdict within {CONSUMER_R75_TIMEOUT_S} s")

    argv0 = ["aplay", "-D", device]
    if transport == "file":
        text, code, blocked = run(argv0 + [str(path)])
        label = str(path.relative_to(ROOT))
    elif transport == "stdin_pipe":
        text, code, blocked = run(argv0 + ["-"], input=data)
        label = "-"
    elif transport == "redirected_fd":
        with path.open("rb") as fh:
            text, code, blocked = run(argv0 + ["-"], stdin=fh)
        label = "-"
    else:
        with tempfile.TemporaryDirectory(prefix="aplay-r75-") as tmp:
            fifo = Path(tmp) / path.name
            os.mkfifo(fifo)
            writer = threading.Thread(target=fifo_feed,
                                      args=(fifo, data, hold_s), daemon=True)
            writer.start()
            try:
                text, code, blocked = run(argv0 + [str(fifo)])
            finally:
                writer.join(timeout=hold_s + 5)
                reap_fifo_orphans(fifo)
        label = path.name
    (kind, spec), aerr = _aplay_fields(text)
    leg = {"input": label, "exit_code": code, "device": device,
           "alsa_kind": kind, "alsa_spec": spec, "alsa_error": aerr,
           "error": blocked or aerr or (None if code == 0 else
                                       f"exit {code}")}
    tail = _consumer2_tail(text, label)
    if tail:
        leg["stderr_tail"] = tail
    return leg


# ffplay's periodic status line (`... fd= N aq= NKB vq= NKB sq= NB`,
# `nan` before open resolves) races the verdict line for the last slot —
# dropped before tail extraction so rejects land on the verdict line and
# decodes on the closing `Statistics:` line.
_FFPLAY_STATUS_TAIL = re.compile(r"fd=\s*\d+\s+aq=\s*\d+KB.*sq=")


def _ffplay_fields(text):
    """ffplay's own stderr surface (-v debug): `Input #0, <fmt>, from` is
    the lavf detect, `Stream #0:0...: Audio: <codec>` the decoded codec,
    `Format <fmt> probed ... score=N` the probe score, and the last
    `Statistics: N bytes read, M seeks` the avio seek count — mpv's
    refresh seek would land in M; the SDL pull model stays 0. Reject/
    seek evidence: `Invalid data found when processing input`,
    `could not seek`. `[ctx @ 0x...]` ASLR prefixes are never keyed
    (the tail normalizer strips them)."""
    detected = re.search(r"Input #0, ([^,\s]+), from", text)
    codec = re.search(r"Stream #0:0[^:\n]*: Audio: ([^,\s]+)", text)
    duration = re.search(r"Duration: ([^,\n]+)", text)
    probed = re.search(r"Format (\S+) probed with size=(\d+) and score=(\d+)",
                       text)
    stats = re.findall(r"Statistics: (\d+) bytes read, (\d+) seeks", text)
    return {
        "ffplay_detected": detected.group(1) if detected else None,
        "ffplay_codec": codec.group(1) if codec else None,
        "ffplay_duration": (duration.group(1).strip() if duration else None),
        "lavf_probe": probed.group(1) if probed else None,
        "lavf_score": int(probed.group(3)) if probed else None,
        "avio_bytes_read": int(stats[-1][0]) if stats else None,
        "avio_seeks": int(stats[-1][1]) if stats else None,
        "could_not_seek": "could not seek" in text,
        "ffplay_invalid": ("Invalid data found when processing input"
                           in text)}


def ffplay_leg(transport, path, data, hold_s, extra_opts=(),
               loglevel="debug"):
    """One bounded `ffplay -nodisp -autoexit` leg -> lavf pull-model
    verdict.

    SDL_AUDIODRIVER=dummy fixes the sink (no daemon, no card) — the ops
    entry axes the driver separately. stdin is `-i -` (the fd: protocol
    — '-' alone is not an input alias); redirected_fd hands the same
    flag a seekable regular-file fd. Verdict fields key on detection +
    seek evidence, never bare rc: this build exits 0 even on 'Invalid
    data found when processing input'. A fifo leg without a writer
    never reaches the consumer's own bound — avformat's open blocks in
    the read thread while the main loop polls (ops pins the class) —
    the subprocess timeout is the KILL bound."""
    env = {**os.environ, **FFPLAY_R75_ENV}

    def run(argv, **kw):
        try:
            proc = subprocess.run(argv, capture_output=True,
                                  timeout=CONSUMER_R75_TIMEOUT_S, env=env,
                                  **kw)
            return proc.stderr.decode(errors="replace"), proc.returncode, None
        except subprocess.TimeoutExpired as exc:
            return ((exc.stderr or b"").decode(errors="replace"), None,
                    f"blocked: no verdict within {CONSUMER_R75_TIMEOUT_S} s")

    argv0 = ["ffplay", "-nodisp", "-autoexit", "-v", loglevel, *extra_opts]
    if transport == "file":
        text, code, blocked = run(argv0 + [str(path)])
        label = str(path.relative_to(ROOT))
    elif transport == "stdin_pipe":
        text, code, blocked = run(argv0 + ["-i", "-"], input=data)
        label = "-"
    elif transport == "redirected_fd":
        with path.open("rb") as fh:
            text, code, blocked = run(argv0 + ["-i", "-"], stdin=fh)
        label = "-"
    else:
        with tempfile.TemporaryDirectory(prefix="ffplay-r75-") as tmp:
            fifo = Path(tmp) / path.name
            os.mkfifo(fifo)
            writer = threading.Thread(target=fifo_feed,
                                      args=(fifo, data, hold_s), daemon=True)
            writer.start()
            try:
                text, code, blocked = run(argv0 + [str(fifo)])
            finally:
                writer.join(timeout=hold_s + 5)
                reap_fifo_orphans(fifo)
        label = path.name
    leg = {"input": label, "exit_code": code}
    leg.update(_ffplay_fields(text))
    leg["error"] = blocked or (
        "invalid_data" if leg["ffplay_invalid"] else
        "could_not_seek" if leg["could_not_seek"] else
        None if leg["ffplay_detected"] else f"exit {code}")
    ftext = "\n".join(ln for ln in text.splitlines()
                      if not _FFPLAY_STATUS_TAIL.search(ln))
    tail = _consumer2_tail(ftext, label)
    if tail:
        leg["stderr_tail"] = tail
    return leg


def consumer2_transport_entry(member, path):
    """r75 receipt entry: THREE playback consumers on the member's
    transport matrix (same member set + verdict-group machinery as
    consumer_transport_entry). Each consumer keys its own signature so
    the receipt pins which polarity each exercises — paplay
    (exit, spec, pa_error), aplay (exit, kind, aplay_error), ffplay
    (exit, detected, seeks, invalid). A fork lands as a failure keyed
    by consumer (r67 convention)."""
    hold_s = fifo_writer_hold_s()
    data = path.read_bytes()
    consumers = {}
    failures = []
    for consumer, legs in (("paplay", paplay_leg), ("aplay", aplay_leg),
                           ("ffplay", ffplay_leg)):
        arms = {t: legs(t, path, data, hold_s)
                for t in ("file", "stdin_pipe", "redirected_fd",
                          "fifo_path")}
        for t, named, seekable in TRANSPORT_R67_ARMS:
            arms[t]["named"], arms[t]["seekable"] = named, seekable
        groups = []
        for t in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
            a = arms[t]
            if consumer == "paplay":
                sig = (a["exit_code"], a["pa_sample_spec"], a["pa_error"])
            elif consumer == "aplay":
                sig = (a["exit_code"], a["alsa_kind"], a["alsa_error"])
            else:
                sig = (a["exit_code"], a["ffplay_detected"],
                       a["avio_seeks"], a["ffplay_invalid"])
            for g in groups:
                if g[0] == sig:
                    g[1].append(t)
                    break
            else:
                groups.append((sig, [t]))
        consumers[consumer] = {
            "transport_axis": arms,
            "transport_verdict_groups": [
                {"transports": ts, "verdict": list(sig)}
                for sig, ts in groups],
            "transport_fork": len(groups) > 1}
        if consumers[consumer]["transport_fork"]:
            desc = " vs ".join("/".join(ts) + "=" + "/".join(str(s) for s in sig)
                               for sig, ts in groups)
            failures.append(f"transport: {consumer} verdict forks across "
                            f"transports ({desc})")
    return {"path": str(path.relative_to(ROOT)), "pair_member": member,
            "consumers": consumers,
            "consumer_protocol": {
                "arm_timeout_s": CONSUMER_R75_TIMEOUT_S,
                "fifo_writer_hold_s": hold_s,
                "fifo_feed": "one-shot write then writer lingers",
                "paplay": ("paplay -v [<path>] — pacat 17.0/libpulse 17.0 "
                           "playback, libsndfile decode via sf_open_fd "
                           "(name-blind); stdin = no-arg, '-' is a "
                           "literal filename; daemon-gated AFTER input "
                           "open"),
                "aplay": ("aplay -D null [<path>|-> — in-process ALSA, "
                          "forward-only content-magic parse, raw "
                          "fallback accepts unmatched buffers"),
                "ffplay": ("ffplay -nodisp -autoexit -v debug "
                           "SDL_AUDIODRIVER=dummy [<path>|-i -] — lavf "
                           "pull-model, verdict = detect+seek fields "
                           "(rc is 0 even on invalid input)")},
            "failures": failures}


def _nowriter_cell(argv, extra_env=None):
    """Spawn `argv` on a writerless fifo and pin the kill class: wait
    NOWRITER_WAIT_S, sample wchan/state, send SIGTERM, allow
    SIGTERM_WAIT_S, then SIGKILL the process group. The class is
    per-consumer: paplay dies on TERM (rc -15), aplay catches TERM
    ('Aborted by signal Terminated') yet stays blocked (-9), ffplay's
    handler exits 123 while its read thread stays blocked in open()
    (pw-cat ignores TERM -> -9, r74)."""
    with tempfile.TemporaryDirectory(prefix="nowriter-r75-") as tmp:
        fifo = Path(tmp) / "nowriter.wav"
        os.mkfifo(fifo)
        env = {**os.environ, **(extra_env or {})}
        proc = subprocess.Popen(argv + [str(fifo)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=env, start_new_session=True)
        try:
            proc.wait(timeout=CONSUMER_R75_NOWRITER_WAIT_S)
            return {"argv": " ".join(argv + ["<fifo>"]),
                    "blocked": False, "exit_code": proc.returncode,
                    "waited_s": CONSUMER_R75_NOWRITER_WAIT_S}
        except subprocess.TimeoutExpired:
            try:
                wchan = Path(f"/proc/{proc.pid}/wchan").read_text().strip()
            except OSError:
                wchan = None
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=CONSUMER_R75_SIGTERM_WAIT_S)
                term_immune = False
            except subprocess.TimeoutExpired:
                term_immune = True
            if term_immune:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            try:
                err = proc.stderr.read().decode(errors="replace")
            except Exception:
                err = ""
            rec = {"argv": " ".join(argv + ["<fifo>"]),
                   "blocked": True, "wchan": wchan,
                   "sigterm_wait_s": CONSUMER_R75_SIGTERM_WAIT_S,
                   "sigterm_immune": term_immune,
                   "exit_code": proc.returncode,
                   "waited_s": CONSUMER_R75_NOWRITER_WAIT_S}
            if err.strip():
                rec["stderr_tail"] = _consumer2_tail(err, str(fifo))
            return rec
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            reap_fifo_orphans(fifo)


def consumers2_paplay_ops_entry():
    """r75 paplay ops surface — the pulse daemon gate plus the ORDERING
    that distinguishes it from pw-cat:
    (a) daemon liveness via pactl;
    (b) dead-server gate on a VALID member — instant rc=1
        'Connection failure' (input parses, connect fails);
    (c) gate ordering — dead server + writerless fifo: paplay opens the
        INPUT first, so it blocks in open() and never reaches the dead
        server (no connection error in stderr, TERM -> -15);
    (d) writerless fifo under a LIVE server — same open block class,
        SIGTERM kills (rc -15; contrast pw-cat's TERM-immune -9);
    (e) the .snd name-axis control on identical no-magic bytes —
        named files {snd,wav,bin}, fifos {snd,wav,bin}, and an rfd —
        predicted INVARIANT-REJECT everywhere because sf_open_fd is
        name-blind (the r73 pw-cat fork cannot transfer);
    (f) --raw bypass on the .snd fifo — skips the decode layer, rc=0;
    (g) empty-writer fifo — immediate EOF under libsndfile."""
    failures = []
    entry = {"probe": "paplay consumer operational surface"}
    try:
        proc = subprocess.run(["pactl", "info"], capture_output=True,
                              timeout=10)
        out = proc.stdout.decode(errors="replace")
        m = re.search(r"^Server Name:\s*(.*)$", out, re.M)
        s = re.search(r"^Default Sink:\s*(.*)$", out, re.M)
        entry["daemon_live"] = {
            "pactl_exit": proc.returncode,
            "server_name": m.group(1).strip() if m else None,
            "default_sink": s.group(1).strip() if s else None,
            "live": proc.returncode == 0}
    except (subprocess.TimeoutExpired, OSError) as exc:
        entry["daemon_live"] = {"pactl_exit": None, "live": False,
                                "error": str(exc)[:120]}
    snd_dir, snd_name = TRANSPORT_R69_MEMBERS["extsuffix_snd"]
    snd_path = ROOT / "live" / snd_dir / snd_name
    snd_data = snd_path.read_bytes()
    dead_env = {"PULSE_SERVER": "unix:/nonexistent-r75-paplay-gate"}
    # (b) dead server + valid member: input parses, connect fails fast.
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            ["paplay", str(CONSUMER_R73_PACER)], capture_output=True,
            env={**os.environ, **dead_env},
            timeout=CONSUMER_R75_TIMEOUT_S)
        entry["daemon_gate_dead"] = {
            "env_override": "PULSE_SERVER=unix:<nonexistent>",
            "exit_code": proc.returncode,
            "wall_s": round(time.monotonic() - t0, 3),
            "stderr_tail": _consumer2_tail(
                proc.stderr.decode(errors="replace"),
                str(CONSUMER_R73_PACER))}
    except subprocess.TimeoutExpired:
        entry["daemon_gate_dead"] = {
            "env_override": "PULSE_SERVER=unix:<nonexistent>",
            "exit_code": None, "blocked": True,
            "wall_s": round(time.monotonic() - t0, 3)}
    gate = entry["daemon_gate_dead"]
    if not (gate.get("exit_code") == 1 and
            "onnection" in (gate.get("stderr_tail") or "")):
        failures.append("paplay: dead-server gate deviated from the "
                        "measured signature (instant rc=1 Connection "
                        "failure)")
    # (c)+(d) ordering cell: the writerless-fifo open block is identical
    # with a dead server and a live one — paplay never reaches connect.
    entry["gate_ordering_dead_fifo"] = _nowriter_cell(["paplay"], dead_env)
    go = entry["gate_ordering_dead_fifo"]
    ordering_ok = (go.get("blocked") and
                   "onnection" not in (go.get("stderr_tail") or ""))
    if not ordering_ok:
        failures.append("paplay: dead-server writerless fifo deviated "
                        "from the input-first ordering (blocked in "
                        "open(), no connection error reached)")
    entry["fifo_no_writer"] = _nowriter_cell(["paplay"])
    for cell in ("gate_ordering_dead_fifo", "fifo_no_writer"):
        nw = entry[cell]
        if not (nw.get("blocked") and nw.get("sigterm_immune") is False
                and nw.get("exit_code") == -signal.SIGTERM):
            failures.append(f"paplay: {cell} deviated from the measured "
                            "kill class (blocked, SIGTERM kills -> rc "
                            "-15)")
    # (e) name axis on identical no-magic bytes: named files + fifos +
    # rfd — sf_open_fd is name-blind so ALL reject 'Failed to open
    # audio file.' (pw-cat's .snd accept does not transfer).
    name_axis = {}
    with tempfile.TemporaryDirectory(prefix="paplay-r75-") as tmp:
        for fname in ("axis.snd", "axis.wav", "axis.bin"):
            fpath = Path(tmp) / fname
            fpath.write_bytes(snd_data)
            try:
                proc = subprocess.run(["paplay", str(fpath)],
                                      capture_output=True,
                                      timeout=CONSUMER_R75_TIMEOUT_S)
                _, pe = _paplay_fields(proc.stderr.decode(errors="replace"))
                name_axis["file:" + fname] = {
                    "exit_code": proc.returncode, "pa_error": pe}
            except subprocess.TimeoutExpired:
                name_axis["file:" + fname] = {"exit_code": None,
                                              "blocked": True}
        name_hold_s = fifo_writer_hold_s()
        fdir = Path(tmp) / "fifos"
        fdir.mkdir()
        for fname in ("axis.snd", "axis.wav", "axis.bin"):
            fifo = fdir / fname
            os.mkfifo(fifo)
            writer = threading.Thread(
                target=fifo_feed, args=(fifo, snd_data, name_hold_s),
                daemon=True)
            writer.start()
            try:
                proc = subprocess.run(["paplay", str(fifo)],
                                      capture_output=True,
                                      timeout=CONSUMER_R75_TIMEOUT_S)
                _, pe = _paplay_fields(proc.stderr.decode(errors="replace"))
                name_axis["fifo:" + fname] = {
                    "exit_code": proc.returncode, "pa_error": pe}
            except subprocess.TimeoutExpired:
                name_axis["fifo:" + fname] = {"exit_code": None,
                                              "blocked": True}
            finally:
                writer.join(timeout=name_hold_s + 5)
                reap_fifo_orphans(fifo)
    with snd_path.open("rb") as fh:
        try:
            proc = subprocess.run(["paplay"], stdin=fh, capture_output=True,
                                  timeout=CONSUMER_R75_TIMEOUT_S)
            _, pe = _paplay_fields(proc.stderr.decode(errors="replace"))
            name_axis["rfd:" + snd_name] = {
                "exit_code": proc.returncode, "pa_error": pe}
        except subprocess.TimeoutExpired:
            name_axis["rfd:" + snd_name] = {"exit_code": None,
                                            "blocked": True}
    entry["paplay_name_axis"] = {
        "member": str(snd_path.relative_to(ROOT)),
        "claim": ("sf_open_fd is name-blind -> invariant-reject "
                  "(pw-cat's .snd fork cannot transfer)"),
        "legs": name_axis}
    if not all(l.get("exit_code") == 1 for l in name_axis.values()):
        failures.append("paplay: name axis deviated from invariant-"
                        "reject (predicted rc=1 'Failed to open audio "
                        "file' on every name + transport)")
    # (f) --raw bypass on the identical .snd bytes.
    name_hold_s = fifo_writer_hold_s()
    with tempfile.TemporaryDirectory(prefix="paplay-r75-") as tmp:
        fifo = Path(tmp) / "axis.snd"
        os.mkfifo(fifo)
        writer = threading.Thread(
            target=fifo_feed, args=(fifo, snd_data, name_hold_s),
            daemon=True)
        writer.start()
        try:
            proc = subprocess.run(["paplay", "--raw", str(fifo)],
                                  capture_output=True,
                                  timeout=CONSUMER_R75_TIMEOUT_S)
            entry["raw_bypass"] = {
                "mode": "paplay --raw (decode layer skipped)",
                "fifo_name": "axis.snd",
                "exit_code": proc.returncode}
        except subprocess.TimeoutExpired:
            entry["raw_bypass"] = {"exit_code": None, "blocked": True}
        finally:
            writer.join(timeout=name_hold_s + 5)
            reap_fifo_orphans(fifo)
    if entry["raw_bypass"].get("exit_code") != 0:
        failures.append("paplay: --raw bypass deviated (predicted rc=0 "
                        "on the identical .snd fifo bytes)")
    # (g) empty-writer fifo.
    with tempfile.TemporaryDirectory(prefix="paplay-r75-") as tmp:
        fifo = Path(tmp) / "empty.wav"
        os.mkfifo(fifo)

        def empty_feed():
            try:
                open(fifo, "wb").close()
            except OSError:
                pass
        t = threading.Thread(target=empty_feed, daemon=True)
        t.start()
        try:
            proc = subprocess.run(["paplay", str(fifo)],
                                  capture_output=True,
                                  timeout=CONSUMER_R75_TIMEOUT_S)
            _, pe = _paplay_fields(proc.stderr.decode(errors="replace"))
            entry["fifo_empty_writer"] = {"exit_code": proc.returncode,
                                          "pa_error": pe}
        except subprocess.TimeoutExpired:
            entry["fifo_empty_writer"] = {"exit_code": None,
                                          "blocked": True}
        finally:
            t.join(timeout=5)
            reap_fifo_orphans(fifo)
    entry["failures"] = failures
    return entry


def consumers2_aplay_ops_entry():
    """r75 aplay ops surface — device coupling instead of a daemon gate:
    (a) `aplay -l`/`-L` device census (the viability precondition — an
        absent card list degrades the hw cell to a recorded blockage);
    (b) device axis on one member: -D null (in-process, always), aplay
        default + -D pipewire (plugin routing -> daemon-coupled on this
        host), -D hw:<first card> (kernel device -> format-coupled
        rejection measured);
    (c) writerless fifo under -D null: blocked in open(); aplay catches
        SIGTERM ('Aborted by signal Terminated') yet stays blocked ->
        SIGKILL -> -9;
    (d) name axis on identical no-magic bytes via fifos
        {snd,wav,bin}: content-parse accepts EVERY name as 'raw data'
        (invariant-accept);
    (e) empty-writer fifo -> header read error rc=1."""
    failures = []
    entry = {"probe": "aplay consumer operational surface"}
    cards = []
    try:
        proc = subprocess.run(["aplay", "-l"], capture_output=True,
                              timeout=10)
        for m in re.finditer(r"card (\d+): (\S+) \[(.*?)\], device (\d+):",
                             proc.stdout.decode(errors="replace")):
            cards.append({"card": int(m.group(1)), "card_id": m.group(2),
                          "card_name": m.group(3),
                          "device": int(m.group(4))})
        entry["device_census"] = {
            "aplay_dash_l_exit": proc.returncode,
            "playback_devices": cards}
    except (subprocess.TimeoutExpired, OSError) as exc:
        entry["device_census"] = {"aplay_dash_l_exit": None,
                                  "playback_devices": [],
                                  "error": str(exc)[:120]}
    try:
        proc = subprocess.run(["aplay", "-L"], capture_output=True,
                              timeout=10)
        names = [ln.strip() for ln in
                 proc.stdout.decode(errors="replace").splitlines()
                 if ln.strip() and not ln.startswith(" ")]
        entry["plugin_census"] = {
            "aplay_dash_L_exit": proc.returncode,
            "has_null": "null" in names,
            "has_pipewire": "pipewire" in names,
            "has_default": "default" in names}
    except (subprocess.TimeoutExpired, OSError) as exc:
        entry["plugin_census"] = {"aplay_dash_L_exit": None,
                                  "error": str(exc)[:120]}
    # (b) device axis on the dec_act member (8 kHz mono wav): -D null is
    # the matrix sink; default + pipewire are daemon-coupled plugin
    # routes on this host; hw:<first> exercises the kernel driver's
    # format constraints (this USB device rejects 8 kHz mono).
    directory, filename = TRANSPORT_R67_MEMBERS["dec_act"]
    member_path = ROOT / "live" / directory / filename
    device_legs = {}
    targets = [("null", ["-D", "null"]), ("default", []),
               ("pipewire", ["-D", "pipewire"])]
    if cards:
        targets.append(("hw_first",
                        ["-D", f"hw:{cards[0]['card']},{cards[0]['device']}"]))
    for name, dargv in targets:
        try:
            proc = subprocess.run(
                ["aplay", *dargv, str(member_path)], capture_output=True,
                timeout=CONSUMER_R75_TIMEOUT_S)
            text = proc.stderr.decode(errors="replace")
            (kind, spec), aerr = _aplay_fields(text)
            device_legs[name] = {
                "exit_code": proc.returncode, "alsa_kind": kind,
                "alsa_spec": spec, "alsa_error": aerr,
                "stderr_tail": _consumer2_tail(text, str(member_path))}
        except subprocess.TimeoutExpired:
            device_legs[name] = {"exit_code": None, "blocked": True}
    if not cards:
        device_legs["hw_first"] = {
            "blockage": "no ALSA playback card enumerated by `aplay -l`"}
    entry["device_axis"] = {"member": str(member_path.relative_to(ROOT)),
                            "legs": device_legs}
    if device_legs.get("null", {}).get("exit_code") != 0:
        failures.append("aplay: -D null device deviated from rc=0 (the "
                        "in-process sink must always accept)")
    # (c) writerless fifo under -D null.
    entry["fifo_no_writer"] = _nowriter_cell(["aplay", "-D", "null"])
    nw = entry["fifo_no_writer"]
    if not (nw.get("blocked") and nw.get("sigterm_immune")
            and nw.get("exit_code") == -signal.SIGKILL):
        failures.append("aplay: writerless fifo deviated from the "
                        "measured kill class (blocked, TERM caught but "
                        "stuck -> SIGKILL -9)")
    # (d) name axis on identical no-magic bytes: content-parse accepts
    # every fifo name as 'raw data' (u8/8000/mono) — invariant-accept.
    snd_dir, snd_name = TRANSPORT_R69_MEMBERS["extsuffix_snd"]
    snd_data = (ROOT / "live" / snd_dir / snd_name).read_bytes()
    name_hold_s = fifo_writer_hold_s()
    name_axis = {}
    with tempfile.TemporaryDirectory(prefix="aplay-r75-") as tmp:
        for fname in ("axis.snd", "axis.wav", "axis.bin"):
            fifo = Path(tmp) / fname
            os.mkfifo(fifo)
            writer = threading.Thread(
                target=fifo_feed, args=(fifo, snd_data, name_hold_s),
                daemon=True)
            writer.start()
            try:
                proc = subprocess.run(["aplay", "-D", "null", str(fifo)],
                                      capture_output=True,
                                      timeout=CONSUMER_R75_TIMEOUT_S)
                text = proc.stderr.decode(errors="replace")
                (kind, spec), aerr = _aplay_fields(text)
                name_axis[fname] = {"exit_code": proc.returncode,
                                    "alsa_kind": kind, "alsa_spec": spec,
                                    "alsa_error": aerr}
            except subprocess.TimeoutExpired:
                name_axis[fname] = {"exit_code": None, "blocked": True}
            finally:
                writer.join(timeout=name_hold_s + 5)
                reap_fifo_orphans(fifo)
    entry["aplay_name_axis"] = {
        "member": str((ROOT / "live" / snd_dir / snd_name
                       ).relative_to(ROOT)),
        "claim": ("content-parse only -> invariant-accept 'raw data' "
                  "under every fifo name"),
        "legs": name_axis}
    if not all(l.get("exit_code") == 0 and l.get("alsa_kind") == "raw data"
               for l in name_axis.values()):
        failures.append("aplay: name axis deviated from invariant-accept "
                        "('raw data' rc=0 under every fifo name)")
    # (e) empty-writer fifo -> header read error.
    with tempfile.TemporaryDirectory(prefix="aplay-r75-") as tmp:
        fifo = Path(tmp) / "empty.wav"
        os.mkfifo(fifo)

        def empty_feed():
            try:
                open(fifo, "wb").close()
            except OSError:
                pass
        t = threading.Thread(target=empty_feed, daemon=True)
        t.start()
        try:
            proc = subprocess.run(["aplay", "-D", "null", str(fifo)],
                                  capture_output=True,
                                  timeout=CONSUMER_R75_TIMEOUT_S)
            text = proc.stderr.decode(errors="replace")
            (kind, spec), aerr = _aplay_fields(text)
            entry["fifo_empty_writer"] = {"exit_code": proc.returncode,
                                          "alsa_kind": kind,
                                          "alsa_error": aerr}
        except subprocess.TimeoutExpired:
            entry["fifo_empty_writer"] = {"exit_code": None,
                                          "blocked": True}
        finally:
            t.join(timeout=5)
            reap_fifo_orphans(fifo)
    if entry["fifo_empty_writer"].get("exit_code") != 1:
        failures.append("aplay: empty-writer fifo deviated from the "
                        "measured signature (rc=1 header read error)")
    entry["failures"] = failures
    return entry


def consumers2_ffplay_ops_entry():
    """r75 ffplay ops surface — the SDL audio-driver gate + the lavf
    pull-model cells:
    (a) SDL_AUDIODRIVER axis on one member: {dummy,pulse,alsa} — dummy
        is the deterministic sink, pulse is daemon-coupled, alsa is
        card-coupled (each leg records its own gate);
    (b) writerless fifo: avformat's open blocks in the READ THREAD while
        the main loop polls (wchan hrtimer_nanosleep) — SIGTERM is
        honored by the event loop -> graceful exit 123, a third kill
        class beside paplay's -15 and aplay/pw-cat's -9;
    (c) -ss 2 position cell on the 4.0 s wav: seekable file seeks;
        non-seekable stdin logs 'could not seek' and rescues by
        decode-discard — the fork is in the seek PATH, not the played
        extent (~2 s wall both arms);
    (d) empty-writer fifo -> 'Invalid data found' at rc=0 (rc is never
        the verdict)."""
    failures = []
    entry = {"probe": "ffplay consumer operational surface"}
    directory, filename = TRANSPORT_R67_MEMBERS["dec_act"]
    member_path = ROOT / "live" / directory / filename
    driver_legs = {}
    for drv in ("dummy", "pulse", "alsa"):
        env = {**os.environ, "SDL_AUDIODRIVER": drv}
        try:
            proc = subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-v", "info",
                 str(member_path)], capture_output=True,
                env=env, timeout=CONSUMER_R75_TIMEOUT_S)
            text = proc.stderr.decode(errors="replace")
            detected = re.search(r"Input #0, ([^,\s]+), from", text)
            sdl_err = re.search(r"(SDL[^:\n]*:[^\n]*|could not (?:open|"
                                r"initialize)[^\n]*)", text)
            driver_legs[drv] = {
                "exit_code": proc.returncode,
                "ffplay_detected": detected.group(1) if detected else None,
                "error": sdl_err.group(0).strip()[:120] if sdl_err else None,
                # `ALSA lib ... underrun` diagnostics and the periodic
                # status line are timing-dependent — dropped before the
                # tail so the receipt stays deterministic.
                "stderr_tail": _consumer2_tail(
                    "\n".join(ln for ln in text.splitlines()
                              if not ln.startswith("ALSA lib")
                              and not _FFPLAY_STATUS_TAIL.search(ln)),
                    str(member_path))}
        except subprocess.TimeoutExpired:
            driver_legs[drv] = {"exit_code": None, "blocked": True}
    entry["sdl_driver_axis"] = {
        "member": str(member_path.relative_to(ROOT)),
        "legs": driver_legs}
    if driver_legs.get("dummy", {}).get("exit_code") != 0:
        failures.append("ffplay: SDL_AUDIODRIVER=dummy deviated from "
                        "rc=0 (the deterministic sink must always work)")
    # (b) writerless fifo — read-thread open block, main-loop TERM exit.
    entry["fifo_no_writer"] = _nowriter_cell(
        ["ffplay", "-nodisp", "-autoexit", "-v", "info"],
        extra_env=FFPLAY_R75_ENV)
    nw = entry["fifo_no_writer"]
    if not (nw.get("blocked") and nw.get("sigterm_immune") is False
            and nw.get("exit_code") == 123):
        failures.append("ffplay: writerless fifo deviated from the "
                        "measured kill class (blocked, SIGTERM -> "
                        "graceful rc 123)")
    # (c) -ss position cell: seekable arm seeks, non-seekable logs
    # 'could not seek' + decode-discard rescue.
    hold_s = fifo_writer_hold_s()
    data = CONSUMER_R73_PACER.read_bytes()
    pos = {}
    pos["file"] = ffplay_leg("file", CONSUMER_R73_PACER, data, hold_s,
                             extra_opts=("-ss", str(CONSUMER_R75_START_S)))
    pos["stdin_pipe"] = ffplay_leg(
        "stdin_pipe", CONSUMER_R73_PACER, data, hold_s,
        extra_opts=("-ss", str(CONSUMER_R75_START_S)))
    entry["ffplay_startpos"] = {
        "member": str(CONSUMER_R73_PACER.relative_to(ROOT)),
        "cell": f"ffplay -ss {CONSUMER_R75_START_S} on a seeking wav",
        "predicted": ("file arm seeks (no 'could not seek'); stdin arm "
                      "logs 'could not seek' and rescues by "
                      "decode-discard — path fork, not extent fork"),
        "legs": pos}
    f_leg, s_leg = pos["file"], pos["stdin_pipe"]
    if not (f_leg["could_not_seek"] is False
            and s_leg["could_not_seek"] is True
            and f_leg["exit_code"] == 0 and s_leg["exit_code"] == 0):
        failures.append("ffplay: -ss position cell deviated from the "
                        "measured shape (seek ok on file / could-not-"
                        "seek + decode-discard on stdin, rc=0 both)")
    # (d) empty-writer fifo.
    with tempfile.TemporaryDirectory(prefix="ffplay-r75-") as tmp:
        fifo = Path(tmp) / "empty.wav"
        os.mkfifo(fifo)

        def empty_feed():
            try:
                open(fifo, "wb").close()
            except OSError:
                pass
        t = threading.Thread(target=empty_feed, daemon=True)
        t.start()
        try:
            proc = subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-v", "info",
                 str(fifo)], capture_output=True, env={**os.environ,
                                                      **FFPLAY_R75_ENV},
                timeout=CONSUMER_R75_TIMEOUT_S)
            text = proc.stderr.decode(errors="replace")
            entry["fifo_empty_writer"] = {
                "exit_code": proc.returncode,
                "ffplay_invalid": ("Invalid data found when processing "
                                   "input" in text),
                "stderr_tail": _consumer2_tail(
                    "\n".join(ln for ln in text.splitlines()
                              if not _FFPLAY_STATUS_TAIL.search(ln)),
                    "empty.wav")}
        except subprocess.TimeoutExpired:
            entry["fifo_empty_writer"] = {"exit_code": None,
                                          "blocked": True}
        finally:
            t.join(timeout=5)
            reap_fifo_orphans(fifo)
    if entry["fifo_empty_writer"].get("exit_code") != 0:
        failures.append("ffplay: empty-writer fifo deviated from the "
                        "measured signature (rc=0 'Invalid data found')")
    entry["failures"] = failures
    return entry


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
                                    "fifo_writer_hold_s": fifo_writer_hold_s(),
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
    parser.add_argument("--probe-fifo-hold-ladder-r70", action="store_true")
    parser.add_argument("--probe-ffprobe-transport-r71", action="store_true")
    parser.add_argument("--probe-sndfile-transport-r72",
                        action="store_true")
    parser.add_argument("--probe-consumers-r73", action="store_true")
    parser.add_argument("--probe-lavfsweep-r74", action="store_true")
    parser.add_argument("--probe-consumers2-r75", action="store_true")
    args = parser.parse_args()
    if sum([args.probe_slope, args.probe_failing, args.probe_flat, args.probe_layer_flat, args.probe_layer_join, args.probe_layer_slope, args.probe_layer_alt_flat, args.probe_layer_alt_join, args.probe_layer_alt_slope, args.probe_layer_alt_reverse, args.probe_layer_third_slope, args.probe_layer_third_slope_edge_pass, args.probe_layer_third_slope_edge_fail, args.probe_layer_third_join, args.probe_layer_third_join_edge_pass, args.probe_layer_third_join_edge_fail, args.probe_invalid, args.probe_ui_clone, args.probe_ui_duration_below, args.probe_ui_duration_at, args.probe_ui_centroid_below, args.probe_ui_centroid_above, args.probe_ui_lower_centroid_below, args.probe_ui_lower_centroid_above, args.probe_ui_orientation_forward, args.probe_ui_orientation_reverse, args.probe_ui_joint_below, args.probe_ui_mixed_pass, args.probe_ambience_centroid_below, args.probe_ambience_centroid_above, args.probe_ambience_orientation_forward, args.probe_ambience_orientation_reverse, args.probe_outer_endpoint_983, args.probe_outer_endpoint_984, args.probe_outer_slope_32, args.probe_outer_slope_33, args.probe_ui_peak_31129, args.probe_ui_peak_31130, args.probe_ui_crest_46, args.probe_ui_crest_47, args.probe_ui_tolerance_5807, args.probe_ui_tolerance_5809, args.probe_ui_lower_tolerance_5713, args.probe_ui_lower_tolerance_5711, args.probe_ui_absolute_centroid_below, args.probe_ui_absolute_centroid_above, args.probe_ui_upper_centroid_below, args.probe_ui_upper_centroid_above, args.probe_ui_rate_47999, args.probe_ui_rate_48000, args.probe_ui_rate_48001, args.probe_ui_rate_48000_r49, args.probe_ui_channel_stereo, args.probe_ui_channel_mono, args.probe_ui_pcm24, args.probe_ui_pcm16, args.probe_ui_pcm8, args.probe_ui_pcm16_r52, args.probe_ui_float32, args.probe_ui_pcm16_r53, args.probe_ui_pcm32, args.probe_ui_pcm16_r54, args.probe_ui_extensible_pcm16, args.probe_ui_standard_pcm16_r55, args.probe_ui_extensible_mask_zero, args.probe_ui_extensible_mask_center, args.probe_ui_extensible_valid_15, args.probe_ui_extensible_valid_16, args.probe_ui_extensible_valid_14_r58, args.probe_ui_extensible_valid_16_r58, args.probe_ui_extensible_valid_13_r59, args.probe_ui_extensible_valid_16_r59, args.probe_ui_extensible_valid_0_r60, args.probe_ui_extensible_valid_16_r60, args.probe_ui_extensible_valid_17_r61, args.probe_ui_extensible_valid_16_r61, args.probe_ui_extensible_valid_24_r62, args.probe_ui_extensible_valid_32_r62, args.probe_ui_route_act_84_r63, args.probe_ui_route_act_00_r63, args.probe_ui_extensible_valid_8_r64, args.probe_ui_extensible_valid_9_r64, args.probe_ui_extensible_valid_24_r64, args.probe_ui_extensible_valid_25_r64, args.probe_ui_extensible_valid_56_r64, args.probe_ui_extensible_valid_57_r64, args.probe_ui_preempt_act_r65, args.probe_ui_preempt_gsrt_r65, args.probe_ui_preempt_hcom_r65, args.probe_ui_preempt_both_r65, args.probe_ui_dec_hcom_r66, args.probe_ui_dec_act_r66, args.probe_ui_lengate_gsrt_24_r66, args.probe_ui_lengate_gsrt_25_r66, args.probe_ui_lengate_hcom_131_r66, args.probe_ui_lengate_hcom_132_r66, args.probe_transport_preempt_act_r67, args.probe_transport_preempt_gsrt_r67, args.probe_transport_preempt_hcom_r67, args.probe_transport_preempt_both_r67, args.probe_transport_dec_hcom_r67, args.probe_transport_dec_act_r67, args.probe_transport_lengate_gsrt_24_r67, args.probe_transport_lengate_gsrt_25_r67, args.probe_transport_lengate_hcom_131_r67, args.probe_transport_lengate_hcom_132_r67, args.probe_transport_posttable_nomatch_r68, args.probe_transport_txw_piperefuse_r68, args.probe_transport_extsuffix_wav_r69, args.probe_transport_extsuffix_bin_r69, args.probe_transport_extsuffix_txw_r69, args.probe_transport_extsuffix_f32_r69, args.probe_transport_extsuffix_snd_r69, args.probe_fifo_hold_ladder_r70, args.probe_ffprobe_transport_r71, args.probe_sndfile_transport_r72, args.probe_consumers_r73, args.probe_lavfsweep_r74, args.probe_consumers2_r75]) > 1:
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
            *(["--probe-fifo-hold-ladder-r70"] if args.probe_fifo_hold_ladder_r70 else []),
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
    if args.probe_fifo_hold_ladder_r70:
        # r70: pin fifo_writer_hold_s as a MEASURED determinism bound. r67
        # chose 1.0 s because a bare one-shot writer raced the ffmpeg
        # bridge's open #2 (5/5 shell runs -> exit-2 au-magic; one python
        # run blocked >10 s). This ladder sweeps hold x feed on the dec_act
        # member — the arm whose verdict needs open #2 — and records the
        # per-cell verdict DISTRIBUTION, so the bound is measured rather
        # than asserted. The chunked feed (writer attached through delivery)
        # is the claim's 'correctly blocking writer' arm: if the verdict is
        # binary on writer-attached-at-open-#2, chunked is stable at h=0
        # whenever the feed window alone covers the re-open.
        directory, filename = TRANSPORT_R67_MEMBERS[TRANSPORT_R70_MEMBER]
        measurements["fifo_hold_ladder_dec_act_r70_probe"] = fifo_hold_ladder_entry(
            TRANSPORT_R70_MEMBER, ROOT / "live" / directory / filename)
    if args.probe_ffprobe_transport_r71:
        # r71: SECOND DECODER runtime (ffmpeg n9.0.1/ffprobe) on the tracked
        # transport member set — a NEW parallel ledger family, prior rows
        # untouched. The falsifiable claim (content-probing vs the r68/r69
        # suffix/named axis) is measured per-member: extsuffix_* carry
        # identical bytes under five names (does ffmpeg care about the
        # name at all?), posttable/txw carry post-table content, dec_* are
        # the members whose SOX verdicts already cross the ffmpeg bridge.
        for member, (directory, filename) in TRANSPORT_R71_MEMBERS.items():
            path = ROOT / "live" / directory / filename
            measurements[f"ffprobe_{member}_r71_probe"] = ffprobe_transport_entry(
                member, path)
    if args.probe_consumers_r73:
        # r73: CONSUMER class — pw-cat (PipeWire realtime playback) + mpv
        # (lavf detect/decode) on the canonical member x transport matrix.
        # A NEW parallel ledger family, prior rows untouched. The MEASURED
        # claim (r73 adjudicated — the briefed class-polarity partition was
        # falsified corpus-wide, confirmed member-locally): two forks with
        # different drivers — mpv x dec_hcom inverts on the seekable bit
        # (lavf refresh-seek -> synthetic EPERM, rc2 vs rc0; redirected_fd
        # groups with file since the fd IS seekable), pw-cat x .snd forks
        # on the NAME axis (its decode layer IS libsndfile — inherits the
        # r72 post-sniff extension fallback; pwcat_name_axis isolates it:
        # identical bytes via .snd/.wav/.bin fifos -> rc 0/1/1).
        # The ops entry pins the pw-cat daemon gate + fifo writer semantics
        # + playback-paced consumption (viability-conditional: needs a
        # reachable PipeWire daemon).
        measurements["consumer_pwcat_ops_r73_probe"] = consumer_ops_entry()
        for member, (directory, filename) in CONSUMER_R73_MEMBERS.items():
            path = ROOT / "live" / directory / filename
            measurements[f"consumer_{member}_r73_probe"] = \
                consumer_transport_entry(member, path)
    if args.probe_lavfsweep_r74:
        # r74: lavf NO-SEEK demuxer sweep (xconnector X2) + pw-cat ops-2
        # (X3). mpv's seekable-bit fork is predicted PER MEMBER from the
        # demuxer's source-level seek capability: iss/apc/acm satisfy all
        # four clauses (probe-detected, no read_seek/read_timestamp, no
        # GENERIC_INDEX, non-pcm codec) and must fork; adx/aifc/dec_act
        # fail clause (3)/(2)/(4) respectively and must stay invariant.
        # New members are generated byte-deterministically under
        # corpus/live/round-74 before the sweep so the arm is
        # self-sufficient on a fresh tree; a generation blockage degrades
        # to a recorded blockage, never a fabricated member.
        gen = build_lavf_r74_members()
        measurements["lavfsweep_generation_r74_probe"] = {
            "probe": "lavf r74 member generation (byte-deterministic)",
            "failures": [], **gen}
        for member, (directory, filename, prediction) in \
                LAVF_R74_MEMBERS.items():
            path = ROOT / "live" / directory / filename
            if member in gen["blocked"] or not path.exists():
                measurements[f"lavfsweep_{member}_r74_probe"] = {
                    "pair_member": member, "predicted": prediction,
                    "blockage": gen["blocked"].get(
                        member, "member absent after generation"),
                    "failures": []}
                continue
            measurements[f"lavfsweep_{member}_r74_probe"] = \
                lavf_transport_entry(member, path)
        measurements["lavf_startpos_wav_r74_probe"] = \
            lavf_startpos_entry(LAVF_R74_PACER)
        measurements["consumer_pwcat_ops2_r74_probe"] = pwcat_ops2_entry()
    if args.probe_consumers2_r75:
        # r75: consumer breadth-2 — paplay (pacat/pipewire-pulse, fd-open
        # libsndfile = name-blind), aplay (in-process ALSA, device-coupled
        # not daemon-coupled, raw-accept), ffplay (SDL pull-model — a
        # second lavf consumer: no post-probe refresh seek, so mpv's
        # dec_hcom seekable-bit fork cannot transfer; rc is never the
        # verdict — invalid input still exits 0). A NEW parallel ledger
        # family, prior rows untouched. Ops rows pin each consumer's
        # gate (pulse server / ALSA card / SDL driver), the writerless-
        # fifo kill classes (paplay -15, aplay -9, ffplay 123), and the
        # paplay .snd name-axis control (predicted invariant-reject).
        measurements["consumer2_paplay_ops_r75_probe"] = \
            consumers2_paplay_ops_entry()
        measurements["consumer2_aplay_ops_r75_probe"] = \
            consumers2_aplay_ops_entry()
        measurements["consumer2_ffplay_ops_r75_probe"] = \
            consumers2_ffplay_ops_entry()
        for member, (directory, filename) in CONSUMER_R75_MEMBERS.items():
            path = ROOT / "live" / directory / filename
            measurements[f"consumer2_{member}_r75_probe"] = \
                consumer2_transport_entry(member, path)
    if args.probe_sndfile_transport_r72:
        # r72: THIRD DECODER (libsndfile) on the same canonical members —
        # the 3-decoder verdict lattice. Claim under test (critic-corrected):
        # measured partition is {sox-only (txw-seekable/.f32-named),
        # sox+sndfile joint (.snd-named), ffmpeg-strictest} — NOT
        # "sndfile-only .snd" (sox accepts it too) nor "ffmpeg superset"
        # (ffmpeg detect set is the SMALLEST: 8 < sndfile 10 < sox 11-14).
        for member, (directory, filename) in TRANSPORT_R72_MEMBERS.items():
            path = ROOT / "live" / directory / filename
            measurements[f"sndfile_{member}_r72_probe"] = sndfile_transport_entry(
                member, path)
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
    mode = "probe-consumers2-r75" if args.probe_consumers2_r75 else "probe-lavfsweep-r74" if args.probe_lavfsweep_r74 else "probe-consumers-r73" if args.probe_consumers_r73 else "probe-sndfile-transport-r72" if args.probe_sndfile_transport_r72 else "probe-ffprobe-transport-r71" if args.probe_ffprobe_transport_r71 else "probe-fifo-hold-ladder-r70" if args.probe_fifo_hold_ladder_r70 else "probe-transport-extsuffix-wav-r69" if args.probe_transport_extsuffix_wav_r69 else "probe-transport-extsuffix-bin-r69" if args.probe_transport_extsuffix_bin_r69 else "probe-transport-extsuffix-txw-r69" if args.probe_transport_extsuffix_txw_r69 else "probe-transport-extsuffix-f32-r69" if args.probe_transport_extsuffix_f32_r69 else "probe-transport-extsuffix-snd-r69" if args.probe_transport_extsuffix_snd_r69 else "probe-transport-posttable-nomatch-r68" if args.probe_transport_posttable_nomatch_r68 else "probe-transport-txw-piperefuse-r68" if args.probe_transport_txw_piperefuse_r68 else "probe-transport-preempt-act-r67" if args.probe_transport_preempt_act_r67 else "probe-transport-preempt-gsrt-r67" if args.probe_transport_preempt_gsrt_r67 else "probe-transport-preempt-hcom-r67" if args.probe_transport_preempt_hcom_r67 else "probe-transport-preempt-both-r67" if args.probe_transport_preempt_both_r67 else "probe-transport-dec-hcom-r67" if args.probe_transport_dec_hcom_r67 else "probe-transport-dec-act-r67" if args.probe_transport_dec_act_r67 else "probe-transport-lengate-gsrt-24-r67" if args.probe_transport_lengate_gsrt_24_r67 else "probe-transport-lengate-gsrt-25-r67" if args.probe_transport_lengate_gsrt_25_r67 else "probe-transport-lengate-hcom-131-r67" if args.probe_transport_lengate_hcom_131_r67 else "probe-transport-lengate-hcom-132-r67" if args.probe_transport_lengate_hcom_132_r67 else "probe-ui-dec-hcom-r66" if args.probe_ui_dec_hcom_r66 else "probe-ui-dec-act-r66" if args.probe_ui_dec_act_r66 else "probe-ui-lengate-gsrt-24-r66" if args.probe_ui_lengate_gsrt_24_r66 else "probe-ui-lengate-gsrt-25-r66" if args.probe_ui_lengate_gsrt_25_r66 else "probe-ui-lengate-hcom-131-r66" if args.probe_ui_lengate_hcom_131_r66 else "probe-ui-lengate-hcom-132-r66" if args.probe_ui_lengate_hcom_132_r66 else "probe-ui-preempt-act-r65" if args.probe_ui_preempt_act_r65 else "probe-ui-preempt-gsrt-r65" if args.probe_ui_preempt_gsrt_r65 else "probe-ui-preempt-hcom-r65" if args.probe_ui_preempt_hcom_r65 else "probe-ui-preempt-both-r65" if args.probe_ui_preempt_both_r65 else "probe-ui-extensible-valid-8-r64" if args.probe_ui_extensible_valid_8_r64 else "probe-ui-extensible-valid-9-r64" if args.probe_ui_extensible_valid_9_r64 else "probe-ui-extensible-valid-24-r64" if args.probe_ui_extensible_valid_24_r64 else "probe-ui-extensible-valid-25-r64" if args.probe_ui_extensible_valid_25_r64 else "probe-ui-extensible-valid-56-r64" if args.probe_ui_extensible_valid_56_r64 else "probe-ui-extensible-valid-57-r64" if args.probe_ui_extensible_valid_57_r64 else "probe-ui-route-act-84-r63" if args.probe_ui_route_act_84_r63 else "probe-ui-route-act-00-r63" if args.probe_ui_route_act_00_r63 else "probe-ui-extensible-valid-24-r62" if args.probe_ui_extensible_valid_24_r62 else ("probe-ui-extensible-valid-32-r62" if args.probe_ui_extensible_valid_32_r62 else ("probe-ui-extensible-valid-17-r61" if args.probe_ui_extensible_valid_17_r61 else ("probe-ui-extensible-valid-16-r61" if args.probe_ui_extensible_valid_16_r61 else ("probe-ui-extensible-valid-0-r60" if args.probe_ui_extensible_valid_0_r60 else ("probe-ui-extensible-valid-16-r60" if args.probe_ui_extensible_valid_16_r60 else ("probe-ui-extensible-valid-13-r59" if args.probe_ui_extensible_valid_13_r59 else ("probe-ui-extensible-valid-16-r59" if args.probe_ui_extensible_valid_16_r59 else ("probe-ui-extensible-valid-14-r58" if args.probe_ui_extensible_valid_14_r58 else ("probe-ui-extensible-valid-16-r58" if args.probe_ui_extensible_valid_16_r58 else ("probe-ui-extensible-valid-15" if args.probe_ui_extensible_valid_15 else ("probe-ui-extensible-valid-16" if args.probe_ui_extensible_valid_16 else ("probe-ui-extensible-mask-zero" if args.probe_ui_extensible_mask_zero else ("probe-ui-extensible-mask-center" if args.probe_ui_extensible_mask_center else ("probe-ui-extensible-pcm16" if args.probe_ui_extensible_pcm16 else ("probe-ui-standard-pcm16-r55" if args.probe_ui_standard_pcm16_r55 else ("probe-ui-pcm32" if args.probe_ui_pcm32 else ("probe-ui-pcm16-r54" if args.probe_ui_pcm16_r54 else ("probe-ui-float32" if args.probe_ui_float32 else ("probe-ui-pcm16-r53" if args.probe_ui_pcm16_r53 else ("probe-ui-pcm8" if args.probe_ui_pcm8 else ("probe-ui-pcm16-r52" if args.probe_ui_pcm16_r52 else ("probe-ui-pcm24" if args.probe_ui_pcm24 else ("probe-ui-pcm16" if args.probe_ui_pcm16 else ("probe-ui-channel-stereo" if args.probe_ui_channel_stereo else ("probe-ui-channel-mono" if args.probe_ui_channel_mono else ("probe-ui-rate-48001" if args.probe_ui_rate_48001 else ("probe-ui-rate-48000-r49" if args.probe_ui_rate_48000_r49 else ("probe-ui-rate-47999" if args.probe_ui_rate_47999 else ("probe-ui-rate-48000" if args.probe_ui_rate_48000 else ("probe-ui-upper-centroid-below" if args.probe_ui_upper_centroid_below else ("probe-ui-upper-centroid-above" if args.probe_ui_upper_centroid_above else ("probe-ui-absolute-centroid-below" if args.probe_ui_absolute_centroid_below else ("probe-ui-absolute-centroid-above" if args.probe_ui_absolute_centroid_above else ("probe-ui-lower-tolerance-5713" if args.probe_ui_lower_tolerance_5713 else ("probe-ui-lower-tolerance-5711" if args.probe_ui_lower_tolerance_5711 else ("probe-ui-tolerance-5807" if args.probe_ui_tolerance_5807 else ("probe-ui-tolerance-5809" if args.probe_ui_tolerance_5809 else ("probe-ui-crest-46" if args.probe_ui_crest_46 else ("probe-ui-crest-47" if args.probe_ui_crest_47 else ("probe-ui-peak-31129" if args.probe_ui_peak_31129 else ("probe-ui-peak-31130" if args.probe_ui_peak_31130 else ("probe-outer-slope-32" if args.probe_outer_slope_32 else ("probe-outer-slope-33" if args.probe_outer_slope_33 else ("probe-outer-endpoint-983" if args.probe_outer_endpoint_983 else ("probe-outer-endpoint-984" if args.probe_outer_endpoint_984 else ("probe-ambience-orientation-forward" if args.probe_ambience_orientation_forward else ("probe-ambience-orientation-reverse" if args.probe_ambience_orientation_reverse else ("probe-ambience-centroid-above" if args.probe_ambience_centroid_above else ("probe-ambience-centroid-below" if args.probe_ambience_centroid_below else ("probe-ui-mixed-pass" if args.probe_ui_mixed_pass else ("probe-ui-joint-below" if args.probe_ui_joint_below else ("probe-ui-orientation-forward" if args.probe_ui_orientation_forward else ("probe-ui-orientation-reverse" if args.probe_ui_orientation_reverse else ("probe-ui-lower-centroid-below" if args.probe_ui_lower_centroid_below else ("probe-ui-lower-centroid-above" if args.probe_ui_lower_centroid_above else ("probe-ui-centroid-below" if args.probe_ui_centroid_below else ("probe-ui-centroid-above" if args.probe_ui_centroid_above else ("probe-ui-duration-below" if args.probe_ui_duration_below else ("probe-ui-duration-at" if args.probe_ui_duration_at else ("probe-ui-clone" if args.probe_ui_clone else ("probe-layer-third-join-edge-pass" if args.probe_layer_third_join_edge_pass else ("probe-layer-third-join-edge-fail" if args.probe_layer_third_join_edge_fail else ("probe-layer-third-join" if args.probe_layer_third_join else ("probe-layer-third-slope-edge-pass" if args.probe_layer_third_slope_edge_pass else ("probe-layer-third-slope-edge-fail" if args.probe_layer_third_slope_edge_fail else "probe-layer-third-slope" if args.probe_layer_third_slope else ("probe-layer-alt-reverse" if args.probe_layer_alt_reverse else ("probe-layer-alt-slope" if args.probe_layer_alt_slope else ("probe-layer-alt-join" if args.probe_layer_alt_join else ("probe-layer-alt-flat" if args.probe_layer_alt_flat else ("probe-layer-slope" if args.probe_layer_slope else ("probe-layer-join" if args.probe_layer_join else ("probe-layer-flat" if args.probe_layer_flat else ("probe-flat" if args.probe_flat else ("probe-slope" if args.probe_slope else ("probe-failing" if args.probe_failing else "normal")))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))
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
    suffix = "-consumers2-r75" if args.probe_consumers2_r75 else "-lavfsweep-r74" if args.probe_lavfsweep_r74 else "-consumers-r73" if args.probe_consumers_r73 else "-sndfile-transport-r72" if args.probe_sndfile_transport_r72 else "-ffprobe-transport-r71" if args.probe_ffprobe_transport_r71 else "-fifo-hold-ladder-r70" if args.probe_fifo_hold_ladder_r70 else "-transport-extsuffix-wav-r69" if args.probe_transport_extsuffix_wav_r69 else "-transport-extsuffix-bin-r69" if args.probe_transport_extsuffix_bin_r69 else "-transport-extsuffix-txw-r69" if args.probe_transport_extsuffix_txw_r69 else "-transport-extsuffix-f32-r69" if args.probe_transport_extsuffix_f32_r69 else "-transport-extsuffix-snd-r69" if args.probe_transport_extsuffix_snd_r69 else "-transport-posttable-nomatch-r68" if args.probe_transport_posttable_nomatch_r68 else "-transport-txw-piperefuse-r68" if args.probe_transport_txw_piperefuse_r68 else "-transport-preempt-act-r67" if args.probe_transport_preempt_act_r67 else "-transport-preempt-gsrt-r67" if args.probe_transport_preempt_gsrt_r67 else "-transport-preempt-hcom-r67" if args.probe_transport_preempt_hcom_r67 else "-transport-preempt-both-r67" if args.probe_transport_preempt_both_r67 else "-transport-dec-hcom-r67" if args.probe_transport_dec_hcom_r67 else "-transport-dec-act-r67" if args.probe_transport_dec_act_r67 else "-transport-lengate-gsrt-24-r67" if args.probe_transport_lengate_gsrt_24_r67 else "-transport-lengate-gsrt-25-r67" if args.probe_transport_lengate_gsrt_25_r67 else "-transport-lengate-hcom-131-r67" if args.probe_transport_lengate_hcom_131_r67 else "-transport-lengate-hcom-132-r67" if args.probe_transport_lengate_hcom_132_r67 else "-ui-dec-hcom-r66" if args.probe_ui_dec_hcom_r66 else "-ui-dec-act-r66" if args.probe_ui_dec_act_r66 else "-ui-lengate-gsrt-24-r66" if args.probe_ui_lengate_gsrt_24_r66 else "-ui-lengate-gsrt-25-r66" if args.probe_ui_lengate_gsrt_25_r66 else "-ui-lengate-hcom-131-r66" if args.probe_ui_lengate_hcom_131_r66 else "-ui-lengate-hcom-132-r66" if args.probe_ui_lengate_hcom_132_r66 else "-ui-preempt-act-r65" if args.probe_ui_preempt_act_r65 else "-ui-preempt-gsrt-r65" if args.probe_ui_preempt_gsrt_r65 else "-ui-preempt-hcom-r65" if args.probe_ui_preempt_hcom_r65 else "-ui-preempt-both-r65" if args.probe_ui_preempt_both_r65 else "-ui-extensible-valid-8-r64" if args.probe_ui_extensible_valid_8_r64 else "-ui-extensible-valid-9-r64" if args.probe_ui_extensible_valid_9_r64 else "-ui-extensible-valid-24-r64" if args.probe_ui_extensible_valid_24_r64 else "-ui-extensible-valid-25-r64" if args.probe_ui_extensible_valid_25_r64 else "-ui-extensible-valid-56-r64" if args.probe_ui_extensible_valid_56_r64 else "-ui-extensible-valid-57-r64" if args.probe_ui_extensible_valid_57_r64 else "-ui-route-act-84-r63" if args.probe_ui_route_act_84_r63 else "-ui-route-act-00-r63" if args.probe_ui_route_act_00_r63 else "-ui-extensible-valid-24-r62" if args.probe_ui_extensible_valid_24_r62 else ("-ui-extensible-valid-32-r62" if args.probe_ui_extensible_valid_32_r62 else ("-ui-extensible-valid-17-r61" if args.probe_ui_extensible_valid_17_r61 else ("-ui-extensible-valid-16-r61" if args.probe_ui_extensible_valid_16_r61 else ("-ui-extensible-valid-0-r60" if args.probe_ui_extensible_valid_0_r60 else ("-ui-extensible-valid-16-r60" if args.probe_ui_extensible_valid_16_r60 else ("-ui-extensible-valid-13-r59" if args.probe_ui_extensible_valid_13_r59 else ("-ui-extensible-valid-16-r59" if args.probe_ui_extensible_valid_16_r59 else ("-ui-extensible-valid-14-r58" if args.probe_ui_extensible_valid_14_r58 else ("-ui-extensible-valid-16-r58" if args.probe_ui_extensible_valid_16_r58 else ("-ui-extensible-valid-15" if args.probe_ui_extensible_valid_15 else ("-ui-extensible-valid-16" if args.probe_ui_extensible_valid_16 else ("-ui-extensible-mask-zero" if args.probe_ui_extensible_mask_zero else ("-ui-extensible-mask-center" if args.probe_ui_extensible_mask_center else ("-ui-extensible-pcm16" if args.probe_ui_extensible_pcm16 else ("-ui-standard-pcm16-r55" if args.probe_ui_standard_pcm16_r55 else ("-ui-pcm32" if args.probe_ui_pcm32 else ("-ui-pcm16-r54" if args.probe_ui_pcm16_r54 else ("-ui-float32" if args.probe_ui_float32 else ("-ui-pcm16-r53" if args.probe_ui_pcm16_r53 else ("-ui-pcm8" if args.probe_ui_pcm8 else ("-ui-pcm16-r52" if args.probe_ui_pcm16_r52 else ("-ui-pcm24" if args.probe_ui_pcm24 else ("-ui-pcm16" if args.probe_ui_pcm16 else ("-ui-channel-stereo" if args.probe_ui_channel_stereo else ("-ui-channel-mono" if args.probe_ui_channel_mono else ("-ui-rate-48001" if args.probe_ui_rate_48001 else ("-ui-rate-48000-r49" if args.probe_ui_rate_48000_r49 else ("-ui-rate-47999" if args.probe_ui_rate_47999 else ("-ui-rate-48000" if args.probe_ui_rate_48000 else ("-ui-upper-centroid-below" if args.probe_ui_upper_centroid_below else ("-ui-upper-centroid-above" if args.probe_ui_upper_centroid_above else ("-ui-absolute-centroid-below" if args.probe_ui_absolute_centroid_below else ("-ui-absolute-centroid-above" if args.probe_ui_absolute_centroid_above else ("-ui-lower-tolerance-5713" if args.probe_ui_lower_tolerance_5713 else ("-ui-lower-tolerance-5711" if args.probe_ui_lower_tolerance_5711 else ("-ui-tolerance-5807" if args.probe_ui_tolerance_5807 else ("-ui-tolerance-5809" if args.probe_ui_tolerance_5809 else ("-ui-crest-46" if args.probe_ui_crest_46 else ("-ui-crest-47" if args.probe_ui_crest_47 else ("-ui-peak-31129" if args.probe_ui_peak_31129 else ("-ui-peak-31130" if args.probe_ui_peak_31130 else ("-outer-slope-32" if args.probe_outer_slope_32 else ("-outer-slope-33" if args.probe_outer_slope_33 else ("-outer-endpoint-983" if args.probe_outer_endpoint_983 else ("-outer-endpoint-984" if args.probe_outer_endpoint_984 else ("-ambience-orientation-forward" if args.probe_ambience_orientation_forward else ("-ambience-orientation-reverse" if args.probe_ambience_orientation_reverse else ("-ambience-centroid-above" if args.probe_ambience_centroid_above else ("-ambience-centroid-below" if args.probe_ambience_centroid_below else ("-ui-mixed-pass" if args.probe_ui_mixed_pass else ("-ui-joint-below" if args.probe_ui_joint_below else ("-ui-orientation-forward" if args.probe_ui_orientation_forward else ("-ui-orientation-reverse" if args.probe_ui_orientation_reverse else ("-ui-lower-centroid-below" if args.probe_ui_lower_centroid_below else ("-ui-lower-centroid-above" if args.probe_ui_lower_centroid_above else ("-ui-centroid-below" if args.probe_ui_centroid_below else ("-ui-centroid-above" if args.probe_ui_centroid_above else ("-ui-duration-below" if args.probe_ui_duration_below else ("-ui-duration-at" if args.probe_ui_duration_at else ("-ui-clone" if args.probe_ui_clone else ("-layer-third-join-edge-pass" if args.probe_layer_third_join_edge_pass else ("-layer-third-join-edge-fail" if args.probe_layer_third_join_edge_fail else ("-layer-third-join" if args.probe_layer_third_join else ("-layer-third-slope-edge-pass" if args.probe_layer_third_slope_edge_pass else ("-layer-third-slope-edge-fail" if args.probe_layer_third_slope_edge_fail else "-layer-third-slope" if args.probe_layer_third_slope else ("-layer-alt-reverse" if args.probe_layer_alt_reverse else ("-layer-alt-slope" if args.probe_layer_alt_slope else ("-layer-alt-join" if args.probe_layer_alt_join else ("-layer-alt-flat" if args.probe_layer_alt_flat else ("-layer-slope" if args.probe_layer_slope else ("-layer-join" if args.probe_layer_join else ("-layer-flat" if args.probe_layer_flat else ("-flat" if args.probe_flat else ("-slope" if args.probe_slope else ("-failing" if args.probe_failing else "-normal")))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))
    out = ROOT / "live" / "runs" / (stamp + suffix)
    out.mkdir(parents=True)
    (out / "measurements.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    failed = {k: v["failures"] for k,v in measurements.items() if v["failures"]}
    print(json.dumps({"receipt": str(out / "measurements.json"), "failures": failed}))
    return bool(failed)


if __name__ == "__main__":
    sys.exit(main())
