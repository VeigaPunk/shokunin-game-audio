#!/usr/bin/env python3
"""r98b sandbox — private PipeWire core (+ optional WirePlumber) for axis variation.

Seat: audio r98 boundary (leaf). Everything runs inside
corpus/live/r98-boundary/sandbox with PIPEWIRE_RUNTIME_DIR/XDG_* redirected, so
the shared graph is never touched. Own PIDs only; teardown verified.

Experiments (argv[1]):
  geometry  — buffer geometry vs the *server's* clock quantum / rate
  bare      — no session manager: what autoconnect/fallback/capture do without WP
  default   — with WP: does the silent fallback follow the WP default sink?
  drain     — drained period vs server quantum
"""
import json
import os
import resource
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SB = ROOT / "sandbox"
PROBE = ROOT / "probes" / "r98bstream"
REC = ROOT / "receipts"
LOGS = SB / "logs"
for d in (SB, LOGS, SB / "conf" / "pw", SB / "xdg-config", SB / "xdg-state",
          SB / "xdg-data"):
    d.mkdir(parents=True, exist_ok=True)
RT = SB / "rt"
RT.mkdir(mode=0o700, exist_ok=True)

VARIANTS = {
    "q1024": {"default.clock.quantum": 1024},
    "q512": {"default.clock.quantum": 512, "default.clock.max-quantum": 2048},
    "q2048": {"default.clock.quantum": 2048},
    "r44100": {"default.clock.rate": 44100, "default.clock.allowed-rates": "[ 44100 ]"},
}
PROCS = {}


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _preexec():
    os.setsid()
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def make_conf(variant):
    props = VARIANTS[variant]
    cdir = SB / "conf" / "pw" / variant
    (cdir / "pipewire.conf.d").mkdir(parents=True, exist_ok=True)
    shutil.copy("/usr/share/pipewire/pipewire.conf", cdir / "pipewire.conf")
    # clients (pw-cli, the probe) read client.conf from PIPEWIRE_CONFIG_DIR too;
    # without it pw_context_new() fails and the probe dereferences NULL (rc -11)
    shutil.copy("/usr/share/pipewire/client.conf", cdir / "client.conf")
    lines = ["context.properties = {"]
    for k, v in props.items():
        lines.append(f"  {k} = {v}")
    lines += ["  module.profiler = false", "  module.portal = false", "}"]
    (cdir / "pipewire.conf.d" / "10-r98b.conf").write_text("\n".join(lines) + "\n")
    return cdir


def sb_env(variant, extra=None):
    e = dict(os.environ)
    e.update({
        "PIPEWIRE_RUNTIME_DIR": str(RT),
        "XDG_RUNTIME_DIR": str(RT),
        "XDG_CONFIG_HOME": str(SB / "xdg-config"),
        "XDG_STATE_HOME": str(SB / "xdg-state"),
        "XDG_DATA_HOME": str(SB / "xdg-data"),
        "PIPEWIRE_CONFIG_DIR": str(make_conf(variant)),
        "PIPEWIRE_REMOTE": "pipewire-0",
    })
    e.pop("PIPEWIRE_NODE", None)
    e.pop("PIPEWIRE_QUANTUM", None)
    e.pop("PIPEWIRE_AUTOCONNECT", None)
    e.pop("PIPEWIRE_PROPS", None)
    e.pop("PIPEWIRE_LATENCY", None)
    if extra:
        e.update(extra)
    return e


def sh(argv, env, timeout=20):
    t0 = time.time()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout, env=env,
                           preexec_fn=_preexec)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = "timeout", e.stdout or b"", e.stderr or b""
    return {"argv": argv, "rc": rc, "out": out, "err": err,
            "wall_ms": int((time.time() - t0) * 1000)}


def start_core(variant):
    env = sb_env(variant)
    log = open(LOGS / f"{variant}-core.log", "wb")
    p = subprocess.Popen(["pipewire", "-c", "pipewire.conf"], env=env,
                         stdout=log, stderr=log, preexec_fn=_preexec)
    PROCS[f"core-{variant}"] = (p, log, env)
    sock = RT / "pipewire-0"
    for _ in range(80):
        if sock.exists():
            break
        if p.poll() is not None:
            raise RuntimeError(f"core {variant} died rc={p.returncode}; see {log.name}")
        time.sleep(0.25)
    else:
        raise RuntimeError(f"core {variant} socket never appeared")
    return env


def start_wp(variant, env):
    log = open(LOGS / f"{variant}-wp.log", "wb")
    p = subprocess.Popen(["wireplumber"], env=env, stdout=log, stderr=log,
                         preexec_fn=_preexec)
    PROCS[f"wp-{variant}"] = (p, log, env)
    return p


def stop(name, sig=signal.SIGTERM, wait=6):
    if name not in PROCS:
        return None
    p, log, env = PROCS.pop(name)
    if p.poll() is None:
        try:
            os.killpg(os.getpgid(p.pid), sig)
        except Exception:
            pass
        try:
            p.wait(timeout=wait)
        except Exception:
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                p.wait(timeout=5)
            except Exception:
                pass
    log.close()
    return {"name": name, "pid": p.pid, "rc": p.returncode}


def sb_dump(env):
    r = sh(["pw-dump"], env, timeout=25)
    try:
        return json.loads(r["out"])
    except Exception:
        return []


def sb_nodes(env):
    objs = sb_dump(env)
    out = []
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Node"):
            p = o.get("info", {}).get("props", {})
            out.append({"id": o.get("id"), "name": p.get("node.name"),
                        "class": p.get("media.class"), "serial": p.get("object.serial")})
    return out


def create_sink(env, name, channels=1):
    pos = "[MONO]" if channels == 1 else "[FL FR]"
    arg = ("{ factory.name=support.null-audio-sink node.name=" + name +
           " media.class=Audio/Sink object.linger=true audio.position=" + pos + " }")
    r = sh(["pw-cli", "create-node", "adapter", arg], env, timeout=20)
    return r


def links_of(objs, node_name):
    names = {}
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Node"):
            names[o.get("id")] = o.get("info", {}).get("props", {}).get("node.name")
    out = []
    for o in objs:
        if o.get("type", "").startswith("PipeWire:Interface:Link"):
            p = o.get("info", {}).get("props", {})
            on, inn = names.get(p.get("link.output.node")), names.get(p.get("link.input.node"))
            if node_name in (on, inn):
                out.append({"id": o.get("id"), "out": on, "in": inn,
                            "state": p.get("link.state")})
    return out


def parse_out(text):
    d, ev = {}, []
    for line in text.splitlines():
        if line.startswith("R98 "):
            body = line[4:]
            if "=" in body:
                k, v = body.split("=", 1)
                d[k] = v
        elif line.startswith("EV "):
            ev.append(line[3:])
    d["_events"] = ev
    return d


def run_probe(env, args, live=None, timeout=40, tone=None):
    """Run the probe in the sandbox; optional live pw-dump link witness."""
    rec = {"argv": [str(PROBE)] + args, "utc": utc(), "loadavg": open("/proc/loadavg").read().split()[:3]}
    tone_proc = None
    if tone:
        tp = subprocess.Popen(["pw-play", "--target", tone, str(ROOT / "scratch" / "r98b_tone997.wav")],
                              env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              preexec_fn=_preexec)
        tone_proc = tp
        time.sleep(0.4)
    p = subprocess.Popen([str(PROBE)] + args, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, preexec_fn=_preexec)
    snap = None
    try:
        if live is not None:
            time.sleep(live)
            mynode = "r98b_" + (args[0] if not any(a.startswith("name=") for a in args)
                                else [a.split("=", 1)[1] for a in args if a.startswith("name=")][0])
            snap = {"links": links_of(sb_dump(env), mynode)}
        out, err = p.communicate(timeout=timeout)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            pass
        out, err = p.communicate()
        rc = "timeout"
    if tone_proc:
        try:
            os.killpg(os.getpgid(tone_proc.pid), signal.SIGKILL)
        except Exception:
            pass
        tone_proc.wait(timeout=5)
    rec.update({"rc": rc, "parsed": parse_out(out.decode(errors="replace")),
                "stderr": err.decode(errors="replace")[:2000]})
    if snap is not None:
        rec["snapshot"] = snap
    return rec


def geom_view(p):
    return {k: p.get(k) for k in ("state", "cb_count", "last_maxsize", "last_bufid",
                                  "last_nbufs", "last_chunk_size", "last_stride",
                                  "fmt_format", "fmt_rate", "fmt_channels", "delay",
                                  "size", "queued", "queued_buffers", "avail_buffers",
                                  "rate_num", "rate_denom", "n_add_buffer",
                                  "stream_error", "param_ids", "cb_log")}


def find_sink_id(env, name):
    for n in sb_nodes(env):
        if n["name"] == name:
            return n
    return None


# ------------------------------------------------------------- experiments ---

def exp_geometry(reps=3, variants=("q512", "q1024", "q2048", "r44100")):
    out = {"utc": utc(), "experiment": "geometry", "variants": {}, "legs": []}
    for v in variants:
        env = start_core(v)
        create_sink(env, "r98b_sb_ns")
        start_wp(v, env)
        time.sleep(3.5)
        nodes = sb_nodes(env)
        info = run_probe(env, ["info"])
        core_props = {k.split(" ", 1)[1].split("=", 1)[0]: k.split("=", 1)[1]
                      for k in info["parsed"].get("_events", []) if False}
        props = {}
        for line in info["parsed"].get("_raw", []) if False else []:
            pass
        out["variants"][v] = {"nodes": nodes, "info": info["parsed"]}
        for rep in range(reps):
            rec = run_probe(env, ["run", "target=r98b_sb_ns", "flags=autoconnect", "ms=1500"],
                            live=0.8)
            rec["variant"] = v
            rec["rep"] = rep
            rec["geom"] = geom_view(rec["parsed"])
            out["legs"].append(rec)
            print(f"[geom] {v} r{rep} rc={rec['rc']} state={rec['parsed'].get('state')} "
                  f"max={rec['parsed'].get('last_maxsize')} req={rec['parsed'].get('last_bufid')} "
                  f"nbufs={rec['parsed'].get('last_nbufs')} links={rec.get('snapshot',{}).get('links')}",
                  flush=True)
        # a quantum-independent drain probe (period scaling)
        for rep in range(2):
            rec = run_probe(env, ["drain", "target=r98b_sb_ns", "flags=autoconnect",
                                  "ms=2200", "nbuf=5"], live=None)
            rec["variant"] = v
            rec["rep"] = rep
            out["legs"].append(rec)
            print(f"[drain] {v} r{rep} n_drained={rec['parsed'].get('n_drained')} "
                  f"first={rec['parsed'].get('first_drained_ms')} "
                  f"ev={[e for e in rec['parsed'].get('_events', []) if 'drained' in e][:6]}", flush=True)
        stop(f"wp-{v}")
        stop(f"core-{v}")
        time.sleep(1)
    (REC / "sandbox-geometry.json").write_text(json.dumps(out, indent=1))
    return out


def exp_ratios():
    """3-point rate lattice: graph rate x stream rate -> buffer geometry.

    The r44100 sandbox reproduced the shared-graph excursion (maxsize 53500 B,
    requested 30) exactly; this pins the direction of the asymmetry.
    """
    out = {"utc": utc(), "experiment": "rate-lattice", "legs": []}
    combos = [("q1024", None), ("q1024", 44100), ("r44100", None), ("r44100", 44100)]
    for variant, srate in combos:
        env = start_core(variant)
        create_sink(env, "r98b_sb_ns")
        start_wp(variant, env)
        time.sleep(3.5)
        for rep in range(3):
            args = ["run", "target=r98b_sb_ns", "flags=autoconnect", "ms=1200"]
            if srate:
                args.append(f"rate={srate}")
            rec = run_probe(env, args, live=0.7)
            rec["variant"] = variant
            rec["stream_rate"] = srate or 48000
            rec["rep"] = rep
            out["legs"].append(rec)
            p = rec["parsed"]
            print(f"[ratio] graph={variant} stream={srate or 48000} r{rep} "
                  f"state={p.get('state')} max={p.get('last_maxsize')} "
                  f"req={p.get('last_bufid')} nbufs={p.get('last_nbufs')} "
                  f"fmt={p.get('fmt_format')}/{p.get('fmt_rate')} "
                  f"links={[l['in'] for l in rec.get('snapshot', {}).get('links', [])]}",
                  flush=True)
        stop(f"wp-{variant}")
        stop(f"core-{variant}")
        time.sleep(1)
    (REC / "sandbox-ratios.json").write_text(json.dumps(out, indent=1))
    return out


def exp_bare():
    out = {"utc": utc(), "experiment": "bare-no-session-manager", "legs": []}
    env = start_core("q1024")
    create_sink(env, "r98b_sb_ns")
    time.sleep(1.0)
    out["nodes"] = sb_nodes(env)
    legs = [
        ["run", "target=r98b_sb_ns", "flags=autoconnect", "ms=1500"],
        ["run", "target=no_such_r98b", "flags=autoconnect", "ms=1500"],
        ["cap", "dir=in", "target=r98b_sb_ns", "flags=autoconnect", "ms=1200"],
        ["cap", "dir=in", "target=r98b_sb_ns", "props=stream.capture.sink=true",
         "flags=autoconnect", "ms=1200"],
        ["cap", "dir=in", "flags=autoconnect", "ms=1200"],
    ]
    for rep in range(2):
        for args in legs:
            rec = run_probe(env, args, live=0.8)
            rec["rep"] = rep
            rec["geom"] = geom_view(rec["parsed"])
            out["legs"].append(rec)
            print(f"[bare] r{rep} {' '.join(args[:2])} rc={rec['rc']} "
                  f"state={rec['parsed'].get('state')} err={rec['parsed'].get('stream_error')} "
                  f"cb={rec['parsed'].get('cb_count')} links={rec.get('snapshot',{}).get('links')}",
                  flush=True)
    stop("core-q1024")
    (REC / "sandbox-bare.json").write_text(json.dumps(out, indent=1))
    return out


def exp_default():
    """With WP: does the garbage-target fallback follow the WP default sink?"""
    out = {"utc": utc(), "experiment": "default-node-state", "legs": []}
    env = start_core("q1024")
    create_sink(env, "r98b_sb_a")
    create_sink(env, "r98b_sb_b")
    start_wp("q1024", env)
    time.sleep(4.0)
    nodes = sb_nodes(env)
    out["nodes"] = nodes
    a = find_sink_id(env, "r98b_sb_a")
    b = find_sink_id(env, "r98b_sb_b")
    out["ids"] = {"a": a, "b": b}

    def set_default(name):
        return sh(["pw-metadata", "-n", "default", "0", "default.audio.sink",
                   json.dumps({"name": name})], env, timeout=15)

    def read_default():
        return sh(["pw-metadata", "-n", "default", "0", "default.audio.sink"], env, timeout=15)

    for target_default in ("r98b_sb_b", "r98b_sb_a", "r98b_sb_b"):
        setr = set_default(target_default)
        time.sleep(1.2)
        cur = read_default()
        for rep in range(3):
            rec = run_probe(env, ["run", "target=no_such_r98b", "flags=autoconnect",
                                  "ms=1200", "name=fb"], live=0.7)
            rec["rep"] = rep
            rec["default_set_to"] = target_default
            rec["set_rc"] = setr["rc"]
            rec["default_readback"] = cur["out"].decode(errors="replace").strip()
            out["legs"].append(rec)
            print(f"[default={target_default}] r{rep} state={rec['parsed'].get('state')} "
                  f"links={rec.get('snapshot',{}).get('links')} "
                  f"err={rec['parsed'].get('stream_error')}", flush=True)
        # exact-name resolution against the non-default sink
        rec = run_probe(env, ["run", "target=r98b_sb_a", "flags=autoconnect",
                              "ms=1200", "name=exact"], live=0.7)
        rec["default_set_to"] = target_default
        out["legs"].append(rec)
        print(f"[exact-name=a default={target_default}] links={rec.get('snapshot',{}).get('links')}",
              flush=True)
    stop("wp-q1024")
    stop("core-q1024")
    (REC / "sandbox-default.json").write_text(json.dumps(out, indent=1))
    return out


def main():
    exp = sys.argv[1] if len(sys.argv) > 1 else "geometry"
    try:
        if exp == "geometry":
            exp_geometry()
        elif exp == "ratios":
            exp_ratios()
        elif exp == "bare":
            exp_bare()
        elif exp == "default":
            exp_default()
        else:
            raise SystemExit(f"unknown experiment {exp}")
    finally:
        for name in list(PROCS):
            stop(name)
        # verify no r98b objects leaked into the *shared* graph
        shared = sh(["pw-dump"], dict(os.environ), timeout=25)
        leaked = [l for l in shared["out"].decode(errors="replace").splitlines()
                  if "r98b_sb" in l]
        sock = (RT / "pipewire-0").exists()
        print(json.dumps({"utc": utc(), "socket_left": sock,
                          "shared_r98b_sb_mentions": len(leaked)}), flush=True)
        (REC / f"sandbox-teardown-{exp}.json").write_text(json.dumps(
            {"utc": utc(), "experiment": exp, "socket_left": sock,
             "shared_r98b_sb_mentions": len(leaked)}, indent=1))


if __name__ == "__main__":
    main()
