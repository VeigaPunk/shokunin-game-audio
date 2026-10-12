# Round 3 simplifier recommendation

## Smallest integration

Keep the existing entrypoint and checks. Add one decoded-PCM quantity for loop fixtures only: `slope_join_delta = abs((x[1] - x[0]) - (x[-1] - x[-2]))`, in full-scale units per sample. Record it in each loop measurement and apply a separate local threshold alongside (not instead of) the existing endpoint-amplitude threshold. This is a numerical join proxy, not an audibility criterion.

The clean PCM16 artifacts currently give slope-join deltas: `ambience` 3.05176e-5, `ambience_alt` 0, `stem` 3.05176e-5 full-scale/sample. A simple bound with margin is `1e-4` (roughly 3.3x the observed maximum); label it as a local fixture bound, not universal. Include this bound and units in receipt thresholds. Preserve all existing measurement and distinctness checks unchanged.

Add a separate `--probe-slope` mode, not a change to normal measurement or `--probe-failing`. It should build a temporary positive-control WAV from generated fixture data, setting its last sample exactly equal to its first while altering the second sample (or penultimate) enough that the slope-join delta exceeds `1e-4`. Do not write over canonical artifacts. Measure its endpoint and slope metrics, require endpoint delta <= .03 and slope delta > bound, and write a distinct probe receipt. Keep normal mode's nine-fixture pass/fail status independent of this probe. This isolates slope detection from the existing broken-amplitude probe and avoids adding a test framework.

## Scope / evidence notes

I inspected the current measurement/builder scripts and directly read the three loop WAVs as decoded PCM16 for the figures above. No shell command was run; therefore there are no shell exit codes to report. I did not edit scripts or artifacts, and make no listening or perceptual claim. Parent owns implementation and verification.
