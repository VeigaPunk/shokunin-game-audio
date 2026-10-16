# Adjudicator report — round 84 (pactl / monitor-tap lattice)

DECISION: **ADMIT-with-findings** on `fbe65713`. 147 legs / 6 entries; verifier VERIFIED on a
frozen git-archive replay (147/147, gain laws exact); reviewer PASS; critic ADMIT-w-f; simplifier
PASS (net −7 queued); scribe INTACT w/ citation defects.

Fold queue (all latent, none blocking the landing):
1. F1 (3-seat consensus: verifier+critic+reviewer): family lock is TMPDIR-scoped — same-family
   runs across different TMPDIRs race and cross-credit foreign node names. Fix: fixed-path lock
   outside $TMPDIR or foreign `r84a_*` precondition.
2. F2 (critic, live-proven): `vol_neg` recorded value never read — one-assertion fix.
3. F3 (critic): no absolute base floor on `vol_150`/`vol_25_idx`/`vol_0_100`/`mute_cycle`.
4. F2 (reviewer): sticky-pin median window 0.8–3.2 s spans the 2.0 s repair — narrow to 0.8–1.9 s.
5. Report-citation corrections (scribe ADJ-1..3, reviewer F4): loadavg claim, leg counts,
   failures-type wording — text fixes only.
6. Simplifier patch (net −7, T1–T10) unapplied — fold with next writer.
