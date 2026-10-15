#!/usr/bin/env python3
"""r92 scout driver v2 — proven single-driver rig with a pre-chain reference tap.

Topology (all seat-local; the only driver is the seat null sink):
    pw-play r92s_play --(link)--> r92s_in null sink (driver, mono)
    r92s_in:monitor_MONO --(link)--> r92s_fc_in:playback_MONO   (filter-chain in)
    r92s_in:monitor_MONO --(link)--> r92s_ref:input_MONO        (PRE-chain tap)
    r92s_fc_out:output_MONO --(link)--> r92s_rec:input_MONO     (POST-chain tap)
Transfer function = post/pre, so every route gain cancels exactly.

Stages: dsp | ir | configs | absent | clamp
"""
import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib as L
import driver as D

HERE = D.HERE
RUNS, SCRATCH, REC = D.RUNS, D.SCRATCH, D.REC

NS = "r92s_in"
FC_IN, FC_OUT = "r92s_fc_in", "r92s_fc_out"
PLAY, REF, RECN = "r92s_play", "r92s_ref", "r92s_rec"
FREQS = D.TONE_FREQS
RATE = D.RATE
WIN = 24000


def full_args(nodes, **kw):
    """The shipped-config shape: both stream props present (this is what makes the
    streams honour audio.channels/audio.position instead of defaulting to stereo)."""
    kw.setdefault("capture_props",
                  "node.name=%s,node.autoconnect=false,media.class=Audio/Sink" % FC_IN)
    kw.setdefault("playback_props", "node.name=%s,node.autoconnect=false" % FC_OUT)
    return D.fckwargs(nodes, **kw)


def live_r92s():
    d = L.run(["pw-dump"], wall=6.0)
    try:
        objs = json.loads(d.out)
    except Exception:
        objs = []
    names = []
    for o in objs:
        if o.get("type") != "PipeWire:Interface:Node":
            continue
        p = o.get("info", {}).get("props", {})
        nm = p.get("node.name", "")
        if nm.startswith("r92s") or p.get("node.description") == "r92s_fc":
            names.append(nm)
    mods = [l.split()[0] for l in L.run(["pactl", "list", "modules", "short"], wall=6.0).out.splitlines()
            if "r92s" in l]
    return {"nodes": names, "modules": mods, "procs": D.stray_procs()}


def preflight():
    """Clean any residue from an aborted prior run BEFORE arming anything: a
    duplicate seat null sink makes every pw-link name ambiguous."""
    before = live_r92s()
    killed = D.kill_stray()
    for m in before["modules"]:
        L.run(["pactl", "unload-module", m], wall=6.0)
    time.sleep(0.5)
    after = live_r92s()
    return {"before": before, "killed_procs": killed, "after": after,
            "was_clean": not (before["nodes"] or before["modules"] or before["procs"])}


def sweep():
    """Final teardown: unload every remaining seat module, verify, report."""
    before = live_r92s()
    for m in before["modules"]:
        L.run(["pactl", "unload-module", m], wall=6.0)
    time.sleep(0.5)
    after = live_r92s()
    return {"before": before, "after": after,
            "clean": not (after["nodes"] or after["modules"] or after["procs"])}


class Rig:
    def __init__(self, tag, args):
        self.tag = tag
        self.args = args
        self.cleanup = []
        self.link_log = []
        self.pre = live_r92s()

    def arm(self):
        self.sink = D.sink_load(NS)
        self.cli = L.PwCli(env={"PIPEWIRE_DEBUG": "3"}, idle=0.35, hard=2.5)
        out, var = self.cli.load("libpipewire-module-filter-chain", self.args)
        self.load_out, self.fc_var = out, var
        time.sleep(0.6)
        self._link("feed", f"{NS}:monitor_MONO", f"{FC_IN}:playback_MONO")
        return self

    def _link(self, tag, a, b, tries=10):
        """Retry until the ports exist: a stream node publishes its ports a moment
        after the client starts, and pw-link does not wait for them."""
        last = None
        for i in range(tries):
            r = L.run(["pw-link", a, b], wall=4.0)
            last = r
            if r.rc == 0:
                self.link_log.append({"tag": tag, "argv": [a, b], "rc": 0, "tries": i + 1})
                return 0
            if "File exists" in r.err:
                self.link_log.append({"tag": tag, "argv": [a, b], "rc": 0, "tries": i + 1,
                                      "note": "already linked"})
                return 0
            time.sleep(0.25)
        self.link_log.append({"tag": tag, "argv": [a, b], "rc": last.rc,
                              "err": last.err.strip(), "tries": tries})
        return last.rc

    def links_now(self):
        lk = L.run(["pw-link", "-l"], wall=5.0).out
        return [l.strip() for l in lk.splitlines() if "r92s" in l]

    def start_captures(self, ref_path, out_path, wall=14.0):
        for p in (ref_path, out_path):
            if os.path.exists(p):
                os.unlink(p)
        self.ref = D.Bg(["pw-record", "--channels", "1", "-P", "node.name=%s" % REF,
                         "-P", "node.autoconnect=false", ref_path], wall=wall)
        self.rec = D.Bg(["pw-record", "--channels", "1", "-P", "node.name=%s" % RECN,
                         "-P", "node.autoconnect=false", out_path], wall=wall)
        time.sleep(0.6)
        self.ok_ref = self._link("ref-tap", f"{NS}:monitor_MONO", f"{REF}:input_MONO") == 0
        self.ok_rec = self._link("post-tap", f"{FC_OUT}:output_MONO", f"{RECN}:input_MONO") == 0
        time.sleep(0.2)

    def play(self, wav, wall=8.0):
        """--target lets WP bind the stream to the seat sink (one less manual race)."""
        p = D.Bg(["pw-play", "--target", NS, "-P", "node.name=%s" % PLAY, wav], wall=wall)
        time.sleep(0.8)
        got = [l for l in self.links_now() if PLAY in l]
        if not got:
            self._link("stimulus", f"{PLAY}:output_MONO", f"{NS}:playback_MONO")
        else:
            self.link_log.append({"tag": "stimulus-wp", "argv": [PLAY, NS], "rc": 0, "tries": 1})
        t0 = time.time()
        while p.alive() and time.time() - t0 < wall:
            time.sleep(0.1)
        st = p.stop()
        time.sleep(0.3)
        return st

    def stop(self):
        out = {}
        for nm, obj in (("play", getattr(self, "player", None)),
                        ("ref", getattr(self, "ref", None)),
                        ("rec", getattr(self, "rec", None))):
            if obj is not None:
                out[nm] = obj.stop()
        time.sleep(0.3)
        return out

    def disarm(self):
        res = {"tag": self.tag, "args": self.args, "pre": self.pre,
               "sinks": getattr(self, "sink", None), "links": self.link_log,
               "load_out": (self.load_out or "")[-400:], "fc_var": getattr(self, "fc_var", None),
               "fc_log": self.cli_log()}
        try:
            if getattr(self, "fc_var", None) is not None:
                res["unload"] = self.cli.cmd("unload-module %d" % self.fc_var)[-200:]
            res["cli_close_ok"] = True
        except Exception as e:
            res["cli_error"] = repr(e)
            try:
                os.killpg(os.getpgid(self.cli.p.pid), signal.SIGKILL)
            except Exception:
                pass
        try:
            self.cli.close()
        except Exception:
            pass
        time.sleep(0.5)
        res["after_exit_nodes"] = [n["name"] for n in D.census(self.tag + "-exit")["nodes"]]
        res["sink_unload"] = D.sink_unload(NS, self.sink["id"]) if getattr(self, "sink", None) else None
        time.sleep(0.3)
        res["live"] = live_r92s()
        return res

    def cli_log(self):
        txt = "".join(self.cli.log) if getattr(self, "cli", None) else ""
        keep = []
        for l in txt.splitlines():
            if ("[E]" in l or "[W]" in l or "spa.filter-graph" in l
                    or "convolver" in l or "delay" in l):
                keep.append(l.strip()[:280])
        return keep[-60:]


def best_window(x, win=WIN, step=2400):
    """Window fully inside the steady tone: max-RMS 0.5 s slice (the tone starts
    late in the recording, so a fixed offset silently measures the prefill)."""
    if len(x) <= win:
        return x
    best, bi = -1.0, 0
    for i in range(0, len(x) - win + 1, step):
        seg = x[i:i + win]
        r = sum(v * v for v in seg)
        if r > best:
            best, bi = r, i
    return x[bi:bi + win], bi


def valid_pair(an):
    return (an.get("ref_bytes", 0) > 1000 and an.get("out_bytes", 0) > 1000
            and max(an.get("ref_mags", {}).values() or [0]) > 1e-6
            and max(an.get("out_mags", {}).values() or [0]) > 1e-6)


def run_leg(name, tok, kind, rep, tag="d"):
    """One bounded leg with one retry when the capture taps came back empty."""
    for attempt in range(2):
        rp = os.path.join(SCRATCH, "%s_ref_%s_%d_%d.wav" % (tag, name, rep, attempt))
        op = os.path.join(SCRATCH, "%s_out_%s_%d_%d.wav" % (tag, name, rep, attempt))
        rig = Rig(name, tok).arm()
        rig.start_captures(rp, op)
        play = rig.play(os.path.join(SCRATCH, "delta.wav") if kind == "ir"
                        else os.path.join(SCRATCH, "tone.wav"))
        stops = rig.stop()
        an = analyze_ir(rp, op) if kind == "ir" else analyze_pair(rp, op)
        d = rig.disarm()
        row = {"rep": rep, "attempt": attempt, "analysis": an, "play": play, "stops": stops,
               "links": d.get("links"), "after_exit": d.get("after_exit_nodes"),
               "sink_unload": d.get("sink_unload"), "live": d.get("live"), "fc_log": d.get("fc_log")}
        if kind == "ir":
            ok = an.get("out_bytes", 0) > 1000 and (an.get("n_gt_0.02") or 0) > 0
        else:
            ok = valid_pair(an)
        row["valid"] = bool(ok)
        if ok:
            return row
        time.sleep(0.4)
    return row


def analyze_pair(ref_path, out_path):
    if not (os.path.exists(ref_path) and os.path.exists(out_path)):
        return {"ref_bytes": 0, "out_bytes": 0}
    rb, ob = os.path.getsize(ref_path), os.path.getsize(out_path)
    r = {"ref_bytes": rb, "out_bytes": ob}
    if rb < 1000 or ob < 1000:
        return r
    wr = L.read_wav(ref_path)
    wo = L.read_wav(out_path)
    xr, xo = wr["x"][0], wo["x"][0]
    r["ref_frames"], r["out_frames"] = wr["frames"], wo["frames"]
    sr, offr = best_window(xr)
    so, offo = best_window(xo)
    r["win_offsets"] = [offr, offo]
    mr = L.dft_mags(sr, FREQS, RATE)
    mo = L.dft_mags(so, FREQS, RATE)
    r["ref_mags"], r["out_mags"] = mr, mo
    r["gain_db"] = {str(f): round(20 * L.math.log10(max(1e-15, mo[f]) / max(1e-15, mr[f])), 3)
                    for f in FREQS}
    r["ref_peak"] = round(max(abs(v) for v in sr), 6)
    r["out_peak"] = round(max(abs(v) for v in so), 6)
    r["out_rms"] = round((sum(v * v for v in so) / len(so)) ** 0.5, 8)
    return r


def analyze_ir(ref_path, out_path):
    if not (os.path.exists(ref_path) and os.path.exists(out_path)):
        return {}
    r = {"ref_bytes": os.path.getsize(ref_path), "out_bytes": os.path.getsize(out_path)}
    if r["ref_bytes"] < 1000 or r["out_bytes"] < 1000:
        return r
    xo = L.read_wav(out_path)["x"][0]
    nz = [(i, round(v, 7)) for i, v in enumerate(xo) if abs(v) > 0.02]
    r["n_gt_0.02"] = len(nz)
    r["first_nz"] = nz[0] if nz else None
    r["head"] = nz[:20]
    if nz:
        i0 = nz[0][0]
        r["window"] = [round(v, 7) for v in xo[max(0, i0 - 3):i0 + 130]]
        pk = sorted(nz, key=lambda t: -abs(t[1]))[:8]
        r["top_peaks"] = pk
        if len(pk) >= 2:
            r["peak_gap"] = pk[1][0] - pk[0][0]
            r["peak_ratio"] = round(abs(pk[1][1]) / max(1e-12, abs(pk[0][1])), 5)
        r["max_abs"] = round(max(abs(v) for v in xo), 7)
    r["rms"] = round((sum(v * v for v in xo) / max(1, len(xo))) ** 0.5, 9)
    return r


# ------------------------------------------------------------------- stages

def stage_dsp(reps):
    tone = os.path.join(SCRATCH, "tone.wav")
    L.write_wav(tone, L.multitone(FREQS, 1.2, rate=RATE, amp=0.2), rate=RATE, ch=1)
    graphs = {
        "identity": full_args([]),
        "copy": full_args(["{type=builtin,name=c,label=copy}"]),
        "gain-0.5": full_args(["{type=builtin,name=g,label=gain,control={Gain=0.5}}"]),
        "gain-0.25": full_args(["{type=builtin,name=g,label=gain,control={Gain=0.25}}"]),
        "bq_lowpass-1000": full_args([D.NODE("bq_lowpass", Freq=1000.0, Q=0.707)]),
        "bq_highpass-1000": full_args([D.NODE("bq_highpass", Freq=1000.0, Q=0.707)]),
        "bq_peaking-1000-g6": full_args([D.NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=6.0)]),
        "bq_peaking-1000-gm6": full_args([D.NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=-6.0)]),
        "bq_notch-1000": full_args([D.NODE("bq_notch", Freq=1000.0, Q=1.0)]),
        "bq_allpass-1000": full_args([D.NODE("bq_allpass", Freq=1000.0, Q=1.0)]),
        "bq_lowshelf-200-g6": full_args([D.NODE("bq_lowshelf", Freq=200.0, Q=0.707, Gain=6.0)]),
        "bq_highshelf-4000-gm6": full_args([D.NODE("bq_highshelf", Freq=4000.0, Q=0.707, Gain=-6.0)]),
        "bq_bandpass-1000": full_args([D.NODE("bq_bandpass", Freq=1000.0, Q=1.0)]),
        "eq3-chain": full_args([D.NODE("bq_lowshelf", "b1", Freq=200.0, Q=0.707, Gain=6.0),
                                 D.NODE("bq_peaking", "b2", Freq=1000.0, Q=1.0, Gain=-12.0),
                                 D.NODE("bq_highshelf", "b3", Freq=4000.0, Q=0.707, Gain=6.0)],
                                links=['{output=b1:Out,input=b2:In}',
                                       '{output=b2:Out,input=b3:In}']),
        "param_eq": full_args(["{type=builtin,name=pe,label=param_eq,config={filters=[{type=bq_peaking,freq=1000.0,gain=6.0,q=1.0}]}}"]),
        "invert": full_args(["{type=builtin,name=i,label=invert}"]),
        "delay-10ms": full_args(["{type=builtin,name=d,label=delay,config={max-delay=0.05},control={Delay=0.01}}"]),
    }
    out = {"stage": "dsp", "freqs": FREQS, "graphs": {}}
    for name, tok in graphs.items():
        rows = []
        for rep in range(reps):
            row = run_leg(name, tok, "dsp", rep, tag="d")
            an = row["analysis"]
            rows.append(row)
            print("dsp %-24s r%d a%d valid=%-5s ref=%-7d out=%-7d %s" %
                  (name, rep, row["attempt"], row["valid"], an.get("ref_bytes", 0),
                   an.get("out_bytes", 0), an.get("gain_db")))
        out["graphs"][name] = {"args": tok, "rows": rows}
    return out


def stage_ir(reps):
    delta = os.path.join(SCRATCH, "delta.wav")
    L.delta_wav(delta, taps=[(100, 1.0)], rate=RATE, n=4096)
    two = os.path.join(SCRATCH, "ir_2tap.wav")
    L.delta_wav(two, taps=[(0, 1.0), (64, 0.5)], rate=RATE, n=4096)
    dl = os.path.join(SCRATCH, "ir_d100.wav")
    L.delta_wav(dl, taps=[(100, 1.0)], rate=RATE, n=8192)
    graphs = {
        "identity": full_args([]),
        "copy": full_args(["{type=builtin,name=c,label=copy}"]),
        "convolver-2tap": full_args(["{type=builtin,name=cv,label=convolver,config={filename=%s,blocksize=1024,tailsize=1024,gain=1.0}}" % two]),
        "convolver-delta100": full_args(["{type=builtin,name=cv,label=convolver,config={filename=%s,blocksize=1024,tailsize=1024}}" % dl]),
        "convolver-2tap-g0.5": full_args(["{type=builtin,name=cv,label=convolver,config={filename=%s,blocksize=1024,tailsize=1024,gain=0.5}}" % two]),
        "convolver-noconfig": full_args(["{type=builtin,name=cv,label=convolver}"]),
        "convolver-missing": full_args(["{type=builtin,name=cv,label=convolver,config={filename=/nonexistent/r92s_ir.wav}}"]),
        "delay-10ms": full_args(["{type=builtin,name=d,label=delay,config={max-delay=0.05},control={Delay=0.01}}"]),
        "delay-noconfig": full_args(["{type=builtin,name=d,label=delay}"]),
    }
    out = {"stage": "ir", "stim": {"delta": delta, "two": two, "d100": dl}, "graphs": {}}
    for name, tok in graphs.items():
        rows = []
        for rep in range(reps):
            row = run_leg(name, tok, "ir", rep, tag="i")
            an = row["analysis"]
            rows.append(row)
            print("ir %-24s r%d a%d valid=%-5s out=%-7d nz=%-5s gap=%-6s ratio=%s first=%s" %
                  (name, rep, row["attempt"], row["valid"], an.get("out_bytes", 0),
                   an.get("n_gt_0.02"), an.get("peak_gap"), an.get("peak_ratio"),
                   an.get("first_nz")))
        out["graphs"][name] = {"args": tok, "rows": rows}
    return out


def norm_args(txt):
    """Shipped config text -> one whitespace-free pw-cli args token.

    The module-args grammar is PipeWire's properties parser: members may be
    separated by whitespace or ',', but the token that reaches `pw-cli
    load-module` must not contain whitespace (it is one argv word). So:
      * protect quoted strings (their spaces are content, not separators)
      * kill whitespace around '=' and inside the brackets
      * turn every other whitespace run into ','
    Dropping whitespace wholesale merges adjacent members
    (`type = builtin freq = 1000` -> `type=builtinfreq=1000`) and is exactly
    the `Mismatched bracket` failure the first pass produced.
    """
    import re
    # strip '#' comments to end of line (outside quotes) — the properties
    # parser treats '#' as a comment start, and after whitespace folding there
    # is only one line, so an unstripped comment would swallow the whole token.
    lines = []
    for ln in txt.splitlines():
        q = re.split(r'("[^"]*")', ln)
        for i in range(0, len(q), 2):
            if "#" in q[i]:
                q[i] = q[i][:q[i].index("#")]
        lines.append("".join(q))
    txt = "\n".join(lines)
    parts = re.split(r'("[^"]*")', txt)
    for i in range(1, len(parts), 2):
        parts[i] = parts[i].replace(" ", "\x00")
    t = " ".join("".join(parts).replace("\n", " ").split())
    t = re.sub(r"\s*=\s*", "=", t)
    t = re.sub(r"([\[{])\s+", r"\1", t)
    t = re.sub(r"\s+([\]},])", r"\1", t)
    t = re.sub(r",\s+", ",", t)
    t = re.sub(r"\s+", ",", t)
    return t.replace("\x00", " ").strip()


def stage_configs(reps):
    d = "/usr/share/pipewire/filter-chain"
    out = {"stage": "configs", "dir": d, "files": {}}
    for f in sorted(x for x in os.listdir(d) if x.endswith(".conf")):
        body = D._extract_args(os.path.join(d, f))
        rows = []
        for rep in range(reps):
            tok = body
            tok = tok.replace("\n", " ")
            for k in ("effect_input.", "effect_output.", "input_lfe", "output_lfe",
                      "mix_input", "mix_output", "input.rnnoise", "output.rnnoise",
                      "input.virtual-surround", "output.virtual-surround",
                      "input.demonic", "output.demonic", "input.duplicate",
                      "output.duplicate", "input.upmix", "output.upmix",
                      "input.matrix", "output.matrix", "input.hesuvi", "output.hesuvi",
                      "input.dolby", "output.dolby"):
                tok = tok.replace(k, "r92s_" + k.replace(".", "_"))
            tok = norm_args(tok)
            rig = Rig("cfg-" + f, tok)
            rig.arm()
            time.sleep(0.5)
            c = D.census("cfg-%s-%d" % (f, rep))
            fc = [n for n in c["nodes"] if "r92s_fc" in n["name"] or n["name"].startswith("r92s_")
                  and n["name"] != NS]
            d2 = rig.disarm()
            rows.append({"rep": rep, "fc_nodes": [{"name": n["name"], "class": n["class"],
                                                   "ports": n["ports"], "state": n["state"],
                                                   "ch": n["channels"]} for n in fc],
                         "n_fc": len(fc), "links": c["r92s_links"],
                         "fc_log": d2.get("fc_log"), "live": d2.get("live")})
            print("cfg %-34s r%d fc_nodes=%d %s" %
                  (f, rep, len(fc), [n["name"] for n in fc]))
        out["files"][f] = {"args_raw": body, "rows": rows}
    return out


def stage_absent(reps):
    graphs = {
        "ladspa-missing-so": full_args(["{type=ladspa,name=l,plugin=r92s_no_such_plugin,label=x}"]),
        "ladspa-g2reverb": full_args(["{type=ladspa,name=l,plugin=g2reverb,label=G2reverb}"]),
        "lv2-missing-uri": full_args(["{type=lv2,name=v,plugin=http://example.org/r92s#none,label=x}"]),
        "lv2-spec-uri": full_args(["{type=lv2,name=v,plugin=http://lv2plug.in/ns/ext/atom,label=x}"]),
        "sofa-missing": full_args(["{type=sofa,name=s,label=x,config={filename=/nonexistent/r92s.sofa}}"]),
        "sofa-noconfig": full_args(["{type=sofa,name=s,label=x}"]),
        "ffmpeg-volume": full_args(["{type=ffmpeg,name=f,plugin=filtergraph,label=volume=0.5}"]),
        "ebur128": full_args(["{type=ebur128,name=e,label=x}"]),
        "unknown-type": full_args(["{type=r92s_bogus,name=u,label=x}"]),
        "bad-label": full_args(["{type=builtin,name=x,label=not_a_filter}"]),
    }
    out = {"stage": "absent", "graphs": {}}
    for name, tok in graphs.items():
        rows = []
        for rep in range(reps):
            rig = Rig(name, tok)
            rig.arm()
            time.sleep(0.5)
            c = D.census("abs-%s-%d" % (name, rep))
            d = rig.disarm()
            rows.append({"rep": rep,
                         "fc_nodes": [{"name": n["name"], "class": n["class"], "ports": n["ports"]}
                                      for n in c["nodes"] if n["name"] != NS],
                         "fc_log": d.get("fc_log"), "load_out": d.get("load_out"),
                         "live": d.get("live")})
            print("absent %-20s r%d nodes=%s" %
                  (name, rep, [n["name"] for n in c["nodes"] if n["name"] != NS]))
        out["graphs"][name] = {"args": tok, "rows": rows}
    return out


def stage_clamp(reps):
    """Control-value clamp law + graph-rate sensitivity."""
    tone = os.path.join(SCRATCH, "tone.wav")
    graphs = {
        "bq_lowpass-Freq0": full_args([D.NODE("bq_lowpass", Freq=0.0, Q=0.707)]),
        "bq_lowpass-Freq99999": full_args([D.NODE("bq_lowpass", Freq=99999.0, Q=0.707)]),
        "bq_lowpass-Freq-neg": full_args([D.NODE("bq_lowpass", Freq=-1000.0, Q=0.707)]),
        "bq_lowpass-Q0": full_args([D.NODE("bq_lowpass", Freq=1000.0, Q=0.0)]),
        "bq_peaking-gain100": full_args([D.NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=100.0)]),
        "bq_peaking-gainneg200": full_args([D.NODE("bq_peaking", Freq=1000.0, Q=1.0, Gain=-200.0)]),
        "gain-2.0": full_args(["{type=builtin,name=g,label=gain,control={Gain=2.0}}"]),
        "gain-0": full_args(["{type=builtin,name=g,label=gain,control={Gain=0.0}}"]),
        "mixer-1in-gain0.5": full_args(["{type=builtin,name=m,label=mixer,control={Gain1=0.5}}"]),
        "unknown-control": full_args([D.NODE("bq_lowpass", Freq=1000.0, Q=0.707, Bogus=3.0)]),
    }
    out = {"stage": "clamp", "graphs": {}}
    for name, tok in graphs.items():
        rows = []
        for rep in range(reps):
            row = run_leg(name, tok, "dsp", rep, tag="c")
            an = row["analysis"]
            rows.append(row)
            print("clamp %-22s r%d a%d valid=%-5s out=%-7d %s" %
                  (name, rep, row["attempt"], row["valid"], an.get("out_bytes", 0),
                   an.get("gain_db")))
        out["graphs"][name] = {"args": tok, "rows": rows}
    return out


LABELS = ["bq_lowpass", "bq_highpass", "bq_bandpass", "bq_lowshelf", "bq_highshelf",
          "bq_peaking", "bq_notch", "bq_allpass", "bq_raw", "copy", "invert", "mixer",
          "gain", "mult", "clamp", "dcblock", "linear", "recip", "sine", "convolver",
          "delay", "param_eq", "noisegate", "nop", "passthrough", "sum", "avg", "max",
          "min", "abs", "exp", "log"]


def stage_labels(reps):
    """Measured builtin-label inventory: strings in the .so are not descriptors."""
    out = {"stage": "labels", "labels": {}}
    for lab in LABELS:
        rows = []
        for rep in range(reps):
            tok = "node.description=r92s_lab,filter.graph={nodes=[{type=builtin,name=n0,label=%s}]},audio.channels=1,audio.position=[MONO]" % lab
            one = L.run(["pw-cli"], wall=6.0, stdin_data=(
                "load-module libpipewire-module-filter-chain " + tok + "\nquit\n").encode())
            var = 1 if "@module:" in one.out else None
            lo = one.out
            txt = lo
            keep = [l.strip()[:200] for l in txt.splitlines()
                    if "spa.filter-graph" in l and ("descriptor_load" in l or "loaded n_input" in l
                                                    or "cannot create" in l or "impl_init" in l
                                                    or "using port" in l)]
            ok = var is not None and not any("cannot create label" in l or "can't load graph" in l for l in keep)
            ports = [l for l in keep if "using port" in l]
            n_in = n_out = n_ctl = None
            for l in keep:
                if "loaded n_input" in l:
                    t = l.split("loaded ")[-1]
                    for kv in t.split():
                        if kv.startswith("n_input:"):
                            n_in = kv.split(":")[1]
                        if kv.startswith("n_output:"):
                            n_out = kv.split(":")[1]
                        if kv.startswith("n_control:"):
                            n_ctl = kv.split(":")[1]
            rows.append({"rep": rep, "loaded": ok, "var": var, "n_in": n_in, "n_out": n_out,
                         "n_ctl": n_ctl, "ports": ports, "log": keep})
            time.sleep(0.1)
        out["labels"][lab] = rows
        print("label %-14s loaded=%s n_in=%s n_out=%s n_ctl=%s" %
              (lab, [r["loaded"] for r in rows], rows[0]["n_in"], rows[0]["n_out"], rows[0]["n_ctl"]))
    return out


def stage_links(reps):
    """The links=[...] grammar: does a quoted 'node:port' survive pw-cli -> spa-json?"""
    variants = {
        "unquoted-colon": "links=[{output=b1:Out,input=b2:In}]",
        "quoted-colon": 'links=[{output="b1:Out",input="b2:In"}]',
        "quoted-space-sep": 'links=[{output="b1:Out" input="b2:In"}]',
        "brace-only": "links=[{output=b1,input=b2}]",
        "links-omitted": "",
    }
    out = {"stage": "links", "variants": {}}
    for name, lk in variants.items():
        rows = []
        for rep in range(reps):
            tok = ("node.description=r92s_lk,filter.graph={nodes=["
                   "{type=builtin,name=b1,label=bq_lowpass,control={Freq=1000.0,Q=0.707}},"
                   "{type=builtin,name=b2,label=bq_highpass,control={Freq=200.0,Q=0.707}}]"
                   + ("," + lk if lk else "") + "},audio.channels=1,audio.position=[MONO]")
            one = L.run(["pw-cli"], wall=6.0, stdin_data=(
                "load-module libpipewire-module-filter-chain " + tok + "\nquit\n").encode())
            var = 1 if "@module:" in one.out else None
            lo = one.out
            txt = lo
            keep = [l.strip()[:220] for l in txt.splitlines()
                    if "[E]" in l or "[W]" in l or "spa.filter-graph" in l]
            rows.append({"rep": rep, "loaded": var is not None, "var": var, "log": keep[-8:]})
            time.sleep(0.1)
        out["variants"][name] = {"args": lk, "rows": rows}
        print("links %-18s loaded=%s" % (name, [r["loaded"] for r in rows]))
    return out


STAGES = {"dsp": stage_dsp, "labels": stage_labels, "links": stage_links, "ir": stage_ir, "configs": stage_configs,
          "absent": stage_absent, "clamp": stage_clamp}


def main():
    stage = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    t0 = time.time()
    pf = preflight()
    pre = live_r92s()
    res = {"stage": stage, "reps": reps, "preflight": pf, "precondition": pre,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    res["data"] = STAGES[stage](reps)
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["sweep"] = sweep()
    res["final"] = live_r92s()
    path = os.path.join(REC, "v2_%s.json" % stage)
    L.jdump(path, res)
    print("WROTE %s (%.1fs)" % (path, time.time() - t0))
    print("SWEEP clean:", res["sweep"]["clean"], "final:", res["final"])


if __name__ == "__main__":
    main()
