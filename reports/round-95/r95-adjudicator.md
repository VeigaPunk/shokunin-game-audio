# r95 adjudication — JACK<->PipeWire interop family

Landing: ffeb5155 (author) -> 6ba0201c (foldfix). Verdict: **ADMIT-with-findings**.

## Gate tally
- author: 5 entries / 24 legs, +1805/-3, 2 green runs (worktree bytes)
- scribe: INTACT-with-findings (block-extraction merge verbatim, +1809/-3 explained)
- critic: PASS-required-fold -> fired live: legs dropped, exit census skipped, tree-local unbounded lock, failures:[]-while-measuring-nothing
- reviewer: BLOCKED-ON-HOST (daemon wedge) + F1-F8 (overlapping classes)
- verifier: PASS on committed bytes + 2 armed-cell folds (d_metadata race, b_pw2jack band) + stdout green-on-blocked defect
- foldfix 6ba0201c: +773/-263, union landed; 3 green archive-tree runs, all negative probes named
- foldverify on 6ba0201c: every claim CONFIRMED on committed bytes (24 legs, legs on all exits, census on abort, 2.0s bounded lock, daemon-down -> 5 named blocks) except stdout cosmetic

## Findings carried forward
- CF1 stdout summary prints failures:{} rc0 on fully-blocked run (display layer; receipts carry measured:false/legs_measured:0/coverage_blocked). Next fold: print blocked count.
- CF2 refused lock waiter truncates live holder's text file (evidence loss, exclusion unaffected).
- CF3 b_pw2jack +/-1% energy band latent flake (late link landing) — disclosed, unarmed.
- CF4 d_metadata pair arm (0,'value1')|(-1,'') is an out-of-union disclosed correction.
- CF5 measured:true = ran-to-end, not all-arms-measured; gates read coverage_blocked.

## Host incident (recorded)
Shared PipeWire daemon wedged ~06:00-09:24Z under sibling load + orphaned load-hogs; orchestrator restarted pipewire/pipewire-pulse/wireplumber, pactl info 4-5ms after. Fold greens ran post-restart.
