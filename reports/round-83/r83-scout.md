# R83 scout — pw-loopback prop lattice / stream remix props / midi surface / adaptive resampler

Round 83 pre-measurement. Host `plazir27`, measured 2026-10-15 ~02:52–03:12
UTC−3 (05:52–06:12Z). Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`a2616f7` (`r78 LOG: adjudicator ADMIT-corr`). Toolchain: PipeWire **1.6.8**
(pw-loopback/pw-cat/pw-record/pw-mididump/pw-midiplay/pw-cli/pw-dump/pw-link
1.6.8), libpulse **17.0** (pactl 17.0-98-gb096, protocol 35), WirePlumber
**0.5.17**, alsa-utils **1.2.16** (aplaymidi/aseqdump), Python **3.14.7**
(numpy 2.5.3), Linux **7.2.3-arch1-3**.

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/r83-scout/` plus this report.** `corpus/fixtures/measure_audio.py`
was dirty at entry (the sibling r78/r79 fold run owns it; never read, imported
or executed here — own harness `r83_probe.py`, own tones, own FFT classifiers).
`git status` shows exactly one new untracked path from this seat plus this
report. Scratch **540 KB** at exit (receipts + analysis + one evidence wav;
recorded monitors and tones trimmed).

**Isolation.** Five seat-owned null sinks (`r83dsp_p1_ns{a,b}`, `r83dsp_p4_ns`,
`r83dsp_p4_nsm` mono, `r83dsp_p5_ns48`, `r83dsp_p5_ns44` rate=44100, plus
verify-pair `r83dsp_v_ns48/ns44`) loaded per driver and unloaded **by index
verified against sink_name** — never by name. All stream nodes `r83dsp*`.
No tone ever targets the shared SPDIF default sink (the sibling r78 seat is
live and recording it — §9 ledger). Exit verified: 0 `r83dsp` nodes, 0 modules,
0 processes.

---

## 0. Headline — the brief's five items

| # | frontier item | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | pw-loopback `-i`/`-o` prop lattice | **PINNED + crash class** | every prop form lands verbatim (`k=v` space/comma, `{ k = v }`, `{ "k": v }` JSON); **`-i ''`/`-o ''` segfaults 6/6 (rc 139)**; a malformed string silently drops the *whole* props value; `audio.position=[ MONO ]` lands on the node but does **not** steer the DSP copy (stereo passthrough measured) — matrix is `-c`/`-m` flag-only |
| 2 | pw-filter existence | **NAMED COVERAGE GAP** | `pw-filter` is absent from PATH, from `pipewire`/`pipewire-audio` file lists, and from man — the filter surface is `libpipewire-module-filter-chain` (man7) + SPA `filter-graph` plugins (builtin/ebur128/ladspa/lv2/sofa); `pw-cli` has **no `list-modules` command** (`ls Module` lists the 12 daemon modules) |
| 3 | pw-mididump / pw-midiplay | **BOTH LIVE, pin-armed round-trip** | `pw-mididump <file>` parses+prints SMF; bare publishes `midi-dump` (Filter/DSP/Midi, no media.class, `input` port, **no autoconnect**); `pw-midiplay` → `Stream/Output/Midi`/`output_1`; `--target Midi-Bridge` **and** bare auto both die `no target node available` (rc=1, **no fallback**); manual `pw-link` pins carry real events **both directions** (aseqdump/aplaymidi witnesses) |
| 4 | `node.passive`/`node.dont-remix`/`channelmix.*` | **LAW SPLIT: `stream.dont-remix` is the only effective prop** | `node.dont-remix`, `channelmix.upmix/downmix/disabled/normalize/stereo-widen/upmix-method` all **land verbatim but are content-inert** on pw-cat playback; `stream.dont-remix=true` changes the *port layout* (mono→`output_MONO`→FL-only) and the content (R=0 / stereo→mono keeps FL full-amp, drops FR); `node.passive=true` lands, links, flows; `node.dont-move` → `move-sink-input` rc=0 silent no-op |
| 5 | adaptive resampler / rate mismatch | **TWO NEW CONTENT CLASSES** | 44.1k file→48k sink: `node.rate='1/44100'`, tag tone verifies at 1000/1500 Hz (pitch preserved); **`resample.disable=true` + mismatch → pure digital silence** (96044 B of zeros, links live, no error); **`resample.peaks=true` + mismatch → half-wave rectified tone + a zeroed sample every ~12.3** (mean +4383, deterministic 2/2); loopback default `resample.disable` does **not** break 44.1k→48k copies |

Plus operational traps in §8 (the `sink_name` prefix-match unload bug my own
harness hit; the empty-props segv; `-l`/`-d` unit asymmetry).

---

## 1. FRONTIER 1 — the pw-loopback arg lattice (`receipts/p1-args.json`)

Fixed route on every leg: `-C <nsa> -i stream.capture.sink=true -P <nsb>`,
both probe-owned. "Lands" = present in `pw-dump` node props; "effective" =
observable in links or monitor content. 38 legs.

### 1.1 Prop syntax forms — all parse; two failure shapes

| leg | `-i` value | lands? | verdict |
| --- | --- | --- | --- |
| S1 | `media.name=SPACEV bogus.prop=42` | both on input node | space k=v |
| S2 | `{ media.name = BRACEV bogus.prop = 42 }` | both | braced k=v |
| S3 | `{ "media.name" = "BRACEQ" "bogus.prop" = "42" }` | both | braced+quoted |
| S4 | `{ "media.name": "COLONV" }` | lands | **JSON colon form** |
| S5 | `media.name=COMMAV,bogus.prop=42` | both | comma-separated |
| S6 | `}{ garbage` | **nothing** — both nodes spawn with full default props, full links, empty stderr | **malformed → whole `-i` value silently dropped** (not partially parsed) |
| S7 | `''` (empty) | — | **SIGSEGV**, `timeout: the monitored command dumped core`, rc=139 |

S7 verified **6/6** (`-i ''` ×3, `-o ''` ×3; bare `pw-loopback` control runs
fine). Class `loopback_empty_props_segv`. The props parser is full SPA-JSON:
unquoted/quoted keys, `=`/`:` separators, space/comma lists, brace wrapping —
all accepted. **Arming rule: never emit an empty `-i`/`-o`; a malformed one
fails silently.**

### 1.2 `-i` writes only the capture node, `-o` only the playback node

Every S/R/P leg confirms one-sided prop placement; `media.name=…` on `-i`
appears only on `input.<n>`. **`-i node.name=X` overrides `-n` on the capture
node** (P7: node published as `r83dsp_capX`, not `input.<n>`); `-o node.name=X`
same on the playback node (P8 → `r83dsp_pbX`).

### 1.3 Channel map: props land, the flag does the work

| leg | prop on node (measured) | monitor content | verdict |
| --- | --- | --- | --- |
| C1 `-i 'audio.position=[ MONO ]'` | input: `audio.position='[ MONO ]'`, channels still 2, ports still `input_FL/FR` | **stereo passthrough** (amp 8191.9 @1k / 8192.0 @1.5k, cross-terms 0) | **prop-only — the copy does not remix** |
| C2 `{ audio.position = [ MONO ] }` | same | stereo passthrough | same |
| C3 `audio.channels=1 audio.position=[ MONO ]` | input: `channels=1` + `[ MONO ]` | stereo passthrough | lands, prop-only |
| C4 `channelmap.map=[ MONO ]` | input: `channelmap.map='[ MONO ]'` verbatim; `audio.position` unchanged | stereo passthrough | **lands, inert** (pulse-style key ≠ the real knob) |
| C5 `-o 'audio.position=[ MONO ]'` | output: `[ MONO ]` | stereo passthrough | prop-only |
| C6 `-c 6 -m '[ FL, FR, RL, RR, FC, LFE ]'` | **both** nodes `channels=6` + 6-position | — | flags set both nodes + the copy format |
| CC0 control (no props) | `[ FL, FR ]` both | `tone1000`/`tone1500` clean | baseline |
| CC3 `-i` **and** `-o` `[ MONO ]` | both `[ MONO ]` | **still stereo passthrough** | prop-only even on both sides |

**Law.** On pw-loopback the matrix mixer is driven by `-c`/`-m` (r79's
`0.5·(L+R)` signature), **not** by `audio.position`/`audio.channels` props —
those land on the node verbatim and are ignored by the in-client copy. This is
the "props land vs silently drop" answer in its sharpest form: **every `-i`/`-o`
prop lands on the stream node; what drops is the *effect*.**

### 1.4 resample.* / passive / dont-* / channelmix.* — landing table

| `-i`/`-o` prop | lands as | side |
| --- | --- | --- |
| `resample.quality=0` / `=14` / `=999` | `0`/`14`/`999` verbatim — **no write-time clamp** | respective node |
| `resample.disable=false` | `false` (loopback default is `true` on both nodes) | respective node |
| `resample.peaks=true` | `true` | respective node |
| `resample.prefill=false` | `false` (default `true`) | respective node |
| `node.passive=true` | `true` | respective node |
| `node.dont-move=true` | `true` | respective node |
| `node.dont-remix=true` | `true` — **lands but inert** (§4) | respective node |
| `stream.dont-remix=true` | `true` — effective on streams (§4) | respective node |
| `channelmix.disabled/stereo-widen/upmix` | verbatim | respective node — all inert (§4) |
| `media.class=Audio/Source` (`-i`) | input node class `Audio/Source` | **input loses ALL links** (r78 `prop_media_class_unlinked` on the loopback) |

### 1.5 `-l`/`-d`/`-g`/`-C`/`-P` flags

| leg | flag | measured `node.latency` (both nodes) |
| --- | --- | --- |
| L1 | `-l 5` | `'240/48000'` (5 ms × 48) |
| L8 | `-l 256` | `'12288/48000'` (256 ms × 48) |
| L9 | `-l 2.5` | `'96/48000'` — **atoi: "2.5"→2 ms** |
| L3/L4/L10 | `-l 0` / `-l abc` / `-l 0.5` | *(prop absent)* — **silently dropped, no error** (contrast pw-cat `--latency 0` which at least prints `bad latency value`) |
| L6 | `-l 10000` | `'480000/48000'` — 10 s accepted verbatim |
| L2 | `-d 0.25` | `'4000/48000'` |
| d-series | `-d {0.1,0.5,1.0,2.0}` | `'1600'/'8000'/'16000'/'32000'` per 48000 |
| L5 | `-d -1` | *(absent)* — silent drop |
| ld/dl | `-l 5 -d 0.25` **and** `-d 0.25 -l 5` | `'240/48000'` both orders — **`-l` beats `-d`** |

- **`-l` is integer ms** (atoi — `2.5` truncates, `abc`→0→drop) → `node.latency
  = l·48 / 48000`. **`-d` is float s × a fixed 16000** → `node.latency =
  d·16000 / 48000` (`-d 1.0` reports 333 ms at 48k). Two different scales land
  on the same prop.
- **Latency props are prop-only on this topology** (content witness): with
  `-d 1.0` (`'16000/48000'` = nominal 333 ms) the first non-silent monitor
  sample arrives at **42.7 ms — identical to the no-delay control** (42.7 ms;
  a `-d 0.033` leg gave 19.7 ms = jitter). Reproduces r79's "the request is
  intent, not a measured param" for the loopback.
- `-g r83dsp_grp` → `node.group='r83dsp_grp'` on **both** nodes (default
  `pw-loopback-<pid>`; `node.link-group` stays `loopback-<pid>-<n>`).
- `-C`/`-P` accept **`object.serial` numbers**: `-C 14419 -P 14419` resolved
  to the sink on both directions (monitor→input, output→playback links live).
- `-r/--remote` untested (no second remote on this host) — residual gap.

---

## 2. FRONTIER 2 — pw-filter: named coverage gap (`receipts/p2-filter.json`)

| surface | measured |
| --- | --- |
| `which pw-filter` | absent |
| `pacman -Ql pipewire \| grep bin/` | `pipewire pw-cli pw-config pw-container pw-dot pw-dump pw-link pw-metadata pw-mon pw-profiler pw-reserve pw-top spa-inspect spa-json-dump spa-monitor` |
| `pacman -Ql pipewire-audio \| grep bin/` | `pipewire-aes67 pipewire-avb pw-cat pw-dsdplay pw-encplay pw-loopback pw-midi2play pw-midi2record pw-mididump pw-midiplay pw-midirecord pw-play pw-record pw-sysex spa-acp-tool spa-resample` — **no pw-filter** |
| `man -w pw-filter` | `No manual entry` |
| `find /usr -name 'pw-filter*'` | only `/usr/share/man/man7/libpipewire-module-example-filter.7.gz` |
| `pw-cli help` | **no `list-modules` command** — the module surface is `pw-cli ls Module` (list-objects) |
| `pw-cli ls Module` | 12 daemon modules: `libpipewire-module-{rt,protocol-native,profiler,metadata,spa-device-factory,spa-node-factory,client-node,client-device,portal,access,adapter,link-factory,session-manager}` |
| `pw-dump` factories | none named `*filter*`/`dsp` |
| `/usr/lib/spa-0.2/filter-graph/` | `libspa-filter-graph.so` + plugins `builtin, ebur128, ladspa, lv2, sofa` |
| `man -w libpipewire-module-filter-chain` | exists (man7) |

**Gap verdict:** `pw-filter` the tool does not exist on this host (it is not
built/shipped by the Arch `pipewire-audio` split). The DSP/filter coverage on
this host is exactly r79's `libpipewire-module-filter-chain` surface
(conf.d + `pw-cli load-module`, client-scoped) plus the SPA filter-graph
plugin set above. **Any arm cell naming `pw-filter` is a guaranteed
not-found row; the sibling binaries to name instead are `pw-loopback`,
`pw-encplay`, `pw-dsdplay`, `pw-sysex`, `pw-midirecord`/`pw-midi2record`.**

---

## 3. FRONTIER 3 — pw-mididump / pw-midiplay (`receipts/p3-midi.json` + live legs)

Graph objects: `Midi-Bridge` node (id 50, `factory.name=api.alsa.seq.bridge`,
`media.class=Midi/Bridge`) with `in` port `Midi Through: Port-0 (playback)`
(id 51) and `out` port `…(capture)` (id 52), both `8 bit raw midi`;
`bluez_midi.server` (id 35) with `in`/`out` midi ports. ALSA seq witness:
`Midi Through` at `14:0`.

### 3.1 `pw-mididump` — two disjoint modes

- **`<file>` or `-` (stdin): SMF event printer**, no PipeWire node at all:
  ```
  $ pw-mididump r83_note.mid          (rc=0)
  opened r83_note.mid format:0 ntracks:1 division:96
  track: 0 sec:0.000000 Meta: Tempo: 500000 microseconds per quarter note, 120.00 BPM
  track: 0 sec:0.000000 Note On    (channel  1): note   C4, velocity  96
  track: 0 sec:2.500000 Note Off   (channel  1): note   C4, velocity  64
  track: 0 sec:2.500000 Meta: End Of Track
  ```
  Missing file → rc=255 `error opening <path>: No such file or directory`.
- **Bare: a live event sink.** Publishes node `midi-dump` (id 84:
  `media.type=Midi`, `media.category=Filter`, `media.role=DSP`, **no
  `media.class`**, `node.want-driver=true`) with one `input` port
  `8 bit raw midi`. **No autoconnect** — zero links at spawn.
- **Manual pin works**: `pw-link 'Midi-Bridge:Midi Through: Port-0 (capture)' 'midi-dump:input'`
  → rc=0, link `active` (50:52 → 84:86). `aplaymidi -p 14:0 r83_note.mid` then
  delivers on stdout:
  ```
    31: track: 0 sec:0.021979 Note On    (channel  1): note   C4, velocity  96
   229: track: 0 sec:2.522104 Note Off   (channel  1): note   C4, velocity  64
  ```
  (leading integer = buffer/frame counter; `-M ump` mode also publishes, untested
  beyond node shape.)

### 3.2 `pw-midiplay` — `Stream/Output/Midi` + `output_1`; name targets all fail

| leg | result |
| --- | --- |
| `pw-midiplay f.mid` (auto) | rc=1 `stream node 162 error: no target node available` + `remote error … no target node available` — node created then dies; **no default fallback** (unlike audio playback) |
| `--target Midi-Bridge` | rc=1, same `no target node available` (node id 140) — **the bridge is not a resolvable target** |
| `--target no_such_midi_r83` | rc=1, same class (node id 90) |
| `--target 0` | node `r83dsp_midi0` `Stream/Output/Midi`, port `output_1` `8 bit raw midi`, `media.type=Midi`, `stream.is-live` — **published unlinked, alive** |
| `-P node.name=r83dsp_midiplay` | lands as `node.name` |
| missing file | rc=1 `midifile: can't read midi file '<path>': No such file or directory` + `error: open failed…` + full usage on stderr |

**Pin-armed playback (the headline):**
```
pw-midiplay --target 0 -P node.name=r83dsp_mplay r83_note.mid &
pw-link 'r83dsp_mplay:output_1' 'Midi-Bridge:Midi Through: Port-0 (playback)'   # rc=0, link active (86:167 -> 50:51)
aseqdump -p 14:0    ->    14:0   Note on   0, note 60, velocity 96
                          0:1    Port subscribed   143:0 -> 128:0
```
The SMF's C4 note traversed PipeWire→ALSA-seq. Both directions verified:
**the PipeWire↔ALSA-seq midi path exists but only through manual `pw-link`
pins** — name-based targeting fails for the capture side (r78's `pw-record -M
midi` law), for the playback side, and for auto. Class
`midi_target_no_node` (rc=1, `no target node available`).

---

## 4. FRONTIER 4 — playback stream props: effective vs landed (`receipts/p4-remix.json`)

`pw-cat -p <file> --target <sink>`; content = sink monitor FFT. Tone amp 8192.
MONO48 = 1 kHz mono; TONE48 = L 1 kHz / R 1.5 kHz stereo.

### 4.1 Mono file → stereo sink (the upmix surface)

| leg | prop | stream ports/links | monitor | verdict |
| --- | --- | --- | --- | --- |
| M0 | — | `output_FL/FR`→`playback_FL/FR` | peak [8192,8192], amp@1k=8191.9 both | **mono→stereo = duplicate at full amp** |
| M1 | `node.dont-remix=true` | lands `true`; identical links | [8192,8192] both tone | **lands, inert** |
| M2 | `stream.dont-remix=true` | lands `true`; **`output_MONO`→`playback_FL` only** | **[8192,0] — FL tone, FR digital 0** | **EFFECTIVE: no remix, mono plays FL only** |
| M3 | `channelmix.upmix=false` | lands `false`; identical links | [8192,8192] | lands, inert |
| M4 | `channelmix.disabled=true` | lands `true`; identical | [8192,8192] | lands, inert |
| M5 | `channelmix.normalize=true` | lands `true`; identical | [8192,8192] | lands, inert |

### 4.2 Stereo file → stereo sink (widen/remix surface)

| leg | prop | monitor `amp_at` (L@1k / R@1.5k) | verdict |
| --- | --- | --- | --- |
| W0 | — | 8191.9 / 8192.0, cross 0.0 | baseline |
| W1 | `channelmix.stereo-widen=1.0` | 8191.9 / 8192.0, cross 0.0 | **lands, zero spectral effect** |
| W2 | `stereo-widen=0.5` | identical | inert |
| W3 | `node.dont-remix=true` | identical | inert (stereo→stereo anyway) |
| W4 | `channelmix.upmix-method=simple` | identical | inert |

### 4.3 Stereo file → MONO sink (`channel_map=mono` null sink)

| leg | prop | stream ports/links | monitor content | verdict |
| --- | --- | --- | --- | --- |
| D0 | — | `output_MONO`→`playback_MONO` | peak 7802, amp 4095.9 @1k **and** @1.5k | **downmix = 0.5·(L+R)** (r79 signature reproduced on the sink side) |
| D1 | `channelmix.downmix=false` | lands `false`; same mono link | identical | **lands, inert** |
| D2 | `node.dont-remix=true` | same | identical | inert |
| D3 | `stream.dont-remix=true` | lands `true`; **`output_FL`→`playback_MONO` only** | **peak 8192, pure 1 kHz (FL only, full amp — FR dropped entirely)** | **EFFECTIVE: keeps native layout; unmapped channels drop, not mix** |

### 4.4 passive / dont-move

| leg | prop | measured | verdict |
| --- | --- | --- | --- |
| P0 | `node.passive=true` | lands `true`; links live; tone verifies at full amp | **lands, no link/content effect** on this topology |
| P1 | `node.passive=false` | lands `false`; same | control |
| P2 | `node.dont-move=true` + `pactl move-sink-input <idx> SPDIF` | move **rc=0**, `edges_after_move` still → `r83dsp_p4_ns` | **silent no-op move** (r80 law, now on a plain pw-cat stream) |
| P3 | (none) + `move-sink-input <idx> r83dsp_p4_nsm` | move rc=0; `edges_after_move` = `output_MONO→playback_MONO` | control: moved and **re-negotiated to mono** on the mono sink |

**Laws.**

- **`stream.dont-remix` is THE remix switch; `node.dont-remix` is a decoy** —
  both land verbatim on the node props; only the `stream.*` one changes port
  layout and content. `dont-remix` means *no remap at all*: unmapped output
  channels are dropped (FR→mono sink case) and unmapped input positions stay
  silent (mono→FL only).
- **All `channelmix.*` props land verbatim and are content-inert** on the plain
  pw-cat playback path (upmix, downmix, disabled, normalize, stereo-widen 0.5/
  1.0, upmix-method=simple). Whatever consumes them is not in this path —
  an arm that needs a channelmix effect cannot use a bare pw-cat stream.
- **`node.passive` on a playback stream records intent only** (links + content
  identical); **`node.dont-move` is honored silently** (move rc=0, no move).

---

## 5. FRONTIER 5 — adaptive resampler & rate mismatch (`receipts/p5-resample.json` + verify legs)

Sink pair: `r83dsp_p5_ns48` (48k) / `r83dsp_p5_ns44` (`rate=44100`, EnumFormat
honored per r80). TONE44 = 44.1 kHz stereo dual-tone, amp 8192.

### 5.1 pw-cat playback across the rate boundary

| leg | node props | monitor | verdict |
| --- | --- | --- | --- |
| S0 `tone44 → ns48` | `node.rate='1/44100'`, `node.latency='4410/44100'` | peak [8192,8191], **dom 1000.0/1500.0 Hz** | **tag tone verifies at mismatched rate — adaptive resampler preserves pitch** |
| S1 `+ resample.disable=true` | prop lands `true`, `node.rate='1/44100'` | **peak [0,0] — 96044 B of zeros, links live, stderr empty** | **`resample_disabled_zero_fill`: mismatch + disable → pure silence, no error** |
| S2 `+ resample.quality=0` | lands `0` | dom 1000/1500, amp≈S0 | freq invariant |
| S3 `+ resample.quality=14` | lands `14` | dom 1000/1500, amp≈S0 | freq invariant |
| S4 `+ resample.peaks=true` | lands `true` | **peak [8192,8192] but dom bin = DC (0.0 Hz), mean +4383** | **`peaks_rectified_artifact`** — see 5.2 |
| S5 `+ --rate 48000` | **`node.rate` stays `'1/44100'`** | verifies | **`--rate` flag does not override the file rate on pw-cat** |
| S6 `tone48 → ns44` | `node.rate='1/48000'` | verifies (amp asymmetric ~2:1 — downsample path) | pitch preserved both directions |

### 5.2 `resample.peaks` corruption shape (2/2 deterministic reps)

At matched rate (48k→48k): `resample.peaks=true` content = clean tone
(mean ≈0, dom 1000/1500) — **harmless when no resampler runs**. Across the
44.1k→48k boundary:

- waveform = **half-wave rectified**: every negative sample clamped to ~0
  (min observed ≈ +100..+900, never negative), positive half-cycle intact to
  +8192;
- **one sample in every ~12.3 output samples forced to exact 0** (gap
  histogram: 12×1187, 13×549 in 24000 frames);
- mean DC = **+4383.3/+4382.4 both reps**; windowed mean settles at +4791 after
  a 2751 startup ramp — deterministic, not noise;
- the tone's fundamental still verifies (amp@1k=12882 > baseline 11450 —
  rectification adds DC+harmonics, not detune).

### 5.3 pw-loopback across 44.1k→48k (all three resample variants)

| leg | resample props | ns48 monitor |
| --- | --- | --- |
| LB0 default (`resample.disable=true` on **both** nodes) | default | **verifies at 1000/1500, peak 8192** |
| LB1 `-i`/`-o resample.disable=false` | lands `false` | verifies identically |
| LB2 `resample.disable=false quality=14` | lands | verifies identically |

**Law.** The loopback's default `resample.disable=true` does **not** produce
the S1 silence and does **not** pitch-shift — the 44.1k sink→48k sink copy is
pitch-correct in every variant. Whatever `resample.disable` controls, the
loopback's own rate conversion still happens (contrast pair: same prop on
pw-cat playback → zeros; on pw-loopback → correct pitch).

---

## 6. Verbatim-armable cells (author-ready)

Every cell names probe-owned resources; rename `r83dsp_*` before arming.

```sh
# A1 props lattice — all four syntax forms land both props on input.<n>
pw-loopback -n X -C <sink> -i 'k1=v1 k2=v2' -P <sink2>
pw-loopback -n X -C <sink> -i '{ "k1" = "v1", "k2" = "v2" }' -P <sink2>
pw-loopback -n X -C <sink> -i '{ "k1": "v1" }' -P <sink2>
# A2 crash — DO NOT ARM except as a known-crash cell:
pw-loopback -n X -i ''            # rc=139 SIGSEGV (6/6)
pw-loopback -n X -i '}{ garbage'  # runs with DEFAULT props, empty stderr (silent drop)
# A3 channel-map: flags steer, props decorate
pw-loopback -n X -m '[ MONO ]' -C <ns> -i stream.capture.sink=true -P <ns2>
   # -> monitor(ns2): both ch = 0.5*(L+R), amp≈2047.6/freq, peak≈7801
pw-loopback -n X -i 'audio.position=[ MONO ]' -C <ns> -i stream.capture.sink=true -P <ns2>
   # -> input.<n> prop shows [ MONO ]; content stays stereo (prop-only)
# A4 latency props
pw-loopback -n X -l 5 -d 0.25 ...     # node.latency='240/48000' (-l integer-ms*48 beats -d*16000)
pw-loopback -n X -l abc ...           # no prop, no error (atoi->0->drop)
# A5 stream.dont-remix (the effective remix switch)
pw-cat -p -P node.name=T -P stream.dont-remix=true --target <stereo sink> mono.wav
   # -> stream publishes output_MONO->playback_FL only; monitor [8192, 0]
pw-cat -p -P node.name=T -P stream.dont-remix=true --target <mono sink> stereo.wav
   # -> output_FL->playback_MONO only; monitor peak 8192 @FL freq, FR dropped
# A6 inert props (land verbatim, assert no effect by content)
pw-cat -p -P node.dont-remix=true ...        # prop present, content unchanged
pw-cat -p -P channelmix.stereo-widen=1.0 ... # prop present, amp_at identical
pw-cat -p -P node.passive=true ...           # prop present, links+tone normal
# A7 dont-move silent no-op
pw-cat -p -P node.dont-move=true --target <nsA> tone.wav &
pactl move-sink-input <idx> <nsB>            # rc=0; edges stay on nsA
# B1 resampler: pitch verifies; disable->zeros; peaks->rectify
pw-cat -p --target <48k sink> tone44.wav                        # dom 1000/1500
pw-cat -p -P resample.disable=true --target <48k sink> tone44.wav  # monitor ALL-ZERO
pw-cat -p -P resample.peaks=true --target <48k sink> tone44.wav    # mean +4383, rectified, 1/12.3 zeroed
# B2 midi round-trip (the only working midi arms)
pw-mididump file.mid                # SMF->stdout printer (rc=0)
pw-mididump &                       # live sink: node 'midi-dump', input port, no autoconnect
pw-link 'Midi-Bridge:Midi Through: Port-0 (capture)' 'midi-dump:input'
aplaymidi -p 14:0 file.mid          # events print on pw-mididump stdout
pw-midiplay --target 0 -P node.name=T file.mid &
pw-link 'T:output_1' 'Midi-Bridge:Midi Through: Port-0 (playback)'
aseqdump -p 14:0                    # sees 'Note on 0, note 60, velocity 96'
pw-midiplay --target Midi-Bridge file.mid   # rc=1 'no target node available' (documented refusal)
# B3 serial targets
pw-loopback -n X -C <object.serial> -i stream.capture.sink=true -P <object.serial>
```

## 7. Falsification list

1. `-i`/`-o` accept space `k=v`, comma `k=v,k=v`, `{ k = v }`, `{ "k" = "v" }`,
   `{ "k": "v" }` — falsified by any of these forms failing to land all pairs
   verbatim on the respective node's pw-dump props.
2. `-i ''`/`-o ''` SIGSEGV — falsified by an empty-string leg that spawns both
   nodes (6/6 measured on 1.6.8).
3. Malformed `-i '}{ garbage'` silently drops the whole value — falsified by
   any prop landing or any stderr text.
4. `audio.position`/`audio.channels`/`channelmap.map` via `-i`/`-o` do NOT
   remix the copy — falsified by a prop-set mono leg producing the
   `0.5·(L+R)` signature in monitor content (flags `-c`/`-m` do produce it).
5. `stream.dont-remix=true` is effective, `node.dont-remix`/`channelmix.*` are
   inert — falsified by a `node.dont-remix` mono→stereo leg producing
   `[8192,0]`, or a `stream.dont-remix` leg that still upmixes.
6. Mono→stereo upmix duplicates at full amp; stereo→mono downmixes at
   `0.5·(L+R)` (amp@each freq = 4095.9, peak 7802) — falsified by halved
   upmix amp or unequal downmix gains.
7. `resample.disable=true` + 44.1k→48k → all-zero monitor — falsified by tone
   or pitch-shifted content in that leg (matched-rate legs carry tone fine).
8. `resample.peaks=true` + mismatch → rectified content (mean ≈ +4383, 1/12.3
   zeroed) — falsified by clean tone through the same leg (at matched rate it
   *is* clean).
9. `node.latency` units: `-l`=integer ms×48, `-d`=float s×16000, `-l` beats
   `-d` both orders — falsified by any other scale/precedence.
10. `-d 1.0` adds no measurable onset delay (~43 ms ≈ control) — falsified by
    first-tone-sample ≥ ~100 ms later than control through the loopback.
11. `pw-midiplay`/`pw-mididump` have no name-based or auto target resolution
    (`no target node available`, rc=1) — falsified by any name/auto leg
    linking without a manual pin.
12. pw-filter absent — falsified by `which pw-filter`/`pacman -Ql` finding it.
13. `-C`/`-P` resolve `object.serial` — falsified by a serial arg landing on
    the default sink/source instead.

## 8. Named classes added this round

| class | signature |
| --- | --- |
| `loopback_empty_props_segv` | `pw-loopback -i ''`/`-o ''` → SIGSEGV rc=139, "dumped core" (6/6) |
| `loopback_malformed_props_silent_drop` | non-empty garbage props → whole value dropped, defaults used, stderr empty |
| `prop_only_lands_no_effect` | `node.dont-remix`, `channelmix.*`, `audio.position` on loopback/pw-cat: verbatim in pw-dump, zero link/content change |
| `resample_disabled_zero_fill` | `resample.disable` + rate mismatch → links live, monitor all-zero, no error |
| `peaks_rectified_artifact` | `resample.peaks` + rate mismatch → half-wave rectified + periodic zeroed samples, mean ≈ +4383, dom bin DC |
| `midi_target_no_node` | midi play/dump target by name or auto → rc=1 `no target node available` |

## 9. Contamination ledger (mandatory)

Sibling seat live the whole window: **r78/r79 fold** (`--probe-capture-r78`,
pid 3130296 then restarted as 3341762; sinks `r78_prop_a/b_*`; recording the
SPDIF monitor and later `r78_prop_a`'s monitor). Its early legs had hijacked
the **default source** to `r78prop_class_source_stall` (a Source-class
null sink) during my recon; it recovered to `…Line__source` later — noted
because r79's capture fallback lands on the default source; none of my legs
depended on it (all `-C` targets were probe-owned sinks/serials).

This seat's footprint on shared objects:

| window | action | shared object touched |
| --- | --- | --- |
| 02:5x–03:0x | `pactl move-sink-input` P2 attempt → SPDIF | **none** — refused by `node.dont-move` (rc=0 no-op); zero tone reached SPDIF |
| ~03:0x | `pw-link` pins + `aplaymidi` on `Midi Through` (14:0) | ALSA seq broadcast bus — a foreign `aseqdump` would have seen my C4 note; links died with my clients |
| throughout | `pw-dump`/`pw-cli ls`/`pactl list` | read-only |

No tone ever targeted SPDIF (fail-closed: every tone leg pins a probe-owned
`-P`/sink). One known harness defect fixed live: `p3_midi.py` treated a
`P.sh` result dict as a Popen (killed before it could corrupt anything);
its first run's "nodes" list was polluted by in-flight p1 legs — the midi
verdicts above were re-measured after the fix.

## 10. Artifacts & provenance

`corpus/live/r83-scout/` (untracked): `r83_probe.py` harness; drivers
`p1_args.py`, `p2_filter.py`, `p3_midi.py`, `p4_remix.py`, `p5_resample.py`;
consolidated receipts `receipts/p{1-args,2-filter,3-midi,4-remix,5-resample}.json`;
evidence `raw/PK44_{1,2}.wav` (the rectified-peaks artifacts);
`scratch/r83_note.mid` (the 42-byte SMF used for both midi directions);
`scratch/mididump_out.txt`, `mplay_*`, `aseq_out.txt` witnesses. Tones are
regenerable via `r83_probe.ensure_tones()`. sha256 of any row available from
the receipts JSON.

**Confidence.** High: every headline law has ≥2 witnesses (prop + link, or
prop + content FFT), the segv is 6/6, the peaks artifact 2/2 deterministic,
the midi round-trip has ALSA-side witnesses both ways. Medium: the S6
48k→44k amp asymmetry (single observation, mechanism unexplained); the
`-r` remote flag (untested — no second remote); whether `channelmix.*` /
`resample.peaks` behave identically on non-pw-cat consumers.
