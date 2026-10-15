#!/usr/bin/env python3
"""r85 boundary harness — falsification of the r85 scout claims under host-state
variation and CPU load. Seat-owned everything; audio objects tagged r85b_*.
Scratch only under corpus/live/r85-boundary/.  No tracked writes.

Stages:
  b0  census (quiet baseline / final)
  b1  sndfile lattice — verbatim replays + mode hunting (quiet)
  b2  sndfile lattice — verbatim replays under CPU hog load
  b3  mixing / aplay env — quiet
  b4  mixing / aplay env — under CPU hog load
  b5  capture source-loss + self-destruct ladder — quiet
  b6  capture source-loss + self-destruct ladder — under CPU hog load
  b7  pactl addressing lattice + name/serial collision — quiet then under load
"""
import json, os, re, shlex, signal, subprocess, sys, time, wave, hashlib, shutil
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
TAGS = HERE / "tags"; RUNS = HERE / "runs"; RCPT = HERE / "receipts"
for d in (TAGS, RUNS, RCPT):
    d.mkdir(parents=True, exist_ok=True)
SR = 48000
HOGS = []
LOG = []


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    LOG.append(line)


def sh(cmd, timeout=25, env=None, cwd=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                       text=True, timeout=timeout, env=e, cwd=cwd)
    return p.returncode, p.stdout, p.stderr


def spawn(cmd, env=None):
    e = dict(os.environ); e.update(env or {})
    return subprocess.Popen(cmd, shell=isinstance(cmd, str), env=e,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                            text=True, start_new_session=True)


def killp(p, sig=signal.SIGTERM):
    if p is None:
        return None
    try:
        os.killpg(p.pid, sig)
    except ProcessLookupError:
        pass
    try:
        return p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return p.wait(timeout=5)


def pwdump():
    rc, out, _ = sh("pw-dump", timeout=20)
    return json.loads(out) if rc == 0 and out.strip() else []


def board():
    d = pwdump()
    nodes, ports, links = {}, {}, []
    for o in d:
        t = o.get("type", "")
        if t == "PipeWire:Interface:Node":
            pr = o.get("info", {}).get("props", {}) or {}
            nodes[o["id"]] = {"name": pr.get("node.name"), "class": pr.get("media.class"),
                              "serial": pr.get("object.serial"), "props": pr}
        elif t == "PipeWire:Interface:Port":
            pr = o.get("info", {}).get("props", {}) or {}
            ports[o["id"]] = {"node": pr.get("node.id"), "name": pr.get("port.name"),
                              "dir": pr.get("port.direction")}
        elif t == "PipeWire:Interface:Link":
            inf = o.get("info", {}) or {}
            links.append({"on": inf.get("output-node-id"), "in": inf.get("input-node-id"),
                          "op": inf.get("output-port-id"), "ip": inf.get("input-port-id"),
                          "state": (inf.get("state") or "?")})
    return {"nodes": nodes, "ports": ports, "links": links, "raw_n": len(d)}


def nid_by_name(b, name):
    return [i for i, n in b["nodes"].items() if n["name"] == name]


def linkstr(b, nid):
    out = []
    for l in b["links"]:
        if l["in"] == nid:
            pn = b["ports"].get(l["op"], {}); qn = b["ports"].get(l["ip"], {})
            on = b["nodes"].get(l["on"], {}).get("name")
            out.append(f"{on}:{pn.get('name')} -> {qn.get('name')}")
        if l["on"] == nid:
            pn = b["ports"].get(l["op"], {}); qn = b["ports"].get(l["ip"], {})
            inn = b["nodes"].get(l["in"], {}).get("name")
            out.append(f"{pn.get('name')} -> {inn}:{qn.get('name')}")
    return out


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def size(p):
    p = Path(p)
    return p.stat().st_size if p.exists() else None


def gen_tone(path, dur, chans, specs, rate=SR, amp_head="s16", scale=1.0):
    n = int(dur * rate)
    data = np.zeros((n, chans), dtype=np.float64)
    t = np.arange(n) / rate
    for ch, f, a in specs:
        data[:, ch] += a * np.sin(2 * np.pi * f * t)
    data = np.clip(data * scale, -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(chans); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(data.tobytes())
    return n


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        ch, sw, fr, nf = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(nf)
    a = np.frombuffer(raw, dtype="<i2")
    return (a.reshape(-1, ch) if ch > 1 else a[:, None]), fr


def fft_amp(x, f, rate=SR):
    n = len(x)
    if n == 0:
        return 0.0
    k = int(round(f * n / rate))
    seg = np.abs(np.fft.rfft(x.astype(np.float64)))
    lo, hi = max(0, k - 3), min(len(seg), k + 4)
    return float(2 * seg[lo:hi].max() / n)


def windows(path, win=0.25, freqs=(1000, 2500, 3000, 4500)):
    try:
        a, fr = read_wav(path)
    except Exception:
        return []
    wl = int(win * fr); out = []
    for s in range(0, len(a) - wl + 1, wl):
        w_ = a[s:s + wl]
        rec = {"t0": round(s / fr, 2), "peak": int(np.abs(w_).max()),
               "rms": round(float(np.sqrt((w_.astype(np.float64) ** 2).mean())), 1),
               "rail": int((np.abs(w_) >= 32760).sum()),
               "zeros": int((w_ == 0).all(axis=1).sum())}
        for f in freqs:
            rec[f"L{int(f)}"] = round(fft_amp(w_[:, 0], f), 1)
            if w_.shape[1] > 1:
                rec[f"R{int(f)}"] = round(fft_amp(w_[:, 1], f), 1)
        out.append(rec)
    return out


def mod_line(name):
    """return (index, line) for a module whose sink_name= or source_name= is `name`.
    (r85 scout's mod_index grepped only sink_name= — fixed here.)"""
    rc, out, _ = sh("pactl list short modules")
    for line in out.splitlines():
        parts = line.split("\t") if "\t" in line else line.split(None, 2)
        if len(parts) < 3:
            continue
        if f"sink_name={name}" in line or f"source_name={name}" in line:
            return int(parts[0]), line
    return None, None


def load_sink(name, extra=""):
    rc, out, err = sh(f"pactl load-module module-null-sink sink_name={name} {extra}")
    idx = out.strip()
    for _ in range(60):
        b = board()
        if nid_by_name(b, name):
            return {"idx": idx, "rc": rc, "err": err.strip()[:120], "node": nid_by_name(b, name)[0]}
        time.sleep(0.1)
    return {"idx": idx, "rc": rc, "err": err.strip()[:120], "node": None}


def unload_verified(name):
    """index-verified unload: look the index up immediately before the call."""
    idx, line = mod_line(name)
    if idx is None:
        return {"idx": None, "rc": None, "out": "no module", "line": None}
    rc, out, err = sh(f"pactl unload-module {idx}")
    return {"idx": idx, "rc": rc, "out": out.strip()[:80], "err": err.strip()[:80], "line": line}


def wait_node(name, want=True, t=8.0):
    end = time.time() + t
    while time.time() < end:
        b = board()
        found = bool(nid_by_name(b, name))
        if found == want:
            return True, b
        time.sleep(0.08)
    return False, board()


# ------------------------------------------------------------------ hog load
HOGFILE = HERE / "hogs.pid"


def kill_stray_hogs():
    """kill only hogs this seat recorded in hogs.pid (never foreign `yes`)."""
    if not HOGFILE.exists():
        return []
    killed = []
    for tok in HOGFILE.read_text().split():
        try:
            pid = int(tok)
            os.kill(pid, signal.SIGKILL)
            killed.append(pid)
        except (ProcessLookupError, ValueError):
            pass
    HOGFILE.write_text("")
    return killed


def start_hogs(n=40):
    stop_hogs()
    kill_stray_hogs()
    for _ in range(n):
        HOGS.append(subprocess.Popen(["yes"], stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL, start_new_session=True))
    HOGFILE.write_text(" ".join(str(p.pid) for p in HOGS))
    time.sleep(1.0)
    return loadavg()


def stop_hogs():
    while HOGS:
        p = HOGS.pop()
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass
    HOGFILE.write_text("")
    return loadavg()


def loadavg():
    return [round(x, 2) for x in os.getloadavg()]


# ------------------------------------------------------------------ sndfile
def conv(inp, outp, flags=""):
    cmd = f"sndfile-convert {flags} {shlex.quote(str(inp))} {shlex.quote(str(outp))}"
    rc, so, se = sh(cmd, timeout=30)
    return {"rc": rc, "stdout": so.strip()[:300], "stderr": se.strip()[:200],
            "out": str(outp), "exists": Path(outp).exists(),
            "bytes": size(outp), "sha": sha(outp) if Path(outp).exists() and Path(outp).stat().st_size else None}


def sinfo(path):
    rc, so, se = sh(f"sndfile-info {shlex.quote(str(path))}", timeout=20)
    d = {"rc": rc, "stdout": so.strip()[:600], "stderr": se.strip()[:200]}
    for key, rx in [("rate", r"^Sample Rate\s*:\s*(\S+)"), ("frames", r"^Frames\s*:\s*(\S+)"),
                    ("format", r"^Format\s*:\s*(\S+)"), ("channels", r"^Channels\s*:\s*(\S+)"),
                    ("bitwidth", r"^Bit width\s*:\s*(\S+)"), ("sigmax", r"^Signal Max\s*:\s*(.*)")]:
        m = re.search(rx, so, re.M)
        d[key] = m.group(1).strip() if m else None
    m = re.search(r"Format not recognised", so)
    d["unrecognised"] = bool(m)
    m = re.search(r"Error\s*:\s*(.*)", so)
    d["err_stdout"] = m.group(1).strip()[:200] if m else None
    m = re.search(r"Stream serialno\s*:\s*(\S+)", so)
    d["serialno"] = m.group(1) if m else None
    return d


def infometa(path):
    rc, so, se = sh(f"sndfile-info {shlex.quote(str(path))}", timeout=20)
    keys = {}
    for l in so.splitlines():
        m = re.match(r"\s*(Title|Artist|Comment|Album|Date|Software|Copyright|Track|Genre|License|Encoded by)\s*:\s*(.*)", l)
        if m:
            keys[m.group(1)] = m.group(2).strip()
    return keys


def meta_blocks(path):
    rc, so, se = sh(f"sndfile-info {shlex.quote(str(path))}", timeout=20)
    return [l.strip() for l in so.splitlines()
            if re.match(r"\s*(LIST INFO|Vorbis Comment|Stream serialno|PCM offset|PCM end|Encoded by)", l)]


def b0(tag):
    rc, o, _ = sh("pactl get-default-sink"); ds = o.strip()
    rc, o, _ = sh("pactl get-default-source"); ds2 = o.strip()
    rc, so, _ = sh("pactl list short sinks")
    rc, so2, _ = sh("pactl list short sources")
    rc, so3, _ = sh("pactl list short modules")
    b = board()
    foreign = sorted({n["name"] for n in b["nodes"].values()
                      if n["name"] and not str(n["name"]).startswith("r85b")
                      and str(n["name"]) not in ("Midi-Bridge", "Dummy-Driver", "Freewheel-Driver")})
    rc, h, _ = sh("git -C /home/vgpnk/Projects/shokunin/audio-shokunin rev-parse HEAD")
    snap = {"tag": tag, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "host": os.uname().nodename, "loadavg": loadavg(), "nproc": os.cpu_count(),
            "default_sink": ds, "default_source": ds2,
            "sinks": [l for l in so.splitlines()],
            "sources": [l for l in so2.splitlines()],
            "r85b_modules": [l for l in so3.splitlines() if "r85b" in l],
            "foreign_nodes": foreign, "head": h.strip(),
            "pw_cli": (lambda r: r[1].strip().splitlines()[:2])(sh("pw-cli --version")),
            "sndfile_info": (lambda r: r[1].strip().splitlines()[:2])(sh("sndfile-info"))}
    (RCPT / f"b0-{tag}.json").write_text(json.dumps(snap, indent=1, default=str))
    log(f"b0 {tag}: default={ds.split('.')[-1]} load={snap['loadavg']} foreign_nodes={len(foreign)} r85b_mods={len(snap['r85b_modules'])}")
    return snap


# ------------------------------------------------------- ogg page diff tool
def ogg_pages(data):
    off, pages = 0, []
    while off + 27 <= len(data):
        if data[off:off + 4] != b"OggS":
            break
        nseg = data[off + 26]
        hdr = 27 + nseg
        body = sum(data[off + 27 + i] for i in range(nseg)) if off + hdr <= len(data) else 0
        pages.append({"off": off, "hdr": hdr, "serial": data[off + 14:off + 18].hex(),
                      "serial_range": [off + 14, off + 18],
                      "crc_range": [off + 22, off + 26],
                      "granule": data[off + 6:off + 14].hex(),
                      "seqno": data[off + 18:off + 22].hex(),
                      "page_len": hdr + body})
        off += hdr + body
    return pages


def ogg_pair_diff(pa, pb):
    a, b = Path(pa).read_bytes(), Path(pb).read_bytes()
    pages = ogg_pages(a)
    serial_r = [(p["serial_range"][0], p["serial_range"][1]) for p in pages]
    crc_r = [(p["crc_range"][0], p["crc_range"][1]) for p in pages]
    n = min(len(a), len(b))
    diffs = [i for i in range(n) if a[i] != b[i]]
    diffset = set(diffs)
    in_serial = [i for i in diffs if any(s <= i < e for s, e in serial_r)]
    in_crc = [i for i in diffs if any(s <= i < e for s, e in crc_r)]
    outside = [i for i in diffs if i not in set(in_serial) | set(in_crc)]

    def ranges(offs):
        out = []
        for i in sorted(offs):
            if out and i == out[-1][1]:
                out[-1][1] = i + 1
            else:
                out.append([i, i + 1])
        return out[:30]

    return {"len_a": len(a), "len_b": len(b), "n_diffs": len(diffs),
            "n_in_serial": len(in_serial), "n_in_crc": len(in_crc),
            "n_outside_serial_or_crc": len(outside),
            "outside_ranges": ranges(outside), "serial_ranges": ranges(in_serial)[:6],
            "crc_ranges": ranges(in_crc)[:6],
            "pages": len(pages), "serials_a": [p["serial"] for p in pages][:3],
            "serials_b": [p["serial"] for p in ogg_pages(b)][:3],
            "granules_a": [p["granule"] for p in pages][:2],
            "granules_b": [p["granule"] for p in ogg_pages(b)][:2]}


# ------------------------------------------------------------------ b1/b2
def sndfile_core(tag, reps=3, page_reps=8):
    """verbatim A1..A10 replays + mode hunting; returns receipt dict."""
    R = {"tag": tag, "load_at_start": loadavg()}
    d0 = RUNS / tag / "core"; d0.mkdir(parents=True, exist_ok=True)
    src = TAGS / "src.wav"
    if not src.exists():
        gen_tone(src, 1.5, 2, [(0, 997, 10000), (1, 1502, 7000)])
    ref_raw = d0 / "src.raw"
    conv(src, ref_raw)
    R["src_sha"], R["src_raw_sha"] = sha(src), sha(ref_raw)
    R["src_info"] = sinfo(src)

    # A1 flac determinism (3 reps) + A3 round-trip + cmp
    fl_shas, rt = [], []
    for rep in range(reps):
        d = d0 / f"flac_r{rep}"; d.mkdir(exist_ok=True)
        r1 = conv(src, d / "m.flac"); r2 = conv(d / "m.flac", d / "o.wav"); r3 = conv(d / "o.wav", d / "o.raw")
        cmp_rc, cmp_so, cmp_se = sh(f"sndfile-cmp {src} {d/'o.wav'}")
        fl_shas.append(r1["sha"])
        rt.append({"flac": r1, "wav": r2, "raw": r3, "payload_eq_src": r3["sha"] == R["src_raw_sha"],
                   "cmp": {"rc": cmp_rc, "stdout": cmp_so.strip()[:120], "stderr": cmp_se.strip()[:120]}})
    R["A1_flac_identical"] = len(set(fl_shas)) == 1
    R["A1_flac_shas"] = fl_shas
    R["A3_rt"] = rt

    # A2 ogg nondeterminism + decoded payload
    og = []
    for rep in range(page_reps):
        d = d0 / f"ogg_r{rep}"; d.mkdir(exist_ok=True)
        r1 = conv(src, d / "m.ogg"); r2 = conv(d / "m.ogg", d / "o.raw", "-pcm16")
        og.append({"ogg": r1, "raw": r2})
    R["A2_ogg_shas"] = [x["ogg"]["sha"] for x in og]
    R["A2_ogg_distinct"] = len({x["ogg"]["sha"] for x in og})
    R["A2_raw_shas"] = [x["raw"]["sha"] for x in og]
    R["A2_raw_distinct"] = len({x["raw"]["sha"] for x in og})
    R["A2_raw_eq_src"] = og[0]["raw"]["sha"] == R["src_raw_sha"]
    R["A2_page_diffs"] = [ogg_pair_diff(d0 / "ogg_r0/m.ogg", d0 / f"ogg_r{r}/m.ogg")
                          for r in range(1, page_reps)]
    # verbatim cmp -l of rep0 vs rep1
    rc, so, se = sh(f"cmp -l {d0/'ogg_r0/m.ogg'} {d0/'ogg_r1/m.ogg'}")
    R["A2_cmp_l"] = {"rc": rc, "lines": so.strip().splitlines()[:14], "n": len(so.strip().splitlines())}

    # A4/A5 refusal + -pcm16 unlock, and container x codec lattice
    ogg0 = d0 / "ogg_r0/m.ogg"
    r = conv(ogg0, d0 / "refuse.wav")
    R["A4_noenc_ogg_wav"] = r
    R["A4_stdout_only"] = bool(r["stdout"]) and not r["stderr"]
    R["A5_pcm16_ogg_wav"] = conv(ogg0, d0 / "unlock.wav", "-pcm16")
    lat = []
    for enc, ext in [("", "wavex"), ("", "w64"), ("", "caf"), ("", "au"), ("", "aiff"),
                     ("", "rf64"), ("", "oga"), ("", "opus"),
                     ("-pcm16", "wavex"), ("-pcm16", "caf"), ("-pcm16", "w64")]:
        o = d0 / f"lat_{enc[1:] or 'none'}_{ext}.{ext}"
        lat.append({"enc": enc or "(none)", "ext": ext, "r": conv(ogg0, o)})
    R["lattice_from_ogg"] = lat
    R["flac_to_ogg_noenc"] = conv(d0 / "flac_r0/m.flac", d0 / "flac_to_ogg.ogg")
    R["ogg_to_flac_noenc"] = conv(ogg0, d0 / "ogg_to_flac.flac")

    # A6 override-sample-rate relabel (verbatim) + mode hunting over rates
    ov = []
    for rep in range(reps):
        d = d0 / f"ovr_r{rep}"; d.mkdir(exist_ok=True)
        r = conv(src, d / "o.wav", "-override-sample-rate=44100")
        i = sinfo(d / "o.wav") if r["exists"] else {}
        rr = conv(d / "o.wav", d / "o.raw") if r["exists"] else {}
        ov.append({"rep": rep, "r": r, "info": {k: i.get(k) for k in ("rate", "frames", "format", "sigmax")},
                   "payload_eq_src": rr.get("sha") == R["src_raw_sha"]})
    R["A6_ovr_44100"] = ov
    ovr_rates = []
    for val in ["0", "1", "2", "8000", "44100", "96000", "192000", "384000", "768000",
                "1000000", "4294967295", "4294967296", "-1", "abc", "44100.5", " 44100"]:
        o = d0 / f"ovr_{re.sub(r'[^0-9a-zA-Z]+','_',val)}.wav"
        r = conv(src, o, f"-override-sample-rate={shlex.quote(val)}")
        i = sinfo(o) if r["exists"] else {}
        rr = conv(o, str(o) + ".raw") if r["exists"] else {}
        ovr_rates.append({"val": val, "rc": r["rc"], "bytes": r["bytes"],
                          "stdout": r["stdout"][:160], "stderr": r["stderr"][:120],
                          "rate": i.get("rate"), "frames": i.get("frames"), "format": i.get("format"),
                          "payload_eq_src": rr.get("sha") == R["src_raw_sha"]})
    R["ovr_rates"] = ovr_rates

    # A7 unknown-extension lattice (content = pcm16 wav source)
    exts = ["bogusext", "xyz", "XYZ", "wavx", "flacx", "oggx", "oga", "opus", "mp3", "aiff",
            "aifc", "au", "snd", "voc", "xi", "w64", "rf64", "mat4", "mat5", "paf", "svx",
            "nist", "ircam", "wve", "dwd", "dff", "mka", "webm", "mp4", "raw", "pcm", "wav"]
    ext_rows = []
    for e in exts:
        o = d0 / f"ext_{e}.{e}"
        r = conv(src, o)
        i = sinfo(o) if r["exists"] else {}
        ext_rows.append({"ext": e, "rc": r["rc"], "bytes": r["bytes"], "exists": r["exists"],
                         "format": i.get("format"), "bitwidth": i.get("bitwidth"),
                         "rate": i.get("rate"), "frames": i.get("frames"),
                         "stdout": r["stdout"][:120], "stderr": r["stderr"][:120]})
    # no extension at all / trailing dot / dot-dot
    for nm, path in [("nonext", d0 / "o_noext"), ("dot", d0 / "o."), ("double", d0 / "o.wav.bak")]:
        r = conv(src, path)
        i = sinfo(path) if r["exists"] else {}
        ext_rows.append({"ext": f"<{nm}>", "rc": r["rc"], "bytes": r["bytes"], "exists": r["exists"],
                         "format": i.get("format"), "bitwidth": i.get("bitwidth"),
                         "rate": i.get("rate"), "frames": i.get("frames"),
                         "stdout": r["stdout"][:120], "stderr": r["stderr"][:120]})
    R["A7_ext_lattice"] = ext_rows
    # unknown ext x non-pcm input (interaction of carry-law and default container)
    inter = []
    for nm, inp in [("flac", d0 / "flac_r0/m.flac"), ("ogg", ogg0)]:
        o = d0 / f"inter_{nm}.bogusext"
        r = conv(inp, o)
        i = sinfo(o) if r["exists"] else {}
        inter.append({"in": nm, "rc": r["rc"], "exists": r["exists"], "bytes": r["bytes"],
                      "format": i.get("format"), "stdout": r["stdout"][:200]})
        o2 = d0 / f"inter_{nm}_pcm16.bogusext"
        r2 = conv(inp, o2, "-pcm16")
        i2 = sinfo(o2) if r2["exists"] else {}
        inter.append({"in": nm + "+pcm16", "rc": r2["rc"], "exists": r2["exists"], "bytes": r2["bytes"],
                      "format": i2.get("format"), "stdout": r2["stdout"][:200]})
    R["ext_x_input"] = inter

    # A8 content sniffing (content vs extension), including ogg/aiff content
    sniff = []
    shutil.copyfile(d0 / "flac_r0/m.flac", d0 / "fake.wav")
    shutil.copyfile(src, d0 / "fake.flac")
    shutil.copyfile(ogg0, d0 / "fakeogg.wav")
    shutil.copyfile(d0 / "lat__aiff.aiff", d0 / "fakeaiff.flac") if (d0 / "lat__aiff.aiff").exists() else None
    for f in ["fake.wav", "fake.flac", "fakeogg.wav", "fakeaiff.flac"]:
        p = d0 / f
        if not p.exists():
            continue
        sniff.append({"file": f, "info": {k: sinfo(p).get(k) for k in ("rc", "format", "rate", "frames", "unrecognised")},
                      "conv_out_ext_wav": conv(p, d0 / (f + ".out.wav"))})
    R["A8_sniff"] = sniff

    # A9 sndfile-info rc lies
    weird = []
    (d0 / "empty.wav").write_bytes(b"")
    (d0 / "text.wav").write_text("this is not audio\n" * 8)
    (d0 / "trunc.wav").write_bytes(src.read_bytes()[:100])
    (d0 / "garbage").write_bytes(bytes(range(256)) * 4)
    for nm, p in [("missing", "/nonexistent_r85b.wav"), ("garbage", d0 / "garbage"),
                  ("empty", d0 / "empty.wav"), ("text", d0 / "text.wav"),
                  ("trunc", d0 / "trunc.wav"), ("dir", d0), ("devnull", "/dev/null"),
                  ("hostname", "/etc/hostname")]:
        i = sinfo(p)
        weird.append({"leg": nm, "rc": i["rc"], "stdout": i["stdout"][:160],
                      "stderr": i["stderr"][:120], "unrecognised": i["unrecognised"],
                      "err_stdout": i["err_stdout"]})
    R["A9_info_weird"] = weird

    # A10 normalize determinism + mode hunting on edge content
    nz = []
    for rep in range(reps):
        d = d0 / f"norm_r{rep}"; d.mkdir(exist_ok=True)
        r = conv(src, d / "o.wav", "-normalize")
        i = sinfo(d / "o.wav") if r["exists"] else {}
        nz.append({"rep": rep, "rc": r["rc"], "sha": r["sha"], "sigmax": i.get("sigmax")})
    R["A10_normalize"] = nz
    R["A10_norm_identical"] = len({x["sha"] for x in nz}) == 1
    edges = []
    gen_tone(d0 / "sil.wav", 1.0, 2, [])
    gen_tone(d0 / "dc.wav", 1.0, 2, [(0, 0.0001, 32767), (1, 0.0001, 32767)])
    gen_tone(d0 / "one.wav", 1 / 48000, 2, [(0, 1000, 1000)])
    gen_tone(d0 / "quiet.wav", 1.0, 2, [(0, 1000, 1), (1, 1000, 1)])
    for nm, p in [("silence", d0 / "sil.wav"), ("dc", d0 / "dc.wav"),
                  ("oneframe", d0 / "one.wav"), ("quiet", d0 / "quiet.wav"), ("src", src)]:
        o = d0 / f"nz_{nm}.wav"
        r = conv(p, o, "-normalize")
        i = sinfo(o) if r["exists"] else {}
        edges.append({"in": nm, "rc": r["rc"], "bytes": r["bytes"], "sigmax": i.get("sigmax"),
                      "stdout": r["stdout"][:160], "stderr": r["stderr"][:160]})
    R["normalize_edges"] = edges

    # sndfile-cmp mismatch classes (scout unknown #4)
    cmp_rows = []
    for nm, a, b in [("equal", src, d0 / "ext_wav.wav"),
                     ("content_differs", src, d0 / "nz_src.wav"),
                     ("truncated", src, d0 / "trunc.wav"),
                     ("rate_differs", src, d0 / "ovr_44100.wav"),
                     ("missing_operand", src, "/nonexistent_r85b_b.wav"),
                     ("one_operand", src, None)]:
        if b is None:
            rc, so, se = sh(f"sndfile-cmp {a}")
        else:
            rc, so, se = sh(f"sndfile-cmp {a} {b}")
        cmp_rows.append({"leg": nm, "rc": rc, "stdout": so.strip()[:300], "stderr": se.strip()[:200]})
    R["cmp_mismatch"] = cmp_rows

    # endian on non-wav containers (mode hunt)
    end_rows = []
    for e in ("little", "big", "cpu"):
        for ext in ("wav", "flac", "ogg", "aiff", "caf"):
            o = d0 / f"end_{e}.{ext}"
            r = conv(src, o, f"-endian={e}")
            end_rows.append({"endian": e, "ext": ext, "rc": r["rc"], "bytes": r["bytes"],
                             "magic": Path(o).read_bytes()[:4].hex() if r["exists"] else None,
                             "stderr": r["stderr"][:100], "stdout": r["stdout"][:100]})
    R["endian_lattice"] = end_rows

    # metadata matrix replay (ffmpeg writes tags; sndfile carries them)
    meta = "-metadata title=r85btitle -metadata artist=r85bartist -metadata comment=r85bcmt -metadata album=r85balb -metadata date=2026"
    tag_files = {}
    for ext in ("wav", "flac", "ogg", "aif"):
        p = TAGS / f"tagged.{ext}"
        rc, so, se = sh(f"ffmpeg -y -v error -i {src} {meta} {p}")
        tag_files[ext] = p
    R["meta_read"] = {e: {"meta": infometa(p), "blocks": meta_blocks(p)} for e, p in tag_files.items()}
    hops = []
    for i, (a, b) in enumerate([("wav", "flac"), ("wav", "ogg"), ("wav", "aif"), ("flac", "wav"),
                                ("ogg", "wav"), ("wav", "wav"), ("aif", "wav")]):
        o = d0 / f"metahop{i}.{b}"
        r = conv(tag_files[a], o)
        hops.append({"from": a, "to": b, "rc": r["rc"], "exists": r["exists"],
                     "meta": infometa(o) if r["exists"] else None,
                     "stdout": r["stdout"][:200]})
    R["meta_hops"] = hops

    # error-shape census
    errs = []
    cases = [("info_missing", "sndfile-info /nonexistent_r85b.wav", None),
             ("conv_missing_in", f"sndfile-convert /nonexistent_r85b.wav {d0}/x.wav", None),
             ("conv_bad_outdir", f"sndfile-convert {src} /nonexistent_dir_r85b/x.wav", None),
             ("conv_bad_flag", f"sndfile-convert -bogusflag {src} {d0}/x.wav", None),
             ("conv_one_arg", f"sndfile-convert {src}", None),
             ("conv_zero_arg", "sndfile-convert", None),
             ("conv_ovr_noval", f"sndfile-convert -override-sample-rate {src} {d0}/x2.wav", None),
             ("conv_dir_out", f"sndfile-convert {src} {d0}", None)]
    for nm, cmd, cwd in cases:
        rc, so, se = sh(cmd, cwd=cwd, timeout=20)
        errs.append({"leg": nm, "cmd": cmd, "rc": rc, "stdout": so.strip()[:300], "stderr": se.strip()[:200]})
    R["errors"] = errs

    (RCPT / f"{tag}-sndfile.json").write_text(json.dumps(R, indent=1, default=str))
    log(f"{tag}: flac_det={R['A1_flac_identical']} ogg_distinct={R['A2_ogg_distinct']}/{page_reps} "
        f"raw_distinct={R['A2_raw_distinct']} raw_eq_src={R['A2_raw_eq_src']} "
        f"A4_rc={R['A4_noenc_ogg_wav']['rc']} A5_rc={R['A5_pcm16_ogg_wav']['rc']} "
        f"cmp_diff_rc={[c['rc'] for c in cmp_rows[:4]]} ovr_eq_src={[x['payload_eq_src'] for x in ov]}")
    return R


# ------------------------------------------------------------------ b1x mode hunts
def infometa2(path):
    """tag reader that understands LIST INFO codes (INAM/IART/...) and Vorbis lowercase keys."""
    rc, so, se = sh(f"sndfile-info {shlex.quote(str(path))}", timeout=20)
    tags = {}
    for l in so.splitlines():
        m = re.match(r"\s+(INAM|IART|ICMT|ICRD|IPRD|ISFT|ICOP|IGNR|ITRK)\s*:\s*(.*)", l)
        if m:
            tags[m.group(1)] = m.group(2).strip()
        m = re.match(r"\s+(title|artist|comment|date|album|software|genre|copyright|track|license)\s*:\s*(.*)", l)
        if m:
            tags[m.group(1)] = m.group(2).strip()
        m = re.match(r"\s*(Title|Artist|Comment|Date|Album|Software|Encoded by)\s*:\s*(.*)", l)
        if m:
            tags[m.group(1)] = m.group(2).strip()
    return tags, [l.strip() for l in so.splitlines() if re.match(r"\s*(LIST INFO|Vorbis Comment|Metadata|Stream serialno)", l)], so


def b1x(tag="b1x"):
    R = {"tag": tag, "load_at_start": loadavg()}
    d0 = RUNS / tag; d0.mkdir(parents=True, exist_ok=True)
    src = TAGS / "src.wav"
    ogg = RUNS / "b1" / "core" / "ogg_r0" / "m.ogg"
    flac = RUNS / "b1" / "core" / "flac_r0" / "m.flac"

    # --- metadata, fixed parser (raw text kept)
    meta = "-metadata title=r85btitle -metadata artist=r85bartist -metadata comment=r85bcmt -metadata album=r85balb -metadata date=2026"
    tf = {}
    for ext in ("wav", "flac", "ogg", "aif"):
        p = d0 / f"tagged.{ext}"
        sh(f"ffmpeg -y -v error -i {src} {meta} {p}")
        tf[ext] = p
    R["meta_read"] = {e: infometa2(p)[0] for e, p in tf.items()}
    hops = []
    for i, (a, b) in enumerate([("wav", "flac"), ("wav", "ogg"), ("wav", "aif"), ("flac", "wav"),
                                ("ogg", "wav"), ("wav", "wav"), ("aif", "wav"), ("flac", "ogg")]):
        o = d0 / f"hop{i}_{a}_to_{b}.{b}"
        r = conv(tf[a], o)
        tags, blocks, raw = infometa2(o) if r["exists"] else ({}, [], "")
        hops.append({"from": a, "to": b, "rc": r["rc"], "exists": r["exists"], "tags": tags,
                     "blocks": blocks, "raw": raw[:900], "stdout": r["stdout"][:200]})
    R["meta_hops"] = hops
    # aif chain: aif -> wav (does anything survive the aif hop?)
    o1 = d0 / "aif_hop.aif"; conv(tf["wav"], o1)
    o2 = d0 / "aif_hop_back.wav"; r2 = conv(o1, o2)
    R["aif_chain"] = {"aif_tags": infometa2(o1)[0], "aif_info": infometa2(o1)[2][:600],
                      "back_rc": r2["rc"], "back_tags": infometa2(o2)[0] if r2["exists"] else None}

    # --- flag x container lattice from the PCM wav source
    lat = []
    flags = ["", "-pcm16", "-pcm24", "-float32", "-vorbis", "-opus", "-alac16", "-ulaw"]
    exts = ["wav", "wavex", "w64", "rf64", "caf", "aiff", "au", "ogg", "flac", "opus", "mp3",
            "raw", "bogusext"]
    for f in flags:
        for e in exts:
            o = d0 / f"lat2_{(f[1:] or 'none')}.{e}"
            r = conv(src, o, f)
            i = sinfo(o) if r["exists"] else {}
            lat.append({"flag": f or "(none)", "ext": e, "rc": r["rc"], "bytes": r["bytes"],
                        "format": i.get("format"), "rate": i.get("rate"), "frames": i.get("frames"),
                        "stdout": r["stdout"][:120], "stderr": r["stderr"][:80]})
    R["flag_x_ext_from_pcm"] = lat
    # same lattice from the Ogg (Vorbis) source: does an explicit flag beat the carry law?
    lat2 = []
    for f in ["", "-pcm16", "-pcm24", "-float32", "-vorbis", "-opus"]:
        for e in ["wav", "wavex", "w64", "caf", "bogusext", "raw", "oga", "mp3"]:
            o = d0 / f"lat3_{(f[1:] or 'none')}.{e}"
            r = conv(ogg, o, f)
            i = sinfo(o) if r["exists"] else {}
            lat2.append({"flag": f or "(none)", "ext": e, "rc": r["rc"], "bytes": r["bytes"],
                         "format": i.get("format"), "stdout": r["stdout"][:140]})
    R["flag_x_ext_from_ogg"] = lat2

    # --- refusal text for the odd known extensions + raw output info
    odd = []
    for e in ["oga", "xi", "svx", "wve", "raw", "nonext"]:
        o = d0 / f"odd.{e}" if e != "nonext" else d0 / "odd_nonext"
        r = conv(src, o)
        raw = sh(f"sndfile-info {o}")[1][:400] if r["exists"] else ""
        odd.append({"ext": e, "rc": r["rc"], "bytes": r["bytes"], "exists": r["exists"],
                    "stdout": r["stdout"][:300], "info_head": raw[:300]})
    R["odd_ext"] = odd

    # --- 44-byte stub on decode failure; refusal file existence
    stub = {"normalize_silence_bytes": size(RUNS / "b1" / "core" / "nz_silence.wav"),
            "normalize_silence_head": (RUNS / "b1" / "core" / "nz_silence.wav").read_bytes()[:64].hex()
            if (RUNS / "b1" / "core" / "nz_silence.wav").exists() else None,
            "a4_refuse_exists": (RUNS / "b1" / "core" / "refuse.wav").exists(),
            "a4_refuse_bytes": size(RUNS / "b1" / "core" / "refuse.wav")}
    # a decode-failure refusal that writes a stub: convert a garbage file to wav
    (d0 / "garbage.wav").write_bytes(bytes(range(256)) * 4)
    r = conv(d0 / "garbage.wav", d0 / "garbage_out.wav")
    stub["garbage_in_rc"] = r["rc"]; stub["garbage_out_bytes"] = r["bytes"]
    stub["garbage_stdout"] = r["stdout"][:200]
    R["stub_on_failure"] = stub

    # --- mp3/opus outputs: determinism + info
    det = []
    for e, flag in [("mp3", ""), ("opus", ""), ("oga", "")]:
        shas = []
        for rep in range(3):
            o = d0 / f"det_{e}_r{rep}.{e}"
            r = conv(src, o, flag)
            shas.append(r["sha"])
        o = d0 / f"det_{e}_r0.{e}"
        det.append({"ext": e, "shas": shas, "identical": len(set(shas)) == 1,
                    "info": {k: sinfo(o).get(k) for k in ("format", "rate", "frames", "bitwidth")},
                    "bytes": size(o)})
    R["lossy_determinism"] = det

    (RCPT / f"{tag}-modehunt.json").write_text(json.dumps(R, indent=1, default=str))
    log(f"{tag}: meta_wav_tags={len(R['meta_read']['wav'])} hop_flac_tags={len(hops[0]['tags'])} "
        f"hop_aif_tags={len(hops[2]['tags'])} stub={stub} "
        f"mp3_det={det[0]['identical']} opus_det={det[1]['identical']}")
    return R


# ------------------------------------------------------------------ b7x collision
def b7x(tag="b7x"):
    """Name/serial collision discriminator: a sink literally NAMED with another
    sink's object.serial. Identity is read from the LINK TARGET node name."""
    R = {"tag": tag, "load_at_start": loadavg()}
    a = "r85b_ca"
    load_sink(a); wait_node(a)
    b = board()
    ids = nid_by_name(b, a)
    S = b["nodes"][ids[0]]["serial"]
    coll = str(S)
    lc = load_sink(coll); wait_node(coll)
    bb = board()
    R["setup"] = {"serial": S, "a_node": {"id": ids[0], "name": a},
                  "collision_name": coll, "collision_load": lc,
                  "collision_node": [{"id": i, "name": bb["nodes"][i]["name"]}
                                     for i in nid_by_name(bb, coll)],
                  "short_sinks": [l for l in sh("pactl list short sinks")[1].splitlines()
                                  if "r85b" in l or f"\t{coll}\t" in l]}
    # 1. pactl get-sink-volume <S> (both sinks exist; volumes distinct by construction:
    #    set the named sink to 55% via its OWN unique *description* lookup is impossible,
    #    so use the link identity of a moved stream instead)
    p = spawn(f"pw-play -P node.name=r85b_cx --target {a} {TAGS/'a1k.wav'}")
    time.sleep(0.8)
    bb = board()
    sids = nid_by_name(bb, "r85b_cx")
    ser = bb["nodes"][sids[0]]["serial"] if sids else None
    rc, so, se = sh(f"pactl move-sink-input {ser} {coll}") if ser else (None, "", "no stream")
    time.sleep(0.7)
    bb = board()
    lk = linkstr(bb, nid_by_name(bb, "r85b_cx")[0]) if nid_by_name(bb, "r85b_cx") else []
    R["move_identity"] = {"stream_serial": ser, "rc": rc, "stdout": so.strip()[:120],
                          "stderr": se.strip()[:120], "links_after": lk}
    killp(p)
    # 2. capture side: pw-record --target <S> (noprop) -> whose monitor?
    f = RUNS / tag / "cap.wav"
    p2 = spawn(f"pw-record -P node.name=r85b_cxrec --target {coll} --rate 48000 --channels 2 "
               f"--format s16 -n 96000 {f}")
    time.sleep(1.1)
    bb = board()
    lk2 = linkstr(bb, nid_by_name(bb, "r85b_cxrec")[0]) if nid_by_name(bb, "r85b_cxrec") else []
    killp(p2)
    R["capture_identity"] = {"links": lk2, "bytes": size(f)}
    # 3. get-sink-volume with distinct volumes: set A by name (unique), collision by
    #    moving a stream is done; here just read both addresses
    R["reads"] = {"by_number": sh(f"pactl get-sink-volume {coll}")[1].splitlines()[:1],
                  "by_a_name": sh(f"pactl get-sink-volume {a}")[1].splitlines()[:1]}
    unload_verified(coll); unload_verified(a)
    R["load_at_end"] = loadavg()
    (RCPT / f"{tag}-collision.json").write_text(json.dumps(R, indent=1, default=str))
    log(f"{tag}: serial={S} move->{lk[:1]} cap->{lk2[:1]} reads={R['reads']}")
    return R


# ------------------------------------------------------------------ b3t tap stability
def b3t(tag="b3t", reps=12, reuse_sink=False):
    """Exact scout tap shape, link-validated, fresh or reused sink.
    Measures the monitor-tap gain stability (1.0 vs 1/8 vs silent)."""
    R = {"tag": tag, "load_at_start": loadavg(), "reuse_sink": reuse_sink, "rows": []}
    ensure_tones()
    d0 = RUNS / tag; d0.mkdir(parents=True, exist_ok=True)
    shared = "r85b_tshared"
    if reuse_sink:
        load_sink(shared); wait_node(shared)
    for i in range(reps):
        sink = shared if reuse_sink else f"r85b_t{i}"
        if not reuse_sink:
            load_sink(sink); wait_node(sink)
        time.sleep(0.3)
        f = d0 / f"tap_r{i}.wav"
        rec = spawn(f"pw-record -P stream.capture.sink=true -P node.name=r85b_tt{i} "
                    f"--target {sink} --rate 48000 --channels 2 --format s16 -n 144000 {f}")
        time.sleep(0.35)
        b = board()
        ids = nid_by_name(b, f"r85b_tt{i}")
        lk = linkstr(b, ids[0]) if ids else []
        props = {k: b["nodes"][ids[0]]["props"].get(k) for k in
                 ("target.object", "stream.capture.sink", "media.class")} if ids else {}
        pl = spawn(f"pw-play -P node.name=r85b_tp{i} --target {sink} {TAGS/'a1k.wav'}")
        time.sleep(1.6)
        killp(pl); killp(rec)
        time.sleep(0.3)
        w = windows(f)
        steady = [x for x in w if x["peak"] > 0]
        R["rows"].append({"rep": i, "sink": sink, "links": lk, "tap_props": props,
                          "frames": w and (w[0] and None) or None, "n_windows": len(w),
                          "peak": max((x["peak"] for x in w), default=None),
                          "L1000": max((x["L1000"] for x in w), default=None),
                          "steady_windows": len(steady),
                          "sink_vol": sh(f"pactl get-sink-volume {sink}")[1].splitlines()[0] if sink else None})
        if not reuse_sink:
            unload_verified(sink)
    if reuse_sink:
        unload_verified(shared)
    R["load_at_end"] = loadavg()
    (RCPT / f"{tag}-tapstab.json").write_text(json.dumps(R, indent=1, default=str))
    log(f"{tag}: peaks={[r['peak'] for r in R['rows']]} L1000={[r['L1000'] for r in R['rows']]} "
        f"links_ok={[bool([x for x in r['links'] if 'monitor_' in x]) for r in R['rows']]}")
    return R


# ------------------------------------------------------------------ b9 verification
def b9(tag="b9", reps=3):
    """tight re-verification of the sharp boundary claims found in b1/b1x."""
    R = {"tag": tag, "load_at_start": loadavg()}
    d0 = RUNS / tag; d0.mkdir(parents=True, exist_ok=True)
    src = TAGS / "src.wav"
    ogg = RUNS / "b1" / "core" / "ogg_r0" / "m.ogg"

    # 1. AIFF metadata: does anything survive wav->aif->wav?
    meta = "-metadata title=r85btitle -metadata artist=r85bartist -metadata comment=r85bcmt -metadata album=r85balb -metadata date=2026"
    tw = d0 / "tagged.wav"
    sh(f"ffmpeg -y -v error -i {src} {meta} {tw}")
    aif_rows = []
    for rep in range(reps):
        a = d0 / f"aif_r{rep}.aif"; b = d0 / f"aif_back_r{rep}.wav"
        r1 = conv(tw, a); r2 = conv(a, b)
        aif_rows.append({"rep": rep, "aif_rc": r1["rc"], "aif_info_tags": infometa2(a)[0],
                         "back_rc": r2["rc"], "back_tags": infometa2(b)[0],
                         "back_raw": infometa2(b)[2][:400]})
    # control: wav -> wav directly
    w2 = d0 / "wav_back.wav"; conv(tw, w2)
    R["aif_meta"] = {"reps": aif_rows, "wav_to_wav_tags": infometa2(w2)[0],
                     "aif_info_text": infometa2(d0 / "aif_r0.aif")[2][:500]}
    # ffmpeg-written aiff control
    fa = d0 / "ff_aif.aif"
    sh(f"ffmpeg -y -v error -i {src} {meta} {fa}")
    fb = d0 / "ff_aif_back.wav"; conv(fa, fb)
    R["aif_meta"]["ffmpeg_aif_back_tags"] = infometa2(fb)[0]

    # 2. carry-vs-container-default discriminator: distinct input codecs -> .wav (no flag)
    codec_rows = []
    variants = {}
    for enc, ext in [("-pcmu8", "wav"), ("-pcm24", "wav"), ("-pcm32", "wav"), ("-float32", "wav"),
                     ("-ulaw", "wav"), ("-ima-adpcm", "wav"), ("-pcm24", "flac"), ("-pcm24", "aiff")]:
        v = d0 / f"var_{enc[1:]}.{ext}"
        r = conv(src, v, enc)
        variants[f"{enc[1:]}.{ext}"] = v
        codec_rows.append({"flag": enc, "ext": ext, "rc": r["rc"], "format": sinfo(v).get("format"),
                           "bytes": r["bytes"]})
    R["codec_variants"] = codec_rows
    # now the discriminator legs: each variant -> .wav with NO flag
    disc = []
    for name, v in variants.items():
        if not v.exists():
            continue
        o = d0 / f"disc_{name}.wav"
        r = conv(v, o)
        i = sinfo(o)
        rr = conv(o, str(o) + ".raw")
        src_raw = conv(v, d0 / f"disc_{name}.src.raw")
        disc.append({"in": name, "in_format": sinfo(v).get("format"), "out_format": i.get("format"),
                     "out_bytes": r["bytes"], "rc": r["rc"],
                     "payload_eq_input_payload": rr.get("sha") == src_raw.get("sha"),
                     "stdout": r["stdout"][:120]})
    R["carry_vs_default"] = disc

    # 3. .ogg vs .oga asymmetry (no flag), from PCM and from Vorbis
    asym = []
    for lab, inp in [("pcm", src), ("vorbis", ogg)]:
        for e in ["ogg", "oga", "opus", "mp3"]:
            for rep in range(reps):
                o = d0 / f"asym_{lab}_{e}_r{rep}.{e}"
                r = conv(inp, o)
                asym.append({"in": lab, "ext": e, "rep": rep, "rc": r["rc"], "bytes": r["bytes"],
                             "format": sinfo(o).get("format") if r["exists"] else None,
                             "stdout": r["stdout"][:140]})
    R["ogg_vs_oga"] = asym
    # explicit -pcm16 -> .ogg message
    R["pcm16_to_ogg"] = conv(src, d0 / "pcm16_to_ogg.ogg", "-pcm16")

    # 4. Opus/Ogg-family byte diff confinement (serialno+CRC?) 4 reps
    for e, fl in [("opus", ""), ("oga", "-vorbis")]:
        shas = []
        for rep in range(4):
            o = d0 / f"det_{e}_r{rep}.{e}"
            shas.append(conv(src, o, fl)["sha"])
        diffs = [ogg_pair_diff(d0 / f"det_{e}_r0.{e}", d0 / f"det_{e}_r{r}.{e}") for r in range(1, 4)]
        R[f"det_{e}"] = {"shas": shas, "distinct": len(set(shas)), "diffs": diffs}

    # 5. truncated-header rc class at several lengths
    full = src.read_bytes()
    tr = []
    for n in (12, 44, 60, 100, 1000):
        p = d0 / f"trunc_{n}.wav"
        p.write_bytes(full[:n])
        i = sinfo(p)
        tr.append({"n": n, "rc": i["rc"], "unrecognised": i["unrecognised"], "err": i["err_stdout"],
                   "frames": i["frames"], "format": i["format"], "stdout": i["stdout"][:160]})
    R["trunc_class"] = tr

    # 6. normalize stub reproducibility + a convert-to-wav stub control
    nz = []
    for rep in range(2):
        o = d0 / f"nz_sil_{rep}.wav"
        r = conv(RUNS / "b1" / "core" / "sil.wav", o)
        nz.append({"rep": rep, "rc": r["rc"], "bytes": r["bytes"], "stdout": r["stdout"][:160],
                   "head": Path(o).read_bytes()[:48].hex() if r["exists"] else None})
    R["stub_repro"] = nz

    (RCPT / f"{tag}-verify.json").write_text(json.dumps(R, indent=1, default=str))
    log(f"{tag}: aif_back={[r['back_tags'] for r in aif_rows]} wav2wav={R['aif_meta']['wav_to_wav_tags']} "
        f"carry={[(d['in'], d['in_format'], d['out_format'], d['payload_eq_input_payload']) for d in disc]} "
        f"asym=" + str([(a["in"], a["ext"], a["rc"], a["format"]) for a in asym[:8]]))
    return R


# ------------------------------------------------------------------ mixing
MIX_TONES = {
    "a1k.wav": (2, [(0, 1000, 12000)]),
    "b25.wav": (2, [(1, 2500, 12000)]),
    "mono1k.wav": (2, [(0, 1000, 12000), (1, 1000, 12000)]),
    "mono1kinv.wav": (2, [(0, 1000, -12000), (1, 1000, -12000)]),
    "h1k.wav": (2, [(0, 1000, 24576), (1, 1000, 24576)]),
    "h25.wav": (2, [(0, 2500, 24576), (1, 2500, 24576)]),
    "sil.wav": (2, []),
}


def ensure_tones():
    for nm, (ch, specs) in MIX_TONES.items():
        p = TAGS / nm
        if not p.exists():
            gen_tone(p, 3.0, ch, specs)
    if not (TAGS / "tone12.wav").exists():
        gen_tone(TAGS / "tone12.wav", 12.0, 2, [(0, 1000, 12000), (1, 1000, 12000)])


def mix_stage(tag, reps=3):
    R = {"tag": tag, "load_at_start": loadavg()}
    ensure_tones()
    sink = "r85b_mix"
    ls = load_sink(sink)
    ok, b = wait_node(sink)
    R["sink_load"] = ls
    R["sink_nodes"] = [{"id": i, "serial": b["nodes"][i]["serial"], "name": b["nodes"][i]["name"]}
                       for i in nid_by_name(b, sink)]
    sink_serial = R["sink_nodes"][0]["serial"] if R["sink_nodes"] else None
    d0 = RUNS / tag / "mix"; d0.mkdir(parents=True, exist_ok=True)

    def play(f, tg, tgt=sink, env=None):
        return spawn(f"pw-play -P node.name={tg} --target {tgt} {f}", env=env)

    def tap(wavf, frames=192000, tag_name="r85b_tap", shape="prop_name"):
        if shape == "prop_name":
            return spawn(f"pw-record -P stream.capture.sink=true -P node.name={tag_name} "
                         f"--target {sink} --rate 48000 --channels 2 --format s16 -n {frames} {wavf}")
        if shape == "noprop_serial":
            return spawn(f"pw-record -P node.name={tag_name} --target {sink_serial} --rate 48000 "
                         f"--channels 2 --format s16 -n {frames} {wavf}")
        if shape == "prop_serial":
            return spawn(f"pw-record -P stream.capture.sink=true -P node.name={tag_name} "
                         f"--target {sink_serial} --rate 48000 --channels 2 --format s16 -n {frames} {wavf}")
        raise ValueError(shape)

    def tap_valid(tagname):
        b = board()
        ids = nid_by_name(b, tagname)
        if not ids:
            return False, []
        lk = linkstr(b, ids[0])
        return any(f"{sink}:monitor_" in x for x in lk), lk

    def run_mix(leg, files, reps=3, delay2=0.0, tapframes=192000, waits=2.3):
        rows = []
        for rep in range(reps):
            d = d0 / leg / f"r{rep}"; d.mkdir(parents=True, exist_ok=True)
            tagname = f"r85b_{leg}_t{rep}"
            tapmeta = {"attempts": []}
            rec = None
            for shape in ("prop_name", "noprop_serial", "prop_serial"):
                rec = tap(d / "mon.wav", frames=tapframes, tag_name=tagname, shape=shape)
                time.sleep(0.35)
                ok, lk = tap_valid(tagname)
                tapmeta["attempts"].append({"shape": shape, "linked": ok, "links": lk})
                if ok:
                    tapmeta["shape"] = shape
                    break
                killp(rec); rec = None
                try:
                    (d / "mon.wav").unlink()
                except FileNotFoundError:
                    pass
                time.sleep(0.2)
            if rec is None:
                rows.append({"tap_failed": True, "tap_check": tapmeta})
                continue
            procs = [play(f, f"r85b_{leg}_p{i}") for i, f in enumerate(files)]
            if delay2:
                time.sleep(delay2)
                procs.append(play(files[0], f"r85b_{leg}_pd"))
            time.sleep(waits)
            b = board()
            lk = {f"r85b_{leg}_p{i}": (linkstr(b, nid_by_name(b, f"r85b_{leg}_p{i}")[0])
                                       if nid_by_name(b, f"r85b_{leg}_p{i}") else []) for i in range(len(files))}
            if delay2 and nid_by_name(b, f"r85b_{leg}_pd"):
                lk["r85b_{leg}_pd"] = linkstr(b, nid_by_name(b, f"r85b_{leg}_pd")[0])
            ports = {}
            for i, n in b["nodes"].items():
                if n["name"] == sink:
                    ports["sink_input_ports"] = sorted(
                        {b["ports"][l["ip"]]["name"] for l in b["links"] if l["in"] == i})
            for p in procs:
                try:
                    p.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    killp(p)
            try:
                rec.wait(timeout=4)
            except subprocess.TimeoutExpired:
                killp(rec)
            w = windows(d / "mon.wav")
            rows.append({"links": lk, "sink_ports": ports, "tap_check": tapmeta,
                         "play_rcs": [p.returncode for p in procs], "win": w, "n_windows": len(w)})
        return rows

    R["mix1"] = run_mix("m1", [TAGS / "a1k.wav"], reps)
    R["mix2"] = run_mix("m2", [TAGS / "a1k.wav", TAGS / "b25.wav"], reps)
    R["mixdup"] = run_mix("md", [TAGS / "a1k.wav", TAGS / "a1k.wav"], reps)
    R["mixinv"] = run_mix("mi", [TAGS / "mono1k.wav", TAGS / "mono1kinv.wav"], reps)
    R["mixclip"] = run_mix("mc", [TAGS / "h1k.wav", TAGS / "h25.wav"], reps)
    R["mixdelay"] = run_mix("mx", [TAGS / "mono1k.wav"], reps, delay2=0.5)

    # aplay env targeting lattice
    aplay = []
    other = "r85b_alt"
    load_sink(other); wait_node(other)
    cases = [("node", {"PIPEWIRE_NODE": sink}), ("props", {"PIPEWIRE_PROPS": f"{{ target.object={sink} }}"}),
             ("none", {}), ("bogus_node", {"PIPEWIRE_NODE": "no_such_sink_r85b"}),
             ("conflict", {"PIPEWIRE_NODE": sink, "PIPEWIRE_PROPS": f"{{ target.object={other} }}"}),
             ("props_serial", {"PIPEWIRE_PROPS": f"{{ target.object={R['sink_nodes'][0]['serial']} }}"})]
    for envdesc, env in cases:
        for rep in range(2):
            p = spawn(f"aplay -D pipewire -q {TAGS/'sil.wav'}", env=env)
            time.sleep(0.7)
            b = board()
            nd = [i for i, n in b["nodes"].items() if n["name"] and "aplay" in str(n["name"])]
            aplay.append({"env": envdesc, "rep": rep, "env_vars": env,
                          "nodes": [{"name": b["nodes"][i]["name"], "class": b["nodes"][i]["class"],
                                     "target.object": b["nodes"][i]["props"].get("target.object"),
                                     "node.target": b["nodes"][i]["props"].get("node.target")} for i in nd],
                          "links": [linkstr(b, i) for i in nd]})
            killp(p)
    R["aplay_env"] = aplay
    unload_verified(other)
    unload_verified(sink)
    R["load_at_end"] = loadavg()
    (RCPT / f"{tag}-mix.json").write_text(json.dumps(R, indent=1, default=str))
    log(f"{tag} mix: " + " ".join(
        f"{k}={[ (r['win'][1]['L1000'], r['win'][1]['R2500'], r['win'][1]['peak'], r['win'][1]['rail']) if len(r['win'])>1 else None for r in R[k]][:3] }"
        for k in ("mix1", "mix2", "mixdup", "mixinv", "mixclip")))
    return R


# ------------------------------------------------------------------ capture
def cap_stage(tag, reps=3, with_load=False):
    R = {"tag": tag, "load_at_start": loadavg(), "with_load": with_load}
    ensure_tones()
    sink = "r85b_tone"
    load_sink(sink); ok, b = wait_node(sink)
    R["tone_sink"] = [{"id": i, "serial": b["nodes"][i]["serial"]} for i in nid_by_name(b, sink)]
    d0 = RUNS / tag / "cap"; d0.mkdir(parents=True, exist_ok=True)
    tone_proc = spawn(f"pw-play -P node.name=r85b_tonep --target {sink} {TAGS/'tone12.wav'}")
    time.sleep(0.6)

    def load_remap(name, master=f"{sink}.monitor"):
        rc, out, err = sh(f"pactl load-module module-remap-source master={master} source_name={name}")
        for _ in range(60):
            b = board()
            if nid_by_name(b, name):
                return {"idx": out.strip(), "rc": rc, "err": err.strip()[:120],
                        "node": nid_by_name(b, name)[0]}
            time.sleep(0.1)
        return {"idx": out.strip(), "rc": rc, "err": err.strip()[:120], "node": None}

    def timeline_rec(leg, target, delete_fn=None, act_t=1.5, dur=4.6, frames=288000, prop=False,
                     rep=0, tag_name=None):
        d = d0 / leg / f"r{rep}"; d.mkdir(parents=True, exist_ok=True)
        f = d / "cap.wav"
        tn = tag_name or f"r85b_{leg}_rec"
        props = "-P stream.capture.sink=true" if prop else ""
        p = spawn(f"pw-record {props} -P node.name={tn} --target {target} "
                  f"--rate 48000 --channels 2 --format s16 -n {frames} {f}")
        tl = []
        pre = post = None
        t0 = time.time(); acted = False
        while time.time() - t0 < dur:
            el = time.time() - t0
            if not acted and el >= act_t and delete_fn:
                pre = {"mod_line": mod_line(leg_src)[1]}
                delete_fn()
                time.sleep(0.05)
                post = {"mod_line": mod_line(leg_src)[1]}
                acted = True
            b = board()
            tl.append({"t": round(el, 2), "sz": size(f), "links": linkstr(b, nid_by_name(b, tn)[0])
                       if nid_by_name(b, tn) else [], "node": bool(nid_by_name(b, tn))})
            time.sleep(0.1)
        rc = p.poll()
        alive = rc is None
        if alive:
            rc = killp(p)
        wins = windows(f) if f.exists() and f.stat().st_size > 1000 else []
        post_win = [w for w in wins if w["t0"] >= act_t + 0.2]
        pre_win = [w for w in wins if w["t0"] < act_t - 0.2]
        growth = None
        if len(tl) >= 4 and post_win:
            s1, s2 = tl[len(tl) // 2]["sz"], tl[-1]["sz"]
            if s1 is not None and s2 is not None and s2 >= 0:
                growth = round((s2 - s1) / max(0.01, (tl[-1]["t"] - tl[len(tl) // 2]["t"])), 0)
        return {"target": str(target), "prop": prop, "rc": rc, "alive_when_killed": alive,
                "final_bytes": size(f), "pre_unload": pre, "post_unload": post,
                "growth_bytes_per_s": growth, "timeline": tl,
                "pre_win": [{"t0": w["t0"], "peak": w["peak"], "rms": w["rms"]} for w in pre_win],
                "post_win": [{"t0": w["t0"], "peak": w["peak"], "rms": w["rms"], "zeros": w["zeros"]} for w in post_win]}

    # --- A14 verbatim replay: remap source, delete mid-record (3 reps)
    leg_src = "r85b_vsrc"
    R["A14_reps"] = []
    for rep in range(reps):
        lr = load_remap(leg_src)
        R.setdefault("vsrc_loads", []).append(lr)
        time.sleep(0.4)
        row = timeline_rec("a14", leg_src, delete_fn=lambda: unload_verified(leg_src), rep=rep)
        row["vsrc_load"] = lr
        R["A14_reps"].append(row)
        time.sleep(0.2)

    # --- late-bind: absent name, then a conforming remap source appears mid-stall
    late = "r85b_late"
    R["late_bind"] = []
    for rep in range(reps):
        d = d0 / "late" / f"r{rep}"; d.mkdir(parents=True, exist_ok=True)
        f = d / "cap.wav"
        p = spawn(f"pw-record -P node.name=r85b_late_rec --target {late} --rate 48000 "
                  f"--channels 2 --format s16 -n 288000 {f}")
        tl = []; t0 = time.time(); loaded = None
        while time.time() - t0 < 4.6:
            el = time.time() - t0
            if loaded is None and el >= 1.5:
                loaded = load_remap(late)
            b = board()
            tl.append({"t": round(el, 2), "sz": size(f),
                       "links": linkstr(b, nid_by_name(b, "r85b_late_rec")[0])
                       if nid_by_name(b, "r85b_late_rec") else [],
                       "late_node": bool(nid_by_name(b, late))})
            time.sleep(0.1)
        rc = p.poll(); alive = rc is None
        if alive:
            rc = killp(p)
        R["late_bind"].append({"rc": rc, "loaded": loaded, "final_bytes": size(f),
                               "late_node_alive_end": bool(nid_by_name(board(), late)), "timeline": tl})
        unload_verified(late)
        time.sleep(0.2)

    # --- addressing: which --target forms bind on capture (noprop / prop)
    vsrc_load = load_remap("r85b_addr")
    time.sleep(0.4)
    b = board()
    vn = nid_by_name(b, "r85b_addr")
    vs = {"node": vn[0] if vn else None,
          "serial": b["nodes"][vn[0]]["serial"] if vn else None,
          "ports": sorted(b["ports"][l["op"]]["name"] for l in b["links"]
                          if l["on"] == (vn[0] if vn else -1)) if vn else [],
          "all_ports": sorted({p["name"] for p in b["ports"].values() if p["node"] == (vn[0] if vn else -1)})}
    sink_serial = R["tone_sink"][0]["serial"]
    addr = []
    for label, tgt, prop in [("vsrc_name_noprop", "r85b_addr", False),
                             ("vsrc_name_prop", "r85b_addr", True),
                             ("vsrc_serial_noprop", vs["serial"], False),
                             ("vsrc_objid_noprop", vs["node"], False),
                             ("sink_serial_noprop", sink_serial, False),
                             ("sink_name_noprop", sink, False),
                             ("sink_name_prop", sink, True),
                             ("default_monitor_prop", "@DEFAULT_MONITOR@", True)]:
        d = d0 / f"addr_{label}"; d.mkdir(parents=True, exist_ok=True)
        f = d / "cap.wav"
        tn = f"r85b_ad_{label}"
        props = "-P stream.capture.sink=true" if prop else ""
        p = spawn(f"pw-record {props} -P node.name={tn} --target {tgt} --rate 48000 "
                  f"--channels 2 --format s16 -n 96000 {f}")
        time.sleep(1.1)
        bb = board()
        lk = linkstr(bb, nid_by_name(bb, tn)[0]) if nid_by_name(bb, tn) else []
        rc = killp(p)
        addr.append({"label": label, "target": str(tgt), "prop": prop, "links": lk,
                     "bytes": size(f), "rc": rc})
    R["target_addr"] = addr
    R["vsrc_info"] = vs
    unload_verified("r85b_addr")

    # --- self-destruct ladder: media.class=Audio/Source null-sink x client kind
    def selfd_leg(client_kind, reps=2, idle_s=0.0):
        rows = []
        for rep in range(reps):
            nm = "r85b_sd"
            sh(f"pactl load-module module-null-sink sink_name={nm} media.class=Audio/Source")
            ok, b = wait_node(nm, t=6.0)
            t_load = time.time()
            proc = None; d = d0 / "selfd" / client_kind / f"r{rep}"; d.mkdir(parents=True, exist_ok=True)
            f = d / "cap.wav"
            tl = []
            def sample(el):
                bb = board()
                idx, line = mod_line(nm)
                tl.append({"t": round(el, 3), "node": bool(nid_by_name(bb, nm)),
                           "module": idx, "links": linkstr(bb, nid_by_name(bb, nm)[0])
                           if nid_by_name(bb, nm) else []})
            if client_kind == "idle":
                t0 = time.time()
                while time.time() - t0 < idle_s:
                    sample(time.time() - t0); time.sleep(0.1)
            else:
                if client_kind == "pwrecord_noprop":
                    proc = spawn(f"pw-record -P node.name=r85b_sdrec --target {nm} --rate 48000 "
                                 f"--channels 2 --format s16 -n 96000 {f}")
                elif client_kind == "pwrecord_prop":
                    proc = spawn(f"pw-record -P stream.capture.sink=true -P node.name=r85b_sdrec "
                                 f"--target {nm} --rate 48000 --channels 2 --format s16 -n 96000 {f}")
                elif client_kind == "pwcat":
                    proc = spawn(f"pw-cat -r -P node.name=r85b_sdrec --target {nm} --rate 48000 "
                                 f"--channels 2 --format s16 {f}")
                elif client_kind == "parec":
                    proc = spawn(f"parec -d {nm} --rate=48000 --channels=2 --format=s16le "
                                 f"--file-format=wav {f}")
                elif client_kind == "ffmpeg":
                    proc = spawn(f"ffmpeg -y -v error -f pulse -i {nm} -ar 48000 -ac 2 {f}")
                elif client_kind == "pwplay":
                    proc = spawn(f"pw-play -P node.name=r85b_sdplay --target {nm} {TAGS/'sil.wav'}")
                t0 = time.time()
                while time.time() - t0 < 1.2:
                    sample(time.time() - t0); time.sleep(0.05)
            rc = killp(proc)
            idx, line = mod_line(nm)
            death = next((x["t"] for x in tl if x["module"] is None), None)
            node_death = next((x["t"] for x in tl if not x["node"]), None)
            rows.append({"client": client_kind, "rep": rep, "rc": rc, "loaded_ok": ok,
                         "death_t_module": death, "death_t_node": node_death,
                         "module_alive_end": idx is not None, "bytes": size(f), "timeline": tl})
            unload_verified(nm)
            time.sleep(0.2)
        return rows

    R["selfd"] = {}
    for kind in ["idle", "pwrecord_noprop", "pwrecord_prop", "pwcat", "parec", "ffmpeg", "pwplay"]:
        reps_k = 3 if kind == "idle" else 2
        R["selfd"][kind] = selfd_leg(kind, reps=reps_k, idle_s=6.0 if kind == "idle" else 0)

    # --- manual pw-link to the self-destruct node (does linking alone kill it?)
    rows = []
    for rep in range(2):
        nm = "r85b_sd"
        sh(f"pactl load-module module-null-sink sink_name={nm} media.class=Audio/Source")
        ok, b = wait_node(nm, t=6.0)
        nid = nid_by_name(b, nm)
        ports = sorted({p["name"] for p in b["ports"].values() if p["node"] == (nid[0] if nid else -1)})
        out_port = next((p for p in ports if p.startswith("capture")), None)
        rc, so, se = (None, "", "no port")
        if out_port:
            rc, so, se = sh(f"pw-link {nm}:{out_port} r85b_tone:playback_FL")
        tl = []
        t0 = time.time()
        while time.time() - t0 < 1.2:
            bb = board(); idx, line = mod_line(nm)
            tl.append({"t": round(time.time() - t0, 3), "node": bool(nid_by_name(bb, nm)), "module": idx,
                       "links": linkstr(bb, nid_by_name(bb, nm)[0]) if nid_by_name(bb, nm) else []})
            time.sleep(0.05)
        rows.append({"rep": rep, "ports": ports, "out_port": out_port, "pwlink_rc": rc,
                     "pwlink_err": (se or so).strip()[:120], "timeline": tl})
        unload_verified(nm)
        time.sleep(0.2)
    R["pwlink_selfd"] = rows

    killp(tone_proc)
    unload_verified(sink)
    R["load_at_end"] = loadavg()
    (RCPT / f"{tag}-cap.json").write_text(json.dumps(R, indent=1, default=str))
    a14 = R["A14_reps"]
    log(f"{tag} cap: A14 growth={[r['growth_bytes_per_s'] for r in a14]} "
        f"post_peak={[ (r['post_win'][0]['peak'] if r['post_win'] else None) for r in a14]} "
        f"alive={[r['alive_when_killed'] for r in a14]} "
        f"selfd_deaths={{k: [r['death_t_module'] for r in v] for k, v in R['selfd'].items()}} "
        f"pwlink={[r['timeline'][-1]['module'] for r in rows]}")
    return R


# ------------------------------------------------------------------ pactl
def pactl_stage(tag, cycles=6, with_load=False):
    R = {"tag": tag, "load_at_start": loadavg(), "with_load": with_load}
    a, bn = "r85b_a", "r85b_b"
    load_sink(a); load_sink(bn)
    wait_node(a); wait_node(bn)
    b = board()
    info = {}
    for nm in (a, bn):
        ids = nid_by_name(b, nm)
        info[nm] = {"id": ids[0] if ids else None, "serial": b["nodes"][ids[0]]["serial"] if ids else None,
                    "props_serial": b["nodes"][ids[0]]["props"].get("object.serial") if ids else None}
    R["nodes"] = info
    rc, so, _ = sh("pactl list short sinks")
    R["short_sinks"] = [l for l in so.splitlines() if "r85b" in l or "SPDIF" in l]
    rc, so, _ = sh("pactl list short sources")
    R["short_sources"] = [l for l in so.splitlines() if "r85b" in l or "SPDIF" in l]

    def getter(verb, arg):
        rc, so, se = sh(f"pactl {verb} {shlex.quote(str(arg))}")
        return {"rc": rc, "stdout1": so.strip().splitlines()[0] if so.strip() else "",
                "stderr1": se.strip().splitlines()[0] if se.strip() else ""}

    sa, sb = info[a], info[bn]
    rows = []
    for label, arg in [("name", a), ("other_name", bn), ("serial", sa["serial"]),
                       ("other_serial", sb["serial"]), ("object_id", sa["id"]),
                       ("at_default_sink", "@DEFAULT_SINK@"), ("at_default_source", "@DEFAULT_SOURCE@"),
                       ("at_default_monitor", "@DEFAULT_MONITOR@"), ("dot_monitor", a + ".monitor"),
                       ("bogus", "no_such_sink_r85b"), ("empty", ""), ("neg", "-1"), ("zero", "0"),
                       ("one", "1"), ("big", "99999999")]:
        rows.append({"arg_kind": label, "arg": str(arg), "get_sink_volume": getter("get-sink-volume", arg),
                     "get_source_volume": getter("get-source-volume", arg)})
    R["addr_matrix"] = rows

    # disambiguate `0`: give every candidate a distinct volume, then read 0
    sh(f"pactl set-sink-volume {a} 13%")
    sh(f"pactl set-sink-volume {bn} 27%")
    rc, ds, _ = sh("pactl get-default-sink"); ds = ds.strip()
    disp = {"a_volume": getter("get-sink-volume", a), "b_volume": getter("get-sink-volume", bn),
            "default_sink": ds, "default_volume": getter("get-sink-volume", ds),
            "zero_volume": getter("get-sink-volume", "0"),
            "zero_source_volume": getter("get-source-volume", "0"),
            "zero_name_collision": None}
    R["zero_disambiguation"] = disp

    # name/serial collision: a sink literally NAMED with another sink's serial
    coll = str(sa["serial"])
    lc = load_sink(coll); wait_node(coll)
    sh(f"pactl set-sink-volume {coll} 55%")
    bb = board()
    coll_node = nid_by_name(bb, coll)
    R["collision"] = {"collision_name": coll, "load": lc,
                      "collision_node": {"id": coll_node[0] if coll_node else None,
                                         "serial": bb["nodes"][coll_node[0]]["serial"] if coll_node else None},
                      "short_rows": [l for l in sh("pactl list short sinks")[1].splitlines() if "r85b" in l],
                      "get_by_number": getter("get-sink-volume", coll),
                      "a_volume_now": getter("get-sink-volume", a)}
    # capture side of the collision: pw-record --target <number> (noprop)
    f = RUNS / tag / "collision_cap.wav"
    p = spawn(f"pw-record -P node.name=r85b_coll_rec --target {coll} --rate 48000 --channels 2 "
              f"--format s16 -n 96000 {f}")
    time.sleep(1.1)
    bb = board()
    lk = linkstr(bb, nid_by_name(bb, "r85b_coll_rec")[0]) if nid_by_name(bb, "r85b_coll_rec") else []
    killp(p)
    R["collision"]["capture_target_number"] = {"links": lk, "bytes": size(f)}
    unload_verified(coll)

    # monitor shares the sink serial
    R["monitor_serial"] = {"sink_serial": sa["serial"],
                           "get_source_volume_by_sink_serial": getter("get-source-volume", sa["serial"]),
                           "get_sink_volume_by_sink_serial": getter("get-sink-volume", sa["serial"]),
                           "monitor_name": getter("get-source-volume", a + ".monitor")}

    # numeric parse edges
    edges = []
    for lab, arg in [("leading_space", f" {sa['serial']}"), ("plus", f"+{sa['serial']}"),
                     ("hex", hex(int(sa["serial"]))), ("float", f"{sa['serial']}.0"),
                     ("zero_pad", f"0{sa['serial']}"), ("suffix", f"{sa['serial']}x"),
                     ("trailing_space", f"{sa['serial']} "), ("underscore", "31_599")]:
        edges.append({"label": lab, "arg": arg, "r": getter("get-sink-volume", arg)})
    R["numeric_edges"] = edges

    # move-sink-input by name / serial / bogus
    mv = []
    for lab, tgt in [("name", bn), ("serial", sb["serial"]), ("bogus", "no_such_r85b")]:
        p = spawn(f"pw-play -P node.name=r85b_mv_{lab} --target {a} {TAGS/'a1k.wav'}")
        time.sleep(0.8)
        bb = board()
        sids = nid_by_name(bb, f"r85b_mv_{lab}")
        ser = bb["nodes"][sids[0]]["serial"] if sids else None
        rc, so, se = sh(f"pactl move-sink-input {ser} {shlex.quote(str(tgt))}") if ser else (None, "", "no stream")
        time.sleep(0.6)
        bb = board()
        lk = linkstr(bb, nid_by_name(bb, f"r85b_mv_{lab}")[0]) if nid_by_name(bb, f"r85b_mv_{lab}") else []
        mv.append({"to": lab, "target": str(tgt), "stream_serial": ser, "rc": rc,
                   "stdout": so.strip()[:120], "stderr": se.strip()[:120], "links_after": lk})
        killp(p)
    R["move_sink_input"] = mv

    # serial monotonicity across unload/reload cycles (+ module index reuse)
    ser_hist, idx_hist = [], []
    for i in range(cycles):
        u = unload_verified(a)
        time.sleep(0.15)
        l = load_sink(a)
        wait_node(a)
        bb = board()
        ids = nid_by_name(bb, a)
        ser_hist.append(bb["nodes"][ids[0]]["serial"] if ids else None)
        idx_hist.append({"load_idx": l["idx"], "unload_idx": u["idx"]})
        time.sleep(0.15)
    R["serial_monotonic"] = {"serials": ser_hist, "idx": idx_hist,
                             "all_distinct": len(set(ser_hist)) == len(ser_hist),
                             "strictly_increasing": all(
                                 int(ser_hist[i]) < int(ser_hist[i + 1])
                                 for i in range(len(ser_hist) - 1) if ser_hist[i] and ser_hist[i + 1]),
                             "reused_indices": len(set(x["load_idx"] for x in idx_hist)) != len(idx_hist)}
    unload_verified(a); unload_verified(bn)
    R["load_at_end"] = loadavg()
    (RCPT / f"{tag}-pactl.json").write_text(json.dumps(R, indent=1, default=str))
    log(f"{tag} pactl: serial_ok={R['serial_monotonic']['all_distinct']} "
        f"strict={R['serial_monotonic']['strictly_increasing']} serials={ser_hist} "
        f"zero={disp['zero_volume']['stdout1'][:40]} collision={R['collision']['get_by_number']['stdout1'][:60]}")
    return R


# ------------------------------------------------------------------ cleanup
def cleanup(tag="final"):
    """unload every r85b_* module, kill hogs, kill leftover r85b pw-* clients."""
    report = {"tag": tag, "actions": []}
    rc, so, _ = sh("pactl list short modules")
    for line in so.splitlines():
        if "r85b" in line:
            parts = line.split("\t") if "\t" in line else line.split(None, 2)
            report["actions"].append({"unload": line.strip()[:200],
                                      "r": sh(f"pactl unload-module {parts[0]}")[0]})
    stop_hogs()
    report["stray_hogs_killed"] = kill_stray_hogs()
    rc, so, _ = sh("pgrep -a -f 'r85b_|pw-record|pw-play|pw-cat|parec|aplay'")
    for line in so.splitlines():
        if "r85b" in line and "pgrep" not in line:
            pid = line.split()[0]
            if int(pid) in (os.getpid(), os.getppid()) or "r85b_probe" in line or "r85b-boundary" in line:
                continue  # never kill this seat's own harness/driver
            try:
                os.kill(int(pid), signal.SIGKILL)
                report["actions"].append({"killed_pid": pid, "line": line[:160]})
            except (ProcessLookupError, ValueError):
                pass
    time.sleep(0.5)
    rc, so, _ = sh("pactl list short modules")
    report["r85b_modules_left"] = [l for l in so.splitlines() if "r85b" in l]
    b = board()
    report["r85b_nodes_left"] = [n["name"] for n in b["nodes"].values()
                                 if n["name"] and str(n["name"]).startswith("r85b")]
    rc, so, _ = sh("pgrep -a -f r85b")
    report["r85b_procs_left"] = [l for l in so.splitlines()
                                 if "pgrep" not in l and "r85b_probe" not in l
                                 and "run_stages" not in l]
    report["hogs_left"] = len(HOGS)
    report["loadavg"] = loadavg()
    report["default_sink"] = sh("pactl get-default-sink")[1].strip()
    report["scratch_du"] = sh(f"du -sh {HERE}")[1].strip()
    (RCPT / f"{tag}-cleanup.json").write_text(json.dumps(report, indent=1, default=str))
    log(f"cleanup {tag}: mods_left={len(report['r85b_modules_left'])} "
        f"nodes_left={len(report['r85b_nodes_left'])} procs_left={len(report['r85b_procs_left'])} "
        f"hogs={report['hogs_left']} load={report['loadavg']}")
    return report


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("b0", "all"):
        b0("baseline")
    if which == "b1":
        sndfile_core("b1")
    if which == "b1x":
        b1x()
    if which == "b2":
        log(f"hogs up: {start_hogs(40)}")
        try:
            sndfile_core("b2", reps=3, page_reps=8)
        finally:
            log(f"hogs down: {stop_hogs()}")
    if which == "b3":
        mix_stage("b3", reps=3)
    if which == "b4":
        log(f"hogs up: {start_hogs(40)}")
        try:
            mix_stage("b4", reps=3)
        finally:
            log(f"hogs down: {stop_hogs()}")
    if which == "b5":
        cap_stage("b5", reps=3)
    if which == "b6":
        log(f"hogs up: {start_hogs(40)}")
        try:
            cap_stage("b6", reps=3, with_load=True)
        finally:
            log(f"hogs down: {stop_hogs()}")
    if which == "b7":
        pactl_stage("b7", cycles=6)
    if which == "b8":
        log(f"hogs up: {start_hogs(40)}")
        try:
            pactl_stage("b8", cycles=6, with_load=True)
        finally:
            log(f"hogs down: {stop_hogs()}")
    if which == "b9":
        b9()
    if which == "b7x":
        b7x()
    if which == "b3t":
        b3t("b3t", reps=12)
        b3t("b3tr", reps=6, reuse_sink=True)
    if which in ("cleanup", "all"):
        cleanup("final")
    if which == "all":
        b0("final")
    (HERE / "b_run_log.txt").write_text("\n".join(LOG) + "\n")
