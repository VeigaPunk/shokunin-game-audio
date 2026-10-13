# R60 guard — designated78, earlier extra78, and protected baselines

## Scope and disposition

Read `/tmp/mission-audio-standing.md`, the R60 declaration in `.shokunin/audio/LOG.md`, and R59 source/reports. This is a read-only guard audit of prior replay/baseline evidence and the R60 write boundary. I did **not** inspect/build an R60 fixture, execute decoder or project measurement commands, run an R60 mode, or make an R60 integration claim. The R60 `executor/` directory was empty; I created only the authorized empty `corpus/live/round-60/guard/` scratch directory. I wrote only this report. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit/push was made.

## R59 replay provenance: designated 78 and earlier disjoint 78

The R59 designated non-author verifier report (`reports/round-59/r59-verifier.md`) identifies a serial set from `20261013T131241531728Z` through `20261013T131403651634Z`: 78 unique fresh receipts, 40 exit 0 and 38 expected validation exit 1. The R59 report says the mapped R58 subset is 76/76 exact complete parsed JSON, initial/final normal objects match, and these designated paths are separate from earlier replay and historical paths. This guard did not independently rerun the verifier or reparse the 78 JSON files; these counts and comparisons are attributed to its report, not new guard verification.

Important R59 provenance: there is a **separate earlier receipt-producing 78**, `20261013T131110133069Z` through `20261013T131231893990Z`, with paths disjoint from the designated set. R59 adjudication reports that it parsed both sets, found corresponding complete JSON objects equal, and corrected the earlier “after” chronology as report transcription. The verifier's later clarification says the first complete run had already succeeded; a subsequent malformed quoting command exited 127 before runner startup and created zero receipts, after which a second complete run was unnecessarily executed because the first run's in-memory results were mistakenly believed lost. Thus the quote error is **setup only**; the earlier 78 are real receipts, chronologically before the designated 78, and must be disclosed separately—not conflated with the designated ledger, counted as its additional credit, or described as receiptless. The verifier's designated ledger is counted once as 78, not 156/157. No R60 runner inference follows.

## Canonical17 audit

I independently hashed all current `.shokunin/audio/corpus/artifacts/*.wav` using:

```sh
python3 -c 'import hashlib,pathlib; p=pathlib.Path(".shokunin/audio/corpus/artifacts"); [(print(f"{x.name} {hashlib.sha256(x.read_bytes()).hexdigest()}")) for x in sorted(p.glob("*.wav"))]'
```

Exit **0**. All **17/17** SHA-256 values match the R59 verifier's canonical ledger and the R58/R59 guard baseline. Canonical identity is not an R60 replay or integration result. The previously recorded normal-receipt metrics are the baseline only; this guard did not remeasure them.

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
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 0.04998779296875 | -31.667277345674258 | 277.9513846029918 |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 0.04998779296875 | -31.66724765274306 | 287.93805923844434 |

Note: canonical SHA values above were independently verified. Metrics are copied from the R59 verifier/preceding baseline; this guard did not independently remeasure them. The table retains only the concise metric columns needed to identify the baseline.

## R59 prior battery, controls, and scope

The R59 verifier reports the mapped prior78 commands/exits and complete receipt objects equal to its R58 predecessor set; this guard treats that as the verifier's audited comparison, not an independent JSON replay. The R58 baseline was 76 commands (38 clean exit 0 / 38 expected validation exit 1); R59 added two selected modes to make 78. The verifier records unchanged canonical17 hashes/metrics, five generic `_alt` distinctness comparisons, four family maps (UI, impact, movement, ambience; two comparisons apiece), four section records, and these eight invalid-probe classifications:

- `short_sections`: section-count failure
- `corrupt`: decode failure
- `wrong_format`: format failure
- `odd_sections`: section-count failure
- `native16_probe`: expected pass
- `native24_probe`, `stereo48_probe`, `mono441_probe`: format failures

Recorded unchanged thresholds: 48,000 Hz; duration ±0.001 s; peak <0.95; RMS >0.001; UI centroid 250–4,000 Hz; impact 50–15,000 Hz; movement 100–16,000 Hz; ambience 5–200 Hz; stem 100–2,000 Hz; loop endpoint delta ≤0.03; loop slope ≤0.001 full-scale/sample; section contrast ≥6 dB; component amplitude ≥0.01; section RMS ≥0.001; internal-join gap ≤0.03; side-slope mismatch ≤0.001 full-scale/sample; distinctness duration delta ≥0.020 s or relative centroid delta ≥10%. These are reported historical settings, not R60 modifications.

## R60 declaration and boundary

The LOG declares a calibration comparison of matched 5,760-frame mono48k extensible PCM-subtype headers (fmt40, cbSize22, mask0x4, 16-bit container, identical signed16 UI-shaped payload), `wValidBitsPerSample=0` versus `16`. Valid-bits zero is explicitly an **invalid/unspecified, nonconforming declaration**, not a positive standards-conformance test. Whether ffprobe, SoX, or the unchanged project measurer rejects it or accepts it is **not yet observed in this guard**. There is no R60 header parse, command, exit, metadata, vector, metric, runner receipt, or integration evidence here. A future clean outcome, if any, can only indicate this host's handling of this malformed field and must not be generalized to conformance, universal decoder support, meaningful zero-bit audio, precision/fidelity, audibility, quality, or production.

The conditional 80-command replay applies only if **both** R60 opt-in modes actually yield receipts; otherwise preserve the actual unsupported/decode/setup/gate outcome without manufacturing receipts. Preserve R59's 78 raw receipt baseline and all canonical17/generic/family/threshold/section/eight-invalid controls. This report makes no R60 integration claim.
