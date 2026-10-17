#!/usr/bin/env python3
"""r88 scout analysis (fixed) — witness diff over receipts from r88_scout.py
and r88_addendum.py. Pure read of raw/; writes receipts/analysis.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
REC = ROOT / "receipts"

main_legs = json.loads((REC / "r88-legs.json").read_text())
add_legs = json.loads((REC / "r88-addendum.json").read_text())
by_name = {l["leg"]: l for l in main_legs["legs"] + add_legs["legs"]}

analysis: dict = {"stability": {}, "objects": {}, "set_rule": {}, "pwt": {},
                  "pactl_map": {}, "bluez_endpoints": {}, "refusals": {}}

for name, l in by_name.items():
    analysis["stability"][name] = {
        "reps": l["reps"], "stable_stdout": l["stable_stdout"], "rcs": l["rcs"]}

# ---------- helpers ----------
SPA_ID_TO_NAME = {1: "PropInfo", 2: "Props", 3: "EnumFormat", 4: "Format",
                  5: "Buffers", 6: "Meta", 7: "IO", 8: "Profile",
                  9: "EnumProfile", 10: "PortConfig", 11: "Route",
                  12: "EnumRoute", 13: "Latency", 14: "ProcessLatency",
                  15: "Latency", 16: "Tag", 17: "Tag"}


def load_census(path: Path) -> dict:
    d = json.loads(path.read_text())
    return {o["id"]: o for o in d}


CENSUS = load_census(RAW / "pw-dump-census.1.json")


def parse_cli_info(text: str) -> dict:
    props, params, scalars = {}, {}, {}
    section = None
    for line in text.splitlines():
        s = line.strip().lstrip("*").strip()
        if s == "properties:":
            section = "props"; continue
        if s.startswith("params:"):
            section = "params"
            m = re.search(r"params:\s*\((\d+)\)", s)
            if m:
                scalars["param_count"] = int(m.group(1))
            continue
        if section == "props" and " = " in s:
            k, v = s.split(" = ", 1)
            props[k.strip()] = v.strip()
        elif section == "params":
            m = re.match(r"(\d+) \((Spa:Enum:ParamId:\w+)\) (\S+)", s)
            if m:
                params[int(m.group(1))] = {"name": m.group(2), "access": m.group(3)}
        elif ":" in s and " = " not in s:
            k, _, v = s.partition(":")
            scalars[k.strip()] = v.strip()
    return {"props": props, "params": params, "scalars": scalars}


def prop_diff(dump_props: dict, cli_props: dict) -> dict:
    only_dump = sorted(set(dump_props) - set(cli_props))
    only_cli = sorted(set(cli_props) - set(dump_props))
    type_diff = []
    for k in sorted(set(dump_props) & set(cli_props)):
        dv, cv = dump_props[k], cli_props[k]
        cs = cv.strip('"')
        if isinstance(dv, bool):
            if cs not in ("true", "false"):
                type_diff.append({"key": k, "dump": dv, "cli": cv, "kind": "bool_vs_str"})
        elif isinstance(dv, (int, float)):
            if not re.fullmatch(r"-?\d+(\.\d+)?", cs):
                type_diff.append({"key": k, "dump": dv, "cli": cv, "kind": "num_vs_str"})
        elif isinstance(dv, str) and cs != dv:
            type_diff.append({"key": k, "dump": dv, "cli": cv, "kind": "value_mismatch"})
    return {"only_dump": only_dump, "only_cli": only_cli,
            "shared": len(set(dump_props) & set(cli_props)),
            "type_or_value_diffs": type_diff}


# ---------- 1. per-object witness diff (dump from full census, cli from leg) ----------
for oid in (35, 46, 133):
    obj = CENSUS[oid]
    dump_props = obj["info"].get("props", {})
    dump_params = obj["info"].get("params") or {}
    cli = parse_cli_info((RAW / f"pw-cli-info-{oid}.1.txt").read_text())
    cli_params = cli["params"]
    dump_param_names = set(dump_params)
    cli_param_names = {v["name"] for v in cli_params.values()}
    analysis["objects"][str(oid)] = {
        "identity": {
            "name": dump_props.get("node.name"), "class": dump_props.get("media.class"),
            "factory": dump_props.get("factory.name"),
        },
        "dump_top_keys": sorted(obj.keys()),
        "dump_info_keys": sorted(obj["info"].keys()),
        "dump_prop_count": len(dump_props),
        "cli_prop_count": len(cli["props"]),
        "prop_diff": prop_diff(dump_props, cli["props"]),
        "dump_param_names": sorted(dump_param_names),
        "cli_param_names": sorted(cli_param_names),
        "cli_param_ids": {str(k): v["name"] for k, v in sorted(cli_params.items())},
        "cli_param_access": {v["name"]: v["access"] for v in cli_params.values()},
        "params_only_dump": sorted(dump_param_names - cli_param_names),
        "params_only_cli": sorted(cli_param_names - dump_param_names),
        "dump_state": obj["info"].get("state"),
        "cli_state": cli["scalars"].get("state", "").strip('"'),
        "cli_scalars": cli["scalars"],
        "dump_perm": obj.get("permissions"),
        "dump_version": obj.get("version"),
        "dump_props_param_value": (dump_params.get("Props") or [{}])[0].get("props") if dump_params.get("Props") else None,
        "leg_rcs": {n: by_name[n]["rcs"][0] for n in
                    (f"pw-cli-props-{oid}", f"pw-cli-format-{oid}", f"pw-cli-propinfo-{oid}")},
    }

# ---------- 2. pw-dump <N> set rule: id==N or serial==N ----------
serial_of = {i: (o.get("info") or {}).get("props", {}).get("object.serial") for i, o in CENSUS.items()}


def dump_ids(path: Path):
    try:
        d = json.loads(path.read_text())
        return [o["id"] for o in d]
    except json.JSONDecodeError:
        return []


for key in (32, 33, 35, 45, 46, 60, 133, 99999):
    f = RAW / f"add-dump-{key}.1.json" if key != 99999 else RAW / "refuse-pwdump-99999.1.json"
    if not f.exists():
        f = RAW / f"pw-dump-{key}.1.json"
    actual = dump_ids(f)
    expected = sorted(i for i, o in CENSUS.items()
                      if i == key or serial_of.get(i) == key)
    analysis["set_rule"][str(key)] = {
        "expected_id_or_serial": expected,
        "actual_ids": actual,
        "rule_holds": actual == expected,
        "matched_by_serial_only": sorted(set(expected) - {key}),
        "output_empty": len(actual) == 0,
    }

# ---------- 3. pw-top analysis ----------
def parse_pwtop(text: str):
    refreshes, cur = [], []
    for line in text.splitlines():
        if line.startswith("S   ID"):
            if cur:
                refreshes.append(cur)
            cur = []
            continue
        m = re.match(r"^(\S)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(.+?)\s+(\S+)\s*$", line)
        if m:
            cur.append({"state": m.group(1), "id": int(m.group(2)), "quant": int(m.group(3)),
                        "rate": int(m.group(4)), "err": int(m.group(9)),
                        "format": m.group(10).strip(), "name": m.group(11)})
    if cur:
        refreshes.append(cur)
    return refreshes


ptop_report = {}
for leg, path in [("n1", RAW / "pw-top-n1.1.txt"), ("n2", RAW / "add-pwtop-n2.1.txt"),
                  ("n3", RAW / "add-pwtop-n3.1.txt")]:
    refreshes = parse_pwtop(path.read_text())
    ptop_report[leg] = {
        "refresh_count": len(refreshes),
        "rows_per_refresh": [len(r) for r in refreshes],
        "state_chars_per_refresh": [sorted({row["state"] for row in r}) for r in refreshes],
        "names_refresh1": [row["name"] for row in refreshes[0]] if refreshes else [],
        "last_refresh_states": {str(row["id"]): row["state"] for row in refreshes[-1]} if refreshes else {},
    }
# instability across n2 reps: which names differ
rep_names = []
for i in (1, 2, 3):
    rs = parse_pwtop((RAW / f"add-pwtop-n2.{i}.txt").read_text())
    rep_names.append({row["name"] for row in rs[-1]})
analysis["pwt"] = {
    "report": ptop_report,
    "n2_last_refresh_name_sets_identical": len(set(frozenset(s) for s in rep_names)) == 1,
    "n2_last_refresh_symdiff": [sorted(rep_names[0] ^ rep_names[1]), sorted(rep_names[1] ^ rep_names[2])],
    "census_nodes": {str(i): {"name": (o.get("info") or {}).get("props", {}).get("node.name"),
                              "state": (o.get("info") or {}).get("state")} for i, o in sorted(CENSUS.items())
                     if o["type"] == "PipeWire:Interface:Node"},
    "dump_state_vs_ptop_last": [
        {"id": i, "dump_state": (CENSUS[i].get("info") or {}).get("state"), "ptop_char": ptop_report["n2"]["last_refresh_states"].get(str(i))}
        for i in sorted(CENSUS) if CENSUS[i]["type"] == "PipeWire:Interface:Node"
    ],
}
man = (RAW / "add-pwtop-man.1.txt").read_text()
legend = []
grab = False
for line in man.splitlines():
    if line.strip().startswith("S") and "Node status" in line:
        grab = True
    if grab:
        legend.append(line.strip())
        if len(legend) > 12:
            break
analysis["pwt"]["state_legend_manpage"] = [l for l in legend if l]

# ---------- 4. pactl index vs native id ----------
sinks = []
for line in (RAW / "pactl-sinks.1.txt").read_text().splitlines():
    f = line.split("\t")
    if len(f) >= 2:
        sinks.append({"pactl_index": int(f[0]), "name": f[1], "state": f[-1]})
mapping = []
for s in sinks:
    native = next((i for i, o in CENSUS.items() if (o.get("info") or {}).get("props", {}).get("node.name") == s["name"]), None)
    serial = serial_of.get(native) if native else None
    mapping.append({**s, "native_node_id": native, "native_serial": serial})
analysis["pactl_map"] = {"sinks": mapping,
                         "index_eq_native_all": all(m["pactl_index"] == m["native_node_id"] for m in mapping),
                         "index_eq_serial_any": any(m["pactl_index"] == m["native_serial"] for m in mapping)}

# ---------- 5. bluez endpoint surface ----------
log = (RAW / "bluez-endpoint-log.1.txt").read_text()
reg = sorted(set(re.findall(r"Endpoint registered: sender=:1\.75450 path=(\S+)", log)))
analysis["bluez_endpoints"] = {
    "registered_paths_current_wireplumber": reg,
    "count": len(reg),
    "codecs_seen": sorted({p.rsplit("/", 1)[1] for p in reg}),
    "a2dp_endpoints": sorted(p for p in reg if "A2DP" in p),
    "hfp_hsp_endpoints": sorted(p for p in reg if "HFP" in p or "HSP" in p),
    "sbc_endpoints": sorted(p for p in reg if "sbc" in p),
}

# ---------- 6. refusals ----------
for name in sorted(n for n in by_name if n.startswith("refuse-")):
    l = by_name[name]
    err = (RAW / f"{name}.1.err").read_text().strip()
    out = (RAW / f"{name}.1.txt").read_text().strip() if (RAW / f"{name}.1.txt").exists() else ""
    if not out and (RAW / f"{name}.1.json").exists():
        out = (RAW / f"{name}.1.json").read_text().strip()
    analysis["refusals"][name] = {"rcs": l["rcs"], "stable": l["stable_stdout"],
                                  "stderr": err, "stdout": out}

# ---------- 7. bluez device record ----------
dev = {}
txt = (RAW / "bluez-device-props.1.txt").read_text()
for m in re.finditer(r"^\.(\w+)\s+property\s+(\S+)\s+(.*?)\s*$", txt, re.M):
    dev[m.group(1)] = m.group(3).strip()
analysis["bluez_device_record"] = dev

(REC / "analysis.json").write_text(json.dumps(analysis, indent=1))

# ---------- console summary ----------
print("=== set rule ===")
for k, v in analysis["set_rule"].items():
    print(f"  key {k}: expected {v['expected_id_or_serial']} actual {v['actual_ids']} holds={v['rule_holds']}")
print("=== prop diff ===")
for oid, v in analysis["objects"].items():
    print(f"  obj {oid} ({v['identity']['name']}): dump={v['dump_prop_count']} cli={v['cli_prop_count']} "
          f"only_dump={v['prop_diff']['only_dump']} only_cli={v['prop_diff']['only_cli']} "
          f"typediffs={len(v['prop_diff']['type_or_value_diffs'])}")
    print(f"    params only_dump={v['params_only_dump']} only_cli={v['params_only_cli']}")
print("=== pw-top ===")
for leg, r in ptop_report.items():
    print(f"  {leg}: refreshes={r['refresh_count']} rows={r['rows_per_refresh']} states={r['state_chars_per_refresh']}")
print("  n2 name sets identical:", analysis["pwt"]["n2_last_refresh_name_sets_identical"])
print("  n2 symdiff:", analysis["pwt"]["n2_last_refresh_symdiff"])
print("=== pactl map ===")
for m in mapping:
    print(f"  pulse {m['pactl_index']} <-> native {m['native_node_id']} (serial {m['native_serial']}) {m['name']}")
print("=== endpoints ===")
print(f"  {analysis['bluez_endpoints']['count']} endpoints, codecs: {analysis['bluez_endpoints']['codecs_seen']}")
print("=== refusals ===")
for k, v in analysis["refusals"].items():
    print(f"  {k}: rcs={v['rcs']} stderr={v['stderr'][:70]!r} stdout={v['stdout'][:70]!r}")
