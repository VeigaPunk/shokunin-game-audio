#!/usr/bin/env python3
"""r87 reviewer — S7: the create-node refusal legs under churn.

The fixture's `create_badfac` / `create_usage` verdicts search the LAST
400 chars of a held-session log for the async refusal. This probe re-runs
both commands with a FULL log capture and records where the refusal sits
relative to the end of the log. Nothing is created (bogus factory /
missing factory.name), nothing is destroyed.
"""
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent / "create-node-tail.json"


def session(cmd, wait_s):
    p = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         start_new_session=True)
    chunks = []

    def drain():
        try:
            while True:
                b = p.stdout.read(65536)
                if not b:
                    return
                chunks.append(b)
        except (OSError, ValueError):
            return

    th = threading.Thread(target=drain, daemon=True)
    th.start()
    time.sleep(1.2)
    p.stdin.write(cmd.encode() + b"\n")
    p.stdin.flush()
    time.sleep(wait_s)
    p.stdin.write(b"quit\n")
    p.stdin.flush()
    try:
        p.stdin.close()
    except OSError:
        pass
    try:
        p.wait(timeout=8)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.wait(timeout=3)
    th.join(timeout=2.0)
    log = b"".join(chunks).decode(errors="replace")
    return log


def main():
    res = {"reps": []}
    for rep in range(3):
        for name, cmd, wait_s, pat in (
                ("create_badfac",
                 'create-node adapter { factory.name='
                 '"no_such_r87_factory" }', 2.0,
                 r"res:-2.*can't create node"),
                ("create_usage", 'create-node adapter { }', 1.6,
                 r"res:-22.*usage: factory\.name=")):
            log = session(cmd, wait_s)
            m = re.search(pat, log)
            pos = m.start() if m else None
            res["reps"].append({
                "rep": rep, "leg": name, "log_chars": len(log),
                "refusal_found": bool(m),
                "refusal_at_char": pos,
                "chars_from_end": (len(log) - pos) if m else None,
                "inside_last_400": bool(m and len(log) - pos <= 400),
                "errors": re.findall(r'Error: "([^"]+)"', log)[:4],
                "tail400": log[-400:]})
        res["loadavg_at_rep%d" % rep] = open("/proc/loadavg").read().split()[:3]
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps([{k: r[k] for k in ("rep", "leg", "log_chars",
                                         "refusal_found",
                                         "chars_from_end",
                                         "inside_last_400")}
                      for r in res["reps"]], indent=1))
    print("receipt:", OUT)


if __name__ == "__main__":
    main()
