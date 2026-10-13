# Round 50 guard — stereo-format calibration and preservation audit

## Declaration and scope

I read the Round 50 declaration in `.shokunin/audio/LOG.md`. It specifies one numerical calibration comparison: deterministic 5,760-frame stereo PCM16 at 48,000 Hz, with each channel carrying the mono control's PCM16 sequence, against that 5,760-frame mono PCM16 control. Target duration is .12 s within ±.001 s; project SoX-f32 decoded peak <.95 FS, RMS >=.001 FS, and whole-wave centroid 250–4,000 Hz for both. Expected result: stereo exits 1 with sole `format: expected 48kHz mono`; mono exits 0 with no failures, via unchanged `measure(..., SPECS["ui"])`.

This is a fixture-local numerical gate test. It does not establish channel-agnostic stereo handling, per-channel analysis, or general stereo/downmix behavior. No audition, quality, perception, production, rights, engine, publishing, or promotion inference. Historical material below is carried forward and not re-run by this guard.

## Candidate measurements

The executor scratch pair is in `.shokunin/audio/corpus/live/round-50/executor/`. Both WAVs contain 5,760 frames; the stereo file has two channels with the corresponding mono sequence in each channel. The project measurement function processes each WAV using its SoX-f32 decoded stream; the reported peak, RMS and centroid below are the actual project measurements of that decoded stream, not inferred from the source array.

| Candidate | WAV SHA-256 | Frames | ffprobe rate / channels / codec / sample_fmt / bits | ffprobe duration | Project decoded peak FS | Project decoded RMS dBFS | Project decoded whole-wave centroid | Project failures |
|---|---|---:|---|---:|---:|---:|---:|---|
| Stereo | `59e508f1b30d17eef5f00951434915bc7974e02d6988faf07a557270611e950e` | 5760 | 48000 / 2 / pcm_s16le / s16 / 16 | .120000 s | .3160400390625 | -19.902100515581505 | 2019.8445020922231 Hz | `format: expected 48kHz mono` only |
| Mono control | `93223ee4df8c027d6efaa12d9eca47af3de4fba1eba90c27f29c49ab0086a54a` | 5760 | 48000 / 1 / pcm_s16le / s16 / 16 | .120000 s | .3160400390625 | -19.902100515581505 | 1928.2134621890698 Hz | none |

Both measurements pass duration, peak, RMS and centroid bands. Stereo receives only the expected format failure; mono has no failures. The measured whole-wave centroid differs for stereo and mono; this report makes no inference about how channels are handled beyond these exact input files and project outputs.

## Exact commands and exits

From repository root, I ran this ffprobe command for both scratch WAVs; exit **0**. It reports the stream metadata and .120000 duration shown above:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && for f in .shokunin/audio/corpus/live/round-50/executor/stereo.wav .shokunin/audio/corpus/live/round-50/executor/mono.wav; do printf '%s\n' "$f"; ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_fmt,sample_rate,channels,bits_per_sample,duration,nb_frames -show_entries format=duration -of json "$f"; done
```

I ran the existing project measurement function on both original scratch WAVs; command exit **0**. The returned per-file values and failures are transcribed in the table:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve(); s=importlib.util.spec_from_file_location("ma",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=m.SPECS["ui"]; [(print(name, m.measure(name, spec, (Path(".shokunin/audio/corpus/live/round-50/executor")/(name+".wav")).resolve()))) for name in ("stereo","mono")]'
```

No setup errors, numeric fit failures beyond the expected stereo format failure, or report transcription corrections were found in these two checks. These are direct scratch-file measurements, not fresh runner receipts; this guard did not run the serial replay.

## Historical baseline and preservation checks (carried forward)

**Old canonical 17 SHA/metrics:** carried forward from the prior guard; not independently rehashed or measured here.

| Canonical | SHA-256 | Duration (s) | Rate | Ch | Encoding | Peak FS | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---|---:|---:|---:|
| `ui` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | .12 | 48000 | 1 | pcm_s16le/16 | .375946044921875 | -19.991687666366516 | 966.8966593379727 |
| `ui_alt` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | .16 | 48000 | 1 | pcm_s16le/16 | .31878662109375 | -20.525534144496497 | 1423.1532540422852 |
| `ui_third` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | .20 | 48000 | 1 | pcm_s16le/16 | .375946044921875 | -22.20695387316763 | 966.7216217320357 |
| `impact` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | .32 | 48000 | 1 | pcm_s16le/16 | .80877685546875 | -20.40218668053459 | 10843.127202979935 |
| `impact_alt` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | .32 | 48000 | 1 | pcm_s16le/16 | .75616455078125 | -17.32957040921516 | 473.79153568100764 |
| `impact_third` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | .40 | 48000 | 1 | pcm_s16le/16 | .45611572265625 | -20.84958464133168 | 6838.143302962279 |
| `movement` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | .24 | 48000 | 1 | pcm_s16le/16 | .53948974609375 | -23.779940832329185 | 11934.484045946316 |
| `movement_alt` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | .36 | 48000 | 1 | pcm_s16le/16 | .639312744140625 | -21.987315616484317 | 12024.214879348818 |
| `movement_third` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | .30 | 48000 | 1 | pcm_s16le/16 | .489501953125 | -14.025186267550422 | 4553.583280111138 |
| `ambience` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | 48000 | 1 | pcm_s16le/16 | .174591064453125 | -18.153351293681563 | 36.61640767851373 |
| `ambience_alt` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | 48000 | 1 | pcm_s16le/16 | .199737548828125 | -17.67032381358842 | 58.01919713436623 |
| `ambience_third` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | 48000 | 1 | pcm_s16le/16 | .225006103515625 | -16.92261930553234 | 112.03210352691181 |
| `stem` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | 48000 | 1 | pcm_s16le/16 | .32379150390625 | -14.881434973008286 | 272.6756827789141 |
| `stem_sections` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | 48000 | 1 | pcm_s16le/16 | .17236328125 | -23.066521225821248 | 201.87069023000652 |
| `stem_layer` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | 48000 | 1 | pcm_s16le/16 | .05999755859375 | -30.28756654598196 | 190.1433267529918 |
| `stem_layer_alt` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 48000 | 1 | pcm_s16le/16 | .04998779296875 | -31.667277345674258 | 277.9513846028647 |
| `stem_layer_third` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 48000 | 1 | pcm_s16le/16 | .04998779296875 | -31.6672476528647 | 287.93805923844434 |


**Prior replay baseline:** Round 49's named non-author verifier reports 58 fresh serial runner invocations and 58 distinct new receipts, **25 exit 0 / 33 expected fixture-validation exit 1**. The old58 comparison is represented by the prior58 baseline; the preceding Round 48 replay was 56 invocations, 24/32. Round 49 verifier separately compared its old56 subset with prior receipts. These counts are historical and are not Round 50 replay results. Round 49 discarded two wrapper-construction attempts (all attempts exit127 before Python, zero receipts); those were setup errors, not fixture gate outcomes.

Round 49 verifier reports initial and final normal JSON equal, 17 canonical measurements clean, and the old17 SHA baseline intact. These are prior verifier results, not a normal-restoration run by this guard.

**Existing checks carried forward unchanged:** five generic `_alt` comparisons (UI, impact, movement, ambience, stem_layer); four family groups/eight third-variant comparisons (UI, impact, movement, ambience). Thresholds: exact 48,000-Hz mono PCM16; duration ±.001 s; peak <.95 FS; RMS >=.001 FS; fixture-specific whole-wave centroid bands (UI 250–4,000, impact 50–15,000, movement 100–16,000, ambience 5–200, stems 100–2,000 Hz); loop endpoint jump <=.03 FS and outer slope mismatch <=.001 FS/sample; distinctness duration delta >=.020 s **or** relative centroid delta >=.10; section validity exact 192,000 samples, two 96,000-sample sections, 30-Hz amplitudes >=.01 FS and section RMS >=.001 FS; section contrast >=6 dB; internal section join gap <=.03 FS and slope mismatch <=.001 FS/sample.

Eight prior invalid-fixture outcomes: `short_sections` section-count failure; `corrupt` decode failure; `wrong_format` format failure; `odd_sections` section-count failure; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` format failures. These are fixture-validation outcomes, not setup errors. Prior58 preservation records also include the five generic/four family comparisons, thresholds, invalid cases, and normal restoration. None were re-run by this guard.

## Scope / boundaries

I wrote only `.shokunin/audio/reports/round-50/r50-guard.md`. No shared source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push. No channel-agnostic stereo handling, audition, quality, perception, production, rights, engine, publishing, or promotion inference is made.
