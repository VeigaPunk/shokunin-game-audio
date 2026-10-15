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
        "# r93-scout receipts index",
        "",
        "Seat: SCOUT (leaf), round 93. Surface: **`ebur128`** — the SPA",
        "filter-graph loudness node of `libpipewire-module-filter-chain`",
        "(PipeWire 1.6.8), measured against an own BS.1770 reference and an",
        "ffmpeg `ebur128` cross-witness.",
        "",
        "Generated %s. %d files, %.2f MB. Every path below is untracked scratch; "
        "nothing outside `corpus/live/r93-scout/` was written except the round report."
        % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), len(files), total / 1e6),
        "",
        "## Receipts (JSON) — one per stage; every leg triple-bounded",
        "",
        "| file | stage | what it holds |",
        "| --- | --- | --- |",
        "| `receipts/recon1.json` | recon1 | ebur128 port table (PIPEWIRE_DEBUG=3), load shape, node params |",
        "| `receipts/recon2.json` | recon2 | pw-cli id/enum-params discovery (one-shot races) |",
        "| `receipts/recon3.json` | recon3 | enum-params under a live tone |",
        "| `receipts/recon4.json` | recon4 | Props param has no LUFS keys; pw-dump mid-tone |",
        "| `receipts/recon5.json` | recon5 | **notify -> debug:Control log readout proven** + first label probes |",
        "| `receipts/refflat.json` | refflat | ffmpeg ebur128 cross-witness + own reference on the stimulus |",
        "| `receipts/portmap.json` | portmap | 7 input ports x {Momentary,Global} x 3 reps: channel-map bug |",
        "| `receipts/amp.json` | amp | amplitude ladder vs own reference (6 levels, 3 reps) |",
        "| `receipts/freq.json` | freq | K-weighting transfer (40/100/1k/4k/10k, 3 reps) |",
        "| `receipts/stereo.json` | stereo | FL+FR / FL-tone+FR-silence / mono FL / mono FR x 2 readouts x 3 reps |",
        "| `receipts/modes.json` | modes | notify-only coupling (Range/Peak/Window/Global/Momentary) + passthrough |",
        "| `receipts/window.json` | window | max-window matrix (absent/0.05/0.4/1.0/2.0/5.0 s), decay-length law |",
        "| `receipts/history.json` | history | Global through silence, default vs max-history=2.0 |",
        "| `receipts/hist2.json` | hist2 | two-burst program: max-history eviction law |",
        "| `receipts/peaks.json` | peaks | Peak/True Peak per input port (index bug) |",
        "| `receipts/lufs2gain.json` | lufs2gain | gain law, target clamp, silence, audio-domain ratio |",
        "| `receipts/l2gcheck.json` | l2gcheck | Global+Gain in one leg (resolves the m100 anomaly) |",
        "| `receipts/ctlgrammar.json` | ctlgrammar | control-key quoting: raw vs quoted, verbatim error |",
        "| `receipts/edge.json` | edge | config error classes, stream/graph port mismatch |",
        "| `receipts/labels.json` | labels | 12-label load matrix (6 omitted by r92 + the 6 absent strings) |",
        "| `receipts/labels2.json` | labels2 | `null` label shapes |",
        "| `receipts/nullprobe.json` / `nullprobe2.json` / `nullprobe3.json` | nullprobe | verbatim load output for `label=null` |",
        "| `receipts/passthrough.json` | passthrough | bit-exact audio copy witness (aligned dual tap) |",
        "| `receipts/gating.json` | gating | relative-gate semantics, loud/quiet/loud + histogram arm |",
        "| `receipts/mix.json` | mix | unequal stereo channels: dB-mean law, relative-gate exclusion |",
        "| `receipts/ebur_witness.txt` | C witness | host libebur128 1.2.6 API semantics (init modes, window units, peak index, set_channel) |",
        "",
        "## Probes",
        "",
        "| file | role |",
        "| --- | --- |",
        "| `probes/pwlib93.py` | own bounded runner (killpg + wall cap + byte cap + RLIMIT_CORE=0), own f32 WAV I/O, own synth, own libebur128-matched K-weighting + gating reference |",
        "| `probes/r93driver.py` | the stage driver (24 stages, stage = argv[1], reps = argv[2]) |",
        "| `probes/recon1.py`..`recon5.py` | discovery legs (topology, readout hunt, readout proof) |",
        "| `probes/ebur_witness.c` | C harness against the installed libebur128 (compiled with `-lebur128 -lm`) |",
        "| `probes/nullprobe.py` | verbatim `label=null` load output |",
        "| `probes/analyze.py` | cross-stage summary over the receipts (read-only) |",
        "| `run_all.sh`, `run_all2.sh`, `run_all3.sh` | sequential stage batteries (single lane) |",
        "",
        "## Sources read",
        "",
        "`sources/` holds the version-matched upstream sources fetched for this seat",
        "(PipeWire 1.6.8 tag: `module-filter-chain.c`, `filter-graph.c`,",
        "`plugin_ebur128.c`, `plugin_builtin.c`; libebur128 v1.2.6 `ebur128.c`),",
        "with `sources/FETCHED-SOURCES.sha256`. On-disk version-matched artifacts",
        "read: the 1.6.8 filter-chain man page, `/usr/include/ebur128.h`,",
        "`/usr/lib/spa-0.2/filter-graph/*` strings/ldd, the installed",
        "`libspa-filter-graph-plugin-ebur128.so` (objdump -d), `pactl`/`pw-cli`",
        "output. **Source vs binary divergence flagged in the report (max-window",
        "unit hack): the measured law is authoritative.**",
        "",
        "## Notes",
        "",
        "- `scratch/` holds the stimuli (own f32 synth) and the captured WAVs.",
        "- No sibling fixture (`corpus/fixtures/measure_audio.py`) was read, imported or executed.",
        "- Teardown: every mutating leg unloads its own module by index verified against the",
        "  seat name; each stage sweeps and asserts zero r93s nodes/modules/processes;",
        "  the final host check is clean and the defaults are unchanged.",
        "- Sibling lanes were live throughout (recorded in the report's contention ledger).",
        "",
    ]
    with open(REC, "w") as f:
        f.write("\n".join(lines))
    print("manifest: %d files, %.2f MB" % (len(files), total / 1e6))
    print("receipts: %s" % REC)


if __name__ == "__main__":
    main()
