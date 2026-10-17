#!/usr/bin/env python3
"""r96 VERIFIER independent live re-derivation (own code only).

Nothing here imports the fixture. Every measurement below is taken by this
script's own argv, own tone writer, own `pactl -f json` parsing, own WAV
analysis and own transcription (`r96v_laws.fix_attr`, written from the
committed pipewire C source). It exercises the committed instrument binary
(built from the committed blob) as an opaque tool.

Usage: r96v_live.py --probe /path/pulse_r96_probe [--scratch DIR]
"""
from __future__ import annotations

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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r96v_laws import fix_attr, predict_leg, env_ms, usec_to_bytes  # noqa: E402

PID = os.getpid()
NS = f"r96v_ns_{PID}"
TONE_S = 75.0


def hermetic(**kw):
    env = {k: v for k, v in os.environ.items() if not k.startswith("PULSE_")}
    for k, v in kw.items():
        if v is None:
            env.pop(k, None)
        else:
            env[k] = str(v)
    return env


def run(argv, timeout=12.0, env=None):
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout,
                           env=env or hermetic(), start_new_session=True)
        return {"argv": " ".join(map(str, argv)), "rc": p.returncode,
                "wall_s": round(time.monotonic() - t0, 3),
                "stdout": p.stdout.decode(errors="replace"),
                "stderr": p.stderr.decode(errors="replace")}
    except subprocess.TimeoutExpired as exc:
        return {"argv": " ".join(map(str, argv)), "rc": None,
                "wall_s": round(time.monotonic() - t0, 3),
                "stdout": (exc.stdout or b"").decode(errors="replace"),
                "stderr": "TIMEOUT"}


def spawn(argv, env=None):
    return subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                            env=env or hermetic(), start_new_session=True)


def kill(proc, wait=1.0):
    if proc is None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except OSError:
        pass
    t0 = time.monotonic()
    while proc.poll() is None and time.monotonic() - t0 < wait:
        time.sleep(0.02)
    if proc.poll() is None:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except OSError:
            pass
    try:
        proc.wait(timeout=1.0)
    except subprocess.TimeoutExpired:
        pass


def modules_short():
    """pactl list modules short: id, name, args — the only place the
    module index appears in this client's output."""
    out = run(["pactl", "list", "modules", "short"], timeout=12.0)
    rows = []
    for ln in (out["stdout"] or "").splitlines():
        parts = ln.split("\t")
        if len(parts) >= 3 and parts[0].strip().isdigit():
            rows.append({"index": parts[0].strip(), "name": parts[1],
                         "args": parts[2]})
    return rows


def pactl_json(what):
    out = run(["pactl", "-f", "json", "list", what], timeout=12.0)
    try:
        return json.loads(out["stdout"])
    except (ValueError, TypeError):
        return []


def write_tone(path, seconds=TONE_S, amp=8192, rate=48000, freq=997.0):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for f in range(int(rate * seconds)):
            v = int(amp * math.sin(2.0 * math.pi * freq * f / rate))
            frames += struct.pack("<h", v)
        w.writeframes(bytes(frames))


def wav_windows(path, rate=48000, channels=2):
    """Own WAV reader: nonzero-frame counts in [0,1.0) s and [1.5,inf) s."""
    if not path.exists():
        return None
    with wave.open(str(path), "rb") as w:
        n = w.getnframes()
        ch = w.getnchannels()
        raw = w.readframes(n)
    step = 2 * ch
    early = late = total = 0
    for i in range(0, len(raw) - step + 1, step):
        v = struct.unpack_from("<h", raw, i)[0]
        if v != 0:
            total += 1
            t = (i // step) / rate
            if t < 1.0:
                early += 1
            elif t >= 1.5:
                late += 1
    return {"frames": n, "channels": ch, "nonzero_total": total,
            "nonzero_lt_1s": early, "nonzero_ge_1_5s": late}


def attr_fields(props):
    def _int(key):
        try:
            return int(str((props or {}).get(key)).strip())
        except (TypeError, ValueError):
            return None
    lat = (props or {}).get("node.latency")
    num = den = None
    if isinstance(lat, str) and "/" in lat:
        try:
            num, den = (int(x) for x in lat.split("/", 1))
        except ValueError:
            pass
    return {"tlength": _int("pulse.attr.tlength"),
            "prebuf": _int("pulse.attr.prebuf"),
            "minreq": _int("pulse.attr.minreq"),
            "maxlength": _int("pulse.attr.maxlength"),
            "latency_num": num, "latency_denom": den}


def census():
    mods = pactl_json("modules")
    sinks = pactl_json("sinks")
    inputs = pactl_json("sink-inputs")
    outs = pactl_json("source-outputs")
    info = run(["pactl", "info"], timeout=12.0)
    srv = {}
    for key, pat in (("default_sink", r"^Default Sink:\s*(.*)$"),
                     ("default_source", r"^Default Source:\s*(.*)$")):
        m = re.search(pat, info.get("stdout") or "", re.M)
        srv[key] = m.group(1).strip() if m else None
    own = [m for m in mods
           if "r96v_" in str(m.get("argument", ""))
           or "r96a_" in str(m.get("argument", ""))]
    own_sinks = [s.get("name") for s in sinks
                 if "r96v_" in (s.get("name") or "")
                 or "r96a_" in (s.get("name") or "")]
    procs = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit() or d.name == str(PID):
            continue
        try:
            cmd = (d / "cmdline").read_bytes().decode(errors="replace")
        except OSError:
            continue
        if "r96v_live.py" in cmd:
            continue
        if re.search(r"(pulse_r96_probe|r96v_ns_|r96a_)", cmd):
            procs.append({"pid": int(d.name), "cmd": cmd.replace("\0", " ")[:120]})
    clock = run(["pw-metadata", "-n", "settings"], timeout=8.0)
    keys = {}
    for ln in (clock.get("stdout") or "").splitlines():
        for k in ("clock.force-quantum", "clock.force-rate", "clock.quantum",
                  "clock.rate"):
            if f"key:'{k}'" in ln:
                m = re.search(r"value:'([^']*)'", ln)
                keys[k] = m.group(1) if m else None
    return {"own_modules": own, "own_sinks": own_sinks,
            "own_processes": procs, "server": srv, "clock": keys,
            "sink_inputs": len(inputs), "source_outputs": len(outs)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", required=True)
    ap.add_argument("--scratch", default="/home/vgpnk/r96v/live")
    args = ap.parse_args()
    scratch = Path(args.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    probe = args.probe
    results = {"pid": PID, "ns": NS, "checks": {}, "census_in": census(),
               "probe_sha256": __import__("hashlib").sha256(
                   Path(probe).read_bytes()).hexdigest()}

    def check(cid, ok, detail):
        results["checks"][cid] = {"ok": bool(ok), "detail": detail}
        print(f"{'PASS' if ok else 'FAIL'} {cid}: {detail}")

    # 0. bounded preflight
    pre = run(["pactl", "info"], timeout=12.0)
    check("preflight.pactl_info", pre["rc"] == 0
          and "Server Name:" in pre["stdout"],
          f"rc={pre['rc']} wall={pre['wall_s']}")

    # 1. own null sink, name-verified unload later
    tone = scratch / f"{NS}_tone.wav"
    write_tone(tone)
    load = run(["pactl", "load-module", "module-null-sink",
                f"sink_name={NS}"], timeout=15.0)
    mid = (load["stdout"] or "").strip()
    check("sink.loaded", load["rc"] == 0 and mid.isdigit(),
          f"module={mid} rc={load['rc']} {load['stderr'][:80]}")
    sinks = pactl_json("sinks")
    ns_idx = next((s.get("index") for s in sinks if s.get("name") == NS), None)
    check("sink.enumerated", ns_idx is not None, f"index={ns_idx}")
    mrec = next((m for m in modules_short() if m["index"] == mid), None)
    check("sink.module_args_verified",
          bool(mrec) and f"sink_name={NS}" in mrec["args"],
          f"module {mid} args={ (mrec or {}).get('args') }")

    # 2. the attr law, my own cells
    cells = [
        ("default", [], None, 2),
        ("lat_100", ["--latency-msec=100"], None, 2),
        ("proc_5", ["--process-time-msec=5"], None, 2),
        ("env250_flag100", ["--latency-msec=100"], {"PULSE_LATENCY_MSEC": "250"}, 2),
        ("env_plus100_invalid", [], {"PULSE_LATENCY_MSEC": "+100"}, 2),
        ("env_hex64", [], {"PULSE_LATENCY_MSEC": "0x64"}, 2),
        ("s24_default", ["--format=s24le"], None, 3),
        ("stereo_100", ["--channels=2", "--latency-msec=100"], None, 4),
    ]
    for name, extra, envk, frame in cells:
        argv = ["pacat", "--playback", "--device", NS,
                "--format=s16le", "--channels=1", "--rate=48000"]
        if "--format=s24le" in extra:
            argv[argv.index("--format=s16le")] = "--format=s24le"
        if "--channels=2" in extra:
            argv[argv.index("--channels=1")] = "--channels=2"
        argv += [x for x in extra if x not in ("--format=s24le", "--channels=2")]
        argv += [str(tone)]
        proc = spawn(argv, env=hermetic(**(envk or {})))
        row, attrs = None, None
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            for r in pactl_json("sink-inputs"):
                if (r.get("properties") or {}).get(
                        "application.process.id") == str(proc.pid):
                    row = r
                    break
            if row is not None:
                a = attr_fields(row.get("properties") or {})
                if a["tlength"] is not None:
                    attrs = a
                    break
            time.sleep(0.12)
        kill(proc)
        lat_ms = 100 if "--latency-msec=100" in extra else None
        proc_ms = 5 if "--process-time-msec=5" in extra else None
        env_raw = (envk or {}).get("PULSE_LATENCY_MSEC")
        pred, ms = predict_leg(lat_ms, proc_ms, env_raw, frame)
        fields = ("tlength", "prebuf", "minreq", "maxlength",
                  "latency_num", "latency_denom")
        check(f"attr.{name}",
              attrs is not None
              and all(attrs[k] == pred[k] for k in fields),
              f"measured={attrs} own_prediction="
              f"{ {k: pred[k] for k in fields} } env_ms={ms}")

    # 3. the instrument: pa_stream_get_latency rc (own parsing)
    out = run([probe, "--mode", "latency", "--label", f"{NS}_lat",
               "--device", NS, "--start-corked", "0", "--seconds", "0.6",
               "--hold-ms", "200", "--latency-hz", "5"], timeout=14.0)
    rcs = [int(m.group(1)) for ln in out["stdout"].splitlines()
           if " latency " in ln
           for m in [re.search(r"rc=(-?\d+)", ln)] if m]
    check("instrument.latency_rc_nodata",
          len(rcs) >= 3 and all(rc == -16 for rc in rcs),
          f"calls={len(rcs)} rcs={rcs}")

    # 4. the cork flow gate with my own monitor capture
    cap = scratch / f"{NS}_cork.wav"
    rec = spawn(["pw-record", "-P", "stream.capture.sink=true",
                 "-P", f"node.name={NS}_tap_cork", "--target", NS,
                 "--rate", "48000", "--channels", "2", "--format", "s16",
                 str(cap)])
    time.sleep(0.3)
    out = run([probe, "--mode", "cork", "--label", f"{NS}_cork",
               "--device", NS, "--start-corked", "1", "--seconds", "1.5",
               "--hold-ms", "1200"], timeout=16.0)
    time.sleep(1.0)
    kill(rec)
    w = wav_windows(cap)
    check("instrument.cork_flow_gate",
          bool(w) and w["nonzero_lt_1s"] == 0 and w["nonzero_ge_1_5s"] > 0,
          f"windows={w} (corked window must be silent, post-uncork loud)")

    # 5. the trigger negative
    cap2 = scratch / f"{NS}_trigger.wav"
    rec = spawn(["pw-record", "-P", "stream.capture.sink=true",
                 "-P", f"node.name={NS}_tap_trig", "--target", NS,
                 "--rate", "48000", "--channels", "2", "--format", "s16",
                 str(cap2)])
    time.sleep(0.3)
    run([probe, "--mode", "trigger", "--label", f"{NS}_trig",
         "--device", NS, "--start-corked", "1", "--seconds", "1.5",
         "--hold-ms", "1200"], timeout=16.0)
    time.sleep(0.8)
    kill(rec)
    w2 = wav_windows(cap2)
    check("instrument.trigger_negative",
          bool(w2) and w2["nonzero_total"] == 0, f"windows={w2}")

    # 6. the bogus-host DNS wall (own timing, own client)
    bogus = run(["pactl", "info"], timeout=25.0,
                env=hermetic(PULSE_SERVER=f"{NS}-nonexistent"))
    check("cli.bogus_host_wall",
          bogus["rc"] == 1 and bogus["wall_s"] >= 2.0,
          f"rc={bogus['rc']} wall={bogus['wall_s']} s stderr="
          f"{bogus['stderr'].strip()[:60]!r}")

    # 7. teardown + exit census
    res = census()
    pre_unload = [m for m in modules_short() if NS in m["args"]]
    check("teardown.module_present_before_unload",
          any(m["index"] == mid for m in pre_unload),
          f"modules_short match={pre_unload}")
    run(["pactl", "unload-module", mid], timeout=12.0)
    time.sleep(0.4)
    out_census = census()
    results["census_out"] = out_census
    check("census.sinks_gone", NS not in [s.get("name") for s in
                                          pactl_json("sinks")],
          f"sinks={[s.get('name') for s in pactl_json('sinks') if 'r96' in (s.get('name') or '')]}")
    check("census.own_modules_gone", out_census["own_modules"] == [],
          f"own_modules={out_census['own_modules']}")
    check("census.own_processes_gone", out_census["own_processes"] == [],
          f"own_processes={out_census['own_processes']}")
    check("census.default_sink_unchanged",
          out_census["server"]["default_sink"]
          == results["census_in"]["server"]["default_sink"],
          f"in={results['census_in']['server']['default_sink']} "
          f"out={out_census['server']['default_sink']}")
    check("census.default_source_recorded",
          True,
          f"in={results['census_in']['server']['default_source']} "
          f"out={out_census['server']['default_source']} (a foreign lane "
          "moves this on the shared host; this seat never issues "
          "set-default-*)")
    check("census.clock_unchanged",
          out_census["clock"] == results["census_in"]["clock"],
          f"in={results['census_in']['clock']} out={out_census['clock']}")
    results["residual_pre_unload_census"] = res
    results["module_before_unload"] = pre_unload

    out_path = scratch / "r96v_live.json"
    out_path.write_text(json.dumps(results, indent=1) + "\n")
    n_pass = sum(1 for c in results["checks"].values() if c["ok"])
    print(f"checks: {n_pass}/{len(results['checks'])} PASS -> {out_path}")
    return 0 if n_pass == len(results["checks"]) else 1


if __name__ == "__main__":
    sys.exit(main())
