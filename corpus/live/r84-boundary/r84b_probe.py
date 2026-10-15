#!/usr/bin/env python3
"""r84b boundary harness — falsify r84 scout claims under load.

Seat: BOUNDARY (leaf, r84). Namespace ALL audio objects r84b_*.
Writes only under corpus/live/r84-boundary/ (untracked scratch). No tracked writes.
Methods: verbatim replays of r84-scout cells, host-state variation, hog load,
bounded mode hunting. Never touches foreign objects; own modules unloaded by
index-verified module id.
"""
import json, os, re, signal, subprocess, sys, time, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TMP = ROOT / "tmp"; RUNS = ROOT / "runs"; RCPTS = ROOT / "receipts"
for d in (TMP, RUNS, RCPTS): d.mkdir(parents=True, exist_ok=True)

TAG = "r84b"
NS = "r84b_ns"; NS2 = "r84b_ns2"; SR = 48000
LINE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
SPDIF = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
SPEAKER = "alsa_output.usb-Generic_USB_Audio-00.HiFi__Speaker__sink"

DEVNULL = subprocess.DEVNULL

# ---------------- bounded exec ----------------
def run(cmd, timeout, env_extra=None):
    env = dict(os.environ); env.update(env_extra or {})
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env, start_new_session=True, stdin=DEVNULL)
    try:
        out, err = p.communicate(timeout=timeout); to = False
    except subprocess.TimeoutExpired:
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        out, err = p.communicate(); to = True
    return {"rc": p.returncode, "wall": round(time.time() - t0, 3),
            "out": out.decode("utf-8", "replace")[-4000:],
            "err": err.decode("utf-8", "replace")[-4000:],
            "timeout": to, "cmd": " ".join(str(c) for c in cmd)}

class Proc:
    def __init__(self, cmd, env_extra=None):
        env = dict(os.environ); env.update(env_extra or {})
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  env=env, start_new_session=True, stdin=DEVNULL)
        self.t0 = time.time()
    def alive(self): return self.p.poll() is None
    def kill(self, sig=signal.SIGKILL):
        try: os.killpg(self.p.pid, sig)
        except (ProcessLookupError, PermissionError): pass
    def finish(self):
        try: out, err = self.p.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            self.kill(); out, err = self.p.communicate()
        return {"rc": self.p.returncode, "wall": round(time.time() - self.t0, 3),
                "out": out.decode("utf-8", "replace")[-2000:],
                "err": err.decode("utf-8", "replace")[-2000:], "timeout": False}

class Hog:
    """Bounded host load: CPU burners + optional audio hog Procs (own ns)."""
    def __init__(self, ncpu=24, audio=None):
        self.procs = []
        for _ in range(ncpu):
            self.procs.append(subprocess.Popen(
                [sys.executable, "-c", "while True: pass"],
                stdout=DEVNULL, stderr=DEVNULL, start_new_session=True))
        self.audio = list(audio or [])
    def stop(self):
        for a in self.audio:
            a.kill()
        for a in self.audio:
            try: a.finish()
            except Exception: pass
        for p in self.procs:
            try: os.killpg(p.pid, signal.SIGKILL)
            except Exception: pass
        for p in self.procs:
            try: p.wait(timeout=2)
            except Exception: pass

# ---------------- witnesses ----------------
def loadavg():
    try: return float(Path("/proc/loadavg").read_text().split()[0])
    except Exception: return -1.0

def default_sink():
    r = subprocess.run(["pactl", "get-default-sink"], capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip(): return r.stdout.strip()
    for ln in subprocess.run(["pactl", "info"], capture_output=True, text=True).stdout.splitlines():
        if ln.startswith("Default Sink:"): return ln.split(":", 1)[1].strip()
    return "?"

def pw_dump():
    return json.loads(subprocess.run(["pw-dump"], capture_output=True).stdout)

PROPS_OF = ("node.name", "target.object", "node.target", "media.role", "node.latency",
            "application.name", "media.name", "application.icon-name",
            "application.icon_name", "application.process.binary", "zzz.invented",
            "module-stream-restore.id", "filter.want")

def witness_nodes(*subs):
    out = []
    for o in pw_dump():
        if o.get("type") != "PipeWire:Interface:Node": continue
        pr = o.get("info", {}).get("props", {}) or {}
        nm = str(pr.get("node.name", ""))
        if any(s in nm for s in subs):
            out.append({"id": o.get("id"), "serial": o.get("info", {}).get("serial") or pr.get("object.serial"),
                        "name": nm, "state": o.get("info", {}).get("state"),
                        "props": {k: pr.get(k) for k in PROPS_OF if k in pr}})
    return out

def linkmap():
    txt = subprocess.run(["pw-link", "-l"], capture_output=True).stdout.decode()
    m = {}; cur = None
    for ln in txt.splitlines():
        if not ln.startswith((" ", "\t", "|")):
            cur = ln.strip(); m[cur] = {">": [], "<": []}
        elif cur:
            mm = re.match(r"\s*\|([<>-]+)\s+(\S+)", ln)
            if mm:
                d = ">" if ">" in mm.group(1) else "<"
                m[cur][d].append(mm.group(2))
    return m

def consumers_of(name):
    out = []
    for port, e in linkmap().items():
        if port.startswith(name + ":"): out += e[">"]
    return out

def pactl_json(what):
    r = subprocess.run(["pactl", "-f", "json", "list", what], capture_output=True)
    try: return json.loads(r.stdout)
    except Exception: return []

SI_PROPS = ("application.name", "media.name", "media.role", "module-stream-restore.id",
            "application.icon_name", "application.icon-name", "application.process.binary",
            "zzz.invented", "filter.want", "node.name")

def si_witness(match):
    out = []
    for si in pactl_json("sink-inputs"):
        pr = si.get("properties", {}) or {}
        blob = " ".join(str(pr.get(k, "")) for k in ("application.name", "media.name", "node.name"))
        if match in blob:
            vol = ((si.get("volume") or {}).get("front-left") or {}).get("value_percent")
            out.append({"index": si.get("index"), "value_percent": vol,
                        "props": {k: pr.get(k) for k in SI_PROPS if k in pr}})
    return out

def pcm_status(card, dev, direction):
    try: return Path(f"/proc/asound/card{card}/pcm{dev}{direction}/sub0/status").read_text().splitlines()[0].strip()
    except Exception: return "?"

# ---------------- audio gen + analysis ----------------
def synth_wav(path, secs, freqs, amp=8192, chs=2, rate=SR):
    import numpy as np
    n = int(secs * rate); t = np.arange(n) / rate
    chans = []
    for c in range(chs):
        f = freqs[c] if isinstance(freqs, (list, tuple)) else freqs
        chans.append((amp * np.sin(2 * np.pi * f * t)).astype(np.int16))
    data = np.column_stack(chans)
    with open(path, "wb") as fh:
        fh.write(b"RIFF" + struct.pack("<I", 36 + data.nbytes) + b"WAVEfmt " +
                 struct.pack("<IHHIIHH", 16, 1, chs, rate, rate * chs * 2, chs * 2, 16) +
                 b"data" + struct.pack("<I", data.nbytes) + data.tobytes())

def read_s16(path):
    import numpy as np
    try: b = Path(path).read_bytes()
    except FileNotFoundError: return np.zeros((0, 2), np.int16)
    i = b.find(b"data")
    if i < 0: return np.zeros((0, 2), np.int16)
    sz = struct.unpack("<I", b[i + 4:i + 8])[0]
    avail = len(b) - i - 8
    if sz == 0 or sz > avail: sz = avail  # SIGKILLed writers leave size 0
    a = np.frombuffer(b[i + 8:i + 8 + sz], np.int16)
    return a[:len(a) // 2 * 2].reshape(-1, 2)

def windows(path, freqs=(1000, 1500, 2000), win=0.25):
    import numpy as np
    a = read_s16(path)
    if a.size == 0: return []
    w = int(win * SR); out = []
    k = {f: int(round(f * w / SR)) for f in freqs}
    for s in range(0, len(a) - w + 1, w):
        seg = a[s:s + w].astype(np.float64)
        row = {"t0": round(s / SR, 3), "peak": int(np.abs(seg).max())}
        for ci, ch in enumerate(("L", "R")):
            F = np.fft.rfft(seg[:, ci])
            for f, kk in k.items():
                row[f"{ch}@{f}"] = round(2 * abs(F[kk]) / w, 1)
        out.append(row)
    return out

def amp_series(path, win=0.1):
    return [(w["t0"], w["peak"]) for w in windows(path, win=win)]

def file_hdr(path):
    try:
        b = Path(path).read_bytes()[:64]
        return {"size": Path(path).stat().st_size, "magic": b[:4].decode("ascii", "replace"),
                "head_hex": b[:48].hex()}
    except FileNotFoundError:
        return {"size": -1, "magic": "MISSING"}

def nz_stats(path):
    import numpy as np
    a = read_s16(path)
    if a.size == 0: return {"frames": 0}
    nz = (np.abs(a).sum(axis=1) > 0)
    idx = np.flatnonzero(nz)
    starts = idx[np.r_[True, np.diff(idx) > 1]] if len(idx) else np.array([], int)
    sp = np.diff(starts).tolist() if len(starts) > 1 else []
    return {"frames": int(a.shape[0]), "nz_rows": int(nz.sum()),
            "bursts": int(len(starts)), "first_starts": starts[:6].tolist(),
            "spacings_head": sp[:6], "spacing_mode": (max(set(sp), key=sp.count) if sp else None),
            "peak": int(np.abs(a).max()) if a.size else 0}

# ---------------- module lifecycle ----------------
def load_ns(name):
    r = run(["pactl", "load-module", "module-null-sink", f"sink_name={name}"], 8)
    idx = (r["out"].strip() or "0")
    try: idx_i = int(idx)
    except ValueError: idx_i = -1
    ok = False
    for ln in subprocess.run(["pactl", "list", "short", "modules"],
                             capture_output=True).stdout.decode().splitlines():
        parts = ln.split("\t")
        if parts and parts[0].isdigit() and int(parts[0]) == idx_i and f"sink_name={name}" in ln:
            ok = True
    return {"idx": idx_i, "verified": ok, "load": r}

def unload_idx(idx, expect_name):
    for ln in subprocess.run(["pactl", "list", "short", "modules"],
                             capture_output=True).stdout.decode().splitlines():
        parts = ln.split("\t")
        if parts and parts[0].isdigit() and int(parts[0]) == idx:
            if expect_name in ln:
                return run(["pactl", "unload-module", str(idx)], 8)
            return {"rc": -99, "err": f"refused: idx {idx} is not {expect_name}: {ln}", "timeout": False}
    return {"rc": -98, "err": f"idx {idx} not present", "timeout": False}

# ---------------- leg plumbing ----------------
def leg_dir(probe, leg, rep):
    d = RUNS / probe / leg / f"rep{rep}"
    d.mkdir(parents=True, exist_ok=True)
    return d

def record_leg(probe, leg, rep, res, extra=None):
    d = leg_dir(probe, leg, rep)
    (d / "cmd").write_text(str(res.get("cmd", "")))
    (d / "stdout").write_text(str(res.get("out", "")))
    (d / "stderr").write_text(str(res.get("err", "")))
    (d / "result.json").write_text(json.dumps(
        {**{k: res.get(k) for k in ("rc", "wall", "timeout")}, **(extra or {})}, indent=1))

def compact(res, extra=None):
    return {"rc": res["rc"], "wall": res["wall"], "err": res["err"].splitlines()[:4],
            "out": res["out"].splitlines()[:2], **(extra or {})}

def during(probe, leg, rep, argv, wait=0.6, witness=None, env=None, timeout=8):
    p = Proc(argv, env_extra=env)
    time.sleep(wait)
    w = witness() if witness else {}
    fin = p.finish()
    res = {"rc": fin["rc"], "wall": fin["wall"], "out": fin["out"], "err": fin["err"],
           "timeout": False, "cmd": " ".join(map(str, argv))}
    return res, w

def play_at(ns, wav, name, vol=None, extra=None):
    cmd = ["pw-play", "-P", f"node.name={name}", "--target", ns]
    if vol is not None: cmd += ["--volume", vol]
    return Proc(cmd + [wav] + (extra or []))

def si_index(name):
    for n in witness_nodes(name):
        if n["name"] == name: return n["serial"]
    return None

def tone_short(): 
    p = TMP / "tone_short.wav"
    if not p.exists(): synth_wav(p, 1.2, [1000, 1500])
    return str(p)

def tone_a():
    p = TMP / "tone_a.wav"
    if not p.exists(): synth_wav(p, 4.0, [1000, 1500])
    return str(p)

def tone_b():
    p = TMP / "tone_b.wav"
    if not p.exists(): synth_wav(p, 4.0, 2000)
    return str(p)

def tone_long(secs=30):
    p = TMP / f"tone_long{secs}.wav"
    if not p.exists(): synth_wav(p, secs, [1000, 1500])
    return str(p)

# ---------------- batch: verbatim replays (device lattice + refusals) ----------------
def b_replay():
    probe = "pA-replay"; results = {}
    base = {"loadavg0": loadavg(), "default_sink0": default_sink()}
    legs = [
        ("a_pulse",        ["aplay", "-D", "pulse", tone_short()], 6),
        ("a_nosuch",       ["aplay", "-D", "nosuch_pcm_r84b", tone_short()], 6),
        ("a_hw9",          ["aplay", "-D", "hw:9", tone_short()], 6),
        ("a_hw_cardnosuch",["aplay", "-D", "hw:CARD=NosuchR84b", tone_short()], 6),
        ("a_hw09",         ["aplay", "-D", "hw:0,9", tone_short()], 6),
        ("a_iec958_d1",    ["aplay", "-D", "iec958:CARD=Audio,DEV=1", tone_short()], 6),
        ("a_default_card", ["aplay", "-D", "default:CARD=Audio", tone_short()], 6),
        ("a_server_bad",   ["aplay", "-D", "pipewire:SERVER=nonexistent_r84b", tone_short()], 8),
        ("a_null",         ["aplay", "-D", "null", tone_short()], 6),
        ("a_hw00",         ["aplay", "-D", "hw:0,0", tone_short()], 8),
        ("a_front",        ["aplay", "-D", "front:CARD=Audio,DEV=0", tone_short()], 8),
        ("a_iec958_d0",    ["aplay", "-D", "iec958:CARD=Audio,DEV=0", tone_short()], 8),
        ("a_empty_d",      ["aplay", "-D", "", tone_short()], 6),
        ("r_empty_d",      ["arecord", "-D", "", "-d", "1"], 6),
        ("r_hw00",         ["arecord", "-D", "hw:0,0", "-d", "1", "-f", "cd", str(TMP / "r_hw00.wav")], 8),
        ("r_hw01",         ["arecord", "-D", "hw:0,1", "-d", "1", "-f", "cd", str(TMP / "r_hw01.wav")], 8),
        ("r_hw03",         ["arecord", "-D", "hw:0,3", "-d", "1", "-f", "cd", str(TMP / "r_hw03.wav")], 8),
        ("r_null",         ["arecord", "-D", "null", "-d", "1", "-f", "cd", str(TMP / "r_null.wav")], 8),
        ("r_pw",           ["arecord", "-D", "pipewire", "-d", "2", "-f", "cd", str(TMP / "r_pw.wav")], 10),
        ("r_pw_default",   ["arecord", "-D", "default", "-d", "2", "-f", "cd", str(TMP / "r_pw_def.wav")], 10),
        ("r_pw_node_line", ["arecord", "-D", f"pipewire:NODE={LINE}", "-d", "2", "-f", "cd", str(TMP / "r_pw_line.wav")], 10),
        ("st_null_c2",     ["speaker-test", "-D", "null", "-c", "2", "-l", "1", "-t", "sine", "-S", "10"], 8),
        ("st_c0",          ["speaker-test", "-D", "null", "-c", "0", "-l", "1"], 8),
        ("st_hw00_c1",     ["speaker-test", "-D", "hw:0,0", "-c", "1", "-l", "1", "-t", "sine"], 8),
        ("st_t_bogus",     ["speaker-test", "-D", "null", "-t", "bogus", "-c", "2", "-l", "1"], 8),
    ]
    for name, argv, to in legs:
        reps = []
        for rep in range(2):
            w = None
            if name.startswith("a_"):
                npc0 = len(witness_nodes("alsa_playback"))
                res, w = during(probe, name, rep, argv, wait=0.5, witness=lambda: witness_nodes("aplay", "alsa_playback"))
                npc1 = len(witness_nodes("alsa_playback"))
                extra = {"new_playback_nodes": npc1 - npc0, "nodes": w, "loadavg": loadavg(), "default_sink": default_sink()}
            else:
                res = run(argv, to)
                extra = {"loadavg": loadavg(), "default_sink": default_sink()}
                if name.startswith("r_") and name != "r_empty_d":
                    out = argv[-1]
                    extra["hdr"] = file_hdr(out)
                    if name == "r_null":
                        extra["nz"] = nz_stats(out)
                    elif name in ("r_hw00", "r_hw01"):
                        import numpy as np
                        a = read_s16(out)
                        extra["peak"] = int(np.abs(a).max()) if a.size else -1
                    elif name == "r_pw_node_line":
                        extra["nodes"] = witness_nodes("alsa_capture")
                elif name == "r_pw" or name == "r_pw_default":
                    extra["hdr"] = file_hdr(argv[-1])
            record_leg(probe, name, rep, res, extra)
            reps.append(compact(res, extra))
        results[name] = reps
        r0 = reps[0]
        print(f"{name:18s} rc={[x['rc'] for x in reps]} wall={[x['wall'] for x in reps]} "
              f"err={r0['err'][:1]} extra={ {k:v for k,v in r0.items() if k not in ('rc','wall','err','out')} }")
    (RCPTS / "pA-replay.json").write_text(json.dumps({**base, "legs": results}, indent=1))

# ---------------- batch: plugin args + capture shapes ----------------
def b_plugin():
    probe = "pB-plugin"; results = {}
    s1 = load_ns(NS)
    assert s1["verified"], s1
    try:
        legs = [
            ("a_pw_node_ns",   ["aplay", "-D", f"pipewire:NODE={NS}", tone_short()]),
            ("a_pw_node_bogus",["aplay", "-D", "pipewire:NODE=no_such_r84b", tone_short()]),
            ("a_pw_role",      ["aplay", "-D", "pipewire:ROLE=Communication", tone_short()]),
            ("a_pw_period",    ["aplay", "-D", "pipewire:PERIOD_BYTES=4096", tone_short()]),
            ("a_pw_rate44",    ["aplay", "-D", "pipewire:RATE=44100", tone_short()]),
            ("a_pw_ch6",       ["aplay", "-D", "pipewire:CHANNELS=6", tone_short()]),
            ("a_pw_excl",      ["aplay", "-D", "pipewire:EXCLUSIVE=1", tone_short()]),
            ("a_pw_node_mon",  ["aplay", "-D", f"pipewire:NODE={NS}.monitor", tone_short()]),
        ]
        for name, argv in legs:
            reps = []
            for rep in range(2):
                res, w = during(probe, name, rep, argv, wait=0.5,
                                witness=lambda: {"nodes": witness_nodes("alsa_playback", "aplay"),
                                                 "cons": consumers_of("r84b_ns") + consumers_of("aplay") + consumers_of("alsa_playback.aplay")})
                extra = {"witness": w, "loadavg": loadavg(), "default_sink": default_sink()}
                record_leg(probe, name, rep, res, extra)
                reps.append(compact(res, extra))
            results[name] = reps
            print(f"{name:16s} rc={[x['rc'] for x in reps]} err={reps[0]['err'][:2]} "
                  f"nodes={[n['name'] for n in reps[0]['witness']['nodes']]}")
        # env legs
        for name, env in [("a_env_node", {"PIPEWIRE_NODE": NS}),
                          ("a_env_props", {"PIPEWIRE_PROPS": "{node.name=r84b_envp media.role=Communication}"})]:
            reps = []
            for rep in range(2):
                res, w = during(probe, name, rep, ["aplay", "-D", "pipewire", tone_short()], wait=0.5,
                                env=env, witness=lambda: {"nodes": witness_nodes("alsa_playback", "r84b_envp")})
                extra = {"witness": w, "env": env, "loadavg": loadavg(), "default_sink": default_sink()}
                record_leg(probe, name, rep, res, extra)
                reps.append(compact(res, extra))
            results[name] = reps
            print(f"{name:16s} rc={[x['rc'] for x in reps]} err={reps[0]['err'][:1]} nodes={[n['name'] for n in reps[0]['witness']['nodes']]}")
        # capture-side plugin shapes (state-flip replay + mode hunt)
        cap_legs = [
            ("r_pw_node_ns",     ["arecord", "-D", f"pipewire:NODE={NS}", "-d", "2", "-f", "cd", str(TMP / "r_pw_ns.wav")]),
            ("r_pw_node_nosuch", ["arecord", "-D", "pipewire:NODE=no_such_r84b", "-d", "2", "-f", "cd", str(TMP / "r_pw_nsn.wav")]),
            ("r_pw_node_mon",    ["arecord", "-D", f"pipewire:NODE={NS}.monitor", "-d", "2", "-f", "cd", str(TMP / "r_pw_mon.wav")]),
            ("r_pw_node_line",   ["arecord", "-D", f"pipewire:NODE={LINE}", "-d", "2", "-f", "cd", str(TMP / "r_pw_line2.wav")]),
        ]
        for name, argv in cap_legs:
            reps = []
            for rep in range(2):
                res, w = during(probe, name, rep, argv, wait=0.8, witness=lambda: {"nodes": witness_nodes("alsa_capture")})
                extra = {"witness": w, "hdr": file_hdr(argv[-1]), "loadavg": loadavg()}
                record_leg(probe, name, rep, res, extra)
                reps.append(compact(res, extra))
            results[name] = reps
            print(f"{name:16s} rc={[x['rc'] for x in reps]} hdr={[x['hdr']['size'] for x in reps]} err={reps[0]['err'][:2]}")
        # speaker-test plugin target replay
        reps = []
        for rep in range(2):
            res, w = during(probe, "st_pw_node_ns", rep,
                            ["speaker-test", "-D", f"pipewire:NODE={NS}", "-c", "2", "-l", "1", "-t", "sine", "-S", "5"],
                            wait=0.8, witness=lambda: {"nodes": witness_nodes("speaker-test")})
            extra = {"witness": w, "loadavg": loadavg()}
            record_leg(probe, "st_pw_node_ns", rep, res, extra)
            reps.append(compact(res, extra))
        results["st_pw_node_ns"] = reps
        print(f"st_pw_node_ns      rc={[x['rc'] for x in reps]} nodes={[n['name'] for n in reps[0]['witness']['nodes']]}")
        (RCPTS / "pB-plugin.json").write_text(json.dumps(results, indent=1))
    finally:
        unload_idx(s1["idx"], NS)

# ---------------- batch: PULSE_PROP env ----------------
def b_props():
    probe = "pC-props"; results = {}
    s1 = load_ns(NS)
    assert s1["verified"], s1
    try:
        legs = [
            ("role_comm",    {"PULSE_PROP_media.role": "Communication"}),
            ("role_music",   {"PULSE_PROP_media.role": "Music"}),
            ("role_bogus",   {"PULSE_PROP_media.role": "notarole"}),
            ("invented",     {"PULSE_PROP_zzz.invented": "42"}),
            ("appname",      {"PULSE_PROP_application.name": "r84b_app"}),
            ("medianame",    {"PULSE_PROP_media.name": "r84b_media"}),
            ("iconname",     {"PULSE_PROP_application.icon_name": "r84b_icon"}),
            ("proc_bin",     {"PULSE_PROP_application.process.binary": "r84b_bin"}),
            ("restore_id",   {"PULSE_PROP_module-stream-restore.id": "r84b_srid"}),
            ("bare_prop",    {"PULSE_PROP": "media.role=Communication"}),
        ]
        for name, env in legs:
            reps = []
            for rep in range(2):
                p = Proc(["paplay", "-d", NS, tone_a()], env_extra=env)
                time.sleep(1.0)
                w = {"nodes": witness_nodes("paplay"), "si": si_witness("paplay"), "loadavg": loadavg()}
                fin = p.finish()
                res = {"rc": fin["rc"], "wall": fin["wall"], "out": fin["out"], "err": fin["err"],
                       "timeout": False, "cmd": f"paplay -d {NS} tone_a.wav {env}"}
                record_leg(probe, name, rep, res, {"witness": w, "env": env})
                reps.append(compact(res, {"witness": w}))
            results[name] = reps
            n0 = reps[0]["witness"]["nodes"]
            s0 = reps[0]["witness"]["si"]
            print(f"{name:12s} rc={[x['rc'] for x in reps]} node_props={n0[0]['props'] if n0 else None} si={s0}")
            time.sleep(0.3)
        (RCPTS / "pC-props.json").write_text(json.dumps(results, indent=1))
    finally:
        unload_idx(s1["idx"], NS)

# ---------------- batch: cubic volume law (ambient / hog) ----------------
def vol_leg(probe, name, rep, actions, dur=7.0, wav=None, use_ns=NS):
    out = TMP / f"{probe}_{name}_{rep}.wav"
    player = play_at(use_ns, wav or tone_long(7), f"r84b_{probe}_{name}")
    time.sleep(0.5)
    rec = Proc(["pw-record", "-P", "stream.capture.sink=true", "-P", f"node.name=r84b_rec_{name}",
                "--target", use_ns, "--rate", "48000", "--channels", "2", "--format", "s16",
                str(out)])
    t0 = time.time(); acts = []
    for at, cmd in actions:
        while time.time() - t0 < at: time.sleep(0.02)
        acts.append({"t": at, "cmd": " ".join(cmd), "res": run(cmd, 6)})
    while time.time() - t0 < dur - 0.5: time.sleep(0.05)
    rec.kill(signal.SIGTERM); time.sleep(0.5); rres = rec.finish()
    while player.alive() and time.time() - t0 < dur + 3: time.sleep(0.1)
    pres = player.finish()
    series = amp_series(out, win=0.1)
    res = {"rc": pres["rc"], "wall": pres["wall"], "out": "", "err": pres["err"], "timeout": False,
           "cmd": f"pw-play {use_ns} + pw-record monitor + actions {[a['cmd'] for a in acts]}"}
    extra = {"acts": [{"t": a["t"], "cmd": a["cmd"], "rc": a["res"]["rc"],
                       "err": a["res"]["err"].splitlines()[:2]} for a in acts],
             "rec_rc": rres["rc"], "rec_size": file_hdr(out)["size"],
             "amp_series": series, "loadavg": loadavg()}
    record_leg(probe, name, rep, res, extra)
    try: out.unlink()
    except FileNotFoundError: pass
    return compact(res, extra)

def amp_med(series, t0, t1):
    import statistics
    vals = [p for t, p in series if t0 <= t <= t1]
    return int(statistics.median(vals)) if vals else -1

def amp_first_change(series, base, t0, thresh=0.5):
    for t, p in series:
        if t >= t0 and (base == 0 or abs(p - base) > thresh * max(base, 1)):
            return {"t_change": t, "amp": p}
    return None

def b_vol(probe="pD-vol", hog=False, ncpu=24):
    results = {"hog": hog}
    s1 = load_ns(NS); s2 = load_ns(NS2)
    assert s1["verified"] and s2["verified"], (s1, s2)
    h = None
    try:
        if hog:
            audio = [play_at(NS2, tone_long(30), "r84b_hog", vol="0.3"),
                     Proc(["pw-record", "-P", "stream.capture.sink=true", "-P", "node.name=r84b_hogrec",
                           "--target", NS2, "--rate", "48000", "--channels", "2", "--format", "s16", str(TMP / "hog.wav")])]
            h = Hog(ncpu=ncpu, audio=audio)
            time.sleep(1.5)
        results["loadavg_start"] = loadavg()
        legs = [
            ("vol_50",     [(2.0, ["pactl", "set-sink-volume", NS, "50%"])]),
            ("vol_150",    [(2.0, ["pactl", "set-sink-volume", NS, "150%"])]),
            ("vol_25_idx", [(2.0, ["pactl", "set-sink-volume", "@DEFAULT_SINK@", "25%"])]),  # placeholder, replaced below
            ("src_vol50",  [(2.0, ["pactl", "set-source-volume", f"{NS}.monitor", "50%"])]),
            ("mute_cycle", [(2.0, ["pactl", "set-sink-mute", NS, "1"]), (4.0, ["pactl", "set-sink-mute", NS, "0"])]),
            ("vol_0_100",  [(2.0, ["pactl", "set-sink-volume", NS, "0%"]), (4.0, ["pactl", "set-sink-volume", NS, "100%"])]),
        ]
        for name, acts_list in legs:
            reps = []
            for rep in range(3):
                run(["pactl", "set-sink-volume", NS, "100%"], 6)
                run(["pactl", "set-source-volume", f"{NS}.monitor", "100%"], 6)
                run(["pactl", "set-sink-mute", NS, "0"], 6)
                time.sleep(0.3)
                if name == "vol_25_idx":
                    serial = None
                    for n in witness_nodes(NS):
                        if n["name"] == NS: serial = n["serial"]
                    acts = [(2.0, ["pactl", "set-sink-volume", str(serial), "25%"])]
                else:
                    acts = acts_list
                r = vol_leg(probe, name, rep, acts)
                reps.append(r)
                base = amp_med(r["amp_series"], 0.5, 1.8)
                post = amp_med(r["amp_series"], 2.6, 6.0)
                reps[-1]["base_amp"] = base; reps[-1]["post_amp"] = post
                print(f"{name:10s} rep{rep} base={base} post={post} ratio={(post/base if base else 0):.4f} "
                      f"acts={[a['rc'] for a in r['acts']]} change={amp_first_change(r['amp_series'], base, 2.0)}")
            results[name] = reps
            run(["pactl", "set-sink-volume", NS, "100%"], 6)
            run(["pactl", "set-source-volume", f"{NS}.monitor", "100%"], 6)
            run(["pactl", "set-sink-mute", NS, "0"], 6)
        results["loadavg_end"] = loadavg()
        (RCPTS / f"{probe}.json").write_text(json.dumps(results, indent=1))
    finally:
        if h: h.stop()
        run(["pactl", "set-sink-volume", NS, "100%"], 6)
        run(["pactl", "set-source-volume", f"{NS}.monitor", "100%"], 6)
        run(["pactl", "set-sink-mute", NS, "0"], 6)
        run(["pactl", "suspend-sink", NS, "0"], 6)
        unload_idx(s1["idx"], NS); unload_idx(s2["idx"], NS2)

# ---------------- batch: suspend semantics ----------------
def b_susp(hog=False, ncpu=24):
    probe = "pE-susp"; results = {"hog": hog}
    s1 = load_ns(NS)
    assert s1["verified"], s1
    h = None
    try:
        if hog:
            h = Hog(ncpu=ncpu, audio=[play_at(NS, tone_long(30), "r84b_hogs", vol="0.1")])
            time.sleep(1.0)
        results["loadavg_start"] = loadavg()
        reps = []
        for rep in range(2):
            out = TMP / f"susp_live_{rep}.wav"
            player = play_at(NS, tone_long(7), "r84b_susplive")
            time.sleep(0.5)
            rec = Proc(["pw-record", "-P", "stream.capture.sink=true", "-P", "node.name=r84b_susprec",
                        "--target", NS, "--rate", "48000", "--channels", "2", "--format", "s16", str(out)])
            time.sleep(1.2)
            a1 = run(["pactl", "suspend-sink", NS, "1"], 6)
            time.sleep(0.4)
            st = run(["pactl", "list", "short", "sinks"], 6)
            node_state = [n["state"] for n in witness_nodes(NS) if n["name"] == NS]
            time.sleep(1.2)
            a2 = run(["pactl", "suspend-sink", NS, "0"], 6)
            rec.kill(signal.SIGTERM); time.sleep(0.4); rec.finish()
            for _ in range(90):
                if not player.alive(): break
                time.sleep(0.1)
            pres = player.finish()
            series = amp_series(out, win=0.1)
            r = {"rc": pres["rc"], "wall": pres["wall"], "out": "", "err": pres["err"], "timeout": False,
                 "cmd": f"pw-play {NS} + suspend-sink {NS} 1/0 mid-play"}
            extra = {"acts": [{"cmd": "suspend 1", "rc": a1["rc"], "err": a1["err"].splitlines()[:1]},
                              {"cmd": "suspend 0", "rc": a2["rc"], "err": a2["err"].splitlines()[:1]}],
                     "state_after_suspend": [l for l in st["out"].splitlines() if NS in l],
                     "node_state_after_suspend": node_state,
                     "amp_series": series, "loadavg": loadavg()}
            record_leg(probe, "susp_live", rep, r, extra)
            reps.append(compact(r, extra))
            base = amp_med(series, 0.6, 1.6); post = amp_med(series, 2.0, 3.6)
            reps[-1]["base_amp"] = base; reps[-1]["post_amp"] = post
            print(f"susp_live rep{rep} rc={r['rc']} wall={r['wall']} base={base} post={post} "
                  f"state={extra['state_after_suspend']} node={node_state}")
            try: out.unlink()
            except FileNotFoundError: pass
            time.sleep(0.4)
        results["susp_live"] = reps
        # idle suspend / unsuspend / play-into-suspended
        run(["pactl", "suspend-sink", NS, "0"], 6); time.sleep(0.3)
        st0 = [l for l in run(["pactl", "list", "short", "sinks"], 6)["out"].splitlines() if NS in l]
        a = run(["pactl", "suspend-sink", NS, "1"], 6); time.sleep(0.4)
        st1 = [l for l in run(["pactl", "list", "short", "sinks"], 6)["out"].splitlines() if NS in l]
        b = run(["pactl", "suspend-sink", NS, "0"], 6); time.sleep(0.4)
        st2 = [l for l in run(["pactl", "list", "short", "sinks"], 6)["out"].splitlines() if NS in l]
        player = play_at(NS, tone_short(), "r84b_suspwake")
        time.sleep(0.8)
        st3 = [l for l in run(["pactl", "list", "short", "sinks"], 6)["out"].splitlines() if NS in l]
        cons = consumers_of("r84b_suspwake")
        pres = player.finish()
        idle = {"state_idle_before": st0, "after_suspend1": st1, "after_suspend0": st2,
                "state_during_play": st3, "consumers": cons, "player_rc": pres["rc"], "player_wall": pres["wall"]}
        results["susp_idle_cycle"] = idle
        print("susp_idle_cycle:", json.dumps(idle))
        # refusal classes
        cls = {}
        for name, cmd in [("susp_bad2", ["pactl", "suspend-sink", NS, "2"]),
                          ("susp_nosuch", ["pactl", "suspend-sink", "no_such_r84b", "1"]),
                          ("susp_deadidx", ["pactl", "suspend-sink", "999999", "1"]),
                          ("vol_bogus", ["pactl", "set-sink-volume", NS, "bogus"]),
                          ("vol_frac", ["pactl", "set-sink-volume", NS, "50.5%"]),
                          ("vol_raw", ["pactl", "set-sink-volume", NS, "1.5"]),
                          ("vol_neg", ["pactl", "set-sink-volume", NS, "-10%"])]:
            rs = []
            for rep in range(2):
                r = run(cmd, 6)
                rs.append(compact(r))
                record_leg(probe, "cls_" + name, rep, r, {"loadavg": loadavg()})
            if name == "vol_frac" or name == "vol_raw":
                gv = run(["pactl", "get-sink-volume", NS], 6)
                rs.append({"get": gv["out"].strip()[:200]})
            cls[name] = rs
            print(f"cls/{name:12s} rc={[x['rc'] for x in rs if 'rc' in x]} err={rs[0]['err'][:2]} "
                  f"{rs[-1].get('get','') if isinstance(rs[-1], dict) else ''}")
        results["classes"] = cls
        results["loadavg_end"] = loadavg()
        (RCPTS / "pE-susp.json").write_text(json.dumps(results, indent=1))
    finally:
        if h: h.stop()
        run(["pactl", "suspend-sink", NS, "0"], 6)
        run(["pactl", "set-sink-volume", NS, "100%"], 6)
        unload_idx(s1["idx"], NS)

# ---------------- batch: monitor-stream deep ----------------
def parec_pin(args, dur, tag):
    o = TMP / f"mon_{tag}_{int(time.time()*1000)%10**7}.wav"
    p = Proc(["parec", "--latency-msec=50", "--rate=48000", "--channels=2",
              "--format=s16le", "--file-format=wav"] + args + [str(o)])
    return p, o

def sig_of(win):
    out = []
    for row in win:
        l1, r15, l2 = row.get("L@1000", 0), row.get("R@1500", 0), row.get("L@2000", 0)
        tag = "A+B" if (l1 > 500 and l2 > 500) else "A" if l1 > 500 else "B" if l2 > 500 else ("?" if row["peak"] else "-")
        out.append((row["t0"], tag, row["peak"]))
    tr = []; last = None
    for t, tag, pk in out:
        if tag != last: tr.append((t, tag, pk)); last = tag
    return tr

def fin_parec(p, o, dur, actions=None, probe=None, leg=None, rep=None):
    t0 = time.time(); acts = []
    for at, cmd in (actions or []):
        while time.time() - t0 < at: time.sleep(0.02)
        acts.append({"t": at, "cmd": " ".join(cmd) if isinstance(cmd, (list, tuple)) else cmd,
                     "res": run(cmd if isinstance(cmd, (list, tuple)) else cmd.split(), 6)})
    while time.time() - t0 < dur and p.alive(): time.sleep(0.05)
    try: os.killpg(p.p.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError): pass
    r = p.finish()
    w = windows(o)
    res = {"rc": r["rc"], "wall": r["wall"], "out": "", "err": r["err"], "timeout": False, "cmd": " ".join(p.p.args if hasattr(p.p, 'args') else [])}
    return res, {"size": file_hdr(o)["size"], "sig": sig_of(w), "win_head": w[:4], "acts": acts}, o

def b_mon():
    probe = "pF-monstream"; results = {}
    s1 = load_ns(NS); s2 = load_ns(NS2)
    assert s1["verified"] and s2["verified"], (s1, s2)
    try:
        results["loadavg_start"] = loadavg()
        for leg, argf in [
            ("sink_monitor",   lambda ia, ib: ["-d", f"{NS}.monitor"]),
            ("monA",           lambda ia, ib: ["-d", NS, "--monitor-stream", str(ia)]),
            ("monA_nod",       lambda ia, ib: ["--monitor-stream", str(ia)]),
            ("monA_bogusd",    lambda ia, ib: ["-d", "no_such_r84b", "--monitor-stream", str(ia)]),
            ("monA_othersink", lambda ia, ib: ["-d", NS2, "--monitor-stream", str(ia)]),
            ("mon_bad0",       lambda ia, ib: ["-d", NS, "--monitor-stream", "0"]),
            ("mon_deadidx",    lambda ia, ib: ["-d", NS, "--monitor-stream", "999999"]),
        ]:
            reps = []
            for rep in range(2):
                pa = play_at(NS, tone_a(), "r84b_ta"); pb = play_at(NS, tone_b(), "r84b_tb")
                time.sleep(0.6)
                ia, ib = si_index("r84b_ta"), si_index("r84b_tb")
                p, o = parec_pin(argf(ia, ib), 3.4, leg)
                r, x, _o = fin_parec(p, o, 3.4)
                extra = {"idxA": ia, "idxB": ib, **x, "loadavg": loadavg()}
                record_leg(probe, leg, rep, r, extra)
                reps.append(compact(r, extra))
                print(f"{leg:16s} rc={[r['rc']]} size={x['size']} sig={x['sig']} idxA={ia}")
                pa.kill(); pa.finish(); pb.kill(); pb.finish()
                try: _o.unlink()
                except FileNotFoundError: pass
                time.sleep(0.3)
            results[leg] = reps
        # source-output idx as monitor-stream (mode replay)
        reps = []
        for rep in range(2):
            rec0 = Proc(["pw-record", "-P", "stream.capture.sink=true", "-P", "node.name=r84b_srcout",
                         "--target", NS, str(TMP / "so.wav")])
            pa = play_at(NS, tone_a(), "r84b_ta"); time.sleep(0.7)
            so = si_index("r84b_srcout"); ia = si_index("r84b_ta")
            p, o = parec_pin(["-d", NS, "--monitor-stream", str(so)], 2.6, "soidx")
            r, x, _o = fin_parec(p, o, 2.6)
            extra = {"so": so, "idxA": ia, **x}
            record_leg(probe, "mon_soidx", rep, r, extra)
            reps.append(compact(r, extra))
            print(f"mon_soidx        rc={[r['rc']]} size={x['size']} sig={x['sig']} so={so}")
            rec0.kill(); rec0.finish(); pa.kill(); pa.finish()
            try: _o.unlink(); (TMP / "so.wav").unlink()
            except FileNotFoundError: pass
            time.sleep(0.3)
        results["mon_soidx"] = reps
        # mid-run events
        for leg, mode in [("monA_kill", "kill"), ("monA_move", "move"), ("monA_sivol", "sivol"),
                          ("monA_simute", "simute")]:
            reps = []
            for rep in range(2):
                pa = play_at(NS, tone_long(9), "r84b_ta"); pb = play_at(NS, tone_b(), "r84b_tb")
                time.sleep(0.6)
                ia, ib = si_index("r84b_ta"), si_index("r84b_tb")
                p, o = parec_pin(["-d", NS, "--monitor-stream", str(ia)], 6.6, leg)
                acts = []
                if mode == "kill":
                    t0 = time.time()
                    while time.time() - t0 < 2.4: time.sleep(0.02)
                    pa.kill()
                    acts.append({"t": 2.4, "cmd": "kill A", "res": {"rc": 0, "err": ""}})
                    r, x, _o = fin_parec(p, o, 6.6)
                elif mode == "move":
                    r, x, _o = fin_parec(p, o, 6.6, actions=[(2.4, ["pactl", "move-sink-input", str(ia), NS2])])
                elif mode == "sivol":
                    r, x, _o = fin_parec(p, o, 6.6, actions=[(2.4, ["pactl", "set-sink-input-volume", str(ia), "50%"])])
                else:
                    r, x, _o = fin_parec(p, o, 6.6, actions=[(2.4, ["pactl", "set-sink-input-mute", str(ia), "1"]),
                                                              (4.4, ["pactl", "set-sink-input-mute", str(ia), "0"])])
                post = consumers_of("r84b_ta")
                extra = {"idxA": ia, "post_links": post, **x, "loadavg": loadavg()}
                if mode == "kill":
                    # growth witness: sample size right after kill and at end
                    time.sleep(0.4)
                    sz1 = file_hdr(o)["size"]
                    time.sleep(1.2)
                    sz2 = file_hdr(o)["size"]
                    extra["size_after_kill_1"] = sz1; extra["size_after_kill_2"] = sz2
                record_leg(probe, leg, rep, r, extra)
                reps.append(compact(r, extra))
                print(f"{leg:16s} rc={[r['rc']]} sig={x['sig']} post={post[:3]} acts={[(a['cmd'], a['res']['rc']) for a in x['acts']]}")
                for xx in (pa, pb):
                    if xx.alive(): xx.kill()
                    xx.finish()
                try: _o.unlink()
                except FileNotFoundError: pass
                run(["pactl", "set-sink-input-volume", str(ia), "100%"], 4)
                time.sleep(0.3)
            results[leg] = reps
        # sticky stream-restore replay (short window, repaired)
        reps = []
        for rep in range(2):
            pa = play_at(NS, tone_long(4), "r84b_ta")
            time.sleep(0.6)
            ia = si_index("r84b_ta")
            wr = run(["pactl", "set-sink-input-volume", str(ia), "30%"], 6)
            time.sleep(0.6)
            pa.kill(); pa.finish()
            time.sleep(0.5)
            pb2 = play_at(NS, tone_long(4), "r84b_ta")
            time.sleep(0.7)
            ib2 = si_index("r84b_ta")
            si = [x for x in si_witness("r84b_ta")]
            tap = parec_pin(["-d", NS, "--monitor-stream", str(ib2)], 2.0, "sticky")
            r, x, _o = fin_parec(tap[0], tap[1], 2.0)
            amp = amp_med([(w["t0"], w["peak"]) for w in windows(_o)], 0.4, 1.8)
            extra = {"write_rc": wr["rc"], "si_after_respawn": si, "tap_amp": amp, **x}
            record_leg(probe, "sticky_restore", rep, r, extra)
            reps.append(compact(r, extra))
            print(f"sticky_restore   rep{rep} write_rc={wr['rc']} si={si} tap_amp={amp}")
            # repair
            run(["pactl", "set-sink-input-volume", str(ib2), "100%"], 6)
            time.sleep(0.3)
            pb2.kill(); pb2.finish()
            try: _o.unlink()
            except FileNotFoundError: pass
            # verify repair with a fresh respawn
            pc = play_at(NS, tone_short(), "r84b_ta"); time.sleep(0.6)
            verify = si_witness("r84b_ta")
            pc.kill(); pc.finish()
            reps[-1]["repair_verify"] = verify
            print(f"                 repair_verify={verify}")
            time.sleep(0.3)
        results["sticky_restore"] = reps
        results["loadavg_end"] = loadavg()
        (RCPTS / "pF-monstream.json").write_text(json.dumps(results, indent=1))
    finally:
        unload_idx(s1["idx"], NS); unload_idx(s2["idx"], NS2)

# ---------------- batch: ebusy leg ----------------
def b_ebusy():
    probe = "pH-ebusy"; results = {}
    try:
        p = play_at(SPEAKER, tone_long(6), "r84b_ebusy")
        time.sleep(1.0)
        st0 = pcm_status(0, 0, "p")
        a1 = run(["aplay", "-D", "hw:0,0", tone_short()], 8)
        st1 = pcm_status(0, 0, "p")
        a2 = run(["aplay", "-D", "plughw:0,0", tone_short()], 8)
        st2 = pcm_status(0, 0, "p")
        p.kill(); pres = p.finish()
        time.sleep(0.8)
        st3 = pcm_status(0, 0, "p")
        a3 = run(["aplay", "-D", "hw:0,0", tone_short()], 8)
        results = {"pcm_status_before": st0, "aplay_hw00_while_busy": compact(a1),
                   "pcm_status_after1": st1, "aplay_plughw_while_busy": compact(a2),
                   "pcm_status_after2": st2, "player_rc": pres["rc"], "player_wall": pres["wall"],
                   "pcm_status_after_kill": st3, "aplay_hw00_after_kill": compact(a3),
                   "loadavg": loadavg()}
        for name, r in [("aplay_hw00_while_busy", a1), ("aplay_plughw_while_busy", a2), ("aplay_hw00_after_kill", a3)]:
            record_leg(probe, name, 0, r, {"loadavg": loadavg()})
        print(json.dumps({k: (v if not isinstance(v, dict) else {kk: v[kk] for kk in ('rc','wall','err')}) for k, v in results.items()}, indent=1)[:2000])
        (RCPTS / "pH-ebusy.json").write_text(json.dumps(results, indent=1))
    finally:
        pass

# ---------------- main ----------------
if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "replay"
    if what == "replay": b_replay()
    elif what == "plugin": b_plugin()
    elif what == "props": b_props()
    elif what == "vol": b_vol()
    elif what == "hogvol": b_vol(probe="pD-hogvol", hog=True)
    elif what == "susp": b_susp()
    elif what == "hogsusp": b_susp(hog=True)
    elif what == "mon": b_mon()
    elif what == "ebusy": b_ebusy()
    else: sys.exit(f"unknown batch {what}")
    print("DONE", what)
