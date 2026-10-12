# Round 11 slope-only candidate

Role: `r11-slope` executor. Scope: original scratch candidate and its evidence only; no shared fixture or measurement code edits.

## Candidate
- Source: `corpus/artifacts/stem_layer.wav` (reproducibly rebuilt by `python3 .shokunin/audio/corpus/fixtures/build_artifacts.py`).
- Recipe: copy source PCM16 samples exactly, then add 0.0004 full-scale to sample index 96001, round to PCM16, preserve WAV parameters. This perturbs only the first right-side sample at the 2s join.
- Builder: `python3 .shokunin/audio/corpus/live/round-11/create_slope_candidate.py` (exit 0); output `corpus/live/round-11/slope_candidate.wav` SHA-256 `cf5ca8467a7943060f038e9e98bd4b8b8551725b7432bc728d22c27b8ea12e9d`.
- Measurement command: `python3 -c 'import runpy; from pathlib import Path; m=runpy.run_path(".shokunin/audio/corpus/fixtures/measure_audio.py"); p=Path(".shokunin/audio/corpus/live/round-11/slope_candidate.wav").resolve(); print(m["measure"]("slope_probe", m["SPECS"]["stem_layer"], p)); print(m["section_contrast"](p,120))'` (exit 0). A first attempt with a relative candidate path exited 1 because `measure` requires a path relative to its fixture ROOT; resolving the same scratch path fixed it, without changing source or candidate.
- Decoded SoX samples 95998..96002: `[-0.0003662109375, -0.00018310546875, 0.0, 0.0013427734375, 0.00189208984375]`. Internal adjacent gap = `0.000183105` FS, below .03. Side-slope mismatch = `0.001159668` FS/sample, above proposed .001.

## Existing checks
- Existing `measure("slope_probe", SPECS["stem_layer"], candidate)` returned no failures (4.000s, 48kHz mono, peak .059998 FS, RMS -30.288 dBFS, centroid 211.475 Hz, outer endpoint .000946 FS, outer slope mismatch .000763 FS/sample). This uses existing layer spec as telemetry, not a new gate.
- Existing 120Hz `section_contrast` passes: valid contrast 13.979372 dB; join gap .000183105 FS.
- This demonstrates candidate fit for a proposed internal-slope-only gate; code has not yet been integrated, and sole failure awaits parent integration plus independent verifier.
- Candidate is a numeric synthetic control, not an audible-quality claim or threshold calibration.
