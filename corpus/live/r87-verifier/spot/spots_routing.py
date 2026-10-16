#!/usr/bin/env python3
"""r87-verifier routing-precedence spot (verifier-owned; no fixture
import).

Independently re-derives the boundary-CORRECTED binding chain that the
r87 landing arms:

    target.object (env > last -P) > --target flag > node.target
    object.serial resolves on both paths; object.id never resolves;
    a garbage --target does NOT fall through to node.target.

Method: verifier-owned `r87v_<pid>` null sinks; each leg spawns
`pw-play` with a verifier-generated 2 s tone and a tagged node name; the
verdict is the LINK witness (pw-dump link output-node-id -> input-node-id
into ns / ns2 / the default sink), never intent props.

Safety: own namespace, own modules unloaded by name-verified index; the
only foreign object ever linked is the host default sink, for the
garbage-target legs (the fixture's own design), with a quiet tone.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
import wave

PID = os.getpid()
NS = f"r87v_ns_{PID}"
NS2 = f"r87v_ns2_{PID}"
TONE = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"r87v-tone-{PID}.wav")


def tone(path, seconds=2.0, amp=0.05):
    import math
    import struct
    n = int(48000 * seconds)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"".join(
            struct.pack("<h", int(32767 * amp * math.sin(2 * math.pi * 440 * i / 48000)))
            for i in range(n)))
    return path


def sh(argv, timeout=20):
    p = subprocess.run(argv, capture_output=True, timeout=timeout)
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def load_sink(name):
    rc, out, err = sh(["pactl", "load-module", "module-null-sink",
                       f"sink_name={name}",
                       f"media.class=Audio/Sink"])
    idx = out.strip() if rc == 0 else None
    # name-verified: find the module index whose arg carries OUR name
    rc2, lst, _ = sh(["pactl", "list", "modules", "short"])
    verified = None
    for ln in lst.splitlines():
        if f"sink_name={name}" in ln:
            verified = ln.split("\t")[0].strip()
    return {"loaded_index": idx, "verified_index": verified,
            "rc": rc, "err": err.strip()[:120]}


def unload_sink(name):
    rc, lst, _ = sh(["pactl", "list", "modules", "short"])
    for ln in lst.splitlines():
        if f"sink_name={name}" in ln:
            idx = ln.split("\t")[0].strip()
            rc2, _, err = sh(["pactl", "unload-module", idx])
            return {"index": idx, "rc": rc2, "err": err.strip()[:120]}
    return {"index": None, "rc": None, "err": "not listed"}


def dump():
    p = subprocess.run(["pw-dump"], capture_output=True, timeout=30)
    return json.loads(p.stdout.decode())


def node_by_name(d, name):
    for o in d:
        pr = (o.get("info") or {}).get("props") or {}
        if o.get("type") == "PipeWire:Interface:Node" and \
                pr.get("node.name") == name:
            return {"id": o["id"], "serial": pr.get("object.serial"),
                    "objid": pr.get("object.id"),
                    "class": pr.get("media.class")}
    return None


def consumers(d, stream_id):
    """Node names the stream node feeds."""
    names = {}
    for o in d:
        if o.get("type") == "PipeWire:Interface:Node":
            names[o["id"]] = ((o.get("info") or {}).get("props") or {}) \
                .get("node.name")
    out = []
    for o in d:
        if o.get("type") == "PipeWire:Interface:Link":
            if (o.get("info") or {}).get("output-node-id") == stream_id:
                n = names.get((o.get("info") or {}).get("input-node-id"))
                if n and n not in out:
                    out.append(n)
    return out


def default_sink():
    return sh(["pactl", "get-default-sink"])[1].strip()


def leg(name, argv, props, expect, wait=(0.9, 1.7), env=None):
    penv = dict(os.environ)
    if env:
        penv.update(env)
    p = subprocess.Popen(["pw-play", "--volume", "0.05",
                          "-P", f"node.name={NS}_{name}", *argv,
                          *[x for pair in props for x in ("-P", pair)],
                          TONE],
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL, start_new_session=True,
                         env=penv)
    snaps = []
    for t in wait:
        time.sleep(t - (snaps[-1]["t"] if snaps else 0.0))
        d = dump()
        n = node_by_name(d, f"{NS}_{name}")
        snaps.append({"t": t, "node": bool(n),
                      "consumers": consumers(d, n["id"]) if n else []})
    if p.poll() is None:
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    try:
        p.wait(timeout=4)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        p.wait(timeout=3)
    cons = snaps[-1]["consumers"] if snaps else []
    if expect == "default_not_ns2":
        ok = bool(cons) and NS2 not in cons and NS not in cons
    elif expect == "not_ns2":
        ok = NS2 not in cons
    else:
        ok = cons == expect
    return {"leg": name, "argv": argv, "props": list(props),
            "env": env, "snaps": snaps, "consumers": cons,
            "expected": expect, "ok": ok}


def main():
    out = {"loadavg": open("/proc/loadavg").read().strip(),
           "ns": NS, "ns2": NS2, "legs": []}
    out["tone_bytes"] = os.path.getsize(tone(TONE))
    a = load_sink(NS)
    b = load_sink(NS2)
    out["load"] = {"ns": a, "ns2": b}
    try:
        time.sleep(0.8)
        d = dump()
        n1, n2 = node_by_name(d, NS), node_by_name(d, NS2)
        out["nodes"] = {"ns": n1, "ns2": n2}
        defv = default_sink()
        out["default_sink"] = defv
        L = out["legs"]
        L.append(leg("p_own", ["--target", NS], (), [NS]))
        L.append(leg("p_flag_beats_nt", ["--target", NS],
                     (f"node.target={NS2}",), [NS]))
        L.append(leg("p_nt_alone", [], (f"node.target={NS2}",), [NS2]))
        L.append(leg("p_prop_beats_flag", ["--target", NS],
                     (f"target.object={NS2}",), [NS2]))
        L.append(leg("p_env_beats_prop", ["--target", NS],
                     (f"target.object={NS}",), [NS2],
                     env={"PIPEWIRE_PROPS":
                          "{ target.object=" + NS2 + " }"}))
        L.append(leg("p_zero", ["--target", "0"], (), []))
        if n2:
            L.append(leg("p_prop_serial", [],
                         (f"target.object={n2['serial']}",), [NS2]))
            L.append(leg("p_objid_flag", ["--target", str(n2["objid"])],
                         (), "default_not_ns2"))
        L.append(leg("p_garbage_nt", ["--target", "r87v_no_such"],
                     (f"node.target={NS2}",), "default_not_ns2"))
        out["summary"] = {
            "legs": len(L),
            "ok": sum(1 for l in L if l["ok"]),
            "fail": [l["leg"] for l in L if not l["ok"]],
        }
    finally:
        out["unload"] = {"ns": unload_sink(NS), "ns2": unload_sink(NS2)}
        try:
            os.unlink(TONE)
        except OSError:
            pass
    print(json.dumps(out, indent=1))
    return 0 if out["summary"]["fail"] == [] else 1


if __name__ == "__main__":
    sys.exit(main())
