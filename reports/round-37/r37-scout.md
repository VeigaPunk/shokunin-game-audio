# Round 37 scout — existing probe wiring and baseline receipts

## Scope and method
Read-only inspection of `.shokunin/audio/corpus/fixtures/build_artifacts.py`, `measure_audio.py`, the declared Round 37 LOG entry, and committed/live measurements. No source, LOG, scorecard, canonical asset, or other report was changed. **No shell commands were run**, so there are no shell command/exit receipts to report; the inspection was through the Python REPL. No new measurements or scratch fits were run.

## Existing opt-in UI probe wiring
`measure_audio.py` exposes one-mode-at-a-time argparse flags for UI probes. Each selected branch invokes `build_artifacts.py` with the corresponding flag; the builder writes named scratch WAVs under `corpus/live/round-N/`. The measurement runner measures all canonical SPECS and adds the scratch pair to `measurements`, then applies the shared `_alt` distinctness rule: pass if absolute duration difference is at least `.020 s` **OR** relative spectral-centroid difference is at least `.10`. A failed pair gets `distinctness: duration < .020 s and centroid delta < 10%` on the variant. Runner writes JSON receipt to a timestamped `corpus/live/runs/*-ui-*/measurements.json` and exits nonzero when any measurement has failures. These checks are numeric fixture controls only.

Current UI examples:

- `--probe-ui-clone`: identical 0.12 s decaying 700 Hz chirps, scratch `round-26`; deliberate exact-duplicate negative.
- `--probe-ui-duration-below` / `--probe-ui-duration-at`: shared chirp synthesis; baseline 5760 frames (0.12 s), alternate 6719 frames (0.139979 s) or 6720 frames (0.14 s), `round-27`. At-boundary duration delta is 0.020 s; below is one sample under.
- `--probe-ui-centroid-below` / `--probe-ui-centroid-above`: equal-length chirps with frequency multiplier 1.11 / 1.10, `round-28`; measured values calibrate around the 10% centroid bound.
- `--probe-ui-joint-below`: same chirp with 6719-frame duration and multiplier .88, `round-31`; both OR arms below threshold.
- `--probe-ui-mixed-pass`: 6719-frame alternate with multiplier 1.14, `round-32`; duration arm below, centroid arm above, expected pass. Additional lower-centroid and orientation controls are similarly opt-in.

The live receipts show that the framework reports pair-level distinctness and leaves canonical fixture checks in the same receipt. For example, `20261013T035443299028Z-ui-joint-below` has UI alternate duration delta `0.019978999999999997`, relative centroid delta `0.09964036511023265`, and distinctness failure; `20261013T035442203152Z-ui-mixed-pass` has the same duration delta and centroid relative delta `0.1059638814557548`, no failure. These are UI-class SFX controls, not the ambience-family control declared for this round.

## Ambience synthesis and numeric baseline
The current builder’s canonical ambience generation is deterministic 48 kHz mono PCM16 (`save` rounds clipped samples to little-endian int16): a 2.0 s baseline sum of 12/36 Hz sines, an alternate sum of 20/60/100 Hz sines, and a third sum of 90/130 Hz sines. `measure_audio.py` SPECS set each ambience to 2.0 s, centroid band 5–200 Hz, looping enabled. The numeric loop checks are endpoint absolute difference `<= .03` full scale and endpoint-slope mismatch `<= .001` full scale/sample; ordinary checks include PCM16/48 kHz mono, duration tolerance ±1 ms, peak `<.95`, RMS `>=.001`, and centroid within band. Existing `ambience_family_comparisons` compare `ambience_third` to both baseline and `_alt` using the generic `.020 s OR .10` distinctness rule.

Round 36 normal baseline receipt: `corpus/live/runs/20261013T035209336280Z-normal/measurements.json` (receipt says `mode: normal`, no measurement failures). Baseline ambience: 2.0 s, centroid `36.61640767851373 Hz`, peak `0.174591064453125`, RMS `-18.153351293681563 dBFS`, endpoint delta `0.00067138671875`, slope mismatch `3.0517578125e-05`; alternate centroid `58.01919713436623 Hz`, peak `0.199737548828125`, RMS `-17.67032381358842 dBFS`, endpoint delta `0.00189208984375`, slope `0`. Third canonical fixture centroid `112.03210352691181 Hz`, endpoint `0.002777099609375`, slope `0`; both family comparisons have duration delta `0.0` and centroid-relative deltas `2.059614818322321` and `0.9309488765840295`, passing the OR rule. The round36 LOG records 17 canonical entries and SHA `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` for the third fixture; that is baseline context, not a Round37 negative fit.

## Setup vs numeric fit; scope boundary
This is a wiring/baseline survey only. No Round37 ambience negative-control pair was synthesized or numerically fitted here; no result is claimed for `--probe-ambience-centroid-below`. Existing successful receipts establish that the runner/builder path and canonical numeric measurements work in prior modes, not that a new scratch pair meets the requested `<.10` centroid delta with exactly equal duration and passes loop/ordinary checks. A failed CLI invocation before receipt generation would be setup evidence, not a numeric fit; no invocation was attempted here.

All numbers are control measurements under the project’s rules. They do **not** establish perceived similarity or difference, audible seamlessness, musical quality, production suitability, rights, engine/publish readiness, or promotion.
