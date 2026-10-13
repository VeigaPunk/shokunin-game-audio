# R53 reviewer — opt-in float32/PCM16 UI probes

## Scope and evidence

Source-only review of the R53 declaration in `.shokunin/audio/LOG.md`, the R52 source/report context, and current `corpus/fixtures/build_artifacts.py` plus `measure_audio.py`. I did not edit shared source or run builds, measurements, syntax checks, or probes. Thus no actual command exits, hashes, ffprobe output, receipt metadata, or measured metrics are claimed.

The current files already have the R52 paired pattern: builder options `--probe-ui-pcm8` / `--probe-ui-pcm16-r52`, a helper writing `live/round-52/pair_pcm*.wav`, and runner opt-in guard, builder forwarding, supplemental `measure(..., SPECS["ui"], path)`, receipt mode, and output suffix. The runner first measures the canonical `SPECS` and computes its ordinary receipt comparisons; the pair's extra result is added separately. R53 can follow this pattern without changing `format_failures()`, `SPECS["ui"]`, thresholds, canonical fixtures, or comparison logic. Existing probes must remain untouched.

## Minimal wiring proposal

1. **Builder:** add argparse flags `--probe-ui-float32` and `--probe-ui-pcm16-r53`; add one corresponding dispatch branch ahead of older probe branches. As with R52, run `main()` first and then build the selected pair, so canonical artifacts are prepared and the scratch files exist before runner measurement. Add one `build_ui_float32_probe()` helper writing only to `OUT.parent / "live" / "round-53"` (make directory with `exist_ok=True`). Make the deterministic 5,760-frame mono/48,000-Hz ordinary UI samples, quantize once to little-endian signed int16 (`s16`), and derive float samples as `(s16.astype(float32) / 32768.0).astype("<f4")`. Write `pair_pcm16.wav` as PCM16 and `pair_float32.wav` as a valid IEEE-float WAV (WAVE_FORMAT_IEEE_FLOAT tag 3, 32 bits, mono, 48 kHz; `wave`'s ordinary PCM writer must not be assumed to emit this format). Verify the RIFF header and actual ffprobe codec/bit-depth rather than inferring metadata from the extension. Keep the signals comfortably within peak bounds and in the UI centroid band.
2. **Runner parser / dispatch:** declare both flags. Add both to the existing one-probe-mode sum, forward the selected flag to the builder command, and add the extra result using unchanged `measure(name, SPECS["ui"], path)`: `ui_depth_float32_r53_probe` from `live/round-53/pair_float32.wav`, or `ui_depth_pcm16_r53_probe` from `live/round-53/pair_pcm16.wav`. Add distinct mode labels (`probe-ui-float32`, `probe-ui-pcm16-r53`) and corresponding run-directory suffixes. Do not let either scratch result enter family, `_alt`, or section comparisons. Preserve the canonical receipt contents and every prior option.
3. **Evidence checks:** run each flag separately; inspect raw WAV headers and `ffprobe` codec/sample format/channels/rate/duration, and compare both files' decoded project SoX-f32 vectors. Verify both have 5,760 frames / .120 s, non-format UI metrics within existing bounds (duration ±.001 s, peak <.95, RMS >=.001, centroid 250–4000 Hz), and record exact hashes, metrics, and all failures. Expected target results are float32 exit 1 with sole `format: expected PCM16`, PCM16 exit 0 with no failures. These are expected statuses, not observed results. Run both flags together to verify runner's one-mode rejection before building; expected argparse error exit 2. A float-specific failure beyond format or unequal decoded vectors is contrary evidence: disclose it and repair scratch construction, never relax a gate.

Suggested commands from repository root (not run here):

```sh
python .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-float32
python .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r53
python .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-float32 --probe-ui-pcm16-r53
```

Expected exits in order: **1**, **0**, **2**. The first two should each emit a receipt under `.shokunin/audio/corpus/live/runs/` with the respective mode/suffix; the third should stop at `choose one probe mode` without a receipt. These expectations require actual execution and are not evidence that the integration works.

## Limits

This proposed matched integer-grid pair tests only this fixture's existing format predicate and SoX-f32 decoding. It does not establish general float WAV support/conversion, greater dynamic range, precision/fidelity, audibility, quality, engine/production compatibility, rights, or promotion. No source changes or R53 runtime measurements were made. Preserve prior64 modes, canonical17 SHA/metrics, five generic `_alt` / four family checks, sections, invalid probes, and normal restoration in verification.
