# r85 author — pactl name/serial addressing + monitor-stream lattice (`--probe-pactlmon-r85`)

Seat: `ufo-executor` (probeParent). Authoring pass over `corpus/fixtures/measure_audio.py`.
Insertion-only: **+2178 lines, 3 modified wiring lines** (add_argument append, mutex-sum
append, mode/suffix ternary prepends — identical convention to r82/r83/r84). No prior
family touched; all `r85a_*` namespaced; nothing committed.

## Host / toolchain (as measured at run time)

- host `plazir27`, kernel Linux 7.2.3-arch1-3, loadavg **~50** throughout both runs
  (heavily contended shared host — every arm carries tag/link/graph evidence rather
  than timing assumptions; several boundary claims turned out to be load-realization
  dependent and are encoded as recorded realizations, see below)
- PipeWire 1.6.8, WirePlumber 0.5.17, pactl/libpulse 17.0-98-gb096 (protocol 35),
  python 3.14.7, numpy 2.5.3, aplay/parec/pw-record/pw-link/pw-cli/pw-dump all present
- `TMPDIR=/home/vgpnk/Projects/shokunin/tmp` for all runs (`/tmp` quota — known
  environmental constraint)

## Entries (5) and legs (87 total)

| entry | legs | content |
|---|---|---|
| `pactlmon_addr_r85_probe` | 40 | get-sink-volume arg lattice ×19 (name/serial/object.id/@DEFAULT_*/`.monitor`/bogus/huge/neg/`""`/`0`/parse edges + the bimodal `0<digits>` row) + get-source-volume class ×8 (`.monitor` name + sink-serial share the monitor's volume) + pw-cli id↔serial inversion ×2 (id resolves; serial → rc0 `unknown global` lie shape) + move-sink-input name/serial/bogus ×3 + **name/serial collision** (sink literally named with ns's serial — pactl move still lands on the serial holder; pw-record `--target <digits>` measured `serial_monitor_bypass` on this host, recorded) + serial monotonicity ×3 (`serials` strictly increasing across unload/reload; module index recycled identically ×3) |
| `pactlmon_mix_r85_probe` | 7 | N-streams-one-sink mixing on own sink with the **boundary's §2.1 protocol folded in**: tap link-validated before any player + same-run solo reference (measured `l_a=r_b=8190.7 ≈ 8192`, zero bleed) — `solo`, `mix2` (4 links → 2 playback_* ports, each tone full-amp, zero cross-channel bleed), `mixdup`/`mixdelay` (coherent-sum **realizations** recorded; armed only the linear bound ≤2.05× — see §4), `mixinv` (phase-pair realization), `mixclip` (peak at the s16 rail, clipped-frame fraction envelope, clip-product spur >300) |
| `pactlmon_aplayenv_r85_probe` | 6 | aplay `-D pipewire` env surface — `PIPEWIRE_NODE=<ns>` and `PIPEWIRE_PROPS='{ target.object=<ns> }'` both publish + link the named sink; conflict → **props win**; numeric serial inside props resolves (publishes int `target.object`, consumers = the sink name); bogus NODE → silent default fallback measured with a **SILENCE** file; no-env control — silence only, no tag tone ever reaches the shared sink |
| `pactlmon_capture_r85_probe` | 17 | the capture-side monitor/source surface — `cap_baseline` (remap source carries the feeder tone, peak 8192) + the boundary-corrected `--target` lattice ×7 (source name/serial/**object.id** all bind `capture_*`; sink serial noprop bypasses to `monitor_*`; sink name **never** links `monitor_*` — `bound_source` realization on this host; prop+sink-name → own monitor; prop+source-name → **default** monitor) + the loss law ×3 (links die, never re-form, stream alive, growth ceases, post-loss bytes bounded ≤8 quanta — the in-flight flush, see §4) + prop-form loss → default monitor re-link + the Audio/Source self-destruct ladder ×4 (idle survives ≥3.6 s; pw-record/parec bind kills module+node at **0.08–0.09 s**; manual `pw-link` never kills; prop form → default monitor with module fate recorded) + `latebind` (see §4) |
| `pactlmon_negctl_r85_probe` | 17 | classifier unit table ×13 (named classes incl. the two r85-local ones `pa_invalid_arg`, `pwcli_unknown_global`; must-classify-nothing: empty/volume-chatter/segv-words/`Recording WAVE` + `Unknown PCM` still reachable through the r84 chain) + live no-error controls (`pactl info`, `pw-dump`, live `pw-cli` unknown-global) + the SIGKILL-vs-refusal discriminator |

## Encoded laws (boundary-surviving, as corrected)

1. **pactl numbers are object.serial, never object.id.** `get-sink-volume <oid>`
   → rc1 `pa_get_info_noent`; `<serial>`/name/`@DEFAULT_SINK@` → rc0 identical
   volume row. `pw-cli` inverts the namespace (id resolves, serial → rc0 +
   `unknown global '<n>'` — a rc-0 lie, classified `pwcli_unknown_global`).
2. **Verbs are typed.** `@DEFAULT_SOURCE@`/`@DEFAULT_MONITOR@`/`<name>.monitor`
   refuse as sink args; `<name>.monitor` and the sink's own serial resolve on
   get-source-volume (the monitor source shares the sink's serial).
3. **`""` is a distinct refusal** (`Operation failed: Invalid argument`,
   new class `pa_invalid_arg`) — not `No such entity`.
4. **`0` resolves to the LIVE default** — the boundary's resolution of the
   scout's ambiguous row; armed by comparing the `0` volume row to
   `@DEFAULT_SINK@`'s in the same run.
5. **Numeric parse edges**: ` <ser>`, `+<ser>`, `<ser>.0`, `<ser>x`, `0x<hex>`
   all parse; a `_`-grouped serial refuses. The `0<digits>` row is **recorded
   only** — the boundary measured rc0/rc1 across windows; this host measured
   rc1 `pa_get_info_noent` ×2.
6. **Serials are monotonic** (235347→235361→235375 / 236361→236375→236389 —
   strictly increasing, never recycled); the module INDEX is recycled
   (536870916 identical ×3) — recorded, never armed.
7. **Collision law**: pactl's numeric arg is serial-first — a sink named
   `<digits>` cannot shadow `move-sink-input … <digits>` (lands on the serial
   holder, both runs).
8. **--target lattice** (boundary-corrected): source name/serial/object.id →
   `capture_*` (the scout's object.id stall is falsified — measured binding
   on this host ×2); sink serial noprop → `monitor_*` (numeric bypass); sink
   name noprop → **never** `monitor_*` (realization recorded: this host bound
   the live remap source's `capture_*`, the boundary's arbitrary-source
   realization — refusal also observed in recon); prop+sink-name → own
   `monitor_*`; prop+source-name → the DEFAULT monitor, never the named
   source.
9. **Loss law (folded falsification 15)**: name-verified unload mid-record →
   links die, never re-form, process alive, growth ceases, post-loss bytes
   bounded ≤8 quanta. Prop form re-links to the default monitor.
10. **Audio/Source self-destruct**: idle ≥3.6 s survives; pw-record/parec bind
    kills module+node at 0.08–0.09 s; manual `pw-link` never kills (survived
    1.2 s + alive witness); prop form lands on the default monitor.
11. **Mixing**: 4 links → the sink's 2 `playback_*` ports; each tone full-amp,
    zero bleed (armed on the validated tap + same-run solo reference); the
    2-stream sum is bounded-coherent (≤2.05× — phase realizations recorded);
    over-FS sum hard-clips at the tap (peak ≥32767, rail-frac ∈ [0.08,0.60],
    spur >300 — phase-dependent amplitudes never pinned).
12. **aplay env**: `PIPEWIRE_NODE`/`PIPEWIRE_PROPS target.object` both publish
    + link the named sink; on conflict **props win**; serial-in-props resolves;
    bogus NODE publishes the bogus target.object but silently falls to the
    live default (measured on silence files only).

## Falsifications NOT encoded (boundary's 3 + 1 vacuity pair, folded)

- The scout's universal **carry-input-codec** rule (WAV→OGG succeeded) — the
  sndfile surface is out of this family's scope entirely.
- **OGG "one byte"** — differs at serial + CRC bytes; not encoded.
- **Unknown-extension universality** — varies; not encoded.
- **Deterministic sustained-zeros capture** after source loss — replaced by
  the folded loss law: bounded flush allowed, growth must cease, links must
  never re-form; the froze/zeros/flushed-content shape is recorded, not armed.
- The two vacuous measurements (bare amplitude without a validated tap; the
  s3d unverifiable unload) — avoided structurally: every amplitude arm runs
  behind `_pactlmon_r85_wait_tap_link` + a same-run solo reference, and every
  module lookup matches the module's OWN `sink_name=`/`source_name=` arg
  (the scout's `mod_index()` grepped sink_name only, which is why its remap
  unloads never fired — `_pactlmon_r85_module_index` takes the field name).

## Author-discovered host variances (realizations recorded, narrower arms)

The heavy load (~50) exposed three **boundary-vs-authoring-host realizations**
that falsify the boundary's strong forms — encoded as recorded fates with
invariant arms only:

1. **`latebind`: the late source DID bind** (both runs — links to
   `r85a_late:capture_*`, file grew 44→483 kB). The boundary measured never-
   re-arm 6/6; on this host WirePlumber re-targets the stalled record. Arm:
   any link must land on the LATE source's own `capture_*` ports (never a
   monitor, never foreign). Fate class `late_bound` recorded.
2. **`cdup_cap`: serial-bypass, not name-shadow** — pw-cat's `--target <digits>`
   resolved the digits as a SERIAL on this host (links → `ns:monitor_*`,
   consistent with the `t_sinkserial` law); the boundary's host resolved
   name-first (never a monitor). Arm: any monitor link must land on the
   serial holder's monitor. Fate `serial_monitor_bypass` recorded.
3. **`sd_prop`: transient bind-kill-fallback** — the prop record briefly
   name-bound the trap (killing it at bind latency) before the prop steered
   to the default monitor; boundary measured the clean fallback. Arm: links
   must land on the default monitor; module fate recorded
   (`bind_killed_then_default` ×2).
4. **In-flight flush**: a dying remap source can append one bounded quantum
   of real content post-loss (2048 frames measured ×3 legs, then growth
   ceases — `grew_content`/`froze` both recorded); the boundary froze 6/6.
   Arm: `post_frames ≤ 16384` AND last-two-samples equal size AND no re-link.
5. **Coherent-sum slip**: `mixdup` measured coherent_2x (ratio 2.0, run1) and
   partial (0.259, run2); `mixdelay` partial (0.226) / cancelled (0.025);
   `mixinv` slipped (1.87/1.85) — under ~50 load the negotiation-quantum
   phase alignment is a realization, not a law. Arm: the linear bound
   `ratio ≤ 2.05` only.
6. **pw-record exits rc=1 on its SIGTERM handler** — realizations classify
   on links + liveness, never on the bare exit code (a bound+SIGTERM'd
   record reads rc=1).

## Guards inherited (verbatim conventions)

- `r85a_<pid>` namespace on every name (`ns`, `ns2`, `mix`, `tone`, `vsrc`,
  `vsrcb`, `sd`, `late`, `cyc`, stream/node tags); `media.role =
  r85arole<pid>` private restore key (never shared `music`).
- `_pactlmon_r85_family_lock` — `measure_audio-pactlmon-r85.lock` flock held
  to exit (two concurrent runs would cross-credit taps + contest the
  collision/cycle sinks).
- Name-verified teardown: `_pactlmon_r85_unload_own` re-reads the module
  table immediately before firing, matches the module's OWN
  `sink_name=`/`source_name=` arg exactly (field taken explicitly — the
  scout's vacuity cause), never fires a stale index; witnesses `sinks_gone`
  + `sources_gone` + `own_nodes_after` per entry, all clean both runs.
- Bounded process groups (`start_new_session` + killpg SIGTERM→SIGKILL);
  taps bounded by `-n` AND link-validated; tag tones fail-closed to
  probe-owned sinks — the only shared-sink landings are the aplay SILENCE
  fallback legs and the prop-form default-monitor capture arms (measured
  surfaces, recorded).
- The feeder pw-play is killed before the tone-sink loss leg so the r78
  default-fallback can never land a tag tone on the shared sink.
- Family-local error classes checked before the r84 chain; never prepended
  into `_CAPTURE_ERR_CLASSES`.

## Green receipts (identical source bytes, two runs)

- `corpus/live/r85-author/runs/run1/measurements.json`
  (canon `corpus/live/runs/20261016T061227150495Z-pactlmon-r85/measurements.json`)
- `corpus/live/r85-author/runs/run2/measurements.json`
  (canon `corpus/live/runs/20261016T061417931113Z-pactlmon-r85/measurements.json`)
- source `sha256` both runs: `714564a32141f134f849401dd029e1e10c4aa19bb848a43fd50f70a251499ee2`

Both: `failures: {}` across all five entries, no `blocked` / `coverage_blocked`,
`own_nodes_after: []`, all `sinks_gone`/`sources_gone` true, zero r85a-owned
residue on the live host. Leg names + error classes + exit codes + realization
tags are stable across the two runs **except** the documented phase/coherence
realizations (`mixdup` coherent_2x↔partial, `mixdelay` partial↔cancelled) —
exactly the volatile surface the boundary warned about; every *armed* verdict
is identical. (Per family convention the whole-receipt bytes differ only in
volatile fields — pid, tmp paths, wall times, loadavg, object ids — the
identical-bytes requirement applies to the source implementation.)

Measured headline values (run2): solo ref `l_a=r_b=8190.7` (validated tap,
no 1/8 hazard); mixdup ratio 0.259 `partial`; mixinv residual 1.85 `slipped`;
mixclip peak 32768, rail_frac 0.2325, spur 1921; serials 236361→236375→236389
(monotonic; module idx 536870916 recycled ×3); `g_lead0` rc1 `pa_get_info_noent`;
cdup `serial_monitor_bypass`; t_sinkname `bound_source`; cap_loss posts
`grew_content` 2048f / `grew_content` 2048f (bounded flush, growth ceased);
cap_loss_prop → default monitor; sd deaths 0.08 s/0.09 s; latebind `late_bound`.

## Blockers

None. Remaining risks: (a) three boundary claims came out host-bimodal under
~50 load — they are encoded as recorded realizations with invariant arms, so a
low-load verifier host may realize the OTHER side (all sides armed); (b) the
`0<digits>` pactl row stays record-only (boundary itself was bimodal there);
(c) `t_sinkname` noprop remains the least-stable row — armed only on the
never-monitor invariant.

## Files changed

- `corpus/fixtures/measure_audio.py` — +2178/−3 (family block before `main()`,
  5 entries, helpers, constants; wiring: add_argument, mutex sum, dispatch,
  mode, suffix)
- `corpus/live/r85-author/runs/run{1,2}/measurements.json` — green receipts
- `reports/round-85/r85-author.md` — this report
