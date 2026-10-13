# Round 35 executor — movement candidate

## Scope and artifact
Generated an original deterministic candidate only at `.shokunin/audio/corpus/live/round-35/executor/movement_third_candidate.wav` (SHA-256 `4d114fdda5a94d64c849e90bfb85cf2c7f18db982d3f9af99429d73b5a30f830`). It is 0.30 s, 48 kHz mono PCM16. Synthesis: 620 Hz sine with smooth sinusoidal envelope and deterministic short noise onset (NumPy seed 3501). No canonical WAV, source, LOG, SCORECARD, or other report was edited.

## Measurement and fit
Used the project measurement function (`measure_audio.py` `measure`) on the scratch candidate and each canonical baseline. Candidate receipt: duration 0.300 s; centroid 7443.167204 Hz; peak 0.279968 FS; RMS -15.585662 dBFS; failures `[]`.

| Baseline | Duration | Centroid | Candidate duration delta | Relative centroid delta |
|---|---:|---:|---:|---:|
| `movement.wav` | 0.240 s | 11934.484046 Hz | 0.060 s | 0.376331 (37.6331%) |
| `movement_alt.wav` | 0.360 s | 12024.214879 Hz | 0.060 s | 0.380985 (38.0985%) |

Both baseline measurements also had ordinary failures `[]`. Candidate clears requested >=0.10 relative centroid difference from each and exactly 0.06 s duration difference from each; its centroid is within the 100–16000 Hz movement band, and peak/RMS clear the stated level checks. These are numeric proxies only, not evidence of perceived distinction, quality, production readiness, rights, engine compatibility, publishing, or promotion. Candidate remains scratch and is not canonical.

## Commands and exits
- `python3 .shokunin/audio/corpus/live/round-35/executor/generate_measure.py` — exit 0. The script deterministically writes the scratch WAV, calls the project measurement function for candidate and both baselines, and prints metrics/deltas/SHA.
- One initial malformed shell invocation failed before running the script: shell reported `/usr/bin/bash: line 4: python3 .shokunin/audio/corpus/live/round-35/executor/generate_measure.py: No such file or directory` (exit 127). This was command-quoting/setup failure, not a synthesis or candidate-fit failure; the correctly invoked command above succeeded.
