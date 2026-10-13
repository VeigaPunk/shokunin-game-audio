# R50 executor — same PCM mono/stereo calibration pair

## Claim and method

Generated an original deterministic 5760-frame, 48 kHz PCM16 mono WAV and a stereo WAV with left and right channels equal to that mono integer sequence. The pair tests the unchanged `measure(..., SPECS["ui"])` format predicate against the already-declared `.12 s` UI duration, peak `<.95`, RMS `>=.001`, and centroid 250–4000 Hz checks. WAV channels are interleaved in the stereo file. The project measurement decodes the complete SoX float stream and computes one whole-stream FFT/centroid; I make no claim about channel-agnostic handling or separate per-channel results.

Files are under `.shokunin/audio/corpus/live/round-50/executor/`: `generate.py`, `mono.wav`, `stereo.wav`, `measure_one.py`, `check.py`. Generator: `n=5760`, `t=i/48000`; quantized PCM16 sequence `round(32767 * clip((.18 sin(2π440t)+.10 sin(2π1200t+.2)+.06 sin(2π2600t+.7))*exp(-8t), -.95, .95))`. Stereo interleaves that sequence twice.

## Commands and exits

- `python3 .shokunin/audio/corpus/live/round-50/executor/generate.py` — exit **0**.
- Initial measurement invocation passed a string path to the project helper: `python3 -c "import importlib.util,pathlib,json; s=importlib.util.spec_from_file_location('m',r'.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure('ui',m.SPECS['ui'],r'.shokunin/audio/corpus/live/round-50/executor/mono.wav'),sort_keys=True))"` — exit **1**, `AttributeError: 'str' object has no attribute 'relative_to'`. This is a harness invocation/setup error, not a numeric fit or gate result.
- Corrected invocation used a `pathlib.Path`: `python3 .shokunin/audio/corpus/live/round-50/executor/measure_one.py .shokunin/audio/corpus/live/round-50/executor/mono.wav` — exit **0**, no failures.
- `python3 .shokunin/audio/corpus/live/round-50/executor/measure_one.py .shokunin/audio/corpus/live/round-50/executor/stereo.wav` — exit **1**, sole failure `format: expected 48kHz mono`.
- `python3 .shokunin/audio/corpus/live/round-50/executor/check.py` — exit **1** by design of this local check (mono clean, stereo sole expected format rejection); printed the same project results. It returns nonzero when either input has failures.
- `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json <file>` — exit **0** for both files; actual metadata below.
- SoX metric command used by the project: `sox <file> -t f32 -e floating-point -`; both exits **0**.

## Actual metadata and decoded project metrics

| WAV | SHA-256 | ffprobe sample rate / channels / codec / bits | ffprobe duration | SoX decoded floats | project peak | project RMS dBFS | project whole-wave centroid | project failures |
|---|---|---|---:|---:|---:|---:|---:|---|
| mono.wav | `93223ee4df8c027d6efaa12d9eca47af3de4fba1eba90c27f29c49ab0086a54a` | 48000 / 1 / pcm_s16le / 16 | 0.120000 s | 5760 | 0.3160400390625 | -19.902100515581505 | 1928.2134621890698 Hz | none; exit 0 |
| stereo.wav | `59e508f1b30d17eef5f00951434915bc7974e02d6988faf07a557270611e950e` | 48000 / 2 / pcm_s16le / 16 | 0.120000 s | 11520 interleaved values | 0.3160400390625 | -19.902100515581505 | 2019.8445020922231 Hz | sole `format: expected 48kHz mono`; exit 1 |

Both durations are within ±1 ms; both peaks are `<.95`, RMS is `>=.001`, centroids are within 250–4000 Hz. Project whole-wave FFT centroids differ because interleaving changes the decoded stream analyzed as one sequence; this report does not interpret the stereo result as per-channel analysis. Payload SHA-256 of the 5760 little-endian mono PCM samples is `b4ff799a96924c8b8df0a77e76c1e0d69b4fc3f0ce457ae1c32621a77f891d23`; SoX-decoded stereo adjacent values compared equal (`max abs(left-right)=0`).

## Failure classification / limits

No unsuccessful numeric fit required iteration. The only observed gate rejection is the intended mono-only format predicate on stereo. The one string-vs-Path exception is setup error, disclosed above. No transcription error. This establishes only this deterministic pair under the existing project measurement function. It does not establish general stereo handling, downmixing, channel-agnostic behavior, audibility, quality, perception, production, rights, engine behavior, publishing, or promotion.
