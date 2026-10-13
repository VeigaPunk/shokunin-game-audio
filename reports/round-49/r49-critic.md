# R49 critic — format isolation and rate-tag confounds

## Scope and finding

The available 48001/48000 pair supports a **fixture-level exact-format predicate check**, not full physical-time isolation. Both WAVs contain the same 5760 PCM16 values (payload SHA-256 `058cacc8a6cdf19afa215c4d386bb903ede8641b9aed0468ff4678ef327c9eea`), but the header-rate change changes the represented duration and frequency axis. At 48001 Hz, duration is 0.119998 s; at 48000 Hz, it is 0.120000 s (2 microseconds apart, each within the declared ±1 ms duration tolerance). Identical discrete samples therefore do not encode an identical signal over physical time. This is a rate-tag/metadata fixture, **not a test of resampling or converter behavior**.

The project measurement yields the intended sole format failure at 48001 and no failure at 48000. The unchanged `format_failures` predicate is exact integer `sample_rate == 48000` plus mono (and separately PCM16); thus this fixture demonstrates its boundary on these two generated files. It does not demonstrate behavior for arbitrary rates or validate a general audio conversion workflow.

## Evidence and exact commands

Executor WAV SHA-256: 48001 `92b22d8749c5f02d4f68d9a8daa32b935404f1d7cdbc31bca55af2f9adf4cb5a`; 48000 `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c`. Their PCM payload hashes match. SoX-decoded project-f32 SHA-256 matches for both: `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f` (5760 samples, 23040 bytes).

- `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/executor/ui-48001.wav` — **exit 0**. Actual metadata: 48001 Hz, mono, `pcm_s16le`, 16 bit; duration `0.119998` s.
- `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-49/executor/ui-48000.wav` — **exit 0**. Actual metadata: 48000 Hz, mono, `pcm_s16le`, 16 bit; duration `0.120000` s.
- Project helper invoked against both absolute WAV paths:
  `python3 -c 'import importlib.util; s=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); from pathlib import Path; print(m.measure("ui",m.SPECS["ui"],Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-49/executor/ui-48001.wav"))); print(m.measure("ui",m.SPECS["ui"],Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-49/executor/ui-48000.wav")))'` — **exit 0**.
  - 48001: peak `0.27996826171875`, RMS `-18.327858226717105 dBFS`, centroid `1022.557447787877 Hz`, failures `['format: expected 48kHz mono']` only.
  - 48000: peak `0.27996826171875`, RMS `-18.327858226717105 dBFS`, centroid `1022.536144951523 Hz`, failures `[]`.
  - Centroid differs by about `0.021303 Hz`; the FFT frequency grid is rate-dependent even for matching decoded sample values. Both centroids lie inside the UI fixture band. This is numeric measurement only, not a perception or quality judgment.

Independent alt pair also had matching PCM payload SHA-256 `b9542500b2c252351c8861587abaaeb01ed73bcdb4fb995fa13b578183d236a1`. Its project measurements passed the ordinary gates except the expected 48001 format failure. Centroids were `2595.3844257189635 Hz` (48001; sole format failure) and `2595.3303563365407 Hz` (48000; no failures); peak `0.279998779296875`, RMS `-14.906829610550412 dBFS`, duration/format metadata as above. This second pair likewise changes physical duration and FFT frequency axis with its header rate.

## Setup errors and limits

`python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48001` — **exit 2**, unrecognized argument. The checked-in measurement CLI still exposes round-48 `--probe-ui-rate-47999` and `--probe-ui-rate-48000` modes, not a round-49 48001 mode. This is an integration/setup mismatch, not a failed numeric fit or gate result. A first ad-hoc helper call with a relative `Path` — `python3 -c 'import importlib.util; s=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); from pathlib import Path; print(m.measure("ui",m.SPECS["ui"],Path(".shokunin/audio/corpus/live/round-49/executor/ui-48001.wav"))); print(m.measure("ui",m.SPECS["ui"],Path(".shokunin/audio/corpus/live/round-49/executor/ui-48000.wav")))'` — **exit 1**, `ValueError` because that relative path is outside the helper's resolved corpus root. Retrying with absolute paths succeeded (above). No numeric fit failed; do not conflate the two setup errors with fixture outcomes.

I did not infer audible quality, perceived behavior, production readiness, rights, engine integration, publishing, or promotion. No audition was performed. No source or shared LOG/SCORECARD/canonical files were changed by this critic.
