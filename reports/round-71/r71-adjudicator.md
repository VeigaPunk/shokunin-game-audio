# R71 adjudicator (Sol) — second decoder: ffmpeg/ffprobe transport matrix

Round: 71. Wave: `shokunin-train-20261101-w10`. Work commit `7b9e75d`.

## Declared move (coverage/runtime-breadth)

ffmpeg/ffprobe n9.0.1 on the 9-member transport corpus; claim: verdicts
track CONTENT probing, not the r68/r69 suffix/named axis.

## Seat convergence

| seat | landing | contribution |
|---|---|---|
| author | operator-substituted | ffprobe_leg/ffmpeg_transport_matrix/ffprobe_transport_entry + --probe-ffprobe-transport-r71; per-process fifo writers; fresh-fd-per-leg |
| scout | never landed (massacre) | operator pre-flight: ffprobe detects wav on artifact set |
| critic | dispatched v2 post-landing | pending — incl. the fd-sharing artifact + probe_score null + transport-class-equivalence questions |
| boundary | dispatched v2 post-landing | pending — ffmpeg fifo hold band, truncation cliffs |
| verifier | dispatched v2 post-landing | pending — receipt replay + byte-stability |
| baseline/scribe/simplifier/reviewer | never landed | pending post-reset |

## Operator verification

- `--probe-ffprobe-transport-r71` → exit 0, receipt
  `corpus/live/runs/20261014T140155796326Z-normal/measurements.json`:
  zero transport forks on all 9 members under ffmpeg.
- Self-caught defect fixed pre-land: shared-fd offset artifact forked
  redirected_fd; fresh-fd-per-leg removed it.
- Prior-row stability: insertion-only flag; ledger byte-identity check
  armed (`corpus/live/r71-author/compare_receipts.py`, runs vs r70 TSV
  when the 121-mode ledger completes).

## Measured headline

Claim CONFIRMED: content-probing on every transport; suffix plays no
role (7 no-match members reject identically on all 4); dec_act→wav /
dec_hcom→hcom transport-invariant. The SoX named/suffix partition is
decoder-specific — an honest narrowing of the r68/r69 model's scope.
Fixture mechanics learned: per-process fifo writers for consumer chains;
fresh fd per leg for pipe: over seekable fd.

**Verdict: provisional ADMIT.** Bounded: ffmpeg/ffprobe n9.0.1, this
host. Post-landing seats pending free-pool reset.
