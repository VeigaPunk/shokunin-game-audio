# R48 reviewer — adjacent integer sample-rate modes

## Recommendation

The calibration gap is the exact-rate boundary in `format_failures(stream)`: it requires integer ffprobe `sample_rate == 48000` and mono. Round 25’s `mono441_probe` is a broad 44.1-kHz mismatch, not evidence about the adjacent 47,999-Hz boundary. Add just two mutually exclusive opt-in modes (suggested names `--probe-ui-rate-47999` and `--probe-ui-rate-48000`). Each should create/measure one deterministic 5760-frame UI-shaped mono PCM16 scratch WAV at its named rate, via the existing ordinary `measure("ui", SPECS["ui"], path)` path. Keep `format_failures`, `SPECS["ui"]`, duration/level/centroid thresholds, canonical fixtures and ordinary run unchanged. Expected results: 47999 exits 1 with sole `format: expected 48kHz mono`; 48000 exits 0 without failures. These are a minimal proposal, not currently implemented runner flags or runs I executed.

## Fixture evidence

I independently inspected and measured the executor’s original fixtures. The WAV payloads are identical (5760 PCM frames); only the WAV sample-rate header differs. Actual ffprobe stream metadata and duration:

| WAV | SHA-256 | ffprobe | Project SoX-decoded metrics | Result |
|---|---|---|---|---|
| `live/round-48/executor/ui-47999.wav` | `71551e200633e62b1b9db4ee5a582f8d4d996cd693f2e4a040a96023b130a210` | 47999 Hz, mono, `pcm_s16le`, 16 bit; 0.120003 s | peak 0.27996826171875; RMS −18.327858226717105 dBFS; centroid 1022.5148421151724 Hz; bandwidth 586.904753883307 Hz | sole format failure |
| `live/round-48/executor/ui-48000.wav` | `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c` | 48000 Hz, mono, `pcm_s16le`, 16 bit; 0.120000 s | peak 0.27996826171875; RMS −18.327858226717105 dBFS; centroid 1022.536144951523 Hz; bandwidth 586.9169813204176 Hz | no failures |

Both satisfy UI duration tolerance (±0.001 s), peak < .95, RMS > .001 and centroid 250–4000 Hz. The exact WAV bytes differ because their headers encode distinct rates; decoded PCM frame payload is identical. This supports a numerical fixture comparison across the format predicate only. It does not establish behavior for arbitrary rates or resampling/conversion.

## Commands, exits, and accounting

Exact commands I ran:

```sh
for f in .shokunin/audio/corpus/live/round-48/executor/ui-47999.wav .shokunin/audio/corpus/live/round-48/executor/ui-48000.wav; do echo "$f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample -show_entries format=duration -of json "$f"; done
# exit 0; metadata/durations shown above.

sha256sum .shokunin/audio/corpus/live/round-48/executor/ui-47999.wav .shokunin/audio/corpus/live/round-48/executor/ui-48000.wav .shokunin/audio/corpus/live/round-48/alt/ui-47999.wav .shokunin/audio/corpus/live/round-48/alt/ui-48000.wav
# exit 0; executor hashes shown above (independent alt files also hashed, not otherwise analyzed here).

python -c 'import sys; from pathlib import Path; sys.path.insert(0, ".shokunin/audio/corpus/fixtures"); import measure_audio as m; [print(m.measure("ui", m.SPECS["ui"], Path(p))) for p in (".shokunin/audio/corpus/live/round-48/executor/ui-47999.wav", ".shokunin/audio/corpus/live/round-48/executor/ui-48000.wav")]'
# exit 1: setup/path error: helper's receipt path conversion rejects relative paths outside its ROOT; no metrics emitted.

python -c 'import sys; from pathlib import Path; sys.path.insert(0, ".shokunin/audio/corpus/fixtures"); import measure_audio as m; [print(m.measure("ui", m.SPECS["ui"], Path(p).resolve())) for p in (".shokunin/audio/corpus/live/round-48/executor/ui-47999.wav", ".shokunin/audio/corpus/live/round-48/executor/ui-48000.wav")]'
# exit 0; actual project SoX-f32-decoded measurements shown above.
```

The failed relative-path invocation was a measurement setup error, not a failed numeric fit. No runner mode command was run; no numeric candidate failed. I did not audition or transcribe anything, and found no report-transcription discrepancy in the independently checked values above.

## Limits

This is only numerical fixture calibration of the exact sample-rate format predicate. No inference about audible quality, perception, production, rights, engine behavior, publishing, or promotion. No audition.
