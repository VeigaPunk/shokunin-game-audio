# r78 reviewer — working notes (scratch, untracked)

## Structural (d9aa6f9 vs bdf748e, corpus/fixtures/measure_audio.py)
- difflib opcodes: 3 inserts (2372 lines @old5905 + 1 arg line + 25-line dispatch) + 3 single-line replaces.
- residual after stripping inserts = old, differing in exactly 3 lines; each is a pure
  prepend/insertion:
  - guard: `...probe_capture_r77]) > 1:` -> `...probe_capture_r77, args.probe_capture_r78]) > 1:` (exact)
  - mode:  `    mode = "probe-capture-r78" if args.probe_capture_r78 else ` + old[11:]
  - suffix: `    suffix = "-capture-r78" if args.probe_capture_r78 else ` + old[11:]
- numstat +2401/-3 == 2398 net inserts + 3 replaced lines. py_compile: n/a yet (env copy).
- committed pyc `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` at d9aa6f9 embeds
  source_size 499311 but the committed source is 502350 -> STALE pyc (precedent: 65790f1 also stale;
  bdf748e/731937c/1a84ca7 match).

## Host topology (my window, 23:0xZ)
- DualSense USB audio GONE (kernel: usb 10-3 disconnect 19:55:12 local = 22:55:12Z; HID re-registered
  over BT at 22:55:55Z). Default source now Line; default sink SPDIF. r78-baseline named
  "DualSense default source" as the environmental set — that set has moved AGAIN.
- Stale `aplay -D null /tmp/nowriter-r75-.../nowriter.wav` (pid 2202613) running >2.9h.
- Stale null sink `r78p_check` (module 536870916).

## My independent harness run (own env tree, HEAD blob-verified)
receipt: corpus/live/r78-reviewer/env/corpus/live/runs/20261014T230634982331Z-capture-r78/measurements.json
- 6/8 entries `failures: []`; 2 failures, both attributed below.
- lattice / loss / props / segv / zeros / parec: leaf-for-leaf identical to the author's receipt
  (modulo PID-stamped probe names) — see comparison output in logs/.
- follow entry differs: moved leg [s_new, SPDIF] (author [s_new, s_new]); still_probe [SPDIF, SPDIF]
  (author [s_new, s_new]); pactl moved_at=0.5 (author None); nofollow pinned=True+followed=True
  (author followed=True, pinned=False).
- target_0 failure in my harness run: tap on the default sink carried 1000/1500@8189 tone from
  tap 3.1s..5.6s while the stream's own consumers were [] at 1.0/2.5/4.5 and the node stayed
  suspended -> the harness's content witness has NO foreign guard and its tone is NOT seat-unique
  (the r79 scout's discriminator is the same 1000/1500@8192; r78-boundary used 1100/1750@12000 for
  exactly this reason). Attribution: contended-host content confound, not a law violation.

## My raw re-derivations (own tone L880/R1320@10000, own parser)
raw-checks.json / logs/raw-checks-a.log
- zeros: producer_unlink sizes [155692,401452,499756,593964,786476,880684] final=expected 960044,
  pre_mine 14/14, post 27/27 silent peak 0 -> unlinked_sustained_zeros AGREE (exact author numbers)
- zeros: consumer_unlink froze 311340 across 3 samples then resumed to 1344044 -> unlinked_stall AGREE
- segv: 4 invalid classes rc=-11, stderr_len 0, no ports/consumers; crash wall 0.06s (harness reports
  2.01 = its own sampling schedule, not the death time); control rc=0; Audio/Source stall rc=-9 AGREE
- parec: hdr_rate_fix bps=195756 (header rate=22050) vs hdr_rate_plain bps=85111 (header 22050)
  -> header_prefix_mismatch AGREE; rate_fix_raw bps=195756 vs rate_req_raw 85111 -> fix adopts 48000 AGREE
- lattice (first run contaminated: startup default was the simplifier's probe sink):
  fallback legs -> SPDIF consumers rc=0 wall 2.62; honored -> probe sink; target_0 rc=-9 killed
  consumers=[] tap_mine=0/36 (no tone on the default) -> target_0 stall AGREE (needs clean re-run)
- cross-seat event: my raw-checks startup read r78_def_sink_927430 (simplifier's) as session default
  and its finally restored that value at 23:09:43Z; reviewer restored SPDIF at 23:10Z. The
  simplifier's control run then failed playback_default_follow_r78_probe (my interference, named).

## TODO
- clean re-run: lattice, follow, aplay (after the simplifier's in-flight pair).
- prior-cell: run --probe-capture-r77 (and r76) in the env, leafdiff vs canonical.
- report -> reports/round-78/r78-reviewer.md

## STATUS (final)
- lattice (clean re-run, logs/raw-checks-b.log): all 6 fallback legs + monitor_of_probe -> SPDIF
  rc=0 wall 2.62-2.67 with 26/36 own-tone windows; honored -> probe sink; target_0 rc=-9 cons=[]
  0/36 windows. DONE.
- follow + aplay raw (logs/raw-checks-c.log): follow DONE (both directions; pactl delayed 3.5s;
  durability 0.25s). aplay raw CONTENDED (witness EBUSY + 5.9s release reproduced; +7s/convert
  legs held by a sibling probe) -> covered by my harness run instead.
- prior cells DONE: fresh --probe-capture-r77 failures {}; 302 leaves vs canonical, 0 undeclared
  (logs/r77-vs-canonical.txt, logs/r77-classification.txt).
- report written: reports/round-78/r78-reviewer.md (277 lines).
- NOTE: the run-1 r78 receipt was destroyed by my own scratch cleanup; its comparison extract is
  logs/r78-run1-compare-extract.txt; run 2 receipt kept at receipts/r78-measurements-run2.json.

