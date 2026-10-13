# R59 guard — prior battery, canonical baseline, and scratch pair audit

## Scope and disposition

Read `/tmp/mission-audio-standing.md`, the R59 declaration in `.shokunin/audio/LOG.md`, R58 source/report evidence, and available R59 scratch. This is a **read-only guard** of prior evidence and scratch candidates—not a runner replay or integration claim. I wrote only this report. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.

## R59 candidate observations (scratch only)

Executor scratch generator command:

```sh
python3 ".shokunin/audio/corpus/live/round-59/executor/generate.py"
```

Exit **0**. It generated 11,588-byte mono WAVs with 11,520-byte/5,760-sample identical signed16 payload, SHA-256 `88cac2a0475a0fdbedc4be3758a2215b3937219f13a5c8ff0515a10f1e09ccd1`; samples range `-21624..21616` and all are divisible by eight. RIFF files:

| Scratch file | WAV SHA-256 | Valid bits | Payload SHA-256 |
|---|---|---:|---|
| `executor/valid-13.wav` | `873485d5dd0d5108f0523ab974cbba6ce792e715861d481db0ad68ea35f2f2e0` | 13 | `88cac2a0475a0fdbedc4be3758a2215b3937219f13a5c8ff0515a10f1e09ccd1` |
| `executor/valid-16.wav` | `c8f327e38f34125a15bfe3e490905852a228ba26436b0a3b1633a6f58a4a1f3b` | 16 | same |

Independent RIFF parsing observed for both: RIFF/WAVE, `fmt` size 40, tag `0xfffe`, mono 48,000 Hz, byte rate 96,000, block align 2, 16-bit container, `cbSize=22`, mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`, 11,520 data bytes; valid-bits field 13 versus 16. Payload bytes are identical; only the valid-bits field differs.

Exact ffprobe commands (each exit **0**):

```sh
ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels,duration -of json ".shokunin/audio/corpus/live/round-59/executor/valid-13.wav"
ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels,duration -of json ".shokunin/audio/corpus/live/round-59/executor/valid-16.wav"
```

Both reported `pcm_s16le`, `s16`, 16 bits/sample, 48,000 Hz mono, duration `0.120000`. These are decoded/container fields, not the parsed valid-bits field.

Exact SoX commands (each exit **0**):

```sh
sox ".shokunin/audio/corpus/live/round-59/executor/valid-13.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-59/executor/valid-13.f32"
sox ".shokunin/audio/corpus/live/round-59/executor/valid-16.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-59/executor/valid-16.f32"
```

Each output has 5,760 float32 samples; both SHA-256 `afb6ad28ef01a4ed9f3a9ebf4423ee7fc7324982f1ed3fd5ad2a711c6c84c3b7`; vectors compare exactly equal, max absolute difference `0.0`.

Exact unchanged project UI measurement commands (each exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-59/executor/valid-13.wav")))'
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-59/executor/valid-16.wav")))'
```

Both directly measured 5,760 samples, duration `0.12 s`, 48,000 Hz mono, `pcm_s16le`/16 bits, peak `0.659912109375`, RMS `-8.811743007017897 dBFS`, centroid `2139.5871109211243 Hz`, bandwidth `3627.575019576501 Hz`, LUFS `null`, `failures: []`. These direct scratch function results are not integrated runner receipts.

The independent alt and scout pairs were read-only parsed: each has a distinct shared-payload 13/16 pair, 5,760 frames, fmt40/tag `0xfffe`/cb22/mask `0x4`/16-bit container/PCM GUID, all payload values divisible by eight. Executor, alt, and scout SoX-f32 scratch outputs each contain 5,760 samples and compare exactly equal within their pair (max difference `0.0`). I did not use those separate signals to substitute for executor measurements or make a runner claim.

## Prior 76 receipts and canonical baseline

R58 non-author verifier `reports/round-58/r58-verifier.md` records **76 fresh serial receipts: 38 exit 0 / 38 expected validation exit 1**. It maps the prior R57 74-command replay into that battery as **36 exit 0 / 38 exit 1**, with complete JSON/command/exit matches for those mapped receipts, unique fresh receipt paths, and identical initial/final normal JSON. Its selected R58 valid14/valid16 probes both exited 0 with no measurement failures. This guard did not execute or reparse those runner receipts; it reports the existing R58 verifier’s evidence only.

I independently SHA-256 checked the current canonical `corpus/artifacts/*.wav`: **17/17 match** the R58 guard’s R57-baseline ledger. Canonical SHA and recorded normal-receipt metrics:

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

R58 verifier records five generic `_alt` distinctness comparisons; four family maps (UI, impact, movement, ambience), two comparisons each; and four section records (`stem_sections`, `stem_layer`, `stem_layer_alt`, `stem_layer_third`). Its eight invalid-battery classifications: `short_sections` section count; `corrupt` decode; `wrong_format` format; `odd_sections` section count; `native16_probe` expected pass; `native24_probe` format; `stereo48_probe` format; `mono441_probe` format.

Recorded unchanged thresholds: rate 48,000 Hz; duration tolerance ±0.001 s; peak <0.95; RMS >0.001; centroid bands UI 250–4,000 Hz, impact 50–15,000 Hz, movement 100–16,000 Hz, ambience 5–200 Hz, stem 100–2,000 Hz; loop endpoint delta ≤0.03; loop slope ≤0.001 full-scale/sample; section contrast ≥6 dB; section component amplitude ≥0.01; section RMS ≥0.001; internal-join adjacent delta ≤0.03; internal-join side-slope mismatch ≤0.001 full-scale/sample; distinctness duration delta ≥0.020 s or relative centroid delta ≥10%.

## Setup and guard boundary

The generator, ffprobe, SoX, and direct project measurement commands above succeeded. Two preliminary REPL-only scratch-inspection expressions failed before invoking any shell command (a missing NumPy alias and an incorrect await on an already-returned `BashResult`); corrected checks produced the recorded observations. These are analysis/setup mistakes, not fixture, decoder, gate, or runner failures, and produced no receipt. No runner command was attempted and no R59 receipt was produced. No R59 source diff or integrated mode was evaluated. Prior76/canonical17 and scratch metrics are reference evidence only—not evidence that R59 probes exist, were integrated, passed runner gates, or were independently replayed. Conclusions are limited to the stated constructed scratch files and local readers. No general valid-bit semantics/enforcement, precision/fidelity, WAVE/codec/decoder conformance, audibility, quality, production, rights, engine, publishing, or promotion claim.
