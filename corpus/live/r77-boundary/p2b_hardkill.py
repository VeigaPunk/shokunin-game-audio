"""r77 BOUNDARY probe 2b — HARD kill of the node-owning client (provider death).

The scout's `sustained_after_target_loss` used `pactl unload-module` (a graceful
daemon-side removal). This probe creates the sink from a CLIENT (`pw-cli`
create-node, `object.linger=false`) and `kill -9`s that client, then measures the
same capture. The client must stay alive to own the node, so it is driven over a
pipe rather than as a one-shot command.
"""

from __future__ import annotations

import json
import subprocess
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
    spawn,
    wipe_scratch,
)

N = 288000
NOMINAL = N * 2 * 2 + 44
NODE = "r77bkill"


class Sampler(threading.Thread):
    def __init__(self, path, interval=0.15):
        super().__init__(daemon=True)
        self.path, self.interval, self.samples = path, interval, []
        self.stop = threading.Event()

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


def sink_listed(name):
    return name in sh(["pactl", "list", "short", "sinks"], timeout=10)["out"]


def main():
    wipe_scratch()
    make_tone()
    rec = {"probe": "r77-boundary/p2b-hard-kill-provider", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    # Drive pw-cli interactively: the client stays alive and owns the node.
    cli = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True)
    cmd = (f"create-node adapter {{ factory.name = support.null-audio-sink node.name = {NODE} "
           f"media.class = Audio/Sink object.linger = false audio.rate = 48000 "
           f"audio.channels = 2 audio.position = [ FL FR ] }}")
    cli.stdin.write(cmd + "\n")
    cli.stdin.flush()
    time.sleep(1.6)
    rec["create_node"] = {"cmd": cmd, "pid": cli.pid, "listed": sink_listed(NODE),
                          "cli_alive": cli.poll() is None}
    if not rec["create_node"]["listed"]:
        out = ""
        try:
            cli.stdin.close()
            out = cli.stdout.read()[:800]
        except Exception:  # noqa: BLE001
            pass
        rec["create_node"]["cli_output"] = out
        rec["abort"] = "client-owned null sink was not created"
        try:
            cli.kill()
        except Exception:  # noqa: BLE001
            pass
        save_receipt("probe-p2b-hard-kill-provider.json", rec)
        print(json.dumps(rec["create_node"], indent=1))
        print("ABORT:", rec["abort"])
        return

    # capture its monitor, then hard-KILL the owning client mid-stream
    out_file = SCRATCH / "hardkill.wav"
    cap = spawn(["pw-record", "-P", "stream.capture.sink=true", "--target", NODE, "-n", str(N), str(out_file)])
    s = Sampler(out_file)
    s.start()
    time.sleep(1.5)
    rec["topology_before_kill"] = sh(["pw-link", "-l"], timeout=10, cap=200000)["out"].count("monitor")
    cli.send_signal(9)  # HARD KILL of the node owner
    time.sleep(0.5)
    rec["after_kill"] = {
        "cli_rc": cli.poll(),
        "sink_still_listed": sink_listed(NODE),
        "pactl_sources_grep": sh(["bash", "-lc", f"pactl list short sources | grep -c {NODE}"], timeout=10)["out"].strip(),
    }
    rep = reap(cap, timeout=16)
    samples = s.finish()
    insp = inspect_wav(out_file)
    rec["capture"] = {"rc": rep["rc"], "killed_by_us": rep["killed_by_us"], "err": rep["err"].strip()[:300],
                      "file": {k: insp.get(k) for k in ("bytes", "riff_size_field", "data_declared_field",
                                                        "payload_bytes_actual", "frames", "peak", "nonzero_frac")},
                      "nominal_bytes": NOMINAL,
                      "overrun_vs_nominal": (insp.get("bytes") or 0) - NOMINAL}
    rec["pacing"] = {"samples": samples,
                     "rate_after_kill_Bps": _rate(samples, 2.0),
                     "nominal_Bps": 48000 * 2 * 2}

    save_receipt("probe-p2b-hard-kill-provider.json", rec)
    print("create_node:", json.dumps(rec["create_node"]))
    print("after_kill:", json.dumps(rec["after_kill"]))
    print("capture:", json.dumps(rec["capture"]))
    print("rate after kill:", rec["pacing"]["rate_after_kill_Bps"], "nominal", rec["pacing"]["nominal_Bps"])
    print("samples:", samples)


def _rate(samples, after_t):
    pts = [(t, s) for t, s in samples if s is not None and t >= after_t]
    if len(pts) < 2:
        return None
    (t0, s0), (t1, s1) = pts[0], pts[-1]
    return round((s1 - s0) / max(t1 - t0, 1e-6), 1)


if __name__ == "__main__":
    main()
