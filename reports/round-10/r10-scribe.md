# Round 10 scribe — decision table draft

## Declared move and evidence boundary

The declared move is **depth**: for the original analytic `stem_layer` fixture (4.000 s, 48 kHz mono, two 96,000-frame halves), measure the decoded-PCM adjacent sample difference at the internal boundary, between zero-based samples 95,999 and 96,000. Proposed fixture-local decision is pass at `<= 0.03` FS and fail at `> 0.03` FS. This reuses the existing outer endpoint-delta number as a discriminator; it is not independently calibrated. The move is supportable only if a non-author replay shows an isolated new-predicate failure, and confirms unchanged old fixtures/modes and hashes.

## Exact decision table (draft)

| decision | measurement and threshold | action on failure | scope / evidence required |
|---|---|---|---|
| Expected input format and duration | Decoded PCM: 48,000 Hz, mono, 192,000 frames (4.000 s; existing ffprobe duration tolerance ±1 ms) | Report the existing format/duration failure; do not evaluate a purported join-only control as isolated | Existing fixture check; no new format policy |
| Expected signal bounds | Existing `stem_layer` generic bounds: peak <0.95 FS, RMS >0.001 FS, magnitude-weighted spectral centroid within its declared 100–2,000 Hz band | Report each existing failure; no isolation claim if any also fails | Existing checks unchanged |
| Outer endpoint and slope | `abs(samples[0]-samples[-1]) <= 0.03` FS; `abs((samples[-1]-samples[-2])-(samples[1]-samples[0])) <= 0.001` FS/sample | Report existing outer loop-seam failure(s) | Distinct from the internal boundary |
| Two section measurements | Existing 120 Hz component estimate on each 96,000-sample half; both amplitudes >=0.01 FS, each section RMS >=0.001 FS; amplitude contrast `20*log10(second/first) >= 6 dB` | Report existing invalid/contrast failure | Measures section-level 120 Hz amplitude contrast, not join behavior |
| **Internal join sample-gap proxy (proposed)** | `internal_join_adjacent_delta_full_scale = abs(samples[96000]-samples[95999])`; pass if `<= 0.03` FS; fail iff `> 0.03` FS | Fail only this predicate for the isolated negative control; preserve the observed value and all other measurements | One decoded adjacent-sample difference, not a transition-quality or audibility test |
| Isolated negative-control decision | A scratch 4 s/48 kHz mono candidate must satisfy every existing generic, outer-edge, and 120 Hz section predicate, while the new join metric is `>0.03` FS | If any other predicate fails, classify as a failed-fit candidate, not isolated evidence | Candidate stays under `corpus/live/round-10/`, never counted as canonical |

## Before → proposed after, controls, caveats

| item | before | proposed after / evidence needed |
|---|---|---|
| Internal join coverage | The generic measure checks first/last sample delta and outer-edge slope only. `section_contrast()` measures 120 Hz per half. Neither inspects the pair straddling frame 96,000. | Add one explicitly named internal adjacent-sample metric/check at the fixed declared join. Preserve all existing predicates and receipt semantics otherwise. This is a narrow depth improvement if replayed and isolated. |
| Clean `stem_layer` control | The original artifact read locally here has 192,000 frames. Its decoded pair around the join is `[-0.00018310546875, 0.0, 0.000946044921875]` for frames 95,999–96,001, hence adjacent delta `0.00018310546875` FS. | Must independently pass the new threshold and continue passing the old checks. This local inspection is not a non-author replay. |
| Proposed positive control | No admitted receipt yet in this scribe report. | Non-author replay must show the candidate's complete receipt: join delta above threshold and no other failure; plus normal/old controls and canonical hashes unchanged. |
| Existing negative controls | Flat30/flat120, slope, failing, invalid modes test their previously declared predicates. | Replay them with expected behavior unchanged; they do not substitute for isolated join control. A control with extra failures is not sole-failure evidence. |
| Calibration and interpretation | The `.03` endpoint limit is a fixture-local existing constant. | Reusing it for a different sample pair is a design choice, not empirical threshold calibration. No portability to other content, rates, bit depths, playback levels, codecs or engines. |

A one-pair jump is only a discrete PCM amplitude-difference proxy. It does not establish click-free transitions, waveform/slope continuity at the join, smoothness over a window, adaptive engine timing, or audible quality. A value above the bound documents that pair's measured difference; it does not predict a listener response. Passing does not prove perceptual continuity. No perceptual, engine, security, or production conclusion follows.

## Scratch telemetry noticed during report drafting (not an integrated test)

I inspected the existing scratch WAVs in `corpus/live/round-10/` by Python-decoding PCM16 and computing summary values. This is author-side telemetry only; no source edits or measurement CLI replay were performed. `join_candidate.wav` (SHA-256 `c4818b9a2fdf4c6479a945f2f2739c6c0caf1559b1b31d62c4c630af84396e2d`) is 192,000 frames and has join delta `0.040191650390625` FS, outer endpoint delta `0.000946044921875`, outer slope delta `0.000762939453125`, peak `0.05999755859375`, RMS `0.03059310849989651`, centroid `2526.2284064342743` Hz, and 120 Hz half contrast `13.979372283819849` dB. Its centroid is **above** the fixture's 2,000 Hz upper bound, so this candidate is not sole-failure evidence as measured. It must not be described as an isolated successful control.

The six `join_0.0305.wav` through `join_0.035.wav` candidates also exceed the 2,000 Hz centroid bound (observed centroids about 2038.67–2275.64 Hz), and `try_0.0295.wav` through `try_0.0301.wav` have centroids about 1986.02–2017.35 Hz; the latter span both sides of that bound. Their observed join deltas range from `0.029693603515625` to `0.035186767578125` FS. These values show a potential spectral side effect from localized perturbation; do not infer a valid isolated negative control from join delta alone. `join_alt_candidate.wav` is 384,000 frames, has peak `0.99896240234375`, and is not a format/level/contrast-matched isolated control. Hashes and all these values are incidental inventory, not canonical artifacts or verified receipts.

## Commands and exits

Shell command run: `git status --short` (exit 0; initially it showed the parent-edited `LOG.md`, generated `__pycache__`, and round-10 scratch; this report's parent-owned folder was untracked). Shell command run: `git rev-parse --short HEAD && git status --short` (exit 0; HEAD `f32ab7f`; status showed parent-owned `LOG.md`, scratch and reports). No CLI, test, builder, or shell audio command was run. WAV inspection used Python in the REPL; it has no shell exit code. No source, shared record, canonical artifact, or audio scratch was changed by me.
