# Round 36 guard — old canonical invariants and replay context

## Scope and limits

This guard records the declared Round 36 baseline and carried-forward Round 35 replay evidence from `.shokunin/audio/LOG.md` and `reports/round-35/r35-verifier.md`. I did not run shell commands, measure or audition audio, change shared source, LOG, SCORECARD, canonical artifacts, or other reports, and made no commits or pushes. This is a guard report, not candidate or integration evidence. Any candidate scratch remains noncanonical unless the parent integrates it and independently verifies it.

## Old 16 canonical WAVs

Declared clean-before revision: `1fdccc41e936772150fae74131bda1a1ef7e3520`. The sixteen canonical files at that baseline, with Round 35 replay measurements (duration; peak FS; RMS dBFS; centroid Hz), are:

| Canonical WAV | SHA-256 | Duration | Peak | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---:|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.00 s | 0.174591 | -18.153351 | 36.616408 |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.00 s | 0.199738 | -17.670324 | 58.019197 |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 s | 0.808777 | -20.402187 | 10843.127203 |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 s | 0.756165 | -17.329570 | 473.791536 |
| `impact_third.wav` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.40 s | 0.456116 | -20.849585 | 6838.143303 |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 s | 0.539490 | -23.779941 | 11934.484046 |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 s | 0.639313 | -21.987316 | 12024.214879 |
| `movement_third.wav` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.30 s | 0.489502 | -14.025186 | 4553.583280 |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.00 s | 0.323792 | -14.881435 | 272.675683 |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.00 s | 0.059998 | -30.287567 | 190.143327 |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.00 s | 0.049988 | -31.667277 | 277.951384 |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.00 s | 0.049987 | -31.667248 | 287.938059 |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.00 s | 0.172363 | -23.066521 | 201.870691 |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 s | 0.375946 | -19.991688 | 966.896659 |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 s | 0.318787 | -20.525534 | 1423.153254 |
| `ui_third.wav` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.20 s | 0.375946 | -22.206954 | 966.721622 |

These metrics are numeric proxies. The carried-forward Round 35 replay states all 15 then-existing old hashes matched its clean-before `56f2b0f8d244966c13ebfd7b28d521e3825dd3aa`; the sixteenth `movement_third.wav` was the Round 35 addition (above hash). Round 36 must independently preserve these declared 16 bytes/records.

## Five generic `_alt` records

Round 35 normal receipt `.shokunin/audio/corpus/live/runs/20261013T034131375782Z-normal/measurements.json` records:

| Pair | Duration delta | Relative centroid delta | Result |
|---|---:|---:|---|
| `ui` → `ui_alt` | 0.04 s | 0.4718773100 | pass |
| `impact` → `impact_alt` | 0.00 s | 0.9563048992 | pass |
| `movement` → `movement_alt` | 0.12 s | 0.0075186186 | pass |
| `ambience` → `ambience_alt` | 0.00 s | 0.5845136324 | pass |
| `stem_layer` → `stem_layer_alt` | 0.00 s | 0.46179931397 | pass |

Threshold remains duration delta ≥0.020 s **OR** baseline-relative centroid delta ≥0.10. The Round 35 report says these five records/cutoffs were preserved. No claim that these scalar comparisons establish perceptual distinction.

## Explicit UI, impact, and movement family records

These are additive records, separate from the unchanged five-item generic `_alt` set:

- UI: `ui`→`ui_third` = 0.08000000000000002 s / 0.00018103031409457665 relative centroid; duration arm alone passes. `ui_alt`→`ui_third` = 0.04000000000000001 s / 0.3207185389302337; both arms pass.
- Impact: `impact`→`impact_third` = 0.08000000000000002 s / 0.36935690461299725; both arms pass. `impact_alt`→`impact_third` = 0.08000000000000002 s / 13.432810187572105; both arms pass.
- Movement: `movement`→`movement_third` = 0.06 s / 0.6184516010427937; both arms pass. `movement_alt`→`movement_third` = 0.06 s / 0.6212989100908565; both arms pass.

Round 36's declared ambience target is exactly equal duration, so it must not rely on a duration delta; centroid is the only qualifying branch of the unchanged OR predicate for those comparisons. Seam and centroid metrics do not establish perceptual seamlessness, quality, or novelty.

## Prior-33 outcomes and invalid statuses

Round 35 verifier replay: 33 serial invocations; **12 exit 0, 21 expected exit 1, zero other exits or replay setup failures**. The prior-32 subset was 11 exit 0 / 21 exit 1; #33 was the extra normal restore. Exact command examples from that verifier: `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` → exit 0 (#1 and restores #30–#33); `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` → exit 1 (#29). The 21 expected failures were fixture probe failures, not runner setup errors. Valid receipts had 16 measurements; invalid receipt #29 had no canonical measurement/threshold set.

The eight invalid statuses in #29 were: `short_sections=expected_failure(section count)`; `corrupt=expected_failure(decode)`; `wrong_format=expected_failure(format)`; `odd_sections=expected_failure(section count)`; `native16_probe=expected_pass`; `native24_probe=expected_failure(format)`; `stereo48_probe=expected_failure(format)`; `mono441_probe=expected_failure(format)`.

Verifier setup failures: none. Separate historical Round 35 wave-one issues, not replay failures or candidate-fit results: executor malformed shell invocation exit 127 before candidate execution; alt first measurement attempt exit 1 due relative-path setup, then corrected measurement succeeded; reviewer two helper calls exited 1 (wrong argument type/path); scribe inspection `find` exited 1; one REPL quoting syntax error had no shell command/exit. These are recorded separately from the verifier's expected exit-1 fixture probes. No Round 36 candidate fit has been run or assessed by this guard.

## Evidence boundary

No audition or quality assessment. These are numeric analytic-fixture proxies only, not sound quality, production, rights, engine, publishing, or promotion evidence. A candidate is scratch, not canonical, until parent integration and verification.
