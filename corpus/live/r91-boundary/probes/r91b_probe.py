#!/usr/bin/env python3
"""r91 BOUNDARY probe driver — falsification of the r91 scout's mechanism read.

Attack surface (all from the scout's own report, reports/round-91/r91-scout.md):

  A. Headline 1 says the DONT_RECONNECT flag is set "unconditionally on the
     capture element" (gstpipewiresrc.c:1207-1211).  That code path is
     `gst_pipewire_src_create_stream()`, reached from BOTH a no-target connect
     and a --target connect; the `PW_DIRECTION_INPUT` is the constant for
     "capture stream", not "target is a source".  So a no-prop pipewiresrc
     against a SINK name should connect (monitor rule) and carry
     node.dont-reconnect=true.  If it does, "unconditionally on the capture
     element" is right but the scout's F1 no-prop law ("never links") is a
     *target-direction* law, not a *capture* law -- and the scout's own
     §0.5 mechanism (`getTargetDirection` returns "output" for a no-prop
     capture) predicts a SINK-name target is filtered out.  Direct test.

  B. §1.1 last row / headline-falsification row: "with keepalive 0 the create
     loop does pw_thread_loop_wait ... no timeout, no error path for 'no
     buffer ever arrives again'".  But gstpipewiresrc.c:1631-1643 has an
     explicit opt-in timeout branch (`keepalive_time > 0` -> timed_wait ->
     `timeout=TRUE` -> :1601-1605 resend a copy of last_buffer), and
     :613-689 has an explicit `on-disconnect` = eos|error path for
     "all buffers removed".  Prediction if the source-read is right: setting
     keepalive-time>0 makes the frozen file GROW again after target loss.
     Prediction if the freeze is instead a client-side stall that the
     element's own timeout cannot break: bytes stay flat.

  C. r91 boundary's assigned probe list: does force-quantum move the freeze
     window?  quantum is client-injectable via PIPEWIRE_QUANTUM=<q>/<rate>
     (stream.c:2149-2157 -> node.force-quantum + node.force-rate; note that
     PIPEWIRE_LATENCY sets only node.latency and does NOT move the quantum --
     the r91 scout's implied recipe would not have armed this leg).

  D. Scout headline 2 claims the freeze is "Gate B (client)" and specific to
     the gst element.  But the scout's own F1s leg (pw-record, remap-source
     target loss) also freezes (headline 8).  Control: pw-record source-loss
     with a manual relink -- if a pw-record freeze also does not resume on a
     fresh link, the "Gate B" framing is not a gst-element property.

  E. Manual-link-after-freeze on the gst element (scout §4) re-run under load.

Every leg is triple-bounded: element bound in argv (num-buffers), wall cap,
byte cap checked in the same loop that owns the process group
(start_new_session + os.killpg).  Seat-owned names only: r91b_* / gst_r91b_*.
Never set-default-sink/source.  Module unloads are index-verified against the
seat name immediately before the call.
"""

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time

ROOT = "/home/vgpnk/Projects/shokunin/audio-shokunin"
SCRATCH = os.path.join(ROOT, "corpus/live/r91-boundary")
RUNS = os.path.join(SCRATCH, "runs")
RECEIPTS = os.path.join(SCRATCH, "receipts")
TMP = os.path.join(SCRATCH, "tmp")

NS1 = "r91b_ns1"          # target sink for most legs
NS2 = "r91b_ns2"          # second sink (manual-relink arm)
SRC1 = "r91b_src1"        # remap-source (pw-record source-loss arm)
BYTE_CAP = 4 * 1024 * 1024
TONE_WAV = os.path.join(TMP, "r91b_tone.wav")

CAP_PROPS = "stream-properties=props,stream.capture.sink=true"


def gst_argv(name, out, extra_src_props=(), extra_props=(), target=NS1):
    """Build the canonical F3-shaped gst capture leg."""
    props = ["stream-properties=props,stream.capture.sink=true"]
    if extra_src_props:
        props = ["stream-properties=props,stream.capture.sink=true,"
                 + ",".join(extra_src_props)]
    argv = ["gst-launch-1.0", "-q", "pipewiresrc",
            "client-name=" + name, "target-object=" + target]
    argv += props
    for k, v in extra_props:
        argv += [k + "=" + v]
    argv += ["num-buffers=1000000", "!",
             "audio/x-raw,format=S16LE,rate=48000,channels=2", "!",
             "wavenc", "!", "filesink", "location=" + out]
    return argv


# ------------------------------------------------------------------ helpers

def sha(b):
    return hashlib.sha256(b).hexdigest()


def sh(argv, timeout=20, env=None):
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
            "node.description=r91b_" + name])
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
    r = sh(["pw-dump"], timeout=25)
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
            out.append({"id": o.get("id"), "serial": props.get("object.serial"),
                        "state": info.get("state"), "props": props})
    return out


def relevant_links(text, needles=("r91b", "gst_r91b")):
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        if any(n in line for n in needles):
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


STATE_RE = re.compile(r"^\s*\*?\s*state:\s*\"?([a-z]+)\"?", re.M)


def node_state_of(prefix):
    """Cheap-ish single pw-cli info read of the seat node -> stream state."""
    dump, _ = pw_dump()
    nodes = nodes_by_prefix(dump, prefix)
    if not nodes:
        return None
    info = sh(["pw-cli", "info", str(nodes[0]["id"])], timeout=8)
    m = STATE_RE.search(info["stdout"])
    return {"id": nodes[0]["id"], "node_state": nodes[0]["state"],
            "stream_state": m.group(1) if m else None,
            "props": {k: nodes[0]["props"].get(k) for k in
                      ("node.dont-reconnect", "stream.capture.sink",
                       "node.force-quantum", "node.force-rate", "target.object",
                       "node.target")},
            "info_head": info["stdout"][:400]}


def find_ports(direction, pattern):
    if direction == "o":
        r = sh(["pw-link", "-o", pattern])
    else:
        r = sh(["pw-link", "-i", "", pattern])
    return [l.strip() for l in r["stdout"].splitlines() if l.strip()], r


def wav_head(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        head = f.read(64)
    if len(head) < 44:
        return {"too_short": len(head), "head_hex": head.hex()}
    return {
        "file_bytes": os.path.getsize(path),
        "riff_size_le": hex(int.from_bytes(head[4:8], "little")),
        "data_size_le": hex(int.from_bytes(head[40:44], "little")),
        "head_hex": head.hex(),
    }


# ------------------------------------------------------------ bounded runner

def run_bounded(leg_dir, argv, wall, byte_cap_path=None, unload_at=None,
                unload_fn=None, sample_fn=None, sample_interval=0.15,
                byte_cap=BYTE_CAP, env=None, cwd=None):
    """One loop owns the process group: wall cap + byte cap + timed unload +
    periodic sampling; killpg on any cap.  env is the CHILD env only."""
    os.makedirs(leg_dir, exist_ok=True)
    log_path = os.path.join(leg_dir, "combined.log")
    log = open(log_path, "wb")
    child_env = None
    if env:
        child_env = dict(os.environ)
        child_env.update(env)
    p = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
                         start_new_session=True, cwd=cwd, env=child_env)
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
                except Exception as e:
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
        "argv": argv, "child_env": env or {}, "rc": rc, "killed": killed,
        "elapsed_s": elapsed, "unload_at": unload_at, "unload_t": unload_t,
        "unload_result": unload_res, "timeline": timeline,
        "combined_log_sha256": sha(log_bytes), "combined_log_len": len(log_bytes),
        "combined_log_head": log_bytes[:3000].decode("utf-8", "replace"),
        "wall_cap_s": wall, "byte_cap_bytes": byte_cap,
    }


def classify(res, out_path, settle=0.35):
    """Post-loss shape: grows / flat / clean-exit, plus the freeze window."""
    tl = res["timeline"]
    ut = res["unload_t"]
    sizes = [(s.get("t"), s.get("file_bytes")) for s in tl
             if s.get("file_bytes") is not None]
    post = [x for x in sizes if ut is not None and x[0] >= ut + settle]
    pre = [x for x in sizes if ut is not None and x[0] < ut]
    cls = {
        "samples": len(sizes),
        "bytes_at_unload": (max([x[1] for x in pre if x[1] is not None], default=None)),
        "bytes_first_post": post[0][1] if post else None,
        "bytes_last_post": post[-1][1] if post else None,
        "post_growth": (post[-1][1] - post[0][1]) if len(post) >= 2 else None,
        "flat_post": (len(post) >= 2 and post[-1][1] == post[0][1]),
        "grows_post": (len(post) >= 2 and post[-1][1] > post[0][1]),
        "exit_rc": res["rc"], "killed": res["killed"],
        "head": wav_head(out_path) if out_path else None,
    }
    cls["frozen_final"] = bool(cls["flat_post"]) and cls["exit_rc"] is None
    return cls


# ------------------------------------------------------------------ stages

def stage_census(tag):
    dump, _ = pw_dump()
    rec = {
        "tag": tag,
        "when": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "default_sink": sh(["pactl", "get-default-sink"]),
        "default_source": sh(["pactl", "get-default-source"]),
        "modules_short": sh(["pactl", "list", "modules", "short"]),
        "pw_dump_objects": len(dump) if dump else None,
        "r91b_residue": [n["props"].get("node.name") for n in nodes_by_prefix(dump, "r91b")] if dump else None,
        "pw_link_l": sh(["pw-link", "-l"]),
        "loadavg": open("/proc/loadavg").read().strip(),
    }
    with open(os.path.join(RECEIPTS, f"census-{tag}.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    return rec


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


# ---- LEG TABLE -----------------------------------------------------------

def legs():
    """name -> spec.  Each spec is a callable ctx -> dict."""
    L = {}

    def gst_leg(name, prefix, extra_props=(), extra_src_props=(),
                target=NS1, env=None, manual_relink=False, target_alive=False):
        def make(ctx):
            out_path = os.path.join(TMP, f"{name}.wav")
            argv = gst_argv(prefix, out_path, extra_src_props=extra_src_props,
                            extra_props=extra_props, target=target)
            ns1 = load_null_sink(NS1)
            ns2 = None
            tone = None
            tone_log = None
            if manual_relink:
                ns2 = load_null_sink(NS2)
                ensure_tone_wav(TONE_WAV)
                tone_log = open(os.path.join(ctx["leg_dir"], "tone.log"), "wb")
                tone = subprocess.Popen(
                    ["pw-play", "-P", "node.name=r91b_tone_ns2",
                     "--target", NS2, TONE_WAV],
                    stdout=tone_log, stderr=subprocess.STDOUT, start_new_session=True)
                time.sleep(1.0)
            st = {"node": None, "manual": None, "manual_t": None}

            def sample(t):
                s = {"t": t}
                if st["node"] is None:
                    dump, _ = pw_dump()
                    nodes = nodes_by_prefix(dump, prefix)
                    if nodes:
                        st["node"] = nodes[0]
                if st["node"] is not None:
                    info = sh(["pw-cli", "info", str(st["node"]["id"])], timeout=8)
                    m = STATE_RE.search(info["stdout"])
                    s["stream_state"] = m.group(1) if m else None
                    s["node_state"] = st["node"]["state"]
                    if "node.dont-reconnect" not in s and t > 1.0:
                        pass
                s["links_relevant"] = relevant_links(sh(["pw-link", "-l"], timeout=8)["stdout"])
                s["file_bytes"] = os.path.getsize(out_path) if os.path.exists(out_path) else None
                if manual_relink and st["manual"] is None and t >= 2.2:
                    outs, _ = find_ports("o", NS2)
                    ins, _ = find_ports("i", prefix)
                    done = []
                    for o in outs:
                        sfx = o.split(":")[-1]
                        if not sfx.startswith("monitor_"):
                            continue
                        want = "input_" + sfx.split("_", 1)[1]
                        for i in ins:
                            if i.endswith(":" + want):
                                done.append({"out": o, "in": i, "res": sh(["pw-link", o, i])})
                                break
                    st["manual"] = {"links": done}
                    st["manual_t"] = t
                    s["manual"] = st["manual"]
                return s

            ctx.update({"ns1": ns1, "ns2": ns2, "tone": tone, "tone_log": tone_log,
                        "out_path": out_path, "prefix": prefix, "st": st,
                        "manual_relink": manual_relink})
            ctx["unload_fn"] = (lambda: unload_verified(ns1["idx"], NS1)) if not target_alive else None
            ctx["unload_at"] = None if target_alive else 1.2
            ctx["sample_fn"] = sample
            ctx["argv"] = argv
            ctx["env"] = env
            ctx["wall"] = 5.0 if not target_alive else 3.0
            return ctx

        L[name] = {"make": make, "prefix": prefix, "kind": "gst"}
        return make

    gst_leg("B0_baseline_freeze", "gst_r91b_b0")
    gst_leg("B1_keepalive20", "gst_r91b_b1", extra_props=[("keepalive-time", "20")])
    gst_leg("B2_resend_last", "gst_r91b_b2", extra_props=[("resend-last", "true")])
    gst_leg("B3_on_disconnect_eos", "gst_r91b_b3", extra_props=[("on-disconnect", "eos")])
    gst_leg("B4_on_disconnect_error", "gst_r91b_b4", extra_props=[("on-disconnect", "error")])
    gst_leg("B5_force_quantum_4096", "gst_r91b_b5", env={"PIPEWIRE_QUANTUM": "4096/48000"})
    gst_leg("B6_force_quantum_1024", "gst_r91b_b6", env={"PIPEWIRE_QUANTUM": "1024/48000"})
    gst_leg("B7_manual_relink", "gst_r91b_b7", manual_relink=True)
    gst_leg("B8_target_alive_control", "gst_r91b_b8", target_alive=True)
    gst_leg("B9_noprop_sink_target", "gst_r91b_b9", extra_src_props=("__NOPROP__",))
    gst_leg("B10_keepalive20_manual_relink", "gst_r91b_b10",
            extra_props=[("keepalive-time", "20")], manual_relink=True)

    return L


def build_leg(name, ctx, spec):
    """Materialise argv for special cases."""
    if name == "B9_noprop_sink_target":
        # no stream-properties at all: does a no-prop gst capture connect to a
        # SINK name?  (scout F1 law says a no-prop capture never links to a sink)
        out = ctx["out_path"]
        ctx["argv"] = ["gst-launch-1.0", "-q", "pipewiresrc",
                       "client-name=gst_r91b_b9", "target-object=" + NS1,
                       "num-buffers=1000000", "!",
                       "audio/x-raw,format=S16LE,rate=48000,channels=2", "!",
                       "wavenc", "!", "filesink", "location=" + out]
    return ctx


# ---- pw-record source-loss arm ------------------------------------------

def leg_pwrec_srcloss(ctx, do_relink=True):
    """F1s replay (+ optional manual relink): pw-record frozen on remap-source
    loss, then (optionally) a hand-made link to a live seat monitor.

    The scout only tested the manual-relink arm on the *gst* element
    (recover-inloop); B11/B12 run it on pw-record too, plus the no-relink
    control that pins the frozen shape.
    """
    leg_dir = ctx["leg_dir"]
    out_path = os.path.join(TMP, ctx["name"] + ".wav")
    ensure_tone_wav(TONE_WAV)
    ns1 = load_null_sink(NS1)
    ns2 = load_null_sink(NS2)
    tone1_log = open(os.path.join(leg_dir, "tone1.log"), "wb")
    tone1 = subprocess.Popen(["pw-play", "-P", "node.name=r91b_tone_ns1",
                              "--target", NS1, TONE_WAV],
                             stdout=tone1_log, stderr=subprocess.STDOUT,
                             start_new_session=True)
    time.sleep(1.2)
    src = load_remap_source(SRC1, NS1)
    time.sleep(1.2)
    tone2_log = open(os.path.join(leg_dir, "tone2.log"), "wb")
    tone2 = subprocess.Popen(["pw-play", "-P", "node.name=r91b_tone_ns2",
                              "--target", NS2, TONE_WAV],
                             stdout=tone2_log, stderr=subprocess.STDOUT,
                             start_new_session=True)
    time.sleep(1.0)
    prefix = ctx["prefix"]
    argv = ["pw-record", "-P", "node.name=" + prefix, "--target", SRC1,
            "-n", "1000000", out_path]
    st = {"node": None, "manual": None}

    def sample(t):
        s = {"t": t}
        if st["node"] is None:
            dump, _ = pw_dump()
            nodes = nodes_by_prefix(dump, prefix)
            if nodes:
                st["node"] = nodes[0]
        if st["node"] is not None:
            info = sh(["pw-cli", "info", str(st["node"]["id"])], timeout=8)
            m = STATE_RE.search(info["stdout"])
            s["stream_state"] = m.group(1) if m else None
            s["node_state"] = st["node"]["state"]
        s["links_relevant"] = relevant_links(sh(["pw-link", "-l"], timeout=8)["stdout"])
        s["file_bytes"] = os.path.getsize(out_path) if os.path.exists(out_path) else None
        if do_relink and st["manual"] is None and t >= 2.2:
            outs, _ = find_ports("o", NS2)
            ins, _ = find_ports("i", prefix)
            done = []
            for o in outs:
                sfx = o.split(":")[-1]
                if not sfx.startswith("monitor_"):
                    continue
                want = "input_" + sfx.split("_", 1)[1]
                for i in ins:
                    if i.endswith(":" + want):
                        done.append({"out": o, "in": i, "res": sh(["pw-link", o, i])})
                        break
            st["manual"] = {"links": done}
            s["manual"] = st["manual"]
        return s

    ctx.update({"ns1": ns1, "ns2": ns2, "src": src, "tone1": tone1, "tone2": tone2,
                "tone1_log": tone1_log, "tone2_log": tone2_log,
                "out_path": out_path, "prefix": prefix, "st": st,
                "unload_fn": lambda: unload_verified(src["idx"], SRC1),
                "unload_at": 1.2, "sample_fn": sample, "argv": argv,
                "env": None, "wall": 5.0})
    return ctx


def teardown(ctx, spec):
    st = ctx.get("st") or {}
    if st.get("manual"):
        for l in st["manual"]["links"]:
            sh(["pw-link", "-d", l["out"], l["in"]])
    for k in ("tone", "tone1", "tone2"):
        p = ctx.get(k)
        if p is not None:
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                p.wait(timeout=5)
            except Exception:
                pass
    for k in ("tone_log", "tone1_log", "tone2_log"):
        h = ctx.get(k)
        if h is not None:
            h.close()
    for k, nm in (("src", SRC1), ("ns2", NS2), ("ns1", NS1)):
        m = ctx.get(k)
        if m and m.get("idx"):
            unload_verified(m["idx"], nm)
    if ctx.get("out_path") and os.path.exists(ctx["out_path"]):
        os.unlink(ctx["out_path"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legs", default="")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    for d in (RUNS, RECEIPTS, TMP):
        os.makedirs(d, exist_ok=True)
    ensure_tone_wav(TONE_WAV)
    table = legs()
    table["B11_pwrec_srcloss"] = {"make": None, "prefix": "r91b_pwrec_srcloss",
                                  "kind": "pwrec",
                                  "fn": lambda ctx: leg_pwrec_srcloss(ctx, True)}
    table["B12_pwrec_srcloss_norelink"] = {"make": None,
                                           "prefix": "r91b_pwrec_norelink",
                                           "kind": "pwrec",
                                           "fn": lambda ctx: leg_pwrec_srcloss(ctx, False)}
    if args.list:
        print("\n".join(sorted(table)))
        return
    want = [x for x in args.legs.split(",") if x] or sorted(table)
    out = {"stage": "boundary", "reps": args.reps, "legs": {},
           "entry": stage_census("entry")}
    for name in want:
        spec = table[name]
        for rep in range(args.reps):
            leg = f"{name}_r{rep}"
            leg_dir = os.path.join(RUNS, leg)
            os.makedirs(leg_dir, exist_ok=True)
            ctx = {"leg_dir": leg_dir, "name": name,
                   "prefix": spec.get("prefix") or name.lower()}
            if spec["kind"] == "pwrec":
                ctx = spec["fn"](ctx)
            else:
                ctx = spec["make"](ctx)
                ctx = build_leg(name, ctx, spec)
            res = run_bounded(leg_dir, ctx["argv"], wall=ctx["wall"],
                              byte_cap_path=ctx["out_path"],
                              unload_at=ctx["unload_at"],
                              unload_fn=ctx["unload_fn"],
                              sample_fn=ctx["sample_fn"],
                              sample_interval=0.15, env=ctx["env"])
            cls = classify(res, ctx["out_path"])
            tl = res["timeline"]
            states = [s.get("stream_state") for s in tl]
            # first sample where the stream state leaves streaming
            drop = next((s for s in tl if s.get("stream_state") not in (None, "streaming")), None)
            manual_t = next((s["t"] for s in tl if s.get("manual")), None)
            post_manual = [s.get("file_bytes") for s in tl
                           if manual_t is not None and s["t"] > manual_t]
            rec = {
                "leg": leg, "name": name, "rep": rep,
                "argv": res["argv"], "child_env": res["child_env"],
                "node_props_at_connect": (ctx["st"].get("node") or {}).get("props"),
                "unload_result": res["unload_result"], "unload_t": res["unload_t"],
                "classify": cls,
                "state_seq": states,
                "first_state_drop": drop,
                "manual_t": manual_t,
                "resumed_after_manual": (bool(post_manual) and post_manual[-1] > post_manual[0]) if post_manual else None,
                "post_unload_links": [l for s in tl
                                      if res["unload_t"] is not None and s["t"] >= res["unload_t"] + 0.35
                                      for l in (s.get("links_relevant") or [])][:20],
                "run": res,
            }
            with open(os.path.join(leg_dir, "receipt.json"), "w") as f:
                json.dump(rec, f, indent=1, sort_keys=True)
            out["legs"][leg] = {
                "name": name, "rep": rep, "classify": cls,
                "state_seq": states, "first_state_drop": drop,
                "manual_t": manual_t, "resumed_after_manual": rec["resumed_after_manual"],
                "node_props_at_connect": rec["node_props_at_connect"],
                "unload_ok": (res["unload_result"] or {}).get("ok"),
                "post_unload_links": rec["post_unload_links"],
                "run_rc": res["rc"], "run_killed": res["killed"],
                "argv": res["argv"], "child_env": res["child_env"],
            }
            teardown(ctx, spec)
            print(json.dumps({k: out["legs"][leg][k] for k in
                              ("name", "rep", "classify", "first_state_drop",
                               "resumed_after_manual", "run_rc", "run_killed")},
                             sort_keys=True))
    out["exit"] = stage_census("exit")
    with open(os.path.join(RECEIPTS, "boundary.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
