# R49 reviewer — adjacent above-rate fixture check

## Scope and verdict

The declared numerical check is coherent: compare two opt-in probes, 48001 Hz and 48000 Hz, with the same 5760-frame mono PCM16 sample payload, and let the existing exact metadata predicate distinguish them. It is a fixture calibration result only. The 48001Hz file fails only the rate/channel format check; the 48000Hz file passes. This does not establish physical-time equivalence, conversion or resampling behavior, or anything about sound quality or perception.

At review time, `measure_audio.py` still had only the prior `--probe-ui-rate-47999` and `--probe-ui-rate-48000` CLI flags; it did not contain a 48001 flag or point its existing 48000 mode at a round-49 file. Thus the generated-pair measurements below support the calibration claim but do not verify the requested new opt-in CLI wiring. Keep any integration limited to adding the two modes and selecting their scratch fixtures; leave `format_failures(stream)`, `SPECS["ui"]` (including its `.12s` target and thresholds), and canonical fixtures unchanged.

## Exact observed commands and results

From `/home/vgpnk/Projects/prymeagnt/audio`, the executor reported this generation/hash/probe command with overall exit **0**:

```sh
python3 .shokunin/audio/corpus/live/round-49/executor/generate.py .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav 48001 && python3 .shokunin/audio/corpus/live/round-49/executor/generate.py .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav 48000 && sha256sum .shokunin/audio/corpus/live/round-49/executor/ui-*.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav
```

Observed ffprobe metadata: `ui-48001.wav` SHA-256 `92b22d8749c5f02d4f68d9a8daa32b935404f1d7cdbc31bca55af2f9adf4cb5a`, 48001 Hz, 1 channel, `pcm_s16le`, 16 bits, duration `0.119998` s; `ui-48000.wav` SHA-256 `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c`, 48000 Hz, 1 channel, `pcm_s16le`, 16 bits, duration `0.120000` s. Both duration values meet the UI `.12s ± .001s` check.

This exact project-helper measurement command exited **0**:

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-49/executor"); print(json.dumps({"48001":m.measure("ui",m.SPECS["ui"],d/"ui-48001.wav"),"48000":m.measure("ui",m.SPECS["ui"],d/"ui-48000.wav")},indent=2))'
```

Project SoX-decoded whole-wave results:

| Rate | Peak FS | RMS dBFS | Centroid Hz | Bandwidth Hz | Failures |
|---:|---:|---:|---:|---:|---|
| 48001 | 0.27996826171875 | -18.327858226717105 | 1022.557447787877 | 586.929208757528 | `format: expected 48kHz mono` only |
| 48000 | 0.27996826171875 | -18.327858226717105 | 1022.536144951523 | 586.9169813204176 | none |

Both numeric UI-level and centroid conditions fit: peak `< .95`, RMS above `.001`, centroid in `[250,4000]` Hz. `integrated_lufs` was `null` for both; it is not an added failure. The recorded SoX decode-and-compare command exited **0** (`sox ... -t f32 -e floating-point - > ...` for each file, followed by `cmp ...` and `sha256sum ...`); both decoded outputs were byte-identical, SHA-256 `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f`.

## Error distinctions and limits

For the pair measured here, the executor reports no setup errors, numeric fit failures, or report transcription corrections. The sole expected failure is the 48001Hz metadata-rate predicate. The differing header rate also changes reported duration and the FFT frequency grid used for centroid; identical decoded sample bytes do not prove identical physical-time signals. No audition was performed. No inference is made about arbitrary rates, resampling, quality, perception, production, rights, engine behavior, publishing, or promotion.
