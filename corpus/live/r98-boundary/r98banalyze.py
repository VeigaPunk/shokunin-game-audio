#!/usr/bin/env python3
"""r98b analysis — turn the boundary batteries into a verdict table.

Usage: r98banalyze.py <battery-file> [<battery-file> ...]
Prints one compact line per (leg, rep) with the law-relevant fields, plus a
per-leg-type consensus summary and a quiet-vs-load diff when both are given.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REC = ROOT / "receipts"

FIELDS = [
    "state", "connect_rc", "connect2_rc", "node_id", "node_id_final",
    "get_time_pre_rc", "get_time_after_deactivate_rc", "disconnect_rc",
    "set_active_pre_rc", "flush_pre_rc", "set_rate_pre_rc", "dequeue_pre_rc",
    "queue_pre_rc", "set_active_rc", "set_rate_rc", "set_active_false_rc",
    "cb_count", "last_maxsize", "last_bufid", "last_nbufs", "last_stride",
    "last_chunk_size", "fmt_format", "fmt_rate", "fmt_channels", "param_ids",
    "n_param_changed", "update_params_rc", "n_add_buffer", "n_drained",
    "first_drained_ms", "trigger_count", "trigger_rc", "n_trigger_done",
    "proc_tid", "main_tid", "proc_sched", "proc_prio", "proc_nice",
    "stream_error", "rate_num", "rate_denom", "ticks", "delay", "queued",
    "buffered", "queued_buffers", "avail_buffers", "size", "is_driving",
    "is_lazy", "cap_frames", "cap_peak", "g997_mag2", "g440_mag2",
    "dequeue_null", "queue_err", "add_buffer_data_null", "cb_log",
    "stall_start_ms", "stall_end_ms", "stall_gap_ms", "t_first_cb_ms",
    "t_streaming_ms",
]
SHORT = {"state": "state", "cb_count": "cb", "last_maxsize": "maxsize",
         "last_bufid": "req", "last_nbufs": "nbufs", "last_stride": "stride",
         "fmt_format": "fmt", "fmt_rate": "frate", "param_ids": "pids",
         "stream_error": "err", "delay": "delay", "size": "size",
         "queued": "queued", "n_drained": "ndrain", "first_drained_ms": "1stdrain",
         "trigger_count": "ntrig", "trigger_rc": "trc", "proc_tid": "ptid",
         "main_tid": "mtid", "proc_sched": "psched", "cb_log": "cblog"}


def load(f):
    return json.loads(Path(f).read_text())


def verdict(r):
    p = r["parsed"]
    out = {}
    for k in FIELDS:
        if k not in p:
            continue
        v = p[k]
        if k in ("cb_log",):
            try:
                ts = [int(x) for x in str(v).split(",") if x.strip()]
                out["cblog_n"] = len(ts)
                if len(ts) > 1:
                    d = [ts[i + 1] - ts[i] for i in range(len(ts) - 1)]
                    out["cb_gap_ms"] = f"{min(d)}-{max(d)}/med{int(sorted(d)[len(d)//2])}"
            except Exception:
                pass
            continue
        if k in ("proc_tid", "main_tid") and isinstance(v, str) and " " in v:
            out[k] = v.split()[0]
            continue
        out[k] = v
    if "snapshot" in r:
        out["links"] = [[l["out"], l["in"], l.get("id")] for l in r["snapshot"]["links"]]
    if "profiler" in r and isinstance(r["profiler"], dict):
        pr = r["profiler"]
        out["pxrun"] = pr.get("follower_xrun_max")
        out["dxrun"] = pr.get("driver_xrun_max")
        out["negwait"] = pr.get("follower_negative_wait_records")
        out["pstat"] = pr.get("follower_statuses")
    if "pwtop" in r and isinstance(r["pwtop"], dict):
        rows = r["pwtop"].get("rows", {})
        errs = {}
        for nm, rr in rows.items():
            for row in rr:
                if len(row) >= 9 and row[8].isdigit() and row[0] in ("R",):
                    errs[nm] = row[8]
        out["pwtop_err"] = errs
    return out


def main():
    files = sys.argv[1:] or [str(REC / "battery-quiet.json")]
    data = {}
    for f in files:
        tag = Path(f).stem.replace("battery-", "")
        data[tag] = load(f)
    for tag, arr in data.items():
        print(f"\n===== {tag}: {len(arr)} legs, "
              f"loadavg {arr[0]['loadavg_before']} .. {arr[-1]['loadavg_after']} =====")
        by = {}
        for r in arr:
            by.setdefault(r["leg"], []).append(r)
        for leg, rs in by.items():
            print(f"\n-- {leg} ({len(rs)} reps, rc={[r['rc'] for r in rs]})")
            for r in rs:
                v = verdict(r)
                s = {SHORT.get(k, k): v[k] for k in v if k in SHORT}
                extra = {k: v[k] for k in v if k not in SHORT}
                print(f"   r{r['rep']}: {json.dumps(s)}")
                if extra:
                    print(f"        {json.dumps(extra)[:400]}")
    if len(data) == 2:
        tags = list(data)
        a, b = data[tags[0]], data[tags[1]]
        print(f"\n===== quiet-vs-load diff ({tags[0]} vs {tags[1]}) =====")
        for leg in sorted(set(r["leg"] for r in a) & set(r["leg"] for r in b)):
            va = [verdict(r) for r in a if r["leg"] == leg]
            vb = [verdict(r) for r in b if r["leg"] == leg]
            keys = set()
            for v in va + vb:
                keys |= set(v)
            diffs = {}
            for k in sorted(keys):
                sa = sorted(set(repr(v.get(k)) for v in va))
                sb = sorted(set(repr(v.get(k)) for v in vb))
                if sa != sb:
                    diffs[k] = {"quiet": sa, "load": sb}
            if diffs:
                print(f"\n-- {leg}")
                for k, d in diffs.items():
                    print(f"     {k}: {json.dumps(d)[:300]}")


if __name__ == "__main__":
    main()
