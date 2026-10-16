#!/usr/bin/env python3
"""r88-verifier mechanism probe: the `wd_dump_empty` bracket race.

The fixture arms `pw-dump ''` (the "full dump") against two bracketing
censuses c1 (entry start) and c2 (right after): the run PASSES only if the
'' dump's object-id set equals c1 OR c2.  Each `pw-dump`/`pw-cli`
invocation is itself a transient Client object, so the id set drifts
between brackets.  This probe replays the fixture's own sequence shape
(c1 -> ~20 mixed transient clients -> '' -> c2) N times and counts how
often the middle dump matches NEITHER bracket (the false-FAIL shape),
plus a churn variant with extra short-lived clients.
"""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20


def run(argv, timeout=25):
    p = subprocess.run([str(a) for a in argv], capture_output=True,
                       timeout=timeout, stdin=subprocess.DEVNULL)
    return p.stdout.decode(errors="replace")


def ids_of(t):
    try:
        return sorted(str(o.get("id")) for o in json.loads(t))
    except ValueError:
        return None


def churn(n=3):
    procs = []
    for _ in range(n):
        procs.append(subprocess.Popen(
            ["pw-cli", "ls", "Node"], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
            start_new_session=True))
    for p in procs:
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def rep(i, churn_extra):
    c1 = ids_of(run(["pw-dump"]))
    for _ in range(20):          # the entry's own transient-client legs
        run(["pw-dump", "1"])
    if churn_extra:
        churn(3)
    mid = ids_of(run(["pw-dump", ""]))
    c2 = ids_of(run(["pw-dump"]))
    ok = (mid is not None) and (mid == c1 or mid == c2)
    return {"rep": i, "churn": churn_extra, "c1": len(c1 or []),
            "mid": len(mid or []), "c2": len(c2 or []),
            "eq_c1": mid == c1, "eq_c2": mid == c2, "match": ok}


rows = [rep(i, False) for i in range(1, N + 1)]
rows += [rep(i, True) for i in range(1, N + 1)]
summary = {}
for r in rows:
    k = "with_extra_churn" if r["churn"] else "solo"
    s = summary.setdefault(k, {"reps": 0, "false_fail": 0, "eq_c1": 0,
                               "eq_c2": 0})
    s["reps"] += 1
    s["eq_c1"] += bool(r["eq_c1"])
    s["eq_c2"] += bool(r["eq_c2"])
    s["false_fail"] += (not r["match"])
(OUT / "raw" / "dumpempty-race.json").write_text(
    json.dumps({"rows": rows, "summary": summary}, indent=1) + "\n")
print(json.dumps(summary, indent=1))
