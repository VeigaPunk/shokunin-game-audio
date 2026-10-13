# Round 30 alt — independent swapped-orientation fit

## Result
Independent source generation and direct measurement reproduce the declared candidate. The two forward/reverse pairs are byte-identical by role swap (SHA-256 below). Both WAVs individually meet the existing canonical UI ordinary checks: 48 kHz, mono, PCM16, 5760 frames / 0.120000 s, peak below .95, RMS above .001, centroid within 250–4000 Hz. Duration difference is zero.

| Pair role | Phase multiplier | Frames; duration | Centroid (Hz) | Existing ordinary UI checks |
|---|---:|---:|---:|---|
| forward baseline | 1.00 | 5760; .120000 s | 966.8966593379727 | pass |
| forward variant | .95 | 5760; .120000 s | 871.155504521436 | pass |
| reverse baseline | .95 | 5760; .120000 s | 871.155504521436 | pass |
| reverse variant | 1.00 | 5760; .120000 s | 966.8966593379727 | pass |

With the declared baseline-denominator calculation `abs(variant - baseline) / baseline`, forward is `0.09901901500217196` (< .10), while reverse is `0.10990133715464667` (> .10). Thus these measurements support a forward-below / reverse-above threshold outcome solely for the same pair of bytes assigned to opposite roles. They directly exhibit the orientation dependence of this baseline-denominator ratio; they do not establish a perceptual, symmetry-normative, or general audio claim.

## Exact byte identity
- forward-base.wav and reverse-variant.wav: `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`
- forward-variant.wav and reverse-base.wav: `6e626b9b5b177cd6f7ba986758b12ec612cf003f9947bd170b766f1652d9bac2`

## Procedure and commands
Generated 48 kHz mono PCM16 WAVs in `.shokunin/audio/corpus/live/round-30/alt/` using the round-29 analytic source formula for 0.12 s: `round(clip(.38*sin(2*pi*k*(700*t+800*t*t))*exp(-30*t), -1, 1)*32767)` cast to little-endian int16, with `t = arange(5760)/48000`; `k=1.0` and `.95`. The same sample arrays were written to swapped base/variant filenames. `measure_direct.py` in that scratch directory directly invokes ffprobe and SoX, calculates the whole-waveform positive-frequency magnitude-weighted FFT centroid, and prints measured file metadata/levels. It does not invoke the fixture builder, checker, or comparator.

Exact shell commands run (exit status):

```text
python3 "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-30/alt/measure_direct.py" "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-30/alt/forward-base.wav" "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-30/alt/forward-variant.wav" "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-30/alt/reverse-base.wav" "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-30/alt/reverse-variant.wav"  # 0
sha256sum "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-30/alt/forward-base.wav" "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-30/alt/forward-variant.wav" "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-30/alt/reverse-base.wav" "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-30/alt/reverse-variant.wav"  # 0
```

No failed fit or setup attempt is used as evidence. No source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push was made. This report makes no claim about perceptual similarity, symmetry as a normative expectation, rights, engine behavior, publishing, or promotion.
