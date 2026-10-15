#!/usr/bin/env python3
"""r97b stage WF — forensics on a LIVE wedged private core (r97 scout [?]3).

Captures, without re-arming first:
  wf1 the wedged state: pw-dump (bounded), pw-cli ls Client (bounded, full
      output), wpctl status, the core's /proc thread states / fd count
  wf2 does killing ONLY the private WirePlumber (own pid file, cmdline guard)
      unwedge the core? (the scout's second observation was "after a
      WirePlumber restart")
  wf3 after re-arming: is the new pair healthy, and does the wedge count in the
      ledger match?
Writes receipts/wedge_forensics.json. Bounded everywhere; own pids only.
"""
import json, os, signal, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import (SEAT, RUN, ENV, REC, SCR, run, dump, ensure_up, down,
                     stage_out, stage_write, loadavg, hog_count, note_wedge, health)


def proc_state(pidfile):
    try:
        pid = int(open(pidfile).read().strip())
    except Exception:
        return {"pid": None}
    out = {"pid": pid}
    try:
        st = open(f"/proc/{pid}/stat").read().split()
        out.update({"state": st[2], "nlwp": st[19], "utime": st[13], "stime": st[14]})
    except Exception as e:
        out["stat_error"] = str(e)
    try:
        out["wchan"] = open(f"/proc/{pid}/wchan").read().strip()
        out["cmdline"] = open(f"/proc/{pid}/cmdline").read().replace("\0", " ").strip()
        out["fds"] = len(os.listdir(f"/proc/{pid}/fd"))
        out["threads"] = []
        for t in os.listdir(f"/proc/{pid}/task"):
            try:
                out["threads"].append({"tid": t,
                                       "wchan": open(f"/proc/{pid}/task/{t}/wchan").read().strip()})
            except Exception:
                pass
    except Exception as e:
        out["proc_error"] = str(e)
    return out


def guarded_kill_pidfile(pidfile):
    try:
        pid = int(open(pidfile).read().strip())
    except Exception:
        return "no pidfile"
    try:
        cmd = open(f"/proc/{pid}/cmdline").read().replace("\0", " ")
    except Exception:
        return "gone"
    if SEAT not in cmd:
        return f"REFUSED (foreign cmd={cmd})"
    try:
        os.killpg(os.getpgid(pid), signal.SIGKILL)
    except Exception:
        try:
            os.kill(pid, signal.SIGKILL)
        except Exception:
            pass
    return "killed"


def main():
    out = stage_out("wf_forensics")
    out["loadavg_at_entry"] = loadavg()
    out["hogs_at_entry"] = hog_count()

    # wf1: characterize the live wedge
    r = run(["pw-dump"], timeout=12.0)
    out["wf1_pw_dump"] = {"rc": r["rc"], "timed_out": r["timed_out"],
                          "dur_s": r["dur_s"], "bytes": len(r["stdout"])}
    r2 = run(["pw-cli", "ls", "Client"], timeout=12.0)
    out["wf1_pw_cli_ls_client"] = {"rc": r2["rc"], "timed_out": r2["timed_out"],
                                   "dur_s": r2["dur_s"],
                                   "stdout": r2["stdout"][:2000],
                                   "stderr": r2["stderr"][:600]}
    r3 = run(["wpctl", "status"], timeout=12.0)
    out["wf1_wpctl_status"] = {"rc": r3["rc"], "timed_out": r3["timed_out"],
                               "dur_s": r3["dur_s"], "bytes": len(r3["stdout"])}
    out["wf1_core_proc"] = proc_state(os.path.join(RUN, "core.pid"))
    out["wf1_wp_proc"] = proc_state(os.path.join(RUN, "wp.pid"))
    out["wf1_wedged"] = (r["timed_out"] or r["rc"] != 0)
    note_wedge("forensics_wedged_state", "wf1", out["wf1_pw_dump"])

    # wf2: kill ONLY the private WirePlumber and re-probe
    out["wf2_kill_wp"] = guarded_kill_pidfile(os.path.join(RUN, "wp.pid"))
    time.sleep(1.5)
    h = health(cap=10.0, context="wf2/after_wp_kill")
    out["wf2_health_after_wp_kill"] = h
    note_wedge("forensics_after_wp_kill", "wf2", h)
    out["wf2_core_proc_after"] = proc_state(os.path.join(RUN, "core.pid"))
    if not h["ok"]:
        # kill the core too (own pid, guarded) and re-probe with the socket gone
        out["wf2_kill_core"] = guarded_kill_pidfile(os.path.join(RUN, "core.pid"))
        time.sleep(1.0)
        out["wf2_health_after_core_kill"] = health(cap=8.0, context="wf2/after_core_kill")

    # wf3: re-arm and confirm the new pair is healthy
    e = ensure_up(verbose=True)
    out["wf3_rearm"] = e
    out["wf3_health_after_rearm"] = health(cap=10.0, context="wf3/after_rearm")
    out["loadavg_at_exit"] = loadavg()
    print(json.dumps(out, indent=1)[:4000])
    stage_write(out, "wedge_forensics.json")


if __name__ == "__main__":
    main()
