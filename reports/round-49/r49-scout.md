# R49 scout — exact rate predicate and R48 lower-side reference

## Predicate and metadata path

Read-only inspection of `.shokunin/audio/corpus/fixtures/measure_audio.py` shows `format_failures(stream)` uses exact integer equality for rate and channel count:

```python
if int(stream["sample_rate"]) != 48000 or int(stream["channels"]) != 1:
    failures.append("format: expected 48kHz mono")
if stream.get("codec_name") != "pcm_s16le" or stream.get("bits_per_sample") != 16:
    failures.append("format: expected PCM16")
```

Thus the format checks are distinct: a mono PCM16 stream reporting 48000 passes both; a mono PCM16 stream reporting 47999 fails only the first with exactly `format: expected 48kHz mono`. The predicate does not test a rate range or tolerance. `measure()` gets stream fields and container duration from ffprobe (`stream=sample_rate,channels,codec_name,bits_per_sample:format=duration`), converts sample rate to `int`, then decodes with the project command `sox PATH -t f32 -e floating-point -`. It computes the whole-wave centroid on an FFT frequency grid using `1/rate`. UI duration/peak/RMS/centroid checks are separate from the metadata format checks.

Round 48 provides the immediately lower-side reference. Its pair used 5760 frames and identical PCM16 sample payload / SoX-decoded f32 sequence; the WAV headers reported 47999 and 48000 respectively. This is a same-discrete-samples metadata comparison, not evidence about resampling or identical physical-time signals.

## R48 observed files and outcomes

The R48 executor report records these exact probe invocations, each exit **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-48/executor/ui-47999.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-48/executor/ui-48000.wav
```

Observed ffprobe stream metadata and format duration:

| File | SHA-256 | rate | channels | codec | bits/sample | duration |
|---|---|---:|---:|---|---:|---:|
| `ui-47999.wav` | `71551e200633e62b1b9db4ee5a582f8d4d996cd693f2e4a040a96023b130a210` | 47999 | 1 | pcm_s16le | 16 | 0.120003 s |
| `ui-48000.wav` | `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c` | 48000 | 1 | pcm_s16le | 16 | 0.120000 s |

Both durations are within UI `.12s ± .001s`. The project helper measurement command below exited **0** for both:

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-48/executor"); print(json.dumps({"47999":m.measure("ui",m.SPECS["ui"],d/"ui-47999.wav"),"48000":m.measure("ui",m.SPECS["ui"],d/"ui-48000.wav")},indent=2))'
# exit 0
```

SoX-decoded/project-measured values:

| Rate | peak FS | RMS dBFS | centroid Hz | bandwidth Hz | format result |
|---:|---:|---:|---:|---:|---|
| 47999 | 0.27996826171875 | -18.327858226717105 | 1022.5148421151724 | 586.904753883307 | sole failure: `format: expected 48kHz mono` |
| 48000 | 0.27996826171875 | -18.327858226717105 | 1022.536144951523 | 586.9169813204176 | no failures |

The 47999 and 48000 values both fit the UI duration, peak `< .95`, RMS `>= .001`, centroid `[250,4000] Hz` conditions. The slight centroid/bandwidth change reflects the frequency grid using the metadata rate; no signal processing inference follows. R48 reports byte-identical PCM and SoX-f32 decode output (decoded SHA-256 `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f`).

## Errors and scope

R48 executor reports no setup errors, failed numeric fits, or transcription corrections for the measured pair. The separate R48 scout report mentions an exploratory direct SoX stats command that exited 1 because raw stdin had unspecified rate (SoX defaulted to 8 kHz and then reported differing sample rates). That was a malformed direct-stats setup, not a project-helper metric failure. These are prior-round reported observations; I did not run a new numeric fit or transcribe new measurements for this scout task.

Round 25's 44100-Hz mono PCM16 probe was a broad off-rate example and also failed UI duration; it did not isolate the adjacent rate boundary. This note maps the exact predicate against R48's measured lower-side case only. It makes no claim about arbitrary rates, conversion/resampling, audio quality or perception, production, rights, engine behavior, publishing, or promotion; no audition was performed.
