# r75 reviewer — independent pre-landing reconnaissance (seat scratch)

Host plazir27, measured 2026-10-14 ~16:00–16:10 UTC. HEAD `6f905c3` (pre-landing).
All commands run from `~/Projects/shokunin/audio-shokunin`. Tools: paplay
(pacat 17.0-98-gb096), aplay 1.2.16 (ALSA card 0 USB Audio present),
ffplay n9.0.1, pipewire-pulse live (pactl proto 35, default sink present),
SDL_AUDIODRIVER=dummy for ffplay determinism.

## Consumer surfaces (independently measured, before the author arm landed)

### paplay (PulseAudio client; links libsndfile.so.1)
- `paplay <file>` dec_act -> rc0. dec_hcom -> rc0: libsndfile reads the
  RIFF/WAVE header and decodes the hcom payload as s16le 8 kHz PCM
  (`--verbose`: "Using sample spec 's16le 1ch 8000Hz'"), i.e. paplay does
  NOT see the hcom demuxer — its decode layer is WAV.
- Invalid bytes (r69 identical-byte family): rc1 "Failed to open audio
  file." on ALL FIVE names {.wav .bin .txw .f32 .snd} — **no .snd name
  axis** (pw-cat replay on same bytes: .snd rc0 / .wav rc1, axis intact).
  Mechanism consistent with fd-open: pacat opens the path itself and hands
  the fd to libsndfile (sf_open_fd), so the extension fallback in
  libsndfile's sndr CHECK row never sees a name. Named-fifo arm with the
  .snd bytes also rc1 (axis collapsed on the named arm too).
- stdin convention: NO file argument reads stdin (`paplay < f` rc0);
  `paplay -` treats "-" as a filename -> "open(): No such file or
  directory" rc1. `paplay /dev/stdin` works (rc0 on dec_act).
- Writerless fifo: blocked, wchan `wait_for_partner`, **TERM-TERMINABLE**
  (SIGTERM -> rc -15 in 0.001 s) — distinct from pw-cat's measured
  SIGTERM-immune open block.
- Daemon gate: pulse severed (empty PIPEWIRE_RUNTIME_DIR + PULSE_SERVER
  pointing into it) on a valid file -> instant rc1 in 0.002 s
  ("Connection failure: Connection refused / pa_context_connect()
  failed"). GATE PRECEDENCE: input-open FIRST (same severed env + a
  writerless fifo -> blocked the full 5 s window) — opposite of pw-cat's
  daemon-connect-first precedence (r73).

### aplay (ALSA direct)
- Real wav: "Playing WAVE '<name>' : Signed 16 bit Little Endian, Rate
  8000 Hz, Mono", rc0.
- Unrecognized bytes: **raw fallback** "Playing raw data '<name>' :
  Unsigned 8 bit, Rate 8000 Hz, Mono", rc0 — on every name {.wav .bin
  .snd}. rc is NOT a verdict for aplay; the surface is the stderr line.
- stdin: `aplay -` works ("Playing WAVE 'stdin'").
- Writerless fifo: blocked, wchan `wait_for_partner`, **SIGTERM-IMMUNE**
  (survived 1.0 s), killpg SIGKILL -> rc -9 (pw-cat class).
- Device gate: `-D hw:99` -> rc1 "Cannot get card index for 99 / audio
  open error: Invalid argument"; `-D nosuchdev` -> rc1 "Unknown PCM
  nosuchdev / audio open error: No such file or directory" (instant,
  device open precedes input read).
- `aplay -l`: card 0 USB Audio, devices 0–3 present -> viable (not
  blocked).

### ffplay (SDL + lavf)
- dec_hcom: detected as hcom demuxer (`Input #0, hcom`), **rc0 on ALL
  three transports** {file, stdin (`from 'fd:'`), fifo}; debug log shows
  `seeks:0` / "0 seeks" — **no refresh-seek fork** (mpv: file arm rc2
  EPERM). The brief's fork question measures as AVOIDED by ffplay.
- Invalid bytes (r69 family): rc0 + "Invalid data found when processing
  input" -> rc is NOT a verdict; text surface.
- Writerless fifo: main thread `hrtimer_nanosleep` (SDL event loop),
  reader thread `wait_for_partner`; SIGTERM -> **rc 123 in 0.003 s**
  (SDL TERM handler; TERM-terminable, distinct from paplay/aplay).
- SDL driver gate: SDL_AUDIODRIVER=nosuchdriver -> instant rc1 "Could
  not initialize SDL - Audio target 'nosuchdriver' not available".
- TRAP pinned: `-an -vn` on an audio-only member -> "Failed to open file
  ... or configure filtergraph" AND THEN HANGS (rc 137 under `timeout -s
  KILL 15`). Correct headless flag set is `-nodisp [-vn]` with audio
  enabled.

## Poll state
- HEAD stays `6f905c3`; `reports/round-75/` absent; no `corpus/live/r75-author/`;
  no r75 fixture refs / receipts (scribe watch log corroborates).
- Awaiting author commit; replay plan = scratch tree at committed revision,
  `--probe-consumers2-r75` + prior-row probes (consumers-r73,
  lavfsweep-r74), receipt byte-compare vs committed.
