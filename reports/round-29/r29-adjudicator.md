# Round 29 — Sol independent adjudication

**Verdict: ADMIT one narrowly demonstrated depth move; zero demonstrated scoped harm.** Before `99b6c0afb121fd7f1a85623a3a5854493c38ccf8`, Round 28 tested the existing absolute relative-centroid comparison with higher-centroid alternatives only. The integrated Round 29 opt-in probe now shows its lower-centroid direction on two measured points, with the duration arm false. This verdict is for the observed numeric fixture path, not a general sound-quality assertion. The source changes are not yet committed; `HEAD` is the clean-before revision, not a delivered work-commit hash.

| Owned axis | Judgment | Before → after |
|---|---|---|
| **Depth** (the one declared move) | **improved narrowly** | The existing absolute-centroid comparison is now exercised from below the baseline with matched-duration UI inputs on both sides of `.10`. A signed `(variant-base)/base` substitute would wrongly reject the above-cutoff lower-centroid case. |
| Coverage | unchanged | Two opt-in scratch modes add no canonical WAV, category, production fixture, or guarantee across parameter values. |
| Calibration | unchanged | The existing `abs(variant_centroid-base_centroid)/base_centroid >= .10` **OR** duration delta `>= .020 s`, canonical UI `.12 s` specification, and threshold objects are unchanged. This round does not locate equality at `.10` or recalibrate either limit. |

## Work performed and landed-change attribution

I inspected the Round 29 LOG declaration/fit/integration/replay entries; all eight wave-1 reports (`r29-{scout,executor,alt,critic,reviewer,simplifier,scribe,guard}.md`); the named non-author Luna `r29-verifier.md`; raw replay below/above/initial-normal/invalid/restored-normal receipts; `SHONEN.md`; and fixture-source diff against `99b6c0a`. Scout, reviewer, simplifier and scribe do not establish integrated outcomes. Executor and alt independently selected `k=.95/.94` from scratch fits; critic independently found another lower-side bracket, while reviewer and scribe proposed other candidates. The nonmonotonic sweeps are candidate evidence, not runner proof or a continuous transition. Alt's initial relative-path command exit 1 was a **setup/path error**, corrected to exit 0, not a waveform failure.

The uncommitted source diff adds only the opt-in lower-centroid builder route (`build_artifacts.py`, phase multiplier `k=1.0` baseline, `.95` below, `.94` above) and runner flags, measurement routes and receipt names (`measure_audio.py`). The source generates `x=.38*sin(2*pi*k*(700*t+800*t*t))*exp(-30*t)`, `t=arange(5760)/48000`; the writer quantizes to mono PCM16 at 48 kHz. Runner lines 285–289 measure **both** pair members with unchanged `SPECS["ui"]`, and lines 294–297 retain the absolute relative-centroid rule and `.020 OR .10` constants. No canonical asset/source threshold changes are in the diff. LOG integration and independent replay are the change evidence; there is no new work commit to cite yet.

## Before → after measurements and independent commands

The verifier's exact commands from the repository root and raw receipts are:

| Command | Exit | Receipt under `.shokunin/audio/` | Measured result |
|---|---:|---|---|
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | **1** | `corpus/live/runs/20261013T022558239794Z-ui-lower-centroid-below/measurements.json` | Baseline `966.8966593379727 Hz` > variant `871.155504521436 Hz`; duration delta `0.0`; absolute relative delta `0.09901901500217196` < `.10`. Sole failure: `ui_lower_centroid_below_alt` distinctness. |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | **0** | `corpus/live/runs/20261013T022559154018Z-ui-lower-centroid-above/measurements.json` | Baseline `966.8966593379727 Hz` > variant `862.0264574403602 Hz`; duration delta `0.0`; absolute relative delta `0.1084606104331939` >= `.10`; pair passes, empty failure lists. |

I inspected the four scratch WAV headers: **each has exactly 5760 frames, 48 kHz, one channel, 16-bit PCM**, so each lasts `.120000 s`. Both members of both pairs satisfy the **same canonical UI `.12 s` ordinary checks** (format, ±.001 s duration, peak < `.95`, RMS > `.001`, centroid in 250–4000 Hz); the below alternate's sole failure is appended by the existing distinctness rule. The signed relative deltas would be negative for both variants, so the signed comparator would miss the above-cutoff case. Exit 1 on the below mode is the intended negative gate, not a process/setup failure.

Luna's corrected replay has **26 actual serial runner executions with receipts**, seven exit 0, nineteen exit 1, none exit 2; full exact command/exit/receipt table is in `r29-verifier.md`. Prior 24 mode outcomes are replay rows **#1 and #4–#26** (six exit 0, eighteen expected exit 1), not a mistaken #1–#24 slice. The eight invalid-control statuses in raw `corpus/live/runs/20261013T022618102481Z-invalid/measurements.json` match expectations: `short_sections`, `odd_sections` section count; `corrupt` decode; `wrong_format`, `native24_probe`, `stereo48_probe`, `mono441_probe` format; `native16_probe` expected pass. Initial/restored normal receipts `20261013T022557335369Z-normal` and `20261013T022618922834Z-normal` are equal after excluding only measurement paths. Their five existing variants all pass (`ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, `stem_layer_alt`); 13 canonical SHA-256 hashes match the guard/baseline, and receipt threshold objects match. Before the corrected replay, a misquoted shell-wrapper invocation produced **26 exit-127 setup errors and no receipts**. These are excluded, **not 26 gate proofs**, and distinct from the corrected 26 executions.

My own read-only shell commands, all from the repo root: `git rev-parse HEAD` exit **0** (`99b6c0afb121fd7f1a85623a3a5854493c38ccf8`); `git diff 99b6c0afb121fd7f1a85623a3a5854493c38ccf8 -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` exit **0**; `git diff --check -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` exit **0**; `git diff --quiet 99b6c0afb121fd7f1a85623a3a5854493c38ccf8 -- .shokunin/audio/corpus/artifacts` exit **0** (no canonical artifact difference); `sha256sum .shokunin/audio/corpus/artifacts/*.wav` exit **0** (13 hashes agreeing with `r29-guard.md` and `r29-verifier.md`). Raw JSON comparison and WAV-header inspection used Python directly; I did not run another fixture probe.

## SHONEN and limits

- [x] Decision tables/error patterns/checklists: named non-author `audio-r1-verifier`, `.shokunin/reports/audio-r1-verifier.md`.
- [x] End-to-end task logged: named non-author `r2-verifier`, `reports/round-2/r2-verifier.md`.
- [x] Executable fixture-battery instructions: named non-authors `r3-adjudicator`/`r3-verifier`, `reports/round-3/`.
- [x] Province/no cross-domain bleed: named non-author `r24-verifier`, `reports/round-24/r24-verifier.md`.

All four boxes were already checked; **no rank change**. Admission requires at least one improved axis and no harmed axis, met here only for scoped depth. FFT spectral centroid is a numeric whole-waveform proxy. Neither two-point result proves exact `.10` equality, smoothness, monotonicity, perceptual/auditory difference, engine behavior, rights, publishing readiness, production readiness, or promotion. No shared edit, commit, push, or merge was made by this adjudicator.
