# Round 18 scribe — proposed depth-axis decision (draft)

## Before / proposed after

| axis | before (`7083a3f`) | proposed after, pending implementation and evidence |
|---|---|---|
| depth | The original 200 Hz `stem_layer_third.wav` passes the existing internal side-slope check at `.00091552734375` FS/sample (30 PCM counts / 32768, below the strict `.001` limit). The prior log identifies no matched 200 Hz slope-only negative. | Add one opt-in scratch probe derived from that original WAV, increasing decoded PCM frame 96001 from 43 to 51 (+8 counts). On the logged neighboring samples `[-26,-13,0,43]` at frames 95998–96001, this predicts a side-slope mismatch of 38/32768 = `.00115966796875` FS/sample, crossing the existing limit. This is a hypothesis only; no runner result is established here. |
| coverage | 13 original canonical measured WAVs, including the 200 Hz third layer. | Intended unchanged: the probe is scratch, not canonical content; all 13 canonical hashes should remain unchanged. |
| calibration | Existing local slope limit `.001` FS/sample, gap limit `.03` FS and section contrast minimum 6 dB. | Intended unchanged: reuse the existing slope gate without threshold adjustment. |

## Evidence needed before admission

A valid depth result requires an independently measured scratch WAV and a receipt showing that the probe fails **only** the 200 Hz internal side-slope gate, while section validity/contrast, internal join gap, generic level/format/spectrum and outer seam checks pass. Confirm the exact decoded PCM frames and computed mismatch rather than relying on the +8-count arithmetic prediction. If another gate fails, record that as a failed fit and adjust the probe without relaxing thresholds. A non-author replay must establish the probe behavior and preservation of the 13 canonical hashes, prior negative-mode outcomes, five `_alt` comparisons, and normal/restore equality; the planned mode count is 14, but no replay is claimed here. Named adjudicator judgment remains necessary.

## Limits

This is a proposed bounded test-depth move, not evidence of an actual runner outcome. The threshold is an existing numeric proxy, not perceptual calibration. No audible, musical, adaptive-engine, security, rights, external JSON compatibility, or production claim follows. Scratch control evidence does not add content coverage. Any setup failure or failed fit must be reported separately from a successful negative-control result.
