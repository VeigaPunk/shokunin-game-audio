# fb-pipewire — FRONTIER pre-measurement: realtime/pipewire transport (pw-cat/pw-play + mpv)

- Seat: scout (LEAF). Brief: `.ufo/waves/shokunin-train-20261101-w10/tasks/audio-frontier-b.txt`.
- Host: `plazir27`, measured 2026-11-01. Scratch: `corpus/live/frontier-pipewire/` (fifos + per-run logs kept there).
- Tools: `pw-cat`/`pw-play` (libpipewire 1.6.8; `pw-play` is a symlink → `pw-cat`), `pactl` (PulseAudio-on-PipeWire protocol 35), `mpv` v0.41.0 (libavformat 63.1.101).
- Corpus members exercised: `corpus/live/round-66/pair_dec_{hcom,act}.wav`, `round-66/pair_lengate_gsrt_25.wav`, `round-68/txw_piperefuse.wav`, `round-69/extsuffix_nomatch.{wav,txw}`, plus scratch-generated `tone4s.wav` (8 kHz s16 mono, 4 s, 64078 B).

## (a) Headless viability — pw-cat NEEDS a daemon; one is live here

Live daemon present: `pgrep` → `pipewire` pid 1905, `pipewire-pulse` pid 2290, `wireplumber` pid 1906. `pactl info` → "Server Name: PulseAudio (on PipeWire 1.6.8)", default spec float32le 2ch 48000Hz; 4 real ALSA sinks + 2 sources, all SUSPENDED (USB audio + HDMI).

Daemon dependency is a hard precondition and it is checked **before the input is opened**:

```
PIPEWIRE_RUNTIME_DIR=$PWD/emptyrt timeout -s KILL 8 pw-cat -p pair_dec_hcom.wav
→ error: pw_context_connect() failed: Host is down        rc=1
PIPEWIRE_RUNTIME_DIR=$PWD/emptyrt pw-cat -p fifo3          → same rc=1 instantly
                                                           (never reaches fifo open)
XDG_RUNTIME_DIR=$PWD/emptyrt pactl info                    → Connection refused
```

So "headless" is fine only if a PipeWire daemon is reachable; no socket → immediate rc=1, no fifo block. pw-cat does not itself spawn a daemon.

Two operational traps found:

- `--target 0` (don't link): stream goes `connecting -> paused` and pw-cat **hangs forever** — an unlinked stream never drains. `pw-cat -p --target 0 pair_dec_hcom.wav` → rc=124 under `timeout`. Do not use for sink-less timing; playback requires an actual link.
- Decode layer is **libsndfile**: all file errors carry the `sndfile:` prefix. Format selection is pure content sniff — a fifo named `fifo1` plays a WAV fine, and `extsuffix_nomatch.txw` (raw bytes) is NOT opened as TXW. **No suffix/name axis.** `-a/--raw` + `--rate/--channels/--format` bypasses sniffing entirely.

## (b) pw-cat over a fifo — writer-attach semantics

| Phase | Observed |
|---|---|
| No writer | Blocks in `open()` (wchan `wait_for_partner`), **zero output**. Survives `timeout`'s SIGTERM >30 s — needs SIGKILL or a writer attach. (`timeout -s KILL` mandatory in harnesses.) |
| Writer attaches, 0 bytes | open() returns, then blocks in read(). Writer closes empty → `sndfile: ... Format not recognised.` rc=1. |
| Writer writes member, closes | sniffs, plays, exits **rc=0 at writer EOF**. Single open — **no re-open-by-name bridge** like sox's act path; no writer-linger needed for pw-cat itself. |
| Instant dump (64 KB / 4 s audio in one `cat`) | wall = 4 s — **consumption is playback-paced**, not read-paced. |
| Half-rate trickle (1600 B chunks, 0.2 s apart; ~8 s to deliver 4 s of audio) | wall = 9 s, rc=0 — streams as bytes arrive, blocks when starved, no underrun abort. |
| `-a` raw mode over fifo | rc=0, ~5 s wall — works identically. |

Verdict-vs-file table (pw-cat, `--target` default → linked playback):

| member | file | fifo | note |
|---|---|---|---|
| `pair_dec_hcom.wav` | rc=0 plays | rc=0 plays | invariant |
| `pair_dec_act.wav` | rc=0 plays | — | (same-class member) |
| `txw_piperefuse.wav` | rc=1 "unimplemented format" | rc=1 identical | invariant |
| `extsuffix_nomatch.wav` / `.txw` | rc=1 "Format not recognised" | rc=1 identical | invariant |
| `pair_lengate_gsrt_25.wav` | rc=1 "No 'data' chunk marker" | — | file arm |

pw-cat verdicts are **transport-invariant** on every member tried — same sndfile predicate, single open, EOF semantics the only difference (fifo EOF = writer close).

## (c) mpv on fifo members — content sniffer, and it FORKS

mpv probes via libavformat regardless of transport (`[lavf] Found 'hcom' at score=100` on both arms). Detection is transport-invariant, but **decode forks on the seekable bit — inverted vs the sox act bridge**: non-seekable *helps*.

| member | `mpv file` | `mpv fifo` (writer: `cat member > fifo`) |
|---|---|---|
| `pair_dec_hcom.wav` | rc=2 — lavf 'hcom' score=100 → "refresh seek to 0" → `Seek failed (Operation not permitted)` → "no audio or video data played" | rc=0 — same detection, "Stream is not seekable" → no refresh seek → hcom decoder consumes stream → `● Audio --aid=1 (hcom 1ch 22050 Hz)` plays |
| `txw_piperefuse.wav` | rc=2 — "No format found … Failed to recognize file format" | rc=2 — identical |
| `extsuffix_nomatch.wav` | rc=2 — "No format found" | rc=2 — identical |

Command shape: `timeout -s KILL 15 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file=<log> <fifo|file>`; mpv exits at writer EOF on a fifo (no hang observed once a writer attaches and closes). rc vocabulary: 0 = played, 2 = load/recognize failure or zero-data playback.

Yes — mpv sniffs content (libavformat probe); the .wav extension did not rescue `extsuffix_nomatch.wav` and did not prevent the hcom detection on `pair_dec_hcom.wav`.

## Net assessment for wave-11 dispatch

- **Viable surface.** Live daemon present with real sinks; pw-cat streams fifos correctly, paces at playback rate, exits cleanly on writer EOF, and needs no linger protocol. The act-style re-open hazard does not exist (single open).
- pw-cat adds a **content-only sndfile detector + realtime drain**; its fifo hazards are operational (open-block, SIGTERM-immunity, unlinked-stream hang) rather than verdict forks.
- mpv forks on `{seekable}` for the hcom member (file rc=2 / fifo rc=0) — a live playback-consumer fork candidate distinct from the sox ffmpeg-bridge mechanism (lavf refresh-seek EPERM, not name re-resolution).

## Unresolved / caveats

- mpv's file-arm `Seek failed (Operation not permitted)` on a seekable file: mechanism inferred from log order (lavf hcom demuxer likely declines the seek); not straced.
- pw-cat with a daemon but **zero sinks** untested (only `--target 0` hang observed); a dispatch on a sink-less box needs a virtual sink (e.g. `pw-cli`/null-sink module).
- Did not test `pw-record`, MIDI modes, multiple writers, or writer-dies-mid-stream (predicted: reader sees EOF → normal rc=0 of partial playback).
- Two stale `timeout … strace sox` processes (pids 1965371, 1970028, sigsuspend) from earlier rounds were left untouched — not mine to kill.
