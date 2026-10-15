#!/usr/bin/env python3
"""r96-boundary battery A — replay of the r96 scout's pulse CLI cells under
controlled conditions (tag = quiet|load), plus new falsifiers.

Every leg: fresh process, wall cap + process-group kill + byte caps, loadavg
recorded. Seat objects only (r96b_*); playback targets the seat null sink
unless the cell is about fallback routing (then a -60 dBFS quiet tone).

Groups: avail server target latency props introspect
Usage: r96b_cli.py GROUP TAG
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r96b_lib as L  # noqa: E402

ROOT = L.ROOT
SEAT = L.SEAT_SINK_NAME
TONE = os.path.join(ROOT, "scratch", "tone1k5.wav")
QUIET = os.path.join(ROOT, "scratch", "tone1k5_quiet.wav")


def runlog(tag):
    return os.path.join(ROOT, "runs", f"batteryA_{tag}.log")


def stream_snapshot(pid, kind="sink-inputs"):
    rows, meta = L.pactl_json(["list", kind])
    mine, others = [], []
    for row in rows or []:
        props = row.get("properties", {})
        if str(props.get("application.process.id")) == str(pid):
            mine.append(row)
        else:
            others.append({"index": row.get("index"), "app": props.get("application.name"), "client.api": props.get("client.api")})
    return mine, {"all_count": len(rows or []), "foreign": others[:8], **meta}


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


def slim_rows(rows):
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
            "source_latency_usec": row.get("source_latency_usec"),
            "resample_method": row.get("resample_method"),
            "props": {k: props.get(k) for k in (
                "pulse.corked", "pulse.attr.tlength", "pulse.attr.prebuf",
                "pulse.attr.minreq", "pulse.attr.maxlength", "node.latency",
                "node.rate", "media.role", "application.name", "media.name",
                "zzz.invented", "zzz.empty", "state.restore-props", "target.object",
                "application.process.binary", "client.api",
            ) if k in props},
        })
    return slim


def leg_stream(name, argv, env_extra=None, reps=3, timeout=9.0, snapshot_at=0.35,
               snapshot_kind="sink-inputs", kill_after_snapshot=False):
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
        dflt = L.run_bounded(["pactl", "get-default-sink"], env=L.base_env(), timeout=4)["stdout"].strip()
        results.append({
            "rep": rep, "argv": argv, "env_extra": env_extra or {},
            "rc": proc.returncode, "timed_out": timed_out,
            "wall_s": round(time.monotonic() - t0, 4),
            "loadavg": L.loadavg(),
            "session_default_sink": dflt,
            "stdout": out[:4000].decode("utf-8", "replace"),
            "stderr": err[:4000].decode("utf-8", "replace"),
            "my_streams": slim_rows(rows), "snapshot_meta": snap[1] if snap else None,
        })
        L.log_line(runlog(name), f"{name} rep{rep} rc={proc.returncode} wall={results[-1]['wall_s']} streams={json.dumps(slim_rows(rows))[:300]}")
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
        L.log_line(runlog(name), f"{name} rep{rep} rc={r['rc']} timed_out={r['timed_out']} wall={r['wall_s']} err={r['stderr'][:120]!r}")
    return {"leg": name, "results": results}


def restore_rows():
    return L.restore_rows()


def group_avail():
    rec = {}
    rec["a1_versions"] = {t: L.run_bounded([t, "--version"], timeout=4) for t in ("pactl", "pacat", "paplay", "parec")}
    rec["a1_which"] = {}
    for t in ("pactl", "pacat", "paplay", "parec", "parecord", "pamon", "pacmd", "pa-info", "pax11publish", "pw-pulse"):
        r = L.run_bounded(["which", t], timeout=4)
        rec["a1_which"][t] = {"rc": r["rc"], "path": r["stdout"].strip()}
    rec["a1_symlinks"] = L.run_bounded(["ls", "-l", "/usr/bin/paplay", "/usr/bin/parec", "/usr/bin/pacat", "/usr/bin/pactl"], timeout=4)["stdout"]
    rec["a1_sha"] = {t: L.run_bounded(["sha256sum", p], timeout=4)["stdout"].strip() for t, p in
                     (("pacat", "/usr/bin/pacat"), ("pactl", "/usr/bin/pactl")) if os.path.exists(p)}
    rec["a1_pacmd_equiv"] = {v: L.run_bounded(["pactl", v], timeout=5) for v in ("kill-sink-input", "kill-source-output", "dump")}
    rec["a1_json_modules_short"] = L.run_bounded(["pactl", "-f", "json", "list", "modules", "short"], timeout=6)["stdout"][:600]
    return rec


def group_server():
    rec = {}
    uid = os.getuid()
    rec["b_default"] = leg_cmd("b_default", ["pactl", "info"])
    rec["b_unix_prefix"] = leg_cmd("b_unix_prefix", ["pactl", "info"], {"PULSE_SERVER": f"unix:/run/user/{uid}/pulse/native"})
    rec["b_bare_path"] = leg_cmd("b_bare_path", ["pactl", "info"], {"PULSE_SERVER": f"/run/user/{uid}/pulse/native"})
    rec["b_unix_missing"] = leg_cmd("b_unix_missing", ["pactl", "info"], {"PULSE_SERVER": "unix:/nonexistent"})
    rec["b_tcp_refused"] = leg_cmd("b_tcp_refused", ["pactl", "info"], {"PULSE_SERVER": "tcp:127.0.0.1:4713"})
    rec["b_host_bogus"] = leg_cmd("b_host_bogus", ["pactl", "info"], {"PULSE_SERVER": "nonexistent-r96b"}, reps=2, timeout=16)
    rec["b_runtime_path"] = leg_cmd("b_runtime_path", ["pactl", "info"], {"PULSE_RUNTIME_PATH": "/tmp/r96b_nope"})
    rec["b_empty_server"] = leg_cmd("b_empty_server", ["pactl", "info"], {"PULSE_SERVER": ""})
    rec["b_cookie_devnull"] = leg_cmd("b_cookie_devnull", ["pactl", "info"], {"PULSE_COOKIE": "/dev/null"})
    rec["b_flag_beats_env"] = leg_cmd("b_flag_beats_env", ["pactl", "-s", f"unix:/run/user/{uid}/pulse/native", "info"], {"PULSE_SERVER": "tcp:127.0.0.1:1"})
    rec["b_env_loses_to_flag"] = leg_cmd("b_env_loses_to_flag", ["pactl", "-s", "tcp:127.0.0.1:1", "info"], {"PULSE_SERVER": f"unix:/run/user/{uid}/pulse/native"})
    # new axis: global option after the subcommand
    rec["b_flag_after_cmd"] = leg_cmd("b_flag_after_cmd", ["pactl", "info", "-s", f"unix:/run/user/{uid}/pulse/native"], reps=2)
    # new axis: tcp6 + trailing-slash unix path
    rec["b_tcp6_refused"] = leg_cmd("b_tcp6_refused", ["pactl", "info"], {"PULSE_SERVER": "tcp6:[::1]:4713"}, reps=2)
    rec["b_unix_trailing_slash"] = leg_cmd("b_unix_trailing_slash", ["pactl", "info"], {"PULSE_SERVER": f"unix:/run/user/{uid}/pulse/native/"}, reps=2)
    cc = os.path.join(ROOT, "scratch", "r96b_client_badserver.conf")
    with open(cc, "w") as fh:
        fh.write("default-server = tcp:127.0.0.1:1\n")
    rec["b_clientconfig_badserver"] = leg_cmd("b_clientconfig_badserver", ["pactl", "info"], {"PULSE_CLIENTCONFIG": cc})
    return rec


def group_target():
    rec = {}
    L.ensure_sink()
    rec["c_env_sink_seat"] = leg_stream("c_env_sink_seat", ["paplay", QUIET], {"PULSE_SINK": SEAT})
    rec["c_env_sink_default"] = leg_stream("c_env_sink_default", ["paplay", QUIET], {"PULSE_SINK": "@DEFAULT_SINK@"})
    rec["c_env_sink_missing"] = leg_stream("c_env_sink_missing", ["paplay", QUIET], {"PULSE_SINK": "no_such_r96b"})
    seat_idx = str(L.seat_sink_index())
    rec["c_env_sink_index"] = leg_stream("c_env_sink_index", ["paplay", QUIET], {"PULSE_SINK": seat_idx})
    rec["c_env_sink_badindex"] = leg_stream("c_env_sink_badindex", ["paplay", QUIET], {"PULSE_SINK": "999999"})
    rec["c_env_sink_monitor"] = leg_stream("c_env_sink_monitor", ["paplay", QUIET], {"PULSE_SINK": SEAT + ".monitor"})
    rec["c_env_sink_empty"] = leg_stream("c_env_sink_empty", ["paplay", QUIET], {"PULSE_SINK": ""})
    rec["c_flag_beats_env"] = leg_stream("c_flag_beats_env", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", "@DEFAULT_SINK@", QUIET], {"PULSE_SINK": SEAT})
    rec["c_flag_seat"] = leg_stream("c_flag_seat", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", SEAT, QUIET], {"PULSE_SINK": "@DEFAULT_SINK@"})
    rec["c_source_seat_monitor"] = leg_stream(
        "c_source_seat_monitor", ["parec", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", SEAT + ".monitor"],
        {"PULSE_SOURCE": SEAT + ".monitor"}, snapshot_kind="source-outputs", kill_after_snapshot=True, snapshot_at=0.6)
    rec["c_source_default"] = leg_stream(
        "c_source_default", ["parec", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", "@DEFAULT_SOURCE@"],
        {"PULSE_SOURCE": "@DEFAULT_SOURCE@"}, snapshot_kind="source-outputs", kill_after_snapshot=True, snapshot_at=0.5)
    rec["c_source_missing"] = leg_stream(
        "c_source_missing", ["parec", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", "no_such_r96b"],
        {"PULSE_SOURCE": "no_such_r96b"}, snapshot_kind="source-outputs", kill_after_snapshot=True, snapshot_at=0.5)
    rec["c_pacat_default_monitor"] = leg_stream(
        "c_pacat_default_monitor", ["pacat", "--record", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", "@DEFAULT_MONITOR@"],
        snapshot_kind="source-outputs", kill_after_snapshot=True, snapshot_at=0.5)
    # new: client-side default-node state (PULSE_CLIENTCONFIG default-sink) with an
    # unresolvable PULSE_SINK -> which default does the fallback use?
    cc2 = os.path.join(ROOT, "scratch", "r96b_client_defaultsink.conf")
    with open(cc2, "w") as fh:
        fh.write(f"default-sink = {SEAT}\n")
    rec["c_clientconf_defaultsink_nosink"] = leg_stream(
        "c_clientconf_defaultsink_nosink", ["paplay", QUIET], {"PULSE_CLIENTCONFIG": cc2, "PULSE_SINK": "no_such_r96b"})
    rec["c_clientconf_defaultsink_plain"] = leg_stream(
        "c_clientconf_defaultsink_plain", ["paplay", QUIET], {"PULSE_CLIENTCONFIG": cc2})
    # new: option after the positional file argument (CLI order axis)
    rec["c_flag_after_file"] = leg_stream(
        "c_flag_after_file", ["paplay", QUIET, "--device=" + SEAT], reps=2)
    # new: target a live foreign null sink by name if one exists (read-only contact)
    foreign = None
    sinks, _ = L.pactl_json(["list", "sinks", "short"])
    for s in sinks or []:
        n = str(s.get("name", ""))
        if n.startswith("r9") and not n.startswith("r96b") and n.endswith("_ns"):
            foreign = n
            break
    rec["c_foreign_target_note"] = {"foreign_sink": foreign}
    if foreign:
        rec["c_foreign_target"] = leg_stream("c_foreign_target", ["paplay", QUIET], {"PULSE_SINK": foreign}, reps=2)
    return rec


def group_latency():
    rec = {}
    L.ensure_sink()
    rec["d_default"] = leg_stream("d_default", ["paplay", TONE], {"PULSE_SINK": SEAT})
    rec["d_env100"] = leg_stream("d_env100", ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": "100"})
    rec["d_flag100"] = leg_stream("d_flag100", ["pacat", "--playback", "--latency-msec=100", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT})
    rec["d_env250_flag100"] = leg_stream("d_env250_flag100", ["pacat", "--playback", "--latency-msec=100", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": "250"})
    rec["d_env100_flag250"] = leg_stream("d_env100_flag250", ["pacat", "--playback", "--latency-msec=250", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": "100"})
    for tag, val in (("zero", "0"), ("neg", "-5"), ("nan", "abc"), ("empty", "")):
        rec[f"d_env_{tag}"] = leg_stream(f"d_env_{tag}", ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": val})
    # new parse falsifiers (pa_atou: base 0, full-string, uint32)
    for tag, val in (("hex64", "0x64"), ("space100", " 100"), ("plus100", "+100"),
                     ("float", "100.5"), ("exp", "1e3"), ("overflow", "99999999999")):
        rec[f"d_env_{tag}"] = leg_stream(f"d_env_{tag}", ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": val}, reps=2)
    rec["d_env_huge"] = leg_stream("d_env_huge", ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": "100000"}, reps=2)
    matrix = {}
    for m in ("10", "20", "50", "200", "500", "1000", "2000"):
        matrix[m] = leg_stream(f"d_matrix_{m}", ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": m}, reps=1)
    rec["d_matrix"] = matrix
    rec["d_proctime5"] = leg_stream("d_proctime5", ["pacat", "--playback", "--process-time-msec=5", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT})
    rec["d_latency_bytes"] = leg_stream("d_latency_bytes", ["pacat", "--playback", "--latency=9600", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT})
    rec["d_proctime_bytes"] = leg_stream("d_proctime_bytes", ["pacat", "--playback", "--process-time=480", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT})
    rec["d_stereo100"] = leg_stream("d_stereo100", ["pacat", "--playback", "--latency-msec=100", "--raw", "--rate=48000", "--format=s16le", "--channels=2", TONE], {"PULSE_SINK": SEAT})
    rec["d_f32_100"] = leg_stream("d_f32_100", ["pacat", "--playback", "--latency-msec=100", "--raw", "--rate=48000", "--format=f32le", "--channels=1", TONE], {"PULSE_SINK": SEAT})
    # new CLI order axis: latency flag before vs after the device flag
    rec["d_order_lat_dev"] = leg_stream("d_order_lat_dev", ["pacat", "--playback", "--latency-msec=100", "--device=" + SEAT, "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], reps=2)
    rec["d_order_dev_lat"] = leg_stream("d_order_dev_lat", ["pacat", "--playback", "--device=" + SEAT, "--latency-msec=100", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], reps=2)
    # new: process-time + latency combined, both orders
    rec["d_proc_then_lat"] = leg_stream("d_proc_then_lat", ["pacat", "--playback", "--process-time-msec=5", "--latency-msec=100", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT}, reps=2)
    rec["d_lat_then_proc"] = leg_stream("d_lat_then_proc", ["pacat", "--playback", "--latency-msec=100", "--process-time-msec=5", "--raw", "--rate=48000", "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT}, reps=2)
    return rec


def group_props():
    rec = {}
    L.ensure_sink()
    rec["e_props"] = leg_stream(
        "e_props", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                    "--property=media.role=game", "--property=application.name=r96b_prop",
                    "--property=zzz.invented=42", "--stream-name=r96b_streamname", TONE],
        {"PULSE_SINK": SEAT})
    rec["e_props_malformed"] = leg_stream(
        "e_props_malformed", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                              "--property=noequals", TONE], {"PULSE_SINK": SEAT}, reps=2)
    # new: property order + duplicate key + empty value
    rec["e_props_order"] = leg_stream(
        "e_props_order", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                          "--stream-name=r96b_streamname", "--property=zzz.invented=42",
                          "--property=application.name=r96b_prop", "--property=media.role=game", TONE],
        {"PULSE_SINK": SEAT}, reps=2)
    rec["e_props_dup"] = leg_stream(
        "e_props_dup", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                        "--property=media.role=first", "--property=media.role=second", TONE],
        {"PULSE_SINK": SEAT}, reps=2)
    rec["e_props_empty"] = leg_stream(
        "e_props_empty", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                          "--property=zzz.empty=", TONE], {"PULSE_SINK": SEAT}, reps=2)
    rec["e_stream_vs_media"] = leg_stream(
        "e_stream_vs_media", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                              "--property=media.name=r96b_fromprop", "--stream-name=r96b_fromflag", TONE],
        {"PULSE_SINK": SEAT}, reps=2)
    rec["e_envprop_vs_cli"] = leg_stream(
        "e_envprop_vs_cli", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                             "--property=application.name=r96b_cli", TONE],
        {"PULSE_SINK": SEAT, "PULSE_PROP": "application.name=r96b_env"})
    rec["e_client_name"] = leg_stream(
        "e_client_name", ["pacat", "--playback", "--client-name=r96b_client", "--raw", "--rate=48000",
                          "--format=s16le", "--channels=1", TONE], {"PULSE_SINK": SEAT})
    # restore-props suppression: playback, then capture (scout unknown #6)
    rows_before = restore_rows()
    rec["e_restore_off"] = leg_stream(
        "e_restore_off", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                          "--property=state.restore-props=false", TONE], {"PULSE_SINK": SEAT})
    time.sleep(1.6)
    rec["e_restore_off"]["rows_before"] = rows_before
    rec["e_restore_off"]["rows_after"] = restore_rows()
    rows_before2 = restore_rows()
    rec["e_restore_off_record"] = leg_stream(
        "e_restore_off_record", ["pacat", "--record", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                                 "-d", SEAT + ".monitor", "--property=state.restore-props=false"],
        snapshot_kind="source-outputs", kill_after_snapshot=True, snapshot_at=0.6)
    time.sleep(1.6)
    rec["e_restore_off_record"]["rows_before"] = rows_before2
    rec["e_restore_off_record"]["rows_after"] = restore_rows()
    return rec


def group_introspect():
    rec = {}
    L.ensure_sink()
    env = L.base_env(); env.update({"PULSE_SINK": SEAT})
    proc = subprocess.Popen(["paplay", TONE], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True, preexec_fn=L._limits)
    time.sleep(0.4)
    full = L.run_bounded(["pactl", "list", "sink-inputs"], timeout=6)["stdout"]
    blocks = full.split("\n\n")
    keep = "\n\n".join(b for b in blocks if f'"{proc.pid}"' in b)
    rec["f_sinkinput_fulltext"] = {"pid": proc.pid, "block": keep[:6000]}
    rec["f_sinkinput_json"] = {"rows": slim_rows(stream_snapshot(proc.pid, "sink-inputs")[0])}
    clients = L.run_bounded(["pactl", "list", "clients"], timeout=6)["stdout"]
    cblocks = clients.split("\n\n")
    rec["f_client_fulltext"] = {"block": "\n\n".join(b for b in cblocks if f'"{proc.pid}"' in b)[:4000]}
    proc.communicate(timeout=8)
    rec["f_sinkinput_fulltext"]["rc"] = proc.returncode
    # short forms
    rec["f_sinkinputs_short"] = L.run_bounded(["pactl", "list", "sink-inputs", "short"], timeout=6)["stdout"][:1500]
    rec["f_clients_short"] = L.run_bounded(["pactl", "list", "clients", "short"], timeout=6)["stdout"][:2500]
    # capture introspection: source-output full text + latency fields
    env2 = L.base_env(); env2.update({"PULSE_SOURCE": SEAT + ".monitor"})
    p2 = subprocess.Popen(["parec", "--raw", "--rate=48000", "--format=s16le", "--channels=1", "-d", SEAT + ".monitor"],
                          env=env2, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                          start_new_session=True, preexec_fn=L._limits)
    time.sleep(0.6)
    so = L.run_bounded(["pactl", "list", "source-outputs"], timeout=6)["stdout"]
    sob = "\n\n".join(b for b in so.split("\n\n") if f'"{p2.pid}"' in b)
    rec["f_sourceoutput_fulltext"] = {"pid": p2.pid, "block": sob[:5000]}
    rec["f_sourceoutput_json"] = {"rows": slim_rows(stream_snapshot(p2.pid, "source-outputs")[0])}
    try:
        os.killpg(p2.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    p2.communicate(timeout=6)
    # native (non-pulse) stream: Corked field derivation (pulse.corked absent -> state != RUNNING)
    fifo = os.path.join(ROOT, "scratch", "r96b_fifo")
    if os.path.exists(fifo):
        os.unlink(fifo)
    os.mkfifo(fifo)
    p4 = subprocess.Popen(["pw-play", "--target", SEAT, fifo], env=L.base_env(),
                          stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                          start_new_session=True, preexec_fn=L._limits)
    time.sleep(0.6)
    rows4, _ = L.pactl_json(["list", "sink-inputs"])
    mine4 = [r for r in (rows4 or []) if str(r.get("properties", {}).get("application.process.id")) == str(p4.pid)]
    rec["f_native_idle_corked"] = {
        "pid": p4.pid,
        "rows": [{"index": r.get("index"), "corked": r.get("corked"),
                  "props": {k: r.get("properties", {}).get(k) for k in
                            ("pulse.corked", "application.name", "media.class", "client.api", "node.name")}} for r in mine4],
    }
    nodes, _ = L.pw_dump_filtered([str(p4.pid)])
    try:
        os.killpg(p4.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    p4.communicate()
    return rec


def group_extra():
    """Corrected / stronger frame-size falsifiers (the scout's `--format=f32le`
    arm never created a stream: rc 1 `Invalid sample specification`)."""
    rec = {}
    L.ensure_sink()
    rec["z_f32_default"] = leg_stream("z_f32_default", ["pacat", "--playback", "--raw", "--rate=48000",
                                                        "--format=float32le", "--channels=1", TONE],
                                      {"PULSE_SINK": SEAT}, reps=2)
    rec["z_f32_100"] = leg_stream("z_f32_100", ["pacat", "--playback", "--latency-msec=100", "--raw", "--rate=48000",
                                                "--format=float32le", "--channels=1", TONE],
                                  {"PULSE_SINK": SEAT}, reps=3)
    rec["z_s24_100"] = leg_stream("z_s24_100", ["pacat", "--playback", "--latency-msec=100", "--raw", "--rate=48000",
                                                "--format=s24le", "--channels=1", TONE],
                                  {"PULSE_SINK": SEAT}, reps=2)
    rec["z_s24_default"] = leg_stream("z_s24_default", ["pacat", "--playback", "--raw", "--rate=48000",
                                                        "--format=s24le", "--channels=1", TONE],
                                      {"PULSE_SINK": SEAT}, reps=2)
    rec["z_f32le_invalid"] = leg_stream("z_f32le_invalid", ["pacat", "--playback", "--latency-msec=100", "--raw",
                                                            "--rate=48000", "--format=f32le", "--channels=1", TONE],
                                        {"PULSE_SINK": SEAT}, reps=2)
    rec["z_env_parses"] = {
        tag: leg_stream(f"z_env_{tag}", ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": val}, reps=2)
        for tag, val in (("space100", " 100"), ("plus100", "+100"), ("hex100", "0x64"), ("float100", "100.5"))}
    return rec


def group_extra2():
    """Parse-law cells sharpened from the fetched pa_atou source
    (prepare_number_string: rejects isspace/'+'/'-', strips leading zeros unless
    the string starts with lowercase '0x', strtoul base 0, full-string, uint32)
    + the reversed --stream-name/--property=media.name order."""
    rec = {}
    L.ensure_sink()
    cells = {
        "w_parse_0100": "0100",       # zeros stripped -> decimal 100 (not octal 64)
        "w_parse_007": "007",         # -> 7 ms
        "w_parse_0X64": "0X64",       # uppercase X not recognized -> reject
        "w_parse_tab100": "\t100",    # isspace -> reject
        "w_parse_plus0x64": "+0x64",  # '+' -> reject
        "w_parse_minus0x64": "-0x64", # '-' -> reject
        "w_parse_00x64": "00x64",     # zero-strip eats the prefix -> reject
    }
    for tag, val in cells.items():
        rec[tag] = leg_stream(tag, ["paplay", TONE], {"PULSE_SINK": SEAT, "PULSE_LATENCY_MSEC": val}, reps=2)
    rec["w_stream_media_rev"] = leg_stream(
        "w_stream_media_rev", ["pacat", "--playback", "--raw", "--rate=48000", "--format=s16le", "--channels=1",
                               "--stream-name=r96b_rev_flag", "--property=media.name=r96b_rev_prop", TONE],
        {"PULSE_SINK": SEAT}, reps=2)
    return rec


GROUPS = {
    "avail": group_avail,
    "server": group_server,
    "target": group_target,
    "latency": group_latency,
    "props": group_props,
    "introspect": group_introspect,
    "extra": group_extra,
    "extra2": group_extra2,
}


def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "server"
    tag = sys.argv[2] if len(sys.argv) > 2 else "adhoc"
    t_start = time.time()
    receipts = GROUPS[group]()
    payload = {
        "battery": "r96b_cli",
        "group": group,
        "tag": tag,
        "started": t_start,
        "finished": time.time(),
        "loadavg_start": L.loadavg(),
        "seat_sink": SEAT,
        "seat_sink_index": L.seat_sink_index(),
        "receipts": receipts,
    }
    path = L.write_receipt(f"r96b_cli_{group}_{tag}.json", payload)
    print("wrote", path)
    for k, v in receipts.items():
        if isinstance(v, dict) and "results" in v:
            print(f"  {k}: rc={[r['rc'] for r in v['results']]}")
        elif isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, dict) and "results" in vv:
                    print(f"  {k}.{kk}: rc={[r['rc'] for r in vv['results']]}")
                else:
                    print(f"  {k}.{kk}: (meta)")
        else:
            print(f"  {k}: (meta)")


if __name__ == "__main__":
    main()
