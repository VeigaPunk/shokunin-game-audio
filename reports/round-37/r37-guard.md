# Round 37 guard — Old17 canonical and prior replay context

## Scope, commands, and evidence boundary

This report records the Round 37 LOG declaration and carried-forward Round 36 non-author verifier evidence. I did not run measurement, fixture, or replay shell commands, perform numeric fits, audition audio, or modify source, LOG, SCORECARD, canonical assets, or any other report. I wrote only this report; no commit or push. The shell commands I did run for inspection, with exits, were:

- `pwd; ls -la .shokunin/audio; find .shokunin/audio -maxdepth 3 -type f | sort | tail -80` — exit 0.

Round 37's declaration is a proposed equal-duration ambience-family below-threshold negative control; it is not evidence that a new candidate fit or replay succeeded. Keep setup/invocation failures distinct from numeric-fit results and expected validation failures. The Round 36 verifier disclosed an initial wrapper mistake: 34 attempts exited 127 before invoking the runner and produced no receipts; after correction, the actual 34-run replay had zero runner setup failures. Those 127s are setup failures, not fit failures or numeric evidence. Round 36 wave-one helper/path invocation errors likewise are not numeric fit results. No Round 37 fit or replay is reported here.

## Old 17 canonical WAVs

Round 37 LOG names clean-before revision `83395d1b4241582463d9d5fbdece619180610372` and 17 canonical WAVs. The following hashes and measurements are the preserved Round 36 non-author baseline (duration, peak FS, RMS dBFS, centroid Hz); this guard does not independently re-hash them. The Round 36 addition `ambience_third.wav` has SHA-256 `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404`, and measurements 2.00 s, 0.225006 FS, −16.922619 dBFS, 112.032104 Hz.

| Canonical WAV | SHA-256 | Duration | Peak | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---:|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.00 s | 0.174591 | −18.153351 | 36.616408 |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.00 s | 0.199738 | −17.670324 | 58.019197 |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 s | 0.808777 | −20.402187 | 10843.127203 |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 s | 0.756165 | −17.329570 | 473.791536 |
| `impact_third.wav` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.40 s | 0.456116 | −20.849585 | 6838.143303 |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 s | 0.539490 | −23.779941 | 11934.484046 |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 s | 0.639313 | −21.987316 | 12024.214879 |
| `movement_third.wav` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.30 s | 0.489502 | −14.025186 | 4553.583280 |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.00 s | 0.323792 | −14.881435 | 272.675683 |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.00 s | 0.059998 | −30.287567 | 190.143327 |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.00 s | 0.049988 | −31.667277 | 277.951384 |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.00 s | 0.049987 | −31.667248 | 287.938059 |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.00 s | 0.172363 | −23.066521 | 201.870691 |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 s | 0.375946 | −19.991688 | 966.896659 |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 s | 0.318787 | −20.525534 | 1423.153254 |
| `ui_third.wav` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.20 s | 0.375946 | −22.206954 | 966.721622 |
| `ambience_third.wav` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.00 s | 0.225006 | −16.922619 | 112.032104 |

## Five generic `_alt` comparisons

Round 36 replay preserved the five generic records; the unchanged predicate is duration delta ≥.020 s **OR** baseline-relative centroid delta ≥.10.

| Pair | Duration delta | Relative centroid delta | Result |
|---|---:|---:|---|
| `ui` → `ui_alt` | 0.04000000000000001 s | 0.47187731004956435 | pass |
| `impact` → `impact_alt` | 0.0 s | 0.9563048992406177 | pass |
| `movement` → `movement_alt` | 0.12 s | 0.007518618572621081 | pass |
| `ambience` → `ambience_alt` | 0.0 s | 0.5845136323520758 | pass |
| `stem_layer` → `stem_layer_alt` | 0.0 s | 0.46179931396667484 | pass |

## Four explicit family records

Round 36 reports these eight explicit pair comparisons (distinct from the five generic `_alt` records). Threshold remains duration delta ≥.020 s OR relative centroid delta ≥.10.

| Family / pair | Duration delta | Relative centroid delta | Result / qualifying arm(s) |
|---|---:|---:|---|
| UI `ui` → `ui_third` | 0.08000000000000002 s | 0.00018103031409457665 | pass, duration only |
| UI `ui_alt` → `ui_third` | 0.04000000000000001 s | 0.3207185389302337 | pass, both |
| Impact `impact` → `impact_third` | 0.08000000000000002 s | 0.36935690461299725 | pass, both |
| Impact `impact_alt` → `impact_third` | 0.08000000000000002 s | 13.432810187572105 | pass, both |
| Movement `movement` → `movement_third` | 0.06 s | 0.6184516010427937 | pass, both |
| Movement `movement_alt` → `movement_third` | 0.06 s | 0.6212989100908565 | pass, both |
| Ambience `ambience` → `ambience_third` | 0.0 s | 2.059614818322321 | pass, centroid only |
| Ambience `ambience_alt` → `ambience_third` | 0.0 s | 0.9309488765840295 | pass, centroid only |

## Prior 34-run outcomes and invalid statuses

The Round 36 non-author replay executed 34 serial runner invocations: **13 exit 0, 21 expected fixture-validation exit 1, zero other replay exits, zero corrected-replay runner setup failures**. Its carried-forward prior-33 sequence was 12 exit 0 / 21 expected exit 1; #34 was the additional normal restore. The 21 exit-1 outcomes are expected probe rejections, not runner setup errors. The invalid probe (#29) had these eight statuses:

- `short_sections`: expected_failure(section count)
- `corrupt`: expected_failure(decode)
- `wrong_format`: expected_failure(format)
- `odd_sections`: expected_failure(section count)
- `native16_probe`: expected_pass
- `native24_probe`: expected_failure(format)
- `stereo48_probe`: expected_failure(format)
- `mono441_probe`: expected_failure(format)

Round 36's valid receipts had 17 canonical entries; invalid receipt #29 had no canonical measurement set. These are carried-forward Round 36 results, not a Round 37 replay.

## Numeric and claim limits

Round 37 LOG calls for an optional equal-duration ambience negative where duration delta is exactly zero and a measured nonzero centroid delta is strictly below .10, intended to fail the unchanged distinctness OR predicate without ordinary/seam failures. It proposes generated 2.0 s, 48 kHz mono PCM16 scratch WAVs and asks for a project-measured fit. This guard has no candidate fit result to report; setup success alone would not count as numeric fit. The old/new centroid is a lossy scalar, and endpoint/slope are numeric seam proxies. Nothing here establishes spectral-distribution similarity/novelty, audible seamlessness, listening or quality, production suitability, rights, engine suitability, publishing, or promotion.
