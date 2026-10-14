# R75 adjudicator (Sol) — consumer-class breadth: paplay + aplay + ffplay

Round: 75. Wave: `shokunin-train-20261101-w14` (recovery dispatch — the
first seat generation died with its parent session ~16:10Z; all landed
work is the 16:20Z+ respawn generation). Work commit `db46fba`, folds
commit `5f60747`.

## Declared move

`--probe-consumers2-r75`: three PLAYBACK consumers (paplay via pacat/
libpulse, aplay via in-process ALSA, ffplay via lavf pull-model) on the
canonical member × transport matrix (9 members × {file, stdin_pipe,
redirected_fd, fifo_path}), plus per-consumer ops rows (daemon gate,
SDL driver axis, writerless-fifo kill classes, device axis, `-ss`
position cell).

## Claim adjudication

- **Consumer breadth CONFIRMED** — 27/27 transport-invariant verdict
  groups on the landed tree; verifier AGREE on all committed claims
  (byte-identical receipts ×5 vs the author's). New reach: paplay's
  `.snd` name axis does NOT transfer from pw-cat (sf_open_fd is
  name-blind → all reject `Failed to open audio file.`); ffplay does
  NOT reproduce mpv's dec_hcom inverted seek fork (SDL pull-model,
  avio seeks stay 0); aplay's raw fallback accepts unmatched content
  (name-blind parse, `raw data` invariant-accept).
- **Kill classes per consumer** — writerless fifo: paplay dies on TERM
  (-15), aplay catches TERM yet stays blocked → SIGKILL -9, ffplay's
  handler exits 123 while the read thread stays blocked. Ordering
  cell: paplay opens the input BEFORE connecting, so a dead-server +
  writerless-fifo blocks in `open()` without ever reaching the daemon
  gate.
- **critic C1 CONFIRMED + folded** — `sigterm_immune` mislabeled a
  one-TERM observation: aplay dies to a second SIGTERM. Field renamed
  `alive_after_term1` in `_nowriter_cell` (the r70-era `esc` cell at
  :1800 keeps its frozen name — prior evidence).
- **critic C2 CONFIRMED + folded** — vacuous invariance: with a dead
  PULSE_SERVER all four arms collapse to one errored signature and
  `transport_fork: false` would misreport. Guard added
  (`viable_legs` + named failure) — fires only on same-infra-wall
  collapse (paplay `Connection failure` / aplay device error / ffplay
  undetected abort); uniform content rejection on reject members is
  a real verdict, not a collapse (integrator re-verified: 27/27
  clean post-fold, and the guard is silent on the live host).
- **critic C3 CONFIRMED + folded** — `ffplay -ss` stdin arm: the
  claimed decode-discard rescue was predicted-but-false; measured is
  `could not seek` + silent abort (0 status samples, ~0.16 s wall).
  `predicted` text + failure message corrected.
- **critic C4 + reviewer R1 CONFIRMED + folded** —
  `_PACAT_RACY_TAIL`'s `Time:.*Latency:` alternative was dead (the `$`
  required EOL right after `Latency:`; real lines carry the usec
  field). Re-anchored to consume to EOL; paired fix (C4c): the quote
  rule now collapses only path-bearing quotes so the
  `Using sample spec '…'` witness survives where the Time: filter now
  engages. stderr_tail leaves shift accordingly (declared fold delta;
  the committed pre-fold receipts remain the historical record).
- **reviewer R2 folded** — `_nowriter_cell` routed through the ffplay
  status-line filter (status lines previously raced the verdict for
  the tail slot).
- **reviewer R3 folded** — ffplay `error` aligned to mpv-leg
  convention (block/nonzero-rc only; invalid/seek detail lives in
  `ffplay_invalid`/`could_not_seek`).
- **simplifier D1–D3 folded** (all proven byte-identical pre-fold):
  shadowed `pa_context_connect` pattern dropped; `Input #0` regex and
  `Invalid data` literal deduped through `_ffplay_fields`. D4 withheld
  by the simplifier itself — re-anchoring (not deletion) was the
  correct fold, done under C4a.
- **Recorded, not folded** — critic C5 (the "content wins over name"
  claim lacks a landed accept-leg for paplay — the name axis measured
  only on reject path) → r76 frontier. Recurring defect (3rd
  recurrence): author report called untracked scratch receipts
  "committed" — filed report stands; flagged in adjudication.

## Seat accounting

9/9 reported: author (`db46fba`, +936/−3; 27/27 groups; ops cells
measured 3 consumers × daemon/device/SDL/fifo/seek axes); scout;
boundary (consumer-specific severing both ways: PULSE_SERVER kills
paplay not pw-cat; PIPEWIRE_RUNTIME_DIR vice versa; aplay TERM-class;
ffplay rc0-everything 42/42); baseline (zero-drift on freeze,
committed-tree replay clean); scribe (dead-draft archive); critic
903c9f81 (C1–C5, two folded as fixture corrections); reviewer
832af493 (R1–R6 LOW, insertion-only + replay byte-identical);
simplifier e19679a6 (D1–D3 proven, D4 correctly withheld);
verifier fd930c97 (AGREE all claims, byte-identical ×5).

## Verdict

**ADMIT-corr** — three-consumer breadth confirmed with four
falsifications honestly folded (labels, vacuity, prediction, dead
filter). Bounded: pacat/libpulse 17.0, aplay (in-process ALSA,
`-D null`), ffplay/ffmpeg lavf (SDL_AUDIODRIVER=dummy), this host.
r76 frontier: paplay content-vs-name accept leg, consumer tail/parser
hardening under load, SDL driver-axis depth.
