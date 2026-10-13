# Round 27 independent verifier — NON-AUTHOR

## Verdict

**Narrow adjacent-count duration comparison verified in the integrated runner; no exact-equality claim.** I serially replayed 22 invocations: initial normal, below and at duration probes, Round 26 clone plus its prior 17 modes in the recorded order, then normal restore. `--probe-ui-duration-below` exited 1 solely for the new variant distinctness failure; `--probe-ui-duration-at` exited 0. Both scratch pairs passed their per-file format/level/centroid checks and separately declared duration specs. The `.120 s` canonical UI duration spec is not claimed for the longer scratch variants. The measured ffprobe durations are six-decimal values; subtraction yields `0.019978999999999997` and `0.020000000000000018`. The latter is above `.020`, not exact equality. Evidence establishes only this adjacent 6719/6720-frame transition through this runner/toolchain. No threshold was changed.

## Serial replay: exact commands, exits, receipts, failure kinds

Commands ran serially from repository root. Empty failure set is `{}`. Receipts are runner-generated JSON. No setup failures, tracebacks, or exit 2 occurred in these 22 invocations.

| # | Exact command | Exit | Receipt | Failure kind(s) |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T020338855236Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020339743260Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T020340636504Z-ui-duration-at/measurements.json` | none |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020341529003Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T020342415924Z-layer-third-join-edge-pass/measurements.json` | none |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020343300607Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020344195278Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T020345077240Z-layer-third-slope-edge-pass/measurements.json` | none |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020345953896Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020346844027Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020347721286Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020348594260Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020349481477Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020350378429Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020351268783Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020352146744Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020353035938Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020353913916Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020354786161Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020355602382Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band, loop seam: endpoint jump > .03 full scale |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T020355945654Z-invalid/measurements.json` | short_sections: section count; corrupt: decode; wrong_format: format; odd_sections: section count; native16_probe: None; native24_probe: format; stereo48_probe: format; mono441_probe: format |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T020356764840Z-normal/measurements.json` | none |

## Duration probe observations and isolation

The `below` and `at` receipts record baseline/variant names `ui_duration_below` → `ui_duration_below_alt` and `ui_duration_at` → `ui_duration_at_alt`. Both baselines are 5760 frames, ffprobe `0.120000` s. Variants are 6719 frames / `0.139979` s and 6720 frames / `0.140000` s. The six-decimal ffprobe strings, not nominal frame ratios, are comparator inputs. Receipts show:

| Pair | Ordinary per-file failures (baseline / variant) | Duration delta | Centroid relative delta | Duration arm `>= .020` | Centroid arm `>= .10` | Distinctness |
|---|---|---:|---:|---|---|---|
| below | `[]` / `[]` before runner-appended distinctness | `0.019978999999999997` | `0.026103720992748162` (< .10) | false | false | fail; only `distinctness: duration < .020 s and centroid delta < 10%` appended |
| at | `[]` / `[]` | `0.020000000000000018` | `0.028427598871782873` (< .10) | true | false | pass |

Both variants were measured with an individual UI-shaped spec `(expected_duration, 250, 4000, False)`: baseline `.12`, below variant `6719/48000` s, at variant `6720/48000` s. This isolates the distinctness comparator while retaining format (48 kHz mono PCM16), peak/RMS, and 250–4000 Hz centroid-band checks; it does **not** show that the variants pass canonical `SPECS["ui"]` duration `.12 s` (±.001 s). Existing thresholds remained unchanged. The distinctness minima remain `.020 s` and `.10`.

The below/at receipts contain full measurements and distinctness mappings. Each `_alt` suffix maps to the baseline name formed by removing `_alt`. No per-file failure was conflated with the negative distinctness result.

## Preservation checks

- SHA-256 for all 13 canonical WAVs matches the Round 26 baseline table in `r27-guard.md` (reference `666688827adc3bcf0e4c67b481fc827d900ae2e7`): all 13 unchanged.
- The five existing `_alt` comparisons in both initial and restored normal receipts match prior normal results and pass: `ui_alt` (duration `0.04000000000000001`, centroid `0.47187731004956435`); `impact_alt` (`0.0`, `0.9563048992406177`); `movement_alt` (`0.12`, `0.007518618572621081`); `ambience_alt` (`0.0`, `0.5845136323520758`); `stem_layer_alt` (`0.0`, `0.46179931396667484`).
- Threshold objects in initial and restored normal receipts are equal, and equal the prior Round 26 normal threshold object. Normal and restored normal receipts compare equal after recursively excluding `path` fields; current normal also equals Round 26 initial normal on that basis.
- All 8 invalid-control statuses remain as expected in replay #21: `short_sections` → `expected_failure/section count`; `corrupt` → `expected_failure/decode`; `wrong_format` → `expected_failure/format`; `odd_sections` → `expected_failure/section count`; `native16_probe` → `expected_pass/none`; `native24_probe`, `stereo48_probe`, `mono441_probe` → `expected_failure/format`.
- The prior 20-mode outcomes are reproduced in this replay (#1 and #4–#22: initial normal, clone, prior 17 modes, restored normal): exits and failure kinds match `reports/round-26/r26-verifier.md`. The five legacy `_alt` comparisons are unchanged.

## Failed/setup outcomes and scope

No setup failures or failed fits occurred during this replay. The 6719 case is the intended distinctness negative, not a setup or per-file measurement failure. Earlier worker notes mention an unrelated corrected relative-path error during separate direct-fit work; it was not part of this replay.

This is a numeric comparison for two source-generated 48 kHz PCM16 UI scratch variants. It does not demonstrate exact equality: observed subtraction is `0.020000000000000018` (> `.020`), and only the adjacent 6719/6720 transition is observed. No perceptual/audio-quality, engine/runtime, rights, publishing, promotion, or clearance claim. No shared source, log, scorecard, canonical artifact, or other report was edited; no commit or push.
