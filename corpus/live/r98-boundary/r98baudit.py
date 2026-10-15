#!/usr/bin/env python3
"""Receipt audit — do the r98-scout receipts actually support the r98-scout report?

Zero-load, read-only pass over the scout's own battery JSONs:
  * per-leg-type variance across reps (the report claims only ticks/timestamps vary)
  * the exact values the report asserts (geometry, param ids, tids, rc lattice,
    drain cadence, xrun counters)
"""
import json
import sys
from pathlib import Path

SC = Path(__file__).resolve().parent.parent / "r98-scout" / "receipts"
OUT = Path(__file__).resolve().parent / "scratch" / "audit-scout-receipts.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

VOLATILE = {"ticks", "now", "t_first_cb_ms", "t_streaming_ms", "t_connect_ms",
            "t_end_ms", "cb_log", "last_bufid", "wall_ms", "utc_start", "utc_end",
            "stdout_sha", "stderr_sha", "stdout_len", "stderr_len", "_events",
            "loadavg", "proc_tid", "main_tid", "stall_start_ms", "stall_end_ms",
            "stall_gap_ms", "first_drained_ms", "n_drained", "n_param_changed",
            "trigger_count", "n_io_changed", "n_control_info", "cb_count", "cb_bytes",
            "queued", "buffered", "queued_buffers", "avail_buffers", "size", "delay",
            "last_chunk_size", "last_stride", "last_maxsize", "last_nbufs",
            "n_add_buffer", "n_remove_buffer", "fmt_seen", "fmt_format", "fmt_rate",
            "fmt_channels", "node_id", "node_id_final", "set_active_rc",
            "activate_done", "trigger_done", "trigger_rc", "n_trigger_done",
            "dequeue_null", "queue_err", "add_buffer_data_null", "is_driving",
            "is_lazy", "cap_frames", "cap_nz", "cap_peak", "cap_rms",
            "g997_mag2", "g440_mag2", "param_ids", "time_rc_after", "rate_num",
            "rate_denom", "proc_sched", "proc_prio", "proc_nice", "main_sched",
            "main_prio", "stream_error", "state", "connect_rc", "connect2_rc",
            "update_params_rc", "flush_rc", "set_active_pre_rc", "get_time_pre_rc",
            "disconnect_pre_rc", "flush_pre_rc", "set_rate_pre_rc", "dequeue_pre_rc",
            "queue_pre_rc", "get_time_after_deactivate_rc", "set_active_false_rc",
            "set_rate_rc", "core_cookie", "exit"}

res = {"sources": [], "variance": {}, "pins": {}}
legs = []
for f in ("battery-all.json", "battery-followup.json", "battery-drain2.json",
          "battery-time.json", "battery-info.json"):
    p = SC / f
    if not p.exists():
        continue
    arr = json.loads(p.read_text())
    res["sources"].append({"file": f, "n_legs": len(arr)})
    for r in arr:
        r["_src"] = f
        legs.append(r)

by_type = {}
for r in legs:
    by_type.setdefault(r["leg"], []).append(r)

print(f"total legs across scout batteries: {len(legs)}; types: {len(by_type)}")
print("\n== per-type variance across reps (non-volatile fields that differ) ==")
for t, rs in sorted(by_type.items()):
    if len(rs) < 2:
        continue
    keys = set()
    for r in rs:
        keys |= set(r.get("parsed", {}).keys())
    diff = []
    for k in sorted(keys):
        vals = []
        for r in rs:
            v = r.get("parsed", {}).get(k)
            if isinstance(v, list):
                v = tuple(v)
            vals.append(v)
        if len(set(map(repr, vals))) > 1:
            diff.append({k: [repr(v) for v in vals]})
    stable = [d for d in diff if list(d)[0] not in VOLATILE]
    unstable_vol = [d for d in diff if list(d)[0] in VOLATILE]
    res["variance"][t] = {"n": len(rs), "diff_fields": [list(d)[0] for d in diff],
                          "stable_diff": stable, "volatile_diff": [list(d)[0] for d in unstable_vol]}
    if stable:
        print(f"  {t} ({len(rs)} reps): NON-VOLATILE DIFF -> {stable}")
    elif diff:
        print(f"  {t} ({len(rs)} reps): only volatile/timing fields differ "
              f"({[list(d)[0] for d in diff]})")
    else:
        print(f"  {t} ({len(rs)} reps): byte-identical parsed fields")

print("\n== rc census ==")
rcs = {}
for r in legs:
    rcs.setdefault(r["leg"], []).append(r["rc"])
for t, v in sorted(rcs.items()):
    if len(set(map(repr, v))) > 1:
        print(f"  {t}: rc varies across reps -> {v}")

print("\n== report-asserted pins, read back from receipts ==")
want = {
    "run_autoconnect": ["state", "cb_count", "last_maxsize", "last_bufid", "last_stride",
                        "last_nbufs", "param_ids", "fmt_format", "fmt_rate", "fmt_channels",
                        "n_add_buffer", "proc_tid", "main_tid", "proc_sched", "proc_prio"],
    "state": ["connect_rc", "node_id", "get_time_pre_rc", "node_id_final", "disconnect_rc"],
    "dont_reconnect": ["node.dont-reconnect", "node.autoconnect"],
    "dont_reconnect_false_prop": ["node.dont-reconnect"],
    "inactive_activate": ["state", "cb_count", "set_active_rc"],
    "trigger": ["state", "cb_count", "trigger_count", "trigger_rc"],
    "rt_process": ["proc_tid", "main_tid", "proc_sched", "proc_prio", "proc_nice"],
    "time": ["rate_num", "rate_denom", "queued", "queued_buffers", "size", "delay",
             "set_rate_rc", "set_active_false_rc", "is_driving", "is_lazy"],
    "drain_cb": ["flush_rc", "n_drained", "first_drained_ms", "state", "cb_count"],
    "drain_timer2": ["flush_rc", "n_drained", "first_drained_ms", "state", "cb_count"],
    "neg_stream": ["param_ids", "update_params_rc", "n_param_changed", "state"],
    "err_set_active_pre": ["set_active_pre_rc", "get_time_pre_rc", "disconnect_pre_rc",
                           "flush_pre_rc", "set_rate_pre_rc", "dequeue_pre_rc", "queue_pre_rc"],
    "err_connect_twice": ["connect_rc", "connect2_rc"],
    "err_bad_direction": ["connect_rc", "state"],
    "err_no_params": ["connect_rc", "state"],
    "remote_bad": ["connect_rc", "errno"],
    "cap_prop": ["state", "cb_count", "cap_frames", "cap_peak", "g997_mag2", "g440_mag2"],
    "cap_noprop": ["state", "stream_error", "cb_count"],
    "cap_default_source": ["state", "stream_error"],
    "media_class_sink": ["state", "stream_error"],
    "media_class_source": ["state", "stream_error", "param_ids"],
    "s16_format": ["last_maxsize", "last_stride", "fmt_format"],
    "quantum512": ["last_maxsize", "last_bufid", "size", "delay"],
    "quantum2048": ["last_maxsize", "last_bufid", "size", "delay"],
    "stall": ["state", "cb_count"],
}
for t in sorted(want):
    rs = by_type.get(t)
    if not rs:
        continue
    print(f"\n  [{t}]")
    for r in rs:
        vals = {k: r["parsed"].get(k) for k in want[t] if k in r["parsed"]}
        extra = ""
        if "profiler" in r:
            extra = f" profiler={ {k: r['profiler'].get(k) for k in ('follower_xrun_max','driver_xrun_max','follower_negative_wait_records','follower_statuses')} }"
        if "pwtop" in r:
            extra += f" pwtop_rows={ {k: v[:1] for k, v in list(r['pwtop'].get('rows', {}).items())[:2]} }"
        print(f"    r{r['rep']} rc={r['rc']} {json.dumps(vals)}{extra}")
        res["pins"].setdefault(t, []).append({"rep": r["rep"], "rc": r["rc"], "vals": vals,
                                              "profiler": r.get("profiler")})

OUT.write_text(json.dumps(res, indent=1))
print(f"\nwrote {OUT}")
