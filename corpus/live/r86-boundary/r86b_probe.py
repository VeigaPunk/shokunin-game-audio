#!/usr/bin/env python3
"""r86-boundary falsification harness — seat r86b_* (audio lane, round 86).

Attacks the r86 scout claims: verbatim replays, host-state variation, hog load,
unstated-mode hunting.  Writes only under corpus/live/r86-boundary/.
Usage: r86b_probe.py <stage> [<stage> ...]   stages: b0 b1 b2 b3 b4 b5 b6 clean
"""
import json, os, re, signal, subprocess, sys, time, wave, hashlib, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(ROOT, "receipts")
RUNS = os.path.join(ROOT, "runs")
KEEP = os.path.join(ROOT, "keep")
NS = "r86b"
SINK = f"{NS}_ns"
TONE = os.path.join(KEEP, "tone_r86b.wav")
CAP = 6000  # truncation for stored raw text


def load():
    with open("/proc/loadavg") as f:
        return f.read().split()[0:3]


def host():
    return {"load": load(), "t": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "yes": len(subprocess.run(["pgrep", "-x", "yes"], capture_output=True, text=True).stdout.split()),
            "r86b_procs": subprocess.run(["bash", "-lc", f"pgrep -f {NS} | wc -l"], capture_output=True, text=True).stdout.strip()}


def trunc(s, n=CAP):
    s = s if isinstance(s, str) else str(s)
    return s if len(s) <= n else s[:n] + f"\n...[truncated {len(s)-n} chars]"


def run(cmd, timeout=30, env=None, input=None):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env, input=input)
        return {"cmd": cmd if isinstance(cmd, str) else " ".join(cmd), "rc": p.returncode,
                "out": trunc(p.stdout), "err": trunc(p.stderr), "secs": round(time.time() - t0, 3)}
    except subprocess.TimeoutExpired as e:
        return {"cmd": cmd if isinstance(cmd, str) else " ".join(cmd), "rc": "TIMEOUT",
                "out": trunc(e.stdout or ""), "err": trunc(e.stderr or ""), "secs": round(time.time() - t0, 3)}


def sh(cmd, **kw):
    return run(["bash", "-lc", cmd], **kw)


def save(stage, obj):
    obj["host_end"] = host()
    p = os.path.join(REC, f"{stage}.json")
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)
    print(f"[receipt] {p} ({os.path.getsize(p)} B)")
    return p


def pw_dump():
    p = subprocess.run(["pw-dump"], capture_output=True, text=True, timeout=60)
    return json.loads(p.stdout), p.stdout


def objs_by_id(dump):
    return {o["id"]: o for o in dump if "id" in o}


def ser(o):
    try:
        return int(o["info"]["props"]["object.serial"])
    except Exception:
        return None


def props(o):
    try:
        return o["info"]["props"]
    except Exception:
        return {}


def diff_ids(a, b):
    """a,b: dict id->obj. returns added/removed/changed id lists + changed paths."""
    added = sorted(set(b) - set(a)); removed = sorted(set(a) - set(b)); changed = []
    for i in sorted(set(a) & set(b)):
        if a[i] != b[i]:
            changed.append({"id": i, "type": a[i].get("type"), "paths": diff_paths(a[i], b[i])[:8]})
    return {"added": added, "removed": removed, "changed": changed}


def diff_paths(x, y, path="", depth=0, acc=None):
    if acc is None:
        acc = []
    if depth > 4 or len(acc) > 40:
        return acc
    if type(x) != type(y):
        acc.append(f"{path}: type {type(x).__name__}->{type(y).__name__}")
        return acc
    if isinstance(x, dict):
        for k in sorted(set(x) | set(y)):
            if k not in x or k not in y:
                acc.append(f"{path}.{k}: {'missing' if k not in x else 'added'}")
            else:
                diff_paths(x[k], y[k], f"{path}.{k}", depth + 1, acc)
    elif isinstance(x, list):
        if len(x) != len(y):
            acc.append(f"{path}: len {len(x)}->{len(y)}")
        for i, (u, v) in enumerate(zip(x, y)):
            diff_paths(u, v, f"{path}[{i}]", depth + 1, acc)
    elif x != y:
        acc.append(f"{path}: {trunc(str(x),120)} -> {trunc(str(y),120)}")
    return acc


def canon_hash(dump):
    """drop the pw-dump self client row(s), canonical-serialize, hash."""
    keep = [o for o in dump if props(o).get("application.name") != "pw-dump"]
    b = json.dumps(keep, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(b).hexdigest()[:16], len(keep), [o["id"] for o in dump if props(o).get("application.name") == "pw-dump"]


# ---------------------------------------------------------------- b0
def stage_b0():
    r = {"stage": "b0", "host_start": host()}
    r["versions"] = {v: run([v, "--version"]) for v in ["pw-cli", "pw-dump", "pw-metadata", "pw-top"]}
    r["pactl_version"] = run(["pactl", "--version"])
    dump, raw = pw_dump()
    r["census"] = {"n_objects": len(dump), "types": {}}
    for o in dump:
        r["census"]["types"][o.get("type", "?")] = r["census"]["types"].get(o.get("type", "?"), 0) + 1
    with open(os.path.join(KEEP, "census_b0.json"), "w") as f:
        f.write(raw)
    byid = objs_by_id(dump)
    # serial/id collision hunt
    byser = {}
    for o in dump:
        s = ser(o)
        if s is not None:
            byser.setdefault(s, []).append(o["id"])
    pairs = []
    for s, ids in sorted(byser.items()):
        for oid in ids:
            if oid in byid and s in byid and s != oid:
                pairs.append({"serial": s, "serial_holder": ids, "id_holder": {"id": s, "type": byid[s].get("type")}})
    r["collision_pairs"] = pairs[:6]
    r["id_serials_self"] = {"n_with_serial": len(byser), "example": [(k, v) for k, v in list(sorted(byser.items()))[:5]]}

    # class census via pw-cli ls <iface>
    ifaces = ["Core", "Module", "Factory", "Device", "Node", "Port", "Client", "Link",
              "Metadata", "Profiler", "Session", "Endpoint", "EndpointStream", "ClientNode",
              "ClientEndpoint", "SecurityContext", "Bogus", "node", "node_", "PORT", ""]
    r["ls_classes"] = {}
    for i in ifaces:
        c = run(["pw-cli", "ls", i] if i != "" else ["pw-cli", "ls"])
        r["ls_classes"][i or "<bare>"] = {"rc": c["rc"], "n_lines": len(c["out"].splitlines()),
                                          "out_head": trunc(c["out"], 300), "err": c["err"]}
    # addressing: collision pair + sentinels
    r["addressing"] = {}
    if pairs:
        s = pairs[0]["serial"]; oid = pairs[0]["id_holder"]["id"]
        for label, num in [("collision_serial", s), ("collision_id", oid), ("s99999", 99999), ("s0", 0)]:
            r["addressing"][label] = {
                "n": num,
                "ls": run(["pw-cli", "ls", str(num)]),
                "info": run(["pw-cli", "info", str(num)]),
                "dump": run(["pw-dump", str(num)]),
            }
    r["addressing"]["info_bogus"] = run(["pw-cli", "info", "bogus"])
    r["addressing"]["dump_99999_bytes"] = run(["bash", "-lc", "pw-dump 99999 | wc -c"])
    r["addressing"]["dump_bogus_bytes"] = run(["bash", "-lc", "pw-dump bogus | wc -c"])
    # create seat sink now (stable node for later stages)
    r["sink_create"] = run(["pactl", "load-module", "module-null-sink", f"sink_name={SINK}"])
    r["sink_module_line"] = sh(f"pactl list short modules | grep -F {SINK} || true")
    time.sleep(0.4)
    dump2, raw2 = pw_dump()
    with open(os.path.join(KEEP, "census_b0_sink.json"), "w") as f:
        f.write(raw2)
    mine = [o for o in dump2 if props(o).get("node.name") == SINK or props(o).get("application.name") == "pw-cli"]
    r["sink_objects"] = [{"id": o["id"], "type": o.get("type"), "name": props(o).get("node.name") or props(o).get("port.name") or props(o).get("application.name"),
                          "serial": ser(o)} for o in dump2 if props(o).get("node.name") == SINK]
    r["sink_ports"] = [{"id": o["id"], "type": o.get("type"), "port": props(o).get("port.name"), "dir": props(o).get("port.direction"), "serial": ser(o)}
                       for o in dump2 if o.get("type") == "PipeWire:Interface:Port" and str(props(o).get("node.id")) == str(next((x["id"] for x in dump2 if props(x).get("node.name") == SINK), ""))]
    # rc discipline sentinels
    nid = next((x["id"] for x in dump2 if props(x).get("node.name") == SINK), None)
    r["rc_sentinels"] = {
        "enum_bogus": run(["pw-cli", "enum-params", str(nid), "Bogus"]),
        "setparam_usage": run(["pw-cli", "set-param", str(nid), "Props"]),
        "setparam_badglobal": run(["pw-cli", "set-param", "99999", "Props", "{ }"]),
        "metadata_bogus_store": run(["pw-metadata", "-n", "bogus_store_r86b"]),
        "pwlink_bogus": run(["pw-link", "no_such_out_r86b", "no_such_in_r86b"]),
    }
    save("b0", r)


# ---------------------------------------------------------------- b0b
def stage_b0b():
    """Decisive id-vs-serial split on seat-owned objects + metadata census."""
    r = {"stage": "b0b", "host_start": host()}
    d, raw = pw_dump()
    byid = objs_by_id(d)
    ser_map = {}
    for o in d:
        s = ser(o)
        if s is not None:
            ser_map.setdefault(s, []).append(o["id"])
    small = sorted([s for s in ser_map if s < 1000])
    r["small_serials"] = [(s, ser_map[s]) for s in small[:20]]
    r["serials_total"] = len(ser_map)
    r["serial_min_max"] = [min(ser_map), max(ser_map)] if ser_map else None
    r["id_min_max"] = [min(byid), max(byid)]
    # true collisions (serial value == some object id)
    coll = [{"serial": s, "serial_holder": v} for s, v in sorted(ser_map.items()) if s in byid and s not in v]
    r["true_collisions"] = coll
    mine = next((o for o in d if props(o).get("node.name") == SINK), None)
    r["mine"] = {"id": mine["id"], "serial": ser(mine), "type": mine.get("type")} if mine else None
    if mine:
        i, s = mine["id"], ser(mine)
        r["split_test"] = {}
        for label, n in [("own_id", i), ("own_serial", s)]:
            r["split_test"][label] = {"n": n,
                                      "ls": run(["pw-cli", "ls", str(n)]),
                                      "info": run(["pw-cli", "info", str(n)]),
                                      "enum_props": run(["pw-cli", "enum-params", str(n), "Props"]),
                                      "dump": run(["pw-dump", str(n)])}
        r["split_test"]["cross_numbers"] = {
            "ls_own_id_first60": r["split_test"]["own_id"]["ls"]["out"][:60],
            "ls_own_serial_first60": r["split_test"]["own_serial"]["ls"]["out"][:60],
            "info_own_id_first60": r["split_test"]["own_id"]["info"]["out"][:60],
            "info_own_serial_err": r["split_test"]["own_serial"]["info"]["err"],
            "dump_own_id_bytes": len(r["split_test"]["own_id"]["dump"]["out"]),
            "dump_own_serial_bytes": len(r["split_test"]["own_serial"]["dump"]["out"]),
        }
        for lab in r["split_test"]:
            if lab == "cross_numbers":
                continue
            x = r["split_test"][lab]
            x["ls_head"] = trunc(x["ls"]["out"], 200); x["info_head"] = trunc(x["info"]["out"], 200)
            x["dump_head"] = trunc(x["dump"]["out"], 300)
    # per-class object counts from ls output ("id N," lines)
    r["ls_counts"] = {}
    for iface in ["Core", "Module", "Factory", "Device", "Node", "Port", "Client", "Link",
                  "Metadata", "Profiler", "SecurityContext", "Session"]:
        c = run(["pw-cli", "ls", iface])
        r["ls_counts"][iface] = {"rc": c["rc"], "n_objects": len(re.findall(r"^\s*id \d+,", c["out"], re.M)),
                                 "n_lines": len(c["out"].splitlines())}
    # metadata census: pw-metadata -l vs pw-dump Metadata objects vs pw-cli ls Metadata
    r["metadata"] = {"pw_metadata_l": run(["pw-metadata", "-l"]),
                     "pw_dump_metadata_objects": [{"id": o["id"], "props": {k: v for k, v in props(o).items() if "name" in k or "id" in k}} for o in d if o.get("type") == "PipeWire:Interface:Metadata"],
                     "pw_cli_ls_metadata": run(["pw-cli", "ls", "Metadata"])}
    save("b0b", r)


# ---------------------------------------------------------------- b1
def stage_b1():
    r = {"stage": "b1", "host_start": host()}
    rounds = []
    for rnd in range(2):
        snaps = []
        for i in range(5):
            d, raw = pw_dump()
            h, n, selfids = canon_hash(d)
            snaps.append({"i": i, "hash": h, "n_obj_canon": n, "self_ids": selfids, "n_obj": len(d),
                          "ids": [o["id"] for o in d], "bytes": len(raw)})
            if i == 0:
                with open(os.path.join(KEEP, f"dump_b1_r{rnd}_s0.json"), "w") as f:
                    f.write(raw)
            if i < 4:
                time.sleep(0.5)
        diffs = []
        for i in range(4):
            d1 = json.loads(open(os.path.join(KEEP, f"dump_b1_r{rnd}_s0.json")).read()) if False else None
        rounds.append({"round": rnd, "snaps": snaps, "load": host()})
    # pairwise object diffs (re-dump twice quickly, keep in memory)
    dumps = []
    for i in range(3):
        d, _ = pw_dump()
        dumps.append(objs_by_id(d))
        if i < 2:
            time.sleep(0.5)
    r["rounds"] = rounds
    r["pair_diffs"] = [diff_ids(dumps[0], dumps[1]), diff_ids(dumps[1], dumps[2])]
    r["canon_hash_stable_round0"] = len({s["hash"] for s in rounds[0]["snaps"]}) == 1
    r["canon_hash_stable_round1"] = len({s["hash"] for s in rounds[1]["snaps"]}) == 1
    # modes
    r["modes"] = {
        "-N": run(["pw-dump", "-N"]), "-R": run(["pw-dump", "-R"]), "-i0": run(["pw-dump", "-i", "0"]),
        "-Cnever": run(["pw-dump", "-C", "never"]), "-Calways_piped": run(["pw-dump", "-C", "always"]),
        "-s": run(["pw-dump", "-s"]), "-h": run(["pw-dump", "-h"]),
    }
    for k in ["-N", "-R", "-i0", "-Cnever", "-Calways_piped", "-s"]:
        r["modes"][k]["out_bytes"] = len(r["modes"][k]["out"])
        r["modes"][k]["ansi_escapes"] = r["modes"][k]["out"].count("\x1b")
    # -m bounded
    t0 = time.time()
    p = subprocess.Popen(["pw-dump", "-m"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(1.5)
    p.kill()
    out, err = p.communicate()
    r["modes"]["-m_1p5s"] = {"rc": p.returncode, "out_lines": len(out.splitlines()), "out_bytes": len(out),
                             "secs": round(time.time() - t0, 2), "tail": trunc(out[-600:], 600)}
    # id-family of pw-dump <N> using the collision pair (recompute)
    d, _ = pw_dump()
    byid = objs_by_id(d)
    byser = {}
    for o in d:
        s = ser(o)
        if s is not None:
            byser.setdefault(s, []).append(o["id"])
    pair = next(({"serial": s, "holder": v} for s, v in sorted(byser.items()) if s in byid and s not in v and s != v[0]), None)
    if pair:
        n = pair["serial"]
        got = run(["pw-dump", str(n)])
        try:
            arr = json.loads(got["out"])
            r["dump_id_family"] = {"n": n, "pair": pair, "returned": [{"id": o["id"], "type": o.get("type"), "props_serial": ser(o)} for o in arr],
                                   "rc": got["rc"]}
        except Exception as e:
            r["dump_id_family"] = {"n": n, "pair": pair, "parse_error": str(e), "raw": trunc(got["out"], 300)}
    save("b1", r)


# ---------------------------------------------------------------- b2
def stage_b2():
    r = {"stage": "b2", "host_start": host()}
    d, _ = pw_dump()
    byid = objs_by_id(d)
    def find(pred, typ=None):
        return [o for o in d if (typ is None or o.get("type") == typ) and pred(o)]
    nid = next((o["id"] for o in find(lambda o: props(o).get("node.name") == SINK, "PipeWire:Interface:Node")), None)
    pid_ = next((o["id"] for o in find(lambda o: props(o).get("node.name") == SINK, "PipeWire:Interface:Port")), None)
    dev = next((o["id"] for o in find(lambda o: True, "PipeWire:Interface:Device")), None)
    cli = next((o["id"] for o in find(lambda o: True, "PipeWire:Interface:Client")), None)
    fac = next((o["id"] for o in find(lambda o: True, "PipeWire:Interface:Factory")), None)
    mod = next((o["id"] for o in find(lambda o: True, "PipeWire:Interface:Module")), None)
    lnk = next((o["id"] for o in find(lambda o: True, "PipeWire:Interface:Link")), None)
    r["ids"] = {"node": nid, "port": pid_, "device": dev, "client": cli, "factory": fac, "module": mod, "link": lnk}
    params = ["Props", "PropInfo", "EnumFormat", "Format", "Latency", "ProcessLatency", "IO", "Meta",
              "Profile", "EnumProfile", "Route", "EnumRoute", "Bogus", "999", "all", "3"]
    r["matrix"] = {}
    for label, oid in [("node", nid), ("port", pid_), ("device", dev), ("client", cli), ("factory", fac), ("module", mod), ("link", lnk)]:
        if oid is None:
            continue
        r["matrix"][label] = {}
        for pm in params:
            c = run(["pw-cli", "enum-params", str(oid), pm])
            r["matrix"][label][pm] = {"rc": c["rc"], "out": c["out"], "err": c["err"],
                                      "class": classify_ep(c)}
    # numeric == name
    r["numeric_eq_name"] = {"enum_3": run(["pw-cli", "enum-params", str(nid), "3"]),
                            "enum_EnumFormat": run(["pw-cli", "enum-params", str(nid), "EnumFormat"])}
    # Format racy: 12 reps on port
    reps = []
    for i in range(12):
        c = run(["pw-cli", "enum-params", str(pid_), "Format"])
        reps.append({"i": i, "rc": c["rc"], "out_len": len(c["out"]), "err_head": c["err"][:160]})
    r["format_racy_12"] = {"reps": reps, "eio_text": sum(1 for x in reps if "Input/output" in x["err_head"] or "res:-5" in x["err_head"]),
                           "silent": sum(1 for x in reps if x["out_len"] == 0 and not x["err_head"])}
    # negotiated-format test: play a tone, then enum Format on node+port
    if os.path.exists(TONE):
        player = subprocess.Popen(["pw-play", "--target", SINK, TONE], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        time.sleep(1.0)
        r["format_after_negotiation"] = {"node": run(["pw-cli", "enum-params", str(nid), "Format"]),
                                         "port": run(["pw-cli", "enum-params", str(pid_), "Format"])}
        player.kill(); player.wait()
        time.sleep(0.5)
        r["format_after_stop"] = {"port": run(["pw-cli", "enum-params", str(pid_), "Format"])}
    else:
        r["format_after_negotiation"] = "tone missing"
    save("b2", r)


def classify_ep(c):
    e, o = c["err"], c["out"]
    if "not implemented on object" in e:
        return "ep_local_not_impl"
    if "unknown param type" in e:
        return "ep_local_unknown_type"
    if "unknown global" in e:
        return "ep_unknown_global"
    if "res:-2" in e or "No such file" in e:
        return "ep_remote_enoent"
    if "res:-5" in e or "Input/output" in e:
        return "ep_remote_eio_racy"
    if not e and not o.strip():
        return "ep_silent_empty"
    if not e and o.strip():
        return "pod_dump"
    return "other"


# ---------------------------------------------------------------- b2b
def stage_b2b():
    """Port-side enum-params matrix + Format pre/during/post negotiation (fixed lookup)."""
    r = {"stage": "b2b", "host_start": host()}
    d, _ = pw_dump()
    nid = next((o["id"] for o in d if props(o).get("node.name") == SINK), None)
    ports = [o for o in d if o.get("type") == "PipeWire:Interface:Port" and str(props(o).get("node.id")) == str(nid)]
    r["ids"] = {"node": nid, "ports": {props(p).get("port.name"): {"id": p["id"], "serial": ser(p), "direction": props(p).get("port.direction")} for p in ports}}
    pl = next((p for p in ports if props(p).get("port.name") == "playback_FL"), None)
    if pl is None:
        save("b2b", r); return
    pid_ = pl["id"]
    params = ["Props", "PropInfo", "EnumFormat", "Format", "Latency", "ProcessLatency", "IO", "Meta",
              "Profile", "EnumProfile", "Route", "EnumRoute", "Bogus", "3"]
    r["port_matrix"] = {}
    for pm in params:
        c = run(["pw-cli", "enum-params", str(pid_), pm])
        r["port_matrix"][pm] = {"rc": c["rc"], "out": trunc(c["out"], 700), "err": c["err"], "class": classify_ep(c)}
    # 12 reps Format pre-negotiation
    reps = []
    for i in range(12):
        c = run(["pw-cli", "enum-params", str(pid_), "Format"])
        reps.append({"i": i, "rc": c["rc"], "out_len": len(c["out"]), "err_head": c["err"][:200]})
    r["format_pre_12"] = {"reps": reps,
                          "eio_text": sum(1 for x in reps if "res:-5" in x["err_head"] or "Input/output" in x["err_head"]),
                          "enoent_text": sum(1 for x in reps if "res:-2" in x["err_head"]),
                          "silent": sum(1 for x in reps if x["out_len"] == 0 and not x["err_head"]),
                          "with_out": sum(1 for x in reps if x["out_len"] > 0)}
    # during negotiation
    player = subprocess.Popen(["pw-play", "--target", SINK, TONE], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    time.sleep(1.0)
    r["during"] = {"port_format": run(["pw-cli", "enum-params", str(pid_), "Format"]),
                   "node_format": run(["pw-cli", "enum-params", str(nid), "Format"]),
                   "port_latency": run(["pw-cli", "enum-params", str(pid_), "Latency"]),
                   "port_io": run(["pw-cli", "enum-params", str(pid_), "IO"]),
                   "port_meta": run(["pw-cli", "enum-params", str(pid_), "Meta"]),
                   "port_props": run(["pw-cli", "enum-params", str(pid_), "Props"]),
                   "port_enumformat": run(["pw-cli", "enum-params", str(pid_), "EnumFormat"]),
                   "info_port": run(["pw-cli", "info", str(pid_)])}
    for k, v in r["during"].items():
        if isinstance(v, dict):
            v["class"] = classify_ep(v)
    player.wait(timeout=20)
    time.sleep(0.8)
    r["post"] = {"port_format": run(["pw-cli", "enum-params", str(pid_), "Format"]),
                 "node_format": run(["pw-cli", "enum-params", str(nid), "Format"]),
                 "info_port": run(["pw-cli", "info", str(pid_)])}
    for k, v in r["post"].items():
        v["class"] = classify_ep(v)
    # link census while nothing plays (Link objects)
    r["links_now"] = run(["pw-cli", "ls", "Link"])
    save("b2b", r)


# ---------------------------------------------------------------- b3
def stage_b3():
    r = {"stage": "b3", "host_start": host()}
    d, _ = pw_dump()
    nid = next((o["id"] for o in d if props(o).get("node.name") == SINK), None)
    r["ids"] = {"node": nid}
    r["inventory"] = run(["pw-metadata", "-l"])
    r["bogus_store"] = run(["pw-metadata", "-n", "bogus_store_r86b"])
    r["bare_equals_default"] = {"bare": run(["pw-metadata"]), "default": run(["pw-metadata", "-n", "default"])}
    r["subject0_read"] = run(["pw-metadata", "-n", "default", "0"])
    r["subject0_keys"] = sorted(set(re.findall(r"key:'([^']+)'", r["subject0_read"]["out"])))
    r["seat_subject0_key_absent"] = run(["pw-metadata", "-n", "default", "0", f"{NS}_absent_key"])
    # live-subject cycle
    cyc = []
    cyc.append({"op": "write", "r": run(["pw-metadata", "-n", "default", str(nid), f"{NS}_k1", "V1"])})
    cyc.append({"op": "read", "r": run(["pw-metadata", "-n", "default", str(nid), f"{NS}_k1"])})
    cyc.append({"op": "overwrite", "r": run(["pw-metadata", "-n", "default", str(nid), f"{NS}_k1", "V2"])})
    cyc.append({"op": "read", "r": run(["pw-metadata", "-n", "default", str(nid), f"{NS}_k1"])})
    cyc.append({"op": "write_typed", "r": run(["pw-metadata", "-n", "default", str(nid), f"{NS}_k1", "V3", "Spa:String"])})
    cyc.append({"op": "read", "r": run(["pw-metadata", "-n", "default", str(nid), f"{NS}_k1"])})
    cyc.append({"op": "read_absent", "r": run(["pw-metadata", "-n", "default", str(nid), f"{NS}_nokey"])})
    cyc.append({"op": "del", "r": run(["pw-metadata", "-n", "default", "-d", str(nid), f"{NS}_k1"])})
    cyc.append({"op": "read_after_del", "r": run(["pw-metadata", "-n", "default", str(nid), f"{NS}_k1"])})
    cyc.append({"op": "del_absent", "r": run(["pw-metadata", "-n", "default", "-d", str(nid), f"{NS}_nokey"])})
    cyc.append({"op": "subject0_del_seatkey_absent", "r": run(["pw-metadata", "-n", "default", "-d", "0", f"{NS}_absent_key"])})
    r["cycle"] = cyc
    # dead subject
    r["dead_subject"] = {"write": run(["pw-metadata", "-n", "default", "99997", f"{NS}_dead", "D1"]),
                         "read": run(["pw-metadata", "-n", "default", "99997", f"{NS}_dead"]),
                         "read_all": run(["pw-metadata", "-n", "default", "99997"])}
    # multi-key under live subject then bare-subject delete
    r["multi"] = {"w1": run(["pw-metadata", "-n", "default", str(nid), f"{NS}_m1", "A"]),
                  "w2": run(["pw-metadata", "-n", "default", str(nid), f"{NS}_m2", "B"]),
                  "read_all": run(["pw-metadata", "-n", "default", str(nid)]),
                  "del_subject": run(["pw-metadata", "-n", "default", "-d", str(nid)]),
                  "read_all_after": run(["pw-metadata", "-n", "default", str(nid)])}
    # monitor bounded (all + subject filter)
    for label, args in [("m_all", ["pw-metadata", "-m"]), ("m_subj", ["pw-metadata", "-m", str(nid)])]:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(1.2)
        p.kill(); out, err = p.communicate()
        r[label] = {"out_lines": len(out.splitlines()), "head": trunc(out, 400), "err": trunc(err, 200), "rc": p.returncode}
    r["stores_read"] = {s: run(["pw-metadata", "-n", s]) for s in ["settings", "filters", "sm-objects", "route-settings"]}
    save("b3", r)


# ---------------------------------------------------------------- b4
def stage_b4():
    r = {"stage": "b4", "host_start": host()}
    # pw-jack env law
    q = 'echo "[${PIPEWIRE_QUANTUM-unset}] ${PIPEWIRE_REMOTE-unset} ${PIPEWIRE_DEBUG-unset}"'
    r["pwjack"] = {
        "s44100_p256": run(["pw-jack", "-s", "44100", "-p", "256", "sh", "-c", q]),
        "p512_only": run(["pw-jack", "-p", "512", "sh", "-c", q]),
        "s44100_only": run(["pw-jack", "-s", "44100", "sh", "-c", q]),
        "true": run(["pw-jack", "true"]),
        "bogus": run(["pw-jack", "definitely_not_a_cmd_r86b"]),
        "h": run(["pw-jack", "-h"]),
        "noargs": run(["pw-jack"]),
        "v": run(["pw-jack", "-v", "sh", "-c", q]),
        "vv": run(["pw-jack", "-v", "-v", "sh", "-c", q]),
        "v_preset": run(["pw-jack", "-v", "sh", "-c", q], env={**os.environ, "PIPEWIRE_DEBUG": "4"}),
        "r_remote": run(["pw-jack", "-r", "some_remote_r86b", "sh", "-c", q]),
        "unknown_flag": run(["pw-jack", "-Z", "true"]),
    }
    r["jack_ldd"] = sh("ldd /usr/lib/libjack.so.0.3.1608 | head -5")
    r["jack_tools"] = sh("for t in jackd jack_lsp jack_connect jack_alias jack_control jack_server_control; do command -v $t || echo MISSING $t; done")
    # pw-cli read-only mode hunts
    d, _ = pw_dump()
    cli_id = next((o["id"] for o in d if o.get("type") == "PipeWire:Interface:Client"), None)
    r["pwcli_modes"] = {
        "list-vars": run(["pw-cli", "list-vars"]),
        "list-remotes": run(["pw-cli", "list-remotes"]),
        "get-permissions": run(["pw-cli", "get-permissions", str(cli_id)]),
        "help": run(["pw-cli", "help"]),
        "h": run(["pw-cli", "h"]),
        "ls_Node": run(["pw-cli", "ls", "Node"]),
        "ls_Module": run(["pw-cli", "ls", "Module"]),
        "i_all_bytes": sh("pw-cli info all | wc -c"),
        "repl_devnull": run(["pw-cli"], input=""),
        "repl_ls": run(["pw-cli"], input="ls\n"),
        "tty_oneshot": run(["script", "-qec", "pw-cli ls Node", "/dev/null"], timeout=20),
    }
    # pw-link modes (read-only on live graph)
    r["pwlink_modes"] = {k: run(["pw-link", k]) for k in ["-l", "-o", "-i", "-I", "-t", "-v"]}
    for k in r["pwlink_modes"]:
        r["pwlink_modes"][k]["n_lines"] = len(r["pwlink_modes"][k]["out"].splitlines())
    # pw-top cheap modes
    r["pwtop_modes"] = {
        "V": run(["pw-top", "-V"]), "h": run(["pw-top", "-h"]),
        "b_n2": run(["pw-top", "-b", "-n", "2"], timeout=20),
        "b_n2_head": run(["bash", "-lc", "pw-top -b -n 2 | head -4"], timeout=20),
        "b_n0_bounded": run(["timeout", "-s", "KILL", "2", "pw-top", "-b", "-n", "0"]),
        "b_nneg": run(["timeout", "-s", "KILL", "2", "pw-top", "-b", "-n", "-1"]),
        "b_no_n_bounded": run(["timeout", "-s", "KILL", "2", "pw-top", "-b"]),
    }
    save("b4", r)


# ---------------------------------------------------------------- b4b
def stage_b4b():
    """pw-link rc discipline + unstated modes, seat-owned links only."""
    r = {"stage": "b4b", "host_start": host()}
    A, B = f"{NS}_a", f"{NS}_b"
    r["create"] = {"a": run(["pactl", "load-module", "module-null-sink", f"sink_name={A}"]),
                   "b": run(["pactl", "load-module", "module-null-sink", f"sink_name={B}"])}
    r["mod_lines"] = sh(f"pactl list short modules | grep -E '{NS}_[ab]' || true")
    time.sleep(0.5)
    r["ports"] = {"out_a": sh(f"pw-link -o | grep -F '{A}:' || true"),
                  "in_b": sh(f"pw-link -i | grep -F '{B}:' || true")}
    out_p = f"{A}:monitor_FL"; in_p = f"{B}:playback_FL"
    r["link_create"] = run(["pw-link", out_p, in_p])
    r["link_dup"] = run(["pw-link", out_p, in_p])
    r["links_after_dup"] = sh(f"pw-link -l | grep -F '{A}' || true")
    r["link_bogus"] = run(["pw-link", f"{A}:nope_r86b", f"{B}:playback_FL"])
    r["link_ids"] = run(["pw-link", "-I"])
    r["link_ids_mine"] = sh(f"pw-link -I | grep -E '{A}|{B}' || true")
    r["latency_t"] = sh(f"pw-link -t | grep -F '{A}' || true")
    r["verbose_v"] = sh(f"pw-link -v | grep -F '{A}' | head -8 || true")
    r["usage"] = run(["pw-link"])
    # disconnect by ports
    r["disc_ports"] = run(["pw-link", "-d", out_p, in_p])
    r["after_disc"] = sh(f"pw-link -l | grep -F '{A}' || true")
    # recreate with props + passive, then disconnect by link-id
    r["link_props"] = run(["pw-link", "-p", '{ "link.passive": true }', out_p, in_p])
    r["ids_after_props"] = sh(f"pw-link -I | grep -E '{A}|{B}' || true")
    lid = None
    m = re.search(r"^\s*(\d+)\s", r["ids_after_props"]["out"], re.M)
    if m:
        lid = m.group(1)
    r["disc_id"] = run(["pw-link", "-d", lid]) if lid else "no id found"
    r["after_disc_id"] = sh(f"pw-link -l | grep -F '{A}' || true")
    r["link_passive_flag"] = run(["pw-link", "-P", out_p, in_p])
    r["after_passive"] = sh(f"pw-link -l | grep -F '{A}' || true")
    r["link_wait"] = run(["pw-link", "-w", out_p, in_p], timeout=20)
    r["monitor_bounded"] = run(["timeout", "-s", "KILL", "1.5", "pw-link", "-m"])
    r["monitor_out"] = None
    p = subprocess.Popen(["pw-link", "-m"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(1.5)
    p.kill(); out, err = p.communicate()
    r["monitor_out"] = {"head": trunc(out, 400), "lines": len(out.splitlines()), "rc": p.returncode}
    save("b4b", r)


# ---------------------------------------------------------------- b5
def sig_rc(rc):
    return rc if rc >= 0 else 128 + abs(rc)


def stage_b5():
    r = {"stage": "b5", "host_start": host()}
    r["core_count_before"] = sh("coredumpctl list --no-pager 2>/dev/null | wc -l")
    # clean batch reps
    r["batch_clean"] = [run(["pw-top", "-b", "-n", "2"], timeout=20) for _ in range(3)]
    for x in r["batch_clean"]:
        x["n_lines"] = len(x["out"].splitlines()); x["head"] = trunc(x["out"], 200)
    # TUI piped + TERM (2 reps)
    r["tui_term"] = []
    for i in range(2):
        p = subprocess.Popen(["pw-top"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(1.2)
        p.send_signal(signal.SIGTERM)
        out, err = p.communicate(timeout=15)
        r["tui_term"].append({"raw_rc": p.returncode, "shell_rc": sig_rc(p.returncode),
                              "err_tail": trunc(err[-500:], 500), "out_bytes": len(out), "load": host()})
    # TUI KILL (1 rep)
    p = subprocess.Popen(["pw-top"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(1.0)
    p.send_signal(signal.SIGKILL)
    out, err = p.communicate(timeout=15)
    r["tui_kill"] = {"raw_rc": p.returncode, "shell_rc": sig_rc(p.returncode), "err_tail": trunc(err[-300:], 300)}
    # H1 (labrat hypothesis): batch mid-run TERM (3 reps)
    r["batch_term"] = []
    for i in range(3):
        p = subprocess.Popen(["pw-top", "-b", "-n", "100000"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(1.5)
        p.send_signal(signal.SIGTERM)
        out, err = p.communicate(timeout=20)
        r["batch_term"].append({"raw_rc": p.returncode, "shell_rc": sig_rc(p.returncode),
                                "err_tail": trunc(err[-500:], 500), "out_lines": len(out.splitlines()), "load": host()})
    # batch mid-run INT (1 rep)
    p = subprocess.Popen(["pw-top", "-b", "-n", "100000"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(1.2)
    p.send_signal(signal.SIGINT)
    out, err = p.communicate(timeout=20)
    r["batch_int"] = {"raw_rc": p.returncode, "shell_rc": sig_rc(p.returncode), "err_tail": trunc(err[-400:], 400)}
    r["core_count_after"] = sh("coredumpctl list --no-pager 2>/dev/null | wc -l")
    save("b5", r)


# ---------------------------------------------------------------- b6
def make_tone():
    if os.path.exists(TONE):
        return
    import numpy as np
    sr, secs, amp, f = 48000, 3.0, 12000, 1000.0
    n = int(sr * secs)
    t = np.arange(n) / sr
    x = (amp * np.sin(2 * np.pi * f * t)).astype("<i2")
    stereo = np.repeat(x[:, None], 2, axis=1).tobytes()
    with wave.open(TONE, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(stereo)


def peaks(path, win=0.25):
    import numpy as np
    with wave.open(path, "rb") as w:
        sr = w.getframerate(); ch = w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").reshape(-1, ch)
    k = int(sr * win)
    out = []
    for i in range(0, len(x) - k + 1, k):
        out.append(round(float(np.abs(x[i:i + k]).max()), 1))
    return out, sr, len(x)


def stage_b6():
    import numpy as np
    r = {"stage": "b6", "host_start": host()}
    make_tone()
    d, _ = pw_dump()
    nid = next((o["id"] for o in d if props(o).get("node.name") == SINK), None)
    r["ids"] = {"node": nid}
    if nid is None:
        save("b6", r); return
    r["sink_ports"] = sh(f"pw-link -o | grep -F {SINK} || true")

    def leg(name, write=None, reps=1):
        outs = []
        for rep in range(reps):
            cap = os.path.join(RUNS, f"b6_{name}_r{rep}.wav")
            tapper = subprocess.Popen(["pw-record", "-P", "stream.capture.sink=true", "-P", f"node.name={NS}_tap_{name}_{rep}",
                                       "--target", SINK, "-n", str(48000 * 5), "--rate", "48000", "--channels", "2",
                                       "--format", "s16", cap], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            time.sleep(0.5)
            link = sh(f"pw-link -l | grep -F '{SINK}:monitor' || true")
            player = subprocess.Popen(["pw-play", "--target", SINK, TONE], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            t0 = time.time()
            wrote = None
            if write is not None:
                delay, cmd = write
                time.sleep(max(0.0, t0 + delay - time.time()))
                wrote = run(cmd)
            player.wait(timeout=20)
            tapper.wait(timeout=20)
            try:
                pk, sr, n = peaks(cap)
            except Exception as e:
                pk, sr, n = [f"analyze_error {e}"], None, None
            outs.append({"rep": rep, "link": link["out"].strip()[:200], "write": wrote, "peaks": pk,
                         "load": host(), "cap_bytes": os.path.getsize(cap) if os.path.exists(cap) else None})
            time.sleep(0.3)
        r[name] = outs

    run(["pactl", "set-sink-volume", SINK, "100%"])
    leg("solo_ref", None, 2)
    leg("chvol_025", (2.0, ["pw-cli", "set-param", str(nid), "Props", "{ channelVolumes: [0.25,0.25] }"]), 2)
    r["after_chvol_025"] = {"pactl_pct": run(["pactl", "get-sink-volume", SINK]),
                            "enum": run(["pw-cli", "enum-params", str(nid), "Props"])}
    run(["pactl", "set-sink-volume", SINK, "100%"])
    leg("chvol_05", (2.0, ["pw-cli", "set-param", str(nid), "Props", "{ channelVolumes: [0.5,0.5] }"]), 1)
    r["after_chvol_05"] = {"pactl_pct": run(["pactl", "get-sink-volume", SINK]),
                           "enum": run(["pw-cli", "enum-params", str(nid), "Props"])}
    run(["pactl", "set-sink-volume", SINK, "100%"])
    leg("mute", (2.0, ["pw-cli", "set-param", str(nid), "Props", "{ mute: true }"]), 2)
    run(["pw-cli", "set-param", str(nid), "Props", "{ mute: false }"])
    run(["pactl", "set-sink-volume", SINK, "100%"])
    leg("volume_dead", (2.0, ["pw-cli", "set-param", str(nid), "Props", "{ volume: 0.25 }"]), 2)
    r["after_volume_dead"] = {"pactl_pct": run(["pactl", "get-sink-volume", SINK]),
                              "enum": run(["pw-cli", "enum-params", str(nid), "Props"]),
                              "enum_volume_line": sh(f"pw-cli enum-params {nid} Props | grep -A3 -i volume | head -12")}
    run(["pactl", "set-sink-volume", SINK, "100%"])
    leg("pactl_25", (2.0, ["pactl", "set-sink-volume", SINK, "25%"]), 2)
    r["after_pactl_25"] = {"pactl_pct": run(["pactl", "get-sink-volume", SINK])}
    run(["pactl", "set-sink-volume", SINK, "100%"])
    # write-refusal lattice
    r["writes"] = {
        "garbage": run(["pw-cli", "set-param", str(nid), "Props", "garbage"]),
        "empty_obj": run(["pw-cli", "set-param", str(nid), "Props", "{ }"]),
        "unknown_key": run(["pw-cli", "set-param", str(nid), "Props", "{ zzz.r86b: 7 }"]),
        "wrong_type": run(["pw-cli", "set-param", str(nid), "Props", '{ volume: "high" }']),
        "enumformat_write": run(["pw-cli", "set-param", str(nid), "EnumFormat", "{ mediaType: 1, mediaSubtype: 2 }"]),
        "port_latency": run(["pw-cli", "set-param", next((str(o["id"]) for o in pw_dump()[0] if o.get("type") == "PipeWire:Interface:Port" and props(o).get("node.name") == SINK), "0"), "Latency", "{ minQuantum: 2.0 }"]),
    }
    r["writes_recheck"] = {"unknown_key_reenum": sh(f"pw-cli enum-params {nid} Props | grep -c zzz || true")}
    save("b6", r)


# ---------------------------------------------------------------- clean
def stage_clean():
    r = {"stage": "clean", "host_start": host()}
    mods = sh(f"pactl list short modules | grep -F {NS} || true")
    r["modules_before"] = mods
    idxs = []
    for line in mods["out"].splitlines():
        m = re.match(r"^(\d+)\s", line)
        if m and (f"sink_name={SINK}" in line or f"sink_name={NS}_" in line):
            idxs.append((m.group(1), line))
    r["unloads"] = []
    for idx, line in idxs:
        verify = sh(f"pactl list short modules | grep -E '^{idx}\\s' || true")
        r["unloads"].append({"idx": idx, "verified_line": trunc(verify["out"], 300),
                             "is_mine": f"sink_name={NS}_" in verify["out"],
                             "call": run(["pactl", "unload-module", idx]) if f"sink_name={NS}_" in verify["out"] else "REFUSED: index no longer mine"})
    time.sleep(0.5)
    r["after"] = {
        "modules": sh(f"pactl list short modules | grep -cF {NS} || true"),
        "dump_nodes": sh(f"pw-dump | grep -cF '{NS}_' || true"),
        "procs": sh(f"pgrep -f {NS} | wc -l"),
        "metadata_keys": sh(f"pw-metadata -n default | grep -cF '{NS}_' || true"),
        "pactl_default_sink": run(["pactl", "get-default-sink"]),
        "pactl_default_source": run(["pactl", "get-default-source"]),
        "hogs_mine": sh(f"pgrep -f 'r86b_hog' | wc -l"),
    }
    r["core_count"] = sh("coredumpctl list --no-pager 2>/dev/null | wc -l")
    save("clean", r)


if __name__ == "__main__":
    stages = sys.argv[1:] or ["b0"]
    for s in stages:
        print(f"=== {s} ===")
        {"b0": stage_b0, "b0b": stage_b0b, "b1": stage_b1, "b2": stage_b2, "b3": stage_b3,
         "b2b": stage_b2b, "b4": stage_b4, "b4b": stage_b4b, "b5": stage_b5, "b6": stage_b6, "clean": stage_clean}[s]()
