# R67 verifier — non-author independent replay: **AGREE 5/5**

host: devin (same lane; canonical repo `/home/vgpnk/Projects/shokunin/audio-shokunin`
HEAD `366fcc1` — confirmed `git rev-parse HEAD`; zero modified tracked files
pre-run; `corpus/fixtures/measure_audio.py` clean vs HEAD).
Toolchain observed: python 3.14.7, `/usr/bin/sox` = SoX_ng v14.8.0.1 — matches
the author's declared toolchain.
Scratch: `corpus/live/r67-verifier/` (run_ledger.py + compare_receipts.py copied
verbatim from `corpus/live/r67-author/`; only the output TSV path redirected to
`ledger-r67-verifier.tsv` — the committed `r67-author/ledger-r67.tsv` was never
touched). **All runs serial.** No commits; leaf seat.

## Method

1. `cd ~/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/live/r67-verifier/run_ledger.py`
   — one contiguous serial run of the committed 112-command ledger (r66's 102 +
   the 10 new `--probe-transport-*-r67` modes at positions 2-11), TSV ->
   `r67-verifier/ledger-r67-verifier.tsv`, progress log `ledger-stderr.log`.
2. `python3 .shokunin/audio/corpus/live/r67-verifier/compare_receipts.py` —
   byte-compares my rows {1}∪{12-112} against the r66 ledger's committed
   receipts (`corpus/live/r66-author/ledger-r66.tsv` paths; all 102 target
   receipt files exist on disk and are git-tracked under `corpus/live/runs/`).
3. `python3 .shokunin/audio/corpus/live/r67-verifier/compare_vs_author.py` —
   byte-compares my 10 transport receipts vs the author's own ledger receipts.
4. Two extra serial reruns each of `--probe-transport-dec-act-r67` and
   `--probe-transport-preempt-act-r67`; `cmp` + `sha256sum` across the three
   receipts per member.

## Claim 1 — fork set = exactly the act+gsrt-detected members (5/10): **AGREE**

My receipts (rows 2-11 of `ledger-r67-verifier.tsv`), extracted verbatim:

| member | detected | exit | fork | verdict groups (mine) |
|---|---|---|---|---|
| preempt_act | act | 1 | yes | file=decode 3839 \| stdin_pipe/fifo_path=`can't find Sun/NeXT/DEC identifier` \| redirected_fd=`premature EOF` (3) |
| preempt_gsrt | gsrt | 1 | yes | file/redirected_fd=`premature EOF` \| stdin_pipe/fifo_path=`invalid format for this file type` (2) |
| preempt_hcom | hcom | 0 | no | all-4 `bad compression type` |
| preempt_both | gsrt | 1 | yes | identical shape to preempt_gsrt (2) |
| dec_hcom | hcom | 0 | no | all-4 decode 9 exit 0 |
| dec_act | act | 1 | yes | file=decode 278 \| stdin_pipe/fifo_path=au-magic \| redirected_fd=`premature EOF` (3) |
| lengate_gsrt_24 | wav | 0 | no | all-4 `fmt chunk not found` |
| lengate_gsrt_25 | gsrt | 1 | yes | file/redirected_fd=`premature EOF` \| stdin_pipe/fifo_path=`invalid/missing file name in header` (2) |
| lengate_hcom_131 | wav | 0 | no | all-4 decode 43 exit 0 |
| lengate_hcom_132 | hcom | 0 | no | all-4 `premature EOF` |

Fork set = {preempt_act, preempt_gsrt, preempt_both, dec_act, lengate_gsrt_25}
— exactly the 5 act- and gsrt-detected members; all 5 hcom/wav-detected members
transport-invariant. Matches the author's table verbatim, including the
member-level error-string difference between the two gsrt non-seekable groups
(`invalid format for this file type` vs `invalid/missing file name in header`).

Bonus evidence beyond the claim: `compare_vs_author.py` shows all 10 of my
independently produced receipts **byte-identical** to the author's own
ledger receipts (`10 identical, 0 differ`).

## Claim 2 — detection never forks (decode-stage only): **AGREE**

`sox_detected_format` extracted per arm from all 10 receipts (claim asked >=3;
checked all 10): each member reports one identical detected format across
file/stdin_pipe/redirected_fd/fifo_path — act x2, gsrt x3, hcom x3, wav x2.
Every recorded verdict-group difference is in `(exit, samples_read, error)`
only. Illustrative: on dec_act the fifo arm still detects `act` and routes
`ffmpeg` (detection identical) while exiting 2 au-magic — the fork is
strictly decode-stage.

## Claim 3 — act fifo leg deterministic via pinned 1.0 s writer-linger: **AGREE**

- Every receipt pins `transport_protocol =
  {arm_timeout_s: 10, fifo_writer_hold_s: 1.0, fifo_feed: "one-shot write then
  writer lingers"}` — the 1.0 s linger is in the committed bytes.
- fifo leg stable across >=2 reruns on **both** act members: ledger-run receipt
  + 2 independent reruns byte-identical per member —
  - dec_act: `cmp` clean 2/2; sha256 `195d755410c97d119356bd7dbdb5ed220425603887b97fd419cab95138aa9410`
    (matches the sha256 the author quoted for its own reruns).
  - preempt_act: `cmp` clean 2/2; sha256 `434d82d359024fc35b15a27ed03baf13299021fcd1f9b0ec36ccb7e7e3d65415`.
- The fifo arm records the same terminal class as the pipe arm
  (`can't find Sun/NeXT/DEC identifier`, exit 2, ffmpeg route) — the claimed
  "bridge on a contended fifo" verdict shape.
- Limit: I did not re-probe the counterfactual bare-writer race (would need an
  uncommitted harness variant); the claim as scoped — pinned linger recorded +
  fifo leg stable across reruns — is fully confirmed.

## Claim 4 — full ledger: 112 rows, 49/63; prior-102 byte-identical: **AGREE**

`ledger-r67-verifier.tsv`: `wc -l` = **112** rows;
`awk -F'\t' '{print $2}' | sort | uniq -c` -> **49 x exit 0 / 63 x exit 1**.
`compare_receipts.py` -> `102 prior-mode pairs checked, 0 mismatches`
(exit codes and receipt bytes vs the r66 committed receipts).
Additional check: my 112 exit codes are position-identical to the author's
`ledger-r67.tsv` (`0 exit-code mismatches across 112 rows`).

## Claim 5 — serial ledger integrity, zero UNPARSED: **AGREE**

`grep -c UNPARSED ledger-r67-verifier.tsv` -> **0**; all 112 physical rows
parsed to `(exit, receipt, failsum)`. No transient flakes observed on my run
(author's disclosed mid-write flake class is concurrency-triggered; I ran
strictly serial with no concurrent artifact rebuilds).

## Disclosures / limits

- Same host, same toolchain build as the author — no independent host or SoX
  version. The verdict-matrix strings are toolchain-specific by nature.
- Verdict signature is string-level (author-disclosed: `premature EOF` merges
  multiple mechanisms); my checks confirm verdict-level, not mechanism-level.
- Scratch files produced: `r67-verifier/run_ledger.py`,
  `compare_receipts.py`, `compare_vs_author.py`, `ledger-r67-verifier.tsv`,
  `ledger-stderr.log`; receipts under `corpus/live/runs/20261014T0533*|
  20261014T0535*` (117 new dirs = 112 ledger + 1 smoke + 4 stability reruns).
- Concurrent sibling-seat churn was live during my run: `git status`
  post-run shows `M`/`D` under `corpus/live/r67-scribe/` that was not
  present at my pre-run check — the author's disclosed sibling-rebuild
  condition. None of my commands touch that path, and none of the
  evidence above was affected (0 UNPARSED, all byte-compares clean).

## Verdict

**AGREE on all 5 claims.** The committed bytes independently reproduce the
claimed fork set, detection invariance, pinned-linger determinism, ledger
shape, and prior-receipt byte-identity. No blockers; no commits made.
