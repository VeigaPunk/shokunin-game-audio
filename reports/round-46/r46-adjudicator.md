# Round 46 Sol adjudication — absolute lower UI centroid band

## Verdict and admission

**Admit the one declared calibration move, narrowly.** The two source-generated opt-in fixtures bracket the unchanged ordinary UI absolute lower centroid bound: the below fixture fails solely `spectrum: centroid outside fixture band`; the above fixture passes. The named non-author fresh replay confirms both while preserving the prior controls. Admission requires at least one improved axis and zero demonstrated scoped harm; this evidence meets that rule only at the numerical fixture-gate level.

| Axis | Judgment | Reason |
|---|---|---|
| Depth | **Unchanged** | No new validator semantics or causal isolation: the existing `SPECS["ui"] = (.12, 250, 4000, False)` and `if not spec[1] <= centroid <= spec[2]` remain intact. |
| Coverage | **Unchanged** | Two optional examples exercise an existing check; they do not expand ordinary acceptance, artifact families, or the previously replayed controls. |
| Calibration | **Improved** | Measured SoX-decoded, whole-wave magnitude-FFT centroids fall on opposite sides of 250 Hz, with the expected sole failure/pass and controlled format, duration, and levels. Fresh non-author receipts reproduce the result. |

The separate R29 relative pairwise distinctness test uses a `.10` centroid delta; it is not this per-file absolute 250–4000 Hz predicate. No exact-250 Hz equality case was exercised.

## Direct evidence inspected

I read the Round 46 declaration/integration/replay entries of `.shokunin/audio/LOG.md`; all eight wave-one reports (`r46-{scout,executor,alt,critic,reviewer,simplifier,scribe,guard}.md`); the named non-author `r46-verifier.md`; the raw new-probe, initial/final normal and invalid receipts; and the source diff against clean-before `803c5fbbc19576d980acc5578138522f91e644b0`. I parsed all 52 fresh receipt paths listed in the verifier command ledger: they exist and are unique, spanning `20261013T065600343881Z`–`20261013T065654336632Z`; ledger exits are **22 exit 0 / 30 expected fixture-validation exit 1**, and the inherited prior-50 subset is **21/29**. These exit-1 rows are recorded validator outcomes, not replay setup errors. The ledger in `r46-verifier.md` supplies each exact invocation, exit and receipt; I did not rerun 52 commands.

| Probe / fresh command | Receipt | SHA-256 of generated WAV | Actual centroid (Hz) | Peak FS / RMS dBFS | Outcome |
|---|---|---|---:|---|---|
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-below` — exit **1** | `corpus/live/runs/20261013T065601381736Z-ui-absolute-centroid-below/measurements.json` | `fff9d981fe76c9163ba6a0db851e498b15fe193a1597427c8b73993b4666bfdf` | **249.71389590882862** | `0.279754638671875` / `-18.327838866709165` | Sole spectrum-band failure |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-above` — exit **0** | `corpus/live/runs/20261013T065602421400Z-ui-absolute-centroid-above/measurements.json` | `6e453ff6cdf02e3fb72e0ebb0734f39a566a823841da8949187ad73d74a90a2a` | **250.3250670185918** | `0.27984619140625` / `-18.32783946042307` | No failures |

The SHA values also match the integrated generated WAV bytes I inspected. Both are original deterministic 5760-frame/0.12 s, 48 kHz mono PCM16 controls; both pass format/duration/peak `<.95` and RMS `>=.001` checks. Nominal oscillator frequencies **225/226 Hz are not** the measured centroids. For each new receipt the 17 canonical measurement entries and all other normal receipt fields except mode/extra probe match the initial normal receipt. Initial `20261013T065600343881Z-normal/measurements.json` and final `20261013T065654336632Z-normal/measurements.json` compare as equal complete JSON, with 17 canonical measurements and no failures. The raw invalid receipt `20261013T065649253843Z-invalid/measurements.json` has eight expected outcomes, including native16 expected pass and the seven expected rejection cases. The verifier records old-17 SHA/metrics and five generic `_alt` comparisons, four family groups/eight comparisons, thresholds/sections, and restores as preserved; historical canonical SHA was not newly recomputed by this adjudicator. `git diff --check 803c5fb -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` exited **0** and `git diff --quiet 803c5fb -- .shokunin/audio/corpus/artifacts` exited **0**. The source diff adds only two explicit opt-in generation/measurement modes; ordinary comparator and thresholds are unchanged.

## Falsification and limits

Executor's first nominal 230/270 Hz pair measured 253.80451803986455/293.3534382718592 Hz: both in-band, a **numeric bracket fit failure**, not evidence of a runner failure. The alternate's initial decaying candidates also failed numeric fits; one relative-path helper invocation exited 1 from **setup**, separately corrected. Its independent final 200/300 nominal pair has different SHA and measured centroids 202.48468234677034/302.47893043755806 Hz, reproducing polarity over a wider interval, but is not the integrated pair. The reviewer below-peak draft `.279754150390625` was corrected to `.279754638671875`: transcription, not a changed gate result. The scribe's earlier pending judgment concerned initial candidates before the final integrated pair and fresh replay. The four SHONEN checks reported in the round declared no promotion; this calibration admission does not imply rank change.

Isolation is **only at the gate level**. The two WAVs have different nominal frequencies, quantized samples, and complete FFT distributions. They do not isolate a single causal physical variable. No exact-250 equality, timbre, perceived quality/novelty, universal spectral calibration, production suitability, rights, engine behavior, publishing, or promotion is demonstrated. No shared source, LOG, scorecard, commit, push, or other report was edited by this adjudication.
