#!/usr/bin/env python3
"""r96-scout summary receipt — consolidates the headline measured facts.

Reads the per-group receipts and emits receipts/r96s_summary.json + runs/summary.txt.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "receipts")


def load(name):
    with open(os.path.join(R, name)) as fh:
        return json.load(fh)["receipts"]


def stable(results, key=lambda r: (r["rc"], r["stderr"])):
    vals = {key(r) for r in results}
    return len(vals) == 1


def main():
    srv = load("r96s_cli_server.json")
    tgt = load("r96s_cli_target.json")
    lat = load("r96s_cli_latency.json")
    props = load("r96s_cli_props.json")
    intro = load("r96s_cli_introspect.json")
    cork = load("r96s_cork_cork.json")
    preb = load("r96s_cork_prebuf.json")
    rec = load("r96s_cork_record.json")
    res = load("r96s_cork_resolve.json")
    census = json.load(open(os.path.join(R, "r96s_census.json")))

    summary = {"seat": "r96s", "surface": "PulseAudio-native client API via pipewire-pulse"}
    summary["toolchain"] = {
        "pactl": "17.0-98-gb096 (libpulse 17.0.0)",
        "pacat/paplay/parec": "17.0-98-gb096",
        "pipewire_pulse": "1:1.6.8-1",
        "server_name": "PulseAudio (on PipeWire 1.6.8)",
        "server_version": "15.0.0",
        "protocol": 35,
        "socket": "/run/user/1000/pulse/native",
        "pacmd": "ABSENT",
        "pa_info": "ABSENT",
        "libpulse_sha256": "cf1020d2e4ee28a0417fdfe5f47241d74567298112f337ac9ef936baff537362",
    }
    summary["server_resolution"] = {
        leg: {
            "rc": body["results"][0]["rc"],
            "stable": stable(body["results"]),
            "wall_s": [r["wall_s"] for r in body["results"]],
            "stderr": body["results"][0]["stderr"].strip(),
            "env": body["results"][0].get("env_extra"),
        }
        for leg, body in srv.items() if "results" in body
    }
    summary["targeting"] = {}
    for leg, body in tgt.items():
        if "results" not in body:
            continue
        rows = [s for r in body["results"] for s in r["my_streams"]]
        summary["targeting"][leg] = {
            "env": body["results"][0].get("env_extra"),
            "argv": body["results"][0]["argv"],
            "rcs": [r["rc"] for r in body["results"]],
            "landings": [{"sink": x["sink"], "sink_name": x["sink_name"], "source": x["source"],
                          "source_name": x["source_name"], "target_object": x["props"].get("target.object")} for x in rows],
            "stderr": body["results"][0]["stderr"].strip()[:120],
        }
    summary["resolve_device_discriminator"] = {
        tag: {"device": v["device"], "landings": [{"sink": x["sink"], "target_object": x["props"].get("target.object")}
                                                   for r in v["results"] for x in (r["timeline"][len(r["timeline"]) // 2]["rows"] if r["timeline"] else [])]}
        for tag, v in res["g_resolve"].items()
    }
    summary["latency_attr_rows"] = {}
    for leg, body in lat.items():
        if isinstance(body, dict) and "results" in body:
            rows = [s for r in body["results"] for s in r["my_streams"]]
            if rows:
                summary["latency_attr_rows"][leg] = {k: rows[0]["props"].get(k) for k in
                                                     ("pulse.attr.tlength", "pulse.attr.prebuf", "pulse.attr.minreq", "node.latency")}
        elif isinstance(body, dict):
            for m, sub in body.items():
                rows = [s for r in sub["results"] for s in r["my_streams"]]
                if rows:
                    summary["latency_attr_rows"][f"{leg}.{m}"] = {k: rows[0]["props"].get(k) for k in
                                                                  ("pulse.attr.tlength", "pulse.attr.prebuf", "pulse.attr.minreq", "node.latency")}
    summary["props"] = {
        "e_props": [s["props"] for r in props["e_props"]["results"] for s in r["my_streams"]][:1],
        "e_props_malformed": {"rcs": [r["rc"] for r in props["e_props_malformed"]["results"]],
                              "stderr": props["e_props_malformed"]["results"][0]["stderr"].strip()},
        "restore_props_off_rows": {"before": props["e_restore_props_off"]["rows_before"]["r96s_rows"],
                                   "after_leg": props["e_restore_props_off"]["rows_after"]["r96s_rows"],
                                   "after_next_leg": props["e_restore_props_off"]["rows_final"]["r96s_rows"]},
        "client_name": [s["props"].get("application.name") for r in props["e_client_name"]["results"] for s in r["my_streams"]][:1],
    }
    summary["cork_trigger"] = {
        leg: {"rcs": [r["rc"] for r in body["results"]],
              "onset_ms_rel_event": [r["onset_ms_rel_event"] for r in body["results"]],
              "nonzero_frames": [sum(1 for v in __import__("array").array("h", open(r["capture"]["path"], "rb").read()[44:]) if abs(v) > 1000) if r["capture"].get("onset") and r["capture"]["onset"].get("first_tone_frame") is not None else 0 for r in body["results"]]}
        for leg, body in cork.items() if "results" in body
    }
    summary["prebuf"] = {}
    for leg, body in preb.items():
        if "results" not in body:
            continue
        summary["prebuf"][leg] = {
            "attr_prebuf": [next((e["attr_prebuf"] for e in r["events"] if e.get("ev") == "stream_ready"), None) for r in body["results"]],
            "nonzero_frames": [next((r["capture"]["onset"]["first_tone_frame"] is not None and
                                     sum(1 for v in __import__("array").array("h", open(r["capture"]["path"], "rb").read()[44:]) if abs(v) > 1000)) or 0
                                    for _ in [0]) for r in body["results"]],
        }
    summary["record_cork"] = [{"rc": r["rc"],
                               "readable_corked": next((e.get("readable_corked") for e in r["events"] if e["ev"] == "corked_check"), None),
                               "readable_uncorked": next((e.get("readable_uncorked") for e in r["events"] if e["ev"] == "uncorked_check"), None),
                               "peek_bytes": next((e.get("peek_bytes") for e in r["events"] if e["ev"] == "drained"), None)}
                              for r in rec["j_record_cork"]["results"]]
    summary["introspection"] = {
        "latency_fields_zero": {"buffer_latency_usec": [s.get("buffer_latency_usec") for r in intro["f_sinkinput_json"][0] for s in [r]],
                                "source": "pulse-server.c:4143-4144 TAG_USEC 0LL hardcoded"},
        "native_idle_rows": intro["f_native_idle_corked"],
        "subscribe_events": intro["f_subscribe"]["events"].splitlines()[:8],
    }
    summary["exit_census"] = {k: census.get(k) for k in
                              ("sinks_r96s", "sources_r96s", "modules_r96s", "pw_dump_r96s", "seat_procs_after",
                               "default_sink", "default_source", "settings_metadata_keys",
                               "stream_properties_total_rows")}
    summary["stream_properties_r96s_rows"] = census.get("stream_properties_r96s_rows")
    path = os.path.join(R, "r96s_summary.json")
    with open(path, "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    print("wrote", path)
    print(json.dumps({k: summary[k] for k in ("server_resolution",)}, indent=1)[:1200])


if __name__ == "__main__":
    main()
