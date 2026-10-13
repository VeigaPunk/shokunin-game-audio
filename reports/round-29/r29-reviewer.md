# Round 29 reviewer — minimal opt-in runner proposal

## Minimal shape

Keep the established pair of opt-in runner modes, `--probe-ui-centroid-below` and `--probe-ui-centroid-above`, and add only their matching source-generated scratch pair. The UI baseline is the existing 5760-sample analytic chirp (`k=1.0`); use a lower frequency multiplier for each alternate (`k=0.85` for the below-cutoff case, `k=0.80` for the above-cutoff case). Both pairs stay 5760 samples at 48 kHz (duration delta 0), and must be measured against the unchanged `SPECS["ui"]` for both files. Reuse the existing `_alt` distinctness rule and its `abs(variant_centroid - base_centroid) / base_centroid >= .10` test; do not add a signed rule or adjust thresholds. No shared/canonical artifact edits are needed.

The key polarity check is that both alternates are below the baseline centroid, yet the .80 pair clears existing distinctness. A signed `(variant-base)/base` comparison would misclassify that passing pair. Keep the change to the two argparse flags, builder dispatch/source pair, and receipt mode/path suffix selection; avoid generalized sweep/config machinery.

## Candidate fit and unsuccessful candidates

The source waveform is `.38*sin(2*pi*(700*k*t + 800*k*t*t))*exp(-30*t)`, `t = arange(5760)/48000`, rounded/clipped to PCM16 by the existing builder. A local numerical PCM16/FFT fit (not a project runner execution) estimated baseline centroid `966.90 Hz`; `k=.85` estimated `911.28 Hz`, relative absolute delta `.0575`; `k=.80` estimated `845.46 Hz`, delta `.1256`. Both estimates are below baseline and bracket `.10`. Estimated RMS is about `.100` and peak `.376`, within ordinary level limits; both centroids are inside the UI 250–4000 Hz band. These are candidate estimates only; author and independent project runner receipts must establish ffprobe/SoX measurements and all unchanged ordinary checks. Do not infer exact cutoff equality, monotonicity, smoothness, or perception.

Exploratory lower-k points `.90` and `.75` were not selected: measured estimates `.1047` and `.2555` respectively, so they do not furnish the needed below-cutoff and nearby opposite-side pair. These are failed candidate fits for the requested bracket, not runner/setup failures. The `.50`–`.70` exploratory points were also poor candidates (relative deltas about `.26`–`.48); the centroid response is not assumed monotonic. The prior R28 `k=1.11`/`1.10` points are higher-centroid cases and do not cover this negative direction.

## Commands / execution status

I did not execute project commands or alter shared files. After the modes are integrated, the exact invocations to run from the repository root are:

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above
```

No exit codes or receipts are available from this reviewer pass; do not present these commands as having run. Candidate scratch fit was numerical only, with no ffprobe/SoX or runner setup. Thus there were no setup failures to report separately. Record any future setup/tool errors (including their command and exit code) separately from a candidate whose ordinary check or distinctness assertion fails. Expected semantic outcome, if the integrated pair reproduces the fit: below mode exits 1 for the sole existing distinctness failure; above mode exits 0. An unexpected ordinary failure or exit 2 would block the polarity claim.

This is a review proposal, not a validation/admission verdict. No exact `.10` equality, smoothness, perceptual, rights, engine, publishing, production, or promotion claim is made.
