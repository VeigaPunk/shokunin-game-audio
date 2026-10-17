#!/usr/bin/env python3
"""r74 critic — independent no-seek fork-shape probe.

Own member builder (from FFmpeg n9.0.1 source read this session) + own mpv
runner. Deliberately not importing measure_audio.py or the reviewer's
mpv_matrix.py so agreement/disagreement is evidence, not shared code.

Legs per member: file | fifo.  Measurement: rc + decoded bytes written by
--ao=pcm (raw u8) + parsed lavf log fields.

Predicted (critic, from seek.c n9.0.1):
  hcom 1pkt / hcom multi : file rc2 zero-data  (dts=NOPTS -> seek_frame_generic
                            loop reads to EOF; AVFMT_NOGENSEARCH unset)
  iss multi              : file rc0 head-truncated (first pkt consumed, dts>0+KEY)
  acm multi              : NO fork (AVFMT_NOGENSEARCH -> av_seek_frame -1
                            immediately, zero consumption)
"""
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TIMEOUT = 15


def build_hcom_multi():
    """600 B hcom-detected member + 16384 zero bytes -> 4 x 4096 B packets."""
    src = HERE.parent / "round-66" / "pair_dec_hcom.wav"
    data = src.read_bytes() + b"\x00" * 16384
    p = HERE / "c2-hcom-multipkt.wav"
    p.write_bytes(data)
    return p


def build_iss(n_packets, name, pkt=512):
    hdr = " ".join(["IMA_ADPCM_Sound", str(pkt), "1", str(pkt * n_packets),
                    "0", "0", "1", "0", "1", str(n_packets)]) + " "
    p = HERE / name
    p.write_bytes(hdr.encode() + b"\x00" * (pkt * n_packets))
    return p


def build_acm(n_samples, name, subformat=0x7700, payload=2380):
    hdr = bytes((0x97, 0x28, 0x03, 0x01))
    hdr += struct.pack("<I", n_samples)
    hdr += struct.pack("<H", 1)
    hdr += struct.pack("<H", 44100)
    hdr += struct.pack("<H", subformat)
    p = HERE / name
    p.write_bytes(hdr + b"\x00" * payload)
    return p


def feed(fifo, data, hold):
    try:
        with open(fifo, "wb") as fh:
            fh.write(data)
            fh.flush()
            time.sleep(hold)
    except OSError:
        pass


def parse_log(text):
    def g(pat, grp=1):
        m = re.search(pat, text)
        return m.group(grp) if m else None
    return {
        "detected": g(r"Detected file format: (\S+) \(libavformat\)"),
        "probe_score": g(r"Found '([^']+)' at score=(\d+)", 2),
        "fsi_bytes": g(r"avformat_find_stream_info\(\) finished after (\d+) bytes"),
        "not_seekable": "Stream is not seekable" in text,
        "refresh_seek": "refresh seek to" in text,
        "seek_failed": g(r"Seek failed \(([^)]*)\)"),
        "no_data": "got EOF with no data before it" in text,
        "verdict": g(r"finished playback, (.*)$"),
        "eof_reached": "EOF reached" in text,
    }


def run_leg(member: Path, transport: str):
    data = member.read_bytes()
    with tempfile.TemporaryDirectory(prefix="r74c-") as tmp:
        tmp = Path(tmp)
        out = tmp / "pcm.raw"
        log = tmp / "mpv.log"
        argv = ["mpv", "--no-config", "--vo=null", "--ao=pcm",
                f"--ao-pcm-file={out}", "--ao-pcm-waveheader=no",
                "--audio-display=no", "--really-quiet", f"--log-file={log}"]
        kw = {}
        w = None
        if transport == "file":
            argv.append(str(member))
        elif transport == "fifo":
            fifo = tmp / member.name
            os.mkfifo(fifo)
            w = threading.Thread(target=feed, args=(fifo, data, 1.5), daemon=True)
            w.start()
            argv.append(str(fifo))
        try:
            p = subprocess.run(argv, capture_output=True, timeout=TIMEOUT, **kw)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            rc = "TIMEOUT"
        if w is not None:
            w.join(timeout=5)
        text = log.read_text(errors="replace") if log.exists() else ""
        leg = {"transport": transport, "rc": rc,
               "pcm_bytes": out.stat().st_size if out.exists() else 0}
        leg.update(parse_log(text))
        return leg


def main():
    members = [
        ("hcom-1pkt", HERE / "m1-hcom-600.wav"),
        ("hcom-4pkt", build_hcom_multi()),
        ("iss-6pkt", build_iss(6, "c3-iss-6pkt.iss")),
        ("iss-1pkt", build_iss(1, "c4-iss-1pkt.iss")),
        ("acm-multi", build_acm(400, "c5-acm-multi.acm")),
        ("acm-multi-subfmt0", build_acm(400, "c6-acm-multi-s0.acm", subformat=0)),
    ]
    results = {}
    for name, path in members:
        legs = {t: run_leg(path, t) for t in ("file", "fifo")}
        results[name] = {"path": str(path), "size": path.stat().st_size,
                         "legs": legs}
        f, q = legs["file"], legs["fifo"]
        print(f"{name:22s} file: rc={f['rc']:>7} pcm={f['pcm_bytes']:>7} "
              f"seekfail={f['seek_failed']} nodata={f['no_data']} | "
              f"fifo: rc={q['rc']:>7} pcm={q['pcm_bytes']:>7} "
              f"notseek={q['not_seekable']}")
        sys.stdout.flush()
    (HERE / "probe-results.json").write_text(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
