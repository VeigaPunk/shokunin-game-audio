# R47 reviewer — two opt-in upper-centroid calibration modes

## Recommendation

The declared gap is the ordinary UI predicate’s absolute **upper** bound, not pairwise distinctness. `SPECS["ui"]` remains `(.12, 250, 4000, False)` and `measure()` retains `250 <= centroid <= 4000`. Minimal checker additions are two mutually exclusive opt-in modes, e.g. `--probe-ui-absolute-centroid-below-4000` and `--probe-ui-absolute-centroid-above-4000`, each generating only its own deterministic UI-shaped 5760-frame, 48 kHz mono PCM16 fixture in a round-47 scratch path and measuring it through the unchanged ordinary `measure(..., SPECS["ui"], path)` predicate. Below must return exit 0/no failures; above exit 1 with sole `spectrum: centroid outside fixture band`. Store ordinary receipts. Do not alter the comparator, `SPECS`, thresholds, canonical fixtures or ordinary run behavior; no generalized calibration machinery is needed. These names describe a minimal implementation recommendation, not modes I ran or verified as present.

## Measured fixture evidence

I independently measured the executor’s two original WAVs using the project `measure()` helper, which SoX-decodes to f32 and computes the whole-wave magnitude-rFFT weighted centroid. SHA values independently checked with `sha256sum`:

| Fixture | SHA-256 | Duration / decoded format | Centroid | Bandwidth | Peak FS | RMS dBFS | Result |
|---|---|---|---:|---:|---:|---:|---|
| `upper-below.wav` | `b04d00164fc57a97a0cdd591a589a44792d0084ba66cdc2118989183ae22fc17` | 0.12 s / 5760 samples, 48 kHz mono PCM16 | 3999.922795974407 Hz | 486.36936100091117 Hz | 0.279754638671875 | -18.327854015660773 | no failures |
| `upper-above.wav` | `8f6dd0411d240e46ea619c32e3c344b8c03491d860ebc6ab32b248cbd51e4383` | 0.12 s / 5760 samples, 48 kHz mono PCM16 | 4000.427101452783 Hz | 480.73591177279206 Hz | 0.2789306640625 | -18.32785200392649 | sole spectrum failure |

Both pass the format, duration and level checks (peak < .95; RMS exceeds .001 linear). The distinct hashes and measured centroids form a numerical gate-level bracket. Nominal sine frequencies are inputs, not the decoded centroids: executor reports nominal 3983/3984 Hz. The measurements here agree with that report. The independent simplifier candidates are much broader (centroids 3917.096806437624 / 4116.535402468537 Hz); they were decoded scratch controls, not checker-run receipts. The actual final narrow pair gives a tighter declared bracket.

## Error and command accounting

I ran no candidate generator, checker mode, test, or audition. No failed numeric fit was made by me. Executor reports initial nominal 3950/4050 and 3980/4020 candidates as broad but valid brackets, then final 3983/3984 as the narrow pair; none is a failed bracket fit. The simplifier’s independent 3900/4100 nominal pair also bracketed successfully. Do not confuse these with setup/report errors.

Exact commands I ran, with exit status:

```sh
python -c 'import sys; sys.path.insert(0, ".shokunin/audio/corpus/fixtures"); import measure_audio as m; print(m.measure("ui", m.SPECS["ui"], ".shokunin/audio/corpus/live/round-47/executor/upper-below.wav")); print(m.measure("ui", m.SPECS["ui"], ".shokunin/audio/corpus/live/round-47/executor/upper-above.wav"))'
# exit 1: setup/API error; passed str where helper expects Path (AttributeError), no numeric result.

python -c 'import sys; from pathlib import Path; sys.path.insert(0, ".shokunin/audio/corpus/fixtures"); import measure_audio as m; [print(m.measure("ui", m.SPECS["ui"], Path(f".shokunin/audio/corpus/live/round-47/executor/upper-{x}.wav"))) for x in ("below", "above")]'
# exit 1: setup/path error; relative WAV paths are outside helper ROOT for relative_to(), no numeric result.

python -c 'import sys; from pathlib import Path; sys.path.insert(0, ".shokunin/audio/corpus/fixtures"); import measure_audio as m; [print(m.measure("ui", m.SPECS["ui"], Path(f".shokunin/audio/corpus/live/round-47/executor/upper-{x}.wav").resolve())) for x in ("below", "above")]'
# exit 0: both actual project measurements printed above.

sha256sum .shokunin/audio/corpus/live/round-47/executor/upper-below.wav .shokunin/audio/corpus/live/round-47/executor/upper-above.wav
# exit 0: hashes printed above.
```

The executor lists its generation commands and then labels its second path a correction, but the original and correction text are identical. This is a redundant report note, not an observed path discrepancy; I did not run either generation command. No discrepancy found in the independently measured SHA/metrics.

## Limits

This supports only a numerical fixture calibration bracket against the existing gate. The two signals differ in nominal frequency, quantized samples and FFT distributions, so this is **not causal single-variable spectral isolation**. No exact 4000 Hz equality, timbre, quality, perception, universal-band, production, rights, engine, publishing, or promotion inference. No audition.
