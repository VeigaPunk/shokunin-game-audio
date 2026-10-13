# Round 21 alternate grid/isolation challenge

## Scope and numeric method

I independently constructed paired 200 Hz scratch WAVs under `.shokunin/audio/corpus/live/round-21/alt/`. These are not canonical assets and were not passed through an integrated round-21 CLI mode. I reused the current numeric measurement functions (`measure()` and `section_contrast()`) for proxies only; no listening or perception claim is made.

The candidate starts with the existing canonical `stem_layer_third.wav` and adds the original 220/330 Hz bed used in the runner's round-20 join probe. At frames 95998–96001 the resulting PCM16 values are `[-290,-145,0,175]`; I set frame 96000 to 838 (pass candidate) or 839 (fail candidate), then set frame 96001 to preserve the left adjacent difference. Thus the tested decoded PCM16 join differences are exactly 983 or 984 counts. Under the runner's SoX f32 decode these measure `.029998779296875` and `.030029296875` FS. The existing strict gate is `> .03` FS, so the first is below and the second above. This probes the claimed arithmetic grid for this constructed waveform and decode path; it does not test a generalized tolerance.

## Exact commands and outcomes

Commands were run from repository root unless noted.

1. `python3 .shokhun/audio/corpus/live/round-21/alt/make_alt.py` — exit **2** (path typo; no file generated).
2. `python3 .shokunin/audio/corpus/live/round-21/alt/make_alt.py` — exit **0** on an initial, incorrect no-bed draft. Its 838/839 candidates measured 851/852 counts because the canonical layer alone has a different left sample. This is failed-fit telemetry, not evidence for the boundary.
3. `python3 .shokhun/audio/corpus/live/round-21/alt/make_alt.py` — exit **2** (same path typo after revising draft).
4. `python3 .shokunin/audio/corpus/live/round-21/alt/make_alt.py` — exit **0** on the final bedded construction. It reports:
   - `alt_pass.wav`, SHA-256 `36ccb3eb8d4ab030b448441e9b1f34adc7469bf91f73bb107e8bea745468f23f`, four counts `[-290,-145,838,983]`, join 983 counts.
   - `alt_fail.wav`, SHA-256 `3792be747db096b68a47a12f9e64e2f5cb866f42c0ff9c46e025fc9efa5ff6d5`, four counts `[-290,-145,839,984]`, join 984 counts.
5. First `python3 .shokhun/audio/corpus/live/round-21/alt/analyze_alt.py` — exit **1**, because the relative scratch path was not beneath the measurement module's resolved root. No measurements from this failed invocation are counted.
6. Corrected `python3 .shokhun/audio/corpus/live/round-21/alt/analyze_alt.py` — exit **0**. It runs the existing measurement functions on both files. Both have no generic failures, valid 200 Hz contrast (`10.4573358` dB), and side-slope mismatch `0.0`. The pass candidate's internal gap is `.029998779296875` FS and would have no section-gate failure; the fail candidate's gap is `.030029296875` FS and would fail only `gap` among the manually evaluated section gates. The script intentionally omits integrated runner execution; its result is a numeric-function challenge only.

## Challenge and limits

This alternate construction independently supports the declared 983/984-count strict-polarity bracket while matching the existing contrast/generic checks. It also highlights that the bracket depends on the left sample: my first no-bed candidates at the same target values landed at 851/852 counts, so target PCM values alone do not define the boundary independent of waveform context. The bedded construction is itself a deliberately composed scratch signal, not a waveform-identical edit of the canonical layer.

I did not invoke a CLI probe route, write or change shared builder/measurement code, alter canonical artifacts, or establish full runner integration. In particular, these measurements do not independently prove the parent's route wiring, preservation of historical modes/hashes, or non-author end-to-end admission. No claim about audibility, a perceptual tolerance, production audio, or threshold retuning.
