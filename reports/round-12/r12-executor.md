# Round 12 executor — provisional alternate layer candidate

## Scope and result

Built an original synthetic PCM16 little-endian WAV at `.shokunin/audio/corpus/live/round-12/layer_alt_candidate.wav`; no source, LOG, SCORECARD, canonical artifacts, or commits were changed. This is a provisional fixture candidate, not accepted coverage until parent integration and independent verification. It is synthetic measurement material only: no audible, engine/adaptive playback, rights beyond this generated signal, security, or production claim.

SHA-256: `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` (384044 bytes). Recipe: 48,000 Hz, mono, 16-bit signed PCM; 192,000 frames (4 s). For each frame `i`, use amplitude `.015` when `i < 96000`, otherwise `.050`, and `round(amplitude * sin(2*pi*180*i/48000) * 32767)` as the signed PCM sample. No borrowed samples.

## Commands and exits

- Python REPL generation using `wave`, `numpy`, `hashlib`: exit status not applicable (completed successfully); wrote the above WAV and computed its SHA-256.
- `ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json .shokunin/audio/corpus/live/round-12/layer_alt_candidate.wav && sox .shokunin/audio/corpus/live/round-12/layer_alt_candidate.wav -t f32 -e floating-point - | wc -c` — exit **0**; reports 48000 Hz, mono, 4.000000 s, 768000 decoded f32 bytes.
- `ffmpeg -hide_banner -nostats -i .shokunin/audio/corpus/live/round-12/layer_alt_candidate.wav -filter_complex ebur128=peak=true -f null -` — exit **0**; reports integrated loudness `-32.7 LUFS` (measurement only).

## Measured fit (decoded PCM)

All generic and join numbers below were computed from decoded f32 samples; no fixture checker currently registers this provisional file. Against the existing `stem_layer` band (100–2000 Hz) and generic gates:

| Metric | Candidate | Existing local criterion | Result |
|---|---:|---:|---|
| Format / duration | 48 kHz, mono / 4.000 s | 48 kHz mono / 4 s ±1 ms | pass |
| Peak | 0.049987793 FS | <0.95 | pass |
| RMS | 0.026099737 FS (`-31.67 dBFS`) | >=0.001 FS | pass |
| Whole-file positive-frequency magnitude-weighted centroid | 277.951385 Hz | 100–2000 Hz | pass |
| Spectral bandwidth | 1028.368376 Hz | telemetry only | — |
| Outer endpoint delta | 0.001190186 FS | <=0.03 for looping fixture | pass |
| Outer endpoint slope mismatch | 0.000793457 FS/sample | <=0.001 for looping fixture | pass |
| First/second 2 s 180 Hz component amplitudes | 0.014999922 / 0.049997872 FS | each >=0.01 and each-half RMS >=0.001 | pass |
| 180 Hz component amplitude contrast | 10.457251 dB | >=6 dB | pass |
| Internal join adjacent-sample delta | 0.000366211 FS | <=0.03 | pass |
| Internal join side-slope mismatch | 0.000854492 FS/sample | <=0.001 | pass |
| Distinctness vs `stem_layer` | duration delta 0 s; relative centroid delta 46.1799% (baseline centroid 190.143327 Hz) | duration >=0.020 s OR centroid change >=10% | pass |

No candidate fit failure was observed against these declared numeric checks. The existing thresholds are reused local proxies, not empirically calibrated hearing thresholds. Spectral centroid/bandwidth and loudness are generic computed descriptors, not timbre or perceived quality evidence. Distinctness is only the current duration/centroid comparison.

## Reproduction details / limitations

Decoded samples came from `sox ... -t f32 -e floating-point -`; metrics were computed with NumPy FFT, RMS, peak, sample-index join differences, and the 180 Hz DFT bin for each 96,000-frame half. The original candidate reaches a **provisional numerical fit**, not measured source integration: no `measure_audio.py` mode exists yet for it, and no unrelated historical modes, canonical hashes, receipt schema, or old-mode behavior were exercised here. Parent should decide whether to integrate this exact candidate, and verifier must independently check before counting a new measured variant. Do not infer adaptive playback, loop audibility, smoothness, engine behavior, music, or production readiness.
