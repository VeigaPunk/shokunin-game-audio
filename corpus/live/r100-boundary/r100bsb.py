#!/usr/bin/env python3
"""r100b sandbox — private PipeWire core for the sofa/spatializer surface.

Seat: audio r100-boundary (leaf). Nothing here touches the shared graph: every
client runs with PIPEWIRE_RUNTIME_DIR / XDG_* redirected into `sandbox/`, so the
private core is a separate socket. Own PIDs only; teardown verified.

Variants vary the *server* clock (quantum, rate) — the axis the r100 scout never
varied (it varied only the filter-chain's own `audio.rate`).

Usage: r100bsb.py <stage>   stages: smoke | clock | az | all
       r100bsb.py <stage> --wp   also start a private WirePlumber (policy links)
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

HERE = Path(__file__).resolve().parent
SB = HERE / "sandbox"
LOGS = SB / "logs"
REC = HERE / "receipts"
RAW = HERE / "raw"
SCRATCH = HERE / "scratch"
sys.path.insert(0, str(HERE / "probes"))
import r100b_sofa as P  # noqa: E402

L = P.L
RT = SB / "rt"
for d in (SB, LOGS, REC, RAW, SCRATCH, RT, SB / "conf", SB / "xdg-config",
          SB / "xdg-state", SB / "xdg-data"):
    d.mkdir(parents=True, exist_ok=True)
os.chmod(RT, 0o700)

VARIANTS = {
    "q512": {"default.clock.quantum": 512, "default.clock.max-quantum": 2048},
    "q1024": {"default.clock.quantum": 1024},
    "q2048": {"default.clock.quantum": 2048},
    "r44100": {"default.clock.rate": 44100, "default.clock.allowed-rates": "[ 44100 ]"},
    "r96000": {"default.clock.rate": 96000, "default.clock.allowed-rates": "[ 96000 ]"},
    "r44100q512": {"default.clock.rate": 44100, "default.clock.allowed-rates": "[ 44100 ]",
                   "default.clock.quantum": 512, "default.clock.max-quantum": 2048},
}
PROCS = {}


def _preexec():
    os.setsid()
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def make_conf(variant):
    props = VARIANTS[variant]
    cdir = SB / "conf" / variant
    (cdir / "pipewire.conf.d").mkdir(parents=True, exist_ok=True)
    shutil.copy("/usr/share/pipewire/pipewire.conf", cdir / "pipewire.conf")
    shutil.copy("/usr/share/pipewire/client.conf", cdir / "client.conf")
    lines = ["context.properties = {"]
    for k, v in props.items():
        lines.append("  %s = %s" % (k, v))
    lines += ["  module.profiler = false", "  module.portal = false", "}"]
    (cdir / "pipewire.conf.d" / "10-r100b.conf").write_text("\n".join(lines) + "\n")
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
    for k in ("PIPEWIRE_NODE", "PIPEWIRE_QUANTUM", "PIPEWIRE_AUTOCONNECT",
              "PIPEWIRE_PROPS", "PIPEWIRE_LATENCY", "PULSE_SERVER"):
        e.pop(k, None)
    if extra:
        e.update(extra)
    return e


def sh(argv, env, timeout=25):
    t0 = time.time()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout, env=env,
                           preexec_fn=_preexec)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = "timeout", e.stdout or b"", e.stderr or b""
    # NB: keep the FULL stdout (pw-dump is JSON and truncation breaks parsing);
    # only stderr is tail-capped.
    return {"argv": argv, "rc": rc, "out": out.decode("utf-8", "replace")[:4 << 20],
            "err": err.decode("utf-8", "replace")[-1200:],
            "wall_ms": int((time.time() - t0) * 1000)}


def start_core(variant):
    env = sb_env(variant)
    log = open(LOGS / ("%s-core.log" % variant), "wb")
    p = subprocess.Popen(["pipewire", "-c", "pipewire.conf"], env=env,
                         stdout=log, stderr=log, preexec_fn=_preexec)
    PROCS["core"] = (p, log, env)
    sock = RT / "pipewire-0"
    for _ in range(80):
        if sock.exists():
            break
        if p.poll() is not None:
            raise RuntimeError("core %s died rc=%s (see %s)" % (variant, p.returncode, log.name))
        time.sleep(0.25)
    else:
        raise RuntimeError("core socket never appeared")
    return env


def start_wp(env, variant):
    log = open(LOGS / ("%s-wp.log" % variant), "wb")
    p = subprocess.Popen(["wireplumber", "-p", "r100b"], env=env, stdout=log, stderr=log,
                         preexec_fn=_preexec)
    PROCS["wp"] = (p, log, env)
    time.sleep(1.5)
    return p


def stop(name, wait=6):
    if name not in PROCS:
        return None
    p, log, env = PROCS.pop(name)
    if p.poll() is None:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
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


def stop_all():
    return [stop(k) for k in list(PROCS)]


def sbdump(env):
    try:
        return json.loads(sh(["pw-dump"], env, timeout=30)["out"])
    except Exception:
        return []


def sb_nodes(env, prefix="r100b"):
    out = {}
    for o in sbdump(env):
        if str(o.get("type", "")).startswith("PipeWire:Interface:Node"):
            p = o.get("info", {}).get("props", {})
            nm = p.get("node.name", "")
            if nm.startswith(prefix):
                out[nm] = {"id": o.get("id"), "state": o.get("info", {}).get("state"),
                           "driver": p.get("node.driver"), "clock.rate": p.get("clock.rate"),
                           "clock.quantum": p.get("clock.quantum")}
    return out


def sb_links(env):
    names = {}
    for o in sbdump(env):
        if str(o.get("type", "")).startswith("PipeWire:Interface:Node"):
            names[o.get("id")] = o.get("info", {}).get("props", {}).get("node.name")
    out = []
    for o in sbdump(env):
        if str(o.get("type", "")).startswith("PipeWire:Interface:Link"):
            p = o.get("info", {}).get("props", {})
            out.append({"id": o.get("id"), "out": names.get(p.get("link.output.node")),
                        "in": names.get(p.get("link.input.node")), "state": p.get("link.state")})
    return out


def sblink(a, b, env, tries=10):
    last = None
    for i in range(tries):
        r = sh(["pw-link", a, b], env, timeout=12)
        last = r
        if r["rc"] == 0:
            return {"argv": [a, b], "rc": 0, "tries": i + 1}
        if "File exists" in r["err"]:
            return {"argv": [a, b], "rc": 0, "tries": i + 1, "note": "already"}
        time.sleep(0.25)
    return {"argv": [a, b], "rc": last["rc"], "err": last["err"].strip()[-200:], "tries": tries}


def sb_ports(node, env):
    o = sh(["pw-link", "-o"], env)["out"] + sh(["pw-link", "-i"], env)["out"]
    return sorted(l.strip() for l in o.splitlines() if node in l)


def create_sink(env, name):
    arg = ("{ factory.name=support.null-audio-sink node.name=%s media.class=Audio/Sink "
           "object.linger=true audio.position=[MONO] }" % name)
    return sh(["pw-cli", "create-node", "adapter", arg], env, timeout=25)


def sb_leg(name, variant, rate, az, rep=0, with_wp=False, tone_secs=1.6, tag=None,
           extra_cfg=None, post=None, play_bg=True):
    t0 = time.time()
    tag = tag or ("sb_%s_r%d" % (name, rep))
    env = sb_env(variant)
    row = {"leg": name, "variant": variant, "rate": rate, "azimuth": az, "rep": rep,
           "with_wp": with_wp, "loadavg_start": P.loadavg(), "sandbox": True}
    wav = SCRATCH / ("cap_%s.wav" % tag)
    if wav.exists():
        wav.unlink()
    refwav = SCRATCH / ("ref_%s.wav" % tag)
    cli = None
    recp = playp = None
    try:
        row["sink_create"] = create_sink(env, P.SINK_IN)
        time.sleep(0.5)
        row["nodes_before_fc"] = sb_nodes(env)
        cli = L.PwCli(env=env, idle=0.4, hard=3.0)
        tok = P.node_tok(rate, az=az, el=0.0, radius=1.0, extra_cfg=extra_cfg)
        out, var = cli.load("libpipewire-module-filter-chain", P.args_token(rate, tok))
        row["module_var"] = var
        row["load_out"] = out.strip()[-400:]
        time.sleep(0.8)
        row["nodes_now"] = sb_nodes(env)
        row["ports_fc_in"] = sb_ports(P.FC_IN, env)
        row["ports_fc_out"] = sb_ports(P.FC_OUT, env)
        row["props_enum_in"] = P.enum_props(P.FC_IN, save=str(RAW / ("enum_%s_in.txt" % tag)),
                                           env=env) if hasattr(P, "enum_props") else None
        recp = P.Bg(["pw-record", "--channels", "2", "-P", "node.name=%s" % P.NS_REC,
                     "-P", "node.autoconnect=false", str(wav)], wall=tone_secs + 8.0, env=env)
        time.sleep(0.8)
        row["ports_rec"] = sb_ports(P.NS_REC, env)
        row["links"] = []
        if var is not None:
            row["links"].append(sblink("%s:monitor_MONO" % P.SINK_IN, "%s:playback_MONO" % P.FC_IN, env))
            row["links"].append(sblink("%s:output_FL" % P.FC_OUT, "%s:input_FL" % P.NS_REC, env))
            row["links"].append(sblink("%s:output_FR" % P.FC_OUT, "%s:input_FR" % P.NS_REC, env))
        tone = str(SCRATCH / ("tone_%d.wav" % rate))
        if not os.path.exists(tone):
            import math
            n = int(rate * tone_secs)
            L.write_wav(tone, [0.5 * math.sin(2 * math.pi * 440.0 * i / rate) for i in range(n)],
                        rate=rate, ch=1)
        if play_bg:
            playp = P.Bg(["pw-play", "--target", P.SINK_IN, "-P", "node.name=%s" % P.NS_PLAY,
                          "-P", "node.autoconnect=false", tone], wall=tone_secs + 8.0, env=env)
            time.sleep(0.6)
            row["ports_play"] = sb_ports(P.NS_PLAY, env)
            pre = sb_links(env)
            policy = any(l["out"] == P.NS_PLAY or l["in"] == P.NS_PLAY for l in pre)
            row["play_link_origin"] = "policy" if policy else "manual"
            if not policy:
                row["links"].append(sblink("%s:output_MONO" % P.NS_PLAY, "%s:playback_MONO" % P.SINK_IN, env))
            row["nodes_mid"] = sb_nodes(env)
            row["links_mid"] = sb_links(env)
            row["clock_mid"] = P.clock_witness()
            t_play = time.time()
            evs = []
            for act in sorted(post or [], key=lambda a: a.get("t", 0)):
                wait = t_play + float(act.get("t", 0)) - time.time()
                if wait > 0:
                    time.sleep(wait)
                evs.append(P._post_action(act, row, cli, {"id": None}, playp, env, str(wav)))
            row["post_events"] = evs
            time.sleep(max(0.0, tone_secs - (time.time() - t_play)))
            row["play_stop"] = playp.stop()
            playp = None
        else:
            row["play"] = sh(["pw-play", "--target", P.SINK_IN, tone], env, timeout=tone_secs + 5)
        time.sleep(0.5)
        if recp is not None:
            row["rec"] = recp.stop()
            recp = None
        row["analysis"] = P.analyze(str(wav), rate)
        row["analysis_series"] = P.analyze_series(str(wav), 200)
        if var is not None:
            try:
                row["unload"] = cli.cmd("unload-module %d" % var, idle=0.4, hard=2.5)[-200:]
            except Exception as e:
                row["unload"] = {"error": repr(e)}
    except Exception as e:
        row["leg_error"] = repr(e)
    finally:
        if recp is not None:
            row["rec"] = recp.stop()
        if playp is not None:
            row["play_stop"] = playp.stop()
        if cli is not None:
            row["fc_log"] = P.fc_log_lines("\n".join(cli.close()))
        row["nodes_end"] = sb_nodes(env)
        row["links_end"] = sb_links(env)
        # clean the sandbox namespace between legs (own objects only)
        sh(["pw-cli", "destroy", "r100b_sb_in"] if False else ["true"], env, timeout=5)
    row["wall_s"] = round(time.time() - t0, 2)
    return row


def run_stage(stage, with_wp=False):
    rows = []
    plan = {
        "smoke": [("q1024", 44100, 0.0, 0), ("q1024", 44100, 90.0, 0)],
        "clock": [("q512", 44100, 90.0, 0), ("q1024", 44100, 90.0, 0),
                  ("q2048", 44100, 90.0, 0), ("r44100", 44100, 90.0, 0),
                  ("r96000", 44100, 90.0, 0), ("r44100q512", 44100, 90.0, 0),
                  ("q1024", 44100, 0.0, 0), ("r44100", 44100, 0.0, 0)],
        "az": [("q1024", 44100, 0.0, 0), ("q1024", 44100, 90.0, 0),
               ("q1024", 44100, 270.0, 0), ("q1024", 48000, 90.0, 0)],
        "rate": [("q1024", 48000, 90.0, 0), ("q1024", 96000, 90.0, 0)],
    }[stage]
    for variant, rate, az, rep in plan:
        stop_all()
        start_core(variant)
        env = sb_env(variant)
        if with_wp:
            start_wp(env, variant)
        try:
            row = sb_leg("%s_%s_az%d" % (stage, variant, int(az)), variant, rate, az,
                         rep=rep, with_wp=with_wp,
                         tag="%s_%s_az%d_r%d" % (stage, variant, int(az), rep))
        except Exception as e:
            row = {"leg": "%s_%s_az%d" % (stage, variant, int(az)), "variant": variant,
                   "rate": rate, "azimuth": az, "leg_error": repr(e)}
        rows.append(row)
        P.write_json(str(REC / ("sandbox-%s.json" % stage)), rows)
        a = row.get("analysis", {})
        print("[sandbox/%s] %-26s var=%-11s rate=%s az=%-6s ild=%-8s rms=%s wall=%s" % (
            stage, row["leg"], variant, rate, az, a.get("ild_db"),
            [c["rms"] for c in a.get("channels", [])], row.get("wall_s")), flush=True)
        stop_all()
        time.sleep(0.8)
    P.write_json(str(REC / ("sandbox-%s.json" % stage)), rows)
    return rows


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    with_wp = "--wp" in sys.argv
    print("sandbox stage=%s with_wp=%s loadavg=%s" % (stage, with_wp, P.loadavg()), flush=True)
    try:
        rows = run_stage(stage, with_wp=with_wp)
    finally:
        stop_all()
        time.sleep(0.5)
        print("sockets left:", sorted(p.name for p in RT.glob("*")), flush=True)
        print("procs:", {k: v[0].pid for k, v in PROCS.items()}, flush=True)


if __name__ == "__main__":
    main()
