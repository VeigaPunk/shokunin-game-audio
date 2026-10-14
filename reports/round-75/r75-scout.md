# r75-scout (audio) — pre-measurement of the declared surface: paplay / aplay / ffplay

Seat **scout** (leaf, report-only). Wave `shokunin-train-20261101-w14`, lane audio,
repo `/home/vgpnk/Projects/shokunin/audio-shokunin`, HEAD **`6f905c3`** (unchanged
all session). Host `plazir27`, window 2026-10-14 **16:24Z–16:46Z** (UTC; local TZ
UTC−3, `ls` mtimes are local). Write scope: this report +
`corpus/live/r75-scout/` only. No git mutation, no subagents, no fixture edit
(`corpus/fixtures/measure_audio.py` untouched; the pre-existing dirty
`__pycache__/measure_audio.cpython-314.pyc` was not touched). **No receipt mode
was run and no receipt was written by this seat** — every artifact below is
scout scratch.

Toolchain (measured this session, `corpus/live/r75-scout/toolchain-gates.txt`):
`paplay`→`/usr/bin/pacat` symlink, **pacat 17.0-98-gb096 / libpulse 17.0.0**,
links `libsndfile.so.1`; **libsndfile 1.2.2-4** (`libsndfile.so.1.0.37`);
`aplay` **alsa-utils 1.2.16**, links `libasound.so.2` only (**no** libsndfile,
**no** libpulse — it has its own RIFF parser); `ffplay` **n9.0.1** (lavf
63.1.101) + **sdl2-compat 2.32.72-1** (`libSDL2-2.0.so.0.3200.72`), links
libsndfile/libpulse/libpipewire as *transitive* SDL deps only. Session:
`DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-1`, `XDG_RUNTIME_DIR=/run/user/1000`,
`pipewire`/`wireplumber`/`pipewire-pulse` live (pids 1203634/1203636/1203790,
untouched), Pulse protocol 35, default sink
`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.2`.

**LSP device: unavailable this session** — `mcp_list_servers` → only `rea`
(Ghidra; no definition/references/hover). No source-trace was possible; every
mechanism claim below is labelled **inference** and rests on process-level
measurement with receipts, never on grep-as-proof.

## Headline — six results that change what the author should build

1. **The `dec_hcom` member is not a member for paplay/aplay.** `pair_dec_act.wav`
   and `pair_dec_hcom.wav` are **byte-identical RIFF/WAVE files except one byte**
   (`cmp -l` → 1 differing byte, offset 69; both 600 B, fmt 16, 8 kHz mono s16).
   lavf re-detects the second as `hcom` by **content probe** (`probe_score=100`
   vs `99` for wav); `sndfile-info` and `aplay` both read it as plain WAV. The
   member axis therefore exists **only for lavf consumers** (mpv, ffplay).
2. **The `.snd` name axis is libsndfile's, not pw-cat's — and paplay does not
   inherit it.** Identical 512 B no-magic bytes (sha `f073e70a…`): bare
   `sndfile-info` **accepts** `.snd`/`.au` (`Format 0x00040010` = RAW|ULAW,
   8 kHz mono, 512 frames, 0.064 s) and **rejects** `.wav`/`.bin`; `pw-cat -p`
   reproduces that table exactly; **`paplay` rejects all four** (`rc=1 Failed to
   open audio file.`, 1–2 ms). Same library, same bytes, same name, different
   verdict ⇒ the difference is in the client's open call (inference: pacat opens
   by fd, so libsndfile's path/extension fallback never fires).
3. **ffplay does not share mpv's refresh-seek fork.** On `dec_hcom` file:
   ffplay `rc=0`, `600 bytes read, 0 seeks`, `find_stream_info` consumed the
   whole stream (`frames:1`); mpv on the same file is `rc=2` (r73/r74 receipts).
   ffplay issues no seek at all on the no-seek demuxers.
4. **ffplay's `rc=0` is a false positive, and `-ss` on a non-seekable transport
   silently aborts playback.** 4 s stem, SDL dummy: file + `-ss 2` → `rc=0`,
   wall 2.103 s, last status position **3.91** (seek honoured); stdin pipe or
   named fifo + `-ss 2` → `rc=0`, wall **0.159 s**, **0 status samples**
   (`fd:: could not seek to position 2.000`). A/B on identical bytes/transport:
   no `-ss` → `rc=0`, 4.03 s, 128 status samples, last **3.87**.
   **rc collapses the fork; the status-line position is the witness.**
5. **aplay is name-blind, content-first, and rc-blind.** All 45 file×name legs
   `rc=0` except empty-fifo; the witness is the stderr line `Playing WAVE …` vs
   `Playing raw data … Unsigned 8 bit, Rate 8000 Hz`. `-q` erases that witness
   (rc0, 0 B stderr) — never run aplay with `-q` when the line is the evidence.
6. **The carried guard "fifo-open blocks are SIGTERM-immune" is too strong.**
   Measured per consumer: `paplay` dies on the **first** TERM inside the open
   block (−15); `aplay` is immune to **exactly one** TERM (its handler restores
   SIG_DFL, so TERM₂ kills it, −15); `ffplay` never blocks in open at all (no
   fifo fd in its table; TERM₁ → `rc=123`). The scratch's `aplay …
   sigterm_immune: true, exit_code: -9` was a **one-TERM artifact**.

## 1. Recovery — what was reused, what was discarded

Reused as sound (prior generation died ~16:10Z): `toolchain-gates.txt`,
`members.txt` (member shas, all re-verified below), `legs/*` probe outputs,
`fifo_cells.py` + `fifo-cells.json` (writerless/writer legs, paplay name cells,
ffplay `-ss` pair), `probe-{paplay,aplay,ffplay}-*.txt`.

**Discarded as unsound** (do not cite):

| artifact | why |
|---|---|
| `legs/ffplay-default.{stdout,stderr}` `rc=126` | harness quoting bug — stderr is `bash: line 1: …/pair_dec_act.wav: Permission denied`, i.e. bash tried to exec the member; ffplay never ran |
| `probe-gates-2.txt` | empty file |
| scratch `aplay` nowriter cell (`sigterm_immune: true`, `-9`) | one-TERM ladder; a second TERM kills it (−15) — see §6 |
| my own `gates` batch v1 (`aplay -t 0.05`) | `-t` is aplay's **`--file-type`** → `unrecognized file format 0.05`; re-run without it (§2). Same class of bug: `-d 0.05` / `-d 0.05s` → `invalid duration argument` (`-d 2` is accepted) |

New this seat: `scout_fill.py` (sha `a2d222db81b52ae9`), 9 receipts,
**187 legs** under `corpus/live/r75-scout/runs/` — all bounded, all fifo arms
group-killed (`timeout -s KILL` / `killpg`), each leg carrying `rc`, wall,
`timeout_hit` and the consumer's own witness text.

## 2. Viability gates (measured) and the blockages, exactly

| consumer | requirement | verdict on this host | witness |
|---|---|---|---|
| `paplay` | a Pulse server | **viable** — protocol 35 over `pipewire-pulse` | `PULSE_SERVER=unix:/nonexistent` → `rc=1` in 1 ms, `Connection failure: Connection refused` / `pa_context_connect() failed` |
| `aplay` | an ALSA device | **viable only via null / pipewire / sysdefault / plughw** | `aplay -D null` `rc=0`; `-D default` `rc=0` (0.205 s); `-D pipewire` `rc=0` (0.211 s); `-D sysdefault` `rc=0`; `-D plughw:0,0` `rc=0` (0.266 s) |
| | direct `hw:` | **blocked, two distinct causes** | `hw:0,0`,`hw:1,3`,`hw:2,3` → `rc=1 set_params:1404: Channels count non available` (mono 8 k / 48 k mono unsupported); `hw:0,3` → `rc=1 main:850: audio open error: Device or resource busy` (pipewire owns the SPDIF pcm) |
| | real-time pacing | works | `-D pipewire` on the 4 s stem → 4.063 s wall; `plughw:0,0` → 4.14 s |
| `ffplay` | a valid SDL audio driver | **viable** — `SDL_AUDIODRIVER=dummy` / `pulse` / `alsa` / `pipewire` → `rc=0` | `bogus`, `default`, `pipewire-pulse` → `rc=1 Could not initialize SDL - Audio target 'X' not available` (SDL driver names, not Pulse names; `default` is **not** a driver) |
| | headless determinism | `-nodisp` + explicit driver | session has `DISPLAY=:0`; dummy driver paces at real time (4 s stem → 4.027 s), so wall time is a usable playback witness |

`sndfile-info` needs no daemon and no device — it is the cleanest libsndfile
witness available on this host. **Its rc is always 0** (a nonexistent path
returns 0) — text only, never rc.

## 3. The name axis, resolved (identical bytes, three clients, three transports)

Bytes: `corpus/live/round-69/extsuffix_nomatch.snd` (512 B, no magic, sha
`f073e70a…`). Positive control: `pair_dec_act.wav` (RIFF). Receipt
`runs/scout-fill-name-lattice.json` (52 legs), `runs/scout-fill-fifo-close.json`
(26 legs, writer writes then **closes**).

| name | `sndfile-info` (path open) | `pw-cat -p` | `paplay --verbose` |
|---|---|---|---|
| `.snd` | **accept** — `Format 0x00040010`, 8000 Hz, 512 frames, 0.064 s | **rc=0** | rc=1 `Failed to open audio file.` |
| `.au` | **accept** (same format word) | **rc=0** | rc=1 |
| `.wav` | `Format not recognised.` | rc=1 | rc=1 |
| `.bin` | `Format not recognised.` | rc=1 | rc=1 |
| RIFF content, any of `.wav/.snd/.bin/.au/.raw` | accept (WAVE) | rc=0 | rc=0 |
| empty, any name | not recognised | rc=1 | rc=1 |

- **Transport is not the variable**: file, named fifo (closing writer) and
  stdin/`/dev/stdin` give the same verdict per (client, name) — the writer-hold
  class is a separate confound (§6). `sndfile-info` on a fifo with EOF also
  accepts `.snd`, so the fallback does not need a seekable stream.
- **`paplay -` is not stdin**: it returns `rc=1 open(): No such file or
  directory` (it tries to open a file literally named `-`); use `/dev/stdin`.
- **Answer to the brief's question (a)**: paplay's libsndfile path does **not**
  inherit the `.snd` fork — it rejects `.snd`, `.au`, `.wav`, `.bin` alike on
  identical bytes, while pw-cat accepts `.snd`/`.au`. The r73/r74 phrasing
  "pw-cat × `.snd` = a separate NAME-axis fork" is **imprecise**: the axis is
  libsndfile's extension-driven RAW fallback (witness: bare `sndfile-info`,
  no client involved), and the *client* decides whether it is reachable.
  Inference (medium-high): `pw-cat` passes the path (`sf_open`), `pacat` opens
  by fd (`sf_open_fd`), so the extension is unavailable to it. Falsifiable
  prediction: any libsndfile client given a *path* inherits the `.snd`/`.au`
  fallback; one given only an fd does not.
- `paplay --raw` on the same bytes/fifo name → `rc=0` (scratch
  `fifo-cells.json`), i.e. paplay can play raw when told; it simply has no
  auto-raw fallback.

## 4. ffplay — no refresh-seek fork, but a `-ss` transport fork (rc-identical)

Receipts `runs/scout-fill-ffplay.json`, `runs/scout-fill-ffplay-position.json`,
`runs/scout-fill-fifo-seek.json`, plus scratch
`legs/ffplay-dummy-hcom-debug.stderr` (full debug log).

| cell | rc | bytes read / seeks | find_stream_info | witness |
|---|---|---|---|---|
| `dec_hcom` **file**, `-loglevel debug` | 0 | 600 / **0** | `pos:600 read:600 seeks:0 nb_streams:1 frames:1` | `Input #0, hcom` — whole stream consumed, **no seek** |
| `dec_hcom` fifo (closing writer) | 0 | 600 / 0 | — | `Input #0, hcom, from '…/leg.wav'` |
| `dec_act` file / fifo / stdin | 0 | 600 / 0 | — | `Input #0, wav` |
| mpv, same `dec_hcom` file (r73/r74) | **2** | — | refresh seek → flush | *not re-measured this seat* |

**ffplay does not fork on the no-seek members** — it has no refresh-seek
architecture and issues zero seeks. The mpv fork stays mpv-local.

The `-ss` cell (4 s `stem_sections.wav`, `SDL_AUDIODRIVER=dummy`):

| transport | no `-ss` | `-ss 2` |
|---|---|---|
| seekable file | rc=0, 4.029 s, 8 status samples, last pos **3.87**, 2 seeks | rc=0, **2.103 s**, last pos **3.91**, 2 seeks — seek honoured |
| stdin pipe (`-i -`) | rc=0, **4.03 s**, **128** samples, last **3.87** | rc=0, **0.158 s**, **0 samples**, `fd:: could not seek to position 2.000` |
| named fifo (closing writer) | rc=0, 4.028 s, 8 samples, last **3.90** | rc=0, **0.159 s**, **0 samples**, `could not seek` |

`-ss 0` behaves like `-ss 2` on the non-seekable arms (0.158 s, 0 samples) — the
fork is **not** about the seek target. Measured rc semantics for ffplay:
**0 = "ran to the end" (possibly without playing anything)**, 1 = SDL/audio-open
failure, **123 = SIGTERM received** (ffplay's handler calls `exit(123)`), and
`rc=0` also on garbage and on `/dev/null` (0.029 s). The only playback witnesses
are the `Input #0, <fmt>` line and the status-line position (`nan` vs `N.NN`),
plus `Statistics: N bytes read, M seeks` under `-loglevel debug`.

## 5. aplay — name-blind, content-first, rc-blind

Receipts `runs/scout-fill-aplay.json` (41 legs), `runs/scout-fill-devices.json`
(14), `runs/scout-fill-fifo-close.json`.

- 35 file×name legs (7 member variants {act, hcom, 64-byte truncation, 512 B no
  magic, the same 512 B under a second tag, 1 byte, empty} × 5 names
  {`.wav .snd .bin .au .raw`}): **every file/stdin leg `rc=0`**; only the empty
  *fifo* is `rc=1`. The name never changes the verdict.
- Witness line: unrecognized content → `Playing raw data 'x' : Unsigned 8 bit,
  Rate 8000 Hz, Mono` (a raw fallback with a **different** default than the WAV
  path, which is `Signed 16 bit`); RIFF content (incl. the 64-byte truncation —
  the header is complete in the first 44 bytes) → `Playing WAVE 'x' : Signed 16
  bit Little Endian, Rate 8000 Hz, Mono`.
- `-q` erases it: `aplay -D null -q -` with garbage → `rc=0`, **0 B stderr**.
- Transport-local edges: empty **file** → raw fallback `rc=0`; empty **fifo**
  (writer opens, writes 0 B, closes) → `rc=1 aplay: read_header:2973: read
  error`; no-argument with empty stdin → same `rc=1`.
- `aplay -` reads stdin (`Playing … 'stdin'`).
- `dec_hcom` under aplay is a **WAV** (its own RIFF parser), consistent with §Headline-1.

## 6. Hang classes and the corrected kill guard (TERM₁/TERM₂ ladder + fd table)

Receipt `runs/scout-fill-hangs.json` (9 legs; `/proc/<pid>/{wchan,stat,fd}`
sampled 1.2 s after spawn, then TERM, poll, TERM, poll, KILL).

| consumer | writerless (block in `open`) | silent writer (open ok, no data) | writer-hold (member written, **no EOF**) |
|---|---|---|---|
| `paplay` | `wchan=wait_for_partner`, **fifo fd absent**, TERM₁ → **−15** | `wchan=anon_pipe_read`, fd present, TERM₁ → −15 | fd present, **TERM₁ alive, TERM₂ alive** → −9 |
| `aplay -D null` | `wchan=wait_for_partner`, **fifo fd absent**, TERM₁ **alive**, TERM₂ → **−15** | `wchan=anon_pipe_read`, fd present, TERM₁ alive, TERM₂ → −15 | **exits by itself, rc=0** (honours the declared WAV length; no EOF needed) |
| `ffplay` | `wchan=hrtimer_nanosleep`, **fifo fd absent**, TERM₁ → **rc=123** | `wchan=hrtimer_nanosleep`, fd present, TERM₁ → 123 | TERM₁ → 123 |

Corrections to the carried guards:
- **"fifo-open blocks are SIGTERM-immune → `timeout -s KILL`" is consumer-local
  and, for aplay, one-shot.** paplay dies on TERM₁ in the open block; aplay is
  immune to exactly one TERM (its handler prints `Aborted by signal
  Terminated...` and restores SIG_DFL, so TERM₂ kills it); ffplay never blocks in
  open. Keep the KILL backstop, but classify per consumer and send **≥2 TERMs**
  before recording "immune" — a one-TERM ladder produced the scratch's false
  `sigterm_immune: true` row.
- **ffplay's main-thread `wchan` is not a block witness** (its reader runs off
  the main thread; the main thread sleeps in the SDL loop). Use the fd table:
  fifo fd present ⇒ the open succeeded.
- **The writer-hold class is a harness-level confound, not a consumer property.**
  A writer that writes a complete member and keeps the fd open converts paplay
  and ffplay into blocks (my `with_writer("data")` → 8–20 s timeouts) while the
  same bytes with a closing writer are `rc=0` in ~0.13 s (the r74 shape).
  Receipts must state the writer's EOF policy; standardize on write-then-close.

## 7. Pre-measured receipt surface for the author (fields, not rc)

| consumer | required witness | positive | negative |
|---|---|---|---|
| `paplay` | `--verbose` is **mandatory** — the default success surface is 0 B stdout and 0 B stderr | `Opening a playback stream with sample specification 's16le 1ch 8000Hz'` + `Playback stream drained.` + `Connected to device …` | `Failed to open audio file.` (decode refusal, 1–2 ms); `Connection refused` (daemon gate) |
| `aplay` | the `Playing WAVE|raw data` line (**never `-q`**) | `Playing WAVE '…' : Signed 16 bit …` | `Playing raw data … Unsigned 8 bit` (silent fallback), `read_header: read error`, `set_params:1404`, `audio open error: Device or resource busy` |
| `ffplay` | `Input #0, <fmt>, from …` + status-line position + `Statistics: N bytes read, M seeks` | position advances (`3.87 M-A:`) | `nan` / 0 status samples (no playback), `Invalid data found when processing input`, `Could not initialize SDL - Audio target 'X' not available` |
| all three | — | — | **rc alone collapses every cell**: aplay rc0 on garbage, ffplay rc0 on garbage/empty/aborted-`-ss`, paplay rc1 for both "wrong bytes" and "no daemon" |

Reusable harness constants: `timeout -s KILL` on every fifo arm; SDL dummy paces
at real time (wall is a witness); `aplay -D null` consumes instantly (no pacing,
ideal for matrix legs); `sndfile-info` rc is meaningless (text only).

## 8. Carried guards — status after this seat

| guard | status |
|---|---|
| reorder topology = fd1-OWNER's buffering mode | not exercised here (no reorder cell in this arm) |
| bpy ignores `PYTHONUNBUFFERED` | not exercised (no Python consumer in this arm) |
| `io.DEFAULT_BUFFER_SIZE=131072` build-specific | not exercised |
| wire order + write order both needed as witness | **confirmed in spirit** — every cell above needed a second witness (spec line / Playing line / position / seeks) beside rc |
| rc alone is never a verdict | **confirmed ×3** (aplay rc0 on garbage, ffplay rc0 on garbage and on aborted playback, `sndfile-info` rc0 on a nonexistent path) |
| fifo-open blocks are SIGTERM-immune → `timeout -s KILL` | **corrected**: consumer-local; aplay's immunity is one-shot; ffplay does not block in open; KILL backstop still required |
| lavf wound partition gated on `AVFMT_NOGENSEARCH` | not exercised; ffplay adds a *different* lavf-client polarity (§4) |
| consumer forks are member-local | **confirmed** — the `.snd` name axis is libsndfile-local, the `-ss` abort is transport-local, the writer-hold block is harness-local |

## 9. Confidence and remaining unknowns

**High confidence** (process-level, reproducible, witnesses retained): the
toolchain/gate table; the pair fixture being a one-byte RIFF pair with a lavf
probe collision; the name lattice (52+26 legs, three clients, three transports);
aplay's name-blindness and raw fallback; ffplay's 0-seek no-fork on
`dec_hcom`/`dec_act`; the `-ss` transport fork with rc identical; the TERM
ladder table and the fd-table block-location partition.

**Medium-high**: the libsndfile-fallback attribution (`sndfile-info` accepts
`.snd`/`.au`, rejects `.wav`/`.bin`; `Format 0x00040010` = RAW|ULAW) — the
measured table is certain, the "path-open vs fd-open" explanation is inference
(no libsndfile source on the host, no LSP device).

**Unresolved / not measured**:
- The exact libsndfile rule that admits `.snd`/`.au` but not `.wav`/`.bin`
  (extension table vs AU-default codec) — not source-traced.
- Why `paplay` survives both TERMs in the writer-hold class while it dies on
  TERM₁ in the open and silent classes (signal-handler installation timing) —
  observed, mechanism unresolved.
- aplay's `-d` parser rejects `0.05` and `0.05s` while accepting `2` on 1.2.16
  (recorded as a harness note, not chased).
- mpv's fork cells are quoted from r73/r74 receipts, not re-measured this seat.
- No `--cache`/`--ao=pcm` byte-witness arms were extended to the new consumers;
  ffplay has no cumulative decoded-byte counter, so its decode witness is the
  status position + wall pacing (SDL dummy), not a byte count.
- Only one long member (4 s, 48 kHz mono) was used for the seek/pacing cells;
  the `-ss` fork is unprobed on stereo/other rates.
- All claims bounded to this host and these builds: libsndfile 1.2.2-4,
  alsa-utils 1.2.16, pacat 17.0-98-gb096, ffmpeg n9.0.1, sdl2-compat 2.32.72-1,
  PipeWire 1.6.8, kernel 116-device ALSA layout.

## 10. Evidence index (all under `corpus/live/r75-scout/`)

| artifact | sha256 (16) | legs |
|---|---|---|
| `scout_fill.py` | `a2d222db81b52ae9` | harness (all new batches) |
| `runs/scout-fill-name-lattice.json` | `c787d101c90c8325` | 52 |
| `runs/scout-fill-aplay.json` | `f2a7bc3539b7f0d9` | 41 |
| `runs/scout-fill-fifo-close.json` | `fef041bba89382ee` | 26 |
| `runs/scout-fill-gates.json` | `10c4afbc4739520a` | 25 |
| `runs/scout-fill-devices.json` | `0202ca8625c967fb` | 14 |
| `runs/scout-fill-ffplay.json` | `eb3b059570181f0a` | 12 |
| `runs/scout-fill-hangs.json` | `0edc8e7313fb69d4` | 9 |
| `runs/scout-fill-ffplay-position.json` | `7611d905db256e2f` | 6 |
| `runs/scout-fill-fifo-seek.json` | `3cca75c53f48b26e` | 2 |
| `fifo_cells.py` (prior gen, reused) | `dc97271598b7d68b` | 4+13 |
| `fifo-cells.json` (prior gen, reused) | `a978b55c07d89821` | — |
| `toolchain-gates.txt` | `edf6ac7fadcb8c7a` | gates |
| `members.txt` | `16a9ec78cea4e9a8` | member shas |
| `legs/ffplay-dummy-hcom-debug.stderr` | (file) | the 0-seek witness |

Reproduce (from the repo root; ~2.5 min total, all bounded):

```sh
python3 corpus/live/r75-scout/scout_fill.py names        # 52 legs, ~42 s
python3 corpus/live/r75-scout/scout_fill.py aplay        # 41 legs, ~8 s
python3 corpus/live/r75-scout/scout_fill.py gates        # 25 legs, ~13 s
python3 corpus/live/r75-scout/scout_fill.py devices      # 14 legs, ~9 s
python3 corpus/live/r75-scout/scout_fill.py hangs        #  9 legs, ~20 s
python3 corpus/live/r75-scout/scout_fill.py ffplay       # 12 legs, ~67 s
python3 corpus/live/r75-scout/scout_fill.py fifo-close   # 26 legs, ~35 s
python3 corpus/live/r75-scout/scout_fill.py ffplay-pos   #  6 legs, ~15 s
```

**Seat stop.** Findings above; no edits outside `corpus/live/r75-scout/` + this
report; no git mutation; no receipt written; sibling scratch untouched.
