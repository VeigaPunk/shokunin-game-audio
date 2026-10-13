# R49 simplifier — smallest builder/runner change

## Recommendation

Keep this to the two existing opt-in rate-probe modes. No new abstraction, configurable-rate framework, threshold changes, or broad rate sweep is needed. In the existing fixture builder, extend/replace the R48 rate-probe pair with exactly `(48001, 48000)`, writing the existing 5760-frame mono PCM16 payload under those two WAV header rates. In the runner, keep exactly two mutually exclusive flags and the current per-mode probe/receipt flow; replace the `47999` mode with `48001` in the parser, mutually-exclusive flag list, generated fixture selection, mode label, and receipt suffix. Keep the `48000` control mode. The input rate must be the header metadata rate, while generated samples remain the existing deterministic UI-shaped array. Do not generalize flags into user-supplied arbitrary rates.

This is a narrow upper-neighbor calibration companion to R48's lower-neighbor pair. The existing `format_failures(stream)` exact integer comparison remains untouched; duration, peak, RMS, and centroid criteria remain untouched. Canonical fixtures, the generic five `_alt`/four family, prior 56 modes, invalid probes, and normal restore remain untouched.

## Numerical evidence (executor report)

The executor ran these commands from `/home/vgpnk/Projects/prymeagnt/audio`; each listed overall exit was **0**:

```sh
python3 .shokunin/audio/corpus/live/round-49/executor/generate.py .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav 48001 && python3 .shokunin/audio/corpus/live/round-49/executor/generate.py .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav 48000 && sha256sum .shokunin/audio/corpus/live/round-49/executor/ui-*.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav
```

ffprobe reported 48001 WAV: `sample_rate=48001`, `channels=1`, `codec_name=pcm_s16le`, `bits_per_sample=16`, duration `0.119998` s; 48000 WAV: `sample_rate=48000`, `channels=1`, `codec_name=pcm_s16le`, `bits_per_sample=16`, duration `0.120000` s. WAV SHA-256: 48001 `92b22d8749c5f02d4f68d9a8daa32b935404f1d7cdbc31bca55af2f9adf4cb5a`; 48000 `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c`.

Project SoX-f32 decoded measurements were produced by this exact command (exit **0**):

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-49/executor"); print(json.dumps({"48001":m.measure("ui",m.SPECS["ui"],d/"ui-48001.wav"),"48000":m.measure("ui",m.SPECS["ui"],d/"ui-48000.wav")},indent=2))'
```

| Header rate | Peak FS | RMS dBFS | Centroid Hz | Bandwidth Hz | Result |
|---:|---:|---:|---:|---:|---|
| 48001 | 0.27996826171875 | -18.327858226717105 | 1022.557447787877 | 586.929208757528 | Sole failure: `format: expected 48kHz mono` |
| 48000 | 0.27996826171875 | -18.327858226717105 | 1022.536144951523 | 586.9169813204176 | No failures |

Both project durations fit `.12 s ± .001`, peaks are below `.95`, RMS exceeds `.001`, and centroids are in 250–4000 Hz. SoX decoding and byte comparison used (exit **0**):

```sh
sox .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav -t f32 -e floating-point - > .shokunin/audio/corpus/live/round-49/executor/decoded-48001.f32 && sox .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav -t f32 -e floating-point - > .shokunin/audio/corpus/live/round-49/executor/decoded-48000.f32 && cmp .shokunin/audio/corpus/live/round-49/executor/decoded-48001.f32 .shokunin/audio/corpus/live/round-49/executor/decoded-48000.f32 && sha256sum .shokunin/audio/corpus/live/round-49/executor/decoded-*.f32
```

Both decoded f32 files have SHA-256 `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f`. The header rate changes reported duration and the frequency grid used for centroid; identical decoded samples do not establish identical physical-time signals or resampling/converter behavior.

## Errors and bounds

Executor reported no setup errors, numeric fit failures, or transcription corrections. These are executor observations; I made no independent measurements and no audition. This is numerical fixture calibration only. No inference about arbitrary sample rates, conversion/resampling, audio quality or perception, production, rights, engine behavior, publishing, or promotion.
