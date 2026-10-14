# R76 BOUNDARY (audio) — capture direction: source/device gates, bound units, the TERM ladder, write-side edges

Seat **boundary** (leaf, report-only; no subagents, no git mutation). Wave
`shokunin-train-20261101-w15`, lane audio. Repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`, HEAD **`2250be9`** (unchanged by
this seat; `git rev-parse HEAD` at 17:29Z and 17:41Z). Host `plazir27`
(`Linux 7.2.3-arch1-3`, 32 CPUs), window 2026-10-14 **17:29Z–17:45Z** (UTC; local
TZ UTC−3, so `ls` mtimes are local). Fixture `corpus/fixtures/measure_audio.py`
sha256 **`ebecea00…f948`** — the `--probe-capture-r76` arm has **not landed** at
any point in this window (`grep -c 'probe-capture-r76' → 0`), so every claim
below is *pre-landing* boundary evidence for that parser.

Write scope honoured: this report + `corpus/live/r76-boundary/` only. No tracked
file touched (`git status --porcelain` shows only untracked lane scratch); no git
mutation beyond `rev-parse`/`status`.

**LSP device: unavailable this session.** `mcp_list_servers` → only `rea`
(Ghidra; `annotate_native_function`/dossiers — no `definition`, `references`,
`hover`, `type_definition`, `implementation`). No source trace was possible for
any client binary, so every **mechanism** sentence below is labelled *inference*
and rests on process-level measurement with retained receipts. No text grep is
offered as semantic proof anywhere in this report.

Consumers under test (verbatim versions): `pw-record`/`pw-cat` **libpipewire
1.6.8** · `parec`/`parecord` **pacat 17.0-98-gb096**, libpulse 17.0.0 ·
`arecord` **alsa-utils 1.2.16** · `ffmpeg` **n9.0.1** (lavf 63.1.101,
`--enable-libpulse`) · contrast leg `sox`/`soxi`. Live session: `pactl info` →
*PulseAudio (on PipeWire 1.6.8)*, protocol 35, default source
`alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source`.

---

## Headline — ten results that change what the author should build

1. **`rc` is not merely weak for `pw-record` — it is constant.** Across 48
   measured `pw-record` cells the only rc values are **1 (n=42)** and **−9
   (harness KILL, n=6)**. **20 of the rc=1 cells carry a complete, correctly
   finalized WAV** (`declared == size−8`, payload > 0) including every bounded
   `-n` capture. There is no rc that means "capture succeeded" for this consumer.
2. **A bound is honoured in its own unit, and the brief's single predicate
   "duration/byte cap honoured per consumer" is false.** `-n`/`-s` are frame
   counts (byte-exact); `-d`/`-t` are *stream-time* bounds; `-fs` is a byte bound
   with a one-packet overshoot. On a **non-pacing** device `-d`/`-t` stop being
   wall-clock bounds at all: `arecord -D null -d 1` = 1.000 s of audio in
   **0.021 s** wall, and `ffmpeg -f alsa -i null -t 1` writes **13.533 s** of
   audio in 1.023 s wall (13.2×; 11.7× for `-t 2`).
3. **`parecord` loses ≈1.9 s at stream start.** captured_s/wall_s = 0.51 (4 s
   window) and 0.77 (8 s window) — a *fixed* dead start, not a rate. Two-point
   fit: 4.000−2.048 = 1.952 s, 8.000−6.144 = 1.856 s. `--latency-msec=10`
   removes it (8.030 s captured in 8.005 s wall). Consequence: a 1–2 s
   TERM-bounded `parecord` leg captures **0 bytes** and finalizes a **valid empty
   WAV** — an unfalsifiable-looking success.
4. **The three writers leave three different partial headers, and two
   independent readers disagree about the same file in opposite directions.**
   `arecord` pre-declares its requested duration (a 1.375 s kill declares
   **300 s**, 218× over) → `ffprobe` says 1.375 s while `sox` says 300.000 s.
   `ffmpeg` leaves the **0xFFFFFFFF** placeholder → `ffprobe` says 1.365 s while
   `sox` says **0.000 s** (`data length is unknown`). `libsndfile`
   (pw-record/parecord) rewrites a consistent header at close → both agree.
5. **"Usable partial wav" must name the reader.** For the same killed file the
   verdict ranges over {usable, 218×-overstated, silently-zero, hard-reject}.
   The only in-header truncation witness is `data_declared + 36 != declared`
   (observed once, on a cut that landed between `arecord`'s two header updates —
   *inference*).
6. **The capture consumers have no TERM₁ immunity** (contrast: r75's `aplay` was
   TERM-immune). All 7 targets die to TERM₁ mid-capture. The single exception is
   phase-local: `ffmpeg -f pulse` TERM₁'d at 0.05 s **survives** TERM₁ for the
   0.5 s grace in 4/4 reps and is killed by TERM₂ (rc 255 ×3 / 123 ×1, 0-byte
   output). One-TERM survival only — no immunity is claimed from one send.
7. **A fifo output is a consumer-local fork, and the fifo rendezvous precedes the
   format check.** With **no reader**, pw-record/parecord/arecord all block at
   `open(O_WRONLY)` (harness KILL at the wall bound). With a reader that leaves
   after 4096 B: `arecord` **dies of SIGPIPE (rc −13)**, `pw-record` refuses
   (`this file format does not support pipe write`), `parecord` refuses
   (`Failed to open audio file.`), `ffmpeg` refuses earlier and for a different
   reason (no muxer for a `.fifo` extension → rc 234).
8. **The roundtrip cell is viable — but only through the pulse leg.**
   `parec -d @DEFAULT_MONITOR@` while `pw-play corpus/artifacts/stem_sections.wav`
   plays → payload RMS **0.061736**, peak 0.125854, against a *silence control*
   of **exactly 0.000000** (digital silence) and a source member of 0.070254 /
   0.172363. `pw-record --target <monitor>` and `--target <sink>` both fail with
   `no target node available`; `pw-dump` shows **no monitor node exists** on this
   host (monitors are ports on the sink node).
9. **Determinism**: 5 of 7 consumers produce **byte-identical** TERM₁ partials
   across 4 independent reps (arecord-hw 264 044 B, parecord 44 B, ffmpeg
   262 144 B ×2 legs, arecord-null 288 000 044 B); `pw-record` varies over 3
   sizes in 1.45–1.51 s; **`sev-early-ar-hw` is bimodal** (rc −15/stale ×3 vs
   rc 1/consistent ×2).
10. **A record-adjacent child can outlive the harness.** A
    `start_new_session` consumer blocked on a writerless fifo **survived the
    harness being killed** and had to be killed by hand (measured on my own
    harness, §0.3). Fixed by putting an inner `timeout -s KILL` wrapper *inside*
    every cell argv — the outer wrapper alone does not cover orphans.

---

## 0. Protocol, harness provenance, defects found and fixed

### 0.1 Harness

`corpus/live/r76-boundary/probe_boundary_r76.py` (sha256
`440468fcf675050360fc12d3af17d322c62a4f2e9dde512db726b9580ce04e05` — the
revision that produced the `decl` matrix; the runs cited as authoritative
(`gates2`, `name`, `main3`, `sevrep1-4`, `fifo2`, `decl`) were each made with the
then-current revision and every one of them post-dates the fixes listed in §0.3).
Every run was launched as `timeout -s KILL <N> python3
probe_boundary_r76.py <groups>`. From the orphan fix onward (§0.3) every cell
*also* carries its **own** inner `timeout -s KILL` wrapper (bound = harness bound
+ 3 s, or ladder end + 6 s), recorded in the cell receipt as `wrapper`; the two
runs that pre-date that fix (`gates2`, `name`) contain **no** fifo-adjacent and
**no** ladder cells, so the outer wrapper is the only bound they need. Cells are
spawned with `start_new_session=True` and signalled by `killpg`; the ladder sends
exactly one TERM per phase and checks survival after a 0.5 s grace.

Receipts: `runs/<stamp>-boundary-r76-<tag>/{measurements.json,<group>-measurements.json,env.txt,cells/<cell>.log}`.
229 cells total; 0 runaway cells; 27 harness kills (all expected unbounded
streams or writerless-fifo blocks). `runs/verdicts-r76/verdicts.json` is the
derived lattice (`verdicts.py`, sha256 `4832aea4…ad7f0`).

### 0.2 Ladder semantics (r76 form of the carried guard)

`alive_after_term1` is measured **after** a 0.5 s grace from a single TERM₁; if
the process is still alive, TERM₂ is sent and `alive_after_term2` is measured;
only then is KILL used. `killed_by ∈ {term1, term2, kill, harness}`.

### 0.3 Defects I created and corrected (honest accounting)

| defect | how it was caught | correction | blast radius |
|---|---|---|---|
| TERM **storm**: the first ladder loop re-sent TERM every 20 ms while `alive1` was still `None` (≈5 signals in 80 ms) | `ffmpeg` printed `Received > 3 system signals, hard exiting` in a cell where I had sent one signal | explicit phase machine: `pre → post1 → post2`, one send per phase | run `…-main2` only; **all sever numbers in this report are from the corrected runs** (`main3`, `sevrep1-4`) |
| `sever` phases shared one output path → `bytes_at_term1` read the previous phase's file | `sev-early-ff-pulse` reported `bytes_at_term1=262144` with a 0-byte final file | per-phase output paths (`<stem>-<phase>.wav`) | run `…-main3` early-phase `bytes_at_term1` values; re-measured in `sevrep1-4` |
| fifo "early-exit" cells started **no reader** (wrong helper signature) → they were duplicate "no reader" cells | hand pin showed `arecord` dying of SIGPIPE where the receipt showed a 4 s block | `fifo_pre(mode=…)` + reader statistics recorded in the receipt | run `…-main3` fifo group; replaced by `…-fifo2` |
| gate batch conflated the **device axis with the channel axis** (`arecord -D hw:0,0 -c 1` fails on channels) | the same argv with `-c 2` succeeded | channel count held at 2 for device cells, mono kept as an explicit negative control | run `…-gates`; replaced by `…-gates2` |
| pw-record gate cells omitted the output file token (`error: filename or - argument missing`, rc 1 in 0.02 s) | all 8 cells returned the usage text | output path is an argv token in every cell | run `…-gates`; replaced by `…-gates2` |
| **orphan**: a `arecord` blocked on a writerless fifo survived `pkill` of the harness | `pgrep -af` after the kill | inner `timeout -s KILL` in every cell argv | no receipts affected; recorded as finding 10 |

**Disk hygiene.** The `arecord -D null` ladder cells wrote multi-hundred-MB
partials (288 MB / 234 MB / 200 MB / 194 MB). Scratch peaked at **2.2 GB**; after
their headers were receipted (`edge/partials-r76/usability.json`,
`…-measurements.json`) the >50 MB files were deleted → **70 MB** retained. No
split-file flood occurred: every null-device cell carried a positive
`-d`/`-s` bound (contrast: r76-scout §6, whose unbounded null legs produced 91 GB).

---

## 1. Viability gates — exact enumerations and the gate lattice

### 1.1 Inventory (this host, 17:29Z)

- `pactl list sources short` (rc 0): **6 sources** — 4 monitors
  (`…hdmi-stereo.monitor`, `…SPDIF__sink.monitor`, `…Speaker__sink.monitor`,
  `…Headphones__sink.monitor`) + 2 real sources (`…HiFi__Line__source` = Default
  Source, `…HiFi__Mic__source`); all 48 kHz, all `SUSPENDED`.
- `pactl list sinks short` (rc 0): **4 sinks**, all `SUSPENDED`.
- `pw-dump` node inventory (`env.txt`): **4 `Audio/Sink` nodes, 2 `Audio/Source`
  nodes, and NO monitor node.** `pw-link -o` lists the monitors as ports on the
  sink node (`alsa_output.…SPDIF__sink:monitor_FL/FR`). *This is the structural
  reason the native monitor route is closed (§5).*
- `arecord -l` (rc 0): **3 capture devices on card 0** (`USB Audio` dev 0/1/2),
  `Subdevices 1/1` each. `arecord -L` adds `null`, `default`, `pipewire`.
- `ffmpeg -devices`: `alsa` and `pulse` both `DE`.

### 1.2 Gate lattice (rc / bytes / header / exact message)

| consumer | cell | rc | bytes | header | message (verbatim tail) |
|---|---|---|---|---|---|
| `pw-record` | `--target <Line__source> -n 48000` | **1** | 192 044 | **finalised** (1.000 s) | *(empty stderr)* |
| | `--target <monitor node name>` | 1 | 44 | finalised-empty | `no target node available` |
| | `--target <monitor>` (pulse spelling) | 1 | 44 | finalised-empty | same |
| | `--target <sink>` (monitor's own node) | 1 | 44 | finalised-empty | same |
| | `--target 55` (**node id** of the source) | 1 | 44 | finalised-empty | same |
| | `--target 46` (sink node id) | 1 | 44 | finalised-empty | same |
| | **no `--target`** | 1 | 44 | finalised-empty | `no target node available` |
| | `--target 0` (don't link) | **−9** | 44 | header only | *(blocked; harness KILL @4.013 s)* |
| | dead `PIPEWIRE_RUNTIME_DIR` | 1 | none | none | `error: pw_context_connect() failed: Host is down` |
| `parecord` | `-d @DEFAULT_SOURCE@` | **−9** | 393 260 | libsndfile 8/0 | *(unbounded; KILL @4.014 s; 2.048 s captured)* |
| | `-d @DEFAULT_MONITOR@` | **−9** | 393 260 | libsndfile 8/0 | same byte count as the source leg |
| | `-d <absent>` | 1 | 44 | finalised-empty @44100 | `Stream error: No such entity` |
| | dead `XDG_RUNTIME_DIR`+`PULSE_SERVER` | 1 | 44 | finalised-empty | `Connection failure: Connection refused` + `pa_context_connect() failed` |
| | dead `PULSE_SERVER` only | 1 | 44 | finalised-empty | same |
| `arecord` | `-D null -c 1` | 0 | 96 044 | finalised (1.000 s) | *(0.021 s wall — unpaced)* |
| | `-D hw:0,0 -c 2` | 0 | 192 044 | finalised (1.000 s) | *(1.044 s wall — paced)* |
| | `-D hw:0,0 -c 1` | 1 | none | none | `arecord: set_params:1404: Channels count non available` |
| | `-D default` / `-D pipewire` (1 **and** 2 ch) | 1 | none | none | `set_params:1462: Unable to install hw params:` + hw-param dump |
| | `-D hw:9,0` | 1 | none | none | `Cannot get card index for 9` + `main:850: audio open error: No such file or directory` |
| | `-D nosuchdevice` | 1 | none | none | `[error.pcm] Unknown PCM nosuchdevice` + `main:850: …` |
| | `-D default` **dead runtime** | 1 | none | none | `main:850: audio open error: Host is down` |
| | `-D hw:0,0` **dead runtime** | **0** | 192 044 | finalised | *(daemon-independent)* |
| `ffmpeg -f pulse` | `-i <Line__source> -t 1` | 0 | 193 618 | finalised (1.008 s) | *(1.144 s wall)* |
| | `-i <…monitor> -t 1` | 0 | 200 470 | finalised (1.044 s) | *(1.185 s wall)* |
| | `-i default -t 1` | **251** | none | none | `Error opening input: Input/output error` |
| | `-i nosuchsource -t 1` | **251** | none | none | **byte-identical message** |
| | dead `XDG_RUNTIME_DIR` | **253** | none | none | `Error opening input: **No such process**` |
| `ffmpeg -f alsa` | `-i hw:0,0 -t 1` | 0 | 192 322 | finalised (1.001 s) | *(1.084 s wall)* |
| | `-i null -t 1` | 0 | **2 309 274** | finalised (**12.027 s**) | *(1.044 s wall)* |
| | `-i hw:9,0` / `-i nosuchdevice` / `-i default` | 251 | none | none | `Input/output error` (all three, identical) |
| | `-i hw:0,0` **dead runtime** | **0** | 192 558 | finalised | *(daemon-independent)* |

**F1.1 — the gate must be keyed on the *name form*, not the message.** For
`ffmpeg -f pulse`, a *valid* Pulse name that resolves to nothing usable
(`default`) and an *absent* source (`nosuchsource`) produce the same rc (251) and
the same message; the only separable class is the dead daemon, and it is
separable **by rc** (253 = −ESRCH vs 251 = −EIO). A gate keyed on
`"Input/output error" in tail` cannot tell "you named it wrong" from "there is no
such source".

**F1.2 — the ALSA `default`/`pipewire` PCM is capture-blocked while the same
device works for playback.** r75 measured `aplay -D pipewire`/`-D default` rc 0
(0.205 s); `arecord -D default` fails at hw-param install for **both** mono and
stereo 48 k s16, and `ffmpeg -f alsa -i default` fails with the same EIO as an
absent device. The inversion is capture-side, and the plugin's own log is the
only witness. Bounded: alsa-utils 1.2.16 / libpipewire 1.6.8, this host.

**F1.3 — device axis vs channel axis.** `-D hw:0,0 -c 1` is rejected on
*channels*, not on the device; a device-axis cell that does not hold the channel
count fixed measures the wrong axis. (I made exactly this mistake in the first
gate batch — §0.3.)

**F1.4 — `--target` is a name resolver.** `--target 55` (the Line source's own
`pw-dump` id) fails exactly like an absent name, so numeric ids are not accepted
by this build's `--target`; and because **no monitor node exists**, both the
monitor name and the sink name fail. *Inference (medium):* `--target` resolves
against `node.name` via the session manager, and the monitor's ports live on the
sink node, which the capture-direction resolver refuses. r76-scout §1 found the
workaround (`--target <sink> -P stream.capture.sink=true`), which I did not
re-test; my negative result is for the plain forms only.

---

## 2. Bounded capture — which bound is honoured, in what unit

`bound-*` receipts, run `…-main3`. `captured_s` = payload bytes / (header
rate × channels × 2), i.e. the file's own claim; `wall` is measured.

| cell | requested bound | wall | captured (stream) | rc | header | verdict |
|---|---|---|---|---|---|---|
| `pw-record --target LINE -n 48000` | 48 000 frames | 1.084 | **1.000 s** (192 000 B) | **1** | finalised | exact, rc lies |
| `pw-record … -n 24000` | 24 000 frames | 0.562 | **0.500 s** | **1** | finalised | exact (half) |
| `arecord -D null -d 1 -c 1` | 1 s | **0.021** | 1.000 s | 0 | finalised | stream-time only (**48×** realtime) |
| `arecord -D null -s 48000` | 48 000 frames | **0.021** | 1.000 s | 0 | finalised | exact, unpaced |
| `arecord -D hw:0,0 -d 1 -c 2` | 1 s | 1.043 | 1.000 s | 0 | finalised | exact, paced |
| `ffmpeg -f pulse -i LINE -t 1` | 1 s | 1.164 | **1.005 s** | 0 | finalised | honoured |
| `ffmpeg -f alsa -i hw:0,0 -t 1` | 1 s | 1.084 | **1.003 s** | 0 | finalised | honoured |
| `ffmpeg -f alsa -i null -t 1` | 1 s | 1.023 | **13.533 s** | 0 | finalised | **13.2× over** |
| `ffmpeg -f alsa -i null -t 2` | 2 s | 2.026 | **23.675 s** | 0 | finalised | **11.7× over** |
| `ffmpeg -f pulse -i LINE -fs 100000` | 100 000 B | 0.702 | 105 600 B payload (105 678 B file) | 0 | finalised | **+5.7 % overshoot** (one packet) |
| `parecord` (no bound exists) | — | 2.027 | 0.341 s (65 580 B) | **0** | finalised | TERM₁ is the only bound; ~1.9 s dead start |

**F2.1 — `-t` bounds the device clock, not bytes.** On the unpaced ALSA `null`
device the delivered frame count runs ≈10× ahead of the timestamps ffmpeg
assigns, so `-t 1` yields 9.73 s / 12.03 s / 13.53 s across runs (non-reproducible)
and `-t 2` yields 23.26 s / 23.68 s. On paced devices (pulse, `hw:0,0`) the same
flag is exact to ≤0.8 %. The bound is a *stream-time* bound; the byte cap is a
function of the device's delivery rate.

**F2.2 — `-fs` is checked per packet.** Requested 100 000 B → 105 678 B on disk
(+5.7 %, one fragment).

**F2.3 — `pw-record` rc is constant.** 48 cells: rc ∈ {1 ×42, −9 ×6}. 20 rc=1
cells carry a complete finalized WAV (`name-pw-n_wav/bin/foo`,
`name-pw-container-override`, `gate-pw-target-src`, `bound-pw-src-n48000/n24000`,
`sev-mid-pw`, …). `-v` prints a full successful stream trace and **no error
line**. Any harness that treats `rc != 0` as failure will call every successful
`pw-record` capture a failure.

**F2.4 — `parecord` dead start (two-point fit).** 8 s window → 6.144 s captured
(1 179 692 B, 18×65536); 4 s window → 2.048 s captured (393 260 B, 6×65536);
`--latency-msec=10` → 8.030 s captured in 8.005 s wall (1 541 804 B);
`--fix-rate --fix-channels` → 6.687 s and a **44100 Hz header** (the requested
rate, not the source's). *Inference (medium):* a fixed ≈1.9 s stream-start cost
(suspend/resume or first-fragment wait), removed by a small latency request.
*Unknown:* which of those two mechanisms.

---

## 3. The TERM ladder — sever classes mid-capture

4 independent reps (`main3`, `sevrep1-4`), TERM₁ at 1.5 s (mid) or 0.05 s
(early), grace 0.5 s, then TERM₂, then KILL. Classes are from the corrected
single-send ladder.

| target | phase | rc | bytes at TERM₁ | final size | captured | `alive_after_term1` | header after death | class |
|---|---|---|---|---|---|---|---|---|
| `pw-record` | mid | **1** | 290 860 | 290 860 | 1.515 s | False | **finalised** | TERM₁-fatal, usable partial |
| `pw-record` | early | **1** | 4 140 | 4 140 | 0.021 s | False | finalised | TERM₁-fatal, usable tiny partial |
| `parecord` | mid | **0** | 44 | 44 | **0.000 s** | False | finalised-empty | TERM₁-fatal, **valid empty WAV** |
| `parecord` | early | **0** | 44 | 44 | 0.000 s | False | finalised-empty | same |
| `arecord -D hw:0,0` | mid | **−15** | 264 044 | 264 044 | 1.375 s | False | **declares 57 600 036 B** (300 s) | TERM₁-fatal, overstated ×218 |
| `arecord -D hw:0,0` | early | **−15 ×3 / 1 ×2** | 44 | 44 / 24 044 | 0 / 0.125 s | False | pre-declared / consistent | **bimodal** (§3.3) |
| `arecord -D null` | mid | 0 | 288 000 044 | 288 000 044 | 3000 s | False | finalised | completed before TERM (unpaced) |
| `arecord -D null` | early | −15 / 1 | ~2×10⁸ | 173–234 MB | 1800–2440 s | False | inconsistent or finalised | race (cut mid-flush) |
| `ffmpeg -f pulse` | mid | **255** | 262 144 | 262 144 | 1.365 s | False | **0xFFFFFFFF** | TERM₁-fatal, unresolved length |
| `ffmpeg -f alsa -i null` | mid | 255 | 2 621 440 | 2.6–3.4 MB | 13.7–17.7 s | False | 0xFFFFFFFF | same (unpaced) |
| `ffmpeg -f alsa -i hw:0,0` | mid | 255 | 262 144 | 262 144 | 1.365 s | False | 0xFFFFFFFF | same |
| `ffmpeg -f pulse` | early | 255 ×3 / **123** ×1 | 0 | **0** | — | **True (4/4)** | no file | **survives TERM₁**, dies on TERM₂ |

**F3.1 — no TERM₁ immunity in the capture direction.** Every mid-capture target
died to TERM₁ (0.02–0.08 s after the send). The one `alive_after_term1 = True`
is `ffmpeg`'s early phase (TERM₁ during startup): it survived the 0.5 s grace in
**4/4** reps and was killed by TERM₂, leaving a **0-byte** file. Per the carried
guard this is one-TERM survival only; TERM₂ was sufficient, so no immunity is
claimed.

**F3.2 — three partial-header idioms, three different truncation witnesses.**

| writer | state after TERM₁ | state after KILL | in-header truncation witness |
|---|---|---|---|
| libsndfile (`pw-record`, `parecord`) | rewritten at close: `declared == size−8` (consistent) | `declared=8, data=0` placeholder (stdlib `wave` rejects) | **none** — a truncated libsndfile file is indistinguishable from a short one |
| alsa-utils (`arecord`) | pre-declared requested duration; `declared == data+36` but 218× over | same, or split across two updates | `data_declared + 36 != declared` (1 observation) |
| lavf (`ffmpeg`) | `0xFFFFFFFF` in both fields (13/14 TERM₁ cells) | `0xFFFFFFFF`, or a 0-byte file before the first 256 KiB flush | `declared == 0xFFFFFFFF` → the length is *unknown*, must be byte-scanned |

**F3.3 — the arecord header conflict (resolved against r76-scout §3).** Four
cells, identical argv except the bound, TERM₁ at 1.5 s, all ending with
`size = 264 044`, `rc = −15`:

| argv | `declared` | `data_declared` | implied duration |
|---|---|---|---|
| *(no `-d`/`-s`)* | 2 147 483 684 | 2 147 483 648 | 2 GiB placeholder (`0x80000000`) |
| `-d 30` | 5 760 036 | 5 760 000 | 30 s |
| `-d 300` | 57 600 036 | 57 600 000 | 300 s |
| `-s 14400000` | 57 600 036 | 57 600 000 | 300 s |

So the scout's `0x80000000` KILL placeholder and my 300 s declaration are the
**same idiom under different bounds**: with a bound, arecord pre-declares that
bound; without one it writes the 2 GiB placeholder. In *both* cases the header is
internally consistent and the file is overstated; ffprobe recovers 1.375 s from
the real file size while a header-trusting reader reports the declaration. The
scout's rc=1 row and my rc=−15 rows are the two branches of a **phase race**:
if TERM₁ lands before the first period flush → `rc=−15` + the last-written
(pre-declared / placeholder) header, 3/5 reps; after ≥1 flush → `rc=1` and
arecord reaches its own exit path, which **corrects the data size** (2/5 reps;
the scout's no-bound `rc=1` row with `data=216136` is this branch, so the
correction happens on the no-bound path too). *Actionable:* whether a
TERM-killed arecord file is usable is decided by that race, not by the file.

**F3.4 — determinism across reps.**

- byte-identical TERM₁ partials in 4/4 reps: `arecord -D hw:0,0` 264 044 B;
  `parecord` 44 B; `ffmpeg -f pulse` 262 144 B; `ffmpeg -f alsa -i hw:0,0`
  262 144 B; `arecord -D null` (mid) 288 000 044 B.
- class-stable, size-varying: `pw-record` mid ∈ {278 572, 286 764, 290 860}
  (1.451–1.515 s); `ffmpeg -f alsa -i null` ∈ {2 621 440, 2 883 584, 3 145 728,
  3 407 872}; `arecord -D null` early ∈ {173.9, 195.0, 200.8, 214.0, 234.4 MB}.
- **bimodal (reported, not averaged)**: `sev-early-ar-hw` (rc −15/stale ×3 vs
  rc 1/consistent ×2) and `sev-early-ff-pulse` rc {255 ×3, 123 ×1} with a stable
  0-byte output and stable `alive_after_term1=True`.
- **bimodal at 1/14**: ffmpeg's declared-length state after TERM₁ is
  `0xFFFFFFFF` in 13 cells and *finalised* in one (`load8-ff-alsa-null-4`,
  rc 255, 3 203 442 B) — the trailer write occasionally wins the race.

**F3.5 — flush-block witness (payload gcd of partials).** This is the capture
direction's instance of the carried "buffering mode" guard: the byte count of a
killed capture measures the **writer's flush boundary**, never the captured
interval.

| consumer | payload gcd | n | note |
|---|---|---|---|
| `pw-record` | **4096 B** | 6 partials | 8 s harness-KILL file ends with a 1024 B remainder → 4096 is the dominant block, not an invariant |
| `parecord` | **65 536 B** | 6 | 65 580 / 196 652 / 262 188 / 393 260 / 1 179 692 / 131 116 |
| `arecord -D hw:0,0` | **24 000 B** | 10 | = ALSA period (6000 frames × 2 ch × 2 B) |
| `arecord -D null` (mono) | **12 000 B** | 10 | = period (6000 frames × 1 ch × 2 B) |
| `ffmpeg` (wav) | ≥262 144 B | — | 0-byte file if killed before the first 256 KiB flush; 262 144 / 1 310 720 / 3 145 728 B after |

---

## 4. Partial-file usability — reader-dependent by construction

`edge/partials-r76/usability.json`, `logs/partial-usability.txt`. Two independent
readers on the *same* killed files: `ffprobe` (derives duration from the real
file size) and `soxi` (trusts the header).

| file (killed) | size | `declared` / `data` | header predicate | ffprobe dur | `soxi -D` | verdict split |
|---|---|---|---|---|---|---|
| `sev_pw-mid.wav` | 290 860 | 290 852 / 290 816 | finalised | 1.5147 | 1.5147 | **both agree (usable)** |
| `sev_pa-mid.wav` | 44 | 36 / 0 | finalised | N/A | 0.0000 | both agree: empty |
| `sev_ar_hw-mid.wav` | 264 044 | 57 600 036 / 57 600 000 | consistent, 218× over | 1.3750 | **300.0000** | **readers disagree 218×** |
| `sev_ar_hw-early.wav` | 44 | 57 600 036 / 57 600 000 | consistent, 218× over | N/A | **300.0000** | empty file claiming 300 s |
| `sev_ar_null.wav` (cut) | 194 952 044 | 194 952 036 / 288 000 000 | **inconsistent** | 2030.75 | 3000.000 | both wrong, differently |
| `sev_ff_p-mid.wav` | 262 144 | 0xFFFFFFFF / 0xFFFFFFFF | length **unknown** | 1.3649 | **0.0000** + `data length is unknown` | **readers disagree 1.36 s vs 0** |
| `sev_ff_*-early.wav` | 0 | — | no header | rc 1 `Invalid data` | FAIL | hard reject |

**F4.1** "Usable partial wav" is a *reader-dependent* predicate, and the three
writers fail in three different ways. A verdict that says only "the file parses"
is vacuous on this lattice: the same arecord kill is 1.4 s to ffprobe and 300 s
to sox, and the same ffmpeg kill is 1.36 s to ffprobe and 0 s to sox. **The
receipt must name the reader** (this is the capture-direction analogue of r74's
3-valued `fork_kind` lattice).

**F4.2** The one in-header truncation witness I found is
`data_declared + 36 != declared`, observed on a cut that landed between
arecord's two header updates. *Inference (medium):* alsa-utils updates the RIFF
size and the data size as two separate writes, so a kill between them yields an
inconsistent header while a kill after both yields a consistent-but-overstated
one.

---

## 5. Write-side edges — fifo, /dev/full, /dev/null, path errors

`…-fifo2` run (22 cells). Reader modes: **none** (no reader ever),
**early** (reader drains 4096 B then closes), **drain** (reader drains to EOF).

| consumer | no reader | early-exit reader | draining reader |
|---|---|---|---|
| `pw-record` | **blocks** (rc −9, harness KILL @4.013 s) | rc **1** — `sndfile: failed to open audio file … this file format does not support pipe write` + `error: open failed: Input/output error`; reader read **0 B** | rc 1, same refusal (reader `eof=True`, 0 B) |
| `parecord` | **blocks** (rc −9 @4.013 s) | rc **1** — `Failed to open audio file.`; reader 0 B | rc 1, same (0 B) |
| `arecord -D null` | **blocks** (rc −9 @4.013 s) | rc **−13 (SIGPIPE)** after the reader took 4096 B | rc **0**, reader drained **28 800 044 B** to EOF |
| `ffmpeg -f pulse` | rc **234** @0.081 s — `Error opening output files: Invalid argument` | rc 234 | rc 234 |

**F5.1 — the fifo rendezvous precedes the format check.** With no reader, all
three file-writing consumers block in `open(O_WRONLY)` *before* they can discover
that they cannot write to a pipe; with a reader attached they fail immediately
(pw-record/parecord) or stream until the reader leaves (arecord → SIGPIPE). A
harness that omits the reader turns a **named refusal** into an **unbounded
block** — the concrete reason `timeout -s KILL` is mandatory on fifo-adjacent
cells, and the reason the r75 guard "receipt completeness is the verdict carrier"
applies here too.

**F5.2 — `ffmpeg` refuses the fifo for a different reason** (no muxer is
inferrable from a `.fifo` extension), so its refusal is *not* evidence about pipe
writes; it must be recorded as a name-axis failure, not a pipe failure.

**F5.3 — sink/path edges are named failures everywhere; nothing silently
succeeds.**

| cell | pw-record | parecord | arecord | ffmpeg |
|---|---|---|---|---|
| `/dev/full` | rc 1 `System error : No space left on device.` + `open failed: Input/output error` | rc 1 `Failed to open audio file.` | rc 1 `arecord: begin_wave:2773: write error` | rc 234 (no muxer for `/dev/full`) |
| `/dev/null` | streams forever (rc −9 @4.013 s) | streams forever (rc −9 @4.013 s) | rc 0 (30 s of audio written in 0.02 s) | rc 234 |
| directory as target | — | — | rc 1 `…out: Is a directory` | — |
| unwritable path (`/proc/self/nope.wav`) | — | — | rc 1 `…: No such file or directory` | — |

---

## 6. Load replays

**F6.1 — class invariance under concurrency and CPU load.** 8 concurrent ladder
cells (`load8-*`, one class per target) and 4 ladder cells under 16 CPU hogs
(`loadcpu16-*`): every class identical to the serial run (pw rc 1/finalised;
parecord rc 0/44 B; arecord-null completed; ffmpeg rc 255/0xFFFFFFFF), walls
1.525–1.645 s (no inflation), **0 harness kills inside the load cells**. No
contention artifact appeared.

**F6.2 — replay identity.** Across 4 ladder reps: 9/14 cells byte-identical in
signature (rc, alive flags, header fields, size), 4 more stable in class with
timing-dependent sizes, 1 bimodal (§3.4). Full-receipt sha256 with timing fields
excluded differs per rep *only* through the timing-dependent sizes — i.e. the
**classes** replay, the **byte counts** do not (they are wall-clock TERM timing,
not drift).

---

## 7. Roundtrip gate (stretch) — viable, pulse-leg only

`rt` group + `logs/…`; player `pw-play corpus/artifacts/stem_sections.wav`
(4.000 s, 192 000 frames) into the default sink, capture started 0.8 s later for
2.5 s.

| capture | rc | payload | samples | peak | RMS |
|---|---|---|---|---|---|
| `parec -d @DEFAULT_MONITOR@` — **silence control** (nothing playing) | −9 (harness) | 131 116 B | 65 536 | **0.000000** | **0.000000** |
| `parec -d @DEFAULT_MONITOR@` — member playing | −9 (harness) | 131 116 B | 65 536 | 0.125854 | **0.061736** |
| source member `stem_sections.wav` (4.000 s) | — | 384 044 B | 192 000 | 0.172363 | 0.070254 |
| `pw-record --target <monitor>` (same window) | **1** | 44 B | — | — | `no target node available` |

**F7.1** The monitor roundtrip **works on this host**, and the silence control is
*exactly* zero — so a nonzero capture is signal, not dither. The two captures are
byte-different (sha256 `d1ada02e…` vs `dd0fc8e3…`) at identical size, i.e. the
payload differs although the flush boundary is identical.

**F7.2** The native leg cannot reach the monitor at all (no monitor node exists;
`--target <sink>` also refuses). The roundtrip cell must therefore be built on
`parec`/`ffmpeg -f pulse`, or on the scout's `-P stream.capture.sink=true`
workaround.

**F7.3 (honest scope)** My windows do not match the member's, so the RMS
difference (0.0617 vs 0.0703) is **not** a level-match claim — only the
class-level claim (nonzero vs digital silence) is made here. r76-scout §7 has the
stronger matched-window result (identical peak −15.27 dBFS, two-section envelope
reproduced).

---

## 8. Cross-check against r76-scout (same wave, same host, overlapping window)

| item | scout | boundary | resolution |
|---|---|---|---|
| `pw-record` name axis | §4 "**flag-driven, name-blind**" | `.wav`→RIFF; `.raw`→**headerless 96 000 B**; `.bin`/`.foo`→RIFF (WAV fallback); `.flac`→**FLAC 172 B** (ffprobe `codec=flac`, 0.5 s); `--container wav` into `.raw`→RIFF; `-a`→headerless | **scout's row is falsified by the no-flag extension cells** (`name-pw-n_*`, run `…-name`). pw-record is **extension-driven with a WAV fallback**, and `--container`/`-a` override it |
| SIGTERM finalisation | §3 "SIGTERM finalizes the header for **all four** consumers" | ffmpeg TERM₁ → `0xFFFFFFFF` in 13/14 cells (`soxi -D` = 0.000 s); arecord TERM₁ → pre-declared duration (218× over) | **conditional, not universal**: libsndfile finalises; alsa-utils pre-declares; lavf leaves the placeholder (1/14 race exception) |
| arecord KILL placeholder | §3 `data=0x80000000` → stdlib `wave` reports 536 870 912 frames | reproduced, and explained: that is the **no-bound** placeholder; with `-d N`/`-s N` the same file declares **N seconds** instead | both correct; the declaration is bound-dependent |
| arecord TERM rc | §3 `rc=1` + finalised `data=216136` | rc −15 + stale declaration in 3/5 reps; rc 1 + consistent in 2/5 | **phase race**, not a contradiction |
| `arecord -D default`/`pipewire` blocked for capture | §1 blocked | §1.2 blocked (1 ch and 2 ch) | agree |
| monitor route | §1 `pw-record --target <sink> -P stream.capture.sink=true` viable | plain `--target <sink>` and `--target <sink>.monitor` fail; pulse route works; no monitor node in `pw-dump` | agree; scout supplies the native workaround |
| `parec` flush granularity | §5 64 KiB | §3.5 65 536 B (gcd over 6 partials) | agree |
| roundtrip | §7 positive, matched windows | §7 positive + **digital-silence control** | agree, complementary |
| rc is never the verdict | §3 confirmed ×4 | §2.3 pw-record rc=1 in 42/48 cells, 20 with complete files | agree, sharpened |

---

## 9. Carried guards — status after this seat

| guard | status |
|---|---|
| reorder topology = fd1-OWNER's buffering mode | **new instances, capture direction**: partial sizes are 4096 B (pw-record), 65 536 B (parecord), period-sized (arecord), ≥262 144 B (ffmpeg) granular. A "captured bytes" verdict on a short leg measures the flush boundary. |
| fifo-adjacent cells: `timeout -s KILL` is the kill bound; receipt completeness is the verdict carrier | **confirmed and extended**: the *outer* wrapper alone does **not** bound an orphan (finding 10); the bound must live inside the cell argv. Receipt completeness is exactly what fails on a writerless fifo for all three file writers. |
| `alive_after_term1` = ONE-TERM survival only | **honoured**: one survival observed (`ffmpeg` early), TERM₂ sent, killed by TERM₂, no immunity claimed. |
| a verdict group of ONE identical-errored signature is vacuous invariance | **avoided**: 7 targets carry ≥5 distinct (rc, header) signatures, and the two bimodal cells are reported as bimodal rather than collapsed. |
| lavf wound partition 3-valued, gated on AVFMT_NOGENSEARCH | **not exercised** (no demuxer cell in this arm); the capture direction adds a different partition — **buffer-granular wound** (0 B before the first flush; `0xFFFFFFFF` after). |
| rc alone is never a verdict | **confirmed ×4** (pw-record rc 1 + complete file ×20; parecord rc 0 + 0 bytes; arecord rc −15 + 300 s declaration; ffmpeg rc 255 + 0-byte or `0xFFFFFFFF` file). |
| consumer forks are member-local | **confirmed, new axis**: the fifo-output class is consumer-local (refuse / SIGPIPE / muxer-refusal) and the *bound unit* is consumer-local. |
| `io.DEFAULT_BUFFER_SIZE` / bpy guards | not exercised (no Python consumer in this arm). |

---

## 10. Remaining unknowns

1. **Mechanism behind `pw-record`'s constant rc=1.** `-v` shows a complete,
   error-free stream; no LSP/source trace was possible. *Observation only.*
2. **Why ffmpeg survives TERM₁ in the early phase** (4/4) but not mid-capture.
   *Inference:* the SIGTERM flag is not polled before the main loop starts.
3. **The exact cause of `parecord`'s ≈1.9 s dead start** (stream-start latency vs
   suspend/resume vs first-fragment wait). `--latency-msec=10` removes it;
   mechanism unmeasured.
4. **Why the PipeWire ALSA plugin's capture path is unusable** (`-D default` /
   `-D pipewire`) while its playback path works. Only the plugin's own
   hw-params dump is available as a witness.
5. **Version scope**: the native-monitor asymmetry (no monitor node) is bounded
   to libpipewire 1.6.8 / WirePlumber as shipped here; not tested against other
   PipeWire versions.
6. **`arecord` header update atomicity** (two writes vs one) is an inference from
   two observed header states (consistent-but-overstated vs inconsistent); it was
   not instrumented directly.

---

## 11. Receipts

Scratch root: `corpus/live/r76-boundary/`.

| path | contents |
|---|---|
| `probe_boundary_r76.py` | harness (sha256 `440468fc…4e05`); groups `gates bounded probe2 decl sever sever-early name fifo load loadcpu rt` |
| `verdicts.py`, `runs/verdicts-r76/verdicts.json` | derived lattice over all 229 cells |
| `runs/20261014T173229Z-boundary-r76-gates2/` | 37 gate cells + `env.txt` (versions, `pactl`, `arecord -l/-L`, `pw-link -o`, `pw-dump` node inventory, fixture sha, HEAD) |
| `runs/20261014T173145Z-boundary-r76-name/` | 24 name-axis cells |
| `runs/20261014T173629Z-boundary-r76-main3/` | bounded + sever + sever-early + fifo + rt + load + loadcpu |
| `runs/20261014T173845Z…sevrep1/`, `…173856Z…sevrep2/`, `…173909Z…sevrep3/`, `…174021Z…sevrep4/` | 4 independent ladder reps |
| `runs/20261014T173955Z-boundary-r76-fifo2/` | 22 fifo/sink edge cells with reader statistics |
| `runs/20261014T174112Z-boundary-r76-decl/` | arecord declaration matrix (`-d`/`-s` presence) |
| `runs/20261014T173319Z-boundary-r76-main/` | probe2 (8 s wall-vs-audio ratios, `--target` id cells) + bounded (pre-fix) |
| `edge/partials-r76/{*.wav,usability.json}` | the killed partials (<1 MB) + the two-reader usability table (the >50 MB null-device partials were receipted here and then deleted) |
| `logs/{partial-usability,flush-block,ffmpeg-header-states,aggregates,fifo-earlyexit-pin,verdicts.md}.txt` | derived tables, hand pin, run logs |
| `out/`, `rt/` | raw capture outputs and fifos (70 MB retained) |

Reproduce: `cd corpus/live/r76-boundary && timeout -s KILL 1500 python3
probe_boundary_r76.py gates bounded probe2 decl sever sever-early name fifo load
loadcpu rt --concurrency 4 --run recheck` then `python3 verdicts.py`.

**Bounded claims.** Every number above is this host (`plazir27`, Linux
7.2.3-arch1-3), these versions (libpipewire 1.6.8, pacat 17.0-98-gb096/libpulse
17.0.0, alsa-utils 1.2.16, ffmpeg n9.0.1/lavf 63.1.101, sox/soxi as shipped),
this live PipeWire session, 2026-10-14 17:29Z–17:45Z, with the fixture
`measure_audio.py` at `ebecea00…f948` (no `--probe-capture-r76` arm present).
