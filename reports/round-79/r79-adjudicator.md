# r79 adjudicator — ADMIT-corr

## Verdict: ADMIT-corr

The pw-loopback -C/-P binding frontier lands 66 legs over eight
entries with all wave-B corrections applied and verified on the folded
bytes (run D: exit 0, zero failures, all correlates live).

## Receipts

- Author: B/C formal runs green (frozen artifact sha in
  `corpus/live/r79-author/frozen-artifact.txt`), +2779 lines.
- Verifier: independent V1/V2 replays green; 681 verdict-bearing keys
  byte-stable across B/C/V1/V2 modulo pid tags; two receipted
  forge-kills (F-union, F-tap) fail closed.
- Fold: run D on vfold+corrections — green; b13's unnegotiated branch
  measured formally (first positive instance of the fallback law);
  `content_pin_unmeasured` named 6x on vacuous taps.

## Findings disposition

| finding | disposition |
|---|---|
| critic C1 (constant source gate) | FIXED — conjunct gate, verified |
| critic C2 (tap precedence) | FIXED — `B & (O \| I)`, verified |
| critic C3 (amplitude excuse) | FIXED — origin witness required |
| critic C4-C6 (report claims) | FIXED — falsified man-page claim corrected; authority wording bound; unexecuted class marked |
| critic C7 (no positive instance) | FIXED — b13 two-branch leg; unnegotiated branch measured |
| verifier A1 (r78 wait_source defect) | DISCLOSED pre-existing; queued r80 |
| verifier A2 (vacuous content pin) | FIXED — named outcome |
| verifier A3-A7 (jitter/warts/foreign leaks) | noted, non-blocking |
| simplifier 16 folds | APPLIED — strict 0+0 leaf proof |
| scribe F1-F11 | applied (F1 unexecuted mark, F2 man-page falsification, F4 r78 durable defect) |
| boundary 7 classes | recorded host-bounded; no pinned claim falsified; falsification list filed |

## Pre-existing defects carried (not r79 regressions)

- r78 `_playback_r78_wait_source` can never confirm a null-sink
  monitor on this host (ports are sink-owned `<sink>:monitor_*`) —
  two r78 capture arms silently `coverage_blocked` since 05:50Z.
  Proven on the pristine HEAD module by the verifier. Owner: r80.

## Authority note

`source_meta` (default.audio.source metadata / wpctl marker) and
`source_pactl` (pactl enumeration) are DIFFERENT authorities and
diverged live in run D (meta None / pactl Line source). All
default-source gates use the metadata authority per leg; the report's
wording is bound accordingly.
