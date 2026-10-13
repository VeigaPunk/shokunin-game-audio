# Round 48 critic — adjacent-rate format fixture

## Scope and declared claim

I read `.shokunin/audio/LOG.md` Round 48 declaration. Its narrow intended calibration is an original mono PCM16 UI-shaped pair at 47999/48000 Hz, 5760 frames, with the same decoded PCM if feasible; a format-only failure at 47999 and clean pass at 48000, while duration, level, and centroid checks pass. This review tests whether the available artifacts support that narrow numeric claim and challenges broader interpretations. I did not edit source, LOG, scorecard, canonical artifacts, or other reports; I did not run the measurement runner, audition audio, or transcribe an outcome from a run receipt.

## Evidence inspected

The available executor scratch contains `corpus/live/round-48/executor/generate.py`, `ui-47999.wav`, and `ui-48000.wav`. The generator writes the same 5760 little-endian PCM16 values to both WAVs, using a 48 kHz time grid; only the WAV sample-rate header differs. WAV hashes are distinct:

- 47999 Hz: `71551e200633e62b1b9db4ee5a582f8d4d996cd693f2e4a040a96023b130a210`
- 48000 Hz: `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c`

Exact metadata command used for both files:

```sh
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,bits_per_sample,bits_per_raw_sample,duration:format=duration -of json <absolute-path>
```

Exit **0** for each. Actual stream metadata:

| File | codec | sample rate | channels | bits/sample | stream/format duration |
|---|---|---:|---:|---:|---:|
| `ui-47999.wav` | `pcm_s16le` | 47999 | 1 | 16 | 0.120003 / 0.120003 s |
| `ui-48000.wav` | `pcm_s16le` | 48000 | 1 | 16 | 0.120000 / 0.120000 s |

I ran the project’s documented SoX decode shape on each (`sox <absolute-path> -t f32 -e floating-point -`). Both exited **0**, returned 5760 samples, and had the same decoded-f32 SHA-256 `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f`; arrays were exactly equal (max difference 0). Metrics computed from those returned arrays using `measure_audio.py`’s whole-wave `abs(rfft)` centroid formula, with each file’s ffprobe rate for its frequency grid:

| File | peak | RMS dBFS | centroid Hz |
|---|---:|---:|---:|
| `ui-47999.wav` | 0.27996826171875 | -18.327858226717105 | 1022.5148421151706 |
| `ui-48000.wav` | 0.27996826171875 | -18.327858226717105 | 1022.5361449515246 |

Both centroids are inside the UI band (250–4000 Hz); peak and RMS satisfy the stated level limits. Both metadata durations are within ±0.001 s of 0.12. The PCM values are identical, but their sample-rate tags—and therefore represented time scale, duration, and FFT frequency grid—are not. The centroid difference (~0.0213 Hz) is small and does not change the band result; still, this is not literal invariance of all non-format measurements.

For context, Round 25’s existing broad negative controls are unlike this adjacent-rate pair. Exact command `ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,bits_per_sample:format=duration -of json <path>` exited **0** for both: `mono441_probe.wav` is PCM16/44100/mono/4.000000 s, while `stereo48_probe.wav` is PCM16/48000/two-channel/4.000000 s. These metadata examples test obvious mismatches, not 47999 versus 48000.

## Falsification / limits

- **“Sole format isolation” needs qualification.** The generator holds the PCM sample sequence constant, and measured level/sample count are equal, so this is a useful *metadata-rate boundary* fixture. But changing the WAV rate also changes interpreted duration by 3 microseconds and the FFT frequency axis; centroid is not identical. Those other gates happen to remain comfortably passing, rather than being mathematically invariant. The intended failure can at most demonstrate the behavior of the exact `format_failures()` predicate on these inputs, once the runner receipt confirms it—not a universal single-variable causal result.
- **No resampling claim follows.** SoX was used to decode each file to f32; it returned identical samples. No resampling command or converter path was exercised. That says nothing about a resampling engine, rate conversion, or other readers’ treatment of these files. Equal decoded sample arrays are not evidence of converter behavior.
- **Duration boundary is not exercised.** Both durations pass the runner’s ±1 ms check by a wide margin; the pair does not establish behavior at either duration tolerance edge. Nor is a successful project-run receipt present in the inspected material, so setup, runner exit status, JSON failures, and actual gate attribution remain unverified here. A candidate WAV’s apparent metadata is not the same thing as a completed measurement-run outcome.
- **Universality is unsupported.** Two generated mono PCM16 WAVs around one exact rate, on one code path, cannot establish behavior for other rates, codecs, channel layouts, containers, decoded audio sources, applications, or conversion workflows. Round 25’s 44.1k and stereo probes only show distinct gross metadata cases. No quality, perception, production, rights, engine, publishing, or promotion conclusion is warranted.

**Assessment:** scratch data supports a narrow candidate pair with identical decoded PCM, distinct rate metadata, and duration/level/centroid values inside declared bounds. It does not independently verify the promised runner pass/fail or prove universal format isolation or resampling behavior. Keep setup evidence, numeric fit, and any later runner transcription as separate claims.
