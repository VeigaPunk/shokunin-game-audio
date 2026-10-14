# R78 AUTHOR (audio) — the playback-direction lattice

Round: 78. Wave: `shokunin-train-20261101-w19`. Repo
`~/Projects/shokunin/audio-shokunin` @ HEAD `bdf748e` (base for the diff:
`bdf748e:corpus/fixtures/measure_audio.py`; a sibling r77 seat edited the
same file mid-round — its `_capture_r77_node_props` client-id→PID resolution
is preserved verbatim).

**Seat: AUTHOR. Tracked edits: exactly one file —
`corpus/fixtures/measure_audio.py` (+2401 / −3).** The three rewritten
lines are the prepend-only wiring the r77 fold used: the one-mode
exclusivity sum, the `mode` ternary, the `suffix` ternary — every prior
flag's value unchanged. Everything else is new symbols plus one new
`--probe-capture-r78` flag. Receipt under
`corpus/live/runs/20261014T221945369366Z-capture-r78/measurements.json`
(all rows pass, `failures: {}`). **No commit.**

Toolchain (this host, this session): PipeWire **1.6.8**, pacat/pactl
**17.0-98-gb096**, alsa-utils **1.2.16**, Python **3.14.7**, Linux
**7.2.3-arch1-3**. Host `plazir27`, session default sink
`…HiFi__SPDIF__sink`, default source `…DualSense…Direct__source`
(DualSense, the r78-stable change the brief warned about).
`host_is_quiet=false` on the final pass — one foreign `aplay -D null`
plus concurrent r79/r78-boundary lanes were live throughout; every probe
node name is PID-stamped (`r78_*_844895`) and topology is matched by
exact name, never by application name.

---

## Declared move

`--probe-capture-r78`: eight entries over the write-side frontier the
r77 fold left open — the playback `--target` fallback lattice (14 legs,
two witnesses each), live-default following through `pw-metadata` vs
`pactl`, mid-play target loss, `target.object`/`node.target`/
`PIPEWIRE_PROPS` precedence (14 legs), bogus `media.class` SIGSEGV, the
`aplay` device axis (18 legs), and the two remaining capture-side rows:
directional link-loss and `parec --fix-*` header honesty.

**Three corrections to the scout's pre-measurement**, all recorded with
mechanism:

1. `.monitor` is **not** a clean default fallback — it is a *racy*
   source-domain resolution (§1.4).
2. `pactl set-default-sink` is **stale, not merely delayed** — rc=0, the
   session metadata does not move within 5.6 s of polling (§2.2).
3. An **active** fallback stream **follows** a mid-play default move —
   the session manager re-links it (~1 s); it is not pinned at
   spawn-time (§2.3).

---

## 0. Headline

| # | frontier | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | `--target` lattice | **LAW CONFIRMED, 13/14 legs** | every unresolvable form — garbage, absent name, `default`, `pulse`, `@DEFAULT_SINK@`, `@DEFAULT_MONITOR@`, `@DEFAULT_SOURCE@`, a *source* name, empty, absent — lands the session default `[…SPDIF__sink]`, rc=0, empty stderr, real-time wall, tag tone on the default's monitor tap |
| 1b | `.monitor` | **RACY — named class** | resolves through the source domain to *either* the default sink *or* the default source's peer sink (DualSense `…Direct__sink`), both observed across runs, with a mid-leg re-link on the peer path → `monitor_target_source_peer` |
| 1c | `--target 0` | **STALL, not fallback** | publishes an *unlinked*, suspended stream — zero consumers ever; bounded then killed (rc=−9); tone never reaches the default. `--target 0` is `unlinked_stall`, not fallback |
| 2 | live default | **FOLLOW MEASURED, BOTH VERBS** | `pw-metadata` applies in 0.0 s — new spawns land the new default immediately; `pactl set-default-sink` rc=0 moves nothing for ≥5.6 s → `pactl_stale_default`; an **active** fallback stream re-links to the new default within ~1 s of the write → `followed_move` |
| 3 | mid-play target loss | **RE-LINK vs SUSTAINED-UNLINK, rc=0 both** | `pactl unload-module` mid-play → silent re-link to the session default, playout to EOF at real-time rate (`playback_relink_on_target_loss`); `pw-link -d` → *no* re-link, consumers `[]` for the rest of the file, rc=0, wall = duration (`unlinked_sustained_playout`) |
| 4 | props precedence | **`-P` > `--target`, both directions** | `-P target.object=B --target A` → consumers `[B]`; the mirror lands `[A]`; `node.target=` routes identically; `PIPEWIRE_PROPS` is a second, independent vector; `media.role`/`stream.capture.*`/monitor props are decoration; `node.autoconnect=false` and `media.class=Audio/Source` publish unlinked → bounded `-9` stalls |
| 5 | `media.class` crash | **REPRODUCIBLE SIGSEGV, named** | `Audio/Sink`, `Stream/Input/Audio`, `Audio/Duplex`, `Audio/Bogus` → rc=−11 each, empty stderr, ~2.01 s wall, no node ever published → `class_override_segv`; `Stream/Output/Audio` control rc=0; `Audio/Source` boundary = stall, not crash |
| 6 | `aplay` axis | **EBUSY + retention bracket + asymmetry** | `aplay -D hw:0,0` under a monitor witness → rc=1 `alsa_busy`; the lock outlives the holder by ~5.9 s (+1 s still `alsa_busy`, +7 s free); `aplay` **converts** (`-f FLOAT_LE` rc=0, "format is changed to S16_LE") where `arecord` **constrains** (`alsa_sample_format` listing `S16_LE`,`S24_3LE`); `pulse` → `alsa_unknown_pcm`; `default`/`pipewire` plugins rc=0 |
| 7 | capture link loss | **DIRECTION SPLITS THE CLASS** | cutting the capture's *own input* links freezes file growth at 311 340 B → `unlinked_stall`; cutting the *producer* links keeps the stream running — file grows to full bound while 33/50 windows are digital zero from the unlink point → `unlinked_sustained_zeros` |
| 8 | `parec --fix-*` | **HEADER LIES, PAYLOAD TELLS** | `--fix-rate`: header advertises the requested 22050 Hz while payload runs source 48000 → `header_prefix_mismatch`; same for `--fix-format` (header 16-bit / payload float32) and `--fix-channels` (header 1ch / payload 2ch); the no-fix control is `header_honest`; WAV legs need a seekable fd — on a pipe parec fails `Failed to open audio file.` |

---

## 1. FRONTIER 1 — the `--target` fallback lattice (14 legs)

`pw-play --target T` on a 48 kHz stereo discriminator tone (left 1 kHz,
right 1.5 kHz, ≈8192 amplitude), serialized, per-leg `pw-link -l`
consumer differencing plus a monitor-tap FFT witness on the expected
sink.

| leg | `--target` | rc | consumers | tone on expected |
| --- | --- | --- | --- | --- |
| `probe_sink` | `r78_play_sink_844895` | 0 | `[r78_play_sink_844895]` | yes |
| `other_sink` | hdmi sink | 0 | `[…hdmi-stereo]` | yes |
| `garbage` | `no_such_sink_r78` | 0 | `[…SPDIF__sink]` | yes |
| `absent_sink` | unloaded probe sink name | 0 | `[…SPDIF__sink]` | yes |
| `default_token` | `default` | 0 | `[…SPDIF__sink]` | yes |
| `pulse_token` | `pulse` | 0 | `[…SPDIF__sink]` | yes |
| `at_default_sink` | `@DEFAULT_SINK@` | 0 | `[…SPDIF__sink]` | yes |
| `at_default_monitor` | `@DEFAULT_MONITOR@` | 0 | `[…SPDIF__sink]` | yes |
| `at_default_source` | `@DEFAULT_SOURCE@` | 0 | `[…SPDIF__sink]` | yes |
| `source_name` | DualSense *source* | 0 | `[…SPDIF__sink]` | yes |
| `monitor_name` | `<source>.monitor` | 0 | `{SPDIF, DualSense-peer}` | yes (default leg) |
| `empty_target` | `""` | 0 | `[…SPDIF__sink]` | yes |
| `no_target` | *(flag absent)* | 0 | `[…SPDIF__sink]` | yes |
| `target_0` | `0` | −9 (bound) | `[]` | — |

**The law.** A resolvable *sink* name is honored — including a foreign
one (hdmi). Every name that fails to resolve as a playback-capable sink,
plus the meta-tokens, plus a *source* name, silently falls back to the
**current session default**: identical rc=0, empty stderr, real-time
wall, and the tag tone measured on the default's monitor tap. Intent
(`target.object` on the stream node) and consumption (`pw-link -l`
consumers) are recorded separately — the stream still advertises the
requested name while its ports are fed by the default.

### 1.4 `.monitor` is racy, not a fallback — `monitor_target_source_peer`

A `<name>.monitor` target resolves through the **source domain**: the
probe finds the default source's `api.alsa.path` peer sink (the
DualSense `…Direct__sink` here). Across runs on this host the leg landed
**both** outcomes — run 2 consumed the DualSense peer first, then
re-linked to SPDIF mid-leg; run 4 consumed SPDIF directly. The verdict
accepts exactly `{default, source-peer}` as the consumer set and nothing
else — a stall or a third node is a failure — and records
`landed_peer`. When the union includes the default, its tap must carry
the tag tone (measured: `mine_spans` from 0.5 s).

### 1.5 `--target 0` is a published stall — `unlinked_stall`

The literal `0` publishes a stream node that **never links**: zero
consumers at every sample, process suspended, killed at the 6 s bound
(rc=−9), and the default's tap carries no tag tone. It is classified
with the same `unlinked_stall` family as `node.autoconnect=false` —
publishing is not routing.

---

## 2. FRONTIER 2 — live-default following, both verbs

### 2.1 `pw-metadata` is the authoritative switch — 0.0 s apply

`pw-metadata -n default 0 default.audio.sink '{"name":"r78_def_sink_844895"}'`
applies within the same poll (0.0 s). The `before` leg consumed SPDIF,
`moved` and `still_probe` consumed the probe null sink — **new spawns
follow the live default**, and the restore leg re-landed SPDIF after the
metadata was written back unconditionally in `finally`.

### 2.2 `pactl set-default-sink` is stale — `pactl_stale_default`

rc=0, then **11 consecutive 0.5 s polls** (5.6 s) show the session
metadata *and* `pactl info` both still naming `r78_def_sink_844895` —
`moved_at_s: null`. On an earlier development run the write appeared to
land ~3.5 s late, so the harness carries both named classes
(`pactl_delayed_default` remains admissible); on the measured receipt
the class is `pactl_stale_default`. Either way the pin is behavioral:
rc=0 while the routing authority (the metadata key) does not change
inside the poll window. `pw-metadata`, not `pactl`, is the reliable
switch on this host.

### 2.3 An *active* fallback stream follows the move — `followed_move`

The `nofollow` leg spawned on the probe default (`[r78_def_sink_844895]`
at +1.0 s), the metadata was restored to SPDIF at +1.6 s mid-play, and
the stream's consumers were `[…SPDIF__sink]` at +2.6 s and +4.0 s —
the session manager re-linked the running stream to the new default
within ~1 s. The scout's record showed only new-spawn following; the
measured law is stronger for *fallback* streams: `followed_move=true`,
`pinned=false`. The harness admits either pin-or-follow (`post ⊆
{spawn, restore}`) and records which — a third node eating the stream is
the failure, not either law.

---

## 3. FRONTIER 3 — mid-play target loss

One probe-owned `module-null-sink` (`r78_loss_sink_844895`) as the
explicit honored target, a 6 s real-time file:

| leg | event at ~1.5 s | consumers after | rc | wall |
| --- | --- | --- | --- | --- |
| `unload_relink` | `pactl unload-module` | `[…SPDIF__sink]` @3.0 s, 5.0 s | 0 | 6.03 |
| `manual_unlink` | `pw-link -d` on the stream's edges | `[]` @3.0 s, 5.0 s | 0 | 6.03 |

Destroying the target sink triggers `playback_relink_on_target_loss`:
the stream silently re-links to the session default and plays to EOF.
Manually disconnecting the same stream leaves it `unlinked_sustained_playout`:
no re-link, no error, the file consumed at exactly real-time rate into
nowhere — a player reports success while emitting nothing.

---

## 4. FRONTIER 4 — property precedence (14 legs)

| leg | routing | consumers |
| --- | --- | --- |
| `flag_a_prop_b` | `--target A` + `-P target.object=B` | `[B]` |
| `flag_b_prop_a` | `--target B` + `-P target.object=A` | `[A]` |
| `prop_only` | `-P target.object=A` alone | `[A]` |
| `node_target` | `-P node.target=A` | `[A]` |
| `flag_garbage_prop_b` | `--target garbage` + `-P target.object=B` | `[B]` |
| `prop_garbage` | `-P target.object=garbage` | `[SPDIF]` (fallback) |
| `node_target_garbage` | `-P node.target=garbage` | `[SPDIF]` (fallback) |
| `env_props_flag_a` | `PIPEWIRE_PROPS=target.object=B` + `--target A` | `[B]` |
| `env_props_flag_garbage` | `PIPEWIRE_PROPS=target.object=B` + `--target garbage` | `[B]` |
| `role_decoration` | `-P media.role=…` + `-P target.object=A` | `[A]` |
| `capture_prop_decoration` | `-P stream.capture.sink=true` + `-P target.object=A` | `[A]` |
| `monitor_prop_decoration` | monitor-prop variant | `[A]` |
| `autoconnect_false` | `-P node.autoconnect=false` | `[]` — killed at bound |
| `class_source_stall` | `-P media.class=Audio/Source` | `[]` — killed at bound |

**`-P target.object` beats `--target` in both directions**, `node.target`
routes equivalently, and `PIPEWIRE_PROPS` is a fully independent second
vector (it also beats `--target`). The decoration legs pin the negative
space: role/capture/monitor properties change nothing about routing —
the stream lands exactly where `target.object` says.

---

## 5. FRONTIER 5 — `media.class` override → `class_override_segv`

| leg | `media.class` | rc | wall | stderr | node published |
| --- | --- | --- | --- | --- | --- |
| `segv_sink` | `Audio/Sink` | −11 | 2.01 | (empty) | none |
| `segv_audio` | `Stream/Input/Audio` | −11 | 2.02 | (empty) | none |
| `segv_duplex` | `Audio/Duplex` | −11 | 2.01 | (empty) | none |
| `segv_bogus` | `Audio/Bogus` | −11 | 2.01 | (empty) | none |
| `control_output` | `Stream/Output/Audio` | 0 | 1.63 | (empty) | normal playout |
| `boundary_source` | `Audio/Source` | −9 (bound) | 6.0 | (empty) | published, unlinked |

Four of five invalid classes reproduce SIGSEGV deterministically (the
mechanism is a `pw-play` client crash, not a server refusal — the node
never appears). The `Audio/Source` boundary is *not* a crash: the
stream publishes with an inapplicable class and sits unlinked — the same
stall family as `target_0`. The class row is `class_override_segv` with
the boundary leg recorded separately.

---

## 6. FRONTIER 6 — the `aplay` device axis (18 legs)

All `hw:` legs are **observer-sensitive by construction** — a monitor
witness holds the PCM during the busy legs, so `alsa_busy` is a
contention verdict, not a physical-output claim:

- **EBUSY under witness**: `aplay -D hw:0,0` while the witness holds the
  PCM → rc=1, `alsa_busy` ("Device or resource busy").
- **Lock retention ~5.9 s**: measured `witness_lock_release_s`, then the
  bracket — `retention_1s` still `alsa_busy`, `retention_7s` rc=0 →
  `alsa_lock_retention` {+1 s busy, +7 s free}.
- **Convert vs constrain**: `aplay -f FLOAT_LE` → rc=0 with
  `Warning: format is changed to S16_LE`; `arecord` on the same device →
  rc=1 `alsa_sample_format` listing exactly `S16_LE`,`S24_3LE` —
  `aplay_converts_arecord_constrains`.
- **Envelope**: `params_play` rc=0, `params_cap` rc=1 (this USB device
  is playback-only on `hw:0,0`); `hw_baseline` plays the s16 tag tone
  rc=0.
- **Plugin split**: `default` and `pipewire` plugins rc=0 (routed
  through PipeWire); `pulse` → rc=1 `alsa_unknown_pcm`; `null` accepts
  and drains unpaced (rc=0, ~0 s wall — no clock).
- `refuse_bogus` (illegal `-f`) → rc=1 `aplay_bad_format`.

---

## 7. FRONTIER 7 — capture link loss: direction decides

`pw-record` on a probe null sink's monitor, tone fed by a `pw-play`
producer, `pw-link -d` applied to one edge set mid-run, then re-linked:

| leg | edges cut | file growth during unlink | content |
| --- | --- | --- | --- |
| `consumer_unlink` | stream `input_*` ← sink `monitor_*` | **frozen**: 311 340 B flat across 3 samples, resumes after re-link | 69/70 windows carry the tone — **no zeros recorded** |
| `producer_unlink` | feed `output_*` → sink `playback_*` | **continues**: 593 964 → 880 684 B to full bound | 33/50 windows digital zero starting at file offset ~1.7 s — `unlinked_sustained_zeros` |

The scout's single-direction assumption was wrong: starving the
*consumer* stalls the write (`unlinked_stall`), starving the *producer*
leaves the negotiated stream running and filling with zeros
(`unlinked_sustained_zeros`). The harness measures file size-trace and
content windows separately so buffered pre-unlink tone is never
misreported as zeros. Both legs finalize at exactly `expected_bytes`,
rc=1 (pw-record's normal bounded-capture exit), `unlink_rc`/`relink_rc`
recorded per edge.

---

## 8. FRONTIER 8 — `parec --fix-*`: the header is a request echo

Source monitor on this host: `float32le 2ch 48000` (module-null-sink).
Byte rate is measured as a least-squares slope over output-file growth
(`dd bs=8192` pipe for raw legs; see the seekability note), which kills
both the ~1.5 s PipeWire connect window and the 64 KiB flush-quantum
endpoint jitter.

| leg | request | measured payload | verdict |
| --- | --- | --- | --- |
| `rate_req` | `--raw --rate=22050` | 76 600 B/s → 22050 | request honored |
| `rate_fix` | `+ --fix-rate` | 195 756 B/s → 48000 | **adopted source rate** |
| `fmt_req` | `--raw --format=s32le` | 383 002 B/s → 4 B/smp | request honored |
| `fmt_fix` | `--format=s16le + --fix-format` | 383 002 B/s → 4 B/smp | **adopted source float32** |
| `ch_req` | `--raw --channels=1` | 97 878 B/s → 1 ch | request honored |
| `ch_fix` | `+ --fix-channels` | 195 756 B/s → 2 ch | **adopted source 2ch** |
| `hdr_rate_fix` | wav `--rate=22050 --fix-rate` | header **22050** / payload 48000 | `header_prefix_mismatch` |
| `hdr_fmt_fix` | wav `--format=s16le --fix-format` | header **16-bit** / payload float32 | `header_prefix_mismatch` |
| `hdr_ch_fix` | wav `--channels=1 --fix-channels` | header **1ch** / payload 2ch | `header_prefix_mismatch` |
| `hdr_rate_plain` | wav `--rate=22050`, no fix | header 22050 / payload 22050 | `header_honest` control |

**The lie is one-directional**: `--fix-*` makes the *payload* adopt the
source spec while the WAV header keeps advertising the *requested* spec
— a file that claims 22050 Hz s16 mono while carrying 48000 Hz float32
stereo. Any reader trusting the header misreads the stream.

**Transport caveat discovered this round**: `--file-format=wav` requires
a seekable output — piped through `dd`, parec fails at open with
`Failed to open audio file.` (rc=1, zero bytes; libsndfile seeks back
to finalize the header). The wav legs therefore write direct-to-file;
the raw legs keep the `dd` pipe.

---

## 9. Guards, limits, and host qualifications

- **Fail-closed**: every leg carries rc, stderr class, consumer union,
  and content witness; fallback legs must additionally prove the tag
  tone on the claimed sink's tap — topology alone never passes a row.
- **Shared-state restoration**: `default.audio.sink` is restored
  unconditionally in `finally`; all probe sinks (`r78_*_844895`) are
  unloaded; post-run `pw-dump` shows zero r78 nodes and metadata back at
  SPDIF.
- **Metadata parser tolerance**: the reader accepts quoted and bare SPA
  names — a concurrent r78-boundary lane wrote malformed values
  (`{"name":r78b_ns}`, `this is not json`) during development; the parse
  is evidence, never trusted blindly.
- **Nondeterminism admitted, not hidden**: `.monitor` (§1.4) and the
  `pactl` write (§2.2) are recorded as *sets* of measured outcomes with
  named classes — the harness asserts the set, not a single timing.
- **Observer sensitivity**: `alsa_busy` measures lock contention while a
  witness holds the PCM — it is not a claim about unobserved `hw:0,0`
  behavior. `host_is_quiet=false` is recorded on the receipt (one
  foreign `aplay`, r79 nodes live).
- **Sibling preservation**: the concurrent r77 `_capture_r77_node_props`
  client-id→PID fix is untouched; r49–r77 cells byte-stable (diff is
  +2401/−3, all three rewrites prepend-only).
- Not measured / out of scope: `pactl move-sink-input` (scout-confirmed,
  not re-armed), suspend/mute verbs, physical-lineout audibility, and
  any kernel-level PCM behavior. `alsa_tick_time` remains falsified per
  the scout and is not re-armed.
