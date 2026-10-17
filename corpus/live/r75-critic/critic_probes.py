#!/usr/bin/env python3
"""r75-critic counterexample probes.

Pre-land falsification of the r75 audio-author declared surface
(paplay / aplay / ffplay on the canonical member x transport matrix).
Evidence-only: writes receipts under corpus/live/r75-critic/; touches no
tracked file; no git mutation; leaf seat, no subagents.

Protocol mirrors r73/r74: 4 transports {file, stdin_pipe, redirected_fd,
fifo_path}; fifo arm = mkfifo + one-shot writer that lingers
FIFO_HOLD_S; every leg bounded by ARM_TIMEOUT_S via SIGKILL; writerless
fifo cells probe SIGTERM immunity explicitly.
"""
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FIFO_HOLD_S = 1.0
ARM_TIMEOUT_S = 15.0
NOWRITER_WAIT_S = 3.0
TERM_PROBE_WAIT_S = 1.0

MEMBERS = {
    "posttable_nomatch": "corpus/live/round-68/posttable_nomatch.wav",
    "txw_piperefuse": "corpus/live/round-68/txw_piperefuse.wav",
    "dec_act": "corpus/live/round-66/pair_dec_act.wav",
    "dec_hcom": "corpus/live/round-66/pair_dec_hcom.wav",
    "extsuffix_wav": "corpus/live/round-69/extsuffix_nomatch.wav",
    "extsuffix_bin": "corpus/live/round-69/extsuffix_nomatch.bin",
    "extsuffix_txw": "corpus/live/round-69/extsuffix_nomatch.txw",
    "extsuffix_f32": "corpus/live/round-69/extsuffix_nomatch.f32",
    "extsuffix_snd": "corpus/live/round-69/extsuffix_nomatch.snd",
}
LAVF74_MEMBERS = {
    "lavf_iss": "corpus/live/round-74/lavf_iss.iss",
    "lavf_iss_multi": "corpus/live/round-74/lavf_iss_multi.iss",
    "lavf_apc": "corpus/live/round-74/lavf_apc.apc",
    "lavf_acm": "corpus/live/round-74/lavf_acm.acm",
    "lavf_adx": "corpus/live/round-74/lavf_adx.adx",
    "lavf_aifc": "corpus/live/round-74/lavf_aifc.aifc",
}
TRANSPORTS = ("file", "stdin_pipe", "redirected_fd", "fifo_path")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_bounded(argv, env=None, stdin=None, input_bytes=None, timeout=ARM_TIMEOUT_S):
    """One leg -> (rc, wall_s, stderr_text, blocked_flag). SIGKILL on timeout
    (subprocess.run timeout-kill) — the only signal a fifo-blocked opener
    honors; wall recorded either way."""
    t0 = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=timeout,
                              env=env, stdin=stdin, input=input_bytes)
        return (proc.returncode, round(time.monotonic() - t0, 3),
                proc.stderr.decode(errors="replace"), None)
    except subprocess.TimeoutExpired as exc:
        return (None, round(time.monotonic() - t0, 3),
                (exc.stderr or b"").decode(errors="replace"),
                f"blocked: no verdict within {timeout} s (SIGKILL)")


def fifo_feed(fifo, data, hold_s):
    try:
        with open(fifo, "wb") as fh:
            fh.write(data)
            fh.flush()
            time.sleep(hold_s)
    except (BrokenPipeError, OSError):
        pass


def fifo_leg(argv, path, data, env=None):
    """Named-fifo leg: one-shot writer lingers FIFO_HOLD_S after the write."""
    with tempfile.TemporaryDirectory(prefix="r75critic-fifo-") as tmp:
        fifo = Path(tmp) / path.name
        os.mkfifo(fifo)
        writer = threading.Thread(target=fifo_feed, args=(fifo, data, FIFO_HOLD_S),
                                  daemon=True)
        writer.start()
        try:
            rc, wall, err, blocked = run_bounded(argv + [str(fifo)], env=env)
        finally:
            writer.join(timeout=FIFO_HOLD_S + 5)
    return rc, wall, err, blocked, path.name


def tail(text, n=200):
    lines = [ln for ln in (text or "").strip().splitlines() if ln.strip()]
    return lines[-1][-n:] if lines else None


# ---------------------------------------------------------------- paplay

def paplay_argv(transport, path):
    # paplay has NO `-` stdin convention (measured: literal filename -> ENOENT);
    # the anonymous arms are the no-FILE-argument form.
    if transport == "file":
        return ["paplay", str(path)]
    if transport in ("stdin_pipe", "redirected_fd"):
        return ["paplay"]
    raise ValueError(transport)


def paplay_fields(text):
    t = text or ""
    return {
        "sndfile_fail": "Failed to open audio file." in t,
        "connection_failure": bool(re.search(r"[Cc]onnection failure|Connection refused|Host is down", t)),
        "enoent": "No such file or directory" in t,
        "stream_spec": (re.search(r"sample specification '([^']+)'", t).group(1)
                        if re.search(r"sample specification '([^']+)'", t) else None),
    }


def paplay_leg(transport, path, data, env=None):
    if transport == "file":
        rc, wall, err, blocked = run_bounded(["paplay", str(path)], env=env)
        label = str(path.relative_to(ROOT))
    elif transport == "stdin_pipe":
        rc, wall, err, blocked = run_bounded(["paplay"], env=env, input_bytes=data)
        label = "-"
    elif transport == "redirected_fd":
        with path.open("rb") as fh:
            rc, wall, err, blocked = run_bounded(["paplay"], env=env, stdin=fh)
        label = "-"
    else:
        rc, wall, err, blocked, label = fifo_leg(["paplay"], path, data, env=env)
    fields = paplay_fields(err)
    leg = {"input": label, "exit_code": rc, "wall_s": wall, **fields,
           "error": blocked or (tail(err) if rc not in (0, None) else None)}
    if rc not in (0, None):
        leg["stderr_tail"] = tail(err)
    return leg


# ---------------------------------------------------------------- ffplay

FFPLAY_BASE = ["ffplay", "-hide_banner", "-autoexit", "-nodisp", "-loglevel", "info"]
FFPLAY_ENV = {**os.environ, "SDL_AUDIODRIVER": "dummy"}


def ffplay_fields(text):
    t = text or ""
    det = re.search(r"Input #0, ([^,]+),", t)
    aud = re.search(r"Stream #\d+:\d+: Audio: ([^,]+),", t)
    return {
        "detected": det.group(1) if det else None,
        "audio_codec": aud.group(1) if aud else None,
        "eperm": "Operation not permitted" in t,
        "seek_mention": bool(re.search(r"[Ss]eek", t)),
        "invalid_data": "Invalid data found" in t,
        "no_streams": "could not find codec parameters" in t or "Output file #0 does not contain" in t,
    }


def ffplay_leg(transport, path, data):
    if transport == "file":
        rc, wall, err, blocked = run_bounded(FFPLAY_BASE + [str(path)], env=FFPLAY_ENV)
        label = str(path.relative_to(ROOT))
    elif transport == "stdin_pipe":
        rc, wall, err, blocked = run_bounded(FFPLAY_BASE + ["-"], env=FFPLAY_ENV,
                                             input_bytes=data)
        label = "-"
    elif transport == "redirected_fd":
        with path.open("rb") as fh:
            rc, wall, err, blocked = run_bounded(FFPLAY_BASE + ["-"], env=FFPLAY_ENV,
                                                 stdin=fh)
        label = "-"
    else:
        rc, wall, err, blocked, label = fifo_leg(FFPLAY_BASE + ["-"], path, data)
    fields = ffplay_fields(err)
    leg = {"input": label, "exit_code": rc, "wall_s": wall, **fields,
           "error": blocked or (tail(err) if rc not in (0, None) else None)}
    return leg


# ---------------------------------------------------------------- aplay

def aplay_leg(device, transport, path, data, extra=(), env=None):
    argv = ["aplay", "-D", device] + list(extra)
    try:
        label0 = str(path.relative_to(ROOT))
    except ValueError:
        label0 = str(path)
    if transport == "file":
        rc, wall, err, blocked = run_bounded(argv + [str(path)], env=env)
        label = label0
    elif transport == "stdin_pipe":
        rc, wall, err, blocked = run_bounded(argv + ["-"], env=env, input_bytes=data)
        label = "-"
    elif transport == "redirected_fd":
        with path.open("rb") as fh:
            rc, wall, err, blocked = run_bounded(argv + ["-"], env=env, stdin=fh)
        label = "-"
    else:
        rc, wall, err, blocked, label = fifo_leg(argv, path, data, env=env)
    t = err or ""
    leg = {"device": device, "input": label, "exit_code": rc, "wall_s": wall,
           "not_wave": "not a WAVE file" in t,
           "channels_unavailable": "Channels count non available" in t,
           "device_busy": "Device or resource busy" in t,
           "underrun": "underrun" in t.lower(),
           "error": blocked or (tail(err) if rc not in (0, None) else None)}
    return leg


# ---------------------------------------------------------------- writerless fifo

def writerless_fifo_cell(consumer):
    """fifo with NO writer: block + SIGTERM immunity + killpg SIGKILL."""
    with tempfile.TemporaryDirectory(prefix="r75critic-nowriter-") as tmp:
        fifo = Path(tmp) / "nowriter.wav"
        os.mkfifo(fifo)
        if consumer == "paplay":
            argv = ["paplay", str(fifo)]
        elif consumer == "aplay":
            argv = ["aplay", "-D", "plughw:0,0", str(fifo)]
        else:
            argv = FFPLAY_BASE + [str(fifo)]
        proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, start_new_session=True,
                                env=FFPLAY_ENV if consumer == "ffplay" else None)
        time.sleep(NOWRITER_WAIT_S)
        blocked = proc.poll() is None
        wchan = None
        try:
            wchan = Path(f"/proc/{proc.pid}/wchan").read_text().strip()
        except OSError:
            pass
        sigterm_immune = None
        if blocked:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            time.sleep(TERM_PROBE_WAIT_S)
            sigterm_immune = proc.poll() is None
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        return {"blocked": blocked, "waited_s": NOWRITER_WAIT_S, "wchan": wchan,
                "sigterm_immune": sigterm_immune,
                "exit_code": proc.returncode}


def main():
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    run_dir = OUT / f"{stamp}-critic-probes"
    run_dir.mkdir(parents=True, exist_ok=True)

    def save(receipt):
        (run_dir / "receipt.json").write_text(json.dumps(receipt, indent=1) + "\n")

    receipt = {
        "probe": "r75-critic pre-land counterexample probes",
        "seat": "audio-critic r75", "host": os.uname().nodename,
        "timestamp_utc": stamp,
        "protocol": {"fifo_hold_s": FIFO_HOLD_S, "arm_timeout_s": ARM_TIMEOUT_S,
                     "fifo_kill": "SIGKILL (subprocess timeout)",
                     "ffplay_env": "SDL_AUDIODRIVER=dummy"},
        "member_sha256": {k: sha256(ROOT / v) for k, v in {**MEMBERS, **LAVF74_MEMBERS}.items()},
        "cells": {},
    }
    data_cache = {k: (ROOT / v).read_bytes() for k, v in {**MEMBERS, **LAVF74_MEMBERS}.items()}

    # -- A. paplay: canonical 9 x 4 transports --------------------------
    a = {}
    for m, rel in MEMBERS.items():
        path = ROOT / rel
        a[m] = {t: paplay_leg(t, path, data_cache[m]) for t in TRANSPORTS}
    receipt["cells"]["paplay_transport"] = a
    save(receipt)

    # -- B. paplay name axis: identical bytes under 3 names + anonymous --
    snd_bytes = data_cache["extsuffix_snd"]
    name_axis = {"named_file": {}, "named_fifo": {}, "anonymous": {}}
    for name in ("snd", "wav", "bin"):
        p = ROOT / f"corpus/live/round-69/extsuffix_nomatch.{name}"
        name_axis["named_file"][f"axis.{name}"] = paplay_leg("file", p, snd_bytes)
    for name in ("snd", "wav", "bin"):
        p = ROOT / f"corpus/live/round-69/extsuffix_nomatch.{name}"
        rc, wall, err, blocked, label = fifo_leg(["paplay"], p, snd_bytes)
        name_axis["named_fifo"][f"axis.{name}"] = {
            "input": label, "exit_code": rc, "wall_s": wall,
            "error": blocked or tail(err), "stderr_tail": tail(err)}
    p = ROOT / "corpus/live/round-69/extsuffix_nomatch.snd"
    name_axis["anonymous"]["rfd"] = paplay_leg("redirected_fd", p, snd_bytes)
    name_axis["anonymous"]["stdin_pipe"] = paplay_leg("stdin_pipe", p, snd_bytes)
    # protocol control: valid wav through the anonymous arm proves the
    # no-arg stdin path is a real libsndfile read, not raw-mode noise.
    ui = ROOT / "corpus/artifacts/ui.wav"
    name_axis["protocol_control_valid_wav_stdin"] = paplay_leg(
        "stdin_pipe", ui, ui.read_bytes())
    receipt["cells"]["paplay_name_axis"] = name_axis
    save(receipt)

    # -- C. paplay daemon gates -----------------------------------------
    ui = ROOT / "corpus/artifacts/ui.wav"
    gates = {}
    with tempfile.TemporaryDirectory(prefix="r75critic-gate-") as tmp:
        empty = Path(tmp)
        gates["baseline_live"] = paplay_leg("file", ui, b"")
        env = {**os.environ, "PULSE_SERVER": f"unix:{empty}/nope.sock"}
        gates["gate_pulse_server"] = paplay_leg("file", ui, b"", env=env)
        env = {**os.environ, "PIPEWIRE_RUNTIME_DIR": str(empty)}
        gates["gate_pipewire_runtime_dir"] = paplay_leg("file", ui, b"", env=env)
        env = {**os.environ, "XDG_RUNTIME_DIR": str(empty)}
        gates["gate_xdg_runtime_dir"] = paplay_leg("file", ui, b"", env=env)
    receipt["cells"]["paplay_gates"] = gates
    save(receipt)

    # -- D. ffplay: canonical 9 x 4 + r74 lavf members x 4 --------------
    f = {}
    for m, rel in MEMBERS.items():
        path = ROOT / rel
        f[m] = {t: ffplay_leg(t, path, data_cache[m]) for t in TRANSPORTS}
    for m, rel in LAVF74_MEMBERS.items():
        path = ROOT / rel
        f[m] = {t: ffplay_leg(t, path, data_cache[m]) for t in TRANSPORTS}
    receipt["cells"]["ffplay_transport"] = f
    save(receipt)

    # -- E. ffplay debug log surface on dec_hcom (file + fifo) ----------
    debug = {}
    p = ROOT / "corpus/live/round-66/pair_dec_hcom.wav"
    dbg_base = ["ffplay", "-hide_banner", "-autoexit", "-nodisp",
                "-loglevel", "debug"]
    rc, wall, err, blocked = run_bounded(dbg_base + [str(p)], env=FFPLAY_ENV)
    debug["file"] = {"exit_code": rc, "wall_s": wall,
                     "seek_lines": [ln for ln in err.splitlines()
                                    if re.search(r"seek|Seek|Operation not permitted", ln)][:12],
                     "stderr_tail": tail(err, 300)}
    rc, wall, err, blocked, label = fifo_leg(dbg_base + ["-"], p, data_cache["dec_hcom"])
    debug["fifo_path"] = {"exit_code": rc, "wall_s": wall,
                          "seek_lines": [ln for ln in err.splitlines()
                                         if re.search(r"seek|Seek|Operation not permitted", ln)][:12],
                          "stderr_tail": tail(err, 300)}
    receipt["cells"]["ffplay_debug_dec_hcom"] = debug
    save(receipt)

    # -- F. aplay device census + routes --------------------------------
    ap = {}
    rc, wall, err, _ = run_bounded(["aplay", "-l"], timeout=10)
    ap["device_census"] = {"exit_code": rc, "stdout_head":
                           (subprocess.run(["aplay", "-l"], capture_output=True,
                                           timeout=10).stdout.decode(errors="replace")
                            .strip().splitlines()[:8])}
    ui = ROOT / "corpus/artifacts/ui.wav"
    ui_data = ui.read_bytes()
    routes = {}
    for dev in ("null", "default", "plughw:0,0", "hw:0,0", "sysdefault"):
        routes[dev] = aplay_leg(dev, "file", ui, ui_data)
    ap["routes_ui_wav"] = routes
    with tempfile.TemporaryDirectory(prefix="r75critic-agate-") as tmp:
        env = {**os.environ, "XDG_RUNTIME_DIR": tmp, "PIPEWIRE_RUNTIME_DIR": tmp}
        ap["gate_default_under_empty_xdg"] = aplay_leg("default", "file", ui, ui_data, env=env)
        ap["gate_plughw_under_empty_xdg"] = aplay_leg("plughw:0,0", "file", ui, ui_data, env=env)
    # stereo control for the hw device channel constraint
    stereo = Path(tempfile.mkdtemp(prefix="r75critic-stereo-")) / "stereo.wav"
    gen = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                          "sine=frequency=440:sample_rate=48000:duration=0.25",
                          "-ac", "2", "-c:a", "pcm_s16le", "-y", str(stereo)],
                         check=False, capture_output=True)
    ap["stereo_gen"] = {"exit_code": gen.returncode,
                        "exists": stereo.exists(),
                        "stderr_tail": gen.stderr.decode(errors="replace")[-200:]}
    if stereo.exists():
        ap["hw_0_0_stereo_control"] = aplay_leg("hw:0,0", "file", stereo,
                                                stereo.read_bytes())
    ap["hw_0_0_mono_file"] = aplay_leg("hw:0,0", "file", ui, ui_data)
    # transport matrix on the one valid-wav member, both device classes
    dec = ROOT / "corpus/live/round-66/pair_dec_act.wav"
    dec_data = data_cache["dec_act"]
    ap["transport_plughw_dec_act"] = {t: aplay_leg("plughw:0,0", t, dec, dec_data)
                                      for t in TRANSPORTS}
    ap["transport_null_dec_act"] = {t: aplay_leg("null", t, dec, dec_data)
                                    for t in TRANSPORTS}
    # non-WAV: no autodetect at all -> name axis cannot exist
    snd = ROOT / "corpus/live/round-69/extsuffix_nomatch.snd"
    ap["nonwav_no_raw_null"] = aplay_leg("null", "file", snd, snd_bytes)
    ap["nonwav_raw_null"] = aplay_leg(
        "null", "file", snd, snd_bytes,
        extra=["-t", "raw", "--format", "S16_LE", "--rate", "48000", "--channels", "1"])
    receipt["cells"]["aplay"] = ap
    save(receipt)

    # -- G. writerless fifo: TERM immunity per consumer -----------------
    receipt["cells"]["writerless_fifo"] = {
        c: writerless_fifo_cell(c) for c in ("paplay", "aplay", "ffplay")}

    save(receipt)
    print(f"receipt -> {run_dir / 'receipt.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
