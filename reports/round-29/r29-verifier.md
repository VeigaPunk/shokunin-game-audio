# Round 29 independent verifier — NON-AUTHOR

## Verdict

**The integrated runner verifies the requested lower-centroid two-point comparator polarity, narrowly.** I serially replayed 26 invocations: initial normal, the two new lower-centroid probes, then the prior round-28 24-mode sequence with its duplicate initial normal removed (prior #1 plus prior #4–#26), ending in normal restore. The new below point exits 1 solely for existing distinctness; the above point exits 0. Both baseline/variant pairs pass ordinary format, level, duration, and centroid-band checks under the same canonical `SPECS["ui"]` .120 s spec. Both are 5760-frame, 48 kHz mono PCM16, and each duration delta is 0.

Baseline centroid is 966.8966593379727 Hz, higher than both variants: 871.155504521436 Hz and 862.0264574403602 Hz. The measured absolute relative deltas are `0.09901901500217196` (below: existing distinctness failure) and `0.1084606104331939` (above: pass). The signed variant-minus-baseline deltas are negative for both; a signed implementation would reject the above-cutoff lower-centroid case. Existing absolute-value comparator and `.020 s OR .10` bounds are unchanged. This verifies two numeric points only, not exact equality or smoothness.

## Serial replay (26 invocations)

Commands ran from repository root, serially. Paths in the table are runner-generated receipt paths relative to repository root. Exit 1 on negative probes is expected gate behavior, not a setup error.

| # | Exact command | Exit | Receipt | Failure kind |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T022557335369Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022558239794Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt distinctness only |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T022559154018Z-ui-lower-centroid-above/measurements.json` | none |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022600061151Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt distinctness only |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T022600962582Z-ui-centroid-above/measurements.json` | none |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022601879992Z-ui-duration-below/measurements.json` | ui_duration_below_alt distinctness only |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T022602775639Z-ui-duration-at/measurements.json` | none |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022603665417Z-ui-clone/measurements.json` | ui_clone_alt distinctness only |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T022604545761Z-layer-third-join-edge-pass/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022605429503Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe internal gap |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022606302740Z-layer-third-join/measurements.json` | join200_probe internal gap |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T022607176422Z-layer-third-slope-edge-pass/measurements.json` | none |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022608050797Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe slope |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022608921461Z-layer-third-slope/measurements.json` | slope200_probe slope |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022609785464Z-layer-alt-reverse/measurements.json` | reverse180_probe contrast |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022610658213Z-layer-alt-slope/measurements.json` | slope180_probe slope |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022611536224Z-layer-alt-join/measurements.json` | join180_probe internal gap |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022612411860Z-layer-alt-flat/measurements.json` | flat180_probe contrast |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022613306259Z-layer-slope/measurements.json` | layer_slope_probe slope |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022614207869Z-layer-join/measurements.json` | join_probe internal gap |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022615190336Z-flat/measurements.json` | flat30_probe contrast |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022616084422Z-layer-flat/measurements.json` | flat120_probe contrast |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022616948115Z-slope/measurements.json` | slope_probe loop seam |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022617761614Z-failing/measurements.json` | ambience centroid band + loop endpoint jump |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T022618102481Z-invalid/measurements.json` | 8 expected invalid-control statuses |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T022618922834Z-normal/measurements.json` | none |

Correct totals: **26 invocations, 7 exit 0 and 19 exit 1; no exit 2**. The historical prior-24 subset is this replay's #1 plus #4–#26 (24 invocations): **6 exit 0 and 18 exit 1**, matching prior round-28 mode outcomes. The new lower-centroid rows #2–#3 are excluded from that historical subset.

The eight invalid-control statuses in #25 were: `short_sections` expected_failure (section count); `corrupt` expected_failure (decode); `wrong_format` expected_failure (format); `odd_sections` expected_failure (section count); `native16_probe` expected_pass (no failure); `native24_probe` expected_failure (format); `stereo48_probe` expected_failure (format); `mono441_probe` expected_failure (format). All expected statuses matched.

## Pair evidence and preservation

The receipts record identical baseline centroids for the two pairs (`966.8966593379727` Hz), variant centroids below baseline, `.12` s duration for each member, 48 kHz mono PCM16, and empty ordinary-check failure lists. Pair outcomes and recomputed formula `abs(variant - baseline) / baseline`:

| Probe | Baseline → variant centroid (Hz) | Duration delta | Absolute relative delta | Pair result |
|---|---:|---:|---:|---|
| `--probe-ui-lower-centroid-below` | 966.8966593379727 → 871.155504521436 | 0 | 0.09901901500217196 | exit 1, distinctness only |
| `--probe-ui-lower-centroid-above` | 966.8966593379727 → 862.0264574403602 | 0 | 0.1084606104331939 | exit 0 |

All 13 canonical WAV SHA-256 hashes match `HEAD` `99b6c0a`:
- `ambience.wav` `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`
- `ambience_alt.wav` `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc`
- `impact.wav` `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc`
- `impact_alt.wav` `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`
- `movement.wav` `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d`
- `movement_alt.wav` `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`
- `stem.wav` `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0`
- `stem_layer.wav` `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`
- `stem_layer_alt.wav` `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9`
- `stem_layer_third.wav` `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`
- `stem_sections.wav` `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`
- `ui.wav` `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`
- `ui_alt.wav` `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`

The five pre-existing `_alt` comparisons remain present and pass in initial and restored normal receipts: `ui_alt` duration `.04000000000000001`, centroid relative `.47187731004956435`; `impact_alt` 0 / `.9563048992406177`; `movement_alt` `.12` / `.007518618572621081`; `ambience_alt` 0 / `.5845136323520758`; `stem_layer_alt` 0 / `.46179931396667484`. Receipt threshold objects are unchanged across all normal gate receipts, preserving duration `.02` and centroid `.1`. Initial and restored normal receipts are equal after excluding only measurement `path` fields.

The two fixture source files differ from `HEAD` only by the two new opt-in lower-centroid builder/runner routes; canonical WAV bytes remain unchanged. No threshold or existing absolute comparator change was observed. Prior 24-mode outcomes are retained in rows #1 and #4–#26; eight invalid statuses are unchanged.

## Setup errors, scope, and limits

Before the successful replay, I accidentally passed the combined command string as a single executable to the shell wrapper (`bash -c '"""..."""'`), producing 26 exit-127 “No such file” setup errors and no receipts. I corrected command invocation and then completed the 26 serial runner executions above. These setup errors are not gate outcomes and are excluded from the 26-invocation replay/count.

This is a numeric whole-waveform FFT spectral-centroid **proxy** only. No exact equality, smoothness, monotonicity, perceptual/auditory, engine/runtime, rights, publish, or promotion claim is established. I wrote only `.shokunin/audio/reports/round-29/r29-verifier.md`; all other new artifacts listed above are runner-generated receipts under `corpus/live/runs/`. I did not edit shared source, LOG, SCORECARD, canonical assets, or another report, and did not commit or push.
