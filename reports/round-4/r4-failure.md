# Round 4 flat-section negative control

**Scope:** negative-control scratch only. This is an original synthesized WAV; no borrowed samples, engine/canon edits, or perceptual claim.

## Artifact and construction

`corpus/live/round-4/flat_probe.wav` is mono, 48,000 Hz, signed PCM16, exactly 4.000 s (192,000 samples). SHA-256: `7189005218eb1ed24292186f3023d49e5d0f7d9cc786b3943d18113477bda62f`.

Exact recipe (NumPy, with `t = np.arange(192000)/48000`):

```python
u = np.clip((t - 1.8) / 0.4, 0, 1)
blend = 0.5 - 0.5 * np.cos(np.pi * u)
e = np.minimum(np.clip(t / 0.1, 0, 1), np.clip((4 - t) / 0.1, 0, 1))
edge = 0.5 - 0.5 * np.cos(np.pi * e)
x = 0.22*np.sin(2*np.pi*440*t) + edge*(
    0.13*(1-blend)*np.sin(2*np.pi*660*t) +
    0.13*blend*np.sin(2*np.pi*880*t))
pcm = np.rint(np.clip(x, -1, 1)*32767).astype('<i2')
# Write pcm as 1-channel, 2-byte/sample, 48000-Hz WAV.
```

The named component for the flattened-section control is the 440-Hz sinusoid. It is present at constant amplitude in both contiguous 2-s sections. As an independent decoded-PCM check, take `abs(rfft(section)[440])**2` for each 96,000-sample section (bin spacing is 0.5 Hz); results are `111506745.8221424` and `111507066.22880337`, a difference of `+0.00001248 dB` (rounding/leakage). Thus it does not meet a >=6 dB section contrast requirement for that component. This is an analytic negative control, not evidence of an audible motif.

The file was designed with 0.1-s endpoint fades. Its decoded endpoint amplitude delta is `0.012664794921875` (<0.03), adjacent-slope gap is `0.000030517578125` (<0.001), peak is `0.332916259765625`, RMS is `0.1793676078670412`; it is not near-silent or clipping. These are measured fixture-local guards, not universal quality limits.

## Shell validation

Exact command:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,sample_fmt,bits_per_sample -show_entries format=duration -of json ".shokunin/audio/corpus/live/round-4/flat_probe.wav"
```

Exit: **0**. Output reports `sample_fmt=s16`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`, `duration=4.000000`.

No shared measurement script was changed or run: this probe is intentionally scoped to the proposed named-component section metric, which is not yet integrated. A verifier should independently measure the raw artifact and show the section-contrast test rejects it while endpoint/slope and ordinary format/level checks pass. No claim about perceived quality, playback, engine behavior, soundtrack narrative, or production readiness.
