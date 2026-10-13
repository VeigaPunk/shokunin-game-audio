# Round 26 critic — exact-duplicate negative

## Falsification target

The declared result is that a matched `ui_clone` / `ui_clone_alt` exact-copy pair passes each ordinary measurement and fails *only* the existing distinctness OR rule at duration delta 0 and relative centroid delta 0. That is a plausible narrow negative, but the declaration alone is not evidence that it was achieved: I found no round-26 scratch inputs or receipts at review time. No shell commands were run; therefore there are no command exits to report.

## Critical checks / rejection conditions

- Pair identity must be established at the bytes or decoded-sample level, not inferred from matching labels or similar measurements. For a claimed exact waveform copy, compare SHA-256 of the two WAVs (or demonstrate identical decoded mono samples); a mismatch may still be an identical decoded signal if only container metadata differs, but that would not be a byte-identical duplicate.
- Both records must have empty ordinary `failures` before distinctness is appended: 48 kHz mono PCM16, duration within the UI spec's ±1 ms, non-clipping/non-silent levels, and centroid in 250–4000 Hz. A duration/spec mismatch, format error, or other failure defeats “solely distinctness.”
- The receipt must show `duration_delta_s == 0` and `centroid_relative_delta == 0` (or justify exact numeric representation), `distinctness["ui_clone_alt"].passed == false`, and the variant's only failure exactly `distinctness: duration < .020 s and centroid delta < 10%`. Verify the reported baseline is `ui_clone`; check there is no accidental pairing with a canonical `ui` or stale/missing measurement.
- The intended runner outcome is exit 1 for this deliberate negative, with no unexpected additional failures. Exit 2 or an ordinary measurement failure falsifies the attribution. Confirm the thirteen canonical WAV hashes and their normal results separately; this scratch negative is not canonical content.

## Duplicate versus branch boundary

An exact duplicate at (0 s, 0%) is a clear *joint* negative: both alternatives in `duration_delta >= .020 OR centroid_relative_delta >= .10` are false, well away from either boundary. It distinguishes the exact-duplicate case from the five existing passing variants, but does **not** test either cutoff, establish behavior at `.020 s` or `.10`, or identify which OR arm is responsible for a near-boundary result. Do not call it a boundary test or infer a general deduplication/perceptual property. Separate one-coordinate controls would be needed to probe branch/boundary behavior; adding them is outside this round's one-move claim.

## Verdict

No independent execution or receipt was available to validate the result at this review point. Treat the declared outcome as pending until the checks above are evidenced. If satisfied, the supportable conclusion is limited to a matched exact duplicate failing the current distinctness rule while ordinary UI measurements pass; it is not evidence about auditory similarity, sound-engine behavior, rights, publication, or promotion.
