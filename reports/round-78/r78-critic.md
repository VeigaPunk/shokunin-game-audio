# R78 CRITIC (audio) — adversarial gate review of `d9aa6f9`

Seat: **CRITIC**. Scope: `corpus/fixtures/measure_audio.py` @ `d9aa6f9`
(`--probe-capture-r78`, 8 entries / 60+ legs) against receipt
`corpus/live/runs/20261014T221945369366Z-capture-r78/measurements.json`.
Method: re-implemented every entry's failure predicates as a pure replay over
the recorded legs (`corpus/live/r78-critic/replay_gates.py`), then mutated the
recorded evidence and re-ran the gates. **Read-only on tracked files.**

## Replay verdict

All 8 entries replay to `failures: []` — the recorded evidence does satisfy
the coded gates; the `failures:{}` headline is internally consistent, not
self-printed. Diff claim verified: 3 rewritten lines are the prepend-only
sum/mode/suffix ternaries; all r78 symbols are new; r77's
`_capture_r77_node_props` is untouched.

The armed core held under mutation: wrong-sink routing (M10), third-node
post-move consumers (M11), segv rc≠−11 (M12), post-gap audio in the zeros
window (M13), honored payload on a `--fix-*` wav leg (M14) are all caught.
Boundary's `late_bind_retarget`, `dup_name_lowest_serial_wins`,
`move_revives_unlinked` and `default_metadata_triple_divergence` would all
surface as consumer-set mismatches → **fail-closed**, not forged passes.

## Finding 1 (strongest — receipt-demonstrated): monitor-tap provenance is not bound

The `nofollow` leg's own receipt contradicts its tap label:

- Topology samples: `r78fol_nofollow` consumes `[r78_def_sink_844895]` at
  t=1.0, then `[…SPDIF__sink]` at t=2.6 and t=4.0 — zero links to `s_new`
  after ~2.1 s (`pw-link -l` ports enumerated exhaustively).
- The tap filed as `"target": "r78_def_sink_844895"` records `mine` (the
  1 kHz/1.5 kHz @ 8192 tag tone) continuously 2.1→5.5 s — i.e., after the
  stream demonstrably left `s_new`, the "s_new monitor tap" kept recording
  exactly the moved stream's content until EOF (tone stops at 5.5 = 5.1 s
  stream-time = file end).

The tap re-bound — either the tap rode the default (it was spawned while
`s_new` *was* `default.audio.sink`, and followed the restore to SPDIF), or
capture-side re-resolution pulled it to the content-bearing monitor
(boundary §8.4 measured capture-side late-bind; §9 confesses the same
defected-witness wart). Mechanism aside, **the receipt itself proves a tap
wav is not provenance-bound to `tap.target`**: the file carries no evidence
of which node it measured.

Consequence: every `carries_tone`/`mine_windows` pin is only as strong as
the tap's binding. A tap that migrates *with* the audio launders a positive
pin (M-measured: this receipt's tap did exactly that); a tap that migrates
*off* the tone-bearing node forges a negative pin (`mine_windows == 0`). On
this receipt the only migrated tap was recorded-not-asserted, so no verdict
was laundered — but the same gate shape drives every positive pin in the
lattice, props, plugin and loss-relink legs, and every negative pin in
`target_0`/`tap_default`.

**Impacted axes:** evidence integrity, host fidelity. **Smallest fix:**
sample `_playback_r78_producers(<tap tag>)` once per leg and require the
tap's producer == `tap_target`'s monitor ports (or record `tap_bound_to`
and fail on divergence). Cheap: one `pw-link -l` parse already exists per
sample.

## Finding 2: `arecord_constrain`'s named class is recorded, not asserted (r77 wound, live)

`legs["arecord_constrain"]` gates on `exit_code != 0` alone; `error_class`
is stored but never asserted. M5 shows the pair passes with
`acls == "alsa_busy"` — and `arecord_honored` failure is *excused* iff
`acls == "alsa_busy"`. Under a lingering device lock (the busiest failure
mode on this host — `contention.aplay=1` on every entry) the whole
`aplay_converts_arecord_constrains` half-verdict is vacuous. The receipt
happens to record `alsa_sample_format` (stderr lists `S16_LE`,`S24_3LE` —
honest data, unarmed gate).

**Fix:** assert `acls == "alsa_sample_format"`; on `alsa_busy` classify the
pair `contended`, never pass/fail.

## Finding 3: six demonstrated forge/vacuity holes (mutation-proven)

| ID | mutation | gate result |
| --- | --- | --- |
| M2 | `target_0` tap dead/missing | **PASSES** — negative pins (`mine_windows` falsy) never require the tap to have run |
| M3 | `monitor_name` consumers = `{source_peer}` only, no peer tap | **PASSES** — `carries_tone` is required only when the *default* is in the union; a peer-only landing has zero content verification |
| M4 | `consumer_unlink`/`producer_unlink` = `{}` | **PASSES** — `if a:`/`if b:` skip all checks; contrast the lattice's leg-absent→failure (inconsistent arming of the same contract) |
| M6 | `boundary_source` publishes no ports/node | **PASSES** — asserts only killed+no-consumers; the "published but unlinked" half is unproven (lattice/props stall legs *do* assert ≥2 ports — this twin doesn't; the receipt's own `capture_FL/FR` ports show the data exists unasserted) |
| M7 | `still_probe` unlinked at every sample | **PASSES** — `[] ⊆ allowed` admits a transitional stream that linked to nothing |
| M9 | fallback leg consumers = `[want, foreign_extra]` | **PASSES** as recorded `confound`, not failure — an extra unclaimed consumer never fails a leg |

Plus the structural standing holes: a lattice leg `{"blocked": …}` is
skipped silently (declared policy, but coverage shrinks without a signal —
"the table is the coverage contract" fires only for *absent* legs), and an
entry-level `blocked` early-return lands `failures: []` — indistinguishable
from pass in the top-level `failed` dict.

**Fixes:** require `tap.exists and windows` before accepting a negative
tone pin; leg-absent *and* leg-blocked → coverage note in `failures` or a
named `coverage_gaps` list the adjudicator reads; port/state assertions on
`boundary_source`; transitional `[]` → distinct class; `want`+foreign-extra
→ failure (or a `confound_extra_consumer` named failure, not silent pass).

## Finding 4: `alsa_busy` attribution unverified (pcm_stolen_silent_success crossover)

`busy_under_witness`/`retention_1s` attribute EBUSY to our monitor tap
holding the PCM — but the witness tap is never itself witnessed: no link
sample of `r78aplay_wit_tap`'s producers, its output file never read
(no `tap` key on the leg at all). `contention.aplay=1` was live through the
run; a foreign (or stale) holder of `hw:0,0` produces `alsa_busy`
identically — the causal claim passes whether or not the witness worked.
**Fix:** sample the tap's producer link during the busy window.

## Exploit-map coverage (brief's list)

- `pcm_stolen_silent_success`: lattice pins are graph+monitor level —
  physical-steal is invisible *and* declared out of scope (author §9);
  crossover lands on Finding 4 (EBUSY attribution), where it does matter.
- `default_metadata_triple_divergence`: `want` re-read via pactl per leg;
  divergence → consumer mismatch → fail-closed (false-negative risk only).
- `late_bind_retarget`/`dup_name_lowest_serial_wins`: a materialized/earlier
  same-named node appears in `consumers_union` → fail-closed.
- `move_revives_unlinked`: would surface as non-empty post consumers →
  fail-closed; the cell correctly claims only "no re-link this run".
- `suspend_advisory_wakeup`: zeros-at-rate on a suspended tap can't forge a
  `mine` window (fail-closed on positive pins); on negative pins it's
  absorbed by Finding 3/M2.
- `class_segv_consumer_partition`: landed claims are pw-play-scoped; the
  extended partition (pw-record stall, paplay conn-term, Midi sub-class
  plays, case-variant stalls) contradicts nothing but bounds the class's
  generality — coverage gap, not a defect.
- `aplay_file_fmt_refusal`: `convert_float` is `-f`-flag-scoped, matching
  boundary's scoping; the *file-fmt* refusal direction on `hw:` is never
  armed (coverage gap only).

## Record-not-asserted / prose deltas (r77-wound audit)

- `monitor_target_source_peer`: `landed_peer=false` on this receipt — the
  leg landed default-only; the racy-peer half rests on dev runs, honestly
  recorded but **not demonstrated by the final receipt**.
- `nofollow.tap`: recorded-not-asserted (by design) — and per Finding 1 its
  content measured SPDIF, not its labeled target.
- segv "wall ~2.01 s": `live:false` at t=0.7 — the crash is <0.7 s; wall is
  the event-schedule artifact and the <4.0 gate bounds nothing about crash
  timing.
- aplay envelope: positive `S32_LE∈playback` never asserted (only
  "not-both"); the channels check is skipped entirely if either
  `--dump-hw-params` parse fails.
- Author report says "+2401/−3"; git records +2404/−3 — trivial.

## Smallest safe correction set

1. Tap-provenance sample (`tap_bound_to` assert) — kills Finding 1 and most
   of M2/M3's surface.
2. `acls == "alsa_sample_format"` assert + `contended` class on `alsa_busy`.
3. Leg-absent and leg-blocked → named coverage failures (all entries).
4. `boundary_source` ports/suspended asserts; `still_probe` non-empty-or-
   named-class; negative pins require live tap evidence.
5. Witness-tap producer link check on the busy/retention legs.

None require new machinery — all reuse `_playback_r78_*` helpers already in
the diff. Everything else about the lattice's central claim (ungated
fallback, consumers+content double witness, intent-vs-consumption leaf) is
armed and replayed clean.
