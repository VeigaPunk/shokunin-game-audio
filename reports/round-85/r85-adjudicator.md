# Adjudicator report — round 85 (pactl / monstreams leg lattice)

DECISION: **ADMIT-with-findings** on `2a49d540`. 87 legs / 5 entries; verifier VERIFIED on a
frozen git-archive replay (87/87 x2, 101-law checker clean); critic ADMIT-w-f; reviewer PASS;
simplifier PASS (-22 queued); scribe INTACT w/ citation defects + one gate defect.

The three host-bimodal realizations are pinned either-way and sustained under attack — EXCEPT:

Fold queue:
1. cdup_cap is NOT armed both ways (scribe ADJ-3 + critic F1 + simplifier, 3-seat consensus):
   name_shadow_bound absorbs a foreign capture_* bind — no out_node constraint. Fix or re-scope.
2. Numeric node.name aborts the run (reviewer F1 + verifier F1 carried, 2-seat): TypeError in
   _alsapw_r84_cands / _playback_r78_node_names; family plants such names itself. Add a
   non-string guard.
3. Arm-looseness cluster (critic F2/F3): connect-kill accepts module-never-loaded; mixdup/
   mixdelay/mixinv bound only the upper side (ratio 1.0 + 1/8-tap signature pass).
4. sd_prop vacuous corner: dead-trap + no-links accepted as bind_killed_then_default; needs an
   explicit dead_unbound realization.
5. TMPDIR-scoped family lock (carried from r84, still unfixed — r86 author instructed to use
   fixed-path lock).
6. Citation defects (scribe ADJ-1/2): two uncited executions incl. one RED (strong-form arms
   failed on-host — that IS the either-way justification; disclose them in the fold report).
7. Simplifier patch net -22 (T1-T14) unapplied.
