# r28-simplifier

## Recommendation

Keep this as a two-point polarity check around the existing centroid-relative comparator, not a generalized search facility. Preserve the existing `.10` constant and canonical specs/artifacts. Generate a same-duration baseline and two source-side variants in round-28 scratch only; hold sample count (5760), sample rate (48 kHz), mono PCM16 encoding, envelope, and output level fixed. Vary one named analytic waveform parameter. Choose and record the two parameter values before any runner integration, based on measured centroid deltas on opposite sides of `.10`.

The simplest candidate is a small change to one chirp coefficient in the existing UI-shaped analytic signal, leaving duration and envelope fixed. This is only a candidate: the measured centroid is an FFT-magnitude-weighted proxy, not a direct function of that coefficient. Do not report a successful fit until actual SoX/FFT/ffprobe measurements show both variants pass the ordinary UI gates and duration delta is zero. If a concise fixed candidate pair cannot meet those conditions, report failed fit rather than adding a reusable optimizer, widening the parameter sweep into production code, or changing limits.

## Integration boundary

If a pair is demonstrated, runner support should expose only the two named opt-in probes needed to measure the pair and apply the existing comparator. Keep the baseline and variants outside canonical `SPECS`, leave existing modes and fixtures untouched, and avoid duplicating comparison logic. Report observed values and failures separately; no exact `.10` equality is needed or implied.

## Scope and evidence

No project commands or measurements were run for this simplification review (there are no command exit codes to report). No fit is claimed. This addresses numeric centroid proxy behavior only; it makes no audibility/perception, rights, engine, publishing, or promotion claim.
