# Round 66 adjudication — preemptor-map completion (Sol)

Work commit `014b532`. Seat set: author, baseline, scout, critic, reviewer,
simplifier, scribe, boundary (8/8 reports) + named non-author verifier
(`r66-verifier.md`).

## Own reproductions on the committed tree (this host, SoX_ng 14.8.0.1
USING_FFMPEG + ffmpeg n9.0.1)

| check | command (abbrev.) | observed |
|---|---|---|
| dec hcom | `sox -V3 corpus/live/round-66/pair_dec_hcom.wav -n stat` | `detected file format type 'hcom'`; `Samples read: 9`, exit 0 |
| dec act | same on `pair_dec_act.wav` | `detected ... 'act'`; `Samples read: 278` (ffmpeg bridge) |
| gsrt gate | `pair_lengate_gsrt_{24,25}.wav` | 24→`wav`, 25→`gsrt` — exact |
| hcom gate | `pair_lengate_hcom_{131,132}.wav` | 131→`wav`, 132→`hcom` — exact |
| wve predicate | own 15-B `ALawSoundFile**` + tail | detected `wve`; byte0 `0x41` — RIFF (`0x52`) unreachable by construction |

All six tracked members reproduce exactly; the wve geometric falsification is
first-hand.

## Verdict per claim

1. **Reachable pre-act set on RIFF+0x84@256 = exactly {gsrt, hcom};
   order gsrt ≺ hcom ≺ act ≺ wav** — CONFIRMED (author ledger + critic
   byte/exact verification + scout 36-probe matrix rerun + boundary
   91-fixture sweep + my spot-checks).
2. **wve predicate `len≥15 ∧ file[0:15]=="ALawSoundFile**"`; unreachable on
   RIFF** — CONFIRMED as declared-else-branch falsification: 15 mutants dead
   (boundary), 768-value sweep hits only true bytes, ~25 RIFF-embedded
   constructions never detect wve. On non-RIFF carriers wve DOES preempt
   gsrt/hcom/act — the row-80 position is live but only off the RIFF family.
   SCORECARD r65 cell corrected to scope wve off-RIFF (reviewer LOW-1).
3. **Decodable-preemptor controls tracked** — CONFIRMED: `pair_dec_hcom`
   byte-identical to r65-critic D1 (3-way convergence); native hcom reader
   decodes 9 samples; `pair_dec_act` sole-byte@68 flips to act-bridge 278.
4. **Exact length gates** — CONFIRMED: gsrt 24‖25, hcom 131‖132 (RIFF
   shells + bare carriers; `len≥p+l` read-window property).
5. **Ledger 96→102, prior receipts byte-identical** — CONFIRMED (baseline
   96/96 frozen; author + 3-seat identical new receipts).

## Absorbed refinements (claim-bounding, not defects)

- Critic: autodetect→act on stdin structurally broken (257-B prefetch
  replayed into the au reader; fifo blocks in open()); gsrt reader floor
  34 B vs detector 25 B — band [25,33] detects-but-never-decodes; hcom
  close-time guards inert on decode path. Scoped in the knowledge entry.
- Boundary: `pair_dec_act` decode is transport-forked — 278 on regular
  file, fails on pipe/redir; `txw`/`smp` readers hard-refuse pipes.
  Scoped: file-transport claim only.
- Scribe: detection≠accept asymmetries tabulated (wve detector looser
  15<18 B; gsrt stricter at byte 24; hcom chain-gated).

## Verdict: ADMIT

Preemptor map complete on the declared domain. Bounded to this host's
SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1; ffmpeg-less builds drop the
act row and shrink AUTO_DETECT_SIZE to 132. No standards-conformance,
fidelity, or production inference.
