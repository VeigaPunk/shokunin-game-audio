#!/usr/bin/env python3
"""r75-scout fifo cells: writerless-hang + SIGTERM immunity + writer legs.

Protocol per SHARED.md carried guards: fifo-open blocks are SIGTERM-immune ->
bounded escalation to SIGKILL; rc alone is never a verdict (stderr tail kept).
Consumers: paplay (pulse client), aplay (-D null ALSA in-process), ffplay
(SDL dummy driver). Read-only wrt the repo; writes only under
corpus/live/r75-scout/.
"""
import json
import os
import signal
import subprocess
import tempfile
import threading
import time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = REPO / "corpus/live/r75-scout"
SCRATCH = OUT / "scratch"
SCRATCH.mkdir(parents=True, exist_ok=True)

DEC_ACT = REPO / "corpus/live/round-66/pair_dec_act.wav"
DEC_HCOM = REPO / "corpus/live/round-66/pair_dec_hcom.wav"
SND = REPO / "corpus/live/round-69/extsuffix_nomatch.snd"

CONSUMERS = {
    "paplay": ["paplay"],
    "aplay": ["aplay", "-D", "null"],
    "ffplay": ["ffplay", "-nodisp", "-autoexit", "-loglevel", "info"],
}
ENV_FFPLAY = {**os.environ, "SDL_AUDIODRIVER": "dummy"}


def env_for(name):
    return ENV_FFPLAY if name == "ffplay" else os.environ.copy()


def nowriter(name, argv, extra_env=None):
    """Spawn consumer on a writerless fifo; 1.5 s in, record wchan/state, send
    SIGTERM, 1.0 s later check survival, then SIGKILL the group."""
    fifo = SCRATCH / f"nowriter-{name}.fifo"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    env = env_for(name)
    if extra_env:
        env.update(extra_env)
    # start_new_session=True -> child is its own session+group leader, so
    # killpg(pid) reaches the consumer directly (no `setsid` wrapper: the
    # utility forks when already a leader, orphaning the real consumer).
    proc = subprocess.Popen(argv + [str(fifo)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=env, start_new_session=True)
    time.sleep(1.5)
    rec = {"fifo": str(fifo.relative_to(REPO)), "cmd": " ".join(argv)}
    if proc.poll() is not None:
        out, err = proc.communicate(timeout=5)
        rec.update({"blocked": False, "exit_code": proc.returncode,
                    "stderr": err.decode(errors="replace")[-300:]})
        fifo.unlink()
        return rec
    try:
        rec["wchan"] = Path(f"/proc/{proc.pid}/wchan").read_text().strip()
    except OSError:
        rec["wchan"] = None
    try:
        rec["state"] = Path(f"/proc/{proc.pid}/stat").read_text().split()[2]
    except OSError:
        rec["state"] = None
    os.kill(proc.pid, signal.SIGTERM)
    time.sleep(1.0)
    rec["sigterm_immune"] = proc.poll() is None
    if rec["sigterm_immune"]:
        os.killpg(proc.pid, signal.SIGKILL)
    try:
        out, err = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
    rec["exit_code"] = proc.returncode
    rec["blocked"] = True
    rec["stderr"] = err.decode(errors="replace")[-300:]
    fifo.unlink()
    return rec


def writer_leg(name, argv, data, fname, extra_env=None, hold_s=0.5):
    """fifo named fname fed with data; consumer runs to writer EOF."""
    tmp = tempfile.mkdtemp(prefix=f"r75-{name}-", dir=SCRATCH)
    fifo = Path(tmp) / fname
    os.mkfifo(fifo)
    env = env_for(name)
    if extra_env:
        env.update(extra_env)

    def feed():
        try:
            with open(fifo, "wb") as fh:
                fh.write(data)
                fh.flush()
                time.sleep(hold_s)
        except OSError:
            pass

    t = threading.Thread(target=feed, daemon=True)
    t.start()
    t0 = time.monotonic()
    try:
        proc = subprocess.run([*argv, str(fifo)], capture_output=True,
                              timeout=15, env=env)
        rc, out, err, blocked = proc.returncode, proc.stdout, proc.stderr, None
    except subprocess.TimeoutExpired as exc:
        rc, out, err, blocked = None, exc.stdout or b"", exc.stderr or b"", True
    wall = round(time.monotonic() - t0, 3)
    t.join(timeout=hold_s + 5)
    for f in fifo.parent.iterdir():
        pass
    rec = {"fifo_name": fname, "exit_code": rc, "wall_s": wall,
           "blocked": blocked,
           "stderr_tail": err.decode(errors="replace")[-400:]}
    try:
        for f in fifo.parent.iterdir():
            f.unlink()
        fifo.parent.rmdir()
    except OSError:
        pass
    return rec


def log(msg):
    print(msg, flush=True)


def save(out):
    (OUT / "fifo-cells.json").write_text(json.dumps(out, indent=2) + "\n")


def main():
    out = {}
    # 1. writerless-fifo hang class per consumer.
    out["nowriter"] = {}
    for name, argv in CONSUMERS.items():
        log(f"[step] nowriter {name}")
        out["nowriter"][name] = nowriter(name, argv)
        log(f"[step] nowriter {name} -> {json.dumps(out['nowriter'][name])}")
        save(out)
    # 2. paplay daemon-gate precedence: bad PULSE_SERVER + writerless fifo.
    log("[step] nowriter paplay_badserver")
    out["nowriter"]["paplay_badserver"] = nowriter(
        "paplay", CONSUMERS["paplay"],
        extra_env={"PULSE_SERVER": "unix:/nonexistent-r75-gate"})
    log(f"[step] nowriter paplay_badserver -> "
        f"{json.dumps(out['nowriter']['paplay_badserver'])}")
    save(out)
    # 3. writer-attached legs.
    dec_act, dec_hcom, snd = (DEC_ACT.read_bytes(), DEC_HCOM.read_bytes(),
                              SND.read_bytes())
    out["writer"] = {}
    for name, argv in CONSUMERS.items():
        log(f"[step] writer {name}_dec_act")
        out["writer"][f"{name}_dec_act"] = writer_leg(
            name, argv, dec_act, "leg.wav")
        log(f"[step] writer {name}_dec_act -> "
            f"{json.dumps(out['writer'][f'{name}_dec_act'])}")
        save(out)
    log("[step] writer aplay_empty")
    out["writer"]["aplay_empty"] = writer_leg(
        "aplay", CONSUMERS["aplay"], b"", "empty.wav")
    log(f"[step] writer aplay_empty -> "
        f"{json.dumps(out['writer']['aplay_empty'])}")
    save(out)
    log("[step] writer ffplay_dec_hcom")
    out["writer"]["ffplay_dec_hcom"] = writer_leg(
        "ffplay", CONSUMERS["ffplay"], dec_hcom, "leg.wav")
    log(f"[step] writer ffplay_dec_hcom -> "
        f"{json.dumps(out['writer']['ffplay_dec_hcom'])}")
    save(out)
    # 4. paplay name axis on identical no-magic bytes (content-only check).
    for fname in ("axis.snd", "axis.wav", "axis.bin"):
        log(f"[step] writer paplay_{fname}")
        out["writer"][f"paplay_{fname}"] = writer_leg(
            "paplay", CONSUMERS["paplay"], snd, fname)
        log(f"[step] writer paplay_{fname} -> "
            f"{json.dumps(out['writer'][f'paplay_{fname}'])}")
        save(out)
    # 5. paplay --raw control on the same bytes.
    log("[step] writer paplay_raw_axis_snd")
    out["writer"]["paplay_raw_axis_snd"] = writer_leg(
        "paplay", ["paplay", "--raw"], snd, "axis.snd")
    log(f"[step] writer paplay_raw_axis_snd -> "
        f"{json.dumps(out['writer']['paplay_raw_axis_snd'])}")
    # 6. ffplay -ss position cell: seekable file vs stdin.
    log("[step] ffplay_ss2_file")
    t0 = time.monotonic()
    proc = subprocess.run(
        ["ffplay", "-nodisp", "-autoexit", "-ss", "2", "-loglevel", "info",
         str(REPO / "corpus/artifacts/stem_sections.wav")],
        capture_output=True, timeout=20, env=ENV_FFPLAY)
    out["ffplay_ss2_file"] = {
        "exit_code": proc.returncode, "wall_s": round(time.monotonic() - t0, 3),
        "stderr_tail": proc.stderr.decode(errors="replace")[-400:]}
    t0 = time.monotonic()
    proc = subprocess.run(
        ["ffplay", "-nodisp", "-autoexit", "-ss", "2", "-loglevel", "info",
         "-i", "-"], input=(REPO / "corpus/artifacts/stem_sections.wav").read_bytes(),
        capture_output=True, timeout=20, env=ENV_FFPLAY)
    out["ffplay_ss2_stdin"] = {
        "exit_code": proc.returncode, "wall_s": round(time.monotonic() - t0, 3),
        "stderr_tail": proc.stderr.decode(errors="replace")[-400:]}

    path = OUT / "fifo-cells.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
