#!/usr/bin/env python3
"""r100 scout — sofa/spatializer HRTF probe (seat-owned, bounded, self-cleaning).

Surface under test: `libpipewire-module-filter-chain` node type `sofa`
(label `spatializer`) with the host's shipped SOFA HRIR file
(/usr/share/libmysofa/MIT_KEMAR_normal_pinna.sofa, Data.SamplingRate = 44100).

Hypotheses (predeclared):
  H1  no-config spatializer is SILENT (r92 [?]3 predicted, not measured)
  H2  a real SOFA file at a mismatched graph rate (48000) is refused/na
  H3  a real SOFA file at the matching graph rate (44100) loads and produces
      NON-SILENT stereo output from a mono input
  H4  Azimuth (90 = left, 270 = right) moves the energy between L and R

Harness: imports the r92-scout `pwlib` (read-only, sibling seat, proven) and
builds its own seat-local rig. Every child is element+wall+byte bounded and
killed by process group. All PipeWire objects are `r100s*` and are unloaded by
verified index; nothing touches the operator's devices (node.autoconnect=false
on every stream).
"""
import importlib.util
import json
import math
import os
import signal
import struct
import subprocess
import sys
import time
import wave

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # corpus/live/r100-scout
R92P = os.path.join(os.path.dirname(HERE), "r92-scout", "probes")
_spec = importlib.util.spec_from_file_location("pwlib", os.path.join(R92P, "pwlib.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)

SCRATCH = os.path.join(HERE, "scratch")
RUNS = os.path.join(HERE, "runs")
REC = os.path.join(HERE, "receipts")
for d in (SCRATCH, RUNS, REC):
    os.makedirs(d, exist_ok=True)

SOFA = "/usr/share/libmysofa/MIT_KEMAR_normal_pinna.sofa"
NS_IN, NS_REC = "r100s_in", "r100s_rec"
FC_IN, FC_OUT = "r100s_sofa_in", "r100s_sofa_out"
TOOL_PREFIX = ("pw-play", "pw-record", "pw-cli", "pw-link", "pw-dump", "pactl", "pipewire")


# ------------------------------------------------------------------ host state
def live():
    d = L.run(["pw-dump"], wall=8.0)
    names = []
    try:
        for o in json.loads(d.out):
            if o.get("type") != "PipeWire:Interface:Node":
                continue
            nm = o.get("info", {}).get("props", {}).get("node.name", "")
            if nm.startswith("r100s"):
                names.append(nm)
    except Exception:
        pass
    mods = []
    for line in L.run(["pactl", "list", "modules", "short"], wall=6.0).out.splitlines():
        if "r100s" in line:
            mods.append(line.split()[0])
    procs = []
    for l in L.run(["ps", "-eo", "pid,cmd"], wall=5.0).out.splitlines():
        p = l.strip().split(None, 1)
        if len(p) == 2 and p[1].startswith(TOOL_PREFIX) and "r100s" in p[1]:
            procs.append(l.strip()[:140])
    return {"nodes": names, "modules": mods, "procs": procs}


def sweep():
    before = live()
    for m in before["modules"]:
        L.run(["pactl", "unload-module", m], wall=6.0)
    for l in before["procs"]:
        try:
            os.kill(int(l.split()[0]), signal.SIGKILL)
        except Exception:
            pass
    time.sleep(0.6)
    after = live()
    return {"before": before, "after": after,
            "clean": not (after["nodes"] or after["modules"] or after["procs"])}


def sink_load(name, channels, rate):
    extra = ("channels=%d rate=%d sink_properties=state.restore-props=false"
             % (channels, rate))
    out = L.run(["pactl", "load-module", "module-null-sink",
                 "sink_name=%s" % name, extra], wall=6.0)
    mid = None
    try:
        mid = int(out.out.strip().split()[-1])
    except Exception:
        pass
    return {"argv": out.argv, "rc": out.rc, "out": out.out.strip(), "id": mid}


def sink_unload(name, expect_id):
    """Unload only if the index is still the one this leg created."""
    lst = L.run(["pactl", "list", "modules", "short"], wall=6.0).out
    cand = [int(l.split()[0]) for l in lst.splitlines()
            if "module-null-sink" in l and ("sink_name=%s" % name) in l]
    if expect_id not in cand:
        return {"rc": None, "note": "id-not-found", "cand": cand}
    out = L.run(["pactl", "unload-module", str(expect_id)], wall=6.0)
    return {"rc": out.rc, "out": out.out.strip()}


# ------------------------------------------------------------------ rig
class Bg:
    def __init__(self, argv, wall=10.0):
        self.argv = argv
        self.wall = wall
        self.p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.DEVNULL, start_new_session=True,
                                  preexec_fn=L._ncore)

    def stop(self):
        try:
            os.killpg(os.getpgid(self.p.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            out, err = self.p.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = self.p.communicate()
        return {"argv": self.argv, "rc": self.p.returncode,
                "out": out.decode("utf-8", "replace")[-800:],
                "err": err.decode("utf-8", "replace")[-800:]}


def link(a, b, tries=12):
    last = None
    for i in range(tries):
        r = L.run(["pw-link", a, b], wall=4.0)
        last = r
        if r.rc == 0:
            return {"argv": [a, b], "rc": 0, "tries": i + 1}
        if "File exists" in r.err:
            return {"argv": [a, b], "rc": 0, "tries": i + 1, "note": "already"}
        time.sleep(0.25)
    return {"argv": [a, b], "rc": last.rc, "err": last.err.strip()[-200:], "tries": tries}


def ports_of(node_name):
    out = L.run(["pw-link", "-o"], wall=5.0).out + L.run(["pw-link", "-i"], wall=5.0).out
    return sorted(l.strip() for l in out.splitlines() if node_name in l)


def fc_log_lines(text):
    keep = []
    for l in text.splitlines():
        low = l.lower()
        if any(k in low for k in ("spatializer", "sofa", "sampling rate",
                                  "using n_samples", "error", "warn")):
            keep.append(l.strip()[:300])
    return keep[-40:]


def args_token(rate, node_tok):
    return ("node.description=r100s_sofa,filter.graph={nodes=[%s]},audio.channels=1,"
            "audio.position=[MONO],audio.rate=%d,"
            "capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},"
            "playback.props={node.name=%s,node.autoconnect=false,audio.channels=2,"
            "audio.position=[FL,FR]}" % (node_tok, rate, FC_IN, FC_OUT))


def make_tone(path, rate, freq=440.0, secs=1.6, amp=0.5):
    n = int(rate * secs)
    L.write_wav(path, [amp * math.sin(2 * math.pi * freq * i / rate) for i in range(n)],
                rate=rate, ch=1)
    return path


def best_window(x, win):
    if len(x) <= win:
        return x, 0
    best, bi = -1.0, 0
    step = max(1, win // 10)
    for i in range(0, len(x) - win + 1, step):
        r = sum(v * v for v in x[i:i + win])
        if r > best:
            best, bi = r, i
    return x[bi:bi + win], bi


def goertzel(x, f, rate):
    if not x:
        return 0.0
    w = 2 * math.pi * f / rate
    c = 2 * math.cos(w)
    s1 = s2 = 0.0
    for v in x:
        s0 = v + c * s1 - s2
        s2, s1 = s1, s0
    p = s1 * s1 + s2 * s2 - c * s1 * s2
    return 2.0 * math.sqrt(max(0.0, p)) / len(x)


def analyze(path, rate):
    if not os.path.exists(path):
        return {"bytes": 0}
    w = L.read_wav(path)
    res = {"bytes": os.path.getsize(path), "frames": w["frames"], "ch": w["ch"]}
    if w["ch"] < 2:
        res["ch_warning"] = "expected stereo"
    win = min(int(0.4 * rate), max(1, w["frames"]))
    res["channels"] = []
    for ci, x in enumerate(w["x"]):
        seg, off = best_window(x, win)
        rms = (sum(v * v for v in seg) / max(1, len(seg))) ** 0.5
        pk = max((abs(v) for v in x), default=0.0)
        res["channels"].append({
            "rms": round(rms, 8), "peak": round(pk, 6),
            "tone440": round(goertzel(seg, 440.0, w["rate"]), 8),
            "win_offset": off, "rate": w["rate"]})
    if len(res["channels"]) >= 2:
        l, r = res["channels"][0]["rms"], res["channels"][1]["rms"]
        res["ild_db"] = round(20 * math.log10(max(1e-12, l) / max(1e-12, r)), 3)
    return res


def run_leg(name, rate, node_tok, azimuth=None, rep=0, tone_secs=1.6):
    """One bounded leg; returns a JSON-able row."""
    t0 = time.time()
    tag = "%s_r%d" % (name, rep)
    row = {"leg": name, "rep": rep, "rate": rate, "azimuth": azimuth,
           "node": node_tok, "argv_args": args_token(rate, node_tok)}
    sw = sweep()
    row["pre_sweep"] = sw
    sink = sink_load(NS_IN, 1, rate)
    row["sinks"] = {"in": sink}
    cli = L.PwCli(env={"PIPEWIRE_DEBUG": "3"}, idle=0.4, hard=3.0)
    out_wav = os.path.join(SCRATCH, "cap_%s.wav" % tag)
    if os.path.exists(out_wav):
        os.unlink(out_wav)
    recp = None
    try:
        out, var = cli.load("libpipewire-module-filter-chain", args_token(rate, node_tok))
        row["load_out"] = out.strip()[-600:]
        row["module_var"] = var
        time.sleep(0.7)
        row["nodes_now"] = sorted(n for n in live()["nodes"])
        row["ports_fc_in"] = ports_of(FC_IN)
        row["ports_fc_out"] = ports_of(FC_OUT)
        # post tap = a pw-record STREAM (its input_FL/input_FR ports are the sink side)
        recp = Bg(["pw-record", "--channels", "2", "-P", "node.name=%s" % NS_REC,
                   "-P", "node.autoconnect=false", out_wav], wall=tone_secs + 6.0)
        time.sleep(0.8)
        row["ports_rec"] = ports_of(NS_REC)
        row["links"] = []
        if var is not None and row["ports_fc_in"] and row["ports_fc_out"]:
            row["links"].append(link("%s:monitor_MONO" % NS_IN, "%s:playback_MONO" % FC_IN))
            for ch in ("FL", "FR"):
                row["links"].append(link("%s:output_%s" % (FC_OUT, ch),
                                         "%s:input_%s" % (NS_REC, ch)))
        tone = make_tone(os.path.join(SCRATCH, "tone_%d.wav" % rate), rate, secs=tone_secs)
        play = L.run(["pw-play", "--target", NS_IN, tone], wall=tone_secs + 3.0)
        row["play"] = play.as_dict()
        time.sleep(0.5)
        stop = recp.stop()
        recp = None
        row["rec"] = stop
        row["analysis"] = analyze(out_wav, rate)
        row["links_after"] = [l.strip() for l in L.run(["pw-link", "-l"], wall=5.0).out.splitlines()
                              if "r100s" in l]
        if var is not None:
            try:
                row["unload"] = cli.cmd("unload-module %d" % var, idle=0.4, hard=2.5)[-300:]
            except Exception as e:  # pw-cli can die (r92 §2.7 crash class) after the take
                row["unload"] = {"error": repr(e)}
    except Exception as e:  # a leg must never kill the stage; record and continue
        row["leg_error"] = repr(e)
    finally:
        if recp is not None:
            row["rec"] = recp.stop()
        log = cli.close()
        row["fc_log"] = fc_log_lines("\n".join(log))
        row["sink_unloads"] = {"in": sink_unload(NS_IN, sink["id"])}
        time.sleep(0.4)
        row["post_sweep"] = sweep()
    row["wall_s"] = round(time.time() - t0, 2)
    return row


# ------------------------------------------------------------------ stages
def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    res = {"seat": "r100s", "surface": "sofa/spatializer", "sofa_file": SOFA,
           "sofa_rate": 44100, "stages": {}}

    def save(name, rows):
        res["stages"][name] = rows
        with open(os.path.join(RUNS, "sofa_%s.json" % name), "w") as f:
            json.dump(rows, f, indent=1)

    if stage in ("all", "gate"):
        rows = []
        # A: no config at 48000 (r92 [?]3)
        rows.append(run_leg("noconfig_48k", 48000, "{type=sofa,name=s0,label=spatializer}"))
        # B: real SOFA at mismatched rate 48000
        rows.append(run_leg("sofa_48k", 48000,
                            '{type=sofa,name=s0,label=spatializer,config={filename=%s}}' % SOFA))
        # C: real SOFA at matching rate 44100, azimuth 0
        rows.append(run_leg("sofa_44k_az0", 44100,
                            '{type=sofa,name=s0,label=spatializer,config={filename=%s},'
                            'control={Azimuth=0.0,Elevation=0.0,Radius=1.0}}' % SOFA))
        save("gate", rows)
        for r in rows:
            a = r.get("analysis", {})
            print("%-14s load_var=%s ports=%s/%s ild=%s rms=%s" % (
                r["leg"], r.get("module_var"), len(r.get("ports_fc_in", [])),
                len(r.get("ports_fc_out", [])), a.get("ild_db"),
                [c["rms"] for c in a.get("channels", [])]))

    if stage in ("all", "azimuth"):
        rows = []
        for az in (0.0, 90.0, 270.0):
            for rep in range(3):
                rows.append(run_leg("sofa_44k_az%d" % int(az), 44100,
                                    '{type=sofa,name=s0,label=spatializer,'
                                    'config={filename=%s},'
                                    'control={Azimuth=%s,Elevation=0.0,Radius=1.0}}'
                                    % (SOFA, az), azimuth=az, rep=rep))
        save("azimuth", rows)
        for r in rows:
            a = r.get("analysis", {})
            print("%-16s r%d ild=%-8s rms=%s" % (
                r["leg"], r["rep"], a.get("ild_db"),
                [c["rms"] for c in a.get("channels", [])]))

    if stage in ("all", "extra"):
        rows = []
        # F1: does the HRTF survive a graph-rate mismatch (48000 vs file 44100)?
        for rep in range(3):
            rows.append(run_leg("sofa_48k_az90", 48000,
                                '{type=sofa,name=s0,label=spatializer,'
                                'config={filename=%s},'
                                'control={Azimuth=90.0,Elevation=0.0,Radius=1.0}}'
                                % SOFA, azimuth=90.0, rep=rep))
        # F2: front/back — az180 must NOT be identical to az0 (spectral, not ILD)
        for rep in range(2):
            rows.append(run_leg("sofa_44k_az180", 44100,
                                '{type=sofa,name=s0,label=spatializer,'
                                'config={filename=%s},'
                                'control={Azimuth=180.0,Elevation=0.0,Radius=1.0}}'
                                % SOFA, azimuth=180.0, rep=rep))
        save("extra", rows)
        for r in rows:
            a = r.get("analysis", {})
            print("%-16s r%d ild=%-8s tone=%s" % (
                r["leg"], r["rep"], a.get("ild_db"),
                [c["tone440"] for c in a.get("channels", [])]))

    with open(os.path.join(REC, "sofa_probe_%s.json" % stage), "w") as f:
        json.dump(res, f, indent=1)
    print("final sweep:", sweep())


if __name__ == "__main__":
    main()
