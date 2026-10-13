# Round 24 guard — canonical assets, thresholds, variants, and ownership

## Scope and result

This is a bounded baseline inventory for the round-24 checklist task, not a promotion or a SHONEN box-4 verdict. At inspection, `HEAD` was `2a198118a527baf749dbd2e23b6667a79a1ccf31` (`Audio round 23: final calibration report`), the declared round-24 before commit. The worktree already had a modified `.shokunin/audio/LOG.md`; I did not edit it. The only file I wrote is this report. I made no source, artifact, or shared-document edits, and did not run the builder or measurement runner.

## Canonical artifact baseline

The tracked artifact inventory contains 13 WAVs. SHA-256 values below were computed from the working files, and the tracked artifact diff against `HEAD` was empty. Since `HEAD` is the declared baseline commit, these identify the current before-state; this is not an independent replay of generation or measurement.

| Canonical WAV | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

## Threshold inventory and current variant receipt

I inspected `.shokunin/audio/corpus/fixtures/measure_audio.py` and the latest normal receipt available at inspection, `corpus/live/runs/20261013T011843291086Z-normal/measurements.json`. The receipt has 13 measurements, no fixture failures, and five passing distinctness records. These are the current local checker bounds, not universal audio standards or evidence of perceived quality:

- Format: 48,000 Hz, mono, `pcm_s16le`, `bits_per_sample == 16`.
- Duration: configured fixture duration within ±0.001 s.
- Peak: `< 0.95` full scale. RMS: code rejects `< 0.001`, so equality passes (although the receipt key retains the misleading name `rms_min_exclusive`).
- Spectral centroid inclusive bands (Hz): UI 250–4,000; impact 50–15,000; movement 100–16,000; ambience 5–200; stem/stem_sections/all three stem layers 100–2,000. Each `_alt` uses its corresponding category band.
- Looped fixtures: endpoint amplitude delta `<= 0.03` full scale and outer slope mismatch `<= 0.001` full scale/sample.
- Section checks: component amplitudes each `>= 0.01` full scale; section RMS each `>= 0.001`; component-amplitude contrast `>= 6.0 dB` (the reported contrast is `20*log10(A2/A1)`, not integrated energy). Relevant stem layers additionally require internal join adjacent-sample delta `<= 0.03` and side-slope mismatch `<= 0.001` full scale/sample.
- Variant distinctness: duration delta `>= 0.020 s` **or** centroid-relative delta `>= 0.10`.
- Loudness: integrated LUFS is reported when finite and above the EBU gated floor; there is no LUFS acceptance window. A null/floor result is not a loudness pass or silence measurement.

Passing variants in the inspected receipt: `ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, and `stem_layer_alt`. The runner computes the duration-or-centroid rule for each. This receipt is a checked existing run, not a run performed by me; I do not claim the listed sound is perceptually distinct.

## Path ownership and scope caveat

`.shokunin/audio/PROVINCE.md` says the lane owns game audio (SFX and soundtrack) and headless analysis, and refuses unsupported perceptual claims, publishing/store submission, sample-rights clearance, engine source mutation, game mechanics, and narrative canon. It permits writes only to `.shokunin/audio/**` and the lane's own `.shokunin/reports/**`; the round-24 task specifies its final report at `.shokunin/reports/round-N/audio.md`. Current repo files inspected for the round include the audio fixtures, builder/measurement scripts and audio knowledge/reports. The declared allowed/refused checklist is a proposal to be verified, not already proven by this inventory.

This check covers the named commit/worktree snapshot and observed paths only. It does **not** prove universal historical behavior, untracked/external work, all future task classification, sample rights, engine behavior, or absence of cross-domain bleed. SHONEN box 4 remains unchecked in the inspected file; this report does not check it.

## Commands run and exit statuses

Commands were run from the repository working directory. Statuses below are exact. The final two shell commands are independent measurements/inventory checks, not a runner replay.

| Command | Exit | Relevant result |
|---|---:|---|
| `git status --short --branch` | 0 | `## craft/audio-r1`; pre-existing ` M .shokunin/audio/LOG.md` |
| `git rev-parse HEAD` | 0 | `2a198118a527baf749dbd2e23b6667a79a1ccf31` |
| `git show -s --format='%H%n%s' 2a198118a527baf749dbd2e23b6667a79a1ccf31` | 0 | Confirmed declared baseline commit and subject |
| `git diff --name-only 2a198118a527baf749dbd2e23b6667a79a1ccf31..HEAD` | 0 | Empty (same before commit and HEAD) |
| `git ls-files .shokunin/audio/corpus/artifacts/*.wav \| sort` | 0 | 13 tracked canonical WAV paths |
| `git ls-files .shokunin/audio/corpus/fixtures .shokunin/audio/corpus/knowledge .shokunin/audio/reports/round-24` | 0 | Builder, runner, knowledge paths; no tracked round-24 report yet at that check |
| `git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts; printf 'exit=%s\n' "$?"` | 0 | Printed `exit=0`: no tracked artifact content difference |
| `git status --short -- .shokuhin/audio/corpus/artifacts .shokunin/audio/corpus/fixtures .shokunin/audio/reports/round-24` | 0 | Report directory was untracked; no artifact/fixture status entries. Note: command contains the literal typo `.shokuhin` in its first pathspec, so it is not evidence for that misspelled path. The correct artifact/fixture pathspecs were also included. |
| `sha256sum .shokunin/audio/corpus/artifacts/*.wav` | 0 | Values listed above |
| `git ls-files --stage .shokunin/audio/corpus/artifacts/*.wav` | 0 | All 13 paths are tracked stage-0 entries |

No shell test/build/runner commands were run. I inspected code and the existing normal receipt directly; no behavior is inferred beyond their contents.
