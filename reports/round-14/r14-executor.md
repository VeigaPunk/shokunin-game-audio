# Round 14 executor: `join180_candidate.wav`

## Candidate and recipe

Built the original 4 s, 48 kHz, mono PCM16 synthetic 180 Hz layer in the assigned scratch directory only:

`.shokunin/audio/corpus/live/round-14/join180_candidate.wav`

Source recipe follows `build_artifacts.py`'s existing `stem_layer_alt`: for `n=0..191999`, `t=n/48000`, `x[n] = (0.015 if t<2 else 0.050) * sin(2*pi*180*t)`. Quantize as `round(clip(x,-1,1)*32767)` to little-endian signed PCM16. Then set frame 96000 to `round(.040*32767)=1311`; set frame 96001 to `frame96000 + frame95999 - frame95998` (=1454). This adjusts only the join sample and its immediate right neighbor; all other frames retain the generated layer. The desired slope equality is exact in integer PCM here. WAV SHA-256: `e81f0a2331c718748a94c34218c9e956b4e5464901afc8d3cee5d71804b03781`.

Frames 95998..96001 as signed PCM16: `-287, -144, 1311, 1454`; decoded FS: `-0.008758812, -0.004394665, 0.040009766, 0.044373913`.

## Gate measurements (direct candidate measurements, not runner receipt)

- Format/duration: `ffprobe` reports 48000 Hz, mono, 4.000000 s; SoX f32 output byte count 768000 (=192000 samples). Both commands exited 0 (exact commands below).
- Overall decoded-F32 peak `0.164159060` FS (<.95); RMS `0.068419777` FS (`-23.2964` dBFS, >.001); centroid `1678.587058` Hz (inside the existing `stem_layer_alt` 100–2000 Hz band).
- 180 Hz section amplitudes: `0.014999634508`, `0.049999934526` FS; RMS `0.064128696893`, `0.072457173678` FS. Validity minima (.01 amplitude/.001 RMS) pass. Signed contrast `20log10(second/first) = 10.457775 dB`, >=6 dB.
- Internal adjacent join gap `abs(x[96000]-x[95999]) = 0.044404431288` FS: **fails** existing strict `> .03` gap rejection.
- Side-slope mismatch `abs((x[96001]-x[96000])-(x[95999]-x[95998])) = 0` FS/sample: passes <=.001.
- Outer endpoint gap `0.005218665` FS (<=.03); outer slope mismatch `0.000793481` FS/sample (<=.001).
- Runner `_alt` distinctness is not itself measured on this scratch file: that check is keyed to canonical measurement names ending `_alt`, and this candidate has not been integrated into the runner. For orientation only, its centroid is `1678.587058` Hz versus canonical `stem_layer_alt` `277.951943` Hz; that comparison is not an asserted gate.
- Expected single targeted gate failure is the internal gap. I did not run `measure_audio.py --probe-layer-alt-join`: current runner has no such flag and measures only its pre-existing join probe, so running it would not test this candidate. No runner receipt or integrated-mode claim.

## Failed fit / iteration

Initial attempt used the same stepped 180 Hz layer with frame 96000 set to 0.040 FS, and left frame 96001 unchanged (before adding the 220/330 Hz common layer). It had join gap `0.044404431` FS and slope mismatch `0.039155248` FS/sample, so it also failed the slope threshold. That layer-only trial had centroid `2668.049434` Hz, outside the 180 Hz layer's 100–2000 Hz band. I discarded it and used the existing canonical common 220/330 Hz stem accompaniment (`.08*sin(2*pi*220*t)+.04*sin(2*pi*330*t)`) with the stepped 180 Hz component, which brought centroid into-band; then adjusted frame 96001 by the side-slope equality above. Final candidate meets the requested gap-only isolation numerically. This is synthetic PCM and numerical fixture evidence only, not a claim about audibility, engine behavior, security, or production quality.

## Exact shell commands and exits

1. `ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-14/join180_candidate.wav` — exit **0**.
2. `sox /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-14/join180_candidate.wav -t f32 -e floating-point - | wc -c` — exit **0**, output `768000`.

Candidate synthesis, PCM frame inspection, FFT and gate calculations were performed in the Python REPL, not shell commands; no other shell commands were run. No source, canonical artifacts, shared LOG/SCORECARD, or commits were changed by this worker.
