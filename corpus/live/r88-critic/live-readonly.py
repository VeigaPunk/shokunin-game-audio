#!/usr/bin/env python3
"""r88 critic — bounded READ-ONLY live corroboration.

No object is created, loaded, unloaded, linked or destroyed; no
set-default-*; no stream is spawned. Every command is a read verb
(busctl get-property/tree, pactl list/get, pw-dump, pw-cli info/ls,
pw-top -b bounded, ls/find/strings). Each spawn is timeout-bounded;
the infinite pw-top forms are killed by process group.

The frozen probeParent's one read-only labrat returned STILL NO EXEC
(recorded as unavailability, not absence), so the dispatcher ran this
battery directly.
"""
import json
import os
import re
import signal
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = {"commands": [], "checks": {}}


def run(argv, timeout_s=20.0, stdin_data=None):
    t0 = time.monotonic()
    try:
        p = subprocess.Popen(argv, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdin=(subprocess.PIPE if stdin_data
                                    else subprocess.DEVNULL),
                             start_new_session=True)
    except OSError as exc:
        return {"argv": argv, "spawn_error": str(exc)}
    killed = False
    try:
        out, err = p.communicate(input=stdin_data, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        killed = True
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
    rec = {"argv": argv, "rc": p.returncode, "killed_at_bound": killed,
           "wall_s": round(time.monotonic() - t0, 3),
           "stdout": out.decode(errors="replace"),
           "stderr": err.decode(errors="replace")}
    OUT["commands"].append({k: (v if k not in ("stdout", "stderr")
                                else v[:4000]) for k, v in rec.items()})
    return rec


def j(argv, timeout_s=20.0):
    r = run(argv, timeout_s)
    try:
        r["json"] = json.loads(r["stdout"])
    except ValueError:
        r["json"] = None
    return r


def census():
    return j(["pw-dump"], 25.0)


C = census()
objs = C["json"] or []


def props(o):
    return (o.get("info") or {}).get("props") or {}


def oid(o):
    return str(o.get("id"))


# ---------------- 1. bluez absence surface ----------------
OUT["checks"]["bluez"] = {}
tree = run(["busctl", "--system", "tree", "org.bluez"], 15)
devs = sorted(set(re.findall(r"(/org/bluez/hci\d+/dev_[0-9A-Fa-f_]+)",
                             tree["stdout"])))
adapters = sorted(set(re.findall(r"(/org/bluez/hci\d+)", tree["stdout"])))
OUT["checks"]["bluez"]["tree"] = {"adapters": adapters, "devices": devs}
if adapters:
    a = adapters[0]
    OUT["checks"]["bluez"]["powered"] = run(
        ["busctl", "--system", "get-property", "org.bluez", a,
         "org.bluez.Adapter1", "Powered"], 10)["stdout"].strip()
    OUT["checks"]["bluez"]["media1_uuids"] = run(
        ["busctl", "--system", "get-property", "org.bluez", a,
         "org.bluez.Media1", "SupportedUUIDs"], 10)["stdout"].strip()
for d in devs:
    rec = {}
    for prop in ("UUIDs", "Class", "Icon", "Connected", "Paired"):
        rec[prop] = run(["busctl", "--system", "get-property",
                         "org.bluez", d, "org.bluez.Device1", prop],
                        10)["stdout"].strip()
    rec["uuid16"] = sorted(u.lower() for u in re.findall(
        r'"0000([0-9a-fA-F]{4})-', rec["UUIDs"]))
    OUT["checks"]["bluez"].setdefault("devices", {})[d] = rec
pl = run(["pactl", "list"], 20)
bluez_lines = [ln.strip() for ln in pl["stdout"].splitlines()
               if re.search(r"bluez|a2dp|sco", ln, re.I)]
OUT["checks"]["bluez"]["pactl_bluez_lines"] = bluez_lines
cards = run(["pactl", "list", "cards", "short"], 15)["stdout"]
sinks = run(["pactl", "list", "sinks", "short"], 15)["stdout"]
OUT["checks"]["bluez"]["pactl_cards_bluez"] = [
    ln for ln in cards.splitlines() if re.search("bluez", ln, re.I)]
OUT["checks"]["bluez"]["pactl_sinks_bluez"] = [
    ln for ln in sinks.splitlines() if re.search("bluez", ln, re.I)]
spa = run(["ls", "/usr/lib/spa-0.2/bluez5/"], 10)
OUT["checks"]["bluez"]["spa_files"] = sorted(
    f for f in spa["stdout"].splitlines() if f.strip())
st = run(["strings", "-a", "/usr/lib/spa-0.2/bluez5/libspa-bluez5.so"], 60)
lines = st["stdout"].splitlines()
OUT["checks"]["bluez"]["codecs_strings"] = {
    "substring_hits": sorted({ln.strip() for ln in lines
                              if "bluez5.codecs" in ln}),
    "standalone_lines": sum(1 for ln in lines
                            if ln.strip() == "bluez5.codecs"),
    "bluez5_names": sum(1 for ln in set(lines) if "bluez5." in ln)}
OUT["checks"]["bluez"]["module_files"] = [
    ln for ln in run(["find", "/usr/lib", "/usr/lib64", "-name",
                      "*module-bluez5*"], 30)["stdout"].splitlines()
    if ln.strip()]
bluez_objs = [{"id": oid(o), "name": props(o).get("node.name"),
               "media_class": props(o).get("media.class"),
               "factory": props(o).get("factory.name")}
              for o in objs
              if str(props(o).get("device.api")) == "bluez5"
              or str(props(o).get("factory.name") or "").startswith(
                  "api.bluez5")]
OUT["checks"]["bluez"]["graph_bluez_objects"] = bluez_objs
OUT["checks"]["bluez"]["graph_audio_bluez"] = [
    x for x in bluez_objs
    if str(x.get("media_class") or "").startswith("Audio/")]

# ---------------- 2. the {id u serial} set rule ----------------
OUT["checks"]["setrule"] = {}
node = next((o for o in objs if str(o.get("type", "")).endswith("Node")
             and str(props(o).get("node.name") or "")), None)
node2 = next((o for o in objs if str(o.get("type", "")).endswith("Node")
              and o is not node), None)
if node is not None:
    nid, nser = oid(node), str(props(node).get("object.serial"))
    pred = sorted({oid(o) for o in objs
                   if oid(o) == nid
                   or str(props(o).get("object.serial")) == nser})
    for label, argv in (("id", ["pw-dump", nid]),
                        ("serial", ["pw-dump", nser]),
                        ("mode_R", ["pw-dump", "-R", nid]),
                        ("mode_i0", ["pw-dump", "-i", "0", nid])):
        r = j(argv, 20)
        got = sorted(str(o.get("id")) for o in (r["json"] or []))
        ports = sum(1 for o in (r["json"] or [])
                    if str(o.get("type", "")).endswith("Port"))
        OUT["checks"]["setrule"][label] = {
            "argv": argv, "got": got, "predicted": pred,
            "ports": ports, "match": got == pred}
    if node2 is not None:
        r = j(["pw-dump", nid, oid(node2)], 20)
        OUT["checks"]["setrule"]["two_args"] = {
            "argv": ["pw-dump", nid, oid(node2)],
            "ids": sorted(str(o.get("id")) for o in (r["json"] or []))}
    r = run(["pw-dump", "-s", nid], 20)
    OUT["checks"]["setrule"]["spa_form"] = {
        "has_id": f"id = {nid}" in r["stdout"],
        "has_serial": f"object.serial = {nser}" in r["stdout"]}
    OUT["checks"]["setrule"]["node"] = {"id": nid, "serial": nser}

# ---------------- 3. metadata split (ls ⊋ dump) ----------------
dump_meta = sorted(oid(o) for o in objs
                   if str(o.get("type", "")).endswith("Metadata"))
ls = run(["pw-cli", "ls", "Metadata"], 15)
ls_ids = sorted(int(m.group(1)) for m in
                re.finditer(r"^[ \t]*id (\d+),", ls["stdout"], re.M))
OUT["checks"]["metadata_split"] = {
    "dump": dump_meta, "ls": [str(i) for i in ls_ids],
    "extra": sorted(set(ls_ids) - set(int(i) for i in dump_meta)),
    "ls_superset": set(int(i) for i in dump_meta) <= set(ls_ids)}
if ls_ids:
    extra0 = sorted(set(ls_ids) - set(int(i) for i in dump_meta))
    if extra0:
        r = run(["pw-cli", "info", str(extra0[0])], 15)
        OUT["checks"]["metadata_split"]["info_on_ls_only"] = {
            "argv": ["pw-cli", "info", str(extra0[0])], "rc": r["rc"],
            "stdout": r["stdout"][:200], "stderr": r["stderr"][:200]}
ia = run(["pw-cli", "info", "all"], 40)
described = sorted(set(re.findall(r"^\tid: (\d+)", ia["stdout"], re.M)))
OUT["checks"]["metadata_split"]["info_all"] = {
    "described": len(described),
    "census": len(objs),
    "metadata_described": sorted(i for i in dump_meta
                                 if i in described)}

# ---------------- 4. pactl index == object.serial ----------------
name_serial = {str(props(o).get("node.name")): str(
    props(o).get("object.serial")) for o in objs
    if str(o.get("type", "")).endswith("Node")}
matched, viol, unmatched = [], [], []
for ln in sinks.splitlines():
    f = ln.split("\t")
    if len(f) >= 2 and f[0].strip().isdigit():
        idx, nm = int(f[0].strip()), f[1].strip()
        ser = name_serial.get(nm)
        if ser is None:
            unmatched.append(nm)
        elif str(idx) == ser:
            matched.append(nm)
        else:
            viol.append({"name": nm, "index": idx, "serial": ser})
OUT["checks"]["serial_law"] = {"matched": matched,
                               "violations": viol,
                               "unmatched": unmatched}

# ---------------- 5. pw-top traps ----------------
OUT["checks"]["pwtop"] = {}


def frames(text):
    fr, cur = [], None
    for ln in (text or "").splitlines():
        if re.match(r"^S\s+ID\s+QUANT", ln):
            cur = []
            fr.append(cur)
            continue
        m = re.match(r"^([A-Za-z])\s+(\d+)\s", ln)
        if cur is not None and m:
            cur.append({"status": m.group(1), "id": int(m.group(2))})
    return fr


r = run(["pw-top", "-b", "-n", "1"], 15)
f1 = frames(r["stdout"])
OUT["checks"]["pwtop"]["n1"] = {
    "frames": [len(x) for x in f1],
    "status_sets": [sorted({y["status"] for y in x}) for x in f1]}
r = run(["pw-top", "-b", "-n", "3"], 20)
f3 = frames(r["stdout"])
OUT["checks"]["pwtop"]["n3"] = {
    "frames": [len(x) for x in f3],
    "status_sets": [sorted({y["status"] for y in x}) for x in f3],
    "last_frame_hist": (sorted({y["status"]: sum(
        1 for z in f3[-1] if z["status"] == y["status"])
        for y in f3[-1]}.items()) if f3 else None)}
r = run(["pw-top", "-b", "-n", "0"], 15)
f0 = frames(r["stdout"])
OUT["checks"]["pwtop"]["n0"] = {"frames": [len(x) for x in f0]}
r = run(["pw-top", "-b", "-n", "-1"], 4.0)
OUT["checks"]["pwtop"]["nneg"] = {
    "killed": r["killed_at_bound"], "rc": r["rc"],
    "frames": [len(x) for x in frames(r["stdout"])]}
r = run(["pw-top", "-b", "-n", "abc"], 4.0)
OUT["checks"]["pwtop"]["nabc"] = {
    "killed": r["killed_at_bound"], "rc": r["rc"],
    "frames": [len(x) for x in frames(r["stdout"])]}
r = run(["pw-top", "-r", "r88a-critic-bogus"], 15)
OUT["checks"]["pwtop"]["rbogus"] = {"rc": r["rc"],
                                    "stderr": r["stderr"][:200]}

# ---------------- 6. silent absences + misc ----------------
OUT["checks"]["silent"] = {}
for label, argv in (("dead_id", ["pw-dump", "98765432"]),
                    ("abc", ["pw-dump", "abc"]),
                    ("huge", ["pw-dump", "99999999999999999999"])):
    r = run(argv, 15)
    OUT["checks"]["silent"][label] = {
        "rc": r["rc"], "stdout_empty": not r["stdout"].strip(),
        "stderr_empty": not r["stderr"].strip()}
r = j(["pw-dump", ""], 30)
OUT["checks"]["silent"]["empty_arg"] = {
    "rc": r["rc"], "ids": sorted(str(o.get("id"))
                                 for o in (r["json"] or []))[:8],
    "count": len(r["json"] or []), "census_count": len(objs)}
r = run(["pw-dump", "-1"], 15)
OUT["checks"]["silent"]["neg1"] = {
    "rc": r["rc"], "stderr": r["stderr"][:200]}
r = run(["pw-cli", "info", "98765432"], 15)
OUT["checks"]["silent"]["cli_dead"] = {
    "rc": r["rc"], "stderr": r["stderr"][:120],
    "stdout_empty": not r["stdout"].strip()}
r = run(["pw-cli", "ls", "Node"], 15)
has_serial = bool(re.search(r'object.serial = "\d+"', r["stdout"]))
OUT["checks"]["silent"]["cli_ls_node_serial"] = has_serial
r = run(["pw-cli", "enum-params", "98765432", "Format"], 15)
OUT["checks"]["silent"]["enum_dead"] = {
    "rc": r["rc"], "stdout_empty": not r["stdout"].strip(),
    "stderr": r["stderr"][:120]}

# ---------------- 7. idle state vocab (no stream spawned) ----------
sink0 = next((o for o in objs if str(o.get("type", "")).endswith("Node")
              and str(props(o).get("media.class")) == "Audio/Sink"), None)
if sink0 is not None:
    sid = oid(sink0)
    st_dump = None
    r = j(["pw-cli", "info", sid], 15)
    m = re.search(r'state: "([a-z]+)"', r["stdout"])
    st_cli = m.group(1) if m else None
    st_pactl = None
    for ln in sinks.splitlines():
        f = ln.split("\t")
        if len(f) >= 3 and f[1].strip() == str(props(sink0).get("node.name")):
            st_pactl = f[-1].strip()
    st_top = None
    if f3:
        row = next((x for x in f3[-1] if x["id"] == int(sid)), None)
        st_top = (row or {}).get("status")
    # dump state from the census itself
    st_dump = props(sink0).get("node.state") or None
    if st_dump is None:
        # node.state lives in info.state for pw-dump
        st_dump = (sink0.get("info") or {}).get("state")
    vocab = {"pactl": st_pactl, "dump": st_dump, "cli": st_cli,
             "top": st_top}
    OUT["checks"]["state_vocab_idle"] = vocab

with open(os.path.join(HERE, "live-readonly.json"), "w") as f:
    json.dump(OUT, f, indent=2, sort_keys=True, default=str)

# compact human summary
print("bluez:",
      json.dumps({k: v for k, v in OUT["checks"]["bluez"].items()
                  if k != "pactl_bluez_lines"}, indent=1)[:1200])
print("pactl bluez lines:", OUT["checks"]["bluez"]["pactl_bluez_lines"])
print("setrule:", json.dumps(OUT["checks"]["setrule"], indent=1))
print("metadata split:", json.dumps(
    OUT["checks"]["metadata_split"], indent=1)[:800])
print("serial law:", json.dumps(OUT["checks"]["serial_law"], indent=1))
print("pwtop:", json.dumps(OUT["checks"]["pwtop"], indent=1))
print("silent:", json.dumps(OUT["checks"]["silent"], indent=1))
print("state idle:", OUT["checks"].get("state_vocab_idle"))
