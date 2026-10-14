# R67 adjudicator (Sol) — transport as a first-class ledger axis

Round: 67. Wave: `shokunin-train-20261014-w6`. Work commit: `366fcc1`
("r67: transport as first-class ledger axis — fork set measured exact").

## Declared move (depth)

Treat transport as a first-class measured axis over the complete tracked
autodetection/decoder member set: at least one tracked member's verdict
forks on transport (gsrt file-vs-pipe was already measured), and the exact
fork set is the object of measurement. Single parameterized
`transport_leg`/`transport_matrix` over `{file, stdin_pipe, redirected_fd,
fifo_path}`; detection tracked separately from decode-stage verdicts;
deterministic fifo via the pinned writer-linger protocol.

## Seat convergence

| seat | landing | contribution |
|---|---|---|
| author | yes | 10-member × 4-transport matrix; 112-row ledger (49/63), 0 UNPARSED; prior-102 receipts byte-identical; fork set = 5 act/gsrt members, invariant = 5 hcom/wav members |
| critic | yes | fork set re-measured exactly (5/10); verdict-tuple reading pinned ({exit,samples}-only → 2 act members); concurrent `build_artifacts.py` rebuild race flagged — receipts bounded to serial execution; fifo-writer race residual risk disclosed |
| reviewer | yes | r66 audit re-executed verbatim; `pair_dec_act` transport fork independently reproduced |
| simplifier | yes | keep-all: full 10×4 matrix load-bearing; fifo-arm grandchild-leak risk + missing txw/smp member flagged as next-round gap |
| baseline | yes | frozen prior-state replay clean |
| boundary | yes | verdict space refined: the contract is *child-side path resolvability*, not the `{named × seekable}` proxy; fifo+act hangs on dead writer; early-EOF fifo flips detection at len gates; 14-transport extension sweep, detection columns identical |
| verifier | yes | **AGREE 5/5** — 10 replayed receipts byte-identical to author's; fork/invariant partition verbatim incl. distinct non-seekable gsrt errors; fifo linger pin confirmed (`195d7554…` stability ×3 runs); 112 rows 49/63, prior-102 byte-identical, 0 UNPARSED |
| scout | yes | 8-transport × 18-input extension: 12/18 fork under error-inclusive signature (granularity-relative); mechanism pinned — bridge re-opens BY NAME, `-` nameless forever, `/dev/stdin` file-equivalent; **orthogonal `-t` axis found** (`cat f | sox -t act -` decodes on pipe — type-forcing bypasses detection) |
| scribe | yes | verified dead instance's 68-leg matrix post-fix; added timing-free `fifo_hold` (O_RDWR holder) transport — identical verdicts; 49-arm cross-check vs author verbatim; disclosed provenance caveats |

## Adjudicator own reproduction (committed tree `366fcc1`)

- `--probe-transport-dec-act-r67`: forks — `file=decode 278 samples` vs
  `stdin_pipe`/`fifo_path=can't find Sun/NeXT/DEC identifier` vs
  `redirected_fd=premature EOF` (3-group) — matches author verbatim.
- `--probe-transport-preempt-gsrt-r67`: forks — `file`/`redirected_fd`
  `premature EOF` vs `stdin_pipe`/`fifo_path` `invalid format for this
  file type` (2-group, seekable-bit split) — matches.
- `--probe-transport-dec-hcom-r67`: zero failures — the
  transport-invariant control holds (decode 9 × 4).

## Per-axis verdict — **ADMIT**

- **coverage: improved locally** — transport added as a measured ledger
  axis with a parameterized harness; the complete 10×4 matrix is pinned
  and the exact fork partition is a receipt-level fact, not a summary.
- **depth: improved locally** — detection proven transport-invariant
  while decode forks; fork locus attributed (bridge name-resolvability /
  native seekable-bit); boundary's child-resolvability refinement and the
  verdict-tuple reading absorbed; serial-execution bound recorded.
- **calibration: unchanged** — no thresholds or predicates edited;
  additive axis only.

Bounds: SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1 on this host;
receipt byte-stability claimed for serial execution only
(`build_artifacts.py` non-atomic under concurrent rebuild — disclosed,
unfixed); fifo legs deterministic under the pinned 1.0 s writer-linger
(residual extreme-load race disclosed); no standards/fidelity/production
inference.

Work commit `366fcc1`; report-last commit lands scout/scribe +
knowledge/LOG/SCORECARD.
