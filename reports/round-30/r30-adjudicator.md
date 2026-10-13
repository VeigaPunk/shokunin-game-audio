# Round 30 adjudicator — independent per-axis verdict

**Admit round 30, narrowly.** One declared **calibration** move is supported: the existing absolute centroid difference divided by the **baseline** centroid yields opposite decisions when the *same two whole WAV files* exchange baseline/alternate roles. Calibration **improved**; depth **unchanged**; coverage **unchanged**. No scoped axis is harmed. This satisfies the declared admission rule (at least one improved, zero demonstrated scoped harm), without changing checker policy.

## Before, implementation, and independent evidence

Clean-before commit `6a3696822741388d862243745f653a76eec21d1f` already had the round-29 k=1.00 baseline → k=.95 alternate test, which failed distinctness at `0.09901901500217196`. The round-30 LOG declared a swapped-role two-mode test before integration. I read its declaration and integration/replay entries, all eight wave-1 reports (`r30-{scout,executor,alt,critic,reviewer,simplifier,scribe,guard}.md`), and the separate non-author `r30-verifier.md`. The scout/reviewer/simplifier/scribe proposed behavior, and executor/alt/critic supplied direct *pre-integration* fit evidence, not runner-gate receipts; guard recorded the preserved baseline. The critic explicitly warned that fit alone could not prove integrated mode attribution.

The source diff versus `6a36968` adds only opt-in `--probe-ui-orientation-forward` and `--probe-ui-orientation-reverse` generation, dispatch, measurements, and receipt labels. Both use `SPECS["ui"]` and the existing name-ending-`_alt` pairing. Source still computes `abs(variant_centroid - base_centroid) / base_centroid` and `duration_delta >= .020 or centroid_relative_delta >= .10`. There is no symmetric denominator, changed threshold, or canonical fixture replacement. The two roles generate the same analytic UI PCM16 source at `k=1.00` and `.95`, swapping their measurement names.

I inspected the non-author's raw forward/reverse receipts, corresponding raw WAV files, initial/restored normal receipts, and invalid receipt. Direct whole-file SHA-256 inspection agrees with the verifier:

| Member | Centroid Hz | Whole-file SHA-256 | Ordinary UI checks |
|---|---:|---|---|
| forward baseline = reverse alternate, k=1.00 | 966.8966593379727 | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | pass in both roles |
| forward alternate = reverse baseline, k=.95 | 871.155504521436 | `6e626b9b5b177cd6f7ba986758b12ec612cf003f9947bd170b766f1652d9bac2` | pass as an ordinary fixture in both roles |

Each of these four paths is 5760 frames, 48 kHz, mono, PCM16, duration `.120 s`, under the unchanged canonical UI format/duration/level/centroid-band checks. The forward alternate's **only** failure is the separately applied distinctness rule. Both duration deltas are **0**. Thus the unchanged duration arm does not decide either case; the identical absolute centroid gap `95.7411548165367 Hz` is divided by different baseline centroids:

- Forward receipt `corpus/live/runs/20261013T023818100104Z-ui-orientation-forward/measurements.json`: `95.7411548165367 / 966.8966593379727 = 0.09901901500217196 < .10`; sole `ui_orientation_forward_alt` distinctness failure, runner **exit 1**.
- Reverse receipt `corpus/live/runs/20261013T023818983830Z-ui-orientation-reverse/measurements.json`: `95.7411548165367 / 871.155504521436 = 0.10990133715464667 > .10`; no failure, runner **exit 0**.

Those exit codes are independently executed by the named non-author verifier, not inferred from the pre-integration fits. Source, receipt baseline names, ordinary-check results and raw bytes agree. This establishes the proposed numerical orientation property at the two measured points, not an exact cutoff-equality result.

## Preservation, command provenance, and verdict

The verifier's corrected **28 actual serial runner invocations** have **8 exit 0, 20 expected gate exit 1, no exit 2**, with a receipt for each. Its historical prior-26 subset is replay #1 plus #4–#28 (7 exit 0, 19 exit 1); #2 and #3 are the new forward/reverse modes. The invalid receipt `corpus/live/runs/20261013T023839657513Z-invalid/measurements.json` contains all eight expected statuses (seven `expected_failure`, one native16 `expected_pass`). Initial and restored normal receipts (`20261013T023817208830Z-normal` and `20261013T023840471149Z-normal`) have empty failures, identical five original `_alt` distinctness results, and identical threshold objects; the thirteen canonical artifact SHA-256 values remain those of `6a36968` as independently enumerated in `r30-verifier.md`. The 28 earlier **exit-127** command-wrapper attempts produced **no receipts**: setup errors, excluded from all gate counts and never treated as 28 failed runner checks. The executor's initial relative-path exit 1 was likewise a setup failure; its corrected direct measurement exit 0 remains pre-integration candidate evidence, not the non-author replay.

| Axis | Verdict | Reason |
|---|---|---|
| **Calibration** | **improved narrowly** | Byte-swapped, ordinary-passing samples and non-author receipts isolate the baseline-denominator orientation of the unchanged `.020 OR .10` rule with forward rejection/reverse acceptance. |
| **Depth** | **unchanged** | The runner adds two opt-in applications of existing UI and `_alt` checks, not another signal measure or deeper validation. No established checks regressed in the corrected replay. |
| **Coverage** | **unchanged** | Two source-generated scratch-role probes exercise one existing UI pair, not a new canonical category/asset or general sample coverage. Thirteen canonical files, five existing variants, prior modes and invalid controls hold. |

Inspection command I ran from repository root: `git diff 6a3696822741388d862243745f653a76eec21d1f -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` — **exit 0**. Other inspection was Python REPL reads/parsing/hashing of existing files, not fresh shell runner commands; I did not rerun the 28 commands or claim their exits as my own executions. Exact runner commands/exits and receipt paths are in `r30-verifier.md`. No source/shared file, commit or push by this adjudicator.

**Limits and rank:** Numeric orientation of this baseline-denominator formula on two specific original waveforms only. Neither symmetric normalization as a norm nor perceptual/auditory similarity, codec behavior, rights, engine behavior, publishing readiness, or promotion follows. `SHONEN.md` has four evidence-checked boxes already; this round does not change them or the rank.
