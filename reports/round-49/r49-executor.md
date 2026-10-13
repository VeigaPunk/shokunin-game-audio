# Round 49 executor — above-rate UI sample-rate pair

## Result

Generated original 5760-frame mono PCM16 UI-shaped WAVs at 48001 and 48000 Hz. Both meet the UI duration tolerance (ffprobe durations 0.119998s and 0.120000s), peak/RMS limits, and 250–4000Hz centroid band. The 48001Hz measurement has exactly one failure, `format: expected 48kHz mono`; the 48000Hz measurement has none. SoX-decoded f32 outputs compare byte-identically (`cmp` exit 0), with SHA-256 `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f` for each. This is a numerical fixture calibration pair, not a claim of physical-time signal equivalence or resampling behavior.

| WAV | SHA-256 | Frames | ffprobe sample rate / channels / codec / bits | ffprobe duration | Project SoX-decoded centroid | Bandwidth | Peak FS | RMS dBFS | Integrated LUFS | Failures |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| `ui-48001.wav` | `92b22d8749c5f02d4f68d9a8daa32b935404f1d7cdbc31bca55af2f9adf4cb5a` | 5760 | 48001 / 1 / pcm_s16le / 16 | 0.119998 s | 1022.557447787877 Hz | 586.929208757528 Hz | 0.27996826171875 | -18.327858226717105 | null | `format: expected 48kHz mono` only |
| `ui-48000.wav` | `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c` | 5760 | 48000 / 1 / pcm_s16le / 16 | 0.120000 s | 1022.536144951523 Hz | 586.9169813204176 Hz | 0.27996826171875 | -18.327858226717105 | null | none |

Both peaks are below .95 and RMS levels exceed .001; both centroids are within 250–4000Hz. `null` LUFS is the helper's reported undefined loudness result, not a failure. The generated sample array uses `t=np.arange(5760)/48000`, `x=.28*sin(2*pi*1000*t)*np.hanning(5760)`, clipped/rounded to little-endian PCM16; those same PCM bytes are written with the respective header rates. WAV SHA values differ because headers encode different rates. The helper computes the centroid frequency grid using each probed header rate, so small differences in duration and centroid are expected from the rate tag.

## Exact shell commands and exits

Commands ran from `/home/vgpnk/Projects/prymeagnt/audio`.

Generation, WAV SHA-256, and ffprobe metadata (overall exit **0**):

```sh
python3 .shokunin/audio/corpus/live/round-49/executor/generate.py .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav 48001 && python3 .shokunin/audio/corpus/live/round-49/executor/generate.py .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav 48000 && sha256sum .shokunin/audio/corpus/live/round-49/executor/ui-*.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav
```

The first ffprobe returned `sample_rate="48001"`, one channel, `pcm_s16le`, 16 bits, duration `0.119998`; the second returned `sample_rate="48000"`, the same remaining stream fields, duration `0.120000`.

Project measurement via `measure_audio.py` (exit **0**):

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); d=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-49/executor"); print(json.dumps({"48001":m.measure("ui",m.SPECS["ui"],d/"ui-48001.wav"),"48000":m.measure("ui",m.SPECS["ui"],d/"ui-48000.wav")},indent=2))'
```

SoX decode, `cmp`, and decoded hashes (overall exit **0**):

```sh
sox .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav -t f32 -e floating-point - > .shokunin/audio/corpus/live/round-49/executor/decoded-48001.f32 && sox .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav -t f32 -e floating-point - > .shokunin/audio/corpus/live/round-49/executor/decoded-48000.f32 && cmp .shokunin/audio/corpus/live/round-49/executor/decoded-48001.f32 .shokunin/audio/corpus/live/round-49/executor/decoded-48000.f32 && sha256sum .shokunin/audio/corpus/live/round-49/executor/decoded-*.f32
```

No setup errors, numeric fit failures, or transcription corrections. No audition occurred. These observations do not support quality, perception, production, rights, engine, publishing, or promotion inference.
