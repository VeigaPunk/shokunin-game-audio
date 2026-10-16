#!/usr/bin/env python3
"""r87-verifier pin-leg repro (verifier-owned; no fixture import).

The r87 `pin` leg: spawn `pw-midirecord --target 0`, link
`Midi-Bridge:<capture port>` -> own `input_1`, inject via `aplaymidi -p
<seq>` and require the recorded SMF to carry the injected note-ons/offs
(45 B in the author runs). One wave replay (r87v2) saw pw-link rc=0 with
zero edges visible at +0.4 s and a 0-byte SMF. This repro re-runs the
same shape with verifier-owned code and an `r87v_<pid>` namespace, three
reps, recording every stage.

Safety: own namespace only; recorder is SIGTERM'd then SIGKILL'd; the
link dies with the recorder's port; nothing global is written.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time

PID = os.getpid()
NS = f"r87v_{PID}"
SMF = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"r87v-pin-{PID}.mid")


def write_smf(path):
    trk = bytes.fromhex("55903c60"      # delta 0x55, note-on C4 vel 96
                        "8300803c00"    # note-off C4
                        "8140904060"    # note-on E4
                        "8140804000"    # note-off E4
                        "00ff2f00")     # end of track
    mthd = bytes.fromhex("4d54686400000006000000010060")
    mtrk = bytes.fromhex("4d54726b") + len(trk).to_bytes(4, "big") + trk
    with open(path, "wb") as f:
        f.write(mthd + mtrk)
    return len(mthd + mtrk)


def dump():
    p = subprocess.run(["pw-dump"], capture_output=True, timeout=30)
    return json.loads(p.stdout.decode())


def find_bridge(d):
    node = port = None
    for o in d:
        pr = (o.get("info") or {}).get("props") or {}
        if o.get("type") == "PipeWire:Interface:Node" and \
                pr.get("node.name") == "Midi-Bridge":
            node = o["id"]
    for o in d:
        pr = (o.get("info") or {}).get("props") or {}
        if o.get("type") == "PipeWire:Interface:Port" and \
                pr.get("node.id") == node and \
                pr.get("port.direction") == "out":
            port = pr.get("port.name")
    return node, port


def find_node(d, name):
    for o in d:
        pr = (o.get("info") or {}).get("props") or {}
        if o.get("type") == "PipeWire:Interface:Node" and \
                pr.get("node.name") == name:
            return o["id"]
    return None


def in_ports(d, nid):
    out = []
    for o in d:
        pr = (o.get("info") or {}).get("props") or {}
        if o.get("type") == "PipeWire:Interface:Port" and \
                o.get("info", {}).get("props", {}).get("node.id") == nid and \
                pr.get("port.direction") == "in":
            out.append(pr.get("port.name"))
    return sorted(out)


def edges_in(d, name):
    """Links whose input node is `name` (pw-dump link node-id fields)."""
    nodes = {}
    for o in d:
        if o.get("type") == "PipeWire:Interface:Node":
            nodes[o["id"]] = (o.get("info") or {}).get("props", {}) \
                .get("node.name")
    out = []
    for o in d:
        if o.get("type") == "PipeWire:Interface:Link":
            i = (o.get("info") or {}).get("input-node-id")
            op = (o.get("info") or {}).get("output-node-id")
            if nodes.get(i) == name:
                out.append({"in_node": nodes.get(i), "out_node": nodes.get(op)})
    return out


def seq_port():
    p = subprocess.run(["aplaymidi", "-l"], capture_output=True, timeout=10)
    m = re.search(r"^\s*(\d+:\d+)\s+.*Midi Through", p.stdout.decode(),
                  re.M)
    return m.group(1) if m else None


def witness(path):
    if not os.path.exists(path):
        return {"exists": False}
    b = open(path, "rb").read()
    return {"exists": True, "bytes": len(b), "has_mthd": b[:4] == b"MThd",
            "note_ons": b.count(b"\x90"), "note_offs": b.count(b"\x80"),
            "head_hex": b[:48].hex()}


def rep(i):
    rec = os.path.join(os.environ.get("TMPDIR", "/tmp"),
                       f"r87v-pin-{PID}-{i}.mid")
    d = dump()
    bnode, bport = find_bridge(d)
    seq = seq_port()
    r = {"rep": i, "bridge_node": bnode, "bridge_port": bport, "seq": seq}
    p = subprocess.Popen(["pw-midirecord", "-P", f"node.name={NS}_mr",
                          "--target", "0", rec],
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL, start_new_session=True)
    time.sleep(1.2)
    d = dump()
    nid = find_node(d, f"{NS}_mr")
    r["node_found"] = nid is not None
    if nid is None:
        r["record_rc"] = p.poll()
        return r
    ports = in_ports(d, nid)
    r["in_ports"] = ports
    if not ports:
        return r
    lk = subprocess.run(["pw-link", f"Midi-Bridge:{bport}",
                         f"{NS}_mr:{ports[0]}"],
                        capture_output=True, timeout=15)
    r["pwlink_rc"] = lk.returncode
    r["pwlink_err"] = lk.stderr.decode(errors="replace")[-120:]
    time.sleep(0.4)
    r["edges_at_0.4s"] = len(edges_in(dump(), f"{NS}_mr"))
    inj = subprocess.run(["aplaymidi", "-p", seq, SMF],
                         capture_output=True, timeout=20)
    r["aplay_rc"] = inj.returncode
    time.sleep(1.2)
    r["edges_at_1.6s"] = len(edges_in(dump(), f"{NS}_mr"))
    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    try:
        p.wait(timeout=3)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        p.wait(timeout=3)
    r["record_rc"] = p.returncode
    r["file"] = witness(rec)
    try:
        os.unlink(rec)
    except OSError:
        pass
    return r


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    size = write_smf(SMF)
    out = {"loadavg_start": open("/proc/loadavg").read().strip(),
           "smf_bytes": size, "ns": NS, "reps": []}
    for i in range(n):
        out["reps"].append(rep(i))
        print(json.dumps(out["reps"][-1]))
    out["loadavg_end"] = open("/proc/loadavg").read().strip()
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
