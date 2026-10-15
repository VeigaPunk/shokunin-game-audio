#!/usr/bin/env python3
"""r100b — boundary rig for the r100 sofa/spatializer surface (seat: audio r100-boundary).

Namespace `r100b_*` only. Own PIDs only. Never touches foreign objects (r95 sweep
incident precedent): every sweep is filtered on the `r100b` token, and the process
sweep additionally requires a known PipeWire tool in argv[0] (comm).

Reuses the r92-scout `pwlib` read-only (the same helper the r100 scout imported):
bounded children (wall+byte caps, own session, RLIMIT_CORE=0), WAV I/O, Goertzel.

This rig is a superset of the scout's `sofa_probe.py`:
  * same arming shape (null sink driver, pw-cli-loaded filter chain, pw-record post tap)
  * fresh process per leg; per-leg loadavg + hog census
  * axis knobs: argv token order, control order, rate, quantum (sandbox), sibling
    presence, channel swap, reference tap, runtime control change, source loss,
    relink timing, driver drop, extra config keys
"""
import importlib.util
import json
import math
import os
import re
import signal
import subprocess
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # corpus/live/r100-boundary
R92P = os.path.join(os.path.dirname(HERE), "r92-scout", "probes")
_spec = importlib.util.spec_from_file_location("pwlib", os.path.join(R92P, "pwlib.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)

SCRATCH = os.path.join(HERE, "scratch")
RUNS = os.path.join(HERE, "runs")
REC = os.path.join(HERE, "receipts")
RAW = os.path.join(HERE, "raw")
for d in (SCRATCH, RUNS, REC, RAW):
    os.makedirs(d, exist_ok=True)

SOFA = "/usr/share/libmysofa/MIT_KEMAR_normal_pinna.sofa"
DEFAULT_SOFA = "/usr/share/libmysofa/default.sofa"

SINK_IN = "r100b_in"
NS_REC = "r100b_rec"
NS_REF = "r100b_ref"
NS_PLAY = "r100b_play"
FC_IN = "r100b_sofa_in"
FC_OUT = "r100b_sofa_out"
SIB_IN = "r100b_sib_in"
SIB_OUT = "r100b_sib_out"
TOOL_PREFIX = ("pw-play", "pw-record", "pw-cli", "pw-link", "pw-dump", "pw-cat",
               "pactl", "pipewire", "mysofa2json", "spa-json-dump")


# --------------------------------------------------------------- host census
def loadavg():
    with open("/proc/loadavg") as f:
        p = f.read().split()
    return {"l1": float(p[0]), "l5": float(p[1]), "l15": float(p[2]),
            "running": p[3], "lastpid": p[4]}


def _proc_census():
    """Observation only — foreign processes are counted, never signalled."""
    own, foreign = [], []
    try:
        out = L.run(["ps", "-eo", "pid,comm,args"], wall=8.0).out
    except Exception:
        return {"own": own, "foreign": foreign}
    for line in out.splitlines()[1:]:
        parts = line.strip().split(None, 2)
        if len(parts) < 3:
            continue
        pid, comm, args = parts
        if comm in ("yes", "r93b_hog", "r93b_hog.py") or "hog" in comm:
            foreign.append({"pid": pid, "comm": comm})
        if args.startswith(TOOL_PREFIX) and "r100b" in args:
            own.append({"pid": pid, "comm": comm, "args": args[:120]})
    return {"own": own, "foreign": foreign}


def live():
    """Namespace-scoped census of this seat's objects (r100b only)."""
    nodes, states, foreign_nodes = [], {}, []
    try:
        for o in json.loads(L.run(["pw-dump"], wall=10.0).out):
            if not str(o.get("type", "")).startswith("PipeWire:Interface:Node"):
                continue
            info = o.get("info", {})
            nm = info.get("props", {}).get("node.name", "")
            if nm.startswith("r100b"):
                nodes.append(nm)
                states[nm] = info.get("state")
            elif re.match(r"r\d+[a-z]?_", str(nm)):
                foreign_nodes.append(nm)
    except Exception:
        pass
    mods, foreign_mods = [], []
    try:
        for line in L.run(["pactl", "list", "modules", "short"], wall=8.0).out.splitlines():
            if "r100b" in line:
                mods.append(line.split()[0])
            elif re.search(r"r\d+[a-z]?_", line):
                foreign_mods.append(line.split()[0])
    except Exception:
        pass
    pc = _proc_census()
    return {"nodes": sorted(nodes), "node_states": states, "modules": sorted(mods),
            "procs": pc["own"],
            "foreign_nodes": sorted(foreign_nodes)[:40],
            "foreign_modules": sorted(foreign_mods)[:20],
            "foreign_hogs": len(pc["foreign"])}


def clock_witness():
    """Live graph clock witness (r98 could not capture the instant of a rate flip)."""
    res = {"core": {}, "drivers": []}
    try:
        rr = L.run(["pw-cli", "info", "0"], wall=20.0)
        txt = rr.out
        res["core_rc"] = rr.rc
        res["core_len"] = len(txt)
        res["core_timed_out"] = rr.timed_out
        for line in txt.splitlines():
            s = line.strip().lstrip("*").strip()
            for k in ("default.clock.rate", "default.clock.quantum",
                      "default.clock.allowed-rates", "clock.power-of-two-quantum",
                      "settings.check-rate", "settings.check-quantum"):
                if s.startswith(k):
                    res["core"][k] = s.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    try:
        for o in json.loads(L.run(["pw-dump"], wall=10.0).out):
            if not str(o.get("type", "")).startswith("PipeWire:Interface:Node"):
                continue
            info = o.get("info", {})
            p = info.get("props", {})
            if p.get("node.driver") in (True, "true") or p.get("node.name") == SINK_IN:
                res["drivers"].append({"name": p.get("node.name"), "state": info.get("state"),
                                       "clock.rate": p.get("clock.rate"),
                                       "clock.quantum": p.get("clock.quantum"),
                                       "node.driver": p.get("node.driver")})
    except Exception:
        pass
    return res


def sweep():
    """Unload/kill only r100b objects (own namespace). Foreign objects are never touched."""
    before = live()
    for m in before["modules"]:
        L.run(["pactl", "unload-module", m], wall=8.0)
    killed = []
    for p in before["procs"]:
        try:
            os.kill(int(p["pid"]), signal.SIGKILL)
            killed.append(p["pid"])
        except Exception:
            pass
    time.sleep(0.6)
    after = live()
    return {"before": before, "killed": killed, "after": after,
            "clean": not (after["nodes"] or after["modules"] or after["procs"])}


def census():
    c = live()
    c["loadavg"] = loadavg()
    c["utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return c


# ------------------------------------------------------------------- modules
def sink_load(name, channels, rate):
    extra = ("channels=%d rate=%d sink_properties=state.restore-props=false"
             % (channels, rate))
    out = L.run(["pactl", "load-module", "module-null-sink",
                 "sink_name=%s" % name, extra], wall=8.0)
    mid = None
    try:
        mid = int(out.out.strip().split()[-1])
    except Exception:
        pass
    return {"argv": out.argv, "rc": out.rc, "out": out.out.strip(), "id": mid}


def sink_unload(name, expect_id):
    lst = L.run(["pactl", "list", "modules", "short"], wall=8.0).out
    cand = [int(l.split()[0]) for l in lst.splitlines()
            if "module-null-sink" in l and ("sink_name=%s" % name) in l]
    if expect_id not in cand:
        return {"rc": None, "note": "id-not-found", "cand": cand}
    out = L.run(["pactl", "unload-module", str(expect_id)], wall=8.0)
    return {"rc": out.rc, "out": out.out.strip()}


class Bg:
    def __init__(self, argv, wall=10.0, env=None):
        self.argv = argv
        self.wall = wall
        e = dict(os.environ)
        if env:
            e.update(env)
        self.p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.DEVNULL, start_new_session=True,
                                  preexec_fn=L._ncore, env=e)

    def stop(self, sig=signal.SIGTERM):
        try:
            os.killpg(os.getpgid(self.p.pid), sig)
        except ProcessLookupError:
            pass
        try:
            out, err = self.p.communicate(timeout=4)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = self.p.communicate()
        return {"argv": self.argv, "rc": self.p.returncode,
                "out": out.decode("utf-8", "replace")[-600:],
                "err": err.decode("utf-8", "replace")[-600:]}


def link(a, b, tries=12, env=None):
    last = None
    for i in range(tries):
        r = L.run(["pw-link", a, b], wall=5.0, env=env)
        last = r
        if r.rc == 0:
            return {"argv": [a, b], "rc": 0, "tries": i + 1}
        if "File exists" in r.err:
            return {"argv": [a, b], "rc": 0, "tries": i + 1, "note": "already"}
        time.sleep(0.25)
    return {"argv": [a, b], "rc": last.rc, "err": last.err.strip()[-200:], "tries": tries}


def unlink(a, b, env=None):
    r = L.run(["pw-link", "-d", a, b], wall=5.0, env=env)
    return {"argv": ["-d", a, b], "rc": r.rc, "err": r.err.strip()[-160:]}


def ports_of(node_name, env=None):
    out = L.run(["pw-link", "-o"], wall=6.0, env=env).out + L.run(["pw-link", "-i"], wall=6.0, env=env).out
    return sorted(l.strip() for l in out.splitlines() if node_name in l)


def node_id(name, env=None):
    try:
        for o in json.loads(L.run(["pw-dump"], wall=10.0, env=env).out):
            if str(o.get("type", "")).startswith("PipeWire:Interface:Node"):
                if o.get("info", {}).get("props", {}).get("node.name") == name:
                    return o.get("id")
    except Exception:
        pass
    return None


def enum_props(name, save=None, env=None):
    nid = node_id(name, env=env)
    if nid is None:
        return {"node": name, "id": None}
    out = L.run(["pw-cli", "enum-params", str(nid), "Props"], wall=8.0, env=env)
    txt = out.out.strip()
    res = {"node": name, "id": nid, "rc": out.rc, "bytes": len(txt),
           "has_azimuth": "Azimuth" in txt, "has_elevation": "Elevation" in txt,
           "has_radius": "Radius" in txt}
    if save:
        with open(save, "w") as f:
            f.write(txt)
        res["raw"] = save
    # keep the spatializer control block (if the param exposes one)
    lines = txt.splitlines()
    keep = [l for l in lines if any(k in l for k in
                                    ("Azimuth", "Elevation", "Radius", "spatializer",
                                     "Params", "Prop"))]
    res["lines"] = keep[:40]
    return res


def set_prop(name, key, value, prefixes=("s0:", "")):
    """Try the plausible control-change syntaxes; record which one the node accepted.

    The Props param exposes the graph controls as `s0:Azimuth` (node name prefix),
    so the prefixed key is tried first.
    """
    nid = node_id(name)
    if nid is None:
        return {"node": name, "id": None, "error": "node not found"}
    stamp = "%s_%s_%s" % (name, key, time.strftime("%H%M%S"))
    before = enum_props(name, save=os.path.join(RAW, "ctl_before_%s.txt" % stamp))
    tries = []
    for key_try in ["%s%s" % (p, key) for p in prefixes]:
        for f in ('{ params = [ "%s" %s ] }' % (key_try, value),
                  '{ "%s" = %s }' % (key_try, value),
                  '{ params = [ %s %s ] }' % (key_try, value)):
            r = L.run(["pw-cli", "set-param", str(nid), "Props", f], wall=8.0)
            tries.append({"form": f, "rc": r.rc, "out": r.out.strip()[-200:],
                          "err": r.err.strip()[-200:]})
            if r.rc == 0:
                break
        if tries and tries[-1]["rc"] == 0:
            break
    after = enum_props(name, save=os.path.join(RAW, "ctl_after_%s.txt" % stamp))
    return {"node": name, "id": nid, "tries": tries,
            "values_before": _ctl_values(before.get("raw")),
            "values_after": _ctl_values(after.get("raw"))}


def _ctl_values(raw_path):
    """Read the s0: control values back out of a saved enum-params dump."""
    if not raw_path or not os.path.exists(raw_path):
        return None
    out = {}
    try:
        with open(raw_path) as f:
            lines = [l.strip() for l in f]
    except Exception:
        return None
    for i, l in enumerate(lines):
        m = re.match(r'^String "(s\d+):(Azimuth|Elevation|Radius)"$', l)
        if m and i + 1 < len(lines):
            val = lines[i + 1]
            mm = re.match(r"^(Float|Int|Double) ([-\d.eE+]+)$", val)
            if mm:
                out["%s:%s" % (m.group(1), m.group(2))] = float(mm.group(2))
    return out


# ---------------------------------------------------------------------- argv
def node_tok(rate, az=None, el=None, radius=None, cfg=None, ctl_order="config_first",
             quote=False, filename=SOFA, extra_cfg=""):
    cfg = {} if cfg is None else dict(cfg)
    cfg.setdefault("filename", filename)
    if extra_cfg:
        cfg.update(extra_cfg)
    ctl = {}
    if az is not None:
        ctl["Azimuth"] = az
    if el is not None:
        ctl["Elevation"] = el
    if radius is not None:
        ctl["Radius"] = radius
    q = '"' if quote else ""
    cfg_s = ",".join("%s%s%s=%s%s%s" % (q, k, q, q, v, q) for k, v in cfg.items())
    ctl_s = ",".join("%s%s%s=%s%s%s" % (q, k, q, q, v, q) for k, v in ctl.items())
    body = "{type=sofa,name=s0,label=spatializer"
    parts = ["config={%s}" % cfg_s, "control={%s}" % ctl_s]
    if ctl_order == "control_first":
        parts = list(reversed(parts))
    return body + "," + ",".join(parts) + "}"


def args_token(rate, tok, order="base", sib=False):
    base = [("node.description=r100b_sofa", "nd"),
            ("filter.graph={nodes=[%s]}" % tok, "fg"),
            ("audio.channels=1", "ac"),
            ("audio.position=[MONO]", "ap"),
            ("audio.rate=%d" % rate, "ar"),
            ("capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink}" % FC_IN, "cp"),
            ("playback.props={node.name=%s,node.autoconnect=false,audio.channels=2,audio.position=[FL,FR]}" % FC_OUT, "pp")]
    if order == "base":
        seq = base
    elif order == "reversed":
        seq = list(reversed(base))
    elif order == "graph_last":
        seq = [t for t in base if t[1] != "fg"] + [t for t in base if t[1] == "fg"]
    elif order == "props_first":
        seq = [t for t in base if t[1] in ("cp", "pp", "nd")] + [t for t in base if t[1] not in ("cp", "pp", "nd")]
    elif order == "rates_first":
        seq = [t for t in base if t[1] in ("ar", "ac", "ap")] + [t for t in base if t[1] not in ("ar", "ac", "ap")]
    else:
        raise ValueError(order)
    return ",".join(t[0] for t in seq)


def sib_token(rate=48000):
    return ("node.description=r100b_sib,filter.graph={nodes=[{type=sofa,name=s1,"
            "label=spatializer,config={filename=%s},control={Azimuth=0.0,Elevation=0.0,"
            "Radius=1.0}}]},audio.channels=1,audio.position=[MONO],audio.rate=%d,"
            "capture.props={node.name=%s,node.autoconnect=false,media.class=Audio/Sink},"
            "playback.props={node.name=%s,node.autoconnect=false,audio.channels=2,"
            "audio.position=[FL,FR]}" % (SOFA, rate, SIB_IN, SIB_OUT))


# ------------------------------------------------------------------ analysis
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


def ild_db(l, r):
    return round(20 * math.log10(max(1e-12, l) / max(1e-12, r)), 3)


def analyze(path, rate, tone=440.0, win_rate=None):
    """Analysis in two recipes:
    * `channels` — window = 0.4 s of the *file's* rate (the r100b recipe)
    * `scout`    — window = 0.4 s of the *filter-chain* rate, exactly the r100 scout's
                   `analyze(out_wav, rate)` recipe, so its published numbers can be
                   compared digit-for-digit.
    """
    if not os.path.exists(path):
        return {"bytes": 0}
    w = L.read_wav(path)
    res = {"bytes": os.path.getsize(path), "frames": w["frames"], "ch": w["ch"],
           "file_rate": w["rate"]}
    if w["ch"] < 2:
        res["ch_warning"] = "expected stereo"
    res["channels"] = []
    for ci, x in enumerate(w["x"]):
        win = min(int(0.4 * w["rate"]), max(1, w["frames"]))
        seg, off = best_window(x, win)
        rms = (sum(v * v for v in seg) / max(1, len(seg))) ** 0.5
        full = (sum(v * v for v in x) / max(1, len(x))) ** 0.5
        pk = max((abs(v) for v in x), default=0.0)
        nz = sum(1 for v in x if v != 0.0)
        res["channels"].append({
            "rms": round(rms, 8), "rms_full": round(full, 8), "peak": round(pk, 6),
            "tone": round(goertzel(seg, tone, w["rate"]), 8),
            "nonzero": nz, "win_offset": off, "rate": w["rate"]})
    if len(res["channels"]) >= 2:
        res["ild_db"] = ild_db(res["channels"][0]["rms"], res["channels"][1]["rms"])
        res["ild_full_db"] = ild_db(res["channels"][0]["rms_full"], res["channels"][1]["rms_full"])
    if res["channels"]:
        res["peak"] = max(c["peak"] for c in res["channels"])
    # scout recipe
    wr = win_rate or rate
    sc = []
    for ci, x in enumerate(w["x"]):
        win = min(int(0.4 * wr), max(1, w["frames"]))
        seg, off = best_window(x, win)
        rms = (sum(v * v for v in seg) / max(1, len(seg))) ** 0.5
        sc.append({"rms": round(rms, 8), "win_offset": off,
                   "tone440": round(goertzel(seg, tone, w["rate"]), 8),
                   "rate": w["rate"]})
    res["scout"] = {"win_rate": wr, "win": min(int(0.4 * wr), max(1, w["frames"])),
                    "channels": sc}
    if len(sc) >= 2:
        res["scout"]["ild_db"] = ild_db(sc[0]["rms"], sc[1]["rms"])
    return res


def analyze_series(path, win_ms=100):
    """Per-window ILD/level time series (for runtime-change and timing legs)."""
    if not os.path.exists(path):
        return {"bytes": 0}
    w = L.read_wav(path)
    n = w["frames"]
    win = max(1, int(w["rate"] * win_ms / 1000.0))
    series = []
    for off in range(0, max(1, n - win + 1), win):
        seg = [c[off:off + win] for c in w["x"]]
        rms = [(sum(v * v for v in s) / max(1, len(s))) ** 0.5 for s in seg]
        series.append({"ms": round(off * 1000.0 / w["rate"], 1),
                       "rms": [round(v, 8) for v in rms],
                       "ild": ild_db(rms[0], rms[1]) if len(rms) >= 2 else None})
    return {"frames": n, "file_rate": w["rate"], "win_ms": win_ms, "series": series}


def write_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)
    return path


# ----------------------------------------------------------------------- leg
def fc_log_lines(text):
    keep = []
    for l in text.splitlines():
        low = l.lower()
        if any(k in low for k in ("spatializer", "sofa", "sampling rate",
                                  "using n_samples", "error", "warn")):
            keep.append(l.strip()[:300])
    return keep[-40:]


def run_leg(name, rate=44100, az=0.0, el=None, radius=None, tok=None, argv_order="base",
            ctl_order="config_first", quote=False, extra_cfg=None, sib=None,
            tone_secs=1.6, tone_freq=440.0, tone_amp=0.5, play="bg", post=None,
            swap_channels=False, ref_tap=False, rep=0, rec_secs=None, tag=None,
            env=None, save_series=False, keep_wav=True, tone_path=None, rec_channels=2):
    """One bounded leg with fresh processes. Returns a JSON-able row."""
    t0 = time.time()
    tag = tag or ("%s_r%d" % (name, rep))
    row = {"leg": name, "rep": rep, "tag": tag, "rate": rate, "azimuth": az,
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "elevation": el, "radius": radius, "argv_order": argv_order,
           "ctl_order": ctl_order, "quote": quote, "sib": bool(sib),
           "post": post, "swap_channels": swap_channels, "ref_tap": ref_tap,
           "tone": {"freq": tone_freq, "secs": tone_secs, "amp": tone_amp},
           "loadavg_start": loadavg()}
    sw = sweep()
    row["pre_sweep"] = sw
    if tok is None:
        tok = node_tok(rate, az=az, el=el, radius=radius, ctl_order=ctl_order,
                       quote=quote, extra_cfg=extra_cfg)
    row["node_tok"] = tok
    row["argv_args"] = args_token(rate, tok, order=argv_order)
    sink = sink_load(SINK_IN, 1, rate)
    row["sinks"] = {"in": sink}
    # PIPEWIRE_DEBUG=3 is what makes the *plugin's* log lines (n_samples / no config
    # / rate) visible in the pw-cli client's output - the scout used the same env
    cli_env = {"PIPEWIRE_DEBUG": "3"}
    if env:
        cli_env.update(env)
    cli = L.PwCli(env=cli_env, idle=0.4, hard=3.0)
    out_wav = os.path.join(SCRATCH, "cap_%s.wav" % tag)
    if os.path.exists(out_wav):
        os.unlink(out_wav)
    recp = refp = playp = None
    sibp = None
    try:
        if sib:
            so, sv = cli.load("libpipewire-module-filter-chain", sib_token(sib if isinstance(sib, int) else 48000))
            row["sib_load"] = {"var": sv, "out": so.strip()[-200:]}
            time.sleep(0.6)
        out, var = cli.load("libpipewire-module-filter-chain", row["argv_args"])
        row["load_out"] = out.strip()[-600:]
        row["module_var"] = var
        time.sleep(0.7)
        row["nodes_now"] = sorted(n for n in live()["nodes"])
        row["ports_fc_in"] = ports_of(FC_IN)
        row["ports_fc_out"] = ports_of(FC_OUT)
        row["props_enum_in"] = enum_props(FC_IN, save=os.path.join(RAW, "enum_%s_in.txt" % tag))
        row["props_enum_out"] = enum_props(FC_OUT, save=os.path.join(RAW, "enum_%s_out.txt" % tag))
        recp = Bg(["pw-record", "--channels", str(rec_channels), "-P", "node.name=%s" % NS_REC,
                   "-P", "node.autoconnect=false", out_wav],
                  wall=(rec_secs or tone_secs) + 8.0, env=env)
        time.sleep(0.8)
        row["ports_rec"] = ports_of(NS_REC)
        if ref_tap:
            refp = Bg(["pw-record", "--channels", "1", "-P", "node.name=%s" % NS_REF,
                       "-P", "node.autoconnect=false", os.path.join(SCRATCH, "ref_%s.wav" % tag)],
                      wall=(rec_secs or tone_secs) + 8.0, env=env)
            time.sleep(0.7)
            row["ports_ref"] = ports_of(NS_REF)
        row["links"] = []
        if var is not None and row["ports_fc_in"] and row["ports_fc_out"]:
            row["links"].append(link("%s:monitor_MONO" % SINK_IN, "%s:playback_MONO" % FC_IN))
            if refp is not None:
                row["links"].append(link("%s:monitor_MONO" % SINK_IN, "%s:input_MONO" % NS_REF))
            # channel-swap falsifier: cross the FC outputs into the recorder's
            # channel ports (FL->FR, FR->FL) so the recorded channel order is inverted
            pairs = [("FL", "FR"), ("FR", "FL")] if swap_channels else [("FL", "FL"), ("FR", "FR")]
            for src, dst in pairs:
                row["links"].append(link("%s:output_%s" % (FC_OUT, src),
                                         "%s:input_%s" % (NS_REC, dst)))
        row["links_before_play"] = [l.strip() for l in L.run(["pw-link", "-l"], wall=6.0).out.splitlines()
                                    if "r100b" in l]
        if tone_path is None:
            tone_path = os.path.join(SCRATCH, "tone_%s_%d.wav" % (tone_freq, rate))
            n = int(rate * tone_secs)
            L.write_wav(tone_path, [tone_amp * math.sin(2 * math.pi * tone_freq * i / rate)
                                    for i in range(n)], rate=rate, ch=1)
        row["tone_file"] = tone_path
        tw = L.read_wav(tone_path)
        row["tone_file_rms"] = round(
            (sum(v * v for v in tw["x"][0]) / max(1, tw["frames"])) ** 0.5, 8)
        if play == "fg":
            pl = L.run(["pw-play", "--target", SINK_IN, tone_path], wall=tone_secs + 4.0, env=env)
            row["play"] = pl.as_dict()
            row["play_link_origin"] = "policy"
            if pl.timed_out:
                row["play_hang"] = True
        else:
            playp = Bg(["pw-play", "--target", SINK_IN, "-P", "node.name=%s" % NS_PLAY,
                        "-P", "node.autoconnect=false", tone_path],
                       wall=tone_secs + 8.0, env=env)
            row["play"] = {"argv": playp.argv, "mode": "bg"}
            time.sleep(0.6)
            row["ports_play"] = ports_of(NS_PLAY)
            pre_links = [l.strip() for l in L.run(["pw-link", "-l"], wall=6.0).out.splitlines()]
            policy = any(NS_PLAY in l and SINK_IN in l for l in pre_links)
            row["play_link_origin"] = "policy" if policy else "manual"
            if not policy:
                # policy autolink can silently miss (r98 §3.5) — link it ourselves,
                # same Link object, same ports; origin is recorded either way
                row["links"].append(link("%s:output_MONO" % NS_PLAY, "%s:playback_MONO" % SINK_IN, tries=4))
            row["graph_witness_mid"] = {"loadavg": loadavg(), "clock": clock_witness(),
                                        "nodes": live()["nodes"], "node_states": live()["node_states"]}
            evs = []
            t_play = time.time()
            for act in sorted(post or [], key=lambda a: a.get("t", 0)):
                wait = t_play + float(act.get("t", 0)) - time.time()
                if wait > 0:
                    time.sleep(wait)
                evs.append(_post_action(act, row, cli, sink, playp, env, out_wav))
            row["post_events"] = evs
            time.sleep(max(0.0, (rec_secs or tone_secs) - (time.time() - t_play)))
            if playp is not None:
                row["play_stop"] = playp.stop()
                playp = None
        time.sleep(0.5)
        if recp is not None:
            row["rec"] = recp.stop()
            recp = None
        if refp is not None:
            row["ref"] = refp.stop()
            refp = None
        row["analysis"] = analyze(out_wav, rate, tone=tone_freq)
        if ref_tap:
            row["ref_analysis"] = analyze(os.path.join(SCRATCH, "ref_%s.wav" % tag), rate, tone=tone_freq)
        if save_series:
            row["series"] = analyze_series(out_wav)
        row["links_after"] = [l.strip() for l in L.run(["pw-link", "-l"], wall=6.0).out.splitlines()
                              if "r100b" in l]
        if var is not None:
            try:
                row["unload"] = cli.cmd("unload-module %d" % var, idle=0.4, hard=2.5)[-300:]
            except Exception as e:
                row["unload"] = {"error": repr(e)}
        if sib and row.get("sib_load", {}).get("var") is not None:
            try:
                row["sib_unload"] = cli.cmd("unload-module %d" % row["sib_load"]["var"],
                                            idle=0.4, hard=2.5)[-200:]
            except Exception as e:
                row["sib_unload"] = {"error": repr(e)}
    except Exception as e:
        row["leg_error"] = repr(e)
    finally:
        if recp is not None:
            row["rec"] = recp.stop()
        if refp is not None:
            row["ref"] = refp.stop()
        if playp is not None:
            row["play_stop"] = playp.stop()
        log = cli.close()
        row["fc_log"] = fc_log_lines("\n".join(log))
        row["sink_unloads"] = {"in": sink_unload(SINK_IN, sink["id"])}
        time.sleep(0.4)
        row["post_sweep"] = sweep()
    row["loadavg_end"] = loadavg()
    row["wall_s"] = round(time.time() - t0, 2)
    return row


def _post_action(act, row, cli, sink, playp, env, out_wav):
    """Timing/robustness actions fired mid-stream."""
    key = act.get("do")
    at = act.get("t")
    if key == "kill_source" and playp is not None:
        st = playp.stop(sig=signal.SIGKILL)
        return {"at": at, "action": "kill_source", "result": st}
    if key == "relink_out":
        u = unlink("%s:output_FL" % FC_OUT, "%s:input_FL" % NS_REC)
        time.sleep(0.35)
        r = link("%s:output_FL" % FC_OUT, "%s:input_FL" % NS_REC)
        return {"at": at, "action": "relink_out", "unlink": u, "relink": r}
    if key == "relink_in":
        u = unlink("%s:monitor_MONO" % SINK_IN, "%s:playback_MONO" % FC_IN)
        time.sleep(0.35)
        r = link("%s:monitor_MONO" % SINK_IN, "%s:playback_MONO" % FC_IN)
        return {"at": at, "action": "relink_in", "unlink": u, "relink": r}
    if key == "drop_driver":
        u = sink_unload(SINK_IN, sink["id"])
        time.sleep(0.4)
        return {"at": at, "action": "drop_driver", "unload": u,
                "nodes_after": sorted(n for n in live()["nodes"])}
    if key == "set_azimuth":
        sp = set_prop(act.get("node", FC_IN), act.get("key", "Azimuth"), act.get("value", 90.0))
        return {"at": at, "action": "set_azimuth", "result": sp}
    if key == "unload_fc":
        try:
            out = cli.cmd("unload-module %d" % row["module_var"], idle=0.4, hard=2.5)
        except Exception as e:
            out = {"error": repr(e)}
        time.sleep(0.4)
        return {"at": at, "action": "unload_fc", "result": out[-300:] if isinstance(out, str) else out,
                "nodes_after": sorted(n for n in live()["nodes"])}
    return {"at": at, "action": key, "result": "unknown-action"}
