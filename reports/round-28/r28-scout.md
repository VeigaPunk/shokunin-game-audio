# r28-scout — centroid comparator, UI base, and numerical path

## Existing comparison

The exact `_alt` lookup is in `corpus/fixtures/measure_audio.py:272–282`: for each measurement name ending `_alt`, the runner chooses the base as `measurements[name[:-4]]`. It computes

```text
duration_delta = abs(variant.duration_s - base.duration_s)
centroid_relative_delta = abs(variant.spectral_centroid_hz - base.spectral_centroid_hz) / base.spectral_centroid_hz
passed = duration_delta >= 0.020 or centroid_relative_delta >= 0.10
```

If both arms are below threshold, it appends `distinctness: duration < .020 s and centroid delta < 10%`. The centroid arm is **relative to the baseline centroid**, not absolute Hz and not symmetric normalization. Equality at `.10` passes due to `>=`; the OR means duration must remain below `.020` to isolate the centroid arm.

`ui_alt` is the existing production fixture alt and maps to `ui`; both are measured from `SPECS` at `measure_audio.py:14–29`. The base UI spec is `(.12, 250, 4000, False)`: 120 ms, centroid allowed from 250 through 4000 Hz, non-looping. `build_artifacts.py:110–114` synthesizes the canonical UI base as `.38 * sin(2π(700t + 800t²)) * exp(-30t)` for `t = arange(round(.12*48000))/48000`; `save()` writes clipped, rounded PCM16 mono at 48 kHz (`build_artifacts.py:10–25`). This source waveform gives a fixed reference for any candidate, but changing it would change the canonical artifact and is outside this scout task. Existing `ui_alt` is a distinct .16 s chirp, not a near-centroid transition candidate.

## Centroid calculation and float/FFT sensitivity

`measure()` (`measure_audio.py:45–58`) gets sample rate and duration from `ffprobe`; decodes samples via `sox PATH -t f32 -e floating-point -`; interprets little-endian float32 and casts to float64. On the *entire* decoded frame sequence it computes `spectrum = abs(np.fft.rfft(samples))`, `freqs = np.fft.rfftfreq(N, 1/rate)`, and `centroid = dot(freqs, spectrum) / spectrum.sum()`. Thus this is an unwindowed magnitude-spectrum weighted mean of nonnegative FFT-bin frequencies, not a power-spectrum centroid. It is a numeric proxy only. The `1/N` scaling common to both FFT numerator and denominator cancels; relative delta then divides the absolute centroid difference by the baseline value.

For equal-duration files, same rate, and same frame count, both use the same FFT bin grid. Quantization is applied upstream by `save()` via rounding to int16; SoX outputs float32, then the analysis is float64. Small analytic parameter changes can be erased or altered by PCM16 rounding and float32 decoding; FFT magnitudes can also respond nonlinearly to phase/envelope/interference. A candidate that changes only a short tail or endpoint can shift the whole-file FFT distribution, so the centroid delta does not by itself isolate a simple frequency parameter. If sample counts differ, bin spacing `rate/N` differs; here declared round28 setup requires both 5760 samples, so that particular resolution confound should not arise. No windowing, detrending, or amplitude threshold is applied before the FFT. Any near-.10 result must therefore be measured on the saved/read-back WAVs, not inferred from source float arrays or nominal parameter values. Duration comparator also uses `float(ffprobe format.duration)` (`measure_audio.py:47–53`), so zero means equal reported durations, not a separate exact sample-count guarantee.

Ordinary `measure()` gates remain independent: 48 kHz mono PCM16 (`:36–42`), duration within ±1 ms of the supplied spec (`:72–79`), peak `< .95` and RMS `>= .001`, centroid in the supplied UI band. Use the canonical base spec for the baseline and an otherwise-identical per-file duration spec if necessary; do not mistake an ordinary gate failure for a distinctness outcome. In this round both candidates are required to pass ordinary checks and duration delta must be 0 for the centroid threshold polarity claim.

## Existing baseline receipt and exact diagnostic

Latest available normal receipt inspected: `corpus/live/runs/20261013T021100212192Z-normal/measurements.json`. It reports UI duration `0.12 s`, rate 48000, mono `pcm_s16le` 16-bit, peak `0.375946044921875`, RMS `-19.991687666366516 dBFS`, centroid `966.8966593379727 Hz`, and no failures. Its five pre-existing `_alt` comparisons all pass; it is context only, not evidence for the proposed near-threshold pair.

Command run from repository root:

```sh
ffprobe -v error -show_entries 'stream=sample_rate,channels,codec_name,bits_per_sample:format=duration' -of json .shokunin/audio/corpus/artifacts/ui.wav
```

Exit **0**. Output: 48000 Hz, one channel, `pcm_s16le`, 16 bits, duration `0.120000`.

## Fit status and scope

No generator sweep, candidate measurement, or fit was run by this scout; therefore there are no failed fits or candidate commands/exits to report. I read the declared round-28 LOG claim and inspected source/receipt only. I make no claim that a near-.10 pair exists or that centroid difference corresponds to audible/perceptual difference. No rights, engine, publishing, or promotion claims.
