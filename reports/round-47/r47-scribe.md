# R47 scribe — absolute upper centroid bracket decision table

## Decision boundary and pending integration

The LOG declares a missing **absolute upper** UI centroid bracket for the existing inclusive predicate `250 <= decoded whole-wave magnitude-FFT centroid <= 4000 Hz`. This is not the `_alt` pairwise distinctness predicate (which compares each variant with its baseline using `duration_delta >= .020 s OR relative_centroid_delta >= .10`). The two R47 opt-in source-generated runner modes and final replay are **pending integration**; this report measures worker scratch WAVs through the current project `measure()` implementation and applies the declared absolute predicate to those measured values. It does not claim that a new R47 runner flag or integrated receipt exists yet.

| Scratch candidate | Nominal generator sine frequency | Project SoX-f32 decoded whole-wave centroid | Project metrics (duration; format; peak; RMS; bandwidth) | Absolute UI band classification | Fit/result |
|---|---:|---:|---|---|---|
| `executor/tone-3950.wav` | 3950 Hz | 3967.091051928427 Hz | .12 s; 48 kHz mono PCM16; peak .279937744140625 FS; RMS −18.32784493868716 dBFS; bandwidth 487.2151877057162 Hz | in-band | Not a tight bracket endpoint |
| `executor/tone-4050.wav` | 4050 Hz | 4066.3960394571745 Hz | .12 s; 48 kHz mono PCM16; peak .279937744140625 FS; RMS −18.32783731892519 dBFS; bandwidth 478.658396171282 Hz | above band | Not a tight bracket endpoint |
| `executor/tone-3980.wav` | 3980 Hz | 3996.0324472283282 Hz | .12 s; 48 kHz mono PCM16; peak .279510498046875 FS; RMS −18.327852778919972 dBFS; bandwidth 472.57781961754705 Hz | in-band | Trial below endpoint |
| `executor/tone-4020.wav` | 4020 Hz | 4035.675153533777 Hz | .12 s; 48 kHz mono PCM16; peak .279510498046875 FS; RMS −18.327840390030335 dBFS; bandwidth 469.6379137369862 Hz | above band | Trial above endpoint |
| `executor/tone-3983.wav` / `upper-below.wav` | 3983 Hz | **3999.922795974407 Hz** | **.12 s; 48 kHz mono PCM16; peak .279754638671875 FS; RMS −18.327854015660773 dBFS; bandwidth 486.36936100091117 Hz** | **in band; expected ordinary-gate pass** | Final below endpoint |
| `executor/tone-3984.wav` / `upper-above.wav` | 3984 Hz | **4000.427101452783 Hz** | **.12 s; 48 kHz mono PCM16; peak .2789306640625 FS; RMS −18.32785200392649 dBFS; bandwidth 480.73591177279206 Hz** | **above band; expected sole spectrum failure** | Final above endpoint |

Final endpoints have distinct SHA-256: below `b04d00164fc57a97a0cdd591a589a44792d0084ba66cdc2118989183ae22fc17` and above `8f6dd0411d240e46ea619c32e3c344b8c03491d860ebc6ab32b248cbd51e4383`. They are each 5760 frames, 48 kHz, mono, PCM16. Both are .12 seconds, with peak < .95 and RMS > .001. The displayed centroid is the project's SoX-f32-decoded, whole-wave magnitude-weighted FFT centroid, not nominal carrier frequency. The boundary values are strictly below/above 4000; no equality fixture is claimed.

### Metrics and receipt caveat

Full final endpoint `measure()` output gave below peak `.279754638671875`, RMS `-18.327854015660773dBFS`, bandwidth `486.36936100091117Hz`, no failures; above peak `.2789306640625`, RMS `-18.32785200392649dBFS`, bandwidth `480.73591177279206Hz`, with `spectrum: centroid outside fixture band`. “Expected ordinary-gate pass/fail” above is the measured scratch result evaluated by the unchanged predicate, **not** a runner receipt for the not-yet-integrated R47 modes. No claims about timbre or audible difference follow.

The 3950/4050 and 3980/4020 pairs both numerically classify on opposite sides, but their decoded gaps from the boundary are broader than the final 3983/3984 nominal pair. They are trial candidates, not failed fits: no attempted numeric fit failed to straddle the gate. The decisive decoded samples came from 3983 and 3984 nominal generator tones. Nominal frequency is not the measured centroid. The final pair changes waveform frequency and its quantized samples/spectral distribution, so this is a **gate-level bracket**, not causal single-variable spectral isolation.

## Commands, setup and errors

Scratch generator source is `corpus/live/round-47/executor/generate.py`: `.28 * sin(2π f t) * Hann(5760)`, quantized to PCM16 at 48 kHz. The exact project-measure command for the final pair was:

```sh
python3 -c 'import runpy; m=runpy.run_path(".shokunin/audio/corpus/fixtures/measure_audio.py"); from pathlib import Path; d=Path(".shokunin/audio/corpus/live/round-47/executor").resolve(); [print(n, m["measure"]("ui", m["SPECS"]["ui"], d/n)) for n in ("upper-below.wav", "upper-above.wav")]'
```

Exit **0**. It reported the final metrics above and `failures: []` below, `failures: ['spectrum: centroid outside fixture band']` above. This direct measurement does not launch the integrated runner.

One attempt used a relative, rather than resolved absolute, scratch path with the same project helper. Exact command:

```sh
python3 -c 'import runpy; m=runpy.run_path(".shokunin/audio/corpus/fixtures/measure_audio.py"); from pathlib import Path; d=Path(".shokunin/audio/corpus/live/round-47/executor"); [print(n, m["measure"]("ui", m["SPECS"]["ui"], d/n)) for n in ("upper-below.wav", "upper-above.wav")]'
```

Exit **1**, setup/path error: helper's `path.relative_to(ROOT)` raised `ValueError` because the relative path was not beneath its absolute `ROOT`. This was corrected by `.resolve()` in the successful command. It is not a failed numerical fit or a gate result.

I also ran the two *currently existing* R46 runner options, not R47 options:

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-below
```

Exit **1**, produced `corpus/live/runs/20261013T070831844185Z-ui-absolute-centroid-below/measurements.json`; it measured old `live/round-46/centroid-below.wav` at **249.71389590882862 Hz**, peak `.279754638671875`, RMS `-18.327838866709165 dBFS`, bandwidth `625.8273248256264 Hz`, sole spectrum failure.

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-above
```

Exit **0**, produced `corpus/live/runs/20261013T070844771672Z-ui-absolute-centroid-above/measurements.json`; it measured old `live/round-46/centroid-above.wav` at **250.3250670185918 Hz**, peak `.27984619140625`, RMS `-18.32783946042307 dBFS`, bandwidth `625.8448652317335 Hz`, no failures. These are valid old lower-bound receipts, **not evidence for the R47 upper-bound pair**.

Final SHA-256 values are below `b04d00164fc57a97a0cdd591a589a44792d0084ba66cdc2118989183ae22fc17` and above `8f6dd0411d240e46ea619c32e3c344b8c03491d860ebc6ab32b248cbd51e4383`. No transcription correction was required; no auditory assessment was made.

## Scope

This is numerical fixture calibration only. No audition, quality, perception, production, rights, engine, publishing or promotion inference; no universal-band claim. Pending work is R47 CLI integration, opt-in receipts, preservation/replay verification, and adjudication. The R47 integrated gates have not been run by this scribe.
