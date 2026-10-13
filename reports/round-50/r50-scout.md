# R50 scout — channel-count predicate, historical stereo48, falsifiable UI pair

## Predicate mapping

Read-only inspection of `.shokunin/audio/corpus/fixtures/measure_audio.py` shows the channel-count branch is part of `format_failures(stream)`:

```python
if int(stream["sample_rate"]) != 48000 or int(stream["channels"]) != 1:
    failures.append("format: expected 48kHz mono")
if stream.get("codec_name") != "pcm_s16le" or stream.get("bits_per_sample") != 16:
    failures.append("format: expected PCM16")
```

This is an exact channel-count condition (`channels == 1`), joined with exact rate equality by `or`; it does not express channel-agnostic stereo acceptance. A stream with rate 48000, channels 2, `pcm_s16le`, and 16 bits fails the first condition with exactly `format: expected 48kHz mono` while meeting the separate PCM16 test. The ordinary `measure(..., SPECS["ui"])` flow obtains stream/container metadata using ffprobe and SoX-decodes to f32; UI duration, peak, RMS, and centroid are independent checks. For multichannel decode the project helper's FFT sees the scalar SoX output stream; its metric must not be described as per-channel analysis.

## Historical invalid stereo48 contrast

Round 25 introduced `stereo48_probe` in the invalid-probe inventory. The verifier reports the exact runner invocation and result:

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid
```

Exit **1** (expected invalid-fixture result); receipt `.shokunin/audio/corpus/live/runs/20261013T014025494866Z-invalid/measurements.json`. Its stereo row was `expected_failure / format`, with metadata 48000 Hz, 2 channels, `pcm_s16le`, 16-bit, 4 s. In the same receipt, `native16_probe` was `expected_pass` at 48000 Hz, mono, `pcm_s16le`, 16-bit. Thus the channel-count-only metadata contrast is isolated against native16; `wrong_format` (44100 Hz stereo) remains co-confounded and is not the isolation evidence.

The historical exact ffprobe command for stereo48 was:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-25/stereo48_probe.wav
```

Round-25 verifier reports this direct measurement command (exit **0**):

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location("measure_audio",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure("stereo48_probe",(4.0,100,1000,False),Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-25/stereo48_probe.wav"),),indent=2))'
```

That historical project result was duration 4.0 s; stream 48000 Hz / 2 channels / PCM16; peak `0.199981689453125`; RMS `-16.98997934609775` dBFS; centroid `563.261685059` Hz; sole failure `format: expected 48kHz mono`. It used a broad 100–1000 Hz custom spec, not the UI spec. Its SoX scalar sequence was described as 384000 interleaved samples (192000 frames × 2); this is not evidence of mono-equivalent metrics or channel-independent handling. The invalid-mode receipt tests format metadata, not the ordinary UI-shaped acoustic gates.

The R49 scout gives a useful neighboring exact positive baseline: its 5760-frame mono PCM16 48000-Hz `ui-48000.wav` row has 48000/1/`pcm_s16le`/16-bit metadata, duration 0.120000 s, and no failure. The R49 executor's exact pair measurement command exited **0**:

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-49/executor"); print(json.dumps({"48001":m.measure("ui",m.SPECS["ui"],d/"ui-48001.wav"),"48000":m.measure("ui",m.SPECS["ui"],d/"ui-48000.wav")},indent=2))'
```

Its mono 48000 control metrics were peak `0.27996826171875`, RMS `-18.327858226717105` dBFS, centroid `1022.536144951523` Hz; sole candidate-negative contrast was the rate neighbor, not channels. R49 does not test stereo under the UI gates.

## Proposed falsifiable sole-format UI pair (not run by this scout)

Use the LOG-declared deterministic pair: stereo PCM16 48000 Hz, 5760 frames, with left and right carrying the same PCM16 sequence; and mono PCM16 48000 Hz, 5760 frames carrying that same sequence. Run unchanged ordinary `measure("ui", SPECS["ui"], path)` on each. Prediction: ffprobe reports respectively 48000/2/`pcm_s16le`/16 and 48000/1/`pcm_s16le`/16; both actual format durations are within `.12 s ± .001 s`; both project SoX-f32 decoded streams fit peak `< .95`, RMS `>= .001`, and whole-wave centroid 250–4000 Hz. The mono control should have no failures and exit 0; stereo should have exactly the sole failure `format: expected 48kHz mono` and exit 1. A different result falsifies the declared pair's predicted sole-format UI result. If the stereo scalar/interleaved decode misses a numeric gate, record that failed fit; do not attribute it to channels alone or change the comparator/thresholds.

This is a proposed metadata-and-project-metric test, not a finding that stereo is generally supported or rejected through any channel-aware process. No R50 pair generation, ffprobe, or SoX/project measurement was performed by this scout; therefore there are no R50 hashes, metadata observations, actual numeric fits, or command exits to report. No setup error, R50 numeric-fit failure, or transcription correction was observed because no R50 run was made. Historical values above are explicitly prior-round evidence. No audition or claims about quality, perception, production, rights, engine behavior, publishing, or promotion.
