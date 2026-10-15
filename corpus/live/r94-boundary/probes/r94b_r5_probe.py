#!/usr/bin/env python3
"""r94b focused probe — the `-v` alias-rejection claim in r94-scout §1.5 claim 5.

The scout report text says: "Default (`-h`) and `-v` reject it at -84/-130 dB".
Its own receipts contain no 23 kHz `-v` leg.  This probe measures the claim
directly, at higher precision and with an independent band definition, in both
passes, with fresh processes.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r94b_lib as L  # noqa: E402

PASS = os.environ.get("R94B_PASS", "quiet")
HOGS = int(os.environ.get("R94B_HOGS", "0"))
J = L.SCRATCH / "r94b_stim_j.wav"          # 23 kHz, 0.5 FS, 48 kHz, 0.25 s
H = L.SCRATCH / "r94b_stim_h.wav"          # 20 kHz control

OPTS = [("default", []), ("q", ["-q"]), ("l", ["-l"]), ("m", ["-m"]), ("h", ["-h"]),
        ("v", ["-v"]), ("u", ["-u"]), ("a", ["-a"]), ("q_a", ["-q", "-a"]),
        ("v_a", ["-v", "-a"]), ("u_a", ["-u", "-a"])]


def spectrum_metrics(path):
    arr, meta = L.read_wav(path)
    v = arr[:, 0]
    rate = meta["rate"]
    win = np.hanning(v.size)
    spec = np.abs(np.fft.rfft(v * win)) * 2.0 / (win.sum() * 0.5)
    freqs = np.fft.rfftfreq(v.size, 1.0 / rate)
    out = {"frames": meta["frames"], "rate": rate,
           "peak_db": round(L.peak_db(arr), 6),
           "rms_db": round(L.rms_db(arr), 6)}
    # narrow band levels (own reference, 10 Hz half-width)
    for f0 in (997.0, 20000.0, 21000.0, 21100.0, 21500.0, 22000.0):
        band = (freqs >= f0 - 10) & (freqs <= f0 + 10)
        if band.any():
            pk = float(spec[band].max())
            out[f"band10hz_{int(f0)}"] = round(20 * np.log10(pk), 6) if pk > 0 else None
    # strongest component anywhere in the output passband and the total out-of-band energy
    passb = freqs <= 20000.0
    out["max_in_band_0_20k_db"] = round(float(20 * np.log10(spec[passb].max())), 6) if passb.any() else None
    out["max_spectral_peak_db"] = round(float(20 * np.log10(spec.max())), 6)
    out["max_spectral_peak_hz"] = round(float(freqs[int(np.argmax(spec))]), 3)
    # energy above 20 kHz relative to the passband (alias residue measure)
    hi = freqs > 20000.0
    e_hi = float(np.sum(spec[hi] ** 2))
    e_lo = float(np.sum(spec[passb] ** 2))
    out["energy_above_20k_db_rel_passband"] = round(10 * np.log10(e_hi / e_lo), 6) if e_lo > 0 else None
    return out


def run(stim, opt_name, opts, rep):
    out = L.SCRATCH / f"r94b_{PASS}_r5_{stim.stem}_{opt_name}_r{rep}.wav"
    if out.exists():
        out.unlink()
    argv = [L.SOX, "-D", str(stim), str(out), "rate", *opts, "44100"]
    leg = L.RUNS / PASS / "r5" / f"{stim.stem}_{opt_name}" / f"rep{rep}"
    meta = L.run_bounded(argv, leg, wall=15.0, out_path=out)
    m = {}
    if out.exists():
        m = spectrum_metrics(out)
    return {"argv": argv, "rc": meta["rc"], "out_sha256": meta["out_sha256"],
            "stderr_head": meta["stderr_head"].strip(), "metrics": m,
            "loadavg1": meta["loadavg1_before"]}


def main():
    t0 = time.time()
    warmup_s = float(os.environ.get("R94B_HOG_WARMUP", "0"))
    hogs = L.HogSet(HOGS).start() if HOGS > 0 else None
    if hogs is not None and warmup_s > 0:
        print(f"  warming {HOGS} hogs for {warmup_s:g}s ...", flush=True)
        hogs.warmup(warmup_s)
    try:
        cells = []
        for stim, label in ((J, "23k"), (H, "20k")):
            for opt_name, opts in OPTS:
                rows = [run(stim, opt_name, opts, rep) for rep in range(3)]
                shas = [r["out_sha256"] for r in rows if r["out_sha256"]]
                cells.append({"family": "R5", "name": f"{label}_{opt_name}",
                              "argv": rows[0]["argv"],
                              "rcs": [r["rc"] for r in rows],
                              "n_distinct_shas": len(set(shas)), "reps_n": 3,
                              "stable": len(set(shas)) == 1 and len(shas) == 3,
                              "metrics": rows[0]["metrics"], "reps": rows,
                              "stderr_head": rows[0]["stderr_head"]})
                print(f"  {label}_{opt_name:8s} rc={rows[0]['rc']} "
                      f"band21.1k={rows[0]['metrics'].get('band10hz_21100')} "
                      f"peak={rows[0]['metrics'].get('peak_db')} "
                      f"sha={str(rows[0]['out_sha256'])[:12]}", flush=True)
        payload = {"pass": PASS, "hogs": HOGS, "host": L.host_context(),
                   "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
                   "notes": [{"stimuli": {"r94b_stim_j.wav": L.sha256_file(J),
                                          "r94b_stim_h.wav": L.sha256_file(H)}},
                             {"purpose": "attack r94-scout §1.5 claim 5 '-v rejects it at -130 dB'; "
                                         "band = 10 Hz half-width windowed DFT, own reader"}],
                   "cells": cells}
        if hogs is not None:
            payload["hog_set"] = hogs.receipt()
        p = L.write_receipt(f"r5-{PASS}", payload)
        print(f"[r5-{PASS}] {len(cells)} cells -> {p}", flush=True)
    finally:
        if hogs is not None:
            hogs.stop()
            print(f"  hogs stopped: alive={hogs.alive()}", flush=True)


if __name__ == "__main__":
    main()
