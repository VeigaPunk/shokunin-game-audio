# R50-alt independent channel-pair attempt

## Scope
I generated an original 0.12 s mono/stereo PCM16 pair in the assigned `alt/` scratch directory. Both stereo channels contain the same 5,760-sample sequence as the mono control. I called the unchanged `measure(..., SPECS["ui"])` for each file. I did not edit shared sources, declarations, scorecard, canonical artifacts, or other reports. This is a project-metric replay only; it is not an audition or claim about general stereo handling.

## Commands, exits, and setup telemetry

1. `python3 .shokunin/audio/corpus/live/round-50/alt/generate.py` — exit **0**, output `generated 5760 frames per channel`.
2. `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-50/alt/mono.wav` — exit **0**.
3. `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-50/alt/stereo.wav` — exit **0**.
4. `sox .shokunin/audio/corpus/live/round-50/alt/mono.wav -t f32 -e floating-point - -V1` — exit **0**; stdout captured as 36,000 bytes (9,000 decoded float32 values).
5. `sox .shokunin/audio/corpus/live/round-50/alt/stereo.wav -t f32 -e floating-point - -V1` — exit **0**; stdout captured as 72,000 bytes (18,000 decoded float32 values).
6. First analysis setup attempted to pass a string path to `measure`; it exited **1** with `AttributeError: 'str' object has no attribute 'relative_to'`. Retrying with a relative `Path` exited **1** with `ValueError` because it was not under the script's resolved corpus root. These are analysis setup errors, not numeric fit failures. Corrected by resolving the scratch path absolutely.
7. Corrected mono command (exit **0**):

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=".shokunin/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure("ui",m.SPECS["ui"],Path(".shokunin/audio/corpus/live/round-50/alt/mono.wav").resolve()),indent=2))'
```

8. Corrected stereo command (exit **0**): same command with `stereo.wav` in the `Path(...)` argument.
9. `sha256sum .shokunin/audio/corpus/live/round-50/alt/mono.wav .shokunin/audio/corpus/live/round-50/alt/stereo.wav` — exit **0**.

## File metadata and hashes

`ffprobe` reported for both: `codec_name=pcm_s16le`, `sample_rate=48000`, `bits_per_sample=16`, `duration=0.120000` s. Mono: `channels=1`; stereo: `channels=2`.

- mono SHA-256: `c9f705a030771fc583ea9321625fa8cb456f3e9ae83c9ba8ad1c8e883c5c1049`
- stereo SHA-256: `f55b5fa90ec546af9c60985b292c8ec16adca0f77ca815c3c47baed958d85ec6`

The SoX-decoded output is interpreted as a flat float32 sequence by the existing project metric. It contains 9,000 values for mono and 18,000 for stereo; the latter is the interleaved whole-wave stream, not a per-channel result. No channel-independent inference is made.

## `measure()` values and fits

Mono decoded metrics: duration **0.12 s**; peak **0.274658203125 FS**; RMS **−14.234543387343951 dBFS**; centroid **1000.9487688622268 Hz**; bandwidth **121.74509593693145 Hz**; integrated LUFS **null**; failures **none**. It fits the 0.12 s ±1 ms duration, peak `<.95`, RMS `>=.001` and UI centroid 250–4000 Hz checks; ordinary measure result is clean.

Stereo decoded metrics: duration **0.12 s**; peak **0.274658203125 FS**; RMS **−14.234543387343951 dBFS**; centroid **1229.8665438991552 Hz**; bandwidth **4030.487915669439 Hz**; integrated LUFS **null**; sole failure: `format: expected 48kHz mono`. It fits duration, peak, RMS and UI centroid bounds; the expected mono-format gate is the only failed fit. The centroid shift is reported as measured, not generalized to stereo streams.

Generation recipe: `x[n] = round(9000 * sin(2π * 1000 * n / 48000))` for `n=0..5759`, serialized as little-endian signed 16-bit PCM; the stereo file duplicates each value into left and right samples. The pair tests this one deterministic signal and these decoded project metrics only.
