#!/usr/bin/env python3
"""r74 BOUNDARY scratch probe — lavf no-seek edge members + pw-cat kill class + daemon cells.

Scratch only (corpus/live/r74-boundary/), NOT tracked evidence.  Mirrors the
r74 author arm shape (`--probe-lavfsweep-r74`: iss/apc/acm x {file,fifo} x mpv,
lavf log fields, NEVER bare rc) but owns the BOUNDARY lattice:
  matrix   : hand-built members x {ffprobe, mpv file, mpv fifo, pw-cat file, pw-cat fifo}
  linger   : malformed/valid member + fifo writer that does NOT close  (hang class)
  target0  : pw-cat --target 0 kill class, single + under load + TERM/KILL escalation
  daemon   : zero-sink private daemon feasibility (private PIPEWIRE_RUNTIME_DIR)
  startpos : mpv --start=N position fork on tone4s.wav (file seeks vs fifo plays from 0)

All arms bounded; every fifo-adjacent arm uses `timeout -s KILL`.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent
ROOT = SCRATCH.parents[2]
MEM = SCRATCH / "members"
RUNS = SCRATCH / "runs"
LOGS = SCRATCH / "logs"
FIFODIR = LOGS / "fifos"
ARM_TIMEOUT = 20


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cmd(cmd, timeout_s, cwd=None, env=None):
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=timeout_s + 5, cwd=cwd, env=env)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = 999, e.stdout or b"", e.stderr or b""
    return {"rc": rc, "wall_s": round(time.monotonic() - t0, 3),
            "stdout": out.decode("utf-8", "replace"),
            "stderr": err.decode("utf-8", "replace")}


def make_fifo(name):
    FIFODIR.mkdir(parents=True, exist_ok=True)
    f = FIFODIR / name
    if f.exists():
        f.unlink()
    os.mkfifo(f, 0o600)
    return f


def norm(text, *paths):
    for p in paths:
        text = text.replace(str(p), "<" + Path(str(p)).name + ">")
    return [ln.strip() for ln in text.strip().splitlines() if ln.strip()][:5]


# ---------------------------------------------------------------- member cells

def ffprobe_file(member):
    r = run_cmd(["ffprobe", "-hide_banner", "-v", "debug", "-i", str(member)], 10)
    v = {"rc": r["rc"]}
    m = re.search(r"Format (\S+) probed with size=(\d+) and score=(\d+)", r["stderr"])
    if m:
        v["probed"] = {"fmt": m.group(1), "size": int(m.group(2)),
                       "score": int(m.group(3))}
    lines = [ln for ln in r["stderr"].splitlines()
             if "Invalid data" in ln or "Error" in ln]
    v["err_tail"] = lines[-1].strip() if lines else None
    return v


def parse_mpv_log(logpath):
    txt = logpath.read_text(encoding="utf-8", errors="replace") if logpath.exists() else ""
    v = {"detected": None, "not_seekable": "Stream is not seekable." in txt,
         "refresh_seek": "refresh seek to 0.000000" in txt,
         "seek_failed_eperm": "Seek failed (Operation not permitted)" in txt,
         "audio_track": None, "finished": None, "reason": None,
         "eof_reached": "EOF reached." in txt,
         "start_seek": None, "demux_error": None}
    m = re.search(r"\[lavf\] Found '([^']+)' at score=(\d+) size=(\d+)", txt)
    if m:
        v["detected"] = {"fmt": m.group(1), "score": int(m.group(2)),
                         "size": int(m.group(3))}
    m = re.search(r"● Audio\s+--aid=1\s+\(([^)]+)\)", txt)
    if m:
        v["audio_track"] = m.group(1)
    m = re.search(r"finished playback, ([a-z ]+) \(reason (\d+)\)", txt)
    if m:
        v["finished"] = m.group(1).strip()
        v["reason"] = int(m.group(2))
    m = re.search(r"Seek to ([0-9.]+)", txt)
    if m:
        v["start_seek"] = m.group(1)
    m = re.search(r"(Error while decoding|Invalid data found|Could not open|error reading)", txt)
    if m:
        v["demux_error"] = m.group(1)
    return v


def mpv_file(member, tag, extra=None, ao="null", logname=None):
    log = LOGS / (logname or f"r74-mpv-file-{tag}.log")
    cmd = ["timeout", "-s", "KILL", str(ARM_TIMEOUT), "mpv", "--no-config",
           "--vo=null", f"--ao={ao}", "--audio-display=no", "--really-quiet",
           f"--log-file={log}"]
    cmd += extra or []
    cmd.append(str(member))
    r = run_cmd(cmd, ARM_TIMEOUT)
    return {"rc": r["rc"], "wall_s": r["wall_s"], **parse_mpv_log(log)}


def mpv_fifo(member, tag, writer_script=None, logname=None, extra=None, ao="null"):
    fifo = make_fifo(member.name)
    log = LOGS / (logname or f"r74-mpv-fifo-{tag}.log")
    cmd = ["timeout", "-s", "KILL", str(ARM_TIMEOUT), "mpv", "--no-config",
           "--vo=null", f"--ao={ao}", "--audio-display=no", "--really-quiet",
           f"--log-file={log}"]
    cmd += extra or []
    cmd.append(str(fifo))
    mpv = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.35)
    script = (writer_script.format(fifo=fifo) if writer_script
              else f"cat {member} > {fifo}")
    wr = run_cmd(["timeout", "-s", "KILL", str(ARM_TIMEOUT), "sh", "-c", script],
                 ARM_TIMEOUT)
    t0 = time.monotonic()
    try:
        mpv.communicate(timeout=ARM_TIMEOUT + 5)
        rc = mpv.returncode
    except subprocess.TimeoutExpired:
        mpv.kill()
        mpv.communicate()
        rc = 999
    wall = round(time.monotonic() - t0 + 0.35, 3)
    if fifo.exists():
        fifo.unlink()
    return {"rc": rc, "wall_s": wall, "writer_rc": wr["rc"],
            **parse_mpv_log(log)}


def pwcat_file(member):
    r = run_cmd(["timeout", "-s", "KILL", str(ARM_TIMEOUT), "pw-cat", "-p",
                 str(member)], ARM_TIMEOUT)
    return {"rc": r["rc"], "wall_s": r["wall_s"],
            "stderr_norm": norm(r["stderr"], member)}


def pwcat_fifo(member):
    fifo = make_fifo(member.name)
    reader = subprocess.Popen(["timeout", "-s", "KILL", str(ARM_TIMEOUT),
                               "pw-cat", "-p", str(fifo)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.35)
    wr = run_cmd(["timeout", "-s", "KILL", str(ARM_TIMEOUT), "sh", "-c",
                  f"cat {member} > {fifo}"], ARM_TIMEOUT)
    t0 = time.monotonic()
    try:
        out, err = reader.communicate(timeout=ARM_TIMEOUT + 5)
        rc = reader.returncode
    except subprocess.TimeoutExpired:
        reader.kill()
        out, err = reader.communicate()
        rc = 999
    wall = round(time.monotonic() - t0 + 0.35, 3)
    if fifo.exists():
        fifo.unlink()
    return {"rc": rc, "wall_s": wall, "writer_rc": wr["rc"],
            "stderr_norm": norm(err.decode("utf-8", "replace"), member, fifo)}


# ------------------------------------------------------------------- subcmds

def cmd_matrix():
    names = sorted(p.name for p in MEM.iterdir() if p.is_file())
    cells = {}
    for tag in names:
        member = MEM / tag
        cells[f"ffprobe_file:{tag}"] = ffprobe_file(member)
        cells[f"mpv_file:{tag}"] = mpv_file(member, tag)
        cells[f"mpv_fifo:{tag}"] = mpv_fifo(member, tag)
        cells[f"pwcat_file:{tag}"] = pwcat_file(member)
        cells[f"pwcat_fifo:{tag}"] = pwcat_fifo(member)
        print(f"[matrix] {tag}", flush=True)
    return cells


def cmd_linger():
    cells = {}
    # valid member + writer that keeps the fifo open after the dump -> reader
    # should never see EOF (bounded KILL).  Also the huge-packet malformed case.
    for tag in ("iss_valid", "iss_pkt_huge", "acm_valid", "apc_valid"):
        member = MEM / tag
        script = (f"python3 {SCRATCH}/linger_writer.py {member} {{fifo}} 30")
        cells[f"mpv_fifo_linger:{tag}"] = mpv_fifo(
            member, f"linger-{tag}", writer_script=script,
            logname=f"r74-mpv-fifo-linger-{tag}.log")
        print(f"[linger] {tag}", flush=True)
    # pw-cat variant on one member (writer stays open)
    member = MEM / "iss_valid"
    fifo = make_fifo(member.name)
    reader = subprocess.Popen(["timeout", "-s", "KILL", str(ARM_TIMEOUT),
                               "pw-cat", "-p", str(fifo)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.35)
    wr = run_cmd(["timeout", "-s", "KILL", str(ARM_TIMEOUT), "python3",
                  f"{SCRATCH}/linger_writer.py", str(member), str(fifo), "30"],
                 ARM_TIMEOUT)
    t0 = time.monotonic()
    try:
        out, err = reader.communicate(timeout=ARM_TIMEOUT + 5)
        rc = reader.returncode
    except subprocess.TimeoutExpired:
        reader.kill()
        out, err = reader.communicate()
        rc = 999
    wall = round(time.monotonic() - t0 + 0.35, 3)
    if fifo.exists():
        fifo.unlink()
    cells["pwcat_fifo_linger:iss_valid"] = {
        "rc": rc, "wall_s": wall, "writer_rc": wr["rc"],
        "stderr_norm": norm(err.decode("utf-8", "replace"), member, fifo)}
    print("[linger] pwcat done", flush=True)
    return cells


def cmd_target0():
    member = MEM / "tone4s.wav"        # sndfile-accepted member; --target 0 needs
    reject = MEM / "iss_valid"         # a member past the sndfile gate (see cell)
    cells = {}
    # the gate confound: iss/apc/acm never reach the link stage
    r = run_cmd(["timeout", "-s", "TERM", "4", "pw-cat", "-p", "--target", "0",
                 str(reject)], 10)
    cells["t0_iss_sndfile_gate"] = {"rc": r["rc"], "wall_s": r["wall_s"],
                                    "stderr_norm": norm(r["stderr"], reject)}
    # control, single instance
    cells["t0_single_term"] = run_cmd(
        ["timeout", "-s", "TERM", "4", "pw-cat", "-p", "--target", "0",
         str(member)], 10)
    cells["t0_single_term_k3"] = run_cmd(
        ["timeout", "-k", "3", "-s", "TERM", "4", "pw-cat", "-p", "--target",
         "0", str(member)], 12)
    # hang proof: 4 s of audio must NOT finish under a 8 s KILL window if the
    # unlinked stream never drains; linked control must finish at ~4 s.
    cells["t0_kill8_hang_proof"] = run_cmd(
        ["timeout", "-s", "KILL", "8", "pw-cat", "-p", "--target", "0",
         str(member)], 12)
    cells["linked_control_kill8"] = run_cmd(
        ["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(member)], 12)
    # under load: 8 concurrent
    t0 = time.monotonic()
    procs = [subprocess.Popen(["timeout", "-s", "TERM", "4", "pw-cat", "-p",
                               "--target", "0", str(member)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
             for _ in range(8)]
    rcs = []
    for p in procs:
        try:
            p.communicate(timeout=15)
            rcs.append(p.returncode)
        except subprocess.TimeoutExpired:
            p.kill()
            p.communicate()
            rcs.append(999)
    cells["t0_load8_term"] = {"rcs": rcs, "wall_s": round(time.monotonic() - t0, 3)}
    # writerless fifo contrast (SIGTERM-immune) x4
    f = make_fifo("t0_writerless")
    procs = [subprocess.Popen(["timeout", "-k", "3", "-s", "TERM", "4",
                               "pw-cat", "-p", str(f)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
             for _ in range(4)]
    t0 = time.monotonic()
    rcs = []
    for p in procs:
        try:
            p.communicate(timeout=20)
            rcs.append(p.returncode)
        except subprocess.TimeoutExpired:
            p.kill()
            p.communicate()
            rcs.append(999)
    cells["writerless_load4_term_k3"] = {"rcs": rcs,
                                         "wall_s": round(time.monotonic() - t0, 3)}
    if f.exists():
        f.unlink()
    # mixed: 4 target0 + 4 writerless simultaneously
    f = make_fifo("t0_mixed")
    procs = []
    for i in range(8):
        if i % 2 == 0:
            procs.append(("t0", subprocess.Popen(
                ["timeout", "-s", "TERM", "4", "pw-cat", "-p", "--target", "0",
                 str(member)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)))
        else:
            procs.append(("writerless", subprocess.Popen(
                ["timeout", "-k", "3", "-s", "TERM", "4", "pw-cat", "-p", str(f)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)))
    t0 = time.monotonic()
    mixed = []
    for kind, p in procs:
        try:
            p.communicate(timeout=25)
            mixed.append((kind, p.returncode))
        except subprocess.TimeoutExpired:
            p.kill()
            p.communicate()
            mixed.append((kind, 999))
    cells["mixed_load8"] = {"pairs": mixed, "wall_s": round(time.monotonic() - t0, 3)}
    if f.exists():
        f.unlink()
    return cells


def cmd_daemon():
    cells = {}
    rt = SCRATCH / "rt-nosink"
    rt.mkdir(exist_ok=True)
    env = dict(os.environ, PIPEWIRE_RUNTIME_DIR=str(rt), XDG_RUNTIME_DIR=str(rt))
    t0 = time.monotonic()
    pw = subprocess.Popen(["timeout", "-s", "KILL", "90", "pipewire"],
                          env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sock = rt / "pipewire-0"
    up = False
    for _ in range(100):
        if sock.exists():
            up = True
            break
        time.sleep(0.05)
    cells["private_daemon_up"] = {"up": up,
                                  "socket_s": round(time.monotonic() - t0, 3)}
    if up:
        def dump_summary(tag):
            d = run_cmd(["pw-dump"], 10, env=env)
            names = re.findall(r'"node\.name":\s*"([^"]+)"', d["stdout"])
            return {"rc": d["rc"],
                    "n_nodes": d["stdout"].count('"type": "PipeWire:Interface:Node"'),
                    "n_ports": d["stdout"].count('"type": "PipeWire:Interface:Port"'),
                    "node_names": names}
        cells["pw_dump_nodes"] = dump_summary("before")
        # pw-cat playback on zero-sink daemon (expect hang -> KILL)
        member = MEM / "tone4s.wav"
        cells["pwc_zero_sink"] = run_cmd(
            ["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(member)], 12, env=env)
        # --target 0 control on the private daemon
        cells["pwc_zero_sink_target0"] = run_cmd(
            ["timeout", "-s", "KILL", "6", "pw-cat", "-p", "--target", "0",
             str(member)], 10, env=env)
        # the sndfile-gate confound (iss member never reaches the link stage)
        cells["pwc_zero_sink_iss_gate"] = run_cmd(
            ["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(MEM / "iss_valid")],
            12, env=env)
        # feasibility: load fallback-sink at runtime
        lm = run_cmd(["pw-cli", "load-module", "libpipewire-module-fallback-sink"],
                     10, env=env)
        cells["load_fallback_sink"] = {"rc": lm["rc"],
                                       "out": (lm["stdout"] + lm["stderr"]).strip()[:300]}
        cells["pw_dump_after_fallback"] = dump_summary("after")
        cells["pwc_with_fallback_sink"] = run_cmd(
            ["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(member)], 12, env=env)
    # teardown
    pw.terminate()
    try:
        pw.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        pw.kill()
        pw.communicate()
    cells["daemon_teardown_rc"] = pw.returncode
    # residue check
    r = run_cmd(["pgrep", "-a", "pipewire"], 5)
    cells["pipewire_after_teardown"] = r["stdout"].strip().splitlines()
    return cells


def pcm_bytes(path):
    p = Path(path)
    return p.stat().st_size if p.exists() else None


def cmd_daemon2():
    """Zero-sink private daemon + fallback-sink loaded IN THE DAEMON config.

    (`pw-cli load-module` runs in the pw-cli client context, so the earlier
    rc=0 load did not touch the daemon — this is the correct feasibility arm.)
    """
    cells = {}
    src = Path("/usr/share/pipewire/pipewire.conf").read_text()
    # append the module at the END of context.modules (it needs the native
    # protocol module, so it must not be first in the list)
    start = src.index("context.modules = [")
    end = src.index("\n]", start)
    conf = (src[:end] +
            "\n    { name = libpipewire-module-fallback-sink }\n" +
            src[end:])
    confpath = SCRATCH / "fallback.conf"
    confpath.write_text(conf)
    cells["fallback_conf_sha256"] = hashlib.sha256(conf.encode()).hexdigest()
    rt = SCRATCH / "rt-fallback"
    rt.mkdir(exist_ok=True)
    env = dict(os.environ, PIPEWIRE_RUNTIME_DIR=str(rt), XDG_RUNTIME_DIR=str(rt))
    pw = subprocess.Popen(["timeout", "-s", "KILL", "60", "pipewire", "-c",
                           str(confpath)],
                          env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sock = rt / "pipewire-0"
    up = False
    for _ in range(100):
        if sock.exists():
            up = True
            break
        time.sleep(0.05)
    cells["fallback_daemon_up"] = {"up": up}
    if up:
        time.sleep(0.3)
        d = run_cmd(["pw-dump"], 10, env=env)
        cells["pw_dump_fallback"] = {
            "rc": d["rc"],
            "node_names": re.findall(r'"node\.name":\s*"([^"]+)"', d["stdout"]),
            "n_ports": d["stdout"].count('"type": "PipeWire:Interface:Port"')}
        member = MEM / "tone4s.wav"
        cells["pwc_fallback_daemon"] = run_cmd(
            ["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(member)], 12, env=env)
    pw.terminate()
    try:
        pw.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        pw.kill()
        pw.communicate()
    cells["daemon2_teardown_rc"] = pw.returncode
    return cells


def cmd_crosscheck():
    """Independent re-measurement of the AUTHOR's landed r74 members
    (corpus/live/round-74/lavf_*), read-only, through this seat's harness."""
    src = ROOT / "corpus/live/round-74"
    cells = {}
    files = sorted(p for p in src.glob("lavf_*") if p.is_file())
    for member in files:
        tag = member.name
        cells[f"ffprobe_file:{tag}"] = ffprobe_file(member)
        cells[f"mpv_file:{tag}"] = mpv_file(member, tag)
        cells[f"mpv_fifo:{tag}"] = mpv_fifo(member, tag)
        cells[f"pwcat_file:{tag}"] = pwcat_file(member)
        cells[f"sha256:{tag}"] = sha256(member)
        print(f"[crosscheck] {tag}", flush=True)
    return cells


def cmd_truncation():
    """How much audio actually reaches the AO on the no-seek members, file vs
    fifo, measured as raw PCM bytes from mpv --ao=pcm (untimed: wall is not a
    witness, bytes are)."""
    targets = [
        ("iss_valid", MEM / "iss_valid", 81920, "40x512B pkts -> 40960 smp @44100", 44100),
        ("acm_valid", MEM / "acm_valid", None, "350 frames", 22050),
        ("lavf_iss.iss", ROOT / "corpus/live/round-74/lavf_iss.iss", 4096,
         "2x256B pkts -> 2048 smp @44100", 44100),
        ("lavf_iss_multi.iss", ROOT / "corpus/live/round-74/lavf_iss_multi.iss",
         524288, "256x512B pkts -> 262144 smp @44100", 44100),
        ("lavf_acm.acm", ROOT / "corpus/live/round-74/lavf_acm.acm", None,
         "20x119B frames", 22050),
    ]
    cells = {}
    for tag, member, expect, note, rate in targets:
        if not member.exists():
            cells[f"missing:{tag}"] = str(member)
            continue
        for arm in ("file", "fifo"):
            out = LOGS / f"r74-trunc-{tag}-{arm}.pcm"
            if out.exists():
                out.unlink()
            extra = ["--ao=pcm", f"--ao-pcm-file={out}", "--ao-pcm-waveheader=no"]
            if arm == "file":
                v = mpv_file(member, f"trunc-{tag}-{arm}", extra=extra, ao="pcm",
                             logname=f"r74-mpv-trunc-{tag}-{arm}.log")
            else:
                v = mpv_fifo(member, f"trunc-{tag}-{arm}", extra=extra, ao="pcm",
                             logname=f"r74-mpv-trunc-{tag}-{arm}.log")
            v["pcm_bytes"] = pcm_bytes(out)
            v["pcm_s"] = round((v["pcm_bytes"] or 0) / 2.0 / rate, 3)
            v["expect_bytes"] = expect
            v["note"] = note
            cells[f"{tag}:{arm}"] = v
            print(f"[trunc] {tag}:{arm} rc={v['rc']} bytes={v['pcm_bytes']} "
                  f"({v['pcm_s']}s) expect={expect}", flush=True)
    return cells


def cmd_startpos():
    tone = MEM / "tone4s.wav"
    cells = {}
    for start in ("1", "5"):
        for arm in ("file", "fifo"):
            out = LOGS / f"r74-start{start}-{arm}.pcm"
            if out.exists():
                out.unlink()
            extra = [f"--start={start}", "--ao=pcm",
                     f"--ao-pcm-file={out}", "--ao-pcm-waveheader=no"]
            tag = f"start{start}-{arm}"
            if arm == "file":
                v = mpv_file(tone, tag, extra=extra, ao="pcm",
                             logname=f"r74-mpv-{tag}.log")
            else:
                v = mpv_fifo(tone, tag, extra=extra, ao="pcm",
                             logname=f"r74-mpv-{tag}.log")
            v["pcm_bytes"] = pcm_bytes(out)
            v["pcm_s"] = round((v["pcm_bytes"] or 0) / (8000 * 1 * 2), 3)
            cells[tag] = v
            print(f"[startpos] {tag} rc={v['rc']} bytes={v['pcm_bytes']}", flush=True)
    # log tail for the two --start=1 arms (seek trace)
    for arm in ("file", "fifo"):
        log = LOGS / f"r74-mpv-start1-{arm}.log"
        txt = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
        hits = [ln for ln in txt.splitlines()
                if re.search(r"[Ss]eek|not seekable|start|EOF", ln)]
        cells[f"log_tail:start1-{arm}"] = hits[-12:]
    return cells


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "matrix"
    fn = {"matrix": cmd_matrix, "linger": cmd_linger, "target0": cmd_target0,
          "daemon": cmd_daemon, "daemon2": cmd_daemon2,
          "crosscheck": cmd_crosscheck, "truncation": cmd_truncation,
          "startpos": cmd_startpos}[which]
    stamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime()) + f"{time.time()%1:.9f}"[1:10]
    rundir = RUNS / f"{stamp}Z-{which}-r74"
    rundir.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    cells = fn()
    (rundir / "measurements.json").write_text(json.dumps(cells, indent=1, sort_keys=True))
    # verdicts = replay-stable core: drop walls and daemon pids
    verdicts = {}
    for k, v in cells.items():
        if isinstance(v, dict):
            verdicts[k] = {kk: vv for kk, vv in v.items()
                           if kk not in ("wall_s", "stderr", "stdout")}
        else:
            verdicts[k] = v
    (rundir / "verdicts.json").write_text(json.dumps(verdicts, indent=1, sort_keys=True))
    print(f"receipts -> {rundir}")
    print("verdicts sha256:", hashlib.sha256(
        (rundir / "verdicts.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
