# Round 27 scout — comparator and duration-spec map

## Claim under inspection

The declared calibration move targets the existing distinctness duration comparator: `passed = duration_delta >= .020 or centroid_relative_delta >= .10` (`corpus/fixtures/measure_audio.py`, lines 266–272). It proposes a 48 kHz mono PCM16 UI baseline of 0.120 s and matched variant durations 0.1399791666667 s (6719 frames; nominal delta 959/48000) and 0.140 s (6720 frames; nominal delta 960/48000), with centroid relative delta below .10. The first should fail distinctness and the exact-boundary candidate should pass it, if the measured `ffprobe` values retain those relationships.

## Per-file duration spec is separate

`SPECS["ui"] == (.12, 250, 4000, False)` and `SPECS["ui_alt"] == (.16, 250, 4000, False)`. In `measure()`, duration is `float(probe["format"]["duration"])`; the duration check fails only when `abs(duration - spec[0]) > .001`. Thus equality at exactly ±1 ms passes. The intended duration pair cannot both use `SPECS["ui"]`: a 0.139979… or 0.140 s file is about 20 ms too long and would independently fail that file-level duration check. Measuring the longer synthetic file against its own declared duration (0.1399791666667 or 0.140) avoids falsely counting that duration-spec failure as a distinctness result; retain the same UI centroid band, format, level checks and other tuple fields. The baseline remains measured against its own 0.120 s spec. A custom spec is test setup, not a change to canonical `SPECS`.

The full per-file checks include 48 kHz mono; `pcm_s16le`, 16-bit; duration within inclusive ±1 ms; peak below .95 and RMS at least .001; centroid in the inclusive 250–4000 Hz band. UI has no loop seam check. `measure()` obtains format/duration via `ffprobe`, samples via SoX float32 decode, then computes centroid from the decoded samples. The distinctness comparison uses the ffprobe duration float and the measured centroid values.

## Rounding / strictness

Duration-spec boundary: `> .001` is failure, so exactly .001 deviation passes (assuming the parsed decimal/float lands exactly there). Distinctness boundary: `>= .020` is duration-branch success; centroid `>= .10` is the other success branch. Only when both comparisons are strictly less than their limits does it append `distinctness: duration < .020 s and centroid delta < 10%`. Equality on either distinctness branch passes.

Python binary-float illustration (not an audio measurement): `0.14 - 0.12` is `0.020000000000000018`, which compares `>= .020` as `True`; `0.1399791666667 - 0.12` is `0.019979166666699993`, which compares as `False`. `ffprobe` prints a decimal duration string and Python parses it to binary float; actual files must be checked with the exact tool/output and runner, not inferred from nominal frame count. `ffprobe` may report rounded decimal text (the observed existing `ui.wav` reports `0.120000`), so do not claim sample-exact duration arithmetic from the nominal sample count alone.

## Exact shell evidence collected

Ran only this diagnostic command, against the existing canonical UI artifact:

```sh
ffprobe -v error -show_entries 'stream=sample_rate,channels,codec_name,bits_per_sample:format=duration' -of json .shokunin/audio/corpus/artifacts/ui.wav
```

Exit **0**. Output reported `sample_rate: "48000"`, `channels: 1`, `codec_name: "pcm_s16le"`, `bits_per_sample: 16`, and `format.duration: "0.120000"`. This confirms the queried existing file's probe representation only. No generator, `measure_audio.py`, runner, or candidate fit was run by scout; no candidate comparison or exit status is asserted here.

## Fit status and scope

Candidate frame-to-duration predictions are arithmetic, not measured candidate results. No fit has been attempted in this scout role, so there is no failed fit to report. A measured candidate is valid evidence only if it passes its own duration spec and ordinary per-file checks, while its comparison reports centroid delta `< .10`; otherwise the intended isolated calibration result has not been demonstrated. This maps the declared comparator and spec interactions only. It makes no perceptual, rights, engine, publishing, or promotion claim.
