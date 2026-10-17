"""r77 BOUNDARY probe 9 — readers vs a FINALIZED >4 GiB wav.

p7 showed a pw-record capture ending on its own bound at 4,608,000,608 bytes with
`riff_size_field = 0xFFFFFFFF`, a `fact` chunk carrying the true frame count
(9,000,000) and a `PEAK` chunk. This probe re-creates that file and runs the
metadata readers on it BEFORE deleting it: which readers survive a legal,
self-describing, >4 GiB wav?
"""

from __future__ import annotations

import json
import shutil
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import (  # noqa: E402
    SPDIF_SINK,
    SCRATCH,
    reader_digest,
    readers,
    reap,
    save_receipt,
    sh,
    spawn,
    wipe_scratch,
)

FOUR_GIB = 2**32


def main():
    wipe_scratch()
    rec = {"probe": "r77-boundary/p9-readers-over-4gib",
           "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    free = round(shutil.disk_usage("/dev/shm").free / 1e9, 2)
    rec["free_gb_before"] = free
    if free < 8.0:
        rec["skipped"] = "tmpfs too full"
        save_receipt("probe-p9-readers-over-4gib.json", rec)
        print("SKIPPED", rec["skipped"])
        return

    out = SCRATCH / "over4gib.wav"
    frames = 9_000_000
    cmd = ["pw-record", "-P", "stream.capture.sink=true", "--target", SPDIF_SINK, "--rate", "768000",
           "--channels", "64", "--format", "f64", "-n", str(frames), str(out)]
    p = spawn(cmd)
    t0 = time.monotonic()
    while time.monotonic() - t0 < 160:
        time.sleep(0.5)
        if p.poll() is not None:
            break
    ended = p.poll() is not None
    if not ended:
        p.send_signal(9)
    r = reap(p, timeout=10)
    size = out.stat().st_size if out.exists() else None
    rec["capture"] = {"cmd": " ".join(cmd), "ended_on_its_own": ended, "rc": r["rc"],
                      "wall_s": round(time.monotonic() - t0, 2), "bytes": size,
                      "over_4gib_by": (size - FOUR_GIB) if size else None,
                      "err": r["err"].strip()[:200]}
    if not out.exists() or (size or 0) < FOUR_GIB:
        rec["abort"] = "did not reach 4 GiB"
        out.unlink(missing_ok=True)
        save_receipt("probe-p9-readers-over-4gib.json", rec)
        print(json.dumps(rec["capture"], indent=1), "ABORT", rec["abort"])
        return

    with open(out, "rb") as fh:
        head = fh.read(96)
    rec["header"] = {"hex96": head.hex(), "riff_size_field": int.from_bytes(head[4:8], "little")}

    # metadata readers only: a full decode of 9M frames x 64ch would dominate
    t0 = time.monotonic()
    rd = readers(out)
    rec["reader_wall_s"] = round(time.monotonic() - t0, 2)
    d = reader_digest(rd)
    d["soxi_s_raw"] = rd["soxi_s"]["out"].strip()
    d["soxi_D_raw"] = rd["soxi_D"]["out"].strip()
    d["soxi_s_err"] = rd["soxi_s"]["err"].strip()[:200]
    d["soxi_D_err"] = rd["soxi_D"]["err"].strip()[:200]
    d["sndfile_rc"] = rd["sndfile_info"]["rc"]
    d["sndfile_head"] = (rd["sndfile_info"]["out"] or "").strip()[:400]
    d["sndfile_err"] = (rd["sndfile_info"]["err"] or "").strip()[:200]
    d["ffprobe_rc"] = rd["ffprobe_dur"]["rc"]
    d["ffprobe_err"] = rd["ffprobe_dur"]["err"].strip()[:200]
    d["truth"] = {"frames": frames, "duration_s": round(frames / 768000.0, 4), "channels": 64, "rate": 768000}
    rec["readers"] = d

    out.unlink(missing_ok=True)
    rec["free_gb_after_cleanup"] = round(shutil.disk_usage("/dev/shm").free / 1e9, 2)
    save_receipt("probe-p9-readers-over-4gib.json", rec)
    print("capture:", json.dumps(rec["capture"]))
    print("header riff_size:", rec["header"]["riff_size_field"])
    print("readers:", json.dumps(d, indent=1))


if __name__ == "__main__":
    main()
