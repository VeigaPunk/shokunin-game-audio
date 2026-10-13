# r22-guard — baseline hashes, mode inventory, and variant coverage

## Scope and result

This is a baseline/inventory report only. I made no shared-source, LOG, SCORECARD, canonical-WAV, or other-report edits; no commits or pushes. The round-22 declaration names before-HEAD `14cf9861ca19041ddb25c322facc5ace9271a146`. At task inspection, working-tree status showed a modified `.shokunin/audio/LOG.md` and untracked `.shokunin/audio/corpus/live/round-22/`; these are not claimed as my edits. I did not spawn agents.

## Canonical baseline

The 13 WAV Git blobs at declared before-HEAD `14cf9861ca19041ddb25c322facc5ace9271a146` have these SHA-256 values:

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
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

These are hashes of the Git blobs at the declared baseline commit, not a claim that current working files were independently checked against them. The declaration and prior round-21 verifier report document the 13/13 unchanged comparison; round-21 verifier states all 13 current canonical hashes match its before state `b1af040` (same artifact inventory). No canonical files were written by me.

## Replay inventory: 19 executions

The latest pre-round replay inventory is the non-author round-21 verifier’s serial sequence. It consists of 17 distinct flag modes, bracketed by normal and restored-normal executions: 19 executions total. Prior round-21 evidence records the exact outcomes below. This is a historical baseline inventory, not a replay performed by this guard lane.

| # | Mode / exact flag | Historical exit |
|---:|---|---:|
| 1 | normal (no flag) | 0 |
| 2 | `--probe-layer-third-join-edge-pass` | 0 |
| 3 | `--probe-layer-third-join-edge-fail` | 1 |
| 4 | `--probe-layer-third-join` | 1 |
| 5 | `--probe-layer-third-slope-edge-pass` | 0 |
| 6 | `--probe-layer-third-slope-edge-fail` | 1 |
| 7 | `--probe-layer-third-slope` | 1 |
| 8 | `--probe-layer-alt-reverse` | 1 |
| 9 | `--probe-layer-alt-slope` | 1 |
| 10 | `--probe-layer-alt-join` | 1 |
| 11 | `--probe-layer-alt-flat` | 1 |
| 12 | `--probe-layer-slope` | 1 |
| 13 | `--probe-layer-join` | 1 |
| 14 | `--probe-flat` | 1 |
| 15 | `--probe-layer-flat` | 1 |
| 16 | `--probe-slope` | 1 |
| 17 | `--probe-failing` | 1 |
| 18 | `--probe-invalid` | 1 |
| 19 | restored normal (no flag) | 0 |

The historical exact command for each row is `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` followed by that row’s flag, when present. Round-21 verifier reports that all expected failure kinds held and initial/restored normal receipts matched apart from path identity. Round 22’s declaration requires these 18 prior flag outcome classes (the 17 flags plus normal) to remain, in addition to the two new PCM-width controls planned for its verifier. This baseline report does not claim those new controls were run or passed.

## Existing five variant checks

The round-21 verifier documents five passing `_alt` distinctness records in both edge receipts:

- `ui_alt`: duration delta 0.04 s.
- `impact_alt`: centroid relative delta 0.9563.
- `movement_alt`: duration delta 0.12 s.
- `ambience_alt`: centroid relative delta 0.5845.
- `stem_layer_alt`: centroid relative delta 0.4618.

These are existing fixture distinctness checks, not perceptual comparisons. This task did not rerun them.

## Shell commands invoked and exits

I list every shell invocation made in this task, including the failed setup attempt:

1. `cat .shokunin/audio/LOG.md` — exit **0**. Read the round-22 declaration and earlier history.
2. `git status --short && git rev-parse HEAD && git -c user.name=audio-shokunin -c user.email=audio@shokunin.local status --short` — exit **0**. Output showed modified `.shokunin/audio/LOG.md`, untracked `.shokunin/audio/corpus/live/round-22/`, and HEAD `14cf9861ca19041ddb25c322facc5ace9271a146`.
3. `git ls-tree -r --name-only 14cf9861ca19041ddb25c322facc5ace9271a146 -- .shokunin/audio/corpus/artifacts` — exit **0**. Listed the 13 baseline artifact paths.
4. `python3 -c "import hashlib,subprocess; p=subprocess.check_output(['git','ls-tree','-r','--name-only','14cf9861ca19041ddb25c322facc5ace9271a146','--','.shokunin/audio/corpus/artifacts'],text=True).splitlines(); [(lambda b,n: print(hashlib.sha256(b).hexdigest(),n))(subprocess.check_output(['git','show',f'14cf9861ca19041ddb25c322facc5ace9271a146:{x}']),x) for x in p]` — exit **2**. Shell quoting was malformed (`unexpected EOF while looking for matching "`); no hashes were produced by this attempt.
5. `python3 -c 'import hashlib,subprocess; p=subprocess.check_output(["git","ls-tree","-r","--name-only","14cf9861ca19041ddb25c322facc5ace9271a146","--",".shokunin/audio/corpus/artifacts"],text=True).splitlines(); [(lambda b,n: print(hashlib.sha256(b).hexdigest(),n))(subprocess.check_output(["git","show","14cf9861ca19041ddb25c322facc5ace9271a146:"+x]),x) for x in p]'` — exit **0**. Produced the table above.

No other shell commands were invoked. Python filesystem reads used to inspect the two already-existing round-22 reports and the round-21 verifier do not invoke a shell. No audio execution, perceptual/sample-rights/engine/publishing claim, or new validation claim is made.
