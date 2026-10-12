# Round 3 regression inventory and guard

Reviewer: `r3-regression` (non-author inventory). I inspected the round-3 claim, the round-2 independent verification, builder, and measurement entrypoint. I did not change source or artifacts and made no perceptual claims.

## Before-state at `ef2dc582a597439e986414e7a94c29f6e97158c3`

The commit itself adds only `.shokunin/reports/round-2/audio.md`; the integrated fixture builder and measurement script are present in the tree. The verifier recorded nine deterministic WAVs: `ui`, `ui_alt`, `impact`, `impact_alt`, `movement`, `movement_alt`, `ambience`, `ambience_alt`, and `stem`. I independently checked their current bytes against the same paths at `ef2dc58`: all nine SHA-256 values match.

| WAV | SHA-256 at `ef2dc58` (also current) |
|---|---|
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |

The existing checks are: mono 48 kHz; duration within ±1 ms of each fixture spec; peak <0.95 and RMS >0.001; centroid within fixture-specific bands; for the three loop fixtures, endpoint amplitude delta <=0.03. Variant distinctness is measured against its baseline: duration delta >=0.020 s **or** relative whole-file magnitude-weighted FFT centroid delta >=10%. All nine were passing on verifier receipts `20261012T161812132927Z-normal` and `20261012T161815632474Z-normal`. The four variant results were: UI +0.040 s/+47.19%, impact +0 s/+95.63%, movement +0.120 s/+0.75%, ambience +0 s/+58.45% (duration / centroid). Original five bytes match the earlier pre-variant commit `31d8e9e` according to the independent verifier.

## Existing negative control and coverage gap

The existing `--probe-failing` builder corrupts the ambience tail. Independent verifier receipt `20261012T161822938808Z-failing` exited 1: ambience failed both centroid band and endpoint amplitude delta >0.03. Clean restore `20261012T161825061249Z-normal` exited 0 and restored all nine hashes. This validates the old amplitude check, but **does not isolate slope detection**: centroid also fails, and the old probe is not an equal-endpoint discontinuous-slope control. The clean measurements do not record first-difference/slope values. Thus round 3 needs its specified new probe and independent measurement; this inventory alone cannot support the slope claim.

## Recommended regression guard

Retain all nine fixture specs, baseline/variant pairings, original five hashes, old format/duration/level/centroid/endpoint checks, and four distinctness results. Add a separate decoded-PCM slope-join measurement for exactly `ambience`, `ambience_alt`, and `stem`, with the clean-derived bound documented in the receipt. Include an equal-endpoint probe where endpoint delta remains <=0.03 but slope metric exceeds that bound; assert the endpoint test passes and the slope test alone rejects it. Run that probe without overwriting canonical clean artifacts, then rerun the regular negative-amplitude probe and clean restore. Regression passes only when all nine clean fixtures pass, original hashes and distinctness remain unchanged, the old negative probe still fails/restores, and the isolated slope probe fails for the slope reason (not centroid, format, duration, or level). This is a numerical local-fixture guard, not evidence of audible or playback seamlessness.

## Commands and exit codes

- `git show ef2dc58 --stat && git status --short && git rev-parse ef2dc58` — exit 0.
- `sha256sum .shokunin/audio/corpus/artifacts/*.wav; git status --short; git show --format=fuller --stat ef2dc58` — exit 0.
- `python3 -c 'import hashlib,subprocess,pathlib; names="ui ui_alt impact impact_alt movement movement_alt ambience ambience_alt stem".split(); [(lambda n,b,c: print(n, hashlib.sha256(b).hexdigest(), hashlib.sha256(c).hexdigest(), "MATCH" if b==c else "DIFF"))(n,subprocess.check_output(["git","show",f"ef2dc58:.shokunin/audio/corpus/artifacts/{n}.wav"]),pathlib.Path(f".shokunin/audio/corpus/artifacts/{n}.wav").read_bytes()) for n in names]'` — exit 0; all nine `MATCH`.
- `git show ef2dc58:.shokunin/audio/corpus/artifacts/ui.wav | sha256sum; git show ef2dc58:.shokunin/audio/corpus/artifacts/ui_alt.wav | sha256sum` — exit 0 (spot-check; included in full comparison).
- Initial attempted per-file command template `git show ef2dc58:.shokunin/audio/corpus/artifacts/<name>.wav | sha256sum` (run for each of the nine names) — exit 127 each; shell-wrapper quoting made the full command string a command name (`No such file or directory`). This was command construction only; the corrected single Python command above verified all nine.
- Initial attempted Python comparison command passed as one doubly-quoted shell string — exit 127 (`python3 -c '...names=ui...`: `ui: command not found`) due wrapper quoting. The corrected quoted Python command above exited 0.
