#!/usr/bin/env python3
"""r92 scout driver — libpipewire-module-filter-chain (SPA filter-graph host).

Stages (argv[1]):
  shape    load-shape census across graph variants (no tone)
  dsp      biquad family + gain/copy/mixer/param_eq + identity, multitone probe
  ir       convolver + delay, delta-stimulus impulse-response capture
  configs  the 12 shipped /usr/share/pipewire/filter-chain/*.conf, load matrix
  absent   ladspa / lv2 / sofa / ffmpeg / ebur128 classes
  rate     audio.rate mismatch (chain 44100 vs graph 48000)

argv[2] = reps (default 3).
Triple bounds: every child has a wall cap (killpg) + byte cap; the pipeline
itself has a per-leg wall cap. Seat-owned names only (r92s_*).
"""
import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(HERE, "runs")
SCRATCH = os.path.join(HERE, "scratch")
REC = os.path.join(HERE, "receipts")
for d in (RUNS, SCRATCH, REC):
    os.makedirs(d, exist_ok=True)

NS_IN, NS_OUT = "r92s_in", "r92s_out"
FC_IN, FC_OUT = "r92s_fc_in", "r92s_fc_out"
PLAY, RECN = "r92s_play", "r92s_rec"

TONE_FREQS = [200, 1000, 4000, 12000]
RATE = 48000


def fckwargs(nodes, **kw):
    """Build the pw-cli module-args token (comma form, no spaces)."""
    g = "filter.graph={nodes=[%s]" % ",".join(nodes)
    if kw.get("links"):
        g += ",links=[%s]" % ",".join(kw["links"])
    if kw.get("inputs"):
        g += ",inputs=[%s]" % ",".join(kw["inputs"])
    if kw.get("outputs"):
        g += ",outputs=[%s]" % ",".join(kw["outputs"])
    g += "}"
    parts = ["node.description=r92s_fc", g,
             "audio.channels=%d" % kw.get("channels", 1),
             "audio.position=[MONO]" if kw.get("channels", 1) == 1 else "audio.position=[FL,FR]"]
    if kw.get("rate"):
        parts.append("audio.rate=%d" % kw["rate"])
    if kw.get("capture_props"):
        parts.append("capture.props={%s}" % kw["capture_props"])
    if kw.get("playback_props"):
        parts.append("playback.props={%s}" % kw["playback_props"])
    return ",".join(parts)


def NODE(label, name="f1", **ctl):
    """One filter.graph node. The braces are REQUIRED: spa-json rejects a bare
    `k=v` element inside `[...]` with `Invalid array separator`."""
    return "{%s}" % ("type=builtin,name=%s,label=%s" % (name, label)
                     + (",control={%s}" % ",".join("%s=%s" % kv for kv in ctl.items())
                        if ctl else ""))


class Bg:
    """Background child with wall cap + killpg teardown."""

    def __init__(self, argv, wall=12.0, env=None):
        self.argv = argv
        self.wall = wall
        self.t0 = time.time()
        e = dict(os.environ)
        if env:
            e.update(env)
        self.p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.DEVNULL, start_new_session=True, env=e,
                                  preexec_fn=L._ncore)

    def stop(self):
        rc = None
        try:
            os.killpg(os.getpgid(self.p.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            out, err = self.p.communicate(timeout=3)
            rc = self.p.returncode
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = self.p.communicate()
            rc = self.p.returncode
        return {"rc": rc, "dur": round(time.time() - self.t0, 3),
                "out": out.decode("utf-8", "replace")[-1500:],
                "err": err.decode("utf-8", "replace")[-1500:]}

    def alive(self):
        return self.p.poll() is None


def census(tag, only_r92=True):
    """Seat scope = r92s* names + anything the filter-chain publishes.

    The filter-chain's default node names are `filter-chain-<pid>-<n>` when the
    caller does not override capture.props/playback.props node.name, and it always
    stamps node.description from our own `node.description=r92s_fc` arg.
    """
    d = L.run(["pw-dump"], wall=6.0)
    try:
        objs = json.loads(d.out)
    except Exception:
        objs = []
    nodes = []
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        p = o.get("info", {}).get("props", {})
        nm = p.get("node.name", "")
        desc = p.get("node.description", "")
        mine = (nm.startswith("r92s") or nm.startswith("filter-chain-")
                or desc == "r92s_fc")
        if only_r92 and not mine:
            continue
        ports = [q["info"]["props"].get("port.name")
                 for q in objs if q.get("type") == "PipeWire:Interface:Port"
                 and q.get("info", {}).get("props", {}).get("node.id") == o["id"]]
        nodes.append({"id": o["id"], "name": nm, "class": p.get("media.class"),
                      "desc": desc, "autoconnect": p.get("node.autoconnect"),
                      "channels": p.get("audio.channels"),
                      "position": p.get("audio.position"),
                      "state": o.get("info", {}).get("state"),
                      "latency": p.get("node.latency"),
                      "rate": p.get("node.rate") or p.get("audio.rate"),
                      "ports": sorted(ports)})
    lk = L.run(["pw-link", "-l"], wall=5.0).out
    return {"tag": tag, "nodes": nodes,
            "r92s_links": [l for l in lk.splitlines() if "r92s" in l],
            "spdif_links": [l for l in lk.splitlines() if "SPDIF" in l],
            "host_default_sink_links": [l for l in lk.splitlines() if "HiFi__SPDIF" in l]}


AUDIO_TOOLS = ("pw-record", "pw-play", "pw-cli", "pw-cat", "pw-dump", "pw-link",
               "pw-mididump", "pw-midiplay", "pw-loopback", "pipewire")


def stray_procs():
    """Only real audio-tool children — never the driving shell/python."""
    out = L.run(["ps", "-eo", "pid,cmd"], wall=5.0).out
    keep = []
    for l in out.splitlines():
        parts = l.strip().split(None, 1)
        if len(parts) != 2:
            continue
        pid, cmd = parts
        if not cmd.startswith(AUDIO_TOOLS):
            continue
        if "r92s" in cmd:
            keep.append(l.strip()[:140])
    return keep


def kill_stray():
    import signal as _sig
    killed = []
    for l in stray_procs():
        pid = int(l.split()[0])
        try:
            os.kill(pid, _sig.SIGKILL)
            killed.append(pid)
        except Exception:
            pass
    return killed


def sink_load(name, extra="channels=1"):
    out = L.run(["pactl", "load-module", "module-null-sink",
                 "sink_name=%s" % name, extra], wall=6.0)
    mid = None
    try:
        mid = int(out.out.strip().split()[-1])
    except Exception:
        pass
    return {"argv": out.argv, "rc": out.rc, "out": out.out.strip(), "id": mid}


def sink_unload(name, expect_id):
    """Index verified against the exact sink_name token before unload."""
    lst = L.run(["pactl", "list", "modules", "short"], wall=6.0).out
    cand = []
    for line in lst.splitlines():
        if "module-null-sink" in line and ("sink_name=%s" % name) in line:
            cand.append(int(line.split()[0]))
    verified = expect_id in cand
    out = L.run(["pactl", "unload-module", str(expect_id)], wall=6.0) if verified else None
    return {"name": name, "expected_id": expect_id, "candidates": cand,
            "verified": verified, "unload_rc": out.rc if out else None,
            "unload_err": out.err.strip() if out else None}


class Pipeline:
    """sinks + filter-chain + hand links, fully seat-local (no autoconnect)."""

    def __init__(self, tag, args_token, log_level="3"):
        self.tag = tag
        self.args = args_token
        self.log = []
        self.sinks = {}
        self.rec = None
        self.player = None
        self.cli = None
        self.fc_module_id = None
        self.wall_t0 = time.time()

    def arm(self, link=True):
        for n in (NS_IN, NS_OUT):
            self.sinks[n] = sink_load(n)
        self.cli = L.PwCli(env={"PIPEWIRE_DEBUG": "3"})
        self.log_off = sum(len(x) for x in self.cli.log)
        out, var = self.cli.load("libpipewire-module-filter-chain", self.args)
        self.fc_module_var = var
        self.load_out = out
        time.sleep(0.5)
        self.link_log = []
        if link:
            for a, b in [(f"{NS_IN}:monitor_MONO", f"{FC_IN}:input_MONO"),
                         (f"{FC_OUT}:output_MONO", f"{NS_OUT}:playback_MONO")]:
                r = L.run(["pw-link", a, b], wall=5.0)
                self.link_log.append({"argv": r.argv, "rc": r.rc, "err": r.err.strip()})
        return self

    def fc_log(self):
        """Module-side log lines only (SPA filter-graph emits to the client log)."""
        txt = "".join(self.cli.log) if self.cli else ""
        keep = []
        for l in txt.splitlines():
            if ("spa.filter-graph" in l or "filter-graph" in l or "convolver" in l
                    or "delay:" in l or "ladspa" in l or "lv2" in l or "sofa" in l
                    or "ebur128" in l or "ffmpeg" in l or "[E]" in l or "[W]" in l):
                keep.append(l.strip()[:300])
        return keep[-80:]

    def start_rec(self, path, wall=14.0):
        self.rec_path = path
        if os.path.exists(path):
            os.unlink(path)
        self.rec = Bg(["pw-record", "--channels", "1", "-P", "node.name=%s" % RECN,
                       "-P", "node.autoconnect=false", path], wall=wall)
        time.sleep(0.6)
        r = L.run(["pw-link", f"{NS_OUT}:monitor_MONO", f"{RECN}:input_MONO"], wall=5.0)
        self.link_log.append({"argv": r.argv, "rc": r.rc, "err": r.err.strip()})
        time.sleep(0.3)
        return r

    def play_file(self, path, wall=8.0):
        p = Bg(["pw-play", "-P", "node.name=%s" % PLAY,
                "-P", "node.autoconnect=false", path], wall=wall)
        time.sleep(0.6)
        r = L.run(["pw-link", f"{PLAY}:output_MONO", f"{NS_IN}:playback_MONO"], wall=5.0)
        self.link_log.append({"argv": r.argv, "rc": r.rc, "err": r.err.strip()})
        t0 = time.time()
        while p.alive() and time.time() - t0 < wall:
            time.sleep(0.1)
        self.player = p
        st = p.stop()
        return st

    def stop_rec(self):
        st = self.rec.stop() if self.rec else None
        time.sleep(0.2)
        return st

    def disarm(self, census_after=True):
        res = {"tag": self.tag, "sinks": self.sinks, "links": self.link_log,
               "fc_module_var": getattr(self, "fc_module_var", None),
               "load_out": getattr(self, "load_out", "")[-900:],
               "fc_log": self.fc_log()}
        if self.player and self.player.alive():
            res["play_stop"] = self.player.stop()
        if self.rec and self.rec.alive():
            res["rec_stop"] = self.rec.stop()
        if self.cli:
            nodes_now = census(self.tag + "-preunload")
            res["nodes_before_unload"] = [n["name"] for n in nodes_now["nodes"]]
            var = getattr(self, "fc_module_var", None)
            if var is not None:
                # verify the module var still exists in this pw-cli session
                check = self.cli.cmd("ls Module")[-1200:]
                res["ls_module"] = [l for l in check.splitlines() if "@module" in l][:20]
                res["unload_out"] = self.cli.cmd("unload-module %d" % var)[-600:]
                time.sleep(0.3)
                res["nodes_after_unload"] = [n["name"] for n in census(self.tag + "-postunload")["nodes"]]
            res["cli_log"] = "".join(self.cli.log)[-2000:]
            self.cli.close()
        time.sleep(0.5)
        if census_after:
            c = census(self.tag + "-exit")
            res["nodes_at_exit"] = [n["name"] for n in c["nodes"]]
            res["spdif_links_at_exit"] = c["spdif_links"]
        res["sink_unload"] = [sink_unload(n, self.sinks[n]["id"]) for n in self.sinks]
        time.sleep(0.2)
        res["stray_procs"] = stray_procs()
        return res


# ------------------------------------------------------------------ stages

def stage_shape(reps):
    """Load-shape census: graph variants, no tone, no links."""
    variants = {
        "empty-graph": fckwargs([]),
        "one-biquad": fckwargs([NODE("bq_lowpass", Freq=1000.0, Q=0.707)]),
        "two-nodes-nolinks": fckwargs([NODE("bq_lowpass", "a", Freq=1000.0, Q=0.707),
                                       NODE("bq_highpass", "b", Freq=200.0, Q=0.707)]),
        "two-nodes-linked": fckwargs([NODE("bq_lowpass", "a", Freq=1000.0, Q=0.707),
                                      NODE("bq_highpass", "b", Freq=200.0, Q=0.707)],
                                     links=["{output=a:Out,input=b:In}"]),
        "stereo-2ch": fckwargs([NODE("bq_lowpass", Freq=1000.0, Q=0.707)], channels=2),
        "media-class-sink": fckwargs([NODE("bq_lowpass", Freq=1000.0, Q=0.707)],
                                     capture_props="node.name=%s,node.autoconnect=false,media.class=Audio/Sink" % FC_IN,
                                     playback_props="node.name=%s,node.autoconnect=false" % FC_OUT),
        "autoconnect-true": fckwargs([NODE("bq_lowpass", Freq=1000.0, Q=0.707)],
                                     capture_props="node.name=%s,node.autoconnect=true" % FC_IN,
                                     playback_props="node.name=%s,node.autoconnect=true" % FC_OUT),
        "bad-label": fckwargs(["{type=builtin,name=x,label=not_a_filter}"]),
        "bq-unknown-freq": fckwargs([NODE("bq_lowpass", Freq=0.0, Q=0.707)]),
        "graph-not-object": "node.description=r92s_fc,filter.graph=42",
    }
    out = {"stage": "shape", "variants": {}}
    for name, tok in variants.items():
        for rep in range(reps):
            p = Pipeline(name, tok)
            p.arm(link=False)
            time.sleep(0.4)
            c = census("%s-r%d" % (name, rep))
            d = p.disarm()
            d["census_live"] = c
            out["variants"].setdefault(name, []).append(d)
            print("shape %-20s r%d nodes=%d links=%d" %
                  (name, rep, len(c["nodes"]), len(c["r92s_links"])))
            if p.cli and p.cli.p.poll() is None:
                pass
    return out


def stage_dsp(reps):
    """Frequency response of the builtin filters via multitone steady state."""
    tone = os.path.join(SCRATCH, "tone.wav")
    L.write_wav(tone, L.multitone(TONE_FREQS, 1.0, rate=RATE, amp=0.2), rate=RATE, ch=1)
    ref = L.read_wav(tone)["x"][0]
    win = 24000
    refmags = L.dft_mags(ref[:win], TONE_FREQS, RATE)

    graphs = {
        "identity": fckwargs([]),
        "copy": fckwargs(["{type=builtin,name=c,label=copy}"]),
        "gain-0.5": fckwargs(["{type=builtin,name=g,label=gain,control={Gain=0.5}}"]),
        "bq_lowpass-1000": fckwargs([NODE("bq_lowpass", Freq=1000.0, Q=0.707)]),
        "bq_highpass-1000": fckwargs([NODE("bq_highpass", Freq=1000.0, Q=0.707)]),
        "bq_peaking-1000-g6": fckwargs([NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=6.0)]),
        "bq_peaking-1000-gm6": fckwargs([NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=-6.0)]),
        "bq_notch-1000": fckwargs([NODE("bq_notch", Freq=1000.0, Q=1.0)]),
        "bq_allpass-1000": fckwargs([NODE("bq_allpass", Freq=1000.0, Q=1.0)]),
        "bq_lowshelf-200-g6": fckwargs([NODE("bq_lowshelf", Freq=200.0, Q=0.707, Gain=6.0)]),
        "bq_highshelf-4000-gm6": fckwargs([NODE("bq_highshelf", Freq=4000.0, Q=0.707, Gain=-6.0)]),
        "bq_bandpass-1000": fckwargs([NODE("bq_bandpass", Freq=1000.0, Q=1.0)]),
        "eq6-chain": fckwargs([NODE("bq_lowshelf", "b1", Freq=200.0, Q=0.707, Gain=6.0),
                               NODE("bq_peaking", "b2", Freq=1000.0, Q=1.0, Gain=-12.0),
                               NODE("bq_highshelf", "b3", Freq=4000.0, Q=0.707, Gain=6.0)],
                              links=["{output=b1:Out,input=b2:In}",
                                     "{output=b2:Out,input=b3:In}"]),
        "param_eq": fckwargs(["{type=builtin,name=pe,label=param_eq,config={filters=[{type=bq_peaking,freq=1000.0,gain=6.0,q=1.0},{type=bq_lowpass,freq=4000.0}]}}"]),
        "mixer-2in": fckwargs(["{type=builtin,name=m,label=mixer,control={Gain1=0.5,Gain2=0.5}}"]),
        "invert": fckwargs(["{type=builtin,name=i,label=invert}"]),
        "delay-10ms": fckwargs(["{type=builtin,name=d,label=delay,config={max-delay=0.05},control={Delay=0.01}}"]),
        "sine-gen": fckwargs(["{type=builtin,name=s,label=sine}"]),
    }
    out = {"stage": "dsp", "ref_mags": refmags, "freqs": TONE_FREQS,
           "stim": {"path": tone, "sha": _sha(tone)}, "graphs": {}}
    for name, tok in graphs.items():
        rows = []
        for rep in range(reps):
            recp = os.path.join(SCRATCH, "rec_%s_r%d.wav" % (name.replace(".", "_"), rep))
            p = Pipeline(name, tok)
            p.arm()
            p.start_rec(recp)
            st = p.play_file(tone)
            rs = p.stop_rec()
            d = p.disarm()
            row = {"rep": rep, "play": st, "rec_stop": rs, "rec_bytes": os.path.getsize(recp) if os.path.exists(recp) else 0}
            if os.path.exists(recp) and row["rec_bytes"] > 1000:
                w = L.read_wav(recp)
                x = w["x"][0]
                # steady-state window: skip 0.6 s of head, take 0.5 s
                skip = int(0.6 * w["rate"])
                seg = x[skip:skip + win] if len(x) >= skip + win else x[-win:]
                mags = L.dft_mags(seg, TONE_FREQS, RATE)
                row["mags"] = mags
                row["gain_db"] = {str(f): round(20 * _log10(max(1e-12, mags[f]) / max(1e-12, refmags[f])), 3)
                                  for f in TONE_FREQS}
                row["rms"] = round((sum(v * v for v in seg) / len(seg)) ** 0.5, 6)
                row["peak"] = round(max(abs(v) for v in seg), 6)
                row["dc"] = round(sum(seg) / len(seg), 8)
                row["rec_frames"] = w["frames"]
            row["teardown"] = {"nodes_after_unload": d.get("nodes_after_unload"),
                               "nodes_at_exit": d.get("nodes_at_exit"),
                               "spdif_at_exit": d.get("spdif_links_at_exit"),
                               "sink_unload": d.get("sink_unload")}
            rows.append(row)
            print("dsp %-24s r%d bytes=%-8d %s" %
                  (name, rep, row["rec_bytes"], row.get("gain_db")))
        out["graphs"][name] = {"args": tok, "rows": rows}
    return out


def stage_ir(reps):
    """Impulse response through the chain: convolver / delay, delta stimulus."""
    delta = os.path.join(SCRATCH, "delta.wav")
    L.delta_wav(delta, taps=[(100, 1.0)], rate=RATE, n=4096)
    two = os.path.join(SCRATCH, "ir_2tap.wav")
    L.delta_wav(two, taps=[(0, 1.0), (64, 0.5)], rate=RATE, n=4096)
    longir = os.path.join(SCRATCH, "ir_delay100.wav")
    L.delta_wav(longir, taps=[(100, 1.0)], rate=RATE, n=8192)
    graphs = {
        "identity": fckwargs([]),
        "copy": fckwargs(["{type=builtin,name=c,label=copy}"]),
        "convolver-2tap": fckwargs(["{type=builtin,name=cv,label=convolver,config={filename=%s,blocksize=1024,tailsize=1024,gain=1.0}}" % two]),
        "convolver-delay100": fckwargs(["{type=builtin,name=cv,label=convolver,config={filename=%s,blocksize=1024,tailsize=1024}}" % longir]),
        "convolver-noconfig": fckwargs(["{type=builtin,name=cv,label=convolver}"]),
        "convolver-missing-file": fckwargs(["{type=builtin,name=cv,label=convolver,config={filename=/nonexistent/r92s_ir.wav}}"]),
        "delay-10ms": fckwargs(["{type=builtin,name=d,label=delay,config={max-delay=0.05},control={Delay=0.01}}"]),
        "delay-noconfig": fckwargs(["{type=builtin,name=d,label=delay}"]),
    }
    out = {"stage": "ir", "stim": {"delta": delta, "two_tap": two, "long": longir}, "graphs": {}}
    for name, tok in graphs.items():
        rows = []
        for rep in range(reps):
            recp = os.path.join(SCRATCH, "ir_%s_r%d.wav" % (name.replace(".", "_"), rep))
            p = Pipeline(name, tok)
            p.arm()
            p.start_rec(recp)
            st = p.play_file(delta)
            rs = p.stop_rec()
            d = p.disarm()
            row = {"rep": rep, "play": st, "rec_bytes": os.path.getsize(recp) if os.path.exists(recp) else 0}
            if os.path.exists(recp) and row["rec_bytes"] > 1000:
                x = L.read_wav(recp)["x"][0]
                nz = [(i, round(v, 6)) for i, v in enumerate(x) if abs(v) > 0.02]
                row["n_nonzero_gt_0.02"] = len(nz)
                row["first_nz"] = nz[0] if nz else None
                row["nonzero_head"] = nz[:24]
                if nz:
                    i0 = nz[0][0]
                    row["window"] = [round(v, 6) for v in x[max(0, i0 - 4):i0 + 140]]
                    pk = sorted(nz, key=lambda t: -abs(t[1]))[:6]
                    row["top_peaks"] = pk
                    if len(pk) >= 2:
                        row["peak_gap_samples"] = pk[1][0] - pk[0][0]
                        row["peak_ratio"] = round(abs(pk[1][1]) / max(1e-9, abs(pk[0][1])), 4)
                row["rms"] = round((sum(v * v for v in x) / max(1, len(x))) ** 0.5, 8)
                row["rec_frames"] = len(x)
            row["teardown"] = {"nodes_after_unload": d.get("nodes_after_unload"),
                               "nodes_at_exit": d.get("nodes_at_exit"),
                               "spdif_at_exit": d.get("spdif_links_at_exit"),
                               "sink_unload": d.get("sink_unload")}
            row["fc_log"] = d.get("fc_log")
            rows.append(row)
            print("ir %-26s r%d bytes=%-8d nz=%-5s first=%s gap=%s" %
                  (name, rep, row["rec_bytes"], row.get("n_nonzero_gt_0.02"),
                   row.get("first_nz"), row.get("peak_gap_samples")))
        out["graphs"][name] = {"args": tok, "rows": rows}
    return out


def _extract_args(path):
    """Pull the args = { ... } object out of a shipped filter-chain conf fragment."""
    txt = open(path).read()
    i = txt.find("args")
    if i < 0:
        return None
    j = txt.find("{", i)
    depth = 0
    for k in range(j, len(txt)):
        if txt[k] == "{":
            depth += 1
        elif txt[k] == "}":
            depth -= 1
            if depth == 0:
                return txt[j:k + 1]
    return None


def stage_configs(reps):
    d = "/usr/share/pipewire/filter-chain"
    files = sorted(f for f in os.listdir(d) if f.endswith(".conf"))
    out = {"stage": "configs", "dir": d, "files": {}}
    for f in files:
        p = os.path.join(d, f)
        body = _extract_args(p)
        rows = []
        for rep in range(reps):
            # rewrite node.names to seat-owned so nothing can collide with a sibling
            tok = body
            for k, v in [("effect_input", "r92s_effect_input"), ("effect_output", "r92s_effect_output"),
                         ("input_lfe", "r92s_input_lfe"), ("output_lfe", "r92s_output_lfe"),
                         ("mix_input", "r92s_mix_input"), ("mix_output", "r92s_mix_output"),
                         ("input.rnnoise", "r92s_input_rnnoise"), ("output.rnnoise", "r92s_output_rnnoise"),
                         ("input.virtual-surround", "r92s_input_vs"),
                         ("output.virtual-surround", "r92s_output_vs"),
                         ("input.demonic", "r92s_input_demonic"), ("output.demonic", "r92s_output_demonic"),
                         ("effect_input.", "r92s_effect_input."), ("effect_output.", "r92s_effect_output."),
                         ("input.duplicate", "r92s_input_dup"), ("output.duplicate", "r92s_output_dup"),
                         ("input.upmix", "r92s_input_upmix"), ("output.upmix", "r92s_output_upmix"),
                         ("input.matrix", "r92s_input_matrix"), ("output.matrix", "r92s_output_matrix")]:
                tok = tok.replace(k, v)
            tok = tok.replace("\n", " ").replace('"', "")
            tok = " ".join(tok.split())
            tok = tok.replace(" ", "")
            p2 = Pipeline("cfg-" + f, tok)
            p2.arm(link=False)
            time.sleep(0.4)
            c = census("cfg-%s-r%d" % (f, rep))
            d2 = p2.disarm()
            nodes = [n["name"] for n in c["nodes"]]
            row = {"rep": rep, "nodes": nodes, "n_nodes": len(nodes),
                   "links": c["r92s_links"], "spdif_links": c["spdif_links"],
                   "fc_log": d2.get("fc_log"), "load_out_tail": d2.get("load_out"),
                   "nodes_after_unload": d2.get("nodes_after_unload"),
                   "nodes_at_exit": d2.get("nodes_at_exit"),
                   "sink_unload": d2.get("sink_unload"),
                   "ports": {n["name"]: n["ports"] for n in c["nodes"]}}
            rows.append(row)
            print("cfg %-34s r%d nodes=%d %s" % (f, rep, len(nodes), nodes))
        out["files"][f] = {"args_raw": body, "rows": rows}
    return out


def stage_absent(reps):
    graphs = {
        "ladspa-missing-so": fckwargs(["{type=ladspa,name=l,plugin=r92s_no_such_plugin,label=x}"]),
        "ladspa-g2reverb": fckwargs(["{type=ladspa,name=l,plugin=g2reverb,label=G2reverb}"]),
        "lv2-missing-uri": fckwargs(["{type=lv2,name=v,plugin=http://example.org/r92s#none,label=x}"]),
        "lv2-spec-uri": fckwargs(["{type=lv2,name=v,plugin=http://lv2plug.in/ns/ext/atom,label=x}"]),
        "sofa-missing": fckwargs(["{type=sofa,name=s,label=x,config={filename=/nonexistent/r92s.sofa}}"]),
        "sofa-noconfig": fckwargs(["{type=sofa,name=s,label=x}"]),
        "ffmpeg-volume": fckwargs(["{type=ffmpeg,name=f,plugin=filtergraph,label=volume=0.5}"]),
        "ebur128": fckwargs(["{type=ebur128,name=e,label=x}"]),
        "unknown-type": fckwargs(["{type=r92s_bogus,name=u,label=x}"]),
        "convolver-noconfig": fckwargs(["type=builtin,name=c,label=convolver"]),
    }
    out = {"stage": "absent", "graphs": {}}
    for name, tok in graphs.items():
        rows = []
        for rep in range(reps):
            p = Pipeline(name, tok)
            p.arm(link=False)
            time.sleep(0.3)
            c = census("absent-%s-r%d" % (name, rep))
            d = p.disarm()
            rows.append({"rep": rep, "nodes": [n["name"] for n in c["nodes"]],
                         "ports": {n["name"]: n["ports"] for n in c["nodes"]},
                         "log": d.get("fc_log"), "load_out": d.get("load_out"),
                         "nodes_at_exit": d.get("nodes_at_exit"),
                         "sink_unload": d.get("sink_unload")})
            print("absent %-22s r%d nodes=%s" % (name, rep, [n["name"] for n in c["nodes"]]))
        out["graphs"][name] = {"args": tok, "rows": rows}
    return out


def stage_rate(reps):
    tone = os.path.join(SCRATCH, "tone44.wav")
    L.write_wav(tone, L.multitone(TONE_FREQS, 1.0, rate=44100, amp=0.2), rate=44100, ch=1)
    tone48 = os.path.join(SCRATCH, "tone.wav")
    graphs = {
        "rate-48000": fckwargs([NODE("bq_lowpass", Freq=1000.0, Q=0.707)], rate=48000),
        "rate-44100": fckwargs([NODE("bq_lowpass", Freq=1000.0, Q=0.707)], rate=44100),
        "rate-96000": fckwargs([NODE("bq_lowpass", Freq=1000.0, Q=0.707)], rate=96000),
    }
    out = {"stage": "rate", "graphs": {}}
    ref48 = L.read_wav(tone48)["x"][0]
    ref44 = L.read_wav(tone)["x"][0]
    win = 24000
    for name, tok in graphs.items():
        rows = []
        for rep in range(reps):
            recp = os.path.join(SCRATCH, "rate_%s_r%d.wav" % (name, rep))
            p = Pipeline(name, tok)
            p.arm()
            p.start_rec(recp)
            st = p.play_file(tone48)
            rs = p.stop_rec()
            d = p.disarm()
            row = {"rep": rep, "play": st, "rec_bytes": os.path.getsize(recp) if os.path.exists(recp) else 0}
            if os.path.exists(recp) and row["rec_bytes"] > 1000:
                w = L.read_wav(recp)
                x = w["x"][0]
                skip = int(0.6 * w["rate"])
                seg = x[skip:skip + win] if len(x) >= skip + win else x[-win:]
                refm = L.dft_mags(ref48[:win], TONE_FREQS, RATE)
                mags = L.dft_mags(seg, TONE_FREQS, RATE)
                row["rate_seen"] = w["rate"]
                row["gain_db"] = {str(f): round(20 * _log10(max(1e-12, mags[f]) / max(1e-12, refm[f])), 3)
                                  for f in TONE_FREQS}
                row["mags"] = mags
            row["teardown"] = {"nodes_at_exit": d.get("nodes_at_exit"),
                               "spdif_at_exit": d.get("spdif_links_at_exit"),
                               "sink_unload": d.get("sink_unload")}
            rows.append(row)
            print("rate %-14s r%d bytes=%-8d %s" % (name, rep, row["rec_bytes"], row.get("gain_db")))
        out["graphs"][name] = {"args": tok, "rows": rows}
    return out


def _sha(p):
    import hashlib
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def _log10(x):
    import math
    return math.log10(x)


STAGES = {"shape": stage_shape, "dsp": stage_dsp, "ir": stage_ir,
          "configs": stage_configs, "absent": stage_absent, "rate": stage_rate}


def main():
    stage = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    t0 = time.time()
    res = STAGES[stage](reps)
    res["reps"] = reps
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    res["final_census"] = census("final")
    path = os.path.join(REC, "%s.json" % stage)
    L.jdump(path, res)
    print("WROTE %s (%.1fs)" % (path, time.time() - t0))
    print("FINAL r92s nodes:", [n["name"] for n in res["final_census"]["nodes"]],
          "spdif links:", len(res["final_census"]["spdif_links"]))
    print("STRAY r92s PROCS:", stray_procs())
    print("r92s modules left:", L.run(["pactl", "list", "modules", "short"], wall=5.0).out.count("r92s"))


if __name__ == "__main__":
    main()
