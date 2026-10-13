# Round 21 scribe — numeric decision table and calibration limits

## Decision table (declared hypothesis; not a result)

| Case | Internal-join decoded sample delta | Full-scale value | Strict gate (`> 0.03`) | Expected section result | Decision if the paired replay confirms all controls |
|---|---:|---:|---|---|---|
| Lower edge | 983 PCM16 counts | 983/32768 = 0.029998779296875 | No | No internal-gap failure | Pass this gate only |
| Upper edge | 984 PCM16 counts | 984/32768 = 0.030029296875 | Yes | Sole internal-gap failure | Fail this gate only |

The declared discriminator is the strict comparison: exactly `0.03` would not fail, while the 984-count value is above it. Quantization matters: 0.03 × 32768 = 983.04, so 983 and 984 decoded counts straddle the cutoff. The values are decoded-float full-scale deltas for this PCM16/SoX measurement path, not generic audio tolerances.

## Isolation requirements for accepting the calibration claim

The candidate pair must preserve the 200 Hz component contrast (at least 6 dB and valid component/RMS amplitudes), format (48 kHz mono), four-second duration within 1 ms, peak below 0.95, RMS above 0.001, centroid within 100–2000 Hz, and the internal side-slope mismatch at or below 0.001 full scale/sample. The only expected difference in failure lists is the internal-gap failure at 984; 983 must not carry it. Section `passed` means contrast only, not that the full measurement has no failures. Any additional failure invalidates the claimed isolated bracket; do not adjust another threshold to force a pass.

The declared round-21 move is calibration only: it does not retune the strict `> .03` gate, add a detector, establish perceptual/audibility meaning, or certify an engine/production runner. Preserve all 13 canonical SHA-256s, five `_alt` distinctness outcomes, prior 17 replay modes and existing thresholds as specified in `.shokunin/audio/LOG.md`. Full acceptance remains contingent on the separately declared non-author serial replay of 19 modes and its evidence; a scratch fixture or arithmetic alone is not runner integration evidence.

## Evidence and limitations

The round-21 declaration and historical round-20 result are documented in `.shokunin/audio/LOG.md`. It records the existing 984-count-associated gap as 0.030029296875 FS, the round-20 selected probe's sole gap failure, and 200 Hz contrast 10.457519263296449 dB. The fixture source `corpus/fixtures/measure_audio.py` implements `internal_join_adjacent_delta_full_scale > .03` and reports the section contrast separately. `build_artifacts.py` records the PCM16 writer's `round(clip(samples)*32767)` encoding; decoded measurement is then through SoX float output. These facts support the proposed numerical bracket, but no round-21 candidates or replay receipts were present when this note was drafted. Therefore both table outcomes remain predictions, not observations, and no integration or sensory claim is made.

Commands executed for this report: none (source and declaration were read through the Python REPL). Thus there are no shell exit codes to report. No shared files, fixtures, canonical artifacts, or other reports were edited.
