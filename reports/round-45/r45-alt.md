# R45 alt — independent negative-side duration calibration

Scope: independently generated numerical fixtures only. I did not edit shared source, `LOG.md`, `SCORECARD.md`, canonical artifacts, or another report; I did not commit or push. Scratch files are confined to `.shokunin/audio/corpus/live/round-45/alt/`.

## Fixtures and method

Generated two original mono PCM16 WAVs at 48 kHz using NumPy, each a decaying quadratic-phase chirp: `y=.27*sin(2*pi*(520*t + 1050*t*t))*exp(-4.2*t)`, rounded to PCM16. The files have 5713 and 5711 frames. Their SHA-256 values are pinned below. Measurements use the existing fixture helper's `measure("ui", SPECS["ui"], path)` with unchanged UI spec target `.12 s`, duration predicate `abs(duration-.12) > .001`, peak/RMS checks, and centroid band 250–4000 Hz. This is numerical fixture calibration, not an audition or a quality/production assessment.

## Measurements

Signed delta is measured ffprobe duration minus `.12 s`; absolute delta is its magnitude. The ffprobe decimal is what the helper parsed and compared (not ideal frame arithmetic).

| Frames | SHA-256 | ffprobe duration | Signed delta | Absolute delta | Format | Peak FS | RMS dBFS | Centroid Hz | Failures |
|---:|---|---:|---:|---:|---|---:|---:|---:|---|
| 5713 | `745bb3dffb2cce371765e9abbe45613266a1e32c9489fe7af5c6dcda15c01620` | .119021 s | -.000979 s | .000979 s | 48kHz mono PCM16 | .269439697265625 | -16.374928267066153 | 1388.963153267418 | none (pass) |
| 5711 | `e23080bce71c97780b0760f413926decf9925fa76e9c11bdf39ea7be39e4818e` | .118979 s | -.001021 s | .001021 s | 48kHz mono PCM16 | .269439697265625 | -16.375168252396996 | 1375.7265323144181 | sole `duration: outside ±1 ms` |

For both, format, peak (<.95), RMS (well above .001 linear; reported RMS dBFS), and centroid (250–4000 Hz) checks pass. Thus the failure on 5711 is isolated to the ordinary duration predicate. The small centroid and level differences between fixtures do not approach their respective boundaries; this pair does not isolate duration by making every sample value equal. Integrated LUFS was unavailable (`null`) for both and is not used by these pass/fail checks.

Ideal frame offsets are -47/48000 = -.0009791666666666666 s and -49/48000 = -.0010208333333333334 s, but the measured ffprobe decimals above govern. No 5712-frame/`.001 s` equality claim is tested.

## Commands and exits

Exact measurement command:

```sh
python3 .shokunin/audio/corpus/live/round-45/alt/measure_alt.py
```

Exit **0**; emitted both JSON results, with `failures: []` for 5713 and only `duration: outside ±1 ms` for 5711.

Exact ffprobe command (looped over the two listed fixture paths):

```sh
for f in .shokunin/audio/corpus/live/round-45/alt/alt-ui-5713.wav .shokunin/audio/corpus/live/round-45/alt/alt-ui-5711.wav; do ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json "$f"; printf 'ffprobe_exit=%s\n' "$?"; done
```

Both ffprobe invocations exited **0** and reported respectively `.119021` and `.118979` seconds, 48000 Hz, one channel, `pcm_s16le`, 16 bits/sample. The loop shell exited **0**.

A first helper invocation exposed a path setup error, not a numeric fit failure:

```sh
python3 .shokunin/audio/corpus/live/round-45/alt/measure_alt.py
```

That attempt exited **1** with `ValueError: '.shokunin/audio/corpus/live/round-45/alt/alt-ui-5713.wav' is not in the subpath of '/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus'` from the helper's `relative_to(ROOT)`. I corrected only the scratch helper to resolve the corpus root and reran the exact command above successfully. This setup exception is separate from the 5711 expected numeric duration failure.

## Limits

This supports only an independent negative-side pair for the existing numeric tolerance predicate: 5713 passes and 5711 fails on duration alone under this helper. It makes no claim about perceptual duration, audio quality, production, rights, engines, publishing, or promotion.
