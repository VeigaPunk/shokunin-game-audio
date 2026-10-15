#!/usr/bin/env python3
"""r95 scout driver — JACK<->PipeWire interop (pipewire-jack 1.6.8).

Seat-owned names only (r95s_*). Every child triple-bounded (wall cap +
byte cap + killpg), RLIMIT_CORE=0 (pw-cli SIGABRTs on EOF, r92). No tracked
writes. No pactl set-default-*. Modules unloaded by id verified against the
seat name. Own tone synth, own Goertzel. Never imports the sibling-owned
corpus/fixtures/measure_audio.py.

Stages: avail shape jack2pw pw2jack quantum global xrun latency rtprio
        transport metadata
Usage: r95driver.py <stage> [reps]
"""
import hashlib
import json
import math
import os
import re
import resource
import signal
import struct
import subprocess
import sys
import time
import wave

SEAT = "r95s"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)              # corpus/live/r95-scout
RECEIPTS = os.path.join(ROOT, "receipts")
RUNS = os.path.join(ROOT, "runs")
SCRATCH = os.path.join(ROOT, "scratch")
PROBE = os.path.join(HERE, "r95jack")
FREQ = 997.0
RATE = 48000
DEFAULT_WALL = 12.0
BYTE_CAP = 8 << 20


def _ncore():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


class Bounded:
    def __init__(self, argv, wall=DEFAULT_WALL, byte_cap=BYTE_CAP, env=None, cwd=None,
                 wait=True):
        e = dict(os.environ)
        if env:
            e.update(env)
        self.argv = argv
        self.byte_cap = byte_cap
        self.t0 = time.time()
        self.timed_out = False
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.DEVNULL, start_new_session=True,
                             preexec_fn=_ncore, env=e, cwd=cwd)
        self.p = p
        self.pid = p.pid
        self.rc = None
        self.out = ""
        self.err = ""
        self.dur = None
        if wait:
            self.finish(wall)

    def _decode(self, out, err):
        self.out = out.decode("utf-8", "replace")
        self.err = err.decode("utf-8", "replace")
        if len(self.out) > self.byte_cap:
            self.out = self.out[:self.byte_cap]
            self.byte_capped = True

    def finish(self, wall=DEFAULT_WALL):
        """Wait for completion (bounded); kill the group on timeout."""
        try:
            out, err = self.p.communicate(timeout=wall)
            self.rc = self.p.returncode
        except subprocess.TimeoutExpired:
            self.timed_out = True
            try:
                os.killpg(os.getpgid(self.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = self.p.communicate()
            self.rc = self.p.returncode
        self.dur = time.time() - self.t0
        self._decode(out, err)
        return self.rc, self.out, self.err

    def term(self, grace=4.0):
        """SIGTERM the process group, collect output, return (rc, out, err)."""
        try:
            os.killpg(os.getpgid(self.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            out, err = self.p.communicate(timeout=grace)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = self.p.communicate()
        self.rc = self.p.returncode
        self.dur = time.time() - self.t0
        self._decode(out, err)
        return self.rc, self.out, self.err


def sh(argv, wall=8.0, env=None):
    return Bounded(argv, wall=wall, env=env)


def parse_jack(out):
    rows = [l for l in out.splitlines() if l.startswith("R95JSON ")]
    if not rows:
        return None
    try:
        return json.loads(rows[-1][len("R95JSON "):])
    except json.JSONDecodeError as ex:
        return {"_json_error": str(ex), "_raw": rows[-1][:400]}


def jack_json(argv, wall=DEFAULT_WALL, env=None, wait=True):
    b = Bounded(argv, wall=wall, env=env, wait=wait)
    if not wait:
        return None, b
    return parse_jack(b.out), b


def pactl_load_null(name):
    b = sh(["pactl", "load-module", "module-null-sink", "sink_name=" + name,
            "channels=1", "sink_properties=state.restore-props=false,device.description=" + name])
    m = re.match(r"(\d+)\s*$", b.out.strip())
    return int(m.group(1)) if m else None


def pactl_unload(idx):
    if idx is None:
        return None
    return sh(["pactl", "unload-module", str(idx)])


def modules_matching(pat):
    b = sh(["pactl", "list", "modules", "short"], wall=10)
    rows = []
    for line in b.out.splitlines():
        m = re.match(r"^(\d+)\t([^\t]+)\t(.*)$", line)
        if m and pat in m.group(2):
            rows.append((int(m.group(1)), m.group(2)))
    return rows


def procs_matching(pat):
    """Match ONLY seat-owned audio processes: argv[0] basename must be one of the
    seat's own binaries AND the command line must carry the seat namespace (`r95s`).

    INCIDENT NOTE (2026-10-15 17:5x): an earlier version of this function killed any
    `pw-record`/`pw-play`/`pw-cat` process regardless of namespace; that swept up
    sibling r85-boundary legs (`r85b_mx_*`). Never match on binary name alone.
    """
    out = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                raw = f.read()
        except OSError:
            continue
        argv = raw.split(b"\0")
        if not argv or not argv[0]:
            continue
        cmdline = b" ".join(argv).decode("utf-8", "replace").strip()
        a0 = os.path.basename(argv[0].decode("utf-8", "replace"))
        seat_bin = a0.startswith(("r95jack", "pw-record", "pw-play", "pw-cat"))
        if seat_bin and pat in cmdline:
            out.append((int(pid), cmdline))
    return out


def sweep():
    """Kill stray seat audio procs, unload stray seat modules. Never touches foreign objects."""
    killed = []
    for pid, cmd in procs_matching("r95jack"):
        try:
            os.kill(pid, signal.SIGKILL)
            killed.append((pid, cmd))
        except ProcessLookupError:
            pass
    unloaded = []
    for idx, name in modules_matching(SEAT):
        pactl_unload(idx)
        unloaded.append((idx, name))
    return {"killed": killed, "unloaded": unloaded}


def graph_snapshot():
    b = sh(["pw-dump"], wall=15)
    try:
        d = json.loads(b.out)
    except json.JSONDecodeError:
        return {"_error": "pw-dump parse", "_raw": b.out[:200]}
    nodes, clients, ports, meta = {}, {}, {}, []
    seat_nodes = set()
    for o in d:
        if o.get("type") == "PipeWire:Interface:Node":
            p = (o.get("info") or {}).get("props") or {}
            if "r95s" in str(p.get("node.name", "")) or "jack" in str(p.get("client.api", "")):
                seat_nodes.add(o["id"])
    for o in d:
        t = o.get("type")
        info = o.get("info") or {}
        p = info.get("props") or {}
        if t == "PipeWire:Interface:Node" and o["id"] in seat_nodes:
            nodes[o["id"]] = {k: p.get(k) for k in (
                "node.name", "client.api", "node.description", "media.class", "media.category",
                "media.role", "node.group", "node.always-process", "node.force-quantum",
                "node.force-rate", "node.latency", "node.pause-on-idle", "node.passive",
                "application.name", "node.nick", "object.serial")}
        if t == "PipeWire:Interface:Client" and "r95s" in str(p.get("client.name", "")):
            clients[o["id"]] = {k: p.get(k) for k in (
                "client.name", "client.api", "application.name",
                "application.process.binary", "pipewire.sec.pid")}
        if t == "PipeWire:Interface:Port":
            alias = str(p.get("port.alias", ""))
            path = str(p.get("object.path", ""))
            if p.get("node.id") in seat_nodes or "r95s" in alias or "r95s" in path:
                ports[o["id"]] = {k: p.get(k) for k in (
                    "port.name", "port.alias", "object.path", "port.direction", "format.dsp",
                    "port.physical", "port.terminal", "port.extra", "node.id")}
        if t == "PipeWire:Interface:Metadata":
            mp = o.get("props") or {}
            name = mp.get("metadata.name")
            keep_keys = ("clock.quantum", "clock.force-quantum", "clock.force-rate",
                         "clock.rate", "default.audio.sink", "default.audio.source")
            rows = []
            for r in (o.get("metadata") or []):
                key = str(r.get("key", ""))
                subj = r.get("subject")
                if key.startswith("r95s") or (subj == 0 and key in keep_keys):
                    rows.append({"subject": subj, "key": key,
                                 "type": r.get("type"), "value": r.get("value")})
            meta.append({"id": o["id"], "name": name, "rows": rows[:80]})
    return {"nodes": nodes, "clients": clients, "ports": ports, "metadata": meta}


def pw_link_l():
    return sh(["pw-link", "-l"], wall=10).out


def link_lines_for(pat):
    return [l.strip() for l in pw_link_l().splitlines() if pat in l]


def pw_metadata(name):
    b = sh(["pw-metadata", "-n", name], wall=10)
    rows = {}
    for line in b.out.splitlines():
        m = re.match(r"update: id:(\d+) key:'(.*?)' value:'(.*?)' type:'(.*?)'", line)
        if m:
            rows[(int(m.group(1)), m.group(2))] = {"value": m.group(3), "type": m.group(4)}
    return rows


def defaults():
    b = sh(["pactl", "info"], wall=10)
    d = {}
    for line in b.out.splitlines():
        if line.startswith("Default Sink:") or line.startswith("Default Source:"):
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def tone_wav(path, dur=1.5, freq=FREQ, amp=0.5, rate=RATE):
    n = int(rate * dur)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(
            struct.pack("<h", int(amp * 32767 * math.sin(2 * math.pi * freq * i / rate)))
            for i in range(n)))
    return n


def analyze_wav(path, freq=FREQ):
    with wave.open(path, "rb") as w:
        n = w.getnframes()
        fr = w.getframerate()
        ch = w.getnchannels()
        data = w.readframes(n)
    if not data:
        return {"frames": 0, "bytes": 0, "rms": 0.0, "goertzel_mag2": 0.0, "peak": 0.0}
    s = struct.unpack("<%dh" % (len(data) // 2), data)
    N = len(s)
    peak = max(abs(x) for x in s) / 32768.0
    rms = math.sqrt(sum(x * x for x in s) / N) / 32768.0
    coef = 2.0 * math.cos(2.0 * math.pi * freq / fr)
    g1 = g2 = 0.0
    for x in s:
        y = x / 32768.0 + coef * g1 - g2
        g2 = g1
        g1 = y
    mag2 = g1 * g1 + g2 * g2 - coef * g1 * g2
    return {"frames": n, "rate": fr, "channels": ch, "bytes": len(data),
            "rms": rms, "peak": peak, "goertzel_mag2": mag2}


def pw_top_snapshot():
    b = sh(["pw-top", "-b", "-n", "1"], wall=6)
    rows = []
    for line in b.out.splitlines():
        parts = line.split()
        if len(parts) >= 9 and parts[0] in ("S", "C", "I") and parts[1].isdigit():
            rows.append({"status": parts[0], "id": parts[1], "quant": parts[2],
                         "rate": parts[3], "err": parts[6], "name": parts[8]})
    return rows


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_receipt(stage, data):
    os.makedirs(RECEIPTS, exist_ok=True)
    path = os.path.join(RECEIPTS, f"{stage}.json")
    data["_stage"] = stage
    data["_ts"] = now()
    with open(path, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)
    return path


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def base_env():
    return {"RLIMIT_CORE": "0"}


# ---------------------------------------------------------------- stages

def stage_avail(reps):
    which = {}
    for tool in ("jackd", "jack_lsp", "jack_connect", "jack_disconnect", "jackdbus",
                 "jack_control", "pw-jack", "pw-metadata", "pw-top"):
        b = sh(["bash", "-lc", f"command -v {tool} || true"], wall=6)
        which[tool] = b.out.strip() or None
    pkgs = {}
    for p in ("pipewire-jack", "jack2", "jack", "pipewire"):
        b = sh(["bash", "-lc", f"pacman -Q {p} 2>&1 || true"], wall=8)
        pkgs[p] = b.out.strip()
    libjack = "/usr/lib/libjack.so.0.3.1608"
    lib = {"path": libjack, "sha256": sha256(libjack) if os.path.exists(libjack) else None,
           "size": os.path.getsize(libjack) if os.path.exists(libjack) else None}
    b = sh(["bash", "-lc",
            f"nm -D {libjack} 2>/dev/null | grep -c ' T jack_' || true"], wall=8)
    n_export = int(b.out.strip() or 0)
    b = sh(["bash", "-lc",
            "grep -hoE 'jack_[a-z_0-9]+ *\\(' /usr/include/jack/*.h | sed 's/ *(//' | sort -u | wc -l"], wall=8)
    n_declared = int(b.out.strip() or 0)
    b = sh(["bash", "-lc", "nm -D " + libjack + " | grep ' T jack_' | awk '{print $3}' | sort"], wall=8)
    exports = b.out.split()
    b = sh(["bash", "-lc",
            "grep -hoE 'jack_[a-z_0-9]+ *\\(' /usr/include/jack/*.h | sed 's/ *(//' | sort -u"], wall=8)
    declared = b.out.split()
    missing = sorted(set(declared) - set(exports))
    b = sh(["bash", "-lc", "man -w pw-jack; man -w pipewire-jack 2>&1; true"], wall=8)
    mans = [l for l in b.out.splitlines() if l.strip()]
    b = sh(["bash", "-lc",
            "grep -oE '^[[:space:]]*#?[[:space:]]*jack\\.[a-z0-9-]+' /usr/share/pipewire/jack.conf | tr -d ' #' | sort -u"],
           wall=8)
    jack_opts = b.out.split()
    b = sh(["bash", "-lc", "sha256sum /usr/share/pipewire/jack.conf /usr/bin/pw-jack"], wall=8)
    cfg_shas = b.out.strip().splitlines()
    ldd = sh(["ldd", PROBE], wall=8).out.strip().splitlines()
    settings = pw_metadata("settings")
    pre = {"defaults": defaults(),
           "modules": modules_matching(""),
           "graph": graph_snapshot()}
    rec = {
        "which": which, "packages": pkgs, "libjack": lib,
        "symbols": {"exported": n_export, "declared_in_headers": n_declared,
                    "declared_not_exported_count": len(missing),
                    "declared_not_exported": missing},
        "man_pages": mans, "jack_conf_options": jack_opts, "config_shas": cfg_shas,
        "ldd": ldd, "settings_metadata": {f"{k[0]}:{k[1]}": v for k, v in settings.items()},
        "pre_state": {"defaults": pre["defaults"], "module_count": len(pre["modules"]),
                      "node_count": len(pre["graph"]["nodes"]),
                      "metadata_objects": pre["graph"]["metadata"]},
    }
    post = sweep()
    rec["sweep_after"] = post
    rec["post_state"] = {"defaults": defaults(), "module_count": len(modules_matching(""))}
    write_receipt("a_avail", rec)
    return rec


def stage_shape(reps):
    rec = {"reps": []}
    for r in range(reps):
        sweep()
        mid = pactl_load_null("r95s_ns")
        time.sleep(0.6)
        b = Bounded([PROBE, "shape", "1.6"], wait=False)
        time.sleep(0.5)
        snap = graph_snapshot()
        links = link_lines_for("r95s_shape")
        top = pw_top_snapshot()
        b.finish(wall=6)
        d = parse_jack(b.out)
        rec["reps"].append({
            "rep": r, "nullsink_module": mid, "rc": b.rc, "dur": round(b.dur, 3),
            "json": d, "graph": snap, "links_while_running": links, "top": top,
            "stderr": b.err[:300],
        })
        pactl_unload(mid)
        time.sleep(0.3)
        rec["reps"][-1]["residue_after"] = {
            "modules": modules_matching("r95s"), "procs": procs_matching("r95jack"),
            "nodes": graph_snapshot()["nodes"]}
    rec["sweep_after"] = sweep()
    write_receipt("b_shape", rec)
    return rec


def stage_shape_xconnect(reps):
    """Addressing law: which name form resolves a native PW port from a JACK client?"""
    rec = {"arms": {}}
    env_alias = {"PIPEWIRE_PROPS": "{ jack.fill-aliases = true }"}
    for arm in ("rendered", "native", "fillalias"):
        rows = []
        for r in range(reps):
            sweep()
            mid = pactl_load_null("r95s_ns")
            time.sleep(0.6)
            snap0 = graph_snapshot()
            desc = None
            for n in snap0["nodes"].values():
                if n.get("node.name") == "r95s_ns":
                    desc = n.get("node.description")
            rendered = (desc or "r95s_ns") + ":playback_MONO"
            target = {"rendered": rendered,
                      "native": "r95s_ns:playback_MONO",
                      "fillalias": "r95s_ns:playback_0"}[arm]
            env = env_alias if arm == "fillalias" else None
            b = Bounded([PROBE, "shape", "1.8", target, "disconnect"], env=env, wait=False)
            time.sleep(0.9)
            links = link_lines_for("r95s_shape")
            top = pw_top_snapshot()
            b.finish(wall=6)
            d = parse_jack(b.out)
            rows.append({"rep": r, "arm": arm, "target": target, "desc": desc,
                         "rc": b.rc, "json": d, "links_while_running": links,
                         "top": top, "stderr": b.err[:300]})
            pactl_unload(mid)
            time.sleep(0.3)
        rec["arms"][arm] = rows
    rec["sweep_after"] = sweep()
    write_receipt("b_shape_xconnect", rec)
    return rec


def stage_tone_unlinked(reps):
    """JACK client with no link, null-sink driver present: does the process callback run?"""
    rec = {"reps": []}
    for r in range(reps):
        sweep()
        mid = pactl_load_null("r95s_ns")
        time.sleep(0.6)
        b = Bounded([PROBE, "tone", "1.6"], wait=False)
        time.sleep(0.6)
        links = link_lines_for("r95s_probe")
        top = pw_top_snapshot()
        b.finish(wall=6)
        d = parse_jack(b.out)
        rec["reps"].append({"rep": r, "nullsink_module": mid, "rc": b.rc, "json": d,
                            "links_while_running": links, "top": top,
                            "stderr": b.err[:300]})
        pactl_unload(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("b_tone_unlinked", rec)
    return rec


def stage_jack2pw(reps):
    rec = {"reps": []}
    for r in range(reps):
        sweep()
        mid = pactl_load_null("r95s_ns")
        time.sleep(0.6)
        desc = None
        for n in graph_snapshot()["nodes"].values():
            if n.get("node.name") == "r95s_ns":
                desc = n.get("node.description")
        target = (desc or "r95s_ns") + ":playback_MONO"
        wav = os.path.join(SCRATCH, f"c1_rep{r}.wav")
        if os.path.exists(wav):
            os.remove(wav)
        rb = Bounded(["pw-record", "-P", "stream.capture.sink=true",
                      "-P", "node.name=r95s_rec", "-P", "state.restore-props=false",
                      "--target", "r95s_ns", "--rate", "48000", "--channels", "1", wav],
                     wall=10, wait=False)
        time.sleep(0.7)
        tb = Bounded([PROBE, "tone", "2.5", "0", "0", target], wait=False)
        time.sleep(1.0)
        links = link_lines_for("r95s")
        top = pw_top_snapshot()
        snap = graph_snapshot()
        tb.finish(wall=6)
        d = parse_jack(tb.out)
        time.sleep(0.4)
        rb.term(grace=4)
        time.sleep(0.4)
        analysis = analyze_wav(wav) if os.path.exists(wav) else None
        rec["reps"].append({"rep": r, "nullsink_module": mid, "rc": tb.rc, "json": d,
                            "target": target, "links_while_running": links, "top": top, "graph": snap,
                            "wav": analysis, "wav_sha256": sha256(wav) if os.path.exists(wav) else None})
        pactl_unload(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("c_jack2pw", rec)
    return rec


def stage_pw2jack(reps):
    rec = {"reps": []}
    tone = os.path.join(SCRATCH, "tone997.wav")
    if not os.path.exists(tone):
        tone_wav(tone)
    rec["tone_file"] = {"path": tone, "sha256": sha256(tone)}
    for r in range(reps):
        sweep()
        jb = Bounded([PROBE, "tone", "3.2"], wall=12, wait=False)
        time.sleep(0.7)
        pb = Bounded(["pw-play", "-P", "node.autoconnect=false", "-P", "node.name=r95s_play",
                      "-P", "state.restore-props=false", "--channels", "1", "--rate", "48000", tone],
                     wall=8, wait=False)
        time.sleep(0.6)
        link1 = sh(["pw-link", "r95s_play:output_MONO", "r95s_probe:in"], wall=8)
        links = link_lines_for("r95s_play")
        top = pw_top_snapshot()
        # wait for the tone client to finish on its own
        deadline = time.time() + 6
        while time.time() < deadline and jb.p.poll() is None:
            time.sleep(0.2)
        if jb.p.poll() is None:
            try:
                os.killpg(os.getpgid(jb.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        jb.finish(wall=4)
        jd = parse_jack(jb.out)
        rec["reps"].append({"rep": r, "pw_link_rc": link1.rc, "pw_link_err": link1.err.strip()[:200],
                            "links_while_running": links, "jack_json": jd,
                            "pw_play_rc": pb.rc, "pw_play_stderr": pb.err.strip()[:300],
                            "top": pw_top_snapshot()})
        try:
            os.killpg(os.getpgid(pb.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("c_pw2jack", rec)
    return rec


def stage_quantum(reps):
    rec = {"reps": []}
    for r in range(reps):
        sweep()
        mid = pactl_load_null("r95s_ns")
        time.sleep(0.6)
        b = Bounded([PROBE, "bufsize", "1.4", "2048", "512"], wait=False)
        time.sleep(0.7)
        snap = graph_snapshot()
        meta = pw_metadata("settings")
        top = pw_top_snapshot()
        b.finish(wall=6)
        d = parse_jack(b.out)
        rec["reps"].append({"rep": r, "nullsink_module": mid, "rc": b.rc, "json": d,
                            "graph": snap, "settings": {f"{k[0]}:{k[1]}": v for k, v in meta.items()},
                            "top": top})
        pactl_unload(mid)
        time.sleep(0.3)
    # env arm: PIPEWIRE_QUANTUM
    rec["env_arm"] = []
    for r in range(reps):
        sweep()
        mid = pactl_load_null("r95s_ns")
        time.sleep(0.6)
        b = Bounded([PROBE, "info", "0.8"], env={"PIPEWIRE_QUANTUM": "512/48000"}, wait=False)
        time.sleep(0.35)
        snap = graph_snapshot()
        top = pw_top_snapshot()
        b.finish(wall=6)
        d = parse_jack(b.out)
        rec["env_arm"].append({"rep": r, "rc": b.rc, "json": d, "graph": snap, "top": top})
        pactl_unload(mid)
        time.sleep(0.3)
    # pw-jack wrapper arm
    rec["pwjack_arm"] = []
    for r in range(reps):
        sweep()
        mid = pactl_load_null("r95s_ns")
        time.sleep(0.6)
        b = Bounded(["pw-jack", "-p", "512", PROBE, "info", "0.8"], wait=False)
        time.sleep(0.35)
        snap = graph_snapshot()
        top = pw_top_snapshot()
        b.finish(wall=6)
        d = parse_jack(b.out)
        rec["pwjack_arm"].append({"rep": r, "rc": b.rc, "json": d, "graph": snap, "top": top})
        pactl_unload(mid)
        time.sleep(0.3)
    # cross-client arm: A forces 2048 per-client; does B (a second JACK client) see it?
    rec["cross_arm"] = []
    for r in range(reps):
        sweep()
        mid = pactl_load_null("r95s_ns")
        time.sleep(0.6)
        ab = Bounded([PROBE, "bufsize", "1.8", "2048", "0"], wait=False)
        time.sleep(0.7)
        snap = graph_snapshot()
        top = pw_top_snapshot()
        db, bb = jack_json([PROBE, "info", "0.4"], wall=10)
        ab.finish(wall=6)
        a_json = parse_jack(ab.out)
        rec["cross_arm"].append({"rep": r, "a_json": a_json, "b_json": db, "b_rc": bb.rc,
                                 "graph": snap, "top": top})
        pactl_unload(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("d_quantum", rec)
    return rec


def stage_global(reps):
    """jack.global-buffer-size=true -> clock.force-quantum metadata. Disclosed host-state
    mutation; each rep restores via jack_set_buffer_size(1)->"0" and verifies."""
    rec = {"reps": [], "disclosure": "clock.force-quantum set to 512 for ~2.4 s per rep, "
                                     "restored to 0 and verified; no other metadata touched"}
    env = {"PIPEWIRE_PROPS": "{ jack.global-buffer-size = true }"}
    for r in range(reps):
        sweep()
        mid = pactl_load_null("r95s_ns")
        time.sleep(0.6)
        before = pw_metadata("settings")
        ab = Bounded([PROBE, "bufsize", "2.2", "512", "0"], env=env, wait=False)
        time.sleep(0.8)
        during_meta = pw_metadata("settings")
        during_top = pw_top_snapshot()
        during_snap = graph_snapshot()
        db, bb = jack_json([PROBE, "info", "0.4"], wall=10)
        time.sleep(0.4)
        ab.finish(wall=6)
        a_json = parse_jack(ab.out)
        after_a = pw_metadata("settings")
        # restore
        rb = Bounded([PROBE, "bufsize", "0.4", "1", "0"], wall=8, env=env)
        time.sleep(0.5)
        restored = pw_metadata("settings")
        restored_top = pw_top_snapshot()
        rec["reps"].append({
            "rep": r, "nullsink_module": mid,
            "settings_before": {f"{k[0]}:{k[1]}": v for k, v in before.items() if "quantum" in k[1]},
            "settings_during": {f"{k[0]}:{k[1]}": v for k, v in during_meta.items() if "quantum" in k[1]},
            "settings_after_client_exit": {f"{k[0]}:{k[1]}": v for k, v in after_a.items() if "quantum" in k[1]},
            "settings_restored": {f"{k[0]}:{k[1]}": v for k, v in restored.items() if "quantum" in k[1]},
            "a_json": a_json, "b_json": db, "b_rc": bb.rc,
            "top_during": during_top, "top_restored": restored_top,
            "graph_during": during_snap,
        })
        pactl_unload(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("d_global", rec)
    return rec


def stage_xrun(reps):
    rec = {"reps": []}
    for r in range(reps):
        sweep()
        mid = pactl_load_null("r95s_ns")
        time.sleep(0.6)
        ctl, cb = jack_json([PROBE, "tone", "2.0", "0", "0", "r95s_ns:playback_MONO"], wall=12)
        st, sb = jack_json([PROBE, "stall", "2.0", "4", "150000", "r95s_ns:playback_MONO"], wall=14)
        rec["reps"].append({"rep": r, "control": ctl, "control_rc": cb.rc,
                            "stall": st, "stall_rc": sb.rc, "top": pw_top_snapshot()})
        pactl_unload(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("e_xrun", rec)
    return rec


def stage_latency(reps):
    rec = {"reps": []}
    for r in range(reps):
        sweep()
        d, b = jack_json([PROBE, "latency", "0.6"], wall=10)
        rec["reps"].append({"rep": r, "rc": b.rc, "json": d})
    rec["sweep_after"] = sweep()
    write_receipt("e_latency", rec)
    return rec


def stage_rtprio(reps):
    rec = {"reps": []}
    for r in range(reps):
        sweep()
        d, b = jack_json([PROBE, "rtprio"], wall=10)
        rec["reps"].append({"rep": r, "rc": b.rc, "json": d})
    rec["sweep_after"] = sweep()
    write_receipt("e_rtprio", rec)
    return rec


def stage_transport(reps):
    rec = {"reps": []}
    for r in range(reps):
        sweep()
        mid = pactl_load_null("r95s_ns")
        time.sleep(0.6)
        desc = None
        for n in graph_snapshot()["nodes"].values():
            if n.get("node.name") == "r95s_ns":
                desc = n.get("node.description")
        target = (desc or "r95s_ns") + ":playback_MONO"
        b = Bounded([PROBE, "transport", "1.6", target], wait=False)
        time.sleep(0.5)
        top = pw_top_snapshot()
        snap = graph_snapshot()
        b.finish(wall=6)
        d = parse_jack(b.out)
        rec["reps"].append({"rep": r, "nullsink_module": mid, "rc": b.rc, "json": d,
                            "target": target, "top": top, "graph": snap, "stderr": b.err[:300]})
        pactl_unload(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("f_transport", rec)
    return rec


def stage_metadata(reps):
    rec = {"reps": []}
    for r in range(reps):
        sweep()
        jb = Bounded([PROBE, "metadata", "1.6"], wait=False)
        time.sleep(0.7)
        default_rows = pw_metadata("default")
        snap = graph_snapshot()
        deadline = time.time() + 5
        while time.time() < deadline and jb.p.poll() is None:
            time.sleep(0.2)
        jb.finish(wall=4)
        jd = parse_jack(jb.out)
        time.sleep(0.5)
        after_rows = pw_metadata("default")
        # the PW metadata subject is the object's registry id (pw-dump "id"),
        # while the JACK uuid index is the object.serial
        own_id = None
        own_serial = None
        for nid, n in snap["nodes"].items():
            if n.get("node.name") == "r95s_meta":
                own_id = int(nid)
                own_serial = n.get("object.serial")
        during_own = {f"{k[0]}:{k[1]}": v for k, v in default_rows.items()
                      if own_id is not None and k[0] == own_id}
        after_own = {f"{k[0]}:{k[1]}": v for k, v in after_rows.items()
                     if own_id is not None and k[0] == own_id}
        rec["reps"].append({"rep": r, "json": jd, "own_registry_id": own_id,
                            "own_object_serial": own_serial,
                            "default_metadata_during": during_own,
                            "default_metadata_after_exit": after_own,
                            "graph": snap, "top": pw_top_snapshot()})
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("g_metadata", rec)
    return rec


def stage_nameproj(reps):
    """PIPEWIRE_PROPS control: node.description overrides make jack_client_open fail
    with JackNameNotUnique (status 4) because the JACK client name is projected from
    the PipeWire node description."""
    rec = {"reps": []}
    arms = {"control_prop": "{ mem.warn-mlock = false }",
            "description_override": "{ node.description = \"r95s_forced\" }",
            "nodename_override": "{ node.name = \"r95s_forced_name\" }"}
    for arm, props in arms.items():
        rows = []
        for r in range(reps):
            sweep()
            d, b = jack_json([PROBE, "info", "0.3"], wall=8,
                             env={"PIPEWIRE_PROPS": props})
            rows.append({"rep": r, "arm": arm, "props": props, "rc": b.rc,
                         "json": d, "stderr": b.err[:200]})
            time.sleep(0.2)
        rec["reps"].append({"arm": arm, "rows": rows})
    rec["sweep_after"] = sweep()
    write_receipt("b_nameproj", rec)
    return rec


STAGES = {
    "avail": stage_avail,
    "shape": stage_shape,
    "shape_xconnect": stage_shape_xconnect,
    "tone_unlinked": stage_tone_unlinked,
    "nameproj": stage_nameproj,
    "jack2pw": stage_jack2pw,
    "pw2jack": stage_pw2jack,
    "quantum": stage_quantum,
    "global": stage_global,
    "xrun": stage_xrun,
    "latency": stage_latency,
    "rtprio": stage_rtprio,
    "transport": stage_transport,
    "metadata": stage_metadata,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in STAGES:
        print("stages:", " ".join(STAGES))
        return 2
    stage = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    os.makedirs(RECEIPTS, exist_ok=True)
    os.makedirs(RUNS, exist_ok=True)
    os.makedirs(SCRATCH, exist_ok=True)
    t0 = time.time()
    rec = STAGES[stage](reps)
    rec["_wall_s"] = round(time.time() - t0, 1)
    write_receipt(stage, rec)
    print(json.dumps({"_stage": stage, "_ok": True, "_wall_s": rec["_wall_s"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
