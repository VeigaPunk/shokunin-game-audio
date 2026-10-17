#!/usr/bin/env python3
"""r74-scout: mpv file-vs-fifo matrix on hand-built iss/apc/acm members +
generatable adx/wv controls + the two canonical r73 controls.

Two legs per (member, arm):
  verdict: --ao=null          -> rc + lavf log fields
  decode : --ao=pcm           -> rc + raw PCM byte count (head-truncation
                                witness: same rc, fewer bytes on file arm)
Protocol: every leg bounded by `timeout -s KILL` semantics (subprocess
timeout -> SIGKILL); fifo legs use a fresh fifo named with the member
basename + a one-shot writer thread.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEMBERS = ROOT / "members"
FIFOS = ROOT / "fifos"
LOGS = ROOT / "logs"
RAW = ROOT / "raw"
TIMEOUT = 20
CANON = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live")

# label -> path
SETS = {
    "r74": {
        "iss_1pkt": MEMBERS / "sweep_iss_1pkt.iss",
        "iss_4pkt": MEMBERS / "sweep_iss_4pkt.iss",
        "apc_1pkt": MEMBERS / "sweep_apc_1pkt.apc",
        "apc_multi": MEMBERS / "sweep_apc_multi.apc",
        "acm_64blk": MEMBERS / "sweep_acm_64blk.acm",
        "adx": MEMBERS / "sweep_adx.adx",
        "wv": MEMBERS / "sweep_wv.wv",
    },
    "r74b": {
        "iss_40pkt": MEMBERS / "sweep_iss_40pkt.iss",
        "apc_3pkt": MEMBERS / "sweep_apc_3pkt.apc",
        "acm_2000blk": MEMBERS / "sweep_acm_2000blk.acm",
    },
    "canon": {
        "dec_hcom": CANON / "round-66/pair_dec_hcom.wav",
        "dec_act": CANON / "round-66/pair_dec_act.wav",
    },
}

MPV = ["mpv", "--no-config", "--vo=null", "--audio-display=no",
       "--really-quiet"]


def feed_fifo(fifo, data):
    try:
        with open(fifo, "wb") as fh:
            fh.write(data)
    except OSError as exc:      # reader vanished
        print("writer:", exc, file=sys.stderr)


def parse_log(text):
    out = {}
    m = re.search(r"Found '([^']+)' at score=(\d+) size=(\d+)", text)
    if m:
        out["found_format"], out["probe_score"], out["probe_size"] = (
            m.group(1), int(m.group(2)), int(m.group(3)))
    out["stream_not_seekable"] = "Stream is not seekable." in text
    out["refresh_seek"] = "refresh seek to" in text
    m = re.search(r"refresh seek to ([\d.]+)", text)
    if m:
        out["refresh_seek_to"] = m.group(1)
    out["seek_failed"] = bool(re.search(r"Seek failed \(([^)]+)\)", text))
    m = re.search(r"Seek failed \(([^)]+)\)", text)
    if m:
        out["seek_failed_str"] = m.group(1)
    m = re.search(r"finished playback, (.+) \(reason (\d+)\)", text)
    if m:
        out["playback"] = m.group(1)
        out["reason"] = int(m.group(2))
    m = re.search(r"Audio --aid=1[^\n]*", text)
    if m:
        out["audio_line"] = m.group(0).strip()
    return out


def run_leg(label, member, arm, decode, extra=()):
    data = member.read_bytes()
    log = LOGS / ("%s__%s__%s.log" % (label, arm, "dec" if decode else "ver"))
    pcm = RAW / ("%s__%s.raw" % (label, arm))
    for p in (log, pcm):
        if p.exists():
            p.unlink()
    argv = list(MPV)
    if decode:
        argv += ["--ao=pcm", "--ao-pcm-file=%s" % pcm,
                 "--ao-pcm-waveheader=no"]
    else:
        argv += ["--ao=null"]
    argv += list(extra)
    if arm == "file":
        argv.append(str(member))
        fifo = writer = None
    else:
        fifo = FIFOS / ("%s__%s.fifo" % (label, arm))
        if fifo.exists():
            fifo.unlink()
        os.mkfifo(fifo)
        writer = threading.Thread(target=feed_fifo, args=(fifo, data),
                                  daemon=True)
        writer.start()
        argv.append(str(fifo))
    argv += ["--log-file=%s" % log]
    t0 = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=TIMEOUT)
        rc, timed_out = proc.returncode, False
    except subprocess.TimeoutExpired:
        rc, timed_out = -9, True
    wall = time.monotonic() - t0
    text = log.read_text(errors="replace") if log.exists() else ""
    rec = {
        "member": label, "arm": arm, "leg": "decode" if decode else "verdict",
        "rc": rc, "timed_out": timed_out, "wall_s": round(wall, 3),
        "input_bytes": len(data),
        "input_sha256": hashlib.sha256(data).hexdigest(),
    }
    rec.update(parse_log(text))
    rec["pcm_bytes"] = pcm.stat().st_size if pcm.exists() else 0
    if fifo is not None:
        writer.join(timeout=2.0)
        rec["writer_alive"] = writer.is_alive()
        try:
            fifo.unlink()
        except OSError:
            pass
    return rec


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "r74"
    out = []
    for label, member in SETS[which].items():
        for arm in ("file", "fifo"):
            for decode in (False, True):
                rec = run_leg(label, member, arm, decode)
                out.append(rec)
                print("%-10s %-4s %-7s rc=%-3s pcm=%-6d found=%-6s "
                      "notseek=%-5s refresh=%-5s seekfail=%-5s playback=%s"
                      % (label, arm, rec["leg"], rec["rc"], rec["pcm_bytes"],
                         rec.get("found_format"), rec["stream_not_seekable"],
                         rec["refresh_seek"], rec["seek_failed"],
                         rec.get("playback")), flush=True)
    (ROOT / "runs").mkdir(exist_ok=True)
    (ROOT / "runs" / ("mpv-matrix-%s.json" % which)).write_text(
        json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
