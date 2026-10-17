#!/usr/bin/env python3
"""r91 VERIFIER — full-family replay with the clock entry instrumented.

Runs the five committed entry functions in the battery's own order (prop,
clock, resume, srcloss, connect) on the frozen tree, wrapping every clock
leg with the target-liveness probe. Catches the c_alive red with context.

Usage: diag_family.py <out.json>
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

TREE = Path("/home/vgpnk/r91-verify-tree")
spec = importlib.util.spec_from_file_location(
    "ma_r91v", TREE / "corpus/fixtures/measure_audio.py")
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

NS = ma.GSTFRZ_R91_NS
orig_leg = ma._gstfrz_r91_leg
events = []


def pactl_probe():
    def rows(args, col):
        try:
            p = subprocess.run(["pactl", "list"] + args + ["short"],
                               capture_output=True, timeout=8)
            return [ln.split()[col] for ln in
                    p.stdout.decode(errors="replace").splitlines()
                    if len(ln.split()) > col]
        except (subprocess.TimeoutExpired, OSError):
            return None
    sinks = rows(["sinks"], 1)
    sources = rows(["sources"], 1)
    return {"sink_listed": (NS in sinks) if sinks is not None else None,
            "monitor_listed": ((NS + ".monitor") in sources)
            if sources is not None else None,
            "module_index": ma._pactlmon_r85_module_index("sink_name", NS)}


def dump_probe():
    try:
        g = ma._pactlmon_r85_graph()
        node = ma._pactlmon_r85_node(g, NS)
        nid = (node or {}).get("node_id")
        mon = [p.get("name") for p in (g.get("ports") or {}).values()
               if str(p.get("node_id")) == str(nid)
               and "monitor" in (p.get("name") or "")]
        return {"present": bool(node), "state": (node or {}).get("state"),
                "monitor_ports": len(mon)}
    except Exception as exc:
        return {"exc": repr(exc)[:160]}


def leg2(name, argv, ctx, **kw):
    pre = {"pactl": pactl_probe(), "dump": dump_probe()}
    rec = orig_leg(name, argv, ctx, **kw)
    events.append({"leg": name, "pre": pre, "post": dump_probe(),
                   "killed": rec.get("killed"),
                   "out_bytes": (rec.get("out") or {}).get("bytes"),
                   "first_states": [nd.get("state") for s in
                                    (rec.get("samples") or [])
                                    for nd in (s.get("nodes") or [])][:2],
                   "fired": [(f.get("kind"), f.get("at"),
                              (f.get("result") or {}).get("verified_index"))
                             for f in rec.get("fired") or []]})
    return rec


ma._gstfrz_r91_leg = leg2

out = {"entries": {}}
for fn in ("gstfrz_prop_r91_entry", "gstfrz_clock_r91_entry",
           "gstfrz_resume_r91_entry", "gstfrz_srcloss_r91_entry",
           "gstfrz_connect_r91_entry"):
    e = getattr(ma, fn)()
    out["entries"][fn] = {
        "failures": e.get("failures"),
        "coverage_blocked": e.get("coverage_blocked"),
        "unloads": {k: (v or {}).get("verified_index")
                    for k, v in (e.get("unloads") or {}).items()},
        "sinks_gone": e.get("sinks_gone"),
        "own_nodes_after": e.get("own_nodes_after")}
out["events"] = events
Path(sys.argv[1]).write_text(json.dumps(out, indent=1, default=str) + "\n")
print(json.dumps({k: v["failures"] for k, v in out["entries"].items()}))
