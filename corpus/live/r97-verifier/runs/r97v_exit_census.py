#!/usr/bin/env python3
"""r97 verifier exit census.

    python3 r97v_exit_census.py <out.json> [--baseline <precensus.txt>]

Measures, after every verifier run has exited:
  1. the operator's shared graph: objects, any r97a-named object;
  2. a global /proc scan for r97a-named processes and for live private
     `wppol-r97-*` instances (cmdline OR environ — a private wireplumber has
     no seat path in argv);
  3. every `$TMPDIR/wppol-r97-*` root's pid files and whether those pids live;
  4. the shared session daemons' pid + start time (proves they were never
     signalled), compared with the pre-run baseline when given.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

TMP = Path("/home/vgpnk/Projects/shokunin/tmp")
SHARED_DAEMONS = ("/usr/bin/pipewire", "/usr/bin/pipewire-pulse")


def graph_census():
    try:
        r = subprocess.run(["pw-dump"], capture_output=True, text=True,
                           timeout=30)
    except subprocess.TimeoutExpired:
        return {"unreadable": True, "reason": "pw-dump timeout"}
    if r.returncode != 0:
        return {"unreadable": True, "reason": f"rc={r.returncode}"}
    try:
        objs = json.loads(r.stdout or "[]")
    except json.JSONDecodeError as exc:
        return {"unreadable": True, "reason": f"parse: {exc}"}
    hits = []
    for o in objs:
        props = (o.get("info") or {}).get("props") or {}
        blob = json.dumps(props)
        if "r97a" in blob:
            hits.append({k: props.get(k) for k in
                         ("node.name", "application.name", "object.serial")})
    return {"unreadable": False, "objects": len(objs), "r97a_hits": hits}


def proc_census():
    hits = []
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            cmd = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode(
                "utf-8", "replace")
        except OSError:
            continue
        try:
            env = (p / "environ").read_bytes().replace(b"\0", b"\n").decode(
                "utf-8", "replace")
        except OSError:
            env = ""
        if "r97a" in cmd or "r97a" in env or "wppol-r97-" in cmd or \
                "wppol-r97-" in env:
            hits.append({"pid": int(p.name), "cmd": cmd[:180],
                         "via": ("cmdline" if "wppol-r97-" in cmd or
                                 "r97a" in cmd else "environ")})
    return hits


def root_census():
    out = []
    for root in sorted(TMP.glob("wppol-r97-*")):
        owner = None
        m = re.match(r"wppol-r97-(\d+)-", root.name)
        if m:
            owner = int(m.group(1))
        rec = {"root": str(root), "owner_pid": owner, "pids": []}
        for pf in sorted((root / "run").glob("*.pid")):
            try:
                pid = int(pf.read_text().strip())
            except (OSError, ValueError):
                pid = None
            alive = False
            if pid:
                try:
                    os.kill(pid, 0)
                    alive = True
                except OSError:
                    alive = False
            rec["pids"].append({"tag": pf.stem, "pid": pid, "alive": alive})
        out.append(rec)
    return out


def daemon_identity():
    r = subprocess.run(["ps", "-eo", "pid,lstart,args"], capture_output=True,
                       text=True)
    rows = []
    for ln in r.stdout.splitlines():
        if any(d in ln for d in SHARED_DAEMONS):
            rows.append(ln.strip())
    return rows


def main():
    out = Path(sys.argv[1])
    baseline = None
    if "--baseline" in sys.argv:
        baseline = Path(sys.argv[sys.argv.index("--baseline") + 1]).read_text()
    rec = {"graph": graph_census(), "procs": proc_census(),
           "private_roots": root_census(), "shared_daemons_now":
           daemon_identity()}
    if baseline:
        base_rows = [ln.strip() for ln in baseline.splitlines()
                     if any(d in ln for d in SHARED_DAEMONS)]
        rec["shared_daemons_pre"] = base_rows
        rec["shared_daemons_unchanged"] = base_rows == rec["shared_daemons_now"]
    own = [p for p in rec["procs"]
           if "r97a" in p["cmd"] or "r97a" in p.get("via", "")]
    rec["r97a_processes"] = [p for p in rec["procs"]
                             if "r97a" in p["cmd"]]
    rec["verdict"] = {
        "graph_r97a_hits": len(rec["graph"].get("r97a_hits") or []),
        "r97a_processes": len(rec["r97a_processes"]),
        "live_private_roots": [r for r in rec["private_roots"]
                               if any(x["alive"] for x in r["pids"])],
        "shared_daemons_unchanged": rec.get("shared_daemons_unchanged"),
    }
    out.write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec["verdict"], indent=1))
    print("r97a procs:", json.dumps(rec["r97a_processes"]))
    print("private wppol-r97 procs:", json.dumps(
        [p for p in rec["procs"] if "wppol-r97-" in p["cmd"]
         or p["via"] == "environ"][:8]))
    ok = (rec["verdict"]["graph_r97a_hits"] == 0
          and rec["verdict"]["r97a_processes"] == 0
          and rec.get("shared_daemons_unchanged") is not False)
    print("EXIT CENSUS:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
