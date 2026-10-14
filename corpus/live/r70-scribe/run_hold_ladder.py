#!/usr/bin/env python3
"""r70-scribe hold ladder — pin fifo_writer_hold_s as a MEASURED bound.

Re-runs (independently) the r70 declared ladder on the dec_act member
(corpus/live/round-66/pair_dec_act.wav — the arm that needs the ffmpeg
bridge's second open): fifo writer hold {0, 0.05, 0.2, 0.5, 1.0, 2.0}s x
feed {oneshot, chunked, wait-close} x N reps, own driver.

Verdict parsing reuses the LANDED module's transport_error + detection/
samples regexes (import by path — no copy, no edit). The leg runner is my
own: Popen in a new session so a blocked ffmpeg bridge child (open #2 on a
writerless fifo blocks forever) is killed by process GROUP on timeout, not
just the sox parent — the one defect-class risk of the landed runner.

Feeds:
  oneshot : open(fifo,"wb"); write(data); flush(); sleep(hold); close()
            (== landed TRANSPORT_R67 feed when hold==1.0)
  chunked : open; for each 64B chunk { write; flush; sleep(5ms) };
            sleep(hold); close()   — feed granularity variant
  waitclose : open; write(data); flush(); block until sox exits; close()
            — the claim's "correctly blocking writer" (h*=0 semantics:
            writer is attached whenever open #2 could possibly fire)

Output: runs/hold-ladder-<stamp>.json {meta, cells:[{hold,feed,reps:[{…}]}]}
"""
import hashlib
import importlib.util
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
MEMBER = ROOT / "corpus" / "live" / "round-66" / "pair_dec_act.wav"
OUTDIR = ROOT / "corpus" / "live" / "r70-scribe" / "runs"
ARM_TIMEOUT_S = 10.0          # == TRANSPORT_R67_ARM_TIMEOUT_S
CHUNK_BYTES = 64
CHUNK_GAP_S = 0.005

# verdict parsing identical to the landed module (imported, not copied)
spec = importlib.util.spec_from_file_location(
    "measure_audio", ROOT / "corpus" / "fixtures" / "measure_audio.py")
ma = importlib.util.module_from_spec(spec)
sys.modules["measure_audio"] = ma
spec.loader.exec_module(ma)
transport_error = ma.transport_error

HOLDS = (0.0, 0.05, 0.2, 0.5, 1.0, 2.0)
REPS = 15
REPS_H0 = 25          # race-rate resolution where it is cheapest


def leg(args, label, data=None, stdin=None):
    """Own leg runner: same verdict fields as transport_leg, but the child
    runs in its own session so a blocked ffmpeg bridge (open #2 on a
    writerless fifo) dies by process-GROUP kill at timeout."""
    kw = {"input": data} if data is not None else \
         ({"stdin": stdin} if stdin else {})
    t0 = time.monotonic()
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True, **kw)
    blocked = False
    try:
        _, err = proc.communicate(timeout=ARM_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        blocked = True
        os.killpg(proc.pid, signal.SIGKILL)
        _, err = proc.communicate()
    dt = time.monotonic() - t0
    text = err.decode(errors="replace")
    detected = re.search(r"detected file format type `(\S+?)'", text)
    read = re.search(r"Samples read:\s*(\d+)", text)
    return {"input": label,
            "sox_detected_format": detected.group(1) if detected else None,
            "sox_route": ("ffmpeg" if (detected and detected.group(1) == "act")
                          or "(ffmpeg)" in text else "native" if detected else "none"),
            "exit_code": None if blocked else proc.returncode,
            "samples_read": int(read.group(1)) if read else None,
            "error": (f"blocked: no verdict within {ARM_TIMEOUT_S} s"
                      if blocked else transport_error(text)),
            "wall_s": round(dt, 3)}


def fifo_arm(path, hold_s, feed):
    """One fifo_path leg under a parameterized writer protocol."""
    result = {}
    with tempfile.TemporaryDirectory(prefix="holdladder-r70-") as tmp:
        fifo = Path(tmp) / path.name
        os.mkfifo(fifo)
        release = threading.Event()   # waitclose feed: main releases on leg end

        def feed_oneshot():
            try:
                with fifo.open("wb") as fh:
                    fh.write(data)
                    fh.flush()
                    time.sleep(hold_s)
            except OSError:
                pass

        def feed_chunked():
            try:
                with fifo.open("wb") as fh:
                    for i in range(0, len(data), CHUNK_BYTES):
                        fh.write(data[i:i + CHUNK_BYTES])
                        fh.flush()
                        time.sleep(CHUNK_GAP_S)
                    time.sleep(hold_s)
            except OSError:
                pass

        def feed_waitclose():
            try:
                with fifo.open("wb") as fh:
                    fh.write(data)
                    fh.flush()
                    release.wait(timeout=ARM_TIMEOUT_S + 30)
            except OSError:
                pass

        data = path.read_bytes()
        writer = threading.Thread(
            target={"oneshot": feed_oneshot, "chunked": feed_chunked,
                    "waitclose": feed_waitclose}[feed], daemon=True)
        writer.start()
        try:
            result = leg(["sox", "-V6", str(fifo), "-n", "stat"], path.name)
        finally:
            release.set()
            writer.join(timeout=hold_s + 40)
    result["named"] = True
    result["seekable"] = False
    return result


def main():
    feeds = sys.argv[1].split(",") if len(sys.argv) > 1 else ["oneshot"]
    holds = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 \
        else list(HOLDS)
    reps = int(sys.argv[3]) if len(sys.argv) > 3 else REPS
    reps_h0 = int(sys.argv[4]) if len(sys.argv) > 4 else REPS_H0
    cells = []
    for feed in feeds:
        for hold in holds:
            n = reps_h0 if hold == 0.0 else reps
            cell = {"fifo_feed": feed, "fifo_writer_hold_s": hold,
                    "reps_planned": n, "reps": []}
            for i in range(n):
                r = fifo_arm(MEMBER, hold, feed)
                r["rep"] = i
                cell["reps"].append(r)
                print(f"{feed} hold={hold:<4} rep={i:<2} -> "
                      f"exit={r['exit_code']} det={r['sox_detected_format']} "
                      f"samples={r['samples_read']} err={r['error']!r} "
                      f"wall={r['wall_s']}", flush=True)
            # verdict distribution for this cell
            dist = {}
            for r in cell["reps"]:
                sig = json.dumps([r["sox_detected_format"], r["sox_route"],
                                  r["exit_code"], r["samples_read"], r["error"]])
                dist[sig] = dist.get(sig, 0) + 1
            cell["verdict_distribution"] = [
                {"signature": json.loads(k), "count": v}
                for k, v in sorted(dist.items(), key=lambda kv: -kv[1])]
            cells.append(cell)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = OUTDIR / f"hold-ladder-{stamp}.json"
    out.write_text(json.dumps({
        "meta": {"member": str(MEMBER.relative_to(ROOT)),
                 "member_sha256": hashlib.sha256(MEMBER.read_bytes()).hexdigest(),
                 "arm_timeout_s": ARM_TIMEOUT_S,
                 "chunk_bytes": CHUNK_BYTES, "chunk_gap_s": CHUNK_GAP_S,
                 "holds": holds, "feeds": feeds, "reps": reps,
                 "reps_hold0": reps_h0, "host_time_utc": stamp},
        "hold_ladder": cells}, indent=2, allow_nan=False) + "\n")
    print("RECEIPT", out)


if __name__ == "__main__":
    main()
