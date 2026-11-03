# audio: source candidate, batch 3 — 2026-11-03

**Unassimilated, post-hyaku reading queue.** No installation, execution, training or capability admission. Original summary only; no source code reproduced.

## Rubber Band: stretch onset and end-of-stream accounting

**Question:** Can tempo-adjusted stems retain their intended onset and complete tail without mistaking temporary output starvation for completion?

**Primary source and pin:** Breakfast Quay's official [Rubber Band mirror](https://github.com/breakfastquay/rubberband), commit [e4296ac80b1170018a110bc326fd0d45a0eb27d6](https://github.com/breakfastquay/rubberband/commit/e4296ac80b1170018a110bc326fd0d45a0eb27d6), dated 2025-02-27T11:04:40Z. Opened 2026-11-03; this is a reading revision, not a latest-release claim.

**Source summary:** Offline stretching requires a study pass and handles starting compensation internally. Real-time mode instead exposes input padding and output-delay trimming. The processing API counts multichannel frames, not individual channel samples; available output of zero differs from the terminal value of minus one. These distinctions support an onset/tail contract independent of perceived quality.

**Reading path:** [RubberBandStretcher.h](https://github.com/breakfastquay/rubberband/blob/e4296ac80b1170018a110bc326fd0d45a0eb27d6/rubberband/RubberBandStretcher.h): offline/real-time overview → getPreferredStartPad/getStartDelay → study/process → available/retrieve. Read the [README licensing section](https://github.com/breakfastquay/rubberband/blob/e4296ac80b1170018a110bc326fd0d45a0eb27d6/README.md) before considering reuse: GPL-2.0-or-later, with a separate commercial alternative and dependency-specific terms. No license purchase or input-recording rights clearance is implied.

**Original later exercise, not performed:** Propose an original stereo impulse train with a known final pulse. Predeclare observations for first onset, last pulse, total frames, padding and terminal drain. Compare whole-signal offline processing against correctly handled streaming and deliberately omitted compensation. Vary chunk boundaries so a single lucky buffer size cannot conceal truncation. Keep raw measurements separate from any listening assessment; require a named negative control to fail before treating the check as useful.

**Novelty and limits:** Searches for Rubber Band/breakfastquay across supplied registries and both earlier batches found no matches. This addresses independent tempo/pitch transformation, not Opus framing or libsamplerate rate conversion. Runtime mixer integration remains outside audio's scope; no claim of seamless loops, superior sound, host compatibility or recent upstream maintenance follows. Attribution, redistribution and training permission remain separate questions.
