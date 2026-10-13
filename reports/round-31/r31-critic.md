# Round 31 critic — joint-below fit and confounds

## Verdict

The available scratch measurements support a candidate joint-below pair, but do **not** yet establish an integrated runner result. The executor's initial `k=1.0` variant is a useful failed fit: its measured centroid-relative delta is `0.13531931846217793`, above `.10`. The alternate scratch fit at `k=.88` measures a nonzero delta `0.09964036511023155`, below `.10`. For both the base and that candidate, measured duration delta is `0.019978999999999997` s, nonzero and below `.020`. This is evidence for the numeric target in the declared joint-below case, not evidence that the parent runner's `_alt` path rejected it; no round31 integrated mode or receipt is present in the inspected fixture/report state.

## Direct checks and limitations

I inspected `measure_audio.py`: `_alt` compares measured ffprobe durations and computes absolute centroid difference divided by baseline centroid, then passes if duration delta `>= .020` OR centroid-relative delta `>= .10`. For the alternate candidate, that makes both comparisons false. I directly measured scratch files using the project's `measure()` implementation with the separately declared per-variant duration `(6719/48000, *SPECS["ui"][1:])`:

| Scratch source | Frames | ffprobe duration | Centroid | Per-file failures |
|---|---:|---:|---:|---|
| Base | 5760 | 0.120000 s | 966.896659337973 Hz | none |
| Executor `k=1.0` (failed fit) | 6719 | 0.139979 s | 1097.7364563029441 Hz | none with its scratch spec |
| Alternate `k=.88` candidate | 6719 | 0.139979 s | 870.5547231776742 Hz | none with its scratch spec |

The candidate duration delta is `0.019978999999999997` s from reported ffprobe durations (`959/48000` by frame counts). Candidate centroid relative delta is `abs(870.5547231776742 - 966.896659337973) / 966.896659337973 = 0.09964036511023155`. These values are nonzero and strictly below their distinctness cutoffs. Both files pass the existing format, level, and UI spectral checks when the variant's own duration is declared as `6719/48000`.

That separate duration expectation is necessary for this scratch candidate's per-file check, but it changes what is being checked: the longer variant is checked against approximately `.139979` s, not canonical UI `.120` s. It offers no canonical `.12 s` UI duration conformance evidence. The duration difference itself remains measured by the comparator between the two files, not by their separate expected-duration declarations.

The pair changes both sample count and analytic coefficient, so its centroid delta is not causally isolated from duration/truncation and FFT-window effects. It demonstrates only that both measured comparator values can be nonzero and below their cutoffs together. It does not show independent contribution of each signal, threshold equality, or a universal OR law. A same-duration control is needed for a causal centroid-specific claim; this round's declared scope does not require that broader claim.

## Commands and setup/fitting status

Shell command run:

- `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-31/alt/ui_alt.wav` — exit 0; PCM16, mono, 48000 Hz, duration `0.139979` s.

Direct checks used the already available scratch files and imported project measurement helper in the REPL; no shell test or integrated runner command was run. One direct measurement attempt used relative paths and raised `ValueError` because `measure()` returns paths relative to its absolute fixture root; rerunning with absolute scratch paths succeeded. This was a measurement setup mistake, not a WAV fit or runner failure. The executor `k=1.0` fit failed the target centroid bound as reported above; the `.88` alternate fit met the numeric target. No claim is made that the failed fit passed.

No shared source, LOG, SCORECARD, canonical artifact, or other report was changed. No commit or push.

## Limits

No exact cutoff equality, perceptual similarity, rights, engine, publish, promotion, or canonical UI `.12 s` claim for the longer variant. No integrated comparator verdict is claimed.
