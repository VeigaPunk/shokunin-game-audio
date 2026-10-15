# R78 scout receipts index

Seat: scout (leaf). Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`503689cecd96997e7509a967f2c1371e43b5066c` (measure_audio.py dirty at
`ac9b282e20311dce` — the r77 author's concurrent edit, +1397/−2; never
imported by this seat). Write scope: `corpus/live/r78-scout/` only.
Toolchain: `toolchain.txt` (PipeWire 1.6.8, libpulse 17.0, alsa-utils
1.2.16, ffmpeg n9.0.1, pipewire-jack 1.6.8, py 3.14.7, Linux 7.2.3).

| artifact | sha256 (first 16) | content |
| --- | --- | --- |
| `probe-props-lattice-r78.json` | `35a79f8dea833aea` | 22 prop legs + 6 resample legs; `-P` routing vs decoration lattice |
| `probe-pwlink-r78.json` | `d418f5cc7f7c1d0c` | target-0 manual pin, mid-run `pw-link -d`, FL-only pin, 2-producer mix, refusal classes, `-m` shape |
| `probe-parec-format-r78.json` | `215bf39e74d0c25c` | 25 `--file-format` legs, 12 `--fix-*` header legs, monitor-stream refusals |
| `probe-parec-rate-ms-r78.json` | `8b6aa5db6bfa7dd4` | 2.5 s raw byte-rate legs; `--monitor-stream` mine (tone carried) |
| `probe-parec-fixdisc-r78.json` | `254a112c8b401365` | fix-* discriminators (22050/s32/u8/c1 requests vs fix flags) |
| `probe-parec-fmtlong-r78.json` | `2b0e16150a157ea0` | flac/oga/caf/raw/wav at 1.3 s vs 3.0 s — granule-delay falsification |
| `probe-jack-ffmpeg-r78.json` | `442d6b0261e7f68c` | pw-jack/no-shim/named-target/env-props legs + ffmpeg alsa/oss lattice |
| `probe-midi-r78.json` | `f62ca44f82577a07` | arecordmidi/aseqdump/aplaymidi/aseqsend + pw-record -M midi refusals |
| `r78_probe.py` | `a8980b3986e919a8` | shared harness (own classifiers; never imports corpus/fixtures) |
| `probe_a_props.py` | `ffa0e2b58d391a01` | props lattice driver |
| `probe_b_pwlink.py` | `c804ec319709f6c3` | pw-link lattice driver |
| `probe_c_parec.py` | `4f61043a2cf05186` | parec format/fix/monstream driver |
| `probe_d_jack_ffmpeg.py` | `d67d18dc5847982d` | jack + ffmpeg device driver |
| `probe_e_midi.py` | `2132726bec658f49` | midi driver |
| `toolchain.txt` | `5fd90b36f1dd46be` | version pins |

In-line (non-file) evidence in `r78-scout.md`: disconnect-window content
peaks (0 vs 16384), two-producer mix supplement, jack manual pin, arecord
`-D pipewire|default|sysdefault` parity, Midi-Bridge serial-target refusal.

Labrat dispatch: one `ufo-labrat` spawned (hypothesis: parec flac 0-byte =
granule-delay vs broken). It reported **NOT EXECUTED** — its filesystem
view lacks exec capability, `parec`, and the pipewire sockets; zero writes,
zero commands, repository untouched. The hypothesis was answered by this
seat's own `probe-parec-fmtlong-r78.json` instead. Provenance recorded per
the exact-route rule.
