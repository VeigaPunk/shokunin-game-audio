#!/usr/bin/env python3
"""r88 reviewer SPOT — independent pw-top -n 3 own-row check.

Loads a seat-owned null sink (r88r_top_<pid>), resolves its native node
id, runs `pw-top -b -n 3` (bounded retry), and reports the first frame's
status set and the own row's status in the LAST frame — the one pt_n3
sub-check the receipts cannot re-derive (stdout_raw is popped).  The
sink is unloaded name-verified at the end.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time

PID = os.getpid()
NAME = f"r88r_top_{PID}"


def run(argv, timeout, kill_on_timeout=False):
    p = subprocess.Popen(argv, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, start_new_session=True)
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out.decode(), err.decode()
    except subprocess.TimeoutExpired:
        if kill_on_timeout:
            os.killpg(p.pid, signal.SIGKILL)
            out, err = p.communicate()
            return p.returncode, out.decode(), err.decode()
        raise


def frames_of(text):
    frames, cur = [], None
    for ln in text.splitlines():
        if re.match(r"^S\s+ID\s+QUANT", ln):
            cur = []
            frames.append(cur)
            continue
        m = re.match(r"^([A-Za-z])\s+(\d+)\s", ln)
        if cur is not None and m:
            cur.append({"status": m.group(1), "id": int(m.group(2))})
    return frames


def main():
    rc, out, err = run(["pactl", "load-module", "module-null-sink",
                        f"sink_name={NAME}"], 15)
    idx = int(out.strip())
    time.sleep(0.4)
    census = json.loads(subprocess.run(["pw-dump"], capture_output=True,
                                       timeout=30).stdout)
    own = next((o for o in census
                if ((o.get("info") or {}).get("props") or {})
                .get("node.name") == NAME), None)
    own_id = own["id"]
    result = {"name": NAME, "module_index": idx, "own_id": own_id,
              "attempts": []}
    frames = []
    for attempt in range(1, 4):
        rc2, out2, _ = run(["pw-top", "-b", "-n", "3"], 20)
        frames = frames_of(out2)
        result["attempts"].append({"attempt": attempt,
                                   "frames": [len(f) for f in frames]})
        if len(frames) >= 2:
            break
    if len(frames) >= 2:
        first = sorted({r["status"] for r in frames[0]})
        last_row = next((r for r in frames[-1] if r["id"] == own_id), None)
        result.update({
            "first_frame_statuses": first,
            "last_frame_status_hist": sorted(
                {r["status"]: sum(1 for x in frames[-1]
                                  if x["status"] == r["status"])
                 for r in frames[-1]}.items()),
            "own_row_last_frame": last_row})
    else:
        result["frames"] = [len(f) for f in frames]
    # name-verified unload
    m = subprocess.run(["pactl", "list", "modules", "short"],
                       capture_output=True, timeout=10).stdout.decode()
    line = next((l for l in m.splitlines()
                 if l.split("\t")[0] == str(idx)), "")
    if NAME in line:
        subprocess.run(["pactl", "unload-module", str(idx)],
                       capture_output=True, timeout=15)
        result["unload"] = "name-verified, rc0"
    else:
        result["unload"] = f"REFUSED line={line!r}"
    time.sleep(0.3)
    sinks = subprocess.run(["pactl", "list", "sinks", "short"],
                           capture_output=True, timeout=10).stdout.decode()
    result["own_sink_gone"] = NAME not in sinks
    print(json.dumps(result, indent=1))
    with open("corpus/live/r88-reviewer/receipts/spot-pwtop-ownrow.json",
              "w") as fh:
        json.dump(result, fh, indent=1)


if __name__ == "__main__":
    main()
