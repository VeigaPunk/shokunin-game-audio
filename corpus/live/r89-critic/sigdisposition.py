#!/usr/bin/env python3
"""r89 critic: read-only signal-disposition watcher.

The committed `g_hup` leg requires SIGHUP at 0.8 s to KILL `pw-profiler`
(rc -1). On the committed bytes that happens in the author's two runs and
in some sibling replays, and does NOT happen in others (rc -9: the run
survives HUP and is bound-killed at 9.0 s). This watcher polls for live
`pw-profiler` processes (the red shape stays alive ~9 s, so it is
catchable) and reads /proc/<pid>/status SigIgn / SigCgt / SigBlk plus
the cmdline — READ-ONLY, no signal is sent, nothing is spawned.
"""
import json
import os
import re
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
DURATION_S = 30.0

SIGNALS = {1: "SIGHUP", 2: "SIGINT", 3: "SIGQUIT", 4: "SIGILL", 5: "SIGTRAP",
           6: "SIGABRT", 7: "SIGBUS", 8: "SIGFPE", 9: "SIGKILL", 10: "SIGUSR1",
           11: "SIGSEGV", 12: "SIGUSR2", 13: "SIGPIPE", 14: "SIGALRM",
           15: "SIGTERM", 17: "SIGCHLD", 18: "SIGCONT", 19: "SIGSTOP",
           20: "SIGTSTP", 23: "SIGURG", 24: "SIGXCPU", 25: "SIGXFSZ",
           26: "SIGVTALRM", 28: "SIGWINCH", 29: "SIGIO"}


def mask_names(mask_hex, want="ign"):
    if not mask_hex:
        return []
    m = int(mask_hex, 16)
    out = []
    for sig in range(1, 32):
        if m & (1 << (sig - 1)):
            out.append(SIGNALS.get(sig, f"SIG{sig}"))
    return out


def proc_status(pid):
    try:
        txt = Path(f"/proc/{pid}/status").read_text()
    except OSError:
        return None
    d = {}
    for k in ("SigIgn", "SigCgt", "SigBlk", "SigPnd", "Name", "PPid"):
        m = re.search(rf"^{k}:\s*(\S+)", txt, re.M)
        if m:
            d[k] = m.group(1)
    return d


def cmdline(pid):
    try:
        return Path(f"/proc/{pid}/cmdline").read_bytes().replace(
            b"\0", b" ").decode(errors="replace").strip()
    except OSError:
        return None


observed = []
seen = set()
t0 = time.monotonic()
while time.monotonic() - t0 < DURATION_S:
    try:
        pids = [int(p) for p in os.listdir("/proc") if p.isdigit()]
    except OSError:
        pids = []
    for pid in pids:
        if pid in seen or pid == os.getpid():
            continue
        cl = cmdline(pid) or ""
        if not re.search(r"pw-profiler\b", cl):
            continue
        st = proc_status(pid)
        if not st:
            continue
        seen.add(pid)
        observed.append({
            "pid": pid, "cmdline": cl, "at_s": round(time.monotonic() - t0, 3),
            "SigIgn": st.get("SigIgn"),
            "SigIgn_names": mask_names(st.get("SigIgn")),
            "SigCgt_names": mask_names(st.get("SigCgt")),
            "hup_ignored": "SIGHUP" in mask_names(st.get("SigIgn")),
            "hup_caught": "SIGHUP" in mask_names(st.get("SigCgt")),
            "ppid": st.get("PPid")})
    time.sleep(0.05)

res = {"duration_s": DURATION_S, "observed": observed,
       "n_observed": len(observed),
       "n_hup_ignored": sum(1 for o in observed if o["hup_ignored"]),
       "n_hup_caught": sum(1 for o in observed if o["hup_caught"]),
       "cmdline_shapes": sorted({o["cmdline"] for o in observed})}
(OUT / "sigdisposition.json").write_text(json.dumps(res, indent=2) + "\n")
print(f"observed {res['n_observed']} pw-profiler processes in "
      f"{DURATION_S}s")
print("hup_ignored:", res["n_hup_ignored"],
      " hup_caught:", res["n_hup_caught"])
for o in observed[:20]:
    print(f"  pid {o['pid']} t={o['at_s']}s cmd='{o['cmdline'][:50]}' "
          f"SigIgn={o['SigIgn']} {o['SigIgn_names']} "
          f"SigCgt={o['SigCgt_names']}")
