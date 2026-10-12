# Round 13 independent critical review — failure isolation and claim limits

## Basis

I read the round-13 declaration in `.shokunin/audio/LOG.md`, the fixture builder and measurement runner. I did not run shell commands, generate fixtures, or change shared source. This is a source-level critique, not evidence that a candidate control has been built or passed.

## Main isolation risk

The promised sole-failure claim needs stronger evidence than a single `sections: 180 Hz component amplitude contrast < 6 dB or invalid` entry. The runner emits that same failure for both a valid contrast below threshold and an invalid section measurement. The receipt must therefore show `sections.flat180_probe.valid == true`, finite amplitudes/RMS above the validity floors, and a measured contrast below 6 dB (ideally near 0 dB), alongside the failure list. Otherwise it has not isolated the contrast branch from invalid-input behavior.

There is also a gate-wiring blind spot: the internal-join and internal-side-slope failure checks are explicitly name-gated to `stem_layer`, `stem_layer_alt`, `join_probe`, and `layer_slope_probe`. A probe named `flat180_probe` gets section metrics but is not subjected to those two internal checks by the current runner. Its measurements passing numerically would not prove the runner rejects a bad join/slope on that probe. Keep the candidate construction continuous and report internal join gap and side-slope values anyway; describe the control as testing the contrast branch, not as independently validating all 180Hz-specific gates. Do not widen source scope to fix this unless the parent revises the declared one-control scope.

The ordinary `measure()` gates do apply to a probe passed through its path: 48kHz mono, duration, peak/RMS, centroid band, and endpoint seam/slope. Verify their values/failure list in the receipt. A sine with an abrupt half-boundary phase/sign discontinuity could still fail generic endpoint gates or yield non-flat spectral content; use equal-amplitude, phase-continuous halves of the same 180Hz sinusoid and verify actual decoded metrics rather than infer success from the formula.

## Distinctness and threshold polarity

Do not call the control `stem_layer_alt` or another `_alt` name. `_alt` records are evaluated against a baseline by duration/centroid distinctness, which is a separate condition and could add an unrelated failure. `flat180_probe` is not `_alt`, so it avoids that check. The canonical `stem_layer_alt` should remain passing and distinctness should remain unchanged.

The code computes signed `20*log10(second_half_amplitude / first_half_amplitude)` and accepts only `>= 6.0`; equal halves produce approximately 0 dB and should fail. Do not use absolute contrast or reverse the ratio to make a weak-first/strong-second signal pass. The 6 dB cutoff and amplitude/RMS validity floors are existing constants, not tuned by this round. Check validity and contrast explicitly because the combined failure text alone obscures threshold polarity and invalidity.

## Claim boundary / falsifiers

A clean original synthetic flat control that has valid sections near 0 dB, only the intended measurement failure, and otherwise passing reported ordinary metrics would support a narrow claim: this deterministic numeric check distinguishes the existing unequal-half 180Hz fixture from one equal-half synthetic control. It would not demonstrate that the waveform sounds flat, that a listener hears the difference, or that an audio engine, music workflow, security property, or production behavior is correct.

Falsify the claimed isolation if the canonical alt fails, the control has any additional failure, validity is false, or its contrast is not below 6 dB. Also do not treat a passing flat control as proof that the internal join/slope guards are exercised for this new probe name; their runner branches currently exclude it. No shell commands were run, so there are no command exits to report.
