# R66 baseline — frozen before-state replay of the 96-command ledger

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
Frozen state = `git archive` of canonical HEAD **`30e5e32`** ("audio r65
adjudication: ADMIT — LOG/SCORECARD/knowledge/verifier+scribe+boundary
reports"), extracted to `corpus/live/r66-baseline/frozen/` (137 MB, 8,458
files incl. all 3,246 tracked run receipts). HEAD was `30e5e32` at dispatch,
at archive time (02:28 UTC), and at report time — no mid-window commit, no
disambiguation needed this round.

## Exclusion accounting (new this round — nested baselines removed)

Per the r66 brief, the archive listing was filtered before extraction:
`archive-manifest.txt` holds all **12,717** tar members;
`archive-excluded.txt` holds the **693** dropped members — every
`corpus/live/r*-baseline` tree tracked at HEAD (`r62-baseline` 254,
`r63-baseline` 256, `r64-baseline` 183 members) plus `node_modules`
(**zero** such members exist at HEAD). Extracted file count 8,458 equals
manifest − excluded − directory entries − the `pax_global_header` member,
and `find frozen -type d -name 'r*-baseline' -o -name node_modules` returns
empty — no nested baseline/frozen trees were carried in.

Frozen-commit proof: extracted `corpus/live/r65-author/ledger-r65.tsv` sha256
`5a9a3ef3…`, `corpus/fixtures/measure_audio.py` sha256 `cf65beb4…`, and
`corpus/live/round-65/pair_preempt_both.wav` sha256 `a37adc7c…` each equal
`git show 30e5e32:<path>` byte-for-byte.

Toolchain: `SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` +
`numpy 2.5.3` — unchanged from the r63/r64/r65 declared set.

## Standalone-capability finding

Unchanged: `measure_audio.py:13` anchors
`ROOT = Path(__file__).resolve().parents[1]` (= `frozen/corpus`); every
fixture input, probe wav (`live/round-65/pair_preempt_*.wav` included), and
receipt write resolves inside the frozen tree. The replay wrote zero files
outside `corpus/live/r66-baseline/` — all 96 ledger col-3 receipt paths carry
the `r66-baseline/frozen/corpus/live/runs/` prefix.

## Replay result — deterministic, exact

`rerun.py` (verbatim 96-MODES copy of `r65-author/run_ledger.py`: the prior
92 + the four r65 preempt modes at positions 02–05; serial, `cwd=frozen`)
ran 02:30:05→02:31:48 UTC (~104 s). Outputs: `ledger-r66-baseline.tsv`;
per-command captures `out/{01..96}.{stdout,stderr}`; census
`runs-{before,after,new}.txt` (3,246 / 3,342 / 96); hash tables
`committed-shas.tsv`, `receipt-compare.tsv`; field-level check
`semantic-compare.tsv`; `compare.py`, `semantic_compare.py`, `rerun.log`,
`toolchain.txt`.

- **Counts by exit: 44 × exit 0 / 52 × exit 1** — matches committed
  `ledger-r65.tsv` exactly.
- **96/96 rows identical** to committed on (idx, exit, failure-summary) —
  `diff` over TSV cols 1,2,4 → empty.
- **Census: 3,246 → 3,342 run dirs (+96, zero extras).** All 96 fresh receipt
  paths resolve under `r66-baseline/frozen/corpus/live/runs/` (stamps
  `20261014T023005…T023148`).
- **Receipts: 86/96 byte-identical** (sha256) to the committed counterparts
  named in ledger col 3 — the committed r65 run dirs are still on disk
  untracked under canonical `corpus/live/runs/20261014T0143…`. Ten differing
  rows, all the same path-coupled class:
  - rows 13 `ui-route-act-00-r63` and 91 `--probe-invalid`: the two carriers
    known since r64 — absolute paths embedded in full `sox_stderr` /
    `detail.stderr`. Full-prefix normalization (frozen→canonical) restores
    the committed sha256 exactly (`normalized` in `receipt-compare.tsv`).
  - rows 08–11 `ui-extensible-valid-{24,25,56,57}-r64`: the known
    `tail[-1][-160:]` truncation class — embedded absolute path is cut
    mid-token (`pen input file `/home/…` committed vs `ects/shokunin/…`
    frozen), so no prefix rewrite can sha-match. Unified diff: only the
    `sox_native_stderr` (and row-10 `sox_stderr`) line differs; common
    suffix `…/round-64/pair_valid_NN.wav': number of valid bits exceeds
    the number of bits per sample` byte-identical.
  - rows 02–05 `ui-preempt-{act,gsrt,hcom,both}-r65`: **newly disclosed this
    round** — the r65 preempt family embeds the same absolute fixture path
    in up to four stderr leaves (`sox_stderr`, `sox_stat_stderr`,
    `sox_bridge_stderr`, `sox_native_stderr`), several truncation-cut at the
    head (`s/shokunin/…`, `nk/Projects/…`, `: can't open input file …`).
    Same class, same `pair_preempt_*.wav': <reason>` suffixes.
- JSON-level comparison (`semantic_compare.py`: identical structure, every
  differing string leaf anchored at its last `corpus/` occurrence with the
  fresh leaf carrying the `live/r66-baseline/frozen/` infix): **96/96
  receipts equal modulo the disclosed path embeddings** — `86 EQUAL`,
  `10 EQUAL-MOD-PATHS`, `0 CONTENT-DIFF` in `semantic-compare.tsv`.
- Key receipt SHAs (fresh == committed): row 01 normal
  `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — the
  same value the r65 baseline recorded.
- Fixture bytes stable in-tree post-replay: `pair_preempt_act.wav`
  `cf5edecc…` (== the r63 `pair_route_84.wav` value, consistent with the
  uncollided-control design), `pair_preempt_gsrt.wav` `477bd371…`,
  `pair_preempt_hcom.wav` `bfc61413…`, `pair_valid_24.wav` `714998b8…` —
  all equal committed bytes.
- Committed-ledger guard: `corpus/live/r65-author/ledger-r65.tsv` sha256
  `5a9a3ef373a4a21a16e5180855d2e56b80e5c03c0109d7f76596b678d404b7bd`
  identical before and after my run — the replay writes only to scratch.
- **Drift: zero** — all deltas are explained by the known path-embedding
  convention.

## Live-tree events during the window (observed, not mine)

- HEAD stable at `30e5e32`; no commits landed during the replay.
- Sibling r66 lanes are mid-sweep on the declared preemptor/length-gate
  axis: uncommitted `M corpus/fixtures/measure_audio.py`, `M
  build_artifacts.py`, `M __pycache__/*.pyc`; canonical
  `corpus/live/runs/` dirs stamped `…T0232`+ include the r66 probe names
  `ui-dec-{hcom,act}-r66`, `ui-lengate-{gsrt-24,gsrt-25,hcom-131,hcom-132}-r66`
  plus a full 96-mode pass — none written by this replay.
- Other r66 scratch dirs present: `corpus/live/r66-{author,reviewer,
  simplifier}/`, `reports/round-66/r66-reviewer.md`.

## Write-scope accounting

Wrote only: this report; `corpus/live/r66-baseline/` (`frozen/` minus the
693 excluded members, `archive-{manifest,excluded}.txt`, `rerun.py`,
`ledger-r66-baseline.tsv`, `out/`, `runs-{before,after,new}.txt`,
`committed-shas.tsv`, `receipt-compare.tsv`, `semantic-compare.tsv`,
`compare.py`, `semantic_compare.py`, `committed-ledger-sha.before.txt`,
`toolchain.txt`, `rerun.log`). No canonical `corpus/live/runs/` writes, no
tracked-file edits, no commits. Leaf seat — no dispatch performed.

## Residual gaps

- Path-embedded receipts (rows 02–05, 08–11, 13, 91) can never be
  raw-byte-identical off the canonical path; rows 02–05 and 08–11 truncate
  the path mid-token at the leaf head, so anchor-level JSON comparison is
  the strongest check available in a displaced tree.
- Whether the sibling `M` fixture edits get committed, amended, or reverted
  is outside my seat; if committed, the next round's freeze captures them
  and this report remains the `30e5e32` reference.
