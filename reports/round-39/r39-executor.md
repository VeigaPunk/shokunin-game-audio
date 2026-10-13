# Round 39 executor — numeric fit

## Result

Fit one pair of deterministic equal-duration looped ambience PCM16 WAVs for the declared strict denominator split. The project measurement helper measured baseline A centroid **70.76230338852849 Hz** and variant B **78.18153634552728 Hz** (A < B). Forward `abs(B-A)/A` = **0.10484725060832** (> 0.10); reverse `abs(B-A)/B` = **0.09489750782345** (< 0.10). Both margins are strict, not equality.

| Scratch WAV | Construction | SHA-256 | Duration / format | Ordinary + seam helper failures |
|---|---|---|---|---|
| `corpus/live/round-39/executor/baseline.wav` | 12 Hz amplitude .15 + 120 Hz amplitude .07; 48 kHz, 2 s, mono PCM16 | `d516b687e91b983e60a7353cd19bb62f544be99ea9ec31a8bd7b5b2b4457d062` | 2.0 s; 48,000 Hz; mono; pcm_s16le / 16-bit | `[]` |
| `corpus/live/round-39/executor/variant.wav` | 12 Hz amplitude .15 + 120 Hz amplitude .11; 48 kHz, 2 s, mono PCM16 | `4f9c5365744b22643ca9fb48c6656529550f3457243871cc9a4c1503d035baec` | 2.0 s; 48,000 Hz; mono; pcm_s16le / 16-bit | `[]` |

Measured seam endpoint deltas were 0.0013427734375 and 0.001953125; slope mismatches were 3.0517578125e-05 and 3.0517578125e-05. Peak values were 0.218170166016 and 0.258178710938. Both have no failures from `measure_audio.py` ordinary or loop seam checks.

## Failed attempts / setup, separately

- Initial low-amplitude candidate (A as above, B 12 Hz amplitude .15 + 120 Hz amplitude .085) was a **numeric failed fit**: centroids 70.7623033885285 / 73.83612494647429 Hz; forward 0.04343868713640685 and reverse 0.041630320661791016, so neither is on the required opposite side of .10. It was overwritten by the selected B in scratch; not a gate result.
- A trial B with 120 Hz amplitude .4 was also a **numeric failed fit**: forward 0.41503602117344135 and reverse 0.2933042091955131, both > .10. This unsuccessful candidate was overwritten; not a gate result.
- First shell invocation treated the whole command string as one executable: `python3 /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-39/executor/measure_pair.py` (actual shell body was quoted as a single command). Exit **127**, “No such file or directory”; setup failure, no measurement.
- Corrected command `python3 "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-39/executor/measure_pair.py"` initially exited **1** because the helper resolved the fixture path one directory too high (`.../.shokunin/audio/fixtures/measure_audio.py`). Fixed only the helper in this executor scratch folder; rerun succeeded. This was a setup error, not a failed runner fit.

## Reproduction / scope

Successful command (exit **0**):

```sh
python3 "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-39/executor/measure_pair.py"
```

The scratch helper calls the project `measure_audio.py` measurement function on both WAVs with `(2.0, 5, 200, True)` and prints measured metrics and both denominator ratios. WAVs and helper are in `.shokunin/audio/corpus/live/round-39/executor/`; this report is the only report written. This is a numeric control result only; no audition, perceived quality, production, rights, engine, publishing, or promotion claim is made. The fit alone does not establish integrated forward/reverse runner receipts.
