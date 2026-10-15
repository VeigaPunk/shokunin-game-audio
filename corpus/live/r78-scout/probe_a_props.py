#!/usr/bin/env python3
"""Probe A — PipeWire stream-props lattice (beyond stream.capture.sink).

Question: which -P props actually route a capture (change the consumed node),
which are decoration (invisible in artifact AND in links), and what are the
named refusal/degenerate shapes.

Method: probe-owned null sink r78_ns carries a distinct-freq stereo tone
(L=1kHz R=1.5kHz) via pw-cat; each pw-record leg gets a UNIQUE node.name so
its pw-link ports are unambiguous next to the concurrent seat's pw-records.
Witness per leg: rc, bytes, fmt, peak/nz_frac, payload sha16, and the
pw-link -l producer set feeding this stream's input_* ports mid-run.
"""
import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78_probe import (SEAT, SCRATCH, M_NS, NS, LINE, S_SPDIF, sh,
                       load_ns, unload_ns, gen_tone, inspect, audio_stats,
                       payload_sha, out_kind, errclass, norm_err, pwlink_map,
                       mk, emit, du)

LEGS = [
    # name, extra props/flags after node.name, target
    ("baseline_sink_prop", ["-P", "stream.capture.sink=true"], NS),
    ("role_Communication", ["-P", "stream.capture.sink=true",
                            "-P", "media.role=Communication"], NS),
    ("role_Production", ["-P", "stream.capture.sink=true",
                         "-P", "media.role=Production"], NS),
    ("role_DSP", ["-P", "stream.capture.sink=true",
                  "-P", "media.role=DSP"], NS),
    ("role_Music", ["-P", "stream.capture.sink=true",
                    "-P", "media.role=Music"], NS),
    ("node_target_prop", ["-P", "stream.capture.sink=true",
                          "-P", "node.target=" + NS], None),
    ("node_target_garbage", ["-P", "stream.capture.sink=true",
                             "-P", "node.target=no_such_node_xyz"], None),
    ("targetobject_prop", ["-P", "stream.capture.sink=true",
                           "-P", "target.object=" + NS], None),
    ("flag_wins_over_prop", ["-P", "stream.capture.sink=true",
                             "-P", "target.object=no_such_node_xyz"], NS),
    ("prop_wins_over_flag", ["-P", "stream.capture.sink=true",
                             "-P", "target.object=" + NS],
     "no_such_node_xyz"),
    ("sinkfalse_target_sink", ["-P", "stream.capture.sink=false"], NS),
    ("sinkfalse_target_mon", ["-P", "stream.capture.sink=false"], M_NS),
    ("noprop_target_mon", [], M_NS),
    ("noprop_target_sink", [], NS),
    ("noprop_target_line", [], LINE),
    ("sinkfalse_garbage", ["-P", "stream.capture.sink=false"],
     "no_such_node_xyz"),
    ("prop_garbage_fallback", ["-P", "stream.capture.sink=true"],
     "no_such_node_xyz"),
    ("prop_default_alias", ["-P", "stream.capture.sink=true"],
     "@DEFAULT_MONITOR@"),
    ("sinkfalse_line", ["-P", "stream.capture.sink=false"], LINE),
    ("autoconnect_false", ["-P", "stream.capture.sink=true",
                           "-P", "node.autoconnect=false"], NS),
    ("stream_monitor_prop", ["-P", "stream.capture.sink=true",
                             "-P", "stream.monitor=true"], NS),
    ("media_class_override", ["-P", "stream.capture.sink=true",
                              "-P", "media.class=Audio/Source"], NS),
]


def run_leg(name, extra, target, tmp, tone):
    tag = "r78a_" + name[:20]
    out = os.path.join(tmp, name + ".wav")
    if os.path.exists(out):
        os.unlink(out)
    argv = ["pw-record", "-P", "node.name=" + tag] + extra + \
        (["--target", target] if target else []) + \
        ["-n", "48000", out]
    play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    time.sleep(0.35)
    t0 = time.monotonic()
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE)
    time.sleep(0.9)
    rc, so, _e, _w, _t = sh(["pw-link", "-l"], timeout=6)
    producers = pwlink_map(so.decode(errors="replace"), tag + ":input")
    deadline = t0 + 12
    prc = p.poll()
    while prc is None and time.monotonic() < deadline:
        time.sleep(0.05)
        prc = p.poll()
    if prc is None:
        p.send_signal(signal.SIGTERM)
        try:
            prc = p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.send_signal(signal.SIGKILL)
            prc = p.wait(timeout=3)
    se = p.stderr.read().decode(errors="replace")
    p.stderr.close()
    try:
        play.wait(timeout=4)
    except subprocess.TimeoutExpired:
        play.kill()
    insp = inspect(out)
    st = audio_stats(out)
    return {"leg": name, "argv": argv, "rc": prc,
            "err_class": errclass(se)[0], "err_line": norm_err(se),
            "out_kind": out_kind(insp), "bytes": insp.get("bytes"),
            "data_actual": insp.get("data_actual"),
            "riff_size_field": insp.get("riff_size_field"),
            "data_declared_field": insp.get("data_declared_field"),
            "fmt": insp.get("fmt"), "peak": st.get("peak"),
            "nz_frac": st.get("nz_frac"),
            "sha16": payload_sha(out) if insp.get("bytes") else None,
            "link_producers": producers}


def resample_leg(name, extra, tmp, tone):
    """Resample axis: --rate 44100 on a 48k source; compare payload sha."""
    return run_leg(name, extra + ["--rate", "44100"], NS, tmp, tone)


def main():
    tmp = mk()
    tone = gen_tone(os.path.join(tmp, "tone.wav"))
    idx, note = load_ns()
    res = {"ns_module": idx, "ns_note": note, "legs": [], "resample": []}
    if idx is None:
        emit(res, "probe-props-lattice-r78.json")
        print("NULL SINK FAILED", note, file=sys.stderr)
        return
    try:
        for name, extra, target in LEGS:
            leg = run_leg(name, extra, target, tmp, tone)
            res["legs"].append(leg)
            print(f"{name}: rc={leg['rc']} bytes={leg['bytes']} "
                  f"peak={leg['peak']} prod={leg['link_producers']}",
                  file=sys.stderr)
        # resample axis — content-bearing so the resampler is observable
        for name, extra in (
            ("resq_default", ["-P", "stream.capture.sink=true"]),
            ("resq_flag_q0", ["-P", "stream.capture.sink=true", "-q", "0"]),
            ("resq_flag_q14", ["-P", "stream.capture.sink=true", "-q", "14"]),
            ("resq_prop_q0", ["-P", "stream.capture.sink=true",
                              "-P", "resample.quality=0"]),
            ("resq_prop_q14", ["-P", "stream.capture.sink=true",
                               "-P", "resample.quality=14"]),
            ("resq_prop_bogus", ["-P", "stream.capture.sink=true",
                                 "-P", "resample.quality=999"]),
        ):
            leg = resample_leg(name, extra, tmp, tone)
            res["resample"].append(leg)
            print(f"{name}: rc={leg['rc']} sha={leg['sha16']} "
                  f"peak={leg['peak']}", file=sys.stderr)
    finally:
        unload_ns(idx)
    res["scratch_bytes"] = du()
    emit(res, "probe-props-lattice-r78.json")


if __name__ == "__main__":
    main()
