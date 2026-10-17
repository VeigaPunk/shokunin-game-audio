#!/usr/bin/env python3
"""r90 scout harness — five uncovered candidate families on PipeWire 1.6.8.

Families (stage CLI arg):
  f1  WirePlumber settings + session-manager state persistence (read-only)
  f2  pipewire-pulse module namespace edges: tunnel / zeroconf / roc / stubs
  f3  pw-v4l2 bridge (absent-class, read-only)
  f4  pw-link grammar: bulk connect/disconnect, partial failure, -w wait
  f5  EnumFormat (capability) vs Format (write-only) + mid-stream set-param
  f6  session-manager restore: stream-properties write/read/target law

Every leg is run >=3 times (reps). Raw per-step stdout/stderr land under
runs/<leg>/rep<N>/; consolidated receipts under receipts/<stage>.json.
Mutating stages (f2/f4/f5/f6) create only seat-owned objects named r90* and
tear them down by ID; census() is captured at stage entry and exit.
"""
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"
REC = ROOT / "receipts"
STATE_DIR = Path.home() / ".local/state/wireplumber"
TONE48 = ROOT / "r90_tone48.wav"
TONE441 = ROOT / "r90_tone441.wav"
STAGES = ("f1", "f2", "f3", "f4", "f5", "f6")
for d in (RUNS, REC):
    d.mkdir(parents=True, exist_ok=True)


def sha(b):
    if isinstance(b, str):
        b = b.encode()
    return hashlib.sha256(b).hexdigest()


def sh(cmd, timeout=20, env=None):
    t0 = time.monotonic_ns()
    try:
        p = subprocess.run([str(c) for c in cmd], capture_output=True,
                           timeout=timeout, env=env)
        rc, out, err, to = p.returncode, p.stdout, p.stderr, False
    except subprocess.TimeoutExpired as e:
        rc, out, err, to = None, e.stdout or b"", e.stderr or b"", True
    t1 = time.monotonic_ns()
    return {"cmd": [str(c) for c in cmd], "rc": rc, "timed_out": to,
            "out": out, "err": err, "ms": (t1 - t0) // 10**6,
            "t0": t0, "t1": t1}


def step(leg, rep, label, cmd, timeout=20, pre_sleep=0.0, keep=None):
    """Run one command of a leg and persist its raw bytes."""
    wd = RUNS / leg / f"rep{rep}"
    wd.mkdir(parents=True, exist_ok=True)
    if pre_sleep:
        time.sleep(pre_sleep)
    r = sh(cmd, timeout=timeout)
    (wd / f"{label}.cmd").write_text(" ".join(r["cmd"]) + "\n")
    (wd / f"{label}.stdout").write_bytes(r["out"])
    (wd / f"{label}.stderr").write_bytes(r["err"])
    rec = {"label": label, "cmd": r["cmd"], "rc": r["rc"],
           "timed_out": r["timed_out"], "ms": r["ms"],
           "out_sha": sha(r["out"]), "err_sha": sha(r["err"]),
           "out_len": len(r["out"]), "err_len": len(r["err"]),
           "out_head": r["out"][:1200].decode("utf-8", "replace"),
           "err_head": r["err"][:600].decode("utf-8", "replace")}
    if keep:
        rec.update(keep(r))
    return rec


def spawn(cmd, env=None):
    return subprocess.Popen([str(c) for c in cmd], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env or os.environ.copy())


def stop(p, sig=signal.SIGTERM, timeout=6):
    if p is None:
        return None
    if p.poll() is None:
        p.send_signal(sig)
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
    out, err = p.communicate()
    return {"rc": p.returncode, "out_sha": sha(out), "err_sha": sha(err),
            "err_head": err[:400].decode("utf-8", "replace")}


# ---------------------------------------------------------------- graph utils
def pw_dump():
    r = sh(["pw-dump"], timeout=30)
    try:
        return json.loads(r["out"])
    except Exception:
        return []


def nodes_by_name(name, objs=None):
    objs = pw_dump() if objs is None else objs
    return [o for o in objs if o.get("type") == "PipeWire:Interface:Node"
            and (o.get("info", {}).get("props", {}) or {}).get("node.name") == name]


def node_id(name):
    n = nodes_by_name(name)
    return n[0]["id"] if n else None


def ports_of(nodeid, objs=None):
    objs = pw_dump() if objs is None else objs
    out = []
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Port":
            continue
        pr = o.get("info", {}).get("props", {}) or {}
        if pr.get("node.id") == nodeid:
            out.append({"id": o["id"], "name": pr.get("port.name"),
                        "dir": pr.get("port.direction"),
                        "serial": o.get("info", {}).get("props", {}).get("object.serial")})
    return out


def module_ids():
    r = sh(["pactl", "list", "modules", "short"])
    ids = set()
    for line in r["out"].decode().splitlines():
        tok = line.split("\t")[0].strip()
        if tok.isdigit():
            ids.add(int(tok))
    return sorted(ids)


def census():
    objs = pw_dump()
    return {
        "modules": module_ids(),
        "r90_nodes": sorted((o.get("info", {}).get("props", {}) or {}).get("node.name")
                            for o in objs if o.get("type") == "PipeWire:Interface:Node"
                            and str((o.get("info", {}).get("props", {}) or {})
                                    .get("node.name", "")).startswith("r90")),
        "sibling_nodes": sorted(set(str((o.get("info", {}).get("props", {}) or {}).get("node.name"))
                                    for o in objs if o.get("type") == "PipeWire:Interface:Node"
                                    and re.match(r"r\d\d", str((o.get("info", {}).get("props", {}) or {})
                                                              .get("node.name", ""))) and
                                    not str((o.get("info", {}).get("props", {}) or {})
                                            .get("node.name", "")).startswith("r90"))),
        "clients": len([o for o in objs if o.get("type") == "PipeWire:Interface:Client"]),
    }


def load_null_sink(name):
    r = sh(["pactl", "load-module", "module-null-sink", f"sink_name={name}"])
    mid = None
    txt = (r["out"] + r["err"]).decode("utf-8", "replace").strip()
    if r["rc"] == 0 and txt.isdigit():
        mid = int(txt)
    return mid, r, txt


def unload(mid):
    r = sh(["pactl", "unload-module", str(mid)])
    return {"cmd": r["cmd"], "rc": r["rc"], "err": r["err"].decode()[:200]}


def tone(path, rate, secs=3.0, freq=440.0):
    if path.exists():
        return
    import math
    import struct
    n = int(rate * secs)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(n):
            v = int(12000 * math.sin(2 * math.pi * freq * i / rate))
            frames += struct.pack("<hh", v, v)
        w.writeframes(bytes(frames))


def parse_settings(text):
    out = {}
    cur = {}
    for line in text.splitlines():
        line = line.rstrip()
        m = re.match(r"^- Id: (\S+)", line)
        if m:
            cur = {"id": m.group(1)}
            out[m.group(1)] = cur
            continue
        m = re.match(r"^\s+(Name|Desc|Type|Default|Value): (.*)$", line)
        if m and cur:
            cur[m.group(1).lower()] = m.group(2)
    return out


def parse_stream_props():
    p = STATE_DIR / "stream-properties"
    raw = p.read_bytes()
    entries, keys = {}, []
    for line in raw.decode("utf-8", "replace").splitlines():
        if line.startswith("[") or not line.strip():
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        keys.append(k)
        try:
            entries[k] = json.loads(v)
        except Exception:
            entries[k] = {"_raw": v[:200]}
    valkeys = {}
    for v in entries.values():
        if isinstance(v, dict):
            for kk in v:
                valkeys[kk] = valkeys.get(kk, 0) + 1
    return {"path": str(p), "size": len(raw), "sha256": sha(raw),
            "mtime": p.stat().st_mtime, "n_entries": len(entries),
            "entries": entries, "key_shapes": sorted(set(
                re.sub(r":[^:]+$", ":<VAL>", k) for k in keys)),
            "value_keys": valkeys}


# ---------------------------------------------------------------- stage f1
def stage_f1(rep):
    res = {}
    res["s1_settings"] = step("f1_s1_settings", rep, "wpctl_settings",
                              ["wpctl", "settings"])
    res["s2_settings_help"] = step("f1_s2_settings_help", rep, "wpctl_settings_h",
                                   ["wpctl", "settings", "-h"])
    res["s3_state_ls"] = step("f1_s3_state_ls", rep, "ls_state",
                              ["ls", "-la", str(STATE_DIR)])
    res["s4_default_nodes"] = step("f1_s4_default_nodes", rep, "cat",
                                   ["cat", str(STATE_DIR / "default-nodes")])
    res["s5_journal"] = step("f1_s5_journal", rep, "journal",
                             ["journalctl", "--user", "-u", "wireplumber",
                              "--since", "-2h", "--no-pager"], timeout=20)
    res["s6_state_witness"] = step(
        "f1_s6_state_witness", rep, "grep_state",
        ["bash", "-c", "grep -rn 'State (\"' /usr/share/wireplumber/scripts/ | sort"])
    res["s7_settings_module"] = step(
        "f1_s7_settings_module", rep, "strings",
        ["bash", "-c", "strings -a /usr/lib/wireplumber-0.5/libwireplumber-module-settings.so "
                       "| grep -iE 'persistent|sm-settings|state' | sort -u"])
    res["s8_pulse_conf"] = step(
        "f1_s8_pulse_conf", rep, "pulse_conf",
        ["bash", "-c", "sed -n '66,90p' /usr/share/pipewire/pipewire-pulse.conf"])
    # parsed summaries
    s = parse_settings(res["s1_settings"]["out_head"] if False else
                       (RUNS / "f1_s1_settings" / f"rep{rep}" / "wpctl_settings.stdout").read_text())
    sp = parse_stream_props()
    res["parsed"] = {"n_settings": len(s), "settings": s,
                     "state_files": sorted(p.name for p in STATE_DIR.iterdir()),
                     "stream_props": {k: v for k, v in sp.items() if k != "entries"},
                     "stream_props_entry_names": sorted(sp["entries"])}
    return res


# ---------------------------------------------------------------- stage f2
F2_MODULES = [
    ("p1_null_sink", ["module-null-sink", "sink_name=r90ns"], "control"),
    ("p2_tunnel_sink", ["module-tunnel-sink", "server=127.0.0.1:1", "sink_name=r90tun"], "tunnel"),
    ("p3_tunnel_source", ["module-tunnel-source", "server=127.0.0.1:1", "source_name=r90tuns"], "tunnel"),
    ("p4_zeroconf_discover", ["module-zeroconf-discover"], "zeroconf"),
    ("p5_zeroconf_publish", ["module-zeroconf-publish"], "zeroconf"),
    ("p6_roc_sink", ["module-roc-sink"], "roc"),
    ("p7_stream_restore", ["module-stream-restore"], "stub"),
    ("p8_device_restore", ["module-device-restore"], "stub"),
    ("p9_always_sink", ["module-always-sink"], "stub"),
    ("p10_unknown", ["module-not-a-module"], "control"),
]


def stage_f2(rep):
    res = {"entry_census": census(), "legs": {}}
    before = set(res["entry_census"]["modules"])
    for leg, argv, cls in F2_MODULES:
        name = f"f2_{leg}"
        r_load = step(name, rep, "load", ["pactl", "load-module"] + argv)
        txt = (r_load["out_head"] + r_load["err_head"]).strip()
        mid = int(txt) if re.fullmatch(r"\d+", txt) else None
        rec = {"class": cls, "load": r_load, "module_id": mid}
        if mid is not None:
            rec["objects"] = step(name, rep, "after_load", [
                "bash", "-c",
                "pactl list sinks short; pactl list sources short; "
                "pw-dump | python3 -c \"import json,sys;d=json.load(sys.stdin);"
                "print(sorted(str((o.get('info',{}).get('props',{}) or {}).get('node.name')) "
                "for o in d if o.get('type')=='PipeWire:Interface:Node'))\""], timeout=30)
            rec["unload"] = unload(mid)
            rec["census_after"] = census()
        res["legs"][leg] = rec
    res["exit_census"] = census()
    res["module_set_restored"] = set(res["exit_census"]["modules"]) == before
    res["r90_nodes_at_exit"] = res["exit_census"]["r90_nodes"]
    return res


# ---------------------------------------------------------------- stage f3
def stage_f3(rep):
    res = {}
    res["v1_which"] = step("f3_v1_which", rep, "which",
                           ["bash", "-c", "which pw-v4l2; ls -l /usr/bin/pw-v4l2; "
                                          "ls /usr/share/man/man1 | grep -i v4l2"])
    res["v2_pkg"] = step("f3_v2_pkg", rep, "pkg",
                         ["bash", "-c", "pacman -Qs pipewire-v4l2; "
                                        "pacman -Ql pipewire | grep -i v4l2; "
                                        "pacman -Ss '^pipewire-v4l2$'"])
    res["v3_spa"] = step("f3_v3_spa", rep, "spa",
                         ["bash", "-c", "ls -la /usr/lib/spa-0.2/v4l2/; "
                                        "strings -a /usr/lib/spa-0.2/v4l2/libspa-v4l2.so "
                                        "| grep -cE 'v4l2' "])
    res["v4_devices"] = step("f3_v4_devices", rep, "devices",
                             ["bash", "-c", "ls -la /dev/video* 2>&1; "
                                            "lsmod | grep -icE 'v4l2|uvcvideo'; "
                                            "ls /sys/class/video4linux 2>&1"])
    res["v5_services"] = step("f3_v5_services", rep, "services",
                              ["bash", "-c", "pactl list | grep -i v4l2; "
                                             "pw-cli ls Device | grep -c v4l2"])
    objs = pw_dump()
    res["parsed"] = {
        "v4l2_nodes": sorted(str((o.get("info", {}).get("props", {}) or {}).get("node.name"))
                             for o in objs if o.get("type") == "PipeWire:Interface:Node"
                             and "v4l2" in json.dumps(o.get("info", {}).get("props", {})).lower()),
        "device_apis": sorted(set(str((o.get("info", {}).get("props", {}) or {}).get("device.api"))
                                  for o in objs if o.get("type") == "PipeWire:Interface:Device")),
    }
    return res


# ---------------------------------------------------------------- stage f4
def stage_f4(rep):
    """pw-link grammar on two seat-owned null sinks (r90a/r90b)."""
    res = {}
    mid_a, ra, ta = load_null_sink("r90a")
    mid_b, rb, tb = load_null_sink("r90b")
    res["setup"] = {"mid_a": mid_a, "mid_b": mid_b, "load_a": ta, "load_b": tb}
    time.sleep(0.5)
    na, nb = node_id("r90a"), node_id("r90b")
    res["setup"].update({"node_a": na, "node_b": nb,
                         "ports_a": ports_of(na), "ports_b": ports_of(nb)})
    A, B = "r90a:monitor_FL", "r90b:playback_FL"
    A2, B2 = "r90a:monitor_FR", "r90b:playback_FR"

    def links():
        return step("f4_links", rep, f"l_{time.monotonic_ns()}", ["pw-link", "-l"],
                    keep=lambda r: {"n_lines": len(r["out"].decode().splitlines()),
                                    "lines": r["out"].decode().splitlines()[:8]})

    res["l1_list_ports"] = step("f4_l1_ports", rep, "pw_link_o", ["pw-link", "-o"])
    res["l1b_list_ids"] = step("f4_l1b_ids", rep, "pw_link_I_o", ["pw-link", "-I", "-o"])
    res["l2_connect"] = step("f4_l2_connect", rep, "connect", ["pw-link", A, B])
    res["l2_witness"] = step("f4_l2_witness", rep, "links", ["pw-link", "-l"])
    res["l2_ids"] = step("f4_l2_ids", rep, "link_ids", ["pw-link", "-I", "-l"])
    res["l2_disconnect"] = step("f4_l2_disconnect", rep, "disconnect", ["pw-link", "-d", A, B])
    res["l2_after"] = step("f4_l2_after", rep, "links", ["pw-link", "-l"])

    # bulk: two pairs in one invocation
    res["l3_bulk_connect"] = step("f4_l3_bulk", rep, "bulk_connect",
                                  ["pw-link", A, B, A2, B2])
    res["l3_witness"] = step("f4_l3_witness", rep, "links", ["pw-link", "-l"])
    res["l3_bulk_disconnect"] = step("f4_l3_bulk_disconnect", rep, "bulk_disc",
                                     ["pw-link", "-d", A, B, A2, B2])
    res["l3_after"] = step("f4_l3_after", rep, "links", ["pw-link", "-l"])

    # partial failure, forward and reverse order
    res["l4_partial_fwd"] = step("f4_l4_partial", rep, "partial_fwd",
                                 ["pw-link", A, B, "r90nope:out", "r90nope:in"])
    res["l4_witness"] = step("f4_l4_witness", rep, "links", ["pw-link", "-l"])
    res["l4_cleanup"] = step("f4_l4_cleanup", rep, "disconnect", ["pw-link", "-d", A, B])
    res["l5_partial_rev"] = step("f4_l5_partial", rep, "partial_rev",
                                 ["pw-link", "r90nope:out", "r90nope:in", A, B])
    res["l5_witness"] = step("f4_l5_witness", rep, "links", ["pw-link", "-l"])

    # duplicate + wrong direction + self
    res["l6_dup1"] = step("f4_l6_dup", rep, "dup1", ["pw-link", A, B])
    res["l6_dup2"] = step("f4_l6_dup", rep, "dup2", ["pw-link", A, B])
    res["l6_cleanup"] = step("f4_l6_cleanup", rep, "disconnect", ["pw-link", "-d", A, B])
    res["l7_direction"] = step("f4_l7_dir", rep, "reversed",
                               ["pw-link", B, A])
    res["l8_self"] = step("f4_l8_self", rep, "self",
                          ["pw-link", A, "r90a:playback_FL"])
    res["l9_glob"] = step("f4_l9_glob", rep, "glob",
                          ["pw-link", "r90a:monitor_*", "r90b:playback_*"])
    res["l9_witness"] = step("f4_l9_witness", rep, "links", ["pw-link", "-l"])

    # -w wait semantics on a port that does not exist (2 s bound)
    res["l10_wait_missing"] = step("f4_l10_wait", rep, "wait_missing",
                                   ["pw-link", "-w", A, "r90b:playback_ZZ"], timeout=3)
    res["l10_wait_ok"] = step("f4_l10b_wait_ok", rep, "wait_ok",
                              ["pw-link", "-w", A, B], timeout=3)
    res["l10_after"] = step("f4_l10_after", rep, "links", ["pw-link", "-l"])

    # disconnect by link-id, two ids in one call
    ids = step("f4_l11_ids", rep, "ids", ["pw-link", "-I", "-l"])
    got = [l.split()[0] for l in ids["out_head"].splitlines() if l.strip()]
    res["l11_id_lines"] = got
    if got:
        res["l11_disconnect_two_ids"] = step("f4_l11_disc_ids", rep, "disc_two_ids",
                                             ["pw-link", "-d"] + got[:2])
    res["l11_after"] = step("f4_l11_after", rep, "links", ["pw-link", "-l"])
    res["l12_badlink_id"] = step("f4_l12_badid", rep, "disc_bad_id",
                                 ["pw-link", "-d", "999999"])
    # teardown by ID only
    res["teardown"] = {"a": unload(mid_a) if mid_a else None,
                       "b": unload(mid_b) if mid_b else None}
    time.sleep(0.4)
    res["teardown"]["nodes_after"] = [n["info"]["props"].get("node.name")
                                      for n in nodes_by_name("r90a") + nodes_by_name("r90b")]
    return res


# ---------------------------------------------------------------- stage f5
def stage_f5(rep):
    """EnumFormat vs Format on a seat-owned sink node/port, mid-stream."""
    res = {}
    mid, r, txt = load_null_sink("r90a")
    res["setup"] = {"mid": mid, "load": txt}
    time.sleep(0.5)
    nid = node_id("r90a")
    ports = ports_of(nid)
    res["setup"].update({"node_id": nid, "ports": ports})
    pin = next((p["id"] for p in ports if p["name"] == "playback_FL"), None)
    res["setup"]["port_in_id"] = pin

    def read(tag, extra_label=""):
        out = {}
        out["node_enum"] = step("f5_reads", rep, f"{tag}_node_enum",
                                ["pw-cli", "enum-params", str(nid), "EnumFormat"])
        out["node_format"] = step("f5_reads", rep, f"{tag}_node_format",
                                  ["pw-cli", "enum-params", str(nid), "Format"])
        if pin:
            out["port_enum"] = step("f5_reads", rep, f"{tag}_port_enum",
                                    ["pw-cli", "enum-params", str(pin), "EnumFormat"])
            out["port_format"] = step("f5_reads", rep, f"{tag}_port_format",
                                      ["pw-cli", "enum-params", str(pin), "Format"])
        return out

    res["rest"] = read("rest")
    # stream at 48k
    p48 = spawn(["pw-play", "--target", "r90a", "-P", "node.name=r90e48",
                 "-P", "application.name=r90e48", str(TONE48)])
    time.sleep(1.2)
    sid = node_id("r90e48")
    res["stream48"] = {"node_id": sid, "alive": p48.poll() is None}
    if sid:
        res["stream48"]["enum"] = step("f5_reads", rep, "s48_enum",
                                       ["pw-cli", "enum-params", str(sid), "EnumFormat"])
        res["stream48"]["format"] = step("f5_reads", rep, "s48_format",
                                         ["pw-cli", "enum-params", str(sid), "Format"])
        res["stream48"]["props"] = step("f5_reads", rep, "s48_props",
                                        ["pw-cli", "enum-params", str(sid), "Props"])
    res["during48"] = read("dur48")
    res["links48"] = step("f5_reads", rep, "s48_links", ["pw-link", "-l"])
    # mid-stream set-param Format on the SINK node (the other end of the link)
    res["mid_setparam"] = step("f5_reads", rep, "s48_setparam_format",
                               ["pw-cli", "set-param", str(nid), "Format",
                                "{ mediaType: 1, mediaSubtype: 1, format: 259, "
                                "rate: 44100, channels: 2 }"])
    res["post_setparam"] = read("postsp")
    res["links_post"] = step("f5_reads", rep, "s48_links_post", ["pw-link", "-l"])
    res["stream_alive_post"] = p48.poll() is None
    res["stop48"] = stop(p48)
    time.sleep(0.6)
    res["after48"] = read("after48")
    # stream at 44.1k
    p441 = spawn(["pw-play", "--target", "r90a", "-P", "node.name=r90e441",
                  "-P", "application.name=r90e441", str(TONE441)])
    time.sleep(1.2)
    sid2 = node_id("r90e441")
    res["stream441"] = {"node_id": sid2, "alive": p441.poll() is None}
    if sid2:
        res["stream441"]["format"] = step("f5_reads", rep, "s441_format",
                                          ["pw-cli", "enum-params", str(sid2), "Format"])
    res["during441"] = read("dur441")
    res["stop441"] = stop(p441)
    time.sleep(0.5)
    res["after441"] = read("after441")
    res["teardown"] = unload(mid) if mid else None
    return res


# ---------------------------------------------------------------- stage f6
def wait_for_entry(key, want=True, timeout=10.0, poll=0.15):
    """Poll the stream-properties store until key appears/disappears."""
    t0 = time.time()
    seen = []
    while time.time() - t0 < timeout:
        try:
            sp = parse_stream_props()
        except Exception as e:
            return {"error": str(e)}
        present = key in sp["entries"]
        seen.append((round(time.time() - t0, 3), present, sp["mtime"]))
        if present == want:
            return {"found": present, "delay_s": round(time.time() - t0, 3),
                    "mtime": sp["mtime"], "entry": sp["entries"].get(key),
                    "polls": seen[:6]}
        time.sleep(poll)
    return {"found": None, "delay_s": None, "polls": seen[-3:]}


def stage_f6(rep):
    """session-manager restore law: write / read / target / opt-out."""
    res = {}
    mid_a, _, _ = load_null_sink("r90a")
    mid_b, _, _ = load_null_sink("r90b")
    res["setup"] = {"mid_a": mid_a, "mid_b": mid_b}
    time.sleep(0.5)
    snap0 = parse_stream_props()
    res["snapshot0"] = {k: v for k, v in snap0.items() if k != "entries"}
    res["snapshot0"]["has_r90"] = sorted(k for k in snap0["entries"] if "r90" in k)

    app1 = f"r90w{rep}"
    key1 = f"Output/Audio:application.name:{app1}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app1}",
               "-P", f"node.name={app1}", str(TONE48)])
    time.sleep(1.0)
    nid = node_id(app1)
    res["w1_stream"] = {"node_id": nid, "alive": p.poll() is None,
                        "links": step("f6_w", rep, "links", ["pw-link", "-l"])["out_head"]}
    res["w1_stop"] = stop(p)
    res["w1_entry"] = wait_for_entry(key1, want=True, timeout=10.0)
    res["w1_store"] = {k: v for k, v in parse_stream_props().items() if k != "entries"}

    # props-change store: play again, set volume mid-stream, expect volume saved
    app2 = f"r90v{rep}"
    key2 = f"Output/Audio:application.name:{app2}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app2}",
               "-P", f"node.name={app2}", str(TONE48)])
    time.sleep(1.0)
    nid2 = node_id(app2)
    res["v2_stream"] = {"node_id": nid2}
    if nid2:
        res["v2_setvol"] = step("f6_v", rep, "setvol",
                                ["pw-cli", "set-param", str(nid2), "Props",
                                 "{ volume: 0.5 }"])
        time.sleep(0.3)
        res["v2_props"] = step("f6_v", rep, "props",
                               ["pw-cli", "enum-params", str(nid2), "Props"])
    res["v2_stop"] = stop(p)
    res["v2_entry"] = wait_for_entry(key2, want=True, timeout=10.0)

    # read side: same application.name, no --volume -> restored volume 0.5?
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app2}",
               "-P", f"node.name={app2}b", str(TONE48)])
    time.sleep(1.2)
    nid3 = node_id(f"{app2}b")
    res["v3_restore_stream"] = {"node_id": nid3}
    if nid3:
        res["v3_props"] = step("f6_v", rep, "props_after_restore",
                               ["pw-cli", "enum-params", str(nid3), "Props"])
    res["v3_stop"] = stop(p)

    # per-stream opt-out
    app3 = f"r90x{rep}"
    key3 = f"Output/Audio:application.name:{app3}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app3}",
               "-P", f"node.name={app3}", "-P", "state.restore-props=false",
               str(TONE48)])
    time.sleep(1.2)
    res["x3_alive"] = p.poll() is None
    res["x3_stop"] = stop(p)
    res["x3_entry"] = wait_for_entry(key3, want=True, timeout=4.0)
    res["x3_absent"] = wait_for_entry(key3, want=False, timeout=0.1)

    # key precedence: application.id vs application.name
    app4, appid4 = f"r90p{rep}", f"r90pid{rep}"
    key4a = f"Output/Audio:application.id:{appid4}"
    key4b = f"Output/Audio:application.name:{app4}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app4}",
               "-P", f"application.id={appid4}", "-P", f"node.name={app4}", str(TONE48)])
    time.sleep(1.2)
    res["p4_stop"] = stop(p)
    res["p4_id_entry"] = wait_for_entry(key4a, want=True, timeout=6.0)
    res["p4_name_entry"] = wait_for_entry(key4b, want=True, timeout=1.0)

    # target restore: move stream to r90b, then replay and witness the link
    app5 = f"r90t{rep}"
    key5 = f"Output/Audio:application.name:{app5}"
    p = spawn(["pw-play", "--target", "r90a", "-P", f"application.name={app5}",
               "-P", f"node.name={app5}", str(TONE48)])
    time.sleep(1.0)
    si = step("f6_t", rep, "sink_inputs", ["pactl", "list", "sink-inputs", "short"])
    idx = None
    for line in si["out_head"].splitlines():
        if app5 in line:
            idx = line.split("\t")[0].strip()
    res["t5_sink_input"] = {"index": idx, "list": si["out_head"]}
    if idx:
        res["t5_move"] = step("f6_t", rep, "move", ["pactl", "move-sink-input", idx, "r90b"])
        time.sleep(0.4)
        res["t5_links"] = step("f6_t", rep, "links_moved", ["pw-link", "-l"])
    res["t5_stop"] = stop(p)
    res["t5_entry"] = wait_for_entry(key5, want=True, timeout=10.0)
    p = spawn(["pw-play", "-P", f"application.name={app5}", "-P", f"node.name={app5}b",
               str(TONE48)])
    time.sleep(1.5)
    res["t5_replay_links"] = step("f6_t", rep, "links_replay", ["pw-link", "-l"])
    res["t5_replay_si"] = step("f6_t", rep, "si_replay",
                               ["pactl", "list", "sink-inputs", "short"])
    res["t5_replay_stop"] = stop(p)

    # capture direction key
    app6 = f"r90c{rep}"
    key6 = f"Input/Audio:application.name:{app6}"
    p = spawn(["pw-record", "--target", "r90a", "-P", f"application.name={app6}",
               "-P", f"node.name={app6}", "/dev/null"])
    time.sleep(1.2)
    res["c6_alive"] = p.poll() is None
    res["c6_stop"] = stop(p)
    res["c6_entry"] = wait_for_entry(key6, want=True, timeout=8.0)

    res["teardown"] = {"a": unload(mid_a) if mid_a else None,
                       "b": unload(mid_b) if mid_b else None}
    time.sleep(0.4)
    snap9 = parse_stream_props()
    res["snapshot9"] = {k: v for k, v in snap9.items() if k != "entries"}
    res["snapshot9"]["r90_keys"] = sorted(k for k in snap9["entries"] if "r90" in k)
    return res


STAGE_FN = {"f1": stage_f1, "f2": stage_f2, "f3": stage_f3,
            "f4": stage_f4, "f5": stage_f5, "f6": stage_f6}
MUTATING = {"f2", "f4", "f5", "f6"}


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "f1"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    assert stage in STAGE_FN, f"stage must be one of {STAGES}"
    tone(TONE48, 48000)
    tone(TONE441, 44100)
    out = {"stage": stage, "reps": reps, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "host": {"pipewire": "1.6.8", "wireplumber": "0.5.17"},
           "entry_census": census(), "legs": []}
    for rep in range(1, reps + 1):
        t0 = time.time()
        try:
            r = STAGE_FN[stage](rep)
            r["_wall_s"] = round(time.time() - t0, 2)
        except Exception as e:  # keep the other reps
            import traceback
            r = {"error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-800:]}
        out["legs"].append({"rep": rep, **r})
        print(f"[{stage}] rep{rep} done in {round(time.time()-t0,2)}s "
              f"{'ERR' if 'error' in r else ''}", flush=True)
    out["exit_census"] = census()
    if stage in MUTATING:
        out["census_restored"] = out["entry_census"]["modules"] == out["exit_census"]["modules"]
        out["r90_nodes_at_exit"] = out["exit_census"]["r90_nodes"]
    (REC / f"{stage}.json").write_text(json.dumps(out, indent=1))
    print(f"[{stage}] wrote {REC / (stage + '.json')}")


if __name__ == "__main__":
    main()
