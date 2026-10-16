#!/usr/bin/env python3
"""r85-critic bounded READ-ONLY live corroboration of the encoded
addressing law (the labrat seat had no exec tool — dispatcher fallback).

READ VERBS ONLY: pw-dump, pactl get-*, pactl list, pw-cli info.
No module load/unload, no stream/pw-play/pw-record, no set-*/move-*.
Writes only under corpus/live/r85-critic/live-readonly/.
"""
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r85-critic/live-readonly")
OUT.mkdir(parents=True, exist_ok=True)
log = []


def run(argv, timeout=20):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        rec = {"argv": " ".join(argv), "exit": p.returncode,
               "stdout": p.stdout.decode(errors="replace")[:2000],
               "stderr": p.stderr.decode(errors="replace")[:800]}
    except Exception as exc:  # noqa: BLE001
        rec = {"argv": " ".join(argv), "error": f"{type(exc).__name__}: {exc}"}
    log.append(rec)
    return rec


def dump():
    p = subprocess.run(["pw-dump"], capture_output=True, timeout=30)
    return json.loads(p.stdout or b"[]")


d = dump()
def_sink = run(["pactl", "get-default-sink"])["stdout"].strip()
def_src = run(["pactl", "get-default-source"])["stdout"].strip()

sink_leaf = src_leaf = None
for o in d:
    if not str(o.get("type", "")).endswith("Node"):
        continue
    props = (o.get("info") or {}).get("props") or {}
    if props.get("node.name") == def_sink:
        sink_leaf = {"global_id": o.get("id"),
                     "object.serial": props.get("object.serial"),
                     "object.id_prop": props.get("object.id"),
                     "node.name": props.get("node.name")}
    if props.get("node.name") == def_src:
        src_leaf = {"global_id": o.get("id"),
                    "object.serial": props.get("object.serial"),
                    "object.id_prop": props.get("object.id"),
                    "node.name": props.get("node.name")}

res = {"default_sink": def_sink, "default_source": def_src,
       "sink_leaf": sink_leaf, "source_leaf": src_leaf}

if sink_leaf:
    ser = str(sink_leaf["object.serial"])
    oid = str(sink_leaf["object.id_prop"] if sink_leaf["object.id_prop"]
              is not None else sink_leaf["global_id"])
    res["pactl_get_sink_volume_by_serial"] = run(["pactl", "get-sink-volume", ser])
    res["pactl_get_sink_volume_by_object_id"] = run(["pactl", "get-sink-volume", oid])
    res["pactl_get_sink_volume_by_name"] = run(["pactl", "get-sink-volume", def_sink])
    res["pactl_get_sink_volume_by_global_id"] = run(["pactl", "get-sink-volume", str(sink_leaf["global_id"])])
    res["pwcli_info_by_object_id"] = run(["pw-cli", "info", oid])
    res["pwcli_info_by_serial"] = run(["pw-cli", "info", ser])
    short = run(["pactl", "list", "sinks", "short"])
    res["pactl_list_sinks_short_default_line"] = next(
        (ln for ln in short["stdout"].splitlines() if def_sink in ln), None)
    full = run(["pactl", "list", "sinks"])
    blk = []
    keep = False
    for ln in full["stdout"].splitlines():
        if ln.startswith("Sink #"):
            keep = False
        if def_sink in ln:
            keep = True
        if keep:
            blk.append(ln)
        if keep and ln.strip().startswith("Volume:"):
            break
    res["pactl_list_sinks_default_block"] = blk

if src_leaf:
    sser = str(src_leaf["object.serial"])
    res["pactl_get_source_volume_by_name"] = run(["pactl", "get-source-volume", def_src])
    res["pactl_get_source_volume_by_serial"] = run(["pactl", "get-source-volume", sser])
res["pactl_get_source_volume_by_sink_name"] = run(["pactl", "get-source-volume", def_sink])
res["pactl_get_source_volume_by_sink_serial"] = run(
    ["pactl", "get-source-volume", str(sink_leaf["object.serial"])] if sink_leaf else ["true"])

(OUT / "probe.json").write_text(json.dumps(res, indent=2, default=str) + "\n")
(OUT / "raw-log.json").write_text(json.dumps(log, indent=2, default=str) + "\n")

# verdict per step
v = {}
v["serial_resolves"] = res["pactl_get_sink_volume_by_serial"]["exit"] == 0
v["object_id_refused"] = (res["pactl_get_sink_volume_by_object_id"]["exit"] == 1
                          and "No such entity" in res["pactl_get_sink_volume_by_object_id"]["stderr"])
v["global_id_refused"] = (res["pactl_get_sink_volume_by_global_id"]["exit"] == 1
                          and "No such entity" in res["pactl_get_sink_volume_by_global_id"]["stderr"])
v["name_resolves_same_row"] = (
    res["pactl_get_sink_volume_by_name"]["exit"] == 0 and
    res["pactl_get_sink_volume_by_name"]["stdout"].splitlines()[:1] ==
    res["pactl_get_sink_volume_by_serial"]["stdout"].splitlines()[:1])
v["pwcli_id_resolves"] = (res["pwcli_info_by_object_id"]["exit"] == 0
                          and "unknown global" not in res["pwcli_info_by_object_id"]["stderr"])
v["pwcli_serial_lie"] = (res["pwcli_info_by_serial"]["exit"] == 0
                         and "unknown global" in res["pwcli_info_by_serial"]["stderr"])
line = res.get("pactl_list_sinks_short_default_line") or ""
idx_field = line.split("\t")[0].strip() if line else None
v["short_index_field"] = idx_field
v["short_index_equals_serial"] = (
    sink_leaf is not None and idx_field is not None and
    str(sink_leaf["object.serial"]) == idx_field)
v["source_name_and_serial_resolve"] = (
    res.get("pactl_get_source_volume_by_name", {}).get("exit") == 0 and
    res.get("pactl_get_source_volume_by_serial", {}).get("exit") == 0)
v["source_verb_refuses_sink_arg"] = (
    res["pactl_get_source_volume_by_sink_name"]["exit"] == 1 and
    "No such entity" in res["pactl_get_source_volume_by_sink_name"]["stderr"])
res["verdict_steps"] = v
res["verdict"] = "supported" if all(
    v[k] for k in ("serial_resolves", "object_id_refused", "global_id_refused",
                   "name_resolves_same_row", "pwcli_id_resolves", "pwcli_serial_lie",
                   "short_index_equals_serial", "source_name_and_serial_resolve",
                   "source_verb_refuses_sink_arg")) else "falsified/partial"
(OUT / "verdict.json").write_text(json.dumps({"verdict": res["verdict"],
                                              "steps": v}, indent=2, default=str) + "\n")
print(json.dumps({"verdict": res["verdict"], "steps": v,
                  "sink_leaf": sink_leaf, "source_leaf": src_leaf}, indent=2, default=str))
