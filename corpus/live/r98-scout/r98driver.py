#!/usr/bin/env python3
"""r98 scout driver — native pw_stream C-API battery (namespace r98s_*).

Seat: audio r98 scout (leaf). Writes only under corpus/live/r98-scout/.
Every child is bounded: wall timeout + start_new_session + killpg, RLIMIT_CORE=0
via preexec. Seat-owned objects only; the private null-sink r98s_ns is loaded
and unloaded by verified module index; no `pactl set-default-*` is ever issued.
"""
import hashlib
import json
import os
import re
import resource
import shutil
import signal
import subprocess
import sys
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROBE = ROOT / "probes" / "r98stream"
RAW = ROOT / "raw"
REC = ROOT / "receipts"
RUNS = ROOT / "runs"
SCRATCH = ROOT / "scratch"
SINK = "r98s_ns"
for d in (RAW, REC, RUNS, SCRATCH):
    d.mkdir(parents=True, exist_ok=True)


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha(b):
    return hashlib.sha256(b).hexdigest()


def _preexec():
    os.setsid()
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def sh(argv, timeout=20, env=None, cwd=None):
    t0 = time.time()
    p = subprocess.run(argv, capture_output=True, timeout=timeout, env=env,
                       cwd=cwd, preexec_fn=_preexec)
    return {"argv": argv, "rc": p.returncode, "out": p.stdout, "err": p.stderr,
            "wall_ms": int((time.time() - t0) * 1000)}


def kill_tree(p):
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except Exception:
        pass
    try:
        p.wait(timeout=5)
    except Exception:
        pass


def pw_dump():
    r = sh(["pw-dump"], timeout=15)
    try:
        return json.loads(r["out"])
    except Exception:
        return []


def node_name_by_id(objs):
    m = {}
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Node"):
            p = o.get("info", {}).get("props", {})
            m[o.get("id")] = p.get("node.name")
    return m


def links_of(objs, node_name):
    names = node_name_by_id(objs)
    out = []
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Link"):
            p = o.get("info", {}).get("props", {})
            on = names.get(p.get("link.output.node"))
            inn = names.get(p.get("link.input.node"))
            if node_name in (on, inn):
                out.append({"out": on, "in": inn, "state": p.get("link.state")})
    return out


def census(tag):
    objs = pw_dump()
    r98s_nodes = []
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Node"):
            p = o.get("info", {}).get("props", {})
            if str(p.get("node.name", "")).startswith("r98s"):
                r98s_nodes.append(p.get("node.name"))
    pactl = sh(["pactl", "list", "modules", "short"], timeout=15)
    r98s_mods = [l for l in pactl["out"].decode(errors="replace").splitlines()
                 if "r98s" in l]
    ps = sh(["ps", "-eo", "pid,args"], timeout=10)
    r98s_procs = []
    for l in ps["out"].decode(errors="replace").splitlines():
        toks = l.split()
        if not toks:
            continue
        if any(t.startswith("r98s") or "r98stream" in t for t in toks[1:]):
            r98s_procs.append(l)
    sp = Path.home() / ".local/state/wireplumber/stream-properties"
    sp_txt = sp.read_text(errors="replace") if sp.exists() else ""
    out = {"utc": utc(), "n_objects": len(objs), "r98s_nodes": r98s_nodes,
           "r98s_modules_pactl": r98s_mods, "r98s_procs": r98s_procs,
           "stream_properties_r98s_lines": [l for l in sp_txt.splitlines()
                                            if "r98s" in l]}
    (REC / f"census-{tag}.json").write_text(json.dumps(out, indent=1))
    return out


def parse_out(text):
    d = {}
    ev = []
    for line in text.splitlines():
        if line.startswith("R98 "):
            body = line[4:]
            if "=" in body:
                k, v = body.split("=", 1)
                d[k] = v
        elif line.startswith("EV "):
            ev.append(line[3:])
    d["_events"] = ev
    return d


def run_leg(name, args, rep=0, timeout=25, env=None, live=None, snap_pwtop=False,
            profiler=False, tone=False, sink_exists=True):
    """Run one probe leg. live: seconds after start to snapshot pw-dump links."""
    rec = {"leg": name, "rep": rep, "utc_start": utc(), "argv": [str(PROBE)] + args}
    tone_proc = prof_proc = None
    tone_path = SCRATCH / "r98_tone997.wav"
    if tone:
        if not tone_path.exists():
            make_tone(tone_path)
        tp = subprocess.Popen(["pw-play", "--target", SINK, str(tone_path)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              preexec_fn=_preexec)
        tone_proc = tp
        time.sleep(0.35)
    if profiler:
        pf = open(SCRATCH / f"prof-{name}-r{rep}.json", "wb")
        prof_proc = subprocess.Popen(
            ["pw-profiler", "-J", "-n", "400"], stdout=pf,
            stderr=subprocess.DEVNULL, preexec_fn=_preexec)
        rec["profiler_path"] = str(SCRATCH / f"prof-{name}-r{rep}.json")
        time.sleep(0.3)
    t0 = time.time()
    p = subprocess.Popen([str(PROBE)] + args, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env, preexec_fn=_preexec)
    snap = None
    top = None
    try:
        if live is not None:
            time.sleep(live)
            objs = pw_dump()
            mynode = "r98s_" + (args_name(args) or args[0])
            snap = {"links": links_of(objs, mynode)}
            if snap_pwtop:
                top = sh(["pw-top", "-b", "-n", "3"], timeout=10)
        out, err = p.communicate(timeout=timeout)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        kill_tree(p)
        out, err = p.communicate()
        rc = "timeout"
    wall = int((time.time() - t0) * 1000)
    if tone_proc:
        kill_tree(tone_proc)
    if prof_proc:
        try:
            prof_proc.terminate()
            prof_proc.wait(timeout=6)
        except Exception:
            kill_tree(prof_proc)
    rec.update({"rc": rc, "wall_ms": wall, "utc_end": utc(),
                "stdout_sha": sha(out), "stderr_sha": sha(err),
                "stdout_len": len(out), "stderr_len": len(err),
                "parsed": parse_out(out.decode(errors="replace"))})
    if snap is not None:
        rec["snapshot"] = snap
    if top is not None:
        rec["pwtop"] = parse_pwtop(top["out"].decode(errors="replace"), name)
    if profiler:
        rec["profiler"] = parse_profiler(SCRATCH / f"prof-{name}-r{rep}.json")
    (RAW / f"{name}-r{rep}.out").write_bytes(out)
    (RAW / f"{name}-r{rep}.err").write_bytes(err)
    return rec


def args_name(args):
    for a in args:
        if a.startswith("name="):
            return a.split("=", 1)[1]
    return None


def parse_pwtop(text, legname):
    """Return rows for r98s_* nodes: {name: {state,quant,rate,wait,busy,wq,bq,err,fmt}}"""
    rows = {}
    lines = text.splitlines()
    header = None
    for l in lines:
        if "ERR" in l and "NAME" in l:
            header = l
            continue
        if "r98s" in l:
            parts = l.split()
            if len(parts) >= 6:
                rows.setdefault(parts[-1].lstrip("+").strip(), []).append(parts)
    return {"header": header, "rows": rows}


def parse_profiler(path):
    try:
        txt = Path(path).read_text()
        arr = json.loads(txt) if txt.strip() else []
    except Exception as e:
        return {"error": str(e)}
    fol = [r for r in arr if r.get("type") == "follower" and "r98s" in str(r.get("name"))]
    drv = [r for r in arr if r.get("type") == "driver" and "r98s" in str(r.get("name"))]
    xs = [r["xrun_count"] for r in fol]
    neg_wait = [r for r in fol if (r["awake"] - r["signal"]) < 0]
    return {"records": len(arr), "r98s_follower_records": len(fol),
            "r98s_driver_records": len(drv),
            "follower_xrun_max": max(xs) if xs else None,
            "follower_xrun_last": xs[-1] if xs else None,
            "follower_statuses": sorted(set(r["status"] for r in fol)) if fol else [],
            "follower_negative_wait_records": len(neg_wait),
            "driver_xrun_max": max([r["xrun_count"] for r in drv]) if drv else None}


def make_tone(path):
    import math
    import struct
    fr, dur = 48000, 3
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fr)
        data = bytearray()
        for n in range(fr * dur):
            v = int(0.5 * 32767 * math.sin(2 * math.pi * 997 * n / fr))
            data += struct.pack("<h", v)
        w.writeframes(bytes(data))


def load_sink():
    # unload any stale seat sink first
    short = sh(["pactl", "list", "modules", "short"], timeout=15)
    for line in short["out"].decode(errors="replace").splitlines():
        if "r98s_ns" in line:
            mid = line.split()[0]
            sh(["pactl", "unload-module", mid], timeout=15)
    r = sh(["pactl", "load-module", "module-null-sink", f"sink_name={SINK}",
            "channels=1", "rate=48000",
            "sink_properties=state.restore-props=false,device.description=" + SINK],
           timeout=20)
    mid = r["out"].decode().strip()
    check = sh(["pactl", "list", "modules", "short"], timeout=15)
    row = [l for l in check["out"].decode().splitlines() if l.startswith(mid)]
    assert row and SINK in row[0], f"sink load failed: {r}"
    time.sleep(0.6)
    return mid


def unload_sink(mid):
    short = sh(["pactl", "list", "modules", "short"], timeout=15)
    row = [l for l in short["out"].decode(errors="replace").splitlines()
           if l.startswith(str(mid))]
    assert row and SINK in row[0], f"refusing unload: index {mid} row={row}"
    r = sh(["pactl", "unload-module", str(mid)], timeout=15)
    return {"rc": r["rc"], "err": r["err"].decode(errors="replace")}


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    env_remote_bad = dict(os.environ, PIPEWIRE_REMOTE="r98s_nonexistent")

    entry = census("entry")
    mid = load_sink()
    objs = pw_dump()
    # find sink serial + id
    sink_serial = sink_id = None
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Node"):
            p = o.get("info", {}).get("props", {})
            if p.get("node.name") == SINK:
                sink_serial = p.get("object.serial")
                sink_id = str(o.get("id"))
    assert sink_serial, "sink serial not found"
    legs = []
    P3 = ["run", f"target={SINK}", "flags=autoconnect", "ms=1500"]
    defs = [
        ("info", ["info"], 3, {}),
        ("state", ["state", "ms=900"], 3, {}),
        ("run_autoconnect", P3, 3, {}),
        ("run_no_autoconnect", ["run", "ms=1200"], 3, {}),
        ("dont_reconnect", ["flags", f"target={SINK}", "flags=autoconnect,dont_reconnect", "ms=800"], 3, {}),
        ("dont_reconnect_false_prop", ["props", f"target={SINK}",
            "props=node.dont-reconnect=false", "flags=autoconnect,dont_reconnect", "ms=800"], 3, {}),
        ("inactive_activate", ["flags", f"target={SINK}", "flags=inactive,autoconnect",
            "activate_after=400", "ms=1500"], 3, {}),
        ("trigger", ["flags", f"target={SINK}", "flags=trigger,autoconnect,rt_process",
            "trigger_after=300", "ms=1500"], 3, {}),
        ("rt_process", ["flags", f"target={SINK}", "flags=autoconnect,rt_process", "ms=1200"], 3, {}),
        ("alloc_buffers", ["flags", f"target={SINK}",
            "flags=autoconnect,alloc_buffers", "ms=1200"], 1, {}),
        ("map_buffers", ["flags", f"target={SINK}",
            "flags=autoconnect,map_buffers", "ms=1200"], 1, {}),
        ("exclusive", ["flags", f"target={SINK}", "flags=autoconnect,exclusive", "ms=900"], 1, {}),
        ("driver_flag", ["flags", f"target={SINK}", "flags=driver,autoconnect", "ms=900"], 1, {}),
        ("early_process", ["flags", f"target={SINK}",
            "flags=autoconnect,rt_process,early_process", "ms=1200"], 1, {}),
        ("time", ["time", f"target={SINK}", "flags=autoconnect,rt_process", "ms=1500"], 3, {}),
        ("drain", ["drain", f"target={SINK}", "flags=autoconnect", "ms=2500", "nbuf=5"], 3, {}),
        ("neg", ["neg", f"target={SINK}", "flags=autoconnect,inactive", "ms=900"], 3, {}),
        ("cap_prop", ["cap", "dir=in", f"target={SINK}",
            "props=stream.capture.sink=true", "flags=autoconnect", "ms=1500"], 3, {"tone": True}),
        ("cap_noprop", ["cap", "dir=in", f"target={SINK}", "flags=autoconnect", "ms=1000"], 3, {}),
        ("cap_default_source", ["cap", "dir=in", "flags=autoconnect", "ms=1000"], 1, {}),
        ("err_set_active_pre", ["error", "case=set_active_pre"], 3, {}),
        ("err_connect_twice", ["error", "case=connect_twice"], 3, {}),
        ("err_no_params", ["error", "case=no_params"], 3, {}),
        ("err_bad_direction", ["error", "case=bad_direction"], 3, {}),
        ("err_queue_unowned", ["error", "case=queue_unowned"], 3, {}),
        ("media_class_sink", ["props", f"target={SINK}",
            "props=media.class=Audio/Sink", "flags=autoconnect", "ms=900"], 3, {}),
        ("media_class_source", ["props", f"target={SINK}",
            "props=media.class=Audio/Source", "flags=autoconnect", "ms=900"], 3, {}),
        ("noconvert_44100", ["run", f"target={SINK}",
            "flags=autoconnect,no_convert", "rate=44100", "ms=900"], 3, {}),
        ("convert_44100", ["run", f"target={SINK}",
            "flags=autoconnect", "rate=44100", "ms=900"], 3, {}),
        ("s16_format", ["run", f"target={SINK}", "flags=autoconnect", "fmt=s16", "ms=900"], 1, {}),
        ("target_serial", ["run", f"target={sink_serial}", "flags=autoconnect",
            "ms=1200", "name=tgt_serial"], 3, {"live": 0.7}),
        ("target_object_id", ["run", f"target={sink_id}", "flags=autoconnect",
            "ms=1200", "name=tgt_id"], 3, {"live": 0.7}),
        ("target_garbage", ["run", "target=no_such_r98s", "flags=autoconnect",
            "ms=1200", "name=tgt_bad"], 3, {"live": 0.7}),
        ("stall", ["stall", f"target={SINK}", "flags=autoconnect,rt_process",
            "stall_at=3", "stall_ms=300", "ms=3000"], 3,
         {"profiler": True, "snap_pwtop": True, "live": 0.9}),
        ("remote_bad", ["info"], 3, {"env": env_remote_bad}),
    ]
    FOLLOWUP = [
        ("drain_timer", ["drain", f"target={SINK}", "flags=autoconnect", "ms=2500",
            "drain_at=800"], 3, {}),
        ("neg_stream", ["neg", f"target={SINK}", "flags=autoconnect", "ms=900"], 3, {}),
        ("cap_default_source", ["cap", "dir=in", "flags=autoconnect", "ms=1000"], 3, {}),
        ("stall600", ["stall", f"target={SINK}", "flags=autoconnect,rt_process",
            "stall_at=3", "stall_ms=600", "ms=3000"], 2,
         {"profiler": True, "snap_pwtop": True, "live": 0.9}),
        ("quantum512", ["run", f"target={SINK}", "flags=autoconnect",
            "props=node.force-quantum=512", "ms=1200"], 2, {}),
        ("quantum2048", ["run", f"target={SINK}", "flags=autoconnect",
            "props=node.force-quantum=2048", "ms=1200"], 2, {}),
        ("rt_nice", ["flags", f"target={SINK}", "flags=autoconnect,rt_process", "ms=800"], 1, {}),
    ]
    DRAIN2 = [
        ("drain_cb", ["drain", f"target={SINK}", "flags=autoconnect", "ms=2500", "nbuf=5"], 3, {}),
        ("drain_timer2", ["drain", f"target={SINK}", "flags=autoconnect", "ms=2500",
            "drain_at=800"], 3, {}),
    ]
    if stage == "drain2":
        defs = DRAIN2
    elif stage == "followup":
        defs = FOLLOWUP
    elif stage != "all":
        defs = [d for d in defs if d[0] == stage]
    for (name, args, reps, opts) in defs:
        for rep in range(reps):
            rec = run_leg(name, args, rep=rep, timeout=30, **opts)
            legs.append(rec)
            print(f"{name} r{rep}: rc={rec['rc']} wall={rec['wall_ms']}ms "
                  f"state={rec['parsed'].get('state')} cb={rec['parsed'].get('cb_count')}",
                  flush=True)
    (REC / f"battery-{stage}.json").write_text(json.dumps(legs, indent=1))

    exit_unload = unload_sink(mid)
    exit_census = census("exit")
    summary = {
        "utc": utc(), "stage": stage, "sink_module": mid,
        "sink_serial": sink_serial, "sink_id": sink_id,
        "probe_sha": sha(PROBE.read_bytes()),
        "probe_c_sha": sha((ROOT / "probes" / "r98stream.c").read_bytes()),
        "entry_census": entry, "exit_census": exit_census,
        "unload": exit_unload,
        "defaults": sh(["pactl", "info"], timeout=15)["out"].decode(errors="replace"),
    }
    (REC / f"summary-{stage}.json").write_text(json.dumps(summary, indent=1))
    print("exit census r98s nodes:", exit_census["r98s_nodes"],
          "modules:", exit_census["r98s_modules_pactl"],
          "procs:", exit_census["r98s_procs"])


if __name__ == "__main__":
    main()
