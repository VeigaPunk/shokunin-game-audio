#!/usr/bin/env python3
"""r84 scout harness — ALSA-direct + pulse-compat deeper params.
Seat-owned nodes/streams tagged r84alsa_*. Writes stay under corpus/live/r84-scout/.
"""
import json, os, re, signal, subprocess, sys, time, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TMP = ROOT / "tmp"; RUNS = ROOT / "runs"; RCPTS = ROOT / "receipts"
for d in (TMP, RUNS, RCPTS): d.mkdir(parents=True, exist_ok=True)
TAG = "r84alsa"
NS = "r84alsa_ns"; NS2 = "r84alsa_ns2"
SR = 48000

# ---------- bounded exec ----------
def run(cmd, timeout, env_extra=None, cwd=None):
    env = dict(os.environ); env.update(env_extra or {})
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env, cwd=cwd, start_new_session=True,
                         stdin=subprocess.DEVNULL)
    try:
        out, err = p.communicate(timeout=timeout)
        to = False
    except subprocess.TimeoutExpired:
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        out, err = p.communicate(); to = True
    return {"rc": p.returncode, "wall": round(time.time() - t0, 3),
            "out": out.decode("utf-8", "replace")[-4000:],
            "err": err.decode("utf-8", "replace")[-4000:],
            "timeout": to, "cmd": " ".join(str(c) for c in cmd)}

class Proc:
    """spawn + sample while alive."""
    def __init__(self, cmd, env_extra=None):
        env = dict(os.environ); env.update(env_extra or {})
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  env=env, start_new_session=True,
                                  stdin=subprocess.DEVNULL)
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
                "timeout": False,
                "out": out.decode("utf-8", "replace")[-3000:],
                "err": err.decode("utf-8", "replace")[-3000:]}

# ---------- graph witnesses ----------
def pw_dump():
    return json.loads(subprocess.run(["pw-dump"], capture_output=True).stdout)

def nodes_named(*subs):
    out = []
    for o in pw_dump():
        if o.get("type") != "PipeWire:Interface:Node": continue
        pr = o.get("info", {}).get("props", {}) or {}
        nm = str(pr.get("node.name", ""))
        if any(s in nm for s in subs):
            out.append({"id": o.get("id"), "serial": o.get("info", {}).get("serial") or pr.get("object.serial"),
                        "name": nm, "props": pr,
                        "state": o.get("info", {}).get("state")})
    return out

def linkmap():
    """port -> {'>': [dst], '<': [src]}"""
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
    lm = linkmap(); out = []
    for port, e in lm.items():
        if port.startswith(name + ":"): out += e[">"]
    return out

def producers_of(name):
    lm = linkmap(); out = []
    for port, e in lm.items():
        if port.startswith(name + ":"): out += e["<"]
    return out

def pactl_json(what):
    r = subprocess.run(["pactl", "-f", "json", "list", what], capture_output=True)
    try: return json.loads(r.stdout)
    except Exception: return []

def pcm_status(card, dev, direction):  # direction 'p'|'c'
    f = f"/proc/asound/card{card}/pcm{dev}{direction}/sub0/status"
    try: return Path(f).read_text().splitlines()[0].strip()
    except Exception: return "?"

def pcm_owner(card, dev, direction):
    f = f"/proc/asound/card{card}/pcm{dev}{direction}/sub0/info"
    try:
        for ln in Path(f).read_text().splitlines():
            if ln.startswith("owner_pid"): return ln.split(":")[1].strip()
    except Exception: pass
    return "?"

# ---------- audio gen + analysis ----------
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
    b = Path(path).read_bytes()
    i = b.find(b"data")
    if i < 0: return np.zeros((0, 2), np.int16)
    sz = struct.unpack("<I", b[i + 4:i + 8])[0]
    a = np.frombuffer(b[i + 8:i + 8 + min(sz, len(b) - i - 8)], np.int16)
    return a[:len(a) // 2 * 2].reshape(-1, 2)

def windows(path, freqs=(1000, 1500, 2000), win=0.25):
    """per-window peak + goertzel amps at freqs; returns list."""
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

def file_hdr(path):
    try:
        b = Path(path).read_bytes()[:64]
        return {"size": Path(path).stat().st_size, "magic": b[:4].decode("ascii", "replace"),
                "head_hex": b[:48].hex()}
    except FileNotFoundError:
        return {"size": -1, "magic": "MISSING"}

# ---------- module lifecycle (index-verified, never by-name) ----------
def load_ns(name):
    r = run(["pactl", "load-module", "module-null-sink", f"sink_name={name}"], 8)
    idx = (r["out"].strip() or "0")
    try: idx_i = int(idx)
    except ValueError: idx_i = -1
    # verify the index really owns `name`
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

# ---------- leg driver ----------
def leg_dir(probe, leg, rep):
    d = RUNS / probe / leg / f"rep{rep}"
    d.mkdir(parents=True, exist_ok=True)
    return d

def record_leg(probe, leg, rep, res, extra=None):
    d = leg_dir(probe, leg, rep)
    (d / "cmd").write_text(str(res.get("cmd", "")))
    (d / "stdout").write_text(str(res.get("out", "")))
    (d / "stderr").write_text(str(res.get("err", "")))
    (d / "result.json").write_text(json.dumps({**{k: res.get(k) for k in ("rc", "wall", "timeout")}, **(extra or {})}, indent=1))

def play_at(ns, wav, name, vol="1.0", extra=None):
    return Proc(["pw-play", "-P", f"node.name={name}", "--target", ns, "--volume", vol, wav] + (extra or []))
