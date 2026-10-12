# Round 5 coverage / before-state audit

## Scope and method

I audited the round-5 before-state identified in `.shokunin/audio/LOG.md` against commit `358f625` (the round-4 final coverage-report commit). This is a source-tree coverage audit, not an audio replay or perceptual review. I made no artifact, code, knowledge, receipt, or shared-log changes. My shell commands and exits are recorded below.

## Ten canonical WAVs

Commit `68a3c3c` contains the prior nine canonical WAVs. At `358f625`, those same nine paths have identical Git blob object IDs; therefore their file contents are byte-identical across the comparison. The tenth file, `stem_sections.wav`, is the declared round-4 addition. These are Git blob IDs (not SHA-256 digests).

| Canonical artifact | Git blob at `358f625` |
|---|---|
| `ambience.wav` | `57934d4dfce588247d8105f3d5d6fae5efba5011` |
| `ambience_alt.wav` | `c8ff048023a260a66bf12e2e7cb6c4d1978244ee` |
| `impact.wav` | `3d6ab86764390fc162ce717a8d773509bbc4fc4c` |
| `impact_alt.wav` | `59444145ca1b7c657e51aadd4ee4c11993b63f2e` |
| `movement.wav` | `93af9d3cd7ed43e0197625f7dfcfa431277775c6` |
| `movement_alt.wav` | `021e02ce78cfcd1f9f9b8d6d94294e29e1dde175` |
| `stem.wav` | `bd886f23df4efe9996112dd3c1b363bf6bfcef41` |
| `stem_sections.wav` | `ba31691718bb05020f677dce5ba4a3ca9161633b` |
| `ui.wav` | `0dca35d3cf7a44b2bcb9965d496240fb4d9e62fc` |
| `ui_alt.wav` | `a5a1fafce4513960b3b6b5aa1b0b06b2c7eecac6` |

The pre-round-4 set is exactly the nine paths other than `stem_sections.wav`; no existing canonical artifact was replaced or removed. This supports the round-5 guard that the ten-file baseline is preserved, while noting `358f625` itself adds only the report: the fixture addition predates it.

## Check-coverage inventory

Inspection of `measure_audio.py` at `358f625` shows all declared clean-fixture checks remain represented for the ten named WAVs: 48 kHz mono format; per-file duration within ±1 ms; peak `<0.95` and RMS `>=0.001`; per-fixture centroid bands; loop endpoint delta `<=0.03` and slope delta `<=0.001` for the three loop-marked fixtures; four SFX alternate distinctness checks (duration delta `>=0.020 s` OR relative centroid delta `>=10%`); and the `stem_sections` two-second split with 30 Hz component amplitudes `>=0.01`, section RMS `>=0.001`, and contrast `>=6 dB`. The section metric uses exact FFT bin 60 on each 96,000-sample half. LUFS values are reported where available; values at/below ebur128's `-70 LUFS` floor become null, and RMS dBFS remains separate. This is not a loudness acceptance window.

The source also retains independent probe modes for the flat-30-Hz contrast probe, slope-discontinuity probe, and broken-amplitude ambience probe. Their existence/check behavior is source-inventory evidence only; this audit did not rerun receipts or establish their exits. It therefore does not claim the round-5 distribution/control calculations or independent calibration replay are complete.

## Exact shell commands and exits

1. `git show --name-status --format=fuller 358f625; git rev-parse 358f625^; git status --short` — exit 0. Commit `358f625` adds only `.shokunin/reports/round-4/audio.md`; parent is `ff0f9fcf3512a12245eb67e08b630b5e9c68fa1e`.
2. `git show --format= --stat 358f625; git diff 358f625^ 358f625 -- .shokunin/audio; git diff -- .shokunin/audio/corpus/fixtures .shokunin/audio/corpus/artifacts` — exit 0. The commit changes no `.shokunin/audio` paths; no working-tree fixture/code diff was shown by the last command.
3. `git diff --name-status 68a3c3c 358f625 -- .shokunin/audio/corpus` — exit 0. Shows `stem_sections.wav` added among canonical artifacts, builder/measurement/knowledge updates, round-4 probes/receipts; does not show deletion/replacement of any prior canonical WAV.
4. `git show 358f625:.shokunin/audio/corpus/fixtures/measure_audio.py | sed -n '1,165p'` (combined with builder inspection) — exit 0. Inventory above is from the checked-in measurement source.
5. `set -o pipefail; for f in ambience.wav ambience_alt.wav impact.wav impact_alt.wav movement.wav movement_alt.wav stem.wav ui.wav ui_alt.wav; do a=$(git rev-parse 68a3c3c:.shokunin/audio/corpus/artifacts/$f) || exit; b=$(git rev-parse 358f625:.shokunin/audio/corpus/artifacts/$f) || exit; test "$a" = "$b" || { echo "MISMATCH $f $a $b"; exit 1; }; echo "$f $a"; done; printf 'stem_sections '; git rev-parse 358f625:.shokunin/audio/corpus/artifacts/stem_sections.wav` — exit 0. All nine comparisons matched; IDs are listed above.

## Coverage finding / limits

No regression in canonical artifact count or named check inventory is apparent at this before-state: nine prior canonical files persist unchanged and round 4 adds `stem_sections.wav` as the tenth. The round-5 calibration claim still requires raw-WAV distributions, probe receipt measurements, and non-author recomputation; this scoped coverage audit cannot establish those. No mastering, perceptual-quality, or universal-threshold conclusion is made.
