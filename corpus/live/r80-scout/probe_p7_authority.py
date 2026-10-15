#!/usr/bin/env python3
"""P7 — who may create links, and who tears them down:
  * pw-link (linger) vs pw-link -m (non-linger) vs pw-cli create-link
  * pactl move-sink-input as the pulse-level reroute (temporary or sticky?)
  * node.dont-move / object.linger on streams
  * pw-cli load-module (native namespace) vs pactl (pulse namespace)
  * wpctl surface (read-only)
REPS reps per row.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r80_probe import Receipt, load, unload, snap, pactl, run, TONE, SR

REPS = 3
T = "r80_q"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")


def spawn(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def kill(p):
    if p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=2)
        except Exception:
            p.kill()
    return p.poll()



def sink_input_of(node_name):
    """pactl -f json list sink-inputs -> index of the stream whose
    node.name == node_name."""
    e = sink_input_entry(node_name)
    return str(e.get("index")) if e else None


def sink_input_entry(node_name):
    r = pactl("-f", "json", "list", "sink-inputs")
    try:
        arr = json.loads(r["stdout"])
    except Exception:
        return None
    for e in arr:
        if (e.get("properties") or {}).get("node.name") == node_name:
            return e
    return None

def nid(name):
    s = snap()
    return next((int(k) for k, v in s["nodes"].items() if v.get("name") == name), None)


def links_touching(prefix):
    s = snap()
    return [l["out"] + "->" + l["in"] for l in s["links"]
            if l["out"].split(":")[0].startswith(prefix) or
            l["in"].split(":")[0].startswith(prefix)]


def clean(prefix=T):
    for k, v in snap()["nodes"].items():
        if (v.get("name") or "").startswith(prefix):
            run(["pw-cli", "destroy", str(k)])


def main():
    rc = Receipt("p7-linkauthority")
    want = set(sys.argv[1:]) or {"A", "B", "C", "D", "E", "F"}

    # ---- A: pw-link (linger) survives? pw-link -m (non-linger) survives?
    if "A" in want:
        for rep in range(REPS):
            idx, _ = load("module-null-sink", f"sink_name={T}_ns")
            time.sleep(0.4)
            p = spawn(["pw-record", "-P", f"node.name={T}_rec", "-P", "stream.capture.sink=true",
                       "--target", "0", "-n", str(3 * SR), os.path.join(OUT, "q-a.wav")])
            time.sleep(1.2)
            ports = [x for x in run(["pw-link", "-o"])["stdout"].split()
                     if x.startswith(f"{T}_ns:")]
            inports = [x for x in run(["pw-link", "-i"])["stdout"].split()
                       if x.startswith(f"{T}_rec:")]
            a = {}
            if ports and inports:
                a["linger"] = run(["pw-link", ports[0], inports[0]])
            s1 = snap()
            n1 = [l["out"] + "->" + l["in"] for l in s1["links"] if f"{T}_rec" in l["in"] or f"{T}_rec" in l["out"]]
            time.sleep(2.0)
            s2 = snap()
            n2 = [l["out"] + "->" + l["in"] for l in s2["links"] if f"{T}_rec" in l["in"] or f"{T}_rec" in l["out"]]
            kill(p)
            time.sleep(0.3)
            # non-linger: -m without -L
            p2 = spawn(["pw-record", "-P", f"node.name={T}_rec2", "-P", "stream.capture.sink=true",
                        "--target", "0", "-n", str(3 * SR), os.path.join(OUT, "q-a2.wav")])
            time.sleep(1.2)
            ports2 = [x for x in run(["pw-link", "-o"])["stdout"].split()
                      if x.startswith(f"{T}_ns:")]
            inports2 = [x for x in run(["pw-link", "-i"])["stdout"].split()
                        if x.startswith(f"{T}_rec2:")]
            b = {}
            if ports2 and inports2:
                m = spawn(["pw-link", "-m", ports2[0], inports2[0]])
                time.sleep(1.5)
                b["link_while_m_running"] = links_touching(f"{T}_rec2")
                kill(m)
                time.sleep(1.0)
                b["link_after_m_killed"] = links_touching(f"{T}_rec2")
            kill(p2)
            rc.leg(f"A-rep{rep}", {"create_linger": a, "links_immediately": n1,
                                   "links_after_2s": n2, "nonlinger": b})
            rc.note(f"A rep{rep} pw-link rc={a.get('linger',{}).get('rc')} "
                    f"links_now={n1} links_after_2s={n2} "
                    f"m_while={b.get('link_while_m_running')} m_after_kill={b.get('link_after_m_killed')}")
            unload(idx)
            clean()
            time.sleep(0.3)

    # ---- B: pactl move-sink-input — sticky or temporary?
    if "B" in want:
        for rep in range(REPS):
            i1, _ = load("module-null-sink", f"sink_name={T}_m1")
            i2, _ = load("module-null-sink", f"sink_name={T}_m2")
            time.sleep(0.4)
            p = spawn(["pw-cat", "-p", "--target", f"{T}_m1", "--volume", "0.05",
                       "-P", f"node.name={T}_play", TONE])
            time.sleep(1.2)
            idx_in = sink_input_of(f"{T}_play")
            before = links_touching(f"{T}_play")
            mv = pactl("move-sink-input", str(idx_in), f"{T}_m2") if idx_in else None
            time.sleep(1.0)
            just = links_touching(f"{T}_play")
            time.sleep(2.5)
            later = links_touching(f"{T}_play")
            time.sleep(2.5)
            last = links_touching(f"{T}_play")
            node_props = {}
            n = nid(f"{T}_play")
            if n:
                d = run(["pw-dump", str(n)])
                try:
                    node_props = json.loads(d["stdout"])[0]["info"]["props"]
                except Exception:
                    node_props = {"_err": d["stdout"][:200]}
            kill(p)
            rc.leg(f"B-rep{rep}", {"sink_input_index": idx_in, "move": mv,
                                   "links_before": before, "links_after_1s": just,
                                   "links_after_3.5s": later, "links_after_6s": last,
                                   "stream_props": {k: node_props.get(k) for k in
                                                    ("node.dont-move", "target.object",
                                                     "node.target", "stream.dont-remix",
                                                     "media.class", "node.name")}})
            rc.note(f"B rep{rep} idx={idx_in} move_rc={mv['rc'] if mv else None} "
                    f"err={mv['stderr'].strip() if mv else ''!r} "
                    f"before={before} +1s={just} +3.5s={later} +6s={last}")
            unload(i1)
            unload(i2)
            clean()
            time.sleep(0.3)

    # ---- C: node.dont-move=true on the stream, then pulse move
    if "C" in want:
        for rep in range(REPS):
            i1, _ = load("module-null-sink", f"sink_name={T}_d1")
            i2, _ = load("module-null-sink", f"sink_name={T}_d2")
            time.sleep(0.4)
            p = spawn(["pw-cat", "-p", "--target", f"{T}_d1", "--volume", "0.05",
                       "-P", f"node.name={T}_playd", "-P", "node.dont-move=true", TONE])
            time.sleep(1.2)
            idx_in = sink_input_of(f"{T}_playd")
            before = links_touching(f"{T}_playd")
            props = {}
            n = nid(f"{T}_playd")
            if n:
                d = run(["pw-dump", str(n)])
                try:
                    props = json.loads(d["stdout"])[0]["info"]["props"]
                except Exception:
                    props = {}
            mv = pactl("move-sink-input", str(idx_in), f"{T}_d2") if idx_in else None
            time.sleep(1.2)
            after = links_touching(f"{T}_playd")
            kill(p)
            rc.leg(f"C-rep{rep}", {"sink_input_index": idx_in, "move": mv,
                                   "links_before": before, "links_after": after,
                                   "prop_on_node": props.get("node.dont-move"),
                                   "prop_all": {k: v for k, v in props.items()
                                                if "dont" in k or "move" in k}})
            rc.note(f"C rep{rep} dont-move prop={props.get('node.dont-move')!r} "
                    f"+ move rc={mv['rc'] if mv else None} before={before} after={after}")
            unload(i1)
            unload(i2)
            clean()
            time.sleep(0.3)

    # ---- D: object.linger on a stream — does the node outlive the client?
    if "D" in want:
        for rep in range(REPS):
            i1, _ = load("module-null-sink", f"sink_name={T}_l1")
            time.sleep(0.4)
            p = spawn(["pw-cat", "-p", "--target", f"{T}_l1", "--volume", "0.05",
                       "-P", f"node.name={T}_playl", "-P", "object.linger=true", TONE])
            time.sleep(1.5)
            n_before = nid(f"{T}_playl")
            props = {}
            if n_before:
                d = run(["pw-dump", str(n_before)])
                try:
                    props = json.loads(d["stdout"])[0]["info"]["props"]
                except Exception:
                    props = {}
            kill(p)
            time.sleep(1.0)
            n_after = nid(f"{T}_playl")
            s = snap()
            rc.leg(f"D-rep{rep}", {"node_before": n_before, "node_after_client_death": n_after,
                                   "props": {k: props.get(k) for k in
                                             ("object.linger", "client.id", "media.class",
                                              "node.name", "node.dont-move", "node.linger")},
                                   "links_after": links_touching(f"{T}_playl")})
            rc.note(f"D rep{rep} object.linger on stream: node_before={n_before} "
                    f"after_client_death={n_after} props={json.dumps({k: props.get(k) for k in ('object.linger','client.id','node.linger')})}")
            unload(i1)
            clean()
            time.sleep(0.3)

    # ---- E: pw-cli load-module (native namespace) vs pactl
    if "E" in want:
        for rep in range(REPS):
            lm = run(["pw-cli", "load-module", "libpipewire-module-null-audio-sink",
                      "{ node.name=r80_q_nat sink.props={ media.class=Audio/Sink } }"], timeout=20)
            time.sleep(0.6)
            s = snap()
            nat = {k: v for k, v in s["nodes"].items() if v.get("name") == "r80_q_nat"}
            pmods = pactl("list", "short", "modules")["stdout"]
            psinks = pactl("list", "short", "sinks")["stdout"]
            # native module id from pw-cli output var, and pactl's view
            var = None
            for tok in lm["stdout"].split():
                if tok.isdigit():
                    var = tok
            um = run(["pw-cli", "unload-module", var], timeout=20) if var else None
            time.sleep(0.6)
            s2 = snap()
            gone = not any(v.get("name") == "r80_q_nat" for v in s2["nodes"].values())
            rc.leg(f"E-rep{rep}", {"load": lm, "var": var, "nodes": nat,
                                   "pactl_sees_sink": "r80_q_nat" in psinks,
                                   "pactl_module_list_has_native": "libpipewire" in pmods,
                                   "unload": um, "node_gone": gone})
            rc.note(f"E rep{rep} pw-cli load-module rc={lm['rc']} out={lm['stdout'].strip()[:80]!r} "
                    f"err={lm['stderr'].strip()[:80]!r} node={list(nat)} "
                    f"pactl_sees_sink={'r80_q_nat' in psinks} unload_rc={um['rc'] if um else None} gone={gone}")
            # also: pactl load-module of a native name
            bad = pactl("load-module", "libpipewire-module-null-audio-sink")
            rc.note(f"E rep{rep} pactl load-module libpipewire-module-null-audio-sink rc={bad['rc']} err={bad['stderr'].strip()!r}")
            clean()
            time.sleep(0.3)

    # ---- F: wpctl surface (read-only) + does it see pulse modules?
    if "F" in want:
        i1, _ = load("module-null-sink", f"sink_name={T}_w1")
        time.sleep(0.5)
        st = run(["wpctl", "status"], timeout=20)
        ins = run(["wpctl", "inspect", f"{T}_w1"], timeout=20)
        settings = run(["wpctl", "settings"], timeout=20)
        rc.leg("F-wpctl", {"load_idx": i1, "status": st, "inspect": ins, "settings": settings})
        rc.note("wpctl status rc=%s (sinks section has r80_q_w1: %s)" %
                (st["rc"], f"{T}_w1" in st["stdout"]))
        rc.note("wpctl inspect rc=%s len=%d" % (ins["rc"], len(ins["stdout"])))
        for ln in ins["stdout"].splitlines()[:6]:
            rc.note("   " + ln)
        rc.note("wpctl settings rc=%s first lines: %s" %
                (settings["rc"], " | ".join(settings["stdout"].splitlines()[:3])))
        rc.note("wpctl can see the pulse module index? " +
                str("pulse.module.id" in ins["stdout"]))
        unload(i1)
        clean()
    rc.close()


if __name__ == "__main__":
    main()
