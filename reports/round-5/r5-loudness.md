# Round 5 loudness scout

## Evidence examined

I read the declared round-5 claim/spec in `.shokunin/audio/LOG.md`, the fixture-battery knowledge note, `corpus/fixtures/measure_audio.py`, the ten WAV files under `corpus/artifacts/`, and the latest clean receipt `corpus/live/runs/20261012T164320494590Z-normal/measurements.json`. The receipt is one of five available round-5 clean normal receipts (`163815397777Z`, `163817890027Z`, `164259005327Z`, `164313398133Z`, `164320494590Z`); all five report the same loudness values. It has 10 clean measurements and no per-file failures. The ten artifacts are generated analytic/seeded source WAVs, not borrowed samples.

Decoded PCM16 RMS values recomputed from those ten WAVs match the receipt’s `rms_dbfs` values (within printed precision):

| Fixture | integrated LUFS | RMS dBFS |
|---|---:|---:|
| ui | null | -19.9917 |
| ui_alt | null | -20.5255 |
| impact | null | -20.4022 |
| impact_alt | null | -17.3296 |
| movement | null | -23.7799 |
| movement_alt | null | -21.9873 |
| ambience | -30.7 | -18.1534 |
| ambience_alt | -24.7 | -17.6703 |
| stem | -15.8 | -14.8814 |
| stem_sections | -24.7 | -23.0665 |

Thus the reported integrated-LUFS distribution is **6 null / 4 finite**; the finite range is **-30.7 to -15.8 LUFS**. Across all ten, RMS ranges **-23.7799 to -14.8814 dBFS**. Null is not zero, silence, or a numeric loudness measurement to include in a range. The receipt/source explicitly converts a parsed non-finite value or any parsed value `<= -70` to null. It emits `integrated_lufs` only when the parsed result is finite and above that floor.

## Interpretation / calibration limits

The `-70 LUFS` comparison is an ebur128 measurement/gating floor convention in this code, not a minimum-level acceptance threshold for assets. The short SFX have RMS from about -17 to -24 dBFS while their LUFS results are null, demonstrating that null does not imply silence. The longer ambience, music stem, and four-second two-section stem receive finite readings, but those values do not define a pass/fail target: no loudness acceptance window is declared or enforced in the receipt. RMS is separately measured and only the generic `rms > 0.001` floor is enforced; that is a near-silence guard, not loudness matching.

This supports the narrow decision-table wording “ebur128 integrated loudness: finite values as reported; null means absent/at-or-below the implementation’s -70 floor; no acceptance window / no LUFS pass criterion.” Do not infer a universal ebur128 gate behavior for all material from these ten generated files, or infer a mastering target, perceived level, comparability across content, or audio quality. The four finite values and six nulls describe this fixture battery and this implementation only. A brief signal could produce no usable integrated result for reasons tied to duration/content and gating; the observed RMS values establish only that these six files are not silent under the receipt’s RMS measure.

No thresholds or source definitions were changed. No external shell commands were run; this analysis used Python to inspect receipts/source and decode WAV PCM.
