#!/usr/bin/env python3
"""r97-scout stage E — two residual cells:
  E1 priority.driver fallback (node-utils.get_session_priority: session, else driver)
  E2 linking.follow-default-target=false as a behavioural settings witness
"""
import json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97lib import (SEAT, ENV, PwCli, run, dump, nullsink, sink_by_name,
                    default_sink_value, ensure_up)
from d_linking import Stream, stream_links

REC = os.path.join(SEAT, "receipts")
SCR = os.path.join(SEAT, "scratch")


def wait_node(name, cap=6.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < cap:
        i = sink_by_name(dump(), name)
        if i is not None:
            return i
        time.sleep(0.2)
    return None


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    ensure_up()
    out = {"stage": "e_residuals", "reps": []}
    for n in range(reps):
        cli = PwCli(logpath=os.path.join(SCR, f"pwcli_e{n}.log"))
        obs = {"rep": n}
        try:
            # --- E1: priority.driver is the fallback when priority.session is absent
            run(["wpctl", "clear-default"], timeout=6.0)
            nullsink(cli, f"r97s_y{n}", 100, 100)          # incumbent, session=100
            idy = wait_node(f"r97s_y{n}")
            time.sleep(1.0)
            # challenger: NO priority.session, priority.driver=999
            props = (f"{{ factory.name=support.null-audio-sink node.name=r97s_x{n} "
                     f"node.description=r97s_x{n} media.class=Audio/Sink priority.driver=999 }}")
            cli.cmd("create-node adapter " + props)
            idx = wait_node(f"r97s_x{n}")
            time.sleep(1.5)
            _, d = default_sink_value(dump())
            obs["e1_driver_fallback"] = {"incumbent_y": idy, "challenger_x": idx,
                                        "default": d,
                                        "verdict": "x_took_default" if (d or {}).get("name") == f"r97s_x{n}" else "y_kept_default"}
            for i in (idx, idy):
                if i:
                    cli.cmd(f"destroy {i}")
            time.sleep(0.8)
            run(["wpctl", "clear-default"], timeout=6.0)

            # --- E2: follow-default-target=false
            nullsink(cli, f"r97s_sa{n}", 100, 100)
            ida = wait_node(f"r97s_sa{n}")
            nullsink(cli, f"r97s_sb{n}", 500, 100)
            idb = wait_node(f"r97s_sb{n}")
            time.sleep(1.2)
            _, d = default_sink_value(dump())
            setres = run(["wpctl", "settings", "linking.follow-default-target", "false"], timeout=8.0)
            show = run(["wpctl", "settings", "linking.follow-default-target"], timeout=8.0)
            time.sleep(0.8)
            st = Stream(props="{ node.name = r97s_str }")
            time.sleep(1.6)
            before = stream_links(dump(), "r97s_str")
            mv = run(["wpctl", "set-default", str(ida)], timeout=6.0)
            time.sleep(2.2)
            after = stream_links(dump(), "r97s_str")
            st.stop()
            show2 = run(["wpctl", "settings", "linking.follow-default-target"], timeout=8.0)
            obs["e2_follow_false"] = {
                "setup_default": d, "set_setting": setres["stdout"].strip(),
                "setting_before": show["stdout"].strip(),
                "setting_after": show2["stdout"].strip(),
                "before_links": before, "after_links": after,
                "moved": bool(before) and bool(after) and
                         {l[1] for l in before} != {l[1] for l in after}}
            run(["wpctl", "settings", "linking.follow-default-target", "true"], timeout=8.0)
            run(["wpctl", "clear-default"], timeout=6.0)
        finally:
            cli.close()
            time.sleep(0.5)
        out["reps"].append(obs)
    os.makedirs(REC, exist_ok=True)
    json.dump(out, open(os.path.join(REC, "e_residuals.json"), "w"), indent=1)
    for r in out["reps"]:
        print(f"--- rep {r['rep']}")
        print("   E1", r["e1_driver_fallback"])
        e2 = r["e2_follow_false"]
        print(f"   E2 setting={e2['setting_after'].strip()[:40]!r} moved={e2['moved']} "
              f"before={e2['before_links']} after={e2['after_links']}")


if __name__ == "__main__":
    main()
