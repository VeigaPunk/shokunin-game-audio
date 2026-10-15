#!/usr/bin/env python3
"""r97b stage B — replay of the r97 scout core law (claim 3, row
`wp.core.access_module_required`) under load: a private core whose fragment
disables `module.access` accepts the socket but never answers a client.

Cells (own runtime dir run3/, own conf dir per cell, core killed by own pid
with a cmdline namespace guard):
  B1 fragment with module.access = false   -> clients must time out (no reply)
  B2 fragment rt/profiler/portal off only  -> clients answer
  B3 no fragment at all                    -> clients answer
Each cell: start core, wait for socket, then `pw-cli ls Client` (cap 8 s) and
`pw-dump` (cap 8 s). Fresh core process per cell, per rep. Bounded.
"""
import json, os, signal, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import SEAT, ENV, REC, SCR, run, stage_out, stage_write, loadavg

RUN3 = os.path.join(SEAT, "run3")
BASE = os.path.join(SEAT, "conf", "pw")

CELLS = {
    "B1_access_off": ("context.properties = {\n"
                      "  module.rt = false\n  module.profiler = false\n"
                      "  module.portal = false\n  module.access = false\n}\n"),
    "B2_access_untouched": ("context.properties = {\n"
                            "  module.rt = false\n  module.profiler = false\n"
                            "  module.portal = false\n}\n"),
    "B3_no_fragment": None,
}


def build_dirs():
    """One conf dir per cell: a copy of the shipped conf + (maybe) one fragment."""
    src = open(os.path.join(BASE, "r97b-pipewire.conf")).read()
    dirs = {}
    for cell, frag in CELLS.items():
        d = os.path.join(BASE, f"r97b-cell-{cell}")
        os.makedirs(os.path.join(d, "r97b-pipewire.conf.d"), exist_ok=True)
        with open(os.path.join(d, "r97b-pipewire.conf"), "w") as f:
            f.write(src)
        fp = os.path.join(d, "r97b-pipewire.conf.d", "10-r97b-cell.conf")
        if frag is None:
            if os.path.exists(fp):
                os.unlink(fp)
        else:
            with open(fp, "w") as f:
                f.write(frag)
        dirs[cell] = d
    return dirs


def guarded_kill(pid):
    try:
        cmd = open(f"/proc/{pid}/cmdline").read().replace("\0", " ")
    except Exception:
        return "gone"
    if SEAT in cmd:
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except Exception:
            try:
                os.kill(pid, signal.SIGKILL)
            except Exception:
                pass
        return "killed"
    return f"REFUSED (foreign cmd={cmd})"


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out = stage_out("b_access")
    out["arm"] = arm
    os.makedirs(RUN3, exist_ok=True)
    dirs = build_dirs()
    out["cells"] = {c: (CELLS[c] or "(no fragment)") for c in CELLS}
    e = dict(ENV)
    e["PIPEWIRE_RUNTIME_DIR"] = RUN3
    e["XDG_RUNTIME_DIR"] = RUN3
    e["PIPEWIRE_DEBUG"] = "2"

    for n in range(reps):
        rep = {"rep": n, "cells": {}}
        for cell, d in dirs.items():
            # fresh runtime dir contents: only this seat's sockets are removed
            for f in os.listdir(RUN3):
                p = os.path.join(RUN3, f)
                if os.path.exists(p):
                    os.unlink(p)
            conf = os.path.join(d, "r97b-pipewire.conf")
            p = subprocess.Popen(["pipewire", "-c", conf], env=e,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 start_new_session=True, text=True)
            sock = os.path.join(RUN3, "pipewire-0")
            for _ in range(60):
                if os.path.exists(sock):
                    break
                time.sleep(0.25)
            cellobs = {"sock_present": os.path.exists(sock), "core_pid": p.pid}
            r1 = run(["pw-cli", "ls", "Client"], timeout=8.0, env=e)
            r2 = run(["pw-dump"], timeout=8.0, env=e)
            cellobs["pw_cli"] = {"rc": r1["rc"], "timed_out": r1["timed_out"],
                                 "dur_s": r1["dur_s"],
                                 "out_head": r1["stdout"][:300],
                                 "err_head": r1["stderr"][:300]}
            cellobs["pw_dump"] = {"rc": r2["rc"], "timed_out": r2["timed_out"],
                                  "dur_s": r2["dur_s"],
                                  "out_len": len(r2["stdout"]),
                                  "err_head": r2["stderr"][:300]}
            cellobs["answered"] = (r1["rc"] == 0 and not r1["timed_out"])
            cellobs["loadavg"] = loadavg()
            cellobs["kill"] = guarded_kill(p.pid)
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            try:
                corelog = p.stdout.read() or ""
            except Exception:
                corelog = ""
            lp = os.path.join(SCR, f"b_{cell}_rep{n}.log")
            open(lp, "w").write(corelog)
            cellobs["core_log"] = lp.replace(SEAT, "$SEAT")
            cellobs["core_log_head"] = corelog[:600]
            rep["cells"][cell] = cellobs
            time.sleep(0.5)
        out["reps"].append(rep)
        out["loadavg_end_rep"] = loadavg()

    for rep in out["reps"]:
        print(f"--- rep {rep['rep']}")
        for c, o in rep["cells"].items():
            print(f"  {c:<22} sock={o['sock_present']} answered={o['answered']} "
                  f"pw_cli rc={o['pw_cli']['rc']} timed={o['pw_cli']['timed_out']} "
                  f"{o['pw_cli']['dur_s']}s | dump rc={o['pw_dump']['rc']} "
                  f"timed={o['pw_dump']['timed_out']} len={o['pw_dump']['out_len']}")
    stage_write(out, "b_access.json")


if __name__ == "__main__":
    main()
