# Round 7 critic — odd-section exception attribution and scope

## Evidence boundary

I read the round-7 declaration in `.shokunin/audio/LOG.md`, the current `.shokunin/audio/corpus/fixtures/measure_audio.py`, and the old file at `3b02c31` via `git show`. I did not run the audio toolchain, inspect the scratch by decoding it, or make any perceptual, security, or production claim. Exact shell command run: `git show 3b02c31:.shokunin/audio/corpus/fixtures/measure_audio.py` — exit 0. The current-source snapshot I read listed only `short_sections`, `corrupt`, and `wrong_format` in `invalid_probes()`; it did not yet list `odd_sections`. This is a time-bounded observation, not a claim about later parent integration.

## Causal attribution

The old function source has a concrete candidate cause: it invokes `np.split(samples, 2)` before checking `len(samples) == 192000`. An odd-length decoded array is not evenly divisible into two sections, so NumPy's split can raise `ValueError` before the old function returns its ordinary invalid result. The post-round-6 function instead checks the exact expected count first and returns `failure_kind: "section count"`. This source-level ordering difference supports a narrow causal explanation **if** the 101-frame WAV is shown to decode through SoX to exactly 101 mono float samples and the baseline run actually reports the split exception.

Do not attribute the exception merely to “short input” or to `section_contrast()` generally. The round-6 `short_sections` file is even length; the LOG itself corrects that it would reach the old count predicate. The discriminating condition here is odd decoded sample count (and successful decode), not a universal short-file defect. If the baseline produces a SoX/command error or a different exception first, the split-cause claim is not established.

Also distinguish a direct function regression from an observed old CLI failure: in the old source, the general measurement flow only invokes `section_contrast()` for canonical `stem_sections` and the flat probe. It did not expose an arbitrary-input invalid-probe CLI. Thus, unless another old call path is demonstrated, the comparison establishes behavior of this function on a deliberately supplied input, not that an existing user-facing command previously crashed on this scratch file.

## Scope of any new category

`odd_sections` is an additional named fixture/control within the already existing `section count` failure class. It is not a new audio category, WAV format class, or general malformed-input handling guarantee. Keep the claim bounded to the exact valid-header, PCM16, mono, 48 kHz, 101-frame scratch and the observed decode/result. The test can support a narrow depth move: the new opt-in invalid-probe path reports this named wrong-section-count case instead of allowing the prior split exception, provided the after receipt includes it and has no traceback. It does not show robustness for arbitrary odd lengths, tiny arrays, multichannel inputs, truncated/corrupt WAVs beyond the separately named controls, or unhandled exceptions elsewhere.

Evidence needed for a clean causal statement: scratch recipe/hash and successful decode/sample count; independent baseline command and exact exception; after-state source showing the new probe is included and count check precedes split; after receipt naming the probe, observed `section count`, actual/expected counts, and process exit. Keep old exception and new expected rejection distinct in wording. No thresholds or category taxonomy need change.
