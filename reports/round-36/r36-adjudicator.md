# Round 36 Sol adjudication — analytic ambience coverage

## Verdict

**Admit the one declared coverage move, narrowly.** Against clean-before `1fdccc41e936772150fae74131bda1a1ef7e3520`:

| Axis | Verdict | Basis |
|---|---|---|
| Coverage (declared axis) | **Improved** | A third original, deterministic 2-second ambience fixture is canonical and measured; the corpus grows from 16 to 17 valid-mode analytic WAV entries and has two explicit ambience-family comparisons. |
| Depth | **Unchanged** | No new acoustic dimension, threshold, perceptual test, or deeper validation is demonstrated. |
| Calibration | **Unchanged** | Existing tests and thresholds remain stable; explicit receipt and setup exclusions maintain the prior evidence boundary rather than establish an additional calibration gain. |

At least one scoped axis improved and **zero demonstrated scoped harms**: admit only this narrow analytic fixture-coverage addition. This is not a rank promotion: **SHONEN four checked, no rank change**. No other fixture or sound-development claim is admitted.

## Evidence examined

I read the round-36 LOG declaration, all eight wave-one reports (`r36-scout`, `executor`, `alt`, `critic`, `reviewer`, `simplifier`, `scribe`, `guard`), named non-author `r36-verifier.md`, raw initial normal, final restore, and invalid receipts, and source/artifact status/diff relative to `1fdccc4`. The integrated builder adds only `save("ambience_third", .20*sin(2π·90t)+.025*sin(2π·130t))` in its existing deterministic 48-kHz PCM16 save path; measurement adds its `(2.0, 5, 200, True)` specification and two explicit `ambience_family_comparisons`. The generic five-pair `_alt` loop and `.020 s OR .10` predicate are unchanged. The new canonical WAV is untracked relative to clean-before pending parent commit; its bytes have SHA-256 `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404`, matching the independent selected alt scratch candidate. The executor's separate 110-Hz candidate was not selected. The source diff changes only these builder/measurement additions; no old artifact is shown modified. The independent verifier additionally compared all **16** old artifact hashes against `1fdccc4` and all old normal measurement records against the earlier normal receipt; all matched. My direct raw-receipt comparison likewise found all 16 records equal excluding `path`.

Raw normal receipt `corpus/live/runs/20261013T035441105253Z-normal/measurements.json` measures `ambience_third.wav` at **2.0 s / 96,000 frames, 48,000 Hz mono PCM16** (WAV header independently inspected), peak **0.225006103515625 FS** (<.95), RMS **−16.92261930553234 dBFS** (> .001 FS), weighted whole-signal centroid **112.03210352691181 Hz** (5–200), loop endpoint delta **0.002777099609375 FS** (<.03), side-slope mismatch **0.0 FS/sample** (<.001), ordinary failures `[]`. It contains 17 canonical measurements; the invalid-mode receipt #29 contains no canonical measurement set. Explicit ambience pairs are:

| Pair | Duration delta (s) | Baseline-relative centroid delta | Predicate |
|---|---:|---:|---|
| `ambience` → `ambience_third` | 0.0 | 2.059614818322321 | centroid-only pass |
| `ambience_alt` → `ambience_third` | 0.0 | 0.9309488765840295 | centroid-only pass |

Both **duration arms are false** (0 < .020); both centroid arms are true (≥.10). The generic five `_alt` records and the UI, impact, and movement third-family records agree exactly with the prior raw normal receipt. Existing thresholds match; only the expected `[5,200]` centroid-band mapping for the third ambience is added. The critic's changed-line-spectrum, near-same-centroid example would fail this gate despite different spectra: a **false negative** showing that scalar centroid is not a spectral-distribution or perceptual-novelty test. Boundary endpoint/slope checks are numeric seam proxies, **not audible seamlessness**.

## Non-author serial replay and setup boundary

Named non-author verifier's **34 corrected serial commands** each produced its cited receipt: **13 exit 0, 21 expected probe exit 1**, no other corrected-run exits or setup errors. Prior33 #1–#33 remain **12 exit 0 / 21 expected exit 1**; #34 is an additional normal restore. Every valid-mode receipt has 17 canonical measurements, ordinary checks passing for the new fixture; #1, #30, #31, #32, #33, and #34 normal receipts match after excluding paths. The eight #29 invalid statuses are `short_sections=expected_failure(section count)`, `corrupt=expected_failure(decode)`, `wrong_format=expected_failure(format)`, `odd_sections=expected_failure(section count)`, `native16_probe=expected_pass`, `native24_probe=expected_failure(format)`, `stereo48_probe=expected_failure(format)`, `mono441_probe=expected_failure(format)`. The verifier's **34 initial wrapper exit-127 attempts yielded no receipts** and are **excluded setup errors**, not gate observations or 34 failed fixture fits. The executor's initial relative-path helper exit 1 was also setup, followed by corrected fit exit 0. No failed selected-candidate fit is reported. Exact per-mode runner commands/exits and receipt paths are preserved in `r36-verifier.md`; e.g. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` → exit 0 on #1/#30–#34 and `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` → expected exit 1 on #29.

## This adjudicator's commands and limits

I ran only read-only shell commands:

- `git diff 1fdccc41e936772150fae74131bda1a1ef7e3520 -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py; git status --short -- .shokunin/audio/corpus/artifacts .shokunin/audio/corpus/fixtures` — combined shell exit **0**; source files modified and `ambience_third.wav` untracked as expected.
- `git diff --check 1fdccc41e936772150fae74131bda1a1ef7e3520 -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py .shokunin/audio/corpus/artifacts; git diff --name-status 1fdccc41e936772150fae74131bda1a1ef7e3520 -- .shokunin/audio/corpus/artifacts` — combined shell exit **0**, no tracked artifact diff. The untracked new WAV is separately evidenced by SHA and header; `git diff` alone does not include it.

All receipt/file comparisons and WAV-header/SHA inspection in my lane used Python REPL reads, not shell commands. I did **not** rerun the 34 modes, synthesize or audition sound, edit shared source/artifacts/LOG/SCORECARD, commit, or push. The admitted result proves only analytic fixture coverage. It does **not** establish auditory quality, audible seamlessness, full-spectrum/perceptual novelty, production readiness, rights, engine suitability, publishing, or promotion. Parent may commit scoped `.shokunin/audio/**` work and write the report-last summary separately; no push or merge is authorized by this verdict.
