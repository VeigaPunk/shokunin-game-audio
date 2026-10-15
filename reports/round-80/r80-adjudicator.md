# r80 adjudicator — ADMIT-corr

Parent-integrator adjudication over the full wave ledger.

## Ledger

| seat | status | key evidence |
|---|---|---|
| author | ✓ (dead-seat salvage, complete) | +905/−3; 10 legs; receipts `134206`(disclosed failing), `134359`, parent `152510` — all `failures: {}` |
| baseline | ✓ | runs-a/b pre-state |
| scout | ✓ | module-arg lattice; §10 foreign-unload incident; re-link transient flagged unattributed |
| critic | ✓ | no live forge (10 legs ×4 green); F1–F8 defects, two material |
| verifier | ✓ CONFIRM | 4th green run; 266 leaf keys ×4 runs, 0 non-volatile diffs; hygiene held under real concurrency (sibling pid observed mid-flight, zero residue) |
| boundary | ✓ (read-only, parent-persisted) | B2 dup-name direction correction; B3 enumerable-union; armed-unrun gaps |
| simplifier | ✓ proven vfold | −29 lines, 0 receipt diffs vs 3 base runs |
| scribe | ✓ | all verdict-bearing claims trace; 2 prose-cell defects |

## Corrections folded (all convergent items resolved)

- **F1 (material, model falsified)**: `description=` is not dropped —
  it lands as a literal passthrough prop; `node.description` stays
  derived. Verdict unchanged, mechanism model corrected in fixture +
  report.
- **F2 (material, safety)**: teardown re-unloads guarded by
  `_module_r80_unload_own` — LIFO-recycled stale ids skip
  `already_unloaded`/`foreign_risk` instead of blind-firing into a
  possible foreign module. Orphan pmid citations excluded via client_id
  (the only live-vs-stale discriminator). Run D exercises both guard
  paths.
- **F3**: absence witnesses no longer fail open — strict readers +
  `coverage_blocked` on teardown sinks/nodes and t3's post-death
  `pw-link` read.
- **F4/scribe-F1/F2**: verbatim column re-emitted from run-2's actual
  receipt (pid/pmid/destroy-id/peak/count all corrected; `23→23` was
  untraceable).
- **F5–F8**: t4 both-halves edge assertions, block-path `unload_own`
  witnesses, t3 FR-port edge isolation, tries→loads leak guard.
- **B2/B3**: boundary corrections recorded (dup-name direction is a
  dict-key artifact; pactl lists native ids — union not disjoint).

## Axis verdicts

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | pactl module-lattice surface armed: 10 legs over `load-module` arg lattice (derived-vs-passthrough description, no range check on `rate`, media.class flip, linger orphan) + topology ops (`@DEFAULT_SINK@` refusal, `pw-link` linger vs `-m`, move-sink-input sticky vs dont-move no-op) |
| depth | **improved** | the linger-orphan lifecycle measured end-to-end (survives unload, stale pmid, pactl-invisible, `pw-cli destroy` only); passthrough-prop mechanism corrected against the falsified "dropped" model; stale-id hazard closed with a live-citation discriminator |
| calibration | **improved** | F1 model correction; F2 safety guard; F3 vacuity armed; verbatim column pinned to its named receipt; two bimodal-adjacent hazards (recycle window, reader fail-open) converted to named classes |

**Verdict: ADMIT-corr.** Four green runs on the final bytes (author ×2,
verifier, fold run D); every wave-B finding either folded or named.
Bounded: PipeWire 1.6.8 / libpulse 17.0 / WirePlumber 0.5.17, this
host; shared-host constraints recorded (by-name unload banned,
disposable-daemon probes parked).
