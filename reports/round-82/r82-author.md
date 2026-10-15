# r82 AUTHOR — the ffmpeg/ffprobe/ffplay↔PipeWire lattice armed into the lane harness

host: devin (`Linux plazir27 7.2.3-arch1-3`). Seat: author (r82). Scope:
arm the r82 scout's nine pinned frontier claims
(`reports/round-82/r82-scout.md` §0 + §9 verbatim-armable cells; receipts
`corpus/live/r82-scout/s*.json`), as corrected/bounded by the r82-boundary
seat (`reports/round-82/r82-boundary.md`, receipts
`corpus/live/r82-boundary/`), into `corpus/fixtures/measure_audio.py` as a
**new parallel ledger family, insertion-only** — `--probe-ffmpeg-r82` —
run it twice green, replay the full prior battery twice with prior rows
verdict-stable, and document evidence + corrections. **No commit, no
push.**

Toolchain (receipt-verified): ffmpeg/ffprobe/ffplay **n9.0.1**
(libavformat 63.1.101, `--enable-libpulse` — no native pipewire device),
PipeWire **1.6.8**, `PulseAudio (on PipeWire 1.6.8)` protocol 35,
WirePlumber **0.5.17**, Python 3.14.7. `corpus/live/r82-author/
toolchain.txt` pins the banner lines.

## 1. Declared move

`--probe-ffmpeg-r82`: **eight entries, 76 legs**, one entry per armed
claim group:

| entry (measurements key) | legs | claims |
| --- | --- | --- |
| `ffpw_device_surfaces_r82_probe` | 8 | device lattice (no pipewire device; `-f pipewire` rc=234 EINVAL; `-sources pipewire` empty; live `-sources/-sinks pulse`; `*` vs pactl recorded; `-h muxer=/demuxer=pulse` option table) |
| `ffpw_capture_lattice_r82_probe` | 17 | capture validates at connect (251 EIO bare/bogus/sink-name), `default` bimodal ×3, aliases resolve, the `.monitor`-suffix permissive hole (boundary), name/env-prop split, spec legs, pulse no-clamp |
| `ffpw_playback_lattice_r82_probe` | 13 | playback validates only `""` (rc=187); every other name rc=0 + literal `target.object` + silent re-route to default, tap-witnessed; `@DEFAULT_SINK@` resolves; PULSE_SINK honored; `-server` rc=187 |
| `ffpw_buffer_knobs_r82_probe` | 14 | outdev `pulse.attr.*` map with libpulse floors/clamps; indev `fragment_size`→`fragsize`+`node.latency`; post-`-i` swallow vs `-frame_size` SIGABRT vs pre-`-i` deprecation |
| `ffpw_target_loss_r82_probe` | 8 | BOTH directions re-link to default under own-sink destruction (3+3 reps) + pw-record control (2 reps); growth/finalization of the capture artifact; pump's own re-link witnessed |
| `ffpw_error_classes_r82_probe` | 6 | typed rc map: 222 ERANGE option-range ×3, SIGABRT libpulse asserts ×2, 253 ESRCH bad-server |
| `ffpw_alsa_split_r82_probe` | 7 | hw busy 251 both directions, subdevice independence under PW-held playback, `pipewire`/bogus PCM 251, `default` bimodal envelope, silent rate clamp |
| `ffpw_ffplay_ffprobe_r82_probe` | 3 | ffplay dual personality (SDL-native vs SDL-pulse, `PULSE_SINK` ignored under the pulse driver), ffprobe live-indev wallclock PTS |

Harness anchors: family block `measure_audio.py:14180`–`16311`;
constants `:14248`–`:14279`; error-class tuple `:14281` (separate table —
never prepended into the shared `_CAPTURE_ERR_CLASSES`, same rule as
r77/r78/r81); runner `_ffpw_r82_leg` `:14402` (the pgid-owning
triple-bounded loop); entries `:14773`/`:14903`/`:15235`/`:15493`/
`:15661`/`:15905`/`:15980`/`:16180`; wiring `:16436` (flag), `:16444`
(mutex), `:16735` (dispatch), `:17358` (mode), `:17378` (suffix).
Tracked diff: **+2 170/−3** (the −3 are the three wiring lines — mutex
sum, mode ternary, suffix ternary — each rewritten as a prepend-only
ternary; every other byte is insertion).
`python3 -m py_compile` clean.

**Contention (mandatory, inherited and tightened):** every routing leg
targets the seat-owned null sink `r82ff_ns_<pid>` or is read-only;
stream/node names `r82ff_<pid>_*`; env-prop names `r82ffx_<pid>_*`;
**every unload goes through `_ffpw_r82_unload_own` →
`_gst_r81_unload_own(sink_name=FFPW_R82_NS)`** — `pactl list modules
short` is re-read immediately before firing and only the index whose
*argument string* carries our `sink_name=` is unloaded (a bare captured
index is never trusted — indices recycle LIFO, the scout's §10 incident);
`pactl set-default-sink`/`set-default-source` are never invoked; every
ffmpeg/ffprobe/ffplay/pw-record leg is **triple-bounded** in the same
loop that owns the process group — element bound (`-t`/`-n`/`-re` EOF)
inside argv + wall cap + byte cap (`_ffpw_r82_leg`, `:14402`); graph
identity is by **object id** with the client join
`node.client.id → Client.application.process.id` — never by name
(`ffplay` and `pw-record`/`pw-cat` names collide across seats).
Tone witnesses are the tag-tone classifier on bounded monitor taps
(`_ffpw_r82_tap` → `pw-record -n <samples>` on `<sink>` with
`stream.capture.sink=true`).

## 2. Headline — the nine claims, re-measured (run1 verbatim)

All nine scout claims held under author re-measurement; every number
below is from `run1.measurements.json` verbatim (sha-pinned copy under
`corpus/live/r82-author/ffmpeg-r82-runs/`); the same verdict surfaces
reproduced in `run2` and in the final-sha pair `final3`/`final4`.

### Claim 1 — device surfaces → `ffpw_device_surfaces_r82_probe`

- `d0_devices_r{0,1}`: `DE pulse`, `DE alsa`, `D. jack`, `DE oss`,
  `DE sndio`, `D. lavfi` — **no pipewire row**, identical across reps.
- `d1_forced_pipewire`: rc=**234**, class `ff_unknown_format`
  (`Unknown input format: 'pipewire'`).
- `d2_sources_pipewire`: rc=0, **zero rows**. `d3`/`d4`: rc=0 with the
  live graph enumerated — including the foreign seats' nodes
  (`r83b_ns{a,b,m,48,44}`, `r84b_ns`, `r93s_in`, `r93s_fc_in` — a live
  contention witness).
- `d4_sinks_pulse.star_vs_pactl` = **`agree`** this run (`*` = SPDIF,
  matching `pactl info`) — recorded-not-gated; the scout's "observed
  disagree once" stays an open leaf (§10 falsification #11).
- `d5`/`d6`: option tables pin `server/name/stream_name/device/
  buffer_size/buffer_duration/prebuf/minreq` (muxer) and
  `server/name/stream_name/sample_rate/channels/frame_size/
  fragment_size/wallclock` (demuxer) with `name` default `"Lavf63.1.101"`,
  `stream_name` `"record"`, `48000`/`2`.

### Claim 2 — the capture-vs-playback validation asymmetry

**Capture** (`ffpw_capture_lattice_r82_probe`):

- `c0_ns_monitor`: rc=0, node `Lavf63.1.101`, `media.class=
  Stream/Input/Audio`, `target.object=r82ff_ns_<pid>` (`.monitor`
  STRIPPED), `stream.capture.sink=True`, `client.api=pipewire-pulse`,
  `node.rate=1/48000`, `node.latency=2400/48000`,
  `pulse.attr.fragsize=9600`, `producers==[ns]` — and the pump's tag
  tone lands in the captured wav (`mine_windows=20` over the 2 s bound).
- Refusals: `c1_bare_sink`, `c2_bogus_src`, `c12_sink_name` (the bare
  default-sink name) all rc=**251** `ff_io_error` in well under a second
  (boundary's tighter bound 0.022–0.063 s vs scout's ~0.93 s — the
  fixture pins the class, not the wall). No wav bytes beyond the header.
- `c3_default_r{0,1,2}`: **3/3 `eio_251`** — the `hang_killed` arm of
  the envelope never realized on author runs (scout saw 1 hang in 3;
  boundary saw 11/11 EIO — the envelope stays `{eio_251, hang_killed}`).
- `c4_defmon_alias`/`c5_defsrc_alias`: `@DEFAULT_MONITOR@` and
  `@DEFAULT_SOURCE@` resolve to the leg-time defaults
  (`target.object`/`producers` = resolved names, not the literals).
- `c6_named`: `-name`/`-stream_name` rename `node.name`/
  `application.name`/`media.name` verbatim.
- `c7_env_props`: `PIPEWIRE_PROPS node.name=r82ffx_<pid>_cap` is
  **overridden to `Lavf63.1.101`** on the pulse path while
  `stream.capture.sink=true` from the same string lands — the
  env-prop split law.
- `c8_spec_44k1`: `node.rate=1/44100`, `node.latency=2205/44100`,
  `fragsize=4410`, wav 44100/1ch. `c10_weird_ch7`: `fragsize=33600`,
  `maxlength=4194302`, 7ch wav.
- `c9_real_source`: direct source capture binds the default source.
- **`c13_bogus_monitor` (boundary-encoded)**: `-i no_such_thing_
  <pid>.monitor` → rc=**0**, `target.object` = the literal
  `.monitor`-stripped name, `stream.capture.sink=True`,
  `producers=[SPDIF default]` — the permissive hole: the `.monitor`
  suffix bypasses name validation entirely and silently falls back to
  the default sink's monitor.
- **`c14_rate_passthrough` (boundary-encoded)**: `-sample_rate 12345`
  pre-`-i` → `node.rate=1/12345`, `node.latency=617/12345`,
  `fragsize=2468`, wav rate 12345 — **no pulse-side clamp** (contrast
  `a6`'s ALSA nearest-supported).
- `c11_bad_server`: `-server unix:/nonexistent-r82ff` → rc=**253**
  `ff_no_such_process`.

**Playback** (`ffpw_playback_lattice_r82_probe`):

- `p0_honor`: rc=0, `target.object=ns`, `consumers=[ns]`, node carries
  the full pinned prop set (`tlength=384000`, `prebuf=380164`,
  `minreq=3840`, `maxlength=4194304`, `latency=8192/48000`,
  `want-driver=True`, `media.name=r82ff-play-<pid>` = the outdev URL
  tail), and the ns tap carries the tag tone while the default tap
  stays clean.
- `p1_bogus`/`p2_src_name`/`p3_monitor_name`/`p4_default_kw`: rc=0
  **all**, `target.object` = the literal (bogus string / source name /
  `ns.monitor` / `default`), `consumers=[SPDIF default]` — and the
  **default tap carries the tag tone while the ns tap stays silent**:
  the silent re-route is content-witnessed, not inferred.
- `p5_alias`: `@DEFAULT_SINK@` lands **resolved**
  (`target.object=<real default>` — the one non-literal).
- `p6_env_sink`: `PULSE_SINK=ns` honored → lands on ns (ns tap tone).
- `p7_env_vs_flag`: `-device default` beats `PULSE_SINK=ns` →
  `winner=device_flag`, `consumers=[default]` — flag-over-env.
- `p8_no_device`: no `-device` → **no `target.object` at all**,
  consumers=[default].
- `p9_bad_server`: `-server unix:/nonexistent-r82ff` on the outdev →
  rc=**187** `ff_access_denied` (`Cannot connect context: Access
  denied`) — the 253/187 split between indev and outdev holds.
- `p10_named`: `-name`/`-stream_name` rename lands with
  `target.object=ns`.
- `p11_env_target`: `PIPEWIRE_PROPS {target.object=ns}` on the outdev
  is **ignored** — no `target.object` prop, `consumers=[default]`.
- **`p12_empty_device` (boundary-encoded)**: `-device ""` → rc=**187**,
  class `ff_pulse_sink_info` (`pa_context_get_sink_info_by_name
  failed` + `Updating sink info failed`), **no node, taps silent** —
  the single validated string; falsifies "never validates" as a
  universal law (boundary claim-1 correction, now armed).

### Claim 3 — the buffer/latency lattice → `ffpw_buffer_knobs_r82_probe`

Outdev (options between `-f pulse` and the URL) — exact pulse.attr map:

| leg | tlength | prebuf | minreq | node.latency |
| --- | --- | --- | --- | --- |
| b0_default | 384000 | 380164 | 3840 | 8192/48000 |
| b1_bufsize 16384 | 16384 | 12548 | 3840 | 2176/48000 |
| b2_bufdur 500 | 96000 | 92164 | 3840 | 8192/48000 |
| b3_prebuf 8192 | 384000 | 8192 | 3840 | (unchanged) |
| b4_minreq 512 | 384000 | 382980 | **1024** (clamped up) | 8192/48000 |
| b5_all | 38400 | 16384 | 1024 | — |
| b6_bufsize_1 | 3072 | 2052 | 1024 | 256/48000 |

Indev — position is the law: `ci1` (`-fragment_size 2048` **before**
`-i`) → `fragsize=2048`, `latency=512/48000`; `ci2` (`65536`) →
`65536`, `16384/48000`; `ci4` (same option **after** `-i`) → `fragsize`
unchanged 9600, **zero stderr** — the silent swallow. `ci3`
(`-frame_size 8192` before `-i`) → deprecation note printed, fragsize
unchanged. `ci5` (`-frame_size 8192` after `-i`) → **rc=-6 SIGABRT**
`ff_sched_assert` (`enc->sq_idx[0] >= 0`) — the position-dependent
crash, armed as a crash cell not hidden. `ci6` (post-`-i`
`-sample_rate 44100 -channels 1`, the demuxer spellings) → swallowed,
wav keeps 48000/2ch (boundary's "post-`-i` `-ac`/`-ar` land" is about
the *encoder* spellings — disjoint claim, noted in-code).

### Claim 4 — target loss re-links BOTH directions → `ffpw_target_loss_r82_probe`

3+3 reps at `timeline=0.2 s`, unload fired at t≈1.2 s through the
name-verified index:

- `t1_play_r{0,1,2}`: unload at 1.203/1.208/1.206 s; **consumers
  re-appear `[SPDIF default]` at the very next 0.2 s sample**
  (1.203/1.208/1.206 s — i.e. within the sampling quantum; the
  boundary's finer 35–57 ms sits below my resolution, consistent);
  every rep exits rc=0 at input EOF; the default-monitor tap carries
  the tag tone **post-unlink** (content witness of the re-route).
- `t2_cap_r{0,1,2}`: producers re-link `[ns]→[SPDIF]` at the unload
  sample; the wav **keeps growing** through the event and finalizes at
  the `-t 5` bound; `cap_tone.mine_spans` continuous (16 windows each,
  spans covering the pre-unlink pump interval); the pump's own playback
  node re-links `[SPDIF]` inside the same samples (witnessed in-place).
- `t3_pwrec_r{0,1}`: the pw-record control re-links producers→default
  too (r1 at +0.2 s sample) — the WirePlumber-generic control —
  exiting rc=1 at its `-n` bound (the rc itself is pw-record's bound
  exit, recorded not gated).

Envelope vs pins: the fixture arms `FFPW_R82_RELINK_BOUND_S = 0.8 s`
(scout ~0.22–0.27 s, boundary 19–57 ms — an envelope, not a constant).

### Claim 5 — typed rc map → `ffpw_error_classes_r82_probe`

| leg | rc | class | hit |
| --- | --- | --- | --- |
| e1 `-sample_rate 0` | 222 | `ff_option_range` | `out of range [` |
| e2 `-channels 0` | 222 | `ff_option_range` | `out of range [` |
| e3 `-fragment_size -2` | 222 | `ff_option_range` | `out of range [` |
| e4 `-channels 99` | **-6 SIGABRT** | `ff_libpulse_assert` | `pa_channels_valid` |
| e5 `-sample_rate 999999` | **-6 SIGABRT** | `ff_libpulse_assert` | `pa_sample_spec_valid` |
| e6 `-server unix:…` indev | 253 | `ff_no_such_process` | `No such process` |

(The `ff_pulse_sink_info` class added to the family tuple for p12 —
insertion at the tail of the local table, never into the shared one.)

### Claim 6 — the ALSA split → `ffpw_alsa_split_r82_probe`

`alsa_dev=hw:0,0` (first enumerated capture dev):

- `a0`/`a1`: rc=251 `ff_alsa_busy` under an arecord/aplay holder —
  busy in **both** directions.
- `a2`: with PW holding the card's playback subdevice (an ffmpeg
  pulse stream on `…Speaker__sink`, `holder_consumers` recorded),
  `ffmpeg -f alsa -i hw:0,0` capture → **rc=0**, finalized wav —
  subdevice independence.
- `a3`: `-i pipewire` → 251 `ff_alsa_params` (`cannot set
  parameters`); `a4`: bogus PCM → 251 `ff_alsa_unknown_pcm`.
- `a5_default_plugin`: realized **`params_251`** in both author runs —
  matching the boundary's correction (the `default` PCM's *capture*
  direction is broken host-wide right now: ffmpeg 251 **and** arecord
  `-D default` rc=1; the plugin stream the scout sampled once — with
  `node.name` env-landing — is the other arm of the armed envelope
  `{plugin_rc0, params_251}`).
- `a6`: `-sample_rate 12345` → rc=0, wav rate **44100** — the silent
  nearest-supported clamp (boundary generalized it to a negotiation
  map: 96000→96000, 999999→192000 — the fixture pins the scout's
  12345 cell verbatim).

### Claim 7 — ffplay/ffprobe → `ffpw_ffplay_ffprobe_r82_probe`

- `f0_ffplay_native`: rc=0, node `ffplay`, **no `client.api`** (SDL's
  native PipeWire client), `media.role=Game`,
  `node.latency=2048/48000`, `consumers=[SPDIF default]`.
- `f1_ffplay_sdl_pulse`: `SDL_AUDIODRIVER=pulseaudio` +
  `PULSE_SINK=ns` → `client.api=pipewire-pulse`, `media.name="Audio
  Stream"`, `tlength=6144`/`prebuf=4100`/`minreq=2048`,
  `latency=512/48000` — and `target.object=[SPDIF default]`:
  **SDL's pulse driver ignores `PULSE_SINK`** while ffmpeg's own
  `-f pulse` honored it in p6 — the client-specificity law
  (boundary claim-5 confirmed, armed).
- `f2_ffprobe_live`: `ffprobe -show_streams -f pulse -i ns.monitor` →
  rc=0 in ~0.18 s (scout ~1.02 s — wall is an envelope), reporting
  `pcm_s16le`/`48000`/`2ch` with `start_time≈1792092631.093` —
  epoch-class wallclock PTS; **no persistent node** (the stream dies
  with the read).

### Claim 8/9 — honest leaves

- `-sinks pulse` `*` vs `pactl info`: `agree` in both author runs —
  kept as a recorded leaf (`star_vs_pactl`), not gated (falsification
  #11 stays open: disagreement was observed once with an r78
  leftover).
- Harness artifact confirmed and quarantined: **`-nostdin` is not an
  ffplay option** — `Failed to set value '-nodisp' for option
  'nostdin'` rc=1 (the scout's recorded artifact; the family comments
  the exclusion in-place and runs the real legs without it).

## 3. Corrections vs the scout, encoded

| scout claim | author resolution |
| --- | --- |
| "capture validates the name" (universal) | **bounded** — the `.monitor` suffix bypasses lookup entirely (c13: rc=0, literal stripped target, default-monitor fallback). Universal form dropped. |
| "playback never validates" (universal) | **bounded** — `-device ""` is rc=187 `ff_pulse_sink_info` (p12); every non-empty string stays rc=0+fallback. |
| capture EIO "~0.93 s" | **timing not pinned** — class/rc only; boundary measured 0.022–0.063 s, mine are in that band. |
| `-i default` capture "hang+EIO" | envelope `{eio_251, hang_killed}` armed; author saw 6/6 `eio_251` (boundary 11/11 EIO). |
| `-f alsa -i default` → plugin rc=0 | **bimodal** `{plugin_rc0, params_251}` armed; author saw `params_251` both runs (host capture-default is currently broken — boundary's correction). |
| `pw-record` control "sustained zeros" | measured otherwise here: re-links producers→default and exits rc=1 at `-n` — recorded verbatim, no verdict borrowed. |
| `-frame_size` position-dependent SIGABRT | confirmed exactly: pre-`-i` deprecation-only (ci3), post-`-i` `ff_sched_assert` rc=-6 (ci5). |
| pulse `-sample_rate` clamp | **none** — c14 publishes `1/12345` verbatim; the clamp lives on the ALSA path only (a6). |

## 4. Repetitions and the full prior battery

**Formal family runs**: four `--probe-ffmpeg-r82` executions total —
the battery-script pair `run1`/`run2` (fixture sha `f9d88dcc…`,
`20261015T194415547218Z`/`…194659044785Z-ffmpeg-r82`) and the **final
pair `final3`/`final4` on the landed sha `eb865760…`**
(`corpus/live/runs/20261015T200955375107Z-ffmpeg-r82/` and
`…201238976393Z-ffmpeg-r82/measurements.json`, copies at
`ffmpeg-r82-runs/final{3,4}.measurements.json`) — all four
`{"failures": {}}` exit 0, `sinks_gone`/`own_nodes_after` clean in
every loaded entry. **76 legs ×4 = 304 leg-executions, all green**;
the final pair is byte-frozen on the handoff fixture. A-vs-B on the
final pair (`percase.py`, pid/scratch/clock-normalized,
`corpus/live/r82-author/stability-r82-final34.txt`): **17 612 leaf
paths** — base entries 100 % exact; r82 semantic leaves **50**, all
environmental class (sibling default-source churn `r85b_*`, foreign
nodes appearing in the `-sources`/`-sinks` enumerations, `host_is_quiet`
flips, 0.2 s-timeline sample-count + node-array-order phase jitter
inside the loss legs). **Zero verdict-surface drift** — every rc,
error class, prop pin, relink set and tone verdict reproduced
bit-for-bit.

**Prior battery**: the r82-baseline seat's 4-command battery verbatim —
`normal`, `--probe-capture-r78`, `--probe-capture-r79`,
`--probe-module-r80` — replayed **twice** on the live tree
(`corpus/live/r82-author/battery.sh`, receipts/logs under `runs-a/`,
`runs-b/`):

- **Commands: 8** (4 modes × 2 passes). Row census per pass: **86
  entries / 136 legs** — `normal` 17/0, `capture-r78` 25/59,
  `capture-r79` 25/67, `module-r80` 19/10 — **identical to the
  baseline's census in every run**; ×2 passes = **172 entry-rows /
  272 leg-rows replayed**.
- **Verdicts**: 5/8 runs fully clean (both `normal`, `runs-b`
  `capture-r79`, both `module-r80`). The three reds are all the
  **sibling-contention class the r82-baseline itself logged**
  (commit `2333fac`: "reds = named sibling contention"):
  `runs-a/capture-r78` and `runs-b/capture-r78` each red once in
  `playback_default_follow_r78_probe` ("stream never settled on the
  live default at ITS spawn `r78_def_sink_*`" — the probe's own
  default-sink handoff raced a sibling's default churn; the baseline
  recorded the *same probe* red in its `runs-b`);
  `runs-a/capture-r79` red twice in `loopback_capture_lattice_r79_probe`
  (`b03_dotmonitor`/`b05_garbage` "expected producers `[r85b_vd5]`/
  `[r85b_vd7]`" — the leg-time default sink was a *sibling's* node
  which vanished mid-leg; the baseline recorded `b05_garbage` under
  the same confound). No r82 row is implicated in any red — all three
  are r78/r79 environmental cells under live default churn.
- **Byte-identity**: the `normal` receipt sha
  `8e8cdad6cc3c356d07c4…` is **byte-identical 6 ways** — author-a,
  author-b, baseline-a, baseline-b, and the tracked canonical receipt
  (the r82-baseline `byte-identity.txt` pins it against 375 landed
  receipts).
- Fixture sha is recorded before/after every command in
  `commands.log`: `f9d88dcc…` through runs-a `capture-r78`;
  `eb865760…` from runs-a `capture-r79` onward — the one mid-battery
  delta is the dead-expression removal inside `ci6`'s own added
  block (comment + unused var; zero behavioral change; both shas
  constant within every run; the formal pair `final3`/`final4`
  re-verified the r82 family on `eb865760…`).

## 5. Contention ledger

- **Siblings live throughout**: `r83b_*` (5 null sinks), `r84b_ns*`,
  `r85b_*` (actively flipping `default_source` — `r85b_sd`,
  `r85b_late`, `r85b_mix` observed as the leg-time default source),
  `r93s_in`/`r93s_fc_in`/`r93s_fc_out`/`r93s_rec` (a live DSP/filter-chain
  scout with a running `pw-record`). All enumerated in the `-sources
  pulse`/`d3` rows of the receipts.
- All r82 resources are `r82ff_ns_<pid>`/`r82ff_<pid>_*`/`r82ffx_<pid>_*`;
  the foreign census rides in `contention` + `d3`/`d4` row lists.
- The shared default sink `alsa_output.…SPDIF__sink` carries the tag
  tone during the deliberately-armed fallback legs (bounded ~2.2 s
  each — the same witness technique the scout used; `contamination`
  blocks declare it in the playback and loss entries).
- `pactl set-default-sink`/`set-default-source`: **0 invocations**
  (grep-clean over the family; the `@DEFAULT_*@` alias legs and
  default-fallback legs only READ the leg-time default).
- Every unload: name-verified index (`verified_index`/`captured`/
  `recycled` recorded per call); runs show `recycled:false`, rc=0,
  and `skipped:not_listed` where a loss leg's own event already fired
  it (no double-unload).
- Post-run sweep: `sinks_gone` true / `own_nodes_after []` in every
  loaded entry on both formal runs; a post-battery census shows **zero**
  `r82ff_*`/`r82ffx_*` sinks, nodes or modules (see §6 post-state).

## 6. Write scope, replay, tree state

- **Tracked edits: one file** — `corpus/fixtures/measure_audio.py`
  (+2 170/−3, sha256 `eb86576063b359b8bd69d5147b03e443e73990052e76f
  9221a552cd0864d20b4` final; the two formal probe runs ran on
  `f9d88dcc…` — the only delta between them is the `ci6`
  dead-expression cleanup).
- **Untracked artifacts**: `corpus/live/r82-author/` (`battery.sh`,
  `battery.log`, `pre-state.txt`, `toolchain.txt`,
  `ffmpeg-r82-runs/run{1,2}.measurements.json` + commands/stderr/sha
  logs, `runs-a/`/`runs-b/` receipts+logs, `stability-r82-runsAB.txt`);
  the canonical receipts the fixture wrote under `corpus/live/runs/`
  (two `-ffmpeg-r82` dirs + eight battery dirs); this report.
  **No commit, no push.**
- **Replay**: `python3 corpus/fixtures/measure_audio.py
  --probe-ffmpeg-r82` from the repo root (~3.5 min; writes a
  `-ffmpeg-r82` receipt, prints `{"receipt": …, "failures": {}}`,
  exit 0 on a clean run).
- **post-state** (`corpus/live/r82-author/post-state.txt`,
  2026-10-15T20:15Z): **zero** `r82ff_*`/`r82ffx_*` sinks, modules or
  nodes; zero leftover ffmpeg/ffplay/pw-record/measure_audio
  processes. The only tracked modification at handoff is
  `corpus/fixtures/measure_audio.py` (`__pycache__` .pyc restored via
  `git checkout` — the tracked diff is the source edit alone); HEAD
  moved `b7d80d0`→`2333fac`→`3db77b13`→`1abd9549` during the window —
  sibling commits, not mine.

## 7. Remaining unknowns (carried honest)

- The `c3` `hang_killed` arm is armed-but-unrealized on this host
  today (6/6 EIO in author runs; scout 1/3 hang; boundary 11/11 EIO) —
  the envelope stays; a hang realization would exercise it.
- The `a5` `plugin_rc0` arm likewise (0/2 author realizations; scout
  sampled it once pre-correction).
- Re-link latency finer than the 0.2 s sample quantum is the
  boundary's domain (19–57 ms); the fixture's armed bound is 0.8 s —
  deliberately an envelope, not a pin.
- `ffmpeg -sinks pulse` `*` provenance remains unverified (mechanism
  unknown; `agree` recorded twice).
- `pactl list sink-inputs` attribution is deliberately unused —
  object-id/client-pid joins only (the scout's own caveat, §11).
