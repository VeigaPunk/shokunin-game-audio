# Round 35 guard — canonical baseline and carried-forward invariants

## Scope and result

I read the Round 35 declaration in `.shokunin/audio/LOG.md`, the Round 34 guard/verifier reports, the Round 33 verifier report, the current normal measurement receipt, and the four Round 35 lane reports present when I wrote this (`executor`, `critic`, `scribe`, `simplifier`). I ran one read-only command to hash the 15 declared canonical files at clean-before `56f2b0f8d244966c13ebfd7b28d521e3825dd3aa`; it exited 0. All 15 hashes match the declared baseline. The metrics below are from the pre-existing Round 34 non-author normal receipt `corpus/live/runs/20261013T032822674797Z-normal/measurements.json`, not a new measurement run by me. The Round 35 executor's file remains scratch-only; this guard did not modify source, canonical artifacts, LOG, SCORECARD, or other reports.

## Clean-before canonical SHA-256 and normal metrics (15)

All files measured as 48 kHz mono PCM16 (`pcm_s16le`), and each has ordinary `failures: []` in that receipt. Peak is linear full scale; RMS is dBFS; centroid is Hz.

| Canonical WAV | SHA-256 | Duration (s) | Peak FS | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---:|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.00 | 0.174591 | -18.153352 | 36.616408 |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0ae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.00 | 0.199738 | -17.670324 | 58.019197 |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 | 0.808777 | -20.402187 | 10843.127203 |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 | 0.756165 | -17.329570 | 473.791536 |
| `impact_third.wav` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.40 | 0.456116 | -20.849585 | 6838.143303 |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 | 0.539490 | -23.779941 | 11934.484046 |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 | 0.639313 | -21.987316 | 12024.214879 |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.00 | 0.323792 | -14.881435 | 272.675683 |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.00 | 0.059998 | -30.287567 | 190.143327 |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.00 | 0.049988 | -31.667278 | 277.951385 |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.00 | 0.049988 | -31.667248 | 287.938060 |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.00 | 0.172363 | -23.066521 | 201.870691 |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 | 0.375946 | -19.991688 | 966.896659 |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 | 0.318787 | -20.525534 | 1423.153254 |
| `ui_third.wav` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.20 | 0.375946 | -22.206954 | 966.721622 |

## Existing generic and family comparison records

The five unchanged generic `_alt` variant records from that normal receipt (duration delta s / baseline-relative centroid delta; all `passed: true`):

| Variant vs baseline | Duration delta | Centroid relative delta | OR arms |
|---|---:|---:|---|
| `ui_alt` vs `ui` | 0.04000000000000001 | 0.47187731004956435 | both |
| `impact_alt` vs `impact` | 0.0 | 0.9563048992406177 | centroid only |
| `movement_alt` vs `movement` | 0.12 | 0.007518618572621081 | duration only |
| `ambience_alt` vs `ambience` | 0.0 | 0.5845136323520758 | centroid only |
| `stem_layer_alt` vs `stem_layer` | 0.0 | 0.46179931396667484 | centroid only |

The pre-existing explicit UI family records are `ui`→`ui_third`: 0.08000000000000002 s / 0.00018103031409457665 centroid relative (duration arm only); and `ui_alt`→`ui_third`: 0.04000000000000001 s / 0.3207185389302337 (both arms). Pre-existing impact family records are `impact`→`impact_third`: 0.08000000000000002 s / 0.36935690461299725; `impact_alt`→`impact_third`: 0.08000000000000002 s / 13.432810187572105 (both arms each). The existing rule is duration >= .020 s OR centroid relative >= .10. These are numeric proxy records, not perceptual distinctions. Round 35 movement candidate claims in `r35-executor.md` are scratch results only, not canonical evidence; parent integration and verification remain necessary.

## Prior replay and invalid-probe invariants

Round 34 non-author verifier report records 32 serial invocations: **11 exit 0, 21 expected exit 1, zero runner/setup exit 2**. Its carried-forward prior31 subset (#1–#31) is **10 exit 0 / 21 exit 1**; #32 is the extra normal restore. Round 35's declared prior32 carry-forward is therefore the Round 34 verifier's 32-run set: **11/21**, with the extra normal restored and matching the initial normal after removing receipt paths. This is reported from `reports/round-34/r34-verifier.md`, not replayed by me.

The eight invalid-probe expected statuses recorded in that verifier are: `short_sections` expected_failure (section count); `corrupt` expected_failure (decode); `wrong_format` expected_failure (format); `odd_sections` expected_failure (section count); `native16_probe` expected_pass; `native24_probe` expected_failure (format); `stereo48_probe` expected_failure (format); `mono441_probe` expected_failure (format). Round 34 verifier reports unchanged prior 14 hashes, five generic `_alt` comparisons, existing UI comparisons and thresholds. For Round 35, preserve all 15 hashes above, all five generic records, both UI records, existing impact records/thresholds and carried-forward statuses unless parent integration explicitly adds the separate movement-family records.

## Commands, exits, and setup/fit separation

Exact shell command I ran (read-only baseline hash check):

`for f in .shokunin/audio/corpus/artifacts/*.wav; do printf "%s " "$(basename "$f")"; git show 56f2b0f8d244966c13ebfd7b28d521e3825dd3aa:"$f" | sha256sum | cut -d' ' -f1; done` — **exit 0**, 15 lines, matching hashes above. No project runner, build, or replay command was run by me; no fit/setup attempt by me.

Separate lane-reported setup/fit facts (not my commands): `r35-executor.md` reports one malformed invocation, `python3 .shokunin/audio/corpus/live/round-35/executor/generate_measure.py` (shell interpreted the path as command text), exit **127**, classified there as quoting/setup failure; corrected `python3 .shokunin/audio/corpus/live/round-35/executor/generate_measure.py` exited **0** and measured the scratch candidate successfully. The scribe reports `find .shokunin/audio/reports/round-35 -maxdepth 1 -type f -print` exit **1** because the directory did not yet exist at that inspection, and `find .shokunin/audio/corpus/live/round-35 -maxdepth 3 -type f -print` exit **0** with no files at that time. These are setup/path inspection outcomes, not failed candidate fits. No failed fit is reported by executor; its scratch fit is successful. No candidate is canonical by this report.

Only duration, RMS/peak, and centroid numbers are recorded. No audition, sound-quality, production, rights, engine, publish, or promotion claim is made. No commit or push.
