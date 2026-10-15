#!/usr/bin/env python3
"""r93 scout driver — ebur128 (SPA filter-graph loudness node) measured hard.

Stages (argv[1]), reps (argv[2], default 3):
  portmap  7 input ports x {Momentary,Global}  — channel-map / weight law
  amp      amplitude ladder vs own BS.1770 reference
  freq     K-weighting transfer (40/100/1k/4k/10k)
  stereo   FL+FR / FL+tone FR+silence / mono FL / mono FR
  modes    notify-only coupling (which modes init) + passthrough witness
  window   max-window config matrix (Window LUFS)
  history  max-history eviction (Global after silence)
  peaks    Peak / True Peak per input port (index bug)
  lufs2gain  LUFS->gain law + audio-domain application
  edge     config error classes + two-state graph
  refflat  ffmpeg cross-witness + own reference over captured pre-tap

Seat-owned names r93s_*; every child triple-bounded (wall + byte cap +
start_new_session/killpg + RLIMIT_CORE=0). Index-verified unloads only.
"""
import json
import math
import os
import re
import select
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pwlib93 as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(HERE, "receipts")
SCRATCH = os.path.join(HERE, "scratch")
RUNS = os.path.join(HERE, "runs")
for d in (REC, SCRATCH, RUNS):
    os.makedirs(d, exist_ok=True)

NS = "r93s_in"
FC_IN, FC_OUT = "r93s_fc_in", "r93s_fc_out"
REF, RECN = "r93s_ref", "r93s_rec"
TONE = os.path.join(SCRATCH, "r93s_tone.wav")

CTRL_RE = re.compile(r"\[I\]\[(\d\d:\d\d:\d\d\.\d+)\]\[[^\]]*\]\s+control:\s*(-?[\d.]+|-?nan|-?inf)")
TS_RE = re.compile(r"\[I\]\[(\d\d):(\d\d):(\d\d)\.(\d+)\]")


def ts_seconds(line):
    m = TS_RE.search(line)
    if not m:
        return None
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1e6


# ------------------------------------------------------------------ graph args

def NODE(label, name="x", cfg=None, ctl=None, type_="builtin"):
    s = "type=%s,name=%s,label=%s" % (type_, name, label)
    if cfg:
        s += ",config={%s}" % cfg
    if ctl:
        parts = []
        for kv in ctl.split(","):
            k, _, v = kv.partition("=")
            parts.append(("%s=%s" % (k if k.startswith('"') else (q(k) if " " in k else k), v)))
        s += ",control={%s}" % ",".join(parts)
    return "{%s}" % s


def EBU(name="e", cfg=None, ctl=None):
    return NODE("ebur128", name, cfg=cfg, ctl=ctl, type_="ebur128")


def mkargs(nodes, links, inputs, outputs, ch=1, position="[MONO]"):
    return (
        "node.description=r93s_fc,"
        "filter.graph={nodes=[%s],links=[%s],inputs=[%s],outputs=[%s]},"
        "audio.channels=%d,audio.position=%s,"
        "capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},"
        "playback.props={node.name=%s,node.autoconnect=false}"
        % (",".join(nodes), ",".join(links), ",".join('"%s"' % i for i in inputs),
           ",".join('"%s"' % o for o in outputs), ch, position, FC_IN, FC_OUT)
    )


def q(p):
    return '"%s"' % p


def link_spec(outp, inp):
    return "{output=%s,input=%s}" % (q(outp), q(inp))


# ------------------------------------------------------------------------ rig

class Rig:
    def __init__(self, tag, args, ch=1, capture_ref=False, capture_post=False, stim=None,
                 dur=3.5, read_extra=1.4):
        self.tag = tag
        self.args = args
        self.ch = ch
        self.capture_ref = capture_ref
        self.capture_post = capture_post
        self.stim = stim
        self.dur = dur
        self.read_extra = read_extra

    def link(self, a, b, tries=12):
        last = None
        for i in range(tries):
            r = L.run(["pw-link", a, b], wall=4.0)
            last = r
            if r.rc == 0 or "File exists" in r.err:
                return {"ok": True, "tries": i + 1}
            time.sleep(0.25)
        return {"ok": False, "rc": last.rc, "err": last.err.strip(), "tries": tries}

    def run(self):
        row = {"tag": self.tag, "args": self.args}
        sink = L.run(["pactl", "load-module", "module-null-sink", "sink_name=%s" % NS,
                      "channels=%d" % self.ch], wall=6.0)
        row["sink"] = sink.out.strip()
        time.sleep(0.3)
        cli = L.PwCli(env={"PIPEWIRE_DEBUG": "3"}, idle=0.4, hard=5.0)
        load_out, var = cli.load("libpipewire-module-filter-chain", self.args)
        row["fc_var"] = var
        row["load_ok"] = var is not None
        row["load_tail"] = load_out[-1200:]
        row["load_errs"] = [l.strip()[:220] for l in load_out.splitlines()
                            if "[E]" in l or "[W]" in l]
        time.sleep(0.8)
        if var is None:
            cli.close()
            if sink.out.strip().isdigit():
                L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)
            row["valid"] = False
            return row
        # feed links
        feeds = []
        if self.ch == 1:
            feeds.append(self.link("%s:monitor_MONO" % NS, "%s:playback_MONO" % FC_IN))
        else:
            feeds.append(self.link("%s:monitor_FL" % NS, "%s:playback_FL" % FC_IN))
            feeds.append(self.link("%s:monitor_FR" % NS, "%s:playback_FR" % FC_IN))
        row["feeds"] = feeds
        # capture taps
        refp = os.path.join(SCRATCH, "%s_ref.wav" % self.tag)
        postp = os.path.join(SCRATCH, "%s_post.wav" % self.tag)
        cap = []
        if self.capture_ref:
            if os.path.exists(refp):
                os.unlink(refp)
            cap.append(("ref", L.Bg(["pw-record", "--format", "f32", "--channels", "1",
                                     "-P", "node.name=%s" % REF,
                                     "-P", "node.autoconnect=false", refp],
                                    wall=self.dur + 5.0)))
        if self.capture_post:
            if os.path.exists(postp):
                os.unlink(postp)
            cap.append(("post", L.Bg(["pw-record", "--format", "f32", "--channels", "1",
                                      "-P", "node.name=%s" % RECN,
                                      "-P", "node.autoconnect=false", postp],
                                     wall=self.dur + 5.0)))
        time.sleep(0.5)
        for nm, _ in cap:
            tgt = REF if nm == "ref" else RECN
            row["%s_link" % nm] = self.link("%s:monitor_MONO" % NS if nm == "ref"
                                            else "%s:output_MONO" % FC_OUT,
                                            "%s:input_MONO" % tgt)
        # play + read log
        play = None
        if self.stim:
            play = L.Bg(["pw-play", "--target", NS, self.stim], wall=self.dur + 8.0)
        buf = b""
        t0 = time.time()
        hard = self.dur + self.read_extra + 1.5
        while time.time() - t0 < hard:
            r, _, _ = select.select([cli.p.stdout], [], [], 0.2)
            if r:
                chunk = os.read(cli.p.stdout.fileno(), 262144)
                if not chunk:
                    break
                buf += chunk
                if len(buf) > 4 << 20:
                    break
        row["log_bytes"] = len(buf)
        txt = buf.decode("utf-8", "replace")
        row["control"] = parse_series(txt)
        row["log_sample"] = [l.strip()[:160] for l in txt.splitlines() if "control:" in l][:3]
        row["log_tail"] = txt[-600:]
        row["log_warnerr"] = [l.strip()[:240] for l in txt.splitlines()
                              if "[E]" in l or "[W]" in l][:40]
        if play is not None:
            row["play"] = play.stop()
        stops = {}
        for nm, obj in cap:
            stops[nm] = obj.stop()
        row["captures"] = stops
        if os.path.exists(refp):
            row["ref_path"] = refp
        if os.path.exists(postp):
            row["post_path"] = postp
        # teardown
        cli.cmd("unload-module %d" % var)
        cli.close()
        time.sleep(0.4)
        if sink.out.strip().isdigit():
            L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)
        time.sleep(0.3)
        row["valid"] = True
        return row


def parse_series(txt):
    out = []
    for m in CTRL_RE.finditer(txt):
        v = m.group(2)
        if v == "nan":
            val = float("nan")
        elif v == "inf":
            val = float("inf")
        elif v == "-inf":
            val = float("-inf")
        else:
            val = float(v)
        out.append((ts_seconds(m.group(0)), val))
    if out and out[0][0] is not None:
        t0 = out[0][0]
        out = [(round(t - t0, 4), v) for t, v in out]
    return out


def stats(series):
    """Plateau = median of the longest run of consecutive near-equal finite
    values (the steady tone plateau); tail decays are excluded."""
    vals = [v for _, v in series]
    st = {"n": len(vals), "n_nan": sum(1 for v in vals if math.isnan(v)),
          "n_inf": sum(1 for v in vals if v == float("-inf")),
          "n_finite": sum(1 for v in vals if math.isfinite(v))}
    groups = []
    cur = []
    for i, v in enumerate(vals):
        if math.isfinite(v):
            if cur and abs(v - cur[-1][1]) > 0.05:
                groups.append(cur)
                cur = []
            cur.append((i, v))
        else:
            if cur:
                groups.append(cur)
                cur = []
    if cur:
        groups.append(cur)
    if groups:
        g = max(groups, key=len)
        gv = sorted(v for _, v in g)
        med = gv[len(gv) // 2]
        st["plateau"] = round(med, 6)
        st["plateau_n"] = len(g)
        st["plateau_t0"] = round(series[g[0][0]][0], 3)
        st["plateau_t1"] = round(series[g[-1][0]][0], 3)
        st["plateau_span"] = round(st["plateau_t1"] - st["plateau_t0"], 3)
        finite = [v for v in vals if math.isfinite(v)]
        st["max_finite"] = round(max(finite), 6)
        st["last_finite"] = round(finite[-1], 6)
        idx = next((i for i, v in enumerate(vals)
                    if math.isfinite(v) and abs(v - med) <= 0.1), None)
        st["conv_idx"] = idx
        st["conv_s"] = round(idx * 1024.0 / 48000.0, 3) if idx is not None else None
    st["head"] = [round(v, 4) if math.isfinite(v) else str(v) for _, v in series[:8]]
    st["tail"] = [round(v, 4) if math.isfinite(v) else str(v) for _, v in series[-6:]]
    return st


# ------------------------------------------------------------------- analysis

def capture_stats(path):
    if not path or not os.path.exists(path):
        return {}
    w = L.read_wav_any(path)
    x = w["x"][0]
    n = len(x)
    rms = math.sqrt(sum(v * v for v in x) / max(1, n))
    pk = max((abs(v) for v in x), default=0.0)
    nz = sum(1 for v in x if v != 0.0)
    return {"frames": n, "rms": round(rms, 8), "peak": round(pk, 8),
            "nz": nz, "rate": w["rate"], "ch": w["ch"]}


def ref_momentary_plateau(x, rate=48000, win_s=0.4):
    """Own reference: K-weighted (libebur128 coefficients) mean-square over the
    max-energy 400 ms window (weight 1.0 = LEFT fallback)."""
    b, a = ebur_coeffs(rate)
    y = filt5(x, b, a)
    win = int(win_s * rate)
    best = -1.0
    bi = 0
    step = max(1, win // 8)
    for i in range(0, max(1, len(y) - win), step):
        e = sum(v * v for v in y[i:i + win]) / win
        if e > best:
            best, bi = e, i
    return 10 * math.log10(best) - 0.691 if best > 0 else float("-inf"), bi


def ebur_coeffs(rate=48000):
    f0 = 1681.974450955533
    G = 3.999843853973347
    Q = 0.7071752369554196
    K = math.tan(math.pi * f0 / rate)
    Vh = 10 ** (G / 20.0)
    Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    pb = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0,
          (Vh - Vb * K / Q + K * K) / a0]
    pa = [1.0, 2 * (K * K - 1.0) / a0, (1 - K / Q + K * K) / a0]
    rb = [1.0, -2.0, 1.0]
    f0 = 38.13547087602444
    Q = 0.5003270373238773
    K = math.tan(math.pi * f0 / rate)
    ra = [1.0, 2 * (K * K - 1.0) / (1 + K / Q + K * K),
          (1 - K / Q + K * K) / (1 + K / Q + K * K)]
    b = [pb[0] * rb[0], pb[0] * rb[1] + pb[1] * rb[0],
         pb[0] * rb[2] + pb[1] * rb[1] + pb[2] * rb[0],
         pb[1] * rb[2] + pb[2] * rb[1], pb[2] * rb[2]]
    a = [pa[0] * ra[0], pa[0] * ra[1] + pa[1] * ra[0],
         pa[0] * ra[2] + pa[1] * ra[1] + pa[2] * ra[0],
         pa[1] * ra[2] + pa[2] * ra[1], pa[2] * ra[2]]
    return b, a


def filt5(x, b, a):
    y = [0.0] * len(x)
    v = [0.0] * 5
    for i, xx in enumerate(x):
        v0 = xx - a[1] * v[1] - a[2] * v[2] - a[3] * v[3] - a[4] * v[4]
        yv = b[0] * v0 + b[1] * v[1] + b[2] * v[2] + b[3] * v[3] + b[4] * v[4]
        v[4] = v[3]
        v[3] = v[2]
        v[2] = v[1]
        v[1] = v0
        y[i] = yv
    return y


def ref_global(x, rate=48000, block_s=0.4, overlap=0.75, weight=1.0):
    """Own gated integrated loudness (BS.1770-4) over the captured signal."""
    b, a = ebur_coeffs(rate)
    y = filt5(x, b, a)
    win = int(block_s * rate)
    step = int(win * (1 - overlap))
    blocks = []
    for st in range(0, max(1, len(y) - win), step):
        e = weight * sum(v * v for v in y[st:st + win]) / win
        blocks.append(e)
    if not blocks:
        return {"lufs": float("-inf"), "n_blocks": 0}
    abs_gate = 10 ** ((-70.0 + 0.691) / 10.0)
    above = [e for e in blocks if e >= abs_gate]
    if not above:
        return {"lufs": float("-inf"), "n_blocks": len(blocks), "n_above_abs": 0}
    rel = (sum(above) / len(above)) * 10 ** (-1.0)
    rel_gate = max(rel, abs_gate)
    keep = [e for e in above if e >= rel_gate]
    mean = sum(keep) / len(keep)
    return {"lufs": round(10 * math.log10(mean) - 0.691, 6), "n_blocks": len(blocks),
            "n_above_abs": len(above), "n_keep": len(keep)}


# --------------------------------------------------------------------- stages

def stage_portmap(reps):
    ports = ["FL", "FR", "FC", "UNUSED", "SL", "SR", "DUAL MONO"]
    out = {"stage": "portmap", "reps": reps, "legs": []}
    stim = os.path.join(SCRATCH, "tone_1000_050.wav")
    L.write_wav_f32(stim, L.sine(1000, 3.5, amp=0.5))
    for port in ports:
        for rd in ("Momentary LUFS", "Global LUFS"):
            args = mkargs([EBU(), NODE("debug", "dbg")],
                          [link_spec("e:%s" % rd, "dbg:Control")],
                          ["e:In %s" % port], ["e:Out %s" % port])
            for rep in range(reps):
                tag = "portmap_%s_%s_r%d" % (port.replace(" ", ""), rd.split()[0], rep)
                row = Rig(tag, args, stim=stim, capture_ref=True).run()
                row["port"] = port
                row["readout"] = rd
                row["rep"] = rep
                if row.get("valid"):
                    row["stats"] = stats(row["control"])
                    if row.get("ref_path"):
                        w = L.read_wav_any(row["ref_path"])
                        pl, _ = ref_momentary_plateau(w["x"][0])
                        row["ref_momentary"] = round(pl, 6)
                        row["ref_global"] = ref_global(w["x"][0])
                out["legs"].append(row)
    return out


def stage_amp(reps):
    out = {"stage": "amp", "reps": reps, "legs": []}
    for amp in (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125):
        stim = os.path.join(SCRATCH, "tone_1000_a%05d.wav" % int(amp * 100000))
        L.write_wav_f32(stim, L.sine(1000, 3.5, amp=amp))
        for rd in ("Momentary LUFS",) + (("Global LUFS",) if amp in (0.5, 0.125, 0.03125) else ()):
            args = mkargs([EBU(), NODE("debug", "dbg")],
                          [link_spec("e:%s" % rd, "dbg:Control")],
                          ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
            for rep in range(reps):
                tag = "amp_%d_%s_r%d" % (int(amp * 1000), rd.split()[0], rep)
                row = Rig(tag, args, stim=stim, capture_ref=True).run()
                row.update({"amp": amp, "readout": rd, "rep": rep})
                if row.get("valid"):
                    row["stats"] = stats(row["control"])
                    if row.get("ref_path"):
                        w = L.read_wav_any(row["ref_path"])
                        pl, _ = ref_momentary_plateau(w["x"][0])
                        row["ref_momentary"] = round(pl, 6)
                        row["ref_global"] = ref_global(w["x"][0])
                out["legs"].append(row)
    return out


def stage_freq(reps):
    out = {"stage": "freq", "reps": reps, "legs": []}
    for f in (40, 100, 1000, 4000, 10000):
        stim = os.path.join(SCRATCH, "tone_%d_050.wav" % f)
        L.write_wav_f32(stim, L.sine(f, 3.5, amp=0.5))
        args = mkargs([EBU(), NODE("debug", "dbg")],
                      [link_spec("e:Momentary LUFS", "dbg:Control")],
                      ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        for rep in range(reps):
            tag = "freq_%d_r%d" % (f, rep)
            row = Rig(tag, args, stim=stim, capture_ref=True).run()
            row.update({"freq": f, "readout": "Momentary LUFS", "rep": rep})
            if row.get("valid"):
                row["stats"] = stats(row["control"])
                if row.get("ref_path"):
                    w = L.read_wav_any(row["ref_path"])
                    pl, _ = ref_momentary_plateau(w["x"][0])
                    row["ref_momentary"] = round(pl, 6)
            out["legs"].append(row)
    return out


def stage_stereo(reps):
    out = {"stage": "stereo", "reps": reps, "legs": []}
    both = os.path.join(SCRATCH, "st_both.wav")
    fson = os.path.join(SCRATCH, "st_fl_fr_sil.wav")
    t = L.sine(1000, 3.5, amp=0.5)
    sil = [0.0] * len(t)
    L.write_wav_f32(both, list(zip(t, t)), ch=2)
    L.write_wav_f32(fson, list(zip(t, sil)), ch=2)
    configs = [
        ("both", 2, ["e:In FL", "e:In FR"], ["e:Out FL", "e:Out FR"], both),
        ("fl_tone_fr_silence", 2, ["e:In FL", "e:In FR"], ["e:Out FL", "e:Out FR"], fson),
        ("mono_fl", 1, ["e:In FL"], ["e:Out FL"], os.path.join(SCRATCH, "tone_1000_050.wav")),
        ("mono_fr", 1, ["e:In FR"], ["e:Out FR"], os.path.join(SCRATCH, "tone_1000_050.wav")),
    ]
    for name, ch, ins, outs, stim in configs:
        for rd in ("Momentary LUFS", "Global LUFS"):
            args = mkargs([EBU(), NODE("debug", "dbg")],
                          [link_spec("e:%s" % rd, "dbg:Control")], ins, outs, ch=ch,
                          position="[MONO]" if ch == 1 else "[FL,FR]")
            for rep in range(reps):
                tag = "st_%s_%s_r%d" % (name, rd.split()[0], rep)
                row = Rig(tag, args, ch=ch, stim=stim, capture_ref=True).run()
                row.update({"cfg": name, "readout": rd, "rep": rep})
                if row.get("valid"):
                    row["stats"] = stats(row["control"])
                out["legs"].append(row)
    return out


def stage_modes(reps):
    out = {"stage": "modes", "reps": reps, "legs": []}
    stim = os.path.join(SCRATCH, "tone_1000_050.wav")
    arms = [
        ("only_range", "Range LU"),
        ("only_peak", "Peak"),
        ("only_window", "Window LUFS"),
        ("only_global", "Global LUFS"),
        ("only_momentary", "Momentary LUFS"),
    ]
    for name, rd in arms:
        args = mkargs([EBU(), NODE("debug", "dbg")],
                      [link_spec("e:%s" % rd, "dbg:Control")],
                      ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        for rep in range(reps):
            tag = "modes_%s_r%d" % (name, rep)
            row = Rig(tag, args, stim=stim, capture_post=True).run()
            row.update({"arm": name, "readout": rd, "rep": rep})
            if row.get("valid"):
                row["stats"] = stats(row["control"])
                row["post"] = capture_stats(row.get("post_path"))
            out["legs"].append(row)
    return out


def stage_window(reps, cfgs=(None, "max-window=2.0", "max-window=1.0", "max-window=0.4",
                           "max-window=5.0", "max-window=0.05")):
    out = {"stage": "window", "reps": reps, "legs": []}
    stim = os.path.join(SCRATCH, "tone_1000_050.wav")
    for cfg in cfgs:
        nodes = [EBU(cfg=cfg),
                 NODE("linear", "lin"), NODE("debug", "dbg")]
        links = [link_spec("e:Momentary LUFS", "lin:Control"),
                 link_spec("e:Window LUFS", "dbg:Control")]
        args = mkargs(nodes, links, ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        for rep in range(reps):
            tag = "win_%s_r%d" % (cfg or "default", rep)
            row = Rig(tag, args, stim=stim).run()
            row.update({"cfg": cfg, "readout": "Window LUFS", "rep": rep})
            if row.get("valid"):
                row["stats"] = stats(row["control"])
            out["legs"].append(row)
    return out


def stage_history(reps):
    out = {"stage": "history", "reps": reps, "legs": []}
    stim = os.path.join(SCRATCH, "tone_1000_1500ms.wav")
    L.write_wav_f32(stim, L.sine(1000, 1.5, amp=0.5))
    for cfg in (None, "max-history=2.0"):
        nodes = [EBU(cfg=cfg), NODE("linear", "lin"), NODE("debug", "dbg")]
        links = [link_spec("e:Momentary LUFS", "lin:Control"),
                 link_spec("e:Global LUFS", "dbg:Control")]
        args = mkargs(nodes, links, ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        for rep in range(reps):
            tag = "hist_%s_r%d" % (cfg or "default", rep)
            row = Rig(tag, args, stim=stim, dur=1.5, read_extra=5.0).run()
            row.update({"cfg": cfg, "readout": "Global LUFS", "rep": rep})
            if row.get("valid"):
                row["stats"] = stats(row["control"])
            out["legs"].append(row)
    return out


def stage_peaks(reps):
    out = {"stage": "peaks", "reps": reps, "legs": []}
    st08 = os.path.join(SCRATCH, "st_fl02_fr08.wav")
    a = L.sine(1000, 3.5, amp=0.2)
    b = L.sine(1000, 3.5, amp=0.8)
    L.write_wav_f32(st08, list(zip(a, b)), ch=2)
    configs = [
        ("mono_fl", 1, ["e:In FL"], ["e:Out FL"], os.path.join(SCRATCH, "tone_1000_050.wav")),
        ("mono_dual", 1, ["e:In DUAL MONO"], ["e:Out DUAL MONO"],
         os.path.join(SCRATCH, "tone_1000_050.wav")),
        ("st_fl02_fr08", 2, ["e:In FL", "e:In FR"], ["e:Out FL", "e:Out FR"], st08),
    ]
    for name, ch, ins, outs, stim in configs:
        for rd in ("Peak", "True Peak"):
            nodes = [EBU(), NODE("linear", "lin"), NODE("debug", "dbg")]
            links = [link_spec("e:Momentary LUFS", "lin:Control"),
                     link_spec("e:%s" % rd, "dbg:Control")]
            args = mkargs(nodes, links, ins, outs, ch=ch,
                          position="[MONO]" if ch == 1 else "[FL,FR]")
            for rep in range(reps):
                tag = "peak_%s_%s_r%d" % (name, rd.replace(" ", ""), rep)
                row = Rig(tag, args, ch=ch, stim=stim).run()
                row.update({"cfg": name, "readout": rd, "rep": rep})
                if row.get("valid"):
                    row["stats"] = stats(row["control"])
                out["legs"].append(row)
    return out


def stage_lufs2gain(reps):
    out = {"stage": "lufs2gain", "reps": reps, "legs": []}
    stim = os.path.join(SCRATCH, "tone_1000_050.wav")
    arms = [
        ("default", None, stim),
        ("target_m100_clamp", '"Target LUFS"=-100', stim),
        ("target_0", '"Target LUFS"=0', stim),
        ("target_unquoted", "Target LUFS=-100", stim),
        ("silence", None, os.path.join(SCRATCH, "silence.wav")),
    ]
    L.write_wav_f32(os.path.join(SCRATCH, "silence.wav"), [0.0] * 168000)
    for name, ctl, st in arms:
        nodes = [EBU(), NODE("lufs2gain", "l2g", ctl=ctl, type_="ebur128"),
                 NODE("linear", "lin"), NODE("linear", "lin2"), NODE("debug", "dbg")]
        links = [link_spec("e:Momentary LUFS", "lin2:Control"),
                 link_spec("e:Global LUFS", "l2g:LUFS"),
                 link_spec("l2g:Gain", "lin:Mult"),
                 link_spec("l2g:Gain", "dbg:Control"),
                 link_spec("e:Out DUAL MONO", "lin:In")]
        args = mkargs(nodes, links, ["e:In DUAL MONO"], ["lin:Out"])
        for rep in range(reps):
            tag = "l2g_%s_r%d" % (name, rep)
            row = Rig(tag, args, stim=st, capture_ref=(name == "default"),
                      capture_post=(name == "default")).run()
            row.update({"arm": name, "readout": "Gain", "rep": rep})
            if row.get("valid"):
                row["stats"] = stats(row["control"])
                if name == "default" and row.get("ref_path") and row.get("post_path"):
                    wr = L.read_wav_any(row["ref_path"])["x"][0]
                    wo = L.read_wav_any(row["post_path"])["x"][0]
                    n = min(len(wr), len(wo))
                    seg = slice(n // 2, n // 2 + 48000)
                    rr = math.sqrt(sum(v * v for v in wr[seg]) / 48000)
                    ro = math.sqrt(sum(v * v for v in wo[seg]) / 48000)
                    row["audio_ratio"] = round(ro / rr, 6) if rr > 0 else None
                    row["ref_global"] = ref_global(wr)
            out["legs"].append(row)
    return out


def stage_edge(reps):
    out = {"stage": "edge", "reps": reps, "legs": []}
    stim = os.path.join(SCRATCH, "tone_1000_050.wav")
    arms = [
        ("unknown_key", EBU(cfg="bogus=1"), ["e:In DUAL MONO"], ["e:Out DUAL MONO"]),
        ("bad_max_history", EBU(cfg="max-history=abc"), ["e:In DUAL MONO"],
         ["e:Out DUAL MONO"]),
        ("fl_plus_dual", EBU(), ["e:In FL", "e:In DUAL MONO"],
         ["e:Out FL", "e:Out DUAL MONO"]),
    ]
    for name, e, ins, outs in arms:
        args = mkargs([e, NODE("debug", "dbg")],
                      [link_spec("e:Momentary LUFS", "dbg:Control")], ins, outs)
        for rep in range(reps):
            tag = "edge_%s_r%d" % (name, rep)
            row = Rig(tag, args, stim=stim).run()
            row.update({"arm": name, "readout": "Momentary LUFS", "rep": rep})
            if row.get("valid"):
                row["stats"] = stats(row["control"])
            out["legs"].append(row)
    return out


def ensure_stimuli():
    """Deterministic f32 stimuli shared by stages (idempotent)."""
    want = {
        "tone_1000_050.wav": lambda: L.sine(1000, 3.5, amp=0.5),
        "tone_1000_1500ms.wav": lambda: L.sine(1000, 1.5, amp=0.5),
        "silence.wav": lambda: [0.0] * 168000,
    }
    for name, fn in want.items():
        p = os.path.join(SCRATCH, name)
        if not os.path.exists(p):
            L.write_wav_f32(p, fn())


def stage_refflat(reps):
    out = {"stage": "refflat", "reps": reps, "legs": []}
    stim = os.path.join(SCRATCH, "tone_1000_050.wav")
    ensure_stimuli()
    # ffmpeg cross-witness
    for rep in range(reps):
        r = L.run(["ffmpeg", "-hide_banner", "-nostats", "-i", stim,
                   "-af", "ebur128=peak=true", "-f", "null", "-"], wall=30.0)
        txt = r.err
        vals = {}
        for key in ("I:", "LRA:", "Peak:"):
            m = [l.strip() for l in txt.splitlines() if key in l]
            vals[key] = m[-1][:120] if m else None
        out["legs"].append({"tag": "ffmpeg_r%d" % rep, "rep": rep, "rc": r.rc,
                            "summary": vals, "tail": txt[-500:]})
    # own reference over the same stimulus
    w = L.read_wav_any(stim)
    pl, _ = ref_momentary_plateau(w["x"][0])
    out["ref_stimulus"] = {"momentary": round(pl, 6), "global": ref_global(w["x"][0])}
    return out


def stage_labels(reps):
    """Label inventory: the 6 labels r92's 32-candidate census omitted + the 6
    known-absent strings. Load-only legs (bounded, no tone)."""
    out = {"stage": "labels", "reps": reps, "legs": []}
    cases = [
        ("debug", "In/Out"), ("ramp", "In/Out"), ("zeroramp", "In/Out"),
        ("sqrt", "In/Out"), ("busy", "null/null"), ("null", "In/null"),
        ("avg", "In/Out"), ("gain", "In/Out"), ("min", "In/Out"),
        ("nop", "In/Out"), ("passthrough", "In/Out"), ("sum", "In/Out"),
    ]
    for label, shape in cases:
        for rep in range(reps):
            ins, outs = shape.split("/")
            if ins == "null":
                insl, outsl = ["null"], ["null"]
            elif outs == "null":
                insl, outsl = ["x:%s" % ins], ["null"]
            else:
                insl, outsl = ["x:%s" % ins], ["x:%s" % outs]
            args = mkargs([NODE(label, "x")], [], insl, outsl)
            row = {"tag": "label_%s_r%d" % (label, rep), "label": label, "rep": rep,
                   "args": args}
            sink = L.run(["pactl", "load-module", "module-null-sink",
                          "sink_name=%s" % NS, "channels=1"], wall=6.0)
            time.sleep(0.25)
            cli = L.PwCli(idle=0.35, hard=3.0)
            lo, var = cli.load("libpipewire-module-filter-chain", args)
            row["load_ok"] = var is not None
            row["errs"] = [l.strip()[:200] for l in lo.splitlines()
                           if "[E]" in l or "[W]" in l]
            if var is not None:
                cli.cmd("unload-module %d" % var)
            cli.close()
            time.sleep(0.3)
            if sink.out.strip().isdigit():
                L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)
            time.sleep(0.2)
            out["legs"].append(row)
    return out


def stage_passthrough(reps):
    """ebur128 audio path: bit-exact copy witness (dual tap, aligned diff)."""
    out = {"stage": "passthrough", "reps": reps, "legs": []}
    stim = os.path.join(SCRATCH, "tone_1000_050.wav")
    args = mkargs([EBU(), NODE("debug", "dbg")],
                  [link_spec("e:Momentary LUFS", "dbg:Control")],
                  ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
    for rep in range(reps):
        tag = "passthrough_r%d" % rep
        row = Rig(tag, args, stim=stim, capture_ref=True, capture_post=True).run()
        row["rep"] = rep
        if row.get("valid"):
            row["stats"] = stats(row["control"])
            if row.get("ref_path") and row.get("post_path"):
                wr = L.read_wav_any(row["ref_path"])["x"][0]
                wo = L.read_wav_any(row["post_path"])["x"][0]
                n = min(len(wr), len(wo))
                # align: first sample above 0.05 in each, then +/-2 refine on max-diff
                def onset(x):
                    return next((i for i, v in enumerate(x) if abs(v) > 0.05), 0)
                lag = onset(wo) - onset(wr)
                best = None
                for dl in range(-3, 4):
                    L2 = lag + dl
                    if L2 < 0:
                        continue
                    seg_r = wr[96000:96000 + 8192]
                    seg_o = wo[96000 + L2:96000 + L2 + 8192]
                    if len(seg_o) < 8192:
                        continue
                    md = max(abs(a - b) for a, b in zip(seg_r, seg_o))
                    if best is None or md < best[1]:
                        best = (L2, md)
                row["align"] = {"lag": lag, "best_lag": best[0] if best else None,
                                "max_abs_diff": round(best[1], 9) if best else None}
        out["legs"].append(row)
    return out


def stage_gating(reps):
    """Relative-gate semantics: loud/quiet/loud program; Global excludes the
    quiet section, Momentary follows it. use-histogram cross-arm."""
    out = {"stage": "gating", "reps": reps, "legs": []}
    seg = 2.0
    loud = L.sine(1000, seg, amp=0.5)
    quiet = L.sine(1000, seg, amp=0.005)
    prog = loud + quiet + loud
    stim = os.path.join(SCRATCH, "prog_loud_quiet_loud.wav")
    L.write_wav_f32(stim, prog)
    arms = [
        ("global_default", None, "Global LUFS"),
        ("momentary_default", None, "Momentary LUFS"),
        ("global_histogram", "use-histogram=true", "Global LUFS"),
    ]
    for name, cfg, rd in arms:
        args = mkargs([EBU(cfg=cfg), NODE("debug", "dbg")],
                      [link_spec("e:%s" % rd, "dbg:Control")],
                      ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        for rep in range(reps):
            tag = "gate_%s_r%d" % (name, rep)
            row = Rig(tag, args, stim=stim, dur=6.0, capture_ref=True).run()
            row.update({"arm": name, "readout": rd, "rep": rep})
            if row.get("valid"):
                row["stats"] = stats(row["control"])
                # segment means: t in [1.0,2.0) loud1, [3.0,4.0) quiet, [5.0,6.0) loud2
                ser = row["control"]
                def segmean(a, b):
                    vs = [v for t, v in ser if a <= t < b and math.isfinite(v)]
                    return round(sum(vs) / len(vs), 4) if vs else None
                row["seg"] = {"loud1": segmean(1.0, 2.0), "quiet": segmean(3.0, 4.0),
                              "loud2": segmean(5.0, 6.0)}
                if row.get("ref_path"):
                    w = L.read_wav_any(row["ref_path"])
                    row["ref_global"] = ref_global(w["x"][0])
            out["legs"].append(row)
    return out


def stage_mix(reps):
    """Stereo with unequal channels: pins the dB-domain mean law for
    Momentary and the relative-gate exclusion of the quiet channel in Global."""
    out = {"stage": "mix", "reps": reps, "legs": []}
    a = L.sine(1000, 3.5, amp=0.5)
    b = L.sine(1000, 3.5, amp=0.05)
    stim = os.path.join(SCRATCH, "st_fl05_fr005.wav")
    L.write_wav_f32(stim, list(zip(a, b)), ch=2)
    for rd in ("Momentary LUFS", "Global LUFS"):
        args = mkargs([EBU(), NODE("debug", "dbg")],
                      [link_spec("e:%s" % rd, "dbg:Control")],
                      ["e:In FL", "e:In FR"], ["e:Out FL", "e:Out FR"], ch=2,
                      position="[FL,FR]")
        for rep in range(reps):
            tag = "mix_%s_r%d" % (rd.split()[0], rep)
            row = Rig(tag, args, ch=2, stim=stim, dur=3.5, read_extra=3.0).run()
            row.update({"readout": rd, "rep": rep})
            if row.get("valid"):
                row["stats"] = stats(row["control"])
            out["legs"].append(row)
    return out


def stage_hist2(reps):
    """max-history is a block-count cap, not a time window: two loud bursts of
    different level separated by silence; with max-history=2.0 the first burst's
    blocks are evicted by the second burst, default (10 s) keeps both."""
    out = {"stage": "hist2", "reps": reps, "legs": []}
    b1 = L.sine(1000, 2.5, amp=0.5)
    sil = [0.0] * int(1.5 * 48000)
    b2 = L.sine(1000, 2.5, amp=0.25)
    prog = b1 + sil + b2
    stim = os.path.join(SCRATCH, "prog_burst_quiet.wav")
    L.write_wav_f32(stim, prog)
    for cfg in (None, "max-history=2.0"):
        args = mkargs([EBU(cfg=cfg), NODE("linear", "lin"), NODE("debug", "dbg")],
                      [link_spec("e:Momentary LUFS", "lin:Control"),
                       link_spec("e:Global LUFS", "dbg:Control")],
                      ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        for rep in range(reps):
            tag = "hist2_%s_r%d" % (cfg or "default", rep)
            row = Rig(tag, args, stim=stim, dur=6.5, read_extra=2.0, capture_ref=True).run()
            row.update({"cfg": cfg, "rep": rep})
            if row.get("valid"):
                row["stats"] = stats(row["control"])
                ser = row["control"]
                def segmean(a, b):
                    vs = [v for t, v in ser if a <= t < b and math.isfinite(v)]
                    return round(sum(vs) / len(vs), 4) if vs else None
                row["seg"] = {"b1": segmean(1.5, 2.5), "b2": segmean(5.5, 6.5)}
                if row.get("ref_path"):
                    w = L.read_wav_any(row["ref_path"])
                    row["ref_global"] = ref_global(w["x"][0])
            out["legs"].append(row)
    return out


def stage_l2gcheck(reps):
    """Disambiguate the m100-clamp arm: read Global and Gain in the SAME leg
    (two debug nodes); values are attributable by range (Global < -1 < Gain <= 1
    during the clamped run)."""
    out = {"stage": "l2gcheck", "reps": reps, "legs": []}
    stim = os.path.join(SCRATCH, "tone_1000_050.wav")
    arms = [
        ("m100", '"Target LUFS"=-100'),
        ("m70", '"Target LUFS"=-70'),
    ]
    for name, ctl in arms:
        nodes = [EBU(), NODE("lufs2gain", "l2g", ctl=ctl, type_="ebur128"),
                 NODE("linear", "lin"), NODE("linear", "lin2"),
                 NODE("debug", "dbgG"), NODE("debug", "dbgK")]
        links = [link_spec("e:Momentary LUFS", "lin2:Control"),
                 link_spec("e:Global LUFS", "l2g:LUFS"),
                 link_spec("l2g:Gain", "lin:Mult"),
                 link_spec("e:Global LUFS", "dbgG:Control"),
                 link_spec("l2g:Gain", "dbgK:Control"),
                 link_spec("e:Out DUAL MONO", "lin:In")]
        args = mkargs(nodes, links, ["e:In DUAL MONO"], ["lin:Out"])
        for rep in range(reps):
            tag = "l2gcheck_%s_r%d" % (name, rep)
            row = Rig(tag, args, stim=stim, capture_ref=True, capture_post=True).run()
            row.update({"arm": name, "ctl": ctl, "rep": rep})
            if row.get("valid"):
                ser = row["control"]
                glob = [v for _, v in ser if math.isfinite(v) and v < -1.0]
                gain = [v for _, v in ser if math.isfinite(v) and -1.0 <= v <= 1.0 and v > 0.0]
                row["global_series"] = len(glob)
                row["gain_series"] = len(gain)
                row["global_tail"] = [round(v, 4) for v in glob[-5:]]
                row["gain_tail"] = [round(v, 6) for v in gain[-5:]]
                if row.get("ref_path"):
                    w = L.read_wav_any(row["ref_path"])
                    row["ref_global"] = ref_global(w["x"][0])
            out["legs"].append(row)
    return out


def stage_ctlgrammar(reps):
    """Control-key grammar: a key containing a space must be quoted; the raw
    form fails at the properties parser (verbatim error preserved)."""
    out = {"stage": "ctlgrammar", "reps": reps, "legs": []}
    stim = os.path.join(SCRATCH, "tone_1000_050.wav")
    raw_unquoted = ('node.description=r93s_fc,'
                    'filter.graph={nodes=[{type=ebur128,name=e,label=ebur128},'
                    '{type=ebur128,name=l2g,label=lufs2gain,control={Target LUFS=-100}},'
                    '{type=builtin,name=dbg,label=debug}],'
                    'links=[{output="e:Global LUFS",input="l2g:LUFS"},'
                    '{output="l2g:Gain",input="dbg:Control"}],'
                    'inputs=["e:In DUAL MONO"],outputs=["e:Out DUAL MONO"]},'
                    'audio.channels=1,audio.position=[MONO],'
                    'capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},'
                    'playback.props={node.name=%s,node.autoconnect=false}' % (FC_IN, FC_OUT))
    quoted = raw_unquoted.replace('control={Target LUFS=-100}',
                                  'control={"Target LUFS"=-100}')
    for name, args in (("raw_unquoted", raw_unquoted), ("quoted", quoted)):
        for rep in range(reps):
            tag = "ctl_%s_r%d" % (name, rep)
            row = Rig(tag, args, stim=stim, dur=2.0, read_extra=1.0).run()
            row.update({"arm": name, "rep": rep})
            if row.get("valid"):
                row["stats"] = stats(row["control"])
            out["legs"].append(row)
    return out


def stage_labels2(reps):
    """`null` label shape probe: is the earlier failure a label absence or a
    graph-shape constraint (a node with no audio output cannot close a graph)?"""
    out = {"stage": "labels2", "reps": reps, "legs": []}
    shapes = [
        ("null_only_outnull", [NODE("null", "x")], [], ["x:In"], ["null"]),
        ("null_plus_copy", [NODE("null", "x"), NODE("copy", "c")], [], ["x:In"], ["c:Out"]),
        ("copy_only_control", [NODE("copy", "c")], [], ["c:In"], ["c:Out"]),
    ]
    for name, nodes, links, ins, outs in shapes:
        for rep in range(reps):
            args = mkargs(nodes, links, ins, outs)
            row = {"tag": "lab2_%s_r%d" % (name, rep), "shape": name, "rep": rep,
                   "args": args}
            sink = L.run(["pactl", "load-module", "module-null-sink",
                          "sink_name=%s" % NS, "channels=1"], wall=6.0)
            time.sleep(0.25)
            cli = L.PwCli(idle=0.35, hard=3.0)
            lo, var = cli.load("libpipewire-module-filter-chain", args)
            row["load_ok"] = var is not None
            row["errs"] = [l.strip()[:220] for l in lo.splitlines()
                           if "[E]" in l or "[W]" in l][:6]
            if var is not None:
                cli.cmd("unload-module %d" % var)
            cli.close()
            time.sleep(0.3)
            if sink.out.strip().isdigit():
                L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)
            time.sleep(0.2)
            out["legs"].append(row)
    return out


STAGES = {
    "portmap": stage_portmap, "amp": stage_amp, "freq": stage_freq,
    "stereo": stage_stereo, "modes": stage_modes, "window": stage_window,
    "history": stage_history, "peaks": stage_peaks, "lufs2gain": stage_lufs2gain,
    "edge": stage_edge, "refflat": stage_refflat, "labels": stage_labels,
    "passthrough": stage_passthrough, "gating": stage_gating, "mix": stage_mix,
    "hist2": stage_hist2, "l2gcheck": stage_l2gcheck, "ctlgrammar": stage_ctlgrammar,
    "labels2": stage_labels2,
}


def preflight():
    stray = [l.strip()[:140] for l in L.run(["ps", "-eo", "pid,cmd"], wall=5.0).out.splitlines()
             if "r93s" in l and l.strip().split(None, 1)[-1].startswith(
                 ("pw-", "pipewire", "pactl"))]
    killed = []
    for l in stray:
        try:
            os.kill(int(l.split()[0]), 9)
            killed.append(l.split()[0])
        except Exception:
            pass
    mods = [l.split()[0] for l in L.run(["pactl", "list", "modules", "short"],
                                        wall=6.0).out.splitlines() if "r93s" in l]
    for m in mods:
        L.run(["pactl", "unload-module", m], wall=6.0)
    time.sleep(0.3)
    return {"stray": stray, "killed": killed, "modules_unloaded": mods}


def sweep():
    mods = [l.split()[0] for l in L.run(["pactl", "list", "modules", "short"],
                                        wall=6.0).out.splitlines() if "r93s" in l]
    for m in mods:
        L.run(["pactl", "unload-module", m], wall=6.0)
    time.sleep(0.4)
    d = L.run(["pw-dump"], wall=8.0)
    try:
        objs = json.loads(d.out)
    except Exception:
        objs = []
    nodes = [o["info"]["props"].get("node.name") for o in objs
             if o.get("type") == "PipeWire:Interface:Node"
             and "r93s" in o.get("info", {}).get("props", {}).get("node.name", "")]
    procs = [l.strip()[:120] for l in L.run(["ps", "-eo", "pid,cmd"], wall=5.0).out.splitlines()
             if "r93s" in l and l.strip().split(None, 1)[-1].startswith(
                 ("pw-", "pipewire", "pactl"))]
    return {"modules_left": mods, "nodes_left": nodes, "procs_left": procs,
            "clean": not (mods or nodes or procs)}


def main():
    stage = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    res = {"toolchain": {"pipewire": "1.6.8", "libebur128": "1.2.6",
                         "wireplumber": "0.5.17", "python": sys.version.split()[0]},
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "preflight": preflight()}
    ensure_stimuli()
    t0 = time.time()
    res.update(STAGES[stage](reps))
    res["sweep"] = sweep()
    res["wall_s"] = round(time.time() - t0, 1)
    path = os.path.join(REC, "%s.json" % stage)
    L.jdump(path, res)
    legs = res.get("legs", [])
    ok = sum(1 for r in legs if r.get("valid"))
    print("%s: legs=%d valid=%d sweep_clean=%s wall=%.1fs -> %s"
          % (stage, len(legs), ok, res["sweep"]["clean"], res["wall_s"], path))
    for r in legs[:200]:
        st = r.get("stats") or {}
        print("  %-34s %-14s plateau=%s nan=%s inf=%s conv=%s" % (
            r.get("tag"), r.get("readout"), st.get("plateau"), st.get("n_nan"),
            st.get("n_inf"), st.get("conv_s")))


if __name__ == "__main__":
    main()
