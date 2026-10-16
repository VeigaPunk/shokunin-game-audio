#!/usr/bin/env python3
"""r84-critic probe B — ambient-env inheritance on the r84 plugin legs.

The r83 critic (F3) proved every r83 leg spawns with `env=None`, so the
session's `PIPEWIRE_*`/`PULSE_*` reach the clients and override pinned
flags. The committed r84 tree keeps the same spawn convention
(`_alsapw_r84_run/_spawn/_play` default `env=None`), and its
`pw_period` pin reads `node.latency == 1024/48000` (from
`PERIOD_BYTES=4096`). This probe measures, on the committed bytes:

  1. control  : clean env  -> node.latency must be 1024/48000
  2. treatment: PIPEWIRE_LATENCY=2048/48000 -> the env value wins over
     the device-string PERIOD_BYTES (the r84 pin would read FALSE RED)
  3. treatment: PIPEWIRE_PROPS='{node.name=r84c_envname}' -> the ambient
     props rename an aplay node that sets no name of its own (the
     dev_lattice gates search `alsa_playback.aplay` by name)

Seat namespace r84c_*; own sink only; unloaded + verified. No tracked
writes. TMPDIR under the lane.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SRC = Path("/home/vgpnk/Projects/shokunin/tmp/r84critic-src/corpus/fixtures")
sys.path.insert(0, str(SRC))
import measure_audio as M  # noqa: E402

PREFIX = "r84c"
NS = f"{PREFIX}_env"
OUT = Path(__file__).with_name("probeB-env-hermeticity.json")
TMP = Path(os.environ.get("TMPDIR",
                          "/home/vgpnk/Projects/shokunin/tmp"))


def modules():
    return subprocess.run(["pactl", "list", "modules", "short"],
                          capture_output=True, timeout=10
                          ).stdout.decode(errors="replace")


def load(name):
    proc = subprocess.run(
        ["pactl", "load-module", "module-null-sink", f"sink_name={name}"],
        capture_output=True, timeout=15)
    return {"rc": proc.returncode,
            "out": proc.stdout.decode(errors="replace").strip()}


def unload(name):
    idx = M._gst_r81_sink_module_index(name)
    if idx is None:
        return {"skipped": "not_listed"}
    proc = subprocess.run(["pactl", "unload-module", str(idx)],
                          capture_output=True, timeout=15)
    return {"index": idx, "rc": proc.returncode}


def leg(name, tone, dev, env_extra):
    env = dict(os.environ)
    env.update(env_extra or {})
    argv = ["aplay", "-D", dev, str(tone)]
    rec = {"name": name, "argv": " ".join(argv),
           "env_extra": sorted((env_extra or {}).keys())}
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.DEVNULL, env=env,
                            start_new_session=True)
    time.sleep(0.8)
    g = M._alsapw_r84_graph()
    cands = M._alsapw_r84_cands(g, "alsa_playback.aplay", PREFIX + "_env")
    for c in cands:
        c["consumers"] = M._alsapw_r84_consumers_id(g, c["object_id"])
    rec["nodes_mid"] = [
        {"name": c["name"], "state": c.get("state"),
         "node_latency": (c.get("props") or {}).get("node.latency"),
         "target_object": (c.get("props") or {}).get("target.object"),
         "consumers": c["consumers"]}
        for c in cands]
    try:
        proc.wait(timeout=6.0)
    except subprocess.TimeoutExpired:
        M._alsapw_r84_killpg(proc)
        proc.wait()
        rec["killed_at_bound"] = True
    rec["exit_code"] = proc.returncode
    rec["stderr_tail"] = proc.stderr.read().decode(errors="replace")[:200]
    return rec


def main():
    rec = {"probe": "probeB-env-hermeticity", "pid": os.getpid(),
           "loadavg": open("/proc/loadavg").read().split()[:3],
           "ambient_audio_env": {k: v for k, v in os.environ.items()
                                 if k.startswith(("PIPEWIRE", "PULSE"))}}
    TMP.mkdir(parents=True, exist_ok=True)
    tone = TMP / "r84c_env_tone.wav"
    M._playback_r78_write_tone(tone, 1.4)
    try:
        rec["load"] = load(NS)
        time.sleep(0.4)
        rec["legs"] = {
            "ctl": leg("ctl", tone, f"pipewire:NODE={NS},PERIOD_BYTES=4096",
                       {}),
            "env_latency": leg(
                "env_latency", tone,
                f"pipewire:NODE={NS},PERIOD_BYTES=4096",
                {"PIPEWIRE_LATENCY": "2048/48000"}),
            "env_props_name": leg(
                "env_props_name", tone, f"pipewire:NODE={NS}",
                {"PIPEWIRE_PROPS": "{ node.name=r84c_envname }"}),
        }
    finally:
        rec["unload"] = unload(NS)
        time.sleep(0.4)
        rec["residue_modules"] = [ln.strip() for ln in modules().splitlines()
                                  if PREFIX in ln]
        rec["residue_sinks"] = [
            ln.strip() for ln in subprocess.run(
                ["pactl", "list", "sinks", "short"], capture_output=True,
                timeout=10).stdout.decode(errors="replace").splitlines()
            if PREFIX in ln]
    OUT.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
