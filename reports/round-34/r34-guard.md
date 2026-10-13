# Round 34 guard — corpus and replay invariants

## Scope and result

I guarded the proposed impact-family coverage move against changes to the clean-before corpus and carried-forward runner evidence. The declared clean-before revision is `d6bfc6ea374e634fd6eb1322030d014612ff98cb`. It contains 14 canonical WAVs, five generic `_alt` variants, and two impact fixtures (`impact.wav`, `impact_alt.wav`), both declared at 0.32 s. The Round 34 proposal is a 0.40 s third impact; the scout and alt reports describe the analytic measurement and scratch-only fit. A candidate is not canonical unless parent integration and verification confirm it.

I ran only a read-only baseline hash command. It hashes the 14 artifact paths as stored at the declared baseline commit; all 14 values are listed below. I did not run a project runner, generate a candidate, or alter source, LOG, SCORECARD, canonical artifacts, or another report. No fit/setup attempt was made by me; the separate scratch candidate result below is reported by `r34-alt.md`, not my run.

## Baseline canonical SHA-256 (14)

| Canonical file | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |
| `ui_third.wav` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` |

## Existing generic variants and prior replay

The five generic `_alt` variants are `ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, and `stem_layer_alt`. The prior Round 33 non-author replay (report `reports/round-33/r33-verifier.md`) records 31 actual serial runner invocations: 10 exit 0, 21 expected exit 1, no runner exit 2 or setup failure. This is the prior31 carried-forward set. The eight invalid-probe rows had expected statuses: `short_sections` expected_failure (section count); `corrupt` expected_failure (decode); `wrong_format` expected_failure (format); `odd_sections` expected_failure (section count); `native16_probe` expected_pass; `native24_probe` expected_failure (format); `stereo48_probe` expected_failure (format); `mono441_probe` expected_failure (format). The prior report says baseline canonical hashes, five generic comparisons, thresholds, and normal restoration held. These are prior verifier results, not a new replay by me.

## Scratch fit and guard interpretation

`reports/round-34/r34-alt.md` reports scratch-only SHA-256 `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf`; measured 0.400000 s, 48 kHz mono PCM16, peak 0.4561157, RMS −20.849585 dBFS, centroid 6,838.143303 Hz, and no ordinary check failures. Reported baseline-to-candidate deltas are:

| Baseline | Duration delta | Relative centroid delta | Existing `.020 s OR .10` outcome |
|---|---:|---:|---|
| `impact.wav` (10,843.127203 Hz) | 0.080000 s | 0.369357 | pass, both arms |
| `impact_alt.wav` (473.791536 Hz) | 0.080000 s | 13.432810 | pass, both arms |

These are numeric proxies reported from the scratch fit, not a canonical integration, independent replay, or perceptual distinction. Preserve all 14 baseline hashes, the five generic variants, and existing thresholds; a new 15th file/hash and two explicit impact-family comparisons require parent integration and independent verification. No audition or sound-quality, production, rights, engine, publish, or promotion claim is made.

## Commands and exits

Exact shell command I ran:

`for f in .shokunin/audio/corpus/artifacts/*.wav; do printf "%s " "$(basename "$f")"; git show d6bfc6ea374e634fd6eb1322030d014612ff98cb:"$f" | sha256sum | cut -d' ' -f1; done` — **exit 0**. It printed the 14 declared baseline hashes above. No other shell/project command was run by me. There were no failed fit or setup attempts by me. The prior31 counts and invalid statuses above are carried forward from the named prior verifier, not my commands.
