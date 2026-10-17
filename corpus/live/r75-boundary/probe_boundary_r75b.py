#!/usr/bin/env python3
"""r75 BOUNDARY supplement (r75b) — new edge members + daemon-severing isolation.

Companion to probe_boundary_r75.py (which owns the canonical member x transport
matrix, gates, fork, name axis, kill classes, load, pacing). This script adds
only what the base probe does not cover:

  A. edge2 members (chunk-structure / declared-length / container family):
       listchunk_dec_act.wav   — LIST chunk between fmt and data (chunk walking)
       riff_giant_decl.wav     — data chunk declares 0xFFFFFFF0, payload short
                                 (declared-length trust -> hang probe)
       fmtext_dec_act.wav      — WAVE_FORMAT_EXTENSIBLE (fmt size 40, cbSize 22)
       rifx_dec_act.wav        — RIFX big-endian container
       datafirst_dec_act.wav   — data chunk before fmt chunk
     x 3 consumers x {file, fifo} = 30 cells.

  B. daemon-severing isolation (independent verification of the scout claim
     "PIPEWIRE_RUNTIME_DIR=<empty> does NOT sever paplay; XDG_RUNTIME_DIR /
     PULSE_SERVER do"):
       paplay and pw-cat on the same 6 env cells -> 12 cells.

  C. device negative controls: `aplay -D pipewire`, `aplay -D hw:0,3`
     (card 0 device 3 is Subdevices 0/1 at gate time).

All fifo/file arms are wrapped in `timeout -s KILL` (fifo-open blocks are
TERM-immune; see the base probe's kill group). No tracked-file writes.
"""
import hashlib
import json
import os
import re
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent
ROOT = SCRATCH.parents[2]
LIVE = ROOT / "corpus" / "live"
EDGE2 = SCRATCH / "edge2"
LOGS = SCRATCH / "logs" / "r75b"
RUNS = SCRATCH / "runs"
CANON_DEC_ACT = LIVE / "round-66" / "pair_dec_act.wav"
CANON_DEC_HCOM = LIVE / "round-66" / "pair_dec_hcom.wav"
ARM_TIMEOUT_S = 20
STAMP = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
RUN_DIR = RUNS / f"{STAMP}-boundary-r75b"
VERD, MEAS, LOG_FILES = {}, {}, {}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_tail(text, extra=()):
    t = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
    lines = [ln.strip() for ln in t.replace("\r", "\n").splitlines() if ln.strip()]
    if not lines:
        return None
    tail = lines[-1]
    tail = re.sub(r"'(?:[^']*)'", "'<input>'", tail)
    tail = re.sub(r'"(?:[^"]*)"', '"<input>"', tail)
    tail = re.sub(r"/tmp/[^\s:]+", "<input>", tail)
    tail = re.sub(r"/home/[^\s:]+", "<input>", tail)
    for p in extra:
        tail = tail.replace(str(p), "<input>")
    return tail[:220]


def run_bounded(argv, timeout_s, env=None, stdin=None, log_path=None):
    t0 = time.time()
    full_env = dict(os.environ)
    if env:
        for k, v in env.items():
            if v is None:
                full_env.pop(k, None)
            else:
                full_env[k] = v
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            stdin=stdin, env=full_env, start_new_session=True)
    killed = False
    try:
        out, err = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        killed = True
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
    res = {"rc": proc.returncode, "wall_s": round(time.time() - t0, 3),
           "harness_kill": killed, "stdout": out.decode(errors="replace"),
           "stderr": err.decode(errors="replace")}
    if log_path:
        LOG_FILES[str(log_path)] = res["stderr"] + ("\n--- stdout ---\n" + res["stdout"] if res["stdout"] else "")
    return res


def consumer_argv(consumer, path):
    if consumer == "paplay":
        return ["paplay", str(path)]
    if consumer == "aplay":
        return ["aplay", "-D", "null", str(path)]
    if consumer == "pwcat":
        return ["pw-cat", "-p", str(path)]
    if consumer == "ffplay":
        return ["ffplay", "-nodisp", "-autoexit", "-vn", "-hide_banner", str(path)]
    raise ValueError(consumer)


def consumer_env(consumer):
    return {"SDL_AUDIODRIVER": "dummy"} if consumer == "ffplay" else None


def parse_verdict(consumer, res):
    text = res["stderr"] + "\n" + res["stdout"]
    v = {"rc": res["rc"]}
    if res["harness_kill"]:
        v["harness_kill"] = True
    if consumer == "paplay":
        m = re.search(r"(pa_context_connect\(\) failed: [^\n]*)", text)
        v["open_fail"] = "Failed to open audio file." in text
        v["connect_error"] = m.group(1) if m else None
        v["error"] = norm_tail(text)
    elif consumer == "aplay":
        mw = re.search(r"Playing WAVE '[^']*' : ([^\n]*)", text)
        mr = re.search(r"Playing raw data '[^']*' : ([^\n]*)", text)
        v["mode"] = "wav" if mw else ("raw" if mr else "error")
        v["detail"] = (mw or mr).group(1).strip() if (mw or mr) else None
        v["error"] = norm_tail(text) if not (mw or mr) else None
    elif consumer == "pwcat":
        m = re.search(r'sndfile: failed to open audio file "[^"]*":\s*(.*)', text)
        mc = re.search(r"(pw_context_connect[^\n]*)", text)
        v["sndfile_error"] = m.group(1).strip() if m else None
        v["connect_error"] = mc.group(1) if mc else None
        v["error"] = norm_tail(text)
    elif consumer == "ffplay":
        mf = re.search(r"Input #0, ([^,]+), from", text)
        ma = re.search(r"Stream #\d+:\d+[^:]*: Audio: ([^\n]*)", text)
        v["detected_format"] = mf.group(1).strip() if mf else None
        v["audio_stream"] = ma.group(1).strip() if ma else None
        v["error"] = norm_tail(text) if not mf else None
    return v


def spawn_writer(mode, member, fifo):
    if mode == "none":
        return None
    if mode == "full":
        argv = ["bash", "-c", 'cat "$1" > "$2"', "_", str(member), str(fifo)]
    else:
        raise ValueError(mode)
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                            start_new_session=True)


def reap_writer(proc, grace=1.5):
    if proc is None:
        return {"writer": "none"}
    t0 = time.time()
    try:
        proc.wait(timeout=grace)
        alive = False
    except subprocess.TimeoutExpired:
        alive = True
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
    return {"writer_rc": proc.returncode, "writer_alive_at_teardown": alive,
            "writer_wait_s": round(time.time() - t0, 3)}


def record(group, cell, member, transport, consumer, res, verdict, log_name=None):
    VERD[cell] = {"group": group, "cell": cell, "member": member, "transport": transport,
                  "consumer": consumer, **verdict}
    MEAS[cell] = {"group": group, "cell": cell, "wall_s": res["wall_s"],
                  "harness_kill": res["harness_kill"], "rc": res["rc"],
                  "writer": res.get("writer"), "stderr_tail": norm_tail(res["stderr"]),
                  "stdout_tail": norm_tail(res["stdout"])}
    if log_name:
        LOG_FILES[str(log_name)] = res["stderr"] + ("\n--- stdout ---\n" + res["stdout"] if res["stdout"] else "")


# ------------------------------------------------------------------ build edge2

def riff(chunks, magic=b"RIFF", endian="<", declared_override=None):
    body = b"".join(chunks)
    total = 4 + len(body) if declared_override is None else declared_override
    return magic + struct.pack(endian + "I", total) + b"WAVE" + body


def fmt_pcm(endian="<"):
    return b"fmt " + struct.pack(endian + "I", 16) + struct.pack(
        endian + "HHIIHH", 1, 1, 8000, 16000, 2, 16)


def fmt_extensible(endian="<"):
    guid = struct.pack(endian + "IHH", 1, 0, 0x0010) + b"\x80\x00\x00\xaa\x00\x38\x9b\x71"
    payload = struct.pack(endian + "HHIIHH", 0xFFFE, 1, 8000, 16000, 2, 16) + \
        struct.pack(endian + "H", 22) + struct.pack(endian + "H", 16) + \
        struct.pack(endian + "I", 4) + guid
    return b"fmt " + struct.pack(endian + "I", len(payload)) + payload


def data_chunk(payload, endian="<", declared=None):
    n = len(payload) if declared is None else declared
    return b"data" + struct.pack(endian + "I", n) + payload


def build_edge2():
    EDGE2.mkdir(parents=True, exist_ok=True)
    act = CANON_DEC_ACT.read_bytes()
    hcom = CANON_DEC_HCOM.read_bytes()
    payload = act[44:]  # the canonical member's PCM body, verbatim
    (EDGE2 / "listchunk_dec_act.wav").write_bytes(riff([
        fmt_pcm(),
        b"LIST" + struct.pack("<I", 24) + b"INFOISFT" + struct.pack("<I", 8) + b"r75b\x00\x00\x00\x00",
        data_chunk(payload)]))
    (EDGE2 / "riff_giant_decl.wav").write_bytes(riff([
        fmt_pcm(), data_chunk(payload, declared=0xFFFFFFF0)]))
    (EDGE2 / "fmtext_dec_act.wav").write_bytes(riff([fmt_extensible(), data_chunk(payload)]))
    (EDGE2 / "rifx_dec_act.wav").write_bytes(riff([fmt_pcm(">"), data_chunk(payload, ">")],
                                                  magic=b"RIFX", endian=">"))
    (EDGE2 / "datafirst_dec_act.wav").write_bytes(riff([data_chunk(payload), fmt_pcm()]))
    (EDGE2 / "hcom_fmtext.wav").write_bytes(riff([fmt_extensible(), data_chunk(hcom[44:])]))
    manifest = {}
    for p in sorted(EDGE2.iterdir()):
        if p.is_file():
            manifest[p.name] = {"bytes": p.stat().st_size, "sha256": sha256(p)}
    (EDGE2 / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    return manifest


def group_edge2():
    members = {p.name: p for p in sorted(EDGE2.iterdir()) if p.suffix == ".wav"}
    for consumer in ("paplay", "aplay", "ffplay"):
        for member, path in sorted(members.items()):
            for transport in ("file", "fifo"):
                cell = f"e2-{consumer}-{member}-{transport}"
                log = LOGS / "edge2" / f"{cell}.stderr.log"
                if transport == "file":
                    res = run_bounded(["timeout", "-s", "KILL", str(ARM_TIMEOUT_S)] + consumer_argv(consumer, path),
                                      ARM_TIMEOUT_S + 5, env=consumer_env(consumer))
                else:
                    tmp = Path(tempfile.mkdtemp(prefix="r75b2-"))
                    fifo = tmp / path.name
                    os.mkfifo(fifo)
                    writer = spawn_writer("full", path, fifo)
                    try:
                        res = run_bounded(["timeout", "-s", "KILL", str(ARM_TIMEOUT_S)] + consumer_argv(consumer, fifo),
                                          ARM_TIMEOUT_S + 5, env=consumer_env(consumer))
                    finally:
                        res["writer"] = reap_writer(writer)
                        shutil.rmtree(tmp, ignore_errors=True)
                v = parse_verdict(consumer, res)
                record("edge2", cell, member, transport, consumer, res, v, log)


# ------------------------------------------------------- B: severing isolation

# value None = variable explicitly UNSET for the child; "" = empty string.
ISO_CELLS = [
    ("iso-baseline", {}),
    ("iso-pwrt-dead", {"PIPEWIRE_RUNTIME_DIR": "<DEAD>"}),
    ("iso-xdg-dead", {"XDG_RUNTIME_DIR": "<DEAD>", "PIPEWIRE_RUNTIME_DIR": "<DEAD>"}),
    ("iso-pulse-dead", {"PULSE_SERVER": "unix:<DEAD>/native"}),
    ("iso-xdg-dead-pulse-live", {"XDG_RUNTIME_DIR": "<DEAD>",
                                 "PULSE_SERVER": "unix:<LIVE>/pulse/native"}),
    ("iso-pulse-empty", {"XDG_RUNTIME_DIR": "<DEAD>", "PULSE_SERVER": ""}),
]


def group_iso():
    live_rt = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    dead = Path(tempfile.mkdtemp(prefix="r75b2-dead-"))
    try:
        for label, template in ISO_CELLS:
            env = {}
            for k, val in template.items():
                env[k] = None if val is None else str(val).replace("<DEAD>", str(dead)).replace("<LIVE>", live_rt)
            for consumer, path in (("paplay", CANON_DEC_ACT), ("pwcat", CANON_DEC_ACT)):
                cell = f"{label}-{consumer}"
                log = LOGS / "iso" / f"{cell}.stderr.log"
                res = run_bounded(["timeout", "-s", "KILL", "8"] + consumer_argv(consumer, path), 10, env=env)
                v = parse_verdict(consumer, res)
                v["env_override"] = {k: ("<unset>" if v2 is None else v2) for k, v2 in env.items()}
                v["live_rt"] = live_rt
                record("iso", cell, path.name, "file", consumer, res, v, log)
    finally:
        shutil.rmtree(dead, ignore_errors=True)


# ----------------------------------------------------- C: device negative controls

def group_devices():
    cells = [
        ("dev-aplay-pipewire", ["aplay", "-D", "pipewire", str(CANON_DEC_ACT)], None),
        ("dev-aplay-hw0,3", ["aplay", "-D", "hw:0,3", str(CANON_DEC_ACT)], None),
        ("dev-aplay-default", ["aplay", str(CANON_DEC_ACT)], None),
        ("dev-aplay-null", ["aplay", "-D", "null", str(CANON_DEC_ACT)], None),
    ]
    for cell, argv, env in cells:
        res = run_bounded(["timeout", "-s", "KILL", "10"] + argv, 12, env=env)
        v = parse_verdict("aplay", res)
        record("devices", cell, CANON_DEC_ACT.name, "file", "aplay", res, v, LOGS / "devices" / f"{cell}.stderr.log")


# ------------------------------------------------------------------ receipts

def env_snapshot():
    lines = []
    for argv in (["uname", "-a"], ["paplay", "--version"], ["aplay", "--version"],
                 ["ffplay", "-version"], ["pw-cat", "--version"], ["pactl", "info"]):
        try:
            p = subprocess.run(argv, capture_output=True, timeout=8)
            lines.append("$ " + " ".join(argv))
            txt = (p.stdout + p.stderr).decode(errors="replace").strip()
            lines.extend(txt.splitlines()[:3] if txt else ["(no output)"])
        except Exception as exc:  # noqa: BLE001
            lines.append("$ " + " ".join(argv) + f" -> {exc}")
    lines.append(f"$ env XDG_RUNTIME_DIR={os.environ.get('XDG_RUNTIME_DIR')} "
                 f"PIPEWIRE_RUNTIME_DIR={os.environ.get('PIPEWIRE_RUNTIME_DIR')!r} "
                 f"PULSE_SERVER={os.environ.get('PULSE_SERVER')!r}")
    return "\n".join(lines) + "\n"


def write_receipts(groups):
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    for rel, text in LOG_FILES.items():
        p = Path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    (RUN_DIR / "measurements.json").write_text(json.dumps(MEAS, sort_keys=True, indent=1) + "\n")
    (RUN_DIR / "verdicts.json").write_text(json.dumps(VERD, sort_keys=True, indent=1) + "\n")
    (RUN_DIR / "env.txt").write_text(env_snapshot())
    (RUN_DIR / "groups.txt").write_text(" ".join(groups) + "\n")
    rows = ["group\tcell\tmember\ttransport\tconsumer\trc\twall_s\tdetail"]
    for cell, v in sorted(VERD.items()):
        m = MEAS.get(cell, {})
        detail = v.get("detail") or v.get("error") or v.get("connect_error") or v.get("detected_format") or ""
        rows.append("\t".join(str(x) for x in [v["group"], cell, v.get("member"), v.get("transport"),
                                               v.get("consumer"), v.get("rc", ""), m.get("wall_s", ""),
                                               str(detail).replace("\t", " ")[:120]]))
    (RUN_DIR / "summary.tsv").write_text("\n".join(rows) + "\n")
    print("receipt:", RUN_DIR)
    print(json.dumps({p.name: sha256(p) for p in sorted(RUN_DIR.iterdir()) if p.is_file()},
                     indent=1, sort_keys=True))


def main():
    groups = sys.argv[1:] or ["build", "edge2", "iso", "devices"]
    for g in groups:
        t0 = time.time()
        print(f"=== {g} ===", flush=True)
        if g == "build":
            print(json.dumps(build_edge2(), indent=1, sort_keys=True))
        elif g == "edge2":
            group_edge2()
        elif g == "iso":
            group_iso()
        elif g == "devices":
            group_devices()
        else:
            raise SystemExit(f"unknown group {g}")
        print(f"--- {g} done in {time.time() - t0:.1f}s", flush=True)
    write_receipts(groups)
    p = subprocess.run(["pgrep", "-a", "paplay|aplay|ffplay|mpv|pw-cat"], capture_output=True)
    print("orphans:", p.stdout.decode(errors="replace").strip() or "(none)")


if __name__ == "__main__":
    main()
