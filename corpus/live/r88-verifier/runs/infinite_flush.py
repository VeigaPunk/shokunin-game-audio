#!/usr/bin/env python3
"""r88-verifier mechanism probe: can the `-n -1` / `-n abc` frame arm
false-FAIL because the killed process's buffered output never reached the
pipe?

Replicates the fixture's runner discipline (Popen + start_new_session +
SIGKILL the group at the bound, then communicate() to drain) at the
fixture's own bound (BTWIT_R88_PWT_BOUND_S = 4.0) and at a shorter 3.0,
5 reps each, and reports captured bytes / parsed frames.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")


def frames_of(t):
    frames, cur = [], None
    for ln in (t or "").splitlines():
        if re.match(r"^S\s+ID\s+QUANT", ln):
            cur = []
            frames.append(cur)
            continue
        m = re.match(r"^([A-Za-z])\s+(\d+)\s", ln)
        if cur is not None and m:
            cur.append((m.group(1), int(m.group(2))))
    return frames


def rep(n_arg, bound, i):
    t0 = time.monotonic()
    p = subprocess.Popen(["pw-top", "-b", "-n", str(n_arg)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL, start_new_session=True)
    killed = False
    try:
        out, err = p.communicate(timeout=bound)
    except subprocess.TimeoutExpired:
        killed = True
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
    t = out.decode(errors="replace")
    fr = frames_of(t)
    return {"n": str(n_arg), "bound_s": bound, "rep": i,
            "killed_at_bound": killed, "rc": p.returncode,
            "stdout_bytes": len(out), "lines": len(t.splitlines()),
            "frames": [len(f) for f in fr],
            "status_sets": [sorted({s for s, _ in f}) for f in fr],
            "wall_s": round(time.monotonic() - t0, 3)}


rows = []
for n_arg in ("-1", "abc"):
    for bound in (3.0, 4.0):
        for i in range(1, 6):
            rows.append(rep(n_arg, bound, i))
summary = {}
for r in rows:
    key = f"{r['n']}@{r['bound_s']}"
    s = summary.setdefault(key, {"reps": 0, "empty_capture": 0,
                                 "bytes": [], "frames_ok": 0})
    s["reps"] += 1
    s["bytes"].append(r["stdout_bytes"])
    if r["stdout_bytes"] == 0:
        s["empty_capture"] += 1
    if r["frames"]:
        s["frames_ok"] += 1
(OUT / "raw" / "infinite-flush.json").write_text(
    json.dumps({"rows": rows, "summary": summary}, indent=1) + "\n")
print(json.dumps(summary, indent=1))
