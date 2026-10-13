# Round 49 guard — upper adjacent-rate fixture and preservation audit

## Declaration and scope

I read the Round 49 declaration in `.shokunin/audio/LOG.md`. It specifies one numerical calibration comparison: original deterministic 5,760-frame mono PCM16 UI-shaped WAVs tagged 48,001 Hz and 48,000 Hz, target UI duration .12 s within ±.001 s, peak <.95 FS, RMS >=.001 FS, whole-wave SoX-f32 centroid 250–4,000 Hz. Expected result: 48,001 exits 1 with sole `format: expected 48kHz mono`; 48,000 exits 0 with no failures. Preserve the exact format comparator and existing checks.

This is a fixture-local numerical gate test only. No audition or inference about quality, perception, production, rights, engine behavior, publishing or promotion; no general-rate, resampling or converter claim. Historical material below is clearly identified as carried forward, not newly re-run by this guard.

## Candidate pair measurements

The executor scratch generator uses `n=5760`, creates one PCM16 sample sequence from `t=np.arange(n)/48000`, and writes the sequence with the selected WAV header rate. Both project-measured candidates are mono `pcm_s16le`, `s16`, 16-bit. Their files have the same 11,520-byte PCM payload; SoX-decoded float32 files are identical (23,040 bytes, SHA-256 `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f`). The container headers differ.

| Candidate | WAV SHA-256 | Frames | ffprobe rate / channels / codec / sample_fmt / bits | ffprobe duration | Project peak FS | Project RMS dBFS | Project SoX-f32 centroid | Project failures |
|---|---|---:|---|---:|---:|---:|---:|---|
| 48,001 Hz | `92b22d8749c5f02d4f68d9a8daa32b935404f1d7cdbc31bca55af2f9adf4cb5a` | 5760 | 48001 / 1 / pcm_s16le / s16 / 16 | .119998 s | .27996826171875 | -18.327858226717105 | 1022.557447787877 Hz | `format: expected 48kHz mono` only |
| 48,000 Hz | `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c` | 5760 | 48000 / 1 / pcm_s16le / s16 / 16 | .120000 s | .27996826171875 | -18.327858226717105 | 1022.536144951523 Hz | none |

Both pass UI duration ±.001 s, peak <.95, RMS >=.001 and centroid [250,4000] Hz. The format outcome differs only because exact integer rate is checked. The rate metadata affects duration and FFT frequency axis; identical samples do not represent a claim of identical physical-time signals.

## Exact commands and exits

I ran this exact ffprobe command from the repository root; exit **0**, with the actual JSON metadata summarized above:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && for f in .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav; do printf "%s\n" "$f"; ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_fmt,sample_rate,channels,bits_per_sample,duration,nb_frames -show_entries format=duration -of json "$f"; done
```

I ran the project's existing measurement function on both original scratch WAVs; command exit **0**. The returned measurements and per-file failure arrays are transcribed above:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve(); s=importlib.util.spec_from_file_location("ma",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=m.SPECS["ui"]; [(print(name, m.measure(name, spec, (Path(".shokunin/audio/corpus/live/round-49/executor")/(name+".wav")).resolve()))) for name in ("ui-48001","ui-48000")]'
```

No command/setup errors, numeric fit failures beyond the declared 48,001-Hz format failure, or report transcription corrections were found in this guard check. These are direct scratch measurements, not fresh runner receipts; I did not run the 58-command replay.

## Historical baseline and preservation checks (carried forward)

**Old canonical 17 SHA/metrics:** the following table is carried forward from Round 48 guard's R47 baseline transcription; I did not independently hash or re-measure these canonical files in this task. Round 48 verifier separately reported that all 17 current canonical WAV hashes matched that baseline and first/final normal JSON agreed.

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


**Prior replay baseline:** Round 48's named non-author verifier reports 56 fresh serial runner invocations, 56 distinct new receipts, **24 exit 0 / 32 expected fixture-validation exit 1**, no setup failures. Its prior-54 subset was 23/31. The new rate commands in that replay were:

| Exact command | Exit | Outcome | Receipt |
|---|---:|---|---|
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-47999` | 1 | sole `format: expected 48kHz mono` | `.shokunin/audio/corpus/live/runs/20261013T073438393360Z-ui-rate-47999/measurements.json` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000` | 0 | no failures | `.shokunin/audio/corpus/live/runs/20261013T073439440343Z-ui-rate-48000/measurements.json` |

Those are the Round 48 below-rate probe receipts and their command names, not Round 49 replay results. Round 48's full 56-command ledger and replay evidence remain in `.shokunin/audio/reports/round-48/r48-verifier.md`.

The Round 48 below-rate replay also documented normal restoration: initial and final normal receipts had identical JSON for all 17 canonical measurements, with no failures. This is a prior verifier result, not restoration run by this guard.

**Existing checks carried forward unchanged:** five generic `_alt` comparisons: UI, impact, movement, ambience, and stem_layer. Four family groups/eight third-variant comparisons: UI, impact, movement, ambience. Historical reported comparisons passed. Thresholds: exact 48,000-Hz mono PCM16; duration ±.001 s; peak <.95 FS; RMS >=.001 FS; fixture-specific whole-wave centroid bands (UI 250–4,000, impact 50–15,000, movement 100–16,000, ambience 5–200, stems 100–2,000 Hz); loop endpoint jump <=.03 FS and outer slope mismatch <=.001 FS/sample; distinctness duration delta >=.020 s **or** relative centroid delta >=.10; section validity requires exact 192,000 samples, two 96,000-sample sections, 30-Hz amplitudes >=.01 FS and section RMS >=.001 FS; section contrast >=6 dB; internal section join gap <=.03 FS and slope mismatch <=.001 FS/sample.

Eight prior invalid-fixture outcomes: `short_sections` section-count failure; `corrupt` decode failure; `wrong_format` format failure; `odd_sections` section-count failure; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` format failures. These are fixture-validation outcomes, not setup errors. These preservation checks, thresholds and invalid cases were not re-run by this guard.

## Scope / boundaries

I wrote only `.shokunin/audio/reports/round-49/r49-guard.md`. No shared source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push. No quality, perception, production, rights, engine, publishing, or promotion inference is made.
