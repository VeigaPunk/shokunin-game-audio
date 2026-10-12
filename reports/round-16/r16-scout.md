# Round 16 scout — 180 Hz section contrast and join map

## Scope

Read the Round 16 declaration in `.shokunin/audio/LOG.md`, `corpus/fixtures/measure_audio.py`, `corpus/fixtures/build_artifacts.py`, and existing Round 13/15 scout reports and receipts. No shell commands were run; no candidate was synthesized or measured by this scout, and no source or artifact was changed. Values below are either existing decoded receipt values or clearly labeled predictions from the generator formula/PCM16 quantization. They are not execution of a reverse probe.

## Existing 180 Hz controls

The canonical `stem_layer_alt.wav` is four seconds, 48 kHz mono; `section_contrast(..., 180)` divides its 192,000 decoded samples into two 96,000-sample halves. From the existing clean receipt `corpus/live/runs/20261012T184825401717Z-normal/measurements.json`, measured first/second 180 Hz component amplitudes are `0.014999921578770435` / `0.04999787162649197` FS. Both exceed the existing `.01` FS component minimum (and both half-RMS values exceed `.001` FS); signed contrast is `+10.457250572050896 dB`, so the existing `>=6 dB` test passes. Internal join gap is `0.0003662109375` FS and side-slope mismatch `0.0008544921875` FS/sample; outer endpoint delta is `0.001190185546875` FS and outer slope mismatch `0.00079345703125` FS/sample. These are receipt facts, not a reverse-candidate result.

The older flat 180 Hz control is `corpus/live/round-13/flat180_probe.wav`; its existing receipt is `corpus/live/runs/20261012T184819795852Z-layer-alt-flat/measurements.json`. Measured component amplitudes are equal, `0.03599800833461317` / `0.03599800833461317` FS, so contrast is `0.0 dB`; validity passes and the contrast check fails. Generic and outer checks pass; internal join gap is `0.0008544921875` FS and internal slope mismatch `0.0` FS/sample. Its sole recorded failure is `sections: 180 Hz component amplitude contrast < 6 dB or invalid`. This tests equal-amplitude rejection, not the negative signed direction.

## Reverse prediction (not executed)

The declared synthesis hypothesis is `where(t < 2, .050, .015) * sin(2*pi*180*t)` for `t = arange(192000)/48000`, then the builder's PCM16 conversion (`round(clip(x,-1,1)*32767)`). By symmetry with the measured canonical, predicted decoded section amplitudes are approximately `.0499979` then `.0149999` FS, both valid, and predicted signed contrast is approximately `-10.45725 dB`. Thus the existing contrast gate should fail its `>=6 dB` condition if this generated waveform is used; this is a calculation/prediction only, not a runner observation.

At the midpoint, values predicted from the stated formula followed by PCM16 quantization are frames 95998..96001 approximately `[-.0023499252, -.0011902219, 0, .0003662221]` FS. Predicted internal adjacent gap is `.0011902219` FS and side-slope mismatch `.0007934812` FS/sample, below existing `.03` and `.001` bounds. Predicted outer endpoint gap is `.0003662221` FS and outer slope mismatch `.0008545183` FS/sample, also below `.03` and `.001`. Those are formula-derived expected numbers and must not be represented as measurements: actual decoding/quantization/tool outputs may differ slightly. Generic format/duration, level, centroid, and all other gates still require actual runner evidence; no sole-failure claim follows from these predictions alone.

## Gate semantics / limits

`section_contrast` defines signed contrast as `20*log10(second_half_amplitude / first_half_amplitude)` and passes only if both sections are valid and that value is at least 6 dB. The proposed reversed sections are not interchangeable with the flat control: the flat test has valid equal amplitudes and zero contrast; a reversed test would have valid amplitudes but negative contrast. The internal join metrics are calculated around samples 95999/96000/96001 and are separate from outer seam metrics. Existing bounds are fixture-local checks, not perceptual thresholds.

No audible seamlessness, musical-quality, adaptive-engine, rights, external-reader, security, or production claim is supported. No reverse candidate was run here; no exact shell commands or shell exit codes apply.
