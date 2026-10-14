# R77 scout — capture/playback frontier pre-measurement

Round: 77 (pre-measurement for the next capture frontier). Host `plazir27`,
measured 2026-10-14 ~16:20–16:45 UTC. Repo `~/Projects/shokunin/audio-shokunin`
@ HEAD `d566a317e6b849032c444155e933b33a102bbada`.

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/r77-scout/`.** Own harness (`r77_probe.py` + `probe_*.py`), own
classifiers — `corpus/fixtures` was never imported, so the live concurrent
edit to that file (see §7) cannot have shaped any number here.

Toolchain (this host, this session): PipeWire **1.6.8**, pacat/parec
**17.0-98-gb096** (libpulse 17.0.0, protocol 35), alsa-utils **1.2.16**,
ffmpeg **n9.0.1** (libavformat 63.1.101), SoX_ng **14.8.0.1**, Python
**3.14.7**, Linux 7.2.3-arch1-3.

---

## 0. Headline: five frontier claims, three of them falsify a prior r76 row

| # | frontier | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | source-selection lattice | **NEW LAW, pinned** | with `-P stream.capture.sink=true`, a *sink* target is honored but a *source* name / `default` / `pulse` / garbage **silently falls back to the DEFAULT sink's monitor** — same rc, same byte count, same finalized header, no stderr |
| 2 | hot-plug / target loss | **NEW CLASS** | destroying the captured node mid-run changes **nothing**: the capture keeps producing bytes at 100 % rate, rc=1, finalized header, empty stderr |
| 3 | format axis | **NEW LAW, pinned** | `pw-record` honors *every* legal `--format/--rate/--channels` (client-side convert) and refuses illegal ones by dumping `--help` at rc=1 **with no file at all**; `arecord -D hw:0,0` is **stereo-only** |
| 4 | cross-decoder disagreement | **NEW MATRIX, 5 witnesses** | on the same wound bytes: `wave` rejects / `soxi -s` says **0** / `sndfile-info` says **honest** / `ffprobe` says **honest**; on arecord-KILL `soxi -D` says **3 h 22 m** for a 2.4 s file |
| 5 | raw integrity | **CONFIRMED WEAK** | `parec --raw` severed by TERM and by KILL deliver **byte-identical 65536 B**; only `rc` separates them, and a pipe reader never sees rc |
| 6 | concurrent playback + capture | **NO HAZARD** | N concurrent `pw-record` captures of the *same* monitor node all carry the tone; no ordering hazard, no contention |
| 7 | provider freed mid-stream | **same as #2** | `pactl unload-module` of the null sink under capture → zero artifact change; plus a **device-dependent** arecord TERM shape (§4) |

---

## 1. FRONTIER 1 — the source-selection lattice (the round's main result)

**Method.** A 1 kHz stereo tone is played into the **default sink**
(SPDIF) with `pw-cat -p`, then a bounded capture is taken with a named
target. A capture that *carries the tone* consumed the default sink's
monitor; a silent capture consumed some other node. This anchor is essential:
**the Line and Mic sources on this host are digital silence**
(`nonzero_frac = 0.0`), so byte identity between two source captures is *not*
evidence of anything — my own first pass (probe A2/A3b) was misled by exactly
that, and the serialized tone-anchored re-run (§1.3) falsified it.

### 1.1 The law (probe `probe-capture-sink-lattice-r77.json`)

`pw-record -P stream.capture.sink=true --target T -n 96000`, tone into the
default sink:

| `--target T` | consumed the default monitor? | verdict |
| --- | --- | --- |
| `<default sink>` (`…SPDIF__sink`) | **yes** | target honored |
| `<default sink>.monitor` | **yes** | `.monitor` suffix accepted with the prop |
| `<other sink>` (`…Speaker__sink`) | no (silent) | **target honored** |
| `<other sink>` (`…hdmi-stereo`) | no (silent) | **target honored** |
| `<LINE source>` (a *real* node name) | **yes** | **silent fallback** |
| `@DEFAULT_SOURCE@` | **yes** | **silent fallback** |
| `@DEFAULT_MONITOR@` | **yes** | fallback (same node as default — indistinguishable here) |
| `default` | **yes** | **silent fallback** |
| `pulse` | **yes** | **silent fallback** |
| `no_such_node_xyz` | **yes** | **silent fallback** |
| *(no `--target` at all)* | **yes** | auto ⇒ default sink monitor (r76's idiom) |

Without the prop, the same lattice collapses: **only a real source node name
resolves** (`noprop|LINE_source` → 384000 B, rc=1, silent-and-correct);
`noprop|<sink>`, `noprop|<sink>.monitor` and `noprop|auto` all produce a
**44-byte finalized WAV with `data(0)`** at rc=1 — never a missing file,
never a nonzero rc.

### 1.2 The fallback is unobservable except by content or link topology

Every fallback cell and every honored cell share: `rc = 1`, a full-length
capture, a `finalized` RIFF header, the same container class, and **empty
stderr**. The two witnesses that separate them:

- **content** (the tone anchor above), or
- **`pw-link -l`** — for `prop|--target <MIC source>` the capture stream's
  `input_FL/FR` ports are fed by
  `alsa_output.…SPDIF__sink:monitor_FL/FR`, i.e. the **default** sink's
  monitor (`probe-override-extent2-r77.json`).

**And the stream's own advertised target lies.** In the same run the capture
object's props were
`{'target.object': 'alsa_input.…HiFi__Mic__source', 'stream.capture.sink': True}`
while it was consuming the SPDIF monitor. `pw-dump`'s `target.object` is a
**statement of intent, not of consumption**; only `pw-link -l`'s producer
list names the consumed node. This is a provenance trap for any future arm
that tries to certify "which node did we capture" from `pw-dump`.

### 1.3 Honest correction — a hypothesis I had to kill

My first pass (probe A2 `probe-target-override-r77.json`, A3b
`probe-override-extent2-r77.json`) showed `prop|target=<anything>` producing
**byte-identical 19244-byte payloads** (`sha 17744bb6a4ed1d9d`, `nz=0.0`) and
I provisionally read that as *"the prop overrides `--target` entirely"*. The
serialized tone-anchored re-run (`probe-override-content-serial-r77.json`)
**falsifies the strong form**: `prop|SPEAKER_sink` is **silent** while
`prop|SPDIF_sink` carries the tone, so a sink target *is* honored. The
byte-identity was silence — the default sink's monitor was also silent when
nothing was playing. The surviving, narrower law is §1.1. Recording this
because the byte-identity trap is exactly what a later arm would fall into.

### 1.4 Other lattice rows (`probe-source-lattice-r77.json`, 60 cells)

- `pw-record --target <unresolvable>` → rc=1, **`no_target_node`**, and a
  **44-byte finalized WAV**. Every unresolvable name lands this same shape
  (10/10 names measured). It is a *well-formed empty wav*, not an error file.
- `pw-record --target 0` → **no verdict within the 12 s bound** (documented
  "0 means don't link"), leaving a 44-byte `placeholder_8` file. Named class:
  `target_0_unlinked` / blocked.
- `parec -d <name> --raw` resolves `@DEFAULT_SOURCE@`, `@DEFAULT_MONITOR@`,
  a literal source, a literal `<sink>.monitor`, **and `0`**; it fails with
  `pa_no_such_entity` on `default`, `pulse`, and a bare sink name.
- `parec -d <name> --file-format=wav` **to a non-seekable stdout** fails
  `Failed to open audio file.` (rc=1) on *every* name — sndfile needs a
  seekable target. A container request on a pipe is a hard fail, not a
  silent downgrade to raw.
- `ffmpeg -f pulse -i <name>` works for literal sources and literal
  `<sink>.monitor`; `default`/`pulse`/bare-sink → rc=251 `ffmpeg_io`.
- `ffmpeg -f alsa -i <pulse name>` → rc=251 on every pulse name
  (`alsa_unknown_pcm` for most, `ffmpeg_alsa` for the literal `default`).
- `arecord -L` on this host is `{null, sysdefault, pipewire, default,
  sysdefault:CARD=Audio, front:CARD=Audio,DEV=0}` — **there is no `pulse`
  PCM**, so `arecord -D pulse` is `alsa_unknown_pcm` for all 13 format legs
  (`probe-format-axis-r77.json`). **arecord has no pulse route on this host.**

---

## 2. FRONTIER 2 + 7 — target loss and provider death are invisible

**Measured directly** (not via a module proxy): load a probe-owned
`module-null-sink`, capture its monitor with `pw-record -P
stream.capture.sink=true --target r77_v2`, then `pactl unload-module <id>`
mid-run. The unload **succeeds** (rc=0, sink gone from `pactl list sources`)
and:

```
before unload   286764 B
+1.5 s          569388 B      (still growing, 188416 B/s)
+2.5 s          761900 B      (192512 B/s ≈ 100 % of 48000×2ch×s16)
TERM            rc=1, header finalized, stderr empty
```

**The capture of a destroyed node keeps producing bytes at full rate, forever,
with rc=1 and a finalized header.** No partial-file shape. No error class. No
rc change. The only witnesses are (a) the content, or (b) an external link
query. I propose the named class **`sustained_after_target_loss`** (a
"zombie capture") — it is the exact capture-side analogue of the r76
finding that `rc` is never the verdict, one level worse: here *nothing* in
the artifact is the verdict.

Same shape for every consumer (`probe-hotplug-r77.json`), each **byte-identical
to its no-event baseline**:

| leg | baseline bytes | after target unload | rc | err |
| --- | --- | --- | --- | --- |
| `pw-record` (monitor, `-P`) | 421932 | **421932** | 1 | none |
| `parec --file-format=wav` | 65580 | **65580** | 0 | none |
| `ffmpeg -f pulse -i <mon>` | 489678 | **489678** | 255 | none |

Also measured, all with **no artifact difference from the baseline**:
`pactl set-default-source` mid-run (a `parec -d @DEFAULT_SOURCE@` stream does
**not** follow the new default — it is resolved at open), `pactl
suspend-source` mid-run, and `pactl set-source-mute` mid-run. The one leg that
*did* move: `pactl move-source-output <idx> <other-source>` returned rc=0 and
the stream ended as a **44-byte empty wav at rc=0** — but that is the
`parec --file-format=wav` granule degenerate (§4.3), not a move verdict.

---

## 3. FRONTIER 3 — the format axis (`probe-format-axis-r77.json`)

### 3.1 `pw-record` — total convert, or a usage refusal with *no file*

Every legal request is honored and the `fmt` chunk reports exactly what was
asked; the source's own format (Line `s24le 2ch 48000`, SPDIF monitor
`s16le`, Speaker monitor `s32le`) never constrains the output:

| request | bytes | reported `fmt` | note |
| --- | --- | --- | --- |
| `-n 4800` (baseline s16/2ch/48 k) | 19244 | `PCM/2/48000/16` | |
| `--format s24` / `s32` / `f32` / `f64` / `u8` | 28844 / 38444 / 38488 / 76888 / 9644 | `PCM/24`, `PCM/32`, `FLOAT/32`, `FLOAT/64`, `PCM/8` | all honored |
| `--format ulaw` | 9658 | `ULAW/2/48000/8` | 1 byte/sample, rate kept |
| `--rate 8000` / `44100` / `96000` / `192000` | 19244 each | rate reported verbatim | `-n` counts **frames**, so bytes are rate-invariant |
| `--channels 1` | 9644 | `PCM/1/48000/16` | downmix |
| `--channels 6` | 57680 | **tag 65534 (`WAVE_FORMAT_EXTENSIBLE`)**/6/48000/16 | upmix; extensible tag appears **on the capture side** |
| `--channels 1 --channel-map FL,FR` | **no file** | — | refused |

The four refusals (`--format bogus`, `--rate 0`, `--channels 0`,
`--channels 1 --channel-map FL,FR`) all land **rc=1, no output file at all,
and the tail of `pw-record --help` on stderr**. That is a named class worth
pinning: **`usage_refusal`** — a pre-capture argument rejection that never
touches the device and leaves *no file*, which is structurally different from
the `no_target_node` 44-byte empty wav. The `--quality 0|15` legs are
byte-identical to the default, so `-q` is not observable in the artifact.

### 3.2 `arecord` — `hw:0,0` is stereo-only; `null` is the format oracle

`arecord -D hw:0,0` accepts **only** `-f cd` (44.1 k/2ch) and `-f dat`
(48 k/2ch). Everything else — including `-f S16_LE` and `-r 44100` *alone*,
because arecord's default `-c` is **1** — lands `alsa_channels`
(`Channels count non available`), rc=1, no file. `-c 6` also fails. So the
device is stereo-only and the class `alsa_channels` covers both the too-few
and the too-many direction.

`arecord -D null` accepts every legal combination and reports it back
verbatim; its own default is **mono 8000 Hz**:

| request | bytes | reported |
| --- | --- | --- |
| `-f S16_LE` (defaults c=1, r=8000) | 16044 | `PCM/1/8000/16` |
| `-r 96000 -f S16_LE` | 192044 | `PCM/1/96000/16` |
| `-c 6 -f S16_LE` | 96044 | `PCM/6/8000/16` |
| `-f FLOAT_LE` | 32044 | `FLOAT/1/8000/32` |
| `-f BOGUS` | no file | rc=1, refused pre-capture |

Every `-D null -d 1` byte count is exactly `44 + rate × channels ×
bytes_per_sample` — the null device is the exact-arithmetic oracle and the
right place to pin format semantics.

### 3.3 `ffmpeg -f pulse` — input options are honored

`-sample_rate`/`-channels` are **input** options (before `-i`) and all seven
combinations succeeded (rc=0). `-sample_rate 96000` and `-channels 6` both
emit **fmt tag 65534 (`WAVE_FORMAT_EXTENSIBLE`)**; `-sample_rate 44100` and
`-channels 1` emit tag 1. So the extensible-tag boundary is a *muxer* rule
(rate > 48 k, channels > 2, or bits > 16) and it is reachable from both
`pw-record` and `ffmpeg` on the capture side — the r55–r64 UI-side
extensible axis has a capture-side twin that is not yet pinned.

---

## 4. FRONTIER 4 — the 5-witness cross-decoder matrix

`probe-sever-readers2-r77.json`: 9 consumers × {TERM, KILL} × 2 sever wall
times, each wound read by **five** independent witnesses. Unit calibration
first, because two of these readers are unit-ambiguous:

```
synthetic 96000-frame 2ch/48k wav:
  soxi -s                      -> 96000     == FRAMES, not interleaved samples
  sndfile-info `Frames`        -> 96000
  stdlib wave.getnframes()     -> 96000
  ffprobe stream.nb_read_frames-> 24        == a PACKET count; unusable as frames
  ffprobe stream/format.duration -> 2.000000 (size-derived, honest)
```

### 4.1 The matrix

| wound (w=2.5 s) | rc | bytes | riff field | data declared | honest | `wave` | `sndfile` | `soxi -s` | `soxi -D` | `ffprobe` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `pw-record` TERM | 1 | 475180 | finalized | finalized | 118784 | honest | honest | honest | 2.474667 | 2.474667 |
| `pw-record` KILL | −9 | 479276 | `placeholder_8` | `zero` | 119808 | **rejects** | **honest** | **0** | **0.000000** | 2.496000 |
| `pw-cat` KILL | −9 | 479276 | `placeholder_8` | `zero` | 119808 | **rejects** | **honest** | **0** | **0.000000** | 2.496000 |
| `parecord` KILL | −9 | 131116 | `placeholder_8` | `zero` | 32768 | **rejects** | **honest** | **0** | **0.000000** | 0.743039 |
| `arecord -D hw:0,0` TERM | 1 | 419120 | finalized | finalized | 104769 | honest | honest | honest | 2.375714 | 2.375714 |
| `arecord -D hw:0,0` KILL | −9 | 419032 | `other` | `placeholder_80000000` | 104747 | **inflated** | **honest** | **inflated** | **12173.943583** | 2.375215 |
| `ffmpeg -f pulse` TERM | 255 | 489678 | finalized | finalized | 122400 | honest | honest | honest | 2.550000 | 2.550000 |
| `ffmpeg -f pulse` KILL | −9 | 262144 | `placeholder_ff` | `placeholder_ff` | 65516 | **inflated** | **honest** | **0** | **0.000000** | 1.364938 |

**Every TERM cell: all five witnesses agree = honest. Every KILL cell: three-way
disagreement.**

### 4.2 Who is right

- **`sndfile-info` is honest in 11/11 wounds** — the only reader never wrong.
- **`ffprobe` (`format.duration`) is honest whenever it answers**; it abstains
  (`null`) on the 44-byte files, which is honest abstention, not error.
- **`wave` fails *safe***: it rejects the `placeholder_8`/`zero` family and
  inflates on `placeholder_ff` / `0x80000000`.
- **`soxi` fails *loud***, in both directions on the same file family:
  - `soxi -s` / `soxi -D` → **0** on the `placeholder_8`+`zero` family: it
    calls a 479276-byte, 2.496 s capture **empty**. That is the most
    dangerous answer in the matrix — a false "no audio" verdict on real audio.
  - `soxi -s` → **536870912** and `soxi -D` → **12173.943583 s (3 h 22 m 54 s)**
    on the arecord `0x80000000` wound, for a **2.375 s** file. Identical at
    both sever wall times because it is derived from the declared field.

So the ordering for a future arm's reader choice is
`sndfile-info ≳ ffprobe > wave (fail-safe) > soxi (fail-loud)`.

### 4.3 Two sever shapes are functions of the sever wall time, not classes

- **`ffmpeg` KILL is time-parameterised, not a union.**
  `w=1.0 s` → **0-byte file**; `w=2.5 s` → **exactly 262144 B** with
  `placeholder_ff` on **both** the RIFF and the data field. r76 called this a
  union of {missing / 0-byte / `placeholder_ff`} and left the flush boundary
  unpinned; measured here it is deterministic at a fixed wall time. The
  `data_256k_aligned` field is a *real* discriminator for this consumer.
- **`parec`/`parecord --file-format=wav` granule count is wall-time
  dependent and 0 is legal at rc=0.**
  `w=1.0 s` → **44 bytes, 0 frames, rc=0**; `w=2.5 s` → **131116 bytes,
  32768 frames (exactly one 64 KiB granule), rc=0**. This is the r76 critic's
  D1 degenerate reproduced as the *systematic* outcome: `rc=0` +
  `data_finalized` + `data_64k_aligned` (`0 % 65536 == 0`) all hold on a
  **zero-audio** capture. The pinned r76 row "parecord TERM ⇒ 64-KiB-aligned
  granule shape" is true and simultaneously vacuous at w=1.0 s.

### 4.4 `arecord`'s TERM shape is DEVICE-dependent — a falsified r76 row

`probe-arecord-device-sever-r77.json`, clean serial run, re-confirmed with
`-d 2`:

| device | SIGTERM result | stderr | class |
| --- | --- | --- | --- |
| `hw:0,0` | **finalized** (242720 B) | `Aborted by signal Terminated...` | `aborted_by_signal` |
| `plughw:0,0` | **finalized** (242724 B) | `Aborted by signal Terminated...` | `aborted_by_signal` |
| `sysdefault` | **`riff=other`, `data=placeholder_80000000`** (255724 B) | `arecord: pcm_read:2285: read error: Interrupted system call` | **`alsa_read_eintr` (new)** |

So r76's row "arecord TERM ⇒ rc=1 `aborted_by_signal`, finalized, wave honest"
holds for `hw:`/`plughw:` and is **false for `sysdefault`**, which lands the
same `placeholder_80000000` unfinalized wound at TERM that it lands at KILL.
The r76 device axis (which found `{sysdefault, plughw:0,0, hw:0,0}` all viable
and byte-exact) is correct for the *bounded* leg and incomplete for the
*sever* leg. `sysdefault` routes through the plug layer, where the read
surfaces EINTR instead of completing arecord's own SIGTERM finalize.
`alsa_read_eintr` (`read error: Interrupted system call`) is **not** in r76's
`_CAPTURE_ERR_CLASSES` and should be added, most-specific-first, ahead of the
generic classes.

### 4.5 `placeholder_80000000` has a NAMED CAUSE — it is arecord's 2 GiB split sentinel

This is the reinterpretation the r76 critic's D9 was circling. Measured
(`probe-flood-boundary-r77.json`): a **bounded 0.35 s** run of
`arecord -D null -f cd` produced `r77rot.wav` at **1874763532 bytes** with
`data_declared = 2147483648 = 0x80000000` and
`data_declared_field = placeholder_80000000`.

So `0x80000000` is not an arbitrary "unknown length" placeholder — it is
arecord's literal **2 GiB wav split sentinel**, and the split limit is
`0x80000000 + 44 = 2147483692` bytes total. That is exactly the size the r76
critic observed on four of the eleven rotation files. And the split is
**silent**: after the first split, the requested filename
`<name>.wav` **does not exist** — arecord has renamed it to `<name>-01.wav`
and continues into `-02`, `-03`, … So an unbounded `arecord -D null` capture
**writes to filenames the caller never asked for**, and the caller's own path
check reports "no file" (`bytes = None`) for a capture that in fact wrote
tens of gigabytes.

Measured rotation siblings at w=1.2 s: `dev_null_TERM-01..-03.wav` for TERM
and `dev_null_KILL-01..-03.wav` for KILL, with the base name absent in both.

**Byte-discipline note (mine, and it fired).** My own probe C2 ran the
unbounded `-D null` legs and flooded **36 GB** into
`corpus/live/r77-scout/scratch/`, and a follow-up test filled the 16 GB
`/tmp` tmpfs to quota (`Disk quota exceeded`) — which *invalidated* one
arecord device comparison until I re-ran it on a non-full disk (§4.4 is the
clean re-run). Everything is deleted; the seat's footprint is now **36 MB**.
The r76 rule "never run `-D null` unbounded" is confirmed with a **named
mechanism** (silent 2 GiB split + rename) and a sharper operational form:
*an unbounded `-D null` leg is not merely fast, it is a filename-integrity
hazard, and its rotation is invisible to the requested path.*

---

## 5. FRONTIER 5 — raw streams carry no integrity witness

`probe-capture-sink-lattice-r77.json` §raw:

| leg | rc | signal | bytes | all-zero |
| --- | --- | --- | --- | --- |
| `parec --raw -d <LINE>` TERM @1.2 s | 0 | TERM | **65536** | true |
| `parec --raw -d <LINE>` KILL @1.2 s | **−9** | KILL | **65536** | true |

**Byte-identical.** The two artifacts differ only in `rc`, and for the shape
that matters — `parec --raw | <consumer>` — the downstream reader gets the
same 64 KiB and the same EOF in both cases and **never sees `rc` at all**.
With no header, no length field and (on this host) a digitally-silent source,
**byte count is the only verdict a raw capture carries**, and it is only
deterministic if the caller supplied its own bound:

- `pw-record --raw --target <LINE> -n 48000` → **192000 B exactly** (rc=1)
- `pw-record --target <LINE> -n 48000` (container) → **192044 B exactly** (rc=1)

`-n` is the only exact raw witness, and note the container form's rc is *also*
1 — so `rc` cannot be used to certify a raw capture even when it is visible.

`pw-cat -r -` (stdout) **has no default target**: `pw-cat -r -` and
`pw-cat -r --raw -` both fail rc=1 with the named
`no target node available` — and the container form leaves **24 bytes** of
partial header on stdout before failing, while `--raw` leaves **0**. That is
a new, small, sharp row: a *failed* `pw-cat` capture can still emit a
non-empty prefix.

---

## 6. FRONTIER 6 — concurrent playback + capture: no hazard

`probe-capture-sink-lattice-r77.json` §concurrent, serialized, tone-anchored,
with a clean silence baseline (`BASELINE no playback`: payload 384000,
**peak 0**):

| leg | cap rc | carries tone |
| --- | --- | --- |
| tone into default sink + one `pw-record` monitor capture | 1 | **yes** |
| tone + **TWO concurrent** `pw-record` monitor captures | 1 / 1 | **yes, both** |
| tone + `parec -d <mon> --raw` | 0 | **yes** |
| tone + `ffmpeg -f pulse -i <mon> -t 2` | 255 | **yes** (payload 499234) |
| tone + `paplay --device <sink>` + `pw-record` monitor (earlier run) | 1 | yes |

**PipeWire allows N concurrent attaches to the same monitor node with no
contention, no ordering hazard and no loss.** The r76 roundtrip idiom
(play into the sink while capturing its monitor) is sound, and the
"two captures of one monitor" case is not a hazard class.

---

## 7. Confounds and provenance

- **A concurrent seat was live on this host for most of my window.**
  `pgrep` at 16:20 showed `r76-verifier` running
  `corpus/fixtures/measure_audio.py --probe-capture-r76` (pid 2925184), and
  that seat's run was still in flight at 16:31.
- **`corpus/fixtures/measure_audio.py` is dirty at HEAD, and it is not mine.**
  `git status` shows ` M corpus/fixtures/measure_audio.py` (mtime
  **16:26:38**, `+60/−16`), and the diff is the r76 critic's fix set
  (`seq[:=]` normalization, a new `fmt_absent` wave class, the removal of
  `data_4k_aligned`). I did not touch it; my harness never imports
  `corpus/fixtures`. It is recorded here because a reader of my numbers will
  see a dirty tracked file and needs the attribution. My own write scope is
  exactly `corpus/live/r77-scout/` (untracked, new).
- **Concurrency confounded two probes, and I discarded their conclusions.**
  Probe A4 (`probe-override-content-r77.json`) and probe E
  (`probe-raw-concurrent-r77.json`) ran at the same time as each other, so
  A4's `tone->SPEAKER; cap parec SPDIF.monitor` row showed a tone on the
  wrong monitor and E's `BASELINE_no_playback` showed `nz=0.8777` with no
  playback. Both were re-run **serialized** (probes A5, H) and only the
  serialized numbers are used above. The stale files are kept on disk as
  evidence of the confound, clearly labelled here.
- **This host's default source is digital silence.** Line and Mic both
  measure `nonzero_frac = 0.0` and `peak = 0`. Any "did we capture signal"
  witness on the source path is **vacuous on this host** without an injected
  tone. This is also why the r76 roundtrip witness works on the *monitor*
  path (the played member provides the signal) and would fail on the *source*
  path.
- All numbers are this-host pins at these tool versions; nothing here is a
  portability claim.

---

## 8. Receipts

All under `corpus/live/r77-scout/` (untracked; operator to commit).

| artifact | sha256 (first 16) |
| --- | --- |
| `probe-capture-sink-lattice-r77.json` | `f6d1294748ae383a` |
| `probe-sever-readers2-r77.json` | `49ee33b28ed7a110` |
| `probe-format-axis-r77.json` | `6e5f49cf8c82340a` |
| `probe-source-lattice-r77.json` | `b01e2e64915273a2` |
| `probe-hotplug-r77.json` | `4e5ed0f16bf9db54` |
| `probe-arecord-device-sever-r77.json` | `f18c36ef4d2b2757` |
| `probe-flood-boundary-r77.json` | `d7f02123f5a66ceb` |
| `probe-override-content-serial-r77.json` | `5240c0fdab25421d` |
| `probe-override-extent2-r77.json` | `a6e6e48971445741` |
| `r77_probe.py` (harness) | `7fa77e1806f20b00` |
| `toolchain.txt` | `b5ba2bc171eba24b` |

Superseded / confounded, kept for the record:
`probe-target-override-r77.json`, `probe-override-extent-r77.json`,
`probe-override-content-r77.json`, `probe-raw-concurrent-r77.json`,
`probe-sever-readers-r77.json` (v1 — `ffprobe nb_frames` is a packet count,
superseded by v2).

---

## 9. Frontier claims for round 77, ranked by measured sharpness

1. **The `stream.capture.sink` fallback law** (§1.1) — a *source* name,
   `default`, `pulse`, or garbage under the prop silently yields the
   **default sink's monitor** at rc=1 with a full-length capture and no
   stderr, while `target.object` advertises the name you asked for. Falsifiable
   by the tone anchor and by `pw-link -l`.
2. **`sustained_after_target_loss`** (§2) — destroying the target mid-run is
   invisible in every artifact and every exit code; the capture runs on at
   100 % rate.
3. **The 5-witness reader matrix** (§4.1–4.2) — `sndfile-info` honest 11/11;
   `soxi` reports **0** on a 2.5 s capture and **3 h 22 m** on a 2.4 s one;
   `wave` fails safe by rejecting.
4. **`arecord`'s TERM shape is device-dependent** (§4.4) — `sysdefault`
   falsifies the r76 row; new class `alsa_read_eintr`.
5. **`placeholder_80000000` is the 2 GiB split sentinel and the split
   renames the file** (§4.5) — names the cause of the r76 critic's D9 flood
   and turns "don't run `-D null` unbounded" into a filename-integrity rule.
6. **`pw-record`'s format axis is total-convert-or-usage-refusal** (§3.1) —
   four refusal shapes land rc=1 with **no file at all** and a `--help` dump;
   `--channels 6` reaches `WAVE_FORMAT_EXTENSIBLE` (tag 65534) on the capture
   side.
7. **Raw has no witness** (§5) — TERM and KILL deliver byte-identical output;
   `-n` is the only exact raw witness and `rc` is 1 even on an exact capture.
8. **`parec/parecord --file-format=wav` granule count is wall-time
   dependent and 0 is legal at rc=0** (§4.3) — the r76 critic's D1 reproduced
   as the systematic outcome, with the wall-time threshold measured.
9. **No concurrency hazard** (§6) — N captures of one monitor all carry the
   tone.

## 10. Remaining unknowns (honest edges)

- **The fallback trigger is characterised but not explained.** I measured
  *which* names fall back; I did not read `pw-record`/libpipewire source to
  establish whether the fallback is a `node.target` miss that then hits
  auto-target, or an explicit `stream.capture.sink` policy. A `lsp`/source
  read of the capture-sink resolution path would close this.
- **`@DEFAULT_MONITOR@` is indistinguishable from the fallback here** because
  both name the same node; a leg that first moves the default sink and then
  asks for `@DEFAULT_MONITOR@` would separate them. Not measured.
- **The `parec` granule arithmetic is not derived.** I measured 0 granules at
  1.0 s and exactly 1 at 2.5 s but did not establish the flush cadence
  (connect latency vs 64 KiB accumulation). The threshold is therefore
  bracketed, not pinned.
- **`sysdefault`'s EINTR path is characterised at one wall time.** I did not
  test whether `sysdefault` TERM can ever finalize (e.g. under a different
  `-d`), nor whether the `dmix`/plug route is the cause.
- **The `stream.capture.sink` lattice was measured against one default sink.**
  With the default sink moved to Speaker or HDMI, the fallback target should
  move with it; not measured.
- **`ffprobe nb_frames` is unusable as a frame witness** (it is a packet
  count). My v1 receipt used it and is superseded; a future arm should use
  `format.duration` or `-count_frames`' `nb_read_frames` and then *say* it is
  a packet count.
- **`ffmpeg`'s monitor capture measured `peak = 26230` against a member tone
  of amplitude 16384** in the concurrent leg. I did not chase the 4.1 dB
  discrepancy; it may be a mix/gain artifact of concurrent legs.
