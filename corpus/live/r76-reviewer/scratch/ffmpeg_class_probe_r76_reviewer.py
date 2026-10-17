#!/usr/bin/env python3
"""r76 REVIEWER ffmpeg error-class derivation probe.

The r76 gate asserts (rc, class) pairs for ffmpeg legs. This probe prints
the FULL stderr of each leg so the class label can be checked against the
raw evidence rather than trusted (rc alone is never the verdict).
"""
import os
from pathlib import Path
import subprocess
import tempfile

LEGS = [
    ("pulse_default", ["ffmpeg", "-nostdin", "-nostats", "-v", "verbose",
                       "-f", "pulse", "-i", "default", "-t", "1", "-y"],
     None),
    ("alsa_default", ["ffmpeg", "-nostdin", "-nostats", "-v", "verbose",
                      "-f", "alsa", "-i", "default", "-t", "1", "-y"],
     None),
    ("pulse_dead_server", ["ffmpeg", "-nostdin", "-nostats", "-v", "verbose",
                           "-f", "pulse", "-i", "@DEFAULT_SOURCE@", "-t", "1",
                           "-y"],
     {"PULSE_SERVER": "unix:/nonexistent-r76-gate"}),
    ("pulse_monitor_alias", ["ffmpeg", "-nostdin", "-nostats", "-v",
                             "verbose", "-f", "pulse", "-i",
                             "alsa_output.usb-Generic_USB_Audio-00."
                             "HiFi__SPDIF__sink.monitor", "-t", "0.5", "-y"],
     None),
]


def main():
    with tempfile.TemporaryDirectory(prefix="r76rev-ff-") as tmp:
        for name, argv, env in LEGS:
            out = Path(tmp) / f"{name}.wav"
            e = dict(os.environ)
            if env:
                e.update(env)
            p = subprocess.run(argv + [str(out)], capture_output=True,
                               timeout=30, env=e)
            print(f"===== {name} rc={p.returncode}")
            print("stderr:")
            print(p.stderr.decode(errors="replace").strip()[:3000])
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
