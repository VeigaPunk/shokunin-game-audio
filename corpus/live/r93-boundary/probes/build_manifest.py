#!/usr/bin/env python3
"""Build manifest.sha256 + RECEIPTS.md for corpus/live/r93-scout/."""
import hashlib
import os
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "manifest.sha256")
REC = os.path.join(HERE, "RECEIPTS.md")


def sha(p, n=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(n)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def walk(root):
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for f in sorted(fn):
            out.append(os.path.join(dp, f))
    return sorted(out)


def main():
    files = []
    for p in walk(HERE):
        rel = os.path.relpath(p, HERE)
        if rel in ("manifest.sha256", "RECEIPTS.md"):
            continue
        files.append((rel, os.path.getsize(p), sha(p)))
    with open(OUT, "w") as f:
        for rel, size, h in files:
            f.write("%s  %s\n" % (h, rel))
    total = sum(s for _, s, _ in files)
    lines = [
        "# r93-boundary receipts index",
        "",
        "Seat: EXECUTOR (boundary), round 93. Surface: the r93 scout's armed",
        "`ebur128` cells replayed under own-hog load and quiet-ish, plus the",
        "independent axes (PipeWire quantum/rate, CLI flag order, default-node",
        "state, sibling-seat presence). Canonical judgment belongs to the",
        "orchestrator; this seat measures and reports.",
        "",
        ("Generated %s. %d files, %.2f MB. Every path below is untracked scratch; "
         "nothing outside `corpus/live/r93-boundary/` was written except the round "
         "report `reports/round-93/r93-boundary.md`."
         % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), len(files), total / 1e6)),
        "",
        "## Receipts (JSON) — one per stage x condition x rep",
        "",
        "| file | what it holds |",
        "| --- | --- |",
        "| `receipts/recon_quiet_r1.json` | port table, notify/Props readout check, cadence, own vs foreign nodes |",
        "| `receipts/core_<cond>_r<N>.json` | the armed-cell replay: calibration, portmap, stereo/mix, notify-only modes, peaks, lufs2gain (+ same-leg Global/Gain check), ctlgrammar, gating, bit-exact passthrough |",
        "| `receipts/window_<cond>_r1.json` | max-window matrix + decay-length measurement |",
        "| `receipts/history_<cond>_r1.json` | Global through 5 s of silence, default vs max-history=2.0 |",
        "| `receipts/hist2_<cond>_r1.json` | two-burst eviction program |",
        "| `receipts/labels_<cond>_r1.json` | builtin label load matrix (debug/busy/sqrt/ramp/zeroramp/null/avg/sum/gain/nop) |",
        "| `receipts/ref_quiet_r1.json` | ffmpeg ebur128 + own reference + libebur128 witness on one Global leg |",
        "| `receipts/rate_<cond>_r1.json` | rate axis: stimulus rate vs sink rate vs graph rate |",
        "| `receipts/quantum_<cond>_r1.json` | clock.force-quantum axis (cadence + plateau), settings restored |",
        "| `receipts/frate_quiet_r1.json` | graph-rate axis via clock.force-rate + allowed-rates, restored and verified |",
        "| `receipts/flags_<cond>_r1.json` | argv-shape axis (module arg order, pw-play/pw-record flag order, reversed pw-link) |",
        "| `receipts/defaults_<cond>_r1.json` | default-node state axis (ambient vs own sink; restored and verified) |",
        "| `receipts/amp_<cond>_r1.json` | amplitude ladder vs own reference + libebur128 witness |",
        "| `receipts/freq_<cond>_r1.json` | K-weighting transfer ladder (40/100/1k/4k/10k) |",
        "| `receipts/scout_audit.json` | receipt-fidelity audit of `reports/round-93/r93-scout.md` against the scout's own receipts |",
        "| `receipts/witness_amp.json`, `witness_gating.json` | libebur128 witness scan over the SCOUT's frozen captures |",
        "| `receipts/analysis.json` | collapsed per-tag table over this seat's receipts |",
        "",
        "## Probes",
        "",
        "| file | role |",
        "| --- | --- |",
        "| `probes/r93blib.py` | bounded child runner (start_new_session + wall cap + killpg + RLIMIT_CORE=0), f32 WAV I/O, own synth, own BS.1770 reference, host snapshots |",
        "| `probes/r93bdriver.py` | the stage driver (13 stages); every leg = fresh sink + fresh module + fresh pw-play; arm failures retried bounded |",
        "| `probes/r93b_hog.py` | own CPU hog (PR_SET_NAME r93b_hog), wall-capped, killed by exact PID |",
        "| `probes/ebur_witness2.c` / `ebur_witness2` | independent witness: installed libebur128's own `ebur128_loudness_global` on a capture (full and silence-trimmed) |",
        "| `probes/witness_scan.py` | witness scan over a receipt's captures |",
        "| `probes/audit_scout.py` | receipt-fidelity audit of the scout report |",
        "| `probes/analyze.py` | cross-stage collapse over this seat's receipts |",
        "| `battery.sh quiet|load` | single-lane sequential batteries |",
        "",
        "## Notes",
        "",
        "- `scratch/` holds the stimuli (own f32 synth) and per-leg captured taps.",
        "- Sweeps use an exact-token selector (`r93b_in`, `r93b_fc_in`, `r93b_fc_out`,",
        "  `r93b_ref`, `r93b_rec`, `r93b_hogrec`, `r93b_fc,`, `r93b_hog.py`), never a",
        "  bare substring: the sibling lanes are r95b_*/r96b_*/r98b_* and at least one",
        "  foreign tool uses an `/tmp` path containing `r93b` (r82 F4 / r95 precedent).",
        "- Hog PIDs are recorded per stage (`hogs_start.pids`) and killed by exact PID.",
        "- No `pactl set-default-*` is left behind (the one axis leg restores and verifies).",
        "- Session metadata (`clock.force-quantum`, `clock.allowed-rates`, `clock.force-rate`)",
        "  is restored and verified in the same receipt.",
        "- Sibling lanes and foreign hog batteries were live throughout (see the report's",
        "  contention ledger).",
        "",
    ]
    with open(REC, "w") as f:
        f.write("\n".join(lines))
    print("manifest: %d files, %.2f MB" % (len(files), total / 1e6))
    print("receipts: %s" % REC)


if __name__ == "__main__":
    main()
