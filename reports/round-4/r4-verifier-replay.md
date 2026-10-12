# Round 4 independent verifier replay

Non-author replay against the checked-in integrated `build_artifacts.py` and `measure_audio.py`. I did not edit either source file or `.shokunin/audio/LOG.md`. The runs below are fresh receipts from this replay.

## Commands and outcomes

Commands were run sequentially in this exact order from the repository root:

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
```

| Mode | Exit | Receipt | Reported failures |
|---|---:|---|---|
| normal | 0 | `corpus/live/runs/20261012T164313398133Z-normal/measurements.json` | none (`{}`) |
| `--probe-flat` | 1 | `corpus/live/runs/20261012T164318673149Z-flat/measurements.json` | `flat30_probe`: sections: 30 Hz energy contrast < 6 dB or invalid |
| `--probe-slope` | 1 | `corpus/live/runs/20261012T164319311023Z-slope/measurements.json` | `slope_probe`: loop seam slope mismatch > .001 full scale/sample |
| `--probe-failing` | 1 | `corpus/live/runs/20261012T164319899564Z-failing/measurements.json` | `ambience`: centroid outside fixture band; endpoint jump > .03 full scale |
| normal restore | 0 | `corpus/live/runs/20261012T164320494590Z-normal/measurements.json` | none (`{}`) |

The normal receipts contain ten WAV measurements: `ui`, `ui_alt`, `impact`, `impact_alt`, `movement`, `movement_alt`, `ambience`, `ambience_alt`, `stem`, `stem_sections`. Every measurement has an empty `failures` list in both normal receipts. The final normal run restored the generated artifact state after all probes.

## Section contrast and guards

The integrated battery reads decoded floating-point samples from each WAV, takes the first and second 96,000-sample halves, and estimates the 30 Hz component amplitude as `2*abs(rfft(section)[60])/96000` (0.5 Hz bin spacing). It requires each component amplitude >=0.01 FS, each section RMS >=0.001 FS, and energy contrast >=6 dB. This is a fixture-local numeric proxy only.

- `stem_sections.wav`: amplitudes `0.0119994651` and `0.0599980712` FS; section RMS `0.06381031` and `0.07615526` FS; contrast **13.979508 dB**, valid and passed (threshold >=6 dB). Duration 4.000 s, 48 kHz mono. Seam endpoint delta `0.00427246` FS (limit .03); slope gap `0.000152588` FS/sample (limit .001). Peak `0.17236328` (<.95); RMS `-23.066521` dBFS.
- `flat30_probe.wav` in flat receipt: amplitudes `0.0359986155` and `0.0359986155` FS, section RMS `0.06817450` and `0.06817450` FS; contrast **0.0 dB**, valid but rejected. It is the sole failure in `--probe-flat`; its loop guards pass (endpoint `0.00418091` FS, slope `0.000030518` FS/sample). The valid section thresholds mean the rejection isolates contrast rather than silence/invalid data.
- Old slope probe in `--probe-slope`: endpoint delta `0.0` FS passes; slope gap `0.46997070` FS/sample fails the .001 limit, and is the sole failure.
- Old amplitude probe in `--probe-failing`: `ambience` peak `0.49932861` FS, endpoint jump `0.49932861` FS (> .03), centroid `2690.187705` Hz, outside its configured 5–200 Hz band. These are exactly the two reported failure classes; this probe is not a section-contrast failure.

## Original-artifact preservation and variants

Compared the current artifact WAV file hashes with `git show 68a3c3c:<path> | sha256sum`. All nine original artifact files match byte-for-byte:

- `ambience.wav`: `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` — MATCH
- `ambience_alt.wav`: `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` — MATCH
- `impact.wav`: `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` — MATCH
- `impact_alt.wav`: `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` — MATCH
- `movement.wav`: `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` — MATCH
- `movement_alt.wav`: `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` — MATCH
- `stem.wav`: `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` — MATCH
- `ui.wav`: `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` — MATCH
- `ui_alt.wav`: `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` — MATCH

New integrated `artifacts/stem_sections.wav` SHA-256: `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`. Composer scratch `.shokunin/audio/corpus/live/round-4/stem_sections.wav` SHA-256 is `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`; it matches the integrated generated WAV. The four registered variant checks all pass in both normal receipts: `ui_alt` duration delta 0.040 s (centroid delta 47.19%); `impact_alt` duration delta 0 s (centroid delta 95.63%); `movement_alt` duration delta 0.120 s (centroid delta 0.75%); `ambience_alt` duration delta 0 s (centroid delta 58.45%). Each passes at least one declared distinctness condition (duration >=.020 s OR centroid relative delta >=10%).

The separate wave-1 440 Hz `flat_probe.wav` has SHA-256 `7189005218eb1ed24292186f3023d49e5d0f7d9cc786b3943d18113477bda62f`. Its author telemetry refers to constant 440 Hz, while the integrated checker and negative control here use the specified 30 Hz component. This 440 Hz probe is a **failed-fit telemetry mismatch**, not the control and not evidence against the 30 Hz test; only `flat30_probe.wav` is the matched contrast control.

## Scope

This replay verifies fixture generation, fixed numeric checks, isolation of the declared controls, and byte preservation. The 30 Hz energy contrast is a specified analytic section proxy; it does not establish musical motif identity, recurrence, audibility, musicality, playback quality, engine behavior, or any perceptual claim.
