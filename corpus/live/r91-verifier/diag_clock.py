#!/usr/bin/env python3
"""r91 VERIFIER — targeted diagnostic for the c_alive red (run 1).

Runs the committed clock entry from the frozen tree and records, for every
sample, the TARGET sink's pactl liveness (cheap), plus a pw-dump node probe
at each leg's start and end. Nothing here edits the tree.

Usage: diag_clock.py <out.json>
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
orig_sample = ma._gstfrz_r91_sample
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
    mods = rows(["modules"], 0)
    return {"sink_listed": (NS in sinks) if sinks is not None else None,
            "monitor_listed": ((NS + ".monitor") in sources)
            if sources is not None else None,
            "module_index": ma._pactlmon_r85_module_index("sink_name", NS),
            "n_modules": len(mods) if mods is not None else None}


def dump_probe():
    try:
        g = ma._pactlmon_r85_graph()
        node = ma._pactlmon_r85_node(g, NS)
        nid = (node or {}).get("node_id")
        mon = sorted((p.get("name") or "") for p in
                     (g.get("ports") or {}).values()
                     if str(p.get("node_id")) == str(nid)
                     and "monitor" in (p.get("name") or ""))
        return {"present": bool(node), "state": (node or {}).get("state"),
                "monitor_ports": mon}
    except Exception as exc:
        return {"exc": repr(exc)[:160]}


def sample2(proc, out_path, el):
    s = orig_sample(proc, out_path, el)
    s["target"] = pactl_probe()
    return s


def leg2(name, argv, ctx, **kw):
    pre = {"pactl": pactl_probe(), "dump": dump_probe()}
    rec = orig_leg(name, argv, ctx, **kw)
    events.append({"leg": name, "pre": pre, "post_dump": dump_probe(),
                   "killed": rec.get("killed"),
                   "out_bytes": (rec.get("out") or {}).get("bytes"),
                   "fired": [(f.get("kind"), f.get("at"),
                              (f.get("result") or {}).get("verified_index"))
                             for f in rec.get("fired") or []]})
    return rec


ma._gstfrz_r91_sample = sample2
ma._gstfrz_r91_leg = leg2

entry = ma.gstfrz_clock_r91_entry()

out = {"failures": entry.get("failures"),
       "unloads": entry.get("unloads"),
       "legs": {tag: {"killed": l.get("killed"),
                      "out": (l.get("out") or {}).get("bytes"),
                      "timeline": [
                          {"t": s.get("t"), "size": s.get("size"),
                           "ours": [n.get("state")
                                    for n in (s.get("nodes") or [])],
                           "target": s.get("target")}
                          for s in l.get("samples") or []]}
                for tag, l in (entry.get("legs") or {}).items()},
       "events": events}
Path(sys.argv[1]).write_text(json.dumps(out, indent=1, default=str) + "\n")
print(json.dumps({"failures": out["failures"]}, indent=1))
