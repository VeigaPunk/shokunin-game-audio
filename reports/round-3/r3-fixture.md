# Round 3 fixture reviewer: join indices, counterexample, quantization

## Scope and method

I reviewed the declared join formula and read the three clean loop WAVs (`ambience`, `ambience_alt`, `stem`) as PCM16 using Python's `wave` module and NumPy. I did not run a shell command, edit fixtures, or make perceptual claims. No shell command/exit code applies.

For an N-sample mono loop `x[0:N]`, playback wraps from `x[N-1]` to `x[0]`. The existing endpoint jump is `abs(x[0] - x[N-1])`. The proposed first-difference comparison, with both differences oriented forward in time, is:

```
incoming = x[N-1] - x[N-2]   # last in-loop step before the wrap
outgoing = x[1] - x[0]       # first in-loop step after the wrap
slope_delta = abs(incoming - outgoing)
```

This compares the neighboring in-loop slopes on either side of the join; it does not compare the wrap interval's slope to either neighbor. Keep the endpoint jump check independently: equal slopes do not imply equal endpoint values, and endpoint equality alone says nothing about slopes. The formula needs at least two samples and assumes one channel / a single decoded sample sequence; a multi-channel implementation must define how channels are handled rather than silently flattening them.

## Clean PCM16 values

Each clean artifact has 96,000 samples at 48 kHz. In normalized full-scale units, the measurements were:

| Loop | endpoint delta | incoming | outgoing | slope delta |
|---|---:|---:|---:|---:|
| ambience | 22 LSB | 21 LSB | 22 LSB | 1 LSB |
| ambience_alt | 62 LSB | 62 LSB | 62 LSB | 0 LSB |
| stem | 373 LSB | 372 LSB | 373 LSB | 1 LSB |

One PCM16 LSB here is `1/32768 = 0.000030517578125` full scale. Therefore a candidate strict rejection rule `slope_delta > 1 LSB` accepts all three clean loops while allowing quantization-sized difference. This is only a bound matching this three-file clean distribution, not an audible or universal threshold. If the implementation uses `>= 1 LSB`, it rejects two of these clean fixtures. The local numerical threshold and strictness should be explicit in the receipt.

The values are consistent with PCM16 quantization: each decoded sample and adjacent difference lies on the PCM16 grid. Because the WAV source is PCM16, calculating integer tick differences (then normalizing by 32768) avoids hiding rounding choices. If the measurement decodes through float32, PCM16 values are exactly representable in float32, but the report should still state source bit depth and units. A different source bit depth or lossy decode would have a different quantization/noise floor; do not transfer this one-LSB bound to those cases.

## Equal-endpoint, discontinuous-slope counterexample

Take a PCM16 loop with `x[0] = x[N-1] = 0`, `x[1] = +0.5`, and `x[N-2] = +0.5` (other samples arbitrary and within full scale). Its endpoint delta is zero, but `outgoing = +0.5`, `incoming = -0.5`, and slope delta is `1.0` full scale (`32768` PCM16 LSB). It passes the endpoint test and exceeds the proposed clean-derived bound by a wide margin. This is a numerical counterexample to endpoint-only coverage, not a claim about what a listener hears.

## Limitation

The metric is a local discrete first-difference mismatch. It is not a derivative estimate with a physical-time normalization unless divided by the sample interval; because all fixtures share 48 kHz, the unnormalized sample difference is consistent for this local comparison. Neither endpoint nor slope checks establish seamless playback, codec behavior, or perceived quality.
