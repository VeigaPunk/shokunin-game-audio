#!/usr/bin/env python3
"""r89 edge legs — scout-finisher addendum to r89_probe.py.

Edges the main probe does not declare, same pw-profiler surface:
  E1 timing_live:   is -J stdout streamed per-iteration or dump-on-exit?
  E2 kill_live:     SIGKILL mid-run with data pending -> total loss?
  E3 concurrent:    two -J clients on one live driver — broadcast or not?
  E4 two_drivers:   -n semantics with 2 driver domains (which cycles count,
                    how many clock/driver rows per iteration)?
  E5 remote_named:  -r pipewire-0 accepted as remote name?
Every mutating leg uses seat-owned r89edge_* sinks, unloaded by index
verified against sink_name (r90 by-name-unload landmine honored).
Receipts: runs_edge/<leg>/rep*/{cmd,stdout.bin,stderr.txt,meta.json},
consolidated receipts/s-edge.json.
"""
import json
import os
import signal
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs_edge"
REC = ROOT / "receipts"
TONE = ROOT / "r89_tone.wav"
RUNS.mkdir(parents=True, exist_ok=True)
REC.mkdir(parents=True, exist_ok=True)


def sha(b):
    import hashlib
    return hashlib.sha256(b).hexdigest()


def leg_dir(leg, rep):
    wd = RUNS / leg / f"rep{rep}"
    (wd / "wd").mkdir(parents=True, exist_ok=True)
    return wd


def write_meta(wd, meta):
    (wd / "meta.json").write_text(json.dumps(meta, indent=1))


def pactl(*a):
    return subprocess.run(["pactl", *a], capture_output=True, text=True,
                          timeout=15)


class Sink:
    """Seat-owned null sink, unloaded by verified index."""

    def __init__(self, name, rate=48000):
        self.name = name
        self.rate = rate
        self.idx = None
        ld = pactl("load-module", "module-null-sink",
                   f"sink_name={name}", f"rate={rate}", "channels=2")
        self.load_rc = ld.returncode
        idx = ld.stdout.strip()
        if ld.returncode == 0 and idx.isdigit():
            self.idx = idx
            for _ in range(50):
                if name in pactl("list", "sinks", "short").stdout:
                    break
                time.sleep(0.1)

    def close(self):
        out = {"idx": self.idx, "load_rc": self.load_rc}
        if self.idx:
            cur = pactl("list", "modules", "short").stdout
            ok = any(l.split() and l.split()[0] == self.idx
                     and "module-null-sink" in l
                     for l in cur.splitlines())
            out["unload_index_verified"] = ok
            if ok:
                out["unload_rc"] = pactl("unload-module", self.idx).returncode
        return out


def play(target):
    return subprocess.Popen(["pw-play", "--target", target, str(TONE)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)


def stop(p):
    if p:
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()


def e1_timing_live():
    rows = []
    for rep in range(2):
        wd = leg_dir("e1_timing_live", rep)
        sk = Sink("r89edge_a")
        pl = play("r89edge_a")
        time.sleep(0.8)
        t0 = time.monotonic()
        p = subprocess.Popen(["pw-profiler", "-J", "-n", "60"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=wd / "wd")
        (wd / "cmd.txt").write_text("pw-profiler -J -n 60  # sampled mid-run\n")
        os.set_blocking(p.stdout.fileno(), False)
        snaps = []
        for at in (1.0, 2.0):
            while time.monotonic() - t0 < at:
                time.sleep(0.05)
            snaps.append((at, p.stdout.read() or b""))
        os.set_blocking(p.stdout.fileno(), True)
        out_rest, err = p.communicate(timeout=15)
        meta = {"rc": p.returncode,
                "wall_s": round(time.monotonic() - t0, 3),
                "snap_at_1s_len": len(snaps[0][1]),
                "snap_at_1s_head": snaps[0][1][:80].decode("utf-8", "replace"),
                "snap_at_2s_len": len(snaps[1][1]),
                "snap_at_2s_head": snaps[1][1][:80].decode("utf-8", "replace"),
                "post_len": len(out_rest),
                "post_tail": out_rest[-60:].decode("utf-8", "replace"),
                "stderr": err.decode("utf-8", "replace")[:200]}
        (wd / "stdout.bin").write_bytes(
            snaps[0][1] + snaps[1][1] + out_rest)
        (wd / "stderr.txt").write_bytes(err)
        write_meta(wd, meta)
        meta["unload"] = sk.close()
        stop(pl)
        rows.append(meta)
    return {"e1_timing_live": rows}


def e2_kill_live():
    rows = []
    for rep in range(2):
        wd = leg_dir("e2_kill_live", rep)
        sk = Sink("r89edge_a")
        pl = play("r89edge_a")
        time.sleep(0.8)
        p = subprocess.Popen(["pw-profiler", "-J", "-n", "500"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=wd / "wd")
        (wd / "cmd.txt").write_text(
            "pw-profiler -J -n 500  # SIGKILL at ~1.2s\n")
        time.sleep(1.2)
        p.send_signal(signal.SIGKILL)
        out, err = p.communicate(timeout=5)
        meta = {"rc": p.returncode, "stdout_len": len(out),
                "stdout_tail": out[-80:].decode("utf-8", "replace"),
                "stderr": err.decode("utf-8", "replace")[:200]}
        (wd / "stdout.bin").write_bytes(out)
        (wd / "stderr.txt").write_bytes(err)
        write_meta(wd, meta)
        meta["unload"] = sk.close()
        stop(pl)
        rows.append(meta)
    return {"e2_kill_live": rows}


def e3_concurrent():
    rows = []
    for rep in range(2):
        wd = leg_dir("e3_concurrent", rep)
        sk = Sink("r89edge_a")
        pl = play("r89edge_a")
        time.sleep(0.8)
        t0 = time.monotonic()
        ps = [subprocess.Popen(["pw-profiler", "-J", "-n", "8"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               cwd=wd / "wd") for _ in range(2)]
        (wd / "cmd.txt").write_text("2x pw-profiler -J -n 8 concurrent\n")
        outs = []
        for i, p in enumerate(ps):
            o, e = p.communicate(timeout=20)
            (wd / f"stdout_{i}.bin").write_bytes(o)
            (wd / f"stderr_{i}.txt").write_bytes(e)
            outs.append(o)
        arrs = []
        for o in outs:
            try:
                arrs.append(json.loads(o.decode().strip()))
            except Exception as ex:
                arrs.append(f"parse_err {ex}")
        meta = {"rcs": [p.returncode for p in ps],
                "wall_s": round(time.monotonic() - t0, 3),
                "lens": [len(o) for o in outs],
                "shas": [sha(o) for o in outs],
                "n_recs": [len(a) if isinstance(a, list) else a
                           for a in arrs],
                "byte_identical": outs[0] == outs[1],
                "driver_names": sorted({
                    x.get("name") for a in arrs if isinstance(a, list)
                    for x in a if x.get("type") == "driver"})}
        write_meta(wd, meta)
        meta["unload"] = sk.close()
        stop(pl)
        rows.append(meta)
    return {"e3_concurrent": rows}


def e4_two_drivers():
    rows = []
    for rep in range(2):
        wd = leg_dir("e4_two_drivers", rep)
        ska = Sink("r89edge_a", 48000)
        skb = Sink("r89edge_b", 44100)
        pla = play("r89edge_a")
        plb = play("r89edge_b")
        time.sleep(0.8)
        t0 = time.monotonic()
        p = subprocess.Popen(["pw-profiler", "-J", "-n", "4"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=wd / "wd")
        (wd / "cmd.txt").write_text(
            "pw-profiler -J -n 4  # drivers r89edge_a@48k + r89edge_b@44.1k\n")
        out, err = p.communicate(timeout=15)
        (wd / "stdout.bin").write_bytes(out)
        (wd / "stderr.txt").write_bytes(err)
        recs = {"rc": p.returncode,
                "wall_s": round(time.monotonic() - t0, 3)}
        try:
            arr = json.loads(out.decode().strip())
            infos = [x for x in arr if x.get("type") == "info"]
            clocks = [x for x in arr if x.get("type") == "clock"]
            drivers = [x for x in arr if x.get("type") == "driver"]
            recs.update({
                "n_recs": len(arr), "info_counts": [x["count"] for x in infos],
                "clock_names": sorted({x["name"] for x in clocks}),
                "driver_names": sorted({x["name"] for x in drivers}),
                "clock_ids": sorted({x["id"] for x in clocks}),
                "driver_ids": sorted({x["id"] for x in drivers}),
                "n_clock_rows": len(clocks), "n_driver_rows": len(drivers)})
        except Exception as ex:
            recs["parse_err"] = str(ex)
        write_meta(wd, recs)
        recs["unload_a"] = ska.close()
        recs["unload_b"] = skb.close()
        stop(pla)
        stop(plb)
        rows.append(recs)
    return {"e4_two_drivers": rows}


def e5_remote_named():
    rows = []
    for rep in range(2):
        wd = leg_dir("e5_remote_named", rep)
        (wd / "cmd.txt").write_text(
            "pw-profiler -r pipewire-0 -J -n 2  # idle, SIGINT at 2s\n")
        p = subprocess.Popen(["pw-profiler", "-r", "pipewire-0", "-J",
                              "-n", "2"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=wd / "wd")
        timer = threading.Timer(2.0, p.send_signal, args=(signal.SIGINT,))
        timer.start()
        out, err = p.communicate(timeout=10)
        timer.cancel()
        meta = {"rc": p.returncode,
                "stdout": out.decode("utf-8", "replace")[:300],
                "stderr": err.decode("utf-8", "replace")[:300]}
        (wd / "stdout.bin").write_bytes(out)
        (wd / "stderr.txt").write_bytes(err)
        write_meta(wd, meta)
        rows.append(meta)
    return {"e5_remote_named": rows}


def main():
    out = {}
    for fn in (e1_timing_live, e2_kill_live, e3_concurrent,
               e4_two_drivers, e5_remote_named):
        out.update(fn())
        (REC / "s-edge.json").write_text(json.dumps(out, indent=1))
        print(f"done {fn.__name__}", flush=True)
    # host-state: zero r89edge residue
    d = json.loads(subprocess.run(["pw-dump"], capture_output=True,
                                  timeout=20).stdout)
    residue = [o["id"] for o in d
               if "r89edge" in json.dumps(o)]
    print(json.dumps({"edge_residue_ids": residue}))


if __name__ == "__main__":
    main()
