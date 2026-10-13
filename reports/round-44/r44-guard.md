# Round 44 guard — duration-tolerance numeric fixture audit

## Scope and finding

I read the Round 44 declaration in `.shokunin/audio/LOG.md`. The unchanged duration rule is `abs(ffprobe_duration - spec_duration) > .001`; for the UI fixture `spec_duration` is 0.12 s. The candidate files are the executor’s original deterministic 48 kHz mono PCM16 fixtures: 5,807 and 5,809 frames. They are expected to straddle the comparator, with all non-duration ordinary checks passing. This is numerical fixture calibration only; no audition or quality judgment.

## Candidate evidence

I obtained the actual `ffprobe` format durations and ran the project `measure_audio.measure()` helper on each decoded candidate. Deltas below are actual reported duration minus 0.12 s (not ideal frame arithmetic):

| Candidate | SHA-256 | Frames / format | ffprobe duration | Delta from .12 s | Peak FS | RMS dBFS | Centroid Hz | Result |
|---|---|---|---:|---:|---:|---:|---:|---|
| 5,807 (`pass-5807.wav`) | `17890e483de91075569283a2bcfbada6a6402e1cd87ab52da53bdfbc605cf934` | 5807; 48 kHz mono PCM16 | 0.120979 s | +0.000979 s | 0.27947998046875 | -16.431537076901346 | 1132.7351495568296 | no failures |
| 5,809 (`fail-5809.wav`) | `c0552b983ecd9230b16d6ac3441eb8be7b43e80130bbd413fb62272752d7d510` | 5809; 48 kHz mono PCM16 | 0.121021 s | +0.001021 s | 0.27947998046875 | -16.432818198672756 | 936.6642301482127 | sole `duration: outside ±1 ms` |

Both have expected format and pass level and UI centroid (250–4000 Hz); no numeric candidate fit failed. The 5,807 frame result is inside the implemented tolerance; 5,809 is outside. This does not test exact 5,808-frame / 0.001-second equality.

## Preservation and baseline context

The Round 44 LOG declares clean-before `8009269ade6fff69c95de3cbde6a2cd653c33dc9`. This guard made no source, LOG, SCORECARD, canonical asset, or other report edits, and did not run the normal fixture suite or independently verify canonical preservation/restoration. Those are for the required non-author replay. The executor candidates are scratch files under `corpus/live/round-44/executor/` only.

Old 17 canonical SHA/metrics are carried forward from the prior verifier baseline (`fc638d9` / R43 replay); they are not measurements made by this guard. All 17 canonical files had no ordinary failures in that baseline:

| Canonical | SHA-256 | Duration | Peak FS | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---:|
| `ui` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | .12 | .375946044921875 | -19.991687666366516 | 966.8966593379727 |
| `ui_alt` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | .16 | .31878662109375 | -20.525534144496497 | 1423.1532540422852 |
| `ui_third` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | .20 | .375946044921875 | -22.20695387316763 | 966.7216217320357 |
| `impact` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | .32 | .80877685546875 | -20.40218668053459 | 10843.127202979935 |
| `impact_alt` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | .32 | .75616455078125 | -17.32957040921516 | 473.79153568100764 |
| `impact_third` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | .40 | .45611572265625 | -20.84958464133168 | 6838.143302962279 |
| `movement` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | .24 | .53948974609375 | -23.779940832329185 | 11934.484045946316 |
| `movement_alt` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | .36 | .639312744140625 | -21.987315616484317 | 12024.214879348818 |
| `movement_third` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | .30 | .489501953125 | -14.025186267550422 | 4553.583280111138 |
| `ambience` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | .174591064453125 | -18.153351293681563 | 36.61640767851373 |
| `ambience_alt` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | .199737548828125 | -17.67032381358842 | 58.01919713436623 |
| `ambience_third` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | .225006103515625 | -16.92261930553234 | 112.03210352691181 |
| `stem` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | .32379150390625 | -14.881434973008286 | 272.6756827789141 |
| `stem_sections` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | .17236328125 | -23.066521225821248 | 201.87069023000652 |
| `stem_layer` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | .05999755859375 | -30.28756654598196 | 190.1433267529918 |
| `stem_layer_alt` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | .04998779296875 | -31.667277345674258 | 277.9513846028647 |
| `stem_layer_third` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | .04998779296875 | -31.66724765274306 | 287.93805923844434 |

The five generic `_alt` comparisons carried forward all passed: `ui→ui_alt` duration delta .04000000000000001 s / relative centroid delta .47187731004956435; `impact→impact_alt` 0 / .9563048992406177; `movement→movement_alt` .12 / .007518618572621081; `ambience→ambience_alt` 0 / .5845136323520758; `stem_layer→stem_layer_alt` 0 / .46179931396667484. Four family groups (UI, impact, movement, ambience), two third-variant comparisons each, also carried forward as passing; not rerun here.

Thresholds carried forward unchanged: 48 kHz mono PCM16; duration tolerance ±.001 s; peak <.95 FS; RMS >=.001 FS; canonical centroid bands (UI 250–4000 Hz); loop endpoint delta <=.03 FS; outer slope mismatch <=.001 FS/sample; section contrast >=6 dB with component amplitude >=.01 FS and section RMS >=.001 FS; internal join gap <=.03 FS and slope mismatch <=.001 FS/sample; distinctness duration delta >=.020 s OR relative centroid delta >=.10. No threshold changed in this guard.

R43 fresh non-author replay baseline was 46 commands, 19 exit 0 / 27 expected fixture-validation exit 1; its prior44 subset was 18/26. R42 corrected fresh replay was 44 commands, 18/26; its prior42 subset 17/25. These counts are historical and not new replay evidence. The prior46 sequence includes the existing probe modes and invalid fixture checks; required R44 non-author replay should freshly rerun it plus the two new candidates and verify restoration.

Eight invalid fixture outcomes carried forward from R43 replay: `short_sections` expected section-count failure; `corrupt` expected decode failure; `wrong_format` expected format failure; `odd_sections` expected section-count failure; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, `mono441_probe` expected format failures. These expected fixture validation statuses are not setup errors.

## Commands, exits, and error classification

This guard did not invoke the runner CLI or a standalone shell `ffprobe`; it called the helper through shell Python commands below. `ffprobe` is called internally by the helper, returned successfully for both WAVs, and supplied the durations above.

1. Exact command: `python3 -c "import importlib.util,json; p='.shokunin/audio/corpus/fixtures/measure_audio.py'; s=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); [print(json.dumps(m.measure('ui',m.SPECS['ui'],'.shokunin/audio/corpus/live/round-44/executor/'+f),sort_keys=True)) for f in ['pass-5807.wav','fail-5809.wav']]"` — exit **1**. Setup/API error: passed strings where helper expects a `Path` (`AttributeError: 'str' object has no attribute 'relative_to'`); not a fit result.
2. Exact command: `python3 -c "import importlib.util,json; from pathlib import Path; p='.shokunin/audio/corpus/fixtures/measure_audio.py'; s=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); [print(json.dumps(m.measure('ui',m.SPECS['ui'],Path('.shokunin/audio/corpus/live/round-44/executor')/f),sort_keys=True)) for f in ['pass-5807.wav','fail-5809.wav']]"` — exit **1**. Setup/path error: relative path was outside helper `ROOT` for its receipt field (`ValueError`); not a fit result.
3. Exact command: `python3 -c "import importlib.util,json; from pathlib import Path; p='.shokunin/audio/corpus/fixtures/measure_audio.py'; s=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); [print(json.dumps(m.measure('ui',m.SPECS['ui'],Path('.shokunin/audio/corpus/live/round-44/executor').resolve()/f),sort_keys=True)) for f in ['pass-5807.wav','fail-5809.wav']]"` — exit **0**. Both measurements printed; only 5,809 failed numerically, and only on declared duration tolerance.

Thus the two initial exits are tooling setup mistakes, distinct from the single expected numeric failed fit. There were no failed candidate fits beyond the intended duration failure and no generation errors observed in this guard.

## Limits

Numerical fixture calibration only. No audition, quality, production, rights, engine, publishing, promotion, or threshold inference. No shared source or canonical files changed, no commit/push; restoration and full replay remain for the declared verifier.
