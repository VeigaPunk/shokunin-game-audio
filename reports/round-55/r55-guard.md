# R55 guard — prior battery and canonical preservation audit

## Scope and verdict

This is a bounded pre-integration guard audit, not a runner-verification report and not a claim that R55 has a new integrated mode. I read the standing brief, R55 LOG declaration, R54 source context, R54 verifier/adjudicator reports, and the available R55 scratch reports. The R55 declaration is a positive header-representation control: conventional PCM tag 1 versus one specific WAVE_FORMAT_EXTENSIBLE PCM16 header. It does not justify a universal extensible-WAV claim.

At inspection, the fixture builder and runner still expose the R54 `--probe-ui-pcm32` / `--probe-ui-pcm16-r54` probes; no R55 flags or integrated runner receipts were available. I therefore make **no new-mode, source-integration, 70-command replay, or gate-admission claim**. This report makes no shared-source edit.

## R54 historical battery preservation baseline

I checked the R54 verifier's 68-row serial ledger and its receipt files. All 68 referenced JSON receipts exist and have distinct paths. The verifier reports 30 exit-0 receipts and 38 exit-1 validation receipts; the prior R53 battery subset is 66 exact full-JSON matches (29/37), at rows 1 and 4–68. R54's first and final normal receipts are equal, each with all 17 canonical measurements and no failures. These are historical R54 verifier results, not a replay performed by this guard.

The preserved baseline recorded there contains five generic `_alt` distinctness comparisons; four family maps (UI, impact, movement, ambience), each with two comparisons; and the four section records for the stem-section and three stem-layer checks. The unchanged thresholds are 48 kHz; duration ±0.001 s; peak <0.95; RMS >=0.001; centroid within each fixture band; loop endpoint delta <=0.03; loop slope <=0.001 full scale/sample; section contrast >=6 dB; internal-join adjacent delta <=0.03; and internal-join side-slope mismatch <=0.001 full scale/sample.

The eight invalid-probe classifications in the preserved R54 receipt are: `short_sections`—section count; `corrupt`—decode; `wrong_format`—format; `odd_sections`—section count; `native16_probe`—pass; `native24_probe`—format; `stereo48_probe`—format; `mono441_probe`—format. In particular, historical `native24_probe` is PCM24 (`pcm_s24le`, 24 bits), not PCM32 or a test of R55 extensible PCM16.

## Canonical 17 audit

I independently SHA-256 checked the 17 files in `corpus/artifacts/`; hashes match the R54 verifier's table. The table below records its clean-normal metrics (duration, peak, RMS dBFS, centroid). The clean normal receipts reported by the verifier retain these same canonical measurements.

| Fixture | SHA-256 | Duration s | Peak FS | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---:|
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 | 0.375946044921875 | -19.991687666366516 | 966.8966593379727 |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 | 0.31878662109375 | -20.525534144496497 | 1423.1532540422852 |
| `ui_third.wav` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.2 | 0.375946044921875 | -22.20695387316763 | 966.7216217320357 |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 | 0.80877685546875 | -20.40218668053459 | 10843.127202979935 |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 | 0.75616455078125 | -17.32957040921516 | 473.79153568100764 |
| `impact_third.wav` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.4 | 0.45611572265625 | -20.84958464133168 | 6838.143302962279 |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 | 0.53948974609375 | -23.779940832329185 | 11934.484045946316 |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 | 0.639312744140625 | -21.987315616484317 | 12024.214879348818 |
| `movement_third.wav` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.3 | 0.489501953125 | -14.025186267550422 | 4553.583280111138 |
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | 0.174591064453125 | -18.153351293681563 | 36.61640767851373 |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | 0.199737548828125 | -17.67032381358842 | 58.01919713436623 |
| `ambience_third.wav` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | 0.225006103515625 | -16.92261930553234 | 112.03210352691181 |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | 0.32379150390625 | -14.881434973008286 | 272.6756827789141 |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | 0.17236328125 | -23.066521225821248 | 201.87069023000652 |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | 0.05999755859375 | -30.28756654598196 | 190.1433267529918 |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 0.04998779296875 | -31.667277345674258 | 277.9513846028647 |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 0.04998779296875 | -31.66724765274306 | 287.93805923844434 |

## R55 scratch-only positive control observations

The executor's original WAV pair is scratch under `corpus/live/round-55/executor/`, not an integrated probe. For this pair I ran the following metadata/decode commands (both ffprobe and SoX invocations exited 0; `cmp` exited 0):

```sh
for f in .shokunin/audio/corpus/live/round-55/executor/pcm16-tag1.wav .shokunin/audio/corpus/live/round-55/executor/extensible-40.wav; do
  ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels,duration -of json "$f"
  sox "$f" -t f32 -e floating-point -b 32 "/tmp/$(basename "$f").f32"
done
cmp -s /tmp/pcm16-tag1.wav.f32 /tmp/extensible-40.wav.f32
```

Both report `pcm_s16le`, `s16`, 16 bits, 48,000 Hz, mono, `.120000` s. The decoded vectors compare byte-identically; decoded SHA-256 is `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7`. The two executor WAV hashes are standard `9ac26f38a7df9b1dd60c6130049d1e37056811fcd241f15a03559b5766bb4ba9` and extensible `bd7d95901935c0effe21fd64e44a474e44a47487372fd91c1713679d0e7f5ba7f629c0`.

From the decoded samples I independently calculated peak `.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293338 Hz`, and bandwidth `276.1544498122306 Hz`. Both the R55 executor report and critic report record successful project `measure()` calls on their matching scratch pair with these UI metrics and no failures; those reports are corroborating scratch-only observations, not this guard running `measure()` or an integrated runner result. The measurements fit the unchanged UI numeric bounds and metadata predicate for this constructed payload/header only. These checks do not verify the proposed 70-command replay.

## Limits

The R54 baseline review is bounded to its logged verifier evidence and existing canonical files. This guard did not edit shared source, LOG, SCORECARD, canonical files, or another report; no commit or push was made. No claim is made about universal WAVE_FORMAT_EXTENSIBLE support, other masks/subtypes/valid-bit layouts, generic fidelity, audibility, quality, production, rights, engine behavior, publishing, or promotion.
