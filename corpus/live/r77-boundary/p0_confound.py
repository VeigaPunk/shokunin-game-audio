"""r77 BOUNDARY probe 0 — non-invasive confound detector.

Captures each sink monitor for a bounded window WITHOUT playing anything. A
non-zero peak means some other client is feeding that sink right now (another
seat's probe), which is the confound that makes a one-sided tone verdict unsafe.
This probe never plays audio, so it cannot perturb a concurrent seat's lattice.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import (  # noqa: E402
    HDMI_SINK,
    SCRATCH,
    SPDIF_SINK,
    SPEAKER_SINK,
    inspect_wav,
    reap,
    save_receipt,
    sh,
    spawn,
    wipe_scratch,
)


def baseline(tag, sink, n=72000):
    out = SCRATCH / f"b_{tag}.wav"
    p = spawn(["pw-record", "-P", "stream.capture.sink=true", "--target", sink, "-n", str(n), str(out)])
    r = reap(p, timeout=12)
    insp = inspect_wav(out)
    return {"tag": tag, "sink": sink, "rc": r["rc"], "bytes": insp.get("bytes"),
            "peak": insp.get("peak"), "nz": round(insp.get("nonzero_frac") or 0, 5),
            "fft_hz": insp.get("fft_peak_hz"), "data": insp.get("data_declared_field"),
            "busy_other_client": bool((insp.get("peak") or 0) > 0)}


def main():
    wipe_scratch()
    rec = {"probe": "r77-boundary/p0-confound-detector",
           "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rec["ps_concurrent"] = sh(["bash", "-lc",
                               "ps -eo pid,etimes,cmd | grep -E 'measure_audio|pw-cat|ffplay|ffmpeg' | grep -v grep | head -8"],
                              timeout=10)["out"].strip().splitlines()
    rec["baselines"] = [baseline("spdif", SPDIF_SINK), baseline("speaker", SPEAKER_SINK),
                        baseline("hdmi", HDMI_SINK), baseline("spdif2", SPDIF_SINK)]
    rec["verdict"] = {
        "any_sink_busy": any(b["busy_other_client"] for b in rec["baselines"]),
        "quiet_sinks": [b["tag"] for b in rec["baselines"] if not b["busy_other_client"]],
        "busy_sinks": [b["tag"] for b in rec["baselines"] if b["busy_other_client"]],
    }
    save_receipt("probe-p0-confound.json", rec)
    for b in rec["baselines"]:
        print(f"{b['tag']:8s} {b['sink'][-28:]:28s} rc={b['rc']} peak={b['peak']} nz={b['nz']} fft={b['fft_hz']} "
              f"busy={b['busy_other_client']}")
    print("verdict:", rec["verdict"])
    print("concurrent:", rec["ps_concurrent"])


if __name__ == "__main__":
    main()
