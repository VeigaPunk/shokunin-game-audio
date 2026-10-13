# R49 alt — independent above-side adjacent-rate pair

## Scope and result

Independent scratch pair, generated without touching shared source, `LOG.md`, `SCORECARD.md`, canonical fixtures, or other reports. Original mono PCM16 WAVs contain 5760 frames from one deterministic sample-index signal; only the WAV sample-rate field differs. The decoded PCM payloads are identical. This is numerical fixture calibration only—not an audition or any quality, perception, production, rights, engine, publishing, or promotion inference.

| file | WAV SHA-256 | ffprobe rate / channels / codec / bits | ffprobe duration | project SoX-f32 peak | RMS dBFS | centroid Hz | project gate |
|---|---|---|---:|---:|---:|---:|---|
| `corpus/live/round-49/alt/ui-48001.wav` | `271e160bc8bc00bd4dfade5d3412185fea9482007a8067b4e5d2fe3f84aa826e` | 48001 / 1 / pcm_s16le / 16 | 0.119998 s | 0.279998779296875 | -14.906829610550412 | 2595.3844257189635 | sole `format: expected 48kHz mono` |
| `corpus/live/round-49/alt/ui-48000.wav` | `f63c9f23f79694bfce44d0d946ade66ef121e58cf1b58a6b989ee35991a4e72a` | 48000 / 1 / pcm_s16le / 16 | 0.120000 s | 0.279998779296875 | -14.906829610550412 | 2595.3303563365407 | no failures |

Both durations meet the UI ±1 ms condition; both levels and 250–4000 Hz centroid meet their project bounds. The PCM payload SHA-256 is `b9542500b2c252351c8861587abaaeb01ed73bcdb4fb995fa13b578183d236a1` in both files. Project SoX-f32 decoded output SHA-256 is `a7e3b8a8870c87a10090775cd92e34dad7fd1aaf32a4ff21d969c67bded0718d` for both. The small centroid difference is consistent with the rate-tag-dependent frequency axis; this does not demonstrate equal physical-time signals or conversion/resampling behavior.

## Commands and receipts

Generator command, exit 0:

```sh
python .shokunin/audio/corpus/live/round-49/alt/generate_pair.py
```

The script prints each WAV hash above and the shared PCM payload hash. Actual ffprobe command, exit 0 for each file:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/alt/ui-48001.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/alt/ui-48000.wav
```

Observed ffprobe stream/format values, respectively: `48001`, 1, `pcm_s16le`, 16, `0.119998`; and `48000`, 1, `pcm_s16le`, 16, `0.120000`.

Project `measure_audio.measure("ui", SPECS["ui"], resolved_path)` was run for each WAV; the helper's SoX decode is `sox <wav> -t f32 -e floating-point -` (exit 0), and both measurements are shown in the table. The project helper invocation printed those measurements and exited 0.

Decoded-byte identity was checked with:

```sh
for rate in 48001 48000; do sox .shokunin/audio/corpus/live/round-49/alt/ui-$rate.wav -t f32 -e floating-point - > .shokunin/audio/corpus/live/round-49/alt/decoded-$rate.f32; echo "sox_exit=$? rate=$rate"; done
sha256sum .shokunin/audio/corpus/live/round-49/alt/decoded-*.f32
```

Both SoX commands exited 0; both hashes equal the decoded-output hash above.

## Setup error / fit disclosure

One exploratory project-helper invocation used a relative path. It exited 1 with `ValueError: ... is not in the subpath of .../corpus` because `measure()` records paths relative to the corpus root; rerunning with resolved absolute paths exited 0. A separate attempted SoX command incorrectly included `-o`; it exited 1 with `sox FAIL getopt: invalid option '-o'`. Corrected stdout redirection command above exited 0. These are setup errors, not fixture gate failures. There were no failed numeric fits and no report transcription discrepancy identified. The final 48001 fixture's expected sole format failure is an observed numeric gate result, not a setup failure.
