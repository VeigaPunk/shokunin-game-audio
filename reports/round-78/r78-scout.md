# R78 scout — stream-props / link-graph / midi frontier pre-measurement

Round: 78 (pre-measurement for the next capture frontier). Host `plazir27`,
measured 2026-10-14 ~16:50–17:15 UTC. Repo `~/Projects/shokunin/audio-shokunin`
@ HEAD `503689cecd96997e7509a967f2c1371e43b5066c`. `measure_audio.py` is dirty
at sha256 `ac9b282e20311dce` (+1397/−2) — **the r77 author's concurrent edit;
this seat never imported `corpus/fixtures`.**

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/r78-scout/` + this report.** Own harness (`r78_probe.py` + five
probe drivers), own classifiers. All routing measurements run against a
**probe-owned null sink `r78_ns`** (loaded/unloaded per probe) with unique
`node.name=r78*` stream tags, so a concurrent seat's Speaker/SPDIF traffic
can never alias a `pw-link -l` witness or a tone anchor. Seat footprint
**~0.4 MB** (scratch trimmed; every leg triple-bounded: consumer flag,
subprocess timeout, reader cap).

Toolchain: PipeWire **1.6.8**, libpulse **17.0** (pactl 17.0-98-gb096),
alsa-utils **1.2.16**, ffmpeg **n9.0.1**, pipewire-jack **1.6.8**,
Python **3.14.7**, Linux **7.2.3-arch1-3**.

---

## 0. Headline: eight frontier claims

| # | frontier | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | prop routing lattice | **NEW LAW, pinned** | `target.object` set via `-P` **overrides the `--target` flag in both directions**; `media.role` (4 values) and `stream.monitor` are decoration; `media.class` override → unlinked 44 B |
| 2 | fallback asymmetry | **LAW NARROWED** | `stream.capture.sink=false` ≡ prop absent: garbage target → **44 B wav + ZERO links** — there is *no* default-source fallback; r77's "garbage → default monitor" only exists under `=true`. `.monitor` is a Pulse alias, not a node |
| 3 | `pw-link -d` mid-run | **NEW CLASS** | disconnecting a live link: file keeps growing at **exactly 100 % rate filled with zeros** (window peak 0), relink resumes the tone — link loss is invisible except in content |
| 4 | manual port pin | **NEW LAW** | `pw-record --target 0` publishes ports unlinked (44 B stall); `pw-link <mon>:port <stream>:input` starts the flow and `-n` then binds; **same pin works on ffmpeg's JACK ports** — pin law is consumer-agnostic |
| 5 | two producers → one port | **NEW LAW** | both links coexist and the input receives the **sample sum** (peak 23488 ≈ 12000+12000-tone mix) — PipeWire mixes on the input port |
| 6 | parec `--fix-*` | **NEW LAW + LIE** | `--fix-rate/format/channels` each **discard the request knob and adopt the source spec**, while the emitted wav header still records the **pre-fix** spec — `header_prefix_mismatch` |
| 7 | parec `--file-format` | **LATTICE + 2 refusal shapes** | 16 formats write real containers (flac 0 B @1.3 s is granule-delay → 57 KB valid `fLaC` @3.0 s); known-unwritable → `Failed to open audio file` + **0-byte file**; unknown name → `Unknown file format X` + **missing file** |
| 8 | JACK without jackd | **CONFIRMED + SHAPED** | `libjack.so.0` *is* pipewire-jack: `ffmpeg -f jack` works unshimmed, registers `<client>:input_N` ports, **auto-connects to nothing** → unlinked zeros at rate; manual `pw-link` pin then carries the tone |
| 9 | ALSA-seq / MIDI | **FIXTURE ROW EXISTS** | `aplaymidi -p 14:0` → `arecordmidi -p 14:0 -n 4` yields a valid 52-byte SMF through Midi Through; `pw-record -M midi` **cannot bind the bridge by name or serial** (`no_target_node` + 44 B wav) |
| 10 | ffmpeg/arecord alsa parity | **PARITY MEASURED** | both refuse `pipewire`/`default` PCMs (ffmpeg `ffmpeg_alsa`, arecord `TICK_TIME` — new class `alsa_tick_time`); `sysdefault`/`hw` work in both — and `hw:0,0` reads **analog noise floor** where the pulse path reads digital zeros |

---

## 1. FRONTIER 1 — the stream-props lattice (`probe-props-lattice-r78.json`)

Method: `r78_ns` null sink carries a dual-tone (L 1 kHz / R 1.5 kHz, amp
16384) via `pw-cat`; each `pw-record` leg gets `-P node.name=r78a_<leg>` so
`pw-link -l` names *this* stream's producers unambiguously. Tone witness =
payload peak; routing witness = producer port set.

| leg (all `-n 48000`, tone playing) | producers feeding my ports | peak | verdict |
| --- | --- | --- | --- |
| `-P stream.capture.sink=true --target r78_ns` | `r78_ns:monitor_F{LR}` | 16384 | baseline honored |
| `+ -P media.role={Communication,Production,DSP,Music}` | same | 16384 | **decoration ×4** |
| `-P node.target=r78_ns` (no `--target`) | `r78_ns:monitor_F{LR}` | 16384 | **node.target routes** |
| `-P node.target=no_such` | **SPDIF `monitor_F{LR}`** | 5648 | routes → fallback |
| `-P target.object=r78_ns` (no `--target`) | `r78_ns:monitor_F{LR}` | 16384 | **target.object routes** |
| `--target r78_ns -P target.object=no_such` | **SPDIF monitor** | 5648 | **prop beats flag** |
| `--target no_such -P target.object=r78_ns` | `r78_ns:monitor` | 16384 | **prop beats flag** |
| `-P stream.capture.sink=false --target r78_ns` | *(none)* | 44 B | **unlinked** |
| `-P stream.capture.sink=false --target r78_ns.monitor` | *(none)* | 44 B | **unlinked** |
| *(no -P)* `--target r78_ns` / `r78_ns.monitor` | *(none)* | 44 B | **unlinked** |
| *(no -P)* `--target <LINE source>` | `Line:capture_F{LR}` | 0 | real source, silent host |
| `-P stream.capture.sink=false --target <LINE>` | `Line:capture_F{LR}` | 0 | false ≡ absent |
| `-P stream.capture.sink=false --target no_such` | *(none)* | 44 B | **no fallback** |
| `-P stream.capture.sink=true --target no_such` | SPDIF monitor | 5648 | fallback (r77 law) |
| `-P stream.capture.sink=true --target @DEFAULT_MONITOR@` | SPDIF monitor | 5648 | alias = default sink mon |
| `+ -P node.autoconnect=false` | *(none)* | 44 B | **honored: never links** |
| `+ -P stream.monitor=true` | `r78_ns:monitor` | 16384 | decoration on capture |
| `+ -P media.class=Audio/Source` | *(none)* | 44 B | **class override → unlinked** |

### 1.1 The laws

- **Prop precedence:** `target.object` (as a stream property) > `--target`
  flag > absent. `node.target` behaves identically to `target.object`
  (both resolve → honored or fall back under `stream.capture.sink=true`).
- **The fallback is one-sided.** Under `stream.capture.sink=true`,
  unresolvable names land the **default sink's monitor**. Without the prop
  (or with `=false`), unresolvable names produce **no link at all** — a
  44 B finalized `data(0)` wav at rc=1, never a default-source
  substitution. The r77 "garbage → default monitor" law is gated on the
  prop; there is no symmetric law on the source side.
- **`.monitor` is not a node.** `pw-dump` shows monitor "sources" do not
  exist as `Audio/Source` nodes — they are `monitor_*` *ports on the
  `Audio/Sink` node itself*. `pactl` synthesizes them as PA sources, which
  is why `parec -d X.monitor` resolves but `pw-record --target X.monitor`
  (no prop) cannot — and why adding `stream.capture.sink=true` makes it
  resolve (the prop authorizes sink-side matching, `.monitor` suffix
  accepted).
- **`media.class` override is a degenerate, not decoration**: setting
  `Audio/Source` on the capture stream leaves it unlinked (44 B) —
  the stream node's own class drives the autoconnect match.
- **`PIPEWIRE_PROPS` env is a second prop vector**: `{ stream.capture.sink=true
  node.name=r78env }` in the environment produced `r78env:input_*` ports
  linked to `r78_ns:monitor_*` — same props, same routing, no CLI.
- **`resample.quality` is the `-q` knob**: `-P resample.quality=0|14` and
  `-q 0|14` give byte-identical payload shas (`88ad…`/`84f0…`); `=999`
  clamps to the q14 result. With content flowing, the resampler is
  observable in payload bytes (default `b4f5…` ≠ q0 ≠ q14) — r77's "q not
  observable" was a silence artifact, as suspected.

---

## 2. FRONTIER 2 — pw-link consumption lattice (`probe-pwlink-r78.json`)

### 2.1 `--target 0` = published-but-unlinked; manual pin starts the flow

```
pw-record -P node.name=r78b -P stream.capture.sink=true --target 0 -n 192000
  t=1.0 s  file=44 B   links={}        ports PUBLISHED: r78b:input_FL/FR (pw-link -i)
  pw-link r78_ns:monitor_FL r78b:input_FL   rc=0
  pw-link r78_ns:monitor_FR r78b:input_FR   rc=0
  t=2.2 s  file=229420 B, links={r78_ns:monitor_* -> r78b:input_*}
  final    768044 B finalized rc=1, peak 16384 (tone)
```

**A capture CAN be pinned to a specific port pair post-spawn**, and `-n`
begins counting only when frames flow. r77's `target_0_unlinked` is the
pre-pin half of this story.

### 2.2 `pw-link -d` mid-run — the stream never notices

```
t=1.5 s   sz=286764   pw-link -d both links   rc=0, links now {}
t=1.7 s   sz=325676
t=2.7 s   sz=518188   (+192512 B ≈ exactly 100 % of 48k×2ch×s16)
           CONTENT: disconnect-window peak = 0 (pre: 16384, post-relink: 16384)
  relink  rc=0 → +229376 B in next 1.2 s, tone back
final     747564 B finalized at TERM, rc=1
```

Named class **`unlinked_sustained_zeros`**: a fully unlinked capture
stream keeps producing **zeros at exactly the negotiated rate** — rc,
growth rate, final header all indistinguishable from a linked run. The
disconnect window is only visible in content. This is the link-level twin
of r77's `sustained_after_target_loss` (node destroyed → same law), so
*both* loss mechanisms land one class family: **producer loss is
invisible in the artifact**.

### 2.3 Port-level granularity

- **FL-only pin** → stereo file with `peak_L=16384, peak_R=0`: channels are
  independently linkable; an unlinked channel delivers zeros inside a
  healthy container.
- **Two producers → one input port**: `r78_ns:monitor_FL` AND
  `Line:capture_FL` both accepted onto `r78b:input_FL` (rc=0, both links
  listed). With two *distinct* tones (12000-amp 1 kHz into `r78_ns`,
  12000-amp 2.5 kHz into `r78_ns2`): **payload peak 23488 ≈ sum** —
  PipeWire mixes producers on the input port, no arbitration.

### 2.4 Refusals collapse to one class

bogus out-port, bogus in-port, input→input, output→output, unlink-never-
linked — all → **rc=255, `failed to (un)?link ports: No such file or
directory`**. Class `pwlink_enoent`. No direction/typology information in
the error at all.

### 2.5 Consumer differences on the same unlinked state

| consumer | unlinked behavior | artifact |
| --- | --- | --- |
| `pw-record --target 0 -n N` | **stall** — 0 frames, `-n` never binds | 44 B placeholder until TERM |
| `ffmpeg -f jack -t 1.0` (never linked) | **zero-fill** — duration met | 215650 B of zeros, honest header |
| `pw-record -P node.autoconnect=false` | **stall** | 44 B |
| `pw-record` after `pw-link -d` | **zero-fill** — stream stays running | grows at rate |

Two named shapes: `unlinked_stall` vs `unlinked_zero_fill` — same PipeWire
state, different consumer semantics (frame-bound vs wall-bound).

---

## 3. FRONTIER 3 — JACK without jackd (`probe-jack-ffmpeg-r78.json`)

`pacman -Qo /usr/lib/libjack.so.0` → **pipewire-jack 1:1.6.8-1**: libjack
is already PipeWire's; `pw-jack` is a thin env wrapper (PIPEWIRE_DEBUG /
remote / samplerate / period), not a server substitute.

| leg | rc | bytes | peak | notes |
| --- | --- | --- | --- | --- |
| `ffmpeg -f jack -i ffmpeg -t 1.0` (no shim) | 0 | 215650 | 0 | works unshimmed |
| `pw-jack ffmpeg -f jack -i ffmpeg -t 1.2` | 0 | 387906 | 0 | identical result |
| `pw-jack ffmpeg -f jack -i r78_ns -t 1.2` (tone on ns) | 0 | 230478 | 0 | `-i` = client name, not target |
| `pw-jack ffmpeg -f jack -i r78probe` + manual pin | 0 | 496746 | **16384** | `r78probe:input_1/2` linked to `r78_ns:monitor_*` |

- ffmpeg's jack demuxer has **only `-channels`** — no connect control; the
  client registers `<name>:input_N` ports and **auto-connects to
  nothing**. All unlinked jack legs deliver the `unlinked_zero_fill`
  shape (valid wav, duration met, all zeros).
- **The manual pin law is consumer-agnostic**: the same `pw-link` command
  that feeds `r78b:input_FL` feeds `r78probe:input_1` on a jack stream.
- JACK-style target naming does not bind a PipeWire node — `-i r78_ns`
  named the *client* "r78_ns" and still connected to nothing.

---

## 4. FRONTIER 4 — parec format / fix / monitor-stream
(`probe-parec-format-r78.json`, `-rate-ms-`, `-fixdisc-`, `-fmtlong-`)

### 4.1 The 27-format lattice (seekable file, TERM window)

- **Writes real containers** (magic + payload verified at 3.0 s):
  wav `RIFF`, aiff `FORM`, au `.snd`, **flac `fLaC`** (0 B @1.3 s → 56994 B
  @3.0 s: the 0-byte shape is **granule-delay**, not refusal — my labrat
  could not run, this is my own falsification), oga `OggS`, caf `caff`,
  rf64 `RF64` (data field `0xFFFFFFFF` placeholder — rf64 semantics),
  w64 (RIFF+GUID), voc `Creative Voice File`, pvf `PVF1`, mat, sf, paf,
  mpc.
- **Known-but-unwritable** → rc=1 `Failed to open audio file.` +
  **0-byte file created**: iff, avr, htk, sds, sd2, m1a, xi, wve. (Class
  `pa_bad_file_format`, now on seekable targets too.)
- **Unknown name** → rc=1 `Unknown file format bogus_fmt.` + **no file at
  all**. New class `pa_unknown_file_format` — distinct artifact shape
  (missing vs 0-byte) from the unwritable-format class.
- Bare `--file-format` (no value) = wav.
- `--channels=6` writes but warns nonfatally: `Warning: failed to write
  channel map to file.`

### 4.2 `--fix-*` law — adopt source spec, header keeps the lie

Raw-stream byte count in a 2.5 s window (granule-quantized; Line source =
s24le 2ch 48000, ns monitor = s16le 2ch 48000):

| request | bytes/2.5 s | interpretation |
| --- | --- | --- |
| `--raw` (defaults 44100/16/2) | 196608 | 3 granules |
| `--rate=96000` | 262144 | rate honored (4) |
| `--rate=22050` | 131072 | request honored (2) |
| `--rate=22050 --fix-rate` | **196608** | **fix-rate discards the request → ~48 k** |
| `--format=s32le` | 262144 | request honored (4 B/smp) |
| `--format=s32le --fix-format` | **196596** | **fix-format → s24 granule (65532-unit)** |
| `--format=u8 --fix-format` | **196596** | same: source format wins |
| `--channels=1 --fix-channels` | **196608** | fix-channels → source 2 ch |
| `--fix-rate --fix-format --fix-channels` | 262128 | non-64k granule again |

**Each `--fix-*` flag overrides its matching request knob with the source
spec.** Measured against requests that differ from *both* the default and
the source, so the adoption is proven, not guessed.

**And the emitted header does not follow.** Every
`--file-format=wav --fix-*` leg's `fmt` chunk still records the
**requested/default spec** (`44100/16/2ch` — also on `line_fix_all` where
the stream demonstrably delivers s24/48k). Named class
**`header_prefix_mismatch`**: with fix flags, the container lies about
its own payload spec. (Contrast with pw-record §r77: its header always
reports the *requested* spec too, but there the request *is* what the
stream delivers after client-side conversion — parec's fix flags break
that coincidence.)

### 4.3 `--monitor-stream=<idx>` — per-stream capture surface

`parec -d r78_ns --monitor-stream=23478 --file-format=wav` (idx of my
`pw-cat` sink-input) → rc=0, 131116 B, `fmt 44100/16/2`, **peak 16384**:
captures exactly one sink-input pre-mix. Bad index (`0`, `999999`) →
rc=1 `pa_no_such_entity` + 44 B empty wav — **same class as a bad `-d`
name**, so error-class alone cannot separate bad-source from bad-index.

---

## 5. FRONTIER 5 — MIDI / ALSA seq (`probe-midi-r78.json`)

| surface | result |
| --- | --- |
| `aseqdump -p 14:0` idle | bounded text witness: `Waiting for data…` header only, TERM rc=0 |
| `aplaymidi -p 14:0 <smf>` + `aseqdump -p 14:0` | prints `Note on 0, note 60, velocity 96` / `Note off …` lines |
| `aplaymidi -p 14:0` + `arecordmidi -p 14:0 -n 4 -b 120` | **rc=0, valid 52 B SMF** (`MThd`+1 `MTrk`, note-on `0x90` C4/96, note-off) — division re-encoded 384 tpq ≠ input 480 |
| `aseqsend -p 14:0 -s <hex>` | treats arg as FILENAME: `cannot open <hex> - No such file or directory` **at rc=0** — rc-lies row; `-s <real file>` works (send_err="") |
| `pw-record -M midi --target {Midi-Bridge,"Midi Through",51,garbage}` | **all `no_target_node` rc=1 + 44 B wav** — the seq bridge node is untargetable by name AND serial |
| `arecordmidi|aseqdump|aplaymidi -p 99:9` | rc=1 `Cannot connect (from|to) port 99:9 - Invalid argument` — class `aseq_einval` |

**Fixture-row answer:** yes — `Midi Through` (14:0) is a loopback;
`aplaymidi` injects, `arecordmidi -n N` gives a bounded deterministic SMF
capture, `aseqdump` gives the text witness. The PipeWire-side MIDI surface
(`pw-record -M midi`) is **not reachable** via target naming on this host.

---

## 6. FRONTIER 6 — ffmpeg / arecord device parity
(`probe-jack-ffmpeg-r78.json` + arecord cells)

| input | rc | artifact |
| --- | --- | --- |
| `ffmpeg -f pulse -i r78_ns.monitor` | 0 | 232518 B, peak 16384 (tone) |
| `ffmpeg -f alsa -i pipewire` / `-i default` | 251 | `ffmpeg_alsa` I/O error, **no file** |
| `ffmpeg -f alsa -i sysdefault` | 0 | 197038 B, peak **655** |
| `ffmpeg -f alsa -i plughw:0,0` / `hw:0,0` | 0 | ~192 KB, peak 286–323 |
| `ffmpeg -f oss -i /dev/dsp` | 251 | `ffmpeg_io`, no file (device absent) |
| `arecord -D pipewire` / `-D default` | 1 | **`TICK_TIME: [0 0]`** — new class `alsa_tick_time`, no file |
| `arecord -D sysdefault -d 1 -f cd` | 0 | 176444 B finalized |

- **ffmpeg and arecord agree on the broken set**: the `pipewire`/`default`
  ALSA-plugin PCMs listed by `arecord -L` refuse in both tools (different
  error strings). Parity is real — the asymmetry is protocol-level: only
  the pulse/pipewire-protocol consumers (parec/pw-record/ffmpeg -f pulse)
  reach PipeWire nodes.
- **`hw:0,0`/`sysdefault` carry an analog noise floor (peak 286–655,
  nz≈1.0) where the pulse-path `Line` source reads exact digital zero.**
  Same physical input, two different content laws by route — a future
  "source content" witness must pin the route too.

---

## 7. Named classes added this round

| class | signature | where |
| --- | --- | --- |
| `unlinked_sustained_zeros` | link loss/still unlinked → bytes grow at exactly rate, content = 0 | pw-record + pw-link -d; ffmpeg jack unlinked |
| `unlinked_stall` / `unlinked_zero_fill` | consumer-bound semantics on identical PipeWire state | pw-record `-n` vs ffmpeg `-t` |
| `pwlink_enoent` | rc=255 `failed to (un)link ports: No such file or directory` | all bad pw-link ops |
| `pa_unknown_file_format` | rc=1 `Unknown file format X`, **missing file** | parec --file-format=bogus |
| `pa_bad_file_format` (extended) | rc=1 `Failed to open audio file`, **0-byte file** | 8 real-but-unwritable formats |
| `header_prefix_mismatch` | wav `fmt` records pre-fix spec while stream delivers source spec | parec --fix-* |
| `prop_media_class_unlinked` | `media.class=` override → 44 B, zero links | pw-record -P |
| `alsa_tick_time` | rc=1 `TICK_TIME: [0 0]` | arecord -D pipewire/default |
| `aseq_einval` | rc=1 `Cannot connect (from|to) port <p> - Invalid argument` | arecordmidi/aseqdump/aplaymidi bad port |
| `seq_rc0_failure` | error text on stderr, **rc=0** | aseqsend -s <non-file> |

---

## 8. Confounds and provenance

- **The r77 author was live for my entire window.** At 17:05–17:15 they
  ran `--probe-capture-r76` then `--probe-capture-r77` with in-flight
  `pw-record`/`pw-cat` legs on Speaker and SPDIF. My isolation held
  because: (a) every routing leg targeted my own `r78_ns` null sink,
  (b) every stream carried `-P node.name=r78*` so `pw-link -l` producers
  are unambiguous, (c) tone anchors live only on `r78_ns`.
- **SPDIF's monitor was not silent during my window** (peak 5648 in two
  fallback legs — some audio was on the default sink). Every fallback
  verdict above is therefore pinned by the **link witness** (which ports
  feed my stream), not by content.
- **One test deliberately not run:** the `@DEFAULT_MONITOR@` follow-the-
  default check needs `pactl set-default-sink` — a 2–3 s window where the
  concurrent seat's garbage-target fallback legs would land on *my* sink
  and corrupt their measurements. Designed, deferred, recorded as a
  residual (§10).
- **Labrat provenance (exact route):** I dispatched my single permitted
  `ufo-labrat` (hypothesis: parec flac 0-byte = granule-delay). It
  reported **NOT EXECUTED** — its substrate exposes only read-only
  filesystem tools and sees neither `parec` nor the pipewire sockets.
  Zero writes, honest refusal. The hypothesis was answered by my own
  `probe-parec-fmtlong-r78.json` run.
- **Classifier wart (mine):** `ffmpeg_jack` matched the word "jack" in
  ffmpeg progress lines on *successful* legs — classes are only asserted
  on failures; the pattern needs a failure anchor if reused.
- All numbers are this-host pins at these tool versions; nothing here is
  a portability claim.

## 9. Receipts

`corpus/live/r78-scout/RECEIPTS.md` — sha table for all 8 JSON receipts +
harness files (probes a–e + supplements). Scratch trimmed to ~180 KB.

## 10. Ranked r78 cell candidates

1. **`unlinked_sustained_zeros`** (§2.2) — `pw-link -d` mid-run: full-rate
   zero-fill, invisible except in content. The link-level twin of
   `sustained_after_target_loss`; cheap to pin (one disconnect, three
   size samples, one window peak).
2. **The prop precedence lattice** (§1.1) — `target.object` prop > flag;
   `node.target` routes; `media.role`/`stream.monitor` decoration;
   `media.class` override → unlinked degenerate; `PIPEWIRE_PROPS` env as
   a second vector. A compact `-P` truth table.
3. **Fallback asymmetry** (§1.1) — `stream.capture.sink` is the *gate*
   for fallback AND for sink/monitor resolution; `=false` ≡ absent; no
   default-source substitution exists. Plus `.monitor`-is-a-pulse-alias
   (explains why pw-record can't resolve it bare).
4. **Manual pin law + port granularity** (§2.1, §2.3, §3) — `--target 0`
   publishes unlinked ports; `pw-link` binds any port pair on pw-record
   AND jack clients; FL-only → half-silent stereo; two producers → sum.
5. **parec fix-* law + `header_prefix_mismatch`** (§4.2) — the only cell
   where a container provably lies about its own spec.
6. **parec format lattice with two refusal shapes** (§4.1) —
   missing-file `Unknown` vs 0-byte `Failed to open`; flac granule-delay
   falsified.
7. **`--monitor-stream` per-stream capture** (§4.3) + `pa_no_such_entity`
   class collision with bad `-d`.
8. **MIDI fixture row** (§5) — arecordmidi bounded SMF roundtrip;
   `pw-record -M midi` cannot bind the bridge (name or serial).
9. **alsa/pulse route asymmetry** (§6) — `alsa_tick_time` on the plugin
   PCMs in both tools; `hw:` analog-noise vs pulse digital-zero on the
   same input.

## 11. Remaining unknowns (honest edges)

- **`@DEFAULT_MONITOR@` move-follow** — designed, unrun (§8, inter-seat
  hazard): `set-default-sink r78_ns` → prop+`@DEFAULT_MONITOR@` should
  land MY monitor; restore after. Separates alias-tracking from
  fixed-fallback.
- **resample.quality legality bound** — `=999` clamps (to what exactly?);
  the prop may accept a named-quality enum I didn't enumerate.
- **`node.latency`/`--latency` props** — unmeasured; latency axis untouched.
- **`pacat` parity** — assumed `parec ≡ pacat -r` (same binary); the
  `--playback` side of the same lattice unmeasured.
- **Midi-Bridge targetability** — serial and name both refuse; a
  `target.object=<object.serial as decimal>` or port-id route may exist;
  `pw-cli`/`pw-dump` param paths unexplored.
- **Two-producer mix** measured on s16 pw-record payload only — the sum
  law's format/clip behavior (does mixing saturate? dither?) unmeasured.
- **`hw:` analog floor vs pulse zero** — one host, one mixer state; the
  route-content law needs a mixer-read (`amixer`) leg to name the cause.
