# Round 33 critic — duration, distinctness, and coverage limits

## Verdict
A 0.20 s `ui_third` can add a third *duration class* to the analytic corpus if it passes its declared file checks and is explicitly compared with both UI fixtures. The declared 0.08 s and 0.04 s nominal duration gaps are each well above the existing 0.020 s OR threshold. That makes the distinctness result effectively duration-only; it does not establish spectral or perceptual diversity. Treat this as fixture/measurement coverage, not evidence that the sound is usefully different or suitable for a game.

## Challenge to the distinctness inference
The predicate is `duration_delta >= .020 or centroid_relative_delta >= .10`. For .12 s vs .20 s and .16 s vs .20 s, duration alone should make both pairs pass, even if the centroids were identical (or the spectra otherwise duplicated). Thus the result tests that the comparator can report two additional passing comparisons, not that it detected new timbral variety. This is consistent with the predicate's stated OR semantics; it is not a defect if the claim is named narrowly.

Measure and report actual ffprobe duration deltas and centroid deltas for each pair, but label the pass reason per pair. Include both ordered baselines if the implementation reports a relative centroid: that term divides by the baseline centroid and is orientation-dependent. Do not describe a pass as “audibly distinct,” “more varied,” or a validation of the 10% centroid threshold. Duration is a structural property, not a perceptual proxy established by this experiment.

## Coverage claim and risk
The defensible coverage claim is: “the deterministic analytic fixture corpus has a third UI-labeled source at a separately specified 0.20 s duration, and the runner records comparisons against both existing UI fixtures.” It does not prove broader UI coverage, a representative range of interface sounds, comparator correctness in general, or production readiness.

Adding a canonical artifact is a durable schema change, not merely a probe. Risks to check in integration/replay: exact preservation of all 13 old canonical hashes; exactly one additional canonical WAV and its reproducible hash; no accidental rewrite of `ui.wav` or `ui_alt.wav` by the builder; the new spec is included in ordinary validation; both intended pair records exist and identify their baselines; generic `_alt` comparison behavior and thresholds remain unchanged; ordinary normal-run receipt and restoration are clean. A third fixture name may be included by generic enumeration, but it will not automatically generate the two requested pair comparisons unless the runner explicitly creates those records. Avoid claiming the existing five `_alt` comparisons became six: two explicit UI-family edges would be a different graph/count unless deliberately represented as the same schema.

The declared 0.20 s value corresponds to 9,600 samples at 48 kHz. Verify actual frames/duration, mono PCM16/48 kHz, UI-band centroid, peak <.95, RMS >.001, and the existing duration tolerance against the new `.20` spec. If duration is itself the reason both edges pass, say so plainly. The chirp/envelope's measured centroid is still useful as a per-file validity check, not evidence of between-file spectral novelty.

## Evidence boundary
I did not run project commands or modify any fixture/source, so there are no project shell commands/exits to quote. This is a claim/risk critique of the declared round plan, not validation of a generated candidate or replay. A failed fit, setup error, or absent receipt must not be called a gate rejection; report setup/fit status separately if encountered in later rounds.

No claim here about audition or quality, rights, engine integration, publishing, or promotion. The existing 13 canonical files are outside this report's scope and must remain byte-identical.
