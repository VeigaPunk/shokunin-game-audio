# Round 33 guard — corpus and replay invariants

## Scope and result

I guarded the declared Round 33 coverage move against accidental mutation of the established corpus and carried-forward runner evidence. The declared clean-before revision is `b8e3e5c8de6ee0f82d87f6187437991b73b56073`. Its canonical artifact set is 13 WAVs. The five existing `_alt` variants are `ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, and `stem_layer_alt`; they are already included within those 13 files. UI currently has only `ui.wav` (declared .12 s) and `ui_alt.wav` (.16 s).

I compared every current canonical WAV’s SHA-256 with the bytes at the declared clean-before revision. All 13 hashes match exactly (table below). This is a current snapshot guard, not evidence that a proposed addition has been integrated or replayed. Current worktree shows the shared LOG modified and round-33 scratch/reports present; I did not edit those shared files, canonical fixtures, source, or any other report. The existing `r33-alt.md` confirms only a scratch candidate fit. I did not run the project measurement runner, so I have no direct normal-run receipt, new-fixture receipt, or integration result.

## Existing canonical SHA-256 guard

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

## Carried-forward Round 32 runner guard

The declared prior round’s corrected non-author replay reports 30 actual serial runner receipts: 9 exit 0, 21 expected exit 1, and 0 runner exit 2. Its prior-29 subset was 8 exit 0 / 21 exit 1. All eight invalid-probe rows had the expected statuses: `short_sections` expected failure (section count); `corrupt` expected failure (decode); `wrong_format` expected failure (format); `odd_sections` expected failure (section count); `native16_probe` expected pass; `native24_probe` expected failure (format); `stereo48_probe` expected failure (format); `mono441_probe` expected failure (format).

That replay also documents 30 initial mistyped-script-path setup attempts, each exit 2 with no receipt; those are setup errors, excluded from runner outcomes, not gate failures. I did not rerun those commands. The Round 32 verifier states the 13 hashes, five existing variants, threshold objects, and normal restoration held in its replay. These are prior-round reported results, not a Round 33 independent replay.

## Round 33 scope and interpretation guard

The alternate scratch analysis reports a 9,600-frame 48 kHz mono PCM16 candidate at measured 0.20 s, with peak `0.375946044921875`, RMS `-22.20695387316763 dBFS`, centroid `966.7216217320357 Hz`, and no ordinary helper failures. Reported pair deltas are `ui`→candidate duration `0.08000000000000002 s`, centroid-relative `0.00018103031409457665`; `ui_alt`→candidate duration `0.04000000000000001 s`, centroid-relative `0.3207185389302337`. On the declared `.020 s OR .10` rule both pass by duration; the first is duration-only. These are scratch measurements, not canonical integration or independent replay.

A proposed `ui_third` is an analytic fixture only. Its intended 14th canonical hash must be new, while all 13 listed hashes remain unchanged; keep the five prior variants and existing `.020 OR .10` thresholds/comparator unchanged. A third duration point and numeric comparisons do not establish perceptual or auditory distinctness, representative UI coverage, sound quality, or production readiness. No audition, quality, rights, engine, publishing, or promotion claim is made.

## Commands and exits

Exact command used for the baseline comparison:

`for f in .shokunin/audio/corpus/artifacts/*.wav; do printf '%s ' "$(basename "$f")"; git show b8e3e5c8de6ee0f82d87f6187437991b73b56073:"$f" | sha256sum | cut -d' ' -f1; done` — **exit 0**. It printed the 13 hashes above. No project shell command or measurement runner was run by me. There was no failed fit or setup attempt by me; the 30 historical setup errors above belong to the Round 32 verifier’s report and are kept separate from its 30 runner outcomes.
