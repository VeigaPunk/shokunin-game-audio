#!/usr/bin/env python3
"""r89 critic: the SIGHUP-disposition inheritance chain (mechanism proof).

Read-only w.r.t. the audio graph (spawns only `sleep`). Proves:

  (1) SIG_IGN for SIGHUP is inherited across execve (POSIX: only SIG_IGN
      survives exec, handlers are reset to SIG_DFL);
  (2) `subprocess.Popen(restore_signals=True)` — the fixture's default —
      does NOT reset SIGHUP (it resets only SIGPIPE/SIGXFZ/SIGXFSZ);
  (3) a launcher that ignores SIGHUP therefore hands the fixture's
      `pw-profiler` children an ignored SIGHUP, which makes the committed
      `g_hup` leg (rc must be -1) unpassable — it survives to the 9.0 s
      bound and the harness SIGKILLs it (rc -9).

The live /proc evidence for the wave's own runs is in
sigdisposition.json + the co-tenancy witness.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
CHILD = "import time; time.sleep(2.0)"


def sig_ign_mask(pid):
    txt = Path(f"/proc/{pid}/status").read_text()
    m = re.search(r"^SigIgn:\s*(\S+)", txt, re.M)
    mask = int(m.group(1), 16)
    names = []
    for sig, nm in ((1, "SIGHUP"), (2, "SIGINT"), (3, "SIGQUIT"),
                    (13, "SIGPIPE"), (25, "SIGXFSZ"), (15, "SIGTERM")):
        if mask & (1 << (sig - 1)):
            names.append(nm)
    return m.group(1), names


res = {"cases": []}


def case(name, ignore, restore):
    if ignore:
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    else:
        signal.signal(signal.SIGHUP, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    p = subprocess.Popen([sys.executable, "-c", CHILD],
                         restore_signals=restore)
    time.sleep(0.15)
    mask, names = sig_ign_mask(p.pid)
    p.wait()
    res["cases"].append({"case": name, "parent_ignores_hup": ignore,
                         "restore_signals": restore, "child_SigIgn": mask,
                         "child_ignored": names})
    print(f"{name:34s} parent_ignores_hup={ignore!s:5s} "
          f"restore_signals={restore!s:5s} -> child SigIgn={mask} {names}")


case("A parent default", False, True)
case("B parent ignores HUP", True, True)
case("C parent ignores HUP, no restore", True, False)

(OUT / "sig-inherit.json").write_text(json.dumps(res, indent=2) + "\n")
