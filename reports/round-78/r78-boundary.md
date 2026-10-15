# R78 BOUNDARY (audio) — hostile variants of the playback-lattice rows

Seat: **BOUNDARY (executor, leaf)**. Repo `~/Projects/shokunin/audio-shokunin`
@ HEAD `bdf748e` (`r77 fold-2`). Host `plazir27`, measured 2026-10-14
**~18:55–20:05 UTC**.

**Write scope: exactly `corpus/live/r78-boundary/` (untracked, new) plus this
report. Zero tracked-file edits.** Own harness (`r78b_lib.py` + 9 probe
drivers), own classifiers; `corpus/fixtures/measure_audio.py` was never read
or imported (a sibling seat edits it live). Tag tone is seat-unique:
**L 1100 Hz / R 1750 Hz, amp 12000**, 48 kHz s16 (scout used 1000/1500 @ 8192;
a foreign lane runs ~1 kHz stereo @ ~4096).

Toolchain: PipeWire **1.6.8**, pactl/pacat/parec **17.0-98-gb096**, alsa-utils
**1.2.16**, ffmpeg **n9.0.1**, Python **3.14.7**, numpy 2.5.3, Linux
7.2.3-arch1-3.

**r78-author-diff status:** the author *report* (`r78-author.md`) landed on
disk at the tail of my window (untracked, self-described "No commit");
`measure_audio.py` remains an uncommitted +2401/−3 worktree diff
(`--probe-capture-r78`, eight write-side entries). All probe rows below were
measured against the shipped surface before the report landed; §10.1 maps my
findings onto the author's declared coverage.

---

## 0. Headline

| # | brief row | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | forged `target.object` on playback | **LATTICE + 4 new laws** | every unresolvable prop/flag shape (source name, `.monitor`, source serial, port serial, `99999999`, glob, `0x50`, `-1`, u32max, live stream node) falls back — but `-P target.object=` **empty is a parse refusal** (rc=1, no node), `-P target.object=0` **falls back where `--target 0` pins**, a duplicated sink name **always resolves to the lowest serial** (3/3), and a target that appears *after* spawn **re-binds the live stream out of its fallback** |
| 2 | fallback under a DELETED default | **heals, fast** | after `pactl unload-module` of the metadata-named default, WirePlumber **rewrote `default.audio.sink` back to SPDIF within ~0.7 s**; fallback legs routed to SPDIF |
| 3 | `pw-metadata` default to a nonexistent name | **3-WAY DIVERGENCE** | bogus values are **stored verbatim then healed <0.7 s**; during the window `pactl get-default-sink` reported **Speaker** while the routed sink was the **DualSense Direct** sink (4-ch) and the stored value was my forgery — three resolvers, three answers. A stream riding the fallback **followed the poisoned default live** |
| 4 | `move-sink-input` races | **not atomic; revives the dead** | a rapid double move exposed `{old,new}` **fan-out windows** (ns+ns2, then ns2+SPDIF ~0.3–0.5 s each); and `move-sink-input` **re-links a `pw-link -d`'d stream** — `unlinked_sustained_playout` is not terminal |
| 5 | monitor-tap of a suspended sink | **suspend is advisory** | tapping a suspended sink (null **and** hardware Speaker) wakes it: node goes `running`, capture delivers **zeros at full negotiated rate** — indistinguishable from a silent live sink |
| 6 | `aplay -D hw:` vs active monitor | **reverse direction is silent-deadly** | with `aplay` holding `hw:0,0` first, `pw-play --target Speaker` still **rc=0, real-time, monitor carries the tone** — graph-level success while the PCM physically belongs to another process |
| 7 | `media.class` beyond the crashed | **partition extended + consumer-split** | crash set grows (`Audio/Sink/Virtual`, `Audio/Source/Virtual`, `Stream/Input/Audio[/Midi]`, `Audio/Duplex`, `Audio/Internal`); `Stream/Output/Audio/Midi` **plays** (sub-class tolerated); case variants **stall not crash**; `pw-record` + `Audio/Sink` **stalls not segv**; `paplay` gets `Connection terminated` not a crash; `PIPEWIRE_PROPS` env route segvs too |
| 8 | format axis on playback | **scout row needs scoping** | on `hw:` a **wav's own fmt is authoritative**: f32/u8/mulaw/8k-mono files are **refused** (`Sample format non available`, `can't play WAVE-file format 0x0007`, `Channels count non available`) — aplay's "adapts" applies only to the `-f` request flag; `plughw:`/`default` convert; truncated-header wav plays the real bytes (EOF-driven); pw-play converts everything and drops surplus channels at decode (6-ch file → exactly `output_FL/FR`) |
| 9 | play+capture self-contamination | **four mechanisms pinned** | double-fallback false positive (producer AND witness both defect to default → a name-only arm reads "honored" on two nonexistent nodes); two-producer sum hides the quieter tone under dominant-freq analysis; duplicate `node.name` merges `pw-link -l` consumers; capture-side **late-bind mirror** confirmed |

---

## 1. Forged `target.object` — the full lattice (`probe-p1-forged-target-r78b.json`, `probe-p1b-fixups-r78b.json`)

All legs `pw-play -P node.name=r78bA_<leg> … tone(1.8 s)`; routing witness =
`pw-link -l` consumers + tagged-tone monitor captures.

| leg | target.object prop or `--target` | routed to | verdict |
| --- | --- | --- | --- |
| `srcname_prop` / `srcname_flag` | `alsa_input…Line__source` | SPDIF | fallback |
| `monitor_prop` | `<SPDIF>.monitor` | SPDIF | fallback |
| `srcserial_prop` | object.serial of a **source** | SPDIF | fallback |
| `bogus_serial_prop` | `99999999` | SPDIF | fallback |
| `portserial_prop` | object.serial of a **Port** (`67`) | SPDIF | fallback — a port serial is not a target |
| `glob_prop` | `r78b_*` | SPDIF | fallback — no glob expansion |
| `u32max_flag` | `4294967295` | SPDIF | fallback (or `ANY` → same destination; indistinguishable) |
| `neg_flag` / `hex_flag` | `-1` / `0x50` | SPDIF | fallback |
| `ws_serial_flag` | `" 51183 "` (spaces) | SPDIF | fallback — whitespace breaks numeric parse |
| `streamnode_prop` / `streamnode_flag` | node.name of a **live Stream/Output/Audio** node | SPDIF | fallback — another stream is not a sink |
| `trailspace_prop` | `"r78b_ns "` | **r78b_ns** | honored — the trailing space is **trimmed at prop-parse** (node stores `target.object=r78b_ns`) |
| `empty_prop` | `-P target.object=` | **rc=1 `error: syntax error in --properties: Expected object value`** | **parse refusal — no node is ever spawned** (`prop_syntax_refusal`) |
| `zeroprop` | `-P target.object=0` | SPDIF, prop stored as **int 0** | **prop `0` falls back where flag `--target 0` pins-unlinked** — the pin law is flag-only |

**Duplicate-name determinism.** Two live `module-null-sink` nodes both named
`r78b_dup` (serials 53247/53254; earlier pair 52695/52708): `--target r78b_dup`
and `-P target.object=r78b_dup` both resolved to the **lowest object.serial /
first-created node, 3/3** — verified by serial-targeted monitor witnesses.
A name collision silently disenfranchises the younger node; there is no error
and no arbitration. For a hostile arm this is an identity primitive: load a
sink with a victim's `node.name` **earlier** and the name routes to you.

**Late-bind law (playback).** `pw-play --target r78b_late` spawned while the
sink does not exist: consumers = SPDIF at t=1.03 s (fallback), then
`r78b_late` was module-loaded at t=0.8 s and the consumers **moved to
`r78b_late:playback_*` by t=1.29 s**, staying for the rest of the file. The
fallback binding is **not latched** — the session manager keeps the named
intent and re-applies it when the node materializes. (This is the same
mechanism as the scout's unload→recreate-same-name row, here proven for a
*first* appearance out of a different sink's fallback.)

**Channel-granular pin.** `--target 0` publishes unlinked ports; pinning
**only `output_FL`** to `ns:playback_FL` runs the stream: the sink's monitor
shows `peak_L=12000, f_L≈1100, peak_R=0` for the whole tail (windows 2.0–6.5 s)
while FR stays unlinked — a half-linked playback plays at real-time with a
silent right channel.

## 2. Deleted & forged defaults (`probe-p2-stale-default-r78b.json`, `probe-p2b-divergence-r78b.json`)

**Deleted default heals.** `default.audio.sink → {"name":"r78b_def"}`,
verified `pactl get-default-sink = r78b_def`; `unload-module` of `r78b_def`:
within ~0.7 s the **metadata itself was rewritten to
`{"name":"…SPDIF__sink"}`** (not just ignored — healed) and
garbage/no-target/deleted-name legs all routed SPDIF.

**Forged values are stored verbatim, then healed, and the transient diverges
three ways.** For each of `{"name":"no_such_sink_r78b"}`,
`{"name":""}`, `this is not json`, `{"name":<LINE source>}`, `["r78b_ns"]`,
bare `r78b_ns` — `pw-metadata` accepts and stores the string raw (rc=0, no
validation), `pactl get-default-sink` answers **Speaker**, the stream's actual
links land on the **DualSense `Direct__Direct__sink`** (publishing
`playback_FL/FR/RL/RR`, 4-ch), and within ~0.7 s WirePlumber overwrites the
forgery with SPDIF. `{"name":123}` (wrong JSON type) takes a different path —
routed to SPDIF (the configured-fallback), not the manager pick. Working
variants: `{"name":"r78b_ns","bogus":1}` (extra field ignored) and
`{"name":r78b_ns}` (SPA-JSON tolerates the unquoted value) both resolve and
route to `r78b_ns`.

**A fallback-riding stream follows the default live.** A leg intended for
`r78b_ns` (absent → fell back to SPDIF) got a bogus-default write at t=2.2 s;
consumers switched `SPDIF → DualSense` at t≈2.4–2.6 s (timeline + DualSense
monitor carried the tone 2.5→4.0 s). Contrast the scout's row: an **honored**
stream does not follow a default change; a **fallback** stream does. The
binding's dynamism is a property of which route it took.

**Cross-resolver divergence under the poisoned window** (`source_name` leg):
playback routed to DualSense while the defected monitor witness carried no
tone — the capture-side fallback resolved to a *different* node than the
playback-side in that window. The `aplay -D default` leg under a bogus default
also carried tone on the (non-SPDIF) picked sink.

## 3. `move-sink-input` races (`probe-p3-move-races-r78b.json`, `probe-p3b-unlink-move-r78b.json`)

| leg | result |
| --- | --- |
| baseline move ns→ns2 at t=2.0 | rc=0, consumers ns→ns2 by ~2.3 s, tone follows (scout row reproduced on my tag) |
| move to `no_such_sink_r78b` | rc=1 `Failure: No such entity`, stream stays put |
| move to a **source** name / `<sink>.monitor` / stale idx `999999` | same rc=1 class, stream unaffected |
| `move-sink-input <a source-output idx>` | rc=1 `No such entity` — wrong entity type refused identically |
| **double move ns→ns2→SPDIF, 60 ms apart** | transient fan-out: consumers `{ns,ns2}` at t=2.04, `{ns2,SPDIF}` at t=2.3; ns2 carried the tone only 2.0–2.5 s; final placement SPDIF — **a move is not atomic; the stream is briefly linked to two sinks** |
| move→ns2 then `unload-module` ns2 at +0.35 s | consumers `{}` for ~0.35 s, then re-link to SPDIF — loss-fallback composes with move |
| `pw-link -d` both links, then `move-sink-input` ns→ns2 | **the move RE-LINKS the unlinked stream to ns2** (tone resumes 3.0→6.0 s) — `unlinked_sustained_playout` is not terminal; the pulse-layer move re-binds it |
| manual `pw-link` re-pin to ns2 after `pw-link -d` | same re-bind via link verbs |

## 4. Suspended-sink monitor tap (`probe-p4-suspended-tap-r78b.json`)

| leg | state before | capture | state after |
| --- | --- | --- | --- |
| tap suspended null sink (`suspend-sink 1` confirmed `suspended`) | suspended | **rc=1 (normal bounded rc), 384 044 B, all zeros at rate, 2.0 s** | `idle` — **the tap woke it** |
| tap suspended **hardware** Speaker | suspended | identical shape — zeros at rate | `idle` |
| suspend flag set while a tap is attached | — | node state read `running` despite the suspend request | suspension does not preempt an existing consumer |
| `pw-play` into a suspended sink | suspended | plays, tone on its monitor | `idle` after |

**Suspend is an idle policy, not an access barrier**: a monitor tap of a
sleeping sink resumes it and produces **zeros indistinguishable from a live
silent sink** — and, per §5, the resumed sink holds the ALSA PCM (that is why
the scout's witness caused `EBUSY`).

## 5. `aplay -D hw:` contention — the reverse direction (`probe-p5-aplay-reverse-r78b.json`)

| order | result |
| --- | --- |
| `aplay -D hw:0,0` on idle PCM | rc=0, 2.0 s |
| monitor tap on Speaker first → `aplay -D hw:0,0` | **EBUSY** (tap holds the PCM; scout row reproduced) |
| `pw-play → Speaker` first → `aplay` | EBUSY (reproduced) |
| **`aplay` holds hw:0,0 first → `pw-play --target Speaker`** | **rc=0, 2.475 s wall, links to Speaker ports, Speaker monitor carries the tone** — PipeWire "plays" into a sink whose PCM is foreign-held: the graph consumes, mixes, and feeds the monitor while the hardware emits nothing of it — `pcm_stolen_silent_success` |
| retention re-check (my tag) | `aplay` still EBUSY at +0.3/+1.5/+4 s after the prior hold ended — consistent with the scout's 1–7 s bracket |

The hostile content of row 6 is the asymmetry: PipeWire-first blocks aplay
(loud refusal), aplay-first blocks **nothing observable** — the PW stream
reports full success and even *content-verifies* through the monitor while the
DAC plays another process's bytes. An arm that trusts "monitor carried my
tone" cannot see the physical output was stolen.

## 6. `media.class` lattice — extended (`probe-p6-mediaclass-r78b.json`)

`pw-play -P media.class=<v> --target r78b_ns`, 6 s bound per leg:

| outcome | values |
| --- | --- |
| **plays** (rc=0, tone carried) | `Stream/Output/Audio`, **`Stream/Output/Audio/Midi`** (sub-class tolerated), `Stream/Output/Audio ` (trimmed at parse) |
| **SIGSEGV** (rc=−11, ~1.42 s, no node) | `Audio/Sink`, `Audio/Sink/Virtual`, `Audio/Source/Virtual`, `Stream/Input/Audio`, `Stream/Input/Audio/Midi`, `Audio/Duplex`, `Audio/Internal` |
| **stall** (node published `suspended`, zero links, timeout) | `Audio/Source`, `Audio/Source/Sink`, `Midi/Bridge`, `Video/Source`, `stream/output/audio`, `STREAM/OUTPUT/AUDIO` |

Cross-consumer, same wrong class:
- `pw-cat -p -P media.class=Audio/Sink` → **SIGSEGV** (1.63 s).
- `PIPEWIRE_PROPS='{media.class=Audio/Sink}' pw-play` → **SIGSEGV** — the env
  prop vector reaches the same crash.
- `paplay` + `PULSE_PROP_media.class=Audio/Sink` → **rc=1 `Connection failure:
  Connection terminated`** — the pulse path kills the stream; no crash.
- `pw-record -P media.class=Audio/Sink` (capture) → **stall**, not crash:
  suspended, zero links, `-n` never binds. The segv is a **pw-cat-family
  playback-client crash**, not a direction-symmetric PipeWire fault.

## 7. Format axis on playback (`probe-p7-format-play-r78b.json`)

Real wav files (own generator + ffmpeg for f32/mulaw) against `hw:0,0`,
`plughw:0,0`, `default`, and `pw-play --target r78b_ns`:

| file | `aplay -D hw:0,0` | `plughw:0,0` | `-D default` | `pw-play → ns` |
| --- | --- | --- | --- | --- |
| s16/48k/2ch | rc=0 | – | – | rc=0, tone |
| **f32** | **rc=1 `Sample format non available`** | – | rc=0 (plugin converts) | rc=0, converts |
| s24 packed | rc=0 (device has S24_3LE) | – | – | rc=0 |
| u8 | **rc=1 format refusal** | – | – | rc=0 |
| 6-ch | rc=0 (2–8 ch range) | rc=0 | – | rc=0 — **publishes exactly `output_FL/FR`** (surplus channels dropped at decode) |
| 8 kHz mono | **rc=1 `Channels count non available`** | rc=0 (resamples+upmixes) | rc=0 | rc=0, resamples |
| 96 kHz | rc=0 | – | – | rc=0 |
| μ-law wav | **rc=1 `can't play WAVE-file format 0x0007`** | same refusal | – | rc=0 (sndfile decodes) |
| truncated (declared ~16 MB, real ~80 KB) | rc=0, **0.645 s** — EOF-driven | – | – | rc=0, ~EOF-driven wall |
| 600 B garbage | rc=1 format refusal | – | – | rc=1 `sndfile: failed to open audio file` |

**Scoped correction to the scout's "aplay adapts the file":** the
`Warning: format is changed to S16_LE` behaviour applies to the `-f` *request*
knob; a wav's own `fmt` chunk is authoritative on `hw:` and refuses outright
when the device lacks it. Conversion lives in the plug/plugin layers.
**Truncated playout is EOF-driven in both tools** — a lying `data` size never
becomes playout time (reader-side analog of the r77 header-lie family).

## 8. Self-contamination mechanisms (`probe-p8-selfcontam-r78b.json`)

1. **Double-fallback false positive.** Playback `--target r78b_missing_play`
   (nonexistent) → SPDIF; simultaneously a "witness" capture `--target
   r78b_missing_witness` (also nonexistent) → defected to the SPDIF monitor and
   read **my tag tone 0.5–4.5 s**. Producer and witness defected to the same
   node: a name-only arm records a perfect "honored" roundtrip **for two
   nodes that never existed**.
2. **Two-producer sum.** `pw-play` tone-A (12000) and tone-B (14000,
   800/2100 Hz) into `r78b_ns` concurrently: monitor peaks ≈ **25 906/25 741**
   (the sum, near-saturating) but dominant-frequency analysis yields only
   tone-B — **the quieter stream is invisible to a single-tone classifier**;
   `mine_windows=[]` for tone-A while it demonstrably played.
3. **Twin `node.name`.** Two streams both tagged `r78bK_twin` → `pw-link -l`
   merges them: `output_FL` peers `[r78b_ns, r78b_ns2]` — topology cannot
   attribute which twin feeds which sink; only content separates.
4. **Capture-side late-bind (mirror law).** `pw-record --target r78b_late3`
   started while absent → defected to default; `r78b_late3` module-loaded at
   ~0.6 s, tone fed 1.1–5.1 s → capture windows `mine` **1.0→5.0 s**: the
   capture re-bound to the appearing target. Fallback is unlatched in **both**
   directions.

## 9. Confounds & provenance

- **Foreign lanes were live throughout**: a LÖVE battery (`sink-input "love"`,
  `output.r79_*` streams, `r79_ns_*` sinks — gone by seat exit), the
  `r78-baseline` seat's `measure_audio.py --probe-capture-r76` + a `parec
  --raw`, a foreign null sink `r78_prop_a_719095`, and the r75 `aplay -D null`
  stray. None of my legs touched foreign nodes/modules (`unload_all_mine`
  matches only `sink_name=r78b`).
- **I wrote `default.audio.sink` 15 times** (each bogus window ≤ ~3 s, every
  leg followed by a verified SPDIF restore; final state SPDIF, verified by
  `get-default-sink` **and** `pw-metadata`). During each bogus window a
  *sibling's* unresolvable-target leg would have routed to the DualSense sink —
  the standard hazard of this probe class (r77-boundary took the same lock).
- **My own defection incidents:** (a) in p2 the `ns2` witness targeted a sink
  I never loaded in that probe — every `ns2` reading there is a defected
  capture of the *current* default monitor, used as such in the analysis;
  (b) in p2b `r78b_ns` was absent for the follow-leg (load not verified —
  harness wart, mine), which is *why* the leg cleanly measured fallback-riding
  rather than honored binding. Evidence internally consistent both ways.
- **Classifier wart (mine):** p7's generated files put 1100 Hz on *both*
  channels, so `is_mine` read them "foreign" — the windows show the tone
  content plainly (1100 Hz at amplitude); verdicts for those legs were taken
  from the window data, not the classifier.
- ALSA holds were ≤3 s on `hw:0,0` (Speaker, suspended/unused, verified no
  foreign sink-inputs first); SPDIF was never suspended, muted, or
  metadata-poisoned beyond the tagged windows.

## 10. Shipped surface at HEAD + what the author diff should cover

`HEAD:bdf748e` `measure_audio.py` exposes probe families through
`--probe-capture-r77` (and r76); **no playback-family probe exists in the
committed fixture**.

### 10.1 Vs the landed author report (`r78-author.md`, declared surface)

The author's `--probe-capture-r78` declares: 14-leg `--target` fallback
lattice, live-default following (`pw-metadata` vs `pactl`), mid-play target
loss, `target.object`/`node.target`/`PIPEWIRE_PROPS` precedence (14 legs),
bogus `media.class` SIGSEGV, the `aplay` device axis (18 legs), directional
link-loss, and `parec --fix-*` header honesty.

**My rows that AGREE with the author's corrections:** "an active fallback
stream follows a mid-play default move" (author `followed_move`) = my
`leg_follow` measurement (§2); `pactl set-default-sink` stale = scout/boundary
law re-confirmed; `unlinked_sustained_playout` rc=0 full-duration = my §3
baseline rows. **New mechanism cross-ref:** the author names `.monitor`-target
resolution `monitor_target_source_peer` — routing to **the default *source*'s
peer sink (the DualSense `Direct__sink`)**. That is very plausibly the same
pick I measured under a forged `default.audio.sink` (§2: routed DualSense
while `pactl` said Speaker) — the poisoned-default fallback lands on the
source-peer, not on a hardware sink. Attributed to the author's report; my
legs measured the behaviour, not the resolver internals.

**My rows BEYOND the declared surface** (gaps a verifier should still probe):
the forged-prop edge cases (Port serial, duplicate-name lowest-serial rule,
glob/whitespace/hex/negative shapes, live-stream-node targets,
empty-prop parse refusal, `target.object=0` ≠ `--target 0`), the
**poisoned/deleted default** path (metadata heal <0.7 s + the 3-way
divergence) — the author covers live switching, not poisoning; the
**`move-sink-input` race family** (transient fan-out, wrong-type index
refusals, and **move-revives-unlinked**); the **suspended-sink monitor tap**
(tap wakes the node; suspend is advisory); **`pcm_stolen_silent_success`**
(aplay-first hold: PW plays rc=0 + monitor tone while the PCM is foreign-held);
the extended `media.class` partition (`Stream/Output/Audio/Midi` **plays**,
case-variants stall, pw-record stalls not crashes, paplay connection-
terminated, `PIPEWIRE_PROPS` env crash); **file-fmt authority on `hw:`**
(aplay refuses real f32/u8/mulaw/8k-mono wavs — the scout's "adapts" row is
`-f`-flag-scoped); and the four **self-contamination** mechanisms (§8).

## 11. Named classes added this round

| class | shape | trigger |
| --- | --- | --- |
| `prop_syntax_refusal` | rc=1 `syntax error in --properties`, no node | `-P key=` empty value |
| `target0_prop_flag_asymmetry` | `-P target.object=0` → default fallback vs `--target 0` → pinned stall | numeric `0` via the two vectors |
| `dup_name_lowest_serial_wins` | name target resolves to first-created of N same-named nodes | duplicate `node.name` on sinks |
| `late_bind_retarget` | fallback at spawn, re-link on target appearance | named target materializes mid-stream |
| `default_metadata_triple_divergence` | stored-forgery ≠ `pactl get-default-sink` (Speaker) ≠ routed sink (DualSense), heal <0.7 s | bogus `default.audio.sink` value |
| `move_transient_fanout` | `{old,new}` consumers coexist ~0.3–0.5 s | rapid/double `move-sink-input` |
| `move_revives_unlinked` | `pw-link -d`ed stream re-links on move | `move-sink-input` on zero-link stream |
| `suspend_advisory_wakeup` | suspended sink → `running` under tap; zeros at rate | monitor-tap of suspended sink |
| `pcm_stolen_silent_success` | rc=0 + monitor tone while aplay holds the PCM | `aplay -D hw:` before `pw-play` to that sink |
| `class_segv_consumer_partition` | segv on pw-cat-family only; paplay→`Connection terminated`; pw-record→stall | `-P media.class=<non-Stream/Output>` |
| `aplay_file_fmt_refusal` | rc=1 pre-open; `fmt` chunk authoritative on `hw:` | real wav in a format `hw:` lacks |
| `double_fallback_falsepos` | missing-target producer + missing-target witness both land on default → fake roundtrip | two unresolvable targets in one arm |
| `dominant_freq_blindness` | quieter stream invisible under dominant-freq classification | two producers summed on one sink |
| `twin_name_topology_merge` | `pw-link -l` merges same-named streams' consumer lists | duplicate stream `node.name` |

## 12. Receipts

All under `corpus/live/r78-boundary/` (untracked; raw monitor wavs trimmed —
~740 KB kept: 9 scripts + 12 JSONs).

| receipt | sha256[:16] |
| --- | --- |
| `probe-p0-smoke-r78b.json` | `c48c10e5d31c6b8b` |
| `probe-p1-forged-target-r78b.json` | `89c3ce6d0912bea2` |
| `probe-p1b-fixups-r78b.json` | `36bbc62cd98e2f37` |
| `probe-p2-stale-default-r78b.json` | `2b610e458407bca8` |
| `probe-p2b-divergence-r78b.json` | `e85bad5a382dd0dc` |
| `probe-p3-move-races-r78b.json` | `03ddfed763d81dce` |
| `probe-p3b-unlink-move-r78b.json` | `831922103e5f2413` |
| `probe-p4-suspended-tap-r78b.json` | `c9757f38214f92b1` |
| `probe-p5-aplay-reverse-r78b.json` | `809eb22f18ab0e89` |
| `probe-p6-mediaclass-r78b.json` | `b10e2cd8ca9af423` |
| `probe-p7-format-play-r78b.json` | `268fa79f2724ce75` |
| `probe-p8-selfcontam-r78b.json` | `dcef109479133160` |

## 13. Honest edges

- All verdicts are this-host/this-toolchain; the crash partition is
  behavioural (no debugger), and the DualSense-vs-Speaker pick under a forged
  default is a measured fact whose resolver internals I did not read.
- `late_bind` was proven by topology timeline; its content witness defected
  (target absent at monitor start) — the same trap §8.1 measures.
- The capture-side resolver's pick under a forged default is weakly pinned
  (one divergent leg, `source_name`); the playback-side pick (DualSense) is
  5-leg certain.
- `dup_name` winner rule is 3/3 first-created in *this* session; ordering
  under concurrent creation is untested.
- Not attempted: hardware-sink destruction (would take a device off the host),
  SPDIF suspend/mute (foreign traffic risk), `pw-cli`-level param probing.
- Host at exit: no `r78b*` modules, no seat processes, `default.audio.sink`
  and `get-default-sink` restored to SPDIF, `git status --porcelain` shows
  only my untracked seat dir + this report (plus the pre-existing fixture
  dirty state, a sibling seat's).
