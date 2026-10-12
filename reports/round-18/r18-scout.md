# Round 18 scout — 200 Hz slope probe map

## Source and baseline evidence

The source is `corpus/artifacts/stem_layer_third.wav`, the 4 s, 48 kHz mono original 200 Hz two-section fixture. The runner maps this fixture's section component to 200 Hz; each half is 96,000 samples. `section_contrast` measures the adjacent-sample gap at the join and the absolute mismatch between one-sample slopes on the two sides. The local side-slope failure condition is strictly `> 0.001` full scale/sample (equality passes); join-gap failure is strictly `> 0.03` FS. The outer-loop slope bound is also strictly `> 0.001` FS/sample.

Read the canonical PCM as signed 16-bit counts using the exact command `sox .shokunin/audio/corpus/artifacts/stem_layer_third.wav -t s16 -`; exit **0**. Midpoint counts at frames 95,998–96,001 are respectively **[-26, -13, 0, 43]**. Thus the two side slopes are +13 and +43 counts/sample and their absolute mismatch is 30 counts / 32768 = **0.00091552734375 FS/sample**. This is below the strict limit by **0.00008447265625 FS/sample** (2.768 counts).

The current canonical runner receipt is `corpus/live/runs/20261012T191207784092Z-normal/measurements.json` (normal run recorded by parent; not a probe). Its measured 200 Hz section evidence is valid: amplitudes 0.014999984892417233 and 0.04999803906398615 FS; signed contrast +10.457242997641432 dB; join gap 0.000396728515625 FS (13 counts), passing the 0.03 bound. Measured join and outer slope mismatch is 0.00091552734375 FS/sample, passing the .001 bound. The canonical measurement has no failures. These are baseline measurements, not a measurement of the proposed probe.

## +8-only hypothesis (prediction, not a result)

If only frame 96,001 changes from **43 to 51 counts** (+8 counts, 8/32768 = 0.000244140625 FS), the predicted side slopes become +13 and +51 counts/sample. Their absolute mismatch becomes **38/32768 = 0.00115966796875 FS/sample**, which exceeds the strict 0.001 bound by 5.232 counts/sample (0.00015966796875 FS/sample). This is a prediction from the defined arithmetic, not a WAV build or runner result.

Predicted unaffected quantities under this single-sample edit: the join-adjacent gap remains 13/32768 = 0.000396728515625 FS, below .03; the outer-loop endpoints and endpoint-side samples do not change, so its slope remains the measured 0.00091552734375 FS/sample; format/duration do not change. The section component-validity and >=6 dB contrast should remain passing, but are **not measured here** and must be verified on the actual probe. No claim that a probe exists, passes, or has been replayed.

## Commands and limits

Inspection command `sox .shokunin/audio/corpus/artifacts/stem_layer_third.wav -t s16 -` exited **0**; source/receipt inspection was performed in Python. No setup command failed. No audio was synthesized or modified by this scout. This analysis supports only a narrowly predicted local slope-bound crossing in the existing offline measurement fixture. It does not establish audible/perceptual, musical, production, adaptive-engine, compatibility, security, or rights conclusions.
