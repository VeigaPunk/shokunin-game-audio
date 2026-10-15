# R82 scout — the ffmpeg/ffprobe/ffplay surface on the PipeWire host

Round 82 pre-measurement. Host `plazir27`. A first seat measured
**2026-10-15 ~06:02–06:30Z** (stages s0–s7+s9) and died upstream; this seat
re-entered **~06:47–07:00Z** and ran `r82_probe_ext.py` (receipt `s8-ext.json`)
to close the gaps — this report covers **both** receipt sets; every cell names
which stage it came from. Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`a2616f7`. Toolchain: **ffmpeg/ffprobe/ffplay n9.0.1** (`--enable-libpulse`,
no pipewire/jack *device* — jack indev only), PipeWire **1.6.8**,
libpulse **17.0-98-gb096** (protocol 35, `PulseAudio (on PipeWire 1.6.8)`),
alsa-utils **1.2.16**, Python **3.14.7**, Linux **7.2.3-arch1-3**.

**Seat: SCOUT (leaf). Zero tracked-file edits. Everything under
`corpus/live/r82-scout/` (2.6 MB at exit — wavs trimmed; `receipts/*.json` +
175 per-leg `runs/**` cmd/stdout/stderr/meta dirs are the durable evidence)
plus this report.** Harnesses `r82_probe.py` (s0–s6, s9) and
`r82_probe_ext.py` (s8, imports the helpers, no new trust boundary). Own
seeded dual-tone (L@1 kHz/R@1.5 kHz + ±30 LSB dither — *a pure 1k/1.5k s16
wav is mis-probed as mpegts by ffmpeg*, measured), own Goertzel window
classifier. Seat objects `r82ff_*`/`r82ffx_*`; every `pactl unload-module`
was index-verified against `sink_name=` first; nothing unloaded by name.

**Contention.** Foreign live objects during the window: `r83dsp_p4_ns`,
`r83dsp_v_ns48`, `r83dsp_v_ns44` (sinks+monitors in `-sources pulse`),
leftover `r78_def_sink_3341762` (marked `*` by `ffmpeg -sinks`!), `r84alsa_ns`
(an r84 `paplay` playing `tone_a.wav` into it appears inside two of this
seat's `pactl list sink-inputs` snapshots — observed, never touched), and at
extension time `r86ctl_ns`. Default sink stayed **SPDIF**
(`alsa_output.usb-…HiFi__SPDIF__sink`) for every session-manager resolution
this seat caused. §7 ledger.

---

## 0. Headline — the frontier cells

| # | frontier item | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | device surfaces (`-devices`/`-sources`/`-formats`) | **PINNED** | `DE pulse`, `DE alsa`, `D jack`, `DE oss`, `DE sndio` — **no pipewire device exists** in n9.0.1: `ffmpeg -f pipewire -i x` → `Unknown input format: 'pipewire'`, rc=**234** (EINVAL class); `-sources pipewire` → rc=0, **empty list**. `-sources pulse`/`-sinks pulse` enumerate every live node incl. foreign ones |
| 2 | `-device`/`device=` targeting vs session default | **ASYMMETRIC** | **capture** validates the name at connect: bogus/source-bare/`default` → rc=**251** EIO in ~0.93 s. **playback never validates**: `-device no_such_sink_r82`, a *source* name, even `<sink>.monitor` → rc=**0**, `target.object` publishes the literal bogus string, and WirePlumber silently re-routes to the default sink — tone measured on SPDIF.monitor all 9 reps, zero stderr warning. `PULSE_SINK=` env and `@DEFAULT_SINK@`/`default` keywords all resolve |
| 3 | stream node naming / media.class / props | **MAPPED** | `node.name`/`application.name` = `-name` (default `Lavf63.1.101` — the libavformat soname), `media.name` = `-stream_name` (indev default `record`; **outdev default = the output URL tail**, `r82ff-play`); class `Stream/Input\|Output/Audio`; publishes `node.latency`, `node.rate=1/48000`, `node.want-driver`, `pulse.attr.{tlength,prebuf,minreq,maxlength\|fragsize}`, `client.api=pipewire-pulse` |
| 4 | sink-loss behaviour | **RE-LINKS BOTH DIRECTIONS** | playback: unload the target sink mid-play → re-linked to `<DEF>:playback_*` in **~0.22 s** (2.09→2.31 s ×3 reps), zero-gap tone on the default-sink monitor witness, rc=0 clean exit. capture: unload under a `…monitor` capture → re-linked to `<DEF>:monitor_*` in **~0.27 s**, file keeps growing (256 KiB write chunks), tone windows continuous 0.0→7.5 s. **Contrast**: r81 `pipewiresrc` freezes at last buffer; r85 `pw-record` emits sustained zeros; ffmpeg-pulse re-links like pw-play |
| 5 | latency/buffering knobs → stream props | **LANDS (position-sensitive)** | outdev: `-buffer_size 16384`→`pulse.attr.tlength=16384`,`prebuf=12548`,`node.latency=2176/48000`; `-buffer_duration 500`→`tlength=96000`; `-minreq 512`→**clamped to 1024**; `-buffer_size 1`→`tlength=3072`, latency `256/48000`. indev: `-fragment_size 2048` **before** `-i`→`fragsize=2048`, `node.latency=512/48000`; `65536`→`16384/48000`. **Same options AFTER `-i` are silently swallowed as output options — no error, no "unused" warning at `-loglevel warning`, props unchanged** (s4 ci* legs + s8 re-runs) |
| 6 | error classes | **TYPED RC MAP** | 251=EIO bogus device / busy PCM / `-i default`; 253=ESRCH indev `-server unix:/nonexistent`; 187 outdev bad server (`Cannot connect context: Access denied`); 222=ERANGE option out-of-range (`rate 0`, `ch 0`, `frag -2` — pre-open validation); **-6=SIGABRT** libpulse asserts (`-channels 99` → `pa_channels_valid`; `-sample_rate 999999` → `pa_sample_spec_valid`; `-frame_size 8192` in *output* position → `enc->sq_idx[0] >= 0` ffmpeg_sched assert); 234=EINVAL `-f pipewire` |
| 7 | `ffplay` surface | **TWO PERSONALITIES** | auto driver → SDL **native PipeWire** client (node `ffplay`, `media.role=Game`, `media.category=Playback`, `node.async`, `node.latency=2048/48000`); `SDL_AUDIODRIVER=pulseaudio` → `client.api=pipewire-pulse` (`media.name="Audio Stream"`, `tlength=6144 B`≈32 ms) — and **`PULSE_SINK` is ignored by SDL's pulse driver** while ffmpeg's own `-f pulse` honors it |
| 8 | `ffprobe` on a live indev | **WORKS** | `ffprobe -show_streams -f pulse -i <sink>.monitor` → rc=0 in ~1.02 s, reports `pcm_s16le 48000 stereo`, **`start_pts`≈epoch µs** (pulse indev `-wallclock 1` default = wall-clock PTS) |
| 9 | `-f alsa` on a PW host | **SPLIT** | `-i default`/`sysdefault` → rc=0 via pipewire-alsa plugin — stream node `application.name="PipeWire ALSA [ffmpeg]"`, `media.name="ALSA Capture"`, `node.latency=128/48000`, and **`PIPEWIRE_PROPS node.name=` lands here** (ignored on the pulse path — libpulse overwrites it); `-i pipewire` → rc=251 `cannot set parameters`; `hw:0,0` capture while PW held the same card's playback → **rc=0** (independent subdevice); `-sample_rate 12345` → silent clamp to 44100, no error |

---

## 1. FRONTIER — device surfaces (`s0-baseline`, `s7-extra`)

`ffmpeg -devices` (3 reps, identical):

```
 DE alsa     ALSA audio output
 D  jack     JACK Audio Connection Kit   (indev only)
 DE oss      OSS playback
 DE pulse    Pulse audio output          ← the only PW-reaching surface
 DE sndio    sndio audio playback
 (+fbdev/kmsgrab/lavfi/v4l2/x11grab/xv non-audio)
```

- **No `pipewire` device.** `-f pipewire -i x` → `Unknown input format:
  'pipewire'` / rc **234**; `ffmpeg -sources pipewire` → rc 0, empty.
- `ffmpeg -sources pulse` lists every live source incl. foreign monitors
  (`r83dsp_*.monitor`, `r78_def_sink_3341762.monitor`), `*` marking
  `alsa_input.…Line__source`; `-sinks pulse` listed `*` on
  **`r78_def_sink_3341762` while `pactl info` said `Default Sink: SPDIF` in
  the same minute** — ffmpeg's default-marker disagreed with pactl's
  (recorded; falsification item 11).
- `pactl info`: `Server Name: PulseAudio (on PipeWire 1.6.8)`, protocol 35.
- Indev opts (`-h demuxer=pulse`): `server`, `name` (default
  `Lavf63.1.101`), `stream_name` (default `record`), `sample_rate` (48000),
  `channels` (2), `frame_size` (1024, **deprecated**), `fragment_size` (-1),
  `wallclock` (1). Outdev (`-h muxer=pulse`): `server`, `name`,
  `stream_name`, `device`, `buffer_size`, `buffer_duration` (ms), `prebuf`,
  `minreq`.
- `ffprobe -show_streams -f pulse -i r82ff_ns.monitor` → rc=0, ~1.02 s,
  `pcm_s16le s16 48000 2ch`, `start_time`≈epoch s (wallclock PTS). ×2.

## 2. FRONTIER — targeting lattice (`s1-capture`, `s2-playback`, `s8-ext`)

### 2.1 Capture (`-f pulse -i <dev>`, 3 reps each unless noted)

| `-i` arg | rc | wav / links | note |
| --- | --- | --- | --- |
| `r82ff_ns.monitor` | 0 | 96–97 k frames, peak 8222, tone windows present | `target.object=r82ff_ns`, links `← ns:monitor_FL/FR` |
| `r82ff_ns` (bare sink) | **251** | none | sinks are not sources — EIO ~0.93 s |
| `no_such_source_r82` | **251** | none | validated at connect |
| `alsa_output.…SPDIF__sink` (bare) | **251** | none | same class |
| `alsa_input.…Line__source` | 0 | silence (peak 0) — Line is silent | `target.object=<src>`; `stream.capture.sink` absent, direct capture |
| `default` | **251 EIO ×3 + 1 hang** (c0) then **251 ×3** (x0 recheck, second session) | none | the literal string `default` does NOT mean "default source" on the capture side — 6/7 attempts EIO |
| `@DEFAULT_MONITOR@` | 0 | links via `target.object=…SPDIF__sink` + `stream.capture.sink` | pactl-style alias **works in the ffmpeg indev** (contrast: bare `default` fails) |
| `@DEFAULT_SOURCE@` | 0 | `target.object=…Line__source` | works |
| `-server unix:/nonexistent-r82 -i default` | **253** | none | `No such process` — distinct class |
| `-name X -stream_name Y -i ns.monitor` | 0 | tone lands | `node.name=application.name=X`, `media.name=Y` |
| `-sample_rate 44100 -channels 1 -i ns.monitor` | 0 | **44100/1ch** wav | `node.latency=2205/44100` (same 50 ms) |
| `-channels 7 -i ns.monitor` | 0 | 7-ch wav | server guesses `6.1` layout — accepted |
| `PIPEWIRE_PROPS='{node.name=r82ff_env stream.capture.sink=true}' -i ns.monitor` | 0 | tone | `stream.capture.sink` **lands**; `node.name` **overridden** to `Lavf63.1.101` — libpulse sets `node.name=application.name` explicitly, beating env props |

### 2.2 Playback (`-f pulse [-device X] <url>`, 3 reps each; content witnesses
on `r82ff_ns.monitor` **and** `SPDIF.monitor`)

| `-device` | rc | `target.object` published | where the tone landed |
| --- | --- | --- | --- |
| `r82ff_ns` | 0 | `r82ff_ns` | **ns only** (ns-mon tone, def-mon silent) |
| *(absent)* | 0 | *(no prop)* | SPDIF (session default) |
| `default` | 0 | `default` | SPDIF |
| `@DEFAULT_SINK@` | 0 | `…SPDIF__sink` | SPDIF |
| `PULSE_SINK=r82ff_ns` env | 0 | `r82ff_ns` | **ns** (env honored by ffmpeg's outdev) |
| `no_such_sink_r82` | **0** | `no_such_sink_r82` | **SPDIF — silent fallback, zero warning** |
| `alsa_input.…Line__source` (a source) | **0** | `…Line__source` | **SPDIF — same silent fallback** |
| `r82ff_ns.monitor` (a monitor) | **0** | `r82ff_ns.monitor` | **SPDIF — same silent fallback** |
| `-server unix:/nonexistent-r82 -device r82ff_ns` | **187** | — | `Cannot connect context: Access denied` |

The playback path never checks that `-device` exists — the string is copied
into `target.object` and WirePlumber resolves-or-defaults. The capture path
validates at `connect_record` and returns EIO. **Same surface, opposite
failure visibility.**

Default node props (p0, all reps): `media.class=Stream/Output/Audio`,
`node.latency=8192/48000` (~171 ms), `node.rate=1/48000`,
`node.want-driver=true`, `node.autoconnect=true`,
`node.loop.name=data-loop.0`, `client.api=pipewire-pulse`,
`pulse.attr.tlength=384000` (2 s @48 kHz×4 B), `pulse.attr.prebuf=380164`,
`pulse.attr.minreq=3840` (20 ms), `pulse.attr.maxlength=4194304`,
`stream.is-live=true`, `port.group=stream.0`, `window.x11.display=:0`,
plus `application.process.{id,host,binary=ffmpeg,…}`.

## 3. FRONTIER — sink loss (`s3-loss`, 3+3 reps)

Playback into `r82ff_ns`, `pactl unload-module <idx>` at t≈2.1 s of an 8 s
`-re` tone:

| rep | unload t | re-linked to `SPDIF:playback_FL/FR` at | witness (SPDIF.monitor tone windows) | rc |
| --- | --- | --- | --- | --- |
| 0 | 2.09 s | 2.31 s | 2.0→7.0 s, **no missing window** | 0 |
| 1 | 2.11 s | 2.32 s | 2.0→7.0 s | 0 |
| 2 | 2.07 s | 2.34 s | 2.0→7.0 s | 0 |

Capture from `r82ff_ns.monitor` (a seat pump feeding it tone), unload at
t≈2.07 s:

| rep | re-linked to `SPDIF:monitor_*` at | file | tone windows |
| --- | --- | --- | --- |
| 0–2 | ~2.34–2.36 s | keeps growing, 256 KiB write chunks, `max_u32` streaming header (killed) | 0.0→7.5 s continuous — the pump **also** re-linked to SPDIF, so the re-linked monitor still carried it |

**Law**: `ffmpeg -f pulse` streams are pw-play-class under target loss —
WirePlumber re-links them to the session default in ~0.2–0.3 s, both
directions. Not the r81 `pipewiresrc` freeze and not the r85 `pw-record`
sustained-zeros class. ffmpeg itself does nothing (no message, no rc change) —
the re-link is entirely session-manager work.

## 4. FRONTIER — buffer knobs → props (`s4-buffers` + `s8-ext`)

### 4.1 Outdev (correctly placed, between `-f pulse` and the URL) — all land

| opts | `tlength` | `prebuf` | `minreq` | `node.latency` |
| --- | --- | --- | --- | --- |
| *(default)* | 384 000 | 380 164 | 3 840 | 8192/48000 (171 ms) |
| `-buffer_size 16384` | **16 384** | 12 548 | 3 840 | **2176/48000 (45 ms)** |
| `-buffer_duration 500` | **96 000** (=500 ms×192 B) | 92 164 | 3 840 | 8192/48000 |
| `-prebuf 8192` | 384 000 | **8 192** | 3 840 | 8192/48000 |
| `-minreq 512` | 384 000 | 382 980 | **1 024** (clamped up) | 8192/48000 |
| `-buffer_size 32768 -buffer_duration 200 -prebuf 16384 -minreq 1024` | **38 400** (the 200 ms duration wins over 32 KiB) | 16 384 | 1 024 | 8192/48000 |
| `-buffer_size 1` | **3 072** floor | 2 052 | 1 024 | **256/48000 (5.3 ms)** |

### 4.2 Indev — position decides whether the knob exists at all

| position | cmd shape | result |
| --- | --- | --- |
| **before `-i`** | `-f pulse -fragment_size 2048 -i ns.monitor` | `pulse.attr.fragsize=2048`, `node.latency=512/48000` — **lands** (×3) |
| before `-i` | `-fragment_size 65536` | `fragsize=65536`, `node.latency=16384/48000` (~341 ms) (×3) |
| before `-i` | `-frame_size 8192` | rc=0 + `The "frame_size" option is deprecated` — read-chunk only, fragsize stays 9600 (×3) |
| **after `-i`** | `-i ns.monitor -fragment_size 2048 …` | **silently unused**: rc=0, fragsize stays 9600, zero warning at `-loglevel warning` (×3 — s4 ci1) |
| after `-i` | `-i ns.monitor -frame_size 8192 …` | **SIGABRT** `Assertion enc->sq_idx[0] >= 0 failed at fftools/ffmpeg_sched.c:1874` (×3 — s4 ci2): consumed as an *encoder-side* option |
| after `-i` | `-i ns.monitor -sample_rate 44100 -channels 1 …` | **silently unused**: wav still 48000/2ch (×3 — s4 ci4; contrast c5 with the same options before `-i` → real 44100/1ch) |

Defaults on the indev side: `pulse.attr.fragsize=9600` (50 ms),
`node.latency=2400/48000`, `maxlength=4194304`.

## 5. FRONTIER — error-class map (`s5-alsa`, `s6-errors`, `s7-extra`, `s8-ext`)

| leg | rc | stderr signature |
| --- | --- | --- |
| `-f pulse -i` bogus/sink-bare/`default` | **251** | `Error opening input: Input/output error` (EIO) |
| indev `-server unix:/nonexistent` | **253** | `Error opening input: No such process` (ESRCH) |
| outdev `-server unix:/nonexistent` | **187** | `Cannot connect context: Access denied` → `Could not write header … Generic error in an external library` |
| `-sample_rate 0` / `-channels 0` / `-fragment_size -2` | **222** | `Value … for parameter 'X' out of range [1|-1 - 2.14748e+09]` → `Numerical result out of range` (ERANGE) — AVOption validation, pre-connect |
| `-channels 99` | **-6** | libpulse `Assertion 'pa_channels_valid(channels)' failed … channelmap.c:400` SIGABRT |
| `-sample_rate 999999` | **-6** | `Assertion 'pa_sample_spec_valid(spec)' failed … sample.c:67` SIGABRT |
| `-f alsa -i hw:0,0` while `arecord` holds capture | **251** | `cannot open audio device hw:0,0 (Device or resource busy)` ~21 ms — EBUSY surfaces as EIO |
| `-f alsa hw:0,0` playback while `aplay` holds | **251** | `cannot open audio device hw:0,0 (Device or resource busy)` → `Could not write header` |
| `-f alsa -i hw:0,0` while **PipeWire streams the same card's Speaker sink** | **0** | clean 2 s capture — playback and capture subdevices are independent |
| `-f alsa -i hw:0,0 -sample_rate 12345` | **0** | silent clamp to **44100** — no negotiation error exists at this surface (x6) |
| `-f alsa -i pipewire` | **251** | `cannot set parameters (No such file or directory)` — ffmpeg's ALSA indev cannot drive the pipewire PCM plugin (aplay `-D pipewire` works — ffmpeg-specific refusal) |
| `-f alsa -i default` / `sysdefault` | **0** | via pipewire-alsa plugin — see §6 |
| `-f pipewire -i x` | **234** | `Unknown input format: 'pipewire'` (EINVAL) |
| `-f pulse -i default` | **251** | EIO — see §2.1 (also e6 duplicate rows) |

## 6. FRONTIER — ffplay + the ALSA-plugin identity (`s8-ext`)

- `ffplay -nodisp -autoexit tone.wav` headless, rc=0, ~2.0 s wall ×3.
  `-nostdin` is **not** an ffplay option: rc=1 `Failed to set value
  '-nodisp' for option 'nostdin'` (option-parser collision — logged as a
  harness artifact; the real legs run without it).
- **Auto driver → SDL's native PipeWire client** (SDL ≥ its own pw backend):
  `node.name=ffplay`, `media.name=ffplay`, `media.class=Stream/Output/Audio`,
  `media.category=Playback`, **`media.role=Game`**, `media.type=Audio`,
  `node.async=true`, `node.always-process=true`, `node.loop.name=SDLAudioP19`,
  `node.latency=2048/48000`, `target.object=…SPDIF__sink`. No
  `client.api=pipewire-pulse` — native.
- **`SDL_AUDIODRIVER=pulseaudio` → pipewire-pulse client**: `node.name=
  ffplay`, `media.name="Audio Stream"`, `node.latency=512/48000`, tiny
  `pulse.attr.tlength=6144 B` (~32 ms) / `prebuf=4100` / `minreq=2048`,
  `target.object=…SPDIF__sink` — and **`PULSE_SINK=r82ff_ns` was ignored**
  (still SPDIF). Same env honored by `ffmpeg -f pulse` (§2.2). SDL's pulse
  backend doesn't route `PULSE_SINK` the way libavdevice's does.
- `-f alsa -i default` → captures through pipewire-alsa: node
  `application.name="PipeWire ALSA [ffmpeg]"`, `media.name="ALSA Capture"`,
  `node.latency=128/48000`, and **`PIPEWIRE_PROPS '{node.name=…}'` lands**
  (published as `node.name=r82ffx_x5`) where the pulse path overrode it.
- hw:0 = **card 0 `USB Audio`** (Generic USB Audio, usb-0000:11:00.0-12):
  capture devices 0/2 free when PW only plays; `hw:0,0` capture +
  PW-playback on the same card coexist (x6 + s5 `cap_hw00_pwheld`).

## 7. Contention ledger (mandatory)

- Foreign objects live during the window, all tagged by name in receipts:
  `r83dsp_p4_ns`/`r83dsp_v_ns48`/`r83dsp_v_ns44` (visible in `-sources pulse`
  rep0), leftover `r78_def_sink_3341762` (the `*` discord in §1), `r84alsa_ns`
  with an r84 `paplay` of `tone_a.wav` mid-p-stage (its sink-input block
  appears in 3 s2 `sink_input` snapshots — recorded, never touched), and
  `r86ctl_ns` at extension time. No `set-default-*` issued here.
- **Interference caused by this seat**: ~5.3 s of tag tone ×3 reps landed on
  the real **SPDIF** sink during the loss-relink legs (that is the
  measurement — re-link targets the session default); bogus-`-device` legs
  each put ≤2 s on SPDIF. `PULSE_SINK`/`PIPEWIRE_PROPS` were per-process
  env, never server state. No foreign module/node/stream unloaded, moved,
  suspended or re-volumed.
- **Inherited debt, disclosed**: `s9-final` found one orphaned
  `r82ff_ffpump` ffmpeg node (`pulse.corked=false`, idle, pid 3524495) —
  an interrupted pump outliving its harness. Verified gone at this seat's
  exit: `pactl list short modules | grep r82ff` → 0 rows; `pw-dump` → no
  `r82ff*`/`ffplay`/`Lavf*` nodes; no matching processes.
- The earlier seat's `runs/extra/` dir exists but empty (s7 legs never wrote
  per-leg receipts — consolidated JSON only, kept).

## 8. Receipts index

| artifact | sha256 (prefix) |
| --- | --- |
| `receipts/s0-baseline.json` (devices/formats/sources/sinks/help/pactl, ×3) | `13d892fbae6e9dd4` |
| `receipts/s1-capture.json` (11 capture legs ×3) | `b9fc15f440e46dee` |
| `receipts/s2-playback.json` (10 playback legs ×3, dual witnesses) | `16a39637d6a880df` |
| `receipts/s3-loss.json` (re-link timelines, 3+3) | `cb00415df0eb97a8` |
| `receipts/s4-buffers.json` (7 out + 5 in knob legs ×3) | `63c71c94117bac2c` |
| `receipts/s5-alsa.json` (busy/pw-held/bogus/pipewire/default) | `41e17c3a23ea2699` |
| `receipts/s6-errors.json` (option-range + libpulse asserts) | `c64e0d526b03a831` |
| `receipts/s7-extra.json` (`-f pipewire`, alias/serial targeting) | `abf4afda7adbc4a5` |
| `receipts/s8-ext.json` (this seat: x0–x7 + ffplay/ffprobe/hw-id) | `f06b73fe3801f34c` |
| `receipts/s9-final.json` (cleanup + orphan-node snapshot) | `b522225e3ebeb524` |
| `runs/**` — 175 per-leg receipt dirs (`cmd.txt`/`stdout`/`stderr`/`meta`) | — |

## 9. Verbatim-armable cells

| # | arm | expected |
| --- | --- | --- |
| A1 | `ffmpeg -hide_banner -devices` | `DE pulse`, **no pipewire row** |
| A2 | `ffmpeg -f pipewire -i x` | rc=234, `Unknown input format: 'pipewire'` |
| A3 | `pactl load-module module-null-sink sink_name=NS` then `ffmpeg -re -i TONE -f pulse -device NS out` | rc=0; node `Lavf63.1.101` `Stream/Output/Audio` `target.object=NS`; `pulse.attr.tlength=384000` |
| A4 | same + `-device no_such_sink_r82` | **rc=0**, `target.object=no_such_sink_r82`, links land on `<DEF>` — silent fallback |
| A5 | A3 then `pactl unload-module <idx>` mid-play | re-link to `<DEF>:playback_*` within ~0.3 s; rc=0 |
| A6 | `ffmpeg -f pulse -i NS.monitor -t 2 -c:a pcm_s16le o.wav` with `PIPEWIRE_PROPS='{stream.capture.sink=true}'` | rc=0 tone-bearing wav; node `fragsize=9600`, `node.latency=2400/48000` |
| A7 | same but `-i default` | **rc=251 EIO** (capture-side literal `default` fails) |
| A8 | `-f pulse -i @DEFAULT_MONITOR@` | rc=0, resolves to `<DEF>` monitor |
| A9 | `-f pulse -fragment_size 2048 -i NS.monitor …` vs `-i NS.monitor -fragment_size 2048 …` | before: `fragsize=2048`/`latency 512/48000`; after: **unchanged, no warning** |
| A10 | `-i NS.monitor -frame_size 8192 -t 2 …` (after `-i`) | SIGABRT `enc->sq_idx[0] >= 0` |
| A11 | `-f pulse -buffer_size 16384 -device NS out` | `tlength=16384`, `node.latency=2176/48000` |
| A12 | `-f pulse -i no_such_source_r82` | rc=251 EIO ~0.93 s |
| A13 | `-f pulse -server unix:/nonexistent -i default` / `-f pulse -server unix:/nonexistent out` | 253 ESRCH / 187 `Access denied` |
| A14 | `-f pulse -channels 99 -i NS.monitor` | SIGABRT `pa_channels_valid` |
| A15 | `arecord -D hw:0,0 …` held, then `ffmpeg -f alsa -i hw:0,0 -t 2 o.wav` | rc=251 `Device or resource busy` ~21 ms |
| A16 | `ffmpeg -f alsa -i pipewire -t 2 o.wav` | rc=251 `cannot set parameters` |
| A17 | `SDL_AUDIODRIVER=pulseaudio PULSE_SINK=NS ffplay -nodisp -autoexit TONE` | node `ffplay` `client.api=pipewire-pulse`, `tlength=6144`, **`target.object=<DEF>`** (env ignored) |
| A18 | `ffprobe -show_streams -f pulse -i NS.monitor` | rc=0 ~1 s, `pcm_s16le 48000 2ch`, wallclock `start_time` |
| A19 | `ffmpeg -sinks pulse` while `pactl info` says `Default Sink: X` | `*` row may disagree (observed r78 leftover `*` vs SPDIF default) |

## 10. Falsification list

1. "no pipewire device in n9.0.1" — an `-f pipewire` leg that opens, or a
   `pipewire` row in `-devices`.
2. "playback `-device` is unvalidated" — a bogus `-device` leg returning
   rc≠0 or producing no stream node.
3. "capture validates" — a bogus `-i` leg returning rc=0 with a linked node.
4. "both directions re-link ~0.2–0.3 s" — a loss leg with frozen links, a
   zeros tail, or an rc≠0 exit.
5. "knobs land in `pulse.attr.*`" — a `-buffer_size`/`-fragment_size`
   (pre-`-i`) leg whose published props equal the defaults.
6. "post-`-i` indev options are silently unused" — one that lands on props
   or errors; and the `-frame_size` SIGABRT is claimed *position-dependent*
   (pre-`-i` survives, deprecated) — a pre-`-i` crash would falsify.
7. "`-i default` fails on capture" — a succeeding `default` capture
   (1 hang + 6 EIO observed across two sessions; a success suggests
   server-state dependence, worth re-measuring).
8. "rc classes typed" — a bogus source returning anything but 251/EIO, or
   bad-server legs swapping 253/187.
9. "hostile params SIGABRT" — `-channels 99` returning a normal error rc.
10. "`-f alsa -i pipewire` refuses while `-i default` works" — either leg
    flipping (note: the plugin stream is `PipeWire ALSA [ffmpeg]`-branded).
11. "ffmpeg `-sinks`/`-sources` `*` can disagree with pactl Default" —
    claimed only as *observed once* (r78 leftover marked `*` while SPDIF was
    pactl default); a stable agreement would retire the cell.
12. "SDL-pulse ignores `PULSE_SINK`" — an `SDL_AUDIODRIVER=pulseaudio`
    ffplay leg whose `target.object` follows `PULSE_SINK`.

## 11. Remaining unknowns (honest edges)

- Whether ffmpeg-pulse re-link timing (~0.22–0.27 s) is a WirePlumber
  constant or load-dependent — only 3+3 reps on this host's WP 0.5.17.
- The `default` capture failure mechanism (literal-name lookup vs
  NULL-means-default in pipewire-pulse) is inferred from the alias contrast;
  not read from source.
- `pactl list sink-inputs` snapshots are weak attribution under sibling
  traffic — the pw node/link evidence is authoritative; two si blocks show
  an r84 paplay instead of the seat stream (grep-matched the wrong block).
- `-buffer_duration`+`-buffer_size` precedence observed once (duration won);
  order-dependence unprobed.
- `ffmpeg -sinks` `*` provenance (which server field it marks) unverified —
  discordance with `pactl info` measured, mechanism not.
- Whether `-wallclock 0`/`-frame_size` change packet timing measurably —
  props identical; only deprecation text observed.
