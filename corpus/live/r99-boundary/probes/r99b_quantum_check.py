#!/usr/bin/env python3
"""r99-boundary AX-QUANTUM support: prove the graph quantum really changed.

The ts-delta lattice measured by cell axis_quantum is identical at quantum 256
and 4096; this probe records the *effective* quantum (pw-metadata settings)
so the invariance is not an artefact of a no-op override.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r99b_common import (core_up, core_down, write_fragment, sh, receipt, loadavg, read_json)
from r99b_driver import sink_args, P, live_tap, play, finish, tone_props


def main():
    out = []
    for q in (256, 1024, 4096):
        write_fragment([("libpipewire-module-rtp-sink", sink_args(dest_port=P + 40))], quantum=q)
        ok, msg = core_up(with_wp=True)
        rec = {"requested_quantum": q, "core_up": ok, "msg": msg}
        if ok:
            rc, o, e = sh(["pw-metadata", "-n", "settings"], timeout=25)
            rec["metadata"] = [l.strip() for l in o.splitlines()
                               if "clock.quantum" in l or "clock.rate" in l or "max-quantum" in l]
            port = P + 40
            tap = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "raw", "quantum-%d.tap.json" % q)
            os.makedirs(os.path.dirname(tap), exist_ok=True)
            p = live_tap(tap, port, 2.5)
            time.sleep(0.4)
            p_play = play("r99b_sink", node_name="r99b_play_q")
            time.sleep(2.2)
            finish(p_play, 3)
            finish(p, 8)
            rec["recv"] = read_json(tap)
            rec["loadavg"] = loadavg()
        out.append(rec)
        core_down()
    receipt("axis-quantum-metadata.json", out)
    for r in out:
        print(json.dumps({k: r.get(k) for k in ("requested_quantum", "metadata")}))


if __name__ == "__main__":
    main()
