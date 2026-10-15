# R82 boundary — edge stress of the r82 scout claims

**Seat: BOUNDARY (executor-class, leaf).** Host `plazir27`, repo
`~/Projects/shokunin/audio-shokunin` @ HEAD **`b7d80d0`**. Window
**2026-10-15 ~15:46–16:06Z**. Toolchain: ffmpeg/ffprobe/ffplay **n9.0.1**
(libavformat 63.1.101, `--enable-libpulse`), PipeWire **1.6.8**,
`PulseAudio (on PipeWire 1.6.8)` protocol 35, 32 cores, loadavg 3.7–4.8 with
sibling seats live. Everything under `corpus/live/r82-boundary/`
(harness + `receipts/` + 4-figure `runs/**` + `manifest.json`, 803 files).
**No tracked-file edits, no commits, no `set-default-*`.** Seat names
`r82bnd_*`; the only module ever loaded was
`module-null-sink sink_name=r82bnd_ns`, unloaded strictly by the index
returned by `load-module` and re-verified against
`pactl list short modules` (`module-null-sink` + `sink_name=r82bnd_ns`)
before each `unload-module`.

The single `probeParent` labrat was dispatched once for a lavfi-only
option-law hypothesis; its substrate session exposed **no shell/exec tooling**,
so it returned UNSTABLE (untested) with zero evidence and zero side effects.
Every measurement below is seat-owned.

---

## 0. Verdict table

| # | scout claim | verdict | sharpest measured fact |
| --- | --- | --- | --- |
| 1 | playback never validates `-device` | **CONFIRMED for every non-empty string / FALSIFIED as a universal law** | 15/15 non-empty strings (bogus, source, `.monitor`, spaces, unicode, invalid-UTF-8, 512 chars, `@NOPE@`, newline, …) → rc=0 + silent fallback to SPDIF; **`-device ""` → rc=187** ×4, no node, no tone — `pa_context_get_sink_info_by_name failed` |
| 2 | capture EIO rc=251 in ~0.93 s | **rc CONFIRMED / timing FALSIFIED** | 30 EIO reps: **0.022–0.063 s** (quiet 0.024–0.029; 30 CPU hogs 0.038–0.063). `-i default` 11/11 EIO, no hang. Bonus: any unresolvable name **ending in `.monitor` succeeds** (rc=0, silent fallback to default-sink monitor) |
| 3 | post-`-i` indev options silently swallowed | **CONFIRMED + generalized** | swallowed: `-fragment_size -wallclock -stream_name -channels -sample_rate -buffer_size -server -prebuf -minreq -buffer_duration` (debug shows name matched at split, never applied). **Not** swallowed: `-frame_size N≥1` → SIGABRT (`ffmpeg_sched.c:1874`, N=1,1024,8192, also pure lavfi). Mirror: outdev options **before** `-i` hard-error rc=8 |
| 4 | sink-loss re-link ~0.2–0.3 s both directions | **CONFIRMED, tighter bound** | playback link → SPDIF **35–57 ms** after unload (6/6); capture → SPDIF.monitor **19–53 ms**, pump 24–46 ms (5/5); capture wav **63/63 tone windows at 0.1 s, zero missing** → no miss window ≥0.1 s |
| 5 | ffplay SDL-pulse ignores `PULSE_SINK` | **CONFIRMED** | 3/3 `SDL_AUDIODRIVER=pulseaudio PULSE_SINK=r82bnd_ns` legs: node `ffplay`, `client.api=pipewire-pulse`, `media.name="Audio Stream"`, `tlength=6144`, `target.object=SPDIF`, tone on SPDIF.monitor, ns-mon silent. Same-host control: `ffmpeg -f pulse` honors the same env (2/2 → ns) |
| 6 | `-sample_rate 12345` → silent clamp to 44100 | **CONFIRMED for 12345 / FALSIFIED as a fixed clamp** | ALSA `hw:0,0` pre-`-i`: 12345→44100, 8000→44100, 1→44100, 44100→44100, **96000→96000, 999999→192000** (nearest-supported negotiation). Pulse path: 12345→**12345**, no clamp. `rate 0`/`ch 0` → rc=222; `ch 99`/`rate 999999` → SIGABRT; ALSA `-channels 0` → rc=8 |

**Additional state correction (scout §5/§6, not in the 6 claims):** the ALSA
`default` PCM's **capture** direction is broken host-wide right now
(`ffmpeg` rc=251 *and* `arecord -D default` rc=1, same hw-params failure), and
`sysdefault` is **direct hw:0,0**, not pipewire-alsa. `aplay -D
default|pipewire|sysdefault` all rc=0. So the scout's "`-i pipewire` is an
ffmpeg-specific refusal" is falsified by the right control: `arecord -D pipewire`
fails identically — the asymmetry is **capture vs playback**, not ffmpeg vs others.

---

## 1. Claim 1 — playback targeting never validates

Legs: `runs/c1/*` (13), `runs/c1/empty_r{1,2,3}`, `runs/c1x/*` (5);
consolidated `receipts/c1.json` + `receipts/summary.json`. Each leg ran two
monitor witnesses (SPDIF.monitor + `r82bnd_ns.monitor`, `-t 3.6`) against a
2 s dual-tone player, with a mid-play pw-dump of the player's node and links.

| `-device` string | rc | linked to | tone witness |
| --- | --- | --- | --- |
| `r82bnd_ns` (control, clean single-instance re-run) | 0 | `r82bnd_ns` | ns-mon only |
| `no_such_sink_r82bnd` | 0 | SPDIF | SPDIF-mon |
| `r82bnd_ns.monitor` (a monitor) | 0 | SPDIF | SPDIF-mon |
| `alsa_input.…Line__source` (a source) | 0 | SPDIF | SPDIF-mon |
| `"   "` (3 spaces) | 0 | SPDIF | SPDIF-mon |
| `no such sink r82bnd` | 0 | SPDIF | SPDIF-mon |
| `r82bnd_🎵_sink` (unicode) | 0 | SPDIF | SPDIF-mon |
| `\xff\xfe` (invalid UTF-8 bytes) | 0 | SPDIF | SPDIF-mon |
| `x`×512 | 0 | SPDIF | SPDIF-mon |
| `default`, `@DEFAULT_MONITOR@`, `@DEFAULT_SOURCE@`, `@NOPE@`, `42`, `a\nb`, `" r82bnd_ns"` | 0 | SPDIF | SPDIF-mon |
| **`""` (empty)** | **187** | **no node ever** | **none anywhere** |

`target.object` always published the literal requested string (checked by
pw-dump on the player's client id); stderr for every rc=0 leg is just
`[aist#0:0/pcm_s16le …] Guessed Channel Layout: stereo` — zero warning at
`-loglevel warning`. The fallback is WirePlumber resolution, not ffmpeg.

**Bimodal cell — verbatim.** `-device ""` (4/4 reps, wall ≈1.06 s,
`runs/c1/empty/stderr.txt`, addresses vary per run):

```
[aist#0:0/pcm_s16le @ 0x55e23add7180] Guessed Channel Layout: stereo
[PulseAudio outdev @ 0x55e23ae29480] pa_context_get_sink_info_by_name failed.
[PulseAudio outdev @ 0x55e23ae29480] Updating sink info failed.
[out#0/pulse @ 0x55e23ae290c0] Could not write header (incorrect codec parameters ?): Generic error in an external library
[af#0:0 @ 0x55e23ae2a000] Error sending frames to consumers: Generic error in an external library
[af#0:0 @ 0x55e23ae2a000] Task finished with error code: -542398533 (Generic error in an external library)
[af#0:0 @ 0x55e23ae2a000] Terminating thread with return code -542398533 (Generic error in an external library)
[out#0/pulse @ 0x55e23ae290c0] Nothing was written into output file, because at least one of its streams received no packets.
```

So: the law is **"every non-empty string is unvalidated; the empty string
aborts at sink-info lookup"**, and rc **187 is a class with ≥2 mechanisms**
(bad server "Access denied" per scout, and this sink-info failure). The author
must not pin "playback never validates" without the empty-string carve-out.

## 2. Claim 2 — capture EIO bound and `-i default`

Legs: `runs/c2/*` (25), `runs/c2x/*` (load reps, monitor-resolution probes,
ALSA/arecord/aplay cells, held-Line reps); `receipts/c2.json`.

**rc class CONFIRMED, timing FALSIFIED at this state.**

| shape | n | rc | wall (s) |
| --- | --- | --- | --- |
| `-i r82bnd_ns` (bare sink) quiet | 5 | 251 | 0.027 ×5 |
| `-i no_such_source_r82bnd` quiet | 5 | 251 | 0.024–0.029 |
| `-i default` quiet | 6 | 251 | 0.027–0.028 |
| same three shapes, 30 CPU hogs (33 runnable/32 cores) | 15 | 251 | 0.038–0.063 |
| `-i default` while Line held by `parec` | 2 | 251 | 0.025–0.027 |
| quiet re-check after load | 2 | 251 | 0.027 |
| `-f alsa -i hw:0,0` while `arecord` holds it | 2 | 251 | 0.022–0.023 |

Verbatim (`runs/c2/sink_bare_r0/stderr.txt`):

```
[in#0 @ 0x563003be5940] Error opening input: Input/output error
Error opening input file r82bnd_ns.
Error opening input files: Input/output error
```

**30/30 reps between 0.022 s and 0.063 s.** The scout's "~0.93 s" is not
reproduced under quiet *or* saturated CPU; `-i default` is deterministic EIO
(11/11), no hang, and the held-Line control shows it is name resolution, not
busy state. The rc=251 EIO class is safe to pin; **do not pin 0.93 s**.

**New edge the scout missed (capture-side silent fallback).** Names that do not
resolve but **end in `.monitor`** do NOT EIO — they open rc=0 and re-route to
the **default sink's monitor** (`runs/c2x/monres_*`):

```
no_such_sink_r82bnd.monitor   → rc=0  target.object=no_such_sink_r82bnd   stream.capture.sink=true
no_such_source_r82bnd.monitor → rc=0  target.object=no_such_source_r82bnd
r82bnd_ns.monitor.monitor     → rc=0  target.object=r82bnd_ns.monitor
links (all three): alsa_output.…SPDIF__sink:monitor_FL -> r82bnd_monq:input_FL
                   alsa_output.…SPDIF__sink:monitor_FR -> r82bnd_monq:input_FR
```

This is exactly the falsifier the scout listed as #3 ("a bogus `-i` leg
returning rc=0 with a linked node") — it exists, gated on the `.monitor`
suffix. Correct law: **bare unresolvable name → 251 EIO; `.monitor`-suffixed
unresolvable name → rc=0 + default-sink-monitor fallback.**

## 3. Claim 3 — option position law

Legs: `runs/c3/*` (24) + `runs/c3x/*` (4); `receipts/c3.json`.

| leg | rc | capture node props / wav |
| --- | --- | --- |
| `-f pulse -fragment_size 2048 -i M` (pre) | 0 | fragsize **2048**, latency 512/48000 |
| `-f pulse -stream_name PREBND -i M` | 0 | media.name **PREBND** |
| `-f pulse -channels 1 -sample_rate 44100 -i M` | 0 | wav **44100×1**, latency 2205/44100 |
| `-f pulse -i M -fragment_size 2048` (post) | 0 | fragsize 9600, latency 2400/48000 — unchanged, **no warning** |
| `… -i M -wallclock 0` / `-stream_name POSTBND` / `-channels 1 -sample_rate 44100` / `-buffer_size 16384` / `-server unix:/nonexistent` / `-prebuf 8192 -minreq 512 -buffer_duration 500` | 0 | all unchanged, silent |
| `-f pulse -buffer_size 16384 -i M` (outdev opt, input position) | **8** | `Option buffer_size not found.` |
| `-f pulse -i M -frame_size {1,1024,8192}` | **-6** | SIGABRT (3/3 values) |
| `-f pulse -frame_size 8192 -i M` (pre) | 0 | rc=0, deprecation text, fragsize 9600 |
| `-f pulse -i M -ac 1` / `-ar 44100` (proper output opts) | 0 | wav **48000×1** / **44100×2** — they DO land |

Verbatim SIGABRT (`runs/c3/post_frame_size_1/stderr.txt`):

```
[aist#0:0/pcm_s16le @ 0x55a26bc44b00] Guessed Channel Layout: stereo
Assertion enc->sq_idx[0] >= 0 failed at fftools/ffmpeg_sched.c:1874
```

The same assert reproduces with **`-f lavfi -i anullsrc … -frame_size 1024`**
(`runs/c3/lavfi_post_frame_size`) — so it is the *output encoder* option, not a
pulse quirk, and it is **value-independent for N≥1** (scout pinned only 8192).

Verbatim mechanism (`runs/c3x/post_frag_debug/stderr.txt`, `-loglevel debug`):

```
Reading option '-fragment_size' ... matched as AVOption 'fragment_size' with argument '2048'.
...
Parsing a group of options: output url …/out.wav.
Applying option t (stop transcoding after specified duration) with argument 1.2.
Applying option c:a (select encoder/decoder ('copy' to copy stream without reencoding)) with argument pcm_s16le.
Successfully parsed a group of options.
```

`fragment_size` is matched globally at split time (hence accepted) and then
**never applied** to any group. The general law: name validity is global;
applicability is per-group; a name unknown to the group is silently dropped in
*output* position but hard-errors (`rc=8`, `Option X not found.`) in *input*
position; a name that does map to the output encoder is applied — which is why
`-frame_size` aborts. "ALL post-`-i` options are swallowed" is **false**.

## 4. Claim 4 — re-link timing and miss windows

Legs: `runs/c4/*` (6 playback + 5 capture, half under 8 CPU hogs);
`receipts/c4.json`. Poller: `pw-dump` every ~35 ms, links keyed to the player
(`r82bnd_lossplay`), pump (`r82bnd_losspump`), capture (`r82bnd_losscap`).

**Playback** (unload by verified index at t≈2.00 s of a 6 s tone):

| rep | unload t | link → SPDIF | Δ |
| --- | --- | --- | --- |
| r0–r2 quiet | 2.001–2.003 | 2.036–2.043 | **0.035–0.041 s** |
| r3–r5, 8 hogs | 2.001–2.002 | 2.052–2.058 | **0.050–0.057 s** |

rc=0 all 6. SPDIF witness tone is continuous from the switch; re-analysis at
**0.1 s** windows: first tone window at witness 2.3 s (= player 2.0–2.1),
no missing windows afterwards. In 2/6 reps the poller caught an intermediate
peerless state (2.008/2.011 → 2.058/2.057), i.e. a link gap bounded by the
~50 ms poll resolution; no audio gap ≥0.1 s.

**Capture** (pump feeding `r82bnd_ns`, capture from `r82bnd_ns.monitor`,
unload at t≈2.00 s):

| rep | capture → SPDIF.monitor | pump → SPDIF | tone windows (0.1 s) |
| --- | --- | --- | --- |
| r0–r4 | 2.021–2.056 (Δ 0.019–0.053) | 2.026–2.048 (Δ 0.024–0.046) | **63/63, zero missing** |

So: both directions re-link in **≤60 ms**, capture re-link to `.monitor` always
succeeded (5/5), and there is **no miss window ≥0.1 s**. The scout's 0.22–0.27 s
is a safe upper bound; the boundary bound is tighter.

## 5. Claim 5 — ffplay SDL-pulse ignores `PULSE_SINK`

Legs: `runs/c5/*` + `runs/c5/ffmpeg_env_sink_r*`; `receipts/c5.json`.

```
SDL_AUDIODRIVER=pulseaudio PULSE_SINK=r82bnd_ns ffplay -nodisp -autoexit tone2.wav
node: name=ffplay media.name="Audio Stream" client.api=pipewire-pulse
      target.object=alsa_output.…SPDIF__sink  node.latency=512/48000  tlength=6144
links: ffplay:output_FL/FR -> …SPDIF__sink:playback_FL/FR
witness: def-mon 5 tone windows, ns-mon 0        (3/3 reps, rc=0)
```

Controls on the same host/session: without `PULSE_SINK` → SPDIF (2/2);
native SDL (no driver override) → SPDIF (1/1); **`PULSE_SINK=r82bnd_ns
ffmpeg -f pulse` → `target.object=r82bnd_ns`, tone into ns (2/2)**. CONFIRMED —
the env is honored by libavdevice and ignored by SDL's pulse backend.

## 6. Claim 6 — clamp and typed rc map

Legs: `runs/c6/*` (16) + `runs/c6x/*` (12); `receipts/c6.json`.

ALSA `hw:0,0`, **pre-`-i`** `-sample_rate V` (correct indev position):

| V | rc | wav rate | note |
| --- | --- | --- | --- |
| 12345 | 0 | **44100** | scout's cell, ×4 incl. verbose |
| 8000 / 1 | 0 | 44100 | clamped **up** |
| 44100 | 0 | 44100 | |
| 96000 | 0 | 96000 | no clamp |
| 999999 | 0 | **192000** | clamped to device max, **not** 44100 |
| 0 / -1 | **222** | — | `Value … for parameter 'sample_rate' out of range [1 - 2.14748e+09]` |

Post-`-i` `-sample_rate 12345` → wav **48000** (silently dropped, §3 law).
Pulse path pre-`-i` `-sample_rate 12345` → wav **12345** (no clamp at all) —
so "silent clamp to 44100" is an ALSA device-negotiation artifact, not a
universal law. The scout's §5 table row shows the post-`-i` shape
(`-i hw:0,0 -sample_rate 12345`) but their receipt command
(`runs/ext/x6_alsa_nego/r0/cmd.txt`) is pre-`-i`; the table shape is miscited.

Typed rc map (all reproduced, verbatim first lines):

```
pulse -sample_rate 0   → 222  Value 0.000000 for parameter 'sample_rate' out of range [1 - 2.14748e+09]
pulse -channels 0      → 222  Value 0.000000 for parameter 'channels' out of range [1 - 2.14748e+09]
pulse -fragment_size -2→ 222  Value -2.000000 for parameter 'fragment_size' out of range [-1 - 2.14748e+09]
pulse -channels 99     → -6   Assertion 'pa_channels_valid(channels)' failed at ../pulseaudio/src/pulse/channelmap.c:400, function pa_channel_map_init_extend(). Aborting.
pulse -sample_rate 999999 → -6 Assertion 'pa_sample_spec_valid(spec)' failed at ../pulseaudio/src/pulse/sample.c:67, function pa_frame_size(). Aborting.
alsa  -channels 0 (pre-i) → 8  Option channels not found.        (ALSA indev has ch_layout, not channels)
alsa  -ch_layout mono     → 251 cannot set channel count to 1 (Invalid argument)
```

## 7. ALSA-surface drift vs the scout (extra, not in the 6 claims)

- `-f alsa -i default` → **251** `cannot set parameters (No such file or
  directory)` in 0.028 s; **`arecord -D default` fails identically**
  (`arecord: set_params:1462: Unable to install hw params: ACCESS: RW_INTERLEAVED`).
  → the pipewire-alsa PCM's **capture** direction is currently broken
  host-wide, not an ffmpeg refusal. Scout measured rc=0 for this leg.
- `-f alsa -i sysdefault` → rc=0, but it is **direct hw:0,0**, not
  pipewire-alsa: `arecord -D sysdefault --dump-hw-params` prints
  `ACCESS: MMAP_INTERLEAVED … RW_INTERLEAVED`, and while it holds the device
  `ffmpeg -f alsa -i hw:0,0` → `cannot open audio device hw:0,0 (Device or
  resource busy)` rc=251. No PipeWire node appears during a sysdefault capture.
- `aplay -D default|pipewire|sysdefault` → all rc=0 (~0.3 s).
  `arecord -D pipewire` → rc=1, same hw-params failure as ffmpeg.
  → the scout's "aplay works, so ffmpeg's refusal is ffmpeg-specific" uses the
  wrong control; the split is **playback OK / capture broken**, not client-specific.

---

## I. Harness incident (disclosed, resolved)

First-pass `ensure_ns()` tested `"r82bnd_ns.monitor" in pactl list short sinks`
— monitors are *sources*, so the test was always false and **every** stage call
loaded a fresh null sink; 7 duplicate `r82bnd_ns` modules accumulated. The first
c4 pass was therefore invalid (the player linked to a different same-named sink
than the one unloaded → "no re-link" artifact) and its files were **overwritten**
by the corrected re-run at the same paths. All 7 duplicates were then removed by
**verified index** (row must contain `module-null-sink` + `sink_name=r82bnd_ns`),
`pactl list short sinks|modules | grep r82bnd` empty; the harness now matches an
exact sink row (`^\d+\tr82bnd_ns\t`) and refuses on duplicates. c4, c5, c6 and
all follow-up legs ran single-instance. `c1/valid_ns` was re-run clean as
`c1x/valid_ns_r0` (same result).

## II. Contention ledger

- Default sink/source unchanged across the whole window: SPDIF / Line
  (setup + teardown receipts). No `set-default-*` issued.
- Foreign live objects observed, never touched: `r78lat_at_default_sink_tap`
  (pw-record on SPDIF.monitor) + `r78lat_at_default_sink` (pw-play into
  `@DEFAULT_SINK@`) during c1–c2; `r79lb_7655_b01_sink_prop_tap` (pw-record
  from `r79lb_ns_b_7655`) during c4. The r78 tone file was classified
  read-only against my frequencies: magnitude ≤1 LSB at 440/500/1k/1.2k/1.5k/
  1.8k/3k vs ~4000 in-window for my own tone → no witness false positives.
- Interference caused by this seat: bounded tones on the real SPDIF sink during
  c1 bogus legs (≤2 s ×15), c4 re-link legs (≤4 s ×11, that is the
  measurement), c5 ffplay legs (≤2 s ×6). `PULSE_SINK`/`SDL_AUDIODRIVER` were
  per-process env only. `-f alsa -i hw:0,0` legs briefly held the USB card's
  capture subdevice (1 s each); the busy-test holder was 3 s and reaped.
  No foreign module/node/stream was unloaded, moved, suspended or re-volumed.

## III. Cleanup

At exit: no `r82bnd_*` sink, source, node, module or process remains
(`pactl list short sinks|modules | grep r82bnd` empty; teardown receipt
`unload.ok=true, sink_gone=true`; `stray_killed=[]`).

## IV. Receipts index (sha256 prefix)

| artifact | sha16 |
| --- | --- |
| `r82bnd_probe.py` | `25a1a5f86c21c986` |
| `receipts/setup.json` | `0424602424899216` |
| `receipts/c1.json` (13 legs) | `33ca97a5831b9cc8` |
| `receipts/c2.json` (25 legs) | `9e04ca364a98a126` |
| `receipts/c3.json` (24 legs) | `910def3a5c9db666` |
| `receipts/c4.json` (11 legs) | `92695e375fa42e7b` |
| `receipts/c5.json` (6 legs) | `9896e3779cbfaebf` |
| `receipts/c6.json` (16 legs) | `4d598bc19615032d` |
| `receipts/summary.json` (per-leg roll-up) | `e069fb4bb4431258` |
| `receipts/teardown.json` | `834128007069fd83` |
| `manifest.json` (803 files) | `e239ef14e452bb69`¹ |

¹ The manifest embeds its generation timestamp, so its own sha changes on every
regeneration; all per-file shas inside it are stable. The index was regenerated
after the final teardown (803 files, zero `r82bnd_*` entries).

Follow-up legs without a consolidated stage json live as per-leg receipts under
`runs/c1x/`, `runs/c2x/`, `runs/c3x/`, `runs/c6x/` (each with
`cmd.txt`/`stderr.txt`/`meta.json`); all are covered by `manifest.json`.

## V. What the author may safely pin (and must not)

- Pin **non-empty `-device` → rc=0 + silent default-sink fallback**, with
  `target.object` = literal string; pin the **empty-string carve-out** rc=187
  with its distinct stderr. Do not pin "never validates" universally.
- Pin **capture 251/EIO for bare unresolvable names** but not the 0.93 s
  timing; pin the **`.monitor` suffix fallback** (rc=0 → default sink monitor).
- Pin the **position law** with its two exceptions (`-frame_size` aborts for any
  N≥1; outdev options in input position error rc=8) and the debug evidence.
- Pin **re-link ≤60 ms both directions** and capture **no gap ≥0.1 s**.
- Pin **SDL-pulse ignores PULSE_SINK** with the libavdevice control.
- Pin the **rate negotiation map** (not a constant 44100) and the rc classes
  with their exact signatures; pin ALSA `-channels` → rc=8 (option absent) as
  distinct from pulse `-channels 0` → 222.

Seat stop. No commits, no tracked writes, no scope widening.
