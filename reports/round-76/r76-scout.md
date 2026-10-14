# r76-scout (audio) — pre-measurement of the capture surface: pw-record / parec / arecord / ffmpeg

Seat **scout** (leaf, report-only). Wave `shokunin-train-20261101-w15`, lane
audio, repo `/home/vgpnk/Projects/shokunin/audio-shokunin`, HEAD **`2250be9`**
(unchanged all session; `git rev-parse HEAD` at 17:29Z and again at 17:36Z).
Host `plazir27`, window 2026-10-14 **17:29Z–17:38Z** (UTC; local TZ UTC−3, so
`ls` mtimes are local). Write scope honoured: this report +
`corpus/live/r76-scout/` only. **No fixture edit, no receipt mode was run, no
`corpus/live/runs/*` receipt was written** — every artifact below is scout
scratch under `corpus/live/r76-scout/`. No git mutation, no subagents.

**LSP device: unavailable this session.** `mcp_list_servers` → only `rea`
(Ghidra/REA binary analysis: `annotate_native_function` and dossiers; no
`definition` / `references` / `hover` / `type_definition` / `implementation`).
No source trace was possible for any client binary; every *mechanism* sentence
below is labelled **inference** and rests on process-level measurement with
retained artifacts, never on grep-as-proof. No text grep is offered as semantic
proof anywhere in this report.

Toolchain (measured, `probe-versions-help.txt`, `probe-ffmpeg-capture.txt`):
`pw-record`/`pw-cat` **1.6.8** (libpipewire 1.6.8), `parec`/`parecord`/`pacat`
**17.0-98-gb096** (libpulse 17.0.0), `arecord` **alsa-utils 1.2.16**, `ffmpeg`
**n9.0.1** (lavf 63.1.101, `--enable-libpulse`). Server: `pactl info` →
`PulseAudio (on PipeWire 1.6.8)`, protocol 35, **Default Source
`alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source`**.

---

## Headline — eight results that change what the author should build

1. **The default source is NOT reachable by the implicit default of two of the
   four consumers.** `pw-record` with no `--target` → `rc=1`, 44-byte header,
   `stream node … error: no target node available`; `parec` with no `-d` →
   `rc=1`, 0 B, `Stream error: No such entity`. Yet `parec -d @DEFAULT_SOURCE@`
   works and `pw-record --target <source name>` works. "The default source" is
   reachable **only through the explicit token / explicit name**.
2. **Monitor capture is not one surface but two.** `parec -d @DEFAULT_MONITOR@`
   and `ffmpeg -f pulse -i <sink>.monitor` accept the `.monitor` name directly;
   `pw-record --target <sink>.monitor` **fails** (`no target node available`) —
   it needs `--target <sink> -P stream.capture.sink=true`.
3. **`arecord -D default` and `-D pipewire` are BLOCKED for capture** on this
   host (`set_params:1462: Unable to install hw params`) although r75 measured
   both **viable for playback**. The inversion is capture-side. Viable capture
   devices: `null`, `sysdefault`, `hw:0,0` / `plughw:0,0` **stereo 48 k only**
   (mono 48 k → `set_params:1404: Channels count non available`, the same
   rejection class r75 saw on the playback side).
4. **`arecord -D null` is an exact-size, garbage-content, unpaced oracle — and a
   filesystem hazard.** `-d 1` → exactly `192044` B (44 + 48000×2×2) in
   **0.01 s**; two identical-argv runs differ in **112 of 192000** data bytes
   (content is *not* reproducible). With **no** `-d`/`-d 0` it does not block: it
   floods **2 GiB split files (`name-01.wav`, `-02`, …) at ≈5.8 GB/s**. My own
   harness produced **91 GB** of split files before I noticed and deleted them
   (see §6).
5. **The `-t`/duration cap is not one property.** `arecord -d N` is **exact**
   (192000 B/s at 48 k stereo, both on the unpaced null device and on hardware);
   `pw-record --sample-count N` is **exact** (19200 B for 4800 frames);
   `ffmpeg -t 1` overshoots **≈0.6 %** on a paced pulse source (193490 B,
   192258 B on repeat) and **≈10×** on the unpaced `alsa null` device
   (1928910 B, 1509522 B on repeat — non-reproducible); `parec` has **no**
   duration/byte flag at all (bound must be TERM/KILL + an outer `timeout`).
6. **SIGTERM finalizes the header for all four consumers; SIGKILL does not —
   and the failure mode differs per consumer.** TERM → finalized RIFF/data sizes
   (usable). KILL → pw-record & parec leave `riff=8, data=0` (stdlib `wave`
   **rejects**), arecord leaves the **placeholder `data=0x80000000`** (stdlib
   `wave` *accepts* and reports 536870912 frames ≈ 3.1 h; ffprobe tolerates it
   and reports 1.125 s), ffmpeg leaves **0 bytes** (nothing below its 256 KiB
   output buffer had flushed).
7. **rc is never the verdict here either.** `pw-record`/`pw-cat -r` exit **1**
   after a *complete, correctly finalized* bounded capture (even with `-v` there
   is no error line); `parec` exits **0** with **0 bytes** written when TERM
   arrives before its first 64 KiB stdout flush; `ffmpeg` exits **255** on TERM;
   `arecord` exits **1** with `Aborted by signal Terminated...`.
8. **The roundtrip cell works and is measurable.** Playing
   `corpus/artifacts/stem_sections.wav` into the default sink while capturing its
   monitor with three different consumers reproduces the source's **two-section
   RMS envelope** (2090.6 → 2501.2 int16 counts vs source 2090.9 → 2495.5) and
   the **identical peak level** (−15.27 dBFS), with the spectral centroid
   shifted 199.5 Hz → 208.4 Hz (+4.5 %).

---

## 1. Viability gates (measured) — which cells are viable vs blocked

`probe-pactl-sources.txt`, `probe-pactl-info.txt`, `probe-pwlink.txt`,
`probe-arecord-devices.txt`, `probe-ffmpeg-capture.txt`, `runs/scout-capture-all.json`.

Source inventory on this host (`pactl list sources short`, rc=0): **6 sources** —
4 monitors (`pci-0000_01_00.1.hdmi-stereo.monitor`,
`usb-…HiFi__SPDIF__sink.monitor`, `…Speaker__sink.monitor`,
`…Headphones__sink.monitor`) and **2 real capture sources**
(`…HiFi__Line__source` = Default Source, `…HiFi__Mic__source`), all 48 kHz
stereo, states `SUSPENDED`/`IDLE`. `pw-link -o` (rc=0) shows the monitor ports
as **ports on the sink node** (`…SPDIF__sink:monitor_FL/FR`) plus
`…Line__source:capture_FL/FR` — the monitor is not a node of its own.
`arecord -l` (rc=0): **3 capture devices on card 0** (USB Audio dev 0/1/2);
`arecord -L` adds plugins `null`, `sysdefault`, `pipewire`, `default`.
`ffmpeg -devices`: `pulse` and `alsa` are both `DE` (demux **and** mux) —
`ffmpeg -h demuxer=pulse` lists `-server -name -stream_name -sample_rate
-channels -frame_size -fragment_size -wallclock`; `-h demuxer=alsa` lists only
`-sample_rate -ch_layout`.

| consumer | requirement | verdict on this host | witness (exact) |
|---|---|---|---|
| `pw-record` | PipeWire daemon + **explicit node** | **viable only with `--target <name>`** | no `--target` → `rc=1`, 44 B, `no target node available`; `--target <Line__source>` → 19244 B |
| | monitor as `--target <x>.monitor` | **blocked** | `rc=1`, 44 B, `no target node available` |
| | monitor as `--target <sink> -P stream.capture.sink=true` | **viable** | 19244 B / 192044 B, finalized header |
| | `--target 0` (don't link) | **blocked** | 44 B, ran to the 10 s wall bound, KILLed (−9) — no data ever |
| | daemon gate | **named failure** | `PIPEWIRE_RUNTIME_DIR=/nonexistent` → `rc=1` `pw_context_connect() failed: Host is down` |
| `parec`/`parecord` | Pulse server + **explicit `-d`** | **viable with `-d <name>` or `-d @DEFAULT_SOURCE@` / `@DEFAULT_MONITOR@`** | no `-d` → `rc=1` 0 B `Stream error: No such entity`; `-d @DEFAULT_SOURCE@` → 1966080 B in 12 s |
| | daemon gate | **named failure** | `PULSE_SERVER=unix:/nonexistent` → `rc=1` 0 B `Connection failure: Connection refused` / `pa_context_connect() failed` |
| | bad device name | **named failure** | `-d does.not.exist` → `rc=1` `Stream error: No such entity` |
| `arecord` | an ALSA device | **viable: `null`, `sysdefault`, `hw:0,0`, `plughw:0,0` (stereo 48 k)** | `-D hw:0,0 -d 1 -c 2` → `rc=0`, 192044 B in 1.036 s |
| | `-D default`, `-D pipewire` | **blocked for capture** | `set_params:1462: Unable to install hw params:` + the full hw-params dump (1 ch and 2 ch alike) |
| | `-D hw:0,0 -c 1` | **blocked (format)** | `set_params:1404: Channels count non available` |
| | unknown device / card | **named failure** | `-D does_not_exist` → `ALSA lib … [error.pcm] Unknown PCM does_not_exist` + `main:850: audio open error: No such file or directory`; `-D hw:9,9` → `Cannot get card index for 9` + same `main:850` |
| `ffmpeg -f pulse` | pulse server + device name | **viable** | `-i <Line__source> -t 1` → `rc=0`, 193490 B, 1.178 s wall; `-i <…monitor>` → `rc=0`, 194390 B |
| | bad device / dead server | **named failure, two classes** | `-i does.not.exist` → `rc=251` (`Input/output error`); `PULSE_SERVER=unix:/nonexistent` → `rc=253` (`No such process`) |
| `ffmpeg -f alsa` | an ALSA device | **viable: `null`, `plughw:0,0`** | `-i plughw:0,0 -t 1` → `rc=0`, 192618 B; `-i null -t 1` → `rc=0`, 1928910 B |
| | `-i default` | **blocked** | `cannot set parameters (No such file or directory)` → `rc=251` |
| | bad device | **named failure** | `-i does_not_exist` → `ALSA lib … Unknown PCM` + `cannot open audio device … (No such file or directory)` → `rc=251` |

rc encoding note (measured, needed to read the table): ffmpeg returns
`-AVERROR` truncated to 8 bits, so `251 = −5 (EIO)`, `253 = −3 (ESRCH)`,
`234 = −22 (EINVAL)`.

## 2. Can each consumer produce bytes at all — and under what cap

| consumer | exact argv (bound) | rc | wall | bytes | header |
|---|---|---|---|---|---|
| `pw-record` | `--target LINE --sample-count 4800 --rate 48000 --channels 2 --format s16` | **1** | 0.131 s | **19244** (=44+4800×4) | finalized |
| `pw-record` | `--sample-count 48000` (1.0 s) | **1** | 1.026 s | **192044** | finalized |
| `pw-record` | `--sample-count 0` + TERM@1.2 s | 1 | 1.218 s | 229420 (≈1.194 s) | finalized |
| `pw-cat -r` | same as row 1 | **1** | 0.131 s | 19244 | finalized |
| `parec` | `-d @DEFAULT_SOURCE@ --raw` + TERM@2.0 s | 0 | 2.013 s | **65536** | raw |
| `parec` | `--file-format=wav` + TERM@2.5 s | 0 | 2.516 s | **131116** (=44+131072) | finalized |
| `arecord` | `-D null -d 1 -c 2` | 0 | **0.010 s** | **192044** | finalized |
| `arecord` | `-D null -d 5 -c 2` | 0 | 0.002 s | **960044** | finalized |
| `arecord` | `-D hw:0,0 -d 1 -c 2` | 0 | 1.036 s | **192044** | finalized |
| `ffmpeg -f pulse` | `-i LINE -t 1` (wav) | 0 | 1.178 s | **193490** | finalized |
| `ffmpeg -f pulse` | `-i LINE -t 1 -f s16le` (raw) | 0 | 1.157 s | **195248** | raw |
| `ffmpeg -f pulse` | `-i LINE -t 2` | 0 | 2.133 s | 383990 | finalized |
| `ffmpeg -f alsa` | `-i null -t 1` | 0 | 1.028 s | **1928910** | finalized |

All four consumers produce bytes on this host — **no consumer is fully blocked**,
but each needs a different device-naming idiom (§1) and a different bound (§5).

## 3. Sever classes: TERM vs KILL, and what "usable partial wav" means

`runs/scout-capture-all.json` legs `sev*`, `kill-*`; header verdicts computed
from the raw bytes and from two parsers (stdlib `wave`, `ffprobe`).

| consumer | SIGTERM@1.2 s | header after TERM | SIGKILL@1.2 s | header after KILL | file bytes after KILL |
|---|---|---|---|---|---|
| `pw-record` | dies, **rc=1**, 1.218 s | **finalized** `riff=229412 data=229376` | dies, **−9** | `riff=8 data=0` | 229420 (data present!) |
| `parec --file-format=wav` | dies, **rc=0**, 1.217 s | **finalized** (44 B empty file) | dies, **−9** | `riff=8 data=0` | 44 |
| `arecord -D hw:0,0` | dies, **rc=1**, 1.288 s, `Aborted by signal Terminated...` | **finalized** `data=216136` | dies, **−9** | **placeholder** `riff=2147483684 data=2147483648` | 216044 |
| `ffmpeg -f pulse` | dies, **rc=255**, 1.620 s | **finalized** (`fmt`+`LIST`+`data` chunk chain consistent) | dies, **−9** | **file is 0 bytes** | 0 |

Parser-dependent usability of the *same* KILL-unfinalized arecord file
(`kill-arec-hw00.wav`, 216044 B, `data=0x80000000`):

- `ffprobe` → `duration=1.125` (derives from the real file size; tolerant).
- Python stdlib `wave` → **accepts**, `getnframes() = 536870912` (≈3.1 h at
  48 kHz) — a *silently false* duration rather than a rejection.
- For comparison: the TERM-finalized twin `sev1-arec-hw00.out` → stdlib `wave`
  frames `54034` (= 216136/4) — exact.

**So "usable partial wav" must name the parser.** The stdlib-`wave`-reject class
(`riff=8 data=0`, pw-record/parec KILLs) and the stdlib-`wave`-accept-but-lie
class (arecord KILL placeholder) are *different* failure modes; ffprobe hides
both.

TERM ladder detail: `pw-record` dies to **TERM₁** (the TERM₂@1.6 s leg is
degenerate — the process was already gone at 1.217 s), `arecord` likewise
(`Aborted by signal Terminated...` then exit 1), `parec` exits 0, `ffmpeg`
exits 255 after ~0.4 s of drain. No consumer in this arm needed the
`timeout -s KILL` backstop to *stop*; the backstop is still required as the outer
bound (and is what produced every `kill-*` row).

## 4. Output-name / format axis: extension-driven vs flag-driven

| consumer | evidence | verdict |
|---|---|---|
| `ffmpeg` | same argv into `…gate-ff-pulse-line-t1.out` → `rc=234` `Error initializing the muxer …: Invalid argument`; into `…wav` → `rc=0`, valid WAV; `-f s16le` → raw | **extension-driven**, `-f` overrides |
| `arecord` | `-t wav` → 192044 B (RIFF); `-t raw` → 192000 B; `-t raw` **into a `.wav` name** → still 192000 B raw | **flag-driven, name-blind** |
| `pw-record` | default → RIFF; `--raw` into `.raw` → 19200 B raw; `--container raw` **into a `.wav` name** → 19200 B raw; `--raw` into `.wav` → 19200 B raw | **flag-driven, name-blind** |
| `parec` | `--file-format=wav` into a **`.raw`** name → RIFF header (`riff=36`); `--raw` into a `.wav` name → raw | **flag-driven, name-blind** |

Harness warning for the author: the `.out` failure is *not* an ffmpeg gate — it
is the muxer-inference gate. Any ffmpeg leg whose output path lacks a known
extension fails with `EINVAL` **before** any capture happens (this cost me one
whole batch; the corrected batch is the one reported).

## 5. Bound semantics and flush granularity (the partial-write mechanism)

- **`arecord -d N` is exact** on both an unpaced device (`null`: 192000 B per
  second, 0.01 s wall) and hardware (192000 B in 1.036 s wall) — 44-byte header
  + N×48000×2×2 bytes.
- **`pw-record --sample-count N` is exact**: 4800 frames → 19200 B; 48000
  frames → 192000 B; header patched to the exact byte count on both the
  natural exit and TERM.
- **`parec` has no duration/byte bound** (no `-t`, no `-n` for samples — `-n`
  is `--client-name`). Its stdout is flushed in **64 KiB blocks**: TERM@0.5 s /
  1.0 s / 1.5 s → **0 bytes** (rc=0); TERM@2.0 s → **65536**; TERM@3.0 s →
  **262144** (=4×65536); KILL@1.2 s → 0; KILL@4 s → 393216 (=6×65536). A
  "captured bytes" verdict on a short `parec` leg is measuring the *flush
  boundary*, not the capture.
- **`ffmpeg` writes in 256 KiB blocks** (`runs/flush-series.txt`, sampled every
  0.25 s): `0,0,0,0,0,262144,262144,…,524288,524288` — nothing on disk before
  ≈1.4 s, then whole 262144-byte blocks. This is why KILL@1.2 s leaves a
  **0-byte** file while TERM@1.2 s leaves 297600 data bytes (256 KiB flushed +
  the remainder on graceful close).
- **`arecord -D null` without `-d`/`-d 0` is unbounded and splits**: 3 files of
  2147483692 B in 1.0 s (`/tmp/rtest/plain-01.wav`, `-02`, `-03`), i.e.
  ≈5.8 GB/s, split at the 0x80000000 placeholder. `-d 0` behaves the same
  (the `-01` split file receives the data; the *named* file stays absent/0 B).
  On the **hardware** device `-d 0`/no-`-d` is a normal paced unbounded capture
  (216140 B in 1.288 s). **Inference (medium):** the split/placeholder share the
  same 2 GiB constant; the null plugin's capture is unpaced.

## 6. Hazards created and cleaned (honest accounting)

- **My harness generated 91 GB of scratch.** The gates batch contained
  `arecord -D null` legs with no positive `-d`; they wrote 2 GiB split files
  (`sev1-arec-null-01.out` …, `cap-arec-d0-01.out` …) into
  `corpus/live/r76-scout/legs/` until I deleted the 48 split files
  (`rm -f legs/*-[0-9][0-9].wav legs/*-[0-9][0-9].out`; `du` 91G → 49M). A
  second runaway (an `arecord` I had failed to kill because `pgrep -f` matched
  its parent subshell) produced `wchan-test-01..30.wav`; killed and deleted.
  `/tmp/rtest` (5.8 GB) deleted. No file outside `corpus/live/r76-scout/` and
  `/tmp` was touched; repo disk is back to 24 MB of scratch.
- **Stray processes killed**: two `ffmpeg -f pulse` flush-series processes
  (pids 2630177, 2634536) and one `ffmpeg … flush-series.wav` (2643422) —
  all mine, all `kill -9`ed and verified gone. One **pre-existing** r70 orphan
  remains that is not mine and was not touched:
  `ffmpeg -loglevel quiet -nostdin -strict -2 -i /tmp/fifo-hold-r70-1ldgj_be/pair_dec_act.wav -f au -`
  (pid 2629126 at 17:34Z).
- **Guard for the boundary seat:** `timeout -s KILL` alone does **not** bound an
  `arecord -D null` leg — the flood is ~6 GB/s. Use `-d N`, or a size-capped
  scratch dir, or drop the null-device arm from unbounded cells.

## 7. Roundtrip cell (stretch) — measured, positive

`roundtrip.sh` + `roundtrip_analyze.py` → `runs/roundtrip-analysis.json`.
Player: `paplay corpus/artifacts/stem_sections.wav` (48 k mono, 4.000 s) into the
default sink, started 0.4 s after each capture began; capture window 5 s.

| capture | rc | duration | peak dBFS | centroid Hz | envelope (0.25 s RMS) |
|---|---|---|---|---|---|
| source member | — | 4.000 | −15.27 | 199.5 | 2090.9×8 → 2495.5×8 |
| `ffmpeg -f pulse -i <monitor>` | 0 | 5.019 | **−15.27** | 207.0 | 0 → 2098 → 2084 → … → 2500 → 1822 → 0 |
| `ffmpeg` (repeat) | 0 | 5.023 | −15.27 | 208.4 | same shape |
| `parec -d @DEFAULT_MONITOR@ --file-format=wav` (KILLed) | 137 | 4.096 | −15.27 | 208.4 | same shape |
| `pw-record --target <sink> -P stream.capture.sink=true` (KILLed) | 137 | 5.973 | −15.27 | 208.4 | same shape |

The captured bytes carry the source's **two-section structure** and its **exact
peak level**; only the centroid moves (+4.5 %, consistent with the mono→stereo
48 k float mix on the monitor path). So a captured copy lands in the **same
detect class** as its source member for level and section-contrast features, and
a **near-but-not-identical** class for centroid features. Two of the three
captures were SIGKILLed and are *unfinalized* — ffmpeg decoded them anyway,
stdlib `wave` would not (see §3).

## 8. Carried guards — status after this seat

| guard | status |
|---|---|
| reorder topology = fd1-OWNER's buffering mode | **new instance, capture direction**: parec's stdout flush is 64 KiB-granular; ffmpeg's file flush is 256 KiB-granular. A short capture leg measures the flush boundary, not the capture. |
| `timeout -s KILL` is the kill bound | **confirmed necessary but insufficient** for `arecord -D null` (§6) — the flood outruns the wall bound by ~6 GB/s. |
| `alive_after_term1` = ONE-TERM survival only | not contradicted: every capture consumer here died to TERM₁ (no immunity observed in the capture direction). |
| vacuous invariance from one identical-errored signature | **not incurred**: the four consumers carry four distinct signatures (rc 1 / 0 / 1 / 255) and four distinct header failure modes. |
| lavf wound partition 3-valued, gated on AVFMT_NOGENSEARCH | not exercised in the capture direction; ffmpeg capture adds a *different* partition — **buffer-granular wound** (0 B before the first 256 KiB flush, finalized after TERM). |
| rc alone is never a verdict | **confirmed ×4** (pw-record rc=1 on complete data; parec rc=0 with 0 B; arecord rc=1 with a finalized file; ffmpeg rc=255 with a valid file). |
| consumer forks are member-local | **confirmed in spirit, new axis**: the format choice is client-local (ffmpeg extension-driven vs the other three flag-driven) and the *default-device* resolution is client-local (implicit default fails, explicit token works). |
| bpy / io.DEFAULT_BUFFER_SIZE guards | not exercised (no Python consumer in this arm). |

## 9. Confidence and remaining unknowns

**High confidence** (process-level, reproducible, artifacts retained): the gate
table (§1); the exact byte counts and their caps (§2); the TERM/KILL header
partition and the parser-dependent usability table (§3); the format-axis
partition (§4); the flush granularities and the null-device flood (§5).

**Medium** (measured, mechanism inferred, no LSP device): why `pactl`'s Default
Source resolves for the explicit token but not for the implicit default of
`pw-record`/`parec`; why `arecord -D null` returns mostly-zero bytes with
sporadic non-zero residuals (uninitialized-buffer hypothesis, untraced); why
`pw-record` exits 1 on a clean bounded capture (no error text even under `-v`;
`stream set volume to 1.000 - success` is the last verbose line).

**Concurrent-seat context (affects wall-time confidence only):** sibling seats
were live during this window — `corpus/live/r76-boundary/out/loadcpu_ff-pulse_3.wav`
(a load-replay ffmpeg pulse leg, pid 2651317) and
`corpus/live/r76-baseline/measure-env/…` (ebur128, pid 2651872) were running
while later legs were measured. Byte counts, rc values and header fields are
device-driven and unaffected; **`wall_s` values may carry a load component** and
should be re-measured before being used as a verdict carrier.

**Not measured / open for the author or boundary seat**:
- The capture direction was probed with **one** real source (USB Line, currently
  silent — two independent bounded `pw-record` runs are byte-identical,
  sha `3ac1bdf363578593`) and **one** monitor (SPDIF). The Mic source and the
  other three monitors are unprobed.
- No fifo/writer-hold cells in the capture direction: whether `pw-record` keeps
  its r73/r74 `wait_for_partner` TERM-immunity when its *output* is a fifo is
  untested (its output is a file here).
- `parec --list-file-formats`, `pw-record --list-containers/--list-formats`,
  and the `-f pulse -sample_rate/-channels/-fragment_size` options are unprobed.
- `ffmpeg -f alsa -i null` is an **unstable** source: `-t 1` produced 1928910 B
  then 1509522 B; it emits `Non-monotonic DTS` and drops every frame on some
  runs, and its TERM was ignored for >2 s (both TERM legs ended as −9). Do not
  key a verdict on the null device's byte count or its TERM behaviour.
- The exact split threshold/placeholder coupling (0x80000000) is measured but not
  source-traced.

## 10. Evidence index (all under `corpus/live/r76-scout/`)

| artifact | sha256 (16) | content |
|---|---|---|
| `probe-pactl-sources.txt` | — | `pactl list sources short`, rc=0, 6 sources |
| `probe-pactl-info.txt` | — | `pactl info`, Default Source/Sink |
| `probe-pwlink.txt` | — | `pw-link -o/-i/-l` |
| `probe-arecord-devices.txt` | — | `arecord -l` (3 capture devices), `arecord -L` |
| `probe-ffmpeg-capture.txt` | — | ffmpeg version/config, `-devices`, `-formats`, `-h demuxer={pulse,alsa}` |
| `probe-versions-help.txt` | — | `pw-record --version/--help`, `parec --version/--help`, `arecord --version` |
| `capture_probe.py` | `9ff33f4eaa7c18bb` | harness (64 legs; TERM→KILL ladder + outer wall bound) |
| `runs/scout-capture-gates.json` | `0527866eb8e8834d` | 43 legs (first batch, ffmpeg `.out` muxer bug included and reported) |
| `runs/scout-capture-all.json` | `e143cf51f8c8ddaf` | **64 legs — the authoritative batch** |
| `runs/run-all.log` | — | one-line-per-leg summary (rc/wall/bytes/data-size) |
| `runs/flush-series.txt` | `48f715fce3adeec9` | ffmpeg 256 KiB flush time-series |
| `roundtrip.sh` | `12d1c37b2d41907a` | 4 roundtrip captures (3 consumers + repeat) |
| `roundtrip_analyze.py` | `7d7f3ea321507c84` | ffmpeg-decode analysis (envelope/centroid/peak) |
| `runs/roundtrip-analysis.json` | `00e0ecb82c22e9e4` | roundtrip numbers |
| `runs/roundtrip.log` | — | player/capture rc per roundtrip leg |
| `legs/` | — | 96 raw outputs (24 MB); split-flood files deleted (§6) |

**Seat stop.** Files written: this report + `corpus/live/r76-scout/**` only. No
fixture edit, no receipt mode, no `corpus/live/runs/*` receipt, no git mutation,
no subagents. HEAD `2250be9` unchanged. The author's `--probe-capture-r76` flag
does **not** exist in `corpus/fixtures/measure_audio.py` at this HEAD (verified
by reading the argparse block, `main()` at :2939) — the capture family is
entirely new work, and §1–§5 above are the gates it must respect.
