# Adjudicator report — round 89 (pw-profiler output lattice)

DECISION: **ADMIT-with-findings**, landing closed at `5755be5b` (r89
foldfix commit); chain: author `f1ef7071` -> foldfix `5755be5b`.

Gate history: verifier GATE FAIL at `0cbbb3bb` (1464/1484, x_top/x_foot/
g_hup arm classes) -> foldfix landed sigreset preexec_fn on all arm
children, own-scoped x_foot census, x_top real-row guard, 52-leg count
correction -> **re-verifier GATE PASS** on `5755be5b` (867/888 cells,
0 FAIL, 21 named coverage_blocked; all 20 baseline reds re-derive green
or named; revert-the-fix mutants red as designed — g_hup is causal).

Wave-B on the original landing: critic GATE FAIL as a reproducible
green landing — PASS on every encoded law (8/8 arm replay, 254
mutations behaved, schema/suspension/xw all hold) but correctly named
the three execution-mode classes the foldfix repaired; reviewer
PASS-wf (F1 SIGHUP inheritance 2-seat convergent — the foldfix
mechanism); simplifier PASS net -11 proven (queued, composes with r88
fold); scribe custody INTACT (222/222 re-derivations, no falsified
measurement — ADJ-1..6 are arithmetic/prose nits, folded).

Encodings that survived: -n exact-N gating, 4096 B stream blocks,
INT/TERM-graceful vs KILL-truncating classes, SIGKILL 49152 B
incremental write, schema invariants, suspension 21->0, xw witnesses.

Fold queue:
1. Simplifier -11 proven (composes with the r88 fold) — dedicated fold
   round, never inside an author landing.
2. Scribe ADJ-1..6: headline leg-count arithmetic (52 real vs 51
   headers vs 47 claimed — the foldfix corrected to 52), run-2-only
   provenance figure, modules_delta witness naming.
3. Re-verifier residual honesty notes: x_foot armed 2/8 (rest named
   coverage_blocked under load), x_top 4/8 blocked co-tenanted —
   these are coverage classes, not failures; revisit only if the
   bracket can be widened without weakening the arm.
4. Inherited: tree-relative family lock (r86-r89 F-class); receipt-
   level laws cannot catch fully self-consistent rewrites (live
   battery + pin remains ground truth).

Adjudicated by the lane orchestrator after the foldfix + re-verifier
closed the gate at `5755be5b`.
