# r20-guard baseline (audio shokunin round 20)

Role: READ-ONLY baseline of pre-round corpus and r19 verifier routes.
Worktree: `/home/vgpnk/Projects/prymeagnt/audio` (branch `craft/audio-r1`).
No commits. No edits outside this report path.

## Git identity and HEAD

Exact commands:

```
cd /home/vgpnk/Projects/prymeagnt/audio && git rev-parse HEAD
cd /home/vgpnk/Projects/prymeagnt/audio && git status --short
cd /home/vgpnk/Projects/prymeagnt/audio && git config user.name && git config user.email
```

Exits: all 0.

Observed:

- HEAD: `a905a265517828d2d10efc33b7dbcf36655e935f` (short `a905a26`)
- `git status --short`: empty (clean worktree; no staged/unstaged output)
- `user.name`: `games-engine-mechanics-shokunin`
- `user.email`: `games-engine-mechanics@shokunin.local`

Note for parent: commit must use `git -c user.name=audio-shokunin -c user.email=audio@shokunin.local`. This leaf did not commit.

## Artifact SHA-256 baseline (13 files)

Directory: `.shokunin/audio/corpus/artifacts/*.wav`

Method: `hashlib.sha256` of on-disk bytes; compare to `git show a905a26:<path> | sha256sum` and `git show 7083a3f:<path> | sha256sum`.

| file | disk SHA-256 | vs a905a26 | vs 7083a3f |
|---|---|---|---|
| ambience.wav | b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198 | MATCH | MATCH |
| ambience_alt.wav | 2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc | MATCH | MATCH |
| impact.wav | a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc | MATCH | MATCH |
| impact_alt.wav | a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6 | MATCH | MATCH |
| movement.wav | 23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d | MATCH | MATCH |
| movement_alt.wav | 51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639 | MATCH | MATCH |
| stem.wav | fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0 | MATCH | MATCH |
| stem_layer.wav | ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9 | MATCH | MATCH |
| stem_layer_alt.wav | 74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9 | MATCH | MATCH |
| stem_layer_third.wav | 3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445 | MATCH | MATCH |
| stem_sections.wav | 49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702 | MATCH | MATCH |
| ui.wav | 4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9 | MATCH | MATCH |
| ui_alt.wav | 166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f | MATCH | MATCH |

Count: 13 files. `stem_layer_third.wav` matches expected canonical SHA-256 `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`.

## r19 verifier routes (16) — no third-join

Source: `.shokunin/audio/reports/round-19/r19-verifier.md`

Extracted exact commands (16):

1. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` (exit 0)
2. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` (exit 0)
3. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` (exit 1)
4. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` (exit 1)
5. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` (exit 1)
6. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` (exit 1)
7. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` (exit 1)
8. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` (exit 1)
9. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` (exit 1)
10. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` (exit 1)
11. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` (exit 1)
12. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` (exit 1)
13. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` (exit 1)
14. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` (exit 1)
15. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` (exit 1)
16. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` (exit 0)

Confirmation: **none** of the 16 commands is `--probe-layer-third-join`. Existing gap-only routes remain `--probe-layer-join` (120 Hz) and `--probe-layer-alt-join` (180 Hz). 200 Hz routes present are slope-only: `--probe-layer-third-slope`, `--probe-layer-third-slope-edge-pass`, `--probe-layer-third-slope-edge-fail`.

## Five `_alt` distinctness names

From `measure_audio.py` SPECS / distinctness checks (runner):

1. `ui_alt`
2. `impact_alt`
3. `movement_alt`
4. `ambience_alt`
5. `stem_layer_alt`

(r19-verifier also states all five `_alt` distinctness records passed in normal and edge receipts.)

## Baseline verdict

**clean** — 13/13 artifact hashes MATCH HEAD `a905a26` and `7083a3f`; worktree status empty; third-layer hash as expected; r19 has 16 routes and zero `--probe-layer-third-join`.
