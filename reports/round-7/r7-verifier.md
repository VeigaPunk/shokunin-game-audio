# Round 7 independent replay — odd section-count regression

Verifier: non-author replay lane. Scope: directly exercise the declared old exception, current invalid-input receipt, normal fixture/variant coverage, previous three invalid probes, and the round-6 negative modes. No perceptual, security, codec, or production claim.

## Before-state exception

Ran the isolated `section_contrast` function extracted from Git `3b02c31` with NumPy and its command helper in an ephemeral namespace against `corpus/live/round-7/odd_sections.wav`:

```sh
python3 -c 'import ast, subprocess, numpy as np; source=subprocess.check_output(["git","show","3b02c31:.shokunin/audio/corpus/fixtures/measure_audio.py"], text=True); tree=ast.parse(source); node=next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name=="section_contrast"); ns={"np": np, "command": lambda *args: subprocess.run(args, check=True, capture_output=True)}; exec(compile(ast.Module(body=[node], type_ignores=[]), "3b02c31:.shokunin/audio/corpus/fixtures/measure_audio.py", "exec"), ns); print(ns["section_contrast"](".shokunin/audio/corpus/live/round-7/odd_sections.wav"))'
```

Exit **1**, traceback ends `ValueError: array split does not result in an equal division` from old `np.split(samples, 2)`, line 85. The odd WAV is mono PCM16/48 kHz, 101 frames, SHA-256 `81c7ba97bfc8f68a9ad48403a6b102bf4d5f573963f5d8f74a9697bd09aa72d8`. This confirms the prior function exception on the directly supplied input; it is not a claim that the old public CLI processed arbitrary unlisted files.

## Current invalid-input receipt

`python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` exited **1** and wrote `corpus/live/runs/20261012T171718939143Z-invalid/measurements.json`. The receipt lists four `expected_failure` entries: `short_sections` 144000/192000 `section count`; `corrupt` `decode` (ffprobe exit 1); `wrong_format` 44100 Hz/stereo `format`; and `odd_sections` 101/192000 `section count`. Odd probe includes a structured section result, `failure_kind: section count`; no traceback. All four were observed as expected. Its exit 1 is the intentional negative-control outcome, not a harness failure.

## Normal and preserved controls

The first malformed batch attempted these five intended commands, each wrapped by the REPL as `bash(f'"""{c}"""')`; due to the wrapper/quoting mistake, each failed with exit **127** before Python ran. The shell attempted to find the whole command as one executable (for example `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat`):

```text
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
```

A second malformed batch used the same wrapper and failed the four control/restore commands (also exit 127):

```text
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
```

Thus there were **9 setup failures, all exit 127**, in two batches; none is counted as a pass. Each emitted `/usr/bin/bash: line 4: <entire command>: No such file or directory`, confirming that the full command text was parsed as the executable name. Corrected commands were issued with the executable and arguments separated:

| Exact command | Exit | Receipt and observed outcome |
|---|---:|---|
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T171605486878Z-normal/measurements.json`; 10 measurements, no failures; all four distinctness checks pass. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `corpus/live/runs/20261012T171613915489Z-flat/measurements.json`; `flat30_probe` rejected for section contrast. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `corpus/live/runs/20261012T171614543341Z-slope/measurements.json`; `slope_probe` rejected for slope mismatch. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `corpus/live/runs/20261012T171615125782Z-failing/measurements.json`; `ambience` rejected for centroid and endpoint. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T171615709159Z-normal/measurements.json`; clean restoration, no failures. |

Each corrected command used `python3 .shokunin/audio/corpus/fixtures/measure_audio.py ...` as a real command. The independent normal receipt has ten fixtures and passing UI/impact/movement/ambience alternative distinctness checks. It confirms current coverage under the existing fixture battery, not sonic quality.

## Canonical hashes and source scope

Computed SHA-256 for each current `.shokunin/audio/corpus/artifacts/*.wav` and compared with `git show cba2748:<path>` bytes: all ten are byte-identical. Names: ambience, ambience_alt, impact, impact_alt, movement, movement_alt, stem, stem_sections, ui, ui_alt. For each filename, I independently computed `hashlib.sha256(Path(".shokunin/audio/corpus/artifacts/<name>.wav").read_bytes()).hexdigest()` and compared it with `hashlib.sha256(subprocess.check_output(["git", "show", "cba2748:.shokunin/audio/corpus/artifacts/<name>.wav"])).hexdigest()`; all ten comparisons returned true. Full digests are in `r7-guard.md`. The integrated diff only adds deterministic generation of the 101-frame scratch input and its named entry in the invalid-probe list/path selection. A line-level comparison of `measure_audio.py` against `git show cba2748:.shokunin/audio/corpus/fixtures/measure_audio.py` confirms the enforcement values and branches for duration `.001`, peak `.95`, RMS `.001`, endpoint `.03`, slope `.001`, exact `192000` section count, section amplitude `.01`, RMS `.001`, and contrast `6.0 dB` are unchanged. No threshold or canonical WAV was changed. Existing invalid records retain their expected categories.

## Bounded conclusion

The old isolated function raises on the precisely constructed 101-frame input; the current opt-in invalid mode records that input as a structured `section count` expected failure and preserves the three previous named invalid results. Normal run, prior flat/slope/failing controls, restoration, ten canonical hashes, and four variant-distinctness checks remain as recorded above. This supports only the declared odd-length section-count receipt improvement. It does not establish behavior for arbitrary malformed WAVs or direct old CLI acceptance of this scratch. No shared fixture logic beyond the named probe was tested.
