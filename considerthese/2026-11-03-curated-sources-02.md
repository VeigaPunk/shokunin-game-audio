# audio: curated source to consider, batch 2 — 2026-11-03

**Status: unassimilated candidate for post-hyaku review.** Reading queue only, not training, admission or capability evidence. No candidate code was installed, run or integrated. This note contains original summaries; no third-party code or prose is reproduced.

## libsamplerate: streaming conversion state and output headroom

- **Primary source:** [libsamplerate: streaming conversion state and output headroom](https://github.com/libsndfile/libsamplerate).
- **Verified reading anchor:** [c96f5e3de9c4488f4e6c97f59f5245f22fda22f7](https://github.com/libsndfile/libsamplerate/blob/c96f5e3de9c4488f4e6c97f59f5245f22fda22f7/docs/api_full.md). [Release 0.2.2](https://github.com/libsndfile/libsamplerate/releases/tag/0.2.2) published 2021-09-05T11:50:41Z; tag resolved through the GitHub commits API, not inferred from neighboring CI activity. Opened 2026-11-03.
- **Source summary:** The simple API expects a complete signal, not successive chunks. The full API retains conversion state and reports consumed/generated frames; resetting starts an unrelated signal. FAQ Q1 and Q6 distinguish output overshoot from converter delay. This makes resampling a separately inspectable cause of damaged seams, shifted onsets or clipped assets rather than attributing every difference to codecs.
- **Read first:** docs/api_simple.md, opening warning; docs/api_full.md, Process and Reset; docs/faq.md, Q1 and Q4–Q6.
- **Why useful here:** Adds stateful sample-rate conversion to existing loudness, decoder and codec work. First-batch Opus timing does not cover resampler-state misuse.
- **License:** [BSD-2-Clause](https://github.com/libsndfile/libsamplerate/blob/c96f5e3de9c4488f4e6c97f59f5245f22fda22f7/COPYING). Retain applicable copyright/license notices on later reuse; inspect dependencies and individual asset terms separately. Attribution, redistribution and AI-training permission remain separate; no training or input-asset rights determination is made.
- **Hard limits:** A library comparison cannot establish perceived quality, engine behavior or rights to input recordings. The 2021 release is a deliberate stable reading anchor, not evidence of recent maintenance. Keep conversion measurements separate from loudness normalization and runtime audio routing.

## Original lane-specific evaluation proposal, not performed

**Future question:** Can a future audio-only fixture distinguish reset-induced block seams, startup delay and conversion overshoot?

After hyaku and separate authorization, design original stereo impulses plus a periodic tone at 44.1 kHz. Specify a 48 kHz whole-signal reference, preserved-state chunked case, and deliberate per-block-reset control. Predeclare frame-accounting, onset-alignment, boundary-discontinuity and float-peak observations. Vary chunk sizes, include final draining, and keep float results before any PCM conversion. A failure should name the violated property, never subjective sound quality.

## Duplicate and selection review

New libsndfile/libsamplerate repository family; libsndfile decoder mentions are acknowledged but are a different project. No libsamplerate name or URL occurs in any supplied context. Distinct from first-batch xiph/opus and RFC 7845.

Reviewed existing-urls.json and all four assigned lane contexts, including their published first-batch notes; candidate names/paths were also searched across all supplied lane contexts. This is source-inventory dedup, not a claim that every private corpus file was read. One focused candidate was retained; no broader framework adoption is implied. Re-open the pinned source and define an authorized, lane-local admission gate before future execution.

