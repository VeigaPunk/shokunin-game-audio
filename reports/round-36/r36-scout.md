# Round 36 scout — ambience baseline, `_alt` rule, and provenance

Scope: read-only mapping of the declared round-36 move. I did not generate or fit a candidate, so there is no candidate SHA, direct measurement, or fit result to report. This is not an admission. All statements below are numeric fixture/provenance observations only; no audition, quality, production, rights, engine, publishing, or promotion claim is made.

## Declared move and existing baseline

The declared clean-before revision is `1fdccc41e936772150fae74131bda1a1ef7e3520` (from `.shokunin/audio/LOG.md`). It has 16 canonical WAV fixtures. The proposed addition is one source-generated `ambience_third.wav`, exactly 2.0 s, 48 kHz mono PCM16, with centroid in 5–200 Hz, peak <.95 FS, RMS >.001, endpoint delta <.03 FS, and side-slope mismatch <.001 FS/sample. Its measured centroid must be at least 10% relative to each existing ambience; duration differences are exactly zero. The declared target is 17 analytic fixtures, with all 16 existing canonical hashes unchanged.

At the declared revision, the deterministic builder SHA-256 is `8d4021d36b56a7b08cfcd9800fe9725107fe266969a6568f3bdb737a3a8a2ec3`; measurement script SHA-256 is `71dc5b3688e9282dc4311cb741ecaa884e9b3d3efe55c379d8cca25220aa8892`. Builder code generates `ambience` as `.15*sin(2π·12t) + .09*sin(2π·36t)` and `ambience_alt` as `.15*sin(2π·20t) + .09*sin(2π·60t) + .06*sin(2π·100t)` over `time(2)`, then saves each using the builder's common save path. Existing artifact hashes at that revision:

| Artifact | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |

The inspected pre-round36 normal receipt `corpus/live/runs/20261013T032851712243Z-normal/measurements.json` reports:

| Artifact | Duration | Peak FS | RMS dBFS | Weighted full-signal centroid | Endpoint delta FS | Side-slope mismatch FS/sample | Ordinary failures |
|---|---:|---:|---:|---:|---:|---:|---|
| `ambience` | 2.0 s | 0.174591064453125 | -18.153351293681563 | 36.61640767851373 Hz | 0.00067138671875 | 0.000030517578125 | none |
| `ambience_alt` | 2.0 s | 0.199737548828125 | -17.67032381358842 | 58.01919713436623 Hz | 0.00189208984375 | 0.0 | none |

The receipt's generic `ambience_alt` comparison reports duration delta 0.0 s, centroid relative delta 0.5845136323520758, `passed: true`.

## Generic `_alt` rule and proposed family comparison

In `measure_audio.py`, every measured name ending `_alt` is paired to its base name. It passes when `abs(duration_delta) >= .020` **OR** `abs(centroid_delta)/baseline_centroid >= .10`. These thresholds are recorded as `distinctness_duration_delta_min_s: 0.02` and `distinctness_centroid_relative_delta_min: 0.1`. For the existing ambience pair durations are equal, so the generic pass is centroid-only: its duration arm is false and centroid arm true. This is a scalar, weighted full-signal centroid criterion, not a spectral-distribution or perceptual test.

The LOG's new third-family selection criterion also requires centroid relative delta >=.10 against **both** `ambience` and `ambience_alt`, but with both target durations fixed at 2.0 s the explicit family comparisons pass the generic OR rule only through centroid. Keep the existing generic `_alt` loop and cutoffs unchanged; the planned addition is an explicit `ambience_family_comparisons` record for the third member, not a new `_alt` artifact. No candidate was attempted here; failed setup/fit do not apply.

## Commands, exits, and scope

Commands run in this scout lane (each shell invocation returned exit code 0):

1. `pwd; git status --short; find .shokunin/audio -maxdepth 4 -type f | sort | tail -80`
2. `git show 1fdccc41e936772150fae74131bda1a1ef7e3520:.shokunin/audio/corpus/fixtures/measure_audio.py | sed -n '1,260p'; echo '--- ambience artifacts'; find .shokunin/audio/corpus -type f -iname '*ambience*' -o -path '*ambience*' | sort; echo '--- round35 scout'; cat .shokunin/audio/reports/round-35/r35-scout.md`
3. `git show 1fdccc41e936772150fae74131bda1a1ef7e3520:.shokunin/audio/corpus/fixtures/build_artifacts.py | grep -n -A28 -B5 'ambience'; git show 1fdccc41e936772150fae74131bda1a1ef7e3520:.shokunin/audio/corpus/fixtures/measure_audio.py | grep -n -A65 -B10 'distinctness'; find .shokunin/audio/corpus/live/runs -name measurements.json | sort | tail -8`
4. `git show 1fdccc41e936772150fae74131bda1a1ef7e3520:.shokunin/audio/corpus/fixtures/build_artifacts.py | sha256sum; git show 1fdccc41e936772150fae74131bda1a1ef7e3520:.shokunin/audio/corpus/fixtures/measure_audio.py | sha256sum; git show 1fdccc41e936772150fae74131bda1a1ef7e3520:.shokunin/audio/corpus/artifacts/ambience.wav | sha256sum; git show 1fdccc41e936772150fae74131bda1a1ef7e3520:.shokunin/audio/corpus/artifacts/ambience_alt.wav | sha256sum; python3 - <<'PY'
import json,glob,os
for f in sorted(glob.glob('.shokunin/audio/corpus/live/runs/*normal/measurements.json'))[-8:]:
 d=json.load(open(f)); print(f,[(k,d['measurements'][k]['duration_s'],d['measurements'][k]['spectral_centroid_hz'],d['measurements'][k]['peak_full_scale'],d['measurements'][k]['rms_dbfs'],d['measurements'][k]['seam_endpoint_delta_full_scale'],d['measurements'][k]['seam_slope_delta_full_scale_per_sample'],d['measurements'][k]['failures']) for k in ('ambience','ambience_alt')],d['distinctness'].get('ambience_alt'))
PY`
5. `git show 1fdccc41e936772150fae74131bda1a1ef7e3520:.shokunin/audio/corpus/fixtures/build_artifacts.py | sed -n '180,196p'; git show 1fdccc41e936772150fae74131bda1a1ef7e3520:.shokunin/audio/corpus/fixtures/measure_audio.py | sha256sum; git show 1fdccc41e936772150fae74131bda1a1ef7e3520:.shokunin/audio/corpus/fixtures/build_artifacts.py | sha256sum; git status --short -- .shokunin/audio`

No fixture build, measure, fit, or candidate command was run; therefore there are no setup/fit failures or candidate evidence. I wrote only this report. No shared source, canonical artifact, LOG, SCORECARD, or other report was edited; no commit or push was made.
