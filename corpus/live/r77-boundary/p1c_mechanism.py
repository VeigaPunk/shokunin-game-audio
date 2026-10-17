"""r77 BOUNDARY probe 1c — the MECHANISM behind the fallback law.

Hypothesis: in PipeWire a monitor is not a node, so a native pw client resolving
`--target <sink>.monitor` matches no node and falls back to the default sink's
monitor, while a bare sink node name IS matched. Prediction that falsifies it:
with the default sink moved to SPEAKER, `--target <SPDIF>.monitor` must land on
the SPEAKER monitor (fallback), not on SPDIF.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import (  # noqa: E402
    SPDIF_SINK,
    SPEAKER_SINK,
    TONE,
    SCRATCH,
    inspect_wav,
    make_tone,
    reap,
    save_receipt,
    sh,
    spawn,
    wipe_scratch,
)

PROP = ["-P", "stream.capture.sink=true"]


def leg(tag, target, tone_sink, n=96000):
    out = SCRATCH / f"p1c_{tag}.wav"
    cmd = ["pw-record"] + PROP + (["--target", target] if target else []) + ["-n", str(n), str(out)]
    p = spawn(cmd)
    time.sleep(0.35)
    pl = spawn(["pw-cat", "-p", "--target", tone_sink, str(TONE)])
    r = reap(p, timeout=14)
    reap(pl, timeout=6)
    insp = inspect_wav(out)
    peak, nz, fft = insp.get("peak") or 0, insp.get("nonzero_frac") or 0, insp.get("fft_peak_hz")
    return {"tag": tag, "cmd": " ".join(cmd), "rc": r["rc"], "bytes": insp.get("bytes"),
            "peak": peak, "nz": round(nz, 4), "fft_hz": fft,
            "tone": bool(peak > 2000 and nz > 0.3 and fft and abs(fft - 1000) <= 25)}


def sig2(tag, target):
    a = leg(f"{tag}__SPDIF", target, SPDIF_SINK)
    b = leg(f"{tag}__SPK", target, SPEAKER_SINK)
    consumed = ("default/SPDIF monitor" if a["tone"] and not b["tone"] else
                "SPEAKER monitor" if b["tone"] and not a["tone"] else
                "BOTH" if a["tone"] and b["tone"] else "neither")
    return {"tag": tag, "target": target, "signature": [a["tone"], b["tone"]],
            "consumed": consumed, "a": a, "b": b}


def set_default(name):
    return sh(["pw-metadata", "-n", "default", "0", "default.audio.sink", json.dumps({"name": name})],
              timeout=10)


def get_default():
    return sh(["pactl", "get-default-sink"], timeout=10)["out"].strip()


def main():
    wipe_scratch()
    make_tone()
    rec = {"probe": "r77-boundary/p1c-mechanism", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    # A. is there any node whose node.name carries ".monitor"?
    d = sh(["bash", "-lc", "pw-dump"], timeout=25, cap=4_000_000)
    try:
        nodes = json.loads(d["out"])
        names = [(o.get("info", {}).get("props", {}) or {}).get("node.name",
                 (o.get("info", {}).get("props", {}) or {}).get("node.description"))
                 for o in nodes if str(o.get("type", "")).endswith("Node")]
        classes = [(o.get("info", {}).get("props", {}) or {}).get("media.class")
                   for o in nodes if str(o.get("type", "")).endswith("Node")]
        rec["node_inventory"] = {
            "total_nodes": len(names),
            "names": [n for n in names if n][:24],
            "monitor_named_nodes": [n for n in names if n and ".monitor" in n],
            "sink_nodes": [n for n, c in zip(names, classes) if c == "Audio/Sink"],
            "source_nodes": [n for n, c in zip(names, classes) if c == "Audio/Source"],
        }
    except Exception as exc:  # noqa: BLE001
        rec["node_inventory"] = {"error": f"{type(exc).__name__}: {exc}"[:200]}

    # B. pactl set-default-sink is a no-op — reproduce, with the metadata value
    b = {"before": {"get": get_default(), "meta": sh(["pw-metadata", "-n", "default"], timeout=10)["out"].strip()[:300]}}
    sh(["pactl", "set-default-sink", SPEAKER_SINK], timeout=10)
    time.sleep(0.5)
    b["after_pactl_set"] = {"get": get_default(),
                            "meta": sh(["pw-metadata", "-n", "default"], timeout=10)["out"].strip()[:300]}
    b["pactl_noop"] = b["after_pactl_set"]["get"] != SPEAKER_SINK
    rec["pactl_set_default_noop"] = b

    try:
        # C. with the default genuinely moved: the falsifying 2x2
        set_default(SPEAKER_SINK)
        time.sleep(0.5)
        rec["default_after_move"] = get_default()
        rec["moved_matrix"] = [
            sig2("moved_spdif_bare", SPDIF_SINK),
            sig2("moved_spdif_monitor_name", SPDIF_SINK + ".monitor"),
            sig2("moved_speaker_bare", SPEAKER_SINK),
            sig2("moved_garbage", "no_such_node_xyz"),
        ]
    finally:
        set_default(SPDIF_SINK)
        time.sleep(0.4)
        rec["restored"] = get_default()

    save_receipt("probe-p1c-mechanism.json", rec)
    print("node inventory:", json.dumps({k: v for k, v in rec["node_inventory"].items() if k != "names"}))
    print("  names:", rec["node_inventory"].get("names"))
    print("pactl set-default-sink no-op:", rec["pactl_set_default_noop"]["pactl_noop"])
    print("  before get:", rec["pactl_set_default_noop"]["before"]["get"])
    print("  after  get:", rec["pactl_set_default_noop"]["after_pactl_set"]["get"])
    print("default after pw-metadata move:", rec["default_after_move"], "-> restored:", rec["restored"])
    for L in rec["moved_matrix"]:
        print(f"{L['tag']:28s} target={str(L['target'])[-26:]:26s} sig={L['signature']} consumed={L['consumed']} "
              f"peak_a={L['a']['peak']} peak_b={L['b']['peak']} fft_a={L['a']['fft_hz']} fft_b={L['b']['fft_hz']}")


if __name__ == "__main__":
    main()
