#!/usr/bin/env python3
"""r76 BOUNDARY probe (audio lane, wave-15).

Capture-direction boundary: source/device/daemon gates, bounded-capture honour,
signal-escalation classes mid-capture (TERM1 -> TERM2 -> KILL ladder),
output-name axis, write-side fifo/absent-reader classes, load replays.

Discipline (carried guards):
- every record-adjacent cell carries a hard KILL bound (harness killpg at
  `timeout_s`); the whole probe is additionally wrapped by the caller in
  `timeout -s KILL`.
- `alive_after_term1` is ONE-TERM survival only; TERM2 is always sent before
  any immunity claim is recorded.
- rc alone is never a verdict: header declared-vs-actual, ffprobe usability,
  byte-quantisation and wall_s are recorded for every cell.
- receipts are JSON; the file tree is append-only under corpus/live/r76-boundary/.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]          # repo root (audio-shokunin)
RT = HERE / "rt"                # dead-runtime dir for daemon gates
OUT = HERE / "out"
LOGS = HERE / "logs"
MEMBERS = HERE / "members"
SRC = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"
MON = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.monitor"
SINK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
DEAD_ENV = {"XDG_RUNTIME_DIR": str(RT), "PIPEWIRE_RUNTIME_DIR": str(RT),
            "PULSE_SERVER": ""}

# ---------------------------------------------------------------- utilities

def sha256(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def riff_info(path):
    """Parse RIFF/WAVE header of a (possibly truncated) output file."""
    info = {"riff": False, "wave": False, "declared": None, "data_off": None,
            "data_declared": None, "actual": None}
    try:
        info["actual"] = os.path.getsize(path)
    except OSError:
        return info
    try:
        with open(path, "rb") as f:
            head = f.read(4096)
    except OSError:
        return info
    if len(head) >= 12 and head[0:4] == b"RIFF" and head[8:12] == b"WAVE":
        info["riff"] = info["wave"] = True
        info["declared"] = int.from_bytes(head[4:8], "little")
        # walk chunks
        off = 12
        while off + 8 <= len(head):
            cid = head[off:off + 4]
            csz = int.from_bytes(head[off + 4:off + 8], "little")
            if cid == b"data":
                info["data_off"] = off + 8
                info["data_declared"] = csz
                break
            if csz in (0xFFFFFFFF, 0xFFFFFFF0):
                break
            off += 8 + csz + (csz & 1)
    return info


def probe(path):
    """ffprobe usability witness."""
    try:
        p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "stream=sample_rate,channels,codec_name:format=duration",
                            "-of", "json", str(path)],
                           capture_output=True, timeout=20)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"rc": None, "error": str(exc)}
    out = {"rc": p.returncode}
    if p.returncode == 0:
        try:
            j = json.loads(p.stdout)
            st = (j.get("streams") or [{}])[0]
            out.update(rate=st.get("sample_rate"), ch=st.get("channels"),
                       codec=st.get("codec_name"),
                       duration=float((j.get("format") or {}).get("duration", "nan")))
        except (ValueError, TypeError, KeyError) as exc:
            out["parse_error"] = str(exc)
    else:
        out["stderr_tail"] = p.stderr.decode("utf-8", "replace").strip()[-300:]
    return out


def quantise(size):
    """Buffering witness: is (size-44) a multiple of a common flush block?"""
    if size is None:
        return {}
    body = size - 44
    q = {}
    for block in (4096, 16384, 65536, 131072):
        q[f"mult{block}"] = (body % block == 0) and body > 0
    q["body"] = body
    return q


# ---------------------------------------------------------------- runner

class Cell:
    def __init__(self, name, argv, *, out=None, env=None, timeout_s=6.0,
                 ladder=None, cwd=None, pre=None, post=None, group="cell"):
        self.name = name
        self.argv = [str(a) for a in argv]
        self.out = Path(out) if out else None
        self.env = env or {}
        self.timeout_s = timeout_s
        self.ladder = ladder          # (term1_at, term2_at, kill_at)
        self.cwd = cwd
        self.pre = pre
        self.post = post
        self.group = group
        self.rec = {"cell": name, "group": group, "argv": self.argv,
                    "env_over": self.env, "out": str(self.out) if self.out else None,
                    "ladder": ladder}

    def _tail(self, path, n=400):
        try:
            data = Path(path).read_bytes()[-n:]
            return data.decode("utf-8", "replace").strip()
        except OSError:
            return ""

    def run(self, logdir):
        if self.pre:
            self.pre()
        log = Path(logdir) / f"{self.name}.log"
        env = dict(os.environ)
        env.update(self.env)
        env["LC_ALL"] = "C"
        # Carried guard: every record-adjacent cell carries its own
        # `timeout -s KILL` wrapper. The wrapper is a *backstop* (its bound sits
        # above the harness bound) and is what makes the cell orphan-safe: if
        # this harness is itself killed, the wrapper still takes the consumer
        # down. Measured here: an orphaned `arecord` blocked on a writerless
        # fifo survived the harness death until it was killed by hand.
        bound = max((self.ladder[2] if self.ladder else self.timeout_s) + 6,
                    self.timeout_s + 3)
        argv = ["timeout", "-s", "KILL", str(int(bound))] + self.argv
        self.rec["wrapper"] = argv[:4]
        t0 = time.monotonic()
        with open(log, "wb") as lf:
            proc = subprocess.Popen(argv, stdout=lf, stderr=lf,
                                    stdin=subprocess.DEVNULL, env=env,
                                    cwd=self.cwd or str(HERE),
                                    start_new_session=True)
            pgid = os.getpgid(proc.pid)
            r = self.rec
            r["pid"] = proc.pid
            alive1 = alive2 = None
            killed_by = None
            if self.ladder:
                t1, t2, tk = self.ladder
                grace = 0.5
                phase, check_at = "pre", None
                while True:
                    el = time.monotonic() - t0
                    if phase == "pre" and el >= t1:
                        r["bytes_at_term1"] = (self.out.stat().st_size
                                               if self.out and self.out.exists() else None)
                        r["wall_at_term1"] = round(el, 3)
                        os.killpg(pgid, signal.SIGTERM)
                        killed_by = "term1"
                        phase, check_at = "post1", el + grace
                    elif phase == "post1":
                        if proc.poll() is not None:
                            alive1 = False
                            r["wall_died_after_term1"] = round(el, 3)
                            break
                        if el >= check_at:
                            alive1 = True
                            r["bytes_at_term2"] = (self.out.stat().st_size
                                                   if self.out and self.out.exists() else None)
                            r["wall_at_term2"] = round(el, 3)
                            os.killpg(pgid, signal.SIGTERM)
                            killed_by = "term2"
                            phase, check_at = "post2", el + grace
                    elif phase == "post2":
                        if proc.poll() is not None:
                            alive2 = False
                            r["wall_died_after_term2"] = round(el, 3)
                            break
                        if el >= check_at:
                            alive2 = True
                            r["wall_at_kill"] = round(el, 3)
                            os.killpg(pgid, signal.SIGKILL)
                            killed_by = "kill"
                            break
                    if el > self.timeout_s + 5:
                        os.killpg(pgid, signal.SIGKILL)
                        r["runaway"] = True
                        break
                    time.sleep(0.02)
            else:
                deadline = t0 + self.timeout_s
                while proc.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.02)
                if proc.poll() is None:
                    os.killpg(pgid, signal.SIGKILL)
                    r["harness_kill"] = True
                    killed_by = "harness"
            proc.wait()
            r["wall_s"] = round(time.monotonic() - t0, 3)
            r["rc"] = proc.returncode
            r["killed_by"] = killed_by
            if self.ladder:
                r["alive_after_term1"] = bool(alive1)
                r["alive_after_term2"] = bool(alive2)
        r["stdout_tail"] = self._tail(log)
        # Only regular files are stat'ed/hashed/probed: opening a fifo or
        # /dev/* would block this harness (writer/reader-partner wait).
        if self.out and self.out.is_file():
            r["size"] = self.out.stat().st_size
            r["sha256"] = sha256(self.out)
            r["riff"] = riff_info(self.out)
            r["quant"] = quantise(r.get("size"))
            if r.get("size"):
                r["probe"] = probe(self.out)
        elif self.out:
            r["non_regular"] = True
        if self.post:
            self.post(r)
        return r


def pw_nodes():
    """PipeWire node inventory: {id, name, media.class} for audio nodes."""
    try:
        p = subprocess.run(["pw-dump"], capture_output=True, timeout=20)
        dump = json.loads(p.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return []
    nodes = []
    for obj in dump:
        if obj.get("type") != "PipeWire:Interface:Node":
            continue
        props = (obj.get("info") or {}).get("props") or {}
        nodes.append({"id": obj.get("id"), "name": props.get("node.name"),
                      "class": props.get("media.class"),
                      "desc": props.get("node.description")})
    return nodes


def monitor_node():
    for n in pw_nodes():
        nm = n.get("name") or ""
        if "SPDIF" in nm and nm.endswith(".monitor"):
            return n
    return None


# ---------------------------------------------------------------- gates

def gate_cells():
    cells = []
    A = cells.append
    mon = monitor_node() or {}
    mon_name = mon.get("name") or MON
    mon_id = str(mon.get("id") or "")
    # --- pw-record (PipeWire native capture); the output file is an ARGV token ---
    def pw(name, target=None, fname=None, env=None, n="48000", tmo=6):
        argv = ["pw-record"]
        if target is not None:
            argv += ["--target", target]
        argv += ["-n", n, OUT / fname]
        A(Cell(name, argv, out=OUT / fname, env=env, timeout_s=tmo))
    pw("gate-pw-target-src", SRC, "gate_pw_src.wav")
    pw("gate-pw-target-mon", mon_name, "gate_pw_mon.wav")
    pw("gate-pw-target-mon-pulse-name", MON, "gate_pw_monpulse.wav")
    pw("gate-pw-target-mon-bare", MON.replace(".monitor", ""), "gate_pw_monbare.wav")
    pw("gate-pw-target-sink-wrongdir", SINK, "gate_pw_sink.wav")
    pw("gate-pw-target-absent", "nosuchnode", "gate_pw_absent.wav")
    pw("gate-pw-no-target", None, "gate_pw_notarget.wav")
    pw("gate-pw-target0", "0", "gate_pw_t0.wav", tmo=4)
    pw("gate-pw-dead-daemon", SRC, "gate_pw_dead.wav", env=DEAD_ENV, tmo=4)
    if mon_id:
        pw("gate-pw-nodeid", mon_id, "gate_pw_nodeid.wav", tmo=6)
    # --- parecord (pulse-compat capture) ---
    A(Cell("gate-pa-default-src", ["parecord", "-d", "@DEFAULT_SOURCE@",
                                   "--file-format=wav", "--rate=48000",
                                   "--channels=2", OUT / "gate_pa_src.wav"],
           out=OUT / "gate_pa_src.wav", timeout_s=4))
    A(Cell("gate-pa-default-mon", ["parecord", "-d", "@DEFAULT_MONITOR@",
                                   "--file-format=wav", "--rate=48000",
                                   "--channels=2", OUT / "gate_pa_mon.wav"],
           out=OUT / "gate_pa_mon.wav", timeout_s=4))
    A(Cell("gate-pa-absent-source", ["parecord", "-d", "nosuchsource",
                                     "--file-format=wav", OUT / "gate_pa_absent.wav"],
           out=OUT / "gate_pa_absent.wav", timeout_s=4))
    A(Cell("gate-pa-named-src", ["parecord", "-d", SRC, "--file-format=wav",
                                 "--rate=48000", "--channels=2",
                                 OUT / "gate_pa_named.wav"],
           out=OUT / "gate_pa_named.wav", timeout_s=4))
    A(Cell("gate-pa-dead-runtime", ["parecord", "-d", "@DEFAULT_SOURCE@",
                                    "--file-format=wav", OUT / "gate_pa_dead.wav"],
           out=OUT / "gate_pa_dead.wav",
           env={"XDG_RUNTIME_DIR": str(RT), "PIPEWIRE_RUNTIME_DIR": str(RT),
                "PULSE_SERVER": "unix:%s/native" % RT}, timeout_s=4))
    A(Cell("gate-pa-pulse-server-dead", ["parecord", "-d", "@DEFAULT_SOURCE@",
                                         "--file-format=wav", OUT / "gate_pa_ps.wav"],
           out=OUT / "gate_pa_ps.wav",
           env={"PULSE_SERVER": "unix:%s/native" % RT}, timeout_s=4))
    # --- arecord (ALSA direct); channel count is held at 2 for the device axis
    #     except where the cell IS the channel negative control ---
    for tag, dev, ch in (("null", "null", "1"), ("null-stereo", "null", "2"),
                         ("hw00-mono", "hw:0,0", "1"), ("hw00", "hw:0,0", "2"),
                         ("hw9", "hw:9,0", "2"), ("nosuch", "nosuchdevice", "2"),
                         ("default-mono", "default", "1"),
                         ("default", "default", "2"),
                         ("pipewire", "pipewire", "2")):
        A(Cell(f"gate-ar-{tag}",
               ["arecord", "-D", dev, "-f", "S16_LE", "-r", "48000", "-c", ch,
                "-d", "1", OUT / f"gate_ar_{tag}.wav"],
               out=OUT / f"gate_ar_{tag}.wav", timeout_s=6))
    A(Cell("gate-ar-default-dead-rt",
           ["arecord", "-D", "default", "-f", "S16_LE", "-r", "48000", "-c", "2",
            "-d", "1", OUT / "gate_ar_default_dead.wav"],
           out=OUT / "gate_ar_default_dead.wav", env=DEAD_ENV, timeout_s=5))
    A(Cell("gate-ar-hw00-dead-rt",
           ["arecord", "-D", "hw:0,0", "-f", "S16_LE", "-r", "48000", "-c", "2",
            "-d", "1", OUT / "gate_ar_hw00_dead.wav"],
           out=OUT / "gate_ar_hw00_dead.wav", env=DEAD_ENV, timeout_s=5))
    # --- ffmpeg capture, both lavf legs ---
    for tag, fmt, dev in (("pulse-src", "pulse", SRC), ("pulse-mon", "pulse", MON),
                          ("pulse-default", "pulse", "default"),
                          ("pulse-absent", "pulse", "nosuchsource"),
                          ("alsa-null", "alsa", "null"),
                          ("alsa-hw00", "alsa", "hw:0,0"),
                          ("alsa-hw9", "alsa", "hw:9,0"),
                          ("alsa-nosuch", "alsa", "nosuchdevice"),
                          ("alsa-default", "alsa", "default")):
        A(Cell(f"gate-ff-{tag}",
               ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
                "-f", fmt, "-i", dev, "-t", "1", "-y",
                OUT / f"gate_ff_{tag}.wav"],
               out=OUT / f"gate_ff_{tag}.wav", timeout_s=12))
    A(Cell("gate-ff-pulse-dead-rt",
           ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
            "-f", "pulse", "-i", SRC, "-t", "1", "-y", OUT / "gate_ff_pulse_dead.wav"],
           out=OUT / "gate_ff_pulse_dead.wav", env=DEAD_ENV, timeout_s=6))
    A(Cell("gate-ff-alsa-hw00-dead-rt",
           ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
            "-f", "alsa", "-i", "hw:0,0", "-t", "1", "-y",
            OUT / "gate_ff_alsa_dead.wav"],
           out=OUT / "gate_ff_alsa_dead.wav", env=DEAD_ENV, timeout_s=8))
    return cells


# ---------------------------------------------------------------- bounded

def bounded_cells():
    cells = []
    A = cells.append
    A(Cell("bound-pw-src-n48000", ["pw-record", "--target", SRC, "-n", "48000",
                                   OUT / "bound_pw_1s.wav"],
           out=OUT / "bound_pw_1s.wav", timeout_s=8))
    A(Cell("bound-pw-src-n24000", ["pw-record", "--target", SRC, "-n", "24000",
                                   OUT / "bound_pw_halfs.wav"],
           out=OUT / "bound_pw_halfs.wav", timeout_s=8))
    A(Cell("bound-ar-null-d1", ["arecord", "-D", "null", "-f", "S16_LE", "-r", "48000",
                                "-c", "1", "-d", "1", OUT / "bound_ar_1s.wav"],
           out=OUT / "bound_ar_1s.wav", timeout_s=8))
    A(Cell("bound-ar-null-s48000", ["arecord", "-D", "null", "-f", "S16_LE",
                                    "-r", "48000", "-c", "1", "-s", "48000",
                                    OUT / "bound_ar_samp.wav"],
           out=OUT / "bound_ar_samp.wav", timeout_s=8))
    A(Cell("bound-ar-hw00-d1", ["arecord", "-D", "hw:0,0", "-f", "S16_LE",
                                "-r", "48000", "-c", "2", "-d", "1",
                                OUT / "bound_ar_hw_1s.wav"],
           out=OUT / "bound_ar_hw_1s.wav", timeout_s=8))
    A(Cell("bound-ff-pulse-src-t1", ["ffmpeg", "-hide_banner", "-nostdin",
                                     "-loglevel", "error", "-f", "pulse", "-i", SRC,
                                     "-t", "1", "-y", OUT / "bound_ff_p_1s.wav"],
           out=OUT / "bound_ff_p_1s.wav", timeout_s=12))
    A(Cell("bound-ff-alsa-null-t1", ["ffmpeg", "-hide_banner", "-nostdin",
                                     "-loglevel", "error", "-f", "alsa", "-i", "null",
                                     "-t", "1", "-y", OUT / "bound_ff_n_1s.wav"],
           out=OUT / "bound_ff_n_1s.wav", timeout_s=12))
    A(Cell("bound-ff-alsa-null-t2", ["ffmpeg", "-hide_banner", "-nostdin",
                                     "-loglevel", "error", "-f", "alsa", "-i", "null",
                                     "-t", "2", "-y", OUT / "bound_ff_n_2s.wav"],
           out=OUT / "bound_ff_n_2s.wav", timeout_s=20))
    A(Cell("bound-ff-alsa-hw00-t1", ["ffmpeg", "-hide_banner", "-nostdin",
                                     "-loglevel", "error", "-f", "alsa", "-i", "hw:0,0",
                                     "-t", "1", "-y", OUT / "bound_ff_hw_1s.wav"],
           out=OUT / "bound_ff_hw_1s.wav", timeout_s=12))
    A(Cell("bound-ff-pulse-src-fs100k", ["ffmpeg", "-hide_banner", "-nostdin",
                                         "-loglevel", "error", "-f", "pulse", "-i", SRC,
                                         "-fs", "100000", "-y",
                                         OUT / "bound_ff_fs.wav"],
           out=OUT / "bound_ff_fs.wav", timeout_s=12))
    # parecord has no native duration/sample bound: the wrapper is the bound.
    A(Cell("bound-pa-term1", ["parecord", "-d", "@DEFAULT_SOURCE@",
                              "--file-format=wav", "--rate=48000", "--channels=2",
                              OUT / "bound_pa_term.wav"],
           out=OUT / "bound_pa_term.wav", ladder=(2.0, 4.0, 6.0), timeout_s=8))
    return cells


# ---------------------------------------------------------------- sever ladder

SEVER_TARGETS = [
    ("pw", ["pw-record", "--target", SRC], OUT / "sev_pw.wav"),
    ("pa", ["parecord", "-d", "@DEFAULT_SOURCE@", "--file-format=wav",
            "--rate=48000", "--channels=2"], OUT / "sev_pa.wav"),
    ("ar-null", ["arecord", "-D", "null", "-f", "S16_LE", "-r", "48000", "-c", "1",
                 "-d", "3000"], OUT / "sev_ar_null.wav"),
    ("ar-hw", ["arecord", "-D", "hw:0,0", "-f", "S16_LE", "-r", "48000", "-c", "2",
               "-d", "300"], OUT / "sev_ar_hw.wav"),
    ("ff-pulse", ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
                  "-f", "pulse", "-i", SRC, "-y"], OUT / "sev_ff_p.wav"),
    ("ff-alsa-null", ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
                      "-f", "alsa", "-i", "null", "-y"], OUT / "sev_ff_n.wav"),
    ("ff-alsa-hw", ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
                    "-f", "alsa", "-i", "hw:0,0", "-y"], OUT / "sev_ff_hw.wav"),
]

PHASES = [("mid", (1.5, 3.5, 5.5), 8.0),     # TERM after 1.5 s of streaming
          ("early", (0.05, 2.05, 4.05), 7.0)]  # TERM before first write settles


def sever_cells(phase="mid", only=None):
    t1, t2, tk = next(p[1] for p in PHASES if p[0] == phase)
    cells = []
    for tag, argv, out in SEVER_TARGETS:
        if only and tag not in only:
            continue
        # per-phase output path: the two phases must never share a target file
        # (a stale file from the previous phase corrupted bytes_at_term1)
        p = out.with_name(out.stem + f"-{phase}" + out.suffix)
        cells.append(Cell(f"sev-{phase}-{tag}", list(argv) + [p], out=p,
                          ladder=(t1, t2, tk), timeout_s=tk + 3,
                          group=f"sever-{phase}"))
    return cells


# ---------------------------------------------------------------- name axis

def name_cells():
    cells = []
    A = cells.append
    names = ["n.wav", "n.raw", "n.bin", "n.flac", "n.foo"]
    for nm in names:
        A(Cell(f"name-pw-{nm.replace('.', '_')}",
               ["pw-record", "--target", SRC, "-n", "24000", OUT / f"nm_pw_{nm}"],
               out=OUT / f"nm_pw_{nm}", timeout_s=6, group="name"))
    A(Cell("name-pw-raw-flag", ["pw-record", "--target", SRC, "-n", "24000", "-a",
                                OUT / "nm_pw_rawflag.raw"],
           out=OUT / "nm_pw_rawflag.raw", timeout_s=6, group="name"))
    A(Cell("name-pw-container-override",
           ["pw-record", "--target", SRC, "-n", "24000", "--container", "wav",
            OUT / "nm_pw_container.raw"],
           out=OUT / "nm_pw_container.raw", timeout_s=6, group="name"))
    for nm in names:
        A(Cell(f"name-ar-{nm.replace('.', '_')}",
               ["arecord", "-D", "null", "-f", "S16_LE", "-r", "48000", "-c", "1",
                "-d", "1", OUT / f"nm_ar_{nm}"], out=OUT / f"nm_ar_{nm}",
               timeout_s=6, group="name"))
    A(Cell("name-ar-t-raw", ["arecord", "-D", "null", "-t", "raw", "-f", "S16_LE",
                             "-r", "48000", "-c", "1", "-d", "1",
                             OUT / "nm_ar_traw.wav"],
           out=OUT / "nm_ar_traw.wav", timeout_s=6, group="name"))
    for nm in names:
        A(Cell(f"name-ff-{nm.replace('.', '_')}",
               ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
                "-f", "pulse", "-i", SRC, "-t", "1", "-y", OUT / f"nm_ff_{nm}"],
               out=OUT / f"nm_ff_{nm}", timeout_s=10, group="name"))
    A(Cell("name-ff-explicit-f", ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel",
                                  "error", "-f", "pulse", "-i", SRC, "-t", "1",
                                  "-f", "wav", "-y", OUT / "nm_ff_explicit.raw"],
           out=OUT / "nm_ff_explicit.raw", timeout_s=10, group="name"))
    for nm in names:
        A(Cell(f"name-pa-{nm.replace('.', '_')}",
               ["parecord", "-d", "@DEFAULT_SOURCE@", "--file-format=wav",
                "--rate=48000", "--channels=2", OUT / f"nm_pa_{nm}"],
               out=OUT / f"nm_pa_{nm}", timeout_s=3, group="name"))
    return cells


# ---------------------------------------------------------------- fifo / sink edges

def fifo_pre(name, mode="none", read_bytes=4096):
    """Create a fresh fifo and (optionally) start a reader child thread.

    mode: "none"   -> no reader at all (open(O_WRONLY) has no partner)
          "early"  -> reader drains `read_bytes` then closes and exits
          "drain"  -> reader drains to EOF
    """
    path = HERE / "rt" / name
    if path.exists():
        path.unlink()
    os.mkfifo(path)
    stats = {}

    def start():
        def reader():
            try:
                with open(path, "rb") as f:
                    if mode == "early":
                        data = f.read(read_bytes)
                        stats["bytes"] = len(data)
                        stats["eof"] = False
                        return
                    total = 0
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        total += len(chunk)
                    stats["bytes"] = total
                    stats["eof"] = True
            except OSError as exc:
                stats["error"] = str(exc)
        th = threading.Thread(target=reader, daemon=True)
        th.start()
        return th
    return path, start, stats


def fifo_cells():
    cells = []
    A = cells.append
    consumers = [
        ("pw", ["pw-record", "--target", SRC]),
        ("pa", ["parecord", "-d", "@DEFAULT_SOURCE@", "--file-format=wav",
                "--rate=48000", "--channels=2"]),
        ("ar", ["arecord", "-D", "null", "-f", "S16_LE", "-r", "48000", "-c", "1",
                "-d", "300"]),
        ("ff-pulse", ["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
                      "-f", "pulse", "-i", SRC, "-y"]),
    ]
    for tag, argv in consumers:
        for mode, tmo in (("none", 4), ("early", 5), ("drain", 5)):
            p, start, stats = fifo_pre(f"{mode}-{tag}.fifo", mode=mode)
            A(Cell(f"fifo-{mode}-{tag}", list(argv) + [p], out=p, timeout_s=tmo,
                   group="fifo", pre=(start if mode != "none" else None),
                   post=lambda r, s=stats: r.update(reader=dict(s))))
    # /dev/full and /dev/null write classes
    for tag, argv in consumers:
        A(Cell(f"sink-devfull-{tag}", list(argv) + ["/dev/full"], timeout_s=4,
               group="sink"))
        A(Cell(f"sink-devnull-{tag}", list(argv) + ["/dev/null"], timeout_s=4,
               group="sink"))
    A(Cell("sink-dir-as-target", ["arecord", "-D", "null", "-f", "S16_LE",
                                  "-r", "48000", "-c", "1", "-d", "1", OUT],
           timeout_s=4, group="sink"))
    A(Cell("sink-unwritable", ["arecord", "-D", "null", "-f", "S16_LE", "-r",
                               "48000", "-c", "1", "-d", "1",
                               "/proc/self/nope.wav"], timeout_s=4, group="sink"))
    return cells


# ---------------------------------------------------------------- load replays

def load_cells(n=8, cpu_load=0):
    """Load replay targets: only non-device-contending consumers (PipeWire
    multiplexes streams on one source; `-D null` is software-only)."""
    targets = [t for t in SEVER_TARGETS if t[0] != "ar-hw" and t[0] != "ff-alsa-hw"]
    cells = []
    for i in range(n):
        tag, argv, out = targets[i % len(targets)]
        cells.append(Cell(f"load{n}-{tag}-{i}",
                          list(argv) + [OUT / f"load_{tag}_{i}.wav"],
                          out=OUT / f"load_{tag}_{i}.wav",
                          ladder=(1.5, 3.5, 5.5), timeout_s=8, group="load"))
    return cells


def loadcpu_cells(n=4, hogs=16):
    cells = []
    targets = [t for t in SEVER_TARGETS if t[0] != "ar-hw" and t[0] != "ff-alsa-hw"]
    for i in range(n):
        tag, argv, out = targets[i % len(targets)]
        cells.append(Cell(f"loadcpu{hogs}-{tag}-{i}",
                          list(argv) + [OUT / f"loadcpu_{tag}_{i}.wav"],
                          out=OUT / f"loadcpu_{tag}_{i}.wav",
                          ladder=(1.5, 3.5, 5.5), timeout_s=8, group="loadcpu",
                          pre=(lambda k=hogs: CPU_HOGS.append(cpu_hogs(k))) if i == 0
                          else None))
    return cells


def probe2_cells():
    """Pin the residual unknowns: pw-record rc=1 on success, sink-node id
    target, parecord wall-vs-audio ratio (dead start / pacing)."""
    cells = []
    A = cells.append
    A(Cell("pin-pw-rc-src-v", ["pw-record", "-v", "--target", SRC, "-n", "48000",
                               OUT / "pin_pw_v.wav"], out=OUT / "pin_pw_v.wav",
           timeout_s=6, group="probe2"))
    A(Cell("pin-pw-rc-src-rep", ["pw-record", "--target", SRC, "-n", "48000",
                                 OUT / "pin_pw_rep.wav"], out=OUT / "pin_pw_rep.wav",
           timeout_s=6, group="probe2"))
    A(Cell("pin-pw-sink-nodeid", ["pw-record", "--target", "46", "-n", "48000",
                                  OUT / "pin_pw_id46.wav"], out=OUT / "pin_pw_id46.wav",
           timeout_s=6, group="probe2"))
    A(Cell("pin-pw-src-nodeid", ["pw-record", "--target", "55", "-n", "48000",
                                 OUT / "pin_pw_id55.wav"], out=OUT / "pin_pw_id55.wav",
           timeout_s=6, group="probe2"))
    A(Cell("pin-pw-8s-wall", ["pw-record", "--target", SRC, OUT / "pin_pw_8s.wav"],
           out=OUT / "pin_pw_8s.wav", timeout_s=8, group="probe2"))
    A(Cell("pin-pa-8s-wall", ["parecord", "-d", "@DEFAULT_SOURCE@",
                              "--file-format=wav", "--rate=48000", "--channels=2",
                              OUT / "pin_pa_8s.wav"], out=OUT / "pin_pa_8s.wav",
           timeout_s=8, group="probe2"))
    A(Cell("pin-pa-mon-8s-wall", ["parecord", "-d", "@DEFAULT_MONITOR@",
                                  "--file-format=wav", "--rate=48000", "--channels=2",
                                  OUT / "pin_pa_mon_8s.wav"],
           out=OUT / "pin_pa_mon_8s.wav", timeout_s=8, group="probe2"))
    A(Cell("pin-pa-lat10-8s", ["parecord", "-d", "@DEFAULT_SOURCE@",
                               "--file-format=wav", "--rate=48000", "--channels=2",
                               "--latency-msec=10", OUT / "pin_pa_lat10.wav"],
           out=OUT / "pin_pa_lat10.wav", timeout_s=8, group="probe2"))
    A(Cell("pin-pa-native-8s", ["parecord", "-d", "@DEFAULT_SOURCE@",
                                "--file-format=wav", "--fix-rate", "--fix-channels",
                                OUT / "pin_pa_fix.wav"], out=OUT / "pin_pa_fix.wav",
           timeout_s=8, group="probe2"))
    A(Cell("pin-ff-pulse-8s-wall", ["ffmpeg", "-hide_banner", "-nostdin",
                                    "-loglevel", "error", "-f", "pulse", "-i", SRC,
                                    "-y", OUT / "pin_ff_8s.wav"],
           out=OUT / "pin_ff_8s.wav", timeout_s=8, group="probe2"))
    A(Cell("pin-ff-alsa-null-8s-wall", ["ffmpeg", "-hide_banner", "-nostdin",
                                        "-loglevel", "error", "-f", "alsa", "-i", "null",
                                        "-y", OUT / "pin_ff_n_8s.wav"],
           out=OUT / "pin_ff_n_8s.wav", timeout_s=8, group="probe2"))
    A(Cell("pin-ar-null-8s-wall", ["arecord", "-D", "null", "-f", "S16_LE",
                                   "-r", "48000", "-c", "1", "-d", "8",
                                   OUT / "pin_ar_8s.wav"],
           out=OUT / "pin_ar_8s.wav", timeout_s=8, group="probe2"))
    return cells


def cpu_hogs(k=16):
    procs = []
    for _ in range(k):
        procs.append(subprocess.Popen(
            [sys.executable, "-c", "while True: pass"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    return procs


# ---------------------------------------------------------------- roundtrip gate

def roundtrip_cells():
    cells = []
    member = ROOT / "corpus" / "artifacts" / "stem_sections.wav"
    if not member.exists():
        member = ROOT / "corpus" / "artifacts" / "ui.wav"
    if not member.exists():
        return cells

    def play():
        subprocess.Popen(["pw-play", str(member)], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        time.sleep(0.8)          # let the SUSPENDED sink resume before capturing
    # (1) monitor capture with nothing playing (silence control)
    cells.append(Cell("rt-silent-mon", ["parec", "-d", "@DEFAULT_MONITOR@",
                                        "--file-format=wav", "--rate=48000",
                                        "--channels=2", OUT / "rt_silent.wav"],
                      out=OUT / "rt_silent.wav", timeout_s=2.5, group="rt"))
    # (2) monitor capture while a member plays through the default sink
    cells.append(Cell("rt-playing-mon", ["parec", "-d", "@DEFAULT_MONITOR@",
                                         "--file-format=wav", "--rate=48000",
                                         "--channels=2", OUT / "rt_playing.wav"],
                      out=OUT / "rt_playing.wav", timeout_s=2.5, group="rt",
                      pre=play))
    # (3) same, through the native leg (pw-record) — monitor target expected to fail
    cells.append(Cell("rt-playing-pwrec", ["pw-record", "--target",
                                           MON, OUT / "rt_playing_pw.wav"],
                      out=OUT / "rt_playing_pw.wav", timeout_s=2.5, group="rt",
                      pre=play))
    return cells


# ---------------------------------------------------------------- driver

def declaration_cells():
    """Resolve the arecord TERM-header conflict: does the pre-declared data
    size exist only when a *duration/sample bound* is given?"""
    cells = []
    base = ["arecord", "-D", "hw:0,0", "-f", "S16_LE", "-r", "48000", "-c", "2"]
    for tag, extra in (("nod", []), ("d300", ["-d", "300"]),
                       ("d30", ["-d", "30"]), ("s14400000", ["-s", "14400000"])):
        p = OUT / f"decl_ar_{tag}.wav"
        cells.append(Cell(f"decl-ar-{tag}", base + extra + [p], out=p,
                          ladder=(1.5, 3.5, 5.5), timeout_s=8,
                          group="decl"))
    return cells


GROUPS = {
    "gates": gate_cells,
    "bounded": bounded_cells,
    "probe2": probe2_cells,
    "decl": declaration_cells,
    "sever": lambda: sever_cells("mid"),
    "sever-early": lambda: sever_cells("early"),
    "name": name_cells,
    "fifo": fifo_cells,
    "load": lambda: load_cells(8),
    "loadcpu": lambda: loadcpu_cells(4),
    "rt": roundtrip_cells,
}

CPU_HOGS = []


def env_receipt():
    lines = []
    for cmd in (["uname", "-a"], ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                ["arecord", "--version"], ["ffmpeg", "-version"],
                ["pactl", "--version"], ["pw-record", "--version"],
                ["parecord", "--version"], ["sox", "--version"]):
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=10)
            lines.append(f"$ {' '.join(cmd)}\n"
                         + p.stdout.decode("utf-8", "replace").strip()
                         + p.stderr.decode("utf-8", "replace").strip())
        except (OSError, subprocess.TimeoutExpired) as exc:
            lines.append(f"$ {' '.join(cmd)}\n!! {exc}")
    for cmd in (["pactl", "list", "sources", "short"], ["pactl", "list", "sinks", "short"],
                ["arecord", "-l"], ["arecord", "-L"], ["pw-link", "-o"],
                ["ffmpeg", "-hide_banner", "-devices"]):
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=10)
            lines.append(f"$ {' '.join(cmd)}\n"
                         + p.stdout.decode("utf-8", "replace").strip()
                         + p.stderr.decode("utf-8", "replace").strip())
        except (OSError, subprocess.TimeoutExpired) as exc:
            lines.append(f"$ {' '.join(cmd)}\n!! {exc}")
    fixture = ROOT / "corpus" / "fixtures" / "measure_audio.py"
    lines.append(f"fixture {fixture} sha256={sha256(fixture)}")
    nodes = pw_nodes()
    lines.append("$ pw-dump node inventory (id | media.class | node.name)\n"
                 + "\n".join(f"{n['id']:>4} | {n['class']} | {n['name']} | {n['desc']}"
                             for n in nodes))
    try:
        p = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                           capture_output=True, timeout=10)
        lines.append("HEAD " + p.stdout.decode().strip())
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "\n\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("group", nargs="+", choices=list(GROUPS) + ["all"])
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--run", default=None, help="run dir suffix")
    args = ap.parse_args()

    groups = list(GROUPS) if "all" in args.group else args.group
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = HERE / "runs" / f"{stamp}-boundary-r76{'-' + args.run if args.run else ''}"
    (run_dir / "cells").mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    RT.mkdir(exist_ok=True)
    (run_dir / "env.txt").write_text(env_receipt())

    all_recs = []
    for g in groups:
        cells = GROUPS[g]()
        seq = g in ("sever", "sever-early", "fifo", "rt")  # device-contending
        conc = 1 if seq else max(1, args.concurrency)
        print(f"[{g}] {len(cells)} cells, concurrency={conc}", flush=True)
        t0 = time.monotonic()
        if conc == 1:
            recs = [c.run(run_dir / "cells") for c in cells]
        else:
            recs = [None] * len(cells)
            lock = threading.Lock()
            idx = iter(range(len(cells)))

            def worker():
                while True:
                    with lock:
                        try:
                            i = next(idx)
                        except StopIteration:
                            return
                    recs[i] = cells[i].run(run_dir / "cells")
            ths = [threading.Thread(target=worker) for _ in range(conc)]
            [t.start() for t in ths]
            [t.join() for t in ths]
        for r in recs:
            all_recs.append(r)
        print(f"[{g}] done in {time.monotonic() - t0:.1f}s", flush=True)
        (run_dir / f"{g}-measurements.json").write_text(
            json.dumps(recs, indent=1, sort_keys=True) + "\n")
    (run_dir / "measurements.json").write_text(
        json.dumps(all_recs, indent=1, sort_keys=True) + "\n")
    for group in CPU_HOGS:
        for p in group:
            p.kill()
    print(f"run dir: {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
