#!/usr/bin/env python3
"""r75 reviewer ops probe #2: ffplay all-thread wchan; gate cells
(paplay pulse-severed, aplay bad device, ffplay bad SDL driver)."""
import json
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

SDL = {**os.environ, "SDL_AUDIODRIVER": "dummy"}
out = {}


def threads_wchan(pid):
    rec = {}
    try:
        for t in sorted(os.listdir(f"/proc/{pid}/task")):
            try:
                rec[t] = Path(f"/proc/{pid}/task/{t}/wchan").read_text().strip()
            except OSError:
                rec[t] = None
    except OSError:
        pass
    return rec


# --- ffplay writerless fifo, all threads ---
with tempfile.TemporaryDirectory(prefix="r75rev2-") as tmp:
    fifo = Path(tmp) / "nowriter.wav"
    os.mkfifo(fifo)
    proc = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "-hide_banner",
                             "-loglevel", "warning", str(fifo)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True, env=SDL)
    time.sleep(3.0)
    alive = proc.poll() is None
    out["ffplay_nowriter"] = {"alive_after_3s": alive,
                              "threads_wchan": threads_wchan(proc.pid) if alive else None}
    if alive:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
        out["ffplay_nowriter"]["exit_code_killpg"] = proc.returncode

# --- paplay: pulse severed ---
with tempfile.TemporaryDirectory(prefix="r75rev2-rt-") as rt:
    t0 = time.monotonic()
    p = subprocess.run(["paplay", "corpus/live/round-66/pair_dec_act.wav"],
                       capture_output=True, timeout=15,
                       env={**os.environ, "PIPEWIRE_RUNTIME_DIR": rt,
                            "PULSE_SERVER": f"unix:{rt}/pulse/native"})
    out["paplay_pulse_severed"] = {
        "exit_code": p.returncode, "wall_s": round(time.monotonic() - t0, 3),
        "stderr": p.stderr.decode(errors="replace").strip()[:200]}

# --- paplay: writerless fifo with pulse severed (gate precedence) ---
with tempfile.TemporaryDirectory(prefix="r75rev2-gate-") as tmp, \
     tempfile.TemporaryDirectory(prefix="r75rev2-rt-") as rt:
    fifo = Path(tmp) / "nowriter.wav"
    os.mkfifo(fifo)
    t0 = time.monotonic()
    try:
        p = subprocess.run(["paplay", str(fifo)], capture_output=True,
                           timeout=5,
                           env={**os.environ, "PIPEWIRE_RUNTIME_DIR": rt,
                                "PULSE_SERVER": f"unix:{rt}/pulse/native"})
        out["paplay_gate_precedence"] = {
            "exit_code": p.returncode, "wall_s": round(time.monotonic() - t0, 3),
            "stderr": p.stderr.decode(errors="replace").strip()[:200]}
    except subprocess.TimeoutExpired:
        out["paplay_gate_precedence"] = {"blocked": True,
                                         "wall_s": round(time.monotonic() - t0, 3)}

# --- aplay: bad device ---
for dev in ("hw:99", "nosuchdev"):
    t0 = time.monotonic()
    p = subprocess.run(["aplay", "-D", dev, "corpus/live/round-66/pair_dec_act.wav"],
                       capture_output=True, timeout=15)
    out[f"aplay_device_{dev}"] = {
        "exit_code": p.returncode, "wall_s": round(time.monotonic() - t0, 3),
        "stderr": p.stderr.decode(errors="replace").strip()[:200]}

# --- ffplay: bad SDL driver ---
t0 = time.monotonic()
p = subprocess.run(["ffplay", "-nodisp", "-autoexit", "-hide_banner",
                    "-loglevel", "error", "corpus/live/round-66/pair_dec_act.wav"],
                   capture_output=True, timeout=15,
                   env={**os.environ, "SDL_AUDIODRIVER": "nosuchdriver"})
out["ffplay_bad_sdl_driver"] = {
    "exit_code": p.returncode, "wall_s": round(time.monotonic() - t0, 3),
    "stderr": p.stderr.decode(errors="replace").strip()[:300]}

print(json.dumps(out, indent=1))
