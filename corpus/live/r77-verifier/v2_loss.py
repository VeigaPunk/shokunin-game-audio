#!/usr/bin/env python3
"""r77 verifier — independent re-derivation of `sustained_after_target_loss`
(claim 2): a verifier-owned null sink (own name, own module id) is captured,
then destroyed mid-run; the bounded leg must keep rc / exact frames /
finalized header, and the artifact must be byte-identical to the FALLBACK
node's own same-bound control.

The wall-clock leg RELOADS the sink first, so it measures a real loss
transition — unlike the arm's own wall leg, whose sink is already gone (the
bounded leg unloaded it), so its first sample already shows the fallback.

Byte discipline: `-n 96000` frames = 384044 B per bounded leg (3 legs) plus
one unbounded leg severed at 3 s (~577 KB). All < 16 MB.
"""
import hashlib
import importlib.util
import json
import signal
import subprocess
import tempfile
import time
from pathlib import Path

_here = Path(__file__).with_name("v1_lattice.py")
_spec = importlib.util.spec_from_file_location("v1", _here)
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)

OUT = v1.OUT
SINK = "r77v_loss_sink"
FRAMES = 96000
BOUND_BYTES = 44 + FRAMES * 4          # 384044
NOMINAL_BPS = 192000
UNLOAD_AFTER_S = 0.6
WALL_UNLOAD_S = 1.0
WALL_SEVER_S = 3.0


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def load_sink():
    p = subprocess.run(["pactl", "load-module", "module-null-sink",
                        f"sink_name={SINK}"], capture_output=True, text=True,
                       timeout=20)
    out = p.stdout.strip()
    return int(out) if p.returncode == 0 and out.isdigit() else None


def unload(mid):
    if mid is None:
        return {"skipped": "no module id"}
    p = subprocess.run(["pactl", "unload-module", str(mid)],
                       capture_output=True, text=True, timeout=15)
    return {"module_id": mid, "exit_code": p.returncode,
            "stderr": p.stderr.strip()[:120]}


def nodes_now(before):
    """Consumed node(s) attributable to THIS client: the `pw-link -l`
    producers present now but not in the pre-spawn snapshot (a foreign
    client's steady link cancels)."""
    during = v1.link_map()
    merged = {p: sorted(set(during.get(p, [])) - set(before.get(p, [])))
              for p in set(before) | set(during)}
    return v1.consumed(merged)


def run(argv, out, mid=None, unload_after_s=None, sever_after_s=None,
        samples_at=()):
    rec = {"argv": " ".join(argv[:-1]) + " <out>", "samples": []}
    before = v1.link_map()
    proc = subprocess.Popen(argv + [str(out)], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    t0 = time.monotonic()
    events = sorted([(s, kind) for s, kind in ((unload_after_s, "unload"),
                                               (sever_after_s, "sever"))
                     if s is not None])
    ei, sample_times, si = 0, sorted(samples_at), 0
    while proc.poll() is None:
        t = time.monotonic() - t0
        if ei < len(events) and t >= events[ei][0]:
            kind = events[ei][1]
            if kind == "unload":
                rec["unload"] = unload(mid)
            else:
                proc.send_signal(signal.SIGTERM)
            ei += 1
        if si < len(sample_times) and t >= sample_times[si]:
            size = out.stat().st_size if out.exists() else 0
            rec["samples"].append({"t": round(t, 2), "bytes": size,
                                   "nodes": nodes_now(before)})
            si += 1
        if t > 30:
            import os
            os.killpg(proc.pid, signal.SIGKILL)
            break
        time.sleep(0.02)
    proc.wait()
    rec["wall_s"] = round(time.monotonic() - t0, 2)
    rec["exit_code"] = proc.returncode
    rec["stderr"] = proc.stderr.read().decode(errors="replace").strip()[:200]
    rec["file"] = v1.pcm(out)
    rec["sha16"] = sha(out)
    return rec


def rates(samples):
    out = []
    for a, b in zip(samples, samples[1:]):
        dt = b["t"] - a["t"]
        if dt > 0:
            out.append({"from_s": a["t"], "to_s": b["t"],
                        "pct_of_nominal": round(
                            (b["bytes"] - a["bytes"]) / dt / NOMINAL_BPS * 100)})
    return out


def main():
    sink = v1.default_sink()
    entry = {"probe": "r77-verifier independent target-loss re-link",
             "own_sink_name": SINK, "fallback_node": sink,
             "bound_bytes": BOUND_BYTES, "failures": []}
    base_argv = ["pw-record", "-P", "stream.capture.sink=true",
                 "--target", SINK, "-n", str(FRAMES), "--rate", "48000",
                 "--channels", "2", "--format", "s16"]
    mid1 = load_sink()
    entry["sink_load_1"] = mid1
    if mid1 is None:
        entry["blocked"] = "could not load the verifier's own null sink"
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "v2_loss.json").write_text(json.dumps(entry, indent=2) + "\n")
        print(json.dumps({"receipt": str(OUT / "v2_loss.json"),
                          "failures": entry["failures"]}))
        return
    mid2 = None
    try:
        with tempfile.TemporaryDirectory(prefix="r77v-loss-") as tmp:
            b = Path(tmp) / "baseline.wav"
            c = Path(tmp) / "fallback_control.wav"
            l = Path(tmp) / "after_loss.wav"
            w = Path(tmp) / "wall.wav"
            entry["baseline"] = run(base_argv, b, samples_at=(0.3, 0.9))
            entry["fallback_control"] = run(
                ["pw-record", "-P", "stream.capture.sink=true",
                 "--target", sink, "-n", str(FRAMES), "--rate", "48000",
                 "--channels", "2", "--format", "s16"], c,
                samples_at=(0.3, 0.9))
            entry["after_loss"] = run(base_argv, l, mid=mid1,
                                      unload_after_s=UNLOAD_AFTER_S,
                                      samples_at=(0.3, 0.9, 1.6))
            entry["sink_gone_after_bounded"] = SINK not in v1.sink_names()
            # a REAL transition for the wall leg: reload the sink first
            mid2 = load_sink()
            entry["sink_load_2"] = mid2
            entry["wall_clock"] = run(
                ["pw-record", "-P", "stream.capture.sink=true",
                 "--target", SINK, "--rate", "48000", "--channels", "2",
                 "--format", "s16"], w, mid=mid2,
                unload_after_s=WALL_UNLOAD_S, sever_after_s=WALL_SEVER_S,
                samples_at=(0.4, 1.2, 1.8, 2.8))
            entry["wall_clock"]["rates"] = rates(
                entry["wall_clock"]["samples"])
    finally:
        entry["unload_1"] = unload(mid1)
        entry["unload_2"] = unload(mid2)
    entry["sink_gone"] = SINK not in v1.sink_names()
    f = entry["failures"]
    for key in ("baseline", "fallback_control", "after_loss"):
        leg = entry[key]
        if leg["exit_code"] != 1 or leg["file"].get("bytes") != BOUND_BYTES \
                or leg["file"].get("data_declared") != FRAMES * 4:
            f.append(f"{key}: expected rc=1 / {BOUND_BYTES} B / declared "
                     f"{FRAMES * 4}, got rc={leg['exit_code']} "
                     f"bytes={leg['file'].get('bytes')} "
                     f"declared={leg['file'].get('data_declared')}")
    before = [s for s in entry["baseline"]["samples"] if s["t"] < 0.6]
    after = [s for s in entry["after_loss"]["samples"] if s["t"] > 0.9]
    entry["nodes_before"] = before[-1]["nodes"] if before else None
    entry["nodes_after"] = after[0]["nodes"] if after else None
    if entry["nodes_before"] != [SINK]:
        f.append(f"pre-unload consumption expected [{SINK}], got "
                 f"{entry['nodes_before']}")
    if entry["nodes_after"] != [sink]:
        f.append(f"post-unload consumption expected [{sink}] (the fallback), "
                 f"got {entry['nodes_after']}")
    entry["sha_match_control"] = (entry["fallback_control"]["sha16"] ==
                                  entry["after_loss"]["sha16"])
    entry["sha_match_dead_sink"] = (entry["baseline"]["sha16"] ==
                                    entry["after_loss"]["sha16"])
    if not entry["sha_match_control"]:
        f.append("the post-loss artifact is NOT byte-identical to the "
                 "fallback node's own same-bound control")
    if not entry["sink_gone"]:
        f.append("the verifier's null sink survived its unload — the leg "
                 "measured nothing")
    # the wall leg's real transition
    wl = entry["wall_clock"]
    first = next((s for s in wl["samples"] if s["t"] < WALL_UNLOAD_S), None)
    later = [s for s in wl["samples"] if s["t"] > WALL_UNLOAD_S]
    if first is None or first["nodes"] != [SINK]:
        f.append(f"wall leg: expected consumption of [{SINK}] before the "
                 f"unload, got {first and first['nodes']}")
    for s in later:
        if s["nodes"] != [sink]:
            f.append(f"wall leg at t={s['t']}: expected the fallback "
                     f"[{sink}], got {s['nodes']}")
    if wl["exit_code"] != 1 or wl["file"].get("data_declared") != \
            wl["file"].get("samples") * 2:
        f.append(f"wall leg: expected a finalized rc=1 capture, got "
                 f"rc={wl['exit_code']} declared="
                 f"{wl['file'].get('data_declared')} "
                 f"samples={wl['file'].get('samples')}")
    for r in wl["rates"]:
        if r["pct_of_nominal"] < 90:
            f.append(f"wall leg rate {r['from_s']}-{r['to_s']}s = "
                     f"{r['pct_of_nominal']}% of nominal — not sustained")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "v2_loss.json").write_text(json.dumps(entry, indent=2) + "\n")
    print(json.dumps({"receipt": str(OUT / "v2_loss.json"),
                      "failures": entry["failures"]}))


if __name__ == "__main__":
    main()
