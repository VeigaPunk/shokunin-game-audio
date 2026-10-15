#!/usr/bin/env python3
"""Probe B — PLAYBACK-side property lattice: precedence + decoration.

r78 pinned on the CAPTURE side: prop `target.object` > `--target` flag, and
`media.role`/`stream.monitor` are decoration.  Does the playback path obey
the same precedence, and does pw-dump's `target.object` on a playback stream
describe intent or consumption?
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H

STATIC = [
    # (label, argv)  -- argv AFTER node.name, played against the tone
    ("flag_ns_prop_ns2", ["-P", f"target.object={H.NS2}", "--target", H.NS]),
    ("flag_ns2_prop_ns", ["-P", f"target.object={H.NS}", "--target", H.NS2]),
    ("prop_only_ns", ["-P", f"target.object={H.NS}"]),
    ("prop_only_ns2", ["-P", f"target.object={H.NS2}"]),
    ("node_target_ns", ["-P", f"node.target={H.NS}"]),
    ("node_target_garbage", ["-P", "node.target=no_such_sink_xyz"]),
    ("prop_garbage_only", ["-P", "target.object=no_such_sink_xyz"]),
    ("flag_garbage_prop_ns", ["--target", "no_such_sink_xyz", "-P",
                              f"target.object={H.NS}"]),
    ("flag_garbage_prop_ns2", ["--target", "no_such_sink_xyz", "-P",
                               f"target.object={H.NS2}"]),
    ("capture_sink_prop", ["-P", "stream.capture.sink=true", "--target", H.NS]),
    ("capture_sink_prop_garbage", ["-P", "stream.capture.sink=true",
                                   "--target", "no_such_sink_xyz"]),
    ("playback_sink_prop", ["-P", "stream.playback.sink=true", "--target",
                            H.NS]),
    ("stream_monitor_prop", ["-P", "stream.monitor=true", "--target", H.NS]),
    ("autoconnect_false", ["-P", "node.autoconnect=false", "--target", H.NS]),
    ("media_class_source", ["-P", "media.class=Audio/Source", "--target",
                            H.NS]),
    ("media_class_sink", ["-P", "media.class=Audio/Sink", "--target", H.NS]),
    ("media_role_comm", ["-P", "media.role=Communication", "--target", H.NS]),
    ("media_role_prod", ["-P", "media.role=Production", "--target", H.NS]),
    ("prop_monitor_name", ["-P", f"target.object={H.NS}.monitor"]),
    ("prop_source_name", ["-P", f"target.object={H.LINE}"]),
]


def main():
    out = {"probe": "playback-props-lattice-r78p", "legs": [],
           "toolchain": H.toolchain()}
    m1, _, _ = H.load_null(H.NS)
    m2, _, _ = H.load_null(H.NS2)
    out["null_sinks"] = {"ns": m1, "ns2": m2}
    time.sleep(0.5)
    H.make_tone(dur=1.6)

    nodes = H.pw_nodes()
    ns_id = nodes.get(H.NS, {}).get("_id")
    out["ns_id"] = ns_id
    legs = list(STATIC)
    if ns_id:
        legs.append(("serial_ns", ["--target", str(ns_id)]))
    legs.append(("serial_bogus", ["--target", "999999"]))
    legs.append(("serial_zero_serial", ["--target", "0"]))

    for label, args in legs:
        tag = "r78pB_" + label
        argv = ["pw-play", "-P", f"node.name={tag}", *args, H.TONE]
        mon = H.Monitors(tag="r78pmonB_" + label)
        leg = H.one_leg(mon, argv, tag, probe_at=0.85, timeout=9.0)
        leg["label"], leg["requested"] = label, args
        out["legs"].append(leg)
        print(f"{label:26s} rc={leg['rc']} wall={leg['wall_s']:5.2f} "
              f"carried={leg['carried']} "
              f"links={sorted({p for v in leg['mid'].get('links', {}).values() for p in v})} "
              f"tgt={leg['mid'].get('props', {}).get('target.object')} "
              f"err={leg['stderr'][:50]!r}")

    # second prop vector: PIPEWIRE_PROPS in the environment
    for label, envprops, args in [
            ("env_ns2_flag_ns", "{ target.object=r78p_ns2 }",
             ["--target", H.NS]),
            ("env_ns_flag_none", "{ target.object=r78p_ns }", []),
            ("env_garbage", "{ target.object=no_such_sink_xyz }", [])]:
        tag = "r78pB_" + label
        argv = ["pw-play", "-P", f"node.name={tag}", *args, H.TONE]
        mon = H.Monitors(tag="r78pmonB_" + label)
        leg = H.one_leg(mon, argv, tag, probe_at=0.85, timeout=9.0,
                        env={"PIPEWIRE_PROPS": envprops})
        leg["label"], leg["requested"] = label, args
        leg["env"] = envprops
        out["legs"].append(leg)
        print(f"{label:26s} rc={leg['rc']} wall={leg['wall_s']:5.2f} "
              f"carried={leg['carried']} "
              f"links={sorted({p for v in leg['mid'].get('links', {}).values() for p in v})}")

    H.unload(m1)
    H.unload(m2)
    keep = {"flag_ns_prop_ns2", "prop_only_ns", "autoconnect_false",
            "media_class_source", "capture_sink_prop"}
    for f in os.listdir(H.RAW):
        if f.startswith("r78pmonB_"):
            lab = f[len("r78pmonB_"):].rsplit("_", 1)[0]
            if lab not in keep:
                os.unlink(os.path.join(H.RAW, f))
    H.save("probe-play-props-r78p.json", out)


if __name__ == "__main__":
    main()
