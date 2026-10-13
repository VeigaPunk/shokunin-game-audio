# R46 scout — ordinary absolute UI centroid band vs R29 distinctness

## Declaration and distinction

The ordinary UI measurement is an **absolute** range check: `measure("ui", SPECS["ui"], ...)` uses the UI spec `(.12, 250, 4000, False)` and appends `spectrum: centroid outside fixture band` unless `250 <= spectral_centroid_hz <= 4000`. This is performed per waveform alongside format (48 kHz mono PCM16), duration (within ±.001 s), and level (peak `< .95`, RMS `>= .001`) checks. The band endpoints are inclusive in the Python condition.

Round 29 addressed a different predicate: **pairwise distinctness** for a variant compared with its `ui` baseline. It computes `abs(variant_centroid - base_centroid) / base_centroid` and accepts that arm at `>= .10` (OR duration delta `>= .020 s`). Its candidates remained within the ordinary 250–4000 Hz band; R29's below/above labels mean below/above the *relative .10 delta cutoff*, not below/above the ordinary 250 Hz absolute lower band. The predicates answer different questions: whether one measured centroid is in a fixed range vs whether two centroids differ enough relative to baseline. Neither is a perception measure.

## Measurement path and existing actual project evidence

`corpus/fixtures/measure_audio.py::measure` obtains decoded samples with the project command `sox <wav> -t f32 -e floating-point -`, reads little-endian float32, converts to float64, then computes `abs(np.fft.rfft(samples))` over the **whole waveform**, with `np.fft.rfftfreq(len(samples), 1/rate)`. The centroid is `dot(freqs, magnitude) / magnitude.sum()`: a positive-frequency magnitude-weighted FFT centroid, not a power-weighted centroid and not a perceptual/timbre judgment. Duration/format come from ffprobe; peak and RMS are computed from the same decoded SoX samples.

I inspected the existing direct project measurement receipt `corpus/live/round-29/executor/direct_project_measure.json`; I ran no shell commands and generated no data. It records `measure()` output for the original 5760-frame candidates using UI spec `(.12,250,4000,False)`:

| Candidate | Duration | Format | Peak FS | RMS dBFS | Whole-wave centroid | Band result | Other ordinary failures |
|---|---:|---|---:|---:|---:|---|---|
| baseline | 0.120 s | 48 kHz mono PCM16 | 0.375946044921875 | -19.991687666366516 | 966.8966593379727 Hz | within | none |
| `k_0.95.wav` | 0.120 s | 48 kHz mono PCM16 | 0.375732421875 | -19.991709185457857 | 871.155504521436 Hz | within | none |
| `k_0.94.wav` | 0.120 s | 48 kHz mono PCM16 | 0.37567138671875 | -19.991703358630403 | 862.0264574403602 Hz | within | none |

The same receipt records R29 relative deltas `.09901901500217196` and `.1084606104331939` against the baseline, with duration deltas `0.0 s`. Thus the `.10` pairwise distinction does not imply a lower-band violation: all three absolute centroids are hundreds of hertz above 250 Hz, and all pass the ordinary absolute band. R29 does not supply the requested <250 / >250 absolute-band bracket. It also does not demonstrate an exact 250 Hz boundary result.

## Scope and command record

This is source/receipt mapping only. **No shell commands were run**, no candidate fitting was attempted, and no setup or numeric-fit failures occurred in this scout. No files other than this assigned report were written. No audition or inference about quality, perception, timbre, novelty, production, rights, engine behavior, publishing, or promotion is made.
