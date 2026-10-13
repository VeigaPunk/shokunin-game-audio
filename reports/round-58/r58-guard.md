# R58 guard — prior battery, canonical baseline, and scratch pair audit

## Scope and disposition

Read `/tmp/mission-audio-standing.md`, the R58 declaration in `.shokunin/audio/LOG.md`, R57 source/report evidence, and the available R58 scratch. This is a **read-only guard** of the prior baseline and scratch candidates, not an integrated runner replay or an integration claim. I did not run the project runner or alter shared source, LOG, SCORECARD, canonical artifacts, or other reports. I wrote only this report. Executor scratch originals remain under `corpus/live/round-58/executor/`; no commit or push.

## R58 candidate observations (scratch only)

The executor generator was run as:

```sh
python3 ".shokunin/audio/corpus/live/round-58/executor/generate.py"
```

Exit **0**. It generated two 11,588-byte files, with 11,520-byte identical payload SHA-256 `0b40e3c0f28aa6a50937f87c0fa260b2100f97572dbc8fdf517cea981e79b4fc`. Header/WAV SHA details:

| Scratch file | WAV SHA-256 | Header valid bits | Payload SHA-256 |
|---|---|---:|---|
| executor/valid-14.wav | `6b4b07d1eee022f99116a043b444821914acc68110544a644ba7204f3a63fb26` | 14 | `0b40e3c0f28aa6a50937f87c0fa260b2100f97572dbc8fdf517cea981e79b4fc` |
| executor/valid-16.wav | `738263969d226d31a0525bbad1c7dda8609b270dd3ec8fa82645905d4667a7f2` | 16 | `0b40e3c0f28aa6a50937f87c0fa260b2100f97572dbc8fdf517cea981e79b4fc` |

I parsed RIFF fields independently: both RIFF/WAVE, `fmt` size 40, tag `0xfffe`, mono 48,000 Hz, block align 2, 16-bit container, `cbSize=22`, mask `0x4`, PCM subtype GUID bytes `0100000000001000800000aa00389b71`; valid bits differ 14 versus 16, and all shared executor signed samples are divisible by four. The declared difference and payload match the R58 candidate shape.

Exact ffprobe commands per executor file (both exit **0**):

```sh
ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels,duration -of json ".shokunin/audio/corpus/live/round-58/executor/valid-14.wav"
ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels,duration -of json ".shokunin/audio/corpus/live/round-58/executor/valid-16.wav"
```

Both report `pcm_s16le`, `s16`, 16 bits/sample, 48,000 Hz, one channel, duration `0.120000`. These are decoded/container fields, not the parsed WAVE valid-bit field.

Exact SoX commands per executor file (both exit **0**):

```sh
sox ".shokunin/audio/corpus/live/round-58/executor/valid-14.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-58/executor/valid-14.f32"
sox ".shokunin/audio/corpus/live/round-58/executor/valid-16.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-58/executor/valid-16.f32"
```

Each decoded to 5,760 float32 samples; SHA-256 for each output is `ca42332f650f6e2361ebd56649629322a85bb3d72d03e2b2861a112c36915aa8`. Vectors are elementwise equal, maximum absolute difference `0.0`.

The unchanged project UI measurement function was run separately on each executor file (both exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-58/executor/valid-14.wav")))'
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-58/executor/valid-16.wav")))'
```

Both report 5,760 samples, duration `0.12 s`, 48,000 Hz mono, `pcm_s16le`/16 bits, peak `0.3153076171875`, RMS `-14.629479252569332 dBFS`, centroid `1129.9910331085607 Hz`, bandwidth `412.58546294347246 Hz`, LUFS `null`, and `failures: []`. These are direct scratch function results only—not runner receipts or evidence of integrated opt-in modes.

Available independent `alt/valid14.wav` and `alt/valid16.wav` were also parsed: 11,588 bytes each; fmt40, tag `0xfffe`, `cbSize22`, mask `0x4`, 16-bit container, PCM GUID above; valid14/16 respectively. They share payload SHA `501477dbee28e2f9380a8d5027b379020d7e87801946657079399a06310443f5`, and alt WAV SHA values are `c56dd1946015796b3d96e2b699899682a773a6e3daa4084b5b16cde81ebd1a89` and `2bc6d22183197478bf56d36ed7bf7fd715d1e6932a5a59d253f79083432cbee1`. ffprobe exited 0 for both and reported the same `pcm_s16le`/s16/16-bit mono48k/0.120000 fields. SoX exited 0 for both, 5,760 samples each, hash `8a8d20cfa2ab30a4dbe3415e78363c63cd1ba90374318e23e6232f0eb79fa470`, elementwise equal, max absolute difference 0. I did not run the project measurement function on alt; I do not infer its project-gate outcome. Scout scratch similarly has a valid14/16 matched pair, but its payload is a separate signal; it is not integrated or used to substitute for executor/alt evidence.

The successful scratch checks observed no decoder rejection, differing decoded vector, or numeric UI failure for executor. This is limited to these exact matched files and this host/tool path. It does not establish general 14-valid-bit handling, standards conformance, metadata enforcement, fidelity, audibility, production suitability, rights, engine behavior, or promotion.

## Prior 74 receipts and baseline audit

R57 non-author verifier recorded 74 fresh serial commands: **36 exit 0 / 38 expected validation exit 1**, including its selected valid-15/16 pair probes. It reports the prior72 exact full-JSON subset as **34/38**, all fresh paths unique, and normal first/final receipts equal. This guard did not rerun the R57 runner battery and does not claim a new 76-command replay or any R58 receipt.

I independently recomputed SHA-256 for all 17 current `corpus/artifacts/*.wav` files; **17/17 match the R57 verifier's canonical ledger**. The baseline SHA and normal-receipt metrics recorded by the prior guard are:

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

The R57 verifier reports five generic `_alt` distinctness comparisons; four family maps (UI, impact, movement, ambience), two comparisons each; and four section records (`stem_sections`, `stem_layer`, `stem_layer_alt`, `stem_layer_third`). Its eight invalid-battery classifications remain: `short_sections` section count; `corrupt` decode; `wrong_format` format; `odd_sections` section count; `native16_probe` expected pass; `native24_probe` format; `stereo48_probe` format; `mono441_probe` format.

Unchanged thresholds recorded by the prior verifier: sample rate 48,000 Hz; duration tolerance ±0.001 s; peak <0.95; RMS ≥0.001; centroid bands UI 250–4,000 Hz, impact 50–15,000 Hz, movement 100–16,000 Hz, ambience 5–200 Hz, stem 100–2,000 Hz; loop endpoint delta ≤0.03; loop slope ≤0.001 full-scale/sample; section contrast ≥6 dB; section component amplitude ≥0.01; section RMS ≥0.001; internal-join adjacent delta ≤0.03; internal-join side-slope mismatch ≤0.001 full-scale/sample; distinctness requires duration delta ≥0.020 s or relative centroid delta ≥10% per battery predicate.

## Guard boundary

No R58 integration/source diff was evaluated and no runner receipt was produced by this guard. Prior74/ canonical17/metrics and unchanged battery structure are reference evidence only, not a new R58 replay. Do not infer that the R58 candidate has been selected or integrated, that opt-in modes exist, or that a **76-command** replay occurred. All numeric observations above are scratch-only; no new integration, calibration/admission, decoder-generalization, fidelity/audibility, production, rights, engine, publishing, or promotion claim.
