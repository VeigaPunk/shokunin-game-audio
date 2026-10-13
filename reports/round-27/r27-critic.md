# Round 27 critic — duration-branch calibration

## Falsification target

The claim is not established by the declared frame counts. It requires an integrated pair whose only distinctness failure/pass polarity comes from the duration arm, while the centroid arm is demonstrably below `.10`; both audio measurements must otherwise pass. In particular, a failed ordinary duration gate is not a distinctness negative.

## Findings / ways this can fail

- **Spec workaround risks tautology.** The current `measure(name, spec, path)` duration gate is `abs(ffprobe_duration - spec[0]) > .001`. Giving each scratch file a spec whose expected duration is that file’s own observed/selected duration makes this check vacuous for duration, not “otherwise identical UI spec” validation. It can be acceptable only as an explicitly narrow way to reach the distinctness comparator, with format, level and centroid gates retained and no claim that the longer file conforms to canonical `.12 s` UI duration. A shared nominal `.12 s` spec would reject `.139979…` and `.140` before the intended comparison. Report any such additional failure rather than attributing it to distinctness.
- **Comparator operates on ffprobe decimal durations, not frame counts.** Distinctness is `abs(variant["duration_s"] - base["duration_s"]) >= .020`; JSON duration is parsed from ffprobe’s `format.duration` string into binary float. WAV frame counts provide an exact rational duration, but the CLI comparison is on rounded decimal output and a float subtraction. Thus “960 frames equals the threshold” does not alone prove the actual stored comparator sees `>= .020`. Conversely, a rounded just-below value can obscure how close the exact frame ratio is. The proposed 6719-frame variant is 959/48000 = 0.019979166666… s beyond 5760 frames; 6720 is 960/48000 = .020 exactly. Capture raw ffprobe strings plus receipt values, and classify from the actual predicate, not nominal math. If the supposedly failing case passes or equality falls below threshold, record a failed fit; do not tune the `.020` constant.
- **Branch isolation is conjunctive evidence.** Show `centroid_relative_delta < .10` for both rows (prefer the actual computed value), not just “centroids look similar.” Verify the baseline mapping is `ui_clone` and variant is `ui_clone_alt`; an incorrect name/pair or stale path can change what gets compared. For the negative, the only added failure should be the existing distinctness message; for the positive, there should be no distinctness failure. Duration deltas should be computed from the receipt’s two measured durations and match the comparator.
- **“Same UI spec” needs careful wording.** Existing canonical `SPECS["ui"]` is `.12 s`; the proposed longer scratch durations are outside its ±1 ms duration tolerance. If per-file duration specs are changed to `.139979…`/`.140`, that is a deliberate gate bypass for the duration dimension, not evidence both satisfy the canonical UI duration criterion. If instead lengthening or padding changes signal statistics, report measured RMS/peak/centroid and any centroid shift; a fit that fails the <10% centroid condition does not isolate duration.
- **No generic conclusion.** Two samples at 959/960 excess frames can at most exercise these neighboring generated cases and this implementation/toolchain’s duration representation. They do not establish a universal boundary independent of ffprobe/version, float serialization, or WAV rate; do not infer perceptual distinction.

## Inspection / command record

Static inspection of `.shokunin/audio/corpus/fixtures/measure_audio.py` found the comparator at lines 266–272 and the duration check in `measure()`; current `--probe-ui-clone` hardcodes round-26 paths and measures each with `SPECS["ui"]`. No audio-generation, ffprobe, runner, or shell validation was run in this critic task. The only shell invocation was:

```sh
python3 -c 'a=0.139979; b=0.140000; base=0.120000; print(repr(a-base), repr(b-base), (a-base)>=.020, (b-base)>=.020)'
```

Exit 0; output `0.019978999999999997 0.020000000000000018 False True`. This is only binary-float arithmetic on decimal literals, **not** ffprobe output, WAV measurement, or fit evidence. No failed audio fit was run; fit status remains unverified.

## Verdict

This review identifies a material risk in the proposed calibration: per-file duration specs can make the ordinary duration check non-informative, while the comparator’s actual inputs are ffprobe decimal durations rather than exact frame counts. Require raw measured durations, explicit per-file-spec disclosure, empty ordinary failure lists (except the intentionally appended distinctness negative), and verified `<.10` centroid deltas before accepting duration-only attribution. Until then, the declared claim is pending. No perceptual, rights, engine, publishing, or promotion conclusion is made.
