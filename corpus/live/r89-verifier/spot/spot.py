#!/usr/bin/env python3
"""r89 verifier independent live spots — verifier-owned code, own namespace.

Shapes (all measured against the live host, not the fixture):
  S1  SIGHUP disposition A/B: default vs inherited-ignore (the g_hup arm's
      launcher sensitivity, controlled).
  S2  the strtol full-string -n parser lattice on values the fixture does
      not carry (" 10" / "10 " / "+10" / "0x10" + controls).
  S3  the -o incremental-write law: SIGKILL at 1.0/2.0/3.0 s -> size/rows/
      4096-multiple (is "49152 B" reproducible or a timing sample?).
  S4  the -J exact-4096-B stream-block law.
  S5  exact-N completion (-n 8) with own sink + follower.
  S6  the Profiler object's pw-cli introspection refusal.
  S7  closed-reader SIGPIPE (rc -13).
  S8  the suspension law: kill the follower mid-window -> own driver stops
      emitting while the run itself survives to TERM.

Writes only under corpus/live/r89-verifier/spot + TMPDIR scratch. Own
PipeWire names r89v_<pid>; unload only the index whose own sink_name= line
matches; never set-default-*.
"""
import json
import os
import re
import signal
import struct
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

PID = os.getpid()
NS = f"r89v_ns_{PID}"
TAG = f"r89v_{PID}_pl"
ROLE = f"r89vrole{PID}"
HERE = Path(__file__).resolve().parent
OUT = HERE / "spot-results.json"
LOG = []


def log(*a):
    line = " ".join(str(x) for x in a)
    LOG.append(line)
    print(line, flush=True)


def run(argv, timeout=15, **kw):
    try:
        return subprocess.run(argv, capture_output=True, timeout=timeout,
                              text=True, **kw)
    except subprocess.TimeoutExpired:
        return None


def load_ns():
    r = run(["pactl", "load-module", "module-null-sink",
             f"sink_name={NS}", "sink_properties=device.description=r89v"])
    idx = (r.stdout or "").strip() if r else ""
    return int(idx) if idx.isdigit() else None


def own_module_idx():
    r = run(["pactl", "list", "modules", "short"])
    for ln in (r.stdout or "").splitlines():
        f = ln.split("\t")
        if f and f[0].strip().isdigit() and f"sink_name={NS}" in ln:
            return int(f[0].strip())
    return None


def unload(idx):
    if idx is None:
        return None
    if own_module_idx() != idx:
        return "refused: index no longer carries our sink_name"
    return run(["pactl", "unload-module", str(idx)]).returncode


def write_tone(path, seconds=45.0):
    n = int(48000 * seconds)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        try:
            import numpy as np
            t = np.arange(n, dtype=np.float64) / 48000.0
            v = (12000 * np.sin(2 * np.pi * 440 * t)).astype("<i2")
            frames = np.repeat(v[:, None], 2, axis=1).tobytes()
        except Exception:
            frames = bytearray()
            for i in range(n):
                x = int(12000 * __import__("math").sin(
                    2 * 3.14159265358979 * 440 * i / 48000))
                frames += struct.pack("<hh", x, x)
            frames = bytes(frames)
        w.writeframes(frames)


def spawn_player(tone, errpath=None):
    err = open(errpath, "wb") if errpath else subprocess.DEVNULL
    return subprocess.Popen(
        ["pw-play", "-P", f"node.name={TAG}", "-P", f"media.role={ROLE}",
         "--target", NS, str(tone)],
        stdout=subprocess.DEVNULL, stderr=err,
        stdin=subprocess.DEVNULL, start_new_session=True)


def node_ids_by_name():
    try:
        objs = json.loads(run(["pw-dump"], timeout=20).stdout or "[]")
    except Exception:
        return {}
    out = {}
    for o in objs:
        if not str(o.get("type", "")).endswith("Node"):
            continue
        nm = ((o.get("info") or {}).get("props") or {}).get("node.name")
        if nm:
            out.setdefault(nm, o.get("id"))
    return out


def linked_to_sink(src_id, dst_id):
    """True iff a PipeWire Link object joins src node -> dst node.
    Links are their own pw-dump objects (`info.output-node-id` /
    `info.input-node-id`); port props do NOT carry the link keys."""
    try:
        objs = json.loads(run(["pw-dump"], timeout=20).stdout or "[]")
    except Exception:
        return False
    for o in objs:
        if not str(o.get("type", "")).endswith("Link"):
            continue
        info = o.get("info") or {}
        if info.get("output-node-id") == src_id and \
                info.get("input-node-id") == dst_id:
            return True
    return False


def wait_link(wait_s=8.0):
    end = time.monotonic() + wait_s
    while time.monotonic() < end:
        ids = node_ids_by_name()
        if TAG in ids and NS in ids and linked_to_sink(ids[TAG], ids[NS]):
            return True
        time.sleep(0.25)
    return False


def killpg(proc, sig=signal.SIGKILL):
    if proc is None or proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), sig)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        proc.wait(timeout=4)
    except subprocess.TimeoutExpired:
        pass


def stream(argv, timeout_s, sig_at=None, sig=signal.SIGTERM,
           sample_ts=(), preexec=None, close_stdout=False, devnull=False,
           hooks=(), cwd=None):
    """Bounded pw-profiler spawn with drained stdout (backpressure law)."""
    rec = {"argv": " ".join(argv)}
    kw = {}
    if devnull:
        kw["stdout"] = subprocess.DEVNULL
    else:
        kw["stdout"] = subprocess.PIPE
    if cwd is not None:
        kw["cwd"] = str(cwd)
    proc = subprocess.Popen(
        argv, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
        start_new_session=True, preexec_fn=preexec, **kw)
    if close_stdout:
        proc.stdout.close()
    elif not devnull:
        os.set_blocking(proc.stdout.fileno(), False)
    t0 = time.monotonic()
    buf = bytearray()
    samples = []
    pending = list(sample_ts)
    pending_hooks = sorted(list(hooks))
    fired = False
    alive_at_sig = None
    killed = False
    while True:
        now = time.monotonic() - t0
        while pending and now >= pending[0]:
            samples.append({"t": pending.pop(0), "bytes": len(buf)})
        while pending_hooks and now >= pending_hooks[0][0]:
            try:
                pending_hooks.pop(0)[1]()
            except Exception:
                pass
        if sig_at is not None and not fired and now >= sig_at:
            alive_at_sig = proc.poll() is None
            if alive_at_sig:
                try:
                    proc.send_signal(sig)
                except ProcessLookupError:
                    alive_at_sig = False
            fired = True
        if proc.poll() is not None:
            if not devnull and not close_stdout:
                while True:
                    try:
                        chunk = os.read(proc.stdout.fileno(), 65536)
                    except (BlockingIOError, OSError):
                        chunk = b""
                    if not chunk:
                        break
                    buf += chunk
            break
        if now >= timeout_s:
            killed = True
            killpg(proc, signal.SIGKILL)
            continue
        if not devnull and not close_stdout:
            try:
                chunk = os.read(proc.stdout.fileno(), 65536)
                if chunk:
                    buf += chunk
            except (BlockingIOError, OSError):
                pass
        time.sleep(0.01)
    try:
        err = proc.stderr.read() or b""
    except OSError:
        err = b""
    outt = bytes(buf).decode(errors="replace")
    arr = None
    perr = None
    try:
        arr = json.loads(outt.strip())
    except ValueError as exc:
        perr = f"{exc} (len={len(outt)})"
    rec.update({"exit_code": proc.returncode,
                "alive_at_sig": alive_at_sig, "killed_at_bound": killed,
                "wall_s": round(time.monotonic() - t0, 3),
                "stdout_bytes": len(buf),
                "n_info": sum(1 for r in arr or []
                              if isinstance(r, dict) and
                              r.get("type") == "info") if arr else None,
                "term_ok": bool(arr) and arr[-1] == {},
                "parse_error": perr,
                "stream_samples": samples,
                "stderr": err.decode(errors="replace")[:200]})
    if not devnull and not close_stdout:
        rec["stdout_raw"] = outt
    return rec


def blocks(arr):
    out, cur = [], None
    for r in arr or []:
        if not isinstance(r, dict) or not r:
            continue
        if r.get("type") == "info":
            cur = {"info": r, "clock": None, "driver": None, "followers": []}
            out.append(cur)
        elif cur is not None:
            if r.get("type") == "clock":
                cur["clock"] = r
            elif r.get("type") == "driver":
                cur["driver"] = r
            elif r.get("type") == "follower":
                cur["followers"].append(r)
    return out


def main():
    res = {"pid": PID, "ns": NS, "legs": {}, "failures": []}
    tone_dir = Path(tempfile.mkdtemp(prefix="r89v-spot-",
                                     dir=os.environ.get("TMPDIR") or "/tmp"))
    tone = tone_dir / f"{NS}_tone.wav"
    write_tone(tone)
    player = None
    idx = load_ns()
    res["module_id"] = idx
    if idx is None:
        res["failures"].append("null sink never loaded")
        OUT.write_text(json.dumps(res, indent=1))
        return 1
    time.sleep(0.7)
    player = spawn_player(tone, errpath=tone_dir / "player.stderr")
    linked = wait_link()
    res["linked"] = linked
    if not linked:
        res["failures"].append("own follower never linked — spots vacuous")
    try:
        # ---- S1 HUP disposition A/B --------------------------------
        for mode, disp in (("dfl", signal.SIG_DFL), ("ign", signal.SIG_IGN)):
            for rep in range(3):
                def _pre(d=disp):
                    signal.signal(signal.SIGHUP, d)
                r = stream(["pw-profiler", "-J", "-n", "0"], 4.0,
                           sig_at=0.8, sig=signal.SIGHUP,
                           preexec=_pre, devnull=True)
                key = f"s1_hup_{mode}_{rep}"
                res["legs"][key] = r
                log(key, "rc=", r["exit_code"], "alive_at_sig=",
                    r["alive_at_sig"], "wall=", r["wall_s"])
        # ---- S2 strtol lattice ------------------------------------
        for key, arg, want in (("s2_space10", " 10", "bounded10"),
                               ("s2_10space", "10 ", "unbounded"),
                               ("s2_plus10", "+10", "bounded10"),
                               ("s2_hex10", "0x10", "unbounded"),
                               ("s2_007", "007", "bounded7"),
                               ("s2_2p5", "2.5", "unbounded")):
            r = stream(["pw-profiler", "-J", "-n", arg], 3.2,
                       sig_at=1.6, sig=signal.SIGTERM)
            r.pop("stdout_raw", None)
            r["arg"] = arg
            r["want"] = want
            res["legs"][key] = r
            log(key, repr(arg), "rc=", r["exit_code"], "n_info=",
                r["n_info"], "alive=", r["alive_at_sig"], "wall=", r["wall_s"])
        # ---- S3 -o incremental SIGKILL ladder ---------------------
        for key, kt in (("s3_kill_1s", 1.0), ("s3_kill_2s", 2.0),
                        ("s3_kill_3s", 3.0)):
            wd = tone_dir / key
            wd.mkdir(exist_ok=True)
            r = stream(["pw-profiler", "-o", "k", "-n", "0"], kt + 6.0,
                       sig_at=kt, sig=signal.SIGKILL, devnull=True,
                       cwd=wd)
            f = wd / "k"
            sz = f.stat().st_size if f.exists() else None
            rows = sum(1 for ln in f.read_text(errors="replace").splitlines()
                       if ln.strip()) if f.exists() else None
            r.update({"bytes": sz, "rows": rows,
                      "mod4096": (sz % 4096) if sz is not None else None})
            res["legs"][key] = r
            log(key, "rc=", r["exit_code"], "bytes=", sz, "rows=", rows,
                "mod4096=", r["mod4096"])
        # graceful control
        wd = tone_dir / "s3_term"
        wd.mkdir(exist_ok=True)
        r = stream(["pw-profiler", "-o", "g", "-n", "0"], 8.0, sig_at=1.5,
                   sig=signal.SIGTERM, devnull=True, cwd=wd)
        f = wd / "g"
        r.update({"bytes": f.stat().st_size if f.exists() else None})
        res["legs"]["s3_term"] = r
        log("s3_term rc=", r["exit_code"], "bytes=", r.get("bytes"))
        # ---- S4 stream blocks -------------------------------------
        r = stream(["pw-profiler", "-J", "-n", "0"], 6.0, sig_at=1.2,
                   sig=signal.SIGTERM, sample_ts=(0.3, 0.6, 0.9))
        r.pop("stdout_raw", None)
        res["legs"]["s4_blocks"] = r
        log("s4_blocks", r["stream_samples"], "rc=", r["exit_code"],
            "term_ok=", r["term_ok"])
        # ---- S5 exact-N -------------------------------------------
        r = stream(["pw-profiler", "-J", "-n", "8"], 6.0)
        r.pop("stdout_raw", None)
        res["legs"]["s5_exactN"] = r
        log("s5_exactN rc=", r["exit_code"], "n_info=", r["n_info"],
            "term_ok=", r["term_ok"], "wall=", r["wall_s"])
        # ---- S6 Profiler introspection refusal --------------------
        ids = {}
        try:
            objs = json.loads(run(["pw-dump"], timeout=20).stdout or "[]")
            ids = {str(o.get("id")): str(o.get("type")) for o in objs
                   if str(o.get("type", "")).endswith("Profiler")}
        except Exception:
            pass
        res["profiler_ids"] = sorted(ids)
        if ids:
            pid0 = sorted(ids)[0]
            for key, argv in (("s6_info", ["pw-cli", "info", pid0]),
                              ("s6_enum", ["pw-cli", "enum-params", pid0,
                                           "Props"])):
                r = run(argv, timeout=10)
                res["legs"][key] = {
                    "rc": r.returncode if r else None,
                    "stdout": (r.stdout or "")[:200] if r else None,
                    "stderr": (r.stderr or "")[:200] if r else None}
                log(key, "rc=", res["legs"][key]["rc"],
                    "hit=", "unsupported type" in
                    (r.stderr or "") + (r.stdout or "") if r else None)
        # ---- S7 SIGPIPE -------------------------------------------
        r = stream(["pw-profiler", "-J", "-n", "0"], 4.0, close_stdout=True)
        res["legs"]["s7_sigpipe"] = r
        log("s7_sigpipe rc=", r["exit_code"])
        # ---- S8 suspension ----------------------------------------
        if player.poll() is not None:
            player = spawn_player(tone, errpath=tone_dir / "player2.stderr")
            res["linked"] = res["linked"] and wait_link()
        kill_t = {}

        def _kill_player():
            kill_t["ns"] = time.monotonic_ns()
            killpg(player, signal.SIGKILL)

        r = stream(["pw-profiler", "-J", "-n", "0"], 6.0, sig_at=2.4,
                   sig=signal.SIGTERM, hooks=((0.9, _kill_player),))
        arr = None
        try:
            arr = json.loads((r.get("stdout_raw") or "").strip())
        except ValueError:
            arr = None
        r.pop("stdout_raw", None)
        own = [b for b in blocks(arr)
               if (b.get("driver") or {}).get("name") == NS]
        km = kill_t.get("ns", 0)
        r["kill_mono"] = km
        r["own_blocks"] = len(own)
        r["own_pre_kill"] = sum(
            1 for b in own
            if (b.get("clock") or {}).get("nsec", 0) <= km)
        r["own_after_kill"] = sum(
            1 for b in own
            if (b.get("clock") or {}).get("nsec", 0) > km + 600 * 10**6)
        r["foreign_after_kill"] = sum(
            1 for b in blocks(arr)
            if (b.get("driver") or {}).get("name") not in (None, NS)
            and (b.get("clock") or {}).get("nsec", 0) > km + 600 * 10**6)
        res["legs"]["s8_suspend"] = r
        log("s8_suspend rc=", r["exit_code"], "own=", r["own_blocks"],
            "pre=", r["own_pre_kill"], "after=", r["own_after_kill"],
            "foreign_after=", r["foreign_after_kill"])
    finally:
        killpg(player, signal.SIGTERM)
        res["unload_rc"] = unload(idx)
        time.sleep(0.4)
        names = node_ids_by_name()
        res["own_nodes_after"] = sorted(
            n for n in names if f"r89v_{PID}" in n)
        OUT.write_text(json.dumps(res, indent=1, default=str))
        (HERE / "spot-log.txt").write_text("\n".join(LOG) + "\n")
    nfail = len(res["failures"])
    log("FAILURES:", json.dumps(res["failures"]))
    log("unload_rc:", res.get("unload_rc"),
        "own_nodes_after:", res.get("own_nodes_after"))
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
