#!/usr/bin/env python3
"""r90 boundary harness — falsify r90 scout claims (verbatim replays, host-state
variation, hog load, unstated-mode hunting).

Namespace discipline: every audio object this harness creates is named r90b_*.
Every module unload is by the id we loaded, with ONE controlled exception
(stage s4, C13 replay) on module-loopback after a zero-foreign pre-check.
Nothing is ever unloaded by name on a shared class.

Stages:
  s0   read-only census: settings lattice, v4l2 absence, state file, siblings
  s1   pw-link grammar replays (own sinks r90b_ns_a/b)
  s2   EnumFormat/Format replays + mid-stream set-param (sink + stream node)
  s3   restore store law: clean fresh-key latency, field split, target, opt-out
  s4   pulse module namespace: tunnel phantom, unload-by-name (safe class),
       zeroconf publish witness (avahi), stubs
  s5   unstated modes: pw-link -w late port, -p props, -m monitor, -t latency,
       -v verbose; device-backed link for -t
  s6   the timing-critical subset under own hog load (32 yes + 4 dd writers)
  s7   cleanup + final census

Receipts: receipts/<stage>.json. Raw: runs/<stage>/rep<N>/.
"""
import hashlib
import json
import math
import os
import re
import signal
import struct
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
REC = ROOT / "receipts"
STATE = Path.home() / ".local/state/wireplumber/stream-properties"
PREFIX = "r90b_"
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
            "out": out, "err": err, "ms": (t1 - t0) // 10 ** 6,
            "t0": t0, "t1": t1}


def step(stage, rep, label, cmd, timeout=20, keep=None):
    wd = RUNS / stage / f"rep{rep}"
    wd.mkdir(parents=True, exist_ok=True)
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


def spawn(cmd):
    return subprocess.Popen([str(c) for c in cmd], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)


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
            "err_head": err[:300].decode("utf-8", "replace")}


# ---------------------------------------------------------------- graph utils
def pw_dump():
    r = sh(["pw-dump"], timeout=30)
    try:
        return json.loads(r["out"])
    except Exception:
        return []


def node_props(o):
    return (o.get("info", {}).get("props", {}) or {})


def nodes_named(name, objs=None):
    objs = pw_dump() if objs is None else objs
    return [o for o in objs if o.get("type") == "PipeWire:Interface:Node"
            and node_props(o).get("node.name") == name]


def node_id(name):
    n = nodes_named(name)
    return n[0]["id"] if n else None


def nodes_prefix(prefix, objs=None):
    objs = pw_dump() if objs is None else objs
    return [{"id": o["id"], "name": node_props(o).get("node.name")}
            for o in objs if o.get("type") == "PipeWire:Interface:Node"
            and str(node_props(o).get("node.name", "")).startswith(prefix)]


def module_table():
    r = sh(["pactl", "list", "short", "modules"], timeout=20)
    rows = []
    for line in r["out"].decode("utf-8", "replace").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].strip().isdigit():
            rows.append({"id": int(parts[0]), "name": parts[1],
                         "args": parts[2][:200] if len(parts) > 2 else ""})
        elif rows and line.startswith((" ", "\t")) and line.strip():
            # continuation of the previous module's multi-line args
            rows[-1]["args"] += " " + line.strip()[:120]
    return rows


def module_ids():
    return sorted(m["id"] for m in module_table())


def my_modules():
    return [m for m in module_table() if PREFIX in m["args"] or PREFIX in m["name"]]


def load_null(name, extra=None):
    argv = ["pactl", "load-module", "module-null-sink", f"sink_name={name}"]
    if extra:
        argv += list(extra)
    r = sh(argv)
    txt = (r["out"] + r["err"]).decode("utf-8", "replace").strip()
    mid = int(txt) if r["rc"] == 0 and txt.isdigit() else None
    return mid, r, txt


def unload_raw(mid):
    """Raw pactl unload by id — ONLY for phantom ids with a pre-check by caller."""
    if mid is None:
        return None
    r = sh(["pactl", "unload-module", str(mid)])
    return {"cmd": r["cmd"], "rc": r["rc"],
            "err": r["err"].decode("utf-8", "replace").strip()[:120]}


def unload(mid):
    """Namespace-guarded unload: refuses if the id no longer carries r90b_ args."""
    if mid is None:
        return None
    rows = {m["id"]: m for m in module_table()}
    m = rows.get(int(mid))
    if m is None:
        return {"id": mid, "rc": None, "skipped": "id_not_present"}
    if PREFIX not in m["args"]:
        return {"id": mid, "rc": None, "refused": True,
                "name": m["name"], "args": m["args"][:120]}
    r = sh(["pactl", "unload-module", str(mid)])
    return {"id": mid, "rc": r["rc"],
            "err": r["err"].decode("utf-8", "replace").strip()[:120]}


def census():
    objs = pw_dump()
    mods = module_table()
    names = [(o["id"], node_props(o).get("node.name"))
             for o in objs if o.get("type") == "PipeWire:Interface:Node"]
    name_by_id = dict(names)
    links = [o for o in objs if o.get("type") == "PipeWire:Interface:Link"]
    r90b_links = []
    for o in links:
        pr = (o.get("info", {}).get("props", {}) or {})
        ends = [name_by_id.get(pr.get("link.input.node")),
                name_by_id.get(pr.get("link.output.node"))]
        if any(str(e or "").startswith(PREFIX) for e in ends):
            r90b_links.append({"id": o["id"], "ends": ends})
    try:
        la = os.getloadavg()
    except Exception:
        la = None
    return {
        "modules": [m["id"] for m in mods],
        "n_modules": len(mods),
        "r90b_modules": [m for m in mods if PREFIX in m["args"]],
        "r90b_nodes": sorted(str(n) for _, n in names if str(n or "").startswith(PREFIX)),
        "r90b_links": r90b_links,
        "sibling_nodes": sorted(set(str(n) for _, n in names
                                    if re.match(r"r\d\d", str(n or ""))
                                    and not str(n or "").startswith(PREFIX))),
        "n_nodes": len(names), "n_links": len(links),
        "loadavg": la,
    }


# ---------------------------------------------------------------- store utils
def parse_store():
    raw = STATE.read_bytes()
    entries = {}
    for line in raw.decode("utf-8", "replace").splitlines():
        if line.startswith("[") or not line.strip() or "=" not in line:
            continue
        k, v = line.split("=", 1)
        try:
            entries[k] = json.loads(v)
        except Exception:
            entries[k] = {"_raw": v[:120]}
    return entries


def store_meta():
    raw = STATE.read_bytes()
    entries = {}
    for line in raw.decode("utf-8", "replace").splitlines():
        if line.startswith("[") or not line.strip() or "=" not in line:
            continue
        k, v = line.split("=", 1)
        try:
            entries[k] = json.loads(v)
        except Exception:
            entries[k] = {"_raw": v[:120]}
    st = STATE.stat()
    return {"size": len(raw), "sha256": sha(raw), "mtime_ns": st.st_mtime_ns,
            "n_rows": len(entries),
            "r90b_keys": sorted(k for k in entries if PREFIX in k)}


def wait_value(key, pred=None, timeout=8.0, interval=0.002, max_log=10):
    """Stat-gated fast watcher: returns first moment the key matches pred."""
    t0 = time.monotonic()
    last = None
    log = []
    while True:
        el = time.monotonic() - t0
        try:
            st = STATE.stat()
            sig = (st.st_mtime_ns, st.st_size)
        except Exception:
            sig = None
        if sig != last:
            last = sig
            try:
                e = parse_store().get(key)
            except Exception:
                e = None
            log.append((round(el, 3), json.dumps(e)[:100] if e is not None else None))
            if e is not None and (pred is None or pred(e)):
                return {"ok": True, "delay_s": round(el, 3), "entry": e,
                        "log": log[-max_log:]}
        if el > timeout:
            return {"ok": False, "delay_s": None, "log": log[-max_log:]}
        time.sleep(interval)


def key_absent(key, timeout=3.0, interval=0.02):
    """Return present/absent over a window (for opt-out checks)."""
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        try:
            if key in parse_store():
                return {"present": True, "at_s": round(time.monotonic() - t0, 3)}
        except Exception:
            pass
        time.sleep(interval)
    return {"present": False, "at_s": None, "window_s": timeout}


# ---------------------------------------------------------------- tone synth
def tone(path, rate, secs=3.0, freq=440.0, amp=12000):
    if path.exists():
        return
    n = int(rate * secs)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(n):
            v = int(amp * math.sin(2 * math.pi * freq * i / rate)) if amp else 0
            frames += struct.pack("<hh", v, v)
        w.writeframes(bytes(frames))


SIL48 = ROOT / "r90b_sil48.wav"
SIL441 = ROOT / "r90b_sil441.wav"


def ensure_tones():
    tone(SIL48, 48000, secs=3.0, freq=440.0, amp=0)
    tone(SIL441, 44100, secs=3.0, freq=440.0, amp=0)


# ---------------------------------------------------------------- pw-link utils
def link_rows(extra=()):
    r = sh(["pw-link", "-l", *extra])
    rows = [l for l in r["out"].decode("utf-8", "replace").splitlines()
            if "|->" in l or "|<-" in l]
    own = [l for l in rows if PREFIX in l]
    return {"rc": r["rc"], "n": len(rows), "own_n": len(own),
            "own_links": len(own_link_objs()), "ms": r["ms"],
            "rows": rows[:12], "own_rows": own[:8]}


def link_ids():
    """Namespace-filtered link ids (deduped): only rows mentioning r90b_."""
    r = sh(["pw-link", "-I", "-l"])
    ids, seen = [], set()
    for line in r["out"].decode("utf-8", "replace").splitlines():
        if ("|->" in line or "|<-" in line) and PREFIX in line:
            toks = line.split()
            if toks and toks[0].isdigit() and toks[0] not in seen:
                seen.add(toks[0])
                ids.append(toks[0])
    return ids, r["out"].decode("utf-8", "replace")


def own_link_objs():
    """Links where BOTH endpoints are r90b_* nodes (namespace-precise)."""
    objs = pw_dump()
    names = {o["id"]: node_props(o).get("node.name")
             for o in objs if o.get("type") == "PipeWire:Interface:Node"}
    out = []
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Link":
            continue
        pr = (o.get("info", {}).get("props", {}) or {})
        iname = names.get(pr.get("link.input.node"))
        oname = names.get(pr.get("link.output.node"))
        if str(iname or "").startswith(PREFIX) and str(oname or "").startswith(PREFIX):
            out.append({"id": o["id"], "in": iname, "out": oname,
                        "props": {k: v for k, v in pr.items()
                                  if k in ("link.passive", "link.feedback",
                                           "link.async", "object.serial")}})
    return out


def disconnect_all_own():
    killed = []
    for l in own_link_objs():
        r = sh(["pw-link", "-d", str(l["id"])])
        killed.append({"id": l["id"], "rc": r["rc"]})
    return killed


# ---------------------------------------------------------------- hogs
HOG_PIDS = []


def start_hogs(n_yes=32, n_io=4):
    HOG_PIDS.clear()
    for _ in range(n_yes):
        HOG_PIDS.append(subprocess.Popen(["yes"], stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL).pid)
    for i in range(n_io):
        HOG_PIDS.append(subprocess.Popen(
            ["bash", "-c",
             f"while :; do dd if=/dev/zero of=/tmp/r90b_io_{i} bs=1M count=64 "
             f"conv=fdatasync 2>/dev/null; done"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).pid)
    return {"pids": list(HOG_PIDS), "n_yes": n_yes, "n_io": n_io,
            "loadavg_start": os.getloadavg()}


def stop_hogs():
    for pid in list(HOG_PIDS):
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    time.sleep(0.5)
    for pid in list(HOG_PIDS):
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    subprocess.run(["pkill", "-f", "/tmp/r90b_io_"], capture_output=True)
    subprocess.run(["rm", "-f", "/tmp/r90b_io_0", "/tmp/r90b_io_1",
                    "/tmp/r90b_io_2", "/tmp/r90b_io_3"], capture_output=True)
    HOG_PIDS.clear()
    return {"loadavg_end": os.getloadavg()}


# ================================================================== stages
def stage_s0(rep):
    """Read-only census + settings/v4l2 replay."""
    res = {}
    res["census"] = census()
    res["loadavg"] = os.getloadavg()
    res["settings"] = step("s0", rep, "wpctl_settings", ["wpctl", "settings"])
    res["settings_h"] = step("s0", rep, "wpctl_settings_h",
                             ["wpctl", "settings", "-h"])
    res["state_ls"] = step("s0", rep, "state_ls",
                           ["ls", "-la", str(STATE.parent)])
    res["default_nodes"] = step("s0", rep, "default_nodes",
                                ["cat", str(STATE.parent / "default-nodes")])
    res["v4l2_which"] = step("s0", rep, "v4l2_which",
                             ["bash", "-c", "which pw-v4l2; ls -l /usr/bin/pw-v4l2 2>&1; "
                                            "ls /usr/share/man/man1 2>/dev/null | grep -i v4l2"])
    res["v4l2_dev"] = step("s0", rep, "v4l2_dev",
                           ["bash", "-c", "ls /dev/video* 2>&1; "
                                          "ls /sys/class/video4linux 2>&1; "
                                          "lsmod | grep -icE 'v4l2|uvcvideo'"])
    res["v4l2_services"] = step("s0", rep, "v4l2_services",
                                ["bash", "-c", "pactl list | grep -i v4l2; "
                                               "pw-cli ls Device | grep -c v4l2"])
    res["siblings_ps"] = step("s0", rep, "siblings_ps",
                              ["bash", "-c", "ps -eo pid,pcpu,args --sort=-pcpu | "
                                             "grep -E 'r9[0-9]|godot|filter-chain|yes|dd' | "
                                             "grep -v grep | head -20"])
    # parsed: settings lattice
    text = (RUNS / "s0" / f"rep{rep}" / "wpctl_settings.stdout").read_text()
    sett = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^- Id: (\S+)", line.rstrip())
        if m:
            cur = {"id": m.group(1)}
            sett[m.group(1)] = cur
        else:
            m = re.match(r"^\s+(Name|Desc|Type|Default|Value): (.*)$", line)
            if m and cur:
                cur[m.group(1).lower()] = m.group(2)
    # cross-witness: sm-settings metadata keys
    sm_keys, spdif_vol = [], None
    for o in pw_dump():
        if o.get("type") == "PipeWire:Interface:Metadata" and \
                (o.get("props", {}) or {}).get("metadata.name") == "sm-settings":
            sm_keys = sorted(m.get("key") for m in o.get("metadata", []))
        if o.get("type") == "PipeWire:Interface:Node" and \
                "SPDIF" in str(node_props(o).get("node.name", "")):
            pl = ((o.get("info", {}).get("params", {}) or {}).get("Props") or [{}])
            spdif_vol = pl[0].get("channelVolumes") if pl else None
    res["parsed"] = {
        "n_settings": len(sett), "settings": sett,
        "state_files": sorted(p.name for p in STATE.parent.iterdir()),
        "sm_settings_keys": sm_keys,
        "sm_set_equal": sorted(sett) == sm_keys,
        "spdif_channelVolumes": spdif_vol,
        "default_sink_volume_setting": sett.get("device.routes.default-sink-volume"),
        "store": store_meta(),
    }
    return res


def stage_s1(rep):
    """pw-link grammar replays on own sinks."""
    res = {}
    mid_a, ra, ta = load_null(f"{PREFIX}ns_a")
    mid_b, rb, tb = load_null(f"{PREFIX}ns_b")
    res["setup"] = {"mid_a": mid_a, "mid_b": mid_b, "txt_a": ta, "txt_b": tb}
    time.sleep(0.5)
    na, nb = node_id(f"{PREFIX}ns_a"), node_id(f"{PREFIX}ns_b")
    A, B = f"{PREFIX}ns_a:monitor_FL", f"{PREFIX}ns_b:playback_FL"
    A2, B2 = f"{PREFIX}ns_a:monitor_FR", f"{PREFIX}ns_b:playback_FR"
    res["setup"].update({"node_a": na, "node_b": nb})
    try:
        # c1 single connect + witness
        res["c1_connect"] = step("s1", rep, "c1_connect", ["pw-link", A, B])
        res["c1_links"] = link_rows()
        res["c1_ids"] = step("s1", rep, "c1_ids", ["pw-link", "-I", "-l"])
        res["c1_disconnect"] = step("s1", rep, "c1_disconnect", ["pw-link", "-d", A, B])
        res["c1_after"] = link_rows()

        # c2 bulk connect 2 pairs (expect first pair only)
        step("s1", rep, "c2_link1", ["pw-link", A, B])
        step("s1", rep, "c2_link2", ["pw-link", A2, B2])
        res["c2_two_links"] = link_rows()
        res["c2_bulk_disc"] = step("s1", rep, "c2_bulk_disc",
                                   ["pw-link", "-d", A, B, A2, B2])
        res["c2_after_bulk_disc"] = link_rows()
        disconnect_all_own()
        res["c3_bulk_connect"] = step("s1", rep, "c3_bulk_connect",
                                      ["pw-link", A, B, A2, B2])
        res["c3_witness"] = link_rows()
        disconnect_all_own()

        # c4 reversed direction
        res["c4_reversed"] = step("s1", rep, "c4_reversed", ["pw-link", B, A])
        res["c4_links"] = link_rows()

        # c5 glob connect
        res["c5_glob"] = step("s1", rep, "c5_glob",
                              ["pw-link", f"{PREFIX}ns_a:monitor_*",
                               f"{PREFIX}ns_b:playback_*"])
        res["c5_links"] = link_rows()

        # c6 duplicate
        step("s1", rep, "c6_link", ["pw-link", A, B])
        res["c6_dup"] = step("s1", rep, "c6_dup", ["pw-link", A, B])
        disconnect_all_own()

        # c7 two link ids disconnect
        step("s1", rep, "c7_link1", ["pw-link", A, B])
        step("s1", rep, "c7_link2", ["pw-link", A2, B2])
        ids, raw = link_ids()
        res["c7_ids"] = ids
        res["c7_two_ids"] = step("s1", rep, "c7_two_ids",
                                 ["pw-link", "-d"] + ids[:2]) if len(ids) >= 2 else None
        res["c7_after"] = link_rows()
        disconnect_all_own()

        # c8 single link id disconnect works
        step("s1", rep, "c8_link", ["pw-link", A, B])
        ids1, _ = link_ids()
        res["c8_single_id"] = step("s1", rep, "c8_single_id",
                                   ["pw-link", "-d", ids1[0]]) if ids1 else None
        res["c8_after"] = link_rows()

        # l1 listing slot-binding
        step("s1", rep, "l1_link", ["pw-link", A, B])
        res["l1_o_all"] = step("s1", rep, "l1_o_all", ["pw-link", "-o"])
        res["l1_o_glob"] = step("s1", rep, "l1_o_glob",
                                ["pw-link", "-o", f"{PREFIX}ns_a:*"])
        res["l1_i_glob"] = step("s1", rep, "l1_i_glob",
                                ["pw-link", "-i", f"{PREFIX}ns_b:*"])
        res["l1_i_glob2"] = step("s1", rep, "l1_i_glob2",
                                 ["pw-link", "-i", "", f"{PREFIX}ns_b:*"])
        res["l1_l_pattern"] = step("s1", rep, "l1_l_pattern",
                                   ["pw-link", "-l", f"{PREFIX}ns_a:*"])
        res["l1_l_none"] = step("s1", rep, "l1_l_none",
                                ["pw-link", "-l", "zzz_nomatch:*"])

        # l2 -w with valid pair (bounded) and missing port (bounded)
        res["l2_wait_valid"] = step("s1", rep, "l2_wait_valid",
                                    ["pw-link", "-w", A2, B2], timeout=4)
        res["l2_wait_missing_out"] = step("s1", rep, "l2_wait_missing_out",
                                          ["pw-link", "-w", f"{PREFIX}ns_a:monitor_ZZ", B],
                                          timeout=3)
        res["l2_wait_missing_in"] = step("s1", rep, "l2_wait_missing_in",
                                         ["pw-link", "-w", A, f"{PREFIX}ns_b:playback_ZZ"],
                                         timeout=3)
        res["l2_links_after"] = link_rows()
    finally:
        disconnect_all_own()
        res["teardown"] = {"a": unload(mid_a), "b": unload(mid_b)}
        time.sleep(0.3)
        res["nodes_after"] = [n["name"] for n in nodes_prefix(PREFIX)]
    return res


def fmt_read(nodeid, label):
    return {
        "enum": step("s2", 0, f"{label}_enum",
                     ["pw-cli", "enum-params", str(nodeid), "EnumFormat"]),
        "format": step("s2", 0, f"{label}_format",
                       ["pw-cli", "enum-params", str(nodeid), "Format"]),
    }


def stage_s2(rep):
    """EnumFormat invariant; Format readability; mid-stream set-param."""
    res = {}
    mid, r, txt = load_null(f"{PREFIX}fs")
    res["setup"] = {"mid": mid, "txt": txt}
    time.sleep(0.5)
    nid = node_id(f"{PREFIX}fs")
    ports = [{"id": o["id"], "name": node_props(o).get("port.name")}
             for o in pw_dump() if o.get("type") == "PipeWire:Interface:Port"
             and node_props(o).get("node.id") == nid]
    pin = next((p["id"] for p in ports if p["name"] == "playback_FL"), None)
    res["setup"].update({"node": nid, "ports": ports, "port_in": pin})

    def read(tag):
        out = {"node_enum": step("s2", rep, f"{tag}_node_enum",
                                 ["pw-cli", "enum-params", str(nid), "EnumFormat"]),
               "node_format": step("s2", rep, f"{tag}_node_format",
                                   ["pw-cli", "enum-params", str(nid), "Format"])}
        if pin:
            out["port_enum"] = step("s2", rep, f"{tag}_port_enum",
                                    ["pw-cli", "enum-params", str(pin), "EnumFormat"])
            out["port_format"] = step("s2", rep, f"{tag}_port_format",
                                      ["pw-cli", "enum-params", str(pin), "Format"])
        return out

    res["rest"] = read("rest")
    try:
        p48 = spawn(["pw-play", "--target", f"{PREFIX}fs", "-P", f"node.name={PREFIX}e48",
                     "-P", f"application.name={PREFIX}e48", str(SIL48)])
        time.sleep(1.2)
        sid = node_id(f"{PREFIX}e48")
        res["s48"] = {"node": sid, "alive": p48.poll() is None}
        if sid:
            res["s48"]["format"] = step("s2", rep, "s48_format",
                                        ["pw-cli", "enum-params", str(sid), "Format"])
            res["s48"]["enum"] = step("s2", rep, "s48_enum",
                                      ["pw-cli", "enum-params", str(sid), "EnumFormat"])
        res["during48"] = read("dur48")
        res["links48"] = link_rows()
        res["mid_setparam_sink"] = step(
            "s2", rep, "mid_setparam_sink",
            ["pw-cli", "set-param", str(nid), "Format",
             "{ mediaType: 1, mediaSubtype: 1, format: 259, rate: 44100, channels: 2 }"])
        res["post_sink"] = read("postsink")
        res["links_post"] = link_rows()
        res["stream_alive_post"] = p48.poll() is None
        if sid:
            res["mid_setparam_stream"] = step(
                "s2", rep, "mid_setparam_stream",
                ["pw-cli", "set-param", str(sid), "Format",
                 "{ mediaType: 1, mediaSubtype: 1, format: 259, rate: 44100, channels: 2 }"])
            res["stream_alive_post2"] = p48.poll() is None
        res["stop48"] = stop(p48)
        time.sleep(0.6)
        res["after48"] = read("after48")
        p441 = spawn(["pw-play", "--target", f"{PREFIX}fs", "-P", f"node.name={PREFIX}e441",
                      "-P", f"application.name={PREFIX}e441", str(SIL441)])
        time.sleep(1.2)
        sid2 = node_id(f"{PREFIX}e441")
        res["s441"] = {"node": sid2, "alive": p441.poll() is None}
        if sid2:
            res["s441"]["format"] = step("s2", rep, "s441_format",
                                         ["pw-cli", "enum-params", str(sid2), "Format"])
        res["during441"] = read("dur441")
        res["stop441"] = stop(p441)
        time.sleep(0.5)
        res["after441"] = read("after441")
    finally:
        res["teardown"] = unload(mid)
        time.sleep(0.3)
        res["nodes_after"] = [n["name"] for n in nodes_prefix(PREFIX)]
    return res


def stream_leg(rep, tag, app, target, extra_props=(), tone=SIL48, settle=1.2,
               label=None, node_suffix=""):
    """Spawn a stream, return handle dict; caller must stop it."""
    node = f"{app}{node_suffix}"
    argv = ["pw-play"]
    if target:
        argv += ["--target", target]
    argv += ["-P", f"application.name={app}", "-P", f"node.name={node}"]
    for p in extra_props:
        argv += ["-P", p]
    argv += [str(tone)]
    p = spawn(argv)
    time.sleep(settle)
    return {"p": p, "node": node, "nid": node_id(node), "argv": argv}


def sink_input_index(app):
    r = sh(["pactl", "list", "sink-inputs"])
    idx, cur = None, None
    for line in r["out"].decode("utf-8", "replace").splitlines():
        m = re.match(r"^Sink Input #(\d+)", line)
        if m:
            cur = m.group(1)
        if "application.name" in line and app in line:
            idx = cur
    return idx


def restore_battery(rep, stage, tag):
    """The store-law battery. Fresh r90b_* keys every leg; pre-value guards."""
    res = {"tag": tag}
    mid_a, _, _ = load_null(f"{PREFIX}ra")
    mid_b, _, _ = load_null(f"{PREFIX}rb")
    mid_c, _, _ = load_null(f"{PREFIX}rc")
    res["setup"] = {"mid_a": mid_a, "mid_b": mid_b, "mid_c": mid_c}
    time.sleep(0.5)
    store0 = store_meta()
    res["store_before"] = {k: v for k, v in store0.items() if k != "r90b_keys"}

    def key(app):
        return f"Output/Audio:application.name:{app}"

    # P1 creation debounce (fresh key)
    app = f"{PREFIX}cr{rep}{tag[0]}"
    k = key(app)
    res["p1_pre"] = parse_store().get(k)
    h = stream_leg(rep, stage, app, f"{PREFIX}ra", settle=0.0)
    res["p1_wait"] = wait_value(k, None, timeout=8.0)
    res["p1_node_after"] = node_id(h["node"])
    res["p1_stop"] = stop(h["p"])

    # P2 pw-cli Props volume write
    app = f"{PREFIX}pv{rep}{tag[0]}"
    k = key(app)
    h = stream_leg(rep, stage, app, f"{PREFIX}ra")
    res["p2_node"] = h["nid"]
    if h["nid"]:
        res["p2_pre"] = parse_store().get(k)
        res["p2_set"] = step(stage, rep, "p2_setvol",
                             ["pw-cli", "set-param", str(h["nid"]), "Props",
                              "{ volume: 0.5 }"])
        res["p2_wait"] = wait_value(k, lambda e: e.get("volume") == 0.5, timeout=8.0)
    res["p2_stop"] = stop(h["p"])

    # P3 pulse volume write (clean fresh key; the scout's C5 core)
    app = f"{PREFIX}pp{rep}{tag[0]}"
    k = key(app)
    h = stream_leg(rep, stage, app, f"{PREFIX}ra")
    res["p3_node"] = h["nid"]
    idx = sink_input_index(app)
    res["p3_index"] = idx
    if idx:
        res["p3_pre"] = parse_store().get(k)
        res["p3_set"] = step(stage, rep, "p3_setvol",
                             ["pactl", "set-sink-input-volume", idx, "50%"])
        res["p3_wait"] = wait_value(
            k, lambda e: e.get("channelVolumes") == [0.125, 0.125], timeout=8.0)
        if h["nid"]:
            res["p3_live"] = step(stage, rep, "p3_live_props",
                                  ["pw-cli", "enum-params", str(h["nid"]), "Props"])
    res["p3_stop"] = stop(h["p"])

    # P4 replay field split (same key, no --volume)
    h = stream_leg(rep, stage, app, f"{PREFIX}ra", node_suffix="b")
    res["p4_replay_node"] = h["nid"]
    if h["nid"]:
        res["p4_replay_props"] = step(stage, rep, "p4_replay_props",
                                      ["pw-cli", "enum-params", str(h["nid"]), "Props"])
    res["p4_stop"] = stop(h["p"])

    # P5 target store
    app = f"{PREFIX}tg{rep}{tag[0]}"
    k = key(app)
    h = stream_leg(rep, stage, app, f"{PREFIX}ra")
    res["p5_node"] = h["nid"]
    idx = sink_input_index(app)
    res["p5_index"] = idx
    if idx:
        res["p5_pre"] = parse_store().get(k)
        res["p5_move"] = step(stage, rep, "p5_move",
                              ["pactl", "move-sink-input", idx, f"{PREFIX}rb"])
        res["p5_wait"] = wait_value(
            k, lambda e: e.get("target") == f"{PREFIX}rb", timeout=8.0)
    res["p5_stop"] = stop(h["p"])

    # P6 target replay without --target, then with explicit --target
    h = stream_leg(rep, stage, app, None, node_suffix="b", settle=1.3)
    res["p6_replay_node"] = h["nid"]
    res["p6_replay_links"] = link_rows()
    res["p6_replay_meta"] = [
        {"subject": m.get("subject"), "key": m.get("key"), "value": m.get("value")}
        for o in pw_dump() if o.get("type") == "PipeWire:Interface:Metadata"
        and (o.get("props", {}) or {}).get("metadata.name") == "default"
        for m in o.get("metadata", []) if m.get("key") == "target.object"]
    res["p6_replay_stop"] = stop(h["p"])
    h = stream_leg(rep, stage, app, f"{PREFIX}ra", node_suffix="c", settle=1.0)
    res["p6_explicit_node"] = h["nid"]
    res["p6_explicit_links"] = link_rows()
    res["p6_explicit_stop"] = stop(h["p"])

    # P7 stored target that no longer exists (host-state variation)
    app = f"{PREFIX}vt{rep}{tag[0]}"
    k = key(app)
    h = stream_leg(rep, stage, app, f"{PREFIX}ra")
    idx = sink_input_index(app)
    res["p7_index"] = idx
    if idx:
        res["p7_move"] = step(stage, rep, "p7_move",
                              ["pactl", "move-sink-input", idx, f"{PREFIX}rc"])
        res["p7_wait"] = wait_value(
            k, lambda e: e.get("target") == f"{PREFIX}rc", timeout=8.0)
    res["p7_stop"] = stop(h["p"])
    res["p7_unload_c"] = unload(mid_c)
    time.sleep(0.4)
    h = stream_leg(rep, stage, app, None, node_suffix="b", settle=2.2)
    res["p7_replay_node"] = h["nid"]
    res["p7_replay_links"] = link_rows()
    res["p7_replay_stop"] = stop(h["p"])

    # P8 stream opt-out
    app = f"{PREFIX}xo{rep}{tag[0]}"
    k = key(app)
    h = stream_leg(rep, stage, app, f"{PREFIX}ra",
                   extra_props=("state.restore-props=false",), settle=0.0)
    res["p8_absent"] = key_absent(k, timeout=3.0)
    res["p8_stop"] = stop(h["p"])
    app = f"{PREFIX}cc{rep}{tag[0]}"
    k = key(app)
    h = stream_leg(rep, stage, app, f"{PREFIX}ra", settle=0.0)
    res["p8_control_wait"] = wait_value(k, None, timeout=5.0)
    res["p8_control_stop"] = stop(h["p"])

    # P9 device-node opt-out
    mid_o, _, _ = load_null(f"{PREFIX}od{rep}{tag[0]}",
                            extra=["sink_properties=state.restore-props=false"])
    res["p9_optout_mid"] = mid_o
    res["p9_absent"] = key_absent(f"Audio/Sink:node.name:{PREFIX}od{rep}{tag[0]}",
                                  timeout=2.5)
    mid_ctl, _, _ = load_null(f"{PREFIX}oc{rep}{tag[0]}")
    res["p9_control_mid"] = mid_ctl
    res["p9_control_present"] = wait_value(
        f"Audio/Sink:node.name:{PREFIX}oc{rep}{tag[0]}", None, timeout=4.0)
    res["p9_unload_optout"] = unload(mid_o)
    res["p9_unload_control"] = unload(mid_ctl)

    res["teardown"] = {"a": unload(mid_a), "b": unload(mid_b)}
    time.sleep(0.3)
    store9 = store_meta()
    res["store_after"] = {k: v for k, v in store9.items() if k != "r90b_keys"}
    res["r90b_keys_added"] = sorted(set(store9["r90b_keys"]) -
                                    set(store0["r90b_keys"]))
    res["nodes_after"] = [n["name"] for n in nodes_prefix(PREFIX)]
    return res


def stage_s3(rep):
    return restore_battery(rep, "s3", "quiet")


def phantom_unload(mid, sink_name):
    """Recycle-safe replacement for `pactl unload-module <phantom-id>`.

    A phantom id is free, so a raw call could land on a *recycled* foreign
    module (measured: a free id was re-occupied within 4 s by a sibling's
    module). Therefore:
      - id held by my module (args contain sink_name) -> guarded unload;
      - id held by a foreign module -> skip, disclose;
      - id free -> no raw call; witness the error class on an id that cannot
        be assigned (4000000001) instead.
    """
    rows = {m["id"]: m for m in module_table()}
    if int(mid) in rows:
        m = rows[int(mid)]
        if sink_name in m["args"]:
            return {"id": mid, "rc": None, "mine": True,
                    "note": "module alive and mine — phantom claim falsified",
                    "unload": unload(int(mid))}
        return {"id": mid, "skipped": "held_by_foreign", "foreign": m,
                "note": "recycled-index confound; no unload issued"}
    r = unload_raw("4000000001")
    return {"id": mid, "skipped": "id_free_no_raw_call",
            "error_class_witness": r,
            "note": "raw unload of the free phantom id not issued (recycle risk)"}


def probe_module(mid, name, times=(0.0, 0.03, 0.06, 0.12, 0.25, 0.5, 1.0, 2.0)):
    probes = []
    t0 = time.monotonic()
    rows = {}
    for t in times:
        while time.monotonic() - t0 < t:
            time.sleep(0.002)
        if not rows or t < 0.5:
            rows = {m["id"]: m for m in module_table()}
        row = rows.get(int(mid))
        probes.append({
            "t": round(time.monotonic() - t0, 3),
            "module_alive": row is not None,
            "mine": row is not None and name in row["args"],
            "row": row,
            "node": [n["name"] for n in nodes_prefix(name)],
            "in_pactl_sinks": name in sh(["pactl", "list", "sinks", "short"])["out"].decode(),
        })
    return probes


def stage_s4(rep):
    """Pulse module namespace: phantom, by-name unload (safe class), zeroconf."""
    res = {"entry_modules": [m["id"] for m in module_table()]}
    # M1 phantom tunnel (verbatim replay of scout f2b t1)
    r = sh(["pactl", "load-module", "module-tunnel-sink",
            "server=127.0.0.1:1", f"sink_name={PREFIX}tun"])
    mid = r["out"].decode().strip()
    res["m1_load"] = {"rc": r["rc"], "id": mid, "err": r["err"].decode()[:80]}
    if mid.isdigit():
        res["m1_probes"] = probe_module(int(mid), f"{PREFIX}tun")
        res["m1_unload"] = phantom_unload(int(mid), f"{PREFIX}tun")
    # M2 variation: nonexistent unix socket
    r = sh(["pactl", "load-module", "module-tunnel-sink",
            "server=unix:/tmp/r90b_nope.sock", f"sink_name={PREFIX}tun2"])
    mid = r["out"].decode().strip()
    res["m2_load"] = {"rc": r["rc"], "id": mid, "err": r["err"].decode()[:80]}
    if mid.isdigit():
        res["m2_probes"] = probe_module(int(mid), f"{PREFIX}tun2")
        res["m2_unload"] = phantom_unload(int(mid), f"{PREFIX}tun2")
    # M3 variation: discard port
    r = sh(["pactl", "load-module", "module-tunnel-sink",
            "server=127.0.0.1:9", f"sink_name={PREFIX}tun3"])
    mid = r["out"].decode().strip()
    res["m3_load"] = {"rc": r["rc"], "id": mid, "err": r["err"].decode()[:80]}
    if mid.isdigit():
        res["m3_probes"] = probe_module(int(mid), f"{PREFIX}tun3")
        res["m3_unload"] = phantom_unload(int(mid), f"{PREFIX}tun3")
    # M4 reconnect keeps it resident
    r = sh(["pactl", "load-module", "module-tunnel-sink", "server=127.0.0.1:1",
            f"sink_name={PREFIX}tun4", "reconnect_interval_ms=1000"])
    mid = r["out"].decode().strip()
    res["m4_load"] = {"rc": r["rc"], "id": mid, "err": r["err"].decode()[:80]}
    if mid.isdigit():
        time.sleep(0.6)
        res["m4_alive_0.6s"] = int(mid) in set(module_ids())
        res["m4_node"] = [n["name"] for n in nodes_prefix(f"{PREFIX}tun4")]
        res["m4_unload"] = unload(int(mid))
    # M5 C13 replay on a zero-foreign class (module-loopback)
    foreign_before = [m for m in module_table() if m["name"] == "module-loopback"]
    res["m5_foreign_before"] = foreign_before
    mid_a = mid_b = None
    if not foreign_before:
        mid_a, ra, _ = load_null(f"{PREFIX}ra")
        mid_b, rb, _ = load_null(f"{PREFIX}rb")
        l1 = sh(["pactl", "load-module", "module-loopback",
                 f"source={PREFIX}ra.monitor", f"sink={PREFIX}rb",
                 f"node.name={PREFIX}lb1"])
        l2 = sh(["pactl", "load-module", "module-loopback",
                 f"source={PREFIX}ra.monitor", f"sink={PREFIX}rb",
                 f"node.name={PREFIX}lb2"])
        res["m5_loaded"] = {"l1": l1["out"].decode().strip(), "l2": l2["out"].decode().strip(),
                            "rc1": l1["rc"], "rc2": l2["rc"],
                            "n_before": len([m for m in module_table()
                                             if m["name"] == "module-loopback"])}
        res["m5_by_name"] = step("s4", rep, "m5_unload_by_name",
                                 ["pactl", "unload-module", "module-loopback"])
        time.sleep(0.3)
        res["m5_after"] = {
            "n_loopback": len([m for m in module_table()
                               if m["name"] == "module-loopback"]),
            "my_null_sinks_alive": [m for m in (mid_a, mid_b)
                                    if m in module_ids()],
            "foreign_after": [m for m in module_table() if m["name"] == "module-loopback"],
        }
    res["m5_cleanup"] = {"a": unload(mid_a), "b": unload(mid_b)}
    # M6 unstated: is the name form exact, prefix, or substring?
    mid_6a, _, _ = load_null(f"{PREFIX}m6a")
    mid_6b, _, _ = load_null(f"{PREFIX}m6b")
    l1 = sh(["pactl", "load-module", "module-loopback",
             f"source={PREFIX}m6a.monitor", f"sink={PREFIX}m6b",
             f"node.name={PREFIX}lb3"])
    l2 = sh(["pactl", "load-module", "module-loopback",
             f"source={PREFIX}m6a.monitor", f"sink={PREFIX}m6b",
             f"node.name={PREFIX}lb4"])
    res["m6_loaded"] = [l1["out"].decode().strip(), l2["out"].decode().strip()]
    res["m6_prefix_unload"] = step("s4", rep, "m6_prefix",
                                   ["pactl", "unload-module", "module-loopb"])
    time.sleep(0.2)
    res["m6_alive_after_prefix"] = [m["id"] for m in module_table()
                                    if m["name"] == "module-loopback"]
    res["m6_node_name_unload"] = step("s4", rep, "m6_node_name",
                                      ["pactl", "unload-module", f"{PREFIX}m6a"])
    for m in module_table():
        if m["name"] == "module-loopback" and PREFIX in m["args"]:
            res.setdefault("m6_cleanup", []).append(unload(m["id"]))
    res["m6_cleanup_sinks"] = {"a": unload(mid_6a), "b": unload(mid_6b)}
    # M7 zeroconf discover/publish + avahi witness (sink present for publish)
    mid_zc, _, _ = load_null(f"{PREFIX}zc")
    res["m7_discover"] = step("s4", rep, "m7_discover",
                              ["pactl", "load-module", "module-zeroconf-discover"])
    r = sh(["pactl", "load-module", "module-zeroconf-publish", f"{PREFIX}marker=1"])
    mid = r["out"].decode().strip()
    res["m7_publish_load"] = {"rc": r["rc"], "id": mid, "err": r["err"].decode()[:80]}
    if r["rc"] != 0:
        r = sh(["pactl", "load-module", "module-zeroconf-publish"])
        mid = r["out"].decode().strip()
        res["m7_publish_load_plain"] = {"rc": r["rc"], "id": mid,
                                        "err": r["err"].decode()[:80]}
    if mid.isdigit():
        time.sleep(2.0)
        res["m7_alive"] = int(mid) in set(module_ids())
        res["m7_baseline_browse"] = step("s4", rep, "m7_baseline",
                                         ["timeout", "4", "avahi-browse", "-a", "-t", "-p"],
                                         timeout=8)
        res["m7_avahi_sink"] = step("s4", rep, "m7_avahi_sink",
                                    ["timeout", "4", "avahi-browse", "-t", "-r", "-p",
                                     "_pulse-sink._tcp"], timeout=8)
        res["m7_avahi_source"] = step("s4", rep, "m7_avahi_source",
                                      ["timeout", "4", "avahi-browse", "-t", "-r", "-p",
                                       "_pulse-source._tcp"], timeout=8)
        res["m7_unload"] = unload(int(mid))
        res["m7_alive_after_unload"] = int(mid) in set(module_ids())
    res["m7_unload_sink"] = unload(mid_zc)
    # M8/M9 stubs + control
    res["m8_stream_restore"] = step("s4", rep, "m8_stub",
                                    ["pactl", "load-module", "module-stream-restore"])
    res["m9_unknown"] = step("s4", rep, "m9_unknown",
                             ["pactl", "load-module", "module-not-a-module"])
    res["exit_modules"] = [m["id"] for m in module_table()]
    res["my_modules_left"] = my_modules()
    return res


def my_link_props():
    """Full props of every link whose both endpoints are r90b_* nodes."""
    objs = pw_dump()
    names = {o["id"]: node_props(o).get("node.name")
             for o in objs if o.get("type") == "PipeWire:Interface:Node"}
    out = []
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Link":
            continue
        pr = (o.get("info", {}).get("props", {}) or {})
        iname = names.get(pr.get("link.input.node"))
        oname = names.get(pr.get("link.output.node"))
        if str(iname or "").startswith(PREFIX) and str(oname or "").startswith(PREFIX):
            out.append({"id": o["id"], "in": iname, "out": oname, "props": pr})
    return out


def stage_s5(rep):
    """Unstated modes + named gaps."""
    res = {}
    mid_a, _, _ = load_null(f"{PREFIX}la")
    mid_b, _, _ = load_null(f"{PREFIX}lb")
    res["setup"] = {"mid_a": mid_a, "mid_b": mid_b}
    time.sleep(0.5)
    A, B = f"{PREFIX}la:monitor_FL", f"{PREFIX}lb:playback_FL"
    A2, B2 = f"{PREFIX}la:monitor_FR", f"{PREFIX}lb:playback_FR"
    try:
        step("s5", rep, "link", ["pw-link", A, B])
        # -t latency on a null<->null link
        res["t_nullsink"] = step("s5", rep, "t_nullsink", ["pw-link", "-t"])
        res["t_nullsink_v"] = step("s5", rep, "t_nullsink_v", ["pw-link", "-t", "-v"])
        # device-backed link for -t (silence: null sink has no stream)
        spdif = None
        for o in pw_dump():
            if o.get("type") == "PipeWire:Interface:Node" and \
                    "SPDIF" in str(node_props(o).get("node.name", "")):
                spdif = node_props(o).get("node.name")
        res["spdif_node"] = spdif
        if spdif:
            res["t_dev_link"] = step("s5", rep, "t_dev_link",
                                     ["pw-link", A2, f"{spdif}:playback_FL"])
            res["t_device"] = step("s5", rep, "t_device", ["pw-link", "-t"])
            res["t_device_v"] = step("s5", rep, "t_device_v", ["pw-link", "-t", "-v"])
            # named gap: -t with a live (silent) stream on the device-backed link
            p = spawn(["pw-play", "--target", f"{PREFIX}la", "-P",
                       f"node.name={PREFIX}lt", "-P", f"application.name={PREFIX}lt",
                       str(SIL48)])
            time.sleep(1.2)
            res["t_device_stream"] = step("s5", rep, "t_device_stream", ["pw-link", "-t"])
            res["t_device_stream_v"] = step("s5", rep, "t_device_stream_v",
                                            ["pw-link", "-t", "-v"])
            res["t_stream_stop"] = stop(p)
            res["t_device_disc"] = step("s5", rep, "t_device_disc",
                                        ["pw-link", "-d", A2, f"{spdif}:playback_FL"])
        # -p props on connect (sleep before dump: link materialization race)
        res["p_props_passive"] = step("s5", rep, "p_props_passive",
                                      ["pw-link", "-p", '{"link.passive":true}', A2, B2])
        time.sleep(0.3)
        res["p_props_passive_dump"] = my_link_props()
        step("s5", rep, "p_props_disc", ["pw-link", "-d", A2, B2])
        res["p_props_custom"] = step("s5", rep, "p_props_custom",
                                     ["pw-link", "-p", '{"foo":"bar"}', A2, B2])
        time.sleep(0.3)
        res["p_props_custom_dump"] = my_link_props()
        step("s5", rep, "p_props_disc2", ["pw-link", "-d", A2, B2])
        # -v verbose listing
        res["v_links"] = step("s5", rep, "v_links", ["pw-link", "-v", "-l"])
        res["v_outputs"] = step("s5", rep, "v_outputs", ["pw-link", "-v", "-o"])
        # -m: standalone (connect-mode error) and list-prefix forms (bounded)
        res["m_alone"] = step("s5", rep, "m_alone", ["pw-link", "-m"], timeout=2)
        res["m_list"] = step("s5", rep, "m_list", ["pw-link", "-m", "-l"], timeout=2)
        res["m_outputs"] = step("s5", rep, "m_outputs", ["pw-link", "-m", "-o"], timeout=2)
        # -w with a port that appears late
        p = spawn(["pw-link", "-w", f"{PREFIX}late:monitor_FL", B])
        time.sleep(1.5)
        mid_late, _, _ = load_null(f"{PREFIX}late")
        t0 = time.monotonic()
        rc = None
        while time.monotonic() - t0 < 6:
            rc = p.poll()
            if rc is not None:
                break
            time.sleep(0.05)
        if p.poll() is None:
            p.kill()
        out, err = p.communicate()
        res["w_late"] = {"rc": p.returncode, "returned": rc is not None,
                         "ms_after_port": round((time.monotonic() - t0) * 1000, 1)
                         if rc is not None else None,
                         "out": out.decode()[:200], "err": err.decode()[:200]}
        res["w_late_links"] = link_rows()
        res["w_late_unload"] = unload(mid_late)
    finally:
        disconnect_all_own()
        res["teardown"] = {"a": unload(mid_a), "b": unload(mid_b)}
        time.sleep(0.3)
        res["nodes_after"] = [n["name"] for n in nodes_prefix(PREFIX)]
    return res


def stage_s6(rep):
    """Hog load: timing-critical subset under own load."""
    hogs = start_hogs()
    res = {"hogs": hogs}
    try:
        time.sleep(2.0)
        res["restore"] = restore_battery(rep, "s6", "load")
        res["loadavg_mid"] = os.getloadavg()
        # phantom tunnel under load
        r = sh(["pactl", "load-module", "module-tunnel-sink",
                "server=127.0.0.1:1", f"sink_name={PREFIX}tunL"])
        mid = r["out"].decode().strip()
        res["phantom_load"] = {"rc": r["rc"], "id": mid}
        if mid.isdigit():
            res["phantom_probes"] = probe_module(int(mid), f"{PREFIX}tunL")
            res["phantom_unload"] = unload(int(mid))
        # pw-link -w missing under load (bounded 3 s)
        mid_a, _, _ = load_null(f"{PREFIX}wa")
        time.sleep(0.4)
        res["w_missing_load"] = step(
            "s6", rep, "w_missing_load",
            ["pw-link", "-w", f"{PREFIX}wa:monitor_FL", f"{PREFIX}wa:playback_ZZ"],
            timeout=3)
        res["wa_unload"] = unload(mid_a)
        # mid-stream set-param Format under load
        mid_f, _, _ = load_null(f"{PREFIX}fl")
        time.sleep(0.4)
        nid = node_id(f"{PREFIX}fl")
        p = spawn(["pw-play", "--target", f"{PREFIX}fl", "-P", f"node.name={PREFIX}el",
                   "-P", f"application.name={PREFIX}el", str(SIL48)])
        time.sleep(1.2)
        if nid:
            res["fmt_load"] = step(
                "s6", rep, "fmt_load",
                ["pw-cli", "set-param", str(nid), "Format",
                 "{ mediaType: 1, mediaSubtype: 1, format: 259, rate: 44100, channels: 2 }"])
        res["fmt_stop"] = stop(p)
        res["fl_unload"] = unload(mid_f)
    finally:
        res["hogs_stop"] = stop_hogs()
        res["loadavg_end"] = os.getloadavg()
        disconnect_all_own()
        res["nodes_after"] = [n["name"] for n in nodes_prefix(PREFIX)]
        res["my_modules_left"] = my_modules()
    return res


def stage_s7(rep):
    """Cleanup + final census."""
    res = {}
    res["my_modules_before"] = my_modules()
    res["unload_by_id"] = [unload(m["id"]) for m in my_modules()]
    time.sleep(0.3)
    res["disconnected"] = disconnect_all_own()
    r = sh(["bash", "-c", "pgrep -af r90b_ | grep -v pgrep || true"])
    res["procs_r90b"] = r["out"].decode()[:800]
    subprocess.run(["pkill", "-f", "r90b_io_"], capture_output=True)
    time.sleep(0.3)
    res["census"] = census()
    res["store"] = store_meta()
    res["loadavg"] = os.getloadavg()
    res["my_modules_after"] = my_modules()
    r = sh(["bash", "-c", "pgrep -af r90b_ | grep -v pgrep || true"])
    res["procs_r90b_after"] = r["out"].decode()[:400]
    return res


def stage_s8(rep):
    """C10 replay: capture-direction key + dying stream still stores."""
    res = {}
    mid, _, _ = load_null(f"{PREFIX}ca")
    res["setup"] = {"mid": mid}
    time.sleep(0.5)
    try:
        # without the r77-pinned prop
        r = sh(["timeout", "4", "pw-record", "--target", f"{PREFIX}ca",
                f"/tmp/r90b_cap_noprop_{rep}.wav"], timeout=8)
        res["noprop"] = {"rc": r["rc"], "ms": r["ms"],
                         "err": r["err"].decode()[:200],
                         "out": r["out"].decode()[:100]}
        # with the prop
        app = f"{PREFIX}cap{rep}"
        k = f"Input/Audio:application.name:{app}"
        res["prop_pre"] = parse_store().get(k)
        p = spawn(["pw-record", "--target", f"{PREFIX}ca", "-P", "stream.capture.sink=true",
                   "-P", f"application.name={app}", "-P", f"node.name={app}", "/dev/null"])
        res["prop_wait"] = wait_value(k, None, timeout=6.0)
        time.sleep(0.3)
        res["prop_alive"] = p.poll() is None
        res["prop_stop"] = stop(p)
        # dying stream (nonexistent file) still stores
        app2 = f"{PREFIX}dy{rep}"
        k2 = f"Output/Audio:application.name:{app2}"
        res["dying_pre"] = parse_store().get(k2)
        p = spawn(["pw-play", "--target", f"{PREFIX}ca", "-P", f"application.name={app2}",
                   "-P", f"node.name={app2}", "/nonexistent_r90b.wav"])
        time.sleep(0.5)
        res["dying_rc"] = p.poll()
        res["dying_stop"] = stop(p)
        res["dying_wait"] = wait_value(k2, None, timeout=6.0)
    finally:
        res["teardown"] = unload(mid)
        time.sleep(0.3)
        res["nodes_after"] = [n["name"] for n in nodes_prefix(PREFIX)]
    return res


STAGE_FN = {"s0": stage_s0, "s1": stage_s1, "s2": stage_s2, "s3": stage_s3,
            "s4": stage_s4, "s5": stage_s5, "s6": stage_s6, "s7": stage_s7,
            "s8": stage_s8}


def main():
    stage = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    assert stage in STAGE_FN, f"stage must be one of {list(STAGE_FN)}"
    ensure_tones()
    out = {"stage": stage, "reps": reps, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "entry_census": census(), "legs": []}
    for rep in range(1, reps + 1):
        t0 = time.time()
        try:
            r = STAGE_FN[stage](rep)
            r["_wall_s"] = round(time.time() - t0, 2)
        except Exception as e:
            import traceback
            r = {"error": f"{type(e).__name__}: {e}",
                 "tb": traceback.format_exc()[-900:]}
        out["legs"].append({"rep": rep, **r})
        print(f"[{stage}] rep{rep} {round(time.time()-t0,2)}s "
              f"{'ERR' if 'error' in r else ''}", flush=True)
    out["exit_census"] = census()
    out["store_end"] = store_meta()
    (REC / f"{stage}.json").write_text(json.dumps(out, indent=1))
    print("wrote", REC / f"{stage}.json")


if __name__ == "__main__":
    main()
