# Round 44 Sol adjudication — ordinary UI duration tolerance

## One declared move and verdict

**Admit the narrow numerical calibration move.** The opt-in 5807/5809-frame original UI-shaped controls bracket the existing ordinary per-file duration predicate `abs(ffprobe_duration-spec[0]) > .001` against the unchanged `SPECS["ui"]` duration target `.12 s`. This is not the separate pairwise-distinctness `.020 s` duration check tested in R27. Admission requires at least one improved axis and zero demonstrated harm within scope; the fresh non-author runner evidence meets that rule.

| Axis | Verdict | Reason |
|---|---|---|
| Depth | **Unchanged** | No new measurement method or comparator semantics; two explicit modes exercise the old predicate. |
| Coverage | **Unchanged** | This pair covers two measured interior points, not exact equality, other rates, ffprobe versions, or further audio/product requirements. |
| Calibration | **Improved** | An independent integrated pass/fail bracket now isolates ordinary duration at the existing UI target, with full receipts and unrelated checks still passing. |

**Demonstrated scoped harm: none.** This does not assert that every untested case is safe. The SHONEN four remain checked; no promotion follows from this calibration.

## Evidence independently checked

I read the R44 declaration and integration notes in `LOG.md`, all eight wave1 reports (`scout`, `executor`, `alt`, `critic`, `reviewer`, `simplifier`, `scribe`, `guard`), and the named non-author `r44-verifier.md`. I opened all 48 reported fresh receipt JSON files, verified 48 distinct paths and ledger exits (20 exit 0, 28 expected fixture-validation exit 1); the embedded prior46 subset was 19/27. The receipt range is `20261013T060507805101Z`–`20261013T060556451471Z`. The first and final normal receipt JSONs are equal: 17 canonical measurements with no ordinary failures, unchanged five passing generic `_alt` comparisons, four passing family groups (two comparisons each), four passing section records, and unchanged thresholds. At #43 the eight invalid cases have expected outcomes: `short_sections`/`odd_sections` section count, `corrupt` decode, `wrong_format`/`native24_probe`/`stereo48_probe`/`mono441_probe` format failures, and `native16_probe` pass. Old-17 WAV SHA values in the verifier match the 17 on-disk canonical files; normal metrics agree with its carried-forward baseline. No restoration leak is demonstrated.

The new fresh runner controls are:

| Mode and receipt | WAV SHA-256 | ffprobe duration / parsed delta from `.12 s` | Peak / RMS / centroid | Runner outcome |
|---|---|---|---|---|
| `--probe-ui-tolerance-5807`, `20261013T060508841398Z-ui-tolerance-5807/measurements.json` | `17890e483de91075569283a2bcfbada6a6402e1cd87ab52da53bdfbc605cf934` | `.120979 s` / `.0009790000000000076 s` | `.27947998046875` FS / `-16.431537076901346` dBFS / `1132.7351495568296` Hz | exit **0**; no failures |
| `--probe-ui-tolerance-5809`, `20261013T060509860666Z-ui-tolerance-5809/measurements.json` | `c0552b983ecd9230b16d6ac3441eb8be7b43e80130bbd413fb62272752d7d510` | `.121021 s` / `.001021000000000008 s` | `.27947998046875` FS / `-16.432818198672756` dBFS / `936.6642301482127` Hz | exit **1**; sole `duration: outside ±1 ms` |

Both runner-generated WAVs have the declared SHAs, 48 kHz mono PCM16 format, peak below `.95`, RMS above `.001` FS, and centroid inside UI's 250–4000 Hz band. The ideal +47/+49 frame offsets are `.0009791666666666666` / `.0010208333333333334 s`; the displayed ffprobe durations and parsed binary-float deltas, not ideal arithmetic, govern this runner. Independent alternate original WAVs with different SHAs reproduced the same two outcomes. No final candidate numeric mismatch was reported.

I inspected the source diff against clean-before `8009269ade6fff69c95de3cbde6a2cd653c33dc9`: only opt-in builder/mode/receipt wiring in `build_artifacts.py` and `measure_audio.py` (28 insertions, 5 deletions). The ordinary comparison remains `abs(duration-spec[0]) > .001`, the UI target remains `.12`, and no canonical threshold/comparator changes appear. Canonical artifacts compare byte-identically with clean-before.

## Exact commands and error classification

I did **not** rerun the CLI; the named non-author's 48 commands, exact exits, and unique receipt paths are in `r44-verifier.md`. In particular #2 was `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` (exit 0), #3 was `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` (exit 1, expected sole numeric duration failure), and #1/#48 were `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` (both exit 0, initial/final normal receipt equality). My own shell checks were:

```sh
git diff 8009269ade6fff69c95de3cbde6a2cd653c33dc9 -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py
# exit 0; inspected opt-in-only diff
git diff --check 8009269ade6fff69c95de3cbde6a2cd653c33dc9 -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py
# exit 0; no whitespace errors
git diff --quiet 8009269ade6fff69c95de3cbde6a2cd653c33dc9 -- .shokunin/audio/corpus/artifacts
# exit 0; canonical artifacts unchanged
git status --short
# exit 0; inspected worktree status
```

The verifier's fresh replay had **no setup errors**. Wave1 scout's malformed shell command exited 127, and alternate/guard initial relative-path helper calls errored; those were setup mistakes, not numeric failed fits. The 5809 exit 1 is the *intended* numeric failure, not a setup error. Critic's disposable, non-integrated 5808-frame probe reported `.121000 s`, parsed delta `.0010000000000000009 s`, and **fails** the current strict `>.001` float predicate. It is **not** an equality pass or an integrated control.

This verdict concerns numerical fixture calibration only. It does not establish exact mathematical `.001 s` equality behavior, perceptual duration or quality, production suitability, rights, engine behavior, publishing, or promotion. No shared source, LOG, SCORECARD, canonical artifacts, other reports, commit, or push were changed by this adjudication.
