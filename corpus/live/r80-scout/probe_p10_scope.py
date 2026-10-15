#!/usr/bin/env python3
"""P10 — client scope of natively created nodes: does a pw-cli-created node
survive the pw-cli process, and does object.linger change that?
Also: the same question for a pactl module (server-owned).  REPS reps."""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r80_probe import Receipt, load, unload, snap, pactl, run

REPS = 3
T = "r80_c"


def find(name):
    s = snap()
    return {k: v for k, v in s["nodes"].items() if v.get("name") == name}


def main():
    rc = Receipt("p10-client-scope")
    for rep in range(REPS):
        for label, extra in (("plain", ""),
                             ("linger", " object.linger=true"),
                             ("register-false", " object.register=false")):
            nm = f"{T}_{label.replace('-','_')}"
            props = (f"{{ factory.name=support.null-audio-sink node.name={nm} "
                     f"media.class=Audio/Sink{extra} }}")
            r = run(["pw-cli", "create-node", "adapter", props], timeout=20)
            # pw-cli exits here; the node was client-scoped
            time.sleep(0.8)
            after = find(nm)
            ps = pactl("list", "short", "sinks")["stdout"]
            rc.leg(f"{label}-rep{rep}", {"cmd": r["cmd"], "run": r, "name": nm,
                                         "nodes_after_pwcli_exit": after,
                                         "pactl_sees": nm in ps})
            rc.note(f"{label:14s} rep{rep} rc={r['rc']} err={r['stderr'].strip()[:60]!r} "
                    f"node_after_exit={list(after)} pactl_sees={nm in ps}")
            for k in after:
                run(["pw-cli", "destroy", str(k)], timeout=20)
            time.sleep(0.2)

        # long-lived pw-cli: does the node live as long as the client does?
        nm = f"{T}_held"
        p = subprocess.Popen(["pw-cli", "create-node", "adapter",
                              f"{{ factory.name=support.null-audio-sink node.name={nm} media.class=Audio/Sink }}"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        time.sleep(1.0)
        alive = find(nm)
        p.terminate()
        try:
            p.wait(timeout=3)
        except Exception:
            p.kill()
        time.sleep(0.8)
        gone = find(nm)
        rc.leg(f"held-rep{rep}", {"name": nm, "alive_while_pwcli_running": alive,
                                  "after_kill": gone})
        rc.note(f"held           rep{rep} alive_while_running={list(alive)} after_kill={list(gone)}")
        for k in gone:
            run(["pw-cli", "destroy", str(k)], timeout=20)
        # reference: a pactl module's node outlives the pactl process by design
        idx, lr = load("module-null-sink", f"sink_name={T}_srv")
        time.sleep(0.5)
        alive_srv = find(f"{T}_srv")
        rc.leg(f"server-owned-rep{rep}", {"index": idx, "load": lr,
                                          "node_after_pactl_exit": alive_srv})
        rc.note(f"server-owned   rep{rep} idx={idx} node_after_pactl_exit={list(alive_srv)}")
        unload(idx)
        time.sleep(0.3)
    rc.close()


if __name__ == "__main__":
    main()
