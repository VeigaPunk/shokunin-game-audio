# Round 16 executor — reverse 180 Hz fixture

## Candidate and recipe

Created `.shokunin/audio/corpus/live/round-16/reverse180_candidate.wav` with Python's `wave` writer: mono PCM16 little-endian, 48,000 Hz, 192,000 frames. For each `n` in `0..191999`, `t=n/48000`; sample is `round(clip(A[n] * sin(2*pi*180*t), -1, 1) * 32767)`, where `A[n]=0.05` for `n<96000`, else `0.015`. Thus the phase continues through the midpoint; no fade or added noise. File size is 384,044 bytes. SHA-256 of the complete WAV bytes: `c04441ef1ef6c02970e0c946efe0c750b19d3f41ef26865ce37e608ecda4e7d8`.

This is an original scratch candidate, not a builder/runner-integrated probe. The first-half `.05`, second-half `.015` amplitudes were synthesis targets; decoded measurements below are the evidence.

## Independent decoded-sample measurements

Decoded the written PCM16 payload to normalized samples (integer / 32768); computed the whole-file FFT centroid, RMS, peak, endpoint delta and endpoint slope using the existing fixture definitions; computed the two 96,000-sample 180 Hz FFT-bin amplitudes and the internal join gap/slope using `measure_audio.py`'s definitions.

| Check | Result | Existing criterion | Result |
|---|---:|---:|---|
| Format / length | 48 kHz, mono, 192,000 frames (4.000 s) | 48 kHz mono, 4 s ±1 ms | pass |
| Whole-file peak | 0.04998779297 FS | `<0.95` | pass |
| Whole-file RMS | 0.02609973710 FS (`-31.667 dBFS`) | `>=0.001` | pass |
| Whole-file centroid | 277.9514 Hz | stem-layer-alt 100–2000 Hz | pass |
| Outer endpoint gap | 0.00036621094 FS | `<=0.03` | pass |
| Outer endpoint slope mismatch | 0.00085449219 FS/sample | `<=0.001` | pass |
| 180 Hz first/second component amplitudes | 0.04999787163 / 0.01499992158 FS | each `>=0.01` FS | valid |
| Per-section RMS | 0.03535383511 / 0.01060654968 FS | each `>=0.001` FS | valid |
| Signed contrast `20log10(second/first)` | **-10.4572505721 dB** | pass iff `>=6 dB` | **fail** |
| Internal join adjacent-sample gap | 0.00119018555 FS | `<=0.03` | pass |
| Internal join side-slope mismatch | 0.00079345703 FS/sample | `<=0.001` | pass |

All measured generic and outer checks, validity checks, and internal join checks pass; the contrast gate is the sole criterion failure. No failed fits were attempted. These are numeric fixture-proxy results only, not evidence about audible transitions, engine behavior, or production use.

## Commands run and exits

- `cd /home/vgpnk/Projects/prymeagnt/audio && sha256sum .shokunin/audio/corpus/live/round-16/reverse180_candidate.wav` — exit **0**; hash as above.
- `cd /home/vgpnk/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**; normal-mode receipt `.shokunin/audio/corpus/live/runs/20261012T185633816305Z-normal/measurements.json`, no failures. This command measured/regenerated the standard fixtures, **not** the scratch candidate; it is not candidate-gate evidence.
- `cd /home/vgpnk/Projects/prymeagnt/audio && sha256sum .shokunin/audio/corpus/artifacts/*.wav` — exit **0**; recorded the 12 artifact hashes in the command output for provenance. The candidate was not installed as a canonical artifact.
- `cd /home/vgpnk/Projects/prymeagnt/audio && python3 - <<'PY' ... PY` (read the normal receipt's `stem_layer_alt` section, five `_alt` failures and distinctness) — exit **0**. Confirms the pre-existing canonical `stem_layer_alt` is still positive-contrast and passing; it does not measure candidate.

No setup command failed. The candidate synthesis and independent candidate calculations ran in the persistent Python REPL, not a shell command. No source, LOG, SCORECARD, canonical artifact, or commit was changed by this executor.
