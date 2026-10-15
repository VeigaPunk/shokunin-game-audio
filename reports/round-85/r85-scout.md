# R85 scout — the sndfile/format + multi-file concurrency surface

Round 85 pre-measurement. Host `plazir27`, measured **2026-10-15 ~03:00–03:25
UTC−3**. Repo `~/Projects/shokunin/audio-shokunin` @ HEAD `d9aa6f9`.
Toolchain: **libsndfile 1.2.2** (sndfile-info/convert/cmp/deinterleave/
interleave/salvage/play; `sndfile-metadata` and `sndfile-resample`
**absent**), PipeWire **1.6.8**, libpulse **17.0-98-gb096** (protocol 35),
alsa-utils **1.2.16**, ffmpeg **n9.0.1**, Python **3.14.7** (numpy 2.5.3;
**no `soundfile` module**), Linux **7.2.3-arch1-3**.

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/r85-scout/` (2.6 MB at exit; capture wavs trimmed — receipts
are the durable evidence) plus this report.** Own harness `r85_probe.py`
(s0 baseline / s1 sndfile / s2 mixing / s3 capture-loss / s4 addressing),
own tone generator + FFT classifier. `corpus/fixtures` never read,
imported or executed. Every PipeWire leg targets seat-owned
`module-null-sink`/`module-remap-source` nodes named `r85snd_*`; every
unload was index-verified against the seat's own sink name immediately
before the call; nothing was ever unloaded by name.

**Contention.** Four foreign seats were live for the whole window: r82ff
(`r82_probe.py capture`, ffmpeg legs, owns `r82ff_ns`), r84alsa
(`run_arms.py`, owns **two** `r84alsa_ns` null sinks sharing one name),
r83dsp (pw-loopback DSP props), r78fol (folded `measure_audio.py
--probe-capture-r78`, own sinks + a `pw-play` falling back to the default
sink). §10 is the ledger, including one interference event **into** this
seat (a null-source vanished between measurements under concurrent seats).

---

## 0. Headline — the frontier cells

| # | frontier item | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | `sndfile-convert` round-trips | **PINNED** | WAV→FLAC→WAV and WAV→AIFF→WAV are **payload-lossless** (raw sha == source); FLAC encodes **byte-identical** across reps; **OGG container bytes differ per encode** (random `Stream serialno`, e.g. 938879428 vs 261923668) while the decoded payload is byte-identical |
| 2 | auto-encoding law + refusal classes | **NEW LAW** | no `-enc` flag = *carry the input codec* → rc=1 + **no file** + error on **stdout** (stderr empty) whenever the destination container can't hold it (`The 'WAV' container does not support 'Vorbis' codec data.`); `-pcm16` unlocks the decode |
| 3 | `-override-sample-rate` | **RELABEL, NOT RESAMPLE** | 48k→44100 writes rate 44100, frames **unchanged** (72000), payload byte-identical; there is no SRC tool in the suite (`sndfile-resample` missing) |
| 4 | content-vs-extension | **CONTENT WINS** | flac-renamed-`.wav` reads `Format 0x00170002` (FLAC); wav-renamed-`.flac` reads WAV; **unknown extension** → rc=0 silent **WAV pcm24** output |
| 5 | metadata survival matrix | **MAPPED** | `sndfile-convert` carries Title/Artist/Comment/Date/Album wav↔flac↔ogg (LIST INFO ↔ Vorbis Comment), rewrites `software` to `Lavf63.1.101 (libsndfile-1.2.2)`, **AIFF drops everything**; `sndfile-info` prints them all (INFO `IART/ICMT/…`, Vorbis `title/…`) |
| 6 | N streams → one sink mixing | **EXACT LINEAR SUM, HARD-CLIPPED AT TAP** | 2 and 4 concurrent `pw-play` streams land on the **same** `playback_FL/FR` port objects (4 links → 2 ports); each tone keeps full amplitude (11999.6/12000, 7999.5/8000), zero channel bleed; **same file twice = exactly 2×** (coherent phase); sum >FS → s16 monitor rail 32767, 25 % of samples clipped + clip harmonics appear |
| 7 | `aplay -D pipewire` env targeting | **WORKS** | `PIPEWIRE_NODE=<sink>` and `PIPEWIRE_PROPS='{ target.object=<sink> }'` are honored by the ALSA plugin (prop lands, links to the named sink); aplay+pw-play mixed into one sink measured identical to pw-play×2 |
| 8 | capture-side source loss (`pw-record`) | **NEW CLASS CELL** | `pw-record --target <source>` (no prop) + delete source mid-record → **links die, file keeps growing at ~192 KB/s of ZEROS, process alive** — `unlinked_sustained_zeros`, NOT the r81 `pipewiresrc` freeze and NOT a re-link |
| 9 | `media.class=Audio/Source` null-sink | **SELF-DESTRUCTS ON CONNECT** | survives ≥6 s idle; a `pw-record --target` connect kills the **module** within <60–110 ms (node dies with it); record → 44 B stall. 6/6. The real-source control (`--target Line`) does not kill its node |
| 10 | pactl addressing lattice | **EQUIVALENCE CLASSES MAPPED** | pactl number = **`object.serial`** (never `object.id` — `No such entity`); `@DEFAULT_SINK@`/`@DEFAULT_MONITOR@`/`@DEFAULT_SOURCE@` **are valid pactl verbs args** (contrast module-arg position, r80); a monitor source **shares its sink's serial**; serials are **monotonic, never recycled** (31599→31698 on reload) |

---

## 1. FRONTIER — `sndfile-info`/`sndfile-convert` lattice
(`receipts/s1-sndfile.json`; every conversion leg 3 reps; source =
seat-generated 1.5 s stereo 48 kHz s16 dual-tone `tags/src.wav`,
sha `src_sha` in receipt)

### 1.1 Tool presence

| tool | status |
| --- | --- |
| `sndfile-info`, `sndfile-convert`, `sndfile-cmp`, `sndfile-deinterleave`, `sndfile-interleave`, `sndfile-salvage`, `sndfile-play` | **present** (libsndfile 1.2.2) |
| `sndfile-metadata`, `sndfile-resample` | **MISSING** — no metadata writer and no resampler in the suite; the only rate knob is `-override-sample-rate` (§1.4) and the only metadata writer is another tool (here: ffmpeg) |

### 1.2 Round-trips (3 reps; `toraw` = decode to `.raw` for payload compare)

| chain | encode determinism | hop2 | payload vs source |
| --- | --- | --- | --- |
| `wav → flac → wav → raw` | flac bytes **identical ×3** (`67260 B`) | rc=0 | **lossless** (`o.raw` sha == `src.raw` sha) |
| `wav → ogg` | **bytes differ ×3** (`eb97…`/`5341…/`30d2…`, 10911 B) | `ogg → wav` **rc=1 no-enc** | decode with `-pcm16`: identical sha ×3, but **≠ source** (lossy codec) |
| `wav → aif → wav → raw` | identical | rc=0 | **lossless** |
| `wav → wavex → wav` | rc=0 ×3 | rc=0 | — |
| `flac → ogg` | rc=0 | `ogg → flac` **rc=1 no-enc** | — |
| `wav → wav` identity | rc=0 | — | raw payload **byte-identical to source** |

- **OGG nondeterminism is the container serial**: `cmp` on two encodes differs
  at **byte 15** = the Ogg `Stream serialno` field (sndfile-info prints it:
  938879428, 261923668, …). Decoded PCM identical across reps → the *encoder*
  is deterministic, the *muxer* randomizes the serial. An arm must compare
  decoded payload, never the `.ogg` bytes.
- **`sndfile-cmp`**: identical-PCM pair → rc=0 silent. (A content-differing
  pair was not measured — my ogg-decode comparator file was absent because of
  the §1.3 refusal; `cmp` exists and exits rc=1 `Error opening <path>` on a
  missing operand.)

### 1.3 The auto-carry-codec law and refusal shapes

`sndfile-convert` with no encoding flag copies **the input codec** into the
output container. Measured lattice (3 implicit reps via chain + explicit):

| leg | rc | artifact | message (on **stdout** — stderr always empty) |
| --- | --- | --- | --- |
| `ogg → wav` (no enc) | **1** | **none** | `Error : output file format is invalid. The 'WAV' container does not support 'Vorbis' codec data.` |
| `ogg → flac` (no enc) | 1 | none | same family |
| `-vorbis → wav` | 1 | none | same |
| `-alac16 → wav` | 1 | none | (alac is CAF-only) |
| `-pcm16 → ogg` | 1 | none | (ogg needs a codec) |
| `-float32 → flac` | 1 | none | (flac is integer-only) |
| `-pcms8 → wav` | 1 | none | |
| `-gsm610 → wav` | 1 | none | (listed "WAV only", still refused — gsm610 needs `-format`-aware path) |
| `ogg → wav` **with `-pcm16`** | **0** | 288044 B wav | decode works — the refusal was codec-carriage, not decode |
| `-vorbis → ogg/.opus`, `-opus → .ogg/.opus`, `-alac16/-alac24 → caf` | 0 | real files | |

- **wav container accepts**: `-pcm16/24/32`, `-float32/64`, `-pcmu8`,
  `-ulaw`, `-alaw`, `-ima-adpcm`, `-ms-adpcm`.
- **All refusals print to stdout**, never stderr — a probe grepping stderr
  reads every refusal as silent success-with-no-file.
- **`sndfile-info` errors are rc=0**: missing file → rc=0 +
  `Error : Not able to open input file …` on stdout; garbage file → rc=0 +
  `Format not recognised.` on stdout. **Never judge sndfile-info by rc.**

### 1.4 `-override-sample-rate` = relabel

| leg | result ×3 reps |
| --- | --- |
| `-override-sample-rate=44100` on 48 kHz wav | rc=0, output `Sample Rate : 44100`, **`Frames : 72000` unchanged**, raw payload **byte-identical** to source, output sha identical ×3 |

It rewrites the header rate only — playback speed changes, sample count does
not. There is no actual SRC in the libsndfile CLI suite on this host.

### 1.5 Other measured knobs

- `-endian=little|big|cpu`: `big` produces **`RIFX`** magic (`52494658`),
  `little`/`cpu` → `RIFF`; byte-stable.
- `-normalize`: deterministic ×3, `Signal Max 32767 (-0.00 dB)` — scales to
  full scale.
- **Content sniffing beats the extension**: a flac file renamed `.wav` is
  read as `Format 0x00170002` (FLAC), a wav renamed `.flac` as WAV; both
  convert rc=0. Output format is chosen by the **output** extension only.
- **Unknown output extension** (`o.bogusext`) → rc=0, silent, and produces a
  **WAV file with pcm24** payload (`Format 0x00010003`, 432044 B). An arm
  that asserts "unknown ext = error" is wrong.

### 1.6 Metadata survival matrix (tags written by ffmpeg n9.0.1)

`sndfile-info` prints: wav `LIST INFO` (`IART/ICMT/ICRD/INAM/IPRD/ISFT`),
flac/ogg `Vorbis Comment` (lowercase), ogg also `Stream serialno`, `PCM
offset/end`, `Encoded by`. ffmpeg wrote title/artist/comment/date/album to
wav (all six incl `ISFT=Lavf63.1.101`) but only title/artist/date/album to
flac/ogg (no comment — ffmpeg-side mapping).

| hop | survives (libsndfile view) |
| --- | --- |
| `tagged.wav → flac` | title, artist, comment, date, album + `software: Lavf63.1.101 (libsndfile-1.2.2)` |
| `tagged.wav → ogg` | same full set |
| `tagged.flac → wav` | title→INAM, artist→IART, date→ICRD, album→IPRD |
| `tagged.wav → wav` | all six INFO fields, ISFT rewritten as above |
| `tagged.wav → aif` | **nothing** — no metadata chunks in output |
| `tagged.ogg → wav` | **rc=1 refusal** (codec law §1.3) — never reached metadata |

`software`/`ISFT` is rewritten to `<orig> (libsndfile-1.2.2)` on every hop —
libsndfile appends its own tag.

### 1.7 Error classes (named)

| class | signature | legs |
| --- | --- | --- |
| `sf_codec_carry_refusal` | rc=1, no file, stdout `The 'X' container does not support 'Y' codec data` | ogg→wav/flac no-enc; every illegal enc×container pair |
| `sf_open_refusal` | rc=1, stdout `Not able to open (input|output) file …` | missing input, bad output dir |
| `sf_arg_refusal` | rc=1, stdout `Not able to decode argument '-bogusflag'` / usage | bad flag, missing arg |
| `sf_info_rc0_lies` | **rc=0**, `Error :`/`Format not recognised.` on **stdout** | sndfile-info on missing/garbage files |

---

## 2. FRONTIER — concurrent streams on one sink (`receipts/s2-mixing.json`,
`s2b-extra.json`; all legs 3 reps, seat sink `r85snd_mix`)

### 2.1 Topology

Two `pw-play` streams targeted at `r85snd_mix` produce **4 links onto
exactly 2 distinct port objects** (`playback_FL`, `playback_FR`): every
stream's `output_FL` shares the same sink input port. Mixing is the
sink-side per-port sum, N links → 1 port.

### 2.2 Content law — linear sum, zero crosstalk, hard clip at the s16 tap

Monitor-tap FFT (0.25 s windows; steady rows shown; all reps identical):

| leg | L amp @1k | R @2.5k | 3k | 4.5k | peak | rail | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `mix1` (1 stream, L-only 1 kHz@12000) | **11999.6** | 0 | 0 | 0 | 12000 | 0 | passthrough |
| `mix2` (L1k@12000 + R2.5k@12000) | **11999.6** | **11999.6** | 0 | 0 | 12000 | 0 | both full-amp, **zero bleed** (R@1k=0.0) |
| `mix4` (+3k@8000 both +4.5k@8000 both) | 11999.6 | 11999.6 | 7999.4/7999.6 | 7999.5 | 25247 | 0 | all four preserved exactly |
| `mixdup` (same a1k.wav twice) | **23999.2** | 0 | — | — | 24000 | 0 | **exactly 2× — coherent in-phase sum** |
| `mixclip` (1k@24576 + 2.5k@24576 both ch) | 21264.2 both | 21236.4 both | +938.4 (3k spur) | +1875.4 | **32767** | **3000/12000 per window** | **hard clip at the tap**: 25 % of samples at rail, intermod/harmonic products appear |

- The two-streams-same-file doubling (23999.2 = 2×11999.6) means the two
  `pw-play` processes are **quantum-aligned** — sample-coherent through one
  null-sink clock. Do not assume decorrelation between concurrent streams.
- The clip signature (fundamental energy re-spread into 3 kHz/4.5 kHz bins)
  distinguishes a clipped sum from a clean 2× sum at the monitor.

### 2.3 `aplay -D pipewire` is env-targetable

| env | node prop | links |
| --- | --- | --- |
| `PIPEWIRE_NODE=r85snd_mix` | `target.object=r85snd_mix` on `alsa_playback.aplay` | `output_F* → r85snd_mix:playback_*` |
| `PIPEWIRE_PROPS='{ target.object=r85snd_mix }'` | same | same |
| *(none)* | no `target.object` | `→ SPDIF:playback_*` (default) |

`PIPEWIRE_NODE` is honored by the ALSA→PipeWire plugin (same env law r81
measured for gst and r78 for pw-cat). **aplay + pw-play mixed into one seat
sink reproduce the pw-play×2 cells exactly** (L1000=11999.6, R2500=11999.6).
All env tests used a **silence** file — no tone ever reached the shared
default sink from this seat.

---

## 3. FRONTIER — pw-record capture-side target loss
(`receipts/s3-srcloss.json`, `s3b/s3c/s3d/s3e*.json`; 3 reps each leg)

### 3.1 The measured cell — source-node deletion under a live `pw-record`

Instrument: `module-remap-source master=r85snd_tone.monitor
source_name=r85snd_wsrc<N>` gives a real deletable `Audio/Source` that
carries the 1 kHz tone (chain `tone:monitor_* → input.<vsrc>` →
`<vsrc>:capture_*`, measured). `pw-record --target <vsrc>` (no prop)
links `<vsrc>:capture_F{LR} → rec:input_*` at +0.11 s and records the tone
(peak 16383). At t≈1.5 s, `pactl unload-module <verified index>`:

| t | vsrc node | module | links | file |
| --- | --- | --- | --- | --- |
| 0.11 | ✓ | ✓ | `vsrc:capture_* → input_*` | growing |
| 1.5–1.61 | **✗** | **✗** | **{}** | sz 286764–311340 |
| →4.5 s | ✗ | ✗ | **{}** (never re-links) | keeps growing: fb 614444–876588 (~192 KB/s) |

Windows: peak **16383 → 0** at the loss boundary, then all-zero forever.
**3/3.**

**Law.** `pw-record` on a plain source node whose target dies mid-record:
the links are destroyed and **never re-created** (no default-source
substitution — the DualSense mic is never linked), the stream stays running,
and the file fills with **zeros at exactly the negotiated rate**. This is
r78's `unlinked_sustained_zeros` observed on the capture side via node
deletion (r78 produced it via `pw-link -d`).

### 3.2 The three-shape ladder on the same host event (target-node death)

| consumer | bound via | on target death |
| --- | --- | --- |
| `pw-record --target <source>` (no prop) | source `capture_*` | **`unlinked_sustained_zeros`** — grows at rate, all zeros, no re-link (this round, 3/3) |
| `pw-record -P stream.capture.sink=true --target <sink>` | sink `monitor_*` | **re-links to default sink monitor ≤0.11–0.2 s**, file keeps growing with real content (r80 L4 / r81 t7; **re-confirmed here 3/3**: SPDIF monitor at +0.11 s) |
| `gst pipewiresrc + prop` | sink `monitor_*` | **`capture_stall_frozen`** — file frozen at last buffer, process alive, silent (r81) |

So the r81 "pw-record re-links, pipewiresrc freezes" split is **prop-gated on
the pw side**: the re-link only exists for the `stream.capture.sink=true`
family (sink-monitor fallback). A bare source-targeted `pw-record` neither
re-links nor freezes — it zero-fills. Three clients × the same event → three
artifact shapes: growing-zeros, relinked-content, frozen.

### 3.3 `media.class=Audio/Source` null-sink self-destructs on connect

`pactl load-module module-null-sink sink_name=X media.class=Audio/Source`
creates a **single-port** source (`capture_FR` only — r80's "0/1 ports"
measured literally: one output port). Lifecycle: survives ≥6 s idle
(5/5 legs). The moment `pw-record --target X` (or `pw-cli destroy`) runs:
the **module** is gone by the next 50–100 ms sample and the node dies with
it — before any link forms; the record stalls at 44 B. 6/6 connect legs, and
in the instrumented run `mod=False` was already true at the first sample
(<50 ms after spawn) while the node still existed — **the module unload
precedes the node death**. A real source (`--target Line`) survives the same
connect fine, so this is the node shape being torn down, not pw-record
killing nodes. Mechanism unread (WirePlumber/pipewire-pulse teardown of a
non-conforming Source on bind is the consistent hypothesis).

Consequence for the frontier brief: the "delete the captured source
mid-record" cell is unreachable via a `media.class=Audio/Source` null-sink —
it dies *at connect*. `module-remap-source`/`module-virtual-source` are the
deletable real sources (they carry content via their `input.*` stream node).

### 3.4 Prop-on-source at connect (control)

`pw-record -P stream.capture.sink=true --target <Audio/Source>` → links to
the **default sink's monitor** at connect (3/3, r79 B12 reproduced): the
prop makes a source name resolve on the sink-monitor family — it never
touches the named source.

### 3.5 Target appearance mid-stall — inconclusive, honestly recorded

`pw-record --target <absent Audio/Source name>` stalls at 44 B; loading the
module mid-stall produced no link in 3/3 — **but** the created
Audio/Source null-sink may itself have died on the pending connect (§3.3),
so "no late-bind" is *not* established for a conforming source. Untested
variant that would settle it: `--target 0` stall + `pw-link` pin to a
late-created real source port.

---

## 4. FRONTIER — `pactl` short-name vs serial addressing
(`receipts/s4-pactl-addr.json`, `s4b-capaddr.json`; verb = read-only
`get-sink-volume`/`get-source-volume` unless noted)

Objects under test: `r85snd_a` (object.id **157**, object.serial **31599**),
`r85snd_b` (119/31607); `pactl list short` printed `31599`/`31607` —
**the pactl index column IS `object.serial`, not `object.id`.**

### 4.1 Sink-arg equivalence class

| arg | resolves? | note |
| --- | --- | --- |
| `r85snd_a` (node.name) | ✓ | |
| `31599` (object.serial) | ✓ | |
| `157` (**object.id**) | **✗ `No such entity`** | global ids are a different namespace |
| `@DEFAULT_SINK@` | ✓ | → the live default (SPDIF) |
| `@DEFAULT_SOURCE@`, `@DEFAULT_MONITOR@` | ✗ `No such entity` | typed per-verb |
| `r85snd_a.monitor` as a sink | ✗ `No such entity` | |
| `no_such_sink_r85`, `99999999`, `-1` | ✗ `No such entity` | |
| `""` | ✗ `Operation failed: Invalid argument` | different refusal text |
| **`0`** | **✓** | returns a volume row (40 %) — see edge note |

`0` is the only small integer that resolves (`1`,`2`,`5`,`46` →
`No such entity`); it returns the same 40 % volume as SPDIF and
hdmi-stereo (both happen to sit at 40 % — the target it names is
*ambiguous* on this host; recorded, not disambiguated).

### 4.2 Source-arg equivalence class

| arg | resolves? |
| --- | --- |
| `r85snd_a.monitor` | ✓ |
| `31599` (the *sink's* serial) | ✓ — **monitor source shares the sink's `object.serial`**; the verb selects the view (get-sink-volume vs get-source-volume on the same number both rc=0) |
| `@DEFAULT_MONITOR@` | ✓ |
| `r85snd_a` bare / `@DEFAULT_SINK@` / bogus | ✗ `No such entity` |

### 4.3 Namespace inversion vs `pw-cli`, and `pw-record --target`

| surface | `object.serial` (31599) | `object.id` (157) | node.name |
| --- | --- | --- | --- |
| `pactl get-sink-volume` | ✓ | ✗ | ✓ |
| `pw-cli info` | ✗ `unknown global '31599'` | ✓ | n/a |
| `pw-record --target` (capture) | **✓ — links `monitor_*` even WITHOUT the prop** | ✗ (prop→default-monitor fallback; noprop→44 B) | ✓ only with prop / noprop→44 B |

- **`--target <serial>` bypasses the `stream.capture.sink` gate**: a numeric
  sink target links its monitor ports even with the prop absent — name and
  number are NOT the same resolution path on capture. (r78p measured serial
  resolving on playback; this is the capture-side arm.)
- `pactl move-sink-input <stream-serial> <sink-name|sink-serial>` both move
  (rc=0, links follow); bogus sink → rc=1 `No such entity`, stream unmoved.
  **The sink-input index equals the stream's own `object.serial`** — one
  serial namespace serves sinks, sources and streams.
- **`object.serial` is monotonic**: unload+reload of the same `sink_name`
  gives 31599 → 31698, never the old number — contrast `pactl` **module**
  indices, which r80 measured LIFO-recycled. Two different reuse laws inside
  one index space family.

---

## 5. Arm table (verbatim-armable)

`NS` = seat-owned `module-null-sink` name; `VSRC` = `module-remap-source`
slave; `DEF` = `pactl get-default-sink` read live; `SRC.wav` = any 48 kHz
s16 stereo wav. All rows ≥3 reps.

| # | arm | expected |
| --- | --- | --- |
| A1 | `sndfile-convert SRC.wav o.flac` ×2 | rc=0; **two outputs byte-identical** (deterministic encoder) |
| A2 | `sndfile-convert SRC.wav o.ogg` ×2 | rc=0; outputs **differ at byte 15** (ogg serialno); `sndfile-convert -pcm16 o.ogg d.wav` decodes identically both reps |
| A3 | `sndfile-convert SRC.wav o2.wav; sndfile-convert o.flac b.wav; sndfile-cmp o2.wav b.wav` | rc=0 — **flac round-trip lossless** |
| A4 | `sndfile-convert o.ogg o.wav` (no `-enc`) | **rc=1, no file**, stdout `…does not support 'Vorbis' codec data.`, stderr empty |
| A5 | `sndfile-convert o.ogg d.wav` after adding `-pcm16` | rc=0, real wav |
| A6 | `sndfile-convert -override-sample-rate=44100 SRC.wav o.wav` | output `Sample Rate 44100`, frames unchanged, raw payload sha == source |
| A7 | `sndfile-convert SRC.wav o.bogusext` | rc=0 silent, **file exists**, `sndfile-info` → WAV `Bit Width 24` |
| A8 | flac-content renamed `.wav` → `sndfile-info` | reads `Format 0x00170002` (FLAC — content wins) |
| A9 | `sndfile-info /nonexistent.wav` | **rc=0**, `Error : Not able to open input file` on **stdout** |
| A10 | `sndfile-convert -normalize SRC.wav o.wav` ×2 | identical sha, `Signal Max 32767` |
| A11 | `PIPEWIRE_NODE=NS aplay -D pipewire -q any.wav` | node `alsa_playback.aplay` prop `target.object=NS`, links `→ NS:playback_*` |
| A12 | two `pw-play --target NS` of a stereo tone + monitor tap on NS | both tones at full amplitude on the tap; same file twice → **2× amplitude** |
| A13 | two 24576-amp tones concurrent → NS monitor | peak **32767**, ~25 % rail samples, clip harmonics present |
| A14 | `pw-record --target VSRC -n N f.wav`; unload VSRC module mid-record | links→{}, **file grows at rate with zeros**, process alive |
| A15 | `pactl load-module module-null-sink sink_name=X media.class=Audio/Source` then `pw-record --target X` | module+node die <110 ms; record stays 44 B unlinked |
| A16 | `pactl get-sink-volume <object.serial>` / `<node.name>` | rc=0, same row |
| A17 | `pactl get-sink-volume <object.id>` / `@DEFAULT_SOURCE@` (as sink) | rc=1 `Failed to get sink information: No such entity` |
| A18 | `pactl get-source-volume <sink-serial>` / `<name>.monitor` | rc=0 (monitor shares the serial) |
| A19 | `pw-cli info <object.id>` vs `<object.serial>` | id ✓; serial → `unknown global` |
| A20 | `pw-record -P stream.capture.sink=true --target <serial-of-sink>` | links `<sink>:monitor_*` — and **same without the prop** (numeric bypass) |
| A21 | `pactl get-sink-volume @DEFAULT_SINK@` | rc=0 → live default (special names DO work in pactl verbs) |
| A22 | unload+reload `sink_name=X` | new `object.serial` (monotonic; module index may recycle per r80) |

---

## 6. Falsification list

1. "FLAC encode is byte-deterministic" — two `sndfile-convert x.wav o.flac`
   runs with different shas.
2. "OGG differs only in serialno" — two ogg encodes whose **decoded raw**
   payloads differ, or whose byte diffs extend past the serial field.
3. "no-enc conversion carries the codec" — a `x.ogg→x.wav` no-enc leg that
   succeeds, or a `-vorbis→wav` leg that writes a file.
4. "override-sample-rate relabels" — an output whose frame count changes or
   whose payload sha differs from the source.
5. "unknown extension → wav pcm24" — an `o.xyz` leg that refuses or produces
   a different container.
6. "monitor tap mixes linearly" — a 2-stream leg where a tone's amp ≠ its
   solo amp by more than FFT noise (±1 %), or any cross-channel bleed >0.5 %.
7. "same-file-twice sums coherently" — `mixdup` amplitude ≠ ~2× solo
   (would mean streams aren't quantum-aligned — load-dependent?).
8. "the tap clips" — a sum>FS leg with peak <32767 in the s16 monitor.
9. "PIPEWIRE_NODE targets aplay" — a leg where `target.object` is absent or
   the links land on `<DEF>`.
10. "source loss → sustained zeros, no re-link" — an A14 leg with any
    post-loss link (mic, other source, sink monitor), or with bytes frozen.
11. "Audio/Source null-sink dies on connect" — a `--target X` capture leg
    where the node/module survive >1 s with or without a link.
12. "prop-on-source → default sink monitor" — an A15B-shaped leg linking to
    the named source itself.
13. "pactl number = object.serial" — a `get-sink-volume <object.id>` that
    resolves, or `<serial>` that fails.
14. "`--target <serial>` bypasses the prop gate" — a no-prop serial-target
    capture that stays unlinked (44 B).
15. "serials monotonic" — a reload reusing the old serial.
16. "info rc lies" — `sndfile-info` returning rc≠0 on a missing file.

## 7. Contention ledger (mandatory)

- **Foreign seats live all window**: r82ff (`r82_probe.py capture` + ffmpeg),
  r84alsa (`run_arms.py`, duplicate `r84alsa_ns` ×2), r83dsp, r78fol
  (`--probe-capture-r78`, `pw-play … --target no_such_sink_r78` → default
  sink, `r78fol_nofollow_tap` recorder). Default sink stayed SPDIF
  throughout; no `set-default-*` ever issued here.
- **This seat injected no content into shared sinks**: the only default-sink
  legs were `aplay -D pipewire` playing **silence.wav** (env-off control,
  2 reps). All tone anchors lived on `r85snd_*` nodes.
- **Interference into this seat (recorded, not attributed)**: between two
  adjacent exec windows a loaded `r85snd_src` module (index 536870921)
  disappeared without this seat unloading it — consistent with r80 §3.1's
  LIFO index-recycling hazard (a sibling holding a stale index) or foreign
  cleanup. Subsequent §3 legs were re-run with per-leg verify-immediately-
  before-unload; the self-destruct law (§3.3) is independently proven by the
  idle-lifecycle control (survives ≥6 s ×5 with no client).
- **Module-index bug found in my own harness (disclosed)**: `mod_index()`
  greps `sink_name=` — remap-source uses `source_name=`, so the first
  `vsrc` loss batch never actually unloaded (vacuous for loss, valid for
  the 2-hop chain data); 3 leaked modules were found and unloaded by index.
  Receipts `s3d-vsrc.json` (vacuous-for-loss) vs `s3e-vsrc-loss.json`
  (the real cell) are both kept.
- **Harness fix mid-run**: `runs/s4/` was missing on the first s4 pass →
  `pw-record` legs produced no file (8 vacuous rows kept in
  `s4-pactl-addr.json` `pw_target_addr`); fixed, re-run as
  `s4b-capaddr.json` (valid rows).
- Exit state: `pactl list short modules | grep r85` → **0 rows**; `pw-dump`
  → **no r85snd_* nodes**; scratch 2.6 MB.

## 8. Receipts index + remaining unknowns

| artifact | sha256 (prefix) |
| --- | --- |
| `receipts/s0-baseline.json` / `s0-final` via probe | `cb455d595edf4a84` |
| `receipts/s1-sndfile.json` | `b85957630ff125ac` |
| `receipts/s2-mixing.json` | `14410b0a298968f9` |
| `receipts/s2b-extra.json` (links-live + aplay mix) | `7997eb6bcf12e79a` |
| `receipts/s3-srcloss.json` | `58af5f6e898a3820` |
| `receipts/s3b-srcloss-def.json` | `fa45d372f4150fb3` |
| `receipts/s3c-lifecycle.json` | `5eed453eb7d08b3a` |
| `receipts/s3d-vsrc.json` (chain data; loss vacuous — §7) | `a639d147239a59f9` |
| `receipts/s3e-vsrc-loss.json` (the loss cell) | `99ec746c13903827` |
| `receipts/s4-pactl-addr.json` | `0cdd0af90b8bcc8b` |
| `receipts/s4b-capaddr.json` | `4ade21847f6e6078` |

**Remaining unknowns (honest edges).**

- The Audio/Source-null-sink teardown mechanism is characterised, not read
  (which daemon/peer unloads the module on connect is unknown).
- Whether a *conforming* late-appearing source re-arms a stalled
  `pw-record --target <name>` is unsettled (§3.5 confound).
- `pactl get-sink-volume 0` resolves to *some* sink (rc=0, 40 %) — likely
  the default; two candidate sinks share the volume so the target is
  ambiguous.
- `sndfile-cmp`'s content-mismatch exit code wasn't measured (only
  equal→rc=0 and missing-file→rc=1 `Error opening`).
- OGG byte-level nondeterminism beyond the serial field (e.g. granule
  jitter) is bounded only to "decoded payload identical"; a page-diff arm
  could tighten it.
- The 25 %-rail clip fraction is exact for two 0.75-FS sines of the tested
  frequencies; other freq/phase pairs give other fractions — the *law* is
  "saturates", the number is per-tone.
