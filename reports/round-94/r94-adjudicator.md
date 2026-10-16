# Adjudicator report — round 94 (SoX_ng effect/DSP lattice)

DECISION: **ADMIT-with-findings** on `aaf56d30` (merge of wt-r94
`f46dce00`). 8 entries / 150 legs, +2231/-3 insertion-only — the lane's
largest single landing.

Gates: verifier **PASS on the committed merged bytes** (frozen
`aaf56d30` archive, 2/2 green fresh runs on `4808c4cf`, 253 laws x 6 =
1518 cells re-derived, 83/83 independent live probe, forgery suite
11/11, gate mutants detected — closing the merged-artifact gap both
scribe and reviewer flagged); reviewer PASS-wf (88 own-checks, 50/150
legs re-derived, witnesses live both directions); critic PASS-wf
(mutants/laws live, boundary corrections all at corrected values);
scribe PASS-with-gap (receipts in worktree — resolved by verifier's
committed-bytes runs); simplifier PASS (23 proven folds variant A /
26 variant B — queued, not landed).

Encodings that survived: auto-dither precision-tracking law (default
s16 nondeterministic; -D fixes; s24/s32 suppress; explicit dither needs
-R; -D -R == -R); gain/vol rounding split (nearest vs ceil — vol 0.5 !=
vol -6.0206d by 1 LSB); resampler +/-1-frame law with the boundary-
CORRECTED alias lattice (scout's -130 dB claim falsified and disarmed
at measured values; -q hazard at -6.289); remix select-vs-downmix;
fade stop-truncation + 100 dB log law; repeat/pad/silence window law;
dither envelope 21 LSB / RMS 5.740681.

Fold queue:
1. **Critic F8 — census negative control is FAIL-OPEN** (unreadable
   recorded but never armed; `own_objects: []` can pass measuring
   nothing; reproduced live under a stalled daemon). Route
   `cen["unreadable"]` to coverage_blocked or arm it — highest-priority
   fold item.
2. Simplifier variants A (-15, 23 folds: first8_ints/fmt_tag -19.2%
   receipt payload, entailed arm, dead bindings) and B (-19, adds
   leg-dedup of identical-sha laws) — apply decision; both diffs
   re-apply to current HEAD.
3. Critic F1/F2/F4/F6/F7 report-correctness + hygiene: dev-receipt
   count (4 green not 5-with-failures), print both impl shas, norm
   before error_hit, witness call-site vs comparison counts, tighten
   nondeterminism envelopes >=4/>=8.
4. Critic F3 + simplifier A3 — the orphan `alias_20k_v` leg: measured
   but never armed; arm |band|<1.5 or drop (both seats converged).
5. Reviewer LOW: `gain 12` count dither-invariance note; reporter's
   receipt->bytes binding gap (no fixture-sha field in receipts —
   family-wide convention gap, fold spec: add impl sha to receipt).
6. Simplifier hazard: pactl census under stalled pipewire-pulse can
   turn a 5 s pass into >8 min — degrades correctly; r96 census arm
   should bound it.

Adjudicated by the lane orchestrator; wave-B reports land in this
commit.
