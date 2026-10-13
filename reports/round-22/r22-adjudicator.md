# Round 22 — independent depth adjudication (r22-adjudicator)

## Decision

| Owned axis | Verdict | Basis |
|---|---|---|
| Depth | **Improved, narrowly** | The prior `measure()` accepted a matched native 48 kHz mono PCM24 input with `failures: []`; the integrated shared format predicate now requires `codec_name == "pcm_s16le"` **and** `bits_per_sample == 16` alongside 48 kHz mono. The native PCM24 control is rejected **only** as `format: expected PCM16`, and matched native PCM16 still passes. |
| Coverage | **Unchanged** | All 19 serial runner executions retain their historical exits and failure kinds; the existing four invalid controls retain outcomes. The two new width controls exercise the depth predicate, not a new acoustic gate or separately credited coverage axis. |
| Calibration | **Unchanged** | All replayed receipt threshold objects are identical; no numeric signal gate was retuned. This round does not claim a new threshold boundary or perceptual calibration. |

**Admit this one depth move:** one demonstrated improvement, zero demonstrated harm to the three owned axes. SHONEN box 4 **remains open**; this is not a whole-lane review.

## Evidence and fit

The declared baseline is `14cf9861ca19041ddb25c322facc5ace9271a146`. Its `measure_audio.py:measure()` queries stream sample rate and channels (plus container duration), rejects non-48 kHz/non-mono, then SoX-decodes to float for the existing numeric checks. It has **no encoding/bit-width condition**. Wave-1 executor and independent alternate generated matched analytic PCM16/PCM24 WAV pairs: with suitable existing numeric specs, both widths returned `failures: []` from original `measure()`; critic also confirmed passing matched 16/24 conversions of an existing source and a passing float32 case. The executor's direct measurement establishes the before behavior of `measure()`, not pre-change CLI `--probe-invalid` acceptance. Scout's initially mismatched UI-spec run failed duration/centroid, not format; exploratory quoting/path mistakes and these confounded fits are not evidence of width rejection. Scribe and reviewer were design/decision reviews, not integration passes; simplifier identified the shared-predicate path; guard inventoried the 13 hashes and 19 historical executions. All eight wave-1 reports are in this directory, and none alone establishes the after state.

Source diff against `14cf986` adds `build_width_probes()` under `corpus/live/round-22/` to render the same 4-second 440 Hz sine as PCM16 and packed PCM24; it does not alter canonical WAV construction. It adds `format_failures(stream)` and uses it in both `measure()` and the format-invalid classifier. ffprobe now requests `codec_name,bits_per_sample` as well as rate/channels; `sample_fmt` is **not** queried or used in the predicate. Rate/channel and existing numeric comparators remain unchanged. The opt-in invalid mode has a six-record list and admits the native16 expected-positive while requiring native24 `observed_failure: format`. This is an explicit native `pcm_s16le`/16-bit policy for these tested WAVs, not merely a PCM24 blacklist.

Non-author `r22-verifier.md` serially replayed 19 invocations, exits `[0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0]`, with no setup exit 2. Its invalid receipt `corpus/live/runs/20261013T010824568740Z-invalid/measurements.json` records four old outcomes (`section count`, `decode`, `format`, `section count`), native16 `expected_pass`/no failure (`pcm_s16le`, 16 bits), and native24 `expected_failure`/`format` (`pcm_s24le`, 24 bits); both new controls report 48,000 Hz mono. Its corrected, resolved-absolute-path direct `measure()` calls on the matched executor files exited 0 at the shell: PCM16 `failures: []`, PCM24 solely `format: expected PCM16`. Its two preceding relative-path invocations exited 1 during path serialization and are excluded as setup errors, not codec results. Verifier confirms 13/13 canonical SHA-256 matches against baseline, five `_alt` distinctness records pass, old failure sets hold, all replay threshold objects match, and initial/restored normal parsed JSON matches after removing path identity. Raw normal receipts `20261013T010810788169Z-normal` and `20261013T010825350561Z-normal` each have thirteen measurement records without failures; the raw invalid record independently agrees with the verifier summary.

## Scope and possible harm

`sample_fmt=s32` for native PCM24 describes the decoder's sample representation; it does **not** mean that the stored encoding is PCM32. The alternate's WAVE_FORMAT_EXTENSIBLE 24-bit container / 20-valid-bit sample still appears as `pcm_s24le`, 24 bits in the queried ffprobe metadata: `bits_per_sample` here is not proof of valid precision. This round does not resolve extensible valid bits or arbitrary WAV, codec, container, multistream, or export support.

New `codec_name` and `bits_per_sample` keys appear in normal measurement JSON and selected invalid records, and `expected_pass` appears in invalid results. A strict external JSON consumer **could** be affected; no external consumer inventory or compatibility test was supplied, so absence of such harm is unproven, not asserted. In the scoped runner receipts, old records/outcomes and normal restoration persist; this potential downstream schema risk does not show an owned-axis regression. Not querying or requiring `sample_fmt` is deliberate for this encoded-width criterion but leaves decoder-format and valid-bits questions outside scope. The observed format rejection is not an audibility judgment, universal WAV validator, security hardening, engine/production guarantee, or sample-rights assertion.

## Adjudicator commands and exits

From repository root, I ran only read-only shell checks:

- `git diff 14cf9861ca19041ddb25c322facc5ace9271a146 -- .shokunin/audio/corpus/fixtures/measure_audio.py .shokunin/audio/corpus/fixtures/build_artifacts.py` — exit **0**; inspected the source changes summarized above.
- `git show 14cf9861ca19041ddb25c322facc5ace9271a146:.shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**; inspected the original rate/channel-only predicate.
- `git diff --check 14cf9861ca19041ddb25c322facc5ace9271a146 -- .shokunin/audio/corpus/fixtures/measure_audio.py .shokunin/audio/corpus/fixtures/build_artifacts.py` — exit **0**, no whitespace errors in these source diffs.

Other inspections used Python filesystem reads of LOG, eight wave-1 reports, verifier, source, and the named raw receipts; I did not independently rerun the audio CLI or claim its exits as my own. No canonical, shared-source, LOG, or SCORECARD file was edited, and I made no commit or push.
