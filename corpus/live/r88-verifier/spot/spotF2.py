#!/usr/bin/env python3
"""r88-verifier spot F (four-witness state agreement) — instrumented.

Own null sink (r88v_ns_<pid>), idle + driven by an own pw-play stream;
records every witness sample and the link map so a failure is diagnosable.
Name-verified teardown; never set-default-*.
"""
import json
import os
import re
import signal
import struct
import subprocess
import sys
import time
import wave
from math import sin, pi
from pathlib import Path

PID = os.getpid()
NS = f"r88v_ns_{PID}"
TAG = f"r88v_pt_{PID}"
ROLE = f"r88vrole{PID}"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
RAW = OUT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
LOG = []


def run(argv, timeout=25):
    try:
        p = subprocess.run([str(a) for a in argv], capture_output=True,
                           timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return {"rc": None, "out": "", "err": "", "timeout": True}
    return {"rc": p.returncode, "out": p.stdout.decode(errors="replace"),
            "err": p.stderr.decode(errors="replace"), "timeout": False}


def dump():
    r = run(["pw-dump"], 30)
    try:
        return json.loads(r["out"])
    except Exception:
        LOG.append({"dump_failed": r.get("rc"), "err": r.get("err")[:200]})
        return None


def props(o):
    return (o.get("info") or {}).get("props") or {}


def state_of(objs, name):
    for o in objs or []:
        if props(o).get("node.name") == name:
            return {"id": o.get("id"),
                    "state": (o.get("info") or {}).get("state"),
                    "serial": props(o).get("object.serial"),
                    "media_class": props(o).get("media.class")}
    return None


def links_touching(objs, name):
    ids = {o.get("id"): props(o).get("node.name") for o in objs or []}
    out = []
    for o in objs or []:
        p = props(o)
        if str(o.get("type", "")).endswith("Link"):
            out.append({"id": o.get("id"),
                        "out_node": p.get("link.output.node"),
                        "in_node": p.get("link.input.node"),
                        "out": ids.get(p.get("link.output.node")),
                        "in": ids.get(p.get("link.input.node")),
                        "state": (o.get("info") or {}).get("state")})
    return out


def witness(tag):
    sinks = run(["pactl", "list", "sinks", "short"])["out"]
    pactl = None
    for ln in sinks.splitlines():
        f = ln.split("\t")
        if len(f) >= 3 and f[1].strip() == NS:
            pactl = f[-1].strip()
    objs = dump()
    node = state_of(objs, NS)
    cli = run(["pw-cli", "info", str((node or {}).get("id") or 0)])
    m = re.search(r'state: "([a-z]+)"', cli["out"])
    top = run(["pw-top", "-b", "-n", "3"], 25)
    frames, cur = [], None
    for ln in top["out"].splitlines():
        if re.match(r"^S\s+ID\s+QUANT", ln):
            cur = []
            frames.append(cur)
            continue
        mm = re.match(r"^([A-Za-z])\s+(\d+)\s", ln)
        if cur is not None and mm:
            cur.append((mm.group(1), int(mm.group(2))))
    own_row = None
    if frames and node:
        own_row = next((s for s, i in frames[-1] if i == node.get("id")), None)
    rec = {"tag": tag, "pactl": pactl, "dump": (node or {}).get("state"),
           "cli": m.group(1) if m else None, "top": own_row,
           "top_frames": len(frames), "own": node,
           "vocab": {"pactl": {"SUSPENDED": "suspended", "RUNNING": "running",
                               "IDLE": "idle"}.get(pactl),
                     "dump": (node or {}).get("state"),
                     "cli": m.group(1) if m else None,
                     "top": {"S": "suspended", "I": "idle", "R": "running"}
                            .get(own_row)}}
    LOG.append(rec)
    return rec


def main():
    out = {"pid": PID, "ns": NS}
    mod = run(["pactl", "load-module", "module-null-sink", f"sink_name={NS}",
               f"node.description=r88v probe {PID}"])
    mod_id = mod["out"].strip()
    out["load"] = {"rc": mod["rc"], "module_id": mod_id,
                   "err": mod["err"].strip()}
    if mod["rc"] != 0 or not mod_id.isdigit():
        (OUT / "spotF2.json").write_text(json.dumps(out, indent=1))
        return
    t0 = time.time()
    own = None
    while time.time() - t0 < 8:
        objs = dump() or []
        own = state_of(objs, NS)
        if own:
            break
        time.sleep(0.2)
    out["own"] = own
    if not own:
        run(["pactl", "unload-module", mod_id])
        (OUT / "spotF2.json").write_text(json.dumps(out, indent=1))
        return
    time.sleep(0.6)
    out["idle"] = witness("idle")
    tone = RAW / "r88v_tone2.wav"
    with wave.open(str(tone), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"".join(struct.pack("<h", int(
            12000 * sin(2 * pi * 440 * i / 48000))) for i in range(48000 * 8)))
    p = subprocess.Popen(["pw-play", "-P", f"node.name={TAG}",
                          "-P", f"media.role={ROLE}", "--target", NS,
                          str(tone)], stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL, start_new_session=True)
    linked, polls = False, []
    deadline = time.time() + 12
    while time.time() < deadline:
        objs = dump() or []
        stream = state_of(objs, TAG)
        sink = state_of(objs, NS)
        lk = [l for l in links_touching(objs, TAG)
              if l.get("in_node") == (sink or {}).get("id")]
        polls.append({"stream": stream, "sink": sink, "links_to_ns": lk})
        if stream and stream.get("state") == "running" and lk:
            linked = True
            break
        time.sleep(0.25)
    out["linked"] = linked
    out["polls"] = polls[-6:]
    if linked:
        out["active"] = witness("active")
    try:
        os.killpg(p.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        p.wait(timeout=4)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    # name-verified unload
    mods = run(["pactl", "list", "modules", "short"])["out"]
    line = next((ln for ln in mods.splitlines()
                 if ln.split("\t")[0].strip() == mod_id), "")
    out["unload"] = {"line": line,
                     "sink_name_ok": f"sink_name={NS}" in line,
                     "rc": run(["pactl", "unload-module", mod_id])["rc"]}
    time.sleep(0.4)
    objs = dump() or []
    resid = [str(o.get("id")) for o in objs
             if props(o).get("node.name")
             and props(o).get("node.name").startswith("r88v_")]
    out["residual"] = resid
    if resid:
        out["residual_destroy"] = [run(["pw-cli", "destroy", i])
                                   for i in resid]
        time.sleep(0.4)
    objs = dump() or []
    out["sink_gone"] = state_of(objs, NS) is None
    out["residue_after"] = sorted(props(o).get("node.name") for o in objs
                                  if props(o).get("node.name")
                                  and props(o).get("node.name").startswith(
                                      "r88v_"))
    out["log"] = LOG
    (OUT / "spotF2.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
