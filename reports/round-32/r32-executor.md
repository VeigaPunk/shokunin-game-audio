# Round 32 executor — measured mixed-signals pair

## Result
Found a source-generated original pair using the declared 48 kHz mono PCM16 UI-shaped chirp, with a longer variant at 6719 frames. The baseline has 5760 frames. Direct project `measure_audio.measure()` results (from scratch WAVs) show:

| Measurement | Base (5760 frames) | Variant (6719 frames) | Comparison |
|---|---:|---:|---:|
| ffprobe duration | 0.120000 s | 0.139979 s | absolute delta `0.019978999999999997` s: nonzero and `< .020` |
| weighted positive-frequency centroid | 966.8966593379727 Hz | 1069.352782328027 Hz | relative delta `0.1059638814557548`: `>= .10` |
| ordinary per-file failures | none | none | both pass under their declared specs |

Using the existing project comparator expression `duration_delta >= .020 or centroid_relative_delta >= .10`, the duration branch is false and centroid branch true, so the comparison passes. The variant was measured with separately declared scratch spec `(6719/48000, 250, 4000, False)`; it does **not** conform to canonical UI `.12 s ± .001 s` duration. No thresholds or canonical WAV/spec were changed.

This is one measured mixed-signals OR observation. It does not establish causal independence, exact threshold equality, perceptual similarity/distinctness, rights, engine behavior, publishing, or promotion.

## Generation and measurement
Generated in scratch with the project builder's original UI chirp form `0.38*sin(2*pi*k*(700*t + 800*t*t))*exp(-30*t)`, PCM16 save path, and 48 kHz rate. Base `k=1.0`; selected longer variant `k=1.14`. Files and helper are under `.shokunin/audio/corpus/live/round-32/executor/` only. `direct_project_measure.py` loads the fixture's own `measure_audio.py`, calls `measure()` on both scratch files using the stated specs, and prints both measurements plus the comparator branches.

Exact shell command used for direct project measurement:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-32/executor/direct_project_measure.py
```

Exit code: **0**. It reported duration delta `0.019978999999999997`, centroid relative delta `0.1059638814557548`, branches `false` / `true`, comparator pass `true`, and empty ordinary failure lists.

## Fit attempts and setup issues
A small coefficient scan used direct project measurement against the fixed 5760-frame base; no failed ordinary checks occurred. `k=1.0855` measured relative centroid delta `0.099352...` (does not meet the requested centroid arm); `k=1.09` measured about `0.050...`; `k=1.10` about `0.084...`; `k=1.11` about `0.120...`; `k=1.12` about `0.135...`; `k=1.13` about `0.126...`. These were numeric fit misses, not comparator outcomes. Selected `k=1.14` measured `0.1059638814557548` and both files passed their individual checks.

One in-kernel direct-measure call initially supplied a relative `Path`; the project helper's returned-path formatting raised `ValueError` because that path was not absolute relative to its absolute corpus root. Retried with resolved absolute scratch paths; measurement succeeded. A first shell wrapper mistakenly attempted to `await` an already-completed `BashResult`; this was a REPL wrapper mistake, not a project command failure. No project command failure or fit/setup artifact was treated as a negative comparator result.
