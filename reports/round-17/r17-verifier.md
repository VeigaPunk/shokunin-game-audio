# Round 17 non-author serial replay (13 modes)

## Scope

Executed serially from repository root on current integrated working tree. No source files or canonical artifacts were modified by this replay; runner-generated run receipts are under `corpus/live/runs/`. Expected negative-control exits are 1. This is an operational replay report; no audible/perceptual/production claim.

## Commands and exits

1. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191029000301Z-normal/measurements.json`; failures `{}`.
2. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` — exit **1**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191029851140Z-layer-alt-reverse/measurements.json`; failures `{"reverse180_probe":["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}`.
3. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` — exit **1**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191030707107Z-layer-alt-slope/measurements.json`; failures `{"slope180_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]}`.
4. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` — exit **1**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191031575331Z-layer-alt-join/measurements.json`; failures `{"join180_probe":["sections: internal join adjacent sample gap > .03 full scale"]}`.
5. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` — exit **1**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191032426724Z-layer-alt-flat/measurements.json`; failures `{"flat180_probe":["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}`.
6. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` — exit **1**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191033283725Z-layer-slope/measurements.json`; failures `{"layer_slope_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]}`.
7. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` — exit **1**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191034143522Z-layer-join/measurements.json`; failures `{"join_probe":["sections: internal join adjacent sample gap > .03 full scale"]}`.
8. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` — exit **1**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191035013662Z-flat/measurements.json`; failures `{"flat30_probe":["sections: 30 Hz component amplitude contrast < 6 dB or invalid"]}`.
9. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` — exit **1**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191035885175Z-layer-flat/measurements.json`; failures `{"flat120_probe":["sections: 120 Hz component amplitude contrast < 6 dB or invalid"]}`.
10. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` — exit **1**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191036732834Z-slope/measurements.json`; failures `{"slope_probe":["loop seam: slope mismatch > .001 full scale per sample"]}`.
11. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` — exit **1**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191037538102Z-failing/measurements.json`; failures `{"ambience":["spectrum: centroid outside fixture band","loop seam: endpoint jump > .03 full scale"]}`.
12. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` — exit **1**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191037766574Z-invalid/measurements.json`; failures `{"short_sections":"section count","corrupt":"decode","wrong_format":"format","odd_sections":"section count"}`.
13. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**; receipt `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/runs/20261012T191038563669Z-normal/measurements.json`; failures `{}`.

All 13 commands ran serially; no command setup failure occurred. First and final normal JSON receipts are byte-equivalent as parsed objects (`True`): `20261012T191029000301Z-normal/measurements.json` and `20261012T191038563669Z-normal/measurements.json`. Final normal contains 13 canonical measurement records; all pass; all five `_alt` distinctness checks pass. New `stem_layer_third` record: 4.0 s, mono 48 kHz, peak 0.04998779296875 FS, RMS -31.66724765274306 dBFS, centroid 287.93805923844434 Hz, outer endpoint gap 0.001312255859375 FS, outer slope delta 0.00091552734375 FS/sample. Section receipt: component 200 Hz; amplitudes 0.014999984892417233 / 0.04999803906398615 FS; contrast +10.457242997641432 dB; internal gap 0.000396728515625 FS; internal side-slope mismatch 0.00091552734375 FS/sample; valid/passed. The slope margin to 0.001 is 0.00008447265625 FS/sample.

## Canonical hashes (SHA-256)

- `.shokunin/audio/corpus/artifacts/ambience_alt.wav` — `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc`
- `.shokunin/audio/corpus/artifacts/ambience.wav` — `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`
- `.shokunin/audio/corpus/artifacts/impact_alt.wav` — `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`
- `.shokunin/audio/corpus/artifacts/impact.wav` — `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc`
- `.shokunin/audio/corpus/artifacts/movement_alt.wav` — `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`
- `.shokunin/audio/corpus/artifacts/movement.wav` — `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d`
- `.shokunin/audio/corpus/artifacts/stem_layer_alt.wav` — `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9`
- `.shokunin/audio/corpus/artifacts/stem_layer_third.wav` — `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`
- `.shokunin/audio/corpus/artifacts/stem_layer.wav` — `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`
- `.shokunin/audio/corpus/artifacts/stem_sections.wav` — `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`
- `.shokunin/audio/corpus/artifacts/stem.wav` — `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0`
- `.shokunin/audio/corpus/artifacts/ui_alt.wav` — `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`
- `.shokunin/audio/corpus/artifacts/ui.wav` — `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`

## Baseline / regression checks

Compared all 12 old canonical artifact hashes to `git show 6fb9e80:<path>`; all match exactly. The added canonical `stem_layer_third.wav` SHA-256 is `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`, distinct from the old canonical files and equal to the worker scratch candidate hash recorded in the round evidence. Compared final normal receipt with pre-integration normal receipt `20261012T185900519223Z-normal`: old 12 measurement objects, old section records, and all distinctness objects match exactly. Threshold numeric constants are unchanged; only centroid-bands map adds the new fixture at `[100, 2000]` Hz.

## Out-of-scope setup telemetry

An earlier helper-spawn attempt was rejected before any worker started; it was not a fixture check or verification pass. Exact attempted Python call: `rlm.spawn('Inspect repository for r17 non-author serial 13-mode replay. Determine exact intended procedure, execute canonical checks and binary hashes as requested if clear. Produce durable report file with commands, results, hashes; report to parent. Avoid modifying code except report.', 'name='+'r17-replay')`. Error: `TypeError: _RLMNamespace.spawn() takes 2 positional arguments but 3 were given`. Excluded from the 13-mode pass count; the parent subsequently explicitly directed no spawning.


## Confirmatory fresh serial replay (requested task)

I reread the Round 17 LOG/wave specification and repeated all 13 exact commands serially as the non-author verifier. No setup errors occurred in this run. The first and final parsed normal receipts compare equal (`True`); first `20261012T191158236005Z-normal`, restore `20261012T191207784092Z-normal`. Mode command/exit/receipt/failures:

1. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**; receipt `20261012T191158236005Z-normal`; failures `{}`.
2. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` — exit **1**; receipt `20261012T191159087283Z-layer-alt-reverse`; failures `{"reverse180_probe":["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}`.
3. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` — exit **1**; receipt `20261012T191159940936Z-layer-alt-slope`; failures `{"slope180_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]}`.
4. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` — exit **1**; receipt `20261012T191200791191Z-layer-alt-join`; failures `{"join180_probe":["sections: internal join adjacent sample gap > .03 full scale"]}`.
5. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` — exit **1**; receipt `20261012T191201645751Z-layer-alt-flat`; failures `{"flat180_probe":["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}`.
6. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` — exit **1**; receipt `20261012T191202517664Z-layer-slope`; failures `{"layer_slope_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]}`.
7. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` — exit **1**; receipt `20261012T191203370008Z-layer-join`; failures `{"join_probe":["sections: internal join adjacent sample gap > .03 full scale"]}`.
8. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` — exit **1**; receipt `20261012T191204221960Z-flat`; failures `{"flat30_probe":["sections: 30 Hz component amplitude contrast < 6 dB or invalid"]}`.
9. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` — exit **1**; receipt `20261012T191205084115Z-layer-flat`; failures `{"flat120_probe":["sections: 120 Hz component amplitude contrast < 6 dB or invalid"]}`.
10. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` — exit **1**; receipt `20261012T191205933559Z-slope`; failures `{"slope_probe":["loop seam: slope mismatch > .001 full scale per sample"]}`.
11. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` — exit **1**; receipt `20261012T191206755584Z-failing`; failures `{"ambience":["spectrum: centroid outside fixture band","loop seam: endpoint jump > .03 full scale"]}`.
12. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` — exit **1**; receipt `20261012T191206987506Z-invalid`; failures `{"short_sections":"section count","corrupt":"decode","wrong_format":"format","odd_sections":"section count"}`.
13. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**; receipt `20261012T191207784092Z-normal`; failures `{}`.

Fresh normal receipt confirms 13 canonical records including `stem_layer_third`; its 200 Hz section amplitudes are `0.014999984892417233` / `0.04999803906398615` FS, contrast `+10.457242997641432` dB, valid/passed; internal gap `0.000396728515625` FS, internal side-slope `0.00091552734375` FS/sample, outer slope same. All generic gates pass, and all five `_alt` distinctness checks pass. Hashes of `layer200_candidate.wav`, `layer200_other.wav`, and canonical `stem_layer_third.wav` were independently rechecked with `sha256sum`; each is `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`. All 12 old artifact hashes again match the corresponding `git show 6fb9e80:<path>` blob. The final receipt preserves all old 12 measurement records, old section records, and distinctness data versus `20261012T185900519223Z-normal`; threshold numeric values unchanged, only new centroid-band key added. All 11 negative-control failure sets match the report's initial serial replay above. No hearing, engine, or production conclusion is inferred.
