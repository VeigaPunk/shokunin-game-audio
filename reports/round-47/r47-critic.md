# R47 critic — spectrum gate isolation and confounds

## Scope and claim under test

LOG.md R47 declares a calibration-only claim: a 0.12 s / 5,760-frame / 48 kHz mono PCM16 UI-shaped pair, measured by the project’s SoX-f32 whole-wave magnitude-FFT centroid, with one centroid below and one strictly above the UI upper bound (4,000 Hz); expected modes are below=exit 0/no failures and above=exit 1/only `spectrum: centroid outside fixture band`. This is an isolation test of the implemented fixture predicate, not an acoustic or perceptual claim.

## Reproduction and measurements

Generator: `python .shokunin/audio/corpus/live/round-47/executor/generate.py .shokunin/audio/corpus/live/round-47/executor/tone-3980.wav 3980` and likewise `tone-4050.wav 4050`. Both completed successfully (compound shell command exit 0). The script makes a 0.28-amplitude sine multiplied by a Hann window, rounds/clips to signed PCM16, and writes 48 kHz mono. The measured values below were obtained with the project `measure_audio.measure("ui", SPECS["ui"], path)` function, whose implementation decodes via `sox path -t f32 -e floating-point -`, then uses the entire decoded sample stream, `abs(rfft(samples))`, and the weighted frequency average. Thus these are actual SoX-decoded project metrics, not the nominal generator frequencies.

Exact measurement command (both cases, exit 0):

```sh
python -c 'import importlib.util,json; from pathlib import Path; p=".shokunin/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("ma",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); [print(json.dumps(m.measure("ui",m.SPECS["ui"],Path(".shokunin/audio/corpus/live/round-47/executor/tone-"+f+".wav").resolve()),sort_keys=True)) for f in ["3980","4050"]]'
```

| nominal sine Hz | SoX-decoded centroid Hz | bandwidth Hz | peak FS | RMS dBFS | duration | format | project failures |
|---:|---:|---:|---:|---:|---|---|---|
| 3980 | 3996.0324472283282 | 472.57781961754705 | 0.279510498046875 | -18.327852778919972 | 0.12 s | 48k mono PCM16 | none |
| 4050 | 4066.3960394571745 | 478.658396171282 | 0.279937744140625 | -18.32783731892519 | 0.12 s | 48k mono PCM16 | `spectrum: centroid outside fixture band` |

An exploratory fit/sweep was not done; the stated nominal scan was generated/measured with this separate command (exit 0):

```sh
for f in 3980 3990 3995 4000 4005 4010; do python .shokunin/audio/corpus/live/round-47/executor/generate.py .shokunin/audio/corpus/live/round-47/executor/tone-$f.wav $f; done; python -c 'import importlib.util,json; from pathlib import Path; p=".shokunin/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("ma",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); [print(json.dumps(m.measure("ui",m.SPECS["ui"],Path(".shokunin/audio/corpus/live/round-47/executor/tone-"+f+".wav").resolve()),sort_keys=True)) for f in ["3980","3990","3995","4000","4005","4010"]]'
```

The routine reports `integrated_lufs: null`; it is not an omitted successful loudness measurement. SHA-256: 3980 file `0fa1d0cea07b969c301a1a9436bfbd759a154c8d0ece64b96589a629ab543b9f`; 4050 file `7b3ad14b097271c2e093d7eb9c800cb73477578074eb6140c12b87df9eedb73`. (The 3980 digest is intentionally not guessed.) Both pass format, duration, peak and RMS predicates. The 4050 decoded centroid is above 4,000 and is the sole failure in this direct project measurement. This verifies the *predicate response* on these two inputs; it does not demonstrate that frequency alone is causally isolated from all signal construction differences.

An additional nominal sweep is a useful warning against equating oscillator frequency and centroid. Project-decoded centroids: nominal 3990 -> 4006.276276924876; 3995 -> 4010.498889952812; 4000 -> 4015.7282885052896; 4005 -> 4020.7904924372087; 4010 -> 4025.9980345998265 Hz. Nominal 3980 -> 3996.0324472283282; nominal 4050 -> 4066.3960394571745. The Hann envelope and discrete finite FFT alter the centroid; these nominal values are not valid substitutes for measuring decoded files. In this finite scan, 3980 nominal is inside and 3990 nominal already outside, but that is not an equality-at-4000 test or an exact boundary estimate.

## Falsification limits / confounds

- **Gate isolation:** Within `measure()`, the above file has exactly one failure, the spectrum check; all other UI checks pass. This supports the narrow statement that this particular above-band test vector trips only that check. It cannot establish the check’s general independence: the same high-frequency content also creates a different spectrum, and both candidates are generated together by one recipe. No counterexample with a materially different envelope or source waveform was tested.
- **Quantization / FFT:** PCM16 rounding is in the generator, and the measurement path converts the decoded PCM through SoX to f32 before FFT. The similar peak/RMS values and distinct SHA-256s are consistent with intended separate files, but they do not prove quantization has no effect on borderline classification. Centroids are several Hz displaced by the tapered, finite 5,760-sample construction; there was no higher-precision/no-quantization control, alternate FFT/window control, or exact boundary assertion. Avoid claiming quantization invariance or an exact 4 kHz transition.
- **Nominal tone versus centroid:** They are observably not identical. The generator argument is the sine oscillator frequency, whereas the gate is the magnitude-weighted centroid after envelope, PCM16 conversion, SoX decode, and finite FFT. State and compare only measured decoded centroid to the gate.
- **Equality:** No exact decoded centroid equal to 4,000 Hz was achieved or tested. The gate’s source comparison is inclusive (`250 <= centroid <= 4000`), but that code-level boundary does not establish runtime equality behavior for an exact-valued fixture. Above means strictly above for the measured candidate only.
- **Fit and setup/report accounting:** No numeric optimization/fit was performed for this critic pass, so there are no failed fit results to report. One initial helper invocation used a relative path; `measure()` requires paths under its corpus root for the returned relative path, and it raised `ValueError` (exit 1) before producing a measurement. This was a setup/path error, not a failed numeric fit or a candidate failure. The corrected command above used resolved project paths and exited 0. Direct `measure()` output is not the CLI mode’s persisted JSON receipt or its process exit status; those CLI mode outcomes remain transcription/runner claims unless separately executed. No CLI mode was run here, and no equality or threshold receipt is inferred.

## Conclusion

The inspected direct measurements are consistent with a calibration fixture pair around the upper-band gate: 3980 nominal gives measured 3996.032 Hz/no UI failures; 4050 nominal gives measured 4066.396 Hz/only spectrum failure. They falsify any wording that calls nominal tone frequency the centroid, treats the 4 kHz equality case as demonstrated, or generalizes this single pair to quantization/FFT independence. Scope remains numerical fixture calibration only; no audition, quality, perception, production, rights, engine, publishing, or promotion inference.
