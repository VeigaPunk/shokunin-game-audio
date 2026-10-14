# R75 author — consumer breadth-2: paplay + aplay + ffplay

Round: 75. Wave: `shokunin-train-20261101-w14` (recovery dispatch —
`corpus/live/r75-author/` was empty at seat start; all work landed
fresh). Host `plazir27` (measured 2026-10-14 ~16:45 UTC): pacat
**17.0-98-gb096** (libpulse **17.0.0**, `Server Name: PulseAudio (on
PipeWire 1.6.8)`, default sink present), aplay **1.2.16**, ffplay
**n9.0.1** (libavformat **63.1.101**), 12 ALSA playback devices across
3 cards, PipeWire daemon live.

## Landed changes

`corpus/fixtures/measure_audio.py` (**+936/−3**; the 3 changed lines are
the mutex-sum, `mode`, and `suffix` chains — each preserves the prior
expression verbatim and adds only the r75 clause, same edit shape as
r73/r74):

- `paplay_leg` / `aplay_leg` / `ffplay_leg` — one bounded playback leg
  per consumer per transport. Invocation facts pinned by probe:
  - pacat reads stdin ONLY as its no-arg source — `paplay -` is a
    literal filename (`open(): No such file or directory`, rc=1);
    anonymous arms are `paplay -v` with piped/redirected stdin.
  - `aplay -D null -` reads stdin; the matrix fixes `-D null`
    (in-process plugin sink) so the input-parse verdict is
    device-free.
  - ffplay stdin is `-i -` (the `fd:` protocol); headless is
    `-nodisp -autoexit -v debug` under `SDL_AUDIODRIVER=dummy`.
- `consumer2_transport_entry(member, path)` — r73-shape matrix entry:
  per-consumer verdict groups keyed on that consumer's signature —
  paplay `(exit, pa_sample_spec, pa_error)`, aplay `(exit, alsa_kind,
  alsa_error)`, ffplay `(exit, ffplay_detected, avio_seeks,
  ffplay_invalid)`. A fork lands as a failure keyed by consumer (r67
  convention).
- `consumers2_paplay_ops_entry()` — daemon liveness, dead-server gate
  (`PULSE_SERVER=unix:<nonexistent>` on a valid member), gate ORDERING
  cell (dead server + writerless fifo), live-server writerless fifo
  kill class, the .snd name-axis control on identical bytes
  (named files {snd,wav,bin} + fifos {snd,wav,bin} + rfd — 7 legs),
  `--raw` bypass, empty-writer fifo.
- `consumers2_aplay_ops_entry()` — `aplay -l`/`-L` census, device axis
  `{null, default, pipewire, hw:<first card>}` on dec_act, writerless
  fifo kill class, name-axis control {snd,wav,bin} fifos, empty-writer.
- `consumers2_ffplay_ops_entry()` — `SDL_AUDIODRIVER` axis
  `{dummy,pulse,alsa}`, writerless fifo kill class, `-ss 2` position
  cell on the 4.0 s pacer (file vs stdin), empty-writer.
- `_nowriter_cell(argv, env)` — shared writerless-fifo kill-class
  probe (wait 3.0 s -> wchan -> SIGTERM -> 1.0 s -> SIGKILL group).
- `_consumer2_tail` — `_consumer_tail` plus scrubbing the r75 tails
  need: wholesale single-quote normalization and residual dir-prefix
  collapse (aplay/ffplay echo absolute + mkdtemp paths verbatim).
- Flag `--probe-consumers2-r75` wired through argparse, the mutex sum,
  and the `mode`/`suffix` chains (`probe-consumers2-r75` /
  `-consumers2-r75`).

## Measured (committed receipt `runs/20261014T165017429491Z-consumers2-r75`, `failures: {}`; byte-identical ×3 — sha256 `0829a5986b…` reproduced by `…T164819Z` and `…T164913Z`)

ARM — all 9 canonical members × 4 transports × 3 consumers, **27/27
verdict groups transport-INVARIANT**:

| member | paplay | aplay | ffplay |
|---|---|---|---|
| dec_act | `[0, 's16le 1ch 8000Hz', None]` | `[0, WAVE]` | `[0, wav, 0, F]` |
| dec_hcom | `[0, 's16le 1ch 8000Hz', None]` | `[0, WAVE]` | `[0, hcom, 0, F]` |
| extsuffix ×5 | `[1, None, 'Failed to open audio file.']` | `[0, 'raw data']` | `[0, None, 0, T]` |
| posttable_nomatch | rc1 reject | rc0 'raw data' | rc0 invalid |
| txw_piperefuse | rc1 reject | rc0 'raw data' | rc0 invalid |

- **paplay .snd name axis is DEAD — the r73 pw-cat fork does not
  transfer.** pacat opens via `sf_open_fd` (the fd-based libsndfile
  entry, strings-verified in `/usr/bin/paplay`): name-blind on every
  transport. The control ran 7 legs on identical no-magic bytes —
  `file:{axis.snd,axis.wav,axis.bin}`, `fifo:{axis.snd,axis.wav,
  axis.bin}`, `rfd` — all rc=1 'Failed to open audio file.' (where
  pw-cat's path-based `sf_open` accepted `.snd`). `paplay --raw` on the
  same fifo bytes -> rc=0 (decode-layer bypass, same as pw-cat).
- **aplay's name axis is invariant-ACCEPT** — the inverse polarity:
  content-magic parse, raw fallback (`u8/8000/mono`) accepts every
  unmatched buffer under all three fifo names -> `[0, 'raw data']`×3.
- **ffplay does NOT share mpv's inverted-seek fork on dec_hcom.** The
  `-v debug` surface shows `Statistics: 600 bytes read, 0 seeks` on
  ALL FOUR arms including the seekable file — the SDL pull model never
  issues the post-probe refresh seek that mpv's demuxer layer fires
  (mpv: seekable arm rc2 EPERM after probe drain). The hcom fork is an
  mpv-ism, not a lavf property. `ffplay_duration` records the residual
  seekable-bit evidence (`00:00:04.00` vs `N/A` on wav) without
  entering the verdict signature.
- **ffplay rc is never the verdict**: `Invalid data found when
  processing input` exits **rc=0** (matrix rejects, empty-writer, all
  five extsuffix members) — the detect+seek fields carry the verdict.

Ops rows (all pinned, `failures: {}`):

- **paplay**: `pactl` live; dead-server gate -> instant rc=1
  'pa_context_connect() failed: Connection refused' (1 ms). ORDERING
  cell — dead server + writerless fifo: blocked in `wait_for_partner`,
  TERM -> **−15**, stderr carries NO connection error: paplay opens
  INPUT FIRST, never reaches connect — the opposite order of pw-cat's
  gate-first. Live-server writerless fifo: same −15 (SIGTERM kills
  paplay outright — no custom disposition, unlike pw-cat's
  TERM-immune −9). Empty writer -> rc=1.
- **aplay**: census = 12 devices / 3 cards; plugins {null, pipewire,
  default} present. Device axis on dec_act (8 kHz mono): null/default/
  pipewire rc=0 WAVE — **default+pipewire are daemon-coupled plugin
  routes on this host** (default -> PipeWire); `hw:0,0` -> rc=1
  'aplay: set_params:1404: Channels count non available' — the
  kernel-device format-coupled rejection class, measured. Writerless
  fifo (-D null): blocked `wait_for_partner`; SIGTERM caught
  ('Aborted by signal Terminated...') yet STILL blocked -> SIGKILL
  -> **−9** (third kill class). Empty writer -> rc=1
  'aplay: read_header:2973: read error'.
- **ffplay**: SDL axis {dummy, pulse, alsa} all rc=0 wav on this host
  (pulse is daemon-coupled, alsa card-coupled — gates recorded per
  leg; the pin is only on dummy). Writerless fifo: blocked — but the
  wchan is `hrtimer_nanosleep` (avformat's open blocks in the READ
  THREAD while the main loop polls); SIGTERM -> graceful **exit 123**
  — a third class beside paplay's −15 and aplay/pw-cat's −9.
  `-ss 2` position cell: file arm seeks (avio `seeks:2`, duration
  `00:00:04.00`, 641580 B read) vs stdin arm `could not seek` +
  `seeks:0` + `N/A` duration (384044 B) — **path fork, not extent
  fork**: the non-seekable arm rescues by decode-discard and still
  plays the tail at rc=0 (contrast mpv's 4.0 s full play). Empty
  writer -> rc=0 'Invalid data found'.

Kill-class triplet on the identical writerless-fifo cell:

| consumer | wchan | TERM | result |
|---|---|---|---|
| paplay | wait_for_partner | kills | **−15** |
| aplay | wait_for_partner | caught, still stuck | **−9** |
| ffplay | hrtimer_nanosleep | graceful quit | **123** |
| pw-cat (r73/r74) | wait_for_partner | ignored | **−9** |

## Claim outcome

Consumer breadth extends the transport matrix without importing a
single fork: the .snd name axis is pw-cat-specific (`sf_open` path),
mpv's inverted-seek fork is mpv-specific (the second lavf consumer
never refresh-seeks), and aplay's forward-only content magic is
polarity-inverted on the name axis (accept-all vs paplay reject-all).
The three new consumers cover three distinct gate classes — pulse
daemon (input-first ordering), kernel device, SDL driver — and three
distinct kill classes on the same blocked cell.

## Known bounds / risks

- paplay matrix legs are viability-conditional on a reachable pulse
  server (same class as pw-cat); the gate cells record the condition
  rather than fabricating it.
- aplay's matrix verdict measures the input-side parse under `-D null`
  only; device-format constraints live in `device_axis` (hw leg is
  host-card-coupled — `hw:0,0` rejected 8 kHz mono on THIS host's USB
  Audio card; on a host with no card the cell degrades to a recorded
  blockage).
- `SDL_AUDIODRIVER=pulse|alsa` legs record host-dependent gates; only
  `dummy` is pinned.
- `wall_s` values are wall-clock leaves; semantic pins are `exit_code`,
  `wchan`, `sigterm_immune`, `blocked`, `could_not_seek`.
- `avio_bytes_read`/`avio_seeks` come from the `-v debug` `Statistics:`
  line; deterministic per member+arm on this build (641580/2 file vs
  384044/0 stdin on the startpos cell, reproduced ×3).
- stderr_tail determinism needed two racy-line filters (`Time:`/
  drain/index lines for pacat; status-spam + `ALSA lib` lines for
  ffplay) — verified by three consecutive byte-identical receipts.
- Scout scratch (`corpus/live/r75-scout/`) independently measured the
  same classes before this arm landed (paplay −15, aplay −9, ffplay
  123, .snd all-reject, hcom `seeks:0`) — cross-seat agreement.

**Seat stop.** Files changed: `corpus/fixtures/measure_audio.py` only
(+936/−3). Receipts: `corpus/live/runs/20261014T165017429491Z-
consumers2-r75` (committed shape) + two byte-identical prior runs
(`…T164819Z`, `…T164913Z`). Prior rows byte-identical (17 shared base
rows + all 6 meta sections identical to the committed r73 receipt).
No git mutation, no commits — all work left uncommitted for the
integrator.
