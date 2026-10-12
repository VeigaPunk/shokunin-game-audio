# Round 19 critic — scope of the 200 Hz threshold-boundary claim

## Finding

The +2/+3 pair is useful evidence of a **local numeric boundary**, not a calibration of perception, all signals, or even all PCM perturbations. It supports the narrow statement that for this particular canonical 200 Hz layer, at frame 96001, with a positive one-frame edit and SoX float32 decode, the calculated side-slope difference moves from 32 to 33 signed PCM counts: `32/32768 = 0.0009765625` passes and `33/32768 = 0.001007080078125` fails the existing strict `> 0.001` predicate. The runner source has the strict comparison `... > .001`; therefore equality would pass. Neither tested value is equality: the threshold in this scale is `0.001 * 32768 = 32.768` counts, between the two integer outcomes.

This does **not** show that a fixed “32/33 count boundary” holds for arbitrary samples, waveform identity, edit position, edit direction, codec, sample rate, or decoder. The measurement is an absolute full-scale difference of adjacent slopes, not a relative threshold normalized to the signal amplitude. Its consequences therefore depend on the surrounding signal and edit. The two files are not identical signals except for a single PCM sample, and even that one-sample change also changes spectral measurements. Executor values keep centroid within the declared band, but this is not an isolated physical slope intervention or a perception experiment. “Sole failure” is only justified as a named-gate result when the *full integrated runner receipt* reports it; this lane inspected source and scratch evidence, not such receipts. In particular, `section_contrast()`'s `passed` field tests section amplitude validity/contrast, not the internal join gap or slope predicate.

## Evidence audit and reproducibility

Round 19 executor report states it copied canonical PCM16 and changed only frame 96001 (`43→45` and `43→46`), then decoded with SoX. I independently checked the candidate identities against the canonical WAV. Exact command and exit:

```sh
python3 -c 'import wave, numpy as np; from pathlib import Path; base=Path(".shokunin/audio/corpus/artifacts/stem_layer_third.wav");
for name in ("edgepass_candidate.wav","edgefail_candidate.wav","plus1.wav","plus2.wav","plus3.wav","plus4.wav"):
 p=Path(".shokunin/audio/corpus/live/round-19")/name
 with wave.open(str(p),"rb") as w: a=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2").copy()
 with wave.open(str(base),"rb") as w: b=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2").copy()
 d=np.flatnonzero(a!=b); print(name, len(a),len(d), [(int(i),int(b[i]),int(a[i])) for i in d[:4]], "slope-count-delta",int(abs((a[96001]-a[96000])-(a[95999]-a[95998]))))'
```

Exit **0**. For the two named candidates it reported 192000 frames and exactly one changed index, 96001, with `43→45` and `43→46`; corresponding integer slope mismatches were 32 and 33. The additional `plus1` through `plus4` files were present in shared scratch, but this critic did not treat them as validated runner modes or independent tests.

Exact hash command:

```sh
sha256sum .shokunin/audio/corpus/artifacts/stem_layer_third.wav .shokunin/audio/corpus/live/round-19/edgepass_candidate.wav .shokunin/audio/corpus/live/round-19/edgefail_candidate.wav
```

Exit **0**. Hashes: canonical `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`, pass `512b38026eb102fac4773bca1b61e7994261b6f6297e0ec544fb4b47b1104496`, fail `48e2167dd405d05dc66aab304fc7b3c4712d2734dca021fdfd92d15a3e8d2a38`. This corrects the executor report's visibly truncated source-hash transcription; candidate hashes agree with its report.

SoX float32 PCM values use the signed PCM16 scale `integer / 32768` on this decoded path (including the asymmetric signed range); thus the denominator is 32768, not 32767. This is confirmed by the reported exact decoded differences. For reference, exact commands quoted by executor for decode were:

```sh
sox .shokunin/audio/corpus/live/round-19/edgepass_candidate.wav -t f32 -e floating-point -
sox .shokunin/audio/corpus/live/round-19/edgefail_candidate.wav -t f32 -e floating-point -
```

Both exited **0**. These commands write raw samples to stdout; no sample count/value display is included in the command, so the numerical table is executor-derived unless an integrated receipt independently records the results.

## Failure-isolation challenge

The executor's listed direct metrics predict both candidates pass format/duration/level/centroid, outer endpoint and slope, section contrast, and internal gap; +2 should pass internal slope while +3 fails it. Those data are internally consistent with a sole numeric failure **for the listed checks**, but this critic has not run the integrated entry point. Also distinguish `section.passed` (contrast/validity) from the complete `measurements[*].failures` list. Do not state runner-level sole failure or confirm unchanged prior modes from this report. A scratch WAV is not a registered probe mode; provenance alone does not show the artifact is consumed by the runner.

## Verdict and limits

The pair can improve disclosure of **local threshold resolution**, if independent runner receipts later verify the two opposing outcomes with no other failure. It cannot establish perceptual calibration or generalization to “every signal.” Keep the unchanged `.001` bound, denominator, strict comparison, signal identity, positive edit direction, exact frame, PCM format and SoX decoder in the claim. No audible, engine, production, security, rights, or compatibility assertion follows. No source, canonical WAV, LOG, SCORECARD, or commit was changed here.
