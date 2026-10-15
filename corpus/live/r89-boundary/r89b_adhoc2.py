#!/usr/bin/env python3
"""r89b ad-hoc part 2: clean suspension test + cross-witness (all seat players killed first)."""
import json
import os
import select
import signal
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs", "adhoc2")
PW = "pw-profiler"
PLYPID = os.path.join(HERE, "r89b_players.pid")


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


def kill_seat_players():
    killed = []
    if not os.path.exists(PLYPID):
        return killed
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


def run_drain(argv, dur, wd, kill_at=None, kill_all_players_at=None):
    os.makedirs(wd, exist_ok=True)
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=wd,
                         stdin=subprocess.DEVNULL)
    os.set_blocking(p.stdout.fileno(), False)
    t0 = time.monotonic()
    buf = b""
    killed = None
    while time.monotonic() - t0 < dur:
        dt = time.monotonic() - t0
        if kill_at and killed is None and dt >= kill_at[0]:
            try:
                os.kill(kill_at[1], signal.SIGKILL)
            except ProcessLookupError:
                pass
            killed = round(dt, 2)
        if kill_all_players_at and killed is None and dt >= kill_all_players_at:
            kill_seat_players()
            killed = round(dt, 2)
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
    return {"rc": p.returncode, "bytes": len(buf), "raw": buf, "killed_at": killed}


def main():
    r = {"t": time.strftime("%H:%M:%S"), "load": loadavg()}
    r["players_killed_pre"] = kill_seat_players()
    time.sleep(0.5)
    r["players_after_kill"] = subprocess.run(["pgrep", "-af", "pw-play"],
                                             capture_output=True, text=True).stdout.split("\n")
    r["sink_states"] = subprocess.run(["pactl", "list", "sinks", "short"],
                                      capture_output=True, text=True).stdout.split("\n")

    # --- clean suspension: one seat player on r89b_ns, killed at t=1.0
    player = subprocess.Popen(["pw-play", "--target", "r89b_ns",
                               os.path.join(HERE, "r89b_tone48.wav")],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    res = run_drain([PW, "-J", "-n", "0"], 3.0, os.path.join(RUNS, "susp", "wd"),
                    kill_at=(1.0, player.pid))
    bl = blocks(res["raw"])
    own = [b for b in bl if b["driver"] and b["driver"][0].get("name") == "r89b_ns"]
    others = [b for b in bl if b["driver"] and b["driver"][0].get("name") != "r89b_ns"]
    counts = [b["info"]["count"] for b in own]
    r["suspension_clean"] = {
        "rc": res["rc"], "killed_at": res["killed_at"], "total_blocks": len(bl),
        "own_blocks": len(own),
        "own_first": counts[0] if counts else None, "own_last": counts[-1] if counts else None,
        "own_span": (counts[-1] - counts[0]) if counts else None,
        "own_quantum": own[0]["clock"][0].get("duration") if own and own[0]["clock"] else None,
        "other_blocks": len(others),
        "other_drivers": sorted(set(b["driver"][0]["name"] for b in others if b["driver"])),
    }
    try:
        os.kill(player.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass

    # --- cross-witness: pw-top (3 frames) concurrently with a 2 s profiler run on r89b_ns44
    player2 = subprocess.Popen(["pw-play", "--target", "r89b_ns44", "--rate", "44100",
                                os.path.join(HERE, "r89b_tone44.wav")],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    top = subprocess.Popen(["pw-top", "-b", "-n", "3"], stdout=subprocess.PIPE, text=True)
    res2 = run_drain([PW, "-J", "-n", "0"], 2.0, os.path.join(RUNS, "xw", "wd"))
    top_out = top.communicate(timeout=10)[0]
    bl2 = blocks(res2["raw"])
    prof = None
    for b in bl2:
        if b["driver"] and b["driver"][0].get("name") == "r89b_ns44":
            d0 = b["driver"][0]
            prof = {"awake_minus_signal_us": round((d0.get("awake", 0) - d0.get("signal", 0)) / 1000, 2),
                    "finish_minus_awake_us": round((d0.get("finish", 0) - d0.get("awake", 0)) / 1000, 2)}
            break
    rows = [l.rstrip() for l in top_out.split("\n") if "r89b_ns44" in l]
    r["cross_witness"] = {"top_rows": rows, "profiler_first_block": prof, "load": loadavg()}
    try:
        os.kill(player2.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    json.dump(r, open(os.path.join(HERE, "receipts", "adhoc2.json"), "w"), indent=1)
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
