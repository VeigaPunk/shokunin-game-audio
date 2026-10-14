# R76 author — capture direction: bounded record operations

Round: 76. Wave: `shokunin-train-20261101-w15`. Host `plazir27`
(measured 2026-10-14 ~18:15–18:30 UTC): PipeWire **1.6.8** (`Server
Name: PulseAudio (on PipeWire 1.6.8)`), pacat **17.0-98-gb096**
(libpulse **17.0.0**, protocol 35), alsa-utils **1.2.16**, ffmpeg
**n9.0.1** (libavformat **63.1.101**), Python **3.14.7**. All claims are
THIS-HOST measurements — named tool versions only, no portable
generalization.

Assignment arm implemented: `--probe-capture-r76` — the RECORD-side
complement to r75's playback consumers: `pw-record`, `parec`/`parecord`,
`arecord`, and two lavf capture legs (`-f pulse`, `-f alsa`). New ledger
family `capture_*_r76_probe` ×6 entries; same ledger idiom; **prior rows
untouched** (the diff is pure insertion — `+1123/−3` where the 3 touched
lines are the mutex sum and the `mode`/`suffix` ternary chains, each
preserving the prior expression verbatim and prepending the r76 clause).

## Landed changes (`corpus/fixtures/measure_audio.py`)

- `_capture_inventory()` — the enumeration of record: `pactl list
  sources short`, `pactl info`, `pw-link -o`, `arecord -l`/`-L`,
  `ffmpeg -h demuxer={pulse,alsa}`. Every dependent leg gates on it —
  an absent source/device lands a named `blocked`, never fabricated
  audio.
- `_capture_wav_inspect()` — structural walk of a just-written output:
  file size, RIFF size field, chunk table (stops at `data`), fmt
  fields, and declared-vs-actual data size. Size fields are CLASSIFIED
  (`finalized | placeholder_8 | placeholder_ff | placeholder_80000000 |
  zero | other`) so a severed write lands a named class instead of a
  volatile byte count.
- `_capture_parser_verdict()` — stdlib `wave` + `ffprobe` usability on
  a possibly-unfinalized wav; `wave_frames_class`
  (`honest|honest_empty|underreports|inflated|short`) compares the
  reported frame count to the honest one — this is what exposes
  arecord-KILL's accept-and-lie (see below).
- `_capture_errclass` — first-match named failure classes, most
  specific first: `no_target_node`, `pw_connect_failed`,
  `pa_no_such_entity`, `pa_connect_failed`, `alsa_channels`,
  `alsa_hwparams`, `alsa_unknown_pcm`, `alsa_busy`, `ffmpeg_muxer`,
  `ffmpeg_alsa`, `ffmpeg_esrch`, `ffmpeg_io`, `aborted_by_signal`.
- `_capture_run` / `_capture_file_leg` — one bounded leg (outer
  `subprocess` timeout; recorded rc + error class + header inspect).
  `exact_bytes` legs record raw byte counts only where deterministic
  (pw-record `-n`, arecord `-d`); wall-domain legs record
  `duration_bucket_s` + classes so timing never destabilizes the
  receipt. `str(out)` is normalized to `<out>` in argv and error lines.
- `_capture_sever_cell` — spawn → wait → SIGTERM/SIGKILL → classify the
  wound (rc + header classes + parser usability); a leg that exits
  before the sever (held device) lands `early_exit_code` as honest
  data, not a wound verdict. Outer bound: KILL on the process group.
- `capture_gate_r76_entry` — inventory + viability digest + 12 named-
  failure gate legs.
- `capture_bounded_r76_entry` — one native bound per consumer +
  `wall_lt_0.5s` pacing class (a paced `-d N` leg cannot beat its own
  duration; the unpaced null device can).
- `capture_sever_r76_entry` — TERM/KILL matrix on 4 consumers;
  pulse/pipewire cells run before the arecord hw cells so PipeWire's
  suspend-release window has elapsed (a still-held card lands the
  named `alsa_busy` early-exit, never a retry).
- `capture_name_axis_r76_entry` — extension-vs-flag container
  selection per consumer.
- `capture_device_axis_r76_entry` — the arecord `-D` capture axis.
- `capture_roundtrip_r76_entry` — `pw-cat -p` the 4.0 s pacer into the
  default sink while `pw-record` captures its monitor for exactly 5 s;
  captured bytes re-fed through the EXISTING `sox -V6` detect leg and
  `aplay` content-magic leg, with a nonzero/peak content witness.
- Flag wired: argparse `--probe-capture-r76`, the mutex sum, the
  `mode`/`suffix` chains (`probe-capture-r76` / `-capture-r76`).

## Source/device gate (the enumeration of record)

- `pactl list sources short` (rc=0): 2 non-monitor sources
  (`…HiFi__Line__source`, `…HiFi__Mic__source`) + 4 sink monitors
  (HDMI, SPDIF, Speaker, Headphones). `Default Source:
  alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source`; `Default
  Sink: …HiFi__SPDIF__sink`.
- `pw-link -o` (rc=0): 12 monitor/capture ports.
- `arecord -l` (rc=0): card 0 (USB `Audio`), devices 0,1,2.
  `arecord -L`: `{null, sysdefault, pipewire, default,
  sysdefault:CARD=Audio, front:CARD=Audio,DEV=0}`.
- ffmpeg demuxers `pulse` + `alsa` both present.

All 12 named gate legs landed exactly the predicted (rc, class) pairs:

| leg | rc | class |
| --- | --- | --- |
| pw-record auto-target (no `--target`) | 1 | `no_target_node` |
| pw-record dead daemon (`PIPEWIRE_RUNTIME_DIR=/nonexistent`) | 1 | `pw_connect_failed` |
| pw-record `--target <sink>.monitor` (pactl alias is NOT a node) | 1 | `no_target_node` |
| parec bare (no `-d`) | 1 | `pa_no_such_entity` |
| parecord bare | 1 | `pa_no_such_entity` |
| parec `-d @DEFAULT_SOURCE@` + dead `PULSE_SERVER` | 1 | `pa_connect_failed` |
| ffmpeg `-f pulse -i default` (`default` is not a literal source) | 251 | `ffmpeg_io` |
| ffmpeg `-f alsa -i default` | 251 | `ffmpeg_alsa` (`cannot set parameters`) |
| ffmpeg `-f pulse` + dead `PULSE_SERVER` | 253 | `ffmpeg_esrch` |
| arecord `-D default -d 1` | 1 | `alsa_hwparams` (set_params:1462) |
| arecord `-D pipewire -d 1` | 1 | `alsa_hwparams` |
| arecord `-D does_not_exist` | 1 | `alsa_unknown_pcm` |

Gate signatures measured: `pw-record` does NOT resolve a default source
implicitly — `--target` is required, and monitor capture wants
`--target <sink> -P stream.capture.sink=true`. `parec`/`parecord`
require `-d`; `@DEFAULT_SOURCE@`/`@DEFAULT_MONITOR@`/literal names all
resolve. ffmpeg takes only literal device names.

## Bounded capture (per-consumer native bound + `timeout -s KILL` outer bound)

| leg | bound | rc | bytes / shape |
| --- | --- | --- | --- |
| pw-record `--target <line> -n 48000` | exact frame count | 1 | **192044** B, finalized (rc=1 is NOT the verdict) |
| pw-record monitor `-P stream.capture.sink=true -n 48000` | exact | 1 | **192044** B, finalized |
| arecord `-D hw:0,0 -d 1` | paced duration | 0 | **192044** B, `wall_lt_0.5s=false` (paced) |
| arecord `-D null -d 1` | unpaced duration | 0 | **192044** B, `wall_lt_0.5s=true` (CPU-speed oracle) |
| parec `--raw -d @DEFAULT_SOURCE@` | parent byte-cap 262144 B | 0 | exactly `cap_bytes` read, spec `s16le 2ch 48000Hz` |
| parecord `-d @DEFAULT_SOURCE@` | **SIGTERM is the only bound** | 0 | finalized wav, 64-KiB-aligned granule shape |
| ffmpeg `-f pulse -i <mon> -t 1` | wall-domain | 0 | finalized, `duration_bucket_s=1.0` |
| ffmpeg `-f alsa -i plughw:0,0 -t 1` | wall-domain | 0 | finalized, `duration_bucket_s=1.0` |

`-D null` is an exact-but-UNPACED oracle — never run unbounded (scout
measured ~5.8 GB/s rotation-file flood; the leg pins the `-d 1` form:
192044 B in ~0.01 s).

## Sever classes (TERM then `timeout -s KILL`-class bound)

| consumer | SIGTERM | SIGKILL |
| --- | --- | --- |
| pw-record | rc=**1**, header **finalized**, wave `honest` | rc=−9, riff `placeholder_8`, data declared `zero` over real bytes — unfinalized; wave **rejects** (`Error`), ffprobe tolerates |
| parecord | rc=0, finalized, flushed-64KiB-granule data, wave `honest` | rc=−9, riff `placeholder_8`, data `zero` + payload → unfinalized; wave rejects |
| ffmpeg | rc=**255**, finalized, wave `honest` | rc=−9, riff+data `placeholder_ff` — unfinalized class (missing/0-byte/placeholder header; flush granularity is muxer-internal); wave `inflated` |
| arecord `-D hw:0,0` | rc=1 `aborted_by_signal`, finalized, wave `honest` | rc=−9, data `placeholder_80000000` → wave **accepts and inflates** (declared ≫ actual) — accept-and-lie |

Parser-tolerance split is itself a measured class: wave rejects the
pw-record/parecord wound shapes but inflates the
arecord(0x80000000)/ffmpeg(0xFFFFFFFF) placeholder shapes; ffprobe
tolerates all of them. `rc` alone is never the verdict — pw-record
completes a bounded capture at rc=1; ffmpeg TERM lands rc=255 with a
usable file.

## Output-name axis (extension vs flag)

| consumer | `.wav` | `.raw` | `.bin` | explicit flag | class |
| --- | --- | --- | --- | --- | --- |
| pw-record | riff_wav | raw_stream | riff_wav | `--raw` on `.bin` → raw_stream | extension-driven, wav default for unknown suffix, flag override |
| parecord | riff_wav | raw_stream | riff_wav | `--file-format=wav` on `.raw` → riff_wav | extension-driven, wav default, flag override |
| arecord | — | — | riff_wav (no `-t`) | `-t wav` on `.bin` → riff_wav; `-t raw` on `.wav` → raw_stream | flag-driven, **name-blind** |
| ffmpeg | riff_wav | — | **missing** | `-f s16le` on `.bin` → raw_stream | extension-**STRICT**: unknown suffix fails the muxer (rc=234 EINVAL) before any capture; `-f` overrides |

## arecord `-D` device axis — the r75 INVERSION

`{default, pipewire}` accepted playback in r75 but are **blocked for
capture** (`alsa_hwparams`, set_params:1462) — transport direction
inverts the plugin-route viability. `{sysdefault, plughw:0,0, hw:0,0}`
all viable paced and byte-exact (192044 B); `hw:0,0 -c 1` lands the
named `alsa_channels` rejection; `-D null` the unpaced oracle. A held
device would land `alsa_busy` as honest data (none observed across the
two canonical runs).

## Roundtrip (stretch)

`pw-record -P stream.capture.sink=true --target <default-sink> -n
240000` captured exactly **960044 B** finalized (5.0 s × 48000 × stereo
× s16) while `pw-cat -p stem_sections.wav` (rc=0) played the 4.0 s
member. Detect legs on captured bytes vs the member: sox `wav==wav`,
aplay `WAVE==WAVE` — **same verdict class**, plus content witness
(`nonzero_fraction_gt_half=true`, `peak_within_3db_of_member=true`).
Same-class is bounded to measured fields; the capture is stereo
s16/48 k via the monitor mix (member is mono) — a channel/path
difference, not a verdict difference.

## Evidence

Commands (each run under an outer `timeout -s KILL 480`):

```
timeout -s KILL 480 python3 corpus/fixtures/measure_audio.py --probe-capture-r76
```

Receipts (`corpus/live/runs/`):

- `…T181454Z` — first end-to-end run, 3 falsified expectations that
  shaped the pinned classes (ffmpeg-KILL union class, arecord-KILL
  `riff_size=other`, sox argv absolute-path fix).
- `…T181743Z` — clean run, `failures: {}`.
- `…T182210Z`, `…T182305Z` — clean pair; differed in exactly one leaf
  (a tmp-path leak in a muxer `error` line) → path normalization
  added.
- `…T182450100472Z-capture-r76/measurements.json` —
  **`failures: {}`**, sha256
  `ba36cd70f765826a9937fc78c62143c984790f1bdc26a4ad8aaf813cfc00f92f`
- `…T182539237046Z-capture-r76/measurements.json` — **byte-identical**
  rerun, same sha256 `ba36cd70…`.
- Regression sanity: `--probe-failing` (`…T182621929798Z-failing`)
  reproduces its designed `ambience` failure signature — prior arms
  intact.

Hashes: fixture `corpus/fixtures/measure_audio.py` sha256
`691d730d4b4b2aa1475aa03bd4d9d7b5c9bdd3baf6a62d24923097f6fb9e9734`;
scratch harness `corpus/live/r76-author/scratch/sev_probe.py` sha256
`9c2c97eb79b1edf91a36f108e91c9834f9b035fbd0b8db649e8c321e1e3197b4`
(the pre-implementation probe harness that pinned the sever classes).

## Insertion-only discipline

`git status` non-untracked delta is exactly `M
corpus/fixtures/measure_audio.py`. New files (all untracked, operator
to commit): the 5 `-capture-r76` receipt dirs above, this report,
`corpus/live/r76-author/scratch/`, and the regression `-failing`
receipt. Two tracked files were touched by RUNS and restored to HEAD
bytes: `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
(accidental `py_compile` write) and `corpus/artifacts/ambience.wav`
(regenerated by `build_artifacts` on every run — **pre-existing
generator drift**, same size different content; every probe run
re-dirties it, this predates r76). Prior ledger rows: no receipt file
under `corpus/live/runs/` was modified (each run is a new timestamped
dir); the fixture diff is additive-only for all pre-existing flags.

## Limitations / honest edges

- All numbers are this-host pins: PipeWire 1.6.8, pacat 17.0-98,
  alsa-utils 1.2.16, ffmpeg n9.0.1 on `plazir27`.
- The arecord hw sever cells iterate enumerated `hw:` devices; under a
  foreign holder the leg records the named `alsa_busy` early-exit and
  `arecord_contention`/`arecord_*_blockage` instead of a wound verdict
  — contention is data, never a fabricated capture.
- parecord/ffmpeg sever cells use the direct `@DEFAULT_SOURCE@`/literal
  source (not the monitor) so resume latency does not destabilize the
  flushed-granule shape; monitor capture is still covered by
  `pwrecord_monitor_bound`, `ffmpeg_pulse_t`, and the roundtrip leg.
- The pw-record `--target <sink>.monitor` gate failure pins the
  pactl-alias-vs-node distinction; the working monitor form
  (`-P stream.capture.sink=true` on the sink node) is measured in the
  bounded and roundtrip legs.
- ffmpeg KILL's unfinalized class is a union {missing / 0-byte /
  `placeholder_ff` over a flushed prefix}; the aligned-vs-unaligned
  flush boundary was observed BOTH ways and is deliberately not pinned.
- No git mutation performed: no commits, no pushes, uncommitted writes
  only. Two unrelated pre-existing ffmpeg orphan processes from an old
  r70 experiment were observed and intentionally left untouched
  (scout's note; no author-created process remains — verified via
  `pgrep`).
