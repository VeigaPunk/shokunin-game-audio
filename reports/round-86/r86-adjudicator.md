# Adjudicator report — round 86 (pwctl tools lattice)

DECISION: **ADMIT-with-findings** on `fa5994a0`. 149 legs / 5 entries; verifier VERIFIED
(frozen replay 596/596 laws); critic ADMIT-w-f; reviewer PASS; simplifier PASS (-11 queued);
scribe INTACT, all 3 canonical runs cited.

Headline: the r84 3-seat consensus fold (TMPDIR-scoped family lock) is CLOSED — the r86 family
uses a fixed corpus/live/ path; cross-TMPDIR serialization proven by 3 independent seats
(scribe, critic, verifier: 2.0-3.5 s waits vs r85's 0.0001 s control).

Fold queue:
1. Cross-tree co-tenancy residual (critic F6 + reviewer F1 + verifier F1, 3-seat): lock is
   ROOT-relative -> frozen-tree seats don't serialize vs lane worktree; sharpest harm is a
   meta_keys_gone FALSE-FAIL from a sibling's live r86a_ key. Resolve from explicit lane root
   or accept + document.
2. Silent-skip channels (critic F1/F2 + reviewer F4): census-gap arm vacuous on empty dump;
   not-implemented matrix rows skipped when subjects fail; several legs can vanish silently.
3. Fail-open lock (reviewer F2): os.open failure => silently unlocked, no marker.
4. Simplifier patch net -11 (T1-T9) unapplied.
5. Citation nits: +1758 not +1761; line refs ~10 low; receipts carry no fixture sha.
