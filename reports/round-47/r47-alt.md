# R47 alternate executor — independently generated UI centroid pair

## Result

I generated an independent original pair in `corpus/live/round-47/alt/` using the same fixture dimensions and PCM encoding but a separate nominal-frequency recipe. Project `measure_audio.measure()` decoded each through SoX f32 and computed the whole-wave magnitude-FFT centroid.

| Control | SHA-256 | Duration / format | Decoded centroid | Peak FS | RMS dBFS | Failures |
|---|---|---|---:|---:|---:|---|
| `alt-ui-upper-below.wav` | `20668f7a9bd167479e185ac3ad9ec13b36380719cfcf6506775f6bc63294e69d` | .12 s / 5760 frames / 48k mono PCM16 | 3998.2575908677754 Hz | .27996826171875 | -18.327828680796642 | none |
| `alt-ui-upper-above.wav` | `61e69e3041ff76db1d5b67a892b3b4723d2296ea51235511fc2de8edf6f41cfb` | .12 s / 5760 frames / 48k mono PCM16 | 4000.5907358489767 Hz | .27978515625 | -18.327833579476803 | `spectrum: centroid outside fixture band` only |

The runner's ordinary UI band is inclusive through 4000 Hz. Thus the below control is inside and the above control is outside; both pass format, duration, and level checks. LUFS was null and is not a gate. This is a numerical fixture bracket, not a claim about audio quality or perception.

## Recipe and fits

`generate_and_measure.py` writes a .28-amplitude Hann-windowed sinusoid at nominal 3982 Hz and 3985 Hz, respectively, quantized by `np.rint(clip(x,-1,1)*32767)` to little-endian PCM16. It imports the project measurement helper, which runs `sox <wav> -t f32 -e floating-point -` and measures decoded samples. Nominal tone frequency is not the decoded centroid.

Exploratory numerical fits (same duration, format, and windowed-sine recipe) were broader: nominal 3800/3900/3950 yielded decoded centroids 3817.223181586488 / 3917.0968064376293 / 3967.091051928427 Hz (all below); nominal 4050/4100/4200 yielded 4066.3960394571745 / 4116.53540246853 / 4216.391148585723 Hz (all above). These are candidate measurements, not gate failures. The final alternate pair is closer to the boundary while retaining the required polarity. No exact-4000 equality candidate was tested.

## Exact shell command and exit

The final generation-and-measure command was run from the project working directory and exited **0**:

```sh
python3 /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-47/alt/generate_and_measure.py
```

The script prints each exact SHA-256 and complete project-helper result. It calls the helper on absolute paths under its corpus root. I made no changes to the shared source, LOG, SCORECARD, canonical artifacts, or other reports. No audition, quality, perception, production, rights, engine, publishing, or promotion inference.
