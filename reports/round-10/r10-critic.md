# Round 10 critic — internal PCM join gap claim

## Verdict

A decoded-PCM adjacent-sample jump at frame 96,000 is a concrete, reproducible measurement that fills a blind spot in the current checks: the outer loop endpoint/slope predicates inspect only the file edges, and the 120 Hz half-section contrast says nothing about the join. It can support a narrow depth claim if added as a named internal-join sample-gap proxy and if a non-author replay demonstrates an otherwise-clean candidate whose only reported failure is that predicate. It does not measure transition smoothness or establish click-free / audible behavior. Reusing `.03 FS` as a fixture-local bound is not empirical threshold calibration.

## Metric interpretation and threshold portability

Define the metric unambiguously on the decoded mono samples: `abs(samples[96000] - samples[95999])`, with zero-based indexing, so it is the difference across the boundary between the final sample of the first 96,000-frame half and first sample of the second. State that it is a one-edge amplitude discontinuity proxy in full-scale units. It is not loop seam delta, slope mismatch, section contrast, derivative continuity in a perceptual sense, or a measure averaged over a transition window. Receipt naming should say `internal_join_adjacent_delta_full_scale` (or equally explicit), not reuse `seam_*`.

The proposed `<= .03` value borrows the outer endpoint limit for a local deterministic discriminator. The two bounds concern different sample pairs and no evidence here calibrates either against audibility. It must be labeled fixture-local, not generally portable across sample rates, bit depths, playback levels, content, codecs, or engines. At a fixed PCM format, the numeric value is still an author-chosen FS bound; passing it cannot imply inaudibility. Keep exact comparison polarity/boundary (`> .03` fails, equality passes) in the receipt/docs and test quantized decoded PCM, not merely a floating-point synthesis buffer.

## Sole-failure isolation and candidate fit

A plausible isolated candidate is the existing 4-second 120 Hz layer with one localized perturbation at/around the boundary, while preserving both 96,000-frame halves and their component contrast, the generic format/duration/level/centroid checks, and the outer endpoint and slope checks. A one-sample impulse/perturbation can create a large join edge while leaving outer samples untouched, but its two neighboring edges and its spectral contribution must be measured; do not assert fit from construction. The positive layer should retain >=6 dB contrast at 120 Hz, valid section amplitudes/RMS, and all generic checks. An isolated failure is evidenced only by the complete receipt showing exactly the new join predicate fails and no other measurement failure, plus an independent replay and unchanged old controls/hashes. A candidate that also violates spectrum, contrast, duration, level, or outer seam is not an isolated control. If it does not fit, retain exact failed-fit telemetry and narrow or abandon the isolation claim rather than weaken unrelated gates.

The flat120 control is designed to fail section contrast, not to test the join gate; the flat30, slope, failing, invalid and canonical fixture checks likewise cannot substitute for this new control. Exercise old modes separately and show their expected behavior unchanged. Ensure the new scratch file does not enter canonical counts or hashes.

## Transition smoothness / scope

A single adjacent pair can expose a sample jump, but cannot tell whether a transition is musically or perceptually smooth. It misses slope changes when adjacent values match, behavior across more than one sample, envelope/crossfade duration, phase coherence, engine block timing, synchronization, playback conversion, and listener/context effects. Even a zero measured jump does not establish a smooth transition. A measured >.03 jump is only evidence of the declared discrete PCM difference, not a predicted audible click. Do not call this seam quality, click detection, audible continuity, adaptive-engine support, or production readiness.

## Inspection record

Read the round-10 declaration in `.shokunin/audio/LOG.md`, `SCORECARD.md`, `corpus/fixtures/measure_audio.py`, and `corpus/fixtures/build_artifacts.py`, plus prior round-8/9 critic reports. No shell command was run; there are no shell exit codes. This is source/claim review only: I did not synthesize or inspect a candidate WAV, run the measurement CLI, or change source, shared records, canonical assets, or scratch audio. No scratch file was necessary for this critique.
