#!/usr/bin/env python3
"""r89b ad-hoc probes: eager -o file, profiler footprint, driver suspension, cross-witness."""
import json
import os
import select
import signal
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs", "adhoc")
PW = "pw-profiler"


def blocks(raw):
    try:
        arr = json.loads(raw)
    except Exception:
        return []
    out, cur = [], None
    for r in arr:
        if not isinstance(r, dict) or not r:
            continue
        t = r.get("type")
        if t == "info":
            if cur:
                out.append(cur)
            cur = {"info": r, "clock": [], "driver": [], "follower": [], "followerClock": []}
        elif cur is not None and t in cur:
            cur[t].append(r)
    if cur:
        out.append(cur)
    return out


def loadavg():
    return open("/proc/loadavg").read().split()[:3]


def drain_run(argv, dur, wd, kill_pid_at=None):
    """Run argv for dur seconds with a draining reader; optionally kill a pid at t."""
    os.makedirs(wd, exist_ok=True)
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=wd,
                         stdin=subprocess.DEVNULL)
    os.set_blocking(p.stdout.fileno(), False)
    t0 = time.monotonic()
    buf = b""
    killed = False
    while time.monotonic() - t0 < dur:
        dt = time.monotonic() - t0
        if kill_pid_at and not killed and dt >= kill_pid_at[0]:
            try:
                os.kill(kill_pid_at[1], signal.SIGKILL)
            except ProcessLookupError:
                pass
            killed = True
        r, _, _ = select.select([p.stdout], [], [], 0.01)
        if r:
            buf += p.stdout.read() or b""
    p.send_signal(signal.SIGINT)
    try:
        out, err = p.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
    buf += out
    return {"rc": p.returncode, "bytes": len(buf), "raw": buf, "stderr_len": len(err)}


def main():
    r = {"t": time.strftime("%H:%M:%S"), "load": loadavg()}
    # --- 1. eager -o file + footprint during a live run
    wd = os.path.join(RUNS, "eager", "wd")
    os.makedirs(wd, exist_ok=True)
    p = subprocess.Popen([PW, "-o", "eager_x", "-n", "0"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=wd, stdin=subprocess.DEVNULL)
    os.set_blocking(p.stdout.fileno(), False)
    time.sleep(0.15)
    f = os.path.join(wd, "eager_x")
    r["eager_at_150ms"] = {"exists": os.path.exists(f),
                           "size": os.path.getsize(f) if os.path.exists(f) else None}
    time.sleep(0.35)
    try:
        dump = json.loads(subprocess.run(["pw-dump"], capture_output=True, text=True).stdout)
    except Exception:
        dump = []
    clients = [o for o in dump if o.get("type") == "PipeWire:Interface:Client"]
    prof_clients = []
    for o in clients:
        pr = (o.get("info", {}) or {}).get("props", {}) or {}
        if pr.get("application.name") == "pw-profiler":
            prof_clients.append({"id": o["id"], "pid": pr.get("application.process.id")})
    nodes = [o for o in dump if o.get("type") == "PipeWire:Interface:Node"]
    mods = [o for o in dump if o.get("type") == "PipeWire:Interface:Module"]
    r["footprint"] = {"n_objects": len(dump), "n_clients": len(clients),
                      "profiler_clients": prof_clients,
                      "n_nodes": len(nodes), "n_modules": len(mods),
                      "r89b_nodes": [((o.get("info", {}) or {}).get("props", {}) or {}).get("node.name")
                                     for o in nodes
                                     if "r89b" in str(((o.get("info", {}) or {}).get("props", {}) or {}).get("node.name"))]}
    time.sleep(0.7)
    p.send_signal(signal.SIGINT)
    try:
        out, err = p.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
    r["eager_final"] = {"rc": p.returncode, "size": os.path.getsize(f),
                        "stderr_tail": err[-120:].decode("utf-8", "replace")}

    # --- 2. driver suspension: kill the player mid-run, watch own-driver counts freeze
    player = subprocess.Popen(["pw-play", "--target", "r89b_ns", os.path.join(HERE, "r89b_tone48.wav")],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.6)
    wd2 = os.path.join(RUNS, "suspension", "wd")
    res = drain_run([PW, "-J", "-n", "0"], 3.0, wd2, kill_pid_at=(1.0, player.pid))
    bl = blocks(res["raw"])
    own = [b for b in bl if b["driver"] and b["driver"][0].get("name") == "r89b_ns"]
    other = [b for b in bl if b["driver"] and b["driver"][0].get("name") != "r89b_ns"]
    own_counts = [b["info"]["count"] for b in own]
    r["suspension"] = {"rc": res["rc"], "total_blocks": len(bl), "own_blocks": len(own),
                       "own_count_first": own_counts[0] if own_counts else None,
                       "own_count_last": own_counts[-1] if own_counts else None,
                       "own_count_span": (own_counts[-1] - own_counts[0]) if own_counts else None,
                       "other_blocks": len(other),
                       "other_drivers": sorted(set(b["driver"][0]["name"] for b in other if b["driver"]))}
    try:
        os.kill(player.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass

    # --- 3. cross-witness: pw-top WAIT/BUSY vs profiler awake-signal/finish-awake
    player2 = subprocess.Popen(["pw-play", "--target", "r89b_ns44", os.path.join(HERE, "r89b_tone44.wav"),
                                "--rate", "44100"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.6)
    top = subprocess.Popen(["pw-top", "-b", "-n", "2"], stdout=subprocess.PIPE, text=True)
    wd3 = os.path.join(RUNS, "xw", "wd")
    res2 = drain_run([PW, "-J", "-n", "0"], 2.0, wd3)
    top_out = top.communicate(timeout=10)[0]
    rows = [l.rstrip() for l in top_out.split("\n") if "r89b_ns44" in l]
    xw = {"top_rows": rows, "load": loadavg()}
    bl2 = blocks(res2["raw"])
    for b in bl2:
        if b["driver"] and b["driver"][0].get("name") == "r89b_ns44":
            d0 = b["driver"][0]
            xw["profiler"] = {"awake_minus_signal_ns": d0.get("awake", 0) - d0.get("signal", 0),
                              "finish_minus_awake_ns": d0.get("finish", 0) - d0.get("awake", 0)}
            break
    r["cross_witness"] = xw
    try:
        os.kill(player2.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    json.dump(r, open(os.path.join(HERE, "receipts", "adhoc.json"), "w"), indent=1)
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
