#!/usr/bin/env python3
"""r75 BOUNDARY probe — paplay / aplay / ffplay edge lattice + gates + kill classes.

Leaf seat harness (no tracked-file writes; all output under corpus/live/r75-boundary/).
Consumers:
  paplay  — PulseAudio client over pipewire-pulse (live daemon), libsndfile decode
  aplay   — ALSA direct, `-D null` for the deterministic lattice + real-device cells
  ffplay  — SDL + lavf, SDL_AUDIODRIVER=dummy for determinism

Groups: build | matrix (replayed x2) | fork | name | kill (replayed x2) | load | gates | pacing
rc vocabulary (recorded verbatim, interpreted in the report):
  124  = inner `timeout -s TERM` expiry (TERM-terminable hang)
  137  = inner `timeout -s KILL` expiry (hang marker)
  -9   = harness killpg (only when an inner TERM wrapper was still waiting -> TERM-immune)
  else = consumer's own rc (paplay 0/1; aplay 0/1; ffplay 0/1)
Never key a verdict on bare rc: parsed fields travel with every cell.
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
ARTIFACTS = ROOT / "corpus" / "artifacts"
EDGE = SCRATCH / "edge"
LOGS = SCRATCH / "logs"
RUNS = SCRATCH / "runs"

CANON = {
    "dec_act": LIVE / "round-66" / "pair_dec_act.wav",
    "dec_hcom": LIVE / "round-66" / "pair_dec_hcom.wav",
    "lengate_gsrt_24": LIVE / "round-66" / "pair_lengate_gsrt_24.wav",
    "lengate_gsrt_25": LIVE / "round-66" / "pair_lengate_gsrt_25.wav",
    "lengate_hcom_131": LIVE / "round-66" / "pair_lengate_hcom_131.wav",
    "lengate_hcom_132": LIVE / "round-66" / "pair_lengate_hcom_132.wav",
    "posttable_nomatch": LIVE / "round-68" / "posttable_nomatch.wav",
    "txw_piperefuse": LIVE / "round-68" / "txw_piperefuse.wav",
    "extsuffix_wav": LIVE / "round-69" / "extsuffix_nomatch.wav",
    "extsuffix_bin": LIVE / "round-69" / "extsuffix_nomatch.bin",
    "extsuffix_txw": LIVE / "round-69" / "extsuffix_nomatch.txw",
    "extsuffix_f32": LIVE / "round-69" / "extsuffix_nomatch.f32",
    "extsuffix_snd": LIVE / "round-69" / "extsuffix_nomatch.snd",
}
EDGE_MEMBERS = ["empty.bin", "trunc20_dec_act.wav", "trunc300_dec_act.wav",
                "trunc300_dec_hcom.wav", "magicbad_dec_act.wav",
                "hdronly_dec_act.wav", "zerodata.wav", "nomagic512.snd"]
PACER = ARTIFACTS / "stem_sections.wav"
MATRIX_MEMBERS = ["dec_act", "dec_hcom", "lengate_gsrt_24", "lengate_gsrt_25",
                  "lengate_hcom_131", "lengate_hcom_132", "posttable_nomatch",
                  "txw_piperefuse", "extsuffix_wav", "extsuffix_bin",
                  "extsuffix_txw", "extsuffix_f32", "extsuffix_snd"] + EDGE_MEMBERS
CONSUMERS = ["paplay", "aplay", "ffplay"]
ARM_TIMEOUT_S = 20
HARNESS_GRACE_S = 10

STAMP = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
RUN_DIR = RUNS / f"{STAMP}-boundary-r75"

MEAS = {}   # cell -> measurements (walls, raw tails)
VERD = {}   # cell -> verdict core (replay-compared)
LOG_FILES = {}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_tail(text, extra_paths=()):
    """Deterministic last-line tail: strip CR/ANSI, paths -> <input>."""
    t = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
    lines = [ln.strip() for ln in t.replace("\r", "\n").splitlines() if ln.strip()]
    if not lines:
        return None
    tail = lines[-1]
    tail = re.sub(r"'(?:[^']*)'", "'<input>'", tail)
    tail = re.sub(r'"(?:[^"]*)"', '"<input>"', tail)
    tail = re.sub(r"/tmp/[^\s:]+", "<input>", tail)
    tail = re.sub(r"/home/[^\s:]+", "<input>", tail)
    for p in extra_paths:
        tail = tail.replace(str(p), "<input>")
    return tail[:220]


def run_bounded(argv, timeout_s, env=None, stdin=None, log_path=None):
    """Run argv in its own session; harness kills the group at timeout_s."""
    t0 = time.time()
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
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
    wall = round(time.time() - t0, 3)
    res = {"rc": proc.returncode, "wall_s": wall, "harness_kill": killed,
           "stdout": out.decode(errors="replace"), "stderr": err.decode(errors="replace")}
    if log_path:
        LOG_FILES[str(log_path)] = res["stderr"] + ("\n--- stdout ---\n" + res["stdout"] if res["stdout"] else "")
    return res


def spawn_writer(mode, member, fifo, hold_s=8, nbytes=300):
    """Fifo writer subprocesses (own session; reaped by the cell)."""
    if mode == "none":
        return None
    if mode == "full":
        argv = ["bash", "-c", 'cat "$1" > "$2"', "_", str(member), str(fifo)]
    elif mode == "hold":
        argv = ["bash", "-c", 'exec 3>"$2"; cat "$1" >&3; sleep "$3"',
                "_", str(member), str(fifo), str(hold_s)]
    elif mode == "empty":
        argv = ["bash", "-c", ': > "$1"', "_", str(fifo)]
    elif mode == "partial_kill":
        argv = ["bash", "-c", f'head -c {nbytes} "$1" > "$2"; kill -9 $$',
                "_", str(member), str(fifo)]
    else:
        raise ValueError(mode)
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, start_new_session=True)


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


def consumer_argv(consumer, path, debug=False):
    if consumer == "paplay":
        return ["paplay", str(path)]
    if consumer == "aplay":
        return ["aplay", "-D", "null", str(path)]
    if consumer == "pwcat":
        return ["pw-cat", "-p", str(path)]
    if consumer == "ffplay":
        argv = ["ffplay", "-nodisp", "-autoexit", "-vn", "-hide_banner"]
        if debug:
            argv += ["-loglevel", "debug"]
        return argv + [str(path)]
    raise ValueError(consumer)


def consumer_env(consumer):
    if consumer == "ffplay":
        return {"SDL_AUDIODRIVER": "dummy"}
    return None


def parse_verdict(consumer, res, debug=False):
    text = res["stderr"] + "\n" + res["stdout"]
    v = {"rc": res["rc"]}
    if res["harness_kill"]:
        v["harness_kill"] = True
    if consumer == "paplay":
        v["open_fail"] = "Failed to open audio file." in text
        m = re.search(r"(pa_context_connect\(\) failed: [^\n]*)", text)
        v["connect_error"] = m.group(1) if m else None
        v["error"] = norm_tail(text)
    elif consumer == "aplay":
        mw = re.search(r"Playing WAVE '[^']*' : ([^\n]*)", text)
        mr = re.search(r"Playing raw data '[^']*' : ([^\n]*)", text)
        v["mode"] = "wav" if mw else ("raw" if mr else "error")
        v["detail"] = (mw or mr).group(1).strip() if (mw or mr) else None
        v["error"] = norm_tail(text) if not (mw or mr) else None
    elif consumer == "ffplay":
        mf = re.search(r"Input #0, ([^,]+), from", text)
        ma = re.search(r"Stream #\d+:\d+[^:]*: Audio: ([^\n]*)", text)
        v["detected_format"] = mf.group(1).strip() if mf else None
        v["audio_stream"] = ma.group(1).strip() if ma else None
        v["error"] = norm_tail(text) if not mf else None
        if debug:
            ms = re.search(r"Statistics: \d+ bytes read, (\d+) seeks", text)
            v["seeks"] = int(ms.group(1)) if ms else None
    return v


def cell_fifo(consumer, member_path, writer_mode, wrapper, outer_s, debug=False, group="matrix"):
    """One fifo cell: fresh fifo named with the member basename + writer."""
    tmp = Path(tempfile.mkdtemp(prefix="r75b-"))
    fifo = tmp / member_path.name
    os.mkfifo(fifo)
    writer = spawn_writer(writer_mode, member_path, fifo)
    try:
        argv = wrapper + consumer_argv(consumer, fifo, debug=debug)
        res = run_bounded(argv, outer_s, env=consumer_env(consumer))
    finally:
        w = reap_writer(writer)
        shutil.rmtree(tmp, ignore_errors=True)
    res["writer"] = w
    return res


def cell_file(consumer, member_path, wrapper, outer_s, debug=False):
    argv = wrapper + consumer_argv(consumer, member_path, debug=debug)
    return run_bounded(argv, outer_s, env=consumer_env(consumer))


def record(group, cell, member, transport, consumer, res, verdict, log_name=None):
    key = cell
    VERD[key] = {"group": group, "cell": cell, "member": member,
                 "transport": transport, "consumer": consumer, **verdict}
    MEAS[key] = {"group": group, "cell": cell, "wall_s": res["wall_s"],
                 "harness_kill": res["harness_kill"], "rc": res["rc"],
                 "writer": res.get("writer"),
                 "stderr_tail": norm_tail(res["stderr"]),
                 "stdout_tail": norm_tail(res["stdout"])}
    if log_name:
        LOG_FILES[log_name] = res["stderr"] + ("\n--- stdout ---\n" + res["stdout"] if res["stdout"] else "")


# ---------------------------------------------------------------- build

def build_edge():
    EDGE.mkdir(parents=True, exist_ok=True)
    act = CANON["dec_act"].read_bytes()
    hcom = CANON["dec_hcom"].read_bytes()
    (EDGE / "empty.bin").write_bytes(b"")
    (EDGE / "trunc20_dec_act.wav").write_bytes(act[:20])
    (EDGE / "trunc300_dec_act.wav").write_bytes(act[:300])
    (EDGE / "trunc300_dec_hcom.wav").write_bytes(hcom[:300])
    (EDGE / "magicbad_dec_act.wav").write_bytes(b"XXXX" + act[4:])
    (EDGE / "hdronly_dec_act.wav").write_bytes(act[:44])
    zerodata = (b"RIFF" + struct.pack("<I", 36) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, 1, 8000, 16000, 2, 16)
                + b"data" + struct.pack("<I", 0))
    (EDGE / "zerodata.wav").write_bytes(zerodata)
    (EDGE / "nomagic512.snd").write_bytes(CANON["extsuffix_snd"].read_bytes())
    # content-precedence controls
    (EDGE / "wavcontent.snd").write_bytes(act)
    (EDGE / "wavcontent.foo").write_bytes(act)
    # name-axis sweep files (identical no-magic bytes under four names)
    for nm in ("nomatch.snd", "nomatch.SND", "nomatch.wav", "nomatch.foo"):
        (EDGE / nm).write_bytes(CANON["extsuffix_snd"].read_bytes())
    manifest = {}
    for p in sorted(EDGE.iterdir()):
        if p.is_file():
            manifest[p.name] = {"bytes": p.stat().st_size, "sha256": sha256(p)}
    (EDGE / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    return manifest


def member_map():
    m = {}
    for name, p in CANON.items():
        m[name] = p
    for name in EDGE_MEMBERS:
        m[name] = EDGE / name
    return m


def members_sha(members):
    return {name: sha256(p) for name, p in sorted(members.items())}


# ---------------------------------------------------------------- matrix

def group_matrix():
    members = member_map()
    for rep in (1, 2):
        for consumer in CONSUMERS:
            for member, path in sorted(members.items()):
                for transport in ("file", "fifo"):
                    cell = f"m{rep}-{consumer}-{member}-{transport}"
                    log = LOGS / f"matrix/{cell}.stderr.log"
                    if transport == "file":
                        res = cell_file(consumer, path, ["timeout", "-s", "KILL", str(ARM_TIMEOUT_S)], ARM_TIMEOUT_S + 5)
                    else:
                        res = cell_fifo(consumer, path, "full", ["timeout", "-s", "KILL", str(ARM_TIMEOUT_S)], ARM_TIMEOUT_S + 5)
                    v = parse_verdict(consumer, res)
                    record("matrix", cell, member, transport, consumer, res, v, log)
        # replay verdicts are stored separately for the byte-compare (cell name
        # without the rep prefix is the replay key)
        prefix = f"m{rep}-"
        snap = {}
        for k, v in VERD.items():
            if v["group"] == "matrix" and k.startswith(prefix):
                vv = dict(v)
                vv["cell"] = k[len(prefix):]
                snap[k[len(prefix):]] = vv
        sha = hashlib.sha256(json.dumps(snap, sort_keys=True, indent=1).encode()).hexdigest()
        (RUN_DIR / f"matrix-rep{rep}-verdicts.json").write_text(
            json.dumps(snap, sort_keys=True, indent=1) + "\n")
        print(f"matrix rep{rep}: {len(snap)} cells, verdict-sha {sha[:12]}")


# ---------------------------------------------------------------- fork

def group_fork():
    """ffplay vs mpv on dec_hcom (the r73/r74 inverted-seek fork member)."""
    hcom = CANON["dec_hcom"]
    act = CANON["dec_act"]
    # ffplay debug file/fifo
    for member, path in (("dec_hcom", hcom), ("dec_act", act)):
        for transport in ("file", "fifo"):
            cell = f"fork-ffplay-{member}-{transport}"
            log = LOGS / f"fork/{cell}.stderr.log"
            if transport == "file":
                res = cell_file("ffplay", path, ["timeout", "-s", "KILL", str(ARM_TIMEOUT_S)], ARM_TIMEOUT_S + 5, debug=True)
            else:
                res = cell_fifo("ffplay", path, "full", ["timeout", "-s", "KILL", str(ARM_TIMEOUT_S)], ARM_TIMEOUT_S + 5, debug=True)
            v = parse_verdict("ffplay", res, debug=True)
            record("fork", cell, member, transport, "ffplay", res, v, log)
    # mpv contrast (same window)
    for member, path in (("dec_hcom", hcom), ("dec_act", act)):
        for transport in ("file", "fifo"):
            cell = f"fork-mpv-{member}-{transport}"
            log = LOGS / f"fork/{cell}.mpv.log"
            tmp = Path(tempfile.mkdtemp(prefix="r75b-mpv-"))
            mpvlog = tmp / "mpv.log"
            argv = ["mpv", "--no-config", "--vo=null", "--ao=null", "--audio-display=no",
                    "--really-quiet", f"--log-file={mpvlog}"]
            if transport == "file":
                res = run_bounded(["timeout", "-s", "KILL", str(ARM_TIMEOUT_S)] + argv + [str(path)],
                                  ARM_TIMEOUT_S + 5)
                w = {"writer": "none"}
                text = mpvlog.read_text(errors="replace") if mpvlog.exists() else ""
                shutil.rmtree(tmp, ignore_errors=True)
            else:
                fifo = tmp / path.name
                os.mkfifo(fifo)
                writer = spawn_writer("full", path, fifo)
                try:
                    res = run_bounded(["timeout", "-s", "KILL", str(ARM_TIMEOUT_S)] + argv + [str(fifo)],
                                      ARM_TIMEOUT_S + 5)
                finally:
                    w = reap_writer(writer)
                text = mpvlog.read_text(errors="replace") if mpvlog.exists() else ""
                shutil.rmtree(tmp, ignore_errors=True)
            res["writer"] = w
            LOG_FILES[str(log)] = text
            mv = re.search(r"finished playback, ([^\n]*)", text)
            v = {"rc": res["rc"],
                 "detected": bool(re.search(r"Found 'hcom'|Found 'wav'", text)),
                 "refresh_seek": bool(re.search(r"refresh seek", text)),
                 "seek_failed_eperm": bool(re.search(r"Seek failed \(Operation not permitted\)", text)),
                 "not_seekable": bool(re.search(r"Stream is not seekable", text)),
                 "verdict": mv.group(1).strip() if mv else norm_tail(text)}
            record("fork", cell, member, transport, "mpv", res, v, str(log))


# ---------------------------------------------------------------- name axis

def group_name():
    """Identical no-magic 512 B bytes: paplay name axis vs pw-cat contrast."""
    nomagic = CANON["extsuffix_snd"]
    wavc = EDGE / "wavcontent.snd"
    cells = []
    # paplay named files
    for nm in ("nomatch.snd", "nomatch.SND", "nomatch.wav", "nomatch.foo"):
        cells.append(("paplay-file-" + nm, "paplay", EDGE / nm, "file"))
    # paplay named fifos
    for nm in ("nomatch.snd", "nomatch.SND", "nomatch.wav", "nomatch.foo"):
        cells.append(("paplay-fifo-" + nm, "paplay", EDGE / nm, "fifo"))
    # paplay rfd (dev/stdin)
    for label, src in (("paplay-rfd-nomagic", nomagic), ("paplay-rfd-wavcontent", wavc)):
        cell = label
        with open(src, "rb") as fh:
            res = run_bounded(["timeout", "-s", "KILL", str(ARM_TIMEOUT_S), "paplay", "/dev/stdin"],
                              ARM_TIMEOUT_S + 5, stdin=fh)
        v = parse_verdict("paplay", res)
        record("name", cell, src.name, "rfd", "paplay", res, v, LOGS / f"name/{cell}.stderr.log")
    # paplay fifo with wav content under .foo name (content precedence)
    cell = "paplay-fifo-foo-wavcontent"
    res = cell_fifo("paplay", wavc, "full", ["timeout", "-s", "KILL", str(ARM_TIMEOUT_S)], ARM_TIMEOUT_S + 5)
    record("name", cell, wavc.name, "fifo", "paplay", res, parse_verdict("paplay", res),
           LOGS / f"name/{cell}.stderr.log")
    # pw-cat contrast (same bytes, same window)
    for transport in ("file", "fifo"):
        cell = f"pwcat-{transport}-nomagic-snd"
        if transport == "file":
            res = run_bounded(["timeout", "-s", "KILL", str(ARM_TIMEOUT_S), "pw-cat", "-p", str(nomagic)],
                              ARM_TIMEOUT_S + 5)
        else:
            res = cell_fifo("pwcat", nomagic, "full", ["timeout", "-s", "KILL", str(ARM_TIMEOUT_S)], ARM_TIMEOUT_S + 5)
        # pw-cat leg (simplified parse: sndfile error or clean rc)
        text = res["stderr"]
        m = re.search(r'sndfile: failed to open audio file "[^"]*":\s*(.*)', text)
        v = {"rc": res["rc"], "sndfile_error": m.group(1).strip() if m else None,
             "error": norm_tail(text)}
        record("name", cell, nomagic.name, transport, "pw-cat", res, v, LOGS / f"name/{cell}.stderr.log")
    # the named-file/fifo paplay cells
    for cell, consumer, src, transport in cells:
        if transport == "file":
            res = run_bounded(["timeout", "-s", "KILL", str(ARM_TIMEOUT_S), "paplay", str(src)], ARM_TIMEOUT_S + 5)
        else:
            res = cell_fifo("paplay", src, "full", ["timeout", "-s", "KILL", str(ARM_TIMEOUT_S)], ARM_TIMEOUT_S + 5)
        record("name", cell, src.name, transport, "paplay", res, parse_verdict("paplay", res),
               LOGS / f"name/{cell}.stderr.log")


# ---------------------------------------------------------------- kill

def kill_cell(consumer, wrapper, outer_s, member="dec_act", writer_mode="none"):
    path = CANON[member]
    return cell_fifo(consumer, path, writer_mode, wrapper, outer_s)


def group_kill(rep=1):
    cells = []
    for consumer in CONSUMERS:
        cells.append((f"k{rep}-writerless-{consumer}-TERM4", consumer,
                      ["timeout", "-s", "TERM", "4"], HARNESS_GRACE_S, "none"))
        cells.append((f"k{rep}-writerless-{consumer}-KILL6", consumer,
                      ["timeout", "-s", "KILL", "6"], HARNESS_GRACE_S, "none"))
        cells.append((f"k{rep}-writerless-{consumer}-TERM4-k2", consumer,
                      ["timeout", "-k", "2", "-s", "TERM", "4"], HARNESS_GRACE_S, "none"))
        cells.append((f"k{rep}-emptywriter-{consumer}", consumer,
                      ["timeout", "-s", "KILL", "8"], 10, "empty"))
        cells.append((f"k{rep}-lingerwriter-{consumer}", consumer,
                      ["timeout", "-s", "KILL", "6"], 10, "hold"))
        cells.append((f"k{rep}-partialkill-{consumer}", consumer,
                      ["timeout", "-s", "KILL", "8"], 10, "partial_kill"))
    for cell, consumer, wrapper, outer, wmode in cells:
        res = kill_cell(consumer, wrapper, outer, writer_mode=wmode)
        v = parse_verdict(consumer, res)
        v["writer_mode"] = wmode
        if res.get("writer", {}).get("writer_alive_at_teardown"):
            v["writer_alive_at_teardown"] = True
        record("kill", cell, "dec_act", "fifo", consumer, res, v, LOGS / f"kill/{cell}.stderr.log")
    prefix = f"k{rep}-"
    snap = {}
    for k, v in VERD.items():
        if v["group"] == "kill" and k.startswith(prefix):
            vv = dict(v)
            vv["cell"] = k[len(prefix):]
            snap[k[len(prefix):]] = vv
    sha = hashlib.sha256(json.dumps(snap, sort_keys=True, indent=1).encode()).hexdigest()
    (RUN_DIR / f"kill-rep{rep}-verdicts.json").write_text(json.dumps(snap, sort_keys=True, indent=1) + "\n")
    print(f"kill rep{rep}: {len(snap)} cells, verdict-sha {sha[:12]}")


def group_kill_replay():
    group_kill(rep=2)


# ---------------------------------------------------------------- load

def load_cell(cell, consumers_wrappers, outer_s):
    """Spawn N concurrent writerless-fifo readers; collect rcs/walls."""
    tmp = Path(tempfile.mkdtemp(prefix="r75b-load-"))
    procs = []
    for i, (consumer, wrapper) in enumerate(consumers_wrappers):
        fifo = tmp / f"load{i}.wav"
        os.mkfifo(fifo)
        argv = wrapper + consumer_argv(consumer, fifo)
        env = dict(os.environ)
        if consumer == "ffplay":
            env["SDL_AUDIODRIVER"] = "dummy"
        t0 = time.time()
        p = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             env=env, start_new_session=True)
        procs.append((consumer, p, t0))
    results = []
    for consumer, p, t0 in procs:
        try:
            p.wait(timeout=outer_s)
            rc = p.returncode
            killed = False
        except subprocess.TimeoutExpired:
            killed = True
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            p.wait()
            rc = p.returncode
        results.append({"consumer": consumer, "rc": rc, "harness_kill": killed,
                        "wall_s": round(time.time() - t0, 3)})
    shutil.rmtree(tmp, ignore_errors=True)
    rcs = [r["rc"] for r in results]
    VERD[cell] = {"group": "load", "cell": cell, "member": "dec_act", "transport": "fifo",
                  "consumer": f"x{len(results)}", "rcs": rcs, "harness_kills": sum(r["harness_kill"] for r in results)}
    MEAS[cell] = {"group": "load", "cell": cell, "n": len(results), "results": results}
    print(f"{cell}: rcs={rcs}")


def group_load():
    load_cell("load8-paplay-TERM4", [("paplay", ["timeout", "-s", "TERM", "4"])] * 8, HARNESS_GRACE_S)
    load_cell("load8-ffplay-TERM4", [("ffplay", ["timeout", "-s", "TERM", "4"])] * 8, HARNESS_GRACE_S)
    load_cell("load8-aplay-TERM4-k2", [("aplay", ["timeout", "-k", "2", "-s", "TERM", "4"])] * 8, HARNESS_GRACE_S)
    load_cell("load8-mixed-paplay4-ffplay4-TERM4",
              [("paplay", ["timeout", "-s", "TERM", "4"])] * 4 + [("ffplay", ["timeout", "-s", "TERM", "4"])] * 4,
              HARNESS_GRACE_S)


# ---------------------------------------------------------------- gates

def group_gates():
    # G1 live daemon snapshot
    res = run_bounded(["pactl", "info"], 8)
    MEAS["gate-pactl-info"] = {"group": "gates", "cell": "gate-pactl-info", "rc": res["rc"],
                               "stdout_tail": norm_tail(res["stdout"]), "wall_s": res["wall_s"]}
    LOG_FILES[str(LOGS / "gates/pactl-info.txt")] = res["stdout"] + res["stderr"]
    res = run_bounded(["pactl", "list", "short", "sinks"], 8)
    MEAS["gate-pactl-sinks"] = {"group": "gates", "cell": "gate-pactl-sinks", "rc": res["rc"],
                                "sink_lines": len([ln for ln in res["stdout"].splitlines() if ln.strip()]),
                                "stdout_tail": norm_tail(res["stdout"])}
    LOG_FILES[str(LOGS / "gates/pactl-sinks.txt")] = res["stdout"] + res["stderr"]
    # G2 paplay dead runtime dir (missing daemon)
    dead = Path(tempfile.mkdtemp(prefix="r75b-dead-"))
    env = {"PULSE_SERVER": f"unix:{dead}/native", "PIPEWIRE_RUNTIME_DIR": str(dead),
           "XDG_RUNTIME_DIR": str(dead)}
    res = run_bounded(["timeout", "-s", "KILL", "8", "paplay", str(CANON["dec_act"])], 10, env=env)
    v = parse_verdict("paplay", res)
    v["gate"] = "dead_pulse_runtime"
    record("gates", "gate-paplay-deadrt", "dec_act", "file", "paplay", res, v, LOGS / "gates/paplay-deadrt.stderr.log")
    # G2b writer-orphan hazard: writer first, then dead-rt paplay
    fifo = dead / "orphan.wav"
    os.mkfifo(fifo)
    writer = spawn_writer("full", CANON["dec_act"], fifo)
    time.sleep(0.2)
    res2 = run_bounded(["timeout", "-s", "KILL", "8", "paplay", str(fifo)], 10, env=env)
    v2 = parse_verdict("paplay", res2)
    v2["gate"] = "dead_pulse_runtime_orphan_writer"
    v2["writer_still_blocked"] = writer.poll() is None
    record("gates", "gate-paplay-deadrt-orphanwriter", "dec_act", "fifo", "paplay", res2, v2,
           LOGS / "gates/paplay-deadrt-orphanwriter.stderr.log")
    w = reap_writer(writer, grace=0.5)
    MEAS["gate-paplay-deadrt-orphanwriter"]["writer"] = w
    shutil.rmtree(dead, ignore_errors=True)
    # G3 aplay device enumeration
    res = run_bounded(["aplay", "-l"], 8)
    MEAS["gate-aplay-l"] = {"group": "gates", "cell": "gate-aplay-l", "rc": res["rc"],
                            "device_lines": len([ln for ln in (res["stdout"] + res["stderr"]).splitlines()
                                                 if ln.startswith("card ")])}
    LOG_FILES[str(LOGS / "gates/aplay-l.txt")] = res["stdout"] + res["stderr"]
    res = run_bounded(["aplay", "-L"], 8)
    MEAS["gate-aplay-L"] = {"group": "gates", "cell": "gate-aplay-L", "rc": res["rc"],
                            "has_null": "null" in (res["stdout"] + res["stderr"]).split("\n"),
                            "has_default": "default" in (res["stdout"] + res["stderr"]).split("\n")}
    LOG_FILES[str(LOGS / "gates/aplay-L.txt")] = res["stdout"] + res["stderr"]
    # G4 aplay missing device
    res = run_bounded(["timeout", "-s", "KILL", "8", "aplay", "-D", "nosuchdevice", str(CANON["dec_act"])], 10)
    v = parse_verdict("aplay", res)
    v["gate"] = "missing_device"
    record("gates", "gate-aplay-nosuchdevice", "dec_act", "file", "aplay", res, v,
           LOGS / "gates/aplay-nosuchdevice.stderr.log")
    # G5 aplay real default device (coupling; 0.19 s member)
    res = run_bounded(["timeout", "-s", "KILL", "8", "aplay", str(CANON["dec_act"])], 10)
    v = parse_verdict("aplay", res)
    v["gate"] = "real_default_device"
    record("gates", "gate-aplay-default-device", "dec_act", "file", "aplay", res, v,
           LOGS / "gates/aplay-default-device.stderr.log")
    # G6 aplay raw hw device
    res = run_bounded(["timeout", "-s", "KILL", "8", "aplay", "-D", "hw:0,0", str(CANON["dec_act"])], 10)
    v = parse_verdict("aplay", res)
    v["gate"] = "raw_hw_device"
    record("gates", "gate-aplay-hw00", "dec_act", "file", "aplay", res, v, LOGS / "gates/aplay-hw00.stderr.log")
    # G7 ffplay bogus SDL driver
    res = run_bounded(["timeout", "-s", "KILL", "8", "ffplay", "-nodisp", "-autoexit", "-vn", "-hide_banner",
                       str(CANON["dec_act"])], 10, env={"SDL_AUDIODRIVER": "nosuchdriver"})
    v = parse_verdict("ffplay", res)
    v["gate"] = "bogus_sdl_driver"
    record("gates", "gate-ffplay-bogus-sdl", "dec_act", "file", "ffplay", res, v,
           LOGS / "gates/ffplay-bogus-sdl.stderr.log")
    # G8 ffplay default SDL driver (no override) — device-coupled control
    res = run_bounded(["timeout", "-s", "KILL", "8", "ffplay", "-nodisp", "-autoexit", "-vn", "-hide_banner",
                       str(CANON["dec_act"])], 10, env={"SDL_AUDIODRIVER": ""})
    v = parse_verdict("ffplay", res)
    v["gate"] = "default_sdl_driver"
    record("gates", "gate-ffplay-default-sdl", "dec_act", "file", "ffplay", res, v,
           LOGS / "gates/ffplay-default-sdl.stderr.log")


# ---------------------------------------------------------------- pacing

def group_pacing():
    cells = [
        ("pace-paplay-live", "paplay", ["paplay", str(PACER)], None, 12),
        ("pace-ffplay-dummy", "ffplay", ["ffplay", "-nodisp", "-autoexit", "-vn", "-hide_banner", str(PACER)],
         {"SDL_AUDIODRIVER": "dummy"}, 12),
        ("pace-aplay-null", "aplay", ["aplay", "-D", "null", str(PACER)], None, 12),
        ("pace-aplay-default-dec_act", "aplay", ["aplay", str(CANON["dec_act"])], None, 12),
    ]
    for cell, consumer, argv, env, bound in cells:
        res = run_bounded(["timeout", "-s", "KILL", str(bound)] + argv, bound + 5, env=env)
        v = parse_verdict(consumer, res)
        v["content_duration_s"] = 4.0 if "pacer" in cell or "PACER" in cell else 0.03
        record("pacing", cell, "stem_sections.wav" if "dec_act" not in cell else "dec_act", "file", consumer,
               res, v, LOGS / f"pacing/{cell}.stderr.log")


# ---------------------------------------------------------------- env + receipts

def env_snapshot():
    lines = []
    for argv in (["uname", "-a"], ["paplay", "--version"], ["aplay", "--version"],
                 ["ffplay", "-version"], ["pw-cat", "--version"], ["mpv", "--version"],
                 ["ffmpeg", "-version"]):
        try:
            p = subprocess.run(argv, capture_output=True, timeout=8)
            lines.append("$ " + " ".join(argv))
            lines.append((p.stdout + p.stderr).decode(errors="replace").strip().splitlines()[0]
                         if (p.stdout + p.stderr).strip() else "(no output)")
        except Exception as exc:  # noqa: BLE001
            lines.append("$ " + " ".join(argv) + f" -> {exc}")
    pids = subprocess.run(["pgrep", "-a", "pipewire|wireplumber"], capture_output=True)
    lines.append("$ pgrep -a 'pipewire|wireplumber'")
    lines.append(pids.stdout.decode(errors="replace").strip())
    return "\n".join(lines) + "\n"


def write_receipts(groups):
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "measurements.json").write_text(json.dumps(MEAS, sort_keys=True, indent=1) + "\n")
    (RUN_DIR / "verdicts.json").write_text(json.dumps(VERD, sort_keys=True, indent=1) + "\n")
    for rel, text in LOG_FILES.items():
        p = Path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    (RUN_DIR / "env.txt").write_text(env_snapshot())
    (RUN_DIR / "groups.txt").write_text(" ".join(groups) + "\n")
    # summary tsv
    rows = ["group\tcell\tmember\ttransport\tconsumer\trc\twall_s\tdetail"]
    for cell, v in sorted(VERD.items()):
        m = MEAS.get(cell, {})
        detail = v.get("detail") or v.get("error") or v.get("verdict") or v.get("detected_format") or ""
        rows.append("\t".join(str(x) for x in [v["group"], cell, v.get("member"), v.get("transport"),
                                               v.get("consumer"), v.get("rc", ""), m.get("wall_s", ""),
                                               str(detail).replace("\t", " ")[:120]]))
    (RUN_DIR / "summary.tsv").write_text("\n".join(rows) + "\n")
    shas = {p.name: sha256(p) for p in sorted(RUN_DIR.iterdir()) if p.is_file()}
    print("receipt:", RUN_DIR)
    print(json.dumps(shas, indent=1, sort_keys=True))


def orphan_check():
    p = subprocess.run(["pgrep", "-a", "paplay|aplay|ffplay|mpv|pw-cat"], capture_output=True)
    out = p.stdout.decode(errors="replace").strip()
    print("orphans:", out if out else "(none)")


def main():
    groups = sys.argv[1:] or ["build", "matrix", "fork", "name", "kill", "kill_replay", "load", "gates", "pacing"]
    LOGS.mkdir(parents=True, exist_ok=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    for g in groups:
        t0 = time.time()
        print(f"=== {g} ===")
        if g == "build":
            manifest = build_edge()
            print(json.dumps(manifest, indent=1, sort_keys=True))
        elif g == "matrix":
            group_matrix()
        elif g == "fork":
            group_fork()
        elif g == "name":
            group_name()
        elif g == "kill":
            group_kill(rep=1)
        elif g == "kill_replay":
            group_kill(rep=2)
        elif g == "load":
            group_load()
        elif g == "gates":
            group_gates()
        elif g == "pacing":
            group_pacing()
        else:
            raise SystemExit(f"unknown group {g}")
        print(f"--- {g} done in {time.time() - t0:.1f}s")
    if not RUN_DIR.exists():
        RUN_DIR.mkdir(parents=True, exist_ok=True)
    write_receipts(groups)
    orphan_check()


if __name__ == "__main__":
    main()
