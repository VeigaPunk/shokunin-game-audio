# r29-critic — falsification of lower-side signedness candidate

## Result

I independently generated a matched 5,760-frame baseline and two lower-centroid variants from the same chirp family used in round 28, then measured the WAVs through `ffprobe` and `sox`. The negative-side bracket does exist on this measured proxy: the `.89` multiplier has relative centroid delta `0.093939784` (< .10), while `.90` has `0.104663341` (>= .10), both with centroid below the baseline and duration delta zero. If the delta were implemented as signed `(variant - base) / base`, both would be negative and both would be rejected by a `>= .10` test; the absolute-difference rule instead classifies the `.90` candidate above the numeric distinctness cutoff. This is a direct measurement of the relevant signedness counterexample, not an integrated-runner test.

| Candidate | ffprobe duration | centroid (Hz) | relative absolute delta from baseline | peak FS | RMS FS |
|---|---:|---:|---:|---:|---:|
| baseline `k=1.00` | .120000 | 966.896659 | — | .375946 | .1000957 |
| lower-side below `k=.89` | .120000 | 876.066596 | .093939784 | .375427 | .1000953 |
| lower-side above `k=.90` | .120000 | 865.698024 | .104663341 | .375488 | .1000955 |

All were measured as 48 kHz mono PCM16. Both variants meet the declared duration tolerance, peak/RMS level bounds, and UI centroid band by the recorded numeric values. There is no evidence here about runner integration or preservation of other modes.

## Method and command

From repository root, I ran:

- `python3 /tmp/r29_critic_measure.py` — exit 0.

The temporary script source-generated the three PCM16 WAVs under `/tmp/r29-critic-jxomk2xo/`, called `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json <wav>` and `sox <wav> -t f32 -e floating-point -`, then used the checker’s whole-waveform magnitude-weighted positive-frequency FFT centroid formula. The exact observed outputs are recorded in the table. No project command was run; no fixture, runner, canonical asset, threshold, or shared project file was changed.

## Falsification attempts and limits

The source parameter is not an isolated centroid control: `k` scales the entire chirp trajectory (`700*k*t + 800*k*t*t`). The FFT centroid is non-monotonic in `k`; close numeric parameter changes do not imply close output or smooth centroid response. For example, extra exploratory values `.853` and `.854` yielded relative deltas `.106505` and `.145245`, respectively, and `.859` yielded `.101771`; the local sequence is not monotone. These are not failed tool/setup runs, but demonstrate why a parameter sweep alone cannot support smoothness or isolation claims. I found no counterexample to the *numeric* absolute-versus-signed arithmetic for the selected below-baseline pair; I cannot establish the integrated runner’s branch behavior without a runner mode/replay.

This addresses only the checker’s numeric FFT-centroid proxy and threshold polarity. No exact cutoff equality, smoothness, perceptual/auditory, rights, engine, publishing, or promotion claim is made.
