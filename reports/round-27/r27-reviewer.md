# r27 reviewer — minimal opt-in route

The existing distinctness predicate is `abs(variant.duration_s - base.duration_s) >= .020 or centroid_relative_delta >= .10`. Round 26's exact duplicate is a zero/zero case, not a duration-boundary calibration. Recommend exactly two opt-in runner modes, each generating its own original PCM16 48 kHz mono matched pair. Keep all existing thresholds and modes unchanged; do not add a generic duration-probe framework.

| Opt-in mode | Baseline | Variant frames / declared duration spec | Intended result |
|---|---:|---:|---|
| `--probe-ui-duration-below` | 5760 / 0.120 s | 6719 / `0.1399791666667` s (959/48000 delta = `0.0199791666667` s) | Variant passes its own ordinary measurement; pair fails distinctness on duration, while centroid-relative delta remains `< .10`. Runner exit 1, solely the expected distinctness failure. |
| `--probe-ui-duration-at` | 5760 / 0.120 s | 6720 / `0.140` s (960/48000 delta = `0.020` s) | Variant passes its own ordinary measurement; pair passes distinctness if the observed duration delta compares `>= .020` and centroid delta remains `< .10`. Runner exit 0. |

Use per-file duration specs for both members: baseline `(0.120, 250, 4000, False)` and each variant `(0.1399791666667, 250, 4000, False)` or `(0.140, 250, 4000, False)`. This is essential: measuring the longer file against the existing 0.120 s UI spec would yield `duration: outside ±1 ms`, which is not the distinctness result under test. Leave the existing `SPECS["ui"]` and other canonical specs unchanged. Keep both sample sets in the existing UI spectral band and verify measured centroid contrast stays below 10%; frame truncation/quantization may alter it.

After implementation, the exact runner invocations should be:

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below
# expected exit 1: only the below-threshold variant's distinctness failure
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at
# expected exit 0: no measurement or distinctness failures
```

These are proposed commands/outcomes, **not executed by this reviewer**. A zero exit for `below` or a failure other than distinctness invalidates the intended isolation; nonzero for `at` is a failed fit unless the receipt establishes another setup/measurement error. Do not change `.020` to force a desired result. Compare actual receipt floats: binary rounding may make the nominal 0.140−0.120 difference fall below `.020`; report that honestly as a failed fit and adjust the source-generated duration only if the claim is explicitly revised. Likewise report centroid leakage, format/level failures, or failed per-file duration fits rather than calling them distinctness outcomes.

Scope: this would test these source-generated PCM16 cases against the existing duration comparator, not perceptual similarity, boundary behavior of the centroid comparator, audio quality, rights, engine behavior, publication, or promotion. No source or shared file was edited; this report is the only intended write.
