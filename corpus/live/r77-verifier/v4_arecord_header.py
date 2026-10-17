#!/usr/bin/env python3
"""r77 verifier — independent re-derivation of arecord's OPEN-TIME,
BOUND-DERIVED header (claim 4) and the cheap falsifier of
"0x80000000 == the 2 GiB split sentinel".

Law under test: `-d N` writes a size field of N x 192000 DATA bytes at open
(48 kHz x 2ch x 16-bit); `-s S` writes S x 4; unbounded writes 0x80000000.
A KILL leaves that prediction; a TERM finalizes and patches it to truth.

Every leg is <= 0.5 MB (0.5-2.5 s of paced hw capture), serialized with an
ALSA release settle between legs.
"""
import importlib.util
import json
import re
import signal
import subprocess
import tempfile
import time
from pathlib import Path

_here = Path(__file__).with_name("v1_lattice.py")
_spec = importlib.util.spec_from_file_location("v1", _here)
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)
_r = Path(__file__).with_name("v3_readers.py")
_spec2 = importlib.util.spec_from_file_location("v3", _r)
v3 = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(v3)

OUT = v1.OUT
BYTES_PER_SECOND = 192000


def hw_device():
    p = subprocess.run(["arecord", "-l"], capture_output=True, text=True,
                       timeout=15)
    m = re.search(r"card (\d+): .*?device (\d+):", p.stdout, re.S)
    return f"hw:{m.group(1)},{m.group(2)}" if m else None


def leg(name, extra, sig, wait_s, tmp, dev):
    argv = ["arecord", "-D", dev, "-f", "S16_LE", "-r", "48000", "-c", "2",
            "-t", "wav", *extra]
    rec = v3.wound(name, argv, sig, tmp, wait_s=wait_s)
    rec["bound_flags"] = list(extra)
    rec["device"] = dev
    return rec


def main():
    dev = hw_device()
    entry = {"probe": "r77-verifier arecord open-header law",
             "device": dev, "bytes_per_second": BYTES_PER_SECOND,
             "legs": {}, "failures": []}
    if not dev:
        entry["blocked"] = "no ALSA capture device enumerated"
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "v4_arecord_header.json").write_text(
            json.dumps(entry, indent=2) + "\n")
        print(json.dumps({"receipt": str(OUT / "v4_arecord_header.json"),
                          "failures": entry["failures"]}))
        return
    with tempfile.TemporaryDirectory(prefix="r77v-arec-") as tmp:
        for name, extra, sig, wait_s in (
                ("d3_kill_early", ("-d", "3"), signal.SIGKILL, 0.5),
                ("d5_kill_early", ("-d", "5"), signal.SIGKILL, 0.5),
                ("d12_kill_early", ("-d", "12"), signal.SIGKILL, 0.5),
                ("d12_kill_late", ("-d", "12"), signal.SIGKILL, 2.5),
                ("s300k_kill", ("-s", "300000"), signal.SIGKILL, 0.5),
                ("unbounded_kill", (), signal.SIGKILL, 1.0),
                ("d3_term", ("-d", "3"), signal.SIGTERM, 0.5)):
            time.sleep(1.0)          # ALSA release settle between legs
            entry["legs"][name] = leg(name, extra, sig, wait_s, tmp, dev)
    f = entry["failures"]
    for name, want_bytes in (("d3_kill_early", 3 * BYTES_PER_SECOND),
                             ("d5_kill_early", 5 * BYTES_PER_SECOND),
                             ("d12_kill_early", 12 * BYTES_PER_SECOND),
                             ("d12_kill_late", 12 * BYTES_PER_SECOND),
                             ("s300k_kill", 300000 * 4)):
        lg = entry["legs"][name]
        if lg.get("early_exit_code") is not None:
            f.append(f"{name}: early exit {lg['early_exit_code']} — not a "
                     f"wound verdict")
            continue
        got = lg.get("file", {}).get("data_declared")
        if got != want_bytes:
            f.append(f"{name}: expected the bound-derived declaration "
                     f"{want_bytes} B, got {got}")
        if lg.get("file", {}).get("data_finalized") is not False:
            f.append(f"{name}: a KILL must leave the unfinalized open header")
    ub = entry["legs"]["unbounded_kill"]
    # the OPEN-TIME declaration is the DATA chunk's size field (that is what
    # the arm's `data_declared_field` leaf classifies), not the RIFF size.
    if ub.get("file", {}).get("data_declared") != 0x80000000:
        f.append("unbounded_kill: expected the 0x80000000 open-time data "
                 f"declaration, got {ub.get('file', {}).get('data_declared')}")
    if ub.get("file", {}).get("bytes", 1 << 40) < 100000:
        f.append("unbounded_kill: the placeholder witness must be a SMALL "
                 "file — that is the falsifier of '0x80000000 == split "
                 "sentinel'")
    term = entry["legs"]["d3_term"]
    if term.get("file", {}).get("data_finalized") is not True or \
            term.get("file", {}).get("data_declared") != \
            term.get("file", {}).get("data_actual"):
        f.append("d3_term: TERM must finalize and patch the size field")
    entry["inflation"] = {
        name: round(want / max(entry["legs"][name].get("file", {}).get(
            "data_actual", 1), 1), 2)
        for name, want in (("d12_kill_early", 12 * BYTES_PER_SECOND),
                           ("d12_kill_late", 12 * BYTES_PER_SECOND),
                           ("d3_kill_early", 3 * BYTES_PER_SECOND),
                           ("s300k_kill", 300000 * 4))}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "v4_arecord_header.json").write_text(
        json.dumps(entry, indent=2) + "\n")
    print(json.dumps({"receipt": str(OUT / "v4_arecord_header.json"),
                      "failures": entry["failures"]}))


if __name__ == "__main__":
    main()
