#!/usr/bin/env python3
"""R77 scout — FRONTIER 2 + 7: hot-plug / stream-move / provider-kill.

Reversible, module-scoped: a probe-owned null sink is created and destroyed,
so the host's real device graph is never mutated. The capture under test is
always aimed at the probe sink's monitor; the "hot-plug" event is the
module unload (the provider of the captured node vanishes mid-stream).
"""
import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r77_probe import (LINE, M_SPDIF, emit, errclass, inspect, mk,  # noqa
                       norm_err, out_kind, sh)

TMP = mk()
PROBE_SINK = "r77_scout_probe_sink"
PROBE_MON = PROBE_SINK + ".monitor"


def load_null():
    rc, so, se, _w, _t = sh(["pactl", "load-module", "module-null-sink",
                             f"sink_name={PROBE_SINK}",
                             "sink_properties=device.description=r77probe"])
    mid = so.decode(errors="replace").strip()
    return (int(mid) if mid.isdigit() else None), se.strip()


def unload(mid):
    if mid:
        return sh(["pactl", "unload-module", str(mid)])[0]
    return None


def probe_case(label, argv, out, event, wait=1.5, sig=signal.SIGTERM):
    """Start capture; fire `event()` mid-run; then sever."""
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    time.sleep(wait)
    early = proc.poll()
    ev = event() if event else None
    time.sleep(0.7)
    alive = proc.poll() is None
    if alive:
        proc.send_signal(sig)
        try:
            proc.wait(timeout=6)
        except subprocess.TimeoutExpired:
            proc.send_signal(signal.SIGKILL)
            proc.wait(timeout=6)
    err = proc.stderr.read().decode(errors="replace")
    proc.stderr.close()
    insp = inspect(out)
    return {"leg": label,
            "argv": [a if a != out else "<out>" for a in argv],
            "event": ev, "alive_after_event": alive,
            "rc": proc.returncode, "early_exit_rc": early,
            "err_class": errclass(err)[0], "err_tail": norm_err(err),
            "out_kind": out_kind(insp), "bytes": insp.get("bytes"),
            "data_actual": insp.get("data_actual"),
            "riff_size_field": insp.get("riff_size_field"),
            "data_declared_field": insp.get("data_declared_field"),
            "fmt": insp.get("fmt")}


def main():
    out = {"probe": "hotplug-r77", "tmp": TMP, "legs": {}, "modules": {}}
    mid, lerr = load_null()
    out["modules"]["load"] = {"module_id": mid, "stderr": lerr}
    if not mid:
        emit(out, "probe-hotplug-r77.json")
        print("null sink load failed")
        return

    try:
        # 1. provider vanishes mid-capture (module unload)
        cases = [
            ("pwrecord_mon_unload",
             ["pw-record", "-P", "stream.capture.sink=true", "--target",
              PROBE_SINK, os.path.join(TMP, "hp_pwr.wav")],
             os.path.join(TMP, "hp_pwr.wav")),
            ("parec_mon_unload",
             ["parec", "-d", PROBE_MON, "--file-format=wav",
              os.path.join(TMP, "hp_parec.wav")],
             os.path.join(TMP, "hp_parec.wav")),
            ("ffmpeg_mon_unload",
             ["ffmpeg", "-nostdin", "-nostats", "-v", "error", "-f", "pulse",
              "-i", PROBE_MON, "-y", os.path.join(TMP, "hp_ff.wav")],
             os.path.join(TMP, "hp_ff.wav")),
        ]
        # 1a: first pass WITHOUT the unload — baseline for the same shape
        for label, argv, path in cases:
            if os.path.exists(path):
                os.unlink(path)
            out["legs"]["baseline_" + label] = probe_case(
                "baseline_" + label, argv, path, None)
        # 1b: with the unload
        for label, argv, path in cases:
            if os.path.exists(path):
                os.unlink(path)
            out["legs"][label] = probe_case(
                label, argv, path, lambda: unload(mid))
            mid, lerr = load_null()          # restore for the next leg
            out["modules"][f"reload_for_{label}"] = mid

        # 2. default-source change mid-run (resolved-at-open vs follows)
        rc, so, _se, _w, _t = sh(["pactl", "get-default-source"])
        orig = so.decode().strip()
        MIC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Mic__source"
        p = os.path.join(TMP, "hp_defsrc.wav")
        out["legs"]["parec_default_source_move"] = probe_case(
            "parec_default_source_move",
            ["parec", "-d", "@DEFAULT_SOURCE@", "--file-format=wav", p], p,
            lambda: sh(["pactl", "set-default-source", MIC])[0])
        sh(["pactl", "set-default-source", orig])
        out["default_source_restored"] = orig

        # 3. suspend the source mid-capture
        p = os.path.join(TMP, "hp_susp.wav")
        out["legs"]["parec_suspend_source"] = probe_case(
            "parec_suspend_source",
            ["parec", "-d", LINE, "--file-format=wav", p], p,
            lambda: sh(["pactl", "suspend-source", LINE, "1"])[0])
        sh(["pactl", "suspend-source", LINE, "0"])

        # 4. mute the source mid-capture
        p = os.path.join(TMP, "hp_mute.wav")
        out["legs"]["parec_mute_source"] = probe_case(
            "parec_mute_source",
            ["parec", "-d", LINE, "--file-format=wav", p], p,
            lambda: sh(["pactl", "set-source-mute", LINE, "1"])[0])
        sh(["pactl", "set-source-mute", LINE, "0"])

        # 5. move a live capture stream to another source
        p = os.path.join(TMP, "hp_move.wav")
        proc = subprocess.Popen(["parec", "-d", LINE, "--file-format=wav", p],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.PIPE)
        time.sleep(1.2)
        rc, so, _se, _w, _t = sh(["pactl", "list", "source-outputs", "short"])
        idxs = [ln.split("\t")[0] for ln in
                so.decode(errors="replace").splitlines() if ln.strip()]
        mv = sh(["pactl", "move-source-output", idxs[-1], MIC]) if idxs \
            else (None, b"", "no source-outputs", 0, False)
        time.sleep(0.5)
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=6)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=6)
        err = proc.stderr.read().decode(errors="replace")
        proc.stderr.close()
        insp = inspect(p)
        out["legs"]["parec_move_source_output"] = {
            "leg": "parec_move_source_output", "source_output_idx": idxs,
            "move_rc": mv[0], "move_stderr": mv[2].strip()[:160],
            "rc": proc.returncode, "out_kind": out_kind(insp),
            "bytes": insp.get("bytes"), "err_tail": norm_err(err)}
    finally:
        unload(mid)
        sh(["pactl", "list", "modules", "short"])   # settle before exit

    emit(out, "probe-hotplug-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
