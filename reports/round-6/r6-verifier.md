# Round 6 independent verifier replay

## Scope

Non-author replay of the integrated round-6 invalid-input probe and the existing normal/control modes, from the repository root, using the installed Python/FFmpeg/SoX toolchain. I read the round-6 LOG entry, integrated `build_artifacts.py` and `measure_audio.py`, round-6 wave-1 scoped reports, and the fixture-battery extension. This verifies only the named generated probes and fixtures; it is not a security review, an exhaustive malformed-file test, or production validation.

## Exact replay

Commands were run serially and in this order. Exit status **1** is the expected result for each negative-control probe.

| Command | Exit | Receipt | Observed outcome |
|---|---:|---|---|
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261012T170607093097Z-invalid/measurements.json` | Three entries all `status: expected_failure`; short=`section count`, corrupt=`decode`, wrong-format=`format`. No traceback. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T170607675436Z-normal/measurements.json` | Ten measurements, no failures; four variant distinctness checks pass. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T170608325807Z-flat/measurements.json` | Only `flat30_probe` fails the section-contrast check, as intended. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T170608960610Z-slope/measurements.json` | `slope_probe` fails slope mismatch, as intended. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261012T170609548702Z-failing/measurements.json` | Broken ambience fails centroid and endpoint checks, as intended. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T170610141133Z-normal/measurements.json` | Clean restoration: ten measurements and no failures. |

No command output contained `Traceback`.

Invalid receipt details: `short_sections` decoded to **144000** samples against **192000** required, and returned the section-count category before splitting/FFT; `corrupt` was classified `decode` from ffprobe nonzero exit **1**; `wrong_format` reported **44100 Hz, 2 channels** and classified `format`. Each status is `expected_failure`.

## Hashes and guard checks

All ten canonical files in `.shokunin/audio/corpus/artifacts/` were SHA-256 hashed and compared byte-for-byte by hash with `git show 3b02c31:.shokunin/audio/corpus/artifacts/<name>`; **10/10 match**. The three generated round-6 scratch hashes also match the executor reports:

- `short_sections.wav`: `61786e40b1eeca4557bb5b02b9ba4ab65231b46f50ae76702f1b1bdb9a1f3795`
- `corrupt.wav`: `564867d8781dc7f4f43e66543e9db6631f464c90087e3cf87a04040f2e83217c`
- `wrong_format.wav`: `a753c610ccfdc26729e4694f52a34a4bc4b0a116731fe52f6bc6a133fa190712`

The clean receipt contains ten measurements, all with empty failure lists. `ui_alt`, `impact_alt`, `movement_alt`, and `ambience_alt` all have `passed: true` distinctness entries. Comparison of integrated source against `3b02c31` shows the round adds invalid-probe construction/dispatch, an exact section-count guard before FFT, and invalid receipt handling; it does not change existing threshold literals or normal/control check logic. Existing flat/slope/broken-amplitude control outcomes are preserved above.

## Conclusion

The bounded round-6 replay claim passes: under this installed toolchain the three named scratch inputs produce a timestamped structured JSON receipt with the expected categories and nonzero probe exit; clean fixture hashes, normal measurements, variant distinctness, and prior control behavior remain intact. Corrupt classification is narrow: the implementation maps a `subprocess.CalledProcessError` from ffprobe for this named corrupt probe to `decode`; it does not establish behavior for arbitrary malformed files, missing executables, security, or production use.
