"""r77 BOUNDARY probe 1 — fallback-law edges (prop / target / move / multi-prop).

Tone anchor is the witness: this host's real sources are digital silence, so a
capture that carries the injected 1 kHz tone consumed the node whose sink the
tone was played into; a silent capture consumed some other node.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import (  # noqa: E402
    HDMI_SINK,
    LINE_SRC,
    SEAT,
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
N = 96000  # 2 s at 48 k


def leg(tag, target=None, props=None, tone_sink=SPDIF_SINK, n=N, out=None, play=True,
        extra=None, timeout=14.0, note=None):
    """One bounded capture leg with the tone anchor."""
    out = out or (SCRATCH / f"{tag}.wav")
    cmd = ["pw-record"]
    for p in props or []:
        cmd += ["-P", p]
    if target is not None:
        cmd += ["--target", target]
    cmd += ["-n", str(n), str(out)]
    p = spawn(cmd)
    time.sleep(0.4)
    pl = None
    if play:
        pl = spawn(["pw-cat", "-p", "--target", tone_sink, str(TONE)])
    r = reap(p, timeout=timeout)
    if pl:
        reap(pl, timeout=6)
    insp = inspect_wav(out)
    return {
        "tag": tag,
        "cmd": " ".join(cmd),
        "note": note,
        "rc": r["rc"],
        "killed_by_us": r["killed_by_us"],
        "err": r["err"].strip()[:300],
        "bytes": insp.get("bytes"),
        "riff": insp.get("riff_size_field"),
        "data_declared": insp.get("data_declared_field"),
        "peak": insp.get("peak"),
        "nz": insp.get("nonzero_frac"),
        "fft_hz": insp.get("fft_peak_hz"),
        "tone": bool((insp.get("peak") or 0) > 2000 and (insp.get("nonzero_frac") or 0) > 0.3),
        "out": str(out),
    }


def sig(tag, target, props, note="", **kw):
    """Adaptive 2-leg signature: which node did the capture actually consume?"""
    a = leg(f"{tag}__toneSPDIF", target, props, tone_sink=SPDIF_SINK, **kw)
    b = None
    if not a["tone"]:
        b = leg(f"{tag}__toneSPK", target, props, tone_sink=SPEAKER_SINK, **kw)
    if a["tone"]:
        consumed = "default/SPDIF monitor"
    elif b and b["tone"]:
        consumed = "SPEAKER monitor"
    else:
        consumed = "neither (silent node)"
    return {
        "tag": tag,
        "target": target,
        "props": props,
        "note": note,
        "consumed": consumed,
        "a": a,
        "b": b,
    }


def main():
    wipe_scratch()
    make_tone()
    rec = {"probe": "r77-boundary/p1-fallback-law", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rec["inventory"] = {
        "default_sink": sh(["pactl", "get-default-sink"])["out"].strip(),
        "default_source": sh(["pactl", "get-default-source"])["out"].strip(),
    }

    # --- controls -----------------------------------------------------------
    rec["controls"] = [
        sig("ctl_default_sink", SPDIF_SINK, PROP, "expect: honored"),
        sig("ctl_default_monitor", SPDIF_SINK + ".monitor", PROP, "expect: honored"),
        sig("ctl_other_sink", SPEAKER_SINK, PROP, "expect: honored"),
    ]

    # --- EDGE 1: monitor-node names of NON-default sinks under the prop -----
    rec["edge_monitor_names"] = [
        sig("edge_speaker_monitor", SPEAKER_SINK + ".monitor", PROP, "scout's gap"),
        sig("edge_hdmi_monitor", HDMI_SINK + ".monitor", PROP, "scout's gap"),
        sig("edge_spdif_monitor_bare", SPDIF_SINK + ".monitor", PROP, "control"),
        sig("edge_monitor_dup", SPEAKER_SINK + ".monitor.monitor", PROP, "double suffix"),
        sig("edge_sink_dot_nothing", SPEAKER_SINK + ".", PROP, "trailing dot"),
        sig("edge_partial_name", SPEAKER_SINK[: len(SPEAKER_SINK) - 5], PROP, "truncated real name"),
    ]

    # --- EDGE 2: no prop, monitor node name --------------------------------
    rec["no_prop_monitor"] = [
        leg("noprop_speaker_monitor", SPEAKER_SINK + ".monitor", None, tone_sink=SPEAKER_SINK,
            note="r76 says only a real SOURCE node resolves without the prop"),
        leg("noprop_spdif_monitor", SPDIF_SINK + ".monitor", None, tone_sink=SPDIF_SINK),
    ]

    # --- EDGE 3: does the FALLBACK follow a MOVED default sink? ------------
    moved = {}
    try:
        mv1 = sh(["pactl", "set-default-sink", SPEAKER_SINK])
        moved["set_default_speaker_rc"] = mv1["rc"]
        moved["default_now"] = sh(["pactl", "get-default-sink"])["out"].strip()
        moved["legs"] = [
            sig("moved_garbage", "no_such_node_xyz", PROP, "does the fallback move with the default?"),
            sig("moved_default_monitor_alias", "@DEFAULT_MONITOR@", PROP, "alias after the move"),
            sig("moved_speaker_named", SPEAKER_SINK, PROP, "control: named sink still honored"),
            sig("moved_spdif_named", SPDIF_SINK, PROP, "control: other named sink honored"),
            sig("moved_auto_no_target", None, PROP, "auto with prop after the move"),
        ]
    finally:
        back = sh(["pactl", "set-default-sink", SPDIF_SINK])
        moved["restore_rc"] = back["rc"]
        moved["default_restored"] = sh(["pactl", "get-default-sink"])["out"].strip()
    rec["moved_default"] = moved

    # --- EDGE 4: multiple / alternative -P props ---------------------------
    rec["multi_prop"] = [
        sig("prop_node_target", None, ["node.target=" + SPEAKER_SINK, "stream.capture.sink=true"],
            "prop-based target instead of --target"),
        sig("prop_node_target_spdif", None, ["node.target=" + SPDIF_SINK, "stream.capture.sink=true"],
            "prop-based target = default sink"),
        sig("prop_target_object", None, ["stream.capture.sink=true", "target.object=" + SPEAKER_SINK],
            "the prop pw-dump advertises"),
        sig("prop_dup_last_false", None, ["stream.capture.sink=true", "stream.capture.sink=false"],
            "duplicate key: last wins?"),
        sig("prop_dup_last_true", None, ["stream.capture.sink=false", "stream.capture.sink=true"],
            "duplicate key: last wins? (reversed)"),
        sig("prop_only_capture_sink", None, PROP, "auto target under the prop"),
        sig("prop_capture_sink_0", None, ["stream.capture.sink=0"], "numeric false"),
        sig("prop_capture_sink_caps", None, ["stream.capture.sink=TRUE"], "caps true"),
        sig("prop_capture_sink_garbage", None, ["stream.capture.sink=yes_please"], "non-bool value"),
        sig("prop_bogus", None, ["r77b.bogus=1", "stream.capture.sink=true"], "unknown prop alongside"),
    ]

    save_receipt("probe-p1-fallback-law.json", rec)
    # compact console summary
    for group in ("controls", "edge_monitor_names", "moved_default", "multi_prop"):
        v = rec.get(group)
        if isinstance(v, list):
            for row in v:
                print(f"{group:20s} {row['tag']:28s} rc={row['a']['rc']:>3} bytes={row['a']['bytes']:>7} "
                      f"peak={row['a']['peak']:>7} consumed={row['consumed']}")
        elif isinstance(v, dict) and "legs" in v:
            for row in v["legs"]:
                print(f"{group:20s} {row['tag']:28s} rc={row['a']['rc']:>3} bytes={row['a']['bytes']:>7} "
                      f"peak={row['a']['peak']:>7} consumed={row['consumed']}")
    for row in rec["no_prop_monitor"]:
        print(f"{'no_prop_monitor':20s} {row['tag']:28s} rc={row['rc']:>3} bytes={row['bytes']:>7} "
              f"peak={row['peak']:>7} tone={row['tone']} err={row['err'][:60]}")


if __name__ == "__main__":
    main()
