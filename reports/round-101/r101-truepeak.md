# Round 101 — C3 True-Peak Measurement

Claim axis: **depth**. Scope: `corpus/fixtures/measure_audio.py`, parser tests, retained live evidence.

## Implementation

- Added the opt-in `--probe-truepeak-r101` path and fail-closed FFmpeg parser/helpers at `corpus/fixtures/measure_audio.py:54370-54941`; the argument/exclusive-mode guard and dispatch are at `:55080`, `:55093-55094`, and `:55211-55213`. The `mode` and `suffix` selectors are at `:56641` and `:56661`.
- For all 17 `SPECS` WAVs, the probe runs `ebur128=metadata=1:peak=sample+true,ametadata=mode=print` twice: default mono and `dualmono=true`. It records SP, TP, overshoot, integrated I (null at `-inf` or `<= -70`), metadata-vs-summary source/precision per field, NumPy-decoded sample-peak cross-check, and `exceeds_minus1_dbtp` as telemetry only. Missing, malformed, or ambiguous summary/peak output is a failure; missing required numeric peaks fail the probe.
- Added quantized PCM16 controls under `corpus/live/round-101-truepeak/controls/`: 12 kHz phase-π/4 and phase-0 tones, both 2.5 s with a 5 ms raised-cosine fade-in, plus a steady 1 kHz dual-mono control. FFmpeg logs for each mono/dual pass are retained under `corpus/live/round-101-truepeak/ffmpeg/<run-stamp>/`.
- `corpus/fixtures/test_truepeak_r101.py:1-127` contains hermetic fixed-stderr parser tests. `measure()`, `SPECS`, and existing probe bodies were not edited.

## Verification and retained evidence

- `python3 -m pytest -q corpus/fixtures/test_truepeak_r101.py` → unavailable (`No module named pytest`). Required fallback `python3 corpus/fixtures/test_truepeak_r101.py` → **6 tests, OK**.
- Final command, twice: `timeout 900 python3 corpus/fixtures/measure_audio.py --probe-truepeak-r101` → **exit 0**, `failures: {}`, `coverage_blocked: {}` both times.
  - `corpus/live/runs/20261019T222216086962Z-truepeak-r101/measurements.json`
  - `corpus/live/runs/20261019T222222270145Z-truepeak-r101/measurements.json`
  - Both SHA-256: `6b9e1fb8ee78007d5602e841ef738122474662ad0ef84b48040c3630109eff6e` (byte-identical, hence numeric-identical).
  - Final log directories: `corpus/live/round-101-truepeak/ffmpeg/20261019T222214915290Z/` and `.../20261019T222221081891Z/`; each holds the 40 per-pass logs for 17 artifacts + 3 controls. The three deterministic PCM16 control WAVs are in `.../controls/`.
- Normal mode: `timeout 900 python3 corpus/fixtures/measure_audio.py` → **exit 0**, `failures: {}`, `coverage_blocked: {}`. Retained receipt directory: `corpus/live/runs/20261019T222229360101Z-normal/`; receipt SHA-256 `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`, exact match to the r81-r83 pin.
- No-harm diff: `git -C /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/audio-shokunin diff --stat -- corpus/fixtures/measure_audio.py` → `582` lines changed; `--numstat` → `580  2`. The only two deletions are the old one-line `mode` and `suffix` ternary selector lines, each replaced by the same existing ordered arms plus the new r101 arm (the `mode` expression is parenthesized); all old selector outcomes are retained. Every other fixture change is additive.

## Measurements

FFmpeg n9.0.1 emitted `lavfi.r128.sample_peak`, `lavfi.r128.true_peak`, and `lavfi.r128.I`; the receipt uses the available 0.001-linear-amplitude peak metadata converted to dB and 0.001-LU I metadata. Per-field fallback is the ebur128 summary at 0.1 dB/0.1 LU and is explicitly labelled in the receipt. Every canonical sample-peak comparison against NumPy decoding passed within the recorded metadata precision; all 17 artifacts have finite mono and dual-mono SP/TP.

| Artifact | SP dBFS | TP dBTP | TP−SP dB | I mono / dual / Δ LU | > −1 dBTP |
|---|---:|---:|---:|---|:---:|
| ui | -8.496243 | -8.496243 | 0.000000 | floor / floor / — | no |
| ui_alt | -9.924186 | -9.924186 | 0.000000 | floor / floor / — | no |
| ui_third | -8.496243 | -8.496243 | 0.000000 | floor / floor / — | no |
| impact | -1.841030 | -0.658405 | +1.182625 | floor / floor / — | **yes** |
| impact_alt | -2.429564 | -2.429564 | 0.000000 | floor / floor / — | no |
| impact_third | -6.820703 | -6.707160 | +0.113543 | -18.220 / -15.210 / +3.010 | no |
| movement | -5.368225 | -5.051764 | +0.316461 | floor / floor / — | no |
| movement_alt | -3.889983 | -3.098039 | +0.791944 | floor / floor / — | no |
| movement_third | -6.196078 | -6.196078 | 0.000000 | floor / floor / — | no |
| ambience | -15.139239 | -15.139239 | 0.000000 | -30.697 / -27.686 / +3.011 | no |
| ambience_alt | -13.979400 | -13.979400 | 0.000000 | -24.688 / -21.677 / +3.011 | no |
| ambience_third | -12.956350 | -12.956350 | 0.000000 | -18.992 / -15.982 / +3.010 | no |
| stem | -9.789100 | -9.789100 | 0.000000 | -15.761 / -12.750 / +3.011 | no |
| stem_sections | -15.289431 | -15.289431 | 0.000000 | -24.704 / -21.694 / +3.010 | no |
| stem_layer | -24.436975 | -24.436975 | 0.000000 | -29.259 / -26.249 / +3.010 | no |
| stem_layer_alt | -26.020600 | -26.020600 | 0.000000 | -32.698 / -29.688 / +3.010 | no |
| stem_layer_third | -26.020600 | -26.020600 | 0.000000 | -32.628 / -29.618 / +3.010 | no |

## Controls, discrepancy, and risks

- Positive control's quantized 4-sample PCM16 period `[11585, 11585, -11585, -11585]` predicts SP `-9.031078`, TP `-6.020778`, overshoot `+3.010300 dB`; measured SP `-9.019935`, TP `-6.020600`, overshoot `+2.999335 dB`. Overshoot error `0.010965 dB` passes the measured `±0.08 dB` tolerance. Negative phase-0 control measured SP=TP=`-6.020600`, overshoot `0.000000 dB`, within `±0.08 dB`. Tolerance comments explain the critic's faded 12 kHz observation (+3.026 vs ideal +3.010); the summary-only fallback expands peak tolerance to the two 0.1 dB half-steps plus 0.02 dB.
- Steady 1 kHz dual-mono control: I mono `-9.030`, dual `-6.020`, Δ `+3.010 LU`, passes `+3.0103 ±0.002 LU` (0.001-LU metadata rounding per pass).
- **Measured specification discrepancy:** the task's expected `8 gated / 9 short-floor` split is reversed for the checked-in `SPECS` and this receipt. Actual set: **8** files at `<=0.36 s` return the `-70` floor (`ui`, `ui_alt`, `ui_third`, `impact`, `impact_alt`, `movement`, `movement_alt`, `movement_third`); **9** clear the gate, including `impact_third` (0.40 s). Their dual-mono offsets are `+3.010/+3.011 LU`. The probe encodes the observed SPECS-derived `9 gated / 8 floor` census and exits green; it does not misreport the input expectation.
- An initial pre-correction attempt is retained at `corpus/live/runs/20261019T221921076914Z-truepeak-r101/measurements.json` (exit 1) because the first draft expected the reversed 8/9 split; the receipt otherwise records the measured rows/controls. Corrected final runs are the two identical green receipts above.
- LSP was unavailable in this environment (no LSP tool exposed; `command -v pyright-langserver`, `pylsp`, and `jedi-language-server` found none); source locations were inspected with repository reads/search. No remaining implementation blocker. Risk is limited to the recorded source-expectation discrepancy and the documented FFmpeg metadata/summary precision.
## Correction — selector compatibility (post-review)

An adversarial review found that the first selector rewrite omitted the existing `probe_ui_route_act_84_r63` and `probe_ui_route_act_00_r63` arms from both `mode` and `suffix`; those two probes would have been labelled `normal`. Both selector lines are now the original `defbe128` expressions with only the `--probe-truepeak-r101` arm prepended. This corrects the earlier compatibility statement above; no earlier report text was rewritten.

- Exhaustive single-flag comparison against `git show defbe128:corpus/fixtures/measure_audio.py`, including the all-false case: `mode: 144 flags incl r101, plus none; mismatches=[]`; `suffix: 144 flags incl r101, plus none; mismatches=[]`. The new flag maps to `probe-truepeak-r101` / `-truepeak-r101`; every old selector keeps its prior value.
- `python3 corpus/fixtures/test_truepeak_r101.py` → 6 tests, OK.
- Post-fix `timeout 900 python3 corpus/fixtures/measure_audio.py --probe-truepeak-r101` → exit 0, `failures: {}`, `coverage_blocked: {}`; receipt `corpus/live/runs/20261019T224242100746Z-truepeak-r101/measurements.json` (17 artifact rows; all failures empty; SHA-256 `6b9e1fb8ee78007d5602e841ef738122474662ad0ef84b48040c3630109eff6e`).
- Post-fix normal mode → exit 0, `failures: {}`, `coverage_blocked: {}`; receipt `corpus/live/runs/20261019T224248272957Z-normal/measurements.json`, SHA-256 `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` (r81-r83 pin match).
- Final `git diff --numstat -- corpus/fixtures/measure_audio.py` → `580  2`; the two removed lines are the old selector expressions replaced with the original expressions plus the new arm.

