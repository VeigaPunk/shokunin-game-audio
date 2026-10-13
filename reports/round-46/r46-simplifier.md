# Round 46 simplifier — two-mode source review

## Recommendation

Use exactly two explicit opt-in fixture modes for the declared absolute lower-band calibration: one fixed below-band sample and one fixed in-band sample. Keep the existing UI spec and `measure()` path; do not add a generic probe framework, centroid threshold tuning, or alter any predicate. Add only two named flags and their explicit fixed-path/build/measurement/receipt branches to the existing one-mode guard and builder dispatch. Generate the files only under `corpus/live/round-46/<mode>/`; ordinary canonical generation must remain untouched. Each mode should measure one deterministic 48 kHz mono PCM16, 5760-frame WAV with the unchanged `SPECS["ui"]`.

The relevant gate is the existing absolute condition `not 250 <= centroid <= 4000`, not R29's relative pairwise-distinctness check. A bracket is numerically useful only if the low mode's sole failure is `spectrum: centroid outside fixture band`, and the upper mode has no failures. Confirm duration, format, peak and RMS for both from the actual decoded-measurement receipts. Do not use nominal oscillator frequency as the measured centroid, claim exact 250 Hz equality behavior, or generalize beyond these fixtures.

## Local numerical check and commands

I inspected `.shokunin/audio/LOG.md`, `corpus/fixtures/measure_audio.py`, and the independent alt builder `corpus/live/round-46/alt/build_pair.py`. I ran these exact commands from the repository root:

1. `python3 .shokunin/audio/corpus/live/round-46/alt/build_pair.py` — exit **0**, no output.
2. `python3 -c 'import sys; sys.path.insert(0, ".shokunin/audio/corpus/fixtures"); from measure_audio import measure,SPECS; from pathlib import Path; import json; [print(json.dumps(measure("ui",SPECS["ui"],Path(".shokunin/audio/corpus/live/round-46/alt/"+n+".wav")),sort_keys=True)) for n in ("below","above")]'` — exit **1**. Setup/path error, not a numeric fit: `measure()` could not make the relative path `.shokunin/audio/corpus/live/round-46/alt/below.wav` relative to its absolute `ROOT`.
3. `python3 -c 'import sys; sys.path.insert(0, ".shokunin/audio/corpus/fixtures"); from measure_audio import measure,SPECS; from pathlib import Path; import json; d=Path(".shokunin/audio/corpus/live/round-46/alt").resolve(); [print(json.dumps(measure("ui",SPECS["ui"],d/(n+".wav")),sort_keys=True)) for n in ("below","above")]'` — exit **0**. This used the project's actual `measure()` function, which decodes with SoX as f32 and computes the whole-wave magnitude-FFT centroid. Results:

| Scratch WAV | SHA-256 | Decoded centroid | Duration; rate/channels/codec/bits | Peak | RMS dBFS | Failures |
|---|---|---:|---|---:|---:|---|
| `below.wav` | `e2d85d3828bb139f8d7a6a459f34f88d3f2498b9135c105995717fe071184723` | 202.48468234677034 Hz | .12 s; 48000/1/pcm_s16le/16 | .3499755859375 | -12.1292172285544 | `spectrum: centroid outside fixture band` |
| `above.wav` | `2f9e9228b5cdcf7652ecfc8e1df54f4bc3647f8b303df63edd5e7f013b83af88` | 302.47893043755806 Hz | .12 s; 48000/1/pcm_s16le/16 | .3499755859375 | -12.129225594162117 | none |

These decoded numerical results bracket the existing lower bound for this independent pair, and the below-band fit fails only the intended spectrum check. They validate that pair, not a source integration or the requested executor pair. The path exception is setup, distinct from the successful measurement and its intended numeric failure.

## Scope

This is a minimal-diff recommendation, not an implementation: I made no changes to shared source, LOG, SCORECARD, canonical fixtures, or other reports. This report is the only file I wrote. The check is numerical fixture calibration only. No audition or inference about spectral quality, timbre, novelty, perception, production, rights, engine, publishing, or promotion.
