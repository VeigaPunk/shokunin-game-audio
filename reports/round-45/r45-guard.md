# Round 45 guard — prior baseline and preservation audit

## Scope and declaration

I read the Round 45 declaration in `.shokunin/audio/LOG.md`. It specifies one numerical calibration: negative-side UI duration controls at 5,713 and 5,711 frames against the unchanged `.12 s` target and strict `abs(ffprobe_duration - .12) > .001` check. Ideal signed deltas are -47/48000 = -0.0009791666666666666 s (pass) and -49/48000 = -0.0010208333333333334 s (fail); these are arithmetic, not measured ffprobe results. This guard did not generate or measure R45 candidates, so it cannot attest actual duration, deltas, hashes, or numeric fit. No audition or quality judgment.

## Preserved baseline context (historical, not rerun by this guard)

R44's named non-author verifier (`reports/round-44/r44-verifier.md`) recorded **48 fresh serial runner invocations: 20 exit 0 / 28 expected fixture-validation exit 1**, no replay setup errors; its prior-46 subset was 19/27. This is the required prior-48-mode baseline for R45, not a replay performed here. The R44 verifier reported clean-before `8009269ade6fff69c95de3cbde6a2cd653c33dc9`, canonical artifact bytes unchanged, and first/final normal receipt JSON equal (17 canonical measurements, no failures). Its final normal receipt was `corpus/live/runs/20261013T060556451471Z-normal/measurements.json`.

Old 17 canonical SHA/metrics, carried forward from that verifier (not measured by this guard):

| Canonical | SHA-256 | Duration (s) | Rate | Ch | Encoding | Peak FS | RMS | Centroid | Ordinary failures |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| `ui` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 | 48000 | 1 | pcm_s16le/16 | 0.375946044921875 | -19.991687666366516 dBFS | 966.8966593379727 Hz | none |
| `ui_alt` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 | 48000 | 1 | pcm_s16le/16 | 0.31878662109375 | -20.525534144496497 dBFS | 1423.1532540422852 Hz | none |
| `ui_third` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.2 | 48000 | 1 | pcm_s16le/16 | 0.375946044921875 | -22.20695387316763 dBFS | 966.7216217320357 Hz | none |
| `impact` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 | 48000 | 1 | pcm_s16le/16 | 0.80877685546875 | -20.40218668053459 dBFS | 10843.127202979935 Hz | none |
| `impact_alt` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 | 48000 | 1 | pcm_s16le/16 | 0.75616455078125 | -17.32957040921516 dBFS | 473.79153568100764 Hz | none |
| `impact_third` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.4 | 48000 | 1 | pcm_s16le/16 | 0.45611572265625 | -20.84958464133168 dBFS | 6838.143302962279 Hz | none |
| `movement` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 | 48000 | 1 | pcm_s16le/16 | 0.53948974609375 | -23.779940832329185 dBFS | 11934.484045946316 Hz | none |
| `movement_alt` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 | 48000 | 1 | pcm_s16le/16 | 0.639312744140625 | -21.987315616484317 dBFS | 12024.214879348818 Hz | none |
| `movement_third` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.3 | 48000 | 1 | pcm_s16le/16 | 0.489501953125 | -14.025186267550422 dBFS | 4553.583280111138 Hz | none |
| `ambience` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.174591064453125 | -18.153351293681563 dBFS | 36.61640767851373 Hz | none |
| `ambience_alt` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.199737548828125 | -17.67032381358842 dBFS | 58.01919713436623 Hz | none |
| `ambience_third` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.225006103515625 | -16.92261930553234 dBFS | 112.03210352691181 Hz | none |
| `stem` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.32379150390625 | -14.881434973008286 dBFS | 272.6756827789141 Hz | none |
| `stem_sections` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.17236328125 | -23.066521225821248 dBFS | 201.87069023000652 Hz | none |
| `stem_layer` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.05999755859375 | -30.28756654598196 dBFS | 190.1433267529918 Hz | none |
| `stem_layer_alt` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.04998779296875 | -31.667277345674258 dBFS | 277.9513846028647 Hz | none |
| `stem_layer_third` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.04998779296875 | -31.66724765274306 dBFS | 287.93805923844434 Hz | none |





The five generic `_alt` comparisons were all recorded passing: UI 0.04000000000000001 s / centroid-relative 0.47187731004956435; impact 0 / 0.9563048992406177; movement 0.12 / 0.007518618572621081; ambience 0 / 0.5845136323520758; stem_layer 0 / 0.46179931396667484. Four family groups (UI, impact, movement, ambience), eight third-variant comparisons total, were recorded passing. These outcomes and metrics are carried forward, not independently retested here.

Thresholds carried forward unchanged: 48 kHz mono PCM16; ordinary duration tolerance ±.001 s; peak <.95 FS; RMS >=.001 FS; UI centroid 250–4000 Hz; loop endpoint delta <=.03 FS and outer slope mismatch <=.001 FS/sample; section contrast >=6 dB, component amplitude >=.01 FS, section RMS >=.001 FS; internal section join gap <=.03 FS and slope mismatch <=.001 FS/sample; distinctness duration delta >=.020 s OR relative centroid delta >=.10. No threshold or comparator change was made by this guard.

The eight invalid-probe expected statuses recorded in the R44 replay were: `short_sections` section-count failure; `corrupt` decode failure; `wrong_format` format failure; `odd_sections` section-count failure; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` format failures. These are expected validation outcomes, not setup errors. R44's first and final normal runs matched and left canonical measurements restored. R45 replay/restoration is for the declared non-author verifier; this guard did not independently verify current restoration.

## Commands, exits, and error classification

Only shell command run by this guard:

- Exact command: `git status --short && find .shokunin/audio -maxdepth 4 -type f | sort | tail -60` — exit **0**. It showed `.shokunin/audio/LOG.md` modified before this report was written. It did not execute fixture generation, ffprobe, measurement, or a runner mode. All file reads and report assembly were done in the Python REPL; no numeric fit or setup error occurred.

I made no source, LOG, SCORECARD, canonical asset, or other report edits, and did not commit or push. This guard writes only `.shokunin/audio/reports/round-45/r45-guard.md`. No inference about audible/perceptual duration, quality, production, rights, engine, publishing, or promotion.
