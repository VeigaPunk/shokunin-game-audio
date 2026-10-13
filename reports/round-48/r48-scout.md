# R48 scout — exact integer rate predicate and SoX path

## Read-only source finding

`format_failures(stream)` in `.shokunin/audio/corpus/fixtures/measure_audio.py` checks `int(stream["sample_rate"]) != 48000 or int(stream["channels"]) != 1`; either mismatch appends exactly `format: expected 48kHz mono`. A separate check requires `codec_name == "pcm_s16le"` and `bits_per_sample == 16`. The check is exact integer equality, not a range/tolerance. `measure()` obtains stream metadata and container duration with ffprobe, then decodes the input via the project’s SoX call:

```python
command("sox", str(path), "-t", "f32", "-e", "floating-point", "-")
```

Those float32 decoded samples are promoted to float64 for whole-wave FFT centroid, RMS and peak calculations. Centroid bins use `1/rate`, where `rate` is the integer ffprobe sample rate. The UI fixture additionally requires duration `.12s ± .001s`, peak `< .95`, RMS `>= .001`, and centroid in `[250, 4000] Hz`.

Round 25’s existing `mono441_probe.wav` is mono PCM16 at 44100 Hz (ffprobe duration 4.0 s); it is a broad off-rate invalid fixture, not evidence about the adjacent 47999/48000 boundary. Under the UI spec it also fails duration, so it is not a sole-format comparison.

## Original adjacent-rate calibration fixture

Generated two original mono PCM16 WAVs with 5760 frames and byte-identical PCM payloads (11,520 bytes); only WAV sample-rate metadata differs. The source signal is a `.28` amplitude, 1000 Hz sine with Hann envelope generated on a 48 kHz time grid. Commands and exit status:

```sh
python .shokunin/audio/corpus/live/round-48/executor/generate.py .shokunin/audio/corpus/live/round-48/executor/r48-47999.wav 47999
# exit 0
python .shokunin/audio/corpus/live/round-48/executor/generate.py .shokunin/audio/corpus/live/round-48/executor/r48-48000.wav 48000
# exit 0
```

SHA-256 pins:

- 47999 Hz: `71551e200633e62b1b9db4ee5a582f8d4d996cd693f2e4a040a96023b130a210`
- 48000 Hz: `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c`

Actual ffprobe command (each file) and exit status:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json FILE
# exit 0 for each
```

| WAV | ffprobe rate | channels | codec | bits/sample | duration |
|---|---:|---:|---|---:|---:|
| `r48-47999.wav` | 47999 | 1 | pcm_s16le | 16 | 0.120003 s |
| `r48-48000.wav` | 48000 | 1 | pcm_s16le | 16 | 0.120000 s |

Both actual durations are within the UI ±1 ms limit. Project metric path was exercised by importing `measure_audio.measure("ui", SPECS["ui"], absolute_path)` for each WAV; command exited 0 and returned:

| WAV | SoX-decoded peak | RMS dBFS | centroid Hz | bandwidth Hz | UI failures |
|---|---:|---:|---:|---:|---|
| 47999 Hz | 0.27996826171875 | -18.327858226717105 | 1022.5148421151724 | 586.904753883307 | `format: expected 48kHz mono` only |
| 48000 Hz | 0.27996826171875 | -18.327858226717105 | 1022.536144951523 | 586.9169813204176 | none |

Both decoded signals satisfy UI level and centroid limits. The observed distinction is exactly the integer sample-rate format predicate in this fixture pair. Metrics are the project’s SoX-f32-decoded measurements; no listening/audition was performed.

## Setup note and limits

An exploratory direct command `sox "$f" -t f32 -e floating-point - -n stats` returned exit 1 for both files: this SoX build warned raw stdin’s rate was unspecified (defaulted to 8 kHz) and then reported “input files must have the same sample-rate.” That is a malformed direct stats invocation, not a fixture numeric failure. The project’s actual SoX decode command above succeeded for both; no candidate numeric-fit search was performed. No converter/resampling behavior is inferred. This result is only a numerical calibration of this predicate and these fixtures; it says nothing about audio quality, perception, production, rights, engine behavior, or publishing/promotion.
