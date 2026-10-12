# Round 15 alternate: `slope180_other.wav`

## Result

I made an independent, one-frame PCM perturbation of the original generated `stem_layer_alt.wav`. The final scratch file is `.shokunin/audio/corpus/live/round-15/slope180_other.wav`, SHA-256 `16f789d329e2e05224155a6dd8e7ba1d40c74a82c7672b6b34fa92805a1bcf9a`. It has the same 192,000 mono 16-bit PCM frames at 48 kHz as the source. Exactly one frame differs: frame 96001, from 39 to 55 signed PCM counts (all other frames match the source). No canonical file was edited.

| Check (decoded SoX float32, then float64 as in runner) | Measurement | Existing bound | Outcome |
|---|---:|---:|---|
| 180 Hz component amplitudes, first/second 96,000-frame sections | 0.01499992 / 0.04999787 FS | each >= .01 FS | pass |
| 180 Hz amplitude contrast | 10.4572506 dB | >= 6 dB | pass |
| Internal join adjacent-sample gap | 0.00036621094 FS | <= .03 FS | pass |
| Internal join side-slope mismatch | 0.00134277344 FS/sample | <= .001 FS/sample | **fail** |
| Whole-file centroid | 310.2003 Hz | stem_layer_alt band 100–2000 Hz | pass |
| Peak / RMS | 0.0499878 FS / 0.0260997 FS | peak < .95; RMS >= .001 | pass |
| Outer endpoint gap / side-slope mismatch | 0.00119019 FS / 0.00079346 FS/sample | <= .03 / <= .001 | pass |
| Rate / channels / duration | 48,000 Hz / mono / 4.000 s | 48 kHz mono / 4 s ±1 ms | pass |

Thus the perturbation exceeds only the existing internal side-slope bound among the reported format, level, centroid, section-contrast, internal-gap, and outer-seam checks. This is a local deterministic fixture result, not an audible or production claim.

## Explored fits and failed fits

- **Final one-frame fit:** add 16 PCM counts at frame 96001. It keeps the internal gap below bound and contrast valid, while the side-slope metric rises from the clean source's roughly 0.00085449 to 0.00134277 FS/sample. This is the scratch file above.
- **Frame 96001 + 8 counts:** slope mismatch 0.00109863 FS/sample (> .001); it would also fail the same slope gate, but final +16 was retained as the recorded candidate. (Same-index +16 exploratory calculation yielded centroid 310.2003 Hz and valid 10.4573 dB contrast.)
- **Frame 95998 -16 counts:** slope mismatch remained only 0.00036622 FS/sample, so it did not trigger the target failure. It was not suitable.
- **Frame 95999 +16 counts:** slope mismatch 0.00036622 FS/sample, so it did not trigger the target failure. It was not suitable.
- **Frame 96000 edits:** tested small signed offsets moved the gap/slope and sometimes made the section contrast extreme or invalid; no useful fit selected.

## Reproducibility and commands

Scratch construction used Python's `wave` and NumPy in the REPL: read the original signed little-endian PCM, copy it, increment sample index 96001 by 16, then write mono/16-bit/48 kHz WAV. Decoded metrics were computed from `sox <wav> -t f32 -e floating-point -` output using the fixture's formulas and 180 Hz bin 360 in each 96,000-sample FFT. No fixture CLI probe was run, so there is no CLI exit code to report. The only shell command run was `git status --short` (exit 0); it showed the pre-existing modified `.shokunin/audio/LOG.md` plus this round's scratch/report paths. I did not edit the log.

No audio was auditioned. No inference is made about audibility, music quality, engine behavior, security, or production suitability.
