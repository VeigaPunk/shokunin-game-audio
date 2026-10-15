# R85 boundary — falsification of the r85 scout under host-state variation and load

**Seat: BOUNDARY (executor-class, leaf).** Host `plazir27`, lane
`~/Projects/shokunin/audio-shokunin` @ HEAD **`2333fac`** (the scout measured
`d9aa6f9`; the tree moved on between rounds — no file this seat touched is
tracked). Window **2026-10-15 19:33–20:05 UTC** (16:33–17:05 UTC−3).
Toolchain re-verified: **libsndfile 1.2.2** (`sndfile-metadata` and
`sndfile-resample` absent, as the scout said), PipeWire **1.6.8**,
pactl 17.0-98-gb096, Python 3.14.7.

**Zero tracked-file edits, no commits, no `set-default-*`, no engine writes.**
Every write is under `corpus/live/r85-boundary/` (harness `r85b_probe.py`,
`r85b_dbg.py`, `receipts/*.json`, `runs/**`, `keep/**` — receipts are the
durable evidence, raw capture wavs trimmed) plus this report. Every audio
object this seat created is named **`r85b_*`**; every module unload is
index-verified against its own `sink_name=`/`source_name=` line immediately
before the call (the scout's `mod_index()` sink-only grep is fixed in
`mod_line()`); nothing was ever unloaded by name. **Exit state (17:00 UTC):
`pactl list short modules | grep r85b` → 0 rows, `pw-dump` → no `r85b_*`
node, `pgrep -f r85b` → no client, hogs 0** (`receipts/final-cleanup.json`).

**Labrat.** The single permitted `probeParent` labrat was dispatched once for
a bounded Ogg page-diff hypothesis (no PipeWire, `/tmp` scratch only). Its
substrate exposed **no shell/exec tooling**, so it returned **UNSTABLE
(untested)** with zero evidence and zero side effects. Every measurement
below is seat-owned.

---

## 0. Verdict table

| # | r85 scout claim | verdict | sharpest measured fact |
| --- | --- | --- | --- |
| 1 | FLAC encode byte-identical ×3 | **CONFIRMED** | 3/3 identical (`67260 B`), same sha in the quiet and the 40-hog pass |
| 2 | OGG differs per encode only at byte 15 = serialno | **CONFIRMED in substance / FALSIFIED as stated** | 8/8 encodes distinct; every pair differs in **16 serialno bytes + 16 CRC bytes** (4 pages), **0 bytes outside those fields**; decoded payload identical across reps, ≠ source |
| 3 | no `-enc` = carry the input codec; incompatible → rc=1, no file, stdout-only | **CONFIRMED for PCM-family containers / FALSIFIED as a universal law** | `wav→o.ogg` **succeeds** (Vorbis, 3/3); `.bogusext` default is PCM24 **with no carry**; `.ogg` vs `.oga` disagree; carry proven for pcmu8/pcm24/pcm32/float32/ulaw/ima-adpcm and for 24-bit FLAC→WAV (payload-equal) |
| 4 | `-override-sample-rate` relabels, never resamples | **CONFIRMED + edge classes** | 44100: rate 44100, frames 72000, payload sha == source ×3; accepted for 1, 2, 8000…1 000 000; **`0`, `abc`, 2^32 are silent no-ops (rate stays 48000)**; **`-1` / 2^32−1 → rc=1 with a misleading codec-carriage message** |
| 5 | unknown extension → rc=0 silent WAV pcm24 | **PARTLY FALSIFIED** | 12 unknown suffixes (`.bogusext .xyz .XYZ .wavx .flacx .oggx .dwd .dff .mka .webm .mp4 .pcm`) → WAV/PCM24 432044 B, but **no extension at all → rc=1**, `.raw` → headerless PCM, `.mp3`/`.opus` → real lossy writers, `.oga/.xi/.svx/.wve` → rc=1 |
| 6 | content beats extension | **CONFIRMED** | flac-named-`.wav` reads `0x00170002`; ogg-named-`.wav` reads `0x00200060`; wav-named-`.flac` reads WAV; output format still chosen by the output extension |
| 7 | metadata survives wav↔flac↔ogg; **AIFF drops everything** | **CONFIRMED except AIFF / AIFF FALSIFIED** | wav→aif→wav recovers `INAM/ISFT/IART/ICMT` (3/3); the AIFF file itself shows **no tags in `sndfile-info`** — a *view* limit, not a storage limit; wav→wav control carries all 6 |
| 8 | `sndfile-info` errors are rc=0 | **CONFIRMED + extended** | rc=0 for missing/garbage/empty/dir/`/dev/null`/text; **truncated WAVs are accepted silently**: 60 B → `Frames 4`, 100 B → `Frames 14`, 1000 B → `Frames 239`, no error line |
| 9 | refusals: rc=1 + no file + stdout-only | **CONFIRMED + counterexample** | codec refusals leave no file (`refuse.wav` absent); **decode failure leaves a 44-byte WAV stub** (`-normalize` on silence → rc=1, `data` size 0, 3/3) |
| 10 | `sndfile-cmp` mismatch class (scout unknown) | **CLOSED** | PCM differ → rc=1 `sndfile-cmp: PCM data of files …`; length → rc=1; **samplerate differs → rc=1** even with identical payload; missing operand → rc=1 `Error opening`; one operand → usage |
| 11 | N streams → one sink: exact linear sum, zero bleed | **CONFIRMED** | 4 links → 2 ports (`playback_FL/FR`); `mix2` L1k 11999.6 / R2.5k 11999.6 with `R@1k = 0.0`, peak 12000 (quiet and under 40 hogs) |
| 12 | same file twice = exactly 2× (quantum-aligned) | **CONFIRMED, incl. under load** | 23999.2 = 2×11999.6 **6/6** (3 quiet + 3 with 40 hogs); 0.5 s-delayed duplicate also 23999.2 |
| 13 | sum > FS clips at the s16 tap | **CONFIRMED (numbers are phase-dependent)** | peak 32767, rail 3000/12000 samples per 0.25 s window (25 %) 5/5; fundamental 21264.2–21319.6 and spur 800.3–938.4 vary per rep (relative phase of the two tones) |
| 14 | `aplay -D pipewire` is env-targetable | **CONFIRMED + 3 new laws** | `PIPEWIRE_NODE` ✓, `PIPEWIRE_PROPS` ✓, **props win a conflict**, **bogus `PIPEWIRE_NODE` silently falls back to SPDIF**, **a numeric serial inside props is accepted** |
| 15 | source loss → `unlinked_sustained_zeros`, never re-links | **FALSIFIED as a deterministic class (bimodal)** | links die either way, but the file **froze** in 6/6 b5+b6 legs and in 4/7 debug legs, while 2/7 debug legs **kept growing with zeros** (the scout's shape) and 1 froze then grew — the scout's own `s3e` also contains a frozen rep (614444 B @ 3.23 s) |
| 16 | `media.class=Audio/Source` null-sink self-destructs on connect <60–110 ms | **CONFIRMED + widened** | module gone at the first 50 ms sample for pw-record/pw-cat/parec; **ffmpeg 0.105–0.195 s**; **pw-play into it kills it too (1/2 under load)**; survives ≥6 s idle 6/6; **survives a manual `pw-link` 4/4**; the prop leg never touches it (default-monitor fallback) |
| 17 | `--target` addressing lattice | **CONFIRMED in part / corrected** | sink serial noprop → monitor ✓; source serial noprop → source ✓; **source `object.id` noprop also binds** (scout: stall); **sink *name* noprop silently binds an arbitrary source** (scout: stall); prop + any name → default monitor |
| 18 | late-appearing conforming source re-arms a stalled record | **CLOSED (scout unknown)** | absent-name stall + `module-remap-source` appearing at 1.5 s → no link, 44 B, 3/3 quiet + 3/3 load |
| 19 | pactl number = `object.serial`, never `object.id` | **CONFIRMED incl. a name collision** | `object.id` → `No such entity`; serial ✓; with a sink **named** with another sink's serial, `move-sink-input <N>` still lands on the serial holder (`r85b_ca`) |
| 20 | `pactl get-sink-volume 0` is ambiguous | **RESOLVED** | with r85b_a=13 %, r85b_b=27 %, `0` → **40 % = the live default sink (SPDIF)**; `get-source-volume 0` → default source (100 %) |
| 21 | serials monotonic, never recycled; module indices recycle | **CONFIRMED, sharper** | 6+6 unload/reload cycles strictly increasing (101532→101630; 102303→102406); **the module index is reused immediately — the same index for all 6 cycles** |
| 22 | monitor source shares its sink's serial | **CONFIRMED** | `get-source-volume <sink serial>` rc=0, and `<name>.monitor` rc=0 |
| 23 | `move-sink-input` name/serial; bogus → rc=1 unmoved | **CONFIRMED** | both move (links follow); bogus `No such entity`, stream stays |
| 24 | pactl verb arg classes (`@DEFAULT_*`, `.monitor`) | **CONFIRMED** | `@DEFAULT_SINK@` ✓ as sink; `@DEFAULT_SOURCE@`/`@DEFAULT_MONITOR@` ✗ as sink, ✓ as source; `<sink>.monitor` ✗ as sink, ✓ as source; `""` → `Operation failed: Invalid argument` |
| 25 | *(not claimed)* monitor-tap gain is stable | **NEW HAZARD** | the first full battery recorded **digital silence in 15/15 tap legs**; two ad-hoc legs recorded exactly **1/8 (−18 dB)**; 18/18 + 6/6 link-validated reps then recorded exactly 1.0 — an amplitude arm must check the tap link **and** a solo reference |

---

## 1. FRONTIER — sndfile lattice (`receipts/b1-sndfile.json`, `b2-sndfile.json`,
`b1x-modehunt.json`, `b9-verify.json`, `b10-loose.json`)

### 1.1 What survived verbatim

- **A1** `src.wav → m.flac` ×3: identical sha (`bf341febd5…`), 67260 B; the
  same sha in the 40-hog pass. **A3** `flac → wav → raw` payload sha ==
  source raw sha, `sndfile-cmp` rc=0 (3/3). WAV→AIFF→WAV likewise lossless.
- **A2** 8 encodes, 8 distinct shas; decoded `-pcm16` payloads: **1 distinct
  sha** across 8 reps, ≠ source (lossy) — exactly the scout's law.
- **A4** `ogg → wav` no `-enc`: rc=1, **no file**, message on stdout
  (`The 'WAV' container does not support 'Vorbis' codec data.`), stderr empty.
  **A5** `-pcm16` unlocks it (rc=0, 288044 B).
- **A6** `-override-sample-rate=44100`: `Sample Rate 44100`, `Frames 72000`,
  payload sha == source (3/3).
- **A10** `-normalize` deterministic (3/3 identical), `Signal Max 32767`.
- The refusal lattice extends cleanly: from the Ogg source, **`-pcm16`/`-pcm24`/`-float32`
  beat the carry law** for `.wav .wavex .w64 .caf .bogus* .raw`
  (288044/432044/576088 B …) while `.oga .opus .mp3` still refuse.

### 1.2 Falsification 2 — the Ogg byte diff is serialno **+ CRC**, not "byte 15"

7 pairwise diffs of 8 encodes (b1) and 7 more (b2, under load): every pair has
**32 differing bytes in 4 of 7 pairs (31/31/28 in the other three — CRC bytes
that coincide by chance), 16 of them in the per-page serialno field and 16 in
the per-page CRC field of the 4 pages, 0 bytes outside either field**.
`cmp -l` first lines:
`15 14 164 / 16 360 274 / 17 356 211 / 18 64 70 / 23 141 37 …`.
So a page-diff arm must allow **serialno ∪ CRC**, and the "one random field"
framing is wrong by 16 bytes per pair. The same law holds for **Opus**
(`.opus`: 4/4 distinct, diffs confined, 0 outside, 5 pages) and for `.oga`
with `-vorbis` (4/4 distinct, 0 outside, 4 pages) — the muxer randomizes the
serial for **every Ogg-family writer**, not just Vorbis-in-`.ogg`.

### 1.3 Falsification 3 — "no `-enc` carries the codec" has hard carve-outs

Measured lattice (b1x, `flag_x_ext_from_pcm` / `flag_x_ext_from_ogg`, plus
b9 3-rep confirmations):

| input | output ext, no flag | result |
| --- | --- | --- |
| PCM16 wav | `.wav .wavex .w64 .rf64 .caf .aiff .au` | rc=0, **codec carried** (PCM16) |
| **PCM16 wav** | **`.ogg`** | **rc=0, Vorbis 10911 B** — the container's own codec, *not* carried |
| PCM16 wav | `.oga` | **rc=1** (`The 'OGG' container does not support '16 bit PCM' codec data.`) — carried and refused |
| PCM16 wav | `.opus` / `.mp3` | rc=0, Opus 23989 B / MP3 18432 B |
| Vorbis ogg | `.wav .wavex .w64 .caf` | rc=1 (`… does not support 'Vorbis' codec data.`) |
| Vorbis ogg | `.bogusext` | **rc=0, WAV/PCM24 432044 B** — default format, no carry |
| FLAC (24-bit) | `.wav` | rc=0, **PCM24 carried** (`0x00010003`), payload == input payload |

So `.ogg` and `.oga` are **different resolution paths** (3/3 each, both input
codecs), and the unknown-extension default **does not carry**. Carry itself is
real and codec-exact: pcmu8→pcmu8, pcm24→pcm24, pcm32→pcm32, float32→float32,
ulaw→ulaw, ima-adpcm→ima-adpcm, each payload-equal to the input (b9,
`carry_vs_default`) — so "wav→wav is byte-identical" is a *codec-preserving*
identity, not a PCM16-only accident.

### 1.4 Falsification 5 — the extension table is richer than "unknown → pcm24"

33 suffixes + 3 no-suffix shapes (b1, re-run in b2 under load, same results):

- WAV/PCM24 432044 B: `bogusext xyz XYZ wavx flacx oggx dwd dff mka webm mp4 pcm`, `<dot>` (`o.`), `o.wav.bak`;
- real containers: `opus mp3 aiff aifc au snd voc w64 rf64 mat4 mat5 paf nist ircam wav`;
- rc=1: `oga xi svx wve` (refusals: container can't hold the carried codec / mono-only format) and **`<nonext>` → `Not able to determine output file type`**;
- `.raw` → rc=0, **288000 B headerless PCM** (no container at all).

`.mp3` and `.opus` are real **writers** (the scout's §1.1 "no metadata writer
and no resampler" stands, but "the suite has no encoder but FLAC/Vorbis" does
not). MP3 output is byte-deterministic (3/3 identical); Opus/`.oga` are not
(see §1.2).

### 1.5 Falsification 7 — AIFF does not drop metadata; `sndfile-info` just hides it

3/3 reps: `tagged.wav → aif → wav` yields `INAM r85btitle`, `IART
r85bartist`, `ICMT r85bcmt`, `ISFT Lavf63.1.101 (libsndfile-1.2.2)`; the
direct `tagged.wav → wav` control yields all six (`INAM IART ICMT ICRD IPRD
ISFT`). `sndfile-info` on the `.aif` itself prints **no tag lines at all**
(`aif_info_text` in `b9-verify.json`), and the ffmpeg-written AIFF control
round-trips `INAM/ICMT`. Date and Album are lost in the AIFF hop; Title,
Artist, Comment survive. The scout's "AIFF drops everything" is true only as
a *reading* of `sndfile-info` output.

### 1.6 Falsification 4 — `-override-sample-rate` edge classes

| value | rc | output rate | frames | payload == source |
| --- | --- | --- | --- | --- |
| 44100 / 8000 / 96000 / 192000 / 384000 / 768000 / 1e6 | 0 | as given | 72000 | **yes** |
| `1`, `2` | 0 | 1, 2 | 72000 | **yes** |
| `0`, `abc`, `4294967296` | 0 | **48000 (no-op)** | 72000 | yes |
| `44100.5`, `" 44100"` | 0 | 44100 | 72000 | yes |
| **`-1`, `4294967295`** | **1** | — | — | — (`The 'WAV' container does not support '16 bit PCM' codec data.`) |

The last row matters for arm design: an out-of-range *rate* is reported with
the **codec-carriage error text**, so a classifier that greps
`does not support` cannot distinguish "codec carried into a wrong container"
from "sample rate out of int32 range".

### 1.7 Other named classes and stubs

- `sndfile-info` rc=0 for `/nonexistent`, garbage, empty, a directory,
  `/dev/null`, `/etc/hostname`; truncated WAVs (44/60/100/1000 B) are rc=0
  with **no error line** and a bogus frame count (`0/4/14/239`); 12 B →
  `Not able to open input file`, 44 B → `psf_fread returned short count.`
- **Decode-failure stub**: `sndfile-convert -normalize` on a silent or
  1-frame input → **rc=1 and a 44-byte WAV remains** (RIFF size 8, `data`
  size 0, `Frames 0`), 3/3 in `b10-loose.json` plus b1x. Codec refusals
  (`ogg→wav`) leave **no** file, so "rc=1 ⇒ no artifact" is class-specific.
- `sndfile-cmp` mismatch classes are now measured (see table row 10).
- `-endian=big` on `.wav` → `RIFX`; on `.flac`/`.ogg` → rc=1; on `.aiff`/`.caf`
  → rc=0 with unchanged magic.
- Error census: `conv_one_arg`/`conv_zero_arg` → usage rc=1;
  `conv_bad_flag` → `Not able to decode argument '-bogusflag'.`;
  `conv_ovr_noval` → `Not able to decode argument '-override-sample-rate'.`;
  a **directory** as output → `Not able to determine output file type`.

---

## 2. FRONTIER — mixing and `aplay` (`receipts/b3-mix.json`, `b4-mix.json`,
`b3t-tapstab.json`, `b3tr-tapstab.json`, `namereuse.json`, `gain.json`)

All legs: seat sink `r85b_mix`, monitor tap `pw-record -P
stream.capture.sink=true … --target r85b_mix`, 0.25 s windows, 3 reps quiet
(**b3**) and 3 reps with 40 CPU hogs (**b4**).

| leg | quiet (b3) | 40 hogs (b4) |
| --- | --- | --- |
| `mix1` solo L1k@12000 | 11999.6 / peak 12000 / rail 0 | 11999.6 / 12000 / 0 |
| `mix2` L1k + R2.5k | L 11999.6, R 11999.6, **R@1k = 0.0** | same |
| `mixdup` a1k twice | **23999.2** = 2× | **23999.2** = 2× |
| `mixdelay` +0.5 s duplicate | 23999.2 after both start | 23999.2 |
| `mixinv` mono1k + inverted | **cancels to 0** (3/3) | cancels 2/3; **1 rep = 20784 = 1.732×** |
| `mixclip` h1k+h25 | peak **32767**, rail **3000/12000** (25 %), L 21319.6 (2 reps) / 21264.2 (1 rep), spur 800.3 / 938.4 | 32767, 3000, 21319.6/21323.0, spur 800.3 |

- 4 links → exactly 2 port objects (`playback_FL/FR`) on every leg — the
  scout's topology claim reproduced.
- The **inverted-duplicate leg is the sharp probe the scout's battery lacked**:
  cancellation to digital zero proves the two `pw-play` streams are aligned to
  better than a quarter period (≈0.25 ms at 1 kHz). Under 40 hogs one rep
  slipped by ~1/3 ms (residual 20784 = 2·|sin(πfδ)| with δ ≈ 16 samples) while
  `mixdup` still summed to exactly 2× in the same window — so "quantum-aligned"
  is a **mostly-stable, not guaranteed** property under load.
- The clip **fractions** (25 % rail, peak 32767) are stable; the fundamental
  and spur numbers move with the two tones' relative phase (21264.2 ↔ 21319.6,
  938.4 ↔ 800.3), so the scout's exact amplitudes are one phase realization.
- `aplay -D pipewire` (b3+b4, 2 reps each): `PIPEWIRE_NODE=<sink>` and
  `PIPEWIRE_PROPS='{ target.object=<sink> }'` both publish
  `target.object` and link to the named sink; **no env → SPDIF**;
  **`PIPEWIRE_NODE=no_such_sink_r85b` publishes the bogus name but links to
  SPDIF (silent fallback)**; **`PIPEWIRE_NODE=<sink>` + `PIPEWIRE_PROPS='{
  target.object=<other> }'` → props win** (links to `r85b_alt`);
  **`target.object=<serial>` inside props resolves** (links to the sink).

### 2.1 NEW HAZARD — the monitor tap is not gain-stable

- The **first** full battery (b3+b4 pass 1: 5 mix legs × 3 reps × 2 stages =
  30 tap legs) recorded **digital silence in every leg** (`peak 0`,
  `zeros 12000/12000` per window) while the players' links were correct; that
  battery is vacuous and was discarded.
- Two ad-hoc legs recorded the same tone at **exactly 1/8 amplitude**
  (`12000 → 1500`, −18 dB, clean 1 kHz spectrum; kept as
  `keep/tap_1of8_manual2.wav`, `keep/tap_1of8_manual3.wav`).
- After the harness began **validating the tap's link before playing** (and
  recording it), 12/12 fresh-sink reps (`b3t`), 6/6 reused-sink reps
  (`b3tr`), 6/6 node-name-reuse reps and 4/4 linked debug taps recorded
  **exactly 1.0** (`11999.6`), with the tap link
  `r85b_mix:monitor_FL → input_FL`.
- Mechanism unread (no volume was ever issued on a tap or mix sink; the sink
  volume read 100 % in every sampled leg). **Consequence for arms: an
  amplitude claim (A12/A13, "2×", "32767") must record the tap link and a
  solo reference in the same run; a bare amplitude assertion can read 0 or
  1/8 without any visible error.**
- Disclosed confound: the re-run of b3/b4 happened while **two stale
  `r85b_mix` nodes** existed (left by a crashed intermediate attempt — my
  harness bug, §5), so `--target r85b_mix` was name-ambiguous in that window.
  The re-run's amplitudes are internally consistent (solo 11999.6,
  duplicate 23999.2) and match the scout, but the ambiguity is a real
  hazard of the shape and is now recorded in the receipts
  (`sink_nodes` lists every node with that name).

---

## 3. FRONTIER — capture-side loss and the self-destruct node
(`receipts/b5-cap.json`, `b6-cap.json`, `dbg.json`)

### 3.1 FALSIFICATION 15 — the post-loss artifact is bimodal, not "sustained zeros"

Instrument: `module-remap-source master=r85b_tone.monitor source_name=r85b_v*`
carrying a 1 kHz tone; `pw-record --target <vsrc>` (no prop); module unloaded
at t≈1.5 s with the index re-verified immediately before the call.

| dataset | legs | file after the loss |
| --- | --- | --- |
| b5 (quiet window) | 3 | **frozen** — sizes 303148/319532/303148 constant to 4.6 s |
| b6 (40 hogs) | 3 | **frozen** — 327724/311340/323628 constant |
| `dbg.json` | 7 | **4 froze** (294956/294956/397356/286764), **2 grew with zeros** (897068, 892972; +409600 B after the loss ≈ 192 KB/s), 1 froze then grew (471084) |
| scout `s3e-vsrc-loss.json` | 3 | 1 grew to the end (876588), **1 froze at 3.23 s** (614444), 1 grew |

In every case the links die (`{}`), no re-link occurs, and the process stays
alive (killed by the seat). So the *law* is "the links are destroyed and never
re-created"; the *artifact shape* — growing zeros vs frozen last-buffer — is
**not deterministic** on this host (mechanism unread: whichever daemon keeps
the unlinked stream scheduled). An arm that asserts "file keeps growing at
192 KB/s of zeros" is a coin flip; the safe assertions are "links {}",
"never re-links", "process alive", and "no new content".

### 3.2 CLOSED (scout §3.5) — no late-bind for a conforming source

`pw-record --target r85b_late` (absent name, no prop) stalls at 44 B; loading
`module-remap-source … source_name=r85b_late` at t=1.5 s produced **no link in
3/3 quiet and 3/3 load reps** (final 44 B, late node alive at exit). The
scout's confound ("the created source may have self-destructed") does not
apply: a remap source is conforming and survived. The `--target 0` + manual
`pw-link` variant they proposed is therefore not needed to answer this.

### 3.3 CONFIRMED + widened — the `Audio/Source` null-sink self-destruct

`pactl load-module module-null-sink sink_name=r85b_sd media.class=Audio/Source`
(1 port `capture_FR`, as r80 measured):

| client | module death | node death | file |
| --- | --- | --- | --- |
| idle 6 s (3 reps) | never | never | — |
| `pw-record` noprop (4) | **t = 0.0 s** (first 50 ms sample) | 0.0–0.14 s | 44 B |
| `pw-cat -r` (4) | 0.0 s | 0.10–0.14 s | 44 B |
| `parec -d` (4) | 0.0 s | 0.0–0.17 s | 44 B |
| `ffmpeg -f pulse -i` (4) | **0.105–0.114 s quiet / 0.166–0.195 s load** | same | no file |
| `pw-play --target` (playback!) (4) | never ×3, **0.501 s ×1 (load)** | same | — |
| `pw-record` **with** the prop (4) | never | never | 225–241 KB (default-monitor fallback) |
| manual `pw-link …:capture_FR r85b_tone:playback_FL` (4) | never | never | link present, node alive ≥1.2 s |

So the teardown is triggered by a **client bind**, not by any link: pw-record
is fastest (<50 ms, faster than the scout's 60–110 ms), ffmpeg is 2–4× slower
and load-sensitive, and even a *playback* stream can trigger it. The prop
form never touches the node — it captures the default sink monitor (scout
§3.4 confirmed 4/4, `vsrc_name_prop` → `SPDIF:monitor_*`).

### 3.4 CORRECTED — `--target` capture addressing (quiet b5 / load b6 identical)

| target form | prop | binds to |
| --- | --- | --- |
| `r85b_tone` (sink name) | **yes** | `r85b_tone:monitor_*` ✓ |
| `r85b_tone` (sink name) | no | **`r85b_addr:capture_*` — an arbitrary source node, not a stall** |
| `<sink serial>` | no | `r85b_tone:monitor_*` ✓ (numeric bypass, scout A20 confirmed) |
| `r85b_addr` (source name) | no | `r85b_addr:capture_*` ✓ |
| `<source serial>` | no | `r85b_addr:capture_*` ✓ |
| `<source object.id>` | no | `r85b_addr:capture_*` ✓ (**scout: 44 B stall**) |
| `@DEFAULT_MONITOR@` | yes | `SPDIF:monitor_*` ✓ |

Two corrections to the scout's namespace table: on the capture side a bare
**sink name without the prop does not stall — it silently binds some available
source** (in this window, the seat's own remap source), and a **source
`object.id` does resolve**. The scout's `object.id` stall was measured for a
*sink* id with/without the prop; on this host the object id of a source binds,
so "id never works on capture" is not a law.

### 3.5 CLOSED — `pactl` name/serial collision (`receipts/b7x-collision.json`)

With sink `r85b_ca` (serial **112331**) and a second sink literally **named
`112331`** alive at the same time: `pactl move-sink-input <stream> 112331`
moved the stream onto **`r85b_ca`** (the serial holder, links
`output_FL → r85b_ca:playback_FL`), so pactl's numeric argument keeps meaning
`object.serial` even when a node name shadows the digits. On the **pw-cat**
side the same numeric string bound nothing (`--target 112331` noprop → 44 B,
no links) because the *name* `112331` (a sink) matched first and the noprop
source path cannot use a sink — i.e. **the two surfaces disagree about what a
numeric string means when a name collides with it**.

---

## 4. FRONTIER — `pactl` addressing and reuse laws
(`receipts/b7-pactl.json`, `b8-pactl.json`)

Quiet and 40-hog passes are **identical** on every row below.

- **Verb-typed equivalence classes**: `get-sink-volume` accepts the node name
  and the serial; `get-source-volume` accepts `<name>.monitor` and the sink's
  serial (monitor shares it, rc=0 both verbs). `object.id` → `No such entity`.
  `@DEFAULT_SINK@` ✓ as sink / ✗ as source; `@DEFAULT_SOURCE@` and
  `@DEFAULT_MONITOR@` ✓ as source / ✗ as sink; `""` →
  `Operation failed: Invalid argument`; `-1`, `1`, `99999999`, bogus names →
  `No such entity`.
- **`0` is now resolved**: with r85b_a=13 %, r85b_b=27 %, `get-sink-volume 0`
  → **40 %**, the live default sink (SPDIF, 40 %); `get-source-volume 0` →
  100 %, the default source. So the scout's ambiguity is "0 = default", not a
  random small index.
- **Numeric parse edges** (`get-sink-volume`, serial 100850/101675):
  `" 100850"`, `"+100850"`, `"100850.0"`, `"100850x"`, `"100850 "`, `"0x18A52"`
  all rc=0; `"31_599"` → rc=1. **`"0100850"` → rc=0 in b7 but `"0101675"` →
  rc=1 in b8** — a leading zero is not decimal (consistent with a base-0 /
  octal parse; mechanism unread, both rows kept).
- **Serials vs module indices**: 6 unload/reload cycles quiet
  (101532→101630) and 6 under load (102303→102406), all distinct and strictly
  increasing; the **module index returned by `load-module` was the same for
  all 6 cycles** (b7: 536870927 ×6; b8: 536870926 ×2, 536870929 ×4) — module
  indices are recycled immediately while serials are monotonic, sharper than
  "LIFO-recycled".
- `move-sink-input`: by name ✓, by serial ✓ (links follow), bogus → rc=1
  `No such entity` and the stream stays on its original sink.

---

## 5. Harness bugs, instabilities and contention (mandatory disclosure)

1. **My first mix battery was vacuous**: b3/b4 pass 1 recorded digital silence
   in 30/30 tap legs (5 legs × 3 reps × 2 stages; evidence:
   `runs/stage-b3.log`, `runs/stage-b4.log` — every leg printed
   `(0.0, 0.0, 0, 0)`) while the players' links were correct. Pass 2 added
   tap-link validation and a solo reference; only then did the amplitudes
   reproduce the scout's numbers, and the receipts hold that validated pass.
2. **My `lattice_from_ogg` in b1 was vacuous for the flag**: the loop appended
   `conv(ogg0, o)` without passing `enc`, so those rows measured no-flag legs.
   The valid flag×container lattice is `b1x-modehunt.json`
   (`flag_x_ext_from_ogg`), re-confirmed 3/3 in b9.
3. **`b9` stub rows are mis-specified** (`-normalize` omitted); the stub claim
   rests on `b1x-modehunt.json` `stub_on_failure` and the 3/3 re-run in
   `b10-loose.json`. The `b1x` `lossy_determinism` `.oga` row is likewise
   vacuous (no flag from a PCM source → refusal, no file); the valid
   `.oga` determinism measurement is `b9-verify.json` `det_oga` (`-vorbis`).
4. **A crashed intermediate run left two stale `r85b_mix` nodes** (name
   ambiguity during the b3/b4 re-run) and, after a killed driver launch, 12
   stray `yes` hogs — both cleaned up (hogs at 16:42, modules at 16:56) and
   recorded. `hogs.pid` + `kill_stray_hogs()` now guarantee only seat-owned
   hogs are ever killed.
5. **Contention ledger.** Foreign work was live for the whole window: r82ff
   (`r82_probe.py`/ffmpeg, `r82ff_ns_3036129`), r93 scout
   (`probes/r93driver.py` battery, `r93s_in`/`r93s_fc_in`), r84b
   (`r84b_ns`/`r84b_tb`), **r95b** (`run_matrix.sh load` with 15 `yes` +
   12 `r95b_hog`), game-dev-2d/3d batteries (`run_battery.py`), `ocr.py`
   (~100 % CPU), browser-use/CLI-agent servers. Loadavg over the window:
   **2.7 → 108** (per-stage values in every receipt's `load_at_start/end`).
   This seat added 40 `yes` hogs for each "under load" stage only, and they
   are killed in a `finally`; quiet passes are therefore *quiet relative to
   the load passes*, not idle-host measurements. **No `set-default-*` was ever
   issued; the default sink stayed `…HiFi__SPDIF__sink` in the baseline and
   final census.** Tone anchors lived only on `r85b_*` sinks; the only
   default-sink plays were `aplay` **silence** legs and the explicit
   fallback witnesses.

---

## 6. Remaining unknowns (honest edges)

- The tap **gain/liveness instability** (§2.1) is characterised (0, 1/8, 1)
  but not explained; no volume was ever set on a seat sink, and 24/24
  later link-validated reps were 1.0.
- The **freeze-vs-zeros** switch after a capture target dies (§3.1) is
  bimodal within identical legs; the scheduling state that decides it was not
  read.
- **Who tears down the `Audio/Source` null-sink** remains unread (the scout's
  own unknown); this round only widens the *client* set that triggers it and
  shows a manual link does not.
- The **`0<digits>` parse** differs between two runs (rc=0 vs rc=1); the
  octal-parse reading is a hypothesis, not a measurement.
- **`-override-sample-rate`'s int32 boundary** (refusal at −1 and 2^32−1 but
  silent no-op at 2^32) was measured, not explained.
- The **AIFF tag mapping** is measured at the field level
  (Title/Artist/Comment survive, Date/Album do not) but the chunk layout
  libsndfile writes was not read.

---

## 7. Receipts index

| artifact | sha256 (prefix) |
| --- | --- |
| `receipts/b0-baseline.json` (census) | `1326a972b6e32c07` |
| `receipts/b1-sndfile.json` (quiet lattice) | `be3142e1d8ae9503` |
| `receipts/b1x-modehunt.json` (mode hunts) | `aabcb1713eb0bce0` |
| `receipts/b2-sndfile.json` (40-hog lattice) | `3593fd85b84a3a80` |
| `receipts/b3-mix.json` / `b4-mix.json` (mix quiet / load) | `68469930beed6987` / `b1379d7210c760ac` |
| `receipts/b3t-tapstab.json` / `b3tr-tapstab.json` (12+6 taps) | `80dad3834a747e3f` / `59467285000f9184` |
| `receipts/b5-cap.json` / `b6-cap.json` (capture quiet / load) | `960ea1a05bb97348` / `9fdd46e1490dd49b` |
| `receipts/b7-pactl.json` / `b8-pactl.json` (pactl quiet / load) | `25d3c633fb23b0c2` / `3d6d58b62cc43f71` |
| `receipts/b7x-collision.json` (name/serial collision) | `c9b9d27a96faedd9` |
| `receipts/b9-verify.json` (tight re-verification) | `7563b8b6b6c39c69` |
| `receipts/b10-loose.json` (normalize stub 3/3) | `083a9af9460d1801` |
| `receipts/dbg.json` (tap shapes + freeze/zeros ladder) | `d5996da39b6feabc` |
| `receipts/gain.json`, `namereuse.json` (gain probes) | `fc8e8e83976d50f4` / `3eb6d8f68445d181` |
| `receipts/final-cleanup.json` (exit state) | `9f2bf92092ffde3c` |

Harness: `r85b_probe.py` (stages `b0 b1 b1x b2 b3 b3t b4 b5 b6 b7 b7x b8 b9
cleanup`), `r85b_dbg.py`, `run_stages.sh`, `summary.py`. Example captures kept
in `keep/` (`mixdup_r0.wav`, `mixinv_r0.wav`, `mixinv_load_r2.wav`,
`mixclip_r2.wav`, `a14_r0.wav`, `cap_froze.wav`, `cap_grew_serial.wav`).
**Verdicts here are seat-side falsification attempts; the canonical Rust
runtime remains the only judge.**
