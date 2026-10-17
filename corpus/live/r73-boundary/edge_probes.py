#!/usr/bin/env python3
"""r73 BOUNDARY edge probes — cells the r73 author/frontier did not measure.

Each probe writes edge_results_<name>.json in this scratch dir.
Usage: python3 edge_probes.py {a,b,c,d,e,f,g,h,i,j}
"""
import json
import math
import os
import signal
import struct
import subprocess
import sys
import time
import wave
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent
ROOT = SCRATCH.parents[2]
LOGS = SCRATCH / "logs"
FIFODIR = LOGS / "fifos"
FIFODIR.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

M = {
    "dec_act": ROOT / "corpus/live/round-66/pair_dec_act.wav",
    "dec_hcom": ROOT / "corpus/live/round-66/pair_dec_hcom.wav",
    "extsuffix_wav": ROOT / "corpus/live/round-69/extsuffix_nomatch.wav",
    "extsuffix_snd": ROOT / "corpus/live/round-69/extsuffix_nomatch.snd",
}
TONE = SCRATCH / "tone4s.wav"


def run_env(cmd, timeout_s, env=None, stdin=None):
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=timeout_s + 5, env=env)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = 999, e.stdout or b"", e.stderr or b""
    return {"rc": rc, "wall_s": round(time.monotonic() - t0, 3),
            "stdout": out.decode("utf-8", "replace")[:2000],
            "stderr": err.decode("utf-8", "replace")[:2000]}


def mkfifo(name):
    f = FIFODIR / name
    if f.exists():
        f.unlink()
    os.mkfifo(f, 0o600)
    return f


def start_reader(cmd, timeout_s):
    return subprocess.Popen(["timeout", "-s", "KILL", str(timeout_s)] + cmd,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def writer_sh(script, timeout_s=25):
    return subprocess.Popen(["timeout", "-s", "KILL", str(timeout_s), "sh", "-c", script],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)


def reap(w, timeout_s=10):
    """Wait for a writer; on hang, SIGKILL its whole process group (orphan-proof)."""
    try:
        w.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(w.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        w.wait()
    return w.returncode


def finish_reader(reader, timeout_s=30):
    t0 = time.monotonic()
    try:
        out, err = reader.communicate(timeout=timeout_s)
        rc = reader.returncode
    except subprocess.TimeoutExpired:
        reader.kill()
        out, err = reader.communicate()
        rc = 999
    return rc, round(time.monotonic() - t0, 3), err.decode("utf-8", "replace")[:2000]


def norm(text, *paths):
    for p in paths:
        text = text.replace(str(p), "<path>")
    return text.strip()


def make_tone():
    if TONE.exists():
        return
    rate, secs, amp = 8000, 4.0, 0.3
    with wave.open(str(TONE), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(int(rate * secs)):
            v = int(amp * 32767 * math.sin(2 * math.pi * 440 * i / rate))
            frames += struct.pack("<h", v)
        w.writeframes(bytes(frames))


def mpv_log_verdict(log):
    txt = log.read_text(encoding="utf-8", errors="replace")
    out = {"not_seekable": "Stream is not seekable." in txt,
           "refresh_seek": "refresh seek to 0.000000" in txt,
           "seek_failed_eperm": "Seek failed (Operation not permitted)" in txt}
    import re
    m = re.search(r"finished playback, ([a-z ]+) \(reason (\d+)\)", txt)
    if m:
        out["finished"] = m.group(1).strip()
        out["reason"] = int(m.group(2))
    return out


# ---------------------------------------------------------------- probe a
def probe_a():
    """daemon gate: dead runtime dir, file arm / fifo arm / writer attached / pactl."""
    emptyrt = SCRATCH / "emptyrt"
    emptyrt.mkdir(mode=0o700, exist_ok=True)
    env = dict(os.environ, PIPEWIRE_RUNTIME_DIR=str(emptyrt), XDG_RUNTIME_DIR=str(emptyrt))
    res = {}
    res["file_arm"] = run_env(["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(M["dec_hcom"])], 8, env=env)
    res["file_arm"]["stderr_norm"] = norm(res["file_arm"]["stderr"], M["dec_hcom"])
    # fifo arm, no writer: if the gate is checked first, this returns instantly
    fifo = mkfifo("gate.fifo")
    res["fifo_nowriter"] = run_env(["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(fifo)], 8, env=env)
    res["fifo_nowriter"]["stderr_norm"] = norm(res["fifo_nowriter"]["stderr"], fifo)
    # fifo arm, writer attached first: reader should still die instantly (gate before
    # open); the writer must then stay blocked in open() forever
    wr = writer_sh(f"cat {M['dec_hcom']} > {fifo}", timeout_s=6)
    time.sleep(0.3)
    rd = run_env(["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(fifo)], 8, env=env)
    rd["stderr_norm"] = norm(rd["stderr"], fifo)
    time.sleep(0.3)
    writer_still_blocked = wr.poll() is None
    reap(wr)
    res["fifo_with_writer"] = {"reader": rd, "writer_still_blocked_in_open": writer_still_blocked,
                               "writer_rc_after_kill": wr.returncode}
    fifo.unlink()
    res["pactl"] = run_env(["pactl", "info"], 8, env=env)
    res["pactl"]["stderr_norm"] = res["pactl"]["stderr"].strip()
    write_result("a", res)


# ---------------------------------------------------------------- probe b
def probe_b():
    """zero-sink private daemon (frontier's explicit gap) + --target 0 control."""
    rt = SCRATCH / "rt2"
    if rt.exists():
        for f in rt.iterdir():
            f.unlink()
    rt.mkdir(mode=0o700, exist_ok=True)
    env = dict(os.environ, PIPEWIRE_RUNTIME_DIR=str(rt), XDG_RUNTIME_DIR=str(rt))
    log = open(LOGS / "edge-private-pipewire.log", "wb")
    daemon = subprocess.Popen(["pipewire"], env=env, stdout=log, stderr=log)
    res = {"private_daemon_pid": daemon.pid}
    sock = rt / "pipewire-0"
    for _ in range(50):
        if sock.exists():
            break
        time.sleep(0.2)
    res["socket_up"] = sock.exists()
    # sink census via pw-dump (full stdout; run_env truncates, so call directly)
    dump = subprocess.run(["timeout", "-s", "KILL", "5", "pw-dump"], env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
    res["pw_dump_rc"] = dump.returncode
    if dump.returncode == 0:
        try:
            objs = json.loads(dump.stdout.decode("utf-8", "replace"))
            classes = {}
            for o in objs:
                props = (o.get("info") or {}).get("props") or {}
                mc = props.get("media.class")
                if mc:
                    classes[mc] = classes.get(mc, 0) + 1
            res["node_classes"] = classes
            res["audio_sink_count"] = classes.get("Audio/Sink", 0)
        except Exception as e:
            res["pw_dump_parse_error"] = str(e)
    # pw-cat against zero-sink daemon
    res["pwcat_file"] = run_env(["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(M["dec_hcom"])], 8, env=env)
    res["pwcat_file"]["stderr_norm"] = norm(res["pwcat_file"]["stderr"], M["dec_hcom"])
    # control: live daemon, --target 0 (no link)
    res["pwcat_target0_live"] = run_env(["timeout", "-s", "KILL", "8", "pw-cat", "-p", "--target", "0",
                                         str(M["dec_hcom"])], 8)
    res["pwcat_target0_live"]["stderr_norm"] = norm(res["pwcat_target0_live"]["stderr"], M["dec_hcom"])
    # teardown
    daemon.terminate()
    try:
        daemon.wait(timeout=5)
    except subprocess.TimeoutExpired:
        daemon.kill()
        daemon.wait()
    log.close()
    res["private_daemon_gone"] = daemon.poll() is not None
    live = subprocess.run(["pgrep", "-a", "pipewire"], stdout=subprocess.PIPE).stdout.decode().strip().splitlines()
    res["live_pipewire_after"] = live
    write_result("b", res)


# ---------------------------------------------------------------- probe c
def probe_c():
    """no-writer hangs (pw-cat + mpv) and empty-writer-close."""
    res = {}
    fifo = mkfifo("c1.fifo")
    res["pwcat_nowriter"] = run_env(["timeout", "-s", "KILL", "6", "pw-cat", "-p", str(fifo)], 6)
    res["pwcat_nowriter"]["stderr_norm"] = norm(res["pwcat_nowriter"]["stderr"], fifo)
    fifo.unlink()
    fifo = mkfifo("c2.fifo")
    log = LOGS / "edge-mpv-nowriter.log"
    res["mpv_nowriter"] = run_env(["timeout", "-s", "KILL", "6", "mpv", "--no-config", "--vo=null",
                                   "--ao=null", "--audio-display=no", "--really-quiet",
                                   f"--log-file={log}", str(fifo)], 6)
    res["mpv_nowriter"].update(mpv_log_verdict(log))
    fifo.unlink()
    fifo = mkfifo("c3.fifo")
    reader = start_reader(["pw-cat", "-p", str(fifo)], 15)
    time.sleep(0.35)
    wr = writer_sh(f": > {fifo}", timeout_s=10)
    rc, wall, err = finish_reader(reader)
    reap(wr, 10)
    res["pwcat_empty_writer"] = {"rc": rc, "wall_s": round(wall + 0.35, 3),
                                 "writer_rc": wr.returncode,
                                 "stderr_norm": norm(err, fifo)}
    fifo.unlink()
    fifo = mkfifo("c4.fifo")
    log = LOGS / "edge-mpv-empty-writer.log"
    mpv = subprocess.Popen(["timeout", "-s", "KILL", "15", "mpv", "--no-config", "--vo=null",
                            "--ao=null", "--audio-display=no", "--really-quiet",
                            f"--log-file={log}", str(fifo)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.35)
    wr = writer_sh(f": > {fifo}", timeout_s=10)
    t0 = time.monotonic()
    try:
        mpv.communicate(timeout=20)
        rc = mpv.returncode
    except subprocess.TimeoutExpired:
        mpv.kill()
        mpv.communicate()
        rc = 999
    reap(wr, 10)
    res["mpv_empty_writer"] = {"rc": rc, "wall_s": round(time.monotonic() - t0 + 0.35, 3),
                               "writer_rc": wr.returncode, **mpv_log_verdict(log)}
    fifo.unlink()
    write_result("c", res)


# ---------------------------------------------------------------- probe d
def probe_d():
    """writer lingers after full member: does pw-cat exit at data end or writer close?"""
    res = {}
    for tag in ("dec_hcom", "dec_act"):
        fifo = mkfifo(f"d-{tag}.fifo")
        reader = start_reader(["pw-cat", "-p", str(fifo)], 25)
        time.sleep(0.35)
        wr = writer_sh(f"cat {M[tag]} > {fifo}; sleep 2", timeout_s=20)
        rc, wall, err = finish_reader(reader)
        reap(wr, 20)
        res[tag] = {"rc": rc, "wall_s": round(wall + 0.35, 3), "writer_rc": wr.returncode,
                    "stderr_norm": norm(err, fifo)}
        fifo.unlink()
    write_result("d", res)


# ---------------------------------------------------------------- probe e
def probe_e():
    """writer dies / partial write mid-stream (frontier predicted rc=0 partial)."""
    make_tone()
    res = {"tone4s_bytes": TONE.stat().st_size}
    # full instant dump of 4 s tone: playback pacing control
    fifo = mkfifo("e-tone.fifo")
    reader = start_reader(["pw-cat", "-p", str(fifo)], 25)
    time.sleep(0.35)
    wr = writer_sh(f"cat {TONE} > {fifo}", timeout_s=20)
    rc, wall, err = finish_reader(reader)
    reap(wr, 20)
    res["tone_full_instant_dump"] = {"rc": rc, "wall_s": round(wall + 0.35, 3),
                                     "stderr_norm": norm(err, fifo)}
    fifo.unlink()
    # half of the 4 s tone, clean close
    half = TONE.stat().st_size // 2 + 22  # header + half data
    fifo = mkfifo("e-tonehalf.fifo")
    reader = start_reader(["pw-cat", "-p", str(fifo)], 25)
    time.sleep(0.35)
    wr = writer_sh(f"head -c {half} {TONE} > {fifo}", timeout_s=20)
    rc, wall, err = finish_reader(reader)
    reap(wr, 20)
    res["tone_half_close"] = {"rc": rc, "wall_s": round(wall + 0.35, 3), "bytes": half,
                              "stderr_norm": norm(err, fifo)}
    fifo.unlink()
    # writer SIGKILLs itself after half
    fifo = mkfifo("e-tonedie.fifo")
    reader = start_reader(["pw-cat", "-p", str(fifo)], 25)
    time.sleep(0.35)
    py = ("import os,sys; d=open(sys.argv[1],'rb').read(); "
          "fd=os.open(sys.argv[2], os.O_WRONLY); os.write(fd, d[:len(d)//2]); "
          "os.kill(os.getpid(), 9)")
    wr = writer_sh(f"python3 -c \"{py}\" {TONE} {fifo}", timeout_s=20)
    rc, wall, err = finish_reader(reader)
    try:
        reap(wr, 20)
    except subprocess.TimeoutExpired:
        wr.kill()
    res["tone_half_writer_sigkill"] = {"rc": rc, "wall_s": round(wall + 0.35, 3),
                                       "writer_rc": wr.returncode, "stderr_norm": norm(err, fifo)}
    fifo.unlink()
    # dec_hcom half
    fifo = mkfifo("e-hcomhalf.fifo")
    reader = start_reader(["pw-cat", "-p", str(fifo)], 15)
    time.sleep(0.35)
    sz = M["dec_hcom"].stat().st_size // 2
    wr = writer_sh(f"head -c {sz} {M['dec_hcom']} > {fifo}", timeout_s=15)
    rc, wall, err = finish_reader(reader)
    reap(wr, 15)
    res["hcom_half_close"] = {"rc": rc, "wall_s": round(wall + 0.35, 3), "bytes": sz,
                              "stderr_norm": norm(err, fifo)}
    fifo.unlink()
    write_result("e", res)


# ---------------------------------------------------------------- probe f
def probe_f():
    """pw-cat open-block vs SIGTERM: timeout 5 (TERM), poll at 7 s."""
    fifo = mkfifo("f1.fifo")
    p = subprocess.Popen(["timeout", "5", "pw-cat", "-p", str(fifo)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(7)
    alive = p.poll() is None
    pg = subprocess.run(["pgrep", "-f", str(fifo)], stdout=subprocess.PIPE).stdout.decode().strip().splitlines()
    res = {"timeout_termer_still_waiting_at_7s": alive, "pids_holding_fifo": pg}
    # cleanup: kill any pw-cat on this fifo, then the timeout wrapper
    subprocess.run(["pkill", "-9", "-f", str(fifo)])
    p.kill()
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    res["cleanup_rc"] = p.returncode
    time.sleep(0.3)
    res["pids_after_cleanup"] = subprocess.run(["pgrep", "-f", str(fifo)],
                                               stdout=subprocess.PIPE).stdout.decode().strip().splitlines()
    fifo.unlink()
    write_result("f", res)


# ---------------------------------------------------------------- probe g
def probe_g():
    """content-vs-name on fifos: .txw name + hcom bytes; .wav name + no-magic bytes."""
    res = {}

    def pwcat_cell(name, member):
        fifo = mkfifo(name)
        reader = start_reader(["pw-cat", "-p", str(fifo)], 15)
        time.sleep(0.35)
        wr = writer_sh(f"cat {member} > {fifo}", timeout_s=15)
        rc, wall, err = finish_reader(reader)
        reap(wr, 15)
        fifo.unlink()
        return {"rc": rc, "wall_s": round(wall + 0.35, 3), "stderr_norm": norm(err, fifo)}

    def mpv_cell(name, member):
        fifo = mkfifo(name)
        log = LOGS / f"edge-g-{name}.log"
        mpv = subprocess.Popen(["timeout", "-s", "KILL", "15", "mpv", "--no-config", "--vo=null",
                                "--ao=null", "--audio-display=no", "--really-quiet",
                                f"--log-file={log}", str(fifo)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.35)
        wr = writer_sh(f"cat {member} > {fifo}", timeout_s=15)
        t0 = time.monotonic()
        try:
            mpv.communicate(timeout=20)
            rc = mpv.returncode
        except subprocess.TimeoutExpired:
            mpv.kill()
            mpv.communicate()
            rc = 999
        reap(wr, 15)
        fifo.unlink()
        return {"rc": rc, "wall_s": round(time.monotonic() - t0 + 0.35, 3), **mpv_log_verdict(log)}

    res["pwcat_hcom_bytes_named_txw"] = pwcat_cell("g1.txw", M["dec_hcom"])
    res["pwcat_nomagic_bytes_named_wav"] = pwcat_cell("g2.wav", M["extsuffix_wav"])
    res["mpv_hcom_bytes_named_txw"] = mpv_cell("g3.txw", M["dec_hcom"])
    res["mpv_nomagic_bytes_named_wav"] = mpv_cell("g4.wav", M["extsuffix_wav"])
    write_result("g", res)


# ---------------------------------------------------------------- probe h
def probe_h():
    """strace the mpv file arm on hcom: is the EPERM a failing syscall?"""
    log = LOGS / "edge-strace-mpv-file-dec_hcom.txt"
    r = run_env(["strace", "-f", "-o", str(log),
                 "-e", "trace=openat,lseek,fcntl,ioctl,read,pread64",
                 "mpv", "--no-config", "--vo=null", "--ao=null", "--audio-display=no",
                 "--really-quiet", str(M["dec_hcom"])], 20)
    txt = log.read_text(encoding="utf-8", errors="replace")
    eperm_lines = [ln for ln in txt.splitlines() if "EPERM" in ln]
    lseek_lines = [ln.strip() for ln in txt.splitlines() if " lseek(" in ln]
    failed_lseeks = [ln for ln in lseek_lines if "= -1" in ln]
    res = {"mpv_rc": r["rc"], "eperm_syscall_lines": eperm_lines[:5],
           "eperm_syscall_count": len(eperm_lines), "lseek_lines": lseek_lines,
           "failed_lseek_count": len(failed_lseeks), "log": str(log.relative_to(SCRATCH))}
    write_result("h", res)


# ---------------------------------------------------------------- probe i
def probe_i():
    """instant dump pacing (tone4s) and slow trickle."""
    make_tone()
    res = {}
    fifo = mkfifo("i1.fifo")
    reader = start_reader(["pw-cat", "-p", str(fifo)], 25)
    time.sleep(0.35)
    wr = writer_sh(f"cat {TONE} > {fifo}", timeout_s=20)
    rc, wall, err = finish_reader(reader)
    reap(wr, 20)
    res["instant_dump_4s_tone"] = {"rc": rc, "wall_s": round(wall + 0.35, 3), "stderr_norm": norm(err, fifo)}
    fifo.unlink()
    # slow trickle: 1600 B chunks, 0.2 s apart (~8 s to deliver 4 s)
    fifo = mkfifo("i2.fifo")
    reader = start_reader(["pw-cat", "-p", str(fifo)], 40)
    time.sleep(0.35)
    wr = writer_sh(f"python3 -c \"import sys,time; d=open(sys.argv[1],'rb').read(); "
                   f"fd=open(sys.argv[2],'wb'); "
                   f"[ (fd.write(d[i:i+1600]), fd.flush(), time.sleep(0.2)) for i in range(0,len(d),1600) ]; "
                   f"fd.close()\" {TONE} {fifo}", timeout_s=30)
    rc, wall, err = finish_reader(reader)
    reap(wr, 30)
    res["slow_trickle_1600B_200ms"] = {"rc": rc, "wall_s": round(wall + 0.35, 3), "stderr_norm": norm(err, fifo)}
    fifo.unlink()
    write_result("i", res)


# ---------------------------------------------------------------- probe j
def probe_j():
    """two concurrent writers, 3 reps (frontier gap: multiple writers)."""
    res = {"reps": []}
    for rep in range(3):
        fifo = mkfifo(f"j{rep}.fifo")
        reader = start_reader(["pw-cat", "-p", str(fifo)], 20)
        time.sleep(0.35)
        w1 = writer_sh(f"cat {M['dec_act']} > {fifo}", timeout_s=15)
        w2 = writer_sh(f"cat {M['dec_act']} > {fifo}", timeout_s=15)
        rc, wall, err = finish_reader(reader)
        for w in (w1, w2):
            reap(w, 15)
        res["reps"].append({"rc": rc, "wall_s": round(wall + 0.35, 3),
                            "writer_rcs": [w1.returncode, w2.returncode],
                            "stderr_norm": norm(err, fifo)})
        fifo.unlink()
    write_result("j", res)


def write_result(name, res):
    out = SCRATCH / f"edge_results_probe-{name}.json"
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps(res, indent=1, sort_keys=True))
    print(f"# wrote {out}")


def probe_k():
    """force-seekable override on the dec_hcom fork (2x2: file/fs=no, fifo/fs=yes)."""
    res = {}
    log = LOGS / "edge-mpv-file-dec_hcom-fsno.log"
    r = run_env(["timeout", "-s", "KILL", "15", "mpv", "--no-config", "--force-seekable=no",
                 "--vo=null", "--ao=null", "--audio-display=no", "--really-quiet",
                 f"--log-file={log}", str(M["dec_hcom"])], 15)
    res["file_force_seekable_no"] = {"rc": r["rc"], **mpv_log_verdict(log)}
    fifo = mkfifo("k1.fifo")
    log = LOGS / "edge-mpv-fifo-dec_hcom-fsyes.log"
    mpv = subprocess.Popen(["timeout", "-s", "KILL", "15", "mpv", "--no-config",
                            "--force-seekable=yes", "--vo=null", "--ao=null",
                            "--audio-display=no", "--really-quiet",
                            f"--log-file={log}", str(fifo)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.35)
    wr = writer_sh(f"cat {M['dec_hcom']} > {fifo}", timeout_s=15)
    t0 = time.monotonic()
    try:
        mpv.communicate(timeout=20)
        rc = mpv.returncode
    except subprocess.TimeoutExpired:
        mpv.kill()
        mpv.communicate()
        rc = 999
    reap(wr, 15)
    res["fifo_force_seekable_yes"] = {"rc": rc, "wall_s": round(time.monotonic() - t0 + 0.35, 3),
                                      **mpv_log_verdict(log)}
    fifo.unlink()
    write_result("k", res)


def probe_l():
    """pw-cat fifo name sweep: does the libsndfile .snd fallback fire by fifo name?"""
    res = {}

    def cell(name, member):
        fifo = mkfifo(name)
        reader = start_reader(["pw-cat", "-p", str(fifo)], 15)
        time.sleep(0.35)
        wr = writer_sh(f"cat {member} > {fifo}", timeout_s=15)
        rc, wall, err = finish_reader(reader)
        reap(wr, 15)
        fifo.unlink()
        return {"rc": rc, "wall_s": round(wall + 0.35, 3), "stderr_norm": norm(err, fifo)}

    res["snd_bytes_named_foo"] = cell("l1.foo", M["extsuffix_snd"])
    res["snd_bytes_named_snd"] = cell("l2.snd", M["extsuffix_snd"])
    res["snd_bytes_named_SND"] = cell("l3.SND", M["extsuffix_snd"])
    res["snd_bytes_named_wav"] = cell("l4.wav", M["extsuffix_snd"])
    write_result("l", res)


PROBES = {"a": probe_a, "b": probe_b, "c": probe_c, "d": probe_d, "e": probe_e,
          "f": probe_f, "g": probe_g, "h": probe_h, "i": probe_i, "j": probe_j,
          "k": probe_k, "l": probe_l}

if __name__ == "__main__":
    which = sys.argv[1]
    PROBES[which]()
