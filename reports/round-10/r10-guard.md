# Round 10 guard inventory — declared depth claim

## Scope and method

Report-only inventory for the declared internal `stem_layer` join-gap check. I read round-10 LOG, current `measure_audio.py`, prior durable guard/verifier reports, and computed SHA-256 of the eleven current canonical WAV files. I did not run shell commands or replay measurements; accordingly this report adds no new command exits or receipts. I changed no source, scratch, canonical assets, receipts, LOG, SCORECARD, or other report.

## Canonical assets

Current files under `corpus/artifacts/` and their SHA-256 hashes:

| WAV | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

These are current filesystem hashes; this lane did not independently compare them to a Git commit/blob. Prior round-9 verifier records all eleven matching blobs at `aaf4801`. The declared round-10 claim requires those canonical hashes remain unchanged; no replay was performed here.

## Existing modes, prior exits, and receipts

The inspected current CLI has normal, `--probe-flat`, `--probe-layer-flat`, `--probe-slope`, `--probe-failing`, and `--probe-invalid`; there is no `--probe-layer-join` option in the source I inspected. Prior round-9 verifier documented this corrected command sequence, exits and receipts (transcribed, not rerun by this lane):

| Exact command | Exit | Prior receipt |
|---|---:|---|
| `python3 .shokhun/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T173529588648Z-normal/measurements.json` |
| `python3 .shokhun/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `corpus/live/runs/20261012T173530301419Z-flat/measurements.json` |
| `python3 .shokhun/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `corpus/live/runs/20261012T173531012671Z-layer-flat/measurements.json` |
| `python3 .shokhun/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `corpus/live/runs/20261012T173531703686Z-slope/measurements.json` |
| `python3 .shokhun/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `corpus/live/runs/20261012T173532346892Z-failing/measurements.json` |
| `python3 .shokhun/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `corpus/live/runs/20261012T173532571164Z-invalid/measurements.json` |
| `python3 .shokhun/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T173533220319Z-normal/measurements.json` |

The source path is `.shokhun/audio/corpus/fixtures/measure_audio.py`; the table's exact command spelling is transcribed from the prior verifier. Exit 1s are expected negative-control results, not generic success. The prior evidence says flat30 and flat120 each fail only their respective flat contrast, slope fails its slope guard, failing mode has its declared failures, invalid mode classifies four invalid probes as expected failures, and normal/restore pass. This lane did not inspect or independently validate those receipts.

## Existing numeric limits and before-state

The current source retains these relevant thresholds:

- 48,000 Hz mono; duration tolerance ±0.001 s.
- Peak must be `< 0.95` full scale; RMS must be `>= 0.001`.
- Centroid bands: UI 250–4000 Hz; impact 50–15000 Hz; movement 100–16000 Hz; ambience 5–200 Hz; stem families 100–2000 Hz.
- Outer loop endpoint jump `<= 0.03` full scale; outer slope mismatch `<= 0.001` full scale/sample.
- Section contrast requires 192,000 decoded samples split into 96,000-sample halves; component amplitude `>= .01` and section RMS `>= .001` in each half; signed `20*log10(A2/A1) >= 6 dB`. `stem_layer` uses 120 Hz.
- Four alternate variants must differ by at least 20 ms duration **or** 10% relative centroid.

`measure()` currently calculates outer endpoint and slope deltas from first/last samples, then gates those outer loop values only. `section_contrast()` measures per-half 120Hz amplitude and does not inspect the join. For 192,000 decoded samples, the internal boundary is between samples 95,999 and 96,000 (zero-based); the adjacent jump is `abs(samples[96000] - samples[95999])`. Before-state currently has no receipt field or acceptance check for it.

## Guard interpretation

The declared proposed `<= .03` internal sample jump reuses an existing fixture-local numeric endpoint bound, but does not thereby become an empirically calibrated threshold. A candidate control only supports isolation if it preserves 4s/48k mono, peak/RMS, centroid band, outer endpoint and slope limits, and the 120Hz section contrast, while failing solely on internal jump `> .03`. Its generator/hash and decoded metrics need independent evidence. This guard lane produced no candidate and makes no claim that such a control fits. A gap proxy does not prove transition smoothness, click-free behavior, waveform slope continuity, runtime/adaptive timing, or audibility. No perceptual, engine, security, or production claim is made.
