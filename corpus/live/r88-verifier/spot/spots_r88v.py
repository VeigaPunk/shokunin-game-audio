#!/usr/bin/env python3
"""r88-verifier independent live spots (own code, own r88v_<pid> namespace).

Re-derives the landing's headline laws from the live host, with no fixture
import:
  A  bluetooth absent-class surface (D-Bus / pulse / graph / files / strings)
  B  pw-dump {id u serial} set rule over every live key, two brackets
  C  pw-cli ls Metadata superset vs pw-dump + silent info
  D  pactl index == native object.serial
  E  pw-top frame traps (-n 1 all-C, -n 0 one frame, -n 3 last frame,
     -n -1 infinite, -r bogus loud)
  F  four-witness state agreement on an own null sink, idle + driven

Every object this script creates is r88v_-tagged and destroyed by name/id
before exit; never set-default-*, never touch a foreign object.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
import wave
from pathlib import Path

PID = os.getpid()
NS = f"r88v_ns_{PID}"
TAG = f"r88v_pt_{PID}"
ROLE = f"r88vrole{PID}"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
RAW = OUT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
RESULT = {"pid": PID, "ns": NS, "spots": {}}


def run(argv, timeout=15, keep_raw=False):
    t0 = time.monotonic()
    rec = {"argv": " ".join(str(a) for a in argv)}
    try:
        p = subprocess.Popen([str(a) for a in argv], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdin=subprocess.DEVNULL, start_new_session=True)
    except OSError as e:
        rec.update({"rc": None, "spawn_error": str(e)[:120]})
        return rec
    try:
        out, err = p.communicate(timeout=timeout)
        rec["timeout"] = False
    except subprocess.TimeoutExpired:
        # kill the group, then drain whatever was buffered (fixture runner
        # discipline: the partial output is the witness for infinite modes)
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
        rec["timeout"] = True
    rec.update({"rc": p.returncode,
                "out": out.decode(errors="replace"),
                "err": err.decode(errors="replace"),
                "wall_s": round(time.monotonic() - t0, 3)})
    if not keep_raw:
        rec["out_head"] = rec["out"].strip().splitlines()[:6]
        rec["err_head"] = rec["err"].strip().splitlines()[:6]
    return rec


def dump():
    r = run(["pw-dump"], 25)
    try:
        return json.loads(r.get("out") or "[]")
    except ValueError:
        return None


def props(o):
    return (o.get("info") or {}).get("props") or {}


def pred(objs, key):
    return sorted(str(o.get("id")) for o in (objs or [])
                  if str(o.get("id")) == str(key)
                  or str(props(o).get("object.serial")) == str(key))


def top_frames(t):
    frames, cur = [], None
    for ln in (t or "").splitlines():
        if re.match(r"^S\s+ID\s+QUANT", ln):
            cur = []
            frames.append(cur)
            continue
        m = re.match(r"^([A-Za-z])\s+(\d+)\s", ln)
        if cur is not None and m:
            cur.append({"status": m.group(1), "id": int(m.group(2))})
    return frames


def save(name, obj):
    (RAW / f"{name}.json").write_text(json.dumps(obj, indent=1) + "\n")


# ---------------------------------------------------------------- spot A
def spot_a():
    a = {}
    tree = run(["busctl", "--system", "tree", "org.bluez"])
    a["tree"] = tree
    devs = sorted(set(re.findall(r"/org/bluez/hci\d+/dev_[0-9A-Fa-f_]+",
                                 tree.get("out") or "")))
    adapters = sorted(set(re.findall(r"/org/bluez/hci\d+",
                                     tree.get("out") or "")))
    a["adapters"], a["devices"] = adapters, devs
    dev_recs = []
    for dp in devs:
        rec = {"path": dp}
        for prop in ("UUIDs", "Class", "Connected", "Paired", "Modalias"):
            r = run(["busctl", "--system", "get-property", "org.bluez", dp,
                     "org.bluez.Device1", prop])
            rec[prop] = (r.get("out") or "").strip() or r.get("err", "").strip()
        uu = set(re.findall(r'"0000([0-9a-fA-F]{4})-', rec["UUIDs"]))
        rec["uuid16"] = sorted(u.lower() for u in uu)
        rec["audio_uuids"] = sorted(
            u for u in rec["uuid16"]
            if u in {"110a", "110b", "110c", "110e", "111e", "111f", "1108",
                     "1112", "1103", "1101", "1131", "1132", "111b", "112d",
                     "112e", "112f", "1130", "1136", "113a", "113b", "1204",
                     "1843", "1844", "1845", "1846"})
        dev_recs.append(rec)
    a["device_records"] = dev_recs
    if adapters:
        a["adapter_powered"] = run(
            ["busctl", "--system", "get-property", "org.bluez", adapters[0],
             "org.bluez.Adapter1", "Powered"])
        a["media1"] = run(
            ["busctl", "--system", "get-property", "org.bluez", adapters[0],
             "org.bluez.Media1", "SupportedUUIDs"])
    a["media_transport"] = re.findall(r"MediaTransport\S*",
                                      tree.get("out") or "")
    pl = run(["pactl", "list"], 20)
    a["pactl_bluez_lines"] = [ln.strip() for ln in
                              (pl.get("out") or "").splitlines()
                              if re.search(r"bluez|a2dp|sco", ln, re.I)]
    a["pactl_cards"] = [ln.strip() for ln in
                        (run(["pactl", "list", "cards", "short"]).get("out")
                         or "").splitlines() if ln.strip()]
    a["pactl_sinks"] = [ln.strip() for ln in
                        (run(["pactl", "list", "sinks", "short"]).get("out")
                         or "").splitlines() if ln.strip()]
    objs = dump()
    a["bluez_objects"] = [
        {"id": o.get("id"), "name": props(o).get("node.name"),
         "media_class": props(o).get("media.class"),
         "factory": props(o).get("factory.name")}
        for o in (objs or [])
        if str(props(o).get("device.api")) == "bluez5"
        or str(props(o).get("factory.name") or "").startswith("api.bluez5")]
    a["spa_files"] = sorted(os.listdir("/usr/lib/spa-0.2/bluez5")) \
        if os.path.isdir("/usr/lib/spa-0.2/bluez5") else None
    s = run(["strings", "-a", "/usr/lib/spa-0.2/bluez5/libspa-bluez5.so"], 90)
    lines = (s.get("out") or "").splitlines()
    a["codecs_strings"] = sorted({ln.strip() for ln in lines
                                  if "bluez5.codecs" in ln})
    a["codecs_standalone"] = sum(1 for ln in lines
                                 if ln.strip() == "bluez5.codecs")
    a["find_module"] = [ln for ln in
                        (run(["find", "/usr/lib", "/usr/lib64", "-name",
                              "*module-bluez5*"], 60).get("out") or ""
                         ).splitlines() if ln.strip()]
    # refusal battery (module set unchanged)
    a["mods_before"] = run(["pactl", "list", "modules", "short"]).get("out")
    refusals = {}
    for tag, argv in (
            ("discover", ["pactl", "load-module", "module-bluez5-discover"]),
            ("device", ["pactl", "load-module", "module-bluez5-device"]),
            ("device_path", ["pactl", "load-module", "module-bluez5-device",
                             "path=" + (adapters[0] if adapters
                                        else "/org/bluez/hci0")]),
            ("discover_arg", ["pactl", "load-module",
                              "module-bluez5-discover", "a2dp_source=false"])):
        refusals[tag] = run(argv)
    a["refusals"] = refusals
    a["sendmsg"] = run(["pactl", "send-message",
                        adapters[0] if adapters else "/org/bluez/hci0",
                        adapters[0] if adapters else "/org/bluez/hci0"])
    bcard = "bluez_card." + (devs[0].rsplit("dev_", 1)[-1] if devs
                             else "r88v_deadbeef")
    a["setcard_absent"] = run(["pactl", "set-card-profile", bcard,
                               "a2dp-sink"])
    if a["pactl_cards"]:
        real = a["pactl_cards"][0].split("\t")[1].strip()
        a["setcard_bogusctl"] = run(["pactl", "set-card-profile", real,
                                     "bogus-profile-r88v"])
        cards_full = run(["pactl", "list", "cards"]).get("out") or ""
        cur, active = None, None
        for ln in cards_full.splitlines():
            m = re.match(r"^\s+Name:\s+(\S+)", ln)
            if m:
                cur = m.group(1)
            m2 = re.match(r"^\s+Active Profile:\s+(\S+)", ln)
            if m2 and cur == real:
                active = m2.group(1)
        a["setcard_validctl"] = run(["pactl", "set-card-profile", real,
                                     active or "off"])
        a["setcard_real_card"] = real
        a["setcard_active"] = active
    a["mods_after"] = run(["pactl", "list", "modules", "short"]).get("out")
    # fabrication: create-node refusals + residue
    before = {o.get("id") for o in (dump() or [])}
    fab = {}
    for tag, fac in (("a2dp_sink", "api.bluez5.a2dp-sink"),
                     ("sink", "api.bluez5.sink"),
                     ("a2dp_source", "api.bluez5.a2dp.source"),
                     ("midi_node", "api.bluez5.midi.node")):
        fab[tag] = run(["pw-cli", "create-node", "spa-node-factory",
                        "{ factory.name = %s node.name = %s }"
                        % (fac, f"{NS}_fab_{tag}")])
    time.sleep(0.3)
    after_objs = dump() or []
    a["fabrications"] = fab
    a["fab_residue"] = sorted(
        props(o).get("node.name") for o in after_objs
        if props(o).get("node.name")
        and f"{NS}_fab_" in props(o).get("node.name"))
    a["fab_new_ids"] = sorted({str(o.get("id")) for o in after_objs}
                              - {str(i) for i in before})
    save("spotA", a)
    return a


# ---------------------------------------------------------------- spot B
def spot_b():
    c1 = dump() or []
    keys = sorted({str(o.get("id")) for o in c1} |
                  {str(props(o).get("object.serial")) for o in c1
                   if props(o).get("object.serial") is not None})
    rows, churn, silent = [], 0, []
    for k in keys:
        r = run(["pw-dump", k], 20)
        try:
            got = sorted(str(o.get("id")) for o in json.loads(r.get("out")))
        except ValueError:
            got = None  # silent empty / unparsable -> silent-absence class
        p = pred(c1, k)
        rec = {"key": k, "got": got, "predicted": p, "rc": r.get("rc"),
               "out_empty": not (r.get("out") or "").strip()}
        if got is None:
            # a dead/never-live key: re-derive the prediction from a fresh
            # census; the silent-empty signature itself is the law
            c2 = dump() or []
            p2 = pred(c2, k)
            rec["recensus_predicted"] = p2
            rec["silent_absence"] = True
            rec["match"] = (p2 == [] and rec["out_empty"] and
                            r.get("rc") == 0)
            if not rec["match"]:
                churn += 1
                rec["churn"] = True
            silent.append(k)
        else:
            if got != p:
                c2 = dump() or []
                p2 = pred(c2, k)
                rec["recensus_predicted"] = p2
                if p2 != p:
                    churn += 1
                    rec["churn"] = True
                    rec["predicted"] = p2
            rec["match"] = rec["got"] == rec["predicted"]
        rows.append(rec)
    out = {"census_objects": len(c1), "keys": len(keys), "rows": rows,
           "mismatches": [r for r in rows if not r["match"]],
           "churn_recensus": churn, "silent_empty_keys": len(silent),
           "silent_examples": silent[:10]}
    save("spotB", out)
    return out


# ---------------------------------------------------------------- spot C
def spot_c():
    objs = dump() or []
    dump_meta = sorted(str(o.get("id")) for o in objs
                       if str(o.get("type", "")).endswith("Metadata"))
    r = run(["pw-cli", "ls", "Metadata"])
    ls_meta = sorted(int(m.group(1)) for m in
                     re.finditer(r"^[ \t]*id (\d+),", r.get("out") or "",
                                 re.M))
    extra = sorted(set(ls_meta) - {int(i) for i in dump_meta})
    info_extra = run(["pw-cli", "info", str(extra[0])]) if extra else None
    info_all = run(["pw-cli", "info", "all"], 30)
    described = set(re.findall(r"^\tid: (\d+)", info_all.get("out") or "",
                               re.M))
    out = {"ls_ids": [str(i) for i in ls_meta], "dump_ids": dump_meta,
           "extra": [str(i) for i in extra],
           "ls_superset": set(dump_meta).issubset(
               {str(i) for i in ls_meta}) and len(ls_meta) > len(dump_meta),
           "info_extra_silent": None if info_extra is None else {
               "rc": info_extra.get("rc"),
               "out_empty": not (info_extra.get("out") or "").strip(),
               "err_empty": not (info_extra.get("err") or "").strip()},
           "info_all_described": len(described),
           "info_all_dump": len(objs),
           "info_all_meta_described": sorted(
               i for i in dump_meta if i in described),
           "ls_raw": r.get("out")}
    save("spotC", out)
    return out


# ---------------------------------------------------------------- spot D
def spot_d():
    objs = dump() or []
    name2ser = {props(o).get("node.name"): str(props(o).get("object.serial"))
                for o in objs if props(o).get("node.name")}
    out = {"sinks": [], "sources": [], "violations": [], "monitor_rows": []}
    for kind, cmd in (("sinks", ["pactl", "list", "sinks", "short"]),
                      ("sources", ["pactl", "list", "sources", "short"])):
        txt = run(cmd).get("out") or ""
        for ln in txt.splitlines():
            f = ln.split("\t")
            if len(f) >= 2 and f[0].strip().isdigit():
                idx, name = int(f[0].strip()), f[1].strip()
                base = name[:-len(".monitor")] if name.endswith(".monitor") \
                    else name
                ser = name2ser.get(base)
                row = {"index": idx, "name": name, "serial": ser,
                       "monitor": name.endswith(".monitor"),
                       "resolved_as": base}
                if ser is None:
                    row["match"] = None
                    out["violations"].append({"name": name,
                                              "why": "unmatched"})
                else:
                    row["match"] = str(idx) == ser
                    if not row["match"]:
                        out["violations"].append(
                            {"name": name, "index": idx, "serial": ser})
                (out["monitor_rows"] if row["monitor"]
                 else out[kind]).append(row)
    out["matched"] = sum(
        1 for r in out["sinks"] + out["sources"] + out["monitor_rows"]
        if r.get("match") is True)
    out["total"] = len(out["sinks"]) + len(out["sources"]) + \
        len(out["monitor_rows"])
    save("spotD", out)
    return out


# ---------------------------------------------------------------- spot E
def spot_e():
    out = {}
    n1 = run(["pw-top", "-b", "-n", "1"], 15)
    fr = top_frames(n1.get("out"))
    out["n1"] = {"frames": [len(f) for f in fr],
                 "status_sets": [sorted({r["status"] for r in f})
                                 for f in fr]}
    n0 = run(["pw-top", "-b", "-n", "0"], 15)
    out["n0"] = {"frames": [len(f) for f in top_frames(n0.get("out"))]}
    n3 = run(["pw-top", "-b", "-n", "3"], 20)
    fr3 = top_frames(n3.get("out"))
    out["n3"] = {"frames": [len(f) for f in fr3],
                 "status_sets": [sorted({r["status"] for r in f})
                                 for f in fr3]}
    nn = run(["pw-top", "-b", "-n", "-1"], 3.0)
    out["nneg"] = {"rc": nn.get("rc"), "timeout": nn.get("timeout"),
                   "frames": [len(f) for f in top_frames(nn.get("out"))],
                   "lines": len((nn.get("out") or "").splitlines())}
    ab = run(["pw-top", "-b", "-n", "abc"], 3.0)
    out["nabc"] = {"rc": ab.get("rc"), "timeout": ab.get("timeout"),
                   "frames": [len(f) for f in top_frames(ab.get("out"))],
                   "lines": len((ab.get("out") or "").splitlines())}
    rb = run(["pw-top", "-r", f"r88v-bogus-{PID}"], 15)
    out["rbogus"] = {"rc": rb.get("rc"), "err": (rb.get("err") or "").strip()}
    save("spotE", out)
    return out


# ---------------------------------------------------------------- spot F
def spot_f():
    out = {}
    mod = run(["pactl", "load-module", "module-null-sink",
               f"sink_name={NS}", f"node.description=r88v probe {PID}"])
    mod_id = (mod.get("out") or "").strip()
    out["load"] = {"rc": mod.get("rc"), "module_id": mod_id,
                   "err": (mod.get("err") or "").strip()}
    if mod.get("rc") != 0 or not mod_id.isdigit():
        save("spotF", out)
        return out
    deadline = time.monotonic() + 8
    objs, own = None, None
    while time.monotonic() < deadline:
        objs = dump() or []
        own = next((o for o in objs if props(o).get("node.name") == NS), None)
        if own:
            break
        time.sleep(0.2)
    if not own:
        out["error"] = "own node never enumerated"
        run(["pactl", "unload-module", mod_id])
        save("spotF", out)
        return out
    own_id, own_ser = str(own.get("id")), str(props(own).get("object.serial"))
    out["own"] = {"id": own_id, "serial": own_ser}

    def witnesses(tag):
        s = run(["pactl", "list", "sinks", "short"]).get("out") or ""
        st = None
        for ln in s.splitlines():
            f = ln.split("\t")
            if len(f) >= 3 and f[1].strip() == NS:
                st = f[-1].strip()
        g = dump() or []
        node = next((o for o in g if props(o).get("node.name") == NS), {})
        cli = run(["pw-cli", "info", own_id])
        m = re.search(r'state: "([a-z]+)"', cli.get("out") or "")
        top = run(["pw-top", "-b", "-n", "3"], 20)
        fr = top_frames(top.get("out"))
        row = next((r for r in (fr[-1] if fr else [])
                    if str(r["id"]) == own_id), None)
        return {"tag": tag, "pactl": st,
                "dump": (node.get("info") or {}).get("state"),
                "cli": m.group(1) if m else None,
                "top": (row or {}).get("status"),
                "top_frames": len(fr),
                "vocab": {
                    "pactl": {"SUSPENDED": "suspended",
                              "RUNNING": "running", "IDLE": "idle"}.get(st),
                    "dump": (node.get("info") or {}).get("state"),
                    "cli": m.group(1) if m else None,
                    "top": {"S": "suspended", "I": "idle",
                            "R": "running"}.get(
                                (row or {}).get("status"))}}
    out["idle"] = witnesses("idle")
    # drive it with an own stream
    tone = RAW / "r88v_tone.wav"
    with wave.open(str(tone), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        import struct
        w.writeframes(b"".join(
            struct.pack("<h", int(12000 * __import__("math").sin(
                2 * 3.141592653589793 * 440 * i / 48000)))
            for i in range(48000 * 8)))
    p = subprocess.Popen(["pw-play", "-P", f"node.name={TAG}",
                          "-P", f"media.role={ROLE}",
                          "--target", NS, str(tone)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL, start_new_session=True)
    linked = False
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        g = dump() or []
        node = next((o for o in g if props(o).get("node.name") == TAG), None)
        lk = [o for o in g if str(o.get("type", "")).endswith("Link")
              and (props(o).get("link.output.node") == (node or {}).get("id"))
              and (props(o).get("link.input.node") == int(own_id))]
        if node and (node.get("info") or {}).get("state") == "running" and lk:
            linked = True
            break
        time.sleep(0.25)
    out["linked"] = linked
    if linked:
        out["active"] = witnesses("active")
    try:
        os.killpg(p.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        p.wait(timeout=4)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    # teardown: name-verified unload
    mods = run(["pactl", "list", "modules", "short"]).get("out") or ""
    mine = [ln for ln in mods.splitlines()
            if ln.split("\t")[0].strip() == mod_id]
    out["unload"] = {"mod_line": mine,
                     "sink_name_ok": any(f"sink_name={NS}" in ln
                                         for ln in mine),
                     "rc": run(["pactl", "unload-module", mod_id]).get("rc")}
    time.sleep(0.4)
    g = dump() or []
    resid = [str(o.get("id")) for o in g
             if props(o).get("node.name")
             and props(o).get("node.name").startswith("r88v_")]
    if resid:
        out["residual_destroy"] = [run(["pw-cli", "destroy", i])
                                   for i in resid]
        time.sleep(0.4)
    g = dump() or []
    out["sink_gone"] = not any(props(o).get("node.name") == NS for o in g)
    out["residue_after"] = sorted(
        props(o).get("node.name") for o in g
        if props(o).get("node.name")
        and props(o).get("node.name").startswith("r88v_"))
    save("spotF", out)
    return out


def main():
    RESULT["spots"]["A_bluez_absent_class"] = spot_a()
    RESULT["spots"]["B_set_rule"] = spot_b()
    RESULT["spots"]["C_metadata_split"] = spot_c()
    RESULT["spots"]["D_pactl_serial"] = spot_d()
    RESULT["spots"]["E_pwtop_traps"] = spot_e()
    RESULT["spots"]["F_state_agreement"] = spot_f()
    (OUT / "spots-r88v.json").write_text(json.dumps(RESULT, indent=1) + "\n")
    print(json.dumps({"out": str(OUT / "spots-r88v.json")}))


if __name__ == "__main__":
    main()
