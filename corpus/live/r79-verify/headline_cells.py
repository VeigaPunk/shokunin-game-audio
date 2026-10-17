#!/usr/bin/env python3
"""r79-verifier: extract the author's headline cells from any r79 receipt
so the report's verdict table is built from the receipts, not the prose."""
import json
import sys


def cells(p):
    d = json.load(open(p))["measurements"]
    o = {}
    s = d["loopback_shape_r79_probe"]
    a1 = s["legs"]["a1_shape"]
    last = a1["samples"][-1]
    inode = (last["nodes"].get(f"input.{a1['ltag']}") or {})
    onode = (last["nodes"].get(f"output.{a1['ltag']}") or {})
    iw = (last["watch"].get(f"input.{a1['ltag']}") or {})
    ow = (last["watch"].get(f"output.{a1['ltag']}") or {})
    o["shape.a1.media"] = (inode.get("media_class"), onode.get("media_class"))
    o["shape.a1.ports_in"] = (iw.get("input_ports"), iw.get("output_ports"))
    o["shape.a1.ports_out"] = (ow.get("input_ports"), ow.get("output_ports"))
    o["shape.a1.client_id_same"] = inode.get("client_id") == onode.get("client_id")
    o["shape.a1.link_group_same"] = (
        inode.get("node_link_group") == onode.get("node_link_group"))
    o["shape.a1.target_object"] = (inode.get("target_object"),
                                   onode.get("target_object"))
    o["shape.a1.unions"] = (a1.get("input_producers_union"),
                            a1.get("output_consumers_union"))
    o["shape.a1.tap"] = (a1["tap"].get("bound_to_target"),
                         a1["tap"].get("ran"), a1["tap"].get("carries_tone"),
                         a1["tap"].get("mine_windows"))
    o["shape.a1.killed"] = a1.get("killed_at_bound")
    for sid in ("a2_space", "a2_comma"):
        leg = s["legs"][sid]
        n = (leg["samples"][-1]["nodes"] or {})
        il = n.get(f"input.{leg['ltag']}") or {}
        ol = n.get(f"output.{leg['ltag']}") or {}
        o[f"shape.{sid}.props"] = (il.get("stream_capture_sink"),
                                   il.get("media_role"),
                                   il.get("target_object"),
                                   ol.get("media_role"),
                                   ol.get("stream_capture_sink"))
    a5 = s["legs"]["a5_capture_default"]
    o["shape.a5.producers"] = a5.get("producers_union")
    o["shape.a5.outcome"] = a5.get("outcome")
    a6 = s["legs"]["a6_playback_default"]
    o["shape.a6.consumers"] = a6.get("consumers_union")

    cap = d["loopback_capture_lattice_r79_probe"]
    for ln, leg in cap["legs"].items():
        if not isinstance(leg, dict):
            o[f"capture.{ln}"] = leg
            continue
        o[f"capture.{ln}"] = (leg.get("producers_union"), leg.get("outcome"),
                              leg.get("target_object_lies"),
                              leg.get("target_requested"),
                              leg.get("target_object_advertised"))
    play = d["loopback_playback_lattice_r79_probe"]
    for ln, leg in play["legs"].items():
        o[f"playback.{ln}"] = leg.get("consumers_union")
    c07 = play["legs"]["c07_prop_beats_flag"]
    o["playback.c07.ctrltap"] = (c07.get("tap_flag_sink", {}).get("ran"),
                                 c07.get("tap_flag_sink", {}).get("bound_to_target"),
                                 c07.get("tap_flag_sink", {}).get("mine_windows"))
    mx = d["loopback_matrix_r79_probe"]
    for ln, leg in mx["legs"].items():
        tt = leg.get("two_tone") or {}
        o[f"matrix.{ln}"] = (tt.get("mix_signature"), tt.get("stereo_signature"),
                             tt.get("channels"), leg.get("mix_half_gain_ratio"),
                             leg.get("expected"))
    rc = d["loopback_record_target_r79_probe"]
    lb = rc["legs"]["loopback"]
    o["record.lb.unions"] = (_loopback_union(lb["samples"], f"input.{lb['ltag']}", "producers"),
                             _loopback_union(lb["samples"], f"output.{lb['ltag']}", "consumers"))
    for ln in ("d2a_input_node", "d2b_output_node", "d2c_input_capsink",
               "d2d_output_capsink", "d17_manual_pin"):
        leg = rc["legs"][ln]
        o[f"record.{ln}"] = (leg.get("expected_producers"),
                             sorted({n for smp in leg["samples"]
                                     for k, v in (smp.get("watch") or {}).items()
                                     for n in (v.get("producers") or [])}),
                             (leg.get("content") or {}).get("mine_windows"),
                             (leg.get("content") or {}).get("carries_tone"))
    hp = d["loopback_hotplug_r79_probe"]
    for ln in ("e1_unload_playback", "e2_load_playback", "e3_unload_capture"):
        leg = hp["legs"][ln]
        o[f"hotplug.{ln}"] = (leg.get("output_consumers_union") if ln != "e3_unload_capture"
                              else leg.get("input_producers_union"),
                              leg.get("killed_at_bound"))
    pc = d["pwcat_latency_r79_probe"]
    for ln, leg in pc["legs"].items():
        o[f"pwcat.{ln}"] = leg.get("node_latency")
    o["pwcat.verdict"] = pc.get("latency_param_verdict")
    o["pwcat.param_set"] = pc.get("latency_param_set")
    fc = d["filterchain_module_r79_probe"]
    for ln, leg in fc["legs"].items():
        o[f"fc.{ln}"] = (leg.get("expect_met"), leg.get("loader_rc"),
                         leg.get("chain_nodes") if "chain_nodes" in leg else
                         (leg.get("two_tone") or {}).get("channels"))
    return o


def _loopback_union(samples, node, key):
    return sorted({n for s in samples
                   for n in ((s.get("watch") or {}).get(node) or {}).get(key) or []})


if __name__ == "__main__":
    tables = {p.split("/")[-2][:15]: cells(p) for p in sys.argv[1:]}
    keys = sorted(set().union(*[set(t) for t in tables.values()]))
    for k in keys:
        vals = [json.dumps(tables[t].get(k), sort_keys=True) for t in tables]
        mark = "  " if len(set(vals)) == 1 else "!!"
        print(f"{mark} {k}")
        for t, v in zip(tables, vals):
            print(f"      {t}: {v}")
