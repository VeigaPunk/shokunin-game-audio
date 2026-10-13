# R51 reviewer: paired PCM24/PCM16 opt-in UI modes

## Minimal design

Add two mutually exclusive flags to `corpus/fixtures/measure_audio.py`, e.g. `--probe-ui-pcm24` and `--probe-ui-pcm16`. Each flag builds its own deterministic 5760-frame, mono, 48 kHz UI scratch WAV under `corpus/live/round-51/` and adds only that measurement beside the unchanged canonical fixture set. Use the existing `measure(name, SPECS["ui"], path)` and `format_failures`; do not add a PCM24 exception, alter a threshold, or change ordinary mode. The PCM24 flag should be an intentional fixture-validation failure (exit 1, sole `format: expected PCM16`); PCM16 should pass (exit 0). Reject simultaneous flags through the existing argparse one-mode rule. Leave the prior 60 controls, canonical 17, five `_alt` and four family comparisons, sections, invalid probes, and normal restoration untouched.

## Paired scratch measurement

I generated original mono WAVs with the same 5,760-point normalized three-sine sequence (440/1200/2600 Hz; peak target about .266), quantized independently to signed PCM16 and PCM24. They are separate source files, not a conversion chain. I ran:

- `python .shokunin/audio/corpus/live/round-51/reviewer/make_pair.py` — exit **0**.
- `python .shokunin/audio/corpus/live/round-51/reviewer/inspect_pair.py` — exit **0**; ffprobe and SoX decode results:

| File | SHA-256 | ffprobe codec / bits / rate / channels | Duration | SoX f32 decoded values | Peak FS | RMS dBFS | Whole-vector centroid |
|---|---|---|---:|---:|---:|---:|---:|
| pcm16.wav | `53edb7025cc4366be4c319b9dd0c7f22737ad644397b0daf875ec981f04fa8e5` | `pcm_s16le` / 16 / 48000 / 1 | 0.120000 s | 5760 | 0.2662353515625 | -17.874277813034283 | 2318.6837059661143 Hz |
| pcm24.wav | `bc4ca26eccf25b1cdefc8ccda1d6a516580f2c95e39267f8a4cd70b83d2a7568` | `pcm_s24le` / 24 / 48000 / 1 | 0.120000 s | 5760 | 0.26623404026031494 | -17.87429046235651 | 2318.658036790902 Hz |

I then used the project’s unmodified `measure(..., SPECS["ui"], path)` for both files:

- `python .shokunin/audio/corpus/live/round-51/reviewer/project_measure.py` — script exit **0** (it prints both results; it is a measurement harness, not a production probe-mode invocation).
- PCM16 result: all gates pass; duration 0.12 s, 48000 Hz mono `pcm_s16le`/16-bit, peak 0.2662353515625, RMS -17.874277813034283 dBFS, centroid 2318.6837059661143 Hz. The intended per-case mode result is exit **0**.
- PCM24 result: sole failure `format: expected PCM16`; duration 0.12 s, 48000 Hz mono `pcm_s24le`/24-bit, peak 0.26623404026031494, RMS -17.87429046235651 dBFS, centroid 2318.658036790902 Hz. The intended per-case mode result is exit **1**.

For the proposed CLI, exact invocation/expected status is:

```sh
python .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16  # 0
python .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm24  # 1; sole format failure
```

These proposed flags have not been implemented or run here; the actual project measurement was through the direct helper script above. No setup errors, failed numeric fits, or transcription corrections occurred. The measured normalized decoded sequences are extremely close, not asserted bit-identical. This is only an ordinary UI fixture’s PCM format-predicate contrast; it supports no broad codec, conversion, audio-quality, perception, production, rights, engine, publishing, or promotion inference.
