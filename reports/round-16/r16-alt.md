# Round 16 alternate: `reverse180_other.wav`

## Result

I independently generated `.shokunin/audio/corpus/live/round-16/reverse180_other.wav` by synthesizing the same 4-second, 48 kHz mono, signed PCM16 180 Hz sinusoid as the canonical alternate layer, but reversing the section amplitudes: first 96,000 frames at 0.050 FS, second 96,000 at 0.015 FS. SHA-256: `c04441ef1ef6c02970e0c946efe0c750b19d3f41ef26865ce37e608ecda4e7d8`. No canonical artifact or source was modified. This alternate scratch is deliberately independent of a one-frame mutation: 191,520 of 192,000 PCM values differ from canonical.

Measured after SoX float32 decode, with the existing fixture formulas:

| Check | Measurement | Existing bound | Outcome |
|---|---:|---:|---|
| 180 Hz first/second section component amplitudes | 0.04999787 / 0.01499992 FS | each >= .01 FS | pass |
| Signed second/first contrast | -10.45725057 dB | >= +6 dB | **fail (target)** |
| Internal join adjacent-sample gap | 0.00119019 FS | <= .03 FS | pass |
| Internal join side-slope mismatch | 0.00079346 FS/sample | <= .001 FS/sample | pass |
| Whole-file centroid | 277.9514 Hz | 100–2000 Hz | pass |
| Peak / RMS | 0.04998779 FS / 0.02609974 FS | peak < .95; RMS >= .001 | pass |
| Outer endpoint gap / side-slope mismatch | 0.00036621 FS / 0.00085449 FS/sample | <= .03 / <= .001 | pass |
| Rate / channels / duration | 48,000 Hz / mono / 4.000 s | 48 kHz mono / 4 s ±1 ms | pass |

Both section RMS values also exceed .001 FS (0.03535384 and 0.01060655). Thus the section amplitudes are valid and the negative signed contrast is the only failure among the measured generic, format, level, centroid, outer-seam, internal-gap/slope, and section gates. This is candidate evidence from the existing measurement formulas, not an integrated runner replay or an assertion about audio quality.

## Explored fits and failed fits

- **Selected reverse fit:** amplitudes 0.050/0.015 FS. The negative contrast is -10.45725 dB while both sections exceed the .01 FS validity minimum; all other listed checks pass.
- **Shallower reverse attempt:** 0.050/0.030 FS yielded -4.43695 dB, so it was not a negative at or beyond the existing 6 dB bound. Its gap was 0.00119019 FS and slope 0.00045776 FS/sample. Not selected.
- **Invalid-amplitude attempt:** 0.008/0.015 FS yielded first component 0.00799951 FS, below the existing .01 FS minimum. Contrast was consequently undefined under the fixture validity rule; it is not a valid negative contrast example. Not selected.

## Reproducibility and commands

Candidate synthesis used Python REPL `wave`/NumPy to form the 180 Hz sinusoid, apply the two section amplitudes, quantize with `round(clip(x,-1,1)*32767)` to signed little-endian PCM16, and write the scratch WAV. Exact shell command and exit:

```text
sox .shokunin/audio/corpus/live/round-16/reverse180_other.wav -t f32 -e floating-point - > /tmp/reverse180_other.f32
exit 0
```

I initially made a shell invocation mistake by passing the command as one quoted executable (not a valid command); that setup attempt failed and is not measurement evidence:

```text
"sox .shokunin/audio/corpus/live/round-16/reverse180_other.wav -t f32 -e floating-point - > /tmp/reverse180_other.f32"
exit 127
```

No fixture runner probe was run because round-16 runner integration is outside this leaf assignment. No audio was auditioned. No claim is made about audible seamlessness, musical quality, adaptive engine behavior, rights, external compatibility, or production suitability.
