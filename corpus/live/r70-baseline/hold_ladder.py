#!/usr/bin/env python3
"""r70 baseline hold-ladder: measure fifo_writer_hold_s as a DETERMINISM BOUND.

Member: dec_act (corpus/live/round-66/pair_dec_act.wav) — the transport member
whose act detection routes through the ffmpeg bridge, which re-opens the input
BY NAME (open #2). On a fifo, open #2 (O_RDONLY) blocks while no writer is
attached, so the writer's post-write linger is the only thing keeping that
open resolving deterministically to the truncated-stream verdict
("can't find Sun/NeXT/DEC identifier", exit 2) instead of racing writer exit
into a >10 s block.

Cells (each REPS reps):
  feed=oneshot, hold in {0, 0.05, 0.2, 0.5, 1.0, 2.0}  — the r67 protocol's
      post-write linger, laddered.
  feed=chunked, hold=0  — the fifo_feed variant: 10 x 60 B chunks paced
      ~0.1 s apart (~1.0 s writer-attached window delivered by the FEED,
      zero post-write linger) — the "correctly blocking/pacing writer" arm
      of the falsifiable claim.

Verdict identity is EXACTLY the ledger arm's: sox -V6 <fifo> -n stat through
measure_audio.transport_leg imported from the verified env copy, arm timeout
10 s, transport_error normalization and stderr_tail window unchanged.
Writes hold-ladder-reps.tsv (one line per rep) + hold-ladder.json (grouped
distributions) under this lane's scratch only.
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time

HERE = Path(__file__).resolve().parent
ENV_MEASURE = HERE / "measure-env" / "corpus" / "fixtures" / "measure_audio.py"
FIXTURE = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/round-66/pair_dec_act.wav")

spec = importlib.util.spec_from_file_location("env_measure_audio", ENV_MEASURE)
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)
ARM_TIMEOUT = ma.TRANSPORT_R67_ARM_TIMEOUT_S          # 10
transport_leg = ma.transport_leg

REPS = 10
DATA = FIXTURE.read_bytes()
assert len(DATA) == 600, len(DATA)

CELLS = [("oneshot", h) for h in (0.0, 0.05, 0.2, 0.5, 1.0, 2.0)] + [("chunked", 0.0)]
CHUNK_N = 10
CHUNK_PACE_S = 0.1          # 10 chunks x ~0.1 s -> ~1.0 s attached via feed


def run_rep(feed, hold, rep):
    """One fifo leg; returns the leg dict + timing/attachment facts."""
    with tempfile.TemporaryDirectory(prefix=f"holdladder-{feed}-{hold}-") as tmp:
        fifo = Path(tmp) / FIXTURE.name
        os.mkfifo(fifo)
        marks = {"opened": None, "wrote_last": None, "closed": None, "error": None}

        def writer():
            try:
                fh = fifo.open("wb")
                marks["opened"] = time.monotonic()
                if feed == "oneshot":
                    fh.write(DATA)
                    fh.flush()
                    marks["wrote_last"] = time.monotonic()
                    if hold:
                        time.sleep(hold)
                else:  # chunked: pace the feed; no post-write linger
                    step = len(DATA) // CHUNK_N
                    for i in range(0, len(DATA), step):
                        fh.write(DATA[i:i + step])
                        fh.flush()
                        time.sleep(CHUNK_PACE_S)
                    marks["wrote_last"] = time.monotonic()
                fh.close()
                marks["closed"] = time.monotonic()
            except OSError as exc:
                marks["error"] = repr(exc)

        w = threading.Thread(target=writer, daemon=True)
        t0 = time.monotonic()
        w.start()
        try:
            leg = transport_leg(["sox", "-V6", str(fifo), "-n", "stat"], FIXTURE.name)
        finally:
            w.join(timeout=ARM_TIMEOUT + 5)
        wall = time.monotonic() - t0
    leg["feed"] = feed
    leg["hold_s"] = hold
    leg["rep"] = rep
    leg["leg_wall_s"] = round(wall, 4)
    for k in ("opened", "wrote_last", "closed"):
        if marks[k] is not None:
            leg[f"writer_{k}_at_s"] = round(marks[k] - t0, 4)
    if marks["error"]:
        leg["writer_error"] = marks["error"]
    return leg


def verdict_key(leg):
    return json.dumps({"exit_code": leg["exit_code"],
                       "detected": leg["sox_detected_format"],
                       "route": leg["sox_route"],
                       "samples_read": leg["samples_read"],
                       "error": leg["error"]}, sort_keys=True)


def main():
    reps_path = HERE / "hold-ladder-reps.tsv"
    groups = {}
    with reps_path.open("w") as fh:
        fh.write("feed\thold_s\trep\texit_code\tdetected\troute\tsamples\terror\tleg_wall_s\twriter_closed_at_s\n")
        for feed, hold in CELLS:
            for rep in range(REPS):
                leg = run_rep(feed, hold, rep)
                key = f"{feed}|{hold}"
                groups.setdefault(key, []).append(leg)
                fh.write("\t".join([
                    feed, str(hold), str(rep), str(leg["exit_code"]),
                    str(leg["sox_detected_format"]), str(leg["sox_route"]),
                    str(leg["samples_read"]), str(leg["error"]),
                    str(leg["leg_wall_s"]), str(leg.get("writer_closed_at_s"))]) + "\n")
                fh.flush()
                print(f"{feed} h={hold} rep={rep}: exit={leg['exit_code']} "
                      f"err={leg['error']} wall={leg['leg_wall_s']}s",
                      flush=True)
    out = {
        "member": "dec_act",
        "fixture": str(FIXTURE),
        "fixture_bytes": len(DATA),
        "arm_timeout_s": ARM_TIMEOUT,
        "reps_per_cell": REPS,
        "chunked_feed": {"chunks": CHUNK_N, "chunk_bytes": len(DATA) // CHUNK_N,
                         "pace_s": CHUNK_PACE_S,
                         "post_write_hold_s": 0.0},
        "hold_ladder": [],
    }
    for feed, hold in CELLS:
        legs = groups[f"{feed}|{hold}"]
        dist = {}
        for leg in legs:
            k = verdict_key(leg)
            dist[k] = dist.get(k, 0) + 1
        out["hold_ladder"].append({
            "feed": feed, "hold_s": hold, "reps": len(legs),
            "verdict_distribution": [
                {"count": c, **json.loads(k)} for k, c in
                sorted(dist.items(), key=lambda kv: -kv[1])],
            "leg_wall_s": {"min": round(min(l["leg_wall_s"] for l in legs), 3),
                           "max": round(max(l["leg_wall_s"] for l in legs), 3)},
        })
    (HERE / "hold-ladder.json").write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", reps_path, "and hold-ladder.json")


if __name__ == "__main__":
    main()
