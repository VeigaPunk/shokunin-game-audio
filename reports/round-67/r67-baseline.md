# R67 baseline — frozen before-state replay of the 102-command ledger

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
Frozen state = `git archive` of canonical HEAD **`0df212f`** ("r66
report-last: adjudication + knowledge entry + verifier AGREE 5/5"),
extracted to `corpus/live/r67-baseline/frozen/` (165 MB, 13,342 files incl.
all 3,781 tracked `corpus/live/runs/` receipt dirs). HEAD was `0df212f` at
dispatch (~05:0x UTC) and at archive time (05:06–05:07 UTC).

**Mid-window commit (observed, not mine):** `f4621f9` "hygiene: ignore
regenerable baseline tree/frozen dirs (xsentinel w6 MEDIUM)" landed at
05:09:57 UTC — *during* the replay window — adding `corpus/.gitignore`
(3 lines: `live/*/tree/`, `live/*/frozen/`). `git diff 0df212f f4621f9
--stat` shows that single file only: no ledger, receipt, fixture, or
measure_audio.py change. The frozen tree predates it (extracted from
`0df212f` before the commit), and every committed-receipt comparison below
was re-anchored on `git show 0df212f:<path>` explicitly — 102/102 match.

## Exclusion accounting (r66 convention — tracked baseline scratch removed)

`archive-manifest.txt` holds all **18,586** tar members (14,429 file members
+ 4,157 dir entries + `pax_global_header`). `archive-excluded.txt` holds the
**1,097** dropped members — every tracked `corpus/live/r*-baseline` member at
HEAD (r62: 252, r63: 254, r64: 181, r65: 193, r66: 207 flat ledger/capture
files; **zero** tracked `r*-baseline/frozen|tree` members exist at HEAD) plus
`node_modules` (**zero** such members). Extracted file count 13,342 =
14,429 − 1,087 excluded files (10 excluded members are dir entries). `find
frozen -type d \( -name 'r*-baseline' -o -name node_modules \)` returns
empty — no nested baseline/frozen trees carried in. (The `baseline*.wav`
files and `reports/round-*/r*-baseline.md` documents in the frozen tree are
tracked fixture/report content, not seat scratch trees.)

Frozen-commit proof (all byte-equal to `git show 0df212f:<path>`):
`corpus/fixtures/measure_audio.py` `a99bf407…`,
`corpus/live/r66-author/run_ledger.py` `d5cc6371…`,
`corpus/live/r66-author/ledger-r66.tsv` `b152c079…`,
`corpus/live/r66-verifier/ledger-r66-verifier.tsv` `bf079022…`,
`corpus/live/round-66/pair_dec_hcom.wav` `325fb967…`. The raw archive
(`git archive HEAD`, sha256 `489d3255…`) was deleted after extraction — it
is reproducible byte-identically from `0df212f`.

Toolchain: `SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` +
`numpy 2.5.3` — unchanged from the r63–r66 declared set.

Repo-path note: the brief's line 6 names `~/Projects/prymeagnt/audio`; that
worktree resolves `.shokunin/audio` via symlink into this canonical repo
(`/home/vgpnk/Projects/shokunin/audio-shokunin`, the dispatch header's repo).
All scratch/report writes land in the canonical repo as in r62–r66.

## Standalone-capability finding

Unchanged: `measure_audio.py:13` anchors `ROOT =
Path(__file__).resolve().parents[1]` (= `frozen/corpus`); every fixture
input — the r66 family included (`live/round-66/pair_{dec_hcom,dec_act,
lengate_gsrt_24,lengate_gsrt_25,lengate_hcom_131,lengate_hcom_132}.wav` per
`measure_audio.py:466-473`) — resolves inside the frozen tree, and receipt
writes go to `frozen/corpus/live/runs/`. The replay wrote zero files outside
`corpus/live/r67-baseline/` — all 102 ledger col-3 receipt paths carry the
`r67-baseline/frozen/corpus/live/runs/` prefix. Canonical
`corpus/live/runs/` gained zero dirs during my window (the 20 sibling-written
`20261014T050349…T050416` dirs predate it).

## Replay result — deterministic, exact

`rerun.py` (verbatim 102-MODES copy of `r66-author/run_ledger.py` — verified
`==` by import before running: the prior 96 + the six r66 preemptor-map modes
at positions 02–07; serial, `cwd=frozen`) ran 05:08:49→05:10:39 UTC (~110 s),
exit 0. Outputs: `ledger-r67-baseline.tsv`; per-command captures
`out/{01..102}.{stdout,stderr}` (204 files); census
`runs-{before,after,new}.txt` (3,781 / 3,883 / 102); hash tables
`committed-shas.tsv`, `receipt-compare.tsv`; field-level check
`semantic-compare.tsv`; `compare.py`, `semantic_compare.py`, `rerun.log`,
`toolchain.txt`, `committed-ledger-sha.before.txt`.

- **Counts by exit: 44 × exit 0 / 58 × exit 1** — matches committed
  `ledger-r66.tsv` exactly (the r66-verifier ledger agrees identically).
- **102/102 rows identical** to committed on (idx, exit, failure-summary) —
  `diff` over TSV cols 1,2,4 → empty, against **both** committed r66 ledgers
  (`r66-author/ledger-r66.tsv` and `r66-verifier/ledger-r66-verifier.tsv`).
- **Census: 3,781 → 3,883 run dirs (+102, zero extras).** All 102 fresh
  receipts resolve under `r67-baseline/frozen/corpus/live/runs/` (stamps
  `20261014T050850…T051039`).
- **Committed-receipt anchor: 102/102** committed receipts named in
  `ledger-r66.tsv` col 3 are byte-identical to their `git show 0df212f:`
  blobs (checked post-commit against the frozen commit, not moved HEAD).
- **Receipts: 89/102 byte-identical** (sha256) to committed counterparts;
  **2 normalized** (rows 19 `ui-route-act-00-r63`, 97 `--probe-invalid`):
  absolute paths embedded in full stderr leaves — the frozen→canonical
  infix rewrite (`corpus/live/r67-baseline/frozen/corpus/` → `corpus/`)
  restores the committed sha256 exactly;
  **11 raw-DIFFERS, all the known truncation class** — rows 04, 05, 07
  (`ui-lengate-{gsrt-24,gsrt-25,hcom-132}-r66`, newly observed path-embedders
  from the r66 family) and rows 08–11 (`ui-preempt-*-r65`), 14–17
  (`ui-extensible-valid-{24,25,56,57}-r64`): `tail[-1][-160:]` cuts the
  embedded absolute path mid-token at the leaf head, so no prefix rewrite
  can sha-match; anchored suffix after the last `corpus/` is byte-identical
  (`…/round-66/pair_<member>.wav': <reason>` etc.).
- JSON-level comparison (`semantic_compare.py`): identical structure on all
  102 rows; every differing string leaf is `corpus/`-anchored in both
  receipts with equal post-anchor suffix and carries the
  `live/r67-baseline/frozen/` infix — **89 EQUAL, 13 EQUAL-MOD-PATHS,
  0 CONTENT-DIFF, 0 STRUCTURE-DIFF** (`semantic-compare.tsv`).
- Row-01 normal receipt sha `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591
  d117732f09ffaffb1b` — identical fresh and committed; the same value the
  r66 baseline recorded for its row 01.
- Fixture bytes stable in-tree post-replay: `pair_dec_hcom.wav`
  `325fb967…` (== committed), `pair_dec_act.wav` `777b6764…`,
  `pair_lengate_gsrt_24.wav` `e7db9976…`, `pair_lengate_gsrt_25.wav`
  `ede4161b…`, `pair_lengate_hcom_131.wav` `6fd9f471…`,
  `pair_lengate_hcom_132.wav` `a1abdac4…`.
- Committed-ledger guard: `corpus/live/r66-author/ledger-r66.tsv` sha256
  `b152c0795c0d6b19834ca69771e0c6e6142effd6be7f2eaf04c368f4a5e9e224`
  identical before and after my run — the replay writes only to scratch.
- **Drift: zero** — all deltas are explained by the known path-embedding
  convention.

## Live-tree events during the window (observed, not mine)

- `f4621f9` (corpus/.gitignore hygiene) committed 05:09:57 UTC, mid-replay;
  no effect on the frozen `0df212f` baseline or the compared blobs.
- Sibling r67 lanes mid-flight: untracked `corpus/live/r67-{author,boundary,
  critic,reviewer,simplifier}/`; canonical `corpus/live/runs/` dirs stamped
  `20261014T050349…T050416` (two 10-member dec/lengate/preempt sweeps) —
  none written by this replay (my window started 05:08:50).
- `git status` at report time: `M corpus/fixtures/measure_audio.py`
  (+183/−3, adds `TRANSPORT_R67_ARMS`/`TRANSPORT_R67_MEMBERS` — the
  declared transport axis, mtime 05:15:17 UTC, i.e. *after* my replay
  ended 05:10:39) and `M corpus/fixtures/__pycache__/
  measure_audio.cpython-314.pyc` (mtime 05:15:22) — both sibling-author
  work, not mine. A status check at ~05:11 showed zero modified tracked
  files; the edits landed in between. My replay consumed only the frozen
  `0df212f` copy, so the baseline comparison is unaffected. Untracked =
  my `corpus/live/r67-baseline/`, prior rounds' untracked frozen/tree
  dirs, and the sibling dirs above.

## Write-scope accounting

Wrote only: this report; `corpus/live/r67-baseline/` (`frozen/` minus the
1,097 excluded members, `archive-{manifest,excluded}.txt`, `rerun.py`,
`ledger-r67-baseline.tsv`, `out/` (204 captures), `runs-{before,after,
new}.txt`, `committed-shas.tsv`, `receipt-compare.tsv`,
`semantic-compare.tsv`, `compare.py`, `semantic_compare.py`,
`committed-ledger-sha.before.txt`, `toolchain.txt`, `rerun.log`). No
canonical `corpus/live/runs/` writes, no tracked-file edits, no commits,
no pushes. Leaf seat — no dispatch performed.

## Residual gaps

- Path-embedded receipts (rows 04–05, 07–11, 14–17, 19, 97) can never be
  raw-byte-identical off the canonical path; 11 of the 13 truncate the path
  mid-token at the leaf head, so anchor-level JSON comparison is the
  strongest check available in a displaced tree.
- The committed r66 ledger exists in two copies (author + verifier, both
  byte-stable at `0df212f`, exits identical); the replay was anchored on the
  author's `ledger-r66.tsv` per r62–r66 convention, with the verifier
  ledger/ledgers' receipts used as a secondary committed reference —
  no row needed it (0 unresolved DIFFERS).
- Whether the sibling r67 scratch and the `.gitignore` hygiene commit get
  amended/extended is outside my seat; if further commits land, this report
  remains the `0df212f` reference.
