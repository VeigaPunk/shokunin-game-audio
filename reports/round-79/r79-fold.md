# r79 fold — corrections applied, verified on the folded bytes

Verification: run D on the folded tree — **exit 0, `failures {}`**,
receipt `corpus/live/runs/20261015T084630169601Z-capture-r79/` +
copy `corpus/live/r79-fold-verify/r79-runD.stdout.json`. The folded
fixture is the simplifier's proven vfold (16 folds, +70/−112, strict
0+0 leaf equality over 23k-leaf adjacent pairs at pinned pid residue)
plus the critic/verifier corrections below — all verified live in run D.

## Simplifier vfold (applied)

`control 4ee754b3 -> cand a174739b` applied verbatim onto the
critic-corrected tree (28/28 hunks, zero rejects): dead stores and
bindings removed, the 15 named coverage-block sites single-sourced to
`_loopback_r79_block`, the two inline watch unions to
`_loopback_r79_union`, vacuous ternary/parameter/loop removed, two
contradictory latency comments corrected. Preserved: every leaf, gate,
failure string, class, and the frozen r76/r77/r78 arms.

## Critic C1–C7 (applied)

- C1: `capture_default_source_unnegotiated` gate tightened — the `or`
  let a once-per-run probe constant excuse a leg whose own oracle saw
  a live source. Now BOTH conjuncts required: per-leg `source_meta`
  absent AND the run-level probe unavailable.
- C2: tap-provenance precedence — `(B & O) | I` made ANY non-empty
  input-producer set kill the unattributed confound. Corrected to
  `B & (O | I)`; a tap bound off-target now marks the confound.
- C3: foreign-tone excuse is now ORIGIN-gated, not amplitude-gated —
  requires a producer on the leg's capture path carrying none of this
  run's `r79lb_`/`r79fc_` tags; the >8192 peak stays as corroboration.
  No foreign producer -> unexplained contamination FAILS.
- C7: formal positive leg `b13_nullsource_law` — the fallback law as a
  two-branch ASSERTION (`linked` when a live source answers,
  `unnegotiated` when none exists), both branches named outcomes with
  correlates. Run D measured the **unnegotiated branch** with the
  authority split live: `source_meta=None` while
  `source_pactl=alsa_input...Line__source`.
- C4–C6: report-level — `stream.capture.sink` claim falsified (present
  in shipped `libpipewire-module-protocol-simple(7)`); "no default
  source" bound to the metadata/wpctl authority vs pactl enumeration;
  `foreign_tone_on_shared_monitor` marked named-but-unexecuted.

## Verifier A1–A7 (applied)

- A2: never-fed legs with an unattributed tap now emit the named
  outcome `content_pin_unmeasured` — the no-`mine` verdict asserts an
  unmeasured surface rather than crediting it. Fired 6x in run D.
- A1: the r78 `wait_source` defect confirmed durable-pre-existing
  (05:50Z onward, pristine-HEAD proof) — queued for the r80 author,
  not silently relaxed here.

## Boundary classes (recorded for the adjudicator)

Both-sides-fallback pair loop (the arm only ever falls back one side
at a time), kill-teardown atomicity <25 ms with orphan-consumer
survival, freeze outcome reconfiguration-dependent (14/20 vs 6/20),
two-loopback cycle recirculation (~983 flat burst), spawn-time
self-reference unresolved, same-sink comb resonator self-sustaining
2.5 s at rail 32768. All host-bounded; none falsifies a pinned claim —
the threatened legs (b09, c03-c06, d2a, e-legs) keep their correlates.
