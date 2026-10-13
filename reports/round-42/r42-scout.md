# Round 42 scout — peak headroom path

## Scope

Read-only inspection of the R42 declaration in `.shokunin/audio/LOG.md`, `corpus/fixtures/measure_audio.py`, `corpus/fixtures/build_artifacts.py`, and prior control reports. I did not edit shared source, run any shell command, generate/measure a WAV, or audition anything. This report is the only file written in this lane.

## Gate implementation and decoded-PCM path

`measure(name, spec, path=None)` first asks `ffprobe` for stream sample rate, channels, codec, bits/sample, and container duration. It then decodes samples through this exact invocation:

```python
command("sox", str(path), "-t", "f32", "-e", "floating-point", "-").stdout
```

The output bytes are interpreted as little-endian float32 and widened to float64:

```python
samples = np.frombuffer(pcm, dtype="<f4").astype(np.float64)
```

Peak is `float(np.max(np.abs(samples)))`; RMS is `float(np.sqrt(np.mean(samples**2)))`. The single combined level branch is `if peak >= .95 or rms < .001:`, appending exactly `level: clipping headroom or near silence`. Thus the peak comparator is inclusive on failure (`>= .95`), while RMS fails only below `.001`. The receipt records `peak_full_scale`, RMS dBFS, and both thresholds (`peak_max_exclusive: .95`, `rms_min_exclusive: .001`). Peak is computed on the decoded float samples, not by inspecting WAV bytes or relying on an encoder-side requested amplitude.

For PCM16, a decoded signed sample count `c` normally maps to `c/32768` in SoX's float decode. Therefore the declared adjacent values are `31129/32768 = 0.949981689453125` and `31130/32768 = 0.95001220703125`. They straddle `.95` because `.95*32768 = 31129.6`; neither is exact equality. A valid test must establish the actual post-write, post-decode absolute max, not infer it from a floating-point synthesis request. `build_artifacts.py`'s common `save()` quantizer currently uses `round(clip(samples,-1,1)*32767)` to little-endian int16, so a scratch source targeting a particular decoded integer must account for that scale/rounding and then verify the decoded counts.

The checker also independently computes whole-waveform magnitude-spectrum centroid, duration, and format. For the declared UI-shaped probe, spec is `.12 s`, centroid band 250–4000 Hz, non-looping; duration tolerance is ±1 ms, format must be 48 kHz mono PCM16, and RMS must exceed `.001`. To isolate peak behavior the intended 31129 case needs no failures and the 31130 case needs only the combined level failure; centroid/duration/format/RMS must pass for both. The proposed values alone do not demonstrate any of those measured outcomes.

## Existing controls and what they establish

The inspected historical independent round-5 control report records these commands and exits (quoted from `.shokunin/audio/reports/round-5/r5-controls.md`, not run by me):

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
```

Recorded exits: `0, 1, 1, 1, 0`. The report describes those receipts as normal restore, flat30 contrast failure, slope mismatch failure, and broken ambience centroid/endpoint failures, respectively. None is a peak-ceiling negative control: the broken ambience's peak was `.49932861` and RMS `-17.791 dBFS`; its failures were centroid and endpoint, not level. The normal ten-fixture peak range reported in round 5 was `.172363–.808777` FS, comfortably below `.95`; the report explicitly says no level negative control. Round 4's UI clone pair is another broad ordinary-check probe, not a peak boundary test. These establish broad passing/failing fixtures but not either side of the peak boundary.

`measure_audio.py` has prior UI probes for clone, duration, centroid, orientation, joint, and mixed-pass cases, but the source contains no peak-specific mode. Its existing `--probe-failing`, `--probe-slope`, `--probe-flat`, and other historic probes likewise do not deliberately bracket `.95`. The round-42 LOG declaration itself records the coverage gap: only broad controls existed for the peak comparator.

## Execution / calibration record

No shell commands were executed in this scout lane; consequently there are no scout command exit codes, generated WAVs, decoded count results, SHA-256s, numeric failed fits, or setup errors to report. In particular, this report does not verify the proposed 31129/31130 pair or claim that either is correctly constructed. If later experiments report a mismatch in the measured count, peak, or another gate, that is a numeric fixture-fit failure; missing tools, bad paths, malformed files, or unsuccessful invocation are setup/decode errors and should be recorded separately rather than relabeled as measured gate outcomes.

This is numerical fixture calibration only. The adjacent-count result, if later measured, would describe only the checker comparison on these decoded synthetic samples. It is not evidence about audition, sound quality, audible clipping, useful headroom, production, rights, engine behavior, publishing suitability, or promotion.
