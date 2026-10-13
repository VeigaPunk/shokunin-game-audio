# Round 45 scout — negative ordinary duration tolerance

## Map and signed frame arithmetic

The ordinary per-file duration gate in `measure()` parses the `ffprobe` format duration as a Python float and appends `duration: outside ±1 ms` only when `abs(duration - spec[0]) > .001` (source: `corpus/fixtures/measure_audio.py`, lines 78–79). Its comparison is absolute distance from the declared per-file target; a negative signed deviation is not a separate predicate.

For the declared 48 kHz UI target of 0.12 s, the nominal target is 5760 frames. The proposed negative-side controls are:

| Frames | Offset from target | Signed frame-derived delta | Nominal duration | Expected ordinary result |
|---:|---:|---:|---:|---|
| 5713 | -47 frames | `-47/48000 = -0.0009791666666666666 s` | `5713/48000 = 0.11902083333333333 s` | within 1 ms (pass) |
| 5711 | -49 frames | `-49/48000 = -0.0010208333333333334 s` | `5711/48000 = 0.11897916666666667 s` | outside 1 ms (fail) |

These are frame arithmetic, not measured `ffprobe` values.

This complements R44's positive-side ordinary-gate pair: 5807 frames (+47) probed as `.120979`, Python delta `+.0009790000000000076` and passed; 5809 (+49) probed as `.121021`, delta `+.001021000000000008` and failed solely on duration. R44 therefore covered the positive interior/exterior polarity; this proposed pair covers the negative polarity, under the same target and strict `>` comparator. The 5712-frame midpoint is not an equality test and must not be described as one.

Do not conflate either ordinary per-file tolerance pair with R27's pairwise distinctness predicate. R27 compares a variant against a baseline and accepts duration separation at `>= .020 s` (or a centroid-relative separation at `>= .10`); its 6719/6720-frame pair measured that distinctness rule with separately declared variant duration specs. It did not test ordinary ±.001 s compliance. Signed negative deviation from a single target and positive pairwise separation are different quantities and gates.

## ffprobe and floating-point caveat

Frame-derived rational deltas predict the intended sides of the threshold, but the runner compares a decimal duration reported by `ffprobe`, parsed to binary float, against the target float. The measured duration string, parsed value, and signed delta `duration - .12` must be reported for each generated candidate; actual pass/fail depends on `abs(delta) > .001`, not ideal frame arithmetic or a rounded display. Decimal rounding and binary subtraction can move a nominal boundary value across strict `>`; no exact ±.001 equality, symmetric floating behavior, or 5712-frame outcome should be inferred without an actual measurement. R44's disposable 5808-frame case illustrates this: `.121000` parsed to delta `.0010000000000000009`, so it failed strict `>.001`, not an equality pass.

## Evidence status and scope

I did not run shell commands, generate or probe candidates, run the fixture runner, or measure hashes/exits. Thus there are no measured candidate durations/deltas or numeric fit outcomes to report; the table is arithmetic only. There are no shell/setup errors or numeric failed fits from this scout. The expected 5713 pass / 5711 sole-duration failure remain a declared calibration target, not verified evidence.

Numerical fixture calibration only. No audition, quality, production, rights, engine, publishing, or promotion inference.
