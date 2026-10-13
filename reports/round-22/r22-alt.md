# r22-alt — independent PCM width/container challenge

## Result

The current measurement path does **not** distinguish PCM16 from native PCM24. I generated matched 1.000 s, 48 kHz, mono 220 Hz sine WAVs in the permitted `corpus/live/round-22/alt/` scratch directory. Both satisfy the current `measure()` gates with empty `failures`, including the PCM24 WAV. This supports the round's before-state hypothesis for a matched native PCM24 RIFF/WAVE input; it does not prove any proposed integration or admission.

`ffprobe` identifies ordinary 24-bit PCM as `codec_name=pcm_s24le`, `bits_per_sample=24`, while `sample_fmt=s32`. The latter is FFmpeg's decoded representation and is not evidence the file is PCM32. Therefore `sample_fmt == s16` would be a poor native PCM16 predicate: it might distinguish the tested pair, but uses a decoder representation rather than the container's declared PCM bit depth. A source-supported narrow PCM16 check should use ffprobe's `codec_name`/`bits_per_sample` (or equivalent explicit WAV header fields) and test both widths. Do not infer valid bits solely from `bits_per_sample`: my WAVE_FORMAT_EXTENSIBLE 24-bit container with `wValidBitsPerSample=20` is still reported by ffprobe as 24 raw/container bits and does not expose the 20-bit valid-bits field in the queried output. If the intended requirement is valid bits rather than container width, this experiment does not establish a reliable metadata path for it.

## Artifacts (original scratch)

- `native16.wav`: PCM16, mono 48 kHz, one second; SHA-256 `bee0d01f2825fe76220d8c12a1d93876c372414746e19e95f147737da7446383`.
- `native24.wav`: packed little-endian signed PCM24, mono 48 kHz, same analytic sine and duration; SHA-256 `c9843a9a9faf92c42eb3ee708ab94d172f7b65897c8d74c9d78a03b78850979e`.
- `native24_extensible.wav`: WAVE_FORMAT_EXTENSIBLE PCM subtype, 24 container/valid bits; SHA-256 `1c0e12afc01e089d0faafaa2fc7d4c892e116434cf38e55b2fbd239ae8d3b34b`.
- `native24_valid20.wav`: same 24-bit container, extensible `wValidBitsPerSample=20`, samples quantized to 20 significant high bits; SHA-256 `0fac249d21e99dcc64eb1ec0cd2c2527539c6bada3ffc3ab0003bd156de81e12`.

The plain PCM16 and PCM24 measurements both had 48 kHz/mono, duration 1.0 s, peak .25 FS and no current check failures. The 16-bit measured centroid was 231.7556 Hz and PCM24 centroid 220.0440 Hz; both lie within the deliberately broad test spec 100–2000 Hz. This slight measurement difference is expected from quantization/leakage and is not a width detector.

## Exact shell invocations and exits

All commands below were run from repository working directory. Files were generated with Python in the REPL, not shell. Shell exit means the exact invocation's exit status.

1. Exact loop invocation:
   `for f in .shokunin/audio/corpus/live/round-22/alt/native16.wav .shokunin/audio/corpus/live/round-22/alt/native24.wav; do echo "FILE=$f"; ffprobe -v error -show_entries stream=codec_name,sample_fmt,sample_rate,channels,bits_per_sample,bits_per_raw_sample -of json "$f"; echo "FFPROBE_EXIT=$?"; sox "$f" -t f32 -e floating-point - >/dev/null; echo "SOX_EXIT=$?"; done`
   **Exit 0** (both ffprobe and SoX subcommands each printed exit 0 for both files). This established the PCM16 `pcm_s16le`/`s16`/16-bit and PCM24 `pcm_s24le`/`s32`/24-bit metadata and successful decode.
2. First direct measurement invocation, using relative scratch paths:
   `python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=(1.0,100,2000,False); print("PCM16",m.measure("native16",spec,Path(".shokunin/audio/corpus/live/round-22/alt/native16.wav"))); print("PCM24",m.measure("native24",spec,Path(".shokunin/audio/corpus/live/round-22/alt/native24.wav")))'`
   **Exit 1**, harness/setup mistake: `measure()` requires `path.relative_to(ROOT)` and the relative argument did not share the absolute root. No result from this attempt is counted.
3. Corrected direct measurement invocation, absolute scratch paths:
   `python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=(1.0,100,2000,False); print("PCM16",m.measure("native16",spec,Path(".shokunin/audio/corpus/live/round-22/alt/native16.wav").resolve())); print("PCM24",m.measure("native24",spec,Path(".shokunin/audio/corpus/live/round-22/alt/native24.wav").resolve()))'`
   **Exit 0**. PCM16 and PCM24 both returned `failures: []` with measurements summarized above. This directly invokes existing measure function; it is not an integrated CLI replay.
4. Extensible 24-bit valid-bits metadata invocation:
   `ffprobe -v error -show_entries stream=codec_name,sample_fmt,sample_rate,channels,bits_per_sample,bits_per_raw_sample:format=format_name -of json .shokunin/audio/corpus/live/round-22/alt/native24_extensible.wav; echo FFPROBE_EXIT=$?; sox .shokunin/audio/corpus/live/round-22/alt/native24_extensible.wav -t f32 -e floating-point - >/dev/null; echo SOX_EXIT=$?`
   **Exit 0**; ffprobe and SoX each exited 0. ffprobe reports PCM24 and 24 raw bits, `s32` sample format, 48 kHz mono; SoX decodes it.
5. Twenty-valid-bit extensible metadata invocation:
   `ffprobe -v error -show_entries stream=codec_name,sample_fmt,sample_rate,channels,bits_per_sample,bits_per_raw_sample -of json .shokunin/audio/corpus/live/round-22/alt/native24_valid20.wav; echo FFPROBE_EXIT=$?`
   **Exit 0**; ffprobe reports the same `pcm_s24le`, `s32`, 24 bits, 48 kHz mono; its queried fields do not distinguish the declared 20 valid bits.

## Failed fits and limits

- The relative-path measurement attempt failed with `ValueError`; it was corrected using resolved absolute paths and is retained here as failed setup telemetry, not evidence.
- No PCM24 rejection or source patch was attempted: this leaf owns no shared-source edits. The evidence instead verifies that PCM24 passes the current checks and documents metadata choices/limits for parent integration.
- The extensible valid-20 WAV is not a positive control for a valid-bits detector: ffprobe's inspected metadata cannot expose that distinction. Do not claim the `bits_per_sample` field means valid bits.
- No integrated `--probe-invalid` result, prior-mode regression, canonical hash comparison, independent reviewer replay, audible/perceptual judgement, export compatibility, production, rights, or engine claim is made here.
