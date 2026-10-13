# R45 critic: negative duration isolation and boundary limits

## Scope and verdict

I read the R45 declaration in `.shokunin/audio/LOG.md`. The declared claim is a negative-side numerical fixture calibration: 5713 frames should be within the ordinary `.12 s ± .001 s` duration gate, while 5711 frames should fail only that gate, without changing the predicate or canonical fixtures. The available independent alt pair supports those two expected outcomes. It does not prove exact equality behavior, general negative-side robustness, or more than these specific fixtures and tool path.

## Measured alt fixtures

Ran the fixture measurement helper against the two files already present in `corpus/live/round-45/alt/`:

```text
python .shokunin/audio/corpus/live/round-45/alt/measure_alt.py
exit 0
```

It reported 5713 SHA256 `745bb3dffb2cce371765e9abbe45613266a1e32c9489fe7af5c6dcda15c01620` and 5711 SHA256 `e23080bce71c97780b0760f413926decf9925fa76e9c11bdf39ea7be39e4818e`. The helper output measured durations and checks as follows:

| Frames | ffprobe duration (s) | parsed `duration - .12` (s) | `abs(delta)` (s) | Other measurements | Failures |
|---:|---:|---:|---:|---|---|
| 5713 | 0.119021 | -0.0009789999999999938 | 0.0009789999999999938 | 48000 Hz, mono, `pcm_s16le`, 16-bit; peak 0.269439697265625; RMS -16.374928267066153 dBFS; centroid 1388.963153267418 Hz | none |
| 5711 | 0.118979 | -0.0010209999999999941 | 0.0010209999999999941 | 48000 Hz, mono, `pcm_s16le`, 16-bit; peak 0.269439697265625; RMS -16.375168252396996 dBFS; centroid 1375.7265323144181 Hz | solely `duration: outside ±1 ms` |

For direct ffprobe confirmation I ran the exact command below with each WAV path substituted; both invocations exited 0. The 5713 invocation returned format duration `0.119021`; the 5711 invocation returned `0.118979` (and both returned `pcm_s16le`, 48000 Hz, mono, 16 bits):

```text
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-45/alt/alt-ui-5713.wav
exit 0
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-45/alt/alt-ui-5711.wav
exit 0
```

These results counter a simple confound hypothesis that the failing fixture also misses the level, centroid, or format limits: the recorded measurements meet those limits and the helper reports only duration. They show isolation only for these two generated inputs under this measurement helper; they are not a general proof that duration alone is responsible across other signals or environments. The helper's 5711 result is a numeric failed fit to the expected ordinary duration gate, not a setup error.

## Signed boundary and equality caveat

The ideal sample-time negative offsets are -47/48000 = -0.0009791666666666666 s and -49/48000 = -0.0010208333333333334 s. Actual ffprobe outputs are rounded to six decimals, and the measured signed parsed deltas above—not those ideal values—determine the observed fit. I also made a disposable 5712-frame UI-shaped PCM16 WAV outside the repository and ran:

```text
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json /tmp/r45-critic-ui-5712.wav
exit 0
```

It reported `0.119000`. Parsing and subtracting the target gives `0.119 - 0.12 == -0.0010000000000000009`, hence `abs(delta) == 0.0010000000000000009`; the existing strict `abs(duration - target) > .001` expression evaluates true in this Python float path. Thus 5712 frames is not an equality-pass example. It also does not exactly represent mathematical equality after ffprobe decimal formatting and binary-float subtraction. Do not claim exact equality behavior generally or treat ideal symmetric offsets as measured durations.

## Errors and limits

No setup errors occurred in the helper or ffprobe runs. There is one expected numeric failed fit: the 5711-frame fixture, with the sole duration failure shown above. The 5712-frame disposable probe was evaluated only to inspect the float boundary; I did not run the integrated runner on it. I did not audition audio or infer quality, production readiness, rights, engine behavior, publishing, or promotion. This is numerical fixture-calibration evidence only.
