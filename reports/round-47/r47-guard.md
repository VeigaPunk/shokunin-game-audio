# Round 47 guard — upper-band fixture and preservation audit

## Declaration and evidence boundary

I read the Round 47 declaration in `.shokunin/audio/LOG.md`. It declares a single calibration claim: original 0.12 s / 5,760-frame, 48 kHz mono PCM16 fixtures whose **project SoX-f32 decoded whole-wave magnitude-FFT centroids** bracket the existing ordinary UI upper limit: one inside the inclusive 250–4000 Hz band just below 4000 and passing, one strictly above 4000 and failing only the spectrum check. This is an absolute per-file band check, not R29's pairwise distinctness check. I made no audition, quality, perception, production, rights, engine, publishing, or promotion inference; no exact 4000 Hz equality or causal single-variable spectral claim is made.

## Project-measured candidate WAVs

I ran the project's existing `measure_audio.py` `measure()` on the available executor WAVs using its `SPECS["ui"]` comparator. This invokes the same SoX float decode, whole-wave absolute-magnitude FFT centroid, ffprobe format/duration, and decoded peak/RMS calculation as the ordinary fixture measurement. The two intended executor candidates give the required polarity:

| Candidate | SHA-256 | Duration / format | Peak FS | RMS dBFS | Decoded centroid Hz | Failures |
|---|---|---|---:|---:|---:|---|
| `upper-below.wav` | `b04d00164fc57a97a0cdd591a589a44792d0084ba66cdc2118989183ae22fc17` | 0.12 s; 5760 frames; 48 kHz mono PCM16 | 0.279754638671875 | -18.327854015660773 | 3999.922795974407 | none |
| `upper-above.wav` | `8f6dd0411d240e46ea619c32e3c344b8c03491d860ebc6ab32b248cbd51e4383` | 0.12 s; 5760 frames; 48 kHz mono PCM16 | 0.2789306640625 | -18.32785200392649 | 4000.427101452783 | `spectrum: centroid outside fixture band` only |

Both pass 48 kHz mono PCM16, duration (±1 ms), peak <.95 and RMS >=.001 checks. Project-reported bandwidths were 486.36936100091117 Hz below and 480.73591177279206 Hz above; integrated LUFS was null for both and is not a gate. The nominal tone numbers are not the measured centroids.

Other candidate work shows why actual decoded centroid matters. Executor nominal 3950 and 4050 Hz candidates measured **3967.091051928427 Hz** and **4066.3960394571745 Hz**, respectively; this pair brackets, but is comparatively broad. 3980 measured **3996.0324472283282 Hz**, and 3983 measured **3999.922795974407 Hz** (both in band); 3984 measured **4000.427101452783 Hz** (out of band). These are measured fitting trials, not setup failures. Alternate pair measured **3998.2575908677754 Hz** below and **4000.5907358489767 Hz** above, likewise correct polarity. Other alternate trials at nominal 3800/3900/3950/4050/4100/4200 Hz were present; the displayed measurement output includes 3967.091051928427 Hz (in-band) and 4066.3960394571745 Hz (above-band), but does not map every output line back to its nominal trial here. No nominal frequency is substituted for decoded measurement.

## Command record

Exact direct measurement command (exit **0**):

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 -c "import importlib.util; from pathlib import Path; p=Path('.shokunin/audio/corpus/fixtures/measure_audio.py').resolve(); s=importlib.util.spec_from_file_location('ma',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=m.SPECS['ui']; [(print(name, m.measure(name, spec, (Path('.shokunin/audio/corpus/live/round-47/executor')/(name+'.wav')).resolve()))) for name in ('upper-below','upper-above')]"
```

I also ran this broader candidate measurement command (exit **0**); it prints each available WAV's path, decoded centroid, and project failures:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 -c "import importlib.util; from pathlib import Path; p=Path('.shokunin/audio/corpus/fixtures/measure_audio.py').resolve(); s=importlib.util.spec_from_file_location('ma',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=m.SPECS['ui']; files=sorted(Path('.shokunin/audio/corpus/live/round-47').rglob('*.wav')); [(print(str(f), m.measure(f.stem, spec, f.resolve())['spectral_centroid_hz'], m.measure(f.stem, spec, f.resolve())['failures'])) for f in files]"
```

An initial version used a relative WAV path and exited **1** because `measure()` returns `path.relative_to(ROOT)` and the path was not under the fixture corpus root. Exact command (setup/path error, not a numeric fit or gate outcome):

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 -c "import importlib.util; from pathlib import Path; p=Path('.shokunin/audio/corpus/fixtures/measure_audio.py'); s=importlib.util.spec_from_file_location('ma',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=m.SPECS['ui']; [(print(name, m.measure(name, spec, Path('.shokunin/audio/corpus/live/round-47/executor')/(name+'.wav')))) for name in ('upper-below','upper-above')]"
```

I ran no serial fixture-runner command, so this guard supplies no runner exits. Numeric candidates that land on the same side of 4000 are failed **bracket fits**, distinct from the corrected Python path setup error. I found no report transcription correction to make.

## Preserved prior evidence (historical, not re-run here)

The Round 46 named non-author verifier documents **52 fresh serial invocations: 22 exit 0 / 30 expected fixture-validation exit 1**; its prior-50 subset is **21/29**. The first/final normal receipts were equal JSON with 17 canonical measurements and no failures; no replay setup failures were reported. This is the Round 46 lower-250 bracket replay baseline (Round 47's declared next replay is 54 commands). The Round 46 evidence is historical here, not a Round 47 replay.

The following old17 canonical SHA/metrics are carried forward from the Round 46 guard's historical R45 verifier transcription; I did not independently hash/re-measure the canonical artifacts:

| Canonical | SHA-256 | Duration (s) | Rate | Ch | Encoding | Peak FS | RMS | Centroid Hz | Failures |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| `ui` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 | 48000 | 1 | pcm_s16le/16 | 0.375946044921875 | -19.991687666366516 dBFS | 966.8966593379727 | none |
| `ui_alt` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 | 48000 | 1 | pcm_s16le/16 | 0.31878662109375 | -20.525534144496497 dBFS | 1423.1532540422852 | none |
| `ui_third` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.2 | 48000 | 1 | pcm_s16le/16 | 0.375946044921875 | -22.20695387316763 dBFS | 966.7216217320357 | none |
| `impact` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 | 48000 | 1 | pcm_s16le/16 | 0.80877685546875 | -20.40218668053459 dBFS | 10843.127202979935 | none |
| `impact_alt` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 | 48000 | 1 | pcm_s16le/16 | 0.75616455078125 | -17.32957040921516 dBFS | 473.79153568100764 | none |
| `impact_third` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.4 | 48000 | 1 | pcm_s16le/16 | 0.45611572265625 | -20.84958464133168 dBFS | 6838.143302962279 | none |
| `movement` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 | 48000 | 1 | pcm_s16le/16 | 0.53948974609375 | -23.779940832329185 dBFS | 11934.484045946316 | none |
| `movement_alt` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 | 48000 | 1 | pcm_s16le/16 | 0.639312744140625 | -21.987315616484317 dBFS | 12024.214879348818 | none |
| `movement_third` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.3 | 48000 | 1 | pcm_s16le/16 | 0.489501953125 | -14.025186267550422 dBFS | 4553.583280111138 | none |
| `ambience` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.174591064453125 | -18.153351293681563 dBFS | 36.61640767851373 | none |
| `ambience_alt` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.199737548828125 | -17.67032381358842 dBFS | 58.01919713436623 | none |
| `ambience_third` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.225006103515625 | -16.92261930553234 dBFS | 112.03210352691181 | none |
| `stem` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.32379150390625 | -14.881434973008286 dBFS | 272.6756827789141 | none |
| `stem_sections` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.17236328125 | -23.066521225821248 dBFS | 201.87069023000652 | none |
| `stem_layer` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.05999755859375 | -30.28756654598196 dBFS | 190.1433267529918 | none |
| `stem_layer_alt` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.04998779296875 | -31.667277345674258 dBFS | 277.9513846028647 | none |
| `stem_layer_third` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.04998779296875 | -31.66724765274306 dBFS | 287.93805923844434 | none |

Five generic `_alt` comparisons historically passed: UI duration delta 0.04000000000000001 s / relative centroid delta 0.47187731004956435; impact 0 s / 0.9563048992406177; movement 0.12 s / 0.007518618572621081; ambience 0 s / 0.5845136323520758; stem_layer 0 s / 0.46179931396667484. Four family groups (UI, impact, movement, ambience), eight third-variant comparisons, historically passed. These are preserved baseline claims, not retested by this guard.

Thresholds/sections carried forward unchanged: 48 kHz mono PCM16; duration tolerance ±.001 s; peak <.95 FS; RMS >=.001 FS; UI centroid inclusive 250–4000 Hz; loop endpoint delta <=.03 FS and outer slope mismatch <=.001 FS/sample; section contrast >=6 dB, component amplitude >=.01 FS, section RMS >=.001 FS; internal section join gap <=.03 FS and slope mismatch <=.001 FS/sample; distinctness duration delta >=.020 s OR relative centroid delta >=.10.

Eight invalid-probe outcomes carried forward: `short_sections` section-count failure; `corrupt` decode failure; `wrong_format` format failure; `odd_sections` section-count failure; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` format failures. These are expected validation results, not setup errors.

## Scope

I wrote only `.shokunin/audio/reports/round-47/r47-guard.md`. No source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push. The conclusions are limited to numerical fixture calibration and the stated historical preservation evidence.
