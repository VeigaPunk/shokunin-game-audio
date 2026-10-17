#!/usr/bin/env python3
"""r85 scout harness — sndfile lattice + concurrent streams + capture-side
source loss + pactl addressing. Seat-owned everything; nodes tagged r85snd_*.
Scratch only under corpus/live/r85-scout/."""
import json, os, re, shlex, signal, subprocess, sys, time, wave, hashlib
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
TAGS = HERE / "tags"; RUNS = HERE / "runs"; RCPT = HERE / "receipts"
for d in (TAGS, RUNS, RCPT): d.mkdir(exist_ok=True)
SR = 48000

def sh(cmd, timeout=15, env=None, cwd=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                       text=True, timeout=timeout, env=e, cwd=cwd)
    return p.returncode, p.stdout, p.stderr

def spawn(cmd, env=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.Popen(cmd, shell=isinstance(cmd, str), env=e,
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                         text=True, start_new_session=True)
    return p

def killp(p, sig=signal.SIGTERM):
    try:
        os.killpg(p.pid, sig)
    except ProcessLookupError:
        pass
    try:
        return p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        return p.wait(timeout=5)

def pwdump():
    rc, out, err = sh("pw-dump", timeout=15)
    return json.loads(out) if rc == 0 else []

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

def linkstr(b, nid):
    """readable consumers/producers for node nid"""
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

def nid_by_name(b, name):
    return [i for i, n in b["nodes"].items() if n["name"] == name]

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def gen_tone(path, dur, chans, specs, rate=SR, amp_head="s16"):
    """specs: list of (chan, freq, amp). chans=2 stereo."""
    n = int(dur * rate)
    data = np.zeros((n, chans), dtype=np.float64)
    t = np.arange(n) / rate
    for ch, f, a in specs:
        data[:, ch] += a * np.sin(2 * np.pi * f * t)
    data = np.clip(data, -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(chans); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(data.tobytes())
    return n

def fft_amp(x, f, rate=SR):
    n = len(x)
    if n == 0: return 0.0
    k = int(round(f * n / rate))
    seg = np.abs(np.fft.rfft(x.astype(np.float64)))
    lo, hi = max(0, k - 3), min(len(seg), k + 4)
    return float(2 * seg[lo:hi].max() / n)

def read_wav(path):
    with wave.open(str(path), "rb") as w:
        ch, sw, fr, nf = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(nf)
    a = np.frombuffer(raw, dtype="<i2")
    return a.reshape(-1, ch) if ch > 1 else a[:, None], fr

def windows(path, win=0.25, freqs=(1000, 2500, 3000, 4500)):
    """per-window: peak + fft amps at tag freqs + rail count."""
    a, fr = read_wav(path)
    wl = int(win * fr); out = []
    for s in range(0, len(a) - wl + 1, wl):
        w_ = a[s:s + wl]
        rec = {"t0": round(s / fr, 2), "peak": int(np.abs(w_).max()),
               "rail": int((np.abs(w_) >= 32760).sum())}
        for f in freqs:
            rec[f"L{int(f)}"] = round(fft_amp(w_[:, 0], f), 1)
            if w_.shape[1] > 1:
                rec[f"R{int(f)}"] = round(fft_amp(w_[:, 1], f), 1)
        out.append(rec)
    return out

def mod_index(name):
    rc, out, _ = sh("pactl list short modules")
    for line in out.splitlines():
        if f"sink_name={name}" in line:
            return int(line.split()[0])
    return None

def load_sink(name, extra=""):
    sh(f"pactl load-module module-null-sink sink_name={name} {extra}")
    for _ in range(40):
        b = pwdump; b = board()
        if nid_by_name(b, name): return nid_by_name(b, name)[0]
        time.sleep(0.1)
    return None

def unload_mod(name):
    idx = mod_index(name)
    if idx is not None:
        return sh(f"pactl unload-module {idx}")
    return (None, "", "no module")

def wait_node(name, want=True, t=8.0):
    end = time.time() + t
    while time.time() < end:
        b = board()
        found = bool(nid_by_name(b, name))
        if found == want: return True, b
        time.sleep(0.08)
    return False, board()

# ---------------------------------------------------------------- S1 sndfile
def s1(reps=3):
    R = {}
    os.makedirs(RUNS / "s1", exist_ok=True)
    src = TAGS / "src.wav"
    # deterministic-ish source: dual-tone + a short marker ramp, 1.5 s s16 stereo
    n = gen_tone(src, 1.5, 2, [(0, 997, 10000), (1, 1502, 7000)])
    # metadata-tagged variants via ffmpeg
    meta = "-metadata title=r85title -metadata artist=r85artist -metadata comment=r85cmt -metadata album=r85alb -metadata date=2026"
    for ext in ("wav", "flac", "ogg"):
        sh(f"ffmpeg -y -v error -i {src} {meta} {TAGS}/tagged.{ext}")
    R["src_sha"] = sha(src)

    def conv(inp, outp, flags=""):
        cmd = f"sndfile-convert {flags} {inp} {outp}".replace("  ", " ")
        rc, so, se = sh(cmd, timeout=20)
        r = {"rc": rc, "stderr": se.strip()[:200],
             "out_exists": Path(outp).exists(),
             "out_bytes": Path(outp).stat().st_size if Path(outp).exists() else None,
             "out_sha": sha(outp) if Path(outp).exists() and Path(outp).stat().st_size else None}
        return r

    def chain(leg, infile, e1, e2):
        """infile -> tmp.e1 -> tmp.e2 -> raw; 3 reps"""
        rows = []
        for rep in range(reps):
            d = RUNS / "s1" / leg / f"r{rep}"; d.mkdir(parents=True, exist_ok=True)
            f1, f2 = d / f"m.{e1}", d / f"o.{e2}"
            r1 = conv(infile, f1); r2 = conv(f1, f2)
            r3 = conv(f2, d / "o.raw")
            rows.append({"hop1": r1, "hop2": r2, "toraw": r3})
        return rows

    R["rt_flac"] = chain("rt_flac", src, "flac", "wav")
    R["rt_ogg"] = chain("rt_ogg", src, "ogg", "wav")
    R["rt_aif"] = chain("rt_aif", src, "aif", "wav")
    R["rt_wavex"] = chain("rt_wavex", src, "wavex", "wav")
    R["flac_ogg"] = chain("flac_ogg", TAGS / "tagged.flac", "ogg", "flac")

    # identity wav->wav and decode payloads for lossless verdict
    ident = []
    ref_raw = RUNS / "s1" / "src.raw"; conv(src, ref_raw)
    ref_sha = sha(ref_raw)
    for rep in range(reps):
        d = RUNS / "s1" / "ident" / f"r{rep}"; d.mkdir(parents=True, exist_ok=True)
        r1 = conv(src, d / "o.wav"); r2 = conv(d / "o.wav", d / "o.raw")
        ident.append({"wav": r1, "raw": r2, "payload_eq_src": r2["out_sha"] == ref_sha})
    R["ident_wav"] = ident
    # flac decode payload vs src payload
    fl = RUNS / "s1" / "rt_flac" / "r0" / "o.raw"
    R["flac_lossless"] = sha(fl) == ref_sha if fl.exists() else None
    og = RUNS / "s1" / "rt_ogg" / "r0" / "o.raw"
    R["ogg_lossless"] = sha(og) == ref_sha if og.exists() else None
    R["ogg_decode_xrep_same"] = len({r["toraw"]["out_sha"] for r in R["rt_ogg"]}) == 1
    R["flac_encode_xrep_same"] = len({r["hop1"]["out_sha"] for r in R["rt_flac"]}) == 1
    R["ogg_encode_xrep_same"] = len({r["hop1"]["out_sha"] for r in R["rt_ogg"]}) == 1
    R["aif_lossless"] = sha(RUNS / "s1" / "rt_aif" / "r0" / "o.raw") == ref_sha

    # sndfile-cmp verdicts
    cmp_rows = []
    for a, b, nm in [(src, RUNS/"s1"/"rt_flac"/"r0"/"o.wav", "wav_vs_flaCdec"),
                     (src, RUNS/"s1"/"rt_ogg"/"r0"/"o.wav", "wav_vs_oggdec"),
                     (src, RUNS/"s1"/"ident"/"r0"/"o.wav", "wav_vs_wav")]:
        rc, so, se = sh(f"sndfile-cmp {a} {b}")
        cmp_rows.append({"pair": nm, "rc": rc, "stdout": so.strip()[:300], "stderr": se.strip()[:200]})
    R["sndfile_cmp"] = cmp_rows

    # extension mismatch: content-flac named .wav; content-wav named .flac
    import shutil
    shutil.copyfile(RUNS/"s1"/"rt_flac"/"r0"/"m.flac", RUNS/"s1"/"fake.wav")
    shutil.copyfile(src, RUNS/"s1"/"fake.flac")
    mis = []
    for f in ("fake.wav", "fake.flac"):
        rc, so, se = sh(f"sndfile-info {RUNS/'s1'/f}")
        mis.append({"file": f, "rc": rc, "fmtline": [l for l in so.splitlines() if "Format" in l][:2], "err": se.strip()[:120]})
        rc2, so2, se2 = sh(f"sndfile-convert {RUNS/'s1'/f} {RUNS/'s1'/f}.out.wav")
        mis.append({"file": f+".out", "conv_rc": rc2, "conv_err": se2.strip()[:160],
                    "out": Path(str(RUNS/'s1'/f)+'.out.wav').exists()})
    R["ext_mismatch"] = mis

    # -override-sample-rate: relabel, not resample?
    ovs = []
    for rep in range(reps):
        d = RUNS / "s1" / "ovr" / f"r{rep}"; d.mkdir(parents=True, exist_ok=True)
        r = conv(src, d/"o.wav", "-override-sample-rate=44100")
        rc, so, se = sh(f"sndfile-info {d/'o.wav'}")
        rate = [l.strip() for l in so.splitlines() if "Sample Rate" in l][:1]
        frames = [l.strip() for l in so.splitlines() if "Frames" in l][:1]
        r2 = conv(d/"o.wav", d/"o.raw")
        ovs.append({"rc": r["rc"], "sha": r["out_sha"], "rate": rate, "frames": frames,
                    "payload_eq_src": r2["out_sha"] == ref_sha})
    R["override_rate"] = ovs
    # normalize determinism
    nz = []
    for rep in range(reps):
        d = RUNS/"s1"/"norm"/f"r{rep}"; d.mkdir(parents=True, exist_ok=True)
        r = conv(src, d/"o.wav", "-normalize")
        rc, so, se = sh(f"sndfile-info {d/'o.wav'}")
        mx = [l.strip() for l in so.splitlines() if "Signal Max" in l][:1]
        nz.append({"rc": r["rc"], "sha": r["out_sha"], "max": mx})
    R["normalize"] = nz
    # encoding lattice: wav container x encodings + vorbis/opus/alac to own containers
    enc_rows = []
    encs = ["-pcm16", "-pcm24", "-pcm32", "-float32", "-float64", "-pcmu8", "-pcms8",
            "-ulaw", "-alaw", "-ima-adpcm", "-ms-adpcm", "-gsm610"]
    for enc in encs:
        rc, so, se = sh(f"sndfile-convert {enc} {src} {RUNS}/s1/enc_{enc[1:]}.wav")
        p = RUNS/f"s1/enc_{enc[1:]}.wav"
        enc_rows.append({"enc": enc, "cont": "wav", "rc": rc, "err": se.strip()[:160],
                         "bytes": p.stat().st_size if p.exists() else None})
    for enc, ext in [("-vorbis", "ogg"), ("-opus", "opus"), ("-opus", "ogg"),
                     ("-alac16", "caf"), ("-alac24", "caf"), ("-vorbis", "wav"),
                     ("-alac16", "wav"), ("-pcm16", "flac"), ("-float32", "flac"),
                     ("-pcm16", "ogg"), ("-vorbis", "flac")]:
        outp = RUNS/f"s1/encX_{enc[1:]}_{ext}.{ext}"
        rc, so, se = sh(f"sndfile-convert {enc} {src} {outp}")
        enc_rows.append({"enc": enc, "cont": ext, "rc": rc, "err": se.strip()[:160],
                         "bytes": outp.stat().st_size if outp.exists() else None})
    R["enc_lattice"] = enc_rows
    # endian
    for e in ("little", "big", "cpu"):
        outp = RUNS/f"s1/end_{e}.wav"
        rc, so, se = sh(f"sndfile-convert -endian={e} {src} {outp}")
        R.setdefault("endian", []).append({"e": e, "rc": rc, "err": se.strip()[:100],
             "magic": outp.read_bytes()[:4].hex() if outp.exists() else None,
             "sha": sha(outp) if outp.exists() else None})
    # metadata survival: sndfile-info on tagged files, then convert hops
    def infometa(p):
        rc, so, se = sh(f"sndfile-info {p}")
        keys = {}
        for l in so.splitlines():
            m = re.match(r"\s*(Title|Artist|Comment|Album|Date|Software|Copyright|Track|Genre|License|BPM|Encoded|Location)\s*:\s*(.*)", l)
            if m: keys[m.group(1)] = m.group(2).strip()
        return keys
    R["meta_read"] = {f"tagged.{e}": infometa(TAGS/f"tagged.{e}") for e in ("wav","flac","ogg")}
    hops = []
    for i,(a,b) in enumerate([("tagged.wav","flac"),("tagged.wav","ogg"),("tagged.flac","wav"),
                              ("tagged.ogg","wav"),("tagged.wav","wav"),("tagged.flac","ogg"),
                              ("tagged.wav","aif")]):
        outp = RUNS/f"s1/metahop{i}.{b}"
        rc, so, se = sh(f"sndfile-convert {TAGS/a} {outp}")
        hops.append({"from": a, "to": b, "rc": rc, "meta": infometa(outp)})
    R["meta_hops"] = hops
    # error classes
    errs = []
    for cmd, nm in [("sndfile-info /nonexistent_r85.wav", "info_missing"),
                    ("sndfile-info /etc/hostname", "info_garbage"),
                    ("sndfile-convert /nonexistent_r85.wav o.wav", "conv_missing_in"),
                    (f"sndfile-convert {src} /nonexistent_dir_r85/o.wav", "conv_bad_outdir"),
                    (f"sndfile-convert {src} o.bogusext", "conv_bad_ext"),
                    (f"sndfile-convert -bogusflag {src} o.wav", "conv_bad_flag"),
                    (f"sndfile-convert {src}", "conv_one_arg")]:
        rc, so, se = sh(cmd, cwd=RUNS/"s1")
        errs.append({"leg": nm, "rc": rc, "stdout": so.strip()[:160], "stderr": se.strip()[:200]})
    R["errors"] = errs
    (RCPT/"s1-sndfile.json").write_text(json.dumps(R, indent=1, default=str))
    return R

# ---------------------------------------------------------------- S2 mixing
def s2(reps=3):
    R = {}
    os.makedirs(RUNS/"s2", exist_ok=True)
    gen_tone(TAGS/"a1k.wav", 2.0, 2, [(0, 1000, 12000)])          # L only
    gen_tone(TAGS/"b25.wav", 2.0, 2, [(1, 2500, 12000)])          # R only
    gen_tone(TAGS/"c3k.wav", 2.0, 2, [(0, 3000, 8000), (1, 3000, 8000)])
    gen_tone(TAGS/"d45.wav", 2.0, 2, [(0, 4500, 8000), (1, 4500, 8000)])
    gen_tone(TAGS/"h1k.wav", 2.0, 2, [(0, 1000, 24576), (1, 1000, 24576)])
    gen_tone(TAGS/"h25.wav", 2.0, 2, [(0, 2500, 24576), (1, 2500, 24576)])
    gen_tone(TAGS/"sil.wav", 1.5, 2, [])
    sink = "r85snd_mix"
    load_sink(sink)
    ok, b = wait_node(sink)
    R["sink_id"] = nid_by_name(b, sink)

    def play(f, tag, tgt=sink, env=None):
        return spawn(f"pw-play -P node.name={tag} --target {tgt} {f}", env=env)

    def tap(wavf, frames=192000):
        return spawn(f"pw-record -P stream.capture.sink=true -P node.name=r85snd_tap "
                     f"--target {sink} --rate 48000 --channels 2 --format s16 -n {frames} {wavf}")

    def links_of(tags):
        b = board()
        res = {}
        for tg in tags:
            for i in nid_by_name(b, tg):
                res[tg] = linkstr(b, i)
        return res

    def run_mix(leg, files, waits=0.9):
        rows = []
        for rep in range(reps):
            d = RUNS/"s2"/leg/f"r{rep}"; d.mkdir(parents=True, exist_ok=True)
            rec = tap(d/"mon.wav")
            time.sleep(0.45)
            procs = [play(f, f"r85snd_{leg}_p{i}") for i, f in enumerate(files)]
            time.sleep(2.3)
            lk = links_of([f"r85snd_{leg}_p{i}" for i in range(len(files))])
            for p in procs:
                try: p.wait(timeout=4)
                except subprocess.TimeoutExpired: killp(p)
            try: rcr = rec.wait(timeout=4)
            except subprocess.TimeoutExpired: rcr = killp(rec)
            w = windows(d/"mon.wav")
            rows.append({"links": lk, "rec_rc": rcr,
                         "play_rcs": [p.returncode for p in procs],
                         "win": w})
        return rows

    R["mix1"] = run_mix("m1", [TAGS/"a1k.wav"])          # single-stream control
    R["mix2"] = run_mix("m2", [TAGS/"a1k.wav", TAGS/"b25.wav"])   # L tone + R tone
    R["mix4"] = run_mix("m4", [TAGS/"a1k.wav", TAGS/"b25.wav", TAGS/"c3k.wav", TAGS/"d45.wav"])
    R["mixclip"] = run_mix("mc", [TAGS/"h1k.wav", TAGS/"h25.wav"]) # sum > full scale
    R["mixdup"] = run_mix("md", [TAGS/"a1k.wav", TAGS/"a1k.wav"])  # SAME file twice -> in-phase sum 2x?

    # aplay through the pipewire ALSA plugin: env target vectors
    aplay_env = []
    for envdesc, env in [("PIPEWIRE_NODE", {"PIPEWIRE_NODE": sink}),
                         ("PIPEWIRE_PROPS", {"PIPEWIRE_PROPS": "{ target.object=r85snd_mix }"}),
                         ("none", {})]:
        for rep in range(2):
            p = spawn(f"aplay -D pipewire -q {TAGS/'sil.wav'}", env=env)
            time.sleep(0.7)
            b = board()
            nds = [n for n in b["nodes"].values() if n["name"] and "aplay" in str(n["name"])]
            links = [linkstr(b, i) for i,n in b["nodes"].items() if n["name"] and "aplay" in str(n["name"])]
            aplay_env.append({"env": envdesc, "rep": rep,
                "nodes": [{"name": n["name"], "class": n["class"],
                           "target.object": n["props"].get("target.object"),
                           "node.target": n["props"].get("node.target")} for n in nds],
                "links": links})
            killp(p)
    R["aplay_env"] = aplay_env
    unload_mod(sink)
    (RCPT/"s2-mixing.json").write_text(json.dumps(R, indent=1, default=str))
    return R

# ---------------------------------------------------------------- S3 capture-side source loss
def s3(reps=3):
    R = {}
    os.makedirs(RUNS/"s3", exist_ok=True)
    srcname = "r85snd_src"
    # a source-mode null sink = Audio/Source producing (probably) silence
    sh(f"pactl load-module module-null-sink sink_name={srcname} media.class=Audio/Source")
    ok, b = wait_node(srcname)
    srcid = nid_by_name(b, srcname)
    R["src_node"] = [{"id": i, **b["nodes"][i]} for i in srcid]
    # content check: capture 1 s of it
    def recleg(leg, target, prop, act, frames=288000, act_t=1.5, dur_s=4.2, env=None):
        rows = []
        for rep in range(reps):
            d = RUNS/"s3"/leg/f"r{rep}"; d.mkdir(parents=True, exist_ok=True)
            f = d/"cap.wav"
            props = f"-P stream.capture.sink=true" if prop else ""
            p = spawn(f"pw-record {props} -P node.name=r85snd_{leg}_rec --target {target} "
                      f"--rate 48000 --channels 2 --format s16 -n {frames} {f}", env=env)
            tl = []
            t0 = time.time(); acted = False
            while time.time() - t0 < dur_s:
                el = time.time() - t0
                if not acted and el >= act_t:
                    act["fn"]()
                    acted = True
                b = board()
                rl = []
                for i in nid_by_name(b, f"r85snd_{leg}_rec"):
                    rl = linkstr(b, i)
                sz = f.stat().st_size if f.exists() else -1
                tl.append({"t": round(el, 2), "sz": sz, "links": rl})
                time.sleep(0.1)
            rc = p.poll()
            if rc is None: rc = killp(p)
            rows.append({"rc": rc, "timeline": tl,
                         "final_bytes": f.stat().st_size if f.exists() else None,
                         "win": windows(f) if f.exists() and f.stat().st_size > 100 else []})
        return rows

    # A: no-prop capture of a source; delete the source module mid-record
    R["src_loss_noprop"] = recleg("sl", srcname, False,
        {"fn": lambda: unload_mod(srcname)})
    # re-create source for later legs
    sh(f"pactl load-module module-null-sink sink_name={srcname} media.class=Audio/Source")
    wait_node(srcname)
    # B: same but TWO sources live; does re-link pick the other source or default?
    srcname2 = "r85snd_src2"
    sh(f"pactl load-module module-null-sink sink_name={srcname2} media.class=Audio/Source")
    wait_node(srcname2)
    R["src_loss_two_srcs"] = recleg("sl2", srcname, False,
        {"fn": lambda: unload_mod(srcname)})
    # C: monitor-side control (r80 L4 echo): sink monitor target + prop, unload sink
    snk = "r85snd_mon"
    load_sink(snk)
    R["mon_loss_prop"] = recleg("ml", snk, True, {"fn": lambda: unload_mod(snk)})
    # D: target APPEARANCE: record --target <absent name> (no prop) stalls 44B;
    #    then load the module mid-stall -> late link?
    def appear_leg(leg, name):
        rows = []
        for rep in range(reps):
            d = RUNS/"s3"/leg/f"r{rep}"; d.mkdir(parents=True, exist_ok=True)
            f = d/"cap.wav"
            p = spawn(f"pw-record -P node.name=r85snd_{leg}_rec --target {name} "
                      f"--rate 48000 --channels 2 --format s16 -n 288000 {f}")
            tl = []; t0 = time.time(); acted = False
            while time.time() - t0 < 4.2:
                el = time.time() - t0
                if not acted and el >= 1.5:
                    sh(f"pactl load-module module-null-sink sink_name={name} media.class=Audio/Source")
                    acted = True
                b = board()
                rl = []
                for i in nid_by_name(b, f"r85snd_{leg}_rec"):
                    rl = linkstr(b, i)
                tl.append({"t": round(el,2), "sz": f.stat().st_size if f.exists() else -1, "links": rl})
                time.sleep(0.1)
            rc = p.poll()
            if rc is None: rc = killp(p)
            rows.append({"rc": rc, "timeline": tl,
                         "final_bytes": f.stat().st_size if f.exists() else None})
            unload_mod(name)
        return rows
    R["src_appear"] = appear_leg("ap", "r85snd_appear")
    # E: native destroy instead of module unload
    sh(f"pactl load-module module-null-sink sink_name=r85snd_srcd media.class=Audio/Source")
    wait_node("r85snd_srcd")
    def destroy_src():
        b = board()
        for i in nid_by_name(b, "r85snd_srcd"):
            sh(f"pw-cli destroy {i}")
    R["src_loss_destroy"] = recleg("sd", "r85snd_srcd", False, {"fn": destroy_src})
    # F: pw-record on a source WITH the prop (does prop reroute at connect? r79 B12 says default-sink monitor)
    R["src_prop_at_connect"] = recleg("sp", "r85snd_src2", True, {"fn": lambda: None})
    # cleanup
    for nm in (srcname, srcname2, snk, "r85snd_srcd"):
        unload_mod(nm)
    (RCPT/"s3-srcloss.json").write_text(json.dumps(R, indent=1, default=str))
    return R

# ---------------------------------------------------------------- S4 pactl addressing
def s4():
    R = {}
    a, bn = "r85snd_a", "r85snd_b"
    load_sink(a); load_sink(bn)
    ok, b = wait_node(a); ok2, _ = wait_node(bn)
    b = board()
    info = {}
    for nm in (a, bn):
        for i in nid_by_name(b, nm):
            n = b["nodes"][i]
            info[nm] = {"id": i, "serial": n["serial"], "name": n["name"]}
    R["nodes"] = info
    # pactl short-list index vs serial vs id
    rc, out, _ = sh("pactl list short sinks")
    R["short_sinks"] = [l for l in out.splitlines() if "r85snd" in l or "SPDIF" in l]
    rc2, out2, _ = sh("pactl list short sources")
    R["short_sources"] = [l for l in out2.splitlines() if "r85snd" in l]

    def getter(verb, arg):
        rc, so, se = sh(f"pactl {verb} {shlex.quote(str(arg))}")
        return {"rc": rc, "stdout1": so.strip().splitlines()[0] if so.strip() else "",
                "stderr1": se.strip().splitlines()[0] if se.strip() else ""}

    sa, sb = info[a], info[bn]
    serials = {"a_serial": sa["serial"], "b_serial": sb["serial"]}
    addr_rows = []
    for label, arg in [("name", a), ("other_name", bn),
                       ("serial", sa["serial"]), ("other_serial", sb["serial"]),
                       ("object_id", sa["id"]), ("id_as_serial_guess", 0),
                       ("at_default_sink", "@DEFAULT_SINK@"),
                       ("at_default_source", "@DEFAULT_SOURCE@"),
                       ("at_default_monitor", "@DEFAULT_MONITOR@"),
                       ("dot_monitor_on_sink", a + ".monitor"),
                       ("bogus", "no_such_sink_r85"), ("empty", ""), ("neg", "-1"),
                       ("name_like_serial", "99999999")]:
        addr_rows.append({"arg_kind": label, "arg": str(arg),
                          "get_sink_volume": getter("get-sink-volume", arg)})
    R["sink_addr"] = addr_rows
    # source side: r85snd_a.monitor source exists; find its pactl index + object serial
    src_addr = []
    rc, out, _ = sh("pactl list short sources")
    monidx = None
    for l in out.splitlines():
        if a + ".monitor" in l: monidx = l.split()[0]
    b = board()
    # the monitor is a port on the sink node in pw terms; pactl synthesizes a source
    for label, arg in [("name.monitor", a + ".monitor"), ("mon_short_idx", monidx),
                       ("at_default_monitor", "@DEFAULT_MONITOR@"),
                       ("at_default_sink", "@DEFAULT_SINK@"),
                       ("sink_node_name", a), ("sink_serial", sa["serial"]),
                       ("bogus", "no_such_source_r85")]:
        src_addr.append({"arg_kind": label, "arg": str(arg),
                         "get_source_volume": getter("get-source-volume", arg)})
    R["source_addr"] = src_addr
    # pw-record --target serial / object.id on capture (with+without prop)
    cap = []
    for label, tgt, prop in [("serial", sa["serial"], True), ("serial_noprop", sa["serial"], False),
                             ("objid", sa["id"], True), ("objid_noprop", sa["id"], False),
                             ("name", a, True), ("name_noprop", a, False),
                             ("name.mon_noprop", a + ".monitor", False),
                             ("at_defmon", "@DEFAULT_MONITOR@", True)]:
        f = RUNS/f"s4/cap_{label}.wav"
        props = "-P stream.capture.sink=true" if prop else ""
        p = spawn(f"pw-record {props} -P node.name=r85snd_cap_{label} --target {tgt} "
                  f"--rate 48000 --channels 2 --format s16 -n 96000 {f}")
        time.sleep(1.2)
        b = board()
        lk = []
        for i in nid_by_name(b, f"r85snd_cap_{label}"):
            lk = linkstr(b, i)
        rc = killp(p)
        cap.append({"label": label, "target": str(tgt), "prop": prop, "links": lk,
                    "bytes": f.stat().st_size if f.exists() else None})
    R["pw_target_addr"] = cap
    # pw-cli info addressing contrast: global id vs serial
    for label, arg in [("id", sa["id"]), ("serial", sa["serial"])]:
        rc, so, se = sh(f"pw-cli info {arg}")
        R.setdefault("pwcli", []).append({"arg_kind": label, "rc": rc,
            "head": so.strip().splitlines()[:2], "err": se.strip()[:80]})
    # move-sink-input by name vs serial (own stream, own sinks)
    mv = []
    f = TAGS/"a1k.wav"
    for label, tgt in [("name", a), ("serial", sb["serial"]), ("bogus", "no_such_r85")]:
        p = spawn(f"pw-play -P node.name=r85snd_mv_{label} --target {a} {f}")
        time.sleep(0.8)
        rc, out, _ = sh("pactl list short sink-inputs")
        idx = None
        for l in out.splitlines():
            if "pw-play" in l or "pw-cat" in l:
                # match our stream: pw-cat based names show application.name
                pass
        b = board()
        sids = nid_by_name(b, f"r85snd_mv_{label}")
        # find sink-input index: pactl 'Sink Input #' order vs object.serial of stream
        ser = None
        if sids: ser = b["nodes"][sids[0]]["serial"]
        for l in out.splitlines():
            if ser is not None and l.split()[0] == str(ser):
                idx = l.split()[0]
        if idx:
            rc2, so2, se2 = sh(f"pactl move-sink-input {idx} {tgt}")
        else:
            rc2, so2, se2 = (None, "", "no sink-input idx found")
        time.sleep(0.6)
        b = board()
        lk = []
        for i in nid_by_name(b, f"r85snd_mv_{label}"):
            lk = linkstr(b, i)
        mv.append({"to": label, "tgt": str(tgt), "stream_serial": ser, "sink_input_idx": idx,
                   "move_rc": rc2, "move_err": se2.strip()[:120], "links_after": lk})
        killp(p)
    R["move_addr"] = mv
    # serial reuse on reload
    unload_mod(a)
    load_sink(a)
    ok, b = wait_node(a)
    newser = b["nodes"][nid_by_name(b, a)[0]]["serial"] if nid_by_name(b, a) else None
    R["serial_reuse"] = {"old": sa["serial"], "new": newser, "same": newser == sa["serial"]}
    for nm in (a, bn): unload_mod(nm)
    (RCPT/"s4-pactl-addr.json").write_text(json.dumps(R, indent=1, default=str))
    return R

def s0(tag):
    b = board()
    rc, o, _ = sh("pactl get-default-sink"); ds = o.strip()
    rc, o, _ = sh("pactl get-default-source"); ds2 = o.strip()
    rc, o, _ = sh("pactl list short modules")
    snap = {"default_sink": ds, "default_source": ds2,
            "foreign_nodes": [n["name"] for n in b["nodes"].values()
                              if n["name"] and not str(n["name"]).startswith("r85snd")
                              and n["name"] not in ("Midi-Bridge", "Dummy-Driver", "Freewheel-Driver")],
            "modules": o.strip().splitlines()[-10:], "raw_n": b["raw_n"]}
    (RCPT/f"s0-{tag}.json").write_text(json.dumps(snap, indent=1))
    return snap

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    if which in ("s0", "all"): s0("baseline")
    if which in ("s1", "all"): s1(reps)
    if which in ("s2", "all"): s2(reps)
    if which in ("s3", "all"): s3(reps)
    if which in ("s4", "all"): s4()
    if which in ("s9", "all"): s0("final")
