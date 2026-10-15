#!/usr/bin/env python3
"""P9 — native node/module namespace vs the pulse namespace, plus the
module-pipe-sink FIFO.  REPS reps per row."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r80_probe import Receipt, load, unload, snap, pactl, run

REPS = 3
T = "r80_n"
FIFO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp", "r80_p9.fifo")


def find(name):
    s = snap()
    return {k: v for k, v in s["nodes"].items() if v.get("name") == name}


def main():
    rc = Receipt("p9-native-namespace")
    ROWS = [
        ("adapter-load-module", ["pw-cli", "load-module", "libpipewire-module-adapter",
                                 f"{{ factory.name=support.null-audio-sink node.name={T}_a media.class=Audio/Sink node.description=r80native }}"]),
        ("adapter-create-node", ["pw-cli", "create-node", "adapter",
                                 f"{{ factory.name=support.null-audio-sink node.name={T}_b media.class=Audio/Sink }}"]),
        ("null-spa-factory-name", ["pw-cli", "load-module", "libpipewire-module-null-audio-sink",
                                   f"{{ node.name={T}_c }}"]),
    ]
    for label, cmd in ROWS:
        reps = []
        for rep in range(REPS):
            r = run(cmd, timeout=20)
            time.sleep(0.6)
            nm = cmd[cmd.index("node.name=" + T) if False else 0]  # placeholder
            nm = [t for t in cmd if "node.name=" in t][0].split("node.name=")[1].split()[0].strip("}") \
                if any("node.name=" in t for t in cmd) else None
            ns = find(nm) if nm else {}
            psinks = pactl("list", "short", "sinks")["stdout"]
            pmods = pactl("list", "short", "modules")["stdout"]
            # try to unload it via pactl (should fail: no pulse module index)
            pu = pactl("unload-module", str(list(ns)[0])) if ns else None
            # try the pulse module listing for our node
            reps.append({"rep": rep, "cmd": cmd, "run": r, "name": nm, "nodes": ns,
                         "pactl_sink_sees": nm in psinks if nm else None,
                         "pactl_module_list_len": len([l for l in pmods.splitlines() if l.split('\t')[0].strip().isdigit()]),
                         "pactl_unload_node_id": pu,
                         "node_alive_after_pactl_unload": bool(find(nm)) if nm else None})
            # native destroy
            if ns:
                d = run(["pw-cli", "destroy", str(list(ns)[0])], timeout=20)
                time.sleep(0.4)
                reps[-1]["pw_cli_destroy"] = d
                reps[-1]["gone_after_destroy"] = not bool(find(nm))
            time.sleep(0.3)
        rc.leg(label, {"cmd": cmd, "reps": reps})
        x = reps[0]
        rc.note(f"{label:22s} rc={x['run']['rc']} err={x['run']['stderr'].strip()[:70]!r} "
                f"stdout={x['run']['stdout'].strip()[:60]!r} name={x['name']} nodes={list(x['nodes'])} "
                f"pactl_sees_sink={x['pactl_sink_sees']} pactl_unload_rc={x['pactl_unload_node_id']['rc'] if x['pactl_unload_node_id'] else None} "
                f"gone_after_destroy={x.get('gone_after_destroy')}")

    # ---- module-pipe-sink: does the FIFO appear?
    for rep in range(REPS):
        if os.path.exists(FIFO):
            os.unlink(FIFO)
        idx, r = load("module-pipe-sink", f"sink_name={T}_pipe", f"file={FIFO}")
        time.sleep(0.8)
        exists_after_load = os.path.exists(FIFO)
        mode = oct(os.stat(FIFO).st_mode) if exists_after_load else None
        ns = {k: v for k, v in snap()["nodes"].items() if v.get("pulse.module.id") == idx}
        u = unload(idx)
        time.sleep(0.6)
        exists_after_unload = os.path.exists(FIFO)
        rc.leg(f"pipe-fifo-rep{rep}", {"index": idx, "load": r,
                                       "fifo_after_load": exists_after_load, "mode": mode,
                                       "nodes": ns, "unload": u,
                                       "fifo_after_unload": exists_after_unload})
        rc.note(f"pipe rep{rep} rc={r['rc']} idx={idx} fifo_after_load={exists_after_load} "
                f"mode={mode} nodes={[(v['name'], v['class']) for v in ns.values()]} "
                f"fifo_after_unload={exists_after_unload}")
        if os.path.exists(FIFO):
            os.unlink(FIFO)
        time.sleep(0.3)
    rc.close()


if __name__ == "__main__":
    main()
