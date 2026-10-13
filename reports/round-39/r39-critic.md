# R39 critic — denominator, duration, and boundary audit

## Scope and declaration

I read the R39 declaration in `.shokunin/audio/LOG.md`. It asks for one original, deterministic, equal-duration 2.0 s looping ambience pair with lower-centroid A and higher-centroid B, satisfying the strict split `abs(B-A)/A > .10` and `abs(B-A)/B < .10`; forward must pass and reverse must fail solely on distinctness. This is a numeric orientation claim, not a universal or perceptual cutoff claim.

I initially inspected and measured the executor scratch pair during a concurrent overwrite. A subsequent independent measurement pinned to the same baseline and the settled variant SHA reported by the executor confirms the stable candidate **does** satisfy the declared denominator split. The transient failed-fit measurement is preserved below and must not be confused with the stable SHA pair. I did **not** edit source, run the fixture runner in either mode, audition audio, or make any quality/production/rights/engine/publish/promotion claim. No runner outcome is asserted.

## Stable SHA-pinned pair — successful numerical fit only

Files: `.shokunin/audio/corpus/live/round-39/executor/baseline.wav` (A) and `variant.wav` (B). `sha256sum` exit **0**:

```text
d516b687e91b983e60a7353cd19bb62f544be99ea9ec31a8bd7b5b2b4457d062  baseline.wav
4f9c5365744b22643ca9fb48c6656529550f3457243871cc9a4c1503d035baec  variant.wav
```

Independent project-helper measurement, exit **0**, on this SHA-pinned pair:

| Measure | A baseline | B variant |
|---|---:|---:|
| duration (s) | 2.0 | 2.0 |
| format | 48 kHz mono PCM16 | 48 kHz mono PCM16 |
| spectral centroid (Hz) | 70.7623033885285 | 78.18153634552728 |
| peak full scale | 0.218170166015625 | 0.2581787109375 |
| RMS (dBFS) | -18.633069022379566 | -17.61980253353166 |
| endpoint delta | 0.0013427734375 | 0.001953125 |
| seam slope mismatch | 0.000030517578125 | 0.000030517578125 |
| ordinary + seam failures | `[]` | `[]` |

Actual strict ratios from the unrounded helper floats:

- Forward, A denominator: `abs(B-A)/A = 0.10484725060831668` (**> .10**).
- Reverse, B denominator: `abs(B-A)/B = 0.09489750782344704` (**< .10**).

Thus this stable pair satisfies the **numerical strict denominator split**, with both durations exactly 2.0 s (duration delta exactly `0.0`). This is only a fitted pair, not proof that either runner mode produces the declared pass/failure: I did not run the fixture runner, so there are no runner exits or receipts to report. The ordinary level check excludes only clipping/near-silence under its thresholds. The pair is not level-matched (RMS differs by about 1.01 dB); the effect of that difference is not tested, and I make no causal claim about it.

### Transient measurement retained as a failed fit

During concurrent scratch overwrite, I measured the same baseline SHA with transient variant bytes having centroid `104.41599288709146` Hz, peak `0.6981201171875`, RMS `-7.891728666835612` dBFS, endpoint delta `0.008880615234375`, and seam slope mismatch `0.0`. That transient measurement gave forward ratio `0.475587818471419` and reverse ratio `0.3223039744012571`; both are above .10, so it was a **failed numerical fit**. Those metrics are not attributable to settled variant SHA `4f9c...` and do not describe the stable pair. It likewise has no runner outcome. The transient record is preserved to explain my original report rather than silently overwritten.

Equal measured duration (difference exactly `0.0` s) rules out the duration arm `duration_delta >= .020` as an explanation **if** these files are later used in the generic `_alt` comparison. It does not establish that forward passes or reverse fails: the runner modes have not been executed, and the current ratios predict neither strict split. Clean ordinary/seam failure lists establish only that the specified checks passed, not that all other waveform properties are controlled.

## Commands and setup versus fit

1. `git status --short && sed -n "/Round 39 declared calibration claim/,$p" .shokunin/audio/LOG.md | head -n 20 && grep -R "centroid_relative\|duration_delta\|_alt\|loop" -n .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**. The `sed` subcommand emitted `sed: -e expression #1, char 38: unexpected ','` because the address expression was malformed; grep and status still ran. This is a **setup/inspection command error**, not a failed audio fit.
2. `python3 .shokunin/audio/corpus/live/round-39/executor/measure_pair.py` — exit **1**, `FileNotFoundError` attempting `.shokunin/audio/fixtures/measure_audio.py`; the helper script's relative-root calculation points at a nonexistent path. **Setup failure**, not a measurement.
3. `python3 -c 'import importlib.util,pathlib,json; p=pathlib.Path(".shokunin/audio/corpus/live/round-39/executor"); s=importlib.util.spec_from_file_location("measure_audio", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=(2.0,5,200,True); a=m.measure("A",spec,p/"baseline.wav"); b=m.measure("B",spec,p/"variant.wav"); d=abs(b["spectral_centroid_hz"]-a["spectral_centroid_hz"]); print(json.dumps({"A":a,"B":b,"forward_ratio":d/a["spectral_centroid_hz"],"reverse_ratio":d/b["spectral_centroid_hz"]},indent=2))'` — exit **1**, helper raised `ValueError` because relative scratch paths were not relative to the fixture corpus root. **Setup/path failure**, not a fit result.
4. Re-run of that exact Python expression with `p=pathlib.Path(".shokunin/audio/corpus/live/round-39/executor").resolve()` — exit **0**, produced the measurements and ratios above. This successful helper measurement is the **failed numeric fit**.
5. `sha256sum .shokunin/audio/corpus/live/round-39/executor/baseline.wav .shokunin/audio/corpus/live/round-39/executor/variant.wav` — exit **0**, hashes above.

I did not run the fixture runner or claim runner exit codes/receipts. No candidate here establishes exact-boundary behavior: neither ratio is close to .10, and no exact `.10` candidate or boundary sweep was measured. Strict `>` and `<` must be assessed on full-precision values; rounded displays, even at `.10`, cannot prove which side a value occupies. The project predicate's `>= .10` is not itself evidence of strict-boundary behavior.

## Conclusion

The stable SHA-pinned pair meets the requested numerical denominator split and equal-duration/ordinary/loop checks, while the transient overwritten variant was a failed fit. The stable pair is not perfectly level-matched, and no forward/reverse runner receipts were examined or claimed. No exact-boundary, general threshold, or perceptual claim follows from this review.
