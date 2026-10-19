# Round 101 — C3 no-harm repair review

## Original C3 claim retained

Depth: the opt-in `--probe-truepeak-r101` measures sample peak, true peak, overshoot, and mono/dual-mono LUFS on all 17 canonical fixtures, using positive and negative controls. The continuation did not alter or replace C1/C2/C3.

## Before-state and falsifiers

- The read-only continuation scribe inspected base `defbe128`: the original `measure_audio.py` invoked `build_artifacts.py` before probe dispatch; `build_artifacts.py` targets `corpus/artifacts` and writes WAVs there. The in-flight C3 code therefore regenerated canonical inputs before measuring them. Scribe evidence: `W2RoundAudioCont.C3BeforeStateScribe`; base builder line locations and observed command are recorded in the task output and in lesson M23.
- The original control oracle read the generated PCM16 WAV to derive the expected overshoot from that same signal. A phase-0 positive-control mutation could then produce an observed 0 dB and a same-signal expected 0 dB. The pre-repair receipt's positive control measured +2.999335 dB against the derived +3.0103 dB; the negative control measured 0.0 dB against derived 0.0 dB. Lesson M24 records this falsifier.
- The independent control scout derived +3.0102999566 dB for a 12 kHz fs/4 sine at phase π/4 (`20·log10(√2)`) and 0.0 dB at phase 0. PCM16 quantization changes absolute levels, but not the four-sample sinusoid ratio; ±0.08 dB accommodates the observed FFmpeg metadata/filter residual.
- The connector found no sibling-lane ownership overlap or province crossing; the fixtures and measurement harness are audio-owned.

## Landed repair (reviewed statically; L1 execution follows)

- `corpus/fixtures/measure_audio.py`: the builder command is guarded by `if not args.probe_truepeak_r101`, preserving legacy modes while making the new mode read existing canonical fixtures. Its controls, FFmpeg logs, and receipt share `corpus/live/round-101-truepeak/<run-id>/`. The receipt path reuses the probe-created run directory with `exist_ok=True`.
- The analytic oracle is name-keyed (+3.0103 dB / 0.0 dB, ±0.08 dB); `_truepeak_r101_control_overshoot_matches` now gates control acceptance independently. Quantized-PCM expectation remains a separate cross-check.
- `corpus/fixtures/test_truepeak_r101.py` contains 10 hermetic tests: six parser cases, analytic positive/negative acceptance, truepeak dispatch with a builder-call spy and round-scoped receipt, and default-mode dispatch proving the legacy builder call remains present. The tests have not been run by L2.
- New mistake/quality pairs are `corpus/lessons/round-101.md` M23/Q21 (canonical fixture writes/output scope) and M24/Q22 (independent control oracle). The current quality bar is Q1–Q22.

## Final read-only review verdicts

- Reviewer: no actionable finding remains in scope; confirmed builder separation, round-scoped outputs, independent control oracle, 144 single-flag plus all-false mode/suffix equivalence (0 mismatches), and both CLI dispatch tests. No tests/builds were run by the reviewer.
- Critic: no remaining static C3/no-harm blocker; confirmed a phase-0 positive control fails the analytic oracle, the truepeak path skips the builder, legacy modes still call it, and the test receipt stub matches the run directory. No tests/builds were run by the critic.
- The L1 still owns the real probe, parser/dispatch tests, and canonical-artifact immutability check after commit; their outputs are appended in the final measurement record.

## L1 integration results — measured on `d00a8d229645c41fab39b4cdc2f396f64216b581`

- `python3 corpus/fixtures/test_truepeak_r101.py` → 10 tests, OK.
- `timeout 900 python3 corpus/fixtures/measure_audio.py --probe-truepeak-r101` → exit 0; `failures: {}`; `coverage_blocked: {}`. The receipt is `corpus/live/round-101-truepeak/20261019T233319127994Z/measurements.json`, with 17 finite artifact true peaks. Positive control overshoot is +2.999335 dB against independent +3.0103 dB (error 0.010965, tolerance 0.08); phase-0 is 0.000 dB against 0.0; dual-mono control is +3.010 LU.
- Canonical inputs remained byte-identical: `sha256sum corpus/artifacts/*.wav | sha256sum` matched before/after at `f4e1eb8db062802426fb68ce528212d9d4219e8fd698857658529933020410a9`; `git status --porcelain -- corpus/artifacts` emitted nothing; `git diff --quiet defbe128 -- corpus/artifacts` exited 0.
- Default-mode integration in a temporary copy returned rc 0, empty failures/coverage blocks, 17 WAVs, and normal receipt SHA-256 `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`, matching the pinned r81–r83 receipt. The temporary directory was removed by the run context.
