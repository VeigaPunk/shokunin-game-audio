# Round 31 alternative analytic fit

## Scope

Independent scratch-only parameter sweep for the joint nonzero-below control. Scratch files are under `.shokunin/audio/corpus/live/round-31/alt/`; no shared fixture, measurement code, LOG, scorecard, canonical artifact, or other report was edited. No commit/push.

## Fit and measured result

Used the existing UI-shaped analytic construction from the duration/centroid probes: `0.38 * sin(2π * (700*k*t + 800*k*t*t)) * exp(-30*t)`, sampled at 48 kHz and quantized to mono PCM16. Base uses 5760 frames and `k=1`; alternative uses 6719 frames and `k=0.88`. A coarse sweep of `k=0.85..1.15` in 0.005 increments found several nonzero centroid differences below 10%; `k=.88` measured near the upper bound. The fit is an empirical FFT-centroid sweep, not an inference from phase parameters.

Measured from the decoded SoX float samples with the same whole-waveform positive-frequency magnitude-weighted FFT centroid definition as `measure_audio.py`:

| | frames | duration | centroid |
|---|---:|---:|---:|
| base | 5760 | 0.120000 s | 966.896659 Hz |
| alternative (`k=.88`) | 6719 | 0.139979 s (ffprobe rounded) | 870.554723 Hz |

Duration delta from frame counts: `959/48000 = 0.019979166666666666 s` (below `.020`). Absolute relative centroid delta: `abs(870.554723-966.896659)/966.896659 = 0.09964036511023155` (nonzero and below `.10`). Thus both measured distinctness branches are false while both values are nonzero. Separate UI-shaped duration bounds are `.12` and `.16` per existing fixture convention; both durations are in that range. The alternative is longer than `.12 s` and does not conform to the canonical UI duration. This is only numeric fixture evidence; no perceptual or exact-cutoff-equality claim.

## Shell evidence (exact commands and exits)

- `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-31/alt/ui_base.wav` — exit 0; PCM16, mono, 48000 Hz, 0.120000 s.
- `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-31/alt/ui_alt.wav` — exit 0; PCM16, mono, 48000 Hz, 0.139979 s.
- `sox .shokunin/audio/corpus/live/round-31/alt/ui_base.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-31/alt/ui_base.f32` — exit 0.
- `sox .shokunin/audio/corpus/live/round-31/alt/ui_alt.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-31/alt/ui_alt.f32` — exit 0.

Correction: the two SoX commands actually run used `.shokunin/audio/...` (not `.shokhin`). Both exited 0. No shell command failed. The requested integrated distinctness reject was not run: canonical checker has no round-31 probe mode or scratch spec, and this lane must not edit shared measurement code. This report therefore does not claim an integrated rejection or ordinary checker pass receipt.

## Failed fits / limits

No setup or shell failure. The coarse sweep produced multiple usable parameters; no failed fit is being hidden. It is a coarse discrete sweep, not a continuous optimum. Because the integrated checker was not run on these artifacts, format/duration/distinctness behavior here is measured independently, not certified by a checker receipt. No exact cutoff equality, perceptual similarity, rights, engine, publish, or promotion claim.
