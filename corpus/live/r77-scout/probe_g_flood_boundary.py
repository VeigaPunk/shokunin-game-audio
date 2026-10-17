#!/usr/bin/env python3
"""R77 scout — bounded re-verification of two flood-adjacent findings.

(1) `arecord -D null` UNBOUNDED auto-rotates <name>.wav -> <name>-NN.wav at
    the 2 GiB wav limit. Measured file size is the sentinel 0x80000044, i.e.
    the data-chunk sentinel 0x80000000 + the 44-byte header. That names the
    `placeholder_80000000` class: it is arecord's 2 GiB split sentinel, not
    an arbitrary placeholder.
(2) The arecord sever shape is DEVICE-dependent, re-measured with the disk
    not full (the first attempt was invalidated by a full tmpfs).
"""
import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r77_probe import emit, inspect, mk, norm_err, out_kind  # noqa

TMP = mk()
BOUND = 0.35            # seconds of flood before SIGKILL
ROT = "r77rot"


def flood_rotation():
    """Unbounded -D null, killed at BOUND; report every rotation file."""
    base = os.path.join(TMP, ROT + ".wav")
    proc = subprocess.Popen(["arecord", "-D", "null", "-f", "cd", base],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    time.sleep(BOUND)
    proc.send_signal(signal.SIGKILL)
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        pass
    err = proc.stderr.read().decode(errors="replace")
    proc.stderr.close()
    files = []
    for f in sorted(os.listdir(TMP)):
        if f.startswith(ROT):
            p = os.path.join(TMP, f)
            insp = inspect(p) if os.path.getsize(p) > 0 else {"exists": True,
                                                              "bytes": 0}
            files.append({"name": f, "bytes": insp.get("bytes"),
                          "size_hex": hex(insp.get("bytes"))
                          if insp.get("bytes") else None,
                          "riff_size_field": insp.get("riff_size_field"),
                          "data_declared_field":
                              insp.get("data_declared_field"),
                          "data_declared": insp.get("data_declared"),
                          "out_kind": out_kind(insp)})
    return {"base_exists": os.path.exists(base), "rc": proc.returncode,
            "err_tail": norm_err(err), "rotation_files": files,
            "sentinel_expectation": hex(0x80000000 + 44)}


def sever_device(dev, sig, wait=1.2):
    p = os.path.join(TMP, f"dev_{dev.replace(':', '').replace(',', '')}"
                            f"_{sig}.wav")
    if os.path.exists(p):
        os.unlink(p)
    proc = subprocess.Popen(["arecord", "-D", dev, "-f", "cd", p],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    time.sleep(wait)
    proc.send_signal(getattr(signal, "SIG" + sig))
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=8)
    err = proc.stderr.read().decode(errors="replace")
    proc.stderr.close()
    insp = inspect(p)
    # any rotation siblings?
    sib = [f for f in os.listdir(TMP)
           if f.startswith(os.path.basename(p)[:-4] + "-")]
    return {"device": dev, "sig": sig, "rc": proc.returncode,
            "err_tail": norm_err(err),
            "base_out_kind": out_kind(insp), "base_bytes": insp.get("bytes"),
            "riff_size_field": insp.get("riff_size_field"),
            "data_declared_field": insp.get("data_declared_field"),
            "rotation_siblings": sorted(sib)[:6]}


def main():
    out = {"probe": "flood-boundary-r77", "tmp": TMP,
           "flood": flood_rotation(), "sever": {}}
    for dev in ("hw:0,0", "null", "sysdefault"):
        for sig in ("TERM", "KILL"):
            out["sever"][f"{dev}|{sig}"] = sever_device(dev, sig)
    # clean the flood before writing the receipt
    for f in sorted(os.listdir(TMP)):
        if f.startswith(ROT):
            try:
                os.unlink(os.path.join(TMP, f))
            except OSError:
                pass
    out["bytes_after_cleanup"] = sum(
        os.path.getsize(os.path.join(TMP, f)) for f in os.listdir(TMP)
        if os.path.isfile(os.path.join(TMP, f)))
    emit(out, "probe-flood-boundary-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
