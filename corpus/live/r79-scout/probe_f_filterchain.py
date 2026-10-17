#!/usr/bin/env python3
"""R79 probe F — libpipewire-module-filter-chain.

Two loading paths, both bounded and probe-named:

 (1) conf.d fragments, the documented recipe: `pipewire -c filter-chain.conf`
     with PIPEWIRE_CONFIG_DIR pointing at a scratch config dir.  MEASURED
     MECHANISM: the filter-chain module is itself a CLIENT — it connects to the
     running session's socket and publishes its nodes there, so the loader
     needs no socket of its own and the nodes vanish when the loader is killed.
 (2) `pw-cli load-module libpipewire-module-filter-chain <args>` into the live
     daemon (client-scoped, unloadable).

Every fragment pins its playback target to a probe-owned null sink; the tone is
injected with manual pw-link pins (no fallback path to the shared default sink).
"""
import json
import os
import select
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r79_probe import (RAW, SCRATCH, TAG, Graph, analyze, kill, null_sink_load,
                       pw_dump, reap, rec_monitor, save, sh, spawn)

FC = "/tmp/r79fc-" + str(os.getpid())          # SHORT path: AF_UNIX sun_path
BASE = "/usr/share/pipewire/filter-chain.conf"
out = {"probe": "f-filterchain", "tag": TAG, "confd_legs": [], "cli_legs": []}
ns_a, ns_b = f"r79_ns_a_{TAG}", f"r79_ns_b_{TAG}"
mods = [null_sink_load(ns_a), null_sink_load(ns_b)]
time.sleep(0.5)


def log(m):
    print(m, flush=True)


def fc_args(node_in, node_out, target=None, label="mixer"):
    tgt = f'target.object = "{target}"' if target else "node.passive = true"
    return ("{ filter.graph = { nodes = [ { name = mix type = builtin "
            f"label = {label} control = {{ \"Gain 1\" = 0.5 \"Gain 2\" = 0.5 }} }} ] "
            "inputs = [ \"mix:In 1\" \"mix:In 2\" ] outputs = [ \"mix:Out\" ] } "
            f"capture.props = {{ node.name = \"{node_in}\" audio.position = [ FL FR ] "
            "media.class = \"Audio/Sink\" } "
            f"playback.props = {{ node.name = \"{node_out}\" audio.position = [ FL ] "
            f"stream.dont-remix = true {tgt} }} }}")


def fragment(node_in, node_out, target=None, label="mixer", flags=""):
    return ("context.modules = [ { name = libpipewire-module-filter-chain "
            f"{flags} args = " + fc_args(node_in, node_out, target, label)
            + " } ]\n")


def mkcfg(name, fragments):
    d = os.path.join(FC, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "filter-chain.conf.d"))
    shutil.copy(BASE, os.path.join(d, "filter-chain.conf"))
    for fn, body in fragments.items():
        with open(os.path.join(d, "filter-chain.conf.d", fn), "w") as fh:
            fh.write(body)
    return d


def confd_leg(leg_id, cfgdir, expect_node):
    """Documented recipe: a loader client against the LIVE session."""
    env = {"PIPEWIRE_CONFIG_DIR": cfgdir}
    p = spawn(["timeout", "-s", "KILL", "10", "pipewire", "-c", "filter-chain.conf"],
              env=env)
    leg = {"leg": leg_id, "cfg": cfgdir, "expect_node": expect_node}
    try:
        time.sleep(2.0)
        g = Graph(pw_dump())
        leg["loader_alive"] = p.poll() is None
        leg["nodes"] = [n for n in g.nodes if n.startswith("mix_input.r79_fc_")]
        leg["expect_met"] = expect_node in g.nodes
        if leg["expect_met"]:
            n = g.nodes[expect_node]
            leg["ports_in"] = [x[0] for x in n["in"]]
            leg["ports_out"] = [x[0] for x in n["out"]]
            tone_tag = f"{TAG}_{leg_id}_tone"
            tp = spawn(["pw-cat", "-p", "-P", f"node.name={tone_tag}", "--target",
                        "0", os.path.join(SCRATCH, "tone_r79_long.wav")])
            try:
                time.sleep(0.8)
                pins = []
                for ch, port in zip(("FL", "FR"),
                                    [x[0] for x in n["in"]][:2]):
                    r = sh(["pw-link", f"{tone_tag}:output_{ch}",
                            f"{expect_node}:{port}"], timeout=10.0)
                    pins.append({"ch": ch, "port": port, "rc": r["rc"],
                                 "err": r["err"].strip()})
                leg["pins"] = pins
                time.sleep(0.8)
                g2 = Graph(pw_dump())
                leg["edges"] = g2.edges("r79_fc_")
                path = os.path.join(RAW, f"{leg_id}_{TAG}.wav")
                rr = rec_monitor(ns_b, path, 24000, f"{TAG}_{leg_id}_rec")
                leg["record"] = {"rc": rr["rc"], "bytes": rr["bytes"],
                                 "err": rr["err"].strip()}
                leg["content"] = analyze(path)
            finally:
                kill(tp)
    finally:
        kill(p)
        leg["rc"] = p.returncode
        leg["stderr"] = reap(p, wait=1.0)["stderr"]
        time.sleep(0.5)
        g3 = Graph(pw_dump())
        leg["nodes_after_kill"] = [n for n in g3.nodes
                                   if n.startswith("mix_input.r79_fc_")]
    return leg


try:
    cfgs = {
        "F1-confd-good": mkcfg("f1", {"10-good.conf": fragment(
            "mix_input.r79_fc_good", "mix_output.r79_fc_good", target=ns_b)}),
        "F2-confd-bad-syntax": mkcfg("f2", {"10-bad.conf": "context.modules = [ { name = x\n"}),
        "F3-confd-good-plus-bad": mkcfg("f3", {
            "10-good.conf": fragment("mix_input.r79_fc_mixed", "mix_output.r79_fc_mixed"),
            "20-bad.conf": "context.modules = [ { name = x\n"}),
        "F3b-confd-bad-then-good": mkcfg("f3b", {
            "10-bad.conf": "context.modules = [ { name = x\n",
            "20-good.conf": fragment("mix_input.r79_fc_late",
                                     "mix_output.r79_fc_late")}),
        "F4-confd-badlabel-nofail": mkcfg("f4", {"10-bl.conf": fragment(
            "mix_input.r79_fc_bl", "mix_output.r79_fc_bl", label="nosuchfilter",
            flags="flags = [ nofail ]")}),
        "F5-confd-badlabel": mkcfg("f5", {"10-bl.conf": fragment(
            "mix_input.r79_fc_bl2", "mix_output.r79_fc_bl2", label="nosuchfilter")}),
        "F6-confd-base-only": mkcfg("f6", {}),
    }
    for lid, cfgdir in cfgs.items():
        want = {"F1-confd-good": "mix_input.r79_fc_good",
                "F3-confd-good-plus-bad": "mix_input.r79_fc_mixed",
                "F3b-confd-bad-then-good": mkcfg("f3b", {
            "10-bad.conf": "context.modules = [ { name = x\n",
            "20-good.conf": fragment("mix_input.r79_fc_late",
                                     "mix_output.r79_fc_late")}),
        "F4-confd-badlabel-nofail": "mix_input.r79_fc_bl",
                "F3b-confd-bad-then-good": "mix_input.r79_fc_late",
                "F5-confd-badlabel": "mix_input.r79_fc_bl2"}.get(lid, "mix_input.r79_fc_none")
        leg = confd_leg(lid, cfgdir, want)
        out["confd_legs"].append(leg)
        save("probe-f-filterchain-r79.json", out)
        log(f"{lid:26s} alive={leg['loader_alive']} expect_met={leg['expect_met']} "
            f"nodes={leg['nodes']} rc={leg['rc']} "
            f"content={(leg.get('content') or {}).get('class')} "
            f"after_kill={leg['nodes_after_kill']} "
            f"stderr={leg['stderr'][:140]!r}")

    # ---------------------------------------------------------- pw-cli path
    pcli = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def cli(cmd, wait=2.0):
        pcli.stdin.write((cmd + "\n").encode())
        pcli.stdin.flush()
        buf = b""
        deadline = time.monotonic() + wait
        while time.monotonic() < deadline:
            r, _, _ = select.select([pcli.stdout.fileno()], [], [], 0.3)
            if not r:
                continue
            chunk = os.read(pcli.stdout.fileno(), 65536)
            if not chunk:
                break
            buf += chunk
        return buf.decode(errors="replace")

    def replies(text):
        return [l for l in text.splitlines()
                if l.strip() and not l.startswith((" ", "\t")) and
                "added global" not in l and "remote 0" not in l and
                "Welcome" not in l and "unsupported type" not in l]

    try:
        args = fc_args("mix_input.r79_fc_live", "mix_output.r79_fc_live", target=ns_b)
        text = cli("load-module libpipewire-module-filter-chain " + args, 2.5)
        g = Graph(pw_dump())
        node = "mix_input.r79_fc_live"
        leg = {"leg": "F7-cli-load", "reply": replies(text),
               "nodes": [n for n in g.nodes if "r79_fc_live" in n],
               "ports_in": [x[0] for x in g.nodes[node]["in"]] if node in g.nodes else []}
        if node in g.nodes:
            tone_tag = f"{TAG}_f7tone"
            tp = spawn(["pw-cat", "-p", "-P", f"node.name={tone_tag}", "--target",
                        "0", os.path.join(SCRATCH, "tone_r79_long.wav")])
            try:
                time.sleep(0.8)
                pins = []
                for ch, port in zip(("FL", "FR"),
                                    [x[0] for x in g.nodes[node]["in"]][:2]):
                    r = sh(["pw-link", f"{tone_tag}:output_{ch}", f"{node}:{port}"],
                           timeout=10.0)
                    pins.append({"ch": ch, "port": port, "rc": r["rc"],
                                 "err": r["err"].strip()})
                leg["pins"] = pins
                time.sleep(0.8)
                leg["edges"] = Graph(pw_dump()).edges("r79_fc_live")
                path = os.path.join(RAW, f"F7-cli-load_{TAG}.wav")
                rr = rec_monitor(ns_b, path, 24000, f"{TAG}_f7rec")
                leg["record"] = {"rc": rr["rc"], "bytes": rr["bytes"]}
                leg["content"] = analyze(path)
            finally:
                kill(tp)
        out["cli_legs"].append(leg)
        save("probe-f-filterchain-r79.json", out)
        log(f"F7-cli-load reply={leg['reply']} nodes={leg['nodes']} "
            f"pins={leg.get('pins')} class={(leg.get('content') or {}).get('class')}")

        mvar = None
        for tok in " ".join(leg["reply"]).split():
            if tok.startswith("@module:"):
                mvar = tok
        # NON-DESTRUCTIVE: `unload-module <var>` is attempted with the var name
        # pw-cli printed; its refusal is the measured shape.  Never `destroy` an
        # id scraped from a pw-cli reply: those replies also carry the async
        # global dump, so a scraped id can name a daemon-owned module.
        text = cli(f"unload-module {mvar}" if mvar else "ls Module", 1.5)
        g = Graph(pw_dump())
        out["cli_legs"].append({"leg": "F8a-cli-unload-refusal", "mvar": mvar,
                                "reply": replies(text),
                                "nodes_still": [n for n in g.nodes
                                                if "r79_fc_live" in n]})
        save("probe-f-filterchain-r79.json", out)
        log(f"F8a unload {mvar} -> {out['cli_legs'][-1]['reply']} "
            f"nodes_still={out['cli_legs'][-1]['nodes_still']}")

        text = cli("load-module libpipewire-module-filter-chain " +
                   fc_args("mix_input.r79_fc_bad", "mix_output.r79_fc_bad",
                           target=ns_b, label="nosuchfilter"), 2.5)
        g = Graph(pw_dump())
        out["cli_legs"].append({"leg": "F9-cli-bad-label", "reply": replies(text),
                                "nodes_after": [n for n in g.nodes if "r79_fc_bad" in n],
                                "daemon_alive": pw_dump() is not None})
        save("probe-f-filterchain-r79.json", out)
        log(f"F9-cli-bad-label reply={out['cli_legs'][-1]['reply']} "
            f"nodes={out['cli_legs'][-1]['nodes_after']} alive={out['cli_legs'][-1]['daemon_alive']}")

        text = cli("load-module libpipewire-module-filter-chain { args = { oops", 1.5)
        out["cli_legs"].append({"leg": "F10-cli-bad-args", "reply": replies(text),
                                "daemon_alive": pw_dump() is not None})
        save("probe-f-filterchain-r79.json", out)
        log(f"F10-cli-bad-args reply={out['cli_legs'][-1]['reply']} "
            f"alive={out['cli_legs'][-1]['daemon_alive']}")
    finally:
        try:
            pcli.stdin.write(b"quit\n")
            pcli.stdin.flush()
            pcli.wait(timeout=4)
        except Exception:
            pass
        kill(pcli)
        time.sleep(0.8)
        g = Graph(pw_dump())
        out["cli_legs"].append({"leg": "F11-cli-quit-teardown",
                                "nodes_after_quit": [n for n in g.nodes
                                                     if "r79_fc_live" in n]})
        log(f"F11 nodes_after_quit={out['cli_legs'][-1]['nodes_after_quit']}")
finally:
    for m in mods:
        if m["module_id"]:
            sh(["pactl", "unload-module", str(m["module_id"])], timeout=10.0)
    out["cleanup"] = {"unloaded": [m["module_id"] for m in mods]}
    out["null_sinks"] = mods

save("probe-f-filterchain-r79.json", out)
log("saved")
