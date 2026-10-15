#!/usr/bin/env python3
"""r78b p2 — fallback under a DELETED default sink + forged default metadata."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *

out = {"probe": "p2-stale-default", "ts": time.time(),
       "env": foreign_note()}
out["cleanup"] = unload_all_mine()
make_tone(TONE, dur=1.8)
m1, _, _ = load_null(NS, "r78b probe A")
time.sleep(0.5)

ORIG = SPDIF_META_JSON
def meta(): return metadata_default()[0].get("default.audio.sink")
def restore(tag):
    r = set_default_sink_meta(ORIG)
    time.sleep(0.4)
    out.setdefault("restores", []).append(
        {"tag": tag, "rc": r[0], "err": r[2].strip()[:120],
         "after": get_default_sink()[:2], "meta": meta()})

def leg(name, args, timeout=9.0, monitors=None, aplay=False):
    tag = f"r78bC_{name}"
    if aplay:
        argv = ["aplay", "-D", args[0], "-q", TONE]
        return play_leg(argv, tag, timeout=timeout, monitors=monitors)
    argv = ["pw-play", "-P", f"node.name={tag}", *args, TONE]
    return play_leg(argv, tag, timeout=timeout, monitors=monitors)

try:
    # ---- Phase 0: positive control — switch to a REAL owned sink ---------
    out["meta_before"] = meta()
    r = set_default_sink_meta('{"name":"%s"}' % NS); time.sleep(0.5)
    out["control_set_ns"] = {"rc": r[0], "err": r[2].strip()[:120],
                             "get": get_default_sink()[:2], "meta": meta()}
    out["leg_ctrl_garbage"] = leg("ctrl_garbage",
                                ["--target", "no_such_sink_r78b"])
    restore("after-control")

    # ---- Phase A: delete the default sink, leave metadata stale -----------
    md, rc_, e_ = load_null("r78b_def", "r78b def")
    time.sleep(0.4)
    set_default_sink_meta('{"name":"r78b_def"}'); time.sleep(0.5)
    out["A_set_def"] = {"get": get_default_sink()[:2], "meta": meta()}
    unload(md); time.sleep(0.7)
    out["A_after_delete"] = {"get": get_default_sink()[:2],
                             "meta": meta(),
                             "def_nodes": pw_objects_by_name("r78b_def"),
                             "ns_state": node_state(NS)}
    out["A_leg_garbage"] = leg("deld_garbage",
                             ["--target", "no_such_sink_r78b"])
    out["A_leg_notarget"] = leg("deld_notarget", [])
    out["A_leg_deleted_name"] = leg("deld_name", ["--target", "r78b_def"])
    out["A_leg_honored"] = leg("deld_honored", ["--target", NS])
    restore("after-A")

    # ---- Phase B: forged default.audio.sink values ------------------------
    forged = [
        ("nonexistent", '{"name":"no_such_sink_r78b"}'),
        ("empty_name", '{"name":""}'),
        ("not_json", 'this is not json'),
        ("source_name", '{"name":"%s"}' % LINE),
        ("numeric_name", '{"name":123}'),
        ("extra_field", '{"name":"%s","bogus":1}' % NS),
    ]
    out["B"] = {}
    for label, js in forged:
        r = set_default_sink_meta(js); time.sleep(0.5)
        rec = {"set_rc": r[0], "set_err": r[2].strip()[:120],
               "get": get_default_sink()[:2], "meta": meta()}
        rec["leg"] = leg(f"B_{label}", ["--target", "no_such_sink_r78b"],
                         timeout=9.0)
        if label == "nonexistent":
            rec["leg_honored"] = leg("B_honored", ["--target", NS])
            rec["leg_aplay_default"] = leg("B_aplaydef", ["default"],
                                         aplay=True)
        out["B"][label] = rec
        restore(f"B-{label}")

    # ---- Phase C: garbage VALUE TYPE (unquoted name, array) ---------------
    for label, js in [("unquoted", '{"name":%s}' % NS),
                      ("array", '["%s"]' % NS),
                      ("bareword", NS)]:
        r = set_default_sink_meta(js); time.sleep(0.5)
        out["B"][label] = {"set_rc": r[0], "set_err": r[2].strip()[:120],
                           "get": get_default_sink()[:2], "meta": meta(),
                           "leg": leg(f"C_{label}",
                                      ["--target", "no_such_sink_r78b"],
                                      timeout=9.0)}
        restore(f"C-{label}")
finally:
    restore("FINAL")
    out["post_cleanup"] = unload_all_mine()
    out["post_default"] = get_default_sink()
    out["post_meta"] = meta()

save("probe-p2-stale-default-r78b.json", out)

def s(l):
    return (f"rc={l.get('rc')} wall={l.get('wall_s')} "
            f"carried={l.get('carried')} err={str(l.get('stderr'))[:50]!r}")
print("control:", s(out["leg_ctrl_garbage"]))
print("A get-after-delete:", out["A_after_delete"]["get"])
for k in ("A_leg_garbage", "A_leg_notarget", "A_leg_deleted_name",
          "A_leg_honored"):
    print(k, s(out[k]))
for k, v in out["B"].items():
    print(f"B[{k}] get={v.get('get')} leg:", s(v.get("leg", {})))
    if "leg_honored" in v: print("   honored:", s(v["leg_honored"]))
    if "leg_aplay_default" in v: print("   aplay:", s(v["leg_aplay_default"]))
print("final default:", out["post_default"], "| meta:", out["post_meta"])
