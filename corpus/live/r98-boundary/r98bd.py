#!/usr/bin/env python3
"""r98 boundary driver — replay/attack of the r98-scout native pw_stream laws.

Seat: audio r98 boundary (leaf). Writes only under corpus/live/r98-boundary/.
Namespace r98b_* for every object; only own PIDs are ever signalled (hog pids
are recorded at spawn with their /proc starttime and re-verified before kill);
no namespace-blind sweeps, no `pactl set-default-*`.

Stages:
  quiet   — replay of the scout's armed cells, fresh process per rep, no own load
  load    — same replay with N own CPU hogs alive (>=12), loadavg recorded
  axes    — independent axes: flag order, argv order, env-override precedence
  attack  — targeted attacks on the crash class, drain, routing, capture, xrun
"""
import hashlib
import json
import os
import re
import resource
import signal
import subprocess
import sys
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROBE = ROOT / "probes" / "r98bstream"
RAW = ROOT / "raw"
REC = ROOT / "receipts"
RUNS = ROOT / "runs"
SCRATCH = ROOT / "scratch"
SINK = "r98b_ns"
SINK2 = "r98b_ns2"
for d in (RAW, REC, RUNS, SCRATCH):
    d.mkdir(parents=True, exist_ok=True)

STATE = {"hogs": [], "hog_starttimes": {}}


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha(b):
    return hashlib.sha256(b).hexdigest()


def loadavg():
    return open("/proc/loadavg").read().split()[:3]


def _preexec():
    os.setsid()
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def sh(argv, timeout=25, env=None):
    t0 = time.time()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout, env=env,
                           preexec_fn=_preexec)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = "timeout", e.stdout or b"", e.stderr or b""
    return {"argv": argv, "rc": rc, "out": out, "err": err,
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


# ---------------------------------------------------------------- census ----

def proc_starttime(pid):
    try:
        st = Path(f"/proc/{pid}/stat").read_text()
        # comm may contain spaces/parens: take everything after the last ')'
        return st[st.rindex(")") + 2:].split()[19]
    except Exception:
        return None


def spawn_hogs(n):
    """Spawn n own CPU hogs; record pid+starttime so only own PIDs are killed."""
    for _ in range(n):
        p = subprocess.Popen(["/usr/bin/yes"], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, preexec_fn=_preexec)
        st = proc_starttime(p.pid)
        STATE["hogs"].append(p)
        STATE["hog_starttimes"][p.pid] = st
    return [p.pid for p in STATE["hogs"]]


def kill_hogs():
    killed, refused = [], []
    for p in STATE["hogs"]:
        pid = p.pid
        st_now = proc_starttime(pid)
        comm = Path(f"/proc/{pid}/comm").read_text().strip() if Path(f"/proc/{pid}/comm").exists() else None
        if st_now is not None and st_now == STATE["hog_starttimes"].get(pid) and comm == "yes":
            try:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
                killed.append(pid)
            except Exception as e:
                refused.append([pid, str(e)])
        else:
            refused.append([pid, f"identity mismatch comm={comm} start={st_now}"])
    for p in STATE["hogs"]:
        try:
            p.wait(timeout=5)
        except Exception:
            pass
    return {"killed": killed, "refused": refused}


def pw_dump():
    r = sh(["pw-dump"], timeout=20)
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
                out.append({"id": o.get("id"), "out": on, "in": inn,
                            "out_port": p.get("link.output.port"),
                            "in_port": p.get("link.input.port"),
                            "state": p.get("link.state")})
    return out


def foreign_census(objs):
    """Everything that is NOT mine and that a namespace-blind sweep would hit."""
    yes_rows = []
    ps = sh(["ps", "-eo", "pid,ppid,etimes,args"], timeout=15)
    for l in ps["out"].decode(errors="replace").splitlines():
        toks = l.split()
        if len(toks) >= 4 and toks[3].rsplit("/", 1)[-1] == "yes":
            yes_rows.append(l.strip())
    mine = {p.pid for p in STATE["hogs"]}
    foreign_yes = [l for l in yes_rows if int(l.split()[0]) not in mine]
    sibling_nodes = []
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Node"):
            nm = str(o.get("info", {}).get("props", {}).get("node.name", ""))
            if re.match(r"^r\d+[a-z]*_", nm) or nm.startswith("r9"):
                sibling_nodes.append(nm)
    clients = []
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Client"):
            p = o.get("info", {}).get("props", {})
            clients.append(p.get("application.name") or p.get("application.process.binary"))
    return {"foreign_yes_count": len(foreign_yes),
            "foreign_yes_sample": foreign_yes[:4],
            "foreign_yes_total_rows": len(yes_rows),
            "sibling_looking_nodes": sorted(set(sibling_nodes)),
            "clients": sorted(set(c for c in clients if c))}


def census(tag):
    objs = pw_dump()
    r98b_nodes = []
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Node"):
            p = o.get("info", {}).get("props", {})
            if str(p.get("node.name", "")).startswith("r98b"):
                r98b_nodes.append(p.get("node.name"))
    r98s_nodes = []
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Node"):
            p = o.get("info", {}).get("props", {})
            if str(p.get("node.name", "")).startswith("r98s"):
                r98s_nodes.append(p.get("node.name"))
    pactl = sh(["pactl", "list", "modules", "short"], timeout=20)
    mods = pactl["out"].decode(errors="replace").splitlines()
    r98b_mods = [l for l in mods if "r98b" in l]
    r98s_mods = [l for l in mods if "r98s" in l]
    ps = sh(["ps", "-eo", "pid,args"], timeout=15)
    procs = [l for l in ps["out"].decode(errors="replace").splitlines()
             if "r98bstream" in l]
    sp = Path.home() / ".local/state/wireplumber/stream-properties"
    sp_txt = sp.read_text(errors="replace") if sp.exists() else ""
    info = sh(["pactl", "info"], timeout=20)["out"].decode(errors="replace")
    defaults = {}
    for k in ("Default Sink", "Default Source"):
        for l in info.splitlines():
            if l.startswith(k):
                defaults[k] = l.split(":", 1)[1].strip()
    out = {"utc": utc(), "loadavg": loadavg(), "n_objects": len(objs),
           "r98b_nodes": r98b_nodes, "r98s_nodes_present": r98s_nodes,
           "r98b_modules_pactl": r98b_mods, "r98s_modules_pactl_present": r98s_mods,
           "r98b_procs": procs, "defaults": defaults,
           "stream_properties_r98b_lines": [l for l in sp_txt.splitlines() if "r98b" in l],
           "stream_properties_total_lines": len(sp_txt.splitlines()),
           "foreign": foreign_census(objs)}
    (REC / f"census-{tag}.json").write_text(json.dumps(out, indent=1))
    return out


# ------------------------------------------------------------- leg runner ---

def parse_out(text):
    d, ev = {}, []
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


def args_name(args):
    for a in args:
        if a.startswith("name="):
            return a.split("=", 1)[1]
    return None


def parse_pwtop(text):
    rows = {}
    header = None
    for l in text.splitlines():
        if "ERR" in l and "NAME" in l:
            header = l
            continue
        if "r98b" in l:
            parts = l.split()
            if len(parts) >= 6:
                rows.setdefault(parts[-1].lstrip("+").strip(), []).append(parts)
    return {"header": header, "rows": rows}


def parse_profiler(path, max_records=None):
    try:
        txt = Path(path).read_text()
        arr = json.loads(txt) if txt.strip() else []
    except Exception as e:
        return {"error": str(e)}
    fol = [r for r in arr if r.get("type") == "follower" and "r98b" in str(r.get("name"))]
    drv = [r for r in arr if r.get("type") == "driver"]
    xs = [r["xrun_count"] for r in fol]
    neg = [r for r in fol if (r["awake"] - r["signal"]) < 0]
    return {"records": len(arr), "r98b_follower_records": len(fol),
            "r98b_driver_records": len([r for r in drv if "r98b" in str(r.get("name"))]),
            "follower_xrun_max": max(xs) if xs else None,
            "follower_xrun_last": xs[-1] if xs else None,
            "follower_statuses": sorted(set(r["status"] for r in fol)) if fol else [],
            "follower_negative_wait_records": len(neg),
            "driver_xrun_max": max([r["xrun_count"] for r in drv]) if drv else None,
            "driver_xrun_max_all": max([r["xrun_count"] for r in drv]) if drv else None,
            "n_driver_records": len(drv),
            "other_followers": sorted(set(str(r.get("name")) for r in arr
                                          if r.get("type") == "follower"
                                          and "r98b" not in str(r.get("name"))))[:8]}


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


def run_leg(name, args, rep=0, timeout=40, env=None, live=None, snap_pwtop=False,
            profiler=False, tone=False, tag="", probe=None):
    rec = {"leg": name, "rep": rep, "utc_start": utc(),
           "argv": [str(probe or PROBE)] + args, "loadavg_before": loadavg()}
    if env:
        rec["env_overrides"] = {k: v for k, v in env.items() if k.startswith("PIPEWIRE")}
    tone_proc = prof_proc = None
    tone_path = SCRATCH / "r98b_tone997.wav"
    if tone:
        if not tone_path.exists():
            make_tone(tone_path)
        tp = subprocess.Popen(["pw-play", "--target", SINK, str(tone_path)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              preexec_fn=_preexec)
        tone_proc = tp
        time.sleep(0.4)
    if profiler:
        pf = open(SCRATCH / f"prof-{name}-r{rep}{tag}.json", "wb")
        prof_proc = subprocess.Popen(["pw-profiler", "-J", "-n", "400"], stdout=pf,
                                     stderr=subprocess.DEVNULL, preexec_fn=_preexec)
        rec["profiler_path"] = str(SCRATCH / f"prof-{name}-r{rep}{tag}.json")
        time.sleep(0.35)
    t0 = time.time()
    p = subprocess.Popen([str(probe or PROBE)] + args, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env, preexec_fn=_preexec)
    snap = top = None
    try:
        if live is not None:
            time.sleep(live)
            objs = pw_dump()
            mynode = "r98b_" + (args_name(args) or args[0])
            snap = {"links": links_of(objs, mynode)}
            snap["all_links"] = links_of(objs, mynode)
            if snap_pwtop:
                top = sh(["pw-top", "-b", "-n", "3"], timeout=15)
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
            prof_proc.wait(timeout=8)
        except Exception:
            kill_tree(prof_proc)
    rec.update({"rc": rc, "wall_ms": wall, "utc_end": utc(),
                "loadavg_after": loadavg(),
                "stdout_sha": sha(out), "stderr_sha": sha(err),
                "stdout_len": len(out), "stderr_len": len(err),
                "parsed": parse_out(out.decode(errors="replace"))})
    if snap is not None:
        rec["snapshot"] = snap
    if top is not None:
        rec["pwtop"] = parse_pwtop(top["out"].decode(errors="replace"))
    if profiler:
        rec["profiler"] = parse_profiler(rec["profiler_path"])
    (RAW / f"{name}-r{rep}{tag}.out").write_bytes(out)
    (RAW / f"{name}-r{rep}{tag}.err").write_bytes(err)
    return rec


# ------------------------------------------------------------------ legs ----

def sink_ids():
    objs = pw_dump()
    out = {}
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Node"):
            p = o.get("info", {}).get("props", {})
            if p.get("node.name") in (SINK, SINK2):
                out[p["node.name"]] = {"id": str(o.get("id")),
                                       "serial": p.get("object.serial")}
    return out


def core_legs(ids):
    P3 = ["run", f"target={SINK}", "flags=autoconnect", "ms=1500"]
    return [
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
        ("alloc_buffers", ["flags", f"target={SINK}", "flags=autoconnect,alloc_buffers", "ms=1200"], 1, {}),
        ("map_buffers", ["flags", f"target={SINK}", "flags=autoconnect,map_buffers", "ms=1200"], 1, {}),
        ("exclusive", ["flags", f"target={SINK}", "flags=autoconnect,exclusive", "ms=900"], 1, {}),
        ("driver_flag", ["flags", f"target={SINK}", "flags=driver,autoconnect", "ms=900"], 1, {}),
        ("early_process", ["flags", f"target={SINK}", "flags=autoconnect,rt_process,early_process", "ms=1200"], 1, {}),
        ("time", ["time", f"target={SINK}", "flags=autoconnect,rt_process", "ms=1500"], 3, {}),
        ("drain_cb", ["drain", f"target={SINK}", "flags=autoconnect", "ms=2500", "nbuf=5"], 3, {}),
        ("drain_timer", ["drain", f"target={SINK}", "flags=autoconnect", "ms=2500", "drain_at=800"], 3, {}),
        ("neg_paused", ["neg", f"target={SINK}", "flags=autoconnect,inactive", "ms=900"], 3, {}),
        ("neg_stream", ["neg", f"target={SINK}", "flags=autoconnect", "ms=900"], 3, {}),
        ("cap_prop", ["cap", "dir=in", f"target={SINK}",
            "props=stream.capture.sink=true", "flags=autoconnect", "ms=1500"], 3, {"tone": True}),
        ("cap_noprop", ["cap", "dir=in", f"target={SINK}", "flags=autoconnect", "ms=1000"], 3, {}),
        ("cap_default_source", ["cap", "dir=in", "flags=autoconnect", "ms=1000"], 3, {}),
        ("err_set_active_pre", ["error", "case=set_active_pre"], 3, {}),
        ("err_connect_twice", ["error", "case=connect_twice"], 3, {}),
        ("err_no_params", ["error", "case=no_params"], 3, {}),
        ("err_bad_direction", ["error", "case=bad_direction"], 3, {}),
        ("err_queue_unowned", ["error", "case=queue_unowned"], 3, {}),
        ("media_class_sink", ["props", f"target={SINK}",
            "props=media.class=Audio/Sink", "flags=autoconnect", "ms=900"], 3, {}),
        ("media_class_source", ["props", f"target={SINK}",
            "props=media.class=Audio/Source", "flags=autoconnect", "ms=900"], 3, {}),
        ("noconvert_44100", ["run", f"target={SINK}", "flags=autoconnect,no_convert", "rate=44100", "ms=900"], 3, {}),
        ("convert_44100", ["run", f"target={SINK}", "flags=autoconnect", "rate=44100", "ms=900"], 3, {}),
        ("s16_format", ["run", f"target={SINK}", "flags=autoconnect", "fmt=s16", "ms=900"], 3, {}),
        ("quantum512", ["run", f"target={SINK}", "flags=autoconnect",
            "props=node.force-quantum=512", "ms=1200"], 3, {}),
        ("quantum2048", ["run", f"target={SINK}", "flags=autoconnect",
            "props=node.force-quantum=2048", "ms=1200"], 3, {}),
        ("target_serial", ["run", f"target={ids[SINK]['serial']}", "flags=autoconnect",
            "ms=1200", "name=tgt_serial"], 3, {"live": 0.7}),
        ("target_object_id", ["run", f"target={ids[SINK]['id']}", "flags=autoconnect",
            "ms=1200", "name=tgt_id"], 3, {"live": 0.7}),
        ("target_name", ["run", f"target={SINK}", "flags=autoconnect",
            "ms=1200", "name=tgt_name"], 3, {"live": 0.7}),
        ("target_garbage", ["run", "target=no_such_r98b", "flags=autoconnect",
            "ms=1200", "name=tgt_bad"], 3, {"live": 0.7}),
        ("target_prefix_collide", ["run", f"target={SINK}", "flags=autoconnect",
            "ms=1200", "name=tgt_pref"], 3, {"live": 0.7}),
        ("target_ns2_by_id", ["run", f"target={ids[SINK2]['id']}", "flags=autoconnect",
            "ms=1200", "name=tgt_ns2id"], 3, {"live": 0.7}),
        ("stall300", ["stall", f"target={SINK}", "flags=autoconnect,rt_process",
            "stall_at=3", "stall_ms=300", "ms=3000"], 3,
         {"profiler": True, "snap_pwtop": True, "live": 0.9}),
        ("stall600", ["stall", f"target={SINK}", "flags=autoconnect,rt_process",
            "stall_at=3", "stall_ms=600", "ms=3000"], 2,
         {"profiler": True, "snap_pwtop": True, "live": 0.9}),
        ("remote_bad", ["info"], 3, {"env": dict(os.environ, PIPEWIRE_REMOTE="r98b_nonexistent")}),
    ]


def axis_legs(ids):
    """Independent axes: flag order, argv order, env-override precedence."""
    env_ac_false = dict(os.environ, PIPEWIRE_AUTOCONNECT="false")
    env_ac_true = dict(os.environ, PIPEWIRE_AUTOCONNECT="true")
    env_node = dict(os.environ, PIPEWIRE_NODE=str(ids[SINK]["serial"]))
    env_node_garbage = dict(os.environ, PIPEWIRE_NODE="no_such_r98b_env")
    env_props = dict(os.environ, PIPEWIRE_PROPS="node.dont-reconnect=false")
    env_q512 = dict(os.environ, PIPEWIRE_QUANTUM="512/48000")
    env_q2048 = dict(os.environ, PIPEWIRE_QUANTUM="2048/48000")
    env_lat = dict(os.environ, PIPEWIRE_LATENCY="512/48000")
    return [
        # --- flag order (declared order of the flag list) ---
        ("ord_flags_abc", ["props", f"target={SINK}",
            "flags=autoconnect,dont_reconnect,rt_process", "ms=800"], 3, {}),
        ("ord_flags_cba", ["props", f"target={SINK}",
            "flags=rt_process,dont_reconnect,autoconnect", "ms=800"], 3, {}),
        ("ord_flags_bca", ["props", f"target={SINK}",
            "flags=dont_reconnect,autoconnect,rt_process", "ms=800"], 3, {}),
        # --- argv order ---
        ("ord_argv_fwd", ["run", f"target={SINK}", "flags=autoconnect", "ms=1200", "name=argv_fwd"], 3, {"live": 0.7}),
        ("ord_argv_rev", ["run", "name=argv_rev", "ms=1200", "flags=autoconnect", f"target={SINK}"], 3, {"live": 0.7}),
        # --- env-override precedence (source: stream.c:2142-2160) ---
        ("env_ac_false_over_flag", ["props", f"target={SINK}", "flags=autoconnect", "ms=1200"],
         3, {"env": env_ac_false}),
        ("env_ac_true_without_flag", ["props", f"target={SINK}", "ms=1200"], 3, {"env": env_ac_true}),
        ("env_node_over_garbage_prop", ["run", "target=no_such_r98b", "flags=autoconnect",
            "ms=1200", "name=env_node"], 3, {"env": env_node, "live": 0.7}),
        ("env_node_garbage_over_serial_prop", ["run", f"target={ids[SINK]['serial']}",
            "flags=autoconnect", "ms=1200", "name=env_node_bad"], 3,
         {"env": env_node_garbage, "live": 0.7}),
        ("env_props_false_over_flag", ["props", f"target={SINK}",
            "flags=autoconnect,dont_reconnect", "ms=800"], 3, {"env": env_props}),
        ("env_quantum512", ["run", f"target={SINK}", "flags=autoconnect", "ms=1200"], 3, {"env": env_q512}),
        ("env_quantum2048", ["run", f"target={SINK}", "flags=autoconnect", "ms=1200"], 3, {"env": env_q2048}),
        ("env_latency512", ["run", f"target={SINK}", "flags=autoconnect", "ms=1200"], 3, {"env": env_lat}),
    ]


def attack_legs(ids):
    return [
        # crash class: is it target-specific / rate-specific / inactive-specific?
        ("atk_mcsink_target_null", ["props", f"target={SINK}",
            "props=media.class=Audio/Sink", "flags=autoconnect", "ms=900"], 5, {}),
        ("atk_mcsink_no_target", ["props", "props=media.class=Audio/Sink",
            "flags=autoconnect", "ms=900"], 5, {}),
        ("atk_mcsink_44100", ["props", f"target={SINK}", "props=media.class=Audio/Sink",
            "flags=autoconnect", "rate=44100", "ms=900"], 5, {}),
        ("atk_mcsink_inactive", ["props", f"target={SINK}", "props=media.class=Audio/Sink",
            "flags=autoconnect,inactive", "ms=900"], 3, {}),
        ("atk_mcsink_rt", ["props", f"target={SINK}", "props=media.class=Audio/Sink",
            "flags=autoconnect,rt_process", "ms=900"], 5, {}),
        ("atk_mcsink_serial_target", ["props", f"target={ids[SINK]['serial']}",
            "props=media.class=Audio/Sink", "flags=autoconnect", "ms=900"], 3, {}),
        # drain under a different quantum (period scaling)
        ("atk_drain_q512", ["drain", f"target={SINK}", "flags=autoconnect",
            "props=node.force-quantum=512", "ms=2500", "nbuf=5"], 3, {}),
        ("atk_drain_q2048", ["drain", f"target={SINK}", "flags=autoconnect",
            "props=node.force-quantum=2048", "ms=2500", "nbuf=5"], 3, {}),
        # routing: name resolution with a prefix-colliding node present
        ("atk_target_ns2_name", ["run", f"target={SINK2}", "flags=autoconnect",
            "ms=1200", "name=tgt_ns2"], 3, {"live": 0.7}),
        ("atk_target_serial_ns2", ["run", f"target={ids[SINK2]['serial']}", "flags=autoconnect",
            "ms=1200", "name=tgt_ns2ser"], 3, {"live": 0.7}),
        # time/geometry at the other quantum
        ("atk_time_q512", ["time", f"target={SINK}", "flags=autoconnect,rt_process",
            "props=node.force-quantum=512", "ms=1500"], 3, {}),
        ("atk_run_s16_q512", ["run", f"target={SINK}", "flags=autoconnect",
            "props=node.force-quantum=512", "fmt=s16", "ms=1200"], 3, {}),
    ]


def ext_legs(ids):
    """Extension legs (probe r98bhold, `hold=` option): untruncated observation
    windows for the activation arm and the trigger arm, plus a long cadence run."""
    HOLD = ROOT / "probes" / "r98bhold"
    return [
        ("ext_activate_hold", ["flags", f"target={SINK}", "flags=inactive,autoconnect",
            "activate_after=400", "ms=1500", "hold=1500"], 3, {"probe": HOLD}),
        ("ext_activate_hold_q512", ["flags", f"target={SINK}", "flags=inactive,autoconnect",
            "activate_after=400", "ms=1500", "hold=1500",
            "props=node.force-quantum=512"], 2, {"probe": HOLD}),
        ("ext_trigger_hold", ["flags", f"target={SINK}", "flags=trigger,autoconnect,rt_process",
            "trigger_after=300", "ms=1500", "hold=2000"], 3, {"probe": HOLD}),
        ("ext_run_hold", ["run", f"target={SINK}", "flags=autoconnect",
            "ms=1500", "hold=3000"], 3, {"probe": HOLD}),
        ("ext_run_hold_rt", ["run", f"target={SINK}", "flags=autoconnect,rt_process",
            "ms=1500", "hold=3000"], 2, {"probe": HOLD}),
    ]


def run_stage(stage, legs, tag=""):
    recs = []
    for (name, args, reps, opts) in legs:
        for rep in range(reps):
            rec = run_leg(name, args, rep=rep, tag=tag, **opts)
            recs.append(rec)
            p = rec["parsed"]
            print(f"{name} r{rep}: rc={rec['rc']} wall={rec['wall_ms']}ms "
                  f"state={p.get('state')} cb={p.get('cb_count')} "
                  f"max={p.get('last_maxsize')} load={rec['loadavg_before'][0]}",
                  flush=True)
    out = REC / f"battery-{stage}{tag}.json"
    out.write_text(json.dumps(recs, indent=1))
    return recs


def load_sink(name=SINK):
    short = sh(["pactl", "list", "modules", "short"], timeout=20)
    for line in short["out"].decode(errors="replace").splitlines():
        if name in line:
            mid = line.split()[0]
            sh(["pactl", "unload-module", mid], timeout=20)
    r = sh(["pactl", "load-module", "module-null-sink", f"sink_name={name}",
            "channels=1", "rate=48000",
            "sink_properties=state.restore-props=false,device.description=" + name],
           timeout=25)
    mid = r["out"].decode().strip()
    check = sh(["pactl", "list", "modules", "short"], timeout=20)
    row = [l for l in check["out"].decode().splitlines() if l.startswith(mid)]
    assert row and name in row[0], f"sink load failed: {r}"
    return mid


def unload_sink(mid, name=SINK):
    short = sh(["pactl", "list", "modules", "short"], timeout=20)
    row = [l for l in short["out"].decode(errors="replace").splitlines()
           if l.startswith(str(mid))]
    assert row and name in row[0], f"refusing unload: index {mid} row={row}"
    r = sh(["pactl", "unload-module", str(mid)], timeout=20)
    return {"rc": r["rc"], "err": r["err"].decode(errors="replace")}


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "quiet"
    n_hogs = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    entry = census("entry")
    print("entry foreign:", json.dumps(entry["foreign"])[:400], flush=True)
    mid = load_sink(SINK)
    mid2 = load_sink(SINK2)
    time.sleep(0.8)
    ids = sink_ids()
    assert SINK in ids and SINK2 in ids, f"sink ids missing: {ids}"
    print("ids:", json.dumps(ids), flush=True)

    hog_info = None
    if stage == "load":
        pids = spawn_hogs(n_hogs)
        time.sleep(3)
        hog_info = {"n": n_hogs, "pids": pids, "loadavg_after_spawn": loadavg(),
                    "hog_starttimes": {str(k): v for k, v in STATE["hog_starttimes"].items()}}
        print("hogs:", json.dumps(hog_info)[:300], flush=True)

    t_start = time.time()
    if stage == "quiet":
        legs = core_legs(ids)
    elif stage == "load":
        legs = core_legs(ids)
    elif stage == "axes":
        legs = axis_legs(ids)
    elif stage == "attack":
        legs = attack_legs(ids)
    elif stage == "ext":
        legs = ext_legs(ids)
    else:
        raise SystemExit(f"unknown stage {stage}")
    recs = run_stage(stage, legs, tag="")

    hog_kill = None
    if stage == "load":
        hog_kill = kill_hogs()
        time.sleep(2)
    wall = int(time.time() - t_start)

    exit_unload = [unload_sink(mid, SINK), unload_sink(mid2, SINK2)]
    exit_census = census("exit")
    summary = {"utc": utc(), "stage": stage, "wall_s": wall,
               "probe_sha": sha(PROBE.read_bytes()),
               "probe_c_sha": sha((ROOT / "probes" / "r98bstream.c").read_bytes()),
               "sink_module": mid, "sink2_module": mid2, "ids": ids,
               "hogs": hog_info, "hog_kill": hog_kill,
               "entry_census": entry, "exit_census": exit_census,
               "unload": exit_unload,
               "loadavg_end": loadavg(),
               "n_legs": len(recs)}
    (REC / f"summary-{stage}.json").write_text(json.dumps(summary, indent=1))
    print("exit r98b nodes:", exit_census["r98b_nodes"],
          "modules:", exit_census["r98b_modules_pactl"],
          "procs:", exit_census["r98b_procs"], flush=True)
    print("summary:", json.dumps({k: summary[k] for k in
          ("stage", "wall_s", "n_legs", "loadavg_end")}), flush=True)


if __name__ == "__main__":
    main()
