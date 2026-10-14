#!/usr/bin/env python3
"""r67-scribe: independent transport-fork matrix.

For each fixture, present the SAME byte stream to `sox -V4 ... -n stat`
through four transports and record detection + decode verdict:

  file  : sox -V4 PATH -n stat                    (named seekable path)
  pipe  : cat PATH | sox -V4 - -n stat            (fd0 = anonymous pipe)
  redir : sox -V4 - -n stat < PATH                (fd0 = regular file, seekable)
  fifo  : sox -V4 FIFO -n stat with `cat PATH > FIFO` writer
                                                  (named path, non-seekable)

Every sox leg runs in its own process group with a 30 s cap and a
killpg teardown: the act->ffmpeg bridge leaves orphaned ffmpeg
children holding the stderr pipe (observed live on this host), which
would otherwise wedge communicate() on EOF forever.

Emits runs/transport-matrix.tsv + per-leg logs under runs/logs/.
Scratch-only derivation; reads tracked fixtures, never mutates them.
"""
import os
import re
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SCRATCH = ROOT / "corpus/live/r67-scribe"
LOGS = SCRATCH / "runs" / "logs"
TSV = SCRATCH / "runs" / "transport-matrix.tsv"
TIMEOUT = 30

# Discriminating subset: every detected-format class reachable among the
# 102 ledger members (wav / act->ffmpeg / gsrt / hcom), both r65/r66
# preemptor + lengate + dec controls, plus the out-of-ledger boundary
# carriers pinning the pipe-refusing and transport-invariant classes.
FIXTURES = [
    # tracked ledger members
    ("tracked", "corpus/artifacts/ui.wav"),
    ("tracked", "corpus/live/round-63/pair_route_84.wav"),
    ("tracked", "corpus/live/round-65/pair_preempt_act.wav"),
    ("tracked", "corpus/live/round-65/pair_preempt_gsrt.wav"),
    ("tracked", "corpus/live/round-65/pair_preempt_hcom.wav"),
    ("tracked", "corpus/live/round-65/pair_preempt_both.wav"),
    ("tracked", "corpus/live/round-66/pair_dec_act.wav"),
    ("tracked", "corpus/live/round-66/pair_dec_hcom.wav"),
    ("tracked", "corpus/live/round-66/pair_lengate_gsrt_24.wav"),
    ("tracked", "corpus/live/round-66/pair_lengate_gsrt_25.wav"),
    ("tracked", "corpus/live/round-66/pair_lengate_hcom_131.wav"),
    ("tracked", "corpus/live/round-66/pair_lengate_hcom_132.wav"),
    # boundary carriers (tracked in repo, not ledger rows)
    ("boundary", "corpus/live/r66-boundary/probes/g_txw_hcom.bin"),
    ("boundary", "corpus/live/r66-boundary/probes/p_smp_intact.bin"),
    ("boundary", "corpus/live/r66-boundary/probes/p_voc_intact.bin"),
    ("boundary", "corpus/live/r66-boundary/probes/a_wve_valid.bin"),
    ("boundary", "corpus/live/r66-boundary/probes/g_amrnb_hcom.bin"),
]


def sox_guarded(args, stdin=None, timeout=TIMEOUT):
    """Run sox in its own pgroup; on timeout killpg so bridge children
    (ffmpeg grandchildren inheriting our pipes) die with it.
    Returns (rc, stderr, timed_out)."""
    p = subprocess.Popen(args, stdin=stdin, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, start_new_session=True)
    timed_out = False
    try:
        _out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            _out, err = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            err = b""
    return p.returncode, err, timed_out


def parse(stderr: bytes, rc: int, timed_out: bool):
    text = stderr.decode(errors="replace")
    det = re.search(r"detected file format type `(\S+?)'", text)
    samp = re.search(r"Samples read:\s*(\d+)", text)
    lines = [l for l in text.splitlines() if "FAIL" in l or "WARN" in l]
    tail = lines[-1].split("sox ", 1)[-1][:100] if lines else "ok"
    if timed_out:
        tail = f"SCRIBE-TIMEOUT-{TIMEOUT}s-killpg | " + tail
    return (det.group(1) if det else "-", rc,
            int(samp.group(1)) if samp else -1, tail)


def run_file(path: Path):
    return sox_guarded(["sox", "-V4", str(path), "-n", "stat"])


def run_pipe(path: Path):
    cat = subprocess.Popen(["cat", str(path)], stdout=subprocess.PIPE)
    try:
        return sox_guarded(["sox", "-V4", "-", "-n", "stat"],
                           stdin=cat.stdout)
    finally:
        cat.stdout.close()
        cat.wait()


def run_redir(path: Path):
    with open(path, "rb") as fh:
        return sox_guarded(["sox", "-V4", "-", "-n", "stat"], stdin=fh)


def run_fifo(path: Path, fifo_path: Path):
    # sox's open(fifo, O_RDONLY) waits for a writer; then the parent's
    # blocking open-for-write pairs and cat streams the payload.
    p = subprocess.Popen(["sox", "-V4", str(fifo_path), "-n", "stat"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True)
    wr = open(fifo_path, "wb")
    cat = subprocess.Popen(["cat", str(path)], stdout=wr,
                           stderr=subprocess.DEVNULL)
    timed_out = False
    try:
        _out, err = p.communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            _out, err = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            err = b""
    finally:
        try:
            cat.wait(timeout=10)
        except subprocess.TimeoutExpired:
            cat.kill()
            cat.wait()
        wr.close()
    return p.returncode, err, timed_out


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    rows = ["class\tfixture\ttransport\tdetected\texit\tsamples\ttail"]
    for cls, rel in FIXTURES:
        path = ROOT / rel
        name = Path(rel).name
        legs = {}
        legs["file"] = run_file(path)
        legs["pipe"] = run_pipe(path)
        legs["redir"] = run_redir(path)
        fifo_path = SCRATCH / "runs" / f"{name}.fifo"
        if fifo_path.exists():
            fifo_path.unlink()
        os.mkfifo(fifo_path)
        try:
            legs["fifo"] = run_fifo(path, fifo_path)
        finally:
            fifo_path.unlink(missing_ok=True)
        for transport, (rc, err, to) in legs.items():
            logerr = (err or b"")
            if to:
                logerr += b"\nSCRIBE-OBSERVED: killed after timeout (transport hang)\n"
            (LOGS / f"{name}.{transport}.log").write_bytes(logerr)
            det, rc2, samp, tail = parse(err, rc, to)
            rows.append(f"{cls}\t{name}\t{transport}\t{det}\t{rc2}\t{samp}\t{tail}")
            print(rows[-1], flush=True)
    TSV.write_text("\n".join(rows) + "\n")


if __name__ == "__main__":
    sys.exit(main())
