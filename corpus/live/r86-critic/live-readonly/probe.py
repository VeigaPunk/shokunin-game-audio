#!/usr/bin/env python3
"""r86-critic live read-only corroboration (read verbs only).

No host mutation: no links, no metadata writes, no module loads, no
set-default-*, no signals to foreign processes. Every spawn is bounded.
Writes only corpus/live/r86-critic/live-readonly.json.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = REPO / "corpus/live/r86-critic/live-readonly.json"
res = {}


def run(argv, timeout=15.0, env=None):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout,
                           env=env)
        return {"argv": " ".join(argv), "rc": p.returncode,
                "out": p.stdout.decode(errors="replace"),
                "err": p.stderr.decode(errors="replace")}
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"argv": " ".join(argv), "error": type(exc).__name__}


# ---- 1. resolve the default sink node (read-only) -----------------------
dump = run(["pw-dump"], timeout=25.0)
objects = json.loads(dump["out"] or "[]")
nodes = [o for o in objects if str(o.get("type", "")).endswith("Node")]
sinks = [o for o in nodes if (o.get("info") or {}).get("props", {})
         .get("media.class") == "Audio/Sink"]
default_name = run(["pactl", "get-default-sink"])["out"].strip()
target = next((o for o in sinks
               if (o["info"]["props"].get("node.name") or "")
               == default_name), None)
res["host"] = {"default_sink": default_name,
               "loadavg": Path("/proc/loadavg").read_text().strip(),
               "dump_objects": len(objects),
               "live_r86a_objects": sum(
                   1 for o in objects
                   if "r86a" in json.dumps(o.get("info", {})))}
if target is None:
    res["verdict"] = "no default sink node resolved"
    OUT.write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps(res, indent=2)[:800])
    raise SystemExit(1)
nid = target["id"]
ser = str(target["info"]["props"].get("object.serial"))
res["subject"] = {"node_name": target["info"]["props"].get("node.name"),
                  "object.id": nid, "object.serial": ser}

# ---- 2. the addressing split -------------------------------------------
res["ls_serial"] = run(["pw-cli", "ls", ser])
res["ls_id"] = run(["pw-cli", "ls", str(nid)])
res["info_id"] = run(["pw-cli", "info", str(nid)])
res["info_serial"] = run(["pw-cli", "info", ser])
res["enum_serial"] = run(["pw-cli", "enum-params", ser, "Props"])
for k in ("ls_serial", "ls_id", "info_id", "info_serial", "enum_serial"):
    r = res[k]
    r["out_bytes"] = len(r.get("out", ""))
    r["out"] = r.get("out", "")[:400]
    r["err"] = r.get("err", "")[:300]

# ---- 3. pw-dump <id> vs <serial>: FULL-byte equality --------------------
d_id = run(["pw-dump", str(nid)], timeout=25.0)
d_ser = run(["pw-dump", ser], timeout=25.0)
res["dump_id_vs_serial"] = {
    "rc_id": d_id.get("rc"), "rc_serial": d_ser.get("rc"),
    "bytes_id": len(d_id.get("out", "")),
    "bytes_serial": len(d_ser.get("out", "")),
    "sha256_id": hashlib.sha256(d_id.get("out", "").encode()).hexdigest(),
    "sha256_serial": hashlib.sha256(
        d_ser.get("out", "").encode()).hexdigest(),
    "full_byte_equal": d_id.get("out") == d_ser.get("out")}

# ---- 4. metadata census gap (three surfaces) ---------------------------
ml = run(["pw-metadata", "-l"])
store_ids = sorted(int(m.group(2)) for m in re.finditer(
    r'Found "([^"]+)" metadata (\d+)', ml.get("out", "")))
ls = run(["pw-cli", "ls", "Metadata"])
ls_ids = sorted(int(m.group(1)) for m in re.finditer(
    r"\bid (\d+),\s*type PipeWire:Interface:Metadata", ls.get("out", "")))
dump_ids = sorted(o["id"] for o in objects
                  if str(o.get("type", "")).endswith("Metadata"))
res["meta_census"] = {"pw_metadata_l": store_ids, "pw_cli_ls": ls_ids,
                      "pw_dump": dump_ids,
                      "dump_strict_subset_of_ls": set(dump_ids) < set(ls_ids)}
if ls_ids:
    info_meta = run(["pw-cli", "info", str(ls_ids[0])])
    res["info_metadata_first"] = {
        "argv": info_meta["argv"], "rc": info_meta.get("rc"),
        "bytes": len(info_meta.get("out", "")),
        "err": info_meta.get("err", "")[:120]}

# ---- 5. pw-jack env shim (env-only spawn) ------------------------------
res["jack_p512"] = run(["pw-jack", "-p", "512", "sh", "-c",
                        'echo Q=${PIPEWIRE_QUANTUM-unset}'])
res["jack_s_only"] = run(["pw-jack", "-s", "44100", "sh", "-c",
                          'echo Q=${PIPEWIRE_QUANTUM-unset}'])
for k in ("jack_p512", "jack_s_only"):
    res[k]["stdout"] = res[k].get("out", "").strip()
    res[k] = {kk: res[k][kk] for kk in ("argv", "rc", "stdout")}

# ---- 6. the rc0 refusal family + the one nonzero -----------------------
res["info_bogus"] = {k: run(["pw-cli", "info", "bogus"])[k]
                     for k in ("rc",)}
res["info_bogus"]["err"] = run(["pw-cli", "info", "bogus"])["err"][:160]
res["remote_down"] = run(["pw-cli", "-r", "r86crit_nope", "ls", "Node"],
                         timeout=15.0)
res["remote_down"] = {"rc": res["remote_down"].get("rc"),
                      "err": res["remote_down"].get("err", "")[:200]}
res["top_batch"] = {"rc": run(["pw-top", "-b", "-n", "2"])["rc"]}

# ---- 7. residue census (read-only) -------------------------------------
mods = run(["pactl", "list", "short", "modules"])
res["residue"] = {
    "pactl_modules_r86a": sum(1 for ln in mods.get("out", "").splitlines()
                              if "r86a" in ln),
    "dump_r86a_nodes": [o["info"]["props"].get("node.name")
                        for o in nodes
                        if "r86a" in (o["info"]["props"].get("node.name")
                                      or "")],
    "meta_default_r86a_keys": [ln.strip()[:120] for ln in
                               run(["pw-metadata", "-n", "default"])
                               .get("out", "").splitlines()
                               if "r86a" in ln],
}
OUT.write_text(json.dumps(res, indent=2) + "\n")

# ---- summary -----------------------------------------------------------
print(json.dumps({
    "subject": res["subject"],
    "ls_serial_bytes": res["ls_serial"]["out_bytes"],
    "ls_id_bytes": res["ls_id"]["out_bytes"],
    "info_id_rc": res["info_id"]["rc"],
    "info_serial_rc": res["info_serial"]["rc"],
    "info_serial_err_head": res["info_serial"]["err"].strip()[:80],
    "enum_serial_err_head": res["enum_serial"]["err"].strip()[:80],
    "dump_full_byte_equal": res["dump_id_vs_serial"]["full_byte_equal"],
    "dump_bytes": (res["dump_id_vs_serial"]["bytes_id"],
                   res["dump_id_vs_serial"]["bytes_serial"]),
    "meta_census": res["meta_census"],
    "info_metadata": res.get("info_metadata_first"),
    "jack": {"p512": res["jack_p512"]["stdout"],
             "s_only": res["jack_s_only"]["stdout"]},
    "info_bogus_rc": res["info_bogus"]["rc"],
    "remote_down_rc": res["remote_down"]["rc"],
    "top_batch_rc": res["top_batch"]["rc"],
    "residue": res["residue"],
    "live_r86a_objects": res["host"]["live_r86a_objects"],
    "loadavg": res["host"]["loadavg"],
}, indent=2))
