# Round 19 scout — 200 Hz PCM16 boundary map

## Source / baseline map

The round-19 LOG declares a calibration-only proposal: one-frame controls derived from `stem_layer_third.wav`, at frame index 96001, with +2 and +3 PCM counts, testing the unchanged strict `> .001` full-scale-per-sample side-slope comparison. This report maps the source and arithmetic; it is **not** evidence that either scratch was built or that a runner mode passed/failed.

Source: `.shokunin/audio/corpus/artifacts/stem_layer_third.wav` (PCM16, 48 kHz mono). The existing `section_contrast()` in `corpus/fixtures/measure_audio.py` reads SoX `f32` samples, and measures the internal join using indices 95998–96001:

- decoded baseline PCM counts: `[-26, -13, 0, 43]`
- adjacent slopes in PCM counts: left `0 - (-13) = 13`; right `43 - 0 = 43`
- absolute side-slope mismatch: `|43 - 13| = 30` counts
- PCM16 full-scale denominator for this decoding: **32768**, so baseline is `30/32768 = 0.00091552734375` FS/sample, below strict `.001`.

The probe changes count at index 96001, the last value in this four-sample window. A +2 edit predicts `[-26,-13,0,45]`: mismatch `|45-13|=32` counts, `32/32768 = 0.0009765625` FS/sample, so it remains below `.001`. A +3 edit predicts `[-26,-13,0,46]`: mismatch `|46-13|=33` counts, `33/32768 = 0.001007080078125` FS/sample, so it exceeds `.001`. Since the comparison is strictly `>`, 32 counts is below the threshold and 33 counts is above it. This identifies the neighboring decoded count outcomes for these proposed positive one-frame edits; it does not establish a universal quantization property beyond this signal/edit/decode path.

A corresponding +1/+4 edit would predict 31/34 counts, respectively; neither changes the boundary inference. This is arithmetic, not an independently built or measured alternative.

## Evidence / exact command

Read source: `measure_audio.py` computes
`abs((samples[96001] - samples[96000]) - (samples[95999] - samples[95998]))`, and the gate appends a failure only when the value `> .001`. The builder’s existing round-18 probe reads the canonical WAV and increments `frames[96001] += 8`; round 19’s proposed +2/+3 are the same indexed edit with different increments, not currently implemented in the viewed source.

Exact shell command used to inspect the four canonical counts and calculate the baseline integer mismatch:

```sh
python3 -c 'import wave,numpy as np; p=".shokunin/audio/corpus/artifacts/stem_layer_third.wav"; w=wave.open(p,"rb"); x=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2"); i=95998; print("pcm16",x[i:i+4].tolist()); print("decoded_expected",(x[i:i+4]/32768).tolist()); print("baseline_counts",abs((int(x[i+3])-int(x[i+2]))-(int(x[i+1])-int(x[i])))); print("denominator",32768)'
```

Exit: **0**. Output:

```text
pcm16 [-26, -13, 0, 43]
decoded_expected [-0.00079345703125, -0.000396728515625, 0.0, 0.001312255859375]
baseline_counts 30
denominator 32768
```

The `decoded_expected` values above are exact PCM integer divisions by 32768; the runner’s actual decode path is SoX f32. I did not invoke either proposed runner mode, and make no runner, audible, engine, or production assertion. No setup errors occurred.
