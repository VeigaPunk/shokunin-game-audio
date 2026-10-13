# R54 guard — preservation and fixture audit

## Result / boundary

**The bounded source-pair audit and R53-preservation review are complete; R54 integration and replay are not present in the inspected tree. This report makes no R54 integration or validation claim.** The R54 declaration calls for a matched 5,760-frame mono 48 kHz signed PCM32/PCM16 UI-shaped pair and a 68-command future serial replay. At inspection (before writing this report), `measure_audio.py` exposed no R54 PCM32 probe flag, there were no R54 runner receipts, and this report path did not yet exist. The two original executor WAVs and an alternative pair exist only in their respective `corpus/live/round-54/{executor,alt}/` scratch directories. I did not modify shared source, LOG, SCORECARD, canonical assets, or any other report.

## Original scratch pair checks

The executor generator describes a 1 kHz + 1.5 kHz, 5,760-sample, 48 kHz mono signal, quantizes to signed16, then constructs signed32 samples as `s16 * 65536`. The PCM32/PCM16 files are each 0.120 s. Exact file hashes:

| Scratch file | SHA-256 |
|---|---|
| `corpus/live/round-54/executor/pcm32.wav` | `fcbdd5aa0862fddabad017388aba24bedc9e6c98202ccbc04a40125413de47c7` |
| `corpus/live/round-54/executor/pcm16.wav` | `9ac26f38a7df9b1dd60c6130049d1e37056811fcd241f15a03559b5766bb4ba9` |

(The PCM32 hash is `fcbdd5aa0862fddabad017388aba24bedc9e6c98202ccbc04a40125413de47c7`; spacing above is typographic only.) I ran these exact commands; both exited **0**:

- `ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels,duration -of default=noprint_wrappers=1 .shokunin/audio/corpus/live/round-54/executor/pcm32.wav` → `pcm_s32le`, `s32`, 32 bits, 48000 Hz, mono, `.120000` s.
- `ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels,duration -of default=noprint_wrappers=1 .shokunin/audio/corpus/live/round-54/executor/pcm16.wav` → `pcm_s16le`, `s16`, 16 bits, 48000 Hz, mono, `.120000` s.

For each file I ran `python3 -c 'import subprocess,numpy as np,sys; p=sys.argv[1]; b=subprocess.run(["sox",p,"-t","f32","-e","floating-point","-"],capture_output=True,check=True).stdout; x=np.frombuffer(b,dtype="<f4").astype(np.float64); rate=48000; f=np.fft.rfftfreq(len(x),1/rate); a=np.abs(np.fft.rfft(x)); c=np.dot(f,a)/a.sum(); print("samples",len(x),"peak",np.max(np.abs(x)),"rms_dbfs",20*np.log10(np.sqrt(np.mean(x*x))),"centroid_hz",c,"bandwidth_hz",np.sqrt(np.dot((f-c)**2,a)/a.sum()))' <path>`; both exited **0**. Both decode to 5,760 samples with peak `0.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`. A separate exact command decoded both with SoX to f32 and compared vectors: `python3 -c 'import subprocess,numpy as np,sys; a=[];
for p in sys.argv[1:]:
 b=subprocess.run(["sox",p,"-t","f32","-e","floating-point","-"],capture_output=True,check=True).stdout; a.append(np.frombuffer(b,dtype="<f4"))
print("samples",[len(x) for x in a],"equal",np.array_equal(*a),"max_abs_difference",float(np.max(np.abs(a[0]-a[1]))))' <pcm32-path> <pcm16-path>`; exit **0**, lengths `[5760, 5760]`, exact equality, maximum absolute difference `0.0`. This is expected from the chosen grid construction and does not test extra PCM32 precision or general PCM32 handling.

An independent alternative scratch pair is materially different: candidate PCM32 SHA-256 `5cd1711de2ed2dc76fc2505a2f0584f1fd31d523994818168fba18f1cbb49b9a`, control PCM16 `37a1eb68e0a870d3b3a58e4d45d5686de12e0cb4bcabaffa15c079f50da51436`. A critic scratch pair also exists. Neither is integrated evidence or a runner replay.

## Canonical17 audit

I independently SHA-256 hashed the 17 current `corpus/artifacts/*.wav` files. Every digest matches the canonical17 table and fresh normal metrics in the R53 verifier report (`r53-verifier.md`); the same table is in R53 guard. Those metrics are **R53 verifier normal-receipt measurements**, not newly measured by this guard. R53 verifier reports first/final normal receipt equivalence and canonical hashes matching its measurement paths. Current-file hashes and reported metrics:

| Fixture | SHA-256 | Duration s | Peak FS | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---:|
| ui | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 | 0.375946044921875 | -19.991687666366516 | 966.8966593379727 |
| ui_alt | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 | 0.31878662109375 | -20.525534144496497 | 1423.1532540422852 |
| ui_third | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.20 | 0.375946044921875 | -22.20695387316763 | 966.7216217320357 |
| impact | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 | 0.80877685546875 | -20.40218668053459 | 10843.127202979935 |
| impact_alt | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 | 0.75616455078125 | -17.32957040921516 | 473.79153568100764 |
| impact_third | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.40 | 0.45611572265625 | -20.84958464133168 | 6838.143302962279 |
| movement | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 | 0.53948974609375 | -23.779940832329185 | 11934.484045946316 |
| movement_alt | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 | 0.639312744140625 | -21.987315616484317 | 12024.214879348818 |
| movement_third | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.30 | 0.489501953125 | -14.025186267550422 | 4553.583280111138 |
| ambience | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | 0.174591064453125 | -18.153351293681563 | 36.61640767851373 |
| ambience_alt | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | 0.199737548828125 | -17.67032381358842 | 58.01919713436623 |
| ambience_third | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | 0.225006103515625 | -16.92261930553234 | 112.03210352691181 |
| stem | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | 0.32379150390625 | -14.881434973008286 | 272.6756827789141 |
| stem_sections | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | 0.17236328125 | -23.066521225821248 | 201.87069023000652 |
| stem_layer | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | 0.05999755859375 | -30.28756654598196 | 190.1433267529918 |
| stem_layer_alt | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 0.04998779296875 | -31.667277345674258 | 277.9513846028647 |
| stem_layer_third | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 0.04998779296875 | -31.66724765274306 | 287.93805923844434 |

## Prior66 replay order and preserved checks

R53 `r53-verifier.md` records 66 serial commands, **29 exit 0 / 37 expected validation exit 1**. Its order is: (1) normal; (2) `--probe-ui-float32`; (3) `--probe-ui-pcm16-r53`; then (4)–(66) the complete preceding 64-command sequence. I checked that ledger ordering against the R53 report; it states the shifted prior64 raw receipt JSON objects exactly match R52’s verifier sequence, with no receipt reuse. R52’s exact prior62 subset is positions 4–66 of R53 and had 27/35 exits; R53 positions 1 and 4–66 total 28/36 for its prior64 set. R53 reports all 66 paths unique and first/final normals byte-for-byte equivalent as parsed JSON. The candidate future R54 replay should prepend the PCM32 candidate and PCM16 control to this established R53 66-command sequence, for a declared total of **68**; predicted totals would be 30 exit0 / 38 expected exit1 only if both new probes have their declared behavior. This is a projection, not observed R54 results.

Preserved generic distinctness: five `_alt` comparisons (`ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, `stem_layer_alt`). Family comparisons: four groups—UI, impact, movement, ambience—with two comparisons per family. Four section records: `stem_sections`, `stem_layer`, `stem_layer_alt`, `stem_layer_third`. Preserved thresholds: sample rate 48000 Hz; duration tolerance 0.001 s; peak `<0.95`; RMS `>=0.001`; loop endpoint delta `<=0.03`; loop slope delta `<=0.001` full scale/sample; section contrast `>=6 dB`; internal join adjacent delta `<=0.03`; internal join side slope mismatch `<=0.001` full scale/sample; section component amplitude `>=0.01`; section RMS `>=0.001`; distinctness duration delta `>=0.02 s`, centroid relative delta `>=0.1`, plus each fixture’s configured centroid band. Eight invalid-probe classifications: `short_sections` section count; `corrupt` decode; `wrong_format` format; `odd_sections` section count; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, `mono441_probe` format. R53 says normal restoration preserved these fields and first/final normal match.

## Exact inspection/command record and limitation

In Python I read the standing brief, R54 LOG declaration, R53 guard/verifier and source; checked source for an R54 flag, checked report/receipt presence, and SHA-256 hashed the 17 canonical files and R54 scratch WAVs. I ran the two `ffprobe` and two per-file SoX-stat commands and the paired SoX vector-equality command above; all five commands exited 0. I did **not** run the integrated measurement runner or replay any R54 commands because the R54 mode/integration and replay receipts were absent. No predicted pass/fail is counted as an observed gate result.

Scope remains limited to this constructed integer-width metadata pair, current scratch decode measurements, and prior-report preservation audit. Nothing here establishes general codec or PCM32 conversion support, extra precision behavior, general fidelity, audibility, quality, rights, engine behavior, production suitability, or promotion.
