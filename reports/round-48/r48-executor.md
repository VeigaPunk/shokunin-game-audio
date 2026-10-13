# Round 48 executor — adjacent UI sample-rate pair

## Result

Generated two original 5760-frame mono PCM16 WAVs at 47999 and 48000 Hz. Both pass the UI duration tolerance (actual ffprobe durations 0.120003s and 0.120000s), peak/RMS checks, and 250–4000Hz centroid band. The 47999Hz file has exactly one failure, `format: expected 48kHz mono`; the 48000Hz file has no failures. The source PCM values and the actual SoX-decoded f32 sample sequences are byte-identical across files (successful `cmp`; decoded hash below). This compares the same discrete sample sequence at adjacent header rates, not resampling behavior.

| WAV | SHA-256 | Frames | ffprobe sample rate / channels / codec / bits | ffprobe duration | Project SoX-decoded centroid | Bandwidth | Peak FS | RMS dBFS | Integrated LUFS | Failures |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| `ui-47999.wav` | `71551e200633e62b1b9db4ee5a582f8d4d996cd693f2e4a040a96023b130a210` | 5760 | 47999 / 1 / pcm_s16le / 16 | 0.120003 s | 1022.5148421151724 Hz | 586.904753883307 Hz | 0.27996826171875 | -18.327858226717105 | null | `format: expected 48kHz mono` only |
| `ui-48000.wav` | `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c` | 5760 | 48000 / 1 / pcm_s16le / 16 | 0.120000 s | 1022.536144951523 Hz | 586.9169813204176 Hz | 0.27996826171875 | -18.327858226717105 | null | none |

Both peaks are <.95, RMS levels are >.001, and centroids are within 250–4000Hz. Null integrated LUFS is the helper result, not a failure. The two WAV SHA-256 values differ because WAV headers encode their different rates. SoX decoded f32 outputs have identical SHA-256 `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f` and byte-compare equal.

## Recipe and fitting

`generate.py` creates one n=5760 sample array at a fixed 48000Hz time grid: `t=np.arange(n)/48000`, `x=.28*sin(2*pi*1000*t)*np.hanning(n)`, quantized with `np.rint(np.clip(x,-1,1)*32767).astype('<i2')`. It writes those identical PCM bytes into a one-channel, two-byte/sample WAV, setting only the requested header sample rate (47999 or 48000). Thus sample values are identical and only declared sample rate differs. Centroid is computed by the project `measure_audio.py` after SoX f32 decode, using each actual ffprobe sample rate for the FFT frequency grid.

No unsuccessful numeric fits: the first measured pair met requested non-rate gates, distinct sequence match, duration and sole-format-failure outcomes. No resampling was performed. No audition or quality, perception, production, rights, engine, publishing, or promotion inference was made.

## Exact shell commands and exits

Run from `/home/vgpnk/Projects/prymeagnt/audio`.

Generation, hashes and both ffprobe probes (overall exit **0**):

```sh
python3 .shokunin/audio/corpus/live/round-48/executor/generate.py .shokunin/audio/corpus/live/round-48/executor/ui-47999.wav 47999 && python3 .shokunin/audio/corpus/live/round-48/executor/generate.py .shokunin/audio/corpus/live/round-48/executor/ui-48000.wav 48000 && sha256sum .shokunin/audio/corpus/live/round-48/executor/ui-*.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-48/executor/ui-47999.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-48/executor/ui-48000.wav
```

The first ffprobe returned stream `sample_rate="47999"`, `channels=1`, `codec_name="pcm_s16le"`, `bits_per_sample=16`, format `duration="0.120003"`; the second returned `sample_rate="48000"`, same remaining stream fields, `duration="0.120000"`.

Project helper measured both (exit **0**):

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-48/executor"); print(json.dumps({"47999":m.measure("ui",m.SPECS["ui"],d/"ui-47999.wav"),"48000":m.measure("ui",m.SPECS["ui"],d/"ui-48000.wav")},indent=2))'
```

SoX decode and exact sequence comparison (exit **0**):

```sh
sox .shokunin/audio/corpus/live/round-48/executor/ui-47999.wav -t f32 -e floating-point - > .shokunin/audio/corpus/live/round-48/executor/decoded-47999.f32 && sox .shokunin/audio/corpus/live/round-48/executor/ui-48000.wav -t f32 -e floating-point - > .shokunin/audio/corpus/live/round-48/executor/decoded-48000.f32 && cmp .shokunin/audio/corpus/live/round-48/executor/decoded-47999.f32 .shokunin/audio/corpus/live/round-48/executor/decoded-48000.f32 && sha256sum .shokunin/audio/corpus/live/round-48/executor/decoded-*.f32
```

No setup errors, numeric fit failures, or transcription corrections. All reported observations are numerical fixture calibration only; they do not imply broader sample-rate behavior or resampling/converter behavior.
