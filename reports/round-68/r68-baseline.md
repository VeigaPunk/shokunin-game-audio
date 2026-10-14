# R68 baseline — frozen before-state replay of the 112-command ledger

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
Frozen state = `git archive` of canonical HEAD **`bd5e1fe`** ("r67
report-last: verifier AGREE 5/5 + scout/scribe landings (8/8 seats) +
transport-axis knowledge + LOG/SCORECARD"), extracted to
`corpus/live/r68-baseline/frozen/` (180 MB, 14,675 files incl. all 4,317
tracked `corpus/live/runs/` receipt dirs). HEAD was `bd5e1fe` at dispatch
(~09:49 UTC), at archive time (09:50 UTC), and is still `bd5e1fe` at report
time — **zero mid-window commits** this round.

**Committed ledger:** `corpus/live/r67-author/ledger-r67.tsv` (committed at
`366fcc1` "r67: transport as first-class ledger axis"), 112 rows — the prior
102 commands plus the ten r67 transport modes at positions 02–11.
Secondary committed reference: `corpus/live/r67-verifier/ledger-r67-verifier.tsv`
(same 112-mode order). Both sha256'd identical before and after my window
(`7b1580cc…` / `3a8d8c4f…`, `committed-ledger-sha.before.txt`).

## Exclusion accounting (r62–r67 convention — tracked baseline scratch removed)

`archive-manifest.txt` holds all **20,697** tar members (15,981 file members
+ 4,716 directory entries). `archive-excluded.txt` holds the **1,318** dropped
members — every tracked `corpus/live/r*-baseline` member at `bd5e1fe`
(r62: 254, r63: 256, r64: 183, r65: 195, r66: 209, r67: 221 — 1,306 files +
12 dir entries) plus `node_modules` (**zero** such members). Extracted file
count 14,675 = 15,981 − 1,306. The only manifest directories absent from the
frozen tree are the 12 excluded `r*-baseline` dir entries themselves (dirs
are created implicitly by file extraction; git tracks no empty dirs).
`find frozen -type d \( -name 'r*-baseline' -o -name node_modules \)` returns
empty — no nested baseline/frozen trees carried in.

Frozen-commit proof (all byte-equal to `git show bd5e1fe:<path>`):
`corpus/fixtures/measure_audio.py` `a0b2ad6d…`,
`corpus/live/r67-author/run_ledger.py` `d51b0472…`,
`corpus/live/r67-author/ledger-r67.tsv` `7b1580cc…`,
`corpus/live/r67-verifier/ledger-r67-verifier.tsv` `3a8d8c4f…`,
`corpus/live/r67-author/transport-matrix.json` `6111429f…`,
`corpus/live/round-65/pair_preempt_{act,both}.wav` `cf5edecc…`/`a37adc7c…`,
`corpus/live/round-66/pair_{dec_hcom,lengate_hcom_132}.wav`
`325fb967…`/`a1abdac4…`. The raw archive (`git archive HEAD`, sha256
`cf130392…`, 167 MB) was deleted after extraction — it is reproducible
byte-identically from `bd5e1fe`.

Toolchain: `SoX_ng v14.8.0.1`, `ffmpeg/ffprobe n9.0.1`, `python3 3.14.7` +
`numpy 2.5.3` — unchanged from the r63–r67 declared set.

Repo-path note: the brief's line 6 names `~/Projects/prymeagnt/audio`; that
worktree resolves `.shokunin/audio` via symlink into this canonical repo
(`/home/vgpnk/Projects/shokunin/audio-shokunin`, the dispatch header's repo).
All scratch/report writes land in the canonical repo as in r62–r67.

## Standalone-capability finding

Unchanged: `measure_audio.py:17` anchors `ROOT =
Path(__file__).resolve().parents[1]` (= `frozen/corpus`); every fixture
input — the r67 transport members included (`live/round-65/pair_preempt_*.wav`
and `live/round-66/pair_{dec,lengate}_*.wav` per `measure_audio.py:179-189`
`TRANSPORT_R67_MEMBERS`) — resolves inside the frozen tree, and receipt
writes go to `frozen/corpus/live/runs/`. The replay wrote zero files outside
`corpus/live/r68-baseline/` — all 112 ledger col-3 receipt paths carry the
`r68-baseline/frozen/corpus/live/runs/` prefix (grep-verified 112/112).
Canonical `corpus/live/runs/` gained 103 dirs during my window — all sibling
r68-lane work, detailed below; overlap with my 112 fresh receipts: **zero
names**.

## Replay result — deterministic, exact

`rerun.py` (verbatim 112-MODES copy of `r67-author/run_ledger.py` — verified
`==` by importing the frozen copy's `MODES` at startup: the prior 102 + the
ten r67 transport modes at positions 02–11; serial, `cwd=frozen`) ran
09:52:11→09:54:23 UTC (~2 min 12 s), exit 0. Outputs:
`ledger-r68-baseline.tsv`; per-command captures `out/{01..112}.{stdout,
stderr}` (224 files); census `runs-{before,after,new}.txt`
(4,317 / 4,429 / 112); hash tables `committed-shas.tsv`,
`receipt-compare.tsv`; field-level check `semantic-compare.tsv`;
`compare.py`, `semantic_compare.py`, `rerun.log`, `toolchain.txt`,
`committed-ledger-sha.before.txt`, `pre-state.txt`, `frozen-proofs.txt`,
`runs-canonical-{before,after}.txt`, `runs-canonical-{drift,added}.txt`,
`ledger-cols-diff{,-verifier}.txt`, `archive-{manifest,excluded}.txt`.

- **Counts by exit: 49 × exit 0 / 63 × exit 1** — matches committed
  `ledger-r67.tsv` exactly (the r67-verifier ledger agrees identically), and
  the brief's declared expectation.
- **112/112 rows identical** to committed on (idx, exit, failure-summary) —
  `diff` over TSV cols 1,2,4 → empty, against **both** committed r67 ledgers
  (`r67-author/ledger-r67.tsv` and `r67-verifier/ledger-r67-verifier.tsv`).
- **Census: 4,317 → 4,429 run dirs (+112, zero extras).** All 112 fresh
  receipts resolve under `r68-baseline/frozen/corpus/live/runs/` (stamps
  `20261014T095212…T095423`).
- **Committed-receipt anchor: 112/112** committed receipts named in
  `ledger-r67.tsv` col 3 are byte-identical to their `git show bd5e1fe:`
  blobs — anchored on the frozen commit explicitly (the r67 mid-window-commit
  lesson applied up front, though no commit landed this window).
- **Receipts: 99/112 byte-identical** (sha256) to committed counterparts —
  including all ten r67 transport rows (02–11), whose receipts carry no
  absolute paths by design; **2 normalized** (rows 29
  `ui-route-act-00-r63`, 107 `--probe-invalid`): absolute paths embedded in
  full stderr leaves — the frozen→canonical infix rewrite
  (`corpus/live/r68-baseline/frozen/corpus/` → `corpus/`) restores the
  committed sha256 exactly; **11 raw-DIFFERS, all the known truncation
  class** — rows 14, 15, 17 (`ui-lengate-{gsrt-24,gsrt-25,hcom-132}-r66`),
  18–21 (`ui-preempt-{act,gsrt,hcom,both}-r65`), 24–27
  (`ui-extensible-valid-{24,25,56,57}-r64`): `tail[-1][-160:]` cuts the
  embedded absolute path mid-token at the leaf head (fresh leaves begin
  `"pen input file …"`, `"an't open input file …"`), so no prefix rewrite
  can sha-match; anchored suffix after the last `corpus/` is byte-identical.
- JSON-level comparison (`semantic_compare.py`): identical structure on all
  112 rows; every differing string leaf is `corpus/`-anchored in both
  receipts with equal post-anchor suffix and carries the
  `live/r68-baseline/frozen/` infix — **99 EQUAL, 13 EQUAL-MOD-PATHS,
  0 CONTENT-DIFF, 0 STRUCTURE-DIFF** (`semantic-compare.tsv`). All 30
  differing leaves are `sox_{bridge,native,stat,}_stderr` /
  `invalid_probes[1].detail.stderr` — the path-embedding class only.
- Row-01 normal receipt sha `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591
  d117732f09ffaffb1b` — identical fresh and committed; the same value the
  r66 and r67 baselines recorded for row 01.
- Fixture bytes stable in-tree post-replay (all `== git show bd5e1fe:`):
  `pair_preempt_act.wav` `cf5edecc…`, `pair_preempt_gsrt.wav` `477bd371…`,
  `pair_preempt_hcom.wav` `bfc61413…`, `pair_preempt_both.wav` `a37adc7c…`,
  `pair_dec_hcom.wav` `325fb967…`, `pair_dec_act.wav` `777b6764…`,
  `pair_lengate_gsrt_24.wav` `e7db9976…`, `pair_lengate_gsrt_25.wav`
  `ede4161b…`, `pair_lengate_hcom_131.wav` `6fd9f471…`,
  `pair_lengate_hcom_132.wav` `a1abdac4…`.
- Committed-ledger guard: `corpus/live/r67-author/ledger-r67.tsv` sha256
  `7b1580cc909237c1e33b7ceda55d151d7d1227a8b48a63e0448e2c7e40883533` and the
  verifier ledger `3a8d8c4f…` identical before and after my run — the replay
  writes only to scratch.
- **Drift: zero** — all deltas are explained by the known path-embedding
  convention.

## Live-tree events during the window (observed, not mine)

- Sibling r68 lanes mid-flight: untracked `corpus/live/r68-{boundary,critic,
  reviewer,scout,scribe,simplifier}/` plus pre-existing
  `r67-simplifier/head-tree/`.
- Canonical `corpus/live/runs/` gained **103** dirs stamped
  `20261014T095317…T095518` (`runs-canonical-{drift,added}.txt`) — a sibling
  live replay of the same 112-mode r67 ledger (mode names in order, ~65 s
  behind my frozen run). Zero name overlap with my 112 frozen receipts
  (`095212…095423`); none written by this replay — `measure_audio.py`'s
  `__file__` anchor makes canonical writes impossible from the frozen tree.
- `git status` at report time: **zero modified tracked files** — the r68
  author lane's `measure_audio.py` additions (declared axis-move) have not
  landed in the worktree yet; only untracked dirs exist. My replay consumed
  only the frozen `bd5e1fe` copy regardless.

## Write-scope accounting

Wrote only: this report; `corpus/live/r68-baseline/` (`frozen/` minus the
1,318 excluded members, `archive-{manifest,excluded}.txt`, `rerun.py`,
`ledger-r68-baseline.tsv`, `out/` (224 captures), `runs-{before,after,new}.txt`,
`committed-shas.tsv`, `receipt-compare.tsv`, `semantic-compare.tsv`,
`compare.py`, `semantic_compare.py`, `committed-ledger-sha.before.txt`,
`toolchain.txt`, `rerun.log`, `pre-state.txt`, `frozen-proofs.txt`,
`runs-canonical-{before,after,drift,added}.txt`,
`ledger-cols-diff{,-verifier}.txt`). No canonical `corpus/live/runs/`
writes, no tracked-file edits, no commits, no pushes. Leaf seat — no
dispatch performed.

## Residual gaps

- Path-embedded receipts (rows 14–15, 17–21, 24–27, 29, 107) can never be
  raw-byte-identical off the canonical path; 11 of the 13 truncate the path
  mid-token at the leaf head, so anchor-level JSON comparison is the
  strongest check available in a displaced tree.
- The committed r67 ledger exists in two copies (author + verifier, both
  byte-stable at `bd5e1fe`, exits identical); the replay was anchored on the
  author's `ledger-r67.tsv` per r62–r67 convention, with the verifier
  ledger's receipts as secondary committed reference — no row needed it
  (0 unresolved DIFFERS).
- The sibling live replay filling `corpus/live/runs/` (103 dirs) is another
  lane's evidence path; if it is still running, canonical census numbers in
  this report are a snapshot of ~09:55 UTC.
- Whether sibling r68 lanes' scratch gets committed is outside my seat; if
  further commits land, this report remains the `bd5e1fe` reference.
