# Round 24 scout — owned inventory vs province

## Scope and read-only boundary

I read `.shokunin/audio/LOG.md` Round 24, `.shokunin/audio/PROVINCE.md`, and `.shokunin/audio/SHONEN.md`. This is an inventory/scope audit, not a promotion, box-4 verdict, or claim about universal behavior. The current province says audio owns SFX and soundtrack verified by headless duration/loudness/spectrum/seam analysis; refuses unsupported perceptual claims, publishing/store submission, sample-rights clearance, engine-source mutation, game mechanics, and narrative canon; and says “Only writes `.shokunin/audio/**` and its own reports.” The SHONEN box 4 remains unchecked.

The owned corpus has a clear distinction between the 13 canonical generated WAVs and a much larger historical `corpus/live/` area containing round-specific candidate/control WAVs, scripts, and measurement receipts. It is incorrect to call that entire scratch area 13 files or to treat its controls as production audio. The current normal run's receipt identifies exactly 13 canonical measurements; the checks are analytic fixture checks, not listening or deployment evidence.

## Canonical inventory

`find .shokunin/audio/corpus/artifacts -maxdepth 1 -type f -name '*.wav' -printf '%f\n' | sort` (exit 0) listed 13 files:

- UI: `ui.wav`, `ui_alt.wav`
- impacts: `impact.wav`, `impact_alt.wav`
- movement: `movement.wav`, `movement_alt.wav`
- ambience: `ambience.wav`, `ambience_alt.wav`
- soundtrack: `stem.wav`, `stem_sections.wav`, `stem_layer.wav`, `stem_layer_alt.wav`, `stem_layer_third.wav`

`python3 -c 'import wave,pathlib; ps=sorted(pathlib.Path(".shokunin/audio/corpus/artifacts").glob("*.wav")); print(len(ps)); [print(p.name, *[getattr(wave.open(str(p), "rb"), a)() for a in ("getnframes", "getframerate", "getnchannels", "getsampwidth")]) for p in ps]'` (exit 0) reports all 13 are mono, 48 kHz, 16-bit PCM. The short UI/impact/movement/ambience/stem assets and 4-second section/layer assets have differing frame counts; the current measurement receipt is the stronger source for actual durations/check results.

`sha256sum .shokunin/audio/corpus/artifacts/*.wav` (exit 0) recorded these current hashes (alphabetical):

```text
2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc  ambience_alt.wav
b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198  ambience.wav
a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6  impact_alt.wav
a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc  impact.wav
51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639  movement_alt.wav
23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d  movement.wav
74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9  stem_layer_alt.wav
3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445  stem_layer_third.wav
ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9  stem_layer.wav
49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702  stem_sections.wav
fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0  stem.wav
166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f  ui_alt.wav
4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9  ui.wav
```

## Headless replay observed

`python3 .shokunin/audio/corpus/fixtures/measure_audio.py` (exit 0) produced a normal receipt at `corpus/live/runs/20261013T012550660157Z-normal/measurements.json`; I removed this temporary run directory after reading it, so no generated receipt is being added by this scout. The receipt contains 13 canonical measurements, empty per-file failure lists, and five SFX-variant distinctness results (including `stem_layer_alt`); all five are `passed: true`. It reports the current fixture-local bounds: 48 kHz mono PCM16, 1 ms duration tolerance, peak <.95 FS, RMS >=.001 FS in executed code (legacy metadata key `rms_min_exclusive` is misleading at equality), loop endpoint <=.03 FS, loop slope <=.001 FS/sample, section contrast >=6 dB with component-amplitude and section-RMS floors .01/.001 FS, and internal join adjacent delta <=.03 FS and side-slope mismatch <=.001 FS/sample; the source and calibration notes remain necessary to interpret polarity and scope. Per-section frequency is recorded on each section: 30 Hz stem_sections, 120 Hz stem_layer, 180 Hz stem_layer_alt, 200 Hz stem_layer_third. The measured component-amplitude contrasts in this run were 13.9795, 13.9794, 10.4573, and 10.4572 dB respectively. These are constructed-signal measurements against local rules, not musicality or audible continuity claims.

The inventory supports the province's named content families and a headless fixture battery. It does not establish the quality or completeness of all game audio, engine integration/adaptation, playback on target hardware, perceptual acceptability, sample/reference rights, clearance, or publishing readiness.

## Branch-history boundary and observed scope

`git branch --show-current` (exit 0) returned `craft/audio-r1`; `git log --oneline --decorate -6` (exit 0) puts `2a19811` (Round 23 final report) at HEAD. `git log --format='%h %s' -- .shokunin/audio` (exit 0) lists the lane's mint and rounds 1–23. `git log --oneline --name-only 2a198118a527baf749dbd2e23b6667a79a1ccf31 -- .shokunin/audio` (exit 0) showed post-HEAD audio-path commit `71b082a` updating the calibration decision table, log/scorecard and round-23 receipts/reports. That is branch/path-scoped history evidence, not proof about every branch, untracked file, external consumer, or every possible action.

`git status --short --branch` (exit 0) at inspection began with `## craft/audio-r1` and pre-existing `M .shokunin/audio/LOG.md`; this scout did not edit LOG or shared files. A later status also showed the temporary receipt and this report as untracked; I removed only the receipt directory. I did not run another status after writing this report.

## Boundary observations for the parent

1. Province domain nouns are reasonably concrete (SFX categories, soundtrack/motifs/loops/stems/adaptive layers), but it does not give operational examples or a rule for mixed/uncertain requests. A useful lightweight rule is: audio-only artifact or headless analysis inside `.shokunin/audio/**` is in scope; requests changing engine/game mechanics/narrative, asserting rights/clearance, publishing, or asserting perception without a measured proxy must be refused or routed; uncertain cross-domain ownership must be surfaced rather than guessed.
2. There is a path-wording ambiguity worth resolving in the integrated province checklist: current text says only `.shokunin/audio/**` and “its own reports,” while the round directive describes the final lane report at `.shokunin/reports/round-N/audio.md`. My own permitted report is explicitly `.shokunin/audio/reports/round-24/r24-scout.md`. The province can distinguish these two report locations precisely without broadening source ownership.
3. Checked branch history shows observed changes scoped to audio artifacts/docs/reports; that does not establish that *all* task behavior has never crossed boundaries. SHONEN box 4 should remain a non-author verifier decision; this scout makes no recommendation to check it based only on my inventory/path-limited history review.

## Commands, exits, and limitations

Commands run by this scout and their outcomes are recorded inline above. Also run:

- `git status --short --branch` — exit 0 (described above).
- `git branch --show-current` — exit 0.
- `git log --oneline --decorate -6` — exit 0.
- `git ls-files '.shokunin/audio/**/*.wav' '.shokunin/audio/*.wav'` — exit 0; tracked corpus includes canonical artifacts and many live controls. This glob listing is not a complete inventory of every untracked runtime file.
- `find .shokunin/audio -type f -not -path '*/.git/*' | sort` — exit 0; broad output includes many historical live WAVs and receipts; not repeated here as canonical assets.
- `git diff --name-only 2a198118a527baf749dbd2e23b6667a79a1ccf31..HEAD` — exit 0, empty for that commit range.
- An initial six-command batch was accidentally passed through malformed shell quoting; each command was attempted and returned exit 127 (`git status --short --branch`, `git branch --show-current`, `git log --oneline --decorate -6`, the `find` listing, canonical `find`, and `git ls-files`). These failed wrapper attempts were not evidence; each was then rerun correctly, with the valid results above. No external corpus or perceptual test was run.
