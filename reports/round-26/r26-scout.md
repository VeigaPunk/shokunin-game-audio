# r26-scout — current `_alt` lookup and duplicate failure condition

## Scope and method
Read `.shokunin/audio/LOG.md` round-26 claim and inspected `corpus/fixtures/measure_audio.py`, `corpus/fixtures/build_artifacts.py`, and the latest normal receipt `corpus/live/runs/20261013T014026304512Z-normal/measurements.json`. No shell commands were run; inspection was through the Python REPL. No files other than this report were written.

## Current lookup and rule
`SPECS` defines the five `_alt` fixtures. The runner measures every entry in `SPECS`, then iterates the measurement names and considers only names ending exactly in `_alt`. It chooses the base by `measurements[name[:-4]]` (remove the final `_alt`), so the current comparisons are `ui_alt`→`ui`, `impact_alt`→`impact`, `movement_alt`→`movement`, `ambience_alt`→`ambience`, and `stem_layer_alt`→`stem_layer`.

It calculates absolute duration delta and relative centroid delta `abs(alt_centroid - base_centroid) / base_centroid`. Distinctness passes if `duration_delta >= .020` **OR** `centroid_relative_delta >= .10`. It appends exactly `distinctness: duration < .020 s and centroid delta < 10%` when **both** values are below their thresholds. Thus an exact matched duplicate should give zero duration and centroid deltas, fail distinctness, and not fail via this rule merely for being a duplicate; any other fixture checks still independently apply.

## Latest recorded five-pair results
From the cited normal receipt (all five `_alt` fixture `failures` arrays are empty):

| Alt → base | Duration delta (s) | Relative centroid delta | Distinctness |
|---|---:|---:|---|
| `ui_alt` → `ui` | 0.04000000000000001 | 0.47187731004956435 | pass (both) |
| `impact_alt` → `impact` | 0 | 0.9563048992406177 | pass (centroid) |
| `movement_alt` → `movement` | 0.12 | 0.007518618572621081 | pass (duration) |
| `ambience_alt` → `ambience` | 0 | 0.5845136323520758 | pass (centroid) |
| `stem_layer_alt` → `stem_layer` | 0 | 0.46179931396667484 | pass (centroid) |

The ordinary checks in `measure()` independently test stream format, duration within ±1 ms of its spec, peak/RMS level, and centroid band; loop specs additionally check endpoint and slope seam deltas. The stem-layer pair is also subject to its existing section-contrast and internal-join checks. The cited normal receipt records no failures for these alts.

## Limits
This is a source/receipt map, not execution of a new duplicate control. The exact negative is a numerical duplicate test at zero/zero, not a threshold-boundary test, audible-similarity judgment, universal deduplicator, or evidence about an engine, rights, publishing, or promotion. No such claims are made.
