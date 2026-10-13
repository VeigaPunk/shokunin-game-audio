# Round 35 scout — movement baseline and rule map

Scope: read-only mapping for the declared round-35 coverage move. No candidate was generated or measured in this scout lane; this is not a fit result or admission. No audition/perceptual, quality, production, rights, engine, publishing, or promotion claim is made.

## Before-state and provenance

Declared clean-before revision in `.shokunin/audio/LOG.md`: `56f2b0f8d244966c13ebfd7b28d521e3825dd3aa`. The existing movement family contains `corpus/artifacts/movement.wav` and `movement_alt.wav`; the declared target is a new, source-generated `movement_third.wav`, measured as a third family member, not an `_alt`.

The deterministic builder (`corpus/fixtures/build_artifacts.py`, SHA-256 `3107e6c183d4d8885783bf44666e6222cb649c06ba4f3e0f047f2e01483a784c`) creates the original movement from the shared `np.random.default_rng(20261012)` stream after generating the impact noise, with .24 s duration and the expression `.24 * noise * (1-np.exp(-250*t)) * np.exp(-22*t)`. It creates movement_alt from an independently seeded `np.random.default_rng(20261013)`, .36 s, using `.30 * noise_alt * (1-np.exp(-180*t)) * np.exp(-15*t)`. Builder output is mono 48 kHz PCM16 (`save`). Existing artifact SHA-256s:

| Artifact | SHA-256 |
|---|---|
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |

The latest pre-integration normal receipt inspected was `corpus/live/runs/20261013T032851712243Z-normal/measurements.json` (its schema reports mode/metrics by artifact name). It records both artifacts at 48 kHz, mono, PCM16, with no ordinary failures:

| Artifact | Duration | Peak FS | RMS dBFS | Weighted full-signal centroid |
|---|---:|---:|---:|---:|
| movement | 0.24 s | 0.5394897461 | -23.7799408323 | 11934.4840459463 Hz |
| movement_alt | 0.36 s | 0.6393127441 | -21.9873156163 | 12024.2148793488 Hz |

The recorded alt-vs-baseline duration delta is 0.12 s and centroid relative delta is 0.0075186186. The existing generic rule therefore passes via duration, not centroid. These are numeric fixture proxies, not judgments of what a listener hears.

## Generic `_alt` OR rule and proposed third-family check

`corpus/fixtures/measure_audio.py` (SHA-256 `4ab6dd78cb5eed7741060782b1e0fbedd46684091007b6347794202ad66cb8a9`) iterates measured names ending `_alt`, pairs each with the name minus `_alt`, and passes distinctness iff `abs(duration_delta) >= .020 s OR abs(centroid_delta)/baseline_centroid >= .10`. The threshold receipt calls these `distinctness_duration_delta_min_s: 0.02` and `distinctness_centroid_relative_delta_min: 0.1`. This is a disjunction: duration alone suffices; the centroid criterion is not independently required for an `_alt` pass. Do not change the generic loop or cutoffs for this proposed family addition.

The LOG declares `movement_third.wav` target duration .30 s, movement centroid band 100–16000 Hz, peak <.95 FS, RMS >.001, format 48 kHz mono PCM16. It additionally requires measured centroid relative difference >=.10 against **each** of `movement` and `movement_alt` as a selection criterion, while the duration differences (.06 s from each) exceed the generic .020 s OR arm. Thus the declared third-family check is stricter than the generic rule for centroid selection, but the OR pass itself would still be satisfied by duration. The intended integration adds the deterministic builder save, `SPECS["movement_third"]=(.30,100,16000,False)`, and explicit comparisons to both existing movement artifacts, leaving older 15 fixture hashes and the generic `_alt` behavior unchanged. A candidate not meeting the declared fit criteria is a failed fit, not a reason to relax them.

## Shell activity and limits

No shell command was run in this scout lane, so there are no shell commands or exit codes to report. No fit/setup attempt was made. I only read the declared LOG, builder, measurement script, existing WAV hashes, and an existing normal measurement receipt. No shared source, canonical artifact, LOG, SCORECARD, or other report was edited; this report is the only output from this lane. No commit or push was made.
