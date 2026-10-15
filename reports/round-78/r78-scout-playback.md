# R78 scout (playback) — the WRITE-side selection lattice

Round 78, playback frontier. Host `plazir27`, measured 2026-10-14 ~17:50–18:30 UTC.
Repo `~/Projects/shokunin/audio-shokunin` @ HEAD `503689cecd96997e7509a967f2c1371e43b5066c`.

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/r78-scout-playback/` plus this report.** Own harness
(`r78p.py` + 13 probe drivers), own classifiers — `corpus/fixtures` was never
imported (a sibling seat is editing `measure_audio.py` concurrently; this seat
never read it). This seat wrote nothing under `corpus/artifacts` or
`corpus/fixtures`: all 17 tracked artifact wavs verify **byte-identical to HEAD**
(`git status --porcelain corpus/artifacts/` empty), and the fixtures dirty state
predates this seat (§8 provenance).

Toolchain (this host, this session): PipeWire **1.6.8**, pw-cat/pactl
**17.0-98-gb096** (libpulse 17.0.0, protocol 35), alsa-utils **1.2.16**,
ffmpeg **n9.0.1**, Python **3.14.7**, Linux **7.2.3-arch1-3**. Default sink
`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink`, default source the
DualSense mic.

**Method (playback has no output artifact).** Every leg is judged by two
independent witnesses:
* **topology** — `pw-link -l` consumers of `<tag>:output_*` (names the port pair);
* **content** — concurrent `pw-record -P stream.capture.sink=true --target <sink>`
  captures of 5 candidate sinks (2 probe-owned null sinks + SPDIF + Speaker +
  HDMI). The tone is tagged per leg (`node.name=r78p<leg>`) and is
  **frequency-strict**: L 1 kHz / R 1.5 kHz, amp 8192, 48 kHz s16. A window
  counts as *mine* only if the FFT peak of both channels matches within 6 % and
  the amplitude is in range; anything else is labelled FOREIGN (§6.1).
  Captures are analysed over the **whole file** in 0.25–0.5 s windows, so the
  second an event happens is measured, not inferred.

---

## 0. Headline — the brief's four questions

| # | question | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | same fallback lattice as capture? | **YES — but ungated and observable** | every unresolvable/inapplicable target (`garbage`, `default`, `pulse`, `@DEFAULT_*@`, a *source* name, a `.monitor` name, `""`, absent) lands the **current default sink**: rc=0, empty stderr, real-time playout, consumers = `<default>:playback_FL/FR`. No prop gate (capture's fallback needs `stream.capture.sink=true`), no error class — **only topology/content separates honored from fallback** |
| 2 | does `target.object` lie on playback too? | **YES — reproduced** | `--target no_such_sink_xyz` → the live node advertises `target.object="no_such_sink_xyz"` while its ports feed SPDIF. `pw-dump` is intent; `pw-link -l` is consumption |
| 3 | does removing the target sink mid-playback re-link? | **YES — to the default sink, silently** | `pactl unload-module` of the target at 2.0 s: consumers switch to SPDIF's playback ports, the SPDIF monitor carries the tagged tone 2.0→6.0 s, rc=0 at the full 6.05 s, stderr empty. A manual `pw-link -d` instead gives **no** re-link and still rc=0 after the full file duration |
| 4 | where does aplay's device axis differ from arecord's? | **5 measured differences** | `default`/`pipewire` are the PipeWire ALSA plugin for both (`alsa_playback.aplay` / `alsa_capture.aplay`) and **follow the current default sink**; `hw:*` bypasses the graph entirely; aplay adapts the *file* (`Warning: format is changed to S16_LE`) while arecord demands the *device* format; `-D null` is not rate-limited in either direction; and `hw:0,0` has different capability sets per direction (play 2–8 ch + S32_LE, capture stereo-only) |

Plus three new laws and one crash class the brief did not ask for: the
**prop-precedence law on the write side**, the **`--target 0` pin law**
(playback twin of r78's capture pin), **`pactl move-sink-input` works
mid-playback** (the capture side's move is degenerate), and
**`-P media.class=<non-output class>` SIGSEGVs pw-play** (3/3 reproducible).

---

## 1. Q1 — the playback target lattice (`probe-play-lattice-strict-r78p.json`)

`pw-play -P node.name=r78pA_<leg> <target args> tone.wav` (1.6 s), 5 witnesses,
topology sampled every 0.4 s, 25 legs + 1 no-consumer control.

| `--target` | consumers of my ports | tone on | verdict |
| --- | --- | --- | --- |
| `r78p_ns` (probe null) | `r78p_ns:playback_F{LR}` | ns | honored |
| `r78p_ns2` | `r78p_ns2:playback_F{LR}` | ns2 | honored |
| `Speaker__sink` / `SPDIF__sink` / `hdmi-stereo` | that sink's `playback_F{LR}` | that sink | honored |
| `no_such_sink_xyz` | **SPDIF** `playback_F{LR}` | **SPDIF** | **fallback** |
| `r78p_ns_absent` (sink not loaded) | SPDIF | SPDIF | fallback |
| `default` / `pulse` | SPDIF | SPDIF | fallback |
| `@DEFAULT_SINK@` / `@DEFAULT_MONITOR@` / `@DEFAULT_SOURCE@` | SPDIF | SPDIF | fallback |
| `Line` source name / `Mic` source name | SPDIF | SPDIF | fallback |
| `r78p_ns.monitor` / `SPDIF__sink.monitor` | SPDIF | SPDIF | fallback |
| `""` (empty) / **no `--target` at all** | SPDIF | SPDIF | fallback (auto) |
| `0` (with and without `-n 48000`) | **none** | none | `target_0_unlinked` + stall |

* Every honored and every fallback row shares **rc=0, empty stderr, full-length
  real-time playout, and one of the two RIFF-free observables**. `--target 0`
  publishes `output_FL/FR` and never links them: the node is
  `state: "suspended"`, the file is **not consumed** (no exit within the 9–10 s
  bound for a 1.6 s file), all witnesses silent.
* **The fallback follows the CURRENT session-manager default, not SPDIF.** After
  `pw-metadata -n default 0 default.audio.sink '{"name":"…Speaker__sink"}'`,
  `no_target`, `garbage`, `@DEFAULT_SINK@` and `default` all moved to the
  Speaker monitor, and moved back after restoring SPDIF
  (`probe-play-fallback-semantics-r78p.json`, `probe-play-defaults-pin-r78p.json`).
* **Trap: `pactl set-default-sink <name>` returns rc=0 and changes nothing on
  this host** (verified twice: `pactl get-default-sink` and the
  `default.audio.sink` metadata both unchanged, before and after the switch).
  My first "fallback follows the default" run was vacuous because of it; the
  native `pw-metadata` switch is the working verb.
* Control leg (no consumer, 2.6 s): **all five witnesses silent** — the witness
  set has no crosstalk, and every honored leg lights exactly one monitor.

**Delta vs capture (r77/r78):** capture's fallback is *gated* on
`stream.capture.sink=true` and *invisible* (same rc, same byte count, same
finalized header); playback's fallback is *ungated* and *visible in topology*
— but still invisible in rc/stderr/exit timing, so an arm that only reads those
three fields cannot tell "played to my sink" from "played to the default sink".

---

## 2. Q2 — `target.object` provenance, props, numeric axis, and a crash
(`probe-play-props-r78p.json`, `probe-play-class-serial-r78p.json`,
`probe-play-numeric-target-r78p.json`, `probe-play-late-pin-r78p.json`)

### 2.1 `target.object` is intent, not consumption
`--target no_such_sink_xyz` → live props
`{target.object: "no_such_sink_xyz", node.autoconnect: true, media.class:
Stream/Output/Audio}` while `pw-link -l` shows SPDIF's `playback_F{LR}` fed by
my `output_F{LR}` and the SPDIF monitor carries the tone. Same for a source
name and for a `.monitor` name. **The r77 capture-side provenance trap is
reproduced on the write side, unchanged.**

### 2.2 Precedence and decoration (write side)
| leg | tone on | verdict |
| --- | --- | --- |
| `--target ns` + `-P target.object=ns2` | **ns2** | prop beats flag |
| `--target ns2` + `-P target.object=ns` | **ns** | prop beats flag (both directions) |
| `-P target.object=ns` (no flag) / `-P node.target=ns` | ns | prop routes |
| `--target no_such` + `-P target.object=ns` | ns | prop beats a garbage flag |
| `-P target.object=no_such` / `-P node.target=no_such` | SPDIF | prop falls back like the flag |
| `PIPEWIRE_PROPS='{ target.object=ns2 }'` + `--target ns` | ns2 | env is a second prop vector, same precedence |
| `-P media.role=Communication` / `=Production` | ns | decoration |
| `-P stream.monitor=true` / `stream.capture.sink=true` / `stream.playback.sink=true` (invented) | ns | decoration — **the capture-only prop has no write-side effect** |
| `-P media.class=Stream/Output/Audio` | ns | explicit correct class |
| `-P media.class=Audio/Source` | none | **unlinked stall** (rc=None at 9.6 s) — same as r78's capture row |
| `-P node.autoconnect=false` | none | **honored: never links**, stall, rc=None at 9.6 s |

### 2.3 NEW — class-override SIGSEGV (`class_override_segv`)
`pw-play -P media.class=Audio/Sink --target r78p_ns tone.wav` → **rc=−11
(SIGSEGV), wall 1.47 s, empty stderr, no node ever published**; reproduced
**3/3** at the identical wall time. Same shape for `media.class=Stream/Input/Audio`,
`Audio/Duplex`, `Audio/Bogus`. Only `Stream/Output/Audio` behaves normally and
`Audio/Source` stalls. The crash is a function of the class value, not of the
target: the same binary with the same target and the correct class plays fine in
the adjacent leg.

### 2.4 Numeric target axis (clean, single-instance sinks)
`--target <object.serial>` resolves; `-P target.object=<serial>` resolves as
int **and** as string; `--target <node id>` does **not** (falls back to the
default sink) and `-P target.object=<id>` does not either (the prop records the
raw number and the stream lands on the default sink). So "serial" in pw-cat's
help means `object.serial`, never the node id.

### 2.5 Pin law — playback side (r78's pin law is consumer-agnostic)
`--target 0` publishes `output_FL/FR`, is `state: "suspended"`, and stalls.
A manual `pw-link <tag>:output_FL <sink>:playback_FL` (+FR):
* pinned **immediately** → stream goes `running`, file consumed at real-time
  rate, tone windows 0.25→2.0 s, rc=0 at 1.67 s;
* pinned **after a 1.5 s stall** → same: `running`, tone windows 1.75→3.5 s,
  rc=0 at 3.67 s (≈ stall + file duration);
* pinning a **second** sink onto the same ports fans the tone out to both
  monitors simultaneously (ns from 1.75 s, SPDIF from 2.5 s) — one producer,
  two sinks, both carrying the same tagged tone.

---

## 3. Q3 — mid-playback loss, re-link, and the session-manager verbs
(`probe-play-loss-c2-r78p.json` — **one fresh sink per leg**; C1 was invalidated
by a cascade and is kept only as a receipt)

| # | event at t=2.0 s (6 s tone) | tone on own sink | tone on default sink | rc / wall | verdict |
| --- | --- | --- | --- | --- | --- |
| 1 | `pactl unload-module` of the target sink | 0.0–6.0 s (see note) | **2.0–6.0 s** | 0 / 6.05 s | **re-links to the default sink, plays on** |
| 2 | `pw-link -d` both links | 0.0–2.0 s, then silent | never | **0 / 6.05 s** | **`unlinked_sustained_playout`** — no re-link, no stall |
| 3 | `pactl move-sink-input <idx> Speaker` | 0.0–2.0 s | — | 0 / 6.05 s | move works mid-playback (tone on Speaker 2.0–6.0 s, consumers follow) |
| 4 | `move-sink-input` → `no_such_sink` | 0.0–6.0 s | never | 0 / 6.05 s | rc=1 `Failure: No such entity`, clean no-op |
| 5 | native default → Speaker | 0.0–6.0 s | never | 0 / 6.05 s | **active stream does not follow a default change** |
| 6 | `pactl suspend-sink <own> 1` | 0.0–6.0 s | never | 0 / 6.06 s | no effect on the flow |
| 7 | `pactl set-sink-mute <own> 1` | **0.0–2.0 s, then zeros** | never | 0 / 6.05 s | **the monitor tap is post-mute** — a muted sink is invisible to the content witness |
| 8 | unload + re-create the same sink name | 0.0–6.0 s | 2.0–2.5 s only | 0 / 6.16 s | falls back, then **re-links to the re-created same-named node** |

Note on row 1: after the target node dies, the *own* witness (a name-targeted
capture whose target no longer exists) silently becomes a **default-sink
witness** (§6.5), so the honest evidence for the re-link is the SPDIF witness
carrying the tagged tone from 2.0 s to the end of the file. Row 8 is the same
mechanism read twice: the SPDIF witness stops at 2.5 s exactly when the
recreated same-named sink appears.

Row 2 is the important negative: a manually unlinked playback stream
**consumes the entire file at real-time rate into nowhere** — rc=0, wall time
identical to a healthy run, stderr empty, and after the process exits there is
nothing left to inspect. It is r78's `unlinked_sustained_zeros` with the zeros
*and the artifact* removed.

---

## 4. Q4 — aplay's device axis vs arecord's
(`probe-aplay-axis-r78p.json`, `probe-aplay-axis-d2-r78p.json`,
`probe-aplay-pcm-map-r78p.json`)

### 4.1 The mapping (from PipeWire's own node props, not inferred)
| PipeWire sink/source | ALSA PCM (`api.alsa.path`) | card/dev |
| --- | --- | --- |
| Speaker | `hw:Audio,0` | card 0 dev 0 |
| Headphones | `hw:Audio,1` | card 0 dev 1 |
| Mic (source) | `hw:Audio,2` | card 0 dev 2 |
| SPDIF | `hw:Audio,3` | card 0 dev 3 |
| Line (source) | `hw:Audio,1` | card 0 dev 1 |
| HDMI | `hdmi:1` | card 1 dev 3 |

### 4.2 Direct ALSA works — unless something holds the PCM
Unperturbed (no witnesses): `aplay -D hw:0,0|hw:0,1|hw:0,2|hw:0,3|plughw:0,0|
plughw:0,1|sysdefault|front:CARD=Audio,DEV=0|iec958:CARD=Audio,DEV=0|
surround51:CARD=Audio,DEV=0` → **all rc=0**, real-time (1.28–1.39 s), **no new
PipeWire node and no monitor carries the tone** → the direct path bypasses the
graph entirely. (Node diff measured directly in the successful case:
`probe-direct-alsa-nodediff-r78p.json` — `aplay -D hw:0,1` and `-D hw:0,0`
each rc=0 with `new_nodes: []`.)

With a monitor witness on the same PCM: `aplay -D hw:0,0` → rc=1
`audio open error: Device or resource busy` (Speaker witness), `hw:0,1` EBUSY
(Headphones witness), `hw:0,3` EBUSY (SPDIF witness); an HDMI witness (other
card) blocks nothing on card 0. Corroborated with active streams: a PipeWire
playback into SPDIF blocks `hw:0,3`, into Speaker blocks `hw:0,0`.

**The lock outlives the stream (`alsa_lock_retention`):** after a 1.2 s PipeWire
playback to Speaker ends, `aplay -D hw:0,0` is EBUSY at **+1 s** and rc=0 at
**+7 s** (same for hw:0,1). My first lattice run read "every `hw:` leg is
EBUSY" — that was the previous leg's lock, not the device's normal state.

### 4.3 Same PCM, different capability sets (`--dump-hw-params`)
| PCM | playback | capture |
| --- | --- | --- |
| `hw:0,0` | FORMAT `S16_LE S32_LE S24_3LE`, **CHANNELS [2 8]**, RATE [44100 192000] | FORMAT `S16_LE S24_3LE`, **CHANNELS 2**, RATE [44100 192000] |
| `hw:0,1` | FORMAT `S16_LE S32_LE S24_3LE`, CHANNELS 2, RATE [44100 384000] | CHANNELS 2, RATE [44100 192000] |
| `hw:0,2` | FORMAT `S16_LE S24_3LE`, CHANNELS 2 | CHANNELS 2 |
| `hw:0,3` | FORMAT `S16_LE` only, CHANNELS 2 | **no capture params** (playback-only) |

r77's "`arecord -D hw:0,0` is stereo-only" is reproduced — and the *playback*
direction of the same PCM accepts 2–8 channels. `arecord -D hw:0,0 -f cd` /
`-f dat` → rc=0 (1.04 s); with arecord's default request (u8/8k/mono) →
rc=1 `Sample format non available` / `Channels count non available`.

### 4.4 aplay adapts the file; arecord does not adapt the device
Every format request on `hw:0,0`, `hw:0,1`, `sysdefault`, `default`, `pipewire`
was accepted (rc=0), with `Warning: format is changed to S16_LE` where the
device refused the request (`-f FLOAT_LE`, `-f S24_3LE`). The only refusal is a
pre-open one: `-f BOGUS` → rc=1 `aplay: main:638: wrong extended format 'BOGUS'`,
wall **0.00 s**, device never touched. On the capture side the same request set
on `hw:` fails unless it matches the device (`Sample format non available`,
`Channels count non available`) — aplay converts, arecord constrains.

### 4.5 `default` / `pipewire` are the PipeWire plugin on both tools
`aplay -D default --dump-hw-params` reports device **`alsa_playback.aplay`**
and `arecord -D default …` reports **`alsa_capture.aplay`**; the exposed range
is the plugin's (`FORMAT U8 S16_LE S24_LE S32_LE FLOAT_LE S24_3LE S24_3BE`,
CHANNELS [1 128], RATE [1 384000]), not the hardware's. Both **follow the
current default sink**: `aplay -D default` → SPDIF tone with default=SPDIF,
→ Speaker tone after the native default switch; `aplay -D pipewire` identical.
This is the sharpest axis difference from `hw:` (a fixed PCM) and from the
pulse-protocol consumers.

### 4.6 `null` is not rate-limited in either direction
`aplay -D null` finishes a 1.2 s file in **0.00 s** (discard, no pacing);
`arecord -D null` **without** `-d` runs away — one invocation wrote a 2 GiB
segment chain (`file-01…-05`, `data_declared` `0x7fffffff` then `0x80000000`,
i.e. r77's 2 GiB split sentinel reproduced from a second device) and then
exited rc=1. With `-d N` the null device stays the exact-arithmetic oracle
(r77's row). `-D pulse` → `Unknown PCM pulse` on both tools (r77's row).

### 4.7 An r78 row this session does NOT reproduce
r78's scout recorded `arecord -D pipewire` / `-D default` → rc=1
`TICK_TIME: [0 0]`, class `alsa_tick_time`, no file. In this session both PCMs
record fine: `-d 2 /dev/null` → rc=0 (2.05 s, real-time); `-d 2 <file>` → rc=0
(16044 B u8/8k/mono; 352844 B with `-f cd`); **unbounded** → rc=None at my 6 s
bound with 47044 B written (i.e. it recorded, no TICK_TIME, no missing file).
The plugin capture path is rate-limited (~176 KB/s, measured). r78's report does
not record its exact invocation, so the difference cannot be named from the
artifact — the row is falsified *as stated* for this host state, not explained.

---

## 5. Cross-consumer parity — the lattice is consumer-agnostic
(`probe-cross-consumer-playback-r78p.json`, `…-e2-…`, `probe-ffmpeg-pulse-output-r78p.json`)

| consumer | honored target | garbage / source name / `.monitor` / alias | rc / wall |
| --- | --- | --- | --- |
| `paplay --device <sink>` | that sink's monitor | **default sink** (`no_such_sink`, `Line` source, `<ns>.monitor`, `@DEFAULT_SINK@`, `default`) | 0 / ~1.28 s, stderr empty |
| `pacat -p --device <sink> --format=s16le --rate=48000 --channels=2 <raw>` | that sink | **default sink** (`no_such_sink`, `Line`, `@DEFAULT_SINK@`) | 0 / ~1.29 s |
| `ffmpeg -f pulse -device <sink>` | that sink | **default sink** (`no_such_sink`) | 0 / 0.72 s |
| `pw-play --target <sink>` | that sink | **default sink** | 0 / real-time |

Four independent write-side consumers share one lattice and one failure shape.
(ffmpeg needed `-f wav` — see §6.6; its first two attempts never reached
PipeWire and are kept as vacuous receipts.)

---

## 6. Method hazards — five traps, three of them my own errors

*(Also live on this host at seat exit, not mine and not killed: a stray
`aplay -D null /tmp/nowriter-r75-*/nowriter.wav` from `corpus/live/r77-baseline`
(cwd-attributed, started 17:12, still spinning at 18:22), and the `love_battery.py`
clients of item 1. Both are named so a later arm does not attribute them to this
seat.)*

1. **FOREIGN-tone alias.** A concurrent lane's probe tone (amp ≈ 4096, 1 kHz
   stereo) appeared on the default-sink monitor mid-run; my first classifier
   (peak ≥ 512 + nonzero fraction) read it as *my* tone and reported the SPDIF
   monitor as carrying audio in legs that never touched SPDIF. Source identified
   at seat exit: PipeWire clients with `application.name=love`,
   `media.name="Playback Stream"`, spawned by `vbat|vprobe|vfold/love_battery.py`
   (a sibling lane's LÖVE-based battery, still live on the default sink). Fixed
   by frequency-strict classification (this seat's tag tone is L 1 kHz / R 1.5 kHz
   at amp 8192; FFT of the active span, 6 % tolerance, amplitude range). A
   peak/nonzero test is **not** a content witness on a shared default sink.
2. **Analysis-cap truncation (my error, hypothesis killed).** My reader capped
   each capture at 256 KiB ≈ the first 1.36 s, so every *late* event (a pin at
   1.5 s, a loss at 2.0 s, a 6 s tone) analysed as silence. I provisionally
   named `linked_but_silent_after_late_pin`. Re-measured over the whole file,
   the late pin **does** carry audio (windows 1.75→3.5 s, peak 8192, 1 kHz/1.5 kHz)
   — the class is retracted; the surviving law is §2.5. Recorded because the
   byte-identity/truncation trap is what a later arm would fall into.
3. **Duplicate-sink-name artifact (my error).** An earlier crashed probe leaked
   a second null sink with the same `node.name`; a *name*-targeted monitor
   witness and a *serial*-targeted stream then resolved to different nodes, which
   reads exactly like "linked but silent". After `unload_all_mine()` and a
   single-instance re-measure, serial targeting resolves correctly (§2.4).
   Every probe now unloads all probe-owned sinks before **and** after itself.
4. **Witness observer effect + `alsa_lock_retention`.** A monitor capture holds
   the ALSA PCM it taps, so the witness needed to observe the direct-ALSA path
   is what breaks it (EBUSY), and the lock lingers ~1–7 s after any PipeWire
   stream on that sink ends. The honest read of the direct path is "no PipeWire
   node + real-time wall time + no monitor content", with the witness **off**.
5. **Witness fallback trap.** A monitor witness aimed at a sink that does not
   exist is not a null witness: `stream.capture.sink=true --target <missing>`
   silently captures the **default sink's monitor** (r77's capture-side fallback
   law). Observed directly: after the target sink was unloaded, the "own" witness
   carried the SPDIF tone. Any arm that destroys a sink must expect its witness
   to defect to the default sink.
6. **ffmpeg format misprobe.** This seat's periodic dual-tone wav probes as
   **`mpegts` (score 100) over `wav` (99)** in ffmpeg n9.0.1 and fails
   `could not find codec parameters`; `ffprobe`/`soxi` read the same file
   correctly. `-f wav` fixes it. The repo's own artifacts probe as wav — the
   misprobe is content-dependent. Two ffmpeg legs were vacuous until forced.
7. **`pactl set-default-sink` is a silent no-op here** (rc=0, nothing changes)
   while `pw-metadata -n default 0 default.audio.sink '{"name":…}'` works.
   An arm that switches the default with pactl measures a stale default.

---

## 7. Named classes added this round

| class | shape | trigger |
| --- | --- | --- |
| `playback_default_fallback` | rc=0, empty stderr, real-time, consumers = default sink ports | any unresolvable/inapplicable `--target` (ungated) |
| `target_0_unlinked` (playback) | ports published, zero links, node `suspended`, file never consumed | `--target 0` |
| `class_override_segv` | **rc=−11**, wall 1.47 s, empty stderr, no node published, 3/3 | `-P media.class=` ∈ {`Audio/Sink`, `Stream/Input/Audio`, `Audio/Duplex`, `Audio/Bogus`} |
| `unlinked_sustained_playout` | rc=0, full-file wall time, stderr empty, consumers {} | `pw-link -d` mid-playback |
| `playback_relink_on_target_loss` | consumers switch to the default sink, playout continues to EOF | target node destroyed mid-playback |
| `alsa_lock_retention` | `aplay -D hw:` rc=1 `Device or resource busy` for ~1–7 s after a PipeWire stream ends | any PipeWire stream on that PCM (incl. a monitor witness) |
| `null_unpaced_capture` | 2 GiB split chain (`0x7fffffff`→`0x80000000`), rc=1 | `arecord -D null` without `-d` |
| `class_override_unlinked_stall` | zero links, rc=None, monitors silent | `-P media.class=Audio/Source` or `node.autoconnect=false` |

---

## 8. Receipts

All under `corpus/live/r78-scout-playback/` (seat footprint **48 MB**, 49 kept
witness captures + 20 probe JSONs). `sha256` prefixes (full digests on request):

| probe JSON | sha256[:16] |
| --- | --- |
| `probe-play-lattice-strict-r78p.json` | `3009595dffe3d101` |
| `probe-play-fallback-semantics-r78p.json` | `ddae2f9e2f708c76` |
| `probe-play-defaults-pin-r78p.json` | `b9c451323c12ce11` |
| `probe-play-props-r78p.json` | `2038c80e7e50d550` |
| `probe-play-class-serial-r78p.json` | `dfd4faed5bc7caaf` |
| `probe-play-numeric-target-r78p.json` | `52c86e555e7e148c` |
| `probe-play-late-pin-r78p.json` | `34b2f6996f759f3a` |
| `probe-play-loss-c2-r78p.json` | `2f92cf86f62f4308` |
| `probe-aplay-axis-r78p.json` | `787a520ba77c5777` |
| `probe-aplay-axis-d2-r78p.json` | `020970534e230bf8` |
| `probe-aplay-pcm-map-r78p.json` | `b2a0e972c9570b53` |
| `probe-direct-alsa-nodediff-r78p.json` | (node diff, successful direct-ALSA legs) |
| `probe-cross-consumer-playback-r78p.json` | `4c8114a47cc61872` |
| `probe-cross-consumer-playback-e2-r78p.json` | `9f52cfd94170501e` |
| `probe-ffmpeg-pulse-output-r78p.json` | `960b07e1dc78c680` |
| `probe-arecord-2gib-split-r78p.json` | `9b8bd6c270cc271f` |

Retracted/invalidated receipts are kept on disk and named as such:
`probe-play-lattice-r78p.json` (pre-frequency-strict pass),
`probe-play-loss-r78p.json` (C1, cascade-invalidated),
`probe-play-serial-vs-name-r78p.json` + `probe-play-serial-decoy-r78p.json`
(duplicate-name artifact), `probe-smoke-r78p.json` (harness self-test).

Host hygiene at seat exit: `pactl list modules short | grep r78p` → none,
no `r78p*` PipeWire nodes, no stray seat processes, the default sink and the
`default.audio.sink` metadata restored to SPDIF, `corpus/artifacts/*` hashes
unchanged, `corpus/fixtures/measure_audio.py` untouched by this seat (its dirty
state is a sibling seat's).

Provenance note on the shared tree: a concurrent lane regenerated
`corpus/artifacts/*.wav` at 18:14 during this session (mtimes moved;
`git status --porcelain corpus/artifacts/` is **empty**, so all 17 tracked wavs
are byte-identical to HEAD and no diff exists to inherit). `measure_audio.py`
was dirty before this seat started (`sha256 ac9b282e20311dce`, per the r78 scout
at 17:05) and is dirty again with a different digest
(`sha256 e5b00f60ee4fc309`) — a sibling seat's edit; this seat never read or
imported it, and every number here comes from this seat's own harness and
classifiers.

---

## 9. Remaining unknowns (honest edges)

1. **`class_override_segv` mechanism** — the class value is the trigger (3/3 at
   a fixed 1.47 s wall time) but no backtrace was taken (no debugger run in a
   scout seat); whether other PipeWire clients crash the same way is untested.
2. **Why the playback fallback is ungated** while capture's needs
   `stream.capture.sink=true` — session-manager policy internals; only the
   behaviour is measured, not the code path.
3. **Re-link on target loss was measured with a probe-owned null sink only** —
   destroying a *hardware* sink mid-playback was not attempted (that would take
   a device off the host), so the re-link law is stated for node destruction in
   general but proven on a null sink.
4. **The `alsa_lock_retention` boundary** is bracketed (+1 s EBUSY, +7 s free),
   not bisected; it is presumably the node suspend timeout, which was not read
   from configuration.
5. **Whether `aplay -D hw:` reaches the same physical output as the PipeWire
   sink backed by that PCM** is not measurable with a monitor witness (the
   witness causes the EBUSY) — only "no PipeWire node, real-time wall time" is
   evidence, not the physical destination.
6. **r78's unreproduced `alsa_tick_time` row** — its exact invocation is not in
   that report; I can falsify the row for this session but cannot name the
   difference.
7. **`paplay --device <numeric index>`** (as opposed to a name) untested;
   `--device <sink>.monitor` was tested and falls back.
8. **`pw-play`'s `--target` with a *client* name or `application.name`** untested
   (only node names, `object.serial`, node ids, and pulse aliases).
