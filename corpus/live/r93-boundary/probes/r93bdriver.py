#!/usr/bin/env python3
"""r93-boundary driver — boundary replay of the r93 scout's armed ebur128 cells.

Seat: EXECUTOR (boundary). Namespace r93b_*; own PIDs only; own-object sweeps
only. Every leg is a fresh pw-cli client + fresh filter-chain module + fresh
null sink + fresh pw-play (the scout's "arm"), so a rep is a fresh-process rep.

Stages (argv[1]), reps (argv[2]):
  recon     port table, notify/Props readout check, cadence, driver/quantum
  core      the armed cells replayed (calibration, portmap, stereo/mix, modes,
            peaks, lufs2gain, ctlgrammar, gating, passthrough)
  window    max-window matrix + decay-length law
  history   Global through silence, default vs max-history=2.0
  hist2     two-burst eviction program
  labels    builtin label load matrix (debug/busy/sqrt/ramp/zeroramp/null/avg)
  ref       ffmpeg ebur128 + own reference cross-witness on captured taps
  rate      PipeWire/stimulus rate axis
  quantum   clock.force-quantum axis (cadence + plateau)
  flags     CLI flag-order axis (pw-record / pw-play / pw-link / module args)
  defaults  default-node state axis (ambient vs own null sink; restored)

argv[3:] extra: --load N (spawn N CPU hogs + 2 audio hogs for the stage),
--cond NAME (label recorded in the receipt).
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
import r93blib as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(HERE, "receipts")
SCRATCH = os.path.join(HERE, "scratch")
RUNS = os.path.join(HERE, "runs")
for d in (REC, SCRATCH, RUNS):
    os.makedirs(d, exist_ok=True)

NS = "r93b_in"
FC_IN, FC_OUT = "r93b_fc_in", "r93b_fc_out"
REF, RECN = "r93b_ref", "r93b_rec"
HOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r93b_hog.py")

CTRL_RE = re.compile(r"\[I\]\[(\d\d:\d\d:\d\d\.\d+)\]\[[^\]]*\]\s+control:\s*(-?[\d.]+|-?nan|-?inf)")
TS_RE = re.compile(r"\[I\]\[(\d\d):(\d\d):(\d\d)\.(\d+)\]")


def ts_seconds(line):
    m = TS_RE.search(line)
    if not m:
        return None
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1e6


# ------------------------------------------------------------------ graph args

def q(p):
    return '"%s"' % p


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


def mkargs(nodes, links, inputs, outputs, ch=1, position="[MONO]", order="default"):
    head = ("node.description=r93b_fc,"
            "filter.graph={nodes=[%s],links=[%s],inputs=[%s],outputs=[%s]},"
            "audio.channels=%d,audio.position=%s,"
            "capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},"
            "playback.props={node.name=%s,node.autoconnect=false}"
            % (",".join(nodes), ",".join(links), ",".join('"%s"' % i for i in inputs),
               ",".join('"%s"' % o for o in outputs), ch, position, FC_IN, FC_OUT))
    if order == "channels_first":
        # same semantics, different argv order inside the module arg string
        head = ("audio.channels=%d,audio.position=%s,node.description=r93b_fc,"
                "capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},"
                "playback.props={node.name=%s,node.autoconnect=false},"
                "filter.graph={nodes=[%s],links=[%s],inputs=[%s],outputs=[%s]}"
                % (ch, position, FC_IN, FC_OUT, ",".join(nodes), ",".join(links),
                   ",".join('"%s"' % i for i in inputs),
                   ",".join('"%s"' % o for o in outputs)))
    return head


def link_spec(outp, inp):
    return "{output=%s,input=%s}" % (q(outp), q(inp))


# ---------------------------------------------------------------------- hogs

class Hogs:
    """>=12 concurrent own-namespace hogs. Kills exactly the PIDs it spawned."""

    def __init__(self, n_cpu=12, n_audio=2, dur=1800.0):
        self.n_cpu = n_cpu
        self.n_audio = n_audio
        self.dur = dur
        self.procs = []
        self.pids = []
        self.started = None
        self.stopped = None

    def start(self):
        self.started = time.time()
        for i in range(self.n_cpu):
            p = subprocess.Popen([sys.executable, HOG, str(self.dur)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 stdin=subprocess.DEVNULL, start_new_session=True,
                                 preexec_fn=L._ncore)
            self.procs.append(("cpu%d" % i, p))
        for i in range(self.n_audio):
            # audio hog: a recording stream on the seat's own null sink. The sink
            # does not exist until the first leg creates it, so the recorder is
            # wrapped in a bounded retry loop (own session -> killpg teardown).
            script = ("for _ in $(seq 1 2000); do "
                      "timeout 10 pw-record --target %s --format f32 --channels 1 "
                      "-P node.name=r93b_hogrec%d /dev/null; sleep 0.2; done"
                      % (NS, i))
            p = subprocess.Popen(["bash", "-c", script],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 stdin=subprocess.DEVNULL, start_new_session=True,
                                 preexec_fn=L._ncore)
            self.procs.append(("audio%d" % i, p))
        self.pids = [p.pid for _, p in self.procs]
        return {"pids": self.pids, "n_cpu": self.n_cpu, "n_audio": self.n_audio,
                "t0": self.started}

    def alive(self):
        return {nm: (p.poll() is None) for nm, p in self.procs}

    def state(self):
        return {"pids": self.pids, "alive": self.alive(),
                "loadavg": L.loadavg(),
                "cpu_alive": sum(1 for nm, p in self.procs
                                 if nm.startswith("cpu") and p.poll() is None),
                "audio_alive": sum(1 for nm, p in self.procs
                                   if nm.startswith("audio") and p.poll() is None)}

    def stop(self):
        self.stopped = time.time()
        out = []
        for nm, p in self.procs:                      # exact PIDs, own children
            if p.poll() is None:
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                except (ProcessLookupError, PermissionError):
                    pass
        for nm, p in self.procs:
            try:
                p.communicate(timeout=4)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
                try:
                    p.communicate(timeout=3)
                except Exception:
                    pass
            out.append({"name": nm, "pid": p.pid, "rc": p.returncode})
        gone = []
        for e in out:
            try:
                os.kill(e["pid"], 0)
                gone.append(e["pid"])
            except ProcessLookupError:
                pass
            except PermissionError:
                gone.append(e["pid"])
        return {"procs": out, "still_present": gone, "dur_s": round(self.stopped - self.started, 1)}


# ------------------------------------------------------------------------ rig

class Rig:
    """One leg: fresh null sink + fresh filter-chain module + fresh feed links
    (+ optional taps) + fresh pw-play; index-verified teardown."""

    def __init__(self, tag, args, ch=1, capture_ref=False, capture_post=False,
                 stim=None, dur=3.5, read_extra=1.4, sink_rate=None,
                 set_default=False, feed_ports=None, tap_ref_port=None,
                 tap_post_port=None, link_order="normal", enum_params=False,
                 play_argv_shape="target_first", rec_argv_shape="default",
                 need_fc=False):
        self.tag = tag
        self.args = args
        self.ch = ch
        self.capture_ref = capture_ref
        self.capture_post = capture_post
        self.stim = stim
        self.dur = dur
        self.read_extra = read_extra
        self.sink_rate = sink_rate
        self.set_default = set_default
        self.feed_ports = feed_ports
        self.tap_ref_port = tap_ref_port
        self.tap_post_port = tap_post_port
        self.link_order = link_order
        self.enum_params = enum_params
        self.play_argv_shape = play_argv_shape
        self.rec_argv_shape = rec_argv_shape
        self.need_fc = need_fc

    def link(self, a, b, tries=12):
        if self.link_order == "reversed":
            a, b = b, a
        last = None
        for i in range(tries):
            r = L.run(["pw-link", a, b], wall=4.0)
            last = r
            if r.rc == 0 or "File exists" in r.err:
                return {"ok": True, "tries": i + 1}
            time.sleep(0.25)
        return {"ok": False, "rc": last.rc, "err": last.err.strip(), "tries": tries}

    def run(self, tries=3):
        """Arm the leg; a pw-play failure (rc != 0, empty stderr, silent meter)
        is an ARM failure, not an absence: retry the whole leg, bounded."""
        row = None
        for attempt in range(tries):
            row = self._run_once(attempt)
            if not row.get("arm_failed"):
                return row
            time.sleep(1.0)
        return row

    def _run_once(self, attempt=0):
        tag = self.tag if not attempt else "%s_retry%d" % (self.tag, attempt)
        row = {"tag": tag, "base_tag": self.tag, "attempt": attempt,
               "args": self.args, "cond_load": COND["name"],
               "leg_t0": time.strftime("%H:%M:%S", time.gmtime()),
               "loadavg_start": L.loadavg()}
        sink_argv = ["pactl", "load-module", "module-null-sink", "sink_name=%s" % NS,
                     "channels=%d" % self.ch]
        if self.sink_rate:
            sink_argv.append("rate=%d" % self.sink_rate)
        sink = L.run(sink_argv, wall=6.0)
        row["sink"] = sink.out.strip()
        row["sink_argv"] = sink_argv
        time.sleep(0.3)
        snap = L.host_snapshot()
        row["foreign_nodes"] = snap.get("foreign_seat_nodes")
        row["own_nodes_at_start"] = snap.get("own_nodes")
        orig_default = None
        if self.set_default:
            orig_default = L.run(["pactl", "get-default-sink"], wall=5.0).out.strip()
            row["defaults_at_leg"] = {"sink": orig_default}
        if self.set_default and sink.out.strip().isdigit():
            row["set_default"] = L.run(["pactl", "set-default-sink", NS], wall=5.0).rc
            row["default_after_set"] = L.run(["pactl", "get-default-sink"], wall=5.0).out.strip()
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
            if self.set_default and orig_default:
                row["restore_default"] = L.run(["pactl", "set-default-sink", orig_default], wall=5.0).rc
            if sink.out.strip().isdigit():
                L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)
            row["valid"] = False
            row["loadavg_end"] = L.loadavg()
            return row
        # node ids for this leg (own namespace only; only when needed)
        snap2 = L.host_snapshot() if self.need_fc else {"nodes": {}, "ports": {}}
        row["node_scan"] = "full" if self.need_fc else "skipped (need_fc=False)"
        row["own_nodes_loaded"] = snap2.get("own_nodes")
        fc_id = next((i for i, v in (snap2.get("nodes") or {}).items()
                      if v.get("name") == FC_IN), None)
        row["fc_node_id"] = fc_id
        if fc_id is not None:
            row["fc_props"] = (snap2["nodes"][fc_id])
            row["fc_ports"] = sorted(p["name"] for p in (snap2.get("ports") or {}).values()
                                     if str(p.get("node.id")) == str(fc_id))
        if self.enum_params and fc_id is not None:
            cli2 = L.PwCli(idle=0.4, hard=5.0)          # plain session: no registry spam
            props = cli2.cmd("enum-params %s Props" % fc_id, idle=0.5, hard=6.0)
            fmt = cli2.cmd("enum-params %s Format" % fc_id, idle=0.5, hard=6.0)
            cli2.close()
            row["props_out"] = props[-4000:]
            row["format_out"] = fmt[-4000:]
            row["lufs_keys_in_props"] = [l.strip()[:140] for l in props.splitlines()
                                         if "LUFS" in l or "Peak" in l][:10]
            row["rate_in_format"] = [l.strip()[:140] for l in fmt.splitlines()
                                     if "rate" in l.lower()][:10]
            row["props_bytes"] = len(props)
        # feeds
        feeds = []
        ports = self.feed_ports or (["MONO"] if self.ch == 1 else ["FL", "FR"])
        for p in ports:
            feeds.append(self.link("%s:monitor_%s" % (NS, p), "%s:playback_%s" % (FC_IN, p)))
        row["feeds"] = feeds
        # taps
        refp = os.path.join(SCRATCH, "%s_ref.wav" % self.tag)
        postp = os.path.join(SCRATCH, "%s_post.wav" % self.tag)
        cap = []
        if self.capture_ref:
            if os.path.exists(refp):
                os.unlink(refp)
            if self.rec_argv_shape == "path_first":
                argv = ["pw-record", refp, "--format", "f32", "--channels", "1",
                        "-P", "node.name=%s" % REF, "-P", "node.autoconnect=false"]
            else:
                argv = ["pw-record", "--format", "f32", "--channels", "1",
                        "-P", "node.name=%s" % REF,
                        "-P", "node.autoconnect=false", refp]
            row["rec_argv"] = argv
            cap.append(("ref", L.Bg(argv, wall=self.dur + 5.0)))
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
            src = ("%s:monitor_%s" % (NS, self.tap_ref_port or ("MONO" if self.ch == 1 else "FL"))
                   if nm == "ref" else
                   "%s:output_%s" % (FC_OUT, self.tap_post_port or ("MONO" if self.ch == 1 else "FL")))
            row["%s_link" % nm] = self.link(src, "%s:input_MONO" % tgt)
        # play + read the notify log
        play = None
        if self.stim:
            if self.play_argv_shape == "file_first":
                argv = ["pw-play", self.stim, "--target", NS]
            else:
                argv = ["pw-play", "--target", NS, self.stim]
            row["play_argv"] = argv
            play = L.Bg(argv, wall=self.dur + 8.0)
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
            rc = row["play"].get("rc")
            if rc in (-9, -15):          # our own teardown signal
                row["arm_failed"] = len(row.get("control") or []) == 0
            else:
                row["arm_failed"] = rc not in (0, None)
        else:
            row["arm_failed"] = False
        stops = {}
        for nm, obj in cap:
            stops[nm] = obj.stop()
        row["captures"] = stops
        if os.path.exists(refp):
            row["ref_path"] = refp
        if os.path.exists(postp):
            row["post_path"] = postp
        # teardown: default restored BEFORE the sink it points at is unloaded
        if self.set_default and orig_default:
            row["restore_default"] = L.run(["pactl", "set-default-sink", orig_default], wall=5.0).rc
            row["default_after_restore"] = L.run(["pactl", "get-default-sink"], wall=5.0).out.strip()
        cli.cmd("unload-module %d" % var)
        cli.close()
        time.sleep(0.4)
        if sink.out.strip().isdigit():
            L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)
        time.sleep(0.3)
        row["valid"] = True
        row["loadavg_end"] = L.loadavg()
        row["leg_t1"] = time.strftime("%H:%M:%S", time.gmtime())
        return row


COND = {"name": "unset", "load": 0}


# ------------------------------------------------------------------ analysis

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
    values (the scout's plateau convention, reused verbatim for comparability)."""
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


def annotate(row):
    """Attach the plateau convention + cadence classes (whole leg and plateau)."""
    if not row.get("valid"):
        return row
    row["stats"] = stats(row["control"])
    st = row["stats"]
    row["cadence"] = L.cadence(row["control"])
    if st.get("plateau_t0") is not None:
        row["cadence_plateau"] = L.cadence_range(row["control"], st["plateau_t0"],
                                                 st["plateau_t1"])
    return row


def decay_30db(series):
    """Time from the end of the plateau run to the first value 30 dB below it."""
    vals = [v for _, v in series]
    st = stats(series)
    if "plateau" not in st or st["plateau"] <= -100:
        return None
    thr = st["plateau"] - 30.0
    start = st.get("plateau_t1")
    for t, v in series:
        if start is not None and t > start and math.isfinite(v) and v < thr:
            return round(t - start, 3)
    return None


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


def ebur_coeffs(rate=48000):
    """ITU-R BS.1770-4 K-weighting as a 5th-order cascade (libebur128 form)."""
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


def ref_momentary_plateau(x, rate=48000, win_s=0.4):
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
    return (10 * math.log10(best) - 0.691 if best > 0 else float("-inf")), bi


def ref_global(x, rate=48000, block_s=0.4, overlap=0.75, weight=1.0):
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


def ffmpeg_ebur128(path, wall=60.0):
    r = L.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path,
               "-af", "ebur128=peak=true", "-f", "null", "-"], wall=wall)
    lines = [l.strip() for l in r.err.splitlines() if "I:" in l]
    return {"rc": r.rc, "summary": lines[-1][:200] if lines else None}


WITNESS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ebur_witness2")


def libebur128_witness(path):
    """Independent witness: the INSTALLED libebur128's own integrated loudness
    on the same capture (full and silence-trimmed), via ebur_witness2.c."""
    if not os.path.exists(WITNESS):
        return {"error": "witness binary missing"}
    out = {}
    for mode in ("full", "trim"):
        r = L.run([WITNESS, path, mode], wall=30.0)
        m = re.search(r"I=(-?[\d.]+)", r.out)
        out[mode] = float(m.group(1)) if m else None
        out[mode + "_rc"] = r.rc
    return out


def ref_block(row, key="ref_path", rate=None):
    """Own reference on a capture. rate=None -> the capture's own rate (the
    graph rate that produced it); a mismatched rate is recorded separately."""
    p = row.get(key)
    if not p or not os.path.exists(p):
        return {}
    w = L.read_wav_any(p)
    r = w["rate"] if rate is None else rate
    pl, _ = ref_momentary_plateau(w["x"][0], rate=r)
    out = {"momentary": round(pl, 6), "global": ref_global(w["x"][0], rate=r),
           "libebur128": libebur128_witness(p), "ref_rate": r,
           "cap": capture_stats(p)}
    if r != 48000:
        pl48, _ = ref_momentary_plateau(w["x"][0], rate=48000)
        out["momentary_at_48000_coeffs"] = round(pl48, 6)
    return out


# -------------------------------------------------------------------- stimuli

def ensure_stimuli():
    want = {
        "tone_1000_050.wav": lambda: L.sine(1000, 3.5, amp=0.5),
        "tone_1000_050_44k.wav": lambda: L.sine(1000, 3.5, rate=44100, amp=0.5),
        "tone_1000_050_96k.wav": lambda: L.sine(1000, 3.5, rate=96000, amp=0.5),
        "tone_40_050.wav": lambda: L.sine(40, 3.5, amp=0.5),
        "tone_40_050_44k.wav": lambda: L.sine(40, 3.5, rate=44100, amp=0.5),
        "tone_4000_050.wav": lambda: L.sine(4000, 3.5, amp=0.5),
        "silence.wav": lambda: [0.0] * 168000,
    }
    for name, fn in want.items():
        p = os.path.join(SCRATCH, name)
        if not os.path.exists(p):
            L.write_wav_f32(p, fn())


def stim_path(name):
    return os.path.join(SCRATCH, name)


# --------------------------------------------------------------------- stages

def stage_recon(reps):
    out = {"stage": "recon", "reps": reps, "legs": []}
    out["host_before"] = {k: v for k, v in L.host_snapshot().items()
                          if k in ("own_nodes", "foreign_seat_nodes", "unseated_nodes")}
    out["foreign_procs"] = L.foreign_procs()
    out["loadavg_start"] = L.loadavg()
    out["settings_meta"] = L.run(["pw-metadata", "-n", "settings"], wall=6.0).out
    out["default_meta"] = L.run(["pw-metadata", "-n", "default"], wall=6.0).out
    stim = stim_path("tone_1000_050.wav")
    args = mkargs([EBU(), NODE("debug", "dbg")],
                  [link_spec("e:Momentary LUFS", "dbg:Control")],
                  ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
    row = Rig("recon_cal", args, stim=stim, capture_ref=True, dur=3.5, read_extra=1.4,
              enum_params=True, need_fc=True).run()
    if row.get("valid"):
        annotate(row)
        row["cadence"] = L.cadence(row["control"])
        row["ref"] = ref_block(row)
        row["props_has_lufs"] = bool(row.get("lufs_keys_in_props"))
    out["legs"].append(row)
    out["host_after"] = {k: v for k, v in L.host_snapshot().items()
                         if k in ("own_nodes", "foreign_seat_nodes")}
    out["loadavg_end"] = L.loadavg()
    return out


def stage_core(reps):
    """The scout's armed cells, replayed. One rep = one fresh process run."""
    out = {"stage": "core", "reps": reps, "legs": []}
    ensure_stimuli()
    tone = stim_path("tone_1000_050.wav")
    dm = ["e:In DUAL MONO"]
    dmout = ["e:Out DUAL MONO"]

    def add(tag, args, **kw):
        row = Rig(tag, args, **kw).run()
        row["rep"] = reps
        if row.get("valid"):
            annotate(row)
            row["cadence"] = L.cadence(row["control"])
            if row.get("ref_path"):
                row["ref"] = ref_block(row)
        out["legs"].append(row)
        return row

    def dbg(rd, port="DUAL MONO", outs=None):
        return mkargs([EBU(), NODE("debug", "dbg")],
                      [link_spec("e:%s" % rd, "dbg:Control")],
                      ["e:In %s" % port], outs or ["e:Out %s" % port])

    # C1/C2/C3: arm + read, calibration
    add("cal_mom", dbg("Momentary LUFS"), stim=tone, capture_ref=True)
    add("cal_glob", dbg("Global LUFS"), stim=tone, capture_ref=True)
    # C4: port map is dead
    add("port_UNUSED_mom", dbg("Momentary LUFS", "UNUSED"), stim=tone, capture_ref=True)
    add("port_FL_mom", dbg("Momentary LUFS", "FL"), stim=tone, capture_ref=True)
    add("port_SR_glob", dbg("Global LUFS", "SR"), stim=tone, capture_ref=True)
    # C5: dB-domain mean, no summation
    a = L.sine(1000, 3.5, amp=0.5)
    b = L.sine(1000, 3.5, amp=0.05)
    mixp = stim_path("st_fl05_fr005.wav")
    if not os.path.exists(mixp):
        L.write_wav_f32(mixp, list(zip(a, b)), ch=2)
    args = mkargs([EBU(), NODE("debug", "dbg")],
                  [link_spec("e:Momentary LUFS", "dbg:Control")],
                  ["e:In FL", "e:In FR"], ["e:Out FL", "e:Out FR"], ch=2,
                  position="[FL,FR]")
    add("mix_mom", args, ch=2, stim=mixp, dur=3.5, read_extra=3.0)
    # C6: one silent channel poisons Momentary
    sil = [0.0] * len(a)
    fson = stim_path("st_fl_tone_fr_sil.wav")
    if not os.path.exists(fson):
        L.write_wav_f32(fson, list(zip(a, sil)), ch=2)
    for rd in ("Momentary LUFS", "Global LUFS"):
        args = mkargs([EBU(), NODE("debug", "dbg")],
                      [link_spec("e:%s" % rd, "dbg:Control")],
                      ["e:In FL", "e:In FR"], ["e:Out FL", "e:Out FR"], ch=2,
                      position="[FL,FR]")
        add("st_flsil_%s" % rd.split()[0], args, ch=2, stim=fson, dur=3.5, read_extra=3.0)
    # C8/C9: notify-only modes
    for nm, rd in (("only_window", "Window LUFS"), ("only_peak", "Peak"),
                   ("only_range", "Range LU"), ("only_global", "Global LUFS")):
        add("modes_%s" % nm, dbg(rd), stim=tone, capture_post=True)
    # C9: peaks per port
    add("peak_mono_fl", dbg("Peak", "FL"), stim=tone)
    add("peak_mono_dm", dbg("Peak"), stim=tone)
    add("truepeak_mono_fl", dbg("True Peak", "FL"), stim=tone)
    add("truepeak_mono_dm", dbg("True Peak"), stim=tone)
    # C12: lufs2gain law (scout shape: l2g is type=ebur128; gain drives a linear node)
    def l2g_args(ctl):
        nodes = [EBU(), NODE("lufs2gain", "l2g", ctl=ctl, type_="ebur128"),
                 NODE("linear", "lin"), NODE("linear", "lin2"), NODE("debug", "dbg")]
        links = [link_spec("e:Momentary LUFS", "lin2:Control"),
                 link_spec("e:Global LUFS", "l2g:LUFS"),
                 link_spec("l2g:Gain", "lin:Mult"),
                 link_spec("l2g:Gain", "dbg:Control"),
                 link_spec("e:Out DUAL MONO", "lin:In")]
        return mkargs(nodes, links, dm, ["lin:Out"])

    r0 = add("l2g_default", l2g_args(None), stim=tone, capture_ref=True, capture_post=True)
    if r0.get("ref_path") and r0.get("post_path"):
        wr = L.read_wav_any(r0["ref_path"])["x"][0]
        wo = L.read_wav_any(r0["post_path"])["x"][0]
        n = min(len(wr), len(wo))
        seg = slice(n // 2, n // 2 + 48000)
        rr = math.sqrt(sum(v * v for v in wr[seg]) / 48000)
        ro = math.sqrt(sum(v * v for v in wo[seg]) / 48000)
        r0["audio_ratio"] = round(ro / rr, 6) if rr > 0 else None
    add("l2g_t0", l2g_args('"Target LUFS"=0'), stim=tone)
    add("l2g_m100", l2g_args('"Target LUFS"=-100'), stim=tone)
    add("l2g_silence", l2g_args(None), stim=stim_path("silence.wav"), dur=3.0, read_extra=1.0)
    # C12b: Global AND Gain in the same leg (removes cross-leg phase ambiguity)
    nodes = [EBU(), NODE("lufs2gain", "l2g", ctl='"Target LUFS"=0', type_="ebur128"),
             NODE("linear", "lin"), NODE("linear", "lin2"),
             NODE("debug", "dbg_gain"), NODE("debug", "dbg_glob")]
    links = [link_spec("e:Momentary LUFS", "lin2:Control"),
             link_spec("e:Global LUFS", "l2g:LUFS"),
             link_spec("l2g:Gain", "lin:Mult"),
             link_spec("l2g:Gain", "dbg_gain:Control"),
             link_spec("e:Global LUFS", "dbg_glob:Control"),
             link_spec("e:Out DUAL MONO", "lin:In")]
    r1 = add("l2g_check", mkargs(nodes, links, dm, ["lin:Out"]), stim=tone,
             capture_ref=True, dur=3.5, read_extra=1.5)
    if r1.get("valid"):
        vals = [v for _, v in r1["control"]]
        gains = [v for v in vals if math.isfinite(v) and v > 1.5]
        globs = [v for v in vals if math.isfinite(v) and v < 0]
        r1["gain_plateau"] = round(sorted(gains)[len(gains) // 2], 6) if gains else None
        r1["global_plateau"] = round(sorted(globs)[len(globs) // 2], 6) if globs else None
        if r1["gain_plateau"] and r1["global_plateau"]:
            r1["implied_global"] = round(-20 * math.log10(r1["gain_plateau"]), 6)
            r1["law_resid_db"] = round(20 * math.log10(r1["gain_plateau"])
                                       + r1["global_plateau"], 6)
    # C13: control-key grammar (verbatim raw shape, then the quoted repair)
    raw_unquoted = ('node.description=r93b_fc,'
                    'filter.graph={nodes=[{type=ebur128,name=e,label=ebur128},'
                    '{type=ebur128,name=l2g,label=lufs2gain,control={Target LUFS=-100}},'
                    '{type=builtin,name=dbg,label=debug}],'
                    'links=[{output="e:Global LUFS",input="l2g:LUFS"},'
                    '{output="l2g:Gain",input="dbg:Control"}],'
                    'inputs=["e:In DUAL MONO"],outputs=["e:Out DUAL MONO"]},'
                    'audio.channels=1,audio.position=[MONO],'
                    'capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},'
                    'playback.props={node.name=%s,node.autoconnect=false}' % (FC_IN, FC_OUT))
    add("ctl_raw_unquoted", raw_unquoted, stim=tone, dur=2.0, read_extra=1.0)
    add("ctl_quoted", raw_unquoted.replace('control={Target LUFS=-100}',
                                           'control={"Target LUFS"=-100}'),
        stim=tone, dur=2.0, read_extra=1.0)
    # C7: relative gate (loud/quiet/loud)
    loud = L.sine(1000, 2.0, amp=0.5)
    quiet = L.sine(1000, 2.0, amp=0.005)
    prog = stim_path("prog_loud_quiet_loud.wav")
    if not os.path.exists(prog):
        L.write_wav_f32(prog, loud + quiet + loud)
    add("gate_global", dbg("Global LUFS"), stim=prog, dur=6.0, read_extra=1.5, capture_ref=True)
    # C15: bit-exact passthrough
    pt = add("passthrough", dbg("Momentary LUFS"), stim=tone, capture_ref=True,
             capture_post=True)
    if pt.get("ref_path") and pt.get("post_path"):
        wr = L.read_wav_any(pt["ref_path"])["x"][0]
        wo = L.read_wav_any(pt["post_path"])["x"][0]

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
        pt["align"] = {"lag": lag, "best_lag": best[0] if best else None,
                       "max_abs_diff": round(best[1], 9) if best else None,
                       "ref_frames": len(wr), "post_frames": len(wo)}
    return out


def stage_window(reps, cfgs=(None, "max-window=0.05", "max-window=0.4",
                             "max-window=1.0", "max-window=2.0", "max-window=5.0")):
    out = {"stage": "window", "reps": reps, "legs": []}
    ensure_stimuli()
    tone = stim_path("tone_1000_050.wav")
    for cfg in cfgs:
        nodes = [EBU(cfg=cfg), NODE("linear", "lin"), NODE("debug", "dbg")]
        links = [link_spec("e:Momentary LUFS", "lin:Control"),
                 link_spec("e:Window LUFS", "dbg:Control")]
        args = mkargs(nodes, links, ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        row = Rig("win_%s" % (cfg or "default"), args, stim=tone, dur=3.5, read_extra=4.0).run()
        row["rep"] = reps
        row["cfg"] = cfg
        if row.get("valid"):
            annotate(row)
            row["cadence"] = L.cadence(row["control"])
            row["decay_30db_s"] = decay_30db(row["control"])
            row["cfg_window_s"] = (float(cfg.split("=")[1]) if cfg else None)
        out["legs"].append(row)
    return out


def stage_history(reps):
    out = {"stage": "history", "reps": reps, "legs": []}
    ensure_stimuli()
    b1 = L.sine(1000, 1.5, amp=0.5)
    sil = [0.0] * int(5.0 * 48000)
    prog = stim_path("prog_burst_silence.wav")
    if not os.path.exists(prog):
        L.write_wav_f32(prog, b1 + sil)
    for cfg in (None, "max-history=2.0"):
        args = mkargs([EBU(cfg=cfg), NODE("linear", "lin"), NODE("debug", "dbg")],
                      [link_spec("e:Momentary LUFS", "lin:Control"),
                       link_spec("e:Global LUFS", "dbg:Control")],
                      ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        row = Rig("hist_%s" % (cfg or "default"), args, stim=prog, dur=6.5,
                  read_extra=2.0, capture_ref=True).run()
        row["rep"] = reps
        row["cfg"] = cfg
        if row.get("valid"):
            annotate(row)
            ser = row["control"]
            fin = [v for t, v in ser if math.isfinite(v)]
            row["first_finite"] = round(fin[0], 6) if fin else None
            row["last_finite"] = round(fin[-1], 6) if fin else None
            row["hold_drift"] = (round(fin[-1] - fin[0], 6) if len(fin) > 1 else None)
            if row.get("ref_path"):
                row["ref"] = ref_block(row)
        out["legs"].append(row)
    return out


def stage_hist2(reps):
    out = {"stage": "hist2", "reps": reps, "legs": []}
    ensure_stimuli()
    b1 = L.sine(1000, 2.5, amp=0.5)
    sil = [0.0] * int(1.5 * 48000)
    b2 = L.sine(1000, 2.5, amp=0.25)
    prog = stim_path("prog_burst_quiet.wav")
    if not os.path.exists(prog):
        L.write_wav_f32(prog, b1 + sil + b2)
    for cfg in (None, "max-history=2.0"):
        args = mkargs([EBU(cfg=cfg), NODE("linear", "lin"), NODE("debug", "dbg")],
                      [link_spec("e:Momentary LUFS", "lin:Control"),
                       link_spec("e:Global LUFS", "dbg:Control")],
                      ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        row = Rig("hist2_%s" % (cfg or "default"), args, stim=prog, dur=6.5,
                  read_extra=2.0, capture_ref=True).run()
        row["rep"] = reps
        row["cfg"] = cfg
        if row.get("valid"):
            annotate(row)
            ser = row["control"]

            def segmean(a, b):
                vs = [v for t, v in ser if a <= t < b and math.isfinite(v)]
                return round(sum(vs) / len(vs), 4) if vs else None
            row["seg"] = {"b1": segmean(1.5, 2.5), "b2": segmean(5.5, 6.5)}
            if row.get("ref_path"):
                row["ref"] = ref_block(row)
        out["legs"].append(row)
    return out


def stage_labels(reps, labels=("debug", "busy", "sqrt", "ramp", "zeroramp",
                               "null", "avg", "sum", "gain", "nop")):
    out = {"stage": "labels", "reps": reps, "legs": []}
    ensure_stimuli()
    tone = stim_path("tone_1000_050.wav")
    for lab in labels:
        nodes = [EBU(), NODE(lab, "t1")]
        args = mkargs(nodes, [], ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        row = Rig("label_%s" % lab, args, stim=tone if lab in ("debug",) else None,
                  dur=1.0, read_extra=0.2).run()
        row["rep"] = reps
        row["label"] = lab
        row["load_ok"] = row.get("load_ok")
        out["legs"].append(row)
    return out


def stage_ref(reps):
    """Independent cross-witness: ffmpeg ebur128 on the captured pre-tap, own
    reference, and the plugin's Global in the same leg."""
    out = {"stage": "ref", "reps": reps, "legs": []}
    ensure_stimuli()
    tone = stim_path("tone_1000_050.wav")
    args = mkargs([EBU(), NODE("debug", "dbg")],
                  [link_spec("e:Global LUFS", "dbg:Control")],
                  ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
    row = Rig("ref_glob", args, stim=tone, capture_ref=True, dur=3.5, read_extra=1.5).run()
    row["rep"] = reps
    if row.get("valid"):
        annotate(row)
        row["cadence"] = L.cadence(row["control"])
        if row.get("ref_path"):
            row["ref"] = ref_block(row)
            row["ffmpeg"] = ffmpeg_ebur128(row["ref_path"])
    out["legs"].append(row)
    out["ffmpeg_stimulus"] = ffmpeg_ebur128(tone)
    return out


def stage_rate(reps):
    """Rate axis: stimulus rate, null-sink rate, and (one leg) a forced graph rate."""
    out = {"stage": "rate", "reps": reps, "legs": []}
    ensure_stimuli()
    arms = [
        ("stim_44k_sink48k", stim_path("tone_1000_050_44k.wav"), None, "Momentary LUFS"),
        ("stim_96k_sink48k", stim_path("tone_1000_050_96k.wav"), None, "Momentary LUFS"),
        ("stim_48k_sink44k", stim_path("tone_1000_050.wav"), 44100, "Momentary LUFS"),
        ("stim_48k_sink96k", stim_path("tone_1000_050.wav"), 96000, "Momentary LUFS"),
        ("f40_stim48k_sink44k", stim_path("tone_40_050.wav"), 44100, "Momentary LUFS"),
        ("f40_stim44k_sink44k", stim_path("tone_40_050_44k.wav"), 44100, "Momentary LUFS"),
    ]
    for tag, stim, srate, rd in arms:
        args = mkargs([EBU(), NODE("debug", "dbg")],
                      [link_spec("e:%s" % rd, "dbg:Control")],
                      ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        row = Rig(tag, args, stim=stim, sink_rate=srate, capture_ref=True,
                  dur=3.5, read_extra=1.5, need_fc=True, enum_params=True).run()
        row["rep"] = reps
        row["arm"] = tag
        row["sink_rate_arg"] = srate
        if row.get("valid"):
            annotate(row)
            row["cadence"] = L.cadence(row["control"])
            if row.get("ref_path"):
                w = L.read_wav_any(row["ref_path"])
                row["ref"] = ref_block(row)
                # own reference at both candidate rates (fingerprint of the
                # rate the filter actually ran at)
                for r in (44100, 48000, 96000):
                    pl, _ = ref_momentary_plateau(w["x"][0], rate=r)
                    row["ref_mom_at_%d" % r] = round(pl, 6)
        out["legs"].append(row)
    return out


def stage_quantum(reps):
    """clock.force-quantum axis. Ambient value is read first and restored exactly."""
    out = {"stage": "quantum", "reps": reps, "legs": []}
    ensure_stimuli()
    tone = stim_path("tone_1000_050.wav")
    meta0 = L.run(["pw-metadata", "-n", "settings"], wall=6.0).out
    out["settings_before"] = meta0
    cur = None
    for l in meta0.splitlines():
        if "clock.force-quantum" in l:
            cur = l.split("value:")[1].strip().strip("'")
    out["force_quantum_before"] = cur
    for qv in (None, "1024", "2048"):
        if qv is not None:
            L.run(["pw-metadata", "-n", "settings", "0", "clock.force-quantum", qv], wall=6.0)
            time.sleep(0.5)
        args = mkargs([EBU(), NODE("debug", "dbg")],
                      [link_spec("e:Momentary LUFS", "dbg:Control")],
                      ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        row = Rig("quantum_%s" % (qv or "ambient"), args, stim=tone,
                  capture_ref=True, dur=3.5, read_extra=1.5, need_fc=True,
                  enum_params=True).run()
        row["rep"] = reps
        row["force_quantum"] = qv
        row["settings_during"] = [l.strip()[:120] for l in
                                  L.run(["pw-metadata", "-n", "settings"], wall=6.0).out.splitlines()
                                  if "quantum" in l]
        if row.get("valid"):
            annotate(row)
            row["cadence"] = L.cadence(row["control"])
            if row.get("ref_path"):
                row["ref"] = ref_block(row)
        out["legs"].append(row)
    # restore exactly
    if cur is not None:
        L.run(["pw-metadata", "-n", "settings", "0", "clock.force-quantum", cur], wall=6.0)
    out["settings_after"] = L.run(["pw-metadata", "-n", "settings"], wall=6.0).out
    return out


def stage_flags(reps):
    """CLI flag-order / argv-shape axis: does any measured law depend on it?"""
    out = {"stage": "flags", "reps": reps, "legs": []}
    ensure_stimuli()
    tone = stim_path("tone_1000_050.wav")
    dm = ["e:In DUAL MONO"]
    dmout = ["e:Out DUAL MONO"]
    base = mkargs([EBU(), NODE("debug", "dbg")],
                  [link_spec("e:Momentary LUFS", "dbg:Control")], dm, dmout)

    def add(tag, arm, **kw):
        row = Rig(tag, kw.pop("args", base), **kw).run()
        row["rep"] = reps
        row["arm"] = arm
        if row.get("valid"):
            annotate(row)
            row["cadence"] = L.cadence(row["control"])
            if row.get("ref_path"):
                row["ref"] = ref_block(row)
        out["legs"].append(row)
        return row

    add("flags_args_channels_first", "module arg order: audio.channels first", stim=tone,
        args=mkargs([EBU(), NODE("debug", "dbg")],
                    [link_spec("e:Momentary LUFS", "dbg:Control")], dm, dmout,
                    order="channels_first"))
    add("flags_play_target_first", "pw-play --target before file", stim=tone,
        play_argv_shape="target_first", capture_ref=True)
    add("flags_play_file_first", "pw-play file before --target", stim=tone,
        play_argv_shape="file_first", capture_ref=True)
    add("flags_link_reversed", "pw-link operands reversed", stim=tone, link_order="reversed")
    add("flags_record_default", "pw-record flags before path", stim=tone, capture_ref=True)
    add("flags_record_path_first", "pw-record path before flags", stim=tone,
        capture_ref=True, rec_argv_shape="path_first")
    return out


def stage_defaults(reps):
    """Default-node state axis. Ambient default read, own sink made default for
    one leg, then restored and verified; source default untouched."""
    out = {"stage": "defaults", "reps": reps, "legs": []}
    ensure_stimuli()
    tone = stim_path("tone_1000_050.wav")
    out["default_sink_before"] = L.run(["pactl", "get-default-sink"], wall=5.0).out.strip()
    out["default_source_before"] = L.run(["pactl", "get-default-source"], wall=5.0).out.strip()
    out["default_meta_before"] = L.run(["pw-metadata", "-n", "default"], wall=6.0).out
    base = mkargs([EBU(), NODE("debug", "dbg")],
                  [link_spec("e:Momentary LUFS", "dbg:Control")],
                  ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
    row = Rig("default_ambient", base, stim=tone, capture_ref=True).run()
    row["rep"] = reps
    row["arm"] = "ambient default (foreign SPDIF sink)"
    if row.get("valid"):
        annotate(row)
        row["ref"] = ref_block(row)
    out["legs"].append(row)
    row = Rig("default_own_sink", base, stim=tone, capture_ref=True, set_default=True).run()
    row["rep"] = reps
    row["arm"] = "default sink = own r93b_in null sink"
    if row.get("valid"):
        annotate(row)
        row["ref"] = ref_block(row)
    out["legs"].append(row)
    out["default_sink_after"] = L.run(["pactl", "get-default-sink"], wall=5.0).out.strip()
    out["default_source_after"] = L.run(["pactl", "get-default-source"], wall=5.0).out.strip()
    out["default_meta_after"] = L.run(["pw-metadata", "-n", "default"], wall=6.0).out
    return out


def stage_freq(reps, freqs=(40, 100, 1000, 4000, 10000)):
    """K-weighting transfer ladder (scout shape: mono DUAL MONO, Momentary)."""
    out = {"stage": "freq", "reps": reps, "legs": []}
    ensure_stimuli()
    for f in freqs:
        stim = stim_path("tone_%d_050.wav" % f)
        if not os.path.exists(stim):
            L.write_wav_f32(stim, L.sine(f, 3.5, amp=0.5))
        args = mkargs([EBU(), NODE("debug", "dbg")],
                      [link_spec("e:Momentary LUFS", "dbg:Control")],
                      ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        row = Rig("freq_%d" % f, args, stim=stim, capture_ref=True, dur=3.5,
                  read_extra=1.5).run()
        row["rep"] = reps
        row["freq"] = f
        if row.get("valid"):
            annotate(row)
            if row.get("ref_path"):
                row["ref"] = ref_block(row)
        out["legs"].append(row)
    return out


def stage_amp(reps, amps=(1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125)):
    """Amplitude ladder vs own reference (scout shape)."""
    out = {"stage": "amp", "reps": reps, "legs": []}
    ensure_stimuli()
    for a in amps:
        stim = stim_path("tone_1000_a%05d.wav" % int(a * 100000))
        if not os.path.exists(stim):
            L.write_wav_f32(stim, L.sine(1000, 3.5, amp=a))
        for rd in (("Momentary LUFS",) + (("Global LUFS",) if a in (0.5, 0.125, 0.03125) else ())):
            args = mkargs([EBU(), NODE("debug", "dbg")],
                          [link_spec("e:%s" % rd, "dbg:Control")],
                          ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
            row = Rig("amp_%d_%s" % (int(a * 1000), rd.split()[0]), args, stim=stim,
                      capture_ref=True, dur=3.5, read_extra=1.5).run()
            row["rep"] = reps
            row["amp"] = a
            row["readout"] = rd
            if row.get("valid"):
                annotate(row)
                if row.get("ref_path"):
                    row["ref"] = ref_block(row)
            out["legs"].append(row)
    return out




def _meta_get(txt, key):
    m = re.search(r"key:'%s' value:'([^']*)'" % re.escape(key), txt)
    return m.group(1) if m else None


def stage_frate(reps, rates=(44100, 96000)):
    """Graph-rate axis via clock.force-rate + clock.allowed-rates, restored
    exactly (both keys verified after). Bounded window: one 1 kHz leg per rate
    plus one 40 Hz leg at the first rate."""
    out = {"stage": "frate", "reps": reps, "legs": []}
    ensure_stimuli()
    tone = stim_path("tone_1000_050.wav")
    f40 = stim_path("tone_40_050.wav")
    meta0 = L.run(["pw-metadata", "-n", "settings"], wall=6.0).out
    out["settings_before"] = meta0
    allowed0 = _meta_get(meta0, "clock.allowed-rates")
    frate0 = _meta_get(meta0, "clock.force-rate")
    out["allowed_rates_before"] = allowed0
    out["force_rate_before"] = frate0

    def legs_for(rate, stim, tag):
        args = mkargs([EBU(), NODE("debug", "dbg")],
                      [link_spec("e:Momentary LUFS", "dbg:Control")],
                      ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
        row = Rig(tag, args, stim=stim, capture_ref=True, dur=3.5, read_extra=1.5,
                  need_fc=True, enum_params=True).run()
        row["rep"] = reps
        row["forced_rate"] = rate
        if row.get("valid"):
            annotate(row)
            if row.get("ref_path"):
                row["ref"] = ref_block(row)
        out["legs"].append(row)

    try:
        L.run(["pw-metadata", "-n", "settings", "0", "clock.allowed-rates",
               "[ 44100 48000 96000 ]"], wall=6.0)
        for rate in rates:
            L.run(["pw-metadata", "-n", "settings", "0", "clock.force-rate",
                   str(rate)], wall=6.0)
            time.sleep(1.0)
            legs_for(rate, tone, "frate_%d_1k" % rate)
            if rate == rates[0]:
                legs_for(rate, f40, "frate_%d_40" % rate)
    finally:
        if allowed0:
            L.run(["pw-metadata", "-n", "settings", "0", "clock.allowed-rates",
                   allowed0], wall=6.0)
        if frate0 is not None:
            L.run(["pw-metadata", "-n", "settings", "0", "clock.force-rate", frate0],
                  wall=6.0)
    meta1 = L.run(["pw-metadata", "-n", "settings"], wall=6.0).out
    out["settings_after"] = meta1
    out["allowed_rates_after"] = _meta_get(meta1, "clock.allowed-rates")
    out["force_rate_after"] = _meta_get(meta1, "clock.force-rate")
    out["restored"] = (out["allowed_rates_after"] == allowed0
                       and out["force_rate_after"] == frate0)
    return out



def stage_ports(reps):
    """C1 replay: the module's own port inventory, from its full load log."""
    out = {"stage": "ports", "reps": reps, "legs": []}
    ensure_stimuli()
    tone = stim_path("tone_1000_050.wav")
    args = mkargs([EBU(), NODE("debug", "dbg")],
                  [link_spec("e:Momentary LUFS", "dbg:Control")],
                  ["e:In DUAL MONO"], ["e:Out DUAL MONO"])
    sink = L.run(["pactl", "load-module", "module-null-sink",
                  "sink_name=%s" % NS, "channels=1"], wall=6.0)
    time.sleep(0.3)
    cli = L.PwCli(env={"PIPEWIRE_DEBUG": "3"}, idle=0.6, hard=6.0)
    load_out, var = cli.load("libpipewire-module-filter-chain", args)
    time.sleep(0.8)
    row = {"tag": "ports_recon", "valid": var is not None, "fc_var": var,
           "sink": sink.out.strip(), "load_len": len(load_out),
           "port_inventory": [l.strip()[:200] for l in load_out.splitlines()
                              if "n_input" in l][:6],
           "notify_ports": sorted({l.split("port.name =")[1].strip().strip('"')
                                   for l in load_out.splitlines() if "port.name =" in l
                                   and ("LUFS" in l or "Peak" in l or "Range" in l)}),
           "input_ports": sorted({l.split("port.name =")[1].strip().strip('"')
                                  for l in load_out.splitlines() if "port.name =" in l
                                  and "In " in l}),
           "port_lines": [l.strip()[:160] for l in load_out.splitlines()
                          if "port.name =" in l][:60]}
    cli.cmd("unload-module %d" % var)
    cli.close()
    time.sleep(0.3)
    if sink.out.strip().isdigit():
        L.run(["pactl", "unload-module", sink.out.strip()], wall=6.0)
    out["legs"].append(row)
    return out

STAGES = {
    "recon": stage_recon, "ports": stage_ports, "core": stage_core, "window": stage_window,
    "history": stage_history, "hist2": stage_hist2, "labels": stage_labels,
    "ref": stage_ref, "rate": stage_rate, "quantum": stage_quantum,
    "flags": stage_flags, "defaults": stage_defaults, "freq": stage_freq,
    "amp": stage_amp, "frate": stage_frate,
}


# Exact seat tokens. A substring sweep is forbidden (r95 incident / r82 F4):
# the sibling lanes are r95b_*, r96b_*, r98b_* and at least one foreign tool
# uses an /tmp path containing "r93b" (game-dev battery), so "r93b" alone is
# NOT a safe selector.
OWN_TOKENS = ("r93b_in", "r93b_fc_in", "r93b_fc_out", "r93b_ref", "r93b_rec",
              "r93b_hogrec", "r93b_fc,", "r93b_hog.py")


def _own_line(line):
    return any(t in line for t in OWN_TOKENS)


def preflight():
    """Own-namespace preflight: kill only my own leaked children (exact token),
    unload only modules whose short listing carries an exact r93b_* token."""
    stray = []
    for l in L.run(["ps", "-eo", "pid,args"], wall=5.0).out.splitlines():
        if not _own_line(l):
            continue
        cmd = l.strip().split(None, 1)[-1]
        if cmd.startswith(("pw-", "pipewire", "pactl")) or "r93b_hog.py" in cmd:
            stray.append(l.strip()[:140])
    killed = []
    for l in stray:
        try:
            os.kill(int(l.split()[0]), 9)
            killed.append(l.split()[0])
        except Exception:
            pass
    mods = [l.split()[0] for l in L.run(["pactl", "list", "modules", "short"],
                                        wall=6.0).out.splitlines() if _own_line(l)]
    for m in mods:
        L.run(["pactl", "unload-module", m], wall=6.0)
    time.sleep(0.3)
    return {"stray": stray, "killed": killed, "modules_unloaded": mods,
            "selector": list(OWN_TOKENS)}


def sweep():
    """Own-namespace sweep: exact-token selector only; foreign modules and
    foreign seat nodes are listed, never touched."""
    lines = L.run(["pactl", "list", "modules", "short"], wall=6.0).out.splitlines()
    mods = [l.split()[0] for l in lines if _own_line(l)]
    for m in mods:
        L.run(["pactl", "unload-module", m], wall=6.0)
    time.sleep(0.4)
    snap = L.host_snapshot()
    nodes = [n for n in snap.get("own_nodes", []) if any(t in n for t in OWN_TOKENS)]
    procs = [l.strip()[:120] for l in L.run(["ps", "-eo", "pid,args"], wall=5.0).out.splitlines()
             if _own_line(l) and (l.strip().split(None, 1)[-1].startswith(("pw-", "pipewire", "pactl"))
                                  or "r93b_hog.py" in l)]
    foreign_mods = [l.strip()[:100] for l in lines if not _own_line(l) and "r9" in l]
    return {"modules_left": mods, "nodes_left": nodes, "procs_left": procs,
            "foreign_seat_nodes": snap.get("foreign_seat_nodes"),
            "foreign_modules_seen": foreign_mods[:10],
            "selector": list(OWN_TOKENS),
            "clean": not (mods or nodes or procs)}


def main():
    stage = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    args = sys.argv[3:]
    load_n = 0
    if "--load" in args:
        load_n = int(args[args.index("--load") + 1])
    cond = "load%d" % load_n if load_n else "quiet"
    if "--cond" in args:
        cond = args[args.index("--cond") + 1]
    COND["name"] = cond
    COND["load"] = load_n
    res = {"toolchain": {"pipewire": L.run(["pipewire", "--version"], wall=5.0).out.strip(),
                         "libebur128": "1.2.6", "python": sys.version.split()[0]},
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "cond": cond, "load_requested": load_n,
           "preflight": preflight(),
           "loadavg_pre": L.loadavg(),
           "host_pre": {k: v for k, v in L.host_snapshot().items()
                        if k in ("own_nodes", "foreign_seat_nodes", "unseated_nodes")}}
    hogs = None
    if load_n:
        hogs = Hogs(n_cpu=load_n, n_audio=2, dur=1800.0)
        res["hogs_start"] = hogs.start()
        time.sleep(3.0)
        res["hogs_state"] = hogs.state()
    ensure_stimuli()
    t0 = time.time()
    try:
        res.update(STAGES[stage](reps))
    finally:
        if hogs is not None:
            res["hogs_stop"] = hogs.stop()
    res["sweep"] = sweep()
    res["loadavg_post"] = L.loadavg()
    res["wall_s"] = round(time.time() - t0, 1)
    path = os.path.join(REC, "%s_%s_r%d.json" % (stage, cond, reps))
    L.jdump(path, res)
    legs = res.get("legs", [])
    ok = sum(1 for r in legs if r.get("valid"))
    print("%s[%s r%d]: legs=%d valid=%d sweep_clean=%s wall=%.1fs -> %s"
          % (stage, cond, reps, len(legs), ok, res["sweep"]["clean"], res["wall_s"], path))
    for r in legs:
        st = r.get("stats") or {}
        cp = (r.get("cadence_plateau") or {})
        print("  %-28s %-14s plateau=%-12s nan=%-4s inf=%-4s plcad=%-8s" % (
            r.get("tag"), (r.get("readout") or r.get("arm") or ""), st.get("plateau"),
            st.get("n_nan"), st.get("n_inf"), cp.get("frames_at_48k")))


if __name__ == "__main__":
    main()
