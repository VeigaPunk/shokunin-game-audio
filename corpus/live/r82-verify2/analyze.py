#!/usr/bin/env python3
"""r82-verify2 receipt analysis — fold-item spot checks over the run
receipts. Read-only: parses measurements.json + stdout envelopes."""
import json, re, sys
from pathlib import Path

RUNS = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
            "r82-verify2/runs")
EXPECTED_LEGS = {"ffpw_device_surfaces_r82_probe": 8,
                 "ffpw_capture_lattice_r82_probe": 17,
                 "ffpw_playback_lattice_r82_probe": 13,
                 "ffpw_buffer_knobs_r82_probe": 14,
                 "ffpw_target_loss_r82_probe": 8,
                 "ffpw_error_classes_r82_probe": 6,
                 "ffpw_alsa_split_r82_probe": 8,
                 "ffpw_ffplay_ffprobe_r82_probe": 3}

def tone_pair(pid):
    l = 2900.0 + (pid % 4) * 400.0
    return l, l + 560.0

def run_pid(meas):
    pids = set()
    for e in meas.get("measurements", {}).values():
        if not isinstance(e, dict):
            continue
        for k in (e.get("sinks_gone") or {}):
            m = re.fullmatch(r"r82ff_ns_(\d+)", k)
            if m:
                pids.add(int(m.group(1)))
        for k in (e.get("unloads") or {}):
            m = re.fullmatch(r"r82ff_ns_(\d+)", k)
            if m:
                pids.add(int(m.group(1)))
    return pids

def unload_at(leg):
    for f in leg.get("fired") or []:
        if f.get("kind") == "unload_module":
            return f.get("at"), (f.get("result") or {})
    return None, {}

def analyze(tag):
    env = json.loads((RUNS / f"{tag}.stdout.json").read_text())
    receipt = Path(env["receipt"])
    meas = json.loads(receipt.read_text())
    out = {"tag": tag, "receipt": str(receipt), "envelope_failures":
           env.get("failures"), "receipt_sha": None}
    import hashlib
    out["receipt_sha"] = hashlib.sha256(receipt.read_bytes()).hexdigest()
    m = meas["measurements"]
    out["n_measurements"] = len(m)
    legs_total = 0
    per = {}
    for name, want in EXPECTED_LEGS.items():
        e = m.get(name) or {}
        legs = e.get("legs") or {}
        per[name] = {"legs": len(legs), "want": want,
                     "failures": e.get("failures"),
                     "blocked": e.get("blocked"),
                     "coverage_blocked": e.get("coverage_blocked")}
        legs_total += len(legs)
    out["per_entry"] = per
    out["legs_total"] = legs_total
    pids = run_pid(meas)
    out["run_pids"] = sorted(pids)
    out["pid_classes"] = {str(p): {"class": p % 4, "pair": tone_pair(p)}
                          for p in pids}
    # folded-cell checks
    alsa = m.get("ffpw_alsa_split_r82_probe") or {}
    a2 = (alsa.get("legs") or {}).get("a2_hw_free_pwheld") or {}
    a7 = (alsa.get("legs") or {}).get("a7_ch0_option_absent") or {}
    out["a2"] = {"holder_sink": alsa.get("a2_holder_sink"),
                 "holder_consumers": a2.get("holder_consumers"),
                 "exit_code": a2.get("exit_code"),
                 "out_riff": (a2.get("out") or {}).get("riff"),
                 "out_bytes": (a2.get("out") or {}).get("bytes"),
                 "watch_argv": (a2.get("watch_argv") or {}).get("holder")}
    out["a7"] = {"exit_code": a7.get("exit_code"),
                 "error_class": a7.get("error_class"),
                 "error_hit": a7.get("error_hit"),
                 "stderr_head": a7.get("stderr_head"),
                 "argv": a7.get("argv")}
    loss = m.get("ffpw_target_loss_r82_probe") or {}
    t2 = {}
    for rep in range(3):
        leg = (loss.get("legs") or {}).get(f"t2_cap_r{rep}") or {}
        unl_at, res = unload_at(leg)
        spans = (leg.get("cap_tone") or {}).get("mine_spans") or []
        post = [s for s in spans if unl_at is not None and s[1] > unl_at]
        t2[f"t2_cap_r{rep}"] = {"exit_code": leg.get("exit_code"),
                                "unl_at": unl_at, "unload_res": res,
                                "mine_spans": spans,
                                "post_unlink_spans": post,
                                "gate_would_pass": bool(post),
                                "out_riff":
                                (leg.get("out") or {}).get("riff"),
                                "pump_relinked_to":
                                leg.get("pump_relinked_to")}
    out["t2"] = t2
    # t1 taps post-unlink witness + unloads table
    t1 = {}
    for rep in range(3):
        leg = (loss.get("legs") or {}).get(f"t1_play_r{rep}") or {}
        unl_at, res = unload_at(leg)
        tap = ((leg.get("taps") or {}).get("tap_def") or {}).get("tone") or {}
        spans = tap.get("mine_spans") or []
        t1[f"t1_play_r{rep}"] = {"exit_code": leg.get("exit_code"),
                                 "unl_at": unl_at, "unload_res": res,
                                 "tap_mine_spans": spans}
    out["t1"] = t1
    out["unloads"] = loss.get("unloads")
    out["sinks_gone"] = loss.get("sinks_gone")
    out["own_nodes_after"] = loss.get("own_nodes_after")
    # all entries' teardown
    out["teardown_all"] = {n: {"sinks_gone": (m.get(n) or {}).get(
                               "sinks_gone"),
                               "own_nodes_after": (m.get(n) or {}).get(
                               "own_nodes_after")}
                           for n in EXPECTED_LEGS}
    # entries with non-empty failures across ALL measurements
    out["failed_entries"] = {n: e.get("failures")
                             for n, e in m.items()
                             if isinstance(e, dict) and e.get("failures")}
    # every leg executed (has exit_code) — census
    missing_exec = []
    for name in EXPECTED_LEGS:
        for ln, leg in ((m.get(name) or {}).get("legs") or {}).items():
            if "exit_code" not in leg and "rc" not in leg and \
                    not leg.get("spawn_error"):
                missing_exec.append(f"{name}.{ln}")
    out["legs_missing_exec"] = missing_exec
    # host_is_quiet census (under contention)
    out["host_quiet"] = {n: ((m.get(n) or {}).get("contention") or {}).get(
                         "host_is_quiet") for n in EXPECTED_LEGS}
    return out

if __name__ == "__main__":
    res = {t: analyze(t) for t in sys.argv[1:]}
    print(json.dumps(res, indent=2, default=str))
