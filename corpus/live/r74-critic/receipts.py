#!/usr/bin/env python3
"""r74 critic — permanent receipts for the 4 key cells.

Cells (member x {file,fifo}), mpv 0.41.0 + lavf 63.1.101, --ao=pcm raw u8:
  A hcom 1pkt   (r73 anchor)          -> expect rc2/0  pcm 0/3520
  B hcom 4pkt   (wound-shape mutant)  -> critic: rc2/0 pcm 0/134592  (corollary said rc0 head-trunc)
  C iss  6pkt   (dts>0+KEY class)     -> critic: rc0/0 pcm 8128/12192 (2 pkt lost on file)
  D acm  multi (NOGENSEARCH class)    -> critic: rc0/0 pcm 800/800   (NO fork; rule said fork)
Saves logs/pcm per leg under cells/, writes cells.tsv + sha256.
"""
import hashlib
import os
import re
import struct
import subprocess
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CELLS = HERE / "cells"
CELLS.mkdir(exist_ok=True)


def feed(fifo, data, hold=1.5):
    try:
        with open(fifo, "wb") as fh:
            fh.write(data)
            fh.flush()
            time.sleep(hold)
    except OSError:
        pass


def run(member: Path, tag: str, transport: str):
    data = member.read_bytes()
    out = CELLS / f"{tag}.{transport}.pcm"
    log = CELLS / f"{tag}.{transport}.log"
    for p in (out, log):
        if p.exists():
            p.unlink()
    argv = ["mpv", "--no-config", "--vo=null", "--ao=pcm",
            f"--ao-pcm-file={out}", "--ao-pcm-waveheader=no",
            "--audio-display=no", "--really-quiet", f"--log-file={log}"]
    fifo = None
    w = None
    if transport == "file":
        argv.append(str(member))
    else:
        fifo = CELLS / f"{tag}.fifo"
        if fifo.exists():
            fifo.unlink()
        os.mkfifo(fifo)
        w = threading.Thread(target=feed, args=(fifo, data), daemon=True)
        w.start()
        argv.append(str(fifo))
    try:
        p = subprocess.run(argv, capture_output=True, timeout=15)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    if w:
        w.join(timeout=5)
    if fifo and fifo.exists():
        fifo.unlink()
    text = log.read_text(errors="replace") if log.exists() else ""
    m = re.search(r"avformat_find_stream_info\(\) finished after (\d+) bytes", text)
    return {
        "tag": tag, "transport": transport, "member_sha": hashlib.sha256(data).hexdigest(),
        "member_bytes": len(data), "rc": rc,
        "pcm_bytes": out.stat().st_size if out.exists() else 0,
        "pcm_sha": hashlib.sha256(out.read_bytes()).hexdigest()[:16] if out.exists() else "-",
        "fsi_bytes": m.group(1) if m else "-",
        "refresh_seek": "refresh seek to" in text,
        "seek_failed": (re.search(r"Seek failed \(([^)]*)\)", text) or [None, None])[1] if "Seek failed" in text else "-",
        "no_data": "got EOF with no data before it" in text,
        "log_sha": hashlib.sha256(text.encode()).hexdigest()[:16],
    }


def build_iss(n_packets, name, pkt=512):
    hdr = " ".join(["IMA_ADPCM_Sound", str(pkt), "1", str(pkt * n_packets),
                    "0", "0", "1", "0", "1", str(n_packets)]) + " "
    p = HERE / name
    p.write_bytes(hdr.encode() + b"\x00" * (pkt * n_packets))
    return p


def build_apc(n_samples, name, payload=5120):
    hdr = b"CRYO" + b"_APC" + b"1.20"
    hdr += struct.pack("<II", n_samples, 44100)
    hdr += b"\x00" * 8
    hdr += struct.pack("<I", 0)          # 0 -> mono
    p = HERE / name
    p.write_bytes(hdr + b"\x00" * payload)
    return p


def build_adx(name):
    p = HERE / name
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=440:sample_rate=44100:duration=0.5",
                    "-ac", "1", "-c:a", "adpcm_adx", str(p)],
                   check=True, capture_output=True)
    return p


def main():
    members = [
        ("A_hcom_1pkt", HERE / "m1-hcom-600.wav"),
        ("B_hcom_4pkt", HERE / "c2-hcom-multipkt.wav"),
        ("C_iss_6pkt", HERE / "c3-iss-6pkt.iss"),
        ("D_acm_multi", HERE / "c5-acm-multi.acm"),
        ("E_adx_ctl", build_adx("c7-adx-control.adx")),
        ("F_apc_2pkt", build_apc(5120, "c8-apc-2pkt.apc")),
        ("G_iss_40pkt", build_iss(40, "c9-iss-40pkt.iss")),
    ]
    rows = []
    for tag, path in members:
        assert path.exists(), path
        for t in ("file", "fifo"):
            rows.append(run(path, tag, t))
    cols = ["tag", "transport", "rc", "pcm_bytes", "pcm_sha", "fsi_bytes",
            "refresh_seek", "seek_failed", "no_data", "member_bytes", "member_sha", "log_sha"]
    with open(HERE / "cells.tsv", "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]) for c in cols) + "\n")
    for r in rows:
        print(f"{r['tag']:12s} {r['transport']:4s} rc={r['rc']:>7} pcm={r['pcm_bytes']:>7} "
              f"fsi={r['fsi_bytes']:>6} seekfail={r['seek_failed']} nodata={r['no_data']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
