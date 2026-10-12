# Round 11 critic — r11-critic

## Scope and declared claim

I read the Round 11 declared depth claim in `.shokunin/audio/LOG.md`. The claim is narrowly about the decoded-PCM join in `stem_layer` at sample indices 95999/96000: add the absolute mismatch between the adjacent difference before and after the join, using a strict `> .001` FS/sample gate. It is explicitly a fixture-local numerical proxy, not a perceptual or production claim.

## Arithmetic / polarity attack

Given the LOG's clean samples at 95998..96001, `[-.0003662109375, -.00018310546875, 0, .000946044921875]` FS:

- left difference (x[95999]−x[95998]) = `.00018310546875` FS/sample;
- join gap |x[96000]−x[95999]| = `.00018310546875` FS;
- right difference (x[96001]−x[96000]) = `.000946044921875` FS/sample;
- mismatch |right−left| = `.000762939453125` FS/sample.

Thus the proposed strict `> .001` bound passes this stated clean example by `.000237060546875` FS/sample. Polarity matters: signed `right−left` here is positive, but a reversed waveform or opposite kink would be negative. A signed `> .001` test can miss a large negative mismatch; use absolute value if the intended property is magnitude. Equality at exactly `.001` passes under strict `>`; this should be explicit and exercised if asserting polarity. Also, a negative control needs gap <= `.03`, otherwise the existing join gate co-fails and it does not isolate slope mismatch.

## Scope limitations / questions for replay

A two-sided adjacent-difference mismatch can flag a local slope change, but it does not establish audible smoothness: no listening, psychoacoustic threshold, playback path, or engine timing was tested. The bound is borrowed from a start/end loop-slope rule, not calibrated for this internal location; the units match, but the context and salience may not. A passing mismatch also does not bound each side's absolute slope, curvature, longer-window shape, or all possible internal joins. The metric must be computed on the decoded PCM samples actually used by the receipt; verify indexing at the exact join and avoid mixing encoded samples / offsets.

To substantiate sole-failure isolation, replay should show all generic format/duration/level/centroid checks, section validity/contrast, outer endpoint/slope checks, and the old internal gap check pass for the candidate, with only the new internal mismatch gate failing. Verify clean layer stays under bound, equality polarity is strict, and old probe modes/canonical hashes remain unaffected. Without those receipts, this is only a plausible proposal, not validation.

## Commands and exits

No shell commands were run. No audio candidate was created or borrowed. I did not edit source, LOG, SCORECARD, or canonical artifacts.
