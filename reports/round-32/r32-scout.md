# Round 32 scout — existing distinctness OR map

## Predicate and per-file ordinary duration

The runner's `_alt` comparison in `corpus/fixtures/measure_audio.py:309–317` derives actual measured duration difference and baseline-relative absolute centroid difference, then evaluates:

```python
passed = duration_delta >= .020 or centroid_relative_delta >= .10
```

The reported distinctness failure is appended to the alternate only when both arms are false. This is separate from each file's ordinary check in `measure()` (`measure_audio.py:67–90`): its supplied per-file spec sets expected duration and the ordinary duration tolerance is ±.001 s. UI ordinary spec is `SPECS["ui"] = (.12, 250, 4000, False)` (`:15`). New probes must not confuse the pairwise OR with per-file conformance.

| Duration arm (`delta >= .020`) | Centroid arm (`abs(variant-base)/base >= .10`) | OR result | Existing evidence |
|---|---|---|---|
| false | false | reject | Round 31 joint-below: nonzero deltas `.019978999999999997` and `.09964036511023265`; intended distinctness-only exit 1. |
| true | false | pass | Round 27 duration-below fails and duration-at passes, with centroid arm false in both; see `r27-adjudicator.md`. |
| false | true | pass | Round 28 centroid below/above and Round 29 lower-centroid below/above exercise centroid-only comparisons at duration delta 0; see `r28-adjudicator.md`, `r29-adjudicator.md`. |
| true | true | pass | Not established by the cited round-27–31 pair comparisons; the OR's code predicts pass, but don't present it as an observed joint case. |

Nuance for the declared Round 32 gap: centroid-only earlier cases have **zero** duration delta. They prove the OR can pass with only the centroid arm true, but do not supply the missing integrated pair where **both measured signals are nonzero**, duration remains below `.020`, and centroid is at/above `.10`. Round 31 is the converse joint-below pair (both nonzero, both false). The requested Round 32 observation is the missing mixed-signals cell, not a wholly untested Boolean OR row.

## Existing source-generated examples and their per-file specs

- Round 27 (`--probe-ui-duration-below/at`): baseline is 5760 frames (0.120000 s); alternate is 6719 frames (0.139979 s) or 6720 frames (.140000 s). Both ordinary measurement calls use canonical `SPECS["ui"]` in the old runner, so the longer alternate is not ordinary-duration compliant; these are historical OR-polarity examples, not a model for Round 32's ordinary-check requirement. Adjudicator documents measured deltas, ordinary duration consequence and results.
- Rounds 28–30 centroid/orientation probes: both baseline and alternate are 5760 frames, 48 kHz mono PCM16 and measured with `SPECS["ui"]` (canonical .12 s). Round 28 and 29 provide centroid-only below/above observations; Round 30 swaps baseline/alternate roles for the same two files and remains duration delta 0. See respective adjudicators for exact results.
- Round 31 joint-below: builder generates baseline `ui_joint_below` at 5760 frames, k=1.0, and `ui_joint_below_alt` at 6719 frames, k=.88 (`build_artifacts.py:129–136`). Runner `measure_audio.py:301–304` measures baseline with canonical `SPECS["ui"]`, but declares alternate expected duration `(6719 / 48000, *SPECS["ui"][1:])`. This alternate's measured duration is .139979 s, so it **does not conform to canonical .12 s duration**; separate scratch-duration checking lets its ordinary format, level and centroid-band checks pass. The independent joint receipt recorded both OR signals nonzero/below and only distinctness failure; see `reports/round-31/r31-verifier.md` and `r31-adjudicator.md`.
- Round 32 declared contract (LOG, “Round 32 declared depth claim and wave spec”): retain 5760-frame baseline/canonical UI spec and 6719-frame alternate with a separately declared 6719/48000 scratch duration. Required measurement is duration delta nonzero `<.020`, centroid relative delta nonzero `>=.10`, both files passing their own ordinary checks, and existing OR pass via centroid arm. The longer variant remains nonconforming to canonical .12 s duration. No threshold change or canonical asset replacement.

## Provenance, exclusions, limits

I read `.shokunin/audio/LOG.md`, the current fixture source, and the round 27–31 adjudicators cited above. I ran no shell commands and performed no runner replay; thus there are no commands or exits attributable to this scout. Round 31's LOG separates the prior k=1.0 centroid candidate (~.1353) as a **failed numeric fit** from executor relative-path exit 1 / critic helper-path error as **setup errors**, not gate results. The round-31 verifier reports 29 serial invocations and its receipt-backed outcomes; its integrated joint-below negative is intended exit 1, not setup failure. Don't conflate any of these with a Round 32 fit or runner result; no Round 32 measurement was run here.

This maps a fixture's numeric OR logic only. It establishes no exact cutoff equality, causality or branch independence, perceptual/audible distinction, rights, engine behavior, publication, or promotion. In particular, the scratch variant is not canonical `.12 s` duration-conforming.
