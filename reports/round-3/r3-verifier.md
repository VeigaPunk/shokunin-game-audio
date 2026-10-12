# Round 3 independent verification

Reviewer: `r3-verifier` (non-author replay). I independently invoked the integrated fixture builder/measurement entrypoint and inspected the resulting receipts and canonical WAV hashes. I changed no scripts or canonical artifacts. These checks verify numerical fixture behavior only; they do not establish audible seamlessness, playback/codec behavior, production readiness, or sample rights.

## Replay results

Commands ran from the repository root. `measure_audio.py` invokes the deterministic builder before measurement; slope mode also measures the separately retained scratch probe.

| Command | Exit | Receipt | Failure result |
|---|---:|---|---|
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T162822089971Z-normal/measurements.json` | none; all nine clean fixtures passed |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 (expected) | `corpus/live/runs/20261012T162835463500Z-slope/measurements.json` | only `slope_probe`: `loop seam: slope mismatch > .001 full scale per sample` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 (expected) | `corpus/live/runs/20261012T162835970021Z-failing/measurements.json` | only `ambience`: centroid band and endpoint delta failures (existing negative control) |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T162836475076Z-normal/measurements.json` | none; all nine clean fixtures passed after restore |

There was an initial command-wrapper mistake: passing the entire command as an unquoted string to `bash()` made the shell treat it as one executable name (exit 127). I recorded that telemetry and reran each command with the normal `bash(command)` invocation; the successful replay results above supersede that command-construction failure. No fixture conclusions are based on the failed invocation.

## Isolated slope control and clean distribution

The slope receipt reports the scratch probe endpoint delta as `0.0` and slope mismatch as `0.469970703125` FS/sample. It has valid 48 kHz mono, 1.0 s duration and passes the configured centroid and level checks; its sole failure is slope mismatch. The probe’s SHA-256 is `91b4a324124ef8a54b0dc25eea584f3e08f1451090e1413b15d7325ec8bde99f` (96,044 bytes). Thus the equal-endpoint positive control isolates the new metric as intended.

Clean loop slope mismatches across ambience, ambience_alt, and stem were respectively `0.000030517578125`, `0`, and `0.000030517578125` FS/sample in the normal receipt, all below the configured `0.001` bound. Their endpoint deltas were `0.00067138671875`, `0.00189208984375`, and `0.011383056640625`, all below `0.03`. The failing amplitude probe has ambience endpoint delta `0.49932861328125` and slope mismatch `0`; it still fails endpoint and centroid checks, not the new slope check. This confirms the controls distinguish the two checks.

## Coverage and regression guards

I compared SHA-256 hashes of all nine canonical WAVs against their bytes at before-state commit `ef2dc582a597439e986414e7a94c29f6e97158c3`; every hash matched. Hash list (before and after identical):

- `ui.wav` `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`
- `ui_alt.wav` `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`
- `impact.wav` `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc`
- `impact_alt.wav` `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`
- `movement.wav` `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d`
- `movement_alt.wav` `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`
- `ambience.wav` `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`
- `ambience_alt.wav` `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc`
- `stem.wav` `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0`

All four distinctness checks passed in the clean normal and restoration receipts. Duration / centroid-relative deltas were UI `0.040 s / 47.19%`, impact `0 / 95.63%`, movement `0.120 s / 0.75%`, ambience `0 / 58.45%`. The existing amplitude negative control still fails and canonical fixture restoration passes.

## Calibration and scope

The `0.001` FS/sample threshold is about 32.8 times the maximum observed clean mismatch in these three fixtures; the constructed probe is about 470 times the bound. This is a conservative fixture-local calibration, not a universal or perceptual threshold. A local one-sample first-difference comparison can miss other kinds of discontinuity and does not model playback block boundaries or codecs.

**Verification finding:** the planned additional numerical depth proxy is independently reproduced, its equal-endpoint slope control fails only for slope, all nine clean artifacts and existing variant distinctness remain intact, and the old amplitude control still works. Coverage and calibration guards appear unchanged in these replays; the evidence supports only the stated numerical fixture claim.

## Commands / telemetry

- `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` — exit 0, receipt `20261012T162822089971Z-normal`.
- `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` — exit 1, receipt `20261012T162835463500Z-slope`.
- `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` — exit 1, receipt `20261012T162835970021Z-failing`.
- `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` — exit 0, receipt `20261012T162836475076Z-normal`.
- Initial malformed `bash()` command-string invocation for each of those modes — exit 127; corrected invocation above succeeded.
- Python SHA-256 comparison against `git show ef2dc582...:<artifact>` for all nine canonical WAVs — exit 0, all match.
