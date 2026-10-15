#!/usr/bin/env python3
"""r88b follow-up: corrected pw-cli ls/info-all counts, serial resolution, param-name matrix.

Fixes a self-artifact in the first modes battery: `grep -c '^\tid '` inside single quotes
matches a literal backslash-t, not a tab, so every ls count came back 0. Counting is now
done in Python over the real output.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r88b_probe import RAW, REC, run, utc, parse_pwdump_keys  # noqa: E402

IFACES = ["Node", "Device", "Client", "Port", "Link", "Factory", "Metadata", "Module",
          "Core", "Profiler", "SecurityContext", "ClientEndpoint", "Session", "Endpoint"]
PARAMS = ["Format", "EnumFormat", "Props", "PropInfo", "IO", "Buffers", "Meta", "Latency",
          "ProcessLatency", "Tag", "Route", "Profiles", "EnumProfile", "Profile", "BogusXYZ", "4"]


def main():
    d = run(["pw-dump"], timeout=90)
    (RAW / "fix-census.json").write_text(d["stdout"])
    objs = json.loads(d["stdout"])
    by_id, sers, keys, pred = parse_pwdump_keys(objs)
    ids_by_type = {}
    for o in objs:
        ids_by_type.setdefault(o.get("type", "").split(":")[-1], set()).add(o["id"])
    dump_all = set(by_id)

    legs = []

    def add(name, argv, reps=1, timeout=60):
        rows = []
        for i in range(1, reps + 1):
            r = run(argv, timeout=timeout)
            rows.append(r)
            (RAW / f"{name}.{i}.txt").write_text(r["stdout"])
            (RAW / f"{name}.{i}.err").write_text(r["stderr"])
        legs.append({"leg": name, "argv": argv, "rcs": [r["rc"] for r in rows],
                     "wall_ms": [r["wall_ms"] for r in rows],
                     "rows": [{k: v for k, v in r.items() if k not in ("stdout", "stderr")} for r in rows]})
        return rows

    # 1. ls <iface> counts, parsed in Python (tab-safe)
    ls = {}
    for iface in IFACES:
        rows = add(f"fix-ls-{iface}", ["pw-cli", "ls", iface])
        out = rows[0]["stdout"]
        got = sorted(int(m.group(1)) for m in re.finditer(r"^\tid (\d+),", out, re.M))
        ls[iface] = {"n": len(got), "ids": got, "rc": rows[0]["rc"],
                     "expected_n": len(ids_by_type.get(iface, set())),
                     "missing": sorted(ids_by_type.get(iface, set()) - set(got)),
                     "extra": sorted(set(got) - ids_by_type.get(iface, set()))}
    # 2. info all
    rows = add("fix-info-all", ["pw-cli", "info", "all"])
    all_out = rows[0]["stdout"]
    all_ids = sorted(int(m.group(1)) for m in re.finditer(r"^\tid: (\d+)", all_out, re.M))
    info_all = {"n": len(all_ids), "rc": rows[0]["rc"], "missing_vs_dump": sorted(dump_all - set(all_ids)),
                "extra_vs_dump": sorted(set(all_ids) - dump_all), "has_core": 0 in all_ids}
    # 3. serial resolution through ls (serial-only key)
    serial_only = sorted(k for k in keys if k not in by_id and k in sers)
    sk = serial_only[0] if serial_only else None
    serial_probe = None
    if sk is not None:
        rows = add("fix-ls-node-serial", ["pw-cli", "ls", "Node"])
        txt = rows[0]["stdout"]
        serial_probe = {"key": sk, "object": sers[sk],
                        "ls_contains_serial": f'object.serial = "{sk}"' in txt,
                        "ls_contains_obj_id": bool(re.search(rf"^\tid {sers[sk][0]},", txt, re.M))}
    # 4. param-name matrix on several object classes
    node_with_params = next((o["id"] for o in objs if o.get("type", "").endswith("Node")
                             and o.get("info", {}).get("params")), None)
    device = next((o["id"] for o in objs if o.get("type", "").endswith("Device")), None)
    client = next((o["id"] for o in objs if o.get("type", "").endswith("Client")), None)
    port = next((o["id"] for o in objs if o.get("type", "").endswith("Port")), None)
    matrix = []
    for tag, oid in (("node-params", node_with_params), ("device", device),
                     ("client", client), ("port", port)):
        if oid is None:
            continue
        for p in PARAMS:
            r = run(["pw-cli", "enum-params", str(oid), p], timeout=30)
            matrix.append({"class": tag, "id": oid, "param": p, "rc": r["rc"],
                           "out_len": r["stdout_len"], "out_head": r["stdout"][:60],
                           "err": r["stderr"].strip()[:150], "wall_ms": r["wall_ms"]})
    # 5. pw-dump param names present per class (for the "key presence != value" law)
    params_by_class = {}
    for o in objs:
        t = o.get("type", "").split(":")[-1]
        names = sorted(o.get("info", {}).get("params", {}).keys())
        if names:
            params_by_class.setdefault(t, {})[str(o["id"])] = names
    out = {"battery": "fix", "generated_utc": utc(), "n_objects": len(objs),
           "picked": {"serial_only_key": sk, "node_with_params": node_with_params,
                      "device": device, "client": client, "port": port},
           "ls": ls, "info_all": info_all, "serial_probe": serial_probe,
           "param_matrix": matrix, "dump_params_by_class": params_by_class,
           "legs": legs}
    (REC / "B8-fix.json").write_text(json.dumps(out, indent=1))
    print("fix: ls-node", ls["Node"]["n"], "expected", ls["Node"]["expected_n"],
          "| info-all", info_all["n"], "vs dump", len(dump_all),
          "| serial probe", serial_probe)
    print("param matrix rows:", len(matrix))


if __name__ == "__main__":
    main()
