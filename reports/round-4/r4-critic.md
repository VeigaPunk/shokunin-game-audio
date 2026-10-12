# Round 4 critic: component-energy contrast is not motif development

## Claim under challenge

The declared candidate adds a 4.0 s loop with two 2.0 s sections, calling a change of at least 6 dB in the relative energy of a named frequency component “motif development.” That threshold can establish a section-to-section contrast in one selected component, if the analysis is precisely defined. It cannot by itself establish that a motif exists, repeats, develops, or is musically organized.

## What the >=6 dB result can and cannot prove

For component energies measured as squared amplitudes, `10*log10(E2/E1) >= 6 dB` means the selected component's measured energy is at least about 3.98 times as large in section 2 as section 1 (about 2x in component amplitude). It proves only that numeric relation for the chosen component, section windows, decoder, and estimator. It is not evidence of perceived development, melody, motif identity, compositional quality, or general soundtrack coverage.

The result is especially weak as a motif proxy unless the component estimator and reference are fixed. A single-bin DFT can be sensitive to phase/window placement and spectral leakage; broad bands can include unrelated partials/noise. If “relative energy” means normalization against total section energy, changing other frequencies or overall level can move the ratio without changing the target component's absolute energy. If it means absolute component energy, simply scaling one section or adding/removing a sustained tone can pass without any recurring motif. A fixed-frequency component also says nothing about its timing or recurrence. The existing overall centroid/bandwidth checks and loop endpoint/slope metrics do not close these gaps; they answer different numerical questions.

For an interpretable fixture-local test, define the target frequency/component, the exact decoded-PCM estimator (including window and normalization), both half-open sample ranges, and whether the comparison is absolute or normalized. Record both raw section energies and the dB calculation; reject zero/near-zero denominators rather than allowing an undefined or floor-driven ratio. Keep the claim phrased as “section component-energy contrast,” not motif development.

## Required flat-section negative control

Build a control from one 2.0 s source section duplicated byte-for-byte as both halves of a 4.0 s file, using the same encoding, boundaries, and analysis as the candidate. The named component should then have 0 dB section contrast (or numerical estimator tolerance only), so a checker that requires >=6 dB must reject it specifically for insufficient contrast. Record section energies, computed dB contrast, failure reason, and exit status. A control that only changes a label or bypasses the same analysis is not informative. Also verify the control retains the declared format/duration and describe any seam behavior separately; a loop guard pass/fail must not be mistaken for the section-contrast result.

This negative control bounds only whether the threshold rejects a flat component-energy comparison. It does not validate that a passing candidate contains a motif or that a listener would hear development. A stronger future test would separately define repeated motif identity and an explicit recurrence/variation measure, with a control that preserves energy contrast while removes the claimed recurrence; that is beyond this round's declared single-component threshold.

## Verdict boundary

Pending raw-PCM estimator details and the flat-section control, I cannot endorse the phrase “>=6 dB represents motif development.” If non-author replay confirms the candidate's exact component contrast, clean loop guards, and the duplicated-section control's isolated rejection, coverage may be credited narrowly for adding a second soundtrack fixture with measurable section contrast. Do not infer musicality, perceptual development, or engine behavior. No audio was auditioned and no shell command was run for this critique.
