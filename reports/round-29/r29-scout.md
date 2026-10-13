# r29-scout — absolute centroid delta and signedness vulnerability

## Comparator and mapping

In `corpus/fixtures/measure_audio.py`, `measure()` computes the whole-waveform magnitude-spectrum centroid: it decodes SoX float32 PCM, converts samples to float64, then uses `abs(rfft(samples))` and the positive-frequency `rfftfreq` grid (`measure_audio.py:45–58`; especially lines 55–58). This is a numeric measurement, not a perceptual metric.

For every measurement key ending `_alt`, the runner maps its baseline by removing the final four characters (`measure_audio.py:282–284`): `ui_alt` therefore maps to `ui`. It computes

```python
centroid_relative_delta = abs(variant_centroid - base_centroid) / base_centroid
passed = duration_delta >= .020 or centroid_relative_delta >= .10
```

(`measure_audio.py:282–288`; receipt threshold keys at lines 316–318). Absolute value makes the centroid arm insensitive to direction: higher and lower variant centroids can each satisfy it. A signed replacement `(variant_centroid - base_centroid) / base_centroid` would make every lower-centroid variant negative, so it could never meet the positive `>= .10` test, even when its magnitude is at least 10%. That would wrongly reject the intended lower-centroid above-cutoff case when duration delta is below `.020`. The OR is important: a duration delta at least `.020` passes regardless of centroid and cannot demonstrate this signedness behavior. This report makes no exact-cutoff equality claim.

The canonical `ui` spec is `(.12, 250, 4000, False)` (`measure_audio.py:14–18`), and the base waveform is generated at 5760 samples (`.12 * 48000`) from `.38*sin(2*pi*(700*t + 800*t*t))*exp(-30*t)` (`corpus/fixtures/build_artifacts.py:104–109`); the writer emits mono 48 kHz PCM16 (`build_artifacts.py:10–25`). Ordinary checks require 48 kHz mono PCM16, duration within ±1 ms, peak below `.95`, RMS at least `.001`, and centroid within the UI band (`measure_audio.py:36–42,72–79`). Round 29's declaration calls for the same 5760-frame UI spec for base and variants, with duration delta zero, to isolate centroid signedness.

## Baseline evidence

Inspected the existing normal-run receipt `corpus/live/runs/20261013T021100212192Z-normal/measurements.json` (round-28 baseline): `ui` duration `0.12 s`, 48 kHz mono `pcm_s16le` 16-bit, peak `0.375946044921875`, RMS `-19.991687666366516 dBFS`, centroid `966.8966593379727 Hz`, no failures. Its `ui_alt` maps to `ui`, has duration delta `0.04000000000000001 s`, relative centroid delta `0.47187731004956435`, and passes; because duration alone clears the duration arm, this is not evidence for a lower-centroid threshold case. This baseline receipt is context only, not a candidate fit.

## Setup and fit record

I ran no project commands, generators, or candidate fits; there are no failed candidate fits or setup failures from this scout. Source and receipt inspection only. No claims about smoothness, audibility/perception, rights, engine integration, publication, or promotion.
