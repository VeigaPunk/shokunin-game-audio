# R41 simplifier review

## Scope / declaration

Read `.shokunin/audio/LOG.md`, section “Round 41 declared calibration claim and wave spec.” It calls for one outer-neighboring-sample slope calibration: original 2.0 s / 96,000-frame / 48 kHz mono PCM16 fixtures, decoded mismatch 32/32768 (pass) and 33/32768 (fail), both with endpoint delta <= .03 and ordinary fixture checks passing. The criterion remains strict `> .001`; this pair does not test equality at .001. This is distinct from R40 outer endpoint and R21 internal section-join checks.

## Smallest source change recommendation

Do not refactor the runner or alter `measure()`, `SPECS`, thresholds, canonical fixtures, or existing modes. Add just two opt-in runner flags (`--probe-outer-slope-32` and `--probe-outer-slope-33`) and route both through one focused fixture-builder function that writes the two pinned, distinct WAVs under the declared round-41 scratch directory. Add their flags to the existing mutually-exclusive-mode check and builder dispatch; add one measurement dispatch selecting the matching named scratch WAV, and report labels/suffixes for those two modes. Keep ordinary fixture measuring and the existing slope comparator untouched. This confines the diff to the two mode declarations/dispatches and one pair-specific source generator; no general helper or threshold abstraction is justified.

The generator should derive the end-neighbor differences from integer PCM values so decoded output—not pre-quantized float intent—has the declared 32/33-count mismatch. It should keep endpoint delta bounded independently. The executor/reviewer must verify that all ordinary measurements pass for the 32-count case and the 33-count case has exactly the outer slope failure, with decoded side-slope and endpoint values reported from receipts; record hashes for both files. Treat any centroid/level/format/duration/endpoint failures as numeric failed fits, not as evidence about the slope boundary. Missing tools, bad paths, invalid arguments, or generation/measurement exceptions are setup errors and should be recorded separately.

## Evidence / limits

I made no source changes and ran no shell commands; therefore there are no command exit statuses, decoded counts, setup errors, or numeric fit results from this simplifier review. This is only a minimal-diff recommendation, not calibration evidence. It says nothing about audition, sound quality, production, rights, engine use, publishing, or promotion.
