# R48 alt — adjacent sample-rate controls

## Scope and result

This independent control set tests the declared 47999/48000 Hz numeric fixture, not a change to the checker. I created two original mono PCM16 WAVs with exactly 5760 frames and the same decoded signed-16-bit sample sequence. The generated samples are a 0.30-amplitude, 700 Hz sine sampled on a 48 kHz time grid; the WAV headers declare their respective rates. The 47999 Hz WAV's decoded duration is 0.120003 s and the 48000 Hz WAV's is 0.120000 s, both within the UI ±1 ms duration criterion. SoX-decoded whole-wave centroids are in the 250–4000 Hz band; peak and RMS level checks pass.

| Rate | File SHA-256 | ffprobe stream metadata (rate / channels / codec / bits) | ffprobe duration | project SoX-decoded centroid | peak | RMS dBFS | project failures |
|---|---|---|---:|---:|---:|---:|---|
| 47999 | `256180fac93dfdee9ccacff516d56509468da03a8897bb09b09057df6e2bac54` | 47999 / 1 / pcm_s16le / 16 | 0.120003 s | 704.1509902058624 Hz | 0.29998779296875 | -13.468142168262505 | `format: expected 48kHz mono` only |
| 48000 | `263b5ceaf021d0aeba60007fa82b326c71856c0ff72d1ad870a3e6c80e6cbb03` | 48000 / 1 / pcm_s16le / 16 | 0.120000 s | 704.1656603237849 Hz | 0.29998779296875 | -13.468142168262505 | none |

The SoX-rendered signed-16-bit streams have identical SHA-256 `3de1df4b2b2e8e6cfbfc8362e48e032403eb8e41a06e07f54604cb0671a4a292`, corroborating identical decoded PCM samples. This is a numeric sample-rate format-boundary control; it does not imply anything about sound quality, perception, conversion behavior, or uses beyond this fixture/check.

## Exact commands and exits

Commands below were run from repository root. The ffprobe invocations expose the actual container stream metadata and duration:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-48/alt/ui-47999.wav
# exit 0
```

Output: `sample_rate=47999`, `channels=1`, `codec_name=pcm_s16le`, `bits_per_sample=16`, `duration=0.120003`.

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-48/alt/ui-48000.wav
# exit 0
```

Output: `sample_rate=48000`, `channels=1`, `codec_name=pcm_s16le`, `bits_per_sample=16`, `duration=0.120000`.

The following exact project-measurement commands invoke the fixture's `measure()` routine. Its implementation uses ffprobe plus `sox WAV -t f32 -e floating-point -` for project decoded samples and computes the whole-wave magnitude-FFT centroid, peak and RMS:

```sh
python -c "import sys; from pathlib import Path; sys.path.insert(0, '.shokunin/audio/corpus/fixtures'); import measure_audio as m; print(m.measure('alt',(0.12,250,4000,False),m.ROOT/'live/round-48/alt/ui-47999.wav'))"
# exit 0
```

```sh
python -c "import sys; from pathlib import Path; sys.path.insert(0, '.shokunin/audio/corpus/fixtures'); import measure_audio as m; print(m.measure('alt',(0.12,250,4000,False),m.ROOT/'live/round-48/alt/ui-48000.wav'))"
# exit 0
```

Exact PCM equality check:

```sh
sox .shokunin/audio/corpus/live/round-48/alt/ui-47999.wav -t s16 - | sha256sum
# exit 0; 3de1df4b2b2e8e6cfbfc8362e48e032403eb8e41a06e07f54604cb0671a4a292
sox .shokunin/audio/corpus/live/round-48/alt/ui-48000.wav -t s16 - | sha256sum
# exit 0; 3de1df4b2b2e8e6cfbfc8362e48e032403eb8e41a06e07f54604cb0671a4a292
```

## Failed attempts and interpretation boundaries

There were no failed numeric fits: the chosen pair met the requested adjacent header rates, duration, level, centroid, and same-decoded-samples constraints on the first measured candidate. There were no source transcription corrections. Two early measurement invocations were setup mistakes, not measurement failures: passing the WAV path as a string caused `AttributeError` (`relative_to`); passing a repository-root-relative `Path` caused `ValueError` because the helper expects paths rooted under its corpus directory. Retrying with `m.ROOT / 'live/round-48/alt/…'` ran the same project measurement successfully. These controls do not execute checker opt-in modes; they report only the project's measurement function applied to the original files. No audition or qualitative inference was made.
