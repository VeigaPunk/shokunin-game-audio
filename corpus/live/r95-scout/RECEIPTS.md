# r95-scout receipts index — JACK↔PipeWire interop (pipewire-jack 1.6.8)

Host plazir27, 2026-10-15 19:30–20:55Z. HEAD `2333fac`. All receipts are untracked,
written by `probes/r95driver.py` (own bounded runner; own synth; own Goertzel; no
import of `corpus/fixtures/measure_audio.py`). `receipts.sha256` pins every file;
`summary.json` is a compact extraction of all of them.

| receipt | stage | legs / reps | what it pins |
| --- | --- | --- | --- |
| `a_avail.json` | avail | 1 static + censuses | no jackd/jack_lsp; pipewire-jack 1.6.8; libjack sha; 168/218 exports; jack.conf option list; man pages; settings metadata; defaults |
| `b_shape.json` | shape | 3 reps | JACK client = PW client+node (`client.api=jack`, `node.always-process=true`); port alias triple; flag mapping; monitor API local-only; whole-graph census 71 ports; latency defaults 0/0; residue 0 |
| `b_shape_xconnect.json` | shape_xconnect | 3 arms × 3 reps | addressing law: rendered name rc 0 / native name rc 22 / fill-aliases object.path rc 0, with link presence during the run |
| `b_tone_unlinked.json` | tone_unlinked | 3 reps | unlinked JACK client runs while a driver is active (cb 38/38/37), zero links |
| `b_nameproj.json` | nameproj | 3 arms × 3 reps | `node.description` override → open status 4 (JackNameNotUnique); `node.name` override → status 0 |
| `c_jack2pw.json` | jack2pw | 3 reps | JACK→PW byte witness: link present, WAV peak 0.5 / rms 0.294556 / mag² 912488472.0 (3/3 identical) |
| `c_pw2jack.json` | pw2jack | 3 reps | PW→JACK byte witness: in_peak 0.499969482, in_nonzero 71997, mag² 323955146.78 |
| `d_quantum.json` | quantum | 4 arms × 3 reps | per-client `node.force-quantum`; cross-client quantum; live set + buffer-size callback; `PIPEWIRE_QUANTUM`; `pw-jack -p` |
| `d_global.json` | global | 3 reps | `jack.global-buffer-size=true` → settings `clock.force-quantum=512`, persists past exit, reset via `set_buffer_size(1)` → 0 (verified) |
| `e_xrun.json` | xrun | 3 reps × (control+stall) | control `xrun_cbs=1` 3/3; 150 ms stalls do not fire the callback; delayed values ≤ 0.004 |
| `e_latency.json` | latency | 3 reps | default 0/0; sets invisible pre-activate, read back `[100,200]`/`[10,20]`, total 150 |
| `e_rtprio.json` | rtprio | 3 reps × 7 calls | RT-priority accessors return stack garbage (values listed in the report) |
| `f_transport.json` | transport | 3 reps | start→Rolling/frame 22528, stop→Stopped, locate/reposition rc 0 but inert |
| `g_metadata.json` | metadata | 3 reps | `jack_set_property` → PW `default` metadata row keyed by registry id; round-trip; removal leaves no row |
| `summary.json` | — | extraction | compact machine-readable roll-up of all of the above |

Raw runs: `runs/battery1.log` (jack2pw→metadata), `runs/battery2.log` (transport,
metadata re-run), `runs/quantum2.log`, `runs/smoke_tone.json`.
Stimulus/captures: `scratch/tone997.wav` (own synth), `scratch/c1_rep{0,1,2}.wav`
(the three captured JACK→PW monitors).
Sources: `sources/` (version-matched PipeWire 1.6.8 files, `SOURCES.md`,
`SOURCES.sha256`, `BINARIES.sha256`).

Exit state: 0 seat modules, 0 seat nodes/clients/ports, 0 seat processes, defaults
unchanged, `clock.force-quantum=0`; 4 permanent `stream-properties` rows
(`r95s_d1/d2/d3` from the description experiment, `r95s_ns` from the first manual rig).
