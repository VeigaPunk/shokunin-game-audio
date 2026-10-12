# Round 10 scout — decoded internal-join baseline

## Scope

This is a numeric read-only baseline for the original `stem_layer` fixture. It evaluates the decoded PCM samples around the 2-second section boundary, the outer endpoint/slope checks, and the existing 120 Hz section contrast. It does not claim perceptual quality, click-free transitions, engine behavior, or production suitability.

## Source and method

Fixture: `.shokunin/audio/corpus/artifacts/stem_layer.wav` (SHA-256 `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`). The existing normal receipt `corpus/live/runs/20261012T173533220319Z-normal/measurements.json` reports 4.0 s, 48,000 Hz, mono (192,000 decoded frames). With zero-based frame indexing, the 2-second join is between frames 95,999 and 96,000: those are the last decoded sample of the first 96,000-frame half and first decoded sample of the second half.

I independently decoded with SoX to little-endian float32 and inspected both adjacent samples. Command and exit:

```sh
sox .shokunin/audio/corpus/artifacts/stem_layer.wav -t f32 -e floating-point - | python3 -c 'import sys,numpy as np; x=np.frombuffer(sys.stdin.buffer.read(),dtype="<f4"); print("frames",len(x)); print("x95999",repr(float(x[95999])),"x96000",repr(float(x[96000])),"gap",repr(float(abs(x[96000]-x[95999])))); print("outer",repr(float(abs(x[0]-x[-1])))); print("outer_slope",repr(float(abs((x[-1]-x[-2])-(x[1]-x[0])))))'
# exit 0
```

## Numeric baseline

| Check | Baseline | Existing criterion/result |
|---|---:|---|
| Decoded frames | 192,000 | 4 s at 48 kHz; passes format/duration |
| Sample at frame 95,999 | -0.00018310546875 FS | — |
| Sample at frame 96,000 | 0 FS | — |
| Absolute adjacent join gap | 0.00018310546875 FS | Proposed `.03`-FS comparator would pass (about 164× below bound) |
| Outer endpoint delta | 0.000946044921875 FS | Existing `.03`-FS max; passes |
| Outer slope mismatch | 0.000762939453125 FS/sample | Existing `.001` max; passes |
| 120 Hz first/second-half component amplitudes | 0.011999587449951306 / 0.05999774519524399 FS | Both valid; minimum `.01` FS |
| 120 Hz component amplitude contrast | 13.979372282981668 dB | Existing minimum 6 dB; passes |

The decoded join-gap quantity is only the absolute difference between two adjacent samples, not a slope-mismatch or perceptual metric. A clean baseline says the proposed bound does not reject this fixture; it does not establish that the bound is calibrated to audibility. No probe or source changes were made.
