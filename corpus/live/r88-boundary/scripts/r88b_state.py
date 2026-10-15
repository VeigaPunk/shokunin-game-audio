#!/usr/bin/env python3
"""r88b state-vocabulary A/B on ONE namespaced object (r88b_state null sink).

Condition A: sink idle (no stream).  Condition B: sink fed by a pw-cat stream.
Same object, same window -> tests the scout's rule "expect the pulse vocabulary to
disagree with the native vocabulary on the same object" (their n=1 was node 133,
pactl IDLE vs native running).
Creates only r88b_state (module-null-sink) and a pw-cat stream; both removed at the end.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r88b_probe import RAW, REC, run, utc, parse_pwdump_keys  # noqa: E402

WAV = RAW / "r88b_tone.wav"


def make_wav():
    with wave.open(str(WAV), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"\x00" * 48000 * 2 * 2 * 3)   # 3 s silence


def triple(tag):
    p = run(["pactl", "list", "sinks", "short"], timeout=30)
    d = run(["pw-dump"], timeout=60)
    objs = json.loads(d["stdout"])
    node = None
    for o in objs:
        pr = o.get("info", {}).get("props", {})
        if pr.get("node.name") == "r88b_state":
            node = (o["id"], o.get("info", {}).get("state"), pr.get("object.serial"))
    pstate = {}
    for ln in p["stdout"].splitlines():
        f = ln.split("\t")
        if len(f) > 4:
            pstate[f[1]] = f[4]
    t = run(["pw-top", "-b", "-n", "2"], timeout=60)
    (RAW / f"state-{tag}-pwt.txt").write_text(t["stdout"])
    rows = {}
    for line in t["stdout"].splitlines():
        tok = line.split()
        if len(tok) > 2 and tok[0] in ("C", "S", "I", "R", "t", "T", "E") and tok[1].isdigit():
            rows[int(tok[1])] = tok[0]
    streams = sorted(pr.get("node.name", "") for o in objs
                     if o.get("type", "").endswith("Node")
                     for pr in [o.get("info", {}).get("props", {})]
                     if str(pr.get("node.name", "")).startswith(("r88b", "pw-cat", "pw-play")))
    return {"tag": tag, "utc": utc(),
            "pactl_state": pstate.get("r88b_state"),
            "native": node,
            "ptop_state": rows.get(node[0]) if node else None,
            "streams_present": streams,
            "pactl_sink_lines": [ln for ln in p["stdout"].splitlines() if "r88b" in ln]}


def main():
    make_wav()
    out = {"battery": "state", "generated_utc": utc(), "A_idle": [], "B_active": [], "notes": {}}
    lc = run(["pactl", "load-module", "module-null-sink", "sink_name=r88b_state"], timeout=30)
    mid = lc["stdout"].strip()
    out["notes"]["load"] = {"rc": lc["rc"], "module": mid}
    time.sleep(1.0)
    for i in range(3):
        out["A_idle"].append(triple(f"A{i}"))
    # start my own stream into my own sink
    errf = open(RAW / "state-pwcat.err", "w")
    proc = subprocess.Popen(["pw-cat", "--playback", "--target", "r88b_state", str(WAV)],
                            stdout=subprocess.DEVNULL, stderr=errf)
    time.sleep(1.5)
    out["notes"]["pwcat_pid"] = proc.pid
    out["notes"]["pwcat_alive_during_B"] = proc.poll() is None
    for i in range(3):
        out["B_active"].append(triple(f"B{i}"))
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    errf.close()
    out["notes"]["pwcat_returncode"] = proc.returncode
    out["notes"]["pwcat_stderr"] = (RAW / "state-pwcat.err").read_text()[:400]
    time.sleep(0.6)
    ul = run(["pactl", "unload-module", mid], timeout=30)
    out["notes"]["unload"] = {"rc": ul["rc"]}
    time.sleep(0.6)
    chk = run(["bash", "-c", "pactl list sinks short | grep -c r88b_ || true; pw-dump | grep -c r88b_ || true"], timeout=30)
    out["notes"]["cleanup_pactl_dump"] = chk["stdout"].split()
    ps = run(["bash", "-c", "ps -eo pid,args | grep 'pw-cat' | grep -v grep | wc -l"], timeout=30)
    out["notes"]["stray_pwcat"] = ps["stdout"].strip()
    (REC / "B10-state.json").write_text(json.dumps(out, indent=1))
    print("A_idle:", json.dumps(out["A_idle"][0]))
    print("B_active:", json.dumps(out["B_active"][0]))
    print("notes:", json.dumps({k: v for k, v in out["notes"].items() if k != "pwcat_stderr"}))


if __name__ == "__main__":
    main()
