#!/usr/bin/env python3
"""r89b boundary harness - falsification of the r89 scout claims under load.

Namespace: every audio object created here is r89b_*. All writes stay under
corpus/live/r89-boundary/. No tracked-file writes, no commits.

Usage: python3 r89b_probe.py <stage> [stage...]
Stages: state idle driver schema jsig oart load cleanup
"""
import hashlib
import json
import os
import resource
import signal
import subprocess
import sys
import time
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
RECS = os.path.join(HERE, "receipts")
TONE48 = os.path.join(HERE, "r89b_tone48.wav")
TONE44 = os.path.join(HERE, "r89b_tone44.wav")
HOGPID = os.path.join(HERE, "r89b_hogs.pid")
PLYPID = os.path.join(HERE, "r89b_players.pid")
MODPID = os.path.join(HERE, "r89b_modules.json")
os.makedirs(RUNS, exist_ok=True)
os.makedirs(RECS, exist_ok=True)
PW = "pw-profiler"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def loadavg():
    try:
        return open("/proc/loadavg").read().split()[:3]
    except OSError:
        return []


def _nofile():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def pactl_short(kind):
    r = subprocess.run(["pactl", "list", kind, "short"], capture_output=True, text=True)
    lines = r.stdout.split("\n")
    body = lines[:-1] if lines and lines[-1] == "" else lines
    ids, blanks = [], []
    for i, l in enumerate(body):
        if l.strip() == "":
            blanks.append(i + 1)
        else:
            tok = l.split()[0]
            if tok.isdigit():
                ids.append(tok)
    return {"ids": ids, "blanks": blanks, "rc": r.returncode, "raw": r.stdout}


def module_line(idx):
    r = subprocess.run(["pactl", "list", "modules", "short"], capture_output=True, text=True)
    for l in r.stdout.split("\n"):
        t = l.split()
        if t and t[0] == str(idx):
            return l
    return None


def parse_j(raw):
    if not raw.strip():
        return {"ok": False, "err": "empty"}
    try:
        arr = json.loads(raw)
    except Exception as e:
        return {"ok": False, "err": str(e)}
    if not isinstance(arr, list):
        return {"ok": False, "err": "not a list"}
    return {"ok": True, "n": len(arr),
            "last_is_empty_obj": (arr[-1] == {}) if arr else None,
            "types_head": [r.get("type") for r in arr[:12]]}


def blocks(raw):
    """Walk a -J record array into per-cycle blocks (info starts a block)."""
    try:
        arr = json.loads(raw)
    except Exception:
        return None
    out, cur = [], None
    for r in arr:
        if not isinstance(r, dict) or not r:
            continue
        t = r.get("type")
        if t == "info":
            if cur:
                out.append(cur)
            cur = {"info": r, "clock": [], "driver": [], "follower": [],
                   "followerClock": [], "other": []}
        elif cur is not None and t in cur:
            cur[t].append(r)
        elif cur is not None:
            cur["other"].append(r)
    if cur:
        out.append(cur)
    return out


def driver_info(raw):
    bl = blocks(raw)
    if bl is None:
        return None
    return {"n_blocks": len(bl),
            "drivers": [{"id": b["driver"][0].get("id"), "name": b["driver"][0].get("name"),
                         "xrun_count": b["driver"][0].get("xrun_count")}
                        for b in bl if b["driver"]],
            "follower_clock_blocks": sum(1 for b in bl if b["followerClock"]),
            "counts": [b["info"].get("count") for b in bl]}


def leg(stage, label, argv, timeout=10.0, sig=None, sig_after=None, env=None,
        stdout_file=None, cwd_extra=None, drain=False):
    import select
    d = os.path.join(RUNS, stage, label)
    wd = os.path.join(d, "wd")
    os.makedirs(wd, exist_ok=True)
    e = dict(os.environ)
    if env:
        e.update(env)
    so = open(stdout_file, "wb") if stdout_file else subprocess.PIPE
    t0 = time.monotonic()
    p = subprocess.Popen(argv, stdout=so, stderr=subprocess.PIPE, cwd=wd, env=e,
                         preexec_fn=_nofile, stdin=subprocess.DEVNULL)
    if drain:
        os.set_blocking(p.stdout.fileno(), False)
    drained = b""
    sig_at = None
    outer_kill = False
    while True:
        dt = time.monotonic() - t0
        if sig is not None and sig_after is not None and sig_at is None and dt >= sig_after:
            try:
                p.send_signal(sig)
            except ProcessLookupError:
                pass
            sig_at = round(dt, 3)
        if dt >= timeout:
            try:
                p.send_signal(signal.SIGKILL)
            except ProcessLookupError:
                pass
            outer_kill = True
            break
        if p.poll() is not None:
            break
        if drain:
            r, _, _ = select.select([p.stdout], [], [], 0.01)
            if r:
                drained += p.stdout.read() or b""
        else:
            time.sleep(0.005)
    try:
        out, err = p.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
    if stdout_file:
        out = b""
    out = drained + out
    wall = time.monotonic() - t0
    wd_files = {}
    for f in sorted(os.listdir(wd)):
        fp = os.path.join(wd, f)
        if os.path.isfile(fp):
            b = open(fp, "rb").read()
            wd_files[f] = {"size": len(b), "sha": sha(b)}
    meta = {"stage": stage, "label": label, "cmd": argv, "rc": p.returncode,
            "wall_s": round(wall, 3), "sig_at": sig_at, "outer_kill": outer_kill,
            "stdout_len": len(out), "stderr_len": len(err),
            "stdout_sha": sha(out), "stderr_sha": sha(err),
            "stdout_head": out[:240].decode("utf-8", "replace"),
            "stderr_tail": err[-400:].decode("utf-8", "replace"),
            "wd_files": wd_files, "load": loadavg()}
    if "-J" in argv:
        meta["parse"] = parse_j(out)
        meta["drv"] = driver_info(out)
    open(os.path.join(d, "stdout.bin"), "wb").write(out)
    open(os.path.join(d, "stderr.txt"), "wb").write(err)
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
    print(f"[{stage}/{label}] rc={meta['rc']} wall={meta['wall_s']} out={len(out)}B "
          f"err={len(err)}B kill={outer_kill} {meta.get('parse', '')}")
    return meta


def cycle_sensor(label):
    """0.8 s bound: does ANY driver emit a cycle right now?"""
    out, ok = b"", False
    try:
        r = subprocess.run([PW, "-J", "-n", "1"], capture_output=True, timeout=0.8)
        out, ok = r.stdout, r.returncode == 0
    except subprocess.TimeoutExpired as ex:
        out = ex.stdout or b""
    names, cyc = [], None
    try:
        for rec in json.loads(out):
            if rec.get("type") == "driver":
                names.append(rec.get("name"))
            if rec.get("type") == "clock":
                cyc = rec.get("cycle")
    except Exception:
        pass
    s = {"label": label, "completed": ok, "n_bytes": len(out), "drivers": names,
         "cycle": cyc, "load": loadavg(), "t": time.strftime("%H:%M:%S")}
    print("  sensor", s)
    return s


def graph_snapshot():
    try:
        d = json.loads(subprocess.run(["pw-dump"], capture_output=True, text=True).stdout)
    except Exception:
        d = []
    nodes = []
    for o in d:
        if o.get("type", "").endswith("Node"):
            p = (o.get("info", {}) or {}).get("props", {}) or {}
            nodes.append({"id": o["id"], "name": p.get("node.name"),
                          "driver": p.get("node.driver"), "class": p.get("media.class")})
    return {"n_objects": len(d), "nodes": nodes, "load": loadavg()}


def pwtop2():
    r = subprocess.run(["pw-top", "-b", "-n", "2"], capture_output=True, text=True)
    rows = []
    for l in r.stdout.split("\n"):
        t = l.split()
        if len(t) > 3 and t[0] in ("S", "I", "R", "C", "E", "H", "A") and t[1].isdigit():
            rows.append(l.rstrip())
    return {"raw": r.stdout, "rows": rows}


def gen_tone(path, rate, secs, freq=1000.0):
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return
    try:
        import numpy as np
        t = np.arange(rate * secs, dtype=np.float64) / rate
        x = (0.25 * 32767 * np.sin(2 * np.pi * freq * t)).astype("<i2")
        data = x.tobytes()
    except Exception:
        import math
        import struct
        amp = 0.25 * 32767
        data = b"".join(struct.pack("<h", int(amp * math.sin(2 * math.pi * freq * i / rate)))
                        for i in range(rate * secs))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data)


def start_player(target, wav, extra=None, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    argv = ["pw-play", "--target", target] + (extra or []) + [wav]
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=e)
    pids = []
    if os.path.exists(PLYPID):
        pids = [int(x) for x in open(PLYPID).read().split()]
    pids.append(p.pid)
    open(PLYPID, "w").write("\n".join(map(str, pids)))
    return p


def kill_players():
    if not os.path.exists(PLYPID):
        return []
    killed = []
    for pid in [int(x) for x in open(PLYPID).read().split()]:
        try:
            comm = open(f"/proc/{pid}/comm").read().strip()
        except OSError:
            continue
        if comm == "pw-play":
            try:
                os.kill(pid, signal.SIGKILL)
                killed.append(pid)
            except ProcessLookupError:
                pass
    os.remove(PLYPID)
    return killed


def hog_start(n):
    pids = []
    for _ in range(n):
        p = subprocess.Popen(["yes"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pids.append(p.pid)
    open(HOGPID, "w").write("\n".join(map(str, pids)))
    return pids


def hog_stop():
    if not os.path.exists(HOGPID):
        return []
    killed = []
    for pid in [int(x) for x in open(HOGPID).read().split()]:
        try:
            comm = open(f"/proc/{pid}/comm").read().strip()
        except OSError:
            continue
        if comm == "yes":
            try:
                os.kill(pid, signal.SIGKILL)
                killed.append(pid)
            except ProcessLookupError:
                pass
    os.remove(HOGPID)
    return killed


def load_sink(name, props=None, extra=None):
    args = ["pactl", "load-module", "module-null-sink", f"sink_name={name}"]
    if props:
        args.append(f"sink_properties={props}")
    if extra:
        args.extend(extra)
    r = subprocess.run(args, capture_output=True, text=True)
    idx = r.stdout.strip()
    mods = {}
    if os.path.exists(MODPID):
        mods = json.load(open(MODPID))
    mods[idx] = name
    json.dump(mods, open(MODPID, "w"), indent=1)
    return idx, r.returncode, r.stderr.strip()


def unload_verified(idx, name):
    line = module_line(idx)
    if line and f"sink_name={name}" in line:
        r = subprocess.run(["pactl", "unload-module", str(idx)], capture_output=True, text=True)
        return {"ok": r.returncode == 0, "line": line, "rc": r.returncode, "err": r.stderr.strip()}
    return {"ok": False, "line": line, "reason": "line does not match sink_name=" + name}


def node_id_by_name(name):
    snap = graph_snapshot()
    for n in snap["nodes"]:
        if n["name"] == name:
            return n["id"]
    return None


def stream_timing(stage, label, argv, reads=(0.5, 1.0, 1.5, 2.0, 2.5), timeout=8.0):
    import select
    d = os.path.join(RUNS, stage, label)
    wd = os.path.join(d, "wd")
    os.makedirs(wd, exist_ok=True)
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=wd,
                         preexec_fn=_nofile, stdin=subprocess.DEVNULL)
    os.set_blocking(p.stdout.fileno(), False)
    t0 = time.monotonic()
    buf = b""
    checkpoints = []
    first_byte_t = None
    idx = 0
    while time.monotonic() - t0 < timeout:
        dt = time.monotonic() - t0
        r, _, _ = select.select([p.stdout], [], [], 0.02)
        if r:
            chunk = p.stdout.read() or b""
            if chunk:
                buf += chunk
                if first_byte_t is None:
                    first_byte_t = round(dt, 3)
        while idx < len(reads) and dt >= reads[idx]:
            checkpoints.append({"t": reads[idx], "bytes": len(buf)})
            idx += 1
        if p.poll() is not None:
            break
    try:
        out, err = p.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
    buf += out
    wall = time.monotonic() - t0
    meta = {"label": label, "cmd": argv, "rc": p.returncode, "wall_s": round(wall, 3),
            "checkpoints": checkpoints, "first_byte_t": first_byte_t,
            "total_bytes": len(buf), "parse": parse_j(buf), "load": loadavg()}
    open(os.path.join(d, "stdout.bin"), "wb").write(buf)
    open(os.path.join(d, "stderr.txt"), "wb").write(err)
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
    print(f"[{stage}/{label}] stream {meta['checkpoints']} first_byte={first_byte_t} rc={p.returncode}")
    return meta


def concurrent_pair(stage, label, argv, stagger=0.0, timeout=8.0, env=None):
    d = os.path.join(RUNS, stage, label)
    wd = os.path.join(d, "wd")
    os.makedirs(wd, exist_ok=True)
    e = dict(os.environ)
    if env:
        e.update(env)
    p1 = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=wd,
                          env=e, preexec_fn=_nofile, stdin=subprocess.DEVNULL)
    if stagger:
        time.sleep(stagger)
    p2 = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=wd,
                          env=e, preexec_fn=_nofile, stdin=subprocess.DEVNULL)
    o1, e1 = p1.communicate(timeout=timeout)
    o2, e2 = p2.communicate(timeout=timeout)
    b1, b2 = blocks(o1), blocks(o2)
    common, equal, nsec_diff = 0, 0, 0
    if b1 and b2:
        def key(b):
            if not b["driver"]:
                return None
            return (b["driver"][0].get("name"), b["info"].get("count"))
        m1 = {key(b): b for b in b1 if key(b)}
        m2 = {key(b): b for b in b2 if key(b)}
        for k in set(m1) & set(m2):
            common += 1
            if m1[k] == m2[k]:
                equal += 1
            elif m1[k]["clock"] and m2[k]["clock"] and \
                    m1[k]["clock"][0].get("nsec") != m2[k]["clock"][0].get("nsec"):
                nsec_diff += 1
    meta = {"label": label, "cmd": argv, "stagger": stagger,
            "a": {"rc": p1.returncode, "len": len(o1), "sha": sha(o1)},
            "b": {"rc": p2.returncode, "len": len(o2), "sha": sha(o2)},
            "byte_identical": sha(o1) == sha(o2),
            "parse_a": parse_j(o1), "parse_b": parse_j(o2),
            "common_count_keys": common, "dict_equal_blocks": equal,
            "nsec_mismatch_blocks": nsec_diff,
            "drv_a": driver_info(o1), "drv_b": driver_info(o2), "load": loadavg()}
    open(os.path.join(d, "a.bin"), "wb").write(o1)
    open(os.path.join(d, "b.bin"), "wb").write(o2)
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
    print(f"[{stage}/{label}] identical={meta['byte_identical']} a={len(o1)}B b={len(o2)}B "
          f"common={common} equal={equal} nsec_diff={nsec_diff}")
    return meta


def receipt(name, obj):
    json.dump(obj, open(os.path.join(RECS, name + ".json"), "w"), indent=1)
    print("receipt", name, "written")


def stage_state():
    r = {"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "load": loadavg()}
    r["git_head"] = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                   capture_output=True, text=True,
                                   cwd="/home/vgpnk/Projects/shokunin/audio-shokunin").stdout.strip()
    r["git_status"] = subprocess.run(["git", "status", "--short"],
                                     capture_output=True, text=True,
                                     cwd="/home/vgpnk/Projects/shokunin/audio-shokunin").stdout.split("\n")[:12]
    r["modules"] = pactl_short("modules")
    r["module_lines"] = [l for l in r["modules"]["raw"].split("\n") if l.split() and l.split()[0].isdigit()]
    r["sinks"] = pactl_short("sinks")
    r["sources"] = pactl_short("sources")
    r["blank_census"] = {k: {"blanks": pactl_short(k)["blanks"], "n_ids": len(pactl_short(k)["ids"])}
                         for k in ["modules", "cards", "sinks", "sources", "clients", "samples"]}
    r["graph"] = graph_snapshot()
    r["pwtop"] = pwtop2()
    r["pw_cli_info5"] = subprocess.run(["pw-cli", "info", "5"], capture_output=True, text=True).__dict__.get(
        "stderr", "") or subprocess.run(["pw-cli", "info", "5"], capture_output=True, text=True).stderr
    ci = subprocess.run(["pw-cli", "info", "5"], capture_output=True, text=True)
    ep = subprocess.run(["pw-cli", "enum-params", "5", "Props"], capture_output=True, text=True)
    r["profiler_obj"] = {"info_rc": ci.returncode, "info_stderr": ci.stderr.strip(),
                         "enum_rc": ep.returncode, "enum_stderr": ep.stderr.strip()}
    r["profiler_module_args"] = subprocess.run(["pactl", "list", "modules"], capture_output=True,
                                               text=True).stdout.split("libpipewire-module-profiler")[1][:200]
    r["procs"] = subprocess.run(["pgrep", "-af", "pw-play|pw-profiler|pw-top|pw-record|pw-cat"],
                                capture_output=True, text=True).stdout.split("\n")
    r["hogs_own"] = subprocess.run(["pgrep", "-c", "^yes$"], capture_output=True, text=True).stdout.strip()
    receipt("state", r)
    return r


def stage_idle():
    r = {"t": time.strftime("%H:%M:%S"), "sensors": [], "legs": {}}
    r["sensors"].append(cycle_sensor("pre"))
    # verbatim scout legs: idle -n N>0 SIGKILL
    for n in (1, 2, 3, 8):
        for rep in range(3):
            m = leg("idle", f"j_n{n}_kill_r{rep}", [PW, "-J", "-n", str(n)], timeout=3.0)
            r["legs"][f"j_n{n}_kill_r{rep}"] = m
        r["sensors"].append(cycle_sensor(f"after_n{n}"))
    # -n 0 SIGINT/SIGTERM -> [{ } ]
    for sname, s in (("int", signal.SIGINT), ("term", signal.SIGTERM)):
        for rep in range(3):
            r["legs"][f"j_n0_{sname}_r{rep}"] = leg(
                "idle", f"j_n0_{sname}_r{rep}", [PW, "-J", "-n", "0"],
                timeout=6.0, sig=s, sig_after=2.5)
    # bad -n on idle (scout: silent hang)
    for v in ("-1", "abc", "2.5"):
        for rep in range(2):
            r["legs"][f"j_n_{v}_kill_r{rep}"] = leg(
                "idle", f"j_n_{v}_kill_r{rep}", [PW, "-J", "-n", v], timeout=2.5)
    # plain -o eager 0-byte, SIGKILL husk
    for rep in range(2):
        r["legs"][f"plain_n4_kill_r{rep}"] = leg(
            "idle", f"plain_n4_kill_r{rep}", [PW, "-n", "4"], timeout=2.5)
        r["legs"][f"o_n4_kill_r{rep}"] = leg(
            "idle", f"o_n4_kill_r{rep}", [PW, "-o", "idle_o", "-n", "4"], timeout=2.5)
    # plain -o graceful idle: 0-byte file, no aux
    for sname, s in (("int", signal.SIGINT), ("term", signal.SIGTERM)):
        for rep in range(2):
            r["legs"][f"o_n4_{sname}_r{rep}"] = leg(
                "idle", f"o_n4_{sname}_r{rep}", [PW, "-o", "idle_o", "-n", "4"],
                timeout=6.0, sig=s, sig_after=2.5)
    # unstated signals on idle -J
    for sname, s in (("hup", signal.SIGHUP), ("quit", signal.SIGQUIT),
                     ("usr1", signal.SIGUSR1), ("usr2", signal.SIGUSR2)):
        for rep in range(2):
            r["legs"][f"j_n4_{sname}_r{rep}"] = leg(
                "idle", f"j_n4_{sname}_r{rep}", [PW, "-J", "-n", "4"],
                timeout=6.0, sig=s, sig_after=2.5)
    # refusal lattice
    for rep in range(3):
        r["legs"][f"remote_bogus_r{rep}"] = leg(
            "idle", f"remote_bogus_r{rep}", [PW, "-r", "r89b_no_such_remote", "-J", "-n", "2"], timeout=5.0)
        r["legs"][f"opt_bogus_r{rep}"] = leg(
            "idle", f"opt_bogus_r{rep}", [PW, "--r89bbogus"], timeout=5.0)
        r["legs"][f"out_unwritable_r{rep}"] = leg(
            "idle", f"out_unwritable_r{rep}", [PW, "-o", "/proc/r89b/x", "-n", "2"], timeout=5.0)
    for rep in range(2):
        r["legs"][f"remote_empty_r{rep}"] = leg(
            "idle", f"remote_empty_r{rep}", [PW, "-r", "", "-J", "-n", "2"], timeout=2.5)
        r["legs"][f"extra_arg_r{rep}"] = leg(
            "idle", f"extra_arg_r{rep}", [PW, "-J", "-n", "2", "extrapositional"], timeout=2.5)
    # unstated env-var remote
    for rep in range(2):
        r["legs"][f"env_remote_bogus_r{rep}"] = leg(
            "idle", f"env_remote_bogus_r{rep}", [PW, "-J", "-n", "1"],
            timeout=2.5, env={"PIPEWIRE_REMOTE": "r89b_bogus_env"})
        r["legs"][f"env_remote_pw0_r{rep}"] = leg(
            "idle", f"env_remote_pw0_r{rep}", [PW, "-J", "-n", "1"],
            timeout=2.5, env={"PIPEWIRE_REMOTE": "pipewire-0"})
    # named canonical remote
    for rep in range(2):
        r["legs"][f"remote_named_r{rep}"] = leg(
            "idle", f"remote_named_r{rep}", [PW, "-r", "pipewire-0", "-J", "-n", "1"], timeout=2.5)
    # unstated option forms
    r["legs"]["n_repeat"] = leg("idle", "n_repeat", [PW, "-J", "-n", "4", "-n", "0"],
                                timeout=6.0, sig=signal.SIGINT, sig_after=2.5)
    r["legs"]["j_repeat"] = leg("idle", "j_repeat", [PW, "-J", "-J", "-n", "4"],
                                timeout=6.0, sig=signal.SIGINT, sig_after=2.5)
    r["legs"]["dashdash"] = leg("idle", "dashdash", [PW, "-J", "-n", "2", "--"],
                                timeout=2.5)
    r["legs"]["version"] = leg("idle", "version", [PW, "--version"], timeout=5.0)
    r["legs"]["help"] = leg("idle", "help", [PW, "-h"], timeout=5.0)
    r["sensors"].append(cycle_sensor("post"))
    receipt("idle", r)
    return r


def stage_driver():
    r = {"t": time.strftime("%H:%M:%S"), "load": loadavg()}
    gen_tone(TONE48, 48000, 90)
    gen_tone(TONE44, 44100, 90)
    idx, rc, err = load_sink("r89b_ns")
    r["load_ns"] = {"idx": idx, "rc": rc, "err": err, "line": module_line(idx)}
    idx44, rc44, err44 = load_sink("r89b_ns44", extra=["rate=44100"])
    r["load_ns44"] = {"idx": idx44, "rc": rc44, "err": err44, "line": module_line(idx44)}
    r["node_ns"] = node_id_by_name("r89b_ns")
    r["node_ns44"] = node_id_by_name("r89b_ns44")
    p1 = start_player("r89b_ns", TONE48)
    p2 = start_player("r89b_ns44", TONE44, extra=["--rate", "44100"])
    r["player_pids"] = [p1.pid, p2.pid]
    time.sleep(0.8)
    r["sensor_drv"] = cycle_sensor("drv")
    r["legs"] = {}
    for rep in range(3):
        r["legs"][f"n1_r{rep}"] = leg("driver", f"n1_r{rep}", [PW, "-J", "-n", "1"], timeout=5.0)
        r["legs"][f"n8_r{rep}"] = leg("driver", f"n8_r{rep}", [PW, "-J", "-n", "8"], timeout=8.0)
    for rep in range(2):
        r["legs"][f"n40_r{rep}"] = leg("driver", f"n40_r{rep}", [PW, "-J", "-n", "40"], timeout=12.0)
    # two-driver completion: -n 4 should be fast (scout e4)
    for rep in range(2):
        r["legs"][f"two_drv_n4_r{rep}"] = leg("driver", f"two_drv_n4_r{rep}", [PW, "-J", "-n", "4"], timeout=6.0)
    # bad/edge -n on a LIVE driver: this is where atoi semantics are measurable
    live_cases = [
        ("float_2p5", ["-n", "2.5"], "complete2", 3.0, None),
        ("zero_007", ["-n", "007"], "complete7", 3.0, None),
        ("plus3", ["-n", "+3"], "complete3", 3.0, None),
        ("space3", ["-n", " 3"], "complete3", 3.0, None),
        ("suffix_3abc", ["-n", "3abc"], "complete3", 3.0, None),
        ("sci_1e1", ["-n", "1e1"], "complete1", 3.0, None),
        ("ovf_2p32p2", ["-n", "4294967298"], "intcast2", 3.0, None),
        ("ovf_neg", ["-n", "-4294967294"], "intcast2", 3.0, None),
        ("ovf_2p32", ["-n", "4294967296"], "intcast0", 3.0, signal.SIGINT),
        ("ovf_huge", ["-n", "99999999999999999999"], "clamp?", 3.0, signal.SIGINT),
        ("ovf_huge_neg", ["-n", "-99999999999999999999"], "clamp?", 3.0, signal.SIGINT),
        ("neg1", ["-n", "-1"], "unbounded", 2.5, signal.SIGINT),
        ("abc", ["-n", "abc"], "unbounded", 2.5, signal.SIGINT),
        ("zero", ["-n", "0"], "unbounded", 2.5, signal.SIGINT),
    ]
    for label, nargs, expect, tmo, s in live_cases:
        for rep in range(2):
            r["legs"][f"badn_{label}_r{rep}"] = leg(
                "driver", f"badn_{label}_r{rep}", [PW, "-J"] + nargs,
                timeout=tmo, sig=s, sig_after=(2.0 if s else None))
    receipt("driver", r)
    return r


def stage_schema():
    r = {"t": time.strftime("%H:%M:%S"), "load": loadavg(), "legs": {}}
    # count persistence across client attaches on the live r89b_ns driver
    seq = []
    for i in range(3):
        m = leg("schema", f"persist_{i}", [PW, "-J", "-n", "30"], timeout=10.0)
        seq.append(m)
        time.sleep(1.5)
    r["persist_seq"] = seq
    r["persist_counts"] = []
    for m in seq:
        bl = blocks(open(os.path.join(RUNS, "schema", m["label"], "stdout.bin"), "rb").read())
        r["persist_counts"].append(
            [{"count": b["info"].get("count"), "drv": b["driver"][0].get("name") if b["driver"] else None}
             for b in (bl or [])])
    # fresh sink starts at 0?
    idx, rc, err = load_sink("r89b_ns_b")
    r["load_ns_b"] = {"idx": idx, "rc": rc, "err": err}
    pb = start_player("r89b_ns_b", TONE48)
    r["player_b_pid"] = pb.pid
    time.sleep(0.8)
    m = leg("schema", "fresh_b_n5", [PW, "-J", "-n", "15"], timeout=10.0)
    bl = blocks(open(os.path.join(RUNS, "schema", "fresh_b_n5", "stdout.bin"), "rb").read())
    r["fresh_b_counts"] = [{"count": b["info"].get("count"),
                            "drv": b["driver"][0].get("name") if b["driver"] else None}
                           for b in (bl or [])]
    r["fresh_b_leg"] = m
    # invariant windows
    for rep in range(3):
        r["legs"][f"schema_n60_r{rep}"] = leg("schema", f"schema_n60_r{rep}",
                                              [PW, "-J", "-n", "60"], timeout=12.0)
    # analysis of invariants over every block captured in this stage
    inv = {"blocks_total": 0, "blocks_own": 0, "order_violations": [], "pos_step_violations": [],
           "nsec_quantum_violations": [], "count_step_violations": [], "transport_stopped_false": [],
           "diff_values": {}, "xrun_nonzero": [], "follower_clock_rows": 0,
           "cpu_load_sorted": 0, "cpu_load_unsorted": 0}
    for rep in range(3):
        raw = open(os.path.join(RUNS, "schema", f"schema_n60_r{rep}", "stdout.bin"), "rb").read()
        bl = blocks(raw) or []
        inv["blocks_total"] += len(bl)
        last_count = {}
        for b in bl:
            if not b["driver"] or not b["clock"]:
                continue
            d0 = b["driver"][0]
            c0 = b["clock"][0]
            if d0.get("name") == "r89b_ns":
                inv["blocks_own"] += 1
            # timing chain
            if not (d0.get("prev", 0) <= d0.get("signal", 0) <= d0.get("awake", 0) <= d0.get("finish", 0)):
                inv["order_violations"].append({k: d0.get(k) for k in ("prev", "signal", "awake", "finish")})
            for f in b["follower"]:
                if not (f.get("prev", 0) <= f.get("signal", 0) <= f.get("awake", 0) <= f.get("finish", 0)):
                    inv["order_violations"].append({"follower": f.get("name"),
                                                    **{k: f.get(k) for k in ("prev", "signal", "awake", "finish")}})
            # position step
            key = d0.get("name")
            if key in last_count:
                pc, pp = last_count[key]
                if c0.get("position", 0) - pp != c0.get("duration", 0):
                    inv["pos_step_violations"].append({"drv": key, "delta": c0.get("position", 0) - pp,
                                                       "duration": c0.get("duration")})
                if b["info"].get("count") - pc != 1:
                    inv["count_step_violations"].append({"drv": key, "prev": pc,
                                                         "now": b["info"].get("count")})
            last_count[key] = (b["info"].get("count"), c0.get("position", 0))
            # quantum: next_nsec - nsec == duration * 1e9 / rate
            rate = c0.get("rate", "1/48000")
            try:
                num, den = [int(x) for x in rate.split("/")]
                expect = c0["duration"] * den * 1_000_000_000 // num if False else c0["duration"] * 1_000_000_000 * num // den
            except Exception:
                expect = None
            if expect is not None and c0.get("next_nsec") is not None:
                if c0["next_nsec"] - c0["nsec"] != expect:
                    inv["nsec_quantum_violations"].append({"got": c0["next_nsec"] - c0["nsec"],
                                                           "expect": expect, "rate": rate})
            if c0.get("transport") != "stopped":
                inv["transport_stopped_false"].append(c0.get("transport"))
            inv["diff_values"].setdefault(str(c0.get("diff")), 0)
            inv["diff_values"][str(c0.get("diff"))] += 1
            for row in [d0] + b["follower"]:
                if row.get("xrun_count"):
                    inv["xrun_nonzero"].append({"name": row.get("name"), "xrun_count": row.get("xrun_count")})
            if c0.get("xrun"):
                inv["xrun_nonzero"].append({"clock_id": c0.get("id"), "xrun": c0.get("xrun")})
            inv["follower_clock_rows"] += len(b["followerClock"])
            info = b["info"]
            loads = [info.get("cpu_load0"), info.get("cpu_load1"), info.get("cpu_load2")]
            if all(x is not None for x in loads):
                if loads == sorted(loads, reverse=True):
                    inv["cpu_load_sorted"] += 1
                else:
                    inv["cpu_load_unsorted"] += 1
    r["invariants"] = inv
    receipt("schema", r)
    return r


def stage_jsig():
    r = {"t": time.strftime("%H:%M:%S"), "load": loadavg(), "legs": {}}
    r["players"] = restart_players()
    time.sleep(0.5)
    # graceful stop with live data
    for sname, s in (("int", signal.SIGINT), ("term", signal.SIGTERM)):
        for rep in range(3):
            r["legs"][f"j_n0_{sname}_r{rep}"] = leg(
                "jsig", f"j_n0_{sname}_r{rep}", [PW, "-J", "-n", "0"],
                timeout=6.0, sig=s, sig_after=1.5, drain=True)
    # SIGKILL mid-run: truncated invalid JSON
    for rep in range(3):
        r["legs"][f"j_n0_kill_r{rep}"] = leg(
            "jsig", f"j_n0_kill_r{rep}", [PW, "-J", "-n", "0"], timeout=1.5)
    # unstated signals with live data
    for sname, s in (("hup", signal.SIGHUP), ("quit", signal.SIGQUIT),
                     ("usr1", signal.SIGUSR1), ("usr2", signal.SIGUSR2)):
        for rep in range(2):
            r["legs"][f"j_n0_{sname}_r{rep}"] = leg(
                "jsig", f"j_n0_{sname}_r{rep}", [PW, "-J", "-n", "0"],
                timeout=6.0, sig=s, sig_after=1.5, drain=True)
    # -o fully ignored under -J
    for rep in range(3):
        r["legs"][f"j_o_ignored_r{rep}"] = leg(
            "jsig", f"j_o_ignored_r{rep}", [PW, "-o", "jsig_o", "-J", "-n", "0"],
            timeout=6.0, sig=signal.SIGINT, sig_after=1.5, drain=True)
    # stream timing (lazy '[' and block buffering)
    stream_timing("jsig", "stream_n0", [PW, "-J", "-n", "0"], timeout=3.0,
                  reads=(0.25, 0.5, 0.75, 1.0, 1.5, 2.0))
    # concurrency: simultaneous and staggered
    for rep in range(3):
        r["legs"][f"conc_sim_r{rep}"] = concurrent_pair(
            "jsig", f"conc_sim_r{rep}", [PW, "-J", "-n", "8"], timeout=10.0)
    for rep in range(2):
        r["legs"][f"conc_stagger_r{rep}"] = concurrent_pair(
            "jsig", f"conc_stagger_r{rep}", [PW, "-J", "-n", "8"], stagger=0.4, timeout=10.0)
    # stdout write-error paths (unstated)
    r["legs"]["devfull"] = leg("jsig", "devfull", [PW, "-J", "-n", "0"],
                               timeout=6.0, sig=signal.SIGINT, sig_after=1.5,
                               stdout_file="/dev/full")
    # closed pipe (SIGPIPE) - handled inline
    d = os.path.join(RUNS, "jsig", "closed_pipe")
    os.makedirs(os.path.join(d, "wd"), exist_ok=True)
    p = subprocess.Popen([PW, "-J", "-n", "0"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=os.path.join(d, "wd"),
                         preexec_fn=_nofile, stdin=subprocess.DEVNULL)
    time.sleep(1.0)
    p.stdout.close()  # reader goes away -> child gets EPIPE/SIGPIPE on next write
    time.sleep(0.5)
    if p.poll() is None:
        p.send_signal(signal.SIGINT)
    try:
        _, err = p.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()
        _, err = p.communicate()
    r["legs"]["closed_pipe"] = {"rc": p.returncode, "stderr_tail": err[-200:].decode("utf-8", "replace")}
    print("[jsig/closed_pipe]", r["legs"]["closed_pipe"])
    # TTY: is '[' lazy on a tty too, and when do bytes appear?
    r["tty"] = tty_probe()
    receipt("jsig", r)
    return r


def tty_probe():
    import pty
    import select
    d = os.path.join(RUNS, "jsig", "tty")
    os.makedirs(os.path.join(d, "wd"), exist_ok=True)
    mfd, sfd = pty.openpty()
    p = subprocess.Popen([PW, "-J", "-n", "0"], stdout=sfd, stderr=sfd,
                         cwd=os.path.join(d, "wd"), preexec_fn=_nofile,
                         stdin=subprocess.DEVNULL)
    os.close(sfd)
    t0 = time.monotonic()
    buf = b""
    first = None
    while time.monotonic() - t0 < 2.0:
        rr, _, _ = select.select([mfd], [], [], 0.05)
        if rr:
            try:
                c = os.read(mfd, 4096)
            except OSError:
                break
            if c:
                buf += c
                if first is None:
                    first = round(time.monotonic() - t0, 3)
        if p.poll() is not None:
            break
    p.send_signal(signal.SIGINT)
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()
    while True:
        rr, _, _ = select.select([mfd], [], [], 0.1)
        if not rr:
            break
        try:
            c = os.read(mfd, 4096)
        except OSError:
            break
        if not c:
            break
        buf += c
    os.close(mfd)
    meta = {"rc": p.returncode, "bytes": len(buf), "first_byte_t": first,
            "repr_head": repr(buf[:120]), "load": loadavg()}
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
    open(os.path.join(d, "tty_out.bin"), "wb").write(buf)
    print("[jsig/tty]", meta)
    return meta


def stage_oart():
    r = {"t": time.strftime("%H:%M:%S"), "load": loadavg(), "legs": {}}
    r["players"] = restart_players()
    time.sleep(0.5)
    r["legs"]["o_n20_grace"] = leg("oart", "o_n20_grace", [PW, "-o", "o_art", "-n", "20"], timeout=12.0)
    for sname, s in (("int", signal.SIGINT), ("term", signal.SIGTERM)):
        for rep in range(2):
            r["legs"][f"o_n0_{sname}_r{rep}"] = leg(
                "oart", f"o_n0_{sname}_r{rep}", [PW, "-o", "o_int", "-n", "0"],
                timeout=6.0, sig=s, sig_after=2.0, drain=True)
    for rep in range(2):
        r["legs"][f"o_n0_kill_r{rep}"] = leg(
            "oart", f"o_n0_kill_r{rep}", [PW, "-o", "o_kill", "-n", "0"], timeout=1.5)
    # existing file: truncate or append?
    d = os.path.join(RUNS, "oart", "o_existing")
    wd = os.path.join(d, "wd")
    os.makedirs(wd, exist_ok=True)
    open(os.path.join(wd, "o_exist"), "w").write("R89B_MARKER_" + "X" * 100 + "\n")
    r["legs"]["o_existing"] = leg("oart", "o_existing", [PW, "-o", "o_exist", "-n", "10"], timeout=10.0)
    # odd -o targets (unstated)
    for label, target in (("o_dir", "."), ("o_empty", ""), ("o_devnull", "/dev/null"),
                          ("o_devstdout", "/dev/stdout"), ("o_dash", "-")):
        r["legs"][label] = leg("oart", label, [PW, "-o", target, "-n", "10"], timeout=10.0)
    for rep in range(3):
        r["legs"][f"o_proc_r{rep}"] = leg("oart", f"o_proc_r{rep}", [PW, "-o", "/proc/r89b/x", "-n", "2"], timeout=5.0)
    r["legs"]["plain_default"] = leg("oart", "plain_default", [PW, "-n", "10"], timeout=10.0)
    receipt("oart", r)
    return r


def stage_load():
    r = {"t": time.strftime("%H:%M:%S"), "load_pre": loadavg(), "legs": {}, "hog_pids": []}
    r["hog_pids"] = hog_start(32)
    time.sleep(1.0)
    r["load_hogged"] = loadavg()
    try:
        r["sensor"] = cycle_sensor("load")
        for rep in range(2):
            r["legs"][f"load_n40_r{rep}"] = leg("load", f"load_n40_r{rep}", [PW, "-J", "-n", "40"], timeout=15.0)
        for rep in range(2):
            r["legs"][f"load_schema_n60_r{rep}"] = leg("load", f"load_schema_n60_r{rep}",
                                                       [PW, "-J", "-n", "60"], timeout=15.0)
        for rep in range(2):
            r["legs"][f"load_conc_r{rep}"] = concurrent_pair(
                "load", f"load_conc_r{rep}", [PW, "-J", "-n", "8"], timeout=12.0)
        r["top_xw"] = pwtop2()
        r["graph"] = graph_snapshot()
        # xrun induction attempts: try small quantum via PIPEWIRE_QUANTUM env on the player
        kill_players()
        r["legs"]["xrun_q64"] = xrun_attempt(r, "q64", {"PIPEWIRE_QUANTUM": "64"})
        r["legs"]["xrun_q32"] = xrun_attempt(r, "q32", {"PIPEWIRE_QUANTUM": "32"})
        r["load_post"] = loadavg()
    finally:
        r["hogs_killed"] = hog_stop()
    receipt("load", r)
    return r


def xrun_attempt(r, label, env):
    """Restart the driver player with a quantum env, run a long profiler leg, look for xruns."""
    out = {"env": env}
    p = start_player("r89b_ns", TONE48, env=env)
    out["player_pid"] = p.pid
    time.sleep(0.8)
    m = leg("load", f"xrun_{label}", [PW, "-J", "-n", "120"], timeout=12.0)
    out["leg"] = m
    raw = open(os.path.join(RUNS, "load", f"xrun_{label}", "stdout.bin"), "rb").read()
    bl = blocks(raw) or []
    quanta, xr = set(), []
    for b in bl:
        if b["clock"]:
            quanta.add((b["clock"][0].get("duration"), b["clock"][0].get("rate")))
        for row in b["driver"] + b["follower"]:
            if row.get("xrun_count"):
                xr.append({"name": row.get("name"), "xrun_count": row.get("xrun_count")})
        if b["clock"] and b["clock"][0].get("xrun"):
            xr.append({"clock": b["clock"][0].get("id"), "xrun": b["clock"][0].get("xrun")})
    out["quanta_seen"] = sorted(str(q) for q in quanta)
    out["xruns"] = xr
    out["top"] = pwtop2()
    kill_players()
    return out


def stage_cleanup():
    r = {"t": time.strftime("%H:%M:%S"), "load_pre": loadavg()}
    r["players_killed"] = kill_players()
    r["hogs_killed"] = hog_stop()
    r["unloads"] = {}
    if os.path.exists(MODPID):
        mods = json.load(open(MODPID))
        for idx, name in mods.items():
            if name.startswith("r89b_"):
                r["unloads"][f"{idx}:{name}"] = unload_verified(idx, name)
    r["modules_after"] = pactl_short("modules")["ids"]
    snap = graph_snapshot()
    r["r89b_nodes_after"] = [n for n in snap["nodes"] if n["name"] and "r89b" in str(n["name"])]
    r["pgrep_r89b"] = [l for l in subprocess.run(
        ["pgrep", "-af", "r89b"], capture_output=True, text=True).stdout.split("\n") if l and "pgrep" not in l]
    r["load_post"] = loadavg()
    r["git_status"] = subprocess.run(["git", "status", "--short"], capture_output=True, text=True,
                                     cwd="/home/vgpnk/Projects/shokunin/audio-shokunin").stdout.split("\n")
    receipt("cleanup", r)
    return r


def proc_state(pid):
    try:
        st = open(f"/proc/{pid}/stat").read().split()
        state = st[2]
    except OSError:
        state = None
    try:
        wchan = open(f"/proc/{pid}/wchan").read()
    except OSError:
        wchan = None
    return {"state": state, "wchan": wchan}


def bp_leg(label, sig, mode, signal_at=1.2, settle=1.5):
    """Backpressure probe: mode='drain' reads stdout concurrently; 'nodrain' doesn't
    read until after the signal, then drains to see whether the flush completes."""
    import select
    d = os.path.join(RUNS, "bp", label)
    wd = os.path.join(d, "wd")
    os.makedirs(wd, exist_ok=True)
    p = subprocess.Popen([PW, "-J", "-n", "0"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=wd, preexec_fn=_nofile,
                         stdin=subprocess.DEVNULL)
    os.set_blocking(p.stdout.fileno(), False)
    t0 = time.monotonic()
    buf = b""
    pre_state = pre_wchan = None
    exited_before_drain = None
    if mode == "drain":
        while time.monotonic() - t0 < signal_at:
            r, _, _ = select.select([p.stdout], [], [], 0.02)
            if r:
                buf += p.stdout.read() or b""
        pre_state = proc_state(p.pid)
        p.send_signal(sig)
        sig_at = round(time.monotonic() - t0, 3)
        while time.monotonic() - t0 < signal_at + settle:
            r, _, _ = select.select([p.stdout], [], [], 0.02)
            if r:
                buf += p.stdout.read() or b""
            if p.poll() is not None:
                break
    else:
        time.sleep(signal_at)
        pre_state = proc_state(p.pid)
        p.send_signal(sig)
        sig_at = round(time.monotonic() - t0, 3)
        t_sig = time.monotonic()
        exited_before_drain = False
        while time.monotonic() - t_sig < settle:
            if p.poll() is not None:
                exited_before_drain = True
                break
            time.sleep(0.02)
        # drain now: does the pending flush complete?
        t_drain = time.monotonic()
        while time.monotonic() - t_drain < 2.5:
            r, _, _ = select.select([p.stdout], [], [], 0.02)
            if r:
                buf += p.stdout.read() or b""
            if p.poll() is not None:
                break
        if p.poll() is None:
            p.send_signal(signal.SIGKILL)
    try:
        out, err = p.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
    buf += out
    wall = time.monotonic() - t0
    meta = {"label": label, "mode": mode, "signal": sig.name, "rc": p.returncode,
            "sig_at": sig_at, "wall_s": round(wall, 3), "bytes": len(buf),
            "state_at_signal": pre_state, "exited_before_drain": exited_before_drain,
            "parse": parse_j(buf), "stderr_len": len(err),
            "load": loadavg()}
    open(os.path.join(d, "stdout.bin"), "wb").write(buf)
    open(os.path.join(d, "stderr.txt"), "wb").write(err)
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
    print(f"[bp/{label}] sig={sig.name} mode={mode} rc={meta['rc']} bytes={len(buf)} "
          f"state={pre_state} exited_before_drain={exited_before_drain} {meta['parse']}")
    return meta


def stage_bp():
    r = {"t": time.strftime("%H:%M:%S"), "load": loadavg(), "legs": {}}
    for sname, s in (("int", signal.SIGINT), ("term", signal.SIGTERM)):
        r["legs"][f"drain_{sname}"] = bp_leg(f"drain_{sname}", s, "drain")
        r["legs"][f"nodrain_{sname}"] = bp_leg(f"nodrain_{sname}", s, "nodrain")
    for sname, s in (("hup", signal.SIGHUP), ("quit", signal.SIGQUIT),
                     ("usr1", signal.SIGUSR1), ("usr2", signal.SIGUSR2)):
        r["legs"][f"drain_{sname}"] = bp_leg(f"drain_{sname}", s, "drain")
        r["legs"][f"nodrain_{sname}"] = bp_leg(f"nodrain_{sname}", s, "nodrain")
    r["legs"]["nodrain_kill"] = bp_leg("nodrain_kill", signal.SIGKILL, "nodrain")
    receipt("bp", r)
    return r


def stage_idlewatch():
    r = {"t": time.strftime("%H:%M:%S"), "attempts": [], "catches": []}
    for i in range(90):
        out, ok = b"", False
        p = subprocess.Popen([PW, "-J", "-n", "1"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, preexec_fn=_nofile,
                             stdin=subprocess.DEVNULL)
        try:
            out, _ = p.communicate(timeout=1.0)
            ok = p.returncode == 0
        except subprocess.TimeoutExpired:
            p.kill()
            out, _ = p.communicate()
        names = []
        try:
            for rec in json.loads(out):
                if rec.get("type") == "driver":
                    names.append(rec.get("name"))
        except Exception:
            pass
        r["attempts"].append({"i": i, "completed": ok, "bytes": len(out), "drivers": names,
                              "t": time.strftime("%H:%M:%S")})
        if ok:
            time.sleep(0.2)
            continue
        print(f"  idle window at attempt {i}!")
        c = {"i": i, "t": time.strftime("%H:%M:%S"), "legs": {}}
        c["legs"]["n3_kill"] = leg("idlewatch", f"c{i}_n3_kill", [PW, "-J", "-n", "3"], timeout=2.0)
        c["legs"]["n0_int"] = leg("idlewatch", f"c{i}_n0_int", [PW, "-J", "-n", "0"],
                                  timeout=4.0, sig=signal.SIGINT, sig_after=1.5)
        c["legs"]["n0_term"] = leg("idlewatch", f"c{i}_n0_term", [PW, "-J", "-n", "0"],
                                   timeout=4.0, sig=signal.SIGTERM, sig_after=1.5)
        c["legs"]["o_eager_kill"] = leg("idlewatch", f"c{i}_o_eager_kill",
                                        [PW, "-o", "catch_o", "-n", "4"], timeout=1.5)
        c["legs"]["plain_kill"] = leg("idlewatch", f"c{i}_plain_kill", [PW, "-n", "4"], timeout=1.5)
        c["top"] = pwtop2()
        c["sensor_after"] = cycle_sensor(f"c{i}_after")
        r["catches"].append(c)
        if len(r["catches"]) >= 2:
            break
    receipt("idlewatch", r)
    return r


def restart_players():
    ps = []
    if node_id_by_name("r89b_ns") is not None:
        ps.append(start_player("r89b_ns", TONE48))
    if node_id_by_name("r89b_ns44") is not None:
        ps.append(start_player("r89b_ns44", TONE44, extra=["--rate", "44100"]))
    return [p.pid for p in ps]


def stage_schema2():
    """Invariant window with the seat's own drivers demonstrably live."""
    r = {"t": time.strftime("%H:%M:%S"), "load": loadavg(), "legs": {}}
    r["players"] = restart_players()
    time.sleep(0.8)
    r["sensor"] = cycle_sensor("schema2")
    for rep in range(3):
        r["legs"][f"s2_n90_r{rep}"] = leg("schema2", f"s2_n90_r{rep}", [PW, "-J", "-n", "90"],
                                          timeout=15.0, drain=True)
    inv = {"own_blocks": 0, "own_drivers": {}, "pos_step_violations": [],
           "nsec_delta_violations": [], "count_step_violations": [],
           "order_violations": [], "diff_own": {}, "xrun_own": [],
           "follower_clock_rows": 0, "blocks_total": 0}
    for rep in range(3):
        raw = open(os.path.join(RUNS, "schema2", f"s2_n90_r{rep}", "stdout.bin"), "rb").read()
        bl = blocks(raw) or []
        inv["blocks_total"] += len(bl)
        last = {}
        for b in bl:
            if not b["driver"] or not b["clock"]:
                continue
            d0, c0 = b["driver"][0], b["clock"][0]
            nm = d0.get("name")
            inv["own_drivers"][nm] = inv["own_drivers"].get(nm, 0) + 1
            if not nm.startswith("r89b"):
                continue
            inv["own_blocks"] += 1
            if not (d0.get("prev", 0) <= d0.get("signal", 0) <= d0.get("awake", 0) <= d0.get("finish", 0)):
                inv["order_violations"].append({k: d0.get(k) for k in ("prev", "signal", "awake", "finish")})
            if nm in last:
                pc, pp, pq = last[nm]
                if c0.get("position", 0) - pp != c0.get("duration", 0):
                    inv["pos_step_violations"].append({"drv": nm, "delta": c0.get("position", 0) - pp,
                                                       "duration": c0.get("duration"), "prev_dur": pq})
                if b["info"].get("count") - pc != 1:
                    inv["count_step_violations"].append({"drv": nm, "prev": pc, "now": b["info"].get("count")})
                rate = c0.get("rate", "1/48000")
                num, den = [int(x) for x in rate.split("/")]
                expect = c0["duration"] * 1_000_000_000 * num // den
                got = c0.get("next_nsec", 0) - c0.get("nsec", 0)
                if got != expect:
                    inv["nsec_delta_violations"].append({"drv": nm, "got": got, "expect": expect})
            last[nm] = (b["info"].get("count"), c0.get("position", 0), c0.get("duration"))
            inv["diff_own"].setdefault(nm, {})
            inv["diff_own"][nm][str(c0.get("diff"))] = inv["diff_own"][nm].get(str(c0.get("diff")), 0) + 1
            for row in [d0] + b["follower"]:
                if row.get("xrun_count"):
                    inv["xrun_own"].append({"name": row.get("name"), "xrun_count": row.get("xrun_count")})
            if c0.get("xrun"):
                inv["xrun_own"].append({"clock": nm, "xrun": c0.get("xrun")})
            inv["follower_clock_rows"] += len(b["followerClock"])
    r["invariants"] = inv
    receipt("schema2", r)
    return r


def stage_xrun():
    """Quantum/xrun probe under hogs, with a draining reader (no backpressure)."""
    r = {"t": time.strftime("%H:%M:%S"), "load_pre": loadavg(), "legs": {}}
    r["hog_pids"] = hog_start(32)
    time.sleep(1.0)
    r["load_hogged"] = loadavg()
    try:
        kill_players()
        for label, env in (("q64", {"PIPEWIRE_QUANTUM": "64"}),
                           ("q32", {"PIPEWIRE_QUANTUM": "32"}),
                           ("q128", {"PIPEWIRE_QUANTUM": "128"}),
                           ("ctrl", {})):
            x = {"env": env}
            p = start_player("r89b_ns", TONE48, env=env)
            x["player_pid"] = p.pid
            time.sleep(0.8)
            m = leg("xrun", f"x_{label}", [PW, "-J", "-n", "120"], timeout=12.0, drain=True)
            x["leg"] = m
            raw = open(os.path.join(RUNS, "xrun", f"x_{label}", "stdout.bin"), "rb").read()
            bl = blocks(raw) or []
            quanta, xr, nsec_deltas = set(), [], []
            last_nsec = {}
            for b in bl:
                if b["clock"]:
                    c = b["clock"][0]
                    quanta.add((c.get("duration"), c.get("rate")))
                    nm = b["driver"][0].get("name") if b["driver"] else "?"
                    if nm in last_nsec:
                        nsec_deltas.append(c.get("nsec", 0) - last_nsec[nm])
                    last_nsec[nm] = c.get("nsec", 0)
                    if c.get("xrun"):
                        xr.append({"drv": nm, "clock_xrun": c.get("xrun")})
                for row in b["driver"] + b["follower"]:
                    if row.get("xrun_count"):
                        xr.append({"name": row.get("name"), "xrun_count": row.get("xrun_count")})
            x["quanta_seen"] = sorted(str(q) for q in quanta)
            x["xruns"] = xr[:8]
            x["n_xrun_rows"] = len(xr)
            x["own_blocks"] = sum(1 for b in bl if b["driver"] and b["driver"][0].get("name") == "r89b_ns")
            x["nsec_delta_sample"] = nsec_deltas[:5]
            x["top"] = pwtop2()
            kill_players()
            r["legs"][label] = x
    finally:
        r["hogs_killed"] = hog_stop()
    r["load_post"] = loadavg()
    receipt("xrun", r)
    return r


STAGES = {"state": stage_state, "idle": stage_idle, "driver": stage_driver,
          "schema": stage_schema, "jsig": stage_jsig, "oart": stage_oart,
          "load": stage_load, "cleanup": stage_cleanup, "bp": stage_bp,
          "idlewatch": stage_idlewatch, "schema2": stage_schema2, "xrun": stage_xrun}

if __name__ == "__main__":
    for s in sys.argv[1:]:
        print("=" * 20, s, "=" * 20)
        STAGES[s]()
