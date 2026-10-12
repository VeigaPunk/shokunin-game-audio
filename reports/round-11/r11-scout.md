# Round 11 scout — decoded internal join map

## Scope
Mapped the declared `stem_layer` internal join in original analytic PCM only. This is sample-level telemetry; it is not a perceptual, engine, security, or production claim. I made no source, LOG, SCORECARD, or canonical-artifact edits. No scratch audio was needed.

## Clean decoded samples and metrics
The source file `.shokunin/audio/corpus/artifacts/stem_layer.wav` has SHA-256 `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`. Decoded as 48 kHz mono, 192000 float samples. At 2 seconds, frame index 96000 is the first sample of section two; the four samples at frames 95998..96001 are:

| Frame | Value (full scale) |
|---:|---:|
| 95998 | -0.0003662109375 |
| 95999 | -0.00018310546875 |
| 96000 | 0 |
| 96001 | 0.000946044921875 |

The internal join's existing adjacent-sample gap is `abs(x[96000]-x[95999]) = 0.00018310546875` FS, below its `.03` limit. The left-side slope is `x[95999]-x[95998] = 0.00018310546875` FS/sample; right-side slope is `x[96001]-x[96000] = 0.000946044921875` FS/sample. Their absolute mismatch is `0.000762939453125` FS/sample, below the proposed `.001` fixture-local bound.

The proposed metric uses the two local first differences straddling the join, not a whole-file endpoint difference. With indexed samples, it is `abs((x[96001]-x[96000]) - (x[95999]-x[95998]))`. A strict `>` `.001` test would pass this clean layer. This is only a continuity proxy and does not establish perceptual smoothness or a calibrated threshold.

## Existing checks and control context
`measure_audio.py` currently reports whole-file outer endpoint delta and whole-file start/end slope mismatch, then gates those at `.03` and `.001` respectively for loopable specs. Its section analysis splits at 96000, computes per-half 120 Hz amplitudes for `stem_layer`, requires valid sections and at least 6 dB contrast, and reports/gates the single internal adjacent gap for `stem_layer` and `join_probe`. The gap rule is strict `> .03`. There is no internal side-slope mismatch field/gate in the inspected source. The proposed comparison is thus distinct in location and metric from the outer slope check; it does not replace either outer guard or the existing gap gate.

For fit review, a candidate control must keep the join gap `<= .03`, retain valid section contrast `>= 6 dB`, and pass generic format/duration/level/centroid and outer endpoint/slope bounds while the internal side-slope mismatch alone exceeds `.001`. This scout did not build or validate such a control.

## Commands and exits
- `ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json .shokunin/audio/corpus/artifacts/stem_layer.wav` — exit **0**; reported 48000 Hz, mono, 4.000000 s.
- `sox .shokunin/audio/corpus/artifacts/stem_layer.wav -t f32 -e floating-point - | python -c 'import sys,numpy as np; x=np.frombuffer(sys.stdin.buffer.read(),dtype="<f4").astype(np.float64); print(len(x),repr(x[95998:96002].tolist())); print("join",abs(x[96000]-x[95999]),"left",x[95999]-x[95998],"right",x[96001]-x[96000],"mismatch",abs((x[96001]-x[96000])-(x[95999]-x[95998])))'` — exit **0**; reported the values and metrics above.

No other shell commands were run.
