#!/usr/bin/env python3
"""r73 verifier independent replay of the frontier-pipewire consumer claims.

Seat: verifier (LEAF). Writes only inside corpus/live/r73-verifier/.
Independent of the author's fixture code — drives pw-cat + mpv directly,
file arm and fifo arm (writer = one-shot `cat member > fifo`, then close).

Bounded everywhere with timeout -s KILL (frontier: pw-cat open-block
survives SIGTERM). Verdict keys on (rc, normalized stderr/log tail).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
SCRATCH = REPO / "corpus/live/r73-verifier"
MEMBERS = {
    "dec_act": REPO / "corpus/live/round-66/pair_dec_act.wav",
    "dec_hcom": REPO / "corpus/live/round-66/pair_dec_hcom.wav",
    "lengate_gsrt_24": REPO / "corpus/live/round-66/pair_lengate_gsrt_24.wav",
    "lengate_gsrt_25": REPO / "corpus/live/round-66/pair_lengate_gsrt_25.wav",
    "lengate_hcom_131": REPO / "corpus/live/round-66/pair_lengate_hcom_131.wav",
    "lengate_hcom_132": REPO / "corpus/live/round-66/pair_lengate_hcom_132.wav",
    "posttable_nomatch": REPO / "corpus/live/round-68/posttable_nomatch.wav",
    "txw_piperefuse": REPO / "corpus/live/round-68/txw_piperefuse.wav",
    "extsuffix_wav": REPO / "corpus/live/round-69/extsuffix_nomatch.wav",
    "extsuffix_bin": REPO / "corpus/live/round-69/extsuffix_nomatch.bin",
    "extsuffix_txw": REPO / "corpus/live/round-69/extsuffix_nomatch.txw",
    "extsuffix_f32": REPO / "corpus/live/round-69/extsuffix_nomatch.f32",
    "extsuffix_snd": REPO / "corpus/live/round-69/extsuffix_nomatch.snd",
}
TIMEOUT = 30  # playback-paced: longest member ~4 s audio; 30 s headroom


def norm_err(text, path):
    """Last 2 non-empty lines, path/ASLR-normalized (pw-cat emits a
    'sndfile: ... <reason>' line then a generic 'open failed' line)."""
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        return None
    t = " | ".join(lines[-2:])
    t = t.replace(str(path), "<input>")
    t = re.sub(r" @ 0x[0-9a-fA-F]+", "", t)
    return t[-300:]


def feed_fifo(fifo, data):
    try:
        with open(fifo, "wb") as w:
            w.write(data)
    except OSError:
        pass


def run_leg(argv, path=None, log_file=None, env=None):
    t0 = time.monotonic()
    p = subprocess.run(argv, capture_output=True, text=True,
                       timeout=TIMEOUT, env=env)
    wall = time.monotonic() - t0
    err_tail = norm_err(p.stderr, path) if p.stderr else None
    log_tail = None
    if log_file and Path(log_file).exists():
        log_tail = norm_err(Path(log_file).read_text(errors="replace"), path)
    return {"rc": p.returncode, "wall_s": round(wall, 2),
            "stderr_tail": err_tail, "log_tail": log_tail}


def pwcat_file(path):
    return run_leg(["timeout", "-s", "KILL", str(TIMEOUT),
                    "pw-cat", "-p", str(path)], path)


def pwcat_fifo(path):
    data = path.read_bytes()
    with tempfile.TemporaryDirectory(prefix="r73v-pwcat-") as tmp:
        fifo = Path(tmp) / ("f_" + path.name)
        os.mkfifo(fifo)
        w = threading.Thread(target=feed_fifo, args=(fifo, data), daemon=True)
        w.start()
        r = run_leg(["timeout", "-s", "KILL", str(TIMEOUT),
                     "pw-cat", "-p", str(fifo)], path)
        w.join(timeout=5)
    return r


def mpv_leg(target, path, tag):
    log = SCRATCH / f"mpv-{tag}-{path.name}.log"
    log.unlink(missing_ok=True)
    return run_leg(["timeout", "-s", "KILL", str(TIMEOUT),
                    "mpv", "--no-config", "--vo=null", "--ao=null",
                    "--audio-display=no", "--really-quiet",
                    f"--log-file={log}", str(target)], path, log_file=log)


def mpv_file(path):
    return mpv_leg(path, path, "file")


def mpv_fifo(path):
    data = path.read_bytes()
    with tempfile.TemporaryDirectory(prefix="r73v-mpv-") as tmp:
        fifo = Path(tmp) / ("f_" + path.name)
        os.mkfifo(fifo)
        w = threading.Thread(target=feed_fifo, args=(fifo, data), daemon=True)
        w.start()
        r = mpv_leg(fifo, path, "fifo")
        w.join(timeout=5)
    return r


def main():
    out = {}
    for member, path in MEMBERS.items():
        ent = {"path": str(path.relative_to(REPO)),
               "pwcat": {"file": pwcat_file(path),
                         "fifo": pwcat_fifo(path)},
               "mpv": {"file": mpv_file(path),
                       "fifo": mpv_fifo(path)}}
        out[member] = ent
        print(f"{member}: pwcat file={ent['pwcat']['file']['rc']} "
              f"fifo={ent['pwcat']['fifo']['rc']} | "
              f"mpv file={ent['mpv']['file']['rc']} "
              f"fifo={ent['mpv']['fifo']['rc']}", flush=True)
    (SCRATCH / "consumer-matrix-verifier.json").write_text(
        json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
