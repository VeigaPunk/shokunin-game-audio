"""r77 BOUNDARY probe 7/8 — the two rows my earlier passes left unmeasured.

7. A FINALIZED wav past 4 GiB on the pw-record/libsndfile side. p4b showed the
   file grows past 4 GiB (5.24 GiB) with no error and no rename, but that leg
   was killed, so its header was the unfinalized placeholder. Here the capture
   ends on its own `-n` bound, so the FINALIZED header past 4 GiB is readable.
8. The arecord split/rotation counter at -99 -> -100, reached via `-m 1`
   (wall-clock driven: a free-running `-D null` leg wrote 130 s of audio in
   3 ms and never rotated), with a truncate watchdog so the tmpfs footprint
   stays bounded.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import SCRATCH, SPDIF_SINK, reap, save_receipt, sh, spawn, wipe_scratch  # noqa: E402

FOUR_GIB = 2**32


class Mon(threading.Thread):
    def __init__(self, path, stop_evt, interval=0.25, cap_bytes=6.0e9, min_free=3.0e9, truncate_others=False):
        super().__init__(daemon=True)
        self.path, self.stop, self.interval = path, stop_evt, interval
        self.cap, self.min_free, self.samples, self.tripped = cap_bytes, min_free, [], None
        self.truncate_others = truncate_others
        self.files_fn = None

    def run(self):
        t0 = time.monotonic()
        while not self.stop.is_set():
            try:
                sz = self.path.stat().st_size if self.path.exists() else None
            except OSError:
                sz = None
            free = shutil.disk_usage("/dev/shm").free
            self.samples.append((round(time.monotonic() - t0, 2), sz, round(free / 1e9, 2)))
            if self.truncate_others and self.files_fn:
                fs = sorted(self.files_fn(), key=lambda f: f.stat().st_mtime, reverse=True)
                for f in fs[1:]:
                    try:
                        f.truncate(0)
                    except OSError:
                        pass
            if sz and sz > self.cap:
                self.tripped = "cap_bytes"
                self.stop.set()
            if free < self.min_free:
                self.tripped = "min_free"
                self.stop.set()
            self.stop.wait(self.interval)


def phase7_finalized_4gib():
    rec = {"free_gb_before": round(shutil.disk_usage("/dev/shm").free / 1e9, 2)}
    if rec["free_gb_before"] < 8.0:
        rec["skipped"] = "tmpfs too full"
        return rec
    out = SCRATCH / "finalized_big.wav"
    frames = 9_000_000  # x 64ch x f64 = 4.61 GB of payload
    cmd = ["pw-record", "-P", "stream.capture.sink=true", "--target", SPDIF_SINK, "--rate", "768000",
           "--channels", "64", "--format", "f64", "-n", str(frames), str(out)]
    stop = threading.Event()
    mon = Mon(out, stop, cap_bytes=6.0e9)
    mon.start()
    p = spawn(cmd)
    t0 = time.monotonic()
    while not stop.is_set() and time.monotonic() - t0 < 110:
        time.sleep(0.25)
        if p.poll() is not None:
            break
    ended_alone = p.poll() is not None
    if not ended_alone:
        p.send_signal(9)
    r = reap(p, timeout=10)
    stop.set()
    mon.join(timeout=3)
    size = out.stat().st_size if out.exists() else None
    rec.update({
        "cmd": " ".join(cmd), "requested_frames": frames, "ended_on_its_own": ended_alone, "rc": r["rc"],
        "err": r["err"].strip()[:300], "wall_s": round(time.monotonic() - t0, 2), "monitor_tripped": mon.tripped,
        "final_bytes": size, "over_4gib_by": (size - FOUR_GIB) if size else None,
        "size_samples_tail": mon.samples[-4:], "free_gb_after": round(shutil.disk_usage("/dev/shm").free / 1e9, 2),
    })
    if out.exists() and size and size > 64:
        with open(out, "rb") as fh:
            head = fh.read(96)
        rec["header_hex_96"] = head.hex()
        rec["riff_magic"] = head[:4].decode("latin1")
        rec["riff_size_field"] = int.from_bytes(head[4:8], "little")
        rec["riff_size_field_hex"] = head[4:8].hex()
        rec["form_type"] = head[8:12].decode("latin1")
        # walk the chunk list in the header region only
        pos, chunks = 12, []
        while pos + 8 <= len(head) and len(chunks) < 8:
            cid = head[pos : pos + 4].decode("latin1")
            csz = int.from_bytes(head[pos + 4 : pos + 8], "little")
            chunks.append((cid, csz))
            if cid == "data":
                break
            pos += 8 + csz + (csz & 1)
        rec["chunks"] = chunks
    out.unlink(missing_ok=True)
    rec["free_gb_after_cleanup"] = round(shutil.disk_usage("/dev/shm").free / 1e9, 2)
    return rec


def phase8_rot100():
    d = SCRATCH / "rot100"
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*"):
        f.unlink()
    rec = {"free_gb_before": round(shutil.disk_usage("/dev/shm").free / 1e9, 2),
           "cmd": "timeout 118 arecord -D null -f S16_LE -c 1 -r 8000 -t wav -m 1 rot100.wav"}
    if rec["free_gb_before"] < 8.0:
        rec["skipped"] = "tmpfs too full"
        return rec
    target = d / "rot100.wav"
    stop = threading.Event()
    mon = Mon(target, stop, interval=0.03, cap_bytes=1e18, min_free=4.0e9, truncate_others=True)
    mon.files_fn = lambda: list(d.glob("*"))
    mon.start()
    p = spawn(["timeout", "118", "arecord", "-D", "null", "-f", "S16_LE", "-c", "1", "-r", "8000",
               "-t", "wav", "-m", "1", str(target)])
    t0 = time.monotonic()
    while time.monotonic() - t0 < 122:
        time.sleep(0.5)
        if p.poll() is not None:
            break
    ended = p.poll() is not None
    if not ended:
        p.send_signal(9)
    r = reap(p, timeout=10)
    stop.set()
    mon.join(timeout=3)
    files = sorted(d.glob("*"), key=lambda f: f.name)
    nums = []
    for f in files:
        m = re.search(r"-(\d+)\.wav$", f.name)
        if m:
            nums.append(int(m.group(1)))
    rec.update({
        "ended_on_its_own": ended, "rc": r["rc"], "err": r["err"].strip()[:300],
        "wall_s": round(time.monotonic() - t0, 2), "count": len(files),
        "base_name_exists": target.exists(),
        "max_counter": max(nums) if nums else None,
        "names_head": [f.name for f in files[:4]], "names_tail": [f.name for f in files[-4:]],
        "reached_99": 99 in nums, "reached_100": 100 in nums, "reached_101": 101 in nums,
        "reached_108": 108 in nums,
        "names_around_99_101": [f.name for f in files if re.search(r"-(9[89]|10[012])\.wav$", f.name)],
        "unique_names": len({f.name for f in files}),
        "total_bytes_now": sum(f.stat().st_size for f in files),
        "free_gb_after": round(shutil.disk_usage("/dev/shm").free / 1e9, 2),
    })
    shutil.rmtree(d, ignore_errors=True)
    rec["free_gb_after_cleanup"] = round(shutil.disk_usage("/dev/shm").free / 1e9, 2)
    return rec


def main():
    wipe_scratch()
    rec = {"probe": "r77-boundary/p7p8", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rec["concurrent_at_start"] = sh(["bash", "-lc",
                                     "ps -eo pid,etimes,cmd | grep -E 'measure_audio|pw-cat|ffmpeg' | grep -v grep | wc -l"],
                                    timeout=10)["out"].strip()
    rec["phase7_finalized_4gib"] = phase7_finalized_4gib()
    rec["phase8_rot100"] = phase8_rot100()
    save_receipt("probe-p7p8-bigwav-and-counter.json", rec)
    p7 = rec["phase7_finalized_4gib"]
    print("PHASE7:", json.dumps({k: v for k, v in p7.items() if k != "size_samples_tail"}))
    print("  samples_tail:", p7.get("size_samples_tail"))
    p8 = rec["phase8_rot100"]
    print("PHASE8:", json.dumps({k: v for k, v in p8.items() if k not in ("names_head", "names_tail")}))
    print("  names_head:", p8.get("names_head"), "names_tail:", p8.get("names_tail"))


if __name__ == "__main__":
    main()
