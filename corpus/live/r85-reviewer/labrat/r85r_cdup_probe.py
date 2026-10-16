#!/usr/bin/env python3
"""In-seat bounded probe (the dispatched ufo-labrat seat had no shell tool).

H: the pw-cat `--target <digits>` resolution of a numeric string that is
BOTH a live sink's object.serial and a sink's literal name is host-state
dependent, and the name-first side is realizable on this host:
  (a) serial holder alive  -> the record links the holder's monitor_*;
  (b) holder unloaded      -> the same digits never link the digits-named
      sink's own monitor_* (no links, or a non-monitor link).

Probe-owned r85r_* objects only; name-verified unloads; no set-default-*;
no tone is ever played; TMPDIR is the shared lane tmp. Writes only under
corpus/live/r85-reviewer/labrat/.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

TMP = Path(os.environ.get("TMPDIR", "/tmp"))
OUT = Path(__file__).resolve().parent
PID = os.getpid()
A = f"r85r_a_{PID}"
B = f"r85r_b_{PID}"


def sh(argv, timeout=15):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        return {"argv": " ".join(argv), "rc": p.returncode,
                "out": p.stdout.decode(errors="replace")[:400],
                "err": p.stderr.decode(errors="replace")[:400]}
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"argv": " ".join(argv), "error": type(exc).__name__}


def graph():
    p = subprocess.run(["pw-dump"], capture_output=True, timeout=15)
    dump = json.loads(p.stdout or b"[]")
    nodes, ports, links = {}, {}, []
    for o in dump:
        t = str(o.get("type", ""))
        info = o.get("info") or {}
        props = info.get("props") or {}
        if t.endswith("Node"):
            nodes[o["id"]] = {"name": props.get("node.name"),
                              "serial": props.get("object.serial"),
                              "id": props.get("object.id")}
        elif t.endswith("Port"):
            ports[o["id"]] = {"node_id": info.get("node-id"),
                              "name": props.get("port.name")}
        elif t.endswith("Link"):
            links.append({"out_node": info.get("output-node-id"),
                          "out_port": info.get("output-port-id"),
                          "in_node": info.get("input-node-id"),
                          "in_port": info.get("input-port-id")})
    return {"nodes": nodes, "ports": ports, "links": links}


def node_by_name(g, name):
    # str()-compare: a purely numeric node.name is emitted as a JSON int
    # (the exact hazard the committed readers trip over).
    for nid, n in g["nodes"].items():
        if str(n.get("name")) == str(name):
            return n
    return None


def edges_in(g, node_name):
    out = []
    for l in g["links"]:
        on = (g["nodes"].get(l["out_node"]) or {}).get("name")
        inn = (g["nodes"].get(l["in_node"]) or {}).get("name")
        if inn is None or str(inn) != str(node_name):
            continue
        op = (g["ports"].get(l["out_port"]) or {}).get("name")
        ip = (g["ports"].get(l["in_port"]) or {}).get("name")
        out.append({"out": f"{on}:{op}", "in": f"{inn}:{ip}",
                    "out_node": on, "out_port": op,
                    "in_port": ip})
    return out


def module_index(field, value):
    p = subprocess.run(["pactl", "list", "modules", "short"],
                       capture_output=True, timeout=10)
    for ln in p.stdout.decode(errors="replace").splitlines():
        f = ln.split("\t")
        if not (f and f[0].strip().isdigit()):
            continue
        m = re.search(re.escape(field) + r"=(\S+)", ln)
        if m and m.group(1).strip("\"'") == value:
            return int(f[0].strip())
    return None


def unload_own(field, value):
    idx = module_index(field, value)
    if idx is None:
        return {"field": field, "value": value, "skipped": "not_listed"}
    r = sh(["pactl", "unload-module", str(idx)])
    return {"field": field, "value": value, "idx": idx, "rc": r.get("rc")}


def load(name):
    r = sh(["pactl", "load-module", "module-null-sink",
            "sink_name=" + name])
    return {"name": name, "rc": r.get("rc"), "module_id": r.get("out", "").strip()}


def wait_sink(name, timeout=12.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        g = graph()
        if node_by_name(g, name):
            return True
        time.sleep(0.1)
    return False


def capture_run(tag, target, seconds=2.5):
    """One bounded pw-record; sample links at ~0.9/1.9 s."""
    out = TMP / f"{tag}.wav"
    argv = ["pw-record", "-P", f"node.name={tag}", "--target", str(target),
            "--rate", "48000", "--channels", "2", "--format", "s16", str(out)]
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                            start_new_session=True)
    rec = {"tag": tag, "target": str(target), "argv": " ".join(argv),
           "samples": []}
    t0 = time.monotonic()
    for at in (0.9, 1.9):
        left = at - (time.monotonic() - t0)
        if left > 0:
            time.sleep(left)
        g = graph()
        rec["samples"].append(
            {"at_s": round(time.monotonic() - t0, 2),
             "links": edges_in(g, tag),
             "node_alive": node_by_name(g, tag) is not None,
             "size": out.stat().st_size if out.exists() else None})
    left = seconds - (time.monotonic() - t0)
    if left > 0:
        time.sleep(left)
    rec["alive_at_end"] = proc.poll() is None
    if proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        proc.wait(timeout=4.0)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
    rec["exit_code"] = proc.returncode
    rec["stderr_tail"] = proc.stderr.read().decode(errors="replace")[:200]
    rec["file_bytes"] = out.stat().st_size if out.exists() else None
    return rec


def main():
    report = {"pid": PID, "tmpdir": str(TMP), "hypothesis": "cdup either-way",
              "steps": {}}
    try:
        report["steps"]["load_a"] = load(A)
        report["steps"]["load_b"] = load(B)
        if not (wait_sink(A) and wait_sink(B)):
            report["verdict"] = "INCONCLUSIVE"
            report["why"] = "probe sinks never enumerated"
            return report
        g = graph()
        na = node_by_name(g, A) or {}
        ser = na.get("serial")
        report["serial_a"] = ser
        if ser is None:
            report["verdict"] = "INCONCLUSIVE"
            report["why"] = "serial never resolved"
            return report
        report["steps"]["load_digits_named"] = load(str(ser))
        if not wait_sink(str(ser)):
            report["verdict"] = "INCONCLUSIVE"
            report["why"] = "digits-named sink never enumerated"
            return report
        report["steps"]["run_a"] = capture_run(
            f"r85r_cap1_{PID}", str(ser))
        report["steps"]["unload_a"] = unload_own("sink_name", A)
        time.sleep(0.6)
        report["steps"]["run_b"] = capture_run(
            f"r85r_cap2_{PID}", str(ser))
    finally:
        report["steps"]["teardown_b"] = unload_own("sink_name", B)
        report["steps"]["teardown_a"] = unload_own("sink_name", A)
        report["steps"]["teardown_digits"] = unload_own("sink_name", str(
            report.get("serial_a")))
        time.sleep(0.4)
        g = graph()
        report["residue_nodes"] = sorted(
            n["name"] for n in g["nodes"].values()
            if (n.get("name") or "").startswith("r85r_"))
    # verdicts
    ra = report["steps"].get("run_a") or {}
    rb = report["steps"].get("run_b") or {}
    a_links = [e for s in ra.get("samples", []) for e in s.get("links", [])]
    b_links = [e for s in rb.get("samples", []) for e in s.get("links", [])]
    a_mon = [e for e in a_links
             if (e.get("out_port") or "").startswith("monitor_")]
    b_mon = [e for e in b_links
             if (e.get("out_port") or "").startswith("monitor_")]
    report["a_links"] = a_links
    report["b_links"] = b_links
    report["a_monitor_links_to_holder"] = bool(a_mon) and all(
        str(e.get("out_node")) == str(A) for e in a_mon)
    report["b_monitor_links_to_digits_sink"] = any(
        str(e.get("out_node")) == str(report.get("serial_a"))
        for e in b_mon)
    if report["a_monitor_links_to_holder"] and \
            not report["b_monitor_links_to_digits_sink"]:
        report["verdict"] = "CONFIRMED (both sides realized: serial-first " \
                            "with holder alive; no digits-sink monitor " \
                            "link with holder unloaded)"
    elif not report["a_monitor_links_to_holder"]:
        report["verdict"] = "INCONCLUSIVE (side (a) did not realize)"
    else:
        report["verdict"] = "FALSIFIED (digits-named sink's own monitor " \
                            "linked in (b))"
    return report


if __name__ == "__main__":
    r = main()
    (OUT / "cdup-probe.json").write_text(
        json.dumps(r, indent=1, default=str) + "\n")
    print(json.dumps({k: r.get(k) for k in
                      ("verdict", "why", "serial_a",
                       "a_monitor_links_to_holder",
                       "b_monitor_links_to_digits_sink", "residue_nodes")},
                     indent=1))
    sys.exit(0)
