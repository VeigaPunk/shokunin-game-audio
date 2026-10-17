#!/usr/bin/env python3
"""r89 scout harness — pw-profiler output lattice on PipeWire 1.6.8.

Pure-observation surface: libpipewire-module-profiler is already resident
(Module id 4, profile.interval.ms=0) so pw-profiler loads nothing. The only
mutation legs are the own_driver legs (seat-owned module-null-sink +
pw-play, unloaded by index verified against sink_name).

Receipt layout: runs/<leg>/<rep>/{cmd.txt,stdout.bin,stderr.txt,meta.json}
and artifact legs additionally keep wd/ (the pw-profiler cwd) verbatim.
Consolidated per-stage JSON in receipts/.
"""
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
REC = ROOT / "receipts"
TONE = ROOT / "r89_tone.wav"
PWPROF = shutil.which("pw-profiler")
for d in (RUNS, REC):
    d.mkdir(parents=True, exist_ok=True)

HOST_SCRATCH_NOTE = "cwd is under corpus/live/r89-scout/runs"


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def run_leg(leg, rep, cmd, cwd=None, timeout=30, sig_after=None,
            sig=signal.SIGINT, env=None):
    """Run one leg rep. sig_after: seconds after spawn to send sig."""
    wd = RUNS / leg / f"rep{rep}"
    wd.mkdir(parents=True, exist_ok=True)
    workdir = wd / "wd"
    workdir.mkdir(exist_ok=True)
    eff_cwd = cwd or workdir
    (wd / "cmd.txt").write_text(" ".join(str(c) for c in cmd) + "\n"
                                + f"# cwd={eff_cwd}\n")
    t0 = time.monotonic_ns()
    wall0 = time.time()
    proc = subprocess.Popen(
        [str(c) for c in cmd], cwd=eff_cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=env or os.environ.copy())
    timer = None
    if sig_after is not None:
        timer = threading.Timer(sig_after, proc.send_signal, args=(sig,))
        timer.start()
    try:
        out, err = proc.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        timed_out = True
    if timer:
        timer.cancel()
    t1 = time.monotonic_ns()
    (wd / "stdout.bin").write_bytes(out)
    (wd / "stderr.txt").write_bytes(err)
    files = sorted(
        str(p.relative_to(workdir)) for p in workdir.rglob("*")
        if p.is_file()) if workdir.exists() else []
    meta = {
        "cmd": [str(c) for c in cmd], "cwd": str(eff_cwd),
        "rc": proc.returncode, "timed_out": timed_out,
        "wall_s": round(time.time() - wall0, 3),
        "t_mono_ns": [t0, t1],
        "sig_after": sig_after,
        "sig": sig.name if sig_after is not None else None,
        "stdout_len": len(out), "stderr_len": len(err),
        "stdout_sha": sha256(out), "stderr_sha": sha256(err),
        "wd_files": files,
        "wd_file_sha": {f: sha256((workdir / f).read_bytes())
                        for f in files},
    }
    (wd / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta, out, err


def parse_j(stdout):
    """pw-profiler -J emits a JSON array whose last element is {}."""
    txt = stdout.decode("utf-8", "replace").strip()
    try:
        arr = json.loads(txt)
        return arr, None
    except json.JSONDecodeError as e:
        return None, f"{e} (len={len(txt)})"


def jstats(arr):
    """Invariants over one -J run."""
    recs = [o for o in arr if o]
    types = {}
    for o in recs:
        types.setdefault(o.get("type", "?"), 0)
        types[o.get("type", "?")] += 1
    infos = [o for o in recs if o.get("type") == "info"]
    clocks = [o for o in recs if o.get("type") == "clock"]
    drivers = [o for o in recs if o.get("type") == "driver"]
    followers = [o for o in recs if o.get("type") == "follower"]
    fclocks = [o for o in recs if o.get("type") == "followerClock"]
    s = {
        "n_recs": len(recs), "types": types,
        "trailing_empty": bool(arr) and arr[-1] == {},
        "info_counts": [o["count"] for o in infos],
        "clock_names": sorted({o["name"] for o in clocks}),
        "clock_rates": sorted({o["rate"] for o in clocks}),
        "clock_durations": sorted({o["duration"] for o in clocks}),
        "clock_transports": sorted({o.get("transport", "?") for o in clocks}),
        "clock_cycles": [o.get("cycle") for o in clocks],
        "clock_xruns": sorted({o.get("xrun") for o in clocks}),
        "quantum_ns_measured": sorted({
            o["next_nsec"] - o["nsec"] for o in clocks if o.get("next_nsec")}),
        "pos_step_ok": all(
            clocks[i + 1]["position"] - clocks[i]["position"] ==
            clocks[i + 1]["duration"]
            for i in range(len(clocks) - 1)),
        "driver_names": sorted({o["name"] for o in drivers}),
        "driver_statuses": sorted({o["status"] for o in drivers}),
        "driver_latencies": sorted({o["latency"] for o in drivers}),
        "order_ok": all(
            o["prev"] <= o["signal"] <= o["awake"] <= o["finish"]
            for o in drivers + followers),
        "busy_ns_range": [
            min((o["finish"] - o["awake"] for o in drivers + followers),
                default=None),
            max((o["finish"] - o["awake"] for o in drivers + followers),
                default=None)],
        "wait_ns_range": [
            min((o["awake"] - o["signal"] for o in drivers + followers),
                default=None),
            max((o["awake"] - o["signal"] for o in drivers + followers),
                default=None)],
        "prev_is_last_signal": all(
            drivers[i + 1]["prev"] == drivers[i]["signal"]
            for i in range(len(drivers) - 1)
            if drivers[i]["id"] == drivers[i + 1]["id"]) if drivers else None,
        "fclock_frozen": len({
            json.dumps(o, sort_keys=True) for o in fclocks}) <= 1,
        "fclock_ids": sorted({o["id"] for o in fclocks}),
        "xrun_counts": sorted({o["xrun_count"] for o in drivers + followers}),
        "clock_nsec_range": [min((o["nsec"] for o in clocks), default=None),
                             max((o["nsec"] for o in clocks), default=None)],
        "cpu_load_ranges": {
            k: [min(o[k] for o in infos), max(o[k] for o in infos)]
            for k in ("cpu_load0", "cpu_load1", "cpu_load2") if infos},
        "cpu_load_sorted_desc": all(
            o["cpu_load0"] >= o["cpu_load1"] >= o["cpu_load2"]
            for o in infos) if infos else None,
    }
    return s


def census():
    out = subprocess.run(["pw-dump"], capture_output=True, timeout=20).stdout
    d = json.loads(out)
    nodes = {}
    modules = {}
    clients = []
    for o in d:
        t = o["type"].split(":")[-1]
        p = o.get("info", {}).get("props", {})
        if t == "Node":
            nodes[o["id"]] = (p.get("node.name"), p.get("media.class"),
                              o["info"].get("state"))
        elif t == "Module":
            modules[o["id"]] = p.get("module.name")
        elif t == "Client":
            clients.append((o["id"], p.get("application.name"),
                            p.get("object.serial")))
    return {"n_objects": len(d), "nodes": nodes, "modules": modules,
            "clients": clients,
            "r89_objects": [f"{i}:{v[0]}" for i, v in nodes.items()
                            if v[0] and "r89" in str(v[0])]}


def ensure_tone():
    if TONE.exists():
        return
    import struct
    import wave
    rate, secs, amp = 48000, 30, 8000
    with wave.open(str(TONE), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(rate * secs):
            import math
            v = int(amp * math.sin(2 * math.pi * 1000 * i / rate))
            frames += struct.pack("<hh", v, v)
        w.writeframes(bytes(frames))


def pactl(*args):
    return subprocess.run(["pactl", *args], capture_output=True,
                          text=True, timeout=15)


def own_driver_legs(reps=3):
    """Seat-owned null sink + pw-play -> a second driver domain appears."""
    ensure_tone()
    results = []
    for rep in range(reps):
        before = pactl("list", "modules", "short").stdout
        ld = pactl("load-module", "module-null-sink",
                   "sink_name=r89prof_ns", "rate=48000", "channels=2")
        idx = ld.stdout.strip()
        loaded = ld.returncode == 0 and idx.isdigit()
        meta = {"rep": rep, "load_rc": ld.returncode, "idx": idx,
                "load_err": ld.stderr.strip()}
        player = None
        try:
            if loaded:
                for _ in range(50):
                    if "r89prof_ns" in pactl("list", "sinks",
                                           "short").stdout:
                        break
                    time.sleep(0.1)
                player = subprocess.Popen(
                    ["pw-play", "--target", "r89prof_ns", str(TONE)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.8)
                m, out, err = run_leg(
                    "own_driver", rep,
                    [PWPROF, "-J", "-n", "40"])
                arr, perr = parse_j(out)
                meta["prof"] = m
                meta["parse_err"] = perr
                if arr:
                    st = jstats(arr)
                    meta["stats"] = st
                    drivers = [o for o in arr if o.get("type") == "driver"]
                    meta["driver_names_seen"] = st["driver_names"]
                    meta["r89_rows"] = sum(
                        1 for o in arr
                        if "r89prof" in str(o.get("name", "")))
        finally:
            if player:
                player.terminate()
                try:
                    player.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    player.kill()
            if loaded:
                cur = pactl("list", "modules", "short").stdout
                line_ok = any(
                    l.split()[0] == idx and "module-null-sink" in l
                    for l in cur.splitlines())
                meta["unload_index_verified"] = line_ok
                if line_ok:
                    ul = pactl("unload-module", idx)
                    meta["unload_rc"] = ul.returncode
        meta["modules_delta"] = sorted(
            set(pactl("list", "modules", "short").stdout.split())
            - set(before.split()))
        results.append(meta)
    (REC / "s-own-driver.json").write_text(json.dumps(results, indent=1))
    return results


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    c0 = census()
    (REC / "census-entry.json").write_text(json.dumps(c0, indent=1))

    out = {}

    if stage in ("all", "mode"):
        # A. artifact/mode lattice
        rows = []
        for rep in range(3):
            m, o, e = run_leg("j_n8", rep,
                              [PWPROF, "-J", "-o", "prof89", "-n", "8"])
            arr, perr = parse_j(o)
            rows.append({"meta": m, "parse_err": perr,
                         "stats": jstats(arr) if arr else None})
        out["j_n8"] = rows
        rows = []
        for rep in range(3):
            m, o, e = run_leg("plain_o_n4", rep,
                              [PWPROF, "-o", "p", "-n", "4"])
            rows.append(m)
        out["plain_o_n4"] = rows
        rows = []
        for rep in range(3):
            m, o, e = run_leg("plain_default_n4", rep,
                              [PWPROF, "-n", "4"])
            rows.append(m)
        out["plain_default_n4"] = rows
        (REC / "s-mode.json").write_text(json.dumps(out, indent=1))

    if stage in ("all", "nsem"):
        rows = {}
        for n in ("1", "2", "3"):
            reps = []
            for rep in range(2):
                m, o, e = run_leg(f"n_{n}", rep,
                                  [PWPROF, "-J", "-n", n])
                arr, perr = parse_j(o)
                infos = [x for x in (arr or []) if x.get("type") == "info"]
                reps.append({"meta": m, "parse_err": perr,
                             "info_counts": [x["count"] for x in infos],
                             "n_rows": len(arr or []),
                             "trailing_empty": bool(arr) and arr[-1] == {}})
            rows[n] = reps
        # -n 0: bounded by SIGINT at 3s
        reps = []
        for rep in range(2):
            m, o, e = run_leg("n_zero", rep, [PWPROF, "-J", "-n", "0"],
                              sig_after=3.0, sig=signal.SIGINT)
            arr, perr = parse_j(o)
            reps.append({"meta": m, "parse_err": perr,
                         "n_rows": len(arr or []),
                         "raw_info_rows": o.count(b'"type": "info"'),
                         "stdout_tail": o[-120:].decode("utf-8", "replace"),
                         "stderr_tail": e.decode("utf-8", "replace")[-200:]})
        rows["0"] = reps
        # refusals
        for name, args in {
            "n_neg": ["-J", "-n", "-1"],
            "n_abc": ["-J", "-n", "abc"],
            "n_float": ["-J", "-n", "2.5"],
        }.items():
            reps = []
            for rep in range(3):
                m, o, e = run_leg(name, rep, [PWPROF, *args], timeout=10)
                reps.append({"meta": m,
                             "stdout_head": o[:200].decode("utf-8", "replace"),
                             "stderr_head": e[:200].decode("utf-8", "replace")})
            rows[name] = reps
        (REC / "s-nsem.json").write_text(json.dumps(rows, indent=1))

    if stage in ("all", "sig"):
        rows = {}
        for name, sigm, jmode in (
                ("sig_int_plain", signal.SIGINT, False),
                ("sig_term_plain", signal.SIGTERM, False),
                ("sig_kill_plain", signal.SIGKILL, False),
                ("sig_int_j", signal.SIGINT, True),
                ("sig_term_j", signal.SIGTERM, True)):
            reps = []
            nrep = 1 if "kill" in name else 3
            for rep in range(nrep):
                cmd = [PWPROF, "-o", f"{name}"]
                if jmode:
                    cmd += ["-J"]
                m, o, e = run_leg(name, rep, cmd, sig_after=2.5, sig=sigm)
                reps.append({"meta": m,
                             "stdout_len": len(o),
                             "stderr_tail": e.decode("utf-8", "replace")[-300:]})
            rows[name] = reps
        (REC / "s-sig.json").write_text(json.dumps(rows, indent=1))

    if stage in ("all", "refuse"):
        rows = {}
        for name, args in {
            "remote_bogus": ["-r", "r89_no_such_remote", "-J", "-n", "2"],
            "remote_empty": ["-r", "", "-J", "-n", "2"],
            "out_unwritable": ["-o", "/proc/r89prof/x", "-n", "2"],
            "opt_bogus": ["--r89bogus"],
            "extra_arg": ["-J", "-n", "2", "extrapositional"],
            "version": ["--version"],
            "h_flag": ["-h"],
        }.items():
            reps = []
            for rep in range(3):
                m, o, e = run_leg(name, rep, [PWPROF, *args], timeout=15)
                reps.append({"meta": m,
                             "stdout_head": o[:300].decode("utf-8", "replace"),
                             "stderr_head": e[:300].decode("utf-8", "replace")})
            rows[name] = reps
        (REC / "s-refuse.json").write_text(json.dumps(rows, indent=1))

    if stage in ("all", "schema"):
        # E. deep invariant reps — longer windows
        rows = []
        for rep in range(3):
            m, o, e = run_leg("schema_n30", rep, [PWPROF, "-J", "-n", "30"])
            arr, perr = parse_j(o)
            st = jstats(arr) if arr else None
            clocks = [x for x in (arr or []) if x.get("type") == "clock"]
            # clock identity: nsec within the run's monotonic bounds?
            bounds = m["t_mono_ns"]
            inside = (st and st["clock_nsec_range"][0] is not None and
                      bounds[0] - 5_000_000_000 <= st["clock_nsec_range"][0]
                      <= st["clock_nsec_range"][1]
                      <= bounds[1] + 5_000_000_000)
            rows.append({"meta": m, "parse_err": perr, "stats": st,
                         "clock_nsec_inside_monotonic_window": inside,
                         "mono_ns_now": time.monotonic_ns()})
        (REC / "s-schema.json").write_text(json.dumps(rows, indent=1))
        # E2. the Profiler object itself as a pw-cli target
        prows = []
        pid = next((k for k, v in c0["modules"].items()
                    if v == "libpipewire-module-profiler"), None)
        # find the Profiler object id fresh
        d = json.loads(subprocess.run(["pw-dump"], capture_output=True,
                                      timeout=20).stdout)
        prof_id = next((o["id"] for o in d
                        if o["type"].endswith("Profiler")), None)
        for rep in range(2):
            for verb in ("info", "enum-params"):
                cmd = ["pw-cli", verb, str(prof_id)]
                if verb == "enum-params":
                    cmd.append("Props")
                m, o, e = run_leg(f"profobj_{verb}", rep, cmd, timeout=10)
                prows.append({"verb": verb, "rep": rep,
                              "profiler_obj_id": prof_id,
                              "profiler_module_id": pid,
                              "meta": m,
                              "stdout_head":
                              o[:400].decode("utf-8", "replace"),
                              "stderr_head":
                              e[:300].decode("utf-8", "replace")})
        (REC / "s-profobj.json").write_text(json.dumps(prows, indent=1))

    if stage in ("all", "drv"):
        own_driver_legs(3)

    if stage in ("all", "top"):
        # F. pw-top cross-witness during seat-owned driver domain
        ensure_tone()
        rows = []
        for rep in range(3):
            ld = pactl("load-module", "module-null-sink",
                       "sink_name=r89prof_ns", "rate=48000", "channels=2")
            idx = ld.stdout.strip()
            loaded = ld.returncode == 0 and idx.isdigit()
            meta = {"rep": rep, "idx": idx, "load_rc": ld.returncode}
            player = None
            try:
                if loaded:
                    for _ in range(50):
                        if "r89prof_ns" in pactl("list", "sinks",
                                               "short").stdout:
                            break
                        time.sleep(0.1)
                    player = subprocess.Popen(
                        ["pw-play", "--target", "r89prof_ns", str(TONE)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(0.8)
                    mp, op, ep = run_leg("top_xw_prof", rep,
                                         [PWPROF, "-J", "-n", "60"],
                                         timeout=20)
                    arr, _ = parse_j(op)
                    drivers = [x for x in (arr or [])
                               if x.get("type") in ("driver", "follower")]
                    my = [x for x in drivers if "r89prof" in str(x.get("name"))]
                    meta["prof_busy_ns_my"] = [
                        x["finish"] - x["awake"] for x in my][-10:]
                    meta["prof_wait_ns_my"] = [
                        x["awake"] - x["signal"] for x in my][-10:]
                    # pw-top last frame in the same-ish window
                    mt, ot, et = run_leg("top_xw_top", rep,
                                         ["pw-top", "-b", "-n", "3"],
                                         timeout=20)
                    frame = ot.decode("utf-8", "replace")
                    last = [l for l in frame.splitlines() if l.strip()]
                    meta["pwtop_rows"] = [l for l in last
                                          if "r89prof" in l or
                                          l[:1] in "CSIRET"][-15:]
                    meta["pwtop_meta"] = mt
            finally:
                if player:
                    player.terminate()
                    try:
                        player.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        player.kill()
                if loaded:
                    cur = pactl("list", "modules", "short").stdout
                    if any(l.split()[0] == idx and "module-null-sink" in l
                           for l in cur.splitlines()):
                        meta["unload_rc"] = pactl("unload-module",
                                                  idx).returncode
            rows.append(meta)
        (REC / "s-top-xw.json").write_text(json.dumps(rows, indent=1))

    if stage in ("all", "foot"):
        # G. client footprint — pw-dump diff while pw-profiler runs
        rows = []
        for rep in range(2):
            c_b = census()
            proc = subprocess.Popen([PWPROF, "-J", "-n", "200"],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
            time.sleep(0.6)
            c_d = census()
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            new_clients = [c for c in c_d["clients"]
                           if c not in c_b["clients"]]
            rows.append({"rep": rep,
                         "new_clients_during": new_clients,
                         "n_obj_before": c_b["n_objects"],
                         "n_obj_during": c_d["n_objects"],
                         "new_modules": [k for k in c_d["modules"]
                                         if k not in c_b["modules"]],
                         "new_nodes": {k: v for k, v in c_d["nodes"].items()
                                       if k not in c_b["nodes"]}})
        (REC / "s-footprint.json").write_text(json.dumps(rows, indent=1))

    c1 = census()
    (REC / "census-exit.json").write_text(json.dumps(c1, indent=1))
    print(json.dumps({"done": stage,
                      "entry_modules": c0["modules"],
                      "exit_r89": c1["r89_objects"],
                      "exit_module_delta": {
                          "added": {k: v for k, v in c1["modules"].items()
                                    if k not in c0["modules"]},
                          "removed": {k: v for k, v in c0["modules"].items()
                                      if k not in c1["modules"]}}},
                     indent=1))


if __name__ == "__main__":
    main()
