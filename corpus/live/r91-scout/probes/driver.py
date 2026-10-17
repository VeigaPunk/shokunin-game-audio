#!/usr/bin/env python3
"""r91 SCOUT probe driver — mechanism verification of the r81 capture-freeze law.

Surface: WHY `gst pipewiresrc` freezes on target loss while `pw-record`
re-links.  Source read says: gstpipewiresrc.c sets PW_STREAM_FLAG_DONT_RECONNECT
unconditionally (capture only), the sink does not, pw-cat does not; stream.c
turns the flag into the prop `node.dont-reconnect` ONLY IF the prop is not
already present; WirePlumber prepare-link.lua drops the target for
dont-reconnect items that were already handled.  This driver measures the
on-host prop lattice and the behavioural consequences.

Stages:
  census  — entry/exit host census (read-only)
  props   — live prop lattice of 5 client families, 3 reps each
  loss    — target-loss timeline for 4 capture families, 3 reps each
  recover — manual-relink recovery discriminator on a frozen gst capture, 3 reps

Every leg is triple-bounded: element bound in argv (num-buffers / -n), wall cap,
byte cap checked in the same loop that owns the process group (start_new_session
+ os.killpg).  Seat-owned names only: r91s_* / gst_r91_*.  Never
set-default-sink/source.  Module unloads are always index-verified against the
seat name first.
"""

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import time

ROOT = "/home/vgpnk/Projects/shokunin/audio-shokunin"
SCRATCH = os.path.join(ROOT, "corpus/live/r91-scout")
RUNS = os.path.join(SCRATCH, "runs")
RECEIPTS = os.path.join(SCRATCH, "receipts")
TMP = os.path.join(SCRATCH, "tmp")

NS1 = "r91s_ns1"
NS2 = "r91s_ns2"
BYTE_CAP = 4 * 1024 * 1024

FAMILIES = {
    "F1_pwrec_plain": {
        "prefix": "r91s_pwrec_plain",
        "argv": ["pw-record", "-P", "node.name=r91s_pwrec_plain",
                 "--target", NS1, "-n", "1000000", "{out}"],
    },
    "F2_pwrec_capsink": {
        "prefix": "r91s_pwrec_capsink",
        "argv": ["pw-record", "-P", "stream.capture.sink=true",
                 "-P", "node.name=r91s_pwrec_capsink",
                 "--target", NS1, "-n", "1000000", "{out}"],
    },
    "F3_gst_src_default": {
        "prefix": "gst_r91_src_default",
        "argv": ["gst-launch-1.0", "-q", "pipewiresrc",
                 "client-name=gst_r91_src_default", "target-object=" + NS1,
                 "stream-properties=props,stream.capture.sink=true",
                 "num-buffers=1000000", "!",
                 "audio/x-raw,format=S16LE,rate=48000,channels=2", "!",
                 "wavenc", "!", "filesink", "location={out}"],
    },
    "F4_gst_src_override": {
        "prefix": "gst_r91_src_override",
        "argv": ["gst-launch-1.0", "-q", "pipewiresrc",
                 "client-name=gst_r91_src_override", "target-object=" + NS1,
                 "stream-properties=props,stream.capture.sink=true,node.dont-reconnect=false",
                 "num-buffers=1000000", "!",
                 "audio/x-raw,format=S16LE,rate=48000,channels=2", "!",
                 "wavenc", "!", "filesink", "location={out}"],
    },
    "F5_gst_sink_silence": {
        "prefix": "gst_r91_sink_silence",
        "argv": ["gst-launch-1.0", "-q", "audiotestsrc", "wave=silence",
                 "num-buffers=1000000", "!", "audio/x-raw,format=S16LE,rate=48000,channels=2",
                 "!", "pipewiresink", "client-name=gst_r91_sink_silence",
                 "target-object=" + NS1],
        "no_file": True,
    },
}

TONE_WAV = os.path.join(SCRATCH, "tmp", "r91s_tone.wav")

TONE_ARGV = ["pw-play", "-P", "node.name=r91s_tone_ns2", "--target", NS2, TONE_WAV]

TONE_NS1_ARGV = ["pw-play", "-P", "node.name=r91s_tone_ns1", "--target", NS1, TONE_WAV]


# ---------------------------------------------------------------- helpers

def ensure_tone_wav(path, secs=30, rate=48000, freq=997, amp=8000):
    if os.path.exists(path):
        return
    import wave as _wave
    import struct as _struct
    import math as _math
    with _wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        n = int(secs * rate)
        frames = bytearray()
        for i in range(n):
            v = int(amp * _math.sin(2 * _math.pi * freq * i / rate))
            frames += _struct.pack("<hh", v, v)
        w.writeframes(bytes(frames))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sh(argv, timeout=15, env=None):
    t0 = time.monotonic()
    timed_out = False
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout, env=env)
        out, err, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, err, rc, timed_out = (e.stdout or b""), (e.stderr or b""), None, True
    return {
        "argv": argv, "rc": rc, "timed_out": timed_out,
        "stdout": out.decode("utf-8", "replace"),
        "stderr": err.decode("utf-8", "replace"),
        "stdout_sha256": sha(out), "stderr_sha256": sha(err),
        "dur_s": round(time.monotonic() - t0, 3),
    }


def modules_short():
    r = sh(["pactl", "list", "modules", "short"])
    rows = []
    for line in r["stdout"].splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            parts = line.split(None, 2)
        if len(parts) >= 3 and parts[0].isdigit():
            rows.append({"index": int(parts[0]), "name": parts[1], "args": parts[2]})
    return rows, r


def load_null_sink(name):
    r = sh(["pactl", "load-module", "module-null-sink", "sink_name=" + name,
            "node.description=r91scout_" + name])
    try:
        idx = int(r["stdout"].strip())
    except ValueError:
        return {"ok": False, "load": r, "idx": None}
    rows, _ = modules_short()
    row = [x for x in rows if x["index"] == idx]
    ok = bool(row) and (name in row[0]["args"])
    return {"ok": ok, "idx": idx, "load": r, "row": row[:1]}


def load_remap_source(name, master_sink):
    r = sh(["pactl", "load-module", "module-remap-source",
            "source_name=" + name, "master=" + master_sink + ".monitor"])
    try:
        idx = int(r["stdout"].strip())
    except ValueError:
        return {"ok": False, "load": r, "idx": None}
    rows, _ = modules_short()
    row = [x for x in rows if x["index"] == idx]
    ok = bool(row) and (name in row[0]["args"])
    return {"ok": ok, "idx": idx, "load": r, "row": row[:1]}


def unload_verified(idx, name):
    rows, _ = modules_short()
    row = [x for x in rows if x["index"] == idx]
    if not row:
        return {"ok": False, "why": "index absent", "idx": idx}
    if name not in row[0]["args"]:
        return {"ok": False, "why": "name mismatch", "idx": idx, "row": row[0]}
    r = sh(["pactl", "unload-module", str(idx)])
    rows2, _ = modules_short()
    gone = not any(x["index"] == idx for x in rows2)
    return {"ok": (r["rc"] == 0 and gone), "rc": r["rc"], "gone": gone,
            "stdout": r["stdout"].strip(), "stderr": r["stderr"].strip()}


def pw_dump():
    r = sh(["pw-dump"], timeout=20)
    try:
        return json.loads(r["stdout"]), r
    except Exception:
        return None, r


def nodes_by_prefix(dump, prefix):
    out = []
    for o in dump or []:
        if not str(o.get("type", "")).endswith("Node"):
            continue
        info = o.get("info") or {}
        props = info.get("props") or {}
        nm = props.get("node.name") or ""
        if nm.startswith(prefix):
            out.append({
                "id": o.get("id"),
                "serial": props.get("object.serial"),
                "state": info.get("state"),
                "props": props,
            })
    return out


def node_info(node_id):
    if node_id is None:
        return None
    return sh(["pw-cli", "info", str(node_id)], timeout=8)


def links_raw():
    return sh(["pw-link", "-l"], timeout=8)


def relevant_links(text):
    """Keep complete pw-link blocks (port line + indented link lines) when any
    line in the block mentions a seat name."""
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        if ("r91s" in line) or ("gst_r91" in line):
            j = i
            while j - 1 >= 0 and lines[j - 1].startswith(" "):
                j -= 1
            k = i
            while k + 1 < len(lines) and lines[k + 1].startswith(" "):
                k += 1
            for x in range(j, k + 1):
                if lines[x] not in out:
                    out.append(lines[x])
    return out


def node_state(prefix):
    dump, _ = pw_dump()
    nodes = nodes_by_prefix(dump, prefix)
    if not nodes:
        return None
    p = nodes[0]["props"]
    return {"id": nodes[0]["id"], "state": nodes[0]["state"],
            "node.dont-reconnect": p.get("node.dont-reconnect"),
            "stream.capture.sink": p.get("stream.capture.sink"),
            "target.object": p.get("target.object")}


def links_for_node(dump, node_id):
    out = []
    for o in dump or []:
        if not str(o.get("type", "")).endswith("Link"):
            continue
        info = o.get("info") or {}
        props = info.get("props") or {}
        if (props.get("link.input.node") == str(node_id) or
                props.get("link.output.node") == str(node_id)):
            out.append({
                "id": o.get("id"), "state": info.get("state"),
                "in_node": props.get("link.input.node"),
                "in_port": props.get("link.input.port"),
                "out_node": props.get("link.output.node"),
                "out_port": props.get("link.output.port"),
                "passive": props.get("link.passive"),
            })
    return out


def find_ports(direction, pattern):
    """direction 'o' or 'i'; r90 C16: -i needs an empty out-pattern slot."""
    if direction == "o":
        r = sh(["pw-link", "-o", pattern])
    else:
        r = sh(["pw-link", "-i", "", pattern])
    ports = []
    for line in r["stdout"].splitlines():
        line = line.strip()
        if line:
            ports.append(line)
    return ports, r


# ---------------------------------------------------------------- bounded runner

def run_bounded(leg_dir, argv, wall, byte_cap_path=None, unload_at=None,
                unload_fn=None, sample_fn=None, sample_interval=0.2,
                byte_cap=BYTE_CAP, cwd=None):
    """One loop owns the process group: wall cap + byte cap + timed unload +
    periodic sampling; killpg on any cap."""
    os.makedirs(leg_dir, exist_ok=True)
    log_path = os.path.join(leg_dir, "combined.log")
    log = open(log_path, "wb")
    p = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
                         start_new_session=True, cwd=cwd)
    t0 = time.monotonic()
    timeline = []
    killed = None
    unload_res = None
    unload_t = None
    last_sample = -1e9
    try:
        while True:
            t = time.monotonic() - t0
            if unload_at is not None and t >= unload_at and unload_res is None:
                unload_res = unload_fn() if unload_fn else None
                unload_t = round(t, 3)
            if sample_fn is not None and (t - last_sample) >= sample_interval:
                last_sample = t
                try:
                    timeline.append(sample_fn(round(t, 3)))
                except Exception as e:  # never let sampling kill the loop
                    timeline.append({"t": round(t, 3), "sample_error": repr(e)})
            if t >= wall:
                killed = "wallcap"
                break
            if byte_cap and byte_cap_path and os.path.exists(byte_cap_path):
                if os.path.getsize(byte_cap_path) > byte_cap:
                    killed = "bytecap"
                    break
            rc = p.poll()
            if rc is not None:
                break
            time.sleep(0.03)
    finally:
        rc = p.poll()
        if rc is None:
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                rc = p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                rc = None
        log.close()
    elapsed = round(time.monotonic() - t0, 3)
    with open(log_path, "rb") as f:
        log_bytes = f.read()
    return {
        "argv": argv, "rc": rc, "killed": killed, "elapsed_s": elapsed,
        "unload_at": unload_at, "unload_t": unload_t, "unload_result": unload_res,
        "timeline": timeline,
        "combined_log_sha256": sha(log_bytes), "combined_log_len": len(log_bytes),
        "combined_log_head": log_bytes[:2000].decode("utf-8", "replace"),
        "wall_cap_s": wall, "byte_cap_bytes": byte_cap,
    }


# ---------------------------------------------------------------- stages

def stage_census(tag):
    dump, r = pw_dump()
    rec = {
        "tag": tag,
        "when": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "default_sink": sh(["pactl", "get-default-sink"]),
        "default_source": sh(["pactl", "get-default-source"]),
        "modules_short": sh(["pactl", "list", "modules", "short"]),
        "pw_dump_objects": len(dump) if dump else None,
        "r91_residue": [n["props"].get("node.name") for n in nodes_by_prefix(dump, "r91s")] if dump else None,
        "pw_link_l": sh(["pw-link", "-l"]),
    }
    with open(os.path.join(RECEIPTS, f"census-{tag}.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    return rec


def stage_props(reps):
    out = {"stage": "props", "reps": reps, "legs": {}, "entry": stage_census("props-entry")}
    for fam, spec in FAMILIES.items():
        for rep in range(reps):
            leg = f"{fam}_r{rep}"
            leg_dir = os.path.join(RUNS, "props", leg)
            os.makedirs(leg_dir, exist_ok=True)
            ns = load_null_sink(NS1)
            out_path = None if spec.get("no_file") else os.path.join(TMP, f"props_{leg}.wav")
            argv = [a.replace("{out}", out_path or "") for a in spec["argv"]]
            ctx = {"node": None, "wpctl": None}

            def sample(t, ctx=ctx, prefix=spec["prefix"]):
                if ctx["node"] is None:
                    dump, _ = pw_dump()
                    nodes = nodes_by_prefix(dump, prefix)
                    if nodes:
                        ctx["node"] = nodes[0]
                        ctx["wpctl"] = sh(["wpctl", "inspect", str(nodes[0]["id"])])
                s = {"t": t}
                if ctx["node"]:
                    s["node_id"] = ctx["node"]["id"]
                    s["node_state"] = ctx["node"]["state"]
                s["links_relevant"] = relevant_links(links_raw()["stdout"])
                return s

            res = run_bounded(leg_dir, argv, wall=2.4, byte_cap_path=out_path,
                              sample_fn=sample, sample_interval=0.5)
            node = ctx["node"]
            rec = {
                "family": fam, "rep": rep, "leg": leg, "ns1_load": ns,
                "ns1_unload": unload_verified(ns["idx"], NS1) if ns.get("idx") else None,
                "run": res,
                "node": node,
                "wpctl_inspect": (ctx["wpctl"]["stdout"] if ctx["wpctl"] else None),
                "wpctl_rc": (ctx["wpctl"]["rc"] if ctx["wpctl"] else None),
            }
            with open(os.path.join(leg_dir, "receipt.json"), "w") as f:
                json.dump(rec, f, indent=1, sort_keys=True)
            out["legs"][leg] = {k: rec[k] for k in
                                ("family", "rep", "node", "wpctl_inspect", "ns1_load", "ns1_unload")}
            out["legs"][leg]["run_rc"] = res["rc"]
            out["legs"][leg]["run_killed"] = res["killed"]
            if out_path and os.path.exists(out_path):
                out["legs"][leg]["file_bytes"] = os.path.getsize(out_path)
                os.unlink(out_path)
    out["exit"] = stage_census("props-exit")
    with open(os.path.join(RECEIPTS, "props.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    return out


LOSS_FAMILIES = ["F1s_pwrec_srcloss", "F2_pwrec_capsink",
                 "F3_gst_src_default", "F4_gst_src_override"]


def stage_loss(reps):
    out = {"stage": "loss", "reps": reps, "legs": {}, "entry": stage_census("loss-entry")}
    for fam in LOSS_FAMILIES:
        for rep in range(reps):
            leg = f"{fam}_r{rep}"
            leg_dir = os.path.join(RUNS, "loss", leg)
            os.makedirs(leg_dir, exist_ok=True)
            out_path = os.path.join(TMP, f"loss_{leg}.wav")
            ctx = {"node_id": None, "props": None}
            tone = None
            tone_log = None
            ns = None
            src = None

            if fam == "F1s_pwrec_srcloss":
                # deletable real source: pw-play tone -> NS1, remap-source r91s_src1
                ensure_tone_wav(TONE_WAV)
                ns = load_null_sink(NS1)
                tone_log = open(os.path.join(leg_dir, "tone.log"), "wb")
                tone = subprocess.Popen(TONE_NS1_ARGV, stdout=tone_log,
                                        stderr=subprocess.STDOUT, start_new_session=True)
                time.sleep(1.2)
                tone_state = node_state("r91s_tone_ns1")
                src = load_remap_source("r91s_src1", NS1)
                time.sleep(1.2)
                src_state = node_state("r91s_src1")
                prefix = "r91s_pwrec_srcloss"
                argv = ["pw-record", "-P", "node.name=r91s_pwrec_srcloss",
                        "--target", "r91s_src1", "-n", "1000000", out_path]
                unload_fn = lambda src=src: unload_verified(src["idx"], "r91s_src1")
                teardown_unload = None
            else:
                spec = FAMILIES[fam]
                ns = load_null_sink(NS1)
                tone_state = src_state = None
                prefix = spec["prefix"]
                argv = [a.replace("{out}", out_path) for a in spec["argv"]]
                unload_fn = lambda ns=ns: unload_verified(ns["idx"], NS1)
                teardown_unload = None

            def sample(t, ctx=ctx, prefix=prefix, out_path=out_path):
                s = {"t": t}
                if ctx["node_id"] is None:
                    dump, _ = pw_dump()
                    nodes = nodes_by_prefix(dump, prefix)
                    if nodes:
                        ctx["node_id"] = nodes[0]["id"]
                        ctx["props"] = nodes[0]["props"]
                if ctx["node_id"] is not None:
                    s["node_id"] = ctx["node_id"]
                    info = node_info(ctx["node_id"])
                    s["info_rc"] = info["rc"] if info else None
                    s["info_head"] = (info["stdout"] if info else "")[:800]
                    s["info_sha256"] = info["stdout_sha256"] if info else None
                lk = links_raw()
                s["links_sha256"] = lk["stdout_sha256"]
                s["links_relevant"] = relevant_links(lk["stdout"])
                s["file_bytes"] = os.path.getsize(out_path) if os.path.exists(out_path) else None
                return s

            res = run_bounded(leg_dir, argv, wall=4.8, byte_cap_path=out_path,
                              unload_at=1.2, unload_fn=unload_fn,
                              sample_fn=sample, sample_interval=0.15)
            # frozen = no byte growth after the unload settle window
            frozen = None
            sizes = [(s.get("t"), s.get("file_bytes")) for s in res["timeline"] if s.get("file_bytes") is not None]
            if sizes:
                post = [x for x in sizes if x[0] >= (res["unload_t"] or 0) + 0.3 and x[1] is not None]
                if len(post) >= 2:
                    frozen = (post[-1][1] == post[0][1])
            # did a link exist after the unload settle window, and to what
            post_links = []
            for s in res["timeline"]:
                if s.get("t", 0) >= (res["unload_t"] or 0) + 0.3:
                    post_links.extend(s.get("links_relevant") or [])
            rec = {
                "family": fam, "rep": rep, "leg": leg, "ns1_load": ns, "src_load": src,
                "tone_state": tone_state, "src_state": src_state,
                "node_props_at_connect": ctx["props"],
                "run": res, "frozen_bytes_between": frozen,
                "post_unload_link_lines": post_links[:20],
                "final_bytes": os.path.getsize(out_path) if os.path.exists(out_path) else None,
            }
            with open(os.path.join(leg_dir, "receipt.json"), "w") as f:
                json.dump(rec, f, indent=1, sort_keys=True)
            out["legs"][leg] = {
                "family": fam, "rep": rep,
                "node_props_at_connect": ctx["props"],
                "unload_result": res["unload_result"],
                "frozen_bytes_between": frozen,
                "post_unload_link_lines": post_links[:20],
                "final_bytes": rec["final_bytes"],
                "run_rc": res["rc"], "run_killed": res["killed"],
                "timeline": res["timeline"],
            }
            # teardown
            if tone is not None:
                try:
                    os.killpg(os.getpgid(tone.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
                tone.wait(timeout=5)
                tone_log.close()
            if src is not None:
                unload_verified(src["idx"], "r91s_src1")
            if ns is not None:
                unload_verified(ns["idx"], NS1)
            if os.path.exists(out_path):
                os.unlink(out_path)
    out["exit"] = stage_census("loss-exit")
    with open(os.path.join(RECEIPTS, "loss.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    return out


def stage_recover_inloop(reps):
    """The real discriminator: freeze a gst capture, then pw-link it to a live
    seat-owned monitor while it is frozen, and watch the file."""
    out = {"stage": "recover_inloop", "reps": reps, "legs": {}, "entry": stage_census("recover-inloop-entry")}
    for rep in range(reps):
        leg = f"R2_gst_relink_inloop_r{rep}"
        leg_dir = os.path.join(RUNS, "recover", leg)
        os.makedirs(leg_dir, exist_ok=True)
        ns1 = load_null_sink(NS1)
        ns2 = load_null_sink(NS2)
        ensure_tone_wav(TONE_WAV)
        tone_log = open(os.path.join(leg_dir, "tone.log"), "wb")
        tone = subprocess.Popen(TONE_ARGV, stdout=tone_log, stderr=subprocess.STDOUT,
                                start_new_session=True)
        time.sleep(1.0)
        tone_state = node_state("r91s_tone_ns2")
        tone_links = links_raw()
        out_path = os.path.join(TMP, f"recover2_{leg}.wav")
        argv = [a.replace("{out}", out_path) for a in FAMILIES["F3_gst_src_default"]["argv"]]
        prefix = "gst_r91_src_default"
        ctx = {"node_id": None, "manual": None, "frozen_sample": None, "linkinfo": None}

        def sample(t, ctx=ctx, out_path=out_path, prefix=prefix):
            s = {"t": t}
            if ctx["node_id"] is None:
                dump, _ = pw_dump()
                nodes = nodes_by_prefix(dump, prefix)
                if nodes:
                    ctx["node_id"] = nodes[0]["id"]
            if ctx["node_id"] is not None:
                info = node_info(ctx["node_id"])
                s["info_head"] = (info["stdout"] if info else "")[:600]
            lk = links_raw()
            s["links_relevant"] = relevant_links(lk["stdout"])
            s["file_bytes"] = os.path.getsize(out_path) if os.path.exists(out_path) else None
            # manual relink at t>=2.2 if not done yet
            if ctx["manual"] is None and t >= 2.2:
                ctx["manual"] = manual_link()
                ctx["manual_t"] = t
                s["manual"] = ctx["manual"]
            elif ctx["manual"] is not None and ctx["linkinfo"] is None and t >= (ctx.get("manual_t") or 2.2) + 0.2:
                dump, _ = pw_dump()
                ctx["linkinfo"] = links_for_node(dump, ctx["node_id"])
                s["linkinfo"] = ctx["linkinfo"]
            return s

        def manual_link():
            outs, _ = find_ports("o", NS2)
            ins, _ = find_ports("i", prefix)
            done = []
            for o in outs:
                suffix = o.split(":")[-1]
                if not suffix.startswith("monitor_"):
                    continue
                want = "input_" + suffix.split("_", 1)[1]
                for i in ins:
                    if i.endswith(":" + want):
                        done.append({"out": o, "in": i, "res": sh(["pw-link", o, i])})
                        break
            return {"outs": outs, "ins": ins, "links": done}

        res = run_bounded(leg_dir, argv, wall=5.0, byte_cap_path=out_path,
                          unload_at=1.2,
                          unload_fn=lambda ns1=ns1: unload_verified(ns1["idx"], NS1),
                          sample_fn=sample, sample_interval=0.15)
        try:
            os.killpg(os.getpgid(tone.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        tone.wait(timeout=5)
        tone_log.close()
        # teardown links created by the seat (only our own ports involved)
        if ctx["manual"]:
            for l in ctx["manual"]["links"]:
                sh(["pw-link", "-d", l["out"], l["in"]])
        # classify: bytes before manual relink vs after
        tl = res["timeline"]
        manual_t = next((s["t"] for s in tl if s.get("manual")), None)
        sizes = [(s["t"], s.get("file_bytes")) for s in tl if s.get("file_bytes") is not None]
        before = [x[1] for x in sizes if manual_t is not None and x[0] <= manual_t]
        after = [x[1] for x in sizes if manual_t is not None and x[0] > manual_t]
        frozen_before = bool(before) and (before[-1] == before[0])
        resumed_after = bool(after) and (after[-1] > after[0])
        rec = {
            "rep": rep, "leg": leg, "ns1_load": ns1, "ns2_load": ns2,
            "tone_state": tone_state,
            "tone_links": relevant_links(tone_links["stdout"]),
            "manual_t": manual_t,
            "frozen_before_manual": frozen_before,
            "resumed_after_manual": resumed_after,
            "linkinfo": ctx["linkinfo"],
            "run": res,
        }
        with open(os.path.join(leg_dir, "receipt.json"), "w") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
        out["legs"][leg] = {k: rec[k] for k in
                            ("manual_t", "frozen_before_manual", "resumed_after_manual", "tone_links")}
        out["legs"][leg]["run_rc"] = res["rc"]
        out["legs"][leg]["timeline"] = tl
        unload_verified(ns2["idx"], NS2)
        if os.path.exists(out_path):
            os.unlink(out_path)
    out["exit"] = stage_census("recover-inloop-exit")
    with open(os.path.join(RECEIPTS, "recover-inloop.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["census", "props", "loss", "recover-inloop", "all"])
    ap.add_argument("--reps", type=int, default=3)
    args = ap.parse_args()
    for d in (RUNS, RECEIPTS, TMP):
        os.makedirs(d, exist_ok=True)
    ensure_tone_wav(TONE_WAV)
    if args.stage in ("census", "all"):
        stage_census("entry")
    if args.stage in ("props", "all"):
        stage_props(args.reps)
    if args.stage in ("loss", "all"):
        stage_loss(args.reps)
    if args.stage in ("recover-inloop", "all"):
        stage_recover_inloop(args.reps)
    if args.stage in ("census", "all"):
        stage_census("exit")


if __name__ == "__main__":
    main()
