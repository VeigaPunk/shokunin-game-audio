# r80 fold — proven vfold + convergent wave-B corrections

Seat: parent integrator (post-wave-B). Inputs: author `+905/-3` (dead-seat
completion), baseline, scout, critic (`r80-critic.md`, no live forge —
all 10 legs replicated green ×4 — but F1–F8 real defects), verifier
(CONFIRM, 4th green run `dd40b124…`, 266 leaf keys × 4 runs, 0
non-volatile diffs), boundary (`r80-boundary.md`, read-only —
parent-persisted verbatim), simplifier (proven vfold −29 lines /
−1249 bytes, 0 meaningful receipt diffs vs all 3 base runs), scribe
(all verdict-bearing claims trace; 2 prose-cell defects).

## Applied in order

1. **Proven vfold** — `corpus/live/r80-simplifier/folded/measure_audio.py`
   diff applied clean (the simplifier's own byte-diff evidence: same
   measurements on all three prior base runs).
2. **F1 mechanism correction (critic, falsified model)** — the a1 claim
   "plain `description=` is silently dropped" was wrong at the
   mechanism level: unknown modarg keys pass through as **literal node
   props**. The verdict survives (`node.description` is the derived
   string), but the model is corrected: `description=<d>` lands as a
   plain `description` prop, while `sink_properties=device.description=`
   is the only path that moves `node.description`. Fixture comments +
   report headline/prose reworded.
3. **F2 stale-id teardown guard (critic + verifier, convergent)** —
   new `_module_r80_unload_own`: before any teardown/block re-unload it
   reads `pactl list modules short`; an absent id is skipped
   `already_unloaded`, a present id not cited by any *live*
   (client-id-carrying) `r80md_` node is skipped `foreign_risk`. This
   closes the LIFO-recycle kill-a-foreign-module window the critic
   demonstrated live. Orphan pmid citations are deliberately excluded —
   a linger orphan's stale `pulse.module.id` cannot distinguish our
   dead module from a foreign recycler (client_id is the discriminator).
   The a5 re-unload row accepts the named skips as the same law
   client-side. Run D receipt: args legs → `already_unloaded` skips
   (inline unload had already fired); topo legs → `exit_code 0` real
   unloads.
4. **F3 fail-open readers → coverage_blocked (critic)** — teardown's
   absence witnesses now use strict readers: `_capture_r77_sink_names_strict`
   returns None on pactl failure (was: `[]` → vacuous `sinks_gone`);
   `_module_r80_own_nodes` None → `own_nodes_after: "reader_error"` +
   `coverage_blocked`; t3's post-death `pw-link` read None →
   `linked_after_death: null` + `coverage_blocked` (was: `[]` → the
   "link died" claim passed vacuously).
5. **F5 t4 assertion tightening (critic)** — the sticky-move check now
   requires the dst edge **absent** `edges_before`, present at both
   post-move samples, **and** the src edge gone at both samples. Before,
   a preloaded or fan-out edge set passed.
6. **F6 block-path teardown witnesses (critic)** — `_module_r80_block`
   now records `unload_own` outcomes per tracked load; blocks are no
   longer witness-free on teardown.
7. **F7 t3 edge isolation (critic)** — t3 moved to FR ports
   (`monitor_FR`→`playback_FR`); t2 used FL. A failed t2 `teardown_d`
   can no longer alias t3's link evidence.
8. **F8 tries→loads leak guard (critic)** — any hypothetical rc=0
   `module-combine-sink` try now enters `loads` for teardown custody.
9. **F4 + scribe-F1/F2 prose (critic + scribe + verifier, triply
   convergent)** — headline column "run 2 verbatim" re-emitted from the
   actual run-2 receipt: pid marker `736128` (was run-1's `726605`),
   stale pmid `536870931` (was `536870942`), destroy id `227` (was
   `151`), tap peak `8189` (was `8137`), t1 count `49→49` (was `23→23`
   — matched NO receipt; real runs: 47→47 / 48→48 / 49→49), a5
   re-unload `rc=1 pa_no_such_entity` confirmed run-2-accurate. Also
   §4 records the ownership guard, and the module-args probe line now
   names the passthrough mechanism.
10. **Boundary B2/B3 wording** — the scout's dup-name direction and the
    "disjoint namespaces" claim were corrected in boundary's
    parent-persisted report; the enumerable-union fact (native ids 1–22
    list in pactl's module table) is now documented in
    `_module_r80_module_map`'s docstring and §4.

## Verification of the folded+corrected bytes

- Run D `20261015T161018039047Z-module-r80`: **`failures: {}`**, exit 0.
- New evidence shapes realized live: `unload_own` recorded on both
  entries (already_unloaded skips on args legs; real rc=0 unloads on
  topo probe sinks — both guard paths exercised), t3 on FR ports with
  `linked_after_death: false`, no `coverage_blocked` raised, all 10
  legs green.

## Deferred (named, not dropped)

- Boundary armed-but-unrun probes require a disposable daemon (native
  libpipewire-module index unload, `pw-link` double-link/occupied-port,
  contradictory props, out-of-range rates, orphan-slave) — correctly
  parked; this host is shared.
- Armed-unrun receipt-mining gaps noted in boundary §7.

## Provenance note

The r80 author died twice on route sweeps; its +905-line block was
salvaged complete (argparse→dispatch→naming all wired). Run D is the
fourth green run total (author ×2, verifier ×1, fold ×1).
