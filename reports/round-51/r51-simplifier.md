# R51 simplifier

## Recommendation

Keep this as two explicit opt-in builder/runner modes that select one pair member and call the existing `measure(..., SPECS["ui"], path)` unchanged. The builder should write the existing deterministic 5760-frame mono/48kHz pair into the round scratch directory. Reuse the established UI fixture generation path and its existing report/receipt shape; add only the two argument dispatches and labels needed to select PCM16 control or PCM24 candidate. Do not introduce a codec abstraction, generic bit-depth option, shared conversion layer, new threshold, or general framework. The acceptance is narrow: control has no failures; candidate has exactly `format: expected PCM16`.

One low-risk pair construction is to quantize a normalized sample sequence once to signed PCM16 and scale those integer values by 256 for the 24-bit packed little-endian member. That makes their intended normalized values equal and avoids separately chosen signals. Make the WAV headers explicit (mono, 48000, PCM16/PCM24) and use the existing UI SPECS/checks. Evidence below is my executor pair; it is not an integrated builder/runner replay.

## Direct project measurement evidence

Executor files: `corpus/live/round-51/executor/pair_pcm16.wav` and `pair_pcm24.wav`.

Exact commands run:

```sh
python .shokunin/audio/corpus/live/round-51/executor/generate_pair.py
# exit 0
python .shokunin/audio/corpus/live/round-51/executor/measure_pair.py .shokunin/audio/corpus/fixtures/measure_audio.py /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-51/executor/pair_pcm16.wav /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-51/executor/pair_pcm24.wav
# exit 0 (measurement helper prints result objects; it does not set process exit from failures)
```

Project SoX-backed measurement returned for both: duration 0.12 s, sample rate 48000 Hz, mono. PCM16: `pcm_s16le`, 16 bits, peak 0.315399169921875, RMS -14.628083420045229 dBFS, centroid 1123.8154138173777 Hz, failures `[]`. PCM24: `pcm_s24le`, 24 bits, same reported peak/RMS/centroid, failures exactly `["format: expected PCM16"]`. These are project-measurement outputs, not generic codec conclusions.

Actual `ffprobe` stream metadata and file SHA-256:

| file | codec | rate | channels | bits | duration | SHA-256 |
|---|---|---:|---:|---:|---:|---|
| `pair_pcm16.wav` | `pcm_s16le` | 48000 | 1 | 16 | 0.120000 | `2d201f849ecb416401b15c88e172527f9beec852c8998123f5f06131c712fee0` |
| `pair_pcm24.wav` | `pcm_s24le` | 48000 | 1 | 24 | 0.120000 | `6d3f804579124af4fb14f8d7313b25fb87231ca9729a434661475939cae601c8` |

Project SoX-f32 decode produced 5760 values for each. Independent SoX decode commands:

```sh
sox .shokunin/audio/corpus/live/round-51/executor/pair_pcm16.wav -t f32 -e floating-point /tmp/r51-simplifier-pcm16.f32
# exit 0
sox .shokunin/audio/corpus/live/round-51/executor/pair_pcm24.wav -t f32 -e floating-point /tmp/r51-simplifier-pcm24.f32
# exit 0
```

Both yielded decoded peak 0.315399169921875 and decoded RMS -14.628083532559959 dBFS. Both pass the declared UI bounds (duration ±.001 s, peak <.95, RMS >=.001, centroid 250–4000 Hz). The generated pair uses one common quantized sequence scaled into PCM24; actual file hashes differ as expected from headers/packing.

## Setup and evidence boundaries

The first relative-path invocation of `measure_pair.py` exited 1 with `ValueError` because its helper calls `Path.relative_to(ROOT)` and the relative input path was not under its absolute root. This was a path/setup error, not a failed numeric fit or format result. A following quoted-command attempt exited 127 (`bash: ... No such file or directory`), another command-wrapper quoting/setup error. The corrected absolute-path command above ran successfully. Do not count either setup failure as a gate result. No numeric fit failed; no transcription attempted or performed.

This recommendation concerns only minimal wiring for the declared PCM24-vs-PCM16 UI fixture check. No inference about other codecs, conversion, perceptual/audio quality, production, rights, engines, publishing, or promotion.
