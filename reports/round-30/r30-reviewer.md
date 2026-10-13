# Round 30 reviewer — two-mode orientation check

## Minimal proposal

Add exactly two opt-in runner modes, for example `--probe-ui-centroid-baseline-forward` and `--probe-ui-centroid-baseline-reverse`. Each mode generates a 5760-frame, 48 kHz mono PCM16 pair in its round-30 scratch directory from the existing UI chirp. Reuse the existing `SPECS["ui"]` for both measurements and the unchanged `_alt` comparator. Keep the `.020 OR .10` thresholds, absolute value, and baseline denominator unchanged; do not add a comparator or normalization.

| Mode | baseline bytes | alternate bytes | Expected existing distinctness result |
|---|---|---|---|
| forward | `k=1.0` | `k=.95` | relative delta `0.099019015...`; fails distinctness only |
| reverse | `k=.95` | `k=1.0` | relative delta `0.109901337...`; passes |

The relative values use the round-29 measured centroids (966.8966593379727 Hz at `k=1.0`, 871.155504521436 Hz at `k=.95`) and the existing formula `abs(variant - baseline) / baseline`. These are numeric baseline-denominator orientation outcomes only, not a claim that the comparator should be symmetric. Require byte identity across swapped roles (`SHA256(forward baseline) == SHA256(reverse alternate)` and `SHA256(forward alternate) == SHA256(reverse baseline)`) and duration delta zero. Both files in each mode must independently pass the same ordinary UI format, duration, level and centroid-band checks. Do not change canonical WAVs.

Keep wiring narrow: two argparse flags, two builder dispatches/source pairs, and receipt mode/suffix names. Generate the same source expression and PCM16 conversion for each `k` in both roles so swapped files are byte-identical. No generalized sweep or comparator changes.

## Commands and evidence status

I did not run commands, generate scratch audio, or make any project changes. Once integrated, run from repository root:

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-baseline-forward
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-baseline-reverse
```

No actual exit codes or receipts are available from this review. Expected exits if integrated files reproduce the cited measured centroids and pass ordinary checks: forward `1` (sole distinctness failure), reverse `0`. An unexpected ordinary check failure or exit `2` would invalidate the expected result. Do not report expected exits as observed evidence. Failed candidate fits and setup/tool errors must be logged separately from valid runner outcomes and excluded from evidence; this reviewer pass had no fit/setup attempts or failures.

No perceptual-similarity or audio-quality claim, symmetry normative claim, exact-cutoff claim, or rights, engine, publishing, production, or promotion claim is made. This is only a minimal review proposal, not validation or admission.
