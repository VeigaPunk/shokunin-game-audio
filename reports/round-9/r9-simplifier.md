# Round 9 simplifier — one authoritative section-measurement schema

## Recommendation

Keep one executable section-measurement implementation and make its returned per-section `component_hz` the sole frequency value in each new receipt. Remove the unused top-level `thresholds.section_component_hz`; do not replace it with another global frequency table or duplicate the per-section value elsewhere. The call that selects 30 Hz for the existing stem/flat30 and 120 Hz for the layer/flat120 remains the executable input to `section_contrast`, and that function reports the actual argument it measured.

Rename `section_energy_delta_db` to `component_amplitude_contrast_db` wherever `section_contrast` returns it, including the invalid-count result (`None`). Keep the existing signed formula `20*log10(A2/A1)`, thresholds, and pass/fail logic exactly as they are. This is a receipt-schema correction only. Do not emit both names as aliases: that would preserve the ambiguity and create two machine-readable sources for the same value.

Document the old-to-new mapping for newly generated receipts and state that already-written JSON is historical and remains unchanged. Consumers that need this value should read only `sections[name].component_amplitude_contrast_db` alongside that same section's `component_hz`; no compatibility shim or historical-receipt rewrite is warranted. Source/knowledge prose can mention the former field name solely to explain migration, not as an alternative current key.

## Why this is minimal

The frequency is already supplied to the shared `section_contrast` function and returned per section. The top-level `thresholds.section_component_hz: 30` is not read to choose the measured frequency and is misleading for 120 Hz sections, so deleting it removes redundant, stale metadata rather than adding synchronization logic. The old result key is inaccurate about integrated section energy; the replacement names the measured quantity without changing its number or meaning. No numeric limit, fixture, or other measurement needs to change for this cleanup.

## Scope and limits

This recommendation addresses source/receipt semantics and schema migration only. It offers no perceptual, engine, security, production, or audio-quality conclusion. Existing section checks remain fixture-local numerical checks.

## Commands / exits

No shell commands were run; therefore there are no shell exit codes to report. I inspected the round-9 claim in `.shokunin/audio/LOG.md`, `corpus/fixtures/measure_audio.py`, and the round-8 simplifier report. No source, LOG, SCORECARD, canonical asset, receipt, or commit was edited.
