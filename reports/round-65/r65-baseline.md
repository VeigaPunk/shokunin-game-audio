# R65 baseline — frozen before-state replay of the 92-command ledger

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline
(scout). Frozen state = `git archive` of canonical HEAD **`b1e286c`** ("audio
r64 adjudication: ADMIT — …"), extracted to
`corpus/live/r65-baseline/frozen/` (132 MB, incl. all 3,246 tracked run
receipts). HEAD was `b1e286c` at dispatch, at archive time (01:35 UTC), and at
report time — no mid-window commit, no disambiguation needed this round.

Frozen-commit proof: extracted `corpus/live/r64-author/ledger-r64.tsv` sha256
`fd02d690…` equals the committed bytes; extracted
`corpus/fixtures/measure_audio.py` sha256 `14344808…` equals both `git show
b1e286c:` and the then-clean worktree copy (the live file went dirty only
later — see Live-tree events).

Toolchain: `SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` +
`numpy 2.5.3` — unchanged from the r63/r64 declared set.

## Standalone-capability finding

Unchanged from r64: `measure_audio.py:13` anchors
`ROOT = Path(__file__).resolve().parents[1]` (= `frozen/corpus`); every
fixture input, probe wav, and receipt write resolves inside the frozen tree.
No `--runs` flag exists; receipts land at `ROOT/live/runs/<stamp>-<suffix>/`.
The frozen copy runs fully standalone — the replay wrote zero files outside
`corpus/live/r65-baseline/`.

## Replay result — deterministic, exact

`rerun.py` (verbatim 92-MODES copy of `r64-author/run_ledger.py`: the prior 86
+ the six r64 modes at positions 02–07; serial, `cwd=frozen`) finished
01:36:29→01:38:08 UTC (~99 s). Outputs: `ledger-r65-baseline.tsv`; per-command
captures `out/{01..92}.{stdout,stderr}`; census `runs-{before,after,new}.txt`
(3,246 / 3,338 / 92); hash tables `committed-shas.tsv`, `receipt-compare.tsv`;
`rerun.log`, `toolchain.txt`.

- **Counts by exit: 44 × exit 0 / 48 × exit 1** — matches committed
  `ledger-r64.tsv` exactly.
- **92/92 rows identical** to committed on (idx, exit, failure-summary) —
  `diff` over TSV cols 1,2,4 → empty.
- **Census: 3,246 → 3,338 run dirs (+92, zero extras).** All 92 fresh receipt
  paths resolve under `r65-baseline/frozen/corpus/live/runs/`; zero run dirs
  appeared in canonical `corpus/live/runs/` during my window (live `01:36–
  01:38` stamps: none; sibling runs start at `…T0140`).
- **Receipts: 86/92 byte-identical** (sha256) to the committed counterparts
  named in ledger col 3. Six differing rows, all the same path-coupled class:
  - rows 09 `ui-route-act-00-r63` and 87 `--probe-invalid`: the two carriers
    known since r64 — absolute paths embedded in full `sox_stderr` /
    `detail.stderr`. Full-prefix normalization (frozen→canonical) restores the
    committed sha256 exactly.
  - rows 04, 05, 06, 07 `ui-extensible-valid-{24,25,56,57}-r64`: same class,
    **newly disclosed shape** — these receipts record
    `sox_native_stderr = native.stderr tail[-1][-160:]`
    (`measure_audio.py:469–471`), so the embedded absolute path is truncated
    mid-token (`pen input file `/home/…` committed vs `ects/shokunin/…`
    frozen) and can never sha-match after any prefix rewrite. Verified by
    unified diff: exactly one changed line per receipt, common suffix
    `…corpus/live/round-64/pair_valid_NN.wav': number of valid bits exceeds
    the number of bits per sample` byte-identical. JSON-level comparison with
    `audio-shokunin/corpus/`-anchor truncation of every string leaf:
    **92/92 receipts equal** modulo the disclosed path embeddings.
- Effective before-state: **92/92 receipts identical modulo absolute-path
  embeddings** — a host-path coupling, not content drift.
- Key receipt SHAs (fresh == committed): row 01 normal `8e8cdad6cc3c…`; row 08
  `ui-route-act-84-r63` `f242bd6bc966…` — the act/ffmpeg-route receipt
  re-derives identically in the frozen tree.
- Fixture bytes stable in-tree post-replay: `pair_route_84.wav` `cf5edecc…`,
  `pair_route_00.wav` `cb77db31…` (same values the r64 baseline recorded),
  `pair_valid_24.wav` `714998b8…`, `pair_valid_56.wav` `d4ee4431…` — all equal
  committed bytes.
- Committed-ledger guard: `corpus/live/r64-author/ledger-r64.tsv` sha256
  `fd02d690…` identical before and after my run — the replay writes only to
  scratch.

## Live-tree events during the window (observed, not mine)

- HEAD stable at `b1e286c`; no commits landed during the replay.
- Sibling lanes are mid-sweep on the r65 preemptor axis: uncommitted
  `M corpus/fixtures/measure_audio.py` (+65/−5), `M build_artifacts.py` (+41),
  `M __pycache__/*.pyc`; ~103 new canonical `corpus/live/runs/` dirs stamped
  `…T0140`+ including the `ui-preempt-{gsrt,act,hcom,both}-r65` probes and a
  full 92-command pass. The frozen replay deliberately does not see these —
  before-state is `b1e286c` by construction.
- Other r65 scratch dirs present: `corpus/live/r65-{author,critic,reviewer,
  scout,simplifier}/`, `corpus/live/round-65/`, `reports/round-65/`.

## Write-scope accounting

Wrote only: this report; `corpus/live/r65-baseline/` (`frozen/`, `rerun.py`,
`ledger-r65-baseline.tsv`, `out/`, `runs-{before,after,new}.txt`,
`committed-shas.tsv`, `receipt-compare.tsv`, `toolchain.txt`, `rerun.log`).
No canonical `corpus/live/runs/` writes, no tracked-file edits, no commits.
Leaf seat — no dispatch performed.

## Residual gaps

- Path-embedded receipts (rows 04–07, 09, 87) can never be raw-byte-identical
  off the canonical path; normalized + anchor-truncated semantic comparison is
  the strongest check available in a displaced tree. Rows 04–07's
  `tail[-1][-160:]` truncation means even the *normalized* bytes differ at the
  window start — content equality was established at JSON-field level, not
  byte level.
- Whether the sibling `M` fixture edits get committed, amended, or reverted is
  outside my seat; if committed, the next round's freeze captures them and
  this report remains the `b1e286c` reference.
