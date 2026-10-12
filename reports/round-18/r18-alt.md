# Round 18 alternate fit — 200 Hz slope probe

## Scope and method

I read `.shokunin/audio/LOG.md` and inspected `corpus/fixtures/measure_audio.py` and `build_artifacts.py`. The baseline is `stem_layer_third.wav`, the original 4 s, 48 kHz mono 200 Hz layer. I independently copied its PCM16 frames and edited only join-adjacent frame 96001 in scratch WAVs under `corpus/live/round-18/`; no source, canonical artifact, LOG, SCORECARD, or threshold was changed. I used the existing measurement functions and thresholds, including section contrast at 200 Hz. The section helper reports its `passed` boolean without applying the join slope gate; I therefore evaluated its reported slope against the existing strict `> .001` gate as the runner does.

Baseline SHA-256: `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`. Baseline join samples (frames 95998–96001): `[-26, -13, 0, 43]` counts. The side-slope mismatch is 30/32767 = `.000915557` FS/sample by PCM arithmetic (receipt float decode rounds to `.00091552734375`), below `.001`.

## Candidate exploration and results

- `slope200_other.wav`: copied baseline and added **8 counts** at frame 96001 (43→51). SHA-256 `e7c98cc5af858d8dab2be01a4f76382e06008573a017909c2760e68a585b1881`. Existing `measure()` output: 4.0 s, 48000 Hz mono, peak `.04998779296875`, RMS `-31.66724762948755 dBFS`, centroid `303.8188333213137 Hz`, outer endpoint delta `.001312255859375`, outer slope mismatch `.00091552734375`; no generic failures. Section result at 200 Hz: amplitudes `[.014999984892417233, .04999803919712925]`, contrast `10.457243020771665 dB`, join gap `.000396728515625`, internal side-slope mismatch `.00115966796875`. Contrast/validity, internal gap, format, duration, level, centroid, outer endpoint and outer slope gates pass; **the intended internal join slope gate alone fails**.
- To bound PCM quantization, I tried +3 counts: `slope200_other_min.wav`, SHA-256 `48e2167dd405d05dc66aab304fc7b3c4712d2734dca021fdfd92d15a3e8d2a38`. Contrast `10.45724300631526 dB`, gap `.000396728515625`, internal slope `.001007080078125`. Sole failure remains internal join slope, by `.000007080078125` over threshold.
- +2 counts: `slope200_other_below.wav`, SHA-256 `512b38026eb102fac4773bca1b61e7994261b6f6297e0ec544fb4b47b1104496`. Contrast `10.457243003423983 dB`, gap `.000396728515625`, internal slope `.0009765625`. This fits the slope gate, confirming the PCM quantization boundary is at +3 counts for this edit; it is a passing control, not another negative.

The +8 alternate agrees with the proposed +8 hypothesis in crossing the same sole gate. None of these scratch files is a canonical artifact or runner replay. No thresholds were changed.

## Commands and setup telemetry

1. `ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json .shokunin/audio/corpus/live/round-18/slope200_other.wav` — exit **0**; 48000 Hz, mono, 4.000000 s.
2. Measurement invocation (for the +8 file; same form for +3/+2 by substituting the filename):
   `python3 -c 'import importlib.util; from pathlib import Path; p=".shokunin/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); q=Path(".shokunin/audio/corpus/live/round-18/slope200_other.wav").resolve(); print(m.measure("slope200_other", (4.0,100,2000,True), q)); print(m.section_contrast(q,200))'`
   — exit **0**. The same invocation on `slope200_other_min.wav` and `slope200_other_below.wav` also exited **0** with values above.
3. An initial equivalent measurement passed a relative `Path` to `measure()`, which raised `ValueError` at `path.relative_to(ROOT)` (exit **1**): this was a path/setup error, not an audio-fit failure. Retrying with the resolved absolute path succeeded. An initial shell attempt quoted the entire `ffprobe` command as a single executable and exited **127** (`No such file or directory`); corrected direct command above exited **0**. These setup errors are excluded from fit results.

## Claim limits

This is a numerical fit to existing local PCM/analysis gates only. It establishes neither audibility nor musical quality, production behavior, adaptive-engine behavior, rights beyond the original synthesized source, security, or external compatibility.
