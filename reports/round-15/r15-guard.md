# Round 15 guard — canonical inventory and prior mode receipts

Scope: independent inventory only. No runner replay was performed. No canonical PCM was generated or changed by this guard. Baseline is `0928e9e` (round-15 declared pre-change revision); runner/source integration is parent-owned. The working tree showed only `.shokunin/audio/LOG.md` modified before this report, consistent with concurrent round coordination; I did not touch it.

## Twelve canonical WAVs

Binary-safe Git comparison command:

```sh
git diff --quiet 0928e9e -- .shokunin/audio/corpus/artifacts/ambience.wav .shokunin/audio/corpus/artifacts/ambience_alt.wav .shokunin/audio/corpus/artifacts/impact.wav .shokunin/audio/corpus/artifacts/impact_alt.wav .shokunin/audio/corpus/artifacts/movement.wav .shokunin/audio/corpus/artifacts/movement_alt.wav .shokunin/audio/corpus/artifacts/stem.wav .shokunin/audio/corpus/artifacts/stem_layer.wav .shokunin/audio/corpus/artifacts/stem_layer_alt.wav .shokunin/audio/corpus/artifacts/stem_sections.wav .shokunin/audio/corpus/artifacts/ui.wav .shokunin/audio/corpus/artifacts/ui_alt.wav
```

Exit **0**: these tracked files have no working-tree diff from `0928e9e`. Local SHA-256 inventory (`sha256sum .shokunin/audio/corpus/artifacts/*.wav`, exit **0**):

| Canonical WAV | SHA-256 |
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
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

The diff check establishes equality to the baseline tracked blobs; hashes above fingerprint the current files. No comparison of decoded/transcoded PCM was made.

## Round 14 modes and receipt sources (LOG inventory; no replay)

The round-14 non-author replay inventory in `.shokunin/audio/LOG.md` reports serial commands `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` with flags in this order: none (normal), `--probe-layer-alt-join`, `--probe-layer-alt-flat`, `--probe-layer-slope`, `--probe-layer-join`, `--probe-flat`, `--probe-layer-flat`, `--probe-slope`, `--probe-failing`, `--probe-invalid`, none (restore). Reported exits respectively: **0 / 1 / 1 / 1 / 1 / 1 / 1 / 1 / 1 / 1 / 0**.

Receipt sources (each `/measurements.json`):

| Mode | Exit | Receipt directory |
|---|---:|---|
| normal | 0 | `corpus/live/runs/20261012T183540052549Z-normal` |
| layer-alt-join | 1 | `corpus/live/runs/20261012T183540838731Z-layer-alt-join` |
| layer-alt-flat | 1 | `corpus/live/runs/20261012T183541623892Z-layer-alt-flat` |
| layer-slope | 1 | `corpus/live/runs/20261012T183542411062Z-layer-slope` |
| layer-join | 1 | `corpus/live/runs/20261012T183543200001Z-layer-join` |
| flat | 1 | `corpus/live/runs/20261012T183543997090Z-flat` |
| layer-flat | 1 | `corpus/live/runs/20261012T183544783913Z-layer-flat` |
| slope | 1 | `corpus/live/runs/20261012T183545553122Z-slope` |
| failing | 1 | `corpus/live/runs/20261012T183546279984Z-failing` |
| invalid | 1 | `corpus/live/runs/20261012T183546506352Z-invalid` |
| normal restore | 0 | `corpus/live/runs/20261012T183547247214Z-normal` |

This is reported inventory from LOG, not a fresh validation of receipts or modes. LOG says the new round-14 join probe had sole decoded gap failure (`.044403076171875` FS > `.03`), slope mismatch 0, valid 180Hz contrast `10.457775175842691dB`, centroid `1678.5871008347167Hz`; normal and restore JSON were equal, old controls remained expected, selected scratch hash matched worker candidate, and all twelve canonical hashes matched `ce3233a`. I make no new assertion on those mode outcomes beyond accurately listing LOG's reported receipt/exits.

## Command/exit audit

Commands actually relevant to the checks above:

- `git status --short; git ls-tree -r --name-only 0928e9e -- .shokunin/audio/corpus/artifacts` — exit **0**; listed tracked artifact paths and showed pre-existing `M .shokunin/audio/LOG.md`.
- `sha256sum .shokunin/audio/corpus/artifacts/*.wav` — exit **0**; values above.
- `git diff --quiet 0928e9e -- <the twelve explicit paths shown above>` — exit **0**.

I made two malformed hash-command attempts before correcting command construction: a joined unquoted `git show ... | sha256sum; ...` string was passed as a quoted executable and exited **127** (`No such file or directory`); `sha256sum .shokhin/audio/corpus/artifacts/*.wav` (path typo) exited **1**. Neither produced evidence and neither touched files. No test runner or audio measurement command was executed; no replay occurred.

This guard is file-integrity/mode-inventory evidence only. All PCM/artifacts are synthetic fixture assets. No listening or audible, musical, engine, security, sample-rights, compatibility, threshold-calibration, or production claim is made.
