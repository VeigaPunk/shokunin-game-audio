#!/usr/bin/env python3
"""r86-critic census: leg census, teardown witnesses, caveat-arm states,
and leg-name diff across the two green runs. Read-only w.r.t. the repo
tracked tree; writes only under corpus/live/r86-critic/."""
import json
import sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
RUNS = {
    "dev": ROOT / "corpus/live/runs/20261016T062922907396Z-pwctl-r86/measurements.json",
    "run1": ROOT / "corpus/live/runs/20261016T063006268243Z-pwctl-r86/measurements.json",
    "run2": ROOT / "corpus/live/runs/20261016T063043717745Z-pwctl-r86/measurements.json",
}
R86 = ["pwctl_addr_r86_probe", "pwctl_params_r86_probe", "pwctl_dsp_r86_probe",
       "pwctl_meta_r86_probe", "pwctl_tools_r86_probe"]

out = {}
for tag, p in RUNS.items():
    r = json.loads(p.read_text())
    m = r["measurements"]
    rec = {"mode": r.get("mode"), "n_entries": len(m), "r86": {}}
    for e in R86:
        v = m.get(e)
        if v is None:
            rec["r86"][e] = "MISSING"
            continue
        legs = v.get("legs") or {}
        rec["r86"][e] = {
            "legs": len(legs),
            "leg_names": sorted(legs),
            "failures": v.get("failures"),
            "coverage_blocked": v.get("coverage_blocked"),
            "blocked": v.get("blocked"),
            "sinks_gone": v.get("sinks_gone"),
            "own_nodes_after": v.get("own_nodes_after"),
            "meta_keys_gone": v.get("meta_keys_gone"),
            "unloads": {k: {kk: vv for kk, vv in (val or {}).items()
                            if kk in ("module_id", "rc", "verified_index",
                                      "captured", "recycled", "field",
                                      "value", "verified_line")}
                        for k, val in (v.get("unloads") or {}).items()},
            "foreign_r86a_nodes": v.get("foreign_r86a_nodes"),
            "loadavg": v.get("loadavg"),
            "probe": v.get("probe"),
        }
    # full-receipt failure map
    rec["failures_by_entry"] = {k: vv.get("failures")
                                for k, vv in m.items()
                                if vv.get("failures")}
    rec["coverage_blocked_by_entry"] = {k: vv.get("coverage_blocked")
                                        for k, vv in m.items()
                                        if vv.get("coverage_blocked")}
    rec["top_level_keys"] = sorted(r.keys())
    out[tag] = rec

# leg-name diff run1 vs run2 (per entry)
diff = {}
for e in R86:
    a = set(out["run1"]["r86"][e]["leg_names"])
    b = set(out["run2"]["r86"][e]["leg_names"])
    if a != b:
        diff[e] = {"only_run1": sorted(a - b), "only_run2": sorted(b - a)}
out["_legname_diff_run1_run2"] = diff or "IDENTICAL"

# caveat arms + key values per run
kv = {}
for tag in ("run1", "run2"):
    r = json.loads(RUNS[tag].read_text())["measurements"]
    kv[tag] = {}
    addr = r["pwctl_addr_r86_probe"]["legs"]
    par = r["pwctl_params_r86_probe"]["legs"]
    meta = r["pwctl_meta_r86_probe"]["legs"]
    tools = r["pwctl_tools_r86_probe"]["legs"]
    dsp = r["pwctl_dsp_r86_probe"]["legs"]
    kv[tag]["dump_color_eq"] = {k: addr["dump_color_eq"].get(k) for k in
                                ("exit_code", "signal", "stdout_bytes",
                                 "error_class", "armed")}
    kv[tag]["d_route"] = {k: par["d_route"].get(k) for k in
                          ("exit_code", "stdout_bytes", "has_pod",
                           "error_class", "armed")}
    kv[tag]["n_format"] = {k: par["n_format"].get(k) for k in
                           ("exit_code", "stdout_bytes", "has_pod",
                            "error_class", "armed")}
    kv[tag]["n_enumformat"] = {k: par["n_enumformat"].get(k) for k in
                               ("exit_code", "stdout_bytes", "has_pod")}
    kv[tag]["p_format"] = {k: par["p_format"].get(k) for k in
                           ("exit_code", "stdout_bytes", "has_pod")}
    kv[tag]["dump_full1"] = addr["dump_full1"]
    kv[tag]["dump_full2"] = addr["dump_full2"]
    kv[tag]["meta_census"] = r["pwctl_meta_r86_probe"].get("meta_census")
    kv[tag]["meta_store_ids"] = addr.get("meta_store_ids")
    kv[tag]["subj0_keys"] = meta.get("subj0_keys")
    kv[tag]["params_subjects"] = r["pwctl_params_r86_probe"].get("subjects")
    kv[tag]["dsp_regions"] = {k: v["median_peak"] for k, v in
                              (dsp.get("regions") or {}).items()}
    kv[tag]["dsp_writes_rc"] = {k: v.get("exit_code") for k, v in
                                (dsp.get("writes") or {}).items()}
    kv[tag]["dsp_player"] = {"attach": dsp.get("player_attach"),
                             "alive_at_end": dsp.get("player_alive_at_end"),
                             "player_exit": dsp.get("player_exit"),
                             "tap_exit": dsp.get("tap_exit"),
                             "tap_windows": dsp.get("tap_windows")}
    kv[tag]["meta_census_present"] = {
        k: (meta.get("meta_census") or {}).get(k) for k in
        ("store_ids", "ls_ids", "dump_ids")} if "meta_census" in meta \
        else "not-a-meta-leg"
    kv[tag]["not_impl_rows_present"] = {nm: (nm in par) for nm in
                                        ("c_props", "f_props", "m_props",
                                         "l_props", "core_setparam")}
    kv[tag]["ls_id_bytes"] = addr["ls_id"].get("stdout_bytes")
    kv[tag]["ls_serial_bytes"] = addr["ls_serial"].get("stdout_bytes")
    kv[tag]["dump_id_bytes"] = addr["dump_id"].get("stdout_bytes")
    kv[tag]["dump_serial_bytes"] = addr["dump_serial"].get("stdout_bytes")
    kv[tag]["dump_id_eq_serial_prefix"] = (
        addr["dump_id"].get("stdout") == addr["dump_serial"].get("stdout"))
    kv[tag]["meta_info_empty_present"] = "meta_info_empty" in addr
    kv[tag]["tools_env"] = {k: tools[k].get("env") for k in
                            ("jack_p", "jack_sp", "jack_s_only", "jack_v",
                             "jack_vv", "jack_v_preset", "jack_r")
                            if k in tools}
    kv[tag]["top_tui_term"] = {k: tools["top_tui_term"].get(k) for k in
                               ("exit_code", "signal", "loop_assert",
                                "killed_at_bound", "signal_delivered")}
    kv[tag]["cli_devnull"] = {k: tools["cli_devnull"].get(k) for k in
                              ("exit_code", "signal", "loop_assert")}
    kv[tag]["cli_pipe"] = {k: tools["cli_pipe"].get(k) for k in
                           ("exit_code", "signal", "killed_at_bound")}
    kv[tag]["lk_dup"] = {k: tools["lk_dup"].get(k) for k in
                         ("exit_code", "error_class")}
out["_keyvalues"] = kv

(ROOT / "corpus/live/r86-critic/census.json").write_text(
    json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
print(json.dumps({"census": "census.json",
                  "failures_by_entry": out["run1"]["failures_by_entry"],
                  "blocked_by_entry": out["run1"]["coverage_blocked_by_entry"],
                  "legname_diff": out["_legname_diff_run1_run2"],
                  "legs_per_entry_run1": {e: out["run1"]["r86"][e]["legs"]
                                          for e in R86}}, indent=2))
