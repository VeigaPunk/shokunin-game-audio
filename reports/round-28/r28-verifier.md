# Round 28 independent verifier — NON-AUTHOR

## Verdict

**The integrated runner verifies the requested two-point centroid-polarity probe, narrowly.** I ran 24 invocations serially: initial normal, `--probe-ui-centroid-below`, `--probe-ui-centroid-above`, then the previous round-27 22-invocation sequence (initial normal and its prior modes), ending with normal restore. Below exited 1 for the sole `ui_centroid_below_alt` distinctness failure; above exited 0. Both baseline and alternate files ordinarily pass the same canonical `SPECS["ui"]` .12 s checks (no per-file failures), and the existing distinctness comparator alone distinguishes them. Their measured duration deltas are 0; measured relative centroid deltas are `0.09434076861679014` and `0.10454649711208937`. The existing OR predicate remains duration `>= 0.020 s` or relative centroid `>= 0.10`. This establishes polarity at these two measured points only: there is no exact `.10` equality claim, monotonicity claim, or perceptual/audible similarity or quality finding.

## Replay evidence

All commands ran from repository root, serially, with exact common prefix `python3 .shokunin/audio/corpus/fixtures/measure_audio.py`. Each receipt below is runner-generated at `.shokunin/audio/corpus/live/runs/<timestamp>-<mode>/measurements.json`. Exit-1 results are expected negative fixture outcomes, not setup failures. There were no setup failures, tracebacks, or exit-2 outcomes in these 24 invocations.

| # | Exact command suffix | Exit | Receipt directory | Failure kind |
|---:|---|---:|---|---|
| 1 | *(no suffix; normal)* | 0 | `20261013T021551416503Z-normal` | none |
| 2 | `--probe-ui-centroid-below` | 1 | `20261013T021552325140Z-ui-centroid-below` | `ui_centroid_below_alt`: `distinctness: duration < .020 s and centroid delta < 10%` only |
| 3 | `--probe-ui-centroid-above` | 0 | `20261013T021553318570Z-ui-centroid-above` | none |
| 4 | `--probe-ui-duration-below` | 1 | `20261013T021554241651Z-ui-duration-below` | `ui_duration_below_alt`: distinctness only |
| 5 | `--probe-ui-duration-at` | 0 | `20261013T021555170889Z-ui-duration-at` | none |
| 6 | `--probe-ui-clone` | 1 | `20261013T021556100089Z-ui-clone` | `ui_clone_alt`: distinctness only |
| 7 | `--probe-layer-third-join-edge-pass` | 0 | `20261013T021557025335Z-layer-third-join-edge-pass` | none |
| 8 | `--probe-layer-third-join-edge-fail` | 1 | `20261013T021557960315Z-layer-third-join-edge-fail` | `join200_edgefail_probe`: sections, internal join adjacent sample gap > .03 full scale |
| 9 | `--probe-layer-third-join` | 1 | `20261013T021558884376Z-layer-third-join` | `join200_probe`: same sections join-gap failure |
| 10 | `--probe-layer-third-slope-edge-pass` | 0 | `20261013T021559802480Z-layer-third-slope-edge-pass` | none |
| 11 | `--probe-layer-third-slope-edge-fail` | 1 | `20261013T021600715471Z-layer-third-slope-edge-fail` | `edgefail_probe`: sections side-slope mismatch > .001 full scale/sample |
| 12 | `--probe-layer-third-slope` | 1 | `20261013T021601635798Z-layer-third-slope` | `slope200_probe`: same sections slope failure |
| 13 | `--probe-layer-alt-reverse` | 1 | `20261013T021602522944Z-layer-alt-reverse` | `reverse180_probe`: sections 180 Hz contrast < 6 dB or invalid |
| 14 | `--probe-layer-alt-slope` | 1 | `20261013T021603425919Z-layer-alt-slope` | `slope180_probe`: sections side-slope mismatch > .001 full scale/sample |
| 15 | `--probe-layer-alt-join` | 1 | `20261013T021604313594Z-layer-alt-join` | `join180_probe`: sections internal join gap > .03 full scale |
| 16 | `--probe-layer-alt-flat` | 1 | `20261013T021605202755Z-layer-alt-flat` | `flat180_probe`: sections 180 Hz contrast < 6 dB or invalid |
| 17 | `--probe-layer-slope` | 1 | `20261013T021606074624Z-layer-slope` | `layer_slope_probe`: sections side-slope mismatch > .001 full scale/sample |
| 18 | `--probe-layer-join` | 1 | `20261013T021606956343Z-layer-join` | `join_probe`: sections internal join gap > .03 full scale |
| 19 | `--probe-flat` | 1 | `20261013T021607862182Z-flat` | `flat30_probe`: sections 30 Hz contrast < 6 dB or invalid |
| 20 | `--probe-layer-flat` | 1 | `20261013T021608760607Z-layer-flat` | `flat120_probe`: sections 120 Hz contrast < 6 dB or invalid |
| 21 | `--probe-slope` | 1 | `20261013T021609635111Z-slope` | `slope_probe`: loop seam slope mismatch > .001 full scale/sample |
| 22 | `--probe-failing` | 1 | `20261013T021610470299Z-failing` | `ambience`: centroid outside fixture band; loop seam endpoint jump > .03 full scale |
| 23 | `--probe-invalid` | 1 | `20261013T021610820962Z-invalid` | eight expected statuses below |
| 24 | *(no suffix; restore normal)* | 0 | `20261013T021611646952Z-normal` | none |

For every row, append `/measurements.json` to the receipt directory to obtain the exact receipt path. Thus, e.g., row 2 is `.shokunin/audio/corpus/live/runs/20261013T021552325140Z-ui-centroid-below/measurements.json`.

The two new receipts record baseline `ui_centroid_<label>` and variant `ui_centroid_<label>_alt`, with the same canonical `ui` baseline mapping. Below: baseline and variant each duration `.12`, 48 kHz mono PCM16, failures `[]` before the runner's pair distinctness result; duration delta `0.0`, relative centroid delta `0.09434076861679014`, distinctness false. Above: same ordinary checks and duration delta `0.0`, relative centroid delta `0.10454649711208937`, distinctness true. The baseline centroid is `966.8966593379727 Hz`; alternate measured centroids are `1058.1144333529237 Hz` (below) and `1067.9823181411389 Hz` (above). Recomputed as `abs(variant - baseline) / baseline`, these match the receipt deltas above. Both variants pass the canonical UI format, level, duration, and 250–4000 Hz centroid-band checks; distinctness is the only below failure.

Invalid control statuses from row 23: `short_sections` expected_failure / section count; `corrupt` expected_failure / decode; `wrong_format` expected_failure / format; `odd_sections` expected_failure / section count; `native16_probe` expected_pass / no failure; `native24_probe` expected_failure / format; `stereo48_probe` expected_failure / format; `mono441_probe` expected_failure / format. All eight match the expected statuses.

## Prior-22 mapping and preservation

The requested historical subset is prior 22 invocations = this replay's initial normal **#1** plus prior modes **#4–#24** (21 rows); the two newly added centroid modes are #2–#3. The prior sequence's 22nd/restored normal corresponds to #24 here. All prior outcomes match `.shokunin/audio/reports/round-27/r27-verifier.md`: 8 exit-0 and 14 expected exit-1 rows, including the 8 invalid-control statuses; no setup failure/traceback/exit 2.

Current `HEAD` is `13a19e2ea39f7bb3d04ee42b5a2e458b4bde461b`, the declared round baseline. I computed SHA-256 with Python `hashlib` for the 13 canonical WAVs; all hashes match the round-27 guard baseline. The five old `_alt` comparisons retain their baseline names and pass in initial and restored normal receipts: `ui_alt` delta .04000000000000001 / centroid .47187731004956435; `impact_alt` 0 / .9563048992406177; `movement_alt` .12 / .007518618572621081; `ambience_alt` 0 / .5845136323520758; `stem_layer_alt` 0 / .46179931396667484.

The complete receipt `thresholds` objects are identical across the replay and preserve duration minimum `.02` and centroid minimum `.1`; no threshold changes. Initial and restored normal receipts are equal after removing only measurement `path` fields. The fixture diff against HEAD is limited to opt-in builder/runner wiring for the two centroid modes and their pair measurements; the existing predicate/constants, canonical artifacts, and other modes are unchanged. `git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts .shokunin/audio/corpus/fixtures` returned exit 1 because the two fixture source files contain the described round-28 changes; canonical WAV hashes nevertheless match. Round-27 source changes were committed in `HEAD` (`13a19e2ea39f7bb3d04ee42b5a2e458b4bde461b`) before round 28; the prior-22 subset is #1 plus #4–#24.

## Limits and scope

The candidate sweep was nonmonotonic; these two selected points show a measured comparator polarity only. No exact `.10` equality, monotone parameter-to-centroid relation, perceptual similarity, audible quality, engine/runtime, rights, publication, or promotion is established. I did not edit source, LOG, SCORECARD, canonical WAVs, or another report, and did not commit or push. I wrote only `.shokunin/audio/reports/round-28/r28-verifier.md`; runner-generated receipts are in `corpus/live/runs/` as listed.
