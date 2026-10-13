# Round 21 guard baseline (r21-guard)

Scope: baseline inventory only. I did not edit builder/runner, canonical WAVs, LOG, SCORECARD, or other reports; I created only this report. No commands below intentionally modify source or artifact files. Measurements cited from historical reports are not new runner evidence.

## Repository and toolchain baseline

From repository root, the initial status showed branch `craft/audio-r1`, HEAD `b1af040b3cca2e70dabaafa982c5261c971d03a9`, and one pre-existing modification: `.shokunin/audio/LOG.md`. Git identity reads `games-engine-mechanics-shokunin <games-engine-mechanics@shokunin.local>`; round instructions require explicit per-command identity `audio-shokunin <audio@shokunin.local>` for commits. I made no commit.

Exact commands and exits:

| Command | Exit |
|---|---:|
| `git status --short --branch; printf '\nHEAD '; git rev-parse HEAD; printf '\nidentity '; git config user.name; git config user.email; printf '\n'` | 0 |
| `python3 --version` | 0 (`Python 3.14.7`) |
| `python3 -c 'import numpy; print(numpy.__version__)'` | 0 (`NumPy 2.5.3`) |
| `ffmpeg -version` | 0 (`n9.0.1`) |
| `ffprobe -version` | 0 (`n9.0.1`) |
| `sox --version` | 0 (`SoX_ng v14.8.0.1`) |
| `python3 - <<'PY'\nimport ast, pathlib\nfor f in ['.shokunin/audio/corpus/fixtures/measure_audio.py']:\n t=ast.parse(pathlib.Path(f).read_text())\n for n in ast.walk(t):\n  if isinstance(n, ast.FunctionDef) and n.name=='main':\n   for x in ast.walk(n):\n    if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr=='add_argument' and x.args and isinstance(x.args[0],ast.Constant): print(x.args[0].value)\nPY` | 0 (15 flag names; command’s output is listed below) |
| `python3 -c 'import hashlib,pathlib,subprocess,sys; root=pathlib.Path(".shokunin/audio/corpus/artifacts"); files=sorted(root.glob("*.wav")); bad=[]; print("count",len(files)); [print(p.name, hashlib.sha256(p.read_bytes()).hexdigest(), "HEAD="+hashlib.sha256(subprocess.check_output(["git","show",f"HEAD:{p.as_posix()}"])).hexdigest(), "a905a26="+hashlib.sha256(subprocess.check_output(["git","show",f"a905a26:{p.as_posix()}"])).hexdigest()) for p in files]; sys.exit(0 if len(files)==13 and all(p.read_bytes()==subprocess.check_output(["git","show",f"a905a26:{p.as_posix()}"]) for p in files) else 1)'` | 0 |

`measure_audio.py` exposes these 15 modes/flags: normal (no flag), `--probe-layer-third-join`, `--probe-layer-third-slope-edge-pass`, `--probe-layer-third-slope-edge-fail`, `--probe-layer-third-slope`, `--probe-layer-alt-reverse`, `--probe-layer-alt-slope`, `--probe-layer-alt-join`, `--probe-layer-alt-flat`, `--probe-layer-slope`, `--probe-layer-join`, `--probe-flat`, `--probe-layer-flat`, `--probe-slope`, `--probe-failing`, `--probe-invalid`. The 15 flagged modes plus the normal invocation form 16 distinct CLI mode classes; the historical 17-run replay invoked normal twice (start and restore). This inventory is source inspection, not proof every mode works in a fresh replay; historical execution evidence is `reports/round-20/r20-verifier.md`.

## Canonical artifact hashes

There are 13 files under `.shokunin/audio/corpus/artifacts/`. Each local byte hash below matched both the current HEAD blob and `a905a26` (the declared round-20 baseline); the hash command above exited 0.

| Artifact | SHA-256 |
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

## Preservation and scope guards for round 21

Per the round-21 declaration in `.shokunin/audio/LOG.md`:

- Preserve all 13 canonical WAV byte hashes above; do not rewrite canonical artifacts.
- Preserve all five `_alt` distinctness outcomes, every existing threshold/polarity, and all 17 historical mode outcomes. Round 21 may add only the two new opt-in 200 Hz edge controls and their scratch; they are not canonical assets.
- New 983/984-count controls are intended to bracket the existing strict internal-gap predicate `> .03 FS`: `.029998779296875` passes at 983/32768, `.030029296875` fails at 984/32768. This is declared expected behavior only; I did not create, execute, or validate these controls.
- Do not relax spectrum, section contrast, level, outer seam, or other gates to force isolation. Preserve the existing fixture-local/SoX-decode limitation; do not imply audibility, perception, production, engine, rights, publish/push, or cross-domain validation.
- Preserve parent’s pre-existing LOG edit; no worker edits to shared source, canonical artifacts, LOG, scorecard, or other reports. No commit/push. Baseline status was not clean because that LOG modification predated this report.

Historical evidence read: `.shokunin/audio/reports/round-19/r19-verifier.md` and `.shokunin/audio/reports/round-20/r20-verifier.md`. Round-20 verifier reports 17 serialized executions with exit vector `[0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0]`; all five `_alt` records passed in normal and selected new-mode receipts, and all 13 hashes matched `a905a26` / `7083a3f`. The new round-21 edge pass/fail pair is not covered by that historical replay. I did not rerun the fixture runner, so this is baseline/hash/toolchain evidence only, not round-21 integration or end-to-end validation.
