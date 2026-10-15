#!/usr/bin/env python3
"""r96-scout battery A — pulse client CLI surface: server resolution, targeting,
latency vector, stream properties, introspection.

Every leg is bounded (wall cap + process-group kill + byte caps). Only seat
objects (`r96s_*`) are created; playback targets the seat null sink unless the
leg's whole point is to observe default-fallback routing (quiet tone).
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r96s_lib as L  # noqa: E402

ROOT = L.ROOT
SEAT = L.SEAT_SINK_NAME
TONE = os.path.join(ROOT, "scratch", "tone1k5.wav")
QUIET = os.path.join(ROOT, "scratch", "tone1k5_quiet.wav")
RUNLOG = os.path.join(ROOT, "runs", "batteryA.log")


def stream_snapshot(pid, kind="sink-inputs"):
    """Rows of `kind` whose application.process.id == pid (my stream), plus all rows summary."""
    rows, meta = L.pactl_json(["list", kind])
    mine, others = [], []
    for row in rows or []:
        props = row.get("properties", {})
        if str(props.get("application.process.id")) == str(pid):
            mine.append(row)
        else:
            others.append({"index": row.get("index"), "app": props.get("application.name"), "client.api": props.get("client.api")})
    return mine, {"all_count": len(rows or []), "foreign": others[:6], **meta}


def sink_name_of(index):
    sinks, _ = L.pactl_json(["list", "sinks", "short"])
    for s in sinks or []:
        if s.get("index") == index:
            return s.get("name")
    return None


def source_name_of(index):
    srcs, _ = L.pactl_json(["list", "sources", "short"])
    for s in srcs or []:
        if s.get("index") == index:
            return s.get("name")
    return None


def restore_rows():
    path = os.path.expanduser("~/.local/state/wireplumber/stream-properties")
    try:
        with open(path, "r", errors="replace") as fh:
            data = fh.read()
    except OSError:
        return {"path": path, "exists": False}
    lines = [ln for ln in data.splitlines() if "r96s" in ln]
    return {"path": path, "exists": True, "r96s_rows": len(lines), "sample": lines[:5]}


def leg_stream(name, argv, env_extra=None, reps=3, timeout=9.0, snapshot_at=0.35,
               snapshot_kind="sink-inputs", kill_after_snapshot=False, quiet=False):
    """Run a pulse CLI leg that creates a stream; snapshot my stream row while live."""
    env = L.base_env()
    env.update(env_extra or {})
    results = []
    for rep in range(reps):
        t0 = time.monotonic()
        proc = subprocess.Popen(
            argv, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True, preexec_fn=L._limits,
        )
        snap = None
        if snapshot_at is not None:
            time.sleep(snapshot_at)
            snap = stream_snapshot(proc.pid, snapshot_kind)
        if kill_after_snapshot and proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        timed_out = False
        try:
            out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = proc.communicate()
        rows = snap[0] if snap else []
        slim = []
        for row in rows:
            props = row.get("properties", {})
            slim.append({
                "index": row.get("index"),
                "sink": row.get("sink"), "sink_name": sink_name_of(row.get("sink")),
                "source": row.get("source"), "source_name": source_name_of(row.get("source")),
                "corked": row.get("corked"), "mute": row.get("mute"),
                "sample_specification": row.get("sample_specification"),
                "buffer_latency_usec": row.get("buffer_latency_usec"),
                "sink_latency_usec": row.get("sink_latency_usec"),
                "resample_method": row.get("resample_method"),
                "props": {k: props.get(k) for k in (
                    "pulse.corked", "pulse.attr.tlength", "pulse.attr.prebuf",
                    "pulse.attr.minreq", "pulse.attr.maxlength", "node.latency",
                    "node.rate", "media.role", "application.name", "media.name",
                    "zzz.invented", "state.restore-props", "target.object",
                    "application.process.binary", "client.api",
                ) if k in props},
            })
        results.append({
            "rep": rep, "argv": argv, "env_extra": env_extra or {},
            "rc": proc.returncode, "timed_out": timed_out,
            "wall_s": round(time.monotonic() - t0, 4),
            "stdout": out[:4000].decode("utf-8", "replace"),
            "stderr": err[:4000].decode("utf-8", "replace"),
            "my_streams": slim, "snapshot_meta": snap[1] if snap else None,
        })
        L.log_line(RUNLOG, f"{name} rep{rep} rc={proc.returncode} wall={results[-1]['wall_s']} streams={json.dumps(slim)[:300]}")
    return {"leg": name, "results": results}


def leg_cmd(name, argv, env_extra=None, reps=3, timeout=8.0):
    env = L.base_env()
    env.update(env_extra or {})
    results = []
    for rep in range(reps):
        r = L.run_bounded(argv, env=env, timeout=timeout)
        r["rep"] = rep
        r["env_extra"] = env_extra or {}
        results.append(r)
        L.log_line(RUNLOG, f"{name} rep{rep} rc={r['rc']} timed_out={r['timed_out']} wall={r['wall_s']} err={r['stderr'][:120]!r}")
    return {"leg": name, "results": results}


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    receipts = {}
    t_start = time.time()

    if only in ("all", "avail"):
        receipts["a1_avail"] = {
            "tools": {t: (subprocess.run(["command", "-v", t], shell=False, capture_output=True).stdout.decode().strip() if False else None) for t in []},
            "tool_probe": {},
            "pactl_info": L.run_bounded(["pactl", "info"], env=L.base_env(), timeout=6),
            "pactl_stat": L.run_bounded(["pactl", "stat"], env=L.base_env(), timeout=6),
            "socket_ls": L.run_bounded(["ls", "-la", f"/run/user/{os.getuid()}/pulse/"], timeout=4),
            "versions": {t: L.run_bounded([t, "--version"], timeout=4) for t in ("pactl", "pacat", "paplay", "parec")},
            "pactl_help": L.run_bounded(["pactl", "--help"], timeout=4),
        }
        for t in ("pactl", "pacat", "paplay", "parec", "parecord", "pamon", "pacmd", "pa-info", "pax11publish", "pw-pulse"):
            r = L.run_bounded(["which", t], timeout=4)
            receipts["a1_avail"]["tool_probe"][t] = {"rc": r["rc"], "path": r["stdout"].strip()}
        # client.conf read (operator file, read-only)
        for p in ("/etc/pulse/client.conf", os.path.expanduser("~/.config/pulse/client.conf")):
            receipts["a1_avail"][p] = L.run_bounded(["cat", p], timeout=4)["stdout"][:4000]

    if only in ("all", "server"):
        receipts["b_default"] = leg_cmd("b_default", ["pactl", "info"])
        receipts["b_unix_prefix"] = leg_cmd("b_unix_prefix", ["pactl", "info"], {"PULSE_SERVER": f"unix:/run/user/{os.getuid()}/pulse/native"})
        receipts["b_bare_path"] = leg_cmd("b_bare_path", ["pactl", "info"], {"PULSE_SERVER": f"/run/user/{os.getuid()}/pulse/native"})
        receipts["b_unix_missing"] = leg_cmd("b_unix_missing", ["pactl", "info"], {"PULSE_SERVER": "unix:/nonexistent"})
        receipts["b_tcp_refused"] = leg_cmd("b_tcp_refused", ["pactl", "info"], {"PULSE_SERVER": "tcp:127.0.0.1:4713"})
        receipts["b_host_bogus"] = leg_cmd("b_host_bogus", ["pactl", "info"], {"PULSE_SERVER": "nonexistent-r96s"}, reps=2, timeout=15)
        receipts["b_runtime_path"] = leg_cmd("b_runtime_path", ["pactl", "info"], {"PULSE_RUNTIME_PATH": "/tmp/r96s_nope"})
        receipts["b_empty_server"] = leg_cmd("b_empty_server", ["pactl", "info"], {"PULSE_SERVER": ""})
        receipts["b_cookie_devnull"] = leg_cmd("b_cookie_devnull", ["pactl", "info"], {"PULSE_COOKIE": "/dev/null"})
        receipts["b_flag_beats_env"] = leg_cmd("b_flag_beats_env", ["pactl", "-s", f"unix:/run/user/{os.getuid()}/pulse/native", "info"], {"PULSE_SERVER": "tcp:127.0.0.1:1"})
        receipts["b_env_loses_to_flag"] = leg_cmd("b_env_loses_to_flag", ["pactl", "-s", "tcp:127.0.0.1:1", "info"], {"PULSE_SERVER": f"unix:/run/user/{os.getuid()}/pulse/native"})
        # client.conf vectors
        cc = os.path.join(ROOT, "scratch", "r96s_client_badserver.conf")
        with open(cc, "w") as fh:
            fh.write("default-server = tcp:127.0.0.1:1\n")
        receipts["b_clientconfig_badserver"] = leg_cmd("b_clientconfig_badserver", ["pactl", "info"], {"PULSE_CLIENTCONFIG": cc})
        cc2 = os.path.join(ROOT, "scratch", "r96s_client_defaultsink.conf")
        with open(cc2, "w") as fh:
            fh.write(f"default-sink = {SEAT}\n")
        receipts["b_clientconfig_defaultsink"] = leg_stream(
            "b_clientconfig_defaultsink", ["paplay", QUIET], {"PULSE_CLIENTCONFIG": cc2})

    if only in ("all", "target"):
        mod2 = None
        if L.seat_sink_index2() is None:
            r2 = L.run_bounded(["pactl", "load-module", "module-null-sink",
                                "sink_name=" + L.SEAT_SINK2_NAME, "rate=48000", "channels=1",
                                "sink_properties=state.restore-props=false"], env=L.base_env(), timeout=8)
            mod2 = r2["stdout"].strip()
            receipts["c_prep_sink2"] = {"module_id": mod2, "rc": r2["rc"], "stderr": r2["stderr"]}
        receipts["c_env_sink_seat"] = leg_stream("c_env_sink_seat", ["paplay", QUIET], {"PULSE_SINK": SEAT})
        receipts["c_env_sink_default"] = leg_stream("c_env_sink_default", ["paplay", QUIET], {"PULSE_SINK": "@DEFAULT_SINK@"})
        receipts["c_env_sink_missing"] = leg_stream("c_env_sink_missing", ["paplay", QUIET], {"PULSE_SINK": "no_such_r96s"})
        seat_idx = str(L.seat_sink_index())
        receipts["c_env_sink_index"] = leg_stream("c_env_sink_index", ["paplay", QUIET], {"PULSE_SINK": seat_idx})
        receipts["c_env_sink_index2"] = leg_stream("c_env_sink_index2", ["paplay", QUIET], {"PULSE_SINK": str(L.seat_sink_index2() or "NOINDEX2")})
        receipts["c_env_sink_badindex"] = leg_stream("c_env_sink_badindex", ["paplay", QUIET], {"PULSE_SINK": "999999"})
        receipts["c_env_sink_spdif_index"] = leg_stream("c_env_sink_spdif_index", ["paplay", QUIET], {"PULSE_SINK": "61"})
        receipts["c_env_sink_monitor"] = leg_stream("c_env_sink_monitor", ["paplay", QUIET], {"PULSE_SINK": SEAT + ".monitor"})
        receipts["c_env_sink_empty"] = leg_stream("c_env_sink_empty", ["paplay", QUIET], {"PULSE_SINK": ""})
        receipts["c_flag_beats_env"] = leg_stream("c_flag_beats_env", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", "@DEFAULT_SINK@", TONE], {"PULSE_SINK": SEAT})
        receipts["c_flag_seat"] = leg_stream("c_flag_seat", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", SEAT, TONE], {"PULSE_SINK": "@DEFAULT_SINK@"})
        receipts["c_source_seat_monitor"] = leg_stream(
            "c_source_seat_monitor", ["parec", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", SEAT + ".monitor"],
            {"PULSE_SOURCE": SEAT + ".monitor"}, snapshot_kind="source-outputs", kill_after_snapshot=True, snapshot_at=0.6)
        receipts["c_source_default"] = leg_stream(
            "c_source_default", ["parec", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", "@DEFAULT_SOURCE@"],
            {"PULSE_SOURCE": "@DEFAULT_SOURCE@"}, snapshot_kind="source-outputs", kill_after_snapshot=True, snapshot_at=0.5)
        receipts["c_source_missing"] = leg_stream(
            "c_source_missing", ["parec", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", "no_such_r96s"],
            {"PULSE_SOURCE": "no_such_r96s"}, snapshot_kind="source-outputs", kill_after_snapshot=True, snapshot_at=0.5)
        receipts["c_pacat_default_monitor"] = leg_stream(
            "c_pacat_default_monitor", ["pacat", "--record", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", "@DEFAULT_MONITOR@"],
            snapshot_kind="source-outputs", kill_after_snapshot=True, snapshot_at=0.5)
        if mod2:
            u = L.run_bounded(["pactl", "unload-module", mod2], env=L.base_env(), timeout=8)
            receipts["c_teardown_sink2"] = {"module_id": mod2, "rc": u["rc"], "stderr": u["stderr"]}

    if only in ("all", "latency"):
        receipts["d_default"] = leg_stream("d_default", ["paplay", TONE], {"PULSE_SINK": SEAT})
        receipts["d_env100"] = leg_stream("d_env100", ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": "100"})
        receipts["d_flag100"] = leg_stream("d_flag100", ["pacat", "--playback", "--latency-msec=100", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT})
        receipts["d_env250_flag100"] = leg_stream("d_env250_flag100", ["pacat", "--playback", "--latency-msec=100", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": "250"})
        receipts["d_env100_flag250"] = leg_stream("d_env100_flag250", ["pacat", "--playback", "--latency-msec=250", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": "100"})
        for tag, val in (("zero", "0"), ("neg", "-5"), ("nan", "abc"), ("empty", "")):
            receipts[f"d_env_{tag}"] = leg_stream(f"d_env_{tag}", ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": val})
        matrix = {}
        for m in ("10", "20", "50", "200", "500", "1000", "2000"):
            matrix[m] = leg_stream(f"d_matrix_{m}", ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": m}, reps=1)
        receipts["d_matrix"] = matrix
        receipts["d_proctime5"] = leg_stream("d_proctime5", ["pacat", "--playback", "--process-time-msec=5", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT})
        receipts["d_latency_bytes"] = leg_stream("d_latency_bytes", ["pacat", "--playback", "--latency=9600", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT})
        receipts["d_proctime_bytes"] = leg_stream("d_proctime_bytes", ["pacat", "--playback", "--process-time=480", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT})
        # frame-size falsifiers: stereo s16 and mono f32 both have frame_size 4
        receipts["d_stereo100"] = leg_stream("d_stereo100", ["pacat", "--playback", "--latency-msec=100", "--raw", "--rate=48000", "--format=s16le", "--channels=2", TONE], {"PULSE_SINK": SEAT})
        receipts["d_f32_100"] = leg_stream("d_f32_100", ["pacat", "--playback", "--latency-msec=100", "--raw", "--rate=48000", "--format=f32le", "--channels=1", TONE], {"PULSE_SINK": SEAT})

    if only in ("all", "props"):
        receipts["e_props"] = leg_stream(
            "e_props", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                        "--property=media.role=game", "--property=application.name=r96s_prop",
                        "--property=zzz.invented=42", "--stream-name=r96s_streamname", TONE],
            {"PULSE_SINK": SEAT})
        receipts["e_props_malformed"] = leg_stream(
            "e_props_malformed", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                                  "--property=noequals", TONE], {"PULSE_SINK": SEAT}, reps=2)
        rows_before = restore_rows()
        receipts["e_restore_props_off"] = leg_stream(
            "e_restore_props_off", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                                    "--property=state.restore-props=false", TONE], {"PULSE_SINK": SEAT})
        time.sleep(1.6)
        receipts["e_restore_props_off"]["rows_before"] = rows_before
        receipts["e_restore_props_off"]["rows_after"] = restore_rows()
        receipts["e_client_name"] = leg_stream(
            "e_client_name", ["pacat", "--playback", "--client-name=r96s_client", "--raw", "--rate=48000",
                              "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT})
        time.sleep(1.6)
        receipts["e_restore_props_off"]["rows_final"] = restore_rows()

    if only in ("all", "introspect"):
        # full-text introspection for one live stream, verbatim (seat-filtered by process id handled below)
        env = L.base_env(); env.update({"PULSE_SINK": SEAT})
        proc = subprocess.Popen(["paplay", TONE], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True, preexec_fn=L._limits)
        time.sleep(0.4)
        full = L.run_bounded(["pactl", "list", "sink-inputs"], timeout=6)["stdout"]
        mine = [ln for ln in full.splitlines()]
        # keep only the block whose application.process.id is this pid
        blocks = full.split("\n\n")
        keep = "\n\n".join(b for b in blocks if f'"{proc.pid}"' in b)
        receipts["f_sinkinput_fulltext"] = {"pid": proc.pid, "block": keep[:6000]}
        receipts["f_sinkinput_json"] = stream_snapshot(proc.pid, "sink-inputs")
        clients = L.run_bounded(["pactl", "list", "clients"], timeout=6)["stdout"]
        cblocks = clients.split("\n\n")
        receipts["f_client_fulltext"] = {"block": "\n\n".join(b for b in cblocks if f'"{proc.pid}"' in b)[:4000]}
        proc.communicate(timeout=8)
        receipts["f_sinkinput_fulltext"]["rc"] = proc.returncode
        # capture-stream introspection: source-output full text
        env2 = L.base_env(); env2.update({"PULSE_SOURCE": SEAT + ".monitor"})
        p2 = subprocess.Popen(["parec", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", SEAT + ".monitor"],
                              env=env2, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                              start_new_session=True, preexec_fn=L._limits)
        time.sleep(0.6)
        so = L.run_bounded(["pactl", "list", "source-outputs"], timeout=6)["stdout"]
        sob = "\n\n".join(b for b in so.split("\n\n") if f'"{p2.pid}"' in b)
        receipts["f_sourceoutput_fulltext"] = {"pid": p2.pid, "block": sob[:5000]}
        try:
            os.killpg(p2.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        p2.communicate(timeout=6)
        # subscribe events around a stream lifecycle
        sub = subprocess.Popen(["pactl", "subscribe"], env=L.base_env(), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True, preexec_fn=L._limits)
        time.sleep(0.4)
        env3 = L.base_env(); env3.update({"PULSE_SINK": SEAT})
        p3 = subprocess.Popen(["paplay", TONE], env=env3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              start_new_session=True, preexec_fn=L._limits)
        time.sleep(0.6)
        try:
            os.killpg(sub.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        sub_out, _ = sub.communicate(timeout=6)
        p3.communicate(timeout=8)
        receipts["f_subscribe"] = {"events": sub_out.decode("utf-8", "replace")[:3000]}
        receipts["f_stat"] = L.run_bounded(["pactl", "stat"], timeout=6)
        # native (non-pulse) stream: Corked field derivation (pulse.corked absent -> state != RUNNING)
        fifo = os.path.join(ROOT, "scratch", "r96s_fifo")
        if os.path.exists(fifo):
            os.unlink(fifo)
        os.mkfifo(fifo)
        env4 = L.base_env()
        p4 = subprocess.Popen(["pw-play", "--target", SEAT, fifo], env=env4,
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                              start_new_session=True, preexec_fn=L._limits)
        time.sleep(0.6)
        rows4, _ = L.pactl_json(["list", "sink-inputs"])
        mine4 = [r for r in (rows4 or []) if str(r.get("properties", {}).get("application.process.id")) == str(p4.pid)]
        receipts["f_native_idle_corked"] = {
            "pid": p4.pid,
            "rows": [{"index": r.get("index"), "corked": r.get("corked"),
                      "props": {k: r.get("properties", {}).get(k) for k in
                                ("pulse.corked", "application.name", "media.class", "client.api", "node.name")}} for r in mine4],
        }
        try:
            os.killpg(p4.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        p4.communicate()

    payload = {
        "battery": "r96s_cli",
        "started": t_start,
        "finished": time.time(),
        "seat_sink": SEAT,
        "seat_sink_index": L.seat_sink_index(),
        "receipts": receipts,
    }
    path = L.write_receipt(f"r96s_cli_{only}.json", payload)
    print("wrote", path)
    # short summary
    for k, v in receipts.items():
        if isinstance(v, dict) and "results" in v:
            rcs = [r["rc"] for r in v["results"]]
            print(f"  {k}: rc={rcs}")
        else:
            print(f"  {k}: (meta)")


if __name__ == "__main__":
    main()
