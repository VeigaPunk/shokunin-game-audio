"""r77 BOUNDARY probe 2 — zombie capture: pacing, hard-KILLed provider, topology.

Sharpens the scout's `sustained_after_target_loss` class:
  A. is the surviving stream still FRAME-CLOCKED (does -n still bound it) or
     does it free-run, and is its byte rate exactly nominal after the loss?
  B. does a HARD `kill -9` of the node-owning client (not `pactl unload-module`)
     land the same class?
  C. what does the link topology say (the only honest consumption witness)?
  D. feeder-process KILL (the provider of *signal* into a surviving node).
"""

from __future__ import annotations

import json
import re
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import (  # noqa: E402
    SCRATCH,
    TONE,
    inspect_wav,
    make_tone,
    reap,
    save_receipt,
    sh,
    size_watchdog,
    spawn,
    wipe_scratch,
)

N = 288000  # 6 s @48k stereo s16 -> nominal 1152000 payload + 44 hdr
NOMINAL = N * 2 * 2 + 44
NULLSINK = "r77bz"
NULLSINK2 = "r77bz2"


class Sampler(threading.Thread):
    """Poll a growing file's size with timestamps; never reads content."""

    def __init__(self, path, interval=0.15):
        super().__init__(daemon=True)
        self.path, self.interval, self.samples, self.stop = path, interval, [], threading.Event()

    def run(self):
        t0 = time.monotonic()
        while not self.stop.is_set():
            try:
                sz = self.path.stat().st_size if self.path.exists() else None
            except OSError:
                sz = None
            self.samples.append((round(time.monotonic() - t0, 3), sz))
            self.stop.wait(self.interval)

    def finish(self):
        self.stop.set()
        self.join(timeout=2)
        return self.samples


def rate_profile(samples, split_t):
    def rate(a, b):
        pts = [(t, s) for t, s in samples if s is not None and a <= t <= b]
        if len(pts) < 2:
            return None
        (t0, s0), (t1, s1) = pts[0], pts[-1]
        if t1 == t0:
            return None
        return round((s1 - s0) / (t1 - t0), 1)

    return {
        "before_Bps": rate(0, split_t - 0.2),
        "after_Bps": rate(split_t + 0.3, 99),
        "samples": samples,
    }


def link_topology(grep_terms=("r77bz", "monitor")):
    out = sh(["pw-link", "-l"], timeout=10, cap=200000)
    lines = [ln for ln in out["out"].splitlines() if any(g in ln for g in grep_terms)]
    return {"rc": out["rc"], "n_lines": len(lines), "lines": lines[:60]}


def part_a_module_unload():
    r = {}
    load = sh(["pactl", "load-module", "module-null-sink", f"sink_name={NULLSINK}", "rate=48000"])
    r["load"] = load
    if load["rc"] != 0:
        return r
    mid = load["out"].strip()
    r["module_id"] = mid
    time.sleep(0.4)
    out = SCRATCH / "zombie_module.wav"
    p = spawn(["pw-record", "-P", "stream.capture.sink=true", "--target", NULLSINK, "-n", str(N), str(out)])
    s = Sampler(out)
    s.start()
    time.sleep(1.5)
    r["topology_before_loss"] = link_topology()
    un = sh(["pactl", "unload-module", mid], timeout=10)
    r["unload"] = un
    time.sleep(0.4)
    r["sink_still_listed"] = bool(sh(["pactl", "list", "short", "sources"], timeout=10)["out"].find(NULLSINK) >= 0)
    r["topology_after_loss"] = link_topology()
    rep = reap(p, timeout=14)
    samples = s.finish()
    r["rc"] = rep["rc"]
    r["killed_by_us"] = rep["killed_by_us"]
    r["err"] = rep["err"].strip()[:300]
    insp = inspect_wav(out)
    r["file"] = {k: insp.get(k) for k in ("bytes", "riff_size_field", "data_declared", "data_declared_field",
                                          "payload_bytes_actual", "peak", "nonzero_frac", "frames")}
    r["nominal_bytes"] = NOMINAL
    r["overrun_vs_nominal"] = (insp.get("bytes") or 0) - NOMINAL
    r["pacing"] = rate_profile(samples, 1.5)
    r["peak_Bps_nominal"] = 48000 * 2 * 2
    return r


def part_b_hard_kill_provider():
    """Create a node from a CLIENT process (object.linger=false) and kill -9 it."""
    r = {}
    script = (
        "pw-cli create-node adapter '{ factory.name = support.null-audio-sink "
        f"node.name = {NULLSINK2} media.class = Audio/Sink object.linger = false "
        "audio.rate = 48000 audio.channels = 2 audio.position = [ FL FR ] }'"
    )
    p = spawn(["bash", "-c", script], out_path=SCRATCH / "pwcli_create_node.log")
    time.sleep(1.5)
    listed = sh(["pactl", "list", "short", "sinks"], timeout=10)
    r["created"] = NULLSINK2 in listed["out"]
    r["pwcli_pid"] = p.pid
    r["pwcli_alive"] = p.poll() is None
    if not r["created"]:
        r["abort"] = "create-node did not produce a sink"
        reap(p, timeout=3)
        return r
    out = SCRATCH / "zombie_hardkill.wav"
    cap = spawn(["pw-record", "-P", "stream.capture.sink=true", "--target", NULLSINK2, "-n", str(N), str(out)])
    s = Sampler(out)
    s.start()
    time.sleep(1.5)
    r["topology_before_kill"] = link_topology((NULLSINK2, "monitor"))
    t_kill = 1.5
    p.send_signal(9)  # HARD KILL of the node-owning client
    kres = reap(p, timeout=4)
    r["provider_kill"] = {"rc": kres["rc"], "killed": True}
    time.sleep(0.5)
    r["sink_still_listed_after_kill"] = NULLSINK2 in sh(["pactl", "list", "short", "sinks"], timeout=10)["out"]
    r["topology_after_kill"] = link_topology((NULLSINK2, "monitor"))
    rep = reap(cap, timeout=14)
    samples = s.finish()
    r["rc"] = rep["rc"]
    r["killed_by_us"] = rep["killed_by_us"]
    r["err"] = rep["err"].strip()[:300]
    insp = inspect_wav(out)
    r["file"] = {k: insp.get(k) for k in ("bytes", "riff_size_field", "data_declared", "data_declared_field",
                                          "payload_bytes_actual", "peak", "nonzero_frac", "frames")}
    r["nominal_bytes"] = NOMINAL
    r["overrun_vs_nominal"] = (insp.get("bytes") or 0) - NOMINAL
    r["pacing"] = rate_profile(samples, t_kill)
    return r


def part_c_feeder_kill():
    """Provider of SIGNAL killed hard while the node survives."""
    r = {}
    load = sh(["pactl", "load-module", "module-null-sink", f"sink_name={NULLSINK}3", "rate=48000"])
    r["load"] = load
    if load["rc"] != 0:
        return r
    time.sleep(0.3)
    out = SCRATCH / "zombie_feeder.wav"
    cap = spawn(["pw-record", "-P", "stream.capture.sink=true", "--target", f"{NULLSINK}3",
                 "-n", "144000", str(out)])  # 3 s
    feeder = spawn(["pw-cat", "-p", "--target", f"{NULLSINK}3", str(TONE)])
    time.sleep(1.0)
    feeder.send_signal(9)
    fk = reap(feeder, timeout=3)
    r["feeder_kill"] = {"rc": fk["rc"]}
    rep = reap(cap, timeout=12)
    r["rc"] = rep["rc"]
    r["err"] = rep["err"].strip()[:200]
    insp = inspect_wav(out, segs=3)
    r["file"] = {k: insp.get(k) for k in ("bytes", "riff_size_field", "data_declared", "payload_bytes_actual",
                                          "peak", "nonzero_frac", "frames")}
    r["segments"] = insp.get("segments")
    r["nominal_bytes"] = 144000 * 2 * 2 + 44
    sh(["pactl", "unload-module", load["out"].strip()], timeout=10)
    return r


def main():
    wipe_scratch()
    make_tone()
    rec = {"probe": "r77-boundary/p2-zombie", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "nominal_6s_bytes": NOMINAL}
    rec["A_module_unload"] = part_a_module_unload()
    rec["B_hard_kill_provider"] = part_b_hard_kill_provider()
    rec["C_feeder_kill"] = part_c_feeder_kill()
    save_receipt("probe-p2-zombie.json", rec)

    a = rec["A_module_unload"]
    print("A module-unload:", json.dumps({k: a.get(k) for k in
          ("rc", "killed_by_us", "overrun_vs_nominal", "nominal_bytes", "err")}))
    print("   file:", a.get("file"), "pacing:", {k: v for k, v in (a.get("pacing") or {}).items() if k != "samples"})
    print("   samples:", (a.get("pacing") or {}).get("samples"))
    print("   topo_after:", (a.get("topology_after_loss") or {}).get("lines"))
    b = rec["B_hard_kill_provider"]
    print("B hard-kill-provider:", json.dumps({k: b.get(k) for k in
          ("created", "pwcli_alive", "sink_still_listed_after_kill", "rc", "killed_by_us", "overrun_vs_nominal",
           "nominal_bytes", "err", "abort")}))
    print("   file:", b.get("file"), "pacing:", {k: v for k, v in (b.get("pacing") or {}).items() if k != "samples"})
    print("   samples:", (b.get("pacing") or {}).get("samples"))
    c = rec["C_feeder_kill"]
    print("C feeder-kill:", json.dumps({k: c.get(k) for k in ("rc", "nominal_bytes", "err")}))
    print("   file:", c.get("file"), "segs:", c.get("segments"))


if __name__ == "__main__":
    main()
