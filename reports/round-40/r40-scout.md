# Round 40 scout — outer endpoint versus R21 internal gap

## Scope and finding

Read-only source mapping for the declared round-40 calibration probe. I did not generate or audition audio, run the measurement runner, edit fixtures or shared sources, or change thresholds. This report is not evidence that either requested outer-endpoint fixture has passed the complete measurement gates.

The baseline runner source at `9b212354fc1525a52b08209f8c4d26171d9a4c9` has two separate measurement paths:

- In `measure(name, spec, path)`, `sox <path> -t f32 -e floating-point -` decodes the WAV into float32 PCM, then the values are converted to float64. For loop specs (`spec[3]` true), the **outer endpoint** metric is `abs(samples[0] - samples[-1])`; `measure()` adds `loop seam: endpoint jump > .03 full scale` only when this is **strictly greater than** `.03`. Equality would pass this endpoint predicate. Its separate outer side-slope metric compares `(last - penultimate)` against `(second - first)` and fails only when greater than `.001` FS/sample.
- R21's `section_contrast(path)` decodes the same way but requires 192,000 samples and measures the **internal** join at indices 95,999/96,000: `abs(samples[96000] - samples[95999])`. A later runner gate adds `sections: internal join adjacent sample gap > .03 full scale` only when that value is **strictly greater than** `.03`. Its internal side-slope comparison uses samples 95,998–96,001 and the same strict `>.001` polarity. This is not the outer endpoint metric: it compares samples around the 2-second midpoint, not the first and last samples.

## PCM16 bracket arithmetic (expected gate polarity, not a new run)

The requested decoded-count values straddle the existing `.03` bound because `.03 × 32768 = 983.04`:

| Absolute decoded endpoint difference | Full-scale value | Existing outer `> .03` endpoint predicate |
|---:|---:|---|
| 983 counts | `983/32768 = 0.029998779296875` | Does not fail endpoint predicate |
| 984 counts | `984/32768 = 0.030029296875` | Fails endpoint predicate |

No integer PCM16 count is exactly `.03` under this normalization. Existing R21 non-author verifier evidence (not a run by this scout) measured its internal 983 control at `0.029998779296875` FS with internal side-slope `0.0`, and its internal 984 control at `0.030029296875` FS with internal side-slope `0.0`; the former had no failures, the latter solely the internal `> .03` gap failure. These are decoded SoX measurements at the **internal** join, not the outer endpoints. They do not validate outer endpoint fixture synthesis, the full runner path, or outer slope/other gates. Source-level arithmetic alone also does not establish that a new generated WAV decodes to the intended values: the requested gates concern decoded SoX samples. The report's assignment did not authorize a runner replay, so I have no observed decoded outer-endpoint sample measurements or run exits to claim.

## Distinguish setup errors from numeric fit failures

No candidate synthesis/helper or runner command was executed in this scout. Thus there were no setup errors, numeric fit failures, or shell/audio-runner exit codes in this task. For the executor evidence, retain the distinction: a failed helper launch, missing dependency/path, or malformed command is a setup error, not a numeric failed fit; a successfully generated/decoded candidate that misses the requested endpoint count or trips another numeric gate is a numeric fit failure. Neither should be described as a pass. The desired full-run evidence remains 983 mode exit 0 with no failures and 984 mode exit 1 with only the outer endpoint-jump failure, with both candidates' other checks reported.

## Exact shell inspection

- `git show 9b212354fc1525a52b08209f8c4d26171d9a4c9:.shokunin/audio/corpus/fixtures/measure_audio.py | grep -n -E 'def measure|seam_delta|seam_endpoint|seam_slope|internal_join_adjacent_delta|> \.03|samples\[0\]|samples\[-1\]|samples\[96000\]|samples\[95999\]'` — exit **0**. It located the outer endpoint computation and strict gate at lines 74, 84–85; the internal join measurement at lines 114–115; and the internal strict gate at lines 411–412. The inspected source is the declared clean-before commit, not a new test execution.
- `git show 9b212354fc1525a52b08209f8c4d26171d9a4c9:.shokunin/audio/corpus/fixtures/measure_audio.py | sed -n '49,122p'` — exit **0**. It confirmed the complete decode, endpoint, slope, and internal-section sample semantics quoted above.

## Limits

This is only a numeric calibration/source map for the existing local SoX-decoded PCM16 fixture gates. It makes no claim about exact equality at `.03`, audibility, clicks, perceived seamlessness, sound quality, rights, engine behavior, production, publication, or promotion.
