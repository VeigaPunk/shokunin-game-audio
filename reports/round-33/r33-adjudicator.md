# Round 33 Sol adjudication — analytical UI fixture coverage

## Decision

**Admit the declared one-axis move narrowly.** At least one owned axis improves and no scoped axis has demonstrated harm. This is a verdict on measured analytic-fixture coverage, not an asset-quality rating or a rank decision.

| Owned axis | Verdict | Before `b8e3e5c8de6ee0f82d87f6187437991b73b56073` → after |
|---|---|---|
| depth | unchanged | The same ordinary format, duration, level, and full-waveform FFT centroid checks and existing numeric OR predicate now apply to one additional file. Neither auditory validation nor a new kind of numeric negative/positive control was introduced. |
| coverage | **improved narrowly** | Thirteen → fourteen deterministic canonical WAVs, with a third original source-generated UI fixture at a separately declared `.20 s`, plus explicit comparisons with both earlier UI fixtures. The third is measured in every valid replay receipt; the two ordered UI-family comparison records pass. This is one additional measured duration point, not representative or perceptual UI breadth. |
| calibration | unchanged | `.020 s OR .10` comparison cutoffs, existing five generic `_alt` comparisons, ordinary limits, and existing thirteen per-file metrics stay fixed. Adding `ui_third` to the band-spec map does not calibrate those cutoffs. No exact comparator boundary or perceptual threshold is established. |

## Evidence and attribution

The round-33 declaration in `.shokunin/audio/LOG.md` specified **coverage alone**. Eight wave-one reports (`r33-{scout,executor,alt,critic,reviewer,simplifier,scribe,guard}.md`) mapped the old family, tested the candidate independently in scratch, and limited the interpretation. In particular, the critic correctly objects that **duration alone does not imply spectral or perceptual novelty**. The executor's first two direct `measure()` helper calls exited **1** due first to passing a string instead of `Path`, then to an unresolved relative path; they produced no valid measurement conclusion. Its corrected absolute-path call exited **0**. Those setup mistakes are excluded from fixture-gate outcomes. The alternate scratch fit also exited **0** and independently matched the intended candidate.

The source diff from the clean-before revision adds only `save("ui_third", ...)` using the existing deterministic UI chirp/envelope at `time(.20)`, its declared `SPECS["ui_third"]=(.20,250,4000,False)`, and two separate `ui_family_comparisons` records. It leaves the five-comparison generic `_alt` loop and predicate unchanged. The artifact is **original source-generated analytic content**, not an imported recording: `.shokunin/audio/corpus/artifacts/ui_third.wav` is 9,600 frames at 48,000 Hz, mono PCM16 (two-byte samples), ffprobe duration `.2 s`, SHA-256 `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc`. Its measured peak `0.375946044921875` is below `.95`, RMS `-22.20695387316763 dBFS` (well above `.001` linear), centroid `966.7216217320357 Hz` lies inside the UI 250–4000 Hz band, and ordinary failures are `[]`. The source diff and artifact hash, rather than its name alone, support the reproducible canonical addition.

Named **non-author** `r33-verifier.md` gives 31 serial runner receipts. Initial normal #1, restored normal #30, and extra restored normal #31 contain exactly 14 canonical measurement entries each and match after excluding receipt-specific measurement paths. The raw receipts are `corpus/live/runs/20261013T031508389221Z-normal/measurements.json`, `20261013T031534824288Z-normal/measurements.json`, and `20261013T031542838399Z-normal/measurements.json`. Each records the same third-file metrics and the explicit ordered UI-family comparisons:

| Baseline → new fixture | Measured duration delta | Measured baseline-relative centroid delta | Existing OR predicate |
|---|---:|---:|---|
| `ui` → `ui_third` | `0.08000000000000002 s` | `0.00018103031409457665` | pass **by duration only**; centroid arm false |
| `ui_alt` → `ui_third` | `0.04000000000000001 s` | `0.3207185389302337` | pass by duration **and** centroid |

The denominator for each centroid-relative result is its named baseline's centroid. Both records are separate from the five unchanged generic `_alt` records. Old thirteen WAV SHA-256 hashes match the clean-before revision, tracked prior artifacts have no diff, and their normal metrics match the prior round's normal receipt after removing paths. The existing threshold values are unchanged; the centroid-band map gains only `ui_third`. This supports no claim that `ui` and `ui_third` differ meaningfully in spectrum: their centroid-relative delta is only about `0.000181`.

The non-author replay's carried-forward prior-30 subset (#1 plus #2–#30) yielded **9 exit 0 / 21 expected exit 1**, and the extra normal #31 exited **0**: overall 31 receipts, **10 exit 0 / 21 expected exit 1 / zero runner exit 2**. Raw invalid receipt `corpus/live/runs/20261013T031533982443Z-invalid/measurements.json` has eight expected statuses: `short_sections`, `corrupt`, `wrong_format`, `odd_sections`, `native24_probe`, `stereo48_probe`, and `mono441_probe` expected failures in their respective section-count/decode/format checks; `native16_probe` expected pass. Failing probes retain their expected failures, while normal initial and both restores have none. The historical round-32 mistyped-path exit-2 attempts were setup errors of that earlier replay, not round-33 outcomes.

## Limits, commands, and disposition

I inspected the LOG, all eight wave-one reports, the independent verifier, source/artifact diff, raw normal and invalid receipts, and prior normal. My only shell checks in this adjudication relevant to the verdict were:

- `git status --short && git diff --stat b8e3e5c && git diff --name-status b8e3e5c` — **exit 0**; checked source, LOG, new artifact, and receipt/report worktree state.
- `git rev-parse HEAD` — **exit 0**; returned clean-before `b8e3e5c8de6ee0f82d87f6187437991b73b56073`.
- `git diff b8e3e5c -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py && git diff --check` — **exit 0**; confirmed the narrowly scoped source diff and no whitespace errors.
- `git diff --quiet b8e3e5c -- .shokunin/audio/corpus/artifacts && git diff --check` — **exit 0**; no tracked canonical artifact difference or whitespace error. The new, untracked WAV was separately inspected and SHA-256 checked.

I did **not** run a new measurement runner, builder, listening test, or production engine; runner command/exits are the named non-author verifier's exact 31-row table, not mine. My direct Python receipt inspection confirmed the 14-entry normal payloads, third-file metrics, both UI-family values, eight invalid rows, old-metric/threshold/five-generic-comparison preservation, and initial/#30/#31 restoration. There is no demonstrated scoped harm, but strict external JSON consumer compatibility was not tested. Do not infer auditory quality, perceptual distinctness, production readiness, rights clearance, engine behavior, publishing permission, or promotion. Four SHONEN boxes remain checked; **no rank change**. Parent may integrate the admitted scoped audio work and report-last receipt, but this adjudicator neither edits shared sources nor commits, pushes, merges, or publishes.
