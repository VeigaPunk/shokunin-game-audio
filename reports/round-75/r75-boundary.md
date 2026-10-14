# R75 BOUNDARY (audio) — edge cells, negative controls, hang/kill semantics

Seat: **boundary** (leaf, report-only; no subagents, no git mutation). Wave
`shokunin-train-20261101-w14`. Host `plazir27` (`Linux 7.2.3-arch1-3`, local TZ
= UTC−3; report written **16:34Z** = 13:34 local). Repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`, HEAD **`6f905c3`** (unchanged by
this seat). Fixture `corpus/fixtures/measure_audio.py` sha256
**`317c0b486e103ac3eebc258e0c22c2cc623d3a3813f3ceae2c3d71b25f078f2e`** — no
`r75`/`paplay`/`aplay`/`ffplay` leg exists yet (author arm still absent), so
every claim below is *pre-landing* boundary evidence for that parser.

Consumers under test, verbatim versions:
`paplay` = `pacat 17.0-98-gb096`, libpulse 17.0.0 · `aplay` = 1.2.16 (alsa-utils)
· `ffplay` = `n9.0.1` (lavf 63.1.101, SDL) · contrast legs `pw-cat` (libpipewire
1.6.8) and `mpv v0.41.0`. Live daemon: `pactl info` → *PulseAudio (on PipeWire
1.6.8)*, server `/run/user/1000/pulse/native`, default sink
`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.2` (RUNNING), 4 sinks.

## 0. Scope, protocol, recovery provenance

**Assigned:** "Edge members/inputs for the paplay/aplay/ffplay consumers,
missing-daemon/device/backend blockages, kill-escalation classes, load replays.
`timeout -s KILL` fifo-adjacent."

**Recovery.** The prior generation's scratch (`edge/`, `logs/{matrix,fork,name,
kill,gates,pacing}`, `probe_boundary_r75.py`, `runs/20261014T160930Z-boundary-r75/`)
was verified and **reused as harness**, not trusted as receipts: its run dir
holds only 3 files (no `measurements.json`/`verdicts.json`/`env.txt`) — the dead
process flushed per-cell logs but never completed `write_receipts`
(`probe_boundary_r75.py:636-657`). I re-ran the full harness
(`build matrix fork name kill kill_replay load gates pacing`, 152 s, run dir
`runs/20261014T162937Z-boundary-r75/`), which produced the complete receipt set,
and **the two generations agree byte-for-byte**:

| receipt | sha256 | generations |
|---|---|---|
| `matrix-rep1-verdicts.json` | `a2e411dda1763a41e251f1120fe620d219f6e521e7cc80d82cad6c18910af8bd` | 4 files (rep1+rep2 × 2 generations), all identical |
| `matrix-rep2-verdicts.json` | same as rep1 | (intra-run replay identity) |
| `kill-rep1-verdicts.json` | `bd4f62db245bccc2e18ec13615c84425eb70ba5f20c6611e401afd216faf8344` | 3 files (prior rep1 + my rep1 + my rep2), all identical |
| `kill-rep2-verdicts.json` | same as rep1 | (intra-run replay identity) |

That is the strongest determinism statement available here: **252 matrix cells
(21 members × 2 transports × 3 consumers × 2 reps) and 18 kill cells reproduce
byte-identically across reps and across two process generations 20 min apart**
(126 + 18 cells per pass).

**Write scope:** this report + `corpus/live/r75-boundary/` only. New artifacts
this seat added: `probe_boundary_r75b.py` (sha256
`def3e7179702874cdbacfd147d838c7e916537b153975c84243824d22eb7d5a7`),
`edge2/` (manifest `fa64992fed41137f15b69a7a626b20a75d31e274eaa8b30599a0a92625afdb6e`),
`logs/r75b/{edge2,iso,devices}/`, `runs/20261014T163317Z-boundary-r75b/`, and
`logs/full-run-w14b.out` (my full-harness run log). No tracked file touched; no
git command beyond `rev-parse`/`status`.

**Wrapper discipline (carried guard, re-confirmed).** Every fifo-adjacent arm —
matrix fifo, all kill cells, all edge cells, all load cells — ran under
`timeout -s KILL <n>` (`probe_boundary_r75.py:299-301`, `:435-445`;
`probe_boundary_r75b.py:78-105`). Reason measured here, not assumed: `aplay`
blocks on the fifo open and **survives SIGTERM** (§6, F6.1).

**rc vocabulary (recorded verbatim; see §6 for why it must never be the
verdict):** `124` = inner `timeout -s TERM` expiry where the consumer *did* die
of TERM; `-9` = either the harness's `killpg` (`harness_kill: true`, wall = the
harness grace) **or** the inner `timeout -s KILL` wrapper dying inside its own
signalled group (wall ≈ the requested seconds) — **`137` was never observed**;
`0/1` = the consumer's own rc.

## 1. Viability gates (exact enumerations)

| gate | command | result (verbatim) |
|---|---|---|
| pulse daemon | `pactl info` | rc 0; `Server String: /run/user/1000/pulse/native`, `Server Name: PulseAudio (on PipeWire 1.6.8)`, `Server Version: 15.0.0` → **paplay not blocked** |
| sinks | `pactl list short sinks` | rc 0; 4 sinks, default `.HiFi__SPDIF__sink.2` RUNNING |
| ALSA devices | `aplay -l` | rc 0; **12 device lines**: card 0 `USB Audio` dev 0-3, card 1 `HDA NVidia` dev 3/7/8/9, card 2 `HD-Audio Generic` dev 3/7/8/9. **card 0 device 3 = `Subdevices: 0/1`** (already held) → aplay arm is **not** blocked by absence |
| ALSA names | `aplay -L` | rc 0; `null`, `sysdefault`, `pipewire`, `default`, … → `-D null` exists, so the deterministic lattice is legitimate on this host |
| aplay missing device | `aplay -D nosuchdevice dec_act` | rc 1, `ALSA lib pcm.c:2722 … [error.pcm] Unknown PCM nosuchdevice` + `aplay: main:850: audio open error: No such file or directory` |
| aplay busy device | `aplay -D hw:0,3 dec_act` | rc 1, `aplay: main:850: audio open error: Device or resource busy` (**new negative control**, §5) |
| SDL driver | `ffplay … SDL_AUDIODRIVER=nosuchdriver` | rc 1, `Could not initialize SDL - Audio target 'nosuchdriver' not available` + `(Did you set the DISPLAY variable?)` |
| SDL default | `ffplay … SDL_AUDIODRIVER=""` | rc 0, wav detected, device-coupled (0.094 s wall on the 0.03 s member) |

## 2. Canonical member × transport matrix (126 cells × 2 reps)

`probe_boundary_r75.py:290-316`. 13 canonical members (`round-66/68/69`) + 8
edge members × {`paplay`,`aplay -D null`,`ffplay -nodisp -autoexit -vn`} ×
{file, fifo-with-full-writer}, `timeout -s KILL 20`. Per-consumer verdict
vocabulary on the identical 42-cell slice:

| consumer | rc distribution | witness classes |
|---|---|---|
| `paplay` | **0 ×16, 1 ×26** | rc 0 ⇒ **0 B stderr, 0 B stdout — no positive witness at all**; rc 1 ⇒ exactly one 27-byte line `Failed to open audio file.` (no `sndfile:` prefix, no path) |
| `aplay` | 0 ×35, 1 ×7 | rc 0 splits **`wav` ×16 / `raw` ×19**; the `raw` class is *silent garbage playback* (`Playing raw data '<input>' : Unsigned 8 bit, Rate 8000 Hz, Mono`) — rc 0 and mode `raw` is the "did not decode, did play something" state |
| `ffplay` | **0 ×42 (no other rc exists on this lattice)** | rc 0 splits `wav` ×10 / `hcom` ×4 / **no-detected-format ×28**; 28 of the 42 carry an `Invalid data found when processing input` error line **at rc 0** |

**Transport divergence is almost nil: exactly 4 of 63 member pairs differ, all
`aplay`.** Three are message-only (same rc 1, different aplay call site — file
arm `aplay: test_wavefile_read:994: read error (called from line 1055/1067)`,
fifo arm `aplay: read_header:2973: read error`); the fourth is a genuine rc
split:

| cell | file | fifo |
|---|---|---|
| `aplay-empty.bin` | rc **0**, `mode=raw`, `Unsigned 8 bit, Rate 8000 Hz, Mono` (141 B log) | rc **1**, `aplay: read_header:2973: read error` |

So: **for paplay and ffplay the transport axis is verdict-inert on this member
set**; for aplay it is inert except at the empty-input edge. This is the
boundary form of the carried guard "wire order + write order both needed as
witness": the transport does not move the verdict here, but the *fifo path*
collapses aplay's informative call-site line into the generic
`read_header:2973`, i.e. **the fifo arm loses aplay's failure-mode witness**.

## 3. Edge members

### 3.1 Base set (`probe_boundary_r75.py:54-56`, built at `:247-272`)

| member | paplay | aplay | ffplay |
|---|---|---|---|
| `empty.bin` (0 B) | rc1 open-fail | file rc0 raw / fifo rc1 | rc0, no format, `Invalid data` |
| `trunc20_dec_act.wav` | rc1 | rc1 (file: line 1067 / fifo: read_header) | rc0, no format |
| `trunc300_dec_act.wav` (header + 256 B data) | **rc0** | rc0 `wav` | rc0 `wav` |
| `trunc300_dec_hcom.wav` | **rc0** | rc0 `wav` | rc0 **`hcom`** |
| `magicbad_dec_act.wav` (magic `XXXX`) | rc1 | rc0 **raw** | rc0, no format |
| `hdronly_dec_act.wav` (44 B header, 0 data) | **rc0** | rc0 `wav` | rc0 `wav` |
| `zerodata.wav` (`data` size 0) | **rc0** | rc0 `wav` | rc0 `wav` |
| `nomagic512.snd` | rc1 | rc0 raw | rc0, no format |

### 3.2 New set this seat added (`edge2/`, built at `probe_boundary_r75b.py:196-241`)

36 cells (`e2-<consumer>-<member>-{file,fifo}`), **max wall 0.128 s, no hang in
any cell** — receipts `runs/20261014T163317Z-boundary-r75b/verdicts.json`.

| member (sha256 prefix) | what it probes | paplay | aplay `-D null` | ffplay |
|---|---|---|---|---|
| `riff_giant_decl.wav` `27f8bc74` — `data` declares `0xFFFFFFF0`, payload 556 B | declared-length trust → **hang probe** | rc0 | rc0 `wav` | rc0 `wav` |
| `fmtext_dec_act.wav` `d794a343` — `WAVE_FORMAT_EXTENSIBLE`, fmt size 40, cbSize 22 | format family | rc0 | rc0 `wav` (`Signed 16 bit Little Endian`) | rc0 `wav` (`pcm_s16le`) |
| `hcom_fmtext.wav` `ec5460b8` — RIFF/WAVE-extensible container holding **HCOM** bytes | container vs content precedence | rc0 | rc0 `wav` | rc0 **`wav`** (not `hcom`) |
| `rifx_dec_act.wav` `04a391c0` — `RIFX` big-endian container | container family | rc0 | rc0 `wav`, **`Signed 16 bit Big Endian`** | rc0 `wav` (`pcm_s16le` — lavf endian-converts) |
| `datafirst_dec_act.wav` `5a2249a1` — `data` chunk before `fmt ` | chunk order / seek-back | **rc1 open-fail** | rc1 (line 1189) | **file rc0 `wav` vs fifo rc0 no-format** |
| `listchunk_dec_act.wav` `6e821507` — `LIST` declared 24 / 20 content bytes (**4-byte chunk-walk desync**) | malformed chunk length | **rc0** | rc1 (line 1206) | **rc0, no format, `Invalid data`** |

Three boundary facts fall out:

- **F3.1 No consumer trusts a declared data length enough to hang.** The
  `0xFFFFFFF0` declaration, on both file and fifo with a writer that closes
  after the real bytes, exits rc 0 in ≤0.03 s everywhere. The hang classes in
  §6 are therefore *EOF/open* classes, not length classes.
- **F3.2 ffplay's `datafirst` cell is transport-split at rc 0** (file: wav
  detected and played; fifo: `Invalid data`). Same bytes, same command, only
  the seekability of the input changed. This is the second seekability witness
  in the arm (the first is §8's mpv contrast) and it is invisible to rc.
- **F3.3 Container beats content, and beats the file name.** `hcom_fmtext.wav`
  is detected as `wav` by ffplay although its payload is HCOM — the HCOM
  detection in the matrix (`dec_hcom` → `hcom`) only fires for a bare HCOM
  container. `RIFX` is accepted by all three (aplay even reports the byte order
  it decoded). `listchunk` (4-byte desync) is the only member where **all three
  witnesses differ**: libsndfile (paplay) still opens it (rc 0, **no witness of
  what it decoded**), aplay refuses (rc 1), lavf refuses-but-rc-0.

## 4. Name axis — paplay does **not** inherit the pw-cat `.snd` fork

`probe_boundary_r75.py:376-421`. Identical 512 B no-magic bytes under four names
(`nomatch.snd`, `.SND`, `.wav`, `.foo`), file and fifo:

| name | paplay file | paplay fifo | pw-cat (same bytes, same window) |
|---|---|---|---|
| `.snd` / `.SND` / `.wav` / `.foo` | rc1, 27 B `Failed to open audio file.` ×4 | rc1, same ×4 | **rc 0, 0 B stderr** |

And content wins over name for paplay: the canonical WAV bytes copied to
`wavcontent.snd`/`.foo` → rc 0 on file, fifo **and** `/dev/stdin` (rfd). So the
paplay name axis is **degenerate (name-blind)** — the answer to the author
brief's question is *no*, and the contrast is a decoder-strictness fork instead:
`pw-cat` rc 0 with an empty stderr on the same no-magic bytes is an
**unwitnessed positive** (rc alone cannot say whether it decoded or played raw).
`pwcat-{file,fifo}-nomagic-snd.stderr.log` are 0 bytes; treat that leg as
`no-witness`, never as `decoded`.

## 5. Negative controls — daemon/device/backend blockages

### 5.1 Daemon severing is **consumer-specific in both directions** (headline)

`probe_boundary_r75b.py:272-301`, 12 cells, same member/window, override env per
child only (session daemon never touched):

| override (child env) | `paplay` | `pw-cat -p` |
|---|---|---|
| none (baseline) | rc0 (0.132 s) | rc0 (0.084 s) |
| `PIPEWIRE_RUNTIME_DIR=<dead dir>` | **rc0 — NOT severed** (0.128 s) | rc1 `error: pw_context_connect() failed: Host is down` |
| `XDG_RUNTIME_DIR=<dead> + PIPEWIRE_RUNTIME_DIR=<dead>` | rc1 `pa_context_connect() failed: Connection refused` | rc1 `Host is down` |
| `PULSE_SERVER=unix:<dead>/native` | rc1 `Connection refused` | **rc0 — NOT severed** |
| `XDG_RUNTIME_DIR=<dead> + PULSE_SERVER=unix:/run/user/1000/pulse/native` | **rc0 — PULSE_SERVER wins** | rc1 `Host is down` |
| `XDG_RUNTIME_DIR=<dead> + PULSE_SERVER=""` (empty) | rc1 `pa_context_connect() failed: **Invalid server**` | rc1 `Host is down` |

- **F5.1 (independently verifies the carried scout claim, and sharpens it).**
  `PIPEWIRE_RUNTIME_DIR` alone does **not** sever paplay; `XDG_RUNTIME_DIR` and
  `PULSE_SERVER` do. The pair also shows the converse: `PULSE_SERVER` alone does
  **not** sever `pw-cat`. Any single-variable "daemon gate" is therefore only
  valid for the consumer it was calibrated on.
- **F5.2 Two distinct paplay connect-error classes** — `Connection refused`
  (a server path that exists nowhere/refuses) vs `Invalid server` (empty
  `PULSE_SERVER`) — with the *same* rc 1. A gate keyed on
  `"pa_context_connect" in tail` cannot tell them apart; a gate keyed on
  `Connection refused` misses the empty-variable case.
- **F5.3 `PULSE_SERVER` outranks `XDG_RUNTIME_DIR`** for paplay: a dead
  `XDG_RUNTIME_DIR` with a live explicit `PULSE_SERVER` still plays (rc 0).
- **F5.4 paplay's dead-daemon failure is *not* the file-open failure.** In the
  base harness dead-runtime gate (`probe_boundary_r75.py:532-553`) the 87-byte
  stderr is `Connection failure: Connection refused` + `pa_context_connect()
  failed: Connection refused`, and `open_fail` (the
  `"Failed to open audio file."` probe) is **false**. The two failure surfaces
  are disjoint: *daemon* failure never prints the file line; *content* failure
  never prints a connect line.
- **F5.5 The orphan-writer hazard does not materialize for paplay.** Writer
  spawned first on a fifo, then paplay pointed at it with a dead runtime:
  `writer_alive_at_teardown: false`, `writer_rc: 0` — the writer **completed**,
  i.e. paplay opened the fifo (unblocking the writer) *before* it failed to
  connect. Ordering witness: **file open precedes context connect** for paplay.
  (The general hazard is real — §6's writerless cells show both consumers
  blocked on the open — but this specific ordering makes paplay's early-death
  path writer-safe.)

### 5.2 Device / backend controls (aplay, ffplay)

| cell | rc | surface |
|---|---|---|
| `aplay -D null` | 0 | `Playing WAVE '<input>' : Signed 16 bit Little Endian, Rate 8000 Hz, Mono` |
| `aplay -D pipewire` | 0 | same, 0.205 s (couples to the live PipeWire ALSA plugin) |
| `aplay` (default = PipeWire Media Server) | 0 | same, 0.206–0.21 s |
| `aplay -D hw:0,3` | 1 | `audio open error: Device or resource busy` (0.002 s) |
| `aplay -D nosuchdevice` | 1 | `Unknown PCM …` + `audio open error: No such file or directory` |
| `aplay -D hw:0,0` | 1 | `Playing WAVE …` **then** `aplay: set_params:1404: Channels count non available` — a **late** failure: the positive line already printed, so "did it print `Playing WAVE`" is not a success test |
| `ffplay`, `SDL_AUDIODRIVER=nosuchdriver` | 1 | `Could not initialize SDL - Audio target 'nosuchdriver' not available` |
| `ffplay`, `SDL_AUDIODRIVER=""` | 0 | wav detected; the DISPLAY hint line appears only in the failure case (red herring) |

## 6. Hang / kill semantics (`probe_boundary_r75.py:431-462`, 18 cells × 2 reps)

All cells: fifo named `dec_act.wav` (the canonical member), writer mode per row,
`harness_kill` = the outer harness had to `killpg` after its 10 s grace.

| writer mode | wrapper | `paplay` | `aplay` | `ffplay` |
|---|---|---|---|---|
| **none** (writerless fifo) | `timeout -s TERM 4` | rc **124**, wall 4.001 | rc **-9**, wall **10.006**, **`harness_kill: true`** | rc **124**, wall 4.004 |
| none | `timeout -s KILL 6` | rc -9, wall 6.001 | rc -9, wall 6.001 | rc -9, wall 6.002 |
| none | `timeout -k 2 -s TERM 4` | rc 124, wall 4.002 | rc **-9**, wall 6.001 | rc 124, wall 4.004 |
| `empty` (writer opens+closes, 0 B) | `timeout -s KILL 8` | rc 1 `Failed to open audio file.` | rc 1 `aplay: read_header:2973: read error` | **rc 0** `Invalid data found when processing input` |
| `hold` (writes full member, keeps fifo open 8 s) | `timeout -s KILL 6` | rc **-9**, wall **6.001** (waits for EOF) | rc **0**, wall **0.003** (length-trusting, returns at once) | rc **-9**, wall **6.002** (waits for EOF) |
| `partial_kill` (writes 300 B then `kill -9 $$`) | `timeout -s KILL 8` | rc 0 (0.115 s) | rc 0, `mode=wav` (0.003 s) | rc 0, wav detected (0.076 s) |

- **F6.1 TERM-immunity is per-consumer, not per-situation.** On a writerless
  fifo, `aplay` prints `Aborted by signal Terminated...` (32 B) and **keeps
  running** — TERM is acknowledged in text, not in effect; the harness's 10 s
  `killpg` is what ended it (rc -9, `harness_kill: true`, wall 10.006).
  `paplay` and `ffplay` die of TERM (rc 124, wall 4.00). `timeout -k 2` (TERM
  then KILL) ends aplay at wall 6.001 → escalation works, and
  `timeout -s KILL` is the only wrapper that is safe for all three.
- **F6.2 The rc for a `timeout -s KILL` expiry is `-9`, not `137`,** because the
  wrapper dies inside the group it signalled. `-9` alone therefore cannot
  distinguish "inner KILL expiry" from "harness kill" — only `harness_kill` and
  `wall_s` can (`6.001` vs `10.006`). This is the concrete form of the carried
  guard "rc alone is never a verdict".
- **F6.3 A linger writer splits the consumers:** `aplay` exits rc 0 in 3 ms
  while the writer is still holding the fifo open (it plays the declared
  length), whereas `paplay` and `ffplay` block until EOF and must be killed.
  So "hang on a fifo" is *not* a property of the fifo — it is a property of the
  consumer's EOF discipline.
- **F6.4 Truncation is not an error for any of the three:** the `partial_kill`
  writer's 300 bytes (header + 256 B of a 556 B body) yields rc 0 everywhere
  (`aplay` `mode=wav`, `ffplay` detected `wav`, `paplay` no open-fail). A
  short-write is invisible to rc; only the body-length witness would show it.

**Load replays** (`probe_boundary_r75.py:471-516`): 8 concurrent writerless-fifo
readers, one wrapper class per cell, `harness_kills: 0` in every cell —

| cell | rcs | walls |
|---|---|---|
| `load8-paplay-TERM4` | `124 ×8` | 4.018–4.020 |
| `load8-ffplay-TERM4` | `124 ×8` | 4.019–4.020 |
| `load8-mixed-paplay4-ffplay4-TERM4` | `124 ×8` | 4.019–4.021 |
| `load8-aplay-TERM4-k2` | **`-9 ×8`** | 6.021–6.023 |

**F6.5** The kill class is invariant under 8-way concurrency and under a mixed
consumer load: no wall inflation, no new class, no harness kill. aplay's
TERM-immunity is a consumer property (all 8 needed the KILL escalation), not a
contention artifact.

## 7. Pacing — and a warning about the aplay lattice

`probe_boundary_r75.py:600-613`, 4.0 s member (`corpus/artifacts/stem_sections.wav`):

| cell | wall |
|---|---|
| `pace-paplay-live` | **4.03 s** (real-time, live daemon) |
| `pace-ffplay-dummy` | **4.04 s** (real-time under `SDL_AUDIODRIVER=dummy`) |
| `pace-aplay-null` | **0.003 s** (instant — the `null` plugin discards, no pacing) |
| `pace-aplay-default-dec_act` | 0.18 s (0.03 s member + device open/setup) |

**F7.1** Every `aplay` matrix/edge cell used `-D null`; those walls are **null-
device walls, not playback-pacing witnesses**. Any "pacing_instant" reading from
an aplay `-D null` cell is an artifact of the device, not of the consumer —
`aplay` on the real default device does couple to the sink. (`content_duration_s`
in these verdicts is a hardcoded annotation at `:611`, **not** a measurement —
do not cite it.)

## 8. Fork control — ffplay vs mpv on `dec_hcom`

`probe_boundary_r75.py:321-371`, both transports, same window:

| consumer | member | transport | rc | witnesses |
|---|---|---|---|---|
| `ffplay` | `dec_hcom` | file / fifo | **0 / 0** | `detected_format: hcom`, `audio_stream: hcom, 22050 Hz, 1 channels, u8`, **`seeks: 0`** |
| `ffplay` | `dec_act` | file / fifo | 0 / 0 | wav, `seeks: 0` (control) |
| `mpv` | `dec_hcom` | **file** | **2** | `refresh_seek: true`, `seek_failed_eperm: true`, verdict `no audio or video data played (reason 4)` |
| `mpv` | `dec_hcom` | fifo | 0 | `not_seekable: true`, no refresh seek |
| `mpv` | `dec_act` | file / fifo | 0 / 0 | `refresh_seek: true` (file), `not_seekable: true` (fifo) |

**F8.1 The mpv inverted-seek fork does not transfer to ffplay.** On the same
member, in the same window, mpv's file arm fails with an EPERM refresh seek
(rc 2) while ffplay reports 0 seeks and rc 0. ffplay's default pull path never
issues the refresh seek that wounds mpv, so `dec_hcom` is **not** a wound member
for the SDL/lavf consumer class. Bounded claim: `seeks` comes from ffplay's own
`Statistics: … N seeks` line (`-loglevel debug`), and ffplay reports `0` on the
control member too — the counter is real but the *absence* of a seek is only
meaningful next to mpv's positive seek on the same bytes (which is why both legs
are in the receipt).

## 9. Parser hazards for the r75 author (first-hand from the fixture at HEAD)

Verified in `corpus/fixtures/measure_audio.py` (sha pinned in §0):

1. **Consumer verdict-group branch is a two-way binary** —
   `:1168-1170`: `sig = ((exit_code, sndfile_error) if consumer == "pw-cat" else
   (exit_code, lavf_detected, seek_failed))`. A `paplay`/`aplay`/`ffplay` leg
   added without extending this branch is silently keyed on the **mpv**
   signature (`lavf_detected`/`seek_failed` are both absent for paplay/aplay →
   every paplay cell collapses to the same key).
2. **The daemon-gate check is a substring test on the pw-cat spelling** —
   `:1255-1258`: `exit_code != 1 or "pw_context_connect" not in stderr_tail`.
   paplay's analogue is `pa_context_connect` (one letter apart, F5.4) and its
   stderr has **two** lines (87 B) whose last line is the connect line; the
   `pw-cat` gate would fire a false `failures[]` entry on any paplay gate.
3. **`_pwcat_fields` (`:1024-1032`) finds nothing on the new surfaces** — its
   regex is `sndfile: failed to open audio file "…"`; paplay's content failure
   is the 27-byte unprefixed `Failed to open audio file.` (no path, no
   `sndfile:`), aplay's is `aplay: <fn>:<line>: …`, ffplay's is
   `<path>: Invalid data found …`. Reusing it returns `(None, None)` on all
   three (§scribe's audit says the same; confirmed here on raw bytes).
4. **`_consumer_tail` (`:1010-1022`) splits on CR** — ffplay's stderr glues the
   progress fragment to the error line with `\r` (measured 205 B cell:
   `    nan    :  0.000 fd= … sq=    0B ^M<input>: Invalid data found when
   processing input`). A `\n`-only parser sees the header inside a progress
   line; `splitlines()` sees it line-initial. Either way the ffplay tail is a
   **timing leaf** (`M-A: nan/0.000`) whenever the cell ends in a hang or a
   silent success, and it is **not byte-stable run to run** (scribe measured
   1–2 differing bytes; my `norm_tail` normalizes it away by design,
   `probe_boundary_r75.py:82-95`).
5. **rc is empty of information for ffplay (42/42 rc 0) and half-empty for
   aplay (19/35 rc-0 cells are the silent `raw` fallback).** Any verdict that
   keys on rc alone passes an invalid-data cell for ffplay and a garbage cell
   for aplay.
6. **Receipt writer** — `:2871-2872`: `out.mkdir(parents=True)` with **no
   `exist_ok`** and `json.dumps(..., allow_nan=False)`. Two consequences the new
   consumers make live: ffplay's own log contains the literal token `nan`
   (`M-A: nan`), and any float taken from an ffplay tail would raise
   `ValueError: Out of range float values are not JSON compliant`; a duplicate
   run stamp raises `FileExistsError`.
7. **`aplay -q` erases the only witness** (scribe, re-confirmed by construction:
   the positive witness *is* the `Playing WAVE/raw data` line, and the raw line
   is also the failure witness). The r75 aplay leg must not run `-q`.

## 10. Remaining unknowns / not claimed

- **No live-daemon restart was tested.** All severing cells override child env
  only; the session `pipewire`/`pipewire-pulse`/`wireplumber` processes
  (pids 1203634/1203790/1203636) were never signalled. A *dead* (not
  unreachable) daemon path is untested.
- **`PULSE_SERVER` forms beyond `unix:` paths** (`tcp:`, `host=`, `$XDG…`
  expansion) are untested; only unix-socket paths and the empty string are.
- **`aplay -D hw:*` success is not claimed**: the only free raw device tested
  (`hw:0,3`) was busy and `hw:0,0` failed channel negotiation, so "raw hw works"
  is unmeasured; the working aplay legs are `null`, `pipewire`, `default`.
- **The `listchunk` member is a malformed-chunk control** (declared 24 vs 20
  content bytes), not a clean LIST-skip control; a well-formed LIST member was
  not measured, so "aplay cannot skip unknown chunks" is *not* established —
  only "aplay refuses this desync, lavf refuses it at rc 0, libsndfile still
  opens it" is.
- **ffplay's seek counter** is only read from the debug `Statistics:` line; a
  cell where ffplay *does* seek (e.g. an explicit `-ss`) was not measured, so
  the counter's positive path is unproven in this arm.
- **Foreign orphan process observed, not touched** (not this seat's lane):
  pid 1484210 `ffplay -nodisp -autoexit -loglevel debug
  …/corpus/live/r75-scout/scratch/fill-50817180/leg.wav` — a leftover from the
  r75-scout scratch, still resident at 16:33Z. My own arm's orphan check is
  clean (`orphans: (none)` in both `full-run-w14b.out` and
  `full-run-r75b.out`).

## 11. Receipts (all under `corpus/live/r75-boundary/`)

| artifact | sha256 |
|---|---|
| `probe_boundary_r75.py` (harness, reused) | `16f19a837a34db77c6073e5638557916da7e4d561c62d686f789366efa27810e` |
| `probe_boundary_r75b.py` (this seat) | `def3e7179702874cdbacfd147d838c7e916537b153975c84243824d22eb7d5a7` |
| `runs/20261014T162937Z-boundary-r75/{matrix-rep1,matrix-rep2}-verdicts.json` | `a2e411dda1763a41e251f1120fe620d219f6e521e7cc80d82cad6c18910af8bd` |
| `runs/20261014T162937Z-boundary-r75/{kill-rep1,kill-rep2}-verdicts.json` | `bd4f62db245bccc2e18ec13615c84425eb70ba5f20c6611e401afd216faf8344` |
| `runs/20261014T162937Z-boundary-r75/measurements.json` | `87ca00caf550454a1c6a99b5d9d59e95202866c0bf3fca715e5f3e07629f39d1` |
| `runs/20261014T162937Z-boundary-r75/verdicts.json` | `ab047c273e92873f6ae6230a324ce333b21d9d0c96385245e9688a8387bf0f80` |
| `runs/20261014T162937Z-boundary-r75/summary.tsv` | `fe8a9c58418c4c67d7911ba54f35f9c97e4f3c16d18abadc86e8048aaf93561a` |
| `runs/20261014T162937Z-boundary-r75/env.txt` | `02a8979aa9a237a901ee45968461e479a40d528f5f24067f295c8f77c95584f2` |
| `runs/20261014T163317Z-boundary-r75b/verdicts.json` | `4354e0f0e0c0e7a72b320cc3305fde4f2e69f4530f352486f9e5df9410b68b62` |
| `runs/20261014T163317Z-boundary-r75b/measurements.json` | `e3c805d2e40902f324bc09013198c73ce494c1ad2167e64cff48ea22b8d6e117` |
| `runs/20261014T163317Z-boundary-r75b/summary.tsv` | `25abc51bd4f47fa389299aeaf49783671c2afb2b90084fb28372b6a212380c0b` |
| `edge/manifest.json` (15 entries = 14 members + a stale self-entry, see below) | `5088be0b6694f1755d63fc1a43e73c64a1e1f7f7029dc16441fbbe2a4a9a3e8d` |
| `edge2/manifest.json` (6 members) | `fa64992fed41137f15b69a7a626b20a75d31e274eaa8b30599a0a92625afdb6e` |
| raw logs | `logs/matrix` 252 · `logs/kill` 36 · `logs/name` 13 · `logs/gates` 11 · `logs/fork` 8 · `logs/pacing` 4 · `logs/r75b/edge2` 36 · `logs/r75b/iso` 12 · `logs/r75b/devices` 4 |

Prior-generation receipts (`runs/20261014T160930Z-boundary-r75/`) are kept
untouched as the second-generation replay witness; they are byte-identical to
mine for `matrix-rep{1,2}` and `kill-rep1` (see §0) but remain incomplete
(no `measurements.json`/`verdicts.json`/`env.txt`).

**Hygiene wrinkle (recorded, not repaired):** `edge/manifest.json` contains a
self-entry, because `build_edge()` (`probe_boundary_r75.py:267-271`) hashes
every file present *before* rewriting the manifest — and the prior generation's
manifest was already on disk when my run built the same directory. The self-entry
therefore carries the **pre-rewrite** hash of that file. Member hashes
themselves are unaffected (each member is rewritten from the canonical
`round-66` bytes at every build); a reader that wants the true 14-member set
should ignore the `manifest.json` key. No repair was attempted: insertion-only
reuse of the recovered scratch outranks cosmetic hygiene, and the hashes are
recomputable from `edge/` at any time.

**Stop condition:** this seat's assigned question (edge cells + negative
controls + hang/kill semantics for the three new consumers) is answered with
measured receipts; no product file was edited, no receipt outside this seat's
scratch was written, and the author's parser does not yet exist to compare
against.
