# Round 12 scribe — proposed coverage decision table

## Scope and status

This is a decision-table draft from the Round 12 declaration in `.shokunin/audio/LOG.md`, not a verification report. I did not run shell commands or measure fixtures. No Round 12 pass, candidate fit, integration, replay, or adjudication is established here. No source, LOG, SCORECARD, canonical artifact, or commit was changed.

The declared move is **coverage only**: add one original 4 s, 48 kHz mono, stepped-amplitude 180 Hz `stem_layer_alt`, retaining the existing 120 Hz `stem_layer` and all prior controls. The declaration's `.015/.050 * sin(2*pi*180*t)` is a candidate hypothesis, not an accepted recipe. All thresholds are fixture-local reused gates; this is not audibility calibration.

## Decision table: declared before vs. proposed after

| Decision item | Before (`f986933`, per declaration) | Proposed after (must be demonstrated; not yet established) | Evidence required to decide |
|---|---|---|---|
| Canonical coverage | 11 canonical PCM16/48 kHz WAVs | 12, with exactly one new original `stem_layer_alt.wav`; existing 11 unchanged | Hash inventory before/after; compare all original 11 hashes exactly; verify new artifact format, duration and reproducible source recipe. |
| Adaptive-style layer instances | One separately measured 4 s 120 Hz `stem_layer`, two 2 s amplitude sections | Retain that fixture and add a distinct 4 s 180 Hz stepped-amplitude layer with its own 180 Hz section result | Inspect source and normal receipt for both layer entries and their declared component frequencies; decoded measurements for each half. |
| New layer section gate | Existing `stem_layer` section result measures 120 Hz contrast, internal join gap and side-slope mismatch | `stem_layer_alt` must receive its own section result measuring 180 Hz contrast, same two-half validity/6 dB criteria, and internal join gap/slope gates. No new numeric gate. | Source diff shows shared helper/thresholds applied to the new layer; receipt contains new layer section telemetry; component amplitudes valid and contrast >=6 dB; generic, outer seam, internal gap (<=.03), and internal side-slope (<=.001) checks pass. Comparators are strict `>` for existing gap/slope checks. |
| Distinctness from 120 Hz layer | Generic `_alt` path compares duration and centroid, requiring duration delta >=.020 s OR relative centroid delta >=10% | New `_alt` must actually be paired with `stem_layer` and pass this existing distinctness rule | Inspect pairing and receipt's `distinctness` entry; report measured baseline/new centroids and deltas, not assumed identity from filename or generator frequency. |
| Variants / old behavior | Four SFX variants and round-11 controls/modes | Five variants total (four SFX plus layer); old behavior preserved | Non-author serial replay: normal; new 180 Hz negative control if justified; old slope/join/flat30/flat120/outer-slope/failing/invalid; normal restore. Capture exact command and exit for every run, receipt path, and failure classification. The declaration expects nine established round-11 modes plus the new check as applicable; enumerate actual invocations rather than inferring counts. |
| Scope of conclusion | Existing fixture checks only | At most synthetic fixture coverage increases if evidence supports it | No audible/adaptive playback, music, perceptual, engine, security, rights beyond stated original synthesis, or production claim. No audibility calibration. |

## Integration cautions for review

The current fixture source inspected for this draft has `SPECS` entries through `stem_layer`, a generic `_alt` distinctness loop that pairs `stem_layer_alt` with `stem_layer`, and explicit section-result inclusion/component-frequency selection. In the current code, merely adding the artifact would **not** establish 180 Hz section measurement: the explicit section selection and 120 Hz component selection must be deliberately and minimally extended. The per-layer internal gap and slope gate target lists must also include the new layer. Confirm these changes in the eventual diff; do not infer coverage from a generated WAV or the generic `_alt` loop alone.

Do not add another numeric gate. The declared thresholds are existing local fixture gates: 48 kHz mono, 4 s with existing duration tolerance, peak/RMS and centroid bands from the applicable fixture spec, section component amplitude/RMS validity and >=6 dB contrast, endpoint/internal gap `.03`, side-slope `.001`, and `_alt` duration/centroid distinctness `.020 s`/10%. They are not perceptually tuned.

## Exact evidence still needed (none supplied here)

1. Executor recipe, exact shell commands and exits, candidate SHA-256, decoded format/duration/level/centroid, section amplitudes/contrast, outer seam, internal gap/slope, and **all** failure telemetry. A failed fit is telemetry, not a pass. Candidate must be original synthetic PCM; do not borrow samples.
2. Independent source review confirming one new canonical entry and no unrelated changes, correct 180 Hz analysis and gates, correct `_alt` pairing, and unchanged old thresholds/controls.
3. Independent verifier's exact commands/exits and run receipt paths for normal, justified new negative control, each old declared control, invalid mode, and normal restore. Do not treat an author run as independent verification or assert missing invocations.
4. All 12 canonical hashes: first 11 match the declared pre-round baseline; new artifact hash is recorded. Verify five-variant count and each old mode's expected result from actual receipts.
5. Independent per-axis adjudication: coverage improved/unchanged/harmed with rationale; depth and calibration separately unchanged/harmed/improved only where evidence warrants. No verdict is presumed by this draft.
6. Preserve historical receipts/schema; document additive normal-receipt effects and any limitations. No MANIFEST edit or push per declaration.

**Current decision: pending.** The table states a falsifiable target and required evidence only; it does not certify that any proposed-after cell has been achieved.
