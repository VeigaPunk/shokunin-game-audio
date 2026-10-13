# r21-executor — round 21 scratch synthesis report

**Role:** leaf executor. Scope used: `.shokunin/audio/corpus/live/round-21/executor/` plus this report only. No shared builder/runner, canonical artifacts, LOG, SCORECARD, other reports, or commits were changed.

## Candidates and method

Created two separate original WAVs in the executor scratch directory:

- `join200_pass983.wav`: PCM16 value 838 at frame 96000 and 983 at frame 96001.
- `join200_fail984.wav`: PCM16 value 839 at frame 96000 and 984 at frame 96001.

Both were synthesized from scratch using the round-20 paired-join pattern: stepped 200 Hz section signal plus the 220/330 Hz bed, then set the internal join samples while preserving the left first difference. The raw pre-edit join is `[-290, -145, 0, 175]`; thus the edits yield `[-290, -145, 838, 983]` and `[-290, -145, 839, 984]`. They are not PCM copies of a canonical fixture. The 983/984 values denote the measured gap in PCM16 counts, not a universal or audible threshold.

The scripts `make_candidates.py` and `measure_candidates.py` are retained beside the WAVs for reproducibility. The measurement independently decodes each scratch candidate via SoX float32 and computes the existing runner-style numeric proxies (200 Hz exact-bin contrast, adjacent join gap, side-slope mismatch, outer seam, level, and weighted centroid); it does **not** invoke or prove the full runner integration.

## Results

| Proxy | 983 candidate | 984 candidate | Existing local gate |
|---|---:|---:|---|
| decoded join counts `[95998:96002]` | `[-290,-145,838,983]` | `[-290,-145,839,984]` | — |
| internal gap, FS | `0.029998779296875` (=983/32768) | `0.030029296875` (=984/32768) | failure only when `> .03` |
| internal side-slope mismatch, FS/sample | `0.0` | `0.0` | failure only when `> .001` |
| 200 Hz component contrast | `10.457519260400565 dB` | `10.457519263296449 dB` | must be >= 6 dB |
| section component amplitudes, FS | `.0149995862 / .0499983004` | `.0149995862 / .0499983004` | each >= .01 |
| weighted centroid | `1208.5869732 Hz` | `1209.6397189 Hz` | 100–2000 Hz |
| outer endpoint delta, FS | `.005340576171875` | `.005340576171875` | <= .03 |
| outer slope mismatch, FS/sample | `.00091552734375` | `.00091552734375` | <= .001 |
| peak / RMS, FS | `.1636047363 / .0684175985` | `.1636047363 / .0684175986` | peak < .95; RMS >= .001 |
| all listed candidate gates | pass | **internal gap only fails** | — |

`ffprobe` reports both as 48 kHz mono, 4.000000 s. SHA-256: pass `2f26852b2a0eb19f08afbe5189bb41c875f9ff78c072f96d19140d0a02586600`; fail `5194bd8e2cc9929d5287d3ddd910d32b3c24aa2f76ba66f267d83dbbe84d97fd`. The fail hash coincides with the round-20 selected scratch candidate because the final synthesized PCM is identical; the pass file differs only at frame 96000 from that waveform.

The arithmetic brackets the strict local `> .03` comparison: `.03*32768 = 983.04`, so 983/32768 passes and 984/32768 fails. This is scratch evidence on this synthetic signal and SoX decode path only. It does not establish perceptual calibration, audible click, production quality, or full runner integration. Parent/non-author runner replay remains necessary.

## Exact commands and exit codes

All commands ran from repository root `/home/vgpnk/Projects/prymeagnt/audio`.

| Command | Exit | Notes |
|---|---:|---|
| `python3 .shokunin/audio/corpus/live/round-21/executor/make_candidates.py` | 0 | Final pair generated. Earlier iterations of the same scratch generator were overwritten after identifying a spectrum-bound issue; those trial outputs are not selected evidence. |
| `python3 .shokunin/audio/corpus/live/round-21/executor/measure_candidates.py` | 0 | Final independent decoded measurements above. |
| `ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json .shokunin/audio/corpus/live/round-21/executor/join200_pass983.wav` | 0 | 48 kHz mono, 4 s. |
| `ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json .shokunin/audio/corpus/live/round-21/executor/join200_fail984.wav` | 0 | 48 kHz mono, 4 s. |
| `sha256sum .shokunin/audio/corpus/live/round-21/executor/join200_pass983.wav .shokunin/audio/corpus/live/round-21/executor/join200_fail984.wav` | 0 | Hashes recorded above. |
| Initial combined typo command `python3 .shokhin/audio/corpus/live/round-21/executor/measure_candidates.py` | 2 | Misspelled `.shokunin`; no measurement, excluded. Correct command then exited 0. |

No full integrated `measure_audio.py` runner invocation was made; scratch output alone is not runner evidence.
