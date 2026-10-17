#!/usr/bin/env python3
"""R81 BOUNDARY harness — the honest edges of the r81 scout's gst<->pipewire claims.

Seat scope: corpus/live/r81-boundary/ ONLY (untracked receipts). No tracked
file is read for behaviour or written; corpus/fixtures is never imported.
Every leg is bounded three ways: element bound (num-buffers) where it exists,
a wall-clock cap, and a byte cap checked in the SAME loop that owns the
process group (r77 flood lesson). Producers are separate process groups that
the same loop owns and kills.

Isolation: seat-owned names gst_r81_bnd_* , seat-owned null sink gst_r81_bndns
(module index verified against the name immediately before every unload),
never pactl set-default-sink/set-default-source.

Usage: r81_bnd_probe.py <stage> [--reps N]   stages: baseline p1 p2 p3 p4 p5 final
"""
import argparse
import json
import math
import os
import re
import signal
import struct
import subprocess
import sys
import time
import wave
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
RUNS, TMP, REC = OUT / "runs", OUT / "tmp", OUT / "receipts"
for d in (RUNS, TMP, REC):
    d.mkdir(parents=True, exist_ok=True)

NS = "gst_r81_bndns"                 # seat-owned null sink
NS2 = "gst_r81_bndns2"               # seat-owned null sink #2 (reload leg)
PROD = "gst_r81_bnd_prod"            # producer stream node (client-name)
CAPC = "gst_r81_bnd_cap"             # capture stream node (client-name)
SNKC = "gst_r81_bnd_snk"             # playback stream node (client-name)
RAW = "audio/x-raw,format=S16LE,rate=48000,channels=2"
RAW44M = "audio/x-raw,format=S16LE,rate=44100,channels=1"
BYTE_CAP = 4 * 1024 * 1024
ANSI = re.compile(r"\x1b\[[0-9;]*m")
INTEREST = re.compile(r"gst_r81|gst-launch|r78_")
PHYS = re.compile(r"SPDIF|Speaker|Headphones|hdmi-stereo|Line__|Mic__")
PROP_KEEP = re.compile(
    r"^(node\.|stream\.|target\.|media\.|application\.|client\.|object\.|"
    r"priority\.|monitor\.|resample\.|pulse\.|api\.|device\.)")


# --------------------------------------------------------------- primitives
def sh(cmd, timeout=30, env=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           env=env)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return None, "", "timeout"
    except FileNotFoundError as exc:
        return 127, "", repr(exc)


def rm(path):
    p = Path(path)
    if p.exists():
        p.unlink()


def wav_shape(path):
    p = Path(path)
    o = {"exists": p.exists(), "bytes": None, "riff": None, "data": None,
         "frames": None, "ch": None, "rate": None, "bits": None}
    if not p.exists():
        return o
    size = p.stat().st_size
    o["bytes"] = size
    if size < 44:
        o["riff"] = "short"
        return o
    head = p.open("rb").read(64)
    if head[:4] != b"RIFF" or head[8:12] != b"WAVE":
        o["riff"] = "not_wav"
        return o
    riff = struct.unpack("<I", head[4:8])[0]
    o["riff"] = ("finalized" if riff == size - 8 else
                 "placeholder_8" if riff == 8 else
                 "zero" if riff == 0 else
                 "placeholder_7ffff000" if riff == 0x7FFFF000 else
                 "wavenc_streaming" if riff == 0x7FFF0024 else "other:%d" % riff)
    o["ch"] = struct.unpack("<H", head[22:24])[0]
    o["rate"] = struct.unpack("<I", head[24:28])[0]
    o["bits"] = struct.unpack("<H", head[34:36])[0]
    off = 12
    while off + 8 <= 64:
        cid = head[off:off + 4]
        csz = struct.unpack("<I", head[off + 4:off + 8])[0]
        if cid == b"data":
            o["data"] = ("finalized" if csz == size - (off + 8) else
                         "placeholder_7ffff000" if csz == 0x7FFFF000 else
                         "zero" if csz == 0 else "other:%d" % csz)
            frame = max(1, (o["ch"] or 1) * ((o["bits"] or 8) // 8))
            o["frames"] = csz // frame
            break
        off += 8 + csz + (csz & 1)
    return o


def pcm_peak(path, limit=48000):
    p = Path(path)
    if not p.exists() or p.stat().st_size < 44:
        return None
    try:
        with wave.open(str(p), "rb") as w:
            n = min(w.getnframes(), limit)
            raw = w.readframes(n)
        if w.getsampwidth() != 2:
            return None
        vals = struct.unpack("<%dh" % (len(raw) // 2), raw)
        return max(abs(v) for v in vals) if vals else 0
    except Exception:
        return None


def err_class(text):
    pats = (
        ("target_not_found", r"stream error: target not found"),
        ("no_such_entity", r"No such entity"),
        ("connection_refused", r"Connection refused|Failed to connect"),
        ("state_change_failed", r"Failed to set pipeline to PAUSED"),
        ("not_negotiated", r"not-negotiated"),
        ("internal_data_stream", r"Internal data stream error"),
        ("no_element", r"No such element or plugin '([^']+)'"),
        ("parse_error", r"WARNING: erroneous|could not parse|syntax error|no property"),
        ("no_such_file", r"No such file or directory"),
        ("other_error", r"ERROR:"),
    )
    for name, pat in pats:
        m = re.search(pat, text)
        if m:
            return name, m.group(0).strip()[:140]
    return None, None


def graph():
    rc, out, err = sh(["pw-dump"], timeout=15)
    if rc != 0:
        return {"err": (err or "")[:160]}
    try:
        objs = json.loads(out)
    except Exception as exc:
        return {"err": repr(exc)}
    nodes, ports, raw_links, clients = {}, {}, [], {}
    for o in objs:
        t = o.get("type", "")
        i = o.get("info") or {}
        p = i.get("props") or {}
        if t.endswith("Node"):
            name = p.get("node.name") or i.get("name") or ("id%d" % o["id"])
            nodes[o["id"]] = {"name": name, "class": p.get("media.class"),
                              "serial": p.get("object.serial"),
                              "state": i.get("state"),
                              "props": ({k: v for k, v in p.items()
                                         if PROP_KEEP.match(k)}
                                        if INTEREST.search(name or "") else None)}
        elif t.endswith("Port"):
            ports[o["id"]] = {"node": i.get("node-id"),
                              "name": p.get("port.name")}
        elif t.endswith("Link"):
            raw_links.append((i.get("output-node-id"), i.get("output-port-id"),
                              i.get("input-node-id"), i.get("input-port-id")))
        elif t.endswith("Client"):
            clients[o["id"]] = p.get("client.name") or p.get("application.name")

    def ep(nid, pid):
        return "%s:%s" % (nodes.get(nid, {}).get("name") or ("id:%s" % nid),
                          ports.get(pid, {}).get("name") or ("pid:%s" % pid))

    links = sorted({"%s -> %s" % (ep(a, b), ep(c, d)) for a, b, c, d in raw_links})
    mine = {n["name"]: {"class": n["class"], "serial": n["serial"],
                        "state": n["state"], "props": n["props"]}
            for n in nodes.values() if n["props"] is not None}
    seat = sorted([("%s#%s" % (n["name"], n["serial"]), n["class"], n["state"])
                   for n in nodes.values()
                   if (n["name"] or "").startswith("gst_r81_bnd")])
    phys = sorted(n["name"] for n in nodes.values()
                  if n["props"] is None and PHYS.search(n["name"] or ""))
    return {"links": links, "mine": mine, "seat": seat, "phys": phys,
            "node_count": len(nodes), "clients": len(clients)}


# ------------------------------------------------------------- module rails
def mod_lines():
    rc, out, _ = sh(["pactl", "list", "short", "modules"])
    return out.splitlines() if rc == 0 else []


def module_for(name):
    """Return (index, verbatim line) of the module whose args carry `name`."""
    for line in mod_lines():
        parts = line.split("\t")
        if len(parts) >= 3 and "module-null-sink" in parts[1] and name in parts[2]:
            return int(parts[0]), line
    return None, None


def load_ns(name=NS):
    rc, out, err = sh(["pactl", "load-module", "module-null-sink",
                       "sink_name=" + name,
                       "sink_properties=device.description=" + name])
    idx = int(out.strip()) if rc == 0 and out.strip().isdigit() else None
    return {"rc": rc, "index": idx, "stdout": out.strip(), "stderr": err.strip()}


def unload_verified(name=NS):
    """Unload the module that owns `name`, index re-read and matched now.

    Records the seat-node count before and after so a duplicate-name
    contamination (two modules with the same sink_name) is visible.
    """
    idx, line = module_for(name)
    if idx is None:
        return {"rc": None, "reason": "no module matches name", "name": name,
                "nodes_before": ns_nodes(name)}
    again, line2 = module_for(name)
    if again != idx:
        return {"rc": None, "reason": "index changed between reads",
                "first": idx, "second": again, "name": name}
    dup = len([l for l in mod_lines() if name in l])
    before = ns_nodes(name)
    rc, out, err = sh(["pactl", "unload-module", str(idx)])
    time.sleep(0.12)
    return {"rc": rc, "index": idx, "verified_line": line2, "dup_modules": dup,
            "nodes_before": before, "nodes_after": ns_nodes(name),
            "stdout": out.strip(), "stderr": err.strip(), "name": name}


def ns_nodes(name=NS):
    """Count live pw nodes named `name` (duplicates visible, unlike `mine`)."""
    rc, out, _ = sh(["pw-dump"], timeout=15)
    if rc != 0:
        return None
    try:
        objs = json.loads(out)
    except Exception:
        return None
    n = 0
    for o in objs:
        if o.get("type", "").endswith("Node"):
            p = (o.get("info") or {}).get("props") or {}
            if p.get("node.name") == name:
                n += 1
    return n


def ensure_single_ns(name=NS, want_nodes=1):
    """Force exactly one live null sink called `name`, then report the state.

    Unloads EVERY module whose args carry the name (index re-read each time),
    waits for the node count to drop to 0, loads one, waits for count 1.
    """
    rec = {"name": name, "pre_modules": [l for l in mod_lines() if name in l],
           "pre_nodes": ns_nodes(name), "unloads": []}
    for _ in range(8):
        idx, line = module_for(name)
        if idx is None:
            break
        rc, out, err = sh(["pactl", "unload-module", str(idx)])
        rec["unloads"].append({"index": idx, "line": line, "rc": rc,
                               "stderr": err.strip()[:120]})
        time.sleep(0.12)
    for _ in range(60):
        if ns_nodes(name) == 0:
            break
        time.sleep(0.05)
    rec["nodes_after_unload"] = ns_nodes(name)
    rec["load"] = load_ns(name)
    for _ in range(60):
        if ns_nodes(name) == want_nodes:
            break
        time.sleep(0.05)
    rec["nodes_after_load"] = ns_nodes(name)
    rec["post_modules"] = [l for l in mod_lines() if name in l]
    print("  [ensure_single_ns %s] pre_nodes=%s after_unload=%s after_load=%s mods=%d" % (
        name, rec["pre_nodes"], rec["nodes_after_unload"],
        rec["nodes_after_load"], len(rec["post_modules"])))
    return rec


def sinks():
    rc, out, _ = sh(["pactl", "list", "short", "sinks"])
    return [ln for ln in out.splitlines() if rc == 0]


def sources():
    rc, out, _ = sh(["pactl", "list", "short", "sources"])
    return [ln for ln in out.splitlines() if rc == 0]


# ---------------------------------------------------------------------- leg
class Prod:
    """A producer process group the leg loop owns."""

    def __init__(self, name, argv, at=0.0, kill_at=None, env_extra=None):
        self.name, self.argv, self.at, self.kill_at = name, argv, at, kill_at
        self.env_extra = env_extra
        self.p = None
        self.pgid = None
        self.started = None
        self.killed = None
        self.rc = None
        self.ended = None

    def start(self, t0):
        env = dict(os.environ)
        env.update(self.env_extra or {})
        self.p = subprocess.Popen(self.argv, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.PIPE, text=True, env=env,
                                  start_new_session=True)
        self.pgid = os.getpgid(self.p.pid)
        self.started = round(time.monotonic() - t0, 3)

    def tick(self, t0, el):
        if self.p is None:
            return
        if self.p.poll() is not None:
            if self.rc is None:
                self.rc = self.p.returncode
                self.ended = round(el, 3)
            return
        if self.kill_at is not None and el >= self.kill_at:
            try:
                os.killpg(self.pgid, signal.SIGKILL)
                self.killed = "SIGKILL@%.2f" % el
            except ProcessLookupError:
                self.killed = "already_gone"
            self.kill_at = None

    def finish(self):
        if self.p is None:
            return {}
        try:
            self.p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(self.pgid, signal.SIGKILL)
            self.p.wait(timeout=5)
        if self.rc is None:
            self.rc = self.p.returncode
        err = ANSI.sub("", self.p.stderr.read() or "")
        return {"name": self.name, "argv": self.argv, "at": self.at,
                "kill_at": self.kill_at, "started": self.started,
                "ended": self.ended, "killed": self.killed, "rc": self.rc,
                "stderr_head": err.strip().splitlines()[:3]}


def head48(path):
    p = Path(path)
    if not p.exists():
        return None
    b = p.open("rb").read(48)
    return {"len": len(b), "hex": b.hex(),
            "riff_size": struct.unpack("<I", b[4:8])[0] if len(b) >= 8 else None,
            "data_size": struct.unpack("<I", b[40:44])[0] if len(b) >= 44 else None}


def leg(name, argv, *, stage, rep=0, env_extra=None, out_path=None,
        wall_cap=6.0, byte_cap=BYTE_CAP, size_every=0.05, graph_every=0.35,
        at=(), producers=(), note=None, keep=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    if out_path:
        rm(out_path)
    argv = list(argv)
    t0 = time.monotonic()
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                         text=True, env=env, start_new_session=True)
    pgid = os.getpgid(p.pid)
    prods = list(producers)
    sizes, snaps, actions = [], [], []
    pend_at = sorted(at, key=lambda x: x[0])
    next_size = t0
    next_graph = t0 + 0.15
    killed = None
    while True:
        now = time.monotonic()
        el = now - t0
        for pr in prods:
            if pr.p is None and el >= pr.at:
                pr.start(t0)
            pr.tick(t0, el)
        if p.poll() is not None:
            break
        while pend_at and el >= pend_at[0][0]:
            _, fn = pend_at.pop(0)
            try:
                res = fn()
            except Exception as exc:                      # pragma: no cover
                res = {"exc": repr(exc)}
            actions.append({"t": round(el, 3), "result": res})
        if now >= next_size:
            sz = (Path(out_path).stat().st_size
                  if out_path and Path(out_path).exists() else None)
            sizes.append((round(el, 3), sz))
            next_size += size_every
        if now >= next_graph:
            snaps.append({"t": round(el, 3), "g": graph()})
            next_graph += graph_every
        if out_path and Path(out_path).exists() and \
                Path(out_path).stat().st_size > byte_cap:
            killed = "bytecap:%d" % Path(out_path).stat().st_size
            os.killpg(pgid, signal.SIGKILL)
            break
        if el > wall_cap:
            killed = "wallcap"
            os.killpg(pgid, signal.SIGKILL)
            break
        time.sleep(0.006)
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:                     # pragma: no cover
        os.killpg(pgid, signal.SIGKILL)
        p.wait(timeout=5)
    err = ANSI.sub("", p.stderr.read() or "")
    rc = p.returncode
    cls, hit = err_class(err)
    prod_recs = [pr.finish() for pr in prods]
    kept = None
    if keep and out_path and Path(out_path).exists():
        import shutil
        Path(keep).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(out_path, keep)
        kept = {"path": keep, "bytes": Path(keep).stat().st_size,
                "sha256": __import__("hashlib").sha256(
                    Path(keep).read_bytes()).hexdigest(),
                "head48": head48(keep)}
    rec = {"name": name, "stage": stage, "rep": rep, "argv": argv,
           "env_extra": env_extra or None, "rc": rc,
           "signal": signal.Signals(-rc).name if (rc or 0) < 0 else None,
           "killed": killed, "elapsed_s": round(time.monotonic() - t0, 3),
           "stderr_head": err.strip().splitlines()[:4], "err_class": cls,
           "err_hit": hit, "wall_cap": wall_cap, "byte_cap": byte_cap,
           "producers": prod_recs, "actions": actions,
           "sizes": sizes, "samples": snaps,
           "post": graph(), "out": wav_shape(out_path) if out_path else None,
           "out_peak": pcm_peak(out_path) if out_path else None,
           "kept": kept, "note": note}
    d = RUNS / stage / ("%s_r%d" % (name, rep))
    d.mkdir(parents=True, exist_ok=True)
    (d / "cmd.txt").write_text(" ".join(argv) + "\n")
    if env_extra:
        (d / "env.txt").write_text(json.dumps(env_extra) + "\n")
    (d / "stderr.txt").write_text(err)
    (d / "receipt.json").write_text(json.dumps(rec, indent=1))
    last = sizes[-1][1] if sizes else None
    grow = None
    if sizes:
        vals = [s for _, s in sizes if s is not None]
        grow = (vals[-1] - vals[0]) if len(vals) > 1 else 0
    print("  %-26s r%d rc=%-4s %-16s sz=%-9s grow=%-8s %s" % (
        name, rep, rc, cls or "-", last, grow,
        (rec["post"]["links"][:1] if rec["post"].get("links") else "")))
    if out_path:
        rm(out_path)
    return rec


def receipt(stage, body, extra=None):
    doc = {"probe": stage, "host": os.uname().nodename,
           "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "toolchain": toolchain(), "byte_cap_bytes": BYTE_CAP,
           "body": body}
    if extra:
        doc.update(extra)
    p = REC / ("%s.json" % stage)
    p.write_text(json.dumps(doc, indent=1))
    print("[receipt] %s (%d B)" % (p.name, p.stat().st_size))
    return p


def toolchain():
    def one(*a):
        rc, out, err = sh(list(a), timeout=20)
        line = (out + err).strip().splitlines()
        return line[0] if line else None
    return {"gst_launch": one("gst-launch-1.0", "--version"),
            "pw": one("pipewire", "--version"),
            "pactl": one("pactl", "--version"),
            "kernel": os.uname().release, "python": sys.version.split()[0],
            "pkgs": one("pacman", "-Q", "gstreamer", "gst-plugin-pipewire",
                        "pipewire", "libpulse")}


def host_state():
    return {"default_sink": sh(["pactl", "get-default-sink"])[1].strip(),
            "default_source": sh(["pactl", "get-default-source"])[1].strip(),
            "sinks": sinks(), "sources": sources(),
            "modules": mod_lines(),
            "sink_inputs": sh(["pactl", "list", "short", "sink-inputs"])[1].splitlines(),
            "source_outputs": sh(["pactl", "list", "short", "source-outputs"])[1].splitlines(),
            "graph": graph()}


def dir_bytes(p):
    p = Path(p)
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) if p.exists() else 0


# -------------------------------------------------------------------- stages
def stage_baseline():
    st = host_state()
    print(json.dumps({"default_sink": st["default_sink"],
                      "default_source": st["default_source"],
                      "modules": len(st["modules"]),
                      "nodes": st["graph"]["node_count"]}, indent=1))
    receipt("s0-baseline", st)
    return st


def stage_final():
    st = host_state()
    leftovers = [ln for ln in st["modules"] if "gst_r81_bnd" in ln]
    pg = sh(["bash", "-c", "pgrep -af 'gst-launch-1.0|gst_r81_bnd' || true"])[1]
    st["leftover_modules"] = leftovers
    st["leftover_procs"] = [ln for ln in pg.splitlines() if "pgrep" not in ln]
    st["scratch_bytes"] = dir_bytes(OUT)
    print(json.dumps({"leftover_modules": leftovers,
                      "leftover_procs": st["leftover_procs"],
                      "scratch_bytes": st["scratch_bytes"]}, indent=1))
    receipt("s0-final", st)
    return st


def stage_p1(reps=1):
    """on-disconnect vs a peer stream that closes itself."""
    body = {"legs": [], "loads": []}
    d1 = str(TMP / "p1_cap.wav")

    def fresh():
        rec = ensure_single_ns(NS)
        body["loads"].append(rec)
        return rec

    body["load"] = fresh()

    def mkcap(extra, out, **kw):
        return leg(
            kw.pop("name"), ["gst-launch-1.0", "-q", "pipewiresrc",
                             "client-name=" + CAPC, "target-object=" + NS,
                             "stream-properties=props,stream.capture.sink=true",
                             "num-buffers=1000"] + extra +
            ["!", RAW, "!", "wavenc", "!", "filesink", "location=" + out],
            stage="p1", out_path=out, **kw)

    # P1-a: producer exits NATURALLY (EOS, node destroyed) while sink node lives
    for r in range(reps):
        fresh()
        body["legs"].append(mkcap(
            ["on-disconnect=error"], d1, name="a_prod_eos", rep=r,
            wall_cap=5.0,
            producers=[Prod("prod", ["gst-launch-1.0", "-q", "audiotestsrc",
                                     "wave=sine", "freq=1000", "num-buffers=60",
                                     "blocksize=4096", "!", RAW, "!",
                                     "pipewiresink", "client-name=" + PROD,
                                     "target-object=" + NS], at=0.0)],
            note="producer ends by num-buffers EOS at ~1.3s; sink node lives"))

    # P1-b: producer killed ABRUPTLY (SIGKILL, client vanishes) while sink lives
    for r in range(reps):
        fresh()
        body["legs"].append(mkcap(
            ["on-disconnect=error"], d1, name="b_prod_kill", rep=r,
            wall_cap=5.0,
            producers=[Prod("prod", ["gst-launch-1.0", "-q", "audiotestsrc",
                                     "wave=sine", "freq=1000", "num-buffers=200000",
                                     "!", RAW, "!", "pipewiresink",
                                     "client-name=" + PROD,
                                     "target-object=" + NS], at=0.0,
                          kill_at=1.5)],
            note="producer SIGKILLed at 1.5s"))

    # P1-c: control — on-disconnect=error vs TARGET NODE destruction (scout law)
    for r in range(reps):
        fresh()
        body["legs"].append(mkcap(
            ["on-disconnect=error"], d1, name="c_target_unload", rep=r,
            wall_cap=4.0,
            at=[(1.2, lambda: unload_verified(NS))],
            note="sink module unloaded at 1.2s (scout's freeze law control)"))

    # P1-d: same as (c) but on-disconnect=none — is the enum live on this path?
    for r in range(reps):
        fresh()
        body["legs"].append(mkcap(
            ["on-disconnect=none"], d1, name="d_target_unload_none", rep=r,
            wall_cap=4.0,
            at=[(1.2, lambda: unload_verified(NS))],
            note="target unload, on-disconnect=none"))

    # P1-e: capture linked DIRECTLY to the producer stream node (peer == stream)
    def prodargv():
        return ["gst-launch-1.0", "-q", "audiotestsrc", "wave=sine", "freq=1000",
                "num-buffers=200000", "!", RAW, "!", "pipewiresink",
                "client-name=" + PROD, "target-object=" + NS]

    def direct(argv_extra, nm, **kw):
        return leg(nm, ["gst-launch-1.0", "-q", "pipewiresrc",
                        "client-name=" + CAPC, "target-object=" + PROD] +
                   argv_extra + ["num-buffers=1000", "!", RAW, "!", "wavenc", "!",
                                 "filesink", "location=" + d1],
                   stage="p1", out_path=d1, **kw)

    for argv_extra, nm, note in (
            (["stream-properties=props,stream.capture.sink=false", "on-disconnect=error"],
             "e_direct_false", "capture target = a STREAM node; producer dies at 1.5s"),
            (["stream-properties=props,stream.capture.sink=true", "on-disconnect=error"],
             "e_direct_true", "capture.sink=true against a STREAM target"),
            (["on-disconnect=error"], "e_direct_noprop",
             "no stream.capture.sink prop at all, stream target"),
            (["stream-properties=props,stream.capture.sink=false", "on-disconnect=none"],
             "e_direct_none", "true peer death, on-disconnect=none"),
            (["stream-properties=props,stream.capture.sink=false", "on-disconnect=eos"],
             "e_direct_eos", "true peer death, on-disconnect=eos")):
        for r in range(reps):
            fresh()
            body["legs"].append(direct(argv_extra, nm, rep=r, wall_cap=4.0,
                                       producers=[Prod("prod", prodargv(), at=0.0,
                                                       kill_at=1.5)],
                                       note=note))
    # does the capture resume if a SAME-NAME producer returns?
    for r in range(reps):
        fresh()
        body["legs"].append(direct(
            ["stream-properties=props,stream.capture.sink=false", "on-disconnect=error"],
            "e_direct_return", rep=r, wall_cap=5.0,
            producers=[Prod("prod", prodargv(), at=0.0, kill_at=1.2),
                       Prod("prod2", prodargv(), at=2.4, kill_at=4.5)],
            note="producer killed at 1.2s, a NEW same-name producer appears at 2.4s"))
    unload_verified(NS)
    receipt("s1-disconnect", body)
    return body


def stage_p2(reps=1):
    """PIPEWIRE_REMOTE / PIPEWIRE_NODE / PIPEWIRE_PROPS interplay."""
    body = {"load": ensure_single_ns(NS), "legs": []}
    wav = str(TMP / "p2_cap.wav")
    sil = ["audiotestsrc", "wave=silence", "num-buffers=96", "!", RAW, "!"]

    def play(extra_env, nm, **kw):
        return leg(nm, ["gst-launch-1.0", "-q"] + sil +
                   ["pipewiresink", "client-name=" + SNKC],
                   stage="p2", env_extra=extra_env, **kw)

    def cap(extra_env, nm, **kw):
        return leg(nm, ["gst-launch-1.0", "-q", "pipewiresrc",
                        "client-name=" + CAPC,
                        "stream-properties=props,stream.capture.sink=true",
                        "num-buffers=1000", "!", RAW, "!", "wavenc", "!",
                        "filesink", "location=" + wav],
                   stage="p2", env_extra=extra_env, out_path=wav, **kw)

    for r in range(reps):
        body["legs"].append(cap({"PIPEWIRE_NODE": NS}, "c1_envnode", rep=r,
                                wall_cap=4.0,
                                note="capture: env PIPEWIRE_NODE=NS, prop capture.sink, no target-object"))
    for r in range(reps):
        body["legs"].append(cap({"PIPEWIRE_NODE": NS + ".monitor"}, "c2_envnode_mon", rep=r,
                                wall_cap=4.0, note="env PIPEWIRE_NODE=<NS>.monitor on capture"))
    for r in range(reps):
        body["legs"].append(play({"PIPEWIRE_REMOTE": "pipewire-0"}, "p1_remote_ok", rep=r,
                                 wall_cap=3.0, note="env PIPEWIRE_REMOTE=pipewire-0 (valid, explicit)"))
    for r in range(reps):
        body["legs"].append(play({"PIPEWIRE_REMOTE": "bogus_r81_bnd"}, "p2_remote_bogus", rep=r,
                                 wall_cap=3.0, note="env PIPEWIRE_REMOTE=bogus on playback"))
    for r in range(reps):
        body["legs"].append(cap({"PIPEWIRE_REMOTE": "bogus_r81_bnd"}, "c3_remote_bogus", rep=r,
                                wall_cap=3.0, note="env PIPEWIRE_REMOTE=bogus on capture"))
    for r in range(reps):
        body["legs"].append(play({"PIPEWIRE_REMOTE": "bogus_r81_bnd",
                                  "PIPEWIRE_NODE": NS}, "p3_remote_bogus_node", rep=r,
                                 wall_cap=3.0,
                                 note="bogus remote + PIPEWIRE_NODE=NS: does the remote knob bite?"))
    for r in range(reps):
        body["legs"].append(play({"PIPEWIRE_PROPS": "{ node.target=" + NS + " }",
                                  "PIPEWIRE_NODE": "no_such_r81_bnd"}, "p4_props_vs_node", rep=r,
                                 wall_cap=3.0,
                                 note="env-internal precedence: PIPEWIRE_PROPS node.target vs PIPEWIRE_NODE"))
    for r in range(reps):
        body["legs"].append(play({"PIPEWIRE_NODE": NS}, "p5_envnode", rep=r, wall_cap=3.0,
                                 note="playback env PIPEWIRE_NODE=NS (scout re-check)"))
    unload_verified(NS)
    receipt("s2-env", body)
    return body


def stage_p3(reps=1):
    """element prop vs stream-properties on the CAPTURE side."""
    body = {"load": ensure_single_ns(NS), "legs": []}
    wav = str(TMP / "p3_cap.wav")
    CS = "stream.capture.sink=true"

    def cap(argv_extra, nm, **kw):
        return leg(nm, ["gst-launch-1.0", "-q", "pipewiresrc",
                        "client-name=" + CAPC] + argv_extra +
                   ["num-buffers=1000", "!", RAW, "!", "wavenc", "!", "filesink",
                    "location=" + wav],
                   stage="p3", out_path=wav, **kw)

    rows = [
        (["target-object=" + NS, "stream-properties=props," + CS + ",target.object=no_such_r81_bnd"],
         "f1_prop_beats_sp", "element target-object=NS + sp target.object=no_such"),
        (["target-object=no_such_r81_bnd", "stream-properties=props," + CS + ",target.object=" + NS],
         "f2_sp_vs_bogus_prop", "element target-object=bogus + sp target.object=NS"),
        (["target-object=" + NS, "stream-properties=props," + CS + ",node.target=no_such_r81_bnd"],
         "f3_prop_vs_sp_nodetarget", "element NS + sp node.target=bogus"),
        (["stream-properties=props," + CS + ",node.target=" + NS], "f4_sp_nodetarget_only",
         "no element prop; sp node.target=NS"),
        (["target-object=" + NS], "f5_prop_no_capsink",
         "element prop alone, NO stream.capture.sink"),
        (["target-object=" + NS + ".monitor", "stream-properties=props," + CS],
         "f6_monitor_suffix", "target-object=<NS>.monitor + prop (scout c4 re-check)"),
    ]
    for argv_extra, nm, note in rows:
        for r in range(reps if nm in ("f1_prop_beats_sp", "f2_sp_vs_bogus_prop",
                                      "f3_prop_vs_sp_nodetarget", "f5_prop_no_capsink")
                       else 1):
            body["legs"].append(cap(argv_extra, nm, rep=r, wall_cap=4.0, note=note))
    unload_verified(NS)
    receipt("s3-capture-prec", body)
    return body


def stage_p4(reps=1):
    """pulsesrc device= variants the scout did not try (record-side strictness)."""
    body = {"load": ensure_single_ns(NS), "legs": []}
    wav = str(TMP / "p4_cap.wav")

    def rec(extra, nm, env_extra=None, nb=8, **kw):
        return leg(nm, ["gst-launch-1.0", "-q", "pulsesrc", "client-name=" + CAPC] +
                   extra + ["num-buffers=%d" % nb, "!", RAW, "!", "wavenc", "!", "filesink",
                            "location=" + wav],
                   stage="p4", out_path=wav, env_extra=env_extra, **kw)

    rows = [
        (["device=" + NS], "g1_sinkname", None, "a SINK name handed to pulsesrc"),
        (["device=" + NS + ".monitor"], "g2_monitor_name", None, "a REAL source name (null-sink monitor)"),
        (["device=no_such_r81_bnd"], "g3_bogus", None, "scout's refusal row (re-check)"),
        (["device="], "g4_empty_device", {"PULSE_SOURCE": NS + ".monitor"},
         "device= (empty) + PULSE_SOURCE=<NS>.monitor"),
        ([], "g5_env_only", {"PULSE_SOURCE": NS + ".monitor"}, "bare pulsesrc, PULSE_SOURCE set"),
        (["device=no_such_r81_bnd"], "g6_device_vs_env", {"PULSE_SOURCE": NS + ".monitor"},
         "device=bogus + PULSE_SOURCE=<NS>.monitor (who wins)"),
        (["device=" + NS + ".monitor"], "g7_monitor_sourceprop",
         {"PULSE_SOURCE": "no_such_r81_bnd"}, "device=<NS>.monitor beats bogus PULSE_SOURCE"),
        (["device=" + NS + ".monitor", "server=unix:/nonexistent-r81-bnd"], "g8_bad_server",
         None, "valid device but bogus server"),
    ]
    for extra, nm, env_extra, note in rows:
        for r in range(reps if nm in ("g2_monitor_name", "g4_empty_device", "g6_device_vs_env")
                       else 1):
            body["legs"].append(rec(extra, nm, env_extra=env_extra, rep=r,
                                    wall_cap=3.0, note=note))
    # frame-bound honesty on the pulse record path: num-buffers x 480 frames?
    for nb in (20, 200):
        for r in range(reps):
            body["legs"].append(rec(["device=" + NS + ".monitor"], "g9_numbuf_%d" % nb,
                                    rep=r, nb=nb, wall_cap=6.0,
                                    note="pulse frame-bound check: num-buffers=%d x 480?" % nb))
    for r in range(reps):
        body["legs"].append(rec(["device=" + NS + ".monitor", "blocksize=4096"],
                                "g10_blocksize_4096", rep=r, wall_cap=6.0,
                                note="num-buffers=8 with blocksize=4096 (r77: 1024 frames/buffer)"))
    unload_verified(NS)
    receipt("s4-pulsesrc", body)
    return body


def stage_p5(reps=1):
    """the frozen-file law at buffer granularity + target-name return.

    STRICT single-instance discipline: every leg group starts from
    ensure_single_ns() (exactly one live node named NS, one module), and each
    unload records the node count before/after so duplicate-name
    contamination is visible rather than silent.
    """
    body = {"legs": [], "loads": []}
    wav = str(TMP / "p5_cap.wav")
    prod = Prod("prod", ["gst-launch-1.0", "-q", "audiotestsrc", "wave=sine",
                         "freq=1000", "num-buffers=200000", "!", RAW, "!",
                         "pipewiresink", "client-name=" + PROD,
                         "target-object=" + NS], at=0.0)

    def fresh():
        """One live null sink named NS, asserted immediately before the leg."""
        rec = ensure_single_ns(NS)
        body["loads"].append(rec)
        return rec

    def cap(caps, nb, nm, **kw):
        return leg(nm, ["gst-launch-1.0", "-q", "pipewiresrc", "client-name=" + CAPC,
                        "target-object=" + NS,
                        "stream-properties=props,stream.capture.sink=true",
                        "num-buffers=%d" % nb, "!", caps, "!", "wavenc", "!",
                        "filesink", "location=" + wav],
                   stage="p5", out_path=wav, size_every=0.02, graph_every=0.3, **kw)

    # h1: unload at 1.2s, freeze granularity, then target NAME returns at 2.6s
    for r in range(reps):
        fresh()
        body["legs"].append(cap(RAW, 1000, "h1_freeze_then_reload", rep=r,
                                wall_cap=5.0, producers=[Prod("prod", prod.argv,
                                                              at=0.0, kill_at=3.0)],
                                at=[(1.2, lambda: unload_verified(NS)),
                                    (2.6, lambda: ensure_single_ns(NS))],
                                note="unload NS at 1.2s; reload a SAME-NAME null sink at 2.6s"))
    # h2: same freeze, no reload (control) — is the freeze size the same?
    for r in range(reps):
        fresh()
        body["legs"].append(cap(RAW, 1000, "h2_freeze_control", rep=r,
                                wall_cap=4.0,
                                producers=[Prod("prod", prod.argv, at=0.0, kill_at=3.0)],
                                at=[(1.2, lambda: unload_verified(NS))],
                                note="unload NS at 1.2s, nothing returns"))
    # h2b: MISSING target + capture.sink prop — the silent-fallback cell, measured
    for r in range(reps):
        body["loads"].append({"name": NS, "note": "no NS on purpose (missing-target cell)",
                              "pre_nodes": ns_nodes(NS)})
        body["legs"].append(cap(RAW, 1000, "h2b_missing_target_fallback", rep=r,
                                wall_cap=4.0,
                                producers=[Prod("prod", prod.argv, at=0.0, kill_at=3.0)],
                                note="target never exists: capture.sink prop -> default monitor?"))
    # h3: num-buffers boundary — 20 buffers, no unload: does it EOS+finalize?
    for r in range(reps):
        fresh()
        body["legs"].append(cap(RAW, 20, "h3_numbuf_20_eos", rep=r, wall_cap=4.0,
                                producers=[Prod("prod", prod.argv, at=0.0, kill_at=3.0)],
                                note="num-buffers=20, target never destroyed"))
    # h4: same as h3 but unload BEFORE the bound elapses (0.2s)
    for r in range(reps):
        fresh()
        body["legs"].append(cap(RAW, 20, "h4_numbuf20_unload_early", rep=r, wall_cap=4.0,
                                producers=[Prod("prod", prod.argv, at=0.0, kill_at=3.0)],
                                at=[(0.2, lambda: unload_verified(NS))],
                                note="num-buffers=20 but target destroyed at 0.2s"))
    # h5: different caps (44.1k mono) freeze size check
    for r in range(reps):
        fresh()
        body["legs"].append(cap(RAW44M, 1000, "h5_freeze_44k_mono", rep=r, wall_cap=4.0,
                                producers=[Prod("prod", prod.argv, at=0.0, kill_at=3.0)],
                                at=[(1.2, lambda: unload_verified(NS))],
                                note="44.1k mono freeze size vs 48k stereo"))
    # h6: seat-local PIPEWIRE_QUANTUM — does it move the growth step and freeze grid?
    for q in ("256/48000", "2048/48000"):
        for r in range(reps):
            fresh()
            body["legs"].append(cap(
                RAW, 1000, "h6_quantum_" + q.split("/")[0], rep=r, wall_cap=4.0,
                env_extra={"PIPEWIRE_QUANTUM": q},
                producers=[Prod("prod", prod.argv, at=0.0, kill_at=3.0)],
                at=[(1.2, lambda: unload_verified(NS))],
                note="PIPEWIRE_QUANTUM=%s (client-local), unload at 1.2s" % q))
    # h7: unload with NO producer at all, kept artifact for a raw header receipt
    for r in range(reps):
        fresh()
        body["legs"].append(cap(
            RAW, 1000, "h7_kept_header", rep=r, wall_cap=4.0,
            keep=str(OUT / "artifacts" / ("h7_frozen_r%d.wav" % r)),
            at=[(1.2, lambda: unload_verified(NS))],
            note="no producer (silence), unload at 1.2s, artifact KEPT"))
    body["cleanup"] = ensure_single_ns(NS)      # leaves exactly one module...
    body["unload_final"] = unload_verified(NS)  # ...which is then removed
    body["final_nodes"] = ns_nodes(NS)
    receipt("s5-freeze", body)
    return body


def link_detail():
    """Links with node serials + ids, so duplicate names are separable."""
    rc, out, _ = sh(["pw-dump"], timeout=15)
    if rc != 0:
        return {"err": "pw-dump rc=%s" % rc}
    try:
        objs = json.loads(out)
    except Exception as exc:
        return {"err": repr(exc)}
    names, ports, nodes = {}, {}, []
    for o in objs:
        t = o.get("type", "")
        i = o.get("info") or {}
        p = i.get("props") or {}
        if t.endswith("Node"):
            names[o["id"]] = (p.get("node.name"), p.get("object.serial"),
                              p.get("media.class"))
            if (p.get("node.name") or "").startswith("gst_r81_bnd"):
                nodes.append({"id": o["id"], "name": p.get("node.name"),
                              "serial": p.get("object.serial"),
                              "class": p.get("media.class")})
        elif t.endswith("Port"):
            ports[o["id"]] = (i.get("node-id"), p.get("port.name"))

    def ep(nid, pid):
        nn, ser, _ = names.get(nid, ("?", "?", None))
        return "%s#%s:%s" % (nn, ser, ports.get(pid, (None, "?"))[1])

    raw = []
    for o in objs:
        if not o.get("type", "").endswith("Link"):
            continue
        i = o.get("info") or {}
        raw.append("%s -> %s" % (ep(i.get("output-node-id"), i.get("output-port-id")),
                                 ep(i.get("input-node-id"), i.get("input-port-id"))))
    links = sorted(set(l for l in raw if "gst_r81_bnd" in l))
    return {"seat_nodes": sorted(nodes, key=lambda n: n["id"]), "links": links}


def stage_p6(reps=1):
    """Duplicate sink_name: two live nodes with the same name, one unloaded.

    This is the discipline probe that the p5 pass-1 contamination exposed:
    a name-targeted client and a module unloaded by index do not necessarily
    refer to the same node.
    """
    body = {"legs": [], "rounds": []}
    wav = str(TMP / "p6_cap.wav")
    prod = ["gst-launch-1.0", "-q", "audiotestsrc", "wave=sine", "freq=1000",
            "num-buffers=200000", "!", RAW, "!", "pipewiresink",
            "client-name=" + PROD, "target-object=" + NS]

    for r in range(reps):
        round_rec = {"rep": r}
        round_rec["single"] = ensure_single_ns(NS)
        # add a SECOND module with the identical sink_name
        round_rec["dup_load"] = load_ns(NS)
        for _ in range(40):
            if ns_nodes(NS) == 2:
                break
            time.sleep(0.05)
        round_rec["nodes_after_dup"] = ns_nodes(NS)
        round_rec["modules_after_dup"] = [l for l in mod_lines() if NS in l]
        round_rec["detail_before"] = link_detail()
        # which module is first in the list (oldest index) vs second?
        mods = [(int(l.split("\t")[0]), l) for l in mod_lines() if NS in l]
        mods.sort()
        first_idx, second_idx = mods[0][0], mods[1][0]
        round_rec["first_idx"], round_rec["second_idx"] = first_idx, second_idx

        def unload_first():
            return unload_verified(NS)      # always picks the FIRST matching index

        leg_rec = leg("d1_dup_unload_first", [
            "gst-launch-1.0", "-q", "pipewiresrc", "client-name=" + CAPC,
            "target-object=" + NS,
            "stream-properties=props,stream.capture.sink=true", "num-buffers=1000",
            "!", RAW, "!", "wavenc", "!", "filesink", "location=" + wav],
            stage="p6", rep=r, out_path=wav, wall_cap=5.0, size_every=0.02,
            graph_every=0.3,
            producers=[Prod("prod", prod, at=0.0, kill_at=4.6)],
            at=[(1.2, unload_first),
                (2.4, lambda: {"detail": link_detail(),
                               "nodes": ns_nodes(NS)}),
                (2.8, lambda: unload_verified(NS)),
                (3.6, lambda: {"detail": link_detail(), "nodes": ns_nodes(NS)})],
            note="two same-name modules; unload FIRST at 1.2s, survivor at 2.8s")
        round_rec["leg"] = leg_rec
        round_rec["nodes_end"] = ns_nodes(NS)
        round_rec["detail_end"] = link_detail()
        body["rounds"].append(round_rec)
        body["legs"].append(leg_rec)
        for _ in range(40):
            if ns_nodes(NS) == 0:
                break
            time.sleep(0.05)
    body["final_nodes"] = ns_nodes(NS)
    body["final_modules"] = [l for l in mod_lines() if NS in l]
    receipt("s6-dupname", body)
    return body


STAGES = {"baseline": stage_baseline, "p1": stage_p1, "p2": stage_p2,
          "p3": stage_p3, "p4": stage_p4, "p5": stage_p5, "p6": stage_p6,
          "final": stage_final}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=sorted(STAGES))
    ap.add_argument("--reps", type=int, default=1)
    a = ap.parse_args()
    print("[%s] %s" % (a.stage, datetime.now(timezone.utc).isoformat(timespec="seconds")))
    STAGES[a.stage](reps=a.reps) if a.stage.startswith("p") else STAGES[a.stage]()


if __name__ == "__main__":
    main()
