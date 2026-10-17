"""r77 BOUNDARY probe 1b — the MOVED-DEFAULT law, corrected.

p1's moved-default block is VOID: `pactl set-default-sink` returned rc=0 and
`pactl get-default-sink` still answered SPDIF, so the default never moved. This
probe (a) establishes which mechanism can actually move the default, (b) then
re-measures the fallback with a VERIFIED move, and (c) re-measures the monitor
node-name edges with BOTH tone placements (a one-sided verdict cannot separate
"honored" from "fell back to the node the tone was in").
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import (  # noqa: E402
    HDMI_SINK,
    SCRATCH,
    SPDIF_SINK,
    SPEAKER_SINK,
    TONE,
    inspect_wav,
    make_tone,
    reap,
    save_receipt,
    sh,
    spawn,
    wipe_scratch,
)

PROP = ["-P", "stream.capture.sink=true"]
N = 96000


def quiet_window():
    out = sh(["bash", "-lc",
              "ps -eo pid,etimes,cmd | grep -E 'pw-cat|parec|ffmpeg|arecord|measure_audio' | grep -v grep | head -12"],
             timeout=10)
    return {"concurrent_audio_clients": out["out"].strip().splitlines(), "n": len(out["out"].strip().splitlines())}


def leg(tag, target=None, props=None, tone_sink=SPDIF_SINK, n=N, timeout=14.0):
    out = SCRATCH / f"p1b_{tag}.wav"
    cmd = ["pw-record"]
    for p in props or []:
        cmd += ["-P", p]
    if target is not None:
        cmd += ["--target", target]
    cmd += ["-n", str(n), str(out)]
    p = spawn(cmd)
    time.sleep(0.35)
    pl = spawn(["pw-cat", "-p", "--target", tone_sink, str(TONE)])
    r = reap(p, timeout=timeout)
    reap(pl, timeout=6)
    insp = inspect_wav(out)
    peak, nz, fft = insp.get("peak") or 0, insp.get("nonzero_frac") or 0, insp.get("fft_peak_hz")
    tone = bool(peak > 2000 and nz > 0.3 and fft is not None and abs(fft - 1000) <= 25)
    return {
        "tag": tag, "cmd": " ".join(cmd), "rc": r["rc"], "err": r["err"].strip()[:200],
        "bytes": insp.get("bytes"), "riff": insp.get("riff_size_field"), "data": insp.get("data_declared_field"),
        "peak": peak, "nz": round(nz, 4), "fft_hz": fft, "tone": tone,
        "level_inflated_vs_clean_tone": bool(peak > 16384 * 1.05),
    }


def sig2(tag, target, props, note=""):
    """Both tone placements, always. (SPDIF?, SPEAKER?) -> which node was consumed."""
    a = leg(f"{tag}__SPDIF", target, props, tone_sink=SPDIF_SINK)
    b = leg(f"{tag}__SPK", target, props, tone_sink=SPEAKER_SINK)
    if a["tone"] and not b["tone"]:
        consumed = "default/SPDIF monitor"
    elif b["tone"] and not a["tone"]:
        consumed = "SPEAKER monitor"
    elif a["tone"] and b["tone"]:
        consumed = "BOTH (impossible unless both sinks were mixed)"
    else:
        consumed = "neither (silent / unlinked)"
    return {"tag": tag, "target": target, "props": props, "note": note,
            "signature": [a["tone"], b["tone"]], "consumed": consumed, "a": a, "b": b}


def default_probe():
    md = sh(["pw-metadata", "-n", "default"], timeout=10, cap=4096)
    return {
        "pactl_get": sh(["pactl", "get-default-sink"], timeout=10)["out"].strip(),
        "pw_metadata_default": md["out"].strip()[:600],
        "rc": md["rc"],
    }


def main():
    wipe_scratch()
    make_tone()
    rec = {"probe": "r77-boundary/p1b-moved-default", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rec["quiet_at_start"] = quiet_window()

    # ---- 1. which mechanism can move the default sink? --------------------
    m = {}
    m["before"] = default_probe()
    s1 = sh(["pactl", "set-default-sink", SPEAKER_SINK], timeout=10)
    time.sleep(0.4)
    m["after_pactl_set"] = default_probe()
    m["pactl_set_rc"] = s1["rc"]
    m["pactl_set_err"] = s1["err"].strip()[:200]
    # sample for 2 s: does something revert it?
    samples = []
    for _ in range(5):
        samples.append(sh(["pactl", "get-default-sink"], timeout=6)["out"].strip())
        time.sleep(0.4)
    m["get_samples_after_pactl_set"] = samples
    m["pactl_set_effective"] = any(s == SPEAKER_SINK for s in samples)

    # authoritative metadata write
    meta_write = sh(["pw-metadata", "-n", "default", "0", "default.audio.sink",
                     json.dumps({"name": SPEAKER_SINK})], timeout=10)
    time.sleep(0.4)
    m["after_pw_metadata_write"] = default_probe()
    m["pw_metadata_write_rc"] = meta_write["rc"]
    m["pw_metadata_write_out"] = (meta_write["out"] + meta_write["err"]).strip()[:300]
    samples2 = []
    for _ in range(5):
        samples2.append(sh(["pactl", "get-default-sink"], timeout=6)["out"].strip())
        time.sleep(0.4)
    m["get_samples_after_pw_metadata"] = samples2
    m["pw_metadata_effective"] = any(s == SPEAKER_SINK for s in samples2)
    rec["default_move_mechanism"] = m

    default_moved = m["pw_metadata_effective"] or m["pactl_set_effective"]

    # ---- 2. fallback under a VERIFIED moved default -----------------------
    if default_moved:
        rec["moved_legs"] = [
            sig2("moved_garbage", "no_such_node_xyz", PROP, "fallback under a moved default"),
            sig2("moved_alias", "@DEFAULT_MONITOR@", PROP, "alias under a moved default"),
            sig2("moved_auto", None, PROP, "auto+prop under a moved default"),
            sig2("moved_speaker_named", SPEAKER_SINK, PROP, "explicit new-default sink"),
            sig2("moved_spdif_named", SPDIF_SINK, PROP, "explicit old-default sink"),
        ]
    else:
        rec["moved_legs"] = "BLOCKED: default sink could not be moved by pactl or pw-metadata"

    # ---- 3. restore -------------------------------------------------------
    r1 = sh(["pw-metadata", "-n", "default", "0", "default.audio.sink", json.dumps({"name": SPDIF_SINK})],
            timeout=10)
    time.sleep(0.3)
    rec["restore"] = {"rc": r1["rc"], "now": sh(["pactl", "get-default-sink"], timeout=10)["out"].strip()}

    # ---- 4. monitor node-name edges, both placements ----------------------
    rec["monitor_name_edges"] = [
        sig2("edge_speaker_monitor", SPEAKER_SINK + ".monitor", PROP, "non-default monitor name"),
        sig2("edge_hdmi_monitor", HDMI_SINK + ".monitor", PROP, "non-default monitor name"),
        sig2("edge_spdif_monitor", SPDIF_SINK + ".monitor", PROP, "default monitor name"),
        sig2("edge_partial_name", SPEAKER_SINK[:-5], PROP, "truncated real name"),
        sig2("edge_speaker_bare", SPEAKER_SINK, PROP, "bare non-default sink name (control)"),
    ]
    rec["quiet_at_end"] = quiet_window()

    save_receipt("probe-p1b-moved-default.json", rec)
    print("quiet start:", rec["quiet_at_start"]["n"], rec["quiet_at_start"]["concurrent_audio_clients"])
    print("move mechanism:", json.dumps({k: v for k, v in rec["default_move_mechanism"].items()
                                         if k not in ("before", "after_pactl_set", "after_pw_metadata_write")}))
    print("  before:", json.dumps(rec["default_move_mechanism"]["before"])[:200])
    print("  after_pactl:", json.dumps(rec["default_move_mechanism"]["after_pactl_set"])[:200])
    print("  after_meta:", json.dumps(rec["default_move_mechanism"]["after_pw_metadata_write"])[:200])
    print("restore:", rec["restore"])
    if isinstance(rec["moved_legs"], list):
        for L in rec["moved_legs"]:
            print(f"MOVED {L['tag']:26s} sig={L['signature']} consumed={L['consumed']} "
                  f"peak_a={L['a']['peak']} peak_b={L['b']['peak']} fft_a={L['a']['fft_hz']} fft_b={L['b']['fft_hz']}")
    else:
        print("moved legs:", rec["moved_legs"])
    for L in rec["monitor_name_edges"]:
        print(f"EDGE  {L['tag']:26s} sig={L['signature']} consumed={L['consumed']} "
              f"peak_a={L['a']['peak']} peak_b={L['b']['peak']} fft_a={L['a']['fft_hz']} fft_b={L['b']['fft_hz']} "
              f"bytes_a={L['a']['bytes']} bytes_b={L['b']['bytes']} err_a={L['a']['err'][:40]!r}")
    print("quiet end:", rec["quiet_at_end"]["n"])


if __name__ == "__main__":
    main()
