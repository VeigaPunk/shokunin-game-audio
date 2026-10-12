# Round 7 scout — static section-count path map

## Scope

Static source comparison only. No WAV was generated, decoded, or listened to; no runtime claim is made. No source, LOG, SCORECARD, artifact, or commit was edited.

## Before-state at `3b02c31`

In `.shokunin/audio/corpus/fixtures/measure_audio.py`, `section_contrast(path)` begins at line 82. It executes SoX and converts stdout to a NumPy float64 array (lines 83–84), then immediately calls `np.split(samples, 2)` at line 85. For an odd sample count such as 101, NumPy cannot split the array into two equal sections and raises `ValueError` there; the code has not reached the later exact-length validation, which is embedded in `valid = len(samples) == 192000 ...` at line 88. FFT-bin indexing follows at line 86, but is not reached if split raises. Thus the old path has an exception before its count-based `valid` result for odd counts. This is source-based control-flow inference, not a run on an odd WAV.

## Current source

Current `.shokunin/audio/corpus/fixtures/measure_audio.py` lines 82–89 run SoX/read samples first, then test `len(samples) != 192000` and return a result with `valid: False`, `passed: False`, `actual_samples`, and `failure_kind: "section count"`. Only the exact-length case proceeds to `np.split` at line 90 and FFT indexing at line 91. A 101-frame input therefore follows the count-return branch before split, by static inspection.

The current invalid-probe driver at lines 100–105 still enumerates only `short_sections`, `corrupt`, and `wrong_format`; it has no `odd_sections` entry in this source. Therefore the source shows the reusable precheck but does not itself establish that the new round-7 odd input is wired into, or exercised by, `--probe-invalid`.

## Commands and exits

- `git show 3b02c31:.shokunin/audio/corpus/fixtures/measure_audio.py | nl -ba | sed -n '65,115p'` — exit 0. Used to inspect the before-state line numbers and function body.
- Current source was read statically from the working tree with Python; no shell command or test was run for it.
