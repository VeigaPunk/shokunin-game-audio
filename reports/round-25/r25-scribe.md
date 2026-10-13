# Round 25 — scribe decision table

## Scope and evidence status

This is a proposal/evidence table for the declared format-rate/channel isolation move, not a round verdict. I wrote only this report. The shared invalid-probe runner has not yet been integrated with the two new controls, so these are direct `measure()` checks, not persisted runner receipt outcomes. No sound-quality, engine, rights, or publishing claim is made.

The existing checker requires 48,000 Hz, one channel, and PCM16 (`format_failures()`); duration tolerance is ±1 ms, peak must be below .95, RMS at least .001, and centroid must lie within each fixture's supplied band. The two new controls are 4.000 s generated 440 Hz, amplitude-.2 PCM16 sine WAVs. They hold PCM encoding and duration fixed while each changes only one of the two format metadata fields relative to native 48 kHz mono PCM16.

## Decision table

| Case | Rate | Channels | PCM | Duration | Changed field vs native positive | Measured result | Interpretation |
|---|---:|---:|---|---:|---|---|---|
| Existing native16 positive (`round-22/native16_probe.wav`) | 48,000 | 1 | PCM16 | 4.000 s | none | `format_failures`: none | Baseline format tuple accepted; not a runner replay in this task. |
| Existing combined negative (`round-6/wrong_format.wav`) | 44,100 | 2 | PCM16 | 4.000 s | rate **and** channels | `format_failures`: `format: expected 48kHz mono` | Confounded for attributing rejection to rate versus channel. |
| New rate-isolation candidate (`executor/sine_44k1_mono_pcm16.wav`) | 44,100 | 1 | PCM16 | 4.000 s | rate only | `measure()` failures: `format: expected 48kHz mono`; peak .199982, RMS −16.990 dBFS, centroid 457.772 Hz | Intended rate predicate is isolated; listed level and centroid conditions pass the tested 4 s/100–1000 Hz spec. |
| New channel-isolation candidate (`executor/sine_48k_stereo_pcm16.wav`) | 48,000 | 2 | PCM16 | 4.000 s | channels only | `measure()` failures: `format: expected 48kHz mono`; peak .199982, RMS −16.990 dBFS, centroid 563.262 Hz | Intended channel predicate is isolated; listed level and centroid conditions pass the tested 4 s/100–1000 Hz spec. Stereo decoding is flattened by the current checker, so its centroid is not directly equivalent to a mono centroid. |

Both candidates have SHA-256: rate candidate `1bd9aac91baecffb03cb667c7e4116806eb149aa1c39b5cc787e1b861c965e69`; channel candidate `1a71090267d97dc07c14f4a057e2b14a433b45086a424cb99128f55831328987`. The `alt/` scratch files are separate lane telemetry and are not evidence in this table.

## Exact commands and exits

Metadata inspection (each command exited **0**):

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-25/executor/sine_48k_stereo_pcm16.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-25/executor/sine_44k1_mono_pcm16.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-6/wrong_format.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-22/native16_probe.wav
```

Direct acoustic/format measurements (each shell command exited **0**; exit 0 means the invocation ran and printed a measurement object, not that all checker conditions passed):

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location("ma",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure("r25_stereo48",(4.0,100,1000,False),Path(".shokunin/audio/corpus/live/round-25/executor/sine_48k_stereo_pcm16.wav").resolve()),indent=2))'
python3 -c 'import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location("ma",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps(m.measure("r25_mono441",(4.0,100,1000,False),Path(".shokunin/audio/corpus/live/round-25/executor/sine_44k1_mono_pcm16.wav").resolve()),indent=2))'
```

The result objects each contain exactly the one expected format failure and no duration, level, or centroid failure under the supplied spec. No failed setup or fit attempt occurred in this scribe check. The runner's invalid-probe JSON, all historical modes, and independent replay remain untested here; do not count them as passing.

## Limits / proposed decision

This is evidence that the present metadata predicate reports a format failure on each named single-field mismatch, while the measured level/centroid conditions for these constructed candidates pass. It does not establish that every rate/channel mismatch is rejected, that decoder paths or all acoustic measurements are format-independent, or that the controls are perceptually meaningful. In particular, `measure()` flattens interleaved stereo samples before FFT/statistic computation, so stereo centroid semantics differ from mono; only these observed outputs and pass/fail conditions are reported. No threshold, gate, or shared runner was changed. Treat the depth move as pending the parent integration and independent verifier's persisted invalid-mode receipts and guard replay.
