#!/usr/bin/env python3
"""r97-scout: compact roll-up (summary.json) + manifest.sha256."""
import hashlib, json, os, sys

SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(SEAT, "receipts")
SKIP_DIRS = {"__pycache__", "run"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    # --- summary.json: the compact extraction of every receipt
    c = json.load(open(os.path.join(REC, "c_default_nodes.json")))
    c2 = json.load(open(os.path.join(REC, "c2_default_controls.json")))
    c3 = json.load(open(os.path.join(REC, "c3_restart.json")))
    b = json.load(open(os.path.join(REC, "b_wpexec.json")))
    a = json.load(open(os.path.join(REC, "a_arming.json")))
    d = json.load(open(os.path.join(REC, "d_linking.json")))
    e = json.load(open(os.path.join(REC, "e_residuals.json")))
    f = json.load(open(os.path.join(REC, "f_target_property.json")))
    S = {"stage": "r97-scout", "host": os.uname().nodename}

    def step_val(rep, tag, key):
        for s in rep["steps"]:
            if s["tag"] == tag:
                return s.get(key)
        return None

    S["c_default_nodes"] = {
        "reps": len(c["reps"]),
        "first_sink_becomes_default": [step_val(r, f"A_first_sink_becomes_default", "default") for r in c["reps"]],
        "higher_session_priority_takes_over": [step_val(r, f"B_higher_session_priority_takes_default", "default") for r in c["reps"]],
        "lower_priority_does_not": [step_val(r, "C_lower_session_priority_does_not_take_default", "default") for r in c["reps"]],
        "explicit_wins_over_highest": [step_val(r, "D_highest_priority_does_not_override_explicit", "default") for r in c["reps"]],
        "clear_default_picks_best": [step_val(r, "after_clear_default_best_wins", "default") for r in c["reps"]],
        "removed_default_falls_back": [step_val(r, "removed_default_falls_back_to_best_remaining", "default") for r in c["reps"]],
        "equal_session_incumbent_keeps": [step_val(r, "driver_priority_only_e_vs_f", "default") for r in c["reps"]],
    }
    S["c2_controls"] = {
        "reps": len(c2["reps"]),
        "driver_high_first_incumbent_keeps": [step_val(r, "driver_control_high_first", "default") for r in c2["reps"]],
        "no_priority_session_key_loses": [step_val(r, "no_priority_session_key", "default") for r in c2["reps"]],
        "configured_row_written": [step_val(r, "set_default_row", "configured") for r in c2["reps"]],
        "configured_row_survives_no_sinks": [step_val(r, "configured_row_without_sinks", "configured") for r in c2["reps"]],
        "state_file": [r.get("state_after_set") for r in c2["reps"]],
    }
    S["c3_restart"] = {
        "reps": len(c3["reps"]),
        "before_restart_default": [step_val(r, "before_restart", "default") for r in c3["reps"]],
        "after_restart_default": [step_val(r, "after_restart", "default") for r in c3["reps"]],
        "state_after_restart": [r.get("state_after_restart") for r in c3["reps"]],
    }
    S["b_wpexec"] = {
        "reps": len(b["reps"]),
        "found": sorted(set(l[6:] for r in b["reps"] for l in r["legs"]["inventory"]["stdout"].splitlines() if l.startswith("FOUND "))),
        "missing": sorted(set(l[8:] for r in b["reps"] for l in r["legs"]["inventory"]["stdout"].splitlines() if l.startswith("MISSING "))),
        "env_line": sorted(set(l for r in b["reps"] for l in r["legs"]["inventory"]["stdout"].splitlines() if l.startswith("ENV="))),
        "runtime_error": sorted(set((r["legs"]["err_runtime_error_msg"]["rc"], r["legs"]["err_runtime_error_msg"]["stderr"].strip()) for r in b["reps"])),
        "syntax_error": sorted(set((r["legs"]["err_syntax"]["rc"], r["legs"]["err_syntax"]["stderr"].strip()) for r in b["reps"])),
        "no_quit": sorted(set((r["legs"]["err_no_quit"]["rc"], r["legs"]["err_no_quit"]["timed_out"]) for r in b["reps"])),
        "settings_inert": sorted(set((r["legs"]["settings_inert"]["before"]["stdout"].strip(),
                                      r["legs"]["settings_inert"]["after_false"]["stdout"].strip()) for r in b["reps"]))[:1],
        "settings_wpctl_worked": sorted(set(r["legs"]["settings_inert"]["set_false"]["stdout"].strip() for r in b["reps"])),
        "no_arg": sorted(set((r["legs"]["no_arg"]["rc"], r["legs"]["no_arg"]["stderr"].strip()) for r in b["reps"])),
    }
    S["a_arming"] = {"reps": len(a["reps"])}
    VARIANTS = ("V1_CONFIGDIR_without_conf", "V2_CONFIGDIR_with_conf_copy",
                "V3_private_XDG_CONFIG_HOME", "V4_default_user_config",
                "V5_DATA_DIR_additive")
    _av = {}
    for v in VARIANTS:
        rows = set()
        for r in a["reps"]:
            for L in r["legs"]:
                if L["variant"] != v:
                    continue
                frags = tuple(sorted(os.path.basename(x) for x in
                                     [l.split("opening fragment file: ")[-1]
                                      for l in L["lines"] if "opening fragment" in l]))
                rows.add((L["rc"], L["timed_out"], frags))
        _av[v] = [list(x) for x in sorted(rows)]
    S["a_arming"]["variants"] = _av
    S["d_linking"] = {"reps": len(d["reps"]),
                      "cells": {}}
    for tag in ("target_0_no_link", "auto_default", "target_global_id_A",
                "target_object_serial_A", "target_name_A", "bogus_target_99999",
                "bogus_target_dont_fallback", "media_role_Communication"):
        vals = []
        for r in d["reps"]:
            for o in r["obs"]:
                if o.get("tag") == tag:
                    links = o.get("links")
                    vals.append(sorted({l[1] for l in links}) if links else links)
        S["d_linking"]["cells"][tag] = vals
    for tag in ("follow_default_true", "follow_default_false"):
        vals = []
        for r in d["reps"]:
            for o in r["obs"]:
                if o.get("tag") == tag:
                    vals.append({"before": sorted({l[1] for l in (o["before"] or [])}),
                                 "after": sorted({l[1] for l in (o["after"] or [])})})
        S["d_linking"]["cells"][tag] = vals
    S["e_residuals"] = {
        "reps": len(e["reps"]),
        "driver_fallback_verdicts": [r["e1_driver_fallback"]["verdict"] for r in e["reps"]],
        "follow_false_setting_value": [r["e2_follow_false"]["setting_after"].strip() for r in e["reps"]],
        "follow_false_moved": [r["e2_follow_false"]["moved"] for r in e["reps"]],
    }
    S["f_target_property"] = {
        "reps": len(f["reps"]),
        "target_property_written": sorted({tuple(sorted(
            (r[k]["stream_props"] or {}).items())) for r in f["reps"]
            for k in ("by_serial", "by_global_id")}),
    }
    json.dump(S, open(os.path.join(SEAT, "receipts", "summary.json"), "w"), indent=1,
              default=lambda o: sorted(o) if isinstance(o, (set, frozenset)) else list(o))

    # --- manifest.sha256 over everything in the seat dir (excluding run/ and pycache)
    lines = []
    for root, dirs, files in os.walk(SEAT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            p = os.path.join(root, f)
            if f.endswith(".pyc") or f == "manifest.sha256":
                continue
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            st = os.stat(p)
            if not os.path.isfile(p):   # FIFOs / sockets block the hash
                continue
            if st.st_mode & 0o170000 not in (0o100000,):  # regular files only
                continue
            lines.append(f"{sha(p)}  {os.path.relpath(p, SEAT)}")
    lines.sort(key=lambda l: l.split("  ", 1)[1])
    with open(os.path.join(SEAT, "manifest.sha256"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"summary.json + manifest.sha256 written ({len(lines)} files)")


if __name__ == "__main__":
    main()
