# Round 8 simplifier — parameterize the existing section contrast

Scope: implementation-design recommendation only. I inspected the declared round-8 claim in `.shokunin/audio/LOG.md` and the existing measurement implementation. I did not edit shared source, fixtures, LOG, SCORECARD, or canonical assets, and did not run an audio or perceptual test.

## Recommendation

Keep one `section_contrast` implementation and add an optional component-frequency argument, retaining 30 Hz as the default so the existing `stem_sections` behavior is unchanged:

```python
def section_contrast(path, component_hz=30):
    ...
    bin_index = round(component_hz * len(halves[0]) / rate)
    amps = [float(2 * abs(np.fft.rfft(half)[bin_index]) / len(half))
            for half in halves]
    ...
    return {"component_hz": component_hz, ...}
```

Here `rate` should come from the WAV metadata (or be the existing contract constant 48000 if metadata validation guarantees it); the existing `measure()` already probes sample rate. With 96,000 samples per section at 48 kHz, exact-bin tones at 30 Hz and 120 Hz use FFT bins 60 and 240 respectively. Avoid hard-coding either bin. The candidate's 120 Hz analytic tone is bin-aligned for the declared duration, so this preserves the existing single-bin amplitude method without introducing a second checker.

Call it for `stem_sections` with the default and for `stem_layer` with `component_hz=120`. The flat120 control should use the same 120 Hz call. Keep the same validity checks (`amps >= .01`, section RMS `>= .001`) and contrast threshold (`>= 6 dB`) in this one function. The contrast test alone distinguishes the proposed .012-to-.060 layer from .036-to-.036 flat control; do not duplicate those gates in the CLI branch. Use the returned frequency in failure text/receipt labels so the current `30 Hz` failure does not misdescribe the layer result. Keep probe dispatch/report plumbing separate from the contrast calculation.

If integer-bin support must be explicit, compute the nearest bin and reject a frequency that is not bin-aligned within a stated tolerance; do not silently add a Goertzel/nearest-bin behavior change in this bounded round. For the declared analytic inputs the exact-bin approach is sufficient. This proposal parameterizes only the measured component, not thresholds, section count, asset rules, or signal-quality claims.

## Commands / exits

I ran only this repository inventory command; it exited **0**:

```sh
git status --short; git ls-files
```

No audio measurement/build command was run. No PCM was created or analyzed in this report.
