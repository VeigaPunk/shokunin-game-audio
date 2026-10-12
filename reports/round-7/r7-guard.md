# Round 7 guard inventory (report only)

## Scope and status

Read the declared round-7 entry in `.shokunin/audio/LOG.md`, current `corpus/fixtures/measure_audio.py` and `build_artifacts.py`, and round-6 independent verifier report. This is an inventory, **not a replay**: I did not run the normal, flat, slope, failing, restore, or `--probe-invalid` modes. Round-6 receipt observations below are prior recorded evidence, not fresh round-7 verification. I did not make audio/perceptual/security claims.

## Existing mode guards / recorded baseline

The current runner accepts at most one of `--probe-flat`, `--probe-slope`, `--probe-failing`, `--probe-invalid`; absent a flag is normal. In round-6 verifier's recorded sequence the exact commands and exits were:

| Command | Exit | Recorded receipt / guard |
|---|---:|---|
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T170607675436Z-normal/measurements.json`; ten measurements, no failure; four alternate-distinctness checks pass. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.../20261012T170608325807Z-flat/measurements.json`; flat 30-Hz control fails section contrast. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.../20261012T170608960610Z-slope/measurements.json`; slope control fails slope mismatch. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.../20261012T170609548702Z-failing/measurements.json`; broken ambience fails centroid/endpoint checks. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.../20261012T170610141133Z-normal/measurements.json`; clean restoration. |

These are **round-6 verifier-reported results**, not my executions, and predate the declared round-7 integration. Source inspection shows `--probe-invalid` first invokes the artifact builder with `--probe-invalid`, then emits a timestamped invalid receipt and exits 1 if all listed entries have their expected category, else 2. It is not one of the ordinary artifact-measuring modes.

## Three named invalid guard checks (source inventory, not run)

`invalid_probes()` currently iterates only `short_sections` (`section count`), `corrupt` (`decode`), and `wrong_format` (`format`) from `live/round-6`:

1. `short_sections`: calls `section_contrast(path)`, whose 192000-sample exact-count check precedes split/FFT; expected category is `section count`.
2. `corrupt`: runs `ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json <path>` through `command()`; catches `subprocess.CalledProcessError` and labels it `decode`.
3. `wrong_format`: runs the same ffprobe invocation, reads first stream rate/channels, labels `format` unless rate is 48000 and channels is 1.

The list has **no `odd_sections` entry yet** in the source I inspected. The executor's reported 101-frame `corpus/live/round-7/odd_sections.wav` is a separate scratch input; this inventory does not establish its old exception or current-mode receipt behavior.

## Ten canonical WAV SHA-256 comparison to `cba2748`

I enumerated the ten `corpus/artifacts/*.wav` names and for each ran these shell commands (substituting the filename):

- `sha256sum .shokunin/audio/corpus/artifacts/<name>.wav` — exit 0
- `git show cba2748:.shokunin/audio/corpus/artifacts/<name>.wav | sha256sum` — exit 0

All ten current-vs-`cba2748` digests match:

| WAV | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` (baseline `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`) — match; exits 0/0 |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` (baseline `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc`) — match; exits 0/0 |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` (baseline `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc`) — match; exits 0/0 |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` (baseline `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`) — match; exits 0/0 |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` (baseline `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d`) — match; exits 0/0 |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` (baseline `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`) — match; exits 0/0 |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` (baseline `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0`) — match; exits 0/0 |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` (baseline `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`) — match; exits 0/0 |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` (baseline `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`) — match; exits 0/0 |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` (baseline `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`) — match; exits 0/0 |

This establishes byte identity of those ten files against the named Git tree, not any audio-quality conclusion. I did not run the five mode commands above; their exact shell commands/exits are given as reported in the round-6 verifier document. No shared source, LOG, scorecard, artifact, or commit was edited.
