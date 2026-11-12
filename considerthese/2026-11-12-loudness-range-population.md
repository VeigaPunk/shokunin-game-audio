# Audio: define the loudness-range population

[EBU Tech 3342](https://tech.ebu.ch/docs/tech/tech3342.pdf), November 2023, sections 2–4, specifies Loudness Range rather than crest factor. Its history records first publication in 2010 and a 2016 calculation-frequency revision; this is not a new 2023 estimator.

Three-second loudness windows are sampled at least ten times per second. Absolute and relative gates select the population before the 10th-to-95th percentile difference. The relative gate is twenty LU below absolute-gated loudness, not the integrated-loudness gate. Very short or isolated utterance programmes can mislead. Minimum compliance tests do not prove complete accuracy.

**Proposed practice, unperformed:** In an isolated audio workspace, make one original ninety-second signal with three thirty-second level regions. Create variants with a brief impulse and added silence. Use one pinned meter, resetting between runs. Preserve each waveform hash, settings, window trace, included/excluded window counts, LRA, integrated loudness and peak separately. Before running, predict which variants can change each quantity. Compare predictions with observations and explain discrepancies without claiming perceptual quality or compliance. Cap the exercise at three variants and one hour; no engine integration.

The task extends meter-operation readings with population selection. No audio, measurement, training or assimilation was performed. Original commentary and proposed fixture; source and test-asset reuse clearance is not asserted.

Destination: VeigaPunk/shokunin-game-audio, main, considerthese/2026-11-12-loudness-range-population.md.
