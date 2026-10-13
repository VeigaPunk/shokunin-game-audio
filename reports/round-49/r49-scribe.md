# Round 49 scribe — decision table and evidence boundaries

## Declared decision and current status

This is the declared numerical fixture calibration: compare original deterministic 5760-frame mono PCM16 UI-shaped WAVs tagged 48001 Hz and 48000 Hz, with the same PCM sequence where feasible. The existing format predicate requires exact ffprobe rate 48000 and mono. The 48001 sample should therefore fail only `format: expected 48kHz mono`; 48000 should have no failures, provided duration, level, centroid and other checks fit. This is not evidence about arbitrary sample rates, resampling, physical-time equivalence, or audio quality. The pair's measurements are complete. The overall round gate is **pending** fresh non-author replay and adjudication; this report does not admit the move.

## Decision table — project SoX-decoded measurements

| Fixture | ffprobe rate / channels / codec / bits | Duration (UI target 0.12 s ±0.001 s) | Peak FS (<0.95) | RMS dBFS (RMS >=0.001) | Whole-wave centroid (250–4000 Hz) | Format gate / measured failures |
|---|---|---:|---:|---:|---:|---|
| 48001 | 48001 / 1 / pcm_s16le / 16 | 0.119998 s — pass | 0.27996826171875 — pass | -18.327858226717105 — pass | 1022.557447787877 Hz — pass | Fails only `format: expected 48kHz mono` |
| 48000 | 48000 / 1 / pcm_s16le / 16 | 0.120000 s — pass | 0.27996826171875 — pass | -18.327858226717105 — pass | 1022.536144951523 Hz — pass | Pass; no failures |

Both have 5760 frames and WAV SHA-256 values respectively `92b22d8749c5f02d4f68d9a8daa32b935404f1d7cdbc31bca55af2f9adf4cb5a` and `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c`. `integrated_lufs` was null for each (undefined result), not a gate failure. SoX f32 decoded files were byte-identical; each decoded SHA-256 was `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f`.

## Exact commands and exits

Working directory: `/home/vgpnk/Projects/prymeagnt/audio`.

Generator plus SHA-256 and ffprobe metadata command (overall exit **0**):

```sh
python3 .shokunin/audio/corpus/live/round-49/executor/generate.py .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav 48001 && python3 .shokunin/audio/corpus/live/round-49/executor/generate.py .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav 48000 && sha256sum .shokunin/audio/corpus/live/round-49/executor/ui-*.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav
```

The observed ffprobe results were `sample_rate="48001"`, channels 1, codec `pcm_s16le`, 16 bits, duration `0.119998`; and `sample_rate="48000"`, channels 1, codec `pcm_s16le`, 16 bits, duration `0.120000`, respectively.

Project helper measurement command (exit **0**):

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-49/executor"); print(json.dumps({"48001":m.measure("ui",m.SPECS["ui"],d/"ui-48001.wav"),"48000":m.measure("ui",m.SPECS["ui"],d/"ui-48000.wav")},indent=2))'
```

SoX decode, byte comparison and decoded SHA command (overall exit **0**):

```sh
sox .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav -t f32 -e floating-point - > .shokunin/audio/corpus/live/round-49/executor/decoded-48001.f32 && sox .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav -t f32 -e floating-point - > .shokunin/audio/corpus/live/round-49/executor/decoded-48000.f32 && cmp .shokunin/audio/corpus/live/round-49/executor/decoded-48001.f32 .shokunin/audio/corpus/live/round-49/executor/decoded-48000.f32 && sha256sum .shokunin/audio/corpus/live/round-49/executor/decoded-*.f32
```

## Error categories and scope

- **Setup errors:** none reported for this measured pair.
- **Failed numeric fits:** none reported; duration, peak, RMS and centroid fit for both files. The 48001 exact-rate format failure is the intended measured gate result, not a numeric-fit failure.
- **Transcription corrections:** none reported.

No audition was performed. These fixture measurements support only the narrow declared numerical calibration. They do not establish audio quality, perception, production readiness, rights, engine behavior, publishing, or promotion.
