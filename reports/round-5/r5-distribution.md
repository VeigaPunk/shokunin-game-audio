# Round 5 distribution report

Scope: decoded clean ten-fixture distribution and nearest margins against current enforced thresholds. Source receipt: `corpus/live/runs/20261012T164320494590Z-normal/measurements.json` (mode `normal`, all ten failure lists empty). Raw files are `corpus/artifacts/*.wav`; SHA-256s below. This is descriptive of this generated battery only, not a population or universal standard.

## Clean measurements and per-fixture margins

| fixture | duration / target (ms error; tolerance 1 ms) | peak (limit <.95; headroom) | RMS dBFS (limit >−60 dBFS; margin) | centroid Hz (allowed band; nearest margin) | endpoint delta (limit ≤.03; margin) | slope delta (limit ≤.001; margin) | LUFS |
|---|---:|---:|---:|---:|---:|---:|---:|
| ui | 0.120 / 0.120 (0.000; ±1) | 0.375946 (0.574054) | -19.992 (40.008 dB) | 966.897 (250–4000; 716.897) | not enforced | not enforced | null |
| ui_alt | 0.160 / 0.160 (0.000; ±1) | 0.318787 (0.631213) | -20.526 (39.474 dB) | 1423.153 (250–4000; 1173.153) | not enforced | not enforced | null |
| impact | 0.320 / 0.320 (0.000; ±1) | 0.808777 (0.141223) | -20.402 (39.598 dB) | 10843.127 (50–15000; 4156.873) | not enforced | not enforced | null |
| impact_alt | 0.320 / 0.320 (0.000; ±1) | 0.756165 (0.193835) | -17.330 (42.670 dB) | 473.792 (50–15000; 423.792) | not enforced | not enforced | null |
| movement | 0.240 / 0.240 (0.000; ±1) | 0.539490 (0.410510) | -23.780 (36.220 dB) | 11934.484 (100–16000; 4065.516) | not enforced | not enforced | null |
| movement_alt | 0.360 / 0.360 (0.000; ±1) | 0.639313 (0.310687) | -21.987 (38.013 dB) | 12024.215 (100–16000; 3975.785) | not enforced | not enforced | null |
| ambience | 2.000 / 2.000 (0.000; ±1) | 0.174591 (0.775409) | -18.153 (41.847 dB) | 36.616 (5–200; 31.616) | 0.000671387 (margin 0.029328613) | 0.000030518 (margin 0.000969482) | -30.7 |
| ambience_alt | 2.000 / 2.000 (0.000; ±1) | 0.199738 (0.750262) | -17.670 (42.330 dB) | 58.019 (5–200; 53.019) | 0.001892090 (margin 0.028107910) | 0.000000000 (margin 0.001000000) | -24.7 |
| stem | 2.000 / 2.000 (0.000; ±1) | 0.323792 (0.626208) | -14.881 (45.119 dB) | 272.676 (100–2000; 172.676) | 0.011383057 (margin 0.018616943) | 0.000030518 (margin 0.000969482) | -15.8 |
| stem_sections | 4.000 / 4.000 (0.000; ±1) | 0.172363 (0.777637) | -23.067 (36.933 dB) | 201.871 (100–2000; 101.871) | 0.004272461 (margin 0.025727539) | 0.000152588 (margin 0.000847412) | -24.7 |

Clean aggregate range (10 files unless noted): sample rate 48,000 Hz and mono in all; durations exactly match declared sample counts (0 ms displayed duration error); peak 0.172363–0.808777 FS, nearest upper-limit margin 0.141223 FS (`impact`); RMS −23.780 to −14.881 dBFS, minimum-threshold margin at least 36.220 dB; centroid 36.616–12,024.215 Hz, each fixture remains within its own band (smallest nearest-edge margin 31.616 Hz, `ambience`). Bandwidth is recorded descriptively (400.298–7,693.963 Hz), not an enforced threshold. Seam checks apply to four loop fixtures only: endpoint delta 0.000671–0.011383, minimum margin 0.018617 (`stem`); slope delta 0–0.000152588, minimum margin 0.000847412 (`stem_sections`). Duration is compared to ffprobe duration with ±0.001 s tolerance; exact nominal durations are also inherent in the builder sample counts.

## Measurement method

I parsed the final normal JSON receipt with Python `json.loads(Path(...).read_text())` and used its decoded-WAV measurements for the ten fixture rows and aggregates. Per-fixture nearest margins were computed as follows: duration `0.001 - abs(duration_s - declared_seconds)`; peak `0.95 - peak_full_scale`; RMS `rms_dbfs - 20*log10(.001)`; centroid `min(centroid-low_hz, high_hz-centroid)`; loop endpoint `.03 - endpoint_delta`; loop slope `.001 - slope_delta`. For section data I used the receipt's two decoded-half amplitudes/RMS and section contrast; floor margin is observed value minus floor and contrast margin is contrast minus 6 dB. Distinctness is the code's OR: duration delta ≥.020 s or relative centroid delta ≥.10; each branch margin is observed delta minus its own threshold, so a negative value can coexist with a pass via the other branch. This describes receipt values, not a separate recomputation from PCM.

Numeric threshold coverage: sample rate 48,000 Hz / mono; duration tolerance ±0.001 s; peak <.95 FS; RMS ≥.001 FS (−60 dBFS; code fails only when `<.001`); centroid inclusive per-fixture bands shown above; loop endpoint ≤.03 FS; loop slope ≤.001 FS/sample; section component amplitude ≥.01 FS; section RMS ≥.001 FS (code fails only when `<.001`); section contrast ≥6.0 dB; distinctness duration delta ≥.020 s OR relative centroid delta ≥.10. Exact format was 48,000 Hz mono in all ten. All ten decoded duration errors were 0 ms at displayed precision. Thresholds with only a single eligible section fixture (`stem_sections`) have only its two per-section observations, not a ten-file population range; loop bounds apply only to the four loop fixtures, and endpoint/slope range and nearest margins are reported above. Band/channel/format tests are categorical/exact, so numeric “margin” beyond pass is not defined. No LUFS threshold is enforced.

## Derived checks

| decision | measured result | threshold / nearest margin |
| distinctness `ui_alt` vs `ui` (OR rule) | duration Δ 0.040000 s; relative centroid Δ 0.471877; pass | duration ≥0.020 s OR centroid ≥0.10; passing branch margin(s): +0.020000 s / +0.371877 |
| distinctness `impact_alt` vs `impact` (OR rule) | duration Δ 0.000000 s; relative centroid Δ 0.956305; pass | duration ≥0.020 s OR centroid ≥0.10; passing branch margin(s): -0.020000 s / +0.856305 |
| distinctness `movement_alt` vs `movement` (OR rule) | duration Δ 0.120000 s; relative centroid Δ 0.007519; pass | duration ≥0.020 s OR centroid ≥0.10; passing branch margin(s): +0.100000 s / -0.092481 |
| distinctness `ambience_alt` vs `ambience` (OR rule) | duration Δ 0.000000 s; relative centroid Δ 0.584514; pass | duration ≥0.020 s OR centroid ≥0.10; passing branch margin(s): -0.020000 s / +0.484514 |
| section amplitude floor (`stem_sections`, each half) | 0.011999465, 0.059998071 FS | each ≥0.01; margins 0.001999465, 0.049998071 FS |
| section RMS floor (`stem_sections`, each half) | 0.063810315, 0.076155261 FS | each >0.001; margins 0.062810315, 0.075155261 FS |
| section contrast (`stem_sections`) | 13.979508 dB | ≥6.0 dB; margin 7.979508 dB |

The 30 Hz section contrast is an analytic fixture proxy; it does not establish musical motif identity or audible quality. A flat control is deliberately non-passing and belongs under controls, not the clean distribution.

## Probe/control measurements (named receipt set)

| control | relevant observed values | intended result |
| matched flat30 section probe (`20261012T164318673149Z-flat`) | component amplitudes 0.035998615/0.035998615 FS (both above .01 floor); contrast 0.000 dB; failures ['sections: 30 Hz energy contrast < 6 dB or invalid'] | rejected only section contrast (required ≥6 dB) |
| slope probe (`20261012T164319311023Z-slope`) | endpoint 0.000000000 (passes .03); slope 0.469970703 (limit .001); failures ['loop seam: slope mismatch > .001 full scale per sample'] | rejected slope only |
| broken ambience (`20261012T164319899564Z-failing`) | centroid 2690.188 Hz (band 5–200); endpoint 0.499328613 (limit .03); failures ['spectrum: centroid outside fixture band', 'loop seam: endpoint jump > .03 full scale'] | rejected centroid and endpoint |

These probes support localized sensitivity of the named checks, not calibration of every possible failure. The final normal receipt is after the probe sequence; all ten canonical artifacts are restored to clean measurements.

## Threshold interpretation and caveats

Values and boundary polarity are copied from `corpus/fixtures/measure_audio.py` (current receipt `thresholds`). Format is exact 48 kHz mono; duration passes when absolute ffprobe duration error ≤0.001 s; peak is strict `<0.95`; whole-file RMS is strict `>0.001` FS (equivalent to >−60 dBFS); centroid bounds are inclusive per fixture; loop endpoint is `≤0.03` FS and slope mismatch `≤0.001` FS/sample; section amplitude is `≥0.01` FS and section RMS `≥0.001` FS; section contrast `≥6 dB`; distinctness passes if duration delta `≥0.020 s` OR relative centroid delta `≥0.10`. Section contrast formula uses decoded exact 30 Hz FFT-bin amplitude in each 96,000-sample 2 s half, `20 log10(A2/A1)`. The 10 canonical clean files and all four SFX distinctness comparisons pass. The code checks RMS `<.001` as failure, so actual polarity is `≥.001` (different from prose strict `> .001` only at equality; no current fixture is at the boundary).

The distribution and margins characterize this deterministic synthetic fixture set and show margin to local thresholds. They do not derive thresholds from a broad artifact population, listening study, codec/engine playback, production mastering standard, or user requirements. No loudness acceptance window exists in code or in this report. FFmpeg ebur128 returned integrated LUFS for four fixtures only: ambience −30.7, ambience_alt −24.7, stem −15.8, stem_sections −24.7 LUFS; six short/high-frequency SFX yield null after the code maps non-finite or ≤−70 LUFS floor to null. This is not evidence of “quiet” assets or a target. RMS dBFS remains the level guard; LUFS is logged as a non-gated result when available, with no pass/fail window.

## Ten canonical artifact SHA-256

- `ambience.wav`: `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`
- `ambience_alt.wav`: `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc`
- `impact.wav`: `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc`
- `impact_alt.wav`: `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`
- `movement.wav`: `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d`
- `movement_alt.wav`: `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`
- `stem.wav`: `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0`
- `stem_sections.wav`: `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`
- `ui.wav`: `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`
- `ui_alt.wav`: `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`

Recompute with `python3 .shokunin/audio/corpus/fixtures/measure_audio.py`; normal mode rebuilds the ten fixtures and creates a timestamped receipt. Source measurements and controls are round-local; do not infer a universal threshold.
