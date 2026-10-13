# r25-critic — format-control isolation critique

## Scope and verdict

The round-25 declaration identifies a real confound: `wrong_format.wav` changes both sample rate (44100 vs 48000) and channel count (2 vs 1), while the native16 control is 48 kHz mono PCM16. The proposed 48 kHz stereo and 44.1 kHz mono cases are the right pair to separate those two metadata predicates. This would establish only that the current format check rejects each isolated metadata mismatch; it would not establish general format/decoder behavior.

**Caveat to the isolation claim:** a stereo control is not numerically identical to mono under this repository's acoustic-measurement path. `measure()` decodes SoX `f32` output into one flat scalar array, then uses `len(samples)` and the file sample rate for the FFT frequency bins. For interleaved stereo this counts two channel samples per frame, so the inferred FFT duration doubles and frequency interpretation depends on channel content/phase. A duplicated-channel 440 Hz signal would be represented as a 220 Hz sequence by that flattening convention (still within broad existing bands, but not identical); other channel relationships can produce different spectral artifacts. Thus metadata isolation is clean, but acoustic-statistic equivalence is not implied. Sample count and centroid must be reported/checked, not treated as proof the controls differ only acoustically in no way.

The current format predicate is evaluated independently from duration/level/centroid predicates, but `measure()` accumulates failures rather than short-circuiting. A control may therefore correctly show `format` while also failing a numeric check. If the round requires both controls to pass ordinary numeric conditions, candidate generation needs a measured fit; do not change bands/thresholds to force that result. Keep frame count/duration fixed in frames, generate a simple low-amplitude in-band sine, and document decoded scalar sample count as well as WAV frame count. Do not assert that the existing whole-wave `measure()` centroid for stereo has mono semantics.

## Evidence / exact commands

1. Inspected `.shokunin/audio/corpus/fixtures/measure_audio.py` and `build_artifacts.py`. The former decodes through `sox ... -t f32`, flattens with `np.frombuffer`, computes `rfftfreq(len(samples), 1/rate)`, and separately appends `format_failures(stream)`, duration, level, and centroid failures. Its format requirement is 48000 Hz, one channel, PCM16; expected failures are accumulated.
2. Metadata for the existing co-confounded control:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-6/wrong_format.wav
```
Exit **0**. Observed 44100 Hz, 2 channels, `pcm_s16le`, 16 bits, 4.000000 s.

3. Metadata for the existing positive format control:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-22/native16_probe.wav
```
Exit **0**. Observed 48000 Hz, 1 channel, `pcm_s16le`, 16 bits, 4.000000 s.

4. SoX decoded scalar byte counts:

```sh
for f in .shokunin/audio/corpus/live/round-22/native16_probe.wav .shokunin/audio/corpus/live/round-6/wrong_format.wav; do echo "$f"; sox "$f" -t f32 -e floating-point - 2>/dev/null | wc -c; echo "pipeline_exit=${PIPESTATUS[*]}"; done
```
Exit **0**. Pipelines both report `0 0`; native mono is 768000 bytes (=192000 float32 scalar samples), whereas the 4-second stereo control is 1411200 bytes (=352800 decoded scalar samples, 176400 frames × 2). The differing rates explain the frame-count difference; the channel factor demonstrates why decoded scalar count is not WAV frame count.

No candidate control was generated or fitted in this critic lane; no `round-25` data existed at inspection. Therefore no claim is made that either proposed control passes numeric checks or that its receipt has been produced. The declared executor/independent verification must establish that with actual artifacts and measurements. No thresholds, shared code, canonical assets, runner modes, or other reports were changed by this lane. No sound-quality, engine, rights, or publishing claim.
