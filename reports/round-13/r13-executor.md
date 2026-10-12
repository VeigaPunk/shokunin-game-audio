# Round 13 executor: matched flat 180 Hz control

## Artifact

Created only the permitted scratch artifact `corpus/live/round-13/flat180_candidate.wav` (384,044 bytes, PCM16 little-endian, 48,000 Hz, mono, 192,000 frames / 4.000 s). It is original synthetic PCM: `round(0.036 * sin(2π * 180 * n / 48000) * 32767)` for each sample `n`, clipped only by the integer conversion. The two 2-second halves have equal 180 Hz component amplitude. SHA-256: `3c2ff9741fcfc35f660676da1e9f81c5678654fdaa0ea07b1cffeee3945f03ce`.

Exact shell command run and exit:

```text
ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-13/flat180_candidate.wav
exit 0
```

It reported stream sample rate `48000`, channels `1`, duration `4.000000`.

## Measurements

Applied `measure_audio.measure("flat180_candidate", (4.0, 100, 2000, True), path)` and `section_contrast(path, 180)` from the existing fixture measurement module to the scratch WAV. These were direct Python calls in the REPL, not a `measure_audio.py` runner invocation; no runner receipt or new probe mode was created.

- Generic gates: format and duration pass; peak `0.0360107421875` FS, RMS `-31.884730005182025` dBFS, centroid `223.5226879482555` Hz (inside 100–2000 Hz); outer endpoint delta `0.0008544921875` FS and slope mismatch `0.0` FS/sample. **No generic/outer failures.** Integrated loudness reported `-32.9` LUFS; it is descriptive only.
- 180 Hz section component amplitudes: `[0.03599800833461317, 0.03599800833461317]` FS; section RMS `[0.02545443723242487, 0.02545443723242487]` FS. Validity checks pass. Contrast is `0.0 dB`, so the section check fails with exactly `sections: 180 Hz component amplitude contrast < 6 dB or invalid` (the fixture check's failure label; amplitudes are valid, and the contrast is below 6 dB).
- Internal join adjacent gap `0.0008544921875` FS and side-slope mismatch `0.0` FS/sample: both pass their respective `.03` and `.001` bounds.
- Existing `artifacts/stem_layer_alt.wav` baseline: centroid `277.9513846029034` Hz, duration `4.0` s. Candidate duration delta is `0.0` s; centroid-relative delta is `0.19582092290134728` (19.5821%), above the 10% threshold, so this pair is distinct under the fixture's duration-or-centroid rule. This comparison is descriptive; candidate is not a canonical `_alt` item and was not added to runner distinctness records.

## Limits

This locally confirms the proposed matched numeric negative control shape: generic, outer seam, and internal join gates pass, while the 180 Hz contrast check alone fails. It does not demonstrate the runner branch, regression stability, audibility, sound quality, adaptive engine behavior, security, or production readiness. No source, LOG, SCORECARD, canonical asset, or commit was changed.
