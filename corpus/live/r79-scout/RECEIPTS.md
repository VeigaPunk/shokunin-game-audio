# R79 scout receipts index

Seat: scout (leaf). Repo `~/Projects/shokunin/audio-shokunin` @ HEAD `731937c`.
Write scope: `corpus/live/r79-scout/` + `reports/round-79/r79-scout.md` only.
`corpus/fixtures/measure_audio.py` never read/imported (r78 author in flight).
Toolchain: `toolchain.txt`. Bounds: every leg triple-bounded (consumer flag,
subprocess timeout <= 15 s, reader cap); tone legs fail closed on a non-probe-owned
playback target. Contamination windows: report section 9.

| artifact | sha256 (first 16) | bytes | content |
| --- | --- | --- | --- |
| `probe-a-shape-r79.json` | `ecd95e43e341abf9` | 18523 | A1 shape/props/ports/internal-topology + A2 prop syntax + A3/A4 channel-map + A5/A6 one-sided autoconnect |
| `probe-b-capture-r79.json` | `34f6977cabf06cb1` | 49294 | 12 -C legs + 4 channel-map legs; capture-side lattice, prop precedence, downmix signature |
| `probe-c-playback-r79.json` | `712c074def3c7559` | 28437 | 10 -P legs; playback-side lattice, prop precedence with content control, playback-side decoration |
| `probe-d-pwcat-r79.json` | `ae5db5746f1f448c` | 21188 | 10 latency legs + 3 stream.capture.sink-on-playback legs + 4 record-target legs (first pass) |
| `probe-d2-record-targets-r79.json` | `3a439f10f9700065` | 8358 | 4 pw-record --target legs with the link graph sampled while the record stream is alive |
| `probe-e-hotplug-r79.json` | `699205621cabef99` | 14754 | E1 unload playback target / E2 load playback target / E3 unload capture target, phased topology + content |
| `probe-f-filterchain-r79.json` | `f32c185d28c4bc04` | 9996 | 6 conf.d loader legs + 5 pw-cli legs; parse-soft/runtime-fatal split + DSP content witness |
| `r79_probe.py` | `5b51d94e8625d337` | 16167 | shared harness (bounded subprocess, pw-dump graph, own WAV/FFT classifier, fail-closed tone pin) |
| `probe_a_shape.py` | `e24e3143e8608673` | 5872 | driver |
| `probe_b_capture.py` | `f2647281093a0eb0` | 5240 | driver |
| `probe_c_playback.py` | `0a1552bc164e52ba` | 3503 | driver |
| `probe_d_pwcat.py` | `e2679fab07ae9c67` | 7526 | driver |
| `probe_d2_record_targets.py` | `860bd2f8a8b9a4bc` | 3067 | driver |
| `probe_e_hotplug.py` | `c2d1b8134c917d85` | 7276 | driver |
| `probe_f_filterchain.py` | `94582ef7fe65da10` | 12943 | driver |
| `dump_filter.py` | `4929e7d6b3d36c05` | 1637 | recon helper: pw-dump -> compact node/port/module table |

Raw records: `raw/*.wav` (24000-frame probe-sink monitor captures, 96044 B each).
Tones: `scratch/tone_r79_long.wav` (40 s, L 1 kHz / R 1.5 kHz, amp 8192, 48 kHz s16),
`scratch/silence_r79.wav` (2 s digital silence).

Labrat dispatch: one `ufo-labrat` spawned (hypothesis: filter-chain conf.d
fragment merge-append + parse-vs-runtime split). It reported **NOT EXECUTED** —
its seat exposes read-only filesystem tools only (no exec, no `pipewire`), the
same constraint the r78 labrat recorded. Zero writes, zero commands. H1 was
answered by this seat's `probe-f-filterchain-r79.json`; no measured claim here
comes from the labrat.

Trim note: raw/ keeps one record per cited content claim (B01/B08 tone, CM1-4, C07 + control, A3/A4, D2a-d, D17, E1/E2/E3 pre/post, F1/F3/F3b/F7); redundant duplicate passes were removed. Scratch keeps the tone fixtures + logs.

| `make_fixtures.py` | `91c3a872f819a028` | 1526 | regenerates the trimmed tone/silence fixtures deterministically (`python3 make_fixtures.py` before re-running any driver) |
