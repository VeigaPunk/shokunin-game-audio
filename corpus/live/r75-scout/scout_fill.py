#!/usr/bin/env python3
"""r75-scout gap-fill: name-vs-transport lattice, aplay format selection,
writerless/silent/empty fifo hang classes with a TERM ladder, ffplay seek
cells, viability gates.

Fills the holes left by the killed prior generation (scratch kept and
reused where sound). Every fifo/subprocess arm is bounded and group-killed;
rc alone is never recorded as a verdict (stderr / spec line / fd table are).
Writes only under corpus/live/r75-scout/.
"""
import json
import os
import re
import signal
import subprocess
import threading
import time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = REPO / "corpus/live/r75-scout"
RUNS = OUT / "runs"
SCRATCH = OUT / "scratch"
for d in (RUNS, SCRATCH):
    d.mkdir(parents=True, exist_ok=True)

ACT = REPO / "corpus/live/round-66/pair_dec_act.wav"      # RIFF, lavf=wav
HCOM = REPO / "corpus/live/round-66/pair_dec_hcom.wav"    # RIFF, lavf=hcom(100)
NOMAGIC = REPO / "corpus/live/round-69/extsuffix_nomatch.snd"  # 512 B, no magic
STEM = REPO / "corpus/artifacts/stem_sections.wav"

FFPLAY_ENV = {**os.environ, "SDL_AUDIODRIVER": "dummy"}


# ---------------------------------------------------------------- primitives
def run_bounded(argv, timeout=8.0, env=None, stdin_bytes=None, cwd=None):
    """Run argv with a hard bound; on timeout kill the whole group (KILL)."""
    t0 = time.monotonic()
    p = subprocess.Popen(argv, stdin=subprocess.PIPE if stdin_bytes is not None
                         else subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env or os.environ.copy(), cwd=cwd,
                         start_new_session=True)
    try:
        out, err = p.communicate(input=stdin_bytes, timeout=timeout)
        rc, hit = p.returncode, False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
        rc, hit = None, True
    return {"cmd": " ".join(argv), "exit_code": rc, "timeout_hit": hit,
            "wall_s": round(time.monotonic() - t0, 3),
            "stdout_tail": out.decode(errors="replace")[-400:],
            "stderr_tail": err.decode(errors="replace")[-500:]}


def with_writer(mode, argv, timeout=8.0, env=None, data=b"", fname="leg.wav"):
    """mode: 'nowriter' (no writer at all) | 'silent' (writer opens, holds,
    writes nothing) | 'empty' (writer opens, writes 0 B, closes) | 'data'
    (write, then HOLD the fd open -> no EOF) | 'data-close' (write, close
    immediately -> EOF, the r74 fifo shape)."""
    tmp = Path(SCRATCH) / f"fill-{abs(hash((mode, fname, time.time()))) % 10**8}"
    tmp.mkdir(parents=True, exist_ok=True)
    fifo = tmp / fname
    os.mkfifo(fifo)
    stop = threading.Event()

    def feed():
        try:
            fh = open(fifo, "wb")            # blocks until a reader appears
        except OSError:
            return
        try:
            if mode in ("data", "data-close"):
                fh.write(data)
                fh.flush()
            if mode in ("data", "silent"):
                stop.wait(timeout + 2)       # hold the fd open
        finally:
            fh.close()

    th = threading.Thread(target=feed, daemon=True)
    started = mode != "nowriter"
    if started:
        th.start()
    rec = run_bounded([*argv, str(fifo)], timeout=timeout, env=env)
    rec["fifo_mode"] = mode
    rec["fifo_name"] = fname
    stop.set()
    if started:
        th.join(timeout=2)
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    return rec


def proc_probe(p, label):
    """wchan / state / open fds of a live pid (the open-block witness)."""
    rec = {"label": label}
    try:
        rec["wchan"] = Path(f"/proc/{p.pid}/wchan").read_text().strip()
    except OSError:
        rec["wchan"] = None
    try:
        rec["state"] = Path(f"/proc/{p.pid}/stat").read_text().split()[2]
    except OSError:
        rec["state"] = None
    try:
        rec["fds"] = sorted(os.readlink(f"/proc/{p.pid}/fd/{fd}")
                            for fd in os.listdir(f"/proc/{p.pid}/fd"))
    except OSError:
        rec["fds"] = None
    return rec


def term_ladder(p, first_delay=1.2, step=0.8):
    """TERM, poll, TERM again, poll, then SIGKILL the group. Records which
    TERM (if any) was honoured -- the in_abort/SIG_DFL discriminator."""
    time.sleep(first_delay)
    rec = {"poll_after_spawn": p.poll()}
    if p.poll() is None:
        rec["probe_before_term"] = proc_probe(p, "before-term")
        p.send_signal(signal.SIGTERM)
        time.sleep(step)
        rec["alive_after_term1"] = p.poll() is None
        rec["rc_after_term1"] = p.poll()
        if rec["alive_after_term1"]:
            p.send_signal(signal.SIGTERM)
            time.sleep(step)
            rec["alive_after_term2"] = p.poll() is None
            rec["rc_after_term2"] = p.poll()
        if p.poll() is None:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    try:
        out, err = p.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
    rec["exit_code"] = p.returncode
    rec["stderr_tail"] = err.decode(errors="replace")[-300:]
    return rec


def hang_class(name, argv, env=None, mode="nowriter", data=b""):
    """Spawn on a fifo (no writer at all, or a writer that opens and holds the
    fd without writing), then run the TERM ladder. `mode` selects the class:
    'nowriter' -> the block (if any) is in open(2); 'silent' -> open succeeded,
    so any block is in read(2). The fd table before TERM tells them apart.
    With `data` the same writer writes the member first and then holds the fd
    open (no EOF) -- the writer-hold class."""
    fifo = Path(SCRATCH) / f"hang-{name}-{mode}.fifo"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    stop = threading.Event()

    def feed():
        try:
            fh = open(fifo, "wb")
        except OSError:
            return
        try:
            if data:
                fh.write(data)
                fh.flush()
            stop.wait(30)
        finally:
            fh.close()

    th = threading.Thread(target=feed, daemon=True)
    started = mode != "nowriter"
    if started:
        th.start()
    p = subprocess.Popen([*argv, str(fifo)], stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env or os.environ.copy(), start_new_session=True)
    rec = term_ladder(p)
    stop.set()
    if started:
        th.join(timeout=2)
    fifo.unlink()
    rec["fifo_mode"] = mode
    return rec


def save(batch, obj):
    p = RUNS / f"scout-fill-{batch}.json"
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(f"[saved] {p.relative_to(REPO)}", flush=True)


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ batch A/B
NAMES = [".wav", ".snd", ".bin", ".au"]
MEMBERS = {"nomagic": NOMAGIC, "hcom": HCOM, "act": ACT}


def batch_name_lattice():
    """Identical bytes, name x transport x client. The brief's core cell:
    does the .snd acceptance belong to libsndfile, to the client, or to the
    transport?"""
    out = {}
    for tag, path in MEMBERS.items():
        data = path.read_bytes()
        for nm in NAMES:
            leg = f"{tag}{nm}"
            # -- libsndfile itself (no daemon, bare parse witness)
            f = SCRATCH / f"nl-{leg}"
            f.write_bytes(data)
            r = run_bounded(["sndfile-info", str(f)], timeout=6)
            r["sndfile_format_line"] = next(
                (l.strip() for l in r["stdout_tail"].splitlines()
                 if "Format" in l or "Sample Rate" in l or "not recognised" in l
                 or "Error" in l), None)
            out[f"sndfile-info|file|{leg}"] = r
            f.unlink()
            # -- paplay --verbose (spec line = the decoded-spec witness)
            f = SCRATCH / f"nl-{leg}"
            f.write_bytes(data)
            r = run_bounded(["paplay", "--verbose", str(f)], timeout=8)
            r["paplay_spec"] = next(
                (l.strip() for l in r["stderr_tail"].splitlines()
                 if "sample specification" in l or "Failed" in l
                 or "Connection" in l), None)
            out[f"paplay|file|{leg}"] = r
            f.unlink()
            # -- pw-cat -p (the r73/r74 fork client)
            f = SCRATCH / f"nl-{leg}"
            f.write_bytes(data)
            r = run_bounded(["pw-cat", "-p", str(f)], timeout=8)
            out[f"pw-cat|file|{leg}"] = r
            f.unlink()
    # fifo transport for the two clients + libsndfile on the key names
    for tag in ("nomagic", "hcom"):
        data = MEMBERS[tag].read_bytes()
        for nm in (".wav", ".snd"):
            out[f"paplay|fifo|{tag}{nm}"] = with_writer(
                "data", ["paplay", "--verbose"], data=data, fname=f"leg{nm}")
            out[f"pw-cat|fifo|{tag}{nm}"] = with_writer(
                "data", ["pw-cat", "-p"], data=data, fname=f"leg{nm}")
            out[f"sndfile-info|fifo|{tag}{nm}"] = with_writer(
                "data", ["sndfile-info"], data=data, fname=f"leg{nm}")
    # stdin / rfd transport (no name at all)
    for tag in ("nomagic", "hcom"):
        data = MEMBERS[tag].read_bytes()
        out[f"paplay|stdin|{tag}"] = run_bounded(
            ["paplay", "--verbose", "/dev/stdin"], timeout=8, stdin_bytes=data)
        out[f"pw-cat|stdin|{tag}"] = run_bounded(
            ["pw-cat", "-p", "-"], timeout=8, stdin_bytes=data)
    save("name-lattice", out)
    return out


# -------------------------------------------------------------------- batch C
def batch_aplay():
    """aplay's format selection: content header vs name vs raw fallback.
    `-D null` consumes instantly (measured: no pacing), so it is the cheap
    matrix device; the `Playing WAVE|raw data` stderr line is the witness."""
    out = {}
    extra = {"empty": b"", "trunc": ACT.read_bytes()[:64],
             "junk1": b"\x00", "junk512": NOMAGIC.read_bytes()}
    members = {**MEMBERS, **extra}
    for tag, path in members.items():
        data = path if isinstance(path, bytes) else path.read_bytes()
        for nm in NAMES + [".raw"]:
            f = SCRATCH / f"ap-{tag}{nm}"
            f.write_bytes(data)
            r = run_bounded(["aplay", "-D", "null", str(f)], timeout=6)
            r["playing_line"] = next(
                (l.strip() for l in r["stderr_tail"].splitlines()
                 if l.startswith("Playing") or "read_header" in l
                 or "aplay:" in l), None)
            out[f"aplay-null|file|{tag}{nm}"] = r
            f.unlink()
    # stdin arm (aplay supports '-' as stdin) + quiet-flag witness erasure
    out["aplay-null|stdin|nomagic"] = run_bounded(
        ["aplay", "-D", "null", "-"], timeout=6,
        stdin_bytes=NOMAGIC.read_bytes())
    out["aplay-null|stdin|nomagic-q"] = run_bounded(
        ["aplay", "-D", "null", "-q", "-"], timeout=6,
        stdin_bytes=NOMAGIC.read_bytes())
    out["aplay-null|stdin|act-q"] = run_bounded(
        ["aplay", "-D", "null", "-q", "-"], timeout=6,
        stdin_bytes=ACT.read_bytes())
    # writerless / silent / empty fifo on the null device
    out["aplay-null|fifo|nowriter"] = with_writer(
        "nowriter", ["aplay", "-D", "null"], timeout=4)
    out["aplay-null|fifo|silent"] = with_writer(
        "silent", ["aplay", "-D", "null"], timeout=4)
    out["aplay-null|fifo|empty"] = with_writer(
        "empty", ["aplay", "-D", "null"], timeout=4)
    save("aplay", out)
    return out


# -------------------------------------------------------------------- batch D
def batch_hangs():
    """Hang classes for the three new consumers: writerless (open block),
    silent writer (open succeeds, read blocks), writer-hold (member written,
    fd held -> no EOF). Each with the TERM/TERM/KILL ladder + fd table."""
    out = {}
    cons = {"paplay": ["paplay"],
            "aplay": ["aplay", "-D", "null"],
            "ffplay": ["ffplay", "-nodisp", "-autoexit", "-loglevel", "info"]}
    act = ACT.read_bytes()
    for name, argv in cons.items():
        env = FFPLAY_ENV if name == "ffplay" else None
        for mode, data in (("nowriter", b""), ("silent", b""),
                           ("data-hold", act)):
            key = f"{name}|{mode}"
            log(f"[hang] {key}")
            out[key] = hang_class(name, argv, env=env, mode=mode, data=data)
            log(f"[hang] {key} -> {json.dumps(out[key])}")
            save("hangs", out)
    return out


# -------------------------------------------------------------------- batch E
def ffplay_seek_cell(label, argv, timeout=20, env=None, stdin_bytes=None):
    r = run_bounded(argv, timeout=timeout, env=env or FFPLAY_ENV,
                    stdin_bytes=stdin_bytes)
    err = r["stderr_tail"] + r["stdout_tail"]
    r["seeks_stat"] = re.findall(r"Statistics: (\d+) bytes read, (\d+) seeks", err)
    r["find_stream_info"] = re.findall(
        r"avformat_find_stream_info\(\) pos: (\d+) bytes read:(\d+) seeks:(\d+)"
        r" nb_streams:(\d+)\)", err)
    r["could_not_seek"] = "could not seek" in err
    r["input_line"] = next((l.strip() for l in err.splitlines()
                            if l.strip().startswith("Input #")), None)
    r["cell"] = label
    return r


def batch_ffplay():
    out = {}
    for tag, path in (("hcom", HCOM), ("act", ACT)):
        out[f"ffplay|file|{tag}"] = ffplay_seek_cell(
            f"file|{tag}", ["ffplay", "-nodisp", "-autoexit", "-loglevel",
                            "debug", str(path)])
        out[f"ffplay|fifo|{tag}"] = with_writer(
            "data", ["ffplay", "-nodisp", "-autoexit", "-loglevel", "debug"],
            data=path.read_bytes(), timeout=10, env=FFPLAY_ENV)
        out[f"ffplay|stdin|{tag}"] = ffplay_seek_cell(
            f"stdin|{tag}", ["ffplay", "-nodisp", "-autoexit", "-loglevel",
                             "debug", "-i", "-"], stdin_bytes=path.read_bytes())
    # -ss cell: file vs non-seekable stdin vs named fifo (+ -ss 0 controls)
    for ss in ("2", "0"):
        out[f"ffplay|ss{ss}|file"] = ffplay_seek_cell(
            f"ss{ss}|file", ["ffplay", "-nodisp", "-autoexit", "-ss", ss,
                             "-loglevel", "debug", str(STEM)], timeout=20)
        out[f"ffplay|ss{ss}|stdin"] = ffplay_seek_cell(
            f"ss{ss}|stdin", ["ffplay", "-nodisp", "-autoexit", "-ss", ss,
                              "-loglevel", "debug", "-i", "-"],
            stdin_bytes=STEM.read_bytes(), timeout=20)
        out[f"ffplay|ss{ss}|fifo"] = with_writer(
            "data", ["ffplay", "-nodisp", "-autoexit", "-ss", ss,
                     "-loglevel", "debug"], data=STEM.read_bytes(),
            timeout=20, env=FFPLAY_ENV)
    save("ffplay", out)
    return out


# -------------------------------------------------------------------- batch F
def batch_gates():
    out = {}
    act = ACT.read_bytes()
    sil = (SCRATCH / "sil48s.wav")
    if not sil.exists():
        run_bounded(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                     "anullsrc=r=48000:cl=stereo", "-t", "0.3",
                     str(sil), "-y"], timeout=20)
    # aplay device ladder: can the real hardware be driven at all?
    # NOTE: `-t` in aplay is --file-type (not duration); the duration flag is
    # `-d`. An earlier run of this batch passed `-t 0.05` and every leg died
    # with "unrecognized file format 0.05" -- a harness artifact, discarded.
    for dev in ("null", "default", "pipewire", "plughw:0,0", "hw:0,0",
                "hw:0,3", "hw:1,3", "sysdefault"):
        out[f"aplay|dev={dev}|act"] = run_bounded(
            ["aplay", "-D", dev, "-d", "0.05", str(ACT)], timeout=8)
    out["aplay|dev=plughw:0,0|stereo48k"] = run_bounded(
        ["aplay", "-D", "plughw:0,0", "-d", "0.05", str(sil)], timeout=8)
    out["aplay|dev=hw:0,0|stereo48k"] = run_bounded(
        ["aplay", "-D", "hw:0,0", "-d", "0.05", str(sil)], timeout=8)
    out["aplay|dev=null|hcom-member"] = run_bounded(
        ["aplay", "-D", "null", str(HCOM)], timeout=8)
    out["aplay|dev=null|nodur-noarg"] = run_bounded(
        ["aplay", "-D", "null"], timeout=8, stdin_bytes=b"")
    # paplay gates
    out["paplay|PULSE_SERVER=bogus"] = run_bounded(
        ["paplay", str(ACT)], timeout=8,
        env={**os.environ, "PULSE_SERVER": "unix:/nonexistent-r75"})
    out["paplay|device=bogus"] = run_bounded(
        ["paplay", "--device=bogus-r75", str(ACT)], timeout=8)
    out["paplay|device=bogus+fifo"] = with_writer(
        "data", ["paplay", "--device=bogus-r75"], data=act, timeout=8)
    # ffplay SDL gates
    for drv in ("dummy", "bogus", "default", "pulse", "alsa", "pipewire",
                "pipewire-pulse"):
        out[f"ffplay|SDL_AUDIODRIVER={drv}"] = run_bounded(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "info", str(ACT)],
            timeout=8, env={**os.environ, "SDL_AUDIODRIVER": drv})
        err = (out[f"ffplay|SDL_AUDIODRIVER={drv}"]["stderr_tail"]
               + out[f"ffplay|SDL_AUDIODRIVER={drv}"]["stdout_tail"])
        out[f"ffplay|SDL_AUDIODRIVER={drv}"]["sdl_line"] = next(
            (l.strip() for l in err.splitlines()
             if "SDL" in l or "Audio target" in l or "could not" in l
             or "Could not" in l), None)
    out["ffplay|SDL_AUDIODRIVER=dummy|stem"] = run_bounded(
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "info", str(STEM)],
        timeout=20, env=FFPLAY_ENV)
    out["ffplay|SDL_AUDIODRIVER=bogus|stem"] = run_bounded(
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "info", str(STEM)],
        timeout=20, env={**os.environ, "SDL_AUDIODRIVER": "bogus"})
    # ffplay hang class on a *seekable-named* device: /dev/null (no block)
    out["ffplay|dev-null"] = run_bounded(
        ["ffplay", "-nodisp", "-autoexit", str(Path("/dev/null"))], timeout=8,
        env=FFPLAY_ENV)
    save("gates", out)
    return out


# ------------------------------------------------- batch G: closing writer
def batch_fifo_close():
    """The r74 fifo shape: writer writes the member and CLOSES (EOF present).
    This is the transport arm the author's receipts will use; the writer-hold
    class lives in the hangs batch."""
    out = {}
    cons = {
        "paplay": ["paplay", "--verbose"],
        "pw-cat": ["pw-cat", "-p"],
        "aplay": ["aplay", "-D", "null"],
        "ffplay": ["ffplay", "-nodisp", "-autoexit", "-loglevel", "info"],
        "sndfile-info": ["sndfile-info"],
    }
    members = {"nomagic.snd": NOMAGIC.read_bytes(), "nomagic.wav": NOMAGIC.read_bytes(),
               "act.wav": ACT.read_bytes(), "hcom.wav": HCOM.read_bytes(),
               "empty.wav": b""}
    for cname, argv in cons.items():
        env = FFPLAY_ENV if cname == "ffplay" else None
        for mname, data in members.items():
            r = with_writer("data-close", argv, data=data, timeout=8,
                            env=env, fname=mname)
            err = r["stderr_tail"] + r["stdout_tail"]
            r["playing_line"] = next(
                (l.strip() for l in err.splitlines()
                 if l.startswith("Playing") or "Failed" in l or "sndfile" in l
                 or "sample specification" in l or "Format" in l
                 or "Input #" in l), None)
            out[f"{cname}|fifo-close|{mname}"] = r
            log(f"[close] {cname}|{mname} rc={r['exit_code']} "
                f"to={r['timeout_hit']} wall={r['wall_s']} | {r['playing_line']}")
        save("fifo-close", out)
    # ffplay -ss on a closing fifo (the seek cell's transport arm)
    r = with_writer("data-close",
                    ["ffplay", "-nodisp", "-autoexit", "-ss", "2",
                     "-loglevel", "debug"], data=STEM.read_bytes(),
                    timeout=20, env=FFPLAY_ENV)
    err = r["stderr_tail"]
    r["seeks_stat"] = re.findall(r"Statistics: (\d+) bytes read, (\d+) seeks", err)
    r["could_not_seek"] = "could not seek" in err
    out["ffplay|fifo-close|ss2|stem"] = r
    save("fifo-close", out)
    return out


# ------------------------------------------------- batch H: ffplay position
def ffplay_position(label, argv, timeout=20, env=None, stdin_bytes=None):
    """ffplay's own playback witness: the status-line position token
    (`  3.68 M-A:`). rc alone cannot separate 'played' from 'did nothing'."""
    r = run_bounded(argv, timeout=timeout, env=env or FFPLAY_ENV,
                    stdin_bytes=stdin_bytes)
    err = r["stderr_tail"] + r["stdout_tail"]
    r["positions"] = re.findall(r"([\d.]+|nan)\s+M-A:", err)
    r["n_status"] = len(r["positions"])
    r["last_position"] = r["positions"][-1] if r["positions"] else None
    r["could_not_seek"] = "could not seek" in err
    r["seeks_stat"] = re.findall(r"Statistics: (\d+) bytes read, (\d+) seeks", err)
    r["cell"] = label
    return r


def batch_ffplay_position():
    """Re-run the -ss pair capturing the FULL stderr (the tail-only capture
    loses the status lines), file vs pipe, -ss 2 vs -ss 0."""
    out = {}
    for ss in ("0", "2"):
        for transport in ("file", "stdin", "pipe"):
            if transport == "file":
                r = ffplay_position(
                    f"ss{ss}|file",
                    ["ffplay", "-nodisp", "-autoexit", "-ss", ss, "-loglevel",
                     "info", str(STEM)], timeout=20)
            elif transport == "stdin":
                r = ffplay_position(
                    f"ss{ss}|stdin",
                    ["ffplay", "-nodisp", "-autoexit", "-ss", ss, "-loglevel",
                     "info", "-i", "-"], stdin_bytes=STEM.read_bytes(),
                    timeout=20)
            else:  # pipe via cat: ffplay reads a pipe it cannot seek
                r = run_bounded(
                    ["bash", "-c",
                     f"cat {STEM} | timeout -s KILL 20 ffplay -nodisp -autoexit"
                     f" -ss {ss} -loglevel info -i -"],
                    timeout=25, env=FFPLAY_ENV)
                err = r["stderr_tail"] + r["stdout_tail"]
                r["positions"] = re.findall(r"([\d.]+|nan)\s+M-A:", err)
                r["last_position"] = r["positions"][-1] if r["positions"] else None
                r["n_status"] = len(r["positions"])
                r["could_not_seek"] = "could not seek" in err
                r["cell"] = f"ss{ss}|pipe(cat)"
            out[f"ffplay-pos|{r['cell']}"] = r
            log(f"[pos] {r['cell']} rc={r['exit_code']} wall={r['wall_s']} "
                f"last_pos={r['last_position']} n_status={r['n_status']}")
    save("ffplay-position", out)
    return out


# ------------------------------------------------- batch I: device ladder
def batch_devices():
    """aplay device viability without the broken `-d 0.05` argument (aplay's
    -d wants a time suffix on this build: `invalid duration argument`)."""
    out = {}
    for dev in ("null", "default", "pipewire", "sysdefault", "plughw:0,0",
                "hw:0,0", "hw:0,3", "hw:1,3", "hw:2,3"):
        out[f"aplay|dev={dev}|act"] = run_bounded(
            ["aplay", "-D", dev, str(ACT)], timeout=8)
    out["aplay|dev=pipewire|stem"] = run_bounded(
        ["aplay", "-D", "pipewire", str(STEM)], timeout=20)
    out["aplay|dev=plughw:0,0|stem"] = run_bounded(
        ["aplay", "-D", "plughw:0,0", str(STEM)], timeout=20)
    out["aplay|dev=hw:0,0|stem"] = run_bounded(
        ["aplay", "-D", "hw:0,0", str(STEM)], timeout=20)
    out["aplay|-d 2|dev=null"] = run_bounded(
        ["aplay", "-D", "null", "-d", "2", str(STEM)], timeout=20)
    out["aplay|-d 0.05s|dev=null"] = run_bounded(
        ["aplay", "-D", "null", "-d", "0.05s", str(STEM)], timeout=20)
    for k, v in out.items():
        v["playing_line"] = next(
            (l.strip() for l in v["stderr_tail"].splitlines()
             if l.startswith("Playing") or "aplay:" in l), None)
        log(f"[dev] {k} rc={v['exit_code']} wall={v['wall_s']} | "
            f"{v['playing_line']}")
    save("devices", out)
    return out


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    t0 = time.monotonic()
    if which in ("all", "names"):
        batch_name_lattice()
    if which in ("all", "aplay"):
        batch_aplay()
    if which in ("all", "hangs"):
        batch_hangs()
    if which in ("all", "ffplay"):
        batch_ffplay()
    if which in ("all", "gates"):
        batch_gates()
    if which in ("all", "fifo-close"):
        batch_fifo_close()
    if which in ("all", "ffplay-pos"):
        batch_ffplay_position()
    if which in ("all", "devices"):
        batch_devices()
    log(f"[done] {which} in {round(time.monotonic()-t0,1)}s")
