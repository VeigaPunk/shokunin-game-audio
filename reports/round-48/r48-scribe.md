# Round 48 scribe decision table

## Scope

The Round 48 LOG declares a calibration check of 5760-frame, mono PCM16 UI-shaped fixtures at adjacent rates, with actual duration, level, and project SoX-decoded whole-wave centroid checked alongside the existing exact-rate format predicate. The integrated runner does not yet expose these two modes in the source I inspected: `--probe-ui-rate-below` and `--probe-ui-rate-at` are absent from `measure_audio.py`. Therefore this is a direct fixture/probe measurement and decision-table result, **not** an integrated runner receipt or runner exit status.

I ran the executor's existing scratch generator for both rates. The generated files are under `/tmp`, not the project tree. Their PCM payload bytes match exactly (11520 bytes each; payload SHA-256 `058cacc8a6cdf19afa215c4d386bb903ede8641b9aed0468ff4678ef327c9eea`). Whole-WAV hashes differ as expected because rate metadata differs. SoX-decoded lengths also both equal 5760 float samples. The project measurement recipe uses ffprobe's sample rate for the FFT frequency grid; accordingly the rate-adjusted centroid differs slightly, although decoded sample values / peak / RMS are identical.

## Decision table (observed measurements)

| Fixture | ffprobe stream metadata | ffprobe duration | SoX-decoded project measurements | Rate-format decision | Other declared UI gates | Expected overall fixture result* |
|---|---|---:|---|---|---|---|
| 47999 Hz | `sample_rate=47999`, `channels=1`, `codec_name=pcm_s16le`, `bits_per_sample=16` | 0.120003 s | 5760 samples; peak 0.27996826171875 FS; RMS -18.327858226717105 dBFS; centroid 1022.5148421151724 Hz | Fail: exact 48000 Hz requirement; sole format error `format: expected 48kHz mono` | Duration is 0.000003 s from .12 (within ±.001); peak < .95; RMS > .001; centroid within 250–4000 Hz. No other measured gate failure. | Exit 1 from ordinary runner once integrated (format failure only) |
| 48000 Hz | `sample_rate=48000`, `channels=1`, `codec_name=pcm_s16le`, `bits_per_sample=16` | 0.120000 s | 5760 samples; peak 0.27996826171875 FS; RMS -18.327858226717105 dBFS; centroid 1022.536144951523 Hz | Pass | Duration exact; peak < .95; RMS > .001; centroid within 250–4000 Hz. No other measured gate failure. | Exit 0 from ordinary runner once integrated |

*These are decisions obtained by applying the observed metadata and metrics to the existing `format_failures()` and UI numeric criteria; they are **not** executed integrated-runner exits. Runner integration is pending. I did not generate a JSON runner receipt.

## Error and inference accounting

- **Setup:** Both fixture generations, ffprobe calls and SoX decode/metric pipelines succeeded. No setup/tool error observed.
- **Numeric fit:** Neither fixture missed duration, level, or centroid limits. The 47999 Hz intentional exact-rate predicate mismatch is the sole expected validation failure, not a numeric fit failure. The 48000 Hz case meets all measured declared gates.
- **Transcription:** No transcription error in this report; command outcomes and measurements above are copied from the outputs recorded below. No runner exit is represented as observed.
- No audition was performed. This is numerical fixture calibration only. No inference is made about audible/perceptual quality, production, rights, conversion/resampling behavior generally, engine use, publishing, or promotion.

## Exact commands and exits

All commands ran from the repository root. The generator commands each returned **0**:

```sh
python .shokunin/audio/corpus/live/round-48/executor/generate.py /tmp/r48-47999.wav 47999
# exit 0
python .shokunin/audio/corpus/live/round-48/executor/generate.py /tmp/r48-48000.wav 48000
# exit 0
```

The actual probe command for each file was:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json /tmp/r48-47999.wav
# exit 0
sox /tmp/r48-47999.wav -t f32 -e floating-point - | python -c 'import sys,numpy as n; x=n.frombuffer(sys.stdin.buffer.read(),dtype="<f4").astype(n.float64); rate=47999 if len(x)==5760 else 48000; f=n.fft.rfftfreq(len(x),1/rate); s=n.abs(n.fft.rfft(x)); rms=n.sqrt(n.mean(x*x)); print("samples",len(x),"peak",n.max(n.abs(x)),"rms",rms,"rms_dbfs",20*n.log10(rms),"centroid_hz",n.dot(f,s)/s.sum())'
# exit 0 (pipeline status; no pipefail set)

ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json /tmp/r48-48000.wav
# exit 0
sox /tmp/r48-48000.wav -t f32 -e floating-point - | python -c 'import sys,numpy as n; x=n.frombuffer(sys.stdin.buffer.read(),dtype="<f4").astype(n.float64); rate=47999 if len(x)==5760 else 48000; f=n.fft.rfftfreq(len(x),1/rate); s=n.abs(n.fft.rfft(x)); rms=n.sqrt(n.mean(x*x)); print("samples",len(x),"peak",n.max(n.abs(x)),"rms",rms,"rms_dbfs",20*n.log10(rms),"centroid_hz",n.dot(f,s)/s.sum())'
# exit 0 (pipeline status; no pipefail set)
sha256sum /tmp/r48-47999.wav /tmp/r48-48000.wav
# exit 0
```

Whole-file SHA-256: 47999 Hz `71551e200633e62b1b9db4ee5a582f8d4d996cd693f2e4a040a96023b130a210`; 48000 Hz `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c`. The generator script itself is in the executor scratch area; no shared runner/source, LOG, SCORECARD, canonical fixture, or other report was edited. No commit or push.
