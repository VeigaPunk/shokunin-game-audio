# R44 alt — independent fixture pair

## Scope and result

Independently generated two original deterministic UI-shaped mono PCM16 WAVs in the assigned scratch directory. The controls test the unchanged ordinary duration check against a 0.12 s UI target: 5807 frames should pass at the near side of 1 ms; 5809 frames should fail. This is numerical fixture calibration only. No audition or inference about quality, production, rights, engine behavior, publishing, or promotion.

| Frames | SHA-256 | ffprobe duration (s) | Delta from 0.12 s (s) | Tool measurement | Outcome |
|---:|---|---:|---:|---|---|
| 5807 | `a8da540da39f0a803213401ff6133f2b29cd50eba331c3e044d8d3524c22ecaf` | 0.120979 | +0.000979 | peak 0.25; RMS −15.052435940318428 dBFS (0.17675764 FS); centroid 1119.7086943324982 Hz | no failures |
| 5809 | `c39a25850b638fd842981180e7d996a5a37e2de140fd746afcb3550a50529372` | 0.121021 | +0.001021 | peak 0.25; RMS −15.050965747377559 dBFS (0.17678756 FS); centroid 1052.1902300161073 Hz | sole failure `duration: outside ±1 ms` |

Both are 48 kHz mono PCM16, and their peaks, RMS values, and centroids are within the stated ordinary UI fixture gates. Centroid differs slightly because each finite record has a different FFT bin grid; both remain within 250–4000 Hz. The pair thus isolates duration, not centroid equality. The ffprobe decimal durations are rounded output; report those measurements and measured deltas, not an assertion about exact 5808-frame equality or exact 1 ms comparison semantics.

## Commands and errors

Generated originals in `corpus/live/round-44/alt/` as rounded 0.25-amplitude, 1 kHz cosine PCM16 sequences at 48 kHz, with respective frame counts 5807 and 5809. WAV SHA-256 values are in the table.

Exact probe command (exit 0):

```sh
for f in .shokunin/audio/corpus/live/round-44/alt/*.wav; do echo "FILE=$f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,duration:format=duration -of json "$f"; done
```

Project metric helper calls used `measure_audio.measure("ui", SPECS["ui"], absolute_wav_path)`; both completed and returned above metrics. An initial helper call with a relative path raised `ValueError` in `Path.relative_to` (setup/path error, not a numeric fit). Rerunning with an absolute path succeeded. SoX float decode spot-check exact command (exit 0):

```sh
for f in .shokunin/audio/corpus/live/round-44/alt/*.wav; do sox "$f" -t f32 -e floating-point "${f%.wav}.f32"; echo "sox_exit=$? file=$f"; done
```

Both decoded files were removed after the check. No numeric fit failed; the 5809 duration failure is the intended measured gate result. No control/audio was auditioned.
