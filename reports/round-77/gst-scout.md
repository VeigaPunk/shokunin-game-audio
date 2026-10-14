# R77 GST-SCOUT — the GStreamer capture/playback surface, measured

Round 77 (pre-measurement for the capture frontier). Host `plazir27`, measured
2026-10-14 ~19:44–19:56Z (host local UTC−3, ~16:44–16:56). Repo
`~/Projects/shokunin/audio-shokunin` @ HEAD `503689c`.

**Seat: GST-SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/gst-scout/` (untracked) plus this report.** Own harness
(`gst_probe.py`, six stages, one JSON receipt each). `corpus/fixtures` was
never imported and never executed — the concurrent author edit to
`corpus/fixtures/measure_audio.py` (still ` M` at HEAD, not mine) cannot have
shaped any number here.

Toolchain (this host, this session): **GStreamer 1.28.6** (`gst-launch-1.0`,
`gst-inspect-1.0`; plugins-base/good 1.28.6-3, `gst-plugin-pipewire` 1:1.6.8-1;
**no `-bad`, no `-ugly`**), PipeWire **1.6.8**, pacat/pactl
**17.0-98-gb096**, ffmpeg **n9.0.1**, SoX_ng **14.8.0.1**, Python **3.14.7**,
numpy 2.5.3, Linux 7.2.3-arch1-3.

---

## 0. Headline: eight frontier claims, three of them new laws

| # | frontier | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | `pipewiresrc` target lattice | **r77 law CONFIRMED in a 2nd client** | with `stream-properties=props,stream.capture.sink=true`, **all 10** targets (incl. `no_such_node_xyz`, `default`, `pulse`, `@DEFAULT_SOURCE@`, and a real *source* name) give **rc=0, 204844 B, byte-identical sha `51a1a59651704520`** — and `pw-link -l` proves they consume the **default sink's monitor** |
| 2 | refusal shape, no prop | **NEW CLASS** | without the prop, `pipewiresrc` refuses **loudly**: rc=**255**, **0-byte file**, `stream error: target not found` — where `pw-record` lands rc=1 with a **44-byte empty wav** |
| 3 | caps dependence of the fallback | **NEW LAW** | the fallback is **audio-path only**: same prop+target with `video/x-raw` (or a bare `fakesink`) → rc=255 `target not found`; with audio caps → rc=0 |
| 4 | sever taxonomy | **NEW LAW, pinned** | **SIGINT exits rc=0 and does NOT finalize** (data field `0x7FFFF000`, 2 GiB declared); `-e` makes INT finalize; **SIGTERM ignores `-e`**, and TERM/KILL are **byte-identical** (274476 B, same header) differing only in rc (−15 vs −9) |
| 5 | reader disagreement port | **MATRIX REPRODUCED** | on the gst wound: `soxi -s` → **536854528** frames and `soxi -D` → **11184.469 s** for a 1.43 s file; `wave` accepts-and-inflates; `sndfile-info` (68608) and `ffprobe` (1.429333) honest |
| 6 | bound honesty | **NEW CLASS** | `num-buffers` is **not** a byte-exact bound for `pipewiresrc`/`pulsesrc` (1024 vs 2048 frames/buffer on two runs of the *same* leg; `buffer-time=2000000` grows a fixed-50-buffer leg 10×); a free-running `audiotestsrc` writes **~145 MB/s** and only the byte watchdog bounds it |
| 7 | refusal taxonomy (prior-art axis) | **NEW, rc-split** | **parse-time refusals rc=1 with no file**, **state-change failures rc=255 with a 0-byte file**, except `pulsesrc` → **rc=1** `No such entity` (client-dependent rc) |
| 8 | wavenc writer defect | **NEW** | `wavenc` writes **fmt tag 3 (IEEE float) with 64-bit samples and no extended part** → `soxi` warns and reports **Precision: 54-bit**; tag 65534 (extensible) appears at **channels > 2** only (not rate>48k, not bits>16) |

---

## 1. FRONTIER 1 — inventory (`probe-inventory-r77.json`)

`gst-inspect-1.0` (no args) prints `plugin:  factory: description`; parsed:
**1295 features across 196 plugins**, `-b` reports **0 blacklisted**. 226
features carry an audio-ish description. Per-element `Klass`/pad census over 120
candidates:

| element | klass | src/sink pads | props |
| --- | --- | --- | --- |
| `pulsesrc` / `pulsesink` | `Source/Audio` / `Sink/Audio` | 1/0, 0/1 | 22 / 31 |
| `pipewiresrc` / `pipewiresink` | **`Source/Audio/Video`** / `Sink/Audio/Video` | 1/0, 0/1 | 22 / 24 |
| `alsasrc` / `alsasink` | `Source/Audio` / `Sink/Audio` | 1/0, 0/1 | 16 / 26 |
| `autoaudiosrc` / `autoaudiosink` | `Source/Audio` / `Sink/Audio` | 1/0, 0/1 | 6 / 7 |
| `wavparse` / `wavenc` | `Codec/Demuxer/Audio` / `Codec/Muxer/Audio` | 1/1 | 3 / 2 |
| `flacenc` / `flacdec` | `Codec/Encoder/Audio` / `Codec/Decoder/Audio` | 1/1 | 15 / 6 |

The **`Source/Audio/Video` klass of `pipewiresrc` is not cosmetic** — it is the
mechanism behind claim 3 (the target lookup is per-media-type).

Present, beyond the brief's named families: `auparse`, `wavpackparse/dec/enc`,
`mpg123audiodec`, `lamemp3enc`, `twolamemp2enc`, `opusdec/opusenc`,
`vorbisdec/vorbisenc`, `speexdec/speexenc`, `avdec_{aac,flac,mp3}`,
`avenc_{aac,ac3}`, `adpcm`, `mulaw`, `alaw`, `audioconvert/audioresample/
audiorate/audiomixer/audiobuffersplit`, `adder`, `volume`, `level`, `spectrum`,
`removesilence`, `capsfilter`, `queue`, `fakesrc/fakesink`, `appsrc/appsink`,
`identity`, `tee`, `jackaudiosrc/sink`, `oss4src/sink`, `osssrc/sink`,
`shmsrc/sink`, `unixfdsrc/sink`, `souphttpsrc`, `udpsrc`,
`playbin/decodebin/uridecodebin`, `giostreamsrc`.
Absent on this host: `mad`, `lame`, `sbcdec/sbcenc`, `dsddec`, `openalsrc`,
`directsoundsrc`, `osxaudiosrc`, `sfsrc`, `rfsrc`, `avenc_mp3`, `avdec_vorbis`.

---

## 2. FRONTIER 6 — the known-good loop and which bound is honest
(`probe-control-r77.json`)

`audiotestsrc wave=sine freq=1000 num-buffers=N ! audio/x-raw,format=S16LE,
rate=48000,channels=2 ! wavenc ! filesink`:

| leg | rc | bytes | header | frames | peak |
| --- | --- | --- | --- | --- | --- |
| `num-buffers=1` | 0 | **4140** = 44 + 1024·4 | finalized | 1024 | 26213 |
| `num-buffers=100` | 0 | **409644** = 44 + 100·1024·4 | finalized | 102400 | 26213 |

`num-buffers × 1024 frames × 4 B + 44` is **exact** for `audiotestsrc` — the
loop control is byte-deterministic and `rc=0`.

**The three bounds, measured:**

| bound | leg | what happened |
| --- | --- | --- |
| `num-buffers` | `nb100` | rc=0, exact bytes, finalized — the only *clean* bound |
| wall clock | unbounded + `sync=true`, SIGTERM @1.5 s | rc=−15, 133164 B = 66560 frames = **1.509 s of real-time audio**, header **unfinalized** |
| byte cap | unbounded free-run, 8 MiB watchdog | killed at **8783916 B** after **0.061 s (144.0 MB/s)**; the second free-run leg killed at 8851500 B (0.061 s, 145.1 MB/s) — **overshoot over the 8 MiB cap ≈ 0.4–0.46 MB** |
| wall clock vs free-run | unbounded free-run, wall cap 2.0 s | the **byte** cap fired at 0.061 s — a 2 s wall bound is ~145 MB/s × 2 s ≈ 290 MB of artifact if the byte cap is not armed |

**An unbounded free-running gst source writes ~145 MB/s into `filesink`.** A
wall-clock bound is *not* a byte bound: with `sync=false` (filesink's default)
the wall leg reaches its cap in ~60 ms. `sync=true` is what turns a wall bound
into an honest byte bound.

`pulsesrc` bound honesty (`probe-formats-r77.json`), `num-buffers=50` fixed:

| knob | rc | bytes | frames | frames/buffer |
| --- | --- | --- | --- | --- |
| baseline | 0 | 96044 | 24000 | 480 |
| `blocksize=4096` | 0 | 204844 | 51200 | **1024 = 4096 B / 4** |
| `buffer-time=2000000 latency-time=100000` | 0 | **960044** | **240000** | 4800 |
| `buffer-time=50000 latency-time=10000` | 0 | 96044 | 24000 | 480 |
| `blocksize=65536` | **−9** | 2818092 | (declared 536854528) | **wall cap fired at 15.009 s** |

So `num-buffers` is a *buffer* count, never a frame count: `blocksize`/`buffer-time`
move the byte total, and one 50-buffer leg can outrun a 15 s wall cap. A gst
fixture probe must bound with **wall + byte watchdog**, and use `num-buffers`
only where the buffer size is pinned by an explicit `blocksize`/`audiotestsrc`.

*Provenance note for the 1024-vs-2048 claim:* the receipted lattice legs
(`pipewiresrc target-object=no_such_node_xyz stream-properties=props,
stream.capture.sink=true num-buffers=50 ! wavenc ! filesink`) delivered
**204844 B / 51200 frames** (1024 frames per buffer); an **ad-hoc re-run of the
identical command outside the harness** (same session, `t1.wav`) delivered
**409644 B / 102400 frames** (2048 per buffer). The variance is the claim; only
the first number is in `probe-lattice-r77.json`.

---

## 3. FRONTIER 2 — the `pipewiresrc` target lattice, and the cross-client law
(`probe-lattice-r77.json`)

`pipewiresrc target-object=T [stream-properties=props,stream.capture.sink=true]
num-buffers=50 ! wavenc ! filesink`, default sink = `…HiFi__SPDIF__sink`.

### 3.1 Without the prop — loud refusal, no fallback

| target | rc | bytes | class |
| --- | --- | --- | --- |
| `…SPDIF__sink` (a sink) | 255 | **0** | `state_change_failed` / `target not found` |
| `…SPDIF__sink.monitor` | 255 | 0 | same |
| `…Line__source` (**the real source**) | **0** | 225324 | **resolves** (float32, peak 0.0) |
| `…Line__source.monitor` | 255 | 0 | same |
| `no_such_node_xyz` / `default` / `pulse` / `@DEFAULT_SOURCE@` / `@DEFAULT_MONITOR@` / `0` | 255 | 0 | same (8/8) |

### 3.2 With the prop — universal acceptance, silent fallback

**All ten targets** (the eight above plus `…SPDIF__sink` and `.monitor`) land
**rc=0, 204844 B, finalized, 51200 frames, float32, peak 0.0, sha
`51a1a59651704520`** — *byte-identical*. That identity is **silence**, not
proof (the r77 §1.3 trap); the honest witnesses are topology and a tone anchor.

### 3.3 Topology — which node is actually consumed (`pw-link -l` while running)

| capture | `gst-launch-1.0:input_FL/FR` is fed by | verdict |
| --- | --- | --- |
| prop + `no_such_node_xyz` | **`…SPDIF__sink:monitor_FL/FR`** | **silent fallback to the default sink's monitor** |
| prop + `…Line__source` | **`…SPDIF__sink:monitor_FL/FR`** | **fallback even for a real source name** (strong form) |
| prop + `…SPDIF__sink` | `…SPDIF__sink:monitor_FL/FR` | honored (indistinguishable here: the default *is* SPDIF) |
| **no prop** + `…Line__source` | `…Line__source:capture_FL/FR` | honored honestly |

`target.object` is not the witness; the producer list is — the r77 §1.2
provenance trap reproduces verbatim in a second client.

### 3.4 The fallback is caps-dependent — a NEW law

Same prop + `no_such_node_xyz`, only the downstream varies:

| downstream | rc | bytes |
| --- | --- | --- |
| `audio/x-raw,… ! wavenc ! filesink` | **0** | 41004 |
| `audio/x-raw,… ! fakesink` | **0** | (no file) |
| `audioconvert ! fakesink` | **0** | (no file) |
| `fakesink` (bare) | **255** | `target not found` |
| `video/x-raw ! fakesink` | **255** | `target not found` |

The prop's sink→monitor resolution exists **only on the audio path**
(`pipewiresrc` is `Source/Audio/Video`, §1). A probe that omits audio caps sees
a *different* law — a confound worth pinning before anyone reads a
`target not found` as "the name was wrong".

### 3.5 Tone-anchored roundtrip, zero physical-device writes
(`probe-formats-r77.json` §roundtrip)

A seat-owned `module-null-sink` (`gstscout_null`, loaded and unloaded, id
536870917) plus `audiotestsrc ! pipewiresink target-object=gstscout_null` as the
tone source — **no audio is written to any physical sink**:

| capture | cap rc | bytes | frames | peak | carries tone |
| --- | --- | --- | --- | --- | --- |
| `pipewiresrc` prop + `target=gstscout_null` | **0** | 393260 | 98304 | **16383** | **yes** |
| `pw-record -P stream.capture.sink=true --target gstscout_null` | 1 | 384044 | 96000 | **16383** | **yes** |
| `pipewiresrc` no prop, `target=gstscout_null` | 255 | 0 | — | — | no |
| `pipewiresrc` no prop, `target=gstscout_null.monitor` | 255 | 0 | — | — | no |

**`pipewiresrc ! wavenc ! filesink` does capture a real monitor**, tone-anchored,
with the same prop `pw-record` needs; a resolvable sink name is *honored* (tone
present), an unresolvable one falls back to the **default** sink (topology,
§3.3). The `.monitor` suffix does **not** resolve for `pipewiresrc` without the
prop (it does for `pw-record`).

### 3.6 Cross-client refusal/fallback matrix (same session, same host state)

| client | target | prop | rc | artifact | class |
| --- | --- | --- | --- | --- | --- |
| `pw-record` | sink | yes | 1 | 96044 B finalized | honored (r77 row) |
| `pw-record` | **garbage** | yes | 1 | 96044 B finalized, peak 0 | **silent fallback** |
| `pw-record` | source | yes | 1 | 96044 B finalized | **silent fallback** |
| `pw-record` | sink | no | 1 | **44 B empty wav** | quiet degenerate (r77 row) |
| `pipewiresrc` | garbage/any | yes | **0** | 204844 B finalized | **silent fallback** |
| `pipewiresrc` | sink/any-non-source | no | **255** | **0 B** | loud `target not found` |
| `pulsesrc` | `no_such_node_xyz` | — | **1** | **0 B** | `Failed to connect stream: No such entity` |
| `alsasrc` | `hw:99` / bad pcm | — | **255** | **0 B** | `Could not open audio device` |

**Same substrate, four different shapes.** The r77 fallback law is a PipeWire
*client-property* behaviour (shared by `pw-record` and `pipewiresrc`); the
refusal *rc and file shape* are client-specific.

---

## 4. FRONTIER 3 — sever classes: INT vs TERM vs KILL, and `-e`
(`probe-sever-r77.json`)

`audiotestsrc ! audio/x-raw,48k,2ch,s16 ! wavenc ! filesink sync=true` (and the
same shape from `pipewiresrc` prop + SPDIF), severed at **1.5 s**:

| signal | `-e` | rc | signal | bytes | header | RIFF field | data field |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SIGINT | no | **0** | — | 290860 | **unfinalized** | `0x7FFF0024` | **`0x7FFFF000`** |
| SIGINT | **yes** | 0 | — | 294956 | **finalized** | 294948 | 294912 |
| SIGTERM | no | −15 | TERM | 274476 | unfinalized | `0x7FFF0024` | `0x7FFFF000` |
| SIGTERM | **yes** | −15 | TERM | **274476** | unfinalized | `0x7FFF0024` | `0x7FFFF000` |
| SIGKILL | no | −9 | KILL | **274476** | unfinalized | `0x7FFF0024` | `0x7FFFF000` |
| SIGKILL | yes | −9 | KILL | **274476** | unfinalized | `0x7FFF0024` | `0x7FFFF000` |

`pipewiresrc` reproduces every cell (286764 / 274476 / 274476, same fields).

**Four pinned rows:**
1. **`gst-launch` installs a SIGINT handler only.** INT is a *clean shutdown*
   (rc=0) that still leaves an **unfinalized** artifact; `-e` (EOS-on-shutdown)
   is what turns it into a finalized file. **rc=0 is not the verdict** — for
   the first time measured on an artifact that is *truncated* with a success
   exit code.
2. **SIGTERM ignores `-e`** (byte-identical with and without it) and is **not
   finalized**.
3. **TERM and KILL are byte-identical** (274476 B, identical 44-byte header,
   sha-equal), separated only by rc −15 vs −9 — the container analogue of r77
   §5's raw-stream row.
4. **The placeholder is a coherent 2 GiB header, not a marker**: RIFF field =
   data field + 36, data field `0x7FFFF000` = 2147418112, i.e. *a header that
   lies about having 2 GiB of payload*. It is format-independent (same field on
   mono/44.1 k and stereo/48 k legs).

Cross-consumer controls, same session, w=1.5 s:

| consumer | signal | rc | bytes | header | soxi −s | sndfile | ffprobe |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `pw-record -P … --target <SPDIF> -n 96000` | TERM | 1 | 286764 | **finalized** | 71680 | 71680 | 1.493333 |
| `pw-record …` | KILL | −9 | **286764** | `placeholder_8` | 0 | 71680 | 1.493333 |
| `parecord --file-format=wav` | KILL | −9 | **44** | `placeholder_8` | 0 | 0 | — |
| `gst-launch` (testsrc) | TERM | −15 | 274476 | `wavenc_streaming` | **536854528** | 68608 | 1.429333 |

`pw-record` **finalizes on TERM** (r77 row holds); gst **never finalizes on
TERM**; `parecord`'s 44-byte granule at w=1.5 s confirms r77 §4.3's wall-time
dependence (0 granules at 1.5 s, 1 at 2.5 s).

---

## 5. FRONTIER 4 — the reader-disagreement port, five witnesses

On the gst wound (274476 B, 1.429 s of audio, data field `0x7FFFF000`):

| witness | answer | honest? |
| --- | --- | --- |
| `sndfile-info` `Frames` | **68608** | **honest** (== (274476−44)/4) |
| `ffprobe` `format.duration` | **1.429333** | **honest** |
| stdlib `wave` `getnframes()` | **536854528** | accepts and **inflates** to the declared field |
| `soxi -s` | **536854528** | **declared echo** |
| `soxi -D` | **11184.469333 s (3 h 06 m)** | **declared echo** |

Scale check across formats: the *same* `0x7FFFF000` field on the mono/44.1 k
leg makes `soxi -s` report **1073709056** frames and `soxi -D` **24347.144127 s
(6 h 46 m)** for an **8.85 MB** file (sndfile 4425728 frames and ffprobe
100.356644 s, both honest) — the echo is `declared_bytes / block_align`, so
it moves with the format while the header field does not. This is r77's
`declared_echo` class reproduced on a **container** (not raw) wound, with
`wave` on the same side as `soxi` this time (it *accepts* the over-declared
family, exactly as r77 §4.2 pinned).

Reader ordering unchanged: **`sndfile-info ≳ ffprobe > wave > soxi`**.

A second, *non-wound* reader row (`probe-control-r77.json` §caps):
`wavenc` accepts `F64LE` and writes **fmt tag 3 with 64-bit samples and a
16-byte `fmt` chunk** — a non-extensible 64-bit float WAV, which the format
does not allow. `soxi` warns `wave header missing extended part of fmt chunk`
and reports **`Precision: 54-bit`**; `sndfile-info` and `ffprobe`
(`pcm_f64le`) stay honest. A writer-side defect that only one reader
misreports is a *new* matrix cell class (not a sever wound).

---

## 6. FRONTIER 5 — format/property axis (`probe-control-r77.json`,
`probe-formats-r77.json`)

### 6.1 `audiotestsrc` wave axis (25 buffers, 48 k mono s16, volume 0.5)

| wave | bytes | peak | rms | nonzero_frac | sha16 |
| --- | --- | --- | --- | --- | --- |
| sine | 51244 | 16383 | 11585.31 | 0.958 | e9dd6510287a5b53 |
| square | 51244 | 16383 | 16383.00 | 1.000 | 0a228a3d0313e604 |
| saw | 51244 | 16383 | 9461.14 | 0.979 | 74819f1fb6f99e27 |
| triangle | 51244 | 16383 | 9475.95 | 0.958 | 6f6fc353c0271be4 |
| **silence** | 51244 | 0 | — | — | **3dcb6a341da6cbb5** |
| **ticks** | 51244 | **0** | — | — | **3dcb6a341da6cbb5** |
| white-noise | 51244 | 16382 | 9456.24 | 1.000 | caa2d0f33ae7c0c3 |
| pink-noise | 51244 | 9896 | 2704.35 | 1.000 | 211fef947469e524 |
| sine-table | 51244 | 16383 | 11585.30 | 1.000 | 756d14bd9983e550 |
| gaussian-noise | 51244 | **32767** | 15414.34 | 1.000 | 7071f4c0e132d9ed |
| red-noise | 51244 | 8191 | 4616.57 | 1.000 | 09a66f0ec6224e02 |
| blue-noise | 51244 | 10279 | 2641.84 | 1.000 | 1df089affa23dc37 |
| violet-noise | 51244 | 8191 | 4442.33 | 1.000 | e27b4d7e9308376b |

**`ticks` is byte-identical to `silence`** at the default `tick-interval`
(1 s) over 25 buffers — a zero-data vacuity: a probe that "verifies the ticks
waveform" is testing silence unless it also sets `tick-interval` /
`marker-tick-period`. `gaussian-noise` is the only waveform that reaches full
scale (32767 vs 16382 for white-noise).

`freq` axis: 100 / 20000 / **30000 (above the 48 k Nyquist)** all rc=0 with
peak 26213 and identical byte counts — **an out-of-band `freq` is silently
accepted**; `freq=0` is digital silence (peak 0, rc=0).
`volume` axis: `volume=0` → silence; **`volume=2` and `volume=4` are rejected
by GObject with a `GLib-GObject-CRITICAL` on stderr, silently clamped, and
rc=0 with bytes identical to `volume=1`** — the property-axis analogue of "rc
is never the verdict", with the witness on *stderr only*.

### 6.2 Caps → `wavenc` (`probe-control-r77.json` §caps)

| request | bytes | fmt tag | bits | ch | extended part? |
| --- | --- | --- | --- | --- | --- |
| S16LE 48 k 2ch | 102444 | 1 | 16 | 2 | no |
| U8 / S24LE / S32LE | 51244 / 153644 / 204844 | **1** | 8/24/32 | 2 | no |
| F32LE | 204844 | **3** | 32 | 2 | no |
| **F64LE** | 409644 | **3** | **64** | 2 | **no (illegal)** |
| S16LE **96 k** 2ch | 102444 | **1** | 16 | 2 | no |
| S16LE **44.1 k** 2ch | 102444 | **1** | 16 | 2 | no |
| S16LE 48 k **3ch** | 153680 | **65534** | 16 | 3 | **yes, fmt=40 + `fact`** |
| S16LE 48 k **6ch** | 307280 | **65534** | 16 | 6 | yes, fmt=40 + `fact` |

`wavenc`'s extensible boundary is **channels > 2 only** — it does *not* fire on
rate > 48 k or bits > 16, which is a **different rule** from the ffmpeg muxer
rule the r77 capture-side arm measured (§3.3 there). Containers:
`wavenc` 102444 B (`pcm_s16le`), `flacenc` **15533 B** (`flac`, same duration),
raw `filesink` 102400 B (`bintext`).

### 6.3 Source-element property axis

| leg | rc | bytes | class |
| --- | --- | --- | --- |
| `pulsesrc device=<Line source>` | 0 | 96044 finalized | honored |
| `pulsesrc device=<SPDIF monitor>` | 0 | 96044 finalized | honored |
| `pulsesrc device=no_such_node_xyz` | **1** | **0** | `Failed to connect stream: No such entity` |
| **`pulsesrc` (no `device=`)** | **1** | **0** | same — **`pulsesrc` has no working default on this host** |
| `alsasrc device=null` | 0 | 96044 | the format oracle works under gst |
| `alsasrc device=no_such_pcm` / `hw:99` | 255 | 0 | `Could not open audio device` |

No ALSA `hw:` device was opened by this seat (a concurrent seat holds them);
`null` is the only alsa device exercised, and `device=hw:99` fails before open.

---

## 7. FRONTIER 7 — prior-art axis: the gst-launch refusal taxonomy
(`probe-errors-r77.json`)

| leg | rc | file | named class / stderr |
| --- | --- | --- | --- |
| `nosuchelementsrc ! …` | **1** | none | `no element "nosuchelementsrc"` (parse) |
| `nosuchelementsink` | **1** | none | same (parse) |
| `audiotestsrc ! wavparse` | **1** | none | `could not link audiotestsrc0 to wavparse0` (parse) |
| `capsfilter caps=bogus` / unsatisfiable | **1** | none | `could not link … to capsfilter0` (parse) |
| `audiotestsrc ! wavenc` (no sink) | **1** | none | `Internal data stream error` (runtime, no file) |
| empty pipeline | **1** | none | `pipeline could not be constructed` |
| `filesrc location=/nonexistent` | **255** | **0 B** | `Resource not found` |
| `filesink location=/nonexistent-dir/x.wav` | **255** | none | `Could not open file … for writing` |
| `alsasrc device=hw:99` / bad pcm | **255** | **0 B** | `Could not open audio device for recording` |
| `pipewiresrc target-object=no_such_node_xyz` (noprop) | **255** | **0 B** | `stream error: target not found` + `Failed to set pipeline to PAUSED` |
| `pipewiresrc` (no target at all, noprop) | **255** | **0 B** | same |
| `pulsesrc device=no_such_node_xyz` | **1** | **0 B** | `Failed to connect stream: No such entity` |
| `filesink location=/dev/full` | **1** | — | `No space left on the resource` |
| `wavenc` from F64LE caps | **0** | 81964 | *no error* — the §5 writer defect |

**Two rc conventions coexist**: parse-time refusals are **rc=1 with no file**;
runtime state-change failures are **rc=255 with a 0-byte file already created**
(except `filesink`, which cannot open). `pulsesrc` is the outlier: a *runtime*
failure at **rc=1**. Any gst arm that reads `rc == 1` as "gst missing/bad
arguments" will misclassify every alsa/pipewire state-change failure.

---

## 8. Coverage proposal — the smallest gst fixture probe (`--probe-gst-r78`)

A new parallel ledger family `--probe-gst-r78` (prior rows untouched), **six
legs, ≈10 s wall, ≤1 MB of artifacts**, every leg byte-capped and wall-capped:

1. **`gst_present` gate.** `gst-launch-1.0 --version` + `gst-inspect-1.0
   pipewiresrc`. Absent toolchain ⇒ one row `{class: "gst_absent"}` and **no
   further legs** (a host without GStreamer must not look like a gst failure).
2. **Control (`gst_control`).** `audiotestsrc num-buffers=100 ! audio/x-raw,
   S16LE,48k,2ch ! wavenc ! filesink` ⇒ assert **rc=0, 409644 B, finalized,
   102400 frames** — the byte-exact bound and the known-good loop.
3. **Fallback law (`gst_fallback`)** — the round's main row. Two legs against
   the *default sink's* name, audio caps forced (`! audio/x-raw,format=S16LE,
   rate=48000,channels=2 ! wavenc ! filesink`), unbounded capture, **wall 2.0 s
   then SIGTERM**, **byte cap 4 MiB**:
   - `target-object=no_such_node_xyz` **with** `stream-properties=props,
     stream.capture.sink=true` ⇒ rc=0, full-length finalized;
   - the **same target without the prop** ⇒ rc=255, **0-byte file**.
   Record the contrast pair (rc 0/255, bytes full/0) *and*, while the prop leg
   runs, one `pw-link -l` sample: the `gst-launch-1.0:input_*` producers must
   be `<default sink>:monitor_*`. **Do not add a tone**: the topology is the
   witness, and a tone into the default sink contaminates concurrent seats.
4. **Sever row (`gst_sever`).** `… ! wavenc ! filesink sync=true` (real-time
   rate is load-bearing), three legs at w=1.5 s: **INT**, **INT + `-e`**,
   **TERM**. Assert (a) INT ⇒ rc=0 **and** `data_field == 0x7FFFF000` and
   `riff_class == unfinalized`; (b) INT+`-e` ⇒ finalized (RIFF == size−8);
   (c) TERM ⇒ rc=−15, unfinalized, **bytes identical to a KILL leg**. Byte cap
   2 MiB, wall cap 6 s.
5. **Reader port (`gst_readers`).** Five witnesses on the INT-unfinalized file
   from leg 4: assert `sndfile-info`/`ffprobe` honest (±2 %) **and**
   `soxi -s`/`soxi -D` equal to the declared echo (536854528 / 11184.47 s on
   this host's 48 k/2ch wound), i.e. the r77 `declared_echo` class carried onto
   a container wound.
6. **Refusal trio (`gst_refusal`).** `alsasrc device=hw:99`,
   `pipewiresrc target-object=no_such_node_xyz` (no prop), `pulsesrc device=
   no_such_node_xyz` ⇒ assert the **rc split 255 / 255 / 1**, each with a
   0-byte artifact and its named stderr class.

**Named contention / host-state caveats baked into the proposal**

- **Caps are load-bearing.** Leg 3 must force `audio/x-raw` downstream;
  with a bare `fakesink` or `video/x-raw` the *same* prop+target fails
  `target not found` (§3.4). A probe without audio caps measures a different law.
- **The fallback and the explicit default-sink target are indistinguishable on
  this host** (the default sink *is* the sink the fallback resolves). A leg that
  first moves the default sink would separate them — deliberately out of scope
  here (it perturbs every concurrent seat).
- **`num-buffers` is not a byte bound** for `pipewiresrc`/`pulsesrc` (§2);
  never let a leg run without the wall+byte watchdog, and never run a
  free-running `audiotestsrc` unbounded (**~145 MB/s**, §2).
- **`fakesink` is not a neutral downstream** for `pipewiresrc` (§3.4).
- **Host state**: the SPDIF monitor is the default sink today; if the default
  moves, leg 3's expected producer changes with it (assert *"the default sink's
  monitor"*, not a hard-coded node name).
- **Concurrency**: leg 3 and 4 read the live graph; a concurrent capture is
  harmless (r77 §6), but a concurrent *default-sink change* is not. Record the
  `pactl list short sinks` snapshot in the receipt.

---

## 9. Confounds, provenance, and two incidents of my own

- **A concurrent seat was live for the whole window.** `r77-boundary` was
  running `p1b_moved.py` → `p4_format.py` … (pids 427061/427066, `pw-record`
  and `parec` legs on the LINE source), and `r77-author` held a `pw-record`
  capture of the SPDIF monitor. All my stages are internally serialized, but
  cross-seat contention is **not** excluded; every leg's receipt carries its
  own timestamps, and §3.6/§4's cross-client controls were re-measured in this
  session so the comparison is contention-matched.
- **I contaminated a concurrent capture once, and it is mine.** An early smoke
  test (`audiotestsrc wave=sine freq=440 ! pipewiresink`, ~16:47 local) did not
  know that `pipewiresink` **auto-links to the default sink**; it played a
  ~0.4 s tone into `…SPDIF__sink` while `r77-author` was capturing that
  monitor. From that point on every tone this seat produced went into a
  seat-owned `module-null-sink` (§3.5) and no physical device was written.
  Flagging it so the author can discount any 440 Hz burst in that window.
- **I flooded the disk once, and the mechanism is worth pinning.** My first
  harness pass wrote **3.7 GB** (`ctl_unbounded_bytecap.wav`) because the byte
  watchdog thread received a `str` path, raised `AttributeError`, and the cap
  **never armed** — while the main loop's kill could not fire because it waits
  on the same thread's flag. The fix (Path coercion + the cap passed in + the
  watcher killing the process group itself) is load-bearing and commented in
  `gst_probe.py`; artifacts were deleted immediately (scratch now **34 MB**,
  cap 16 MiB/artifact). This is the r77 scout's §4.5 flood hazard reproduced
  with a *named cause* on the gst side: **a watchdog that is not itself
  verified is not a cap.**
- **No tracked file was touched.** `corpus/fixtures/measure_audio.py` remains
  dirty at HEAD from the author's concurrent edit (mtime 16:26 local, before my
  window); my harness never imported it.
- All numbers are this-host pins at these tool versions; nothing here is a
  portability claim.

---

## 10. Receipts

All under `corpus/live/gst-scout/` (untracked; operator to commit).

| artifact | sha256 |
| --- | --- |
| `probe-inventory-r77.json` | `6cc3a69b7e198e7214db9667df0b64b4de3357fef54d486846acf325b86566ae` |
| `probe-control-r77.json` | `eed407b77950de3d780272c0082a32ea8efdc889f04aa8b966542afd2e27e86f` |
| `probe-lattice-r77.json` | `18591c731d0394f70076132ce10a3c981e168daef84b90955236e0bcf732f18c` |
| `probe-sever-r77.json` | `8d002a22faae14ad9e3634986d41ec775ae6cdfbf9b99ea11f8f900f14235e53` |
| `probe-formats-r77.json` | `8710250c044cb969f556dedd0dd1b0c78840142b459f6c28f93f3d97a5664c3e` |
| `probe-errors-r77.json` | `1dccaaeff6dfdb0e5bd783e5ee8fe44f2da83d8a0c76c9c97e257a23a67fc795` |
| `gst_probe.py` (harness) | `f3c08ad1835811f98f3d03c6da9ad2c1d81ea2c736dd8934ca729ae12f2e6dbc` |
| `toolchain.txt` | `1e8500a6e517b9c17e82ae3b92ae2594e337ab18735ca0c09033d2d46ad83b23` |

Scratch artifacts under `corpus/live/gst-scout/scratch/` (34 MB) are the
measured wounds; the operator may prune them — every number above is in the
receipts.

---

## 11. Frontier claims, ranked by measured sharpness

1. **The prop's fallback is a cross-client law** — `stream.capture.sink=true`
   makes *any* target (garbage, `default`, `pulse`, `@DEFAULT_*`, a real source
   name) resolve to the **default sink's monitor**, proven by `pw-link -l` in
   `pipewiresrc` and reproduced by `pw-record` in the same session (§3.2–3.3,
   §3.6). New: **the fallback exists only on the audio path** (§3.4).
2. **`gst-launch` SIGINT ⇒ rc=0 + unfinalized 2 GiB-declaring header; `-e` is
   the finalizer; TERM ignores `-e` and equals KILL byte-for-byte** (§4).
3. **The reader port on a container wound**: `soxi` echoes the declared 2 GiB
   (536854528 frames / 11184 s on a 1.43 s file), `wave` inflates, `sndfile`
   and `ffprobe` are honest (§5).
4. **Refusal shapes are client-specific**: pipewiresrc 255 + 0 B, pulsesrc 1 +
   0 B, pw-record 1 + 44 B, alsasrc 255 + 0 B (§3.6, §7).
5. **`num-buffers` is not a byte bound** on pipe/pulse sources; a free-running
   source writes ~145 MB/s and only a *verified* byte watchdog bounds it (§2).
6. **`wavenc` writes an illegal non-extensible 64-bit float WAV** that only
   `soxi` misreports (Precision 54-bit) (§5, §6.2).
7. **`wavenc`'s extensible boundary is channels>2 only** — unlike the ffmpeg
   muxer rule (§6.2).
8. **Property axis fails silently**: out-of-range `volume` is a stderr
   `GLib-GObject-CRITICAL` + clamp at rc=0; `freq` above Nyquist is accepted;
   `ticks` ≡ `silence` at the default tick interval (§6.1).

## 12. Remaining unknowns (honest edges)

- **The fallback's mechanism is characterised, not explained.** I measured
  *which* names fall back and *that* it is audio-path-only; I did not read
  `gstpipewiresrc.c`/`pw_stream_connect` to establish whether the miss retries
  with a NULL target or an explicit default-monitor policy. `pw-record`'s
  identical behaviour suggests the shared `stream.capture.sink` property, but
  that is inference, not measurement.
- **The default sink was never moved**, so "fallback" and "explicit default
  target" remain indistinguishable here (§8 caveat).
- **`-e`'s finalize path was measured, not derived**: I did not test whether
  INT+`-e` on a *live* `pipewiresrc` pipeline can lose buffers at the EOS
  boundary (the counts differed by 4 KiB between the INT legs).
- **`wavenc`'s placeholder arithmetic** (`0x7FFFF000`, RIFF = data+36) is
  pinned for 16-byte fmt chunks; the 40-byte (extensible) case was only
  observed *finalized*, never wounded.
- **The F64LE defect's reader matrix is one witness deep** — `soxi` misreports
  it; a fifth reader (`soxi -s`/`wave`) agrees on frames, and I did not test
  what a *decoder* (not a prober) does with the 64-bit float payload.
- **`pipewiresrc`'s `.monitor` suffix** was only tested against a null sink
  without the prop (fail); with the prop it was not separated from the fallback.
- **One labrat probe was dispatched (probeParent duty) and returned BLOCKED**:
  its profile exposes no shell/process-execution tool, so it could not run a
  single leg. Named class `labrat_no_exec`; **no contradiction was measured**,
  and no second labrat was spawned (exactly one is permitted). Every claim
  above therefore rests on this seat's own receipts only.
