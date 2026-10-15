#!/usr/bin/env python3
"""r95-boundary receipt analyzer: compact per-claim extraction for the report.
Usage: r95banalyze.py <cond>   (reads receipts/<cond>_*.json, prints a summary)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "receipts")


def load(cond, stage):
    p = os.path.join(R, f"{cond}_{stage}.json")
    if not os.path.exists(p):
        return None
    return json.load(open(p))


def uniq(xs):
    out = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out


def main(cond):
    out = {}
    d = load(cond, "shape")
    if d:
        rows = []
        for r in d["reps_data"]:
            j = r["json"] or {}
            nodes = {v.get("node.name"): {k: v.get(k) for k in
                                          ("client.api", "node.always-process", "node.group",
                                           "media.category", "media.role", "media.class")}
                     for v in r["graph"]["nodes"].values()}
            ports = {v.get("port.name"): {k: v.get(k) for k in
                                          ("port.alias", "object.path", "port.direction",
                                           "format.dsp", "port.physical", "port.terminal",
                                           "port.extra")}
                     for v in r["graph"]["ports"].values()}
            rows.append({"rep": r["rep"], "client_name": j.get("client_name"),
                         "census": j.get("census"), "monitor": [j.get("request_monitor_rc"),
                                                                j.get("monitoring_input"),
                                                                j.get("ensure_monitor_rc")],
                         "links": r["links_while_running"], "nodes": nodes, "ports": ports,
                         "lat_out": j.get("lat_out"), "rc": r["rc"],
                         "foreign_n": len(r["graph"]["foreign_nodes"]),
                         "load1": r["loadavg"]["load1"]})
        out["shape"] = rows
    d = load(cond, "xconnect")
    if d:
        rows = {}
        for arm, rs in d["arms"].items():
            rows[arm] = [{"rep": r["rep"], "target": r["target"], "rc": r["rc"],
                          "by_name_found": (r["json"] or {}).get("xconnect", {}).get("by_name_found"),
                          "connect_rc": (r["json"] or {}).get("xconnect", {}).get("connect_rc"),
                          "connected": (r["json"] or {}).get("xconnect", {}).get("connected"),
                          "links": r["links_while_running"]} for r in rs]
        out["xconnect"] = rows
    d = load(cond, "liveness")
    if d:
        out["liveness"] = {
            "driver_present": [{"rep": r["rep"], "cb": (r["json"] or {}).get("cb"),
                                "xrun_cbs": (r["json"] or {}).get("xrun_cbs"),
                                "links": r["links_while_running"]} for r in d["driver_present"]],
            "no_driver": [{"rep": r["rep"], "cb": (r["json"] or {}).get("cb"),
                           "xrun_cbs": (r["json"] or {}).get("xrun_cbs"),
                           "foreign_nodes": r["graph_foreign"][:12]} for r in d["no_driver"]],
        }
    d = load(cond, "bytepath")
    if d:
        out["bytepath"] = {
            "jack2pw": [{"rep": r["rep"], "cb": (r["json"] or {}).get("cb"),
                         "xrun_cbs": (r["json"] or {}).get("xrun_cbs"),
                         "wav": r["wav"], "sha": r["wav_sha256"],
                         "rc": r["rc"]} for r in d["jack2pw"]],
            "pw2jack": [{"rep": r["rep"], "cb": (r["jack_json"] or {}).get("cb"),
                         "cb_in_nonzero": (r["jack_json"] or {}).get("cb_in_nonzero"),
                         "in_nonzero": (r["jack_json"] or {}).get("in_nonzero"),
                         "in_peak": (r["jack_json"] or {}).get("in_peak"),
                         "in_rms": (r["jack_json"] or {}).get("in_rms"),
                         "mag2": (r["jack_json"] or {}).get("goertzel_mag2"),
                         "xrun_cbs": (r["jack_json"] or {}).get("xrun_cbs"),
                         "pw_link_rc": r["pw_link_rc"]} for r in d["pw2jack"]],
        }
    d = load(cond, "quantum")
    if d:
        q = {"per_client": [], "env": {}, "pwjack": {}, "cross": []}
        for r in d["per_client"]:
            j = r["json"] or {}
            props = {v.get("node.name"): [v.get("node.force-quantum"), v.get("node.force-rate")]
                     for v in r["graph"]["nodes"].values()}
            q["per_client"].append({"rep": r["rep"],
                                    "keys": {k: j.get(k) for k in
                                             ("bufsize_inactive", "set_inactive_rc",
                                              "bufsize_after_set_inactive", "bufsize_activated",
                                              "bufsize_live", "bufsize_cbs", "set_active_rc",
                                              "bufsize_after_set_active", "bufsize_cbs_after",
                                              "last_bufsize_cb_after")},
                                    "props": props})
        for tag, rs in d["env_arms"].items():
            q["env"][tag] = [{"rep": r["rep"],
                              "keys": {k: (r["json"] or {}).get(k) for k in
                                       ("bufsize_inactive", "bufsize_active", "bufsize_live",
                                        "srate_active", "srate_live")},
                              "props": {v.get("node.name"): [v.get("node.force-quantum"),
                                                             v.get("node.force-rate")]
                                        for v in r["graph"]["nodes"].values()},
                              "clock_rate_after": r["settings_after"].get("0:clock.rate", {}).get("value")}
                             for r in rs]
        for tag, rs in d["pwjack_arms"].items():
            q["pwjack"][tag] = [{"rep": r["rep"], "rc": r["rc"],
                                 "mode": (r["json"] or {}).get("mode"),
                                 "keys": {k: (r["json"] or {}).get(k) for k in
                                          ("bufsize_active", "bufsize_live")},
                                 "props": {v.get("node.name"): [v.get("node.force-quantum"),
                                                                v.get("node.force-rate")]
                                           for v in r["graph"]["nodes"].values()}} for r in rs]
        for r in d["cross"]:
            q["cross"].append({"rep": r["rep"],
                               "A": {k: (r["a_json"] or {}).get(k) for k in
                                     ("bufsize_inactive", "bufsize_after_set_inactive",
                                      "bufsize_activated", "bufsize_live")},
                               "B": {k: (r["b_json"] or {}).get(k) for k in
                                     ("bufsize_inactive", "bufsize_active", "bufsize_live",
                                      "srate_active")}})
        out["quantum"] = q
    d = load(cond, "global")
    if d:
        out["global"] = [{"rep": r["rep"],
                          "during": r["settings_during"].get("0:clock.force-quantum", {}).get("value"),
                          "after_exit": r["settings_after_client_exit"].get("0:clock.force-quantum", {}).get("value"),
                          "restored": r["settings_restored"].get("0:clock.force-quantum", {}).get("value"),
                          "final": r["settings_final"].get("0:clock.force-quantum", {}).get("value"),
                          "A_bufsize": (r["a_json"] or {}).get("bufsize_activated"),
                          "B_bufsize": (r["b_json"] or {}).get("bufsize_active"),
                          "t_during": r["t_during"],
                          "other_keys_moved": sorted(k for k, v in r["settings_during"].items()
                                                     if v.get("value") != r["settings_before"].get(k, {}).get("value"))}
                         for r in d["reps_data"]]
    d = load(cond, "xrun")
    if d:
        out["xrun"] = [{"rep": r["rep"],
                        "control": {k: (r["control"] or {}).get(k) for k in
                                    ("cb", "xrun_cbs", "xrun_delayed_usecs", "max_delayed_usecs")},
                        "stall150x4": {k: (r["stall_150x4"] or {}).get(k) for k in
                                       ("cb", "xrun_cbs", "stall_cycles", "xrun_delayed_usecs", "max_delayed_usecs")},
                        "stall60x2": {k: (r["stall_60x2"] or {}).get(k) for k in
                                      ("cb", "xrun_cbs", "stall_cycles", "xrun_delayed_usecs", "max_delayed_usecs")}}
                       for r in d["reps_data"]]
    d = load(cond, "latency")
    if d:
        out["latency"] = [{"rep": r["rep"], "before": r["json"].get("out_before"),
                           "after_set": r["json"].get("out_after_set"),
                           "active": r["json"].get("out_active"),
                           "recompute_rc": r["json"].get("recompute_rc"),
                           "bufsize": r["json"].get("bufsize")} for r in d["reps_data"]]
    d = load(cond, "rtprio")
    if d:
        out["rtprio"] = {
            "plain": [{"rep": r["rep"], "common": [(r["json"] or {}).get("rt_prio"),
                                                   (r["json"] or {}).get("max_rt_prio")],
                       "samples": (r["json"] or {}).get("samples")} for r in d["rtprio"]],
            "poison": [{"rep": r["rep"], "baseline": (r["json"] or {}).get("baseline"),
                        "poison_aa": (r["json"] or {}).get("poison_aa"),
                        "poison_bb": (r["json"] or {}).get("poison_bb"),
                        "hex": (r["json"] or {}).get("poison_aa_hex")} for r in d["poison"]],
        }
    d = load(cond, "transport")
    if d:
        out["transport"] = [{"rep": r["rep"], "keys": {k: (r["json"] or {}).get(k) for k in
                                                       ("state_before_activate", "state_after_activate",
                                                        "state_after_start", "frame_after_start",
                                                        "state_after_stop", "state_after_locate",
                                                        "frame_after_locate", "locate_rc",
                                                        "reposition_rc", "frame_after_reposition",
                                                        "tconn_rc", "out_connected")}} for r in d["reps_data"]]
    d = load(cond, "metadata")
    if d:
        out["metadata"] = [{"rep": r["rep"],
                            "keys": {k: (r["json"] or {}).get(k) for k in
                                     ("set_client_rc", "get_client_rc", "get_client_value",
                                      "get_missing_rc", "all_desc_count", "own_desc_count",
                                      "remove_client_rc", "get_after_remove_rc",
                                      "get_after_remove_value", "client_uuid_index")},
                            "own_id": r["own_registry_id"], "serial": r["own_object_serial"],
                            "during": r["default_metadata_during"],
                            "after": r["default_metadata_after_exit"]} for r in d["reps_data"]]
    d = load(cond, "nameproj")
    if d:
        out["nameproj"] = {"arms": {arm: [{"rep": r["rep"], "rc": r["rc"],
                                           "status": (r["json"] or {}).get("status"),
                                           "open": (r["json"] or {}).get("mode")} for r in rs]
                                    for arm, rs in d["arms"].items()},
                           "duplicate": [{"rep": r["rep"], "second_rc": r["second_rc"],
                                          "second_status": (r["second_json"] or {}).get("status")}
                                         for r in d["duplicate_name"]]}
    d = load(cond, "flags")
    if d:
        out["flags"] = {tag: [{k: r.get(k) for k in
                               ("rep", "rc", "alive_at_census", "links_while_running",
                                "seat_nodes", "good_rc", "bad_rc", "bad_err", "in_nonzero",
                                "rc1", "rc2", "nodes")} for r in rs]
                        for tag, rs in d["arms"].items()}
    d = load(cond, "defaultnode")
    if d:
        out["defaultnode"] = {tag: [{k: r.get(k) for k in
                                     ("rep", "client", "rc", "alive_at_census",
                                      "my_links_to_host_default", "my_links_to_seat_sink")}
                                    for r in rs] for tag, rs in d["arms"].items()}
        out["defaultnode"]["_defaults"] = [d["defaults_before"], d["defaults_after"]]
    d = load(cond, "bufsize1")
    if d:
        out["bufsize1"] = [{"rep": r["rep"],
                            "props": {v.get("node.name"): v.get("node.force-quantum")
                                      for v in r["graph"]["nodes"].values()},
                            "keys": {k: (r["json"] or {}).get(k) for k in
                                     ("bufsize_inactive", "bufsize_after_set_inactive",
                                      "bufsize_activated", "bufsize_live")}} for r in d["reps_data"]]
    d = load(cond, "sibling")
    if d:
        out["sibling"] = [{"rep": r["rep"], "pre_foreign": r["pre"]["foreign"],
                           "post_foreign": r["post"]["foreign"],
                           "shape_rc": r["rc"],
                           "shape_connect": (r["shape"] or {}).get("xconnect", {}).get("connect_rc")}
                          for r in d["snapshots"]]
    d = load(cond, "verify")
    if d:
        out["verify"] = {"force_quantum": d["settings"].get("0:clock.force-quantum", {}).get("value"),
                         "clock_rate": d["settings"].get("0:clock.rate", {}).get("value"),
                         "defaults": d["defaults"], "modules": d["modules_r95b"],
                         "procs": d["procs_r95b"], "nodes": {k: v.get("node.name")
                                                             for k, v in d["graph"]["nodes"].items()},
                         "stream_properties_rows": d["stream_properties_r95_rows"]}
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "q")
