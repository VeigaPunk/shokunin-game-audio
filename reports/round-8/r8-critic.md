# Round 8 critic — coverage claim, flat-control isolation, and seam limits

## Scope

This is a source/measurement critique of the declared round-8 claim in `LOG.md` and the current `measure_audio.py`; I did not create audio, run shell commands, or inspect any new candidate measurement. No command/exit evidence is claimed here.

## Coverage claim: bounded, not adaptive-layer coverage

The declared addition is one original four-second mono PCM16/48 kHz waveform on the same 192,000-frame duration grid as `stem_sections.wav`. That can support a narrow **fixture inventory** claim: one additional time-aligned numeric companion waveform was authored and checked. It does not demonstrate that a game engine can enable/disable it, that it is synchronized in an engine, or that it is an adaptive soundtrack layer in operation. Calling the coverage gain “adaptive-layer coverage” without that boundary would overclaim. Keep it described as a source-generated companion fixture; no engine, mix, or listening evidence is in scope.

The declared 120 Hz check also needs to be an actual 120 Hz check. The existing `section_contrast()` hardcodes `component_hz: 30` and FFT bin 60 for each 96,000-sample half (2 s × 48 kHz). At 120 Hz the matching bin is 240. Reusing the current function unchanged would inspect 30 Hz, not 120 Hz. A small explicit component/bin parameter or a distinct fixed 120 Hz measurement is needed, and the receipt should identify the frequency/bin used. The current field name `section_energy_delta_db` is imprecise if computed as `20*log10(amplitude ratio)`; call it component-amplitude contrast (or state the convention) rather than implying integrated section energy.

The claimed 6 dB minimum is a fixture-local analytic discriminator, not a general adaptive-layer or quality threshold. The 0.012→0.060 amplitudes imply about 13.98 dB by the stated amplitude-ratio convention; report measured values and the exact formula, not only a pass. Ensure the lower amplitude clears any amplitude/RMS validity floor. Do not infer that this contrast is audible or musically useful.

## Flat120 isolation

A same-frequency, same-duration, same-format flat120 control at 0.036 FS in both halves is a useful negative control for the *contrast predicate*: its ideal component-amplitude delta is 0 dB. It is not sufficient to say it “fails only its section contrast” from construction alone. That isolation requires the complete independent receipt to show format, duration, level, centroid, loop endpoint/slope checks and any distinctness checks pass, with the section contrast as the sole failure. In particular, verify the generated PCM and measured centroid rather than assume them from nominal sine parameters, and verify no unintended waveform difference or clipping.

The candidate and control should use the same method and section boundaries; only the section amplitude schedule should differ. If the control is used only by the new `--probe-layer-flat` mode, confirm it is not silently added to canonical assets or counted as a canonical layer. The existing `--probe-flat` means the round-4 flat30 control, so a distinct option name is appropriate, but both controls/modes should remain independently exercised. A flat control that passes all generic checks and fails only the new contrast predicate validates that predicate's discrimination on these two analytic signals; it does not validate detector sensitivity across arbitrary material.

## Internal boundary versus loop seam

The existing loop endpoint and slope metrics compare only sample 0/last sample and their adjacent slopes. They do not examine the internal transition at frame 96,000 between the two sections. The section contrast also compares the halves independently and does not test continuity at their join. Therefore a good outer loop seam cannot establish a seamless section transition.

For the declared signal, both sections are 120 Hz and each is exactly 2 s (240 cycles), so a sine phase can align at the boundary. But changing amplitude from .012 to .060 still changes the derivative at that boundary unless the transition is arranged/smoothed; if the transition occurs at a zero crossing, sample value can match while slope changes. Report the join samples/slopes or explicitly label this as a hard authored section boundary and make no seam/transition-quality claim. Do not fold the loop-endpoint/slope result into a claim about the internal boundary.

## Recommendation

Admit at most a narrow coverage move if independent replay confirms one extra companion WAV, all ten previous canonical hashes remain unchanged, and the measured 120 Hz control pair behaves as specified. Phrase the result as numeric companion-fixture coverage, not adaptive-engine capability or quality. Keep calibration unchanged unless the method/threshold itself is separately justified; the proposed 6 dB rule is local. Keep depth unchanged unless the new detector is independently shown to add a needed measurement. No perceptual, engine, security, production-readiness, or seam-at-boundary claim follows from the declared evidence.
