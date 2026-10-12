# Round 11 alternate slope candidate (r11-alt)

## Result

Built an original-PCM alternate candidate that isolates the declared internal side-slope mismatch proxy in the current numerical fixture checks. This is analytic fixture manipulation only; it is not a perceptual, engine, security, or production claim. The experiment used the existing original `stem_layer.wav` fixture, not borrowed audio.

## Recipe and identity

Source: `.shokunin/audio/corpus/artifacts/stem_layer.wav` (PCM16, mono, 48 kHz, 192000 frames; SHA-256 `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`). Read its signed little-endian PCM16 frames, increment frame 96001 by 66 integer PCM counts, and write all frames unchanged otherwise as PCM16 mono 48 kHz to `.shokunin/audio/corpus/live/round-11/slope_alt_candidate.wav`. This changes only the right-side neighbor of the round-11 join. Candidate SHA-256: `79b79e5150b0a8e517dc9cda8d3019f929723696dd993c0a7cb245cdfc05c2e5` (384044 bytes). Machine-readable details are in `slope_alt_telemetry.json`.

## Measurements

For decoded samples `x`, the current round-10 join gap is `abs(x[96000]-x[95999])`; the proposed internal slope mismatch is `abs((x[96001]-x[96000])-(x[95999]-x[95998]))`. At frames 95998–96001 candidate PCM is `[-0.0003662109375, -0.00018310546875, 0.0, 0.002960205078125]`. Left slope is `0.00018310546875`, right slope `0.002960205078125`, mismatch `0.002777099609375` FS/sample (> .001), while join gap is `0.00018310546875` FS (<= .03). Thus the existing join gate passes and the declared new proxy would fail.

Generic/current fixture telemetry: 4.0 s, mono 48000 Hz PCM16; peak `0.05999755859375` FS; RMS `0.030570242` FS (`-30.2875663558` dBFS); magnitude-weighted spectral centroid `313.4039877069` Hz and bandwidth `1662.7569325209` Hz; outer endpoint delta `0.00091552734375` FS; outer loop slope delta `0.000030517578125` FS/sample. These satisfy the stated generic level/spectrum and outer-loop limits (peak < .95, RMS > .001, centroid 100–2000 Hz, outer endpoint <= .03, outer slope <= .001). The 120 Hz section amplitudes are `[0.011999587449951306, 0.059997745854363925]` FS; section RMS `[0.00848499400645195, 0.042424814204089875]`; amplitude contrast `13.9793723784` dB, exceeding the existing 6 dB contrast condition. Candidate therefore fits the stated isolation conditions numerically. LUFS was not measured.

## Command record

Only shell command run: `ffprobe -v error -show_entries stream=sample_rate,channels,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-11/slope_alt_candidate.wav` — exit 0; reported 48000 Hz, mono, 16-bit, 4.000000 s. Candidate construction and metric calculations were performed in the Python REPL, not a shell command. No source or canonical file was edited.
