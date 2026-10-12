# Round 20 independent verifier (r20-verifier)

Leaf non-author replay. Worktree `/home/vgpnk/Projects/prymeagnt/audio`. No builder/runner/canonical/SCORECARD/LOG/PROVINCE/SHONEN/MANIFEST edits. Only this report was written; receipts are runner-created under `.shokunin/audio/corpus/live/runs/`.

## Replay (17 modes, serial)

Exact commands from repo root. Exit 1 = intentional measured negative. No exit 2.

| # | Exact command | Exit | Receipt | Failure set / observed kinds |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T232008284370Z-normal/measurements.json` | `{}` / none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232009162006Z-layer-third-join/measurements.json` | `join200_probe`: sections: internal join adjacent sample gap > .03 full scale |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261012T232010039574Z-layer-third-slope-edge-pass/measurements.json` | `{}` / none |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232010905024Z-layer-third-slope-edge-fail/measurements.json` | `edgefail_probe`: sections: internal join side slope mismatch > .001 full scale per sample |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232011774386Z-layer-third-slope/measurements.json` | `slope200_probe`: sections: internal join side slope mismatch > .001 full scale per sample |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232012638303Z-layer-alt-reverse/measurements.json` | `reverse180_probe`: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232013494774Z-layer-alt-slope/measurements.json` | `slope180_probe`: sections: internal join side slope mismatch > .001 full scale per sample |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232014351479Z-layer-alt-join/measurements.json` | `join180_probe`: sections: internal join adjacent sample gap > .03 full scale |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232015210551Z-layer-alt-flat/measurements.json` | `flat180_probe`: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232016070609Z-layer-slope/measurements.json` | `layer_slope_probe`: sections: internal join side slope mismatch > .001 full scale per sample |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232016929985Z-layer-join/measurements.json` | `join_probe`: sections: internal join adjacent sample gap > .03 full scale |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232017798039Z-flat/measurements.json` | `flat30_probe`: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232018662879Z-layer-flat/measurements.json` | `flat120_probe`: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232019500434Z-slope/measurements.json` | `slope_probe`: loop seam: slope mismatch > .001 full scale per sample |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232020301176Z-failing/measurements.json` | `ambience`: spectrum: centroid outside fixture band; loop seam: endpoint jump > .03 full scale |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261012T232020531478Z-invalid/measurements.json` | `invalid_probes` kinds: short_sections/odd_sections (section count), corrupt (decode), wrong_format (format) |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T232021323861Z-normal/measurements.json` | `{}` / none |

### Exit vector
`[0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]`

### Expected integration vs observed
- 1 and 17 exit 0, failures `{}`: **held**.
- 2 exit 1 sole `join200_probe` gap failure: **held**.
- 3 exit 0: **held**.
- 4–15 exit 1 with same failure **kinds** as r19-verifier rows 3–14: **held** (probe key for alt-join is `join180_probe` here; r19 table labeled the same gap kind under `join_probe` for that row — kind text matches).
- 16 exit 1 with four `invalid_probes` kinds (malformed inputs): **held**.
- First vs restored normal JSON equal after stripping path/time identity: **held** (`True`).

## New-mode (layer-third-join / join200_probe) numbers

Selected receipt: `.shokunin/audio/corpus/live/runs/20261012T232009162006Z-layer-third-join/measurements.json`

| Field | Value |
|---|---|
| component_hz | 200 |
| section_samples | 96000 |
| component amplitudes FS | 0.014999586208149856, 0.04999830040080907 |
| section RMS FS | 0.06412683387134765, 0.07245470848208663 |
| contrast dB | 10.457519263296449 (≥ 6) |
| internal gap FS | 0.030029296875 (**> .03** → sole runner failure) |
| internal side-slope FS/sample | 0.0 (≤ .001) |
| section.valid / section.passed | true / true (**passed = contrast/validity only, not full gate**) |
| measurement centroid Hz | 1209.6397189190805 (inside 100–2000) |
| outer endpoint / slope | 0.005340576171875 / 0.00091552734375 (generic/outer pass; no extra measurement failures beyond the section gap string) |
| duration / rate / ch / peak | 4.0 s / 48000 / mono / 0.163604736328125 |

Sole failure string: `sections: internal join adjacent sample gap > .03 full scale`.

### Builder claim on selected WAV (confirm/refute)
Live scratch WAV: `.shokunin/audio/corpus/live/round-20/join200_probe.wav`  
SHA-256: `5194bd8e2cc9929d5287d3ddd910d32b3c24aa2f76ba66f267d83dbbe84d97fd`  
**Scratch only — not a 14th canonical artifact.**

PCM16 mono 48 kHz, 192000 samples (same length as `stem_layer_third.wav`). Differs on **191921** frames (not a tiny patch of the third stem alone). Whole-file FFT peaks: **220 Hz, 330 Hz, 200 Hz** — confirms a **220/330 Hz bed** under the 200 Hz section component. At the internal join, `pcm[95999]=-145`, `pcm[96000]=839` (delta 984 counts ≈ 0.03003 FS); **target count 839 at the post-join sample is confirmed**. Side-slope mismatch measured 0.0.

### Parent author failed fit (do not select)
`corpus/live/runs/20261012T231846536176Z-layer-third-join` (path under `.shokunin/audio/...`) failed **both** `spectrum: centroid outside fixture band` (centroid ≈ 2195.85 Hz) **and** internal gap. That is a failed fit / canonical-copy click path, **not** this replay’s selected result. Selected replay keeps centroid inside band and only the gap gate.

## Canonical SHA-256 (13 artifacts)

Hashed `.shokunin/audio/corpus/artifacts/*.wav` and compared to `git show a905a26:.shokunin/audio/corpus/artifacts/<name>` — **all 13 match**. Also matched `7083a3f` for the same paths.

| file | sha256 |
|---|---|
| ambience.wav | b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198 |
| ambience_alt.wav | 2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc |
| impact.wav | a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc |
| impact_alt.wav | a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6 |
| movement.wav | 23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d |
| movement_alt.wav | 51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639 |
| stem.wav | fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0 |
| stem_layer.wav | ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9 |
| stem_layer_alt.wav | 74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9 |
| stem_layer_third.wav | 3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445 |
| stem_sections.wav | 49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702 |
| ui.wav | 4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9 |
| ui_alt.wav | 166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f |

Expected third hash `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`: **confirmed**.

## Distinctness (_alt)

In the new-mode (layer-third-join) receipt, all five `_alt` distinctness records **passed**: `ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, `stem_layer_alt`.

## Invalid mode

Four expected_failure records only (not canonical WAV measurement): short_sections (section count), corrupt (decode), wrong_format (format), odd_sections (section count).

## Limits
- Verifies this runner + these fixtures + this selected join200 scratch WAV only.
- `section.passed` is contrast/validity, not the complete internal-join gate.
- Author receipt `20261012T231846536176Z-layer-third-join` is documented as a failed fit and is not evidence of integration success.
- Does not claim production/engine perceptual calibration or a universal PCM threshold grid.
- r19 alt-join row labeled `join_probe`; this run’s measurement key is `join180_probe` with the same gap kind string.

## Verdict
Round-20 integration replay **holds** on the 17-mode exit/failure contract, canonical hashes, distinctness, normal restore equality, and the selected join200 sole-gap profile with 220/330 bed and post-join sample value 839.
