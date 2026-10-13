# Round 22 scout — ffprobe metadata and format predicate

## Read-only findings

`measure_audio.py:measure()` invokes ffprobe with `-show_entries stream=sample_rate,channels:format=duration`, parses the first stream, then SoX-decodes the input to floating-point PCM for measurements. Its current format predicate is exactly `rate != 48000 or int(stream["channels"]) != 1`; on mismatch it appends `format: expected 48kHz mono`. It does **not** request/check `codec_name`, `sample_fmt`, `bits_per_sample`, or `bits_per_raw_sample`. Consequently, by source inspection, PCM width/encoding is not an explicit format criterion. SoX decode may normalize accepted inputs before all subsequent numeric checks.

Read-only ffprobe evidence on the available matched scratch pair:

- `native24.wav`: `codec_name=pcm_s24le`, `sample_fmt=s32`, `bits_per_sample=24`, `bits_per_raw_sample=24`, `sample_rate=48000`, `channels=1`.
- `native16.wav`: `codec_name=pcm_s16le`, `sample_fmt=s16`, `bits_per_sample=16`, `sample_rate=48000`, `channels=1`.
- Canonical `ui.wav` reports the same PCM16 fields as `native16.wav`.

I invoked the existing `measure()` directly with a 1-second, permissive fixture spec against both scratch files. Both returned `failures: []` (24-bit RMS −15.0515 dBFS; 16-bit RMS −15.0518 dBFS). This demonstrates that these matched files, including PCM24, pass the current measured predicates; it does not demonstrate integrated `--probe-invalid` behavior or a proposed after-state predicate. The initial mismatched 0.12-second/UI spec produced duration and centroid failures on PCM24, not a format failure; this is a confounded fit and is not evidence of bit-depth rejection.

The native PCM24 stream metadata is noteworthy: ffprobe reports `sample_fmt=s32` alongside `pcm_s24le` and 24 raw bits. Thus checking `sample_fmt != "s16"` or relying on that field alone would be a poor PCM16 discriminator. A candidate explicit PCM16 predicate should use the codec name (`pcm_s16le`) and/or `bits_per_raw_sample`/`bits_per_sample` with the known-good PCM16 control, and should be tested at the runner level. This report does not prescribe a broader codec policy.

## Exact shell invocations and exits

1. `ffprobe -v error -show_streams -show_format -of json .shokunin/audio/corpus/live/round-22/alt/native24.wav` — exit **0**; full JSON showed `pcm_s24le`, `s32`, 24-bit, 48 kHz mono, 1.000 s.
2. `ffprobe -v error -show_streams -show_format -of json .shokunin/audio/corpus/live/round-22/alt/native16.wav` — exit **0**; full JSON showed `pcm_s16le`, `s16`, 16-bit, 48 kHz mono, 1.000 s.
3. `python3 -c "import importlib.util; p=".shokunin/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location(\"measure_audio\",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure(\"native24\",(.12,250,4000,False),\".shokhun/audio/corpus/live/round-22/alt/native24.wav\"))"` — exit **1**, shell quoting removed embedded quotes; `SyntaxError`. Failed setup, not a test.
4. `python3 -c 'import importlib.util; p=".shokhun/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("native24",(.12,250,4000,False),".shokunin/audio/corpus/live/round-22/alt/native24.wav"))'` — exit **1**, `AttributeError: 'str' object has no attribute 'relative_to'`; failed harness setup, not a test.
5. `python3 -c 'import importlib.util; from pathlib import Path; p=".shokhun/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("native24",(.12,250,4000,False),Path(".shokunin/audio/corpus/live/round-22/alt/native24.wav")))'` — exit **1**, relative path was not under module `ROOT`; failed harness setup, not a test.
6. `python3 -c 'import importlib.util; from pathlib import Path; p=".shokhun/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("native24",(.12,250,4000,False),Path(".shokunin/audio/corpus/live/round-22/alt/native24.wav").resolve()))'` — exit **0**, but UI spec gave duration and spectrum failures; confounded exploratory fit.
7. Same invocation with `native24` and spec `(1.0,50,1000,False)` — exit **0**, `failures: []`.
8. `ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_fmt,bits_per_sample,bits_per_raw_sample,sample_rate,channels -of json .shokunin/audio/corpus/live/round-22/alt/native24.wav` — exit **0**, exact metadata listed above.
9. Same ffprobe command for `.shokunin/audio/corpus/live/round-22/alt/native16.wav` — exit **0**, exact metadata listed above.
10. Same ffprobe command for `.shokunin/audio/corpus/artifacts/ui.wav` — exit **0**, exact metadata listed above.
11. Same `measure()` invocation as item 7 with `native16` — exit **0**, `failures: []`.

## Limits / failed fits

The only passing direct `measure()` runs use deliberately permissive specs and do not test the full runner or receipt classification. The first attempted UI-spec comparison confounded width with duration/spectrum requirements. The two scratch files are scout-provided originals, not canonical artifacts. No source was changed, no integrated after-state was tested, and no inference is made about audible/perceptual quality, rights, engine behavior, or publishing. Exact commands above include failed setup invocations; those are not passes.
